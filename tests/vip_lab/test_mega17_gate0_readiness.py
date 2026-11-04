"""Tests for MEGA-17 Workstream C: Gate-0 Diagnostic Retrieval Experiment Readiness."""

from __future__ import annotations

import pytest

from vip_lab.common import ReadinessStatus, VipLabError
from vip_lab.mega17.gate0_readiness import (
    GATE0_CONTRACT_ARTIFACT_NAMES,
    GATE0_VERDICT_STATES,
    REFUSAL_GATE0_AUTHENTIC_EXECUTION_NOT_AUTHORIZED,
    REFUSAL_GATE0_GOLD_LABEL_LEAKAGE_TO_RANKER,
    REFUSAL_GATE0_PROMOTION_FROM_SYNTHETIC_FORBIDDEN,
    REFUSAL_GATE0_SINGLE_REVIEWER_INSUFFICIENT,
    REFUSAL_GATE0_WINDOW_SAMPLING_INVALID,
     REFUSAL_GATE1_SUBSTITUTED_FOR_GATE0,
    Gate0ExperimentReadinessReceipt,
    build_gate0_experiment_readiness_receipt,
    evaluate_synthetic_gate0_scoring_fixture,
    inspect_gate0_experiment_readiness,
    verify_gate0_experiment_readiness_receipt,
)


def test_workstream_c_gate0_readiness_receipt_and_mandatory_flags() -> None:
    receipt = build_gate0_experiment_readiness_receipt()
    assert isinstance(receipt, Gate0ExperimentReadinessReceipt)

    # Mandatory Section 8 flags
    assert receipt.gate0_authentic_experiment_status == "NOT_RUN"
    assert receipt.gate0_d3_authorized is False
    assert receipt.gate0_real_model_execution == "NOT_OBSERVED"
    assert receipt.gate0_real_human_labels == "NOT_OBSERVED"
    assert receipt.gate0_promotion is False

    # Protocol cardinality: 24 positive (6x4 families), 8 absent, 8 development = 40 total
    proto = receipt.query_protocol_summary
    assert proto["total_queries"] == 40
    assert proto["evaluation_positive_count"] == 24
    assert proto["evaluation_absent_count"] == 8
    assert proto["development_count"] == 8
    assert proto["family_positive_counts"] == {
        "APPEARANCE": 6,
        "INTERACTION": 6,
        "SCENE_COMPOSITION_CAMERA_MOVEMENT": 6,
        "VISIBLE_ACTION": 6,
    }
    assert proto["independent_reviewer_count"] == 2
    assert proto["gold_labels_withheld_from_ranker"] is True

    # 4-second non-overlapping half-open windows and 2-FPS presentation-frame sampling
    win = receipt.window_sampling_spec
    assert win["window_duration_seconds"] == 4
    assert win["window_overlap_seconds"] == 0
    assert win["endpoint_semantics"] == "HALF_OPEN"
    assert win["sampling_fps"] == 2
    assert win["sampling_domain"] == "PRESENTATION_FRAMES"

    # All 12 Gate-0 contract artifacts validated for schema/contract readiness
    assert set(receipt.contract_artifacts_status.keys()) == set(GATE0_CONTRACT_ARTIFACT_NAMES)
    assert len(GATE0_CONTRACT_ARTIFACT_NAMES) == 12
    for art_name, art_info in receipt.contract_artifacts_status.items():
        assert art_info["contract_defined"] is True
        assert art_info["authentic_artifact_state"] == "NOT_OBSERVED"

    # Gate-0 vs Gate-1 separation explicitly recorded
    sep = receipt.gate0_vs_gate1_boundary
    assert sep["gate0_role"] == "DIAGNOSTIC_USEFUL_MOMENT_LIFT_OVER_METADATA_FLOOR"
    assert sep["gate1_substitutes_for_gate0"] is False
    assert len(sep["gate1_distinct_profiles"]) == 3

    verified = verify_gate0_experiment_readiness_receipt(receipt)
    assert verified["receipt_digest"] == receipt.receipt_digest


