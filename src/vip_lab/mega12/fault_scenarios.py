"""FaultClass capability & refusal scenario evaluation for MEGA-12."""

from __future__ import annotations

import copy
import dataclasses
from pathlib import Path
import tempfile
from typing import Any

from gate2.faults import Capability, FaultClass, capability, inject
from gate2.recovery import RecoveryHarness, RecoveryRefusal
from gate2.workload import WorkloadSpec, generate
from vip_lab.common import VipLabError
from vip_lab.mega12.replay_graph import (
    DEFAULT_CURR_MANIFEST_DIGEST,
    SyntheticReplayHarnessAdapter,
    build_canonical_recovery_binding,
)


def _classify_refusal_code(exc: RecoveryRefusal) -> str:
    msg = str(exc)
    if "generation_id mismatch" in msg or "GENERATION_MISMATCH" in msg:
        return "GENERATION_MISMATCH"
    if "semantic_space_id mismatch" in msg or "SEMANTIC_SPACE_MISMATCH" in msg:
        return "SEMANTIC_SPACE_MISMATCH"
    if "TRUNCATED_PAYLOAD" in msg or "truncated" in msg:
        return "TRUNCATED_PAYLOAD"
    if "PARTIAL_RECORD" in msg:
        return "PARTIAL_RECORD"
    if "PARTIAL_INDEX" in msg:
        return "PARTIAL_INDEX"
    if "DIGEST_MISMATCH" in msg or "digest mismatch" in msg:
        return "DIGEST_MISMATCH"
    if "stale recovery binding" in msg:
        return "STALE_RECOVERY_BINDING"
    return "RECOVERY_REFUSAL"


def _build_canonical_fault_payload(
    fc: FaultClass,
    *,
    workload_spec: WorkloadSpec,
    sample_stage_digest: str,
) -> dict[str, Any]:
    if fc == FaultClass.A_BEFORE_STAGE_START:
        return {
            "predecessor_succeeded": False,
            "stage_digest": sample_stage_digest,
        }
    if fc == FaultClass.E_REPEATED_IDEMPOTENCY_KEY:
        return {
            "second_submission": True,
            "idempotency_key": "job_000_stage_000",
            "stage_digest": sample_stage_digest,
        }
    if fc == FaultClass.F_RESTART_RECONSTRUCTION:
        return {
            "decision_vector_a": sample_stage_digest,
            "decision_vector_b": (
                "f" * 64 if sample_stage_digest != "f" * 64 else "0" * 64
            ),
        }
    if fc == FaultClass.H_INTERRUPTED_RECOVERY:
        return {
            "interruption_observed": True,
            "recovery_swallowed": False,
            "stage_digest": sample_stage_digest,
        }
    if fc == FaultClass.I_CORRUPT_AT_REST:
        return {
            "payload": '{"payload": "{"}',
            "stage_digest": sample_stage_digest,
        }
    if fc == FaultClass.J_POST_SUCCESS_INVALIDATION:
        return {
            "chain": ["AVAILABLE", "CLEANED"],
            "stage_digest": sample_stage_digest,
        }
    if fc == FaultClass.K_IDENTITY_DRIFT:
        return {
            "sealed_digest": DEFAULT_CURR_MANIFEST_DIGEST,
            "observed_digest": "e" * 64,
            "c04_sha": workload_spec.c04_sha,
            "e05_sha": workload_spec.e05_sha,
            "config_digest": workload_spec.config_digest,
        }
    if fc == FaultClass.L_CONCURRENT_WRITER:
        return {
            "writers": ["writer-b", "writer-a"],
            "stage_digest": sample_stage_digest,
        }
    if fc == FaultClass.M_REFERENTIAL_DIVERGENCE:
        return {
            "attempts": [{"attempt_id": "att-000"}],
            "referenced_attempt_ids": ["att-000", "att-missing-001"],
            "stage_digest": sample_stage_digest,
        }
    return {
        "fault_class": fc.value,
        "stage_digest": sample_stage_digest,
    }


