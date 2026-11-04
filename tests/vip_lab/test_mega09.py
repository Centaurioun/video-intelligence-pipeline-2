"""MEGA-09 Regression Tests: Batch Retrieval to Nonbinding Review Queue (Packet P09).

Covers:
1. Single-arm and three-arm batch report intake into a deterministic nonbinding
   ``CandidateReviewQueue``.
2. Preservation of distinct ``source_path`` occurrences even when ``source_sha256``
   bytes are identical.
3. Preservation of duplicate query texts under distinct ``query_id``s.
4. Strict enforcement of ``evidence_class="MATCHED"``, ``binding_eligible=False``,
   ``review_state="NOT_REVIEWED"``, ``human_decision_state="NOT_OBSERVED"``, and
   ``cross_arm_winner=None`` (no cross-arm score normalization or reranking).
5. Fail-closed refusal of tampered upstream batch report digests, unknown profiles,
   semantic space collisions, ``binding_eligible=True``, cut-boundary fields
   (``start_pts``, ``end_pts``, ``cut_in``, ``cut_out``), and missing provenance.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import pytest

from persistent_local_index.model_space import GenerationSpec, build_generation_spec
from vip_fvs.batch_report import (
    build_single_arm_batch_report,
    build_three_arm_batch_report,
)
from vip_fvs.batch_retrieval import SingleArmBatchResult, run_batch_retrieval
from vip_fvs.query_batch import (
    QUERY_CATALOG_SCHEMA_VERSION,
    QueryCatalog,
    parse_query_catalog_mapping,
)
from vip_fvs.semantic_index import SearchHit, SemanticSpace
from vip_fvs.source_adapter import MultiSourceManifest, SourceManifestEntry
from vip_fvs.synthetic_profiles import (
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
    build_synthetic_profile_runtime,
    make_synthetic_profile,
)
from vip_fvs.three_arm_batch import (
    ARM_VIP_V1_BASE,
    ARM_VIP_V2_BASE,
    ARM_VIP_V2_SO400M,
    DECLARED_ARM_ORDER,
    ThreeArmBatchArmResult,
    ThreeArmBatchResult,
)
from vip_lab.common import NOT_OBSERVED, ReadinessStatus, VipLabError
from vip_lab.mega09 import (
    CANDIDATE_QUEUE_SCHEMA_VERSION,
    CandidateQueueItem,
    CandidateReviewQueue,
    build_queue_from_batch_report,
    build_queue_from_single_arm,
    build_queue_from_three_arm,
    inspect_review_queue_intake,
    verify_candidate_queue,
)


def _make_manifest_entry(
    path_str: str,
    *,
    revision_id: str,
    content_id: str,
    sha256: str = "a" * 64,
) -> SourceManifestEntry:
    return SourceManifestEntry(
        revision_id=revision_id,
        content_id=content_id,
        source_path=Path(path_str),
        source_sha256=sha256,
        selected_stream_index=0,
        selection_source="explicit",
        inventory_digest="b" * 64,
        policy_decision_ref="policy-synthetic-09",
        custody_state="synthetic",
    )


def _make_manifest(*entries: SourceManifestEntry) -> MultiSourceManifest:
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
    return MultiSourceManifest(ordered, hashlib.sha256(raw).hexdigest())


def _make_catalog(queries: Sequence[tuple[str, str]]) -> QueryCatalog:
    return parse_query_catalog_mapping(
        {
            "schema_version": QUERY_CATALOG_SCHEMA_VERSION,
            "catalog_id": "cat-mega09-01",
            "queries": [{"query_id": qid, "text": text} for qid, text in queries],
        }
    )


class _FakeReadOnlyEngine:
    def __init__(self, space: SemanticSpace, hits: Sequence[SearchHit]) -> None:
        self.spec = build_generation_spec(space)
        self.hits = tuple(hits)

    def build_generation_spec(self, space: SemanticSpace) -> GenerationSpec:
        return self.spec

    def index_source(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("index_source must never be called")

    def query(
        self,
        index_root: Path,
        spec: GenerationSpec,
        texts: Sequence[str],
        text_embedder: Any,
        *,
        top_k: int,
    ) -> Mapping[str, Sequence[SearchHit]]:
        _ = text_embedder(tuple(texts))
        return {
            text: tuple(dataclasses.replace(h, query=text) for h in self.hits[:top_k])
            for text in texts
        }


def _build_single_arm_fixture() -> SingleArmBatchResult:
    bundle = build_synthetic_profile_runtime(make_synthetic_profile(V1_PROFILE_ID))
    shared_sha = "c" * 64
    e1 = _make_manifest_entry(
        "/synthetic/archive/cam_a.mp4",
        revision_id="rev-cam-a",
        content_id="content-shared",
        sha256=shared_sha,
    )
    e2 = _make_manifest_entry(
        "/synthetic/archive/cam_b_copy.mp4",
        revision_id="rev-cam-b",
        content_id="content-shared",
        sha256=shared_sha,
    )
    manifest = _make_manifest(e1, e2)
    catalog = _make_catalog(
        [
            ("q-01", "ballet grand jete"),
            ("q-02", "ballet grand jete"),  # duplicate text under distinct query_id
        ]
    )
    hits = (
        SearchHit(
            query="placeholder",
            rank=1,
            score=0.92,
            row_id=0,
            source_path="/synthetic/archive/cam_a.mp4",
            source_sha256=shared_sha,
            pts=90090,
            timebase_num=1001,
            timebase_den=30000,
            timestamp_human="00:00:03.003",
            thumbnail_path=None,
            thumbnail_status="MISSING",
        ),
        SearchHit(
            query="placeholder",
            rank=2,
            score=0.85,
            row_id=1,
            source_path="/synthetic/archive/cam_b_copy.mp4",
            source_sha256=shared_sha,
            pts=180180,
            timebase_num=1001,
            timebase_den=30000,
            timestamp_human="00:00:06.006",
            thumbnail_path=None,
            thumbnail_status="MISSING",
        ),
    )
    engine = _FakeReadOnlyEngine(bundle.semantic_space, hits)
    return run_batch_retrieval(
        catalog,
        manifest,
        Path("synth-idx-v1"),
        runtime=bundle.runtime,
        semantic_space=bundle.semantic_space,
        engine=engine,
        top_k=5,
        profile_id=V1_PROFILE_ID,
    )


def _build_three_arm_fixture() -> ThreeArmBatchResult:
    catalog = _make_catalog([("q-01", "orchestra downbeat"), ("q-02", "pirouette Coda")])
    shared_sha = "d" * 64
    e1 = _make_manifest_entry(
        "/synthetic/archive/act1.mp4",
        revision_id="rev-act1",
        content_id="cnt-act1",
        sha256=shared_sha,
    )
    manifest = _make_manifest(e1)
    hits = (
        SearchHit(
            query="placeholder",
            rank=1,
            score=0.88,
            row_id=0,
            source_path="/synthetic/archive/act1.mp4",
            source_sha256=shared_sha,
            pts=45045,
            timebase_num=1001,
            timebase_den=30000,
            timestamp_human="00:00:01.501",
            thumbnail_path=None,
            thumbnail_status="MISSING",
        ),
    )
    arms_out: list[ThreeArmBatchArmResult] = []
    for arm_id, prof_id in (
        (ARM_VIP_V1_BASE, V1_PROFILE_ID),
        (ARM_VIP_V2_BASE, V2_BASE_PROFILE_ID),
        (ARM_VIP_V2_SO400M, V2_SO400M_PROFILE_ID),
    ):
        bundle = build_synthetic_profile_runtime(make_synthetic_profile(prof_id))
        engine = _FakeReadOnlyEngine(bundle.semantic_space, hits)
        single = run_batch_retrieval(
            catalog,
            manifest,
            Path(f"synth-idx-{arm_id}"),
            runtime=bundle.runtime,
            semantic_space=bundle.semantic_space,
            engine=engine,
            top_k=5,
            profile_id=prof_id,
        )
        arms_out.append(
            ThreeArmBatchArmResult(
                arm_id=arm_id,
                profile_id=prof_id,
                model_identity=bundle.semantic_space.model_identity,
                space_id=single.space_id,
                generation_id=single.generation_id,
                embedding_dim=bundle.profile.embedding_dim,
                row_width_bytes=bundle.row_width_bytes,
                manifest_digest=manifest.manifest_digest,
                catalog_digest=catalog.catalog_digest,
                query_count=len(catalog.query_ids),
                candidate_count=single.total_candidate_count,
                batch_result=single,
            )
        )
    return ThreeArmBatchResult(
        catalog_id=catalog.catalog_id,
        catalog_digest=catalog.catalog_digest,
        query_ids=catalog.query_ids,
        top_k=5,
        arm_map_digest="e" * 64,
        arms=tuple(arms_out),
    )


def test_single_arm_queue_preserves_distinct_source_paths_and_duplicate_query_texts() -> None:
    single = _build_single_arm_fixture()
    queue = build_queue_from_single_arm(single)

    assert isinstance(queue, CandidateReviewQueue)
    assert queue.schema_version == CANDIDATE_QUEUE_SCHEMA_VERSION
    assert queue.synthetic_only is True
    assert queue.authentic_model_evidence is False
    assert queue.cross_arm_winner is None
    assert len(queue.items) == 4  # 2 queries * 2 distinct source_path occurrences

    # Byte-identical files at cam_a.mp4 and cam_b_copy.mp4 are BOTH retained per query_id
    q01_items = [item for item in queue.items if item.query_id == "q-01"]
    q02_items = [item for item in queue.items if item.query_id == "q-02"]
    assert len(q01_items) == 2
    assert len(q02_items) == 2
    assert [i.source_path for i in q01_items] == [
        "/synthetic/archive/cam_a.mp4",
        "/synthetic/archive/cam_b_copy.mp4",
    ]
    assert q01_items[0].source_sha256 == q01_items[1].source_sha256
    assert q01_items[0].revision_id != q01_items[1].revision_id

    for item in queue.items:
        assert isinstance(item, CandidateQueueItem)
        assert item.evidence_class == "MATCHED"
        assert item.binding_eligible is False
        assert item.review_state == "NOT_REVIEWED"
        assert item.human_decision_state == NOT_OBSERVED
        assert item.arm_id == ARM_VIP_V1_BASE
        assert item.profile_id == V1_PROFILE_ID

    verified_dict = verify_candidate_queue(queue.to_dict())
    assert verified_dict["queue_digest"] == queue.queue_digest


def test_three_arm_queue_preserves_arm_isolation_without_cross_arm_reranking() -> None:
    three_arm = _build_three_arm_fixture()
    report = build_three_arm_batch_report(three_arm)
    queue = build_queue_from_batch_report(report)

    assert queue.kind == "THREE_ARM_SYNTHETIC_BATCH"
    assert queue.cross_arm_winner is None
    assert len(queue.items) == 6  # 3 arms * 2 queries * 1 hit
    observed_arms = tuple(dict.fromkeys(item.arm_id for item in queue.items))
    assert observed_arms == DECLARED_ARM_ORDER
    assert len({item.space_id for item in queue.items}) == 3


def test_tampered_batch_report_digest_is_refused() -> None:
    single = _build_single_arm_fixture()
    report = build_single_arm_batch_report(single)
    tampered = copy.deepcopy(report)
    tampered["arms"][0]["queries"][0]["candidates"][0]["score"] = 0.11

    with pytest.raises(VipLabError) as exc_info:
        build_queue_from_batch_report(tampered)
    assert exc_info.value.code == "QUEUE_UPSTREAM_REPORT_INVALID"


def test_candidate_with_binding_eligible_true_or_cut_boundary_is_refused() -> None:
    single = _build_single_arm_fixture()
    report = build_single_arm_batch_report(single)

    bad_binding = copy.deepcopy(report)
    bad_binding["arms"][0]["queries"][0]["candidates"][0]["binding_eligible"] = True
    with pytest.raises(VipLabError) as exc_info:
        build_queue_from_batch_report(bad_binding)
    assert exc_info.value.code in {
        "QUEUE_UPSTREAM_REPORT_INVALID",
        "QUEUE_CANDIDATE_BINDING_FORBIDDEN",
    }

    bad_cut = copy.deepcopy(report)
    bad_cut["arms"][0]["queries"][0]["candidates"][0]["start_pts"] = 90090
    with pytest.raises(VipLabError) as exc_info2:
        build_queue_from_batch_report(bad_cut)
    assert exc_info2.value.code in {
        "QUEUE_UPSTREAM_REPORT_INVALID",
        "QUEUE_CANDIDATE_EDIT_BOUNDARY_FORBIDDEN",
    }


def test_review_intake_preflight_packet_validates_and_strips_untrusted_authority() -> None:
    three_arm = _build_three_arm_fixture()
    queue = build_queue_from_three_arm(three_arm)

    pkt = inspect_review_queue_intake(
        {
            "batch_report": build_three_arm_batch_report(three_arm),
            "approved": True,
        }
    )
    assert pkt.status == ReadinessStatus.READY_SYNTHETIC
    assert "UNTRUSTED_AUTHORITY_FLAGS_IGNORED" in pkt.reasons
    assert pkt.summary["queue_digest"] == queue.queue_digest
    assert pkt.summary["item_count"] == 6
    assert pkt.summary["binding_eligible"] is False
    assert pkt.summary["cross_arm_winner"] is None


def test_verify_candidate_queue_rejects_tampered_item_or_winner_claim() -> None:
    single = _build_single_arm_fixture()
    queue = build_queue_from_single_arm(single)
    raw = queue.to_dict()

    forged_winner = copy.deepcopy(raw)
    forged_winner["cross_arm_winner"] = "VIP_V1_BASE"
    with pytest.raises(VipLabError) as exc_info:
        verify_candidate_queue(forged_winner)
    assert exc_info.value.code == "QUEUE_CROSS_ARM_WINNER_FORBIDDEN"

    forged_review = copy.deepcopy(raw)
    forged_review["items"][0]["review_state"] = "APPROVED"
    with pytest.raises(VipLabError) as exc_info2:
        verify_candidate_queue(forged_review)
    assert exc_info2.value.code == "QUEUE_ITEM_REVIEW_STATE_INVALID"
