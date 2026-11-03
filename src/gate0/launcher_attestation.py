"""Single-source launcher policy materialisation and sandbox attestation transport."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

from gate0.canonical_json import canonical_text
from gate0.identity import digest_json, opaque_id, validate_digest

ARGV_TEMPLATE = (
    "/usr/bin/bwrap", "--die-with-parent", "--unshare-net", "--clearenv",
    "--ro-bind", "REPO_ROOT", "REPO_ROOT", "--ro-bind", "INPUT_ROOT", "INPUT_ROOT",
    "--bind", "OUTPUT_ROOT", "OUTPUT_ROOT", "--dev", "/dev", "--proc", "/proc",
    "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib",
    "--ro-bind", "/lib64", "/lib64", "--ro-bind", "/etc/ld.so.cache", "/etc/ld.so.cache",
    "--chdir", "REPO_ROOT", "--setenv", "PATH", "/usr/bin:/bin",
    "--setenv", "PYTHONNOUSERSITE", "1", "--setenv", "PYTHONPATH", "REPO_ROOT/src",
    "--setenv", "GATE0_CHILD_NETWORK_SENTINEL", "1", "--setenv",
    "GATE0_SANDBOX_ATTESTATION_JSON", "ATTESTATION_JSON", "--", "/usr/bin/python3.11",
    "-m", "gate0.cli", "STAGE", "--run", "RUN_DIR", "--config",
    "config/gate0/default.json", "--input-root", "INPUT_ROOT", "--output-root",
    "OUTPUT_ROOT", "--run-id", "RUN_ID",
)
MOUNT_POLICY = (
    {"mode": "ro", "source": "REPO_ROOT", "target": "REPO_ROOT"},
    {"mode": "ro", "source": "INPUT_ROOT", "target": "INPUT_ROOT"},
    {"mode": "rw", "source": "OUTPUT_ROOT", "target": "OUTPUT_ROOT"},
    {"mode": "dev", "target": "/dev"}, {"mode": "proc", "target": "/proc"},
    {"mode": "ro", "source": "/usr", "target": "/usr"},
    {"mode": "ro", "source": "/lib", "target": "/lib"},
    {"mode": "ro", "source": "/lib64", "target": "/lib64"},
    {"mode": "ro", "source": "/etc/ld.so.cache", "target": "/etc/ld.so.cache"},
)

def expected_argv_digest() -> str:
    return digest_json(ARGV_TEMPLATE)

def expected_mount_policy_digest() -> str:
    return digest_json(MOUNT_POLICY)

def build_bwrap_argv(context: Mapping[str, object], attestation_json: str) -> tuple[str, ...]:
    """Materialise the only supported launcher shape from run inputs."""
    required = ("repo_root", "input_root", "output_root", "run_id", "run_dir", "stage")
    if any(key not in context or not str(context[key]) for key in required):
        raise ValueError("launcher context is incomplete")
    values = {"REPO_ROOT": str(context["repo_root"]), "INPUT_ROOT": str(context["input_root"]),
              "OUTPUT_ROOT": str(context["output_root"]), "RUN_ID": str(context["run_id"]),
              "RUN_DIR": str(context["run_dir"]), "STAGE": str(context["stage"]),
              "ATTESTATION_JSON": attestation_json,
              "REPO_ROOT/src": str(context["repo_root"]) + "/src"}
    return tuple(values.get(token, token) for token in ARGV_TEMPLATE)

def normalize_actual_argv(actual_argv: tuple[str, ...] | list[str], context: Mapping[str, object]) -> tuple[str, ...]:
    """Normalize only dynamic slots at their contract-defined positions.

    Dynamic values are deliberately not replaced globally: a run value appearing
    in a flag or a literal argument is an unexpected launcher shape and must
    remain visible to the exact-template check.
    """
    if len(actual_argv) != len(ARGV_TEMPLATE):
        raise ValueError("SANDBOX_ATTESTATION")
    dynamic = {"REPO_ROOT": str(context["repo_root"]), "INPUT_ROOT": str(context["input_root"]),
               "OUTPUT_ROOT": str(context["output_root"]), "RUN_ID": str(context["run_id"]),
               "RUN_DIR": str(context["run_dir"]), "STAGE": str(context["stage"])}
    normalized: list[str] = []
    for actual, expected in zip(actual_argv, ARGV_TEMPLATE):
        actual = str(actual)
        if expected in dynamic:
            if actual != dynamic[expected]:
                raise ValueError("SANDBOX_ATTESTATION")
            normalized.append(expected)
        elif expected == "REPO_ROOT/src":
            if actual != dynamic["REPO_ROOT"] + "/src":
                raise ValueError("SANDBOX_ATTESTATION")
            normalized.append(expected)
        elif expected == "ATTESTATION_JSON":
            if not actual:
                raise ValueError("SANDBOX_ATTESTATION")
            normalized.append(expected)
        elif actual != expected:
            raise ValueError("SANDBOX_ATTESTATION")
        else:
            normalized.append(expected)
    return tuple(normalized)

def derive_normalized_mount_policy(actual_argv: tuple[str, ...] | list[str], context: Mapping[str, object]) -> tuple[dict[str, str], ...]:
    norm = normalize_actual_argv(tuple(actual_argv), context)
    mounts: list[dict[str, str]] = []
    i = 0
    while i < len(norm):
        if norm[i] in ("--ro-bind", "--bind"):
            if i + 2 >= len(norm): raise ValueError("malformed mount")
            mounts.append({"mode": "ro" if norm[i] == "--ro-bind" else "rw", "source": norm[i+1], "target": norm[i+2]}); i += 3
        elif norm[i] in ("--dev", "--proc"):
            if i + 1 >= len(norm): raise ValueError("malformed mount")
            mounts.append({"mode": norm[i][2:], "target": norm[i+1]}); i += 2
        else: i += 1
    return tuple(mounts)

def validate_launch_policy(actual_argv: tuple[str, ...] | list[str], context: Mapping[str, object], sandbox_config: Mapping[str, object]) -> tuple[str, str]:
    normalized = normalize_actual_argv(tuple(actual_argv), context)
    if normalized != ARGV_TEMPLATE: raise ValueError("SANDBOX_ATTESTATION")
    mounts = derive_normalized_mount_policy(tuple(actual_argv), context)
    if mounts != MOUNT_POLICY: raise ValueError("SANDBOX_ATTESTATION")
    argv_digest, mount_digest = digest_json(normalized), digest_json(mounts)
    if sandbox_config.get("argv_digest") != argv_digest or sandbox_config.get("mount_policy_digest") != mount_digest:
        raise ValueError("SANDBOX_ATTESTATION")
    return argv_digest, mount_digest

def build_launcher_attestation(
    sandbox_config: Mapping[str, object], *, argv_digest: str, mount_policy_digest: str,
    binary_probe: Callable[[Path], tuple[str, str]]
) -> Any:
    from gate0.stages.preflight import SandboxAttestation
    if (sandbox_config.get("argv_digest") != argv_digest
            or sandbox_config.get("mount_policy_digest") != mount_policy_digest):
        raise ValueError("SANDBOX_ATTESTATION")
    bp, bd = binary_probe(Path(str(sandbox_config["bwrap_path"])))
    ip, idigest = binary_probe(Path(str(sandbox_config["interpreter_path"])))
    return SandboxAttestation(str(sandbox_config["bwrap_path"]), bp, bd, str(sandbox_config["interpreter_path"]), ip, idigest,
      tuple(sandbox_config["read_only_mounts"]), tuple(sandbox_config["writable_mounts"]), bool(sandbox_config["clearenv"]),
      bool(sandbox_config["net_unshared"]), bool(sandbox_config["child_network_sentinel"]),
      argv_digest, mount_policy_digest)


def prepare_validated_launch(
    context: Mapping[str, object], sandbox_config: Mapping[str, object], *,
    binary_probe: Callable[[Path], tuple[str, str]],
) -> tuple[tuple[str, ...], Any]:
    """Validate the final launcher and bind its observed policy to attestation."""
    placeholder_argv = build_bwrap_argv(context, "ATTESTATION_JSON")
    observed_argv_digest, observed_mount_digest = validate_launch_policy(
        placeholder_argv, context, sandbox_config
    )
    attestation = build_launcher_attestation(
        sandbox_config,
        argv_digest=observed_argv_digest,
        mount_policy_digest=observed_mount_digest,
        binary_probe=binary_probe,
    )
    final_argv = build_bwrap_argv(context, encode_attestation(attestation))
    final_argv_digest, final_mount_digest = validate_launch_policy(
        final_argv, context, sandbox_config
    )
    if not (final_argv_digest == attestation.argv_digest == sandbox_config.get("argv_digest")):
        raise ValueError("SANDBOX_ATTESTATION")
    if not (final_mount_digest == attestation.mount_policy_digest == sandbox_config.get("mount_policy_digest")):
        raise ValueError("SANDBOX_ATTESTATION")
    return final_argv, attestation


def launch(
    context: Mapping[str, object], sandbox_config: Mapping[str, object], *,
    binary_probe: Callable[[Path], tuple[str, str]],
    execv: Callable[[str, list[str]], object],
) -> None:
    """Execute exactly the final argv that passed policy validation."""
    final_argv, _attestation = prepare_validated_launch(
        context, sandbox_config, binary_probe=binary_probe
    )
    execv(final_argv[0], list(final_argv))

def encode_attestation(attestation: Any) -> str:
    return canonical_text(attestation.to_dict(), trailing_lf=False)

def decode_attestation(value: str) -> Any:
    from gate0.stages.preflight import SandboxAttestation
    if not isinstance(value, str): raise ValueError("SANDBOX_ATTESTATION")
    try: obj = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc: raise ValueError("SANDBOX_ATTESTATION") from exc
    if canonical_text(obj, trailing_lf=False) != value: raise ValueError("SANDBOX_ATTESTATION")
    att = SandboxAttestation.from_mapping(obj)
    if att.argv_digest != expected_argv_digest() or att.mount_policy_digest != expected_mount_policy_digest(): raise ValueError("SANDBOX_ATTESTATION")
    return att

def sentinel_ledger_events(*, run_id: str, attempt_id: str, policy_decision_id: str, egress_manifest_digest: str, now: str) -> tuple[dict[str, object], ...]:
    validate_digest(egress_manifest_digest)
    return tuple({"event_id": opaque_id("egress", {"attempt": attempt_id, "tool": "child-network-sentinel", "destination": d, "timestamp": now}),
      "attempt_id": attempt_id, "policy_decision_id": policy_decision_id, "tool_identity": "child-network-sentinel", "timestamp": now,
      "decision": "DENY", "outcome": "BLOCKED", "destination": d, "protocol": p, "attempted_bytes": 1, "transmitted_bytes": 0, "payload": None}
      for p, d in (("DNS", "dns://sentinel.invalid"), ("HTTP_PROXY", "http://proxy.invalid"), ("PROVIDER", "https://provider.invalid"), ("LOOPBACK", "http://127.0.0.1")))

def main() -> None:
    """Materialise and immediately execute the validated final launcher."""
    import os
    import sys
    if len(sys.argv) != 7:
        raise SystemExit(20)
    repo, inp, out, run_id, stage, run_dir = sys.argv[1:]
    config_path = Path(repo) / "config/gate0/default.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))["sandbox"]
    context = {"repo_root": repo, "input_root": inp, "output_root": out, "run_id": run_id, "stage": stage, "run_dir": run_dir}
    def probe(path: Path) -> tuple[str, str]:
        import hashlib
        if not path.is_file(): raise OSError(str(path))
        version = os.popen(f"{path} --version 2>/dev/null").read().splitlines()[0] if os.access(path, os.X_OK) else "NOT_OBSERVED"
        return version.removeprefix("Python "), hashlib.sha256(path.read_bytes()).hexdigest()
    launch(context, config, binary_probe=probe, execv=os.execv)

if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print("SANDBOX_ATTESTATION", file=sys.stderr)
        raise SystemExit(20) from exc
