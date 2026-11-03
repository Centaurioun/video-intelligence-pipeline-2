from __future__ import annotations

import math
import copy
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

import remaining_work_contracts as contracts

sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
from contract_transition_ledger import make_linear_contract_history


def test_canonical_ledger_bytes_ignore_mapping_insertion_order() -> None:
    assert contracts.canonical_transition_ledger_bytes({"b": 1, "a": "ü"}) == (
        b'{"a":"\xc3\xbc","b":1}'
    )
    assert contracts.canonical_transition_ledger_bytes({"a": "ü", "b": 1}) == (
        b'{"a":"\xc3\xbc","b":1}'
    )


def test_canonical_ledger_bytes_preserve_edge_ordinal_order() -> None:
    ledger = {"edges": [{"ordinal": 1}, {"ordinal": 2}]}
    reversed_ledger = {"edges": list(reversed(ledger["edges"]))}

    assert contracts.canonical_transition_ledger_bytes(ledger) != (
        contracts.canonical_transition_ledger_bytes(reversed_ledger)
    )


def test_ledger_digest_excludes_only_digest_field() -> None:
    ledger = {"schema_version": "v1", "edges": [{"ordinal": 1}]}
    digest = contracts.transition_ledger_digest(ledger)

    assert contracts.transition_ledger_digest({**ledger, "digest": digest}) == digest
    assert contracts.transition_ledger_digest({**ledger, "extra": True}) != digest


def test_ledger_digest_rejects_nonfinite_json_values() -> None:
    for nonfinite in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
                contracts.transition_ledger_digest({"value": nonfinite})


def test_validator_rejects_stale_current_ledger_digest(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "stale-current-digest")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"][0]["verification_ref"] = "immutable:changed-without-redigest"

    assert "ledger_digest_mismatch" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_canonical_ledger_golden_digest_is_pinned() -> None:
    payload = {"b": 1, "a": "ü"}
    assert contracts.canonical_transition_ledger_bytes(payload) == b'{"a":"\xc3\xbc","b":1}'
    assert contracts.transition_ledger_digest(payload) == (
        "4e7ff4080b1a00acdaf71eb0cdf2d504aa8068bbb375c002eac2df3f064047a7"
    )


def test_valid_v1_v2_v3_history_has_one_ordered_tip(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "linear")

    assert contracts.validate_transition_ledger(
        fixture["root"],
        fixture["ledger"],
        fixture["registry_by_id"],
        fixture["atlas_by_id"],
    ) == []


def test_exact_c03_v2_edge_three_validates_and_wrong_evidence_fails():
    root = Path(__file__).resolve().parents[2]
    historical = json.loads(subprocess.run(
        ["git", "-C", str(root), "show", "2cd6095587a957575f02c2b996e881ee26c6285a:.orchestration/remaining-work/atlas/contract-transition-ledger.json"],
        check=True, capture_output=True, text=True,
    ).stdout)
    assert historical["schema_version"] == "remaining-work-contract-transition-ledger.v1"
    assert historical["sequence"] == 1
    assert len(historical["edges"]) == 2
    assert [(edge["ordinal"], edge["producer_task_id"]) for edge in historical["edges"]] == [
        (1, "H3-B01"), (2, "H3-B02")
    ]
    assert historical["digest"] == "2e79189cf7f27b494d1912b90eec595fdadb90d84af0605dcd8ba3f78a07311f"
    current = json.loads((root / ".orchestration/remaining-work/atlas/contract-transition-ledger.json").read_text())
    assert current["edges"][:2] == historical["edges"]
    assert current["edges"][1]["ordinal"] == 2
    assert current["edges"][2]["ordinal"] == 3
    assert current["edges"][2]["producer_task_id"] == "H3-C02"
    assert current["edges"][2]["result_fingerprint"] == "875122c70f9b35bd6fae2a68d734f602bb7aeb84"
    assert current["edges"][2]["source_blob_sha"] == "875122c70f9b35bd6fae2a68d734f602bb7aeb84"
    assert current["edges"][-1] == current["edges"][2]

    ledger = copy.deepcopy(historical)
    ledger.update({"schema_version": "remaining-work-contract-transition-ledger.v2", "sequence": 2,
                   "previous_snapshot": {"commit_sha": "2cd6095587a957575f02c2b996e881ee26c6285a",
                                         "digest": "2e79189cf7f27b494d1912b90eec595fdadb90d84af0605dcd8ba3f78a07311f"}})
    ledger["edges"].append({
        "edge_id": "persistent_index_indexer:3", "contract_id": "persistent_index_indexer", "ordinal": 3,
        "predecessor_fingerprint": "8400a3fb52945a539995b041f72f1c1370f64d40",
        "result_fingerprint": "875122c70f9b35bd6fae2a68d734f602bb7aeb84", "producer_task_id": "H3-C02",
        "candidate_commit_sha": "44a7d4d931d5219efc781f8da54fab850ba8bcc1",
        "candidate_tree_sha": "5206b1f5c326596a02ec2295202db374f8d42ce5",
        "source_path": "experiments/persistent_local_index/indexer.py", "source_blob_sha": "875122c70f9b35bd6fae2a68d734f602bb7aeb84",
        "predecessor_producer": {"task_id": "H3-B02", "candidate_commit_sha": "f7f415648e4e7521502efe8da7fd0f352d8fc7bc",
                                  "candidate_tree_sha": "bf65b439798ab9484b77135406fdbf36256f98aa", "result_fingerprint": "8400a3fb52945a539995b041f72f1c1370f64d40"},
        "dependency_evidence": {"commit_sha": "2cd6095587a957575f02c2b996e881ee26c6285a",
                                "source_path": ".orchestration/remaining-work/prompts/H3-C02/overlay-verify-batch008.json",
                                "blob_sha": "8fbeb4301b9245968108975cc27a7fbb27d863e2",
                                "predecessor_task_id": "H3-B02", "predecessor_candidate_commit_sha": "f7f415648e4e7521502efe8da7fd0f352d8fc7bc"},
        "verification_ref": {"commit_sha": "44a7d4d931d5219efc781f8da54fab850ba8bcc1",
                              "source_path": "experiments/persistent_local_index/indexer.py", "blob_sha": "875122c70f9b35bd6fae2a68d734f602bb7aeb84"},
    })
    ledger["digest"] = contracts.transition_ledger_digest(ledger)
    atlas_file = json.loads((root / ".orchestration/remaining-work/atlas/atlas.json").read_text())
    atlas = {node["id"]: node for node in atlas_file["nodes"]}
    registry_file = json.loads((root / ".orchestration/remaining-work/atlas/contract-registry.json").read_text())
    registry = {item["id"]: item for item in registry_file["entries"]}
    registry["persistent_index_indexer"] = {"kind": "GIT_BLOB", "fingerprint": "875122c70f9b35bd6fae2a68d734f602bb7aeb84",
        "source": "experiments/persistent_local_index/indexer.py@44a7d4d931d5219efc781f8da54fab850ba8bcc1"}
    assert contracts.validate_transition_ledger(root, ledger, registry, atlas) == []
    bad = copy.deepcopy(ledger)
    bad["edges"][2]["dependency_evidence"]["blob_sha"] = "0" * 40
    bad["digest"] = contracts.transition_ledger_digest(bad)
    assert "ledger_dependency_blob_mismatch" in contracts.validate_transition_ledger(root, bad, registry, atlas)
    bad_tip = copy.deepcopy(ledger)
    bad_registry = copy.deepcopy(registry)
    bad_registry["persistent_index_indexer"]["fingerprint"] = "8400a3fb52945a539995b041f72f1c1370f64d40"
    assert "ledger_predecessor_mismatch" in contracts.validate_transition_ledger(root, bad_tip, bad_registry, atlas)
    bad_candidate = copy.deepcopy(ledger)
    bad_candidate["edges"][2]["candidate_commit_sha"] = "2" * 40
    bad_candidate["digest"] = contracts.transition_ledger_digest(bad_candidate)
    assert "ledger_candidate_commit_invalid" in contracts.validate_transition_ledger(root, bad_candidate, registry, atlas)


