from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from gate3.qc import bare_pass_is_insufficient
from vip_fvs.real_preview_receipt import FIXTURE_NOT_OBSERVED_REQUIRED
from vip_lab.common import (
    NOT_OBSERVED,
    SyntheticContextMarker,
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)
from vip_lab.mega13 import (
    BLOCKER_AUDIO_EDITORIAL_QC_NOT_OBSERVED,
    BLOCKER_TECHNICAL_QC_NOT_OBSERVED,
    BLOCKER_VISUAL_EDITORIAL_QC_NOT_OBSERVED,
)
from vip_lab.mega15 import Gate3PreparationPacket, verify_gate3_preparation_packet

REFUSAL_BARE_QC_PASS_INSUFFICIENT = "REFUSAL_BARE_QC_PASS_INSUFFICIENT"
REFUSAL_FORGED_SENSORY_OR_MEASURED_QC = "REFUSAL_FORGED_SENSORY_OR_MEASURED_QC"


def validate_qc_claim_or_refuse(claim: Mapping[str, Any]) -> None:
    if not isinstance(claim, Mapping):
        raise VipLabError("QC claim must be a mapping.")
    if bare_pass_is_insufficient(claim):
        raise VipLabError(
            f"{REFUSAL_BARE_QC_PASS_INSUFFICIENT}: bare edit_qc_status='PASS' without qc_scope and supporting_evidence_refs is rejected by gate3.qc.bare_pass_is_insufficient."
        )
    for field_name in (
        "technical_qc_observed",
        "visual_editorial_qc_observed",
        "audio_editorial_qc_observed",
    ):
        val = claim.get(field_name)
        if val is not None and val != NOT_OBSERVED:
            raise VipLabError(
                f"{REFUSAL_FORGED_SENSORY_OR_MEASURED_QC}: {field_name}={val!r} is forbidden in synthetic offline preparation (must be {NOT_OBSERVED!r})."
            )
    if claim.get("edit_qc_status") == "PASS" or claim.get("overall_qc_status") == "PASS":
        raise VipLabError(
            f"{REFUSAL_FORGED_SENSORY_OR_MEASURED_QC}: QC PASS cannot be claimed in synthetic offline preparation without real render and human sensory observation."
        )


@dataclass(frozen=True)
class QCDimensionRequirement:
    dimension_id: str
    required_evidence_class: str
    current_observation_state: str
    satisfied: bool
    required_scope_fields: tuple[str, ...]
    refusal_code: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension_id": self.dimension_id,
            "required_evidence_class": self.required_evidence_class,
            "current_observation_state": self.current_observation_state,
            "satisfied": self.satisfied,
            "required_scope_fields": list(self.required_scope_fields),
            "refusal_code": self.refusal_code,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QCDimensionRequirement:
        if not isinstance(payload, Mapping):
            raise VipLabError("QCDimensionRequirement payload must be a mapping.")
        if payload.get("current_observation_state") != NOT_OBSERVED or bool(payload.get("satisfied")):
            raise VipLabError(
                f"{REFUSAL_FORGED_SENSORY_OR_MEASURED_QC}: QCDimensionRequirement must remain NOT_OBSERVED and satisfied=False."
            )
        return cls(
            dimension_id=str(payload["dimension_id"]),
            required_evidence_class=str(payload["required_evidence_class"]),
            current_observation_state=NOT_OBSERVED,
            satisfied=False,
            required_scope_fields=tuple(str(f) for f in payload["required_scope_fields"]),
            refusal_code=str(payload["refusal_code"]),
        )


