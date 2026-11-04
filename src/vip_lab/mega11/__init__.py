"""MEGA-11: Versioned Editorial Proposal (Not an Edit Plan)."""

from vip_lab.mega11.decision_boundary import (
    STAGE_ID,
    inspect_editorial_decision_boundary,
)
from vip_lab.mega11.editorial_proposal import (
    ALLOWED_PROPOSED_ACTIONS,
    EDITORIAL_PROPOSAL_SCHEMA_VERSION,
    EditorialProposal,
    build_editorial_proposal,
    compute_editorial_proposal_digest,
    verify_editorial_proposal,
)
from vip_lab.mega11.proposal_revisions import (
    advance_proposal_revision,
    verify_proposal_revision_chain,
)

__all__ = [
    "ALLOWED_PROPOSED_ACTIONS",
    "EDITORIAL_PROPOSAL_SCHEMA_VERSION",
    "STAGE_ID",
    "EditorialProposal",
    "advance_proposal_revision",
    "build_editorial_proposal",
    "compute_editorial_proposal_digest",
    "inspect_editorial_decision_boundary",
    "verify_editorial_proposal",
    "verify_proposal_revision_chain",
]
