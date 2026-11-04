"""Unit and adversarial regression tests for MEGA-15 (`vip_lab.mega15`).

Covers against ACTUAL repository contracts:
- MEGA-15.1: `TemporalPreparationRecord`, CFR/VFR PTS resolution, duplicate PTS
  disambiguation, PTS discontinuity refusal vs explicit subdivision, terminal tail
  refusal vs explicit `tail_end` fallback, `seconds * nominal_fps` refusal,
  stream namespace refusal (`audio:0`), forged measurement refusal, and non-monotonic PTS refusal.
- MEGA-15.2: `EditorialHandoffEnvelope`, `Gate3OfflinePreparationPacket`,
  non-human principal refusal (`MODEL`, `TOOL`), unobserved `HUMAN` decision refusal,
  `EditPlanRevision` / `compile_handoff` refusal, and multi-revision chain integrity.
- MEGA-15.3: `Mega15LineageReceipt`, preservation of duplicate `source_sha256`
  occurrences with distinct `source_path`/`revision_id`/`content_id`, preservation of
  identical `query_text` under distinct `query_id`, truthful `False` reporting when
  duplicates are absent from the input fixture, and stale proposal revision refusal.
"""

from __future__ import annotations

from dataclasses import replace
import pytest

from vip_fvs.synthetic_profiles import V1_PROFILE_ID, V2_BASE_PROFILE_ID
from vip_fvs.three_arm_batch import PROFILE_ID_TO_ARM
from vip_lab.common import (
    SyntheticContextMarker,
    VipLabError,
    canonical_sha256,
)
from vip_lab.mega09 import (
    CANDIDATE_QUEUE_SCHEMA_VERSION,
    CandidateQueueItem,
    CandidateReviewQueue,
    verify_candidate_queue,
)
from vip_lab.mega10 import (
    PtsFixtureDiagnostic,
    build_temporal_refinement_request,
    evaluate_pts_fixture_diagnostic,
)
from vip_lab.mega11 import (
    advance_proposal_revision,
    build_editorial_proposal,
)
from vip_lab.mega13 import audit_cross_stage_lineage
from vip_lab.mega15 import (
    REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN,
    REFUSAL_BINDING_ELIGIBILITY_ESCALATION,
    REFUSAL_CANDIDATE_AS_EXACT_CUT,
    REFUSAL_COMPILE_HANDOFF_FORBIDDEN,
    REFUSAL_CROSS_STAGE_JOIN_MISMATCH,
    REFUSAL_DUPLICATE_PTS_AMBIGUOUS,
    REFUSAL_FORGED_SOURCE_MEASUREMENT,
    REFUSAL_HUMAN_DECISION_NOT_OBSERVED,
    REFUSAL_MEGA15_LINEAGE_BROKEN,
    REFUSAL_NOMINAL_FPS_DERIVATION,
    REFUSAL_NON_HUMAN_PRINCIPAL,
    REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE,
    REFUSAL_PROPOSAL_AS_AUTHORITATIVE_PLAN,
    REFUSAL_PROPOSAL_CHAIN_BROKEN,
    REFUSAL_PTS_DISCONTINUITY_UNRESOLVED,
    REFUSAL_PTS_NON_MONOTONIC,
    REFUSAL_QUERY_IDENTITY_COLLAPSE,
    REFUSAL_STALE_PROPOSAL_REVISION,
    REFUSAL_STREAM_NAMESPACE_MISMATCH,
    REFUSAL_TIMEBASE_MISMATCH,
    REFUSAL_TERMINAL_TAIL_UNRESOLVED,
    audit_mega15_lineage,
    build_editorial_handoff_envelope,
    build_gate3_offline_preparation_packet,
    build_temporal_preparation_record,
    refuse_authoritative_handoff_minting,
    refuse_nominal_fps_derivation,
    refuse_non_human_or_unobserved_principal,
    refuse_semantic_candidate_as_cut,
    validate_video_stream_namespace,
    verify_editorial_handoff_envelope,
    verify_gate3_offline_preparation_packet,
    verify_mega15_lineage_receipt,
    verify_temporal_preparation_record,
)
from vip_lab.mega15.temporal_preflight import REFUSAL_SYNTHETIC_TO_REAL_ESCALATION


