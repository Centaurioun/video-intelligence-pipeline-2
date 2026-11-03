import pytest

from gate1.artifacts import (
    ArtifactError,
    ARTIFACT_FILENAMES,
    embedding_record_from_payload,
    embedding_record_payload,
    frozen_protocol_digest,
    load_artifact_root,
    write_artifact_root,
)
from gate1.contracts.types import BenchmarkEnvelope, EmbeddingPayload, EmbeddingRecord


def root_payload():
    return {
        name: ([{"record_id": "a"}] if name.endswith(".jsonl") else {})
        for name in ARTIFACT_FILENAMES
    }


def test_embedding_record_round_trips_all_current_d01_envelope_fields():
    record = EmbeddingRecord(
        envelope=BenchmarkEnvelope(
            record_id="r1", comparison_id="cmp1", run_id="run1", attempt_id="a1",
            arm_id="arm1", input_refs=("input1",), consumed_coverage={"consumed": 1},
            raw_response_artifact_ref=None, absence_reason=None, requested_model="local",
            resolved_backend="NOT_OBSERVED", config_digest="a" * 64,
            policy_decision_id="policy1", request_ref="request1",
            judgment_version_refs=("judgment-v1",),
            resource_observations={"cpu_time_ms": "NOT_OBSERVED"},
            validity_ref="validity1", outcome_ref="outcome1", provider_status="SUCCESS",
            per_item_errors=(), wall_time_ms=12.5,
        ),
        payload=EmbeddingPayload(
            space_id="space1", representation_id="repr1", query_id="q1",
            candidate_id=None, kind="query", vector=(0.25, 0.75), failure_reason=None,
        ),
    )

    payload = embedding_record_payload(record)
    assert payload["envelope"]["request_ref"] == "request1"
    assert payload["envelope"]["judgment_version_refs"] == ["judgment-v1"]
    assert payload["envelope"]["resource_observations"] == {"cpu_time_ms": "NOT_OBSERVED"}
    assert payload["envelope"]["validity_ref"] == "validity1"
    assert payload["envelope"]["outcome_ref"] == "outcome1"
    assert embedding_record_from_payload(payload) == record


def test_writer_emits_canonical_json_and_jsonl_with_exact_ten_file_closure(tmp_path):
    write_artifact_root(tmp_path, root_payload())
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(ARTIFACT_FILENAMES)
    assert (tmp_path / "comparison_contract.json").read_bytes() == b"{}\n"
    assert (tmp_path / "capability_descriptors.jsonl").read_bytes() == b'{"record_id":"a"}\n'
    assert load_artifact_root(tmp_path) == root_payload()


def test_loader_rejects_noncanonical_or_unsorted_jsonl(tmp_path):
    write_artifact_root(tmp_path, root_payload())
    (tmp_path / "capability_descriptors.jsonl").write_text(
        '{"record_id":"z"}\n{"record_id":"a"}\n', encoding="utf-8"
    )
    with pytest.raises(ArtifactError, match="canonical|ordered"):
        load_artifact_root(tmp_path)


def test_writer_refuses_missing_or_extra_artifacts(tmp_path):
    payload = root_payload()
    payload.pop("synthetic_receipt.json")
    with pytest.raises(ArtifactError, match="exactly"):
        write_artifact_root(tmp_path, payload)
    payload = root_payload()
    payload["unexpected.json"] = {}
    with pytest.raises(ArtifactError, match="exactly"):
        write_artifact_root(tmp_path, payload)


def test_loader_refuses_hidden_and_directory_entries(tmp_path):
    write_artifact_root(tmp_path, root_payload())
    (tmp_path / ".hidden").write_text("", encoding="utf-8")
    with pytest.raises(ArtifactError, match="closure"):
        load_artifact_root(tmp_path)


def test_frozen_protocol_binds_current_d01_ranking_input_declarations():
    contract = {"tie_rule": "candidate_id", "retry_policy": "none", "resource_budget": {}}
    run = {
        "source_partitions": {"development": ["d"], "evaluation": ["e"]},
        "candidate_production_inputs": [
            {"kind": "query", "input_id": "q1"},
            {"kind": "candidate", "input_id": "c1"},
        ],
        "synthetic_fault": "NONE",
    }
    original = frozen_protocol_digest(contract, [], [], run)
    mutated = {**run, "candidate_production_inputs": [*run["candidate_production_inputs"],
                                                        {"kind": "query", "input_id": "q2"}]}
    assert original != frozen_protocol_digest(contract, [], [], mutated)


