from __future__ import annotations

import pytest

from gate3.editorial import ModelToolPrincipalError
from gate3.pts import PtsTable
from gate3.rational import TimeBase
from gate3.refinement import is_binding_eligible
from vip_lab.common import NOT_OBSERVED, VipLabError
from vip_lab.mega09 import CandidateQueueItem, CandidateReviewQueue, verify_candidate_queue
from vip_lab.mega10 import (
    PtsFixtureDiagnostic,
    TemporalRefinementRequest,
    build_temporal_refinement_request,
    evaluate_pts_fixture_diagnostic,
)
from vip_lab.mega11 import (
    EditorialProposal,
    advance_proposal_revision,
    build_editorial_proposal,
)
from vip_lab.mega15 import (
    EditorialHandoffEnvelope,
    Gate3LineageCertificate,
    Gate3PreparationPacket,
    REFUSAL_AMBIGUOUS_DUPLICATE_PTS,
    REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN,
    REFUSAL_FORGED_MEASURED_PTS,
    REFUSAL_HUMAN_DECISION_NOT_OBSERVED,
    REFUSAL_MODEL_OR_TOOL_PRINCIPAL_FORBIDDEN,
    REFUSAL_NOMINAL_FPS_FORBIDDEN,
    REFUSAL_PTS_DISCONTINUITY,
    REFUSAL_REVIEW_BUNDLE_REAL_MEASURED_FORBIDDEN,
    REFUSAL_STREAM_NAMESPACE_UNPROVEN,
    REFUSAL_TERMINAL_TAIL_UNCERTAIN,
    StreamNamespacePreflight,
    TemporalPreparationRecord,
    TerminalTailPreflight,
    assert_no_nominal_fps_derivation,
    assert_stream_namespace_separation,
    build_editorial_handoff_envelope,
    build_gate3_preparation_packet,
    build_temporal_preparation_record,
    evaluate_stream_namespace_preflight,
    evaluate_terminal_tail_preflight,
    refuse_authoritative_handoff_minting,
    refuse_non_human_or_unobserved_principal,
    verify_cross_stage_gate3_lineage,
    verify_editorial_handoff_envelope,
    verify_gate3_lineage_certificate,
    verify_gate3_preparation_packet,
    verify_temporal_preparation_record,
)


