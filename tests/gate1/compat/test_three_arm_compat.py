from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest

from gate1.contracts.types import Judgment, RankedCandidate
from gate1.harness import get_case


ARMS = ("VIP_V1_BASE", "VIP_V2_BASE", "VIP_V2_SO400M")


def _case():
    source = get_case("positive_one_axis")
    contract = deepcopy(source["comparison"])
    contract["arm_ids"] = [ARMS[0], ARMS[1]]
    contract["policy_eligibility"] = {ARMS[0]: "policy_a", ARMS[1]: "policy_b"}
    contract["pinned_controls"]["requested_model"] = "fake-generated"
    contract["validity_rules"] = {"require_complete_coverage": False}
    contract["dependency_refs"] = {
        "spec_sha": "d39fad8412b904d7d79cad8e15688bd4b348991f",
        "canonical_contract_blob": "c0b665d70b311dd98b7ff9f4f564b2d5750ed17b",
    }
    contract["decision_rule"] = {"comparison": "difference", "threshold": 0.25,
                                  "direction": "higher_is_better"}

    descriptors = deepcopy(source["descriptors"])
    descriptors[0].update(arm_id=ARMS[0], space_id="space-v1", requested_model="fake-generated")
    descriptors[1].update(arm_id=ARMS[1], space_id="space-v2", requested_model="fake-generated")
    descriptors[0]["requested_model"] = descriptors[1]["requested_model"]
    third = deepcopy(descriptors[1])
    third.update(record_id="descriptor-so400m", arm_id=ARMS[2], space_id="space-so400m",
                 policy_decision_id="policy_c")
    descriptors.append(third)

    policies = deepcopy(source["policies"])
    policies[0].update(policy_decision_id="policy_a")
    policies[1].update(policy_decision_id="policy_b")
    third_policy = deepcopy(policies[1])
    third_policy.update(record_id="policy-record-so400m", policy_decision_id="policy_c")
    policies.append(third_policy)

    manifest = deepcopy(source["run_manifest"])
    manifest["execution_mode"] = "SYNTHETIC"
    manifest["candidate_production_inputs"] = [
        {"kind": "query", "input_id": "query-1"},
        {"kind": "candidate", "input_id": "candidate-1"},
    ] + [
        {"kind": "representation", "input_id": f"repr-{arm}", "arm_id": arm,
         "space_id": descriptor["space_id"]}
        for arm, descriptor in zip(ARMS, descriptors)
    ]
    manifest["provenance"]["config_digest"] = "b" * 64
    b07_states = [
        {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE",
         "reason": "POOLED_GROUND_TRUTH"},
        {"metric_id": "ndcg_at_10", "status": "NOT_COMPUTABLE",
         "reason": "METRIC_NOT_IMPLEMENTED"},
    ]
    pair_contract = deepcopy(contract)
    pair_contract["policy_eligibility"] = dict(zip(ARMS, ("policy_a", "policy_b", "policy_c")))
    pair_contract["b07_metric_states"] = deepcopy(b07_states)
    envelope = {"schema_version": 2, "execution_mode": "SYNTHETIC", "arm_ids": list(ARMS),
                "pair_contract_template": pair_contract,
                "b07_metric_states": deepcopy(b07_states)}

    rankings = {
        ARMS[0]: (_row(ARMS[0], "candidate-1", 2, "space-v1"),
                  _row(ARMS[0], "candidate-2", 1, "space-v1")),
        ARMS[1]: (_row(ARMS[1], "candidate-1", 1, "space-v2"),
                  _row(ARMS[1], "candidate-2", 2, "space-v2")),
        ARMS[2]: (_row(ARMS[2], "candidate-1", 1, "space-so400m"),
                  _row(ARMS[2], "candidate-2", 2, "space-so400m")),
    }
    judgments = (Judgment("j1", "query-1", "candidate-1", True,
                          "synthetic-reviewer", True, "NOT_APPLICABLE_SYNTHETIC"),)
    return envelope, descriptors, policies, manifest, rankings, judgments


