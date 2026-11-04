"""FaultClass capability & refusal scenario evaluation for MEGA-12."""

from __future__ import annotations

from typing import Any

from gate2.faults import Capability, FaultClass, capability, inject
from gate2.recovery import RecoveryBinding, RecoveryHarness, RecoveryRefusal
from gate2.workload import WorkloadSpec, generate


def evaluate_fault_scenario_matrix(
    *,
    workload_spec: WorkloadSpec,
    generation_id: str = "gen-synth-001",
    semantic_space_id: str = "siglip-v1-base:768:v1",
) -> dict[str, Any]:
    fixture = generate(workload_spec)
    sample_job = fixture.jobs[0]
    sample_payload = sample_job.stages[0]

    fault_rows: list[dict[str, Any]] = []
    harnessed_count = 0
    not_yet_harnessed_count = 0
    unreachable_count = 0

    for fc in FaultClass:
        cap = capability(fc)
        if cap == Capability.HARNESSED:
            harnessed_count += 1
            mutated = inject(fc, sample_payload)
            fault_rows.append(
                {
                    "fault_class": fc.value,
                    "capability": cap.value,
                    "execution_state": "EXECUTED_SYNTHETIC",
                    "input_bytes": len(sample_payload),
                    "mutated_bytes": len(mutated),
                    "mutated_differs_from_input": mutated != sample_payload,
                }
            )
        elif cap == Capability.NOT_YET_HARNESSED:
            not_yet_harnessed_count += 1
            fault_rows.append(
                {
                    "fault_class": fc.value,
                    "capability": cap.value,
                    "execution_state": "NOT_EXECUTED",
                    "input_bytes": len(sample_payload),
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
                    "input_bytes": len(sample_payload),
                    "mutated_bytes": None,
                    "mutated_differs_from_input": None,
                }
            )

    binding = RecoveryBinding(
        generation_id=generation_id,
        semantic_space_id=semantic_space_id,
    )
    harness = RecoveryHarness(binding)
    pre_refusal_digest = harness.state_digest()
    refusal_checks: list[dict[str, Any]] = []

    scenarios = [
        (
            "GENERATION_MISMATCH",
            {
                "job_id": sample_job.job_index,
                "stages": sample_job.stages,
                "expected_count": len(sample_job.stages),
                "expected_bytes": workload_spec.payload_bytes,
                "generation_id": "wrong-generation",
                "semantic_space_id": semantic_space_id,
                "declared_digest": sample_job.digest,
            },
        ),
        (
            "SEMANTIC_SPACE_MISMATCH",
            {
                "job_id": sample_job.job_index,
                "stages": sample_job.stages,
                "expected_count": len(sample_job.stages),
                "expected_bytes": workload_spec.payload_bytes,
                "generation_id": generation_id,
                "semantic_space_id": "wrong-semantic-space",
                "declared_digest": sample_job.digest,
            },
        ),
        (
            "TRUNCATED_PAYLOAD",
            {
                "job_id": sample_job.job_index,
                "stages": (inject(FaultClass.A, sample_payload),) + sample_job.stages[1:],
                "expected_count": len(sample_job.stages),
                "expected_bytes": workload_spec.payload_bytes,
                "generation_id": generation_id,
                "semantic_space_id": semantic_space_id,
                "declared_digest": sample_job.digest,
            },
        ),
        (
            "PARTIAL_RECORD",
            {
                "job_id": sample_job.job_index,
                "stages": (inject(FaultClass.E, sample_payload),) + sample_job.stages[1:],
                "expected_count": len(sample_job.stages),
                "expected_bytes": workload_spec.payload_bytes,
                "generation_id": generation_id,
                "semantic_space_id": semantic_space_id,
                "declared_digest": sample_job.digest,
            },
        ),
        (
            "PARTIAL_INDEX",
            {
                "job_id": sample_job.job_index,
                "stages": sample_job.stages[:-1],
                "expected_count": len(sample_job.stages),
                "expected_bytes": workload_spec.payload_bytes,
                "generation_id": generation_id,
                "semantic_space_id": semantic_space_id,
                "declared_digest": sample_job.digest,
            },
        ),
        (
            "DIGEST_MISMATCH",
            {
                "job_id": sample_job.job_index,
                "stages": (inject(FaultClass.F, sample_payload),) + sample_job.stages[1:],
                "expected_count": len(sample_job.stages),
                "expected_bytes": workload_spec.payload_bytes,
                "generation_id": generation_id,
                "semantic_space_id": semantic_space_id,
                "declared_digest": sample_job.digest,
            },
        ),
    ]

    for expected_code, kwargs in scenarios:
        observed_code = "NONE"
        try:
            harness.run_job(**kwargs)
        except RecoveryRefusal as exc:
            observed_code = exc.code
        refusal_checks.append(
            {
                "expected_code": expected_code,
                "observed_code": observed_code,
                "state_unchanged": harness.state_digest() == pre_refusal_digest,
            }
        )

    return {
        "workload_id": workload_spec.workload_id,
        "total_fault_classes": len(fault_rows),
        "harnessed_count": harnessed_count,
        "not_yet_harnessed_count": not_yet_harnessed_count,
        "unreachable_count": unreachable_count,
        "fault_rows": fault_rows,
        "refusal_checks": refusal_checks,
    }
