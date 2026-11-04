"""Packet P06a: Gate-2 Synthetic Workload Plan Preflight.

Delegates directly to ``gate2.workload.WorkloadSpec`` and ``gate2.workload.generate``
to verify deterministic synthetic workload bounds, provenance SHAs, and
reproducible fixture digests without touching archive media.
"""

from __future__ import annotations

from typing import Any, Mapping

from gate2.workload import WorkloadError, WorkloadSpec, generate

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-06.WORKLOAD_PLAN"


def inspect_workload_plan(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Validate a Gate-2 synthetic workload specification and verify deterministic generation."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "WORKLOAD_PLAN_NOT_MAPPING",
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
                code="WORKLOAD_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted self-declared authority flags in workload plan were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    try:
        spec = WorkloadSpec(
            seed=cleaned.get("seed", 0),  # type: ignore[arg-type]
            jobs=cleaned.get("jobs", 0),  # type: ignore[arg-type]
            stages=cleaned.get("stages", 0),  # type: ignore[arg-type]
            artifact_bytes=cleaned.get("artifact_bytes", 0),  # type: ignore[arg-type]
            f01_sha=str(cleaned.get("f01_sha", "")),
            c04_sha=str(cleaned.get("c04_sha", "")),
            e05_sha=str(cleaned.get("e05_sha", "")),
            config_digest=str(cleaned.get("config_digest", "")),
        )
        fixture_a = generate(spec)
        fixture_b = generate(spec)
    except (WorkloadError, TypeError, ValueError) as exc:
        code = "WORKLOAD_SPEC_INVALID"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=str(exc),
                field_path="workload_spec",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "valid_spec": False,
                "deterministic": False,
                "fixture_digest": None,
            },
        )

    digest_a = fixture_a.fixture_digest()
    digest_b = fixture_b.fixture_digest()
    if digest_a != digest_b:
        code = "WORKLOAD_NONDETERMINISTIC_GENERATION"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Repeated generate(spec) produced different fixture digests",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"valid_spec": True, "deterministic": False},
        )

    total_steps = spec.jobs * spec.stages
    total_bytes = total_steps * spec.artifact_bytes
    reasons.append("WORKLOAD_SYNTHETIC_SPEC_DETERMINISTIC")
    findings.append(
        ReadinessFinding(
            code="WORKLOAD_FIXTURE_GENERATED",
            status=ReadinessStatus.READY_SYNTHETIC,
            message="Generated deterministic synthetic Gate-2 workload fixture",
            evidence_state="MEASURED",
            details={
                "fixture_digest": digest_a,
                "total_steps": total_steps,
                "total_bytes": total_bytes,
            },
        )
    )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=ReadinessStatus.READY_SYNTHETIC,
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=(),
        findings=tuple(findings),
        summary={
            "valid_spec": True,
            "deterministic": True,
            "fixture_digest": digest_a,
            "jobs": spec.jobs,
            "stages": spec.stages,
            "artifact_bytes": spec.artifact_bytes,
            "total_steps": total_steps,
            "total_bytes": total_bytes,
            "real_archive_workload_observed": False,
        },
    )
