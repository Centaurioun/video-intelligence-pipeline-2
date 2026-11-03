from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator
import pytest

from tests.gate1.fixtures.three_arm_compat import (
    ARMS,
    B07_MARKERS,
    EXPECTED_CASES,
    PAIR_ORDER,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_SCHEMA = REPO_ROOT / "schemas/gate1_compat_v2/three_arm_compat_report.json"
REPORT_FILENAME = "three_arm_compat_report.json"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((str(REPO_ROOT / "src"), str(REPO_ROOT)))
    return subprocess.run(
        [sys.executable, "-m", "gate1.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _read_report(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(report)
    return report


@pytest.mark.parametrize("case_id", tuple(EXPECTED_CASES))
def test_three_arm_generated_cli_writes_deterministic_adapter_report(tmp_path, case_id):
    first = tmp_path / "first"
    result = run_cli(
        "run-three-arm-generated", "--case-id", case_id,
        "--output-dir", str(first),
    )

    assert result.returncode == 0, result.stderr
    report_path = first / REPORT_FILENAME
    report = _read_report(report_path)
    expected = EXPECTED_CASES[case_id]
    pairs = report["pairwise_evaluations"]
    assert tuple(tuple(row["arm_ids"]) for row in pairs) == PAIR_ORDER
    assert tuple(row["benchmark_status"] for row in pairs) == expected["statuses"]
    assert tuple(row["failure_class"] for row in pairs) == expected["failure_classes"]
    assert tuple(row["primary_value"] for row in pairs) == expected["primary_values"]
    assert report["b07_metric_states"] == list(B07_MARKERS)
    assert report["winner_status"] == "NOT_EVALUATED"

    second = tmp_path / "second"
    repeated = run_cli(
        "run-three-arm-generated", "--case-id", case_id,
        "--output-dir", str(second),
    )
    assert repeated.returncode == 0, repeated.stderr
    assert report_path.read_bytes() == (second / REPORT_FILENAME).read_bytes()


def test_partial_coverage_reports_arm_attributed_omission_counts(tmp_path):
    output = tmp_path / "partial"
    result = run_cli(
        "run-three-arm-generated", "--case-id", "partial_coverage",
        "--output-dir", str(output),
    )
    assert result.returncode == 0, result.stderr
    report = _read_report(output / REPORT_FILENAME)
    first_pair = report["pairwise_evaluations"][0]
    assert first_pair["coverage"][f"{ARMS[0]}::SELECTED"] == 2
    assert first_pair["coverage"][f"{ARMS[1]}::SELECTED"] == 1
    assert first_pair["coverage"][f"{ARMS[1]}::OMITTED"] == 1
    assert first_pair["failure_class"] == "COVERAGE_INCOMPLETE"


@pytest.mark.parametrize("case_id", ["invalid_multi_axis", "missing_generated_case"])
def test_malformed_or_missing_generated_case_fails_before_output_creation(tmp_path, case_id):
    output = tmp_path / case_id
    result = run_cli(
        "run-three-arm-generated", "--case-id", case_id,
        "--output-dir", str(output),
    )
    assert result.returncode != 0
    assert "invalid choice" not in result.stderr
    if case_id == "invalid_multi_axis":
        assert "undeclared material axis" in result.stderr
    else:
        assert case_id in result.stderr
    assert not output.exists()


def test_three_arm_real_mode_refuses_before_case_validation_or_output_creation(tmp_path):
    output = tmp_path / "must-not-be-created"
    result = run_cli(
        "run-three-arm-generated", "--mode", "REAL",
        "--case-id", "missing_generated_case", "--output-dir", str(output),
    )
    assert result.returncode != 0
    assert "REAL" in result.stderr and "refused" in result.stderr
    assert not output.exists()
