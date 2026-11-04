"""MEGA-10 Regression Tests: Candidate Temporal Request & Source-Native PTS Diagnostic (Packet P10).

Covers:
1. Construction of ``TemporalRefinementRequest`` from a MEGA-09 ``CandidateQueueItem``
   with ``measurement_needed=True``, ``source_pts_evidence_state="NOT_OBSERVED"``,
   ``binding_eligible=False``, and ``refinement_status="SYNTHETIC_DIAGNOSTIC_ONLY"``.
2. Exact rational PTS table diagnostics using ``gate3.pts.PtsTable``,
   ``gate3.temporal.resolve_start`` (``first_pts_at_or_after``),
   ``gate3.temporal.resolve_end`` (``first_pts_strictly_after``, half-open ``[start, end)``),
   ``gate3.temporal.classify_vfr``, and ``gate3.temporal.detect_discontinuity``.
3. Fail-closed refusal of:
   - ``seconds * nominal_fps`` frame derivation
   - promoting a candidate timestamp directly to an edit boundary or ``MEASURED`` state
   - duplicate PTS tick resolution without an explicit ``occurrence`` ordinal
   - non-monotonic PTS sequences
   - conflating FFprobe global stream index with ISO-BMFF ``tkhd.track_ID`` (A-7 boundary).
"""

from __future__ import annotations

import pytest

from vip_fvs.synthetic_profiles import V1_PROFILE_ID
from vip_fvs.three_arm_batch import ARM_VIP_V1_BASE
from vip_lab.common import NOT_OBSERVED, ReadinessStatus, VipLabError
from vip_lab.mega09 import CandidateQueueItem
from vip_lab.mega10 import (
    TEMPORAL_REQUEST_SCHEMA_VERSION,
    PtsFixtureDiagnostic,
    TemporalRefinementRequest,
    build_temporal_refinement_request,
    evaluate_pts_fixture_diagnostic,
    inspect_temporal_measurement_boundary,
    verify_temporal_refinement_request,
)


def _sample_queue_item() -> CandidateQueueItem:
    return CandidateQueueItem(
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
        query_text="adagio arabesque",
        rank=1,
        score=0.91,
        revision_id="rev-01",
        content_id="cnt-01",
        source_path="/synthetic/archive/adagio.mp4",
        source_sha256="4" * 64,
        source_sample_pts=3003,
        source_timebase_num=1001,
        source_timebase_den=30000,
        timestamp_human="00:00:00.100",
    )


def test_build_temporal_refinement_request_maintains_nonbinding_not_observed_state() -> None:
    item = _sample_queue_item()
    req = build_temporal_refinement_request(
        item,
        upstream_queue_digest="5" * 64,
        selected_stream_index=0,
        requested_start_pts=3003,
        requested_end_pts=6006,
        pts_ticks=(0, 1001, 2002, 3003, 4004, 5005, 6006, 7007),
    )

    assert isinstance(req, TemporalRefinementRequest)
    assert req.schema_version == TEMPORAL_REQUEST_SCHEMA_VERSION
    assert req.measurement_needed is True
    assert req.source_pts_evidence_state == NOT_OBSERVED
    assert req.candidate_evidence_class == "MATCHED"
    assert req.binding_eligible is False
    assert req.refinement_status == "SYNTHETIC_DIAGNOSTIC_ONLY"
    assert req.synthetic_pts_diagnostic is not None
    assert req.synthetic_pts_diagnostic.resolved_start_ticks == 3003
    # resolve_end uses first_pts_strictly_after(6006) -> 7007 for half-open [start, end)
    assert req.synthetic_pts_diagnostic.resolved_end_ticks == 7007
    assert req.synthetic_pts_diagnostic.endpoint_semantics == "half_open"
    assert req.synthetic_pts_diagnostic.is_vfr == "false"
    assert req.synthetic_pts_diagnostic.authoritative_source_measurement is False

    verified = verify_temporal_refinement_request(req.to_dict())
    assert verified["request_digest"] == req.request_digest