def _make_candidate_item(
    *,
    queue_item_id: str = "qitem_001",
    queue_index: int = 0,
    arm_id: str | None = None,
    profile_id: str = V1_PROFILE_ID,
    model_identity: str = "google/siglip-base-patch16-224",
    space_id: str = "1" * 64,
    generation_id: str = "2" * 64,
    catalog_id: str = "cat_mega15_test",
    catalog_digest: str = "3" * 64,
    manifest_digest: str = "4" * 64,
    query_id: str = "q_01",
    query_text: str = "ballet grand jete leap",
    rank: int = 1,
    score: float = 0.875,
    revision_id: str = "rev_001",
    content_id: str = "cnt_001",
    source_path: str = "synthetic://archive/ballet_a.mp4",
    source_sha256: str = "5" * 64,
    source_sample_pts: int = 2000,
    source_timebase_num: int = 1,
    source_timebase_den: int = 1000,
) -> CandidateQueueItem:
    resolved_arm_id = arm_id if arm_id is not None else PROFILE_ID_TO_ARM[profile_id]
    return CandidateQueueItem(
        queue_item_id=queue_item_id,
        queue_index=queue_index,
        arm_id=resolved_arm_id,
        profile_id=profile_id,
        model_identity=model_identity,
        space_id=space_id,
        generation_id=generation_id,
        catalog_id=catalog_id,
        catalog_digest=catalog_digest,
        manifest_digest=manifest_digest,
        query_id=query_id,
        query_text=query_text,
        rank=rank,
        score=score,
        revision_id=revision_id,
        content_id=content_id,
        source_path=source_path,
        source_sha256=source_sha256,
        source_sample_pts=source_sample_pts,
        source_timebase_num=source_timebase_num,
        source_timebase_den=source_timebase_den,
        timestamp_human="00:00:02.000",
        thumbnail_path=None,
        thumbnail_status="MISSING",
    )


def _build_verified_queue(
    items: list[CandidateQueueItem],
    *,
    catalog_id: str = "cat_mega15_test",
) -> CandidateReviewQueue:
    from vip_fvs.three_arm_batch import DECLARED_ARM_ORDER
    from vip_lab.mega09 import compute_candidate_queue_digest

    query_ids = tuple(dict.fromkeys(it.query_id for it in items))
    unique_arms = tuple(dict.fromkeys(it.arm_id for it in items))
    if len(unique_arms) > 1:
        kind = "THREE_ARM_SYNTHETIC_BATCH"
        arm_ids = DECLARED_ARM_ORDER
    else:
        kind = "SINGLE_ARM_SYNTHETIC_BATCH"
        arm_ids = unique_arms
    upstream_report_digest = "6" * 64
    catalog_digest = items[0].catalog_digest if items else "3" * 64
    top_k = max(it.rank for it in items) if items else 1
    provisional = CandidateReviewQueue(
        schema_version=CANDIDATE_QUEUE_SCHEMA_VERSION,
        kind=kind,
        upstream_report_digest=upstream_report_digest,
        catalog_id=catalog_id,
        catalog_digest=catalog_digest,
        query_ids=query_ids,
        arm_ids=arm_ids,
        top_k=top_k,
        items=tuple(items),
        queue_digest="0" * 64,
        cross_arm_winner=None,
        synthetic_only=True,
        authentic_model_evidence=False,
    )
    queue_digest = compute_candidate_queue_digest(provisional.payload_without_digest())
    queue = CandidateReviewQueue(
        schema_version=CANDIDATE_QUEUE_SCHEMA_VERSION,
        kind=kind,
        upstream_report_digest=upstream_report_digest,
        catalog_id=catalog_id,
        catalog_digest=catalog_digest,
        query_ids=query_ids,
        arm_ids=arm_ids,
        top_k=top_k,
        items=tuple(items),
        queue_digest=queue_digest,
        cross_arm_winner=None,
        synthetic_only=True,
        authentic_model_evidence=False,
    )
    verify_candidate_queue(queue.to_dict())
    return queue


