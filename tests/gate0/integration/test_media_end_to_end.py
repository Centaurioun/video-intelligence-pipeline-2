"""End-to-end Gate-0 experiment over *generated local media*.

This integration test exercises the media-input branch of the executable Gate-0
pipeline.  Unlike the synthetic fixtures (which carry no media at all), every
revision here points at a real MP4 generated at test time by
``tests/gate0/media/generated_media.py``; the measurement stage therefore runs
the real ``ffprobe``/``ffmpeg`` tools and the published evidence must contain
measured source-native presentation timestamps (PTS) in the source time base.

The test deliberately keeps the evidence boundary visible:

* media sampling is ``MEASURED``;
* embeddings and ground truth remain ``SYNTHETIC_FIXTURE``;
* the experiment result is ``NOT_OBSERVED`` and the report stage refuses to
  project a Gate-0 decision (return code 20, ``NOT_RUN``).

It also asserts that the sampler selected real decoded presentation timestamps
instead of synthesising ``tick * frame_duration`` from the nominal FPS, and that
four adversarial media inputs (variable frame rate, truncated, empty and
faststart-truncated files) fail closed with the expected reason codes.

No corpus, model, network or provider call is used: the media is generated from
``lavfi``/``testsrc2`` inside the test's temporary directory and never
committed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
MEDIA_TEST_ROOT = REPO_ROOT / "tests/gate0/media"
GENERATED_MEDIA_ROOT = REPO_ROOT / "tests/gate0/fixtures/generated-media"
SYNTHETIC_INPUT_ROOT = REPO_ROOT / "tests/gate0/fixtures/synthetic-input"
REVIEW_ROOT = REPO_ROOT / "tests/gate0/fixtures/review-input"

for _path in (
    str(REPO_ROOT),
    str(MEDIA_TEST_ROOT),
    str(GENERATED_MEDIA_ROOT),
    str(SYNTHETIC_INPUT_ROOT),
):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import build_media_corpus  # noqa: E402
import generate  # noqa: E402  (synthetic-input generator, reused verbatim)
import generated_media  # noqa: E402

STAGES = ("prepare", "inventory", "split", "label", "preflight", "extract", "embed", "rank")
ARTIFACT_FILENAMES = (
    "source_manifest.json", "discovery_authorizations.jsonl", "policy_decisions.jsonl",
    "split_manifest.json", "queries.jsonl", "gold_events.jsonl", "window_judgments.jsonl",
    "window_sample_manifest.jsonl", "run_manifest.json", "ranked_candidates.jsonl",
    "runtime_and_failure_ledger.json", "metrics.json", "gate_decision.md",
)

TOOLS_AVAILABLE = (
    generated_media.tool_available("ffmpeg") and generated_media.tool_available("ffprobe")
)

# Expected measured evidence for the four generated-media revisions.
EXPECTED_FRAME_COUNT = {
    "rev_eval_sunrise": 120,  # cfr_30
    "rev_eval_office": 100,  # cfr_25
    "rev_eval_night": 100,  # bframes
    "rev_dev_probe": 100,  # byte copy of cfr_25
}
EXPECTED_TIME_BASE = {
    "rev_eval_sunrise": (1, 15360),
    "rev_eval_office": (1, 12800),
    "rev_eval_night": (1, 12800),
    "rev_dev_probe": (1, 12800),
}
MEDIA_CORPUS_KIND = "generated_synthetic_media_not_experiment_evidence"
MEDIA_MEASUREMENT_ORIGIN = "LOCAL_GENERATED_MEDIA_NOT_AUTHORIZED_CORPUS"

pytestmark = pytest.mark.skipif(
    not TOOLS_AVAILABLE, reason="ffmpeg/ffprobe are required to generate and measure media"
)


def _env() -> dict[str, str]:
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return env


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=REPO_ROOT, env=_env(), capture_output=True, text=True, check=False
    )


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _time_base(record: dict) -> tuple[int, int]:
    return int(record["time_base"]["numerator"]), int(record["time_base"]["denominator"])


def _first_pts_at_or_after(pts: list[int], tick: int, numerator: int, denominator: int) -> int:
    """First decoded PTS (raw ticks) at/after the sample target offset ``tick / 2`` seconds."""
    for point in pts:
        if point * numerator * 2 >= tick * denominator:
            return point
    raise AssertionError(f"no decoded PTS at/after target tick {tick}")


@unittest.skipUnless(TOOLS_AVAILABLE, "ffmpeg/ffprobe are required to generate and measure media")
class MediaEndToEndTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._shared_tmp = Path(tempfile.mkdtemp(prefix="gate0-media-shared-"))
        cls._shared_input = cls._shared_tmp / "inputs"
        build_media_corpus.build_media_input(cls._shared_input)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls._shared_tmp, ignore_errors=True)

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="gate0-media-e2e-"))
        self.input_root = self.tmp / "inputs"
        shutil.copytree(self._shared_input, self.input_root)
        self.output_root = self.tmp / "outputs"
        self.output_root.mkdir()
        self.run_id = "run_media_e2e"
        self.run_dir = self.output_root / self.run_id
        self.config = json.loads((REPO_ROOT / "config/gate0/default.json").read_text(encoding="utf-8"))
        self.review_path = REVIEW_ROOT / f"{self.run_id}.json"
        self._media_corpus = json.loads((self.input_root / "media-corpus.json").read_text(encoding="utf-8"))

    def tearDown(self) -> None:
        self.review_path.unlink(missing_ok=True)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers ---------------------------------------------------------
    def _stage(self, stage: str, *extra: str) -> subprocess.CompletedProcess[str]:
        return _run(
            "-m", "gate0.cli", stage,
            "--run", str(self.run_dir),
            "--config", "config/gate0/default.json",
            "--input-root", str(self.input_root),
            "--output-root", str(self.output_root),
            "--run-id", self.run_id,
            *extra,
        )

    def _manifest(self) -> dict:
        return json.loads((self.run_dir / "run_manifest.json").read_text(encoding="utf-8"))

    def _fail(self, stage: str, *extra: str) -> dict:
        """Run one stage expecting a fail-closed (non-zero) return and return its JSON body."""
        result = self._stage(stage, *extra)
        self.assertNotEqual(result.returncode, 0, f"{stage} unexpectedly succeeded: {result.stdout}")
        body = json.loads(result.stdout)
        self.assertNotEqual(body.get("status"), "SUCCEEDED")
        self.assertFalse(
            (self.run_dir / "run_manifest.json").exists()
            and json.loads((self.run_dir / "run_manifest.json").read_text())["status"] == "REPORTED",
            "a failed-closed run must not be reported",
        )
        return body

    def _write_review_input(self) -> None:
        """Build reviewer assertions from the synthetic labels over the *media* windows.

        Labels are reused verbatim from the synthetic-input generator (no
        hand-authored ground truth); only the window universe is projected from
        the media corpus, which carries one window per evaluation revision.
        """
        labels = generate.load_json(self.input_root / generate.LABELS_FILE)
        windows = []
        for revision in self._media_corpus["revisions"]:
            if revision["split"] != "EVALUATION":
                continue
            for window_index in range(int(revision["window_count"])):
                start, end = generate.window_interval(window_index)
                windows.append(
                    {
                        "revision_id": revision["revision_id"],
                        "window_index": window_index,
                        "window_id": generate.window_id(revision["revision_id"], window_index),
                        "start": start,
                        "end": end,
                    }
                )
        generate.write_review_input(
            self.review_path, labels, windows, self.config["blinding"]["token_map"],
            config_digest=self._manifest()["config_digest"],
        )

    def _ffprobe_pts(self, locator: str) -> list[int]:
        """Independently list the decoded presentation timestamps of one source file."""
        ffprobe = str(self.config["runtime"]["ffprobe_path"])
        result = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=pts",
             "-of", "json", str(self.input_root / locator)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, f"ffprobe failed for {locator}: {result.stderr}")
        return [int(frame["pts"]) for frame in json.loads(result.stdout)["frames"]]

    # -- main (positive) experiment --------------------------------------
    def test_media_experiment_runs_end_to_end_with_measured_pts_and_refuses_gate_pass(self) -> None:
        for stage in STAGES:
            result = self._stage(stage)
            self.assertEqual(result.returncode, 0, f"{stage} failed: {result.stdout}{result.stderr}")

        self._write_review_input()
        evaluate = self._stage("evaluate", "--review-input", str(self.review_path))
        self.assertEqual(evaluate.returncode, 0, f"evaluate failed: {evaluate.stdout}{evaluate.stderr}")

        report = self._stage("report")
        self.assertEqual(report.returncode, 20, "generated media must block a Gate-0 decision")
        decision = json.loads(report.stdout)
        self.assertEqual(decision["gate_decision"], "NOT_RUN")
        self.assertEqual(decision["status"], "NOT_RUN")

        published = sorted(path.name for path in self.run_dir.iterdir())
        self.assertEqual(tuple(published), tuple(sorted(ARTIFACT_FILENAMES)))
        self.assertIn("NOT_RUN", (self.run_dir / "gate_decision.md").read_text(encoding="utf-8"))

        manifest = self._manifest()
        self.assertEqual(manifest["status"], "REPORTED")
        self.assertEqual(manifest["evidence_class"], "MEASURED")
        self.assertEqual(manifest["corpus_kind"], MEDIA_CORPUS_KIND)
        self.assertEqual(
            manifest["evidence_class_boundary"],
            {
                "media_sampling": "MEASURED",
                "embedding": "SYNTHETIC_FIXTURE",
                "ground_truth": "SYNTHETIC_FIXTURE",
                "experiment_result": "NOT_OBSERVED",
            },
        )
        self.assertEqual(manifest["media_measurement_origin"], MEDIA_MEASUREMENT_ORIGIN)
        self.assertEqual(manifest["run_decision"]["gate_decision"], "NOT_RUN")
        self.assertEqual(manifest["run_decision"]["benchmark_status"], "NOT_RUN")
        self.assertEqual(
            manifest["run_decision"]["stop_reason_detail"],
            "GENERATED_MEDIA_NOT_AUTHORIZED_CORPUS",
        )
        self.assertTrue(str(manifest["media_tools"]["ffprobe"]["version"]))
        self.assertTrue(str(manifest["media_tools"]["ffmpeg"]["version"]))

        measurements = manifest["media_measurements"]
        self.assertEqual(len(measurements), 4)
        for record in measurements:
            with self.subTest(revision=record["revision_id"]):
                self.assertIsInstance(record["presentation_pts_ticks_first"], int)
                self.assertGreater(int(record["frame_count"]), 0)
                self.assertRegex(str(record["probe_ref"]), r"^probe_[0-9a-f]{32}$")
                self.assertRegex(str(record["source_digest"]), r"^[0-9a-f]{64}$")
                numerator, denominator = _time_base(record)
                self.assertGreater(numerator, 0)
                self.assertGreater(denominator, 0)
                self.assertEqual(record["selected_stream_index"], 0)
                self.assertEqual(record["evidence_class"], "MEASURED")
                self.assertEqual(record["source_kind"], "LOCAL_GENERATED_MEDIA")
                self.assertEqual(record["decoded_frame_count"], record["frame_count"])
                self.assertEqual(record["window_count"], 1)

        self._assert_measured_pts_evidence(measurements)
        self._assert_window_samples(measurements)

    def _assert_measured_pts_evidence(self, measurements: list[dict]) -> None:
        records = {record["revision_id"]: record for record in measurements}
        self.assertEqual(sorted(records), sorted(EXPECTED_FRAME_COUNT))
        for revision_id, record in records.items():
            with self.subTest(revision=revision_id):
                pts = self._ffprobe_pts(str(record["locator"]))
                self.assertEqual(len(pts), EXPECTED_FRAME_COUNT[revision_id])
                self.assertEqual(len(set(pts)), len(pts), "presentation timestamps must be distinct")
                self.assertEqual(record["frame_count"], EXPECTED_FRAME_COUNT[revision_id])
                self.assertEqual(record["decoded_frame_count"], EXPECTED_FRAME_COUNT[revision_id])
                self.assertEqual(_time_base(record), EXPECTED_TIME_BASE[revision_id])
                # the measured first/last PTS must be real decoded timestamps
                self.assertEqual(record["presentation_pts_ticks_first"], min(pts))
                self.assertEqual(record["presentation_pts_ticks_last"], max(pts))
        # cfr_25 starts at PTS 0 and decodes 100 frames; bframes has 100 distinct
        # presentation timestamps (B-frames reorder, they do not collapse).
        self.assertEqual(records["rev_eval_office"]["presentation_pts_ticks_first"], 0)
        self.assertEqual(len(set(self._ffprobe_pts(str(records["rev_eval_night"]["locator"])))), 100)
        # the dev revision is a byte copy, so its measured evidence is identical
        office = records["rev_eval_office"]
        dev = records["rev_dev_probe"]
        self.assertEqual(dev["source_digest"], office["source_digest"])
        self.assertEqual(dev["presentation_pts_ticks_first"], office["presentation_pts_ticks_first"])
        self.assertEqual(dev["presentation_pts_ticks_last"], office["presentation_pts_ticks_last"])

    def _assert_window_samples(self, measurements: list[dict]) -> None:
        records = {record["revision_id"]: record for record in measurements}
        rows = _jsonl(self.run_dir / "window_sample_manifest.jsonl")
        self.assertEqual(len(rows), 4 * 1 * 8, "one window x eight ticks per revision")
        by_revision: dict[str, list[dict]] = {}
        for row in rows:
            payload = row["payload"]
            revision_id = str(payload["window_id"]).split("_window_")[0]
            self.assertIn(revision_id, records)
            by_revision.setdefault(revision_id, []).append(payload)
        self.assertEqual(sorted(by_revision), sorted(records))
        off_grid_samples = 0
        for revision_id, payloads in by_revision.items():
            with self.subTest(revision=revision_id):
                record = records[revision_id]
                pts = sorted(self._ffprobe_pts(str(record["locator"])))
                pts_set = set(pts)
                self.assertEqual(len(payloads), 8)
                self.assertEqual({int(p["tick"]) for p in payloads}, set(range(8)))
                statuses = {str(p["coverage_status"]) for p in payloads}
                # the frozen contract names SUCCEEDED; a sibling contract lane may
                # rename it to SELECTED, so both are accepted and the rest rejected.
                self.assertEqual(len(statuses), 1, f"mixed coverage statuses: {statuses}")
                self.assertIn(statuses.pop(), {"SUCCEEDED", "SELECTED"})
                frame_duration = min(b - a for a, b in zip(pts, pts[1:]))
                numerator, denominator = _time_base(record)
                self.assertEqual(frame_duration, denominator // (EXPECTED_FRAME_COUNT[revision_id] // 4))
                ticks_per_second = denominator // numerator
                for payload in payloads:
                    raw = payload["raw_pts"]
                    self.assertIsInstance(raw["ticks"], int)
                    self.assertEqual((raw["time_base_num"], raw["time_base_den"]), (numerator, denominator))
                    tick = int(payload["tick"])
                    sampled = int(raw["ticks"])
                    # the sampled tick is a real decoded presentation timestamp...
                    self.assertIn(sampled, pts_set)
                    # ...inside the measured first/last PTS range...
                    self.assertGreaterEqual(sampled, int(record["presentation_pts_ticks_first"]))
                    self.assertLessEqual(sampled, int(record["presentation_pts_ticks_last"]))
                    # ...and it is the first real decoded frame at/after the target
                    # offset, i.e. measured frame selection, not arithmetic.
                    self.assertEqual(sampled, _first_pts_at_or_after(pts, tick, numerator, denominator))
                    # An arithmetic sampler would emit `tick/2 * ticks_per_second`
                    # (the nominal-FPS frame grid).  On the 25 fps sources a
                    # half-frame target offset (odd tick) lands off the real frame
                    # grid, so an off-grid synthetic value proves the sampler
                    # measured PTS rather than synthesising it.  (On the 30 fps
                    # source the 0.5 s offsets happen to coincide with real frame
                    # boundaries, so that revision cannot discriminate and is
                    # covered by the exact-frame assertion above instead.)
                    synthesized = (tick * ticks_per_second) // 2
                    if synthesized not in pts_set and sampled != synthesized:
                        off_grid_samples += 1
        self.assertGreaterEqual(
            off_grid_samples,
            8,
            "no half-frame target offset distinguished measured PTS from nominal-FPS arithmetic",
        )

    # -- negative (fail-closed) tests ------------------------------------
    def _rewrite_revision(self, revision_id: str, **changes) -> None:
        path = self.input_root / "media-corpus.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        for revision in document["revisions"]:
            if revision["revision_id"] == revision_id:
                revision.update(changes)
                break
        else:  # pragma: no cover - defensive
            raise AssertionError(f"unknown revision {revision_id}")
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_vfr_concat_revision_fails_closed_on_window_coverage(self) -> None:
        self._rewrite_revision("rev_eval_night", locator="media/vfr_concat.mp4", window_count=1)
        self.assertEqual(self._stage("prepare").returncode, 0)
        body = self._fail("inventory")
        self.assertIn("INVALID_WINDOW_COVERAGE", json.dumps(body))
        self.assertFalse((self.run_dir / "window_sample_manifest.jsonl").exists())

    def test_corrupt_truncated_media_fails_closed_probe_tool_failed(self) -> None:
        self._rewrite_revision("rev_eval_office", locator="media/corrupt_truncated.mp4")
        self.assertEqual(self._stage("prepare").returncode, 0)
        body = self._fail("inventory")
        self.assertIn("PROBE_TOOL_FAILED", json.dumps(body))

    def test_corrupt_empty_media_fails_closed_source_unreadable(self) -> None:
        self._rewrite_revision("rev_eval_office", locator="media/corrupt_empty.mp4")
        self.assertEqual(self._stage("prepare").returncode, 0)
        body = self._fail("inventory")
        self.assertIn("SOURCE_UNREADABLE", json.dumps(body))

    def test_corrupt_truncated_faststart_fails_closed_partial_stream_evidence(self) -> None:
        self._rewrite_revision("rev_eval_office", locator="media/corrupt_truncated_faststart.mp4")
        self.assertEqual(self._stage("prepare").returncode, 0)
        body = self._fail("inventory")
        self.assertIn("PARTIAL_STREAM_EVIDENCE", json.dumps(body))


    # -- source-integrity (Task 6) fail-closed tests ----------------------
    def test_relabelled_corpus_pointing_at_arbitrary_file_fails_closed(self) -> None:
        arbitrary = self.input_root / "media" / "arbitrary.txt"
        arbitrary.write_bytes(b"not a generated media fixture\n")
        self._rewrite_revision("rev_eval_office", locator="media/arbitrary.txt")
        self.assertEqual(self._stage("prepare").returncode, 0)
        body = self._fail("inventory")
        payload = json.dumps(body)
        self.assertTrue(
            "MEDIA_PROVENANCE_UNVERIFIED" in payload or "SOURCE_DIGEST_MISMATCH" in payload,
            payload,
        )

    def test_symlink_locator_fails_closed(self) -> None:
        target = self.input_root / "media" / "cfr_25.mp4"
        link = self.input_root / "media" / "office_link.mp4"
        link.symlink_to(target)
        self._rewrite_revision("rev_eval_office", locator="media/office_link.mp4")
        self.assertEqual(self._stage("prepare").returncode, 0)
        body = self._fail("inventory")
        self.assertIn("SOURCE_SYMLINK", json.dumps(body))

    def test_mutated_fixture_bytes_fail_closed_digest_mismatch(self) -> None:
        source = self.input_root / "media" / "cfr_25.mp4"
        source.write_bytes(source.read_bytes() + b"\x00")
        self.assertEqual(self._stage("prepare").returncode, 0)
        body = self._fail("inventory")
        payload = json.dumps(body)
        self.assertTrue(
            "SOURCE_DIGEST_MISMATCH" in payload or "MEDIA_PROVENANCE_UNVERIFIED" in payload,
            payload,
        )


if __name__ == "__main__":
    unittest.main()