def _build_fixture_queue_and_chains() -> tuple[
    CandidateReviewQueue,
    list[TemporalRefinementRequest],
    list[PtsFixtureDiagnostic],
    dict[str, list[EditorialProposal]],
]:
    sha_dup = "a" * 64
    sha_unique = "b" * 64

    item_a = CandidateQueueItem.create(
        queue_item_id="qitem_001",
        candidate_id="cand_001",
        query_id="q_001",
        query_text="ballet pirouette en dehors",
        arm_id="siglip_v1_base",
        source_id="src_occ_001",
        source_revision_id="rev_001",
        source_sha256=sha_dup,
        source_path="synthetic://ballet/camera_a/clip_01.mp4",
        selected_stream_index=0,
        rank=1,
        score_millipoints=910,
        candidate_start_ticks=1000,
        candidate_end_ticks=3000,
        time_base="1/1000",
    )
    # Duplicate source_sha256 across distinct source_path + duplicate query_text with distinct query_id
    item_b = CandidateQueueItem.create(
        queue_item_id="qitem_002",
        candidate_id="cand_002",
        query_id="q_002",
        query_text="ballet pirouette en dehors",
        arm_id="siglip2_v2_base",
        source_id="src_occ_002",
        source_revision_id="rev_002",
        source_sha256=sha_dup,
        source_path="synthetic://ballet/backup_mirror/clip_01_copy.mp4",
        selected_stream_index=0,
        rank=1,
        score_millipoints=895,
        candidate_start_ticks=2000,
        candidate_end_ticks=4000,
        time_base="1/1000",
    )
    item_c = CandidateQueueItem.create(
        queue_item_id="qitem_003",
        candidate_id="cand_003",
        query_id="q_003",
        query_text="orchestra conductor downbeat",
        arm_id="siglip2_v2_so400m",
        source_id="src_occ_003",
        source_revision_id="rev_003",
        source_sha256=sha_unique,
        source_path="synthetic://music/pit/clip_02.mp4",
        selected_stream_index=0,
        rank=1,
        score_millipoints=940,
        candidate_start_ticks=1000,
        candidate_end_ticks=3000,
        time_base="1/1000",
    )

    queue = CandidateReviewQueue.create(
        queue_id="queue_mega15_001",
        batch_id="batch_mega15_001",
        items=(item_a, item_b, item_c),
    )
    verify_candidate_queue(queue)

    requests: list[TemporalRefinementRequest] = []
    diagnostics: list[PtsFixtureDiagnostic] = []
    proposal_chains: dict[str, list[EditorialProposal]] = {}

    pts_ticks = (0, 1000, 2000, 3000, 4000, 5000)

    for idx, item in enumerate(queue.items, start=1):
        req = build_temporal_refinement_request(
            request_id=f"treq_{idx:03d}",
            queue_item=item,
            producer_attempt_id=f"attempt_{idx:03d}",
        )
        diag = evaluate_pts_fixture_diagnostic(
            diagnostic_id=f"diag_{idx:03d}",
            request=req,
            pts_ticks=pts_ticks,
        )
        v1 = build_editorial_proposal(
            proposal_id=f"prop_{idx:03d}_v1",
            queue_item=item,
            refinement_request=req,
            pts_diagnostic=diag,
            proposed_action="INCLUDE_CANDIDATE_FOR_HUMAN_REVIEW",
            rationale="Initial v1 synthetic proposal for human review.",
        )
        v2 = advance_proposal_revision(
            prior_proposal=v1,
            new_proposal_id=f"prop_{idx:03d}_v2",
            proposed_action="REVISE_CANDIDATE_BOUNDARIES",
            proposed_start_ticks=diag.snapped_start_ticks,
            proposed_end_ticks=diag.snapped_end_ticks,
            rationale="Refined v2 synthetic boundary proposal.",
        )
        v3 = advance_proposal_revision(
            prior_proposal=v2,
            new_proposal_id=f"prop_{idx:03d}_v3",
            proposed_action="HOLD_FOR_ADDITIONAL_EVIDENCE",
            proposed_start_ticks=diag.snapped_start_ticks,
            proposed_end_ticks=diag.snapped_end_ticks,
            rationale="Final v3 pre-review hold awaiting real source measurement and human decision.",
        )
        requests.append(req)
        diagnostics.append(diag)
        proposal_chains[item.queue_item_id] = [v1, v2, v3]

    return queue, requests, diagnostics, proposal_chains


def test_mega15_valid_preparation_packet_and_lineage_certificate() -> None:
    queue, requests, diagnostics, proposal_chains = _build_fixture_queue_and_chains()

    temporal_records: list[TemporalPreparationRecord] = []
    for req, diag in zip(requests, diagnostics, strict=True):
        rec = build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=diag,
            stream_count=1,
        )
        verify_temporal_preparation_record(rec)
        assert rec.gate3_structurally_eligible is True
        assert rec.gate3_binding_eligible is False
        assert rec.source_pts_evidence_state == NOT_OBSERVED
        assert rec.exact_cut_eligible is False
        temporal_records.append(rec)

    packet = build_gate3_preparation_packet(
        packet_id="g3_prep_001",
        queue=queue,
        temporal_records=temporal_records,
        proposal_chains=proposal_chains,
    )
    verify_gate3_preparation_packet(packet)

    assert packet.real_human_decision_state == NOT_OBSERVED
    assert packet.source_pts_evidence_state == NOT_OBSERVED
    assert packet.source_native_exact_edit_eligible is False
    assert packet.authoritative_edit_plan_created is False
    assert packet.production_export_authorized is False
    assert len(packet.handoff_envelopes) == 3

    for env in packet.handoff_envelopes:
        verify_editorial_handoff_envelope(env)
        assert env.active_revision_number == 3
        assert len(env.revision_chain_digests) == 3
        assert env.real_human_decision_state == NOT_OBSERVED
        assert env.human_decision_artifact_minted is False
        assert env.authoritative_edit_plan_created is False
        assert env.source_native_exact_edit_eligible is False
        assert env.production_export_authorized is False

    # Round-trip JSON serialization
    reloaded_packet = Gate3PreparationPacket.from_dict(packet.to_dict())
    assert reloaded_packet.packet_digest == packet.packet_digest

    cert = verify_cross_stage_gate3_lineage(
        certificate_id="g3_lineage_001",
        queue=queue,
        refinement_requests=requests,
        pts_diagnostics=diagnostics,
        proposal_chains=proposal_chains,
        preparation_packet=packet,
    )
    verify_gate3_lineage_certificate(cert)
    assert cert.verified_item_count == 3
    assert cert.duplicate_occurrence_paths_preserved is True
    assert cert.duplicate_query_texts_preserved is True
    assert cert.revision_chains_verified is True
    assert cert.real_human_decision_state == NOT_OBSERVED
    assert cert.source_pts_evidence_state == NOT_OBSERVED
    assert cert.source_native_exact_edit_eligible is False
    assert cert.authoritative_edit_plan_created is False
    assert cert.production_export_authorized is False

    reloaded_cert = Gate3LineageCertificate.from_dict(cert.to_dict())
    assert reloaded_cert.certificate_digest == cert.certificate_digest


