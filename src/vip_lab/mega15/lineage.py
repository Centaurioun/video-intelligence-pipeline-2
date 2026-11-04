"""MEGA-15.3 — Cross-Artifact Lineage & Duplicate/Query Identity Preservation Verifier.

Verifies end-to-end lineage across:
- MEGA-09 `CandidateReviewQueue`
- MEGA-10 `TemporalRefinementRequest`
- MEGA-11 `EditorialProposal` revision chains
- MEGA-13 `LineageAuditReceipt` (`audit_cross_stage_lineage`)
- MEGA-15.1 `TemporalPreparationRecord`
- MEGA-15.2 `EditorialHandoffEnvelope` & `Gate3OfflinePreparationPacket`
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vip_lab.common import (
    SyntheticContextMarker,
    VipLabError,
    canonical_sha256,
)
from vip_lab.mega09 import CandidateReviewQueue, verify_candidate_queue
from vip_lab.mega10 import TemporalRefinementRequest, verify_temporal_refinement_request
from vip_lab.mega11 import EditorialProposal
from vip_lab.mega13 import LineageAuditReceipt, audit_cross_stage_lineage
from vip_lab.mega15.editorial_handoff import (
    Gate3OfflinePreparationPacket,
    REFUSAL_CROSS_STAGE_JOIN_MISMATCH,
    REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE,
    REFUSAL_PROPOSAL_CHAIN_BROKEN,
    REFUSAL_QUERY_IDENTITY_COLLAPSE,
    verify_gate3_offline_preparation_packet,
)
from vip_lab.mega15.temporal_preflight import (
    ensure_non_empty_str,
    make_synthetic_context,
    parse_synthetic_context_dict,
    raise_mega15_error,
    serialize_synthetic_context,
    validate_synthetic_context,
)

MEGA15_LINEAGE_SCHEMA_VERSION = "1.0.0"
MEGA15_LINEAGE_KIND = "vip_lab.mega15.lineage_receipt"

REFUSAL_MEGA15_LINEAGE_BROKEN = "REFUSAL_MEGA15_LINEAGE_BROKEN"
REFUSAL_STALE_PROPOSAL_REVISION = "REFUSAL_STALE_PROPOSAL_REVISION_FORBIDDEN"


@dataclass(frozen=True)
class Mega15LineageReceipt:
    """Deterministic lineage receipt binding MEGA-09..13 to MEGA-15 preparation artifacts."""

    schema_version: str
    kind: str
    receipt_id: str
    catalog_id: str
    queue_digest: str
    upstream_lineage_audit_id: str
    upstream_lineage_receipt_digest: str
    per_item_lineage_receipt_digests: tuple[str, ...]
    preparation_packet_id: str
    preparation_packet_digest: str
    temporal_record_digests: tuple[str, ...]
    handoff_envelope_digests: tuple[str, ...]
    latest_proposal_digests: tuple[str, ...]
    duplicate_occurrence_paths_preserved: bool
    duplicate_query_texts_preserved: bool
    lineage_valid: bool
    synthetic_context: SyntheticContextMarker
    receipt_digest: str

    @property
    def queue_id(self) -> str:
        """Compatibility alias returning ``catalog_id``."""
        return self.catalog_id

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "receipt_id": self.receipt_id,
            "catalog_id": self.catalog_id,
            "queue_digest": self.queue_digest,
            "upstream_lineage_audit_id": self.upstream_lineage_audit_id,
            "upstream_lineage_receipt_digest": self.upstream_lineage_receipt_digest,
            "per_item_lineage_receipt_digests": list(self.per_item_lineage_receipt_digests),
            "preparation_packet_id": self.preparation_packet_id,
            "preparation_packet_digest": self.preparation_packet_digest,
            "temporal_record_digests": list(self.temporal_record_digests),
            "handoff_envelope_digests": list(self.handoff_envelope_digests),
            "latest_proposal_digests": list(self.latest_proposal_digests),
            "duplicate_occurrence_paths_preserved": self.duplicate_occurrence_paths_preserved,
            "duplicate_query_texts_preserved": self.duplicate_query_texts_preserved,
            "lineage_valid": self.lineage_valid,
            "synthetic_context": serialize_synthetic_context(self.synthetic_context),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._digest_payload()
        payload["receipt_digest"] = self.receipt_digest
        return payload

    def validate(self) -> None:
        if self.schema_version != MEGA15_LINEAGE_SCHEMA_VERSION:
            raise_mega15_error(
                "MEGA15_LINEAGE_SCHEMA_MISMATCH",
                f"Unsupported schema_version: {self.schema_version!r}",
            )
        if self.kind != MEGA15_LINEAGE_KIND:
            raise_mega15_error(
                "MEGA15_LINEAGE_KIND_MISMATCH",
                f"Unsupported kind: {self.kind!r}",
            )
        ensure_non_empty_str(self.receipt_id, "receipt_id")
        ensure_non_empty_str(self.catalog_id, "catalog_id")
        ensure_non_empty_str(self.queue_digest, "queue_digest")
        ensure_non_empty_str(self.upstream_lineage_audit_id, "upstream_lineage_audit_id")
        ensure_non_empty_str(
            self.upstream_lineage_receipt_digest, "upstream_lineage_receipt_digest"
        )
        ensure_non_empty_str(self.preparation_packet_id, "preparation_packet_id")
        ensure_non_empty_str(self.preparation_packet_digest, "preparation_packet_digest")
        validate_synthetic_context(self.synthetic_context)

        if self.lineage_valid is not True:
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                "Mega15LineageReceipt requires lineage_valid=True",
            )
        if not isinstance(self.duplicate_occurrence_paths_preserved, bool):
            raise_mega15_error(
                REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE,
                "duplicate_occurrence_paths_preserved must be a bool",
            )
        if not isinstance(self.duplicate_query_texts_preserved, bool):
            raise_mega15_error(
                REFUSAL_QUERY_IDENTITY_COLLAPSE,
                "duplicate_query_texts_preserved must be a bool",
            )
        if (
            not self.per_item_lineage_receipt_digests
            or not self.temporal_record_digests
            or not self.handoff_envelope_digests
            or not self.latest_proposal_digests
        ):
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                "Digest tuples in Mega15LineageReceipt must be non-empty",
            )
        if not (
            len(self.per_item_lineage_receipt_digests)
            == len(self.temporal_record_digests)
            == len(self.handoff_envelope_digests)
            == len(self.latest_proposal_digests)
        ):
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                "Digest tuple lengths in Mega15LineageReceipt must match",
            )

        expected_digest = canonical_sha256(self._digest_payload())
        if self.receipt_digest != expected_digest:
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                f"receipt_digest mismatch: expected {expected_digest}, got {self.receipt_digest}",
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Mega15LineageReceipt":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                "Payload must be a mapping",
            )
        raw_ctx = payload.get("synthetic_context")
        if not isinstance(raw_ctx, Mapping):
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                "synthetic_context must be a mapping",
            )
        raw_t = payload.get("temporal_record_digests")
        raw_e = payload.get("handoff_envelope_digests")
        raw_p = payload.get("latest_proposal_digests")
        raw_l = payload.get("per_item_lineage_receipt_digests", raw_p)
        if (
            not isinstance(raw_t, Sequence)
            or not isinstance(raw_e, Sequence)
            or not isinstance(raw_p, Sequence)
            or not isinstance(raw_l, Sequence)
        ):
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                "Digest fields must be sequences",
            )
        receipt = cls(
            schema_version=str(payload.get("schema_version", "")),
            kind=str(payload.get("kind", "")),
            receipt_id=str(payload.get("receipt_id", "")),
            catalog_id=str(payload.get("catalog_id", payload.get("queue_id", ""))),
            queue_digest=str(payload.get("queue_digest", "")),
            upstream_lineage_audit_id=str(payload.get("upstream_lineage_audit_id", "")),
            upstream_lineage_receipt_digest=str(
                payload.get("upstream_lineage_receipt_digest", "")
            ),
            per_item_lineage_receipt_digests=tuple(str(x) for x in raw_l),
            preparation_packet_id=str(payload.get("preparation_packet_id", "")),
            preparation_packet_digest=str(payload.get("preparation_packet_digest", "")),
            temporal_record_digests=tuple(str(x) for x in raw_t),
            handoff_envelope_digests=tuple(str(x) for x in raw_e),
            latest_proposal_digests=tuple(str(x) for x in raw_p),
            duplicate_occurrence_paths_preserved=bool(
                payload.get("duplicate_occurrence_paths_preserved", False)
            ),
            duplicate_query_texts_preserved=bool(
                payload.get("duplicate_query_texts_preserved", False)
            ),
            lineage_valid=bool(payload.get("lineage_valid", False)),
            synthetic_context=parse_synthetic_context_dict(raw_ctx),
            receipt_digest=str(payload.get("receipt_digest", "")),
        )
        receipt.validate()
        return receipt


def audit_mega15_lineage(
    *,
    queue: CandidateReviewQueue,
    temporal_requests: Sequence[TemporalRefinementRequest],
    proposal_chains: Sequence[Sequence[EditorialProposal]],
    preparation_packet: Gate3OfflinePreparationPacket,
    upstream_lineage_receipt: LineageAuditReceipt | Sequence[LineageAuditReceipt] | None = None,
    receipt_id: str = "m15_lineage_default",
) -> Mega15LineageReceipt:
    """Verify full cross-artifact lineage from MEGA-09..13 through MEGA-15 preparation packet."""
    verify_candidate_queue(queue.to_dict())
    verify_gate3_offline_preparation_packet(preparation_packet)

    if (
        preparation_packet.catalog_id != queue.catalog_id
        or preparation_packet.queue_digest != queue.queue_digest
    ):
        raise_mega15_error(
            REFUSAL_MEGA15_LINEAGE_BROKEN,
            "Preparation packet queue identity/digest does not match CandidateReviewQueue",
        )

    if not (
        len(queue.items)
        == len(temporal_requests)
        == len(proposal_chains)
        == len(preparation_packet.temporal_records)
        == len(preparation_packet.handoff_envelopes)
    ):
        raise_mega15_error(
            REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE,
            "Item counts across queue, temporal_requests, proposal_chains, and preparation_packet must match 1-to-1",
        )

    t_digests: list[str] = []
    e_digests: list[str] = []
    p_digests: list[str] = []
    per_item_receipts: list[LineageAuditReceipt] = []

    for q_item, t_req, p_chain, t_rec, h_env in zip(
        queue.items,
        temporal_requests,
        proposal_chains,
        preparation_packet.temporal_records,
        preparation_packet.handoff_envelopes,
    ):
        verify_temporal_refinement_request(t_req.to_dict())
        if not p_chain:
            raise_mega15_error(
                REFUSAL_PROPOSAL_CHAIN_BROKEN,
                f"Empty proposal chain for item {q_item.queue_item_id!r}",
            )

        tip_proposal = p_chain[-1]
        if (
            t_rec.upstream_request_id != t_req.request_id
            or t_rec.upstream_request_digest != t_req.request_digest
        ):
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                f"TemporalPreparationRecord {t_rec.record_id!r} does not match TemporalRefinementRequest {t_req.request_id!r}",
            )

        if (
            h_env.latest_proposal_digest != tip_proposal.proposal_digest
            or h_env.latest_proposal_version != tip_proposal.proposal_version
            or len(h_env.revision_history) != len(p_chain)
        ):
            raise_mega15_error(
                REFUSAL_STALE_PROPOSAL_REVISION,
                f"EditorialHandoffEnvelope {h_env.envelope_id!r} does not reference latest proposal revision tip",
            )

        try:
            item_receipt = audit_cross_stage_lineage(
                candidate_queue=queue,
                temporal_request=t_req,
                editorial_proposal=tip_proposal,
                proposal_revision_chain=p_chain,
            )
        except VipLabError as exc:
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                f"Upstream MEGA-13 lineage audit failed for item {q_item.queue_item_id!r}: {exc.code}: {exc.message}",
            )

        per_item_receipts.append(item_receipt)
        t_digests.append(t_rec.record_digest)
        e_digests.append(h_env.envelope_digest)
        p_digests.append(tip_proposal.proposal_digest)

    per_item_digests = tuple(r.receipt_digest for r in per_item_receipts)

    if upstream_lineage_receipt is not None:
        if isinstance(upstream_lineage_receipt, LineageAuditReceipt):
            if (
                upstream_lineage_receipt.lineage_valid is not True
                or upstream_lineage_receipt.queue_digest != queue.queue_digest
                or upstream_lineage_receipt.receipt_digest not in set(per_item_digests)
            ):
                raise_mega15_error(
                    REFUSAL_MEGA15_LINEAGE_BROKEN,
                    "Provided upstream LineageAuditReceipt does not match audited MEGA-15 lineage",
                )
            primary_upstream_digest = upstream_lineage_receipt.receipt_digest
            primary_audit_id = (
                f"laudit_{upstream_lineage_receipt.queue_item_id}_"
                f"{upstream_lineage_receipt.receipt_digest[:12]}"
            )
        elif isinstance(upstream_lineage_receipt, Sequence):
            if len(upstream_lineage_receipt) != len(per_item_receipts):
                raise_mega15_error(
                    REFUSAL_MEGA15_LINEAGE_BROKEN,
                    "Sequence of upstream LineageAuditReceipts length mismatch",
                )
            for given, computed in zip(upstream_lineage_receipt, per_item_receipts):
                if (
                    not isinstance(given, LineageAuditReceipt)
                    or given.lineage_valid is not True
                    or given.receipt_digest != computed.receipt_digest
                ):
                    raise_mega15_error(
                        REFUSAL_MEGA15_LINEAGE_BROKEN,
                        "Provided upstream LineageAuditReceipt sequence element mismatch",
                    )
            primary_upstream_digest = per_item_receipts[0].receipt_digest
            primary_audit_id = (
                f"laudit_{per_item_receipts[0].queue_item_id}_"
                f"{per_item_receipts[0].receipt_digest[:12]}"
            )
        else:
            raise_mega15_error(
                REFUSAL_MEGA15_LINEAGE_BROKEN,
                "Invalid upstream_lineage_receipt type",
            )
    else:
        primary_upstream_digest = per_item_receipts[0].receipt_digest
        primary_audit_id = (
            f"laudit_{per_item_receipts[0].queue_item_id}_"
            f"{per_item_receipts[0].receipt_digest[:12]}"
        )

    # Genuine verification of duplicate source_sha256 occurrences with distinct (source_path, revision_id, content_id)
    upstream_occ_tuples = [
        (
            it.queue_item_id,
            it.revision_id,
            it.content_id,
            it.source_path,
            it.source_sha256,
        )
        for it in queue.items
    ]
    temporal_occ_tuples = [
        (
            rec.queue_item_id,
            rec.revision_id,
            rec.content_id,
            rec.source_path,
            rec.source_sha256,
        )
        for rec in preparation_packet.temporal_records
    ]
    handoff_occ_tuples = [
        (
            env.queue_item_id,
            env.revision_id,
            env.content_id,
            env.source_path,
            env.source_sha256,
        )
        for env in preparation_packet.handoff_envelopes
    ]
    packet_occ_tuples = [
        (
            occ.get("queue_item_id", ""),
            occ.get("revision_id", ""),
            occ.get("content_id", ""),
            occ.get("source_path", ""),
            occ.get("source_sha256", ""),
        )
        for occ in preparation_packet.occurrence_identities
    ]

    if (
        temporal_occ_tuples != upstream_occ_tuples
        or handoff_occ_tuples != upstream_occ_tuples
        or packet_occ_tuples != upstream_occ_tuples
    ):
        raise_mega15_error(
            REFUSAL_OCCURRENCE_IDENTITY_COLLAPSE,
            "Occurrence tuples were collapsed, dropped, or relabeled between queue and preparation packet",
        )

    sha_to_distinct_occ: dict[str, set[tuple[str, str, str]]] = {}
    sha_to_distinct_paths: dict[str, set[str]] = {}
    for _item_id, rev_id, cnt_id, src_path, sha in upstream_occ_tuples:
        sha_to_distinct_occ.setdefault(sha, set()).add((src_path, rev_id, cnt_id))
        sha_to_distinct_paths.setdefault(sha, set()).add(src_path)

    has_duplicate_occurrences_in_input = any(
        len(paths) >= 2 and len(sha_to_distinct_occ[sha]) >= 2
        for sha, paths in sha_to_distinct_paths.items()
    )
    dup_occ_preserved = bool(
        has_duplicate_occurrences_in_input
        and temporal_occ_tuples == upstream_occ_tuples
        and handoff_occ_tuples == upstream_occ_tuples
        and packet_occ_tuples == upstream_occ_tuples
    )

    # Genuine verification of identical query_text under distinct query_id
    upstream_query_tuples = [
        (it.queue_item_id, it.query_id, it.query_text) for it in queue.items
    ]
    handoff_query_tuples = [
        (env.queue_item_id, env.query_id, env.query_text)
        for env in preparation_packet.handoff_envelopes
    ]
    packet_query_tuples = [
        (
            q.get("queue_item_id", ""),
            q.get("query_id", ""),
            q.get("query_text", ""),
        )
        for q in preparation_packet.query_identities
    ]
    temporal_query_ids = [
        (rec.queue_item_id, rec.query_id)
        for rec in preparation_packet.temporal_records
    ]
    expected_temporal_query_ids = [
        (it.queue_item_id, it.query_id) for it in queue.items
    ]

    if (
        handoff_query_tuples != upstream_query_tuples
        or packet_query_tuples != upstream_query_tuples
        or temporal_query_ids != expected_temporal_query_ids
    ):
        raise_mega15_error(
            REFUSAL_QUERY_IDENTITY_COLLAPSE,
            "Query tuples were collapsed, dropped, or relabeled between queue and preparation packet",
        )

    qtext_to_qids: dict[str, set[str]] = {}
    for _item_id, qid, qtext in upstream_query_tuples:
        qtext_to_qids.setdefault(qtext, set()).add(qid)

    has_duplicate_query_texts_in_input = any(
        len(qids) >= 2 for qids in qtext_to_qids.values()
    )
    dup_qtext_preserved = bool(
        has_duplicate_query_texts_in_input
        and handoff_query_tuples == upstream_query_tuples
        and packet_query_tuples == upstream_query_tuples
        and temporal_query_ids == expected_temporal_query_ids
    )

    syn_ctx = make_synthetic_context()
    provisional = Mega15LineageReceipt(
        schema_version=MEGA15_LINEAGE_SCHEMA_VERSION,
        kind=MEGA15_LINEAGE_KIND,
        receipt_id=receipt_id,
        catalog_id=queue.catalog_id,
        queue_digest=queue.queue_digest,
        upstream_lineage_audit_id=primary_audit_id,
        upstream_lineage_receipt_digest=primary_upstream_digest,
        per_item_lineage_receipt_digests=per_item_digests,
        preparation_packet_id=preparation_packet.packet_id,
        preparation_packet_digest=preparation_packet.packet_digest,
        temporal_record_digests=tuple(t_digests),
        handoff_envelope_digests=tuple(e_digests),
        latest_proposal_digests=tuple(p_digests),
        duplicate_occurrence_paths_preserved=dup_occ_preserved,
        duplicate_query_texts_preserved=dup_qtext_preserved,
        lineage_valid=True,
        synthetic_context=syn_ctx,
        receipt_digest="",
    )
    digest = canonical_sha256(provisional._digest_payload())
    final_receipt = Mega15LineageReceipt(
        **{**provisional.__dict__, "receipt_digest": digest}
    )
    final_receipt.validate()
    return final_receipt


def verify_mega15_lineage_receipt(
    receipt: Mega15LineageReceipt | Mapping[str, Any],
) -> Mega15LineageReceipt:
    """Verify and return a `Mega15LineageReceipt`."""
    if isinstance(receipt, Mega15LineageReceipt):
        receipt.validate()
        return receipt
    return Mega15LineageReceipt.from_dict(receipt)
