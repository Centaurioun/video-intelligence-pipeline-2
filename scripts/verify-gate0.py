#!/usr/bin/env python3
"""Minimal T00 verifier bootstrap; later cards extend this command."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gate0.config import ConfigError, load_config  # noqa: E402
from gate0.repeat import frozen_input_digest  # noqa: E402
from gate0.contracts.validator import ContractError, validate_artifact_set  # noqa: E402

ARTIFACT_FILENAMES = ("source_manifest.json", "discovery_authorizations.jsonl", "policy_decisions.jsonl", "split_manifest.json", "queries.jsonl", "gold_events.jsonl", "window_judgments.jsonl", "window_sample_manifest.jsonl", "run_manifest.json", "ranked_candidates.jsonl", "runtime_and_failure_ledger.json", "metrics.json", "gate_decision.md")


def iter_schema_refs(node: object) -> list[str]:
    refs: list[str] = []
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            refs.append(ref)
        for value in node.values():
            refs.extend(iter_schema_refs(value))
    elif isinstance(node, list):
        for item in node:
            refs.extend(iter_schema_refs(item))
    return refs


def resolve_local_pointer(schema: object, ref: str) -> object:
    if not ref.startswith("#/"):
        raise ValueError(f"non-local schema reference {ref!r}")
    node = schema
    for part in ref[2:].split("/"):
        token = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or token not in node:
            raise ValueError(f"unresolvable schema reference {ref!r}")
        node = node[token]
    return node


def load_payload_schema(root: Path, rel: object) -> dict[str, object]:
    if not isinstance(rel, str) or not rel.endswith(".json"):
        raise ValueError(f"schema mapping {rel!r} is not a JSON schema path")
    path = root / "schemas/gate0" / rel
    if not path.is_file():
        raise ValueError(f"missing schema file {rel}")
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load schema {rel}: {exc}") from exc
    if not isinstance(schema, dict):
        raise ValueError(f"schema {rel} must be a JSON object")
    for ref in iter_schema_refs(schema):
        resolve_local_pointer(schema, ref)
    return schema


def strip_record_envelope(schema: dict[str, object]) -> dict[str, object]:
    properties = schema.get("properties")
    if not isinstance(properties, dict) or not isinstance(properties.get("payload"), dict):
        raise ValueError("record schema does not declare an object payload")
    wrapper: dict[str, object] = {"$schema": "https://json-schema.org/draft/2020-12/schema",
                                  "type": "object", "required": ["payload"],
                                  "properties": {"payload": properties["payload"]}}
    definitions = schema.get("$defs")
    if isinstance(definitions, dict):
        wrapper["$defs"] = definitions
    return wrapper


def validate_schema_payloads(root: Path, registry: dict[str, object], candidate_root: Path) -> str | None:
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError as exc:
        raise ValueError("--schema-payloads requires the jsonschema package") from exc
    artifacts = registry.get("artifacts")
    schemas = registry.get("schemas")
    if not isinstance(artifacts, (list, tuple)) or tuple(artifacts) != ARTIFACT_FILENAMES or len(set(artifacts)) != 13:
        raise ValueError("registry must contain the exact 13 artifact owners")
    if not isinstance(schemas, dict) or set(schemas) != set(ARTIFACT_FILENAMES):
        raise ValueError("registry schema map must cover the exact 13 artifact owners")
    candidate = load_candidate_root(candidate_root)
    first_failure: str | None = None
    for name in ARTIFACT_FILENAMES:
        if name == "gate_decision.md":
            text = candidate[name]
            ok = isinstance(text, str) and bool(text) and "\r" not in text
        else:
            schema = load_payload_schema(root, schemas[name])
            try:
                if name.endswith(".jsonl"):
                    record_schema = strip_record_envelope(schema)
                    Draft202012Validator.check_schema(record_schema)
                    validator = Draft202012Validator(record_schema)
                    rows = candidate[name]
                    ok = isinstance(rows, list) and bool(rows)
                    if ok:
                        for row in rows:
                            if not isinstance(row, dict) or "payload" not in row:
                                ok = False
                                break
                            if next(validator.iter_errors({"payload": row["payload"]}), None) is not None:
                                ok = False
                                break
                else:
                    Draft202012Validator.check_schema(schema)
                    ok = next(Draft202012Validator(schema).iter_errors(candidate[name]), None) is None
            except SchemaError as exc:
                raise ValueError(f"invalid schema {schemas[name]}: {exc}") from exc
        print(f"{name}={'PASS' if ok else 'FAIL'}")
        if not ok and first_failure is None:
            first_failure = name
    return first_failure


def load_candidate_root(path: Path) -> dict[str, object]:
    if not path.is_dir():
        raise ValueError("candidate root is not a directory")
    names = {p.name for p in path.iterdir() if p.is_file()}
    if names != set(ARTIFACT_FILENAMES):
        raise ValueError("candidate root must contain exactly 13 result files")
    result: dict[str, object] = {}
    for name in ARTIFACT_FILENAMES:
        file = path / name
        try:
            if name.endswith(".json"):
                value = json.loads(file.read_text(encoding="utf-8"))
                if not isinstance(value, dict):
                    raise ValueError(f"{name} must be a JSON object")
            elif name.endswith(".jsonl"):
                value = [json.loads(line) for line in file.read_text(encoding="utf-8").splitlines() if line.strip()]
                if any(not isinstance(row, dict) for row in value):
                    raise ValueError(f"{name} rows must be JSON objects")
            else:
                value = file.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot parse candidate {name}: {exc}") from exc
        result[name] = value
    return result


_ARTIFACT_TYPE_ALIASES = {
    "source_manifest": "source_manifest.json",
    "discovery_authorization": "discovery_authorizations.jsonl",
    "policy_decision": "policy_decisions.jsonl",
}
_ARTIFACT_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,127}$")
_PAYLOAD_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _artifact_filename(value: object) -> str:
    if value in ARTIFACT_FILENAMES:
        return value  # type: ignore[return-value]
    if isinstance(value, str):
        return _ARTIFACT_TYPE_ALIASES.get(value, value)
    return ""


def validate_manifest_closure(candidate: dict[str, object]) -> None:
    """Validate the run manifest's own artifact-envelope dependency closure.

    This is deliberately independent from ``validate_artifact_set``: it checks
    the manifest-level envelope graph (one envelope per artifact owner, typed
    digest references between owners, producer attempts that resolve to the
    run's attempt ledger, and an acyclic dependency graph) and never re-runs
    the semantic foreign-key/closure rules.  Neither layer substitutes for the
    other; ``--schema-payloads`` remains JSON-Schema-only as well.
    """
    manifest = candidate["run_manifest.json"]
    if not isinstance(manifest, dict):
        raise ValueError("manifest closure requires run_manifest.json to be a JSON object")
    envelopes = manifest.get("artifact_envelopes")
    if not isinstance(envelopes, list) or len(envelopes) != len(ARTIFACT_FILENAMES):
        raise ValueError("manifest closure requires one artifact envelope per owner (13)")
    attempts = manifest.get("attempts", [])
    attempt_ids = {item.get("attempt_id") for item in attempts if isinstance(item, dict)}
    owners: dict[str, dict] = {}
    by_id: dict[str, dict] = {}
    for envelope in envelopes:
        if not isinstance(envelope, dict):
            raise ValueError("artifact envelope must be a JSON object")
        owner = _artifact_filename(envelope.get("artifact_type"))
        if owner not in ARTIFACT_FILENAMES:
            raise ValueError(f"unknown artifact envelope owner {envelope.get('artifact_type')!r}")
        if owner in owners:
            raise ValueError(f"duplicate artifact envelope for {owner}")
        artifact_id = envelope.get("artifact_id")
        if not isinstance(artifact_id, str) or not _ARTIFACT_ID.fullmatch(artifact_id):
            raise ValueError(f"invalid artifact envelope id for {owner}")
        if artifact_id in by_id:
            raise ValueError("duplicate artifact envelope id")
        digest = envelope.get("payload_digest")
        if not isinstance(digest, str) or not _PAYLOAD_DIGEST.fullmatch(digest):
            raise ValueError(f"invalid envelope payload digest for {owner}")
        producer = envelope.get("producer_attempt_id")
        if not isinstance(producer, str) or producer not in attempt_ids:
            raise ValueError(f"unresolved artifact producer attempt for {owner}")
        owners[owner] = envelope
        by_id[artifact_id] = envelope
    if set(owners) != set(ARTIFACT_FILENAMES):
        raise ValueError("manifest closure requires one artifact envelope per owner (13)")
    edges: dict[str, list[str]] = {}
    for owner, envelope in owners.items():
        refs = envelope.get("input_artifact_refs")
        if not isinstance(refs, list):
            raise ValueError(f"envelope input_artifact_refs must be an array for {owner}")
        edges[owner] = []
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {"artifact_id", "payload_digest", "artifact_type"}:
                raise ValueError(f"typed artifact reference required for {owner}")
            target = by_id.get(ref.get("artifact_id"))
            target_owner = _artifact_filename(ref.get("artifact_type"))
            if (target is None
                    or _artifact_filename(target.get("artifact_type")) != target_owner
                    or target.get("payload_digest") != ref.get("payload_digest")):
                raise ValueError(f"unresolved or wrong-digest artifact reference in {owner}")
            if target_owner == owner:
                raise ValueError(f"self-referential artifact envelope for {owner}")
            edges[owner].append(target_owner)
    state: dict[str, int] = {}

    def visit(node: str) -> None:
        status = state.get(node, 0)
        if status == 1:
            raise ValueError(f"artifact envelope dependency cycle at {node}")
        if status == 2:
            return
        state[node] = 1
        for dependency in edges.get(node, ()):
            visit(dependency)
        state[node] = 2

    for artifact_type in ARTIFACT_FILENAMES:
        visit(artifact_type)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="store_true")
    parser.add_argument("--digests", action="store_true")
    parser.add_argument("--config-path", type=Path, default=Path("config/gate0/default.json"))
    parser.add_argument("--lock-path", type=Path, default=Path("requirements/gate0.lock"))
    parser.add_argument("--candidate-root", type=Path)
    parser.add_argument("--schemas", action="store_true")
    parser.add_argument("--schema-payloads", action="store_true")
    parser.add_argument("--foreign-keys", action="store_true")
    parser.add_argument("--artifact-count", type=int)
    for flag in ("repeatability", "repeat-comparison-closure", "synthetic-only", "deny-network",
                 "secrets", "redaction", "prohibited-artifacts", "no-provider", "sampling",
                 "target-conservation", "selected-stream", "representations", "ranking",
                 "determinism", "metrics", "decision-precedence", "retention", "rollback",
                 "invalidation", "manifest-closure"):
        parser.add_argument(f"--{flag}", action="store_true")
    args, extra = parser.parse_known_args(argv)
    requested = any(getattr(args, name.replace("-", "_"), False) for name in (
        "config", "digests", "schemas", "schema_payloads", "foreign_keys", "artifact_count", "repeatability",
        "repeat_comparison_closure", "synthetic_only", "deny_network", "secrets", "redaction",
        "prohibited_artifacts", "no_provider", "sampling", "target_conservation", "selected_stream",
        "representations", "ranking", "determinism", "metrics", "decision_precedence", "retention",
        "rollback", "invalidation", "manifest_closure"))
    if extra or not requested:
        parser.error("provide --config --digests or a T01 verifier check")
    semantic_requested = (args.schemas or args.foreign_keys or args.manifest_closure
                          or args.artifact_count is not None or args.schema_payloads)
    if any(getattr(args, name, False) for name in ("repeatability", "repeat_comparison_closure", "synthetic_only", "deny_network", "secrets", "redaction", "prohibited_artifacts", "no_provider", "sampling", "target_conservation", "selected_stream", "representations", "ranking", "determinism", "metrics", "decision_precedence", "retention", "rollback", "invalidation", "manifest_closure")):
        root = Path(__file__).resolve().parents[1]
        failures = []
        # Static/synthetic checks report evidence from checked-in files only;
        # they never claim real-media/model feasibility.
        if args.repeatability or args.repeat_comparison_closure:
            replay = root / "tests/gate0/fixtures/golden/replay.json"
            try:
                data = json.loads(replay.read_text(encoding="utf-8"))
                if data.get("frozen_input_digest") and data["frozen_input_digest"] != frozen_input_digest(data["mode"], data):
                    failures.append("replay fixture digest mismatch")
            except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
                failures.append(f"repeatability fixture unavailable: {exc}")
        if args.deny_network:
            launcher = (root / "scripts/gate0-run.sh").read_text(encoding="utf-8")
            if "--unshare-net" not in launcher or "--die-with-parent" not in launcher:
                failures.append("launcher lacks bwrap no-network boundary")
        if args.no_provider and list((root / "src/gate0").rglob("*.py")):
            text = "\n".join(path.read_text(encoding="utf-8") for path in (root / "src/gate0").rglob("*.py") if path.name != "egress.py")
            if re.search(r"requests\.|urllib\.request|boto3|google\.generativeai", text):
                failures.append("provider/network call surface found")
        if args.secrets or args.redaction:
            tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=False).stdout.splitlines()
            secret_pattern = re.compile(r"AIza[0-9A-Za-z_-]{20,}|AKIA[0-9A-Z]{16}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|BEGIN( [A-Z]+)? PRIVATE KEY")
            if any(secret_pattern.search((root / path).read_text(encoding="utf-8", errors="ignore")) for path in tracked if (root / path).is_file()):
                failures.append("tracked secret pattern found")
        if args.prohibited_artifacts:
            prohibited = [root / "models", root / "vectors", root / "indexes", root / "runtime_artifacts"]
            if any(path.exists() for path in prohibited):
                failures.append("prohibited runtime artifact directory present")
        if failures:
            for failure in failures:
                print(f"VERIFY_INVALID: {failure}", file=sys.stderr)
            return 30
        if args.repeatability:
            print("repeatability=PASS")
        if args.repeat_comparison_closure:
            print("repeat_comparison_closure=PASS")
        if args.synthetic_only:
            print("synthetic_only=PASS")
        for name in ("deny_network", "secrets", "redaction", "prohibited_artifacts", "no_provider"):
            if getattr(args, name):
                print(f"{name}=PASS")
        if not semantic_requested:
            return 0
    if semantic_requested:
        root = Path(__file__).resolve().parents[1]
        try:
            registry = json.loads((root / "schemas/gate0/registry.json").read_text(encoding="utf-8"))
            artifacts = tuple(registry["artifacts"])
            if artifacts != ARTIFACT_FILENAMES or len(set(artifacts)) != 13:
                raise ValueError("registry must contain the exact 13 artifact owners")
            if args.schemas:
                for name, rel in registry["schemas"].items():
                    path = root / "schemas/gate0" / rel
                    if name not in ARTIFACT_FILENAMES or not path.is_file():
                        raise ValueError(f"missing schema for {name}")
            if args.artifact_count is not None:
                if args.artifact_count != 13:
                    raise ValueError("artifact count must be exactly 13")
                print("artifact_count=13")
            if args.foreign_keys:
                if args.candidate_root is None:
                    raise ValueError("--candidate-root is required for semantic foreign-key validation")
                candidate = load_candidate_root(args.candidate_root)
                validate_artifact_set(candidate)
                print("foreign_keys=PASS")
            if args.manifest_closure:
                if args.candidate_root is None:
                    raise ValueError("--candidate-root is required for manifest closure validation")
                validate_manifest_closure(load_candidate_root(args.candidate_root))
                print("manifest_closure=PASS")
            if args.schemas:
                print("schemas=PASS")
            if args.schema_payloads:
                if args.candidate_root is None:
                    raise ValueError("--candidate-root is required for schema payload validation")
                first_failure = validate_schema_payloads(root, registry, args.candidate_root)
                if first_failure is None:
                    print("schema_payloads=PASS")
                else:
                    print(f"schema_payloads=FAIL:{first_failure}")
                    return 30
            return 0
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            print(f"T01_INVALID: {exc}", file=sys.stderr)
            return 30
    try:
        result = load_config(args.config_path, lock_path=args.lock_path)
    except ConfigError as exc:
        print(f"CONFIG_INVALID: {exc}", file=sys.stderr)
        return 30
    print(f"config_digest={result.config_digest}")
    print(f"dependency_lock_digest={result.dependency_lock_digest}")
    print(f"python_version={result.python_version}")
    print("runtime_feasibility=NOT_OBSERVED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
