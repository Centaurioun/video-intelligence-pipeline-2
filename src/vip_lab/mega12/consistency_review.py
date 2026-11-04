"""Recovery & replay consistency review (+ Stretch S3 MeasurementSet discipline) for MEGA-12."""

from __future__ import annotations

from typing import Any, Mapping

from gate2.measure import Measurement, MeasurementSet
from gate2.workload import WorkloadError, WorkloadSpec
from vip_lab.common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)
from vip_lab.mega12.fault_scenarios import evaluate_fault_scenario_matrix
from vip_lab.mega12.replay_graph import (
    ReplayGraph,
    build_replay_graph_from_workload,
    coerce_canonical_workload_spec,
    verify_replay_graph,
)

STAGE_ID = "MEGA-12.RECOVERY_REPLAY_CONSISTENCY"
REQUIRED_NOT_OBSERVED_METRICS: tuple[str, ...] = (
    "archive_reliability",
    "archive_scale",
    "wall_clock_throughput",
    "protected_media_behavior",
)


def build_synthetic_recovery_measurement_set(
    *,
    replay_graph: ReplayGraph,
    fault_matrix: Mapping[str, Any],
) -> MeasurementSet:
    mset = MeasurementSet()
    mset.add(
        Measurement.measured(
            metric_id="synthetic_jobs_committed",
            value=replay_graph.job_count,
            unit="jobs",
            derivation="gate2.workload+gate2.recovery:synthetic_in_memory",
            evidence_class="MEASURED",
        )
    )
    mset.add(
        Measurement.measured(
            metric_id="synthetic_stages_replayed",
            value=len(replay_graph.nodes),
            unit="stages",
            derivation="vip_lab.mega12.replay_graph:synthetic_in_memory",
            evidence_class="MEASURED",
        )
    )
    mset.add(
        Measurement.measured(
            metric_id="synthetic_harnessed_faults_tested",
            value=int(fault_matrix.get("harnessed_count", 0)),
            unit="fault_classes",
            derivation="gate2.faults:synthetic_in_memory",
            evidence_class="MEASURED",
        )
    )
    for metric_name in REQUIRED_NOT_OBSERVED_METRICS:
        mset.add(
            Measurement.not_observed(
                metric_id=metric_name,
                reason="synthetic_lab_no_real_archive_observation",
            )
        )
    return mset


def inspect_recovery_replay_consistency(
    payload: Mapping[str, Any],
) -> ReadinessPacket:
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "RECOVERY_REPLAY_CONSISTENCY_NOT_MAPPING",
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
                code="UNTRUSTED_AUTHORITY_CLAIM",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message=f"Rejected untrusted authority keys: {', '.join(untrusted_flags)}",
                evidence_state=NOT_OBSERVED,
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if (
        cleaned.get("real_archive_workload") is True
        or cleaned.get("claim_archive_scale_proven") is True
        or cleaned.get("introduce_external_queue_service") is True
    ):
        code = "SYNTHETIC_RECOVERY_OVERCLAIM_REFUSED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Synthetic recovery harness results cannot claim real-archive scale or justify new external services.",
                evidence_state=NOT_OBSERVED,
            )
        )

    spec_raw = cleaned.get("workload_spec", {})
    generation_id = str(cleaned.get("generation_id", "gen-synth-001"))
    semantic_space_id = str(cleaned.get("semantic_space_id", "siglip-v1-base:768:v1"))

    replay_graph_dict: dict[str, Any] | None = None
    fault_matrix: dict[str, Any] | None = None
    measurement_dict: dict[str, Any] | None = None

    if not isinstance(spec_raw, (WorkloadSpec, Mapping)):
        code = "INVALID_WORKLOAD_SPEC"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="workload_spec must be a WorkloadSpec or mapping.",
                evidence_state=NOT_OBSERVED,
            )
        )
    else:
        try:
            spec, wl_id = coerce_canonical_workload_spec(spec_raw)
            graph = build_replay_graph_from_workload(
                workload_spec=spec,
                generation_id=generation_id,
                semantic_space_id=semantic_space_id,
                workload_id=wl_id,
            )
            verify_replay_graph(graph)
            replay_graph_dict = graph.to_dict()
            fault_matrix = evaluate_fault_scenario_matrix(
                workload_spec=spec,
                generation_id=generation_id,
                semantic_space_id=semantic_space_id,
                workload_id=wl_id,
            )
            mset = build_synthetic_recovery_measurement_set(
                replay_graph=graph,
                fault_matrix=fault_matrix,
            )
            measurement_dict = mset.to_dict()
        except (WorkloadError, VipLabError, ValueError, TypeError) as exc:
            code = exc.code if isinstance(exc, VipLabError) else "WORKLOAD_OR_REPLAY_ERROR"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=str(exc),
                    evidence_state=NOT_OBSERVED,
                )
            )

    has_refusal = any(
        f.code == "SYNTHETIC_RECOVERY_OVERCLAIM_REFUSED"
        for f in findings
    )
    has_invalid = any(f.status == ReadinessStatus.INVALID for f in findings)

    if has_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif has_invalid:
        status = ReadinessStatus.INVALID
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("RECOVERY_REPLAY_CONSISTENCY_VERIFIED")
        findings.append(
            ReadinessFinding(
                code="RECOVERY_REPLAY_CONSISTENCY_VERIFIED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Generated-only recovery replay graph, fault capability matrix, and NOT_OBSERVED archive metrics verified.",
                evidence_state="MEASURED",
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=status,
        evidence_state="MEASURED" if status == ReadinessStatus.READY_SYNTHETIC else NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "replay_graph": replay_graph_dict,
            "fault_matrix": fault_matrix,
            "measurements": measurement_dict,
            "mechanism_justification": "NOT_JUSTIFIED_SYNTHETIC_ONLY",
            "real_archive_recovery_proven": False,
        },
    )
