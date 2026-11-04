"""Integration tests for Workstreams W3 (batch_retrieval), W4 (three_arm_batch), and W5 (batch_report)."""
from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import pytest

from persistent_local_index import storage
from persistent_local_index.model_space import GenerationSpec, build_generation_spec
from vip_fvs.batch_report import (
    BATCH_REPORT_SCHEMA_VERSION,
    BENCHMARK_STATUS_NOT_RUN,
    GATE_DECISION_NOT_AUTHORIZED,
    KIND_SINGLE_ARM,
    KIND_THREE_ARM,
    MODEL_EVIDENCE_NOT_OBSERVED,
    REPORT_LIMITATIONS,
    REPORT_STATUS_SYNTHETIC_ONLY,
    build_single_arm_batch_report,
    build_three_arm_batch_report,
    compute_batch_report_digest,
    serialize_batch_report,
    verify_batch_report,
)
from vip_fvs.batch_retrieval import run_batch_retrieval
from vip_fvs.local_semantic import CheckedLocalSemanticRuntime, checked_runtime
from vip_fvs.query_batch import (
    MAX_QUERY_COUNT,
    QUERY_CATALOG_SCHEMA_VERSION,
    QueryCatalog,
    parse_query_catalog_mapping,
)
from vip_fvs.semantic_index import (
    PersistentLocalSemanticIndexEngine,
    SearchHit,
    SemanticSpace,
)
from vip_fvs.source_adapter import (
    MultiSourceManifest,
    SourceManifestEntry,
    save_multi_source_manifest,
)
from vip_fvs.synthetic_profiles import (
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
    build_synthetic_profile_runtime,
    make_synthetic_profile,
    make_synthetic_profile_payload,
)
from vip_fvs.three_arm_batch import (
    ARM_VIP_V1_BASE,
    ARM_VIP_V2_BASE,
    ARM_VIP_V2_SO400M,
    DECLARED_ARM_ORDER,
    THREE_ARM_MAP_SCHEMA_VERSION,
    parse_three_arm_map_mapping,
    run_three_arm_batch,
)


def _entry(
    path: Path,
    *,
    revision: str = "revision-a",
    content: str = "content-a",
    digest: str = "a" * 64,
) -> SourceManifestEntry:
    return SourceManifestEntry(
        revision_id=revision,
        content_id=content,
        source_path=path,
        source_sha256=digest,
        selected_stream_index=0,
        selection_source="explicit",
        inventory_digest="b" * 64,
        policy_decision_ref="policy-synthetic",
        custody_state="synthetic",
    )


