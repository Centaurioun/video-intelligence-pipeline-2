from __future__ import annotations

import pytest

from gate2.faults import (
    Capability,
    FaultClass,
    InjectionError,
    capability,
    inject,
)


def test_fault_taxonomy_has_thirteen_stable_ids_and_explicit_states():
    assert tuple(item.value for item in FaultClass) == tuple("abcdefghijklm")
    states = {capability(item) for item in FaultClass}
    assert states <= {Capability.HARNESSED, Capability.NOT_YET_HARNESSED, Capability.UNREACHABLE}
    assert capability(FaultClass.E_REPEATED_IDEMPOTENCY_KEY) is Capability.HARNESSED
    assert capability(FaultClass.L_CONCURRENT_WRITER) is Capability.HARNESSED
    assert capability(FaultClass.M_REFERENTIAL_DIVERGENCE) is Capability.HARNESSED


@pytest.mark.parametrize("fault", [FaultClass.E_REPEATED_IDEMPOTENCY_KEY,
                                    FaultClass.L_CONCURRENT_WRITER,
                                    FaultClass.M_REFERENTIAL_DIVERGENCE])
def test_required_faults_are_deterministic_detected_and_pure(fault):
    payloads = {
        FaultClass.E_REPEATED_IDEMPOTENCY_KEY: {"second_submission": True, "key": "k1"},
        FaultClass.L_CONCURRENT_WRITER: {"writers": ["w2", "w1"], "resource": "synthetic-r"},
        FaultClass.M_REFERENTIAL_DIVERGENCE: {
            "attempts": [{"attempt_id": "a1"}], "referenced_attempt_ids": ["missing", "a1"]
        },
    }
    payload = payloads[fault]
    before = repr(payload)
    first = inject(fault, payload)
    second = inject(fault, payload)
    assert first == second
    assert first.disposition == "PASS"
    assert first.detected is True
    assert repr(payload) == before


def test_unavailable_faults_never_pass_and_unknown_fault_refuses():
    for fault in FaultClass:
        result = inject(fault, {})
        if capability(fault) is not Capability.HARNESSED:
            assert result.disposition == capability(fault).value
            assert result.disposition != "PASS"
    with pytest.raises(InjectionError, match="unknown fault"):
        inject("z", {})


def test_schedule_is_payload_deterministic_without_wall_clock_or_threads():
    payload = {"writers": ["b", "a", "c"], "resource": "r"}
    result = inject(FaultClass.L_CONCURRENT_WRITER, payload)
    assert result.details["schedule"] == (("a", 0), ("b", 1), ("c", 2))
    assert result == inject(FaultClass.L_CONCURRENT_WRITER, payload)

@pytest.mark.parametrize("text", ['{"payload": "{"}', '{"unterminated":', '{not-json}'])
def test_corrupt_at_rest_detects_malformed_json_content(text):
    result = inject(FaultClass.I_CORRUPT_AT_REST, {"payload": text})
    assert result.disposition == "PASS"
    assert result.detected is True
    assert result.details["disposition"] == "BLOCKED_PREREQUISITE"


def test_corrupt_at_rest_accepts_valid_json_object_content():
    result = inject(FaultClass.I_CORRUPT_AT_REST, {"payload": '{"payload": "intact"}'})
    assert result.disposition == "NOT_TRIGGERED"
    assert result.detected is False
    assert result.details["disposition"] == "ACCEPTED"


@pytest.mark.parametrize(
    ("payload", "expected_disposition", "expected_detected",
     "expected_detail", "expected_false_success"),
    [
        ({"recovery_swallowed": False}, "NOT_TRIGGERED", False, "ACCEPTED", False),
        ({"interruption_observed": False, "recovery_swallowed": False},
         "NOT_TRIGGERED", False, "ACCEPTED", False),
        ({"interruption_observed": True, "recovery_swallowed": False},
         "PASS", True, "BLOCKED_PREREQUISITE", False),
        ({"interruption_observed": True, "recovery_swallowed": True},
         "PASS", True, "FALSE_SUCCESS", True),
        ({"interruption_observed": True}, "NOT_TRIGGERED", False,
         "RECOVERY_OUTCOME_NOT_OBSERVED", False),
        ({"interruption_observed": False, "recovery_swallowed": True},
         "NOT_TRIGGERED", False, "ACCEPTED", False),
    ],
)
def test_interrupted_recovery_preserves_explicit_outcome_semantics(
    payload, expected_disposition, expected_detected, expected_detail,
    expected_false_success
):
    before = repr(payload)

    first = inject(FaultClass.H_INTERRUPTED_RECOVERY, payload)
    second = inject(FaultClass.H_INTERRUPTED_RECOVERY, payload)

    assert first == second
    assert first.disposition == expected_disposition
    assert first.detected is expected_detected
    assert first.details["disposition"] == expected_detail
    assert first.details.get("false_success", False) is expected_false_success
    assert repr(payload) == before
