"""Adversarial freeze and closed-contract tests for Gate 2 preregistration."""
from copy import deepcopy
from pathlib import Path

import pytest

from gate2.preregistration import Preregistration


ROOT = Path(__file__).resolve().parents[3]
CONTRACTS = {
    "gate2_synthetic_candidate": "88bff2e1be00bf3717a48c00a3529cabce3d16b5",
    "gate2_reconciliation": "063ae16e9ae6122bd5a460e80a4b167aa0d60a4e",
    "canonical_contracts": "c0b665d70b311dd98b7ff9f4f564b2d5750ed17b",
    "resource_policy_v5": "4e6f887a5b1e6b9855736adfe63fc6ac93ea5da9",
    "gate2_protocol_candidate": "04ea5cd54eada4ac0d0610f8f4628a7c871987b7",
    "gate2_measure_candidate": "07588fc7c721068b678f41023f7358b53c275c0b",
    "gate2_preregistration_schema_candidate": "3530190eabd6efccfae0cb090423c310c6e12c02",
    "gate2_measurement_schema_candidate": "0bf2b12cd75a0d72e815e82089f180a7d5e04070",
}


def policy():
    # Keep the tests runnable in the frozen Gate-0 venv, which intentionally
    # does not carry a YAML parser. Extract only the exercised v5 lease entries.
    text = (ROOT / "docs/portfolio/portfolio-v1/resource-policy-v5.yaml").read_text()
    assert "schema_version: 5" in text
    assert "LIGHTWEIGHT_CPU_TEST:" in text
    assert "ENV_ADMIN:" in text and "max_concurrent: 1" in text
    return {"schema_version": 5, "resource_leases": {
        "LIGHTWEIGHT_CPU_TEST": {"policy": "ADAPTIVE_READY_WORK"},
        "ENV_ADMIN": {"policy": "SERIALIZED", "max_concurrent": 1},
    }}


def valid_payload():
    return {
        "schema_version": "gate2.preregistration.v1",
        "workload_identity": {"workload_id": "synthetic-batch-01", "digest": "c" * 64},
        "configuration_identity": {"config_id": "cfg-v1", "digest": "d" * 64},
        "dependency_generations": {"gate2-protocol": "generation-7"},
        "fault_schedule": {"seed": 17, "repetitions": 2, "events": [{"at": 1, "fault": "timeout"}]},
        "metrics": [{"name": "latency_ms", "unit": "ms", "aggregation": "p95"}],
        "numeric_bounds": {"latency_ms": 1200},
        "classification_rule": {"rule_id": "latency-v1", "threshold": "latency_ms<=1200"},
        "evidence_declarations": {"source": "MEASURED"},
        "run_attempt_identity": {"run_id": "run-001", "attempt_id": "attempt-001"},
        "policy_authority": {"policy_id": "gate2-local", "authority": "approved local synthetic run"},
        "resource_request": {"resource_class": "LIGHTWEIGHT_CPU_TEST", "concurrency": 1},
        "baseline": {"storage": "SQLite descriptive baseline", "index": "local descriptive index"},
        "contract_fingerprints": dict(CONTRACTS),
        "resource_policy_identity": CONTRACTS["resource_policy_v5"],
    }


def freeze(payload=None, *, contracts=None, resource_policy=None):
    return Preregistration.from_payload(
        payload or valid_payload(),
        consumed_contracts=contracts or CONTRACTS,
        resource_policy=resource_policy or policy(),
    ).seal()


def test_freeze_is_deterministic_and_digest_tracks_material_inputs():
    original = valid_payload()
    frozen = freeze(original)
    assert freeze(deepcopy(original)).to_dict() == frozen.to_dict()
    assert freeze(deepcopy(original)).freeze_digest == frozen.freeze_digest
    assert freeze(deepcopy(original)).canonical_bytes() == frozen.canonical_bytes()

    mutations = [
        ("workload_identity", "workload_id", "synthetic-batch-02"),
        ("configuration_identity", "config_id", "cfg-v2"),
        ("numeric_bounds", "latency_ms", 1300),
        ("fault_schedule", "seed", 18),
        ("dependency_generations", "gate2-protocol", "generation-8"),
    ]
    for section, key, value in mutations:
        changed = deepcopy(original)
        changed[section][key] = value
        assert freeze(changed).freeze_digest != frozen.freeze_digest, section


def test_sealed_payload_views_cannot_mutate_the_canonical_payload_or_digest():
    frozen = freeze()
    expected = deepcopy(frozen.to_dict())
    canonical_before = frozen.canonical_bytes()

    exposed_payload = frozen.payload
    exposed_payload["metrics"][0]["name"] = "mutated-after-seal"
    exposed_payload["numeric_bounds"]["latency_ms"] = -1

    assert frozen.to_dict() == expected
    assert frozen.canonical_bytes() == canonical_before
    assert frozen.freeze_digest == expected["freeze_digest"]


