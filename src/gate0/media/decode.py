"""Measured ffprobe/ffmpeg decoder adapter (Gate-0 Objective B).

This module turns a real media file into a :class:`FrameSequence` whose frame
identities come **only** from measured presentation timestamps reported by
``ffprobe``.  It never infers a frame index from a nominal frame rate, never
ranks frames by DTS, and never uses a bare absolute stream index with
``-select_streams`` (an audio-first container silently returns audio frames in
that case).

Design invariants
-----------------
* Presentation identity is ``pts`` in the measured stream time base; a frame
  row without an integer ``pts`` is a hard failure, not a fallback.
* The emitted frame list is kept exactly as the tool reported it.  For a
  well-behaved demuxer this is presentation order, and
  ``presentation_order == decoder_ordinal``; if it is not, the measured rank is
  recorded without silently reordering the sequence.
* ``dts_ticks`` is always ``None``: frame-level ``pkt_dts`` in ffprobe 9.x is a
  presentation-timestamp copy (and absent for EOF-flushed frames), not the
  packet DTS, so it is not identity evidence.
* Silent partial decodes fail closed: container-declared ``nb_frames`` must
  agree with the decoded row count, and corruption markers on stderr abort the
  measurement.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from fractions import Fraction
import json
import re
from typing import Any, Iterator, Mapping, Sequence

from gate0.adapters.decoder import DecodedFrame, DecoderAdapter
from gate0.identity import digest_bytes
from gate0.inventory import RevisionRef
from gate0.media.source_guard import (
    DEFAULT_MAX_SOURCE_BYTES,
    SourceGuardError,
    SourceSnapshot,
    snapshot_path,
    verify_path,
)
from gate0.media.proc import (
    DEFAULT_MAX_STDERR_BYTES,
    DEFAULT_MAX_STDOUT_BYTES,
    ToolError,
    ToolRun,
    run_bounded,
)
from gate0.media.tool_identity import ToolIdentity, measure_tool

__all__ = [
    "DecodeFailure",
    "FrameSequence",
    "FfprobeFrameDecoder",
    "decode_frames",
]

_JSON_ARGUMENTS = ("-print_format", "json")

#: Only fields that actually exist in ffprobe 9.x and that we consume are
#: requested.  In particular ``pkt_duration``/``pkt_duration_time`` do not
#: exist there (they return silently empty output) and ``pkt_dts`` is not DTS.
_FRAME_ENTRY_ALLOWLIST = (
    "frame=media_type,stream_index,key_frame,pts,duration,duration_time"
)

#: Case-insensitive stderr markers that prove the demuxer/decoder saw a
#: partially readable or corrupt bitstream even when the process exits zero.
_PARTIAL_STREAM_MARKERS = ("partial file", "invalid nal", "corrupt")

_TIME_BASE_PATTERN = re.compile(r"^(?P<num>\d+)/(?P<den>\d+)$", re.ASCII)
_DECLARED_FRAME_COUNT_PATTERN = re.compile(r"^\d+$", re.ASCII)
_FRAME_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,127}$", re.ASCII)

#: RGB24 is three bytes per pixel.
_RGB24_BYTES_PER_PIXEL = 3

#: Slack added to the rawvideo byte cap so "too many bytes" is observable
#: instead of being truncated at exactly the expected size.
_DECODE_BYTE_CAP_SLACK = 1


class DecodeFailure(ValueError):
    """A failed, fail-closed decode measurement with a stable reason code."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        message = reason if not detail else f"{reason}: {detail}"
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class FrameSequence:
    """Immutable, digest-bound measurement of one video stream."""

    frames: tuple[DecodedFrame, ...]
    stream_index: int
    time_base: tuple[int, int]
    tool: ToolIdentity
    raw_frames_digest: str
    source_path: str
    source_digest: str
    frame_count: int
    duration_ms: int
    pix_fmt: str | None = None


