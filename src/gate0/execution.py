"""Executable local Gate-0 experiment pipeline over synthetic fixtures.

The frozen Gate-0 experiment contract names eleven CLI stages.  Before this
module existed the CLI only implemented ``repeat``: every other legal stage was
an explicit ``NOT_OBSERVED`` stub and no code produced the closed thirteen
artifact set.  This module makes the declared stage order actually executable:

    prepare -> inventory -> split -> label -> preflight -> extract -> embed
            -> rank -> evaluate -> report

It deliberately does not invent evidence.  A run over the checked-in synthetic
fixture is labelled ``SYNTHETIC_FIXTURE`` and the report stage returns
``NOT_RUN``: the pipeline refuses to project a Gate-0 decision from synthetic
data.  Real corpus, model and human label inputs remain prerequisites (see the
execution report under ``docs/agent-runs``).

The synthetic input surface is three local JSON files beneath ``--input-root``
plus deterministic source bytes; no network, provider or model download is
used.  The ranker never reads the labels file: query vectors live in a separate
fake-embedding file so the label firewall is visible in ``stage_inputs``.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import hashlib
import json
import math
import os
from dataclasses import dataclass
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from gate0.adapters.decoder import DecodedFrame, SyntheticDecoder
from gate0.media.decode import FfprobeFrameDecoder
from gate0.media.tool_identity import ToolError, measure_tool
from gate0.media_experiment import (
    AUTHORIZED_CORPUS_FILE,
    AUTHORIZED_EVIDENCE_CLASS,
    AUTHORIZED_EXECUTION_BLOCKERS,
    AUTHORIZED_PROVENANCE_STATUS,
    AuthorizedLocalCorpus,
    AuthorizedLocalError,
    MEDIA_CORPUS_FILE,
    MEDIA_CORPUS_KIND,
    MEDIA_EVIDENCE_CLASS,
    MediaInputError,
    MediaMeasurement,
    load_authorized_local_declaration,
    load_media_corpus,
    measure_corpus,
    validate_authorized_local_declaration,
)
from gate0.adapters.embedding import FakeEmbeddingAdapter, normalize_vector
from gate0.arms.metadata import metadata_score
from gate0.arms.semantic import RepresentationRecord, _digest as vector_digest, embed_windows
from gate0.canonical_json import canonical_bytes, canonical_jsonl_bytes
from gate0.config import load_config
from gate0.config_freeze import canonical_config_digest
from gate0.contracts.types import ArtifactEnvelope, ArtifactRef, payload_digest, record_digest
from gate0.contracts.validator import ARTIFACT_FILENAMES
from gate0.evaluation import EvaluationResult, Metric, evaluate, load_reviewer_input, reviewer_judgments
from gate0.failure import AttemptRecord
from gate0.identity import (
    digest_bytes,
    digest_json,
    opaque_id,
    validate_digest,
    validate_opaque_id,
)
from gate0.inventory import ProbeEvidence, RevisionRef, SourceOccurrence
from gate0.labels import (
    CANONICAL_TIME_DOMAINS as LABEL_TIME_DOMAINS,
    FAMILIES as LABEL_FAMILIES,
    PRESENCE as LABEL_PRESENCE,
    build_gold_events,
    build_queries,
    label_version_digest,
    ranking_inputs,
)
from gate0.policy import PolicyDecision
from gate0.ranking import rank_candidates
from gate0.repeat import frozen_input_digest
from gate0.split import freeze_relation_split
from gate0.stages.extract import extract
from gate0.stages.inventory import inventory
from gate0.stages.lifecycle import advance_stage
from gate0.stages.report import render_gate_decision
from gate0.temporal import Rational, SampleTarget

FIXED_NOW = "1970-01-01T00:00:00Z"
CORPUS_FILE = "synthetic-corpus.json"
LABELS_FILE = "synthetic-labels.json"
QUERY_VECTORS_FILE = "synthetic-query-vectors.json"
MANIFEST_FILE = "run_manifest.json"
LEDGER_FILE = "runtime_and_failure_ledger.json"
MODEL_IDENTITY = "SYNTHETIC_FAKE_EMBEDDER_V1"
EVIDENCE_CLASS = "SYNTHETIC_FIXTURE"
METADATA_ARM = "metadata-floor"
SEMANTIC_ARM = "offline-development-arm"
FAMILIES = ("APPEARANCE", "VISIBLE_ACTION", "INTERACTION", "SCENE_COMPOSITION_CAMERA_MOVEMENT")


# ---------------------------------------------------------------------------
# small deterministic IO helpers
# ---------------------------------------------------------------------------

def _plain(value: Any) -> Any:
    """Deep-copy frozen config views into JSON-serializable plain values."""
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _load_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}-", suffix=".tmp", delete=False) as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _write_json_artifact(path: Path, value: Any) -> None:
    _atomic_write(path, canonical_bytes(value))


def _write_jsonl_artifact(path: Path, records: Sequence[Mapping[str, Any]]) -> None:
    _atomic_write(path, canonical_jsonl_bytes(records))


def _publish_manifest(run_dir: Path, manifest: dict[str, Any]) -> None:
    _atomic_write(run_dir / MANIFEST_FILE, (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8"))


def _ledger(run_dir: Path) -> dict[str, Any]:
    path = run_dir / LEDGER_FILE
    if path.exists():
        value = _load_json(path)
        if isinstance(value, dict) and isinstance(value.get("events"), list):
            return value
    return {"schema_version": "gate0.runtime_and_failure_ledger.v1", "events": []}


def _publish_ledger(run_dir: Path, ledger: dict[str, Any]) -> None:
    _atomic_write(run_dir / LEDGER_FILE, canonical_bytes(ledger))


def _record(record_type: str, payload: Mapping[str, Any], seed: Any) -> dict[str, Any]:
    row = {
        "record_id": opaque_id("record", seed),
        "record_type": record_type,
        "record_schema_version": "gate0.v1",
        "record_digest": "",
        "payload": dict(payload),
    }
    row["record_digest"] = record_digest(row)
    return row


def _sorted_records(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted((dict(row) for row in rows), key=lambda row: row["record_id"])


# ---------------------------------------------------------------------------
# synthetic input contract
# ---------------------------------------------------------------------------

def has_synthetic_input(input_root: str | Path) -> bool:
    return (Path(input_root) / CORPUS_FILE).is_file()


def has_media_input(input_root: str | Path) -> bool:
    """True when the input root declares a generated local media corpus."""
    return (Path(input_root) / MEDIA_CORPUS_FILE).is_file()


def _is_media_corpus(corpus: Mapping[str, Any]) -> bool:
    return corpus.get("corpus_mode") == "media"


def _evidence_state(corpus: Mapping[str, Any]) -> str:
    return MEDIA_EVIDENCE_CLASS if _is_media_corpus(corpus) else EVIDENCE_CLASS


def _manifest_evidence_state(manifest: Mapping[str, Any]) -> str:
    """Evidence state for non-corpus stages, derived from the sealed run manifest."""
    state = manifest.get("evidence_class")
    return str(state) if isinstance(state, str) and state else EVIDENCE_CLASS


def _load_inputs(input_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if has_media_input(input_root):
        media = load_media_corpus(input_root / MEDIA_CORPUS_FILE)
        corpus: Any = media.execution_corpus()
    else:
        corpus = _load_json(input_root / CORPUS_FILE)
    labels = _load_json(input_root / LABELS_FILE)
    query_vectors = _load_json(input_root / QUERY_VECTORS_FILE)
    if not isinstance(corpus, dict) or not isinstance(labels, dict) or not isinstance(query_vectors, dict):
        raise ValueError("SYNTHETIC_INPUT_INVALID")
    return corpus, labels, query_vectors


def _spec_digest(corpus: Mapping[str, Any], labels: Mapping[str, Any], query_vectors: Mapping[str, Any]) -> str:
    return digest_json({"corpus": corpus, "labels": labels, "query_vectors": query_vectors})


def _pixel_bytes(frame_id: str) -> bytes:
    return b"pixels:" + frame_id.encode("utf-8")


def _frames_for_revision(revision: Mapping[str, Any]) -> tuple[DecodedFrame, ...]:
    frames = []
    for frame in revision["frames"]:
        frames.append(DecodedFrame(
            raw_pts_ticks=int(frame["raw_pts_ticks"]),
            time_base_num=int(frame["time_base_num"]),
            time_base_den=int(frame["time_base_den"]),
            decoder_ordinal=int(frame["decoder_ordinal"]),
            presentation_order=int(frame["presentation_order"]),
            selected_frame_id=str(frame["frame_id"]),
            pixels=_pixel_bytes(str(frame["frame_id"])),
            dts_ticks=frame.get("dts_ticks"),
            frame_index=frame.get("frame_index"),
        ))
    return tuple(frames)


def _revision_refs(manifest: Mapping[str, Any], corpus: Mapping[str, Any]) -> dict[str, RevisionRef]:
    streams = {row["revision_id"]: row for row in manifest.get("selected_streams", [])}
    refs: dict[str, RevisionRef] = {}
    for revision in corpus["revisions"]:
        revision_id = str(revision["revision_id"])
        selected = streams.get(revision_id)
        if selected is None:
            raise ValueError("SELECTED_STREAM_NOT_OBSERVED")
        refs[revision_id] = RevisionRef(revision_id, str(revision["content_id"]), str(revision["locator"]),
                                        int(selected["stream_index"]), str(selected["selection_source"]))
    return refs


def _media_measurements(corpus: Mapping[str, Any], config: Mapping[str, Any],
                        input_root: Path) -> tuple[dict[str, MediaMeasurement], list[dict[str, Any]]]:
    """Measure the declared generated media with the bounded local adapters."""
    if not _is_media_corpus(corpus):
        raise ValueError("MEDIA_INPUT_REQUIRED")
    media = load_media_corpus(input_root / MEDIA_CORPUS_FILE)
    runtime = config["runtime"]
    window_seconds = int(config["windows"]["duration_seconds"])
    try:
        measurements = measure_corpus(
            media,
            input_root=input_root,
            ffprobe_path=str(runtime["ffprobe_path"]),
            ffmpeg_path=str(runtime["ffmpeg_path"]),
            window_seconds=window_seconds,
        )
    except MediaInputError as exc:
        raise ValueError(exc.reason) from exc
    by_revision = {measurement.revision.revision_id: measurement for measurement in measurements}
    if set(by_revision) != {str(row["revision_id"]) for row in corpus["revisions"]}:
        raise ValueError("MEDIA_REVISION_SET_MISMATCH")
    return by_revision, [measurement.to_record() for measurement in measurements]


def _extract_rows(corpus: Mapping[str, Any], refs: Mapping[str, RevisionRef],
                  config: Mapping[str, Any] | None = None,
                  input_root: Path | None = None) -> dict[str, tuple[SampleTarget, ...]]:
    rows: dict[str, tuple[SampleTarget, ...]] = {}
    if _is_media_corpus(corpus):
        if config is None or input_root is None:
            raise ValueError("MEDIA_INPUT_CONTEXT_MISSING")
        measurements, _records = _media_measurements(corpus, config, input_root)
        for revision in corpus["revisions"]:
            revision_id = str(revision["revision_id"])
            measurement = measurements[revision_id]
            rows[revision_id] = extract(
                refs[revision_id],
                FfprobeFrameDecoder(measurement.sequence),
                window_count=measurement.window_count,
                origin_pts_ticks=measurement.origin_pts_ticks,
            )
        return rows
    for revision in corpus["revisions"]:
        revision_id = str(revision["revision_id"])
        rows[revision_id] = extract(
            refs[revision_id],
            SyntheticDecoder(_frames_for_revision(revision)),
            window_count=int(revision.get("window_count", corpus.get("window_count", 1))),
            origin_pts_ticks=int(revision.get("origin_pts_ticks", 0) or 0),
        )
    return rows


def _configured_ffmpeg_identity(config: Mapping[str, Any]) -> dict[str, Any] | None:
    """Measure the configured ffmpeg identity without using it for sampling."""
    executable = str(config["runtime"]["ffmpeg_path"])
    try:
        return measure_tool("ffmpeg", executable).to_dict()
    except ToolError as exc:
        return {"role": "ffmpeg", "executable": executable,
                "status": "NOT_OBSERVED", "detail": str(exc)}


def _media_frame_vector(revision_id: str, frame_id: str, *, dimension: int = 8) -> tuple[float, ...]:
    """Deterministic stand-in embedding for generated media (NOT model inference)."""
    raw = hashlib.sha256(f"media-frame:{revision_id}:{frame_id}".encode("utf-8")).digest()
    values = [((int.from_bytes(raw[index * 2:index * 2 + 2], "big") % 2001) - 1000) / 1000.0
              for index in range(dimension)]
    norm = sum(value * value for value in values) ** 0.5
    return tuple(value / norm for value in values)


def _sample_records(rows_by_revision: Mapping[str, Sequence[SampleTarget]]) -> list[dict[str, Any]]:
    records = []
    for revision_id in sorted(rows_by_revision):
        for row in rows_by_revision[revision_id]:
            records.append(_record("sample_target", row.to_dict(), row.target_id))
    return _sorted_records(records)


def _target_counts(rows_by_revision: Mapping[str, Sequence[SampleTarget]]) -> dict[str, int]:
    counts = {"planned": 0, "succeeded": 0, "failed": 0, "omitted": 0, "quarantined": 0}
    for rows in rows_by_revision.values():
        for row in rows:
            counts["planned"] += 1
            status = row.coverage_status
            if status == "SUCCEEDED":
                counts["succeeded"] += 1
            elif status in ("FAILED",):
                counts["failed"] += 1
            elif status in ("OMITTED",):
                counts["omitted"] += 1
            elif status in ("QUARANTINED",):
                counts["quarantined"] += 1
            else:
                raise ValueError("UNCLASSIFIED_SAMPLE_TARGET")
    return counts


def _window_evidence(rows_by_revision: Mapping[str, Sequence[SampleTarget]]) -> list[dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    for revision_id in sorted(rows_by_revision):
        for row in rows_by_revision[revision_id]:
            if row.coverage_status != "SUCCEEDED" or row.raw_pts is None:
                continue
            window_index = int(row.window_id.rsplit("_", 1)[1])
            evidence.setdefault(row.window_id, {
                "window_id": row.window_id,
                "revision_id": revision_id,
                "window_index": window_index,
                "start": {"numerator": window_index * 4, "denominator": 1},
                "end": {"numerator": (window_index + 1) * 4, "denominator": 1},
                "mapping_ref": row.mapping_ref,
                "origin": {"numerator": 0, "denominator": 1},
                "time_base": {"numerator": int(row.raw_pts["time_base_num"]), "denominator": int(row.raw_pts["time_base_den"])},
            })
    return [evidence[key] for key in sorted(evidence)]


def _frame_vectors(corpus: Mapping[str, Any],
                   rows_by_revision: Mapping[str, Sequence[SampleTarget]] | None = None
                   ) -> tuple[dict[str, bytes], dict[bytes, tuple[float, ...]]]:
    pixels_by_frame: dict[str, bytes] = {}
    vectors: dict[bytes, tuple[float, ...]] = {}
    if _is_media_corpus(corpus):
        for revision_id in sorted(rows_by_revision or {}):
            for row in rows_by_revision[revision_id]:
                if row.selected_frame_id is None:
                    continue
                pixel = _pixel_bytes(row.selected_frame_id)
                pixels_by_frame[row.selected_frame_id] = pixel
                vectors[pixel] = _media_frame_vector(revision_id, row.selected_frame_id)
        return pixels_by_frame, vectors
    for revision in corpus["revisions"]:
        for frame in revision["frames"]:
            frame_id = str(frame["frame_id"])
            pixel = _pixel_bytes(frame_id)
            pixels_by_frame[frame_id] = pixel
            vectors[pixel] = tuple(float(value) for value in frame["vector"])
    return pixels_by_frame, vectors


def _representations(corpus: Mapping[str, Any], rows_by_revision: Mapping[str, Sequence[SampleTarget]],
                     sampling_manifest_digest: str, attempt_id: str,
                     processor_digest: str) -> tuple[list[RepresentationRecord], dict[str, tuple[float, ...]]]:
    pixels_by_frame, vectors = _frame_vectors(corpus, rows_by_revision)
    adapter = FakeEmbeddingAdapter(vectors)
    records: list[RepresentationRecord] = []
    for revision_id in sorted(rows_by_revision):
        records.extend(embed_windows(
            rows_by_revision[revision_id], adapter,
            pixels_by_frame=pixels_by_frame,
            revision_id=revision_id,
            sampling_manifest_digest=sampling_manifest_digest,
            generation_attempt_id=attempt_id,
            model_identity=MODEL_IDENTITY,
            processor_digest=processor_digest,
            preprocessing_digest=digest_json({"synthetic_preprocessing": "gate0.v1"}),
        ))
    window_vectors: dict[str, tuple[float, ...]] = {}
    for record in records:
        if record.representation_status != "SUCCEEDED":
            continue
        frame_values = []
        for row in rows_by_revision[record.revision_id]:
            if row.window_id != record.window_id:
                continue
            pixel = pixels_by_frame[row.selected_frame_id]
            frame_values.append(tuple(normalize_vector(vectors[pixel])))
        mean = [sum(values) / len(frame_values) for values in zip(*frame_values)]
        pooled = tuple(normalize_vector(mean))
        if vector_digest(pooled) != record.vector_digest:
            raise ValueError("REPRESENTATION_DIGEST_MISMATCH")
        window_vectors[record.window_id] = pooled
    return records, window_vectors


def _query_rows(labels: Mapping[str, Any]) -> list[tuple[str, str, tuple[str, str]]]:
    return [(str(row["query_id"]), str(row["text"]), (str(row["family"]), str(row["presence"])))
            for row in labels["queries"]]


def _query_split(labels: Mapping[str, Any]) -> dict[str, str]:
    return {str(row["query_id"]): str(row["split"]) for row in labels["queries"]}


def _gold_inputs(labels: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in labels["gold_events"]]


def _window_entries(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in manifest.get("windows", [])]


def _metadata_rankings(corpus: Mapping[str, Any], queries: Sequence[Mapping[str, Any]],
                       windows: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    basenames = {str(row["revision_id"]): (Path(str(row["locator"])).name, Path(str(row["locator"])).parent.name)
                 for row in corpus["revisions"]}
    windows_by_revision: dict[str, list[dict[str, Any]]] = {}
    for window in windows:
        windows_by_revision.setdefault(str(window["revision_id"]), []).append(window)
    records: list[dict[str, Any]] = []
    projection: list[dict[str, Any]] = []
    for query in queries:
        scored = []
        for revision_id, rows in windows_by_revision.items():
            basename, parent = basenames[revision_id]
            score = metadata_score(str(query["text"]), basename, parent)
            for window in rows:
                candidate_id = opaque_id("candidate", {"query_id": query["query_id"], "arm": METADATA_ARM, "window_id": window["window_id"]})
                start = (int(window["start"]["numerator"]), int(window["start"]["denominator"]))
                tie_key = (-score, revision_id.encode("utf-8"), start, str(window["window_id"]).encode("utf-8"), candidate_id.encode("utf-8"))
                scored.append((tie_key, score, candidate_id, revision_id, window))
        scored.sort(key=lambda item: item[0])
        for rank, (_, score, candidate_id, revision_id, window) in enumerate(scored, 1):
            # D8/Q1=A: the metadata floor has no embedding or model descriptor,
            # so it never declares a representation identity.  The technical
            # window record is the coordinate surface and provenance lives on
            # the artifact envelope; no duplicate coordinates are re-emitted.
            payload = {
                "candidate_id": candidate_id,
                "query_id": query["query_id"],
                "arm_id": METADATA_ARM,
                "window_id": window["window_id"],
                "score": score,
                "score_status": "FINITE",
                "rank": rank,
                "coverage_status": "SELECTED",
                "gold_accessed": False,
            }
            records.append(_record("ranked_candidate", payload, {"query": query["query_id"], "arm": METADATA_ARM, "candidate": candidate_id}))
            projection.append({"query_id": query["query_id"], "arm_id": METADATA_ARM, "candidate_id": candidate_id,
                               "revision_id": revision_id, "window_id": window["window_id"], "score": score, "rank": rank})
    return records, projection


def _semantic_rankings(manifest: Mapping[str, Any], corpus: Mapping[str, Any], queries: Sequence[Mapping[str, Any]],
                       query_vectors: Mapping[str, Any], representation_rows: Sequence[Mapping[str, Any]],
                       windows: Sequence[Mapping[str, Any]], window_vectors: Mapping[str, tuple[float, ...]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    from types import SimpleNamespace
    window_by_id = {str(row["window_id"]): row for row in windows}
    representations = []
    vectors: dict[str, Sequence[float]] = {}
    starts: dict[str, tuple[int, int]] = {}
    for row in representation_rows:
        representation_id = str(row["representation_id"])
        if str(row.get("representation_status")) != "SUCCEEDED":
            representations.append(SimpleNamespace(representation_id=representation_id, revision_id=str(row["revision_id"]),
                                                   window_id=str(row["window_id"]), representation_status="FAILED"))
            continue
        if str(row["window_id"]) not in window_vectors:
            raise ValueError("REPRESENTATION_VECTOR_MISSING")
        representations.append(SimpleNamespace(representation_id=representation_id, revision_id=str(row["revision_id"]),
                                               window_id=str(row["window_id"]), representation_status="SUCCEEDED"))
        vectors[representation_id] = window_vectors[str(row["window_id"])]
        window = window_by_id[str(row["window_id"])]
        starts[representation_id] = (int(window["start"]["numerator"]), int(window["start"]["denominator"]))
    records: list[dict[str, Any]] = []
    projection: list[dict[str, Any]] = []
    for query in queries:
        query_id = str(query["query_id"])
        query_vector = query_vectors.get(query_id)
        if query_vector is None:
            raise ValueError("QUERY_VECTOR_MISSING")
        candidates = rank_candidates(query_vector, representations, query_id=query_id, vectors=vectors, window_starts=starts)
        for candidate in candidates:
            representation_id = candidate.representation_id
            window_id = None
            revision_id = None
            for row in representation_rows:
                if str(row["representation_id"]) == representation_id:
                    window_id, revision_id = str(row["window_id"]), str(row["revision_id"])
                    break
            if window_id is None:
                raise ValueError("REPRESENTATION_JOIN_FAILED")
            # Candidate identity is query+arm+window; the representation is a
            # distinct identity with one-to-one ID cardinality (§9.2).  Keeping
            # them separate prevents the same candidate_id repeating across
            # query rows.  The real representation_id is the cross-artifact FK.
            candidate_id = opaque_id("candidate", {"query_id": query_id, "arm": SEMANTIC_ARM, "window_id": window_id})
            payload = {
                "candidate_id": candidate_id,
                "query_id": query_id,
                "arm_id": SEMANTIC_ARM,
                "representation_id": representation_id,
                "window_id": window_id,
                "score": candidate.score,
                "score_status": candidate.score_status,
                "rank": candidate.rank,
                "coverage_status": candidate.coverage_status,
                "gold_accessed": False,
            }
            records.append(_record("ranked_candidate", payload, {"query": query_id, "arm": SEMANTIC_ARM, "candidate": candidate_id}))
            projection.append({"query_id": query_id, "arm_id": SEMANTIC_ARM, "candidate_id": candidate_id,
                               "revision_id": revision_id, "window_id": window_id,
                               "score": candidate.score, "rank": candidate.rank})
    return records, projection


def _metrics_payload(result: EvaluationResult) -> dict[str, Any]:
    return {"schema_version": "gate0.metrics.v1",
            "metrics": [value.to_dict() for key, value in sorted(result.metrics.items())]}


def _mapping_digest(token_map: Sequence[Mapping[str, str]], *, mapping_version: str, config_digest: str) -> str:
    ordered = sorted((dict(row) for row in token_map), key=lambda row: str(row["blind_arm_token"]).encode())
    return digest_json({"mapping_version": mapping_version, "config_digest": config_digest, "token_map": ordered})


def _runtime(config: Mapping[str, Any], config_digest: str, dependency_lock_digest: str) -> dict[str, Any]:
    import platform
    return {
        "python_version": str(config["runtime"]["python_version"]),
        "os_release_digest": digest_bytes(platform.release().encode("utf-8")),
        "runtime_executable_digest": digest_bytes(sys.executable.encode("utf-8")),
        "dependency_lock_digest": dependency_lock_digest,
        "config_digest": config_digest,
        "blas_thread_control_digest": digest_json({"blas_thread_count": int(config["runtime"]["blas_thread_count"])}),
        "tool_environment_digest": digest_json({
            "python_version": str(config["runtime"]["python_version"]),
            "dependency_lock_digest": dependency_lock_digest,
            "execution_profile": "gate0-synthetic-local-execution.v1",
        }),
    }


# ---------------------------------------------------------------------------
# manifest / attempt bookkeeping
# ---------------------------------------------------------------------------

def _append_stage(manifest: dict[str, Any], *, run_id: str, stage: str, input_digest: str,
                  output_refs: Sequence[Mapping[str, Any]] = (), policy_decision_id: str | None = None) -> None:
    attempt_id = opaque_id("attempt", {"run_id": run_id, "stage": stage})
    runtime = manifest["runtime"]
    attempt = AttemptRecord.create(
        run_id, stage, input_digest, manifest["config_digest"], runtime["tool_environment_digest"], input_digest,
        attempt_id=attempt_id, stage_status="SUCCEEDED", exit_code=0,
    )
    if policy_decision_id is not None:
        attempt = replace(attempt, policy_decision_id=policy_decision_id)
    running = advance_stage(run_id, attempt_id, stage, "PLANNED", "RUNNING", input_digest, manifest["config_digest"],
                            policy_decision_id=policy_decision_id, now=FIXED_NOW)
    terminal = advance_stage(run_id, attempt_id, stage, "RUNNING", "SUCCEEDED", input_digest, manifest["config_digest"],
                             policy_decision_id=policy_decision_id, now=FIXED_NOW)
    manifest["attempts"] = [*manifest.get("attempts", []), attempt.to_dict()]
    manifest["stage_transitions"] = [*manifest.get("stage_transitions", []), running.to_dict(), terminal.to_dict()]
    manifest["status"] = "RUNNING"


def _seal_failure(run_dir: Path, manifest: dict[str, Any], ledger: dict[str, Any], stage: str, reason: str) -> tuple[int, dict[str, Any]]:
    attempt_id = opaque_id("attempt", {"run_id": manifest.get("run_id"), "stage": stage, "failure": reason})
    ledger["events"] = [*ledger.get("events", []), {
        "event_id": opaque_id("event", {"run_id": manifest.get("run_id"), "stage": stage, "reason": reason}),
        "event_type": "FAILURE", "attempt_id": attempt_id, "affected_refs": [], "reason": reason,
        "occurred_at": FIXED_NOW,
    }]
    manifest["status"] = "FAILED"
    _publish_ledger(run_dir, ledger)
    _publish_manifest(run_dir, manifest)
    return 30, {"command": stage, "status": "INVALID_PROTOCOL", "reason": reason, "evidence_state": _manifest_evidence_state(manifest)}


# ---------------------------------------------------------------------------
# stage implementations
# ---------------------------------------------------------------------------

def _arm_registry(config: Mapping[str, Any]) -> list[dict[str, str]]:
    """Return the closed two-arm registry for this run (D8/Q1=A).

    The semantic arm id is the configured ``model.semantic_arm_id``; if the
    configuration diverges from the frozen ``SEMANTIC_ARM`` constant the run is
    refused rather than silently emitting two competing identities.
    """
    semantic_arm_id = str(config["model"]["semantic_arm_id"])
    if semantic_arm_id != SEMANTIC_ARM:
        raise ValueError(f"SEMANTIC_ARM_ID_MISMATCH:{semantic_arm_id}")
    return [
        {"arm_id": METADATA_ARM, "representation_kind": "metadata_floor"},
        {"arm_id": semantic_arm_id, "representation_kind": "embedding"},
    ]


def _stage_prepare(run_dir: Path, run_id: str, corpus: Mapping[str, Any], labels: Mapping[str, Any],
                   query_vectors: Mapping[str, Any], config: Mapping[str, Any], config_digest: str,
                   dependency_lock_digest: str) -> tuple[int, dict[str, Any]]:
    run_dir.mkdir(parents=True, exist_ok=True)
    revision_ids = [str(row["revision_id"]) for row in corpus["revisions"]]
    token_map = _plain(config["blinding"]["token_map"])
    blinding = _plain(config["blinding"])
    blinding["blind_mapping_digest"] = _mapping_digest(token_map, mapping_version=str(config["blinding"]["mapping_version"]), config_digest=config_digest)
    blinding["reviewer_ids"] = list(config["policy"]["reviewer_ids"])
    # Required by the frozen run_manifest schema; blinding scope is the T08
    # evaluation surface only.
    blinding["access_scope"] = "T08_only"
    manifest: dict[str, Any] = {
        "schema_version": "gate0.run_manifest.v1",
        "run_id": run_id,
        "gate_owner_id": str(config["policy"]["gate_owner_id"]),
        "source_revision_ids": revision_ids,
        "config_digest": config_digest,
        "dependency_lock_digest": dependency_lock_digest,
        "policy_decision_ids": [],
        "thresholds": _plain(config["thresholds"]),
        "runtime": _runtime(config, config_digest, dependency_lock_digest),
        "sandbox": _plain(config["sandbox"]),
        "invocations": [],
        "blinding": blinding,
        "stage_transitions": [],
        "attempts": [],
        "artifact_envelopes": [],
        "representations": [],
        "repeat_comparisons": [],
        "status": "PLANNED",
        # Execution-local projection fields (the frozen run_manifest schema is
        # closed; these are retained for the CLI repeat/verifier surface and the
        # schema-conformance follow-up is recorded in the execution report).
        "spec_digest": _spec_digest(corpus, labels, query_vectors),
        "evidence_class": _evidence_state(corpus),
        "corpus_kind": MEDIA_CORPUS_KIND if _is_media_corpus(corpus) else "synthetic_fixture_not_experiment_evidence",
        # Assertion-level evidence boundary: measured generated-media sampling,
        # synthetic embedding/labels, and NOT_OBSERVED experiment evidence stay distinct.
        "evidence_class_boundary": {
            "media_sampling": MEDIA_EVIDENCE_CLASS if _is_media_corpus(corpus) else "SYNTHETIC_FIXTURE",
            "embedding": "SYNTHETIC_FIXTURE",
            "ground_truth": "SYNTHETIC_FIXTURE",
            "experiment_result": "NOT_OBSERVED",
        },
        "synthetic_input": {"corpus": MEDIA_CORPUS_FILE if _is_media_corpus(corpus) else CORPUS_FILE,
                            "labels": LABELS_FILE, "query_vectors": QUERY_VECTORS_FILE},
        "selected_streams": [],
        "stage_inputs": {
            "prepare": [CORPUS_FILE, LABELS_FILE, QUERY_VECTORS_FILE],
            "rank": [CORPUS_FILE, QUERY_VECTORS_FILE],
            "evaluate": [LABELS_FILE],
        },
        "label_isolation": {
            "ranker_inputs": [CORPUS_FILE, QUERY_VECTORS_FILE, "queries.jsonl"],
            "ranker_excludes": [LABELS_FILE, "gold_events.jsonl", "window_judgments.jsonl"],
        },
        "host_sandbox_observation": "NOT_OBSERVED",
        # D8: the closed per-run arm registry is declared at prepare time. Both
        # configured arms are always scored by the rank stage, so the registry
        # is static for the run; representation_kind keeps the metadata floor
        # free of any fabricated embedding/model descriptor.
        "arms": _arm_registry(config),
    }
    _atomic_write(run_dir / LEDGER_FILE, canonical_bytes({"schema_version": "gate0.runtime_and_failure_ledger.v1", "events": []}))
    _append_stage(manifest, run_id=run_id, stage="prepare", input_digest=manifest["spec_digest"])
    _publish_manifest(run_dir, manifest)
    return 0, {"command": "prepare", "status": "SUCCEEDED", "evidence_state": _evidence_state(corpus), "run_id": run_id}


def _decision(manifest: Mapping[str, Any], config: Mapping[str, Any], purpose: str, allowed: Sequence[str],
              retention: str, revision_scope: Sequence[str]) -> PolicyDecision:
    return PolicyDecision(
        policy_decision_id=opaque_id("policy", {"run_id": manifest["run_id"], "purpose": purpose, "scope": list(revision_scope)}),
        revision_scope=tuple(revision_scope), purpose=purpose, sensitivity_consent="INTERNAL",
        allowed_artifact_types=tuple(allowed), provider_model_boundary=str(config["policy"]["provider_model_boundary"]),
        retention_class=retention, expires_at="2999-01-01T00:00:00Z", revocation_ref=None,
        egress_manifest_digest=str(config["policy"]["egress_manifest_digest"]), decision="ALLOW", effective_at_use=True,
    )


def _stage_inventory(run_dir: Path, manifest: dict[str, Any], corpus: Mapping[str, Any], config: Mapping[str, Any],
                     input_root: Path, attempt_stage: str = "inventory") -> tuple[int, dict[str, Any]]:
    revision_ids = [str(row["revision_id"]) for row in corpus["revisions"]]
    discovery = _decision(manifest, config, "DISCOVER", ("source_manifest", "discovery_authorization"), "SOURCE_REFERENCE", revision_ids)
    processing = _decision(manifest, config, "PROCESS",
                           ("window_sample_manifest", "ranked_candidate", "window_judgment", "metrics", "gate_decision"),
                           "DERIVED_REPLAYABLE", revision_ids)
    occurrences = tuple(SourceOccurrence(str(row["occurrence_id"]), str(row["revision_id"]), str(row["content_id"]),
                                         input_root / str(row["locator"]), tuple(row.get("relation_ids", ())))
                        for row in corpus["revisions"])
    media_mode = _is_media_corpus(corpus)
    media_records: list[dict[str, Any]] = []
    if media_mode:
        measurements, media_records = _media_measurements(corpus, config, input_root)
        probes = {revision_id: measurement.probe_evidence() for revision_id, measurement in measurements.items()}
    else:
        probes = {str(row["revision_id"]): ProbeEvidence(dict(row["probe"])) for row in corpus["revisions"]}
    result = inventory(occurrences=occurrences, probe_by_revision=probes, authorization=discovery,
                       output_root=run_dir, attempt_id=opaque_id("attempt", {"run_id": manifest["run_id"], "stage": "inventory"}),
                       selected_stream_index=config["windows"]["selected_stream_index"], now=FIXED_NOW)
    # Serialize the processing decision beside the discovery decision so later
    # stages cite an explicit PROCESS/ALLOW decision rather than reusing DISCOVER.
    rows = []
    text = (run_dir / "policy_decisions.jsonl").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip():
            rows.append(json.loads(line))
    rows.append({"record_id": processing.policy_decision_id, "record_type": "policy_decision",
                 "record_schema_version": "gate0.v1", "record_digest": "", "payload": processing.to_dict()})
    rows[-1]["record_digest"] = record_digest(rows[-1])
    _write_jsonl_artifact(run_dir / "policy_decisions.jsonl", _sorted_records(rows))
    manifest["policy_decision_ids"] = [discovery.policy_decision_id, processing.policy_decision_id]
    manifest["selected_streams"] = [
        {"revision_id": revision_id, "stream_index": int(index), "selection_source": source}
        for revision_id, index, source in result.payload.selected_streams
    ]
    manifest["inventory_digest"] = result.payload.inventory_digest
    if media_mode:
        media_corpus = load_media_corpus(input_root / MEDIA_CORPUS_FILE)
        for revision_id, stream_index, _source in result.payload.selected_streams:
            declared = media_corpus.revision(str(revision_id)).selected_stream_index
            if declared is not None and int(declared) != int(stream_index):
                raise ValueError("SELECTED_STREAM_MISMATCH")
        manifest["media_measurements"] = media_records
        manifest["media_tools"] = {
            # Identity of the probe / frame-evidence tools that actually produced
            # the measured PTS records.
            "ffprobe": media_records[0]["probe_tool"] if media_records else None,
            "frame_evidence": media_records[0]["frame_evidence_tool"] if media_records else None,
            # Configured ffmpeg identity, measured via ``-version`` only: sampling
            # never invokes ffmpeg (no pixel decode, no rendering, no export).
            "ffmpeg": _configured_ffmpeg_identity(config),
            "ffmpeg_used_for_sampling": False,
        }
        manifest["media_measurement_origin"] = "LOCAL_GENERATED_MEDIA_NOT_AUTHORIZED_CORPUS"
    _append_stage(manifest, run_id=manifest["run_id"], stage=attempt_stage, input_digest=manifest["spec_digest"],
                  policy_decision_id=discovery.policy_decision_id)
    _publish_manifest(run_dir, manifest)
    return 0, {"command": attempt_stage, "status": "SUCCEEDED", "evidence_state": _evidence_state(corpus),
               "run_id": manifest["run_id"]}


def _stage_split(run_dir: Path, manifest: dict[str, Any], corpus: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
    revision_ids = [str(row["revision_id"]) for row in corpus["revisions"]]
    edges = [(str(left), str(right)) for left, right in corpus.get("relations", ())]
    evaluation_seeds = tuple(sorted(row["revision_id"] for row in corpus["revisions"] if row["split"] == "EVALUATION"))
    development_seeds = tuple(sorted(row["revision_id"] for row in corpus["revisions"] if row["split"] == "DEVELOPMENT"))
    rows = freeze_relation_split(revision_ids, edges, str(manifest["inventory_digest"]),
                                 evaluation_components=evaluation_seeds, development_components=development_seeds)
    _write_json_artifact(run_dir / "split_manifest.json", {"records": list(rows)})
    manifest["split_version"] = "split-v1"
    manifest["split_digest"] = payload_digest({"records": list(rows)}, "split_manifest.json")
    _append_stage(manifest, run_id=manifest["run_id"], stage="split", input_digest=manifest["inventory_digest"],
                  policy_decision_id=manifest["policy_decision_ids"][0])
    _publish_manifest(run_dir, manifest)
    return 0, {"command": "split", "status": "SUCCEEDED", "evidence_state": _manifest_evidence_state(manifest), "run_id": manifest["run_id"]}


def _stage_label(run_dir: Path, manifest: dict[str, Any], labels: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
    query_version = str(labels.get("query_version", "queries-synthetic-v1"))
    queries = build_queries(_query_rows(labels), _query_split(labels), query_version)
    label_version = label_version_digest([row["payload"] for row in queries])
    gold = build_gold_events(_gold_inputs(labels), queries, label_version)
    _write_jsonl_artifact(run_dir / "queries.jsonl", queries)
    _write_jsonl_artifact(run_dir / "gold_events.jsonl", gold)
    manifest["query_version"] = query_version
    manifest["label_version"] = label_version
    manifest["query_version_digest"] = label_version_digest([row["payload"] for row in queries])
    manifest["gold_version_digest"] = label_version_digest([row["payload"] for row in gold])
    _append_stage(manifest, run_id=manifest["run_id"], stage="label", input_digest=manifest["spec_digest"],
                  policy_decision_id=manifest["policy_decision_ids"][1])
    _publish_manifest(run_dir, manifest)
    return 0, {"command": "label", "status": "SUCCEEDED", "evidence_state": _manifest_evidence_state(manifest), "run_id": manifest["run_id"]}


def _stage_preflight(run_dir: Path, manifest: dict[str, Any], config: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
    from gate0.launcher_attestation import sentinel_ledger_events
    ledger = _ledger(run_dir)
    attempt_id = opaque_id("attempt", {"run_id": manifest["run_id"], "stage": "preflight"})
    policy_id = manifest["policy_decision_ids"][-1]
    events = []
    for event in sentinel_ledger_events(run_id=str(manifest["run_id"]), attempt_id=attempt_id,
                                        policy_decision_id=policy_id,
                                        egress_manifest_digest=str(config["policy"]["egress_manifest_digest"]),
                                        now=FIXED_NOW):
        row = dict(event)
        # `occurred_at` is the canonical time field; the sentinel helper's extra
        # `timestamp` would duplicate it in the closed ledger event schema.
        row.pop("timestamp", None)
        row.setdefault("attempted_bytes", 1)
        row.setdefault("transmitted_bytes", 0)
        row.setdefault("payload", None)
        row.update({"event_type": "EGRESS_BLOCKED", "affected_refs": [],
                    "reason": "child network denied", "occurred_at": FIXED_NOW})
        events.append(row)
    ledger["events"] = [*ledger.get("events", []), *events]
    _publish_ledger(run_dir, ledger)
    # A synthetic execution has no host bwrap observation: the sandbox block
    # stays config-bound and the evidence class records the missing observation.
    manifest["host_sandbox_observation"] = "NOT_OBSERVED"
    manifest["sandbox_observation_source"] = "config_bound_synthetic_fixture"
    _append_stage(manifest, run_id=manifest["run_id"], stage="preflight", input_digest=manifest["spec_digest"],
                  policy_decision_id=policy_id)
    _publish_manifest(run_dir, manifest)
    return 0, {"command": "preflight", "status": "SUCCEEDED", "evidence_state": _manifest_evidence_state(manifest),
               "host_sandbox_observation": "NOT_OBSERVED", "run_id": manifest["run_id"]}


def _stage_extract(run_dir: Path, manifest: dict[str, Any], corpus: Mapping[str, Any],
                   config: Mapping[str, Any], input_root: Path) -> tuple[int, dict[str, Any]]:
    refs = _revision_refs(manifest, corpus)
    rows = _extract_rows(corpus, refs, config, input_root)
    counts = _target_counts(rows)
    if counts["succeeded"] != counts["planned"]:
        raise ValueError("INVALID_TARGET_COVERAGE")
    records = _sample_records(rows)
    _write_jsonl_artifact(run_dir / "window_sample_manifest.jsonl", records)
    manifest["sample_manifest_digest"] = payload_digest(list(records), "window_sample_manifest.jsonl")
    manifest["target_counts"] = counts
    manifest["windows"] = _window_evidence(rows)
    _append_stage(manifest, run_id=manifest["run_id"], stage="extract", input_digest=manifest["sample_manifest_digest"],
                  policy_decision_id=manifest["policy_decision_ids"][1])
    _publish_manifest(run_dir, manifest)
    return 0, {"command": "extract", "status": "SUCCEEDED", "evidence_state": _evidence_state(corpus),
               "run_id": manifest["run_id"]}


def _stage_embed(run_dir: Path, manifest: dict[str, Any], corpus: Mapping[str, Any], config: Mapping[str, Any],
                 input_root: Path) -> tuple[int, dict[str, Any]]:
    refs = _revision_refs(manifest, corpus)
    rows = _extract_rows(corpus, refs, config, input_root)
    records = _sample_records(rows)
    if payload_digest(list(records), "window_sample_manifest.jsonl") != manifest["sample_manifest_digest"]:
        raise ValueError("SAMPLE_MANIFEST_DIGEST_MISMATCH")
    attempt_id = opaque_id("attempt", {"run_id": manifest["run_id"], "stage": "embed"})
    representations, window_vectors = _representations(
        corpus, rows, str(manifest["sample_manifest_digest"]), attempt_id,
        str(config["model"]["processor_digest"]),
    )
    projections = [record.to_dict() for record in representations]
    manifest["representations"] = projections
    manifest["representation_digests"] = sorted(record.vector_digest for record in representations
                                                if record.representation_status == "SUCCEEDED")
    if not manifest["representation_digests"]:
        raise ValueError("NO_SUCCESSFUL_REPRESENTATION")
    manifest["invocations"] = [*manifest.get("invocations", []), {
        "invocation_id": opaque_id("invocation", {"run_id": manifest["run_id"], "stage": "embed"}),
        "attempt_id": attempt_id, "runtime_digest": manifest["runtime"]["tool_environment_digest"],
        "provider_status": "UNSUPPORTED", "requested_model": MODEL_IDENTITY, "resolved_model": MODEL_IDENTITY,
        "processor_digest": str(config["model"]["processor_digest"]), "output_ref": None,
    }]
    _append_stage(manifest, run_id=manifest["run_id"], stage="embed", input_digest=manifest["sample_manifest_digest"],
                  policy_decision_id=manifest["policy_decision_ids"][1])
    _publish_manifest(run_dir, manifest)
    return 0, {"command": "embed", "status": "SUCCEEDED", "evidence_state": _evidence_state(corpus),
               "run_id": manifest["run_id"]}


def _stage_rank(run_dir: Path, manifest: dict[str, Any], corpus: Mapping[str, Any], config: Mapping[str, Any],
                queries: Mapping[str, Any], query_vectors: Mapping[str, Any],
                input_root: Path) -> tuple[int, dict[str, Any]]:
    refs = _revision_refs(manifest, corpus)
    rows = _extract_rows(corpus, refs, config, input_root)
    sampling_digest = payload_digest(list(_sample_records(rows)), "window_sample_manifest.jsonl")
    if sampling_digest != manifest["sample_manifest_digest"]:
        raise ValueError("SAMPLE_MANIFEST_DIGEST_MISMATCH")
    representations, window_vectors = _representations(
        corpus, rows, sampling_digest,
        opaque_id("attempt", {"run_id": manifest["run_id"], "stage": "embed"}),
        str(config["model"]["processor_digest"]),
    )
    declared = {str(record.representation_id): record for record in representations}
    for row in manifest["representations"]:
        record = declared.get(str(row["representation_id"]))
        if record is None or record.vector_digest != row.get("vector_digest"):
            raise ValueError("REPRESENTATION_DIGEST_MISMATCH")
    evaluation_queries = [row for row in queries["queries"] if row["split"] == "EVALUATION"]
    windows = _window_entries(manifest)
    if not windows:
        raise ValueError("WINDOW_EVIDENCE_MISSING")
    metadata_records, metadata_projection = _metadata_rankings(corpus, evaluation_queries, windows)
    semantic_records, _ = _semantic_rankings(manifest, corpus, evaluation_queries, query_vectors,
                                             manifest["representations"], windows, window_vectors)
    records = _sorted_records([*metadata_records, *semantic_records])
    _write_jsonl_artifact(run_dir / "ranked_candidates.jsonl", records)
    manifest["ranking_digest"] = payload_digest(list(records), "ranked_candidates.jsonl")
    manifest["baseline_digest"] = digest_json(sorted(metadata_projection, key=lambda row: (row["query_id"], row["rank"])))
    _append_stage(manifest, run_id=manifest["run_id"], stage="rank", input_digest=manifest["ranking_digest"],
                  policy_decision_id=manifest["policy_decision_ids"][1])
    _publish_manifest(run_dir, manifest)
    return 0, {"command": "rank", "status": "SUCCEEDED", "evidence_state": _evidence_state(corpus),
               "run_id": manifest["run_id"]}


def _stage_evaluate(run_dir: Path, manifest: dict[str, Any], config: Mapping[str, Any], config_path: Path,
                    review_input: Path) -> tuple[int, dict[str, Any]]:
    queries = [row["payload"] for row in _load_json(run_dir / "queries.jsonl") if False] if False else [
        json.loads(line)["payload"] for line in (run_dir / "queries.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if queries and label_version_digest(queries) != manifest.get("query_version_digest"):
        return 30, {"command": "evaluate", "status": "INVALID_PROTOCOL",
                    "reason": "QUERY_VERSION_DIGEST_MISMATCH",
                    "evidence_state": _manifest_evidence_state(manifest)}
    gold = [json.loads(line)["payload"] for line in (run_dir / "gold_events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    candidates = [json.loads(line)["payload"] for line in (run_dir / "ranked_candidates.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    # The published ranked record carries no duplicate window coordinates (the
    # typed window record is canonical), so re-join them here for the metric
    # protocol, which evaluates technical coordinates, not the artifact surface.
    windows_by_id = {str(row["window_id"]): row for row in manifest.get("windows", [])}
    for candidate in candidates:
        window = windows_by_id.get(str(candidate.get("window_id")))
        if window is None:
            return 30, {"command": "evaluate", "status": "INVALID_PROTOCOL", "reason": "WINDOW_EVIDENCE_MISSING",
                        "evidence_state": _manifest_evidence_state(manifest)}
        candidate["revision_id"] = window["revision_id"]
        candidate["start"] = window["start"]
        candidate["end"] = window["end"]
        candidate["mapping_ref"] = window["mapping_ref"]
        candidate["origin"] = window["origin"]
        candidate["time_base"] = window["time_base"]
    token_map = _plain(config["blinding"]["token_map"])
    authorized_root = Path(str(config["policy"]["review_input"]["authorized_root"]))
    if not authorized_root.is_absolute():
        authorized_root = Path(config_path).resolve().parents[2] / authorized_root
    if not config["policy"].get("local_only", False):
        return 20, {"command": "evaluate", "status": "BLOCKED_PREREQUISITE", "reason": "REVIEW_INPUT_POLICY_DENIED"}
    # The envelope must be blind-bound to this run's canonical configuration.
    # The run manifest carries the digest the frozen loader computed at prepare
    # time; the loaded configuration must agree before that manifest evidence is
    # treated as authority.  Never bind to the placeholder zero digest.
    config_digest = str(manifest.get("config_digest", ""))
    if config_digest != canonical_config_digest(config):
        return 30, {"command": "evaluate", "status": "INVALID_PROTOCOL", "reason": "CONFIG_DIGEST_MISMATCH",
                    "evidence_state": _manifest_evidence_state(manifest)}
    expected_mapping = _mapping_digest(token_map, mapping_version=str(config["blinding"]["mapping_version"]), config_digest=config_digest)
    # The sample manifest owns technical window identity; run_manifest.windows
    # is only a projection of successfully sampled rows and can omit windows
    # whose sampling failed or was otherwise classified.
    expected_window_ids = None
    if queries:
        sample_path = run_dir / "window_sample_manifest.jsonl"
        if not sample_path.is_file():
            return 30, {"command": "evaluate", "status": "INVALID_PROTOCOL",
                        "reason": "WINDOW_IDENTITY_EVIDENCE_MISSING",
                        "evidence_state": _manifest_evidence_state(manifest)}
        try:
            sample_records = [json.loads(line) for line in sample_path.read_text(encoding="utf-8").splitlines()
                              if line.strip()]
            sample_digest = payload_digest(sample_records, "window_sample_manifest.jsonl")
            sample_ids = {str(record["payload"]["window_id"]) for record in sample_records}
        except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            return 30, {"command": "evaluate", "status": "INVALID_PROTOCOL",
                        "reason": f"WINDOW_IDENTITY_EVIDENCE_INVALID:{type(exc).__name__}",
                        "evidence_state": _manifest_evidence_state(manifest)}
        if sample_digest != manifest.get("sample_manifest_digest"):
            return 30, {"command": "evaluate", "status": "INVALID_PROTOCOL",
                        "reason": "SAMPLE_MANIFEST_DIGEST_MISMATCH",
                        "evidence_state": _manifest_evidence_state(manifest)}
        expected_window_ids = sample_ids
    try:
        envelope = load_reviewer_input(review_input, authorized_root=authorized_root, token_map=token_map,
                                       expected_mapping_digest=expected_mapping,
                                       expected_reviewer_ids=list(config["policy"]["reviewer_ids"]),
                                       expected_query_ids=({str(row["query_id"]) for row in queries} if queries else None),
                                       expected_window_ids=expected_window_ids,
                                       mapping_version=str(config["blinding"]["mapping_version"]),
                                       config_digest=config_digest)
        judgments = reviewer_judgments(envelope, token_map=token_map)
    except ValueError as exc:
        return 30, {"command": "evaluate", "status": "INVALID_PROTOCOL", "reason": f"REVIEW_INPUT:{exc}", "evidence_state": _manifest_evidence_state(manifest)}
    try:
        result = evaluate(queries, judgments,
                          ranking_digest=manifest["ranking_digest"], baseline_digest=manifest["baseline_digest"],
                          gold_version_digest=manifest["gold_version_digest"],
                          query_version_digest=manifest["query_version_digest"], validity="VALID",
                          ranked_candidates=candidates, gold_events=gold,
                          coverage=manifest.get("target_counts"))
    except ValueError as exc:
        return 30, {"command": "evaluate", "status": "INVALID_PROTOCOL", "reason": f"EVALUATION:{exc}", "evidence_state": _manifest_evidence_state(manifest)}
    arm_by_token = {str(row["blind_arm_token"]): str(row["arm_id"]) for row in token_map}
    judgment_records = []
    for row in envelope.rows:
        payload = {"judgment_id": opaque_id("judgment", {"query_id": row.query_id, "window_id": row.window_id,
                                                          "token": row.blind_arm_token, "reviewer": row.reviewer_id}),
                   "assertion_id": row.assertion_id, "query_id": row.query_id, "window_id": row.window_id,
                   "arm_id": arm_by_token[row.blind_arm_token], "reviewer_id": row.reviewer_id,
                   "grade": row.grade, "ambiguity": row.ambiguity, "review_status": row.review_status}
        judgment_records.append(_record("window_judgment", payload, payload["judgment_id"]))
    _write_jsonl_artifact(run_dir / "window_judgments.jsonl", _sorted_records(judgment_records))
    metrics = _metrics_payload(result)
    _write_json_artifact(run_dir / "metrics.json", metrics)
    manifest["metrics_digest"] = payload_digest(metrics, "metrics.json")
    manifest["judgments_digest"] = result.judgments_digest
    manifest["review_input"] = {"path": str(review_input), "digest": envelope.input_digest}
    manifest["metric_snapshot"] = {key: {"numerator": value.numerator, "denominator": value.denominator}
                                   for key, value in result.metrics.items()}
    _append_stage(manifest, run_id=manifest["run_id"], stage="evaluate", input_digest=manifest["metrics_digest"],
                  policy_decision_id=manifest["policy_decision_ids"][1])
    _publish_manifest(run_dir, manifest)
    return 0, {"command": "evaluate", "status": "SUCCEEDED", "evidence_state": _manifest_evidence_state(manifest), "run_id": manifest["run_id"]}


def _replay(run_dir: Path, manifest: Mapping[str, Any], corpus: Mapping[str, Any], labels: Mapping[str, Any],
            query_vectors: Mapping[str, Any], config: Mapping[str, Any], config_path: Path,
            input_root: Path) -> dict[str, Any]:
    refs = _revision_refs(manifest, corpus)
    rows = _extract_rows(corpus, refs, config, input_root)
    records = _sample_records(rows)
    sampling_digest = payload_digest(list(records), "window_sample_manifest.jsonl")
    representations, window_vectors = _representations(
        corpus, rows, sampling_digest, opaque_id("attempt", {"run_id": manifest["run_id"], "stage": "embed"}),
        str(config["model"]["processor_digest"]),
    )
    representation_digests = sorted(record.vector_digest for record in representations if record.representation_status == "SUCCEEDED")
    queries = [json.loads(line)["payload"] for line in (run_dir / "queries.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    evaluation_queries = [row for row in queries if row["split"] == "EVALUATION"]
    windows = _window_entries(manifest)
    metadata_records, metadata_projection = _metadata_rankings(corpus, evaluation_queries, windows)
    semantic_records, _ = _semantic_rankings(manifest, corpus, evaluation_queries, query_vectors,
                                             manifest["representations"], windows, window_vectors)
    ranked = _sorted_records([*metadata_records, *semantic_records])
    ranking_digest = payload_digest(list(ranked), "ranked_candidates.jsonl")
    baseline_digest = digest_json(sorted(metadata_projection, key=lambda row: (row["query_id"], row["rank"])))
    differences = []
    if sampling_digest != manifest["sample_manifest_digest"]:
        differences.append("sample_manifest_digest")
    if representation_digests != list(manifest["representation_digests"]):
        differences.append("representation_digests")
    if ranking_digest != manifest["ranking_digest"]:
        differences.append("ranking_digest")
    if baseline_digest != manifest["baseline_digest"]:
        differences.append("baseline_digest")
    frozen_index_equal = None
    try:
        metrics = _load_json(run_dir / "metrics.json")
        stored_digest = payload_digest(metrics, "metrics.json")
        frozen_index_equal = stored_digest == manifest.get("metrics_digest")
    except (OSError, ValueError):
        frozen_index_equal = False
    if frozen_index_equal is False:
        differences.append("metrics_digest")
    status = "EQUAL" if not differences else "INVALID_PROTOCOL"
    return {"status": status, "first_difference": differences[0] if differences else None,
            "differences": differences,
            "full_pipeline": {"sample_manifest_digest": sampling_digest,
                              "representation_digests": representation_digests,
                              "ranking_digest": ranking_digest,
                              "baseline_digest": baseline_digest},
            "frozen_index_equal": frozen_index_equal}


def _stage_report(run_dir: Path, manifest: dict[str, Any], config: Mapping[str, Any], config_path: Path,
                  input_root: Path, corpus: Mapping[str, Any], labels: Mapping[str, Any],
                  query_vectors: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
    metrics = _load_json(run_dir / "metrics.json")
    metric_objects = {row["metric_id"]: Metric(**row) for row in metrics["metrics"]}
    result = EvaluationResult(metrics=metric_objects, judgments_digest=str(manifest.get("judgments_digest", "0" * 64)),
                              decision_status="VALID", per_query={})
    replay = _replay(run_dir, manifest, corpus, labels, query_vectors, config, config_path, input_root)
    repeat_status = str(replay["status"])
    validity = "NOT_RUN" if (_is_media_corpus(corpus) or manifest.get("evidence_class") == EVIDENCE_CLASS) else "VALID"
    threshold_digest = digest_json(dict(config["thresholds"]))
    projection, payload_bytes, _digest = render_gate_decision(
        result, run_id=str(manifest["run_id"]), authority=str(config["policy"]["gate_owner_id"]),
        reviewers=list(config["policy"]["reviewer_ids"]), validity=validity, policy_status="ALLOW",
        repeat_status=repeat_status, threshold_digest=threshold_digest,
        gate_owner_id=str(manifest["gate_owner_id"]), decided_at=FIXED_NOW,
    )
    _atomic_write(run_dir / "gate_decision.md", payload_bytes)
    manifest["replay_comparison"] = replay
    manifest["threshold_digest"] = threshold_digest
    manifest["run_decision"] = {"benchmark_status": projection.benchmark_status,
                                "gate_decision": projection.gate_decision,
                                "stop_reason": projection.stop_reason,
                                "stop_reason_detail": ("GENERATED_MEDIA_NOT_AUTHORIZED_CORPUS"
                                                       if _is_media_corpus(corpus)
                                                       else "SYNTHETIC_FIXTURE_NOT_AUTHORIZED_CORPUS")
                                if validity == "NOT_RUN" else "NONE"}
    manifest["frozen_input"] = {
        "source_revision_ids": list(manifest["source_revision_ids"]),
        "sample_manifest_digest": manifest["sample_manifest_digest"],
        "representation_digests": list(manifest["representation_digests"]),
        "ranking_digest": manifest["ranking_digest"],
        "metrics_digest": manifest["metrics_digest"],
        "config_digest": manifest["config_digest"],
    }
    manifest["frozen_input_digests"] = {
        mode: frozen_input_digest(mode, manifest) for mode in ("frozen-index", "full-pipeline")
    }
    manifest["status"] = "REPORTED"
    _append_stage(manifest, run_id=manifest["run_id"], stage="report", input_digest=manifest["metrics_digest"],
                  policy_decision_id=manifest["policy_decision_ids"][1])
    manifest["status"] = "REPORTED"
    _publish_artifact_envelopes(run_dir, manifest, config)
    _publish_manifest(run_dir, manifest)
    return 20, {"command": "report", "status": projection.benchmark_status,
                "gate_decision": projection.gate_decision, "stop_reason": projection.stop_reason,
                "evidence_state": _evidence_state(corpus), "run_id": manifest["run_id"]}


# ---------------------------------------------------------------------------
# artifact envelope closure (report owns the final thirteen-artifact closure)
# ---------------------------------------------------------------------------

def _read_payloads(run_dir: Path) -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    for name in ARTIFACT_FILENAMES:
        path = run_dir / name
        if not path.exists():
            continue
        if name.endswith(".jsonl"):
            payloads[name] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        elif name == "gate_decision.md":
            payloads[name] = path.read_bytes()
        else:
            payloads[name] = _load_json(path)
    return payloads


def _envelope(artifact_type: str, payload: Any, *, producer: str, policy_id: str, retention: str,
              inputs: Sequence[ArtifactRef] = ()) -> ArtifactEnvelope:
    envelope = ArtifactEnvelope.create(artifact_type, payload, producer_attempt_id=producer,
                                       policy_decision_id=policy_id, created_at=FIXED_NOW,
                                       retention_class=retention)
    ordered = tuple(sorted(inputs, key=lambda ref: (ref.artifact_id, ref.artifact_type)))
    return replace(envelope, input_artifact_refs=ordered)


def _ref(envelope: ArtifactEnvelope) -> ArtifactRef:
    return ArtifactRef(envelope.artifact_id, envelope.payload_digest, envelope.artifact_type)


def _publish_artifact_envelopes(run_dir: Path, manifest: dict[str, Any], config: Mapping[str, Any]) -> None:
    payloads = _read_payloads(run_dir)
    missing = [name for name in ARTIFACT_FILENAMES if name not in payloads]
    if missing:
        raise ValueError(f"MISSING_ARTIFACT:{missing[0]}")
    discovery_id, processing_id = manifest["policy_decision_ids"][0], manifest["policy_decision_ids"][1]
    producer = opaque_id("attempt", {"run_id": manifest["run_id"], "stage": "report"})
    envelopes: dict[str, ArtifactEnvelope] = {}
    envelopes["source_manifest.json"] = _envelope("source_manifest.json", payloads["source_manifest.json"],
                                                  producer=producer, policy_id=discovery_id, retention="SOURCE_REFERENCE")
    envelopes["discovery_authorizations.jsonl"] = _envelope(
        "discovery_authorizations.jsonl", payloads["discovery_authorizations.jsonl"], producer=producer,
        policy_id=discovery_id, retention="AUDIT_MINIMUM", inputs=(_ref(envelopes["source_manifest.json"]),))
    envelopes["policy_decisions.jsonl"] = _envelope("policy_decisions.jsonl", payloads["policy_decisions.jsonl"],
                                                    producer=producer, policy_id=discovery_id, retention="AUDIT_MINIMUM")
    envelopes["split_manifest.json"] = _envelope("split_manifest.json", payloads["split_manifest.json"],
                                                 producer=producer, policy_id=processing_id, retention="DERIVED_REPLAYABLE",
                                                 inputs=(_ref(envelopes["source_manifest.json"]),))
    envelopes["queries.jsonl"] = _envelope("queries.jsonl", payloads["queries.jsonl"], producer=producer,
                                           policy_id=processing_id, retention="DERIVED_RESTRICTED",
                                           inputs=(_ref(envelopes["split_manifest.json"]),))
    envelopes["gold_events.jsonl"] = _envelope("gold_events.jsonl", payloads["gold_events.jsonl"], producer=producer,
                                               policy_id=processing_id, retention="DERIVED_RESTRICTED",
                                               inputs=(_ref(envelopes["queries.jsonl"]),))
    envelopes["window_sample_manifest.jsonl"] = _envelope(
        "window_sample_manifest.jsonl", payloads["window_sample_manifest.jsonl"], producer=producer,
        policy_id=processing_id, retention="DERIVED_REPLAYABLE", inputs=(_ref(envelopes["source_manifest.json"]),))
    envelopes["ranked_candidates.jsonl"] = _envelope(
        "ranked_candidates.jsonl", payloads["ranked_candidates.jsonl"], producer=producer, policy_id=processing_id,
        retention="DERIVED_REPLAYABLE",
        inputs=(_ref(envelopes["window_sample_manifest.jsonl"]), _ref(envelopes["queries.jsonl"])))
    envelopes["window_judgments.jsonl"] = _envelope(
        "window_judgments.jsonl", payloads["window_judgments.jsonl"], producer=producer, policy_id=processing_id,
        retention="AUDIT_MINIMUM", inputs=(_ref(envelopes["queries.jsonl"]), _ref(envelopes["ranked_candidates.jsonl"])))
    envelopes["metrics.json"] = _envelope(
        "metrics.json", payloads["metrics.json"], producer=producer, policy_id=processing_id,
        retention="DERIVED_REPLAYABLE",
        inputs=(_ref(envelopes["gold_events.jsonl"]), _ref(envelopes["window_judgments.jsonl"]),
                _ref(envelopes["ranked_candidates.jsonl"])))
    envelopes["gate_decision.md"] = _envelope(
        "gate_decision.md", payloads["gate_decision.md"], producer=producer, policy_id=processing_id,
        retention="AUDIT_MINIMUM", inputs=(_ref(envelopes["metrics.json"]),))
    envelopes["runtime_and_failure_ledger.json"] = _envelope(
        "runtime_and_failure_ledger.json", payloads["runtime_and_failure_ledger.json"], producer=producer,
        policy_id=processing_id, retention="AUDIT_MINIMUM")
    other_refs = tuple(_ref(envelopes[name]) for name in sorted(envelopes))
    manifest_payload = {key: value for key, value in manifest.items() if key != "artifact_envelopes"}
    envelopes["run_manifest.json"] = _envelope("run_manifest.json", manifest_payload, producer=producer,
                                               policy_id=processing_id, retention="AUDIT_MINIMUM", inputs=other_refs)
    manifest["artifact_envelopes"] = [envelopes[name].to_dict() for name in ARTIFACT_FILENAMES]


# ---------------------------------------------------------------------------
# authorized-local admission (Gate-0 D-1 preparation only)
#
# Gate-0 D-1 authorizes a *separate* fail-closed preparation path for a real,
# owner-authorized local corpus.  D-2 (genuine inputs/rights) and D-3 (execution)
# are unattested, so admission can only ever produce an explicit
# BLOCKED_PREREQUISITE refusal.  Admission itself is a filename existence check:
# the declaration is never parsed, and no declared source is opened/stat'ed.
# ---------------------------------------------------------------------------

AUTHORIZED_LOCAL_REASON = "AUTHORIZED_LOCAL_EXECUTION_NOT_AUTHORIZED"


EDITOR_QUERIES_SCHEMA_VERSION = "gate0.editor-queries.v1"
HUMAN_GOLD_SCHEMA_VERSION = "gate0.human-gold.v1"
EDITOR_QUERY_FIELDS = frozenset({"query_id", "text", "family", "presence", "split"})
HUMAN_GOLD_REQUIRED_FIELDS = ("query_id", "revision_id", "reviewer_id", "grade", "rationale",
                              "stream_index", "start", "end", "uncertainty")
HUMAN_GOLD_OPTIONAL_FIELDS = frozenset({
    "adjudication_ref", "adjudicated_grade", "time_domain", "time_base", "review_status",
    "evidence_class", "origin", "precision", "refinement_eligibility", "producer_attempt_id",
})
# Closed vocabularies copied from the frozen schemas/gate0/gold_events.json enums.
HUMAN_GOLD_EVIDENCE_CLASSES = frozenset({
    "MEASURED", "MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED", "EDITORIAL_INFERENCE"})
HUMAN_GOLD_REVIEW_STATUSES = frozenset({"UNREVIEWED", "ACCEPTED", "REJECTED", "AMBIGUOUS"})
HUMAN_GOLD_REFINEMENT_ELIGIBILITY = frozenset({"ELIGIBLE", "INELIGIBLE"})
LABEL_INPUT_MAX_BYTES = 2 * 1024 * 1024


def _authorized_input_require(condition: bool, reason: str, detail: str = "") -> None:
    if not condition:
        raise AuthorizedLocalError(reason, detail)


def _authorized_input_document(path: str | Path, reason: str) -> Mapping[str, Any]:
    """Read a *label input* file (never a declared source path)."""
    label_path = Path(path)
    try:
        input_size = label_path.stat().st_size
    except OSError as exc:
        raise AuthorizedLocalError(reason, type(exc).__name__) from exc
    _authorized_input_require(input_size <= LABEL_INPUT_MAX_BYTES,
                              "AUTHORIZED_LABEL_INPUT_TOO_LARGE", str(input_size))
    try:
        raw = label_path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorizedLocalError(reason, type(exc).__name__) from exc
    _authorized_input_require(isinstance(document, Mapping), reason, "document must be an object")
    return document


def _authorized_input_string(value: Any, field: str, reason: str) -> str:
    _authorized_input_require(isinstance(value, str) and bool(value.strip()), reason, field)
    return value


def _authorized_input_opaque(value: Any, field: str, reason: str) -> str:
    text = _authorized_input_string(value, field, reason)
    try:
        validate_opaque_id(text)
    except ValueError as exc:
        raise AuthorizedLocalError(reason, f"{field}: {exc}") from exc
    return text


def _authorized_input_rational(value: Any, field: str, reason: str) -> Any:
    """Validate — but do not rewrite — an exact rational (reduced later by labels)."""
    if isinstance(value, Mapping):
        if set(value) != {"numerator", "denominator"}:
            _authorized_input_require(False, reason, f"{field}: not an exact rational")
        numerator, denominator = value["numerator"], value["denominator"]
    elif isinstance(value, (tuple, list)):
        if len(value) != 2:
            _authorized_input_require(False, reason, f"{field}: not an exact rational pair")
        numerator, denominator = value[0], value[1]
    else:
        _authorized_input_require(False, reason, f"{field}: not an exact rational")
    for component in (numerator, denominator):
        _authorized_input_require(isinstance(component, int) and not isinstance(component, bool),
                                  reason, f"{field}: components must be integers")
    _authorized_input_require(denominator != 0, reason, f"{field}: zero denominator")
    return value


def _load_editor_queries_document(path: str | Path) -> tuple[str, tuple[dict[str, Any], ...]]:
    document = _authorized_input_document(path, "AUTHORIZED_EDITOR_QUERIES_INVALID")
    _authorized_input_require(document.get("schema_version") == EDITOR_QUERIES_SCHEMA_VERSION,
                              "AUTHORIZED_EDITOR_QUERIES_SCHEMA_MISMATCH",
                              f"expected {EDITOR_QUERIES_SCHEMA_VERSION}")
    query_version = _authorized_input_string(document.get("query_version"), "query_version",
                                             "AUTHORIZED_EDITOR_QUERIES_INVALID")
    raw_queries = document.get("queries")
    _authorized_input_require(isinstance(raw_queries, Sequence) and not isinstance(raw_queries, str)
                              and len(raw_queries) > 0,
                              "AUTHORIZED_EDITOR_QUERIES_INVALID", "queries must be a non-empty list")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(raw_queries):
        _authorized_input_require(isinstance(row, Mapping), "AUTHORIZED_EDITOR_QUERIES_INVALID",
                                  f"queries[{index}]")
        _authorized_input_require(set(row) == EDITOR_QUERY_FIELDS, "AUTHORIZED_EDITOR_QUERIES_INVALID",
                                  f"queries[{index}] fields {sorted(row)}")
        query_id = _authorized_input_opaque(row["query_id"], "query_id",
                                           "AUTHORIZED_EDITOR_QUERIES_INVALID")
        text = _authorized_input_string(row["text"], "text", "AUTHORIZED_EDITOR_QUERIES_INVALID")
        family = row["family"]
        presence = row["presence"]
        split = row["split"]
        _authorized_input_require(family in LABEL_FAMILIES, "AUTHORIZED_EDITOR_QUERIES_INVALID",
                                  f"queries[{index}].family {family!r}")
        _authorized_input_require(presence in LABEL_PRESENCE, "AUTHORIZED_EDITOR_QUERIES_INVALID",
                                  f"queries[{index}].presence {presence!r}")
        _authorized_input_require(split in ("EVALUATION", "DEVELOPMENT"),
                                  "AUTHORIZED_EDITOR_QUERIES_INVALID", f"queries[{index}].split {split!r}")
        _authorized_input_require(query_id not in seen, "AUTHORIZED_EDITOR_QUERIES_INVALID",
                                  f"duplicate query_id {query_id}")
        seen.add(query_id)
        rows.append({"query_id": query_id, "text": text, "family": family,
                     "presence": presence, "split": split})
    return query_version, tuple(rows)


def load_editor_queries(path: str | Path) -> tuple[dict[str, Any], ...]:
    """Load the declared editor-query set; cardinality is enforced by ``labels``."""
    _, rows = _load_editor_queries_document(path)
    return rows


def _load_human_gold_document(path: str | Path) -> tuple[str, tuple[dict[str, Any], ...]]:
    document = _authorized_input_document(path, "AUTHORIZED_HUMAN_GOLD_INVALID")
    _authorized_input_require(document.get("schema_version") == HUMAN_GOLD_SCHEMA_VERSION,
                              "AUTHORIZED_HUMAN_GOLD_SCHEMA_MISMATCH",
                              f"expected {HUMAN_GOLD_SCHEMA_VERSION}")
    label_version = _authorized_input_string(document.get("label_version"), "label_version",
                                             "AUTHORIZED_HUMAN_GOLD_INVALID")
    raw_events = document.get("events")
    _authorized_input_require(isinstance(raw_events, Sequence) and not isinstance(raw_events, str)
                              and len(raw_events) > 0,
                              "AUTHORIZED_HUMAN_GOLD_INVALID", "events must be a non-empty list")
    events: list[dict[str, Any]] = []
    seen: set[tuple] = set()
    for index, row in enumerate(raw_events):
        _authorized_input_require(isinstance(row, Mapping), "AUTHORIZED_HUMAN_GOLD_INVALID",
                                  f"events[{index}]")
        missing = [field for field in HUMAN_GOLD_REQUIRED_FIELDS if field not in row]
        _authorized_input_require(not missing, "AUTHORIZED_HUMAN_GOLD_INVALID",
                                  f"events[{index}] missing {missing}")
        unknown = set(row) - set(HUMAN_GOLD_REQUIRED_FIELDS) - HUMAN_GOLD_OPTIONAL_FIELDS
        _authorized_input_require(not unknown, "AUTHORIZED_HUMAN_GOLD_INVALID",
                                  f"events[{index}] unknown {sorted(unknown)}")
        if "evidence_class" in row:
            evidence_class = row["evidence_class"]
            _authorized_input_require(
                isinstance(evidence_class, str) and evidence_class in HUMAN_GOLD_EVIDENCE_CLASSES,
                "AUTHORIZED_HUMAN_GOLD_EVIDENCE_CLASS_UNKNOWN",
                f"events[{index}].evidence_class {evidence_class!r}")
        if "review_status" in row:
            review_status = row["review_status"]
            _authorized_input_require(
                isinstance(review_status, str) and review_status in HUMAN_GOLD_REVIEW_STATUSES,
                "AUTHORIZED_HUMAN_GOLD_REVIEW_STATUS_UNKNOWN",
                f"events[{index}].review_status {review_status!r}")
        if "refinement_eligibility" in row:
            refinement_eligibility = row["refinement_eligibility"]
            _authorized_input_require(
                isinstance(refinement_eligibility, str)
                and refinement_eligibility in HUMAN_GOLD_REFINEMENT_ELIGIBILITY,
                "AUTHORIZED_HUMAN_GOLD_REFINEMENT_ELIGIBILITY_UNKNOWN",
                f"events[{index}].refinement_eligibility {refinement_eligibility!r}")
        if "time_domain" in row:
            time_domain = row["time_domain"]
            _authorized_input_require(
                isinstance(time_domain, str) and time_domain in LABEL_TIME_DOMAINS,
                "AUTHORIZED_HUMAN_GOLD_TIME_DOMAIN_UNKNOWN",
                f"events[{index}].time_domain {time_domain!r}")
        if "adjudicated_grade" in row:
            adjudicated = row["adjudicated_grade"]
            _authorized_input_require(isinstance(adjudicated, int)
                                      and not isinstance(adjudicated, bool)
                                      and adjudicated in (0, 1, 2),
                                      "AUTHORIZED_HUMAN_GOLD_INVALID",
                                      f"events[{index}].adjudicated_grade {adjudicated!r}")
        if "origin" in row:
            _authorized_input_rational(row["origin"], "origin", "AUTHORIZED_HUMAN_GOLD_INVALID")
        if "time_base" in row:
            _authorized_input_rational(row["time_base"], "time_base",
                                       "AUTHORIZED_HUMAN_GOLD_INVALID")
        if "precision" in row:
            _authorized_input_string(row["precision"], "precision", "AUTHORIZED_HUMAN_GOLD_INVALID")
        if "producer_attempt_id" in row:
            _authorized_input_opaque(row["producer_attempt_id"], "producer_attempt_id",
                                     "AUTHORIZED_HUMAN_GOLD_INVALID")
        if "adjudication_ref" in row:
            _authorized_input_opaque(row["adjudication_ref"], "adjudication_ref",
                                     "AUTHORIZED_HUMAN_GOLD_INVALID")
        query_id = _authorized_input_opaque(row["query_id"], "query_id", "AUTHORIZED_HUMAN_GOLD_INVALID")
        revision_id = _authorized_input_opaque(row["revision_id"], "revision_id",
                                               "AUTHORIZED_HUMAN_GOLD_INVALID")
        reviewer_id = _authorized_input_opaque(row["reviewer_id"], "reviewer_id",
                                               "AUTHORIZED_HUMAN_GOLD_INVALID")
        rationale = _authorized_input_string(row["rationale"], "rationale",
                                             "AUTHORIZED_HUMAN_GOLD_INVALID")
        grade = row["grade"]
        _authorized_input_require(isinstance(grade, int) and not isinstance(grade, bool)
                                  and grade in (0, 1, 2),
                                  "AUTHORIZED_HUMAN_GOLD_INVALID", f"events[{index}].grade {grade!r}")
        stream_index = row["stream_index"]
        _authorized_input_require(isinstance(stream_index, int) and not isinstance(stream_index, bool)
                                  and stream_index >= 0,
                                  "AUTHORIZED_HUMAN_GOLD_INVALID",
                                  f"events[{index}].stream_index {stream_index!r}")
        start = _authorized_input_rational(row["start"], "start", "AUTHORIZED_HUMAN_GOLD_INVALID")
        end = _authorized_input_rational(row["end"], "end", "AUTHORIZED_HUMAN_GOLD_INVALID")
        uncertainty = row["uncertainty"]
        _authorized_input_require(isinstance(uncertainty, Mapping), "AUTHORIZED_HUMAN_GOLD_INVALID",
                                  f"events[{index}].uncertainty")
        uncertainty_keys = set(uncertainty)
        _authorized_input_require(uncertainty_keys == {"start", "end"}
                                  or uncertainty_keys == {"lower", "upper"},
                                  "AUTHORIZED_HUMAN_GOLD_INVALID",
                                  f"events[{index}].uncertainty keys {sorted(uncertainty_keys)}")
        for key, value in uncertainty.items():
            _authorized_input_rational(value, f"uncertainty.{key}", "AUTHORIZED_HUMAN_GOLD_INVALID")
        key = (query_id, revision_id, reviewer_id, tuple(start) if isinstance(start, (list, tuple)) else repr(start),
               tuple(end) if isinstance(end, (list, tuple)) else repr(end))
        _authorized_input_require(key not in seen, "AUTHORIZED_HUMAN_GOLD_INVALID",
                                  f"duplicate gold event at events[{index}]")
        seen.add(key)
        events.append({"query_id": query_id, "revision_id": revision_id,
                       "reviewer_id": reviewer_id, "grade": grade, "rationale": rationale,
                       "stream_index": stream_index, "start": start, "end": end,
                       "uncertainty": dict(uncertainty),
                       **{field: row[field] for field in HUMAN_GOLD_OPTIONAL_FIELDS if field in row}})
    return label_version, tuple(events)


def load_human_gold(path: str | Path) -> tuple[dict[str, Any], ...]:
    """Load the declared human-gold rows; two-reviewer/join rules stay in ``labels``."""
    _, events = _load_human_gold_document(path)
    return events


# Contract A3 (docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md and
# docs/superpowers/plans/2026-10-25-gate0-d1-source-only-preparation.md): forty
# editor queries = 32 EVALUATION (24 positive at six per family + 8 absent) and
# 8 DEVELOPMENT.  The frozen builders enforce the totals; this guard pins the
# per-family distribution they do not see.
EVALUATION_QUERY_COUNT = 32
EVALUATION_POSITIVE_COUNT = 24
EVALUATION_ABSENT_COUNT = 8
POSITIVE_PER_FAMILY = 6
DEVELOPMENT_QUERY_COUNT = 8


def _authorized_query_cardinality(queries: Iterable[Mapping[str, Any]]) -> None:
    """Pin the per-family/absent/development distribution of the 40 queries."""
    rows = list(queries)
    evaluation = [row for row in rows if row.get("split") == "EVALUATION"]
    development = [row for row in rows if row.get("split") == "DEVELOPMENT"]
    positives = [row for row in evaluation if row.get("presence") == "POSITIVE"]
    absent = [row for row in evaluation if row.get("presence") == "ABSENT"]
    for family in sorted({row.get("family") for row in positives}):
        count = sum(1 for row in positives if row.get("family") == family)
        if count != POSITIVE_PER_FAMILY:
            raise AuthorizedLocalError(
                "AUTHORIZED_QUERY_CARDINALITY_INVALID",
                f"family {family} POSITIVE {count} != {POSITIVE_PER_FAMILY}")
    if len(positives) != EVALUATION_POSITIVE_COUNT:
        raise AuthorizedLocalError(
            "AUTHORIZED_QUERY_CARDINALITY_INVALID",
            f"EVALUATION POSITIVE {len(positives)} != {EVALUATION_POSITIVE_COUNT}")
    if len(absent) != EVALUATION_ABSENT_COUNT:
        raise AuthorizedLocalError(
            "AUTHORIZED_QUERY_CARDINALITY_INVALID",
            f"EVALUATION ABSENT {len(absent)} != {EVALUATION_ABSENT_COUNT}")
    if len(development) != DEVELOPMENT_QUERY_COUNT:
        raise AuthorizedLocalError(
            "AUTHORIZED_QUERY_CARDINALITY_INVALID",
            f"DEVELOPMENT {len(development)} != {DEVELOPMENT_QUERY_COUNT}")
    if len(evaluation) != EVALUATION_QUERY_COUNT:
        raise AuthorizedLocalError(
            "AUTHORIZED_QUERY_CARDINALITY_INVALID",
            f"EVALUATION {len(evaluation)} != {EVALUATION_QUERY_COUNT}")


def prepare_authorized_label_inputs(*, declaration: Any, editor_queries_path: str | Path,
                                    human_gold_path: str | Path) -> dict[str, Any]:
    """Build typed label projections for the future real-corpus run.

    Gold assertions may only reference EVALUATION revisions declared in this
    corpus.  The frozen ``labels`` builders remain the single authority for
    cardinality, reviewer independence and join rules; their ``ValueError``
    surfaces unchanged.  Human judgements never enter the ranker projection.
    """
    if not isinstance(declaration, AuthorizedLocalCorpus):
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                                   "declaration must be an AuthorizedLocalCorpus")
    query_version, editor_rows = _load_editor_queries_document(editor_queries_path)
    label_version, gold_rows = _load_human_gold_document(human_gold_path)

    evaluation_ids = set(declaration.evaluation_revision_ids)
    for event in gold_rows:
        revision_id = event["revision_id"]
        try:
            revision = declaration.revision(revision_id)
        except AuthorizedLocalError as exc:
            raise AuthorizedLocalError("AUTHORIZED_GOLD_REVISION_UNKNOWN", revision_id) from exc
        if revision.split != "EVALUATION" or revision_id not in evaluation_ids:
            raise AuthorizedLocalError("AUTHORIZED_GOLD_REVISION_NOT_EVALUATION", revision_id)

    specs = [(row["query_id"], row["text"], (row["family"], row["presence"]))
             for row in editor_rows]
    split_by_id = {row["query_id"]: row["split"] for row in editor_rows}
    queries = build_queries(specs, split_by_id, query_version)
    _authorized_query_cardinality([record["payload"] for record in queries])
    gold_events = build_gold_events(gold_rows, queries, label_version)
    return {
        "queries": list(queries),
        "gold_events": list(gold_events),
        "ranker_inputs": ranking_inputs(queries),
        "gold_excluded_from_ranker": True,
    }


MODEL_PLACEHOLDER_VALUES = frozenset(
    {"", "NOT_OBSERVED", "TODO", "TBD", "PLACEHOLDER", "UNKNOWN", "NONE", "N/A", "PENDING"}
)
MODEL_BLOCKER_IDENTITY = "MODEL_IDENTITY_NOT_OBSERVED"
MODEL_BLOCKER_WEIGHTS = "MODEL_WEIGHTS_DIGEST_MISSING"
MODEL_BLOCKER_PROCESSOR = "MODEL_PROCESSOR_DIGEST_PLACEHOLDER"
MODEL_BLOCKER_LICENCE = "MODEL_LICENCE_MISSING"
MODEL_BLOCKER_PRECISION = "MODEL_RUNTIME_PRECISION_MISSING"
MODEL_BLOCKER_SANDBOX = "MODEL_SANDBOX_BINDING_MISSING"
DECODE_PIXELS_BLOCKER = "DECODE_PIXELS_NOT_AUTHORIZED"
_ZERO_SHA256 = "0" * 64


def _placeholder_string(value: Any) -> bool:
    return (not isinstance(value, str)) or value.strip().upper() in MODEL_PLACEHOLDER_VALUES


def _declared_sha256(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        validate_digest(value)
    except ValueError:
        return False
    return value != _ZERO_SHA256


def _config_section(config: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(config, Mapping):
        return {}
    section = config.get(name)
    return section if isinstance(section, Mapping) else {}


def _sandbox_binding_present(sandbox: Mapping[str, Any]) -> bool:
    """A sandbox binding is declared only by a fully observed execution sandbox."""
    sandbox_id = sandbox.get("sandbox_id")
    bwrap_version = sandbox.get("bwrap_version")
    return (
        not _placeholder_string(sandbox_id)
        and not _placeholder_string(bwrap_version)
        and _declared_sha256(sandbox.get("bwrap_digest"))
        and _declared_sha256(sandbox.get("interpreter_digest"))
    )


def model_preconditions(config: Mapping[str, Any]) -> dict[str, Any]:
    """Deterministic, config-only view of the semantic-arm model preconditions.

    D-1 must not consult installed packages, environment variables, filesystem
    model directories or import probing: the answer is identical whether or not
    torch/transformers exist.  Every placeholder in the config is reported as a
    blocker identity; nothing is inferred.
    """
    model = _config_section(config, "model")
    sandbox = _config_section(config, "sandbox")
    blockers: list[str] = []

    model_identity = model.get("model_identity")
    if _placeholder_string(model_identity):
        blockers.append(MODEL_BLOCKER_IDENTITY)
    weights_digest = model.get("weights_digest")
    if not _declared_sha256(weights_digest):
        blockers.append(MODEL_BLOCKER_WEIGHTS)
    processor_digest = model.get("processor_digest")
    if not _declared_sha256(processor_digest):
        blockers.append(MODEL_BLOCKER_PROCESSOR)
    dimension = model.get("dimension")
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension <= 0:
        if MODEL_BLOCKER_IDENTITY not in blockers:
            blockers.append(MODEL_BLOCKER_IDENTITY)
    runtime_precision = model.get("runtime_precision")
    if _placeholder_string(runtime_precision):
        blockers.append(MODEL_BLOCKER_PRECISION)
    licence = model.get("licence")
    if _placeholder_string(licence):
        blockers.append(MODEL_BLOCKER_LICENCE)
    if not _sandbox_binding_present(sandbox):
        blockers.append(MODEL_BLOCKER_SANDBOX)

    return {
        "config_complete": not blockers,
        "gate_open": authorized_local_execution_gate_open(config),
        "blockers": tuple(blockers),
        "model_identity": model_identity if isinstance(model_identity, str) else "NOT_OBSERVED",
        "weights_digest": weights_digest if isinstance(weights_digest, str) else None,
        "processor_digest": processor_digest if isinstance(processor_digest, str) else None,
        "dimension": dimension if isinstance(dimension, int) and not isinstance(dimension, bool) else 0,
        "runtime_precision": runtime_precision if isinstance(runtime_precision, str) else None,
        "decode_pixels": False,
    }


def authorized_local_execution_gate_open(config: Mapping[str, Any]) -> bool:
    """The real-mode (D-3) operational gate.

    D-1 authorizes source-only preparation, so this gate is closed for every
    configuration.  Opening it requires an explicit Owner D-3 authorization in
    an authorized change — no config value can open it today.
    """
    return False


def decoder_capability(*, config: Mapping[str, Any], decode_pixels: bool = False) -> dict[str, Any]:
    """Report whether real decoding/pixel access would be permitted.

    Under D-1 it never is: the D-3 gate is closed, so the status stays
    ``BLOCKED_PREREQUISITE`` even when the model preconditions are declared.
    ``decode_pixels=True`` additionally records ``DECODE_PIXELS_NOT_AUTHORIZED``.
    No decoder is constructed and no source is touched.
    """
    model = model_preconditions(config)
    gate_open = authorized_local_execution_gate_open(config)
    blockers = list(model["blockers"])
    if decode_pixels and not gate_open:
        blockers.append(DECODE_PIXELS_BLOCKER)
    status = "BLOCKED_PREREQUISITE" if (blockers or not gate_open) else "READY"
    return {
        "status": status,
        "decode_pixels": bool(decode_pixels),
        "gate_open": gate_open,
        "model_config_complete": model["config_complete"],
        "blockers": tuple(blockers),
    }


@dataclass(frozen=True)
class DeferredSiglipSeam:
    """A declared-only SigLIP asset seam.

    It names the assets a future authorized load would need and refuses to load
    them.  It never imports torch/transformers, never touches ``model_root`` on
    disk and never calls ``LocalSiglipEmbeddingAdapter.load_cpu``.
    """

    model_root: str
    revision: str
    weights_sha256: str
    processor_digest: str
    preprocessing_digest: str
    dimension: int
    runtime_precision: str
    licence: str

    @property
    def is_loaded(self) -> bool:
        return False

    def load(self) -> Any:
        raise RuntimeError("AUTHORIZED_LOCAL_MODEL_LOAD_NOT_AUTHORIZED")


def _deferred_siglip_identity(config: Mapping[str, Any]) -> dict[str, Any]:
    model = _config_section(config, "model")
    missing: list[str] = []

    model_root = model.get("model_root")
    if _placeholder_string(model_root):
        missing.append("model_root")
    revision = model.get("revision")
    if _placeholder_string(revision):
        missing.append("revision")
    weights_sha256 = model.get("weights_digest")
    if not _declared_sha256(weights_sha256):
        missing.append("weights_digest")
    processor_digest = model.get("processor_digest")
    if not _declared_sha256(processor_digest):
        missing.append("processor_digest")
    preprocessing_digest = model.get("preprocessing_digest")
    if not _declared_sha256(preprocessing_digest):
        missing.append("preprocessing_digest")
    dimension = model.get("dimension")
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension <= 0:
        missing.append("dimension")
    runtime_precision = model.get("runtime_precision")
    if _placeholder_string(runtime_precision):
        missing.append("runtime_precision")
    licence = model.get("licence")
    if _placeholder_string(licence):
        missing.append("licence")

    if missing:
        raise AuthorizedLocalError("AUTHORIZED_LOCAL_MODEL_NOT_DECLARED",
                                   "incomplete model identity: " + ", ".join(missing))
    return {
        "model_root": model_root,
        "revision": revision,
        "weights_sha256": weights_sha256,
        "processor_digest": processor_digest,
        "preprocessing_digest": preprocessing_digest,
        "dimension": dimension,
        "runtime_precision": runtime_precision,
        "licence": licence,
    }


def build_deferred_siglip_seam(config: Mapping[str, Any]) -> DeferredSiglipSeam:
    """Build the declared-only SigLIP seam; loading stays deferred/refused."""
    return DeferredSiglipSeam(**_deferred_siglip_identity(config))


def has_authorized_local_input(input_root: str | Path) -> bool:
    """True only when the authorized-local declaration file is present.

    Filename existence only: no JSON parse, no policy decision, no source access.
    """
    return (Path(input_root) / AUTHORIZED_CORPUS_FILE).is_file()


def authorized_local_refusal(*, stage: str, input_root: str | Path) -> dict[str, Any]:
    """The explicit non-executable projection for an authorized-local attempt.

    Loading the declaration is best-effort so that a malformed declaration is
    still refused (never silently downgraded to the synthetic/media paths).  It
    must never raise and it must never read run_manifest/config/media.
    """
    input_root = Path(input_root)
    declaration_digest: str | None = None
    declaration_error: str | None = None
    blockers: list[str] = list(AUTHORIZED_EXECUTION_BLOCKERS)
    try:
        corpus = load_authorized_local_declaration(input_root / AUTHORIZED_CORPUS_FILE)
    except AuthorizedLocalError as exc:
        declaration_error = str(exc)
    except Exception as exc:  # refusal must never raise, whatever the declaration
        declaration_error = f"{type(exc).__name__}: {exc}"
    else:
        declaration_digest = corpus.declaration_digest
        blockers = list(validate_authorized_local_declaration(corpus))
    for blocker in AUTHORIZED_EXECUTION_BLOCKERS:
        if blocker not in blockers:
            blockers.append(blocker)
    return {
        "command": stage,
        "status": "BLOCKED_PREREQUISITE",
        "reason": AUTHORIZED_LOCAL_REASON,
        "evidence_state": AUTHORIZED_EVIDENCE_CLASS,
        "source_access_attempted": False,
        "declaration_digest": declaration_digest,
        "blockers": blockers,
        "declaration_error": declaration_error,
    }


# ---------------------------------------------------------------------------
# public stage entrypoint
# ---------------------------------------------------------------------------

def execute_stage(stage: str, *, run: Path, config_path: Path, input_root: Path, output_root: Path,
                  run_id: str, review_input: Path | None = None) -> tuple[int, dict[str, Any]]:
    run = Path(run).resolve()
    input_root = Path(input_root).resolve()
    if has_authorized_local_input(input_root):
        # Defence in depth: a caller that bypasses the CLI still cannot execute.
        raise AuthorizedLocalError(
            AUTHORIZED_LOCAL_REASON,
            "D-2 authorized corpus inputs pending; D-3 execution not authorized",
        )
    if not (has_synthetic_input(input_root) or has_media_input(input_root)):
        raise FileNotFoundError("GENERATED_INPUT_MISSING")
    corpus, labels, query_vectors = _load_inputs(input_root)
    loaded = load_config(Path(config_path))
    config = loaded.config
    if stage == "prepare":
        return _stage_prepare(run, run_id, corpus, labels, query_vectors, config, loaded.config_digest, loaded.dependency_lock_digest)
    try:
        manifest = _load_json(run / MANIFEST_FILE)
    except (OSError, ValueError) as exc:
        raise ValueError("MALFORMED_MANIFEST") from exc
    ledger = _ledger(run)
    try:
        if stage == "inventory":
            return _stage_inventory(run, manifest, corpus, config, input_root)
        if stage == "split":
            return _stage_split(run, manifest, corpus)
        if stage == "label":
            return _stage_label(run, manifest, labels)
        if stage == "preflight":
            return _stage_preflight(run, manifest, config)
        if stage == "extract":
            return _stage_extract(run, manifest, corpus, config, input_root)
        if stage == "embed":
            manifest["model_processor_digest"] = str(config["model"]["processor_digest"])
            return _stage_embed(run, manifest, corpus, config, input_root)
        if stage == "rank":
            queries = {"queries": [json.loads(line)["payload"] for line in
                                   (run / "queries.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]}
            return _stage_rank(run, manifest, corpus, config, queries, query_vectors, input_root)
        if stage == "evaluate":
            if review_input is None:
                raise ValueError("REVIEW_INPUT_REQUIRED")
            return _stage_evaluate(run, manifest, config, Path(config_path), Path(review_input))
        if stage == "report":
            return _stage_report(run, manifest, config, Path(config_path), input_root, corpus, labels, query_vectors)
    except ValueError as exc:
        return _seal_failure(run, manifest, ledger, stage, str(exc))
    raise ValueError("UNKNOWN_STAGE")
