from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from gate3.editorial import EditorialDecision, ModelToolPrincipalError
from gate3.plan import EditPlanRevision
from vip_lab.common import (
    FORBIDDEN_EXTERNAL_AUTHORITY_KEYS,
    NOT_OBSERVED,
    SyntheticContextMarker,
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)
from vip_lab.mega09 import CandidateQueueItem, CandidateReviewQueue, verify_candidate_queue
from vip_lab.mega11 import (
    ALLOWED_PROPOSED_ACTIONS,
    EditorialProposal,
    verify_proposal_revision_chain,
)
from vip_lab.mega15.temporal_preflight import (
    TemporalPreparationRecord,
    verify_temporal_preparation_record,
)

REFUSAL_HUMAN_DECISION_NOT_OBSERVED = "REFUSAL_HUMAN_DECISION_NOT_OBSERVED"
REFUSAL_MODEL_OR_TOOL_PRINCIPAL_FORBIDDEN = "REFUSAL_MODEL_OR_TOOL_PRINCIPAL_FORBIDDEN"
REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN = "REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN"
REFUSAL_REVIEW_BUNDLE_REAL_MEASURED_FORBIDDEN = "REFUSAL_REVIEW_BUNDLE_REAL_MEASURED_FORBIDDEN"


def refuse_non_human_or_unobserved_principal(
    principal_kind: str,
    *,
    claim_real_human_approval: bool = False,
) -> None:
    try:
        decision = EditorialDecision(
            decision_id="preflight_principal_probe",
            refinement_id="ref_probe",
            principal_id="principal_probe",
            principal_kind=principal_kind,
            action="ACCEPT",
            timestamp_utc="2026-11-04T00:00:00Z",
        )
    except ModelToolPrincipalError as exc:
        raise VipLabError(
            f"{REFUSAL_MODEL_OR_TOOL_PRINCIPAL_FORBIDDEN}: {exc}"
        ) from exc

    if decision.principal_authority_evidence is not None:
        raise VipLabError(
            f"{REFUSAL_HUMAN_DECISION_NOT_OBSERVED}: principal_authority_evidence must remain None in synthetic mode."
        )
    if claim_real_human_approval or principal_kind == "human":
        if claim_real_human_approval:
            raise VipLabError(
                f"{REFUSAL_HUMAN_DECISION_NOT_OBSERVED}: real human editorial approval is NOT_OBSERVED in synthetic lab preparation."
            )


def refuse_authoritative_handoff_minting(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, Mapping):
        raise VipLabError("Handoff minting check requires a mapping payload.")
    forbidden_present = sorted(
        k for k in FORBIDDEN_EXTERNAL_AUTHORITY_KEYS if bool(payload.get(k))
    )
    if forbidden_present:
        raise VipLabError(
            f"{REFUSAL_HUMAN_DECISION_NOT_OBSERVED}: forbidden authority keys asserted: {forbidden_present}"
        )

    artifact_kind = str(payload.get("artifact_kind", ""))
    if artifact_kind == "HumanDecisionArtifact" or bool(payload.get("human_decision_artifact_minted")):
        raise VipLabError(
            f"{REFUSAL_HUMAN_DECISION_NOT_OBSERVED}: cannot mint HumanDecisionArtifact in synthetic offline preparation."
        )
    if artifact_kind == "ReviewBundle" and payload.get("source_pts_evidence_state") == "MEASURED":
        raise VipLabError(
            f"{REFUSAL_REVIEW_BUNDLE_REAL_MEASURED_FORBIDDEN}: synthetic preparation cannot mint ReviewBundle claiming real MEASURED source PTS."
        )
    if artifact_kind == "EditPlanRevision" or bool(payload.get("authoritative_edit_plan_created")) or bool(payload.get("export_eligible")):
        # Also verify that gate3.plan.EditPlanRevision.export_eligible is False on synthetic/unmeasured inputs
        probe_plan = EditPlanRevision(
            plan_id="probe_plan",
            revision=1,
            decisions=(),
            pinned_refinements={},
        )
        if probe_plan.export_eligible:
            raise VipLabError("Unexpected export_eligible=True on empty EditPlanRevision.")
        raise VipLabError(
            f"{REFUSAL_AUTHORITATIVE_EDIT_PLAN_FORBIDDEN}: cannot create authoritative EditPlanRevision or claim export_eligible=True in synthetic offline preparation."
        )


