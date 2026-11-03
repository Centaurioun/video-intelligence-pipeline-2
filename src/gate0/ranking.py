"""Deterministic, local-only cosine ranking for Gate-0."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence

from gate0.arms.semantic import RepresentationRecord


class RankingError(ValueError):
    """Raised when a representation cannot participate in deterministic ranking."""


@dataclass(frozen=True)
class RankedCandidate:
    candidate_id: str
    query_id: str
    representation_id: str
    score: float | None
    score_status: str
    rank: int | None
    tie_key: tuple[object, ...] | None
    coverage_status: str
    gold_accessed: bool = False


def _finite_vector(vector: Sequence[float], *, label: str) -> tuple[float, ...]:
    values = tuple(float(value) for value in vector)
    if not values or any(not math.isfinite(value) for value in values):
        raise RankingError(f"rank-eligible representation {label} has non-finite or empty vector")
    norm_sq = sum(value * value for value in values)
    if norm_sq == 0.0 or not math.isfinite(norm_sq):
        raise RankingError(f"rank-eligible representation {label} has ZERO_VECTOR")
    norm = math.sqrt(norm_sq)
    if not math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise RankingError(f"rank-eligible representation {label} is not normalized")
    return values


def _window_start(value: object) -> tuple[int, int]:
    if value is None:
        return (0, 1)
    numerator = getattr(value, "numerator", None)
    denominator = getattr(value, "denominator", None)
    if isinstance(value, tuple) and len(value) == 2:
        numerator, denominator = value
    if not isinstance(numerator, int) or not isinstance(denominator, int) or denominator <= 0:
        raise RankingError("window start must be a positive rational")
    divisor = math.gcd(abs(numerator), denominator)
    return (numerator // divisor, denominator // divisor)


def _cosine(query: tuple[float, ...], vector: tuple[float, ...]) -> float:
    if len(query) != len(vector):
        raise RankingError("query and representation dimensions differ")
    score = sum(left * right for left, right in zip(query, vector))
    if not math.isfinite(score):
        raise RankingError("cosine score is non-finite")
    return score


def rank_candidates(
    query_vector: Sequence[float],
    representations: Sequence[RepresentationRecord],
    *,
    query_id: str,
    vectors: Mapping[str, Sequence[float]] | None = None,
    window_starts: Mapping[str, object] | None = None,
) -> tuple[RankedCandidate, ...]:
    """Rank representation vectors without reading labels or external services.

    ``vectors`` is an explicit in-memory join keyed by representation ID. Failed
    representations remain status rows, while successful rows require a valid
    normalized float64 vector.
    """
    query = _finite_vector(query_vector, label="query")
    vector_map = vectors or {}
    starts = window_starts or {}
    seen: set[str] = set()
    scored: list[tuple[tuple[object, ...], RankedCandidate]] = []
    failed: list[RankedCandidate] = []
    for representation in representations:
        candidate_id = representation.representation_id
        if candidate_id in seen:
            raise RankingError(f"collision for candidate key {candidate_id}")
        seen.add(candidate_id)
        if representation.representation_status != "SUCCEEDED":
            failed.append(RankedCandidate(candidate_id, query_id, candidate_id, None,
                                          representation.representation_status, None, None,
                                          "FAILED", False))
            continue
        if candidate_id not in vector_map:
            raise RankingError(f"rank-eligible representation {candidate_id} has no vector")
        vector = _finite_vector(vector_map[candidate_id], label=candidate_id)
        score = _cosine(query, vector)
        start = _window_start(starts.get(candidate_id))
        # Bytes are deliberate: Python's Unicode ordering is not the contract.
        tie_key: tuple[object, ...] = (-score, representation.revision_id.encode("utf-8"),
                                       start, representation.window_id.encode("utf-8"),
                                       candidate_id.encode("utf-8"))
        scored.append((tie_key, RankedCandidate(candidate_id, query_id, candidate_id,
                                                score, "FINITE", None, tie_key,
                                                "SELECTED", False)))
    if len({item[0] for item in scored}) != len(scored):
        raise RankingError("collision in total ranking key")
    scored.sort(key=lambda item: item[0])
    ranked = [RankedCandidate(item.candidate_id, item.query_id, item.representation_id,
                              item.score, item.score_status, rank, item.tie_key,
                              item.coverage_status, False)
              for rank, (_, item) in enumerate(scored, 1)]
    return tuple(ranked + failed)
