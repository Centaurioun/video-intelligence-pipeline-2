"""Golden structural and cross-artifact contract tests for all 13 T01 owners."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
from gate0.contracts.validator import ARTIFACT_FILENAMES, ContractError, validate_artifact_set
ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = ROOT / "schemas" / "gate0"
SEMANTIC_CLOSURE_FIXTURE = ROOT / "tests" / "gate0" / "fixtures" / "semantic-closure"

#: §9.2 gate-decision matrix fields (the markdown artifact has no JSON schema).
GATE_DECISION_PAYLOAD = {
    "run_id", "benchmark_status", "gate_decision", "stop_reason",
    "metrics_digest", "threshold_digest", "authority", "reviewers", "decided_at",
}

def test_registry_is_exactly_the_closed_thirteen_artifact_set():
    registry = json.loads((SCHEMA_ROOT / "registry.json").read_text())
    assert tuple(registry["artifacts"]) == ARTIFACT_FILENAMES and len(ARTIFACT_FILENAMES) == 13
    assert set(registry["schemas"]) == set(ARTIFACT_FILENAMES)
    for name in ARTIFACT_FILENAMES:
        assert (SCHEMA_ROOT / registry["schemas"][name]).is_file()

def _assert_closed(node, path="schema"):
    if isinstance(node, dict):
        if node.get("type") == "object" or "properties" in node:
            assert node.get("additionalProperties") is False, path
        for key, value in node.items():
            # ``if``/``then``/``else`` hold partial applicator conditions (e.g.
            # record_type -> payload branch binding), not closed object shapes;
            # their property maps intentionally omit additionalProperties.
            if key in {"if", "then", "else"}:
                continue
            _assert_closed(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node): _assert_closed(value, f"{path}[{index}]")

@pytest.mark.parametrize("artifact", ARTIFACT_FILENAMES)
def test_every_artifact_schema_is_closed_and_has_required_fields(artifact):
    registry = json.loads((SCHEMA_ROOT / "registry.json").read_text())
    schema_path = SCHEMA_ROOT / registry["schemas"][artifact]
    if artifact == "gate_decision.md":
        raw = schema_path.read_bytes()
        assert raw and b"\r" not in raw
        text = raw.decode("utf-8")
        assert text == text.rstrip() + "\n"
        assert text.strip()
        return
    schema = json.loads(schema_path.read_text())
    assert schema.get("properties") and schema.get("required")
    _assert_closed(schema, artifact)

def test_artifact_count_rejects_missing_and_fourteenth_result():
    with pytest.raises(ContractError, match="exactly 13"):
        validate_artifact_set(ARTIFACT_FILENAMES[:-1], {})
    with pytest.raises(ContractError, match="exactly 13"):
        validate_artifact_set(ARTIFACT_FILENAMES + ("unexpected.json",), {})

def test_executable_verifier_wires_schema_and_count_checks():
    result = subprocess.run([sys.executable, str(ROOT / "scripts/verify-gate0.py"), "--schemas", "--artifact-count=13"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "artifact_count=13" in result.stdout

def test_run_manifest_schema_resolves_sandbox_and_requires_residual_state_surface():
    schema = json.loads((SCHEMA_ROOT / "run_manifest.json").read_text())
    expected = {
        "schema_version", "run_id", "gate_owner_id", "source_revision_ids",
        "config_digest", "dependency_lock_digest", "policy_decision_ids",
        "thresholds", "runtime", "sandbox", "invocations", "blinding",
        "stage_transitions", "attempts", "artifact_envelopes",
        "representations", "repeat_comparisons", "status",
    }
    assert set(schema["required"]) == expected
    assert schema["properties"]["sandbox"] == {"$ref": "#/$defs/sandbox"}
    sandbox = schema["$defs"]["sandbox"]
    assert sandbox["type"] == "object"
    assert sandbox["additionalProperties"] is False
    assert set(sandbox["required"]) == {
        "bwrap_path", "bwrap_version", "bwrap_digest", "interpreter_path",
        "interpreter_version", "interpreter_digest", "read_only_mounts",
        "writable_mounts", "clearenv", "net_unshared", "argv_digest",
        "mount_policy_digest", "child_network_sentinel",
    }

def test_run_and_stage_status_namespaces_are_distinct():
    schema = json.loads((SCHEMA_ROOT / "run_manifest.json").read_text())
    assert "REPORTED" not in schema["$defs"]["stage_status"]["enum"]
    assert "REPORTED" in schema["$defs"]["run_status"]["enum"]
    assert schema["properties"]["status"] == {"$ref": "#/$defs/run_status"}
    assert schema["$defs"]["attempt"]["properties"]["stage_status"] == {"$ref": "#/$defs/stage_status"}
    assert schema["$defs"]["transition"]["properties"]["from_status"] == {"$ref": "#/$defs/stage_status"}
    assert schema["$defs"]["transition"]["properties"]["to_status"] == {"$ref": "#/$defs/stage_status"}

def test_runtime_ledger_egress_blocked_schema_carries_zero_byte_sentinel_evidence():
    schema = json.loads((SCHEMA_ROOT / "runtime_and_failure_ledger.json").read_text())
    event = schema["$defs"]["event"]
    assert {"policy_decision_id", "tool_identity", "destination", "protocol",
            "attempted_bytes", "transmitted_bytes", "payload"} <= set(event["properties"])
    assert event["properties"]["protocol"]["enum"] == ["DNS", "HTTP_PROXY", "PROVIDER", "LOOPBACK"]
    conditional = next(item for item in event["allOf"] if "if" in item)
    assert conditional["if"]["properties"]["event_type"]["const"] == "EGRESS_BLOCKED"
    required = set(conditional["then"]["required"])
    assert {"policy_decision_id", "tool_identity", "destination", "protocol",
            "attempted_bytes", "transmitted_bytes", "payload"} <= required
    assert conditional["then"]["properties"]["transmitted_bytes"] == {"const": 0}
    assert conditional["then"]["properties"]["payload"] == {"type": "null"}

def test_runtime_ledger_membership_is_artifact_id_set():
    schema = json.loads((SCHEMA_ROOT / "runtime_and_failure_ledger.json").read_text())
    assert schema["$defs"]["event"]["properties"]["affected_refs"]["items"] == {"$ref": "#/$defs/id"}


def _schema_payload_required(schema):
    """Resolve the per-record payload required set of a closed artifact schema."""
    definitions = schema.get("$defs", {})
    payload = definitions.get("payload")
    if isinstance(payload, dict) and "required" in payload:
        return set(payload["required"])
    record = definitions.get("record")
    if isinstance(record, dict):
        return set(record["properties"]["payload"]["required"])
    event = definitions.get("event")
    if isinstance(event, dict) and "required" in event:
        return set(event["required"])
    metric = definitions.get("metric")
    if isinstance(metric, dict) and "required" in metric:
        return set(metric["required"])
    if "payload" in schema.get("properties", {}):
        return set(schema["properties"]["payload"]["required"])
    # The run manifest's payload *is* the whole document.
    return set(schema["required"])


def test_registry_required_payload_fields_match_the_closed_schemas():
    """Guard against the stale-registry defect: inventory mirrors the schemas."""
    registry = json.loads((SCHEMA_ROOT / "registry.json").read_text())
    assert set(registry["required_payload_fields"]) == set(ARTIFACT_FILENAMES)
    for artifact in ARTIFACT_FILENAMES:
        stored = set(registry["required_payload_fields"][artifact])
        if artifact == "gate_decision.md":
            assert stored == GATE_DECISION_PAYLOAD, artifact
            continue
        schema = json.loads((SCHEMA_ROOT / registry["schemas"][artifact]).read_text())
        if artifact == "window_sample_manifest.jsonl":
            # Gate-0 sample rows are the sample_target variant of the closed
            # oneOf payload (the typed_interval variant is not produced here).
            expected = set(schema["$defs"]["sample_target_payload"]["required"])
        else:
            expected = _schema_payload_required(schema)
        assert stored == expected, artifact
    # D8 conditional: representation_id is schema-optional for ranked candidates
    # and therefore must not be listed as a required payload field.
    assert "representation_id" not in registry["required_payload_fields"]["ranked_candidates.jsonl"]
    assert set(registry["required_payload_fields"]["ranked_candidates.jsonl"]) == {
        "candidate_id", "query_id", "arm_id", "window_id", "score_status",
        "coverage_status", "gold_accessed",
    }


def test_run_manifest_registry_inventory_is_the_frozen_eighteen_key_set():
    registry = json.loads((SCHEMA_ROOT / "registry.json").read_text())
    schema = json.loads((SCHEMA_ROOT / "run_manifest.json").read_text())
    assert set(registry["required_payload_fields"]["run_manifest.json"]) == set(schema["required"])
    assert len(schema["required"]) == 18


# ---------------------------------------------------------------------------
# D8 cross-artifact validation (semantic identity closure)
# ---------------------------------------------------------------------------

def _fixture_candidate():
    candidate = {}
    for name in ARTIFACT_FILENAMES:
        path = SEMANTIC_CLOSURE_FIXTURE / name
        if name.endswith(".jsonl"):
            candidate[name] = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        elif name.endswith(".md"):
            candidate[name] = path.read_text()
        else:
            candidate[name] = json.loads(path.read_text())
    return candidate


def _run_manifest(candidate):
    return candidate["run_manifest.json"]


def _ranked_records(candidate):
    return candidate["ranked_candidates.jsonl"]


def _ranked(candidate):
    return [record["payload"] for record in _ranked_records(candidate)]


def _envelope(candidate, artifact):
    return next(item for item in _run_manifest(candidate)["artifact_envelopes"]
                if item["artifact_type"] == artifact)


def test_complete_semantic_closure_fixture_passes_cross_artifact_validation():
    candidate = _fixture_candidate()
    assert validate_artifact_set(candidate) is True
    # The two-arm registry is the closed per-run arm surface.
    assert _run_manifest(candidate)["arms"] == [
        {"arm_id": "metadata-floor", "representation_kind": "metadata_floor"},
        {"arm_id": "offline-development-arm", "representation_kind": "embedding"},
    ]


def test_metadata_candidate_carrying_representation_id_fails():
    candidate = _fixture_candidate()
    _ranked(candidate)[0]["arm_id"] = "metadata-floor"
    with pytest.raises(ContractError, match="metadata"):
        validate_artifact_set(candidate)


def test_metadata_candidate_without_representation_identity_passes():
    candidate = _fixture_candidate()
    # The registry always declares both D03 arms, so keep an embedding row too;
    # per-kind presence (F3) would otherwise reject a metadata-only ranking.
    embedding = json.loads(json.dumps(_ranked_records(candidate)[0]))
    embedding["record_id"] = "record_embedding_keep"
    embedding["payload"]["candidate_id"] = "candidate_embedding_keep"
    _ranked_records(candidate).append(embedding)
    payload = _ranked(candidate)[0]
    payload["arm_id"] = "metadata-floor"
    payload.pop("representation_id")
    assert validate_artifact_set(candidate) is True


def test_embedding_candidate_without_representation_id_fails():
    candidate = _fixture_candidate()
    _ranked(candidate)[0].pop("representation_id")
    with pytest.raises(ContractError, match="representation"):
        validate_artifact_set(candidate)


def test_unknown_representation_id_fails():
    candidate = _fixture_candidate()
    _ranked(candidate)[0]["representation_id"] = "representation_unknown"
    with pytest.raises(ContractError, match="representation"):
        validate_artifact_set(candidate)


def test_representation_window_mismatch_fails():
    candidate = _fixture_candidate()
    _run_manifest(candidate)["representations"][0]["window_id"] = "window_other"
    with pytest.raises(ContractError, match="window"):
        validate_artifact_set(candidate)


def test_unknown_arm_id_fails():
    candidate = _fixture_candidate()
    _ranked(candidate)[0]["arm_id"] = "undeclared-arm"
    with pytest.raises(ContractError, match="arm"):
        validate_artifact_set(candidate)


def test_missing_arm_registry_with_ranked_rows_fails():
    candidate = _fixture_candidate()
    _run_manifest(candidate).pop("arms")
    with pytest.raises(ContractError, match="arm"):
        validate_artifact_set(candidate)


def test_duplicate_arm_registry_entry_fails():
    candidate = _fixture_candidate()
    _run_manifest(candidate)["arms"].append(
        {"arm_id": "metadata-floor", "representation_kind": "embedding"})
    with pytest.raises(ContractError, match="duplicate arm"):
        validate_artifact_set(candidate)


def test_unknown_representation_kind_fails():
    candidate = _fixture_candidate()
    _run_manifest(candidate)["arms"][0]["representation_kind"] = "model"
    with pytest.raises(ContractError, match="representation kind"):
        validate_artifact_set(candidate)


def test_registry_must_declare_exactly_the_frozen_two_arm_set():
    """One local embedding arm + one transparent metadata baseline, always both."""
    candidate = _fixture_candidate()
    _run_manifest(candidate)["arms"] = [
        {"arm_id": "metadata-floor", "representation_kind": "metadata_floor"}]
    with pytest.raises(ContractError, match="exactly the frozen two-arm set"):
        validate_artifact_set(candidate)

    candidate = _fixture_candidate()
    _run_manifest(candidate)["arms"] = [
        {"arm_id": "offline-development-arm", "representation_kind": "embedding"},
        {"arm_id": "second-embedding-arm", "representation_kind": "embedding"}]
    with pytest.raises(ContractError, match="exactly the frozen two-arm set"):
        validate_artifact_set(candidate)


def test_ranked_embedding_candidate_representation_must_be_succeeded():
    candidate = _fixture_candidate()
    _run_manifest(candidate)["representations"][0]["representation_status"] = "FAILED"
    with pytest.raises(ContractError, match="SUCCEEDED"):
        validate_artifact_set(candidate)


def test_ranked_status_row_may_join_a_failed_representation():
    """Spec §5: failed vectors remain status rows, not primary rankings."""
    candidate = _fixture_candidate()
    _run_manifest(candidate)["representations"][0]["representation_status"] = "FAILED"
    row = _ranked(candidate)[0]
    row.update({"score": None, "rank": None, "score_status": "FAILED",
                "coverage_status": "FAILED"})
    validate_artifact_set(candidate)


def test_finite_ranked_row_still_requires_a_succeeded_representation():
    candidate = _fixture_candidate()
    _run_manifest(candidate)["representations"][0]["representation_status"] = "FAILED"
    with pytest.raises(ContractError,
                       match="ranked candidate representation is not SUCCEEDED"):
        validate_artifact_set(candidate)


def test_window_judgment_with_undeclared_arm_fails():
    candidate = _fixture_candidate()
    candidate["window_judgments.jsonl"][0]["arm_id"] = "undeclared-arm"
    with pytest.raises(ContractError, match="arm"):
        validate_artifact_set(candidate)


def test_duplicate_ranked_candidate_id_fails():
    candidate = _fixture_candidate()
    duplicate = json.loads(json.dumps(_ranked_records(candidate)[0]))
    duplicate["record_id"] = "record_duplicate"
    _ranked_records(candidate).append(duplicate)
    with pytest.raises(ContractError, match="duplicate ranked candidate"):
        validate_artifact_set(candidate)


def test_representation_sampling_manifest_digest_mismatch_fails():
    candidate = _fixture_candidate()
    _run_manifest(candidate)["representations"][0]["sampling_manifest_digest"] = "0" * 64
    with pytest.raises(ContractError, match="sampling manifest digest"):
        validate_artifact_set(candidate)


def test_duplicate_representation_id_fails():
    candidate = _fixture_candidate()
    duplicate = json.loads(json.dumps(_run_manifest(candidate)["representations"][0]))
    _run_manifest(candidate)["representations"].append(duplicate)
    with pytest.raises(ContractError, match="duplicate representation"):
        validate_artifact_set(candidate)


def test_tombstoned_artifact_consumption_via_envelope_refs_fails():
    candidate = _fixture_candidate()
    tombstoned = _envelope(candidate, "gate_decision.md")
    _envelope(candidate, "ranked_candidates.jsonl")["input_artifact_refs"].append({
        "artifact_id": tombstoned["artifact_id"],
        "payload_digest": tombstoned["payload_digest"],
        "artifact_type": "gate_decision.md",
    })
    with pytest.raises(ContractError, match="tombstoned"):
        validate_artifact_set(candidate)
