"""Small deterministic builders shared by local/synthetic FVS tests.

These helpers describe a test semantic space; they do not load a model, touch
the network, or imply that the synthetic identity is runtime evidence.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

from persistent_local_index.model_space import (
    EMBEDDING_DIM,
    EMBEDDING_DTYPE,
    TEXT_PREPROCESSING_CONTRACT,
    SemanticSpace,
    build_generation_spec,
)


_ZERO_DIGEST = "0" * 64


def make_model_contract(**overrides: Any) -> dict[str, Any]:
    """Return a stable local-only model contract for synthetic tests.

    The returned mapping intentionally mirrors the Gate-0 ``config.model``
    fields while making the synthetic/test status explicit.  Callers may
    override individual fields to exercise identity or compatibility checks.
    """
    contract: dict[str, Any] = {
        "semantic_arm_id": "vip-fvs-test-semantic-arm",
        "model_identity": "vip-fvs-test-embedder",
        "weights_digest": _ZERO_DIGEST,
        "processor_digest": _ZERO_DIGEST,
        "space_id": "NOT_OBSERVED",
        "dimension": EMBEDDING_DIM,
        "dtype": EMBEDDING_DTYPE,
        "offline_only": True,
        "provider_model_boundary": "local_only",
    }
    contract.update(overrides)
    return contract


def make_semantic_space(**overrides: Any) -> SemanticSpace:
    """Build a deterministic visibly synthetic :class:`SemanticSpace`."""
    values: dict[str, Any] = {
        "model_identity": "vip-fvs-test-embedder",
        "frozen_revision": "synthetic-v1",
        "weights_sha256": _ZERO_DIGEST,
        "processor_digest": _ZERO_DIGEST,
        "image_preprocessing_digest": _ZERO_DIGEST,
        "text_preprocessing_contract": TEXT_PREPROCESSING_CONTRACT,
        "embedding_dim": EMBEDDING_DIM,
        "dtype": EMBEDDING_DTYPE,
        "normalization": "l2",
    }
    values.update(overrides)
    return SemanticSpace(**values)


def make_generation_spec(**overrides: Any):
    """Build the deterministic generation contract for a test semantic space."""
    sampling_interval_seconds = overrides.pop("sampling_interval_seconds", 4.5)
    return build_generation_spec(
        make_semantic_space(**overrides),
        sampling_interval_seconds=sampling_interval_seconds,
    )


def deterministic_vector(seed: str, *, dimension: int = EMBEDDING_DIM) -> np.ndarray:
    """Return a reproducible normalized float32 pseudo-embedding."""
    digest = hashlib.sha256(str(seed).encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    vector = rng.standard_normal(int(dimension)).astype(np.float32)
    norm = np.linalg.norm(vector.astype(np.float64))
    if norm == 0:  # pragma: no cover - astronomically unlikely, but fail closed
        raise ValueError("ZERO_VECTOR")
    return np.ascontiguousarray(vector / np.float32(norm), dtype=np.float32)


def make_text_embedder(mapping: Mapping[str, np.ndarray] | None = None) -> Callable:
    """Create a deterministic text embedder with optional exact seed mapping."""
    supplied = dict(mapping or {})

    def embedder(texts) -> np.ndarray:
        rows = [supplied.get(str(text), deterministic_vector(str(text))) for text in texts]
        if not rows:
            raise ValueError("NO_TEXTS")
        return np.stack(rows).astype(np.float32)

    return embedder


def make_image_embedder() -> Callable:
    """Create a deterministic image embedder keyed to exact file bytes."""

    def embedder(paths) -> np.ndarray:
        rows = []
        for path in paths:
            digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            rows.append(deterministic_vector(digest))
        if not rows:
            raise ValueError("NO_IMAGES")
        return np.stack(rows).astype(np.float32)

    return embedder


__all__ = [
    "deterministic_vector",
    "make_generation_spec",
    "make_image_embedder",
    "make_model_contract",
    "make_semantic_space",
    "make_text_embedder",
]
