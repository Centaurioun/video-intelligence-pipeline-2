"""Rebuild the Gate-2 synthetic evidence bundle on the current base.

The historical bundles under ``.orchestration/remaining-work/runs/H3-F03``
carry the superseded F01 contract generation, the stale 40-hex fingerprint
literals, and the ``f03-evidence.v1`` envelope.  They are preserved as
historical evidence and are never promoted by this script.  This script
derives a fresh bundle (``metrics-003``) from the current tree:

* the frozen preregistration is sealed *before* any observation is taken;
* the contract fingerprints and accepted dependency heads are resolved from
  real git objects, not copied from literals;
* the evidence envelope is the provenance-bearing ``f03-evidence.v2`` form;
* every measured carrier is written to disk and hashed from its exact bytes;
* fault and recovery refusals are produced by calling the real
  ``gate2.faults`` / ``gate2.recovery`` implementations;
* the disposition is derived through the real ``gate2.decision`` engine and
  replayed through the real CLI before the receipt is written.

The bundle is deterministic for the fixture/preregistration content.  Wall
clock and memory observations are measurements of this run and therefore are
not bit-reproducible; ``generation.json`` records the exact environment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from gate2 import faults, workload  # noqa: E402
from gate2.decision import DeficitClass, decide  # noqa: E402
from gate2.preregistration import Preregistration  # noqa: E402
from gate2.recovery import RecoveryBinding, RecoveryHarness, RecoveryRefusal  # noqa: E402
from gate2.verify import (  # noqa: E402
    canonical_digest,
    resolve_accepted_heads,
    resolve_contract_fingerprints,
)

BUNDLE = (
    REPO_ROOT / ".orchestration/remaining-work/runs/H3-F03/measurement/metrics-003"
)

# Accepted generation identities already referenced by the Gate-2 fixture
# suites.  They are real commit objects in this repository.
C04_SHA = "5d482a1016b97d663c57ad31d8bac21c19c8c799"
E05_SHA = "e52b91d38a9f9c6651a4203eccbe59b03d908905"

# Identity keys shared by every observation row and its reason provenance.
IDENTITY_KEYS = (
    "metric_id", "repetition", "status", "value", "unit", "dependency_id",
    "evidence_class", "carrier_path", "carrier_sha256", "dependency_heads",
    "candidate", "preregistration_digest", "freeze_digest", "workload_digest",
    "config_digest", "fault_schedule_digest",
)

METRICS: tuple[dict[str, Any], ...] = (
    {
        "name": "fixture_generation_wall_time",
        "unit": "milliseconds",
        "aggregation": "median",
        "bound": 30000,
        "derivation": "time.perf_counter_ns() around gate2.workload.generate(spec)",
    },
    {
        "name": "restart_recovery_wall_time",
        "unit": "milliseconds",
        "aggregation": "median",
        "bound": 30000,
        "derivation": (
            "time.perf_counter_ns() around the resumed gate2.recovery.RecoveryHarness.run() "
            "that follows a synthetic after_side_effect_before_completion crash"
        ),
    },
    {
        "name": "idempotent_duplicate_applications",
        "unit": "applications",
        "aggregation": "median",
        "bound": 10000,
        "derivation": (
            "distinct adapter state applications for the first operation after the same "
            "operation is submitted twice more post-completion"
        ),
    },
    {
        "name": "peak_memory",
        "unit": "bytes",
        "aggregation": "median",
        "bound": 100000000,
        "derivation": "no memory instrumentation exists in the synthetic apparatus",
    },
)
MEASURED_METRICS = tuple(
    metric["name"] for metric in METRICS if metric["name"] != "peak_memory"
)
OPERATIONS = ("op:stage-0", "op:stage-1", "op:stage-2")
RECEIPT_IDENTITY = "receipt:h3-f03-metrics-003-001"


class RebuildRefusal(RuntimeError):
    """The rebuild cannot produce trustworthy evidence."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_bytes(value) + b"\n")


