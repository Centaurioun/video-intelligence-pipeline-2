"""S-07 / S-08: the harness-built compatibility contract must be schema-closed."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from gate1.harness import CHARTER_ARMS, CHARTER_PAIRS, build_generated_three_arm_inputs


REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "schemas" / "gate1_compat_v2" / "three_arm_compat_contract.json"
ALLOWED_CASES = (
    "positive_one_axis",
    "tie_no_superiority",
    "partial_coverage",
    "quality_failure",
    "resource_failure",
)


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _contract() -> dict:
    return build_generated_three_arm_inputs("positive_one_axis")["contract"]


def test_harness_built_contract_is_schema_valid_for_every_executable_case():
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema()
    for case_id in ALLOWED_CASES:
        contract = build_generated_three_arm_inputs(case_id)["contract"]
        jsonschema.validate(contract, schema)
        assert contract["execution_mode"] == "SYNTHETIC"
        assert contract["arm_ids"] == list(CHARTER_ARMS)


def test_contract_inner_pairs_and_policy_keys_stay_consistent():
    contract = _contract()
    template = contract["pair_contract_template"]

    assert template["execution_mode"] == "SYNTHETIC"
    assert template["arm_ids"] in [list(pair) for pair in CHARTER_PAIRS]
    assert set(template["policy_eligibility"]) == set(CHARTER_ARMS)
    assert template["primary_metric"]["metric_id"] == "macro_hit_at_1"
    assert template["b07_metric_states"] == list(contract["b07_metric_states"])
    assert [state["metric_id"] for state in template["b07_metric_states"]] == [
        "recall_at_5",
        "ndcg_at_10",
    ]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda c: c["pair_contract_template"].update(execution_mode="REAL"),
        lambda c: c["pair_contract_template"].update(arm_ids=["arm_a", "arm_b"]),
        lambda c: c["pair_contract_template"].update(arm_ids=[CHARTER_ARMS[0]]),
        lambda c: c["pair_contract_template"].update(arm_ids=[CHARTER_ARMS[0], "UNKNOWN"]),
        lambda c: c["pair_contract_template"]["primary_metric"].update(metric_id="ndcg_at_10"),
        lambda c: c["pair_contract_template"]["policy_eligibility"].update({"extra-arm": "p"}),
        lambda c: c["pair_contract_template"]["policy_eligibility"].pop(CHARTER_ARMS[0]),
        lambda c: c["pair_contract_template"].pop("b07_metric_states"),
        lambda c: c["pair_contract_template"].update(b07_metric_states=[]),
        lambda c: c["pair_contract_template"].update(
            b07_metric_states=[
                {"metric_id": "ndcg_at_10", "status": "NOT_COMPUTABLE",
                 "reason": "METRIC_NOT_IMPLEMENTED"}
            ]
        ),
        lambda c: c["pair_contract_template"].update(
            b07_metric_states=[
                {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE",
                 "reason": "POOLED_GROUND_TRUTH"},
                {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE",
                 "reason": "METRIC_NOT_IMPLEMENTED"},
            ]
        ),
        lambda c: c.update(arm_ids=list(CHARTER_ARMS[:2])),
        lambda c: c.update(execution_mode="REAL"),
        lambda c: c.update(b07_metric_states=[]),
        lambda c: c.update(
            b07_metric_states=[
                {"metric_id": "ndcg_at_10", "status": "NOT_COMPUTABLE", "reason": "ZERO_IDCG"}
            ]
        ),
        lambda c: c.update(
            b07_metric_states=[
                {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE",
                 "reason": "POOLED_GROUND_TRUTH"},
                {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE",
                 "reason": "POOLED_GROUND_TRUTH"},
            ]
        ),
        lambda c: c.update(
            b07_metric_states=[
                {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE",
                 "reason": "POOLED_GROUND_TRUTH"},
                {"metric_id": "ndcg_at_10", "status": "NOT_COMPUTABLE",
                 "reason": "POOLED_GROUND_TRUTH"},
            ]
        ),
    ],
)
def test_contract_schema_rejects_unconstrained_or_inconsistent_shapes(mutate):
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema()
    candidate = deepcopy(_contract())
    mutate(candidate)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(candidate, schema)
