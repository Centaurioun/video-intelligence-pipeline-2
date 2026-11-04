"""Packet P07a: Gate-3 Candidate -> Source-Native Temporal Refinement Gate.

Reuses ``gate3.pts.PtsTable``, ``gate3.temporal.resolve_start``, ``resolve_end``,
``classify_vfr``, ``detect_discontinuity``, and ``gate3.rational.Rational``, ``TimeBase``
on synthetic numeric PTS tables.

Invariants enforced:
- Semantic retrieval candidates are ``MATCHED`` candidates in ``SEMANTIC_SECONDS``
  and are never ``MEASURED`` or frame-accurate cuts on their own.
- Deriving frame ordinals via ``seconds * nominal_fps`` is strictly forbidden.
- Non-monotonic or ambiguous PTS tables fail closed.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from gate3.pts import PtsTable
from gate3.rational import Rational, TimeBase
from gate3.temporal import (
    classify_vfr,
    detect_discontinuity,
    resolve_end,
    resolve_start,
)

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-07.CANDIDATE_TEMPORAL_GATE"


def _to_rational_seconds(val: Any, field_name: str) -> Rational:
    if isinstance(val, Mapping):
        num = val.get("num")
        den = val.get("den")
        if (
            not isinstance(num, int)
            or isinstance(num, bool)
            or not isinstance(den, int)
            or isinstance(den, bool)
            or den <= 0
        ):
            raise VipLabError(
                "TEMPORAL_RATIONAL_INVALID",
                f"{field_name} rational mapping requires integer num and positive integer den",
                field_path=field_name,
            )
        return Rational(num, den)
    if isinstance(val, int) and not isinstance(val, bool):
        return Rational(val, 1)
    if isinstance(val, float):
        # Convert exact millisecond integer representation only for synthetic convenience
        millis = round(val * 1000)
        return Rational(millis, 1000)
    raise VipLabError(
        "TEMPORAL_COORDINATE_INVALID",
        f"Unsupported coordinate value at {field_name}: {val!r}",
        field_path=field_name,
    )


def inspect_candidate_temporal(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Inspect a retrieval candidate and optional synthetic PTS table for temporal refinement."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "CANDIDATE_TEMPORAL_NOT_MAPPING",
            "payload must be a mapping",
        )

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
                message="Untrusted self-declared authority flags in temporal payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if (
        cleaned.get("derivation_method") == "SECONDS_TIMES_NOMINAL_FPS"
        or bool(cleaned.get("nominal_fps_derived", False))
    ):
        code = "VFR_NOMINAL_FPS_MULTIPLICATION_FORBIDDEN"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Deriving frame positions via seconds * nominal_fps is forbidden",
                field_path="derivation_method",
            )
        )

    candidate = cleaned.get("candidate")
    if not isinstance(candidate, Mapping):
        code = "CANDIDATE_MAPPING_MISSING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="candidate mapping is required",
                field_path="candidate",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"binding_eligible": False},
        )

    cand_ev_class = str(candidate.get("evidence_class", "MATCHED"))
    if cand_ev_class != "MATCHED" or bool(candidate.get("frame_accurate", False)):
        code = "CANDIDATE_SEMANTIC_NOT_FRAME_ACCURATE"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=(
                    "Semantic retrieval candidates must have evidence_class='MATCHED' "
                    "and frame_accurate=False"
                ),
                field_path="candidate",
            )
        )

    pts_ticks_raw = cleaned.get("pts_ticks")
    tb_raw = cleaned.get("time_base", {"num": 1, "den": 90000})
    if pts_ticks_raw is None:
        code = "SOURCE_PTS_TABLE_MISSING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Semantic candidate cannot be temporally refined without a source PTS table",
                field_path="pts_ticks",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "candidate_evidence_class": cand_ev_class,
                "temporal_refined": False,
                "binding_eligible": False,
            },
        )

    if (
        not isinstance(pts_ticks_raw, Sequence)
        or len(pts_ticks_raw) < 2
        or any(not isinstance(t, int) or isinstance(t, bool) for t in pts_ticks_raw)
    ):
        code = "PTS_TABLE_INVALID_SEQUENCE"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="pts_ticks must be a sequence of at least 2 integers",
                field_path="pts_ticks",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"temporal_refined": False, "binding_eligible": False},
        )

    try:
        tb_rat = _to_rational_seconds(tb_raw, "time_base")
        tb = TimeBase(tb_rat.num, tb_rat.den)
        start_sec = _to_rational_seconds(
            candidate.get("start_sec", 0), "candidate.start_sec"
        )
        end_sec = _to_rational_seconds(
            candidate.get("end_sec", 1), "candidate.end_sec"
        )
    except (VipLabError, ValueError) as exc:
        code = exc.code if isinstance(exc, VipLabError) else "TEMPORAL_TIMEBASE_INVALID"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=str(exc),
                field_path="time_base",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"temporal_refined": False, "binding_eligible": False},
        )

    table = PtsTable(tuple(int(t) for t in pts_ticks_raw))
    if table.is_ambiguous:
        code = "PTS_TABLE_NON_MONOTONIC_OR_AMBIGUOUS"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="PTS table is non-monotonic or contains duplicate ticks; failing closed",
                field_path="pts_ticks",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "pts_ambiguous": True,
                "temporal_refined": False,
                "binding_eligible": False,
            },
        )

    # Convert requested start/end seconds to target ticks using exact rational arithmetic
    req_start_ratio = start_sec / tb.rational
    req_end_ratio = end_sec / tb.rational
    req_start_tick = req_start_ratio.num // req_start_ratio.den
    req_end_tick = req_end_ratio.num // req_end_ratio.den

    snap_start = resolve_start(table, req_start_tick)
    snap_end = resolve_end(table, req_end_tick)
    if (
        not snap_start.resolved
        or not snap_end.resolved
        or snap_start.resolved_tick is None
        or snap_end.resolved_tick is None
        or snap_end.resolved_tick <= snap_start.resolved_tick
    ):
        code = "TEMPORAL_BOUNDARY_RESOLUTION_FAILED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Requested candidate window could not be resolved to valid start/end PTS ticks",
                field_path="candidate",
                details={
                    "start_reason": snap_start.reason_code,
                    "end_reason": snap_end.reason_code,
                },
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"temporal_refined": False, "binding_eligible": False},
        )

    vfr_info = classify_vfr(table)
    disc_gap = int(cleaned.get("max_delta_ticks", 90000))
    discontinuities = detect_discontinuity(table, disc_gap)
    start_ord = table.ordinal_of(snap_start.resolved_tick)
    end_ord = table.ordinal_of(snap_end.resolved_tick)

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("SYNTHETIC_PTS_REFINEMENT_COMPUTED")
        reasons.append("HUMAN_EDITORIAL_DECISION_REQUIRED_FOR_PLAN")
        findings.append(
            ReadinessFinding(
                code="SYNTHETIC_PTS_INTERVAL_RESOLVED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Resolved candidate seconds to synthetic PTS ticks and frame ordinals",
                evidence_state="MEASURED",
                details={
                    "start_pts": snap_start.resolved_tick,
                    "end_pts": snap_end.resolved_tick,
                    "start_frame_ordinal": start_ord,
                    "end_frame_ordinal": end_ord,
                    "is_vfr": vfr_info.is_vfr,
                },
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        evidence_state="MEASURED" if final_status == ReadinessStatus.READY_SYNTHETIC else NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "candidate_evidence_class": "MATCHED",
            "refinement_evidence_class": "MEASURED",
            "temporal_refined": final_status == ReadinessStatus.READY_SYNTHETIC,
            "binding_eligible": False,
            "start_pts": snap_start.resolved_tick,
            "end_pts": snap_end.resolved_tick,
            "start_frame_ordinal": start_ord,
            "end_frame_ordinal": end_ord,
            "is_vfr": vfr_info.is_vfr,
            "min_delta_ticks": vfr_info.min_delta,
            "max_delta_ticks": vfr_info.max_delta,
            "discontinuity_count": len(discontinuities),
        },
    )
