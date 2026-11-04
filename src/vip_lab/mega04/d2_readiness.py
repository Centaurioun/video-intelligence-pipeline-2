"""Packet P04a: Gate-0 D2 Intake & Readiness Preflight.

Delegates directly to ``gate0.d2_intake`` (``evaluate_d2_package``, ``D2_FIELDS``,
``D2_FIELD_IDS``, ``D2_BASELINE_STATES``) and guarantees that synthetic or
unauthenticated D2 packages never claim owner approval, never promote fields to
``VERIFIED``, and never authorize D3/Gate-0 real archive execution.
"""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any, Mapping

from gate0.d2_intake import (
    ATTESTATION_DECLARED,
    ATTESTATION_SYNTHETIC,
    D2_BASELINE_STATES,
    D2_FIELDS,
    D2_FIELD_IDS,
    D2IntakeError,
    STATE_BLOCKED,
    STATE_NOT_OBSERVED,
    STATE_PENDING,
    STATE_VERIFIED,
    evaluate_d2_package,
)

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    canonical_json_dumps,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-04.D2_READINESS"


def _write_temp_d2_package(root: Path, payload: Mapping[str, Any]) -> Path:
    pkg_dir = root / "d2_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    attestation = payload.get("attestation")
    fields = payload.get("fields")
    evidence_files = payload.get("evidence_files", {})
    if not isinstance(attestation, Mapping) or not isinstance(fields, Mapping):
        raise VipLabError(
            "D2_MEMORY_PACKAGE_INVALID",
            "In-memory D2 payload must provide 'attestation' and 'fields' mappings",
        )
    (pkg_dir / "owner-attestation.json").write_text(
        canonical_json_dumps(dict(attestation)),
        encoding="utf-8",
    )
    (pkg_dir / "d2-fields.json").write_text(
        canonical_json_dumps(dict(fields)),
        encoding="utf-8",
    )
    if isinstance(evidence_files, Mapping):
        for rel_name, content in evidence_files.items():
            if not isinstance(rel_name, str) or "/" in rel_name or "\\" in rel_name or rel_name in ("", ".", ".."):
                raise VipLabError(
                    "D2_EVIDENCE_FILENAME_INVALID",
                    f"Invalid evidence filename {rel_name!r}",
                )
            target = pkg_dir / rel_name
            if isinstance(content, Mapping):
                target.write_text(canonical_json_dumps(dict(content)), encoding="utf-8")
            elif isinstance(content, str):
                target.write_text(content, encoding="utf-8")
            else:
                raise VipLabError(
                    "D2_EVIDENCE_CONTENT_INVALID",
                    f"Evidence content for {rel_name!r} must be mapping or str",
                )
    return pkg_dir


def inspect_d2_readiness(
    source: str | Path | Mapping[str, Any],
) -> ReadinessPacket:
    """Evaluate Gate-0 D2 intake readiness from a directory path or in-memory mapping."""
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    untrusted_flags: tuple[str, ...] = ()
    package_dir: Path | None = None

    if isinstance(source, (str, Path)):
        package_dir = Path(source)
    elif isinstance(source, Mapping):
        cleaned, untrusted_flags = sanitize_untrusted_authority_claims(source)
        if untrusted_flags:
            reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
            findings.append(
                ReadinessFinding(
                    code="D2_UNTRUSTED_AUTHORITY_STRIPPED",
                    status=ReadinessStatus.NOT_AUTHORIZED,
                    message="Untrusted self-declared authority flags in D2 payload were ignored",
                    details={"ignored_keys": list(untrusted_flags)},
                )
            )
        if "package_dir" in cleaned and cleaned["package_dir"] is not None:
            package_dir = Path(str(cleaned["package_dir"]))
    else:
        raise VipLabError(
            "D2_SOURCE_INVALID_TYPE",
            "inspect_d2_readiness expects a directory path or mapping",
        )

    try:
        if package_dir is not None:
            report = evaluate_d2_package(package_dir)
        else:
            with tempfile.TemporaryDirectory(prefix="vip_lab_d2_") as tmp_dir:
                temp_pkg_dir = _write_temp_d2_package(Path(tmp_dir), cleaned)
                report = evaluate_d2_package(temp_pkg_dir)
    except (D2IntakeError, VipLabError) as exc:
        code = exc.code if isinstance(exc, VipLabError) else "D2_PACKAGE_INTAKE_ERROR"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=str(exc),
                field_path="d2_package",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            owner_approval_status="NOT_GRANTED",
            gate_verdict="NOT_AUTHORIZED",
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "expected_field_ids": list(D2_FIELD_IDS),
                "baseline_states": dict(D2_BASELINE_STATES),
                "field_count": len(D2_FIELDS),
                "verified_count": 0,
                "execution_authorized": False,
                "owner_approval_claimed": False,
                "d3_status": "NOT_AUTHORIZED",
            },
        )

    report_dict = report.as_dict()
    field_states: dict[str, str] = {}
    verified_count = 0
    blocked_fields: list[str] = []

    for row in report.fields:
        field_states[row.field_id] = row.resulting_state
        if row.resulting_state == STATE_VERIFIED:
            verified_count += 1
        if row.resulting_state == STATE_BLOCKED or not row.passed:
            blocked_fields.append(row.field_id)
            blockers.append(f"{row.field_id}:{row.reason_code}")
        findings.append(
            ReadinessFinding(
                code=row.reason_code,
                status=(
                    ReadinessStatus.BLOCKED
                    if not row.passed
                    else ReadinessStatus.READY_SYNTHETIC
                ),
                message=f"{row.field_id} ({row.name}): {row.resulting_state} ({row.reason_code})",
                field_path=f"fields.{row.field_id}",
                evidence_state=NOT_OBSERVED,
                details={
                    "baseline_state": row.baseline_state,
                    "resulting_state": row.resulting_state,
                    "passed": row.passed,
                },
            )
        )

    # Hard invariant: evaluate_d2_package never promotes any field to VERIFIED
    # without cryptographic owner authentication, and never sets execution_authorized=True.
    if verified_count > 0 or report.execution_authorized or report.owner_approval_claimed:
        raise VipLabError(
            "D2_INVARIANT_VIOLATION",
            "Unauthenticated D2 evaluation unexpectedly claimed VERIFIED or execution_authorized",
        )

    reasons.extend(report.reasons)
    if blocked_fields:
        final_status = ReadinessStatus.BLOCKED
        reasons.append("D2_FIELDS_INCOMPLETE_OR_INVALID")
    elif report.attestation_classification in (
        ATTESTATION_SYNTHETIC,
        ATTESTATION_DECLARED,
    ):
        final_status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("D2_SYNTHETIC_INTAKE_STRUCTURALLY_VALID_NOT_AUTHORIZED")
    else:
        final_status = ReadinessStatus.BLOCKED
        blockers.append("D2_ATTESTATION_REJECTED")

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
            "package_digest": report.package_digest,
            "attestation_classification": report.attestation_classification,
            "authenticity": report.authenticity,
            "field_states": field_states,
            "verified_count": verified_count,
            "blocked_fields": blocked_fields,
            "pending_count": sum(
                1 for s in field_states.values() if s == STATE_PENDING
            ),
            "not_observed_count": sum(
                1 for s in field_states.values() if s == STATE_NOT_OBSERVED
            ),
            "owner_approval_claimed": report.owner_approval_claimed,
            "execution_authorized": report.execution_authorized,
            "d3_status": report.d3_status,
            "report": report_dict,
        },
    )
