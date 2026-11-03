"""Regression tests for verifier dispatch correctness (D8 review finding F4).

Root cause under test: ``scripts/verify-gate0.py`` evaluated
``args.manifest_closure`` only inside the semantic artifact branch, but that
branch's guard did not include ``manifest_closure``.  A bare
``--manifest-closure`` therefore exited rc0 with no output and no validation.
The same file also conflated two different validation layers:

* ``--schema-payloads``  -> per-artifact JSON Schema payload validation only;
* ``--foreign-keys``     -> ``validate_artifact_set`` semantic FK closure;
* ``--manifest-closure`` -> the run manifest's own artifact-envelope
  dependency closure (this file), independent of the other two.

These tests drive the real CLI over a real deterministic synthetic run and
prove every requested validation actually executes, fails closed without a
candidate root, rejects corrupted closure references, and does not let one
validation layer claim credit for another.

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
VERIFIER = REPO_ROOT / "scripts/verify-gate0.py"
CONFIG_PATH = REPO_ROOT / "config/gate0/default.json"

ARTIFACT_FILENAMES = (
    "source_manifest.json", "discovery_authorizations.jsonl", "policy_decisions.jsonl",
    "split_manifest.json", "queries.jsonl", "gold_events.jsonl", "window_judgments.jsonl",
    "window_sample_manifest.jsonl", "run_manifest.json", "ranked_candidates.jsonl",
    "runtime_and_failure_ledger.json", "metrics.json", "gate_decision.md",
)
STAGES = ("prepare", "inventory", "split", "label", "preflight", "extract", "embed", "rank")
RUN_ID = "run_f4_dispatch"

if str(FIXTURE_ROOT) not in sys.path:
    sys.path.insert(0, str(FIXTURE_ROOT))

import generate  # noqa: E402

_TMP: Path
_RUN_DIR: Path


def _env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return env


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, env=_env(),
                          capture_output=True, text=True, check=False)


def _verifier(*flags: str) -> subprocess.CompletedProcess[str]:
    return _run(str(VERIFIER), *flags)


def _build_candidate_root(tmp: Path) -> Path:
    """Drive the real deterministic synthetic pipeline to a 13-artifact root."""
    input_root = tmp / "inputs"
    output_root = tmp / "outputs"
    output_root.mkdir(parents=True)
    run_dir = output_root / RUN_ID
    generate.write_fixtures(input_root)
    for stage in STAGES:
        result = _run("-m", "gate0.cli", stage, "--run", str(run_dir),
                      "--config", "config/gate0/default.json",
                      "--input-root", str(input_root), "--output-root", str(output_root),
                      "--run-id", RUN_ID)
        assert result.returncode == 0, f"{stage} failed: {result.stdout}{result.stderr}"
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    review_input = REVIEW_ROOT / f"__f4-dispatch-{os.getpid()}.json"
    corpus = generate.load_json(input_root / generate.CORPUS_FILE)
    labels = generate.load_json(input_root / generate.LABELS_FILE)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    # PKT-D2-2: bind the envelope to the run's canonical config digest.
    run_config_digest = json.loads(
        (run_dir / "run_manifest.json").read_text(encoding="utf-8")
    )["config_digest"]
    generate.write_review_input(review_input, labels, generate.evaluation_windows(corpus),
                                config["blinding"]["token_map"], config_digest=run_config_digest)
    result = _run("-m", "gate0.cli", "evaluate", "--run", str(run_dir),
                  "--config", "config/gate0/default.json",
                  "--input-root", str(input_root), "--output-root", str(output_root),
                  "--run-id", RUN_ID, "--review-input", str(review_input))
    assert result.returncode == 0, f"evaluate failed: {result.stdout}{result.stderr}"
    review_input.unlink(missing_ok=True)
    result = _run("-m", "gate0.cli", "report", "--run", str(run_dir),
                  "--config", "config/gate0/default.json",
                  "--input-root", str(input_root), "--output-root", str(output_root),
                  "--run-id", RUN_ID)
    assert result.returncode == 20, f"report failed: {result.stdout}{result.stderr}"
    published = tuple(sorted(path.name for path in run_dir.iterdir()))
    assert published == tuple(sorted(ARTIFACT_FILENAMES)), published
    return run_dir


def setUpModule() -> None:  # noqa: N802 - unittest hook
    global _TMP, _RUN_DIR
    _TMP = Path(tempfile.mkdtemp(prefix="gate0-f4-dispatch-"))
    _RUN_DIR = _build_candidate_root(_TMP)


def tearDownModule() -> None:  # noqa: N802 - unittest hook
    shutil.rmtree(_TMP, ignore_errors=True)


def _copy_root(name: str) -> Path:
    target = _TMP / name
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(_RUN_DIR, target)
    return target


def _load_manifest(root: Path) -> dict:
    return json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))


def _write_manifest(root: Path, manifest: dict) -> None:
    (root / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def _envelope(manifest: dict, artifact_type: str) -> dict:
    for envelope in manifest["artifact_envelopes"]:
        if envelope["artifact_type"] == artifact_type:
            return envelope
    raise AssertionError(f"no envelope for {artifact_type}")


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
# --manifest-closure dispatch: it must run, fail closed, and reject corruption
# ---------------------------------------------------------------------------

class ManifestClosureDispatchTest(unittest.TestCase):
    def test_bare_manifest_closure_runs_validation_and_reports_pass(self) -> None:
        result = _verifier("--manifest-closure", "--candidate-root", str(_RUN_DIR))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("manifest_closure=PASS", result.stdout,
                      "bare --manifest-closure must execute real validation, not silently no-op")

    def test_manifest_closure_without_candidate_root_fails_closed(self) -> None:
        result = _verifier("--manifest-closure")
        self.assertEqual(result.returncode, 30, result.stdout + result.stderr)
        self.assertIn("T01_INVALID:", result.stderr)
        self.assertIn("--candidate-root", result.stderr)
        self.assertNotIn("manifest_closure=PASS", result.stdout)

    def test_manifest_closure_rejects_wrong_dependency_digest(self) -> None:
        root = _copy_root("closure-wrong-digest")
        manifest = _load_manifest(root)
        refs = _envelope(manifest, "ranked_candidates.jsonl")["input_artifact_refs"]
        self.assertTrue(refs, "fixture run should declare typed dependency references")
        refs[0]["payload_digest"] = "f" * 64
        _write_manifest(root, manifest)
        result = _verifier("--manifest-closure", "--candidate-root", str(root))
        self.assertEqual(result.returncode, 30, result.stdout + result.stderr)
        self.assertIn("digest", result.stderr)
        self.assertNotIn("manifest_closure=PASS", result.stdout)

    def test_manifest_closure_rejects_unresolvable_producer_attempt(self) -> None:
        root = _copy_root("closure-bad-producer")
        manifest = _load_manifest(root)
        _envelope(manifest, "metrics.json")["producer_attempt_id"] = "attempt_missing_producer"
        _write_manifest(root, manifest)
        result = _verifier("--manifest-closure", "--candidate-root", str(root))
        self.assertEqual(result.returncode, 30, result.stdout + result.stderr)
        self.assertIn("producer", result.stderr)

    def test_manifest_closure_is_independent_of_foreign_keys(self) -> None:
        """A manifest-only defect must not be reported by the FK path, and vice versa."""
        root = _copy_root("closure-producer-independence")
        manifest = _load_manifest(root)
        _envelope(manifest, "metrics.json")["producer_attempt_id"] = "attempt_missing_producer"
        _write_manifest(root, manifest)
        foreign_keys = _verifier("--foreign-keys", "--candidate-root", str(root))
        self.assertEqual(foreign_keys.returncode, 0, foreign_keys.stderr)
        self.assertIn("foreign_keys=PASS", foreign_keys.stdout)
        closure = _verifier("--manifest-closure", "--candidate-root", str(root))
        self.assertEqual(closure.returncode, 30, closure.stdout + closure.stderr)

    def test_manifest_closure_rejects_dependency_cycle(self) -> None:
        root = _copy_root("closure-cycle")
        manifest = _load_manifest(root)
        metrics = _envelope(manifest, "metrics.json")
        _envelope(manifest, "source_manifest.json")["input_artifact_refs"].append({
            "artifact_id": metrics["artifact_id"],
            "payload_digest": metrics["payload_digest"],
            "artifact_type": metrics["artifact_type"],
        })
        _write_manifest(root, manifest)
        result = _verifier("--manifest-closure", "--candidate-root", str(root))
        self.assertEqual(result.returncode, 30, result.stdout + result.stderr)
        self.assertIn("cycle", result.stderr.lower())

    def test_manifest_closure_rejects_incomplete_envelope_set(self) -> None:
        root = _copy_root("closure-missing-envelope")
        manifest = _load_manifest(root)
        manifest["artifact_envelopes"] = [
            envelope for envelope in manifest["artifact_envelopes"]
            if envelope["artifact_type"] != "metrics.json"
        ]
        _write_manifest(root, manifest)
        result = _verifier("--manifest-closure", "--candidate-root", str(root))
        self.assertEqual(result.returncode, 30, result.stdout + result.stderr)
        self.assertIn("envelope", result.stderr)

    def test_combined_foreign_keys_and_manifest_closure_report_both_pass(self) -> None:
        result = _verifier("--foreign-keys", "--manifest-closure",
                           "--candidate-root", str(_RUN_DIR))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("foreign_keys=PASS", result.stdout)
        self.assertIn("manifest_closure=PASS", result.stdout)


# ---------------------------------------------------------------------------
# --schema-payloads layer boundary: JSON Schema is not semantic FK closure
# ---------------------------------------------------------------------------

class SchemaPayloadsLayerBoundaryTest(unittest.TestCase):
    def _semantic_only_corruption(self) -> Path:
        """A schema-valid candidate whose typed dependency digest does not resolve."""
        root = _copy_root("schema-payloads-semantic-corruption")
        manifest = _load_manifest(root)
        refs = _envelope(manifest, "ranked_candidates.jsonl")["input_artifact_refs"]
        self.assertTrue(refs)
        refs[0]["payload_digest"] = "f" * 64
        _write_manifest(root, manifest)
        return root

    def test_schema_payloads_does_not_claim_semantic_closure(self) -> None:
        root = self._semantic_only_corruption()
        result = _verifier("--schema-payloads", "--candidate-root", str(root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(_final_line(result.stdout), "schema_payloads=PASS")
        self.assertEqual(set(_artifact_statuses(result.stdout).values()), {"PASS"})
        # JSON Schema validation must never advertise semantic validation it did not run.
        self.assertNotIn("foreign_keys=", result.stdout)
        self.assertNotIn("manifest_closure=", result.stdout)
        # ...and the semantic path must still reject the same candidate.
        foreign_keys = _verifier("--foreign-keys", "--candidate-root", str(root))
        self.assertEqual(foreign_keys.returncode, 30, foreign_keys.stdout + foreign_keys.stderr)
        self.assertIn("digest", foreign_keys.stderr)

    def test_schema_payloads_still_rejects_invalid_json_schema_payload(self) -> None:
        root = _copy_root("schema-payloads-invalid-schema")
        metrics_path = root / "metrics.json"
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        metrics["schema_version"] = "gate0.metrics.tampered"
        metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
        result = _verifier("--schema-payloads", "--candidate-root", str(root))
        self.assertEqual(result.returncode, 30, result.stdout + result.stderr)
        failures = {name for name, status in _artifact_statuses(result.stdout).items()
                    if status == "FAIL"}
        self.assertEqual(failures, {"metrics.json"})
        self.assertEqual(_final_line(result.stdout), "schema_payloads=FAIL:metrics.json")

    def test_schema_payloads_reports_one_line_per_artifact(self) -> None:
        result = _verifier("--schema-payloads", "--candidate-root", str(_RUN_DIR))
        self.assertEqual(result.returncode, 0, result.stderr)
        statuses = _artifact_statuses(result.stdout)
        self.assertEqual(tuple(statuses), ARTIFACT_FILENAMES)
        self.assertEqual(set(statuses.values()), {"PASS"})
        self.assertEqual(_final_line(result.stdout), "schema_payloads=PASS")


# ---------------------------------------------------------------------------
# unrelated requested flags keep executing with unchanged output contracts
# ---------------------------------------------------------------------------

class VerifierDispatchSurfaceUnchangedTest(unittest.TestCase):
    def test_artifact_count_flag_still_prints_and_passes(self) -> None:
        result = _verifier("--artifact-count", "13")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("artifact_count=13", result.stdout)
        self.assertNotIn("manifest_closure=", result.stdout)

    def test_schemas_flag_still_passes_without_payload_checks(self) -> None:
        result = _verifier("--schemas")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("schemas=PASS", result.stdout)
        self.assertNotIn("schema_payloads=", result.stdout)

    def test_foreign_keys_flag_still_passes(self) -> None:
        result = _verifier("--foreign-keys", "--candidate-root", str(_RUN_DIR))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("foreign_keys=PASS", result.stdout)

    def test_manifest_closure_combines_with_artifact_count(self) -> None:
        result = _verifier("--manifest-closure", "--artifact-count", "13",
                           "--candidate-root", str(_RUN_DIR))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("artifact_count=13", result.stdout)
        self.assertIn("manifest_closure=PASS", result.stdout)

    def test_manifest_closure_fails_closed_when_combined_with_static_flags(self) -> None:
        result = _verifier("--manifest-closure", "--synthetic-only")
        self.assertEqual(result.returncode, 30, result.stdout + result.stderr)
        self.assertIn("T01_INVALID:", result.stderr)
        self.assertIn("--candidate-root", result.stderr)


if __name__ == "__main__":
    unittest.main()
