"""Contract-level identity and canonical digest oracles for T01."""

import math
import pytest

from gate0.identity import digest_json, opaque_id, validate_opaque_id


def test_opaque_id_boundary_and_digest_shape():
    # Opaque IDs are generated from a canonical seed digest; the seed is not
    # itself used as the suffix and may contain otherwise-illegal characters.
    assert opaque_id("run", "1_extra") == "run_c3c1e4da90e99e9bab8f7a64f283e9f8"
    assert opaque_id("revision", "a-b") == "revision_4a3ef97adbc41a188a7519c6673e9195"
    assert len(digest_json({"b": 1, "a": "ü"})) == 64
    assert digest_json({"a": 1}) != digest_json({"a": 2})


@pytest.mark.parametrize("valid", ["a", "revision_a-b", "run_1_extra", "x" * 128])
def test_validate_opaque_id_accepts_contract_syntax(valid):
    assert validate_opaque_id(valid)


@pytest.mark.parametrize("bad", ["", "UPPER", "a/b", "a\\b", "é", "x" * 129, "_leading"])
def test_validate_opaque_id_rejects_non_contract_syntax(bad):
    with pytest.raises((ValueError, TypeError)):
        validate_opaque_id(bad)


def test_digest_rejects_nonfinite_numbers():
    with pytest.raises((ValueError, TypeError)):
        digest_json({"value": math.nan})
    with pytest.raises((ValueError, TypeError)):
        digest_json({"value": math.inf})
