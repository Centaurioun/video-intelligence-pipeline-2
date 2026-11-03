import json
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parents[3] / "schemas" / "gate1"


def _schemas():
    return {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in SCHEMA_DIR.glob("*.json")}


def _assert_closed(value):
    if isinstance(value, dict):
        if value.get("type") == "object":
            assert value.get("additionalProperties") is False
        for nested in value.values():
            _assert_closed(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_closed(nested)


def test_schema_registry_is_closed_and_has_exact_artifact_owners():
    schemas = _schemas()
    registry = schemas["registry"]
    expected = {
        "comparison_contract.json": "comparison_contract",
        "capability_descriptors.jsonl": "capability_descriptor",
        "policy_decisions.jsonl": "policy_decision",
        "run_manifest.json": "run_manifest",
        "embedding_results.jsonl": "embedding_result",
        "ranked_candidates.jsonl": "ranked_candidate",
        "judgments.jsonl": "judgment",
        "failure_ledger.json": "failure_ledger",
        "benchmark_report.json": "benchmark_report",
        "synthetic_receipt.json": "synthetic_receipt",
    }
    assert registry["artifacts"] == list(expected)
    assert registry["schemas"] == {artifact: f"{schema}.json" for artifact, schema in expected.items()}
    for name, schema in schemas.items():
        if name == "registry":
            continue
        assert schema.get("required")
        assert schema.get("type") == "object"
        assert schema.get("additionalProperties") is False
        _assert_closed(schema)
    for artifact, schema_name in registry["schemas"].items():
        assert registry["required_payload_fields"][artifact] == schemas[schema_name.removesuffix(".json")]["required"]


def test_embedding_envelope_and_payload_are_separate_closed_objects():
    schema = _schemas()["embedding_result"]
    assert schema["required"] == ["envelope", "payload"]
    envelope = schema["properties"]["envelope"]
    payload = schema["properties"]["payload"]
    assert set(envelope["properties"]) == {
        "record_id", "comparison_id", "run_id", "attempt_id", "arm_id", "input_refs",
        "consumed_coverage", "raw_response_artifact_ref", "absence_reason", "requested_model",
        "resolved_backend", "config_digest", "policy_decision_id", "provider_status",
        "per_item_errors", "wall_time_ms", "request_ref", "judgment_version_refs",
        "resource_observations", "validity_ref", "outcome_ref",
    }
    assert "representation_id" in payload["required"]
    assert "resolved_backend" not in payload["properties"]
    assert "policy_decision_id" not in payload["properties"]


def test_run_manifest_uses_validator_provenance_and_typed_candidate_inputs():
    schema = _schemas()["run_manifest"]
    assert "execution_mode" in schema["required"]
    assert "provenance" in schema["required"]
    assert "candidate_production_inputs" in schema["required"]
    assert "ranking_input_artifacts" not in schema["properties"]
    provenance = schema["properties"]["provenance"]
    assert set(provenance["required"]) == {"run_id", "attempt_id", "config_digest"}
    inputs = schema["properties"]["candidate_production_inputs"]
    query_candidate, representation = inputs["items"]["oneOf"]
    assert query_candidate["additionalProperties"] is False
    assert query_candidate["properties"]["kind"]["enum"] == ["query", "candidate"]
    assert representation["additionalProperties"] is False
    assert set(representation["required"]) == {"kind", "input_id", "arm_id", "space_id"}
    assert representation["properties"]["kind"]["const"] == "representation"
    assert "judgment" not in representation["properties"]


def test_capability_descriptor_projects_canonical_space_without_rival_identity():
    schema = _schemas()["capability_descriptor"]
    fields = schema["properties"]
    assert "space_id" in schema["required"]
    assert "representation_id" not in fields
    assert "compatibility_id" not in fields
    assert "compatibility_key" not in fields


def test_report_status_namespace_excludes_decisions_and_promotion():
    status = _schemas()["benchmark_report"]["properties"]["benchmark_status"]["enum"]
    assert status == ["PLANNED", "VALID", "INVALID_PROTOCOL", "PASS", "FAIL", "NOT_RUN"]
    assert not {"WINNER", "PROMOTED", "RECOMMENDED"}.intersection(status)


def test_public_types_keep_benchmark_envelope_separate_from_payload():
    from dataclasses import fields

    from gate1.contracts.types import BenchmarkEnvelope, CapabilityDescriptor, EmbeddingPayload

    envelope_fields = {field.name for field in fields(BenchmarkEnvelope)}
    payload_fields = {field.name for field in fields(EmbeddingPayload)}
    descriptor_fields = {field.name for field in fields(CapabilityDescriptor)}
    assert {"run_id", "attempt_id", "arm_id", "input_refs", "consumed_coverage"} <= envelope_fields
    assert {"requested_model", "resolved_backend", "config_digest", "policy_decision_id"} <= envelope_fields
    assert {"space_id", "representation_id"} <= payload_fields
    assert not {"resolved_backend", "policy_decision_id", "provider_status"} & payload_fields
    assert "space_id" in descriptor_fields
    assert "representation_id" not in descriptor_fields
    assert "compatibility_id" not in descriptor_fields


def test_types_do_not_encode_historical_gate0_sha_as_current_authority():
    from gate1.contracts import types

    assert not hasattr(types, "GATE0_CONTINUATION_BASE_SHA")
    assert not hasattr(types, "GATE0_TERMINAL_PARKED_STATE")
