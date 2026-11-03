"""Fail-closed stage transition controller."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from gate0.identity import opaque_id

class LifecycleError(ValueError):
    pass

LEGAL = {"PLANNED": {"RUNNING"}, "RUNNING": {"SUCCEEDED", "PARTIAL", "FAILED", "BLOCKED", "CANCELLED"}}

# One authority for the executable stage dependency graph.  ``repeat`` is a
# read-only operation on a reported run and is intentionally not a stage here.
STAGE_ORDER = (
    "prepare", "inventory", "split", "label", "preflight",
    "extract", "embed", "rank", "evaluate", "report",
)
STAGE_PREDECESSOR = {
    "prepare": None,
    "inventory": "prepare",
    "split": "inventory",
    "label": "split",
    "preflight": "label",
    "extract": "preflight",
    "embed": "extract",
    "rank": "embed",
    "evaluate": "rank",
    "report": "evaluate",
}

@dataclass(frozen=True)
class StageTransitionRecord:
    transition_id: str
    run_id: str
    attempt_id: str
    stage: str
    from_status: str
    to_status: str
    input_digest: str
    config_digest: str
    policy_decision_id: str | None
    event_time: str
    failure_event_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"transition_id": self.transition_id, "run_id": self.run_id, "attempt_id": self.attempt_id, "stage": self.stage, "from_status": self.from_status, "to_status": self.to_status, "input_digest": self.input_digest, "config_digest": self.config_digest, "policy_decision_id": self.policy_decision_id, "event_time": self.event_time, "failure_event_ids": list(self.failure_event_ids)}

class StageLifecycle:
    """Stateful controller preventing duplicate terminal transitions."""
    def __init__(self) -> None:
        self.transitions: list[StageTransitionRecord] = []

    def advance(self, *args: Any, **kwargs: Any) -> StageTransitionRecord:
        run_id, attempt_id, stage = args[:3]
        if any(t.run_id == run_id and t.attempt_id == attempt_id and t.stage == stage and t.to_status in {"SUCCEEDED", "PARTIAL", "FAILED", "BLOCKED", "CANCELLED"} for t in self.transitions):
            raise LifecycleError("terminal stage transition already exists")
        record = advance_stage(*args, **kwargs)
        if any(t.transition_id == record.transition_id for t in self.transitions):
            raise LifecycleError("duplicate transition id")
        self.transitions.append(record)
        return record

def advance_stage(run_id: str, attempt_id: str, stage: str, expected_predecessor: str, next_status: str, input_digest: str, config_digest: str, *, policy_decision_id: str | None = None, failure_event_ids: tuple[str, ...] = (), now: str = "1970-01-01T00:00:00Z") -> StageTransitionRecord:
    if next_status not in LEGAL.get(expected_predecessor, set()):
        raise LifecycleError(f"illegal stage transition {expected_predecessor}->{next_status}")
    return StageTransitionRecord(opaque_id("transition", {"run_id": run_id, "attempt_id": attempt_id, "stage": stage, "from": expected_predecessor, "to": next_status, "input": input_digest, "config": config_digest, "time": now}), run_id, attempt_id, stage, expected_predecessor, next_status, input_digest, config_digest, policy_decision_id, now, tuple(failure_event_ids))
