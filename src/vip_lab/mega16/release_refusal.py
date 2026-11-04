"""MEGA-16.3 — Production Export Refusal Certificate & Offline Pipeline Runner.

Assembles the terminal `ReleaseRefusalCertificate` and `Mega1516OfflineReport` binding
MEGA-15 (`Gate3OfflinePreparationPacket`, `Mega15LineageReceipt`) and MEGA-16
(`RenderPreflightSpecification`, `QcRequirementsBundle`) to MEGA-13's 6 canonical
release blockers (`CANONICAL_RELEASE_BLOCKER_CODES`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vip_lab.common import (
    FORBIDDEN_EXTERNAL_AUTHORITY_KEYS,
    SyntheticContextMarker,
    canonical_sha256,
    sanitize_untrusted_authority_claims,
)
from vip_lab.mega09 import CandidateQueueItem, CandidateReviewQueue, verify_candidate_queue
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
    audit_cross_stage_lineage,
    build_release_blocker_summary,
    evaluate_qc_readiness,
)
from vip_lab.mega14 import run_end_to_end_synthetic_lab
from vip_lab.mega15.editorial_handoff import (
    EditorialHandoffEnvelope,
    Gate3OfflinePreparationPacket,
    build_editorial_handoff_envelope,
    build_gate3_offline_preparation_packet,
    verify_gate3_offline_preparation_packet,
)
from vip_lab.mega15.lineage import (
    Mega15LineageReceipt,
    REFUSAL_MEGA15_LINEAGE_BROKEN,
    audit_mega15_lineage,
    verify_mega15_lineage_receipt,
)
from vip_lab.mega15.temporal_preflight import (
    TemporalPreparationRecord,
    build_temporal_preparation_record,
    ensure_non_empty_str,
    make_synthetic_context,
    parse_synthetic_context_dict,
    raise_mega15_error,
    serialize_synthetic_context,
    validate_synthetic_context,
)
from vip_lab.mega16.qc_requirements import (
    QcRequirementsBundle,
    build_qc_requirements_bundle,
    verify_qc_requirements_bundle,
)
from vip_lab.mega16.render_preflight import (
    RenderPreflightSpecification,
    build_render_preflight_specification,
    verify_render_preflight_specification,
)

RELEASE_REFUSAL_SCHEMA_VERSION = "1.0.0"
RELEASE_REFUSAL_KIND = "vip_lab.mega16.release_refusal_certificate"
OFFLINE_REPORT_KIND = "vip_lab.mega15_16.offline_gate3_report"

REFUSAL_PRODUCTION_EXPORT_FORBIDDEN = "REFUSAL_PRODUCTION_EXPORT_UNAUTHORIZED"
REFUSAL_GATE_PROMOTION_FORBIDDEN = "REFUSAL_GATE_PROMOTION_UNAUTHORIZED"
REFUSAL_OWNER_AUTHORITY_FORGERY = "REFUSAL_OWNER_AUTHORITY_FORGERY_FORBIDDEN"
REFUSAL_BLOCKER_SET_INCOMPLETE = "REFUSAL_CANONICAL_RELEASE_BLOCKERS_INCOMPLETE"
REFUSAL_STAGE_ARTIFACT_MISMATCH = "REFUSAL_STAGE_ARTIFACT_DIGEST_MISMATCH"

_ADDITIONAL_AUTHORITY_KEYS: frozenset[str] = frozenset(
    {
        "human_approved",
        "owner_approved",
        "production_export_authorized",
        "gate_promoted",
        "real_human_approved",
        "authoritative_source_measurement",
        "preview_eligible",
        "export_authorized",
    }
)


def _strip_all_untrusted_authority_keys(
    payload: Mapping[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Strip both common FORBIDDEN_EXTERNAL_AUTHORITY_KEYS and MEGA-16 authority keys."""
    cleaned_common, stripped_common = sanitize_untrusted_authority_claims(payload)
    stripped_set = set(stripped_common)

    def _clean_recursive(obj: Any) -> Any:
        if isinstance(obj, Mapping):
            out: dict[str, Any] = {}
            for k, v in obj.items():
                key_str = str(k)
                if (
                    key_str in FORBIDDEN_EXTERNAL_AUTHORITY_KEYS
                    or key_str in _ADDITIONAL_AUTHORITY_KEYS
                ):
                    stripped_set.add(key_str)
                    continue
                out[key_str] = _clean_recursive(v)
            return out
        if isinstance(obj, list):
            return [_clean_recursive(item) for item in obj]
        return obj

    final_clean = _clean_recursive(cleaned_common)
    return final_clean, sorted(stripped_set)


