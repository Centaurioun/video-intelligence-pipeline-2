#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from remaining_work_contracts import (
    LEDGER_CONTRACT_ID,
    LEDGER_B01_COMMIT,
    LEDGER_B02_COMMIT,
    LEDGER_SNAPSHOT_PATH,
    LEDGER_V1_BLOB,
    authorized_self_transition,
    ledger_authorizes_historical_input,
    ledger_authorizes_historical_output,
    produced_blob_mismatches,
    validate_transition_ledger,
)
from remaining_work_authority import validate_implementation_authority

ATLAS_SCHEMA = "remaining-work-atlas.v1"
LAUNCH_SCHEMA = "remaining-work-launch-pack.v1"
LEVELS = {"H0", "H1", "H2", "H3"}
STATES = {
    "PLANNED",
    "READY",
    "BUILDING",
    "BUILD_GREEN",
    "VERIFY_READY",
    "VERIFYING",
    "VERIFIED",
    "REPAIRING",
    "PARKED",
    "DIRTY_BY_CONTRACT_DELTA",
    "STALE_IN_FLIGHT",
    "SUPERSEDED",
}
DEP_KINDS = {
    "INDEPENDENT",
    "SOFT_BUILD_DEPENDENCY",
    "HARD_BUILD_DEPENDENCY",
    "HARD_VERIFY_DEPENDENCY",
}
RESOURCE_CLASSES = {
    "LIGHTWEIGHT_CPU_TEST",
    "HEAVY_CPU",
    "FFMPEG_HEAVY",
    "MODEL_MPS",
    "MIXED_HEAVY",
    "ENV_ADMIN",
}
EXECUTOR_MODES = {
    "PARALLEL_PORTFOLIO",
    "SERIAL_TIGHT_COUPLING",
    "PER_TASK_REVIEW_REQUIRED",
    "VERIFY_ONLY",
    "REPAIR_CELL",
}
CANDIDATE_STATES = {
    "BUILD_GREEN",
    "VERIFY_READY",
    "VERIFYING",
    "VERIFIED",
    "REPAIRING",
}
DIRTY_STATES = {
    "DIRTY_BY_CONTRACT_DELTA",
    "STALE_IN_FLIGHT",
    "PARKED",
    "SUPERSEDED",
}
HEX40_64 = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FROZEN_CORE_SCHEMA = "remaining-work-frozen-core.v1"
LAUNCH_BOOTSTRAP_SCHEMA = "remaining-work-launch-bootstrap.v2"
COMMON_AUTHORITY_READ_SCOPE = {"AGENTS.md", ".orchestration/remaining-work/CONTROLLER_START_HERE.md", ".orchestration/remaining-work/atlas/atlas.json"}
MANDATORY_PARALLELISM_HOOKS = {
    "DISPATCH_INDEPENDENT_H4_CONCURRENTLY",
    "ROOT_IS_CONTROL_PLANE",
    "RECYCLE_TERMINAL_CHILD_SLOTS",
    "EXCLUSIVE_WRITER_OWNERSHIP",
    "ASYNC_FEATURE_REVIEW_ON_VERIFY_FRONTIER",
    "VERIFY_DOES_NOT_BLOCK_UNRELATED_BUILD",
    "NO_STOCK_SUBAGENT_DRIVEN_DEVELOPMENT_DEFAULT",
}
RECEIPT_FIELDS = [
    "TASK",
    "STATUS",
    "BASE_SHA",
    "HEAD_SHA",
    "CHANGED_PATHS",
    "FOCUSED_TESTS",
    "CANDIDATE_GENERATION",
    "CONTRACT_DELTAS",
    "PROBLEMS",
    "DURABLE_HANDOFF",
    "UNLOCKS",
    "PUSH_STATUS",
]
LAUNCH_ONLY_CORE_FIELDS = {
    "base_sha",
    "dependency_heads",
    "branch",
    "worktree",
    "open_problem_ids",
    "contract_deltas",
    "resource_leases",
    "resolved_model_identity",
    "reconciled_at_head",
}


class Problems:
    def __init__(self):
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)

    def fail_if_any(self) -> None:
        if self.items:
            for item in self.items:
                print(f"ATLAS-VERIFY error={item}", file=sys.stderr)
            raise SystemExit(2)


