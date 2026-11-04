"""Regression tests for MEGA-12: Generated-Only Recovery & Replay Consistency (+ Stretch S3)."""

from __future__ import annotations

import pytest

from gate2.recovery import RecoveryBinding
from gate2.workload import WorkloadSpec, generate
from vip_lab.common import NOT_OBSERVED, ReadinessStatus, VipLabError
from vip_lab.mega12 import (
    REPLAY_GRAPH_SCHEMA_VERSION,
    REQUIRED_NOT_OBSERVED_METRICS,
    STAGE_ID,
    ReplayGraph,
    SyntheticReplayHarnessAdapter,
    build_replay_graph_from_workload,
    build_synthetic_recovery_measurement_set,
    coerce_canonical_workload_spec,
    evaluate_fault_scenario_matrix,
    inspect_recovery_replay_consistency,
    verify_replay_graph,
    verify_replay_journal_lines,
)


def _sample_spec() -> WorkloadSpec:
    return WorkloadSpec(
        jobs=3,
        stages=2,
        artifact_bytes=48,
        cost_units=10,
        fault_position=0,
        seed=20261104,
        f01_sha="1" * 40,
        c04_sha="2" * 40,
        e05_sha="3" * 40,
        config_digest="4" * 64,
        concurrency=1,
        repetitions=2,
    )


def test_build_replay_graph_and_idempotent_single_commit() -> None:
    spec = _sample_spec()
    graph = build_replay_graph_from_workload(
        workload_spec=spec,
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
        workload_id="wl-mega12-synth",
    )
    assert isinstance(graph, ReplayGraph)
    assert graph.schema_version == REPLAY_GRAPH_SCHEMA_VERSION
    assert graph.workload_id == "wl-mega12-synth"
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
        workload_id="wl-mega12-synth",
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
        workload_id="wl-mega12-synth",
    )
    assert matrix["workload_id"] == "wl-mega12-synth"
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
    assert all(r["state_unchanged"] is True for r in matrix["refusal_checks"])


def test_stretch_s3_measurement_set_and_consistency_review() -> None:
    spec = _sample_spec()
    graph = build_replay_graph_from_workload(
        workload_spec=spec,
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
        workload_id="wl-mega12-synth",
    )
    matrix = evaluate_fault_scenario_matrix(
        workload_spec=spec,
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
        workload_id="wl-mega12-synth",
    )
    mset = build_synthetic_recovery_measurement_set(
        replay_graph=graph,
        fault_matrix=matrix,
    )
    mset_dict = mset.to_dict()
    assert mset_dict["schema_version"] == "gate2.measurement.v1"
    for row in mset_dict["measured"]:
        assert str(row["metric_id"]).startswith("synthetic_")
        assert str(row["derivation"]).startswith("SYNTHETIC_FIXTURE_ONLY:")
    not_obs_by_id = {row["metric_id"]: row for row in mset_dict["not_observed"]}
    for metric_name in REQUIRED_NOT_OBSERVED_METRICS:
        assert metric_name in not_obs_by_id
        assert not_obs_by_id[metric_name]["status"] == NOT_OBSERVED
        assert bool(not_obs_by_id[metric_name]["reason"])

    packet = inspect_recovery_replay_consistency(
        {
            "workload_spec": {
                **spec.to_dict(),
                "workload_id": "wl-mega12-synth",
            },
            "generation_id": "gen-mega12-01",
            "semantic_space_id": "siglip-v1-base:768:v1",
        }
    )
    assert packet.stage_id == STAGE_ID
    assert packet.status == ReadinessStatus.READY_SYNTHETIC
    assert packet.evidence_state == NOT_OBSERVED
    assert all(f.evidence_state == NOT_OBSERVED for f in packet.findings)
    assert packet.summary["observation_domain"] == "SYNTHETIC_FIXTURE_ONLY"
    assert packet.summary["real_archive_metrics_status"] == NOT_OBSERVED
    assert packet.summary["real_source_measured_claimed"] is False
    assert packet.summary["gate2_scale_evidence_proven"] is False
    assert packet.summary["mechanism_justification"] == "NOT_JUSTIFIED_SYNTHETIC_ONLY"
    assert packet.summary["real_archive_recovery_proven"] is False

    overclaim_packet = inspect_recovery_replay_consistency(
        {
            "workload_spec": {
                **spec.to_dict(),
                "workload_id": "wl-mega12-synth",
            },
            "claim_archive_scale_proven": True,
        }
    )
    assert overclaim_packet.status == ReadinessStatus.NOT_AUTHORIZED
    assert "SYNTHETIC_RECOVERY_OVERCLAIM_REFUSED" in overclaim_packet.blockers

    promote_packet = inspect_recovery_replay_consistency(
        {
            "workload_spec": {
                **spec.to_dict(),
                "workload_id": "wl-mega12-synth",
            },
            "promote_not_observed_metrics": ["archive_scale"],
        }
    )
    assert promote_packet.status == ReadinessStatus.NOT_AUTHORIZED
    assert "SYNTHETIC_RECOVERY_OVERCLAIM_REFUSED" in promote_packet.blockers


