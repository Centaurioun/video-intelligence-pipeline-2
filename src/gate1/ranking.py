"""Deterministic, label-free, arm-local exact vector ranking."""
from __future__ import annotations

import math
from collections.abc import Sequence

from gate1.contracts.types import EmbeddingRecord, RankedCandidate

NORMALIZATION_TOLERANCE = 1e-9
_FAILED_PROVIDER_STATES = frozenset({"FAILED", "PARTIAL"})


class RankingError(ValueError):
    """Raised when ranking inputs are not admissible under the Gate-1 contract."""


def _admissible_vector(record: EmbeddingRecord, role: str) -> tuple[float, ...] | None:
    vector = record.payload.vector
    if vector is None:
        return None
    if not vector:
        raise RankingError(f"{role} vector for {record.payload.representation_id} is empty")
    values: list[float] = []
    for value in vector:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RankingError(f"{role} vector for {record.payload.representation_id} is not numeric")
        number = float(value)
        if not math.isfinite(number):
            raise RankingError(f"{role} vector for {record.payload.representation_id} has a non-finite value")
        values.append(number)
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0.0:
        raise RankingError(f"{role} vector for {record.payload.representation_id} is zero")
    if abs(norm - 1.0) > NORMALIZATION_TOLERANCE:
        raise RankingError(f"{role} vector for {record.payload.representation_id} is not L2-normalized")
    return tuple(values)


def _candidate_failure_status(candidate: EmbeddingRecord) -> str:
    """Map an absent vector to an attributable failure or omission coverage row."""
    if (
        candidate.payload.failure_reason
        or candidate.envelope.provider_status in _FAILED_PROVIDER_STATES
        or candidate.envelope.per_item_errors
    ):
        return "FAILED"
    return "OMITTED"


def rank_arm(
    query: EmbeddingRecord,
    candidates: Sequence[EmbeddingRecord],
) -> tuple[RankedCandidate, ...]:
    """Rank candidates for one query within its canonical arm and space.

    This function accepts candidate-production records only and has no judgment
    or label input. Missing candidate vectors stay visible as FAILED or OMITTED
    rows, without an invented score or rank.
    """
    if query.payload.kind != "query":
        raise RankingError("query record must have kind='query'")
    query_arm = query.envelope.arm_id
    query_space = query.payload.space_id
    query_id = query.payload.query_id
    if not isinstance(query_id, str) or not query_id:
        raise RankingError("query record must declare a query_id")

    query_vector = _admissible_vector(query, "query")
    if query_vector is None:
        raise RankingError(f"query {query_id} has no vector and cannot rank")

    scored: list[tuple[float, bytes, EmbeddingRecord]] = []
    uncovered: list[RankedCandidate] = []
    seen_candidate_ids: set[str] = set()

    for candidate in candidates:
        if candidate.payload.kind != "candidate":
            raise RankingError("candidate record must have kind='candidate'")
        if candidate.envelope.arm_id != query_arm:
            raise RankingError(
                f"candidate arm {candidate.envelope.arm_id!r} differs from query arm {query_arm!r}"
            )
        if candidate.payload.space_id != query_space:
            raise RankingError(
                f"candidate space {candidate.payload.space_id!r} differs from query space "
                f"{query_space!r}; cross-space scoring is refused"
            )
        candidate_id = candidate.payload.candidate_id
        if not isinstance(candidate_id, str) or not candidate_id:
            raise RankingError("candidate records must declare a non-empty candidate_id")
        if candidate_id in seen_candidate_ids:
            raise RankingError(f"duplicate candidate_id {candidate_id!r}")
        seen_candidate_ids.add(candidate_id)

        vector = _admissible_vector(candidate, "candidate")
        if vector is None:
            uncovered.append(
                RankedCandidate(
                    record_id=f"rank-{query_arm}-{query_id}-{candidate_id}",
                    arm_id=query_arm,
                    query_id=query_id,
                    candidate_id=candidate_id,
                    representation_id=candidate.payload.representation_id,
                    space_id=candidate.payload.space_id,
                    score=None,
                    rank=None,
                    tie_key=None,
                    coverage_status=_candidate_failure_status(candidate),
                )
            )
            continue

        if len(vector) != len(query_vector):
            raise RankingError("query and candidate vectors have different dimensions")
        score = sum(left * right for left, right in zip(query_vector, vector))
        scored.append((score, candidate_id.encode("utf-8"), candidate))

    scored.sort(key=lambda item: (-item[0], item[1]))
    ranked = [
        RankedCandidate(
            record_id=f"rank-{query_arm}-{query_id}-{candidate.payload.candidate_id}",
            arm_id=query_arm,
            query_id=query_id,
            candidate_id=candidate.payload.candidate_id,
            representation_id=candidate.payload.representation_id,
            space_id=candidate.payload.space_id,
            score=score,
            rank=position,
            tie_key=(-score, candidate_key),
            coverage_status="SELECTED",
        )
        for position, (score, candidate_key, candidate) in enumerate(scored, start=1)
    ]
    uncovered.sort(key=lambda row: row.candidate_id.encode("utf-8"))
    return tuple(ranked + uncovered)
