from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from vip_fvs.real_preview_receipt import FIXTURE_NOT_OBSERVED_REQUIRED
from vip_lab.common import (
    NOT_OBSERVED,
    SyntheticContextMarker,
    VipLabError,
    canonical_sha256,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)
from vip_lab.mega09 import CandidateReviewQueue, verify_candidate_queue
from vip_lab.mega10 import (
    PtsFixtureDiagnostic,
    TemporalRefinementRequest,
    build_temporal_refinement_request,
    evaluate_pts_fixture_diagnostic,
)
from vip_lab.mega11 import (
    EditorialProposal,
    advance_proposal_revision,
    build_editorial_proposal,
)
from vip_lab.mega13 import (
    CANONICAL_RELEASE_BLOCKER_CODES,
    ReleaseBlockerSummary,
    audit_cross_stage_lineage,
    build_release_blocker_summary,
    evaluate_qc_readiness,
)
from vip_lab.mega14 import (
    default_single_arm_scenario,
    default_three_arm_scenario,
    run_end_to_end_synthetic_lab,
)
from vip_lab.mega15 import (
    Gate3LineageCertificate,
    Gate3PreparationPacket,
    build_gate3_preparation_packet,
    build_temporal_preparation_record,
    verify_cross_stage_gate3_lineage,
    verify_gate3_lineage_certificate,
    verify_gate3_preparation_packet,
)
from vip_lab.mega16.qc_requirements import (
    QCRequirementManifest,
    build_qc_requirement_manifest,
    verify_qc_requirement_manifest,
)
from vip_lab.mega16.render_preflight import (
    RenderPreflightReport,
    build_render_preflight_report,
    verify_render_preflight_report,
)

MEGA15_16_PROGRAM_VERSION = "LAB-MEGA-15-16-v1.0.0"
REFUSAL_PRODUCTION_EXPORT_NOT_AUTHORIZED = "REFUSAL_PRODUCTION_EXPORT_NOT_AUTHORIZED"


