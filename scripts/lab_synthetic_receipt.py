#!/usr/bin/env python3
"""Create and validate the LAB-only MEGA-17 CI evidence receipt."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "lab-synthetic-receipt.v1"
WORKFLOW_PATH = ".github/workflows/vip-ai-studio-synthetic-ci.yml"
LOCKFILE_PATH = "requirements/gate0.lock"
EXPECTED_MODULES = {
    "tests.vip_lab.test_mega17_editorial_readiness",
    "tests.vip_lab.test_mega17_end_to_end",
    "tests.vip_lab.test_mega17_gate0_readiness",
    "tests.vip_lab.test_mega17_integration_readiness",
    "tests.vip_lab.test_mega17_release_readiness",
    "tests.vip_lab.test_mega17_source_readiness",
}
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _parse_collection(path: Path) -> list[str]:
    nodeids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        nodeid = line.strip()
        if nodeid.startswith("tests/vip_lab/test_mega17_") and "::" in nodeid:
            path_part, test_name = nodeid.split("::", 1)
            module = path_part.replace("/", ".").removesuffix(".py")
            nodeids.append(f"{module}::{test_name}")
    return sorted(nodeids)


def _parse_junit(path: Path) -> tuple[list[str], dict[str, int]]:
    root = ET.parse(path).getroot()
    cases = list(root.iter("testcase"))
    executed: list[str] = []
    passed = failed = errors = skipped = 0
    for case in cases:
        classname = case.get("classname", "")
        name = case.get("name", "")
        if not classname or not name:
            raise ValueError("JUnit testcase is missing classname or name")
        executed.append(f"{classname}::{name}")
        if case.find("skipped") is not None:
            skipped += 1
        elif case.find("failure") is not None:
            failed += 1
        elif case.find("error") is not None:
            errors += 1
        else:
            passed += 1
    counts = {
        "collected": len(executed),
        "executed": len(executed),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "deselected": 0,
    }
    return sorted(executed), counts


def validate_receipt(receipt: Any) -> list[str]:
    """Return fail-closed receipt contract errors; empty means internally consistent."""
    if not isinstance(receipt, dict):
        return ["receipt must be a JSON object"]
    required = {
        "schema_version", "lane_id", "scope", "repository", "ref", "commit_sha",
        "tree_sha", "workflow_path", "workflow_blob_sha", "run_id", "job_id",
        "python_version", "pytest_version", "lockfile_sha256", "collected_node_ids",
        "executed_node_ids", "suite_coverage_complete", "counts", "exit_status", "collection_exit_status",
        "pytest_exit_status", "status", "junit_sha256", "collection_sha256",
        "evidence_errors",
    }
    errors = [f"missing required field: {key}" for key in sorted(required - receipt.keys())]
    if errors:
        return errors
    if receipt["schema_version"] != SCHEMA_VERSION:
        errors.append("unsupported schema_version")
    if receipt["lane_id"] != "lab-synthetic" or receipt["scope"] != "LAB_SYNTHETIC_ONLY":
        errors.append("receipt identity must remain LAB synthetic only")
    if receipt["workflow_path"] != WORKFLOW_PATH:
        errors.append("workflow_path does not identify the LAB synthetic workflow")
    if not isinstance(receipt["repository"], str) or not receipt["repository"].strip():
        errors.append("repository must be a non-empty identity")
    if not isinstance(receipt["ref"], str) or not receipt["ref"].strip():
        errors.append("ref must be a non-empty identity")
    for key in ("commit_sha", "tree_sha", "workflow_blob_sha"):
        if not isinstance(receipt[key], str) or not SHA1_RE.fullmatch(receipt[key]):
            errors.append(f"{key} must be a full Git SHA-1")
    for key in ("lockfile_sha256", "junit_sha256", "collection_sha256"):
        if not isinstance(receipt[key], str) or not SHA256_RE.fullmatch(receipt[key]):
            errors.append(f"{key} must be a SHA-256 digest")
    for key in ("run_id", "job_id", "python_version", "pytest_version"):
        if not isinstance(receipt[key], str) or not receipt[key].strip():
            errors.append(f"{key} must be a non-empty string")

    collected = receipt["collected_node_ids"]
    executed = receipt["executed_node_ids"]
    if not isinstance(collected, list) or not all(isinstance(item, str) for item in collected):
        errors.append("collected_node_ids must be a string list")
        collected = []
    if not isinstance(executed, list) or not all(isinstance(item, str) for item in executed):
        errors.append("executed_node_ids must be a string list")
        executed = []
    if not collected or len(collected) != len(set(collected)):
        errors.append("collected_node_ids must be non-empty and unique")
    if len(executed) != len(set(executed)):
        errors.append("executed_node_ids must be unique")
    if sorted(collected) != sorted(executed):
        errors.append("collected and executed node IDs differ (missing, extra, or deselected tests)")
    modules = {nodeid.split("::", 1)[0].replace("/", ".").removesuffix(".py") for nodeid in collected}
    derived_suite_coverage_complete = modules == EXPECTED_MODULES
    if not isinstance(receipt["suite_coverage_complete"], bool):
        errors.append("suite_coverage_complete must be a boolean")
    elif receipt["suite_coverage_complete"] != derived_suite_coverage_complete:
        errors.append("suite_coverage_complete does not match node IDs")
    if not derived_suite_coverage_complete and receipt["status"] != "FAIL":
        errors.append("node IDs do not cover exactly the six MEGA-17 suites")

    counts = receipt["counts"]
    count_keys = {"collected", "executed", "passed", "failed", "errors", "skipped", "deselected"}
    if not isinstance(counts, dict) or count_keys - counts.keys():
        errors.append("counts must contain every execution count")
    else:
        for key in count_keys:
            value = counts[key]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"counts.{key} must be a non-negative integer")
        if all(isinstance(counts[key], int) and not isinstance(counts[key], bool) for key in count_keys):
            if counts["collected"] != len(collected) or counts["executed"] != len(executed):
                errors.append("collection/execution counts do not match node ID lists")
            if counts["passed"] + counts["failed"] + counts["errors"] + counts["skipped"] != counts["executed"]:
                errors.append("outcome counts do not sum to executed count")
            if counts["deselected"] != counts["collected"] - counts["executed"]:
                errors.append("deselected count does not match collection delta")

    exit_status = receipt["exit_status"]
    if not isinstance(exit_status, int) or isinstance(exit_status, bool) or exit_status < 0:
        errors.append("exit_status must be a non-negative integer")
    for key in ("collection_exit_status", "pytest_exit_status"):
        if not isinstance(receipt[key], int) or isinstance(receipt[key], bool) or receipt[key] < 0:
            errors.append(f"{key} must be a non-negative integer")
    if not isinstance(receipt["evidence_errors"], list) or receipt["evidence_errors"]:
        errors.append("evidence_errors must be an empty list for a valid receipt")
    elif isinstance(counts, dict) and count_keys <= counts.keys():
        clean = counts["failed"] == counts["errors"] == counts["skipped"] == counts["deselected"] == 0
        if receipt["status"] == "PASS":
            if exit_status != 0 or receipt["collection_exit_status"] != 0 or receipt["pytest_exit_status"] != 0 or not clean or counts["passed"] != counts["executed"] or not derived_suite_coverage_complete:
                errors.append("PASS requires exit 0, all tests passed, and no fail/error/skip/deselect")
        elif receipt["status"] == "FAIL":
            if exit_status == 0 and receipt["collection_exit_status"] == receipt["pytest_exit_status"] == 0 and clean and derived_suite_coverage_complete:
                errors.append("FAIL requires non-zero exit or a non-passing test outcome")
        else:
            errors.append("status must be PASS or FAIL")
    return errors


def build_receipt(
    collection_path: Path,
    junit_path: Path,
    exit_status: int,
    collection_exit_status: int,
    pytest_exit_status: int,
) -> dict[str, Any]:
    evidence_errors: list[str] = []
    try:
        collected = _parse_collection(collection_path)
        collection_digest: str | None = _sha256(collection_path)
    except (OSError, UnicodeError) as exc:
        collected = []
        collection_digest = None
        evidence_errors.append(f"collection evidence unavailable: {exc}")
    try:
        executed, counts = _parse_junit(junit_path)
        junit_digest: str | None = _sha256(junit_path)
    except (OSError, ET.ParseError, ValueError) as exc:
        executed = []
        counts = {key: 0 for key in ("collected", "executed", "passed", "failed", "errors", "skipped", "deselected")}
        junit_digest = None
        evidence_errors.append(f"JUnit evidence unavailable or malformed: {exc}")
    try:
        workflow_blob = _git("hash-object", WORKFLOW_PATH)
    except subprocess.CalledProcessError:
        workflow_blob = ""
        evidence_errors.append("workflow blob identity unavailable")
    try:
        lockfile_digest: str | None = _sha256(Path(LOCKFILE_PATH))
    except OSError as exc:
        lockfile_digest = None
        evidence_errors.append(f"lockfile identity unavailable: {exc}")
    try:
        pytest_version = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        pytest_version = "NOT_OBSERVED"
        evidence_errors.append("pytest version unavailable")
    counts["collected"] = len(collected)
    counts["deselected"] = max(0, len(collected) - len(executed))
    clean = counts["failed"] == counts["errors"] == counts["skipped"] == counts["deselected"] == 0
    modules = {
        nodeid.split("::", 1)[0].replace("/", ".").removesuffix(".py")
        for nodeid in collected
    }
    complete_suite_coverage = modules == EXPECTED_MODULES
    status = (
        "PASS"
        if exit_status == collection_exit_status == pytest_exit_status == 0
        and clean
        and collected == executed
        and complete_suite_coverage
        and not evidence_errors
        else "FAIL"
    )
    repository = os.environ.get("GITHUB_REPOSITORY", "Centaurioun/video-intelligence-pipeline-2")
    ref = os.environ.get("GITHUB_REF", _git("rev-parse", "--abbrev-ref", "HEAD"))
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "lane_id": "lab-synthetic",
        "scope": "LAB_SYNTHETIC_ONLY",
        "repository": repository,
        "ref": ref,
        "commit_sha": os.environ.get("GITHUB_SHA", _git("rev-parse", "HEAD")),
        "tree_sha": _git("rev-parse", "HEAD^{tree}"),
        "workflow_path": WORKFLOW_PATH,
        "workflow_blob_sha": workflow_blob,
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "job_id": os.environ.get("LAB_JOB_ID", os.environ.get("GITHUB_JOB", f"local-python-{sys.version_info.major}.{sys.version_info.minor}")),
        "python_version": sys.version.split()[0],
        "pytest_version": pytest_version,
        "lockfile_sha256": lockfile_digest,
        "collected_node_ids": collected,
        "executed_node_ids": executed,
        "suite_coverage_complete": complete_suite_coverage,
        "counts": counts,
        "exit_status": exit_status,
        "collection_exit_status": collection_exit_status,
        "pytest_exit_status": pytest_exit_status,
        "status": status,
        "junit_sha256": junit_digest,
        "collection_sha256": collection_digest,
        "evidence_errors": evidence_errors,
    }
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("--collection", type=Path, required=True)
    create.add_argument("--junit", type=Path, required=True)
    create.add_argument("--exit-status", type=int, required=True)
    create.add_argument("--collection-exit-status", type=int, required=True)
    create.add_argument("--pytest-exit-status", type=int, required=True)
    create.add_argument("--output", type=Path, required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("receipt", type=Path)
    args = parser.parse_args(argv)
    if args.command == "create":
        receipt = build_receipt(
            args.collection, args.junit, args.exit_status,
            args.collection_exit_status, args.pytest_exit_status,
        )
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        errors = validate_receipt(receipt)
    else:
        try:
            receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"invalid receipt: {exc}", file=sys.stderr)
            return 1
        errors = validate_receipt(receipt)
    if errors:
        for error in errors:
            print(f"receipt contract error: {error}", file=sys.stderr)
        return 1
    print("LAB synthetic receipt contract valid; this is not canonical-history evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
