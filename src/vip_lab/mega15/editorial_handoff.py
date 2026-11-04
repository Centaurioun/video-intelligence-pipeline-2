"""MEGA-15.2 — Non-Authoritative Editorial Decision & Plan Handoff Envelopes.

Bridges MEGA-09 (`CandidateQueueItem`), MEGA-11 (`EditorialProposal` & revision chains),
and MEGA-15.1 (`TemporalPreparationRecord`) into a non-authoritative Gate-3 handoff
envelope while enforcing Gate-3's human-principal and measured-refinement boundaries.

Strict Non-Negotiable Invariants:
- Real human editorial decisions remain `NOT_OBSERVED`.
- Only `HUMAN` principals can ever mint an accepting/modifying `EditorialDecision` in Gate-3;
  `MODEL` and `TOOL` principals are unconditionally refused, and `HUMAN` is refused in
  offline synthetic preparation because no real human review has been observed.
- Synthetic `EditorialProposal` items cannot be promoted into authoritative
  `gate3.plan.EditPlanRevision` or compiled via `gate3.plan.compile_handoff`.
- Duplicate source occurrences (`same source_sha256`, distinct `source_path` / `revision_id` /
  `content_id`) and identical `query_text` under distinct `query_id` are preserved 1-to-1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from gate3.editorial import EditorialDecision, ModelToolPrincipalError
from gate3.plan import EditPlanRevision
from vip_lab.common import (
    SyntheticContextMarker,
    canonical_sha256,
)
from vip_lab.mega09 import CandidateQueueItem, CandidateReviewQueue, verify_candidate_queue
from vip_lab.mega11 import (
    ALLOWED_PROPOSED_ACTIONS,
    EditorialProposal,
    verify_editorial_proposal,
    verify_proposal_revision_chain,
)
from vip_lab.mega15.temporal_preflight import (
    REFUSAL_BINDING_ELIGIBILITY_ESCALATION,
    REFUSAL_FORGED_SOURCE_MEASUREMENT,
    TemporalPreparationRecord,
    ensure_non_empty_str,
    make_synthetic_context,
    parse_synthetic_context_dict,
    raise_mega15_error,
    serialize_synthetic_context,
    validate_synthetic_context,
    verify_temporal_preparation_record,
)

EDITORIAL_HANDOFF_SCHEMA_VERSION = "1.0.0"
EDITORIAL_HANDOFF_KIND = "vip_lab.mega15.editorial_handoff_envelope"
PREPARATION_PACKET_KIND = "vip_lab.mega15.gate3_offline_preparation_packet"

# Explicit refusal codes for MEGA-15.2
REFUSAL_NON_HUMAN_PRINCIPAL = "REFUSAL_NON_HUMAN_EDITORIAL_PRINCIPAL_FORBIDDEN"
REFUSAL_HUMAN_DECISION_NOT_OBSERVED = "REFUSAL_REAL_HUMAN_DECISION_NOT_OBSERVED"
REFUSAL_PROPOSAL_AS_AUTHORITATIVE_PLAN = "REFUSAL_PROPOSAL_AS_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN"
REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN = "REFUSAL_AUTHORITATIVE_EDIT_PLAN_MINTING_FORBIDDEN"
REFUSAL_COMPILE_HANDOFF_FORBIDDEN = "REFUSAL_GATE3_COMPILE_HANDOFF_FORBIDDEN"
REFUSAL_PROPOSAL_CHAIN_BROKEN = "REFUSAL_PROPOSAL_REVISION_CHAIN_BROKEN"
REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE = "REFUSAL_SOURCE_OCCURRENCE_IDENTITY_COLLAPSE"
REFUSAL_QUERY_IDENTITY_COLLAPSE = "REFUSAL_QUERY_IDENTITY_COLLAPSE"
REFUSAL_CROSS_STAGE_JOIN_MISMATCH = "REFUSAL_CROSS_STAGE_JOIN_MISMATCH"


def refuse_non_human_or_unobserved_principal(
    *,
    principal_kind: str,
    real_human_decision_state: str = "NOT_OBSERVED",
    claim_human_approval: bool = False,
) -> None:
    """Fail closed if a caller attempts to mint an EditorialDecision in synthetic offline preparation."""
    probe_kind = "human" if principal_kind == "HUMAN" else principal_kind
    principal_ref = (
        f"{principal_kind.lower()}:synthetic_probe"
        if principal_kind in ("MODEL", "TOOL")
        else "fixture:principal_probe"
    )
    try:
        EditorialDecision(
            decision_id="preflight_principal_probe",
            principal_kind=probe_kind,
            principal_ref=principal_ref,
            decided_on_refinement="ref_probe",
            decided_on_revision=1,
            decision_class="ACCEPT",
            rationale="Synthetic principal preflight check.",
            fixture_scope="SYNTHETIC_FIXTURE",
        )
    except (ModelToolPrincipalError, TypeError, ValueError) as exc:
        raise_mega15_error(
            REFUSAL_NON_HUMAN_PRINCIPAL,
            f"Non-HUMAN principal {principal_kind!r} cannot mint an EditorialDecision: {exc}",
        )

    if principal_kind not in ("HUMAN", "human", "SYNTHETIC_HUMAN"):
        raise_mega15_error(
            REFUSAL_NON_HUMAN_PRINCIPAL,
            f"Only 'HUMAN' principal exists in Gate-3; got {principal_kind!r}",
        )

    if real_human_decision_state != "OBSERVED" or claim_human_approval:
        raise_mega15_error(
            REFUSAL_HUMAN_DECISION_NOT_OBSERVED,
            "Real HUMAN editorial decision is NOT_OBSERVED in synthetic offline preparation; "
            "cannot mint an authoritative Gate-3 EditorialDecision.",
        )


def refuse_authoritative_handoff_minting(
    *,
    attempt_edit_plan: bool = False,
    attempt_compile_handoff: bool = False,
    attempt_promote_proposal: bool = False,
) -> None:
    """Fail closed if a caller attempts to mint an EditPlanRevision or call compile_handoff."""
    if attempt_promote_proposal:
        raise_mega15_error(
            REFUSAL_PROPOSAL_AS_AUTHORITATIVE_PLAN,
            "Synthetic EditorialProposal cannot be promoted to an authoritative EditPlanRevision.",
        )
    if attempt_edit_plan:
        # Demonstrate that Gate-3 EditPlanRevision itself refuses unpinned/unmeasured plans
        try:
            EditPlanRevision(
                plan_id="forbidden_synthetic_plan",
                plan_revision=1,
                placements=[],
                pinned_refinements={},
                pinned_decisions={},
                plan_scope="SYNTHETIC_FIXTURE",
            )
        except (ValueError, TypeError):
            pass
        raise_mega15_error(
            REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN,
            "Minting an authoritative Gate-3 EditPlanRevision is forbidden in offline synthetic preparation; "
            "requires real source PTS measurement and real HUMAN EditorialDecision.",
        )
    if attempt_compile_handoff:
        raise_mega15_error(
            REFUSAL_COMPILE_HANDOFF_FORBIDDEN,
            "Calling gate3.plan.compile_handoff is forbidden when source PTS measurement and "
            "real HUMAN editorial decisions are NOT_OBSERVED.",
        )


@dataclass(frozen=True)
class EditorialProposalRevisionEntry:
    """Immutable revision link inside an `EditorialHandoffEnvelope`."""

    proposal_id: str
    proposal_version: int
    proposed_action: str
    rationale_note: str
    parent_proposal_digest: str | None
    proposal_digest: str

    @property
    def revision_number(self) -> int:
        """Compatibility alias for ``proposal_version``."""
        return self.proposal_version

    @property
    def rationale(self) -> str:
        """Compatibility alias for ``rationale_note``."""
        return self.rationale_note

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "proposal_version": self.proposal_version,
            "proposed_action": self.proposed_action,
            "rationale_note": self.rationale_note,
            "parent_proposal_digest": self.parent_proposal_digest,
            "proposal_digest": self.proposal_digest,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EditorialProposalRevisionEntry":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                "Revision entry must be a mapping",
            )
        parent = payload.get("parent_proposal_digest")
        version_val = payload.get(
            "proposal_version", payload.get("revision_number", 0)
        )
        rationale_val = payload.get(
            "rationale_note", payload.get("rationale", "")
        )
        return cls(
            proposal_id=str(payload.get("proposal_id", "")),
            proposal_version=int(version_val),
            proposed_action=str(payload.get("proposed_action", "")),
            rationale_note=str(rationale_val),
            parent_proposal_digest=None if parent is None else str(parent),
            proposal_digest=str(payload.get("proposal_digest", "")),
        )


@dataclass(frozen=True)
class EditorialHandoffEnvelope:
    """Non-authoritative Gate-3 editorial handoff preparation envelope."""

    schema_version: str
    kind: str
    envelope_id: str
    queue_item_id: str
    arm_id: str
    profile_id: str
    query_id: str
    query_text: str
    revision_id: str
    content_id: str
    source_path: str
    source_sha256: str
    temporal_record_id: str
    temporal_record_digest: str
    proposal_id: str
    latest_proposal_version: int
    latest_proposed_action: str
    latest_rationale_note: str
    latest_proposal_digest: str
    revision_history: tuple[EditorialProposalRevisionEntry, ...]
    real_human_decision_state: str
    accepted_authority: bool
    is_edit_plan: bool
    is_compiled_handoff: bool
    authoritative_plan_eligible: bool
    binding_eligible: bool
    synthetic_context: SyntheticContextMarker
    envelope_digest: str

    @property
    def candidate_item_id(self) -> str:
        """Compatibility alias for ``queue_item_id``."""
        return self.queue_item_id

    @property
    def source_revision_id(self) -> str:
        """Compatibility alias for ``revision_id``."""
        return self.revision_id

    @property
    def latest_revision_number(self) -> int:
        """Compatibility alias for ``latest_proposal_version``."""
        return self.latest_proposal_version

    @property
    def latest_rationale(self) -> str:
        """Compatibility alias for ``latest_rationale_note``."""
        return self.latest_rationale_note

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "envelope_id": self.envelope_id,
            "queue_item_id": self.queue_item_id,
            "arm_id": self.arm_id,
            "profile_id": self.profile_id,
            "query_id": self.query_id,
            "query_text": self.query_text,
            "revision_id": self.revision_id,
            "content_id": self.content_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "temporal_record_id": self.temporal_record_id,
            "temporal_record_digest": self.temporal_record_digest,
            "proposal_id": self.proposal_id,
            "latest_proposal_version": self.latest_proposal_version,
            "latest_proposed_action": self.latest_proposed_action,
            "latest_rationale_note": self.latest_rationale_note,
            "latest_proposal_digest": self.latest_proposal_digest,
            "revision_history": [entry.to_dict() for entry in self.revision_history],
            "real_human_decision_state": self.real_human_decision_state,
            "accepted_authority": self.accepted_authority,
            "is_edit_plan": self.is_edit_plan,
            "is_compiled_handoff": self.is_compiled_handoff,
            "authoritative_plan_eligible": self.authoritative_plan_eligible,
            "binding_eligible": self.binding_eligible,
            "synthetic_context": serialize_synthetic_context(self.synthetic_context),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._digest_payload()
        payload["envelope_digest"] = self.envelope_digest
        return payload

    def validate(self) -> None:
        if self.schema_version != EDITORIAL_HANDOFF_SCHEMA_VERSION:
            raise_mega15_error(
                "EDITORIAL_HANDOFF_SCHEMA_MISMATCH",
                f"Unsupported schema_version: {self.schema_version!r}",
            )
        if self.kind != EDITORIAL_HANDOFF_KIND:
            raise_mega15_error(
                "EDITORIAL_HANDOFF_KIND_MISMATCH",
                f"Unsupported kind: {self.kind!r}",
            )
        ensure_non_empty_str(self.envelope_id, "envelope_id")
        ensure_non_empty_str(self.queue_item_id, "queue_item_id")
        ensure_non_empty_str(self.arm_id, "arm_id")
        ensure_non_empty_str(self.profile_id, "profile_id")
        ensure_non_empty_str(self.query_id, "query_id")
        ensure_non_empty_str(self.query_text, "query_text")
        ensure_non_empty_str(self.revision_id, "revision_id")
        ensure_non_empty_str(self.content_id, "content_id")
        ensure_non_empty_str(self.source_path, "source_path")
        ensure_non_empty_str(self.source_sha256, "source_sha256")
        ensure_non_empty_str(self.temporal_record_id, "temporal_record_id")
        ensure_non_empty_str(self.temporal_record_digest, "temporal_record_digest")
        ensure_non_empty_str(self.proposal_id, "proposal_id")
        ensure_non_empty_str(self.latest_rationale_note, "latest_rationale_note")
        ensure_non_empty_str(self.latest_proposal_digest, "latest_proposal_digest")

        validate_synthetic_context(self.synthetic_context)

        if self.real_human_decision_state != "NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_HUMAN_DECISION_NOT_OBSERVED,
                f"real_human_decision_state must remain 'NOT_OBSERVED', got {self.real_human_decision_state!r}",
            )
        if self.accepted_authority is not False:
            raise_mega15_error(
                REFUSAL_PROPOSAL_AS_AUTHORITATIVE_PLAN,
                "accepted_authority must remain False in synthetic handoff envelope",
            )
        if self.is_edit_plan is not False:
            raise_mega15_error(
                REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN,
                "is_edit_plan must remain False in synthetic handoff envelope",
            )
        if self.is_compiled_handoff is not False:
            raise_mega15_error(
                REFUSAL_COMPILE_HANDOFF_FORBIDDEN,
                "is_compiled_handoff must remain False in synthetic handoff envelope",
            )
        if self.authoritative_plan_eligible is not False:
            raise_mega15_error(
                REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN,
                "authoritative_plan_eligible must remain False in synthetic handoff envelope",
            )
        if self.binding_eligible is not False:
            raise_mega15_error(
                REFUSAL_BINDING_ELIGIBILITY_ESCALATION,
                "binding_eligible must remain False in synthetic handoff envelope",
            )
        if self.latest_proposed_action not in ALLOWED_PROPOSED_ACTIONS:
            raise_mega15_error(
                "EDITORIAL_HANDOFF_INVALID_ACTION",
                f"Unsupported proposed_action: {self.latest_proposed_action!r}",
            )
        if not self.revision_history:
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                "revision_history must contain at least one proposal revision",
            )

        prev_digest: str | None = None
        for idx, entry in enumerate(self.revision_history, start=1):
            ensure_non_empty_str(entry.proposal_id, f"revision_history[{idx}].proposal_id")
            if entry.proposal_version != idx:
                raise_mega15_error(
                    REFUSAL_PROPOSAL_CHAIN_BROKEN,
                    f"Revision version must be contiguous starting at 1; expected {idx}, got {entry.proposal_version}",
                )
            if entry.proposed_action not in ALLOWED_PROPOSED_ACTIONS:
                raise_mega15_error(
                    "EDITORIAL_HANDOFF_INVALID_ACTION",
                    f"Unsupported proposed_action in history: {entry.proposed_action!r}",
                )
            ensure_non_empty_str(entry.rationale_note, f"revision_history[{idx}].rationale_note")
            ensure_non_empty_str(entry.proposal_digest, f"revision_history[{idx}].proposal_digest")
            if idx == 1:
                if entry.parent_proposal_digest is not None:
                    raise_mega15_error(
                        REFUSAL_PROPOSAL_CHAIN_BROKEN,
                        "First revision must have parent_proposal_digest=None",
                    )
            else:
                if entry.parent_proposal_digest != prev_digest:
                    raise_mega15_error(
                        REFUSAL_PROPOSAL_CHAIN_BROKEN,
                        f"Revision {idx} parent_proposal_digest {entry.parent_proposal_digest!r} != "
                        f"previous digest {prev_digest!r}",
                    )
            prev_digest = entry.proposal_digest

        last_entry = self.revision_history[-1]
        if (
            self.proposal_id != last_entry.proposal_id
            or self.latest_proposal_version != last_entry.proposal_version
            or self.latest_proposed_action != last_entry.proposed_action
            or self.latest_rationale_note != last_entry.rationale_note
            or self.latest_proposal_digest != last_entry.proposal_digest
        ):
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                "Envelope latest_* fields do not match tip of revision_history",
            )

        expected_digest = canonical_sha256(self._digest_payload())
        if self.envelope_digest != expected_digest:
            raise_mega15_error(
                "EDITORIAL_HANDOFF_DIGEST_MISMATCH",
                f"envelope_digest mismatch: expected {expected_digest}, got {self.envelope_digest}",
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EditorialHandoffEnvelope":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                "EDITORIAL_HANDOFF_INVALID_PAYLOAD",
                "Payload must be a mapping",
            )
        raw_ctx = payload.get("synthetic_context")
        if not isinstance(raw_ctx, Mapping):
            raise_mega15_error(
                "EDITORIAL_HANDOFF_INVALID_SYNTHETIC_CONTEXT",
                "synthetic_context must be a mapping",
            )
        raw_history = payload.get("revision_history")
        if not isinstance(raw_history, Sequence) or isinstance(raw_history, (str, bytes)):
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                "revision_history must be a sequence",
            )
        history = tuple(EditorialProposalRevisionEntry.from_dict(item) for item in raw_history)
        envelope = cls(
            schema_version=str(payload.get("schema_version", "")),
            kind=str(payload.get("kind", "")),
            envelope_id=str(payload.get("envelope_id", "")),
            queue_item_id=str(
                payload.get("queue_item_id", payload.get("candidate_item_id", ""))
            ),
            arm_id=str(payload.get("arm_id", "")),
            profile_id=str(payload.get("profile_id", "")),
            query_id=str(payload.get("query_id", "")),
            query_text=str(payload.get("query_text", "")),
            revision_id=str(
                payload.get("revision_id", payload.get("source_revision_id", ""))
            ),
            content_id=str(payload.get("content_id", "")),
            source_path=str(payload.get("source_path", "")),
            source_sha256=str(payload.get("source_sha256", "")),
            temporal_record_id=str(payload.get("temporal_record_id", "")),
            temporal_record_digest=str(payload.get("temporal_record_digest", "")),
            proposal_id=str(payload.get("proposal_id", "")),
            latest_proposal_version=int(
                payload.get(
                    "latest_proposal_version",
                    payload.get("latest_revision_number", 0),
                )
            ),
            latest_proposed_action=str(payload.get("latest_proposed_action", "")),
            latest_rationale_note=str(
                payload.get(
                    "latest_rationale_note", payload.get("latest_rationale", "")
                )
            ),
            latest_proposal_digest=str(payload.get("latest_proposal_digest", "")),
            revision_history=history,
            real_human_decision_state=str(payload.get("real_human_decision_state", "")),
            accepted_authority=bool(payload.get("accepted_authority", True)),
            is_edit_plan=bool(payload.get("is_edit_plan", True)),
            is_compiled_handoff=bool(payload.get("is_compiled_handoff", True)),
            authoritative_plan_eligible=bool(payload.get("authoritative_plan_eligible", True)),
            binding_eligible=bool(payload.get("binding_eligible", True)),
            synthetic_context=parse_synthetic_context_dict(raw_ctx),
            envelope_digest=str(payload.get("envelope_digest", "")),
        )
        envelope.validate()
        return envelope


def build_editorial_handoff_envelope(
    *,
    candidate_item: CandidateQueueItem,
    temporal_record: TemporalPreparationRecord,
    proposal_revisions: Sequence[EditorialProposal],
    principal_kind: str | None = None,
    claim_human_approval: bool = False,
    attempt_edit_plan: bool = False,
    attempt_compile_handoff: bool = False,
    attempt_promote_proposal: bool = False,
) -> EditorialHandoffEnvelope:
    """Build a verified non-authoritative `EditorialHandoffEnvelope` for a single candidate occurrence."""
    if principal_kind is not None or claim_human_approval:
        refuse_non_human_or_unobserved_principal(
            principal_kind=principal_kind or "HUMAN",
            real_human_decision_state="NOT_OBSERVED",
            claim_human_approval=claim_human_approval,
        )
    refuse_authoritative_handoff_minting(
        attempt_edit_plan=attempt_edit_plan,
        attempt_compile_handoff=attempt_compile_handoff,
        attempt_promote_proposal=attempt_promote_proposal,
    )

    if not isinstance(candidate_item, CandidateQueueItem):
        raise_mega15_error(
            "EDITORIAL_HANDOFF_INVALID_CANDIDATE_ITEM",
            "candidate_item must be a CandidateQueueItem instance",
        )
    verify_temporal_preparation_record(temporal_record)

    if not isinstance(proposal_revisions, Sequence) or not proposal_revisions:
        raise_mega15_error(
            REFUSAL_PROPOSAL_CHAIN_BROKEN,
            "proposal_revisions must be a non-empty sequence of EditorialProposal",
        )

    for prop in proposal_revisions:
        if not isinstance(prop, EditorialProposal):
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                "All elements of proposal_revisions must be EditorialProposal instances",
            )
        if prop.accepted_authority is not False or prop.is_edit_plan is not False:
            raise_mega15_error(
                REFUSAL_PROPOSAL_AS_AUTHORITATIVE_PLAN,
                "EditorialProposal cannot claim accepted_authority or is_edit_plan",
            )
        if prop.human_decision_state != "NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_HUMAN_DECISION_NOT_OBSERVED,
                f"EditorialProposal human_decision_state must be 'NOT_OBSERVED', got {prop.human_decision_state!r}",
            )
        if prop.binding_eligible is not False:
            raise_mega15_error(
                REFUSAL_BINDING_ELIGIBILITY_ESCALATION,
                "EditorialProposal binding_eligible must be False",
            )
        try:
            verify_editorial_proposal(prop.to_dict())
        except Exception as exc:
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                f"EditorialProposal failed canonical verification: {exc}",
            )

    try:
        verify_proposal_revision_chain([prop.to_dict() for prop in proposal_revisions])
    except Exception as exc:
        raise_mega15_error(
            REFUSAL_PROPOSAL_CHAIN_BROKEN,
            f"Proposal revision chain verification failed: {exc}",
        )

    if candidate_item.binding_eligible is not False or candidate_item.evidence_class != "MATCHED":
        raise_mega15_error(
            REFUSAL_BINDING_ELIGIBILITY_ESCALATION,
            "CandidateQueueItem must remain MATCHED and binding_eligible=False",
        )
    if candidate_item.human_decision_state != "NOT_OBSERVED":
        raise_mega15_error(
            REFUSAL_HUMAN_DECISION_NOT_OBSERVED,
            "CandidateQueueItem human_decision_state must remain NOT_OBSERVED",
        )
    if candidate_item.synthetic_only is not True or candidate_item.authentic_model_evidence is not False:
        raise_mega15_error(
            REFUSAL_FORGED_SOURCE_MEASUREMENT,
            "CandidateQueueItem must remain synthetic_only=True and authentic_model_evidence=False",
        )

    # Verify strict cross-stage occurrence & identity alignment between candidate_item and temporal_record
    if (
        candidate_item.queue_item_id != temporal_record.queue_item_id
        or candidate_item.revision_id != temporal_record.revision_id
        or candidate_item.content_id != temporal_record.content_id
        or candidate_item.source_path != temporal_record.source_path
        or candidate_item.source_sha256 != temporal_record.source_sha256
        or candidate_item.query_id != temporal_record.query_id
        or candidate_item.arm_id != temporal_record.arm_id
        or candidate_item.profile_id != temporal_record.profile_id
    ):
        raise_mega15_error(
            REFUSAL_CROSS_STAGE_JOIN_MISMATCH,
            "CandidateQueueItem and TemporalPreparationRecord identity fields do not match",
        )

    history_entries: list[EditorialProposalRevisionEntry] = []
    prev_digest: str | None = None
    for idx, prop in enumerate(proposal_revisions, start=1):
        if prop.proposal_version != idx:
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                f"Expected proposal_version={idx}, got {prop.proposal_version}",
            )
        if idx == 1 and prop.parent_proposal_digest is not None:
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                "Revision 1 must have parent_proposal_digest=None",
            )
        if idx > 1 and prop.parent_proposal_digest != prev_digest:
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                f"Broken parent_proposal_digest link at revision {idx}",
            )
        if (
            prop.queue_item_id != candidate_item.queue_item_id
            or prop.temporal_request_id != temporal_record.upstream_request_id
            or prop.upstream_temporal_request_digest != temporal_record.upstream_request_digest
            or prop.revision_id != candidate_item.revision_id
            or prop.source_path != candidate_item.source_path
            or prop.source_sha256 != candidate_item.source_sha256
        ):
            raise_mega15_error(
                REFUSAL_CROSS_STAGE_JOIN_MISMATCH,
                f"Proposal revision {idx} does not match candidate/temporal identity",
            )
        history_entries.append(
            EditorialProposalRevisionEntry(
                proposal_id=prop.proposal_id,
                proposal_version=prop.proposal_version,
                proposed_action=prop.proposed_action,
                rationale_note=prop.rationale_note,
                parent_proposal_digest=prop.parent_proposal_digest,
                proposal_digest=prop.proposal_digest,
            )
        )
        prev_digest = prop.proposal_digest

    latest = proposal_revisions[-1]
    syn_ctx = make_synthetic_context()
    envelope_id = f"ehandoff_{candidate_item.queue_item_id}_r{latest.proposal_version}"

    provisional = EditorialHandoffEnvelope(
        schema_version=EDITORIAL_HANDOFF_SCHEMA_VERSION,
        kind=EDITORIAL_HANDOFF_KIND,
        envelope_id=envelope_id,
        queue_item_id=candidate_item.queue_item_id,
        arm_id=candidate_item.arm_id,
        profile_id=candidate_item.profile_id,
        query_id=candidate_item.query_id,
        query_text=candidate_item.query_text,
        revision_id=candidate_item.revision_id,
        content_id=candidate_item.content_id,
        source_path=candidate_item.source_path,
        source_sha256=candidate_item.source_sha256,
        temporal_record_id=temporal_record.record_id,
        temporal_record_digest=temporal_record.record_digest,
        proposal_id=latest.proposal_id,
        latest_proposal_version=latest.proposal_version,
        latest_proposed_action=latest.proposed_action,
        latest_rationale_note=latest.rationale_note,
        latest_proposal_digest=latest.proposal_digest,
        revision_history=tuple(history_entries),
        real_human_decision_state="NOT_OBSERVED",
        accepted_authority=False,
        is_edit_plan=False,
        is_compiled_handoff=False,
        authoritative_plan_eligible=False,
        binding_eligible=False,
        synthetic_context=syn_ctx,
        envelope_digest="",
    )
    digest = canonical_sha256(provisional._digest_payload())
    final_envelope = EditorialHandoffEnvelope(
        **{**provisional.__dict__, "envelope_digest": digest}
    )
    final_envelope.validate()
    return final_envelope


def verify_editorial_handoff_envelope(
    envelope: EditorialHandoffEnvelope | Mapping[str, Any],
) -> EditorialHandoffEnvelope:
    """Verify and return an `EditorialHandoffEnvelope`."""
    if isinstance(envelope, EditorialHandoffEnvelope):
        envelope.validate()
        return envelope
    return EditorialHandoffEnvelope.from_dict(envelope)


@dataclass(frozen=True)
class Gate3OfflinePreparationPacket:
    """Combined MEGA-15 offline Gate-3 preparation packet across all queue items."""

    schema_version: str
    kind: str
    packet_id: str
    catalog_id: str
    queue_digest: str
    temporal_records: tuple[TemporalPreparationRecord, ...]
    handoff_envelopes: tuple[EditorialHandoffEnvelope, ...]
    occurrence_identities: tuple[dict[str, str], ...]
    query_identities: tuple[dict[str, str], ...]
    real_human_decision_state: str
    source_pts_evidence_state: str
    authoritative_plan_eligible: bool
    synthetic_context: SyntheticContextMarker
    packet_digest: str

    @property
    def queue_id(self) -> str:
        """Compatibility alias returning ``catalog_id``."""
        return self.catalog_id

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "packet_id": self.packet_id,
            "catalog_id": self.catalog_id,
            "queue_digest": self.queue_digest,
            "temporal_records": [rec.to_dict() for rec in self.temporal_records],
            "handoff_envelopes": [env.to_dict() for env in self.handoff_envelopes],
            "occurrence_identities": list(self.occurrence_identities),
            "query_identities": list(self.query_identities),
            "real_human_decision_state": self.real_human_decision_state,
            "source_pts_evidence_state": self.source_pts_evidence_state,
            "authoritative_plan_eligible": self.authoritative_plan_eligible,
            "synthetic_context": serialize_synthetic_context(self.synthetic_context),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._digest_payload()
        payload["packet_digest"] = self.packet_digest
        return payload

    def validate(self) -> None:
        if self.schema_version != EDITORIAL_HANDOFF_SCHEMA_VERSION:
            raise_mega15_error(
                "PREPARATION_PACKET_SCHEMA_MISMATCH",
                f"Unsupported schema_version: {self.schema_version!r}",
            )
        if self.kind != PREPARATION_PACKET_KIND:
            raise_mega15_error(
                "PREPARATION_PACKET_KIND_MISMATCH",
                f"Unsupported kind: {self.kind!r}",
            )
        ensure_non_empty_str(self.packet_id, "packet_id")
        ensure_non_empty_str(self.catalog_id, "catalog_id")
        ensure_non_empty_str(self.queue_digest, "queue_digest")
        validate_synthetic_context(self.synthetic_context)

        if self.real_human_decision_state != "NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_HUMAN_DECISION_NOT_OBSERVED,
                "real_human_decision_state must remain NOT_OBSERVED",
            )
        if self.source_pts_evidence_state != "NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_FORGED_SOURCE_MEASUREMENT,
                "source_pts_evidence_state must remain NOT_OBSERVED",
            )
        if self.authoritative_plan_eligible is not False:
            raise_mega15_error(
                REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN,
                "authoritative_plan_eligible must remain False",
            )
        if not self.temporal_records or not self.handoff_envelopes:
            raise_mega15_error(
                "PREPARATION_PACKET_EMPTY",
                "temporal_records and handoff_envelopes must be non-empty",
            )
        if len(self.temporal_records) != len(self.handoff_envelopes):
            raise_mega15_error(
                REFUSAL_CROSS_STAGE_JOIN_MISMATCH,
                "temporal_records and handoff_envelopes counts must match 1-to-1",
            )

        seen_item_ids: set[str] = set()
        for rec, env in zip(self.temporal_records, self.handoff_envelopes):
            rec.validate()
            env.validate()
            if (
                rec.queue_item_id != env.queue_item_id
                or rec.record_id != env.temporal_record_id
                or rec.record_digest != env.temporal_record_digest
                or rec.revision_id != env.revision_id
                or rec.content_id != env.content_id
                or rec.source_path != env.source_path
                or rec.source_sha256 != env.source_sha256
                or rec.query_id != env.query_id
            ):
                raise_mega15_error(
                    REFUSAL_CROSS_STAGE_JOIN_MISMATCH,
                    f"Mismatch between TemporalPreparationRecord {rec.record_id} and EditorialHandoffEnvelope {env.envelope_id}",
                )
            if rec.queue_item_id in seen_item_ids:
                raise_mega15_error(
                    REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE,
                    f"Duplicate queue_item_id in preparation packet: {rec.queue_item_id!r}",
                )
            seen_item_ids.add(rec.queue_item_id)

        expected_digest = canonical_sha256(self._digest_payload())
        if self.packet_digest != expected_digest:
            raise_mega15_error(
                "PREPARATION_PACKET_DIGEST_MISMATCH",
                f"packet_digest mismatch: expected {expected_digest}, got {self.packet_digest}",
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Gate3OfflinePreparationPacket":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                "PREPARATION_PACKET_INVALID_PAYLOAD",
                "Payload must be a mapping",
            )
        raw_ctx = payload.get("synthetic_context")
        if not isinstance(raw_ctx, Mapping):
            raise_mega15_error(
                "PREPARATION_PACKET_INVALID_SYNTHETIC_CONTEXT",
                "synthetic_context must be a mapping",
            )
        raw_t = payload.get("temporal_records")
        raw_e = payload.get("handoff_envelopes")
        raw_occ = payload.get("occurrence_identities")
        raw_q = payload.get("query_identities")
        if (
            not isinstance(raw_t, Sequence)
            or not isinstance(raw_e, Sequence)
            or not isinstance(raw_occ, Sequence)
            or not isinstance(raw_q, Sequence)
        ):
            raise_mega15_error(
                "PREPARATION_PACKET_INVALID_SEQUENCES",
                "Packet sequences must be valid lists",
            )
        packet = cls(
            schema_version=str(payload.get("schema_version", "")),
            kind=str(payload.get("kind", "")),
            packet_id=str(payload.get("packet_id", "")),
            catalog_id=str(payload.get("catalog_id", payload.get("queue_id", ""))),
            queue_digest=str(payload.get("queue_digest", "")),
            temporal_records=tuple(
                TemporalPreparationRecord.from_dict(item) for item in raw_t
            ),
            handoff_envelopes=tuple(
                EditorialHandoffEnvelope.from_dict(item) for item in raw_e
            ),
            occurrence_identities=tuple(
                {str(k): str(v) for k, v in item.items()} for item in raw_occ
            ),
            query_identities=tuple(
                {str(k): str(v) for k, v in item.items()} for item in raw_q
            ),
            real_human_decision_state=str(
                payload.get("real_human_decision_state", "")
            ),
            source_pts_evidence_state=str(
                payload.get("source_pts_evidence_state", "")
            ),
            authoritative_plan_eligible=bool(
                payload.get("authoritative_plan_eligible", True)
            ),
            synthetic_context=parse_synthetic_context_dict(raw_ctx),
            packet_digest=str(payload.get("packet_digest", "")),
        )
        packet.validate()
        return packet


def build_gate3_offline_preparation_packet(
    *,
    candidate_queue: CandidateReviewQueue,
    temporal_records: Sequence[TemporalPreparationRecord],
    handoff_envelopes: Sequence[EditorialHandoffEnvelope],
    packet_id: str = "g3prep_default",
) -> Gate3OfflinePreparationPacket:
    """Assemble and verify a complete `Gate3OfflinePreparationPacket` preserving duplicate occurrences and queries."""
    if not isinstance(candidate_queue, CandidateReviewQueue):
        raise_mega15_error(
            "PREPARATION_PACKET_INVALID_QUEUE",
            "candidate_queue must be a CandidateReviewQueue instance",
        )
    verify_candidate_queue(candidate_queue.to_dict())

    if len(candidate_queue.items) != len(temporal_records) or len(
        candidate_queue.items
    ) != len(handoff_envelopes):
        raise_mega15_error(
            REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE,
            f"Queue items ({len(candidate_queue.items)}), temporal_records ({len(temporal_records)}), "
            f"and handoff_envelopes ({len(handoff_envelopes)}) must match 1-to-1 without collapsing duplicate occurrences.",
        )

    occ_identities: list[dict[str, str]] = []
    query_identities: list[dict[str, str]] = []

    # Check that duplicate source_sha256 items with distinct source_path/revision_id/content_id are not collapsed
    upstream_occ_by_item: dict[str, tuple[str, str, str, str]] = {}
    upstream_query_by_item: dict[str, tuple[str, str]] = {}
    for q_item in candidate_queue.items:
        upstream_occ_by_item[q_item.queue_item_id] = (
            q_item.revision_id,
            q_item.content_id,
            q_item.source_path,
            q_item.source_sha256,
        )
        upstream_query_by_item[q_item.queue_item_id] = (
            q_item.query_id,
            q_item.query_text,
        )

    for q_item, t_rec, h_env in zip(
        candidate_queue.items, temporal_records, handoff_envelopes
    ):
        if (
            q_item.queue_item_id != t_rec.queue_item_id
            or q_item.queue_item_id != h_env.queue_item_id
        ):
            raise_mega15_error(
                REFUSAL_CROSS_STAGE_JOIN_MISMATCH,
                f"Item order/ID mismatch at {q_item.queue_item_id!r}",
            )
        expected_occ = upstream_occ_by_item[q_item.queue_item_id]
        actual_t_occ = (
            t_rec.revision_id,
            t_rec.content_id,
            t_rec.source_path,
            t_rec.source_sha256,
        )
        actual_h_occ = (
            h_env.revision_id,
            h_env.content_id,
            h_env.source_path,
            h_env.source_sha256,
        )
        if actual_t_occ != expected_occ or actual_h_occ != expected_occ:
            raise_mega15_error(
                REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE,
                f"Occurrence identity collapsed or mutated for item {q_item.queue_item_id!r}",
            )

        expected_q = upstream_query_by_item[q_item.queue_item_id]
        actual_h_q = (h_env.query_id, h_env.query_text)
        if actual_h_q != expected_q or t_rec.query_id != q_item.query_id:
            raise_mega15_error(
                REFUSAL_QUERY_IDENTITY_COLLAPSE,
                f"Query identity collapsed or mutated for item {q_item.queue_item_id!r}",
            )

        occ_identities.append(
            {
                "queue_item_id": q_item.queue_item_id,
                "revision_id": q_item.revision_id,
                "content_id": q_item.content_id,
                "source_path": q_item.source_path,
                "source_sha256": q_item.source_sha256,
            }
        )
        query_identities.append(
            {
                "queue_item_id": q_item.queue_item_id,
                "query_id": q_item.query_id,
                "query_text": q_item.query_text,
            }
        )

    syn_ctx = make_synthetic_context()
    provisional = Gate3OfflinePreparationPacket(
        schema_version=EDITORIAL_HANDOFF_SCHEMA_VERSION,
        kind=PREPARATION_PACKET_KIND,
        packet_id=packet_id,
        catalog_id=candidate_queue.catalog_id,
        queue_digest=candidate_queue.queue_digest,
        temporal_records=tuple(temporal_records),
        handoff_envelopes=tuple(handoff_envelopes),
        occurrence_identities=tuple(occ_identities),
        query_identities=tuple(query_identities),
        real_human_decision_state="NOT_OBSERVED",
        source_pts_evidence_state="NOT_OBSERVED",
        authoritative_plan_eligible=False,
        synthetic_context=syn_ctx,
        packet_digest="",
    )
    digest = canonical_sha256(provisional._digest_payload())
    final_packet = Gate3OfflinePreparationPacket(
        **{**provisional.__dict__, "packet_digest": digest}
    )
    final_packet.validate()
    return final_packet


def verify_gate3_offline_preparation_packet(
    packet: Gate3OfflinePreparationPacket | Mapping[str, Any],
) -> Gate3OfflinePreparationPacket:
    """Verify and return a `Gate3OfflinePreparationPacket`."""
    if isinstance(packet, Gate3OfflinePreparationPacket):
        packet.validate()
        return packet
    return Gate3OfflinePreparationPacket.from_dict(packet)