def refuse_production_export_or_gate_promotion(
    *,
    request_production_export: bool = False,
    request_gate_promotion: bool = False,
    claim_owner_approval: bool = False,
) -> None:
    """Fail closed if a caller requests production export, Gate promotion, or forged owner approval."""
    if claim_owner_approval:
        raise_mega15_error(
            REFUSAL_OWNER_AUTHORITY_FORGERY,
            "Forged or self-declared owner approval is strictly forbidden.",
        )
    if request_production_export:
        raise_mega15_error(
            REFUSAL_PRODUCTION_EXPORT_FORBIDDEN,
            "Production export is refused; all 6 canonical release blockers remain active.",
        )
    if request_gate_promotion:
        raise_mega15_error(
            REFUSAL_GATE_PROMOTION_FORBIDDEN,
            "Gate-0..Gate-3 promotion or acceptance claims are forbidden in synthetic offline preparation.",
        )


@dataclass(frozen=True)
class ReleaseRefusalCertificate:
    """Terminal MEGA-16 certificate proving production export and Gate promotion remain refused."""

    schema_version: str
    kind: str
    certificate_id: str
    preparation_packet_id: str
    preparation_packet_digest: str
    mega15_lineage_receipt_id: str
    mega15_lineage_receipt_digest: str
    render_specification_id: str
    render_specification_digest: str
    qc_requirements_bundle_id: str
    qc_requirements_bundle_digest: str
    upstream_blocker_summary_id: str
    upstream_blocker_summary_digest: str
    active_release_blocker_codes: tuple[str, ...]
    stripped_untrusted_authority_keys: tuple[str, ...]
    real_source_media_state: str
    authentic_model_inference_state: str
    source_pts_measurement_state: str
    real_human_editorial_decision_state: str
    technical_qc_state: str
    visual_editorial_qc_state: str
    audio_editorial_qc_state: str
    preview_eligible: bool
    production_export_authorized: bool
    gate_promotion_authorized: bool
    export_status: str
    synthetic_context: SyntheticContextMarker
    certificate_digest: str

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "certificate_id": self.certificate_id,
            "preparation_packet_id": self.preparation_packet_id,
            "preparation_packet_digest": self.preparation_packet_digest,
            "mega15_lineage_receipt_id": self.mega15_lineage_receipt_id,
            "mega15_lineage_receipt_digest": self.mega15_lineage_receipt_digest,
            "render_specification_id": self.render_specification_id,
            "render_specification_digest": self.render_specification_digest,
            "qc_requirements_bundle_id": self.qc_requirements_bundle_id,
            "qc_requirements_bundle_digest": self.qc_requirements_bundle_digest,
            "upstream_blocker_summary_id": self.upstream_blocker_summary_id,
            "upstream_blocker_summary_digest": self.upstream_blocker_summary_digest,
            "active_release_blocker_codes": list(self.active_release_blocker_codes),
            "stripped_untrusted_authority_keys": list(
                self.stripped_untrusted_authority_keys
            ),
            "real_source_media_state": self.real_source_media_state,
            "authentic_model_inference_state": self.authentic_model_inference_state,
            "source_pts_measurement_state": self.source_pts_measurement_state,
            "real_human_editorial_decision_state": self.real_human_editorial_decision_state,
            "technical_qc_state": self.technical_qc_state,
            "visual_editorial_qc_state": self.visual_editorial_qc_state,
            "audio_editorial_qc_state": self.audio_editorial_qc_state,
            "preview_eligible": self.preview_eligible,
            "production_export_authorized": self.production_export_authorized,
            "gate_promotion_authorized": self.gate_promotion_authorized,
            "export_status": self.export_status,
            "synthetic_context": serialize_synthetic_context(self.synthetic_context),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._digest_payload()
        payload["certificate_digest"] = self.certificate_digest
        return payload

    def validate(self) -> None:
        if self.schema_version != RELEASE_REFUSAL_SCHEMA_VERSION:
            raise_mega15_error(
                "RELEASE_REFUSAL_SCHEMA_MISMATCH",
                f"Unsupported schema_version: {self.schema_version!r}",
            )
        if self.kind != RELEASE_REFUSAL_KIND:
            raise_mega15_error(
                "RELEASE_REFUSAL_KIND_MISMATCH",
                f"Unsupported kind: {self.kind!r}",
            )
        ensure_non_empty_str(self.certificate_id, "certificate_id")
        ensure_non_empty_str(self.preparation_packet_id, "preparation_packet_id")
        ensure_non_empty_str(
            self.preparation_packet_digest, "preparation_packet_digest"
        )
        ensure_non_empty_str(
            self.mega15_lineage_receipt_id, "mega15_lineage_receipt_id"
        )
        ensure_non_empty_str(
            self.mega15_lineage_receipt_digest, "mega15_lineage_receipt_digest"
        )
        ensure_non_empty_str(
            self.render_specification_id, "render_specification_id"
        )
        ensure_non_empty_str(
            self.render_specification_digest, "render_specification_digest"
        )
        ensure_non_empty_str(
            self.qc_requirements_bundle_id, "qc_requirements_bundle_id"
        )
        ensure_non_empty_str(
            self.qc_requirements_bundle_digest, "qc_requirements_bundle_digest"
        )
        ensure_non_empty_str(
            self.upstream_blocker_summary_id, "upstream_blocker_summary_id"
        )
        ensure_non_empty_str(
            self.upstream_blocker_summary_digest,
            "upstream_blocker_summary_digest",
        )
        validate_synthetic_context(self.synthetic_context)

        for field_name, val in (
            ("real_source_media_state", self.real_source_media_state),
            ("authentic_model_inference_state", self.authentic_model_inference_state),
            ("source_pts_measurement_state", self.source_pts_measurement_state),
            (
                "real_human_editorial_decision_state",
                self.real_human_editorial_decision_state,
            ),
            ("technical_qc_state", self.technical_qc_state),
            ("visual_editorial_qc_state", self.visual_editorial_qc_state),
            ("audio_editorial_qc_state", self.audio_editorial_qc_state),
        ):
            if val != "NOT_OBSERVED":
                raise_mega15_error(
                    REFUSAL_PRODUCTION_EXPORT_FORBIDDEN,
                    f"{field_name} must remain 'NOT_OBSERVED', got {val!r}",
                )

        if self.preview_eligible is not False:
            raise_mega15_error(
                REFUSAL_PRODUCTION_EXPORT_FORBIDDEN,
                "preview_eligible must remain False",
            )
        if self.production_export_authorized is not False:
            raise_mega15_error(
                REFUSAL_PRODUCTION_EXPORT_FORBIDDEN,
                "production_export_authorized must remain False",
            )
        if self.gate_promotion_authorized is not False:
            raise_mega15_error(
                REFUSAL_GATE_PROMOTION_FORBIDDEN,
                "gate_promotion_authorized must remain False",
            )
        if self.export_status != "REFUSED_NOT_AUTHORIZED":
            raise_mega15_error(
                REFUSAL_PRODUCTION_EXPORT_FORBIDDEN,
                f"export_status must be 'REFUSED_NOT_AUTHORIZED', got {self.export_status!r}",
            )

        required_blockers = set(CANONICAL_RELEASE_BLOCKER_CODES)
        actual_blockers = set(self.active_release_blocker_codes)
        if not required_blockers.issubset(actual_blockers):
            missing = sorted(required_blockers - actual_blockers)
            raise_mega15_error(
                REFUSAL_BLOCKER_SET_INCOMPLETE,
                f"Missing canonical release blocker codes: {missing}",
            )

        expected_digest = canonical_sha256(self._digest_payload())
        if self.certificate_digest != expected_digest:
            raise_mega15_error(
                "RELEASE_REFUSAL_DIGEST_MISMATCH",
                f"certificate_digest mismatch: expected {expected_digest}, got {self.certificate_digest}",
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ReleaseRefusalCertificate":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                "RELEASE_REFUSAL_INVALID_PAYLOAD",
                "Payload must be a mapping",
            )
        raw_ctx = payload.get("synthetic_context")
        if not isinstance(raw_ctx, Mapping):
            raise_mega15_error(
                "RELEASE_REFUSAL_INVALID_SYNTHETIC_CONTEXT",
                "synthetic_context must be a mapping",
            )
        raw_b = payload.get("active_release_blocker_codes")
        raw_s = payload.get("stripped_untrusted_authority_keys", ())
        if not isinstance(raw_b, Sequence) or not isinstance(raw_s, Sequence):
            raise_mega15_error(
                "RELEASE_REFUSAL_INVALID_LISTS",
                "Blocker and stripped key fields must be sequences",
            )
        cert = cls(
            schema_version=str(payload.get("schema_version", "")),
            kind=str(payload.get("kind", "")),
            certificate_id=str(payload.get("certificate_id", "")),
            preparation_packet_id=str(payload.get("preparation_packet_id", "")),
            preparation_packet_digest=str(
                payload.get("preparation_packet_digest", "")
            ),
            mega15_lineage_receipt_id=str(
                payload.get("mega15_lineage_receipt_id", "")
            ),
            mega15_lineage_receipt_digest=str(
                payload.get("mega15_lineage_receipt_digest", "")
            ),
            render_specification_id=str(payload.get("render_specification_id", "")),
            render_specification_digest=str(
                payload.get("render_specification_digest", "")
            ),
            qc_requirements_bundle_id=str(
                payload.get("qc_requirements_bundle_id", "")
            ),
            qc_requirements_bundle_digest=str(
                payload.get("qc_requirements_bundle_digest", "")
            ),
            upstream_blocker_summary_id=str(
                payload.get("upstream_blocker_summary_id", "")
            ),
            upstream_blocker_summary_digest=str(
                payload.get("upstream_blocker_summary_digest", "")
            ),
            active_release_blocker_codes=tuple(str(x) for x in raw_b),
            stripped_untrusted_authority_keys=tuple(str(x) for x in raw_s),
            real_source_media_state=str(
                payload.get("real_source_media_state", "")
            ),
            authentic_model_inference_state=str(
                payload.get("authentic_model_inference_state", "")
            ),
            source_pts_measurement_state=str(
                payload.get("source_pts_measurement_state", "")
            ),
            real_human_editorial_decision_state=str(
                payload.get("real_human_editorial_decision_state", "")
            ),
            technical_qc_state=str(payload.get("technical_qc_state", "")),
            visual_editorial_qc_state=str(
                payload.get("visual_editorial_qc_state", "")
            ),
            audio_editorial_qc_state=str(
                payload.get("audio_editorial_qc_state", "")
            ),
            preview_eligible=bool(payload.get("preview_eligible", True)),
            production_export_authorized=bool(
                payload.get("production_export_authorized", True)
            ),
            gate_promotion_authorized=bool(
                payload.get("gate_promotion_authorized", True)
            ),
            export_status=str(payload.get("export_status", "")),
            synthetic_context=parse_synthetic_context_dict(raw_ctx),
            certificate_digest=str(payload.get("certificate_digest", "")),
        )
        cert.validate()
        return cert


