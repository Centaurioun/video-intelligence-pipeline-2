"""Contract tests for the separate hosted Task 5 certification workflow."""

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
NODEIDS = ROOT / "tests/contracts/post_mega17_receipt_reconciliation_expected_nodeids.txt"
JUNIT_CHECKER = ROOT / "scripts/check_post_mega17_reconciliation_junit.py"
WORKFLOW = ROOT / ".github/workflows/post-mega17-reconciliation-contract.yml"
EXPECTED_NODEIDS_SHA256 = "f729b01a4233a8a58d226104df724dea8f728e76201414e41c3ef9c59bf96664"


def _node_ids():
    return NODEIDS.read_text(encoding="utf-8").splitlines()


def _junit_xml(node_ids, *, skipped=(), failed=(), errors=()):
    cases = []
    prefix = "tests.contracts.test_post_mega17_receipt_reconciliation"
    for node_id in node_ids:
        name = node_id.split("::", 1)[1]
        outcome = ""
        if node_id in skipped:
            outcome = '<skipped message="unexpected skip" />'
        elif node_id in failed:
            outcome = '<failure message="failed" />'
        elif node_id in errors:
            outcome = '<error message="error" />'
        cases.append(f'<testcase classname="{prefix}" name="{name}">{outcome}</testcase>')
    return (
        '<testsuites><testsuite name="pytest" tests="'
        + str(len(cases))
        + '" errors="'
        + str(len(errors))
        + '" failures="'
        + str(len(failed))
        + '" skipped="'
        + str(len(skipped))
        + '">'
        + "".join(cases)
        + "</testsuite></testsuites>"
    )


def _run_junit_check(tmp_path, xml):
    junit = tmp_path / "results.xml"
    junit.write_text(xml, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(JUNIT_CHECKER), "--junit", str(junit), "--expected-nodeids", str(NODEIDS)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_expected_node_population_is_the_observed_exact_baseline():
    raw = NODEIDS.read_bytes()
    node_ids = raw.decode("utf-8").splitlines()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_NODEIDS_SHA256
    assert len(node_ids) == 60
    assert len(set(node_ids)) == len(node_ids)
    assert all(node_id.startswith("tests/contracts/test_post_mega17_receipt_reconciliation.py::") for node_id in node_ids)


def test_workflow_is_separate_and_scoped_to_relevant_pull_request_changes():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pull_request:" in workflow
    for path in (
        ".github/workflows/post-mega17-reconciliation-contract.yml",
        "requirements/gate0.lock",
        "scripts/check_post_mega17_reconciliation_junit.py",
        "scripts/post_mega17_receipt_reconciliation.py",
        "tests/contracts/post_mega17_receipt_reconciliation_expected_nodeids.txt",
        "tests/contracts/test_post_mega17_receipt_reconciliation.py",
    ):
        assert f"- {path}" in workflow
    assert "vip-ai-studio-synthetic-ci.yml" not in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "fetch-depth: 0" in workflow
    assert "persist-credentials: false" in workflow
    assert "python-version: ['3.11', '3.14']" in workflow


def test_workflow_fails_closed_and_runs_the_real_contract_module():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert 'if [[ ! -f "$test_module" ]]; then' in workflow
    assert "python -m pytest --collect-only -q" in workflow
    assert "diff -u" in workflow
    assert "python -m pytest -q" in workflow
    assert "tests/contracts/test_post_mega17_receipt_reconciliation.py" in workflow
    assert "check_post_mega17_reconciliation_junit.py" in workflow
    assert "continue-on-error" not in workflow
    assert "if-no-files-found: error" in workflow
    assert "actions/upload-artifact@v4" in workflow


def test_junit_checker_accepts_the_exact_population_with_no_skips(tmp_path):
    result = _run_junit_check(tmp_path, _junit_xml(_node_ids()))
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "skipped", "failed", "error", "malformed"])
def test_junit_checker_rejects_population_or_outcome_mismatches(tmp_path, mutation):
    node_ids = _node_ids()
    xml = _junit_xml(node_ids)
    if mutation == "missing":
        xml = _junit_xml(node_ids[:-1])
    elif mutation == "duplicate":
        xml = _junit_xml(node_ids + [node_ids[0]])
    elif mutation == "skipped":
        xml = _junit_xml(node_ids, skipped=[node_ids[0]])
    elif mutation == "failed":
        xml = _junit_xml(node_ids, failed=[node_ids[0]])
    elif mutation == "error":
        xml = _junit_xml(node_ids, errors=[node_ids[0]])
    else:
        xml = "<testsuites><testsuite"
    result = _run_junit_check(tmp_path, xml)
    assert result.returncode != 0


def test_junit_checker_rejects_a_missing_junit_file(tmp_path):
    result = subprocess.run(
        [sys.executable, str(JUNIT_CHECKER), "--junit", str(tmp_path / "missing.xml"), "--expected-nodeids", str(NODEIDS)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
