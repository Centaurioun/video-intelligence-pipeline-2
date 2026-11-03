"""F03 verifier: fail-closed evidence admission with git-object provenance."""
import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from gate2.preregistration import Preregistration
from gate2.verify import (
    _ACCEPTED_DEPENDENCY_HEADS,
    _F01_RESOURCE_POLICY,
    discover_git_root,
    git_blob_sha,
    resolve_accepted_heads,
    resolve_contract_fingerprints,
    verify_evidence,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "schemas" / "gate2" / "verification-evidence.v2.json"
# Current-generation consumed-contract identities are derived from real Git
# objects; they are never hand-declared in this test module.
F01_CONSUMED_CONTRACTS = resolve_contract_fingerprints(REPO_ROOT)
F01_RESOURCE_POLICY = _F01_RESOURCE_POLICY
ACCEPTED_HEADS = copy.deepcopy(_ACCEPTED_DEPENDENCY_HEADS)
F03_TEST_METRIC = "fixture_generation_wall_time"
F01_PAYLOAD = {
    "schema_version": "gate2.preregistration.v1",
    "workload_identity": {"workload_id": "synthetic-scale-v1", "digest": "a" * 64},
    "configuration_identity": {"config_id": "cfg-f03-v1", "digest": "b" * 64},
    "dependency_generations": {"F01": ACCEPTED_HEADS["F01"]["sha"], "F02": ACCEPTED_HEADS["F02"]["sha"]},
    "fault_schedule": {"seed": 20261017, "repetitions": 2, "events": [{"at": 1, "fault": "process_restart"}]},
    "metrics": [{"name": F03_TEST_METRIC, "unit": "milliseconds", "aggregation": "median"}],
    "numeric_bounds": {F03_TEST_METRIC: 30000},
    "classification_rule": {"rule_id": "f03-bounded-v1", "threshold": "within_numeric_bound"},
    "evidence_declarations": {F03_TEST_METRIC: "MEASURED"},
    "run_attempt_identity": {"run_id": "f03-run-002", "attempt_id": "f03-attempt-001"},
    "policy_authority": {"policy_id": "f03-synthetic-v1", "authority": "owner-approved-local-synthetic-only"},
    "resource_request": {"resource_class": "HEAVY_CPU", "concurrency": 1},
    "baseline": {"storage": "local-generated-fixture", "index": "synthetic-in-memory"},
    "contract_fingerprints": F01_CONSUMED_CONTRACTS,
    "resource_policy_identity": F01_CONSUMED_CONTRACTS["resource_policy_v5"],
}
_IDENTITY_KEYS = (
    "metric_id", "repetition", "status", "value", "unit", "dependency_id",
    "evidence_class", "carrier_path", "carrier_sha256",
    "dependency_heads", "candidate",
    "preregistration_digest", "freeze_digest", "workload_digest",
    "config_digest", "fault_schedule_digest",
)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _reason_provenance(item, state="MEASURED", reason_code="OBSERVED"):
    return {
        "schema_version": "gate2.reason-provenance.v1",
        "state": state,
        "reason_code": reason_code,
        "evidence_identity": {key: copy.deepcopy(item[key]) for key in _IDENTITY_KEYS},
    }


def _seal(payload, root):
    frozen = Preregistration.from_payload(
        payload,
        consumed_contracts=F01_CONSUMED_CONTRACTS,
        resource_policy=F01_RESOURCE_POLICY,
    ).seal()
    path = root / "preregistration.json"
    path.write_bytes(frozen.canonical_bytes())
    return frozen, path


def _contract_for(payload, frozen, prereg_path):
    definitions = {}
    for metric in payload["metrics"]:
        name = metric["name"]
        definitions[name] = {
            "unit": metric["unit"],
            "min": 0,
            "max": payload["numeric_bounds"][name],
            "repetitions": payload["fault_schedule"]["repetitions"],
        }
    return {
        "dependency_heads": copy.deepcopy(ACCEPTED_HEADS),
        "preregistration_path": prereg_path.name,
        "preregistration_digest": hashlib.sha256(prereg_path.read_bytes()).hexdigest(),
        "freeze_digest": frozen.freeze_digest,
        "workload_digest": payload["workload_identity"]["digest"],
        "config_digest": payload["configuration_identity"]["digest"],
        "fault_schedule_digest": _digest(payload["fault_schedule"]),
        "metric_definitions": definitions,
        "decision_digest": "e" * 64,
        "candidate": copy.deepcopy(ACCEPTED_HEADS["F02"]),
    }


def _f01_bound_evidence(root, payload=None):
    payload = copy.deepcopy(F01_PAYLOAD if payload is None else payload)
    frozen, prereg_path = _seal(payload, root)
    contract = _contract_for(payload, frozen, prereg_path)
    evidence = {"version": "f03-evidence.v2", **copy.deepcopy(contract), "observations": []}
    for metric in payload["metrics"]:
        for repetition in range(1, payload["fault_schedule"]["repetitions"] + 1):
            item = {
                "metric_id": metric["name"],
                "status": "NOT_OBSERVED",
                "value": None,
                "unit": metric["unit"],
                "evidence_class": None,
                "carrier_path": None,
                "carrier_sha256": None,
                "dependency_id": "F01+F02",
                "dependency_heads": copy.deepcopy(ACCEPTED_HEADS),
                "candidate": copy.deepcopy(ACCEPTED_HEADS["F02"]),
                "preregistration_digest": contract["preregistration_digest"],
                "freeze_digest": frozen.freeze_digest,
                "workload_digest": contract["workload_digest"],
                "config_digest": contract["config_digest"],
                "fault_schedule_digest": contract["fault_schedule_digest"],
                "repetition": repetition,
            }
            item["reason_provenance"] = _reason_provenance(item, "UNAVAILABLE", "SOURCE_UNAVAILABLE")
            evidence["observations"].append(item)
    return contract, evidence


def _verify(evidence, contract, root):
    return verify_evidence(evidence, contract, carrier_root=root, git_root=REPO_ROOT)


def _measured_pair(tmp_path):
    contract, evidence = _f01_bound_evidence(tmp_path)
    metric_id, definition = next(iter(contract["metric_definitions"].items()))
    for item in evidence["observations"]:
        repetition = item["repetition"]
        carrier = tmp_path / "metrics" / f"{repetition}.json"
        carrier.parent.mkdir(parents=True, exist_ok=True)
        carrier.write_text(
            json.dumps([{"repetition": repetition, "metric_id": metric_id, "unit": definition["unit"], "value": 125}]),
            encoding="utf-8",
        )
        item.update({
            "status": "MEASURED",
            "value": 125,
            "evidence_class": "MEASURED",
            "carrier_path": f"metrics/{repetition}.json",
            "carrier_sha256": hashlib.sha256(carrier.read_bytes()).hexdigest(),
        })
        item["reason_provenance"] = _reason_provenance(item)
    return contract, evidence, tmp_path


@pytest.fixture
def bound_pair(tmp_path):
    return _measured_pair(tmp_path)


# ---------------------------------------------------------------- provenance

def test_consumed_contract_fingerprints_are_derived_from_real_git_objects():
    resolved = resolve_contract_fingerprints(REPO_ROOT)
    assert set(resolved) == set(F01_CONSUMED_CONTRACTS)
    assert resolved["gate2_measure_candidate"] == git_blob_sha((REPO_ROOT / "src/gate2/measure.py").read_bytes())
    # The superseded F01-generation pins must not survive as current identity.
    assert resolved["gate2_measure_candidate"] != "07588fc7c721068b678f41023f7358b53c275c0b"
    assert resolved["gate2_preregistration_schema_candidate"] != "3530190eabd6efccfae0cb090423c310c6e12c02"
    assert resolved["gate2_measurement_schema_candidate"] != "0bf2b12cd75a0d72e815e82089f180a7d5e04070"


def test_accepted_generations_resolve_to_declared_commits_and_trees():
    assert resolve_accepted_heads(REPO_ROOT) == _ACCEPTED_DEPENDENCY_HEADS


def test_git_root_discovery_fails_outside_a_repository(tmp_path):
    outside = tmp_path / "not-a-repository"
    outside.mkdir()
    assert discover_git_root(outside) is None


def test_rejects_when_git_provenance_is_unresolvable(bound_pair, tmp_path):
    contract, evidence, _root = bound_pair
    outside = tmp_path / "not-a-repository"
    outside.mkdir()
    result = verify_evidence(evidence, contract, carrier_root=_root, git_root=outside)
    assert result["verified"] is False
    assert any("git-object provenance unavailable" in error for error in result["errors"])


def test_rejects_when_accepted_generations_are_absent(bound_pair, tmp_path):
    contract, evidence, root = bound_pair
    repo = tmp_path / "empty-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.email=a@b", "-c", "user.name=a", "commit", "--allow-empty", "-q", "-m", "empty"],
        cwd=repo,
        check=True,
    )
    result = verify_evidence(evidence, contract, carrier_root=root, git_root=repo)
    assert result["verified"] is False
    assert any("git-object provenance unavailable" in error for error in result["errors"])