def test_pts_fixture_diagnostic_detects_vfr_and_discontinuity() -> None:
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=1,
        timebase_den=1000,
        pts_ticks=(0, 40, 80, 120, 500, 540, 580),
        requested_start_pts=35,
        requested_end_pts=540,
        declared_rate_num=25,
        declared_rate_den=1,
    )
    assert isinstance(diag, PtsFixtureDiagnostic)
    assert diag.resolved_start_ticks == 40
    assert diag.resolved_end_ticks == 580
    assert diag.is_vfr == "true"
    assert diag.discontinuity_gaps == ((120, 500),)
    assert len(diag.subdivided_parts) == 2
    assert diag.diagnostic_only is True
    assert diag.authoritative_source_measurement is False


def test_duplicate_pts_without_occurrence_is_refused_fail_closed() -> None:
    with pytest.raises(VipLabError) as exc_info:
        evaluate_pts_fixture_diagnostic(
            timebase_num=1001,
            timebase_den=30000,
            pts_ticks=(0, 1001, 2002, 2002, 3003, 4004),
            requested_start_pts=2002,
            requested_end_pts=3003,
            start_occurrence=None,
        )
    assert exc_info.value.code == "DUPLICATE_PTS_AMBIGUOUS_WITHOUT_OCCURRENCE"

    # Providing explicit start_occurrence=1 resolves the second retained ordinal cleanly
    diag = evaluate_pts_fixture_diagnostic(
        timebase_num=1001,
        timebase_den=30000,
        pts_ticks=(0, 1001, 2002, 2002, 3003, 4004),
        requested_start_pts=2002,
        requested_end_pts=3003,
        start_occurrence=1,
    )
    assert diag.start_ordinal == 3


def test_nonmonotonic_pts_sequence_is_refused() -> None:
    with pytest.raises(VipLabError) as exc_info:
        evaluate_pts_fixture_diagnostic(
            timebase_num=1,
            timebase_den=90000,
            pts_ticks=(0, 3000, 1500, 6000),
            requested_start_pts=0,
            requested_end_pts=3000,
        )
    assert exc_info.value.code == "PTS_TABLE_NON_MONOTONIC_OR_INVALID"


def test_nominal_fps_derivation_and_stream_conflation_are_refused() -> None:
    item = _sample_queue_item()
    pkt_fps = inspect_temporal_measurement_boundary(
        {
            "queue_item": item.to_dict(),
            "upstream_queue_digest": "5" * 64,
            "derive_from_nominal_fps": True,
            "nominal_fps": 29.97,
        }
    )
    assert pkt_fps.status == ReadinessStatus.BLOCKED
    assert "NOMINAL_FPS_FRAME_DERIVATION_FORBIDDEN" in pkt_fps.blockers

    pkt_stream = inspect_temporal_measurement_boundary(
        {
            "queue_item": item.to_dict(),
            "upstream_queue_digest": "5" * 64,
            "conflate_ffprobe_index_with_iso_track_id": True,
            "selected_stream_index": 1,
            "iso_track_id": 2,
        }
    )
    assert pkt_stream.status == ReadinessStatus.BLOCKED
    assert "A7_STREAM_NAMESPACE_UNPROVEN_REFUSED" in pkt_stream.blockers


def test_direct_promotion_of_candidate_to_measured_or_binding_is_refused() -> None:
    item = _sample_queue_item()
    pkt = inspect_temporal_measurement_boundary(
        {
            "queue_item": item.to_dict(),
            "upstream_queue_digest": "5" * 64,
            "promote_candidate_to_edit_boundary": True,
            "claim_measured_authority": True,
        }
    )
    assert pkt.status == ReadinessStatus.BLOCKED
    assert "CANDIDATE_TIMESTAMP_NOT_EDIT_BOUNDARY" in pkt.blockers
    assert "SYNTHETIC_TEMPORAL_CANNOT_CLAIM_MEASURED" in pkt.blockers
