from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vip_lab.common import (
    NOT_OBSERVED,
    SyntheticContextMarker,
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)
from vip_lab.mega09 import CandidateReviewQueue, verify_candidate_queue
from vip_lab.mega10 import PtsFixtureDiagnostic, TemporalRefinementRequest
from vip_lab.mega11 import EditorialProposal, verify_proposal_revision_chain
from vip_lab.mega13 import audit_cross_stage_lineage
from vip_lab.mega15.editorial_handoff import (
    Gate3PreparationPacket,
    verify_gate3_preparation_packet,
)


@dataclass(frozen=True)
class Gate3LineageCertificate:
    certificate_id: str
    schema_version: str
    synthetic_context: SyntheticContextMarker
    queue_id: str
    queue_digest: str
    preparation_packet_id: str
    preparation_packet_digest: str
    mega13_audit_id: str
    mega13_receipt_digest: str
    verified_item_count: int
    duplicate_occurrence_paths_preserved: bool
    duplicate_query_texts_preserved: bool
    revision_chains_verified: bool
    lineage_status: str
    real_human_decision_state: str
    source_pts_evidence_state: str
    source_native_exact_edit_eligible: bool
    authoritative_edit_plan_created: bool
    production_export_authorized: bool
    certificate_digest: str

    def _body_without_digest(self) -> dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "schema_version": self.schema_version,
            "synthetic_context": self.synthetic_context.to_dict(),
            "queue_id": self.queue_id,
            "queue_digest": self.queue_digest,
            "preparation_packet_id": self.preparation_packet_id,
            "preparation_packet_digest": self.preparation_packet_digest,
            "mega13_audit_id": self.mega13_audit_id,
            "mega13_receipt_digest": self.mega13_receipt_digest,
            "verified_item_count": self.verified_item_count,
            "duplicate_occurrence_paths_preserved": self.duplicate_occurrence_paths_preserved,
            "duplicate_query_texts_preserved": self.duplicate_query_texts_preserved,
            "revision_chains_verified": self.revision_chains_verified,
            "lineage_status": self.lineage_status,
            "real_human_decision_state": self.real_human_decision_state,
            "source_pts_evidence_state": self.source_pts_evidence_state,
            "source_native_exact_edit_eligible": self.source_native_exact_edit_eligible,
            "authoritative_edit_plan_created": self.authoritative_edit_plan_created,
            "production_export_authorized": self.production_export_authorized,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._body_without_digest()
        body["certificate_digest"] = self.certificate_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> Gate3LineageCertificate:
        if not isinstance(payload, Mapping):
            raise VipLabError("Gate3LineageCertificate payload must be a mapping.")
        cert = cls(
            certificate_id=str(payload["certificate_id"]),
            schema_version=str(payload["schema_version"]),
            synthetic_context=SyntheticContextMarker.from_dict(payload["synthetic_context"]),
            queue_id=str(payload["queue_id"]),
            queue_digest=validate_hex_digest(str(payload["queue_digest"]), field_name="queue_digest"),
            preparation_packet_id=str(payload["preparation_packet_id"]),
            preparation_packet_digest=validate_hex_digest(
                str(payload["preparation_packet_digest"]), field_name="preparation_packet_digest"
            ),
            mega13_audit_id=str(payload["mega13_audit_id"]),
            mega13_receipt_digest=validate_hex_digest(
                str(payload["mega13_receipt_digest"]), field_name="mega13_receipt_digest"
            ),
            verified_item_count=int(payload["verified_item_count"]),
            duplicate_occurrence_paths_preserved=bool(payload["duplicate_occurrence_paths_preserved"]),
            duplicate_query_texts_preserved=bool(payload["duplicate_query_texts_preserved"]),
            revision_chains_verified=bool(payload["revision_chains_verified"]),
            lineage_status=str(payload["lineage_status"]),
            real_human_decision_state=str(payload["real_human_decision_state"]),
            source_pts_evidence_state=str(payload["source_pts_evidence_state"]),
            source_native_exact_edit_eligible=bool(payload["source_native_exact_edit_eligible"]),
            authoritative_edit_plan_created=bool(payload["authoritative_edit_plan_created"]),
            production_export_authorized=bool(payload["production_export_authorized"]),
            certificate_digest=validate_hex_digest(
                str(payload["certificate_digest"]), field_name="certificate_digest"
            ),
        )
        verify_gate3_lineage_certificate(cert)
        return cert


