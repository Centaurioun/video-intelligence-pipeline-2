"""Synthetic/local preflight gate and sandbox attestation contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
import json
import shutil
import subprocess

from gate0.identity import digest_json
from gate0.policy import PolicyDecision, PolicyDenied, PolicyUseContext, require_allow


@dataclass(frozen=True)
class SandboxAttestation:
    bwrap_path: str
    bwrap_version: str
    bwrap_digest: str
    interpreter_path: str
    interpreter_version: str
    interpreter_digest: str
    read_only_mounts: tuple[str, ...]
    writable_mounts: tuple[str, ...]
    clearenv: bool
    net_unshared: bool
    child_network_sentinel: bool
    argv_digest: str = ""
    mount_policy_digest: str = ""

    @classmethod
    def synthetic(cls, digest: str) -> "SandboxAttestation":
        from gate0.launcher_attestation import expected_argv_digest, expected_mount_policy_digest
        return cls("/usr/bin/bwrap", "synthetic", digest, "/usr/bin/python3.11", "3.11.9",
                   digest, ("REPO_ROOT", "INPUT_ROOT", "/usr", "/lib", "/lib64", "/etc/ld.so.cache"),
                   ("OUTPUT_ROOT",), True, True, True, expected_argv_digest(), expected_mount_policy_digest())

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "SandboxAttestation":
        required = ("bwrap_path", "bwrap_version", "bwrap_digest", "interpreter_path",
                    "interpreter_version", "interpreter_digest", "read_only_mounts",
                    "writable_mounts", "clearenv", "net_unshared", "child_network_sentinel",
                    "argv_digest", "mount_policy_digest")
        if any(key not in value for key in required) or set(value) != set(required):
            raise ValueError("SANDBOX_ATTESTATION")
        return cls(str(value["bwrap_path"]), str(value["bwrap_version"]), str(value["bwrap_digest"]),
                   str(value["interpreter_path"]), str(value["interpreter_version"]),
                   str(value["interpreter_digest"]), tuple(value["read_only_mounts"]),
                   tuple(value["writable_mounts"]), bool(value["clearenv"]),
                   bool(value["net_unshared"]), bool(value["child_network_sentinel"]),
                   str(value["argv_digest"]), str(value["mount_policy_digest"]))

    def matches(self, expected: dict[str, Any]) -> bool:
        return self.to_dict() == {key: expected[key] for key in self.to_dict()}

    def to_dict(self) -> dict[str, Any]:
        return {"bwrap_path": self.bwrap_path, "bwrap_version": self.bwrap_version,
                "bwrap_digest": self.bwrap_digest, "interpreter_path": self.interpreter_path,
                "interpreter_version": self.interpreter_version, "interpreter_digest": self.interpreter_digest,
                "read_only_mounts": list(self.read_only_mounts), "writable_mounts": list(self.writable_mounts),
                "clearenv": self.clearenv, "net_unshared": self.net_unshared,
                "child_network_sentinel": self.child_network_sentinel,
                "argv_digest": self.argv_digest, "mount_policy_digest": self.mount_policy_digest}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observe_sandbox(config: dict[str, Any], *, argv: tuple[str, ...] = (), mount_policy: tuple[str, ...] = ()) -> tuple[SandboxAttestation | None, str | None]:
    """Observe the launcher boundary; absence is a block, never a fallback."""
    bwrap = Path(str(config.get("bwrap_path", "/usr/bin/bwrap")))
    interpreter = Path(str(config.get("interpreter_path", "/usr/bin/python3.11")))
    if not (bwrap.is_file() and interpreter.is_file()):
        return None, "SANDBOX_ATTESTATION"
    try:
        bwrap_version = subprocess.run([str(bwrap), "--version"], check=True, capture_output=True, text=False).stdout.decode("utf-8", "replace").strip()
        interpreter_version = subprocess.run([str(interpreter), "--version"], check=True, capture_output=True, text=False).stdout.decode("utf-8", "replace").strip().removeprefix("Python ")
        ro = tuple(config.get("read_only_mounts", ()))
        writable = tuple(config.get("writable_mounts", ()))
        policy = tuple(mount_policy) or ro + writable
        attestation = SandboxAttestation(str(bwrap), bwrap_version, _sha256_file(bwrap), str(interpreter), interpreter_version,
            _sha256_file(interpreter), ro, writable, bool(config.get("clearenv")), bool(config.get("net_unshared")),
            bool(config.get("child_network_sentinel")), digest_json(list(argv)), digest_json(list(policy)))
        return attestation, None
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None, "SANDBOX_ATTESTATION"


@dataclass(frozen=True)
class PreflightResult:
    stage_status: str
    exit_code: int
    attempt_id: str
    failure_refs: tuple[str, ...]
    policy_decisions: tuple[PolicyDecision, ...]
    egress_events: tuple[object, ...]
    sandbox_attestation: SandboxAttestation | None
    preflight_status: str
    decision_digests: tuple[str, ...]


def _result(status: str, code: int, failures: tuple[str, ...], discovery, processing, sandbox, attempt_id: str, egress_events=()):
    decisions = tuple(item for item in (discovery, processing) if item is not None)
    return PreflightResult(status, code, attempt_id, failures, decisions, tuple(egress_events), sandbox, status,
                           tuple(digest_json(d.to_dict()) for d in decisions))


def _coerce_decision(value: PolicyDecision | dict[str, Any] | None) -> PolicyDecision | None:
    if value is None or isinstance(value, PolicyDecision):
        return value
    if isinstance(value, dict):
        try:
            return PolicyDecision(**value)
        except Exception as exc:
            raise PolicyDenied("malformed policy decision") from exc
    raise PolicyDenied("malformed policy decision")


def preflight(*, revision_id: str, discovery_decision: PolicyDecision | None,
              processing_decision: PolicyDecision | None,
              expected_egress_manifest_digest: str, sandbox: SandboxAttestation | None,
              output_root: Path | None = None, attempt_id: str = "attempt_preflight",
              now: str = "2026-09-12T12:00:00Z",
              sandbox_expected: dict[str, Any] | None = None,
              sandbox_config: dict[str, Any] | None = None,
              sandbox_attestation_json: str | None = None,
              sandbox_observer=None, egress_guard=None) -> PreflightResult:
    try:
        discovery_decision = _coerce_decision(discovery_decision)
        processing_decision = _coerce_decision(processing_decision)
    except PolicyDenied:
        return _result("BLOCKED_POLICY", 20, ("POLICY_DENIED",), None, None, sandbox, attempt_id)
    if sandbox_attestation_json is not None:
        try:
            from gate0.launcher_attestation import decode_attestation
            sandbox = decode_attestation(sandbox_attestation_json)
        except Exception:
            return _result("BLOCKED_PREREQUISITE", 20, ("SANDBOX_ATTESTATION",), discovery_decision, processing_decision, None, attempt_id)
    if sandbox_config is not None:
        try:
            observed = sandbox_observer(sandbox_config) if sandbox_observer is not None else observe_sandbox(sandbox_config)[0]
            if observed is None:
                return _result("BLOCKED_PREREQUISITE", 20, ("SANDBOX_ATTESTATION",), discovery_decision, processing_decision, None, attempt_id)
            sandbox = observed
            if not sandbox.matches(sandbox_config):
                return _result("BLOCKED_PREREQUISITE", 20, ("SANDBOX_ATTESTATION",), discovery_decision, processing_decision, sandbox, attempt_id)
        except Exception:
            return _result("BLOCKED_PREREQUISITE", 20, ("SANDBOX_ATTESTATION",), discovery_decision, processing_decision, None, attempt_id)
    if sandbox is None or not (sandbox.clearenv and sandbox.net_unshared and sandbox.child_network_sentinel):
        return _result("BLOCKED_PREREQUISITE", 20, ("SANDBOX_ATTESTATION",), discovery_decision, processing_decision, sandbox, attempt_id)
    if sandbox_expected is not None and not sandbox.matches(sandbox_expected):
        return _result("BLOCKED_PREREQUISITE", 20, ("SANDBOX_ATTESTATION",), discovery_decision, processing_decision, sandbox, attempt_id)
    egress_events = ()
    if egress_guard is not None:
        try:
            egress_events = egress_guard.child_network_sentinel("run_preflight", attempt_id,
                processing_decision.policy_decision_id if processing_decision else "policy_unknown",
                expected_egress_manifest_digest, now)
        except Exception:
            return _result("BLOCKED_PREREQUISITE", 20, ("EGRESS_SENTINEL",), discovery_decision, processing_decision, sandbox, attempt_id)
    try:
        require_allow(PolicyUseContext(revision_id, "PROCESS", "PROCESS", "window_sample_manifest",
                                       "local_only", "DERIVED_REPLAYABLE", now,
                                       expected_egress_manifest_digest, discovery_decision, processing_decision))
    except (PolicyDenied, ValueError, TypeError):
        return _result("BLOCKED_POLICY", 20, ("POLICY_DENIED",), discovery_decision, processing_decision, sandbox, attempt_id, egress_events)
    return _result("SUCCEEDED", 0, (), discovery_decision, processing_decision, sandbox, attempt_id, egress_events)
