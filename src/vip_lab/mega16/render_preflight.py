from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from vip_lab.common import (
    FORBIDDEN_EXTERNAL_AUTHORITY_KEYS,
     SyntheticContextMarker,
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)
from vip_lab.mega15 import (
    Gate3LineageCertificate,
    Gate3PreparationPacket,
    verify_gate3_lineage_certificate,
    verify_gate3_preparation_packet,
)

REFUSAL_RENDER_EXECUTION_FORBIDDEN = "REFUSAL_RENDER_EXECUTION_FORBIDDEN"


def _assert_no_render_execution_overrides(overrides: Mapping[str, Any] | None) -> None:
    if overrides is None:
        return
    if not isinstance(overrides, Mapping):
        raise VipLabError("untrusted_overrides must be a mapping when provided.")
    forbidden_flags = {
        "render_executed",
        "ffmpeg_invocation_permitted",
        "media_file_creation_permitted",
        "subprocess_execution_permitted",
        "preview_policy_authorized",
        "production_export_authorized",
        *FORBIDDEN_EXTERNAL_AUTHORITY_KEYS,
    }
    triggered = sorted(k for k in forbidden_flags if bool(overrides.get(k)))
    if triggered:
        raise VipLabError(
            f"{REFUSAL_RENDER_EXECUTION_FORBIDDEN}: render/subprocess/export execution is prohibited in synthetic preflight: {triggered}"
        )


