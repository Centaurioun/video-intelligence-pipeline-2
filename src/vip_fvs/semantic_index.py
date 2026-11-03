"""Stable product-facing boundary for persistent local semantic indexing."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol, Sequence, runtime_checkable

import numpy as np

from persistent_local_index import indexer, model_space, search
from persistent_local_index.indexer import IndexSummary
from persistent_local_index.model_space import GenerationSpec, SemanticSpace
from persistent_local_index.search import SearchHit


ImageEmbedder = Callable[[Sequence[Path]], np.ndarray]
TextEmbedder = Callable[[Sequence[str]], np.ndarray]


@runtime_checkable
class SemanticIndexEngine(Protocol):
    """Injectable API for generation identity, one-source indexing, and query."""

    def build_generation_spec(self, space: SemanticSpace) -> GenerationSpec: ...

    def index_source(
        self, input_path: Path, index_root: Path, spec: GenerationSpec,
        image_embedder: ImageEmbedder,
    ) -> IndexSummary: ...

    def query(
        self, index_root: Path, spec: GenerationSpec, texts: Sequence[str],
        text_embedder: TextEmbedder, *, top_k: int,
    ) -> dict[str, tuple[SearchHit, ...]]: ...


class PersistentLocalSemanticIndexEngine:
    """Delegate the stable interface to the existing persistent engine."""

    def build_generation_spec(self, space: SemanticSpace) -> GenerationSpec:
        return model_space.build_generation_spec(space)

    def index_source(
        self, input_path: Path, index_root: Path, spec: GenerationSpec,
        image_embedder: ImageEmbedder,
    ) -> IndexSummary:
        return indexer.index_inputs(input_path, index_root, spec, image_embedder)

    def query(
        self, index_root: Path, spec: GenerationSpec, texts: Sequence[str],
        text_embedder: TextEmbedder, *, top_k: int,
    ) -> dict[str, tuple[SearchHit, ...]]:
        return search.query_generation(index_root, spec, texts, text_embedder, top_k=top_k)


__all__ = [
    "GenerationSpec", "IndexSummary", "SearchHit", "SemanticIndexEngine",
    "SemanticSpace", "PersistentLocalSemanticIndexEngine",
]
