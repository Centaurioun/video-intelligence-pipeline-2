"""Adversarial checks for the measured real-source probe trust boundary.

These tests intentionally use a synthetic local path and an injected
``subprocess.run`` seam.  They must never invoke ffprobe, touch real media, or
exercise a provider/model runtime.  The probe implementation is expected to
fail closed before any downstream inventory/retrieval work when its local
source, subprocess, or stream-selection contract is invalid.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
import sys
import textwrap
import time

import pytest

from vip_fvs.real_source_probe import MeasuredProbeRefusal, assert_source_unchanged, probe_real_source


def _probe_json(*streams: dict[str, object]) -> str:
    return json.dumps({"streams": list(streams)}, sort_keys=True)


def _video(*, index: int = 0, time_base: str = "1/1000") -> dict[str, object]:
    return {
        "index": index,
        "codec_type": "video",
        "time_base": time_base,
        "width": 16,
        "height": 16,
    }


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "synthetic-source.mp4"
    source.write_bytes(b"synthetic source bytes")
    return source


def _completed(stdout: str, *, returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["ffprobe"], returncode=returncode, stdout=stdout, stderr=stderr)


def test_probe_uses_explicit_argv_and_persists_raw_and_canonical_evidence(tmp_path, monkeypatch):
    source = _source(tmp_path)
    executable = tmp_path / "ffprobe-test-double"
    executable.write_text("synthetic executable", encoding="utf-8")
    payload = _probe_json(_video())
    calls: list[dict[str, object]] = []

    def fake_run(argv, **kwargs):
        calls.append({"argv": argv, **kwargs})
        return _completed(payload)

    monkeypatch.setattr("vip_fvs.real_source_probe.subprocess.run", fake_run)

    binding = probe_real_source(
        source,
        executable=executable,
        timeout_seconds=2.5,
        selected_stream_index=None,
        source_revision_id="rev-synthetic-probe",
        policy_identity="policy-probe-synthetic",
        run_dir=tmp_path / "run",
    )

    assert len(calls) == 1
    invocation = calls[0]
    argv = invocation["argv"]
    assert isinstance(argv, list)
    assert argv[0] == str(executable)
    assert str(source) in argv
    assert "-of" in argv and "json" in argv
    # Real-source preparation derives source-native intervals only from
    # measured frame/packet presentation timestamps.  The production probe
    # command must therefore request those records, not only stream metadata.
    assert "-show_frames" in argv
    assert "-show_packets" in argv
    assert all(isinstance(item, str) for item in argv)
    assert invocation["shell"] is False
    assert invocation["timeout"] == 2.5
    assert binding.source_path == source
    assert binding.source_revision_id == "rev-synthetic-probe"
    assert binding.source_sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
    assert binding.source_byte_count == source.stat().st_size
    assert (binding.timebase_num, binding.timebase_den) == (1, 1000)
    assert binding.selected_stream_index == 0
    assert binding.probe_digest
    assert Path(binding.probe_artifact_ref).exists()
    artifact_root = Path(binding.probe_artifact_ref).parent
    assert any(path.is_file() and "raw" in path.name for path in artifact_root.iterdir())
    assert any(path.is_file() and "canonical" in path.name for path in artifact_root.iterdir())


def test_probe_default_timeout_matches_authorized_per_command_ceiling(tmp_path, monkeypatch):
    source = _source(tmp_path)
    observed: dict[str, object] = {"streams": [_video()]}
    calls: list[dict[str, object]] = []

    def fake_run(argv, **kwargs):
        calls.append({"argv": argv, **kwargs})
        return _completed(json.dumps(observed))

    monkeypatch.setattr("vip_fvs.real_source_probe.subprocess.run", fake_run)
    probe_real_source(
        source,
        executable=tmp_path / "ffprobe-test-double",
        source_revision_id="rev-synthetic-default-timeout",
        policy_identity="policy-synthetic-default-timeout",
        run_dir=tmp_path / "run",
    )

    assert len(calls) == 1
    assert calls[0]["timeout"] == 600


def test_probe_explicit_none_disables_only_the_subprocess_deadline(tmp_path, monkeypatch):
    source = _source(tmp_path)
    calls: list[dict[str, object]] = []

    def fake_run(argv, **kwargs):
        calls.append({"argv": argv, **kwargs})
        return _completed(_probe_json(_video()))

    monkeypatch.setattr("vip_fvs.real_source_probe._run_probe_process", fake_run)
    probe_real_source(
        source,
        executable=tmp_path / "ffprobe-test-double",
        timeout_seconds=None,
        source_revision_id="rev-synthetic-unbounded-probe",
        policy_identity="policy-synthetic-unbounded-probe",
        run_dir=tmp_path / "run",
    )

    assert len(calls) == 1
    assert calls[0]["timeout_seconds"] is None


def test_probe_manual_cancellation_publishes_no_evidence_and_preserves_source(tmp_path):
    source = _source(tmp_path)
    before = source.read_bytes()
    run_dir = tmp_path / "run"

    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        probe_real_source(
            source,
            executable=tmp_path / "ffprobe-test-double",
            timeout_seconds=None,
            source_revision_id="rev-synthetic-cancelled-probe",
            policy_identity="policy-synthetic-cancelled-probe",
            run_dir=run_dir,
            runner=interrupted,
        )

    assert source.read_bytes() == before
    assert not run_dir.exists()


@pytest.mark.skipif(os.name != "posix", reason="synthetic child cancellation test requires POSIX signals")
def test_probe_manual_interrupt_kills_and_reaps_ffprobe_child(tmp_path):
    source = _source(tmp_path)
    pid_file = tmp_path / "fake-ffprobe.pid"
    executable = tmp_path / "slow-ffprobe"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import os, signal, time\n"
        "signal.signal(signal.SIGINT, signal.SIG_IGN)\n"
        "open(os.environ['VIP_TEST_CHILD_PID_FILE'], 'w').write(str(os.getpid()))\n"
        "time.sleep(30)\n",
        encoding="utf-8",
    )
    executable.chmod(0o700)
    caller = textwrap.dedent("""\
        import os, signal, sys, threading, time
        from pathlib import Path
        from vip_fvs.real_source_probe import probe_real_source
        source, executable, pid_file = map(Path, sys.argv[1:])
        def interrupt_after_child_starts():
            deadline = time.monotonic() + 5
            while not pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            time.sleep(0.1)
            os.kill(os.getpid(), signal.SIGINT)
        threading.Thread(target=interrupt_after_child_starts, daemon=True).start()
        try:
            probe_real_source(source, executable=executable, timeout_seconds=None,
                source_revision_id="rev-test-interrupt", policy_identity="policy-test-interrupt")
        except KeyboardInterrupt:
            child_pid = int(pid_file.read_text(encoding="utf-8"))
            try:
                waited_pid, _ = os.waitpid(child_pid, os.WNOHANG)
            except ChildProcessError:
                raise SystemExit(23)
            if waited_pid == child_pid:
                raise SystemExit(24)
            os.kill(child_pid, 9)
            os.waitpid(child_pid, 0)
            raise SystemExit(25)
        raise SystemExit(0)
    """)
    environment = dict(os.environ, VIP_TEST_CHILD_PID_FILE=str(pid_file))
    completed = subprocess.run(
        [sys.executable, "-c", caller, str(source), str(executable), str(pid_file)],
        env=environment, capture_output=True, text=True, timeout=8,
    )
    assert completed.returncode == 23, completed.stderr
    assert pid_file.exists(), "the synthetic FFprobe child did not start"


def test_probe_retains_measured_frame_and_packet_pts_evidence(tmp_path, monkeypatch):
    source = _source(tmp_path)
    executable = tmp_path / "ffprobe-test-double"
    executable.write_text("synthetic executable", encoding="utf-8")
    payload = json.dumps({
        "streams": [_video()],
        "frames": [{"stream_index": 0, "best_effort_timestamp": "40"}],
        "packets": [{"stream_index": 0, "pts": "80"}],
    })
    monkeypatch.setattr(
        "vip_fvs.real_source_probe.subprocess.run",
        lambda argv, **kwargs: _completed(payload),
    )

    binding = probe_real_source(
        source,
        executable=executable,
        source_revision_id="rev-synthetic-pts",
        policy_identity="policy-synthetic-pts",
        run_dir=tmp_path / "run",
    )

    assert binding.ffprobe_json["frames"][0]["best_effort_timestamp"] == "40"
    assert binding.ffprobe_json["packets"][0]["pts"] == "80"


def test_probe_rejects_url_like_source_without_invoking_subprocess(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "vip_fvs.real_source_probe.subprocess.run",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    with pytest.raises(MeasuredProbeRefusal, match="LOCAL_SOURCE_REQUIRED"):
        probe_real_source(
            Path("https://example.invalid/video.mp4"),
            executable=tmp_path / "ffprobe",
            timeout_seconds=1,
            selected_stream_index=None,
            source_revision_id="rev-url",
            policy_identity="policy-url",
            run_dir=tmp_path / "run",
        )
    assert calls == []


@pytest.mark.parametrize(
    ("stdout", "returncode", "reason"),
    [
        (_probe_json(_video()), 1, "PROBE_NONZERO_EXIT"),
        ("not-json", 0, "PROBE_INVALID_JSON"),
        (json.dumps({"streams": [{"index": 0, "codec_type": "audio"}]}), 0, "NO_VIDEO_STREAM"),
        (_probe_json(_video(index=0), _video(index=1)), 0, "AMBIGUOUS_VIDEO_STREAM"),
        (_probe_json(_video(time_base="0/1000")), 0, "INVALID_TIMEBASE"),
    ],
)
def test_probe_refuses_invalid_or_ambiguous_subprocess_evidence(
    tmp_path, monkeypatch, stdout, returncode, reason,
):
    source = _source(tmp_path)
    monkeypatch.setattr(
        "vip_fvs.real_source_probe.subprocess.run",
        lambda *args, **kwargs: _completed(stdout, returncode=returncode),
    )

    with pytest.raises(MeasuredProbeRefusal, match=reason):
        probe_real_source(
            source,
            executable=tmp_path / "ffprobe",
            timeout_seconds=1,
            selected_stream_index=None,
            source_revision_id="rev-invalid-probe",
            policy_identity="policy-invalid-probe",
            run_dir=tmp_path / "run",
        )


def test_explicit_stream_selection_is_required_to_disambiguate_multiple_video_streams(tmp_path, monkeypatch):
    source = _source(tmp_path)
    payload = _probe_json(_video(index=0), _video(index=1))
    monkeypatch.setattr(
        "vip_fvs.real_source_probe.subprocess.run",
        lambda *args, **kwargs: _completed(payload),
    )

    binding = probe_real_source(
        source,
        executable=tmp_path / "ffprobe",
        timeout_seconds=1,
        selected_stream_index=1,
        source_revision_id="rev-selected-stream",
        policy_identity="policy-selected-stream",
        run_dir=tmp_path / "run",
    )
    assert binding.selected_stream_index == 1


def test_source_mutation_after_probe_is_quarantined(tmp_path, monkeypatch):
    source = _source(tmp_path)
    monkeypatch.setattr(
        "vip_fvs.real_source_probe.subprocess.run",
        lambda *args, **kwargs: _completed(_probe_json(_video())),
    )
    binding = probe_real_source(
        source,
        executable=tmp_path / "ffprobe",
        timeout_seconds=1,
        selected_stream_index=None,
        source_revision_id="rev-mutation",
        policy_identity="policy-mutation",
        run_dir=tmp_path / "run",
    )

    source.write_bytes(b"mutated after measured probe")
    with pytest.raises(MeasuredProbeRefusal, match="SOURCE_DIGEST_MISMATCH"):
        assert_source_unchanged(binding)


def test_source_mutation_during_artifact_publication_fails_closed(tmp_path, monkeypatch):
    source = _source(tmp_path)
    monkeypatch.setattr(
        "vip_fvs.real_source_probe.subprocess.run",
        lambda *args, **kwargs: _completed(_probe_json(_video())),
    )
    original_write_bytes = Path.write_bytes

    def write_and_mutate(path, data):
        result = original_write_bytes(path, data)
        if path.name == "probe-canonical.json":
            source.write_bytes(b"mutated during artifact publication")
        return result

    monkeypatch.setattr(Path, "write_bytes", write_and_mutate)
    with pytest.raises(MeasuredProbeRefusal, match="SOURCE_DIGEST_MISMATCH"):
        probe_real_source(
            source,
            executable=tmp_path / "ffprobe",
            source_revision_id="rev-publication-mutation",
            policy_identity="policy-publication-mutation",
            run_dir=tmp_path / "run",
        )