def build_release_refusal_certificate(
    *,
    preparation_packet: Gate3OfflinePreparationPacket,
    mega15_lineage_receipt: Mega15LineageReceipt,
    render_specification: RenderPreflightSpecification,
    qc_bundle: QcRequirementsBundle,
    upstream_blocker_summary: Mapping[str, Any],
    untrusted_authority_payload: Mapping[str, Any] | None = None,
    certificate_id: str = "relrefusal_default",
    request_production_export: bool = False,
    request_gate_promotion: bool = False,
    claim_owner_approval: bool = False,
) -> ReleaseRefusalCertificate:
    """Build and verify a `ReleaseRefusalCertificate` binding MEGA-15 and MEGA-16 artifacts."""
    refuse_production_export_or_gate_promotion(
        request_production_export=request_production_export,
        request_gate_promotion=request_gate_promotion,
        claim_owner_approval=claim_owner_approval,
    )
    verify_gate3_offline_preparation_packet(preparation_packet)
    verify_mega15_lineage_receipt(mega15_lineage_receipt)
    verify_render_preflight_specification(render_specification)
    verify_qc_requirements_bundle(qc_bundle)

    if not isinstance(upstream_blocker_summary, Mapping):
        raise_mega15_error(
            REFUSAL_BLOCKER_SET_INCOMPLETE,
            "upstream_blocker_summary must be a mapping returned by build_release_blocker_summary",
        )

    upstream_blockers = upstream_blocker_summary.get("release_blockers", ())
    upstream_prod_auth = upstream_blocker_summary.get("production_export_authorized")
    upstream_preview = upstream_blocker_summary.get("preview_eligible")
    upstream_export_status = upstream_blocker_summary.get("export_status")
    upstream_summary_digest = str(upstream_blocker_summary.get("summary_digest", ""))

    if (
        upstream_prod_auth is not False
        or upstream_preview is not False
        or upstream_export_status != "REFUSED_NOT_AUTHORIZED"
        or not upstream_summary_digest
        or not set(CANONICAL_RELEASE_BLOCKER_CODES).issubset(set(upstream_blockers))
    ):
        raise_mega15_error(
            REFUSAL_BLOCKER_SET_INCOMPLETE,
            "upstream_blocker_summary failed release refusal verification",
        )

    upstream_summary_id = str(
        upstream_blocker_summary.get(
            "summary_id", f"rblock_{upstream_summary_digest[:12]}"
        )
    )

    # Cross-verify digest chain across MEGA-15 and MEGA-16
    if (
        mega15_lineage_receipt.preparation_packet_digest
        != preparation_packet.packet_digest
        or render_specification.preparation_packet_digest
        != preparation_packet.packet_digest
        or render_specification.mega15_lineage_receipt_digest
        != mega15_lineage_receipt.receipt_digest
        or qc_bundle.render_specification_digest
        != render_specification.specification_digest
    ):
        raise_mega15_error(
            REFUSAL_STAGE_ARTIFACT_MISMATCH,
            "Digest chain mismatch across MEGA-15 preparation, lineage, render preflight, or QC bundle",
        )

    stripped_keys: tuple[str, ...] = ()
    if untrusted_authority_payload is not None:
        _cleaned, stripped_list = _strip_all_untrusted_authority_keys(
            untrusted_authority_payload
        )
        stripped_keys = tuple(sorted(stripped_list))

    combined_blockers = tuple(
        dict.fromkeys(
            list(CANONICAL_RELEASE_BLOCKER_CODES)
            + list(upstream_blockers)
            + list(qc_bundle.required_qc_blocker_codes)
        )
    )

    syn_ctx = make_synthetic_context()
    provisional = ReleaseRefusalCertificate(
        schema_version=RELEASE_REFUSAL_SCHEMA_VERSION,
        kind=RELEASE_REFUSAL_KIND,
        certificate_id=certificate_id,
        preparation_packet_id=preparation_packet.packet_id,
        preparation_packet_digest=preparation_packet.packet_digest,
        mega15_lineage_receipt_id=mega15_lineage_receipt.receipt_id,
        mega15_lineage_receipt_digest=mega15_lineage_receipt.receipt_digest,
        render_specification_id=render_specification.specification_id,
        render_specification_digest=render_specification.specification_digest,
        qc_requirements_bundle_id=qc_bundle.bundle_id,
        qc_requirements_bundle_digest=qc_bundle.bundle_digest,
        upstream_blocker_summary_id=upstream_summary_id,
        upstream_blocker_summary_digest=upstream_summary_digest,
        active_release_blocker_codes=combined_blockers,
        stripped_untrusted_authority_keys=stripped_keys,
        real_source_media_state="NOT_OBSERVED",
        authentic_model_inference_state="NOT_OBSERVED",
        source_pts_measurement_state="NOT_OBSERVED",
        real_human_editorial_decision_state="NOT_OBSERVED",
        technical_qc_state="NOT_OBSERVED",
        visual_editorial_qc_state="NOT_OBSERVED",
        audio_editorial_qc_state="NOT_OBSERVED",
        preview_eligible=False,
        production_export_authorized=False,
        gate_promotion_authorized=False,
        export_status="REFUSED_NOT_AUTHORIZED",
        synthetic_context=syn_ctx,
        certificate_digest="",
    )
    digest = canonical_sha256(provisional._digest_payload())
    final_cert = ReleaseRefusalCertificate(
        **{**provisional.__dict__, "certificate_digest": digest}
    )
    final_cert.validate()
    return final_cert


