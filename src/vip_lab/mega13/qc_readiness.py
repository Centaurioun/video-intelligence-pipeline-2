"""QC evidence completeness and production export refusal evaluator for MEGA-13."""

from __future__ import annotations

from typing import Any, Mapping

from gate3.qc import bare_pass_is_insufficient
from vip_fvs.real_preview_receipt import FIXTURE_NOT_OBSERVED_REQUIRED
from vip_lab.common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)
from vip_lab.mega13.lineage_audit import audit_cross_stage_lineage

STAGE_ID = "MEGA-13.QC_EVIDENCE_AND_EXPORT_REFUSAL"


def evaluate_qc_readiness(payload: Mapping[str, Any]) -> ReadinessPacket:
    if not isinstance(payload, Mapping):
        raise VipLabError("QC_READINESS_NOT_MAPPING", "payload must be a mapping")

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="UNTRUSTED_AUTHORITY_CLAIM",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message=f"Rejected untrusted authority keys: {', '.join(untrusted_flags)}",
                evidence_state=NOT_OBSERVED,
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    claimed_evidence = cleaned.get("claimed_evidence_class")
    if (
        claimed_evidence in ("VISUALLY_OBSERVED", "AUDIO_OBSERVED")
        or cleaned.get("technical_qc_evidence") in ("VISUALLY_OBSERVED", "AUDIO_OBSERVED")
        or cleaned.get("editorial_qc_evidence") in ("VISUALLY_OBSERVED", "AUDIO_OBSERVED")
    ):
        code = "FORGED_SENSORY_OBSERVATION_REFUSED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Unrendered synthetic laboratory artifacts cannot claim VISUALLY_OBSERVED or AUDIO_OBSERVED evidence.",
                evidence_state=NOT_OBSERVED,
            )
        )

    if bool(cleaned.get("request_production_export", False)) or bool(
        cleaned.get("authorize_production_export", False)
    ):
        code = "PRODUCTION_EXPORT_NOT_AUTHORIZED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Production export is strictly refused in synthetic laboratory mode.",
                evidence_state=NOT_OBSERVED,
            )
        )

    qc_record = cleaned.get("qc_record")
    if qc_record is not None:
        if isinstance(qc_record, str):
            synth_rec = {"edit_qc_status": qc_record}
            if bare_pass_is_insufficient(synth_rec):
                code = "BARE_PASS_QC_INSUFFICIENT"
                reasons.append(code)
                blockers.append(code)
                findings.append(
                    ReadinessFinding(
                        code=code,
                        status=ReadinessStatus.BLOCKED,
                        message="Bare 'PASS' string without structured QC scope and supporting evidence is refused.",
                        evidence_state=NOT_OBSERVED,
                    )
                )
        elif isinstance(qc_record, Mapping):
            if bare_pass_is_insufficient(qc_record):
                code = "BARE_PASS_QC_INSUFFICIENT"
                reasons.append(code)
                blockers.append(code)
                findings.append(
                    ReadinessFinding(
                        code=code,
                        status=ReadinessStatus.BLOCKED,
                        message="QC record with bare edit_qc_status='PASS' is insufficient.",
                        evidence_state=NOT_OBSERVED,
                    )
                )
        else:
            code = "INVALID_QC_RECORD_TYPE"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message="qc_record must be a mapping or None.",
                    evidence_state=NOT_OBSERVED,
                )
            )

    q_raw = cleaned.get("candidate_queue")
    t_raw = cleaned.get("temporal_request")
    p_raw = cleaned.get("editorial_proposal")
    chain_raw = cleaned.get("proposal_revision_chain")
    replay_raw = cleaned.get("replay_graph")

    lineage_receipt_dict: dict[str, Any] | None = None
    if not isinstance(q_raw, Mapping) or not isinstance(t_raw, Mapping) or not isinstance(p_raw, Mapping):
        code = "MISSING_UPSTREAM_LINEAGE_ARTIFACTS"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="candidate_queue, temporal_request, and editorial_proposal mappings are required.",
                evidence_state=NOT_OBSERVED,
            )
        )
    else:
        try:
            receipt = audit_cross_stage_lineage(
                candidate_queue=q_raw,
                temporal_request=t_raw,
                editorial_proposal=p_raw,
                proposal_revision_chain=chain_raw if isinstance(chain_raw, list) else None,
                replay_graph=replay_raw if isinstance(replay_raw, Mapping) else None,
            )
            lineage_receipt_dict = receipt.to_dict()
        except VipLabError as exc:
            reasons.append(exc.code)
            blockers.append(exc.code)
            findings.append(
                ReadinessFinding(
                    code=exc.code,
                    status=ReadinessStatus.BLOCKED,
                    message=exc.message,
                    evidence_state=NOT_OBSERVED,
                    details=dict(exc.details),
                )
            )

    has_refusal = any(
        f.code in ("FORGED_SENSORY_OBSERVATION_REFUSED", "PRODUCTION_EXPORT_NOT_AUTHORIZED")
        for f in findings
    )
    has_invalid = any(f.status == ReadinessStatus.INVALID for f in findings)

    if has_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif has_invalid:
        status = ReadinessStatus.INVALID
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("QC_NOT_OBSERVED_AND_EXPORT_REFUSAL_VERIFIED")
        findings.append(
            ReadinessFinding(
                code="QC_NOT_OBSERVED_AND_EXPORT_REFUSAL_VERIFIED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Cross-stage lineage verified; QC evidence remains NOT_OBSERVED and production export remains refused.",
                evidence_state=NOT_OBSERVED,
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=status,
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "lineage_receipt": lineage_receipt_dict,
            "qc_state": NOT_OBSERVED,
            "technical_qc_evidence": NOT_OBSERVED,
            "editorial_qc_evidence": NOT_OBSERVED,
            "fixture_not_observed_fields": list(FIXTURE_NOT_OBSERVED_REQUIRED),
            "preview_eligible": False,
            "production_export_authorized": False,
            "export_status": "REFUSED_NOT_AUTHORIZED",
        },
    )