@dataclass(frozen=True)
class InertDryRunRenderIntent:
    intent_id: str
    handoff_id: str
    candidate_id: str
    source_revision_id: str
    source_sha256: str
    source_path: str
    selected_stream_index: int
    time_base: str
    proposed_interval_ticks: tuple[int, int]
    execution_mode: str
    ffmpeg_invocation_permitted: bool
    media_file_creation_permitted: bool
    subprocess_execution_permitted: bool
    render_executed: bool
    intent_digest: str

    def _body_without_digest(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "handoff_id": self.handoff_id,
            "candidate_id": self.candidate_id,
            "source_revision_id": self.source_revision_id,
            "source_sha256": self.source_sha256,
            "source_path": self.source_path,
            "selected_stream_index": self.selected_stream_index,
            "time_base": self.time_base,
            "proposed_interval_ticks": list(self.proposed_interval_ticks),
            "execution_mode": self.execution_mode,
            "ffmpeg_invocation_permitted": self.ffmpeg_invocation_permitted,
            "media_file_creation_permitted": self.media_file_creation_permitted,
            "subprocess_execution_permitted": self.subprocess_execution_permitted,
            "render_executed": self.render_executed,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._body_without_digest()
        body["intent_digest"] = self.intent_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> InertDryRunRenderIntent:
        if not isinstance(payload, Mapping):
            raise VipLabError("InertDryRunRenderIntent payload must be a mapping.")
        _assert_no_render_execution_overrides(payload)
        if payload.get("execution_mode") != "INERT_DECLARATIVE_DRY_RUN_ONLY":
            raise VipLabError(
                f"{REFUSAL_RENDER_EXECUTION_FORBIDDEN}: execution_mode must be 'INERT_DECLARATIVE_DRY_RUN_ONLY'."
            )
        interval = payload["proposed_interval_ticks"]
        intent = cls(
            intent_id=str(payload["intent_id"]),
            handoff_id=str(payload["handoff_id"]),
            candidate_id=str(payload["candidate_id"]),
            source_revision_id=str(payload["source_revision_id"]),
            source_sha256=validate_hex_digest(str(payload["source_sha256"]), field_name="source_sha256"),
            source_path=str(payload["source_path"]),
            selected_stream_index=int(payload["selected_stream_index"]),
            time_base=str(payload["time_base"]),
            proposed_interval_ticks=(int(interval[0]), int(interval[1])),
            execution_mode="INERT_DECLARATIVE_DRY_RUN_ONLY",
            ffmpeg_invocation_permitted=False,
            media_file_creation_permitted=False,
            subprocess_execution_permitted=False,
            render_executed=False,
            intent_digest=validate_hex_digest(str(payload["intent_digest"]), field_name="intent_digest"),
        )
        expected = canonical_sha256(intent._body_without_digest())
        if intent.intent_digest != expected:
            raise VipLabError(
                f"InertDryRunRenderIntent digest mismatch: expected {expected}, got {intent.intent_digest}"
            )
        return intent


@dataclass(frozen=True)
class RenderPreflightReport:
    preflight_id: str
    schema_version: str
    synthetic_context: SyntheticContextMarker
    preparation_packet_id: str
    preparation_packet_digest: str
    lineage_certificate_id: str
    lineage_certificate_digest: str
    dry_run_intents: tuple[InertDryRunRenderIntent, ...]
    preview_policy_authorized: bool
    render_executed: bool
    production_export_authorized: bool
    export_status: str
    report_digest: str

    def _body_without_digest(self) -> dict[str, Any]:
        return {
            "preflight_id": self.preflight_id,
            "schema_version": self.schema_version,
            "synthetic_context": self.synthetic_context.to_dict(),
            "preparation_packet_id": self.preparation_packet_id,
            "preparation_packet_digest": self.preparation_packet_digest,
            "lineage_certificate_id": self.lineage_certificate_id,
            "lineage_certificate_digest": self.lineage_certificate_digest,
            "dry_run_intents": [i.to_dict() for i in self.dry_run_intents],
            "preview_policy_authorized": self.preview_policy_authorized,
            "render_executed": self.render_executed,
            "production_export_authorized": self.production_export_authorized,
            "export_status": self.export_status,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._body_without_digest()
        body["report_digest"] = self.report_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> RenderPreflightReport:
        if not isinstance(payload, Mapping):
            raise VipLabError("RenderPreflightReport payload must be a mapping.")
        _assert_no_render_execution_overrides(payload)
        report = cls(
            preflight_id=str(payload["preflight_id"]),
            schema_version=str(payload["schema_version"]),
            synthetic_context=SyntheticContextMarker.from_dict(payload["synthetic_context"]),
            preparation_packet_id=str(payload["preparation_packet_id"]),
            preparation_packet_digest=validate_hex_digest(
                str(payload["preparation_packet_digest"]), field_name="preparation_packet_digest"
            ),
            lineage_certificate_id=str(payload["lineage_certificate_id"]),
            lineage_certificate_digest=validate_hex_digest(
                str(payload["lineage_certificate_digest"]), field_name="lineage_certificate_digest"
            ),
            dry_run_intents=tuple(
                InertDryRunRenderIntent.from_dict(i) for i in payload["dry_run_intents"]
            ),
            preview_policy_authorized=bool(payload["preview_policy_authorized"]),
            render_executed=bool(payload["render_executed"]),
            production_export_authorized=bool(payload["production_export_authorized"]),
            export_status=str(payload["export_status"]),
            report_digest=validate_hex_digest(str(payload["report_digest"]), field_name="report_digest"),
        )
        verify_render_preflight_report(report)
        return report


def build_render_preflight_report(
    *,
    preflight_id: str,
    preparation_packet: Gate3PreparationPacket,
    lineage_certificate: Gate3LineageCertificate,
    untrusted_overrides: Mapping[str, Any] | None = None,
) -> RenderPreflightReport:
    _assert_no_render_execution_overrides(untrusted_overrides)
    verify_gate3_preparation_packet(preparation_packet)
    verify_gate3_lineage_certificate(lineage_certificate)

    if lineage_certificate.preparation_packet_id != preparation_packet.packet_id:
        raise VipLabError("preparation_packet_id mismatch between packet and lineage_certificate.")
    if lineage_certificate.preparation_packet_digest != preparation_packet.packet_digest:
        raise VipLabError("preparation_packet_digest mismatch between packet and lineage_certificate.")

    intents: list[InertDryRunRenderIntent] = []
    for env in preparation_packet.handoff_envelopes:
        temp_intent = InertDryRunRenderIntent(
            intent_id=f"intent_{env.handoff_id}",
            handoff_id=env.handoff_id,
            candidate_id=env.candidate_id,
            source_revision_id=env.source_revision_id,
            source_sha256=env.source_sha256,
            source_path=env.source_path,
            selected_stream_index=env.selected_stream_index,
            time_base=env.time_base,
            proposed_interval_ticks=env.proposed_interval_ticks,
            execution_mode="INERT_DECLARATIVE_DRY_RUN_ONLY",
            ffmpeg_invocation_permitted=False,
            media_file_creation_permitted=False,
            subprocess_execution_permitted=False,
            render_executed=False,
            intent_digest="0" * 64,
        )
        intent_digest = canonical_sha256(temp_intent._body_without_digest())
        intents.append(
            InertDryRunRenderIntent(**{**temp_intent.__dict__, "intent_digest": intent_digest})
        )

    temp_report = RenderPreflightReport(
        preflight_id=preflight_id,
        schema_version="1.0.0",
        synthetic_context=SyntheticContextMarker.default("mega16.render_preflight"),
        preparation_packet_id=preparation_packet.packet_id,
        preparation_packet_digest=preparation_packet.packet_digest,
        lineage_certificate_id=lineage_certificate.certificate_id,
        lineage_certificate_digest=lineage_certificate.certificate_digest,
        dry_run_intents=tuple(intents),
        preview_policy_authorized=False,
        render_executed=False,
        production_export_authorized=False,
        export_status="REFUSED_NOT_AUTHORIZED",
        report_digest="0" * 64,
    )
    report_digest = canonical_sha256(temp_report._body_without_digest())
    report = RenderPreflightReport(**{**temp_report.__dict__, "report_digest": report_digest})
    verify_render_preflight_report(report)
    return report


def verify_render_preflight_report(report: RenderPreflightReport) -> None:
    if not isinstance(report, RenderPreflightReport):
        raise VipLabError("Expected RenderPreflightReport instance.")
    report.synthetic_context.validate()
    validate_hex_digest(report.preparation_packet_digest, field_name="preparation_packet_digest")
    validate_hex_digest(report.lineage_certificate_digest, field_name="lineage_certificate_digest")
    validate_hex_digest(report.report_digest, field_name="report_digest")
    if not report.dry_run_intents:
        raise VipLabError("RenderPreflightReport.dry_run_intents must not be empty.")
    for intent in report.dry_run_intents:
        if intent.execution_mode != "INERT_DECLARATIVE_DRY_RUN_ONLY":
            raise VipLabError(f"{REFUSAL_RENDER_EXECUTION_FORBIDDEN}: invalid execution_mode.")
        if (
            intent.ffmpeg_invocation_permitted
            or intent.media_file_creation_permitted
            or intent.subprocess_execution_permitted
            or intent.render_executed
        ):
            raise VipLabError(f"{REFUSAL_RENDER_EXECUTION_FORBIDDEN}: inert intent has active execution flag.")
        expected_intent_digest = canonical_sha256(intent._body_without_digest())
        if intent.intent_digest != expected_intent_digest:
            raise VipLabError("InertDryRunRenderIntent digest mismatch.")

    if report.preview_policy_authorized is not False:
        raise VipLabError(f"{REFUSAL_RENDER_EXECUTION_FORBIDDEN}: preview_policy_authorized must be False.")
    if report.render_executed is not False:
        raise VipLabError(f"{REFUSAL_RENDER_EXECUTION_FORBIDDEN}: render_executed must be False.")
    if report.production_export_authorized is not False:
        raise VipLabError(f"{REFUSAL_RENDER_EXECUTION_FORBIDDEN}: production_export_authorized must be False.")
    if report.export_status != "REFUSED_NOT_AUTHORIZED":
        raise VipLabError("RenderPreflightReport.export_status must be 'REFUSED_NOT_AUTHORIZED'.")

    expected_digest = canonical_sha256(report._body_without_digest())
    if report.report_digest != expected_digest:
        raise VipLabError(
            f"RenderPreflightReport digest mismatch: expected {expected_digest}, got {report.report_digest}"
        )
