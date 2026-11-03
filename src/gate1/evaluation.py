"""Deterministic post-production evaluation for one frozen comparison."""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from gate1.contracts.types import (
    BenchmarkReport,
    ComparisonContract,
    Judgment,
    RankedCandidate,
)

VALID_VALIDITY = "VALID"
INVALID_VALIDITY = "INVALID_PROTOCOL"
_COVERAGE_STATES = ("SELECTED", "FAILED", "OMITTED", "QUARANTINED")
_RESOURCE_FAILURE = "RESOURCE_OPERABILITY"


class EvaluationError(ValueError):
    """Raised when the frozen metric configuration cannot be evaluated."""


def _metric_settings(contract: ComparisonContract) -> tuple[str, int, float, bool]:
    metric = contract.primary_metric
    try:
        metric_id = metric["metric_id"]
        k_value = metric["k"]
        threshold = metric["min_delta"]
    except (KeyError, TypeError) as exc:
        raise EvaluationError(
            "primary_metric must declare metric_id, k, and min_delta"
        ) from exc
    if not isinstance(metric_id, str) or not metric_id.strip():
        raise EvaluationError("primary_metric.metric_id must be a non-empty string")
    if isinstance(k_value, bool) or not isinstance(k_value, int) or k_value < 1:
        raise EvaluationError("primary_metric.k must be a positive integer")
    if isinstance(threshold, bool):
        raise EvaluationError("primary_metric.min_delta must be finite numeric")
    try:
        min_delta = float(threshold)
    except (TypeError, ValueError) as exc:
        raise EvaluationError("primary_metric.min_delta must be finite numeric") from exc
    if not math.isfinite(min_delta):
        raise EvaluationError("primary_metric.min_delta must be finite numeric")
    if len(contract.arm_ids) != 2 or contract.arm_ids[0] == contract.arm_ids[1]:
        raise EvaluationError("comparison must declare two distinct arms")
    return metric_id, k_value, min_delta, bool(metric.get("require_complete_coverage", False))


def _validate_query_ids(
    query_ids: Sequence[str],
    rankings_by_arm: Mapping[str, Sequence[RankedCandidate]],
    arm_ids: Sequence[str],
    judgments: Sequence[Judgment],
) -> tuple[str, ...]:
    if isinstance(query_ids, (str, bytes)) or not isinstance(query_ids, Sequence):
        raise EvaluationError("query_ids must be the frozen query-id sequence")
    if not query_ids or any(
        not isinstance(query_id, str) or not query_id for query_id in query_ids
    ):
        raise EvaluationError("query_ids must contain non-empty query IDs")
    if len(set(query_ids)) != len(query_ids):
        raise EvaluationError("query_ids must be unique")
    frozen = set(query_ids)
    observed = {
        row.query_id
        for arm_id in arm_ids
        for row in rankings_by_arm.get(arm_id, ())
    }
    observed.update(judgment.query_id for judgment in judgments)
    outside = observed - frozen
    if outside:
        raise EvaluationError(
            f"rankings or judgments contain query IDs outside the frozen set: {sorted(outside)}"
        )
    return tuple(sorted(query_ids))


def _coverage(
    rankings_by_arm: Mapping[str, Sequence[RankedCandidate]],
    arm_ids: Sequence[str],
    query_ids: Sequence[str],
) -> tuple[dict[str, int], bool]:
    counts: dict[str, int] = {}
    incomplete = False
    for arm_id in arm_ids:
        rows = rankings_by_arm.get(arm_id, ())
        for row in rows:
            if row.arm_id != arm_id:
                raise EvaluationError(
                    f"ranking row arm_id {row.arm_id!r} does not match arm {arm_id!r}"
                )
            if row.coverage_status == "SELECTED":
                if (
                    isinstance(row.rank, bool)
                    or not isinstance(row.rank, int)
                    or row.rank < 1
                ):
                    raise EvaluationError(
                        f"SELECTED ranking row must have a positive integer rank: {row.record_id}"
                    )
                if (
                    isinstance(row.score, bool)
                    or not isinstance(row.score, (int, float))
                    or not math.isfinite(float(row.score))
                ):
                    raise EvaluationError(
                        f"SELECTED ranking row must have a finite score: {row.record_id}"
                    )
            elif row.rank is not None or row.score is not None:
                raise EvaluationError(
                    f"{row.coverage_status} ranking row must have null rank and score: "
                    f"{row.record_id}"
                )
        arm_counts = Counter(row.coverage_status for row in rows)
        unknown = set(arm_counts) - set(_COVERAGE_STATES)
        if unknown:
            raise EvaluationError(
                f"unsupported coverage status for {arm_id}: {', '.join(sorted(unknown))}"
            )
        for status in _COVERAGE_STATES:
            count = arm_counts.get(status, 0)
            counts[f"{arm_id}::{status}"] = count
            if status != "SELECTED" and count:
                incomplete = True
        ranked_queries = {row.query_id for row in rows}
        missing_query_count = sum(query_id not in ranked_queries for query_id in query_ids)
        if missing_query_count:
            counts[f"{arm_id}::OMITTED"] += missing_query_count
            incomplete = True
    return counts, incomplete


