"""Integration checks for real Gate-2 fault injection and recovery refusals.

Each case calls the production ``gate2.faults`` and ``gate2.recovery`` code and
asserts the observed outcome, so a fabricated fault transcript cannot satisfy
these tests.  Recovery refusals are produced by the harness itself (tampered
checkpoints, stale bindings, invalid measurements, refused receipts), not by
mocking the refusal path.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gate2 import faults
from gate2.recovery import RecoveryBinding, RecoveryHarness, RecoveryRefusal


F01_SHA = "345f9526d54f4fbd582c15f4f0b613bc8ab3996e"
C04_SHA = "5d482a1016b97d663c57ad31d8bac21c19c8c799"
E05_SHA = "e52b91d38a9f9c6651a4203eccbe59b03d908905"
OPERATIONS = ("op:stage-0", "op:stage-1")


class Adapter:
    """Deterministic in-memory recovery adapter with idempotent application."""

    def __init__(self, receipt_identity: str = "receipt:test-001",
                 refuse_receipt: bool = False) -> None:
        self.receipt_identity = receipt_identity
        self.refuse_receipt = refuse_receipt
        self.state: dict[str, int] = {}
        self.completed: set[str] = set()
        self.events: list[str] = []

    def validate_receipt(self, identity: str) -> bool:
        self.events.append("validate_receipt")
        return (not self.refuse_receipt) and identity == self.receipt_identity

    def reconcile_sqlite_tail(self) -> None:
        self.events.append("reconcile_sqlite_tail")

    def state_digest(self) -> str:
        return json.dumps(
            {"applications": dict(sorted(self.state.items())),
             "completed": sorted(self.completed)},
            sort_keys=True, separators=(",", ":"),
        )

    def start_or_resume(self, binding: RecoveryBinding) -> tuple[str, ...]:
        return OPERATIONS

    def is_complete(self, operation_id: str) -> bool:
        return operation_id in self.completed

    def apply_idempotent(self, operation_id: str) -> None:
        self.events.append(f"apply:{operation_id}")
        self.state.setdefault(operation_id, 1)

    def mark_complete(self, operation_id: str) -> None:
        self.completed.add(operation_id)


def _binding(**updates) -> RecoveryBinding:
    fields = dict(
        f01_sha=F01_SHA,
        c04_sha=C04_SHA,
        e05_sha=E05_SHA,
        workload_digest="1" * 64,
        configuration_digest="2" * 64,
        previous_manifest_digest="3" * 64,
        current_manifest_digest="4" * 64,
        generation_id="generation:test-001",
        semantic_space_id="space:test-001",
        receipt_identity="receipt:test-001",
    )
    fields.update(updates)
    return RecoveryBinding(**fields)


def test_detected_blocked_prerequisite_faults_report_pass():
    blocked = faults.inject(
        faults.FaultClass.A_BEFORE_STAGE_START, {"predecessor_succeeded": False}
    )
    assert blocked.detected is True
    assert blocked.disposition == "PASS"
    assert blocked.details["disposition"] == "BLOCKED_PREREQUISITE"

    admitted = faults.inject(
        faults.FaultClass.A_BEFORE_STAGE_START, {"predecessor_succeeded": True}
    )
    assert admitted.detected is False
    assert admitted.disposition == "NOT_TRIGGERED"

    divergence = faults.inject(
        faults.FaultClass.F_RESTART_RECONSTRUCTION,
        {"decision_vector_a": [1], "decision_vector_b": [2]},
    )
    assert divergence.detected is True
    assert divergence.disposition == "PASS"
    assert divergence.details["disposition"] == "BLOCKED_PREREQUISITE"

    illegal = faults.inject(
        faults.FaultClass.J_POST_SUCCESS_INVALIDATION, {"chain": ["AVAILABLE", "CLEANED"]}
    )
    assert illegal.detected is True
    assert illegal.disposition == "PASS"
    assert illegal.details["disposition"] == "ILLEGAL_TRANSITION"

    drift = faults.inject(
        faults.FaultClass.K_IDENTITY_DRIFT,
        {"sealed_digest": "a" * 64, "observed_digest": "b" * 64},
    )
    assert drift.detected is True
    assert drift.disposition == "PASS"
    assert drift.details["disposition"] == "BLOCKED_PREREQUISITE"


def test_false_success_recovery_fault_is_detected():
    swallowed = faults.inject(
        faults.FaultClass.H_INTERRUPTED_RECOVERY,
        {"interruption_observed": True, "recovery_swallowed": True},
    )
    assert swallowed.detected is True
    assert swallowed.details["disposition"] == "FALSE_SUCCESS"
    assert swallowed.details["false_success"] is True


@pytest.mark.parametrize(
    "fault_class",
    [faults.FaultClass.B_DURING_ATTEMPT, faults.FaultClass.C_PARTIAL_ARTIFACT,
     faults.FaultClass.D_RETRY_FAILED_JOB, faults.FaultClass.G_PROJECTION_REBUILD],
)
def test_unsupported_fault_classes_never_report_pass(fault_class):
    result = faults.inject(fault_class, {"attempts": 3})
    assert result.detected is False
    assert result.disposition != "PASS"
    assert faults.capability(fault_class) is not faults.Capability.HARNESSED


def test_crash_then_resume_preserves_idempotent_application(tmp_path):
    adapter = Adapter()
    binding = _binding()
    checkpoint = tmp_path / "checkpoint.json"
    harness = RecoveryHarness.open(checkpoint, binding, adapter)
    with pytest.raises(RuntimeError, match="synthetic crash"):
        harness.run(crash_point="after_side_effect_before_completion")
    assert adapter.state == {OPERATIONS[0]: 1}

    resumed = RecoveryHarness.open(checkpoint, binding, adapter).run()
    assert resumed["attempts"] == 2
    assert resumed["operation_count"] == len(OPERATIONS)
    assert adapter.state == {operation: 1 for operation in OPERATIONS}
    assert adapter.completed == set(OPERATIONS)
    assert resumed["pre_state_digest"] != ""
    assert resumed["post_state_digest"] != ""
    # The replay must not double-apply the side effect.
    assert adapter.events.count(f"apply:{OPERATIONS[0]}") == 2
    assert adapter.events.count(f"apply:{OPERATIONS[1]}") == 1


def test_refused_receipt_identity_fails_closed(tmp_path):
    adapter = Adapter(refuse_receipt=True)
    harness = RecoveryHarness.open(tmp_path / "checkpoint.json", _binding(), adapter)
    with pytest.raises(RecoveryRefusal, match="E05 receipt identity was refused"):
        harness.run()
    assert adapter.events == ["validate_receipt"]


def test_tampered_checkpoint_refuses_with_integrity_error(tmp_path):
    adapter = Adapter()
    binding = _binding()
    checkpoint = tmp_path / "checkpoint.json"
    RecoveryHarness.open(checkpoint, binding, adapter)
    envelope = json.loads(checkpoint.read_text(encoding="utf-8"))
    envelope["payload"]["attempt"] = 7
    checkpoint.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(RecoveryRefusal, match="invalid recovery apparatus checkpoint: integrity mismatch"):
        RecoveryHarness.open(checkpoint, binding, adapter)


def _reseal(checkpoint: Path, payload) -> None:
    envelope = json.loads(checkpoint.read_text(encoding="utf-8"))
    envelope["payload"] = payload
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    envelope["integrity_sha256"] = hashlib.sha256(canonical).hexdigest()
    checkpoint.write_text(json.dumps(envelope), encoding="utf-8")


def test_partial_checkpoint_refuses(tmp_path):
    adapter = Adapter()
    binding = _binding()
    checkpoint = tmp_path / "checkpoint.json"
    RecoveryHarness.open(checkpoint, binding, adapter)
    _reseal(checkpoint, {"schema": "synthetic-recovery-apparatus-v1"})
    with pytest.raises(RecoveryRefusal, match="partial or unknown apparatus checkpoint"):
        RecoveryHarness.open(checkpoint, binding, adapter)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("attempt", -1, "invalid measurement"),
        ("completed_count", "3", "invalid measurement"),
        ("crash_consumed", 0, "invalid crash measurement"),
    ],
)
def test_invalid_checkpoint_measurements_refuse(tmp_path, field, value, message):
    adapter = Adapter()
    binding = _binding()
    checkpoint = tmp_path / "checkpoint.json"
    RecoveryHarness.open(checkpoint, binding, adapter)
    envelope = json.loads(checkpoint.read_text(encoding="utf-8"))
    payload = dict(envelope["payload"])
    payload[field] = value
    _reseal(checkpoint, payload)
    with pytest.raises(RecoveryRefusal, match=message):
        RecoveryHarness.open(checkpoint, binding, adapter)


def test_stale_recovery_binding_refuses(tmp_path):
    adapter = Adapter()
    checkpoint = tmp_path / "checkpoint.json"
    RecoveryHarness.open(checkpoint, _binding(), adapter)
    stale = _binding(generation_id="generation:test-002")
    with pytest.raises(RecoveryRefusal, match="invalid recovery apparatus checkpoint: stale recovery binding"):
        RecoveryHarness.open(checkpoint, stale, adapter)


def test_unsupported_crash_point_refuses_without_adapter_side_effects(tmp_path):
    adapter = Adapter()
    harness = RecoveryHarness.open(tmp_path / "checkpoint.json", _binding(), adapter)
    with pytest.raises(ValueError, match="unsupported synthetic crash point"):
        harness.run(crash_point="during_action")
    assert adapter.events == []


@pytest.mark.parametrize("field", ["f01_sha", "c04_sha", "e05_sha"])
def test_recovery_binding_rejects_malformed_generation_sha(field):
    with pytest.raises(ValueError):
        _binding(**{field: "z" * 40})


def test_recovery_binding_rejects_empty_identity_field():
    with pytest.raises(ValueError):
        _binding(generation_id="")