def test_real_mode_refuses_before_attempting_artifact_or_historical_authority_validation():
    from gate1.verify import VerificationError, verify_artifact_set

    with pytest.raises(VerificationError, match="REAL.*refused"):
        verify_artifact_set({}, mode="REAL")


def _valid_synthetic_candidate():
    from gate1.artifacts import contract_digest, descriptor_digest, frozen_protocol_digest, policy_digest

    arms = ["a", "b"]
    contract = {
        "comparison_id": "cmp-1", "execution_mode": "SYNTHETIC", "question": "synthetic check",
        "estimand": "synthetic", "changed_axis": "space_id",
        "pinned_controls": {"operation": "embedding", "input_mode": "sampled_frames",
                            "window_profile_digest": "b" * 64, "metric": "cosine",
                            "normalization": "l2", "provider_family": "synthetic"},
        "arm_ids": arms, "operation": "embedding", "primary_metric": {"metric_id": "hit@1", "k": 1,
        "min_delta": 0.1, "require_complete_coverage": True}, "decision_rule": {"comparison": "difference"},
        "validity_rules": {"require_complete_coverage": True}, "dependency_refs": {"gate0_terminal_sha": None},
        "policy_eligibility": {"a": "p", "b": "p"}, "tie_rule": "(-score,candidate_id_utf8)",
        "retry_policy": "none", "resource_budget": {"max_attempts": 1}, "owner_approval_ref": "synthetic",
    }
    descriptors = [{"record_id": f"d-{arm}", "arm_id": arm, "capability_revision": "fixture-v1",
        "provider_family": "synthetic", "operation": "embedding", "input_mode": "sampled_frames",
        "requested_model": "fake", "resolved_backend": "NOT_OBSERVED", "runtime_revision": "NOT_OBSERVED",
        "config_digest": "c" * 64, "space_id": f"space-{arm}", "policy_decision_id": "p",
        "window_profile_digest": "b" * 64, "metric": "cosine", "normalization": "l2"} for arm in arms]
    policies = [{"record_id": "p-row", "policy_decision_id": "p", "decision": "ALLOW",
                 "processing_boundary": "SYNTHETIC_TEST_ONLY"}]
    inputs = ([{"kind": "query", "input_id": "q"}, {"kind": "candidate", "input_id": "c"}] +
              [{"kind": "representation", "input_id": f"repr-{arm}-{kind}", "arm_id": arm,
                "space_id": f"space-{arm}"} for arm in arms for kind in ("query", "candidate")])
    manifest = {"schema_version": "gate1.run.v1", "run_id": "", "comparison_id": "cmp-1",
        "execution_mode": "SYNTHETIC", "spec_sha": "1" * 40, "execution_authority_sha": "2" * 40,
        "canonical_contract_blob": "3" * 40, "source_partitions": {"development": ["dev-1"], "evaluation": ["eval-1"]},
        "candidate_production_inputs": inputs, "provenance": {"run_id": "", "attempt_id": "attempt-1", "config_digest": "c" * 64},
        "backend_observation": "NOT_OBSERVED", "contract_digest": contract_digest(contract),
        "descriptor_digest": descriptor_digest(descriptors), "policy_digest": policy_digest(policies),
        "frozen_protocol_digest": "0" * 64, "synthetic_fault": "NONE", "status": "NOT_RUN"}
    manifest["frozen_protocol_digest"] = frozen_protocol_digest(contract, descriptors, policies, manifest)
    manifest["run_id"] = "syn-" + manifest["frozen_protocol_digest"][:16]
    manifest["provenance"]["run_id"] = manifest["run_id"]
    embeddings = []
    rankings = []
    for arm in arms:
        for kind, ident, vector in (("query", "q", [1.0, 0.0]), ("candidate", "c", [1.0, 0.0])):
            repr_id = f"repr-{arm}-{kind}"
            embeddings.append({"envelope": {"record_id": f"env-{arm}-{kind}", "comparison_id": "cmp-1",
                "run_id": manifest["run_id"], "attempt_id": "attempt-1", "arm_id": arm,
                "input_refs": [repr_id], "consumed_coverage": {"expected": 1, "consumed": 1},
                "raw_response_artifact_ref": None, "absence_reason": "SYNTHETIC_INLINE_VECTOR", "requested_model": "fake",
                "resolved_backend": "NOT_OBSERVED", "config_digest": "c" * 64, "policy_decision_id": "p",
                "request_ref": None, "judgment_version_refs": [], "resource_observations": {},
                "validity_ref": None, "outcome_ref": None, "provider_status": "SUCCESS", "per_item_errors": [],
                "wall_time_ms": None}, "payload": {"space_id": f"space-{arm}", "representation_id": repr_id,
                "query_id": ident if kind == "query" else None, "candidate_id": ident if kind == "candidate" else None,
                "kind": kind, "vector": vector, "failure_reason": None}})
        rankings.append({"record_id": f"rank-{arm}-q-c", "arm_id": arm, "query_id": "q", "candidate_id": "c",
            "representation_id": f"repr-{arm}-candidate", "space_id": f"space-{arm}", "score": 1.0, "rank": 1,
            "tie_key": [-1.0, "c"], "coverage_status": "SELECTED"})
    embeddings.sort(key=lambda row: row["envelope"]["record_id"])
    judgments = [{"record_id": "j-1", "query_id": "q", "candidate_id": "c", "relevant": True,
        "reviewer_id": "synthetic-reviewer", "synthetic": True, "evidence_class": "MATCHED"}]
    return {"comparison_contract.json": contract, "capability_descriptors.jsonl": descriptors,
        "policy_decisions.jsonl": policies, "run_manifest.json": manifest,
        "embedding_results.jsonl": embeddings, "ranked_candidates.jsonl": rankings, "judgments.jsonl": judgments,
        "failure_ledger.json": {"record_id": "f-1", "run_id": manifest["run_id"], "comparison_id": "cmp-1",
            "event_type": "NONE", "attempt_id": "attempt-1", "affected_refs": [], "reason": "NONE",
            "occurred_at": "SYNTHETIC_FIXED"},
        "benchmark_report.json": {"comparison_id": "cmp-1", "validity": "VALID", "benchmark_status": "FAIL",
            "primary_metric_id": "hit@1", "primary_value": 0.0, "arm_values": {"a": 1.0, "b": 1.0}, "coverage": {"a": 1, "b": 1},
            "failure_class": "QUALITY", "conclusion": "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"},
        "synthetic_receipt.json": {"spec_sha": "1" * 40, "execution_authority_sha": "2" * 40,
            "canonical_contract_blob": "3" * 40, "execution_mode": "SYNTHETIC", "real_benchmark_executed": False,
            "provider_calls": 0, "network_egress_bytes": 0, "protected_media_used": False,
            "model_download_or_change": False, "winner_observed": False, "real_model_provider_claims": "NOT_OBSERVED",
            "gate0_terminal_sha": None, "gate_promotion": False}}