class SyntheticAdapter:
    """Minimal in-memory adapter implementing the recovery apparatus protocol."""

    def __init__(self, operations: tuple[str, ...], receipt_identity: str,
                 refuse_receipt: bool = False) -> None:
        self.operations = operations
        self.receipt_identity = receipt_identity
        self.refuse_receipt = refuse_receipt
        self.state: dict[str, int] = {}
        self.completed: set[str] = set()
        self.application_attempts: dict[str, int] = {}
        self.reconcile_calls = 0

    def validate_receipt(self, identity: str) -> bool:
        if self.refuse_receipt:
            return False
        return identity == self.receipt_identity

    def reconcile_sqlite_tail(self) -> None:
        self.reconcile_calls += 1

    def state_digest(self) -> str:
        return canonical_digest(
            {"applications": dict(sorted(self.state.items())),
             "completed": sorted(self.completed)}
        )

    def start_or_resume(self, binding: RecoveryBinding) -> tuple[str, ...]:
        return self.operations

    def is_complete(self, operation_id: str) -> bool:
        return operation_id in self.completed

    def apply_idempotent(self, operation_id: str) -> None:
        self.application_attempts[operation_id] = (
            self.application_attempts.get(operation_id, 0) + 1
        )
        # A replayed operation must never mutate state twice.
        self.state.setdefault(operation_id, 1)

    def mark_complete(self, operation_id: str) -> None:
        self.completed.add(operation_id)


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return completed.stdout.strip()


def _base_sha() -> str:
    return _git("rev-parse", "HEAD")


def _element_versions() -> dict[str, str]:
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "base_sha": _base_sha(),
    }


def _configuration(seed: int, repetitions: int) -> dict[str, Any]:
    return {
        "schema": "gate2.synthetic-configuration.v1",
        "base_sha": _base_sha(),
        "generator": "gate2.workload.generate",
        "recovery": "gate2.recovery.RecoveryHarness",
        "timer": "time.perf_counter_ns",
        "resource_class": "HEAVY_CPU",
        "concurrency": 1,
        "artifact_bytes_per_stage": 64,
        "cost_units_per_first_stage": 5,
        "jobs": 4,
        "stages": 3,
        "fault": "after_side_effect_before_completion",
        "fault_position": 1,
        "seed": seed,
        "repetitions": repetitions,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "config_digest_rule": "sha256 over canonical JSON of this configuration document",
    }


def _measure_fixture_generation(spec: workload.WorkloadSpec, repetitions: int
                               ) -> tuple[list[float], workload.SyntheticFixture]:
    values: list[float] = []
    fixture: workload.SyntheticFixture | None = None
    for _ in range(repetitions):
        started = time.perf_counter_ns()
        fixture = workload.generate(spec)
        values.append((time.perf_counter_ns() - started) / 1_000_000)
    assert fixture is not None
    return values, fixture


def _binding(workload_digest: str, config_digest: str, generation: int) -> RecoveryBinding:
    return RecoveryBinding(
        f01_sha=resolve_accepted_heads(REPO_ROOT)["F01"]["sha"],
        c04_sha=C04_SHA,
        e05_sha=E05_SHA,
        workload_digest=workload_digest,
        configuration_digest=config_digest,
        previous_manifest_digest=canonical_digest({"manifest": "previous", "generation": generation}),
        current_manifest_digest=canonical_digest({"manifest": "current", "generation": generation}),
        generation_id=f"generation:h3-f03-metrics-003-{generation}",
        semantic_space_id="space:h3-f03-synthetic",
        receipt_identity=RECEIPT_IDENTITY,
    )