def load_json(path: Path, problems: Problems, label: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        problems.add(f"missing {label}: {path}")
    except json.JSONDecodeError as exc:
        problems.add(f"invalid JSON in {label}: {path}: {exc}")
    return None


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_candidate(value) -> bool:
    if not isinstance(value, dict):
        return False
    sha = value.get("sha")
    tree = value.get("tree")
    core_v = value.get("prompt_core_version")
    overlay_v = value.get("overlay_version")
    contracts = value.get("contract_fingerprints")
    return (
        isinstance(sha, str)
        and HEX40_64.fullmatch(sha) is not None
        and isinstance(tree, str)
        and HEX40_64.fullmatch(tree) is not None
        and isinstance(core_v, str)
        and bool(core_v)
        and isinstance(overlay_v, str)
        and bool(overlay_v)
        and isinstance(contracts, dict)
        and all(
            isinstance(k, str) and isinstance(v, str) and v
            for k, v in contracts.items()
        )
    )


def dependency_satisfied(upstream_state: str, kind: str) -> bool:
    if kind == "INDEPENDENT":
        return True
    if kind == "SOFT_BUILD_DEPENDENCY":
        return upstream_state in {
            "BUILD_GREEN",
            "VERIFY_READY",
            "VERIFYING",
            "VERIFIED",
            "REPAIRING",
        }
    if kind == "HARD_BUILD_DEPENDENCY":
        return upstream_state in {
            "BUILD_GREEN",
            "VERIFY_READY",
            "VERIFYING",
            "VERIFIED",
        }
    if kind == "HARD_VERIFY_DEPENDENCY":
        return upstream_state == "VERIFIED"
    return False


def paths_overlap(a: str, b: str) -> bool:
    aa, bb = a.rstrip("/"), b.rstrip("/")
    return aa == bb or aa.startswith(bb + "/") or bb.startswith(aa + "/")


def verify_atlas(root: Path, atlas_path: Path, problems: Problems):
    atlas = load_json(atlas_path, problems, "atlas")
    if not isinstance(atlas, dict):
        return None, {}

    if atlas.get("schema_version") != ATLAS_SCHEMA:
        problems.add(f"unsupported atlas schema: {atlas.get('schema_version')!r}")
    if (
        atlas.get("active_finish_line")
        != "VERIFICATION_COMPLETE_FOR_CURRENT_AUTHORIZED_LOCAL_FIRST_SCOPE"
    ):
        problems.add("active_finish_line is missing or unsupported")
    if atlas.get("baseline_total_weight") != 100.0:
        problems.add("baseline_total_weight must equal 100.0")

    nodes = atlas.get("nodes")
    if not isinstance(nodes, list):
        problems.add("nodes must be a list")
        return atlas, {}

    ids = [n.get("id") for n in nodes if isinstance(n, dict)]
    counts = Counter(ids)
    for node_id, count in counts.items():
        if node_id is not None and count > 1:
            problems.add(f"duplicate node id: {node_id}")

    by_id = {
        n.get("id"): n
        for n in nodes
        if isinstance(n, dict) and isinstance(n.get("id"), str)
    }
    if "H0" not in by_id or by_id["H0"].get("level") != "H0":
        problems.add("H0 root node is missing")

    h3_weight = 0.0
    graph: dict[str, list[str]] = defaultdict(list)

    registry = atlas.get("contract_registry") or {}
    if not isinstance(registry, dict):
        problems.add("contract_registry must be an object")
        registry = {}

    provenance_path = root / ".orchestration/remaining-work/atlas/contract-registry.json"
    provenance = (
        load_json(provenance_path, problems, "contract registry provenance")
        if provenance_path.is_file()
        else {}
    )
    registry_by_id = {
        entry.get("id"): entry
        for entry in (provenance.get("entries", []) if isinstance(provenance, dict) else [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }

    # The ordered ledger is opt-in once the registry advances beyond its fixed
    # V1 baseline, or whenever a snapshot is present. Validate that snapshot
    # exactly once before considering any historical producer exception.
    ledger_path = root / LEDGER_SNAPSHOT_PATH
    ledger_opted_in = (
        LEDGER_CONTRACT_ID in registry
        and registry.get(LEDGER_CONTRACT_ID) != LEDGER_V1_BLOB
    ) or ledger_path.exists()
    transition_ledger = None
    ledger_valid = False
    if ledger_opted_in:
        transition_ledger = load_json(ledger_path, problems, "contract transition ledger")
        if isinstance(transition_ledger, dict):
            try:
                ledger_errors = validate_transition_ledger(
                    root, transition_ledger, registry_by_id, by_id
                )
            except Exception as exc:
                ledger_errors = [f"ledger_validation_error:{type(exc).__name__}"]
            if ledger_errors:
                for error in ledger_errors:
                    problems.add(f"contract transition ledger invalid: {error}")
            else:
                ledger_valid = True
        elif ledger_path.exists():
            problems.add("contract transition ledger must be an object")
    for contract_id, entry in registry_by_id.items():
        if contract_id in registry and entry.get("fingerprint") != registry[contract_id]:
            problems.add(
                f"contract registry provenance fingerprint mismatch: {contract_id}"
            )

    leases = atlas.get("resource_leases") or {}
    if not isinstance(leases, dict):
        problems.add("resource_leases must be an object")
        leases = {}

    for node in nodes:
        if not isinstance(node, dict):
            problems.add("node must be an object")
            continue

        node_id = node.get("id")
        level = node.get("level")
        state = node.get("state")

        if not isinstance(node_id, str) or not node_id:
            problems.add("node id must be a non-empty string")
            continue
        if level not in LEVELS:
            problems.add(f"invalid level for {node_id}: {level!r}")
        if state not in STATES:
            problems.add(f"invalid state for {node_id}: {state!r}")

        parent = node.get("parent_id")
        if level == "H0":
            if parent is not None:
                problems.add(f"H0 parent must be null: {node_id}")
        elif parent not in by_id:
            problems.add(f"unknown parent for {node_id}: {parent!r}")

        weight = node.get("weight")
        if (
            not isinstance(weight, (int, float))
            or isinstance(weight, bool)
            or weight < 0
        ):
            problems.add(f"invalid weight for {node_id}")
        elif level == "H3":
            if float(weight) <= 0:
                problems.add(f"H3 weight must be positive for {node_id}")
            h3_weight += float(weight)

        if state in CANDIDATE_STATES:
            candidate = node.get("candidate_generation")
            if candidate is None:
                problems.add(
                    f"candidate_generation required for {node_id} in {state}"
                )
            elif not valid_candidate(candidate):
                problems.add(f"invalid candidate_generation for {node_id}")
            else:
                overlay_ref = node.get("overlay_ref")
                if isinstance(overlay_ref, str) and overlay_ref:
                    overlay_path = (root / overlay_ref).resolve()
                    try:
                        overlay_path.relative_to(root.resolve())
                    except ValueError:
                        problems.add(f"overlay_ref escapes repository root for {node_id}")
                    else:
                        transition = load_json(
                            overlay_path, problems, f"launch overlay for {node_id}"
                        )
                        if (
                            isinstance(transition, dict)
                            and transition.get("candidate_sha") == candidate.get("sha")
                            and transition.get("contract_fingerprints")
                            != candidate.get("contract_fingerprints")
                        ):
                            problems.add(
                                "candidate consumed snapshot differs from candidate-bound "
                                f"launch overlay for {node_id}"
                            )

        resource_class = node.get("resource_class")
        if resource_class not in RESOURCE_CLASSES:
            problems.add(
                f"invalid resource_class for {node_id}: {resource_class!r}"
            )

        mode = node.get("executor_mode")
        if mode not in EXECUTOR_MODES:
            problems.add(f"invalid executor_mode for {node_id}: {mode!r}")

        deps = node.get("dependencies")
        if not isinstance(deps, list):
            problems.add(f"dependencies must be a list for {node_id}")
            deps = []

        for dep in deps:
            if not isinstance(dep, dict):
                problems.add(f"malformed dependency for {node_id}")
                continue
            dep_id, kind = dep.get("node_id"), dep.get("kind")
            if kind not in DEP_KINDS:
                problems.add(
                    f"invalid dependency kind for {node_id}: {kind!r}"
                )
                continue
            if kind == "INDEPENDENT":
                continue
            if dep_id not in by_id:
                problems.add(f"unknown dependency for {node_id}: {dep_id!r}")
                continue
            graph[node_id].append(dep_id)
            if state == "READY" and not dependency_satisfied(
                by_id[dep_id].get("state"), kind
            ):
                problems.add(
                    f"unsatisfied {kind} for READY node {node_id}: {dep_id}"
                )

        consumed = node.get("consumed_contracts")
        if not isinstance(consumed, list):
            problems.add(f"consumed_contracts must be a list for {node_id}")
            consumed = []

        for item in consumed:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("id"), str)
                or not isinstance(item.get("fingerprint"), str)
            ):
                problems.add(f"malformed consumed contract for {node_id}")
                continue
            expected = registry.get(item["id"])
            ledger_history_node = (
                item.get("id") == LEDGER_CONTRACT_ID
                and node_id in {"H3-B01", "H3-B02"}
                and isinstance(node.get("candidate_generation"), dict)
                and node["candidate_generation"].get("sha")
                == {"H3-B01": LEDGER_B01_COMMIT, "H3-B02": LEDGER_B02_COMMIT}.get(node_id)
            )
            self_transition_allowed = (
                (not ledger_opted_in or item["id"] != LEDGER_CONTRACT_ID)
                and authorized_self_transition(root, node, item, expected, registry_by_id)
            )
            if (
                expected is not None
                and item["fingerprint"] != expected
                and state not in DIRTY_STATES
                and not (
                    ledger_valid
                    and transition_ledger is not None
                    and ledger_history_node
                    and ledger_authorizes_historical_input(
                        root,
                        node,
                        item,
                        expected,
                        registry_by_id,
                        transition_ledger,
                    )
                )
                and not self_transition_allowed
            ):
                problems.add(
                    f"contract fingerprint mismatch for {node_id}: {item['id']}"
                )

        for contract_id in produced_blob_mismatches(
            root, node, registry_by_id, transition_ledger=transition_ledger
        ):
            problems.add(
                "produced contract fingerprint does not match candidate blob "
                f"for {node_id}: {contract_id}"
            )
        if state not in DIRTY_STATES:
            for item in node.get("produced_contracts", []):
                if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                    continue
                if (
                    item["id"] in registry
                    and registry[item["id"]] != item.get("fingerprint")
                ):
                    if (
                        ledger_valid
                        and transition_ledger is not None
                        and ledger_authorizes_historical_output(
                            root, node, item, transition_ledger
                        )
                    ):
                        continue
                    problems.add(
                        "produced contract registry fingerprint mismatch "
                        f"for {node_id}: {item['id']}"
                    )

        prompt_ref = node.get("prompt_core_ref")
        expected_hash = node.get("prompt_core_sha256")
        if prompt_ref is not None:
            if not isinstance(prompt_ref, str) or not prompt_ref:
                problems.add(f"invalid prompt_core_ref for {node_id}")
            else:
                prompt_path = (root / prompt_ref).resolve()
                try:
                    prompt_path.relative_to(root.resolve())
                except ValueError:
                    problems.add(
                        "prompt_core_ref escapes repository root "
                        f"for {node_id}: {prompt_ref}"
                    )
                    continue
                if not prompt_path.is_file():
                    problems.add(
                        f"missing prompt core for {node_id}: {prompt_ref}"
                    )
                elif (
                    not isinstance(expected_hash, str)
                    or SHA256.fullmatch(expected_hash) is None
                ):
                    problems.add(
                        f"invalid prompt core hash declaration for {node_id}"
                    )
                elif sha256_file(prompt_path) != expected_hash:
                    problems.add(
                        f"prompt core hash mismatch for {node_id}: {prompt_ref}"
                    )

    if abs(h3_weight - 100.0) > 1e-9:
        problems.add(f"H3 weight total must equal 100.0, got {h3_weight:g}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node_id: str) -> None:
        if node_id in visiting:
            problems.add(f"dependency cycle detected at {node_id}")
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for dep_id in graph.get(node_id, []):
            dfs(dep_id)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in by_id:
        dfs(node_id)

    return atlas, by_id


def verify_prompt_metadata(
    root: Path,
    by_id: dict[str, dict],
    problems: Problems,
) -> None:
    for task_id, node in by_id.items():
        if node.get("level") != "H3":
            continue
        prompt_ref = node.get("prompt_core_ref")
        if prompt_ref is None:
            continue

        prompt_path = (root / prompt_ref).resolve()
        try:
            prompt_path.relative_to(root.resolve())
        except ValueError:
            continue

        meta_path = prompt_path.with_name("core.json")
        meta = load_json(meta_path, problems, f"Frozen Core metadata for {task_id}")
        if not isinstance(meta, dict):
            continue
        if meta.get("schema_version") != FROZEN_CORE_SCHEMA:
            problems.add(f"unsupported Frozen Core schema for {task_id}")
            continue
        if meta.get("task_id") != task_id:
            problems.add(f"prompt task_id mismatch for {task_id}")

        core = meta.get("prompt_core")
        if not isinstance(core, dict):
            problems.add(f"prompt_core metadata must be an object for {task_id}")
            continue

        for launch_field in sorted(LAUNCH_ONLY_CORE_FIELDS):
            if launch_field in core:
                problems.add(
                    f"launch-only field in Frozen Core for {task_id}: {launch_field}"
                )

        expected_hash = node.get("prompt_core_sha256")
        if core.get("sha256") != expected_hash:
            problems.add(f"prompt metadata hash mismatch for {task_id}")
        if core.get("dependencies") != node.get("dependencies"):
            problems.add(f"prompt dependencies mismatch for {task_id}")
        if core.get("write_domain") != node.get("write_domain"):
            problems.add(f"prompt write_domain mismatch for {task_id}")
        if core.get("consumed_contracts") != node.get("consumed_contracts"):
            problems.add(f"prompt consumed_contracts mismatch for {task_id}")
        if core.get("executor_mode") != node.get("executor_mode"):
            problems.add(f"prompt executor_mode mismatch for {task_id}")
        if core.get("resource_class") != node.get("resource_class"):
            problems.add(f"prompt resource_class mismatch for {task_id}")

        if node.get("implementation_authorization_required") is True:
            operation_class = (
                "VERIFICATION_AND_EVIDENCE_ADOPTION"
                if node.get("state") == "VERIFY_READY"
                else "IMPLEMENTATION_AND_TEST_EXECUTION"
            )
            authority_problem, _ = validate_implementation_authority(
                root,
                node,
                core,
                expected_hash if isinstance(expected_hash, str) else "",
                operation_class,
            )
            if authority_problem:
                problems.add(f"{authority_problem} for {task_id}")

        deliverables = core.get("expected_deliverables")
        if not isinstance(deliverables, list) or not deliverables:
            problems.add(f"prompt expected_deliverables missing for {task_id}")

        read_scope = core.get("read_scope")
        if not isinstance(read_scope, list):
            read_scope = []
        for required_ref in sorted(COMMON_AUTHORITY_READ_SCOPE - set(read_scope)):
            problems.add(f"prompt common authority read_scope missing for {task_id}: {required_ref}")

        hooks = core.get("parallelism_contract")
        if not isinstance(hooks, list):
            hooks = []
        missing_hooks = MANDATORY_PARALLELISM_HOOKS - set(hooks)
        for hook in sorted(missing_hooks):
            problems.add(
                f"missing mandatory parallelism hook for {task_id}: {hook}"
            )

        verification_hooks = core.get("verification_hooks")
        if (
            not isinstance(verification_hooks, list)
            or "QUEUE_ASYNC_FEATURE_REVIEW_ON_VERIFY_FRONTIER"
            not in verification_hooks
        ):
            problems.add(
                f"missing async feature review hook for {task_id}"
            )

        receipt = core.get("receipt_contract")
        fields = receipt.get("required_fields") if isinstance(receipt, dict) else None
        if fields != RECEIPT_FIELDS:
            problems.add(f"prompt receipt contract mismatch for {task_id}")

        if (
            not isinstance(core.get("version"), str)
            or not core.get("version")
            or not isinstance(core.get("goal"), str)
            or not core.get("goal")
        ):
            problems.add(f"prompt version/goal missing for {task_id}")


def verify_launch_pack(
    root: Path,
    launch_path: Path,
    atlas,
    by_id,
    problems: Problems,
    *,
    historical: bool = False,
) -> None:
    pack = load_json(launch_path, problems, "launch pack")
    if not isinstance(pack, dict):
        return

    if pack.get("schema_version") != LAUNCH_SCHEMA:
        problems.add(
            f"unsupported launch pack schema: {pack.get('schema_version')!r}"
        )

    bootstrap = pack.get("launch_bootstrap")
    bootstrap_text = None
    if not isinstance(bootstrap, dict):
        problems.add("launch bootstrap binding missing")
    else:
        for key in ("version", "sha256", "ref", "metadata_ref", "preflight_script_ref"):
            if not isinstance(bootstrap.get(key), str) or not bootstrap.get(key):
                problems.add(f"launch bootstrap binding missing {key}")
        meta_ref = bootstrap.get("metadata_ref")
        if isinstance(meta_ref, str) and meta_ref:
            meta_path = (root / meta_ref).resolve()
            try:
                meta_path.relative_to(root.resolve())
            except ValueError:
                problems.add("launch bootstrap metadata_ref escapes repository root")
            else:
                meta = load_json(meta_path, problems, "launch bootstrap metadata")
                if isinstance(meta, dict):
                    if meta.get("schema_version") != LAUNCH_BOOTSTRAP_SCHEMA:
                        problems.add("unsupported launch bootstrap schema")
                    for key in ("version", "sha256", "ref", "preflight_script_ref"):
                        if bootstrap.get(key) != meta.get(key):
                            problems.add(f"launch bootstrap {key} mismatch")
                    text_ref = meta.get("ref")
                    if isinstance(text_ref, str) and text_ref:
                        text_path = (root / text_ref).resolve()
                        try:
                            text_path.relative_to(root.resolve())
                        except ValueError:
                            problems.add("launch bootstrap ref escapes repository root")
                        else:
                            if text_path.exists():
                                actual = sha256_file(text_path)
                                if actual != meta.get("sha256"):
                                    problems.add("launch bootstrap hash mismatch")
                                bootstrap_text = text_path.read_text(encoding="utf-8")
                            else:
                                problems.add("missing launch bootstrap text")
                    script_ref = meta.get("preflight_script_ref")
                    if isinstance(script_ref, str) and script_ref:
                        script_path = (root / script_ref).resolve()
                        try:
                            script_path.relative_to(root.resolve())
                        except ValueError:
                            problems.add("launch bootstrap preflight script escapes repository root")
                        else:
                            if not script_path.exists():
                                problems.add("missing launch bootstrap preflight script")

    entries = pack.get("entries")
    if not isinstance(entries, list):
        problems.add("launch pack entries must be a list")
        return

    expected_state = {"BUILD": "READY", "VERIFY": "VERIFY_READY", "REPAIR": "REPAIRING"}
    task_ids: list[str] = []
    normalized: list[tuple[str, str, str, str]] = []
    historical_resource_leases = None

    for entry in entries:
        task_id = entry.get("task_id") if isinstance(entry, dict) else None
        if not isinstance(task_id, str) or task_id not in by_id:
            problems.add(f"unknown launch task: {task_id!r}")
            continue
        task_ids.append(task_id)

        lane = entry.get("lane", "BUILD")
        if lane not in expected_state:
            problems.add(f"invalid launch lane for {task_id}: {lane!r}")
            continue

        state = entry.get("state") if historical else by_id[task_id].get("state")
        if state != expected_state[lane]:
            if lane == "BUILD":
                problems.add(
                    f"launch entry is not READY: {task_id} state={state}"
                )
            else:
                problems.add(
                    f"launch entry state/lane mismatch: {task_id} lane={lane} state={state}"
                )

        write_mode = entry.get(
            "write_mode", "READ_ONLY" if lane == "VERIFY" else "WRITE"
        )
        if lane == "VERIFY" and write_mode != "READ_ONLY":
            problems.add(f"VERIFY launch entry must be READ_ONLY: {task_id}")
        if lane != "VERIFY" and write_mode != "WRITE":
            problems.add(f"{lane} launch entry must be WRITE: {task_id}")

        expected_executor = entry.get("executor_mode") if historical else (
            "VERIFY_ONLY"
            if lane == "VERIFY"
            else "REPAIR_CELL"
            if lane == "REPAIR"
            else by_id[task_id].get("executor_mode")
        )
        executor = entry.get("executor_mode", expected_executor)
        if executor != expected_executor:
            problems.add(
                f"launch executor mismatch for {task_id}: {executor!r} != {expected_executor!r}"
            )

        expected_resource = entry.get("resource_class") if historical else (
            "LIGHTWEIGHT_CPU_TEST"
            if lane == "VERIFY"
            else by_id[task_id].get("resource_class")
        )
        resource = entry.get("resource_class", expected_resource)
        if resource != expected_resource:
            problems.add(
                f"launch resource mismatch for {task_id}: {resource!r} != {expected_resource!r}"
            )

        prompt_ref = entry.get("prompt_ref")
        core_ref = entry.get("core_ref")
        overlay_ref = entry.get("overlay_ref")
        for ref_name, ref_value in (
            ("prompt_ref", prompt_ref),
            ("core_ref", core_ref),
            ("overlay_ref", overlay_ref),
        ):
            if not isinstance(ref_value, str) or not ref_value:
                problems.add(f"launch {ref_name} missing for {task_id}")
        if not historical:
            expected_core_ref = by_id[task_id].get("prompt_core_ref")
            expected_overlay_ref = by_id[task_id].get("overlay_ref")
            if core_ref != expected_core_ref:
                problems.add(f"launch core_ref mismatch for {task_id}")
            if overlay_ref != expected_overlay_ref:
                problems.add(f"launch overlay_ref mismatch for {task_id}")

        if bootstrap_text is not None and isinstance(prompt_ref, str) and prompt_ref:
            prompt_path = (launch_path.parent / prompt_ref).resolve()
            try:
                prompt_path.relative_to(root.resolve())
            except ValueError:
                problems.add(f"launch prompt_ref escapes repository root for {task_id}")
            else:
                if not prompt_path.exists():
                    problems.add(f"missing launch prompt for {task_id}")
                else:
                    prompt_text = prompt_path.read_text(encoding="utf-8")
                    marker = "## Launch Bootstrap v2"
                    overlay_marker = "## Launch Overlay"
                    core_marker = "## Frozen Core" if lane == "BUILD" else "## Governing Frozen Core"
                    if marker not in prompt_text or bootstrap_text not in prompt_text:
                        problems.add(f"launch bootstrap missing from prompt for {task_id}")
                    elif overlay_marker not in prompt_text or prompt_text.index(marker) > prompt_text.index(overlay_marker):
                        problems.add(f"launch bootstrap order invalid for {task_id}")

                    if overlay_marker not in prompt_text or core_marker not in prompt_text:
                        problems.add(f"launch prompt overlay/core markers missing for {task_id}")
                    else:
                        overlay_section = prompt_text.split(overlay_marker, 1)[1].split(core_marker, 1)[0].strip()
                        if overlay_section.startswith("```json"):
                            overlay_section = overlay_section[len("```json"):].lstrip("\n")
                        if overlay_section.endswith("```"):
                            overlay_section = overlay_section[:-3].rstrip()
                        try:
                            embedded_overlay = json.loads(overlay_section)
                        except json.JSONDecodeError:
                            problems.add(f"launch prompt overlay invalid JSON for {task_id}")
                        else:
                            generated_at_head = pack.get("generated_at_head")
                            from remaining_work_materialized_base import is_materialized_base_candidate
                            materialized_metadata = (
                                not historical
                                and is_materialized_base_candidate(task_id, embedded_overlay)
                            )
                            if embedded_overlay.get("base_sha") != generated_at_head and not materialized_metadata:
                                problems.add(f"launch overlay base/generation mismatch for {task_id}")
                            if historical:
                                snapshot_leases = embedded_overlay.get("resource_leases")
                                if not isinstance(snapshot_leases, dict):
                                    problems.add(f"historical resource leases missing for {task_id}")
                                elif historical_resource_leases is None:
                                    historical_resource_leases = snapshot_leases
                                elif snapshot_leases != historical_resource_leases:
                                    problems.add("historical launch resource leases disagree")
                            elif isinstance(overlay_ref, str) and overlay_ref:
                                overlay_path = (root / overlay_ref).resolve()
                                try:
                                    overlay_path.relative_to(root.resolve())
                                except ValueError:
                                    problems.add(f"launch overlay_ref escapes repository root for {task_id}")
                                else:
                                    exact_overlay = load_json(overlay_path, problems, f"launch overlay for {task_id}")
                                    if isinstance(exact_overlay, dict) and embedded_overlay != exact_overlay:
                                        problems.add(f"launch prompt overlay mismatch for {task_id}")
                                    if isinstance(exact_overlay, dict):
                                        if exact_overlay.get("base_sha") != generated_at_head and not materialized_metadata:
                                            problems.add(f"launch overlay base/generation mismatch for {task_id}")
                                        if not historical and is_materialized_base_candidate(task_id, exact_overlay):
                                            from remaining_work_materialized_base import validate_materialized_base
                                            current_main = subprocess.run(
                                                ["git", "-C", str(root), "rev-parse", "--verify", "origin/main"],
                                                text=True, capture_output=True, check=False,
                                            )
                                            if current_main.returncode != 0:
                                                current_main = subprocess.run(
                                                    ["git", "-C", str(root), "rev-parse", "--verify", "main"],
                                                    text=True, capture_output=True, check=False,
                                                )
                                            materialized_error = validate_materialized_base(
                                                root, task_id, by_id[task_id], exact_overlay,
                                                current_controller_sha=current_main.stdout.strip() if current_main.returncode == 0 else "",
                                                generated_at_head=generated_at_head,
                                                overlay_ref=overlay_ref,
                                            )
                                            if materialized_error:
                                                problems.add(f"launch {materialized_error} for {task_id}")

                        core_section = prompt_text.split(core_marker, 1)[1]
                        if core_section.startswith("\n\n"):
                            core_section = core_section[2:]
                        elif core_section.startswith("\n"):
                            core_section = core_section[1:]
                        if isinstance(core_ref, str) and core_ref:
                            core_path = (root / core_ref).resolve()
                            try:
                                core_path.relative_to(root.resolve())
                            except ValueError:
                                problems.add(f"launch core_ref escapes repository root for {task_id}")
                            else:
                                if not core_path.exists():
                                    problems.add(f"missing launch core for {task_id}")
                                else:
                                    exact_core = core_path.read_text(encoding="utf-8")
                                    if core_section != exact_core:
                                        problems.add(f"launch prompt core mismatch for {task_id}")

        normalized.append((task_id, lane, write_mode, resource))

    for task_id, count in Counter(task_ids).items():
        if count > 1:
            problems.add(f"duplicate launch task: {task_id}")

    owned: list[tuple[str, str]] = []
    for task_id, _lane, write_mode, _resource in normalized:
        if write_mode != "WRITE":
            continue
        for path in by_id[task_id].get("write_domain") or []:
            if not isinstance(path, str):
                problems.add(f"invalid write_domain path for {task_id}")
                continue
            for other_task, other_path in owned:
                if paths_overlap(path, other_path):
                    problems.add(
                        "overlapping write ownership: "
                        f"{other_task}:{other_path} vs {task_id}:{path}"
                    )
            owned.append((task_id, path))

    counts = Counter(resource for _task, _lane, _mode, resource in normalized)
    leases = (
        historical_resource_leases
        if historical
        else atlas.get("resource_leases") or {}
    )
    for resource_class, count in counts.items():
        limit = leases.get(resource_class)
        if isinstance(limit, int) and count > limit:
            problems.add(
                "resource lease exceeded: "
                f"{resource_class} count={count} limit={limit}"
            )

def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify Remaining Work Atlas and optional Launch Pack"
    )
    parser.add_argument(
        "--root",
        default=None,
        help="repository root; defaults to script parent repo",
    )
    parser.add_argument(
        "--atlas",
        default=None,
        help="atlas JSON path; defaults under .orchestration",
    )
    parser.add_argument(
        "--launch-pack",
        default=None,
        help="optional launch-pack manifest path",
    )
    parser.add_argument(
        "--historical-launch-pack",
        action="store_true",
        help="validate a saved launch packet against its embedded generation evidence, not current Atlas state",
    )
    parser.add_argument(
        "--require-prompt-metadata",
        action="store_true",
        help="require and validate Frozen Core core.json metadata for H3 nodes that have prompt refs",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_root = Path(__file__).resolve().parents[1]
    root = Path(args.root).resolve() if args.root else script_root
    atlas_path = (
        Path(args.atlas).resolve()
        if args.atlas
        else root / ".orchestration/remaining-work/atlas/atlas.json"
    )

    problems = Problems()
    atlas, by_id = verify_atlas(root, atlas_path, problems)

    if args.require_prompt_metadata and atlas is not None:
        verify_prompt_metadata(root, by_id, problems)

    if args.launch_pack and atlas is not None:
        verify_launch_pack(
            root,
            Path(args.launch_pack).resolve(),
            atlas,
            by_id,
            problems,
            historical=args.historical_launch_pack,
        )

    problems.fail_if_any()
    print(f"ATLAS-VERIFY status=PASS atlas={atlas_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
