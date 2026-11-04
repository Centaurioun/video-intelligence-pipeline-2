"""Strict self-contained verifier for MEGA-09 CandidateReviewQueue payloads.

Packet P09 — Batch Retrieval to Nonbinding Review Queue (`LAB-MEGA-08-14-v1.0.0`).
"""

from __future__ import annotations

from typing import Any, Mapping

from vip_fvs.batch_report import KIND_SINGLE_ARM, KIND_THREE_ARM
from vip_fvs.three_arm_batch import ARM_TO_PROFILE_ID, DECLARED_ARM_ORDER

from ..common import (
    NOT_OBSERVED,
    VipLabError,
    validate_hex_digest,
)
from .candidate_queue import (
    CANDIDATE_QUEUE_SCHEMA_VERSION,
    FORBIDDEN_CUT_BOUNDARY_KEYS,
    CandidateQueueItem,
    compute_candidate_queue_digest,
)


_TOP_QUEUE_FIELDS = frozenset(
    {
        "schema_version",
        "kind",
        "upstream_report_digest",
        "catalog_id",
        "catalog_digest",
        "query_ids",
        "arm_ids",
        "top_k",
        "cross_arm_winner",
        "synthetic_only",
        "authentic_model_evidence",
        "item_count",
        "items",
        "queue_digest",
    }
)


