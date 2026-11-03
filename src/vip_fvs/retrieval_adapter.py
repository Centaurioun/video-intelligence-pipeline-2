"""Functional-slice bridge to the pinned persistent local semantic index.

This module owns FVS orchestration and consumes the stable
``vip_fvs.semantic_index`` engine seam; indexing and ranking behavior remain in
the delegated engine. Fake embeddings are deterministic test/dev plumbing and
are never reported as measured model evidence.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

from .query_modality import (
    CapabilityLevel,
    ModalityAvailability,
    QueryEnvelope,
    QueryModality,
)

from vip_fvs.semantic_index import (
    PersistentLocalSemanticIndexEngine,
    SearchHit,
    SemanticIndexEngine,
    SemanticSpace,
)

_FAKE_EMBEDDING_DIM = 768
_FAKE_EMBEDDING_DTYPE = "float32"
_FAKE_TEXT_PREPROCESSING_CONTRACT = "padding=max_length"


@dataclass(frozen=True)
class RetrievalResult:
    """Query output plus immutable generation and invocation provenance."""

    generation_id: str
    space_id: str
    hits: tuple[SearchHit, ...]
    invocation_ref: str
    fake_embedder_used: bool


class UnsupportedModalityError(ValueError):
    """A declared query modality is not executable by this retrieval path."""


def _query_texts(query: str | Sequence[str] | QueryEnvelope) -> list[str]:
    """Validate an envelope before any runtime, index, or embedder operation."""
    if isinstance(query, QueryEnvelope):
        if query.modality is not QueryModality.TEXT:
            raise UnsupportedModalityError("UNSUPPORTED_QUERY_MODALITY")
        if (query.capability is not CapabilityLevel.EXECUTABLE
                or query.availability is not ModalityAvailability.AVAILABLE):
            raise UnsupportedModalityError("QUERY_MODALITY_NOT_EXECUTABLE")
        text = query.text
        if not isinstance(text, str) or not text.strip():
            raise ValueError("NO_QUERIES")
        return [text]
    return [str(query)] if isinstance(query, str) else [str(item) for item in query]


def _binding_value(binding: Any, name: str) -> Any:
    """Read a SourceBinding field while allowing the Task-1 object to evolve."""
    if isinstance(binding, dict):
        return binding[name]
    return getattr(binding, name)


def _fake_vector(value: str, *, salt: str) -> np.ndarray:
    """Generate a stable, normalized 768-D vector without model or I/O access."""
    # Expand a SHA-256 stream into exactly 768 float32 values.  The explicit
    # bytes-to-values mapping is stable across processes and Python versions.
    chunks = bytearray()
    counter = 0
    while len(chunks) < _FAKE_EMBEDDING_DIM * 4:
        chunks.extend(hashlib.sha256(f"vip-fvs-fake:{salt}:{value}:{counter}".encode()).digest())
        counter += 1
    raw = np.frombuffer(bytes(chunks[: _FAKE_EMBEDDING_DIM * 4]), dtype="<u4").astype(np.float32)
    values = (raw / np.float32(2**32 - 1)) * np.float32(2.0) - np.float32(1.0)
    norm = np.linalg.norm(values.astype(np.float64))
    return np.ascontiguousarray(values / norm, dtype=np.float32)


def fake_image_embedder(paths: Sequence[Path]) -> np.ndarray:
    """Deterministic image seam keyed by path text, not image/model contents."""
    values = [_fake_vector(str(Path(path)), salt="image") for path in paths]
    if not values:
        raise ValueError("NO_IMAGES")
    return np.stack(values).astype(np.float32)


def fake_text_embedder(texts: Sequence[str]) -> np.ndarray:
    """Deterministic text seam used only for local/synthetic execution."""
    values = [_fake_vector(str(text), salt="text") for text in texts]
    if not values:
        raise ValueError("NO_TEXTS")
    return np.stack(values).astype(np.float32)


def fake_semantic_space() -> SemanticSpace:
    """Return a visibly synthetic semantic-space identity for fake runs."""
    return SemanticSpace(
        model_identity="vip-fvs-fake-embedder",
        frozen_revision="synthetic-v1",
        weights_sha256="0" * 64,
        processor_digest="0" * 64,
        image_preprocessing_digest="0" * 64,
        text_preprocessing_contract=_FAKE_TEXT_PREPROCESSING_CONTRACT,
        embedding_dim=_FAKE_EMBEDDING_DIM,
        dtype=_FAKE_EMBEDDING_DTYPE,
        normalization="l2",
    )


def index_inputs(input_path, index_root, spec, image_embedder):
    """Compatibility hook delegating indexing through the stable engine seam.

    Existing synthetic FVS integration fixtures patch this module-level call
    point to avoid media I/O.  The implementation still lives behind
    ``SemanticIndexEngine``; this wrapper carries no engine details.
    """
    return PersistentLocalSemanticIndexEngine().index_source(
        input_path, index_root, spec, image_embedder
    )


def query_generation(index_root, spec, texts, text_embedder, *, top_k):
    """Compatibility hook delegating read-only queries through the seam."""
    return PersistentLocalSemanticIndexEngine().query(
        index_root, spec, texts, text_embedder, top_k=top_k
    )


class _DefaultFvsSemanticIndexEngine(PersistentLocalSemanticIndexEngine):
    """Default engine with compatibility call points for synthetic fixtures."""

    def index_source(self, input_path, index_root, spec, image_embedder):
        return index_inputs(input_path, index_root, spec, image_embedder)

    def query(self, index_root, spec, texts, text_embedder, *, top_k):
        return query_generation(index_root, spec, texts, text_embedder, top_k=top_k)


def retrieve(
    source_binding: Any,
    query: str | Sequence[str] | QueryEnvelope,
    index_root: Path,
    *,
    top_k: int = 5,
    fake_embedder: bool = False,
    image_embedder: Callable[[Sequence[Path]], np.ndarray] | None = None,
    text_embedder: Callable[[Sequence[str]], np.ndarray] | None = None,
    semantic_space: SemanticSpace | None = None,
    invocation_ref: str = "retrieval-invocation",
    engine: SemanticIndexEngine | None = None,
) -> RetrievalResult:
    """Index the bound local source and execute a read-only semantic query.

    ``source_binding`` is intentionally duck-typed to avoid coupling this lane
    to Task 1's final dataclass.  Its ``source_path`` is the authorized input;
    its digest is provenance owned by the binding and is not recomputed here.
    """
    # Refuse unsupported modalities before building a generation, consulting
    # source bindings, embedding, or touching the persistent index.
    texts = _query_texts(query)
    if top_k < 1:
        raise ValueError("INVALID_TOP_K")
    # An explicit semantic runtime is authoritative even if a compatibility
    # caller leaves the historical ``fake_embedder`` flag enabled.  Never
    # replace supplied real callables/space with the synthetic seam: doing so
    # would make the result provenance claim fake execution incorrectly.
    explicit_real = any(value is not None for value in (image_embedder, text_embedder, semantic_space))
    if explicit_real:
        if image_embedder is None or text_embedder is None:
            raise ValueError("EMBEDDERS_REQUIRED")
        if semantic_space is None:
            raise ValueError("SEMANTIC_SPACE_REQUIRED")
        fake_embedder = False
    elif not fake_embedder:
        raise ValueError("EMBEDDERS_REQUIRED")
    else:
        image_embedder = fake_image_embedder
        text_embedder = fake_text_embedder
        semantic_space = fake_semantic_space()
    assert image_embedder is not None and text_embedder is not None
    assert semantic_space is not None
    selected_engine = engine if engine is not None else _DefaultFvsSemanticIndexEngine()
    spec = selected_engine.build_generation_spec(semantic_space)
    source_path = Path(_binding_value(source_binding, "source_path"))
    selected_engine.index_source(source_path, Path(index_root), spec, image_embedder)
    raw = selected_engine.query(Path(index_root), spec, texts, text_embedder, top_k=top_k)
    hits = tuple(hit for text in texts for hit in raw[text])
    # SearchHit is copied only to attach the actual query key; all raw ranking,
    # score, temporal, and provenance fields remain untouched.
    return RetrievalResult(
        generation_id=spec.generation_id,
        space_id=spec.space_id,
        hits=hits,
        invocation_ref=str(invocation_ref),
        fake_embedder_used=bool(fake_embedder),
    )


__all__ = [
    "RetrievalResult",
    "UnsupportedModalityError",
    "fake_image_embedder",
    "fake_text_embedder",
    "fake_semantic_space",
    "retrieve",
]