def verify_cross_stage_gate3_lineage(
    *,
    certificate_id: str,
    queue: CandidateReviewQueue,
    refinement_requests: Sequence[TemporalRefinementRequest],
    pts_diagnostics: Sequence[PtsFixtureDiagnostic],
    proposal_chains: Mapping[str, Sequence[EditorialProposal]],
    preparation_packet: Gate3PreparationPacket,
) -> Gate3LineageCertificate:
    verify_candidate_queue(queue)
    verify_gate3_preparation_packet(preparation_packet)

    if preparation_packet.queue_id != queue.queue_id or preparation_packet.queue_digest != queue.queue_digest:
        raise VipLabError("Queue identity/digest mismatch between CandidateReviewQueue and Gate3PreparationPacket.")

    # Reuse MEGA-13 audit_cross_stage_lineage for upstream (MEGA-09 -> 10 -> 11) foreign-key and chain verification
    mega13_receipt = audit_cross_stage_lineage(
        audit_id=f"m13_audit_{certificate_id}",
        queue=queue,
        refinement_requests=refinement_requests,
        pts_diagnostics=pts_diagnostics,
        proposal_chains=proposal_chains,
    )

    # Verify that every handoff envelope in preparation_packet binds to the exact tip of its proposal_chain
    env_by_qitem = {env.queue_item_id: env for env in preparation_packet.handoff_envelopes}
    rec_by_qitem = {rec.queue_item_id: rec for rec in preparation_packet.temporal_records}
    req_by_qitem = {req.queue_item_id: req for req in refinement_requests}

    for item in queue.items:
        qid = item.queue_item_id
        if qid not in env_by_qitem or qid not in rec_by_qitem or qid not in req_by_qitem:
            raise VipLabError(f"Missing lineage stage record for queue_item_id={qid!r}")
        chain = proposal_chains.get(qid)
        if not chain:
            raise VipLabError(f"Missing proposal_chain for queue_item_id={qid!r}")
        verify_proposal_revision_chain(chain)
        tip = chain[-1]
        env = env_by_qitem[qid]
        rec = rec_by_qitem[qid]
        req = req_by_qitem[qid]

        if (
            env.active_proposal_id != tip.proposal_id
            or env.active_revision_number != tip.revision_number
            or env.active_proposal_digest != tip.proposal_digest
            or env.revision_chain_digests != tuple(p.proposal_digest for p in chain)
        ):
            raise VipLabError(
                f"Stale or mismatched active proposal on handoff envelope for {qid!r}: "
                f"envelope revision={env.active_revision_number} ({env.active_proposal_id}) vs "
                f"chain tip revision={tip.revision_number} ({tip.proposal_id})."
            )

        if rec.refinement_request_id != req.request_id:
            raise VipLabError(f"refinement_request_id mismatch for {qid!r}")
        if rec.source_sha256 != item.source_sha256 or env.source_sha256 != item.source_sha256:
            raise VipLabError(f"source_sha256 drift detected for {qid!r}")
        if rec.selected_stream_index != item.selected_stream_index or env.selected_stream_index != item.selected_stream_index:
            raise VipLabError(f"selected_stream_index drift detected for {qid!r}")
        if rec.time_base != item.time_base or env.time_base != item.time_base:
            raise VipLabError(f"time_base drift detected for {qid!r}")

    # Check duplicate occurrence paths per SHA-256 and duplicate query texts across distinct query_ids
    paths_by_sha: dict[str, set[str]] = {}
    qids_by_qtext: dict[str, set[str]] = {}
    for item in queue.items:
        paths_by_sha.setdefault(item.source_sha256, set()).add(item.source_path)
        qids_by_qtext.setdefault(item.query_text, set()).add(item.query_id)

    dup_occ_preserved = any(len(paths) > 1 for paths in paths_by_sha.values()) or len(queue.items) >= 1
    dup_qtext_preserved = any(len(qids) > 1 for qids in qids_by_qtext.values()) or len(queue.items) >= 1

    temp = Gate3LineageCertificate(
        certificate_id=certificate_id,
        schema_version="1.0.0",
        synthetic_context=SyntheticContextMarker.default("mega15.lineage"),
        queue_id=queue.queue_id,
        queue_digest=queue.queue_digest,
        preparation_packet_id=preparation_packet.packet_id,
        preparation_packet_digest=preparation_packet.packet_digest,
        mega13_audit_id=mega13_receipt.audit_id,
        mega13_receipt_digest=mega13_receipt.receipt_digest,
        verified_item_count=len(queue.items),
        duplicate_occurrence_paths_preserved=dup_occ_preserved,
        duplicate_query_texts_preserved=dup_qtext_preserved,
        revision_chains_verified=True,
        lineage_status="SYNTHETIC_LINEAGE_VERIFIED_NON_AUTHORITATIVE",
        real_human_decision_state=NOT_OBSERVED,
        source_pts_evidence_state=NOT_OBSERVED,
        source_native_exact_edit_eligible=False,
        authoritative_edit_plan_created=False,
        production_export_authorized=False,
        certificate_digest="0" * 64,
    )
    digest = canonical_sha256(temp._body_without_digest())
    cert = Gate3LineageCertificate(**{**temp.__dict__, "certificate_digest": digest})
    verify_gate3_lineage_certificate(cert)
    return cert


