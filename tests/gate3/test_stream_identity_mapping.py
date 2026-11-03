"""S2 W-FACT predicates: structural tkhd identity against probe stream IDs."""
from __future__ import annotations

import hashlib
import inspect
import re
import struct
from collections.abc import Mapping

import pytest


def _api():
    from gate3 import fixturegen
    from gate3.stream_identity import (
        POSITIONAL_IDENTITY_DERIVATION,
        REASON_BOUND_EVIDENCE_UNAVAILABLE,
        REASON_COUNT_MISMATCH,
        REASON_NO_TKHD,
        REASON_POSITIONAL_MISMATCH,
        REASON_PROBE_ID_UNUSABLE,
        REASON_SELECTED_NOT_VIDEO,
        REASON_SELECTION_AMBIGUOUS,
        REASON_TKHD_HEADER_UNSUPPORTED,
        REASON_TRACK_ID_DUPLICATE,
        REASON_TRACK_ID_UNUSABLE,
        StreamIdentityEvidence,
        StreamIdentityUnproven,
        evaluate_stream_identity,
        require_stream_identity,
    )
    return locals()


def _rows(ids, handlers):
    return [
        {"index": i, "codec_type": handler, "id": stream_id}
        for i, (stream_id, handler) in enumerate(zip(ids, handlers))
    ]


def _args(raw, rows, selected=0):
    return {
        "container_bytes": raw,
        "container_sha256": hashlib.sha256(raw).hexdigest(),
        "probe_streams": rows,
        "probe_digest": "a" * 64,
        "probe_provenance": "synthetic-probe.json",
        "selected_stream_index": selected,
    }


def _one_video():
    api = _api()
    raw = api["fixturegen"].build_mp4(media_timescale=1000, sample_deltas=(40, 40))
    return api, raw, _args(raw, _rows(["0x1"], ["video"]))


def _two_tracks(first_id=1, second_id=2, first_handler=b"soun", second_handler=b"vide"):
    api = _api()
    raw = api["fixturegen"].build_multi_trak_mp4(media_timescale=1000, traks=[
        {"media_timescale": 1000, "sample_deltas": (40,), "track_id": first_id, "handler": first_handler},
        {"media_timescale": 48000, "sample_deltas": (1024,), "track_id": second_id, "handler": second_handler},
    ])
    rows = [f"0x{first_id:x}", f"0x{second_id:x}"]
    kinds = ["audio" if first_handler == b"soun" else "video",
             "audio" if second_handler == b"soun" else "video"]
    return api, raw, rows, kinds


def _refused(api, kwargs, reason):
    evidence = api["evaluate_stream_identity"](**kwargs)
    assert evidence.state == "REFUSED"
    assert evidence.reason == reason
    with pytest.raises(api["StreamIdentityUnproven"]) as exc:
        api["require_stream_identity"](**kwargs)
    assert exc.value.reason == reason
    assert exc.value.evidence == evidence
    return evidence


def _proven(api, kwargs):
    evidence = api["evaluate_stream_identity"](**kwargs)
    assert evidence.state == "PROVEN"
    assert evidence.reason is None
    assert evidence.derivation == api["POSITIONAL_IDENTITY_DERIVATION"]
    assert evidence.probe_source_binding == "PRODUCER_SEALED"
    assert evidence.demuxer_build_state == "NOT_OBSERVED"
    assert api["require_stream_identity"](**kwargs) == evidence
    return evidence


def test_r01_single_video_track_proves_identity():
    api, _raw, kwargs = _one_video()
    evidence = _proven(api, kwargs)
    assert evidence.selected_position == 0
    assert evidence.track_ids == (1,)
    assert evidence.probe_ids == (1,)


def test_r02_audio_first_video_second_proves_selected_video():
    api, raw, ids, kinds = _two_tracks()
    evidence = _proven(api, _args(raw, _rows(ids, kinds), selected=1))
    assert evidence.selected_position == 1


def test_r03_reversed_track_ids_are_compared_positionally():
    api, raw, ids, kinds = _two_tracks(2, 1, b"vide", b"soun")
    evidence = _proven(api, _args(raw, _rows(ids, kinds), selected=0))
    assert evidence.track_ids == (2, 1)


def test_r04_multiple_video_tracks_require_and_accept_explicit_selection():
    api = _api()
    raw = api["fixturegen"].build_multi_trak_mp4(media_timescale=1000, traks=[
        {"media_timescale": 1000, "sample_deltas": (40,), "track_id": 1, "handler": b"vide"},
        {"media_timescale": 1000, "sample_deltas": (50,), "track_id": 2, "handler": b"vide"},
    ])
    for selected in (0, 1):
        evidence = _proven(api, _args(raw, _rows(["0x1", "0x2"], ["video", "video"]), selected))
        assert evidence.selected_position == selected


def test_r05_changed_container_bytes_refuse_digest_binding():
    api, raw, kwargs = _one_video()
    changed = bytearray(raw)
    changed[-1] ^= 1
    kwargs["container_bytes"] = bytes(changed)
    _refused(api, kwargs, api["REASON_BOUND_EVIDENCE_UNAVAILABLE"])