def _make_three_item_queue_with_duplicates() -> CandidateReviewQueue:
    shared_sha = "b" * 64
    item_1 = _make_candidate_item(
        queue_item_id="qitem_dup_1",
        queue_index=0,
        profile_id=V1_PROFILE_ID,
        model_identity="google/siglip-base-patch16-224",
        space_id="1" * 64,
        generation_id="2" * 64,
        query_id="q_dup_text_1",
        query_text="adagio promenade en dehors",
        revision_id="rev_cam_a",
        content_id="cnt_cam_a",
        source_path="synthetic://archive/camera_a/adagio.mp4",
        source_sha256=shared_sha,
        source_sample_pts=1000,
    )
    item_2 = _make_candidate_item(
        queue_item_id="qitem_dup_2",
        queue_index=1,
        profile_id=V2_BASE_PROFILE_ID,
        model_identity="google/siglip2-base-patch16-224",
        space_id="7" * 64,
        generation_id="8" * 64,
        query_id="q_dup_text_2",
        query_text="adagio promenade en dehors",
        revision_id="rev_cam_b",
        content_id="cnt_cam_b",
        source_path="synthetic://archive/backup_mirror/adagio_copy.mp4",
        source_sha256=shared_sha,
        source_sample_pts=2000,
    )
    item_3 = _make_candidate_item(
        queue_item_id="qitem_unique_3",
        queue_index=2,
        profile_id=V1_PROFILE_ID,
        model_identity="google/siglip-base-patch16-224",
        space_id="1" * 64,
        generation_id="2" * 64,
        query_id="q_unique_3",
        query_text="coda fouette turns",
        revision_id="rev_coda_3",
        content_id="cnt_coda_3",
        source_path="synthetic://archive/coda.mp4",
        source_sha256="f" * 64,
        source_sample_pts=1500,
    )
    return _build_verified_queue([item_1, item_2, item_3])


def test_cfr_and_vfr_temporal_preparation_record_roundtrip() -> None:
    queue = _build_verified_queue([_make_candidate_item()])
    item = queue.items[0]
    pts_ticks = (0, 950, 2000, 3100, 4050, 5000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=900,
        requested_end_pts=4000,
        pts_ticks=pts_ticks,
        declared_rate_num=1,
        declared_rate_den=1000,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=pts_ticks,
        requested_start_pts=req.requested_start_pts,
        requested_end_pts=req.requested_end_pts,
        declared_rate_num=1,
        declared_rate_den=1000,
    )
    rec = build_temporal_preparation_record(
        refinement_request=req,
        pts_diagnostic=diag,
        declared_rate_num=1,
        declared_rate_den=1000,
    )
    assert rec.resolved_start_pts == 950
    assert rec.resolved_end_pts == 4050
    assert rec.is_vfr is True
    assert rec.vfr_classification == "VFR"
    assert rec.has_discontinuity is False
    assert rec.subdivided_segments == ((950, 4050),)
    assert rec.source_pts_evidence_state == "NOT_OBSERVED"
    assert rec.authoritative_source_measurement is False
    assert rec.binding_eligible is False
    assert rec.stream_id == "video:0"

    restored = verify_temporal_preparation_record(rec.to_dict())
    assert restored == rec


