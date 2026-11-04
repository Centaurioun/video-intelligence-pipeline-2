"""MEGA-17 Workstream D: Gate-3 Native Temporal and Editorial Workflow Readiness (Roadmap Step 6).

Builds on MEGA-09, MEGA-10, MEGA-11, MEGA-13, MEGA-14, and MEGA-15 without
reimplementing MEGA-15. Consumes and verifies ``CandidateReviewQueue``,
``TemporalRefinementRequest``, ``PtsFixtureDiagnostic``, ``Gate3OfflinePreparationPacket``,
and ``Mega15LineageReceipt``; preserves full occurrence/revision/SHA-256/stream/timebase/
query_id/queue_item/proposal ``v1->v2->v3`` lineage; enforces the 5-way separation of
coordinate domains; produces a structured ``ReviewerHandoffRequirementsPacket`` (never
a completed human review); and enforces fail-closed refusals on A-7 stream namespace
ambiguity, IT-6 terminal-tail duration mismatch, and ``seconds * nominal_fps`` derivation.

Hard invariants:
- ``real_source_native_pts_evidence == "NOT_OBSERVED"``
- ``human_editorial_decision == "NOT_OBSERVED"``
- ``binding_eligible_real_edit == False``
- ``authoritative_edit_plan_created == False``
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from vip_lab.common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    canonical_sha256,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)
from vip_lab.mega14.scenario import SyntheticLabScenario
from vip_lab.mega15.lineage import (
    verify_gate3_offline_preparation_packet,
    verify_mega15_lineage_receipt,
)
from vip_lab.mega16.release_refusal import (
    Mega1516OfflineReport,
    run_mega15_16_offline_pipeline,
)


STAGE_ID = "MEGA-17.WORKSTREAM_D_EDITORIAL_WORKFLOW_READINESS"
EDITORIAL_READINESS_SCHEMA_VERSION = "vip_lab.mega17.editorial_readiness.v1"

COORDINATE_DOMAINS_SEPARATION: tuple[str, ...] = (
    "SEMANTIC_CANDIDATE_TIMESTAMPS",
    "SYNTHETIC_PTS_DIAGNOSTICS",
    "SOURCE_NATIVE_PTS_MEASUREMENTS",
    "APPROVED_EDITORIAL_DECISIONS",
    "OUTPUT_TIMELINE_COORDINATES",
)

REFUSAL_A7_STREAM_NAMESPACE_AMBIGUOUS = "REFUSAL_A7_STREAM_NAMESPACE_AMBIGUOUS"
REFUSAL_IT6_TERMINAL_TAIL_MISMATCH = "REFUSAL_IT6_TERMINAL_TAIL_MISMATCH"
REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN = "REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN"
REFUSAL_SEMANTIC_CANDIDATE_AS_EDIT_BOUNDARY = "REFUSAL_SEMANTIC_CANDIDATE_AS_EDIT_BOUNDARY"
REFUSAL_SYNTHETIC_DECISION_AS_REAL_HUMAN_AUTHORITY = (
    "REFUSAL_SYNTHETIC_DECISION_AS_REAL_HUMAN_AUTHORITY"
)
REFUSAL_AUTHORITATIVE_REAL_EDIT_PLAN_FORBIDDEN = (
    "REFUSAL_AUTHORITATIVE_REAL_EDIT_PLAN_FORBIDDEN"
)


@dataclass(frozen=True)
class ReviewerHandoffRequirementsPacket:
    """Structured requirements specification for future human editorial review (never a completed review)."""

    packet_role: str
    completed_human_review: bool
    technical_measurement_readiness: str
    editorial_judgment_readiness: str
    required_upstream_artifacts: tuple[str, ...]
    required_human_decision_fields: tuple[str, ...]
    forbidden_substitutions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_role": self.packet_role,
            "completed_human_review": self.completed_human_review,
            "technical_measurement_readiness": self.technical_measurement_readiness,
            "editorial_judgment_readiness": self.editorial_judgment_readiness,
            "required_upstream_artifacts": list(self.required_upstream_artifacts),
            "required_human_decision_fields": list(self.required_human_decision_fields),
            "forbidden_substitutions": list(self.forbidden_substitutions),
        }


@dataclass(frozen=True)
class EditorialWorkflowReadinessPacket:
    """Immutable Workstream D Gate-3 Native Temporal and Editorial Workflow Readiness packet."""

    schema_version: str
    real_source_native_pts_evidence: str
    human_editorial_decision: str
    binding_eligible_real_edit: bool
    authoritative_edit_plan_created: bool
    consumed_mega15_summary: Mapping[str, Any]
    lineage_spine: Mapping[str, Any]
    coordinate_domain_separation: Mapping[str, Mapping[str, Any]]
    reviewer_handoff_requirements: ReviewerHandoffRequirementsPacket
    guardrail_refusal_capabilities: Mapping[str, str]
    packet_digest: str

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "real_source_native_pts_evidence": self.real_source_native_pts_evidence,
            "human_editorial_decision": self.human_editorial_decision,
            "binding_eligible_real_edit": self.binding_eligible_real_edit,
            "authoritative_edit_plan_created": self.authoritative_edit_plan_created,
            "consumed_mega15_summary": dict(self.consumed_mega15_summary),
            "lineage_spine": dict(self.lineage_spine),
            "coordinate_domain_separation": {
                k: dict(v) for k, v in self.coordinate_domain_separation.items()
            },
            "reviewer_handoff_requirements": self.reviewer_handoff_requirements.to_dict(),
            "guardrail_refusal_capabilities": dict(self.guardrail_refusal_capabilities),
        }

    def to_dict(self) -> dict[str, Any]:
        out = self.payload_without_digest()
        out["packet_digest"] = self.packet_digest
        return out


def build_editorial_workflow_readiness_packet(
    *,
    mega15_16_report: Mega1516OfflineReport | None = None,
    scenario: SyntheticLabScenario | Mapping[str, Any] | None = None,
    workspace_root: str | Path | None = None,
) -> EditorialWorkflowReadinessPacket:
    """Build deterministic Workstream D packet by consuming verified MEGA-14/15/16 artifacts."""
    offline_rep = (
        mega15_16_report
        if mega15_16_report is not None
        else run_mega15_16_offline_pipeline()
    )

    prep_pkt = offline_rep.preparation_packet
    m15_receipt = offline_rep.mega15_lineage_receipt
    verify_gate3_offline_preparation_packet(prep_pkt)
    verify_mega15_lineage_receipt(m15_receipt)

    temp_rec = prep_pkt.temporal_records[0]
    ed_env = prep_pkt.handoff_envelopes[0]
    rev_entries = ed_env.revision_history

    consumed_mega15_summary = {
        "preparation_packet_id": prep_pkt.packet_id,
        "preparation_packet_digest": prep_pkt.packet_digest,
        "temporal_preparation_id": temp_rec.record_id,
        "temporal_preparation_digest": temp_rec.record_digest,
        "editorial_handoff_id": ed_env.envelope_id,
        "editorial_handoff_digest": ed_env.envelope_digest,
        "mega15_lineage_receipt_id": m15_receipt.receipt_id,
        "mega15_lineage_receipt_digest": m15_receipt.receipt_digest,
        "proposal_revision_numbers": [r.revision_number for r in rev_entries],
        "binding_eligible": ed_env.binding_eligible,
        "authoritative_human_decision": ed_env.accepted_authority,
    }

    lineage_spine = {
        "source_occurrence_id": f"occ-{temp_rec.source_revision_id}",
        "source_revision_id": temp_rec.source_revision_id,
        "source_sha256": temp_rec.source_sha256,
        "selected_stream_index": temp_rec.selected_stream_index,
        "timebase": {
            "num": temp_rec.timebase_num,
            "den": temp_rec.timebase_den,
        },
        "query_id": ed_env.query_id,
        "queue_item_id": temp_rec.queue_item_id,
        "temporal_request_id": temp_rec.upstream_request_id,
        "temporal_request_digest": temp_rec.upstream_request_digest,
        "proposal_v1_digest": rev_entries[0].proposal_digest,
        "proposal_v2_digest": rev_entries[1].proposal_digest,
        "proposal_v3_digest": rev_entries[2].proposal_digest,
    }

    coordinate_domain_separation = {
        "SEMANTIC_CANDIDATE_TIMESTAMPS": {
            "time_domain": "SEMANTIC_SECONDS",
            "evidence_class": "MATCHED",
            "binding_eligible": False,
            "role": "Candidate discovery hint only; never an exact frame or PTS cut boundary.",
        },
        "SYNTHETIC_PTS_DIAGNOSTICS": {
            "time_domain": "SYNTHETIC_PTS_DIAGNOSTIC",
            "evidence_class": NOT_OBSERVED,
            "binding_eligible": False,
            "requested_start_pts": temp_rec.requested_start_pts,
            "requested_end_pts": temp_rec.requested_end_pts,
            "role": "Synthetic PTS table diagnostic; never substitutes for byte-bound container measurement.",
        },
        "SOURCE_NATIVE_PTS_MEASUREMENTS": {
            "time_domain": "SOURCE_PTS",
            "evidence_state": NOT_OBSERVED,
            "binding_eligible": False,
            "predicate": "gate3.refinement.is_binding_eligible",
            "role": "Byte-bound ISO-BMFF / ffprobe source-native PTS & rational timebase measurement.",
        },
        "APPROVED_EDITORIAL_DECISIONS": {
            "time_domain": "HUMAN_DECISION_RECORD",
            "evidence_state": NOT_OBSERVED,
            "authoritative": False,
            "predicate": "gate3.editorial.EditorialDecision.real_authority_eligible",
            "role": "Authenticated human editorial ACCEPT/MODIFY/REJECT decision pinned to measured refinement.",
        },
        "OUTPUT_TIMELINE_COORDINATES": {
            "time_domain": "TIMELINE_TIME",
            "evidence_state": NOT_OBSERVED,
            "authoritative": False,
            "predicate": "gate3.plan.EditPlanRevision.export_eligible",
            "role": "Versioned EditPlanRevision placement interval; non-authoritative until real human decision and binding refinement.",
        },
    }

    handoff_req = ReviewerHandoffRequirementsPacket(
        packet_role="REVIEWER_HANDOFF_REQUIREMENTS_ONLY",
        completed_human_review=False,
        technical_measurement_readiness="SYNTHETIC_PREFLIGHT_READY_REAL_PTS_NOT_OBSERVED",
        editorial_judgment_readiness="AWAITING_REAL_MEASUREMENT_AND_HUMAN_PRINCIPAL",
        required_upstream_artifacts=(
            "Byte-bound Gate-3 C2 source-native refinement record (is_binding_eligible == True)",
            "Proven stream identity evidence (gate3.stream_identity.StreamIdentityEvidence.state == 'PROVEN')",
            "Sealed ReviewBundle (vip_fvs.review_bundle.ReviewBundle)",
        ),
        required_human_decision_fields=(
            "decision_id",
            "principal_kind == 'human'",
            "principal_ref (non-fixture)",
            "decided_on_refinement",
            "decided_on_revision",
            "decision_class in ('ACCEPT', 'REJECT', 'MODIFY')",
            "rationale (non-empty)",
        ),
        forbidden_substitutions=(
            "Semantic candidate timestamp as edit cut boundary",
            "seconds * nominal_fps VFR derivation",
            "Model/tool principal as human editorial authority",
            "Synthetic proposal v1/v2/v3 as authoritative EditPlanRevision(plan_scope='REAL')",
        ),
    )

    guardrail_refusal_capabilities = {
        "a7_stream_namespace_ambiguity": REFUSAL_A7_STREAM_NAMESPACE_AMBIGUOUS,
        "it6_terminal_tail_duration_mismatch": REFUSAL_IT6_TERMINAL_TAIL_MISMATCH,
        "vfr_nominal_fps_multiplication": REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN,
        "semantic_candidate_as_cut_boundary": REFUSAL_SEMANTIC_CANDIDATE_AS_EDIT_BOUNDARY,
        "synthetic_decision_as_real_human": REFUSAL_SYNTHETIC_DECISION_AS_REAL_HUMAN_AUTHORITY,
    }

    provisional = EditorialWorkflowReadinessPacket(
        schema_version=EDITORIAL_READINESS_SCHEMA_VERSION,
        real_source_native_pts_evidence=NOT_OBSERVED,
        human_editorial_decision=NOT_OBSERVED,
        binding_eligible_real_edit=False,
        authoritative_edit_plan_created=False,
        consumed_mega15_summary=consumed_mega15_summary,
        lineage_spine=lineage_spine,
        coordinate_domain_separation=coordinate_domain_separation,
        reviewer_handoff_requirements=handoff_req,
        guardrail_refusal_capabilities=guardrail_refusal_capabilities,
        packet_digest="0" * 64,
    )
    digest = canonical_sha256(provisional.payload_without_digest())
    return EditorialWorkflowReadinessPacket(
        schema_version=provisional.schema_version,
        real_source_native_pts_evidence=NOT_OBSERVED,
        human_editorial_decision=NOT_OBSERVED,
        binding_eligible_real_edit=False,
        authoritative_edit_plan_created=False,
        consumed_mega15_summary=provisional.consumed_mega15_summary,
        lineage_spine=provisional.lineage_spine,
        coordinate_domain_separation=provisional.coordinate_domain_separation,
        reviewer_handoff_requirements=provisional.reviewer_handoff_requirements,
        guardrail_refusal_capabilities=provisional.guardrail_refusal_capabilities,
        packet_digest=digest,
    )


def verify_editorial_workflow_readiness_packet(
    packet: EditorialWorkflowReadinessPacket | Mapping[str, Any],
) -> dict[str, Any]:
    """Verify integrity and Section 9 invariants of an EditorialWorkflowReadinessPacket."""
    raw = (
        packet.to_dict()
        if isinstance(packet, EditorialWorkflowReadinessPacket)
        else dict(packet)
    )
    if raw.get("schema_version") != EDITORIAL_READINESS_SCHEMA_VERSION:
        raise VipLabError(
            "EDITORIAL_READINESS_SCHEMA_MISMATCH",
            f"Expected {EDITORIAL_READINESS_SCHEMA_VERSION}, got {raw.get('schema_version')!r}",
        )
    if (
        raw.get("real_source_native_pts_evidence") != NOT_OBSERVED
        or raw.get("human_editorial_decision") != NOT_OBSERVED
        or raw.get("binding_eligible_real_edit") is not False
        or raw.get("authoritative_edit_plan_created") is not False
    ):
        raise VipLabError(
            "EDITORIAL_READINESS_INVARIANT_VIOLATION",
            "EditorialWorkflowReadinessPacket violated mandatory Section 9 invariants.",
        )
    declared_digest = validate_hex_digest(
        str(raw.get("packet_digest", "")),
        field_name="packet_digest",
    )
    body = {k: v for k, v in raw.items() if k != "packet_digest"}
    computed = canonical_sha256(body)
    if declared_digest != computed:
        raise VipLabError(
            "EDITORIAL_READINESS_DIGEST_MISMATCH",
            f"packet_digest mismatch: declared {declared_digest} != computed {computed}",
        )
    return raw


def inspect_editorial_workflow_readiness(
    payload: Mapping[str, Any] | None = None,
) -> ReadinessPacket:
    """Inspect Workstream D temporal/editorial readiness and enforce fail-closed refusals."""
    raw_payload = dict(payload) if isinstance(payload, Mapping) else {}
    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(raw_payload)

    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="WORKSTREAM_D_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Ignored untrusted authority flags in Workstream D payload.",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(cleaned.get("a7_stream_namespace_ambiguous", False)):
        blockers.append(REFUSAL_A7_STREAM_NAMESPACE_AMBIGUOUS)
        reasons.append(REFUSAL_A7_STREAM_NAMESPACE_AMBIGUOUS)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_A7_STREAM_NAMESPACE_AMBIGUOUS,
                status=ReadinessStatus.BLOCKED,
                message="A-7 stream identity is ambiguous or unmapped between ffprobe stream index and ISO-BMFF track_ID.",
            )
        )

    if bool(cleaned.get("it6_terminal_tail_mismatch", False)):
        blockers.append(REFUSAL_IT6_TERMINAL_TAIL_MISMATCH)
        reasons.append(REFUSAL_IT6_TERMINAL_TAIL_MISMATCH)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_IT6_TERMINAL_TAIL_MISMATCH,
                status=ReadinessStatus.BLOCKED,
                message="IT-6 terminal-tail duration consistency mismatch refuses binding refinement.",
            )
        )

    if bool(cleaned.get("derive_pts_from_nominal_fps", False)):
        blockers.append(REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN)
        reasons.append(REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN,
                status=ReadinessStatus.BLOCKED,
                message="Deriving VFR frame/PTS boundaries via seconds * nominal_fps is strictly forbidden.",
            )
        )

    if bool(raw_payload.get("use_semantic_timestamp_as_edit_cut", False)):
        blockers.append(REFUSAL_SEMANTIC_CANDIDATE_AS_EDIT_BOUNDARY)
        reasons.append(REFUSAL_SEMANTIC_CANDIDATE_AS_EDIT_BOUNDARY)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_SEMANTIC_CANDIDATE_AS_EDIT_BOUNDARY,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Semantic candidate timestamps cannot establish frame-accurate edit boundaries.",
            )
        )

    if bool(raw_payload.get("claim_synthetic_decision_is_real_human", False)):
        blockers.append(REFUSAL_SYNTHETIC_DECISION_AS_REAL_HUMAN_AUTHORITY)
        reasons.append(REFUSAL_SYNTHETIC_DECISION_AS_REAL_HUMAN_AUTHORITY)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_SYNTHETIC_DECISION_AS_REAL_HUMAN_AUTHORITY,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Synthetic editorial proposal or fixture principal never confers real human editorial authority.",
            )
        )

    if bool(raw_payload.get("claim_authoritative_edit_plan_created", False)):
        blockers.append(REFUSAL_AUTHORITATIVE_REAL_EDIT_PLAN_FORBIDDEN)
        reasons.append(REFUSAL_AUTHORITATIVE_REAL_EDIT_PLAN_FORBIDDEN)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_AUTHORITATIVE_REAL_EDIT_PLAN_FORBIDDEN,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Authoritative real EditPlanRevision cannot be created without byte-bound PTS refinement and real human decision.",
            )
        )

    pkt = build_editorial_workflow_readiness_packet()

    has_auth_refusal = any(f.status == ReadinessStatus.NOT_AUTHORIZED for f in findings)
    if has_auth_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("EDITORIAL_WORKFLOW_OFFLINE_READINESS_VERIFIED")
        findings.append(
            ReadinessFinding(
                code="EDITORIAL_WORKFLOW_OFFLINE_READINESS_VERIFIED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Consumed MEGA-15 artifacts, verified 5-way coordinate separation, and emitted reviewer handoff requirements.",
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_AUTHORIZED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "packet_digest": pkt.packet_digest,
            "real_source_native_pts_evidence": NOT_OBSERVED,
            "human_editorial_decision": NOT_OBSERVED,
            "binding_eligible_real_edit": False,
            "authoritative_edit_plan_created": False,
            "mega15_preparation_packet_digest": pkt.consumed_mega15_summary[
                "preparation_packet_digest"
            ],
        },
    )