def _row(arm: str, candidate: str, rank: int, space: str):
    return RankedCandidate(
        record_id=f"{arm}-{candidate}", arm_id=arm, query_id="query-1",
        candidate_id=candidate, representation_id=f"repr-{arm}", space_id=space,
        score=float(rank), rank=rank, tie_key=(rank, candidate), coverage_status="SELECTED",
    )


def _compat_report(contract, descriptors, policies, manifest, rankings, judgments,
                   failures=(), **kwargs):
    """Call the adapter with the mandatory synthetic provenance arguments."""
    from gate1.harness import ARM_DERIVATIONS, build_three_arm_compat_report, gate1_code_sha

    kwargs.setdefault("query_ids", ("query-1",))
    kwargs.setdefault("fixture_id", "positive_one_axis")
    kwargs.setdefault("code_sha", gate1_code_sha())
    kwargs.setdefault("arm_derivations", ARM_DERIVATIONS)
    return build_three_arm_compat_report(
        contract, descriptors, policies, manifest, rankings, judgments, failures, **kwargs
    )


def test_three_arm_adapter_expands_charter_pairs_and_reuses_pair_evaluator():
    from gate1.harness import build_three_arm_compat_report

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    report = _compat_report(
        contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
    )

    assert report["compatibility_status"] == "COMPATIBLE"
    assert report["execution_mode"] == "SYNTHETIC"
    assert report["winner_status"] == "NOT_EVALUATED"
    assert [pair["arm_ids"] for pair in report["pairwise_evaluations"]] == [
        [ARMS[0], ARMS[1]], [ARMS[0], ARMS[2]], [ARMS[1], ARMS[2]]
    ]
    assert all(pair["validity"] == "VALID" for pair in report["pairwise_evaluations"])
    assert [pair["benchmark_status"] for pair in report["pairwise_evaluations"]] == [
        "PASS", "PASS", "FAIL"
    ]
    assert [pair["primary_value"] for pair in report["pairwise_evaluations"]] == [1.0, 1.0, 0.0]
    assert all("winner" not in pair for pair in report["pairwise_evaluations"])
    assert report["b07_metric_states"] == contract["b07_metric_states"]


def test_three_arm_adapter_rejects_duplicate_semantic_space_before_pair_evaluation():
    from gate1.harness import CompatibilityError, build_three_arm_compat_report

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    descriptors[2]["space_id"] = descriptors[1]["space_id"]
    with pytest.raises(CompatibilityError, match="distinct semantic spaces"):
        _compat_report(
            contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
        )


def test_three_arm_adapter_rejects_missing_arm_or_query_alignment_mismatch():
    from gate1.harness import CompatibilityError, build_three_arm_compat_report

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    del rankings[ARMS[2]]
    with pytest.raises(CompatibilityError):
        _compat_report(
            contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
        )

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    rankings[ARMS[2]] = (
        _row(ARMS[2], "candidate-1", 1, "space-so400m"),
        _row(ARMS[2], "candidate-2", 2, "space-so400m"),
        RankedCandidate("other-query", ARMS[2], "other-query", "candidate-3", "repr-x",
                        "space-so400m", 1.0, 1, (1, "candidate-3"), "SELECTED"),
    )
    with pytest.raises(CompatibilityError):
        _compat_report(
            contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
        )

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    rankings[ARMS[2]] = tuple(
        replace(row, query_id=[]) for row in rankings[ARMS[2]]
    )
    with pytest.raises(CompatibilityError):
        _compat_report(
            contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
        )


