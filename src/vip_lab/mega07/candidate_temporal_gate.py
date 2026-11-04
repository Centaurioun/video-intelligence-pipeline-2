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
        num = val.get("num", val.get("numerator"))
        den = val.get("den", val.get("denominator"))
        if (
            not isinstance(num, int)
            or isinstance(num, bool)
            or not isinstance(den, int)
            or isinstance(den, bool)
            or den <= 0
        ):
            raise VipLabError(
                "TEMPORAL_RATIONAL_INVALID",
                f"{field_name} rational mapping requires integer num/numerator and positive integer den/denominator",
                field_path=field_name,
            )
        return Rational(num, den)
    if isinstance(val, int) and not isinstance(val, bool):
        return Rational(val, 1)
    if isinstance(val, float):
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
                "refinement_status": "SYNTHETIC_DIAGNOSTIC_ONLY",
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
        tb = TimeBase(tb_rat.numerator, tb_rat.denominator)
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

    ticks_tuple = tuple(int(t) for t in pts_ticks_raw)
    try:
        table = PtsTable(tb, ticks_tuple)
    except ValueError as exc:
        code = "PTS_TABLE_NON_MONOTONIC_OR_AMBIGUOUS"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=f"PTS table rejected by PtsTable: {exc}",
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

    if any(table.is_ambiguous(t) for t in table.ticks):
        code = "PTS_TABLE_NON_MONOTONIC_OR_AMBIGUOUS"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="PTS table contains duplicate/ambiguous ticks; failing closed",
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
    req_start_tick = tb.seconds_to_ticks_floor(start_sec)
    req_end_tick = tb.seconds_to_ticks_floor(end_sec)

    snap_start = resolve_start(table, req_start_tick)
    snap_end = resolve_end(table, req_end_tick)
    if (
        snap_start.resolved_ticks is None
        or snap_end.resolved_ticks is None
        or snap_end.resolved_ticks <= snap_start.resolved_ticks
        or table.is_ambiguous(snap_start.resolved_ticks)
        or table.is_ambiguous(snap_end.resolved_ticks)
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
                    "start_policy": snap_start.policy,
                    "end_policy": snap_end.policy,
                    "resolved_start_ticks": snap_start.resolved_ticks,
                    "resolved_end_ticks": snap_end.resolved_ticks,
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

    resolved_start = snap_start.resolved_ticks
    resolved_end = snap_end.resolved_ticks
    vfr_str, _period, vfr_basis, _vfr_dev = classify_vfr(table)
    is_vfr = vfr_str == "true"
    deltas = [b - a for a, b in zip(table.ticks, table.ticks[1:])]
    min_delta = min(deltas) if deltas else 0
    max_delta = max(deltas) if deltas else 0
    discontinuities = detect_discontinuity(table, resolved_start, resolved_end)
    if discontinuities:
        code = "PTS_DISCONTINUITY_DETECTED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=f"PTS discontinuity detected in interval [{resolved_start}, {resolved_end})",
                field_path="pts_ticks",
                details={"discontinuities": [list(pair) for pair in discontinuities]},
            )
        )

    start_ord = table.ordinals_of(resolved_start)[0]
    end_ord = table.ordinals_of(resolved_end)[0]

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
                message="Resolved candidate seconds to synthetic PTS ticks and frame ordinals (diagnostic only)",
                evidence_state=NOT_OBSERVED,
                details={
                    "start_pts": resolved_start,
                    "end_pts": resolved_end,
                    "start_frame_ordinal": start_ord,
                    "end_frame_ordinal": end_ord,
                    "is_vfr": is_vfr,
                    "refinement_status": "SYNTHETIC_DIAGNOSTIC_ONLY",
                },
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "candidate_evidence_class": "MATCHED",
            "refinement_status": "SYNTHETIC_DIAGNOSTIC_ONLY",
            "refinement_evidence_state": NOT_OBSERVED,
            "temporal_refined": final_status == ReadinessStatus.READY_SYNTHETIC,
            "binding_eligible": False,
            "start_pts": resolved_start,
            "end_pts": resolved_end,
            "start_frame_ordinal": start_ord,
            "end_frame_ordinal": end_ord,
            "start_snap_policy": snap_start.policy,
            "end_snap_policy": snap_end.policy,
            "is_vfr": is_vfr,
            "vfr_classification": vfr_str,
            "vfr_basis": vfr_basis,
            "min_delta_ticks": min_delta,
            "max_delta_ticks": max_delta,
            "discontinuity_count": len(discontinuities),
        },
    )