class FfprobeFrameDecoder(DecoderAdapter):
    """Replay a measured :class:`FrameSequence` through the decoder interface.

    The adapter never re-measures: it yields the frozen sequence unchanged so
    downstream temporal sampling sees exactly the presentation evidence that
    was recorded.  A stream mismatch is an explicit error rather than a silent
    substitution.
    """

    def __init__(self, sequence: FrameSequence) -> None:
        self._sequence = sequence

    @property
    def sequence(self) -> FrameSequence:
        return self._sequence

    def iter_frames(
        self, source: RevisionRef, stream_index: int
    ) -> Iterator[DecodedFrame]:
        if stream_index != source.selected_stream_index:
            raise ValueError("SELECTED_STREAM_MISMATCH")
        if stream_index != self._sequence.stream_index:
            raise ValueError("SELECTED_STREAM_MISMATCH")
        yield from self._sequence.frames


def decode_frames(
    source: RevisionRef,
    *,
    ffprobe_path: str = "ffprobe",
    ffmpeg_path: str = "ffmpeg",
    timeout_seconds: float = 60.0,
    decode_pixels: bool = False,
    expected_source_digest: str | None = None,
    allow_equal_pts_ties: bool = False,
    max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> FrameSequence:
    """Measure one explicitly selected video stream into a frame sequence.

    ``source.locator`` is the media path and ``source.selected_stream_index``
    is the absolute ffprobe stream index (0-based over the whole container).
    """

    source_path = str(source.locator)
    selected_stream_index = source.selected_stream_index
    if (
        not isinstance(selected_stream_index, int)
        or isinstance(selected_stream_index, bool)
        or selected_stream_index < 0
    ):
        raise DecodeFailure(
            "SELECTED_STREAM_NOT_ELIGIBLE",
            f"invalid selected stream index {selected_stream_index!r}",
        )

    # ---- source identity / immutability guard ---------------------------
    initial = _snapshot_source(source_path, max_source_bytes)
    if initial.byte_count == 0:
        raise DecodeFailure("SOURCE_UNREADABLE", f"{source_path} is empty")
    source_digest = initial.digest
    if expected_source_digest is not None:
        if not isinstance(expected_source_digest, str) or (
            expected_source_digest != source_digest
        ):
            raise DecodeFailure(
                "SOURCE_MUTATED",
                "source digest does not match expected_source_digest",
            )

    probe_tool = _measure_tool_identity("ffprobe", ffprobe_path)

    # ---- stream discovery: absolute index -> video ordinal --------------
    discovery = _run_tool(
        probe_tool,
        (
            "-v",
            "error",
            *_JSON_ARGUMENTS,
            "-show_streams",
            source_path,
        ),
        timeout_seconds=timeout_seconds,
    )
    discovery_payload = _parse_json(discovery, "stream discovery")
    streams = discovery_payload.get("streams")
    if not isinstance(streams, list):
        raise DecodeFailure(
            "PROBE_OUTPUT_MALFORMED", "stream discovery has no 'streams' array"
        )

    selected_rows = [
        row
        for row in streams
        if isinstance(row, dict) and row.get("index") == selected_stream_index
    ]
    if len(selected_rows) != 1:
        raise DecodeFailure(
            "SELECTED_STREAM_NOT_ELIGIBLE",
            f"selected stream {selected_stream_index} is not uniquely present",
        )
    discovery_row = selected_rows[0]
    if discovery_row.get("codec_type") != "video":
        raise DecodeFailure(
            "SELECTED_STREAM_NOT_ELIGIBLE",
            f"selected stream {selected_stream_index} is "
            f"{discovery_row.get('codec_type')!r}, not video",
        )

    video_rows = [
        row
        for row in streams
        if isinstance(row, dict) and row.get("codec_type") == "video"
    ]
    video_ordinal: int | None = None
    for position, row in enumerate(video_rows):
        if row.get("index") == selected_stream_index:
            video_ordinal = position
            break
    if video_ordinal is None:  # pragma: no cover - guarded by selected_rows
        raise DecodeFailure(
            "SELECTED_STREAM_NOT_ELIGIBLE",
            f"selected stream {selected_stream_index} has no video ordinal",
        )

    # ---- selected stream measurement (bounded, v:<ordinal>) -------------
    selected_run = _run_tool(
        probe_tool,
        (
            "-v",
            "error",
            *_JSON_ARGUMENTS,
            "-show_streams",
            "-select_streams",
            f"v:{video_ordinal}",
            source_path,
        ),
        timeout_seconds=timeout_seconds,
    )
    selected_payload = _parse_json(selected_run, "selected stream")
    selected_streams = selected_payload.get("streams")
    if not isinstance(selected_streams, list):
        raise DecodeFailure(
            "PROBE_OUTPUT_MALFORMED", "selected stream has no 'streams' array"
        )
    if len(selected_streams) != 1:
        raise DecodeFailure(
            "SELECTED_STREAM_NOT_ELIGIBLE",
            f"selection v:{video_ordinal} returned "
            f"{len(selected_streams)} streams",
        )
    selected_row = selected_streams[0]
    if not isinstance(selected_row, dict):
        raise DecodeFailure(
            "PROBE_OUTPUT_MALFORMED", "selected stream row is not an object"
        )
    if (
        selected_row.get("index") != selected_stream_index
        or selected_row.get("codec_type") != "video"
    ):
        raise DecodeFailure(
            "WRONG_STREAM",
            f"selection v:{video_ordinal} returned stream "
            f"{selected_row.get('index')!r} "
            f"({selected_row.get('codec_type')!r})",
        )

    time_base_num, time_base_den = _parse_time_base(
        selected_row.get("time_base"), selected_stream_index
    )
    width = _positive_int_or_none(selected_row.get("width"))
    height = _positive_int_or_none(selected_row.get("height"))
    declared_frame_count = _declared_frame_count(selected_row.get("nb_frames"))

    # ---- frame listing: presentation evidence ---------------------------
    frames_run = _run_tool(
        probe_tool,
        (
            "-v",
            "error",
            "-select_streams",
            f"v:{video_ordinal}",
            "-show_frames",
            "-show_entries",
            _FRAME_ENTRY_ALLOWLIST,
            *_JSON_ARGUMENTS,
            source_path,
        ),
        timeout_seconds=timeout_seconds,
    )
    frames_payload = _parse_json(frames_run, "frame listing")

    _reject_partial_stream_evidence(
        (discovery, selected_run, frames_run), source_path
    )

    frames_rows = frames_payload.get("frames")
    if not isinstance(frames_rows, list):
        raise DecodeFailure(
            "PROBE_OUTPUT_MALFORMED", "frame listing has no 'frames' array"
        )
    if not frames_rows:
        raise DecodeFailure(
            "NO_FRAMES", f"stream {selected_stream_index} reported no frames"
        )

    frames = _build_frames(
        frames_rows,
        stream_index=selected_stream_index,
        time_base=(time_base_num, time_base_den),
        allow_equal_pts_ties=allow_equal_pts_ties,
    )

    if declared_frame_count is not None and len(frames) != declared_frame_count:
        raise DecodeFailure(
            "INCOMPLETE_STREAM_EVIDENCE",
            f"container declared {declared_frame_count} frames but "
            f"{len(frames)} were decoded",
        )

    duration_ms = _measure_duration_ms(
        selected_row.get("duration"),
        frames_rows,
        time_base=(time_base_num, time_base_den),
    )

    pix_fmt: str | None = None
    if decode_pixels:
        frames, pix_fmt = _attach_pixels(
            frames,
            source_path=source_path,
            selected_stream_index=selected_stream_index,
            width=width,
            height=height,
            ffmpeg_path=ffmpeg_path,
            timeout_seconds=timeout_seconds,
        )

    # ---- immutability re-check ------------------------------------------
    try:
        verify_path(source_path, initial, max_bytes=max_source_bytes)
    except SourceGuardError as exc:
        raise DecodeFailure(
            "SOURCE_MUTATED", f"source changed during measurement: {exc.detail or exc.reason}"
        ) from exc

    return FrameSequence(
        frames=frames,
        stream_index=selected_stream_index,
        time_base=(time_base_num, time_base_den),
        tool=probe_tool,
        raw_frames_digest=digest_bytes(frames_run.stdout),
        source_path=source_path,
        source_digest=source_digest,
        frame_count=len(frames),
        duration_ms=duration_ms,
        pix_fmt=pix_fmt,
    )


# ---------------------------------------------------------------------------
# tool plumbing
# ---------------------------------------------------------------------------


def _snapshot_source(path: str, max_source_bytes: int) -> SourceSnapshot:
    try:
        return snapshot_path(path, max_bytes=max_source_bytes)
    except SourceGuardError as exc:
        reason = "SOURCE_UNREADABLE" if exc.reason == "SOURCE_NOT_REGULAR" else exc.reason
        raise DecodeFailure(reason, exc.detail) from exc


def _measure_tool_identity(role: str, executable: str) -> ToolIdentity:
    try:
        return measure_tool(role, executable)
    except ToolError as exc:
        raise DecodeFailure(
            "PROBE_TOOL_FAILED", f"cannot measure {role} identity: {exc}"
        ) from exc


def _run_tool(
    tool: ToolIdentity,
    arguments: Sequence[str],
    *,
    timeout_seconds: float,
    max_stdout_bytes: int = DEFAULT_MAX_STDOUT_BYTES,
    max_stderr_bytes: int = DEFAULT_MAX_STDERR_BYTES,
) -> ToolRun:
    argv = (tool.executable, *arguments)
    try:
        run = run_bounded(
            argv,
            timeout_seconds=timeout_seconds,
            max_stdout_bytes=max_stdout_bytes,
            max_stderr_bytes=max_stderr_bytes,
        )
    except ToolError as exc:
        raise DecodeFailure(
            "PROBE_TOOL_FAILED", f"{tool.role} could not run: {exc}"
        ) from exc
    if run.timed_out:
        raise DecodeFailure(
            "PROBE_TOOL_TIMEOUT",
            f"{tool.role} exceeded {timeout_seconds:g}s",
        )
    if run.stdout_truncated:
        raise DecodeFailure(
            "PROBE_OUTPUT_TRUNCATED",
            f"{tool.role} stdout exceeded {max_stdout_bytes} bytes",
        )
    if run.exit_code != 0:
        stderr_line = _first_stderr_line(run.stderr_text)
        detail = f"{tool.role} exited {run.exit_code}"
        if stderr_line:
            detail = f"{detail}: {stderr_line}"
        raise DecodeFailure("PROBE_TOOL_FAILED", detail)
    return run


def _first_stderr_line(stderr_text: str) -> str:
    for line in stderr_text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:200]
    return ""


