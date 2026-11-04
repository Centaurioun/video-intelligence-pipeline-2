"""Regression tests for MEGA-11: Versioned Editorial Proposal (Not an Edit Plan)."""

from __future__ import annotations

import pytest

from vip_fvs.synthetic_profiles import V1_PROFILE_ID
from vip_fvs.three_arm_batch import ARM_VIP_V1_BASE
from vip_lab.common import NOT_OBSERVED, ReadinessStatus, VipLabError
from vip_lab.mega09 import CandidateQueueItem
from vip_lab.mega10 import build_temporal_refinement_request
from vip_lab.mega11 import (
    ALLOWED_PROPOSED_ACTIONS,
    EDITORIAL_PROPOSAL_SCHEMA_VERSION,
    STAGE_ID,
    EditorialProposal,
    advance_proposal_revision,
    build_editorial_proposal,
    compute_editorial_proposal_digest,
    inspect_editorial_decision_boundary,
    verify_editorial_proposal,
    verify_proposal_revision_chain,
)


def _sample_queue_and_temporal():
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
    queue_digest = "b" * 64
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue_digest,
        selected_stream_index=0,
        requested_start_pts=500,
        requested_end_pts=1500,
        pts_ticks=(0, 500, 1000, 1500, 2000),
    )
    return item, queue_digest, req


def test_build_initial_editorial_proposal_and_verify() -> None:
    item, queue_digest, req = _sample_queue_and_temporal()
    proposal = build_editorial_proposal(
        queue_item=item,
        temporal_request=req,
        proposed_action="REQUEST_MEASUREMENT",
        rationale_note="Request source-native frame measurement around candidate window.",
    )
    assert isinstance(proposal, EditorialProposal)
    assert proposal.schema_version == EDITORIAL_PROPOSAL_SCHEMA_VERSION
    assert proposal.proposal_version == 1
    assert proposal.parent_proposal_digest is None
    assert proposal.upstream_queue_digest == queue_digest
    assert proposal.upstream_temporal_request_digest == req.request_digest
    assert proposal.queue_item_id == item.queue_item_id
    assert proposal.temporal_request_id == req.request_id
    assert proposal.revision_id == item.revision_id
    assert proposal.source_path == item.source_path
    assert proposal.source_sha256 == item.source_sha256
    assert proposal.proposed_action in ALLOWED_PROPOSED_ACTIONS
    assert proposal.accepted_authority is False
    assert proposal.proposal_status == "PROPOSED_NOT_APPROVED"
    assert proposal.human_decision_state == NOT_OBSERVED
    assert proposal.evidence_state == NOT_OBSERVED
    assert proposal.is_edit_plan is False
    assert proposal.binding_eligible is False
    assert verify_editorial_proposal(proposal) == proposal.proposal_digest
    assert compute_editorial_proposal_digest(proposal.to_dict()) == proposal.proposal_digest


def test_advance_proposal_revision_and_verify_chain() -> None:
    item, _, req = _sample_queue_and_temporal()
    v1 = build_editorial_proposal(
        queue_item=item,
        temporal_request=req,
        proposed_action="REVIEW_CANDIDATE",
        rationale_note="Initial nonbinding review note.",
    )
    v2 = advance_proposal_revision(
        prior_proposal=v1,
        proposed_action="REQUEST_MEASUREMENT",
        rationale_note="Refine to request source-native PTS measurement.",
    )
    v3 = advance_proposal_revision(
        prior_proposal=v2,
        proposed_action="DEFER_PENDING_EVIDENCE",
        rationale_note="Defer editorial decision until real media authority exists.",
    )
    assert v1.proposal_version == 1
    assert v1.parent_proposal_digest is None
    assert v2.proposal_version == 2
    assert v2.parent_proposal_digest == v1.proposal_digest
    assert v3.proposal_version == 3
    assert v3.parent_proposal_digest == v2.proposal_digest
    assert v1.proposed_action == "REVIEW_CANDIDATE"

    chain_summary = verify_proposal_revision_chain([v1, v2, v3])
    assert chain_summary["chain_length"] == 3
    assert chain_summary["root_proposal_digest"] == v1.proposal_digest
    assert chain_summary["head_proposal_digest"] == v3.proposal_digest
    assert chain_summary["accepted_authority"] is False