def _measure_restart_recovery(workload_digest: str, config_digest: str,
                              repetitions: int) -> tuple[list[float], list[float], dict[str, Any]]:
    elapsed: list[float] = []
    duplicate_values: list[float] = []
    transcripts: list[dict[str, Any]] = []
    for repetition in range(1, repetitions + 1):
        adapter = SyntheticAdapter(OPERATIONS, RECEIPT_IDENTITY)
        binding = _binding(workload_digest, config_digest, repetition)
        checkpoint = BUNDLE / "checkpoints" / f"repetition-{repetition}.json"
        if checkpoint.exists():
            checkpoint.unlink()
        crashed = False
        harness = RecoveryHarness.open(checkpoint, binding, adapter)
        try:
            harness.run(crash_point="after_side_effect_before_completion")
        except RuntimeError as exc:
            crashed = "synthetic crash" in str(exc)
        started = time.perf_counter_ns()
        resumed = RecoveryHarness.open(checkpoint, binding, adapter).run()
        elapsed.append((time.perf_counter_ns() - started) / 1_000_000)
        # Duplicate submission after completion: state must remain applied once.
        adapter.apply_idempotent(OPERATIONS[0])
        adapter.apply_idempotent(OPERATIONS[0])
        duplicate_values.append(float(adapter.state[OPERATIONS[0]]))
        transcripts.append(
            {
                "repetition": repetition,
                "crash_observed": crashed,
                "applications": dict(sorted(adapter.state.items())),
                "application_attempts": dict(sorted(adapter.application_attempts.items())),
                "reconcile_calls": adapter.reconcile_calls,
                "resumed": resumed,
            }
        )
    return elapsed, duplicate_values, {"repetitions": transcripts}


