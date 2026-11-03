"""S-14 negative-path coverage for the synthetic three-arm compatibility harness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import gate1.harness as harness
from gate1.harness import (
    CompatibilityError,
    build_generated_three_arm_inputs,
    build_three_arm_compat_report,
    run_generated_three_arm_case,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
REAL_REFUSAL = "REAL execution refused: current harness authority is synthetic-only"


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(REPO_ROOT / "src"), str(REPO_ROOT)))
    return subprocess.run(
        [sys.executable, "-m", "gate1.cli", *args],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True,
    )


def test_missing_case_id_is_a_cli_argument_error(tmp_path):
    output = tmp_path / "out"
    result = _run_cli("run-three-arm-generated", "--output-dir", str(output))
    assert result.returncode == 1
    assert "--case-id is required" in result.stderr
    assert not output.exists()


def test_missing_output_dir_is_a_cli_argument_error():
    result = _run_cli("run-three-arm-generated", "--case-id", "positive_one_axis")
    assert result.returncode == 1
    assert "--output-dir is required" in result.stderr


def test_unknown_execution_mode_is_a_cli_argument_error(tmp_path):
    output = tmp_path / "out"
    result = _run_cli("run-three-arm-generated", "--mode", "OPERATIONAL",
                      "--case-id", "positive_one_axis", "--output-dir", str(output))
    assert result.returncode == 2
    assert "invalid choice" in result.stderr
    assert not output.exists()


def test_real_mode_refusal_ordering_precedes_argument_and_output_work(tmp_path):
    """Refusal must happen before case/output validation and before any artifact write."""
    output = tmp_path / "refused"
    result = _run_cli("run-three-arm-generated", "--mode", "REAL", "--output-dir", str(output))
    assert result.returncode == 1
    assert REAL_REFUSAL in result.stderr
    assert "--case-id" not in result.stderr
    assert not output.exists()

    output.mkdir()
    result = _run_cli("run-three-arm-generated", "--mode", "REAL",
                      "--case-id", "positive_one_axis", "--output-dir", str(output))
    assert result.returncode == 1
    assert REAL_REFUSAL in result.stderr
    assert list(output.iterdir()) == []


def test_unknown_case_id_never_creates_the_output_directory(tmp_path):
    output = tmp_path / "out"
    result = _run_cli("run-three-arm-generated", "--case-id", "not_a_case",
                      "--output-dir", str(output))
    assert result.returncode == 1
    assert "not_a_case" in result.stderr
    assert not output.exists()


def test_ineligible_generated_case_branch_is_reachable_and_refuses(tmp_path, monkeypatch):
    """The dead-but-guarded ineligible branch must be exercised and refuse cleanly."""
    monkeypatch.setattr(harness, "_ALLOWED_CASES", frozenset())
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="generated case is not executable by this harness"):
        run_generated_three_arm_case("positive_one_axis", output)
    assert not output.exists()

    with pytest.raises(ValueError, match="generated case is not executable by this harness"):
        harness.build_generated_three_arm_inputs("positive_one_axis")


def test_contract_invalid_generated_case_names_the_contract_error():
    with pytest.raises(ValueError, match=r"generated case is not executable by this harness: invalid_multi_axis: .+"):
        build_generated_three_arm_inputs("invalid_multi_axis")


def test_b07_metric_states_reject_unknown_metric_ids():
    inputs = build_generated_three_arm_inputs("positive_one_axis")
    contract = inputs["contract"]
    contract["b07_metric_states"] = [
        {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE", "reason": "POOLED_GROUND_TRUTH"},
        {"metric_id": "map_at_10", "status": "NOT_COMPUTABLE", "reason": "METRIC_NOT_IMPLEMENTED"},
    ]
    with pytest.raises(CompatibilityError, match="B07 metric_id"):
        build_three_arm_compat_report(
            contract=contract,
            descriptors=inputs["descriptors"],
            policies=inputs["policies"],
            run_manifest=inputs["run_manifest"],
            rankings_by_arm=inputs["rankings_by_arm"],
            judgments=inputs["judgments"],
            failures=inputs["failures"],
            query_ids=inputs["query_ids"],
            fixture_id=inputs["fixture_id"],
            code_sha=harness.gate1_code_sha(),
            arm_derivations=harness.ARM_DERIVATIONS,
        )


def test_missing_b07_metric_states_is_rejected():
    inputs = build_generated_three_arm_inputs("positive_one_axis")
    contract = dict(inputs["contract"])
    contract.pop("b07_metric_states")
    with pytest.raises(CompatibilityError, match="b07_metric_states"):
        build_three_arm_compat_report(
            contract=contract,
            descriptors=inputs["descriptors"],
            policies=inputs["policies"],
            run_manifest=inputs["run_manifest"],
            rankings_by_arm=inputs["rankings_by_arm"],
            judgments=inputs["judgments"],
            failures=inputs["failures"],
            query_ids=inputs["query_ids"],
            fixture_id=inputs["fixture_id"],
            code_sha=harness.gate1_code_sha(),
            arm_derivations=harness.ARM_DERIVATIONS,
        )
