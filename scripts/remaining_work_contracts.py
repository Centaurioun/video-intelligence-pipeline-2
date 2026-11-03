from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from gate0.canonical_json import canonical_bytes

GIT_BLOB = re.compile(r"^([0-9a-f]{40})$")
GIT_COMMIT = GIT_BLOB
LEDGER_CONTRACT_ID = "persistent_index_indexer"
LEDGER_SOURCE_PATH = "experiments/persistent_local_index/indexer.py"
LEDGER_GENESIS_COMMIT = "0f5b2c22965870578a4f57bd5fdcf84569c07a89"
LEDGER_GENESIS_TREE = "6f90ab49e1ecea10b2f416e047891f594e17f447"
LEDGER_V1_BLOB = "b61db24259cf53f76b687ea572c24bee0037295b"
LEDGER_B01_COMMIT = "4bbb267c654dbe3c251041da4b297d7ef1f48556"
LEDGER_B01_TREE = "ad288a556200e2f0aac31cca9c2b1987db079aad"
LEDGER_B01_RESULT = "f5c936dc039890ad6411cde7218a82e0a2879dd7"
LEDGER_B02_COMMIT = "f7f415648e4e7521502efe8da7fd0f352d8fc7bc"
LEDGER_B02_TREE = "bf65b439798ab9484b77135406fdbf36256f98aa"
LEDGER_B02_RESULT = "8400a3fb52945a539995b041f72f1c1370f64d40"
LEDGER_C02_COMMIT = "44a7d4d931d5219efc781f8da54fab850ba8bcc1"
LEDGER_C02_TREE = "5206b1f5c326596a02ec2295202db374f8d42ce5"
LEDGER_C02_RESULT = "875122c70f9b35bd6fae2a68d734f602bb7aeb84"
LEDGER_C02_EVIDENCE_COMMIT = "2cd6095587a957575f02c2b996e881ee26c6285a"
LEDGER_C02_EVIDENCE_PATH = ".orchestration/remaining-work/prompts/H3-C02/overlay-verify-batch008.json"
LEDGER_C02_EVIDENCE_BLOB = "8fbeb4301b9245968108975cc27a7fbb27d863e2"
LEDGER_B02_OVERLAY_PATH = ".orchestration/remaining-work/prompts/H3-B02/overlay.json"
LEDGER_B02_OVERLAY_BLOB = "50c754c3be5b09a5b71fdcf9d2748563f3922240"
LEDGER_SNAPSHOT_PATH = ".orchestration/remaining-work/atlas/contract-transition-ledger.json"
LEDGER_ANCHOR_BLOBS = {
    ".orchestration/remaining-work/atlas/atlas.json": "61c6dac477427cc44ab9b782bc06c517daa67b69",
    ".orchestration/remaining-work/atlas/contract-registry.json": "ec94c2ac5e2a13fe09acad0ee8a2759ab59ac8a8",
    ".orchestration/remaining-work/prompts/H3-B01/core.json": "89d09cf417ef54084a831c23dc2ccdc5466aad10",
    ".orchestration/remaining-work/prompts/H3-B01/core.md": "012ad8b34240198131ea1174952d30f9b212d1ba",
    ".orchestration/remaining-work/prompts/H3-B01/overlay.json": "6d983af355dc72b6b41a3adeaa7fc384c7b483a2",
    ".orchestration/remaining-work/prompts/H3-B02/core.json": "4ac7e07bf9585dbb6a137502a237c867567c2762",
    ".orchestration/remaining-work/prompts/H3-B02/core.md": "8dbb3b192db40310e86ef67b96dca2facefb5c78",
    LEDGER_B02_OVERLAY_PATH: LEDGER_B02_OVERLAY_BLOB,
    LEDGER_SOURCE_PATH: LEDGER_V1_BLOB,
}


def canonical_transition_ledger_bytes(ledger: dict) -> bytes:
    """Serialize a transition ledger with canonical object keys and ordered arrays."""
    return canonical_bytes(ledger)


def transition_ledger_digest(ledger: dict) -> str:
    """Hash the canonical ledger payload, excluding its self-referential digest."""
    payload = {key: value for key, value in ledger.items() if key != "digest"}
    return hashlib.sha256(canonical_transition_ledger_bytes(payload)).hexdigest()


def _field(value: dict, *names: str) -> Any:
    for name in names:
        if name in value:
            return value[name]
    return None


