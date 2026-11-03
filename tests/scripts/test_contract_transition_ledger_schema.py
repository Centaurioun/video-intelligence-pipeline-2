import copy
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    ROOT
    / "schemas/orchestration/remaining-work-contract-transition-ledger.schema.json"
)
GENESIS_COMMIT = "0f5b2c22965870578a4f57bd5fdcf84569c07a89"
GENESIS_TREE = "6f90ab49e1ecea10b2f416e047891f594e17f447"
V1 = "b61db24259cf53f76b687ea572c24bee0037295b"
V2 = "f5c936dc039890ad6411cde7218a82e0a2879dd7"
V3 = "8400a3fb52945a539995b041f72f1c1370f64d40"
SOURCE_PATH = "experiments/persistent_local_index/indexer.py"
HISTORICAL_V1_COMMIT = "2cd6095587a957575f02c2b996e881ee26c6285a"


def _sha(byte: str) -> str:
    return byte * 40


def _blob(byte: str) -> str:
    return byte * 40


def _digest(byte: str) -> str:
    return byte * 64


def _baseline() -> dict:
    return {
        "fingerprint": V1,
        "kind": "GIT_BLOB",
        "source_path": SOURCE_PATH,
        "commit_sha": GENESIS_COMMIT,
        "tree_sha": GENESIS_TREE,
        "blob_sha": V1,
    }


def _verification_ref() -> dict:
    return {
        "commit_sha": _sha("a"),
        "source_path": "docs/verification/transition-v1.md",
        "blob_sha": _blob("b"),
    }


def _edge(ordinal: int, predecessor: str, result: str, byte: str) -> dict:
    edge = {
        "edge_id": f"persistent_index_indexer:{ordinal}",
        "contract_id": "persistent_index_indexer",
        "ordinal": ordinal,
        "predecessor_fingerprint": predecessor,
        "result_fingerprint": result,
        "producer_task_id": f"H3-B0{ordinal}",
        "candidate_commit_sha": _sha(byte),
        "candidate_tree_sha": _sha(chr(ord(byte) + 1)),
        "source_path": SOURCE_PATH,
        "source_blob_sha": result,
        "verification_ref": _verification_ref(),
    }
    if ordinal > 1:
        edge["predecessor_producer"] = {
            "task_id": "H3-B01",
            "candidate_commit_sha": _sha("c"),
            "candidate_tree_sha": _sha("d"),
            "result_fingerprint": V2,
        }
        edge["dependency_evidence"] = {
            "commit_sha": _sha("e"),
            "source_path": ".orchestration/remaining-work/prompts/H3-B02/overlay.json",
            "blob_sha": _blob("f"),
            "predecessor_task_id": "H3-B01",
            "predecessor_candidate_commit_sha": _sha("c"),
        }
    return edge


def _ledger() -> dict:
    return {
        "schema_version": "remaining-work-contract-transition-ledger.v1",
        "contract_id": "persistent_index_indexer",
        "sequence": 1,
        "genesis_anchor": {"commit_sha": GENESIS_COMMIT, "tree_sha": GENESIS_TREE},
        "previous_snapshot": None,
        "baseline": _baseline(),
        "edges": [_edge(1, V1, V2, "1")],
        "digest": _digest("0"),
    }


def _sequence_two_ledger() -> dict:
    ledger = _ledger()
    ledger["sequence"] = 2
    ledger["previous_snapshot"] = {
        "commit_sha": _sha("7"),
        "digest": _digest("8"),
    }
    ledger["edges"] = [
        _edge(1, V1, V2, "1"),
        _edge(2, V2, V3, "3"),
    ]
    return ledger


def _sequence_one_two_edge_ledger() -> dict:
    ledger = _sequence_two_ledger()
    ledger["sequence"] = 1
    ledger["previous_snapshot"] = None
    return ledger


