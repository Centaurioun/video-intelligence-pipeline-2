from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest

from tests.gate1.compat.test_three_arm_compat import _case


ROOT = Path(__file__).resolve().parents[3]


def _load(name: str):
    return json.loads((ROOT / "schemas/gate1_compat_v2" / name).read_text())


def test_three_arm_compat_schemas_are_closed_and_valid_draft_2020_12():
    contract = _load("three_arm_compat_contract.json")
    report = _load("three_arm_compat_report.json")

    Draft202012Validator.check_schema(contract)
    Draft202012Validator.check_schema(report)
    assert contract["additionalProperties"] is False
    assert report["additionalProperties"] is False
    assert contract["$schema"].endswith("draft/2020-12/schema")
    assert report["$schema"].endswith("draft/2020-12/schema")

    compatibility_contract = _case()[0]
    Draft202012Validator(contract).validate(compatibility_contract)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value.update(arm_ids=["VIP_V1_BASE", "VIP_V2_BASE"]),
        lambda value: value.update(arm_ids=["VIP_V2_BASE", "VIP_V1_BASE", "VIP_V2_SO400M"]),
        lambda value: value.update(unexpected=True),
        lambda value: value["pair_contract_template"].pop("comparison_id"),
        lambda value: value["b07_metric_states"][0].update(status="COMPUTABLE"),
        lambda value: value["b07_metric_states"][0].pop("reason"),
    ],
)
def test_three_arm_contract_schema_rejects_invalid_outer_and_nested_values(mutate):
    schema = _load("three_arm_compat_contract.json")
    value = deepcopy(_case()[0])
    mutate(value)

    assert not Draft202012Validator(schema).is_valid(value)


def test_three_arm_report_schema_accepts_generated_report_and_rejects_adversarial_variants():
    from tests.gate1.compat.test_three_arm_compat import ARMS, _compat_report

    schema = _load("three_arm_compat_report.json")
    validator = Draft202012Validator(schema)
    contract, descriptors, policies, manifest, rankings, judgments = _case()
    valid = _compat_report(
        contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
    )
    assert validator.is_valid(valid)

    invalid_values = []
    too_few_pairs = deepcopy(valid)
    too_few_pairs["pairwise_evaluations"].pop()
    invalid_values.append(too_few_pairs)

    short_pair = deepcopy(valid)
    short_pair["pairwise_evaluations"][0]["arm_ids"] = [ARMS[0]]
    invalid_values.append(short_pair)

    long_pair = deepcopy(valid)
    long_pair["pairwise_evaluations"][0]["arm_ids"] = list(ARMS)
    invalid_values.append(long_pair)

    unknown_pair = deepcopy(valid)
    unknown_pair["pairwise_evaluations"][0]["arm_ids"] = [ARMS[0], "UNKNOWN_ARM"]
    invalid_values.append(unknown_pair)

    extra_pair_field = deepcopy(valid)
    extra_pair_field["pairwise_evaluations"][0]["winner"] = ARMS[2]
    invalid_values.append(extra_pair_field)

    extra_report_field = deepcopy(valid)
    extra_report_field["winner"] = ARMS[2]
    invalid_values.append(extra_report_field)

    winner_claim = deepcopy(valid)
    winner_claim["winner_status"] = "SELECT_V1_BASE"
    invalid_values.append(winner_claim)

    assert all(not validator.is_valid(value) for value in invalid_values)
