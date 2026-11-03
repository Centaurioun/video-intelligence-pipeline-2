from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from tests.gate1.compat.test_three_arm_compat import ARMS, _case, _compat_report


def test_generated_three_arm_compatibility_keeps_pair_order_and_no_winner():
    from gate1.harness import LIMITATIONS

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    report = _compat_report(
        contract, descriptors, policies, manifest, rankings, judgments, (), query_ids=("query-1",)
    )

    assert [pair["arm_ids"] for pair in report["pairwise_evaluations"]] == [
        [ARMS[0], ARMS[1]], [ARMS[0], ARMS[2]], [ARMS[1], ARMS[2]]
    ]
    assert report["winner_status"] == "NOT_EVALUATED"
    schema_path = Path(__file__).resolve().parents[4] / "schemas/gate1_compat_v2/three_arm_compat_report.json"
    schema = json.loads(schema_path.read_text())
    Draft202012Validator(schema).validate(report)
    assert report["limitations"] == list(LIMITATIONS)
