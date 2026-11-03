"""S3 shared stream-identity gate tests using synthetic ISO-BMFF bytes."""
from __future__ import annotations

import hashlib
import inspect
import json

import pytest


def _gate():
    from vip_fvs.stream_identity_gate import require_bound_stream_identity

    return require_bound_stream_identity


def _fixturegen():
    from gate3 import fixturegen

    return fixturegen


def _rows(*streams):
    return [
        {"index": index, "codec_type": codec_type, "id": stream_id}
        for index, (codec_type, stream_id) in enumerate(streams)
    ]


def _two_track_source():
    return _fixturegen().build_multi_trak_mp4(
        media_timescale=1000,
        traks=[
            {"media_timescale": 48000, "sample_deltas": (1024,), "track_id": 1, "handler": b"soun"},
            {"media_timescale": 1000, "sample_deltas": (40,), "track_id": 2, "handler": b"vide"},
        ],
    )


def _three_track_source():
    return _fixturegen().build_multi_trak_mp4(
        media_timescale=1000,
        traks=[
            {"media_timescale": 1000, "sample_deltas": (40,), "track_id": 1, "handler": b"vide"},
            {"media_timescale": 48000, "sample_deltas": (1024,), "track_id": 2, "handler": b"soun"},
            {"media_timescale": 1000, "sample_deltas": (50,), "track_id": 3, "handler": b"vide"},
        ],
    )


def _persist_probe(tmp_path, rows, *, trailing_newline=True, name="probe-canonical.json"):
    payload = {"streams": rows}
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    raw = (serialized + ("\n" if trailing_newline else "")).encode("utf-8")
    path = tmp_path / name
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    return path, digest


def _write_container(tmp_path, raw, name="source.mp4"):
    path = tmp_path / name
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()


def _two_track_files(tmp_path, rows):
    return (
        _write_container(tmp_path, _two_track_source()),
        _persist_probe(tmp_path, rows),
    )


def _invoke(container, probe, *, selected_stream_index):
    container_path, container_sha256 = container
    probe_path, probe_digest = probe if probe is not None else (None, None)
    return _gate()(
        container_path=container_path,
        container_sha256=container_sha256,
        probe_artifact_path=probe_path,
        probe_digest=probe_digest,
        selected_stream_index=selected_stream_index,
    )


def _require_refusal(container, probe):
    from gate3.stream_identity import (
        REASON_BOUND_EVIDENCE_UNAVAILABLE,
        StreamIdentityUnproven,
    )

    with pytest.raises(StreamIdentityUnproven) as exc:
        _invoke(container, probe, selected_stream_index=1)
    assert exc.value.reason == REASON_BOUND_EVIDENCE_UNAVAILABLE
    assert exc.value.evidence.reason == REASON_BOUND_EVIDENCE_UNAVAILABLE
    return exc.value


def test_r_g1_two_track_audio_first_persisted_probe_proves_identity(tmp_path):
    container, probe = _two_track_files(
        tmp_path, _rows(("audio", "0x1"), ("video", "0x2"))
    )

    evidence = _invoke(container, probe, selected_stream_index=1)

    assert evidence.state == "PROVEN"
    assert evidence.probe_source_binding == "PRODUCER_SEALED"
    assert evidence.demuxer_build_state == "NOT_OBSERVED"
    assert evidence.probe_provenance == str(probe[0])


def test_r_g2_artifact_without_producer_trailing_newline_is_refused(tmp_path):
    container, producer = _two_track_files(
        tmp_path, _rows(("audio", "0x1"), ("video", "0x2"))
    )
    no_newline_path, _ = _persist_probe(
        tmp_path,
        _rows(("audio", "0x1"), ("video", "0x2")),
        trailing_newline=False,
        name="probe-without-newline.json",
    )
    assert producer[0] != no_newline_path

    _require_refusal(container, (no_newline_path, producer[1]))


def test_r_g3_one_byte_artifact_tampering_is_refused(tmp_path):
    container, probe = _two_track_files(
        tmp_path, _rows(("audio", "0x1"), ("video", "0x2"))
    )
    probe_path, probe_digest = probe
    artifact = bytearray(probe_path.read_bytes())
    artifact[-2] ^= 1
    probe_path.write_bytes(artifact)

    refusal = _require_refusal(container, probe)
    assert refusal.evidence.state == "REFUSED"
    assert refusal.evidence.probe_digest == probe_digest
    assert refusal.evidence.probe_provenance == str(probe_path)
    assert refusal.evidence.probe_source_binding == ""


def test_r_g4_container_mutated_after_digest_capture_is_refused(tmp_path):
    container = _write_container(tmp_path, _two_track_source())
    raw = container[0].read_bytes()
    changed = bytearray(raw)
    changed[-1] ^= 1
    container[0].write_bytes(changed)
    probe = _persist_probe(
        tmp_path, _rows(("audio", "0x1"), ("video", "0x2"))
    )

    _require_refusal(container, probe)


def test_r_g5_single_track_uses_legacy_success_without_probe_artifact(tmp_path):
    raw = _fixturegen().build_mp4(media_timescale=1000, sample_deltas=(40, 40))
    container = _write_container(tmp_path, raw)

    evidence = _invoke(container, None, selected_stream_index=0)

    assert evidence.state == "PROVEN"
    assert evidence.derivation is None
    assert evidence.track_ids is None
    assert evidence.probe_ids is None
    assert evidence.probe_digest == ""
    assert evidence.probe_provenance == ""
    assert evidence.probe_source_binding == ""
    assert evidence.demuxer_build_state == "NOT_OBSERVED"