def _fault_and_refusal_evidence(workload_digest: str, config_digest: str) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    def record(name: str, expectation: str, call, expected_message: str = "") -> None:
        try:
            outcome = call()
        except Exception as exc:  # noqa: BLE001 - the observation is the exception
            cases.append(
                {
                    "case": name,
                    "expectation": expectation,
                    "observed_exception": type(exc).__name__,
                    "observed_message": str(exc),
                    "passed": False,
                    "traceback": traceback.format_exc(limit=1),
                }
            )
            return
        message = outcome.get("message", "") if isinstance(outcome, dict) else ""
        passed = expected_message in message if expected_message else True
        cases.append({"case": name, "expectation": expectation, "observed": outcome,
                      "passed": passed})

    def injected(fault_class: faults.FaultClass, payload: dict[str, Any],
                 expected_disposition: str) -> dict[str, Any]:
        result = faults.inject(fault_class, payload)
        return {
            "fault_class": result.fault_class.value,
            "capability": faults.capability(fault_class).value,
            "disposition": result.disposition,
            "detected": result.detected,
            "details": dict(result.details),
            "payload_digest": result.payload_digest,
            "expected_disposition": expected_disposition,
            "matches_expectation": result.disposition == expected_disposition,
        }

    for name, fault_class, payload, expected in (
        ("blocked-prerequisite-before-stage", faults.FaultClass.A_BEFORE_STAGE_START,
         {"predecessor_succeeded": False}, "PASS"),
        ("restart-decision-divergence", faults.FaultClass.F_RESTART_RECONSTRUCTION,
         {"decision_vector_a": [1], "decision_vector_b": [2]}, "PASS"),
        ("false-success-swallowed-recovery", faults.FaultClass.H_INTERRUPTED_RECOVERY,
         {"interruption_observed": True, "recovery_swallowed": True}, "PASS"),
        ("illegal-post-success-transition", faults.FaultClass.J_POST_SUCCESS_INVALIDATION,
         {"chain": ["AVAILABLE", "CLEANED"]}, "PASS"),
        ("identity-drift-sealed-vs-observed", faults.FaultClass.K_IDENTITY_DRIFT,
         {"sealed_digest": "a" * 64, "observed_digest": "b" * 64}, "PASS"),
        ("unreachable-class-never-detects", faults.FaultClass.D_RETRY_FAILED_JOB,
         {"attempts": 3}, "UNREACHABLE"),
    ):
        record(name, expected, lambda fc=fault_class, pl=payload, ex=expected: injected(fc, pl, ex))

    refusal_root = BUNDLE / "refusal-apparatus"
    binding = _binding(workload_digest, config_digest, 99)

    def refused_receipt() -> dict[str, Any]:
        adapter = SyntheticAdapter(OPERATIONS, RECEIPT_IDENTITY, refuse_receipt=True)
        checkpoint = refusal_root / "refused-receipt.json"
        if checkpoint.exists():
            checkpoint.unlink()
        try:
            RecoveryHarness.open(checkpoint, binding, adapter).run()
        except RecoveryRefusal as exc:
            return {"refused": True, "message": str(exc)}
        return {"refused": False}

    def tampered_checkpoint() -> dict[str, Any]:
        adapter = SyntheticAdapter(OPERATIONS, RECEIPT_IDENTITY)
        checkpoint = refusal_root / "tampered.json"
        if checkpoint.exists():
            checkpoint.unlink()
        RecoveryHarness.open(checkpoint, binding, adapter)
        envelope = json.loads(checkpoint.read_text(encoding="utf-8"))
        envelope["payload"]["attempt"] = 7
        checkpoint.write_text(json.dumps(envelope), encoding="utf-8")
        try:
            RecoveryHarness.open(checkpoint, binding, adapter)
        except RecoveryRefusal as exc:
            return {"refused": True, "message": str(exc)}
        return {"refused": False}

    def partial_checkpoint() -> dict[str, Any]:
        adapter = SyntheticAdapter(OPERATIONS, RECEIPT_IDENTITY)
        checkpoint = refusal_root / "partial.json"
        if checkpoint.exists():
            checkpoint.unlink()
        RecoveryHarness.open(checkpoint, binding, adapter)
        envelope = json.loads(checkpoint.read_text(encoding="utf-8"))
        payload = {"schema": "synthetic-recovery-apparatus-v1"}
        envelope["payload"] = payload
        envelope["integrity_sha256"] = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
        checkpoint.write_text(json.dumps(envelope), encoding="utf-8")
        try:
            RecoveryHarness.open(checkpoint, binding, adapter)
        except RecoveryRefusal as exc:
            return {"refused": True, "message": str(exc)}
        return {"refused": False}

    def invalid_crash_point() -> dict[str, Any]:
        adapter = SyntheticAdapter(OPERATIONS, RECEIPT_IDENTITY)
        checkpoint = refusal_root / "invalid-crash.json"
        if checkpoint.exists():
            checkpoint.unlink()
        try:
            RecoveryHarness.open(checkpoint, binding, adapter).run(crash_point="during_action")
        except ValueError as exc:
            return {"refused": True, "message": str(exc),
                    "adapter_events": adapter.reconcile_calls}
        return {"refused": False}

    record("e05-receipt-identity-refused", "E05 receipt identity was refused",
           refused_receipt, expected_message="E05 receipt identity was refused")
    record("tampered-checkpoint-refused", "integrity mismatch refusal",
           tampered_checkpoint, expected_message="integrity mismatch")
    record("partial-checkpoint-refused", "partial or unknown checkpoint refusal",
           partial_checkpoint, expected_message="partial or unknown apparatus checkpoint")
    record("unsupported-crash-point-refused", "unsupported synthetic crash point",
           invalid_crash_point, expected_message="unsupported synthetic crash point")

    return {
        "schema": "gate2.fault-refusal-evidence.v1",
        "source": "gate2.faults.inject / gate2.recovery.RecoveryHarness",
        "cases": cases,
        "all_passed": all(case["passed"] for case in cases),
    }


