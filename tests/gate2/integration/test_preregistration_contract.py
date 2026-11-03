"""Integration contract for Gate-2 preregistration sealing (no workload execution)."""
from copy import deepcopy
import json
from pathlib import Path
import re

import pytest
from jsonschema import Draft202012Validator

from gate2.preregistration import Preregistration, PreregistrationError


CONSUMED = {
    "gate2_synthetic_candidate": "88bff2e1be00bf3717a48c00a3529cabce3d16b5",
    "gate2_reconciliation": "063ae16e9ae6122bd5a460e80a4b167aa0d60a4e",
    "canonical_contracts": "c0b665d70b311dd98b7ff9f4f564b2d5750ed17b",
    "resource_policy_v5": "4e6f887a5b1e6b9855736adfe63fc6ac93ea5da9",
    "gate2_protocol_candidate": "04ea5cd54eada4ac0d0610f8f4628a7c871987b7",
    "gate2_measure_candidate": "07588fc7c721068b678f41023f7358b53c275c0b",
    "gate2_preregistration_schema_candidate": "3530190eabd6efccfae0cb090423c310c6e12c02",
    "gate2_measurement_schema_candidate": "0bf2b12cd75a0d72e815e82089f180a7d5e04070",
}
POLICY = {
    "schema_version": 5,
    "resource_leases": {
        "LIGHTWEIGHT_CPU_TEST": {"policy": "ADAPTIVE_READY_WORK", "fixed_quota": False},
        "HEAVY_CPU": {"policy": "ADAPTIVE_MEASURED_LEASE", "initial_max_concurrent": 2, "calibration_target_max_concurrent": 3, "fallback_max_concurrent": 1},
    },
}


def valid_payload():
    return {
        "schema_version": "gate2.preregistration.v1",
        "workload_identity": {"workload_id": "synthetic-recovery-v1", "digest": "a" * 64},
        "configuration_identity": {"config_id": "cfg-v1", "digest": "b" * 64},
        "dependency_generations": {"index": "index-generation-7", "fvs": "fvs-generation-2"},
        "fault_schedule": {"seed": 17, "repetitions": 5, "events": [{"at": 2, "fault": "process_restart"}]},
        "metrics": [{"name": "recovery_latency_ms", "unit": "ms", "aggregation": "p95"}],
        "numeric_bounds": {"max_recovery_latency_ms": 900.0, "min_success_rate": 0.95},
        "classification_rule": {"rule_id": "recovery-v1", "threshold": "bounded_recovery"},
        "evidence_declarations": {"recovery_latency_ms": "MEASURED", "baseline_relation": "MATCHED"},
        "run_attempt_identity": {"run_id": "run-001", "attempt_id": "attempt-001"},
        "policy_authority": {"policy_id": "local-synthetic-policy-v1", "authority": "local_synthetic_only"},
        "resource_request": {"resource_class": "LIGHTWEIGHT_CPU_TEST", "concurrency": 8},
        "baseline": {"storage": "SQLite-backed index", "index": "current persistent index"},
        "contract_fingerprints": dict(CONSUMED),
        "resource_policy_identity": CONSUMED["resource_policy_v5"],
    }


def seal(payload=None, policy=POLICY):
    return Preregistration.from_payload(payload or valid_payload(), consumed_contracts=CONSUMED, resource_policy=policy).seal()


def test_freeze_is_canonical_and_binds_inputs_and_authority():
    first = seal()
    second = seal(deepcopy(valid_payload()))
    assert first.freeze_digest == second.freeze_digest
    changed = valid_payload()
    changed["fault_schedule"]["seed"] += 1
    assert seal(changed).freeze_digest != first.freeze_digest
    changed = valid_payload()
    changed["dependency_generations"]["index"] = "index-generation-8"
    assert seal(changed).freeze_digest != first.freeze_digest
    changed = valid_payload()
    changed["numeric_bounds"]["max_recovery_latency_ms"] = 901
    assert seal(changed).freeze_digest != first.freeze_digest
    assert first.to_dict()["freeze_digest"] == first.freeze_digest


