"""Closed-schema contract tests for ``schemas/gate0/ranked_candidates.json`` (D1/D8).

Authority: ``docs/implementation-spec-v1.1.md`` §3:84 ("Query/arm/window/
representation, finite score, rank, total-order key, coverage/status"),
§3:93-99 (technical windows are canonical ``window_sample_manifest.jsonl``
records, never a duplicated logical record), §5:178-181 (primary ranking
tuple), §9.2 closed record matrix ("Fields not listed are prohibited");
``CANONICAL_CONTRACTS.md`` §6 (representation_id joins the typed window and
sampling manifest); D1/D8 disposition.

Owner decisions (frozen): Q1=A carries an explicit ``arm_id`` and a closed
representation-kind registry; the metadata floor is never dressed up as a
model descriptor and the semantic identity fields stay on the representation
record.  D8 resolves the semantic-identity defect: ``representation_id`` is
required *iff* the candidate's arm declares ``representation_kind=embedding``
and must be absent for ``metadata_floor``.  JSON Schema cannot express that
cross-artifact conditional, so ``contracts/validator.py`` enforces it; this
schema keeps ``representation_id`` an optional id-typed property and never
hardcodes an arm id.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "schemas/gate0/ranked_candidates.json").read_text(encoding="utf-8"))
PAYLOAD = SCHEMA["$defs"]["payload"]

# §9.2 required payload fields (candidate_id, query_id, score_status,
# coverage_status, gold_accessed) plus the Owner-approved explicit identity
# additions arm_id/window_id.  ``representation_id`` is conditional (D8) and
# therefore optional here; score/rank/tie_key are §9.2-optional.
REQUIRED_PAYLOAD = {
    "candidate_id", "query_id", "arm_id", "window_id", "score_status",
    "coverage_status", "gold_accessed",
}
OPTIONAL_PAYLOAD = {"score", "rank", "tie_key", "representation_id"}
#: §9.2-unlisted duplicate coordinate/evidence fields the pre-D8 producer
#: emitted.  The technical window is the canonical coordinate record, so these
#: are prohibited rather than merely optional.
UNLISTED_COORDINATE_FIELDS = (
    "revision_id", "interval_ref", "start", "end", "mapping_ref", "origin",
    "time_base", "input_artifact_refs",
)


def _validator(subschema: dict) -> Draft202012Validator:
    root = {"$defs": SCHEMA["$defs"]}
    root.update(subschema)
    return Draft202012Validator(root)


def _payload(**overrides: object) -> dict:
    payload = {
        "candidate_id": "candidate_abc",
        "query_id": "query_appearance_01",
        "arm_id": "metadata-floor",
        "window_id": "rev_eval_sunrise_window_0",
        "score": 0.71,
        "score_status": "FINITE",
        "rank": 1,
        "coverage_status": "SELECTED",
        "gold_accessed": False,
    }
    payload.update(overrides)
    return payload


def _assert_valid(value: dict) -> None:
    errors = list(_validator(PAYLOAD).iter_errors(value))
    assert not errors, errors


def _assert_invalid(value: dict) -> None:
    with pytest.raises(ValidationError):
        _validator(PAYLOAD).validate(value)


def test_record_schema_version_is_the_governing_gate0_v1() -> None:
    assert SCHEMA["properties"]["record_schema_version"] == {"const": "gate0.v1"}
    assert SCHEMA["properties"]["record_type"] == {"const": "ranked_candidate"}
    record = {
        "record_id": "record_a",
        "record_type": "ranked_candidate",
        "record_schema_version": "gate0.v1",
        "record_digest": "0" * 64,
        "payload": _payload(),
    }
    Draft202012Validator(SCHEMA).validate(record)
    with pytest.raises(ValidationError):
        Draft202012Validator(SCHEMA).validate({**record, "record_schema_version": "gate0.ranked_candidate.v1"})


def test_payload_requires_arm_id_and_window_id() -> None:
    assert REQUIRED_PAYLOAD <= set(PAYLOAD["required"])
    _assert_valid(_payload())
    for key in REQUIRED_PAYLOAD:
        missing = _payload()
        missing.pop(key)
        _assert_invalid(missing)
    for key in ("arm_id", "window_id"):
        assert PAYLOAD["properties"][key] == {"$ref": "#/$defs/id"}


def test_metadata_floor_payload_validates_without_representation_id() -> None:
    """D8: the metadata arm never fabricates a semantic representation identity."""
    assert "representation_id" not in PAYLOAD["required"]
    assert set(PAYLOAD["properties"]) == REQUIRED_PAYLOAD | OPTIONAL_PAYLOAD
    assert PAYLOAD["additionalProperties"] is False
    _assert_valid(_payload())
    _assert_valid(_payload(arm_id="offline-development-arm", representation_id="representation_abc"))


def test_representation_id_is_an_optional_id_typed_property() -> None:
    assert PAYLOAD["properties"]["representation_id"]["$ref"] == "#/$defs/id"
    _assert_valid(_payload(representation_id="representation_abc"))
    _assert_invalid(_payload(representation_id=None))
    _assert_invalid(_payload(representation_id="REPRESENTATION#1"))
    _assert_invalid(_payload(representation_id=7))


def test_representation_id_conditional_is_documented_not_hardcoded() -> None:
    """The cross-artifact conditional lives in the validator, not in arm ids."""
    description = PAYLOAD["properties"]["representation_id"]["description"]
    assert "embedding" in description and "metadata_floor" in description
    assert "validator" in description
    for arm_id in ("metadata-floor", "offline-development-arm", "arbitrary-arm"):
        _assert_valid(_payload(arm_id=arm_id))


def test_unlisted_duplicate_coordinates_are_prohibited_not_optional() -> None:
    for key in UNLISTED_COORDINATE_FIELDS:
        assert key not in PAYLOAD["properties"], key
        _assert_invalid(_payload(**{key: "x"}))
    # The unlisted fields are gone; the window record is the sole coordinate
    # surface.  ``input_artifact_refs`` moves to the artifact envelope.
    _assert_invalid(_payload(unknown_identity="x"))


def test_failed_status_rows_keep_null_score_and_rank() -> None:
    _assert_valid(_payload(score=None, rank=None, score_status="FAILED", coverage_status="FAILED"))
    _assert_valid(_payload(score=0.0, rank=1, tie_key="tie"))
    _assert_invalid(_payload(score="0.71"))
    _assert_invalid(_payload(rank=0))
    _assert_invalid(_payload(score_status="MAYBE"))
    _assert_invalid(_payload(coverage_status="MAYBE"))


def test_rational_coordinate_and_evidence_surfaces_are_gone() -> None:
    for key in ("start", "end", "origin", "time_base"):
        _assert_invalid(_payload(**{key: {"numerator": 0, "denominator": 1}}))
    _assert_invalid(_payload(gold_accessed=True))
    _assert_invalid(_payload(mapping_ref="rev_eval_sunrise_map_0_0_000000"))
    _assert_invalid(_payload(input_artifact_refs=[{
        "artifact_id": "artifact_sampling",
        "payload_digest": "0" * 64,
        "artifact_type": "window_sample_manifest.jsonl",
    }]))
    assert "ref" not in SCHEMA.get("$defs", {})
    assert "rational" not in SCHEMA.get("$defs", {})


def test_identity_fields_are_closed_and_never_a_model_descriptor() -> None:
    assert "model_identity" not in PAYLOAD["properties"]
    _assert_invalid(_payload(arm_id="SYNTHETIC_FAKE_EMBEDDER_V1"))