def test_single_audio_track_does_not_gain_video_selection_authority(tmp_path):
    from gate3.stream_identity import StreamIdentityUnproven, REASON_SELECTED_NOT_VIDEO

    raw = _fixturegen().build_mp4(
        media_timescale=48000, sample_deltas=(1024,), handler=b"soun"
    )
    container = _write_container(tmp_path, raw)

    with pytest.raises(StreamIdentityUnproven) as exc:
        _invoke(container, None, selected_stream_index=0)

    assert exc.value.reason == REASON_SELECTED_NOT_VIDEO


def test_r_g6_multi_track_without_probe_artifact_is_refused(tmp_path):
    container = _write_container(tmp_path, _two_track_source())

    _require_refusal(container, None)


def test_multi_track_s2_refusal_reason_and_evidence_are_preserved(tmp_path):
    from gate3 import fixturegen
    from gate3.stream_identity import StreamIdentityUnproven, REASON_NO_TKHD

    raw = fixturegen._replace_tkhd(_two_track_source(), b"")
    container = _write_container(tmp_path, raw)
    probe = _persist_probe(
        tmp_path, _rows(("audio", "0x1"), ("video", "0x2"))
    )

    with pytest.raises(StreamIdentityUnproven) as exc:
        _invoke(container, probe, selected_stream_index=1)

    assert exc.value.reason == REASON_NO_TKHD
    assert exc.value.evidence.reason == REASON_NO_TKHD


def test_r_g7_three_track_video_audio_video_proves_selected_video(tmp_path):
    raw = _three_track_source()
    container = _write_container(tmp_path, raw)
    probe = _persist_probe(
        tmp_path,
        _rows(("video", "0x1"), ("audio", "0x2"), ("video", "0x3")),
    )

    evidence = _invoke(container, probe, selected_stream_index=2)

    assert evidence.state == "PROVEN"
    assert evidence.selected_position == 2
    assert evidence.probe_source_binding == "PRODUCER_SEALED"
    assert evidence.demuxer_build_state == "NOT_OBSERVED"


def test_r_g8_public_signature_has_no_caller_supplied_stream_count():
    signature = inspect.signature(_gate())
    parameters = signature.parameters

    assert tuple(parameters) == (
        "container_path",
        "container_sha256",
        "probe_artifact_path",
        "probe_digest",
        "selected_stream_index",
    )
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters.values())
    assert all(parameter.default is inspect.Parameter.empty for parameter in parameters.values())


def test_unreadable_container_fails_closed(tmp_path):
    from gate3.stream_identity import (
        REASON_BOUND_EVIDENCE_UNAVAILABLE,
        StreamIdentityUnproven,
    )

    with pytest.raises(StreamIdentityUnproven) as exc:
        _invoke((tmp_path / "missing.mp4", "a" * 64), None, selected_stream_index=0)
    assert exc.value.reason == REASON_BOUND_EVIDENCE_UNAVAILABLE
    assert exc.value.evidence.reason == REASON_BOUND_EVIDENCE_UNAVAILABLE


def test_malformed_container_boxes_fail_with_typed_refusal(tmp_path):
    from gate3.stream_identity import (
        REASON_BOUND_EVIDENCE_UNAVAILABLE,
        StreamIdentityUnproven,
    )

    container = _write_container(tmp_path, b"\x00\x00\x00@moov\x00\x00\x00\x00")

    with pytest.raises(StreamIdentityUnproven) as exc:
        _invoke(container, None, selected_stream_index=0)

    assert exc.value.reason == REASON_BOUND_EVIDENCE_UNAVAILABLE
    assert exc.value.evidence.reason == REASON_BOUND_EVIDENCE_UNAVAILABLE


def test_unreadable_probe_does_not_claim_producer_sealed_binding(tmp_path):
    from gate3.stream_identity import StreamIdentityUnproven

    container = _write_container(tmp_path, _two_track_source())
    probe_path = tmp_path / "missing-probe.json"

    with pytest.raises(StreamIdentityUnproven) as exc:
        _invoke(container, (probe_path, "a" * 64), selected_stream_index=1)

    assert exc.value.evidence.probe_provenance == str(probe_path)
    assert exc.value.evidence.probe_source_binding == ""


def test_digest_mismatch_does_not_claim_producer_sealed_binding(tmp_path):
    from gate3.stream_identity import StreamIdentityUnproven

    container = _write_container(tmp_path, _two_track_source())
    probe = _persist_probe(
        tmp_path, _rows(("audio", "0x1"), ("video", "0x2"))
    )
    probe_path, probe_digest = probe
    tampered = bytearray(probe_path.read_bytes())
    tampered[-2] ^= 1
    probe_path.write_bytes(tampered)

    with pytest.raises(StreamIdentityUnproven) as exc:
        _invoke(container, probe, selected_stream_index=1)

    assert exc.value.evidence.probe_source_binding == ""


def test_malformed_multi_track_probe_json_fails_closed(tmp_path):
    from gate3.stream_identity import StreamIdentityUnproven

    container = _write_container(tmp_path, _two_track_source())
    probe_path = tmp_path / "probe-canonical.json"
    probe_path.write_bytes(b"{not-json\n")

    with pytest.raises(StreamIdentityUnproven) as exc:
        _invoke(
            container,
            (probe_path, hashlib.sha256(probe_path.read_bytes()).hexdigest()),
            selected_stream_index=1,
        )
    assert exc.value.evidence.probe_source_binding == ""
