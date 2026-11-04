"""Temporal measurement boundary preflight evaluator for MEGA-10.

Packet P10 — Candidate Temporal Request & Source-Native Diagnostic (`LAB-MEGA-08-14-v1.0.0`).
"""

from __future__ import annotations

from typing import Any, Mapping

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)
from ..mega09.candidate_queue import CandidateQueueItem
from .temporal_request import build_temporal_refinement_request


STAGE_ID = "MEGA-10.TEMPORAL_MEASUREMENT_BOUNDARY"


def _item_from_mapping(raw: Mapping[str, Any]) -> CandidateQueueItem:
    return CandidateQueueItem(
        queue_item_id=str(raw.get("queue_item_id", "")),
        queue_index=int(raw.get("queue_index", 0)),
        arm_id=str(raw.get("arm_id", "")),
        profile_id=str(raw.get("profile_id", "")),
        model_identity=str(raw.get("model_identity", "")),
        space_id=str(raw.get("space_id", "")),
        generation_id=str(raw.get("generation_id", "")),
        catalog_id=str(raw.get("catalog_id", "")),
        catalog_digest=str(raw.get("catalog_digest", "")),
        manifest_digest=str(raw.get("manifest_digest", "")),
        query_id=str(raw.get("query_id", "")),
        query_text=str(raw.get("query_text", "")),
        rank=int(raw.get("rank", 1)),
        score=float(raw.get("score", 0.0)),
        revision_id=str(raw.get("revision_id", "")),
        content_id=str(raw.get("content_id", "")),
        source_path=str(raw.get("source_path", "")),
        source_sha256=str(raw.get("source_sha256", "")),
        source_sample_pts=int(raw.get("source_sample_pts", 0)),
        source_timebase_num=int(raw.get("source_timebase_num", 1)),
        source_timebase_den=int(raw.get("source_timebase_den", 1)),
        timestamp_human=str(raw.get("timestamp_human", "00:00:00.000")),
        thumbnail_path=raw.get("thumbnail_path"),
        thumbnail_status=str(raw.get("thumbnail_status", "MISSING")),
        evidence_class=str(raw.get("evidence_class", "MATCHED")),
        binding_eligible=bool(raw.get("binding_eligible", False)),
        review_state=str(raw.get("review_state", "NOT_REVIEWED")),
        human_decision_state=str(raw.get("human_decision_state", NOT_OBSERVED)),
        synthetic_only=bool(raw.get("synthetic_only", True)),
        authentic_model_evidence=bool(raw.get("authentic_model_evidence", False)),
    )


def inspect_temporal_measurement_boundary(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Validate candidate-to-temporal request boundaries and synthetic PTS diagnostics."""
    if not isinstance(payload, Mapping):
        raise VipLabError("TEMPORAL_BOUNDARY_NOT_MAPPING", "payload must be a mapping")

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="TEMPORAL_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted authority flags were stripped in MEGA-10 boundary check",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(cleaned.get("derive_from_nominal_fps", False)) or "nominal_fps" in cleaned:
        code = "NOMINAL_FPS_FRAME_DERIVATION_FORBIDDEN"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Frame derivation via seconds * nominal_fps is strictly forbidden",
                field_path="nominal_fps",
            )
        )

    if bool(cleaned.get("conflate_ffprobe_index_with_iso_track_id", False)) or (
        "iso_track_id" in cleaned
        and cleaned.get("selected_stream_index") is not None
        and cleaned.get("iso_track_id") != cleaned.get("selected_stream_index")
    ):
        code = "A7_STREAM_NAMESPACE_UNPROVEN_REFUSED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=(
                    "FFprobe global stream index and ISO-BMFF tkhd.track_ID remain distinct "
                    "namespaces; positive mapping is PENDING under Gate-3 A-7"
                ),
                field_path="iso_track_id",
            )
        )

    if bool(cleaned.get("promote_candidate_to_edit_boundary", False)):
        code = "CANDIDATE_TIMESTAMP_NOT_EDIT_BOUNDARY"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Semantic candidate sample PTS is not a frame-accurate edit boundary",
                field_path="promote_candidate_to_edit_boundary",
            )
        )

    if (
        bool(cleaned.get("claim_measured_authority", False))
        or cleaned.get("source_pts_evidence_state") == "MEASURED"
    ):
        code = "SYNTHETIC_TEMPORAL_CANNOT_CLAIM_MEASURED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Synthetic laboratory temporal request cannot claim MEASURED source-byte authority",
                field_path="claim_measured_authority",
            )
        )

    raw_item = cleaned.get("queue_item")
    upstream_digest = str(cleaned.get("upstream_queue_digest", ""))
    if not isinstance(raw_item, Mapping):
        code = "TEMPORAL_QUEUE_ITEM_MISSING"
        reasons.append(code)
        blockers.append(code)
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"request_valid": False, "binding_eligible": False},
        )

    try:
        item = _item_from_mapping(raw_item)
        pts_ticks = cleaned.get("pts_ticks")
        ticks_seq = tuple(int(t) for t in pts_ticks) if isinstance(pts_ticks, (list, tuple)) else None
        req = build_temporal_refinement_request(
            item,
            upstream_queue_digest=upstream_digest,
            selected_stream_index=int(cleaned.get("selected_stream_index", 0)),
            requested_start_pts=cleaned.get("requested_start_pts"),
            requested_end_pts=cleaned.get("requested_end_pts"),
            pts_ticks=ticks_seq,
            start_occurrence=cleaned.get("start_occurrence"),
            end_occurrence=cleaned.get("end_occurrence"),
            declared_rate_num=cleaned.get("declared_rate_num"),
            declared_rate_den=cleaned.get("declared_rate_den"),
        )
    except (VipLabError, ValueError, TypeError) as exc:
        code = exc.code if isinstance(exc, VipLabError) else "TEMPORAL_REQUEST_BUILD_FAILED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=str(exc),
                field_path="queue_item",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"request_valid": False, "binding_eligible": False},
        )

    if blockers:
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "request_valid": False,
                "binding_eligible": False,
                "refinement_status": "SYNTHETIC_DIAGNOSTIC_ONLY",
                "source_pts_evidence_state": NOT_OBSERVED,
            },
        )

    reasons.append("TEMPORAL_REFINEMENT_REQUEST_SYNTHETIC_READY")
    findings.append(
        ReadinessFinding(
            code="TEMPORAL_NONBINDING_DIAGNOSTIC_VERIFIED",
            status=ReadinessStatus.READY_SYNTHETIC,
            message="Temporal refinement request verified with measurement_needed=True and binding_eligible=False",
            evidence_state=NOT_OBSERVED,
            details={
                "request_id": req.request_id,
                "request_digest": req.request_digest,
            },
        )
    )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=ReadinessStatus.READY_SYNTHETIC,
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=(),
        findings=tuple(findings),
        summary={
            "request_valid": True,
            "request_id": req.request_id,
            "request_digest": req.request_digest,
            "measurement_needed": True,
            "source_pts_evidence_state": NOT_OBSERVED,
            "binding_eligible": False,
            "refinement_status": "SYNTHETIC_DIAGNOSTIC_ONLY",
            "temporal_request": req.to_dict(),
        },
    )
