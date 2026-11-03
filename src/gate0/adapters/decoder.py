"""Decoder seam for synthetic Gate-0 temporal tests.

The adapter deliberately preserves the supplied presentation sequence. It does
not infer frames from a nominal frame rate or reorder by PTS.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Sequence

from gate0.inventory import RevisionRef


@dataclass(frozen=True)
class DecodedFrame:
    raw_pts_ticks: int | None
    time_base_num: int
    time_base_den: int
    decoder_ordinal: int | None
    presentation_order: int | None
    selected_frame_id: str | None
    pixels: bytes | None = None
    status: str = "DECODED"
    dts_ticks: int | None = None
    frame_index: int | None = None
    source_frame_identity: str | None = None

    def __post_init__(self) -> None:
        if self.source_frame_identity is None and self.selected_frame_id is not None:
            object.__setattr__(self, "source_frame_identity", self.selected_frame_id)


class DecoderAdapter:
    def iter_frames(self, source: RevisionRef, stream_index: int) -> Iterator[DecodedFrame]:
        raise NotImplementedError


class SyntheticDecoder(DecoderAdapter):
    def __init__(self, frames: Sequence[DecodedFrame]):
        self.frames = tuple(frames)

    def iter_frames(self, source: RevisionRef, stream_index: int) -> Iterator[DecodedFrame]:
        if stream_index != source.selected_stream_index:
            raise ValueError("SELECTED_STREAM_MISMATCH")
        yield from self.frames

