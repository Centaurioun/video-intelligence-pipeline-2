"""T08 metric-identity contract tests for ``schemas/gate0/metrics.json``.

The frozen T08 metric IDs are dotted namespaces (``hit_at_10.metadata``,
``paired_lift.semantic_minus_metadata``, ``family_hit_at_10.<arm>.<family>``,
``absent_query_diagnostic.<arm>``).  ``metric_id`` previously referenced the
generic ``$defs/id`` pattern ``^[a-z0-9][a-z0-9_-]{0,127}$``, which refuses
every dot, so ``metrics.json`` failed payload-schema validation 13 times on a
produced run (contract-owner proposal D7 / Task 3).

These tests pin the intended contract:

* exactly the frozen T08 IDs validate;
* illegal IDs stay refused;
* the relaxation is local to ``$defs/metric/properties/metric_id``; the generic
  ``$defs/id`` pattern and its other consumers are untouched;
* the producer IDs are never renamed (they are frozen by T08).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from gate0.stages.report import REQUIRED_FAMILY_METRICS, REQUIRED_METRICS

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "schemas" / "gate0" / "metrics.json"

FAMILIES = (
    "appearance",
    "interaction",
    "scene_composition_camera_movement",
    "visible_action",
)

#: Frozen T08 identity set: the three required metrics, both family arms, and
#: both absent-query diagnostics.  Never rename these in the producer.
FROZEN_T08_METRIC_IDS = sorted(
    set(REQUIRED_METRICS)
    | {
        "family_hit_at_10.metadata.appearance",
        "family_hit_at_10.metadata.interaction",
        "family_hit_at_10.metadata.scene_composition_camera_movement",
        "family_hit_at_10.metadata.visible_action",
    }
    | {f"family_hit_at_10.semantic.{family}" for family in FAMILIES}
    | {"absent_query_diagnostic.metadata", "absent_query_diagnostic.semantic"}
)


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validator() -> Draft202012Validator:
    schema = _schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _metric(metric_id: str) -> dict:
    return {
        "metric_id": metric_id,
        "query_version_digest": "0" * 64,
        "gold_version_digest": "1" * 64,
        "judgment_version_digest": "2" * 64,
        "ranking_digest": "3" * 64,
        "baseline_digest": "4" * 64,
        "population_id": "pop_all",
        "numerator": 3,
        "denominator": 24,
        "calculation_version": "gate0.evaluation.v1",
        "benchmark_status": "VALID",
        "validity": "VALID",
    }


def _document(metric_id: str) -> dict:
    return {"schema_version": "gate0.metrics.v1", "metrics": [_metric(metric_id)]}


def _errors(document: object) -> list[str]:
    return [error.message for error in _validator().iter_errors(document)]


def test_frozen_t08_identity_set_is_complete() -> None:
    generated_family = {f"family_hit_at_10.semantic.{family}" for family in FAMILIES}
    assert generated_family == set(REQUIRED_FAMILY_METRICS)
    assert "hit_at_10.metadata" in FROZEN_T08_METRIC_IDS
    assert "hit_at_10.semantic" in FROZEN_T08_METRIC_IDS
    assert "paired_lift.semantic_minus_metadata" in FROZEN_T08_METRIC_IDS
    assert {"absent_query_diagnostic.metadata", "absent_query_diagnostic.semantic"} <= set(
        FROZEN_T08_METRIC_IDS
    )
    assert len(FROZEN_T08_METRIC_IDS) == 13


@pytest.mark.parametrize("metric_id", FROZEN_T08_METRIC_IDS)
def test_frozen_t08_metric_id_is_admissible(metric_id: str) -> None:
    """RED before D7: every dotted ID failed ``^[a-z0-9][a-z0-9_-]{0,127}$``."""
    errors = _errors(_document(metric_id))
    assert errors == [], errors


def test_all_frozen_t08_metrics_validate_together() -> None:
    document = {
        "schema_version": "gate0.metrics.v1",
        "metrics": [_metric(metric_id) for metric_id in FROZEN_T08_METRIC_IDS],
    }
    assert _errors(document) == []


@pytest.mark.parametrize(
    "metric_id",
    [
        "HIT_AT_10.METADATA",  # uppercase
        "hit at 10",  # space
        ".hit_at_10",  # leading dot
        "-hit_at_10",  # leading dash
        "hit/at_10",  # slash
        "hit:at_10",  # colon
        "",  # empty
        "a" * 129,  # too long
    ],
)
def test_illegal_metric_id_is_refused(metric_id: str) -> None:
    assert _errors(_document(metric_id))


def test_boundary_length_metric_id_is_admitted() -> None:
    assert _errors(_document("a" * 128)) == []


# ---------------------------------------------------------------------------
# scoping: the relaxation is local to metric_id
# ---------------------------------------------------------------------------

def test_metric_id_is_not_bound_to_the_generic_id_pattern() -> None:
    metric = _schema()["$defs"]["metric"]
    assert metric["properties"]["metric_id"] != {"$ref": "#/$defs/id"}


def test_generic_id_pattern_and_its_consumers_are_unchanged() -> None:
    schema = _schema()
    assert schema["$defs"]["id"]["pattern"] == "^[a-z0-9][a-z0-9_-]{0,127}$"
    assert schema["$defs"]["metric"]["properties"]["population_id"] == {"$ref": "#/$defs/id"}
    document = _document("hit_at_10.metadata")
    document["metrics"][0]["population_id"] = "pop.dotted"
    assert _errors(document)


def test_non_dotted_metric_ids_remain_admissible() -> None:
    assert _errors(_document("hit_at_10")) == []


@pytest.mark.parametrize(
    "metric_id",
    [
        "hit_at_10.",  # trailing dot
        "hit..at_10",  # empty segment
        "1hit_at_10",  # leading digit
        "hit-at_10",  # dash outside the frozen identity grammar
        "hit_at_10.-metadata",  # segment starts with a non-letter
    ],
)
def test_dot_grammar_is_narrow_not_a_generic_passthrough(metric_id: str) -> None:
    """F3: the metric-id relaxation stays a frozen-identity grammar, so
    malformed dotted names are refused instead of silently admitted."""
    assert _errors(_document(metric_id))


def test_metric_payload_shape_is_unchanged() -> None:
    schema = _schema()
    assert schema["required"] == ["schema_version", "metrics"]
    metric = schema["$defs"]["metric"]
    assert metric["additionalProperties"] is False
    assert metric["required"] == [
        "metric_id", "query_version_digest", "gold_version_digest",
        "judgment_version_digest", "ranking_digest", "baseline_digest",
        "population_id", "numerator", "denominator", "calculation_version",
        "benchmark_status", "validity",
    ]
    assert metric["properties"]["benchmark_status"]["enum"] == [
        "PLANNED", "VALID", "INVALID_PROTOCOL", "PASS", "FAIL", "NOT_RUN"
    ]
    assert metric["properties"]["validity"]["enum"] == [
        "VALID", "INVALID_PROTOCOL", "NOT_RUN"
    ]
