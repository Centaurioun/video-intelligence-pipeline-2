"""Deterministic local tool identity for measured-media provenance.

Gate-0 claims about measured media must name the exact tool that produced the
measurement. An identity is derived from the resolved executable, the exact
``-version`` bytes (digested, not paraphrased), and the build configuration
line. The same tool build yields the same digest; a different build cannot
silently pass as the same tool.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate0.identity import digest_bytes, digest_json
from gate0.media.proc import ToolError, resolve_executable, run_bounded

_VERSION_ARGV = ("-version",)
_VERSION_TIMEOUT_SECONDS = 10.0
_VERSION_MAX_STDOUT_BYTES = 1024 * 1024
_VERSION_MAX_STDERR_BYTES = 8 * 1024


@dataclass(frozen=True)
class ToolIdentity:
    """Immutable, digest-bound identity of one local media tool build."""

    role: str
    executable: str
    version: str
    configuration: str
    version_stdout_digest: str
    identity_digest: str

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "executable": self.executable,
            "version": self.version,
            "configuration": self.configuration,
            "version_stdout_digest": self.version_stdout_digest,
            "identity_digest": self.identity_digest,
        }


def measure_tool(role: str, executable: str, *, timeout_seconds: float = _VERSION_TIMEOUT_SECONDS) -> ToolIdentity:
    """Measure and freeze the identity of one local media tool."""
    if not str(role).strip():
        raise ToolError("tool role is required")
    resolved = resolve_executable(executable)
    run = run_bounded(
        (resolved, *_VERSION_ARGV),
        timeout_seconds=timeout_seconds,
        max_stdout_bytes=_VERSION_MAX_STDOUT_BYTES,
        max_stderr_bytes=_VERSION_MAX_STDERR_BYTES,
    )
    if run.timed_out:
        raise ToolError(f"{role} -version timed out after {timeout_seconds}s")
    if run.stdout_truncated:
        raise ToolError(f"{role} -version output exceeded the capture bound")
    if run.exit_code != 0:
        detail = run.stderr_text.strip().splitlines()[0] if run.stderr_text.strip() else "no stderr"
        raise ToolError(f"{role} -version exited {run.exit_code}: {detail}")
    lines = [line.strip() for line in run.stdout_text.splitlines() if line.strip()]
    if not lines:
        raise ToolError(f"{role} -version produced no identity output")
    configuration = ""
    for line in lines[1:]:
        if line.startswith("configuration:"):
            configuration = line[len("configuration:"):].strip()
            break
    version_stdout_digest = digest_bytes(run.stdout)
    identity_digest = digest_json({
        "role": str(role),
        "executable": resolved,
        "version_stdout_digest": version_stdout_digest,
        "configuration": configuration,
    })
    return ToolIdentity(
        role=str(role),
        executable=resolved,
        version=lines[0],
        configuration=configuration,
        version_stdout_digest=version_stdout_digest,
        identity_digest=identity_digest,
    )
