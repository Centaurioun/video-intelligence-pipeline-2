"""Measured, local-only ffprobe boundary for real-source FVS inputs.

This module is deliberately independent of the synthetic Gate-0 inventory
seam.  It records the bytes observed before and after a read-only ``ffprobe``
invocation, retains both the exact subprocess JSON and a canonical projection,
and refuses ambiguous or malformed timing evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Mapping

DEFAULT_PROBE_TIMEOUT_SECONDS = 600.0


class ProbeFailure(RuntimeError):
    """A measured probe failed in the compatibility/unit contract."""


class MeasuredProbeRefusal(ProbeFailure):
    """The real-source boundary refused an unsafe or unusable observation."""


@dataclass(frozen=True)
class RealSourceProbeBinding:
    source_path: Path
    source_revision_id: str
    source_sha256: str
    source_byte_count: int
    selected_stream_index: int
    timebase_num: int
    timebase_den: int
    ffprobe_json: Mapping[str, Any]
    probe_digest: str
    probe_artifact_ref: str
    raw_probe_artifact_ref: str
    canonical_probe_artifact_ref: str
    policy_identity: str | None = None
    source_locator: str | None = None
    snapshot_evidence: Mapping[str, Any] | None = None

    @property
    def time_base(self) -> tuple[int, int]:
        return self.timebase_num, self.timebase_den

    @property
    def probe_ref(self) -> str:
        """Compatibility name used by Gate-0 probe evidence consumers."""
        return self.probe_artifact_ref


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _refusal(reason: str, detail: str = "") -> MeasuredProbeRefusal:
    # Keep the original source-adapter vocabulary in the message while
    # exposing the more specific measured-boundary reason used by adversarial
    # callers.  Both names describe the same fail-closed outcome.
    compatibility = {
        "PROBE_NONZERO_EXIT": "SOURCE_PROBE_FAILED",
        "PROBE_INVALID_JSON": "SOURCE_PROBE_MALFORMED",
        "NO_VIDEO_STREAM": "NO_ELIGIBLE_VIDEO_STREAM",
    }.get(reason)
    label = f"{compatibility} {reason}" if compatibility else reason
    return MeasuredProbeRefusal(f"{label}{(': ' + detail) if detail else ''}")


def _read_source(path: Path) -> tuple[bytes, str]:
    try:
        data = path.read_bytes()
    except (OSError, ValueError) as exc:
        raise _refusal("LOCAL_SOURCE_REQUIRED", str(exc)) from exc
    return data, _sha256(data)


def _run_probe_process(argv: list[str], *, timeout_seconds: float | None) -> subprocess.CompletedProcess:
    """Kill and wait for FFprobe after a timeout or interruption while communicating."""
    process = subprocess.Popen(argv, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        raise
    except BaseException:
        process.kill()
        process.communicate()
        raise
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)


def _timebase(value: Any) -> tuple[int, int]:
    if isinstance(value, str):
        match = re.fullmatch(r"([0-9]+)\/([0-9]+)", value.strip())
        if not match:
            raise _refusal("INVALID_TIMEBASE")
        num, den = (int(match.group(1)), int(match.group(2)))
    elif isinstance(value, Mapping):
        num, den = value.get("num"), value.get("den")
        if (isinstance(num, bool) or not isinstance(num, int)
                or isinstance(den, bool) or not isinstance(den, int)):
            raise _refusal("INVALID_TIMEBASE")
    else:
        raise _refusal("INVALID_TIMEBASE")
    if num <= 0 or den <= 0:
        raise _refusal("INVALID_TIMEBASE")
    return num, den


def _select_stream(payload: Mapping[str, Any], selected: int | None) -> tuple[Mapping[str, Any], int]:
    streams = payload.get("streams")
    if not isinstance(streams, list):
        raise _refusal("NO_VIDEO_STREAM")
    videos = [stream for stream in streams if isinstance(stream, Mapping) and stream.get("codec_type") == "video"]
    if not videos:
        raise _refusal("NO_VIDEO_STREAM")
    if selected is None:
        if len(videos) != 1:
            raise _refusal("AMBIGUOUS_VIDEO_STREAM")
        stream = videos[0]
    else:
        stream = next((item for item in videos if item.get("index") == selected), None)
        if stream is None:
            raise _refusal("NO_VIDEO_STREAM")
    try:
        index = int(stream["index"])
    except (KeyError, TypeError, ValueError) as exc:
        raise _refusal("NO_VIDEO_STREAM") from exc
    return stream, index


def probe_real_source(
    source_path: str | Path,
    *,
    executable: str | Path,
    timeout_seconds: float | None = DEFAULT_PROBE_TIMEOUT_SECONDS,
    selected_stream_index: int | None = None,
    source_revision_id: str,
    policy_identity: str,
    run_dir: str | Path | None = None,
    runner: Callable[..., Any] | None = None,
    source_locator: str | None = None,
    snapshot_evidence: Mapping[str, Any] | None = None,
) -> RealSourceProbeBinding:
    """Probe one local path with explicit argv and persist measured evidence.

    ``runner`` is a test seam only.  The production default is
    :func:`subprocess.run` with shell execution disabled and captured output.
    No URL/protocol locator is ever passed to the subprocess.
    """
    raw_locator = str(source_path)
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", raw_locator) or "://" in raw_locator:
        raise _refusal("LOCAL_SOURCE_REQUIRED")
    path = Path(source_path)
    if not path.is_file():
        raise _refusal("LOCAL_SOURCE_REQUIRED")
    executable_path = Path(executable)
    # A bare executable name delegates resolution to the ambient PATH.  The
    # measured boundary accepts only a caller-provided path (absolute or
    # explicitly relative with at least one path component).
    if not str(executable).strip() or executable_path.name == str(executable).strip():
        raise _refusal("EXPLICIT_EXECUTABLE_REQUIRED")
    if not isinstance(source_revision_id, str) or not source_revision_id.strip():
        raise _refusal("SOURCE_REVISION_REQUIRED")
    if not isinstance(policy_identity, str) or not policy_identity.strip():
        raise _refusal("POLICY_IDENTITY_REQUIRED")
    if timeout_seconds is not None:
        valid_timeout = False
        if type(timeout_seconds) is int:
            valid_timeout = timeout_seconds > 0
        elif type(timeout_seconds) is float:
            valid_timeout = math.isfinite(timeout_seconds) and timeout_seconds > 0
        if not valid_timeout:
            raise _refusal("INVALID_PROBE_TIMEOUT")

    before, source_digest = _read_source(path)
    # Stream metadata alone cannot support a source-native interval.  Request
    # the presentation records in the same measured payload so downstream
    # preparation can bind its endpoints to observed frame/packet PTS rather
    # than inventing them from a nominal rate or semantic timestamp.
    argv = [
        str(executable_path), "-v", "error", "-of", "json",
        "-show_streams", "-show_format", "-show_frames", "-show_packets",
        str(path),
    ]
    try:
        if runner is not None:
            completed = runner(argv, shell=False, capture_output=True, check=False, timeout=timeout_seconds)
        elif timeout_seconds is None:
            completed = _run_probe_process(argv, timeout_seconds=timeout_seconds)
        else:
            completed = subprocess.run(
                argv, shell=False, capture_output=True, check=False, timeout=timeout_seconds
            )
    except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
        raise _refusal("PROBE_NONZERO_EXIT", str(exc)) from exc
    if getattr(completed, "returncode", 1) != 0:
        stderr = getattr(completed, "stderr", b"")
        detail = stderr.decode("utf-8", errors="replace") if isinstance(stderr, bytes) else str(stderr)
        raise _refusal("PROBE_NONZERO_EXIT", detail)

    stdout = getattr(completed, "stdout", b"")
    if isinstance(stdout, bytes):
        raw_probe = stdout
    elif isinstance(stdout, str):
        raw_probe = stdout.encode("utf-8")
    else:
        raise _refusal("PROBE_INVALID_JSON")
    try:
        payload = json.loads(raw_probe.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _refusal("PROBE_INVALID_JSON") from exc
    if not isinstance(payload, Mapping):
        raise _refusal("PROBE_INVALID_JSON")
    stream, stream_index = _select_stream(payload, selected_stream_index)
    num, den = _timebase(stream.get("time_base"))

    after, after_digest = _read_source(path)
    if after != before or after_digest != source_digest:
        raise _refusal("SOURCE_DIGEST_MISMATCH")

    canonical = (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    probe_digest = _sha256(canonical)
    root = Path(run_dir) if run_dir is not None else path.parent / ".vip-fvs-probes"
    artifact_root = root / "probe" / probe_digest
    artifact_root.mkdir(parents=True, exist_ok=True)
    raw_ref = artifact_root / "probe-raw.json"
    canonical_ref = artifact_root / "probe-canonical.json"
    raw_ref.write_bytes(raw_probe)
    canonical_ref.write_bytes(canonical)
    # Publication is part of the measured boundary: a source mutation during
    # artifact creation invalidates the entire observation and fails closed.
    published, published_digest = _read_source(path)
    if published != before or published_digest != source_digest:
        raise _refusal("SOURCE_DIGEST_MISMATCH")
    return RealSourceProbeBinding(
        source_path=path,
        source_revision_id=source_revision_id,
        source_sha256=source_digest,
        source_byte_count=len(after),
        selected_stream_index=stream_index,
        timebase_num=num,
        timebase_den=den,
        ffprobe_json=dict(payload),
        probe_digest=probe_digest,
        probe_artifact_ref=str(canonical_ref),
        raw_probe_artifact_ref=str(raw_ref),
        canonical_probe_artifact_ref=str(canonical_ref),
        policy_identity=policy_identity,
        source_locator=source_locator or str(path),
        snapshot_evidence=dict(snapshot_evidence) if snapshot_evidence is not None else None,
    )


def assert_source_unchanged(binding: RealSourceProbeBinding) -> None:
    """Re-hash a measured source and refuse if its bytes changed."""
    try:
        current = binding.source_path.read_bytes()
    except OSError as exc:
        raise _refusal("SOURCE_DIGEST_MISMATCH", str(exc)) from exc
    if len(current) != binding.source_byte_count or _sha256(current) != binding.source_sha256:
        raise _refusal("SOURCE_DIGEST_MISMATCH")
