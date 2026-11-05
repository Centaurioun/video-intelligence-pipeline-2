"""Adversarial contract tests; all constructed records here are SYNTHETIC fixtures."""

from copy import deepcopy

import pytest

from scripts.post_mega17_receipt_reconciliation import (
    pull_request_disposition,
    quality_disposition,
    reconcile_slice,
)


EXPECTED = ["tests/example.py::test_one", "tests/example.py::test_two"]
CONTRACT = {
    "repository": "example/canonical",
    "lane": "canonical",
    "scope": "EXAMPLE_SLICE",
    "pr_number": 1,
    "pr_head_sha": "a" * 40,
    "pr_base_sha": "b" * 40,
    "merge_sha": "c" * 40,
    "tree_sha": "d" * 40,
    "workflow_path": ".github/workflows/example.yml",
    "workflow_blob_sha": "e" * 40,
    "python_version": "3.11.0",
    "pytest_version": "pytest 8.3.3",
    "lock_sha256": "f" * 64,
    "expected_node_ids": EXPECTED,
    "run_id": 123,
    "job_id": 456,
    "artifact_sha256": "1" * 64,
}


def valid_evidence():
    return {
        **deepcopy(CONTRACT),
        "artifact_available": True,
        "status": "PASS",
        "disposition": "PASS",
        "runner_started": True,
        "pytest_exit_code": 0,
        "collection_error": False,
        "collected_node_ids": list(EXPECTED),
        "executed_node_ids": list(EXPECTED),
        "node_results": {node: "PASS" for node in EXPECTED},
        "counts": {"collected": 2, "executed": 2, "passed": 2, "failed": 0,
                   "errors": 0, "skipped": 0, "deselected": 0},
        "deselected": 0,
        "blockers": [],
        "job_status": "completed",
        "job_conclusion": "success",
        "git_history_verified": True,
        "pinned_dependencies_verified": True,
        "tree_paths": [],
    }


def junit():
    return [{"node_id": node, "outcome": "PASS"} for node in EXPECTED]


def test_exact_slice_is_passed_without_cross_slice_aggregation():
    assert reconcile_slice(CONTRACT, valid_evidence(), junit()) == "TEST_EXECUTION_PASS"


@pytest.mark.parametrize("field,value", [
    ("artifact_available", False),
    ("artifact_sha256", "0" * 64),
    ("repository", "example/lab"),
    ("lane", "lab"),
    ("scope", "OTHER_SLICE"),
    ("pr_head_sha", "0" * 40),
    ("pr_base_sha", "0" * 40),
    ("merge_sha", "0" * 40),
    ("tree_sha", "0" * 40),
    ("workflow_blob_sha", "0" * 40),
    ("workflow_path", ".github/workflows/wrong.yml"),
    ("python_version", "3.14.0"),
    ("pytest_version", "pytest 0.0"),
    ("lock_sha256", "0" * 64),
    ("run_id", 999),
    ("pr_number", 99),
    ("job_id", None),
    ("git_history_verified", False),
    ("pinned_dependencies_verified", False),
    ("status", "FAIL"),
    ("status", "BLOCKED"),
    ("status", "NOT RUN"),
    ("status", "UNRESOLVED"),
    ("status", "PENDING"),
    ("status", "ERROR"),
    ("status", "SKIP"),
    ("status", "NOT_OBSERVED"),
    ("runner_started", False),
    ("collection_error", True),
    ("deselected", 1),
    ("artifact_available", None),
])
def test_identity_or_unavailable_state_never_defaults_to_pass(field, value):
    evidence = valid_evidence()
    evidence[field] = value
    assert reconcile_slice(CONTRACT, evidence, junit()) == "UNRESOLVED"


@pytest.mark.parametrize("mutation", [
    "missing", "duplicate", "extra", "wrong_expected", "deselected", "incomplete", "junit_mismatch",
    "skipped", "failed", "wrong_counts", "blocked_job", "logical_job_as_id",
    "lab_claims_canonical", "canonical_claims_lab", "co_tree_files_missing",
])
def test_node_and_provenance_attacks_fail_closed(mutation):
    evidence = valid_evidence()
    cases = junit()
    if mutation == "missing":
        evidence["collected_node_ids"].pop()
    elif mutation == "duplicate":
        evidence["collected_node_ids"].append(EXPECTED[0])
    elif mutation == "extra":
        evidence["executed_node_ids"][-1] = "tests/other.py::substituted"
    elif mutation == "wrong_expected":
        evidence["expected_node_ids"].pop()
    elif mutation == "deselected":
        evidence["deselected"] = 1
    elif mutation == "incomplete":
        evidence["executed_node_ids"].pop()
    elif mutation == "junit_mismatch":
        cases.pop()
    elif mutation == "skipped":
        cases[0]["outcome"] = "SKIP"
    elif mutation == "failed":
        cases[0]["outcome"] = "FAIL"
    elif mutation == "wrong_counts":
        evidence["counts"]["passed"] = 1
    elif mutation == "blocked_job":
        evidence["job_status"] = "queued"
        evidence["runner_started"] = False
    elif mutation == "logical_job_as_id":
        evidence["job_id"] = "synthetic-smoke-python-3.11"
    elif mutation == "lab_claims_canonical":
        evidence["repository"] = "example/lab"
        evidence["lane"] = "lab"
        evidence["scope"] = "CANONICAL_HISTORY_33"
    elif mutation == "canonical_claims_lab":
        evidence["scope"] = "LAB_SYNTHETIC"
    elif mutation == "co_tree_files_missing":
        evidence["tree_paths"] = ["src/vip_fvs/bounded_admission.py"]
        evidence["required_tree_paths"] = ["src/vip_fvs/bounded_admission.py",
                                           "tests/vip_fvs/unit/test_bounded_admission.py",
                                           ".github/workflows/python-synthetic-smoke.yml"]
    assert reconcile_slice(CONTRACT, evidence, cases) == "UNRESOLVED"


@pytest.mark.parametrize("conclusion,expected", [
    ("queued", "PENDING"), ("in_progress", "PENDING"), ("pending", "PENDING"),
    ("failure", "FAIL"), (None, "NOT_OBSERVED"), ("success", "PASS"),
])
def test_code_health_disposition_is_independent(conclusion, expected):
    assert quality_disposition(conclusion, "a" * 40, "a" * 40) == expected


def test_stale_code_health_result_is_not_current_head_pass():
    assert quality_disposition("success", "b" * 40, "a" * 40) == "NOT_OBSERVED"


@pytest.mark.parametrize("state,draft,merged,expected", [
    ("open", True, False, "OPEN_DRAFT_UNMERGED"),
    ("open", False, False, "OPEN_UNMERGED"),
    ("closed", False, True, "MERGED"),
    ("open", True, True, "UNRESOLVED"),
    ("closed", True, False, "UNRESOLVED"),
])
def test_draft_or_unmerged_pr_is_not_adopted(state, draft, merged, expected):
    assert pull_request_disposition(state, draft, merged) == expected


def test_synthetic_scope_cannot_be_promoted_to_real_gate_evidence():
    evidence = valid_evidence()
    evidence["scope"] = "REAL_GATE_ACCEPTANCE"
    assert reconcile_slice(CONTRACT, evidence, junit()) == "UNRESOLVED"
