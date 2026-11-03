"""Fail-closed validation for the one authorized H3-E02 dependency materialization."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

TASK_ID = "H3-E02"
CONTROLLER_BASE = "0f5b2c22965870578a4f57bd5fdcf84569c07a89"
DEPENDENCY_SHA = "5a092cd27f7eebfa61c6e2736e537aa0f2899d24"
MERGE_SHA = "75034492ed565a68df1d1aedf47f7da400a1c804"
EXECUTION_BASE = "435050190ed520704d8b4d1cdd83718a0623b54c"
GENERATION_HEAD = "cb1739fe380cf707d3717a9a630c07f4a0a86abd"
RECONCILIATION_REF = ".orchestration/remaining-work/runs/H3-E02/dependency-materialization-reconciliation.json"
RECONCILIATION_SHA256 = "d06b605fa8fdfb1d432d1b8777fc23b6126d82c893d5bba90f8c9cae2c3e0b2f"
EXPECTED_OVERLAY = ".orchestration/remaining-work/prompts/H3-E02/overlay-successor-004.json"
C03_TASK_ID = "H3-C03"
C03_OVERLAY = ".orchestration/remaining-work/prompts/H3-C03/overlay-after-dependency-closure-reconciliation-001.json"
C03_RECORD = ".orchestration/remaining-work/runs/H3-C03/dependency-closure-reconciliation-20261006.json"
C03_MANIFEST_COMMIT = "0ac5348d3ce2ce2b3730b9c80e996f8db2634cdf"
C03_MANIFEST_PATH = "docs/agent-runs/run-20261006-c03-shared-authority-reconciliation/dcm1-materialization-manifest.json"
C03_MANIFEST_BLOB = "97be49142221ecef65b67a4e69a54a9b0a222beb"
C03_MANIFEST_SHA256 = "f7051945248b5a1e02cd7b6f5c31302a5ada4fc130de6df0f84105e863d8de5a"
C03_DCM1 = "da993f1f009486d9b092fa6325db965882cc2e09"
C03_DCM1_TREE = "cbcb32e238e4befe2747b4d2660d73b5fdf78b4e"
C03_DEPENDENCIES = {"H3-C02": "44a7d4d931d5219efc781f8da54fab850ba8bcc1", "H3-B02": "f7f415648e4e7521502efe8da7fd0f352d8fc7bc"}


def is_materialized_base_candidate(
    task_id: str,
    overlay: dict,
    *,
    overlay_ref: str | None = None,
) -> bool:
    """Identify records carrying a pinned marker for the one historical E02 exception."""
    if task_id == C03_TASK_ID and overlay_ref == C03_OVERLAY:
        return True
    if task_id == TASK_ID and overlay_ref == EXPECTED_OVERLAY:
        return True
    refs = overlay.get("dependency_materialization_reconciliation_ref")
    return any((
        overlay.get("base_sha") == EXECUTION_BASE,
        overlay.get("candidate_sha") == DEPENDENCY_SHA,
        overlay.get("candidate_tree") == "994030816eca9db050a3ba53945baeb31b6c11a3",
        overlay.get("dependency_heads") == {"H3-E01": DEPENDENCY_SHA},
        overlay.get("reconciled_at_head") == EXECUTION_BASE,
        isinstance(refs, dict)
        and (refs.get("path") == RECONCILIATION_REF or refs.get("sha256") == RECONCILIATION_SHA256),
    ))


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)


def _blob(root: Path, revision: str, path: str) -> str | None:
    result = _git(root, "rev-parse", "--verify", f"{revision}:{path}")
    return result.stdout.strip() if result.returncode == 0 else None


def validate_materialized_base(
    root: Path,
    task_id: str,
    node: dict,
    overlay: dict,
    *,
    current_controller_sha: str,
    generated_at_head: str | None = None,
    overlay_ref: str | None = None,
) -> str | None:
    """Return a stable failure code, or None when the exact pinned topology matches."""
    if task_id == C03_TASK_ID and overlay_ref == C03_OVERLAY:
        return _validate_c03_profile(root, node, overlay, current_controller_sha, generated_at_head)
    if not is_materialized_base_candidate(task_id, overlay, overlay_ref=overlay_ref):
        return None
    if "dependency_materialization_reconciliation_ref" not in overlay:
        return "materialized_base_metadata_missing"
    if task_id != TASK_ID:
        return "materialized_base_metadata_on_nonmaterialized_task"
    if overlay_ref != EXPECTED_OVERLAY:
        return "materialized_base_overlay_binding_mismatch"
    if current_controller_sha != CONTROLLER_BASE:
        return "materialized_base_controller_base_mismatch"
    if overlay.get("base_sha") != EXECUTION_BASE:
        return "materialized_base_execution_base_mismatch"
    if generated_at_head != GENERATION_HEAD:
        return "materialized_base_generated_at_head_mismatch"

    refs = overlay.get("dependency_materialization_reconciliation_ref")
    if not isinstance(refs, dict) or refs != {
        "disposition": "KEEP_CURRENT_CONTROLLER_WHOLE_FILE",
        "overrides": refs.get("overrides") if isinstance(refs, dict) else None,
        "path": RECONCILIATION_REF,
        "sha256": RECONCILIATION_SHA256,
    }:
        return "materialized_base_reconciliation_binding_mismatch"
    if overlay.get("dependency_heads") != {"H3-E01": DEPENDENCY_SHA}:
        return "materialized_base_dependency_mismatch"
    if overlay.get("candidate_sha") != DEPENDENCY_SHA or overlay.get("candidate_tree") != "994030816eca9db050a3ba53945baeb31b6c11a3":
        return "materialized_base_dependency_tree_mismatch"
    if node.get("dependencies") != [{"node_id": "H3-E01", "kind": "HARD_BUILD_DEPENDENCY"}]:
        return "materialized_base_atlas_dependency_mismatch"
    record_path = root / RECONCILIATION_REF
    try:
        raw = record_path.read_bytes()
        record = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "materialized_base_reconciliation_unavailable"
    if hashlib.sha256(raw).hexdigest() != RECONCILIATION_SHA256:
        return "materialized_base_reconciliation_digest_mismatch"
    if not isinstance(record, dict):
        return "materialized_base_reconciliation_invalid"
    if (
        record.get("schema_version") != "remaining-work-dependency-materialization-reconciliation.v1"
        or record.get("task_id") != TASK_ID
        or record.get("controller_base_sha") != CONTROLLER_BASE
        or record.get("dependency_sha") != DEPENDENCY_SHA
        or record.get("dependency_tree") != "994030816eca9db050a3ba53945baeb31b6c11a3"
        or record.get("materialization_merge_commit") != MERGE_SHA
        or record.get("materialization_merge_tree") != "4515616ccfbc58cfba26a632369945530aaad772"
        or record.get("auto_merge_tree") != "c7af2032fdbc5d0931f159c6462337d36cc7afcf"
        or record.get("semantic_disposition") != "KEEP_CURRENT_CONTROLLER_WHOLE_FILE"
        or overlay.get("reconciled_at_head") != EXECUTION_BASE
        or record.get("task_id") != task_id
        or record.get("extra_conflict_policy") != "STOP"
        or record.get("field_level_merge") is not False
        or record.get("product_conflict_exception") is not False
        or record.get("conflict_paths") != record.get("simulated_conflict_paths")
        or record.get("product_conflicts") != []
        or record.get("source_test_conflict_paths") != []
        or record.get("preservation") != {
            "controller_blobs_preserved_whole_file": True,
            "dependency_commit_is_merge_parent": True,
            "exact_dependency_ancestry": True,
            "historical_e01_evidence_reachable": True,
            "product_and_test_changes_materialized_without_conflicts": True,
        }
    ):
        return "materialized_base_reconciliation_evidence_mismatch"

    if not isinstance(refs.get("overrides"), dict) or refs["overrides"] != record.get("controller_winning_blobs"):
        return "materialized_base_controller_blob_manifest_mismatch"
    merge = _git(root, "cat-file", "-e", f"{MERGE_SHA}^{{commit}}")
    if merge.returncode != 0:
        return "materialized_base_merge_commit_missing"
    for path, blob in record["controller_winning_blobs"].items():
        if _blob(root, CONTROLLER_BASE, path) != blob or _blob(root, MERGE_SHA, path) != blob:
            return "materialized_base_controller_blob_mismatch"
    product_test_blobs = record.get("source_test_merge_blobs")
    if not isinstance(product_test_blobs, dict) or not product_test_blobs:
        return "materialized_base_product_blob_manifest_missing"
    for path, blob in product_test_blobs.items():
        if _blob(root, MERGE_SHA, path) != blob:
            return "materialized_base_product_blob_mismatch"

    parent_line = _git(root, "rev-list", "--parents", "-n", "1", MERGE_SHA)
    if parent_line.returncode != 0 or parent_line.stdout.strip().split()[1:] != [CONTROLLER_BASE, DEPENDENCY_SHA]:
        return "materialized_base_merge_parent_mismatch"
    merge_tree = _git(root, "rev-parse", f"{MERGE_SHA}^{{tree}}")
    if merge_tree.returncode != 0 or merge_tree.stdout.strip() != record.get("materialization_merge_tree"):
        return "materialized_base_merge_tree_mismatch"

    merge_tree_result = _git(root, "merge-tree", "--write-tree", CONTROLLER_BASE, DEPENDENCY_SHA)
    if merge_tree_result.returncode not in (0, 1):
        return "materialized_base_conflict_simulation_unavailable"
    lines = merge_tree_result.stdout.splitlines()
    conflict_paths = sorted(line.rsplit(" in ", 1)[-1].strip() for line in lines if line.startswith("CONFLICT "))
    if lines[0].strip() != record.get("auto_merge_tree") or conflict_paths != sorted(record["conflict_paths"]):
        return "materialized_base_conflict_set_mismatch"

    for sha in (CONTROLLER_BASE, DEPENDENCY_SHA):
        if _git(root, "merge-base", "--is-ancestor", sha, EXECUTION_BASE).returncode != 0:
            return "materialized_base_execution_ancestry_mismatch"
    if _git(root, "merge-base", "--is-ancestor", MERGE_SHA, EXECUTION_BASE).returncode != 0:
        return "materialized_base_merge_not_in_execution_ancestry"
    if _git(root, "merge-base", "--is-ancestor", EXECUTION_BASE, GENERATION_HEAD).returncode != 0:
        return "materialized_base_generation_ancestry_mismatch"
    return None


def _validate_c03_profile(root: Path, node: dict, overlay: dict, current_controller_sha: str, generated_at_head: str | None) -> str | None:
    refs = overlay.get("dependency_materialization_reconciliation_ref")
    if not isinstance(refs, dict) or refs.get("path") != C03_RECORD:
        return "materialized_base_metadata_missing"
    execution_base = overlay.get("base_sha")
    if not isinstance(execution_base, str) or _git(root, "cat-file", "-e", f"{execution_base}^{{commit}}").returncode != 0:
        return "materialized_base_execution_base_mismatch"
    if _git(root, "merge-base", "--is-ancestor", C03_DCM1, execution_base).returncode != 0:
        return "materialized_base_execution_ancestry_mismatch"
    if _git(root, "rev-parse", f"{C03_DCM1}^{{tree}}").stdout.strip() != C03_DCM1_TREE:
        return "materialized_base_dcm1_mismatch"
    if overlay.get("dependency_heads") != C03_DEPENDENCIES:
        return "materialized_base_dependency_mismatch"
    if overlay.get("version") != "h3-c03-overlay-after-dependency-closure-reconciliation-v1.0.0":
        return "materialized_base_overlay_binding_mismatch"
    expected_dependencies = [{"node_id": "H3-C02", "kind": "HARD_BUILD_DEPENDENCY"}, {"node_id": "H3-B02", "kind": "HARD_BUILD_DEPENDENCY"}]
    if node.get("dependencies") != expected_dependencies:
        return "materialized_base_atlas_dependency_mismatch"
    try:
        raw_manifest = _git(root, "show", f"{C03_MANIFEST_COMMIT}:{C03_MANIFEST_PATH}")
        manifest = json.loads(raw_manifest.stdout)
        record_raw = (root / C03_RECORD).read_bytes()
        overlay_raw = (root / C03_OVERLAY).read_bytes()
        record = json.loads(record_raw)
    except (OSError, json.JSONDecodeError):
        return "materialized_base_reconciliation_unavailable"
    if (_blob(root, C03_MANIFEST_COMMIT, C03_MANIFEST_PATH) != C03_MANIFEST_BLOB
            or manifest.get("manifest_sha256") != C03_MANIFEST_SHA256
            or hashlib.sha256(record_raw).hexdigest() != refs.get("sha256")):
        return "materialized_base_manifest_binding_mismatch"
    if record.get("task_id") != C03_TASK_ID or record.get("dcm1_sha") != C03_DCM1 or record.get("dcm1_tree") != C03_DCM1_TREE:
        return "materialized_base_reconciliation_evidence_mismatch"
    if record.get("manifest_sha256") != C03_MANIFEST_SHA256 or record.get("execution_base_sha") != execution_base or record.get("dependency_heads") != C03_DEPENDENCIES:
        return "materialized_base_reconciliation_evidence_mismatch"
    if current_controller_sha != record.get("canonical_main_at_activation"):
        return "materialized_base_controller_base_mismatch"
    entries = manifest.get("entries", [])
    targets = {entry.get("path"): entry.get("target_blob") for entry in entries}
    if (len(targets) != 18 or any(path.startswith(".orchestration/") for path in targets)
            or any(entry.get("action") not in {"ADD", "REPLACE"} for entry in entries)
            or sum(entry.get("action") == "REPLACE" for entry in entries) != 14
            or sum(entry.get("action") == "ADD" for entry in entries) != 4):
        return "materialized_base_manifest_binding_mismatch"
    if any(_blob(root, C03_DCM1, path) != blob or _blob(root, execution_base, path) != blob for path, blob in targets.items()):
        return "materialized_base_product_blob_mismatch"
    if record.get("target_blobs") != targets or record.get("overlay_ref") != C03_OVERLAY:
        return "materialized_base_reconciliation_evidence_mismatch"
    if not isinstance(generated_at_head, str) or _git(root, "merge-base", "--is-ancestor", execution_base, generated_at_head).returncode != 0:
        return "materialized_base_generated_at_head_mismatch"
    record_blob = subprocess.run(["git", "-C", str(root), "hash-object", "--stdin"], input=record_raw, capture_output=True, check=False).stdout.decode().strip()
    overlay_blob = subprocess.run(["git", "-C", str(root), "hash-object", "--stdin"], input=overlay_raw, capture_output=True, check=False).stdout.decode().strip()
    if _blob(root, generated_at_head, C03_RECORD) != record_blob or _blob(root, generated_at_head, C03_OVERLAY) != overlay_blob:
        return "materialized_base_generated_at_head_mismatch"
    return None