@pytest.mark.parametrize("bad", [None, "", "TODO", "TBD", "NOT_OBSERVED", "null"])
def test_null_or_placeholder_fingerprints_fail_closed(bad):
    payload = valid_payload()
    payload["contract_fingerprints"]["gate2-experiment"] = bad
    with pytest.raises((TypeError, ValueError)):
        freeze(payload)


def test_stale_fingerprint_map_fails_closed():
    stale = dict(CONTRACTS)
    stale["gate2_synthetic_candidate"] = "d" * 40
    with pytest.raises((TypeError, ValueError)):
        freeze(contracts=stale)


def test_every_frozen_consumed_contract_is_required():
    payload = valid_payload()
    incomplete = dict(CONTRACTS)
    incomplete.pop("gate2_measure_candidate")
    payload["contract_fingerprints"] = incomplete
    with pytest.raises(ValueError, match="all frozen consumed contracts"):
        freeze(payload, contracts=incomplete)


def test_null_placeholder_fingerprint_is_rejected_even_when_expected_map_matches():
    payload = valid_payload()
    contracts = dict(CONTRACTS)
    contracts["gate2_reconciliation"] = "null"
    payload["contract_fingerprints"] = contracts
    with pytest.raises(ValueError, match="placeholder"):
        freeze(payload, contracts=contracts)


def test_open_top_level_and_nested_keys_fail_closed():
    payload = valid_payload()
    payload["unexpected"] = "accepted?"
    with pytest.raises((TypeError, ValueError)):
        freeze(payload)
    payload = valid_payload()
    payload["baseline"]["desired_mechanism"] = "vector database"
    with pytest.raises((TypeError, ValueError)):
        freeze(payload)


@pytest.mark.parametrize("key", ["desired_mechanism", "adoption", "disposition"])
def test_prospective_decisions_are_rejected(key):
    payload = valid_payload()
    payload[key] = "choose this"
    with pytest.raises((TypeError, ValueError)):
        freeze(payload)


def test_descriptive_current_baseline_storage_and_index_identity_is_allowed():
    frozen = freeze()
    assert frozen.payload["baseline"] == {
        "storage": "SQLite descriptive baseline",
        "index": "local descriptive index",
    }


@pytest.mark.parametrize("field,value", [
    ("fault", 7),
    ("fault", "  "),
])
def test_fault_events_match_closed_schema_types(field, value):
    payload = valid_payload()
    payload["fault_schedule"]["events"][0][field] = value
    with pytest.raises(ValueError):
        freeze(payload)


@pytest.mark.parametrize("placeholder", [
    "", "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme",
    " TODO ", "NoNe", "\tTBD\n",
])
@pytest.mark.parametrize("field", ["fault", "unit", "aggregation", "threshold"])
def test_runtime_rejects_placeholder_strings_in_schema_parity_fields(field, placeholder):
    payload = valid_payload()
    if field == "fault":
        payload["fault_schedule"]["events"][0]["fault"] = placeholder
    elif field in {"unit", "aggregation"}:
        payload["metrics"][0][field] = placeholder
    else:
        payload["classification_rule"]["threshold"] = placeholder
    with pytest.raises(ValueError, match="placeholder"):
        freeze(payload)


@pytest.mark.parametrize(("field", "valid"), [
    ("fault", "process_restart"),
    ("unit", "milliseconds"),
    ("aggregation", "p95"),
    ("threshold", "bounded recovery <= 1200ms"),
])
def test_runtime_accepts_nonplaceholder_strings_in_schema_parity_fields(field, valid):
    payload = valid_payload()
    if field == "fault":
        payload["fault_schedule"]["events"][0]["fault"] = valid
    elif field in {"unit", "aggregation"}:
        payload["metrics"][0][field] = valid
    else:
        payload["classification_rule"]["threshold"] = valid
    freeze(payload)


@pytest.mark.parametrize(("field", "value"), [
    ("name", 7),
    ("name", "bad name"),
    ("name", "_latency"),
    ("unit", 7),
    ("unit", "  "),
    ("aggregation", 7),
    ("aggregation", "  "),
])
def test_metric_fields_match_closed_schema_types(field, value):
    payload = valid_payload()
    payload["metrics"][0][field] = value
    with pytest.raises(ValueError):
        freeze(payload)


@pytest.mark.parametrize("rule_id", ["bad id", "_recovery"])
def test_classification_rule_id_matches_schema_identifier(rule_id):
    payload = valid_payload()
    payload["classification_rule"]["rule_id"] = rule_id
    with pytest.raises(ValueError):
        freeze(payload)


@pytest.mark.parametrize("field", ["metric_name", "rule_id"])
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_identifier_fields_reject_exact_ascii_case_insensitive_placeholders(field, placeholder):
    payload = valid_payload()
    value = placeholder.upper()
    if field == "metric_name":
        payload["metrics"][0]["name"] = value
    else:
        payload["classification_rule"]["rule_id"] = value
    with pytest.raises(ValueError):
        freeze(payload)


