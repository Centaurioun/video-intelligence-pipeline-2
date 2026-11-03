from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


CONTRACT_ID = "persistent_index_indexer"
SOURCE_PATH = "experiments/persistent_local_index/indexer.py"
OVERLAY_PATH = ".orchestration/remaining-work/prompts/H3-B02/overlay.json"
SOURCE_V2 = b"# synthetic persistent indexer V2\n"
SOURCE_V3 = b"# synthetic persistent indexer V3\n"
SOURCE_V3_ALTERNATE = b"# synthetic competing persistent indexer V3\n"
GENESIS_COMMIT = "0f5b2c22965870578a4f57bd5fdcf84569c07a89"
GENESIS_TREE = "6f90ab49e1ecea10b2f416e047891f594e17f447"
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
VARIANTS = {
    "wrong_source_path",
    "wrong_declared_tree",
    "wrong_dependency_head",
    "unrelated_successor",
    "two_successors",
}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write(root: Path, relative_path: str, content: bytes) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "--all")
    _git(root, "commit", "--quiet", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _tree(root: Path, commit: str) -> str:
    return _git(root, "rev-parse", f"{commit}^{{tree}}")


def _blob(root: Path, commit: str, source_path: str = SOURCE_PATH) -> str:
    return _git(root, "rev-parse", f"{commit}:{source_path}")


def _edge(
    *,
    edge_id: str,
    ordinal: int,
    predecessor_fingerprint: str,
    result_fingerprint: str,
    producer_task: str,
    candidate_commit: str,
    candidate_tree: str,
    source_path: str,
    dependency_evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "edge_id": edge_id,
        "contract_id": CONTRACT_ID,
        "ordinal": ordinal,
        "predecessor_fingerprint": predecessor_fingerprint,
        "result_fingerprint": result_fingerprint,
        "producer_task": producer_task,
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "source_path": source_path,
        "source_blob": result_fingerprint,
        "dependency_evidence": dependency_evidence,
        "verification_ref": f".orchestration/remaining-work/reconciliation/batch-{ordinal:03d}-reconciliation.json#{producer_task}",
    }


def _finish_ledger(payload: dict[str, Any]) -> dict[str, Any]:
    payload["digest"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    return payload


def _candidate_node(task_id: str, commit: str, tree: str, consumed_fingerprint: str) -> dict[str, Any]:
    return {
        "id": task_id,
        "state": "VERIFIED",
        "candidate_generation": {
            "sha": commit,
            "tree": tree,
            "contract_fingerprints": {CONTRACT_ID: consumed_fingerprint},
        },
        "consumed_contracts": [{"id": CONTRACT_ID, "fingerprint": consumed_fingerprint}],
        "produced_contracts": [],
        "overlay_ref": f".orchestration/remaining-work/prompts/{task_id}/overlay.json",
        "verification_ref": f".orchestration/remaining-work/reconciliation/{task_id.lower()}-reconciliation.json#{task_id}",
    }


def make_linear_contract_history(root: Path, variant: str | None = None) -> dict[str, Any]:
    """Create a real temporary-Git V1 -> V2 -> V3 history and optional adversary.

    ``root`` is created if absent and must not already contain a Git repository.
    All commit, tree, and blob identities in the returned evidence are produced
    by Git in this repository; no object IDs are synthesized or mocked.
    """
    if variant is not None and variant not in VARIANTS:
        raise ValueError(f"unknown contract transition fixture variant: {variant}")
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError(f"fixture root must be empty: {root}")

    _git(root, "init", "--quiet", "--initial-branch=main")
    _git(root, "config", "user.name", "Contract Transition Fixture")
    _git(root, "config", "user.email", "contract-transition-fixture@example.invalid")
    # Import only the approved genesis object from this local checkout. This is
    # a local object transfer; no remote or network is involved.
    _git(root, "fetch", "--quiet", "--no-tags", str(REPOSITORY_ROOT), GENESIS_COMMIT)
    baseline_commit = GENESIS_COMMIT
    _git(root, "checkout", "--quiet", "--detach", baseline_commit)
    baseline_tree = _tree(root, baseline_commit)
    v1_blob = _blob(root, baseline_commit)
    if baseline_tree != GENESIS_TREE:
        raise RuntimeError("approved genesis commit resolved to an unexpected tree")

    _write(root, SOURCE_PATH, SOURCE_V2)
    b01_commit = _commit(root, "H3-B01: V2")
    b01_tree = _tree(root, b01_commit)
    v2_blob = _blob(root, b01_commit)

    dependency_head = baseline_commit if variant == "wrong_dependency_head" else b01_commit
    overlay = {
        "schema_version": "remaining-work-launch-overlay.v1",
        "task_id": "H3-B02",
        "version": "h3-b02-overlay-v1.0.0",
        "base_sha": baseline_commit,
        "dependency_heads": {"H3-B01": dependency_head},
    }
    _write(root, OVERLAY_PATH, (json.dumps(overlay, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    overlay_commit = _commit(root, "H3-B02 launch overlay pins H3-B01")
    overlay_tree = _tree(root, overlay_commit)
    overlay_blob = _blob(root, overlay_commit, OVERLAY_PATH)

    dependency_evidence = {
        "producer_task": "H3-B02",
        "dependency_task": "H3-B01",
        "dependency_head": dependency_head,
        "commit": overlay_commit,
        "tree": overlay_tree,
        "path": OVERLAY_PATH,
        "blob": overlay_blob,
        "base_commit": baseline_commit,
        "base_tree": baseline_tree,
        "base_source_blob": v1_blob,
    }

    # The ordinary successor is a descendant of B01 and its immutable overlay.
    _write(root, SOURCE_PATH, SOURCE_V3)
    if variant == "wrong_source_path":
        _write(root, "experiments/persistent_local_index/indexer_variant.py", SOURCE_V3)
        declared_source_path = "experiments/persistent_local_index/indexer_variant.py"
    else:
        declared_source_path = SOURCE_PATH
    b02_commit = _commit(root, "H3-B02: V3")
    b02_tree = _tree(root, b02_commit)
    v3_blob = _blob(root, b02_commit)

    if variant == "unrelated_successor":
        _git(root, "checkout", "--quiet", "--detach", baseline_commit)
        _write(root, SOURCE_PATH, SOURCE_V3)
        b02_commit = _commit(root, "H3-B02: unrelated V3 successor")
        b02_tree = _tree(root, b02_commit)
        v3_blob = _blob(root, b02_commit)

    declared_b02_tree = b01_tree if variant == "wrong_declared_tree" else b02_tree
    edges = [
        _edge(
            edge_id="H3-B01-V1-to-V2",
            ordinal=1,
            predecessor_fingerprint=v1_blob,
            result_fingerprint=v2_blob,
            producer_task="H3-B01",
            candidate_commit=b01_commit,
            candidate_tree=b01_tree,
            source_path=SOURCE_PATH,
            dependency_evidence=None,
        ),
        _edge(
            edge_id="H3-B02-V2-to-V3",
            ordinal=2,
            predecessor_fingerprint=v2_blob,
            result_fingerprint=v3_blob,
            producer_task="H3-B02",
            candidate_commit=b02_commit,
            candidate_tree=declared_b02_tree,
            source_path=declared_source_path,
            dependency_evidence=dependency_evidence,
        ),
    ]

    fixture: dict[str, Any] = {
        "root": root,
        "baseline_commit": baseline_commit,
        "baseline_tree": baseline_tree,
        "v1_blob": v1_blob,
        "b01_commit": b01_commit,
        "b01_tree": b01_tree,
        "v2_blob": v2_blob,
        "b02_commit": b02_commit,
        "b02_tree": b02_tree,
        "v3_blob": v3_blob,
        "overlay_commit": overlay_commit,
        "overlay_tree": overlay_tree,
        "overlay_blob": overlay_blob,
        "ledger": {},
        "registry_by_id": {},
        "atlas_by_id": {},
        "variant": variant,
    }

    if variant == "two_successors":
        _git(root, "checkout", "--quiet", "--detach", overlay_commit)
        _write(root, SOURCE_PATH, SOURCE_V3_ALTERNATE)
        alternate_commit = _commit(root, "competing H3-B02: alternate V3")
        alternate_tree = _tree(root, alternate_commit)
        alternate_blob = _blob(root, alternate_commit)
        fixture.update(
            alternate_successor_commit=alternate_commit,
            alternate_successor_tree=alternate_tree,
            alternate_successor_blob=alternate_blob,
        )
        edges.append(
            _edge(
                edge_id="H3-B02-ALTERNATE-V2-to-V3",
                ordinal=3,
                predecessor_fingerprint=v2_blob,
                result_fingerprint=alternate_blob,
                producer_task="H3-B02-ALTERNATE",
                candidate_commit=alternate_commit,
                candidate_tree=alternate_tree,
                source_path=SOURCE_PATH,
                dependency_evidence=dependency_evidence,
            )
        )

    ledger_payload = {
        "schema_version": "remaining-work-contract-transition-ledger.v1",
        "contract_id": CONTRACT_ID,
        "sequence": 1,
        "genesis_anchor": {"commit": GENESIS_COMMIT, "tree": GENESIS_TREE},
        "previous_snapshot": None,
        "baseline": {
            "contract_id": CONTRACT_ID,
            "fingerprint": v1_blob,
            "kind": "GIT_BLOB",
            "source_path": SOURCE_PATH,
            "commit": baseline_commit,
            "tree": baseline_tree,
            "blob": v1_blob,
        },
        "edges": edges,
    }
    fixture["ledger"] = _finish_ledger(ledger_payload)
    fixture["registry_by_id"] = {
        CONTRACT_ID: {
            "id": CONTRACT_ID,
            "kind": "GIT_BLOB",
            "fingerprint": v3_blob,
            "source": f"{SOURCE_PATH}@{b02_commit}",
        }
    }
    fixture["atlas_by_id"] = {
        "H3-B01": _candidate_node("H3-B01", b01_commit, b01_tree, v1_blob),
        "H3-B02": _candidate_node("H3-B02", b02_commit, b02_tree, v1_blob),
    }
    if variant == "two_successors":
        fixture["atlas_by_id"]["H3-B02-ALTERNATE"] = _candidate_node(
            "H3-B02-ALTERNATE",
            fixture["alternate_successor_commit"],
            fixture["alternate_successor_tree"],
            v1_blob,
        )
    return fixture