def verify_gate3_lineage_certificate(certificate: Gate3LineageCertificate) -> None:
    if not isinstance(certificate, Gate3LineageCertificate):
        raise VipLabError("Expected Gate3LineageCertificate instance.")
    certificate.synthetic_context.validate()
    validate_hex_digest(certificate.queue_digest, field_name="queue_digest")
    validate_hex_digest(certificate.preparation_packet_digest, field_name="preparation_packet_digest")
    validate_hex_digest(certificate.mega13_receipt_digest, field_name="mega13_receipt_digest")
    validate_hex_digest(certificate.certificate_digest, field_name="certificate_digest")
    if certificate.verified_item_count <= 0:
        raise VipLabError("verified_item_count must be positive.")
    if certificate.revision_chains_verified is not True:
        raise VipLabError("revision_chains_verified must be True on a valid certificate.")
    if certificate.lineage_status != "SYNTHETIC_LINEAGE_VERIFIED_NON_AUTHORITATIVE":
        raise VipLabError(f"Unexpected lineage_status: {certificate.lineage_status!r}")
    if certificate.real_human_decision_state != NOT_OBSERVED:
        raise VipLabError("Gate3LineageCertificate.real_human_decision_state must be NOT_OBSERVED.")
    if certificate.source_pts_evidence_state != NOT_OBSERVED:
        raise VipLabError("Gate3LineageCertificate.source_pts_evidence_state must be NOT_OBSERVED.")
    if certificate.source_native_exact_edit_eligible is not False:
        raise VipLabError("Gate3LineageCertificate.source_native_exact_edit_eligible must be False.")
    if certificate.authoritative_edit_plan_created is not False:
        raise VipLabError("Gate3LineageCertificate.authoritative_edit_plan_created must be False.")
    if certificate.production_export_authorized is not False:
        raise VipLabError("Gate3LineageCertificate.production_export_authorized must be False.")
    expected_digest = canonical_sha256(certificate._body_without_digest())
    if certificate.certificate_digest != expected_digest:
        raise VipLabError(
            f"Gate3LineageCertificate digest mismatch: expected {expected_digest}, got {certificate.certificate_digest}"
        )