def test_mega15_gate3_binding_eligible_always_false_on_synthetic() -> None:
    queue, requests, diagnostics, _ = _build_fixture_queue_and_chains()
    rec = build_temporal_preparation_record(
        refinement_request=requests[0],
        pts_diagnostic=diagnostics[0],
    )
    # Direct check against gate3.refinement.is_binding_eligible
    assert is_binding_eligible(rec.to_dict()) is False
    assert rec.gate3_binding_eligible is False


def test_mega15_duplicate_pts_ambiguity_and_discontinuity_refusals() -> None:
    queue, requests, _, _ = _build_fixture_queue_and_chains()
    req = requests[0]

    # Duplicate presentation tick at 1000 makes start_ticks=1000 ambiguous without occurrence_index
    dup_diag = evaluate_pts_fixture_diagnostic(
        diagnostic_id="diag_dup",
        request=req,
        pts_ticks=(0, 1000, 1000, 2000, 3000, 4000),
    )
    with pytest.raises(VipLabError, match=REFUSAL_AMBIGUOUS_DUPLICATE_PTS):
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=dup_diag,
            occurrence_index=None,
        )

    # Supplying explicit occurrence_index resolves the ordinal for diagnostic preflight
    rec_resolved = build_temporal_preparation_record(
        refinement_request=req,
        pts_diagnostic=dup_diag,
        occurrence_index=0,
    )
    assert rec_resolved.exact_cut_eligible is False
    assert rec_resolved.gate3_binding_eligible is False

    # Discontinuity (non-monotonic jump backwards inside interval) refused by default
    disc_diag = evaluate_pts_fixture_diagnostic(
        diagnostic_id="diag_disc",
        request=req,
        pts_ticks=(0, 1000, 2500, 1800, 3000, 4000),
    )
    with pytest.raises(VipLabError, match=REFUSAL_PTS_DISCONTINUITY):
        build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=disc_diag,
            allow_discontinuity_subdivision=False,
        )

    # When diagnostic subdivision is permitted, segments are recorded but exact cut remains False
    rec_sub = build_temporal_preparation_record(
        refinement_request=req,
        pts_diagnostic=disc_diag,
        allow_discontinuity_subdivision=True,
    )
    assert rec_sub.discontinuity_detected is True
    assert len(rec_sub.subdivided_segments) >= 2
    assert REFUSAL_PTS_DISCONTINUITY in rec_sub.refusal_codes
    assert rec_sub.exact_cut_eligible is False


def test_mega15_nominal_fps_derivation_refused() -> None:
    with pytest.raises(VipLabError, match=REFUSAL_NOMINAL_FPS_FORBIDDEN):
        assert_no_nominal_fps_derivation({"nominal_fps": 29.97, "seconds": 12.5})

    with pytest.raises(VipLabError, match=REFUSAL_NOMINAL_FPS_FORBIDDEN):
        assert_no_nominal_fps_derivation({"derivation": "seconds * nominal_fps"})


