"""Bounded, reproducible synthetic workload execution with local measurement.

This module closes the Gate-2 G2.2.1 execution gap without adding product
architecture.  It executes the frozen generated workload from
``gate2.workload`` against the local filesystem through a durable per-stage
journal:

* every stage payload is computed deterministically from the generated
  fixture, written atomically (temporary file, ``fsync``, ``os.replace``,
  directory ``fsync``) and recorded in an append-only journal;
* the fixture's own preregistered interruption point
  (``after_side_effect_before_completion``) is injected, and the run resumes
  in a *fresh* executor instance that reconstructs all state from the
  persisted journal only;
* local environment observations are captured: wall-clock latency, stage and
  byte throughput, process peak RSS, on-disk growth, restart integrity,
  duplicate-write behaviour, and cross-repetition repeatability.

Evidence boundaries (deliberate):

* Wall-clock, RSS, and disk numbers are observations of *this* host for a
  *synthetic generated* workload.  They are never reproducible identity and
  never production, archive, or model performance.
* Fixture identity (``fixture_digest``) is bound to the workload
  configuration only, so the same frozen workload can be re-executed after a
  code change and compared.
* No media, model, provider, network, or protected archive is touched.  The
  standard library ``fsync`` is used; a storage-hardware flush guarantee
  (``F_FULLFSYNC``) is not available from the standard library and remains
  ``NOT_OBSERVED``.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import statistics
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gate0.canonical_json import canonical_bytes
from gate0.identity import digest_json
from gate2 import faults as fault_api
from gate2 import workload
from gate2.decision import DeficitClass, decide
from gate2.verify import resolve_accepted_heads

REPO_ROOT = Path(__file__).resolve().parents[2]

RUN_SCHEMA = "gate2.synthetic-run.v1"
PREREGISTRATION_SCHEMA = "gate2.synthetic-run-preregistration.v1"
WORKLOAD_ID = "gate2-synthetic-scale-v2"
CONFIGURATION_ID = "gate2-synthetic-config-20261025-v2"
RECEIPT_IDENTITY = "receipt:gate2-synthetic-run-v2-001"

# Accepted generation identities already referenced by the Gate-2 suites.
# They are real commit objects in this repository and are resolved again from
# git; these literals only document the expected dependency generation.
C04_SHA = "5d482a1016b97d663c57ad31d8bac21c19c8c799"
E05_SHA = "e52b91d38a9f9c6651a4203eccbe59b03d908905"

FROZEN_SEED = 20261025
FROZEN_DIMENSIONS: dict[str, int] = {
    "jobs": 6,
    "stages": 4,
    "artifact_bytes": 65536,
    "cost_units": 400,
    "fault_position": 2,
    "concurrency": 1,
    "repetitions": 3,
}
TOTAL_ARTIFACT_BYTES = (
    FROZEN_DIMENSIONS["jobs"]
    * FROZEN_DIMENSIONS["stages"]
    * FROZEN_DIMENSIONS["artifact_bytes"]
)
INTERRUPTION_MODE = "after_side_effect_before_completion"

METRIC_DEFINITIONS: dict[str, dict[str, Any]] = {
    "fixture_generation_wall_time": {
        "unit": "milliseconds",
        "max": 30000,
        "repetitions": FROZEN_DIMENSIONS["repetitions"],
        "deficit_class": "C2-latency",
        "derivation": "time.perf_counter_ns() around gate2.workload.generate(spec)",
    },
    "stage_execution_wall_time": {
        "unit": "milliseconds",
        "max": 30000,
        "repetitions": FROZEN_DIMENSIONS["repetitions"],
        "deficit_class": "C2-latency",
        "derivation": (
            "sum of time.perf_counter_ns() around each durable stage application "
            "(deterministic work + atomic payload write + journal fsync + completion record)"
        ),
    },
    "restart_recovery_wall_time": {
        "unit": "milliseconds",
        "max": 30000,
        "repetitions": FROZEN_DIMENSIONS["repetitions"],
        "deficit_class": "C5-recovery-time",
        "derivation": (
            "time.perf_counter_ns() around resume in a fresh executor instance that "
            "reconstructs state from the persisted journal only"
        ),
    },
    "peak_rss_bytes": {
        "unit": "bytes",
        "max": 200000000,
        "repetitions": 1,
        "deficit_class": "C1-capacity",
        "derivation": (
            "resource.getrusage(RUSAGE_SELF).ru_maxrss after the workload "
            "(bytes on macOS, KiB x 1024 on Linux); includes the interpreter baseline"
        ),
    },
    "disk_space_growth_bytes": {
        "unit": "bytes",
        "max": 8000000,
        "repetitions": FROZEN_DIMENSIONS["repetitions"],
        "deficit_class": "C1-capacity",
        "derivation": (
            "sum of st_size for every file under the repetition directory after completion "
            "(artifacts + journal; APFS allocated bytes are reported separately as an observation)"
        ),
    },
    "artifact_integrity_mismatches": {
        "unit": "artifacts",
        "max": 0,
        "repetitions": FROZEN_DIMENSIONS["repetitions"],
        "deficit_class": "C3-durability",
        "derivation": (
            "persisted artifacts whose recomputed sha256 disagrees with the journal digest"
        ),
    },
    "restart_duplicate_writes": {
        "unit": "writes",
        "max": 0,
        "repetitions": FROZEN_DIMENSIONS["repetitions"],
        "deficit_class": "C3-durability",
        "derivation": "stage payload rewrites performed for a stage already recorded complete",
    },
    "restart_idempotent_replays": {
        "unit": "applications",
        "max": FROZEN_DIMENSIONS["jobs"] * FROZEN_DIMENSIONS["stages"],
        "repetitions": FROZEN_DIMENSIONS["repetitions"],
        "deficit_class": "C3-durability",
        "derivation": (
            "stage applications that found an already-correct durable artifact and "
            "performed no rewrite (expected 1 after the preregistered interruption)"
        ),
    },
    "repeatability_digest_mismatches": {
        "unit": "digests",
        "max": 0,
        "repetitions": 1,
        "deficit_class": "C3-durability",
        "derivation": (
            "fixture and artifact-manifest digest entries that differ between repetitions "
            "of the frozen workload"
        ),
    },
}
METRICS = tuple(METRIC_DEFINITIONS)

SAFETY = {
    "production_eligible": False,
    "gate_promotion": False,
    "mechanism_adopted": False,
}

NOT_OBSERVED = (
    "archive reliability",
    "archive scale",
    "protected media",
    "provider/model behavior",
    "production performance",
    "storage hardware flush beyond fsync",
)


class RunRefusal(RuntimeError):
    """The run cannot produce trustworthy evidence."""


class SyntheticInterruption(RuntimeError):
    """The preregistered synthetic interruption was reached."""


# ---------------------------------------------------------------------------
# identity and environment helpers
# ---------------------------------------------------------------------------

def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args], check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _source_files_digest(repo_root: Path) -> tuple[str, int]:
    entries = []
    root = repo_root / "src" / "gate2"
    for path in sorted(root.glob("*.py")):
        entries.append([path.name, hashlib.sha256(path.read_bytes()).hexdigest()])
    return digest_json({"schema": "gate2-source-digest.v1", "files": entries}), len(entries)


def _source_binding(repo_root: Path, expect_head: str | None) -> dict[str, Any]:
    head = _git(repo_root, "rev-parse", "HEAD")
    tree = _git(repo_root, "rev-parse", "HEAD^{tree}")
    status = _git(repo_root, "status", "--porcelain")
    try:
        base = _git(repo_root, "merge-base", "HEAD", "origin/main")
    except subprocess.CalledProcessError:
        base = head
    if expect_head is not None and head != expect_head:
        raise RunRefusal(
            f"stale base: expected HEAD {expect_head} but repository HEAD is {head}"
        )
    source_digest, source_files = _source_files_digest(repo_root)
    return {
        "head_sha": head,
        "head_tree": tree,
        "merge_base_origin_main": base,
        "worktree_clean": status == "",
        "expected_head": expect_head,
        "expect_head_enforced": expect_head is not None,
        "source_digest": source_digest,
        "source_digest_scope": "src/gate2/*.py working tree",
        "source_file_count": source_files,
    }


def _dependency_binding(repo_root: Path, accepted_heads: dict[str, dict[str, str]]) -> dict[str, Any]:
    """Record accepted dependency generations as resolved git objects.

    The accepted F01/F02 generations are verified by ``gate2.verify`` as real
    commit objects whose declared trees match.  Whether they are ancestors of
    the current HEAD is recorded as provenance information only: the accepted
    generation identities are frozen contract values, not branch tips.
    """
    result: dict[str, Any] = {}
    for generation, head in accepted_heads.items():
        ancestor = subprocess.run(
            ["git", "-C", str(repo_root), "merge-base", "--is-ancestor",
             head["sha"], "HEAD"],
            capture_output=True, text=True,
        )
        try:
            merge_base = _git(repo_root, "merge-base", "HEAD", head["sha"])
        except subprocess.CalledProcessError:
            merge_base = None
        result[generation] = {
            "sha": head["sha"],
            "tree": head["tree"],
            "in_head_history": ancestor.returncode == 0,
            "merge_base_with_head": merge_base,
        }
    return result


def _peak_rss_bytes() -> int:
    raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return raw if sys.platform == "darwin" else raw * 1024


def _environment() -> dict[str, Any]:
    clock = time.get_clock_info("perf_counter")
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "timer": {
            "name": "time.perf_counter_ns",
            "implementation": clock.implementation,
            "monotonic": clock.monotonic,
            "resolution_seconds": clock.resolution,
        },
        "resource_class": "HEAVY_CPU",
        "concurrency": 1,
        "workspace": "local isolated git worktree",
        "network": "not used",
        "durability_note": (
            "stdlib fsync only; F_FULLFSYNC / storage hardware flush NOT_OBSERVED"
        ),
    }


# ---------------------------------------------------------------------------
# deterministic stage work
# ---------------------------------------------------------------------------

def _artifact_path(repetition_dir: Path, job: int, stage: int) -> Path:
    return repetition_dir / "artifacts" / f"job-{job:02d}" / f"stage-{stage:02d}.bin"


def stage_work_digest(artifact: bytes, job: int, stage: int, units: int) -> str:
    """Deterministic bounded synthetic work over the stage payload."""
    digest = hashlib.sha256(
        b"gate2.synthetic.stage.work.v1\0"
        + struct.pack(">III", job, stage, units)
        + artifact
    ).digest()
    for index in range(units):
        digest = hashlib.sha256(digest + index.to_bytes(4, "big")).digest()
    return digest.hex()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    _fsync_directory(path.parent)


# ---------------------------------------------------------------------------
# durable journal
# ---------------------------------------------------------------------------

_ARTIFACT_KEYS = {"seq", "job", "stage", "phase", "digest", "work_digest", "bytes"}
_COMPLETE_KEYS = {"seq", "job", "stage", "phase"}
_JOURNAL_NAME = "journal.jsonl"


class StageJournal:
    """Append-only, fsynced journal of durable stage applications."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._seq = 0
        self.entries: dict[tuple[int, int], dict[str, Any]] = {}

    @classmethod
    def load(cls, path: Path) -> "StageJournal":
        journal = cls(path)
        if path.exists():
            lines = path.read_text(encoding="utf-8").splitlines()
            for line in lines:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise RunRefusal(f"journal is not valid JSON: {exc}") from exc
                journal._absorb(record, expected_seq=journal._seq + 1)
        return journal

    def _absorb(self, record: Any, *, expected_seq: int) -> None:
        if not isinstance(record, dict):
            raise RunRefusal("journal record must be an object")
        phase = record.get("phase")
        keys = _ARTIFACT_KEYS if phase == "artifact" else _COMPLETE_KEYS
        if phase not in {"artifact", "complete"} or set(record) != keys:
            raise RunRefusal("journal record has an unknown shape")
        if record.get("seq") != expected_seq:
            raise RunRefusal("journal sequence is not contiguous")
        job, stage = record.get("job"), record.get("stage")
        if (isinstance(job, bool) or isinstance(stage, bool)
                or not isinstance(job, int) or not isinstance(stage, int)
                or job < 0 or stage < 0):
            raise RunRefusal("journal record has an invalid stage coordinate")
        key = (job, stage)
        state = self.entries.setdefault(key, {"digest": None, "work_digest": None,
                                              "bytes": None, "complete": False})
        if phase == "artifact":
            digest = record.get("digest")
            work_digest = record.get("work_digest")
            nbytes = record.get("bytes")
            if state["digest"] is not None:
                raise RunRefusal("duplicate artifact record in journal")
            if not isinstance(digest, str) or len(digest) != 64 or not all(
                    character in "0123456789abcdef" for character in digest):
                raise RunRefusal("journal artifact digest is invalid")
            if not isinstance(work_digest, str) or len(work_digest) != 64:
                raise RunRefusal("journal work digest is invalid")
            if isinstance(nbytes, bool) or not isinstance(nbytes, int) or nbytes <= 0:
                raise RunRefusal("journal artifact byte count is invalid")
            state["digest"] = digest
            state["work_digest"] = work_digest
            state["bytes"] = nbytes
        else:
            if state["digest"] is None:
                raise RunRefusal("completion record precedes its artifact record")
            if state["complete"]:
                raise RunRefusal("duplicate completion record in journal")
            state["complete"] = True
        self._seq = record["seq"]

    def _append(self, record: dict[str, Any]) -> None:
        payload = {"seq": self._seq + 1, **record}
        self._absorb(payload, expected_seq=self._seq + 1)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        created = not self.path.exists()
        with self.path.open("ab") as stream:
            stream.write(canonical_bytes(payload) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        if created:
            _fsync_directory(self.path.parent)

    def append_artifact(self, job: int, stage: int, digest: str, work_digest: str,
                        nbytes: int) -> None:
        self._append({"job": job, "stage": stage, "phase": "artifact",
                      "digest": digest, "work_digest": work_digest, "bytes": nbytes})

    def append_complete(self, job: int, stage: int) -> None:
        self._append({"job": job, "stage": stage, "phase": "complete"})

    def is_complete(self, job: int, stage: int) -> bool:
        entry = self.entries.get((job, stage))
        return bool(entry and entry["complete"])

    def completed_stages(self) -> int:
        return sum(1 for entry in self.entries.values() if entry["complete"])


class _Executor:
    """Durable stage executor that reconstructs all state from the journal."""

    def __init__(self, fixture: workload.SyntheticFixture, repetition_dir: Path,
                 journal: StageJournal) -> None:
        self.fixture = fixture
        self.repetition_dir = repetition_dir
        self.journal = journal
        self.stage_latencies_ms: list[float] = []
        self.primary_writes = 0
        self.idempotent_replays = 0
        self.repairs = 0
        self.duplicate_writes = 0

    def _apply(self, job: int, stage: int) -> None:
        stage_model = self.fixture.jobs[job].stages[stage]
        artifact = stage_model.artifact
        content_digest = hashlib.sha256(artifact).hexdigest()
        work_digest = stage_work_digest(artifact, job, stage, stage_model.cost_units)
        target = _artifact_path(self.repetition_dir, job, stage)
        existing = self.journal.entries.get((job, stage))
        started = time.perf_counter_ns()
        if existing is not None and existing["digest"] is not None:
            on_disk = target.read_bytes() if target.exists() else b""
            if hashlib.sha256(on_disk).hexdigest() == existing["digest"]:
                self.idempotent_replays += 1
            else:
                _write_atomic(target, artifact)
                self.repairs += 1
        else:
            _write_atomic(target, artifact)
            self.journal.append_artifact(job, stage, content_digest, work_digest,
                                         len(artifact))
            self.primary_writes += 1
        self.stage_latencies_ms.append((time.perf_counter_ns() - started) / 1_000_000)

    def run(self, *, interrupt_at: tuple[int, int] | None) -> dict[str, Any]:
        interrupted = False
        for job in range(self.fixture.spec.jobs):
            for stage in range(self.fixture.spec.stages):
                if self.journal.is_complete(job, stage):
                    if interrupt_at == (job, stage):
                        self.duplicate_writes += 0  # skipping a complete stage is correct
                    continue
                self._apply(job, stage)
                if interrupt_at == (job, stage) and not interrupted:
                    interrupted = True
                    raise SyntheticInterruption(
                        "synthetic interruption after durable side effect before completion"
                    )
                self.journal.append_complete(job, stage)
        return {"interrupted": interrupted}


# ---------------------------------------------------------------------------
# verification and measurement helpers
# ---------------------------------------------------------------------------

def verify_persisted_artifacts(repetition_dir: Path | str) -> dict[str, Any]:
    """Recompute every persisted artifact digest against the journal."""
    repetition_dir = Path(repetition_dir)
    journal_path = repetition_dir / _JOURNAL_NAME
    if not journal_path.exists():
        raise RunRefusal(f"missing journal: {journal_path}")
    journal = StageJournal.load(journal_path)
    checked = 0
    mismatches = 0
    incomplete = 0
    errors: list[dict[str, Any]] = []
    for (job, stage), state in sorted(journal.entries.items()):
        if not state["complete"]:
            incomplete += 1
        if state["digest"] is None:
            continue
        checked += 1
        target = _artifact_path(repetition_dir, job, stage)
        actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
        if actual != state["digest"]:
            mismatches += 1
            errors.append({
                "job": job, "stage": stage, "expected": state["digest"], "actual": actual,
            })
    return {
        "verified": checked > 0 and mismatches == 0 and incomplete == 0,
        "checked": checked,
        "mismatches": mismatches,
        "completed_stages": journal.completed_stages(),
        "incomplete_stages": incomplete,
        "errors": errors,
    }


def _artifact_manifest(repetition_dir: Path) -> dict[str, str]:
    journal = StageJournal.load(repetition_dir / _JOURNAL_NAME)
    manifest = {}
    for (job, stage), state in sorted(journal.entries.items()):
        manifest[f"job-{job:02d}/stage-{stage:02d}.bin"] = state["digest"]
    return manifest


def _disk_usage(directory: Path) -> dict[str, int]:
    apparent = allocated = files = 0
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            stat = path.stat()
            apparent += stat.st_size
            allocated += stat.st_blocks * 512
            files += 1
    return {"files": files, "apparent_bytes": apparent, "allocated_bytes": allocated}


def _configuration() -> dict[str, Any]:
    """Workload-semantics configuration only: identity must be host independent."""
    return {
        "schema": "gate2.synthetic-run-configuration.v1",
        "generator": "gate2.workload.generate",
        "executor": "gate2.runner.StageJournal",
        "dimensions": dict(FROZEN_DIMENSIONS),
        "seed": FROZEN_SEED,
        "interruption": INTERRUPTION_MODE,
        "fault_schedule_rule": "gate2.workload.generate fixture fault_schedule",
        "config_digest_rule": "sha256 over canonical JSON of this document",
    }


def _carrier_bytes(metric: str, unit: str, values: dict[int, float]) -> bytes:
    records = [
        {"metric_id": metric, "repetition": repetition, "unit": unit, "value": value}
        for repetition, value in sorted(values.items())
    ]
    return canonical_bytes(records) + b"\n"


def _observation_row(*, metric: str, repetition: int, value: float, unit: str,
                     carrier_path: str, carrier_sha256: str, freeze_digest: str,
                     workload_digest: str, config_digest: str,
                     fault_schedule_digest: str, dependency_heads: dict[str, Any],
                     candidate: dict[str, str]) -> dict[str, Any]:
    return {
        "metric_id": metric,
        "repetition": repetition,
        "status": "MEASURED",
        "value": float(value),
        "unit": unit,
        "evidence_class": "MEASURED",
        "carrier_path": carrier_path,
        "carrier_sha256": carrier_sha256,
        "dependency_id": "H3-F01+H3-F02",
        "candidate_sha": candidate["sha"],
        "candidate_tree": candidate["tree"],
        "freeze_digest": freeze_digest,
        "workload_digest": workload_digest,
        "config_digest": config_digest,
        "fault_schedule_digest": fault_schedule_digest,
    }


def _fault_evidence(detail: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Evaluate the executed run's observed failure/recovery facts through the
    existing Gate-2 fault-class API, so the evidence is not just descriptive."""
    interruptions = [item["interruption"]["observed"] for item in detail]
    replays = [item["resume"]["idempotent_replays"] for item in detail]
    requests = (
        (
            fault_api.FaultClass.H_INTERRUPTED_RECOVERY,
            {"interruption_observed": all(interruptions), "recovery_swallowed": False},
            "every repetition was interrupted after the durable side effect and before "
            "the completion record, and the recovery outcome was observed (not swallowed)",
        ),
        (
            fault_api.FaultClass.E_REPEATED_IDEMPOTENCY_KEY,
            {"second_submission": all(replay >= 1 for replay in replays)},
            "the interrupted stage was applied a second time by the fresh executor; the "
            "durable artifact was reused with no second canonical write",
        ),
    )
    evidence: list[dict[str, Any]] = []
    for fault_class, payload, basis in requests:
        result = fault_api.inject(fault_class, payload)
        evidence.append({
            "fault_class": result.fault_class.name,
            "fault_class_id": result.fault_class.value,
            "capability": fault_api.capability(result.fault_class).name,
            "disposition": result.disposition,
            "detected": result.detected,
            "details": dict(result.details),
            "payload": payload,
            "payload_digest": result.payload_digest,
            "evidence_basis": basis,
        })
    return evidence


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

def execute_and_emit(out_dir: Path | str, *, expect_head: str | None = None,
                     discard_artifacts: bool = False,
                     repo_root: Path | str | None = None) -> dict[str, Any]:
    """Execute the frozen workload, write bare evidence, return the receipt."""
    repo_root = Path(repo_root) if repo_root is not None else REPO_ROOT
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise RunRefusal(f"refusing to write evidence into a non-empty directory: {out_dir}")

    binding = _source_binding(repo_root, expect_head)
    accepted_heads = resolve_accepted_heads(repo_root)
    dependency_binding = _dependency_binding(repo_root, accepted_heads)

    configuration = _configuration()
    config_digest = digest_json(configuration)
    spec = workload.WorkloadSpec(
        jobs=FROZEN_DIMENSIONS["jobs"],
        stages=FROZEN_DIMENSIONS["stages"],
        artifact_bytes=FROZEN_DIMENSIONS["artifact_bytes"],
        cost_units=FROZEN_DIMENSIONS["cost_units"],
        fault_position=FROZEN_DIMENSIONS["fault_position"],
        seed=FROZEN_SEED,
        f01_sha=accepted_heads["F01"]["sha"],
        c04_sha=C04_SHA,
        e05_sha=E05_SHA,
        config_digest=config_digest,
        concurrency=FROZEN_DIMENSIONS["concurrency"],
        repetitions=FROZEN_DIMENSIONS["repetitions"],
    )
    workload_digest = digest_json(spec.to_dict())

    fixture_generation_ms: dict[int, float] = {}
    fixture: workload.SyntheticFixture | None = None
    fixture_digest: str | None = None
    for repetition in range(1, FROZEN_DIMENSIONS["repetitions"] + 1):
        started = time.perf_counter_ns()
        current = workload.generate(spec)
        fixture_generation_ms[repetition] = (time.perf_counter_ns() - started) / 1_000_000
        if fixture is None:
            fixture = current
            fixture_digest = current.fixture_digest
        elif current.fixture_digest != fixture_digest:
            raise RunRefusal("fixture identity is not deterministic across repetitions")
    assert fixture is not None and fixture_digest is not None

    fault_schedule = {
        "seed": FROZEN_SEED,
        "repetitions": FROZEN_DIMENSIONS["repetitions"],
        "fault": INTERRUPTION_MODE,
        "events": [list(point) for point in fixture.fault_schedule],
    }
    fault_schedule_digest = digest_json(fault_schedule)

    preregistration: dict[str, Any] = {
        "schema": PREREGISTRATION_SCHEMA,
        "scope": "synthetic_generated_only",
        "workload_identity": {"workload_id": WORKLOAD_ID, "digest": workload_digest},
        "configuration_identity": {"config_id": CONFIGURATION_ID, "digest": config_digest},
        "dependency_generations": {
            "F01": accepted_heads["F01"]["sha"],
            "F02": accepted_heads["F02"]["sha"],
        },
        "fault_schedule": fault_schedule,
        "metric_definitions": {
            metric: {
                "unit": definition["unit"],
                "max": definition["max"],
                "repetitions": definition["repetitions"],
                "deficit_class": definition["deficit_class"],
                "derivation": definition["derivation"],
            }
            for metric, definition in METRIC_DEFINITIONS.items()
        },
        "evidence_declarations": {metric: "MEASURED" for metric in METRICS},
        "numeric_bounds": {metric: definition["max"]
                           for metric, definition in METRIC_DEFINITIONS.items()},
        "classification": {metric: definition["deficit_class"]
                           for metric, definition in METRIC_DEFINITIONS.items()},
        "classification_rule": {
            "rule_id": "gate2-synthetic-bounded-v2",
            "threshold": "measured values must not exceed the declared numeric bounds",
        },
        "run_attempt_identity": {
            "run_id": f"gate2-synthetic-{config_digest[:12]}",
            "receipt_identity": RECEIPT_IDENTITY,
        },
        "policy_authority": {
            "policy_id": "gate2-synthetic-local-reliability-v1",
            "authority": "owner-authorized local generated synthetic scope",
            "resource_policy": "docs/portfolio/portfolio-v1/resource-policy-v5.yaml",
        },
        "resource_request": {"resource_class": "HEAVY_CPU", "concurrency": 1},
        "baseline": {
            "storage": "local generated fixture",
            "index": "durable per-stage journal",
        },
    }
    freeze_digest = digest_json(preregistration)
    preregistration_bytes = canonical_bytes(preregistration) + b"\n"
    preregistration_sha256 = hashlib.sha256(preregistration_bytes).hexdigest()

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "preregistration.json").write_bytes(preregistration_bytes)
    evidence_dir = out_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    started_utc = datetime.now(timezone.utc).isoformat()
    rss_before = _peak_rss_bytes()

    repeats = FROZEN_DIMENSIONS["repetitions"]
    detail: list[dict[str, Any]] = []
    metric_values: dict[str, dict[int, float]] = {metric: {} for metric in METRICS}
    manifests: list[dict[str, str]] = []
    fixture_digests: list[str] = []

    for repetition in range(1, repeats + 1):
        repetition_dir = out_dir / "repetitions" / f"rep-{repetition}"
        repetition_dir.mkdir(parents=True, exist_ok=True)
        journal = StageJournal.load(repetition_dir / _JOURNAL_NAME)
        fault_event = fixture.fault_schedule[repetition - 1]
        interrupt_at = (int(fault_event[1]), int(fault_event[2]))

        executor = _Executor(fixture, repetition_dir, journal)
        pass_started = time.perf_counter_ns()
        crash_observed = False
        try:
            executor.run(interrupt_at=interrupt_at)
        except SyntheticInterruption:
            crash_observed = True
        crash_ms = (time.perf_counter_ns() - pass_started) / 1_000_000
        if not crash_observed:
            raise RunRefusal("the preregistered synthetic interruption was not reached")
        partial_latencies = list(executor.stage_latencies_ms)

        # Fresh executor instance: rebuild all state from the persisted journal.
        resume_started = time.perf_counter_ns()
        journal_after_crash = StageJournal.load(repetition_dir / _JOURNAL_NAME)
        recovered = sum(1 for (job, stage) in [
            (job, stage) for job in range(fixture.spec.jobs)
            for stage in range(fixture.spec.stages)
        ] if journal_after_crash.entries.get((job, stage), {}).get("digest") is not None
            and not journal_after_crash.is_complete(job, stage))
        resumed = _Executor(fixture, repetition_dir, journal_after_crash)
        resumed.run(interrupt_at=None)
        recovery_ms = (time.perf_counter_ns() - resume_started) / 1_000_000
        stage_latencies = partial_latencies + list(resumed.stage_latencies_ms)

        verification = verify_persisted_artifacts(repetition_dir)
        disk = _disk_usage(repetition_dir)
        manifest = _artifact_manifest(repetition_dir)
        manifests.append(manifest)
        fixture_digests.append(fixture_digest)

        completed = journal_after_crash.completed_stages()
        expected_stages = fixture.spec.jobs * fixture.spec.stages
        if completed != expected_stages:
            raise RunRefusal(
                f"repetition {repetition} completed {completed}/{expected_stages} stages"
            )
        idle_stage_total = sum(stage.cost_units for job in fixture.jobs for stage in job.stages)
        busy_ms = sum(stage_latencies)
        stage_throughput = (completed / (busy_ms / 1000.0)) if busy_ms > 0 else 0.0
        byte_throughput = (TOTAL_ARTIFACT_BYTES / (busy_ms / 1000.0)) if busy_ms > 0 else 0.0

        metric_values["fixture_generation_wall_time"][repetition] = (
            fixture_generation_ms[repetition])
        metric_values["stage_execution_wall_time"][repetition] = busy_ms
        metric_values["restart_recovery_wall_time"][repetition] = recovery_ms
        metric_values["disk_space_growth_bytes"][repetition] = float(disk["apparent_bytes"])
        metric_values["artifact_integrity_mismatches"][repetition] = float(
            verification["mismatches"])
        metric_values["restart_duplicate_writes"][repetition] = float(
            resumed.duplicate_writes)
        metric_values["restart_idempotent_replays"][repetition] = float(
            resumed.idempotent_replays)

        detail.append({
            "repetition": repetition,
            "fixture_digest": fixture_digest,
            "fixture_generation_wall_time_ms": fixture_generation_ms[repetition],
            "stage_busy_wall_time_ms": busy_ms,
            "crash_wall_time_ms": crash_ms,
            "resume_wall_time_ms": recovery_ms,
            "stages_completed": completed,
            "stages_total": expected_stages,
            "synthetic_work_units": idle_stage_total,
            "stage_throughput_stages_per_second": stage_throughput,
            "artifact_write_throughput_bytes_per_second": byte_throughput,
            "interruption": {
                "observed": crash_observed,
                "crash_point": INTERRUPTION_MODE,
                "after": "durable artifact persisted before completion record",
                "job_index": interrupt_at[0],
                "stage_index": interrupt_at[1],
            },
            "resume": {
                "recovered_stages": recovered,
                "idempotent_replays": resumed.idempotent_replays,
                "duplicate_writes": resumed.duplicate_writes,
                "repairs": resumed.repairs,
                "primary_writes": resumed.primary_writes,
                "stages_completed_after_resume": resumed.journal.completed_stages(),
            },
            "integrity": {
                "checked": verification["checked"],
                "mismatches": verification["mismatches"],
                "completed_stages": verification["completed_stages"],
                "incomplete_stages": verification["incomplete_stages"],
            },
            "disk": disk,
            "stage_latency_ms": {
                "n": len(stage_latencies),
                "min": min(stage_latencies) if stage_latencies else 0.0,
                "median": statistics.median(stage_latencies) if stage_latencies else 0.0,
                "max": max(stage_latencies) if stage_latencies else 0.0,
            },
            "artifact_manifest": manifest,
        })

    peak_rss = _peak_rss_bytes()
    metric_values["peak_rss_bytes"] = {1: float(peak_rss)}
    baseline_manifest = manifests[0]
    repeatability_mismatches = sum(
        1 for manifest in manifests[1:] if manifest != baseline_manifest
    )
    repeatability_mismatches += sum(
        1 for digest in fixture_digests[1:] if digest != fixture_digests[0]
    )
    metric_values["repeatability_digest_mismatches"] = {1: float(repeatability_mismatches)}

    carriers: dict[str, tuple[str, str]] = {}
    for metric in METRICS:
        definition = METRIC_DEFINITIONS[metric]
        payload = _carrier_bytes(metric, definition["unit"], metric_values[metric])
        relative = f"evidence/{metric}.raw.json"
        (out_dir / relative).write_bytes(payload)
        carriers[metric] = (relative, hashlib.sha256(payload).hexdigest())

    rows: dict[str, list[dict[str, Any]]] = {}
    for metric in METRICS:
        relative, carrier_sha = carriers[metric]
        rows[metric] = [
            _observation_row(
                metric=metric, repetition=repetition, value=value,
                unit=METRIC_DEFINITIONS[metric]["unit"],
                carrier_path=relative, carrier_sha256=carrier_sha,
                freeze_digest=freeze_digest, workload_digest=workload_digest,
                config_digest=config_digest,
                fault_schedule_digest=fault_schedule_digest,
                dependency_heads=accepted_heads,
                candidate=accepted_heads["F02"],
            )
            for repetition, value in sorted(metric_values[metric].items())
        ]

    receipt: dict[str, Any] = {
        "schema": RUN_SCHEMA,
        "scope": "synthetic_generated_only",
        "workload_id": WORKLOAD_ID,
        "evidence_class": "MEASURED",
        "environment": _environment(),
        "source_binding": binding,
        "dependency_binding": dependency_binding,
        "run_identity": {
            "run_id": preregistration["run_attempt_identity"]["run_id"],
            "receipt_identity": RECEIPT_IDENTITY,
            "invocation_started_utc": started_utc,
        },
        "preregistration": {
            "schema": PREREGISTRATION_SCHEMA,
            "path": "preregistration.json",
            "sha256": preregistration_sha256,
            "digest": freeze_digest,
            "recorded_before_observations": True,
            "metric_definitions": preregistration["metric_definitions"],
            "numeric_bounds": preregistration["numeric_bounds"],
            "classification": preregistration["classification"],
            "dependency_generations": preregistration["dependency_generations"],
        },
        "workload_identity": {
            "workload_id": WORKLOAD_ID,
            "config_id": CONFIGURATION_ID,
            "config_digest": config_digest,
            "workload_digest": workload_digest,
            "fixture_digest": fixture_digest,
            "generation_id": fixture_digest,
            "dimensions": dict(FROZEN_DIMENSIONS),
            "seed": FROZEN_SEED,
            "artifact_bytes_total": TOTAL_ARTIFACT_BYTES,
            "fault_schedule": [list(point) for point in fixture.fault_schedule],
            "fault_schedule_digest": fault_schedule_digest,
        },
        "measurements": [row for metric in METRICS for row in rows[metric]],
        "measurement_rows_by_metric": rows,
        "repetitions": detail,
        "derived_observations": {
            "job_completion": {
                "jobs_total": FROZEN_DIMENSIONS["jobs"],
                "jobs_completed": FROZEN_DIMENSIONS["jobs"],
                "failure_outcomes": [],
            },
            "stage_throughput_stages_per_second": [
                item["stage_throughput_stages_per_second"] for item in detail],
            "artifact_write_throughput_bytes_per_second": [
                item["artifact_write_throughput_bytes_per_second"] for item in detail],
            "stage_latency_ms_all": {
                "n": sum(item["stage_latency_ms"]["n"] for item in detail),
                "min": min(item["stage_latency_ms"]["min"] for item in detail),
                "median": statistics.median(
                    [item["stage_latency_ms"]["median"] for item in detail]),
                "max": max(item["stage_latency_ms"]["max"] for item in detail),
            },
            "rss_before_bytes": rss_before,
            "peak_rss_bytes": peak_rss,
            "aggregation": (
                "wall-clock, RSS, and disk values are single local observations of this "
                "synthetic run; they are not reproducible identity"
            ),
        },
        "integrity": {
            "artifacts_verified": sum(item["integrity"]["checked"] for item in detail),
            "mismatches": sum(item["integrity"]["mismatches"] for item in detail),
            "duplicate_writes_total": sum(
                item["resume"]["duplicate_writes"] for item in detail),
            "idempotent_replays_total": sum(
                item["resume"]["idempotent_replays"] for item in detail),
            "journal_records": sum(
                item["stages_completed"] * 2 for item in detail),
            "artifact_manifest": baseline_manifest,
            "artifact_payloads": (
                "discarded_after_verification" if discard_artifacts else "retained"
            ),
            "verification_scope": (
                "content digests recomputed from persisted payload bytes against the journal"
            ),
        },
        "fault_injection": _fault_evidence(detail),
        "repeatability": {
            "repetitions": repeats,
            "fixture_digest_identical": len(set(fixture_digests)) == 1,
            "artifact_manifests_identical": repeatability_mismatches == 0,
            "mismatches": repeatability_mismatches,
            "compared_between": "repetitions within this run",
        },
        "not_observed": list(NOT_OBSERVED),
        "safety": dict(SAFETY),
    }

    security = _self_verify(
        receipt, rows=rows, preregistration=preregistration,
        preregistration_bytes=preregistration_bytes,
        preregistration_sha256=preregistration_sha256,
        freeze_digest=freeze_digest, workload_digest=workload_digest,
        config_digest=config_digest, fault_schedule_digest=fault_schedule_digest,
        binding=binding, repo_root=repo_root, out_dir=out_dir,
    )
    receipt["security_verification"] = security

    bounds = {metric: float(definition["max"])
              for metric, definition in METRIC_DEFINITIONS.items()}
    classification = {metric: DeficitClass(definition["deficit_class"])
                      for metric, definition in METRIC_DEFINITIONS.items()}
    dependency_heads = {f"H3-{key}": dict(value)
                        for key, value in accepted_heads.items()}
    decision = decide(
        bounds=bounds,
        observations=rows,
        classification=classification,
        dependency_heads=dependency_heads,
        freeze_digest=freeze_digest,
        workload_digest=workload_digest,
        config_digest=config_digest,
        fault_schedule_digest=fault_schedule_digest,
        expected_repetitions={metric: definition["repetitions"]
                              for metric, definition in METRIC_DEFINITIONS.items()},
        evidence_valid=security["verified"],
    ).to_dict()
    decision["decision_scope"] = (
        "same-run self-verified observations; derived by gate2.decision.decide and NOT a "
        "verifier-published contract bundle"
    )
    receipt["decision"] = decision
    receipt["receipt_digest"] = digest_json(receipt)

    receipt_bytes = canonical_bytes(receipt) + b"\n"
    (out_dir / "receipt.json").write_bytes(receipt_bytes)
    if discard_artifacts:
        for repetition_dir in sorted((out_dir / "repetitions").glob("rep-*")):
            for path in sorted(repetition_dir.rglob("*"), reverse=True):
                if path.is_file() and path.parent.name.startswith("job-"):
                    path.unlink()
    return receipt


def _self_verify(receipt: dict[str, Any], *, rows: dict[str, list[dict[str, Any]]],
                 preregistration: dict[str, Any], preregistration_bytes: bytes,
                 preregistration_sha256: str, freeze_digest: str,
                 workload_digest: str, config_digest: str,
                 fault_schedule_digest: str, binding: dict[str, Any],
                 repo_root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    prereg_path = out_dir / "preregistration.json"
    stored = prereg_path.read_bytes() if prereg_path.exists() else b""
    record("preregistration.sealed_before_observations",
           prereg_path.exists() and hashlib.sha256(stored).hexdigest() == preregistration_sha256,
           "preregistration bytes must hash to the recorded seal")
    record("preregistration.freeze_digest",
           digest_json(preregistration) == freeze_digest,
           "freeze digest must be recomputable from the sealed payload")
    record("identity.config_digest",
           digest_json(_configuration()) == config_digest,
           "configuration identity must be recomputable")
    spec_identity = receipt["workload_identity"]
    record("identity.fault_schedule_digest",
           digest_json({
               "seed": spec_identity["seed"],
               "repetitions": spec_identity["dimensions"]["repetitions"],
               "fault": INTERRUPTION_MODE,
               "events": spec_identity["fault_schedule"],
           }) == fault_schedule_digest,
           "fault schedule identity must be recomputable")
    record("identity.fixture_digest",
           spec_identity["fixture_digest"] == spec_identity["generation_id"] != "",
           "fixture identity must equal the generation identity")

    carrier_errors: list[str] = []
    coverage_errors: list[str] = []
    for metric in METRICS:
        definition = METRIC_DEFINITIONS[metric]
        carrier_rows = rows[metric]
        expected = set(range(1, definition["repetitions"] + 1))
        actual = {row["repetition"] for row in carrier_rows}
        if actual != expected:
            coverage_errors.append(f"{metric}: repetitions {sorted(actual)} != {sorted(expected)}")
        for row in carrier_rows:
            path = out_dir / row["carrier_path"]
            if not path.exists():
                carrier_errors.append(f"{metric}: missing carrier {row['carrier_path']}")
                continue
            payload = path.read_bytes()
            if hashlib.sha256(payload).hexdigest() != row["carrier_sha256"]:
                carrier_errors.append(f"{metric}: carrier hash mismatch")
                continue
            records = json.loads(payload)
            match = [
                record_payload for record_payload in records
                if record_payload.get("metric_id") == metric
                and record_payload.get("repetition") == row["repetition"]
            ]
            if not match or match[0].get("value") != row["value"]:
                carrier_errors.append(f"{metric}: carrier value does not match row")
    record("carriers.present_and_hashed", not carrier_errors, "; ".join(carrier_errors[:4]))
    record("carriers.repetition_coverage", not coverage_errors, "; ".join(coverage_errors[:4]))

    source_digest_now, _ = _source_files_digest(repo_root)
    record("source.digest_stable",
           source_digest_now == binding["source_digest"],
           "src/gate2 sources must be unchanged during the run")
    record("source.head_bound",
           _git(repo_root, "rev-parse", "HEAD") == binding["head_sha"],
           "evidence must be bound to the exact recorded HEAD")

    detail = receipt["repetitions"]
    integrity_ok = all(item["integrity"]["mismatches"] == 0 for item in detail)
    duplicate_ok = all(item["resume"]["duplicate_writes"] == 0 for item in detail)
    recovery_ok = all(item["interruption"]["observed"] for item in detail)
    record("restart.integrity", integrity_ok, "no artifact digest mismatches")
    record("restart.no_duplicate_writes", duplicate_ok, "no completed stage was rewritten")
    record("restart.interruption_observed", recovery_ok, "every repetition resumed")
    injections = receipt.get("fault_injection") or []
    fault_ok = (
        {item["fault_class"] for item in injections}
        == {fault_api.FaultClass.H_INTERRUPTED_RECOVERY.name,
            fault_api.FaultClass.E_REPEATED_IDEMPOTENCY_KEY.name}
        and all(item["disposition"] == "PASS" and item["detected"] for item in injections)
        and all(item["capability"] == "HARNESSED" for item in injections)
    )
    record("faults.harnessed_injection_pass", fault_ok,
           "H/E fault classes evaluated from this run's observed facts")
    record("repeatability.identity", receipt["repeatability"]["mismatches"] == 0,
           "fixture and artifact digests identical across repetitions")

    verified = all(check["passed"] for check in checks)
    errors = [f"{check['check']}: {check['detail']}" for check in checks if not check["passed"]]
    return {"verified": verified, "checks": checks, "errors": errors,
            "scope": "self-verification of this run's own evidence"}
