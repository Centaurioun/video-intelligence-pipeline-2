import hashlib
import math

import pytest

from gate1.canonical_json import (
    canonical_bytes,
    canonical_jsonl_bytes,
    sha256_digest,
    sha256_digest_bytes,
)


def test_canonical_bytes_sort_keys_and_encode_utf8():
    assert canonical_bytes({"z": "café", "a": 1}) == '{"a":1,"z":"café"}'.encode("utf-8")


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_canonical_bytes_reject_non_finite_numbers(value):
    with pytest.raises(ValueError, match="non-finite"):
        canonical_bytes({"outer": [value]})


def test_jsonl_orders_rows_by_record_id_and_ends_each_record_with_lf():
    rows = [{"record_id": "a", "value": 1}, {"record_id": "b", "value": 2}]

    assert canonical_jsonl_bytes(rows) == (
        b'{"record_id":"a","value":1}\n{"record_id":"b","value":2}\n'
    )


@pytest.mark.parametrize(
    "rows",
    [
        [{"record_id": "b"}, {"record_id": "a"}],
        [{"record_id": "a"}, {"record_id": "a"}],
        [{"value": 1}],
        [None],
    ],
)
def test_jsonl_rejects_unsorted_duplicate_or_missing_record_ids(rows):
    with pytest.raises(ValueError):
        canonical_jsonl_bytes(rows)


def test_sha256_helpers_hash_canonical_values_and_raw_bytes():
    expected = hashlib.sha256(b'{"a":1,"b":2}').hexdigest()

    assert sha256_digest({"b": 2, "a": 1}) == expected
    assert sha256_digest_bytes(b'{"a":1,"b":2}') == expected
    assert len(sha256_digest({"a": 1})) == 64
    assert sha256_digest({"a": 1}) == sha256_digest({"a": 1})
