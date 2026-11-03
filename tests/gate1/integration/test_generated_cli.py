"""Black-box CLI contract for the synthetic-only D05 harness."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

from gate1.artifacts import ARTIFACT_FILENAMES


REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON = Path("/Users/yusuf/Repos/video-intelligence-pipeline/.venv-gate0/bin/python")
CLAIM_TEXT = (
    "protocol readiness",
    "no real benchmark",
    "no winner",
    "no gate promotion",
)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{REPO_ROOT / 'src'}:{REPO_ROOT}"
    return subprocess.run(
        [str(PYTHON), "-m", "gate1.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_protocol_readiness_message(result: subprocess.CompletedProcess[str]) -> None:
    output = f"{result.stdout}\n{result.stderr}".casefold()
    for claim in CLAIM_TEXT:
        assert claim in output, f"missing required synthetic-only claim: {claim!r}\n{output}"


def test_generate_fixtures_emits_requested_generated_catalog(tmp_path):
    target = tmp_path / "generated-fixtures"

    result = run_cli("generate-fixtures", "--output-dir", str(target))

    assert result.returncode == 0, result.stderr
    assert target.is_dir()
    assert any(target.rglob("*.json")), "fixture catalog must contain JSON generated data"
    assert_protocol_readiness_message(result)


@pytest.mark.parametrize("case_id", ["positive_one_axis", "partial_coverage", "tie_no_superiority"])
def test_run_generated_writes_verifiable_artifact_closure_and_safe_claims(tmp_path, case_id):
    target = tmp_path / case_id

    result = run_cli(
        "run-generated", "--case-id", case_id, "--output-dir", str(target)
    )

    assert result.returncode == 0, result.stderr
    assert target.is_dir()
    assert set(path.name for path in target.iterdir()) == set(ARTIFACT_FILENAMES)
    assert_protocol_readiness_message(result)


def test_verify_generated_accepts_synthetic_run_and_states_readiness_only(tmp_path):
    target = tmp_path / "positive"
    run_result = run_cli(
        "run-generated", "--case-id", "positive_one_axis", "--output-dir", str(target)
    )
    assert run_result.returncode == 0, run_result.stderr

    result = run_cli("verify-generated", "--artifact-dir", str(target))

    assert result.returncode == 0, result.stderr
    assert_protocol_readiness_message(result)


def test_real_mode_refuses_before_creating_requested_output_path(tmp_path):
    target = tmp_path / "must-not-be-created"

    result = run_cli("run-generated", "--mode", "REAL", "--output-dir", str(target))

    assert result.returncode != 0
    output = f"{result.stdout}\n{result.stderr}".casefold()
    assert "real" in output and "refus" in output, output
    assert not target.exists(), "REAL refusal must happen before output-path creation"
    assert_protocol_readiness_message(result)
