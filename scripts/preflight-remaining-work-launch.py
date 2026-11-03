#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import sys

BUILD_STATES = {"BUILD_GREEN", "VERIFY_READY", "VERIFYING", "VERIFIED"}
SOFT_BUILD_STATES = BUILD_STATES | {"REPAIRING"}
LANE_FOR_STATE = {"READY": "BUILD", "VERIFY_READY": "VERIFY", "REPAIRING": "REPAIR"}
ALLOWED_CONTROL_PREFIXES = (
    ".orchestration/remaining-work/prompts/",
    ".orchestration/remaining-work/launch-packs/",
    ".orchestration/remaining-work/verification/",
    ".orchestration/remaining-work/bootstrap/",
    ".orchestration/remaining-work/reconciliation/",
    "docs/project/",
)
ALLOWED_CONTROL_EXACT = {".orchestration/remaining-work/controller-state.json"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _git(root: Path, *args: str, check: bool = True):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def _result(task_id: str, status: str, *, recommended_state=None, checks=None, problems=None, **extra):
    out = {
        "task_id": task_id,
        "status": status,
        "recommended_state": recommended_state,
        "checks": checks or {},
        "problems": problems or [],
    }
    out.update(extra)
    return out


def _dependency_satisfied(state: str, kind: str) -> bool:
    if kind == "INDEPENDENT":
        return True
    if kind == "SOFT_BUILD_DEPENDENCY":
        return state in SOFT_BUILD_STATES
    if kind == "HARD_BUILD_DEPENDENCY":
        return state in BUILD_STATES
    if kind == "HARD_VERIFY_DEPENDENCY":
        return state == "VERIFIED"
    return False


def _repo_path(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.split("#", 1)[0]
    if "@" in raw and raw.startswith(("docs/", "src/", "tests/", "experiments/", "schemas/", "scripts/", ".orchestration/")):
        raw = raw.split("@", 1)[0]
    if raw == "AGENTS.md" or raw.startswith(("docs/", "src/", "tests/", "experiments/", "schemas/", "scripts/", ".orchestration/")):
        return raw.rstrip("/")
    return None


def _paths_overlap(a: str, b: str) -> bool:
    aa, bb = a.rstrip("/"), b.rstrip("/")
    return aa == bb or aa.startswith(bb + "/") or bb.startswith(aa + "/")


def _resolve_current_main(root: Path) -> tuple[str, str]:
    origin = _git(root, "rev-parse", "--verify", "origin/main", check=False)
    if origin.returncode == 0:
        return "origin/main", origin.stdout.strip()
    local = _git(root, "rev-parse", "--verify", "main", check=False)
    if local.returncode == 0:
        return "main", local.stdout.strip()
    raise RuntimeError("cannot_resolve_canonical_main")


def packet_preflight(
    root: Path,
    task_id: str,
    overlay_path: Path,
    *,
    operation_class: str | None = None,
) -> dict:
    scripts_dir = str(
        Path(__file__).resolve().parent if "__file__" in globals()
        else Path(root).resolve() / "scripts"
    )
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from remaining_work_contracts import (
        LEDGER_CONTRACT_ID,
        LEDGER_B01_COMMIT,
        LEDGER_B02_COMMIT,
        LEDGER_SNAPSHOT_PATH,
        authorized_self_transition,
        ledger_authorizes_historical_input,
        produced_blob_mismatches,
        validate_transition_ledger,
    )
    from remaining_work_authority import validate_implementation_authority

    root = Path(root).resolve()
    overlay_path = Path(overlay_path)
    if not overlay_path.is_absolute():
        overlay_path = root / overlay_path
    checks = {}

    try:
        atlas = _load(root / ".orchestration/remaining-work/atlas/atlas.json")
        index = _load(root / ".orchestration/remaining-work/prompts/index.json")
        registry = _load(root / ".orchestration/remaining-work/atlas/contract-registry.json")
    except Exception as exc:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=[f"load_error:{exc}"])

    by_id = {n.get("id"): n for n in atlas.get("nodes", []) if isinstance(n, dict)}
    node = by_id.get(task_id)
    if node is None:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["task_missing_from_atlas"])
    overlay_ref = node.get("overlay_ref")
    overlay_rel = Path(overlay_ref) if isinstance(overlay_ref, str) else None
    if (
        overlay_rel is None or not overlay_ref or overlay_rel.is_absolute()
        or ".." in overlay_rel.parts or overlay_rel.as_posix() != overlay_ref
    ):
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["overlay_ref_mismatch"])
    canonical_overlay = root / overlay_rel
    try:
        canonical_resolved = canonical_overlay.resolve(strict=True)
        supplied_resolved = overlay_path.resolve(strict=True)
        canonical_resolved.relative_to(root)
    except (OSError, ValueError):
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["overlay_ref_mismatch"])
    if canonical_overlay.is_symlink() or supplied_resolved != canonical_resolved:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["overlay_ref_mismatch"])
    if _git(root, "cat-file", "-e", f"HEAD:{overlay_ref}", check=False).returncode != 0:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["overlay_ref_mismatch"])
    try:
        overlay = _load(canonical_resolved)
    except Exception as exc:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=[f"load_error:{exc}"])
    if overlay.get("task_id") != task_id:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["overlay_task_mismatch"])
    from remaining_work_materialized_base import is_materialized_base_candidate
    materialized_generation_head = None
    materialized_candidate = is_materialized_base_candidate(
        task_id,
        overlay,
        overlay_ref=node.get("overlay_ref"),
    )
    if materialized_candidate:
        try:
            controller_state = _load(root / ".orchestration/remaining-work/controller-state.json")
            manifest_ref = controller_state.get("current_launch_pack_ref")
            manifest_rel = Path(manifest_ref) if isinstance(manifest_ref, str) else None
            if (
                manifest_rel is None or not manifest_ref or manifest_rel.is_absolute()
                or ".." in manifest_rel.parts or manifest_rel.as_posix() != manifest_ref
            ):
                raise ValueError("manifest_ref_missing")
            manifest_path = (root / manifest_rel).resolve(strict=True)
            manifest_path.relative_to(root)
            if (root / manifest_rel).is_symlink():
                raise ValueError("manifest_ref_symlink")
            manifest = _load(manifest_path)
            entries = manifest.get("entries")
            manifest_entry = next((e for e in entries if isinstance(e, dict) and e.get("task_id") == task_id), None)
            if manifest_entry is None or manifest_entry.get("overlay_ref") != node.get("overlay_ref"):
                raise ValueError("manifest_overlay_ref_mismatch")
            materialized_generation_head = manifest.get("generated_at_head")
        except Exception:
            return _result(task_id, "FAIL", recommended_state="STALE_IN_FLIGHT", problems=["materialized_base_manifest_binding_mismatch"])

    lane = LANE_FOR_STATE.get(node.get("state"))
    if lane is None:
        state = node.get("state")
        recommendation = "STALE_IN_FLIGHT" if state == "STALE_IN_FLIGHT" else "BLOCKED"
        return _result(task_id, "FAIL", recommended_state=recommendation, problems=[f"task_not_launchable:{state}"])
    checks["lane"] = lane

    if lane in {"VERIFY", "REPAIR"}:
        candidate_sha = (node.get("candidate_generation") or {}).get("sha")
        if not candidate_sha:
            return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=["candidate_generation_missing"])
        if _git(root, "cat-file", "-e", f"{candidate_sha}^{{commit}}", check=False).returncode != 0:
            return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=["candidate_commit_missing"])
        checks["candidate_generation"] = candidate_sha

    core_ref = node.get("prompt_core_ref")
    core_path = root / core_ref
    try:
        core_bytes = core_path.read_bytes()
        meta = _load(core_path.with_name("core.json"))["prompt_core"]
    except Exception as exc:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=[f"core_load_error:{exc}"])

    digest = hashlib.sha256(core_bytes).hexdigest()
    idx = next((e for e in index.get("entries", []) if e.get("task_id") == task_id), None)
    declared = {
        node.get("prompt_core_sha256"),
        meta.get("sha256"),
        idx.get("sha256") if idx else None,
    }
    checks["core_hash"] = digest
    if declared != {digest}:
        return _result(task_id, "FAIL", recommended_state="DIRTY_BY_CONTRACT_DELTA", checks=checks, problems=["core_hash_mismatch"])

    for field in ("dependencies", "write_domain", "consumed_contracts"):
        if meta.get(field) != node.get(field):
            return _result(task_id, "FAIL", recommended_state="DIRTY_BY_CONTRACT_DELTA", checks=checks, problems=[f"core_atlas_{field}_mismatch"])
    if meta.get("executor_mode") != node.get("executor_mode") or meta.get("resource_class") != node.get("resource_class"):
        return _result(task_id, "FAIL", recommended_state="DIRTY_BY_CONTRACT_DELTA", checks=checks, problems=["executor_or_resource_mismatch"])

    lane_operation = {
        "BUILD": "IMPLEMENTATION_AND_TEST_EXECUTION",
        "VERIFY": "VERIFICATION_AND_EVIDENCE_ADOPTION",
        "REPAIR": "IMPLEMENTATION_AND_TEST_EXECUTION",
    }.get(lane, lane)
    requested_operation = operation_class or lane_operation
    if node.get("implementation_authorization_required") is True:
        node_authority_ref = node.get("implementation_authorization_ref")
        if not isinstance(node_authority_ref, dict):
            return _result(
                task_id,
                "FAIL",
                recommended_state="BLOCKED",
                checks=checks,
                problems=["implementation_authorization_ref_missing"],
            )
        if overlay.get("implementation_authorization_ref") != node_authority_ref:
            return _result(
                task_id,
                "FAIL",
                recommended_state="BLOCKED",
                checks=checks,
                problems=["implementation_authorization_overlay_mismatch"],
            )
        declared_operation = overlay.get("requested_operation_class")
        if declared_operation != lane_operation:
            return _result(
                task_id,
                "FAIL",
                recommended_state="BLOCKED",
                checks=checks,
                problems=["implementation_authorization_operation_mismatch"],
            )
    authority_problem, authority_digest = validate_implementation_authority(
        root, node, meta, digest, requested_operation
    )
    if authority_problem:
        return _result(
            task_id,
            "FAIL",
            recommended_state="BLOCKED",
            checks=checks,
            problems=[authority_problem],
        )
    if node.get("implementation_authorization_required") is True:
        checks["implementation_authority"] = "MATCH"
        checks["implementation_authorization_sha256"] = authority_digest

    registry_by_id = {e.get("id"): e for e in registry.get("entries", []) if isinstance(e, dict)}
    atlas_by_id = {
        item.get("id"): item for item in atlas.get("nodes", []) if isinstance(item, dict)
    }
    ledger_path = root / LEDGER_SNAPSHOT_PATH
    opted_into_ledger = any(
        isinstance(item, dict) and item.get("id") == LEDGER_CONTRACT_ID
        for item in node.get("consumed_contracts") or []
    )
    transition_ledger = None
    if opted_into_ledger and not ledger_path.exists():
        return _result(
            task_id,
            "FAIL",
            recommended_state="DIRTY_BY_CONTRACT_DELTA",
            checks=checks,
            problems=["contract_transition_ledger_missing"],
        )
    if opted_into_ledger:
        try:
            transition_ledger = _load(ledger_path)
        except Exception:
            return _result(
                task_id,
                "FAIL",
                recommended_state="DIRTY_BY_CONTRACT_DELTA",
                checks=checks,
                problems=["contract_transition_ledger_invalid"],
            )
        try:
            ledger_errors = validate_transition_ledger(
                root, transition_ledger, registry_by_id, atlas_by_id
            )
        except (AttributeError, KeyError, TypeError, ValueError):
            ledger_errors = ["ledger_structure_invalid"]
        if ledger_errors:
            return _result(
                task_id,
                "FAIL",
                recommended_state="DIRTY_BY_CONTRACT_DELTA",
                checks=checks,
                problems=[f"contract_transition_ledger_invalid:{error}" for error in ledger_errors],
            )
        checks["contract_transition_ledger"] = "VALID"
    if produced_blob_mismatches(root, node, registry_by_id):
        return _result(
            task_id,
            "FAIL",
            recommended_state="DIRTY_BY_CONTRACT_DELTA",
            checks=checks,
            problems=["produced_contract_fingerprint_mismatch"],
        )
    for contract in node.get("consumed_contracts") or []:
        current = registry_by_id.get(contract.get("id"))
        current_fingerprint = current.get("fingerprint") if current else None
        authorized_transition = False
        if current_fingerprint != contract.get("fingerprint"):
            candidate_generation = node.get("candidate_generation")
            exact_historical_producer = {
                "H3-B01": LEDGER_B01_COMMIT,
                "H3-B02": LEDGER_B02_COMMIT,
            }.get(node.get("id"))
            if (
                transition_ledger is not None
                and contract.get("id") == LEDGER_CONTRACT_ID
                and isinstance(candidate_generation, dict)
                and candidate_generation.get("sha") == exact_historical_producer
            ):
                authorized_transition = ledger_authorizes_historical_input(
                    root,
                    node,
                    contract,
                    current_fingerprint,
                    registry_by_id,
                    transition_ledger,
                )
            elif not opted_into_ledger or contract.get("id") != LEDGER_CONTRACT_ID:
                authorized_transition = authorized_self_transition(
                    root,
                    node,
                    contract,
                    current_fingerprint,
                    registry_by_id,
                )
        if current is None or (
            current_fingerprint != contract.get("fingerprint") and not authorized_transition
        ):
            return _result(
                task_id,
                "FAIL",
                recommended_state="DIRTY_BY_CONTRACT_DELTA",
                checks=checks,
                problems=[f"contract_fingerprint_mismatch:{contract.get('id')}"],
            )
    checks["contract_fingerprints"] = "MATCH"

    dependency_heads = overlay.get("dependency_heads") or {}
    expected_dependency_ids = set()
    for dep in node.get("dependencies") or []:
        dep_id, kind = dep.get("node_id"), dep.get("kind")
        if kind == "INDEPENDENT":
            continue
        expected_dependency_ids.add(dep_id)
        upstream = by_id.get(dep_id)
        if upstream is None or not _dependency_satisfied(upstream.get("state"), kind):
            return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=[f"dependency_not_ready:{dep_id}:{kind}"])
        candidate_sha = (upstream.get("candidate_generation") or {}).get("sha")
        if not candidate_sha or dependency_heads.get(dep_id) != candidate_sha:
            return _result(task_id, "FAIL", recommended_state="STALE_IN_FLIGHT", checks=checks, problems=[f"dependency_head_mismatch:{dep_id}"])
        if _git(root, "cat-file", "-e", f"{candidate_sha}^{{commit}}", check=False).returncode != 0:
            return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=[f"dependency_commit_missing:{dep_id}"])
    if set(dependency_heads) != expected_dependency_ids:
        return _result(task_id, "FAIL", recommended_state="STALE_IN_FLIGHT", checks=checks, problems=["dependency_head_set_mismatch"])
    checks["dependencies"] = "MATCH"

    node_problem_ids = set(node.get("problem_ids") or [])
    overlay_problem_ids = set(overlay.get("open_problem_ids") or [])
    if node_problem_ids != overlay_problem_ids:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=["problem_set_mismatch"])
    if lane in {"BUILD", "VERIFY"} and overlay_problem_ids:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=["open_problems_present"])
    if lane in {"BUILD", "VERIFY"} and (overlay.get("contract_deltas") or []):
        return _result(task_id, "FAIL", recommended_state="DIRTY_BY_CONTRACT_DELTA", checks=checks, problems=["contract_deltas_present"])
    checks["problems_and_deltas"] = "CLEAR_OR_LANE_APPROPRIATE"

    resource_class = node.get("resource_class")
    overlay_leases = overlay.get("resource_leases") or {}
    atlas_leases = atlas.get("resource_leases") or {}
    lease = overlay_leases.get(resource_class)
    atlas_lease = atlas_leases.get(resource_class)
    if not isinstance(lease, int) or lease <= 0:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=[f"resource_lease_unavailable:{resource_class}"])
    if lease != atlas_lease:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=[f"resource_lease_mismatch:{resource_class}"])
    checks["resource_lease"] = lease

    base_sha = overlay.get("base_sha")
    if not isinstance(base_sha, str) or not base_sha:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=["missing_base_sha"])
    if _git(root, "cat-file", "-e", f"{base_sha}^{{commit}}", check=False).returncode != 0:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=["base_commit_missing"])

    try:
        current_main_ref, current_main_sha = _resolve_current_main(root)
    except RuntimeError as exc:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=[str(exc)])
    checks["current_main_ref"] = current_main_ref
    checks["current_main_sha"] = current_main_sha

    from remaining_work_materialized_base import validate_materialized_base
    has_materialized_metadata = materialized_candidate
    materialized_base = False
    base_is_main_ancestor = _git(root, "merge-base", "--is-ancestor", base_sha, current_main_sha, check=False).returncode == 0
    if has_materialized_metadata:
        materialized_error = validate_materialized_base(
            root, task_id, node, overlay,
            current_controller_sha=current_main_sha,
            generated_at_head=materialized_generation_head,
            overlay_ref=node.get("overlay_ref"),
        )
        if materialized_error:
            return _result(task_id, "FAIL", recommended_state="STALE_IN_FLIGHT", checks=checks, problems=[materialized_error])
        materialized_base = True
        checks["materialized_base"] = "AUTHENTICATED"
    if not materialized_base and not base_is_main_ancestor:
        return _result(task_id, "FAIL", recommended_state="STALE_IN_FLIGHT", checks=checks, problems=["base_not_ancestor_of_current_main"])

    if not materialized_base and base_sha != current_main_sha:
        diff = _git(root, "diff", "--name-only", f"{base_sha}..{current_main_sha}", check=False)
        if diff.returncode != 0:
            return _result(task_id, "FAIL", recommended_state="BLOCKED", checks=checks, problems=["cannot_diff_base_to_main"])
        changed = [line for line in diff.stdout.splitlines() if line]
        scopes = [p.rstrip("/") for p in node.get("write_domain") or []]
        for item in meta.get("read_scope") or []:
            repo_path = _repo_path(item)
            if repo_path and repo_path not in {
                ".orchestration/remaining-work/CONTROLLER_START_HERE.md",
                ".orchestration/remaining-work/atlas/atlas.json",
            }:
                scopes.append(repo_path)
        relevant = []
        for path in changed:
            if path in ALLOWED_CONTROL_EXACT or path.startswith(ALLOWED_CONTROL_PREFIXES):
                continue
            if any(_paths_overlap(path, scope) for scope in scopes):
                relevant.append(path)
        if relevant:
            return _result(
                task_id,
                "FAIL",
                recommended_state="STALE_IN_FLIGHT",
                checks=checks,
                problems=["task_relevant_main_delta:" + ",".join(sorted(relevant))],
            )
    checks["base_to_main_relevant_delta"] = "NONE" if not materialized_base else "CONTROLLER_BASE_EXACT"

    return _result(
        task_id,
        "PASS",
        checks=checks,
        lane=lane,
        base_sha=base_sha,
        current_main_sha=current_main_sha,
        branch=overlay.get("branch"),
        workspace_action="CREATE_ISOLATED_WORKTREE" if overlay.get("worktree") is None else "VERIFY_DECLARED_WORKTREE",
    )