def _parse_json(run: ToolRun, what: str) -> Mapping[str, Any]:
    try:
        payload = json.loads(run.stdout_text)
    except ValueError as exc:
        raise DecodeFailure(
            "PROBE_OUTPUT_MALFORMED", f"{what}: invalid JSON ({exc})"
        ) from exc
    if not isinstance(payload, dict):
        raise DecodeFailure(
            "PROBE_OUTPUT_MALFORMED", f"{what}: JSON root is not an object"
        )
    return payload


def _reject_partial_stream_evidence(
    runs: Sequence[ToolRun], source_path: str
) -> None:
    stderr_blob = "\n".join(run.stderr_text for run in runs).lower()
    for marker in _PARTIAL_STREAM_MARKERS:
        if marker in stderr_blob:
            raise DecodeFailure(
                "PARTIAL_STREAM_EVIDENCE",
                f"{source_path}: ffprobe reported {marker!r} on stderr",
            )


# ---------------------------------------------------------------------------
# stream-row parsing
# ---------------------------------------------------------------------------


def _parse_time_base(value: Any, stream_index: int) -> tuple[int, int]:
    if not isinstance(value, str):
        raise DecodeFailure(
            "TIME_BASE_INVALID",
            f"stream {stream_index} has no string time_base ({value!r})",
        )
    match = _TIME_BASE_PATTERN.fullmatch(value)
    if match is None:
        raise DecodeFailure(
            "TIME_BASE_INVALID",
            f"stream {stream_index} time_base {value!r} is not num/den",
        )
    numerator = int(match.group("num"))
    denominator = int(match.group("den"))
    if numerator <= 0 or denominator <= 0:
        raise DecodeFailure(
            "TIME_BASE_INVALID",
            f"stream {stream_index} time_base {value!r} is not positive",
        )
    return numerator, denominator


