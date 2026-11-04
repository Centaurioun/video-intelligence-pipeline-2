"""Synthetic PTS table diagnostics over Gate-3 exact rational primitives for MEGA-10.

Packet P10 — Candidate Temporal Request & Source-Native Diagnostic (`LAB-MEGA-08-14-v1.0.0`).

Delegates directly to:
- ``gate3.pts.PtsTable``
- ``gate3.rational.Rational``, ``TimeBase``
- ``gate3.temporal.resolve_start``, ``resolve_end``, ``classify_vfr``,
  ``detect_discontinuity``, ``subdivide_on_discontinuity``
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from gate3.pts import PtsTable
from gate3.rational import Rational, TimeBase
from gate3.temporal import (
    classify_vfr,
    detect_discontinuity,
    resolve_end,
    resolve_start,
    subdivide_on_discontinuity,
)

from ..common import VipLabError


@dataclass(frozen=True)
class PtsFixtureDiagnostic:
    """Non-authoritative synthetic PTS table diagnostic result."""

    timebase_num: int
    timebase_den: int
    pts_ticks: tuple[int, ...]
    requested_start_pts: int
    requested_end_pts: int
    resolved_start_ticks: int
    resolved_end_ticks: int
    start_policy: str
    end_policy: str
    start_ordinal: int
    end_ordinal: int
    endpoint_semantics: str
    is_vfr: str
    vfr_period_rational: str | None
    vfr_basis: str
    vfr_deviation: Mapping[str, Any] | None
    discontinuity_gaps: tuple[tuple[int, int], ...]
    subdivided_parts: tuple[tuple[int, int], ...]
    diagnostic_only: bool = True
    authoritative_source_measurement: bool = False

    def __post_init__(self) -> None:
        if self.endpoint_semantics != "half_open":
            raise VipLabError(
                "PTS_DIAGNOSTIC_ENDPOINT_SEMANTICS_INVALID",
                "endpoint_semantics must be 'half_open'",
            )
        if self.resolved_end_ticks <= self.resolved_start_ticks:
            raise VipLabError(
                "PTS_DIAGNOSTIC_DEGENERATE_INTERVAL",
                "resolved_end_ticks must be strictly greater than resolved_start_ticks",
            )
        if self.diagnostic_only is not True or self.authoritative_source_measurement is not False:
            raise VipLabError(
                "PTS_DIAGNOSTIC_AUTHORITY_VIOLATION",
                "PtsFixtureDiagnostic is diagnostic_only=True and never authoritative",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "timebase_num": self.timebase_num,
            "timebase_den": self.timebase_den,
            "pts_ticks": list(self.pts_ticks),
            "requested_start_pts": self.requested_start_pts,
            "requested_end_pts": self.requested_end_pts,
            "resolved_start_ticks": self.resolved_start_ticks,
            "resolved_end_ticks": self.resolved_end_ticks,
            "start_policy": self.start_policy,
            "end_policy": self.end_policy,
            "start_ordinal": self.start_ordinal,
            "end_ordinal": self.end_ordinal,
            "endpoint_semantics": self.endpoint_semantics,
            "is_vfr": self.is_vfr,
            "vfr_period_rational": self.vfr_period_rational,
            "vfr_basis": self.vfr_basis,
            "vfr_deviation": dict(self.vfr_deviation) if self.vfr_deviation else None,
            "discontinuity_gaps": [[a, b] for a, b in self.discontinuity_gaps],
            "subdivided_parts": [[a, b] for a, b in self.subdivided_parts],
            "diagnostic_only": self.diagnostic_only,
            "authoritative_source_measurement": self.authoritative_source_measurement,
        }


def evaluate_pts_fixture_diagnostic(
    *,
    timebase_num: int,
    timebase_den: int,
    pts_ticks: Sequence[int],
    requested_start_pts: int,
    requested_end_pts: int,
    start_occurrence: int | None = None,
    end_occurrence: int | None = None,
    declared_rate_num: int | None = None,
    declared_rate_den: int | None = None,
) -> PtsFixtureDiagnostic:
    """Evaluate a synthetic PTS sequence with Gate-3 rational/PTS primitives."""
    if (
        type(timebase_num) is not int
        or type(timebase_den) is not int
        or timebase_num <= 0
        or timebase_den <= 0
    ):
        raise VipLabError(
            "PTS_DIAGNOSTIC_TIMEBASE_INVALID",
            "timebase_num and timebase_den must be positive integers",
        )
    if (
        type(requested_start_pts) is not int
        or type(requested_end_pts) is not int
        or requested_end_pts < requested_start_pts
    ):
        raise VipLabError(
            "PTS_DIAGNOSTIC_REQUEST_BOUNDS_INVALID",
            "requested_start_pts and requested_end_pts must be integers with start <= end",
        )

    tb = TimeBase(timebase_num, timebase_den)
    try:
        ticks_tuple = tuple(pts_ticks)
        table = PtsTable(tb, ticks_tuple)
    except (ValueError, TypeError) as exc:
        raise VipLabError(
            "PTS_TABLE_NON_MONOTONIC_OR_INVALID",
            f"Invalid PTS table: {exc}",
        ) from exc

    start_snap = resolve_start(table, requested_start_pts)
    end_snap = resolve_end(table, requested_end_pts)
    if start_snap.resolved_ticks is None or end_snap.resolved_ticks is None:
        raise VipLabError(
            "PTS_SNAP_OUT_OF_RANGE",
            "Requested start or end tick could not be snapped within PtsTable",
        )
    if end_snap.resolved_ticks <= start_snap.resolved_ticks:
        raise VipLabError(
            "PTS_SNAP_DEGENERATE_INTERVAL",
            "Snapped half-open interval has resolved_end_ticks <= resolved_start_ticks",
        )

    if table.is_ambiguous(start_snap.resolved_ticks) and start_occurrence is None:
        raise VipLabError(
            "DUPLICATE_PTS_AMBIGUOUS_WITHOUT_OCCURRENCE",
            f"Start tick {start_snap.resolved_ticks} is retained multiple times; explicit start_occurrence required",
        )
    if table.is_ambiguous(end_snap.resolved_ticks) and end_occurrence is None:
        raise VipLabError(
            "DUPLICATE_PTS_AMBIGUOUS_WITHOUT_OCCURRENCE",
            f"End tick {end_snap.resolved_ticks} is retained multiple times; explicit end_occurrence required",
        )

    start_ord = table.ordinal_of(start_snap.resolved_ticks, occurrence=start_occurrence)
    end_ord = table.ordinal_of(end_snap.resolved_ticks, occurrence=end_occurrence)
    if start_ord is None or end_ord is None or end_ord <= start_ord:
        raise VipLabError(
            "PTS_ORDINAL_RESOLUTION_FAILED",
            "Could not resolve valid increasing start and end ordinals in PtsTable",
        )

    declared_rate: Rational | None = None
    if declared_rate_num is not None and declared_rate_den is not None:
        if (
            type(declared_rate_num) is not int
            or type(declared_rate_den) is not int
            or declared_rate_num <= 0
            or declared_rate_den <= 0
        ):
            raise VipLabError(
                "PTS_DECLARED_RATE_INVALID",
                "declared_rate_num and declared_rate_den must be positive integers",
            )
        declared_rate = Rational(declared_rate_num, declared_rate_den)

    is_vfr_flag, period_rat, basis, deviation = classify_vfr(table, declared_rate=declared_rate)
    period_str = (
        f"{period_rat.numerator}/{period_rat.denominator}"
        if isinstance(period_rat, Rational)
        else None
    )
    gaps = tuple(
        (int(a), int(b))
        for a, b in detect_discontinuity(table, start_snap.resolved_ticks, end_snap.resolved_ticks)
    )
    parts, _ = subdivide_on_discontinuity(
        table, start_snap.resolved_ticks, end_snap.resolved_ticks
    )
    parts_tuple = tuple((int(a), int(b)) for a, b in parts)

    return PtsFixtureDiagnostic(
        timebase_num=timebase_num,
        timebase_den=timebase_den,
        pts_ticks=ticks_tuple,
        requested_start_pts=requested_start_pts,
        requested_end_pts=requested_end_pts,
        resolved_start_ticks=start_snap.resolved_ticks,
        resolved_end_ticks=end_snap.resolved_ticks,
        start_policy=start_snap.policy,
        end_policy=end_snap.policy,
        start_ordinal=start_ord,
        end_ordinal=end_ord,
        endpoint_semantics="half_open",
        is_vfr=str(is_vfr_flag),
        vfr_period_rational=period_str,
        vfr_basis=str(basis),
        vfr_deviation=deviation,
        discontinuity_gaps=gaps,
        subdivided_parts=parts_tuple,
        diagnostic_only=True,
        authoritative_source_measurement=False,
    )