def test_three_arm_adapter_wraps_malformed_inputs_in_compatibility_error():
    from gate1.harness import CompatibilityError, build_three_arm_compat_report

    for malformed, query_ids in (
        ("policy", ("query-1",)),
        ("candidate_input", ("query-1",)),
        ("ranking", ("query-1",)),
        ("query_ids", None),
        ("execution_mode", ("query-1",)),
    ):
        contract, descriptors, policies, manifest, rankings, judgments = _case()
        if malformed == "policy":
            policies[0] = None
        elif malformed == "candidate_input":
            manifest["candidate_production_inputs"][0] = None
        elif malformed == "ranking":
            rankings[ARMS[0]] = (None,)
        elif malformed == "execution_mode":
            contract["execution_mode"] = "REAL"
        with pytest.raises(CompatibilityError):
            _compat_report(
                contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=query_ids
            )


def test_three_arm_adapter_wraps_malformed_arm_list_in_compatibility_error():
    from gate1.harness import CompatibilityError, build_three_arm_compat_report

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    contract["arm_ids"] = None
    with pytest.raises(CompatibilityError):
        _compat_report(
            contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
        )


def test_three_arm_adapter_wraps_unhashable_descriptor_arm_id_in_compatibility_error():
    from gate1.harness import CompatibilityError, build_three_arm_compat_report

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    descriptors[0]["arm_id"] = []
    with pytest.raises(CompatibilityError):
        _compat_report(
            contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
        )


def test_three_arm_adapter_wraps_unhashable_ranked_query_id_in_compatibility_error():
    from gate1.harness import CompatibilityError, build_three_arm_compat_report

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    rankings[ARMS[2]] = tuple(replace(row, query_id=[]) for row in rankings[ARMS[2]])
    with pytest.raises(CompatibilityError):
        _compat_report(
            contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
        )


def test_each_pair_receives_only_its_local_rankings_policies_and_representations(monkeypatch):
    import gate1.harness as compat

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    original_validate = compat.validate_comparison
    original_evaluate = compat.evaluate_comparison
    validated = []
    evaluated = []

    def capture_validate(pair_contract, pair_descriptors, pair_policies, pair_manifest):
        validated.append((
            tuple(pair_contract["arm_ids"]),
            {descriptor["arm_id"] for descriptor in pair_descriptors},
            {policy["policy_decision_id"] for policy in pair_policies},
            {item["arm_id"] for item in pair_manifest["candidate_production_inputs"]
             if item["kind"] == "representation"},
        ))
        return original_validate(pair_contract, pair_descriptors, pair_policies, pair_manifest)

    def capture_evaluate(pair_contract, pair_rankings, *args, **kwargs):
        evaluated.append((
            tuple(pair_rankings),
            {row.arm_id for rows in pair_rankings.values() for row in rows},
            {row.space_id for rows in pair_rankings.values() for row in rows},
        ))
        return original_evaluate(pair_contract, pair_rankings, *args, **kwargs)

    monkeypatch.setattr(compat, "validate_comparison", capture_validate)
    monkeypatch.setattr(compat, "evaluate_comparison", capture_evaluate)
    rankings = {
        arm: tuple(replace(row, score=-1.0e100 if arm == ARMS[0] else 1.0e100)
                   for row in rows)
        for arm, rows in rankings.items()
    }
    report = _compat_report(
        contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
    )

    expected = [(ARMS[0], ARMS[1]), (ARMS[0], ARMS[2]), (ARMS[1], ARMS[2])]
    assert [row[0] for row in validated] == expected
    assert [row[1] for row in validated] == [set(pair) for pair in expected]
    assert [row[3] for row in validated] == [set(pair) for pair in expected]
    assert [set(row[2]) for row in validated] == [
        {"policy_a", "policy_b"}, {"policy_a", "policy_c"}, {"policy_b", "policy_c"}
    ]
    assert [row[0] for row in evaluated] == expected
    assert [row[1] for row in evaluated] == [set(pair) for pair in expected]
    assert [len(row[2]) for row in evaluated] == [2, 2, 2]
    assert report["winner_status"] == "NOT_EVALUATED"
    assert [pair["primary_value"] for pair in report["pairwise_evaluations"]] == [1.0, 1.0, 0.0]
