"""D3/D4: exact-rational gold uncertainty and canonical eight time domains.

Frozen authority:

* ``docs/architecture/CANONICAL_CONTRACTS.md`` §2:50-61 -- exact rational
  interval/uncertainty values, never binary floating point.
* ``docs/implementation-spec-v1.1.md`` §9.3:349-352 -- explicit exact
  uncertainty ``[u_start, u_end]``; §5:147-151 -- typed time domains.
* ``docs/implementation-spec-v1.1.md`` §9.2:321 and
  ``docs/architecture/CANONICAL_CONTRACTS.md`` §4:91-112 -- the canonical eight
  time domains (legacy ``NORMALIZED_PTS`` is an alias, not a domain).
* ``docs/superpowers/plans/2026-10-25-g0-schema-closure-and-generated-media-boundary.md``
  Task 4 Step 1 (D3: explicit optional rational ``{start,end}``).
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from gate0.labels import build_gold_events, build_queries

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "schemas/gate0/gold_events.json").read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)

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

PAYLOAD_REQUIRED = {
    "assertion_id", "interval_id", "query_id", "revision_id", "reviewer_id",
    "grade", "rationale", "label_version", "review_status", "evidence_class",
    "stream_index", "time_domain", "origin", "start", "end", "time_base",
    "endpoint_semantics", "precision", "producer_attempt_id",
    "refinement_eligibility",
}


def _record(payload: dict) -> dict:
    return {
        "record_id": "gold_0001",
        "record_type": "gold_event",
        "record_schema_version": "gate0.v1",
        "record_digest": "0" * 64,
        "payload": payload,
    }


def _errors(record: dict) -> list[jsonschema.ValidationError]:
    return list(VALIDATOR.iter_errors(record))


def _queries() -> tuple[dict, ...]:
    specs = (
        [(f"q{i}", f"query {i}", ("APPEARANCE", "POSITIVE")) for i in range(24)]
        + [(f"a{i}", f"absent {i}", ("VISIBLE_ACTION", "ABSENT")) for i in range(8)]
        + [(f"d{i}", f"dev {i}", ("INTERACTION", "POSITIVE")) for i in range(8)]
    )
    split = {
        **{f"q{i}": "EVALUATION" for i in range(24)},
        **{f"a{i}": "EVALUATION" for i in range(8)},
        **{f"d{i}": "DEVELOPMENT" for i in range(8)},
    }
    return build_queries(specs, split, "q-v1")


def _event(reviewer_id: str, **overrides: object) -> dict:
    event: dict[str, object] = {
        "query_id": "q0",
        "revision_id": "r1",
        "reviewer_id": reviewer_id,
        "grade": 2,
        "rationale": "visible",
        "stream_index": 0,
        "start": (0, 1),
        "end": (4, 1),
        "uncertainty": {
            "start": {"numerator": 0, "denominator": 1},
            "end": {"numerator": 0, "denominator": 1},
        },
    }
    event.update(overrides)
    return event


def _producer_payload(**overrides: object) -> dict:
    queries = _queries()
    gold = build_gold_events(
        [_event("u1", **overrides), _event("u2", **overrides)], queries, "gold-v1"
    )
    assert len(gold) == 2
    return gold[0]["payload"]


def test_uncertainty_is_a_closed_exact_rational_start_end_object():
    uncertainty = SCHEMA["properties"]["payload"]["properties"]["uncertainty"]
    assert uncertainty == {
        "type": "object",
        "additionalProperties": False,
        "required": ["start", "end"],
        "properties": {
            "start": {"$ref": "#/$defs/rational"},
            "end": {"$ref": "#/$defs/rational"},
        },
    }
    assert SCHEMA["$defs"]["rational"] == {
        "type": "object",
        "additionalProperties": False,
        "required": ["numerator", "denominator"],
        "properties": {
            "numerator": {"type": "integer"},
            "denominator": {"type": "integer", "minimum": 1},
        },
    }
    assert "lower" not in json.dumps(uncertainty)
    assert "upper" not in json.dumps(uncertainty)


def test_uncertainty_stays_optional_so_unknown_is_not_zero_padded():
    payload_schema = SCHEMA["properties"]["payload"]
    assert set(payload_schema["required"]) == PAYLOAD_REQUIRED
    assert "uncertainty" not in payload_schema["required"]
    payload = _producer_payload()
    del payload["uncertainty"]
    assert _errors(_record(payload)) == []


def test_current_producer_gold_record_is_admitted():
    """RED before D3/D4: the emitted uncertainty is ``{start,end}`` exact
    rationals and time_domain is SEMANTIC_SECONDS, both rejected by the
    checked-in schema (which still requires lower/upper floats)."""
    payload = _producer_payload()
    assert payload["uncertainty"] == {
        "start": {"numerator": 0, "denominator": 1},
        "end": {"numerator": 0, "denominator": 1},
    }
    assert payload["time_domain"] == "SEMANTIC_SECONDS"
    errors = _errors(_record(payload))
    assert errors == [], errors


def test_uncertainty_refuses_floats_and_legacy_lower_upper_keys():
    payload = _producer_payload()
    for uncertainty in (
        {"start": 0.5, "end": 0.5},
        {"start": {"numerator": 0.5, "denominator": 1}, "end": {"numerator": 0, "denominator": 1}},
        {"lower": 0.5, "upper": 0.5},
        {"start": {"numerator": 0, "denominator": 1}},
        {"start": {"numerator": 0, "denominator": 0}, "end": {"numerator": 0, "denominator": 1}},
        {"start": {"numerator": 0, "denominator": 1}, "end": {"numerator": 0, "denominator": 1}, "extra": 0},
    ):
        assert _errors(_record({**payload, "uncertainty": uncertainty})), uncertainty
    exact = {"start": {"numerator": 1, "denominator": 3}, "end": {"numerator": 2, "denominator": 3}}
    assert _errors(_record({**payload, "uncertainty": exact})) == []


def test_time_domain_is_the_canonical_eight_and_rejects_legacy_aliases():
    enum = SCHEMA["properties"]["payload"]["properties"]["time_domain"]["enum"]
    assert tuple(enum) == CANONICAL_TIME_DOMAINS
    payload = _producer_payload()
    for domain in CANONICAL_TIME_DOMAINS:
        assert _errors(_record({**payload, "time_domain": domain})) == [], domain
    for legacy in ("NORMALIZED_PTS", "TIMELINE", "semantic_seconds", "SOURCE_FRAME_PTS"):
        assert _errors(_record({**payload, "time_domain": legacy})), legacy


def test_time_domain_vocabulary_matches_the_typed_interval_schema():
    gold = SCHEMA["properties"]["payload"]["properties"]["time_domain"]["enum"]
    window = json.loads(
        (ROOT / "schemas/gate0/window_sample_manifest.json").read_text(encoding="utf-8")
    )
    typed = window["$defs"]["typed_interval_payload"]["properties"]["time_domain"]["enum"]
    assert tuple(gold) == tuple(typed) == CANONICAL_TIME_DOMAINS