def evaluate_fault_scenario_matrix(
    *,
    workload_spec: WorkloadSpec,
    generation_id: str = "gen-synth-001",
    semantic_space_id: str = "siglip-v1-base:768:v1",
    workload_id: str | None = None,
) -> dict[str, Any]:
    fixture = generate(workload_spec)
    resolved_workload_id = (
        workload_id.strip()
        if isinstance(workload_id, str) and workload_id.strip()
        else f"wl-{fixture.fixture_digest[:16]}"
    )
    sample_job = fixture.jobs[0]
    sample_stage = sample_job.stages[0]
    sample_bytes = sample_stage.artifact
    sample_stage_digest = sample_stage.artifact_digest

    fault_rows: list[dict[str, Any]] = []
    harnessed_count = 0
    harnessed_detected_count = 0
    not_yet_harnessed_count = 0
    unreachable_count = 0

    for fc in FaultClass:
        cap = capability(fc)
        letter_code = fc.name.split("_", 1)[0]
        fault_payload = _build_canonical_fault_payload(
            fc,
            workload_spec=workload_spec,
            sample_stage_digest=sample_stage_digest,
        )
        before_snapshot = copy.deepcopy(fault_payload)
        inj_res = inject(fc, fault_payload)
        input_mutated = fault_payload != before_snapshot
        if input_mutated:
            raise VipLabError(
                "FAULT_INJECTION_MUTATED_INPUT",
                f"gate2.faults.inject() unexpectedly mutated input payload for {fc.name}.",
            )
        if cap == Capability.HARNESSED:
            harnessed_count += 1
            if not inj_res.detected or inj_res.disposition != "PASS":
                raise VipLabError(
                    "HARNESSED_FAULT_NOT_DETECTED",
                    f"Deliberately triggered HARNESSED fault {fc.name} was not detected (disposition={inj_res.disposition!r}, detected={inj_res.detected!r}).",
                )
            harnessed_detected_count += 1
            fault_rows.append(
                {
                    "fault_class": letter_code,
                    "fault_class_id": fc.value,
                    "fault_class_name": fc.name,
                    "capability": cap.value,
                    "execution_state": "EXECUTED_SYNTHETIC",
                    "disposition": inj_res.disposition,
                    "detected": inj_res.detected,
                    "input_mutated": input_mutated,
                    "payload_digest": inj_res.payload_digest,
                    "details": dict(inj_res.details),
                }
            )
        elif cap == Capability.NOT_YET_HARNESSED:
            not_yet_harnessed_count += 1
            fault_rows.append(
                {
                    "fault_class": letter_code,
                    "fault_class_id": fc.value,
                    "fault_class_name": fc.name,
                    "capability": cap.value,
                    "execution_state": "NOT_EXECUTED",
                    "disposition": inj_res.disposition,
                    "detected": inj_res.detected,
                    "input_mutated": input_mutated,
                    "payload_digest": inj_res.payload_digest,
                    "details": dict(inj_res.details),
                }
            )
        else:
            unreachable_count += 1
            fault_rows.append(
                {
                    "fault_class": letter_code,
                    "fault_class_id": fc.value,
                    "fault_class_name": fc.name,
                    "capability": cap.value,
                    "execution_state": "NOT_EXECUTED",
                    "disposition": inj_res.disposition,
                    "detected": inj_res.detected,
                    "input_mutated": input_mutated,
                    "payload_digest": inj_res.payload_digest,
                    "details": dict(inj_res.details),
                }
            )

    binding = build_canonical_recovery_binding(
        fixture=fixture,
        generation_id=generation_id,
        semantic_space_id=semantic_space_id,
    )
    refusal_checks: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        base_ckpt = Path(tmp_dir) / "base_checkpoint.json"
        base_adapter = SyntheticReplayHarnessAdapter(
            fixture=fixture,
            generation_id=generation_id,
            semantic_space_id=semantic_space_id,
        )
        base_harness = RecoveryHarness.open(base_ckpt, binding, base_adapter)
        base_harness.run(crash_point=None)
        committed_digest = base_adapter.state_digest()

        # 1. GENERATION_MISMATCH refusal during start_or_resume
        obs_gen = "NONE"
        gen_ckpt = Path(tmp_dir) / "gen_mismatch_checkpoint.json"
        try:
            gen_harness = RecoveryHarness.open(
                gen_ckpt,
                dataclasses.replace(binding, generation_id="wrong-generation"),
                base_adapter,
            )
            gen_harness.run(crash_point=None)
        except RecoveryRefusal as exc:
            obs_gen = _classify_refusal_code(exc)
        refusal_checks.append(
            {
                "expected_code": "GENERATION_MISMATCH",
                "observed_code": obs_gen,
                "state_unchanged": base_adapter.state_digest() == committed_digest,
            }
        )

        # 2. SEMANTIC_SPACE_MISMATCH refusal during start_or_resume
        obs_space = "NONE"
        space_ckpt = Path(tmp_dir) / "space_mismatch_checkpoint.json"
        try:
            space_harness = RecoveryHarness.open(
                space_ckpt,
                dataclasses.replace(binding, semantic_space_id="wrong-semantic-space"),
                base_adapter,
            )
            space_harness.run(crash_point=None)
        except RecoveryRefusal as exc:
            obs_space = _classify_refusal_code(exc)
        refusal_checks.append(
            {
                "expected_code": "SEMANTIC_SPACE_MISMATCH",
                "observed_code": obs_space,
                "state_unchanged": base_adapter.state_digest() == committed_digest,
            }
        )

        # 3. TRUNCATED_PAYLOAD, PARTIAL_RECORD, PARTIAL_INDEX, DIGEST_MISMATCH
        truncated_bytes = sample_bytes[: max(1, len(sample_bytes) // 2)]
        partial_record_bytes = sample_bytes[:-1]
        corrupted_digest_bytes = bytes([sample_bytes[0] ^ 0xFF]) + sample_bytes[1:]

        adapter_scenarios = [
            (
                "TRUNCATED_PAYLOAD",
                SyntheticReplayHarnessAdapter(
                    fixture=fixture,
                    generation_id=generation_id,
                    semantic_space_id=semantic_space_id,
                    stage_payload_overrides={(0, 0): truncated_bytes},
                ),
            ),
            (
                "PARTIAL_RECORD",
                SyntheticReplayHarnessAdapter(
                    fixture=fixture,
                    generation_id=generation_id,
                    semantic_space_id=semantic_space_id,
                    stage_payload_overrides={(0, 0): partial_record_bytes},
                ),
            ),
            (
                "PARTIAL_INDEX",
                SyntheticReplayHarnessAdapter(
                    fixture=fixture,
                    generation_id=generation_id,
                    semantic_space_id=semantic_space_id,
                    truncated_stage_list_for_job=0,
                ),
            ),
            (
                "DIGEST_MISMATCH",
                SyntheticReplayHarnessAdapter(
                    fixture=fixture,
                    generation_id=generation_id,
                    semantic_space_id=semantic_space_id,
                    stage_payload_overrides={(0, 0): corrupted_digest_bytes},
                ),
            ),
        ]
        for idx, (expected_code, fault_adapter) in enumerate(adapter_scenarios):
            pre_digest = fault_adapter.state_digest()
            ckpt = Path(tmp_dir) / f"fault_{idx}.json"
            observed_code = "NONE"
            try:
                h = RecoveryHarness.open(ckpt, binding, fault_adapter)
                h.run(crash_point=None)
            except RecoveryRefusal as exc:
                observed_code = _classify_refusal_code(exc)
            refusal_checks.append(
                {
                    "expected_code": expected_code,
                    "observed_code": observed_code,
                    "state_unchanged": fault_adapter.state_digest() == pre_digest,
                }
            )

    return {
        "workload_id": resolved_workload_id,
        "total_fault_classes": len(fault_rows),
        "harnessed_count": harnessed_count,
        "harnessed_detected_count": harnessed_detected_count,
        "not_yet_harnessed_count": not_yet_harnessed_count,
        "unreachable_count": unreachable_count,
        "fault_rows": fault_rows,
        "refusal_checks": refusal_checks,
    }
