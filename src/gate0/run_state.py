"""Pure, fail-closed decisions for durable stage predecessor state."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from gate0.stages.lifecycle import STAGE_ORDER, STAGE_PREDECESSOR


_STAGE_STATUSES = {"PLANNED", "RUNNING", "SUCCEEDED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"}
_TERMINAL_STATUSES = {"SUCCEEDED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"}
_TRANSITION_FIELDS = {"transition_id", "run_id", "attempt_id", "stage", "from_status", "to_status"}


@dataclass(frozen=True)
class StageOrderDecision:
    allowed: bool
    stage: str
    predecessor: str | None
    reason: str | None


def _blocked(stage: str, predecessor: str | None, reason: str) -> StageOrderDecision:
    return StageOrderDecision(False, stage, predecessor, reason)


def stage_order_decision(stage: str, manifest: Mapping[str, object] | None) -> StageOrderDecision:
    """Return whether *stage* may start from the supplied persisted manifest.

    This function deliberately treats malformed state as a prerequisite block;
    callers must never proceed by ignoring a malformed transition row.
    """
    if stage not in STAGE_ORDER:
        raise ValueError(f"unknown stage: {stage}")
    predecessor = STAGE_PREDECESSOR[stage]
    if manifest is None:
        if stage == "prepare":
            return StageOrderDecision(True, stage, None, None)
        return _blocked(stage, predecessor, "STAGE_PREDECESSOR")
    if not isinstance(manifest, Mapping):
        return _blocked(stage, predecessor, "MALFORMED_MANIFEST")
    run_id = manifest.get("run_id")
    transitions = manifest.get("stage_transitions")
    if not isinstance(run_id, str) or not run_id or not isinstance(transitions, list):
        return _blocked(stage, predecessor, "MALFORMED_MANIFEST")

    parsed: list[Mapping[str, object]] = []
    seen_ids: set[str] = set()
    for row in transitions:
        if not isinstance(row, Mapping) or not _TRANSITION_FIELDS.issubset(row):
            return _blocked(stage, predecessor, "MALFORMED_TRANSITION")
        if any(not isinstance(row[field], str) or not row[field] for field in _TRANSITION_FIELDS):
            return _blocked(stage, predecessor, "MALFORMED_TRANSITION")
        if row["run_id"] != run_id or row["stage"] not in STAGE_ORDER:
            return _blocked(stage, predecessor, "MALFORMED_TRANSITION")
        if row["from_status"] not in _STAGE_STATUSES or row["to_status"] not in _STAGE_STATUSES:
            return _blocked(stage, predecessor, "MALFORMED_TRANSITION")
        transition_id = row["transition_id"]
        if transition_id in seen_ids:
            return _blocked(stage, predecessor, "MALFORMED_TRANSITION")
        seen_ids.add(transition_id)
        parsed.append(row)

    if stage == "prepare":
        # Any prior stage history means this is a re-entry, including a failed
        # or cancelled attempt; retry semantics belong to the attempt contract.
        return (_blocked(stage, None, "STAGE_HISTORY") if parsed
                else StageOrderDecision(True, stage, None, None))

    if any(row["stage"] == stage and row["to_status"] in _TERMINAL_STATUSES for row in parsed):
        return _blocked(stage, predecessor, "STAGE_REENTRY")
    if not any(row["stage"] == predecessor and row["to_status"] == "SUCCEEDED" for row in parsed):
        return _blocked(stage, predecessor, "STAGE_PREDECESSOR")
    return StageOrderDecision(True, stage, predecessor, None)