def _validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_v2_schema_requires_exact_third_edge_and_predecessor_snapshot():
    path = ROOT / "schemas/orchestration/remaining-work-contract-transition-ledger.v2.schema.json"
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    ledger = _ledger()
    historical = json.loads(subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{HISTORICAL_V1_COMMIT}:.orchestration/remaining-work/atlas/contract-transition-ledger.json"],
        check=True, capture_output=True, text=True,
    ).stdout)
    assert historical["schema_version"] == "remaining-work-contract-transition-ledger.v1"
    assert historical["sequence"] == 1
    assert len(historical["edges"]) == 2
    assert [(edge["ordinal"], edge["producer_task_id"]) for edge in historical["edges"]] == [
        (1, "H3-B01"), (2, "H3-B02")
    ]
    assert historical["digest"] == "2e79189cf7f27b494d1912b90eec595fdadb90d84af0605dcd8ba3f78a07311f"
    ledger.update({
        "schema_version": "remaining-work-contract-transition-ledger.v2",
        "sequence": 2,
        "previous_snapshot": {
            "commit_sha": HISTORICAL_V1_COMMIT,
            "digest": "2e79189cf7f27b494d1912b90eec595fdadb90d84af0605dcd8ba3f78a07311f",
        },
        "edges": copy.deepcopy(historical["edges"]),
    })
    third = _edge(3, V3, "875122c70f9b35bd6fae2a68d734f602bb7aeb84", "4")
    third.update({
        "edge_id": "persistent_index_indexer:3",
        "producer_task_id": "H3-C02",
        "candidate_commit_sha": "44a7d4d931d5219efc781f8da54fab850ba8bcc1",
        "candidate_tree_sha": "5206b1f5c326596a02ec2295202db374f8d42ce5",
        "source_blob_sha": "875122c70f9b35bd6fae2a68d734f602bb7aeb84",
        "predecessor_producer": {
            "task_id": "H3-B02",
            "candidate_commit_sha": "f7f415648e4e7521502efe8da7fd0f352d8fc7bc",
            "candidate_tree_sha": "bf65b439798ab9484b77135406fdbf36256f98aa",
            "result_fingerprint": "8400a3fb52945a539995b041f72f1c1370f64d40",
        },
        "dependency_evidence": {
            "commit_sha": "2cd6095587a957575f02c2b996e881ee26c6285a",
            "source_path": ".orchestration/remaining-work/prompts/H3-C02/overlay-verify-batch008.json",
            "blob_sha": "8fbeb4301b9245968108975cc27a7fbb27d863e2",
            "predecessor_task_id": "H3-B02",
            "predecessor_candidate_commit_sha": "f7f415648e4e7521502efe8da7fd0f352d8fc7bc",
        },
    })
    ledger["edges"].append(third)
    assert len(ledger["edges"]) == 3
    assert ledger["edges"][:2] == historical["edges"]
    assert ledger["edges"][1]["ordinal"] == 2
    assert ledger["edges"][2]["ordinal"] == 3
    assert ledger["edges"][2]["result_fingerprint"] == "875122c70f9b35bd6fae2a68d734f602bb7aeb84"
    assert Draft202012Validator(schema).is_valid(ledger)

    for field in ("predecessor_fingerprint", "result_fingerprint", "producer_task_id", "candidate_commit_sha", "candidate_tree_sha", "source_blob_sha"):
        original = third[field]
        third[field] = "0" * 40 if field != "producer_task_id" else "H3-OTHER"
        assert not Draft202012Validator(schema).is_valid(ledger), field
        third[field] = original
    for field in ("predecessor_producer", "dependency_evidence"):
        saved = third.pop(field)
        assert not Draft202012Validator(schema).is_valid(ledger), field
        third[field] = saved
    third["dependency_evidence"]["blob_sha"] = "0" * 40
    assert not Draft202012Validator(schema).is_valid(ledger)
    third["dependency_evidence"]["blob_sha"] = "8fbeb4301b9245968108975cc27a7fbb27d863e2"
    ledger["previous_snapshot"]["commit_sha"] = "0" * 40
    assert not Draft202012Validator(schema).is_valid(ledger)
    ledger["previous_snapshot"]["commit_sha"] = "2cd6095587a957575f02c2b996e881ee26c6285a"
    ledger["previous_snapshot"]["digest"] = "0" * 64
    assert not Draft202012Validator(schema).is_valid(ledger)


def _assert_invalid(ledger: dict) -> None:
    assert list(_validator().iter_errors(ledger))


def test_ledger_schema_accepts_baseline_and_ordered_edge():
    assert _validator().is_valid(_ledger())
    assert _validator().is_valid(_sequence_two_ledger())


def test_sequence_one_accepts_one_or_two_ordered_edges():
    validator = _validator()
    assert validator.is_valid(_ledger())
    assert validator.is_valid(_sequence_one_two_edge_ledger())


