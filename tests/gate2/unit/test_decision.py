"""Fail-closed BR-1..BR-9 decisions over current run-bound metric carriers."""
from __future__ import annotations

from gate2.decision import DeficitClass, Disposition, decide

F01 = {"sha": "cf8567cbbba321e79059b5e029e58c326dee9d01", "tree": "9d9b34accb355024b1936ebee08af5d7e158c36f"}
F02 = {"sha": "83bfb1732e18d58688a008fae27785c9f6c6e4ee", "tree": "a4bcb06e8b7885da045d525ff25c14529007c7d0"}
FREEZE = "a" * 64
WORKLOAD = "b" * 64
CONFIG = "c" * 64
FAULTS = "d" * 64


def observation(metric_id="restart_recovery_ms", *, status="MEASURED", value=5,
                candidate=F02, dependency_id="H3-F02", **changes):
    item = {
        "metric_id": metric_id, "status": status,
        "value": value if status == "MEASURED" else None,
        "unit": "ms" if status == "MEASURED" else "n/a",
        "evidence_class": "MEASURED" if status == "MEASURED" else None,
        "carrier_path": "runs/current/measurements.jsonl" if status == "MEASURED" else None,
        "carrier_sha256": "e" * 64 if status == "MEASURED" else None,
        "dependency_id": dependency_id,
        "candidate_sha": candidate["sha"], "candidate_tree": candidate["tree"],
        "freeze_digest": FREEZE, "workload_digest": WORKLOAD,
        "config_digest": CONFIG, "fault_schedule_digest": FAULTS,
        "evidence_valid": True,
        "repetition": 1,
    }
    item.update(changes)
    return item


def run(**overrides):
    args = {
        "bounds": {"restart_recovery_ms": 10},
        "observations": {"restart_recovery_ms": observation()},
        "classification": {"restart_recovery_ms": DeficitClass.C5},
        "dependency_heads": {"H3-F01": F01, "H3-F02": F02},
        "freeze_digest": FREEZE, "workload_digest": WORKLOAD,
        "config_digest": CONFIG, "fault_schedule_digest": FAULTS,
        "evidence_valid": True,
    }
    args.update(overrides)
    return decide(**args)


def test_clean_negative_remains_reachable_and_never_adopts():
    result = run()
    assert result.disposition is Disposition.NO_DEFICIT_OBSERVED
    assert not result.mechanism_eligible
    assert all(row["adoption"] is False for row in result.mechanisms)
    output = result.to_dict()
    assert output["production_eligible"] is False
    assert output["gate_promotion"] is False
    assert output["mechanism_adopted"] is False


def test_missing_carrier_with_no_crossing_fails_closed_as_insufficient_observability():
    result = run(observations={"restart_recovery_ms": observation(status="NOT_OBSERVED")})
    assert result.disposition is Disposition.INSUFFICIENT_OBSERVABILITY


def test_missing_carrier_cannot_be_ignored_when_another_metric_crosses():
    observations = {
        "restart_recovery_ms": observation(value=20),
        "startup_open_ms": observation("startup_open_ms", status="NOT_OBSERVED"),
    }
    result = run(bounds={"restart_recovery_ms": 10, "startup_open_ms": 20},
                 observations=observations,
                 classification={"restart_recovery_ms": DeficitClass.C5})
    assert result.disposition is Disposition.INSUFFICIENT_OBSERVABILITY
    assert not result.mechanism_eligible


def test_invalid_policy_identity_and_protocol_fail_closed():
    assert run(policy_decision="ALLOW-ish").disposition is Disposition.RUN_INVALID_POLICY_OR_IDENTITY
    assert run(protocol_valid=False).disposition is Disposition.PROTOCOL_INVALID
    assert run(evidence_valid=False).disposition is Disposition.RUN_INVALID_POLICY_OR_IDENTITY


def test_unreproduced_and_ambiguous_crossings_fail_closed():
    assert run(observations={"restart_recovery_ms": observation(value=20)},
               crossing_reproduced=False).disposition is Disposition.DEFICIT_NOT_REPRODUCED
    result = run(observations={"restart_recovery_ms": observation(value=20)},
                 classification={"restart_recovery_ms": (DeficitClass.C2, DeficitClass.C5)})
    assert result.disposition is Disposition.CLASSIFICATION_AMBIGUOUS


def test_unmapped_and_observability_classes_fail_closed():
    assert run(observations={"restart_recovery_ms": observation(value=20)},
               classification={"restart_recovery_ms": DeficitClass.C1}).disposition is Disposition.NO_MECHANISM_MAPPED
    assert run(observations={"restart_recovery_ms": observation(value=20)},
               classification={"restart_recovery_ms": DeficitClass.C7}).disposition is Disposition.INSUFFICIENT_OBSERVABILITY


def test_eligible_later_never_becomes_adoption():
    result = run(observations={"restart_recovery_ms": observation(value=20)})
    assert result.disposition is Disposition.MECHANISM_ELIGIBLE_FOR_LATER_EVALUATION
    assert result.smallest_missing_mechanism == "retry-backoff"
    assert all(row["adoption"] is False for row in result.mechanisms)


def test_historical_attempt4_numbers_without_current_carrier_are_not_measured():
    historical = {"metric_id": "restart_recovery_ms", "value": 320000,
                  "unit": "ms", "evidence_class": "MEASURED",
                  "derivation": "Attempt-4 historical record"}
    result = run(observations={"restart_recovery_ms": historical})
    assert result.disposition is Disposition.PROTOCOL_INVALID
    assert not result.mechanism_eligible


def test_dependency_or_frozen_run_identity_mismatch_fails_closed():
    assert run(observations={"restart_recovery_ms": observation(candidate=F01)},
               dependency_heads={"H3-F01": F01, "H3-F02": {"sha": "f" * 40, "tree": "1" * 40}}).disposition is Disposition.PROTOCOL_INVALID
    assert run(freeze_digest="f" * 64).disposition is Disposition.PROTOCOL_INVALID
    assert run(observations={"restart_recovery_ms": observation(workload_digest="f" * 64)}).disposition is Disposition.PROTOCOL_INVALID


def test_joint_dependency_measurement_preserves_both_pinned_sources():
    row = observation(dependency_id="H3-F01+H3-F02")
    assert run(observations={"restart_recovery_ms": row}).disposition is Disposition.NO_DEFICIT_OBSERVED
    row["dependency_id"] = "H3-F01+H3-F03"
    assert run(observations={"restart_recovery_ms": row}).disposition is Disposition.PROTOCOL_INVALID


def test_invalid_classification_and_invalid_bounds_fail_closed():
    result = run(observations={"restart_recovery_ms": observation(value=20)},
                 classification={"restart_recovery_ms": "C99"})
    assert result.disposition is Disposition.CLASSIFICATION_AMBIGUOUS
    assert run(bounds={"restart_recovery_ms": float("nan")}).disposition is Disposition.PROTOCOL_INVALID


def test_repetition_coverage_is_required_before_negative_or_eligible_disposition():
    rows = [observation(repetition=1), observation(repetition=2)]
    result = run(observations={"restart_recovery_ms": rows},
                 expected_repetitions={"restart_recovery_ms": 3})
    assert result.disposition is Disposition.INSUFFICIENT_OBSERVABILITY
    assert not result.mechanism_eligible


def test_unmet_preconditions_and_mechanism_preselection_are_closed():
    assert run(unmet_preconditions=("required fixture absent",)).disposition is Disposition.PRECONDITION_UNMET
    try:
        run(requested_mechanism="queue")
    except TypeError:
        pass
    else:
        raise AssertionError("decision API must reject request-side mechanism preselection")