def verify_release_refusal_certificate(
    certificate: ReleaseRefusalCertificate | Mapping[str, Any],
) -> ReleaseRefusalCertificate:
    """Verify and return a `ReleaseRefusalCertificate`."""
    if isinstance(certificate, ReleaseRefusalCertificate):
        certificate.validate()
        return certificate
    return ReleaseRefusalCertificate.from_dict(certificate)


@dataclass(frozen=True)
class Mega1516OfflineReport:
    """Complete deterministic offline Gate-3 preparation, QC, and release-refusal report."""

    schema_version: str
    kind: str
    report_id: str
    preparation_packet: Gate3OfflinePreparationPacket
    mega15_lineage_receipt: Mega15LineageReceipt
    render_specification: RenderPreflightSpecification
    qc_requirements_bundle: QcRequirementsBundle
    release_refusal_certificate: ReleaseRefusalCertificate
    synthetic_context: SyntheticContextMarker
    report_digest: str

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "report_id": self.report_id,
            "preparation_packet": self.preparation_packet.to_dict(),
            "mega15_lineage_receipt": self.mega15_lineage_receipt.to_dict(),
            "render_specification": self.render_specification.to_dict(),
            "qc_requirements_bundle": self.qc_requirements_bundle.to_dict(),
            "release_refusal_certificate": self.release_refusal_certificate.to_dict(),
            "synthetic_context": serialize_synthetic_context(self.synthetic_context),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._digest_payload()
        payload["report_digest"] = self.report_digest
        return payload

    def validate(self) -> None:
        if self.schema_version != RELEASE_REFUSAL_SCHEMA_VERSION:
            raise_mega15_error(
                "OFFLINE_REPORT_SCHEMA_MISMATCH",
                f"Unsupported schema_version: {self.schema_version!r}",
            )
        if self.kind != OFFLINE_REPORT_KIND:
            raise_mega15_error(
                "OFFLINE_REPORT_KIND_MISMATCH",
                f"Unsupported kind: {self.kind!r}",
            )
        ensure_non_empty_str(self.report_id, "report_id")
        validate_synthetic_context(self.synthetic_context)

        self.preparation_packet.validate()
        self.mega15_lineage_receipt.validate()
        self.render_specification.validate()
        self.qc_requirements_bundle.validate()
        self.release_refusal_certificate.validate()

        if (
            self.mega15_lineage_receipt.preparation_packet_digest
            != self.preparation_packet.packet_digest
            or self.render_specification.preparation_packet_digest
            != self.preparation_packet.packet_digest
            or self.render_specification.mega15_lineage_receipt_digest
            != self.mega15_lineage_receipt.receipt_digest
            or self.qc_requirements_bundle.render_specification_digest
            != self.render_specification.specification_digest
            or self.release_refusal_certificate.preparation_packet_digest
            != self.preparation_packet.packet_digest
            or self.release_refusal_certificate.mega15_lineage_receipt_digest
            != self.mega15_lineage_receipt.receipt_digest
            or self.release_refusal_certificate.render_specification_digest
            != self.render_specification.specification_digest
            or self.release_refusal_certificate.qc_requirements_bundle_digest
            != self.qc_requirements_bundle.bundle_digest
        ):
            raise_mega15_error(
                REFUSAL_STAGE_ARTIFACT_MISMATCH,
                "Offline report internal stage digest links do not match",
            )

        expected_digest = canonical_sha256(self._digest_payload())
        if self.report_digest != expected_digest:
            raise_mega15_error(
                "OFFLINE_REPORT_DIGEST_MISMATCH",
                f"report_digest mismatch: expected {expected_digest}, got {self.report_digest}",
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Mega1516OfflineReport":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                "OFFLINE_REPORT_INVALID_PAYLOAD",
                "Payload must be a mapping",
            )
        raw_ctx = payload.get("synthetic_context")
        if not isinstance(raw_ctx, Mapping):
            raise_mega15_error(
                "OFFLINE_REPORT_INVALID_SYNTHETIC_CONTEXT",
                "synthetic_context must be a mapping",
            )
        report = cls(
            schema_version=str(payload.get("schema_version", "")),
            kind=str(payload.get("kind", "")),
            report_id=str(payload.get("report_id", "")),
            preparation_packet=Gate3OfflinePreparationPacket.from_dict(
                payload.get("preparation_packet", {})
            ),
            mega15_lineage_receipt=Mega15LineageReceipt.from_dict(
                payload.get("mega15_lineage_receipt", {})
            ),
            render_specification=RenderPreflightSpecification.from_dict(
                payload.get("render_specification", {})
            ),
            qc_requirements_bundle=QcRequirementsBundle.from_dict(
                payload.get("qc_requirements_bundle", {})
            ),
            release_refusal_certificate=ReleaseRefusalCertificate.from_dict(
                payload.get("release_refusal_certificate", {})
            ),
            synthetic_context=parse_synthetic_context_dict(raw_ctx),
            report_digest=str(payload.get("report_digest", "")),
        )
        report.validate()
        return report


