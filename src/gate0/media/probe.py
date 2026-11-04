"""Real local ``ffprobe`` probe adapter for Gate-0 measured media evidence.

This module is the *only* authority for probe evidence: it launches exactly one
bounded ``ffprobe`` process per source, preserves the parsed JSON verbatim,
binds the measurement to the measured tool identity and to the exact source
bytes, and fails closed with a stable reason code whenever the observation
cannot be proven. It never infers stream selection, never substitutes a
different rate for the measured time base, and never inherits an ambient
environment (``gate0.media.proc.run_bounded`` sanitizes it).

Requested-field allowlist: ``STREAM_FIELDS`` and ``FORMAT_FIELDS`` are explicit
on purpose. ``r_frame_rate`` / ``avg_frame_rate`` are deliberately absent: a
nominal frame rate is not presentation timing, and nothing here may derive a
frame index from ``seconds * FPS``. ``-show_frames`` is also absent; frame-level
presentation timing belongs to the decode adapter, not to probe metadata.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping, NoReturn

from gate0.identity import digest_bytes, opaque_id
from gate0.inventory import ProbeEvidence
from gate0.media.proc import run_bounded
from gate0.media.source_guard import (
    DEFAULT_MAX_SOURCE_BYTES,
    SourceGuardError,
    SourceSnapshot,
    snapshot_path,
    verify_path,
)
from gate0.media.tool_identity import ToolIdentity, measure_tool

PROBE_ROLE = "ffprobe"
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_STDOUT_BYTES = 4 * 1024 * 1024

#: Stream attributes this adapter is allowed to observe. Explicit, minimal, and
#: intentionally free of any nominal-rate field.
STREAM_FIELDS: tuple[str, ...] = (
    "index",
    "codec_type",
    "codec_name",
    "time_base",
    "start_time",
    "duration_ts",
    "nb_frames",
    "has_b_frames",
)
#: Container-level attributes this adapter is allowed to observe.
FORMAT_FIELDS: tuple[str, ...] = ("format_name", "duration", "size", "start_time", "nb_streams")

SHOW_ENTRIES = f"stream={','.join(STREAM_FIELDS)}:format={','.join(FORMAT_FIELDS)}"
#: Everything the adapter passes to ffprobe before the ``-i <source>`` pair.
PROBE_COMMAND_OPTIONS: tuple[str, ...] = (
    "-v",
    "error",
    "-print_format",
    "json",
    "-show_streams",
    "-show_format",
    "-show_entries",
    SHOW_ENTRIES,
)

#: The only stream types Gate-0 provenance records can represent.
STREAM_TYPES: tuple[str, ...] = ("video", "audio", "data", "subtitle")

_TIME_BASE = re.compile(r"([0-9]+)/([0-9]+)", re.ASCII)


class ProbeFailure(ValueError):
    """One fail-closed probe outcome; ``reason`` is the stable machine code."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else f"{reason}: {detail}")


@dataclass(frozen=True)
class ProbeStream:
    """Measured attributes of exactly one probe stream, in probe order."""

    stream_index: int
    stream_type: str
    time_base: tuple[int, int] | None
    codec_name: str | None
    start_time: str | None
    duration_ts: int | None
    nb_frames: str | None
    has_b_frames: int | None


@dataclass(frozen=True)
class ProbeCapture:
    """Immutable, digest-bound observation of one probed source."""

    evidence: ProbeEvidence
    tool: ToolIdentity
    source_path: str
    source_byte_count: int
    source_digest: str
    raw_output_digest: str
    exit_code: int
    duration_ms: int
    streams: tuple[ProbeStream, ...]


def _probe_reason(exc: SourceGuardError) -> str:
    """Map source-guard refusals onto this adapter's stable reason vocabulary.

    A directory/device is reported as an unreadable source (the long-standing
    probe contract); every other refusal keeps its own code so callers can
    distinguish symlink/hardlink/quota/mutation attacks.
    """
    if exc.reason == "SOURCE_NOT_REGULAR":
        return "SOURCE_UNREADABLE"
    return exc.reason


