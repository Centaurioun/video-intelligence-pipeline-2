from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest

import gate0.launcher_attestation as launcher

ROOT = Path(__file__).resolve().parents[3]
CONFIG = json.loads((ROOT / "config/gate0/default.json").read_text())["sandbox"]
CONTEXT = {
    "repo_root": "/repo",
    "input_root": "/input",
    "output_root": "/output",
    "run_id": "run-1",
    "run_dir": "/output/run-1",
    "stage": "preflight",
}


def valid_argv(attestation_json: str = "{}") -> list[str]:
    return list(launcher.build_bwrap_argv(CONTEXT, attestation_json))


def assert_policy_rejects(argv: list[str], config: dict[str, object] | None = None) -> None:
    with pytest.raises(ValueError, match="SANDBOX_ATTESTATION"):
        launcher.validate_launch_policy(argv, CONTEXT, CONFIG if config is None else config)


def fake_binary_probe(path: Path) -> tuple[str, str]:
    return ("synthetic", "a" * 64)


def test_rejects_security_flag_drift():
    argv = valid_argv()
    argv.remove("--unshare-net")
    assert_policy_rejects(argv)


def test_rejects_mount_mode_drift():
    argv = valid_argv()
    i = argv.index("--ro-bind")
    argv[i] = "--bind"
    assert_policy_rejects(argv)


def test_rejects_mount_order_drift():
    argv = valid_argv()
    first = argv.index("--ro-bind")
    second = argv.index("--ro-bind", first + 1)
    first_triplet = argv[first:first + 3]
    second_triplet = argv[second:second + 3]
    argv[first:first + 3] = second_triplet
    argv[second:second + 3] = first_triplet
    assert_policy_rejects(argv)


def test_rejects_environment_binding_drift():
    argv = valid_argv()
    i = argv.index("PYTHONPATH")
    argv[i + 1] = "/unexpected"
    assert_policy_rejects(argv)


def test_rejects_interpreter_invocation_drift():
    argv = valid_argv()
    i = argv.index("/usr/bin/python3.11")
    argv[i] = "/usr/bin/python3.12"
    assert_policy_rejects(argv)


def test_rejects_cli_argument_shape_drift():
    argv = valid_argv()
    i = argv.index("--run")
    argv[i] = "--runtime-dir"
    assert_policy_rejects(argv)


def test_rejects_config_bound_argv_digest_drift():
    config = copy.deepcopy(CONFIG)
    config["argv_digest"] = "0" * 64
    assert_policy_rejects(valid_argv(), config)


def test_rejects_config_bound_mount_digest_drift():
    config = copy.deepcopy(CONFIG)
    config["mount_policy_digest"] = "0" * 64
    assert_policy_rejects(valid_argv(), config)


def test_prepare_validated_launch_binds_final_observed_digests_to_transported_attestation():
    final_argv, attestation = launcher.prepare_validated_launch(
        CONTEXT, CONFIG, binary_probe=fake_binary_probe
    )
    observed_argv, observed_mount = launcher.validate_launch_policy(
        final_argv, CONTEXT, CONFIG
    )
    assert observed_argv == attestation.argv_digest == CONFIG["argv_digest"]
    assert observed_mount == attestation.mount_policy_digest == CONFIG["mount_policy_digest"]


def test_prepare_validated_launch_rejects_attestation_digest_mismatch(monkeypatch):
    real_builder = launcher.build_launcher_attestation

    def bad_builder(*args, **kwargs):
        attestation = real_builder(*args, **kwargs)
        return replace(attestation, argv_digest="f" * 64)

    monkeypatch.setattr(launcher, "build_launcher_attestation", bad_builder)
    with pytest.raises(ValueError, match="SANDBOX_ATTESTATION"):
        launcher.prepare_validated_launch(CONTEXT, CONFIG, binary_probe=fake_binary_probe)


def test_launch_execs_exact_last_validated_final_argv(monkeypatch):
    validated: list[tuple[str, ...]] = []
    executed: list[tuple[str, ...]] = []
    real_validate = launcher.validate_launch_policy

    def recording_validate(actual_argv, context, sandbox_config):
        result = real_validate(actual_argv, context, sandbox_config)
        validated.append(tuple(actual_argv))
        return result

    def fake_execv(path: str, argv: list[str]) -> None:
        assert path == argv[0]
        executed.append(tuple(argv))

    monkeypatch.setattr(launcher, "validate_launch_policy", recording_validate)
    launcher.launch(
        CONTEXT,
        CONFIG,
        binary_probe=fake_binary_probe,
        execv=fake_execv,
    )

    assert len(validated) >= 2
    assert executed == [validated[-1]]
