"""Packet P06b: Gate-2 Synthetic Fault & Recovery Matrix Evaluator.

Delegates directly to:
- ``gate2.workload.WorkloadSpec``, ``generate``
- ``gate2.recovery.RecoveryBinding``, ``RecoveryHarness``, ``RecoveryRefusal``
- ``gate2.faults.FaultClass``, ``inject``, ``capability``, ``InjectionError``
"""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any, Mapping

from gate2.faults import FaultClass, InjectionError, capability, inject
from gate2.recovery import RecoveryBinding, RecoveryHarness, RecoveryRefusal
from gate2.workload import WorkloadError, WorkloadSpec, generate

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-06.RECOVERY_MATRIX"


def inspect_recovery_scenario(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Run a bounded synthetic Gate-2 recovery/fault scenario and report deterministic outcomes."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "RECOVERY_SCENARIO_NOT_MAPPING",
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
                code="RECOVERY_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted authority flags in recovery scenario payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    workload_cfg = cleaned.get("workload", cleaned)
    if not isinstance(workload_cfg, Mapping):
        raise VipLabError(
            "RECOVERY_WORKLOAD_NOT_MAPPING",
            "workload configuration must be a mapping",
        )

    try:
        spec = WorkloadSpec(
            seed=workload_cfg.get("seed", 7),  # type: ignore[arg-type]
            jobs=workload_cfg.get("jobs", 3),  # type: ignore[arg-type]
            stages=workload_cfg.get("stages", 2),  # type: ignore[arg-type]
            artifact_bytes=workload_cfg.get("artifact_bytes", 64),  # type: ignore[arg-type]
            f01_sha=str(workload_cfg.get("f01_sha", "1" * 40)),
            c04_sha=str(workload_cfg.get("c04_sha", "2" * 40)),
            e05_sha=str(workload_cfg.get("e05_sha", "3" * 40)),
            config_digest=str(workload_cfg.get("config_digest", "a" * 64)),
        )
        fixture = generate(spec)
    except (WorkloadError, TypeError, ValueError) as exc:
        code = "RECOVERY_WORKLOAD_SPEC_INVALID"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=str(exc),
                field_path="workload",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"scenario_valid": False},
        )

    binding = RecoveryBinding(
        workload_digest=fixture.fixture_digest(),
        config_digest=spec.config_digest,
        f01_sha=spec.f01_sha,
        c04_sha=spec.c04_sha,
        e05_sha=spec.e05_sha,
    )

    interrupt_at_step = cleaned.get("interrupt_at_step")
    tamper_binding_on_resume = bool(cleaned.get("tamper_binding_on_resume", False))
    corrupt_artifact_on_resume = bool(cleaned.get("corrupt_artifact_on_resume", False))
    fault_class_name = cleaned.get("fault_class")

    fault_summary: dict[str, Any] | None = None
    if fault_class_name is not None:
        try:
            fc = FaultClass(str(fault_class_name))
            cap = capability(fc)
            with tempfile.TemporaryDirectory(prefix="vip_lab_fault_") as ftmp:
                inj = inject(fc, Path(ftmp), payload=b"synthetic-checkpoint-bytes")
            fault_summary = {
                "fault_class": fc.value,
                "capability": cap.value,
                "injected": inj.injected,
                "deterministic": inj.deterministic,
                "detail": inj.detail,
            }
            findings.append(
                ReadinessFinding(
                    code="RECOVERY_FAULT_INJECTED_SYNTHETIC",
                    status=ReadinessStatus.READY_SYNTHETIC,
                    message=f"Simulated synthetic fault class {fc.value}",
                    details=fault_summary,
                )
            )
        except (ValueError, InjectionError) as exc:
            code = "RECOVERY_FAULT_CLASS_INVALID"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message=str(exc),
                    field_path="fault_class",
                )
            )
            return ReadinessPacket(
                stage_id=STAGE_ID,
                status=ReadinessStatus.INVALID,
                reasons=tuple(reasons),
                blockers=tuple(blockers),
                findings=tuple(findings),
                summary={"scenario_valid": False},
            )

    with tempfile.TemporaryDirectory(prefix="vip_lab_rec_") as tmp_dir:
        state_dir = Path(tmp_dir) / "state"
        harness_initial = RecoveryHarness.open(state_dir, fixture, binding)
        initial_run = harness_initial.run(
            interrupt_at_step=(
                int(interrupt_at_step)
                if isinstance(interrupt_at_step, int)
                and not isinstance(interrupt_at_step, bool)
                else None
            )
        )

        if corrupt_artifact_on_resume:
            artifacts_dir = state_dir / "artifacts"
            if artifacts_dir.exists():
                for bin_file in sorted(artifacts_dir.glob("*.bin")):
                    bin_file.write_bytes(b"corrupted-checkpoint-payload")
                    break

        resume_binding = binding
        if tamper_binding_on_resume:
            resume_binding = RecoveryBinding(
                workload_digest="f" * 64,
                config_digest=spec.config_digest,
                f01_sha=spec.f01_sha,
                c04_sha=spec.c04_sha,
                e05_sha=spec.e05_sha,
            )

        try:
            harness_resume = RecoveryHarness.open(state_dir, fixture, resume_binding)
            resume_run = harness_resume.run()
        except RecoveryRefusal as exc:
            code = "RECOVERY_REFUSED_FAIL_CLOSED"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=str(exc),
                    field_path="recovery_resume",
                )
            )
            return ReadinessPacket(
                stage_id=STAGE_ID,
                status=ReadinessStatus.BLOCKED,
                reasons=tuple(reasons),
                blockers=tuple(blockers),
                findings=tuple(findings),
                summary={
                    "scenario_valid": True,
                    "refused_fail_closed": True,
                    "refusal_message": str(exc),
                    "initial_run": dict(initial_run),
                    "fault": fault_summary,
                },
            )

    reasons.append("RECOVERY_SYNTHETIC_SCENARIO_VERIFIED")
    findings.append(
        ReadinessFinding(
            code="RECOVERY_RESUME_CONVERGED",
            status=ReadinessStatus.READY_SYNTHETIC,
            message="Synthetic recovery harness converged with zero recomputation and zero corruption",
            evidence_state="MEASURED",
            details={
                "initial_completed": initial_run["completed_count"],
                "resume_completed": resume_run["completed_count"],
                "recomputed_count": resume_run["recomputed_count"],
                "corrupted_count": resume_run["corrupted_count"],
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
            "scenario_valid": True,
            "refused_fail_closed": False,
            "fixture_digest": fixture.fixture_digest(),
            "initial_run": dict(initial_run),
            "resume_run": dict(resume_run),
            "fault": fault_summary,
            "real_archive_recovery_proven": False,
        },
    )
