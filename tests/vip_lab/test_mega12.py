"""Regression tests for MEGA-12: Generated-Only Recovery & Replay Consistency (+ Stretch S3)."""

from __future__ import annotations

import pytest

from gate2.workload import WorkloadSpec
from vip_lab.common import NOT_OBSERVED, ReadinessStatus, VipLabError
from vip_lab.mega12 import (
    REPLAY_GRAPH_SCHEMA_VERSION,
    REQUIRED_NOT_OBSERVED_METRICS,
    STAGE_ID,
    ReplayGraph,
    build_replay_graph_from_workload,
    build_synthetic_recovery_measurement_set,
    evaluate_fault_scenario_matrix,
    inspect_recovery_replay_consistency,
    verify_replay_graph,
    verify_replay_journal_lines,
)


def _sample_spec() -> WorkloadSpec:
    return WorkloadSpec(
        workload_id="wl-mega12-synth",
        seed=20261104,
        job_count=3,
        stages_per_job=2,
        payload_bytes=48,
    )


def test_build_replay_graph_and_idempotent_single_commit() -> None:
    spec = _sample_spec()
    graph = build_replay_graph_from_workload(
        workload_spec=spec,
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
    )
    assert isinstance(graph, ReplayGraph)
    assert graph.schema_version == REPLAY_GRAPH_SCHEMA_VERSION
    assert graph.workload_id == spec.workload_id
    assert graph.job_count == 3
    assert graph.stages_per_job == 2
    assert len(graph.nodes) == 6
    assert graph.idempotent_replay_verified is True
    assert graph.duplicate_side_effects == 0
    assert verify_replay_graph(graph) == graph.graph_digest

    journal_check = verify_replay_journal_lines(
        graph.journal_lines,
        expected_generation_id="gen-mega12-01",
        expected_semantic_space_id="siglip-v1-base:768:v1",
    )
    assert journal_check["verified_line_count"] == 6
    assert journal_check["final_state_digest"] == graph.final_state_digest


def test_replay_journal_rejects_truncated_line_wrong_generation_and_stage_gap() -> None:
    spec = _sample_spec()
    graph = build_replay_graph_from_workload(
        workload_spec=spec,
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
    )

    truncated = list(graph.journal_lines) + ['{"job_index": 0, "truncated": ']
    with pytest.raises(VipLabError) as exc_trunc:
        verify_replay_journal_lines(
            truncated,
            expected_generation_id="gen-mega12-01",
            expected_semantic_space_id="siglip-v1-base:768:v1",
        )
    assert exc_trunc.value.code == "REPLAY_JOURNAL_TRUNCATED_LINE"

    with pytest.raises(VipLabError) as exc_gen:
        verify_replay_journal_lines(
            graph.journal_lines,
            expected_generation_id="gen-wrong",
            expected_semantic_space_id="siglip-v1-base:768:v1",
        )
    assert exc_gen.value.code == "REPLAY_JOURNAL_GENERATION_MISMATCH"

    with pytest.raises(VipLabError) as exc_space:
        verify_replay_journal_lines(
            graph.journal_lines,
            expected_generation_id="gen-mega12-01",
            expected_semantic_space_id="siglip-v2-base:768:v2",
        )
    assert exc_space.value.code == "REPLAY_JOURNAL_SEMANTIC_SPACE_MISMATCH"

    missing_stage_zero = list(graph.journal_lines[1:])
    with pytest.raises(VipLabError) as exc_order:
        verify_replay_journal_lines(
            missing_stage_zero,
            expected_generation_id="gen-mega12-01",
            expected_semantic_space_id="siglip-v1-base:768:v1",
        )
    assert exc_order.value.code == "REPLAY_JOURNAL_STAGE_ORDER_INVALID"


def test_fault_scenario_matrix_distinguishes_harnessed_and_non_harnessed() -> None:
    matrix = evaluate_fault_scenario_matrix(
        workload_spec=_sample_spec(),
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
    )
    assert matrix["total_fault_classes"] == 13
    assert matrix["harnessed_count"] == 9
    assert matrix["not_yet_harnessed_count"] == 2
    assert matrix["unreachable_count"] == 2

    by_code = {row["fault_class"]: row for row in matrix["fault_rows"]}
    for code in ("A", "E", "F", "H", "I", "J", "K", "L", "M"):
        assert by_code[code]["capability"] == "HARNESSED"
        assert by_code[code]["execution_state"] == "EXECUTED_SYNTHETIC"
        assert by_code[code]["mutated_differs_from_input"] is True

    for code in ("B", "C"):
        assert by_code[code]["capability"] == "NOT_YET_HARNESSED"
        assert by_code[code]["execution_state"] == "NOT_EXECUTED"

    for code in ("D", "G"):
        assert by_code[code]["capability"] == "UNREACHABLE"
        assert by_code[code]["execution_state"] == "NOT_EXECUTED"

    refusal_codes = {r["expected_code"]: r["observed_code"] for r in matrix["refusal_checks"]}
    assert refusal_codes["GENERATION_MISMATCH"] == "GENERATION_MISMATCH"
    assert refusal_codes["SEMANTIC_SPACE_MISMATCH"] == "SEMANTIC_SPACE_MISMATCH"
    assert refusal_codes["TRUNCATED_PAYLOAD"] == "TRUNCATED_PAYLOAD"
    assert refusal_codes["PARTIAL_RECORD"] == "PARTIAL_RECORD"
    assert refusal_codes["PARTIAL_INDEX"] == "PARTIAL_INDEX"
    assert refusal_codes["DIGEST_MISMATCH"] == "DIGEST_MISMATCH"


def test_stretch_s3_measurement_set_and_consistency_review() -> None:
    spec = _sample_spec()
    graph = build_replay_graph_from_workload(
        workload_spec=spec,
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
    )
    matrix = evaluate_fault_scenario_matrix(
        workload_spec=spec,
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
    )
    mset = build_synthetic_recovery_measurement_set(
        replay_graph=graph,
        fault_matrix=matrix,
    )
    mset_dict = mset.as_dict()
    for metric_name in REQUIRED_NOT_OBSERVED_METRICS:
        assert mset_dict[metric_name]["value"] == NOT_OBSERVED
        assert mset_dict[metric_name]["status"] == NOT_OBSERVED

    packet = inspect_recovery_replay_consistency(
        {
            "workload_spec": {
                "workload_id": spec.workload_id,
                "seed": spec.seed,
                "job_count": spec.job_count,
                "stages_per_job": spec.stages_per_job,
                "payload_bytes": spec.payload_bytes,
            },
            "generation_id": "gen-mega12-01",
            "semantic_space_id": "siglip-v1-base:768:v1",
        }
    )
    assert packet.stage_id == STAGE_ID
    assert packet.status == ReadinessStatus.READY_SYNTHETIC
    assert packet.summary["mechanism_justification"] == "NOT_JUSTIFIED_SYNTHETIC_ONLY"
    assert packet.summary["real_archive_recovery_proven"] is False

    overclaim_packet = inspect_recovery_replay_consistency(
        {
            "workload_spec": {
                "workload_id": spec.workload_id,
                "seed": spec.seed,
                "job_count": spec.job_count,
                "stages_per_job": spec.stages_per_job,
                "payload_bytes": spec.payload_bytes,
            },
            "claim_archive_scale_proven": True,
        }
    )
    assert overclaim_packet.status == ReadinessStatus.NOT_AUTHORIZED
    assert "SYNTHETIC_RECOVERY_OVERCLAIM_REFUSED" in overclaim_packet.blockers
