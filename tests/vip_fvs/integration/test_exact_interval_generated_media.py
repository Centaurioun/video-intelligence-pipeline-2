"""Real local ffmpeg integration coverage for the exact PTS-cut contract.

Only generated media is used.  This test deliberately does not load an owner
authorization or touch any real source.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


FFMPEG = Path("/opt/homebrew/bin/ffmpeg")
FFPROBE = Path("/opt/homebrew/bin/ffprobe")


def test_generated_nonkeyframe_interval_preserves_exact_output_ticks(tmp_path: Path):
    if not FFMPEG.is_file() or not FFPROBE.is_file():
        raise AssertionError("required local ffmpeg/ffprobe are unavailable")
    source = tmp_path / "generated-cfr.mp4"
    output = tmp_path / "exact-cut.mp4"
    subprocess.run(
        [str(FFMPEG), "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=160x90:rate=60",
         "-frames:v", "12", "-c:v", "libx264", "-g", "12", "-pix_fmt", "yuv420p",
         "-video_track_timescale", "600", str(source)], check=True,
        capture_output=True, text=True,
    )
    subprocess.run(
        [str(FFMPEG), "-v", "error", "-nostdin", "-copyts", "-i", str(source), "-map", "0:0",
         "-vf", "trim=start_pts=10:end_pts=20,setpts=PTS-STARTPTS", "-c:v", "libx264",
         "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p", "-fps_mode", "passthrough",
         "-video_track_timescale", "600", "-an", "-f", "mp4", str(output)], check=True,
        capture_output=True, text=True,
    )
    probe = subprocess.run(
        [str(FFPROBE), "-v", "error", "-of", "json", "-show_streams", "-show_frames", str(output)],
        check=True, capture_output=True, text=True,
    )
    payload = json.loads(probe.stdout)
    videos = [s for s in payload["streams"] if s.get("codec_type") == "video"]
    assert len(videos) == 1
    assert videos[0]["time_base"] == "1/600"
    assert int(videos[0]["duration_ts"]) == 10
    frames = [f for f in payload["frames"] if f.get("media_type") == "video"]
    assert len(frames) == 1
    assert int(frames[0]["pts"]) == 0