def verify_candidate_queue(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Verify a CandidateReviewQueue dictionary and return a normalized copy."""
    if not isinstance(payload, Mapping):
        raise VipLabError("QUEUE_NOT_MAPPING", "Candidate queue payload must be a mapping")

    actual_keys = set(payload.keys())
    if actual_keys != _TOP_QUEUE_FIELDS:
        raise VipLabError(
            "QUEUE_FIELDS_INVALID",
            f"CandidateReviewQueue keys mismatch: {sorted(actual_keys ^ _TOP_QUEUE_FIELDS)}",
        )

    if payload["schema_version"] != CANDIDATE_QUEUE_SCHEMA_VERSION:
        raise VipLabError(
            "QUEUE_SCHEMA_INVALID",
            f"Invalid schema_version {payload['schema_version']!r}",
        )
    kind = payload["kind"]
    if kind not in (KIND_SINGLE_ARM, KIND_THREE_ARM):
        raise VipLabError("QUEUE_KIND_INVALID", f"Invalid queue kind {kind!r}")

    if payload["cross_arm_winner"] is not None:
        raise VipLabError(
            "QUEUE_CROSS_ARM_WINNER_FORBIDDEN",
            "cross_arm_winner must be None",
            field_path="cross_arm_winner",
        )
    if payload["synthetic_only"] is not True or payload["authentic_model_evidence"] is not False:
        raise VipLabError(
            "QUEUE_SYNTHETIC_FLAGS_INVALID",
            "synthetic_only must be True and authentic_model_evidence must be False",
        )

    upstream_digest = validate_hex_digest(
        payload["upstream_report_digest"],
        field_name="upstream_report_digest",
        error_code="QUEUE_UPSTREAM_DIGEST_INVALID",
    )
    catalog_digest = validate_hex_digest(
        payload["catalog_digest"],
        field_name="catalog_digest",
        error_code="QUEUE_CATALOG_DIGEST_INVALID",
    )
    declared_digest = validate_hex_digest(
        payload["queue_digest"],
        field_name="queue_digest",
        error_code="QUEUE_DIGEST_INVALID",
    )

    arm_ids = payload["arm_ids"]
    if not isinstance(arm_ids, list) or not arm_ids:
        raise VipLabError("QUEUE_ARM_IDS_INVALID", "arm_ids must be a non-empty list")
    if kind == KIND_SINGLE_ARM and len(arm_ids) != 1:
        raise VipLabError("QUEUE_SINGLE_ARM_COUNT_INVALID", "Single-arm queue must have 1 arm")
    if kind == KIND_THREE_ARM and tuple(arm_ids) != DECLARED_ARM_ORDER:
        raise VipLabError(
            "QUEUE_THREE_ARM_ORDER_INVALID",
            f"Three-arm queue must match {DECLARED_ARM_ORDER}",
        )
    for aid in arm_ids:
        if aid not in ARM_TO_PROFILE_ID:
            raise VipLabError("QUEUE_ARM_ID_UNKNOWN", f"Unknown arm_id {aid!r}")

    query_ids = payload["query_ids"]
    if not isinstance(query_ids, list) or not query_ids or len(set(query_ids)) != len(query_ids):
        raise VipLabError("QUEUE_QUERY_IDS_INVALID", "query_ids must be a non-empty unique list")

    raw_items = payload["items"]
    if not isinstance(raw_items, list):
        raise VipLabError("QUEUE_ITEMS_NOT_LIST", "items must be a list")
    if payload["item_count"] != len(raw_items):
        raise VipLabError("QUEUE_ITEM_COUNT_MISMATCH", "item_count does not match len(items)")

    validated_items: list[dict[str, Any]] = []
    seen_item_ids: set[str] = set()
    space_by_arm: dict[str, str] = {}

    for expected_idx, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, Mapping):
            raise VipLabError("QUEUE_ITEM_NOT_MAPPING", f"items[{expected_idx}] must be a mapping")
        if set(raw_item.keys()) & FORBIDDEN_CUT_BOUNDARY_KEYS:
            raise VipLabError(
                "QUEUE_CANDIDATE_EDIT_BOUNDARY_FORBIDDEN",
                f"items[{expected_idx}] contains forbidden cut/edit boundary keys",
            )
        item_obj = CandidateQueueItem(
            queue_item_id=raw_item.get("queue_item_id", ""),
            queue_index=raw_item.get("queue_index", -1),
            arm_id=raw_item.get("arm_id", ""),
            profile_id=raw_item.get("profile_id", ""),
            model_identity=raw_item.get("model_identity", ""),
            space_id=raw_item.get("space_id", ""),
            generation_id=raw_item.get("generation_id", ""),
            catalog_id=raw_item.get("catalog_id", ""),
            catalog_digest=raw_item.get("catalog_digest", ""),
            manifest_digest=raw_item.get("manifest_digest", ""),
            query_id=raw_item.get("query_id", ""),
            query_text=raw_item.get("query_text", ""),
            rank=raw_item.get("rank", 0),
            score=raw_item.get("score", float("nan")),
            revision_id=raw_item.get("revision_id", ""),
            content_id=raw_item.get("content_id", ""),
            source_path=raw_item.get("source_path", ""),
            source_sha256=raw_item.get("source_sha256", ""),
            source_sample_pts=raw_item.get("source_sample_pts", -1),
            source_timebase_num=raw_item.get("source_timebase_num", 0),
            source_timebase_den=raw_item.get("source_timebase_den", 0),
            timestamp_human=raw_item.get("timestamp_human", ""),
            thumbnail_path=raw_item.get("thumbnail_path"),
            thumbnail_status=raw_item.get("thumbnail_status", "MISSING"),
            evidence_class=raw_item.get("evidence_class", ""),
            binding_eligible=raw_item.get("binding_eligible"),  # type: ignore[arg-type]
            review_state=raw_item.get("review_state", ""),
            human_decision_state=raw_item.get("human_decision_state", NOT_OBSERVED),
            synthetic_only=raw_item.get("synthetic_only"),  # type: ignore[arg-type]
            authentic_model_evidence=raw_item.get("authentic_model_evidence"),  # type: ignore[arg-type]
        )
        if item_obj.queue_index != expected_idx:
            raise VipLabError(
                "QUEUE_ITEM_INDEX_ORDER_MISMATCH",
                f"Expected queue_index {expected_idx}, got {item_obj.queue_index}",
            )
        if item_obj.queue_item_id in seen_item_ids:
            raise VipLabError(
                "QUEUE_DUPLICATE_ITEM_ID",
                f"Duplicate queue_item_id {item_obj.queue_item_id!r}",
            )
        seen_item_ids.add(item_obj.queue_item_id)
        if item_obj.catalog_digest != catalog_digest or item_obj.catalog_id != payload["catalog_id"]:
            raise VipLabError(
                "QUEUE_ITEM_CATALOG_MISMATCH",
                "Queue item catalog_id/catalog_digest mismatch",
            )
        if item_obj.query_id not in query_ids:
            raise VipLabError(
                "QUEUE_ITEM_QUERY_ID_UNKNOWN",
                f"Queue item query_id {item_obj.query_id!r} not in queue query_ids",
            )
        if item_obj.arm_id not in arm_ids:
            raise VipLabError(
                "QUEUE_ITEM_ARM_ID_UNKNOWN",
                f"Queue item arm_id {item_obj.arm_id!r} not in queue arm_ids",
            )
        prior_space = space_by_arm.get(item_obj.arm_id)
        if prior_space is not None and prior_space != item_obj.space_id:
            raise VipLabError(
                "QUEUE_ARM_SPACE_INCONSISTENT",
                f"Inconsistent space_id within arm {item_obj.arm_id!r}",
            )
        space_by_arm[item_obj.arm_id] = item_obj.space_id
        validated_items.append(item_obj.to_dict())

    if len(set(space_by_arm.values())) != len(space_by_arm):
        raise VipLabError(
            "QUEUE_CROSS_ARM_SPACE_COLLISION",
            "Distinct arms in CandidateReviewQueue cannot share a space_id",
        )

    normalized: dict[str, Any] = {
        "schema_version": CANDIDATE_QUEUE_SCHEMA_VERSION,
        "kind": kind,
        "upstream_report_digest": upstream_digest,
        "catalog_id": payload["catalog_id"],
        "catalog_digest": catalog_digest,
        "query_ids": list(query_ids),
        "arm_ids": list(arm_ids),
        "top_k": int(payload["top_k"]),
        "cross_arm_winner": None,
        "synthetic_only": True,
        "authentic_model_evidence": False,
        "item_count": len(validated_items),
        "items": validated_items,
        "queue_digest": declared_digest,
    }
    expected_digest = compute_candidate_queue_digest(normalized)
    if declared_digest != expected_digest:
        raise VipLabError(
            "QUEUE_DIGEST_MISMATCH",
            f"CandidateReviewQueue digest mismatch: {declared_digest} != {expected_digest}",
        )
    return normalized