def build_mega15_16_offline_report(
    *,
    preparation_packet: Gate3OfflinePreparationPacket,
    mega15_lineage_receipt: Mega15LineageReceipt,
    render_specification: RenderPreflightSpecification,
    qc_bundle: QcRequirementsBundle,
    refusal_certificate: ReleaseRefusalCertificate,
    report_id: str = "mega15_16_offline_report_default",
) -> Mega1516OfflineReport:
    """Assemble and validate a complete `Mega1516OfflineReport`."""
    syn_ctx = make_synthetic_context()
    provisional = Mega1516OfflineReport(
        schema_version=RELEASE_REFUSAL_SCHEMA_VERSION,
        kind=OFFLINE_REPORT_KIND,
        report_id=report_id,
        preparation_packet=preparation_packet,
        mega15_lineage_receipt=mega15_lineage_receipt,
        render_specification=render_specification,
        qc_requirements_bundle=qc_bundle,
        release_refusal_certificate=refusal_certificate,
        synthetic_context=syn_ctx,
        report_digest="",
    )
    digest = canonical_sha256(provisional._digest_payload())
    final_report = Mega1516OfflineReport(
        **{**provisional.__dict__, "report_digest": digest}
    )
    final_report.validate()
    return final_report


def verify_mega15_16_offline_report(
    report: Mega1516OfflineReport | Mapping[str, Any],
) -> Mega1516OfflineReport:
    """Verify and return a `Mega1516OfflineReport`."""
    if isinstance(report, Mega1516OfflineReport):
        report.validate()
        return report
    return Mega1516OfflineReport.from_dict(report)