def test_nominal_fps_and_candidate_as_cut_refusals() -> None:
    with pytest.raises(VipLabError, match=REFUSAL_NOMINAL_FPS_DERIVATION) as exc_info:
        refuse_nominal_fps_derivation(seconds=2.5, nominal_fps=29.97)
    assert exc_info.value.code == REFUSAL_NOMINAL_FPS_DERIVATION

    with pytest.raises(VipLabError, match=REFUSAL_CANDIDATE_AS_EXACT_CUT) as exc_info2:
        refuse_semantic_candidate_as_cut(evidence_class="MATCHED", treat_as_exact_cut=True)
    assert exc_info2.value.code == REFUSAL_CANDIDATE_AS_EXACT_CUT

    queue = _build_verified_queue([_make_candidate_item()])
    item = queue.items[0]
    pts_ticks = (0, 1000, 2000, 3000, 4000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=3000,
        pts_ticks=pts_ticks,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=pts_ticks,
        requested_start_pts=1000,
        requested_end_pts=3000,
    )
    with pytest.raises(VipLabError, match=REFUSAL_NOMINAL_FPS_DERIVATION):
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=diag,
            seconds=1.0,
            nominal_fps=30.0,
        )
    with pytest.raises(VipLabError, match=REFUSAL_CANDIDATE_AS_EXACT_CUT):
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=diag,
            treat_candidate_as_exact_cut=True,
        )


def test_duplicate_pts_requires_explicit_occurrence() -> None:
    queue = _build_verified_queue([_make_candidate_item(source_sample_pts=1000)])
    item = queue.items[0]
    dup_ticks = (0, 1000, 1000, 2000, 3000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=2500,
        pts_ticks=dup_ticks,
        start_occurrence=0,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=dup_ticks,
        requested_start_pts=1000,
        requested_end_pts=2500,
        start_occurrence=0,
    )
    with pytest.raises(VipLabError, match=REFUSAL_DUPLICATE_PTS_AMBIGUOUS) as exc_info:
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=diag,
            start_occurrence=None,
        )
    assert exc_info.value.code == REFUSAL_DUPLICATE_PTS_AMBIGUOUS

    rec = build_temporal_preparation_record(
        refinement_request=req,
        pts_diagnostic=diag,
        start_occurrence=1,
    )
    assert rec.resolved_start_pts == 1000
    assert rec.start_occurrence == 1


def test_pts_discontinuity_refused_unless_explicitly_subdivided() -> None:
    queue = _build_verified_queue([_make_candidate_item(source_sample_pts=1000)])
    item = queue.items[0]
    # Monotonic ticks with a large forward discontinuity gap (3000 -> 10000 > 3 * 1000)
    disc_ticks = (0, 1000, 2000, 3000, 10000, 11000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=10500,
        pts_ticks=disc_ticks,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=disc_ticks,
        requested_start_pts=1000,
        requested_end_pts=10500,
    )
    with pytest.raises(VipLabError, match=REFUSAL_PTS_DISCONTINUITY_UNRESOLVED) as exc_info:
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=diag,
            allow_discontinuity_subdivision=False,
        )
    assert exc_info.value.code == REFUSAL_PTS_DISCONTINUITY_UNRESOLVED

    rec = build_temporal_preparation_record(
        refinement_request=req,
        pts_diagnostic=diag,
        allow_discontinuity_subdivision=True,
    )
    assert rec.has_discontinuity is True
    assert rec.discontinuity_subdivided is True
    assert len(rec.subdivided_segments) == 2
    assert rec.subdivided_segments == ((1000, 3000), (10000, 11000))


def test_non_monotonic_pts_table_refused() -> None:
    queue = _build_verified_queue([_make_candidate_item(source_sample_pts=1000)])
    item = queue.items[0]
    valid_ticks = (0, 1000, 2000, 3000, 4000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=3000,
        pts_ticks=valid_ticks,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=valid_ticks,
        requested_start_pts=1000,
        requested_end_pts=3000,
    )
    non_monotonic_diag = replace(diag, pts_ticks=[0, 1000, 2500, 1800, 3000, 4000])
    with pytest.raises(VipLabError, match=REFUSAL_PTS_NON_MONOTONIC) as exc_info:
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=non_monotonic_diag,
        )
    assert exc_info.value.code == REFUSAL_PTS_NON_MONOTONIC


