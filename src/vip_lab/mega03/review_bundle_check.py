"""Packet P03c: ReviewBundle V1/V2/V3 compatibility and E01 binding eligibility checker.

Delegates directly to ``vip_fvs.review_bundle.ReviewBundle.from_record`` and
strictly separates:
1. Envelope & schema validity (``v1``, ``v2``, ``v3`` record_digest & dependency_digest)
2. Current E01 binding eligibility (``bundle.current_e01_validated``)

A valid envelope whose ``evidence_artifact_ref`` is missing or unverified has
``envelope_valid=True`` and ``current_e01_validated=False`` — never silently
upgraded to binding-eligible.
"""

from __future__ import annotations

from typing import Any, Mapping

from vip_fvs.review_bundle import (
    ReviewBundle,
    V1_SCHEMA_VERSION,
    V2_SCHEMA_VERSION,
    V3_SCHEMA_VERSION,
)

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-03.REVIEW_BUNDLE_CHECK"
SUPPORTED_BUNDLE_SCHEMAS = (
    V1_SCHEMA_VERSION,
    V2_SCHEMA_VERSION,
    V3_SCHEMA_VERSION,
)
_ENVELOPE_KEYS = frozenset(
    {"record_id", "record_type", "record_schema_version", "record_digest", "payload"}
)


def inspect_review_bundle_record(
    record: Mapping[str, Any],
    *,
    require_e01_binding: bool = False,
) -> ReadinessPacket:
    """Inspect a ReviewBundle v1/v2/v3 record and report envelope vs E01 binding status."""
    if not isinstance(record, Mapping):
        raise VipLabError(
            "REVIEW_BUNDLE_RECORD_NOT_MAPPING",
            "ReviewBundle record must be a mapping",
        )

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(record)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="REVIEW_BUNDLE_UNTRUSTED_FLAGS_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted top-level authority flags were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    envelope_candidate = {
        k: v for k, v in cleaned.items() if k not in untrusted_flags
    }

    try:
        bundle = ReviewBundle.from_record(envelope_candidate)
    except (ValueError, TypeError, KeyError) as exc:
        code = "REVIEW_BUNDLE_VALIDATION_FAILED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=str(exc),
                field_path="record",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "schema_version": envelope_candidate.get("record_schema_version"),
                "envelope_valid": False,
                "current_e01_validated": False,
                "binding_eligible": False,
            },
        )

    bundle_rec = bundle.to_record()
    schema_version = str(bundle_rec["record_schema_version"])
    bundle_id = str(bundle.payload["bundle_id"])

    findings.append(
        ReadinessFinding(
            code="REVIEW_BUNDLE_ENVELOPE_VERIFIED",
            status=ReadinessStatus.READY_SYNTHETIC,
            message=f"Verified {schema_version} envelope and digest chain",
            evidence_state="MEASURED",
            details={
                "schema_version": schema_version,
                "record_digest": bundle.record_digest,
                "dependency_digest": bundle.dependency_digest,
            },
        )
    )

    if bundle.current_e01_validated:
        reasons.append("REVIEW_BUNDLE_E01_BINDING_VALIDATED")
        findings.append(
            ReadinessFinding(
                code="REVIEW_BUNDLE_E01_BINDING_VALIDATED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Persisted E01 refinement artifact verified as binding-eligible",
                evidence_state="MEASURED",
            )
        )
        final_status = ReadinessStatus.READY_SYNTHETIC
        evidence_state = "MEASURED"
    else:
        reasons.append("REVIEW_BUNDLE_ENVELOPE_VALID_BUT_E01_UNVALIDATED")
        findings.append(
            ReadinessFinding(
                code="REVIEW_BUNDLE_E01_UNVALIDATED",
                status=(
                    ReadinessStatus.BLOCKED
                    if require_e01_binding
                    else ReadinessStatus.READY_SYNTHETIC
                ),
                message=(
                    "ReviewBundle envelope is structurally valid, but persisted E01 "
                    "refinement artifact is absent or not binding-eligible"
                ),
                evidence_state=NOT_OBSERVED,
            )
        )
        if require_e01_binding:
            blockers.append("REVIEW_BUNDLE_E01_UNVALIDATED")
            final_status = ReadinessStatus.BLOCKED
        else:
            final_status = ReadinessStatus.READY_SYNTHETIC
        evidence_state = NOT_OBSERVED

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        evidence_state=evidence_state,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "bundle_id": bundle_id,
            "schema_version": schema_version,
            "record_digest": bundle.record_digest,
            "dependency_digest": bundle.dependency_digest,
            "envelope_valid": True,
            "current_e01_validated": bundle.current_e01_validated,
            "binding_eligible": bundle.current_e01_validated,
            "supported_schemas": list(SUPPORTED_BUNDLE_SCHEMAS),
        },
    )