@dataclass(frozen=True)
class ExportReadinessPacket:
    packet_id: str
    schema_version: str
    lab_program_version: str
    synthetic_context: SyntheticContextMarker
    preparation_packet_id: str
    preparation_packet_digest: str
    lineage_certificate_id: str
    lineage_certificate_digest: str
    render_preflight_id: str
    render_preflight_digest: str
    qc_manifest_id: str
    qc_manifest_digest: str
    release_blocker_summary_id: str
    release_blocker_summary_digest: str
    blocker_codes: tuple[str, ...]
    not_observed_fields: tuple[str, ...]
    real_human_decision_state: str
    source_pts_evidence_state: str
    source_native_exact_edit_eligible: bool
    authoritative_edit_plan_created: bool
    preview_policy_authorized: bool
    render_executed: bool
    technical_qc_observed: str
    visual_editorial_qc_observed: str
    audio_editorial_qc_observed: str
    production_export_authorized: bool
    export_status: str
    stripped_untrusted_authority_keys: tuple[str, ...]
    packet_digest: str

    def _body_without_digest(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "schema_version": self.schema_version,
            "lab_program_version": self.lab_program_version,
            "synthetic_context": self.synthetic_context.to_dict(),
            "preparation_packet_id": self.preparation_packet_id,
            "preparation_packet_digest": self.preparation_packet_digest,
            "lineage_certificate_id": self.lineage_certificate_id,
            "lineage_certificate_digest": self.lineage_certificate_digest,
            "render_preflight_id": self.render_preflight_id,
            "render_preflight_digest": self.render_preflight_digest,
            "qc_manifest_id": self.qc_manifest_id,
            "qc_manifest_digest": self.qc_manifest_digest,
            "release_blocker_summary_id": self.release_blocker_summary_id,
            "release_blocker_summary_digest": self.release_blocker_summary_digest,
            "blocker_codes": list(self.blocker_codes),
            "not_observed_fields": list(self.not_observed_fields),
            "real_human_decision_state": self.real_human_decision_state,
            "source_pts_evidence_state": self.source_pts_evidence_state,
            "source_native_exact_edit_eligible": self.source_native_exact_edit_eligible,
            "authoritative_edit_plan_created": self.authoritative_edit_plan_created,
            "preview_policy_authorized": self.preview_policy_authorized,
            "render_executed": self.render_executed,
            "technical_qc_observed": self.technical_qc_observed,
            "visual_editorial_qc_observed": self.visual_editorial_qc_observed,
            "audio_editorial_qc_observed": self.audio_editorial_qc_observed,
            "production_export_authorized": self.production_export_authorized,
            "export_status": self.export_status,
            "stripped_untrusted_authority_keys": list(self.stripped_untrusted_authority_keys),
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._body_without_digest()
        body["packet_digest"] = self.packet_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ExportReadinessPacket:
        if not isinstance(payload, Mapping):
            raise VipLabError("ExportReadinessPacket payload must be a mapping.")
        if bool(payload.get("production_export_authorized")) or payload.get("export_status") != "REFUSED_NOT_AUTHORIZED":
            raise VipLabError(
                f"{REFUSAL_PRODUCTION_EXPORT_NOT_AUTHORIZED}: production export cannot be authorized or marked ready in synthetic offline preparation."
            )
        packet = cls(
            packet_id=str(payload["packet_id"]),
            schema_version=str(payload["schema_version"]),
            lab_program_version=str(payload["lab_program_version"]),
            synthetic_context=SyntheticContextMarker.from_dict(payload["synthetic_context"]),
            preparation_packet_id=str(payload["preparation_packet_id"]),
            preparation_packet_digest=validate_hex_digest(
                str(payload["preparation_packet_digest"]), field_name="preparation_packet_digest"
            ),
            lineage_certificate_id=str(payload["lineage_certificate_id"]),
            lineage_certificate_digest=validate_hex_digest(
                str(payload["lineage_certificate_digest"]), field_name="lineage_certificate_digest"
            ),
            render_preflight_id=str(payload["render_preflight_id"]),
            render_preflight_digest=validate_hex_digest(
                str(payload["render_preflight_digest"]), field_name="render_preflight_digest"
            ),
            qc_manifest_id=str(payload["qc_manifest_id"]),
            qc_manifest_digest=validate_hex_digest(
                str(payload["qc_manifest_digest"]), field_name="qc_manifest_digest"
            ),
            release_blocker_summary_id=str(payload["release_blocker_summary_id"]),
            release_blocker_summary_digest=validate_hex_digest(
                str(payload["release_blocker_summary_digest"]),
                field_name="release_blocker_summary_digest",
            ),
            blocker_codes=tuple(str(c) for c in payload["blocker_codes"]),
            not_observed_fields=tuple(str(f) for f in payload["not_observed_fields"]),
            real_human_decision_state=str(payload["real_human_decision_state"]),
            source_pts_evidence_state=str(payload["source_pts_evidence_state"]),
            source_native_exact_edit_eligible=bool(payload["source_native_exact_edit_eligible"]),
            authoritative_edit_plan_created=bool(payload["authoritative_edit_plan_created"]),
            preview_policy_authorized=bool(payload["preview_policy_authorized"]),
            render_executed=bool(payload["render_executed"]),
            technical_qc_observed=str(payload["technical_qc_observed"]),
            visual_editorial_qc_observed=str(payload["visual_editorial_qc_observed"]),
            audio_editorial_qc_observed=str(payload["audio_editorial_qc_observed"]),
            production_export_authorized=False,
            export_status=str(payload["export_status"]),
            stripped_untrusted_authority_keys=tuple(
                str(k) for k in payload.get("stripped_untrusted_authority_keys", ())
            ),
            packet_digest=validate_hex_digest(str(payload["packet_digest"]), field_name="packet_digest"),
        )
        verify_export_readiness_packet(packet)
        return packet


def build_export_readiness_packet(
    *,
    packet_id: str,
    preparation_packet: Gate3PreparationPacket,
    lineage_certificate: Gate3LineageCertificate,
    render_preflight: RenderPreflightReport,
    qc_manifest: QCRequirementManifest,
    release_blocker_summary: ReleaseBlockerSummary,
    untrusted_input: Mapping[str, Any] | None = None,
) -> ExportReadinessPacket:
    verify_gate3_preparation_packet(preparation_packet)
    verify_gate3_lineage_certificate(lineage_certificate)
    verify_render_preflight_report(render_preflight)
    verify_qc_requirement_manifest(qc_manifest)

    if render_preflight.preparation_packet_digest != preparation_packet.packet_digest:
        raise VipLabError("render_preflight preparation_packet_digest mismatch.")
    if qc_manifest.preparation_packet_digest != preparation_packet.packet_digest:
        raise VipLabError("qc_manifest preparation_packet_digest mismatch.")

    stripped_keys: tuple[str, ...] = ()
    if untrusted_input is not None:
        _, stripped_keys = sanitize_untrusted_authority_claims(untrusted_input)

    not_observed_fields = tuple(
        dict.fromkeys(
            (
                *FIXTURE_NOT_OBSERVED_REQUIRED,
                "real_human_decision_state",
                "source_pts_evidence_state",
                "technical_qc_observed",
                "visual_editorial_qc_observed",
                "audio_editorial_qc_observed",
                *release_blocker_summary.not_observed_fields,
            )
        )
    )

    temp = ExportReadinessPacket(
        packet_id=packet_id,
        schema_version="1.0.0",
        lab_program_version=MEGA15_16_PROGRAM_VERSION,
        synthetic_context=SyntheticContextMarker.default("mega16.export_readiness"),
        preparation_packet_id=preparation_packet.packet_id,
        preparation_packet_digest=preparation_packet.packet_digest,
        lineage_certificate_id=lineage_certificate.certificate_id,
        lineage_certificate_digest=lineage_certificate.certificate_digest,
        render_preflight_id=render_preflight.preflight_id,
        render_preflight_digest=render_preflight.report_digest,
        qc_manifest_id=qc_manifest.manifest_id,
        qc_manifest_digest=qc_manifest.manifest_digest,
        release_blocker_summary_id=release_blocker_summary.summary_id,
        release_blocker_summary_digest=release_blocker_summary.summary_digest,
        blocker_codes=tuple(release_blocker_summary.blocker_codes),
        not_observed_fields=not_observed_fields,
        real_human_decision_state=NOT_OBSERVED,
        source_pts_evidence_state=NOT_OBSERVED,
        source_native_exact_edit_eligible=False,
        authoritative_edit_plan_created=False,
        preview_policy_authorized=False,
        render_executed=False,
        technical_qc_observed=NOT_OBSERVED,
        visual_editorial_qc_observed=NOT_OBSERVED,
        audio_editorial_qc_observed=NOT_OBSERVED,
        production_export_authorized=False,
        export_status="REFUSED_NOT_AUTHORIZED",
        stripped_untrusted_authority_keys=stripped_keys,
        packet_digest="0" * 64,
    )
    digest = canonical_sha256(temp._body_without_digest())
    packet = ExportReadinessPacket(**{**temp.__dict__, "packet_digest": digest})
    verify_export_readiness_packet(packet)
    return packet


def verify_export_readiness_packet(packet: ExportReadinessPacket) -> None:
    if not isinstance(packet, ExportReadinessPacket):
        raise VipLabError("Expected ExportReadinessPacket instance.")
    packet.synthetic_context.validate()
    if packet.lab_program_version != MEGA15_16_PROGRAM_VERSION:
        raise VipLabError(
            f"Unexpected lab_program_version: {packet.lab_program_version!r} != {MEGA15_16_PROGRAM_VERSION!r}"
        )
    validate_hex_digest(packet.preparation_packet_digest, field_name="preparation_packet_digest")
    validate_hex_digest(packet.lineage_certificate_digest, field_name="lineage_certificate_digest")
    validate_hex_digest(packet.render_preflight_digest, field_name="render_preflight_digest")
    validate_hex_digest(packet.qc_manifest_digest, field_name="qc_manifest_digest")
    validate_hex_digest(packet.release_blocker_summary_digest, field_name="release_blocker_summary_digest")
    validate_hex_digest(packet.packet_digest, field_name="packet_digest")

    if set(packet.blocker_codes) != set(CANONICAL_RELEASE_BLOCKER_CODES):
        raise VipLabError("ExportReadinessPacket.blocker_codes must include all CANONICAL_RELEASE_BLOCKER_CODES.")
    if packet.real_human_decision_state != NOT_OBSERVED:
        raise VipLabError("real_human_decision_state must be NOT_OBSERVED.")
    if packet.source_pts_evidence_state != NOT_OBSERVED:
        raise VipLabError("source_pts_evidence_state must be NOT_OBSERVED.")
    if packet.source_native_exact_edit_eligible is not False:
        raise VipLabError("source_native_exact_edit_eligible must be False.")
    if packet.authoritative_edit_plan_created is not False:
        raise VipLabError("authoritative_edit_plan_created must be False.")
    if packet.preview_policy_authorized is not False:
        raise VipLabError("preview_policy_authorized must be False.")
    if packet.render_executed is not False:
        raise VipLabError("render_executed must be False.")
    if packet.technical_qc_observed != NOT_OBSERVED:
        raise VipLabError("technical_qc_observed must be NOT_OBSERVED.")
    if packet.visual_editorial_qc_observed != NOT_OBSERVED:
        raise VipLabError("visual_editorial_qc_observed must be NOT_OBSERVED.")
    if packet.audio_editorial_qc_observed != NOT_OBSERVED:
        raise VipLabError("audio_editorial_qc_observed must be NOT_OBSERVED.")
    if packet.production_export_authorized is not False:
        raise VipLabError(f"{REFUSAL_PRODUCTION_EXPORT_NOT_AUTHORIZED}: production_export_authorized must be False.")
    if packet.export_status != "REFUSED_NOT_AUTHORIZED":
        raise VipLabError(f"{REFUSAL_PRODUCTION_EXPORT_NOT_AUTHORIZED}: export_status must be 'REFUSED_NOT_AUTHORIZED'.")

    expected_digest = canonical_sha256(packet._body_without_digest())
    if packet.packet_digest != expected_digest:
        raise VipLabError(
            f"ExportReadinessPacket digest mismatch: expected {expected_digest}, got {packet.packet_digest}"
        )


@dataclass(frozen=True)
class Mega1516OfflineBundle:
    bundle_id: str
    schema_version: str
    lab_program_version: str
    scenario_mode: str
    synthetic_context: SyntheticContextMarker
    queue_id: str
    queue_digest: str
    preparation_packet: Gate3PreparationPacket
    lineage_certificate: Gate3LineageCertificate
    render_preflight_report: RenderPreflightReport
    qc_requirement_manifest: QCRequirementManifest
    export_readiness_packet: ExportReadinessPacket
    bundle_digest: str

    def _body_without_digest(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "schema_version": self.schema_version,
            "lab_program_version": self.lab_program_version,
            "scenario_mode": self.scenario_mode,
            "synthetic_context": self.synthetic_context.to_dict(),
            "queue_id": self.queue_id,
            "queue_digest": self.queue_digest,
            "preparation_packet": self.preparation_packet.to_dict(),
            "lineage_certificate": self.lineage_certificate.to_dict(),
            "render_preflight_report": self.render_preflight_report.to_dict(),
            "qc_requirement_manifest": self.qc_requirement_manifest.to_dict(),
            "export_readiness_packet": self.export_readiness_packet.to_dict(),
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._body_without_digest()
        body["bundle_digest"] = self.bundle_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> Mega1516OfflineBundle:
        if not isinstance(payload, Mapping):
            raise VipLabError("Mega1516OfflineBundle payload must be a mapping.")
        bundle = cls(
            bundle_id=str(payload["bundle_id"]),
            schema_version=str(payload["schema_version"]),
            lab_program_version=str(payload["lab_program_version"]),
            scenario_mode=str(payload["scenario_mode"]),
            synthetic_context=SyntheticContextMarker.from_dict(payload["synthetic_context"]),
            queue_id=str(payload["queue_id"]),
            queue_digest=validate_hex_digest(str(payload["queue_digest"]), field_name="queue_digest"),
            preparation_packet=Gate3PreparationPacket.from_dict(payload["preparation_packet"]),
            lineage_certificate=Gate3LineageCertificate.from_dict(payload["lineage_certificate"]),
            render_preflight_report=RenderPreflightReport.from_dict(payload["render_preflight_report"]),
            qc_requirement_manifest=QCRequirementManifest.from_dict(payload["qc_requirement_manifest"]),
            export_readiness_packet=ExportReadinessPacket.from_dict(payload["export_readiness_packet"]),
            bundle_digest=validate_hex_digest(str(payload["bundle_digest"]), field_name="bundle_digest"),
        )
        verify_mega15_16_offline_bundle(bundle)
        return bundle


def run_mega15_16_offline_pipeline(*, scenario_mode: str = "three_arm") -> Mega1516OfflineBundle:
    if scenario_mode == "three_arm":
        scenario = default_three_arm_scenario()
    elif scenario_mode == "single_arm":
        scenario = default_single_arm_scenario()
    else:
        raise VipLabError(f"Unsupported scenario_mode: {scenario_mode!r}")

    # Run upstream MEGA-08..14 synthetic lab to obtain the verified CandidateReviewQueue
    e2e_report = run_end_to_end_synthetic_lab(scenario)
    queue = CandidateReviewQueue.from_dict(e2e_report.candidate_queue)
    verify_candidate_queue(queue)

    requests: list[TemporalRefinementRequest] = []
    diagnostics: list[PtsFixtureDiagnostic] = []
    proposal_chains: dict[str, list[EditorialProposal]] = {}

    for idx, item in enumerate(queue.items, start=1):
        req = build_temporal_refinement_request(
            request_id=f"m15_req_{scenario_mode}_{idx:03d}",
            queue_item=item,
            producer_attempt_id=f"m15_attempt_{scenario_mode}_{idx:03d}",
        )
        diag = evaluate_pts_fixture_diagnostic(
            diagnostic_id=f"m15_diag_{scenario_mode}_{idx:03d}",
            request=req,
            pts_ticks=scenario.pts_ticks,
        )
        v1 = build_editorial_proposal(
            proposal_id=f"m15_prop_{scenario_mode}_{idx:03d}_v1",
            queue_item=item,
            refinement_request=req,
            pts_diagnostic=diag,
            proposed_action="INCLUDE_CANDIDATE_FOR_HUMAN_REVIEW",
            rationale="v1 synthetic candidate intake for human editorial review.",
        )
        v2 = advance_proposal_revision(
            prior_proposal=v1,
            new_proposal_id=f"m15_prop_{scenario_mode}_{idx:03d}_v2",
            proposed_action="REVISE_CANDIDATE_BOUNDARIES",
            proposed_start_ticks=diag.snapped_start_ticks,
            proposed_end_ticks=diag.snapped_end_ticks,
            rationale="v2 synthetic PTS-snapped boundary refinement proposal.",
        )
        v3 = advance_proposal_revision(
            prior_proposal=v2,
            new_proposal_id=f"m15_prop_{scenario_mode}_{idx:03d}_v3",
            proposed_action="HOLD_FOR_ADDITIONAL_EVIDENCE",
            proposed_start_ticks=diag.snapped_start_ticks,
            proposed_end_ticks=diag.snapped_end_ticks,
            rationale="v3 synthetic pre-review hold awaiting measured source PTS and human editorial decision.",
        )
        requests.append(req)
        diagnostics.append(diag)
        proposal_chains[item.queue_item_id] = [v1, v2, v3]

    temporal_records = [
        build_temporal_preparation_record(refinement_request=r, pts_diagnostic=d)
        for r, d in zip(requests, diagnostics, strict=True)
    ]

    prep_packet = build_gate3_preparation_packet(
        packet_id=f"m15_prep_{scenario_mode}",
        queue=queue,
        temporal_records=temporal_records,
        proposal_chains=proposal_chains,
    )

    lineage_cert = verify_cross_stage_gate3_lineage(
        certificate_id=f"m15_lineage_{scenario_mode}",
        queue=queue,
        refinement_requests=requests,
        pts_diagnostics=diagnostics,
        proposal_chains=proposal_chains,
        preparation_packet=prep_packet,
    )

    m13_receipt = audit_cross_stage_lineage(
        audit_id=f"m13_audit_{scenario_mode}",
        queue=queue,
        refinement_requests=requests,
        pts_diagnostics=diagnostics,
        proposal_chains=proposal_chains,
    )
    m13_qc = evaluate_qc_readiness(
        checklist_id=f"m13_qc_{scenario_mode}",
        lineage_receipt=m13_receipt,
    )
    m13_blockers = build_release_blocker_summary(
        summary_id=f"m13_blockers_{scenario_mode}",
        lineage_receipt=m13_receipt,
        qc_checklist=m13_qc,
    )

    render_report = build_render_preflight_report(
        preflight_id=f"m16_render_{scenario_mode}",
        preparation_packet=prep_packet,
        lineage_certificate=lineage_cert,
    )
    qc_manifest = build_qc_requirement_manifest(
        manifest_id=f"m16_qc_{scenario_mode}",
        preparation_packet=prep_packet,
    )
    readiness_packet = build_export_readiness_packet(
        packet_id=f"m16_readiness_{scenario_mode}",
        preparation_packet=prep_packet,
        lineage_certificate=lineage_cert,
        render_preflight=render_report,
        qc_manifest=qc_manifest,
        release_blocker_summary=m13_blockers,
    )

    temp_bundle = Mega1516OfflineBundle(
        bundle_id=f"mega15_16_bundle_{scenario_mode}",
        schema_version="1.0.0",
        lab_program_version=MEGA15_16_PROGRAM_VERSION,
        scenario_mode=scenario_mode,
        synthetic_context=SyntheticContextMarker.default("mega16.offline_bundle"),
        queue_id=queue.queue_id,
        queue_digest=queue.queue_digest,
        preparation_packet=prep_packet,
        lineage_certificate=lineage_cert,
        render_preflight_report=render_report,
        qc_requirement_manifest=qc_manifest,
        export_readiness_packet=readiness_packet,
        bundle_digest="0" * 64,
    )
    digest = canonical_sha256(temp_bundle._body_without_digest())
    bundle = Mega1516OfflineBundle(**{**temp_bundle.__dict__, "bundle_digest": digest})
    verify_mega15_16_offline_bundle(bundle)
    return bundle


def verify_mega15_16_offline_bundle(bundle: Mega1516OfflineBundle) -> None:
    if not isinstance(bundle, Mega1516OfflineBundle):
        raise VipLabError("Expected Mega1516OfflineBundle instance.")
    bundle.synthetic_context.validate()
    if bundle.lab_program_version != MEGA15_16_PROGRAM_VERSION:
        raise VipLabError(f"Unexpected lab_program_version: {bundle.lab_program_version!r}")
    if bundle.scenario_mode not in ("three_arm", "single_arm"):
        raise VipLabError(f"Unsupported scenario_mode: {bundle.scenario_mode!r}")

    verify_gate3_preparation_packet(bundle.preparation_packet)
    verify_gate3_lineage_certificate(bundle.lineage_certificate)
    verify_render_preflight_report(bundle.render_preflight_report)
    verify_qc_requirement_manifest(bundle.qc_requirement_manifest)
    verify_export_readiness_packet(bundle.export_readiness_packet)

    if bundle.preparation_packet.queue_id != bundle.queue_id:
        raise VipLabError("Bundle queue_id mismatch with preparation_packet.")
    if bundle.preparation_packet.queue_digest != bundle.queue_digest:
        raise VipLabError("Bundle queue_digest mismatch with preparation_packet.")
    if bundle.lineage_certificate.preparation_packet_digest != bundle.preparation_packet.packet_digest:
        raise VipLabError("Cross-stage digest mismatch: lineage_certificate -> preparation_packet.")
    if bundle.render_preflight_report.preparation_packet_digest != bundle.preparation_packet.packet_digest:
        raise VipLabError("Cross-stage digest mismatch: render_preflight_report -> preparation_packet.")
    if bundle.render_preflight_report.lineage_certificate_digest != bundle.lineage_certificate.certificate_digest:
        raise VipLabError("Cross-stage digest mismatch: render_preflight_report -> lineage_certificate.")
    if bundle.qc_requirement_manifest.preparation_packet_digest != bundle.preparation_packet.packet_digest:
        raise VipLabError("Cross-stage digest mismatch: qc_requirement_manifest -> preparation_packet.")
    if bundle.export_readiness_packet.preparation_packet_digest != bundle.preparation_packet.packet_digest:
        raise VipLabError("Cross-stage digest mismatch: export_readiness_packet -> preparation_packet.")
    if bundle.export_readiness_packet.lineage_certificate_digest != bundle.lineage_certificate.certificate_digest:
        raise VipLabError("Cross-stage digest mismatch: export_readiness_packet -> lineage_certificate.")
    if bundle.export_readiness_packet.render_preflight_digest != bundle.render_preflight_report.report_digest:
        raise VipLabError("Cross-stage digest mismatch: export_readiness_packet -> render_preflight_report.")
    if bundle.export_readiness_packet.qc_manifest_digest != bundle.qc_requirement_manifest.manifest_digest:
        raise VipLabError("Cross-stage digest mismatch: export_readiness_packet -> qc_requirement_manifest.")

    expected_digest = canonical_sha256(bundle._body_without_digest())
    if bundle.bundle_digest != expected_digest:
        raise VipLabError(
            f"Mega1516OfflineBundle digest mismatch: expected {expected_digest}, got {bundle.bundle_digest}"
        )