def _positive_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value > 0:
        return value
    return None


def _declared_frame_count(value: Any) -> int | None:
    """Parse container ``nb_frames`` without ever treating it as a measurement.

    ``"N/A"`` and any non-integer value mean "unknown", not a failure.
    """

    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str) and _DECLARED_FRAME_COUNT_PATTERN.fullmatch(value):
        return int(value)
    return None


def _parse_decimal_seconds(value: Any) -> Fraction | None:
    if not isinstance(value, str):
        return None
    try:
        seconds = Fraction(value)
    except (ValueError, ZeroDivisionError):
        return None
    if seconds < 0:
        return None
    return seconds


def _measure_duration_ms(
    declared_duration: Any,
    frames_rows: Sequence[Any],
    *,
    time_base: tuple[int, int],
) -> int:
    """Measured media duration in whole milliseconds.

    Primary evidence is the selected stream's ``duration`` seconds string
    (container timing, not a synthetic frame-rate calculation).  When that is
    unavailable (``"N/A"``), fall back to the measured frame PTS span plus the
    last frame's reported ``duration`` in stream ticks.
    """

    seconds = _parse_decimal_seconds(declared_duration)
    if seconds is not None:
        return int(seconds * 1000)

    first: Any = frames_rows[0] if frames_rows else None
    last: Any = frames_rows[-1] if frames_rows else None
    if isinstance(first, dict) and isinstance(last, dict):
        first_pts = first.get("pts")
        last_pts = last.get("pts")
        last_duration = last.get("duration")
        if _is_int(first_pts) and _is_int(last_pts):
            span = last_pts - first_pts
            if _is_int(last_duration):
                span += max(last_duration, 0)
            if span >= 0:
                numerator, denominator = time_base
                return int(Fraction(span * numerator * 1000, denominator))
    return 0


