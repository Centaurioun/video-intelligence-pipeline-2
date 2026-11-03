"""Strict validation for digest-bound synthetic fixture source descriptors.

The synthetic vertical slice measures PTS/timebase from a JSON fixture recipe.
That recipe is an *input to a measurement*, so it must be unambiguous,
internally consistent, and bound to the exact bytes the inventory chain hashed.
This module refuses anything else instead of falling back to defaulted or
truncated timestamps.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

SYNTHETIC_RECIPE_SCHEMA = "vip_fvs.fixture.v1"
# The materializer writes exactly these two envelope fields.
ENVELOPE_FIELDS = frozenset({"recipe", "content_sha256"})


class SyntheticRecipeRefusal(ValueError):
    """A synthetic source descriptor is ambiguous, incomplete, or mislabelled."""


def _refuse(code: str) -> None:
    raise SyntheticRecipeRefusal(code)


def _require_int(value: Any, code: str) -> int:
    # ``bool`` is an ``int`` subclass; a flag is not a timestamp.
    if isinstance(value, bool) or not isinstance(value, int):
        _refuse(code)
    return value


def _canonical_digest(recipe: dict[str, Any]) -> str:
    canonical = json.dumps(recipe, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_synthetic_recipe(raw: bytes, *, scenario: str) -> dict[str, Any]:
    """Validate a materialized fixture descriptor and return its recipe.

    Raises :class:`SyntheticRecipeRefusal` with a stable reason token.  The
    caller must not derive any PTS from a refused descriptor.
    """
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        _refuse("SYNTHETIC_RECIPE_SOURCE_NOT_JSON")
    if not isinstance(payload, dict) or frozenset(payload) != ENVELOPE_FIELDS:
        _refuse("SYNTHETIC_RECIPE_ENVELOPE_INVALID")
    recipe = payload.get("recipe")
    declared_digest = payload.get("content_sha256")
    if not isinstance(recipe, dict) or not isinstance(declared_digest, str):
        _refuse("SYNTHETIC_RECIPE_ENVELOPE_INVALID")
    if declared_digest != _canonical_digest(recipe):
        _refuse("SYNTHETIC_RECIPE_DIGEST_MISMATCH")
    if recipe.get("schema_version") != SYNTHETIC_RECIPE_SCHEMA:
        _refuse("SYNTHETIC_RECIPE_SCHEMA_UNSUPPORTED")
    fixture_id = recipe.get("fixture_id")
    if not isinstance(fixture_id, str) or not fixture_id:
        _refuse("SYNTHETIC_RECIPE_IDENTITY_MISMATCH")
    if fixture_id != scenario:
        _refuse("SYNTHETIC_RECIPE_IDENTITY_MISMATCH")
    if recipe.get("source_kind") != "synthetic":
        _refuse("SYNTHETIC_RECIPE_IDENTITY_MISMATCH")
    stream = recipe.get("stream")
    if not isinstance(stream, dict):
        _refuse("SYNTHETIC_RECIPE_TIME_BASE_INVALID")
    if stream.get("type") != "video":
        _refuse("SYNTHETIC_RECIPE_STREAM_INVALID")
    _require_int(stream.get("index"), "SYNTHETIC_RECIPE_STREAM_INVALID")
    time_base = stream.get("time_base")
    if not isinstance(time_base, dict) or frozenset(time_base) != frozenset({"num", "den"}):
        _refuse("SYNTHETIC_RECIPE_TIME_BASE_INVALID")
    numerator = _require_int(time_base["num"], "SYNTHETIC_RECIPE_TIME_BASE_INVALID")
    denominator = _require_int(time_base["den"], "SYNTHETIC_RECIPE_TIME_BASE_INVALID")
    if numerator <= 0 or denominator <= 0:
        _refuse("SYNTHETIC_RECIPE_TIME_BASE_INVALID")
    if _require_int(stream.get("media_timescale"), "SYNTHETIC_RECIPE_TIME_BASE_INVALID") != denominator:
        _refuse("SYNTHETIC_RECIPE_TIME_BASE_INVALID")
    origin_ticks = _require_int(stream.get("origin_pts_ticks"), "SYNTHETIC_RECIPE_PTS_INVALID")
    declared_pts = recipe.get("pts_ticks")
    if not isinstance(declared_pts, list) or not declared_pts:
        _refuse("SYNTHETIC_RECIPE_PTS_INVALID")
    pts = [_require_int(value, "SYNTHETIC_RECIPE_PTS_INVALID") for value in declared_pts]
    if any(current <= previous for previous, current in zip(pts, pts[1:])):
        _refuse("SYNTHETIC_RECIPE_PTS_INVALID")
    if pts[0] != origin_ticks:
        _refuse("SYNTHETIC_RECIPE_PTS_INVALID")
    tail_ticks = _require_int(recipe.get("tail_duration_ticks"), "SYNTHETIC_RECIPE_DURATION_INCONSISTENT")
    if tail_ticks <= 0:
        _refuse("SYNTHETIC_RECIPE_DURATION_INCONSISTENT")
    duration_ticks = _require_int(recipe.get("duration_ticks"), "SYNTHETIC_RECIPE_DURATION_INCONSISTENT")
    if duration_ticks != pts[-1] + tail_ticks:
        _refuse("SYNTHETIC_RECIPE_DURATION_INCONSISTENT")
    frames = recipe.get("frames")
    if frames is not None:
        if not isinstance(frames, list) or len(frames) != len(pts):
            _refuse("SYNTHETIC_RECIPE_FRAME_ORDER_INCONSISTENT")
        for ordinal, frame in enumerate(frames):
            if not isinstance(frame, dict):
                _refuse("SYNTHETIC_RECIPE_FRAME_ORDER_INCONSISTENT")
            if _require_int(frame.get("presentation_ordinal"), "SYNTHETIC_RECIPE_FRAME_ORDER_INCONSISTENT") != ordinal:
                _refuse("SYNTHETIC_RECIPE_FRAME_ORDER_INCONSISTENT")
            if _require_int(frame.get("pts_ticks"), "SYNTHETIC_RECIPE_FRAME_ORDER_INCONSISTENT") != pts[ordinal]:
                _refuse("SYNTHETIC_RECIPE_FRAME_ORDER_INCONSISTENT")
    return recipe


__all__ = ["SYNTHETIC_RECIPE_SCHEMA", "SyntheticRecipeRefusal", "load_synthetic_recipe"]