@pytest.mark.parametrize("mutate", [
    lambda p: p.update(workload_identity=None),
    lambda p: p.update(unreviewed_extra="value"),
    lambda p: p["workload_identity"].update(workload_id="TBD"),
    lambda p: p["contract_fingerprints"].update(canonical_contracts="0" * 40),
    lambda p: p.update(desired_mechanism="ANN index"),
    lambda p: p.update(adoption="adopt durable queue"),
    lambda p: p.update(disposition="PASS"),
])
def test_invalid_or_preselected_inputs_fail_closed(mutate):
    payload = valid_payload()
    mutate(payload)
    with pytest.raises(PreregistrationError):
        seal(payload)


def test_descriptive_baseline_identity_is_not_mechanism_preselection():
    payload = valid_payload()
    payload["baseline"]["storage"] = "SQLite-backed index generation 7"
    assert seal(payload).freeze_digest


def test_resource_concurrency_follows_policy_without_historical_ceiling():
    payload = valid_payload()
    payload["resource_request"] = {"resource_class": "LIGHTWEIGHT_CPU_TEST", "concurrency": 64}
    assert seal(payload).freeze_digest
    payload["resource_request"] = {"resource_class": "HEAVY_CPU", "concurrency": 3}
    assert seal(payload).freeze_digest
    payload["resource_request"]["concurrency"] = 4
    with pytest.raises(PreregistrationError):
        seal(payload)


def test_runtime_seal_matches_preregistration_schema_for_threshold_and_empty_faults():
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    properties = schema["properties"]
    assert properties["classification_rule"]["properties"]["threshold"]["type"] == ["number", "string"]
    assert properties["classification_rule"]["properties"]["rule_id"]["$ref"] == "#/$defs/identifier"
    event_schema = properties["fault_schedule"]["properties"]["events"]
    assert "minItems" not in event_schema
    assert event_schema["items"]["properties"]["fault"]["type"] == "string"
    metric_properties = properties["metrics"]["items"]["properties"]
    assert metric_properties["name"]["$ref"] == "#/$defs/identifier"
    assert all(metric_properties[field]["type"] == "string" for field in ("unit", "aggregation"))
    for threshold in (1.25, "bounded_recovery"):
        payload = valid_payload()
        payload["classification_rule"]["threshold"] = threshold
        payload["fault_schedule"]["events"] = []
        frozen = seal(payload).to_dict()
        assert frozen["classification_rule"]["threshold"] == threshold


@pytest.mark.parametrize(("field", "valid"), [
    ("fault", "process_restart"),
    ("unit", "milliseconds"),
    ("aggregation", "p95"),
    ("threshold", "bounded recovery <= 1200ms"),
])
def test_schema_string_fields_match_runtime_placeholder_policy(field, valid):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    properties = schema["properties"]
    field_schemas = {
        "fault": properties["fault_schedule"]["properties"]["events"]["items"]["properties"]["fault"],
        "unit": properties["metrics"]["items"]["properties"]["unit"],
        "aggregation": properties["metrics"]["items"]["properties"]["aggregation"],
        "threshold": properties["classification_rule"]["properties"]["threshold"],
    }
    pattern = re.compile(field_schemas[field]["pattern"])
    placeholders = ["", "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme",
                    " TODO ", "NoNe", "\tTBD\n"]
    assert not any(pattern.search(value) for value in placeholders)
    assert pattern.search(valid)


