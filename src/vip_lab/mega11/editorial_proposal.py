"""Versioned Editorial Proposal (Not an Edit Plan) for MEGA-11."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from vip_lab.common import (
    NOT_OBSERVED,
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)
from vip_lab.mega09.candidate_queue import CandidateQueueItem
from vip_lab.mega10.temporal_request import (
    TemporalRefinementRequest,
    verify_temporal_refinement_request,
)

EDITORIAL_PROPOSAL_SCHEMA_VERSION = "vip-lab-editorial-proposal-v1"
ALLOWED_PROPOSED_ACTIONS: tuple[str, ...] = (
    "REVIEW_CANDIDATE",
    "REQUEST_MEASUREMENT",
    "DEFER_PENDING_EVIDENCE",
)


@dataclass(frozen=True)
class EditorialProposal:
    schema_version: str
    proposal_id: str
    proposal_version: int
    parent_proposal_digest: str | None
    upstream_queue_digest: str
    upstream_temporal_request_digest: str
    queue_item_id: str
    temporal_request_id: str
    revision_id: str
    source_path: str
    source_sha256: str
    proposed_action: str
    rationale_note: str
    accepted_authority: bool
    proposal_status: str
    human_decision_state: str
    evidence_state: str
    is_edit_plan: bool
    binding_eligible: bool
    proposal_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "proposal_id": self.proposal_id,
            "proposal_version": self.proposal_version,
            "parent_proposal_digest": self.parent_proposal_digest,
            "upstream_queue_digest": self.upstream_queue_digest,
            "upstream_temporal_request_digest": self.upstream_temporal_request_digest,
            "queue_item_id": self.queue_item_id,
            "temporal_request_id": self.temporal_request_id,
            "revision_id": self.revision_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "proposed_action": self.proposed_action,
            "rationale_note": self.rationale_note,
            "accepted_authority": self.accepted_authority,
            "proposal_status": self.proposal_status,
            "human_decision_state": self.human_decision_state,
            "evidence_state": self.evidence_state,
            "is_edit_plan": self.is_edit_plan,
            "binding_eligible": self.binding_eligible,
            "proposal_digest": self.proposal_digest,
        }


def compute_editorial_proposal_digest(payload: Mapping[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "proposal_digest"}
    return canonical_sha256(body)


def build_editorial_proposal(
    *,
    queue_item: CandidateQueueItem,
    temporal_request: TemporalRefinementRequest,
    proposed_action: str = "REQUEST_MEASUREMENT",
    rationale_note: str = "Nonbinding synthetic editorial proposal; requires source-native measurement and human decision.",
) -> EditorialProposal:
    if not isinstance(queue_item, CandidateQueueItem):
        raise VipLabError(
            "INVALID_QUEUE_ITEM_TYPE",
            "queue_item must be a CandidateQueueItem instance.",
        )
    if not isinstance(temporal_request, TemporalRefinementRequest):
        raise VipLabError(
            "INVALID_TEMPORAL_REQUEST_TYPE",
            "temporal_request must be a TemporalRefinementRequest instance.",
        )
    verify_temporal_refinement_request(temporal_request.to_dict())

    if (
        queue_item.queue_item_id != temporal_request.queue_item_id
        or queue_item.revision_id != temporal_request.revision_id
        or queue_item.source_path != temporal_request.source_path
        or queue_item.source_sha256 != temporal_request.source_sha256
    ):
        raise VipLabError(
            "PROPOSAL_UPSTREAM_LINEAGE_MISMATCH",
            "queue_item and temporal_request must share identical queue_item_id, revision_id, source_path, and source_sha256.",
            details={
                "queue_item_id": queue_item.queue_item_id,
                "temporal_queue_item_id": temporal_request.queue_item_id,
                "queue_revision_id": queue_item.revision_id,
                "temporal_revision_id": temporal_request.revision_id,
            },
        )

    if proposed_action not in ALLOWED_PROPOSED_ACTIONS:
        raise VipLabError(
            "INVALID_PROPOSED_ACTION",
            f"proposed_action must be one of {ALLOWED_PROPOSED_ACTIONS}, got {proposed_action!r}.",
        )
    if not isinstance(rationale_note, str) or not rationale_note.strip():
        raise VipLabError(
            "INVALID_PROPOSAL_RATIONALE",
            "rationale_note must be a non-empty string.",
        )

    proposal_id = f"eprop_{queue_item.queue_item_id}_v1"
    body: dict[str, Any] = {
        "schema_version": EDITORIAL_PROPOSAL_SCHEMA_VERSION,
        "proposal_id": proposal_id,
        "proposal_version": 1,
        "parent_proposal_digest": None,
        "upstream_queue_digest": temporal_request.upstream_queue_digest,
        "upstream_temporal_request_digest": temporal_request.request_digest,
        "queue_item_id": queue_item.queue_item_id,
        "temporal_request_id": temporal_request.request_id,
        "revision_id": queue_item.revision_id,
        "source_path": queue_item.source_path,
        "source_sha256": queue_item.source_sha256,
        "proposed_action": proposed_action,
        "rationale_note": rationale_note.strip(),
        "accepted_authority": False,
        "proposal_status": "PROPOSED_NOT_APPROVED",
        "human_decision_state": NOT_OBSERVED,
        "evidence_state": NOT_OBSERVED,
        "is_edit_plan": False,
        "binding_eligible": False,
    }
    digest = compute_editorial_proposal_digest(body)
    return EditorialProposal(**body, proposal_digest=digest)


def verify_editorial_proposal(
    proposal: EditorialProposal | Mapping[str, Any],
) -> str:
    payload = (
        proposal.to_dict() if isinstance(proposal, EditorialProposal) else dict(proposal)
    )
    if payload.get("schema_version") != EDITORIAL_PROPOSAL_SCHEMA_VERSION:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_SCHEMA_MISMATCH",
            f"Expected schema_version {EDITORIAL_PROPOSAL_SCHEMA_VERSION!r}, got {payload.get('schema_version')!r}.",
        )
    version = payload.get("proposal_version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_INVALID_VERSION",
            "proposal_version must be an integer >= 1.",
        )
    parent_digest = payload.get("parent_proposal_digest")
    if version == 1 and parent_digest is not None:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_ROOT_PARENT_FORBIDDEN",
            "proposal_version 1 must have parent_proposal_digest=None.",
        )
    if version > 1:
        if not isinstance(parent_digest, str):
            raise VipLabError(
                "EDITORIAL_PROPOSAL_PARENT_REQUIRED",
                "proposal_version > 1 requires a valid 64-hex parent_proposal_digest.",
            )
        validate_hex_digest(parent_digest, field_name="parent_proposal_digest")

    validate_hex_digest(
        str(payload.get("upstream_queue_digest", "")),
        field_name="upstream_queue_digest",
    )
    validate_hex_digest(
        str(payload.get("upstream_temporal_request_digest", "")),
        field_name="upstream_temporal_request_digest",
    )
    validate_hex_digest(
        str(payload.get("source_sha256", "")),
        field_name="source_sha256",
    )

    if payload.get("proposed_action") not in ALLOWED_PROPOSED_ACTIONS:
        raise VipLabError(
            "INVALID_PROPOSED_ACTION",
            f"proposed_action must be one of {ALLOWED_PROPOSED_ACTIONS}.",
        )
    if payload.get("accepted_authority") is not False:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_AUTHORITY_ESCALATION",
            "EditorialProposal must maintain accepted_authority=False.",
        )
    if payload.get("proposal_status") != "PROPOSED_NOT_APPROVED":
        raise VipLabError(
            "EDITORIAL_PROPOSAL_STATUS_INVALID",
            "EditorialProposal must maintain proposal_status='PROPOSED_NOT_APPROVED'.",
        )
    if payload.get("human_decision_state") != NOT_OBSERVED:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_HUMAN_DECISION_ESCALATION",
            f"EditorialProposal must maintain human_decision_state={NOT_OBSERVED!r}.",
        )
    if payload.get("evidence_state") != NOT_OBSERVED:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_EVIDENCE_STATE_ESCALATION",
            f"EditorialProposal must maintain evidence_state={NOT_OBSERVED!r}.",
        )
    if payload.get("is_edit_plan") is not False:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_PROMOTION_REFUSED",
            "EditorialProposal is not an EditPlan and must maintain is_edit_plan=False.",
        )
    if payload.get("binding_eligible") is not False:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_BINDING_FORBIDDEN",
            "EditorialProposal must maintain binding_eligible=False.",
        )

    declared_digest = validate_hex_digest(
        str(payload.get("proposal_digest", "")),
        field_name="proposal_digest",
    )
    computed = compute_editorial_proposal_digest(payload)
    if declared_digest != computed:
        raise VipLabError(
            "EDITORIAL_PROPOSAL_DIGEST_MISMATCH",
            "EditorialProposal digest does not match canonical payload.",
            details={"declared": declared_digest, "computed": computed},
        )
    return computed
