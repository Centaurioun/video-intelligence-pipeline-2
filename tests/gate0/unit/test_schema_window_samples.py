"""D2: closed ``sample_target`` / ``typed_interval`` union for window samples.

Frozen authority:

* ``docs/implementation-spec-v1.1.md`` §9.2:321-322 -- typed_interval and
  sample_target payload columns.
* ``docs/implementation-spec-v1.1.md`` §9.2:331-333 -- pts_status and
  coverage_status required enum values ("encode it without widening it").
* ``docs/architecture/CANONICAL_CONTRACTS.md`` §4:89-99 -- typed interval
  envelope and the canonical eight time domains.
* ``docs/superpowers/plans/2026-10-25-g0-schema-closure-and-generated-media-boundary.md``
  Task 4 Step 1.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from gate0.adapters.decoder import DecodedFrame
from gate0.inventory import RevisionRef
from gate0.temporal import sample_targets

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "schemas/gate0/window_sample_manifest.json").read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)

# CANONICAL_CONTRACTS.md §4:91-112 (eight typed time domains).
CANONICAL_TIME_DOMAINS = (
    "SEMANTIC_SECONDS",
    "TECHNICAL_WINDOW",
    "MATCHED_OFFSET",
    "SOURCE_PTS",
    "SOURCE_FRAME",
    "PROXY_TIME",
    "TIMELINE_TIME",
    "RENDERED_OUTPUT",
)
# implementation-spec-v1.1.md §9.2:331-333 plus the producer-named coverage
# failures adjudicated for D2 (MIXED_TIME_BASE / MISSING_TIE_EVIDENCE /
# NO_COVERAGE).  MISSING_PTS is producer drift and is deliberately absent.
EXPECTED_PTS_STATUSES = (
    "VALID", "MISSING", "NON_MONOTONE", "DISCONTINUOUS", "OUT_OF_RANGE",
    "WRONG_STREAM", "AMBIGUOUS", "MIXED_TIME_BASE", "MISSING_TIE_EVIDENCE",
    "NO_COVERAGE",
)
# Frozen contract coverage vocabulary (subset shared with ranked candidates).
FROZEN_COVERAGE_STATUSES = (
    "PLANNED", "SELECTED", "FAILED", "OMITTED", "QUARANTINED", "EMPTY",
)

REVISION = RevisionRef("rev_1", "content_1", "synthetic", 0, "config")


def _record(record_type: str, payload: dict) -> dict:
    return {
        "record_id": "sample_0001",
        "record_type": record_type,
        "record_schema_version": "gate0.v1",
        "record_digest": "0" * 64,
        "payload": payload,
    }


def _errors(record: dict) -> list[jsonschema.ValidationError]:
    return list(VALIDATOR.iter_errors(record))


def typed_interval_payload(**overrides: object) -> dict:
    payload: dict[str, object] = {
        "interval_id": "interval_0",
        "revision_id": "rev_1",
        "stream_index": 0,
        "time_domain": "SEMANTIC_SECONDS",
        "origin": {"numerator": 0, "denominator": 1},
        "start": {"numerator": 0, "denominator": 1},
        "end": {"numerator": 1, "denominator": 2},
        "endpoint_semantics": "HALF_OPEN",
        "time_base": {"numerator": 1, "denominator": 90000},
        "precision": "semantic-interval",
        "producer_attempt_id": "attempt_0",
        "refinement_eligibility": "INELIGIBLE",
    }
    payload.update(overrides)
    return payload


def _sample_target_payloads() -> list[dict]:
    frames = (
        DecodedFrame(0, 1, 2, 0, 0, "f0", b"", dts_ticks=-1, frame_index=9),
        DecodedFrame(None, 1, 2, 1, 1, "unknown", b""),
    )
    return [row.to_dict() for row in sample_targets(REVISION, frames, window_count=1)]


def _producer_coverage(payloads: list[dict]) -> set[str]:
    return {str(payload["coverage_status"]) for payload in payloads}


def test_record_type_is_the_closed_two_member_union():
    assert SCHEMA["properties"]["record_type"] == {"enum": ["sample_target", "typed_interval"]}
    assert SCHEMA["properties"]["record_schema_version"] == {"const": "gate0.v1"}
    assert set(SCHEMA["required"]) == {
        "record_id", "record_type", "record_schema_version", "record_digest", "payload",
    }


def test_payload_is_one_of_two_closed_defs_payloads():
    payload = SCHEMA["properties"]["payload"]
    assert set(payload) == {"oneOf"}
    assert payload["oneOf"] == [
        {"$ref": "#/$defs/sample_target_payload"},
        {"$ref": "#/$defs/typed_interval_payload"},
    ]
    for name in ("sample_target_payload", "typed_interval_payload"):
        definition = SCHEMA["$defs"][name]
        assert definition["type"] == "object"
        assert definition["additionalProperties"] is False


def test_valid_producer_sample_target_wire_record_is_admitted():
    """RED before D2: the emitted row carries stream_index/source_frame_identity
    and coverage_status=SUCCEEDED, all rejected by the checked-in schema."""
    payloads = _sample_target_payloads()
    selected = [p for p in payloads if p["coverage_status"] == "SELECTED"]
    assert selected, "producer must emit the frozen SELECTED vocabulary on the wire"
    for payload in payloads:
        errors = _errors(_record("sample_target", payload))
        assert errors == [], errors


def test_producer_failure_targets_use_frozen_pts_and_coverage_vocabulary():
    payloads = _sample_target_payloads()
    assert {"SELECTED", "FAILED"} <= _producer_coverage(payloads)
    pts_statuses = {str(payload["pts_status"]) for payload in payloads}
    assert pts_statuses <= set(EXPECTED_PTS_STATUSES)
    assert "MISSING" in pts_statuses
    assert "MISSING_PTS" not in pts_statuses


def test_sample_target_payload_declares_all_new_provenance_fields():
    properties = SCHEMA["$defs"]["sample_target_payload"]["properties"]
    assert properties["stream_index"] == {"type": "integer", "minimum": 0}
    assert properties["dts_ticks"] == {"type": "integer"}
    assert properties["frame_index"] == {"type": "integer", "minimum": 0}
    assert properties["source_frame_identity"] == {"$ref": "#/$defs/id"}
    assert SCHEMA["$defs"]["id"] == {
        "type": "string",
        "pattern": "^[a-z0-9][a-z0-9_-]{0,127}$",
    }
    payload = _sample_target_payloads()[0]
    assert payload["source_frame_identity"] == "f0"
    assert _errors(_record("sample_target", payload)) == []


def test_sample_target_payload_rejects_typed_interval_fields_and_unknown_fields():
    payload = _sample_target_payloads()[0]
    for extra in (
        {"revision_id": "rev_1"},
        {"time_domain": "SEMANTIC_SECONDS"},
        {"unknown_field": 1},
    ):
        assert _errors(_record("sample_target", {**payload, **extra})), extra


def test_typed_interval_payload_requires_exactly_the_frozen_envelope():
    required = {
        "interval_id", "revision_id", "stream_index", "time_domain", "origin",
        "start", "end", "endpoint_semantics", "time_base", "precision",
        "producer_attempt_id", "refinement_eligibility",
    }
    definition = SCHEMA["$defs"]["typed_interval_payload"]
    assert set(definition["required"]) == required
    assert set(definition["properties"]) == required | {"mapping_ref"}
    record = _record("typed_interval", typed_interval_payload())
    assert _errors(record) == []
    for field in sorted(required):
        payload = typed_interval_payload()
        del payload[field]
        assert _errors(_record("typed_interval", payload)), field
    assert _errors(_record("typed_interval", typed_interval_payload(mapping_ref="rev_1_map_f0"))) == []


def test_typed_interval_endpoint_semantics_is_half_open_const():
    properties = SCHEMA["$defs"]["typed_interval_payload"]["properties"]
    assert properties["endpoint_semantics"] == {"const": "HALF_OPEN"}
    for value in ("CLOSED", "half_open", "OPEN"):
        assert _errors(_record("typed_interval", typed_interval_payload(endpoint_semantics=value))), value


def test_typed_interval_rationals_reject_binary_float_conversion():
    float_payloads = (
        {"origin": 0.5},
        {"start": 0.25},
        {"end": 1.5},
        {"time_base": 0.5},
        {"origin": {"numerator": 0.5, "denominator": 1}},
        {"start": {"numerator": 0, "denominator": 0}},
        {"time_base": {"numerator": 0, "denominator": 1}},
    )
    for override in float_payloads:
        payload = typed_interval_payload(**override)
        assert _errors(_record("typed_interval", payload)), override
    exact = typed_interval_payload(
        origin={"numerator": -1, "denominator": 2},
        start={"numerator": 1, "denominator": 3},
        end={"numerator": 7, "denominator": 3},
        time_base={"numerator": 1, "denominator": 90000},
    )
    assert _errors(_record("typed_interval", exact)) == []


def test_typed_interval_time_domain_is_the_canonical_eight():
    enum = SCHEMA["$defs"]["typed_interval_payload"]["properties"]["time_domain"]["enum"]
    assert tuple(enum) == CANONICAL_TIME_DOMAINS
    assert "NORMALIZED_PTS" not in enum
    for domain in CANONICAL_TIME_DOMAINS:
        assert _errors(_record("typed_interval", typed_interval_payload(time_domain=domain))) == [], domain
    for legacy in ("NORMALIZED_PTS", "TIMELINE", "semantic_seconds"):
        assert _errors(_record("typed_interval", typed_interval_payload(time_domain=legacy))), legacy


def _matching_branches(payload: dict) -> list[str]:
    wrapper = {"$defs": SCHEMA["$defs"], "oneOf": SCHEMA["properties"]["payload"]["oneOf"]}
    names = ("sample_target_payload", "typed_interval_payload")
    return [
        name
        for name, branch in zip(names, wrapper["oneOf"])
        if not list(jsonschema.Draft202012Validator({"$defs": SCHEMA["$defs"], "$ref": branch["$ref"]}).iter_errors(payload))
    ]


def test_payload_branches_are_mutually_exclusive_and_refuse_a_merged_shape():
    """One payload shape, one branch: a target slot row cannot also claim the
    typed-interval envelope (or vice versa), so a merged/invented interval
    identity is refused by the closed union."""
    sample_payload = _sample_target_payloads()[0]
    assert _matching_branches(sample_payload) == ["sample_target_payload"]
    assert _matching_branches(typed_interval_payload()) == ["typed_interval_payload"]
    merged = {**sample_payload, **typed_interval_payload()}
    assert _matching_branches(merged) == []
    assert _errors(_record("sample_target", merged))
    assert _errors(_record("typed_interval", merged))


def test_record_type_is_bound_to_its_payload_branch():
    """F4: ``record_type`` and the payload union must agree.

    JSON Schema cannot couple a sibling ``const`` to ``oneOf`` directly, but an
    ``allOf`` if/then guard does bind them: a ``sample_target`` record may not
    carry the typed-interval envelope and a ``typed_interval`` record may not
    carry the sample-target wire shape.
    """
    assert _errors(_record("sample_target", _sample_target_payloads()[0])) == []
    assert _errors(_record("typed_interval", typed_interval_payload())) == []
    assert _errors(_record("sample_target", typed_interval_payload()))
    assert _errors(_record("typed_interval", _sample_target_payloads()[0]))


def test_pts_status_and_coverage_status_vocabulary_is_exact():
    properties = SCHEMA["$defs"]["sample_target_payload"]["properties"]
    assert tuple(properties["pts_status"]["enum"]) == EXPECTED_PTS_STATUSES
    assert tuple(properties["coverage_status"]["enum"]) == FROZEN_COVERAGE_STATUSES