@dataclass(frozen=True)
class QCRequirementManifest:
    manifest_id: str
    schema_version: str
    synthetic_context: SyntheticContextMarker
    preparation_packet_id: str
    preparation_packet_digest: str
    dimensions: tuple[QCDimensionRequirement, ...]
    technical_qc_observed: str
    visual_editorial_qc_observed: str
    audio_editorial_qc_observed: str
    bare_pass_rejected: bool
    fixture_not_observed_required: tuple[str, ...]
    overall_qc_status: str
    manifest_digest: str

    def _body_without_digest(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "schema_version": self.schema_version,
            "synthetic_context": self.synthetic_context.to_dict(),
            "preparation_packet_id": self.preparation_packet_id,
            "preparation_packet_digest": self.preparation_packet_digest,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "technical_qc_observed": self.technical_qc_observed,
            "visual_editorial_qc_observed": self.visual_editorial_qc_observed,
            "audio_editorial_qc_observed": self.audio_editorial_qc_observed,
            "bare_pass_rejected": self.bare_pass_rejected,
            "fixture_not_observed_required": list(self.fixture_not_observed_required),
            "overall_qc_status": self.overall_qc_status,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._body_without_digest()
        body["manifest_digest"] = self.manifest_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QCRequirementManifest:
        if not isinstance(payload, Mapping):
            raise VipLabError("QCRequirementManifest payload must be a mapping.")
        validate_qc_claim_or_refuse(payload)
        manifest = cls(
            manifest_id=str(payload["manifest_id"]),
            schema_version=str(payload["schema_version"]),
            synthetic_context=SyntheticContextMarker.from_dict(payload["synthetic_context"]),
            preparation_packet_id=str(payload["preparation_packet_id"]),
            preparation_packet_digest=validate_hex_digest(
                str(payload["preparation_packet_digest"]), field_name="preparation_packet_digest"
            ),
            dimensions=tuple(QCDimensionRequirement.from_dict(d) for d in payload["dimensions"]),
            technical_qc_observed=str(payload["technical_qc_observed"]),
            visual_editorial_qc_observed=str(payload["visual_editorial_qc_observed"]),
            audio_editorial_qc_observed=str(payload["audio_editorial_qc_observed"]),
            bare_pass_rejected=bool(payload["bare_pass_rejected"]),
            fixture_not_observed_required=tuple(
                str(x) for x in payload["fixture_not_observed_required"]
            ),
            overall_qc_status=str(payload["overall_qc_status"]),
            manifest_digest=validate_hex_digest(str(payload["manifest_digest"]), field_name="manifest_digest"),
        )
        verify_qc_requirement_manifest(manifest)
        return manifest


def build_qc_requirement_manifest(
    *,
    manifest_id: str,
    preparation_packet: Gate3PreparationPacket,
    untrusted_qc_claim: Mapping[str, Any] | None = None,
) -> QCRequirementManifest:
    verify_gate3_preparation_packet(preparation_packet)
    if untrusted_qc_claim is not None:
        validate_qc_claim_or_refuse(untrusted_qc_claim)

    bare_rejected = bool(bare_pass_is_insufficient({"edit_qc_status": "PASS"}))
    if not bare_rejected:
        raise VipLabError("gate3.qc.bare_pass_is_insufficient unexpectedly returned False.")

    dimensions = (
        QCDimensionRequirement(
            dimension_id="technical_qc",
            required_evidence_class="MEASURED",
            current_observation_state=NOT_OBSERVED,
            satisfied=False,
            required_scope_fields=(
                "rendered_container_sha256",
                "measured_pts_ticks",
                "duration_ts",
                "stream_index",
            ),
            refusal_code=BLOCKER_TECHNICAL_QC_NOT_OBSERVED,
        ),
        QCDimensionRequirement(
            dimension_id="visual_editorial_qc",
            required_evidence_class="VISUALLY_OBSERVED",
            current_observation_state=NOT_OBSERVED,
            satisfied=False,
            required_scope_fields=(
                "human_reviewer_id",
                "observed_frame_range",
                "cut_continuity_assessment",
            ),
            refusal_code=BLOCKER_VISUAL_EDITORIAL_QC_NOT_OBSERVED,
        ),
        QCDimensionRequirement(
            dimension_id="audio_editorial_qc",
            required_evidence_class="AUDIO_OBSERVED",
            current_observation_state=NOT_OBSERVED,
            satisfied=False,
            required_scope_fields=(
                "human_listener_id",
                "audio_channel_layout",
                "av_sync_assessment",
            ),
            refusal_code=BLOCKER_AUDIO_EDITORIAL_QC_NOT_OBSERVED,
        ),
    )

    temp = QCRequirementManifest(
        manifest_id=manifest_id,
        schema_version="1.0.0",
        synthetic_context=SyntheticContextMarker.default("mega16.qc_requirements"),
        preparation_packet_id=preparation_packet.packet_id,
        preparation_packet_digest=preparation_packet.packet_digest,
        dimensions=dimensions,
        technical_qc_observed=NOT_OBSERVED,
        visual_editorial_qc_observed=NOT_OBSERVED,
        audio_editorial_qc_observed=NOT_OBSERVED,
        bare_pass_rejected=bare_rejected,
        fixture_not_observed_required=tuple(FIXTURE_NOT_OBSERVED_REQUIRED),
        overall_qc_status="BLOCKED_NOT_OBSERVED",
        manifest_digest="0" * 64,
    )
    digest = canonical_sha256(temp._body_without_digest())
    manifest = QCRequirementManifest(**{**temp.__dict__, "manifest_digest": digest})
    verify_qc_requirement_manifest(manifest)
    return manifest


def verify_qc_requirement_manifest(manifest: QCRequirementManifest) -> None:
    if not isinstance(manifest, QCRequirementManifest):
        raise VipLabError("Expected QCRequirementManifest instance.")
    manifest.synthetic_context.validate()
    validate_hex_digest(manifest.preparation_packet_digest, field_name="preparation_packet_digest")
    validate_hex_digest(manifest.manifest_digest, field_name="manifest_digest")
    if manifest.technical_qc_observed != NOT_OBSERVED:
        raise VipLabError(f"{REFUSAL_FORGED_SENSORY_OR_MEASURED_QC}: technical_qc_observed must be NOT_OBSERVED.")
    if manifest.visual_editorial_qc_observed != NOT_OBSERVED:
        raise VipLabError(f"{REFUSAL_FORGED_SENSORY_OR_MEASURED_QC}: visual_editorial_qc_observed must be NOT_OBSERVED.")
    if manifest.audio_editorial_qc_observed != NOT_OBSERVED:
        raise VipLabError(f"{REFUSAL_FORGED_SENSORY_OR_MEASURED_QC}: audio_editorial_qc_observed must be NOT_OBSERVED.")
    if manifest.bare_pass_rejected is not True:
        raise VipLabError(f"{REFUSAL_BARE_QC_PASS_INSUFFICIENT}: bare_pass_rejected must be True.")
    if manifest.fixture_not_observed_required != tuple(FIXTURE_NOT_OBSERVED_REQUIRED):
        raise VipLabError("fixture_not_observed_required mismatch with vip_fvs.real_preview_receipt.")
    if manifest.overall_qc_status != "BLOCKED_NOT_OBSERVED":
        raise VipLabError(
            f"{REFUSAL_FORGED_SENSORY_OR_MEASURED_QC}: overall_qc_status must be 'BLOCKED_NOT_OBSERVED', got {manifest.overall_qc_status!r}."
        )
    if len(manifest.dimensions) != 3:
        raise VipLabError("QCRequirementManifest must have exactly 3 QC dimensions.")
    for dim in manifest.dimensions:
        if dim.current_observation_state != NOT_OBSERVED or dim.satisfied is not False:
            raise VipLabError(
                f"{REFUSAL_FORGED_SENSORY_OR_MEASURED_QC}: dimension {dim.dimension_id!r} cannot be satisfied in synthetic preflight."
            )

    expected_digest = canonical_sha256(manifest._body_without_digest())
    if manifest.manifest_digest != expected_digest:
        raise VipLabError(
            f"QCRequirementManifest digest mismatch: expected {expected_digest}, got {manifest.manifest_digest}"
        )
