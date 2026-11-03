"""Read-only multi-source query with exact manifest provenance binding."""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from . import local_semantic
from .semantic_index import SemanticIndexEngine, SemanticSpace
from .source_adapter import MultiSourceManifest, SourceManifestEntry


@dataclass(frozen=True)
class MultiSourceRetrievalCandidate:
    """A ranked semantic match tied to one exact manifest occurrence.

    PTS and timebase identify a source-native sample locator. They are not an
    interval or an edit boundary, and the candidate is never binding eligible.
    """

    query: str
    rank: int
    score: float
    revision_id: str
    content_id: str
    source_path: str
    source_sha256: str
    generation_id: str
    space_id: str
    source_sample_pts: int
    source_timebase_num: int
    source_timebase_den: int
    timestamp_human: str
    thumbnail_path: str | None
    thumbnail_status: str
    evidence_class: str = "MATCHED"
    binding_eligible: bool = False


@dataclass(frozen=True)
class MultiSourceRetrievalResult:
    """Immutable identity and ordered candidate set for one multi-source query."""

    manifest_digest: str
    generation_id: str
    space_id: str
    candidates: tuple[MultiSourceRetrievalCandidate, ...]


def _bind_hit(hit: object, manifest: MultiSourceManifest) -> SourceManifestEntry:
    locator = getattr(hit, "source_path", None)
    digest = getattr(hit, "source_sha256", None)
    if not isinstance(locator, (str, Path)) or not isinstance(digest, str):
        raise ValueError("MULTI_SOURCE_HIT_PROVENANCE_REQUIRED")

    # Keep the locator spelling exact: resolving paths would collapse distinct
    # occurrence identities and could bind a hit to a different manifest row.
    matches = tuple(
        entry for entry in manifest.entries
        if str(entry.source_path) == str(locator) and entry.source_sha256 == digest
    )
    if len(matches) != 1:
        raise ValueError("MULTI_SOURCE_HIT_MANIFEST_BINDING_FAILED")
    return matches[0]


def retrieve_multi_source(
    index_root: str | Path,
    manifest: MultiSourceManifest,
    query: str | Sequence[str],
    *,
    runtime: local_semantic.CheckedLocalSemanticRuntime,
    semantic_space: SemanticSpace,
    engine: SemanticIndexEngine,
    top_k: int = 5,
) -> MultiSourceRetrievalResult:
    """Query the current semantic generation and bind every hit to ``manifest``.

    The only index access is the established read-only ``engine.query`` seam.
    This function does not touch source paths or invoke indexing/media tools.
    """
    if not isinstance(manifest, MultiSourceManifest):
        raise TypeError("manifest must be MultiSourceManifest")
    if not isinstance(runtime, local_semantic.CheckedLocalSemanticRuntime):
        raise ValueError("CHECKED_RUNTIME_REQUIRED")
    if not isinstance(semantic_space, SemanticSpace):
        raise ValueError("SEMANTIC_SPACE_REQUIRED")
    if semantic_space != runtime.semantic_space:
        raise ValueError("SEMANTIC_SPACE_RUNTIME_MISMATCH")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("INVALID_TOP_K")
    texts = [query] if isinstance(query, str) else list(query)
    if not texts or any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("NO_QUERIES")
    if not callable(getattr(engine, "build_generation_spec", None)) or not callable(
        getattr(engine, "query", None)
    ):
        raise ValueError("ENGINE_QUERY_REQUIRED")

    spec = engine.build_generation_spec(semantic_space)
    if getattr(spec, "space", None) != semantic_space:
        raise ValueError("GENERATION_SEMANTIC_SPACE_MISMATCH")
    generation_id = getattr(spec, "generation_id", None)
    space_id = getattr(spec, "space_id", None)
    if not isinstance(generation_id, str) or not generation_id:
        raise ValueError("ENGINE_GENERATION_ID_MISSING")
    if not isinstance(space_id, str) or not space_id:
        raise ValueError("ENGINE_SPACE_ID_MISSING")

    by_query = engine.query(
        Path(index_root), spec, texts, runtime.text_embedder, top_k=top_k
    )
    candidates: list[MultiSourceRetrievalCandidate] = []
    for text in texts:
        if text not in by_query:
            raise ValueError("ENGINE_QUERY_RESULT_MISSING")
        hits = tuple(by_query[text])
        for hit in hits:
            entry = _bind_hit(hit, manifest)
            rank = getattr(hit, "rank", None)
            score = getattr(hit, "score", None)
            pts = getattr(hit, "pts", None)
            tb_num = getattr(hit, "timebase_num", None)
            tb_den = getattr(hit, "timebase_den", None)
            if (isinstance(score, bool) or not isinstance(score, (int, float))
                    or not math.isfinite(score)):
                raise ValueError("MULTI_SOURCE_HIT_SCORE_INVALID")
            if (isinstance(rank, bool) or not isinstance(rank, int) or rank < 1
                    or isinstance(pts, bool) or not isinstance(pts, int)
                    or isinstance(tb_num, bool) or not isinstance(tb_num, int)
                    or isinstance(tb_den, bool) or not isinstance(tb_den, int)
                    or tb_num <= 0 or tb_den <= 0):
                raise ValueError("MULTI_SOURCE_HIT_LOCATOR_INVALID")
            candidates.append(MultiSourceRetrievalCandidate(
                query=text,
                rank=rank,
                score=float(score),
                revision_id=entry.revision_id,
                content_id=entry.content_id,
                source_path=str(entry.source_path),
                source_sha256=entry.source_sha256,
                generation_id=generation_id,
                space_id=space_id,
                source_sample_pts=pts,
                source_timebase_num=tb_num,
                source_timebase_den=tb_den,
                timestamp_human=str(getattr(hit, "timestamp_human", "")),
                thumbnail_path=getattr(hit, "thumbnail_path", None),
                thumbnail_status=str(getattr(hit, "thumbnail_status", "NOT_OBSERVED")),
            ))
    return MultiSourceRetrievalResult(
        manifest_digest=manifest.manifest_digest,
        generation_id=generation_id,
        space_id=space_id,
        candidates=tuple(candidates),
    )


__all__ = [
    "MultiSourceRetrievalCandidate",
    "MultiSourceRetrievalResult",
    "retrieve_multi_source",
]
