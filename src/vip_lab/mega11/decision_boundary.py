"""Editorial decision boundary inspection for MEGA-11."""

from __future__ import annotations

from typing import Any, Mapping

from vip_lab.common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)
from vip_lab.mega11.editorial_proposal import verify_editorial_proposal
from vip_lab.mega11.proposal_revisions import verify_proposal_revision_chain

STAGE_ID = "MEGA-11.EDITORIAL_PROPOSAL_BOUNDARY"


def inspect_editorial_decision_boundary(
    payload: Mapping[str, Any],
) -> ReadinessPacket:
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "EDITORIAL_DECISION_BOUNDARY_NOT_MAPPING",
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
                code="UNTRUSTED_AUTHORITY_CLAIM",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message=f"Rejected untrusted authority keys: {', '.join(untrusted_flags)}",
                evidence_state=NOT_OBSERVED,
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if (
        payload.get("approved") is True
        or bool(cleaned.get("signed_by"))
        or cleaned.get("editor_decision") in ("ACCEPT", "APPROVE", "COMMIT")
        or cleaned.get("human_decision_state") not in (None, NOT_OBSERVED)
    ):
        code = "FORGED_HUMAN_DECISION_REFUSED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Synthetic editorial proposals cannot forge human approval or HumanDecisionArtifact authority.",
                evidence_state=NOT_OBSERVED,
            )
        )

    if (
        cleaned.get("promote_to_edit_plan") is True
        or cleaned.get("promote_to_review_bundle") is True
        or cleaned.get("claim_accepted_authority") is True
        or cleaned.get("is_edit_plan") is True
    ):
        code = "EDITORIAL_PROPOSAL_PROMOTION_REFUSED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="EditorialProposal cannot be promoted to ReviewBundle, HumanDecisionArtifact, or EditPlan in synthetic lab mode.",
                evidence_state=NOT_OBSERVED,
            )
        )

    proposal_raw = cleaned.get("proposal")
    verified_proposal_digest: str | None = None
    chain_summary: dict[str, Any] | None = None

    if not isinstance(proposal_raw, Mapping):
        code = "MISSING_EDITORIAL_PROPOSAL"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="Payload must provide 'proposal' mapping.",
                evidence_state=NOT_OBSERVED,
            )
        )
    else:
        try:
            verified_proposal_digest = verify_editorial_proposal(proposal_raw)
        except VipLabError as exc:
            reasons.append(exc.code)
            blockers.append(exc.code)
            findings.append(
                ReadinessFinding(
                    code=exc.code,
                    status=ReadinessStatus.BLOCKED,
                    message=exc.message,
                    evidence_state=NOT_OBSERVED,
                    details=dict(exc.details),
                )
            )

    revision_chain_raw = cleaned.get("revision_chain")
    if revision_chain_raw is not None:
        if not isinstance(revision_chain_raw, list):
            code = "INVALID_REVISION_CHAIN_TYPE"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message="revision_chain must be a list when provided.",
                    evidence_state=NOT_OBSERVED,
                )
            )
        else:
            try:
                chain_summary = verify_proposal_revision_chain(revision_chain_raw)
            except VipLabError as exc:
                reasons.append(exc.code)
                blockers.append(exc.code)
                findings.append(
                    ReadinessFinding(
                        code=exc.code,
                        status=ReadinessStatus.BLOCKED,
                        message=exc.message,
                        evidence_state=NOT_OBSERVED,
                        details=dict(exc.details),
                    )
                )

    has_refusal = any(
        f.code
        in (
            "FORGED_HUMAN_DECISION_REFUSED",
            "EDITORIAL_PROPOSAL_PROMOTION_REFUSED",
            "EDITORIAL_PROPOSAL_AUTHORITY_ESCALATION",
            "EDITORIAL_PROPOSAL_HUMAN_DECISION_ESCALATION",
        )
        for f in findings
    )
    has_invalid = any(f.status == ReadinessStatus.INVALID for f in findings)

    if has_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif has_invalid:
        status = ReadinessStatus.INVALID
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("EDITORIAL_PROPOSAL_BOUNDARY_PRESERVED")
        findings.append(
            ReadinessFinding(
                code="EDITORIAL_PROPOSAL_BOUNDARY_PRESERVED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="EditorialProposal verified as nonbinding, unapproved, and distinct from EditPlan.",
                evidence_state=NOT_OBSERVED,
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=status,
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "proposal_digest": verified_proposal_digest,
            "revision_chain_summary": chain_summary,
            "accepted_authority": False,
            "human_decision_state": NOT_OBSERVED,
            "is_edit_plan": False,
        },
    )
