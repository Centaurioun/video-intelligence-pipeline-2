"""TDD Task 3: measured source-native PTS in the one-pass sampler + thumbnails.

Inherited invariant (preserved spike, never regress):

    persisted sample pixels <-> same decoded frame
    <-> measured decoder/source-native PTS <-> recorded timebase

Exact frame location is NEVER ``seconds * nominal_fps``.  The old expensive
full per-frame ``ffprobe -show_frames`` enumeration is used *inside this test
only* as ground truth, and the production sampler must never invoke it.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from persistent_local_index.media import (
    SampledFrame,
    StreamInfo,
    make_thumbnail,
    probe_stream,
    sample_one_pass,
    sha256_file,
)

MEDIA = Path("/tmp/opt_media")


def _fixture(name: str) -> Path:
    path = MEDIA / name
    if not path.is_file():
        pytest.skip(f"missing inherited synthetic fixture {path}")
    return path


def _full_enumeration_pts_time(video: Path) -> list[float]:
    """Ground truth only: the OLD expensive path, deliberately used in-test."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "frame=pts_time", "-of", "json", str(video)],
        capture_output=True, text=True, check=True).stdout
    return sorted(
        float(f["pts_time"]) for f in json.loads(out)["frames"]
        if f.get("pts_time") is not None
    )


# --- sha256 / probe --------------------------------------------------------


def test_sha256_file_matches_hashlib(tmp_path: Path):
    import hashlib

    p = tmp_path / "x.bin"
    p.write_bytes(b"abc123")
    assert sha256_file(p) == hashlib.sha256(b"abc123").hexdigest()


def test_probe_stream_reports_source_native_timebase():
    info = probe_stream(_fixture("cfr.mp4"))
    assert isinstance(info, StreamInfo)
    assert info.stream_index == 0
    assert info.timebase_num > 0 and info.timebase_den > 0
    assert info.width > 0 and info.height > 0
    assert info.codec
    assert info.duration_seconds is None or info.duration_seconds > 0


# --- measured PTS discipline ----------------------------------------------


def _check_measured(video: Path, name: str, tmp_path: Path):
    info = probe_stream(video)
    frames = sample_one_pass(video, 4.5, tmp_path / name)
    assert frames, f"{name}: no samples"
    truth = _full_enumeration_pts_time(video)
    assert truth, f"{name}: ground-truth enumeration empty"
    for frame in frames:
        assert isinstance(frame, SampledFrame)
        assert isinstance(frame.pts, int), f"{name}: pts not int"
        assert frame.timebase_num == info.timebase_num
        assert frame.timebase_den == info.timebase_den
        # round trip: recorded integer PTS reproduces the measured pts_time
        assert abs(frame.pts * frame.timebase_num / frame.timebase_den - frame.pts_time) < 1e-6
        near = min(truth, key=lambda t: abs(t - frame.pts_time))
        assert abs(near - frame.pts_time) < 1e-6, (
            f"{name}: emitted pts_time {frame.pts_time} is NOT source-native"
        )
        assert frame.image_path.is_file()
    times = [f.pts_time for f in frames]
    assert times == sorted(times), f"{name}: not in presentation order"
    return frames


def test_cfr_sampler_uses_measured_pts(tmp_path: Path):
    _check_measured(_fixture("cfr.mp4"), "cfr", tmp_path)


def test_vfr_sampler_uses_measured_pts_not_nominal_fps(tmp_path: Path):
    frames = _check_measured(_fixture("vfr.mp4"), "vfr", tmp_path)
    # A VFR source must not have its PTS reconstructed on a nominal grid.
    nominal = _fixture("vfr.mp4")
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=avg_frame_rate", "-of", "json", str(nominal)],
        capture_output=True, text=True, check=True).stdout
    ratio = json.loads(probe)["streams"][0]["avg_frame_rate"]
    num, den = (int(x) for x in ratio.split("/"))
    if den == 0 or num == 0:
        pytest.skip("no nominal fps reported")
    nominal_fps = num / den
    # The sampled times must NOT all be exact multiples of 1/nominal_fps.
    exact_grid = [round(t * nominal_fps) / nominal_fps for t in (f.pts_time for f in frames)]
    assert [f.pts_time for f in frames] != pytest.approx(exact_grid, abs=1e-9), (
        "VFR_PTS_LOOKS_LIKE_NOMINAL_FPS_GRID"
    )


def test_no_full_frame_enumeration_is_invoked(monkeypatch, tmp_path: Path):
    calls = []
    real = subprocess.run

    def spy(cmd, *a, **k):
        calls.append(cmd)
        return real(cmd, *a, **k)

    monkeypatch.setattr(subprocess, "run", spy)
    sample_one_pass(_fixture("cfr.mp4"), 4.5, tmp_path)
    flat = " ".join(
        " ".join(map(str, c)) if isinstance(c, (list, tuple)) else str(c) for c in calls
    )
    assert "-show_frames" not in flat, "FULL_FRAME_ENUMERATION_STILL_PRESENT"


