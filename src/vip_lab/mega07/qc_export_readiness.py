"""Packet P07c: Gate-3 Technical/Editorial QC & Production Export Refusal Guard.

Delegates to:
- ``gate3.qc.bare_pass_is_insufficient``, ``may_consume_for_binding_origin``
- ``vip_fvs.real_preview_receipt.FIXTURE_NOT_OBSERVED_REQUIRED``

Invariants enforced:
- Bare ``"PASS"`` QC status without structured technical and editorial QC checks
  is refused.
- Technical QC and Editorial QC remain distinct axes; passing Technical QC never
  auto-approves Editorial QC.
- Synthetic/fixture QC artifacts cannot be consumed for production binding.
- Production export is ALWAYS refused in synthetic lab mode
  (``production_export_authorized=False``, ``export_status="REFUSED_NOT_AUTHORIZED"``),
  even when non-production preview checks succeed.
"""

from __future__ import annotations

from typing import Any, Mapping

from gate3.qc import bare_pass_is_insufficient, may_consume_for_binding_origin
from vip_fvs.real_preview_receipt import FIXTURE_NOT_OBSERVED_REQUIRED

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-07.QC_EXPORT_READINESS"


def inspect_qc_export_readiness(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Evaluate Technical QC, Editorial QC, and refuse production export in synthetic lab."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "QC_EXPORT_NOT_MAPPING",
            "payload must be a mapping",
        )

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="QC_EXPORT_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted authority flags in QC/export payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    raw_qc = cleaned.get("qc_report")
    if isinstance(raw_qc, str) or raw_qc is None:
        if bare_pass_is_insufficient():
            code = "BARE_PASS_QC_INSUFFICIENT"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message="Bare 'PASS' string or missing structured QC report is insufficient",
                    field_path="qc_report",
                )
            )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "technical_qc_status": NOT_OBSERVED,
                "editorial_qc_status": NOT_OBSERVED,
                "production_export_authorized": False,
                "export_status": "REFUSED_NOT_AUTHORIZED",
            },
        )

    if not isinstance(raw_qc, Mapping):
        code = "QC_REPORT_INVALID_TYPE"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="qc_report must be a structured mapping",
                field_path="qc_report",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "production_export_authorized": False,
                "export_status": "REFUSED_NOT_AUTHORIZED",
            },
        )

    origin = str(raw_qc.get("origin", "SYNTHETIC_FIXTURE"))
    binding_consumable = may_consume_for_binding_origin(origin)
    tech_checks = raw_qc.get("technical_checks")
    ed_checks = raw_qc.get("editorial_checks")

    if not isinstance(tech_checks, Mapping) or len(tech_checks) == 0:
        code = "TECHNICAL_QC_CHECKS_MISSING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Structured technical_checks mapping is required",
                field_path="qc_report.technical_checks",
            )
        )
        tech_status = "BLOCKED"
    else:
        failed_tech = [k for k, v in tech_checks.items() if v is not True]
        if failed_tech:
            code = "TECHNICAL_QC_CHECK_FAILED"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=f"Technical QC checks failed: {sorted(failed_tech)}",
                    field_path="qc_report.technical_checks",
                )
            )
            tech_status = "FAILED"
        else:
            tech_status = "PASSED_SYNTHETIC"

    if not isinstance(ed_checks, Mapping) or len(ed_checks) == 0:
        code = "EDITORIAL_QC_CHECKS_MISSING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=(
                    "Structured editorial_checks mapping is required; Technical QC "
                    "never implies Editorial QC"
                ),
                field_path="qc_report.editorial_checks",
            )
        )
        ed_status = "NOT_OBSERVED"
    else:
        failed_ed = [k for k, v in ed_checks.items() if v is not True]
        if failed_ed:
            code = "EDITORIAL_QC_CHECK_FAILED"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=f"Editorial QC checks failed: {sorted(failed_ed)}",
                    field_path="qc_report.editorial_checks",
                )
            )
            ed_status = "FAILED"
        else:
            ed_status = "PASSED_SYNTHETIC"

    request_production_export = bool(cleaned.get("request_production_export", False))
    if request_production_export:
        code = "PRODUCTION_EXPORT_NOT_AUTHORIZED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message=(
                    "Production render/export requires separate owner authorization; "
                    "non-production preview or synthetic QC does not authorize export"
                ),
                field_path="request_production_export",
            )
        )
    else:
        reasons.append("PRODUCTION_EXPORT_NOT_AUTHORIZED")

    if not blockers:
        reasons.append("QC_SYNTHETIC_CHECKS_VALID_EXPORT_STILL_REFUSED")
        findings.append(
            ReadinessFinding(
                code="QC_SYNTHETIC_DUAL_AXIS_VERIFIED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Both Technical QC and Editorial QC synthetic checks verified; production export remains refused",
                details={
                    "origin": origin,
                    "binding_consumable": binding_consumable,
                    "fixture_not_observed_fields": list(FIXTURE_NOT_OBSERVED_REQUIRED),
                },
            )
        )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_AUTHORIZED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "origin": origin,
            "binding_consumable": binding_consumable,
            "technical_qc_status": tech_status,
            "editorial_qc_status": ed_status,
            "production_export_authorized": False,
            "export_status": "REFUSED_NOT_AUTHORIZED",
            "fixture_not_observed_fields": list(FIXTURE_NOT_OBSERVED_REQUIRED),
        },
    )