def _git_object_text(root: Path, expression: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", expression],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _safe_source_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        return False
    parts = value.split("/")
    return all(part not in {"", ".", ".."} for part in parts)


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, descendant],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _validate_immutable_git_evidence(
    root: Path,
    baseline: dict,
    edges: list,
    atlas_by_id: dict,
    *,
    strict_approved_history: bool = False,
) -> list[str]:
    errors: list[str] = []
    for path, expected_blob in LEDGER_ANCHOR_BLOBS.items():
        actual = _git_object_text(root, f"{LEDGER_GENESIS_COMMIT}:{path}")
        if actual != expected_blob:
            errors.append("ledger_baseline_invalid")
            break
    baseline_commit = _field(baseline, "commit_sha", "commit")
    baseline_tree = _field(baseline, "tree_sha", "tree")
    baseline_path = _field(baseline, "source_path", "source")
    baseline_blob = _field(baseline, "blob_sha", "blob")
    if (
        baseline_commit != LEDGER_GENESIS_COMMIT
        or _git_object_text(root, f"{baseline_commit}^{{commit}}") != LEDGER_GENESIS_COMMIT
        or baseline_tree != LEDGER_GENESIS_TREE
        or _git_object_text(root, f"{baseline_commit}^{{tree}}") != LEDGER_GENESIS_TREE
        or baseline_path != LEDGER_SOURCE_PATH
        or baseline_blob != LEDGER_V1_BLOB
        or _git_object_text(root, f"{baseline_commit}:{baseline_path}") != LEDGER_V1_BLOB
    ):
        errors.append("ledger_baseline_invalid")

    previous_commit = baseline_commit
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            continue
        candidate = _field(edge, "candidate_commit_sha", "candidate_commit")
        tree = _field(edge, "candidate_tree_sha", "candidate_tree")
        path = _field(edge, "source_path", "source")
        blob = _field(edge, "source_blob_sha", "source_blob", "result_fingerprint")
        if not isinstance(candidate, str) or not GIT_COMMIT.fullmatch(candidate):
            errors.append("ledger_candidate_commit_invalid")
            continue
        if _git_object_text(root, f"{candidate}^{{commit}}") != candidate:
            errors.append("ledger_candidate_commit_invalid")
        if not isinstance(tree, str) or not GIT_BLOB.fullmatch(tree):
            errors.append("ledger_candidate_tree_mismatch")
        elif _git_object_text(root, f"{candidate}^{{tree}}") != tree:
            errors.append("ledger_candidate_tree_mismatch")
        if not _safe_source_path(path) or path != LEDGER_SOURCE_PATH:
            errors.append("ledger_source_path_invalid")
        elif not isinstance(blob, str) or not GIT_BLOB.fullmatch(blob):
            errors.append("ledger_source_blob_mismatch")
        else:
            actual_blob = _git_object_text(root, f"{candidate}:{path}")
            if actual_blob != blob or blob != edge.get("result_fingerprint"):
                errors.append("ledger_source_blob_mismatch")
        producer = _field(edge, "producer_task_id", "producer_task")
        node = atlas_by_id.get(producer) if isinstance(producer, str) else None
        generation = node.get("candidate_generation") if isinstance(node, dict) else None
        if not isinstance(generation, dict) or generation.get("sha") != candidate:
            errors.append("ledger_candidate_commit_invalid")
        if not isinstance(generation, dict) or generation.get("tree") != tree:
            errors.append("ledger_candidate_tree_mismatch")
        approved_sequence = (
            ("H3-B01", LEDGER_B01_COMMIT, LEDGER_B01_TREE, LEDGER_B01_RESULT),
            ("H3-B02", LEDGER_B02_COMMIT, LEDGER_B02_TREE, LEDGER_B02_RESULT),
            ("H3-C02", LEDGER_C02_COMMIT, LEDGER_C02_TREE, LEDGER_C02_RESULT),
        )
        if strict_approved_history:
            permitted_edges = 3 if edge.get("edge_id") == "persistent_index_indexer:3" else 2
            if index >= permitted_edges or index >= len(approved_sequence):
                errors.append("ledger_edge_missing")
            else:
                expected_producer, approved_commit, approved_tree, approved_result = approved_sequence[index]
                if producer != expected_producer:
                    errors.append("ledger_candidate_commit_invalid")
                if candidate != approved_commit:
                    errors.append("ledger_candidate_commit_invalid")
                if tree != approved_tree:
                    errors.append("ledger_candidate_tree_mismatch")
                if edge.get("result_fingerprint") != approved_result or blob != approved_result:
                    errors.append("ledger_source_blob_mismatch")

        if index == 0 and producer == "H3-B01":
            b01_overlay_path = ".orchestration/remaining-work/prompts/H3-B01/overlay.json"
            b01_overlay_blob = _git_object_text(root, f"{LEDGER_GENESIS_COMMIT}:{b01_overlay_path}")
            try:
                b01_overlay = json.loads(
                    subprocess.run(
                        ["git", "-C", str(root), "show", f"{LEDGER_GENESIS_COMMIT}:{b01_overlay_path}"],
                        text=True,
                        capture_output=True,
                        check=True,
                    ).stdout
                )
            except (json.JSONDecodeError, subprocess.CalledProcessError):
                b01_overlay = None
            b01_base = b01_overlay.get("base_sha") if isinstance(b01_overlay, dict) else None
            if (
                b01_overlay_blob != LEDGER_ANCHOR_BLOBS[b01_overlay_path]
                or not isinstance(b01_base, str)
                or not GIT_COMMIT.fullmatch(b01_base)
                or _git_object_text(root, f"{b01_base}:{LEDGER_SOURCE_PATH}") != LEDGER_V1_BLOB
                or not _is_ancestor(root, b01_base, candidate)
            ):
                errors.append("ledger_candidate_ancestry_invalid")
        elif index == 0:
            if not _is_ancestor(root, baseline_commit, candidate):
                errors.append("ledger_candidate_ancestry_invalid")
        elif isinstance(previous_commit, str) and GIT_COMMIT.fullmatch(previous_commit):
            if not _is_ancestor(root, previous_commit, candidate):
                errors.append("ledger_candidate_ancestry_invalid")
        previous_commit = candidate
    return errors


