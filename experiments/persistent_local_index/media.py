"""Source hashing, stream probe, one-pass measured-PTS sampler, thumbnails.

Authority: approved design sections 5.3, 8, 10 and plan Task 3.

Carried forward verbatim in spirit from the preserved spike
(``experiments/single-video-semantic-spike/spike_runner.py``, head
``0c14fce1fa979d466292fbd5cfd1e876bfacee92``):

* ONE sequential FFmpeg decode pass for all samples;
* frame selection driven by the filter's source-native presentation time ``t``
  via ``select='isnan(prev_selected_t)+gte(t-prev_selected_t,INTERVAL)'``;
* the *actually decoded* frame's PTS is read back from the same filter chain via
  ``showinfo``, so emitted pixels and emitted PTS come from the SAME frame;
* integer PTS is recovered with the **probed source timebase** and verified by
  round trip.  Frame position is never ``seconds * nominal_fps``.

Full per-frame ``ffprobe -show_frames`` enumeration is deliberately NOT used in
the operational path; the preserved spike proved it was unnecessary and
dominated runtime.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

#: `showinfo` emits source-native presentation times; capture them in order.
SHOWINFO_PTS_TIME = re.compile(r"pts_time:([0-9]+(?:\.[0-9]+)?)")

#: Full-frame enumeration is a *test-only* ground truth, never an operational path.
FORBIDDEN_ENUMERATION_FLAG = "-show_frames"

DEFAULT_THUMBNAIL_MAX_SIDE = 160
DEFAULT_THUMBNAIL_QUALITY = 70


@dataclass(frozen=True)
class StreamInfo:
    stream_index: int
    codec: str
    width: int
    height: int
    timebase_num: int
    timebase_den: int
    duration_seconds: float | None


@dataclass(frozen=True)
class SampledFrame:
    pts: int
    pts_time: float
    timebase_num: int
    timebase_den: int
    timestamp_human: str
    image_path: Path


def sha256_file(path: Path) -> str:
    """SHA-256 of a file's exact bytes.  Source identity is bytes, not path."""
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"FILE_NOT_FOUND:{path.name}")
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def readable_timestamp(pts: int, timebase_num: int, timebase_den: int) -> str:
    """Human-readable candidate timestamp from exact rational PTS time."""
    total = pts * timebase_num / timebase_den
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:06.3f}"


def probe_stream(video: Path) -> StreamInfo:
    """Cheap stream-metadata probe.  Never enumerates frames."""
    video = Path(video)
    completed = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=time_base,width,height,codec_name,duration",
         "-of", "json", str(video)],
        capture_output=True, text=True, check=True,
    )
    payload = json.loads(completed.stdout)
    streams = payload.get("streams") or []
    if not streams:
        raise ValueError("NO_VIDEO_STREAM")
    stream = streams[0]
    raw_timebase = str(stream.get("time_base") or "")
    if "/" not in raw_timebase:
        raise ValueError(f"UNSUPPORTED_TIMEBASE:{raw_timebase!r}")
    num_text, den_text = raw_timebase.split("/", 1)
    num, den = int(num_text), int(den_text)
    if num <= 0 or den <= 0:
        raise ValueError(f"UNSUPPORTED_TIMEBASE:{raw_timebase!r}")
    duration = stream.get("duration")
    try:
        duration_seconds = float(duration) if duration is not None else None
    except (TypeError, ValueError):
        duration_seconds = None
    return StreamInfo(
        stream_index=0,
        codec=str(stream.get("codec_name") or "UNKNOWN"),
        width=int(stream.get("width") or 0),
        height=int(stream.get("height") or 0),
        timebase_num=num,
        timebase_den=den,
        duration_seconds=duration_seconds,
    )


def sample_one_pass(
    video: Path, every_seconds: float, staging_dir: Path
) -> list[SampledFrame]:
    """ONE sequential decode: select ~one real frame per interval and measure its PTS.

    Selection uses the filter's source-native presentation time ``t``; the
    selected frame's PTS is read back from the same filter chain, so pixels and
    PTS are bound to the same decoded frame.
    """
    video = Path(video)
    staging_dir = Path(staging_dir)
    if not (isinstance(every_seconds, (int, float)) and every_seconds > 0):
        raise ValueError(f"INVALID_SAMPLING_INTERVAL:{every_seconds!r}")
    staging_dir.mkdir(parents=True, exist_ok=True)
    for stale in staging_dir.glob("s_*.png"):
        stale.unlink()

    expression = (
        "select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,%s)',showinfo"
        % every_seconds
    )
    completed = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(video), "-vf", expression,
         "-fps_mode", "passthrough", "-y", str(staging_dir / "s_%06d.png")],
        capture_output=True, text=True, check=True,
    )
    # PTS is read back from the SAME decode pass that wrote the pixels, so the
    # measured PTS and the persisted pixels provably come from one frame.
    pts_times = [float(value) for value in SHOWINFO_PTS_TIME.findall(completed.stderr)]
    images = sorted(staging_dir.glob("s_*.png"))
    if not images:
        raise ValueError("NO_SAMPLES")

    info = probe_stream(video)
    if len(pts_times) != len(images):
        raise ValueError(f"SAMPLE_PTS_MISMATCH:{len(images)}!={len(pts_times)}")

    frames: list[SampledFrame] = []
    for image_path, pts_time in zip(images, pts_times):
        pts = int(round(pts_time * info.timebase_den))
        # round trip: measured time must be reproducible from the integer PTS
        if abs(pts * info.timebase_num / info.timebase_den - pts_time) > 1e-6:
            raise ValueError(
                f"SAMPLE_PTS_ROUNDTRIP_FAILED:{pts_time}:{pts}:"
                f"{info.timebase_num}/{info.timebase_den}"
            )
        frames.append(
            SampledFrame(
                pts=pts,
                pts_time=pts_time,
                timebase_num=info.timebase_num,
                timebase_den=info.timebase_den,
                timestamp_human=readable_timestamp(pts, info.timebase_num, info.timebase_den),
                image_path=image_path,
            )
        )
    return frames


def make_thumbnail(
    src_png: Path,
    dst_jpg: Path,
    *,
    max_side: int = DEFAULT_THUMBNAIL_MAX_SIDE,
    quality: int = DEFAULT_THUMBNAIL_QUALITY,
) -> None:
    """Retain one small JPEG inspection thumbnail.  Never upscales; never mutates source."""
    src_png = Path(src_png)
    dst_jpg = Path(dst_jpg)
    if not src_png.is_file():
        raise ValueError(f"THUMBNAIL_SOURCE_MISSING:{src_png.name}")
    dst_jpg.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src_png) as image:
        rgb = image.convert("RGB")
        longest = max(rgb.size)
        if longest > max_side:
            scale = max_side / longest
            target = (
                max(1, int(round(rgb.size[0] * scale))),
                max(1, int(round(rgb.size[1] * scale))),
            )
            rgb = rgb.resize(target, Image.Resampling.LANCZOS)
        rgb.save(dst_jpg, format="JPEG", quality=quality)
