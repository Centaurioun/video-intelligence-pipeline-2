from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from gate1.contracts.types import Judgment, RankedCandidate
from gate1.evaluation import EvaluationError, evaluate_comparison


def _contract(*, min_delta: float = 0.5, complete: bool = False):
    return SimpleNamespace(
        comparison_id="cmp-synthetic",
        arm_ids=("arm-a", "arm-b"),
        estimand="query_macro_hit_at_k_delta",
        primary_metric={
            "metric_id": "query_macro_hit_at_1",
            "k": 1,
            "min_delta": min_delta,
            "require_complete_coverage": complete,
        },
    )


def _row(arm: str, query: str, candidate: str, rank: int | None,
         coverage: str = "SELECTED") -> RankedCandidate:
    return RankedCandidate(
        record_id=f"{arm}-{query}-{candidate}", arm_id=arm, query_id=query,
        candidate_id=candidate, representation_id=f"rep-{arm}",
        space_id=f"space-{arm}", score=1.0 if rank == 1 else 0.0 if rank else None,
        rank=rank, tie_key=(rank, candidate) if rank else None,
        coverage_status=coverage,
    )


def _rankings():
    return {
        "arm-a": (
            _row("arm-a", "q1", "c1", 1),
            _row("arm-a", "q1", "c2", 2),
            _row("arm-a", "q2", "c1", 1),
            _row("arm-a", "q2", "c2", 2),
        ),
        "arm-b": (
            _row("arm-b", "q1", "c1", 1),
            _row("arm-b", "q1", "c2", 2),
            _row("arm-b", "q2", "c1", 2),
            _row("arm-b", "q2", "c2", 1),
        ),
    }


def _judgments():
    return (
        Judgment("j1", "q1", "c1", True, "synthetic-reviewer", True, "MATCHED"),
        Judgment("j2", "q2", "c2", True, "synthetic-reviewer", True, "MATCHED"),
    )


def _evaluate(contract, rankings, judgments, failures, *, query_ids=("q1", "q2"), **kwargs):
    return evaluate_comparison(
        contract, rankings, judgments, failures, query_ids=query_ids, **kwargs
    )


def test_query_macro_hit_at_k_uses_configured_metric_and_reports_delta():
    report = _evaluate(_contract(), _rankings(), _judgments(), ())
    assert report.validity == "VALID"
    assert report.benchmark_status == "PASS"
    assert report.primary_metric_id == "query_macro_hit_at_1"
    assert report.arm_values == pytest.approx({"arm-a": 0.5, "arm-b": 1.0})
    assert report.primary_value == pytest.approx(0.5)
    assert report.conclusion == "SYNTHETIC_DELTA_MEETS_CONFIGURED_THRESHOLD"


def test_invalid_protocol_suppresses_all_outcome_values():
    report = _evaluate(
        _contract(), _rankings(), _judgments(), (), protocol_validity="INVALID_PROTOCOL"
    )
    assert report.validity == "INVALID_PROTOCOL"
    assert report.benchmark_status == "INVALID_PROTOCOL"
    assert report.primary_value is None
    assert report.arm_values == {}
    assert report.conclusion == "COMPARISON_INVALID_NO_OUTCOME_CLAIM"


def test_coverage_counts_are_attributable_by_arm_and_status():
    rankings = _rankings()
    rankings["arm-a"] += (
        _row("arm-a", "q1", "c3", None, "FAILED"),
        _row("arm-a", "q2", "c4", None, "OMITTED"),
        _row("arm-a", "q2", "c5", None, "QUARANTINED"),
    )
    report = _evaluate(_contract(complete=True), rankings, _judgments(), ())
    assert report.coverage == {
        "arm-a::SELECTED": 4,
        "arm-a::FAILED": 1,
        "arm-a::OMITTED": 1,
        "arm-a::QUARANTINED": 1,
        "arm-b::SELECTED": 4,
        "arm-b::FAILED": 0,
        "arm-b::OMITTED": 0,
        "arm-b::QUARANTINED": 0,
    }
    assert report.validity == "VALID"
    assert report.benchmark_status == "FAIL"
    assert report.failure_class == "COVERAGE_INCOMPLETE"


def test_resource_failure_precedes_required_coverage_failure():
    rankings = _rankings()
    rankings["arm-a"] += (_row("arm-a", "q1", "c3", None, "FAILED"),)
    report = _evaluate(
        _contract(complete=True), rankings, _judgments(),
        ({"event_type": "RESOURCE_OPERABILITY"},),
    )
    assert report.validity == "VALID"
    assert report.benchmark_status == "FAIL"
    assert report.failure_class == "RESOURCE_OPERABILITY"


def test_equal_arm_quality_is_valid_negative_synthetic_evidence():
    rankings = _rankings()
    rankings["arm-b"] = tuple(
        _row("arm-b", q, candidate, rank)
        for q, candidate, rank in (
            ("q1", "c1", 1), ("q1", "c2", 2), ("q2", "c1", 1), ("q2", "c2", 2)
        )
    )
    report = _evaluate(_contract(), rankings, _judgments(), ())
    assert report.validity == "VALID"
    assert report.benchmark_status == "FAIL"
    assert report.failure_class == "QUALITY"
    assert report.primary_value == pytest.approx(0.0)
    assert report.conclusion == "SYNTHETIC_DELTA_BELOW_CONFIGURED_THRESHOLD"


def test_query_absent_from_both_arm_rankings_remains_in_macro_denominator():
    report = _evaluate(
        _contract(min_delta=0.4), _rankings(), _judgments(), (), query_ids=("q1", "q2", "q3")
    )

    assert report.arm_values == pytest.approx({"arm-a": 1 / 3, "arm-b": 2 / 3})
    assert report.primary_value == pytest.approx(1 / 3)
    assert report.validity == "VALID"
    assert report.benchmark_status == "FAIL"
    assert report.failure_class == "QUALITY"
    assert report.coverage["arm-a::OMITTED"] == 1
    assert report.coverage["arm-b::OMITTED"] == 1


def test_query_rows_outside_frozen_universe_are_rejected():
    with pytest.raises(EvaluationError, match="outside the frozen set"):
        _evaluate(_contract(), _rankings(), _judgments(), (), query_ids=("q1",))


def test_status_namespace_and_evaluator_source_have_no_production_adapter_path():
    from gate1.contracts.types import BENCHMARK_STATUSES

    report = _evaluate(_contract(), _rankings(), _judgments(), ())
    assert report.benchmark_status in BENCHMARK_STATUSES
    assert not {"WINNER", "PROMOTED", "SELECTED"} & BENCHMARK_STATUSES
    source = Path(__file__).resolve().parents[3] / "src" / "gate1" / "evaluation.py"
    text = source.read_text(encoding="utf-8")
    assert "gate1.adapters" not in text
    assert "gate1.ranking" not in text
    assert "provider" not in text.lower()


def test_selected_coverage_requires_a_real_positive_rank():
    rankings = _rankings()
    rankings["arm-a"] = (_row("arm-a", "q1", "c1", None),)
    with pytest.raises(EvaluationError, match="SELECTED.*rank"):
        _evaluate(_contract(), rankings, _judgments(), ())


def test_nonselected_coverage_cannot_contribute_a_rank_or_score():
    rankings = _rankings()
    rankings["arm-a"] = (_row("arm-a", "q1", "c1", 1, "FAILED"),)
    with pytest.raises(EvaluationError, match="FAILED.*rank and score"):
        _evaluate(_contract(), rankings, _judgments(), ())