@pytest.mark.parametrize("changes", [
    {"probe_digest": None}, {"probe_digest": "a" * 63},
    {"probe_digest": "A" * 64}, {"probe_provenance": ""},
])
def test_r06_missing_or_malformed_probe_evidence_refuses(changes):
    api, _raw, kwargs = _one_video()
    kwargs.update(changes)
    _refused(api, kwargs, api["REASON_BOUND_EVIDENCE_UNAVAILABLE"])


def test_r07_trak_without_tkhd_refuses():
    api = _api()
    raw = api["fixturegen"].build_no_tkhd_mp4()
    kwargs = _args(raw, _rows(["0x1"], ["video"]))
    _refused(api, kwargs, api["REASON_NO_TKHD"])


def test_r08_short_tkhd_refuses():
    api = _api()
    raw = api["fixturegen"].build_short_tkhd_mp4()
    _refused(api, _args(raw, _rows(["0x1"], ["video"])), api["REASON_TKHD_HEADER_UNSUPPORTED"])


def test_r09_zero_size_tkhd_refuses_even_though_reader_expands_it():
    api = _api()
    raw = api["fixturegen"].build_zero_size_tkhd_mp4()
    _refused(api, _args(raw, _rows(["0x1"], ["video"])), api["REASON_TKHD_HEADER_UNSUPPORTED"])


def test_r10_large_size_tkhd_refuses():
    api = _api()
    raw = api["fixturegen"].build_large_size_tkhd_mp4()
    _refused(api, _args(raw, _rows(["0x1"], ["video"])), api["REASON_TKHD_HEADER_UNSUPPORTED"])


def test_r11_unsupported_tkhd_version_refuses():
    api = _api()
    raw = api["fixturegen"].build_tkhd_version_2_mp4()
    _refused(api, _args(raw, _rows(["0x1"], ["video"])), api["REASON_TKHD_HEADER_UNSUPPORTED"])


def test_supported_v1_tkhd_uses_its_versioned_track_id_offset():
    api = _api()
    from gate3.fixturegen import _replace_tkhd, build_mp4
    raw = build_mp4(media_timescale=1000, sample_deltas=(40,))
    payload = b"\x01\x00\x00\x03" + struct.pack(">QQIIQ", 0, 0, 7, 0, 40) + b"\0" * 60
    v1_tkhd = struct.pack(">I4s", 104, b"tkhd") + payload
    raw = _replace_tkhd(raw, v1_tkhd)
    evidence = _proven(api, _args(raw, _rows(["0x7"], ["video"])))
    assert evidence.track_ids == (7,)


@pytest.mark.parametrize("track_id", [0, 0xFFFFFFFF])
def test_r12_zero_or_reserved_track_id_refuses(track_id):
    api = _api()
    raw = api["fixturegen"].build_multi_trak_mp4(media_timescale=1000, traks=[
        {"media_timescale": 1000, "sample_deltas": (40,), "track_id": track_id, "handler": b"vide"},
    ])
    _refused(api, _args(raw, _rows([f"0x{track_id:x}"], ["video"])), api["REASON_TRACK_ID_UNUSABLE"])


def test_r13_duplicate_track_ids_refuse():
    api = _api()
    raw = api["fixturegen"].build_duplicate_track_id_mp4()
    _refused(api, _args(raw, _rows(["0x1", "0x1"], ["video", "audio"])), api["REASON_TRACK_ID_DUPLICATE"])


@pytest.mark.parametrize("count", [1, 3])
def test_r14_probe_stream_count_mismatch_refuses(count):
    api, raw, _ids, _kinds = _two_tracks()
    rows = ["0x1", "0x2", "0x3"][:count]
    kinds = ["video"] * count
    _refused(api, _args(raw, _rows(rows, kinds)), api["REASON_COUNT_MISMATCH"])


@pytest.mark.parametrize("row_change", [
    {"remove_id": True}, {"id": "1"}, {"id": "0x0"}, {"id": "0x01"},
    {"id": "0xFFFFFFFF"}, {"index": 4}, {"remove_index": True},
    {"remove_codec_type": True},
])
def test_r15_missing_noncanonical_or_inconsistent_probe_identity_refuses(row_change):
    api, raw, ids, kinds = _two_tracks()
    kwargs = _args(raw, _rows(ids, kinds), selected=1)
    changes = dict(row_change)
    if changes.pop("remove_id", False):
        del kwargs["probe_streams"][0]["id"]
    if changes.pop("remove_index", False):
        del kwargs["probe_streams"][0]["index"]
    if changes.pop("remove_codec_type", False):
        del kwargs["probe_streams"][0]["codec_type"]
    kwargs["probe_streams"][0].update(changes)
    _refused(api, kwargs, api["REASON_PROBE_ID_UNUSABLE"])


def test_r16_swapped_probe_positions_refuse():
    api, raw, _ids, kinds = _two_tracks()
    _refused(api, _args(raw, _rows(["0x2", "0x1"], kinds), selected=1), api["REASON_POSITIONAL_MISMATCH"])


