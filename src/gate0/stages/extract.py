"""Extract stage over an injected decoder and immutable selected stream."""
from __future__ import annotations

from gate0.adapters.decoder import DecoderAdapter
from gate0.inventory import RevisionRef
from gate0.temporal import SampleTarget, sample_targets


def extract(revision: RevisionRef, decoder: DecoderAdapter, *, window_count: int = 1, duration: int | float | None = None, origin_pts_ticks: int | None = None, interval_id: str = "interval_0") -> tuple[SampleTarget, ...]:
    frames = decoder.iter_frames(revision, revision.selected_stream_index)
    return sample_targets(revision, frames, window_count=window_count, duration=duration, origin_pts_ticks=origin_pts_ticks, interval_id=interval_id)