def test_draft_2020_12_schema_validates_sealed_payload_and_nearby_controls():
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    valid = seal().to_dict()
    assert validator.is_valid(valid)

    controls = deepcopy(valid)
    controls["workload_identity"]["workload_id"] = "synthetic-batch-02"
    controls["configuration_identity"]["config_id"] = "none-other"
    controls["baseline"]["storage"] = "nullary descriptive storage"
    controls["baseline"]["index"] = "local descriptive index"
    controls["policy_authority"]["authority"] = "approved local synthetic run"
    assert validator.is_valid(controls)

    rejected = deepcopy(valid)
    rejected["workload_identity"]["workload_id"] = "ToDo"
    assert not validator.is_valid(rejected)

    rejected = deepcopy(valid)
    rejected["configuration_identity"]["config_id"] = "  TBD  "
    assert not validator.is_valid(rejected)

    rejected = deepcopy(valid)
    rejected["baseline"]["storage"] = "  NuLl  "
    assert not validator.is_valid(rejected)

    rejected = deepcopy(valid)
    rejected["baseline"]["index"] = "PLACEHOLDER"
    assert not validator.is_valid(rejected)

    rejected = deepcopy(valid)
    rejected["policy_authority"]["authority"] = "  NoNe  "
    assert not validator.is_valid(rejected)


@pytest.mark.parametrize("field", ["metric_name", "rule_id"])
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_schema_identifier_fields_reject_exact_ascii_case_insensitive_placeholders(field, placeholder):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()
    value = placeholder.upper()
    if field == "metric_name":
        payload["metrics"][0]["name"] = value
    else:
        payload["classification_rule"]["rule_id"] = value
    assert not validator.is_valid(payload)


@pytest.mark.parametrize("field", ["metric_name", "rule_id"])
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_schema_identifier_fields_accept_embedded_placeholder_words(field, placeholder):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()
    value = f"metric-{placeholder}-v1"
    if field == "metric_name":
        payload["metrics"][0]["name"] = value
    else:
        payload["classification_rule"]["rule_id"] = value
    assert validator.is_valid(payload)


_IDENTIFIER_VALUE_PATHS = [
    ("workload_identity", "workload_id"),
    ("configuration_identity", "config_id"),
    ("dependency_generations", "index"),
    ("metrics", 0, "name"),
    ("classification_rule", "rule_id"),
    ("run_attempt_identity", "run_id"),
    ("run_attempt_identity", "attempt_id"),
    ("policy_authority", "policy_id"),
]


def _set_path(payload, path, value):
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


@pytest.mark.parametrize("path", _IDENTIFIER_VALUE_PATHS)
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_schema_all_identifier_values_reject_exact_ascii_case_insensitive_placeholders(path, placeholder):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()
    _set_path(payload, path, placeholder.upper())
    assert not validator.is_valid(payload), path


@pytest.mark.parametrize("path", _IDENTIFIER_VALUE_PATHS)
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_schema_all_identifier_values_accept_embedded_placeholder_words(path, placeholder):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()
    _set_path(payload, path, f"prefix-{placeholder.upper()}-suffix")
    assert validator.is_valid(payload), path


@pytest.mark.parametrize("section", ["dependency_generations", "numeric_bounds", "evidence_declarations"])
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_schema_identifier_property_names_reject_exact_ascii_case_insensitive_placeholders(section, placeholder):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()
    mapping = payload[section]
    value = mapping.pop(next(iter(mapping)))
    mapping[placeholder.upper()] = value
    assert not validator.is_valid(payload), section


@pytest.mark.parametrize("section", ["dependency_generations", "numeric_bounds", "evidence_declarations"])
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_schema_identifier_property_names_accept_embedded_placeholder_words(section, placeholder):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()
    mapping = payload[section]
    value = mapping.pop(next(iter(mapping)))
    mapping[f"prefix-{placeholder.upper()}-suffix"] = value
    assert validator.is_valid(payload), section


@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_measurement_metric_id_schema_rejects_exact_ascii_case_insensitive_placeholders(placeholder):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/measurement.json").read_text())
    validator = Draft202012Validator(schema)
    payload = {
        "schema_version": "gate2.measurement.v1",
        "measured": [{
            "metric_id": placeholder.upper(), "unit": "count", "value": 1,
            "evidence_class": "MEASURED", "derivation": "counted",
        }],
        "not_observed": [],
        "measurement_set_digest": "a" * 64,
    }
    assert not validator.is_valid(payload)


