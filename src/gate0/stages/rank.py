"""Stage adapter for deterministic local ranking."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from gate0.arms.semantic import RepresentationRecord
from gate0.ranking import RankedCandidate, rank_candidates


def run_rank(query_vector: Sequence[float], representations: Sequence[RepresentationRecord], *, query_id: str, vectors: Mapping[str, Sequence[float]], window_starts: Mapping[str, object] | None = None) -> tuple[RankedCandidate, ...]:
    return rank_candidates(query_vector, representations, query_id=query_id, vectors=vectors, window_starts=window_starts)