# ---------------------------------------------------------------------------
# frame mapping
# ---------------------------------------------------------------------------


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _build_frames(
    rows: Sequence[Any],
    *,
    stream_index: int,
    time_base: tuple[int, int],
    allow_equal_pts_ties: bool,
) -> tuple[DecodedFrame, ...]:
    time_base_num, time_base_den = time_base
    pts_values: list[int] = []

    for ordinal, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DecodeFailure(
                "PROBE_OUTPUT_MALFORMED",
                f"frame row {ordinal} is not an object",
            )
        pts = row.get("pts")
        if not _is_int(pts):
            raise DecodeFailure(
                "MISSING_PRESENTATION_TIMESTAMP",
                f"frame row {ordinal} has no integer pts ({pts!r})",
            )
        row_stream_index = row.get("stream_index")
        if not _is_int(row_stream_index) or row_stream_index != stream_index:
            raise DecodeFailure(
                "WRONG_STREAM",
                f"frame row {ordinal} belongs to stream "
                f"{row_stream_index!r}, expected {stream_index}",
            )
        if "media_type" in row and row["media_type"] != "video":
            raise DecodeFailure(
                "WRONG_STREAM",
                f"frame row {ordinal} media_type is {row['media_type']!r}",
            )
        pts_values.append(pts)

    duplicate_pts = sorted(
        pts for pts, count in Counter(pts_values).items() if count > 1
    )
    if duplicate_pts and not allow_equal_pts_ties:
        raise DecodeFailure(
            "DUPLICATE_PRESENTATION_EVIDENCE",
            f"equal pts values {duplicate_pts!r} need explicit tie opt-in",
        )

    # Ranks from a stable sort by (pts, decoder ordinal).  This is identity
    # bookkeeping only: ``frames`` stays in emitted order.
    ranks = [0] * len(pts_values)
    for rank, ordinal in enumerate(
        sorted(range(len(pts_values)), key=lambda i: (pts_values[i], i))
    ):
        ranks[ordinal] = rank

    frame_ids: list[str] = []
    for ordinal, pts in enumerate(pts_values):
        frame_id = f"{stream_index}_{pts}_{ordinal:06d}"
        if _FRAME_ID_PATTERN.fullmatch(frame_id) is None:
            raise DecodeFailure(
                "AMBIGUOUS_PRESENTATION_EVIDENCE",
                f"frame {ordinal} produces an invalid identity {frame_id!r}",
            )
        frame_ids.append(frame_id)
    if len(set(frame_ids)) != len(frame_ids):  # pragma: no cover - ordinal-unique
        raise DecodeFailure(
            "AMBIGUOUS_PRESENTATION_EVIDENCE", "duplicate frame identities"
        )

    frames = tuple(
        DecodedFrame(
            raw_pts_ticks=pts,
            time_base_num=time_base_num,
            time_base_den=time_base_den,
            decoder_ordinal=ordinal,
            presentation_order=ranks[ordinal],
            selected_frame_id=frame_ids[ordinal],
            pixels=None,
            status="DECODED",
            # Frame-level pkt_dts in ffprobe 9.x is a pts copy (and absent on
            # EOF-flushed frames); real DTS only exists in -show_packets, which
            # this adapter deliberately does not consume.
            dts_ticks=None,
            # The tool provides no source frame index; never synthesise one.
            frame_index=None,
            source_frame_identity=frame_ids[ordinal],
        )
        for ordinal, pts in enumerate(pts_values)
    )
    return frames


