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

from decimal import Decimal, InvalidOperation
from fractions import Fraction
import math
from PIL import Image

#: `showinfo` emits source-native presentation times; capture them in order.
SHOWINFO_PTS_TIME = re.compile(r"pts_time:([0-9]+(?:\.[0-9]+)?)")
SHOWINFO_CONFIG_TIMEBASE = re.compile(r"config in time_base:\s*([^\s,]+)")
SHOWINFO_FRAME_TIMING = re.compile(
    r"(?:(?<!\w)pts:\s*(?P<pts>[^\s]+)\s+)?(?<!\w)pts_time:\s*(?P<pts_time>[^\s]+)"
)

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


def _parse_rational_timebase(
    raw: object, *, error_prefix: str = "UNSUPPORTED_TIMEBASE"
) -> tuple[int, int]:
    if not isinstance(raw, str):
        raise ValueError(f"{error_prefix}:{raw!r}")
    cleaned = raw.strip()
    if not cleaned or cleaned.count("/") != 1:
        raise ValueError(f"{error_prefix}:{raw!r}")
    num_text, den_text = cleaned.split("/", 1)
    if not num_text or not den_text:
        raise ValueError(f"{error_prefix}:{raw!r}")
    try:
        num = int(num_text, 10)
        den = int(den_text, 10)
    except ValueError as exc:
        raise ValueError(f"{error_prefix}:{raw!r}") from exc
    if num <= 0 or den <= 0:
        raise ValueError(f"{error_prefix}:{raw!r}")
    return num, den


def _validate_stream_index(raw_index: object, *, missing_code: str = "MISSING_STREAM_INDEX") -> int:
    if raw_index is None:
        raise ValueError(missing_code)
    if isinstance(raw_index, bool) or not isinstance(raw_index, int) or raw_index < 0:
        raise ValueError(f"INVALID_STREAM_INDEX:{raw_index!r}")
    return raw_index


def probe_stream(video: Path, *, stream_index: int | None = None) -> StreamInfo:
    """Cheap stream-metadata probe.  Never enumerates frames."""
    video = Path(video)
    if stream_index is not None:
        _validate_stream_index(stream_index, missing_code="INVALID_STREAM_INDEX")
    select_arg = "v:0" if stream_index is None else "v"
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            select_arg,
            "-show_entries",
            "stream=index,codec_type,time_base,width,height,codec_name,duration",
            "-of",
            "json",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    if not isinstance(payload, dict):
        raise ValueError("INVALID_FFPROBE_PAYLOAD")
    streams = payload.get("streams")
    if not isinstance(streams, list) or not streams:
        raise ValueError("NO_VIDEO_STREAM")

    seen_indices: set[int] = set()
    validated_streams: list[dict[str, object]] = []
    for entry in streams:
        if not isinstance(entry, dict):
            raise ValueError("INVALID_STREAM_ENTRY")
        if "index" not in entry or entry.get("index") is None:
            raise ValueError("MISSING_STREAM_INDEX")
        entry_index = _validate_stream_index(entry.get("index"))
        if entry_index in seen_indices:
            raise ValueError(f"INCONSISTENT_STREAM_INDEX:{entry_index}")
        seen_indices.add(entry_index)
        validated_streams.append(entry)

    if stream_index is None:
        video_streams = [
            entry
            for entry in validated_streams
            if entry.get("codec_type") in (None, "video")
        ]
        if not video_streams:
            raise ValueError("NO_VIDEO_STREAM")
        stream = video_streams[0]
    else:
        matching = [
            entry
            for entry in validated_streams
            if entry.get("index") == stream_index
        ]
        if not matching:
            raise ValueError(f"STREAM_INDEX_NOT_FOUND:{stream_index}")
        stream = matching[0]
        codec_type = stream.get("codec_type")
        if codec_type not in (None, "video"):
            raise ValueError(f"NOT_VIDEO_STREAM:{stream_index}:{codec_type!r}")

    resolved_stream_index = _validate_stream_index(stream.get("index"))
    num, den = _parse_rational_timebase(
        stream.get("time_base"), error_prefix="UNSUPPORTED_TIMEBASE"
    )
    duration = stream.get("duration")
    try:
        duration_seconds = float(duration) if duration is not None else None
    except (TypeError, ValueError):
        duration_seconds = None
    return StreamInfo(
        stream_index=resolved_stream_index,
        codec=str(stream.get("codec_name") or "UNKNOWN"),
        width=int(stream.get("width") or 0),
        height=int(stream.get("height") or 0),
        timebase_num=num,
        timebase_den=den,
        duration_seconds=duration_seconds,
    )


