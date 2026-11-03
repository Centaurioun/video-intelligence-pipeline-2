"""Regression tests for verifier payload-vs-schema validation.

The Gate-0 verifier used to check only that ``schemas/gate0/*.json`` files
exist.  ``--schema-payloads`` closes that hole by validating each produced
artifact payload against its checked-in closed schema.

These tests drive the real deterministic synthetic pipeline once (module
fixture, in-process ``gate0.execution.execute_stage``), then prove:

* the produced artifact set is payload-schema clean (13/13 PASS) and agrees
  exactly with an independent ``jsonschema`` oracle over the same run, so the
  verifier is not silently skipping validation;
* a schema-minimal payload set synthesized from the *schemas alone* also
  passes, so the closure above is not an artifact of copying produced files;
* a flipped required field, an unknown property, an unknown ledger event type,
  a malformed payload and a duplicated manifest record each fail exactly the
  named artifact;
* a candidate root carrying an extra/unknown file is refused;
* ``--schemas`` and the existing verifier surface are unchanged.

The Gate-0 schema/media closure (2026-10-25) replaced the contract-audit
failure set recorded here historically.  The audited closed set is now empty;
that is an explicit recorded expectation, not a blanket relaxation.
No real corpus, model, network or provider call is used.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = REPO_ROOT / "tests/gate0/fixtures/synthetic-input"
REVIEW_ROOT = REPO_ROOT / "tests/gate0/fixtures/review-input"
SCHEMA_ROOT = REPO_ROOT / "schemas/gate0"
VERIFIER = REPO_ROOT / "scripts/verify-gate0.py"

if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
if str(FIXTURE_ROOT) not in sys.path:
    sys.path.insert(0, str(FIXTURE_ROOT))

import generate  # noqa: E402
import jsonschema  # noqa: E402
from gate0 import execution  # noqa: E402

ARTIFACT_FILENAMES = (
    "source_manifest.json", "discovery_authorizations.jsonl", "policy_decisions.jsonl",
    "split_manifest.json", "queries.jsonl", "gold_events.jsonl", "window_judgments.jsonl",
    "window_sample_manifest.jsonl", "run_manifest.json", "ranked_candidates.jsonl",
    "runtime_and_failure_ledger.json", "metrics.json", "gate_decision.md",
)
STAGES = ("prepare", "inventory", "split", "label", "preflight", "extract", "embed", "rank")
RUN_ID = "run_synthetic_e2e"

# Historical contract-audit evidence (temp/contract-analysis/REPORT.md) named
# these artifacts as closure-red on the executable path.  The 2026-10-25
# Gate-0 closure (D1-D8) fixed every producer/schema delta, so the audited
# set is now empty.  Movement is reported by the test log, never asserted
# silently: if a future change reintroduces drift this comparison fails.
AUDIT_CONTRACT_AUDIT_FAILURES = frozenset({
    "source_manifest.json",
    "split_manifest.json",
    "policy_decisions.jsonl",
    "window_sample_manifest.jsonl",
    "run_manifest.json",
    "ranked_candidates.jsonl",
    "runtime_and_failure_ledger.json",
    "metrics.json",
})
AUDITED_CLOSED_FAILURES: frozenset[str] = frozenset()

_PATTERN_SAMPLES = {
    r"^[a-z0-9][a-z0-9_-]{0,127}$": "a",
    r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$": "a",
    r"^[0-9a-f]{64}$": "0" * 64,
    r"^[a-f0-9]{64}$": "0" * 64,
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$": "2026-01-01T00:00:00Z",
}

_TMP: Path
_RUN_DIR: Path
_MINIMAL_ROOT: Path
_ORACLE_FAILURES: set[str]
_REVIEW_INPUT: Path


# ---------------------------------------------------------------------------
# verifier driver
# ---------------------------------------------------------------------------

def _verifier(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run([sys.executable, str(VERIFIER), *args], cwd=REPO_ROOT, env=env,
                          capture_output=True, text=True, check=False)


def _artifact_statuses(stdout: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for line in stdout.splitlines():
        name, separator, status = line.partition("=")
        if separator and name in ARTIFACT_FILENAMES:
            statuses[name] = status
    return statuses


def _final_line(stdout: str) -> str:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


# ---------------------------------------------------------------------------
# independent oracle: what *should* fail, computed from payloads + schemas
# without sharing any verifier code, so verifier wiring/order/exit behaviour is
# cross-checked rather than assumed.
# ---------------------------------------------------------------------------

def _oracle_payload_failures(run_dir: Path) -> set[str]:
    registry = json.loads((SCHEMA_ROOT / "registry.json").read_text(encoding="utf-8"))
    failures: set[str] = set()
    for name in ARTIFACT_FILENAMES:
        artifact_path = run_dir / name
        if name == "gate_decision.md":
            text = artifact_path.read_text(encoding="utf-8")
            if not text or "\r" in text:
                failures.add(name)
            continue
        schema = json.loads((SCHEMA_ROOT / registry["schemas"][name]).read_text(encoding="utf-8"))
        if name.endswith(".jsonl"):
            record_schema = {
                "type": "object",
                "required": ["payload"],
                "properties": {"payload": schema["properties"]["payload"]},
            }
            if "$defs" in schema:
                record_schema["$defs"] = schema["$defs"]
            validator = jsonschema.Draft202012Validator(record_schema)
            rows = [json.loads(line) for line in artifact_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()]
            bad = not rows or any(
                next(validator.iter_errors({"payload": row["payload"]}), None) is not None
                for row in rows
            )
        else:
            validator = jsonschema.Draft202012Validator(schema)
            document = json.loads(artifact_path.read_text(encoding="utf-8"))
            bad = next(validator.iter_errors(document), None) is not None
        if bad:
            failures.add(name)
    return failures


# ---------------------------------------------------------------------------
# module fixture: one real deterministic synthetic run + one schema-minimal root
# ---------------------------------------------------------------------------

def _run_pipeline(tmp: Path) -> Path:
    input_root = tmp / "inputs"
    output_root = tmp / "outputs"
    output_root.mkdir(parents=True)
    run_dir = output_root / RUN_ID
    generate.write_fixtures(input_root)
    config_path = REPO_ROOT / "config/gate0/default.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    for stage in STAGES:
        code, projection = execution.execute_stage(
            stage, run=run_dir, config_path=config_path, input_root=input_root,
            output_root=output_root, run_id=RUN_ID,
        )
        assert code == 0, f"{stage} failed: {projection}"
    corpus = generate.load_json(input_root / generate.CORPUS_FILE)
    labels = generate.load_json(input_root / generate.LABELS_FILE)
    review_input = REVIEW_ROOT / f"__payload-schema-{os.getpid()}.json"
    # PKT-D2-2: bind the envelope to the run's canonical config digest.
    run_config_digest = json.loads(
        (run_dir / "run_manifest.json").read_text(encoding="utf-8")
    )["config_digest"]
    global _REVIEW_INPUT
    _REVIEW_INPUT = review_input
    try:
        generate.write_review_input(review_input, labels, generate.evaluation_windows(corpus),
                                    config["blinding"]["token_map"], config_digest=run_config_digest)
        code, projection = execution.execute_stage(
            "evaluate", run=run_dir, config_path=config_path, input_root=input_root,
            output_root=output_root, run_id=RUN_ID, review_input=review_input,
        )
        assert code == 0, f"evaluate failed: {projection}"
    finally:
        review_input.unlink(missing_ok=True)
    code, projection = execution.execute_stage(
        "report", run=run_dir, config_path=config_path, input_root=input_root,
        output_root=output_root, run_id=RUN_ID,
    )
    assert code == 20, f"report failed: {projection}"
    return run_dir


def _resolve_pointer(root_schema: dict, ref: str) -> dict:
    node: object = root_schema
    for part in ref[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]  # type: ignore[index]
    return node  # type: ignore[return-value]


def _minimal_instance(root_schema: dict, schema: dict) -> object:
    """Build the smallest instance satisfying a (local-ref) closed schema."""
    if "$ref" in schema:
        return _minimal_instance(root_schema, _resolve_pointer(root_schema, schema["$ref"]))
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0]
    for combinator in ("oneOf", "anyOf"):
        if combinator in schema:
            return _minimal_instance(root_schema, schema[combinator][0])
    type_name = schema.get("type")
    if isinstance(type_name, list):
        type_name = next((name for name in type_name if name != "null"), type_name[0])
    if type_name == "object" or (type_name is None and "properties" in schema):
        result: dict[str, object] = {}
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in properties:
                raise ValueError(f"required property {key!r} is undeclared")
            result[key] = _minimal_instance(root_schema, properties[key])
        return result
    if type_name == "array":
        items = schema.get("items")
        if not isinstance(items, dict):
            return []
        return [_minimal_instance(root_schema, items) for _ in range(int(schema.get("minItems", 1)))]
    if type_name == "string" or (type_name is None and "pattern" in schema):
        pattern = schema.get("pattern")
        if pattern is not None:
            for known, sample in _PATTERN_SAMPLES.items():
                if pattern == known:
                    return sample
            raise ValueError(f"no sample for pattern {pattern!r}")
        if schema.get("format") == "date-time":
            return "2026-01-01T00:00:00Z"
        return "a" * int(schema.get("minLength", 1))
    if type_name == "integer":
        if "minimum" in schema:
            return int(schema["minimum"])
        if "exclusiveMinimum" in schema:
            return int(schema["exclusiveMinimum"]) + 1
        return 0
    if type_name == "number":
        if "minimum" in schema:
            return schema["minimum"]
        if "exclusiveMinimum" in schema:
            return schema["exclusiveMinimum"] + 1
        return 0
    if type_name == "boolean":
        return True
    if type_name == "null":
        return None
    raise ValueError(f"unsupported schema fragment: {schema!r}")


def _envelope_literal(schema: dict, field: str) -> str:
    """Resolve a JSONL envelope field that may be pinned by const or by enum."""
    node = schema.get("properties", {}).get(field, {})
    if isinstance(node.get("const"), str):
        return node["const"]
    enum = node.get("enum")
    if isinstance(enum, list) and enum and all(isinstance(value, str) for value in enum):
        return enum[0]
    raise ValueError(f"record schema does not pin {field!r} strongly enough")


def _write_schema_minimal_artifact(target: Path, name: str, schema: dict) -> None:
    if name.endswith(".jsonl"):
        record_type = _envelope_literal(schema, "record_type")
        version = _envelope_literal(schema, "record_schema_version")
        payload = _minimal_instance(schema, schema["properties"]["payload"])
        record = {
            "record_id": "a",
            "record_type": record_type,
            "record_schema_version": version,
            "record_digest": "0" * 64,
            "payload": payload,
        }
        (target / name).write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    else:
        document = _minimal_instance(schema, schema)
        (target / name).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_schema_minimal_root(target: Path) -> None:
    """Synthesize a candidate root from the schemas alone (no produced files)."""
    target.mkdir(parents=True)
    registry = json.loads((SCHEMA_ROOT / "registry.json").read_text(encoding="utf-8"))
    for name in ARTIFACT_FILENAMES:
        if name == "gate_decision.md":
            (target / name).write_text("schema-minimal control\n", encoding="utf-8")
            continue
        schema = json.loads((SCHEMA_ROOT / registry["schemas"][name]).read_text(encoding="utf-8"))
        _write_schema_minimal_artifact(target, name, schema)


def setUpModule() -> None:  # noqa: N802 - unittest hook
    global _TMP, _RUN_DIR, _MINIMAL_ROOT, _ORACLE_FAILURES
    _TMP = Path(tempfile.mkdtemp(prefix="gate0-payload-schema-"))
    _RUN_DIR = _run_pipeline(_TMP)
    _ORACLE_FAILURES = _oracle_payload_failures(_RUN_DIR)
    print(f"\n[payload-schema] observed oracle payload failures: {sorted(_ORACLE_FAILURES)}")
    _MINIMAL_ROOT = _TMP / "schema-minimal-root"
    _build_schema_minimal_root(_MINIMAL_ROOT)


def tearDownModule() -> None:  # noqa: N802 - unittest hook
    if "_REVIEW_INPUT" in globals():
        _REVIEW_INPUT.unlink(missing_ok=True)
    shutil.rmtree(_TMP, ignore_errors=True)


def _copy_run_root(name: str) -> Path:
    target = _TMP / name
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(_RUN_DIR, target)
    return target


class VerifierSchemaPayloadsTest(unittest.TestCase):
    def test_current_synthetic_run_matches_independent_payload_oracle(self) -> None:
        failures = _ORACLE_FAILURES
        if failures != AUDITED_CLOSED_FAILURES:
            print(
                "\n[payload-schema] failure set differs from audited closed set: "
                f"newly_failing={sorted(failures)} "
                f"historically_failing={sorted(AUDIT_CONTRACT_AUDIT_FAILURES)}"
            )
        self.assertEqual(failures, AUDITED_CLOSED_FAILURES)
        result = _verifier("--schema-payloads", "--candidate-root", str(_RUN_DIR))
        self.assertEqual(result.returncode, 0, result.stderr)
        statuses = _artifact_statuses(result.stdout)
        self.assertEqual(tuple(statuses), ARTIFACT_FILENAMES,
                         "verifier must report one line per artifact in registry order")
        self.assertEqual(set(statuses.values()), {"PASS"})
        self.assertEqual(_final_line(result.stdout), "schema_payloads=PASS")
        print("\n[payload-schema] produced synthetic artifacts: 13/13 PASS")

    def test_schema_minimal_candidate_root_passes_payload_validation(self) -> None:
        result = _verifier("--schema-payloads", "--candidate-root", str(_MINIMAL_ROOT))
        self.assertEqual(result.returncode, 0, result.stderr)
        statuses = _artifact_statuses(result.stdout)
        self.assertEqual(tuple(statuses), ARTIFACT_FILENAMES)
        self.assertEqual(set(statuses.values()), {"PASS"})
        self.assertEqual(_final_line(result.stdout), "schema_payloads=PASS")

    def test_flipped_required_field_fails_only_named_artifact(self) -> None:
        negative = _copy_run_root("negative-metrics-version")
        metrics_path = negative / "metrics.json"
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        metrics["schema_version"] = "gate0.metrics.tampered"
        metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
        result = _verifier("--schema-payloads", "--candidate-root", str(negative))
        self.assertEqual(result.returncode, 30, result.stderr)
        statuses = _artifact_statuses(result.stdout)
        failures = {name for name, status in statuses.items() if status == "FAIL"}
        self.assertEqual(failures, {"metrics.json"})
        self.assertEqual(_final_line(result.stdout), "schema_payloads=FAIL:metrics.json")

    def test_unknown_property_is_refused(self) -> None:
        negative = _copy_run_root("negative-unknown-property")
        path = negative / "metrics.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["unexpected_property"] = 1
        path.write_text(json.dumps(document), encoding="utf-8")
        result = _verifier("--schema-payloads", "--candidate-root", str(negative))
        self.assertEqual(result.returncode, 30, result.stderr)
        failures = {name for name, status in _artifact_statuses(result.stdout).items() if status == "FAIL"}
        self.assertEqual(failures, {"metrics.json"})

    def test_unknown_event_type_is_refused(self) -> None:
        negative = _copy_run_root("negative-unknown-event")
        path = negative / "runtime_and_failure_ledger.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(document["events"], "fixture run should carry ledger events")
        document["events"][0]["event_type"] = "TELEPORT"
        path.write_text(json.dumps(document), encoding="utf-8")
        result = _verifier("--schema-payloads", "--candidate-root", str(negative))
        self.assertEqual(result.returncode, 30, result.stderr)
        failures = {name for name, status in _artifact_statuses(result.stdout).items() if status == "FAIL"}
        self.assertEqual(failures, {"runtime_and_failure_ledger.json"})

    def test_malformed_payload_is_refused(self) -> None:
        negative = _copy_run_root("negative-malformed-payload")
        path = negative / "ranked_candidates.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertTrue(rows)
        rows[0]["payload"].pop("arm_id", None)
        path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        result = _verifier("--schema-payloads", "--candidate-root", str(negative))
        self.assertEqual(result.returncode, 30, result.stderr)
        failures = {name for name, status in _artifact_statuses(result.stdout).items() if status == "FAIL"}
        self.assertEqual(failures, {"ranked_candidates.jsonl"})

    def test_duplicate_source_manifest_record_is_refused(self) -> None:
        negative = _copy_run_root("negative-duplicate-record")
        path = negative / "source_manifest.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(document["records"])
        document["records"].append(json.loads(json.dumps(document["records"][0])))
        path.write_text(json.dumps(document), encoding="utf-8")
        result = _verifier("--schema-payloads", "--candidate-root", str(negative))
        self.assertEqual(result.returncode, 30, result.stderr)
        failures = {name for name, status in _artifact_statuses(result.stdout).items() if status == "FAIL"}
        self.assertEqual(failures, {"source_manifest.json"})

    def test_candidate_root_with_extra_file_is_refused(self) -> None:
        negative = _copy_run_root("negative-extra-file")
        (negative / "extra_artifact.json").write_text("{}\n", encoding="utf-8")
        result = _verifier("--schema-payloads", "--candidate-root", str(negative))
        self.assertEqual(result.returncode, 30)
        self.assertIn("T01_INVALID:", result.stderr)
        self.assertIn("exactly 13", result.stderr)

    def test_schemas_flag_alone_still_passes_without_payload_checks(self) -> None:
        result = _verifier("--schemas")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("schemas=PASS", result.stdout)
        self.assertNotIn("schema_payloads=", result.stdout)

    def test_schema_payloads_combines_with_schemas(self) -> None:
        result = _verifier("--schemas", "--schema-payloads", "--candidate-root", str(_RUN_DIR))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("schemas=PASS", result.stdout)
        self.assertEqual(_final_line(result.stdout), "schema_payloads=PASS")

    def test_schema_payloads_fails_closed_without_candidate_root(self) -> None:
        result = _verifier("--schema-payloads")
        self.assertEqual(result.returncode, 30)
        self.assertIn("T01_INVALID:", result.stderr)
        self.assertIn("--candidate-root", result.stderr)


if __name__ == "__main__":
    unittest.main()
