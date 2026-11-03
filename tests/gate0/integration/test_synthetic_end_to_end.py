"""End-to-end executable Gate-0 experiment over synthetic fixtures.

The frozen experiment contract names eleven CLI stages, but before this lane the
only executable stages were ``preflight`` and ``repeat``: every other stage was
an explicit ``NOT_OBSERVED`` stub and no code produced the closed thirteen
artifact set.  This test drives the real CLI boundary through the full declared
order using the checked-in deterministic synthetic generator, then proves:

* the metadata floor and the semantic arm are ranked, joined to typed window
  evidence and evaluated under the frozen metric protocol;
* the report stage refuses to project a Gate-0 PASS from synthetic evidence;
* the published artifact set passes the repository verifier's semantic closure;
* the read-only repeat boundary reproduces the frozen input digest.

No real corpus, model, network or provider call is used.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = REPO_ROOT / "tests/gate0/fixtures/synthetic-input"
REVIEW_ROOT = REPO_ROOT / "tests/gate0/fixtures/review-input"
ARTIFACT_FILENAMES = (
    "source_manifest.json", "discovery_authorizations.jsonl", "policy_decisions.jsonl",
    "split_manifest.json", "queries.jsonl", "gold_events.jsonl", "window_judgments.jsonl",
    "window_sample_manifest.jsonl", "run_manifest.json", "ranked_candidates.jsonl",
    "runtime_and_failure_ledger.json", "metrics.json", "gate_decision.md",
)
STAGES = ("prepare", "inventory", "split", "label", "preflight", "extract", "embed", "rank")

if str(FIXTURE_ROOT) not in sys.path:
    sys.path.insert(0, str(FIXTURE_ROOT))
import generate  # noqa: E402


def _env() -> dict[str, str]:
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return env


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, env=_env(),
                          capture_output=True, text=True, check=False)


class SyntheticEndToEndTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="gate0-e2e-"))
        self.input_root = self.tmp / "inputs"
        self.output_root = self.tmp / "outputs"
        self.run_id = "run_synthetic_e2e"
        self.run_dir = self.output_root / self.run_id
        self.output_root.mkdir()
        generate.write_fixtures(self.input_root)
        self.config = json.loads((REPO_ROOT / "config/gate0/default.json").read_text(encoding="utf-8"))
        self.review_path = REVIEW_ROOT / f"{self.run_id}.json"

    def tearDown(self) -> None:
        self.review_path.unlink(missing_ok=True)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers ---------------------------------------------------------
    def _stage(self, stage: str, *extra: str) -> subprocess.CompletedProcess[str]:
        return _run("-m", "gate0.cli", stage,
                    "--run", str(self.run_dir), "--config", "config/gate0/default.json",
                    "--input-root", str(self.input_root), "--output-root", str(self.output_root),
                    "--run-id", self.run_id, *extra)

    def _manifest(self) -> dict:
        return json.loads((self.run_dir / "run_manifest.json").read_text(encoding="utf-8"))

    def _write_review_input(self) -> None:
        corpus = generate.load_json(self.input_root / generate.CORPUS_FILE)
        labels = generate.load_json(self.input_root / generate.LABELS_FILE)
        # PKT-D2-2: bind the synthetic reviewer envelope to the run's canonical
        # config digest (published by prepare), never the legacy zero placeholder.
        generate.write_review_input(self.review_path, labels, generate.evaluation_windows(corpus),
                                    self.config["blinding"]["token_map"],
                                    config_digest=self._manifest()["config_digest"])

    # -- full synthetic experiment --------------------------------------
    def test_synthetic_experiment_runs_end_to_end_and_refuses_gate_pass(self) -> None:
        for stage in STAGES:
            result = self._stage(stage)
            self.assertEqual(result.returncode, 0, f"{stage} failed: {result.stdout}{result.stderr}")

        # Sample manifests are revision-qualified: a four-revision run is the
        # regression case for the previous cross-revision window_id collision.
        samples = [json.loads(line) for line in (self.run_dir / "window_sample_manifest.jsonl").read_text().splitlines()]
        pairs = {(row["payload"]["window_id"], row["payload"]["tick"]) for row in samples}
        self.assertEqual(len(pairs), len(samples))
        self.assertEqual(len(samples), 4 * 2 * 8)

        self._write_review_input()
        evaluate = self._stage("evaluate", "--review-input", str(self.review_path))
        self.assertEqual(evaluate.returncode, 0, f"evaluate failed: {evaluate.stdout}{evaluate.stderr}")

        report = self._stage("report")
        self.assertEqual(report.returncode, 20, "synthetic evidence must block a Gate-0 decision")
        decision = json.loads(report.stdout)
        self.assertEqual(decision["gate_decision"], "NOT_RUN")
        self.assertEqual(decision["status"], "NOT_RUN")

        metrics = {row["metric_id"]: (row["numerator"], row["denominator"])
                   for row in json.loads((self.run_dir / "metrics.json").read_text())["metrics"]}
        self.assertEqual(metrics["hit_at_10.semantic"], (18, 24))
        self.assertEqual(metrics["hit_at_10.metadata"], (4, 24))
        self.assertEqual(metrics["paired_lift.semantic_minus_metadata"], (14, 24))
        self.assertEqual(metrics["family_hit_at_10.semantic.scene_composition_camera_movement"], (0, 6))

        published = sorted(path.name for path in self.run_dir.iterdir())
        self.assertEqual(tuple(published), tuple(sorted(ARTIFACT_FILENAMES)))
        verdict = json.loads((self.run_dir / "run_manifest.json").read_text())["run_decision"]
        self.assertEqual(verdict["gate_decision"], "NOT_RUN")
        self.assertEqual(verdict["stop_reason_detail"], "SYNTHETIC_FIXTURE_NOT_AUTHORIZED_CORPUS")

        verifier = _run("scripts/verify-gate0.py", "--candidate-root", str(self.run_dir),
                        "--foreign-keys", "--manifest-closure", "--artifact-count", "13")
        self.assertEqual(verifier.returncode, 0, verifier.stderr)
        self.assertIn("foreign_keys=PASS", verifier.stdout)
        self.assertIn("manifest_closure=PASS", verifier.stdout)

        manifest = self._manifest()
        self.assertEqual(manifest["status"], "REPORTED")
        digest = manifest["frozen_input_digests"]["frozen-index"]
        repeat = self._stage("repeat", "--mode", "frozen-index",
                             "--predecessor-run-id", self.run_id,
                             "--frozen-input-digest", digest)
        self.assertEqual(repeat.returncode, 0, repeat.stderr)
        self.assertEqual(json.loads(repeat.stdout)["status"], "EQUAL")

        # Labels never reach the ranker input surface.
        ranker_inputs = manifest["label_isolation"]["ranker_inputs"]
        self.assertNotIn(generate.LABELS_FILE, ranker_inputs)
        self.assertIn(generate.LABELS_FILE, manifest["label_isolation"]["ranker_excludes"])

    # -- refusal surface -------------------------------------------------
    def test_evaluate_without_review_input_is_invalid_protocol(self) -> None:
        for stage in STAGES:
            self.assertEqual(self._stage(stage).returncode, 0)
        result = self._stage("evaluate")
        self.assertEqual(result.returncode, 30)

    def test_evaluate_rejects_review_input_outside_authorized_root(self) -> None:
        for stage in STAGES:
            self.assertEqual(self._stage(stage).returncode, 0)
        outside = self.tmp / "reviewer.json"
        outside.write_text((REVIEW_ROOT / "README.md").read_text(encoding="utf-8") if (REVIEW_ROOT / "README.md").exists() else "{}")
        result = self._stage("evaluate", "--review-input", str(outside))
        self.assertEqual(result.returncode, 30)


if __name__ == "__main__":
    unittest.main()
