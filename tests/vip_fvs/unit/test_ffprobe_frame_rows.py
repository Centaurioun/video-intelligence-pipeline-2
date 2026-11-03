"""Contracts for canonical FFprobe frame/packet row extraction.

FFprobe 9.x merges ``-show_frames`` and ``-show_packets`` output into a single
``packets_and_frames`` array instead of the separate ``frames``/``packets``
arrays earlier versions emit.  Readers must not each grow a second copy of that
layout knowledge, so this module pins the one shape adapter they all consume.

These tests are generated/synthetic only; the real-tool test is guarded and uses
a locally generated two-second clip.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from vip_fvs.ffprobe_frame_rows import (
    FfprobePayloadShapeError,
    normalized_frame_rows,
    normalized_packet_rows,
)
from vip_fvs.real_preview_verifier import _evidence_facts
from vip_fvs.real_source_probe import RealSourceProbeBinding
from vip_fvs.real_source_service import (
    RealSourcePreparationRefusal,
    _frame_presentation_pts,
    _observed_pts,
)

FFMPEG = Path("/opt/homebrew/bin/ffmpeg")
FFPROBE = Path("/opt/homebrew/bin/ffprobe")


def _frame(tick: int, stream: int = 0, alias: str = "best_effort_timestamp") -> dict:
    return {"stream_index": stream, alias: tick}


def _merged(frames: list[dict], packets: list[dict], order: str = "interleaved") -> list[dict]:
    frame_rows = [{**row, "type": "frame"} for row in frames]
    packet_rows = [{**row, "type": "packet"} for row in packets]
    if order == "frames_first":
        return frame_rows + packet_rows
    rows: list[dict] = []
    for index in range(max(len(frame_rows), len(packet_rows))):
        if index < len(packet_rows):
            rows.append(packet_rows[index])
        if index < len(frame_rows):
            rows.append(frame_rows[index])
    return rows


def _probe(tmp_path: Path, payload: object) -> RealSourceProbeBinding:
    digest = hashlib.sha256(b"generated fixture bytes").hexdigest()
    return RealSourceProbeBinding(
        source_path=tmp_path / "generated.mp4",
        source_revision_id="rev-generated-1",
        source_sha256=digest,
        source_byte_count=24,
        selected_stream_index=0,
        timebase_num=1,
        timebase_den=1000,
        ffprobe_json=payload,  # type: ignore[arg-type]
        probe_digest="a" * 64,
        probe_artifact_ref=str(tmp_path / "run" / "probe.json"),
        raw_probe_artifact_ref=str(tmp_path / "run" / "probe-raw.json"),
        canonical_probe_artifact_ref=str(tmp_path / "run" / "probe-canonical.json"),
        policy_identity="policy-ffprobe-shape-test",
    )


# --- adapter: legacy layout -------------------------------------------------


def test_legacy_layout_is_returned_in_payload_order():
    frames = [_frame(40), _frame(80)]
    packets = [{"stream_index": 0, "pts": 120}, {"stream_index": 1, "pts": 999}]
    payload = {"frames": frames, "packets": packets}

    assert normalized_frame_rows(payload) == tuple(frames)
    assert normalized_packet_rows(payload) == tuple(packets)


def test_absent_row_layouts_are_empty_not_an_error():
    payload = {"streams": [{"index": 0}], "format": {"duration": "2.0"}}

    assert normalized_frame_rows(payload) == ()
    assert normalized_packet_rows(payload) == ()


# --- adapter: ffprobe 9.x merged layout ------------------------------------


def test_merged_layout_splits_rows_and_preserves_interleaved_order():
    frames = [_frame(0), _frame(1000), _frame(2000)]
    packets = [{"stream_index": 0, "pts": 0}, {"stream_index": 0, "pts": 1000},
               {"stream_index": 0, "pts": 2000}]
    payload = {"packets_and_frames": _merged(frames, packets)}

    assert normalized_frame_rows(payload) == tuple(
        {**row, "type": "frame"} for row in frames)
    assert normalized_packet_rows(payload) == tuple(
        {**row, "type": "packet"} for row in packets)


def test_merged_layout_with_sixty_frames_and_packets_is_fully_visible():
    frames = [_frame(1000 * index + 7) for index in range(60)]
    packets = [{"stream_index": 0, "pts": 1000 * index} for index in range(60)]
    payload = {"packets_and_frames": _merged(frames, packets)}

    assert len(normalized_frame_rows(payload)) == 60
    assert len(normalized_packet_rows(payload)) == 60


def test_merged_frame_multiplicity_is_preserved():
    frames = [_frame(0), _frame(0), _frame(1000)]
    payload = {"packets_and_frames": _merged(frames, [])}

    assert normalized_frame_rows(payload) == tuple(
        {**row, "type": "frame"} for row in frames)


# --- adapter: agreement and refusals ---------------------------------------


def test_legacy_and_merged_layouts_that_agree_are_accepted():
    frames = [_frame(40), _frame(80)]
    packets = [{"stream_index": 0, "pts": 120}]
    payload = {"frames": frames, "packets": packets,
               "packets_and_frames": _merged(frames, packets)}

    assert normalized_frame_rows(payload) == tuple(
        {**row, "type": "frame"} for row in frames)
    assert normalized_packet_rows(payload) == tuple(
        {**row, "type": "packet"} for row in packets)


@pytest.mark.parametrize(
    "legacy, merged_frames",
    [
        ([_frame(40), _frame(80)], [_frame(40), _frame(81)]),
        ([_frame(40)], [_frame(40), _frame(80)]),
        ([_frame(40, stream=0)], [_frame(40, stream=1)]),
    ],
)
def test_conflicting_legacy_and_merged_frame_layouts_are_refused(legacy, merged_frames):
    payload = {"frames": legacy, "packets": [],
               "packets_and_frames": _merged(merged_frames, [])}

    with pytest.raises(FfprobePayloadShapeError):
        normalized_frame_rows(payload)


def test_conflicting_legacy_and_merged_packet_layouts_are_refused():
    payload = {"packets": [{"stream_index": 0, "pts": 120}], "frames": [],
               "packets_and_frames": _merged([], [{"stream_index": 0, "pts": 121}])}

    with pytest.raises(FfprobePayloadShapeError):
        normalized_packet_rows(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"frames": {"stream_index": 0}},
        {"frames": ["not-an-object"]},
        {"packets_and_frames": {"type": "frame"}},
        {"packets_and_frames": ["not-an-object"]},
        {"packets_and_frames": [{"stream_index": 0, "best_effort_timestamp": 0}]},
        {"packets_and_frames": [{"type": "subtitle", "stream_index": 0}]},
        {"packets_and_frames": [{"type": None, "stream_index": 0}]},
        [],
    ],
)
def test_malformed_frame_layouts_are_refused(payload):
    with pytest.raises(FfprobePayloadShapeError):
        normalized_frame_rows(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"packets": "not-a-list"},
        {"packets": ["not-an-object"]},
        {"packets_and_frames": {"type": "packet"}},
        {"packets_and_frames": ["not-an-object"]},
        {"packets_and_frames": [{"type": "subtitle", "stream_index": 0}]},
        {"packets_and_frames": [{"type": None, "stream_index": 0}]},
        [],
    ],
)
def test_malformed_packet_layouts_are_refused(payload):
    with pytest.raises(FfprobePayloadShapeError):
        normalized_packet_rows(payload)


# --- service endpoint reader ----------------------------------------------


def test_frame_presentation_pts_reads_ffprobe9_merged_evidence(tmp_path):
    frames = [_frame(0), _frame(1000), _frame(2000), _frame(2000)]
    packets = [{"stream_index": 0, "pts": 0}, {"stream_index": 0, "pts": 1000}]
    probe = _probe(tmp_path, {"packets_and_frames": _merged(frames, packets)})

    # Order and duplicate multiplicity are presentation evidence; packets never
    # contribute to the endpoint authority and are not consulted here.
    assert _frame_presentation_pts(probe) == (0, 1000, 2000, 2000)


def test_frame_presentation_pts_still_ignores_other_streams_in_merged_layout(tmp_path):
    frames = [_frame(0, stream=0), _frame(999, stream=1), _frame(1000, stream=0)]
    probe = _probe(tmp_path, {"packets_and_frames": _merged(frames, [])})

    assert _frame_presentation_pts(probe) == (0, 1000)


def test_frame_presentation_pts_refuses_malformed_merged_evidence(tmp_path):
    probe = _probe(tmp_path, {"packets_and_frames": [{"stream_index": 0}]})

    with pytest.raises(RealSourcePreparationRefusal,
                       match="SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED"):
        _frame_presentation_pts(probe)


def test_frame_presentation_pts_refuses_conflicting_layouts(tmp_path):
    probe = _probe(tmp_path, {
        "frames": [_frame(0), _frame(1000)],
        "packets_and_frames": _merged([_frame(0), _frame(1001)], []),
    })

    with pytest.raises(RealSourcePreparationRefusal,
                       match="SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED"):
        _frame_presentation_pts(probe)


def test_observed_pts_inventory_accepts_ffprobe9_merged_layout(tmp_path):
    frames = [_frame(40), _frame(80, stream=1)]
    packets = [{"stream_index": 0, "pts": 120}]
    probe = _probe(tmp_path, {"packets_and_frames": _merged(frames, packets)})

    assert _observed_pts(probe) == (40, 120)


# --- verifier evidence reader ---------------------------------------------


def _evidence_file(tmp_path: Path, payload: object) -> tuple[Path, str]:
    path = tmp_path / "probe.json"
    path.write_bytes(json.dumps(payload).encode("utf-8"))
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_verifier_evidence_reads_ffprobe9_merged_layout(tmp_path):
    frames = [_frame(0), _frame(1000)]
    packets = [{"stream_index": 0, "pts": 500}]
    path, digest = _evidence_file(
        tmp_path, {"packets_and_frames": _merged(frames, packets)})

    payload, pts = _evidence_facts(path, digest, selected_stream=0)

    assert payload["packets_and_frames"]
    assert pts == (0, 500, 1000)


def test_verifier_evidence_refuses_malformed_merged_layout(tmp_path):
    path, digest = _evidence_file(
        tmp_path, {"packets_and_frames": [{"type": "frame", "stream_index": 0}]})

    # A malformed row is still unreadable evidence: the verifier keeps its
    # existing fail-closed evidence refusal code rather than growing a new one.
    with pytest.raises(ValueError, match="SOURCE_PTS_EVIDENCE_INVALID"):
        _evidence_facts(path, digest, selected_stream=0)


# --- real ffprobe 9.x measurement -----------------------------------------


@pytest.mark.skipif(not (FFPROBE.is_file() and FFMPEG.is_file()),
                    reason="real ffmpeg/ffprobe binaries not available")
def test_real_ffprobe_merged_payload_exposes_all_presentation_rows(tmp_path):
    source = tmp_path / "generated-cfr.mp4"
    subprocess.run(
        [str(FFMPEG), "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x120:rate=30:duration=2",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(source)],
        check=True, capture_output=True,
    )
    completed = subprocess.run(
        [str(FFPROBE), "-v", "error", "-of", "json", "-show_streams",
         "-show_format", "-show_frames", "-show_packets", str(source)],
        check=True, capture_output=True,
    )
    payload = json.loads(completed.stdout)
    if "packets_and_frames" not in payload:
        pytest.skip("installed ffprobe still emits the legacy frames/packets layout")

    assert "frames" not in payload and "packets" not in payload
    rows = payload["packets_and_frames"]
    assert {row["type"] for row in rows} == {"frame", "packet"}
    frame_rows = normalized_frame_rows(payload)
    assert len(frame_rows) == 60
    assert len(normalized_packet_rows(payload)) == 60

    service_rows = _frame_presentation_pts(_probe(tmp_path, payload))
    assert len(service_rows) == 60
    assert service_rows == tuple(row["best_effort_timestamp"] for row in frame_rows)