def _fail(reason: str, detail: str = "") -> NoReturn:
    raise ProbeFailure(reason, detail)


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _parse_time_base(raw: Any) -> tuple[int, int] | None:
    """Parse ``"num/den"`` strictly; ``None`` means the stream reports no time base."""
    if raw is None:
        return None
    if not isinstance(raw, str):
        _fail("TIME_BASE_INVALID", f"time_base is not a string: {raw!r}")
    match = _TIME_BASE.fullmatch(raw)
    if match is None:
        _fail("TIME_BASE_INVALID", f"time_base is not num/den: {raw!r}")
    numerator, denominator = int(match.group(1)), int(match.group(2))
    if numerator <= 0 or denominator <= 0:
        _fail("TIME_BASE_INVALID", f"time_base is not positive: {raw!r}")
    return numerator, denominator


def _parse_stream(raw: Any, seen: set[int]) -> ProbeStream:
    if not isinstance(raw, Mapping):
        _fail("PROBE_OUTPUT_AMBIGUOUS", "stream entry is not an object")
    index = _optional_int(raw.get("index"))
    if index is None:
        _fail("PROBE_OUTPUT_AMBIGUOUS", "stream has no integer index")
    if index in seen:
        _fail("PROBE_OUTPUT_AMBIGUOUS", f"duplicate stream index {index}")
    seen.add(index)
    codec_type = raw.get("codec_type")
    if not isinstance(codec_type, str):
        _fail("PROBE_OUTPUT_AMBIGUOUS", f"stream {index} has no string codec_type")
    if codec_type not in STREAM_TYPES:
        _fail("PROBE_OUTPUT_AMBIGUOUS", f"stream {index} has unsupported codec_type {codec_type!r}")
    return ProbeStream(
        stream_index=index,
        stream_type=codec_type,
        time_base=_parse_time_base(raw.get("time_base")),
        codec_name=_optional_str(raw.get("codec_name")),
        start_time=_optional_str(raw.get("start_time")),
        duration_ts=_optional_int(raw.get("duration_ts")),
        nb_frames=_optional_str(raw.get("nb_frames")),
        has_b_frames=_optional_int(raw.get("has_b_frames")),
    )


def _parse_streams(ffprobe_json: Mapping[str, Any]) -> tuple[ProbeStream, ...]:
    raw_streams = ffprobe_json.get("streams")
    if not isinstance(raw_streams, list) or not raw_streams:
        _fail("PROBE_OUTPUT_MALFORMED", "probe output has no non-empty streams array")
    seen: set[int] = set()
    return tuple(_parse_stream(raw, seen) for raw in raw_streams)


def _select_stream(streams: tuple[ProbeStream, ...], selected_stream_index: int | None) -> ProbeStream:
    """Select the video stream explicitly; never guess when the caller is silent."""
    if selected_stream_index is not None:
        if not isinstance(selected_stream_index, int) or isinstance(selected_stream_index, bool):
            _fail("SELECTED_STREAM_NOT_ELIGIBLE", f"selected stream {selected_stream_index!r} is not an integer")
        for stream in streams:
            if stream.stream_index == selected_stream_index:
                if stream.stream_type != "video":
                    _fail(
                        "SELECTED_STREAM_NOT_ELIGIBLE",
                        f"stream {selected_stream_index} is {stream.stream_type!r}, not video",
                    )
                return stream
        _fail("SELECTED_STREAM_NOT_ELIGIBLE", f"stream {selected_stream_index} does not exist")
    videos = [stream for stream in streams if stream.stream_type == "video"]
    if len(videos) != 1:
        _fail("AMBIGUOUS_STREAM", f"{len(videos)} video streams and no explicit selection")
    return videos[0]


