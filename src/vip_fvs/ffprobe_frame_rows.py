"""Canonical extraction of FFprobe frame and packet rows.

FFprobe 9.x changed the JSON layout when ``-show_frames`` and ``-show_packets``
are requested together: instead of separate ``frames`` and ``packets`` arrays it
emits one ``packets_and_frames`` array whose entries are discriminated by
``type``.  Every VIP FVS reader needs the same rows, so this module is the only
place that knows the payload layout.  It deliberately returns the raw row
mappings unchanged: alias precedence, multiplicity, stream selection, and
de-duplication stay with the reader that owns them.

The adapter is fail-closed.  A malformed layout, an unknown merged row kind, or
two layouts that are both present but disagree about the measured rows raises
:class:`FfprobePayloadShapeError`.  It never silently returns an empty result in
that case, because "no rows" is indistinguishable from "unreadable rows"
downstream and would mask a probe-layout regression as missing evidence.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

FRAME_PRESENTATION_ALIASES: tuple[str, ...] = (
    "best_effort_timestamp",
    "pts",
    "pkt_pts",
)
PACKET_PRESENTATION_ALIASES: tuple[str, ...] = ("pts",)

_LEGACY_FRAME_KEY = "frames"
_LEGACY_PACKET_KEY = "packets"
_MERGED_KEY = "packets_and_frames"


class FfprobePayloadShapeError(ValueError):
    """The FFprobe payload does not expose an unambiguous row layout."""


def normalized_frame_rows(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    """Return the frame rows of an FFprobe payload in payload order.

    Legacy ``frames`` rows and ffprobe-9 ``packets_and_frames`` rows with
    ``type == "frame"`` are both accepted.  When both layouts are present they
    must describe the same measured rows or the payload is refused.
    """
    return _rows(payload, _LEGACY_FRAME_KEY, FRAME_PRESENTATION_ALIASES)


def normalized_packet_rows(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    """Return the packet rows of an FFprobe payload in payload order.

    Legacy ``packets`` rows and ffprobe-9 ``packets_and_frames`` rows with
    ``type == "packet"`` are both accepted.  When both layouts are present they
    must describe the same measured rows or the payload is refused.
    """
    return _rows(payload, _LEGACY_PACKET_KEY, PACKET_PRESENTATION_ALIASES)


def _rows(
    payload: Mapping[str, Any], legacy_key: str, aliases: tuple[str, ...],
) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(payload, Mapping):
        raise FfprobePayloadShapeError("FFPROBE_PAYLOAD_NOT_OBJECT")
    legacy = _legacy_rows(payload, legacy_key)
    merged = _merged_rows(payload)
    merged_rows = None if merged is None else (
        merged[0] if legacy_key == _LEGACY_FRAME_KEY else merged[1])
    if merged_rows is None:
        return legacy if legacy is not None else ()
    if legacy is not None and not _rows_agree(legacy, merged_rows, aliases):
        raise FfprobePayloadShapeError(
            f"FFPROBE_PAYLOAD_{legacy_key.upper()}_LAYOUT_CONFLICT")
    return merged_rows


def _legacy_rows(payload: Mapping[str, Any], key: str) -> tuple[Mapping[str, Any], ...] | None:
    if key not in payload:
        return None
    raw = payload[key]
    if not isinstance(raw, list):
        raise FfprobePayloadShapeError(f"FFPROBE_PAYLOAD_{key.upper()}_NOT_ARRAY")
    rows: list[Mapping[str, Any]] = []
    for index, entry in enumerate(raw):
        if not isinstance(entry, Mapping):
            raise FfprobePayloadShapeError(
                f"FFPROBE_PAYLOAD_{key.upper()}_ROW_{index}_NOT_OBJECT")
        rows.append(entry)
    return tuple(rows)


def _merged_rows(
    payload: Mapping[str, Any],
) -> tuple[tuple[Mapping[str, Any], ...], tuple[Mapping[str, Any], ...]] | None:
    if _MERGED_KEY not in payload:
        return None
    raw = payload[_MERGED_KEY]
    if not isinstance(raw, list):
        raise FfprobePayloadShapeError(
            "FFPROBE_PAYLOAD_PACKETS_AND_FRAMES_NOT_ARRAY")
    frames: list[Mapping[str, Any]] = []
    packets: list[Mapping[str, Any]] = []
    for index, entry in enumerate(raw):
        if not isinstance(entry, Mapping):
            raise FfprobePayloadShapeError(
                f"FFPROBE_PAYLOAD_MERGED_ROW_{index}_NOT_OBJECT")
        kind = entry.get("type")
        if kind == "frame":
            frames.append(entry)
        elif kind == "packet":
            packets.append(entry)
        else:
            # Only the two kinds ffprobe actually emits are proven.  Refuse an
            # unknown/missing discriminator instead of guessing a bucket.
            raise FfprobePayloadShapeError(
                f"FFPROBE_PAYLOAD_MERGED_ROW_{index}_KIND_UNPROVEN")
    return tuple(frames), tuple(packets)


def _rows_agree(
    legacy: tuple[Mapping[str, Any], ...],
    merged: tuple[Mapping[str, Any], ...],
    aliases: tuple[str, ...],
) -> bool:
    if len(legacy) != len(merged):
        return False
    return all(
        _row_identity(left, aliases) == _row_identity(right, aliases)
        for left, right in zip(legacy, merged)
    )


def _row_identity(row: Mapping[str, Any], aliases: tuple[str, ...]) -> tuple[Any, Any]:
    return _stream_identity(row.get("stream_index")), _presentation_identity(row, aliases)


def _stream_identity(value: Any) -> tuple[str, Any]:
    if isinstance(value, bool):
        return "other", repr(value)
    if isinstance(value, int):
        return "int", value
    if isinstance(value, str):
        text = value.strip()
        if text.lstrip("-").isdigit():
            return "int", int(text)
        return "str", text
    return "other", repr(value)


def _presentation_identity(row: Mapping[str, Any], aliases: tuple[str, ...]) -> tuple[str, Any]:
    for alias in aliases:
        value = row.get(alias)
        if isinstance(value, int) and not isinstance(value, bool):
            return "int", value
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return "int", int(value.strip())
    return "absent", None