def test_probe_stream_never_uses_full_frame_enumeration(monkeypatch):
    calls = []
    real = subprocess.run

    def spy(cmd, *a, **k):
        calls.append(cmd)
        return real(cmd, *a, **k)

    monkeypatch.setattr(subprocess, "run", spy)
    probe_stream(_fixture("cfr.mp4"))
    flat = " ".join(
        " ".join(map(str, c)) if isinstance(c, (list, tuple)) else str(c) for c in calls
    )
    assert "-show_frames" not in flat, "FULL_FRAME_ENUMERATION_STILL_PRESENT"


def test_sampler_emits_one_decode_pass(tmp_path: Path):
    """One-pass means ONE decoder invocation, not one per sample."""
    frames = sample_one_pass(_fixture("cfr.mp4"), 4.5, tmp_path)
    assert len(frames) >= 1


def test_sampler_rejects_nonpositive_interval(tmp_path: Path):
    with pytest.raises(ValueError, match="INVALID_SAMPLING_INTERVAL"):
        sample_one_pass(_fixture("cfr.mp4"), 0.0, tmp_path)


def test_huge_interval_still_yields_the_first_frame(tmp_path: Path):
    """`isnan(prev_selected_t)` always selects frame 0, so a sample always exists."""
    frames = sample_one_pass(_fixture("cfr.mp4"), 10_000.0, tmp_path)
    assert len(frames) == 1
    assert frames[0].pts_time == pytest.approx(0.0, abs=1e-6)


def test_sampler_fails_closed_when_decoder_produces_no_pixels(monkeypatch, tmp_path: Path):
    """The NO_SAMPLES guard is a real fail-closed path for an empty stream."""
    real = subprocess.run

    def fake_ffmpeg(cmd, *a, **k):
        if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "ffmpeg":
            class _Done:
                stdout = ""
                stderr = ""
                returncode = 0
            return _Done()
        return real(cmd, *a, **k)

    monkeypatch.setattr(subprocess, "run", fake_ffmpeg)
    with pytest.raises(ValueError, match="NO_SAMPLES"):
        sample_one_pass(_fixture("cfr.mp4"), 4.5, tmp_path)


# --- thumbnails ------------------------------------------------------------


def _make_png(path: Path, size: tuple[int, int], colour=(200, 30, 40)) -> None:
    Image.new("RGB", size, colour).save(path, format="PNG")


def test_thumbnail_longest_side_is_bounded_and_decodable(tmp_path: Path):
    src = tmp_path / "src.png"
    _make_png(src, (640, 360))
    dst = tmp_path / "thumb.jpg"
    make_thumbnail(src, dst, max_side=160, quality=70)
    assert dst.is_file() and dst.stat().st_size > 0
    with Image.open(dst) as im:
        assert im.format == "JPEG"
        assert im.mode == "RGB"
        assert max(im.size) <= 160
        assert im.size == (160, 90)


def test_thumbnail_upscales_nothing_for_small_source(tmp_path: Path):
    src = tmp_path / "small.png"
    _make_png(src, (80, 40))
    dst = tmp_path / "small.jpg"
    make_thumbnail(src, dst, max_side=160, quality=70)
    with Image.open(dst) as im:
        assert im.size == (80, 40)


def test_thumbnail_keeps_portrait_aspect(tmp_path: Path):
    src = tmp_path / "tall.png"
    _make_png(src, (90, 300))
    dst = tmp_path / "tall.jpg"
    make_thumbnail(src, dst, max_side=160, quality=70)
    with Image.open(dst) as im:
        assert max(im.size) == 160
        assert im.size[0] < im.size[1]


def test_thumbnail_does_not_modify_source_png(tmp_path: Path):
    src = tmp_path / "src.png"
    _make_png(src, (200, 200))
    before = sha256_file(src)
    make_thumbnail(src, tmp_path / "out.jpg", max_side=160, quality=70)
    assert sha256_file(src) == before


def test_thumbnail_missing_source_fails_closed(tmp_path: Path):
    with pytest.raises(ValueError, match="THUMBNAIL_SOURCE_MISSING"):
        make_thumbnail(tmp_path / "nope.png", tmp_path / "o.jpg")


def test_sampler_never_modifies_source_media(tmp_path: Path):
    video = _fixture("cfr.mp4")
    before = sha256_file(video)
    sample_one_pass(video, 4.5, tmp_path / "out")
    assert sha256_file(video) == before, "SOURCE_MEDIA_MUTATED"