def test_sequence_one_valid_single_edge_history_remains_valid(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "sequence-one-single-edge")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"] = ledger["edges"][:1]
    ledger["digest"] = contracts.transition_ledger_digest(ledger)
    registry = {
        "persistent_index_indexer": {
            "kind": "GIT_BLOB",
            "fingerprint": fixture["v2_blob"],
            "source": f'experiments/persistent_local_index/indexer.py@{fixture["b01_commit"]}',
        }
    }
    atlas = {"H3-B01": fixture["atlas_by_id"]["H3-B01"]}

    assert contracts.validate_transition_ledger(fixture["root"], ledger, registry, atlas) == []


def test_sequence_one_approved_two_edge_history_is_valid_without_prior_snapshot(
    tmp_path: Path,
) -> None:
    root, ledger, registry, atlas = schema_shaped_repository_history(tmp_path)
    ledger["sequence"] = 1
    ledger["previous_snapshot"] = None
    ledger["digest"] = contracts.transition_ledger_digest(ledger)

    assert contracts.validate_transition_ledger(root, ledger, registry, atlas) == []


def test_sequence_one_requires_null_previous_snapshot(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "sequence-one-prior-snapshot")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["previous_snapshot"] = {
        "commit_sha": fixture["baseline_commit"],
        "digest": ledger["digest"],
    }
    ledger["digest"] = contracts.transition_ledger_digest(ledger)

    assert "ledger_history_rewrite" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_sequence_one_missing_first_of_two_edges_is_refused(tmp_path: Path) -> None:
    root, ledger, registry, atlas = schema_shaped_repository_history(tmp_path)
    ledger["sequence"] = 1
    ledger["previous_snapshot"] = None
    ledger["edges"] = ledger["edges"][1:]
    ledger["digest"] = contracts.transition_ledger_digest(ledger)

    errors = contracts.validate_transition_ledger(root, ledger, registry, atlas)
    assert "ledger_edge_missing" in errors
    assert "ledger_ordinal_invalid" in errors


def test_ledger_baseline_must_match_fixed_genesis(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "bad-baseline")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["baseline"]["fingerprint"] = "0" * 40

    assert "ledger_baseline_invalid" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_missing_v1_to_v2_edge_refuses_v3_edge(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "missing-edge")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"] = ledger["edges"][1:]

    assert "ledger_edge_missing" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_edge_predecessor_must_equal_previous_result(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "bad-predecessor")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"][1]["predecessor_fingerprint"] = fixture["v1_blob"]

    assert "ledger_predecessor_mismatch" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


