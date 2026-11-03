"""RED-first contract tests for the local semantic pilot report.

The report is an honest observation envelope, not a benchmark claim.  These
tests deliberately keep the input observations small and explicit so a report
implementation cannot silently replace missing measurements with zeroes or
derive a classification metric that the pilot did not measure.
"""

from __future__ import annotations

import pytest


def _build(**overrides):
    from vip_fvs.pilot_report import build_pilot_report

    values = {
        "run_id": "pilot-run-001",
        "source_identity": {
            "revision_id": "rev-synthetic-001",
            "source_sha256": "a" * 64,
        },
        "generation_identity": {
            "generation_id": "gen-synthetic-001",
            "model_identity": "vip-fvs-fake-embedder",
            "invocation_ref": "invoke-synthetic-001",
        },
        "observations": [
            {
                "query_id": "q-001",
                "label": "synthetic_positive",
                "observed": True,
                "ranked_candidate_ids": ["candidate-1"],
                "latency_ms": 12.5,
            },
            {
                "query_id": "q-002",
                "label": "synthetic_absent",
                "observed": True,
                "ranked_candidate_ids": [],
                "latency_ms": 8.0,
            },
            {
                "query_id": "q-003",
                "label": "synthetic_unobserved",
                "observed": False,
                "status": "NOT_OBSERVED",
            },
        ],
        "measurements": {
            "query_count_configured": 3,
            "wall_clock_ms": 44.0,
            "peak_rss_bytes": None,
        },
        "synthetic": True,
    }
    values.update(overrides)
    return build_pilot_report(**values)


def test_report_has_versioned_synthetic_label_and_explicit_scope():
    report = _build()

    assert report["schema"] == "vip_fvs.pilot_report.v1"
    assert report["run_label"] == "SYNTHETIC_PLUMBING_ONLY"
    assert report["scope"] == "LOCAL_SYNTHETIC_ONLY"
    assert report["synthetic"] is True
    assert "gate_decision" not in report
    assert "promotion_decision" not in report


def test_denominator_is_observed_query_count_and_raw_observations_are_retained():
    report = _build()

    assert report["summary"]["observed_query_count"] == 2
    assert report["summary"]["query_denominator"] == 2
    assert report["summary"]["configured_query_count"] == 3
    assert report["observations"] == [
        {
            "query_id": "q-001",
            "label": "synthetic_positive",
            "observed": True,
            "ranked_candidate_ids": ["candidate-1"],
            "latency_ms": 12.5,
        },
        {
            "query_id": "q-002",
            "label": "synthetic_absent",
            "observed": True,
            "ranked_candidate_ids": [],
            "latency_ms": 8.0,
        },
        {
            "query_id": "q-003",
            "label": "synthetic_unobserved",
            "observed": False,
            "status": "NOT_OBSERVED",
        },
    ]


def test_report_preserves_source_and_generation_identity():
    report = _build()

    assert report["identity"] == {
        "run_id": "pilot-run-001",
        "source": {
            "revision_id": "rev-synthetic-001",
            "source_sha256": "a" * 64,
        },
        "generation": {
            "generation_id": "gen-synthetic-001",
            "model_identity": "vip-fvs-fake-embedder",
            "invocation_ref": "invoke-synthetic-001",
        },
    }


def test_report_does_not_emit_classification_or_ranking_quality_metrics():
    report = _build()
    forbidden = {"precision", "recall", "mAP", "map", "f1", "auc", "accuracy"}

    def walk(value):
        if isinstance(value, dict):
            yield from value.keys()
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)

    assert not forbidden.intersection(walk(report))
    assert "quality_metrics" not in report


def test_missing_measurements_are_not_observed_and_never_zero_as_evidence():
    report = _build(measurements={"query_count_configured": 0, "wall_clock_ms": None})

    assert report["measurements"]["wall_clock_ms"] is None
    assert "wall_clock_ms" in report["NOT_OBSERVED"]
    assert report["summary"]["observed_query_count"] == 2
    assert report["summary"]["query_denominator"] == 2


def test_non_synthetic_report_requires_explicit_real_pilot_authorization():
    with pytest.raises((ValueError, TypeError)):
        _build(synthetic=False)