def test_mega15_terminal_tail_it6_uncertainty_refusal() -> None:
    table = PtsTable(TimeBase(1, 1000), (0, 1000, 2000, 3000))
    # Requesting end at or beyond the final observed PTS tick triggers stream-tail uncertainty
    tail_preflight = evaluate_terminal_tail_preflight(
        pts_table=table,
        requested_end_ticks=3500,
        container_facts=None,
    )
    assert tail_preflight.end_is_stream_tail is True
    assert tail_preflight.tail_binding_eligible is False
    assert tail_preflight.it6_disposition_state == "PENDING_OWNER_DISPOSITION_P3_IN_FORCE"
    assert tail_preflight.refusal_code == REFUSAL_TERMINAL_TAIL_UNCERTAIN

    # Even with synthetic container_facts claiming MATCH, interim IT-6 P3 keeps pre-review tail_binding_eligible False
    tail_with_facts = evaluate_terminal_tail_preflight(
        pts_table=table,
        requested_end_ticks=4000,
        container_facts={"nb_frames": 4, "duration_ts": 4000, "duration_consistency": "MATCH"},
    )
    assert tail_with_facts.end_is_stream_tail is True
    assert tail_with_facts.tail_binding_eligible is False
    assert tail_with_facts.refusal_code == REFUSAL_TERMINAL_TAIL_UNCERTAIN


def test_mega15_stream_namespace_a7_separation_and_refusals() -> None:
    # Conflating selected_stream_index with tkhd.track_ID or claiming equivalence without byte-bound P2 proof fails
    with pytest.raises(VipLabError, match=REFUSAL_STREAM_NAMESPACE_UNPROVEN):
        assert_stream_namespace_separation(
            ffprobe_stream_index=0,
            iso_bmff_trak_ordinal=0,
            tkhd_track_id=1,
            probe_stream_id_hex="0x1",
            claim_equivalence_without_proof=True,
        )

    # Unusable tkhd.track_ID == 0 or 0xFFFFFFFF refused
    with pytest.raises(VipLabError, match=REFUSAL_STREAM_NAMESPACE_UNPROVEN):
        assert_stream_namespace_separation(
            ffprobe_stream_index=0,
            iso_bmff_trak_ordinal=0,
            tkhd_track_id=0,
            probe_stream_id_hex="0x0",
            claim_equivalence_without_proof=False,
        )

    with pytest.raises(VipLabError, match=REFUSAL_STREAM_NAMESPACE_UNPROVEN):
        assert_stream_namespace_separation(
            ffprobe_stream_index=0,
            iso_bmff_trak_ordinal=0,
            tkhd_track_id=0xFFFFFFFF,
            probe_stream_id_hex="0xffffffff",
            claim_equivalence_without_proof=False,
        )

    # Mismatched probe_stream_id_hex vs tkhd_track_id refused
    with pytest.raises(VipLabError, match=REFUSAL_STREAM_NAMESPACE_UNPROVEN):
        assert_stream_namespace_separation(
            ffprobe_stream_index=0,
            iso_bmff_trak_ordinal=0,
            tkhd_track_id=2,
            probe_stream_id_hex="0x1",
            claim_equivalence_without_proof=False,
        )

    # Multi-stream preflight records unproven namespace state and refusal code
    ns_preflight = evaluate_stream_namespace_preflight(
        source_revision_id="rev_001",
        source_sha256="a" * 64,
        ffprobe_stream_index=1,
        iso_bmff_trak_ordinal=1,
        tkhd_track_id=2,
        probe_stream_id_hex="0x2",
        stream_count=2,
    )
    assert ns_preflight.namespace_equivalence_proven is False
    assert ns_preflight.refusal_code == REFUSAL_STREAM_NAMESPACE_UNPROVEN


