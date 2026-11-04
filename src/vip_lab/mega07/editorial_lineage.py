"""Packet P07b: Gate-3 Editorial Lineage Preflight.

Verifies the provenance chain:
``ReviewBundle -> HumanDecisionArtifact -> EditPlan Lineage``

Delegates directly to:
- ``vip_fvs.review_bundle.ReviewBundle.from_record``
- ``vip_fvs.human_decision.HumanDecisionArtifact.from_record``

Invariants enforced:
- AI-generated edit suggestions are never accepted as human editorial decisions.
- ``HumanDecisionArtifact.payload["bundle_record_digest"]`` and
  ``bundle_dependency_digest`` must match the upstream ``ReviewBundle``.
- ``REJECT`` or ``MODIFY`` decisions cannot advance directly to an active real plan
  (only ``ACCEPT`` with ``plan_action == "BUILD_REAL_PLAN"``).
- ``plan_lineage`` digests must match both the ``ReviewBundle`` and
  ``HumanDecisionArtifact`` digests.
"""

from __future__ import annotations

from typing import Any, Mapping

from vip_fvs.human_decision import HumanDecisionArtifact
from vip_fvs.review_bundle import ReviewBundle

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-07.EDITORIAL_LINEAGE"


def inspect_editorial_lineage(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Validate the ReviewBundle -> HumanDecisionArtifact -> EditPlan lineage chain."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "EDITORIAL_LINEAGE_NOT_MAPPING",
            "payload must be a mapping",
        )

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="LINEAGE_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted authority flags in editorial lineage payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(cleaned.get("ai_generated_decision", False)):
        code = "AI_SUGGESTION_NOT_HUMAN_DECISION"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="An AI-generated edit suggestion is not a human editorial decision",
                field_path="ai_generated_decision",
            )
        )

    bundle_rec = cleaned.get("review_bundle")
    decision_rec = cleaned.get("human_decision")
    plan_lineage = cleaned.get("plan_lineage")

    if not isinstance(bundle_rec, Mapping) or not isinstance(decision_rec, Mapping):
        code = "LINEAGE_BUNDLE_OR_DECISION_MISSING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="Both review_bundle and human_decision mappings are required",
                field_path="review_bundle",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"lineage_valid": False},
        )

    try:
        bundle = ReviewBundle.from_record(dict(bundle_rec))
    except (ValueError, TypeError, KeyError) as exc:
        code = "LINEAGE_REVIEW_BUNDLE_INVALID"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=str(exc),
                field_path="review_bundle",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"lineage_valid": False},
        )

    try:
        decision = HumanDecisionArtifact.from_record(dict(decision_rec))
    except (ValueError, TypeError, KeyError) as exc:
        code = "LINEAGE_HUMAN_DECISION_INVALID"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=str(exc),
                field_path="human_decision",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"lineage_valid": False},
        )

    dec_payload = decision.payload
    bundle_payload = bundle.payload
    bundle_id = str(bundle_payload["bundle_id"])
    decision_id = str(dec_payload["decision_id"])
    decision_class = str(dec_payload["decision_class"])

    if (
        dec_payload.get("bundle_record_digest") != bundle.record_digest
        or dec_payload.get("bundle_dependency_digest") != bundle.dependency_digest
        or dec_payload.get("refinement_id")
        != bundle_payload["refinement"]["refinement_id"]
        or dec_payload.get("source_revision_id")
        != bundle_payload["source"]["source_revision_id"]
        or dec_payload.get("source_sha256") != bundle_payload["source"]["source_sha256"]
    ):
        code = "HUMAN_DECISION_BUNDLE_DIGEST_MISMATCH"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=(
                    "HumanDecisionArtifact digests or source/refinement pins do not "
                    "match upstream ReviewBundle"
                ),
                field_path="human_decision.payload.bundle_record_digest",
            )
        )

    if decision_class == "REJECT":
        code = "HUMAN_DECISION_REJECTED_CANDIDATE"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Rejected candidate cannot advance to an active EditPlan",
                field_path="human_decision.payload.decision_class",
            )
        )
    elif decision_class == "MODIFY":
        code = "HUMAN_DECISION_MODIFICATION_PENDING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="MODIFY decision requires re-refinement before building a plan",
                field_path="human_decision.payload.decision_class",
            )
        )

    if isinstance(plan_lineage, Mapping):
        plan_rb_digest = plan_lineage.get("review_bundle_digest")
        plan_hd_digest = plan_lineage.get("human_decision_digest")
        if (
            plan_rb_digest != bundle.record_digest
            or plan_hd_digest != decision.record_digest
        ):
            code = "PLAN_LINEAGE_DIGEST_MISMATCH"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=(
                        "plan_lineage review_bundle_digest or human_decision_digest "
                        "does not match upstream artifacts"
                    ),
                    field_path="plan_lineage",
                )
            )

    if not blockers:
        reasons.append("EDITORIAL_LINEAGE_SYNTHETIC_VERIFIED")
        findings.append(
            ReadinessFinding(
                code="EDITORIAL_LINEAGE_CHAIN_INTACT",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Verified ReviewBundle -> HumanDecisionArtifact -> EditPlan lineage digests",
                evidence_state="EDITORIAL_INFERENCE",
                details={
                    "bundle_id": bundle_id,
                    "decision_id": decision_id,
                    "decision_class": decision_class,
                },
            )
        )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        evidence_state="EDITORIAL_INFERENCE" if not blockers else NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "lineage_valid": not blockers,
            "bundle_id": bundle_id,
            "review_bundle_digest": bundle.record_digest,
            "decision_id": decision_id,
            "decision_class": decision_class,
            "human_decision_digest": decision.record_digest,
            "current_e01_validated": bundle.current_e01_validated,
        },
    )