def test_terminal_tail_refused_unless_explicit_fallback_enabled() -> None:
    queue = _build_verified_queue([_make_candidate_item(source_sample_pts=1000)])
    item = queue.items[0]
    valid_ticks = (0, 1000, 2000, 3000, 4000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=3500,
        pts_ticks=valid_ticks,
    )
    base_diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=valid_ticks,
        requested_start_pts=1000,
        requested_end_pts=3500,
    )
    diag = replace(base_diag, pts_ticks=(0, 1000, 2000, 3000))
    with pytest.raises(VipLabError, match=REFUSAL_TERMINAL_TAIL_UNRESOLVED) as exc_info:
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=diag,
            allow_terminal_tail_fallback=False,
        )
    assert exc_info.value.code == REFUSAL_TERMINAL_TAIL_UNRESOLVED

    rec = build_temporal_preparation_record(
        refinement_request=req,
        pts_diagnostic=diag,
        allow_terminal_tail_fallback=True,
    )
    assert rec.resolved_end_pts == 4000
    assert rec.end_snap_policy == "EXPLICIT_TAIL_END_FALLBACK"


def test_stream_namespace_and_forged_measurement_refusals() -> None:
    import copy

    with pytest.raises(VipLabError, match=REFUSAL_STREAM_NAMESPACE_MISMATCH):
        validate_video_stream_namespace("audio:0")
    with pytest.raises(VipLabError, match=REFUSAL_STREAM_NAMESPACE_MISMATCH):
        validate_video_stream_namespace("video:abc")

    queue = _build_verified_queue([_make_candidate_item()])
    item = queue.items[0]
    pts_ticks = (0, 1000, 2000, 3000, 4000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=3000,
        pts_ticks=pts_ticks,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=pts_ticks,
        requested_start_pts=1000,
        requested_end_pts=3000,
    )

    with pytest.raises(VipLabError, match=REFUSAL_STREAM_NAMESPACE_MISMATCH):
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=diag,
            stream_id="audio:0",
        )

    forged_diag = copy.copy(diag)
    object.__setattr__(forged_diag, "authoritative_source_measurement", True)
    with pytest.raises(VipLabError, match=REFUSAL_FORGED_SOURCE_MEASUREMENT):
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=forged_diag,
        )

    bad_tb_diag = replace(diag, timebase_den=90000)
    with pytest.raises(VipLabError, match=REFUSAL_TIMEBASE_MISMATCH):
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=bad_tb_diag,
        )


def test_editorial_principal_and_authoritative_plan_refusals() -> None:
    for non_human in ("MODEL", "TOOL"):
        with pytest.raises(VipLabError, match=REFUSAL_NON_HUMAN_PRINCIPAL) as exc_info:
            refuse_non_human_or_unobserved_principal(principal_kind=non_human)
        assert exc_info.value.code == REFUSAL_NON_HUMAN_PRINCIPAL

    with pytest.raises(VipLabError, match=REFUSAL_HUMAN_DECISION_NOT_OBSERVED) as exc_info2:
        refuse_non_human_or_unobserved_principal(
            principal_kind="HUMAN",
            real_human_decision_state="NOT_OBSERVED",
            claim_human_approval=True,
        )
    assert exc_info2.value.code == REFUSAL_HUMAN_DECISION_NOT_OBSERVED

    with pytest.raises(VipLabError, match=REFUSAL_PROPOSAL_AS_AUTHORITATIVE_PLAN):
        refuse_authoritative_handoff_minting(attempt_promote_proposal=True)
    with pytest.raises(VipLabError, match=REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN):
        refuse_authoritative_handoff_minting(attempt_edit_plan=True)
    with pytest.raises(VipLabError, match=REFUSAL_COMPILE_HANDOFF_FORBIDDEN):
        refuse_authoritative_handoff_minting(attempt_compile_handoff=True)


