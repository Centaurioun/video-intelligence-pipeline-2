"""Offline embedding seam used by Gate-0 synthetic tests.

This module intentionally has no provider, network, or model-loading path.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class EmbeddingResult:
    vector: tuple[float, ...] | None
    status: str = "SUCCESS"
    failure_reason: str | None = None


class EmbeddingAdapter:
    """Explicit local seam; implementations must not add fallback behavior."""

    def embed(self, kind: str, value: Any) -> EmbeddingResult:
        raise NotImplementedError


class FakeEmbeddingAdapter(EmbeddingAdapter):
    def __init__(self, vectors: Mapping[Any, tuple[float, ...]]):
        self._vectors = dict(vectors)
        self.provider_calls = 0

    def embed(self, kind: str, value: Any) -> EmbeddingResult:
        vector = self._vectors.get(value, self._vectors.get(kind))
        if vector is None:
            return EmbeddingResult(None, "FAILED", "MISSING_FAKE_VECTOR")
        return EmbeddingResult(tuple(float(v) for v in vector))


def normalize_vector(vector: tuple[float, ...] | list[float]) -> tuple[float, ...]:
    import math

    values = tuple(float(v) for v in vector)
    if not values or any(not math.isfinite(v) for v in values):
        raise ValueError("NON_FINITE")
    norm = math.sqrt(sum(v * v for v in values))
    if norm == 0.0:
        raise ValueError("ZERO_VECTOR")
    return tuple(v / norm for v in values)