@pytest.mark.parametrize("second_ordinal", [1, 3])
def test_ordinals_are_contiguous_and_increasing(tmp_path: Path, second_ordinal: int) -> None:
    fixture = make_linear_contract_history(tmp_path / f"bad-ordinals-{second_ordinal}")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"][1]["ordinal"] = second_ordinal

    assert "ledger_ordinal_invalid" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_later_ledger_snapshot_must_append_prior_committed_edges(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "history-rewrite")
    root = fixture["root"]
    first_snapshot = copy.deepcopy(fixture["ledger"])
    first_snapshot["edges"] = first_snapshot["edges"][:1]
    first_snapshot["digest"] = contracts.transition_ledger_digest(first_snapshot)
    path = root / ".orchestration/remaining-work/atlas/contract-transition-ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(contracts.canonical_transition_ledger_bytes(first_snapshot) + b"\n")
    subprocess.run(["git", "-C", str(root), "add", str(path.relative_to(root))], check=True)
    subprocess.run(
        ["git", "-C", str(root), "commit", "--quiet", "-m", "ledger snapshot 1"], check=True
    )
    previous_commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()

    later = copy.deepcopy(fixture["ledger"])
    later["sequence"] = 2
    later["previous_snapshot"] = {
        "commit_sha": previous_commit,
        "digest": first_snapshot["digest"],
    }
    later["digest"] = contracts.transition_ledger_digest(later)
    later["edges"][0]["result_fingerprint"] = fixture["v3_blob"]
    later["digest"] = contracts.transition_ledger_digest(later)

    assert "ledger_history_rewrite" in contracts.validate_transition_ledger(
        root, later, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_later_snapshot_can_preserve_an_unchanged_single_edge_prefix(tmp_path: Path) -> None:
    root, ledger, registry, atlas = schema_shaped_repository_history(tmp_path)
    ledger["edges"] = ledger["edges"][:1]
    ledger["digest"] = contracts.transition_ledger_digest(ledger)
    registry["persistent_index_indexer"]["fingerprint"] = ledger["edges"][0]["result_fingerprint"]
    registry["persistent_index_indexer"]["source"] = (
        f'{contracts.LEDGER_SOURCE_PATH}@{ledger["edges"][0]["candidate_commit_sha"]}'
    )
    atlas.pop("H3-B02")

    schema_path = Path(__file__).resolve().parents[2] / (
        "schemas/orchestration/remaining-work-contract-transition-ledger.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(ledger)
    assert contracts.validate_transition_ledger(root, ledger, registry, atlas) == []


def test_genesis_anchor_commit_and_path_blobs_are_fixed(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "genesis")
    expected = {
        ".orchestration/remaining-work/atlas/atlas.json": "61c6dac477427cc44ab9b782bc06c517daa67b69",
        ".orchestration/remaining-work/atlas/contract-registry.json": "ec94c2ac5e2a13fe09acad0ee8a2759ab59ac8a8",
        ".orchestration/remaining-work/prompts/H3-B01/core.json": "89d09cf417ef54084a831c23dc2ccdc5466aad10",
        ".orchestration/remaining-work/prompts/H3-B01/core.md": "012ad8b34240198131ea1174952d30f9b212d1ba",
        ".orchestration/remaining-work/prompts/H3-B01/overlay.json": "6d983af355dc72b6b41a3adeaa7fc384c7b483a2",
        ".orchestration/remaining-work/prompts/H3-B02/core.json": "4ac7e07bf9585dbb6a137502a237c867567c2762",
        ".orchestration/remaining-work/prompts/H3-B02/core.md": "8dbb3b192db40310e86ef67b96dca2facefb5c78",
        ".orchestration/remaining-work/prompts/H3-B02/overlay.json": "50c754c3be5b09a5b71fdcf9d2748563f3922240",
        "experiments/persistent_local_index/indexer.py": "b61db24259cf53f76b687ea572c24bee0037295b",
    }
    for path, blob in expected.items():
        actual = subprocess.run(
            ["git", "-C", str(fixture["root"]), "rev-parse", "--verify", f'{fixture["baseline_commit"]}:{path}'],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert actual == blob

    ledger = copy.deepcopy(fixture["ledger"])
    ledger["genesis_anchor"]["commit"] = "1" * 40
    assert "ledger_baseline_invalid" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_edge_result_equals_blob_at_exact_candidate_commit(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "exact-candidate")

    assert contracts.validate_transition_ledger(
        fixture["root"], fixture["ledger"], fixture["registry_by_id"], fixture["atlas_by_id"]
    ) == []


def test_atlas_candidate_tree_must_be_explicitly_bound(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "missing-atlas-tree")
    atlas = copy.deepcopy(fixture["atlas_by_id"])
    del atlas["H3-B02"]["candidate_generation"]["tree"]

    assert "ledger_candidate_tree_mismatch" in contracts.validate_transition_ledger(
        fixture["root"], fixture["ledger"], fixture["registry_by_id"], atlas
    )


def test_edge_rejects_candidate_tree_or_source_blob_mismatch(tmp_path: Path) -> None:
    wrong_tree = make_linear_contract_history(tmp_path / "wrong-tree", variant="wrong_declared_tree")
    assert "ledger_candidate_tree_mismatch" in contracts.validate_transition_ledger(
        wrong_tree["root"], wrong_tree["ledger"], wrong_tree["registry_by_id"], wrong_tree["atlas_by_id"]
    )

    fixture = make_linear_contract_history(tmp_path / "wrong-blob")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"][1]["source_blob"] = "0" * 40
    assert "ledger_source_blob_mismatch" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )

    wrong_path = make_linear_contract_history(
        tmp_path / "wrong-path-object", variant="wrong_source_path"
    )
    assert "ledger_source_path_invalid" in contracts.validate_transition_ledger(
        wrong_path["root"],
        wrong_path["ledger"],
        wrong_path["registry_by_id"],
        wrong_path["atlas_by_id"],
    )


@pytest.mark.parametrize("unsafe_path", ["", "/absolute/path", "../indexer.py", "a/../indexer.py"])
def test_edge_rejects_mutable_refs_and_unsafe_source_path(tmp_path: Path, unsafe_path: str) -> None:
    fixture = make_linear_contract_history(tmp_path / "unsafe-path")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"][1]["source_path"] = unsafe_path
    assert "ledger_source_path_invalid" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_edge_rejects_mutable_candidate_ref(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "mutable-ref")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"][1]["candidate_commit"] = "main"
    assert "ledger_candidate_commit_invalid" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_noninitial_edge_binds_exact_predecessor_producer_and_overlay(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "dependency-valid")
    assert contracts.validate_transition_ledger(
        fixture["root"], fixture["ledger"], fixture["registry_by_id"], fixture["atlas_by_id"]
    ) == []


def test_ancestor_without_exact_dependency_pin_is_rejected(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "dependency-missing")
    ledger = copy.deepcopy(fixture["ledger"])
    ledger["edges"][1]["dependency_evidence"] = None

    assert "ledger_dependency_evidence_missing" in contracts.validate_transition_ledger(
        fixture["root"], ledger, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_b02_overlay_base_proves_v1_and_candidate_ancestry(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    ledger, registry, atlas = repository_transition_history(root)
    assert contracts.validate_transition_ledger(root, ledger, registry, atlas) == []
    assert atlas["H3-B02"]["consumed_contracts"] == [
        {"id": "persistent_index_indexer", "fingerprint": "b61db24259cf53f76b687ea572c24bee0037295b"}
    ]
    assert atlas["H3-B02"]["candidate_generation"]["contract_fingerprints"][
        "persistent_index_indexer"
    ] == "b61db24259cf53f76b687ea572c24bee0037295b"
    assert ledger["edges"][1]["predecessor_fingerprint"] == "f5c936dc039890ad6411cde7218a82e0a2879dd7"


def test_wrong_dependency_commit_or_overlay_blob_is_rejected(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "dependency-mismatch")
    wrong_head = copy.deepcopy(fixture["ledger"])
    wrong_head["edges"][1]["dependency_evidence"]["dependency_head"] = fixture["baseline_commit"]
    assert "ledger_dependency_head_mismatch" in contracts.validate_transition_ledger(
        fixture["root"], wrong_head, fixture["registry_by_id"], fixture["atlas_by_id"]
    )

    wrong_blob = copy.deepcopy(fixture["ledger"])
    wrong_blob["edges"][1]["dependency_evidence"]["blob"] = fixture["v1_blob"]
    assert "ledger_dependency_blob_mismatch" in contracts.validate_transition_ledger(
        fixture["root"], wrong_blob, fixture["registry_by_id"], fixture["atlas_by_id"]
    )

    wrong_overlay_head = make_linear_contract_history(
        tmp_path / "overlay-wrong-head", variant="wrong_dependency_head"
    )
    assert "ledger_dependency_head_mismatch" in contracts.validate_transition_ledger(
        wrong_overlay_head["root"],
        wrong_overlay_head["ledger"],
        wrong_overlay_head["registry_by_id"],
        wrong_overlay_head["atlas_by_id"],
    )


def repository_transition_history(root: Path) -> tuple[dict, dict, dict]:
    baseline_commit = "0f5b2c22965870578a4f57bd5fdcf84569c07a89"
    baseline_tree = "6f90ab49e1ecea10b2f416e047891f594e17f447"
    baseline_blob = "b61db24259cf53f76b687ea572c24bee0037295b"
    b01_commit = "4bbb267c654dbe3c251041da4b297d7ef1f48556"
    b01_tree = "ad288a556200e2f0aac31cca9c2b1987db079aad"
    v2_blob = "f5c936dc039890ad6411cde7218a82e0a2879dd7"
    b02_commit = "f7f415648e4e7521502efe8da7fd0f352d8fc7bc"
    b02_tree = "bf65b439798ab9484b77135406fdbf36256f98aa"
    v3_blob = "8400a3fb52945a539995b041f72f1c1370f64d40"
    overlay_commit = baseline_commit
    overlay_tree = baseline_tree
    overlay_path = ".orchestration/remaining-work/prompts/H3-B02/overlay.json"
    overlay_blob = "50c754c3be5b09a5b71fdcf9d2748563f3922240"
    source_path = "experiments/persistent_local_index/indexer.py"
    ledger = {
        "contract_id": "persistent_index_indexer",
        "sequence": 1,
        "genesis_anchor": {"commit": baseline_commit, "tree": baseline_tree},
        "previous_snapshot": None,
        "baseline": {
            "contract_id": "persistent_index_indexer",
            "fingerprint": baseline_blob,
            "kind": "GIT_BLOB",
            "source_path": source_path,
            "commit": baseline_commit,
            "tree": baseline_tree,
            "blob": baseline_blob,
        },
        "edges": [
            {
                "edge_id": "persistent_index_indexer:1",
                "contract_id": "persistent_index_indexer",
                "ordinal": 1,
                "predecessor_fingerprint": baseline_blob,
                "result_fingerprint": v2_blob,
                "producer_task": "H3-B01",
                "candidate_commit": b01_commit,
                "candidate_tree": b01_tree,
                "source_path": source_path,
                "source_blob": v2_blob,
                "verification_ref": "immutable:b01",
            },
            {
                "edge_id": "persistent_index_indexer:2",
                "contract_id": "persistent_index_indexer",
                "ordinal": 2,
                "predecessor_fingerprint": v2_blob,
                "result_fingerprint": v3_blob,
                "producer_task": "H3-B02",
                "candidate_commit": b02_commit,
                "candidate_tree": b02_tree,
                "source_path": source_path,
                "source_blob": v3_blob,
                "predecessor_producer": {
                    "task_id": "H3-B01",
                    "candidate_commit": b01_commit,
                    "candidate_tree": b01_tree,
                    "result_fingerprint": v2_blob,
                },
                "dependency_evidence": {
                    "producer_task": "H3-B02",
                    "dependency_task": "H3-B01",
                    "dependency_head": b01_commit,
                    "commit": overlay_commit,
                    "tree": overlay_tree,
                    "path": overlay_path,
                    "blob": overlay_blob,
                    "base_commit": "d52009c312f1f57a7701d22758cc6e6c8f4aeb3a",
                    "base_tree": "550e9bfb169c5eb6bdb6bf7b1e138cc0a85abc9f",
                    "base_source_blob": baseline_blob,
                },
                "verification_ref": "immutable:b02",
            },
        ],
    }
    registry = {
        "persistent_index_indexer": {
            "kind": "GIT_BLOB",
            "fingerprint": v3_blob,
            "source": f"{source_path}@{b02_commit}",
        }
    }
    atlas = {
        "H3-B01": {
            "candidate_generation": {
                "sha": b01_commit,
                "tree": b01_tree,
                "contract_fingerprints": {"persistent_index_indexer": baseline_blob},
            },
            "consumed_contracts": [{"id": "persistent_index_indexer", "fingerprint": baseline_blob}],
        },
        "H3-B02": {
            "candidate_generation": {
                "sha": b02_commit,
                "tree": b02_tree,
                "contract_fingerprints": {"persistent_index_indexer": baseline_blob},
            },
            "consumed_contracts": [{"id": "persistent_index_indexer", "fingerprint": baseline_blob}],
        },
    }
    ledger["digest"] = contracts.transition_ledger_digest(ledger)
    return ledger, registry, atlas


def test_duplicate_edge_or_producer_identity_is_rejected(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "duplicates")
    duplicate_edge = copy.deepcopy(fixture["ledger"])
    duplicate_edge["edges"][1]["edge_id"] = duplicate_edge["edges"][0]["edge_id"]
    assert "ledger_edge_duplicate" in contracts.validate_transition_ledger(
        fixture["root"], duplicate_edge, fixture["registry_by_id"], fixture["atlas_by_id"]
    )

    duplicate_producer = copy.deepcopy(fixture["ledger"])
    duplicate_producer["edges"][1]["producer_task"] = duplicate_producer["edges"][0]["producer_task"]
    assert "ledger_producer_duplicate" in contracts.validate_transition_ledger(
        fixture["root"], duplicate_producer, fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_competing_successors_from_one_predecessor_fail_closed(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "competing", variant="two_successors")
    assert "ledger_competing_successor" in contracts.validate_transition_ledger(
        fixture["root"], fixture["ledger"], fixture["registry_by_id"], fixture["atlas_by_id"]
    )


def test_same_id_has_one_authenticated_linear_history(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "duplicate-contract")
    duplicate = copy.deepcopy(fixture["ledger"])
    assert "ledger_contract_duplicate" in contracts.validate_transition_ledger_rows(
        [fixture["ledger"], duplicate]
    )


def _historical_producer_inputs(fixture: dict, producer_id: str) -> tuple[dict, dict, str]:
    node = fixture["atlas_by_id"][producer_id]
    contract = {"id": "persistent_index_indexer", "fingerprint": fixture["v1_blob"]}
    current_fingerprint = fixture["v3_blob"]
    return node, contract, current_fingerprint


def _authorize_historical_input(*args) -> bool:
    authorizer = getattr(contracts, "ledger_authorizes_historical_input", None)
    assert callable(authorizer), "frozen historical producer authorization API is missing"
    return authorizer(*args)


def test_historical_producers_authorize_exact_b01_and_b02_edges(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "historical-producers")
    assert contracts.validate_transition_ledger(
        fixture["root"], fixture["ledger"], fixture["registry_by_id"], fixture["atlas_by_id"]
    ) == []

    for producer_id in ("H3-B01", "H3-B02"):
        node, contract, current_fingerprint = _historical_producer_inputs(fixture, producer_id)
        assert _authorize_historical_input(
            fixture["root"],
            node,
            contract,
            current_fingerprint,
            fixture["registry_by_id"],
            fixture["ledger"],
        ) is True

    # B02 consumed V1 at launch even though its ordered ledger edge starts at V2.
    assert fixture["ledger"]["edges"][1]["predecessor_fingerprint"] == fixture["v2_blob"]
    assert fixture["atlas_by_id"]["H3-B02"]["consumed_contracts"][0]["fingerprint"] == fixture["v1_blob"]


def test_historical_input_does_not_authorize_an_ordinary_stale_consumer(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "ordinary-stale-consumer")
    node, contract, current_fingerprint = _historical_producer_inputs(fixture, "H3-B02")
    node = copy.deepcopy(node)
    node["id"] = "ordinary-stale-consumer"

    assert _authorize_historical_input(
        fixture["root"], node, contract, current_fingerprint,
        fixture["registry_by_id"], fixture["ledger"]
    ) is False


@pytest.mark.parametrize(
    ("mutation", "contract_mutation"),
    [
        ("wrong_candidate_commit", None),
        ("wrong_candidate_tree", None),
        ("another_producer_edge", None),
        ("duplicate_matching_edge", None),
        ("wrong_consumed_fingerprint", "wrong_contract_fingerprint"),
        ("candidate_consumption_mismatch", None),
        ("wrong_contract_id", "wrong_contract_id"),
        ("wrong_current_fingerprint", None),
        ("registry_not_tip", "registry_not_tip"),
        ("source_blob_mismatch", None),
        ("branch_candidate_identity", None),
        ("malformed_candidate_sha", None),
        ("missing_edge", None),
    ],
)
def test_historical_input_rejects_unbound_or_ambiguous_evidence(
    tmp_path: Path, mutation: str, contract_mutation: str | None
) -> None:
    fixture = make_linear_contract_history(tmp_path / mutation)
    node, contract, current_fingerprint = _historical_producer_inputs(fixture, "H3-B02")
    ledger = copy.deepcopy(fixture["ledger"])
    registry = copy.deepcopy(fixture["registry_by_id"])
    node = copy.deepcopy(node)

    if mutation == "wrong_candidate_commit":
        node["candidate_generation"]["sha"] = fixture["b01_commit"]
    elif mutation == "wrong_candidate_tree":
        node["candidate_generation"]["tree"] = fixture["b01_tree"]
    elif mutation == "another_producer_edge":
        ledger["edges"][1]["producer_task"] = "H3-OTHER"
    elif mutation == "duplicate_matching_edge":
        ledger["edges"].append(copy.deepcopy(ledger["edges"][1]))
    elif mutation == "candidate_consumption_mismatch":
        node["candidate_generation"]["contract_fingerprints"]["persistent_index_indexer"] = fixture["v2_blob"]
    elif mutation == "wrong_current_fingerprint":
        current_fingerprint = fixture["v2_blob"]
    elif mutation == "source_blob_mismatch":
        ledger["edges"][1]["source_blob"] = fixture["v2_blob"]
    elif mutation == "branch_candidate_identity":
        node["candidate_generation"]["sha"] = "main"
    elif mutation == "malformed_candidate_sha":
        node["candidate_generation"]["sha"] = "a" * 39
    elif mutation == "missing_edge":
        ledger["edges"] = ledger["edges"][:1]

    if contract_mutation == "wrong_contract_fingerprint":
        contract["fingerprint"] = fixture["v2_blob"]
    elif contract_mutation == "wrong_contract_id":
        contract["id"] = "another_contract"
    elif contract_mutation == "registry_not_tip":
        registry["persistent_index_indexer"]["fingerprint"] = fixture["v2_blob"]

    assert _authorize_historical_input(
        fixture["root"], node, contract, current_fingerprint, registry, ledger
    ) is False


def schema_shaped_repository_history(tmp_path: Path) -> tuple[Path, dict, dict, dict]:
    source_root = Path(__file__).resolve().parents[2]
    old_ledger, registry, atlas = repository_transition_history(source_root)
    source_edges = old_ledger["edges"]
    baseline = old_ledger["baseline"]
    current = {
        "schema_version": "remaining-work-contract-transition-ledger.v1",
        "contract_id": "persistent_index_indexer",
        "sequence": 2,
        "genesis_anchor": {
            "commit_sha": "0f5b2c22965870578a4f57bd5fdcf84569c07a89",
            "tree_sha": "6f90ab49e1ecea10b2f416e047891f594e17f447",
        },
        "previous_snapshot": None,
        "baseline": {
            "fingerprint": baseline["fingerprint"],
            "kind": baseline["kind"],
            "source_path": baseline["source_path"],
            "commit_sha": baseline["commit"],
            "tree_sha": baseline["tree"],
            "blob_sha": baseline["blob"],
        },
        "edges": [],
    }
    for source_edge in source_edges:
        edge = {
            "edge_id": source_edge["edge_id"],
            "contract_id": source_edge["contract_id"],
            "ordinal": source_edge["ordinal"],
            "predecessor_fingerprint": source_edge["predecessor_fingerprint"],
            "result_fingerprint": source_edge["result_fingerprint"],
            "producer_task_id": source_edge["producer_task"],
            "candidate_commit_sha": source_edge["candidate_commit"],
            "candidate_tree_sha": source_edge["candidate_tree"],
            "source_path": source_edge["source_path"],
            "source_blob_sha": source_edge["source_blob"],
            "verification_ref": {
                "commit_sha": source_edge["candidate_commit"],
                "source_path": source_edge["source_path"],
                "blob_sha": source_edge["source_blob"],
            },
        }
        if source_edge["ordinal"] == 2:
            dependency = source_edge["dependency_evidence"]
            edge["predecessor_producer"] = {
                "task_id": source_edge["predecessor_producer"]["task_id"],
                "candidate_commit_sha": source_edge["predecessor_producer"]["candidate_commit"],
                "candidate_tree_sha": source_edge["predecessor_producer"]["candidate_tree"],
                "result_fingerprint": source_edge["predecessor_producer"]["result_fingerprint"],
            }
            edge["dependency_evidence"] = {
                "commit_sha": dependency["commit"],
                "source_path": dependency["path"],
                "blob_sha": dependency["blob"],
                "predecessor_task_id": dependency["dependency_task"],
                "predecessor_candidate_commit_sha": dependency["dependency_head"],
            }
        current["edges"].append(edge)

    prior = copy.deepcopy(current)
    prior["sequence"] = 1
    prior["previous_snapshot"] = None
    prior["edges"] = prior["edges"][:1]
    prior["digest"] = contracts.transition_ledger_digest(prior)

    repo = tmp_path / "schema-history"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "--quiet", "--initial-branch=main"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Ledger Test"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "ledger-test@example.invalid"], check=True
    )
    for revision in (
        "0f5b2c22965870578a4f57bd5fdcf84569c07a89",
        "4bbb267c654dbe3c251041da4b297d7ef1f48556",
        "f7f415648e4e7521502efe8da7fd0f352d8fc7bc",
        "f3d6968592278b84d2b8b82fe331a3e3d2ccc8a4",
    ):
        subprocess.run(
            ["git", "-C", str(repo), "fetch", "--quiet", "--no-tags", str(source_root), revision],
            check=True,
        )
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "--quiet", "--detach", source_edges[0]["candidate_commit"]],
        check=True,
    )
    snapshot_path = repo / ".orchestration/remaining-work/atlas/contract-transition-ledger.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_bytes(contracts.canonical_transition_ledger_bytes(prior) + b"\n")
    subprocess.run(
        ["git", "-C", str(repo), "add", ".orchestration/remaining-work/atlas/contract-transition-ledger.json"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "commit", "--quiet", "-m", "sequence one ledger"], check=True)
    previous_commit = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    current["previous_snapshot"] = {"commit_sha": previous_commit, "digest": prior["digest"]}
    current["digest"] = contracts.transition_ledger_digest(current)

    schema_path = source_root / "schemas/orchestration/remaining-work-contract-transition-ledger.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(current)
    return repo, current, registry, atlas


def test_schema_shaped_sequence_two_history_validates_exact_repository_evidence(tmp_path: Path) -> None:
    root, ledger, registry, atlas = schema_shaped_repository_history(tmp_path)
    assert contracts.validate_transition_ledger(root, ledger, registry, atlas) == []


def test_b01_candidate_requires_approved_base_ancestry(tmp_path: Path) -> None:
    root, ledger, registry, atlas = schema_shaped_repository_history(tmp_path)
    edge = ledger["edges"][0]
    unrelated_commit = subprocess.run(
        ["git", "-C", str(root), "commit-tree", edge["candidate_tree_sha"], "-m", "unrelated B01 candidate"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    edge["candidate_commit_sha"] = unrelated_commit
    edge["verification_ref"]["commit_sha"] = unrelated_commit
    atlas["H3-B01"]["candidate_generation"]["sha"] = unrelated_commit
    ledger["edges"] = ledger["edges"][:1]
    ledger["sequence"] = 1
    ledger["previous_snapshot"] = None
    registry["persistent_index_indexer"]["fingerprint"] = edge["result_fingerprint"]
    registry["persistent_index_indexer"]["source"] = f'{edge["source_path"]}@{unrelated_commit}'
    atlas.pop("H3-B02")
    ledger["digest"] = contracts.transition_ledger_digest(ledger)

    assert "ledger_candidate_ancestry_invalid" in contracts.validate_transition_ledger(
        root, ledger, registry, atlas
    )


def test_b02_overlay_cannot_be_substituted_by_another_commit(tmp_path: Path) -> None:
    root, ledger, registry, atlas = schema_shaped_repository_history(tmp_path)
    evidence = ledger["edges"][1]["dependency_evidence"]
    overlay = json.loads(
        subprocess.run(
            ["git", "-C", str(root), "show", f'{evidence["commit_sha"]}:{evidence["source_path"]}'],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    overlay["version"] = "a-different-overlay-with-the-same-dependency-pin"
    overlay_path = root / evidence["source_path"]
    overlay_path.parent.mkdir(parents=True, exist_ok=True)
    overlay_path.write_text(json.dumps(overlay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", evidence["source_path"]], check=True)
    subprocess.run(
        ["git", "-C", str(root), "commit", "--quiet", "-m", "substitute B02 overlay"], check=True
    )
    evidence["commit_sha"] = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    evidence["blob_sha"] = subprocess.run(
        ["git", "-C", str(root), "rev-parse", f'HEAD:{evidence["source_path"]}'],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    ledger["digest"] = contracts.transition_ledger_digest(ledger)

    assert "ledger_dependency_blob_mismatch" in contracts.validate_transition_ledger(
        root, ledger, registry, atlas
    )


def test_schema_history_cannot_substitute_approved_producer_or_candidate(tmp_path: Path) -> None:
    root, ledger, registry, atlas = schema_shaped_repository_history(tmp_path)
    first = ledger["edges"][0]
    alternate_commit = subprocess.run(
        [
            "git", "-C", str(root), "commit-tree", first["candidate_tree_sha"],
            "-p", "0f5b2c22965870578a4f57bd5fdcf84569c07a89",
            "-m", "substitute V2 producer candidate",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    first["producer_task"] = "H3-OTHER"
    first.pop("producer_task_id")
    first["candidate_commit_sha"] = alternate_commit
    first["verification_ref"]["commit_sha"] = alternate_commit
    atlas["H3-OTHER"] = atlas.pop("H3-B01")
    atlas["H3-OTHER"]["id"] = "H3-OTHER"
    atlas["H3-OTHER"]["candidate_generation"]["sha"] = alternate_commit
    registry["persistent_index_indexer"]["source"] = f'{first["source_path"]}@{alternate_commit}'
    ledger["edges"] = [first]
    ledger["sequence"] = 1
    ledger["previous_snapshot"] = None
    ledger["digest"] = contracts.transition_ledger_digest(ledger)
    registry["persistent_index_indexer"]["fingerprint"] = first["result_fingerprint"]
    atlas.pop("H3-B02")

    assert "ledger_candidate_commit_invalid" in contracts.validate_transition_ledger(
        root, ledger, registry, atlas
    )


def test_schema_history_with_extra_edge_fails_closed_without_crashing(tmp_path: Path) -> None:
    root, ledger, registry, atlas = schema_shaped_repository_history(tmp_path)
    ledger["edges"].append(copy.deepcopy(ledger["edges"][-1]))
    ledger["edges"][-1]["edge_id"] = "persistent_index_indexer:3"
    ledger["edges"][-1]["ordinal"] = 3
    ledger["digest"] = contracts.transition_ledger_digest(ledger)

    assert "ledger_edge_missing" in contracts.validate_transition_ledger(root, ledger, registry, atlas)


def test_concrete_b01_b02_history() -> None:
    root = Path(__file__).resolve().parents[2]
    ledger_path = root / ".orchestration/remaining-work/atlas/contract-transition-ledger.json"
    assert ledger_path.is_file(), f"concrete transition ledger artifact is missing at {ledger_path}"

    schema_path = (
        root / "schemas/orchestration/remaining-work-contract-transition-ledger.schema.json"
    )
    historical = json.loads(subprocess.run(
        ["git", "-C", str(root), "show", "2cd6095587a957575f02c2b996e881ee26c6285a:.orchestration/remaining-work/atlas/contract-transition-ledger.json"],
        check=True, capture_output=True, text=True,
    ).stdout)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(historical)
    assert historical["schema_version"] == "remaining-work-contract-transition-ledger.v1"
    assert historical["sequence"] == 1
    assert historical["previous_snapshot"] is None
    assert historical["contract_id"] == "persistent_index_indexer"
    assert len(historical["edges"]) == 2
    assert [(edge["ordinal"], edge["producer_task_id"]) for edge in historical["edges"]] == [
        (1, "H3-B01"), (2, "H3-B02")
    ]
    assert historical["digest"] == "2e79189cf7f27b494d1912b90eec595fdadb90d84af0605dcd8ba3f78a07311f"

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["edges"][:2] == historical["edges"]
    assert ledger["edges"][1]["ordinal"] == 2
    assert ledger["edges"][2]["ordinal"] == 3
    assert ledger["edges"][2]["producer_task_id"] == "H3-C02"
    assert ledger["edges"][2]["result_fingerprint"] == "875122c70f9b35bd6fae2a68d734f602bb7aeb84"
    assert ledger["edges"][2]["source_blob_sha"] == "875122c70f9b35bd6fae2a68d734f602bb7aeb84"
    assert ledger["edges"][-1] == ledger["edges"][2]

    atlas_path = root / ".orchestration/remaining-work/atlas/atlas.json"
    atlas_data = json.loads(atlas_path.read_text(encoding="utf-8"))
    atlas_by_id = {node["id"]: node for node in atlas_data.get("nodes", [])}

    registry_path = root / ".orchestration/remaining-work/atlas/contract-registry.json"
    registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
    registry_by_id = {item["id"]: item for item in registry_data.get("entries", [])}
    assert contracts.validate_transition_ledger(root, ledger, registry_by_id, atlas_by_id) == []


def test_historical_producer_output_authorizes_exact_b01_edge(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "historical-producer-output")
    node = copy.deepcopy(fixture["atlas_by_id"]["H3-B01"])
    contract = {
        "id": "persistent_index_indexer",
        "fingerprint": fixture["v2_blob"],
    }
    node["produced_contracts"] = [contract]
    assert contracts.ledger_authorizes_historical_output(
        fixture["root"],
        node,
        contract,
        fixture["ledger"],
    ) is True


def test_tip_producer_output_cannot_use_historical_exemption(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "tip-producer-output")
    node = copy.deepcopy(fixture["atlas_by_id"]["H3-B02"])
    contract = {
        "id": "persistent_index_indexer",
        "fingerprint": fixture["v3_blob"],
    }
    node["produced_contracts"] = [contract]
    # allow_tip defaults to False: the tip output must match the current registry, not use historical exemption
    assert contracts.ledger_authorizes_historical_output(
        fixture["root"],
        node,
        contract,
        fixture["ledger"],
    ) is False
    # with allow_tip=True, it validates against the edge
    assert contracts.ledger_authorizes_historical_output(
        fixture["root"],
        node,
        contract,
        fixture["ledger"],
        allow_tip=True,
    ) is True


def test_historical_producer_output_rejects_wrong_fingerprint(tmp_path: Path) -> None:
    fixture = make_linear_contract_history(tmp_path / "bad-output-fingerprint")
    node = copy.deepcopy(fixture["atlas_by_id"]["H3-B01"])
    contract = {
        "id": "persistent_index_indexer",
        "fingerprint": fixture["v1_blob"],
    }
    node["produced_contracts"] = [contract]
    assert contracts.ledger_authorizes_historical_output(
        fixture["root"],
        node,
        contract,
        fixture["ledger"],
    ) is False


def test_valid_v3_ledger_with_v1_registry_refuses_with_tip_mismatch() -> None:
    root = Path(__file__).resolve().parents[2]
    ledger_path = root / ".orchestration/remaining-work/atlas/contract-transition-ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    registry_path = root / ".orchestration/remaining-work/atlas/contract-registry.json"
    registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
    registry_by_id = {item["id"]: item for item in registry_data.get("entries", [])}
    atlas_path = root / ".orchestration/remaining-work/atlas/atlas.json"
    atlas_data = json.loads(atlas_path.read_text(encoding="utf-8"))
    atlas_by_id = {node["id"]: node for node in atlas_data.get("nodes", [])}

    assert ledger["edges"][1]["result_fingerprint"] == "8400a3fb52945a539995b041f72f1c1370f64d40"
    assert ledger["edges"][2]["result_fingerprint"] == "875122c70f9b35bd6fae2a68d734f602bb7aeb84"
    v1_registry_by_id = copy.deepcopy(registry_by_id)
    v1_registry_by_id["persistent_index_indexer"] = {
        "kind": "GIT_BLOB",
        "fingerprint": "b61db24259cf53f76b687ea572c24bee0037295b",
        "source": "experiments/persistent_local_index/indexer.py@0f5b2c22965870578a4f57bd5fdcf84569c07a89",
    }
    errors = contracts.validate_transition_ledger(root, ledger, v1_registry_by_id, atlas_by_id)
    assert "ledger_predecessor_mismatch" in errors