def test_editorial_handoff_envelope_and_broken_chain_refusal() -> None:
    queue = _build_verified_queue([_make_candidate_item()])
    item = queue.items[0]
    pts_ticks = (0, 1000, 2000, 3000, 4000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=3000,
        pts_ticks=pts_ticks,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=pts_ticks,
        requested_start_pts=1000,
        requested_end_pts=3000,
    )
    t_rec = build_temporal_preparation_record(refinement_request=req, pts_diagnostic=diag)

    v1 = build_editorial_proposal(
        queue_item=item,
        temporal_request=req,
        proposed_action="REVIEW_CANDIDATE",
        rationale_note="Initial review candidate.",
    )
    v2 = advance_proposal_revision(
        prior_proposal=v1,
        proposed_action="REQUEST_MEASUREMENT",
        rationale_note="Request source PTS measurement.",
    )
    v3 = advance_proposal_revision(
        prior_proposal=v2,
        proposed_action="DEFER_PENDING_EVIDENCE",
        rationale_note="Hold pending real PTS and human review.",
    )

    env = build_editorial_handoff_envelope(
        candidate_item=item,
        temporal_record=t_rec,
        proposal_revisions=(v1, v2, v3),
    )
    assert env.latest_proposal_version == 3
    assert env.latest_revision_number == 3
    assert env.real_human_decision_state == "NOT_OBSERVED"
    assert env.accepted_authority is False
    assert env.is_edit_plan is False
    assert env.is_compiled_handoff is False
    assert env.authoritative_plan_eligible is False
    assert env.binding_eligible is False
    assert verify_editorial_handoff_envelope(env.to_dict()) == env

    # Skipping v2 breaks revision number & parent_proposal_digest chain
    with pytest.raises(VipLabError, match=REFUSAL_PROPOSAL_CHAIN_BROKEN):
        build_editorial_handoff_envelope(
            candidate_item=item,
            temporal_record=t_rec,
            proposal_revisions=(v1, v3),
        )


def test_mega15_lineage_preserves_duplicates_and_rejects_collapse_or_stale_revision() -> None:
    queue = _make_three_item_queue_with_duplicates()
    t_reqs = []
    t_recs = []
    p_chains = []
    h_envs = []

    for item in queue.items:
        pts_ticks = (0, 1000, 2000, 3000, 4000)
        req = build_temporal_refinement_request(
            item,
            upstream_queue_digest=queue.queue_digest,
            selected_stream_index=0,
            requested_start_pts=1000,
            requested_end_pts=3000,
            pts_ticks=pts_ticks,
        )
        diag = evaluate_pts_fixture_diagnostic(
            timebase_num=item.source_timebase_num,
            timebase_den=item.source_timebase_den,
            pts_ticks=pts_ticks,
            requested_start_pts=1000,
            requested_end_pts=3000,
        )
        t_rec = build_temporal_preparation_record(refinement_request=req, pts_diagnostic=diag)
        v1 = build_editorial_proposal(
            queue_item=item,
            temporal_request=req,
            proposed_action="REVIEW_CANDIDATE",
            rationale_note=f"v1 for {item.queue_item_id}",
        )
        v2 = advance_proposal_revision(
            prior_proposal=v1,
            proposed_action="REQUEST_MEASUREMENT",
            rationale_note=f"v2 for {item.queue_item_id}",
        )
        env = build_editorial_handoff_envelope(
            candidate_item=item,
            temporal_record=t_rec,
            proposal_revisions=(v1, v2),
        )
        t_reqs.append(req)
        t_recs.append(t_rec)
        p_chains.append((v1, v2))
        h_envs.append(env)

    packet = build_gate3_offline_preparation_packet(
        candidate_queue=queue,
        temporal_records=t_recs,
        handoff_envelopes=h_envs,
    )
    assert verify_gate3_offline_preparation_packet(packet.to_dict()) == packet

    # Dropping a duplicate occurrence item must fail closed
    with pytest.raises(VipLabError, match=REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE):
        build_gate3_offline_preparation_packet(
            candidate_queue=queue,
            temporal_records=t_recs[:2],
            handoff_envelopes=h_envs[:2],
        )

    m13_receipt = audit_cross_stage_lineage(
        candidate_queue=queue,
        temporal_request=t_reqs[0],
        editorial_proposal=p_chains[0][-1],
        proposal_revision_chain=p_chains[0],
    )
    m15_receipt = audit_mega15_lineage(
        queue=queue,
        temporal_requests=t_reqs,
        proposal_chains=p_chains,
        preparation_packet=packet,
        upstream_lineage_receipt=m13_receipt,
    )
    assert m15_receipt.lineage_valid is True
    assert m15_receipt.duplicate_occurrence_paths_preserved is True
    assert m15_receipt.duplicate_query_texts_preserved is True
    assert m15_receipt.upstream_lineage_receipt_digest == m13_receipt.receipt_digest
    assert verify_mega15_lineage_receipt(m15_receipt.to_dict()) == m15_receipt

    # Stale proposal revision in handoff envelope must be refused by lineage audit
    stale_env_0 = build_editorial_handoff_envelope(
        candidate_item=queue.items[0],
        temporal_record=t_recs[0],
        proposal_revisions=(p_chains[0][0],),
    )
    stale_packet = build_gate3_offline_preparation_packet(
        candidate_queue=queue,
        temporal_records=t_recs,
        handoff_envelopes=[stale_env_0, h_envs[1], h_envs[2]],
    )
    with pytest.raises(VipLabError, match=REFUSAL_STALE_PROPOSAL_REVISION):
        audit_mega15_lineage(
            queue=queue,
            temporal_requests=t_reqs,
            proposal_chains=p_chains,
            preparation_packet=stale_packet,
            upstream_lineage_receipt=m13_receipt,
        )


