"""Regression tests for MEGA-13: QC Evidence Completeness, Cross-Stage Lineage & Export Refusal."""

from __future__ import annotations

import copy
import pytest

from gate2.workload import WorkloadSpec
from vip_fvs.synthetic_profiles import V1_PROFILE_ID
from vip_fvs.three_arm_batch import ARM_VIP_V1_BASE
from vip_lab.common import NOT_OBSERVED, ReadinessStatus, VipLabError
from vip_lab.mega09 import (
    CANDIDATE_QUEUE_SCHEMA_VERSION,
    CandidateQueueItem,
    CandidateReviewQueue,
    compute_candidate_queue_digest,
)
from vip_lab.mega10 import build_temporal_refinement_request
from vip_lab.mega11 import (
    advance_proposal_revision,
    build_editorial_proposal,
    compute_editorial_proposal_digest,
)
from vip_lab.mega12 import build_replay_graph_from_workload
from vip_lab.mega13 import (
    CANONICAL_RELEASE_BLOCKER_CODES,
    LINEAGE_AUDIT_SCHEMA_VERSION,
    STAGE_ID,
    LineageAuditReceipt,
    audit_cross_stage_lineage,
    build_release_blocker_summary,
    evaluate_qc_readiness,
)


def _sample_pipeline_artifacts():
    item = CandidateQueueItem(
        queue_item_id="cqi-vip_v1_base-q-01-r1-0123456789abcdef",
        queue_index=0,
        arm_id=ARM_VIP_V1_BASE,
        profile_id=V1_PROFILE_ID,
        model_identity="google/siglip-base-patch16-224",
        space_id="1" * 64,
        generation_id="gen-v1-01",
        catalog_id="cat-01",
        catalog_digest="2" * 64,
        manifest_digest="3" * 64,
        query_id="q-01",
        query_text="grand jete leap",
        rank=1,
        score=0.91,
        revision_id="rev_alpha",
        content_id="cnt_alpha",
        source_path="media/alpha.mp4",
        source_sha256="a" * 64,
        source_sample_pts=1000,
        source_timebase_num=1,
        source_timebase_den=1000,
        timestamp_human="00:00:01.000",
    )
    provisional_queue = CandidateReviewQueue(
        schema_version=CANDIDATE_QUEUE_SCHEMA_VERSION,
        kind="SINGLE_ARM_SYNTHETIC_BATCH",
        upstream_report_digest="4" * 64,
        catalog_id="cat-01",
        catalog_digest="2" * 64,
        query_ids=("q-01",),
        arm_ids=(ARM_VIP_V1_BASE,),
        top_k=5,
        items=(item,),
        queue_digest="0" * 64,
    )
    q_digest = compute_candidate_queue_digest(provisional_queue.payload_without_digest())
    queue = CandidateReviewQueue(
        schema_version=provisional_queue.schema_version,
        kind=provisional_queue.kind,
        upstream_report_digest=provisional_queue.upstream_report_digest,
        catalog_id=provisional_queue.catalog_id,
        catalog_digest=provisional_queue.catalog_digest,
        query_ids=provisional_queue.query_ids,
        arm_ids=provisional_queue.arm_ids,
        top_k=provisional_queue.top_k,
        items=provisional_queue.items,
        queue_digest=q_digest,
    )
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=500,
        requested_end_pts=1500,
        pts_ticks=(0, 500, 1000, 1500, 2000),
    )
    v1 = build_editorial_proposal(
        queue_item=item,
        temporal_request=req,
        proposed_action="REVIEW_CANDIDATE",
        rationale_note="Initial review candidate note.",
    )
    v2 = advance_proposal_revision(
        prior_proposal=v1,
        proposed_action="REQUEST_MEASUREMENT",
        rationale_note="Request source-native PTS measurement.",
    )
    graph = build_replay_graph_from_workload(
        workload_spec=WorkloadSpec(
            jobs=2,
            stages=2,
            artifact_bytes=32,
            cost_units=10,
            fault_position=0,
            seed=42,
            f01_sha="1" * 40,
            c04_sha="2" * 40,
            e05_sha="3" * 40,
            config_digest="4" * 64,
            concurrency=1,
            repetitions=2,
        ),
        generation_id="gen-v1-01",
        semantic_space_id="1" * 64,
        workload_id="wl-mega13",
    )
    return queue, req, v1, v2, graph


