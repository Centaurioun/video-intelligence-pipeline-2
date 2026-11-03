"""Adversarial authority checks for the local-only preview seam."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
from subprocess import CompletedProcess

import pytest

from vip_fvs.local_preview import LocalPreviewAdapter, PreviewRefusal
from tests.vip_fvs.unit.test_local_preview import _auth, _plan


class RecordingRunner:
    def __init__(self, *, duplicate_stream: bool = False):
        self.calls: list[list[str]] = []
        self.duplicate_stream = duplicate_stream

    def __call__(self, argv, **kwargs):
        self.calls.append(list(argv))
        if argv[0].endswith("ffprobe"):
            streams = [{"index": 0, "codec_type": "video", "time_base": "1/1000"}]
            if self.duplicate_stream:
                streams.append(dict(streams[0]))
            return CompletedProcess(argv, 0, stdout=json.dumps({"streams": streams}).encode(), stderr=b"")
        Path(argv[-1]).write_bytes(b"preview-bytes")
        return CompletedProcess(argv, 0, stdout=b"", stderr=b"")


def _paths(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "previews"
    source.write_bytes((Path(tempfile.gettempdir()) / "vip-fvs-v3-plan-fixture.mp4").read_bytes())
    ffprobe, ffmpeg = tmp_path / "ffprobe", tmp_path / "ffmpeg"
    ffprobe.write_bytes(b"probe-tool")
    ffmpeg.write_bytes(b"ffmpeg-tool")
    return source, output, ffprobe, ffmpeg


def test_authorization_pins_tool_identity_and_config_before_subprocess(monkeypatch, tmp_path: Path):
    artifacts = _plan(monkeypatch)
    source, output, ffprobe, ffmpeg = _paths(tmp_path)
    auth = _auth(artifacts, source, output)
    tampered = auth.__class__(**{**auth.__dict__, "ffmpeg_tool_digest": "0" * 64, "record_digest": ""})
    runner = RecordingRunner()
    with pytest.raises(PreviewRefusal, match="TOOL_IDENTITY_MISMATCH"):
        LocalPreviewAdapter(runner=runner).render_preview(
            artifacts, authorization=tampered, source_path=source, output_root=output,
            ffprobe_executable=ffprobe, ffmpeg_executable=ffmpeg,
        )
    assert runner.calls == []


def test_authorization_rejects_configuration_digest_drift_before_subprocess(monkeypatch, tmp_path: Path):
    artifacts = _plan(monkeypatch)
    source, output, ffprobe, ffmpeg = _paths(tmp_path)
    auth = _auth(artifacts, source, output)
    tampered = auth.__class__(**{**auth.__dict__, "tool_config_digest": "0" * 64, "record_digest": ""})
    runner = RecordingRunner()
    with pytest.raises(PreviewRefusal, match="TOOL_CONFIG_MISMATCH"):
        LocalPreviewAdapter(runner=runner).render_preview(
            artifacts, authorization=tampered, source_path=source, output_root=output,
            ffprobe_executable=ffprobe, ffmpeg_executable=ffmpeg,
        )
    assert runner.calls == []


def test_duplicate_selected_stream_records_fail_closed(monkeypatch, tmp_path: Path):
    artifacts = _plan(monkeypatch)
    source, output, ffprobe, ffmpeg = _paths(tmp_path)
    runner = RecordingRunner(duplicate_stream=True)
    with pytest.raises(PreviewRefusal, match="PROBE_MISMATCH"):
        LocalPreviewAdapter(runner=runner).render_preview(
            artifacts, authorization=_auth(artifacts, source, output), source_path=source,
            output_root=output, ffprobe_executable=ffprobe, ffmpeg_executable=ffmpeg,
        )
    assert len(runner.calls) == 1
    assert not output.exists() or not any(output.iterdir())