def run_mega15_16_offline_pipeline(
    *,
    seed: int = 20261102,
    untrusted_authority_payload: Mapping[str, Any] | None = None,
) -> Mega1516OfflineReport:
    """Execute the deterministic offline synthetic MEGA-08..14 -> MEGA-15 -> MEGA-16 pipeline."""
    from vip_lab.mega09 import build_queue_from_batch_report
    from vip_lab.mega14 import default_three_arm_scenario

    scen = default_three_arm_scenario()
    if int(seed) != 20261104:
        scen_dict = scen.to_dict()
        scen_dict["workload"]["seed"] = int(seed)
        e2e_report = run_end_to_end_synthetic_lab(scen_dict)
    else:
        e2e_report = run_end_to_end_synthetic_lab(scen)

    verify_candidate_queue(e2e_report.artifacts["candidate_queue"])
    queue = build_queue_from_batch_report(e2e_report.artifacts["batch_report"])

    temporal_requests: list[TemporalRefinementRequest] = []
    pts_diagnostics: list[PtsFixtureDiagnostic] = []
    temporal_records: list[TemporalPreparationRecord] = []
    proposal_chains: list[tuple[EditorialProposal, ...]] = []
    handoff_envelopes: list[EditorialHandoffEnvelope] = []

    pts_scenarios: list[tuple[tuple[int, ...], int, int]] = [
        ((0, 1001, 2002, 3003, 4004, 5005, 6006, 7007), 1001, 6006),
        ((0, 1001, 1950, 3003, 4100, 5005, 6006, 7007), 1001, 6006),
        ((0, 1001, 2002, 3003, 4004, 5005, 6006, 7007), 2002, 6006),
    ]

    for idx, item in enumerate(queue.items):
        pts_ticks, start_req, end_req = pts_scenarios[idx % len(pts_scenarios)]
        req = build_temporal_refinement_request(
            item,
            upstream_queue_digest=queue.queue_digest,
            selected_stream_index=0,
            requested_start_pts=start_req,
            requested_end_pts=end_req,
            pts_ticks=pts_ticks,
            declared_rate_num=30000,
            declared_rate_den=1001,
        )
        diag = evaluate_pts_fixture_diagnostic(
            timebase_num=item.source_timebase_num,
            timebase_den=item.source_timebase_den,
            pts_ticks=pts_ticks,
            requested_start_pts=req.requested_start_pts,
            requested_end_pts=req.requested_end_pts,
            declared_rate_num=30000,
            declared_rate_den=1001,
        )
        t_rec = build_temporal_preparation_record(
            refinement_request=req,
            pts_diagnostic=diag,
            declared_rate_num=30000,
            declared_rate_den=1001,
        )
        v1 = build_editorial_proposal(
            queue_item=item,
            temporal_request=req,
            proposed_action="REVIEW_CANDIDATE",
            rationale_note=f"Initial candidate review for {item.queue_item_id}.",
        )
        v2 = advance_proposal_revision(
            prior_proposal=v1,
            proposed_action="REQUEST_MEASUREMENT",
            rationale_note=f"Request source-native PTS measurement for {item.queue_item_id}.",
        )
        v3 = advance_proposal_revision(
            prior_proposal=v2,
            proposed_action="DEFER_PENDING_EVIDENCE",
            rationale_note=f"Defer final cut pending real PTS and human review for {item.queue_item_id}.",
        )
        chain = (v1, v2, v3)
        env = build_editorial_handoff_envelope(
            candidate_item=item,
            temporal_record=t_rec,
            proposal_revisions=chain,
        )

        temporal_requests.append(req)
        pts_diagnostics.append(diag)
        temporal_records.append(t_rec)
        proposal_chains.append(chain)
        handoff_envelopes.append(env)

    prep_packet = build_gate3_offline_preparation_packet(
        candidate_queue=queue,
        temporal_records=temporal_records,
        handoff_envelopes=handoff_envelopes,
        packet_id="g3prep_e2e_default",
    )

    m13_lineage = audit_cross_stage_lineage(
        candidate_queue=queue,
        temporal_request=temporal_requests[0],
        editorial_proposal=proposal_chains[0][-1],
        proposal_revision_chain=proposal_chains[0],
    )
    m15_lineage = audit_mega15_lineage(
        queue=queue,
        temporal_requests=temporal_requests,
        proposal_chains=proposal_chains,
        preparation_packet=prep_packet,
        upstream_lineage_receipt=m13_lineage,
        receipt_id="m15_lineage_e2e_default",
    )

    m13_qc_readiness = evaluate_qc_readiness(
        {
            "candidate_queue": queue.to_dict(),
            "temporal_request": temporal_requests[0].to_dict(),
            "editorial_proposal": proposal_chains[0][-1].to_dict(),
            "proposal_revision_chain": [p.to_dict() for p in proposal_chains[0]],
        }
    )
    m13_blocker_summary = build_release_blocker_summary(
        lineage_receipt=m13_lineage,
        qc_packet=m13_qc_readiness,
    )

    render_spec = build_render_preflight_specification(
        preparation_packet=prep_packet,
        lineage_receipt=m15_lineage,
        specification_id="rpreflight_e2e_default",
    )
    qc_bundle = build_qc_requirements_bundle(
        render_specification=render_spec,
        qc_readiness_packet=m13_qc_readiness,
        bundle_id="qcreq_e2e_default",
    )
    refusal_cert = build_release_refusal_certificate(
        preparation_packet=prep_packet,
        mega15_lineage_receipt=m15_lineage,
        render_specification=render_spec,
        qc_bundle=qc_bundle,
        upstream_blocker_summary=m13_blocker_summary,
        untrusted_authority_payload=untrusted_authority_payload,
        certificate_id="relrefusal_e2e_default",
    )

    return build_mega15_16_offline_report(
        preparation_packet=prep_packet,
        mega15_lineage_receipt=m15_lineage,
        render_specification=render_spec,
        qc_bundle=qc_bundle,
        refusal_certificate=refusal_cert,
        report_id="mega15_16_offline_report_e2e",
    )
