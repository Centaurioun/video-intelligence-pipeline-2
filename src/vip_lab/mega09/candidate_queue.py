"""Deterministic nonbinding candidate review queue models and builders for MEGA-09.

Packet P09 — Batch Retrieval to Nonbinding Review Queue (`LAB-MEGA-08-14-v1.0.0`).

Invariants enforced:
- Consumes validated ``SingleArmBatchResult``, ``ThreeArmBatchResult``, or verified
  batch report dicts produced by ``vip_fvs.batch_report``.
- Re-verifies upstream report digest, closed profile identity, semantic space, and
  generation ID before constructing queue items.
- Preserves distinct ``source_path`` occurrences even when ``source_sha256`` is identical.
- Preserves duplicate query texts under distinct ``query_id``s.
- Keeps ``evidence_class="MATCHED"``, ``binding_eligible=False``,
  ``review_state="NOT_REVIEWED"``, ``human_decision_state="NOT_OBSERVED"``, and
  ``cross_arm_winner=None``.
- Never normalizes scores across arms, never re-ranks across arms, and never selects
  a winning arm.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

from vip_fvs.batch_report import (
    KIND_SINGLE_ARM,
    KIND_THREE_ARM,
    build_single_arm_batch_report,
    build_three_arm_batch_report,
    verify_batch_report,
)
from vip_fvs.batch_retrieval import SingleArmBatchResult
from vip_fvs.synthetic_profiles import CLOSED_SYNTHETIC_PROFILE_IDS
from vip_fvs.three_arm_batch import (
    ARM_TO_PROFILE_ID,
    DECLARED_ARM_ORDER,
    PROFILE_ID_TO_ARM,
    ThreeArmBatchResult,
)

from ..common import (
    NOT_OBSERVED,
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)


CANDIDATE_QUEUE_SCHEMA_VERSION = "vip-lab-candidate-review-queue-v1"

FORBIDDEN_CUT_BOUNDARY_KEYS = frozenset(
    {
        "source_pts_interval",
        "frame_accurate_boundary",
        "editorial_decision",
        "edit_boundary",
        "start_frame",
        "end_frame",
        "start_pts",
        "end_pts",
        "cut_in",
        "cut_out",
    }
)


@dataclass(frozen=True)
class CandidateQueueItem:
    """One nonbinding ``MATCHED`` candidate queued for downstream temporal request & review."""

    queue_item_id: str
    queue_index: int
    arm_id: str
    profile_id: str
    model_identity: str
    space_id: str
    generation_id: str
    catalog_id: str
    catalog_digest: str
    manifest_digest: str
    query_id: str
    query_text: str
    rank: int
    score: float
    revision_id: str
    content_id: str
    source_path: str
    source_sha256: str
    source_sample_pts: int
    source_timebase_num: int
    source_timebase_den: int
    timestamp_human: str
    thumbnail_path: str | None = None
    thumbnail_status: str = "MISSING"
    evidence_class: str = "MATCHED"
    binding_eligible: bool = False
    review_state: str = "NOT_REVIEWED"
    human_decision_state: str = NOT_OBSERVED
    synthetic_only: bool = True
    authentic_model_evidence: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.queue_item_id, str) or not self.queue_item_id.strip():
            raise VipLabError("QUEUE_ITEM_ID_INVALID", "queue_item_id must be non-empty")
        if type(self.queue_index) is not int or self.queue_index < 0:
            raise VipLabError("QUEUE_ITEM_INDEX_INVALID", "queue_index must be int >= 0")
        if self.profile_id not in CLOSED_SYNTHETIC_PROFILE_IDS:
            raise VipLabError(
                "QUEUE_ITEM_PROFILE_INVALID",
                f"Unsupported profile_id {self.profile_id!r}",
            )
        if ARM_TO_PROFILE_ID.get(self.arm_id) != self.profile_id:
            raise VipLabError(
                "QUEUE_ITEM_ARM_PROFILE_MISMATCH",
                f"arm_id {self.arm_id!r} does not match profile_id {self.profile_id!r}",
            )
        for name in (
            "model_identity",
            "generation_id",
            "catalog_id",
            "query_id",
            "query_text",
            "revision_id",
            "content_id",
            "source_path",
            "timestamp_human",
            "thumbnail_status",
        ):
            val = getattr(self, name)
            if type(val) is not str or not val.strip() or "\x00" in val:
                raise VipLabError(
                    "QUEUE_ITEM_FIELD_INVALID",
                    f"{name} must be a non-empty string without NUL bytes",
                    field_path=name,
                )
        for hex_field in ("space_id", "catalog_digest", "manifest_digest", "source_sha256"):
            validate_hex_digest(
                getattr(self, hex_field),
                field_name=hex_field,
                error_code="QUEUE_ITEM_DIGEST_INVALID",
            )
        if type(self.rank) is not int or self.rank < 1:
            raise VipLabError("QUEUE_ITEM_RANK_INVALID", "rank must be int >= 1")
        if (
            type(self.score) is bool
            or not isinstance(self.score, (int, float))
            or not math.isfinite(self.score)
        ):
            raise VipLabError("QUEUE_ITEM_SCORE_INVALID", "score must be a finite number")
        if (
            type(self.source_sample_pts) is not int
            or type(self.source_timebase_num) is not int
            or type(self.source_timebase_den) is not int
            or self.source_timebase_num <= 0
            or self.source_timebase_den <= 0
        ):
            raise VipLabError(
                "QUEUE_ITEM_LOCATOR_INVALID",
                "source_sample_pts and rational timebase must be valid integers",
            )
        if self.evidence_class != "MATCHED":
            raise VipLabError(
                "QUEUE_ITEM_EVIDENCE_CLASS_INVALID",
                f"Queue item evidence_class must be 'MATCHED', got {self.evidence_class!r}",
            )
        if self.binding_eligible is not False:
            raise VipLabError(
                "QUEUE_CANDIDATE_BINDING_FORBIDDEN",
                "Candidate queue item must maintain binding_eligible=False",
            )
        if self.review_state != "NOT_REVIEWED":
            raise VipLabError(
                "QUEUE_ITEM_REVIEW_STATE_INVALID",
                f"Initial queue item review_state must be 'NOT_REVIEWED', got {self.review_state!r}",
            )
        if self.human_decision_state != NOT_OBSERVED:
            raise VipLabError(
                "QUEUE_ITEM_HUMAN_DECISION_INVALID",
                f"Queue item human_decision_state must be 'NOT_OBSERVED', got {self.human_decision_state!r}",
            )
        if self.synthetic_only is not True or self.authentic_model_evidence is not False:
            raise VipLabError(
                "QUEUE_ITEM_SYNTHETIC_FLAGS_INVALID",
                "Queue item must maintain synthetic_only=True and authentic_model_evidence=False",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "queue_item_id": self.queue_item_id,
            "queue_index": self.queue_index,
            "arm_id": self.arm_id,
            "profile_id": self.profile_id,
            "model_identity": self.model_identity,
            "space_id": self.space_id,
            "generation_id": self.generation_id,
            "catalog_id": self.catalog_id,
            "catalog_digest": self.catalog_digest,
            "manifest_digest": self.manifest_digest,
            "query_id": self.query_id,
            "query_text": self.query_text,
            "rank": self.rank,
            "score": float(self.score),
            "revision_id": self.revision_id,
            "content_id": self.content_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "source_sample_pts": self.source_sample_pts,
            "source_timebase_num": self.source_timebase_num,
            "source_timebase_den": self.source_timebase_den,
            "timestamp_human": self.timestamp_human,
            "thumbnail_path": self.thumbnail_path,
            "thumbnail_status": self.thumbnail_status,
            "evidence_class": self.evidence_class,
            "binding_eligible": self.binding_eligible,
            "review_state": self.review_state,
            "human_decision_state": self.human_decision_state,
            "synthetic_only": self.synthetic_only,
            "authentic_model_evidence": self.authentic_model_evidence,
        }


@dataclass(frozen=True)
class CandidateReviewQueue:
    """Immutable nonbinding candidate review queue derived from a verified batch report."""

    schema_version: str
    kind: str
    upstream_report_digest: str
    catalog_id: str
    catalog_digest: str
    query_ids: tuple[str, ...]
    arm_ids: tuple[str, ...]
    top_k: int
    items: tuple[CandidateQueueItem, ...]
    queue_digest: str
    cross_arm_winner: None = None
    synthetic_only: bool = True
    authentic_model_evidence: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != CANDIDATE_QUEUE_SCHEMA_VERSION:
            raise VipLabError(
                "QUEUE_SCHEMA_INVALID",
                f"Expected schema_version {CANDIDATE_QUEUE_SCHEMA_VERSION!r}",
            )
        if self.kind not in (KIND_SINGLE_ARM, KIND_THREE_ARM):
            raise VipLabError("QUEUE_KIND_INVALID", f"Unsupported queue kind {self.kind!r}")
        validate_hex_digest(
            self.upstream_report_digest,
            field_name="upstream_report_digest",
            error_code="QUEUE_UPSTREAM_DIGEST_INVALID",
        )
        validate_hex_digest(
            self.catalog_digest,
            field_name="catalog_digest",
            error_code="QUEUE_CATALOG_DIGEST_INVALID",
        )
        validate_hex_digest(
            self.queue_digest,
            field_name="queue_digest",
            error_code="QUEUE_DIGEST_INVALID",
        )
        if self.cross_arm_winner is not None:
            raise VipLabError(
                "QUEUE_CROSS_ARM_WINNER_FORBIDDEN",
                "cross_arm_winner must be None; no cross-arm winner selection is permitted",
            )
        if self.synthetic_only is not True or self.authentic_model_evidence is not False:
            raise VipLabError(
                "QUEUE_SYNTHETIC_FLAGS_INVALID",
                "CandidateReviewQueue must remain synthetic_only=True and authentic_model_evidence=False",
            )
        if self.kind == KIND_THREE_ARM and self.arm_ids != DECLARED_ARM_ORDER:
            raise VipLabError(
                "QUEUE_THREE_ARM_ORDER_INVALID",
                f"Three-arm queue must preserve DECLARED_ARM_ORDER {DECLARED_ARM_ORDER}",
            )

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "upstream_report_digest": self.upstream_report_digest,
            "catalog_id": self.catalog_id,
            "catalog_digest": self.catalog_digest,
            "query_ids": list(self.query_ids),
            "arm_ids": list(self.arm_ids),
            "top_k": self.top_k,
            "cross_arm_winner": self.cross_arm_winner,
            "synthetic_only": self.synthetic_only,
            "authentic_model_evidence": self.authentic_model_evidence,
            "item_count": len(self.items),
            "items": [item.to_dict() for item in self.items],
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload_without_digest()
        body["queue_digest"] = self.queue_digest
        return body


def compute_candidate_queue_digest(payload_without_digest: Mapping[str, Any]) -> str:
    """Compute canonical SHA-256 digest of a CandidateReviewQueue payload."""
    body = {k: v for k, v in payload_without_digest.items() if k != "queue_digest"}
    return canonical_sha256(body)


def _derive_queue_item_id(
    *,
    upstream_report_digest: str,
    arm_id: str,
    query_id: str,
    rank: int,
    revision_id: str,
    source_path: str,
    source_sample_pts: int,
) -> str:
    seed = {
        "upstream_report_digest": upstream_report_digest,
        "arm_id": arm_id,
        "query_id": query_id,
        "rank": rank,
        "revision_id": revision_id,
        "source_path": source_path,
        "source_sample_pts": source_sample_pts,
    }
    short_hash = canonical_sha256(seed)[:16]
    return f"cqi-{arm_id.lower()}-{query_id}-r{rank}-{short_hash}"


def build_queue_from_batch_report(report: Mapping[str, Any] | str | bytes) -> CandidateReviewQueue:
    """Validate an upstream batch report and materialize a deterministic CandidateReviewQueue."""
    if isinstance(report, Mapping):
        for arm in report.get("arms", ()) if isinstance(report.get("arms"), (list, tuple)) else ():
            if isinstance(arm, Mapping):
                for q in arm.get("queries", ()) if isinstance(arm.get("queries"), (list, tuple)) else ():
                    if isinstance(q, Mapping):
                        for cand in (
                            q.get("candidates", ())
                            if isinstance(q.get("candidates"), (list, tuple))
                            else ()
                        ):
                            if isinstance(cand, Mapping):
                                if set(cand.keys()) & FORBIDDEN_CUT_BOUNDARY_KEYS:
                                    raise VipLabError(
                                        "QUEUE_CANDIDATE_EDIT_BOUNDARY_FORBIDDEN",
                                        "Candidate contains forbidden edit/cut boundary fields",
                                    )
                                if cand.get("binding_eligible") is not False:
                                    raise VipLabError(
                                        "QUEUE_CANDIDATE_BINDING_FORBIDDEN",
                                        "Candidate must have binding_eligible=False",
                                    )

    try:
        verified = verify_batch_report(report)
    except (ValueError, TypeError) as exc:
        raise VipLabError(
            "QUEUE_UPSTREAM_REPORT_INVALID",
            f"Upstream batch report failed verification: {exc}",
        ) from exc

    upstream_digest = verified["report_digest"]
    catalog_id = verified["catalog_id"]
    catalog_digest = verified["catalog_digest"]
    query_ids = tuple(verified["query_ids"])
    top_k = int(verified["top_k"])
    kind = verified["kind"]

    items: list[CandidateQueueItem] = []
    arm_ids: list[str] = []
    queue_idx = 0

    for arm in verified["arms"]:
        arm_id = arm["arm_id"]
        profile_id = arm["profile_id"]
        model_identity = arm["model_identity"]
        space_id = arm["space_id"]
        generation_id = arm["generation_id"]
        manifest_digest = arm["manifest_digest"]
        arm_ids.append(arm_id)

        for q_row in arm["queries"]:
            qid = q_row["query_id"]
            qtext = q_row["query_text"]
            for cand in q_row["candidates"]:
                item_id = _derive_queue_item_id(
                    upstream_report_digest=upstream_digest,
                    arm_id=arm_id,
                    query_id=qid,
                    rank=cand["rank"],
                    revision_id=cand["revision_id"],
                    source_path=cand["source_path"],
                    source_sample_pts=cand["source_sample_pts"],
                )
                items.append(
                    CandidateQueueItem(
                        queue_item_id=item_id,
                        queue_index=queue_idx,
                        arm_id=arm_id,
                        profile_id=profile_id,
                        model_identity=model_identity,
                        space_id=space_id,
                        generation_id=generation_id,
                        catalog_id=catalog_id,
                        catalog_digest=catalog_digest,
                        manifest_digest=manifest_digest,
                        query_id=qid,
                        query_text=qtext,
                        rank=cand["rank"],
                        score=cand["score"],
                        revision_id=cand["revision_id"],
                        content_id=cand["content_id"],
                        source_path=cand["source_path"],
                        source_sha256=cand["source_sha256"],
                        source_sample_pts=cand["source_sample_pts"],
                        source_timebase_num=cand["source_timebase_num"],
                        source_timebase_den=cand["source_timebase_den"],
                        timestamp_human=cand["timestamp_human"],
                        thumbnail_path=cand["thumbnail_path"],
                        thumbnail_status=cand["thumbnail_status"],
                        evidence_class="MATCHED",
                        binding_eligible=False,
                        review_state="NOT_REVIEWED",
                        human_decision_state=NOT_OBSERVED,
                        synthetic_only=True,
                        authentic_model_evidence=False,
                    )
                )
                queue_idx += 1

    provisional = CandidateReviewQueue(
        schema_version=CANDIDATE_QUEUE_SCHEMA_VERSION,
        kind=kind,
        upstream_report_digest=upstream_digest,
        catalog_id=catalog_id,
        catalog_digest=catalog_digest,
        query_ids=query_ids,
        arm_ids=tuple(arm_ids),
        top_k=top_k,
        items=tuple(items),
        queue_digest="0" * 64,
        cross_arm_winner=None,
        synthetic_only=True,
        authentic_model_evidence=False,
    )
    digest = compute_candidate_queue_digest(provisional.payload_without_digest())
    return CandidateReviewQueue(
        schema_version=provisional.schema_version,
        kind=provisional.kind,
        upstream_report_digest=provisional.upstream_report_digest,
        catalog_id=provisional.catalog_id,
        catalog_digest=provisional.catalog_digest,
        query_ids=provisional.query_ids,
        arm_ids=provisional.arm_ids,
        top_k=provisional.top_k,
        items=provisional.items,
        queue_digest=digest,
        cross_arm_winner=None,
        synthetic_only=True,
        authentic_model_evidence=False,
    )


def build_queue_from_single_arm(
    result: SingleArmBatchResult,
    *,
    arm_id: str | None = None,
) -> CandidateReviewQueue:
    """Convert a SingleArmBatchResult into a verified CandidateReviewQueue."""
    if not isinstance(result, SingleArmBatchResult):
        raise VipLabError(
            "QUEUE_SINGLE_ARM_RESULT_REQUIRED",
            "Expected SingleArmBatchResult instance",
        )
    resolved_arm_id = arm_id if arm_id is not None else PROFILE_ID_TO_ARM.get(result.profile_id)
    try:
        report = build_single_arm_batch_report(result, arm_id=resolved_arm_id)
    except (ValueError, TypeError) as exc:
        raise VipLabError("QUEUE_SINGLE_ARM_REPORT_INVALID", str(exc)) from exc
    return build_queue_from_batch_report(report)


def build_queue_from_three_arm(result: ThreeArmBatchResult) -> CandidateReviewQueue:
    """Convert a ThreeArmBatchResult into a verified CandidateReviewQueue."""
    if not isinstance(result, ThreeArmBatchResult):
        raise VipLabError(
            "QUEUE_THREE_ARM_RESULT_REQUIRED",
            "Expected ThreeArmBatchResult instance",
        )
    try:
        report = build_three_arm_batch_report(result)
    except (ValueError, TypeError) as exc:
        raise VipLabError("QUEUE_THREE_ARM_REPORT_INVALID", str(exc)) from exc
    return build_queue_from_batch_report(report)
