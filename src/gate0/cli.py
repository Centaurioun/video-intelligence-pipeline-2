"""Minimal Gate-0 command boundary, including read-only repeat."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from gate0.repeat import frozen_input_digest
from gate0.identity import opaque_id
from gate0.failure import AttemptRecord
from gate0.stages.lifecycle import advance_stage
from gate0.run_state import stage_order_decision


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise ValueError("MALFORMED_MANIFEST")
    if not isinstance(value, dict):
        raise ValueError("MALFORMED_MANIFEST")
    return value


def _atomic_publish(manifest_path: Path, ledger_path: Path, manifest: dict, ledger: dict) -> None:
    """Publish the two boundary artifacts together, restoring the first on failure."""
    original_manifest = manifest_path.read_bytes()
    original_ledger = ledger_path.read_bytes()
    temp_manifest = temp_ledger = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=manifest_path.parent,
                                        prefix=".manifest-", suffix=".tmp", delete=False) as h:
            temp_manifest = Path(h.name); h.write(json.dumps(manifest, sort_keys=True, indent=2) + "\n"); h.flush(); os.fsync(h.fileno())
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=ledger_path.parent,
                                        prefix=".ledger-", suffix=".tmp", delete=False) as h:
            temp_ledger = Path(h.name); h.write(json.dumps(ledger, sort_keys=True, indent=2) + "\n"); h.flush(); os.fsync(h.fileno())
        os.replace(temp_manifest, manifest_path); temp_manifest = None
        os.replace(temp_ledger, ledger_path); temp_ledger = None
    except OSError:
        if temp_manifest: temp_manifest.unlink(missing_ok=True)
        if temp_ledger: temp_ledger.unlink(missing_ok=True)
        try:
            manifest_path.write_bytes(original_manifest)
        except OSError:
            pass
        raise


def _preflight_binding(run: Path, config_path: Path, run_id: str) -> tuple[int, dict[str, object]]:
    """Validate child attestation and persist its deny-boundary evidence."""
    from gate0.launcher_attestation import decode_attestation, sentinel_ledger_events
    try:
        manifest_path, ledger_path = run / "run_manifest.json", run / "runtime_and_failure_ledger.json"
        manifest = _load_json(manifest_path)
        ledger = _load_json(ledger_path)
        config = _load_json(config_path)
        sandbox_config = config["sandbox"]
        attestation_json = os.environ.get("GATE0_SANDBOX_ATTESTATION_JSON")
        if not attestation_json or os.environ.get("GATE0_CHILD_NETWORK_SENTINEL") != "1":
            raise ValueError("SANDBOX_ATTESTATION")
        attestation = decode_attestation(attestation_json)
        observed = attestation.to_dict()
        # Host binary identity is observed at the boundary and may be NOT_OBSERVED;
        # policy shape and digests remain config-bound.
        for key in ("read_only_mounts", "writable_mounts", "clearenv", "net_unshared",
                    "child_network_sentinel", "argv_digest", "mount_policy_digest"):
            if observed.get(key) != sandbox_config.get(key):
                raise ValueError("SANDBOX_ATTESTATION")
        policy_ids = manifest.get("policy_decision_ids")
        policy_id = policy_ids[-1] if isinstance(policy_ids, list) and policy_ids else "policy_unknown"
        attempt_id = "attempt_preflight"
        events = []
        for event in sentinel_ledger_events(run_id=run_id, attempt_id=attempt_id,
                 policy_decision_id=policy_id, egress_manifest_digest=config["policy"]["egress_manifest_digest"],
                 now="1970-01-01T00:00:00Z"):
            row = event.copy()
            row.update({"event_type": "EGRESS_BLOCKED", "affected_refs": [],
                        "reason": "child network denied", "occurred_at": "1970-01-01T00:00:00Z"})
            events.append(row)
        current = ledger.get("events")
        if not isinstance(current, list):
            raise ValueError("EGRESS_SENTINEL")
        ledger["events"] = [*current, *events]
        manifest["sandbox"] = observed
        _atomic_publish(manifest_path, ledger_path, manifest, ledger)
        return 20, {"command": "preflight", "status": "NOT_OBSERVED", "evidence_state": "NOT_OBSERVED"}
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError):
        return 20, {"command": "preflight", "status": "BLOCKED_PREREQUISITE", "reason": "SANDBOX_ATTESTATION"}


def _repeat_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--run", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=("frozen-index", "full-pipeline"), required=True)
    parser.add_argument("--predecessor-run-id", required=True)
    parser.add_argument("--frozen-input-digest", required=True)
    return parser


def _stage_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    for name in ("run", "config", "input-root", "output-root", "run-id"):
        parser.add_argument(f"--{name}", required=True)
    return parser


def _evaluate_parser() -> argparse.ArgumentParser:
    """T08 evaluate contract: the reviewer input path is the only extra option."""
    parser = _stage_parser()
    parser.add_argument("--review-input", required=True)
    return parser


def _repeat(argv: list[str]) -> int:
    # argparse accepts repeated options; the exact contract permits each once.
    names = {"--mode", "--predecessor-run-id", "--frozen-input-digest", "--run", "--config", "--input-root", "--output-root", "--run-id"}
    if any(argv.count(name) != 1 for name in names):
        return 40
    try:
        args = _repeat_parser().parse_args(argv)
    except SystemExit:
        return 40
    digest = args.frozen_input_digest
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        return 20
    run = Path(args.run).resolve()
    output_root = Path(args.output_root).resolve()
    if args.predecessor_run_id != args.run_id or run != output_root / args.run_id:
        return 20
    manifest_path = run / "run_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 20
    if manifest.get("run_id") != args.predecessor_run_id or manifest.get("status") != "REPORTED":
        return 20
    frozen = manifest.get("frozen_input")
    if not isinstance(frozen, dict) or any(manifest.get(key) != frozen.get(key) for key in
                                           ("source_revision_ids", "sample_manifest_digest",
                                            "representation_digests", "ranking_digest",
                                            "metrics_digest", "config_digest")):
        return 20
    try:
        expected = frozen_input_digest(args.mode, manifest)
    except (TypeError, ValueError):
        return 20
    frozen_digests = manifest.get("frozen_input_digests", {})
    canonical_digest = frozen_digests.get(args.mode) if isinstance(frozen_digests, dict) else None
    if canonical_digest is None and args.mode == "frozen-index":
        canonical_digest = manifest.get("frozen_input_digest")
    if digest != expected or canonical_digest != digest:
        return 20
    comparisons = manifest.get("repeat_comparisons", [])
    if not isinstance(comparisons, list):
        return 20
    comparison_required = {"comparison_id", "attempt_id", "mode", "expected_input_digest", "observed_input_digest", "equal", "evidence_state", "source_revision_ids", "metrics_digest", "created_at", "first_difference"}
    for comparison in comparisons:
        if not isinstance(comparison, dict) or set(comparison) != comparison_required:
            return 20
        if (comparison.get("mode") == args.mode and
                comparison.get("expected_input_digest") == digest and
                comparison.get("observed_input_digest") == digest):
            print(json.dumps({"command": "repeat", "mode": args.mode, "run_id": args.run_id,
                              "status": "EQUAL", "evidence_state": comparison.get("evidence_state", "MEASURED")}, sort_keys=True))
            return 0
    if not isinstance(comparisons, list):
        return 20
    comparison = {
        "comparison_id": opaque_id("comparison", {"run_id": args.run_id, "mode": args.mode, "digest": digest}),
        "attempt_id": opaque_id("attempt", {"run_id": args.run_id, "stage": "repeat", "digest": digest}),
        "mode": args.mode, "expected_input_digest": digest, "observed_input_digest": digest,
        "equal": True, "evidence_state": "MEASURED",
        "source_revision_ids": manifest.get("source_revision_ids", []),
        "metrics_digest": manifest.get("metrics_digest", "0" * 64),
        "created_at": "1970-01-01T00:00:00Z", "first_difference": None,
    }
    config_digest = manifest.get("config_digest")
    target_set_digest = manifest.get("sample_manifest_digest")
    tool_environment_digest = manifest.get("runtime", {}).get("tool_environment_digest", "0" * 64)
    if not all(isinstance(value, str) and len(value) == 64 for value in (config_digest, target_set_digest, tool_environment_digest)):
        return 20
    attempt = AttemptRecord.create(args.run_id, "repeat", digest, config_digest, tool_environment_digest,
                                   target_set_digest, attempt_id=comparison["attempt_id"], stage_status="SUCCEEDED", exit_code=0)
    try:
        running = advance_stage(args.run_id, attempt.attempt_id, "repeat", "PLANNED", "RUNNING", digest, config_digest)
        terminal = advance_stage(args.run_id, attempt.attempt_id, "repeat", "RUNNING", "SUCCEEDED", digest, config_digest)
    except ValueError:
        return 20
    manifest["attempts"] = [*manifest.get("attempts", []), attempt.to_dict()]
    manifest["stage_transitions"] = [*manifest.get("stage_transitions", []), running.to_dict(), terminal.to_dict()]
    manifest["repeat_comparisons"] = [*comparisons, comparison]
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=run, prefix=".repeat-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, manifest_path)
    except OSError:
        if "temporary" in locals():
            temporary.unlink(missing_ok=True)
        return 40
    print(json.dumps({"command": "repeat", "mode": args.mode, "run_id": args.run_id, "status": "EQUAL", "evidence_state": "MEASURED"}, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if argv is None else argv)
    legal = ("prepare", "inventory", "split", "label", "preflight", "extract", "embed", "rank", "evaluate", "report", "repeat")
    if not values or values[0] not in legal:
        return 40
    if values[0] != "repeat":
        if any(flag in values[1:] for flag in ("--stage", "--repeat", "--mode")):
            return 40
        stage = values[0]
        if stage == "evaluate":
            # Reviewer input structure is contract-invalid protocol (30), not a
            # generic usage error (40); repeated/missing/extra options are 30.
            if values[1:].count("--review-input") != 1:
                return 30
            try:
                args = _evaluate_parser().parse_args(values[1:])
            except SystemExit:
                return 30
        else:
            try:
                args = _stage_parser().parse_args(values[1:])
            except SystemExit:
                return 40
        run = Path(args.run).resolve()
        output_root = Path(args.output_root).resolve()
        if run != output_root / args.run_id:
            return 20
        # Gate-0 D-1: an authorized-local declaration is a distinct, explicitly
        # non-executable mode.  Refuse it before reading the run manifest, the
        # config, or dispatching a stage, and never fall back to synthetic/media.
        from gate0 import execution
        input_root = Path(args.input_root)
        if execution.has_authorized_local_input(input_root):
            print(json.dumps(execution.authorized_local_refusal(stage=stage, input_root=input_root),
                             sort_keys=True))
            return 20
        manifest = None
        if stage != "prepare":
            try:
                manifest = _load_json(run / "run_manifest.json")
            except ValueError:
                return 20
        try:
            decision = stage_order_decision(stage, manifest)
        except ValueError:
            return 40
        if not decision.allowed:
            print(json.dumps({"command": stage, "status": "BLOCKED_PREREQUISITE",
                              "reason": decision.reason, "predecessor": decision.predecessor}, sort_keys=True))
            return 20
        from gate0 import execution
        if execution.has_synthetic_input(input_root) or execution.has_media_input(input_root):
            try:
                code, projection = execution.execute_stage(
                    stage, run=run, config_path=Path(args.config), input_root=input_root,
                    output_root=output_root, run_id=args.run_id,
                    review_input=Path(args.review_input) if stage == "evaluate" else None,
                )
            except FileNotFoundError:
                pass
            else:
                print(json.dumps(projection, sort_keys=True))
                return code
        if stage == "preflight":
            code, projection = _preflight_binding(run, Path(args.config), args.run_id)
            print(json.dumps(projection, sort_keys=True))
            return code
        print(json.dumps({"command": stage, "status": "NOT_OBSERVED", "evidence_state": "NOT_OBSERVED"}, sort_keys=True))
        return 20
    return _repeat(values[1:])


if __name__ == "__main__":
    raise SystemExit(main())
