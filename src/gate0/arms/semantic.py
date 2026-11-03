"""One offline semantic representation arm and its closed record shape."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
import math
import struct
from collections import defaultdict
from typing import Mapping, Sequence

from gate0.adapters.embedding import EmbeddingAdapter, normalize_vector
from gate0.temporal import SampleTarget


@dataclass(frozen=True)
class RepresentationRecord:
    space_id: str
    representation_id: str
    revision_id: str
    window_id: str
    sampling_manifest_digest: str
    model_identity: str
    processor_digest: str
    preprocessing_digest: str
    pooling: str
    dimension: int
    dtype: str
    normalization: str
    metric: str
    generation_attempt_id: str
    representation_status: str
    failure_reason: str | None = None
    vector_digest: str | None = None
    vector_digest_algorithm: str | None = None
    vector_encoding: str | None = None
    vector_length: int | None = None
    accumulation_order: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {k: v for k, v in asdict(self).items() if v is not None}


def _digest(vector: tuple[float, ...]) -> str:
    return hashlib.sha256(struct.pack("<%dd" % len(vector), *vector)).hexdigest()


def _representation_id(
    revision_id: str,
    window_id: str,
    attempt: str,
    *,
    model_identity: str,
    processor_digest: str,
    preprocessing_digest: str,
    sampling_manifest_digest: str,
) -> str:
    """Return an ID bound to the complete semantic generation identity.

    A representation ID must not alias when its source/window is unchanged but
    the model, processor, preprocessing, or sampling contract changes.  JSON
    gives each field an unambiguous boundary while preserving the existing
    string API and deterministic digest format.
    """
    identity = {
        "revision_id": revision_id,
        "window_id": window_id,
        "generation_attempt_id": attempt,
        "model_identity": model_identity,
        "processor_digest": processor_digest,
        "preprocessing_digest": preprocessing_digest,
        "sampling_manifest_digest": sampling_manifest_digest,
    }
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return "representation_" + hashlib.sha256(payload.encode()).hexdigest()[:32]


def embed_windows(
    rows: Sequence[SampleTarget],
    adapter: EmbeddingAdapter,
    *,
    pixels_by_frame: Mapping[str, bytes],
    revision_id: str,
    sampling_manifest_digest: str,
    generation_attempt_id: str,
    model_identity: str = "NOT_OBSERVED",
    processor_digest: str = "0" * 64,
    preprocessing_digest: str = "0" * 64,
) -> tuple[RepresentationRecord, ...]:
    grouped: dict[str, list[SampleTarget]] = defaultdict(list)
    for row in sorted(rows, key=lambda item: (item.window_id, item.tick)):
        grouped[row.window_id].append(row)
    out: list[RepresentationRecord] = []
    for window_id, window_rows in sorted(grouped.items()):
        vectors: list[tuple[float, ...]] = []
        failure: str | None = None
        for row in window_rows:
            if row.coverage_status != "SUCCEEDED" or row.selected_frame_id is None:
                failure = "SAMPLE_FAILED"
                break
            pixels = pixels_by_frame.get(row.selected_frame_id)
            if pixels is None:
                failure = "MISSING_PIXELS"
                break
            result = adapter.embed("pixels", pixels)
            if result.vector is None or result.status != "SUCCESS":
                failure = result.failure_reason or result.status
                break
            try:
                vector = normalize_vector(tuple(float(v) for v in result.vector))
                vectors.append(vector)
            except ValueError as exc:
                failure = str(exc)
                break
        rid = _representation_id(
            revision_id,
            window_id,
            generation_attempt_id,
            model_identity=model_identity,
            processor_digest=processor_digest,
            preprocessing_digest=preprocessing_digest,
            sampling_manifest_digest=sampling_manifest_digest,
        )
        common = dict(space_id="semantic_visual", representation_id=rid, revision_id=revision_id,
                      window_id=window_id, sampling_manifest_digest=sampling_manifest_digest,
                      model_identity=model_identity, processor_digest=processor_digest,
                      preprocessing_digest=preprocessing_digest, pooling="MEAN_TARGET_SLOTS",
                      dimension=len(vectors[0]) if vectors else 0, dtype="float64",
                      normalization="L2", metric="COSINE", generation_attempt_id=generation_attempt_id)
        if failure is not None or not vectors:
            out.append(RepresentationRecord(**common, representation_status="FAILED", failure_reason=failure or "ZERO_VECTOR"))
            continue
        if any(len(v) != len(vectors[0]) for v in vectors):
            out.append(RepresentationRecord(**common, representation_status="FAILED", failure_reason="DIMENSION_MISMATCH"))
            continue
        mean = tuple(sum(v[i] for v in vectors) / len(vectors) for i in range(len(vectors[0])))
        try:
            pooled = normalize_vector(mean)
        except ValueError as exc:
            out.append(RepresentationRecord(**common, representation_status="FAILED", failure_reason=str(exc)))
            continue
        common["dimension"] = len(pooled)
        out.append(RepresentationRecord(**common, representation_status="SUCCEEDED",
            vector_digest=_digest(pooled), vector_digest_algorithm="SHA-256",
            vector_encoding="float64_le_row_major", vector_length=len(pooled),
            accumulation_order="target_tick_ascending_serial"))
    return tuple(out)