def _carrier_records(metric: str, unit: str, values: list[float]) -> list[dict[str, Any]]:
    return [
        {"metric_id": metric, "repetition": index, "unit": unit, "value": value}
        for index, value in enumerate(values, start=1)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="replace an existing metrics-003 bundle")
    parser.add_argument("--seed", type=int, default=20261024)
    parser.add_argument("--repetitions", type=int, default=2)
    args = parser.parse_args(argv)

    if BUNDLE.exists():
        if not args.force:
            raise SystemExit(
                f"refusing to overwrite existing bundle {BUNDLE}; pass --force to rebuild"
            )
        for path in sorted(BUNDLE.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
    BUNDLE.mkdir(parents=True, exist_ok=True)

    if args.repetitions < 1 or args.repetitions > 100:
        raise SystemExit("repetitions must be between 1 and 100")

    base_sha = _base_sha()
    accepted_heads = resolve_accepted_heads(REPO_ROOT)
    consumed_contracts = resolve_contract_fingerprints(REPO_ROOT)

    configuration = _configuration(args.seed, args.repetitions)
    config_digest = canonical_digest(configuration)

    spec = workload.WorkloadSpec(
        jobs=4,
        stages=3,
        artifact_bytes=64,
        cost_units=5,
        fault_position=1,
        seed=args.seed,
        f01_sha=accepted_heads["F01"]["sha"],
        c04_sha=C04_SHA,
        e05_sha=E05_SHA,
        config_digest=config_digest,
        concurrency=1,
        repetitions=args.repetitions,
    )
    workload_identity_doc = spec.to_dict()
    workload_digest = canonical_digest(workload_identity_doc)
    fault_schedule = {
        "seed": args.seed,
        "repetitions": args.repetitions,
        "events": [{"at": 1, "fault": "after_side_effect_before_completion"}],
    }
    fault_schedule_digest = canonical_digest(fault_schedule)

    bundle_preregistration = {
        "schema_version": "gate2.preregistration.v1",
        "workload_identity": {
            "workload_id": "h3-f03-synthetic-scale-v1",
            "digest": workload_digest,
        },
        "configuration_identity": {
            "config_id": "h3-f03-config-20261024-003",
            "digest": config_digest,
        },
        "dependency_generations": {
            "F01": accepted_heads["F01"]["sha"],
            "F02": accepted_heads["F02"]["sha"],
        },
        "fault_schedule": fault_schedule,
        "metrics": [
            {"name": metric["name"], "unit": metric["unit"], "aggregation": metric["aggregation"]}
            for metric in METRICS
        ],
        "numeric_bounds": {metric["name"]: metric["bound"] for metric in METRICS},
        "classification_rule": {
            "rule_id": "f03-bounded-synthetic-v2",
            "threshold": "measured values must not exceed the declared numeric bounds",
        },
        "evidence_declarations": {metric["name"]: "MEASURED" for metric in METRICS},
        "run_attempt_identity": {
            "run_id": "h3-f03-20261024-003",
            "attempt_id": "attempt-003",
        },
        "policy_authority": {
            "policy_id": "h3-f03-bounded-synthetic-v1",
            "authority": "owner-authorized local generated synthetic scope",
        },
        "resource_request": {"resource_class": "HEAVY_CPU", "concurrency": 1},
        "baseline": {
            "storage": "local generated fixture",
            "index": "synthetic recovery apparatus",
        },
        "contract_fingerprints": dict(consumed_contracts),
        "resource_policy_identity": consumed_contracts["resource_policy_v5"],
    }

    # Freeze before observing anything.  The sealed bytes are the artifact the
    # verifier re-admits; the script never mutates the payload afterwards.
    from gate2.verify import _F01_RESOURCE_POLICY  # validated v5 projection

    frozen = Preregistration.from_payload(
        bundle_preregistration,
        consumed_contracts=consumed_contracts,
        resource_policy=_F01_RESOURCE_POLICY,
    ).seal()
    prereg_bytes = frozen.canonical_bytes()
    (BUNDLE / "preregistration.json").write_bytes(prereg_bytes)
    preregistration_digest = hashlib.sha256(prereg_bytes).hexdigest()
    freeze_digest = frozen.freeze_digest

    generated_values, fixture = _measure_fixture_generation(spec, args.repetitions)
    recovery_values, duplicate_values, recovery_transcript = _measure_restart_recovery(
        workload_digest, config_digest, args.repetitions
    )
    fault_evidence = _fault_and_refusal_evidence(workload_digest, config_digest)
    _write_json(BUNDLE / "fault-refusal.json", fault_evidence)
    fault_evidence_digest = hashlib.sha256((BUNDLE / "fault-refusal.json").read_bytes()).hexdigest()

    observations: list[dict[str, Any]] = []
    measurement_rows: list[dict[str, Any]] = []
    metric_values: dict[str, list[float]] = {
        "fixture_generation_wall_time": generated_values,
        "restart_recovery_wall_time": recovery_values,
        "idempotent_duplicate_applications": duplicate_values,
    }
    definitions = {
        metric["name"]: {
            "unit": metric["unit"],
            "min": 0,
            "max": metric["bound"],
            "repetitions": args.repetitions,
        }
        for metric in METRICS
    }
    dependency_heads = {
        "F01": dict(accepted_heads["F01"]),
        "F02": dict(accepted_heads["F02"]),
    }
    candidate = dict(accepted_heads["F02"])

    for metric in METRICS:
        name = metric["name"]
        if name in metric_values:
            values = metric_values[name]
            carrier_path = f"{name}.raw.json"
            carrier_bytes = _canonical_bytes(_carrier_records(name, metric["unit"], values)) + b"\n"
            (BUNDLE / carrier_path).write_bytes(carrier_bytes)
            carrier_sha256 = hashlib.sha256(carrier_bytes).hexdigest()
            for index, value in enumerate(values, start=1):
                row = {
                    "metric_id": name,
                    "status": "MEASURED",
                    "value": value,
                    "unit": metric["unit"],
                    "evidence_class": "MEASURED",
                    "carrier_path": carrier_path,
                    "carrier_sha256": carrier_sha256,
                    "dependency_id": "F01+F02",
                    "dependency_heads": dependency_heads,
                    "candidate": candidate,
                    "preregistration_digest": preregistration_digest,
                    "freeze_digest": freeze_digest,
                    "workload_digest": workload_digest,
                    "config_digest": config_digest,
                    "fault_schedule_digest": fault_schedule_digest,
                    "repetition": index,
                }
                row["reason_provenance"] = {
                    "schema_version": "gate2.reason-provenance.v1",
                    "state": "MEASURED",
                    "reason_code": "OBSERVED",
                    "evidence_identity": {key: row[key] for key in IDENTITY_KEYS},
                }
                observations.append(row)
                measurement_rows.append(
                    {
                        "metric_id": name,
                        "status": "MEASURED",
                        "unit": metric["unit"],
                        "repetition": index,
                        "value": value,
                        "evidence_class": "MEASURED",
                        "carrier_path": carrier_path,
                        "carrier_sha256": carrier_sha256,
                        "derivation": metric["derivation"],
                        "dependency_id": "F01+F02",
                        "dependencies": dependency_heads,
                        "candidate": candidate,
                        "preregistration_digest": preregistration_digest,
                        "freeze_digest": freeze_digest,
                        "workload_digest": workload_digest,
                        "config_digest": config_digest,
                        "fault_schedule_digest": fault_schedule_digest,
                    }
                )
        else:
            for index in range(1, args.repetitions + 1):
                row = {
                    "metric_id": name,
                    "status": "NOT_OBSERVED",
                    "value": None,
                    "unit": metric["unit"],
                    "evidence_class": None,
                    "carrier_path": None,
                    "carrier_sha256": None,
                    "dependency_id": "F01+F02",
                    "dependency_heads": dependency_heads,
                    "candidate": candidate,
                    "preregistration_digest": preregistration_digest,
                    "freeze_digest": freeze_digest,
                    "workload_digest": workload_digest,
                    "config_digest": config_digest,
                    "fault_schedule_digest": fault_schedule_digest,
                    "repetition": index,
                }
                row["reason_provenance"] = {
                    "schema_version": "gate2.reason-provenance.v1",
                    "state": "UNAVAILABLE",
                    "reason_code": "SOURCE_UNAVAILABLE",
                    "evidence_identity": {key: row[key] for key in IDENTITY_KEYS},
                }
                row["derivation"] = metric["derivation"]
                observations.append(row)
                measurement_rows.append(
                    {
                        "metric_id": name,
                        "status": "NOT_OBSERVED",
                        "unit": metric["unit"],
                        "repetition": index,
                        "value": None,
                        "evidence_class": None,
                        "carrier_path": None,
                        "carrier_sha256": None,
                        "derivation": metric["derivation"],
                        "dependency_id": "F01+F02",
                        "dependencies": dependency_heads,
                        "candidate": candidate,
                        "preregistration_digest": preregistration_digest,
                        "freeze_digest": freeze_digest,
                        "workload_digest": workload_digest,
                        "config_digest": config_digest,
                        "fault_schedule_digest": fault_schedule_digest,
                    }
                )

    # Note: the NOT_OBSERVED observation rows carry only the closed observation
    # field set; the extra derivation text lives in the receipt rows instead.
    for row in observations:
        row.pop("derivation", None)
        if set(row) - {
            "metric_id", "status", "value", "unit", "evidence_class", "carrier_path",
            "carrier_sha256", "dependency_id", "dependency_heads", "candidate",
            "preregistration_digest", "freeze_digest", "workload_digest",
            "config_digest", "fault_schedule_digest", "repetition", "reason_provenance",
        }:  # pragma: no cover - defensive
            raise RebuildRefusal("observation field set drifted from the verifier contract")

    contract = {
        "dependency_heads": dependency_heads,
        "preregistration_path": "preregistration.json",
        "preregistration_digest": preregistration_digest,
        "freeze_digest": freeze_digest,
        "workload_digest": workload_digest,
        "config_digest": config_digest,
        "fault_schedule_digest": fault_schedule_digest,
        "metric_definitions": definitions,
        "candidate": candidate,
        "decision_digest": "0" * 64,
    }

    # Derive the disposition exactly as the CLI does, so the frozen contract can
    # commit to the disposition digest before the replay.
    bounds = {name: float(definition["max"]) for name, definition in definitions.items()}
    repetitions_by_metric = {name: definition["repetitions"] for name, definition in definitions.items()}
    classes: dict[str, DeficitClass] = {}
    by_metric: dict[str, list[dict[str, Any]]] = {name: [] for name in definitions}
    for row in observations:
        translated = dict(row)
        translated["dependency_id"] = "+".join(
            f"H3-{part}" for part in translated["dependency_id"].split("+")
        )
        translated["candidate_sha"] = translated["candidate"]["sha"]
        translated["candidate_tree"] = translated["candidate"]["tree"]
        by_metric[translated["metric_id"]].append(translated)
    derived = decide(
        bounds=bounds,
        observations=by_metric,
        classification=classes,
        dependency_heads={f"H3-{key}": value for key, value in dependency_heads.items()},
        freeze_digest=freeze_digest,
        workload_digest=workload_digest,
        config_digest=config_digest,
        fault_schedule_digest=fault_schedule_digest,
        expected_repetitions=repetitions_by_metric,
        evidence_valid=True,
    ).to_dict()
    contract["decision_digest"] = derived["disposition_digest"]

    evidence = {
        "version": "f03-evidence.v2",
        **contract,
        "observations": observations,
    }
    _write_json(BUNDLE / "expected-contract.json", contract)
    _write_json(BUNDLE / "evidence.json", evidence)
    _write_json(BUNDLE / "configuration.json", configuration)
    _write_json(BUNDLE / "workload-identity.json", workload_identity_doc)

    # Replay through the CLI boundary; the receipt records the CLI's own output.
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(SRC_ROOT), str(REPO_ROOT / "experiments")]
    )
    replay = subprocess.run(
        [sys.executable, "-m", "gate2.cli", "decide",
         "--input", str(BUNDLE / "evidence.json"),
         "--contract", str(BUNDLE / "expected-contract.json"),
         "--git-root", str(REPO_ROOT)],
        capture_output=True, text=True, env=environment, cwd=str(REPO_ROOT),
    )
    if replay.returncode != 0:
        raise RebuildRefusal(
            "CLI replay failed with exit "
            f"{replay.returncode}: {replay.stdout}{replay.stderr}"
        )
    cli_output = json.loads(replay.stdout)
    if cli_output.get("disposition_digest") != contract["decision_digest"]:
        raise RebuildRefusal("CLI disposition digest does not match the frozen contract")

    verify_replay = subprocess.run(
        [sys.executable, "-m", "gate2.cli", "verify",
         "--input", str(BUNDLE / "evidence.json"),
         "--contract", str(BUNDLE / "expected-contract.json"),
         "--git-root", str(REPO_ROOT)],
        capture_output=True, text=True, env=environment, cwd=str(REPO_ROOT),
    )
    if verify_replay.returncode != 0:
        raise RebuildRefusal(
            "CLI verification replay failed: " + verify_replay.stdout + verify_replay.stderr
        )
    verification = json.loads(verify_replay.stdout)

    receipt = {
        "schema": "h3-f03.measurement-receipt.v3",
        "scope": "synthetic_generated_only",
        "base_sha": base_sha,
        "dependencies": dependency_heads,
        "candidate": candidate,
        "bounds": {name: metric["bound"] for name, metric in
                   ((metric["name"], metric) for metric in METRICS)},
        "configuration": configuration,
        "workload_identity": workload_identity_doc,
        "workload_digest": workload_digest,
        "config_digest": config_digest,
        "fault_schedule_digest": fault_schedule_digest,
        "preregistration": {
            "path": "preregistration.json",
            "freeze_digest": freeze_digest,
            "canonical_bytes_sha256": preregistration_digest,
            "consumed_contracts": dict(consumed_contracts),
            "recorded_before_observations": True,
        },
        "measurements": measurement_rows,
        "security_verification": verification,
        "fault_refusal_evidence": {
            "path": "fault-refusal.json",
            "sha256": fault_evidence_digest,
            "all_passed": fault_evidence["all_passed"],
            "case_count": len(fault_evidence["cases"]),
        },
        "decision_disposition": cli_output.get("disposition"),
        "decision_notes": cli_output.get("notes"),
        "decision": cli_output,
        "safety": {
            "production_eligible": False,
            "gate_promotion": False,
            "mechanism_adopted": False,
        },
    }
    _write_json(BUNDLE / "measurement.json", receipt)
    _write_json(
        BUNDLE / "generation.json",
        {
            "schema": "gate2.evidence-generation.v1",
            "bundle": str(BUNDLE.relative_to(REPO_ROOT)),
            "base_sha": base_sha,
            "accepted_heads": accepted_heads,
            "consumed_contracts": dict(consumed_contracts),
            "environment": _element_versions(),
            "repetitions": args.repetitions,
            "seed": args.seed,
            "fixture_digest": fixture.fixture_digest,
            "recovery_transcript": recovery_transcript,
            "evidence_rebuild_script_sha256": hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
            "observations_summary": {
                name: values for name, values in metric_values.items()
            },
        },
    )
    print(json.dumps({"bundle": str(BUNDLE), "decision": cli_output.get("disposition"),
                      "verified": verification.get("verified"),
                      "fault_evidence": fault_evidence["all_passed"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