def test_current_synthetic_candidate_passes_independent_verifier():
    from gate1.verify import verify_artifact_set

    verify_artifact_set(_valid_synthetic_candidate(), mode="SYNTHETIC")


def test_synthetic_report_recomputes_query_macro_metric_from_judgments():
    from gate1.verify import _independent_report

    candidate = _valid_synthetic_candidate()
    report = _independent_report(candidate)
    assert report["benchmark_status"] == "FAIL"
    assert report["primary_value"] == 0.0
    assert report["arm_values"] == {"a": 1.0, "b": 1.0}
    candidate["judgments.jsonl"][0]["relevant"] = False
    changed = _independent_report(candidate)
    assert changed["arm_values"] == {"a": 0.0, "b": 0.0}
    from gate1.verify import VerificationError, verify_artifact_set
    with pytest.raises(VerificationError, match="report"):
        verify_artifact_set(candidate, mode="SYNTHETIC")


def test_forged_report_metric_and_coverage_are_rejected():
    from gate1.verify import VerificationError, verify_artifact_set

    candidate = _valid_synthetic_candidate()
    candidate["benchmark_report.json"]["arm_values"] = {"a": 0.0, "b": 1.0}
    with pytest.raises(VerificationError, match="report"):
        verify_artifact_set(candidate, mode="SYNTHETIC")
    candidate = _valid_synthetic_candidate()
    candidate["benchmark_report.json"]["coverage"]["a"] = 99
    with pytest.raises(VerificationError, match="report"):
        verify_artifact_set(candidate, mode="SYNTHETIC")