def test_r17_audio_selected_as_video_refuses():
    api, raw, ids, kinds = _two_tracks()
    _refused(api, _args(raw, _rows(ids, kinds), selected=0), api["REASON_SELECTED_NOT_VIDEO"])


@pytest.mark.parametrize("selected", [-1, 2, True, 1.0, "1", None])
def test_r18_invalid_or_ambiguous_selector_refuses(selected):
    api, raw, ids, kinds = _two_tracks()
    evidence = _refused(api, _args(raw, _rows(ids, kinds), selected=selected), api["REASON_SELECTION_AMBIGUOUS"])
    assert evidence.selected_position is None


def test_r19_probe_video_label_cannot_override_audio_handler():
    api, raw, ids, _kinds = _two_tracks()
    _refused(api, _args(raw, _rows(ids, ["video", "video"]), selected=0), api["REASON_SELECTED_NOT_VIDEO"])


def test_refusal_precedence_bound_evidence_before_container_structure():
    api = _api()
    raw = api["fixturegen"].build_no_tkhd_mp4()
    kwargs = _args(raw, _rows(["not-an-id"], ["video"]))
    kwargs["probe_digest"] = "invalid"
    _refused(api, kwargs, api["REASON_BOUND_EVIDENCE_UNAVAILABLE"])


def test_refusal_precedence_missing_tkhd_before_probe_id_and_selection_checks():
    api = _api()
    raw = api["fixturegen"].build_no_tkhd_mp4()
    kwargs = _args(raw, [{"index": 0, "codec_type": "video", "id": "not-an-id"}], selected=True)
    _refused(api, kwargs, api["REASON_NO_TKHD"])


def test_refusal_precedence_unsupported_tkhd_before_probe_id_checks():
    api = _api()
    raw = api["fixturegen"].build_tkhd_version_2_mp4()
    _refused(api, _args(raw, _rows(["not-an-id"], ["video"])), api["REASON_TKHD_HEADER_UNSUPPORTED"])


def test_refusal_precedence_duplicate_track_ids_before_count_mismatch():
    api = _api()
    raw = api["fixturegen"].build_duplicate_track_id_mp4()
    _refused(api, _args(raw, _rows(["0x1"], ["video"])), api["REASON_TRACK_ID_DUPLICATE"])


def test_refusal_precedence_count_mismatch_before_probe_id_parsing():
    api, raw, _ids, _kinds = _two_tracks()
    _refused(api, _args(raw, [{"index": 0, "codec_type": "video", "id": "not-an-id"}]), api["REASON_COUNT_MISMATCH"])


def test_refusal_precedence_probe_id_validation_before_positional_comparison():
    api, raw, _ids, kinds = _two_tracks()
    rows = _rows(["0x9", "0x2"], kinds)
    del rows[1]["id"]
    _refused(api, _args(raw, rows, selected=1), api["REASON_PROBE_ID_UNUSABLE"])


def test_refusal_precedence_positional_mismatch_before_selection_validation():
    api, raw, _ids, kinds = _two_tracks()
    _refused(api, _args(raw, _rows(["0x2", "0x1"], kinds), selected=True), api["REASON_POSITIONAL_MISMATCH"])


def test_r20_valid_track_identity_does_not_require_timing_tables():
    api = _api()
    raw = api["fixturegen"].build_timingless_trak_mp4()
    evidence = _proven(api, _args(raw, _rows(["0x1"], ["video"])))


def test_r21_source_has_no_forbidden_dependencies_or_naive_offsets():
    from pathlib import Path
    source = Path(__file__).parents[2].joinpath("src/gate3/stream_identity.py").read_text()
    assert not re.search(r"subprocess|time\.time|\+20|vip_fvs|open\(|ffprobe|os\.environ", source)
    assert "container._boxes" in source
    assert "container._parse_hdlr" in source
    assert "gate3.container" in source


def test_r22_proven_evidence_preserves_sealed_and_unobserved_labels():
    api, _raw, kwargs = _one_video()
    evidence = _proven(api, kwargs)
    assert isinstance(evidence, api["StreamIdentityEvidence"])
    assert evidence.probe_source_binding == "PRODUCER_SEALED"
    assert evidence.demuxer_build_state == "NOT_OBSERVED"
    assert inspect.signature(api["evaluate_stream_identity"]).parameters.keys() == {
        "container_bytes", "container_sha256", "probe_streams", "probe_digest",
        "probe_provenance", "selected_stream_index",
    }


@pytest.mark.parametrize("buffer_factory", [bytes, bytearray, memoryview])
def test_accepts_bytes_like_without_mutating_input(buffer_factory):
    api, raw, kwargs = _one_video()
    original = bytes(raw)
    kwargs["container_bytes"] = buffer_factory(raw)
    evidence = api["evaluate_stream_identity"](**kwargs)
    assert evidence.state == "PROVEN"
    assert bytes(kwargs["container_bytes"]) == original