def test_workstream_c_deterministic_synthetic_scoring_thresholds_and_verdicts() -> None:
    # 1. Synthetic PASS scenario: Hit@10 = 21/24 (>=20/24), paired lift = 9/24 (>=5/24), family >= 5/6 (>=3/6)
    pass_fixture = evaluate_synthetic_gate0_scoring_fixture(scenario="SYNTHETIC_THRESHOLD_PASS")
    assert pass_fixture["synthetic_threshold_outcome"] == "PASS"
    assert pass_fixture["gate0_authentic_experiment_status"] == "NOT_RUN"
    assert pass_fixture["gate0_promotion"] is False
    assert pass_fixture["semantic_hit_at_10_numerator"] >= 20
    assert pass_fixture["paired_lift_numerator"] >= 5
    assert all(v >= 3 for v in pass_fixture["family_semantic_hits"].values())

    # 2. Synthetic FAIL scenario: overall Hit@10 = 18/24 (<20/24)
    fail_fixture = evaluate_synthetic_gate0_scoring_fixture(scenario="SYNTHETIC_THRESHOLD_FAIL_OVERALL")
    assert fail_fixture["synthetic_threshold_outcome"] == "FAIL"
    assert fail_fixture["gate0_authentic_experiment_status"] == "NOT_RUN"

    # 3. Synthetic FAIL scenario: family floor < 3/6 even if overall is high
    fam_fail = evaluate_synthetic_gate0_scoring_fixture(scenario="SYNTHETIC_THRESHOLD_FAIL_FAMILY_FLOOR")
    assert fam_fail["synthetic_threshold_outcome"] == "FAIL"
    assert "FAMILY_FLOOR_BELOW_3_OF_6" in fam_fail["failure_reasons"]

    # 4. Synthetic FAIL scenario: paired lift < 5/24
    lift_fail = evaluate_synthetic_gate0_scoring_fixture(scenario="SYNTHETIC_THRESHOLD_FAIL_PAIRED_LIFT")
    assert lift_fail["synthetic_threshold_outcome"] == "FAIL"
    assert "PAIRED_LIFT_BELOW_5_OF_24" in lift_fail["failure_reasons"]

    # All 5 verdict states are distinguished
    assert set(GATE0_VERDICT_STATES) == {
        "INVALID_PROTOCOL",
        "NOT_RUN",
        "BLOCKED_PREREQUISITE",
        "FAIL",
        "PASS",
    }


def test_workstream_c_refuses_protocol_violations_and_synthetic_promotion() -> None:
    # 1. Single reviewer instead of 2 independent reviewers
    pkt_rev = inspect_gate0_experiment_readiness({"reviewer_count": 1})
    assert pkt_rev.status == ReadinessStatus.BLOCKED
    assert REFUSAL_GATE0_SINGLE_REVIEWER_INSUFFICIENT in pkt_rev.blockers

    # 2. Gold label leakage into ranking inputs
    pkt_leak = inspect_gate0_experiment_readiness({"leak_gold_labels_to_ranker": True})
    assert pkt_leak.status == ReadinessStatus.BLOCKED
    assert REFUSAL_GATE0_GOLD_LABEL_LEAKAGE_TO_RANKER in pkt_leak.blockers

    # 3. Invalid window / FPS parameters
    pkt_win = inspect_gate0_experiment_readiness(
        {"window_duration_seconds": 5, "window_overlap_seconds": 1, "sampling_fps": 1}
    )
    assert pkt_win.status == ReadinessStatus.BLOCKED
    assert REFUSAL_GATE0_WINDOW_SAMPLING_INVALID in pkt_win.blockers

    # 4. Attempting to promote Gate-0 from synthetic results or substitute Gate-1 for Gate-0
    pkt_promo = inspect_gate0_experiment_readiness(
        {
            "claim_gate0_promotion_from_synthetic": True,
            "substitute_gate1_for_gate0": True,
            "claim_authentic_experiment_executed": True,
        }
    )
    assert pkt_promo.status == ReadinessStatus.NOT_AUTHORIZED
    assert REFUSAL_GATE0_PROMOTION_FROM_SYNTHETIC_FORBIDDEN in pkt_promo.blockers
    assert REFUSAL_GATE1_SUBSTITUTED_FOR_GATE0 in pkt_promo.blockers
    assert REFUSAL_GATE0_AUTHENTIC_EXECUTION_NOT_AUTHORIZED in pkt_promo.blockers


def test_workstream_c_tampered_receipt_is_rejected() -> None:
    receipt = build_gate0_experiment_readiness_receipt()
    raw = receipt.to_dict()
    raw["gate0_promotion"] = True
    with pytest.raises(VipLabError):
        verify_gate0_experiment_readiness_receipt(raw)