def test_revision_chain_rejects_broken_parent_or_version_gap_or_cross_lineage() -> None:
    item, _, req = _sample_queue_and_temporal()
    v1 = build_editorial_proposal(
        queue_item=item,
        temporal_request=req,
        proposed_action="REVIEW_CANDIDATE",
        rationale_note="v1 note",
    )
    v2 = advance_proposal_revision(
        prior_proposal=v1,
        proposed_action="REQUEST_MEASUREMENT",
        rationale_note="v2 note",
    )
    v3 = advance_proposal_revision(
        prior_proposal=v2,
        proposed_action="DEFER_PENDING_EVIDENCE",
        rationale_note="v3 note",
    )
    with pytest.raises(VipLabError) as exc_gap:
        verify_proposal_revision_chain([v1, v3])
    assert exc_gap.value.code == "PROPOSAL_REVISION_VERSION_GAP"

    tampered_v2 = v2.to_dict()
    tampered_v2["parent_proposal_digest"] = "f" * 64
    tampered_v2["proposal_digest"] = compute_editorial_proposal_digest(tampered_v2)
    with pytest.raises(VipLabError) as exc_parent:
        verify_proposal_revision_chain([v1, tampered_v2])
    assert exc_parent.value.code == "PROPOSAL_REVISION_PARENT_MISMATCH"

    cross_v2 = v2.to_dict()
    cross_v2["revision_id"] = "rev_other"
    cross_v2["proposal_digest"] = compute_editorial_proposal_digest(cross_v2)
    with pytest.raises(VipLabError) as exc_lineage:
        verify_proposal_revision_chain([v1, cross_v2])
    assert exc_lineage.value.code == "PROPOSAL_REVISION_LINEAGE_MISMATCH"


def test_build_proposal_rejects_mismatched_candidate_and_temporal_request() -> None:
    item, _, req = _sample_queue_and_temporal()
    other_item = CandidateQueueItem(
        queue_item_id="cqi-vip_v1_base-q-99-r1-9999999999999999",
        queue_index=1,
        arm_id=item.arm_id,
        profile_id=item.profile_id,
        model_identity=item.model_identity,
        space_id=item.space_id,
        generation_id=item.generation_id,
        catalog_id=item.catalog_id,
        catalog_digest=item.catalog_digest,
        manifest_digest=item.manifest_digest,
        query_id=item.query_id,
        query_text=item.query_text,
        rank=item.rank,
        score=item.score,
        revision_id=item.revision_id,
        content_id=item.content_id,
        source_path=item.source_path,
        source_sha256=item.source_sha256,
        source_sample_pts=item.source_sample_pts,
        source_timebase_num=item.source_timebase_num,
        source_timebase_den=item.source_timebase_den,
        timestamp_human=item.timestamp_human,
    )
    with pytest.raises(VipLabError) as exc_info:
        build_editorial_proposal(
            queue_item=other_item,
            temporal_request=req,
            proposed_action="REVIEW_CANDIDATE",
            rationale_note="mismatch test",
        )
    assert exc_info.value.code == "PROPOSAL_UPSTREAM_LINEAGE_MISMATCH"


def test_decision_boundary_refuses_forged_approval_and_edit_plan_promotion() -> None:
    item, _, req = _sample_queue_and_temporal()
    v1 = build_editorial_proposal(
        queue_item=item,
        temporal_request=req,
        proposed_action="REVIEW_CANDIDATE",
        rationale_note="v1 note",
    )
    v2 = advance_proposal_revision(
        prior_proposal=v1,
        proposed_action="REQUEST_MEASUREMENT",
        rationale_note="v2 note",
    )

    ok_packet = inspect_editorial_decision_boundary(
        {
            "proposal": v2.to_dict(),
            "revision_chain": [v1.to_dict(), v2.to_dict()],
        }
    )
    assert ok_packet.stage_id == STAGE_ID
    assert ok_packet.status == ReadinessStatus.READY_SYNTHETIC

    forged_approval_packet = inspect_editorial_decision_boundary(
        {
            "proposal": v2.to_dict(),
            "approved": True,
            "signed_by": "editor_alice",
        }
    )
    assert forged_approval_packet.status == ReadinessStatus.NOT_AUTHORIZED
    assert "FORGED_HUMAN_DECISION_REFUSED" in forged_approval_packet.blockers

    promotion_packet = inspect_editorial_decision_boundary(
        {
            "proposal": v2.to_dict(),
            "promote_to_edit_plan": True,
        }
    )
    assert promotion_packet.status == ReadinessStatus.NOT_AUTHORIZED
    assert "EDITORIAL_PROPOSAL_PROMOTION_REFUSED" in promotion_packet.blockers
