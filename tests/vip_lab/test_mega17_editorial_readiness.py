"""Tests for MEGA-17 Workstream D: Gate-3 Native Temporal and Editorial Workflow Readiness."""

from __future__ import annotations

import pytest

from vip_lab.common import ReadinessStatus, VipLabError
from vip_lab.mega17.editorial_readiness import (
    COORDINATE_DOMAINS_SEPARATION,
    REFUSAL_A7_STREAM_NAMESPACE_AMBIGUOUS,
    REFUSAL_AUTHORITATIVE_REAL_EDIT_PLAN_FORBIDDEN,
    REFUSAL_IT6_TERMINAL_TAIL_MISMATCH,
    REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN,
    REFUSAL_SEMANTIC_CANDIDATE_AS_EDIT_BOUNDARY,
    REFUSAL_SYNTHETIC_DECISION_AS_REAL_HUMAN_AUTHORITY,
    EditorialWorkflowReadinessPacket,
    ReviewerHandoffRequirementsPacket,
    build_editorial_workflow_readiness_packet,
    inspect_editorial_workflow_readiness,
    verify_editorial_workflow_readiness_packet,
)


def test_workstream_d_consumes_mega15_and_preserves_lineage_and_mandatory_flags() -> None:
    packet = build_editorial_workflow_readiness_packet()
    assert isinstance(packet, EditorialWorkflowReadinessPacket)

    # Mandatory Section 9 flags
    assert packet.real_source_native_pts_evidence == "NOT_OBSERVED"
    assert packet.human_editorial_decision == "NOT_OBSERVED"
    assert packet.binding_eligible_real_edit is False
    assert packet.authoritative_edit_plan_created is False

    # Consumes MEGA-15 artifacts without reimplementing them
    m15_ref = packet.consumed_mega15_summary
    assert len(m15_ref["preparation_packet_digest"]) == 64
    assert len(m15_ref["temporal_preparation_digest"]) == 64
    assert len(m15_ref["editorial_handoff_digest"]) == 64
    assert len(m15_ref["mega15_lineage_receipt_digest"]) == 64
    assert m15_ref["proposal_revision_numbers"] == [1, 2, 3]

    # Preserves full source/stream/timebase/query/queue/proposal lineage
    lin = packet.lineage_spine
    assert lin["source_occurrence_id"].startswith("occ-")
    assert lin["source_revision_id"]
    assert len(lin["source_sha256"]) == 64
    assert lin["selected_stream_index"] == 0
    assert lin["timebase"] == {"num": 1001, "den": 30000}
    assert lin["query_id"]
    assert lin["queue_item_id"]
    assert len(lin["proposal_v1_digest"]) == 64
    assert len(lin["proposal_v2_digest"]) == 64
    assert len(lin["proposal_v3_digest"]) == 64

    # 5-way coordinate separation
    assert set(packet.coordinate_domain_separation.keys()) == set(COORDINATE_DOMAINS_SEPARATION)
    assert (
        packet.coordinate_domain_separation["SEMANTIC_CANDIDATE_TIMESTAMPS"]["binding_eligible"]
        is False
    )
    assert (
        packet.coordinate_domain_separation["SYNTHETIC_PTS_DIAGNOSTICS"]["binding_eligible"]
        is False
    )
    assert (
        packet.coordinate_domain_separation["SOURCE_NATIVE_PTS_MEASUREMENTS"]["evidence_state"]
        == "NOT_OBSERVED"
    )
    assert (
        packet.coordinate_domain_separation["APPROVED_EDITORIAL_DECISIONS"]["evidence_state"]
        == "NOT_OBSERVED"
    )
    assert (
        packet.coordinate_domain_separation["OUTPUT_TIMELINE_COORDINATES"]["authoritative"]
        is False
    )

    # Reviewer handoff requirements packet is strictly a requirements specification, not a completed review
    req = packet.reviewer_handoff_requirements
    assert isinstance(req, ReviewerHandoffRequirementsPacket)
    assert req.packet_role == "REVIEWER_HANDOFF_REQUIREMENTS_ONLY"
    assert req.completed_human_review is False
    assert req.technical_measurement_readiness == "SYNTHETIC_PREFLIGHT_READY_REAL_PTS_NOT_OBSERVED"
    assert req.editorial_judgment_readiness == "AWAITING_REAL_MEASUREMENT_AND_HUMAN_PRINCIPAL"

    verified = verify_editorial_workflow_readiness_packet(packet)
    assert verified["packet_digest"] == packet.packet_digest


def test_workstream_d_refuses_a7_stream_ambiguity_and_it6_tail_mismatch_and_vfr_fps() -> None:
    # 1. A-7 stream namespace unmapped / ambiguous
    pkt_a7 = inspect_editorial_workflow_readiness(
        {"a7_stream_namespace_ambiguous": True}
    )
    assert pkt_a7.status == ReadinessStatus.BLOCKED
    assert REFUSAL_A7_STREAM_NAMESPACE_AMBIGUOUS in pkt_a7.blockers

    # 2. IT-6 terminal tail duration mismatch
    pkt_it6 = inspect_editorial_workflow_readiness(
        {"it6_terminal_tail_mismatch": True}
    )
    assert pkt_it6.status == ReadinessStatus.BLOCKED
    assert REFUSAL_IT6_TERMINAL_TAIL_MISMATCH in pkt_it6.blockers

    # 3. seconds * nominal_fps derivation
    pkt_fps = inspect_editorial_workflow_readiness(
        {"derive_pts_from_nominal_fps": True}
    )
    assert pkt_fps.status == ReadinessStatus.BLOCKED
    assert REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN in pkt_fps.blockers


def test_workstream_d_refuses_semantic_boundary_and_forged_editorial_authority() -> None:
    pkt = inspect_editorial_workflow_readiness(
        {
            "use_semantic_timestamp_as_edit_cut": True,
            "claim_synthetic_decision_is_real_human": True,
            "claim_authoritative_edit_plan_created": True,
        }
    )
    assert pkt.status == ReadinessStatus.NOT_AUTHORIZED
    assert REFUSAL_SEMANTIC_CANDIDATE_AS_EDIT_BOUNDARY in pkt.blockers
    assert REFUSAL_SYNTHETIC_DECISION_AS_REAL_HUMAN_AUTHORITY in pkt.blockers
    assert REFUSAL_AUTHORITATIVE_REAL_EDIT_PLAN_FORBIDDEN in pkt.blockers
    assert pkt.summary["real_source_native_pts_evidence"] == "NOT_OBSERVED"
    assert pkt.summary["human_editorial_decision"] == "NOT_OBSERVED"
    assert pkt.summary["binding_eligible_real_edit"] is False
    assert pkt.summary["authoritative_edit_plan_created"] is False


def test_workstream_d_tampered_packet_is_rejected() -> None:
    packet = build_editorial_workflow_readiness_packet()
    raw = packet.to_dict()
    raw["binding_eligible_real_edit"] = True
    with pytest.raises(VipLabError):
        verify_editorial_workflow_readiness_packet(raw)
