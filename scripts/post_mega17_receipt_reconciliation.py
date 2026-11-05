"""Fail-closed checks for normalized cross-repository test evidence slices.

Inputs are normalized from independently fetched GitHub metadata, workflow
receipts, artifact bytes and JUnit XML. This module does not fetch evidence.
"""

from typing import Any, Mapping, Sequence


_CONTRACT_FIELDS = {
    "repository", "lane", "scope", "pr_number", "pr_head_sha", "pr_base_sha",
    "merge_sha", "tree_sha", "workflow_path", "workflow_blob_sha", "python_version",
    "pytest_version", "lock_sha256", "expected_node_ids", "run_id", "job_id",
    "artifact_sha256",
}


def reconcile_slice(
    contract: Mapping[str, Any],
    evidence: Mapping[str, Any],
    junit_cases: Sequence[Mapping[str, str]],
) -> str:
    """Return TEST_EXECUTION_PASS only for a complete exact identity match."""
    if set(contract) != _CONTRACT_FIELDS or not isinstance(evidence, Mapping):
        return "UNRESOLVED"
    required = _CONTRACT_FIELDS | {
        "artifact_available", "status", "disposition", "runner_started", "pytest_exit_code",
        "collection_error", "collected_node_ids", "executed_node_ids", "node_results", "counts",
        "deselected", "blockers", "job_status", "job_conclusion", "git_history_verified",
        "pinned_dependencies_verified",
    }
    if not required.issubset(evidence):
        return "UNRESOLVED"
    for field in _CONTRACT_FIELDS - {"expected_node_ids", "artifact_sha256"}:
        if evidence.get(field) != contract.get(field):
            return "UNRESOLVED"
    if evidence.get("artifact_sha256") != contract.get("artifact_sha256"):
        return "UNRESOLVED"
    if evidence.get("artifact_available") is not True:
        return "UNRESOLVED"
    if type(evidence.get("run_id")) is not int or type(evidence.get("job_id")) is not int:
        return "UNRESOLVED"
    if evidence.get("status") != "PASS" or evidence.get("disposition") != "PASS":
        return "UNRESOLVED"
    if evidence.get("runner_started") is not True or evidence.get("pytest_exit_code") != 0:
        return "UNRESOLVED"
    if evidence.get("collection_error") is not False or evidence.get("deselected") != 0:
        return "UNRESOLVED"
    if evidence.get("blockers") != []:
        return "UNRESOLVED"
    if evidence.get("git_history_verified") is not True or evidence.get("pinned_dependencies_verified") is not True:
        return "UNRESOLVED"
    if evidence.get("job_status") != "completed" or evidence.get("job_conclusion") != "success":
        return "UNRESOLVED"

    expected = contract.get("expected_node_ids")
    collected = evidence.get("collected_node_ids")
    executed = evidence.get("executed_node_ids")
    recorded_expected = evidence.get("expected_node_ids")
    if not all(_unique_strings(value) for value in (expected, collected, executed, recorded_expected)):
        return "UNRESOLVED"
    if set(recorded_expected) != set(expected) or set(collected) != set(expected) or set(executed) != set(expected):
        return "UNRESOLVED"

    if not isinstance(junit_cases, Sequence) or isinstance(junit_cases, (str, bytes)):
        return "UNRESOLVED"
    ids: list[str] = []
    for case in junit_cases:
        if not isinstance(case, Mapping) or set(case) != {"node_id", "outcome"}:
            return "UNRESOLVED"
        if type(case.get("node_id")) is not str or type(case.get("outcome")) is not str:
            return "UNRESOLVED"
        ids.append(case["node_id"])
    if not _unique_strings(ids) or set(ids) != set(expected):
        return "UNRESOLVED"
    if any(case["outcome"] != "PASS" for case in junit_cases):
        return "UNRESOLVED"

    counts = evidence.get("counts")
    expected_counts = {
        "collected": len(expected), "executed": len(expected), "passed": len(expected),
        "failed": 0, "errors": 0, "skipped": 0, "deselected": 0,
    }
    if not isinstance(counts, Mapping) or set(counts) != set(expected_counts) or dict(counts) != expected_counts:
        return "UNRESOLVED"
    node_results = evidence.get("node_results")
    if not isinstance(node_results, Mapping) or set(node_results) != set(expected):
        return "UNRESOLVED"
    if any(result != "PASS" for result in node_results.values()):
        return "UNRESOLVED"

    required_paths = evidence.get("required_tree_paths")
    if required_paths is not None:
        tree_paths = evidence.get("tree_paths")
        if not _unique_strings(required_paths) or not isinstance(tree_paths, (list, tuple)):
            return "UNRESOLVED"
        if not set(required_paths).issubset(tree_paths):
            return "UNRESOLVED"
    return "TEST_EXECUTION_PASS"


def quality_disposition(conclusion: Any, observed_head: Any = None, required_head: Any = None) -> str:
    """Keep the separate code-quality gate explicit; never infer from tests."""
    if type(observed_head) is not str or type(required_head) is not str or observed_head != required_head:
        return "NOT_OBSERVED"
    if type(conclusion) is not str:
        return "NOT_OBSERVED"
    if conclusion == "success":
        return "PASS"
    if conclusion == "failure":
        return "FAIL"
    if conclusion in {"queued", "in_progress", "pending"}:
        return "PENDING"
    return "NOT_OBSERVED"


def pull_request_disposition(state: Any, draft: Any, merged: Any) -> str:
    if merged is True and state == "closed" and draft is False:
        return "MERGED"
    if state == "open" and draft is True and merged is False:
        return "OPEN_DRAFT_UNMERGED"
    if state == "open" and draft is False and merged is False:
        return "OPEN_UNMERGED"
    return "UNRESOLVED"


def _unique_strings(values: Any) -> bool:
    return (
        isinstance(values, (list, tuple))
        and bool(values)
        and all(type(value) is str and value for value in values)
        and len(values) == len(set(values))
    )