def test_failed_and_omitted_query_rows_remain_in_macro_denominator():
    from gate1.verify import _independent_report

    candidate = _valid_synthetic_candidate()
    for arm in ("a", "b"):
        candidate["ranked_candidates.jsonl"].append({
            "record_id": f"rank-{arm}-q2-c", "arm_id": arm, "query_id": "q2",
            "candidate_id": "c", "representation_id": f"repr-{arm}-candidate",
            "space_id": f"space-{arm}", "score": None, "rank": None,
            "tie_key": None, "coverage_status": "OMITTED",
        })
    report = _independent_report(candidate)
    assert report["arm_values"] == {"a": 0.5, "b": 0.5}
    assert report["coverage"] == {"a": 1, "b": 1}
    assert report["benchmark_status"] == "FAIL"
    assert report["failure_class"] == "COVERAGE_INCOMPLETE"


def _candidate_with_null_vector(*, failure_reason=None, provider_status="SUCCESS", per_item_errors=()):
    candidate = _valid_synthetic_candidate()
    for row in candidate["embedding_results.jsonl"]:
        if row["payload"]["kind"] == "candidate":
            row["payload"]["vector"] = None
            row["payload"]["failure_reason"] = failure_reason
            failed = bool(failure_reason) or provider_status in {"FAILED", "PARTIAL"} or bool(per_item_errors)
            row["envelope"]["consumed_coverage"] = {"expected": 1, "consumed": 0, "omitted": int(not failed), "failed": int(failed)}
            row["envelope"]["provider_status"] = provider_status
            row["envelope"]["per_item_errors"] = list(per_item_errors)
    return candidate


def test_null_vector_without_failure_evidence_is_independently_omitted():
    from gate1.verify import _independent_rankings

    rows = _independent_rankings(_candidate_with_null_vector())
    assert [row["coverage_status"] for row in rows if row["candidate_id"] == "c"] == ["OMITTED", "OMITTED"]


@pytest.mark.parametrize("evidence", ["failure_reason", "provider_failed", "provider_partial", "item_error"])
def test_each_attributable_failure_evidence_makes_null_vector_failed(evidence):
    from gate1.verify import _independent_rankings

    kwargs = {
        "failure_reason": "synthetic failure" if evidence == "failure_reason" else None,
        "provider_status": {"provider_failed": "FAILED", "provider_partial": "PARTIAL"}.get(evidence, "SUCCESS"),
        "per_item_errors": ("item failed",) if evidence == "item_error" else (),
    }
    rows = _independent_rankings(_candidate_with_null_vector(**kwargs))
    assert [row["coverage_status"] for row in rows if row["candidate_id"] == "c"] == ["FAILED", "FAILED"]


@pytest.mark.parametrize("forged_status,evidence", [
    ("FAILED", {}),
    ("OMITTED", {"failure_reason": "synthetic failure"}),
])
def test_verifier_rejects_forged_omitted_failed_classification(forged_status, evidence):
    from gate1.verify import VerificationError, _independent_rankings, _independent_report, verify_artifact_set

    candidate = _candidate_with_null_vector(**evidence)
    expected = _independent_rankings(candidate)
    for row in expected:
        if row["candidate_id"] == "c":
            row["coverage_status"] = forged_status
    candidate["ranked_candidates.jsonl"] = expected
    candidate["benchmark_report.json"] = _independent_report(candidate)
    with pytest.raises(VerificationError, match="ranking"):
        verify_artifact_set(candidate, mode="SYNTHETIC")
def test_dangling_resource_failure_reference_is_rejected_without_name_error():
    from gate1.verify import VerificationError, verify_artifact_set

    candidate = _valid_synthetic_candidate()
    manifest = candidate["run_manifest.json"]
    contract = candidate["comparison_contract.json"]
    descriptors = candidate["capability_descriptors.jsonl"]
    policies = candidate["policy_decisions.jsonl"]
    manifest["synthetic_fault"] = "RESOURCE_OPERABILITY"
    manifest["frozen_protocol_digest"] = frozen_protocol_digest(contract, descriptors, policies, manifest)
    from gate1.artifacts import derived_run_id
    manifest["run_id"] = derived_run_id(manifest["frozen_protocol_digest"])
    manifest["provenance"]["run_id"] = manifest["run_id"]
    for row in candidate["embedding_results.jsonl"]:
        row["envelope"]["run_id"] = manifest["run_id"]
    ledger = candidate["failure_ledger.json"]
    ledger.update(run_id=manifest["run_id"], event_type="RESOURCE_OPERABILITY", affected_refs=["missing-env"])
    from gate1.verify import _independent_report
    candidate["benchmark_report.json"] = _independent_report(candidate)
    with pytest.raises(VerificationError, match="failure ledger affected record references"):
        verify_artifact_set(candidate, mode="SYNTHETIC")


