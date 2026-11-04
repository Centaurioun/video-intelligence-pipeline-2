"""Revision advancement and chain verification for MEGA-11 EditorialProposal."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from vip_lab.common import NOT_OBSERVED, VipLabError
from vip_lab.mega11.editorial_proposal import (
    ALLOWED_PROPOSED_ACTIONS,
    EDITORIAL_PROPOSAL_SCHEMA_VERSION,
    EditorialProposal,
    compute_editorial_proposal_digest,
    verify_editorial_proposal,
)


def advance_proposal_revision(
    *,
    prior_proposal: EditorialProposal,
    proposed_action: str,
    rationale_note: str,
) -> EditorialProposal:
    if not isinstance(prior_proposal, EditorialProposal):
        raise VipLabError(
            "INVALID_PRIOR_PROPOSAL_TYPE",
            "prior_proposal must be an EditorialProposal instance.",
        )
    verify_editorial_proposal(prior_proposal)

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

    next_version = prior_proposal.proposal_version + 1
    proposal_id = f"eprop_{prior_proposal.queue_item_id}_v{next_version}"
    body: dict[str, Any] = {
        "schema_version": EDITORIAL_PROPOSAL_SCHEMA_VERSION,
        "proposal_id": proposal_id,
        "proposal_version": next_version,
        "parent_proposal_digest": prior_proposal.proposal_digest,
        "upstream_queue_digest": prior_proposal.upstream_queue_digest,
        "upstream_temporal_request_digest": prior_proposal.upstream_temporal_request_digest,
        "queue_item_id": prior_proposal.queue_item_id,
        "temporal_request_id": prior_proposal.temporal_request_id,
        "revision_id": prior_proposal.revision_id,
        "source_path": prior_proposal.source_path,
        "source_sha256": prior_proposal.source_sha256,
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


def verify_proposal_revision_chain(
    revisions: Sequence[EditorialProposal | Mapping[str, Any]],
) -> dict[str, Any]:
    if not isinstance(revisions, Sequence) or len(revisions) == 0:
        raise VipLabError(
            "EMPTY_PROPOSAL_REVISION_CHAIN",
            "revisions must be a non-empty sequence of EditorialProposal items.",
        )

    normalized: list[dict[str, Any]] = []
    seen_digests: set[str] = set()

    for idx, rev in enumerate(revisions):
        payload = (
            rev.to_dict() if isinstance(rev, EditorialProposal) else dict(rev)
        )
        digest = verify_editorial_proposal(payload)
        if digest in seen_digests:
            raise VipLabError(
                "PROPOSAL_REVISION_CYCLE_DETECTED",
                f"Duplicate proposal_digest {digest!r} at index {idx}.",
            )
        seen_digests.add(digest)
        expected_version = idx + 1
        actual_version = payload["proposal_version"]
        if actual_version != expected_version:
            raise VipLabError(
                "PROPOSAL_REVISION_VERSION_GAP",
                f"Expected proposal_version {expected_version} at index {idx}, got {actual_version}.",
            )
        if idx == 0:
            if payload.get("parent_proposal_digest") is not None:
                raise VipLabError(
                    "EDITORIAL_PROPOSAL_ROOT_PARENT_FORBIDDEN",
                    "Root proposal (v1) must have parent_proposal_digest=None.",
                )
        else:
            prev = normalized[idx - 1]
            if payload.get("parent_proposal_digest") != prev["proposal_digest"]:
                raise VipLabError(
                    "PROPOSAL_REVISION_PARENT_MISMATCH",
                    f"Revision v{actual_version} parent_proposal_digest does not match v{actual_version - 1} proposal_digest.",
                )
            for invariant_key in (
                "upstream_queue_digest",
                "upstream_temporal_request_digest",
                "queue_item_id",
                "temporal_request_id",
                "revision_id",
                "source_path",
                "source_sha256",
            ):
                if payload.get(invariant_key) != prev.get(invariant_key):
                    raise VipLabError(
                        "PROPOSAL_REVISION_LINEAGE_MISMATCH",
                        f"Revision chain mutated immutable lineage field {invariant_key!r} at v{actual_version}.",
                        details={
                            "field": invariant_key,
                            "previous": prev.get(invariant_key),
                            "current": payload.get(invariant_key),
                        },
                    )
        normalized.append(payload)

    return {
        "chain_length": len(normalized),
        "root_proposal_digest": normalized[0]["proposal_digest"],
        "head_proposal_digest": normalized[-1]["proposal_digest"],
        "head_proposal_version": normalized[-1]["proposal_version"],
        "queue_item_id": normalized[-1]["queue_item_id"],
        "temporal_request_id": normalized[-1]["temporal_request_id"],
        "accepted_authority": False,
        "is_edit_plan": False,
        "binding_eligible": False,
    }
