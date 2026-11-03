"""Prepare stage: initialize an attempt without publishing result artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreparePayload:
    run_id: str
    initialized: bool = True


@dataclass(frozen=True)
class PrepareResult:
    stage_status: str
    exit_code: int
    attempt_id: str
    output_artifact_refs: tuple[object, ...]
    failure_refs: tuple[str, ...]
    payload: PreparePayload


def prepare(*, run_id: str, attempt_id: str, output_root: Path, now: str) -> PrepareResult:
    # Initialization is deliberately in-memory. Publication is owned by the
    # inventory stage and no directory/source mutation is allowed here.
    return PrepareResult("SUCCEEDED", 0, attempt_id, (), (), PreparePayload(run_id))
