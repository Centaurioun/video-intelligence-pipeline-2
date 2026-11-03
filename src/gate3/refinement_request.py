"""Closed control envelope for a source-native Gate-3 refinement request.

The request carries intent and expected identity only. It is not evidence and
does not confer temporal, editorial, render, or production authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True, slots=True)
class RefinementRequest:
    """Immutable request to measure one interval in named source-native PTS."""

    request_id: str
    candidate_assertion_ref: str
    source_revision_id: str
    source_locator: str
    expected_source_sha256: str
    selected_stream_index: int
    requested_start_pts: int
    requested_end_pts: int
    producer_attempt_id: str
    idempotency_key: str
    expected_timebase: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "candidate_assertion_ref",
            "source_revision_id",
            "source_locator",
            "producer_attempt_id",
            "idempotency_key",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        if not isinstance(self.expected_source_sha256, str) or not _SHA256_RE.fullmatch(
            self.expected_source_sha256
        ):
            raise ValueError("expected_source_sha256 must be a lowercase SHA-256 digest")

        if (
            not isinstance(self.selected_stream_index, int)
            or isinstance(self.selected_stream_index, bool)
            or self.selected_stream_index < 0
        ):
            raise TypeError("selected_stream_index must be a non-negative integer")

        for name in ("requested_start_pts", "requested_end_pts"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an exact integer source PTS")
        if self.requested_end_pts <= self.requested_start_pts:
            raise ValueError("requested PTS interval must be non-empty and half-open")

        if self.expected_timebase is not None:
            value = self.expected_timebase
            if not isinstance(value, tuple) or len(value) != 2:
                raise TypeError("expected_timebase must be a (numerator, denominator) tuple")
            numerator, denominator = value
            if (
                not isinstance(numerator, int)
                or isinstance(numerator, bool)
                or not isinstance(denominator, int)
                or isinstance(denominator, bool)
            ):
                raise TypeError("expected_timebase components must be exact integers")
            if numerator <= 0 or denominator <= 0:
                raise ValueError("expected_timebase components must be positive")


@dataclass(frozen=True)
class ResolvedResult:
    """Legacy request-resolution result retained for existing callers."""

    request_id: str
    resolved_start_ticks: int | None
    resolved_end_ticks: int | None
    policy: str
