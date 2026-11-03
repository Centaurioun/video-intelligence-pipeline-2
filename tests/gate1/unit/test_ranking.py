"""Deterministic, label-free Gate-1 arm ranking contracts."""
from __future__ import annotations

import pytest

from gate1.contracts.types import BenchmarkEnvelope, EmbeddingPayload, EmbeddingRecord
from gate1.ranking import RankingError, rank_arm


def _record(
    arm: str,
    key: str,
    vector: tuple[float, ...] | None,
    *,
    kind: str,
    space: str | None = None,
    failure_reason: str | None = None,
    provider_status: str = "SUCCESS",
    absence_reason: str | None = None,
) -> EmbeddingRecord:
    space_id = space or f"space-{arm}"
    envelope = BenchmarkEnvelope(
        record_id=f"env-{arm}-{key}",
        comparison_id="cmp-synthetic",
        run_id="run-synthetic",
        attempt_id="attempt-1",
        arm_id=arm,
        input_refs=(f"input-{key}",),
        consumed_coverage={},
        raw_response_artifact_ref=None,
        absence_reason=absence_reason,
        requested_model="synthetic",
        resolved_backend="NOT_OBSERVED",
        config_digest="0" * 64,
        policy_decision_id="synthetic-policy",
        request_ref=None,
        judgment_version_refs=(),
        resource_observations={},
        validity_ref=None,
        outcome_ref=None,
        provider_status=provider_status,
        per_item_errors=(failure_reason,) if failure_reason else (),
        wall_time_ms=None,
    )
    payload = EmbeddingPayload(
        space_id=space_id,
        representation_id=f"rep-{key}",
        query_id=key if kind == "query" else None,
        candidate_id=key if kind == "candidate" else None,
        kind=kind,
        vector=vector,
        failure_reason=failure_reason,
    )
    return EmbeddingRecord(envelope=envelope, payload=payload)


def test_rank_arm_orders_cosine_scores_and_breaks_ties_by_utf8_candidate_id():
    query = _record("arm-a", "q1", (1.0, 0.0), kind="query")
    candidates = (
        _record("arm-a", "z", (1.0, 0.0), kind="candidate"),
        _record("arm-a", "b", (1.0, 0.0), kind="candidate"),
        _record("arm-a", "c", (0.0, 1.0), kind="candidate"),
    )

    rows = rank_arm(query, candidates)

    assert [(r.candidate_id, r.score, r.rank, r.tie_key) for r in rows] == [
        ("b", 1.0, 1, (-1.0, b"b")),
        ("z", 1.0, 2, (-1.0, b"z")),
        ("c", 0.0, 3, (0.0, b"c")),
    ]


@pytest.mark.parametrize(
    "bad_vector",
    [(), (0.0, 0.0), (float("nan"), 1.0), (float("inf"), 0.0), (1.0, 1.0)],
)
def test_rank_arm_rejects_empty_zero_nonfinite_and_non_normalized_vectors(bad_vector):
    query = _record("arm-a", "q1", (1.0, 0.0), kind="query")
    candidate = _record("arm-a", "c1", bad_vector, kind="candidate")

    with pytest.raises(RankingError):
        rank_arm(query, (candidate,))


def test_rank_arm_refuses_cross_arm_and_cross_space_scoring():
    query = _record("arm-a", "q1", (1.0, 0.0), kind="query")
    other_arm = _record("arm-b", "c1", (1.0, 0.0), kind="candidate")
    wrong_space = _record("arm-a", "c2", (1.0, 0.0), kind="candidate", space="space-other")

    with pytest.raises(RankingError, match="arm"):
        rank_arm(query, (other_arm,))
    with pytest.raises(RankingError, match="space"):
        rank_arm(query, (wrong_space,))


def test_rank_arm_rejects_dimension_mismatch_instead_of_truncating_dot_product():
    query = _record("arm-a", "q1", (1.0, 0.0), kind="query")
    candidate = _record("arm-a", "c1", (0.0, 0.0, 1.0), kind="candidate")

    with pytest.raises(RankingError, match="dimension"):
        rank_arm(query, (candidate,))


def test_missing_vector_candidates_remain_failed_or_omitted_rows_without_rank():
    query = _record("arm-a", "q1", (1.0, 0.0), kind="query")
    good = _record("arm-a", "c1", (1.0, 0.0), kind="candidate")
    failed = _record(
        "arm-a", "c2", None, kind="candidate", failure_reason="ENCODING_ERROR", provider_status="FAILED"
    )
    omitted = _record(
        "arm-a", "c3", None, kind="candidate", provider_status="UNSUPPORTED",
        absence_reason="NOT_PRODUCED",
    )

    rows = rank_arm(query, (good, failed, omitted))

    assert len(rows) == 3
    by_id = {r.candidate_id: r for r in rows}
    assert by_id["c1"].coverage_status == "SELECTED"
    for candidate_id, status in (("c2", "FAILED"), ("c3", "OMITTED")):
        row = by_id[candidate_id]
        assert row.coverage_status == status
        assert (row.score, row.rank, row.tie_key) == (None, None, None)


def test_rank_arm_rejects_duplicate_candidate_identity():
    query = _record("arm-a", "q1", (1.0, 0.0), kind="query")
    first = _record("arm-a", "c1", (1.0, 0.0), kind="candidate")
    duplicate = _record("arm-a", "c1", (0.0, 1.0), kind="candidate")

    with pytest.raises(RankingError, match="duplicate"):
        rank_arm(query, (first, duplicate))