@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_measurement_metric_id_schema_accepts_embedded_placeholder_words(placeholder):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/measurement.json").read_text())
    validator = Draft202012Validator(schema)
    payload = {
        "schema_version": "gate2.measurement.v1",
        "measured": [{
            "metric_id": f"metric-{placeholder.upper()}-v1", "unit": "count", "value": 1,
            "evidence_class": "MEASURED", "derivation": "counted",
        }],
        "not_observed": [],
        "measurement_set_digest": "a" * 64,
    }
    assert validator.is_valid(payload)


@pytest.mark.parametrize(("path", "value"), [
    (("workload_identity", "digest"), "0" * 64),
    (("configuration_identity", "digest"), "0" * 64),
    (("contract_fingerprints", "gate2_synthetic_candidate"), "0" * 40),
    (("contract_fingerprints", "gate2_synthetic_candidate"), "0" * 64),
    (("resource_policy_identity",), "0" * 40),
    (("resource_policy_identity",), "0" * 64),
    (("dependency_generations", "gate2-protocol"), "  NuLl  "),
    (("dependency_generations", "gate2-protocol"), "0" * 64),
    (("workload_identity", "workload_id"), "  ToDo  "),
    (("run_attempt_identity", "run_id"), "0" * 64),
    (("configuration_identity", "config_id"), "PLACEHOLDER"),
    (("policy_authority", "policy_id"), "  NoNe  "),
    (("policy_authority", "authority"), "0" * 64),
    (("baseline", "storage"), "  TBD  "),
    (("baseline", "index"), "0" * 64),
    (("fault_schedule", "events", 0, "fault"), "  XXX  "),
    (("fault_schedule", "events", 0, "fault"), "0" * 64),
    (("metrics", 0, "unit"), "  CHANGEme  "),
    (("metrics", 0, "unit"), "0" * 64),
    (("metrics", 0, "aggregation"), "0" * 64),
    (("classification_rule", "threshold"), "  PLACEHOLDER  "),
])
def test_draft_2020_12_rejects_placeholders_and_zero_sentinel_across_value_categories(path, value):
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert not validator.is_valid(payload), path


def test_draft_2020_12_accepts_nearby_valid_controls_for_placeholder_values():
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()
    payload["workload_identity"]["digest"] = "1" * 64
    payload["configuration_identity"]["digest"] = "2" * 64
    payload["contract_fingerprints"]["gate2_synthetic_candidate"] = "a" * 40
    payload["contract_fingerprints"]["gate2_reconciliation"] = "c" * 64
    payload["resource_policy_identity"] = "b" * 40
    payload["dependency_generations"]["gate2-protocol"] = "generation-8"
    payload["workload_identity"]["workload_id"] = "synthetic-batch-02"
    payload["configuration_identity"]["config_id"] = "cfg-v2"
    payload["policy_authority"]["policy_id"] = "local-policy-v2"
    payload["policy_authority"]["authority"] = "approved local synthetic run"
    payload["baseline"]["storage"] = "SQLite descriptive storage"
    payload["baseline"]["index"] = "local index generation 2"
    payload["fault_schedule"]["events"][0]["fault"] = "process_restart"
    payload["metrics"][0]["unit"] = "milliseconds"
    payload["metrics"][0]["aggregation"] = "p95"
    payload["classification_rule"]["threshold"] = "bounded recovery <= 1200ms"
    assert validator.is_valid(payload)


def test_draft_2020_12_accepts_embedded_placeholder_tokens_in_identifiers():
    schema = json.loads((Path(__file__).resolve().parents[3] / "schemas/gate2/preregistration.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    payload = seal().to_dict()

    payload["workload_identity"]["workload_id"] = "ToDoPlan"
    payload["configuration_identity"]["config_id"] = "myPlaceholderPolicy"
    payload["run_attempt_identity"]["run_id"] = "none-other"
    payload["run_attempt_identity"]["attempt_id"] = "0" * 63
    payload["policy_authority"]["policy_id"] = "0" * 65

    assert validator.is_valid(payload)