@dataclass(frozen=True)
class EditorialHandoffEnvelope:
    handoff_id: str
    queue_id: str
    queue_item_id: str
    candidate_id: str
    query_id: str
    query_text: str
    arm_id: str
    source_id: str
    source_revision_id: str
    source_sha256: str
    source_path: str
    selected_stream_index: int
    time_base: str
    preparation_id: str
    preparation_digest: str
    active_proposal_id: str
    active_revision_number: int
    active_proposal_digest: str
    revision_chain_digests: tuple[str, ...]
    proposed_action: str
    proposed_interval_ticks: tuple[int, int]
    evidence_class: str
    real_human_decision_state: str
    human_decision_artifact_minted: bool
    authoritative_edit_plan_created: bool
    source_native_exact_edit_eligible: bool
    production_export_authorized: bool
    envelope_digest: str

    def _body_without_digest(self) -> dict[str, Any]:
        return {
            "handoff_id": self.handoff_id,
            "queue_id": self.queue_id,
            "queue_item_id": self.queue_item_id,
            "candidate_id": self.candidate_id,
            "query_id": self.query_id,
            "query_text": self.query_text,
            "arm_id": self.arm_id,
            "source_id": self.source_id,
            "source_revision_id": self.source_revision_id,
            "source_sha256": self.source_sha256,
            "source_path": self.source_path,
            "selected_stream_index": self.selected_stream_index,
            "time_base": self.time_base,
            "preparation_id": self.preparation_id,
            "preparation_digest": self.preparation_digest,
            "active_proposal_id": self.active_proposal_id,
            "active_revision_number": self.active_revision_number,
            "active_proposal_digest": self.active_proposal_digest,
            "revision_chain_digests": list(self.revision_chain_digests),
            "proposed_action": self.proposed_action,
            "proposed_interval_ticks": list(self.proposed_interval_ticks),
            "evidence_class": self.evidence_class,
            "real_human_decision_state": self.real_human_decision_state,
            "human_decision_artifact_minted": self.human_decision_artifact_minted,
            "authoritative_edit_plan_created": self.authoritative_edit_plan_created,
            "source_native_exact_edit_eligible": self.source_native_exact_edit_eligible,
            "production_export_authorized": self.production_export_authorized,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._body_without_digest()
        body["envelope_digest"] = self.envelope_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> EditorialHandoffEnvelope:
        if not isinstance(payload, Mapping):
            raise VipLabError("EditorialHandoffEnvelope payload must be a mapping.")
        refuse_authoritative_handoff_minting(payload)
        if payload.get("real_human_decision_state") != NOT_OBSERVED:
            raise VipLabError(
                f"{REFUSAL_HUMAN_DECISION_NOT_OBSERVED}: real_human_decision_state must be {NOT_OBSERVED!r}."
            )
        interval = payload["proposed_interval_ticks"]
        env = cls(
            handoff_id=str(payload["handoff_id"]),
            queue_id=str(payload["queue_id"]),
            queue_item_id=str(payload["queue_item_id"]),
            candidate_id=str(payload["candidate_id"]),
            query_id=str(payload["query_id"]),
            query_text=str(payload["query_text"]),
            arm_id=str(payload["arm_id"]),
            source_id=str(payload["source_id"]),
            source_revision_id=str(payload["source_revision_id"]),
            source_sha256=validate_hex_digest(str(payload["source_sha256"]), field_name="source_sha256"),
            source_path=str(payload["source_path"]),
            selected_stream_index=int(payload["selected_stream_index"]),
            time_base=str(payload["time_base"]),
            preparation_id=str(payload["preparation_id"]),
            preparation_digest=validate_hex_digest(str(payload["preparation_digest"]), field_name="preparation_digest"),
            active_proposal_id=str(payload["active_proposal_id"]),
            active_revision_number=int(payload["active_revision_number"]),
            active_proposal_digest=validate_hex_digest(str(payload["active_proposal_digest"]), field_name="active_proposal_digest"),
            revision_chain_digests=tuple(
                validate_hex_digest(str(d), field_name="revision_chain_digest")
                for d in payload["revision_chain_digests"]
            ),
            proposed_action=str(payload["proposed_action"]),
            proposed_interval_ticks=(int(interval[0]), int(interval[1])),
            evidence_class=str(payload["evidence_class"]),
            real_human_decision_state=NOT_OBSERVED,
            human_decision_artifact_minted=bool(payload["human_decision_artifact_minted"]),
            authoritative_edit_plan_created=bool(payload["authoritative_edit_plan_created"]),
            source_native_exact_edit_eligible=bool(payload["source_native_exact_edit_eligible"]),
            production_export_authorized=bool(payload["production_export_authorized"]),
            envelope_digest=validate_hex_digest(str(payload["envelope_digest"]), field_name="envelope_digest"),
        )
        verify_editorial_handoff_envelope(env)
        return env


def build_editorial_handoff_envelope(
    *,
    queue_id: str = "queue_default",
    queue_item: CandidateQueueItem,
    temporal_record: TemporalPreparationRecord,
    proposal_chain: Sequence[EditorialProposal],
) -> EditorialHandoffEnvelope:
    verify_temporal_preparation_record(temporal_record)
    verify_proposal_revision_chain(proposal_chain)

    if queue_item.queue_item_id != temporal_record.queue_item_id:
        raise VipLabError("queue_item_id mismatch between queue_item and temporal_record.")
    if queue_item.candidate_id != temporal_record.candidate_id:
        raise VipLabError("candidate_id mismatch between queue_item and temporal_record.")
    if queue_item.source_id != temporal_record.source_id:
        raise VipLabError("source_id mismatch between queue_item and temporal_record.")
    if queue_item.source_revision_id != temporal_record.source_revision_id:
        raise VipLabError("source_revision_id mismatch between queue_item and temporal_record.")
    if queue_item.source_sha256 != temporal_record.source_sha256:
        raise VipLabError("source_sha256 mismatch between queue_item and temporal_record.")
    if queue_item.source_path != temporal_record.source_path:
        raise VipLabError("source_path mismatch between queue_item and temporal_record.")
    if queue_item.selected_stream_index != temporal_record.selected_stream_index:
        raise VipLabError("selected_stream_index mismatch between queue_item and temporal_record.")
    if queue_item.time_base != temporal_record.time_base:
        raise VipLabError("time_base mismatch between queue_item and temporal_record.")

    tip = proposal_chain[-1]
    if tip.queue_item_id != queue_item.queue_item_id:
        raise VipLabError("proposal_chain tip queue_item_id mismatch.")
    if tip.candidate_id != queue_item.candidate_id:
        raise VipLabError("proposal_chain tip candidate_id mismatch.")
    if tip.refinement_request_id != temporal_record.refinement_request_id:
        raise VipLabError("proposal_chain tip refinement_request_id mismatch.")
    if tip.source_sha256 != queue_item.source_sha256:
        raise VipLabError("proposal_chain tip source_sha256 mismatch.")
    if tip.selected_stream_index != queue_item.selected_stream_index:
        raise VipLabError("proposal_chain tip selected_stream_index mismatch.")
    if tip.time_base != queue_item.time_base:
        raise VipLabError("proposal_chain tip time_base mismatch.")

    temp = EditorialHandoffEnvelope(
        handoff_id=f"handoff_{queue_item.queue_item_id}_r{tip.revision_number}",
        queue_id=queue_id,
        queue_item_id=queue_item.queue_item_id,
        candidate_id=queue_item.candidate_id,
        query_id=queue_item.query_id,
        query_text=queue_item.query_text,
        arm_id=queue_item.arm_id,
        source_id=queue_item.source_id,
        source_revision_id=queue_item.source_revision_id,
        source_sha256=queue_item.source_sha256,
        source_path=queue_item.source_path,
        selected_stream_index=queue_item.selected_stream_index,
        time_base=queue_item.time_base,
        preparation_id=temporal_record.preparation_id,
        preparation_digest=temporal_record.record_digest,
        active_proposal_id=tip.proposal_id,
        active_revision_number=tip.revision_number,
        active_proposal_digest=tip.proposal_digest,
        revision_chain_digests=tuple(p.proposal_digest for p in proposal_chain),
        proposed_action=tip.proposed_action,
        proposed_interval_ticks=(tip.proposed_start_ticks, tip.proposed_end_ticks),
        evidence_class="EDITORIAL_INFERENCE",
        real_human_decision_state=NOT_OBSERVED,
        human_decision_artifact_minted=False,
        authoritative_edit_plan_created=False,
        source_native_exact_edit_eligible=False,
        production_export_authorized=False,
        envelope_digest="0" * 64,
    )
    digest = canonical_sha256(temp._body_without_digest())
    env = EditorialHandoffEnvelope(**{**temp.__dict__, "envelope_digest": digest})
    verify_editorial_handoff_envelope(env)
    return env


def verify_editorial_handoff_envelope(envelope: EditorialHandoffEnvelope) -> None:
    if not isinstance(envelope, EditorialHandoffEnvelope):
        raise VipLabError("Expected EditorialHandoffEnvelope instance.")
    validate_hex_digest(envelope.source_sha256, field_name="source_sha256")
    validate_hex_digest(envelope.preparation_digest, field_name="preparation_digest")
    validate_hex_digest(envelope.active_proposal_digest, field_name="active_proposal_digest")
    validate_hex_digest(envelope.envelope_digest, field_name="envelope_digest")
    if not envelope.revision_chain_digests:
        raise VipLabError("revision_chain_digests must not be empty.")
    if envelope.active_revision_number != len(envelope.revision_chain_digests):
        raise VipLabError("active_revision_number must equal len(revision_chain_digests).")
    if envelope.active_proposal_digest != envelope.revision_chain_digests[-1]:
        raise VipLabError("active_proposal_digest must match final digest in revision_chain_digests.")
    if envelope.proposed_action not in ALLOWED_PROPOSED_ACTIONS:
        raise VipLabError(f"Unsupported proposed_action: {envelope.proposed_action!r}")
    if envelope.evidence_class != "EDITORIAL_INFERENCE":
        raise VipLabError("EditorialHandoffEnvelope.evidence_class must be 'EDITORIAL_INFERENCE'.")
    if envelope.real_human_decision_state != NOT_OBSERVED:
        raise VipLabError(
            f"{REFUSAL_HUMAN_DECISION_NOT_OBSERVED}: real_human_decision_state must be {NOT_OBSERVED!r}."
        )
    if envelope.human_decision_artifact_minted is not False:
        raise VipLabError("human_decision_artifact_minted must be False.")
    if envelope.authoritative_edit_plan_created is not False:
        raise VipLabError("authoritative_edit_plan_created must be False.")
    if envelope.source_native_exact_edit_eligible is not False:
        raise VipLabError("source_native_exact_edit_eligible must be False.")
    if envelope.production_export_authorized is not False:
        raise VipLabError("production_export_authorized must be False.")
    expected_digest = canonical_sha256(envelope._body_without_digest())
    if envelope.envelope_digest != expected_digest:
        raise VipLabError(
            f"EditorialHandoffEnvelope digest mismatch: expected {expected_digest}, got {envelope.envelope_digest}"
        )


@dataclass(frozen=True)
class Gate3PreparationPacket:
    packet_id: str
    schema_version: str
    synthetic_context: SyntheticContextMarker
    queue_id: str
    queue_digest: str
    temporal_records: tuple[TemporalPreparationRecord, ...]
    handoff_envelopes: tuple[EditorialHandoffEnvelope, ...]
    real_human_decision_state: str
    source_pts_evidence_state: str
    source_native_exact_edit_eligible: bool
    authoritative_edit_plan_created: bool
    production_export_authorized: bool
    packet_digest: str

    def _body_without_digest(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "schema_version": self.schema_version,
            "synthetic_context": self.synthetic_context.to_dict(),
            "queue_id": self.queue_id,
            "queue_digest": self.queue_digest,
            "temporal_records": [r.to_dict() for r in self.temporal_records],
            "handoff_envelopes": [e.to_dict() for e in self.handoff_envelopes],
            "real_human_decision_state": self.real_human_decision_state,
            "source_pts_evidence_state": self.source_pts_evidence_state,
            "source_native_exact_edit_eligible": self.source_native_exact_edit_eligible,
            "authoritative_edit_plan_created": self.authoritative_edit_plan_created,
            "production_export_authorized": self.production_export_authorized,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._body_without_digest()
        body["packet_digest"] = self.packet_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> Gate3PreparationPacket:
        if not isinstance(payload, Mapping):
            raise VipLabError("Gate3PreparationPacket payload must be a mapping.")
        packet = cls(
            packet_id=str(payload["packet_id"]),
            schema_version=str(payload["schema_version"]),
            synthetic_context=SyntheticContextMarker.from_dict(payload["synthetic_context"]),
            queue_id=str(payload["queue_id"]),
            queue_digest=validate_hex_digest(str(payload["queue_digest"]), field_name="queue_digest"),
            temporal_records=tuple(
                TemporalPreparationRecord.from_dict(r) for r in payload["temporal_records"]
            ),
            handoff_envelopes=tuple(
                EditorialHandoffEnvelope.from_dict(e) for e in payload["handoff_envelopes"]
            ),
            real_human_decision_state=str(payload["real_human_decision_state"]),
            source_pts_evidence_state=str(payload["source_pts_evidence_state"]),
            source_native_exact_edit_eligible=bool(payload["source_native_exact_edit_eligible"]),
            authoritative_edit_plan_created=bool(payload["authoritative_edit_plan_created"]),
            production_export_authorized=bool(payload["production_export_authorized"]),
            packet_digest=validate_hex_digest(str(payload["packet_digest"]), field_name="packet_digest"),
        )
        verify_gate3_preparation_packet(packet)
        return packet


def build_gate3_preparation_packet(
    *,
    packet_id: str,
    queue: CandidateReviewQueue,
    temporal_records: Sequence[TemporalPreparationRecord],
    proposal_chains: Mapping[str, Sequence[EditorialProposal]],
) -> Gate3PreparationPacket:
    verify_candidate_queue(queue)
    if len(temporal_records) != len(queue.items):
        raise VipLabError("temporal_records count must equal queue.items count.")

    records_by_qitem: dict[str, TemporalPreparationRecord] = {}
    for rec in temporal_records:
        verify_temporal_preparation_record(rec)
        records_by_qitem[rec.queue_item_id] = rec

    envelopes: list[EditorialHandoffEnvelope] = []
    ordered_records: list[TemporalPreparationRecord] = []
    for item in queue.items:
        if item.queue_item_id not in records_by_qitem:
            raise VipLabError(f"Missing TemporalPreparationRecord for {item.queue_item_id!r}")
        if item.queue_item_id not in proposal_chains:
            raise VipLabError(f"Missing proposal_chain for {item.queue_item_id!r}")
        rec = records_by_qitem[item.queue_item_id]
        chain = proposal_chains[item.queue_item_id]
        env = build_editorial_handoff_envelope(
            queue_id=queue.queue_id,
            queue_item=item,
            temporal_record=rec,
            proposal_chain=chain,
        )
        ordered_records.append(rec)
        envelopes.append(env)

    temp = Gate3PreparationPacket(
        packet_id=packet_id,
        schema_version="1.0.0",
        synthetic_context=SyntheticContextMarker.default("mega15.gate3_preparation"),
        queue_id=queue.queue_id,
        queue_digest=queue.queue_digest,
        temporal_records=tuple(ordered_records),
        handoff_envelopes=tuple(envelopes),
        real_human_decision_state=NOT_OBSERVED,
        source_pts_evidence_state=NOT_OBSERVED,
        source_native_exact_edit_eligible=False,
        authoritative_edit_plan_created=False,
        production_export_authorized=False,
        packet_digest="0" * 64,
    )
    digest = canonical_sha256(temp._body_without_digest())
    packet = Gate3PreparationPacket(**{**temp.__dict__, "packet_digest": digest})
    verify_gate3_preparation_packet(packet)
    return packet


def verify_gate3_preparation_packet(packet: Gate3PreparationPacket) -> None:
    if not isinstance(packet, Gate3PreparationPacket):
        raise VipLabError("Expected Gate3PreparationPacket instance.")
    packet.synthetic_context.validate()
    validate_hex_digest(packet.queue_digest, field_name="queue_digest")
    validate_hex_digest(packet.packet_digest, field_name="packet_digest")
    if not packet.temporal_records or not packet.handoff_envelopes:
        raise VipLabError("Gate3PreparationPacket must contain non-empty records and envelopes.")
    if len(packet.temporal_records) != len(packet.handoff_envelopes):
        raise VipLabError("temporal_records and handoff_envelopes counts must match.")
    for rec, env in zip(packet.temporal_records, packet.handoff_envelopes, strict=True):
        verify_temporal_preparation_record(rec)
        verify_editorial_handoff_envelope(env)
        if env.queue_id != packet.queue_id:
            raise VipLabError("Envelope queue_id mismatch in Gate3PreparationPacket.")
        if env.queue_item_id != rec.queue_item_id:
            raise VipLabError("Envelope/record queue_item_id mismatch in Gate3PreparationPacket.")
        if env.preparation_id != rec.preparation_id or env.preparation_digest != rec.record_digest:
            raise VipLabError("Envelope preparation digest/ID mismatch in Gate3PreparationPacket.")

    if packet.real_human_decision_state != NOT_OBSERVED:
        raise VipLabError("Gate3PreparationPacket.real_human_decision_state must be NOT_OBSERVED.")
    if packet.source_pts_evidence_state != NOT_OBSERVED:
        raise VipLabError("Gate3PreparationPacket.source_pts_evidence_state must be NOT_OBSERVED.")
    if packet.source_native_exact_edit_eligible is not False:
        raise VipLabError("Gate3PreparationPacket.source_native_exact_edit_eligible must be False.")
    if packet.authoritative_edit_plan_created is not False:
        raise VipLabError("Gate3PreparationPacket.authoritative_edit_plan_created must be False.")
    if packet.production_export_authorized is not False:
        raise VipLabError("Gate3PreparationPacket.production_export_authorized must be False.")

    expected_digest = canonical_sha256(packet._body_without_digest())
    if packet.packet_digest != expected_digest:
        raise VipLabError(
            f"Gate3PreparationPacket digest mismatch: expected {expected_digest}, got {packet.packet_digest}"
        )
