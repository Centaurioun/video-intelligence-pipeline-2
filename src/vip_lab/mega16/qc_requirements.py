"""MEGA-16.2 — Technical & Editorial QC Requirement Bundles (`NOT_OBSERVED` Enforcement).

Documents the exact Gate-3 `gate3.qc.TechnicalQcReport` and `gate3.qc.EditorialQcReport`
structures (`MEASURED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`) required in a future
authorized real pilot, while strictly enforcing that all three QC states remain
`NOT_OBSERVED` in synthetic offline runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from gate3.qc import QCReport, bare_pass_is_insufficient
from vip_lab.common import (
    ReadinessPacket,
    SyntheticContextMarker,
    canonical_sha256,
)
from vip_lab.mega13 import CANONICAL_RELEASE_BLOCKER_CODES
from vip_lab.mega15.temporal_preflight import (
    ensure_non_empty_str,
    make_synthetic_context,
    parse_synthetic_context_dict,
    raise_mega15_error,
    serialize_synthetic_context,
    validate_synthetic_context,
)
from vip_lab.mega16.render_preflight import (
    RenderPreflightSpecification,
    verify_render_preflight_specification,
)

QC_REQUIREMENTS_SCHEMA_VERSION = "1.0.0"
QC_REQUIREMENTS_KIND = "vip_lab.mega16.qc_requirements_bundle"

CANONICAL_QC_BLOCKER_CODE = "GATE3_TECHNICAL_AND_EDITORIAL_QC_NOT_OBSERVED"

REFUSAL_SYNTHETIC_TECHNICAL_QC_PASS = "REFUSAL_SYNTHETIC_TECHNICAL_QC_PASS_FORBIDDEN"
REFUSAL_SYNTHETIC_VISUAL_QC_PASS = "REFUSAL_SYNTHETIC_VISUAL_EDITORIAL_QC_PASS_FORBIDDEN"
REFUSAL_SYNTHETIC_AUDIO_QC_PASS = "REFUSAL_SYNTHETIC_AUDIO_EDITORIAL_QC_PASS_FORBIDDEN"
REFUSAL_QC_EVIDENCE_CLASS_CONFUSION = "REFUSAL_QC_EVIDENCE_CLASS_CONFUSION_FORBIDDEN"
REFUSAL_QC_BLOCKER_REMOVAL = "REFUSAL_QC_BLOCKER_REMOVAL_FORBIDDEN"


def refuse_synthetic_qc_pass_or_class_confusion(
    *,
    claim_technical_qc_pass: bool = False,
    claim_visual_qc_pass: bool = False,
    claim_audio_qc_pass: bool = False,
    technical_evidence_class: str = "MEASURED",
    visual_evidence_class: str = "VISUALLY_OBSERVED",
    audio_evidence_class: str = "AUDIO_OBSERVED",
) -> None:
    """Fail closed if a caller attempts to mint a passing QC report or confuse evidence classes."""
    if technical_evidence_class != "MEASURED":
        raise_mega15_error(
            REFUSAL_QC_EVIDENCE_CLASS_CONFUSION,
            f"Technical QC requires evidence class 'MEASURED', got {technical_evidence_class!r}",
        )
    if visual_evidence_class != "VISUALLY_OBSERVED":
        raise_mega15_error(
            REFUSAL_QC_EVIDENCE_CLASS_CONFUSION,
            f"Visual editorial QC requires evidence class 'VISUALLY_OBSERVED', got {visual_evidence_class!r}",
        )
    if audio_evidence_class != "AUDIO_OBSERVED":
        raise_mega15_error(
            REFUSAL_QC_EVIDENCE_CLASS_CONFUSION,
            f"Audio editorial QC requires evidence class 'AUDIO_OBSERVED', got {audio_evidence_class!r}",
        )

    if claim_technical_qc_pass:
        _ = (QCReport, bare_pass_is_insufficient)
        raise_mega15_error(
            REFUSAL_SYNTHETIC_TECHNICAL_QC_PASS,
            "Minting a passing technical QCReport ('MEASURED') is forbidden when render execution is NOT_OBSERVED.",
        )
    if claim_visual_qc_pass:
        _ = (QCReport, bare_pass_is_insufficient)
        raise_mega15_error(
            REFUSAL_SYNTHETIC_VISUAL_QC_PASS,
            "Minting a passing visual editorial QCReport ('VISUALLY_OBSERVED') is forbidden in synthetic runs.",
        )
    if claim_audio_qc_pass:
        _ = (QCReport, bare_pass_is_insufficient)
        raise_mega15_error(
            REFUSAL_SYNTHETIC_AUDIO_QC_PASS,
            "Minting a passing audio editorial QCReport ('AUDIO_OBSERVED') is forbidden in synthetic runs.",
        )


@dataclass(frozen=True)
class QcRequirementsBundle:
    """Offline Gate-3 technical & editorial QC requirements bundle with strict `NOT_OBSERVED` states."""

    schema_version: str
    kind: str
    bundle_id: str
    render_specification_id: str
    render_specification_digest: str
    upstream_qc_readiness_packet_id: str
    upstream_qc_readiness_packet_digest: str
    technical_qc_required_evidence_class: str
    visual_editorial_qc_required_evidence_class: str
    audio_editorial_qc_required_evidence_class: str
    technical_qc_required_checks: tuple[str, ...]
    visual_editorial_qc_required_checks: tuple[str, ...]
    audio_editorial_qc_required_checks: tuple[str, ...]
    technical_qc_state: str
    visual_editorial_qc_state: str
    audio_editorial_qc_state: str
    overall_qc_gate_status: str
    required_qc_blocker_codes: tuple[str, ...]
    synthetic_context: SyntheticContextMarker
    bundle_digest: str

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "bundle_id": self.bundle_id,
            "render_specification_id": self.render_specification_id,
            "render_specification_digest": self.render_specification_digest,
            "upstream_qc_readiness_packet_id": self.upstream_qc_readiness_packet_id,
            "upstream_qc_readiness_packet_digest": self.upstream_qc_readiness_packet_digest,
            "technical_qc_required_evidence_class": self.technical_qc_required_evidence_class,
            "visual_editorial_qc_required_evidence_class": self.visual_editorial_qc_required_evidence_class,
            "audio_editorial_qc_required_evidence_class": self.audio_editorial_qc_required_evidence_class,
            "technical_qc_required_checks": list(self.technical_qc_required_checks),
            "visual_editorial_qc_required_checks": list(
                self.visual_editorial_qc_required_checks
            ),
            "audio_editorial_qc_required_checks": list(
                self.audio_editorial_qc_required_checks
            ),
            "technical_qc_state": self.technical_qc_state,
            "visual_editorial_qc_state": self.visual_editorial_qc_state,
            "audio_editorial_qc_state": self.audio_editorial_qc_state,
            "overall_qc_gate_status": self.overall_qc_gate_status,
            "required_qc_blocker_codes": list(self.required_qc_blocker_codes),
            "synthetic_context": serialize_synthetic_context(self.synthetic_context),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._digest_payload()
        payload["bundle_digest"] = self.bundle_digest
        return payload

    def validate(self) -> None:
        if self.schema_version != QC_REQUIREMENTS_SCHEMA_VERSION:
            raise_mega15_error(
                "QC_REQUIREMENTS_SCHEMA_MISMATCH",
                f"Unsupported schema_version: {self.schema_version!r}",
            )
        if self.kind != QC_REQUIREMENTS_KIND:
            raise_mega15_error(
                "QC_REQUIREMENTS_KIND_MISMATCH",
                f"Unsupported kind: {self.kind!r}",
            )
        ensure_non_empty_str(self.bundle_id, "bundle_id")
        ensure_non_empty_str(
            self.render_specification_id, "render_specification_id"
        )
        ensure_non_empty_str(
            self.render_specification_digest, "render_specification_digest"
        )
        ensure_non_empty_str(
            self.upstream_qc_readiness_packet_id,
            "upstream_qc_readiness_packet_id",
        )
        ensure_non_empty_str(
            self.upstream_qc_readiness_packet_digest,
            "upstream_qc_readiness_packet_digest",
        )
        validate_synthetic_context(self.synthetic_context)

        refuse_synthetic_qc_pass_or_class_confusion(
            technical_evidence_class=self.technical_qc_required_evidence_class,
            visual_evidence_class=self.visual_editorial_qc_required_evidence_class,
            audio_evidence_class=self.audio_editorial_qc_required_evidence_class,
        )

        if self.technical_qc_state != "NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_SYNTHETIC_TECHNICAL_QC_PASS,
                f"technical_qc_state must remain 'NOT_OBSERVED', got {self.technical_qc_state!r}",
            )
        if self.visual_editorial_qc_state != "NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_SYNTHETIC_VISUAL_QC_PASS,
                f"visual_editorial_qc_state must remain 'NOT_OBSERVED', got {self.visual_editorial_qc_state!r}",
            )
        if self.audio_editorial_qc_state != "NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_SYNTHETIC_AUDIO_QC_PASS,
                f"audio_editorial_qc_state must remain 'NOT_OBSERVED', got {self.audio_editorial_qc_state!r}",
            )
        if self.overall_qc_gate_status != "BLOCKED_QC_NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_QC_BLOCKER_REMOVAL,
                f"overall_qc_gate_status must be 'BLOCKED_QC_NOT_OBSERVED', got {self.overall_qc_gate_status!r}",
            )

        if CANONICAL_QC_BLOCKER_CODE not in set(self.required_qc_blocker_codes):
            raise_mega15_error(
                REFUSAL_QC_BLOCKER_REMOVAL,
                f"Missing required QC blocker code: {CANONICAL_QC_BLOCKER_CODE!r}",
            )
        for code in self.required_qc_blocker_codes:
            if code not in CANONICAL_RELEASE_BLOCKER_CODES:
                raise_mega15_error(
                    REFUSAL_QC_BLOCKER_REMOVAL,
                    f"Unknown non-canonical QC blocker code: {code!r}",
                )

        if (
            not self.technical_qc_required_checks
            or not self.visual_editorial_qc_required_checks
            or not self.audio_editorial_qc_required_checks
        ):
            raise_mega15_error(
                "QC_REQUIREMENTS_EMPTY_CHECKS",
                "All required check lists must be non-empty",
            )

        expected_digest = canonical_sha256(self._digest_payload())
        if self.bundle_digest != expected_digest:
            raise_mega15_error(
                "QC_REQUIREMENTS_DIGEST_MISMATCH",
                f"bundle_digest mismatch: expected {expected_digest}, got {self.bundle_digest}",
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "QcRequirementsBundle":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                "QC_REQUIREMENTS_INVALID_PAYLOAD",
                "Payload must be a mapping",
            )
        raw_ctx = payload.get("synthetic_context")
        if not isinstance(raw_ctx, Mapping):
            raise_mega15_error(
                "QC_REQUIREMENTS_INVALID_SYNTHETIC_CONTEXT",
                "synthetic_context must be a mapping",
            )
        raw_t = payload.get("technical_qc_required_checks")
        raw_v = payload.get("visual_editorial_qc_required_checks")
        raw_a = payload.get("audio_editorial_qc_required_checks")
        raw_b = payload.get("required_qc_blocker_codes")
        if (
            not isinstance(raw_t, Sequence)
            or not isinstance(raw_v, Sequence)
            or not isinstance(raw_a, Sequence)
            or not isinstance(raw_b, Sequence)
        ):
            raise_mega15_error(
                "QC_REQUIREMENTS_INVALID_LISTS",
                "Required check and blocker fields must be sequences",
            )
        bundle = cls(
            schema_version=str(payload.get("schema_version", "")),
            kind=str(payload.get("kind", "")),
            bundle_id=str(payload.get("bundle_id", "")),
            render_specification_id=str(payload.get("render_specification_id", "")),
            render_specification_digest=str(
                payload.get("render_specification_digest", "")
            ),
            upstream_qc_readiness_packet_id=str(
                payload.get("upstream_qc_readiness_packet_id", "")
            ),
            upstream_qc_readiness_packet_digest=str(
                payload.get("upstream_qc_readiness_packet_digest", "")
            ),
            technical_qc_required_evidence_class=str(
                payload.get("technical_qc_required_evidence_class", "")
            ),
            visual_editorial_qc_required_evidence_class=str(
                payload.get("visual_editorial_qc_required_evidence_class", "")
            ),
            audio_editorial_qc_required_evidence_class=str(
                payload.get("audio_editorial_qc_required_evidence_class", "")
            ),
            technical_qc_required_checks=tuple(str(x) for x in raw_t),
            visual_editorial_qc_required_checks=tuple(str(x) for x in raw_v),
            audio_editorial_qc_required_checks=tuple(str(x) for x in raw_a),
            technical_qc_state=str(payload.get("technical_qc_state", "")),
            visual_editorial_qc_state=str(
                payload.get("visual_editorial_qc_state", "")
            ),
            audio_editorial_qc_state=str(
                payload.get("audio_editorial_qc_state", "")
            ),
            overall_qc_gate_status=str(payload.get("overall_qc_gate_status", "")),
            required_qc_blocker_codes=tuple(str(x) for x in raw_b),
            synthetic_context=parse_synthetic_context_dict(raw_ctx),
            bundle_digest=str(payload.get("bundle_digest", "")),
        )
        bundle.validate()
        return bundle


def build_qc_requirements_bundle(
    *,
    render_specification: RenderPreflightSpecification,
    qc_readiness_packet: ReadinessPacket,
    bundle_id: str = "qcreq_default",
    claim_technical_qc_pass: bool = False,
    claim_visual_qc_pass: bool = False,
    claim_audio_qc_pass: bool = False,
    technical_evidence_class: str = "MEASURED",
    visual_evidence_class: str = "VISUALLY_OBSERVED",
    audio_evidence_class: str = "AUDIO_OBSERVED",
) -> QcRequirementsBundle:
    """Build a verified offline `QcRequirementsBundle` from MEGA-16.1 + MEGA-13 QC readiness."""
    refuse_synthetic_qc_pass_or_class_confusion(
        claim_technical_qc_pass=claim_technical_qc_pass,
        claim_visual_qc_pass=claim_visual_qc_pass,
        claim_audio_qc_pass=claim_audio_qc_pass,
        technical_evidence_class=technical_evidence_class,
        visual_evidence_class=visual_evidence_class,
        audio_evidence_class=audio_evidence_class,
    )
    verify_render_preflight_specification(render_specification)

    if not isinstance(qc_readiness_packet, ReadinessPacket):
        raise_mega15_error(
            "QC_REQUIREMENTS_INVALID_READINESS_PACKET",
            "qc_readiness_packet must be a ReadinessPacket instance",
        )

    if (
        qc_readiness_packet.synthetic_only is not True
        or qc_readiness_packet.execution_authorized is not False
    ):
        raise_mega15_error(
            "REFUSAL_SYNTHETIC_TO_REAL_AUTHORITY_ESCALATION",
            "qc_readiness_packet must remain synthetic_only=True and execution_authorized=False",
        )

    details = qc_readiness_packet.details if isinstance(qc_readiness_packet.details, Mapping) else {}
    tech_ev = getattr(
        qc_readiness_packet,
        "technical_qc_state",
        details.get("technical_qc_evidence", "NOT_OBSERVED"),
    )
    vis_ev = getattr(
        qc_readiness_packet,
        "visual_editorial_qc_state",
        details.get("editorial_qc_evidence", "NOT_OBSERVED"),
    )
    aud_ev = getattr(
        qc_readiness_packet,
        "audio_editorial_qc_state",
        details.get("editorial_qc_evidence", "NOT_OBSERVED"),
    )

    if tech_ev != "NOT_OBSERVED":
        raise_mega15_error(
            REFUSAL_SYNTHETIC_TECHNICAL_QC_PASS,
            "Upstream ReadinessPacket technical QC evidence must be NOT_OBSERVED",
        )
    if vis_ev != "NOT_OBSERVED":
        raise_mega15_error(
            REFUSAL_SYNTHETIC_VISUAL_QC_PASS,
            "Upstream ReadinessPacket visual editorial QC evidence must be NOT_OBSERVED",
        )
    if aud_ev != "NOT_OBSERVED":
        raise_mega15_error(
            REFUSAL_SYNTHETIC_AUDIO_QC_PASS,
            "Upstream ReadinessPacket audio editorial QC evidence must be NOT_OBSERVED",
        )
    if (
        qc_readiness_packet.evidence_state != "NOT_OBSERVED"
        or qc_readiness_packet.stage_status != "NOT_READY_FOR_QC"
        or details.get("preview_eligible", False) is not False
        or details.get("production_export_authorized", False) is not False
    ):
        raise_mega15_error(
            REFUSAL_QC_BLOCKER_REMOVAL,
            "Upstream ReadinessPacket must remain NOT_READY_FOR_QC with NOT_OBSERVED evidence",
        )

    if CANONICAL_QC_BLOCKER_CODE not in set(qc_readiness_packet.blocker_codes):
        raise_mega15_error(
            REFUSAL_QC_BLOCKER_REMOVAL,
            f"Upstream ReadinessPacket missing required QC blocker {CANONICAL_QC_BLOCKER_CODE!r}",
        )

    packet_id = str(
        getattr(
            qc_readiness_packet,
            "packet_id",
            f"qcready_{qc_readiness_packet.stage_id}_{qc_readiness_packet.packet_digest[:12]}",
        )
    )

    syn_ctx = make_synthetic_context()
    provisional = QcRequirementsBundle(
        schema_version=QC_REQUIREMENTS_SCHEMA_VERSION,
        kind=QC_REQUIREMENTS_KIND,
        bundle_id=bundle_id,
        render_specification_id=render_specification.specification_id,
        render_specification_digest=render_specification.specification_digest,
        upstream_qc_readiness_packet_id=packet_id,
        upstream_qc_readiness_packet_digest=qc_readiness_packet.packet_digest,
        technical_qc_required_evidence_class="MEASURED",
        visual_editorial_qc_required_evidence_class="VISUALLY_OBSERVED",
        audio_editorial_qc_required_evidence_class="AUDIO_OBSERVED",
        technical_qc_required_checks=(
            "container_readable",
            "stream_presence_video",
            "duration_tolerance_ticks",
            "pts_monotonicity",
            "black_frame_detector",
            "silence_clipping_detector",
        ),
        visual_editorial_qc_required_checks=(
            "cut_boundary_visual_continuity",
            "choreography_phrase_completeness",
            "stage_framing_integrity",
        ),
        audio_editorial_qc_required_checks=(
            "musical_phrase_boundary_alignment",
            "transition_click_pop_absence",
            "av_sync_perceptual_verification",
        ),
        technical_qc_state="NOT_OBSERVED",
        visual_editorial_qc_state="NOT_OBSERVED",
        audio_editorial_qc_state="NOT_OBSERVED",
        overall_qc_gate_status="BLOCKED_QC_NOT_OBSERVED",
        required_qc_blocker_codes=(CANONICAL_QC_BLOCKER_CODE,),
        synthetic_context=syn_ctx,
        bundle_digest="",
    )
    digest = canonical_sha256(provisional._digest_payload())
    final_bundle = QcRequirementsBundle(
        **{**provisional.__dict__, "bundle_digest": digest}
    )
    final_bundle.validate()
    return final_bundle


def verify_qc_requirements_bundle(
    bundle: QcRequirementsBundle | Mapping[str, Any],
) -> QcRequirementsBundle:
    """Verify and return a `QcRequirementsBundle`."""
    if isinstance(bundle, QcRequirementsBundle):
        bundle.validate()
        return bundle
    return QcRequirementsBundle.from_dict(bundle)