def test_mega15_lineage_truthfully_reports_false_when_no_duplicates_exist() -> None:
    """When input fixture has no duplicate source_sha256 or query_text, flags must be False."""
    single_queue = _build_verified_queue([_make_candidate_item()])
    item = single_queue.items[0]
    pts_ticks = (0, 1000, 2000, 3000, 4000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=single_queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=3000,
        pts_ticks=pts_ticks,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=pts_ticks,
        requested_start_pts=1000,
        requested_end_pts=3000,
    )
    t_rec = build_temporal_preparation_record(refinement_request=req, pts_diagnostic=diag)
    v1 = build_editorial_proposal(
        queue_item=item,
        temporal_request=req,
        proposed_action="REVIEW_CANDIDATE",
        rationale_note="Single unique item review.",
    )
    env = build_editorial_handoff_envelope(
        candidate_item=item,
        temporal_record=t_rec,
        proposal_revisions=(v1,),
    )
    packet = build_gate3_offline_preparation_packet(
        candidate_queue=single_queue,
        temporal_records=(t_rec,),
        handoff_envelopes=(env,),
    )
    receipt = audit_mega15_lineage(
        queue=single_queue,
        temporal_requests=(req,),
        proposal_chains=((v1,),),
        preparation_packet=packet,
    )
    assert receipt.lineage_valid is True
    assert receipt.duplicate_occurrence_paths_preserved is False
    assert receipt.duplicate_query_texts_preserved is False


def test_synthetic_context_authority_escalation_refused() -> None:
    queue = _build_verified_queue([_make_candidate_item()])
    item = queue.items[0]
    pts_ticks = (0, 1000, 2000, 3000, 4000)
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest=queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=1000,
        requested_end_pts=3000,
        pts_ticks=pts_ticks,
    )
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        pts_ticks=pts_ticks,
        requested_start_pts=1000,
        requested_end_pts=3000,
    )
    rec = build_temporal_preparation_record(refinement_request=req, pts_diagnostic=diag)
    payload = rec.to_dict()
    payload["synthetic_context"]["authentic_authority_granted"] = True
    with pytest.raises(VipLabError, match=REFUSAL_SYNTHETIC_TO_REAL_ESCALATION):
        verify_temporal_preparation_record(payload)

    with pytest.raises(VipLabError, match="LAB_AUTHORITY_ESCALATION_FORBIDDEN"):
        SyntheticContextMarker(
            token="VIP_LAB_SYNTHETIC_ONLY_V1",
            synthetic_only=True,
            authentic_authority_granted=True,
        )

    import copy

    escalated_ctx = copy.copy(rec.synthetic_context)
    object.__setattr__(escalated_ctx, "authentic_authority_granted", True)
    bad_rec = replace(rec, synthetic_context=escalated_ctx)
    with pytest.raises(VipLabError, match=REFUSAL_SYNTHETIC_TO_REAL_ESCALATION):
        bad_rec.validate()