def _validate_dependency_evidence(root: Path, edges: list) -> list[str]:
    errors: list[str] = []
    for index, edge in enumerate(edges):
        if index == 0 or not isinstance(edge, dict):
            continue
        previous = edges[index - 1]
        evidence = edge.get("dependency_evidence")
        if not isinstance(evidence, dict):
            errors.append("ledger_dependency_evidence_missing")
            continue
        previous_task = _field(previous, "producer_task_id", "producer_task")
        previous_commit = _field(previous, "candidate_commit_sha", "candidate_commit")
        previous_tree = _field(previous, "candidate_tree_sha", "candidate_tree")
        previous_result = previous.get("result_fingerprint")
        predecessor = edge.get("predecessor_producer")
        if predecessor is not None:
            if (
                not isinstance(predecessor, dict)
                or _field(predecessor, "task_id", "producer_task_id") != previous_task
                or _field(predecessor, "candidate_commit_sha", "candidate_commit") != previous_commit
                or _field(predecessor, "candidate_tree_sha", "candidate_tree") != previous_tree
                or predecessor.get("result_fingerprint") != previous_result
            ):
                errors.append("ledger_dependency_head_mismatch")
        dependency_task = _field(evidence, "predecessor_task_id", "dependency_task")
        dependency_head = _field(evidence, "predecessor_candidate_commit_sha", "dependency_head")
        if dependency_task != previous_task or dependency_head != previous_commit:
            errors.append("ledger_dependency_head_mismatch")

        overlay_commit = _field(evidence, "commit_sha", "commit")
        overlay_path = _field(evidence, "source_path", "path")
        overlay_blob = _field(evidence, "blob_sha", "blob")
        schema_shape = "commit_sha" in evidence
        approved_dependency = (
            overlay_commit == LEDGER_GENESIS_COMMIT
            and overlay_path == LEDGER_B02_OVERLAY_PATH
            and overlay_blob == LEDGER_B02_OVERLAY_BLOB
        ) or (
            overlay_commit == LEDGER_C02_EVIDENCE_COMMIT
            and overlay_path == LEDGER_C02_EVIDENCE_PATH
            and overlay_blob == LEDGER_C02_EVIDENCE_BLOB
        )
        if schema_shape and not approved_dependency:
            errors.append("ledger_dependency_blob_mismatch")
        if (
            not isinstance(overlay_commit, str)
            or not GIT_COMMIT.fullmatch(overlay_commit)
            or _git_object_text(root, f"{overlay_commit}^{{commit}}") != overlay_commit
            or not _safe_source_path(overlay_path)
        ):
            errors.append("ledger_dependency_evidence_missing")
            continue
        actual_overlay_blob = _git_object_text(root, f"{overlay_commit}:{overlay_path}")
        if (
            not isinstance(overlay_blob, str)
            or not GIT_BLOB.fullmatch(overlay_blob)
            or actual_overlay_blob != overlay_blob
        ):
            errors.append("ledger_dependency_blob_mismatch")
            continue
        overlay_tree = _field(evidence, "tree_sha", "tree")
        actual_overlay_tree = _git_object_text(root, f"{overlay_commit}^{{tree}}")
        if overlay_tree is not None and overlay_tree != actual_overlay_tree:
            errors.append("ledger_dependency_blob_mismatch")
        try:
            overlay = json.loads(
                subprocess.run(
                    ["git", "-C", str(root), "show", f"{overlay_commit}:{overlay_path}"],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout
            )
        except (json.JSONDecodeError, subprocess.CalledProcessError):
            errors.append("ledger_dependency_blob_mismatch")
            continue
        dependency_heads = overlay.get("dependency_heads") if isinstance(overlay, dict) else None
        if not isinstance(dependency_heads, dict) or dependency_heads.get(previous_task) != previous_commit:
            errors.append("ledger_dependency_head_mismatch")

        overlay_base = _field(overlay, "base_sha", "base_commit") if isinstance(overlay, dict) else None
        base_commit = evidence.get("base_commit", overlay_base)
        base_tree = evidence.get("base_tree")
        base_source_blob = evidence.get("base_source_blob")
        c03_edge_evidence = (
            overlay_commit == LEDGER_C02_EVIDENCE_COMMIT
            and overlay_path == LEDGER_C02_EVIDENCE_PATH
            and overlay_blob == LEDGER_C02_EVIDENCE_BLOB
            and edge.get("edge_id") == "persistent_index_indexer:3"
        )
        actual_base_tree = (
            _git_object_text(root, f"{base_commit}^{{tree}}")
            if isinstance(base_commit, str) and GIT_COMMIT.fullmatch(base_commit)
            else None
        )
        actual_base_blob = (
            _git_object_text(root, f"{base_commit}:{LEDGER_SOURCE_PATH}")
            if isinstance(base_commit, str) and GIT_COMMIT.fullmatch(base_commit)
            else None
        )
        if (
            not isinstance(base_commit, str)
            or not GIT_COMMIT.fullmatch(base_commit)
            or overlay_base != base_commit
            or (base_tree is not None and actual_base_tree != base_tree)
            or actual_base_blob != LEDGER_V1_BLOB
            or (base_source_blob is not None and base_source_blob != LEDGER_V1_BLOB)
            or (not c03_edge_evidence and not _is_ancestor(root, base_commit, _field(edge, "candidate_commit_sha", "candidate_commit")))
        ):
            errors.append("ledger_dependency_head_mismatch")
    return errors


def validate_transition_ledger_rows(ledgers: list[dict]) -> list[str]:
    """Reject duplicate persisted ledger rows claiming the same contract identity."""
    contract_ids = [ledger.get("contract_id") for ledger in ledgers if isinstance(ledger, dict)]
    return ["ledger_contract_duplicate"] if len(contract_ids) != len(set(contract_ids)) else []


def _snapshot_from_git(root: Path, commit: str) -> dict | None:
    if not GIT_COMMIT.fullmatch(commit):
        return None
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{LEDGER_SNAPSHOT_PATH}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        snapshot = json.loads(result.stdout)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return snapshot if isinstance(snapshot, dict) else None


def _history_is_append_only(root: Path, ledger: dict) -> bool:
    sequence = ledger.get("sequence")
    previous = ledger.get("previous_snapshot")
    if sequence == 1:
        return previous is None
    if not isinstance(sequence, int) or sequence < 2 or not isinstance(previous, dict):
        return False
    commit = _field(previous, "commit_sha", "commit")
    expected_digest = previous.get("digest")
    if not isinstance(commit, str) or not GIT_COMMIT.fullmatch(commit):
        return False
    snapshot = _snapshot_from_git(root, commit)
    if snapshot is None or snapshot.get("sequence") != sequence - 1:
        return False
    try:
        actual_digest = transition_ledger_digest(snapshot)
    except (AttributeError, TypeError, ValueError):
        return False
    if actual_digest != expected_digest or snapshot.get("digest") != expected_digest:
        return False
    old_edges = snapshot.get("edges")
    new_edges = ledger.get("edges")
    return (
        isinstance(old_edges, list)
        and isinstance(new_edges, list)
        and len(new_edges) >= len(old_edges)
        and new_edges[: len(old_edges)] == old_edges
        and snapshot.get("baseline") == ledger.get("baseline")
    )


def validate_transition_ledger(
    root: Path,
    ledger: dict,
    registry_by_id: dict[str, dict],
    atlas_by_id: dict[str, dict],
) -> list[str]:
    """Validate the fixed baseline, ordered continuity, one registry tip, and snapshot history."""
    errors: list[str] = []
    if isinstance(ledger, list):
        return validate_transition_ledger_rows(ledger)
    if not isinstance(ledger, dict):
        return ["ledger_baseline_invalid"]
    ledger_version = ledger.get("schema_version")
    if ledger_version == "remaining-work-contract-transition-ledger.v2":
        if ledger.get("sequence") != 2 or len(ledger.get("edges", [])) != 3:
            return ["ledger_edge_missing"]
        previous = ledger.get("previous_snapshot")
        if previous != {
            "commit_sha": "2cd6095587a957575f02c2b996e881ee26c6285a",
            "digest": "2e79189cf7f27b494d1912b90eec595fdadb90d84af0605dcd8ba3f78a07311f",
        }:
            return ["ledger_history_rewrite"]
    elif ledger_version not in (None, "remaining-work-contract-transition-ledger.v1"):
        return ["ledger_baseline_invalid"]
    try:
        if ledger.get("digest") != transition_ledger_digest(ledger):
            errors.append("ledger_digest_mismatch")
    except (AttributeError, TypeError, ValueError):
        errors.append("ledger_digest_mismatch")

    baseline = ledger.get("baseline")
    anchor = ledger.get("genesis_anchor")
    if not isinstance(baseline, dict) or not isinstance(anchor, dict):
        errors.append("ledger_baseline_invalid")
        return errors
    if (
        ledger.get("contract_id") != LEDGER_CONTRACT_ID
        or _field(anchor, "commit_sha", "commit") != LEDGER_GENESIS_COMMIT
        or _field(anchor, "tree_sha", "tree") != LEDGER_GENESIS_TREE
        or baseline.get("contract_id", LEDGER_CONTRACT_ID) != LEDGER_CONTRACT_ID
        or baseline.get("kind") != "GIT_BLOB"
        or baseline.get("fingerprint") != LEDGER_V1_BLOB
        or _field(baseline, "source_path", "source") != LEDGER_SOURCE_PATH
        or _field(baseline, "commit_sha", "commit") != LEDGER_GENESIS_COMMIT
        or _field(baseline, "tree_sha", "tree") != LEDGER_GENESIS_TREE
        or _field(baseline, "blob_sha", "blob") != LEDGER_V1_BLOB
    ):
        errors.append("ledger_baseline_invalid")

    edges = ledger.get("edges")
    if not isinstance(edges, list) or not edges:
        errors.append("ledger_edge_missing")
        edges = []
    if ledger_version == "remaining-work-contract-transition-ledger.v1" and len(edges) > 2:
        errors.append("ledger_edge_missing")
    if ledger_version == "remaining-work-contract-transition-ledger.v2" and len(edges) != 3:
        errors.append("ledger_edge_missing")
    edge_ids = [edge.get("edge_id") for edge in edges if isinstance(edge, dict)]
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("ledger_edge_duplicate")
    producer_ids = [
        (_field(edge, "producer_task_id", "producer_task"), _field(edge, "candidate_commit_sha", "candidate_commit"))
        for edge in edges
        if isinstance(edge, dict)
    ]
    producer_tasks = [task_id for task_id, _ in producer_ids if task_id is not None]
    candidate_ids = [candidate for _, candidate in producer_ids if candidate is not None]
    if len(producer_tasks) != len(set(producer_tasks)) or len(candidate_ids) != len(set(candidate_ids)):
        errors.append("ledger_producer_duplicate")
    successors: dict[Any, set[tuple[Any, Any]]] = {}
    for edge in edges:
        if isinstance(edge, dict):
            predecessor = edge.get("predecessor_fingerprint")
            successor = (
                edge.get("result_fingerprint"),
                _field(edge, "candidate_commit_sha", "candidate_commit"),
            )
            if isinstance(predecessor, str) and all(
                value is None or isinstance(value, str) for value in successor
            ):
                successors.setdefault(predecessor, set()).add(successor)
    if any(len(candidates) > 1 for candidates in successors.values()):
        errors.append("ledger_competing_successor")
    ordinals = [edge.get("ordinal") if isinstance(edge, dict) else None for edge in edges]
    if ordinals != list(range(1, len(edges) + 1)):
        errors.append("ledger_ordinal_invalid")
        if not ordinals or ordinals[0] != 1 or any(
            not isinstance(ordinal, int) or ordinal != index
            for index, ordinal in enumerate(ordinals, start=1)
        ):
            errors.append("ledger_edge_missing")

    strict_approved_history = (
        isinstance(baseline, dict)
        and "commit_sha" in baseline
        and isinstance(edges, list)
        and bool(edges)
        and isinstance(edges[0], dict)
        and "candidate_commit_sha" in edges[0]
    )
    errors.extend(
        _validate_immutable_git_evidence(
            root,
            baseline,
            edges,
            atlas_by_id,
            strict_approved_history=strict_approved_history,
        )
    )
    errors.extend(_validate_dependency_evidence(root, edges))

    prior_result = baseline.get("fingerprint")
    for edge in edges:
        if not isinstance(edge, dict):
            errors.append("ledger_predecessor_mismatch")
            continue
        predecessor = edge.get("predecessor_fingerprint")
        if predecessor != prior_result:
            errors.append("ledger_predecessor_mismatch")
        if edge.get("contract_id", LEDGER_CONTRACT_ID) != LEDGER_CONTRACT_ID:
            errors.append("ledger_baseline_invalid")
        prior_result = edge.get("result_fingerprint")

    if edges and isinstance(edges[-1], dict):
        registry = registry_by_id.get(LEDGER_CONTRACT_ID)
        tip = edges[-1].get("result_fingerprint")
        if not isinstance(registry, dict) or registry.get("fingerprint") != tip:
            errors.append("ledger_predecessor_mismatch")
        else:
            source = registry.get("source")
            edge = edges[-1]
            candidate = _field(edge, "candidate_commit_sha", "candidate_commit")
            if source != f"{LEDGER_SOURCE_PATH}@{candidate}":
                errors.append("ledger_predecessor_mismatch")
            producer = _field(edge, "producer_task_id", "producer_task")
            node = atlas_by_id.get(producer) if isinstance(producer, str) else None
            candidate_generation = node.get("candidate_generation") if isinstance(node, dict) else None
            if not isinstance(candidate_generation, dict) or candidate_generation.get("sha") != candidate:
                errors.append("ledger_predecessor_mismatch")

    if ledger.get("sequence") == 1:
        if ledger.get("previous_snapshot") is not None:
            errors.append("ledger_history_rewrite")
    elif not _history_is_append_only(root, ledger):
        errors.append("ledger_history_rewrite")

    return list(dict.fromkeys(errors))


def _candidate_blob(root: Path, candidate_sha: str, entry: dict) -> str | None:
    """Resolve a contract's exact source blob only when provenance pins this candidate."""
    source = entry.get("source")
    if not isinstance(source, str) or "@" not in source:
        return None
    path, revision = source.rsplit("@", 1)
    if revision != candidate_sha or not path or path.startswith("/") or ".." in Path(path).parts:
        return None
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", f"{candidate_sha}:{path}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    blob = result.stdout.strip()
    return blob if GIT_BLOB.fullmatch(blob) else None


def authorized_self_transition(
    root: Path,
    node: dict,
    contract: dict,
    current_fingerprint: str | None,
    registry_by_id: dict,
) -> bool:
    """Allow a producer's historical input only for its exact registered output blob."""
    contract_id = contract.get("id")
    old_fingerprint = contract.get("fingerprint")
    if node.get("state") not in {"BUILD_GREEN", "VERIFY_READY", "VERIFYING", "VERIFIED"}:
        return False
    candidate = node.get("candidate_generation")
    if not isinstance(candidate, dict):
        return False
    candidate_sha = candidate.get("sha")
    if not isinstance(candidate_sha, str) or not GIT_BLOB.fullmatch(candidate_sha):
        return False

    consumed = {
        item.get("id"): item.get("fingerprint")
        for item in node.get("consumed_contracts", [])
        if isinstance(item, dict)
    }
    historical = candidate.get("contract_fingerprints")
    if not isinstance(historical, dict) or historical != consumed:
        return False
    if historical.get(contract_id) != old_fingerprint:
        return False

    produced = {
        item.get("id"): item.get("fingerprint")
        for item in node.get("produced_contracts", [])
        if isinstance(item, dict)
    }
    new_fingerprint = produced.get(contract_id)
    if not isinstance(new_fingerprint, str) or new_fingerprint != current_fingerprint:
        return False

    registry_entry = registry_by_id.get(contract_id)
    if not isinstance(registry_entry, dict):
        return False
    if registry_entry.get("kind") != "GIT_BLOB" or registry_entry.get("fingerprint") != new_fingerprint:
        return False
    candidate_blob = _candidate_blob(root, candidate_sha, registry_entry)
    return candidate_blob is not None and candidate_blob == new_fingerprint


def ledger_authorizes_historical_input(
    root: Path,
    node: dict,
    contract: dict,
    current_fingerprint: str | None,
    registry_by_id: dict[str, dict],
    ledger: dict,
) -> bool:
    """Bind one ordered-ledger producer's historical input to its exact edge and current tip.

    valid full-ledger result is a caller precondition; this helper binds one exact
    historical producer to one exact authenticated edge and current tip.
    """
    if not all(isinstance(value, dict) for value in (node, contract, registry_by_id, ledger)):
        return False
    contract_id = contract.get("id")
    node_id = node.get("id")
    state = node.get("state")
    if (
        contract_id != LEDGER_CONTRACT_ID
        or ledger.get("contract_id") != contract_id
        or not isinstance(node_id, str)
        or not isinstance(state, str)
        or state not in {"BUILD_GREEN", "VERIFY_READY", "VERIFYING", "VERIFIED"}
    ):
        return False

    candidate = node.get("candidate_generation")
    if not isinstance(candidate, dict):
        return False
    candidate_sha = candidate.get("sha")
    candidate_tree = candidate.get("tree")
    if (
        not isinstance(candidate_sha, str)
        or not GIT_COMMIT.fullmatch(candidate_sha)
        or not isinstance(candidate_tree, str)
        or not GIT_BLOB.fullmatch(candidate_tree)
        or _git_object_text(root, f"{candidate_sha}^{{commit}}") != candidate_sha
        or _git_object_text(root, f"{candidate_sha}^{{tree}}") != candidate_tree
    ):
        return False

    consumed_items = node.get("consumed_contracts")
    if not isinstance(consumed_items, list):
        return False
    consumed: dict[str, str] = {}
    for item in consumed_items:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or not isinstance(item.get("fingerprint"), str)
            or item["id"] in consumed
        ):
            return False
        consumed[item["id"]] = item["fingerprint"]
    historical = candidate.get("contract_fingerprints")
    if not isinstance(historical, dict) or historical != consumed:
        return False
    historical_fingerprint = historical.get(contract_id)
    if (
        not isinstance(historical_fingerprint, str)
        or not GIT_BLOB.fullmatch(historical_fingerprint)
        or contract.get("fingerprint") != historical_fingerprint
    ):
        return False

    edges = ledger.get("edges")
    if not isinstance(edges, list) or not edges or any(not isinstance(edge, dict) for edge in edges):
        return False
    producer_edges = [
        edge for edge in edges if _field(edge, "producer_task_id", "producer_task") == node_id
    ]
    candidate_edges = [
        edge
        for edge in edges
        if _field(edge, "candidate_commit_sha", "candidate_commit") == candidate_sha
    ]
    matches = [
        edge
        for edge in producer_edges
        if _field(edge, "candidate_commit_sha", "candidate_commit") == candidate_sha
        and _field(edge, "candidate_tree_sha", "candidate_tree") == candidate_tree
    ]
    if len(matches) != 1 or len(producer_edges) != 1 or len(candidate_edges) != 1:
        return False
    edge = matches[0]
    if edge.get("contract_id", contract_id) != contract_id:
        return False

    result_fingerprint = edge.get("result_fingerprint")
    source_path = _field(edge, "source_path", "source")
    source_blob = _field(edge, "source_blob_sha", "source_blob")
    if (
        not isinstance(result_fingerprint, str)
        or not GIT_BLOB.fullmatch(result_fingerprint)
        or source_path != LEDGER_SOURCE_PATH
        or not _safe_source_path(source_path)
        or source_blob != result_fingerprint
        or _git_object_text(root, f"{candidate_sha}:{source_path}") != result_fingerprint
    ):
        return False

    tip = edges[-1]
    tip_fingerprint = tip.get("result_fingerprint")
    if (
        not isinstance(current_fingerprint, str)
        or current_fingerprint != tip_fingerprint
        or not isinstance(tip_fingerprint, str)
        or not GIT_BLOB.fullmatch(tip_fingerprint)
    ):
        return False
    registry_entry = registry_by_id.get(contract_id)
    tip_candidate = _field(tip, "candidate_commit_sha", "candidate_commit")
    tip_tree = _field(tip, "candidate_tree_sha", "candidate_tree")
    tip_path = _field(tip, "source_path", "source")
    if (
        not isinstance(registry_entry, dict)
        or registry_entry.get("kind") != "GIT_BLOB"
        or registry_entry.get("fingerprint") != tip_fingerprint
        or not isinstance(tip_candidate, str)
        or not GIT_COMMIT.fullmatch(tip_candidate)
        or _git_object_text(root, f"{tip_candidate}^{{commit}}") != tip_candidate
        or not isinstance(tip_tree, str)
        or not GIT_BLOB.fullmatch(tip_tree)
        or _git_object_text(root, f"{tip_candidate}^{{tree}}") != tip_tree
        or tip_path != LEDGER_SOURCE_PATH
        or not _safe_source_path(tip_path)
        or _git_object_text(root, f"{tip_candidate}:{tip_path}") != tip_fingerprint
        or registry_entry.get("source") != f"{tip_path}@{tip_candidate}"
    ):
        return False
    return True