def test_mega15_editorial_principal_and_handoff_minting_refusals() -> None:
    # Model or tool principal rejected via gate3.editorial.ModelToolPrincipalError
    with pytest.raises((VipLabError, ModelToolPrincipalError)):
        refuse_non_human_or_unobserved_principal("model")

    with pytest.raises((VipLabError, ModelToolPrincipalError)):
        refuse_non_human_or_unobserved_principal("tool")

    # Claiming real human approval in synthetic lab mode is refused
    with pytest.raises(VipLabError, match=REFUSAL_HUMAN_DECISION_NOT_OBSERVED):
        refuse_non_human_or_unobserved_principal("human", claim_real_human_approval=True)

    # Attempting to mint HumanDecisionArtifact, ReviewBundle with MEASURED PTS, or authoritative EditPlanRevision fails
    with pytest.raises(VipLabError, match=REFUSAL_HUMAN_DECISION_NOT_OBSERVED):
        refuse_authoritative_handoff_minting({"artifact_kind": "HumanDecisionArtifact"})

    with pytest.raises(VipLabError, match=REFUSAL_REVIEW_BUNDLE_REAL_MEASURED_FORBIDDEN):
        refuse_authoritative_handoff_minting(
            {"artifact_kind": "ReviewBundle", "source_pts_evidence_state": "MEASURED"}
        )

    with pytest.raises(VipLabError, match=REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN):
        refuse_authoritative_handoff_minting(
            {"artifact_kind": "EditPlanRevision", "export_eligible": True}
        )


def test_mega15_lineage_rejects_stale_revision_and_tampering() -> None:
    queue, requests, diagnostics, proposal_chains = _build_fixture_queue_and_chains()
    temporal_records = [
        build_temporal_preparation_record(refinement_request=r, pts_diagnostic=d)
        for r, d in zip(requests, diagnostics, strict=True)
    ]
    packet = build_gate3_preparation_packet(
        packet_id="g3_prep_tamper",
        queue=queue,
        temporal_records=temporal_records,
        proposal_chains=proposal_chains,
    )

    # 1. Forged MEASURED source_pts_evidence_state on TemporalPreparationRecord is rejected
    tampered_rec_dict = temporal_records[0].to_dict()
    tampered_rec_dict["source_pts_evidence_state"] = "MEASURED"
    with pytest.raises(VipLabError, match=REFUSAL_FORGED_MEASURED_PTS):
        TemporalPreparationRecord.from_dict(tampered_rec_dict)

    # 2. Stale proposal revision (passing only [v1, v2] to packet while lineage expects [v1, v2, v3]) fails closed
    stale_chains = dict(proposal_chains)
    stale_chains["qitem_001"] = proposal_chains["qitem_001"][:2]
    stale_packet = build_gate3_preparation_packet(
        packet_id="g3_prep_stale",
        queue=queue,
        temporal_records=temporal_records,
        proposal_chains=stale_chains,
    )
    with pytest.raises(VipLabError, match="Stale or mismatched active proposal"):
        verify_cross_stage_gate3_lineage(
            certificate_id="g3_lineage_stale",
            queue=queue,
            refinement_requests=requests,
            pts_diagnostics=diagnostics,
            proposal_chains=proposal_chains,
            preparation_packet=stale_packet,
        )

    # 3. Source SHA mismatch between queue item and temporal record fails closed
    bad_item = CandidateQueueItem.create(
        queue_item_id="qitem_001",
        candidate_id="cand_001",
        query_id="q_001",
        query_text="ballet pirouette en dehors",
        arm_id="siglip_v1_base",
        source_id="src_occ_001",
        source_revision_id="rev_001",
        source_sha256="f" * 64,
        source_path="synthetic://ballet/camera_a/clip_01.mp4",
        selected_stream_index=0,
        rank=1,
        score_millipoints=910,
        candidate_start_ticks=1000,
        candidate_end_ticks=3000,
        time_base="1/1000",
    )
    with pytest.raises(VipLabError, match="source_sha256 mismatch"):
        build_editorial_handoff_envelope(
            queue_item=bad_item,
            temporal_record=temporal_records[0],
            proposal_chain=proposal_chains["qitem_001"],
        )

    # 4. Tampered packet digest fails verification
    tampered_packet_dict = packet.to_dict()
    tampered_packet_dict["packet_digest"] = "0" * 64
    with pytest.raises(VipLabError, match="digest mismatch"):
        Gate3PreparationPacket.from_dict(tampered_packet_dict)
