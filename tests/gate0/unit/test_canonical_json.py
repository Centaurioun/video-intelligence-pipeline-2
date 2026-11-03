"""Canonical JSON/JSONL byte-scope oracles."""
import math
import json
import pytest
from gate0.canonical_json import canonical_json_bytes, canonical_jsonl_bytes

def test_canonical_json_is_key_order_stable_and_utf8():
    assert canonical_json_bytes({"b": 1, "a": "ü"}) == canonical_json_bytes({"a": "ü", "b": 1})
    assert canonical_json_bytes({"a": "ü"}).decode("utf-8")

@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, {"nested": [math.nan]}])
def test_canonical_json_rejects_nonfinite_values(value):
    with pytest.raises((ValueError, TypeError)):
        canonical_json_bytes(value)

def test_jsonl_is_ordered_lf_terminated_and_rejects_blank_lines():
    rows = [{"record_id": "a"}, {"record_id": "b"}]
    output = canonical_jsonl_bytes(rows)
    assert output.endswith(b"\n") and b"\r" not in output
    assert json.loads(output.splitlines()[0]) == rows[0]
    with pytest.raises((ValueError, TypeError)):
        canonical_jsonl_bytes(rows + [None])
