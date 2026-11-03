"""Gate-3 stream-identity namespace safety (A-7).

Authority
---------
``docs/agent-runs/2026-10-25-g3-cprime-v1/authority-disposition-matrix.md``
records A-7 as ``(c) PENDING``: the FFprobe *global stream index* and the
ISO-BMFF *all-trak ordinal* are distinct namespaces, and the design
(§6, §11, OQ-1) requires a composed authority to prove a mapping or refuse
``TEMPORAL_AUTHORITY_STREAM_IDENTITY_DIVERGENCE``.  The matrix' interim rule is
explicit: code may implement **refusal only**; accepting a guessed mapping
violates the S2 fail-closed constraint ("never accept an unproven stream
mapping").

These tests pin that refusal on the byte-bound refinement surface
(``vip_fvs.refinement_adapter``), which today accepts temporal evidence when the
caller-supplied FFprobe ordinal merely *equals* the container's all-trak
ordinal.  Equality of two integers from different namespaces is not identity
evidence: any preceding non-video stream (or a second video trak) shifts one
namespace relative to the other.

Every fixture is synthetic bytes built in-process by ``gate3.fixturegen``; no
real media, network, provider, model or ffmpeg dependency is involved.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from gate3.container import EXPLICIT_SELECTION_DERIVATION, SOLE_VIDEO_DERIVATION
from gate3.container import parse_iso_bmff_timing
from gate3.fixturegen import build_mp4, build_multi_trak_mp4
from vip_fvs.refinement_adapter import RefinementRefusal, refine_retrieval_candidate

MEDIA_TIMESCALE = 1000
UNIFORM_DELTAS = (40, 40, 40)

AUDIO_THEN_VIDEO_BYTES = build_multi_trak_mp4(
    media_timescale=MEDIA_TIMESCALE,
    traks=[
        {"media_timescale": MEDIA_TIMESCALE, "sample_deltas": UNIFORM_DELTAS,
         "handler": b"soun"},
        {"media_timescale": MEDIA_TIMESCALE, "sample_deltas": UNIFORM_DELTAS,
         "handler": b"vide"},
    ],
)

TWO_VIDEO_TRAKS_BYTES = build_multi_trak_mp4(
    media_timescale=MEDIA_TIMESCALE,
    traks=[
        {"media_timescale": MEDIA_TIMESCALE, "sample_deltas": UNIFORM_DELTAS,
         "handler": b"vide"},
        {"media_timescale": MEDIA_TIMESCALE, "sample_deltas": UNIFORM_DELTAS,
         "handler": b"vide"},
    ],
)

SINGLE_TRAK_BYTES = build_mp4(
    media_timescale=MEDIA_TIMESCALE,
    sample_deltas=UNIFORM_DELTAS,
)


def _write(tmp_path: Path, name: str, blob: bytes) -> Path:
    path = tmp_path / f"{name}.mp4"
    path.write_bytes(blob)
    return path


def _measured(path: Path, selected_stream_index: int) -> dict:
    """Parse the fixture the same way the production adapter does."""
    return parse_iso_bmff_timing(path, selected_stream_index=selected_stream_index)


def _refine(path: Path, selected_stream_index: int):
    measured = _measured(path, selected_stream_index)
    hit = {
        "source_path": str(path),
        "source_sha256": measured["source_bytes_sha256"],
        "pts": int(measured["pts_ticks"][-1]),
        "timebase_num": 1,
        "timebase_den": int(measured["media_timescale"]),
        "rank": 1,
        "score": 0.9,
    }
    return refine_retrieval_candidate(
        hit,
        source_revision_id="revision:synthetic-namespace",
        requested_pts=(int(measured["pts_ticks"][0]), int(measured["pts_ticks"][-1])),
        stream_index=selected_stream_index,
        selected_stream_index=selected_stream_index,
        attempt_id="attempt:synthetic-namespace",
        stage_idempotency_key="real-source:synthetic-namespace",
        tool_identity={"name": "vip_fvs.real_source_service", "version": "v3"},
    )


def test_audio_before_video_explicit_ordinal_refuses_temporal_binding(
    tmp_path: Path,
) -> None:
    """A trak ordinal that equals an FFprobe index proves nothing when an audio
    stream precedes the video stream in the same container."""
    path = _write(tmp_path, "audio-then-video", AUDIO_THEN_VIDEO_BYTES)

    measured = _measured(path, 1)
    assert measured["stream_count"] == 2
    assert measured["stream_index"] == 1
    assert measured["stream_identity_derivation"] == EXPLICIT_SELECTION_DERIVATION

    # Equal integers in two namespaces; the mapping is unproven (A-7 PENDING).
    with pytest.raises(RefinementRefusal) as excinfo:
        _refine(path, 1)
    assert "stream identity is unproven" in str(excinfo.value)


@pytest.mark.parametrize("selected_stream_index", [0, 1])
def test_two_video_traks_cannot_be_disambiguated_by_equal_ordinals(
    tmp_path: Path, selected_stream_index: int,
) -> None:
    """With two video timing traks the ordinal is a container-layout fact, not a
    proven FFprobe stream identity, so the refinement must refuse either side."""
    path = _write(tmp_path, f"two-video-{selected_stream_index}", TWO_VIDEO_TRAKS_BYTES)

    measured = _measured(path, selected_stream_index)
    assert measured["stream_count"] == 2
    assert measured["stream_identity_derivation"] == EXPLICIT_SELECTION_DERIVATION

    with pytest.raises(RefinementRefusal) as excinfo:
        _refine(path, selected_stream_index)
    assert "stream identity is unproven" in str(excinfo.value)


def test_single_trak_explicit_selection_still_binds(tmp_path: Path) -> None:
    """A one-trak container has no competing ordinal, so the refusal must not
    overreach: the existing byte-bound refinement contract keeps binding."""
    path = _write(tmp_path, "single-trak", SINGLE_TRAK_BYTES)

    measured = _measured(path, 0)
    assert measured["stream_count"] == 1
    assert measured["stream_identity_derivation"] == EXPLICIT_SELECTION_DERIVATION

    result = _refine(path, 0)
    assert result.binding_eligible is True
    assert result.measured_refinement["evidence_class"] == "MEASURED"
    assert result.measured_refinement["stream_index"] == 0


def test_sole_video_derivation_never_needs_an_ordinal_correspondence(
    tmp_path: Path,
) -> None:
    """The parser's ``None``-selector resolution identifies the only video trak by
    uniqueness, not by ordinal correspondence, so that derivation is not a
    namespace inference."""
    path = _write(tmp_path, "audio-then-video-sole", AUDIO_THEN_VIDEO_BYTES)

    measured = parse_iso_bmff_timing(path, selected_stream_index=None)
    assert measured["stream_identity_derivation"] == SOLE_VIDEO_DERIVATION
    assert measured["stream_index"] == 1
