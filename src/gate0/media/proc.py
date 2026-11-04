"""Bounded, fail-closed subprocess execution for local media tool adapters.

Gate-0 may read generated local media through host tools (``ffprobe`` /
``ffmpeg``). The adapter layer must never block indefinitely, never capture
unbounded output, never inherit an ambient environment, and never guess when a
tool fails. This module is the single bounded-execution seam: callers receive
the exact resolved argv, the exact captured bytes, the exact exit code, and
explicit truncation/timeout flags, and decide themselves whether the result is
usable evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
import subprocess
import threading
import time
from typing import Mapping, Sequence

DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_STDOUT_BYTES = 16 * 1024 * 1024
DEFAULT_MAX_STDERR_BYTES = 64 * 1024
_READ_CHUNK = 64 * 1024
_JOIN_SECONDS = 5.0


class ToolError(RuntimeError):
    """Base class for local media tool failures."""


class ToolNotFound(ToolError):
    """The requested executable does not resolve to an executable host file."""


class ToolLaunchError(ToolError):
    """The process could not be spawned."""


@dataclass(frozen=True)
class ToolRun:
    """Exact, bounded observation of one child process invocation."""

    argv: tuple[str, ...]
    exit_code: int
    stdout: bytes
    stderr: bytes
    duration_ms: int
    stdout_truncated: bool
    stderr_truncated: bool
    timed_out: bool

    @property
    def stdout_text(self) -> str:
        return self.stdout.decode("utf-8", "replace")

    @property
    def stderr_text(self) -> str:
        return self.stderr.decode("utf-8", "replace")


def sanitized_environment(overrides: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return the only environment a media tool child may observe.

    Locale and timezone are pinned so tool output is byte-stable, and every
    other ambient variable (credentials included) is dropped by construction.
    """
    environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
    }
    if overrides:
        environment.update({str(key): str(value) for key, value in overrides.items()})
    return environment


def resolve_executable(candidate: str) -> str:
    """Resolve a declared tool reference to one absolute executable path."""
    reference = str(candidate).strip()
    if not reference:
        raise ToolNotFound("empty tool reference")
    if os.sep in reference or (os.altsep is not None and os.altsep in reference):
        resolved = os.path.realpath(reference)
        if not (os.path.isfile(resolved) and os.access(resolved, os.X_OK)):
            raise ToolNotFound(f"{reference} is not an executable file")
        return resolved
    discovered = shutil.which(reference)
    if discovered is None:
        raise ToolNotFound(f"{reference} is not on PATH")
    resolved = os.path.realpath(discovered)
    if not (os.path.isfile(resolved) and os.access(resolved, os.X_OK)):
        raise ToolNotFound(f"{reference} resolved to a non-executable file")
    return resolved


def _pump(stream, buffer: bytearray, cap: int, truncated: list[bool]) -> None:
    while True:
        chunk = stream.read(_READ_CHUNK)
        if not chunk:
            return
        room = cap - len(buffer)
        if room > 0:
            buffer.extend(chunk[:room])
        if len(chunk) > room:
            truncated[0] = True


def run_bounded(
    argv: Sequence[str],
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_stdout_bytes: int = DEFAULT_MAX_STDOUT_BYTES,
    max_stderr_bytes: int = DEFAULT_MAX_STDERR_BYTES,
    env: Mapping[str, str] | None = None,
    cwd: str | os.PathLike[str] | None = None,
) -> ToolRun:
    """Run one bounded child process and return its exact observed result."""
    if not argv:
        raise ToolError("empty argv")
    if not timeout_seconds > 0:
        raise ToolError("timeout_seconds must be positive")
    if max_stdout_bytes <= 0 or max_stderr_bytes <= 0:
        raise ToolError("output caps must be positive")
    resolved = resolve_executable(str(argv[0]))
    command = (resolved, *[str(argument) for argument in argv[1:]])
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            list(command),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(sanitized_environment() if env is None else env),
            cwd=None if cwd is None else os.fspath(cwd),
            close_fds=True,
        )
    except OSError as exc:  # pragma: no cover - platform dependent
        raise ToolLaunchError(f"cannot launch {resolved}: {exc}") from exc
    stdout_buffer = bytearray()
    stderr_buffer = bytearray()
    stdout_truncated = [False]
    stderr_truncated = [False]
    threads = (
        threading.Thread(target=_pump, args=(process.stdout, stdout_buffer, max_stdout_bytes, stdout_truncated), daemon=True),
        threading.Thread(target=_pump, args=(process.stderr, stderr_buffer, max_stderr_bytes, stderr_truncated), daemon=True),
    )
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        exit_code = process.wait(timeout=float(timeout_seconds))
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        try:
            exit_code = process.wait(timeout=_JOIN_SECONDS)
        except subprocess.TimeoutExpired:  # pragma: no cover - defensive
            exit_code = -9
    for thread in threads:
        thread.join(timeout=_JOIN_SECONDS)
    duration_ms = int((time.monotonic() - started) * 1000)
    for stream in (process.stdout, process.stderr):
        try:
            stream.close()
        except OSError:  # pragma: no cover - defensive
            pass
    return ToolRun(
        argv=command,
        exit_code=int(exit_code),
        stdout=bytes(stdout_buffer),
        stderr=bytes(stderr_buffer),
        duration_ms=duration_ms,
        stdout_truncated=bool(stdout_truncated[0]),
        stderr_truncated=bool(stderr_truncated[0]),
        timed_out=timed_out,
    )
