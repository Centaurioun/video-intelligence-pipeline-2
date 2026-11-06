"""Integration and CLI tests for vip-fvs analyze-local and QUERY_DRIVEN_SEMANTIC_REPORT_V1."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

try:
    import numpy as _np  # noqa: F401
    from PIL import Image as _pil_img  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    import types

    if "numpy" not in sys.modules:
        _stub_np = types.ModuleType("numpy")
        _stub_np.ndarray = object  # type: ignore[attr-defined]
        _stub_np.float32 = float  # type: ignore[attr-defined]
        _stub_np.float64 = float  # type: ignore[attr-defined]
        _stub_np.dtype = lambda *_a, **_kw: types.SimpleNamespace(itemsize=4)  # type: ignore[attr-defined]
        sys.modules["numpy"] = _stub_np
    if "PIL" not in sys.modules:
        _stub_pil = types.ModuleType("PIL")
        _stub_pil.Image = types.SimpleNamespace(Image=object, open=lambda *_a, **_kw: None)  # type: ignore[attr-defined]
        sys.modules["PIL"] = _stub_pil
        sys.modules["PIL.Image"] = _stub_pil.Image  # type: ignore[assignment]

from vip_fvs import cli
from vip_fvs.core_report import (
    CORE_REPORT_KIND,
    CORE_REPORT_SCHEMA_VERSION,
    compute_core_report_digest,
    validate_core_semantic_report,
)
from vip_fvs.source_snapshot import SourceSnapshotStore
from tests.vip_fvs.unit.test_core_analysis import (
    _SqliteBackedStubEngine,
    _make_probe_fn,
    _make_source_file,
    _make_stub_runtime,
)


def _run_cli_in_process(argv: list[str]) -> tuple[int, dict, str]:
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
        exit_code = cli.main(argv)
    raw_out = stdout_buf.getvalue().strip()
    lines = [line for line in raw_out.splitlines() if line.strip()]
    assert len(lines) == 1, f"Expected exactly 1 JSON line on stdout, got: {raw_out!r}"
    payload = json.loads(lines[0])
    return exit_code, payload, stderr_buf.getvalue()


def test_cli_analyze_local_positive_zero_match_and_no_clobber(tmp_path: Path) -> None:
    source_path = tmp_path / "source_video.mp4"
    _make_source_file(source_path, b"cli-integration-video-bytes-v1")
    index_root = tmp_path / "index"
    output_root = tmp_path / "output"
    report_path = output_root / "semantic-report.json"

    stub_engine = _SqliteBackedStubEngine(
        sample_rows=[
            (0, 0, 0.31),
            (1, 30030, 0.88),
            (2, 60060, 0.74),
            (3, 90090, 0.62),
            (4, 120120, 0.55),
            (5, 150150, 0.19),
        ],
        stream_index=1,
        timebase=(1001, 30000),
    )

    with (
        mock.patch(
            "vip_fvs.core_analysis._build_default_runtime",
            return_value=_make_stub_runtime(),
        ),
        mock.patch(
            "vip_fvs.core_analysis._build_default_engine",
            return_value=stub_engine,
        ),
        mock.patch(
            "vip_fvs.core_analysis.probe_real_source",
            side_effect=_make_probe_fn(selected_stream_index=1),
        ),
    ):
        exit_code, summary, stderr_text = _run_cli_in_process(
            [
                "analyze-local",
                "--source",
                str(source_path),
                "--query",
                "ballet ensemble jump",
                "--index-root",
                str(index_root),
                "--output-root",
                str(output_root),
                "--report-path",
                str(report_path),
                "--attempt-id",
                "cli-att-001",
                "--source-revision-id",
                "cli-rev-001",
                "--selected-stream-index",
                "1",
                "--top-k",
                "5",
                "--fake-embedder",
            ]
        )

    assert exit_code == 0
    assert stderr_text == ""
    assert summary["command"] == "analyze-local"
    assert summary["schema_version"] == CORE_REPORT_SCHEMA_VERSION
    assert summary["report_kind"] == CORE_REPORT_KIND
    assert summary["stage_status"] == "SUCCEEDED"
    assert summary["result_kind"] == "MATCHES_FOUND"
    assert summary["top_k"] == 5
    assert summary["returned_candidate_count"] == 5
    assert summary["total_eligible_matches"] == 6
    assert report_path.is_file()

    saved_bytes = report_path.read_bytes()
    saved_report = json.loads(saved_bytes.decode("utf-8"))
    validate_core_semantic_report(saved_report)
    assert saved_report["artifact"]["report_digest"] == compute_core_report_digest(
        saved_report
    )
    assert [m["row_id"] for m in saved_report["matches"]] == [1, 2, 3, 4, 0]

    # Repeated invocation on existing report_path must fail with OUTPUT_ALREADY_EXISTS and preserve bytes
    with (
        mock.patch(
            "vip_fvs.core_analysis._build_default_runtime",
            return_value=_make_stub_runtime(),
        ),
        mock.patch(
            "vip_fvs.core_analysis._build_default_engine",
            return_value=stub_engine,
        ),
        mock.patch(
            "vip_fvs.core_analysis.probe_real_source",
            side_effect=_make_probe_fn(selected_stream_index=1),
        ),
    ):
        dup_code, dup_summary, _ = _run_cli_in_process(
            [
                "analyze-local",
                "--source",
                str(source_path),
                "--query",
                "ballet ensemble jump",
                "--index-root",
                str(index_root),
                "--output-root",
                str(output_root),
                "--report-path",
                str(report_path),
                "--attempt-id",
                "cli-att-001",
                "--source-revision-id",
                "cli-rev-001",
                "--selected-stream-index",
                "1",
                "--top-k",
                "5",
                "--fake-embedder",
            ]
        )

    assert dup_code == 1
    assert dup_summary["result_kind"] == "REFUSED"
    assert dup_summary["error_code"] == "OUTPUT_ALREADY_EXISTS"
    assert report_path.read_bytes() == saved_bytes

    # Zero-match CLI run
    zero_report_path = output_root / "zero-report.json"
    zero_engine = _SqliteBackedStubEngine(return_empty_hits=True, stream_index=1)
    with (
        mock.patch(
            "vip_fvs.core_analysis._build_default_runtime",
            return_value=_make_stub_runtime(),
        ),
        mock.patch(
            "vip_fvs.core_analysis._build_default_engine",
            return_value=zero_engine,
        ),
        mock.patch(
            "vip_fvs.core_analysis.probe_real_source",
            side_effect=_make_probe_fn(selected_stream_index=1),
        ),
    ):
        z_code, z_summary, _ = _run_cli_in_process(
            [
                "analyze-local",
                "--source",
                str(source_path),
                "--query",
                "no matching visual moment",
                "--index-root",
                str(tmp_path / "index_zero"),
                "--output-root",
                str(output_root),
                "--report-path",
                str(zero_report_path),
                "--attempt-id",
                "cli-att-zero",
                "--source-revision-id",
                "cli-rev-001",
                "--selected-stream-index",
                "1",
                "--top-k",
                "5",
                "--fake-embedder",
            ]
        )

    assert z_code == 0
    assert z_summary["stage_status"] == "SUCCEEDED"
    assert z_summary["result_kind"] == "ZERO_MATCH"
    assert z_summary["returned_candidate_count"] == 0
    assert zero_report_path.is_file()


def test_cli_snapshot_divergence_and_partial_failure_leave_no_report(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "live_source.mp4"
    source_sha, _ = _make_source_file(source_path, b"original-snapshot-bytes")
    snap_root = tmp_path / "snap_store"
    store = SourceSnapshotStore(
        snap_root, max_source_bytes=1024 * 1024, max_store_bytes=10 * 1024 * 1024
    )
    snap = store.capture(
        source_path.resolve(),
        expected_sha256=source_sha,
        authorization_id="synthetic-auth:att-snap",
        source_revision_id="rev-snap",
    )
    snap_id = snap.snapshot_path.parent.name

    # Mutate live source after snapshot capture -> preverified snapshot check must refuse
    source_path.write_bytes(b"mutated-live-source-bytes")
    out_snap = tmp_path / "out_snap"
    code_div, sum_div, _ = _run_cli_in_process(
        [
            "analyze-local",
            "--source",
            str(source_path),
            "--query",
            "adagio",
            "--index-root",
            str(tmp_path / "idx_snap"),
            "--output-root",
            str(out_snap),
            "--attempt-id",
            "att-snap",
            "--source-revision-id",
            "rev-snap",
            "--source-snapshot-root",
            str(snap_root),
            "--max-source-bytes",
            str(1024 * 1024),
            "--max-store-bytes",
            str(10 * 1024 * 1024),
            "--preverified-snapshot-id",
            snap_id,
            "--fake-embedder",
        ]
    )
    assert code_div == 1
    assert sum_div["error_code"] == "SOURCE_SNAPSHOT_LIVE_SOURCE_DIVERGED"
    assert not (out_snap / "semantic-report.json").exists()

    # Partial failure during query -> nonzero exit and no partial report or temp file left behind
    failing_engine = _SqliteBackedStubEngine(stream_index=1)
    failing_engine.query = mock.Mock(side_effect=RuntimeError("simulated query crash"))  # type: ignore[method-assign]
    out_fail = tmp_path / "out_fail"
    with (
        mock.patch(
            "vip_fvs.core_analysis._build_default_runtime",
            return_value=_make_stub_runtime(),
        ),
        mock.patch(
            "vip_fvs.core_analysis._build_default_engine",
            return_value=failing_engine,
        ),
        mock.patch(
            "vip_fvs.core_analysis.probe_real_source",
            side_effect=_make_probe_fn(selected_stream_index=1),
        ),
    ):
        code_fail, sum_fail, _ = _run_cli_in_process(
            [
                "analyze-local",
                "--source",
                str(source_path),
                "--query",
                "adagio",
                "--index-root",
                str(tmp_path / "idx_fail"),
                "--output-root",
                str(out_fail),
                "--attempt-id",
                "att-fail",
                "--source-revision-id",
                "rev-fail",
                "--selected-stream-index",
                "1",
                "--fake-embedder",
            ]
        )
    assert code_fail == 1
    assert sum_fail["error_code"] == "QUERY_EXECUTION_FAILED"
    assert not out_fail.exists() or list(out_fail.rglob("*")) == []


def test_fresh_process_cli_refusals_and_command_coexistence(tmp_path: Path) -> None:
    # Verify all existing CLI commands and analyze-local coexist in _parser()
    parser = cli._parser()
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, cli.argparse._SubParsersAction)
    ]
    assert len(subparsers_actions) == 1
    registered_commands = set(subparsers_actions[0].choices.keys())
    expected_commands = {
        "run",
        "index-local",
        "query-local",
        "query-multi",
        "prepare-real",
        "resume-real",
        "preview-real",
        "preview-fixture",
        "query-batch-synthetic",
        "query-three-arm-synthetic",
        "analyze-local",
    }
    assert expected_commands.issubset(registered_commands)

    # Fresh subprocess invocation for real-mode missing authorization refusal
    env = dict(os.environ)
    repo_root = Path(__file__).resolve().parents[3]
    env["PYTHONPATH"] = f"{repo_root / 'src'}:{repo_root / 'experiments'}:{repo_root}"
    cli_args = [
        "analyze-local",
        "--source",
        str(tmp_path / "nonexistent.mp4"),
        "--query",
        "pas de deux",
        "--index-root",
        str(tmp_path / "idx"),
        "--output-root",
        str(tmp_path / "out"),
        "--attempt-id",
        "subproc-att-1",
        "--source-revision-id",
        "subproc-rev-1",
    ]
    proc = subprocess.run(
        [sys.executable, "-m", "vip_fvs.cli", *cli_args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 and "ModuleNotFoundError: No module named 'numpy'" in proc.stderr:
        # Fallback for bare container without numpy/PIL installed
        runner_code = (
            "import sys, types; "
            "np = types.ModuleType('numpy'); np.ndarray = object; np.float32 = float; np.float64 = float; "
            "np.dtype = lambda *a, **k: types.SimpleNamespace(itemsize=4); sys.modules['numpy'] = np; "
            "pil = types.ModuleType('PIL'); pil.Image = types.SimpleNamespace(Image=object, open=lambda *a, **k: None); "
            "sys.modules['PIL'] = pil; sys.modules['PIL.Image'] = pil.Image; "
            "from vip_fvs.cli import main; sys.exit(main(sys.argv[1:]))"
        )
        proc = subprocess.run(
            [sys.executable, "-c", runner_code, *cli_args],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    assert proc.returncode == 1
    stdout_lines = [line for line in proc.stdout.strip().splitlines() if line.strip()]
    assert len(stdout_lines) == 1
    payload = json.loads(stdout_lines[0])
    assert payload["command"] == "analyze-local"
    assert payload["stage_status"] == "FAILED"
    assert payload["result_kind"] == "REFUSED"
    assert payload["error_code"] == "AUTHORIZATION_REQUIRED_BEFORE_REAL_SOURCE_ACCESS"
    assert not (tmp_path / "out" / "semantic-report.json").exists()


def test_cli_analyze_local_with_real_ffprobe_audio_first_container(
    tmp_path: Path,
) -> None:
    ffmpeg_bin = Path("/usr/bin/ffmpeg")
    ffprobe_bin = Path("/usr/bin/ffprobe")
    if not (ffmpeg_bin.is_file() and ffprobe_bin.is_file()):
        return

    tmp_path.mkdir(parents=True, exist_ok=True)
    media_path = tmp_path / "audio_first_synth.mp4"
    gen_cmd = [
        str(ffmpeg_bin),
        "-y",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=48000:cl=mono",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=64x64:r=10:d=1.0",
        "-t",
        "1.0",
        "-map",
        "0:a:0",
        "-map",
        "1:v:0",
        "-c:a",
        "aac",
        "-c:v",
        "mpeg4",
        "-video_track_timescale",
        "1000",
        str(media_path),
    ]
    subprocess.run(gen_cmd, check=True, capture_output=True)

    # Probe with real probe_real_source via cli.main (no mock on probe_real_source)
    stub_engine = _SqliteBackedStubEngine(
        sample_rows=[(0, 0, 0.85), (1, 500, 0.65)],
        stream_index=1,
        timebase=(1, 1000),
    )
    out_root = tmp_path / "out_ffprobe"
    with (
        mock.patch(
            "vip_fvs.core_analysis._build_default_runtime",
            return_value=_make_stub_runtime(),
        ),
        mock.patch(
            "vip_fvs.core_analysis._build_default_engine",
            return_value=stub_engine,
        ),
    ):
        exit_code, summary, _ = _run_cli_in_process(
            [
                "analyze-local",
                "--source",
                str(media_path),
                "--query",
                "blue stage frame",
                "--index-root",
                str(tmp_path / "idx_ffprobe"),
                "--output-root",
                str(out_root),
                "--attempt-id",
                "att-ffprobe-1",
                "--source-revision-id",
                "rev-ffprobe-1",
                "--probe-executable",
                str(ffprobe_bin),
                "--fake-embedder",
            ]
        )

    assert exit_code == 0
    assert summary["selected_stream_index"] == 1
    report = json.loads((out_root / "semantic-report.json").read_text(encoding="utf-8"))
    validate_core_semantic_report(report)
    assert report["source"]["probe"]["selected_stream_index"] == 1
    assert report["matches"][0]["selected_stream_index"] == 1


class CoreAnalyzeLocalCliStdlibTestCase(unittest.TestCase):
    """Stdlib unittest wrapper for test_core_analyze_local_cli.py."""

    def test_all_cli_integration_scenarios(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_cli_analyze_local_positive_zero_match_and_no_clobber(root / "c1")
            test_cli_snapshot_divergence_and_partial_failure_leave_no_report(root / "c2")
            test_fresh_process_cli_refusals_and_command_coexistence(root / "c3")
            test_cli_analyze_local_with_real_ffprobe_audio_first_container(root / "c4")


if __name__ == "__main__":
    unittest.main()