def workspace_preflight(root: Path, task_id: str, overlay_path: Path, worktree: Path) -> dict:
    root = Path(root).resolve()
    worktree = Path(worktree).resolve()
    overlay_path = Path(overlay_path)
    if not overlay_path.is_absolute():
        overlay_path = root / overlay_path

    packet = packet_preflight(root, task_id, overlay_path)
    if packet.get("status") != "PASS":
        return packet

    try:
        overlay = _load(overlay_path)
        atlas = _load(root / ".orchestration/remaining-work/atlas/atlas.json")
    except Exception as exc:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=[f"load_error:{exc}"])

    node = next((n for n in atlas.get("nodes", []) if n.get("id") == task_id), None)
    if node is None:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["task_missing_from_atlas"])
    lane = LANE_FOR_STATE.get(node.get("state"))

    if not worktree.exists():
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["worktree_missing"])
    if _git(worktree, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["not_a_git_worktree"])

    status = _git(worktree, "status", "--porcelain", check=False)
    if status.returncode != 0 or status.stdout.strip():
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["worktree_not_clean"])

    branch = _git(worktree, "branch", "--show-current", check=False).stdout.strip()
    expected_branch = overlay.get("branch")
    head_sha = _git(worktree, "rev-parse", "HEAD", check=False).stdout.strip()
    workspace_checks = {}

    if lane == "VERIFY":
        candidate_sha = (node.get("candidate_generation") or {}).get("sha")
        if head_sha != candidate_sha:
            return _result(task_id, "FAIL", recommended_state="STALE_IN_FLIGHT", problems=["verify_head_not_exact_candidate"])
        if branch and branch != expected_branch:
            return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=[f"branch_mismatch:{branch}:{expected_branch}"])
        workspace_checks["candidate_generation"] = candidate_sha
    else:
        if not branch or branch != expected_branch:
            return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=[f"branch_mismatch:{branch}:{expected_branch}"])

    if lane in {"BUILD", "REPAIR"} and worktree == root:
        return _result(task_id, "FAIL", recommended_state="BLOCKED", problems=["write_lane_requires_isolated_worktree"])

    base_sha = overlay.get("base_sha")
    if lane in {"BUILD", "REPAIR"} and _git(
        worktree, "merge-base", "--is-ancestor", base_sha, head_sha, check=False
    ).returncode != 0:
        return _result(task_id, "FAIL", recommended_state="STALE_IN_FLIGHT", problems=["workspace_head_not_descendant_of_base"])

    authenticated_projection = (
        task_id == "H3-C03"
        and packet.get("checks", {}).get("materialized_base") == "AUTHENTICATED"
    )
    dependency_materialization = {}
    for dep_id, dep_sha in (overlay.get("dependency_heads") or {}).items():
        if not authenticated_projection and _git(worktree, "merge-base", "--is-ancestor", dep_sha, head_sha, check=False).returncode != 0:
            return _result(
                task_id,
                "FAIL",
                recommended_state="STALE_IN_FLIGHT",
                problems=[f"dependency_not_materialized:{dep_id}"],
            )
        dependency_materialization[dep_id] = dep_sha
    workspace_checks["dependency_materialization"] = dependency_materialization
    if authenticated_projection:
        workspace_checks["dependency_materialization_mode"] = "AUTHENTICATED_PROJECTION"

    return _result(
        task_id,
        "PASS",
        checks=workspace_checks,
        lane=lane,
        base_sha=base_sha,
        head_sha=head_sha,
        branch=branch,
        worktree=str(worktree),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed Remaining Work launch preflight")
    parser.add_argument("phase", choices=["packet", "workspace"])
    parser.add_argument("--root", default=None)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--overlay", required=True)
    parser.add_argument("--worktree")
    parser.add_argument("--operation-class")
    args = parser.parse_args()
    if args.root:
        root = Path(args.root).resolve()
    elif sys.argv[0] == "-c":
        parser.error("--root is required when invoked with python -c")
    else:
        root = Path(sys.argv[0]).resolve().parents[1]
    if args.phase == "packet":
        result = packet_preflight(
            root,
            args.task_id,
            Path(args.overlay),
            operation_class=args.operation_class,
        )
    else:
        if not args.worktree:
            parser.error("--worktree is required for workspace phase")
        result = workspace_preflight(root, args.task_id, Path(args.overlay), Path(args.worktree))
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