def _query_hit_at_k(
    rows: Sequence[RankedCandidate],
    query_id: str,
    relevant: frozenset[tuple[str, str]],
    k: int,
) -> float:
    return float(
        any(
            row.query_id == query_id
            and row.coverage_status == "SELECTED"
            and isinstance(row.rank, int)
            and not isinstance(row.rank, bool)
            and 1 <= row.rank <= k
            and (row.query_id, row.candidate_id) in relevant
            for row in rows
        )
    )


def _macro_hit_at_k(
    rows: Sequence[RankedCandidate],
    query_ids: Sequence[str],
    relevant: frozenset[tuple[str, str]],
    k: int,
) -> float:
    if not query_ids:
        raise EvaluationError("comparison rankings must include at least one query")
    return sum(_query_hit_at_k(rows, query_id, relevant, k) for query_id in query_ids) / len(
        query_ids
    )


def _has_resource_failure(
    failures: Sequence[Mapping[str, Any]], synthetic_fault: str
) -> bool:
    return synthetic_fault == _RESOURCE_FAILURE or any(
        failure.get("event_type") == _RESOURCE_FAILURE for failure in failures
    )


def evaluate_comparison(
    contract: ComparisonContract,
    rankings_by_arm: Mapping[str, Sequence[RankedCandidate]],
    judgments: Sequence[Judgment],
    failures: Sequence[Mapping[str, Any]],
    *,
    query_ids: Sequence[str],
    protocol_validity: str = VALID_VALIDITY,
    synthetic_fault: str = "NONE",
) -> BenchmarkReport:
    """Evaluate completed rankings against judgments and a frozen query universe."""
    metric_id, k, min_delta, require_complete = _metric_settings(contract)
    query_ids = _validate_query_ids(
        query_ids, rankings_by_arm, contract.arm_ids, judgments
    )
    coverage, coverage_incomplete = _coverage(
        rankings_by_arm, contract.arm_ids, query_ids
    )

    if protocol_validity != VALID_VALIDITY:
        return BenchmarkReport(
            comparison_id=contract.comparison_id,
            validity=INVALID_VALIDITY,
            benchmark_status=INVALID_VALIDITY,
            primary_metric_id=metric_id,
            primary_value=None,
            arm_values={},
            coverage=coverage,
            failure_class=None,
            conclusion="COMPARISON_INVALID_NO_OUTCOME_CLAIM",
        )

    relevant = frozenset(
        (judgment.query_id, judgment.candidate_id)
        for judgment in judgments
        if judgment.relevant
    )
    arm_values = {
        arm_id: _macro_hit_at_k(
            rankings_by_arm.get(arm_id, ()), query_ids, relevant, k
        )
        for arm_id in contract.arm_ids
    }
    delta = arm_values[contract.arm_ids[1]] - arm_values[contract.arm_ids[0]]

    # Failure precedence is protocol validity, resource operability, required
    # coverage, then the configured metric threshold.
    if _has_resource_failure(failures, synthetic_fault):
        failure_class = _RESOURCE_FAILURE
        conclusion = "SYNTHETIC_VALID_NEGATIVE_EVIDENCE"
    elif require_complete and coverage_incomplete:
        failure_class = "COVERAGE_INCOMPLETE"
        conclusion = "SYNTHETIC_VALID_NEGATIVE_EVIDENCE"
    elif delta >= min_delta:
        failure_class = None
        conclusion = "SYNTHETIC_DELTA_MEETS_CONFIGURED_THRESHOLD"
    else:
        failure_class = "QUALITY"
        conclusion = "SYNTHETIC_DELTA_BELOW_CONFIGURED_THRESHOLD"

    return BenchmarkReport(
        comparison_id=contract.comparison_id,
        validity=VALID_VALIDITY,
        benchmark_status="PASS" if failure_class is None else "FAIL",
        primary_metric_id=metric_id,
        primary_value=delta,
        arm_values=arm_values,
        coverage=coverage,
        failure_class=failure_class,
        conclusion=conclusion,
    )
