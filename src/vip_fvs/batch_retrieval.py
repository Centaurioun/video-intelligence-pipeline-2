"""Read-only multi-source batch retrieval consumer over retrieve_multi_source.

Authority: VIP-LAB-MEGA-02 Workstream W3.

This module is an additive, read-only consumer of
:func:`vip_fvs.multi_source_retrieval.retrieve_multi_source`. It batches
distinct query texts against an existing committed generation while preserving
every ordered ``query_id`` from a :class:`vip_fvs.query_batch.QueryCatalog`,
exact manifest occurrence provenance, and nonbinding ``MATCHED`` semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any, Sequence

from . import local_semantic
from .multi_source_retrieval import (
    MultiSourceRetrievalCandidate,
    MultiSourceRetrievalResult,
    retrieve_multi_source,
)
from .query_batch import QueryCatalog, validate_lab_top_k
from .semantic_index import (
    PersistentLocalSemanticIndexEngine,
    SemanticIndexEngine,
    SemanticSpace,
)
from .source_adapter import MultiSourceManifest
from .synthetic_profiles import (
    CLOSED_SYNTHETIC_PROFILE_IDS,
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
)

_MODEL_ID_TO_PROFILE_ID = {
    "google/siglip-base-patch16-224": V1_PROFILE_ID,
    "google/siglip2-base-patch16-224": V2_BASE_PROFILE_ID,
    "google/siglip2-so400m-patch14-384": V2_SO400M_PROFILE_ID,
}
_PROFILE_ID_TO_DIM = {
    V1_PROFILE_ID: 768,
    V2_BASE_PROFILE_ID: 768,
    V2_SO400M_PROFILE_ID: 1152,
}


@dataclass(frozen=True)
class BatchCandidateRecord:
    """One ranked, manifest-bound semantic match attributed to an exact query_id.

    ``source_sample_pts`` and ``(source_timebase_num, source_timebase_den)``
    are source-native sample locators only. They never establish an interval or
    edit boundary, and ``binding_eligible`` is unconditionally ``False``.
    """

    query_id: str
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

    def __post_init__(self) -> None:
        if type(self.query_id) is not str or not self.query_id:
            raise ValueError("BATCH_CANDIDATE_QUERY_ID_INVALID")
        if type(self.query) is not str or not self.query:
            raise ValueError("BATCH_CANDIDATE_QUERY_TEXT_INVALID")
        if type(self.rank) is not int or self.rank < 1:
            raise ValueError("BATCH_CANDIDATE_RANK_INVALID")
        if (
            type(self.score) is bool
            or not isinstance(self.score, (int, float))
            or not math.isfinite(self.score)
        ):
            raise ValueError("BATCH_CANDIDATE_SCORE_INVALID")
        if (
            type(self.source_sample_pts) is not int
            or type(self.source_timebase_num) is not int
            or type(self.source_timebase_den) is not int
            or self.source_timebase_num <= 0
            or self.source_timebase_den <= 0
        ):
            raise ValueError("BATCH_CANDIDATE_LOCATOR_INVALID")
        if self.evidence_class != "MATCHED":
            raise ValueError(f"BATCH_CANDIDATE_EVIDENCE_CLASS_INVALID:{self.evidence_class!r}")
        if self.binding_eligible is not False:
            raise ValueError("BATCH_CANDIDATE_BINDING_ELIGIBLE_FORBIDDEN")

    def to_dict(self, *, arm_id: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if arm_id is not None:
            payload["arm_id"] = arm_id
        payload.update({
            "query_id": self.query_id,
            "query": self.query,
            "rank": self.rank,
            "score": float(self.score),
            "revision_id": self.revision_id,
            "content_id": self.content_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "generation_id": self.generation_id,
            "space_id": self.space_id,
            "source_sample_pts": self.source_sample_pts,
            "source_timebase_num": self.source_timebase_num,
            "source_timebase_den": self.source_timebase_den,
            "timestamp_human": self.timestamp_human,
            "thumbnail_path": self.thumbnail_path,
            "thumbnail_status": self.thumbnail_status,
            "evidence_class": self.evidence_class,
            "binding_eligible": self.binding_eligible,
        })
        return payload


@dataclass(frozen=True)
class BatchQueryResult:
    """Ordered candidate rows for one catalog query_id."""

    query_id: str
    query_text: str
    candidate_count: int
    candidates: tuple[BatchCandidateRecord, ...]

    def __post_init__(self) -> None:
        if type(self.query_id) is not str or not self.query_id:
            raise ValueError("BATCH_QUERY_RESULT_ID_INVALID")
        if type(self.query_text) is not str or not self.query_text:
            raise ValueError("BATCH_QUERY_RESULT_TEXT_INVALID")
        if type(self.candidates) is not tuple or any(
            type(item) is not BatchCandidateRecord for item in self.candidates
        ):
            raise ValueError("BATCH_QUERY_RESULT_CANDIDATES_INVALID")
        if type(self.candidate_count) is not int or self.candidate_count != len(self.candidates):
            raise ValueError("BATCH_QUERY_RESULT_COUNT_MISMATCH")
        for item in self.candidates:
            if item.query_id != self.query_id or item.query != self.query_text:
                raise ValueError("BATCH_QUERY_RESULT_ATTRIBUTION_MISMATCH")


@dataclass(frozen=True)
class SingleArmBatchResult:
    """Immutable result of one single-arm synthetic multi-source batch query."""

    catalog_id: str
    catalog_digest: str
    manifest_digest: str
    generation_id: str
    space_id: str
    model_identity: str
    profile_id: str
    embedding_dim: int
    row_width_bytes: int
    top_k: int
    query_ids: tuple[str, ...]
    query_results: tuple[BatchQueryResult, ...]
    total_candidate_count: int
    fake_runtime_used: bool = True
    synthetic_only: bool = True
    authentic_model_evidence: bool = False

    def __post_init__(self) -> None:
        if self.profile_id not in CLOSED_SYNTHETIC_PROFILE_IDS:
            raise ValueError(f"BATCH_RESULT_PROFILE_ID_INVALID:{self.profile_id!r}")
        expected_dim = _PROFILE_ID_TO_DIM[self.profile_id]
        if type(self.embedding_dim) is not int or self.embedding_dim != expected_dim:
            raise ValueError("BATCH_RESULT_EMBEDDING_DIM_MISMATCH")
        if type(self.row_width_bytes) is not int or self.row_width_bytes != self.embedding_dim * 4:
            raise ValueError("BATCH_RESULT_ROW_WIDTH_MISMATCH")
        validate_lab_top_k(self.top_k)
        if tuple(q.query_id for q in self.query_results) != self.query_ids:
            raise ValueError("BATCH_RESULT_QUERY_ID_ORDER_MISMATCH")
        expected_total = sum(q.candidate_count for q in self.query_results)
        if type(self.total_candidate_count) is not int or self.total_candidate_count != expected_total:
            raise ValueError("BATCH_RESULT_TOTAL_CANDIDATE_COUNT_MISMATCH")
        if (
            self.fake_runtime_used is not True
            or self.synthetic_only is not True
            or self.authentic_model_evidence is not False
        ):
            raise ValueError("BATCH_RESULT_SYNTHETIC_CLAIM_VIOLATION")


def _resolve_profile_id(
    semantic_space: SemanticSpace, explicit_profile_id: str | None
) -> str:
    inferred = _MODEL_ID_TO_PROFILE_ID.get(semantic_space.model_identity)
    if explicit_profile_id is not None:
        if explicit_profile_id not in CLOSED_SYNTHETIC_PROFILE_IDS:
            raise ValueError(f"MODEL_PROFILE_UNSUPPORTED:{explicit_profile_id!r}")
        if inferred is not None and inferred != explicit_profile_id:
            raise ValueError(
                f"BATCH_PROFILE_SPACE_MISMATCH:{explicit_profile_id}!={inferred}"
            )
        if semantic_space.embedding_dim != _PROFILE_ID_TO_DIM[explicit_profile_id]:
            raise ValueError("BATCH_PROFILE_DIMENSION_MISMATCH")
        return explicit_profile_id
    if inferred is not None and semantic_space.embedding_dim == _PROFILE_ID_TO_DIM[inferred]:
        return inferred
    raise ValueError(
        f"BATCH_PROFILE_ID_UNRESOLVED:{semantic_space.model_identity!r}"
    )


def _from_multi_source_candidate(
    query_id: str,
    candidate: MultiSourceRetrievalCandidate,
    *,
    expected_generation_id: str,
    expected_space_id: str,
) -> BatchCandidateRecord:
    if not isinstance(candidate, MultiSourceRetrievalCandidate):
        raise ValueError("BATCH_CANDIDATE_TYPE_INVALID")
    if (
        candidate.generation_id != expected_generation_id
        or candidate.space_id != expected_space_id
    ):
        raise ValueError("BATCH_CANDIDATE_GENERATION_SPACE_MISMATCH")
    if candidate.evidence_class != "MATCHED" or candidate.binding_eligible is not False:
        raise ValueError("BATCH_CANDIDATE_NONBINDING_CONTRACT_VIOLATION")
    return BatchCandidateRecord(
        query_id=query_id,
        query=candidate.query,
        rank=candidate.rank,
        score=candidate.score,
        revision_id=candidate.revision_id,
        content_id=candidate.content_id,
        source_path=candidate.source_path,
        source_sha256=candidate.source_sha256,
        generation_id=candidate.generation_id,
        space_id=candidate.space_id,
        source_sample_pts=candidate.source_sample_pts,
        source_timebase_num=candidate.source_timebase_num,
        source_timebase_den=candidate.source_timebase_den,
        timestamp_human=candidate.timestamp_human,
        thumbnail_path=candidate.thumbnail_path,
        thumbnail_status=candidate.thumbnail_status,
        evidence_class=candidate.evidence_class,
        binding_eligible=candidate.binding_eligible,
    )


def run_batch_retrieval(
    catalog: QueryCatalog,
    manifest: MultiSourceManifest,
    index_root: str | Path,
    *,
    runtime: local_semantic.CheckedLocalSemanticRuntime,
    semantic_space: SemanticSpace,
    engine: SemanticIndexEngine | None = None,
    top_k: int = 5,
    profile_id: str | None = None,
) -> SingleArmBatchResult:
    """Execute a read-only multi-source batch query over ``retrieve_multi_source``.

    Distinct query strings are batched in one underlying ``retrieve_multi_source``
    call and re-associated with every ordered ``query_id`` in ``catalog``.
    """
    if not isinstance(catalog, QueryCatalog):
        raise TypeError("QUERY_CATALOG_REQUIRED")
    if not isinstance(manifest, MultiSourceManifest):
        raise TypeError("MULTI_SOURCE_MANIFEST_REQUIRED")
    if not isinstance(runtime, local_semantic.CheckedLocalSemanticRuntime):
        raise ValueError("CHECKED_RUNTIME_REQUIRED")
    if runtime.fake is not True:
        raise ValueError("SYNTHETIC_BATCH_REQUIRES_FAKE_RUNTIME")
    if not isinstance(semantic_space, SemanticSpace):
        raise ValueError("SEMANTIC_SPACE_REQUIRED")
    if semantic_space != runtime.semantic_space:
        raise ValueError("SEMANTIC_SPACE_RUNTIME_MISMATCH")
    validated_top_k = validate_lab_top_k(top_k)
    resolved_profile_id = _resolve_profile_id(semantic_space, profile_id)

    active_engine: SemanticIndexEngine = (
        engine if engine is not None else PersistentLocalSemanticIndexEngine()
    )
    if not callable(getattr(active_engine, "build_generation_spec", None)) or not callable(
        getattr(active_engine, "query", None)
    ):
        raise ValueError("ENGINE_QUERY_REQUIRED")

    distinct_texts: Sequence[str] = catalog.distinct_texts()
    multi_result = retrieve_multi_source(
        Path(index_root),
        manifest,
        distinct_texts,
        runtime=runtime,
        semantic_space=semantic_space,
        engine=active_engine,
        top_k=validated_top_k,
    )
    if not isinstance(multi_result, MultiSourceRetrievalResult):
        raise ValueError("BATCH_RETRIEVAL_RESULT_INVALID")
    if multi_result.manifest_digest != manifest.manifest_digest:
        raise ValueError("BATCH_RETRIEVAL_MANIFEST_DIGEST_MISMATCH")

    candidates_by_text: dict[str, list[MultiSourceRetrievalCandidate]] = {
        text: [] for text in distinct_texts
    }
    for candidate in multi_result.candidates:
        if candidate.query not in candidates_by_text:
            raise ValueError(f"BATCH_RETRIEVAL_UNEXPECTED_QUERY_KEY:{candidate.query!r}")
        if manifest.find_entry(candidate.source_path, candidate.source_sha256) is None:
            raise ValueError("MULTI_SOURCE_HIT_MANIFEST_BINDING_FAILED")
        candidates_by_text[candidate.query].append(candidate)

    for text, text_candidates in candidates_by_text.items():
        if len(text_candidates) > validated_top_k:
            raise ValueError(
                f"BATCH_RETRIEVAL_TOP_K_EXCEEDED:{text}:{len(text_candidates)}>{validated_top_k}"
            )
        prev_rank = 0
        for candidate in text_candidates:
            if type(candidate.rank) is not int or candidate.rank < 1 or candidate.rank < prev_rank:
                raise ValueError("BATCH_RETRIEVAL_RANK_ORDER_INVALID")
            prev_rank = candidate.rank

    query_results: list[BatchQueryResult] = []
    for item in catalog.queries:
        matched_for_text = candidates_by_text[item.text]
        bound_records = tuple(
            _from_multi_source_candidate(
                item.query_id,
                candidate,
                expected_generation_id=multi_result.generation_id,
                expected_space_id=multi_result.space_id,
            )
            for candidate in matched_for_text
        )
        query_results.append(
            BatchQueryResult(
                query_id=item.query_id,
                query_text=item.text,
                candidate_count=len(bound_records),
                candidates=bound_records,
            )
        )

    ordered_results = tuple(query_results)
    total_candidates = sum(q.candidate_count for q in ordered_results)
    return SingleArmBatchResult(
        catalog_id=catalog.catalog_id,
        catalog_digest=catalog.catalog_digest,
        manifest_digest=manifest.manifest_digest,
        generation_id=multi_result.generation_id,
        space_id=multi_result.space_id,
        model_identity=semantic_space.model_identity,
        profile_id=resolved_profile_id,
        embedding_dim=semantic_space.embedding_dim,
        row_width_bytes=semantic_space.embedding_dim * 4,
        top_k=validated_top_k,
        query_ids=catalog.query_ids,
        query_results=ordered_results,
        total_candidate_count=total_candidates,
        fake_runtime_used=True,
        synthetic_only=True,
        authentic_model_evidence=False,
    )


__all__ = [
    "BatchCandidateRecord",
    "BatchQueryResult",
    "SingleArmBatchResult",
    "run_batch_retrieval",
]