def _recover_frame_pts_and_seconds(
    *,
    raw_pts: str | None,
    raw_pts_time: str,
    timebase_num: int,
    timebase_den: int,
) -> tuple[int, float]:
    try:
        pts_time = float(raw_pts_time)
        pts_time_dec = Decimal(raw_pts_time)
    except (ValueError, InvalidOperation) as exc:
        raise ValueError(f"INVALID_PTS_TIME:{raw_pts_time!r}") from exc
    if not math.isfinite(pts_time):
        raise ValueError(f"INVALID_PTS_TIME:{raw_pts_time!r}")
    if pts_time < 0 or pts_time_dec < 0:
        raise ValueError(f"NEGATIVE_PTS:{raw_pts_time!r}")

    tb_fraction = Fraction(timebase_num, timebase_den)
    exact_ticks = Fraction(pts_time_dec) / tb_fraction
    derived_pts = int(round(exact_ticks))

    if raw_pts is not None:
        if not re.fullmatch(r"[+-]?[0-9]+", raw_pts):
            raise ValueError(f"INVALID_PTS:{raw_pts!r}")
        pts = int(raw_pts, 10)
        if pts < 0:
            raise ValueError(f"NEGATIVE_PTS:{pts}")
    else:
        pts = derived_pts
        if pts < 0:
            raise ValueError(f"NEGATIVE_PTS:{pts}")
        tick_error = abs(float(exact_ticks - Fraction(pts)))
        if tick_error > 1e-3:
            raise ValueError(
                f"SAMPLE_PTS_ROUNDTRIP_FAILED:{pts_time}:{pts}:"
                f"{timebase_num}/{timebase_den}"
            )

    reconstructed_seconds = float(Fraction(pts * timebase_num, timebase_den))
    # Account for showinfo av_ts2timestr %.6g formatting tolerance while refusing
    # any fractional tick or filter/stream timebase discrepancy.
    seconds_tolerance = max(1e-6, abs(reconstructed_seconds) * 1e-5)
    half_tick_seconds = 0.5 * (timebase_num / timebase_den)
    if (
        abs(reconstructed_seconds - pts_time) > seconds_tolerance
        or abs(reconstructed_seconds - pts_time) >= half_tick_seconds
    ):
        raise ValueError(
            f"SAMPLE_PTS_ROUNDTRIP_FAILED:{pts_time}:{pts}:"
            f"{timebase_num}/{timebase_den}"
        )
    return pts, reconstructed_seconds


def sample_one_pass(
    video: Path,
    every_seconds: float,
    staging_dir: Path,
    *,
    stream_index: int | None = None,
) -> list[SampledFrame]:
    """ONE sequential decode: select ~one real frame per interval and measure its PTS.

    Selection uses the filter's source-native presentation time ``t``; the
    selected frame's PTS is read back from the same filter chain, so pixels and
    PTS are bound to the same decoded frame.
    """
    video = Path(video)
    staging_dir = Path(staging_dir)
    if (
        isinstance(every_seconds, bool)
        or not isinstance(every_seconds, (int, float))
        or not math.isfinite(every_seconds)
        or every_seconds <= 0
    ):
        raise ValueError(f"INVALID_SAMPLING_INTERVAL:{every_seconds!r}")
    if stream_index is not None:
        _validate_stream_index(stream_index, missing_code="INVALID_STREAM_INDEX")

    info = (
        probe_stream(video)
        if stream_index is None
        else probe_stream(video, stream_index=stream_index)
    )
    _validate_stream_index(info.stream_index, missing_code="MISSING_STREAM_INDEX")
    if (
        isinstance(info.timebase_num, bool)
        or not isinstance(info.timebase_num, int)
        or isinstance(info.timebase_den, bool)
        or not isinstance(info.timebase_den, int)
        or info.timebase_num <= 0
        or info.timebase_den <= 0
    ):
        raise ValueError(
            f"UNSUPPORTED_TIMEBASE:{info.timebase_num!r}/{info.timebase_den!r}"
        )

    staging_dir.mkdir(parents=True, exist_ok=True)
    for stale in staging_dir.glob("s_*.png"):
        stale.unlink()

    expression = (
        "select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,%s)',showinfo"
        % every_seconds
    )
    completed = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "info",
            "-i",
            str(video),
            "-map",
            f"0:{info.stream_index}",
            "-vf",
            expression,
            "-fps_mode",
            "passthrough",
            "-y",
            str(staging_dir / "s_%06d.png"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    images = sorted(staging_dir.glob("s_*.png"))
    if not images:
        raise ValueError("NO_SAMPLES")

    for raw_filter_tb in SHOWINFO_CONFIG_TIMEBASE.findall(completed.stderr):
        filter_num, filter_den = _parse_rational_timebase(
            raw_filter_tb, error_prefix="INVALID_FILTER_TIMEBASE"
        )
        if (filter_num, filter_den) != (info.timebase_num, info.timebase_den):
            raise ValueError(
                f"FILTER_TIMEBASE_MISMATCH:{filter_num}/{filter_den}!="
                f"{info.timebase_num}/{info.timebase_den}"
            )

    # PTS is read back from the SAME decode pass that wrote the pixels, so the
    # measured PTS and the persisted pixels provably come from one frame.
    timing_matches = list(SHOWINFO_FRAME_TIMING.finditer(completed.stderr))
    if len(timing_matches) != len(images):
        raise ValueError(f"SAMPLE_PTS_MISMATCH:{len(images)}!={len(timing_matches)}")

    frames: list[SampledFrame] = []
    for image_path, match in zip(images, timing_matches):
        pts, pts_time = _recover_frame_pts_and_seconds(
            raw_pts=match.group("pts"),
            raw_pts_time=match.group("pts_time"),
            timebase_num=info.timebase_num,
            timebase_den=info.timebase_den,
        )
        if frames and pts < frames[-1].pts:
            raise ValueError(f"NON_MONOTONIC_PTS:{pts}<{frames[-1].pts}")
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