def test_valid_resource_failure_reference_is_accepted():
    from gate1.artifacts import derived_run_id
    from gate1.verify import _independent_report, verify_artifact_set

    candidate = _valid_synthetic_candidate()
    manifest = candidate["run_manifest.json"]
    manifest["synthetic_fault"] = "RESOURCE_OPERABILITY"
    manifest["frozen_protocol_digest"] = frozen_protocol_digest(
        candidate["comparison_contract.json"], candidate["capability_descriptors.jsonl"],
        candidate["policy_decisions.jsonl"], manifest,
    )
    manifest["run_id"] = derived_run_id(manifest["frozen_protocol_digest"])
    manifest["provenance"]["run_id"] = manifest["run_id"]
    for row in candidate["embedding_results.jsonl"]:
        row["envelope"]["run_id"] = manifest["run_id"]
    env_id = candidate["embedding_results.jsonl"][0]["envelope"]["record_id"]
    candidate["failure_ledger.json"].update(run_id=manifest["run_id"], event_type="RESOURCE_OPERABILITY",
                                             affected_refs=[env_id])
    candidate["benchmark_report.json"] = _independent_report(candidate)
    verify_artifact_set(candidate, mode="SYNTHETIC")


def test_registered_json_schema_constraints_are_enforced_fail_closed():
    import json
    from pathlib import Path

    from gate1.verify import VerificationError, _schema_instance

    schemas = Path(__file__).resolve().parents[3] / "schemas" / "gate1"
    contract_schema = json.loads((schemas / "comparison_contract.json").read_text())
    with pytest.raises(VerificationError):
        _schema_instance(contract_schema, {**_valid_synthetic_candidate()["comparison_contract.json"],
                                           "validity_rules": {"max_failure_rate": 1.5}}, "contract")
    with pytest.raises(VerificationError):
        _schema_instance({"oneOf": [{"type": "string"}, {"type": "string", "minLength": 1}]}, "x", "value")
    with pytest.raises(VerificationError):
        _schema_instance({"anyOf": [{"type": "integer"}, {"const": "NOT_OBSERVED"}]}, False, "value")
    with pytest.raises(VerificationError):
        _schema_instance({"type": "string", "format": "date-time"}, "yesterday", "value")
    with pytest.raises(VerificationError, match="unsupported format"):
        _schema_instance({"type": "string", "format": "ipv6"}, "::1", "value")
    with pytest.raises(VerificationError):
        _schema_instance({"type": "object", "minProperties": 1}, {}, "value")


def _mark_protocol_invalid(candidate):
    from gate1.artifacts import contract_digest, derived_run_id
    from gate1.verify import _independent_report

    contract = candidate["comparison_contract.json"]
    manifest = candidate["run_manifest.json"]
    contract["changed_axis"] = "capability_revision"  # equal across arms: a protocol-comparability failure
    manifest["contract_digest"] = contract_digest(contract)
    manifest["status"] = "INVALID_PROTOCOL"
    manifest["frozen_protocol_digest"] = frozen_protocol_digest(
        contract, candidate["capability_descriptors.jsonl"], candidate["policy_decisions.jsonl"], manifest)
    manifest["run_id"] = derived_run_id(manifest["frozen_protocol_digest"])
    manifest["provenance"]["run_id"] = manifest["run_id"]
    for row in candidate["embedding_results.jsonl"]:
        row["envelope"]["run_id"] = manifest["run_id"]
    candidate["failure_ledger.json"]["run_id"] = manifest["run_id"]
    candidate["benchmark_report.json"] = _independent_report(candidate)
    return candidate


