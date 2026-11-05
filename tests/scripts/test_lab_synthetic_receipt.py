from __future__ import annotations

import copy
from pathlib import Path

import pytest

from scripts.lab_synthetic_receipt import build_receipt, validate_receipt


def valid_receipt() -> dict[str, object]:
    nodes = [
        f"tests.vip_lab.{suite}::test_example"
        for suite in (
            "test_mega17_editorial_readiness",
            "test_mega17_end_to_end",
            "test_mega17_gate0_readiness",
            "test_mega17_integration_readiness",
            "test_mega17_release_readiness",
            "test_mega17_source_readiness",
        )
    ]
    return {
        "schema_version": "lab-synthetic-receipt.v1",
        "lane_id": "lab-synthetic",
        "scope": "LAB_SYNTHETIC_ONLY",
        "repository": "Centaurioun/video-intelligence-pipeline-2",
        "ref": "refs/pull/7/merge",
        "commit_sha": "a" * 40,
        "tree_sha": "b" * 40,
        "workflow_path": ".github/workflows/vip-ai-studio-synthetic-ci.yml",
        "workflow_blob_sha": "c" * 40,
        "run_id": "12345",
        "job_id": "gate1-synthetic (3.14)",
        "python_version": "3.14.0",
        "pytest_version": "9.0.0",
        "lockfile_sha256": "d" * 64,
        "collected_node_ids": nodes,
        "executed_node_ids": nodes,
        "suite_coverage_complete": True,
        "counts": {
            "collected": 6,
            "executed": 6,
            "passed": 6,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "deselected": 0,
        },
        "exit_status": 0,
        "collection_exit_status": 0,
        "pytest_exit_status": 0,
        "status": "PASS",
        "junit_sha256": "e" * 64,
        "collection_sha256": "f" * 64,
        "evidence_errors": [],
    }


def test_accepts_complete_lab_only_receipt() -> None:
    assert validate_receipt(valid_receipt()) == []


@pytest.mark.parametrize(
    "mutation",
    [
        lambda receipt: receipt.pop("workflow_blob_sha"),
        lambda receipt: receipt.update(lane_id="canonical-history"),
        lambda receipt: receipt["counts"].update(executed=5),
        lambda receipt: receipt["counts"].update(deselected=1),
        lambda receipt: receipt["counts"].update(skipped=1, passed=5),
        lambda receipt: receipt["executed_node_ids"].pop(),
    ],
    ids=("missing-identity", "wrong-lane", "inconsistent-count", "deselected", "skipped", "missing-node"),
)
def test_rejects_malformed_missing_inconsistent_or_skipped_receipts(mutation) -> None:
    receipt = copy.deepcopy(valid_receipt())
    mutation(receipt)
    assert validate_receipt(receipt)


def test_rejects_missing_receipt_and_non_object_payload() -> None:
    assert validate_receipt(None)
    assert validate_receipt({})


def test_accepts_consistent_failed_execution_as_failure_evidence() -> None:
    receipt = valid_receipt()
    receipt["counts"].update(passed=5, failed=1)
    receipt.update(exit_status=1, pytest_exit_status=1, status="FAIL")
    assert validate_receipt(receipt) == []


def test_workflow_keeps_python_matrix_six_suites_and_separate_artifact() -> None:
    workflow = Path(".github/workflows/vip-ai-studio-synthetic-ci.yml").read_text()
    assert "python-version: ['3.11', '3.14']" in workflow
    expected_suites = (
        "test_mega17_editorial_readiness.py",
        "test_mega17_end_to_end.py",
        "test_mega17_gate0_readiness.py",
        "test_mega17_integration_readiness.py",
        "test_mega17_release_readiness.py",
        "test_mega17_source_readiness.py",
    )
    for suite in expected_suites:
        assert workflow.count(suite) == 1
    assert "name: lab-synthetic-${{ matrix.python-version }}" in workflow
    assert "canonical-history status is independent and unchanged" in workflow


def test_builder_does_not_claim_pass_when_one_meg17_suite_is_empty(tmp_path: Path) -> None:
    nodes = valid_receipt()["collected_node_ids"][:-1]
    collection = tmp_path / "collection.txt"
    collection.write_text(
        "\n".join(
            f"{nodeid.split('::', 1)[0].replace('.', '/')}.py::{nodeid.split('::', 1)[1]}"
            for nodeid in nodes
        )
        + "\n",
        encoding="utf-8",
    )
    junit = tmp_path / "junit.xml"
    cases = "".join(
        f'<testcase classname="{nodeid.split("::", 1)[0]}" name="{nodeid.split("::", 1)[1]}" />'
        for nodeid in nodes
    )
    junit.write_text(f"<testsuite>{cases}</testsuite>", encoding="utf-8")

    receipt = build_receipt(collection, junit, 0, 0, 0)

    assert receipt["status"] == "FAIL"
    assert receipt["suite_coverage_complete"] is False
    assert validate_receipt(receipt) == []