class FfprobeAdapter:
    """One measured, fail-closed ``ffprobe`` invocation per source."""

    def __init__(
        self,
        *,
        ffprobe_path: str = "ffprobe",
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_stdout_bytes: int = DEFAULT_MAX_STDOUT_BYTES,
        max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    ) -> None:
        self._ffprobe_path = str(ffprobe_path)
        self._timeout_seconds = float(timeout_seconds)
        self._max_stdout_bytes = int(max_stdout_bytes)
        self._max_source_bytes = int(max_source_bytes)
        self._tool: ToolIdentity | None = None

    @property
    def tool(self) -> ToolIdentity:
        """Measured tool identity, taken once and cached."""
        if self._tool is None:
            self._tool = measure_tool(PROBE_ROLE, self._ffprobe_path)
        return self._tool

    def _snapshot(self, source: Path) -> SourceSnapshot:
        try:
            return snapshot_path(source, max_bytes=self._max_source_bytes)
        except SourceGuardError as exc:
            _fail(_probe_reason(exc), exc.detail)

    def _verify_unchanged(self, source: Path, snapshot: SourceSnapshot) -> None:
        try:
            verify_path(source, snapshot, max_bytes=self._max_source_bytes)
        except SourceGuardError as exc:
            _fail("SOURCE_MUTATED", exc.detail or exc.reason)

    def probe(
        self,
        path: str | Path,
        *,
        expected_digest: str | None = None,
        expected_byte_count: int | None = None,
        selected_stream_index: int | None = None,
    ) -> ProbeCapture:
        """Probe one source and return measured, digest-bound evidence."""
        tool = self.tool
        source = Path(path)
        snapshot = self._snapshot(source)
        if snapshot.byte_count == 0:
            _fail("SOURCE_UNREADABLE", f"empty source: {source}")
        source_digest = snapshot.digest
        if expected_digest is not None and source_digest != expected_digest:
            _fail("SOURCE_MUTATED", "source digest does not match the expected digest")
        if expected_byte_count is not None and snapshot.byte_count != expected_byte_count:
            _fail(
                "SOURCE_MUTATED",
                f"source byte count {snapshot.byte_count} does not match expected {expected_byte_count}",
            )

        resolved = Path(snapshot.path)
        argv = (tool.executable, *PROBE_COMMAND_OPTIONS, "-i", str(resolved))
        run = run_bounded(
            argv,
            timeout_seconds=self._timeout_seconds,
            max_stdout_bytes=self._max_stdout_bytes,
        )

        # The source must keep the same identity and bytes after the run: a
        # probe that observed a changing (or swapped) file is not evidence for
        # any revision, even when the replacement bytes are identical.
        self._verify_unchanged(resolved, snapshot)

        if run.timed_out:
            _fail("PROBE_TOOL_TIMEOUT", f"ffprobe exceeded {self._timeout_seconds}s")
        if run.stdout_truncated:
            _fail("PROBE_OUTPUT_TRUNCATED", f"stdout exceeded {self._max_stdout_bytes} bytes")
        if run.exit_code != 0:
            stderr_lines = run.stderr_text.strip().splitlines()
            detail = stderr_lines[0] if stderr_lines else "no stderr"
            _fail("PROBE_TOOL_FAILED", f"ffprobe exited {run.exit_code}: {detail}")

        try:
            ffprobe_json = json.loads(run.stdout)
        except json.JSONDecodeError as exc:
            _fail("PROBE_OUTPUT_MALFORMED", f"stdout is not JSON: {exc}")
        if not isinstance(ffprobe_json, dict):
            _fail("PROBE_OUTPUT_MALFORMED", "probe output is not a JSON object")

        streams = _parse_streams(ffprobe_json)
        selected = _select_stream(streams, selected_stream_index)
        if selected.time_base is None:
            _fail("TIME_BASE_INVALID", f"selected stream {selected.stream_index} reports no time base")

        raw_output_digest = digest_bytes(run.stdout)
        probe_ref = opaque_id(
            "probe",
            {
                "tool_identity_digest": tool.identity_digest,
                "raw_output_digest": raw_output_digest,
                "source_digest": source_digest,
                "argv": list(argv),
            },
        )
        evidence = ProbeEvidence(
            ffprobe_json=ffprobe_json,
            time_base=selected.time_base,
            probe_ref=probe_ref,
            failure=None,
        )
        return ProbeCapture(
            evidence=evidence,
            tool=tool,
            source_path=str(resolved),
            source_byte_count=snapshot.byte_count,
            source_digest=source_digest,
            raw_output_digest=raw_output_digest,
            exit_code=run.exit_code,
            duration_ms=run.duration_ms,
            streams=streams,
        )
