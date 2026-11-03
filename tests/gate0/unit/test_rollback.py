from __future__ import annotations

import pytest

from gate0.failure import rollback_status, rollback_event
from gate0.stages.lifecycle import advance_stage, LifecycleError, StageLifecycle


def test_rollback_is_idempotent_and_cleanup_failure_stays_blocked():
    assert rollback_status("AVAILABLE", cleanup_succeeded=False) == "QUARANTINED"
    assert rollback_status("QUARANTINED", cleanup_succeeded=False) == "CLEANUP_PENDING"
    assert rollback_status("CLEANUP_PENDING", cleanup_succeeded=False) == "CLEANUP_PENDING"
    assert rollback_status("CLEANUP_PENDING", cleanup_succeeded=True, rebuildable=True) == "CLEANED"
    assert rollback_status("CLEANUP_PENDING", cleanup_succeeded=True, rebuildable=False) == "TOMBSTONED"


def test_stage_controller_emits_ordered_transitions_and_rejects_bad_predecessor():
    running = advance_stage("run_1", "attempt_1", "prepare", "PLANNED", "RUNNING", "input", "cfg", now="2026-01-01T00:00:00Z")
    done = advance_stage("run_1", "attempt_1", "prepare", "RUNNING", "SUCCEEDED", "input", "cfg", now="2026-01-01T00:00:01Z")
    assert (running.from_status, running.to_status) == ("PLANNED", "RUNNING")
    assert done.from_status == "RUNNING"
    with pytest.raises(LifecycleError):
        advance_stage("run_1", "attempt_1", "prepare", "PLANNED", "SUCCEEDED", "input", "cfg")


def test_duplicate_terminal_transition_is_rejected_and_rollback_receipt_is_complete():
    lifecycle = StageLifecycle()
    lifecycle.advance("run_1", "attempt_1", "prepare", "PLANNED", "RUNNING", "input", "cfg")
    lifecycle.advance("run_1", "attempt_1", "prepare", "RUNNING", "SUCCEEDED", "input", "cfg")
    with pytest.raises(LifecycleError):
        lifecycle.advance("run_1", "attempt_1", "prepare", "RUNNING", "SUCCEEDED", "input", "cfg")
    event = rollback_event("attempt_1", ["artifact_a"], before_status="QUARANTINED", after_status="CLEANUP_PENDING", trigger="policy", actor="owner", quarantine_destination="quarantine/run_1", now="2026-01-01T00:00:00Z", errors=())
    assert event.event_type == "ROLLBACK"
    assert event.trigger == "policy"
    assert event.quarantine_destination == "quarantine/run_1"
    assert event.errors == ()
    assert event.idempotency_key


@pytest.mark.parametrize("before,after", [("AVAILABLE", "CLEANUP_PENDING"), ("QUARANTINED", "CLEANED"), ("CLEANUP_PENDING", "QUARANTINED"), ("CLEANED", "TOMBSTONED")])
def test_rollback_event_rejects_non_adjacent_or_terminal_transitions(before, after):
    with pytest.raises(ValueError, match="illegal rollback transition"):
        rollback_event("attempt_1", ["artifact_a"], before_status=before, after_status=after, trigger="policy", actor="owner", quarantine_destination="quarantine/run_1", now="2026-01-01T00:00:00Z")
