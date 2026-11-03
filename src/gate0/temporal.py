"""Exact rational windowing and presentation-order target sampling."""
from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Iterable, Sequence

from gate0.adapters.decoder import DecodedFrame
from gate0.inventory import RevisionRef


@dataclass(frozen=True, order=True)
class Rational:
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if not isinstance(self.numerator, int) or not isinstance(self.denominator, int) or self.denominator <= 0:
            raise ValueError("rational denominator must be positive")
        divisor = gcd(abs(self.numerator), self.denominator)
        object.__setattr__(self, "numerator", self.numerator // divisor)
        object.__setattr__(self, "denominator", self.denominator // divisor)


@dataclass(frozen=True)
class Window:
    index: int
    start: int
    end: int


def build_windows(window_count: int, *, duration: int | float | None = None, window_seconds: int = 4) -> tuple[Window, ...]:
    if window_count < 0 or window_seconds <= 0:
        raise ValueError("invalid window count or duration")
    count = window_count
    if duration is not None:
        count = min(count, int(duration // window_seconds))
    return tuple(Window(i, i * window_seconds, (i + 1) * window_seconds) for i in range(count))


def normalized_pts(raw_pts_ticks: int, origin_pts_ticks: int, time_base_num: int, time_base_den: int) -> Rational:
    if time_base_num <= 0 or time_base_den <= 0:
        raise ValueError("time base must be positive")
    return Rational((raw_pts_ticks - origin_pts_ticks) * time_base_num, time_base_den)


def target_in_window(relative_pts: Rational, target_offset: Rational, window_index: int) -> bool:
    """Apply the literal half-open predicate in normalized window coordinates."""
    if window_index < 0:
        return False
    # Inputs are relative to this window; target is target_offset (typically t/2).
    return target_offset.numerator * relative_pts.denominator <= relative_pts.numerator * target_offset.denominator and relative_pts.numerator < 4 * relative_pts.denominator


def _wire_rational(value: Rational) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


# The persisted window_sample_manifest vocabulary is frozen by
# docs/implementation-spec-v1.1.md §9.2:331-333 (coverage_status includes
# SELECTED; pts_status includes MISSING) and the canonical status namespaces in
# docs/architecture/CANONICAL_CONTRACTS.md §3.  In-process selection keeps the
# historical tokens because the execution owner classifies targets on them;
# only the serialized artifact is normalized here.
_WIRE_COVERAGE_STATUS = {"SUCCEEDED": "SELECTED"}
_WIRE_PTS_STATUS = {"MISSING_PTS": "MISSING"}


@dataclass(frozen=True)
class SampleTarget:
    target_id: str
    window_id: str
    interval_id: str
    tick: int
    target_offset: Rational
    raw_pts: dict[str, int] | None
    normalized_pts: Rational | None
    pts_status: str
    coverage_status: str
    selected_frame_id: str | None = None
    decoder_ordinal: int | None = None
    presentation_order: int | None = None
    duplicate_reason: str | None = None
    mapping_ref: str | None = None
    stream_index: int | None = None
    dts_ticks: int | None = None
    frame_index: int | None = None
    source_frame_identity: str | None = None

    def to_dict(self) -> dict[str, object]:
        out: dict[str, object] = {
            "target_id": self.target_id, "window_id": self.window_id, "interval_id": self.interval_id,
            "tick": self.tick, "target_offset": _wire_rational(self.target_offset),
            "pts_status": _WIRE_PTS_STATUS.get(self.pts_status, self.pts_status),
            "coverage_status": _WIRE_COVERAGE_STATUS.get(self.coverage_status, self.coverage_status),
        }
        if self.raw_pts is not None: out["raw_pts"] = self.raw_pts
        if self.normalized_pts is not None: out["normalized_pts"] = _wire_rational(self.normalized_pts)
        for key, value in (("selected_frame_id", self.selected_frame_id), ("decoder_ordinal", self.decoder_ordinal), ("presentation_order", self.presentation_order), ("duplicate_reason", self.duplicate_reason), ("mapping_ref", self.mapping_ref), ("stream_index", self.stream_index), ("dts_ticks", self.dts_ticks), ("frame_index", self.frame_index), ("source_frame_identity", self.source_frame_identity)):
            if value is not None: out[key] = value
        return out


def sample_targets(revision: RevisionRef, frames: Iterable[DecodedFrame], *, window_count: int = 1, duration: int | float | None = None, origin_pts_ticks: int | None = None, interval_id: str = "interval_0") -> tuple[SampleTarget, ...]:
    sequence = tuple(frames)
    valid = [f for f in sequence if f.raw_pts_ticks is not None and f.time_base_num > 0 and f.time_base_den > 0]
    time_bases = {(f.time_base_num, f.time_base_den) for f in sequence if f.raw_pts_ticks is not None and f.time_base_num > 0 and f.time_base_den > 0}
    mixed_time_base = len(time_bases) > 1
    if origin_pts_ticks is None and valid:
        origin_pts_ticks = valid[0].raw_pts_ticks
    origin_pts_ticks = origin_pts_ticks or 0
    windows = build_windows(window_count, duration=duration)
    rows: list[SampleTarget] = []
    for window in windows:
        for tick in range(8):
            target = Rational(tick, 2)
            selected: tuple[DecodedFrame, Rational] | None = None
            bad_tie = False
            for frame in sequence:
                if frame.raw_pts_ticks is None:
                    continue
                if frame.time_base_num <= 0 or frame.time_base_den <= 0:
                    continue
                pts = normalized_pts(frame.raw_pts_ticks, origin_pts_ticks, frame.time_base_num, frame.time_base_den)
                relative = Rational(pts.numerator - window.start * pts.denominator, pts.denominator)
                if target_in_window(relative, target, window.index):
                    if frame.decoder_ordinal is None and not frame.source_frame_identity:
                        bad_tie = True
                        break
                    selected = (frame, pts)
                    break
            target_id = f"{revision.revision_id}_w{window.index}_t{tick}"
            # Window identity is scoped by source revision: a run spans several
            # sources, so a bare "window_0" would collide across revisions and
            # violate the window_sample_manifest (window_id, tick) uniqueness
            # rule that the artifact contract enforces.
            window_id = f"{revision.revision_id}_window_{window.index}"
            if mixed_time_base:
                rows.append(SampleTarget(target_id, window_id, interval_id, tick, target, None, None, "MIXED_TIME_BASE", "FAILED", stream_index=revision.selected_stream_index))
                continue
            if bad_tie:
                rows.append(SampleTarget(target_id, window_id, interval_id, tick, target, None, None, "MISSING_TIE_EVIDENCE", "FAILED", stream_index=revision.selected_stream_index))
                continue
            if selected is None:
                pts_status = "MISSING_PTS" if any(frame.raw_pts_ticks is None for frame in sequence) else "NO_COVERAGE"
                rows.append(SampleTarget(target_id, window_id, interval_id, tick, target, None, None, pts_status, "FAILED", stream_index=revision.selected_stream_index))
                continue
            frame, pts = selected
            duplicate = "REPEATED_SOURCE_FRAME" if sum(1 for x in sequence if x.source_frame_identity == frame.source_frame_identity) > 1 else None
            raw = {"ticks": frame.raw_pts_ticks, "time_base_num": frame.time_base_num, "time_base_den": frame.time_base_den}
            rows.append(SampleTarget(target_id, window_id, interval_id, tick, target, raw, pts, "VALID", "SUCCEEDED", frame.selected_frame_id, frame.decoder_ordinal, frame.presentation_order, duplicate, f"{revision.revision_id}_map_{frame.selected_frame_id}", revision.selected_stream_index, frame.dts_ticks, frame.frame_index, frame.source_frame_identity))
    return tuple(rows)


def pool_target_slots(rows: Sequence[SampleTarget]) -> tuple[SampleTarget, ...]:
    return tuple(sorted(rows, key=lambda row: (row.window_id, row.tick)))


def target_conservation(rows: Sequence[SampleTarget], planned: int | None = None) -> bool:
    """Return whether every planned slot has one terminal disposition."""
    expected = 8 if planned is None else planned
    terminal = {"SUCCEEDED", "FAILED", "OMITTED", "QUARANTINED"}
    return len(rows) == expected and all(row.coverage_status in terminal for row in rows)


def aggregate_target_slots(rows: Sequence[SampleTarget]) -> tuple[SampleTarget, ...]:
    """Canonical ascending target-tick pooling order (duplicates retained)."""
    return pool_target_slots(rows)