def ledger_authorizes_historical_output(
    root: Path,
    node: dict,
    contract: dict,
    ledger: dict,
    *,
    allow_tip: bool = False,
) -> bool:
    """Validate that a historical producer's output matches its authenticated ledger edge.

    When allow_tip is False, this only authorizes historical non-tip edges.
    When allow_tip is True, it authorizes any valid edge in the ledger.
    """
    if not all(isinstance(value, dict) for value in (node, contract, ledger)):
        return False
    contract_id = contract.get("id")
    node_id = node.get("id")
    state = node.get("state")
    if (
        contract_id != LEDGER_CONTRACT_ID
        or ledger.get("contract_id") != contract_id
        or not isinstance(node_id, str)
        or not isinstance(state, str)
        or state not in {"BUILD_GREEN", "VERIFY_READY", "VERIFYING", "VERIFIED"}
    ):
        return False

    candidate = node.get("candidate_generation")
    if not isinstance(candidate, dict):
        return False
    candidate_sha = candidate.get("sha")
    candidate_tree = candidate.get("tree")
    if (
        not isinstance(candidate_sha, str)
        or not GIT_COMMIT.fullmatch(candidate_sha)
        or not isinstance(candidate_tree, str)
        or not GIT_BLOB.fullmatch(candidate_tree)
        or _git_object_text(root, f"{candidate_sha}^{{commit}}") != candidate_sha
        or _git_object_text(root, f"{candidate_sha}^{{tree}}") != candidate_tree
    ):
        return False

    edges = ledger.get("edges")
    if not isinstance(edges, list) or not edges or any(not isinstance(edge, dict) for edge in edges):
        return False

    producer_edges = [
        edge for edge in edges if _field(edge, "producer_task_id", "producer_task") == node_id
    ]
    candidate_edges = [
        edge
        for edge in edges
        if _field(edge, "candidate_commit_sha", "candidate_commit") == candidate_sha
    ]
    matches = [
        edge
        for edge in producer_edges
        if _field(edge, "candidate_commit_sha", "candidate_commit") == candidate_sha
        and _field(edge, "candidate_tree_sha", "candidate_tree") == candidate_tree
    ]
    if len(matches) != 1 or len(producer_edges) != 1 or len(candidate_edges) != 1:
        return False
    edge = matches[0]
    if edge.get("contract_id", contract_id) != contract_id:
        return False

    if not allow_tip and edge is edges[-1]:
        return False

    result_fingerprint = edge.get("result_fingerprint")
    source_path = _field(edge, "source_path", "source")
    source_blob = _field(edge, "source_blob_sha", "source_blob")
    if (
        not isinstance(result_fingerprint, str)
        or not GIT_BLOB.fullmatch(result_fingerprint)
        or contract.get("fingerprint") != result_fingerprint
        or source_path != LEDGER_SOURCE_PATH
        or not _safe_source_path(source_path)
        or source_blob != result_fingerprint
        or _git_object_text(root, f"{candidate_sha}:{source_path}") != result_fingerprint
    ):
        return False

    return True