# ---------------------------------------------------------------------------
# pixel decoding (opt-in)
# ---------------------------------------------------------------------------


def _attach_pixels(
    frames: tuple[DecodedFrame, ...],
    *,
    source_path: str,
    selected_stream_index: int,
    width: int | None,
    height: int | None,
    ffmpeg_path: str,
    timeout_seconds: float,
) -> tuple[tuple[DecodedFrame, ...], str]:
    if width is None or height is None:
        raise DecodeFailure(
            "GEOMETRY_UNMEASURED",
            "selected video stream has no positive width/height",
        )

    ffmpeg_tool = _measure_tool_identity("ffmpeg", ffmpeg_path)
    frame_bytes = width * height * _RGB24_BYTES_PER_PIXEL
    expected_bytes = len(frames) * frame_bytes
    max_stdout_bytes = max(
        DEFAULT_MAX_STDOUT_BYTES, expected_bytes + _DECODE_BYTE_CAP_SLACK
    )

    run = _run_tool(
        ffmpeg_tool,
        (
            "-v",
            "error",
            "-nostdin",
            "-i",
            source_path,
            "-map",
            f"0:{selected_stream_index}",
            "-fps_mode",
            "passthrough",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ),
        timeout_seconds=timeout_seconds,
        max_stdout_bytes=max_stdout_bytes,
    )

    if run.stdout_truncated or len(run.stdout) != expected_bytes:
        raise DecodeFailure(
            "DECODE_FRAME_COUNT_MISMATCH",
            f"expected {expected_bytes} rgb24 bytes "
            f"({len(frames)} frames x {width}x{height}x3) but measured "
            f"{len(run.stdout)} bytes"
            + (" (stdout truncated)" if run.stdout_truncated else ""),
        )

    decoded = tuple(
        replace(
            frame,
            pixels=run.stdout[
                ordinal * frame_bytes : (ordinal + 1) * frame_bytes
            ],
        )
        for ordinal, frame in enumerate(frames)
    )
    return decoded, "rgb24"