def test_audit_cross_stage_lineage_verifies_connected_chain() -> None:
    queue, req, v1, v2, graph = _sample_pipeline_artifacts()
    receipt = audit_cross_stage_lineage(
        candidate_queue=queue,
        temporal_request=req,
        editorial_proposal=v2,
        proposal_revision_chain=[v1, v2],
        replay_graph=graph,
    )
    assert isinstance(receipt, LineageAuditReceipt)
    assert receipt.schema_version == LINEAGE_AUDIT_SCHEMA_VERSION
    assert receipt.lineage_valid is True
    assert receipt.queue_digest == queue.queue_digest
    assert receipt.temporal_request_digest == req.request_digest
    assert receipt.proposal_digest == v2.proposal_digest
    assert receipt.replay_graph_digest == graph.graph_digest
    assert receipt.queue_item_id == queue.items[0].queue_item_id
    assert receipt.revision_id == "rev_alpha"
    assert receipt.source_sha256 == "a" * 64


def test_audit_cross_stage_lineage_rejects_broken_digest_or_source_swap() -> None:
    queue, req, _, v2, _ = _sample_pipeline_artifacts()

    bad_proposal = v2.to_dict()
    bad_proposal["upstream_temporal_request_digest"] = "f" * 64
    bad_proposal["proposal_digest"] = compute_editorial_proposal_digest(bad_proposal)
    with pytest.raises(VipLabError) as exc_digest:
        audit_cross_stage_lineage(
            candidate_queue=queue,
            temporal_request=req,
            editorial_proposal=bad_proposal,
        )
    assert exc_digest.value.code == "LINEAGE_AUDIT_DIGEST_MISMATCH"

    swapped_source = v2.to_dict()
    swapped_source["source_sha256"] = "e" * 64
    swapped_source["proposal_digest"] = compute_editorial_proposal_digest(swapped_source)
    with pytest.raises(VipLabError) as exc_source:
        audit_cross_stage_lineage(
            candidate_queue=queue,
            temporal_request=req,
            editorial_proposal=swapped_source,
        )
    assert exc_source.value.code == "LINEAGE_AUDIT_SOURCE_MISMATCH"


def test_evaluate_qc_readiness_enforces_not_observed_and_refuses_export() -> None:
    queue, req, v1, v2, graph = _sample_pipeline_artifacts()
    packet = evaluate_qc_readiness(
        {
            "candidate_queue": queue.to_dict(),
            "temporal_request": req.to_dict(),
            "editorial_proposal": v2.to_dict(),
            "proposal_revision_chain": [v1.to_dict(), v2.to_dict()],
            "replay_graph": graph.to_dict(),
        }
    )
    assert packet.stage_id == STAGE_ID
    assert packet.status == ReadinessStatus.READY_SYNTHETIC
    assert packet.summary["qc_state"] == NOT_OBSERVED
    assert packet.summary["technical_qc_evidence"] == NOT_OBSERVED
    assert packet.summary["editorial_qc_evidence"] == NOT_OBSERVED
    assert packet.summary["preview_eligible"] is False
    assert packet.summary["production_export_authorized"] is False
    assert packet.summary["export_status"] == "REFUSED_NOT_AUTHORIZED"

    summary = build_release_blocker_summary(
        lineage_receipt=packet.summary["lineage_receipt"],
        qc_packet=packet,
    )
    assert summary["production_export_authorized"] is False
    assert summary["export_status"] == "REFUSED_NOT_AUTHORIZED"
    for code in CANONICAL_RELEASE_BLOCKER_CODES:
        assert code in summary["release_blockers"]


def test_evaluate_qc_readiness_refuses_forged_sensory_observations_and_bare_pass() -> None:
    queue, req, _, v2, _ = _sample_pipeline_artifacts()

    sensory_pkt = evaluate_qc_readiness(
        {
            "candidate_queue": queue.to_dict(),
            "temporal_request": req.to_dict(),
            "editorial_proposal": v2.to_dict(),
            "claimed_evidence_class": "VISUALLY_OBSERVED",
        }
    )
    assert sensory_pkt.status == ReadinessStatus.NOT_AUTHORIZED
    assert "FORGED_SENSORY_OBSERVATION_REFUSED" in sensory_pkt.blockers

    bare_pass_pkt = evaluate_qc_readiness(
        {
            "candidate_queue": queue.to_dict(),
            "temporal_request": req.to_dict(),
            "editorial_proposal": v2.to_dict(),
            "qc_record": {"edit_qc_status": "PASS"},
        }
    )
    assert bare_pass_pkt.status == ReadinessStatus.BLOCKED
    assert "BARE_PASS_QC_INSUFFICIENT" in bare_pass_pkt.blockers

    export_req_pkt = evaluate_qc_readiness(
        {
            "candidate_queue": queue.to_dict(),
            "temporal_request": req.to_dict(),
            "editorial_proposal": v2.to_dict(),
            "request_production_export": True,
        }
    )
    assert export_req_pkt.status == ReadinessStatus.NOT_AUTHORIZED
    assert "PRODUCTION_EXPORT_NOT_AUTHORIZED" in export_req_pkt.blockers