def produced_blob_mismatches(
    root: Path,
    node: dict,
    registry_by_id: dict,
    transition_ledger: dict | None = None,
) -> list[str]:
    """Return output IDs whose candidate-pinned GIT_BLOB provenance disagrees with their claim."""
    candidate = node.get("candidate_generation")
    if not isinstance(candidate, dict) or not isinstance(candidate.get("sha"), str):
        return []
    if transition_ledger is None:
        ledger_path = root / ".orchestration/remaining-work/atlas/contract-transition-ledger.json"
        if ledger_path.exists():
            try:
                transition_ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            except Exception:
                transition_ledger = None
    mismatches = []
    for item in node.get("produced_contracts", []):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        registry_entry = registry_by_id.get(item["id"])
        if not isinstance(registry_entry, dict) or registry_entry.get("kind") != "GIT_BLOB":
            continue
        source = registry_entry.get("source")
        source_revision = source.rsplit("@", 1)[-1] if isinstance(source, str) and "@" in source else None
        if source_revision != candidate["sha"]:
            if (
                isinstance(transition_ledger, dict)
                and transition_ledger.get("contract_id") == item["id"]
                and ledger_authorizes_historical_output(
                    root, node, item, transition_ledger, allow_tip=True
                )
            ):
                continue
            mismatches.append(item["id"])
            continue
        candidate_blob = _candidate_blob(root, candidate["sha"], registry_entry)
        if candidate_blob is None or candidate_blob != item.get("fingerprint"):
            mismatches.append(item["id"])
    return mismatches
