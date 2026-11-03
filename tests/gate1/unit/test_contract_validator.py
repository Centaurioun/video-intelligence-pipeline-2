from types import SimpleNamespace

import pytest

from gate1.contracts.validator import ContractError, validate_comparison


def fixture(mode="SYNTHETIC"):
    contract = SimpleNamespace(
        comparison_id="cmp-1", execution_mode=mode, question="Does representation improve retrieval?",
        estimand="paired recall difference", changed_axis="space_id",
        pinned_controls={"operation": "embedding", "input_mode": "text", "window_profile_digest": "w" * 64,
                         "metric": "cosine", "normalization": "l2", "provider_family": "local"},
        arm_ids=("a", "b"), operation="embedding", policy_eligibility={"a": "p-a", "b": "p-b"},
    )
    descriptors = [
        SimpleNamespace(record_id="d-a", arm_id="a", capability_revision="cap-v1", provider_family="local", operation="embedding",
                        input_mode="text", requested_model="mock", resolved_backend="NOT_OBSERVED",
                        runtime_revision="NOT_OBSERVED", config_digest="a" * 64, space_id="space-a",
                        policy_decision_id="p-a", window_profile_digest="w" * 64, metric="cosine",
                        normalization="l2"),
        SimpleNamespace(record_id="d-b", arm_id="b", capability_revision="cap-v1", provider_family="local", operation="embedding",
                        input_mode="text", requested_model="mock", resolved_backend="NOT_OBSERVED",
                        runtime_revision="NOT_OBSERVED", config_digest="a" * 64, space_id="space-b",
                        policy_decision_id="p-b", window_profile_digest="w" * 64, metric="cosine",
                        normalization="l2"),
    ]
    policies = [SimpleNamespace(policy_decision_id=f"p-{x}", decision="ALLOW") for x in "ab"]
    run = {
        "execution_mode": mode,
        "source_partitions": {"development": ["src-1"], "evaluation": ["src-2"]},
        "candidate_production_inputs": [
            {"kind": "representation", "input_id": "rep-a", "arm_id": "a", "space_id": "space-a"},
            {"kind": "representation", "input_id": "rep-b", "arm_id": "b", "space_id": "space-b"},
        ],
        "backend_observation": "NOT_OBSERVED",
        "provenance": {"run_id": "run-1", "attempt_id": "attempt-1", "config_digest": "c" * 64},
    }
    return contract, descriptors, policies, run


def test_valid_synthetic_one_axis_comparison_is_admitted():
    validate_comparison(*fixture())


@pytest.mark.parametrize("mutation", ["compound", "missing-control", "duplicate-arm", "overlap", "label-leak",
                                        "denied", "expired", "revoked", "backend-claim", "malformed-provenance"])
def test_invalid_comparisons_fail_closed(mutation):
    c, ds, ps, run = fixture()
    if mutation == "compound":
        ds[1].provider_family = "other"
    elif mutation == "missing-control":
        c.pinned_controls.pop("metric")
    elif mutation == "duplicate-arm":
        ds[1].arm_id = "a"
    elif mutation == "overlap":
        run["source_partitions"]["evaluation"] = ["src-1"]
    elif mutation == "label-leak":
        run["candidate_production_inputs"].append("judgments.jsonl")
    elif mutation == "denied":
        ps[0].decision = "DENY"
    elif mutation == "expired":
        ps[0].decision = "EXPIRED"
    elif mutation == "revoked":
        ps[0].decision = "REVOKED"
    elif mutation == "backend-claim":
        ds[0].resolved_backend = "fake-runtime"
    elif mutation == "malformed-provenance":
        run["provenance"].pop("attempt_id")
    with pytest.raises(ContractError):
        validate_comparison(c, ds, ps, run)


@pytest.mark.parametrize("historical_sha", ["0" * 40, "f" * 40, "865c55c30147eb5320a80b70344f6201f98332f8"])
def test_real_mode_refuses_even_with_historical_sha(historical_sha):
    c, ds, ps, run = fixture("REAL")
    run["historical_gate0_sha"] = historical_sha
    with pytest.raises(ContractError, match="current authority"):
        validate_comparison(c, ds, ps, run)


def test_duplicate_policy_ids_and_descriptor_policy_mismatch_fail():
    c, ds, ps, run = fixture()
    ps[1].policy_decision_id = "p-a"
    with pytest.raises(ContractError):
        validate_comparison(c, ds, ps, run)


def test_synthetic_resource_observations_must_remain_not_observed():
    c, ds, ps, run = fixture()
    run["resource_observations"] = {"wall_time_ms": 12}
    with pytest.raises(ContractError):
        validate_comparison(c, ds, ps, run)


def test_label_firewall_rejects_label_fields_hidden_in_candidate_input_declarations():
    c, ds, ps, run = fixture()
    run["candidate_production_inputs"][0]["input_id"] = "candidate-with-relevance-v3"
    with pytest.raises(ContractError, match="label|judgment|gold|relevance|relevant"):
        validate_comparison(c, ds, ps, run)


def test_candidate_input_declarations_reject_unclosed_label_fields():
    c, ds, ps, run = fixture()
    run["candidate_production_inputs"][0]["declared_fields"] = ["candidate_id", "relevant"]
    with pytest.raises(ContractError, match="closed kind schema|label-bearing data"):
        validate_comparison(c, ds, ps, run)


def test_run_manifest_rejects_unknown_top_level_label_metadata():
    c, ds, ps, run = fixture()
    run["candidate_label_metadata"] = {"version": "v1"}
    with pytest.raises(ContractError, match="label|judgment|gold|relevance|relevant"):
        validate_comparison(c, ds, ps, run)


def test_candidate_input_declarations_must_be_typed_and_closed():
    c, ds, ps, run = fixture()
    run["candidate_production_inputs"] = ["candidates-v3.jsonl"]
    with pytest.raises(ContractError, match="typed|kind|input"):
        validate_comparison(c, ds, ps, run)


@pytest.mark.parametrize("mutation", ["one-sided", "both-sides"])
def test_descriptor_rejects_undeclared_extra_axes(mutation):
    c, ds, ps, run = fixture()
    ds[0].extra_axis = "left"
    if mutation == "both-sides":
        ds[1].extra_axis = "right"
    with pytest.raises(ContractError, match="descriptor fields|undeclared material axis"):
        validate_comparison(c, ds, ps, run)


def test_run_manifest_rejects_neutral_unknown_nested_payload():
    c, ds, ps, run = fixture()
    run["auxiliary_payload"] = {"metadata": {"quality_signal": "human preference"}}
    with pytest.raises(ContractError, match="unknown run-manifest fields"):
        validate_comparison(c, ds, ps, run)


def test_run_manifest_rejects_unknown_nested_partition_fields():
    c, ds, ps, run = fixture()
    run["source_partitions"]["metadata"] = {"quality_signal": "human preference"}
    with pytest.raises(ContractError, match="source_partitions fields"):
        validate_comparison(c, ds, ps, run)


def test_run_manifest_rejects_label_semantics_in_recognized_fields():
    c, ds, ps, run = fixture()
    run["status"] = "ranking_labels_v1"
    with pytest.raises(ContractError, match="label-bearing data"):
        validate_comparison(c, ds, ps, run)


def test_representation_space_join_uses_closed_candidate_input_contract():
    c, ds, ps, run = fixture()
    run["candidate_production_inputs"][0]["space_id"] = "space-b"
    with pytest.raises(ContractError, match="representation space"):
        validate_comparison(c, ds, ps, run)
