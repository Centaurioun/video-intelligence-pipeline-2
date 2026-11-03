"""Model-free three-profile product-path compatibility and refusal regressions.

Covers B08-SYN-01 across the three closed profiles:
- ``vip-v1-siglip-base-224`` (768D, 224 / patch 16, 3072-byte row width)
- ``vip-v2-siglip2-base-224`` (768D, 224 / patch 16, 3072-byte row width)
- ``vip-v2-siglip2-so400m-384`` (1152D, 384 / patch 14, 4608-byte row width)

All fixtures and vectors in this module are explicitly synthetic. They validate
profile identity separation, row-width geometry, coordinator/CLI propagation,
fail-closed refusal ordering, and nonbinding candidate locator preservation
without loading model weights, touching media decoders, or invoking providers.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping, Sequence

import numpy as np
import pytest

from persistent_local_index import storage
from persistent_local_index.embedding import build_fake_profile_runtime, l2_normalize
from persistent_local_index.model_profile import (
     CLOSED_PROFILE_IDS,
    ModelProfile,
    profile_row_width_bytes,
    profile_semantic_space,
    validate_model_profile,
)
from persistent_local_index.model_space import (
    TEXT_PREPROCESSING_CONTRACT,
    GenerationSpec,
    SemanticSpace,
    build_generation_spec,
    semantic_space_id,
)
from persistent_local_index.siglip2_native import create_adapter
from vip_fvs import cli, coordinator, local_semantic, multi_source_retrieval, retrieval_adapter
from vip_fvs.semantic_index import (
    IndexSummary,
    PersistentLocalSemanticIndexEngine,
    SearchHit,
)
from vip_fvs.source_adapter import MultiSourceManifest, SourceManifestEntry

V1_PROFILE_ID = "vip-v1-siglip-base-224"
V2_BASE_PROFILE_ID = "vip-v2-siglip2-base-224"
V2_SO400M_PROFILE_ID = "vip-v2-siglip2-so400m-384"

THREE_PROFILE_IDS: tuple[str, str, str] = (
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
)
V2_PROFILE_IDS: tuple[str, str] = (
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
)


def _compute_processor_digest(assets: Sequence[tuple[str, str]]) -> str:
    payload = json.dumps(
        {
            "identity_mapping": "vip-processor-assets-v1",
            "assets": [
                {"name": name, "sha256": digest}
                for name, digest in sorted(assets, key=lambda item: item[0])
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _synthetic_profile_payload(
    profile_id: str, **overrides: Any
) -> dict[str, Any]:
    """Construct a deterministic, unmistakably synthetic profile JSON payload."""
    if profile_id == V1_PROFILE_ID:
        assets = (("tokenizer.json", "1" * 64),)
        base: dict[str, Any] = {
            "profile_id": V1_PROFILE_ID,
            "model_id": "google/siglip-base-patch16-224",
            "family": "siglip",
            "frozen_revision": "a" * 40,
            "weights_sha256": "2" * 64,
            "processor_asset_digests": [list(item) for item in assets],
            "processor_digest": _compute_processor_digest(assets),
            "image_preprocessing_digest": "3" * 64,
            "text_preprocessing_contract": TEXT_PREPROCESSING_CONTRACT,
            "image_size": 224,
            "patch_size": 16,
            "embedding_dim": 768,
            "output_dtype": "float32",
            "normalization": "l2",
            "loader_kind": "siglip-v1",
            "device_backend": "pytorch-cpu",
            "precision_policy_id": "siglip2-fp16-compute-fp32-output",
            "precision_policy_version": 1,
        }
    elif profile_id == V2_BASE_PROFILE_ID:
        assets = (("tokenizer.json", "4" * 64),)
        base = {
            "profile_id": V2_BASE_PROFILE_ID,
            "model_id": "google/siglip2-base-patch16-224",
            "family": "siglip2",
            "frozen_revision": "b" * 40,
            "weights_sha256": "5" * 64,
            "processor_asset_digests": [list(item) for item in assets],
            "processor_digest": _compute_processor_digest(assets),
            "image_preprocessing_digest": "6" * 64,
            "text_preprocessing_contract": f"{V2_BASE_PROFILE_ID}:text-synthetic:v1",
            "image_size": 224,
            "patch_size": 16,
            "embedding_dim": 768,
            "output_dtype": "float32",
            "normalization": "l2",
            "loader_kind": "siglip2-auto",
            "device_backend": "pytorch-cpu",
            "precision_policy_id": "siglip2-fp16-compute-fp32-output",
            "precision_policy_version": 1,
        }
    elif profile_id == V2_SO400M_PROFILE_ID:
        assets = (("tokenizer.json", "7" * 64),)
        base = {
            "profile_id": V2_SO400M_PROFILE_ID,
            "model_id": "google/siglip2-so400m-patch14-384",
            "family": "siglip2",
            "frozen_revision": "c" * 40,
            "weights_sha256": "8" * 64,
            "processor_asset_digests": [list(item) for item in assets],
            "processor_digest": _compute_processor_digest(assets),
            "image_preprocessing_digest": "9" * 64,
            "text_preprocessing_contract": f"{V2_SO400M_PROFILE_ID}:text-synthetic:v1",
            "image_size": 384,
            "patch_size": 14,
            "embedding_dim": 1152,
            "output_dtype": "float32",
            "normalization": "l2",
            "loader_kind": "siglip2-auto",
            "device_backend": "pytorch-cpu",
            "precision_policy_id": "siglip2-fp16-compute-fp32-output",
            "precision_policy_version": 1,
        }
    else:
        raise ValueError(f"Unexpected profile_id: {profile_id!r}")

    if "processor_asset_digests" in overrides and "processor_digest" not in overrides:
        raw_assets = overrides["processor_asset_digests"]
        tuple_assets = tuple((str(k), str(v)) for k, v in raw_assets)
        overrides["processor_digest"] = _compute_processor_digest(tuple_assets)
    base.update(overrides)
    return base


def _synthetic_profile(profile_id: str, **overrides: Any) -> ModelProfile:
    payload = _synthetic_profile_payload(profile_id, **overrides)
    assets = tuple(tuple(item) for item in payload["processor_asset_digests"])
    return ModelProfile(**{**payload, "processor_asset_digests": assets})


def _write_profile_json(tmp_path: Path, profile_id: str, **overrides: Any) -> Path:
    payload = _synthetic_profile_payload(profile_id, **overrides)
    path = tmp_path / f"{profile_id}.json"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _runtime_for_profile(profile: ModelProfile) -> local_semantic.CheckedLocalSemanticRuntime:
    """Return the model-free checked runtime for any validated closed profile.

    V2 arms use ``build_fake_profile_runtime(profile)``.
    V1 preserves its existing 768D synthetic embedders bound to the validated
    V1 profile's ``SemanticSpace``.
    """
    validate_model_profile(profile)
    if profile.family == "siglip2":
        return build_fake_profile_runtime(profile)
    space = profile_semantic_space(profile)
    return local_semantic.checked_runtime(
        image_embedder=retrieval_adapter.fake_image_embedder,
        text_embedder=retrieval_adapter.fake_text_embedder,
        semantic_space=space,
        fake=True,
        runtime_identity=f"vip-v1-synthetic:{profile.profile_id}",
    )


class ProfileRecordingEngine:
    """Deterministic in-memory SemanticIndexEngine double for product seam tests.

    Executes the passed runtime embedders on synthetic labels to verify that the
    coordinator propagates the exact generation spec and vector width without
    decoding media files or invoking external tools.
    """

    def __init__(
        self,
        *,
        pts: int = 90090,
        timebase_num: int = 1001,
        timebase_den: int = 30000,
        source_sha256: str = "a" * 64,
    ) -> None:
        self.pts = pts
        self.timebase_num = timebase_num
        self.timebase_den = timebase_den
        self.source_sha256 = source_sha256
        self.build_calls: list[SemanticSpace] = []
        self.index_calls: list[tuple[Path, Path, GenerationSpec, Any, tuple[int, int]]] = []
        self.query_calls: list[tuple[Path, GenerationSpec, tuple[str, ...], Any, int, tuple[int, int]]] = []
        self._committed_by_root: dict[Path, tuple[GenerationSpec, Path]] = {}

    def build_generation_spec(self, space: SemanticSpace) -> GenerationSpec:
        self.build_calls.append(space)
        return build_generation_spec(space)

    def index_source(
        self,
        input_path: Path,
        index_root: Path,
        spec: GenerationSpec,
        image_embedder: Any,
    ) -> IndexSummary:
        root = Path(index_root)
        existing = self._committed_by_root.get(root)
        if existing is not None and existing[0].space != spec.space:
            raise ValueError(
                f"SEMANTIC_SPACE_MISMATCH:space_id:"
                f"expected={spec.space_id!r}:existing={existing[0].space_id!r}"
            )
        vectors = np.asarray(image_embedder([Path(input_path)]))
        if vectors.shape != (1, spec.space.embedding_dim):
            raise ValueError(
                f"VECTOR_SHAPE:{vectors.shape}!=expected:(1,{spec.space.embedding_dim})"
            )
        if vectors.dtype != np.float32:
            raise ValueError(f"VECTOR_DTYPE:{vectors.dtype}")
        self.index_calls.append(
            (Path(input_path), root, spec, image_embedder, vectors.shape)
        )
        self._committed_by_root[root] = (spec, Path(input_path))
        return IndexSummary(
            generation_id=spec.generation_id,
            indexed=1,
            skipped=0,
            failed=0,
            superseded=0,
            failures=(),
        )

    def query(
        self,
        index_root: Path,
        spec: GenerationSpec,
        texts: Sequence[str],
        text_embedder: Any,
        *,
        top_k: int = 5,
    ) -> Mapping[str, Sequence[SearchHit]]:
        root = Path(index_root)
        existing = self._committed_by_root.get(root)
        if existing is not None and existing[0].space != spec.space:
            for field in dataclasses.fields(SemanticSpace):
                expected_val = getattr(spec.space, field.name)
                existing_val = getattr(existing[0].space, field.name)
                if expected_val != existing_val:
                    raise ValueError(
                        f"SEMANTIC_SPACE_MISMATCH:{field.name}:"
                        f"expected={expected_val!r}:existing={existing_val!r}"
                    )
        query_tuple = tuple(texts)
        vectors = np.asarray(text_embedder(query_tuple))
        if vectors.shape != (len(query_tuple), spec.space.embedding_dim):
            raise ValueError(
                f"QUERY_DIMENSION_MISMATCH:{vectors.shape[1]}!={spec.space.embedding_dim}"
            )
        self.query_calls.append(
            (root, spec, query_tuple, text_embedder, top_k, vectors.shape)
        )
        source_locator = str(existing[1]) if existing is not None else "synthetic-source.mp4"
        hit = SearchHit(
            query=query_tuple[0],
            rank=1,
            score=0.875,
            row_id=0,
            source_path=source_locator,
            source_sha256=self.source_sha256,
            pts=self.pts,
            timebase_num=self.timebase_num,
            timebase_den=self.timebase_den,
            timestamp_human="00:00:03.003",
            thumbnail_path=None,
            thumbnail_status="MISSING",
        )
        return {
            text: (dataclasses.replace(hit, query=text),) if top_k >= 1 else ()
            for text in query_tuple
        }


def _seed_persisted_generation(
    index_root: Path,
    runtime: local_semantic.CheckedLocalSemanticRuntime,
    *,
    source_path: Path,
    source_sha256: str = "a" * 64,
    samples: Sequence[tuple[int, int, int, str]] = (
        (90090, 1001, 30000, "00:00:03.003"),
        (180180, 1001, 30000, "00:00:06.006"),
    ),
) -> tuple[GenerationSpec, storage.GenerationPaths]:
    """Seed a real SQLite + vectors.f32 generation in ``tmp_path`` without media decoding."""
    spec = build_generation_spec(runtime.semantic_space)
    paths = storage.open_or_create_generation(index_root, spec)
    persisted_samples = [
        storage.PersistedSample(
            pts=pts,
            timebase_num=tb_num,
            timebase_den=tb_den,
            pts_time=(pts * tb_num) / tb_den,
            timestamp_human=ts_human,
            thumbnail_stage_path=paths.staging / f"stage-{idx}.jpg",
        )
        for idx, (pts, tb_num, tb_den, ts_human) in enumerate(samples)
    ]
    synthetic_frame_labels = [
        index_root / f"synthetic-frame-{idx}.jpg" for idx in range(len(persisted_samples))
    ]
    vectors = runtime.image_embedder(synthetic_frame_labels)
    conn = storage.connect_db(paths)
    try:
        storage.append_source_segment(
            paths,
            conn,
            source_sha256=source_sha256,
            source_metadata={
                "source_revision": "synthetic-rev-001",
                "size_bytes": 4096,
                "stream_index": 0,
                "codec": "h264",
                "width": 1920,
                "height": 1080,
                "timebase_num": samples[0][1],
                "timebase_den": samples[0][2],
                "duration_seconds": 12.0,
            },
            samples=persisted_samples,
            normalized_vectors=vectors,
            expected_dim=spec.space.embedding_dim,
            stream_index=0,
        )
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO source_locations ("
                "path, source_sha256, last_observed_size, last_observed_mtime_ns, last_observed_at"
                ") VALUES (?,?,?,?,?)",
                (str(source_path), source_sha256, 4096, 1, "2026-11-04T00:00:00+00:00"),
            )
    finally:
        conn.close()
    return spec, paths


# ---------------------------------------------------------------------------
# Phase B — Synthetic profile fixture matrix
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("profile_id", "expected_family", "expected_dim", "expected_img", "expected_patch", "expected_bytes"),
    [
        (V1_PROFILE_ID, "siglip", 768, 224, 16, 3072),
        (V2_BASE_PROFILE_ID, "siglip2", 768, 224, 16, 3072),
        (V2_SO400M_PROFILE_ID, "siglip2", 1152, 384, 14, 4608),
    ],
)
def test_three_closed_profiles_validate_geometry_and_row_width_bytes(
    profile_id: str,
    expected_family: str,
    expected_dim: int,
    expected_img: int,
    expected_patch: int,
    expected_bytes: int,
) -> None:
    assert set(CLOSED_PROFILE_IDS) == set(THREE_PROFILE_IDS)
    profile = _synthetic_profile(profile_id)
    validate_model_profile(profile)

    assert profile.family == expected_family
    assert profile.embedding_dim == expected_dim
    assert profile.image_size == expected_img
    assert profile.patch_size == expected_patch
    assert profile_row_width_bytes(profile) == expected_bytes

    space = profile_semantic_space(profile)
    assert space.embedding_dim == expected_dim
    assert space.dtype == "float32"
    assert space.normalization == "l2"


def test_v1_and_v2_base_and_so400m_produce_distinct_deterministic_semantic_spaces() -> None:
    # Even when shared digest/revision fields are identical, V1 768D and V2 Base 768D
    # must never collapse to the same SemanticSpace or semantic_space_id.
    shared_assets = (("tokenizer.json", "a" * 64),)
    shared_overrides = {
        "frozen_revision": "f" * 40,
        "weights_sha256": "b" * 64,
        "processor_asset_digests": [list(item) for item in shared_assets],
        "image_preprocessing_digest": "c" * 64,
        "device_backend": "pytorch-cpu",
    }
    v1_profile = _synthetic_profile(V1_PROFILE_ID, **shared_overrides)
    v2_base_profile = _synthetic_profile(V2_BASE_PROFILE_ID, **shared_overrides)
    v2_so400m_profile = _synthetic_profile(V2_SO400M_PROFILE_ID, **shared_overrides)

    v1_space = profile_semantic_space(v1_profile)
    v2_base_space = profile_semantic_space(v2_base_profile)
    v2_so400m_space = profile_semantic_space(v2_so400m_profile)

    assert v1_space.embedding_dim == v2_base_space.embedding_dim == 768
    assert v2_so400m_space.embedding_dim == 1152

    v1_id = semantic_space_id(v1_space)
    v2_base_id = semantic_space_id(v2_base_space)
    v2_so400m_id = semantic_space_id(v2_so400m_space)
    assert len({v1_id, v2_base_id, v2_so400m_id}) == 3

    # Recreating identical synthetic profiles yields identical space and generation IDs.
    assert semantic_space_id(profile_semantic_space(_synthetic_profile(V1_PROFILE_ID, **shared_overrides))) == v1_id
    assert semantic_space_id(profile_semantic_space(_synthetic_profile(V2_BASE_PROFILE_ID, **shared_overrides))) == v2_base_id
    assert semantic_space_id(profile_semantic_space(_synthetic_profile(V2_SO400M_PROFILE_ID, **shared_overrides))) == v2_so400m_id
    assert (
        build_generation_spec(v2_so400m_space).generation_id
        == build_generation_spec(profile_semantic_space(_synthetic_profile(V2_SO400M_PROFILE_ID, **shared_overrides))).generation_id
    )


@pytest.mark.parametrize(
    ("field", "new_value"),
    [
        ("frozen_revision", "d" * 40),
        ("weights_sha256", "e" * 64),
        ("image_preprocessing_digest", "f" * 64),
        ("device_backend", "pytorch-mps"),
        ("processor_asset_digests", [["tokenizer.json", "9" * 64]]),
        (
            "text_preprocessing_contract",
            f"{V2_SO400M_PROFILE_ID}:text-contract:sha256:{'a' * 64}",
        ),
    ],
)
def test_changing_bound_profile_identity_input_changes_semantic_space_id(
    field: str, new_value: Any
) -> None:
    baseline = _synthetic_profile(V2_SO400M_PROFILE_ID)
    mutated = _synthetic_profile(V2_SO400M_PROFILE_ID, **{field: new_value})
    assert semantic_space_id(profile_semantic_space(baseline)) != semantic_space_id(
        profile_semantic_space(mutated)
    )


# ---------------------------------------------------------------------------
# Phase C — Fake adapter and vector-contract integrity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("profile_id", "expected_dim", "expected_row_bytes"),
    [
        (V2_BASE_PROFILE_ID, 768, 3072),
        (V2_SO400M_PROFILE_ID, 1152, 4608),
    ],
)
def test_build_fake_profile_runtime_preserves_width_dtype_norm_and_determinism(
    tmp_path: Path, profile_id: str, expected_dim: int, expected_row_bytes: int
) -> None:
    profile = _synthetic_profile(profile_id)
    runtime = build_fake_profile_runtime(profile)

    assert runtime.fake is True
    assert runtime.semantic_space == profile_semantic_space(profile)
    assert runtime.semantic_space.embedding_dim == expected_dim

    # Nonexistent image paths prove the fake runtime never opens media/image files.
    image_paths = [
        tmp_path / "unopened-frame-001.jpg",
        tmp_path / "unopened-frame-002.jpg",
        tmp_path / "unopened-frame-003.jpg",
    ]
    image_vecs_1 = runtime.image_embedder(image_paths)
    image_vecs_2 = runtime.image_embedder(image_paths)

    assert image_vecs_1.shape == (3, expected_dim)
    assert image_vecs_1.dtype == np.float32
    assert image_vecs_1.flags["C_CONTIGUOUS"]
    assert image_vecs_1.shape[1] * image_vecs_1.dtype.itemsize == expected_row_bytes
    assert np.isfinite(image_vecs_1).all()
    assert np.allclose(np.linalg.norm(image_vecs_1, axis=1), 1.0, atol=1e-5)
    assert np.array_equal(image_vecs_1, image_vecs_2)
    assert not np.array_equal(image_vecs_1[0], image_vecs_1[1])

    texts = ["grand jete landing", "orchestra tuning"]
    text_vecs_1 = runtime.text_embedder(texts)
    text_vecs_2 = runtime.text_embedder(texts)

    assert text_vecs_1.shape == (2, expected_dim)
    assert text_vecs_1.dtype == np.float32
    assert text_vecs_1.flags["C_CONTIGUOUS"]
    assert text_vecs_1.shape[1] * text_vecs_1.dtype.itemsize == expected_row_bytes
    assert np.isfinite(text_vecs_1).all()
    assert np.allclose(np.linalg.norm(text_vecs_1, axis=1), 1.0, atol=1e-5)
    assert np.array_equal(text_vecs_1, text_vecs_2)
    assert not np.array_equal(text_vecs_1[0], text_vecs_1[1])


def test_v1_profile_is_refused_by_v2_native_adapter_and_uses_preserved_v1_synthetic_seam(
    tmp_path: Path,
) -> None:
    v1_profile = _synthetic_profile(V1_PROFILE_ID)
    with pytest.raises(ValueError, match="SIGLIP2_PROFILE_REQUIRED"):
        build_fake_profile_runtime(v1_profile)

    v1_runtime = _runtime_for_profile(v1_profile)
    assert v1_runtime.fake is True
    assert v1_runtime.semantic_space == profile_semantic_space(v1_profile)
    assert v1_runtime.semantic_space.embedding_dim == 768
    img = v1_runtime.image_embedder([tmp_path / "synthetic-a.jpg", tmp_path / "synthetic-b.jpg"])
    txt = v1_runtime.text_embedder(["coda pirouette"])
    assert img.shape == (2, 768) and img.dtype == np.float32
    assert txt.shape == (1, 768) and txt.dtype == np.float32
    assert np.allclose(np.linalg.norm(img, axis=1), 1.0, atol=1e-5)
    assert np.allclose(np.linalg.norm(txt, axis=1), 1.0, atol=1e-5)


def test_fake_profile_runtimes_produce_distinct_non_interchangeable_vectors() -> None:
    v2_base_rt = build_fake_profile_runtime(_synthetic_profile(V2_BASE_PROFILE_ID))
    v2_so400m_rt = build_fake_profile_runtime(_synthetic_profile(V2_SO400M_PROFILE_ID))
    v1_rt = _runtime_for_profile(_synthetic_profile(V1_PROFILE_ID))

    base_vec = v2_base_rt.text_embedder(["harbor lights"])
    v1_vec = v1_rt.text_embedder(["harbor lights"])
    so400m_vec = v2_so400m_rt.text_embedder(["harbor lights"])

    assert base_vec.shape == (1, 768)
    assert v1_vec.shape == (1, 768)
    assert so400m_vec.shape == (1, 1152)
    assert not np.array_equal(base_vec, v1_vec)


# ---------------------------------------------------------------------------
# Phase D — Product-facing index and query lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("profile_id", "expected_dim"),
    [
        (V1_PROFILE_ID, 768),
        (V2_BASE_PROFILE_ID, 768),
        (V2_SO400M_PROFILE_ID, 1152),
    ],
)
def test_coordinator_index_and_query_propagate_all_three_profile_spaces(
    tmp_path: Path, profile_id: str, expected_dim: int
) -> None:
    profile = _synthetic_profile(profile_id)
    runtime = _runtime_for_profile(profile)
    expected_spec = build_generation_spec(runtime.semantic_space)

    source = tmp_path / f"{profile_id}-source.mp4"
    source.write_bytes(b"opaque synthetic bytes; never decoded")
    index_root = tmp_path / f"index-{profile_id}"
    engine = ProfileRecordingEngine(pts=135135, timebase_num=1001, timebase_den=30000)

    indexed = coordinator.index_local_source(
        source,
        index_root,
        runtime=runtime,
        semantic_space=runtime.semantic_space,
        engine=engine,
    )
    assert indexed == {
        "generation_id": expected_spec.generation_id,
        "space_id": expected_spec.space_id,
        "indexed": 1,
        "skipped": 0,
        "failed": 0,
        "superseded": 0,
    }
    assert len(engine.index_calls) == 1
    assert engine.query_calls == []
    assert engine.index_calls[0][2] == expected_spec
    assert engine.index_calls[0][4] == (1, expected_dim)

    first_query = coordinator.query_local_index(
        index_root,
        ["adagio phrasing", "spotting turn"],
        runtime=runtime,
        semantic_space=runtime.semantic_space,
        engine=engine,
        top_k=3,
    )
    second_query = coordinator.query_local_index(
        index_root,
        ["adagio phrasing", "spotting turn"],
        runtime=runtime,
        semantic_space=runtime.semantic_space,
        engine=engine,
        top_k=3,
    )

    assert len(engine.index_calls) == 1, "query_local_index must never re-index"
    assert len(engine.query_calls) == 2
    assert engine.query_calls[0][1] == expected_spec
    assert engine.query_calls[0][2] == ("adagio phrasing", "spotting turn")
    assert engine.query_calls[0][4] == 3
    assert engine.query_calls[0][5] == (2, expected_dim)
    assert first_query == second_query
    assert first_query["generation_id"] == expected_spec.generation_id
    assert first_query["space_id"] == expected_spec.space_id
    assert first_query["query_count"] == 2
    assert len(first_query["hits"]) == 2


@pytest.mark.parametrize(
    ("profile_id", "expected_dim", "expected_row_bytes"),
    [
        (V1_PROFILE_ID, 768, 3072),
        (V2_BASE_PROFILE_ID, 768, 3072),
        (V2_SO400M_PROFILE_ID, 1152, 4608),
    ],
)
def test_persisted_sqlite_and_memmap_query_path_across_all_three_profiles(
    tmp_path: Path, profile_id: str, expected_dim: int, expected_row_bytes: int
) -> None:
    profile = _synthetic_profile(profile_id)
    runtime = _runtime_for_profile(profile)
    source = tmp_path / f"{profile_id}-synthetic.mp4"
    source.write_bytes(b"synthetic locator bytes")
    index_root = tmp_path / f"persisted-{profile_id}"

    spec, paths = _seed_persisted_generation(
        index_root,
        runtime,
        source_path=source,
        source_sha256="ab" * 32,
        samples=(
            (90090, 1001, 30000, "00:00:03.003"),
            (270270, 1001, 30000, "00:00:09.009"),
        ),
    )
    assert spec.space.embedding_dim == expected_dim
    assert paths.vectors.stat().st_size == 2 * expected_row_bytes

    engine = PersistentLocalSemanticIndexEngine()
    result = coordinator.query_local_index(
        index_root,
        "ballet variation",
        runtime=runtime,
        semantic_space=runtime.semantic_space,
        engine=engine,
        top_k=2,
    )
    assert result["generation_id"] == spec.generation_id
    assert result["space_id"] == spec.space_id
    assert result["query_count"] == 1
    assert len(result["hits"]) == 2
    assert {hit["pts"] for hit in result["hits"]} == {90090, 270270}
    assert all(hit["timebase_num"] == 1001 and hit["timebase_den"] == 30000 for hit in result["hits"])
    assert all(hit["source_sha256"] == "ab" * 32 for hit in result["hits"])


# ---------------------------------------------------------------------------
# Phase E — CLI selection and compatibility
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("profile_id", "expected_dim"),
    [
        (V2_BASE_PROFILE_ID, 768),
        (V2_SO400M_PROFILE_ID, 1152),
    ],
)
def test_cli_index_local_and_query_local_propagate_v2_profiles_including_1152d_so400m(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    profile_id: str,
    expected_dim: int,
) -> None:
    profile = _synthetic_profile(profile_id)
    profile_path = _write_profile_json(tmp_path, profile_id)
    expected_space = profile_semantic_space(profile)
    expected_spec = build_generation_spec(expected_space)

    source = tmp_path / f"{profile_id}-cli-source.mp4"
    source.write_bytes(b"synthetic cli fixture")
    index_root = tmp_path / f"cli-index-{profile_id}"

    # Verify index-local CLI dispatches through coordinator.index_local_source with the
    # selected profile's SemanticSpace and 768D/1152D fake image embedder.
    recording_engine = ProfileRecordingEngine()
    monkeypatch.setattr(
        cli,
        "PersistentLocalSemanticIndexEngine",
        lambda: recording_engine,
        raising=False,
    )

    rc_index = cli.main([
        "index-local",
        "--source",
        str(source),
        "--index-root",
        str(index_root),
        "--fake-embedder",
        "--model-profile-json",
        str(profile_path),
    ])
    assert rc_index == 0
    index_out = json.loads(capsys.readouterr().out)
    assert index_out["runtime_mode"] == "fake"
    assert index_out["generation_id"] == expected_spec.generation_id
    assert index_out["space_id"] == expected_spec.space_id
    assert index_out["indexed"] == 1
    assert len(recording_engine.index_calls) == 1
    assert recording_engine.index_calls[0][4] == (1, expected_dim)

    # Now verify query-local CLI against a real persisted SQLite + vectors.f32 generation
    # using the unpatched PersistentLocalSemanticIndexEngine.
    monkeypatch.undo()
    persisted_root = tmp_path / f"cli-persisted-{profile_id}"
    runtime = build_fake_profile_runtime(profile)
    _seed_persisted_generation(
        persisted_root,
        runtime,
        source_path=source,
        source_sha256="cd" * 32,
        samples=((45045, 1001, 30000, "00:00:01.501"),),
    )

    rc_query = cli.main([
        "query-local",
        "--query",
        "rehearsal entrance",
        "--index-root",
        str(persisted_root),
        "--top-k",
        "1",
        "--fake-embedder",
        "--model-profile-json",
        str(profile_path),
    ])
    assert rc_query == 0
    query_out = json.loads(capsys.readouterr().out)
    assert query_out["runtime_mode"] == "fake"
    assert query_out["generation_id"] == expected_spec.generation_id
    assert query_out["space_id"] == expected_spec.space_id
    assert query_out["query_count"] == 1
    assert len(query_out["hits"]) == 1
    assert query_out["hits"][0]["pts"] == 45045
    assert query_out["hits"][0]["timebase_num"] == 1001
    assert query_out["hits"][0]["timebase_den"] == 30000


def test_cli_default_fake_embedder_without_profile_json_preserves_v1_behavior(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    default_rt = local_semantic.fake_runtime()
    expected_spec = build_generation_spec(default_rt.semantic_space)
    source = tmp_path / "v1-default-source.mp4"
    source.write_bytes(b"synthetic v1 bytes")
    index_root = tmp_path / "v1-default-index"

    _seed_persisted_generation(
        index_root,
        default_rt,
        source_path=source,
        source_sha256="ef" * 32,
        samples=((90000, 1, 90000, "00:00:01.000"),),
    )

    rc = cli.main([
        "query-local",
        "--query",
        "default v1 query",
        "--index-root",
        str(index_root),
        "--fake-embedder",
    ])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["runtime_mode"] == "fake"
    assert payload["generation_id"] == expected_spec.generation_id
    assert payload["space_id"] == expected_spec.space_id
    assert payload["hits"][0]["pts"] == 90000


# ---------------------------------------------------------------------------
# Phase F — Mandatory negative/refusal matrix and side-effect ordering
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("indexed_profile_id", "query_profile_id"),
    [
        (V1_PROFILE_ID, V2_BASE_PROFILE_ID),
        (V2_BASE_PROFILE_ID, V1_PROFILE_ID),
        (V2_BASE_PROFILE_ID, V2_SO400M_PROFILE_ID),
        (V2_SO400M_PROFILE_ID, V2_BASE_PROFILE_ID),
        (V1_PROFILE_ID, V2_SO400M_PROFILE_ID),
        (V2_SO400M_PROFILE_ID, V1_PROFILE_ID),
    ],
)
def test_cross_profile_query_on_persisted_generation_refuses_without_mutation(
    tmp_path: Path, indexed_profile_id: str, query_profile_id: str
) -> None:
    indexed_rt = _runtime_for_profile(_synthetic_profile(indexed_profile_id))
    query_rt = _runtime_for_profile(_synthetic_profile(query_profile_id))

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic")
    index_root = tmp_path / f"index-{indexed_profile_id}-vs-{query_profile_id}"
    _, paths = _seed_persisted_generation(index_root, indexed_rt, source_path=source)

    vector_bytes_before = paths.vectors.read_bytes()
    manifest_bytes_before = paths.manifest.read_bytes()

    query_calls = 0
    orig_text_embedder = query_rt.text_embedder

    def counting_text_embedder(texts: Sequence[str]) -> np.ndarray:
        nonlocal query_calls
        query_calls += 1
        return orig_text_embedder(texts)

    spied_query_rt = local_semantic.checked_runtime(
        image_embedder=query_rt.image_embedder,
        text_embedder=counting_text_embedder,
        semantic_space=query_rt.semantic_space,
        fake=True,
        runtime_identity=query_rt.runtime_identity,
    )

    with pytest.raises(ValueError, match="SEMANTIC_SPACE_MISMATCH:model_identity:"):
        coordinator.query_local_index(
            index_root,
            "cross-space query must fail",
            runtime=spied_query_rt,
            semantic_space=spied_query_rt.semantic_space,
            engine=PersistentLocalSemanticIndexEngine(),
            top_k=1,
        )

    assert query_calls == 0, "cross-space mismatch must fail before embedding or scoring query"
    assert paths.vectors.read_bytes() == vector_bytes_before
    assert paths.manifest.read_bytes() == manifest_bytes_before


@pytest.mark.parametrize(
    ("mutated_field", "mutated_value", "expected_mismatch_field"),
    [
        ("frozen_revision", "d" * 40, "frozen_revision"),
        ("weights_sha256", "e" * 64, "weights_sha256"),
        ("processor_asset_digests", [["tokenizer.json", "e" * 64]], "processor_digest"),
        ("image_preprocessing_digest", "f" * 64, "image_preprocessing_digest"),
        ("device_backend", "pytorch-mps", "model_identity"),
    ],
)
def test_so400m_generation_queried_with_mismatched_revision_or_processor_refuses(
    tmp_path: Path,
    mutated_field: str,
    mutated_value: Any,
    expected_mismatch_field: str,
) -> None:
    base_so400m_rt = build_fake_profile_runtime(_synthetic_profile(V2_SO400M_PROFILE_ID))
    mutated_so400m_rt = build_fake_profile_runtime(
        _synthetic_profile(V2_SO400M_PROFILE_ID, **{mutated_field: mutated_value})
    )

    source = tmp_path / "so400m-source.mp4"
    source.write_bytes(b"synthetic")
    index_root = tmp_path / f"so400m-mismatch-{mutated_field}"
    _seed_persisted_generation(index_root, base_so400m_rt, source_path=source)

    with pytest.raises(ValueError, match=f"SEMANTIC_SPACE_MISMATCH:{expected_mismatch_field}:"):
        coordinator.query_local_index(
            index_root,
            "mismatched so400m identity",
            runtime=mutated_so400m_rt,
            semantic_space=mutated_so400m_rt.semantic_space,
            engine=PersistentLocalSemanticIndexEngine(),
            top_k=1,
        )


def test_so400m_adapter_and_storage_refuse_768d_truncation_and_bad_vectors(
    tmp_path: Path,
) -> None:
    so400m_profile = _synthetic_profile(V2_SO400M_PROFILE_ID)

    # 1. Adapter refuses 768D output when 1152D SO400M profile is bound.
    truncated_impl = SimpleNamespace(
        embed_images=lambda paths: l2_normalize(np.ones((len(list(paths)), 768), dtype=np.float32)),
        embed_texts=lambda texts: l2_normalize(np.ones((len(list(texts)), 768), dtype=np.float32)),
    )
    adapter = create_adapter(so400m_profile, lambda _p: truncated_impl)
    with pytest.raises(ValueError, match=r"SIGLIP2_VECTOR_SHAPE:\(1, 768\)"):
        adapter.embed_texts(["must not truncate 1152d to 768d"])
    with pytest.raises(ValueError, match=r"SIGLIP2_VECTOR_SHAPE:\(1, 768\)"):
        adapter.embed_images([tmp_path / "frame.jpg"])

    # 2. Adapter refuses non-finite and non-float32 outputs.
    nonfinite_impl = SimpleNamespace(
        embed_images=lambda paths: np.full((len(list(paths)), 1152), np.nan, dtype=np.float32),
        embed_texts=lambda texts: np.ones((len(list(texts)), 1152), dtype=np.float64),
    )
    bad_adapter = create_adapter(so400m_profile, lambda _p: nonfinite_impl)
    with pytest.raises(ValueError, match="SIGLIP2_VECTOR_NON_FINITE"):
        bad_adapter.embed_images([tmp_path / "frame.jpg"])
    with pytest.raises(ValueError, match="SIGLIP2_VECTOR_DTYPE:float64"):
        bad_adapter.embed_texts(["wrong dtype"])

    # 3. Storage refuses 3072-byte (768D) row alignment against 4608-byte (1152D) SO400M width.
    with pytest.raises(ValueError, match="COMMITTED_BYTES_NOT_ROW_ALIGNED:3072:4608"):
        storage.require_committed_geometry(
            committed_rows=1,
            committed_bytes=3072,
            row_width_bytes=profile_row_width_bytes(so400m_profile),
        )


def test_cli_and_coordinator_refusal_ordering_prevents_downstream_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    side_effects: list[str] = []
    monkeypatch.setattr(
        cli,
        "_real_runtime",
        lambda _args: side_effects.append("real_runtime") or pytest.fail("_real_runtime must not run"),
    )
    monkeypatch.setattr(
        coordinator,
        "index_local_source",
        lambda *a, **k: side_effects.append("index_local_source") or pytest.fail("index_local_source must not run"),
    )
    monkeypatch.setattr(
        coordinator,
        "query_local_index",
        lambda *a, **k: side_effects.append("query_local_index") or pytest.fail("query_local_index must not run"),
    )

    so400m_path = _write_profile_json(tmp_path, V2_SO400M_PROFILE_ID)
    v1_path = _write_profile_json(tmp_path, V1_PROFILE_ID)
    invalid_dim_path = _write_profile_json(tmp_path, V2_SO400M_PROFILE_ID, embedding_dim=768)
    non_object_path = tmp_path / "list-profile.json"
    non_object_path.write_text("[1, 2, 3]", encoding="utf-8")
    bad_assets_path = tmp_path / "bad-assets.json"
    bad_assets_payload = _synthetic_profile_payload(V2_BASE_PROFILE_ID)
    bad_assets_payload["processor_asset_digests"] = "not-a-list"
    bad_assets_path.write_text(json.dumps(bad_assets_payload), encoding="utf-8")

    refusal_cases: list[tuple[list[str], str]] = [
        # --model-profile-json without --fake-embedder
        (
            [
                "query-local",
                "--query",
                "harbor",
                "--index-root",
                str(tmp_path / "idx"),
                "--model-profile-json",
                str(so400m_path),
            ],
            "MODEL_PROFILE_JSON_REQUIRES_EXPLICIT_FAKE_MODE",
        ),
        # --fake-embedder mixed with real-mode flags
        (
            [
                "query-local",
                "--query",
                "harbor",
                "--index-root",
                str(tmp_path / "idx"),
                "--fake-embedder",
                "--model-profile-json",
                str(so400m_path),
                "--model-root",
                str(tmp_path / "model"),
            ],
            "FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS",
        ),
        # Unreadable profile JSON
        (
            [
                "query-local",
                "--query",
                "harbor",
                "--index-root",
                str(tmp_path / "idx"),
                "--fake-embedder",
                "--model-profile-json",
                str(tmp_path / "missing-profile.json"),
            ],
            "MODEL_PROFILE_JSON_UNREADABLE",
        ),
        # Non-object profile JSON
        (
            [
                "query-local",
                "--query",
                "harbor",
                "--index-root",
                str(tmp_path / "idx"),
                "--fake-embedder",
                "--model-profile-json",
                str(non_object_path),
            ],
            "MODEL_PROFILE_JSON_NOT_OBJECT",
        ),
        # Invalid processor_asset_digests type
        (
            [
                "query-local",
                "--query",
                "harbor",
                "--index-root",
                str(tmp_path / "idx"),
                "--fake-embedder",
                "--model-profile-json",
                str(bad_assets_path),
            ],
            "MODEL_PROFILE_ASSETS_INVALID",
        ),
        # Contradictory SO400M profile dimension (768 instead of 1152)
        (
            [
                "query-local",
                "--query",
                "harbor",
                "--index-root",
                str(tmp_path / "idx"),
                "--fake-embedder",
                "--model-profile-json",
                str(invalid_dim_path),
            ],
            "PROFILE_CONTRACT_MISMATCH:embedding_dim",
        ),
        # V1 profile passed to V2-only --model-profile-json adapter seam
        (
            [
                "query-local",
                "--query",
                "harbor",
                "--index-root",
                str(tmp_path / "idx"),
                "--fake-embedder",
                "--model-profile-json",
                str(v1_path),
            ],
            "SIGLIP2_PROFILE_REQUIRED",
        ),
        # Real-mode request missing required explicit inputs
        (
            [
                "query-local",
                "--query",
                "harbor",
                "--index-root",
                str(tmp_path / "idx"),
            ],
            "REAL_MODE_EXPLICIT_INPUTS_REQUIRED:",
        ),
        # Declared-only reference modality must refuse before runtime/index open
        (
            [
                "query-local",
                "--query-modality",
                "image-reference",
                "--reference-id",
                "asset-ref:clip-01",
                "--provenance-ref",
                "ingest-run:run-01",
                "--source-revision-ref",
                "source-revision:rev-01",
                "--index-root",
                str(tmp_path / "idx"),
                "--fake-embedder",
                "--model-profile-json",
                str(so400m_path),
            ],
            "QUERY_MODALITY_NOT_EXECUTABLE:image_reference",
        ),
    ]

    for argv, expected_error in refusal_cases:
        assert cli.main(argv) == 1
        err_payload = json.loads(capsys.readouterr().out)
        assert err_payload["all_checks_passed"] is False
        assert expected_error in err_payload["error"]

    assert side_effects == []


# ---------------------------------------------------------------------------
# Phase G — Candidate timing and provenance discipline
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("profile_id", THREE_PROFILE_IDS)
def test_candidates_preserve_integer_pts_rational_timebase_and_nonbinding_matched_class(
    tmp_path: Path, profile_id: str
) -> None:
    profile = _synthetic_profile(profile_id)
    runtime = _runtime_for_profile(profile)
    source = tmp_path / f"{profile_id}-ballet.mp4"
    source.write_bytes(b"synthetic ballet fixture")
    digest = hashlib.sha256(profile_id.encode("utf-8")).hexdigest()
    index_root = tmp_path / f"timing-{profile_id}"

    spec, _ = _seed_persisted_generation(
        index_root,
        runtime,
        source_path=source,
        source_sha256=digest,
        samples=((135135, 1001, 30000, "00:00:04.504"),),
    )

    entry = SourceManifestEntry(
        revision_id=f"rev-{profile_id}",
        content_id=f"content-{profile_id}",
        source_path=source,
        source_sha256=digest,
        selected_stream_index=0,
        selection_source="explicit",
        inventory_digest="1" * 64,
        policy_decision_ref="policy-synthetic",
        custody_state="synthetic",
    )
    manifest = MultiSourceManifest(entries=(entry,), manifest_digest="2" * 64)

    multi_result = multi_source_retrieval.retrieve_multi_source(
        index_root,
        manifest,
        "fouette turns",
        runtime=runtime,
        semantic_space=runtime.semantic_space,
        engine=PersistentLocalSemanticIndexEngine(),
        top_k=1,
    )
    assert multi_result.generation_id == spec.generation_id
    assert multi_result.space_id == spec.space_id
    assert len(multi_result.candidates) == 1

    candidate = multi_result.candidates[0]
    assert candidate.evidence_class == "MATCHED"
    assert candidate.evidence_class != "MEASURED"
    assert candidate.binding_eligible is False
    assert type(candidate.source_sample_pts) is int and candidate.source_sample_pts == 135135
    assert type(candidate.source_timebase_num) is int and candidate.source_timebase_num == 1001
    assert type(candidate.source_timebase_den) is int and candidate.source_timebase_den == 30000
    assert candidate.source_sha256 == digest
    assert candidate.source_path == str(source)
    assert candidate.revision_id == f"rev-{profile_id}"
    assert not hasattr(candidate, "source_pts_interval")
    assert not hasattr(candidate, "frame_accurate_boundary")
    assert not hasattr(candidate, "editorial_decision")