@pytest.mark.parametrize("field", ["metric_name", "rule_id"])
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_identifier_fields_accept_embedded_ascii_case_insensitive_placeholder_words(field, placeholder):
    payload = valid_payload()
    value = f"metric-{placeholder}-v1"
    if field == "metric_name":
        payload["metrics"][0]["name"] = value
    else:
        payload["classification_rule"]["rule_id"] = value
    freeze(payload)


_IDENTIFIER_VALUE_PATHS = [
    ("workload_identity", "workload_id"),
    ("configuration_identity", "config_id"),
    ("metrics", 0, "name"),
    ("classification_rule", "rule_id"),
    ("run_attempt_identity", "run_id"),
    ("run_attempt_identity", "attempt_id"),
    ("policy_authority", "policy_id"),
    ("dependency_generations", "gate2-protocol"),
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
def test_all_identifier_values_reject_exact_ascii_case_insensitive_placeholders(path, placeholder):
    payload = valid_payload()
    _set_path(payload, path, placeholder.upper())
    with pytest.raises(ValueError, match="placeholder|identifier|generation"):
        freeze(payload)


@pytest.mark.parametrize("path", _IDENTIFIER_VALUE_PATHS)
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_all_identifier_values_accept_embedded_ascii_case_insensitive_placeholder_words(path, placeholder):
    payload = valid_payload()
    _set_path(payload, path, f"prefix-{placeholder.upper()}-suffix")
    freeze(payload)


@pytest.mark.parametrize("section", ["dependency_generations", "numeric_bounds", "evidence_declarations"])
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_identifier_property_names_reject_exact_ascii_case_insensitive_placeholders(section, placeholder):
    payload = valid_payload()
    mapping = payload[section]
    value = mapping.pop(next(iter(mapping)))
    mapping[placeholder.upper()] = value
    with pytest.raises(ValueError, match="placeholder|identifier|generation"):
        freeze(payload)


@pytest.mark.parametrize("section", ["dependency_generations", "numeric_bounds", "evidence_declarations"])
@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_identifier_property_names_accept_embedded_placeholder_words(section, placeholder):
    payload = valid_payload()
    mapping = payload[section]
    value = mapping.pop(next(iter(mapping)))
    mapping[f"prefix-{placeholder.upper()}-suffix"] = value
    freeze(payload)


@pytest.mark.parametrize(("section", "field", "value"), [
    ("workload_identity", "workload_id", "ToDo"),
    ("configuration_identity", "config_id", "  TBD  "),
    ("run_attempt_identity", "run_id", "NuLl"),
    ("policy_authority", "policy_id", "PLACEHOLDER"),
    ("policy_authority", "authority", "  NoNe  "),
    ("baseline", "storage", "  NuLl  "),
    ("baseline", "index", "PLACEHOLDER"),
])
def test_casefolded_or_trimmed_placeholders_are_rejected_in_identity_and_authority_fields(section, field, value):
    payload = valid_payload()
    payload[section][field] = value
    with pytest.raises(ValueError, match="placeholder|identifier"):
        freeze(payload)


@pytest.mark.parametrize("threshold", [0, 1.25])
def test_numeric_classification_threshold_allowed_by_schema(threshold):
    payload = valid_payload()
    payload["classification_rule"]["threshold"] = threshold
    assert freeze(payload).payload["classification_rule"]["threshold"] == threshold


@pytest.mark.parametrize("threshold", [True, False, "  "])
def test_invalid_classification_threshold_rejected(threshold):
    payload = valid_payload()
    payload["classification_rule"]["threshold"] = threshold
    with pytest.raises(ValueError):
        freeze(payload)


def test_empty_fault_events_match_schema():
    payload = valid_payload()
    payload["fault_schedule"]["events"] = []
    assert freeze(payload).payload["fault_schedule"]["events"] == []


def test_resource_class_and_concurrency_follow_supplied_v5_semantics():
    supplied = policy()
    payload = valid_payload()
    # This adaptive class has no numeric max_concurrent in v5; do not freeze in
    # a historical static ceiling copied into preregistration code.
    payload["resource_request"] = {"resource_class": "LIGHTWEIGHT_CPU_TEST", "concurrency": 9}
    assert freeze(payload, resource_policy=supplied).payload["resource_request"]["concurrency"] == 9

    payload["resource_request"] = {"resource_class": "ENV_ADMIN", "concurrency": 2}
    with pytest.raises((TypeError, ValueError)):
        freeze(payload, resource_policy=supplied)

    payload["resource_request"] = {"resource_class": "MIXED_HEAVY", "concurrency": 1}
    supplied["resource_leases"]["MIXED_HEAVY"] = {"policy": "CALIBRATE_SEPARATELY"}
    with pytest.raises(ValueError, match="requires calibration"):
        freeze(payload, resource_policy=supplied)

    payload["resource_request"] = {"resource_class": "UNKNOWN_CLASS", "concurrency": 1}
    with pytest.raises((TypeError, ValueError)):
        freeze(payload, resource_policy=supplied)
