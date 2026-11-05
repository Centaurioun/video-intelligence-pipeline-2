from __future__ import annotations

import copy
import hashlib
import subprocess
from pathlib import Path

import pytest

from scripts.lab_synthetic_receipt import (
    EXPECTED_NODE_IDS,
    EXPECTED_NODE_BASELINE_COUNT,
    LOCKFILE_PATH,
    WORKFLOW_PATH,
    _runtime_identity,
    build_receipt,
    _parse_junit_bytes,
    validate_receipt,
    verify_receipt_evidence,
)


def valid_receipt() -> dict[str, object]:
    nodes = sorted(EXPECTED_NODE_IDS)
    return {
        "schema_version": "lab-synthetic-receipt.v2",
        "lane_id": "lab-synthetic",
        "scope": "LAB_SYNTHETIC_ONLY",
        "repository": "Centaurioun/video-intelligence-pipeline-2",
        "ref": "refs/pull/7/merge",
        "event_name": "pull_request",
        "source_ref": "refs/heads/codex/task4-lab-synthetic-receipts",
        "commit_sha": "a" * 40,
        "pr_base_ref": "main",
        "pr_head_ref": "codex/task4-lab-synthetic-receipts",
        "pr_base_repository": "Centaurioun/video-intelligence-pipeline-2",
        "pr_head_repository": "Centaurioun/video-intelligence-pipeline-2",
        "pr_base_sha": "d" * 40,
        "pr_head_sha": "e" * 40,
        "pr_merge_sha": "a" * 40,
        "tree_sha": "b" * 40,
        "workflow_path": ".github/workflows/vip-ai-studio-synthetic-ci.yml",
        "workflow_blob_sha": "c" * 40,
        "run_id": "12345",
        "job_key": "gate1-synthetic-3.14",
        "github_job_id": "NOT_OBSERVED",
        "python_version": "3.14.0",
        "pytest_version": "9.0.0",
        "lockfile_sha256": "d" * 64,
        "collected_node_ids": nodes,
        "executed_node_ids": list(nodes),
        "suite_coverage_complete": True,
        "counts": {
            "collected": len(nodes),
            "executed": len(nodes),
            "passed": len(nodes),
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


def test_mega17_baseline_is_independently_pinned() -> None:
    baseline = Path("scripts/lab_synthetic_expected_nodes.txt").read_bytes()
    assert EXPECTED_NODE_BASELINE_COUNT == 37
    assert len(EXPECTED_NODE_IDS) == 37
    assert hashlib.sha256(baseline).hexdigest() == (
        "8618d8d4e810dcb065ee4f5d79d3cb28b02d57e817ba845181b2f2b88ec6c374"
    )


def test_accepts_complete_lab_only_receipt() -> None:
    receipt = valid_receipt()
    receipt["collected_node_ids"] = sorted(EXPECTED_NODE_IDS)
    receipt["executed_node_ids"] = sorted(EXPECTED_NODE_IDS)
    receipt["counts"].update(collected=len(EXPECTED_NODE_IDS), executed=len(EXPECTED_NODE_IDS), passed=len(EXPECTED_NODE_IDS))
    assert validate_receipt(receipt) == []


def test_rejects_reduced_or_substituted_mega17_node_set() -> None:
    receipt = valid_receipt()
    receipt["collected_node_ids"] = sorted(EXPECTED_NODE_IDS)
    receipt["executed_node_ids"] = sorted(EXPECTED_NODE_IDS)
    receipt["counts"].update(collected=len(EXPECTED_NODE_IDS), executed=len(EXPECTED_NODE_IDS), passed=len(EXPECTED_NODE_IDS))
    assert validate_receipt(receipt) == []

    reduced = copy.deepcopy(receipt)
    reduced["collected_node_ids"].remove(next(iter(EXPECTED_NODE_IDS)))
    reduced["executed_node_ids"].remove(next(iter(EXPECTED_NODE_IDS)))
    reduced["counts"].update(collected=len(EXPECTED_NODE_IDS) - 1, executed=len(EXPECTED_NODE_IDS) - 1, passed=len(EXPECTED_NODE_IDS) - 1)
    assert validate_receipt(reduced)

    substituted = copy.deepcopy(receipt)
    substituted["collected_node_ids"][0] = substituted["collected_node_ids"][0].replace("test_", "test_replacement_", 1)
    substituted["executed_node_ids"][0] = substituted["collected_node_ids"][0]
    assert validate_receipt(substituted)


def test_allows_additions_when_entire_pinned_baseline_remains() -> None:
    receipt = valid_receipt()
    added_node = "tests.vip_lab.test_mega17_end_to_end::test_new_additive_case"
    receipt["collected_node_ids"].append(added_node)
    receipt["executed_node_ids"].append(added_node)
    receipt["counts"].update(
        collected=len(EXPECTED_NODE_IDS) + 1,
        executed=len(EXPECTED_NODE_IDS) + 1,
        passed=len(EXPECTED_NODE_IDS) + 1,
    )
    assert validate_receipt(receipt) == []


@pytest.mark.parametrize("repository", ["Centaurioun/video-intelligence-pipeline", "other/repo"])
def test_rejects_cross_lane_repository_spoofing(repository: str) -> None:
    receipt = valid_receipt()
    receipt["repository"] = repository
    assert validate_receipt(receipt)


@pytest.mark.parametrize(
    "field,value",
    [("lane_id", "canonical-history"), ("scope", "CANONICAL_HISTORY"),
     ("workflow_path", ".github/workflows/canonical-history-regressions.yml")],
)
def test_rejects_cross_lane_identity_fields(field: str, value: str) -> None:
    receipt = valid_receipt()
    receipt[field] = value
    assert validate_receipt(receipt)


@pytest.mark.parametrize(
    "field",
    ["pr_base_ref", "pr_head_ref", "pr_base_repository", "pr_head_repository", "pr_base_sha", "pr_head_sha", "pr_merge_sha"],
)
def test_rejects_missing_or_conflated_pull_request_commit_identity(field: str) -> None:
    receipt = valid_receipt()
    receipt[field] = "NOT_OBSERVED"
    assert validate_receipt(receipt)


@pytest.mark.parametrize(
    "field,value",
    [("pr_base_repository", "Centaurioun/video-intelligence-pipeline"), ("pr_head_repository", "")],
)
def test_rejects_wrong_or_unobserved_pull_request_repository(field: str, value: str) -> None:
    receipt = valid_receipt()
    receipt[field] = value
    assert validate_receipt(receipt)


def test_rejects_pull_request_head_conflated_with_merge_checkout() -> None:
    receipt = valid_receipt()
    receipt["pr_head_sha"] = receipt["commit_sha"]
    assert validate_receipt(receipt)


def test_logical_job_key_is_not_reported_as_numeric_github_job_id() -> None:
    receipt = valid_receipt()
    receipt["github_job_id"] = receipt["job_key"]
    assert validate_receipt(receipt)


def test_builder_fails_when_pull_request_identity_is_not_observed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    for key in (
        "LAB_PR_BASE_REF", "LAB_PR_HEAD_REF", "LAB_PR_BASE_REPOSITORY",
        "LAB_PR_HEAD_REPOSITORY", "LAB_PR_BASE_SHA",
        "LAB_PR_HEAD_SHA", "LAB_PR_MERGE_SHA",
    ):
        monkeypatch.delenv(key, raising=False)
    nodes = sorted(EXPECTED_NODE_IDS)
    collection = tmp_path / "collection.txt"
    collection.write_text(
        "\n".join(
            f"{node.split('::')[0].replace('.', '/')}.py::{node.split('::', 1)[1]}"
            for node in nodes
        ) + "\n",
        encoding="utf-8",
    )
    junit = tmp_path / "junit.xml"
    cases = "".join(
        f'<testcase classname="{node.split("::")[0]}" name="{node.split("::", 1)[1]}" />'
        for node in nodes
    )
    junit.write_text(f"<testsuite>{cases}</testsuite>", encoding="utf-8")

    receipt = build_receipt(collection, junit, 0, 0, 0)

    assert receipt["status"] == "FAIL"
    assert any("pull request identity unavailable" in error for error in receipt["evidence_errors"])


def test_rejects_junit_counters_that_disagree_with_testcases() -> None:
    junit = b'<testsuite tests="2" failures="0" errors="0" skipped="0"><testcase classname="tests.vip_lab.test_mega17_end_to_end" name="test_one" /></testsuite>'
    with pytest.raises(ValueError, match="JUnit suite tests counter"):
        _parse_junit_bytes(junit)


def test_evidence_verification_rejects_workflow_changed_after_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    workflow = repo / WORKFLOW_PATH
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: reviewed workflow\n", encoding="utf-8")
    lockfile = repo / LOCKFILE_PATH
    lockfile.parent.mkdir(parents=True)
    source_lock = Path(__file__).resolve().parents[2] / LOCKFILE_PATH
    lockfile.write_bytes(source_lock.read_bytes())
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", WORKFLOW_PATH, LOCKFILE_PATH], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo,
        check=True,
    )
    monkeypatch.chdir(repo)
    for key in (
        "GITHUB_SHA", "GITHUB_REF", "GITHUB_RUN_ID", "GITHUB_JOB", "LAB_JOB_ID",
        "LAB_GITHUB_JOB_ID", "LAB_PR_BASE_REF", "LAB_PR_HEAD_REF", "LAB_PR_BASE_REPOSITORY",
        "LAB_PR_HEAD_REPOSITORY", "LAB_PR_BASE_SHA",
        "LAB_PR_HEAD_SHA", "LAB_PR_MERGE_SHA",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "local")

    nodes = sorted(EXPECTED_NODE_IDS)
    collection = tmp_path / "collection.txt"
    collection.write_text(
        "\n".join(
            f"{node.split('::')[0].replace('.', '/')}.py::{node.split('::', 1)[1]}"
            for node in nodes
        ) + "\n",
        encoding="utf-8",
    )
    junit = tmp_path / "junit.xml"
    cases = "".join(
        f'<testcase classname="{node.split("::")[0]}" name="{node.split("::", 1)[1]}" />'
        for node in nodes
    )
    junit.write_text(f"<testsuite tests=\"{len(nodes)}\">{cases}</testsuite>", encoding="utf-8")
    workflow.write_text("name: replaced workflow\n", encoding="utf-8")
    receipt = build_receipt(collection, junit, 0, 0, 0)
    assert verify_receipt_evidence(receipt, collection, junit)


def test_rejects_injected_cross_lane_identity_claim() -> None:
    receipt = valid_receipt()
    receipt["canonical_history_status"] = "PASS"
    assert validate_receipt(receipt)


def test_structural_validation_is_distinct_from_evidence_verification(tmp_path: Path) -> None:
    receipt = valid_receipt()
    receipt["collected_node_ids"] = sorted(EXPECTED_NODE_IDS)
    receipt["executed_node_ids"] = sorted(EXPECTED_NODE_IDS)
    receipt["counts"].update(collected=len(EXPECTED_NODE_IDS), executed=len(EXPECTED_NODE_IDS), passed=len(EXPECTED_NODE_IDS))
    assert validate_receipt(receipt) == []

    collection = tmp_path / "collection.txt"
    collection.write_text("\n".join(f"{node.split('::')[0].replace('.', '/')}.py::{node.split('::', 1)[1]}" for node in EXPECTED_NODE_IDS) + "\n", encoding="utf-8")
    cases = "".join(f'<testcase classname="{node.split("::")[0]}" name="{node.split("::", 1)[1]}" />' for node in EXPECTED_NODE_IDS)
    junit = tmp_path / "junit.xml"
    junit.write_text(f"<testsuite>{cases}</testsuite>", encoding="utf-8")
    receipt["collection_sha256"] = __import__("hashlib").sha256(collection.read_bytes()).hexdigest()
    receipt["junit_sha256"] = __import__("hashlib").sha256(junit.read_bytes()).hexdigest()
    receipt["commit_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt["tree_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
    receipt["workflow_blob_sha"] = subprocess.check_output(["git", "rev-parse", f"HEAD:{WORKFLOW_PATH}"], text=True).strip()
    receipt["lockfile_sha256"] = hashlib.sha256(Path(LOCKFILE_PATH).read_bytes()).hexdigest()
    receipt.update(_runtime_identity())
    verification_errors = verify_receipt_evidence(receipt, collection, junit)
    working_workflow_blob = subprocess.check_output(["git", "hash-object", WORKFLOW_PATH], text=True).strip()
    if working_workflow_blob == receipt["workflow_blob_sha"]:
        assert verification_errors == []
    else:
        assert "workflow file differs from checked-out Git blob" in verification_errors

    collection.write_text("tests/vip_lab/test_mega17_end_to_end.py::test_replacement\n", encoding="utf-8")
    assert verify_receipt_evidence(receipt, collection, junit)

    collection.write_text(
        "\n".join(
            f"{node.split('::')[0].replace('.', '/')}.py::{node.split('::', 1)[1]}"
            for node in EXPECTED_NODE_IDS
        ) + "\n",
        encoding="utf-8",
    )
    junit.write_text("<testsuite><testcase classname='tests.vip_lab.test_fake' name='test_fake'/></testsuite>", encoding="utf-8")
    assert verify_receipt_evidence(receipt, collection, junit)


@pytest.mark.parametrize(
    "field",
    ["commit_sha", "tree_sha", "workflow_blob_sha", "lockfile_sha256",
     "ref", "run_id", "job_key", "python_version", "pytest_version",
     "event_name", "source_ref", "pr_base_ref", "pr_head_ref", "pr_base_repository",
     "pr_head_repository", "pr_base_sha",
     "pr_head_sha", "pr_merge_sha", "github_job_id"],
)
def test_evidence_verification_rejects_unbound_repository_provenance(field: str, tmp_path: Path) -> None:
    receipt = valid_receipt()
    collection = tmp_path / "collection.txt"
    collection.write_text(
        "\n".join(
            f"{node.split('::')[0].replace('.', '/')}.py::{node.split('::', 1)[1]}"
            for node in EXPECTED_NODE_IDS
        ) + "\n",
        encoding="utf-8",
    )
    junit = tmp_path / "junit.xml"
    cases = "".join(
        f'<testcase classname="{node.split("::")[0]}" name="{node.split("::", 1)[1]}" />'
        for node in EXPECTED_NODE_IDS
    )
    junit.write_text(f"<testsuite>{cases}</testsuite>", encoding="utf-8")
    receipt["collection_sha256"] = hashlib.sha256(collection.read_bytes()).hexdigest()
    receipt["junit_sha256"] = hashlib.sha256(junit.read_bytes()).hexdigest()
    receipt["commit_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt["tree_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
    receipt["workflow_blob_sha"] = subprocess.check_output(["git", "hash-object", WORKFLOW_PATH], text=True).strip()
    receipt["lockfile_sha256"] = hashlib.sha256(Path(LOCKFILE_PATH).read_bytes()).hexdigest()
    receipt.update(_runtime_identity())
    receipt[field] = "0" * (64 if field == "lockfile_sha256" else 40)
    assert verify_receipt_evidence(receipt, collection, junit)
    collection.write_text("\n".join(f"{node.split('::')[0].replace('.', '/')}.py::{node.split('::', 1)[1]}" for node in EXPECTED_NODE_IDS) + "\n", encoding="utf-8")
    junit.write_text("<testsuite><testcase classname='tests.vip_lab.test_fake' name='test_fake'/></testsuite>", encoding="utf-8")
    assert verify_receipt_evidence(receipt, collection, junit)


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


def test_rejects_duplicate_node_ids_and_unrecognized_count_fields() -> None:
    duplicate = valid_receipt()
    duplicate["collected_node_ids"].append(duplicate["collected_node_ids"][0])
    duplicate["executed_node_ids"].append(duplicate["executed_node_ids"][0])
    duplicate["counts"].update(collected=len(duplicate["collected_node_ids"]), executed=len(duplicate["executed_node_ids"]))
    assert validate_receipt(duplicate)

    extra_count = valid_receipt()
    extra_count["counts"]["not_run"] = 1
    assert validate_receipt(extra_count)


def test_failed_pytest_cannot_be_represented_as_pass() -> None:
    receipt = valid_receipt()
    receipt.update(exit_status=1, pytest_exit_status=1)
    assert validate_receipt(receipt)


def test_rejects_missing_receipt_and_non_object_payload() -> None:
    assert validate_receipt(None)
    assert validate_receipt({})


def test_accepts_consistent_failed_execution_as_failure_evidence() -> None:
    receipt = valid_receipt()
    receipt["counts"].update(passed=len(EXPECTED_NODE_IDS) - 1, failed=1)
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
    assert "Run LAB receipt contract tests" in workflow
    assert "tests/scripts/test_lab_synthetic_receipt.py" in workflow
    assert "verify-evidence" in workflow
    assert "if-no-files-found: error" in workflow


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
    assert not any("PASS requires" in error for error in validate_receipt(receipt))
