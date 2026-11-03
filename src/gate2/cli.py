"""Deterministic command-line boundary for Gate-2 disposition evidence."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from gate0.identity import digest_json
from gate2.decision import DeficitClass, decide
from gate2.verify import verify_evidence


SAFETY = {
    "production_eligible": False,
    "gate_promotion": False,
    "mechanism_adopted": False,
}

# This is an internal interpretation of supported metric carriers. Callers may
# supply observations and bounds, but cannot select a deficit class/mechanism.
def _read_json(path: str) -> Any:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON input {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def _write_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True, indent=2))


def _frozen_inputs(contract: dict[str, Any], rows: list[Any]) -> tuple[
    dict[str, float], dict[str, int], dict[str, DeficitClass], dict[str, list[dict[str, Any]]]
]:
    """Translate a frozen contract and its observation rows for the decision engine."""
    definitions = contract.get("metric_definitions")
    if not isinstance(definitions, dict) or not isinstance(rows, list):
        raise ValueError("contract metric_definitions and evidence observations are required")
    bounds: dict[str, float] = {}
    repetitions: dict[str, int] = {}
    classes: dict[str, DeficitClass] = {}
    for metric, definition in definitions.items():
        if not isinstance(definition, dict):
            raise ValueError(f"frozen definition for {metric} must be an object")
        try:
            if "deficit_class" in definition:
                classes[metric] = DeficitClass(definition["deficit_class"])
            limits = definition.get("bounds", definition)
            bounds[metric] = float(limits["max"])
            repetitions[metric] = int(definition["repetitions"])
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise ValueError(f"invalid frozen definition for {metric}") from exc
    by_metric: dict[str, list[dict[str, Any]]] = {metric: [] for metric in definitions}
    for row in rows:
        if not isinstance(row, dict) or row.get("metric_id") not in by_metric:
            raise ValueError("observation references an undeclared metric")
        by_metric[row["metric_id"]].append(row)
    return bounds, repetitions, classes, by_metric


def _bind_rows(by_metric: dict[str, list[dict[str, Any]]], contract: dict[str, Any]) -> None:
    """Translate verifier-bound rows into the decision engine's H3 vocabulary."""
    for rows_for_metric in by_metric.values():
        for row in rows_for_metric:
            row["dependency_id"] = "+".join(
                f"H3-{part}" for part in row["dependency_id"].split("+")
            )
            # The decision engine binds each row to the candidate selected by
            # its final dependency. The verifier has already proved this
            # mapping equals the frozen evidence candidate.
            row["candidate_sha"] = row["candidate"]["sha"]
            row["candidate_tree"] = row["candidate"]["tree"]


def _derive_disposition(contract: dict[str, Any], rows: list[Any]) -> dict[str, Any]:
    bounds, repetitions, classes, by_metric = _frozen_inputs(contract, copy.deepcopy(rows))
    _bind_rows(by_metric, contract)
    return decide(
        bounds=bounds,
        observations=by_metric,
        classification=classes,
        dependency_heads={f"H3-{key}": value for key, value in contract["dependency_heads"].items()},
        freeze_digest=contract["freeze_digest"],
        workload_digest=contract["workload_digest"],
        config_digest=contract["config_digest"],
        fault_schedule_digest=contract["fault_schedule_digest"],
        expected_repetitions=repetitions,
        evidence_valid=True,
    ).to_dict()


def cmd_decide(args: argparse.Namespace) -> int:
    evidence = _read_json(args.input)
    contract = _read_json(args.contract)
    allowed_evidence = {
        "version", "dependency_heads", "preregistration_digest", "freeze_digest",
        "preregistration_path",
        "workload_digest", "config_digest", "fault_schedule_digest",
        "metric_definitions", "decision_digest", "candidate", "observations",
    }
    extra = set(evidence) - allowed_evidence
    if extra:
        raise ValueError(f"unknown evidence fields: {sorted(extra)}")
    rows = evidence.get("observations")
    # Fail early on undefined metrics so the verifier only sees decidable input.
    _frozen_inputs(contract, rows)
    # The verifier binds caller input to files beneath the evidence directory.
    verification = verify_evidence(evidence, contract, carrier_root=Path(args.input).resolve().parent,
                                    git_root=args.git_root)
    if not verification.get("verified"):
        _write_json({"verified": False, "errors": verification.get("errors", []), **SAFETY})
        return 2
    # Decision evaluation consumes verifier-bound rows.
    decision = _derive_disposition(contract, rows)
    # Publish a disposition only when the verifier binds the exact evidence,
    # frozen contract, and digest produced by that disposition.
    if decision.get("disposition_digest") != contract.get("decision_digest"):
        verification["verified"] = False
        verification.setdefault("errors", []).append("decision digest mismatch")
    if not verification.get("verified"):
        _write_json({"verified": False, "errors": verification.get("errors", []), **SAFETY})
        return 2
    result = {**decision, **SAFETY, "scope": "synthetic/generated"}
    result["mechanisms"] = [
        {"name": row["mechanism"], "eligible_later": row["eligible_for_later_evaluation"],
         "adopted": False}
        for row in result.get("mechanisms", [])
    ]
    _write_json(result)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    evidence = _read_json(args.input)
    contract = _read_json(args.contract)
    result = verify_evidence(evidence, contract, carrier_root=Path(args.input).resolve().parent,
                             git_root=args.git_root)
    # A decision digest is not self-certifying: recompute the disposition from
    # the verified evidence and require the frozen digest to match it.
    if result.get("verified") is True:
        try:
            recomputed = _derive_disposition(contract, evidence.get("observations"))
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            result["verified"] = False
            result.setdefault("errors", []).append(f"decision replay unavailable: {exc}")
        else:
            if recomputed.get("disposition_digest") != contract.get("decision_digest"):
                result["verified"] = False
                result.setdefault("errors", []).append("decision digest mismatch")
            else:
                result["decision_replayed"] = True
    result.update(SAFETY)
    _write_json(result)
    return 0 if result.get("verified") is True else 2


def cmd_run(args: argparse.Namespace) -> int:
    from gate2 import runner

    try:
        receipt = runner.execute_and_emit(
            args.out,
            expect_head=args.expect_head,
            discard_artifacts=args.discard_artifacts,
        )
    except runner.RunRefusal as exc:
        raise ValueError(str(exc)) from exc
    _write_json(receipt)
    return 0 if receipt.get("security_verification", {}).get("verified") is True else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gate2")
    sub = parser.add_subparsers(dest="command", required=True)
    decision = sub.add_parser("decide", help="derive a synthetic evidence disposition")
    decision.add_argument("--input", required=True, help="JSON observations and bounds")
    decision.add_argument("--contract", required=True, help="JSON frozen expected contract")
    decision.add_argument("--git-root", default=None,
                          help="repository root used for git-object contract provenance")
    decision.set_defaults(func=cmd_decide)
    verify = sub.add_parser("verify", help="verify evidence against a frozen contract")
    verify.add_argument("--input", required=True, help="JSON evidence envelope")
    verify.add_argument("--contract", required=True, help="JSON expected contract")
    verify.add_argument("--git-root", default=None,
                        help="repository root used for git-object contract provenance")
    verify.set_defaults(func=cmd_verify)
    run = sub.add_parser("run", help="execute the bounded synthetic workload and record measurements")
    run.add_argument("--out", required=True, help="evidence directory to create")
    run.add_argument("--expect-head", default=None,
                     help="refuse to run unless repository HEAD equals this commit")
    run.add_argument("--discard-artifacts", action="store_true",
                     help="delete artifact payloads after integrity verification")
    run.set_defaults(func=cmd_run)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"gate2: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