# ---------------------------------------------------------------- envelope

def test_accepts_exact_current_v2_evidence(tmp_path):
    contract, evidence = _f01_bound_evidence(tmp_path)
    result = _verify(evidence, contract, tmp_path)
    assert result["verified"] is True
    assert result["production_eligible"] is False
    assert result["gate_promotion"] is False
    assert result["mechanism_adopted"] is False


def test_rejects_v1_envelope_downgrade(bound_pair):
    contract, evidence, root = bound_pair
    downgraded = copy.deepcopy(evidence)
    downgraded["version"] = "f03-evidence.v1"
    result = _verify(downgraded, contract, root)
    assert result["verified"] is False
    assert any("unsupported evidence envelope version" in error for error in result["errors"])


def test_historical_v1_not_observed_evidence_is_not_admitted(tmp_path):
    contract, evidence = _f01_bound_evidence(tmp_path)
    historical = copy.deepcopy(evidence)
    historical["version"] = "f03-evidence.v1"
    for item in historical["observations"]:
        del item["reason_provenance"]
    before = copy.deepcopy(historical)
    result = _verify(historical, contract, tmp_path)
    assert result["verified"] is False
    assert any("unsupported evidence envelope version" in error for error in result["errors"])
    assert historical == before


@pytest.mark.parametrize("mutation", [
    lambda payload: payload.update(unexpected="open field"),
    lambda payload: payload["contract_fingerprints"].update(gate2_synthetic_candidate="0" * 40),
])
def test_rejects_open_or_stale_accepted_f01_preregistration(tmp_path, mutation):
    contract, evidence = _f01_bound_evidence(tmp_path)
    preregistration_path = tmp_path / "preregistration.json"
    preregistration = json.loads(preregistration_path.read_text(encoding="utf-8"))
    mutation(preregistration)
    preregistration_path.write_text(json.dumps(preregistration, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    contract["preregistration_digest"] = hashlib.sha256(preregistration_path.read_bytes()).hexdigest()
    evidence["preregistration_digest"] = contract["preregistration_digest"]
    assert _verify(evidence, contract, tmp_path)["verified"] is False


def test_rejects_modified_f01_freeze_digest_even_when_file_digest_is_rebound(tmp_path):
    contract, evidence = _f01_bound_evidence(tmp_path)
    preregistration_path = tmp_path / "preregistration.json"
    preregistration = json.loads(preregistration_path.read_text(encoding="utf-8"))
    preregistration["freeze_digest"] = "f" * 64
    preregistration_path.write_text(json.dumps(preregistration, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    contract["preregistration_digest"] = hashlib.sha256(preregistration_path.read_bytes()).hexdigest()
    evidence["preregistration_digest"] = contract["preregistration_digest"]
    assert _verify(evidence, contract, tmp_path)["verified"] is False


@pytest.mark.parametrize("field", ["workload_digest", "config_digest", "fault_schedule_digest"])
def test_rejects_contract_digests_not_derived_from_f01_payload(tmp_path, field):
    contract, evidence = _f01_bound_evidence(tmp_path)
    forged = "9" * 64
    contract[field] = forged
    evidence[field] = forged
    for observation in evidence["observations"]:
        observation[field] = forged
        observation["reason_provenance"] = _reason_provenance(observation, "UNAVAILABLE", "SOURCE_UNAVAILABLE")
    assert _verify(evidence, contract, tmp_path)["verified"] is False


def test_rejects_unknown_observation_fields(bound_pair):
    contract, evidence, root = bound_pair
    evidence["observations"][0]["unreviewed_metadata"] = "must not be ignored"
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("unknown observation fields" in error for error in result["errors"])


# ---------------------------------------------------------------- declarations

def _payload_with_metrics(names, declarations):
    payload = copy.deepcopy(F01_PAYLOAD)
    payload["metrics"] = [{"name": name, "unit": "milliseconds", "aggregation": "median"} for name in names]
    payload["numeric_bounds"] = {name: 30000 for name in names}
    payload["evidence_declarations"] = dict(declarations)
    return payload


def test_rejects_declarations_that_do_not_cover_the_preregistered_metrics(tmp_path):
    payload = _payload_with_metrics([F03_TEST_METRIC, "restart_recovery_wall_time"], {F03_TEST_METRIC: "MEASURED"})
    contract, evidence = _f01_bound_evidence(tmp_path, payload=payload)
    result = _verify(evidence, contract, tmp_path)
    assert result["verified"] is False
    assert any("evidence declarations must cover exactly" in error for error in result["errors"])


def test_preregistration_requires_nonempty_evidence_declarations(tmp_path):
    payload = _payload_with_metrics([F03_TEST_METRIC], {})
    with pytest.raises(Exception):
        Preregistration.from_payload(
            payload,
            consumed_contracts=F01_CONSUMED_CONTRACTS,
            resource_policy=F01_RESOURCE_POLICY,
        ).seal()


def test_rejects_declared_evidence_class_that_disagrees_with_measurement(tmp_path):
    contract, evidence, root = _measured_pair(tmp_path)
    payload = _payload_with_metrics([F03_TEST_METRIC], {F03_TEST_METRIC: "EDITORIAL_INFERENCE"})
    frozen, prereg_path = _seal(payload, tmp_path)
    contract = _contract_for(payload, frozen, prereg_path)
    evidence = copy.deepcopy(evidence)
    for key in ("preregistration_path", "preregistration_digest", "freeze_digest", "workload_digest",
                "config_digest", "fault_schedule_digest", "metric_definitions", "decision_digest"):
        evidence[key] = copy.deepcopy(contract[key])
    for item in evidence["observations"]:
        item["preregistration_digest"] = contract["preregistration_digest"]
        item["freeze_digest"] = contract["freeze_digest"]
        item["reason_provenance"] = _reason_provenance(item)
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("does not match the preregistered declaration" in error for error in result["errors"])


# ---------------------------------------------------------------- carriers

@pytest.mark.parametrize("field,value", [
    ("preregistration_digest", "9" * 64), ("freeze_digest", "9" * 64),
    ("workload_digest", "9" * 64), ("config_digest", "9" * 64),
    ("fault_schedule_digest", "9" * 64),
])
def test_rejects_changed_identity(bound_pair, field, value):
    contract, evidence, root = bound_pair
    evidence[field] = value
    assert not _verify(evidence, contract, root)["verified"]


def test_rejects_changed_dependency_head_metric_unit_bound_or_repetitions(bound_pair):
    contract, evidence, root = bound_pair
    evidence["dependency_heads"]["F02"]["sha"] = "9" * 40
    assert not _verify(evidence, contract, root)["verified"]

    contract, evidence, root = bound_pair
    evidence["metric_definitions"][F03_TEST_METRIC]["unit"] = "seconds"
    assert not _verify(evidence, contract, root)["verified"]

    contract, evidence, root = bound_pair
    evidence["metric_definitions"][F03_TEST_METRIC]["max"] = 999
    assert not _verify(evidence, contract, root)["verified"]

    contract, evidence, root = bound_pair
    evidence["metric_definitions"][F03_TEST_METRIC]["repetitions"] = 4
    assert not _verify(evidence, contract, root)["verified"]


def test_rejects_observation_unit_and_evidence_class_change(bound_pair):
    contract, evidence, root = bound_pair
    evidence["observations"][0]["unit"] = "seconds"
    assert not _verify(evidence, contract, root)["verified"]

    contract, evidence, root = bound_pair
    evidence["observations"][0]["evidence_class"] = "EDITORIAL_INFERENCE"
    assert not _verify(evidence, contract, root)["verified"]


def test_rejects_not_observed_evidence_class_claim(bound_pair):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item.update(status="NOT_OBSERVED", value=None, carrier_path=None, carrier_sha256=None,
                evidence_class="NOT_OBSERVED")
    item["reason_provenance"] = _reason_provenance(item, "UNAVAILABLE", "SOURCE_UNAVAILABLE")
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("invalid evidence class" in error for error in result["errors"])


def test_rejects_changed_decision_digest(bound_pair):
    contract, evidence, root = bound_pair
    evidence["decision_digest"] = "8" * 64
    assert not _verify(evidence, contract, root)["verified"]


def test_rejects_missing_carrier_even_with_well_formed_hash(bound_pair):
    contract, evidence, root = bound_pair
    (root / evidence["observations"][0]["carrier_path"]).unlink()
    assert not _verify(evidence, contract, root)["verified"]


def test_rejects_carrier_content_hash_or_value_mismatch(bound_pair):
    contract, evidence, root = bound_pair
    carrier = root / evidence["observations"][0]["carrier_path"]
    carrier.write_text(
        json.dumps({"metric_id": F03_TEST_METRIC, "observations": [{"repetition": 1, "unit": "milliseconds", "value": 999}]}),
        encoding="utf-8",
    )
    assert not _verify(evidence, contract, root)["verified"]


def test_rejects_path_escape(bound_pair, tmp_path):
    contract, evidence, root = bound_pair
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps([{"repetition": 1, "metric_id": F03_TEST_METRIC, "unit": "milliseconds", "value": 125}]), encoding="utf-8")
    item = evidence["observations"][0]
    item["carrier_path"] = "../outside.json"
    item["carrier_sha256"] = hashlib.sha256(outside.read_bytes()).hexdigest()
    item["reason_provenance"] = _reason_provenance(item)
    assert not _verify(evidence, contract, root)["verified"]


def test_accepts_not_observed_null_and_one_based_repetitions(bound_pair):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item.update(status="NOT_OBSERVED", value=None, evidence_class=None, carrier_path=None, carrier_sha256=None)
    item["reason_provenance"] = _reason_provenance(item, "UNAVAILABLE", "SOURCE_UNAVAILABLE")
    assert _verify(evidence, contract, root)["verified"]


def test_accepts_exact_current_carrier(bound_pair):
    contract, evidence, root = bound_pair
    result = _verify(evidence, contract, root)
    assert result["verified"] is True
    assert result["production_eligible"] is False
    assert result["gate_promotion"] is False
    assert result["mechanism_adopted"] is False


# ---------------------------------------------------------------- INFERRED

def test_inferred_reason_provenance_is_admitted_for_not_observed(bound_pair):
    contract, evidence, root = bound_pair
    inferred = copy.deepcopy(evidence)
    for item in inferred["observations"]:
        item.update(status="NOT_OBSERVED", value=None, evidence_class=None, carrier_path=None, carrier_sha256=None)
        item["reason_provenance"] = _reason_provenance(item, "INFERRED", "CONTEXT_INFERENCE")
    result = _verify(inferred, contract, root)
    assert result["verified"] is True
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(inferred)


def test_inferred_reason_provenance_is_not_admitted_for_measured(bound_pair):
    contract, evidence, root = bound_pair
    inferred = copy.deepcopy(evidence)
    for item in inferred["observations"]:
        item["reason_provenance"] = _reason_provenance(item, "INFERRED", "CONTEXT_INFERENCE")
    assert _verify(inferred, contract, root)["verified"] is False
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert not Draft202012Validator(schema).is_valid(inferred)


def test_v2_rejects_missing_conflicting_malformed_and_stale_reason_provenance(bound_pair):
    contract, evidence, root = bound_pair

    missing = copy.deepcopy(evidence)
    del missing["observations"][0]["reason_provenance"]
    assert not _verify(missing, contract, root)["verified"]

    conflicting = copy.deepcopy(evidence)
    provenance = conflicting["observations"][0]["reason_provenance"]
    provenance["state"] = "UNAVAILABLE"
    provenance["reason_code"] = "SOURCE_UNAVAILABLE"
    assert not _verify(conflicting, contract, root)["verified"]

    malformed = copy.deepcopy(evidence)
    malformed["observations"][0]["reason_provenance"]["unreviewed"] = True
    assert not _verify(malformed, contract, root)["verified"]

    malformed_state = copy.deepcopy(evidence)
    malformed_state["observations"][0]["reason_provenance"]["state"] = []
    assert not _verify(malformed_state, contract, root)["verified"]

    stale = copy.deepcopy(evidence)
    stale["observations"][0]["reason_provenance"]["evidence_identity"]["workload_digest"] = "9" * 64
    assert not _verify(stale, contract, root)["verified"]

    changed_dependency = copy.deepcopy(evidence)
    changed_dependency["observations"][0]["dependency_id"] = "F01"
    assert not _verify(changed_dependency, contract, root)["verified"]


def test_v2_schema_rejects_observation_shapes_runtime_verifier_rejects(bound_pair):
    contract, evidence, root = bound_pair
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    measured_without_carrier = copy.deepcopy(evidence)
    item = measured_without_carrier["observations"][0]
    item.update(value=None, evidence_class=None, carrier_path=None, carrier_sha256=None)
    item["reason_provenance"] = _reason_provenance(item)
    assert _verify(measured_without_carrier, contract, root)["verified"] is False
    assert not validator.is_valid(measured_without_carrier)

    not_observed_with_carrier = copy.deepcopy(evidence)
    item = not_observed_with_carrier["observations"][0]
    item.update(status="NOT_OBSERVED", value=125, evidence_class="MEASURED")
    item["reason_provenance"] = _reason_provenance(item, "UNAVAILABLE", "SOURCE_UNAVAILABLE")
    assert _verify(not_observed_with_carrier, contract, root)["verified"] is False
    assert not validator.is_valid(not_observed_with_carrier)


# ---------------------------------------------------------------- historical attempts

def test_historical_attempt4_dependency_cannot_provide_a_current_carrier(bound_pair):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item["dependency_id"] = "persistent_index_attempt4"
    item["reason_provenance"] = _reason_provenance(item)
    assert not _verify(evidence, contract, root)["verified"]


@pytest.mark.parametrize("carrier_path", [
    "persistent-index/attempt-4.json",
    "persistent-index/attempt_4.json",
    "persistent-index/ATTEMPT4.json",
    "persistent-index/attempt 4.json",
    "persistent-index/attempt.4.json",
    "persistent-index/attempt#4.json",
    "persistent_index/attempt04.json",
])
def test_historical_attempt4_path_variants_cannot_be_current_measurements(bound_pair, carrier_path):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item["carrier_path"] = carrier_path
    item["reason_provenance"] = _reason_provenance(item)
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("historical Attempt-4" in error for error in result["errors"])


def test_attempt_40_is_not_mistaken_for_attempt_4(bound_pair):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item["carrier_path"] = "persistent-index/attempt-40.json"
    item["reason_provenance"] = _reason_provenance(item)
    result = _verify(evidence, contract, root)
    assert not any("historical Attempt-4" in error for error in result["errors"])


def test_dependency_source_must_be_pinned_or_a_pinned_composite(bound_pair):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item["dependency_id"] = "F01+F02"
    item["reason_provenance"] = _reason_provenance(item)
    assert _verify(evidence, contract, root)["verified"] is True

    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item["dependency_id"] = "F03"
    item["reason_provenance"] = _reason_provenance(item)
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("unknown dependency source" in error for error in result["errors"])


# ---------------------------------------------------------------- forged contracts

def test_rejects_forged_contract_bounds_or_classes_even_when_envelope_matches(bound_pair):
    contract, evidence, root = bound_pair
    for field_value in ({"max": 999999}, {"deficit_class": "C5-recovery-time"}):
        forged = copy.deepcopy(contract)
        forged["metric_definitions"][F03_TEST_METRIC].update(field_value)
        forged_evidence = copy.deepcopy(evidence)
        forged_evidence["metric_definitions"] = copy.deepcopy(forged["metric_definitions"])
        result = _verify(forged_evidence, forged, root)
        assert result["verified"] is False
        assert any("preregistration-derived" in error for error in result["errors"])


def test_rejects_envelope_top_level_candidate_mismatch(bound_pair):
    contract, evidence, root = bound_pair
    evidence["candidate"] = {"sha": "8" * 40, "tree": "9" * 40}
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("candidate identity mismatch" in error for error in result["errors"])


def test_preregistration_bytes_must_match_pinned_digest(bound_pair):
    contract, evidence, root = bound_pair
    (root / "preregistration.json").write_text("{}", encoding="utf-8")
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("preregistration digest does not match" in error for error in result["errors"])


# ------------------------------------------------- independent-audit regressions

def test_all_consumed_fingerprints_resolve_from_the_accepted_f01_commit():
    accepted_f01 = _ACCEPTED_DEPENDENCY_HEADS["F01"]["sha"]
    resolved = resolve_contract_fingerprints(REPO_ROOT)
    path_contracts = {
        "gate2_reconciliation": "docs/audits/2026-09-13-portfolio-state-reconciliation-after-gate2-m3.md",
        "canonical_contracts": "docs/architecture/CANONICAL_CONTRACTS.md",
        "resource_policy_v5": "docs/portfolio/portfolio-v1/resource-policy-v5.yaml",
        "gate2_measure_candidate": "src/gate2/measure.py",
        "gate2_preregistration_schema_candidate": "schemas/gate2/preregistration.json",
        "gate2_measurement_schema_candidate": "schemas/gate2/measurement.json",
    }
    for contract_id, relative in path_contracts.items():
        committed = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", f"{accepted_f01}:{relative}"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        assert resolved[contract_id] == committed, contract_id


def test_docs_fingerprints_do_not_track_worktree_bytes():
    resolved = resolve_contract_fingerprints(REPO_ROOT)
    for contract_id in ("gate2_reconciliation", "canonical_contracts", "resource_policy_v5"):
        # Derived from the accepted generation, never from the checked-out file.
        assert resolved[contract_id] != git_blob_sha(b"tampered in the worktree")
        assert resolved[contract_id] != git_blob_sha(b"")


def _two_metric_measured(tmp_path):
    names = ["fixture_generation_wall_time", "restart_recovery_wall_time"]
    payload = _payload_with_metrics(names, {name: "MEASURED" for name in names})
    contract, evidence = _f01_bound_evidence(tmp_path, payload=payload)
    carriers = {}
    for metric_id in names:
        definition = contract["metric_definitions"][metric_id]
        for repetition in (1, 2):
            carrier = tmp_path / "metrics" / f"{metric_id}-{repetition}.json"
            carrier.parent.mkdir(parents=True, exist_ok=True)
            carrier.write_text(
                json.dumps([{"repetition": repetition, "metric_id": metric_id,
                             "unit": definition["unit"], "value": 125}]),
                encoding="utf-8",
            )
            carriers[(metric_id, repetition)] = carrier
    for item in evidence["observations"]:
        carrier = carriers[(item["metric_id"], item["repetition"])]
        item.update({
            "status": "MEASURED",
            "value": 125,
            "evidence_class": "MEASURED",
            "carrier_path": carrier.relative_to(tmp_path).as_posix(),
            "carrier_sha256": hashlib.sha256(carrier.read_bytes()).hexdigest(),
        })
        item["reason_provenance"] = _reason_provenance(item)
    return contract, evidence, tmp_path


def test_accepts_two_metrics_bound_to_their_own_carriers(tmp_path):
    contract, evidence, root = _two_metric_measured(tmp_path)
    result = _verify(evidence, contract, root)
    assert result["verified"] is True, result["errors"]


def test_rejects_cross_metric_list_carrier_substitution(tmp_path):
    contract, evidence, root = _two_metric_measured(tmp_path)
    rows = {item["metric_id"]: item for item in evidence["observations"] if item["repetition"] == 1}
    left, right = rows["fixture_generation_wall_time"], rows["restart_recovery_wall_time"]
    left["carrier_path"], right["carrier_path"] = right["carrier_path"], left["carrier_path"]
    left["carrier_sha256"], right["carrier_sha256"] = right["carrier_sha256"], left["carrier_sha256"]
    for item in (left, right):
        item["reason_provenance"] = _reason_provenance(item)
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("carrier observation metric identity mismatch" in error for error in result["errors"])


def test_rejects_unknown_top_level_evidence_fields(bound_pair):
    contract, evidence, root = bound_pair
    evidence["production_eligible"] = True
    evidence["forged_extra"] = {"claim": "promotion"}
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("evidence envelope is incomplete or has unknown fields" in error for error in result["errors"])


def test_rejects_duplicate_repetition_indices(bound_pair):
    contract, evidence, root = bound_pair
    second = evidence["observations"][1]
    second["repetition"] = 1
    second["reason_provenance"] = _reason_provenance(second)
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("duplicate repetition index" in error for error in result["errors"])


def test_discloses_declared_measured_without_observation(tmp_path):
    contract, evidence = _f01_bound_evidence(tmp_path)
    result = _verify(evidence, contract, tmp_path)
    assert result["verified"] is True, result["errors"]
    assert result["declared_measured_without_observation"] == [F03_TEST_METRIC]


def test_rejects_unit_change_when_provenance_is_rebound(bound_pair):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item["unit"] = "seconds"
    item["reason_provenance"] = _reason_provenance(item)
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("carrier unit mismatch" in error for error in result["errors"])


def test_rejects_non_measured_class_when_provenance_is_rebound(bound_pair):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    item["evidence_class"] = "MATCHED"
    item["reason_provenance"] = _reason_provenance(item)
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("non-measured evidence class" in error or "does not match the preregistered declaration" in error
               for error in result["errors"])


def test_rejects_carrier_value_change_when_hash_and_provenance_are_rebound(bound_pair):
    contract, evidence, root = bound_pair
    item = evidence["observations"][0]
    carrier = root / item["carrier_path"]
    row = json.loads(carrier.read_text(encoding="utf-8"))[0]
    row["value"] = 999
    carrier.write_text(json.dumps([row]), encoding="utf-8")
    item["carrier_sha256"] = hashlib.sha256(carrier.read_bytes()).hexdigest()
    item["reason_provenance"] = _reason_provenance(item)
    result = _verify(evidence, contract, root)
    assert result["verified"] is False
    assert any("carrier observation mismatch" in error for error in result["errors"])
