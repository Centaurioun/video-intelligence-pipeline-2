"""FaultClass capability & refusal scenario evaluation for MEGA-12."""

from __future__ import annotations

import dataclasses
from pathlib import Path
import tempfile
from typing import Any

from gate2.faults import Capability, FaultClass, capability, inject
from gate2.recovery import RecoveryHarness, RecoveryRefusal
from gate2.workload import WorkloadSpec, generate
from vip_lab.common import canonical_json_dumps
from vip_lab.mega12.replay_graph import (
    DEFAULT_CURR_MANIFEST_DIGEST,
    SyntheticReplayHarnessAdapter,
    build_canonical_recovery_binding,
)

_BYTES_FAULT_CLASSES = frozenset({FaultClass.A, FaultClass.E, FaultClass.F})


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
    return "RECOVERY_REFUSAL"


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
    sample_dict = {
        "manifest_digest": DEFAULT_CURR_MANIFEST_DIGEST,
        "c04_sha": workload_spec.c04_sha,
        "e05_sha": workload_spec.e05_sha,
        "configuration_digest": workload_spec.config_digest,
        "duplicate_Complete_attempt": False,
        "stale_recovery_marker": False,
    }
    sample_dict_bytes = canonical_json_dumps(sample_dict).encode("utf-8")

    fault_rows: list[dict[str, Any]] = []
    harnessed_count = 0
    not_yet_harnessed_count = 0
    unreachable_count = 0

    for fc in FaultClass:
        cap = capability(fc)
        if cap == Capability.HARNESSED:
            harnessed_count += 1
            if fc in _BYTES_FAULT_CLASSES:
                mutated_bytes = inject(fc, sample_bytes)
                in_len = len(sample_bytes)
                out_len = len(mutated_bytes)
                differs = mutated_bytes != sample_bytes
            else:
                mutated_dict = inject(fc, dict(sample_dict))
                mutated_serialized = canonical_json_dumps(mutated_dict).encode("utf-8")
                in_len = len(sample_dict_bytes)
                out_len = len(mutated_serialized)
                differs = mutated_dict != sample_dict
            fault_rows.append(
                {
                    "fault_class": fc.value,
                    "capability": cap.value,
                    "execution_state": "EXECUTED_SYNTHETIC",
                    "input_bytes": in_len,
                    "mutated_bytes": out_len,
                    "mutated_differs_from_input": differs,
                }
            )
        elif cap == Capability.NOT_YET_HARNESSED:
            not_yet_harnessed_count += 1
            fault_rows.append(
                {
                    "fault_class": fc.value,
                    "capability": cap.value,
                    "execution_state": "NOT_EXECUTED",
                    "input_bytes": len(sample_bytes),
                    "mutated_bytes": None,
                    "mutated_differs_from_input": None,
                }
            )
        else:
            unreachable_count += 1
            fault_rows.append(
                {
                    "fault_class": fc.value,
                    "capability": cap.value,
                    "execution_state": "NOT_EXECUTED",
                    "input_bytes": len(sample_bytes),
                    "mutated_bytes": None,
                    "mutated_differs_from_input": None,
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

        # 1. GENERATION_MISMATCH on checkpoint reopen
        obs_gen = "NONE"
        try:
            RecoveryHarness.open(
                base_ckpt,
                dataclasses.replace(binding, generation_id="wrong-generation"),
                base_adapter,
            )
        except RecoveryRefusal as exc:
            obs_gen = _classify_refusal_code(exc)
        refusal_checks.append(
            {
                "expected_code": "GENERATION_MISMATCH",
                "observed_code": obs_gen,
                "state_unchanged": base_adapter.state_digest() == committed_digest,
            }
        )

        # 2. SEMANTIC_SPACE_MISMATCH on checkpoint reopen
        obs_space = "NONE"
        try:
            RecoveryHarness.open(
                base_ckpt,
                dataclasses.replace(binding, semantic_space_id="wrong-semantic-space"),
                base_adapter,
            )
        except RecoveryRefusal as exc:
            obs_space = _classify_refusal_code(exc)
        refusal_checks.append(
            {
                "expected_code": "SEMANTIC_SPACE_MISMATCH",
                "observed_code": obs_space,
                "state_unchanged": base_adapter.state_digest() == committed_digest,
            }
        )

        # 3. TRUNCATED_PAYLOAD (FaultClass.A), PARTIAL_RECORD (E), PARTIAL_INDEX, DIGEST_MISMATCH (F)
        adapter_scenarios = [
            (
                "TRUNCATED_PAYLOAD",
                SyntheticReplayHarnessAdapter(
                    fixture=fixture,
                    generation_id=generation_id,
                    semantic_space_id=semantic_space_id,
                    stage_payload_overrides={(0, 0): inject(FaultClass.A, sample_bytes)},
                ),
            ),
            (
                "PARTIAL_RECORD",
                SyntheticReplayHarnessAdapter(
                    fixture=fixture,
                    generation_id=generation_id,
                    semantic_space_id=semantic_space_id,
                    stage_payload_overrides={(0, 0): inject(FaultClass.E, sample_bytes)},
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
                    stage_payload_overrides={(0, 0): inject(FaultClass.F, sample_bytes)},
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
        "not_yet_harnessed_count": not_yet_harnessed_count,
        "unreachable_count": unreachable_count,
        "fault_rows": fault_rows,
        "refusal_checks": refusal_checks,
    }
