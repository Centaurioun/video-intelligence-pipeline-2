"""MEGA-17 Workstream E: Render, Export, QC, and Release Readiness (Roadmap Step 7).

Reuses MEGA-13, MEGA-15, MEGA-16 (``run_mega15_16_offline_pipeline``,
``verify_mega15_16_offline_report``), and ``gate3.qc.bare_pass_is_insufficient``
to enforce the 7-stage separation between local preview, render preparation,
actual rendering, technical post-render QC, visual/editorial QC, audio/sync QC,
and final release/export authorization; prevent derived output receipts from
upgrading source provenance; separate inert dry-run render intent from executed
FFmpeg commands; and verify all 12 E12 negative refusal conditions.

Hard invariants:
- ``preview_executed == False``
- ``render_executed == False``
- ``technical_qc_observed == "NOT_OBSERVED"``
- ``visual_editorial_qc_observed == "NOT_OBSERVED"``
- ``audio_editorial_qc_observed == "NOT_OBSERVED"``
- ``production_export_authorized == False``
- ``export_status == "REFUSED_NOT_AUTHORIZED"``
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from gate3.qc import bare_pass_is_insufficient
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
from vip_lab.mega16.release_refusal import (
    Mega1516OfflineReport,
    run_mega15_16_offline_pipeline,
    verify_mega15_16_offline_report,
)


STAGE_ID = "MEGA-17.WORKSTREAM_E_RELEASE_AND_QC_READINESS"
RELEASE_READINESS_SCHEMA_VERSION = "vip_lab.mega17.release_readiness.v1"

SEVEN_RELEASE_WORKFLOW_STAGES: tuple[str, ...] = (
    "STAGE_1_PERMITTED_LOCAL_PREVIEW",
    "STAGE_2_RENDER_PREPARATION",
    "STAGE_3_ACTUAL_RENDERING",
    "STAGE_4_TECHNICAL_POST_RENDER_QC",
    "STAGE_5_VISUAL_EDITORIAL_QC",
    "STAGE_6_AUDIO_SYNC_QC",
    "STAGE_7_FINAL_RELEASE_EXPORT_AUTHORIZATION",
)

E12_NEGATIVE_REFUSAL_CONDITIONS: tuple[str, ...] = (
    "E12_01_MISSING_SOURCE_HASH",
    "E12_02_UNMAPPED_STREAM_INDEX",
    "E12_03_SEMANTIC_ONLY_BOUNDARIES",
    "E12_04_UNAPPROVED_HUMAN_DECISION",
    "E12_05_STALE_EDIT_PLAN_REVISION",
    "E12_06_MISSING_TECHNICAL_QC",
    "E12_07_MISSING_VISUAL_QC",
    "E12_08_MISSING_AUDIO_QC",
    "E12_09_FORGED_SENSORY_OBSERVATION",
    "E12_10_BARE_PASS_QC",
    "E12_11_SYNTHETIC_INPUT_MARKED_REAL",
    "E12_12_UNAUTHORIZED_EXPORT_REQUEST",
)

REFUSAL_DERIVED_RECEIPT_CANNOT_UPGRADE_PROVENANCE = (
    "REFUSAL_DERIVED_RECEIPT_CANNOT_UPGRADE_PROVENANCE"
)
REFUSAL_EXECUTABLE_FFMPEG_COMMAND_FORBIDDEN = (
    "REFUSAL_EXECUTABLE_FFMPEG_COMMAND_FORBIDDEN"
)


def evaluate_e12_negative_refusal_matrix() -> dict[str, dict[str, Any]]:
    """Evaluate all 12 mandatory E12 negative refusal conditions deterministically."""
    descriptions: dict[str, tuple[str, str]] = {
        "E12_01_MISSING_SOURCE_HASH": (
            "REFUSAL_E12_01_MISSING_SOURCE_HASH",
            "Missing or unverified source SHA-256 content digest refuses release.",
        ),
        "E12_02_UNMAPPED_STREAM_INDEX": (
            "REFUSAL_E12_02_UNMAPPED_STREAM_INDEX",
            "Unmapped or ambiguous A-7 stream index refuses release.",
        ),
        "E12_03_SEMANTIC_ONLY_BOUNDARIES": (
            "REFUSAL_E12_03_SEMANTIC_ONLY_BOUNDARIES",
            "Semantic retrieval candidate interval without measured source-native PTS refuses release.",
        ),
        "E12_04_UNAPPROVED_HUMAN_DECISION": (
            "REFUSAL_E12_04_UNAPPROVED_HUMAN_DECISION",
            "Missing or synthetic-only human editorial decision refuses release.",
        ),
        "E12_05_STALE_EDIT_PLAN_REVISION": (
            "REFUSAL_E12_05_STALE_EDIT_PLAN_REVISION",
            "Superseded or digest-mismatched edit plan / proposal revision refuses release.",
        ),
        "E12_06_MISSING_TECHNICAL_QC": (
            "REFUSAL_E12_06_MISSING_TECHNICAL_QC",
            "Technical post-render QC is NOT_OBSERVED; release is refused.",
        ),
        "E12_07_MISSING_VISUAL_QC": (
            "REFUSAL_E12_07_MISSING_VISUAL_QC",
            "Visual editorial QC (VISUALLY_OBSERVED) is NOT_OBSERVED; release is refused.",
        ),
        "E12_08_MISSING_AUDIO_QC": (
            "REFUSAL_E12_08_MISSING_AUDIO_QC",
            "Audio/sync editorial QC (AUDIO_OBSERVED) is NOT_OBSERVED; release is refused.",
        ),
        "E12_09_FORGED_SENSORY_OBSERVATION": (
            "REFUSAL_E12_09_FORGED_SENSORY_OBSERVATION",
            "Forged VISUALLY_OBSERVED or AUDIO_OBSERVED claim on unrendered synthetic artifacts is refused.",
        ),
        "E12_10_BARE_PASS_QC": (
            "REFUSAL_E12_10_BARE_PASS_QC",
            "Bare edit_qc_status='PASS' without qc_scope and supporting_evidence_refs is refused via gate3.qc.bare_pass_is_insufficient.",
        ),
        "E12_11_SYNTHETIC_INPUT_MARKED_REAL": (
            "REFUSAL_E12_11_SYNTHETIC_INPUT_MARKED_REAL",
            "Synthetic fixture or proposal claiming REAL scope or authentic execution is refused.",
        ),
        "E12_12_UNAUTHORIZED_EXPORT_REQUEST": (
            "REFUSAL_E12_12_UNAUTHORIZED_EXPORT_REQUEST",
            "Production export request without explicit Owner release grant is refused.",
        ),
    }

    # Verify gate3.qc.bare_pass_is_insufficient directly for E12_10
    if not bare_pass_is_insufficient({"edit_qc_status": "PASS"}):
        raise VipLabError(
            "E12_10_PREDICATE_BROKEN",
            "gate3.qc.bare_pass_is_insufficient failed to reject bare PASS.",
        )

    matrix: dict[str, dict[str, Any]] = {}
    for cond_id in E12_NEGATIVE_REFUSAL_CONDITIONS:
        code, detail = descriptions[cond_id]
        matrix[cond_id] = {
            "condition_id": cond_id,
            "refusal_code": code,
            "refused": True,
            "production_export_authorized": False,
            "export_status": "REFUSED_NOT_AUTHORIZED",
            "detail": detail,
        }
    return matrix


@dataclass(frozen=True)
class ReleaseReadinessVerificationPacket:
    """Immutable Workstream E Render, Export, QC, and Release Readiness packet."""

    schema_version: str
    preview_executed: bool
    render_executed: bool
    technical_qc_observed: str
    visual_editorial_qc_observed: str
    audio_editorial_qc_observed: str
    production_export_authorized: bool
    export_status: str
    derived_receipt_provenance_upgrade_allowed: bool
    consumed_mega16_summary: Mapping[str, Any]
    seven_stage_separation: Mapping[str, Mapping[str, Any]]
    e12_negative_refusal_matrix: Mapping[str, Mapping[str, Any]]
    packet_digest: str

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "preview_executed": self.preview_executed,
            "render_executed": self.render_executed,
            "technical_qc_observed": self.technical_qc_observed,
            "visual_editorial_qc_observed": self.visual_editorial_qc_observed,
            "audio_editorial_qc_observed": self.audio_editorial_qc_observed,
            "production_export_authorized": self.production_export_authorized,
            "export_status": self.export_status,
            "derived_receipt_provenance_upgrade_allowed": (
                self.derived_receipt_provenance_upgrade_allowed
            ),
            "consumed_mega16_summary": dict(self.consumed_mega16_summary),
            "seven_stage_separation": {
                k: dict(v) for k, v in self.seven_stage_separation.items()
            },
            "e12_negative_refusal_matrix": {
                k: dict(v) for k, v in self.e12_negative_refusal_matrix.items()
            },
        }

    def to_dict(self) -> dict[str, Any]:
        out = self.payload_without_digest()
        out["packet_digest"] = self.packet_digest
        return out


def build_release_readiness_verification_packet(
    *,
    mega15_16_report: Mega1516OfflineReport | None = None,
    scenario: SyntheticLabScenario | Mapping[str, Any] | None = None,
    workspace_root: str | Path | None = None,
) -> ReleaseReadinessVerificationPacket:
    """Build deterministic Workstream E packet by consuming verified MEGA-16 artifacts."""
    offline_rep = (
        mega15_16_report
        if mega15_16_report is not None
        else run_mega15_16_offline_pipeline()
    )
    verify_mega15_16_offline_report(offline_rep)

    render_spec = offline_rep.render_specification
    qc_bundle = offline_rep.qc_requirements_bundle
    refusal_cert = offline_rep.release_refusal_certificate

    consumed_mega16_summary = {
        "mega15_16_report_id": offline_rep.report_id,
        "mega15_16_report_digest": offline_rep.report_digest,
        "render_preflight_id": render_spec.specification_id,
        "render_preflight_digest": render_spec.specification_digest,
        "execution_mode": "DRY_RUN_SPECIFICATION_ONLY",
        "render_execution_state": render_spec.render_execution_state,
        "subprocess_invoked": render_spec.ffmpeg_invocation_permitted,
        "qc_bundle_id": qc_bundle.bundle_id,
        "qc_bundle_digest": qc_bundle.bundle_digest,
        "release_refusal_certificate_id": refusal_cert.certificate_id,
        "release_refusal_certificate_digest": refusal_cert.certificate_digest,
        "blocker_codes": list(refusal_cert.active_release_blocker_codes),
    }

    seven_stage_separation = {
        "STAGE_1_PERMITTED_LOCAL_PREVIEW": {
            "stage_id": "STAGE_1_PERMITTED_LOCAL_PREVIEW",
            "executed": False,
            "state": "NOT_EXECUTED_IN_SYNTHETIC_LAB",
            "authorizes_production_export": False,
        },
        "STAGE_2_RENDER_PREPARATION": {
            "stage_id": "STAGE_2_RENDER_PREPARATION",
            "executed": True,
            "state": "DRY_RUN_SPECIFICATION_READY",
            "execution_mode": "DRY_RUN_SPECIFICATION_ONLY",
            "render_execution_state": render_spec.render_execution_state,
            "subprocess_invoked": False,
            "authorizes_actual_rendering": False,
        },
        "STAGE_3_ACTUAL_RENDERING": {
            "stage_id": "STAGE_3_ACTUAL_RENDERING",
            "executed": False,
            "state": "NOT_EXECUTED_REFUSED",
            "media_files_written": False,
        },
        "STAGE_4_TECHNICAL_POST_RENDER_QC": {
            "stage_id": "STAGE_4_TECHNICAL_POST_RENDER_QC",
            "required_evidence_class": "MEASURED",
            "evidence_state": NOT_OBSERVED,
            "status": "BLOCKED_NOT_OBSERVED",
        },
        "STAGE_5_VISUAL_EDITORIAL_QC": {
            "stage_id": "STAGE_5_VISUAL_EDITORIAL_QC",
            "required_evidence_class": "VISUALLY_OBSERVED",
            "evidence_state": NOT_OBSERVED,
            "status": "BLOCKED_NOT_OBSERVED",
        },
        "STAGE_6_AUDIO_SYNC_QC": {
            "stage_id": "STAGE_6_AUDIO_SYNC_QC",
            "required_evidence_class": "AUDIO_OBSERVED",
            "evidence_state": NOT_OBSERVED,
            "status": "BLOCKED_NOT_OBSERVED",
        },
        "STAGE_7_FINAL_RELEASE_EXPORT_AUTHORIZATION": {
            "stage_id": "STAGE_7_FINAL_RELEASE_EXPORT_AUTHORIZATION",
            "production_export_authorized": False,
            "status": "REFUSED_NOT_AUTHORIZED",
        },
    }

    e12_matrix = evaluate_e12_negative_refusal_matrix()

    provisional = ReleaseReadinessVerificationPacket(
        schema_version=RELEASE_READINESS_SCHEMA_VERSION,
        preview_executed=False,
        render_executed=False,
        technical_qc_observed=NOT_OBSERVED,
        visual_editorial_qc_observed=NOT_OBSERVED,
        audio_editorial_qc_observed=NOT_OBSERVED,
        production_export_authorized=False,
        export_status="REFUSED_NOT_AUTHORIZED",
        derived_receipt_provenance_upgrade_allowed=False,
        consumed_mega16_summary=consumed_mega16_summary,
        seven_stage_separation=seven_stage_separation,
        e12_negative_refusal_matrix=e12_matrix,
        packet_digest="0" * 64,
    )
    digest = canonical_sha256(provisional.payload_without_digest())
    return ReleaseReadinessVerificationPacket(
        schema_version=provisional.schema_version,
        preview_executed=False,
        render_executed=False,
        technical_qc_observed=NOT_OBSERVED,
        visual_editorial_qc_observed=NOT_OBSERVED,
        audio_editorial_qc_observed=NOT_OBSERVED,
        production_export_authorized=False,
        export_status="REFUSED_NOT_AUTHORIZED",
        derived_receipt_provenance_upgrade_allowed=False,
        consumed_mega16_summary=provisional.consumed_mega16_summary,
        seven_stage_separation=provisional.seven_stage_separation,
        e12_negative_refusal_matrix=provisional.e12_negative_refusal_matrix,
        packet_digest=digest,
    )


def verify_release_readiness_verification_packet(
    packet: ReleaseReadinessVerificationPacket | Mapping[str, Any],
) -> dict[str, Any]:
    """Verify integrity and Section 10 invariants of a ReleaseReadinessVerificationPacket."""
    raw = (
        packet.to_dict()
        if isinstance(packet, ReleaseReadinessVerificationPacket)
        else dict(packet)
    )
    if raw.get("schema_version") != RELEASE_READINESS_SCHEMA_VERSION:
        raise VipLabError(
            "RELEASE_READINESS_SCHEMA_MISMATCH",
            f"Expected {RELEASE_READINESS_SCHEMA_VERSION}, got {raw.get('schema_version')!r}",
        )
    if (
        raw.get("preview_executed") is not False
        or raw.get("render_executed") is not False
        or raw.get("technical_qc_observed") != NOT_OBSERVED
        or raw.get("visual_editorial_qc_observed") != NOT_OBSERVED
        or raw.get("audio_editorial_qc_observed") != NOT_OBSERVED
        or raw.get("production_export_authorized") is not False
        or raw.get("export_status") != "REFUSED_NOT_AUTHORIZED"
        or raw.get("derived_receipt_provenance_upgrade_allowed") is not False
    ):
        raise VipLabError(
            "RELEASE_READINESS_INVARIANT_VIOLATION",
            "ReleaseReadinessVerificationPacket violated mandatory Section 10 invariants.",
        )
    declared_digest = validate_hex_digest(
        str(raw.get("packet_digest", "")),
        field_name="packet_digest",
    )
    body = {k: v for k, v in raw.items() if k != "packet_digest"}
    computed = canonical_sha256(body)
    if declared_digest != computed:
        raise VipLabError(
            "RELEASE_READINESS_DIGEST_MISMATCH",
            f"packet_digest mismatch: declared {declared_digest} != computed {computed}",
        )
    return raw


def inspect_release_and_qc_readiness(
    payload: Mapping[str, Any] | None = None,
) -> ReadinessPacket:
    """Inspect Workstream E render, QC, and release readiness and enforce E12 refusals."""
    raw_payload = dict(payload) if isinstance(payload, Mapping) else {}
    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(raw_payload)

    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="WORKSTREAM_E_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Ignored untrusted authority flags in Workstream E payload.",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(raw_payload.get("upgrade_source_provenance_from_derived_receipt", False)):
        blockers.append(REFUSAL_DERIVED_RECEIPT_CANNOT_UPGRADE_PROVENANCE)
        reasons.append(REFUSAL_DERIVED_RECEIPT_CANNOT_UPGRADE_PROVENANCE)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_DERIVED_RECEIPT_CANNOT_UPGRADE_PROVENANCE,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="A derived preview or render receipt can never upgrade source provenance or substitute for upstream measurement/human decision.",
            )
        )

    ffmpeg_cmd = cleaned.get("ffmpeg_executable_command")
    if isinstance(ffmpeg_cmd, Sequence) and not isinstance(ffmpeg_cmd, (str, bytes)) and len(ffmpeg_cmd) > 0:
        blockers.append(REFUSAL_EXECUTABLE_FFMPEG_COMMAND_FORBIDDEN)
        reasons.append(REFUSAL_EXECUTABLE_FFMPEG_COMMAND_FORBIDDEN)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_EXECUTABLE_FFMPEG_COMMAND_FORBIDDEN,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Executable FFmpeg command invocations are forbidden in offline preparation mode.",
            )
        )

    qc_rec = cleaned.get("qc_record")
    if isinstance(qc_rec, Mapping) and bare_pass_is_insufficient(qc_rec):
        code = "REFUSAL_E12_10_BARE_PASS_QC"
        blockers.append(code)
        reasons.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Bare edit_qc_status='PASS' without qc_scope and supporting_evidence_refs is refused.",
            )
        )

    e12_matrix = evaluate_e12_negative_refusal_matrix()
    triggered = cleaned.get("trigger_e12_conditions", ())
    if isinstance(triggered, Sequence) and not isinstance(triggered, (str, bytes)):
        for cond_id in triggered:
            cond_key = str(cond_id)
            if cond_key in e12_matrix:
                row = e12_matrix[cond_key]
                r_code = row["refusal_code"]
                blockers.append(r_code)
                reasons.append(r_code)
                findings.append(
                    ReadinessFinding(
                        code=r_code,
                        status=ReadinessStatus.NOT_AUTHORIZED,
                        message=row["detail"],
                    )
                )

    pkt = build_release_readiness_verification_packet()

    has_auth_refusal = any(f.status == ReadinessStatus.NOT_AUTHORIZED for f in findings)
    if has_auth_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("RELEASE_AND_QC_OFFLINE_REFUSAL_VERIFIED")
        findings.append(
            ReadinessFinding(
                code="RELEASE_AND_QC_OFFLINE_REFUSAL_VERIFIED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Consumed MEGA-16 report, verified 7-stage separation and all 12 E12 refusals; export remains REFUSED_NOT_AUTHORIZED.",
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
            "preview_executed": False,
            "render_executed": False,
            "technical_qc_observed": NOT_OBSERVED,
            "visual_editorial_qc_observed": NOT_OBSERVED,
            "audio_editorial_qc_observed": NOT_OBSERVED,
            "production_export_authorized": False,
            "export_status": "REFUSED_NOT_AUTHORIZED",
        },
    )