def test_later_sequence_can_preserve_an_unchanged_one_edge_prefix():
    ledger = _sequence_two_ledger()
    ledger["edges"] = ledger["edges"][:1]

    assert _validator().is_valid(ledger)


def test_ledger_schema_requires_exact_contract_id_and_immutable_genesis_anchor():
    ledger = _ledger()
    ledger["contract_id"] = "persistent_index_indexer_v2"
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["edges"][0]["contract_id"] = "persistent_index_indexer_v2"
    _assert_invalid(ledger)

    ledger = _ledger()
    del ledger["genesis_anchor"]
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["genesis_anchor"]["commit_sha"] = _sha("9")
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["baseline"]["tree_sha"] = _sha("9")
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["baseline"]["blob_sha"] = _sha("9")
    _assert_invalid(ledger)


def test_ledger_schema_rejects_unknown_fields_and_mutable_refs():
    ledger = _ledger()
    ledger["unexpected"] = True
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["edges"][0]["candidate_commit_sha"] = "main"
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["edges"][0]["candidate_ref"] = "refs/heads/main"
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["edges"][0]["source_path"] = "../experiments/indexer.py"
    _assert_invalid(ledger)


def test_ledger_schema_requires_noninitial_predecessor_evidence():
    ledger = _sequence_two_ledger()
    del ledger["edges"][1]["predecessor_producer"]
    _assert_invalid(ledger)

    ledger = _sequence_two_ledger()
    del ledger["edges"][1]["dependency_evidence"]
    _assert_invalid(ledger)


def test_ledger_schema_requires_genesis_and_sequence_linkage():
    ledger = _ledger()
    ledger["previous_snapshot"] = {
        "commit_sha": _sha("7"),
        "digest": _digest("8"),
    }
    _assert_invalid(ledger)

    ledger = _sequence_two_ledger()
    ledger["previous_snapshot"] = None
    _assert_invalid(ledger)

    ledger = _sequence_one_two_edge_ledger()
    ledger["previous_snapshot"] = {
        "commit_sha": _sha("7"),
        "digest": _digest("8"),
    }
    _assert_invalid(ledger)

    ledger = _sequence_two_ledger()
    del ledger["previous_snapshot"]["digest"]
    _assert_invalid(ledger)

    ledger = _sequence_two_ledger()
    del ledger["previous_snapshot"]["commit_sha"]
    _assert_invalid(ledger)


def test_ledger_schema_rejects_malformed_git_ids_and_blob_bindings():
    ledger = _ledger()
    ledger["edges"][0]["candidate_commit_sha"] = "a" * 39
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["edges"][0]["candidate_tree_sha"] = "z" * 40
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["edges"][0]["source_blob_sha"] = "not-a-blob"
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["digest"] = "g" * 64
    _assert_invalid(ledger)


def test_ledger_schema_rejects_missing_producer_and_candidate_bindings():
    ledger = _ledger()
    del ledger["edges"][0]["producer_task_id"]
    _assert_invalid(ledger)

    for field in ("candidate_commit_sha", "candidate_tree_sha", "source_path"):
        ledger = _ledger()
        del ledger["edges"][0][field]
        _assert_invalid(ledger)


def test_ledger_schema_rejects_malformed_transition_edges():
    ledger = _ledger()
    ledger["edges"][0]["ordinal"] = 0
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["edges"][0]["predecessor_fingerprint"] = "bad"
    _assert_invalid(ledger)

    ledger = _ledger()
    ledger["edges"][0]["unsupported"] = "value"
    _assert_invalid(ledger)

    ledger = _sequence_two_ledger()
    ledger["edges"][1]["edge_id"] = ledger["edges"][0]["edge_id"]
    _assert_invalid(ledger)


def test_ledger_schema_rejects_malformed_registry_tip_binding():
    ledger = _ledger()
    ledger["registry_tip"] = {
        "contract_id": "persistent_index_indexer",
        "fingerprint": V1,
        "source": "@main",
    }
    _assert_invalid(ledger)


def test_ledger_schema_rejects_mutable_or_malformed_dependency_provenance():
    ledger = _sequence_two_ledger()
    ledger["edges"][1]["dependency_evidence"]["commit_sha"] = "origin/main"
    _assert_invalid(ledger)

    ledger = _sequence_two_ledger()
    ledger["edges"][1]["dependency_evidence"]["blob_sha"] = "bad"
    _assert_invalid(ledger)
