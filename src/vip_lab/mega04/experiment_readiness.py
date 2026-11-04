"""Packet P04c: Gate-0 Experiment Entry Readiness & Config Freeze Preflight.

Combines:
1. ``gate0.config_freeze.inspect_freeze_readiness``
2. Packet P04a D2 intake readiness (``inspect_d2_readiness``)
3. Packet P04b query/gold/reviewer preflight (``inspect_query_review_preflight``)

Hard invariant: Even when all synthetic preflight components pass, Gate-0 remains
``freeze_state="NOT_FROZEN"``, ``authentic=False``, ``execution_authorized=False``,
``owner_approval_status="NOT_GRANTED"``, and ``gate_verdict="NOT_RUN"``.
"""

from __future__ import annotations

from typing import Any, Mapping

from gate0.config_freeze import inspect_freeze_readiness

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)
from .d2_readiness import inspect_d2_readiness
from .query_review_preflight import inspect_query_review_preflight


STAGE_ID = "MEGA-04.GATE0_EXPERIMENT_ENTRY"


def inspect_gate0_entry(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Evaluate complete synthetic Gate-0 experiment entry readiness."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "GATE0_ENTRY_NOT_MAPPING",
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
                code="GATE0_ENTRY_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted self-declared authority flags in Gate-0 entry payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    config_payload = cleaned.get("config")
    observed_digests = cleaned.get("observed_digests")
    d2_source = cleaned.get("d2_package")
    query_review_payload = cleaned.get("query_review")

    if not isinstance(config_payload, Mapping):
        code = "GATE0_CONFIG_MISSING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="config mapping is required for Gate-0 entry inspection",
                field_path="config",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            owner_approval_status="NOT_GRANTED",
            gate_verdict="NOT_RUN",
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "freeze_state": "NOT_FROZEN",
                "authentic": False,
                "execution_authorized": False,
                "gate_verdict": "NOT_RUN",
            },
        )

    # Always force execution_authorized=False in synthetic lab context
    try:
        freeze_report = inspect_freeze_readiness(
            dict(config_payload),
            observed_digests=(
                dict(observed_digests)
                if isinstance(observed_digests, Mapping)
                else None
            ),
            execution_authorized=False,
        )
    except ValueError as exc:
        code = "GATE0_CONFIG_FREEZE_SCHEMA_ERROR"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=str(exc),
                field_path="config",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            owner_approval_status="NOT_GRANTED",
            gate_verdict="NOT_RUN",
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "freeze_state": "NOT_FROZEN",
                "authentic": False,
                "execution_authorized": False,
                "gate_verdict": "NOT_RUN",
            },
        )

    freeze_blockers = list(freeze_report.get("blockers", ()))
    non_auth_freeze_blockers = [
        b
        for b in freeze_blockers
        if b
        not in (
            "EXECUTION_NOT_AUTHORIZED",
            "REAL_ARCHIVE_NOT_OBSERVED",
        )
    ]
    if non_auth_freeze_blockers:
        for b_code in non_auth_freeze_blockers:
            reasons.append(b_code)
            blockers.append(b_code)
            findings.append(
                ReadinessFinding(
                    code=b_code,
                    status=ReadinessStatus.BLOCKED,
                    message=f"Config freeze readiness blocker: {b_code}",
                    field_path="config",
                )
            )
    else:
        findings.append(
            ReadinessFinding(
                code="GATE0_CONFIG_DIGEST_COMPUTED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Gate-0 config schema and digest verified (remains NOT_FROZEN in synthetic lab)",
                details={
                    "config_digest": freeze_report.get("config_digest"),
                    "freeze_state": freeze_report.get("freeze_state"),
                },
            )
        )

    d2_summary: dict[str, Any] | None = None
    if d2_source is not None:
        d2_pkt = inspect_d2_readiness(d2_source)
        d2_summary = dict(d2_pkt.summary)
        if d2_pkt.status != ReadinessStatus.READY_SYNTHETIC:
            for b in d2_pkt.blockers:
                reasons.append(f"D2:{b}")
                blockers.append(f"D2:{b}")
            findings.append(
                ReadinessFinding(
                    code="GATE0_D2_NOT_READY",
                    status=d2_pkt.status,
                    message="D2 readiness check reported blockers",
                    field_path="d2_package",
                    details={"d2_blockers": list(d2_pkt.blockers)},
                )
            )
        else:
            findings.append(
                ReadinessFinding(
                    code="GATE0_D2_SYNTHETIC_VALID",
                    status=ReadinessStatus.READY_SYNTHETIC,
                    message="D2 synthetic package passed structural intake (execution_authorized=False)",
                    details={"package_digest": d2_pkt.summary.get("package_digest")},
                )
            )

    qr_summary: dict[str, Any] | None = None
    if isinstance(query_review_payload, Mapping):
        qr_pkt = inspect_query_review_preflight(query_review_payload)
        qr_summary = dict(qr_pkt.summary)
        if qr_pkt.status != ReadinessStatus.READY_SYNTHETIC:
            for b in qr_pkt.blockers:
                reasons.append(f"QUERY_REVIEW:{b}")
                blockers.append(f"QUERY_REVIEW:{b}")
            findings.append(
                ReadinessFinding(
                    code="GATE0_QUERY_REVIEW_NOT_READY",
                    status=qr_pkt.status,
                    message="Query/gold/reviewer preflight reported blockers",
                    field_path="query_review",
                    details={"query_review_blockers": list(qr_pkt.blockers)},
                )
            )
        else:
            findings.append(
                ReadinessFinding(
                    code="GATE0_QUERY_REVIEW_SYNTHETIC_VALID",
                    status=ReadinessStatus.READY_SYNTHETIC,
                    message="Query split, gold events, and reviewer envelope passed synthetic preflight",
                )
            )

    reasons.append("REAL_EXPERIMENT_EXECUTION_NOT_AUTHORIZED")
    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("GATE0_SYNTHETIC_ENTRY_PREFLIGHT_READY")

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_RUN",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "config_digest": freeze_report.get("config_digest"),
            "freeze_state": freeze_report.get("freeze_state", "NOT_FROZEN"),
            "authentic": False,
            "execution_authorized": False,
            "approval": "NOT_GRANTED",
            "gate_verdict": "NOT_RUN",
            "freeze_blockers": freeze_blockers,
            "d2": d2_summary,
            "query_review": qr_summary,
        },
    )