def _reseal_candidate(candidate):
    from gate1.artifacts import derived_run_id, policy_digest
    from gate1.verify import _independent_report

    manifest = candidate["run_manifest.json"]
    manifest["policy_digest"] = policy_digest(candidate["policy_decisions.jsonl"])
    manifest["frozen_protocol_digest"] = frozen_protocol_digest(
        candidate["comparison_contract.json"], candidate["capability_descriptors.jsonl"],
        candidate["policy_decisions.jsonl"], manifest)
    manifest["run_id"] = derived_run_id(manifest["frozen_protocol_digest"])
    manifest["provenance"]["run_id"] = manifest["run_id"]
    for row in candidate["embedding_results.jsonl"]:
        row["envelope"]["run_id"] = manifest["run_id"]
    candidate["failure_ledger.json"]["run_id"] = manifest["run_id"]
    candidate["benchmark_report.json"] = _independent_report(candidate)
    return candidate


def test_protocol_invalid_synthetic_artifacts_verify_only_as_no_outcome():
    from gate1.verify import VerificationError, verify_artifact_set

    candidate = _mark_protocol_invalid(_valid_synthetic_candidate())
    verify_artifact_set(candidate, mode="SYNTHETIC")
    assert candidate["benchmark_report.json"]["validity"] == "INVALID_PROTOCOL"
    assert candidate["benchmark_report.json"]["benchmark_status"] == "INVALID_PROTOCOL"
    assert candidate["benchmark_report.json"]["primary_value"] is None
    assert candidate["benchmark_report.json"]["conclusion"] == "COMPARISON_INVALID_NO_OUTCOME_CLAIM"

    candidate["benchmark_report.json"]["primary_value"] = 0.0
    with pytest.raises(VerificationError, match="report"):
        verify_artifact_set(candidate, mode="SYNTHETIC")


def test_protocol_invalid_artifacts_do_not_bypass_policy_or_status_checks():
    from gate1.verify import VerificationError, verify_artifact_set

    candidate = _mark_protocol_invalid(_valid_synthetic_candidate())
    candidate["policy_decisions.jsonl"][0]["decision"] = "DENY"
    _reseal_candidate(candidate)
    with pytest.raises(VerificationError, match="D01 contract rejected"):
        verify_artifact_set(candidate, mode="SYNTHETIC")


def test_rank_score_forgery_is_rejected_even_with_other_artifacts_unchanged():
    from gate1.verify import VerificationError, verify_artifact_set

    candidate = _valid_synthetic_candidate()
    candidate["ranked_candidates.jsonl"][0]["score"] = 0.25
    with pytest.raises(VerificationError, match="ranking"):
        verify_artifact_set(candidate, mode="SYNTHETIC")


def test_synthetic_report_cannot_claim_generated_outcome_or_winner():
    from gate1.verify import VerificationError, verify_artifact_set

    candidate = _valid_synthetic_candidate()
    candidate["benchmark_report.json"]["benchmark_status"] = "PASS"
    with pytest.raises(VerificationError, match="report"):
        verify_artifact_set(candidate, mode="SYNTHETIC")


@pytest.mark.parametrize("mutate", [
    lambda row: row["envelope"].update(input_refs=["dangling-reference"]),
    lambda row: row["envelope"].update(input_refs=["repr-a-candidate"]),
    lambda row: row["payload"].update(space_id="space-b"),
])
def test_embedding_input_refs_must_resolve_to_matching_retained_representation(mutate):
    from gate1.verify import VerificationError, verify_artifact_set

    candidate = _valid_synthetic_candidate()
    row = next(row for row in candidate["embedding_results.jsonl"]
               if row["envelope"]["arm_id"] == "a" and row["payload"]["kind"] == "query")
    mutate(row)
    with pytest.raises(VerificationError, match="input reference|representation|space"):
        verify_artifact_set(candidate, mode="SYNTHETIC")


@pytest.mark.parametrize("coverage", [
    {"expected": 2, "consumed": 1},
    {"expected": 1, "consumed": 0},
    {"expected": 1, "consumed": 2},
])
def test_embedding_consumed_coverage_must_match_single_retained_input(coverage):
    from gate1.verify import VerificationError, verify_artifact_set

    candidate = _valid_synthetic_candidate()
    candidate["embedding_results.jsonl"][0]["envelope"]["consumed_coverage"] = coverage
    with pytest.raises(VerificationError, match="consumed coverage"):
        verify_artifact_set(candidate, mode="SYNTHETIC")