def _manifest(*entries: SourceManifestEntry) -> MultiSourceManifest:
    ordered = tuple(
        sorted(
            entries,
            key=lambda e: (e.revision_id.encode("utf-8"), str(e.source_path).encode("utf-8")),
        )
    )
    body = {
        "entries": [
            {
                "revision_id": e.revision_id,
                "content_id": e.content_id,
                "source_path": str(e.source_path),
                "source_sha256": e.source_sha256,
                "selected_stream_index": e.selected_stream_index,
                "selection_source": e.selection_source,
                "inventory_digest": e.inventory_digest,
                "policy_decision_ref": e.policy_decision_ref,
                "custody_state": e.custody_state,
                "inventory_artifact_id": e.inventory_artifact_id,
                "inventory_payload_digest": e.inventory_payload_digest,
            }
            for e in ordered
        ],
        "schema_version": "vip_fvs.multi_source_manifest.v1",
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return MultiSourceManifest(ordered, digest)


def _catalog(queries: Sequence[tuple[str, str]], catalog_id: str = "lab-catalog-01") -> QueryCatalog:
    return parse_query_catalog_mapping({
        "schema_version": QUERY_CATALOG_SCHEMA_VERSION,
        "catalog_id": catalog_id,
        "queries": [{"query_id": qid, "text": text} for qid, text in queries],
    })


def _hit(
    path: Path,
    digest: str = "a" * 64,
    *,
    rank: int = 1,
    score: float = 0.875,
    pts: int = 90090,
    tb_num: int = 1001,
    tb_den: int = 30000,
) -> SearchHit:
    return SearchHit(
        query="placeholder",
        rank=rank,
        score=score,
        row_id=rank - 1,
        source_path=str(path),
        source_sha256=digest,
        pts=pts,
        timebase_num=tb_num,
        timebase_den=tb_den,
        timestamp_human="00:00:03.003",
        thumbnail_path=None,
        thumbnail_status="MISSING",
    )


class InMemoryBatchEngine:
    """Read-only SemanticIndexEngine test double recording exact query batches."""

    def __init__(
        self,
        space: SemanticSpace,
        hits: Sequence[SearchHit] | None = None,
        *,
        omit_query_key: bool = False,
    ) -> None:
        self.spec = build_generation_spec(space)
        self.hits = tuple(hits or ())
        self.omit_query_key = omit_query_key
        self.index_calls: list[Any] = []
        self.query_calls: list[tuple[Path, GenerationSpec, tuple[str, ...], int]] = []

    def build_generation_spec(self, space: SemanticSpace) -> GenerationSpec:
        assert space == self.spec.space
        return self.spec

    def index_source(self, *args: Any, **kwargs: Any) -> Any:
        self.index_calls.append((args, kwargs))
        raise AssertionError("batch retrieval is read-only and must never call index_source")

    def query(
        self,
        index_root: Path,
        spec: GenerationSpec,
        texts: Sequence[str],
        text_embedder: Any,
        *,
        top_k: int,
    ) -> Mapping[str, Sequence[SearchHit]]:
        text_tuple = tuple(texts)
        vecs = text_embedder(text_tuple)
        assert vecs.shape == (len(text_tuple), self.spec.space.embedding_dim)
        self.query_calls.append((Path(index_root), spec, text_tuple, top_k))
        if self.omit_query_key:
            return {}
        return {
            text: tuple(dataclasses.replace(h, query=text) for h in self.hits[:top_k])
            for text in text_tuple
        }


def _seed_persisted_index(
    index_root: Path,
    runtime: CheckedLocalSemanticRuntime,
    *,
    source_path: Path,
    source_sha256: str,
    pts: int = 135135,
    tb_num: int = 1001,
    tb_den: int = 30000,
) -> tuple[GenerationSpec, storage.GenerationPaths]:
    spec = build_generation_spec(runtime.semantic_space)
    paths = storage.open_or_create_generation(index_root, spec)
    samples = [
        storage.PersistedSample(
            pts=pts,
            timebase_num=tb_num,
            timebase_den=tb_den,
            pts_time=(pts * tb_num) / tb_den,
            timestamp_human="00:00:04.504",
            thumbnail_stage_path=paths.staging / "stage-0.jpg",
        )
    ]
    vectors = runtime.image_embedder([index_root / "synthetic-frame-0.jpg"])
    conn = storage.connect_db(paths)
    try:
        storage.append_source_segment(
            paths,
            conn,
            source_sha256=source_sha256,
            source_metadata={
                "source_revision": "rev-synthetic",
                "size_bytes": 2048,
                "stream_index": 0,
                "codec": "h264",
                "width": 1920,
                "height": 1080,
                "timebase_num": tb_num,
                "timebase_den": tb_den,
                "duration_seconds": 10.0,
            },
            samples=samples,
            normalized_vectors=vectors,
            expected_dim=spec.space.embedding_dim,
            stream_index=0,
        )
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO source_locations ("
                "path, source_sha256, last_observed_size, last_observed_mtime_ns, last_observed_at"
                ") VALUES (?,?,?,?,?)",
                (str(source_path), source_sha256, 2048, 1, "2026-11-04T00:00:00+00:00"),
            )
    finally:
        conn.close()
    return spec, paths


# ---------------------------------------------------------------------------
# Workstream W3 — Read-only single-arm batch retrieval
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("query_count", [1, 2, MAX_QUERY_COUNT])
def test_single_arm_batch_retrieval_handles_1_2_and_64_queries_without_indexing(
    query_count: int,
) -> None:
    bundle = build_synthetic_profile_runtime(make_synthetic_profile(V2_SO400M_PROFILE_ID))
    locator = Path("/synthetic/archive/clip-01.mp4")
    manifest = _manifest(_entry(locator))
    catalog = _catalog([
        (f"q-{idx:03d}", f"synthetic performance query {idx}")
        for idx in range(1, query_count + 1)
    ])
    engine = InMemoryBatchEngine(
        bundle.semantic_space,
        hits=(_hit(locator, pts=90090, tb_num=1001, tb_den=30000),),
    )

    result = run_batch_retrieval(
        catalog,
        manifest,
        Path("synthetic-index"),
        runtime=bundle.runtime,
        semantic_space=bundle.semantic_space,
        engine=engine,
        top_k=5,
        profile_id=V2_SO400M_PROFILE_ID,
    )

    assert engine.index_calls == []
    assert len(engine.query_calls) == 1
    assert len(engine.query_calls[0][2]) == query_count
    assert result.profile_id == V2_SO400M_PROFILE_ID
    assert result.embedding_dim == 1152
    assert result.row_width_bytes == 4608
    assert len(result.query_results) == query_count
    assert result.total_candidate_count == query_count

    report = build_single_arm_batch_report(result)
    assert report["kind"] == KIND_SINGLE_ARM
    assert report["status"] == REPORT_STATUS_SYNTHETIC_ONLY
    assert report["benchmark_status"] == BENCHMARK_STATUS_NOT_RUN
    assert report["model_evidence"] == MODEL_EVIDENCE_NOT_OBSERVED
    assert report["gate_decision"] == GATE_DECISION_NOT_AUTHORIZED
    assert len(report["arms"]) == 1
    assert report["arms"][0]["query_count"] == query_count


def test_duplicate_text_queries_execute_once_and_reassociate_with_all_query_ids() -> None:
    bundle = build_synthetic_profile_runtime(make_synthetic_profile(V2_BASE_PROFILE_ID))
    locator = Path("/synthetic/archive/duet.mp4")
    manifest = _manifest(_entry(locator))
    catalog = _catalog([
        ("q-first", "shared query text"),
        ("q-middle", "unique middle query"),
        ("q-repeat", "shared query text"),
    ])
    engine = InMemoryBatchEngine(
        bundle.semantic_space,
        hits=(_hit(locator, rank=1, score=0.91), _hit(locator, rank=2, score=0.73)),
    )

    result = run_batch_retrieval(
        catalog,
        manifest,
        Path("synthetic-index"),
        runtime=bundle.runtime,
        semantic_space=bundle.semantic_space,
        engine=engine,
        top_k=2,
    )

    assert len(engine.query_calls) == 1
    assert engine.query_calls[0][2] == ("shared query text", "unique middle query")
    assert result.query_ids == ("q-first", "q-middle", "q-repeat")
    assert [qr.query_id for qr in result.query_results] == ["q-first", "q-middle", "q-repeat"]
    assert [c.query_id for c in result.query_results[0].candidates] == ["q-first", "q-first"]
    assert [c.query_id for c in result.query_results[2].candidates] == ["q-repeat", "q-repeat"]
    assert [c.score for c in result.query_results[0].candidates] == [0.91, 0.73]
    assert [c.score for c in result.query_results[2].candidates] == [0.91, 0.73]


def test_duplicate_content_digest_at_two_locators_preserves_distinct_occurrences() -> None:
    bundle = build_synthetic_profile_runtime(make_synthetic_profile(V1_PROFILE_ID))
    path_a = Path("/synthetic/occurrence-a.mp4")
    path_b = Path("/synthetic/occurrence-b.mp4")
    shared_sha = "d" * 64
    manifest = _manifest(
        _entry(path_a, revision="rev-occ-a", content="shared-content", digest=shared_sha),
        _entry(path_b, revision="rev-occ-b", content="shared-content", digest=shared_sha),
    )
    catalog = _catalog([("q-001", "coda finale")])
    engine = InMemoryBatchEngine(
        bundle.semantic_space,
        hits=(
            _hit(path_b, shared_sha, rank=1, score=0.95),
            _hit(path_a, shared_sha, rank=2, score=0.82),
        ),
    )

    result = run_batch_retrieval(
        catalog,
        manifest,
        Path("synthetic-index"),
        runtime=bundle.runtime,
        semantic_space=bundle.semantic_space,
        engine=engine,
        top_k=5,
    )

    cands = result.query_results[0].candidates
    assert [(c.revision_id, c.source_path, c.rank) for c in cands] == [
        ("rev-occ-b", str(path_b), 1),
        ("rev-occ-a", str(path_a), 2),
    ]
    assert cands[0].content_id == cands[1].content_id == "shared-content"
    assert all(c.evidence_class == "MATCHED" and c.binding_eligible is False for c in cands)


@pytest.mark.parametrize(
    ("bad_hit", "omit_key", "expected_match"),
    [
        (_hit(Path("/unlisted/path.mp4")), False, "MULTI_SOURCE_HIT_MANIFEST_BINDING_FAILED"),
        (_hit(Path("/synthetic/a.mp4"), digest="9" * 64), False, "MULTI_SOURCE_HIT_MANIFEST_BINDING_FAILED"),
        (_hit(Path("/synthetic/a.mp4"), score=float("nan")), False, "MULTI_SOURCE_HIT_SCORE_INVALID"),
        (_hit(Path("/synthetic/a.mp4"), score=float("inf")), False, "MULTI_SOURCE_HIT_SCORE_INVALID"),
        (_hit(Path("/synthetic/a.mp4"), pts=True), False, "MULTI_SOURCE_HIT_LOCATOR_INVALID"),
        (_hit(Path("/synthetic/a.mp4"), tb_den=0), False, "MULTI_SOURCE_HIT_LOCATOR_INVALID"),
        (_hit(Path("/synthetic/a.mp4")), True, "ENGINE_QUERY_RESULT_MISSING"),
    ],
)
def test_batch_retrieval_fails_whole_batch_on_manifest_or_hit_integrity_violation(
    bad_hit: SearchHit, omit_key: bool, expected_match: str
) -> None:
    bundle = build_synthetic_profile_runtime(make_synthetic_profile(V2_BASE_PROFILE_ID))
    locator = Path("/synthetic/a.mp4")
    manifest = _manifest(_entry(locator))
    catalog = _catalog([("q-001", "valid query")])
    engine = InMemoryBatchEngine(
        bundle.semantic_space,
        hits=(bad_hit,),
        omit_query_key=omit_key,
    )

    with pytest.raises(ValueError, match=expected_match):
        run_batch_retrieval(
            catalog,
            manifest,
            Path("synthetic-index"),
            runtime=bundle.runtime,
            semantic_space=bundle.semantic_space,
            engine=engine,
            top_k=3,
        )


def test_batch_retrieval_refuses_non_fake_runtime_and_space_mismatch_before_query() -> None:
    bundle = build_synthetic_profile_runtime(make_synthetic_profile(V2_BASE_PROFILE_ID))
    other_bundle = build_synthetic_profile_runtime(make_synthetic_profile(V2_SO400M_PROFILE_ID))
    locator = Path("/synthetic/a.mp4")
    manifest = _manifest(_entry(locator))
    catalog = _catalog([("q-001", "query")])
    engine = InMemoryBatchEngine(bundle.semantic_space)

    non_fake_rt = checked_runtime(
        image_embedder=bundle.runtime.image_embedder,
        text_embedder=bundle.runtime.text_embedder,
        semantic_space=bundle.semantic_space,
        fake=False,
    )
    with pytest.raises(ValueError, match="SYNTHETIC_BATCH_REQUIRES_FAKE_RUNTIME"):
        run_batch_retrieval(
            catalog,
            manifest,
            Path("synthetic-index"),
            runtime=non_fake_rt,
            semantic_space=bundle.semantic_space,
            engine=engine,
        )

    with pytest.raises(ValueError, match="SEMANTIC_SPACE_RUNTIME_MISMATCH"):
        run_batch_retrieval(
            catalog,
            manifest,
            Path("synthetic-index"),
            runtime=bundle.runtime,
            semantic_space=other_bundle.semantic_space,
            engine=engine,
        )
    assert engine.query_calls == []


# ---------------------------------------------------------------------------
# Workstream W4 & W5 — Three-arm comparison and deterministic report verifier
# ---------------------------------------------------------------------------


def _setup_three_arm_fixture(tmp_path: Path) -> tuple[QueryCatalog, dict[str, Any], dict[str, storage.GenerationPaths]]:
    catalog = _catalog([
        ("q-001", "adagio supported pirouette"),
        ("q-002", "corps de ballet diagonal waltz"),
    ])
    arms_config = []
    paths_by_arm: dict[str, storage.GenerationPaths] = {}

    arm_specs = (
        (ARM_VIP_V1_BASE, V1_PROFILE_ID, "11" * 32, 90090),
        (ARM_VIP_V2_BASE, V2_BASE_PROFILE_ID, "22" * 32, 135135),
        (ARM_VIP_V2_SO400M, V2_SO400M_PROFILE_ID, "33" * 32, 180180),
    )
    for arm_id, profile_id, sha, pts in arm_specs:
        profile_path = tmp_path / f"{arm_id.lower()}-profile.json"
        profile_path.write_text(
            json.dumps(make_synthetic_profile_payload(profile_id), sort_keys=True),
            encoding="utf-8",
        )
        bundle = build_synthetic_profile_runtime(make_synthetic_profile(profile_id))
        source_locator = tmp_path / f"{arm_id.lower()}-opaque-locator.mp4"
        index_root = tmp_path / f"{arm_id.lower()}-index"
        _, gen_paths = _seed_persisted_index(
            index_root,
            bundle.runtime,
            source_path=source_locator,
            source_sha256=sha,
            pts=pts,
        )
        paths_by_arm[arm_id] = gen_paths

        manifest_path = tmp_path / f"{arm_id.lower()}-manifest.json"
        manifest = _manifest(
            _entry(
                source_locator,
                revision=f"rev-{arm_id.lower()}",
                content=f"content-{arm_id.lower()}",
                digest=sha,
            )
        )
        save_multi_source_manifest(manifest, manifest_path)
        arms_config.append({
            "arm_id": arm_id,
            "model_profile_json": str(profile_path),
            "index_root": str(index_root),
            "manifest": str(manifest_path),
        })

    # Deliberately reverse input arm order to verify output canonicalization to DECLARED_ARM_ORDER.
    arm_map_payload = {
        "schema_version": THREE_ARM_MAP_SCHEMA_VERSION,
        "arms": list(reversed(arms_config)),
    }
    return catalog, arm_map_payload, paths_by_arm


def test_three_arm_batch_and_report_preserve_isolation_order_and_byte_determinism(
    tmp_path: Path,
) -> None:
    catalog, arm_map_payload, paths_by_arm = _setup_three_arm_fixture(tmp_path)
    arm_map = parse_three_arm_map_mapping(arm_map_payload)
    assert tuple(entry.arm_id for entry in arm_map.arms) == DECLARED_ARM_ORDER

    before_bytes = {
        arm_id: (gp.manifest.read_bytes(), gp.vectors.read_bytes())
        for arm_id, gp in paths_by_arm.items()
    }

    result_1 = run_three_arm_batch(catalog, arm_map, top_k=3)
    result_2 = run_three_arm_batch(catalog, arm_map, top_k=3)
    assert result_1 == result_2

    report_1 = build_three_arm_batch_report(result_1)
    report_2 = build_three_arm_batch_report(result_2)
    serialized_1 = serialize_batch_report(report_1)
    serialized_2 = serialize_batch_report(report_2)
    assert serialized_1 == serialized_2
    assert verify_batch_report(serialized_1) == report_1

    assert report_1["schema_version"] == BATCH_REPORT_SCHEMA_VERSION
    assert report_1["kind"] == KIND_THREE_ARM
    assert report_1["status"] == REPORT_STATUS_SYNTHETIC_ONLY
    assert report_1["benchmark_status"] == BENCHMARK_STATUS_NOT_RUN
    assert report_1["model_evidence"] == MODEL_EVIDENCE_NOT_OBSERVED
    assert report_1["gate_decision"] == GATE_DECISION_NOT_AUTHORIZED
    assert report_1["cross_arm_winner"] is None
    assert tuple(report_1["limitations"]) == REPORT_LIMITATIONS
    assert [a["arm_id"] for a in report_1["arms"]] == list(DECLARED_ARM_ORDER)
    assert [a["embedding_dim"] for a in report_1["arms"]] == [768, 768, 1152]
    assert [a["row_width_bytes"] for a in report_1["arms"]] == [3072, 3072, 4608]
    assert len({a["space_id"] for a in report_1["arms"]}) == 3
    assert len({a["generation_id"] for a in report_1["arms"]}) == 3

    after_bytes = {
        arm_id: (gp.manifest.read_bytes(), gp.vectors.read_bytes())
        for arm_id, gp in paths_by_arm.items()
    }
    assert after_bytes == before_bytes


def test_three_arm_batch_refuses_swapped_profile_swapped_index_and_partial_failure(
    tmp_path: Path,
) -> None:
    catalog, arm_map_payload, _ = _setup_three_arm_fixture(tmp_path)
    by_id = {row["arm_id"]: dict(row) for row in arm_map_payload["arms"]}

    # 1. Swapped profile JSON under VIP_V1_BASE (pointing to V2 Base profile).
    swapped_profile_payload = {
        "schema_version": THREE_ARM_MAP_SCHEMA_VERSION,
        "arms": [
            {**by_id[ARM_VIP_V1_BASE], "model_profile_json": by_id[ARM_VIP_V2_BASE]["model_profile_json"]},
            by_id[ARM_VIP_V2_BASE],
            by_id[ARM_VIP_V2_SO400M],
        ],
    }
    with pytest.raises(ValueError, match="THREE_ARM_PROFILE_ID_MISMATCH:VIP_V1_BASE"):
        run_three_arm_batch(catalog, parse_three_arm_map_mapping(swapped_profile_payload))

    # 2. Swapped index roots between VIP_V1_BASE (768D) and VIP_V2_BASE (768D).
    swapped_index_payload = {
        "schema_version": THREE_ARM_MAP_SCHEMA_VERSION,
        "arms": [
            {**by_id[ARM_VIP_V1_BASE], "index_root": by_id[ARM_VIP_V2_BASE]["index_root"]},
            {**by_id[ARM_VIP_V2_BASE], "index_root": by_id[ARM_VIP_V1_BASE]["index_root"]},
            by_id[ARM_VIP_V2_SO400M],
        ],
    }
    with pytest.raises(ValueError, match="SEMANTIC_SPACE_MISMATCH:model_identity:"):
        run_three_arm_batch(catalog, parse_three_arm_map_mapping(swapped_index_payload))

    # 3. Shared index_root across two arms is rejected during arm-map validation.
    shared_root_payload = {
        "schema_version": THREE_ARM_MAP_SCHEMA_VERSION,
        "arms": [
            by_id[ARM_VIP_V1_BASE],
            {**by_id[ARM_VIP_V2_BASE], "index_root": by_id[ARM_VIP_V1_BASE]["index_root"]},
            by_id[ARM_VIP_V2_SO400M],
        ],
    }
    with pytest.raises(ValueError, match="THREE_ARM_SHARED_INDEX_ROOT_FORBIDDEN"):
        parse_three_arm_map_mapping(shared_root_payload)

    # 4. Missing or duplicate arm in arm map.
    with pytest.raises(ValueError, match="THREE_ARM_MAP_INCOMPLETE_ARMS"):
        parse_three_arm_map_mapping({
            "schema_version": THREE_ARM_MAP_SCHEMA_VERSION,
            "arms": [by_id[ARM_VIP_V1_BASE], by_id[ARM_VIP_V2_BASE]],
        })
    with pytest.raises(ValueError, match="THREE_ARM_MAP_DUPLICATE_ARM_ID"):
        parse_three_arm_map_mapping({
            "schema_version": THREE_ARM_MAP_SCHEMA_VERSION,
            "arms": [by_id[ARM_VIP_V1_BASE], by_id[ARM_VIP_V1_BASE], by_id[ARM_VIP_V2_SO400M]],
        })


@pytest.mark.parametrize(
    ("tamper_fn", "expected_match"),
    [
        (
            lambda r: r["arms"][0]["queries"][0]["candidates"][0].update(score=0.12345),
            "BATCH_REPORT_DIGEST_MISMATCH",
        ),
        (
            lambda r: r["arms"][0]["queries"][0]["candidates"][0].update(evidence_class="MEASURED"),
            "BATCH_REPORT_CANDIDATE_EVIDENCE_CLASS_INVALID",
        ),
        (
            lambda r: r["arms"][0]["queries"][0]["candidates"][0].update(binding_eligible=True),
            "BATCH_REPORT_CANDIDATE_BINDING_ELIGIBLE_FORBIDDEN",
        ),
        (
            lambda r: r["arms"][0]["queries"][0]["candidates"][0].update(
                frame_accurate_boundary=[10, 20]
            ),
            "BATCH_REPORT_CANDIDATE_EDIT_BOUNDARY_FORBIDDEN",
        ),
        (
            lambda r: r.update(cross_arm_winner="VIP_V2_SO400M"),
            "BATCH_REPORT_WINNER_FORBIDDEN",
        ),
        (
            lambda r: r.update(status="PASS"),
            "BATCH_REPORT_STATUS_INVALID",
        ),
        (
            lambda r: r.update(benchmark_status="PASS"),
            "BATCH_REPORT_BENCHMARK_STATUS_INVALID",
        ),
        (
            lambda r: r.update(gate_decision="PROMOTED"),
            "BATCH_REPORT_GATE_DECISION_INVALID",
        ),
    ],
)
def test_verify_batch_report_refuses_tampering_and_forbidden_claim_promotions(
    tmp_path: Path, tamper_fn: Any, expected_match: str
) -> None:
    catalog, arm_map_payload, _ = _setup_three_arm_fixture(tmp_path)
    result = run_three_arm_batch(catalog, parse_three_arm_map_mapping(arm_map_payload))
    report = build_three_arm_batch_report(result)

    tampered = copy.deepcopy(report)
    tamper_fn(tampered)
    if expected_match != "BATCH_REPORT_DIGEST_MISMATCH":
        tampered["report_digest"] = compute_batch_report_digest(tampered)

    with pytest.raises(ValueError, match=expected_match):
        verify_batch_report(tampered)
