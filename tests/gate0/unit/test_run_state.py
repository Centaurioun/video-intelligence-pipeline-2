from __future__ import annotations

import pytest

from gate0.run_state import stage_order_decision


def _manifest(*transitions: dict[str, object], run_id: str = "run-1") -> dict[str, object]:
    return {"run_id": run_id, "stage_transitions": list(transitions)}


def _transition(stage: str, to_status: str, *, run_id: str = "run-1") -> dict[str, object]:
    return {
        "transition_id": f"t-{stage}-{to_status}",
        "run_id": run_id,
        "attempt_id": "attempt-1",
        "stage": stage,
        "from_status": "RUNNING",
        "to_status": to_status,
    }


def test_prepare_requires_empty_stage_history():
    assert stage_order_decision("prepare", _manifest()).allowed
    decision = stage_order_decision("prepare", _manifest(_transition("prepare", "RUNNING")))
    assert not decision.allowed
    assert decision.reason == "STAGE_HISTORY"


def test_inventory_requires_prepare_succeeded():
    assert not stage_order_decision("inventory", _manifest()).allowed
    assert stage_order_decision("inventory", _manifest(_transition("prepare", "SUCCEEDED"))).allowed


@pytest.mark.parametrize("status", ["PARTIAL", "FAILED", "BLOCKED", "CANCELLED", "RUNNING"])
def test_predecessor_partial_failed_blocked_cancelled_or_running_is_rejected(status: str):
    decision = stage_order_decision("inventory", _manifest(_transition("prepare", status)))
    assert not decision.allowed
    assert decision.predecessor == "prepare"


def test_later_stage_success_does_not_fill_missing_immediate_predecessor():
    decision = stage_order_decision(
        "embed",
        _manifest(_transition("prepare", "SUCCEEDED"), _transition("inventory", "SUCCEEDED"), _transition("split", "SUCCEEDED"), _transition("label", "SUCCEEDED"), _transition("preflight", "SUCCEEDED"), _transition("rank", "SUCCEEDED")),
    )
    assert not decision.allowed
    assert decision.reason == "STAGE_PREDECESSOR"


def test_duplicate_terminal_stage_reentry_is_rejected():
    decision = stage_order_decision("inventory", _manifest(_transition("prepare", "SUCCEEDED"), _transition("inventory", "SUCCEEDED")))
    assert not decision.allowed
    assert decision.reason == "STAGE_REENTRY"


def test_malformed_or_cross_run_transition_fails_closed():
    malformed = {"run_id": "run-1", "stage": "prepare", "to_status": "SUCCEEDED"}
    assert not stage_order_decision("inventory", _manifest(malformed)).allowed
    cross_run = _transition("prepare", "SUCCEEDED", run_id="run-other")
    assert not stage_order_decision("inventory", _manifest(cross_run)).allowed


def test_unknown_stage_is_a_contract_error():
    with pytest.raises(ValueError, match="unknown stage"):
        stage_order_decision("repeat", _manifest())