def test_unexpected_runtime_error_from_adapter_propagates_unswallowed() -> None:
    spec = _sample_spec()
    fixture = generate(spec)

    class _ExplodingAdapter(SyntheticReplayHarnessAdapter):
        def apply_idempotent(self, operation_id: str) -> None:
            raise RuntimeError("unexpected adapter disk failure")

    exploding = _ExplodingAdapter(
        fixture=fixture,
        generation_id="gen-mega12-01",
        semantic_space_id="siglip-v1-base:768:v1",
    )
    with pytest.raises(RuntimeError, match="unexpected adapter disk failure"):
        build_replay_graph_from_workload(
            workload_spec=spec,
            generation_id="gen-mega12-01",
            semantic_space_id="siglip-v1-base:768:v1",
            workload_id="wl-exploding",
            custom_adapter=exploding,
        )


def test_coerce_canonical_workload_spec_preserves_nondefault_nested_and_flat_and_rejects_conflicts() -> None:
    nondefault = WorkloadSpec(
        jobs=7,
        stages=4,
        artifact_bytes=128,
        cost_units=42,
        fault_position=3,
        seed=99887766,
        f01_sha="a" * 40,
        c04_sha="b" * 40,
        e05_sha="c" * 40,
        config_digest="d" * 64,
        concurrency=5,
        repetitions=6,
    )
    # 1. Nested WorkloadSpec.to_dict() round-trip
    nested_payload = {
        **nondefault.to_dict(),
        "workload_id": "wl-nested-7x4",
    }
    parsed_nested, wl_id_nested = coerce_canonical_workload_spec(nested_payload)
    assert wl_id_nested == "wl-nested-7x4"
    assert parsed_nested == nondefault
    assert parsed_nested.to_dict() == nondefault.to_dict()

    # 2. Flat representation round-trip
    flat_payload = {
        "workload_id": "wl-flat-7x4",
        "jobs": 7,
        "stages": 4,
        "artifact_bytes": 128,
        "cost_units": 42,
        "fault_position": 3,
        "seed": 99887766,
        "f01_sha": "a" * 40,
        "c04_sha": "b" * 40,
        "e05_sha": "c" * 40,
        "config_digest": "d" * 64,
        "concurrency": 5,
        "repetitions": 6,
    }
    parsed_flat, wl_id_flat = coerce_canonical_workload_spec(flat_payload)
    assert wl_id_flat == "wl-flat-7x4"
    assert parsed_flat == nondefault

    # 3. Reject conflicting mixed flat + nested keys
    mixed = {**nested_payload, "jobs": 7}
    with pytest.raises(VipLabError) as exc_mixed:
        coerce_canonical_workload_spec(mixed)
    assert exc_mixed.value.code == "INVALID_WORKLOAD_SPEC"

    # 4. Reject unknown dimension key
    bad_dim = nondefault.to_dict()
    bad_dim["dimensions"]["extra_dim"] = 1
    with pytest.raises(VipLabError) as exc_dim:
        coerce_canonical_workload_spec(bad_dim)
    assert exc_dim.value.code == "INVALID_WORKLOAD_SPEC"

    # 5. Reject missing required dimension key (no silent default replacement)
    missing_dim = nondefault.to_dict()
    del missing_dim["dimensions"]["repetitions"]
    with pytest.raises(VipLabError) as exc_missing:
        coerce_canonical_workload_spec(missing_dim)
    assert exc_missing.value.code == "INVALID_WORKLOAD_SPEC"
