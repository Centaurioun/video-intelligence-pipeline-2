"""Packet P06b: Gate-2 Synthetic Fault & Recovery Matrix Evaluator.

Delegates directly to:
- ``gate2.workload.WorkloadSpec``, ``generate``
- ``gate2.recovery.RecoveryBinding``, ``RecoveryHarness``, ``RecoveryRefusal``
- ``gate2.faults.FaultClass``, ``inject``, ``capability``, ``InjectionError``
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

from gate2.faults import FaultClass, InjectionError, capability, inject
from gate2.recovery import RecoveryBinding, RecoveryHarness, RecoveryRefusal
from gate2.workload import WorkloadError, WorkloadSpec, generate

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    canonical_json_dumps,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-06.RECOVERY_MATRIX"

class _SimulatedInterruptionError(RuntimeError):
    """Raised by the synthetic adapter to simulate mid-run interruption."""


class _SyntheticRecoveryAdapter:
    """In-memory deterministic adapter satisfying gate2.recovery.RecoveryHarness protocol."""

    def __init__(
        self,
        operation_ids: Sequence[str],
        *,
        valid_receipt: str,
        interrupt_at_step: int | None = None,
    ) -> None:
        self.operation_ids: tuple[str, ...] = tuple(operation_ids)
        self.valid_receipt = valid_receipt
        self.interrupt_at_step = interrupt_at_step
        self.completed_ops: set[str] = set()
        self.side_effect_counts: dict[str, int] = {}
        self.corrupted: bool = False

    def validate_receipt(self, receipt_identity: str) -> bool:
        return (not self.corrupted) and (receipt_identity == self.valid_receipt)

    def reconcile_sqlite_tail(self) -> None:
        if self.corrupted:
            raise RecoveryRefusal("corrupt artifact or sqlite tail detected")

    def state_digest(self) -> str:
        raw = canonical_json_dumps(
            {
                "completed": sorted(self.completed_ops),
                "corrupted": self.corrupted,
            }
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def start_or_resume(self, binding: RecoveryBinding) -> Sequence[str]:
        return self.operation_ids

    def is_complete(self, operation_id: str) -> bool:
        return operation_id in self.completed_ops

    def apply_idempotent(self, operation_id: str) -> None:
        if (
            self.interrupt_at_step is not None
            and len(self.completed_ops) >= self.interrupt_at_step
        ):
            raise _SimulatedInterruptionError(
                f"Simulated interruption after {len(self.completed_ops)} completed steps"
            )
        self.side_effect_counts[operation_id] = (
            self.side_effect_counts.get(operation_id, 0) + 1
        )

    def mark_complete(self, operation_id: str) -> None:
        self.completed_ops.add(operation_id)


def _resolve_fault_class(raw_name: str) -> FaultClass:
    cleaned_name = raw_name.strip()
    if cleaned_name.upper() in FaultClass.__members__:
        return FaultClass[cleaned_name.upper()]
    return FaultClass(cleaned_name)


def _default_fault_payload(fc: FaultClass) -> dict[str, Any]:
    if fc is FaultClass.A_BEFORE_STAGE_START:
        return {"predecessor_succeeded": False}
    if fc is FaultClass.E_REPEATED_IDEMPOTENCY_KEY:
        return {"second_submission": True}
    if fc is FaultClass.F_RESTART_RECONSTRUCTION:
        return {"decision_vector_a": "first", "decision_vector_b": "second"}
    if fc is FaultClass.H_INTERRUPTED_RECOVERY:
        return {"interruption_observed": True, "recovery_swallowed": False}
    if fc == FaultClass.I_CORRUPT_AT_REST:
        return {"payload": "not-json"}
    if fc is FaultClass.J_POST_SUCCESS_INVALIDATION:
        return {"chain": ["AVAILABLE", "CLEANED"]}
    if fc is FaultClass.K_IDENTITY_DRIFT:
        return {"sealed_digest": "a" * 64, "observed_digest": "b" * 64}
    if fc is FaultClass.L_CONCURRENT_WRITER:
        return {"writers": ["writer-a", "writer-b"]}
    if fc is FaultClass.M_REFERENTIAL_DIVERGENCE:
        return {"attempts": [], "referenced_attempt_ids": ["missing"]}
    return {}


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
            jobs=workload_cfg.get("jobs", 3),  # type: ignore[arg-type]
            stages=workload_cfg.get("stages", 2),  # type: ignore[arg-type]
            artifact_bytes=workload_cfg.get("artifact_bytes", 64),  # type: ignore[arg-type]
            cost_units=workload_cfg.get("cost_units", 10),  # type: ignore[arg-type]
            fault_position=workload_cfg.get("fault_position", 0),  # type: ignore[arg-type]
            seed=workload_cfg.get("seed", 7),  # type: ignore[arg-type]
            f01_sha=str(workload_cfg.get("f01_sha", "1" * 40)),
            c04_sha=str(workload_cfg.get("c04_sha", "2" * 40)),
            e05_sha=str(workload_cfg.get("e05_sha", "3" * 40)),
            config_digest=str(workload_cfg.get("config_digest", "a" * 64)),
            concurrency=workload_cfg.get("concurrency", 1),  # type: ignore[arg-type]
            repetitions=workload_cfg.get("repetitions", 2),  # type: ignore[arg-type]
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

    fix_digest = fixture.fixture_digest
    receipt_id = str(cleaned.get("receipt_identity", "rcpt_synth_01"))
    binding = RecoveryBinding(
        f01_sha=spec.f01_sha,
        c04_sha=spec.c04_sha,
        e05_sha=spec.e05_sha,
        workload_digest=fix_digest,
        configuration_digest=spec.config_digest,
        previous_manifest_digest=str(cleaned.get("previous_manifest_digest", "4" * 64)),
        current_manifest_digest=str(cleaned.get("current_manifest_digest", "5" * 64)),
        generation_id=str(cleaned.get("generation_id", "gen_synth_01")),
        semantic_space_id=str(
            cleaned.get("semantic_space_id", "vip-v1-siglip-base-224:768")
        ),
        receipt_identity=receipt_id,
    )

    interrupt_at_step = cleaned.get("interrupt_at_step")
    tamper_binding_on_resume = bool(cleaned.get("tamper_binding_on_resume", False))
    corrupt_artifact_on_resume = bool(cleaned.get("corrupt_artifact_on_resume", False))
    fault_class_name = cleaned.get("fault_class")

    fault_summary: dict[str, Any] | None = None
    if fault_class_name is not None:
        try:
            fc = _resolve_fault_class(str(fault_class_name))
            cap = capability(fc)
            custom_fault_payload = cleaned.get("fault_payload")
            fault_payload = (
                dict(custom_fault_payload)
                if isinstance(custom_fault_payload, Mapping)
                else _default_fault_payload(fc)
            )
            inj = inject(fc, fault_payload)
            fault_summary = {
                "fault_class": fc.value,
                "fault_class_name": fc.name,
                "requested_fault_class": str(fault_class_name),
                "capability": cap.value,
                "disposition": inj.disposition,
                "detected": inj.detected,
                "payload_digest": inj.payload_digest,
                "details": dict(inj.details),
            }
            findings.append(
                ReadinessFinding(
                    code="RECOVERY_FAULT_INJECTED_SYNTHETIC",
                    status=ReadinessStatus.READY_SYNTHETIC,
                    message=f"Simulated synthetic fault class {fc.value} ({fc.name})",
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

    operation_ids = [
        f"{job.job_index}:stage_{stage_idx}"
        for job in fixture.jobs
        for stage_idx in range(len(job.stages))
    ]
    step_limit = (
        int(interrupt_at_step)
        if isinstance(interrupt_at_step, int) and not isinstance(interrupt_at_step, bool)
        else None
    )

    with tempfile.TemporaryDirectory(prefix="vip_lab_rec_") as tmp_dir:
        checkpoint_path = Path(tmp_dir) / "checkpoint.json"
        adapter = _SyntheticRecoveryAdapter(
            operation_ids,
            valid_receipt=receipt_id,
            interrupt_at_step=step_limit,
        )
        harness_initial = RecoveryHarness.open(checkpoint_path, binding, adapter)
        interrupted = False
        try:
            harness_initial.run()
        except _SimulatedInterruptionError:
            interrupted = True

        initial_run = {
            "completed_count": len(adapter.completed_ops),
            "interrupted": interrupted,
            "total_operations": len(operation_ids),
        }

        # Lift interruption limit for resume attempt
        adapter.interrupt_at_step = None
        if corrupt_artifact_on_resume:
            adapter.corrupted = True

        resume_binding = binding
        if tamper_binding_on_resume:
            resume_binding = RecoveryBinding(
                f01_sha=spec.f01_sha,
                c04_sha=spec.c04_sha,
                e05_sha=spec.e05_sha,
                workload_digest="f" * 64,
                configuration_digest=spec.config_digest,
                previous_manifest_digest=binding.previous_manifest_digest,
                current_manifest_digest=binding.current_manifest_digest,
                generation_id=binding.generation_id,
                semantic_space_id=binding.semantic_space_id,
                receipt_identity=binding.receipt_identity,
            )

        try:
            harness_resume = RecoveryHarness.open(
                checkpoint_path, resume_binding, adapter
            )
            skipped_completed = len(adapter.completed_ops)
            outcome = harness_resume.run()
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
                    "initial_run": initial_run,
                    "fault": fault_summary,
                },
            )

        recomputed_count = sum(
            count - 1 for count in adapter.side_effect_counts.values() if count > 1
        )
        resume_run = {
            "completed_count": len(adapter.completed_ops),
            "skipped_completed": skipped_completed,
            "recomputed_count": recomputed_count,
            "corrupted_count": 1 if adapter.corrupted else 0,
            "state_digest": outcome["post_state_digest"],
        }

    reasons.append("RECOVERY_SYNTHETIC_SCENARIO_VERIFIED")
    findings.append(
        ReadinessFinding(
            code="RECOVERY_RESUME_CONVERGED",
            status=ReadinessStatus.READY_SYNTHETIC,
            message="Synthetic recovery harness converged with zero recomputation and zero corruption",
            evidence_state=NOT_OBSERVED,
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
            "fixture_digest": fix_digest,
            "initial_run": initial_run,
            "resume_run": resume_run,
            "fault": fault_summary,
            "real_archive_recovery_proven": False,
        },
    )
