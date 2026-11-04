"""Preflight and intake evaluator for MEGA-09 candidate review queues.

Packet P09 — Batch Retrieval to Nonbinding Review Queue (`LAB-MEGA-08-14-v1.0.0`).
"""

from __future__ import annotations

from typing import Any, Mapping

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)
from .candidate_queue import build_queue_from_batch_report
from .queue_validation import verify_candidate_queue


STAGE_ID = "MEGA-09.CANDIDATE_REVIEW_QUEUE"


def inspect_review_queue_intake(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Validate a batch report or candidate queue payload and emit a ReadinessPacket."""
    if not isinstance(payload, Mapping):
        raise VipLabError("REVIEW_QUEUE_INTAKE_NOT_MAPPING", "payload must be a mapping")

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="QUEUE_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted authority flags in review queue intake were stripped",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    try:
        if "candidate_queue" in cleaned and isinstance(cleaned["candidate_queue"], Mapping):
            verified_queue = verify_candidate_queue(cleaned["candidate_queue"])
        elif "batch_report" in cleaned and isinstance(cleaned["batch_report"], Mapping):
            queue_obj = build_queue_from_batch_report(cleaned["batch_report"])
            verified_queue = queue_obj.to_dict()
        elif "schema_version" in cleaned and cleaned.get("schema_version") == "vip-lab-batch-report-v1":
            queue_obj = build_queue_from_batch_report(cleaned)
            verified_queue = queue_obj.to_dict()
        elif (
            "schema_version" in cleaned
            and cleaned.get("schema_version") == "vip-lab-candidate-review-queue-v1"
        ):
            verified_queue = verify_candidate_queue(cleaned)
        else:
            raise VipLabError(
                "QUEUE_INTAKE_MISSING_SOURCE",
                "Expected 'batch_report' or 'candidate_queue' mapping in payload",
            )
    except VipLabError as exc:
        reasons.append(exc.code)
        blockers.append(exc.code)
        findings.append(
            ReadinessFinding(
                code=exc.code,
                status=ReadinessStatus.INVALID,
                message=exc.message,
                field_path=exc.field_path,
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"queue_valid": False, "binding_eligible": False},
        )

    reasons.append("CANDIDATE_REVIEW_QUEUE_SYNTHETIC_READY")
    findings.append(
        ReadinessFinding(
            code="QUEUE_NONBINDING_MATCHED_VERIFIED",
            status=ReadinessStatus.READY_SYNTHETIC,
            message="All candidate queue items verified as MATCHED, nonbinding, and unreviewed",
            evidence_state="MATCHED",
            details={
                "queue_digest": verified_queue["queue_digest"],
                "item_count": verified_queue["item_count"],
                "arm_ids": verified_queue["arm_ids"],
            },
        )
    )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=ReadinessStatus.READY_SYNTHETIC,
        evidence_state="MATCHED",
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "queue_valid": True,
            "queue_digest": verified_queue["queue_digest"],
            "upstream_report_digest": verified_queue["upstream_report_digest"],
            "kind": verified_queue["kind"],
            "catalog_id": verified_queue["catalog_id"],
            "catalog_digest": verified_queue["catalog_digest"],
            "arm_ids": verified_queue["arm_ids"],
            "item_count": verified_queue["item_count"],
            "evidence_class": "MATCHED",
            "binding_eligible": False,
            "review_state": "NOT_REVIEWED",
            "human_decision_state": NOT_OBSERVED,
            "cross_arm_winner": None,
            "queue": verified_queue,
        },
    )
