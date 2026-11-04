"""Cross-stage digest and source-identity lineage audit for MEGA-13."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vip_lab.common import VipLabError, canonical_sha256
from vip_lab.mega09.candidate_queue import CandidateReviewQueue
from vip_lab.mega09.queue_validation import verify_candidate_queue
from vip_lab.mega10.temporal_request import (
    TemporalRefinementRequest,
    verify_temporal_refinement_request,
)
from vip_lab.mega11.editorial_proposal import (
    EditorialProposal,
    verify_editorial_proposal,
)
from vip_lab.mega11.proposal_revisions import verify_proposal_revision_chain
from vip_lab.mega12.replay_graph import ReplayGraph, verify_replay_graph

LINEAGE_AUDIT_SCHEMA_VERSION = "vip-lab-lineage-audit-v1"


@dataclass(frozen=True)
class LineageAuditReceipt:
    schema_version: str
    lineage_valid: bool
    queue_digest: str
    temporal_request_digest: str
    proposal_digest: str
    replay_graph_digest: str | None
    queue_item_id: str
    temporal_request_id: str
    proposal_id: str
    proposal_version: int
    revision_id: str
    source_path: str
    source_sha256: str
    receipt_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "lineage_valid": self.lineage_valid,
            "queue_digest": self.queue_digest,
            "temporal_request_digest": self.temporal_request_digest,
            "proposal_digest": self.proposal_digest,
            "replay_graph_digest": self.replay_graph_digest,
            "queue_item_id": self.queue_item_id,
            "temporal_request_id": self.temporal_request_id,
            "proposal_id": self.proposal_id,
            "proposal_version": self.proposal_version,
            "revision_id": self.revision_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "receipt_digest": self.receipt_digest,
        }


def audit_cross_stage_lineage(
    *,
    candidate_queue: CandidateReviewQueue | Mapping[str, Any],
    temporal_request: TemporalRefinementRequest | Mapping[str, Any],
    editorial_proposal: EditorialProposal | Mapping[str, Any],
    proposal_revision_chain: Sequence[EditorialProposal | Mapping[str, Any]] | None = None,
    replay_graph: ReplayGraph | Mapping[str, Any] | None = None,
) -> LineageAuditReceipt:
    q_payload = (
        candidate_queue.to_dict()
        if isinstance(candidate_queue, CandidateReviewQueue)
        else dict(candidate_queue)
    )
    t_payload = (
        temporal_request.to_dict()
        if isinstance(temporal_request, TemporalRefinementRequest)
        else dict(temporal_request)
    )
    p_payload = (
        editorial_proposal.to_dict()
        if isinstance(editorial_proposal, EditorialProposal)
        else dict(editorial_proposal)
    )

    verified_queue = verify_candidate_queue(q_payload)
    verified_temp = verify_temporal_refinement_request(t_payload)
    p_digest = verify_editorial_proposal(p_payload)

    q_digest = str(verified_queue["queue_digest"])
    t_digest = str(verified_temp["request_digest"])

    if verified_temp.get("upstream_queue_digest") != q_digest:
        raise VipLabError(
            "LINEAGE_AUDIT_DIGEST_MISMATCH",
            "TemporalRefinementRequest.upstream_queue_digest does not match verified CandidateReviewQueue.queue_digest.",
            details={
                "expected": q_digest,
                "actual": verified_temp.get("upstream_queue_digest"),
            },
        )

    if (
        p_payload.get("upstream_queue_digest") != q_digest
        or p_payload.get("upstream_temporal_request_digest") != t_digest
    ):
        raise VipLabError(
            "LINEAGE_AUDIT_DIGEST_MISMATCH",
            "EditorialProposal upstream digests do not match verified queue_digest and temporal_request_digest.",
            details={
                "expected_queue_digest": q_digest,
                "actual_queue_digest": p_payload.get("upstream_queue_digest"),
                "expected_temporal_digest": t_digest,
                "actual_temporal_digest": p_payload.get("upstream_temporal_request_digest"),
            },
        )

    target_item_id = str(verified_temp.get("queue_item_id", ""))
    matching_items = [
        item
        for item in verified_queue.get("items", ())
        if isinstance(item, Mapping) and item.get("queue_item_id") == target_item_id
    ]
    if len(matching_items) != 1:
        raise VipLabError(
            "LINEAGE_AUDIT_SOURCE_MISMATCH",
            f"queue_item_id {target_item_id!r} not uniquely found in CandidateReviewQueue.",
        )
    q_item = matching_items[0]

    for field_name in ("queue_item_id", "revision_id", "source_path", "source_sha256"):
        q_val = q_item.get(field_name)
        t_val = verified_temp.get(field_name)
        p_val = p_payload.get(field_name)
        if not (q_val == t_val == p_val):
            raise VipLabError(
                "LINEAGE_AUDIT_SOURCE_MISMATCH",
                f"Cross-stage source identity mismatch on {field_name!r}: queue={q_val!r}, temporal={t_val!r}, proposal={p_val!r}.",
                details={
                    "field": field_name,
                    "queue_value": q_val,
                    "temporal_value": t_val,
                    "proposal_value": p_val,
                },
            )

    if p_payload.get("temporal_request_id") != verified_temp.get("request_id"):
        raise VipLabError(
            "LINEAGE_AUDIT_SOURCE_MISMATCH",
            "EditorialProposal.temporal_request_id does not match TemporalRefinementRequest.request_id.",
        )

    if proposal_revision_chain is not None:
        chain_summary = verify_proposal_revision_chain(proposal_revision_chain)
        if chain_summary["head_proposal_digest"] != p_digest:
            raise VipLabError(
                "LINEAGE_AUDIT_DIGEST_MISMATCH",
                "EditorialProposal digest does not match head of proposal_revision_chain.",
            )

    replay_digest: str | None = None
    if replay_graph is not None:
        replay_digest = verify_replay_graph(replay_graph)

    body: dict[str, Any] = {
        "schema_version": LINEAGE_AUDIT_SCHEMA_VERSION,
        "lineage_valid": True,
        "queue_digest": q_digest,
        "temporal_request_digest": t_digest,
        "proposal_digest": p_digest,
        "replay_graph_digest": replay_digest,
        "queue_item_id": target_item_id,
        "temporal_request_id": str(verified_temp["request_id"]),
        "proposal_id": str(p_payload["proposal_id"]),
        "proposal_version": int(p_payload["proposal_version"]),
        "revision_id": str(q_item["revision_id"]),
        "source_path": str(q_item["source_path"]),
        "source_sha256": str(q_item["source_sha256"]),
    }
    receipt_digest = canonical_sha256(body)
    return LineageAuditReceipt(**body, receipt_digest=receipt_digest)
