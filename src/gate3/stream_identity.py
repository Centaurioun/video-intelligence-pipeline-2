"""Pure structural ISO-BMFF track and probe-stream identity predicate."""
from __future__ import annotations

import hashlib
import re
import struct
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import gate3.container as container


POSITIONAL_IDENTITY_DERIVATION = "positional_tkhd_track_id_equals_probe_stream_id"

REASON_BOUND_EVIDENCE_UNAVAILABLE = "BOUND-EVIDENCE-UNAVAILABLE"
REASON_NO_TKHD = "NO-TKHD"
REASON_TKHD_HEADER_UNSUPPORTED = "TKHD-HEADER-UNSUPPORTED"
REASON_TRACK_ID_UNUSABLE = "TRACK-ID-UNUSABLE"
REASON_TRACK_ID_DUPLICATE = "TRACK-ID-DUPLICATE"
REASON_COUNT_MISMATCH = "COUNT-MISMATCH"
REASON_PROBE_ID_UNUSABLE = "PROBE-ID-UNUSABLE"
REASON_POSITIONAL_MISMATCH = "POSITIONAL-MISMATCH"
REASON_SELECTED_NOT_VIDEO = "SELECTED-NOT-VIDEO"
REASON_SELECTION_AMBIGUOUS = "SELECTION-AMBIGUOUS"

_PROBE_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_PROBE_ID = re.compile(r"0x[0-9a-f]+\Z")
_TRACK_ID_LIMIT = 0xFFFFFFFF
_TKHD_TRACK_ID_OFFSETS = {0: 12, 1: 20}
_TKHD_MIN_SIZES = {0: 92, 1: 104}


@dataclass(frozen=True)
class StreamIdentityEvidence:
    state: str
    reason: str | None
    derivation: str | None
    selected_position: int | None
    track_ids: tuple[int, ...] | None
    probe_ids: tuple[int, ...] | None
    container_sha256: str
    probe_digest: str
    probe_provenance: str
    probe_source_binding: str
    demuxer_build_state: str


class StreamIdentityUnproven(ValueError):
    """Raised when the available structural evidence cannot prove identity."""

    def __init__(self, reason: str, evidence: StreamIdentityEvidence):
        super().__init__(reason)
        self.reason = reason
        self.evidence = evidence


@dataclass(frozen=True)
class _IdentityContext:
    container_sha256: str
    probe_digest: str
    probe_provenance: str


@dataclass(frozen=True)
class _IdentityObservation:
    selected_position: int | None = None
    track_ids: tuple[int, ...] | None = None
    probe_ids: tuple[int, ...] | None = None


@dataclass(frozen=True)
class _SelectionInputs:
    container_bytes: object
    traks: Sequence
    probe_streams: Sequence
    selected_stream_index: object


def _record(context: _IdentityContext, state: str, reason: str | None,
            observation: _IdentityObservation) -> StreamIdentityEvidence:
    return StreamIdentityEvidence(
        state=state,
        reason=reason,
        derivation=POSITIONAL_IDENTITY_DERIVATION if state == "PROVEN" else None,
        selected_position=observation.selected_position,
        track_ids=observation.track_ids,
        probe_ids=observation.probe_ids,
        container_sha256=context.container_sha256,
        probe_digest=context.probe_digest,
        probe_provenance=context.probe_provenance,
        probe_source_binding="PRODUCER_SEALED",
        demuxer_build_state="NOT_OBSERVED",
    )


def _refuse(context: _IdentityContext, reason: str,
            observation: _IdentityObservation | None = None) -> StreamIdentityEvidence:
    return _record(context, "REFUSED", reason, observation or _IdentityObservation())


def _probe_evidence_is_usable(probe_streams, probe_digest, probe_provenance) -> bool:
    if not _probe_digest_is_usable(probe_digest):
        return False
    if not _probe_stream_rows_are_usable(probe_streams):
        return False
    return _probe_provenance_is_usable(probe_provenance)


def _probe_digest_is_usable(probe_digest):
    return (
        isinstance(probe_digest, str)
        and _PROBE_DIGEST.fullmatch(probe_digest) is not None
    )


def _probe_stream_rows_are_usable(probe_streams):
    return (
        isinstance(probe_streams, Sequence)
        and not isinstance(probe_streams, (str, bytes, bytearray, memoryview))
        and bool(probe_streams)
        and all(isinstance(row, Mapping) for row in probe_streams)
    )


def _probe_provenance_is_usable(probe_provenance):
    return isinstance(probe_provenance, str) and bool(probe_provenance)


def _enumerate_tracks_and_tkhds(raw):
    try:
        moov = _single_moov_box(raw)
        if moov is None:
            return None, None
        traks = _track_children(raw, moov)
        if not traks:
            return None, None
        tkhd_by_trak = _single_tkhd_per_track(raw, traks)
        if tkhd_by_trak is None:
            return None, None
        return traks, tkhd_by_trak
    except (LookupError, ValueError, IndexError, struct.error, TypeError, BufferError):
        return None, None


def _single_moov_box(raw):
    moovs = [box for box in container._boxes(raw) if box[0] == b"moov"]
    if len(moovs) != 1:
        return None
    return moovs[0]


def _single_tkhd_per_track(raw, traks):
    tkhd_by_trak = []
    for trak in traks:
        tkhds = [box for box in container._boxes(raw, trak[1], trak[2])
                 if box[0] == b"tkhd"]
        if len(tkhds) != 1:
            return None
        tkhd_by_trak.append(tkhds[0])
    return tkhd_by_trak


def _read_track_ids(raw, tkhd_by_trak):
    try:
        return tuple(_read_track_header(raw, box) for box in tkhd_by_trak)
    except (IndexError, struct.error, ValueError, TypeError, BufferError):
        return None


def _track_id_refusal(track_ids):
    if not _track_ids_are_usable(track_ids):
        return REASON_TRACK_ID_UNUSABLE
    if len(set(track_ids)) != len(track_ids):
        return REASON_TRACK_ID_DUPLICATE
    return None


def _track_ids_are_usable(track_ids):
    return all(0 < track_id < _TRACK_ID_LIMIT for track_id in track_ids)


def _parse_probe_ids(probe_streams):
    probe_ids = []
    for position, row in enumerate(probe_streams):
        stream_id = row.get("id")
        if not _probe_row_has_canonical_identity(row, position, stream_id):
            return None
        parsed_id = _parse_canonical_probe_id(stream_id)
        if parsed_id is None:
            return None
        probe_ids.append(parsed_id)
    return tuple(probe_ids)


def _probe_row_has_canonical_identity(row, position, stream_id):
    return (
        "index" in row
        and "codec_type" in row
        and "id" in row
        and type(row["index"]) is int
        and row["index"] == position
        and isinstance(stream_id, str)
        and _PROBE_ID.fullmatch(stream_id) is not None
    )


def _parse_canonical_probe_id(stream_id):
    parsed_id = int(stream_id[2:], 16)
    if parsed_id <= 0 or parsed_id >= _TRACK_ID_LIMIT:
        return None
    if stream_id != f"0x{parsed_id:x}":
        return None
    return parsed_id


def _selected_stream_refusal(raw, traks, probe_streams, selected_stream_index):
    if type(selected_stream_index) is not int or not 0 <= selected_stream_index < len(traks):
        return REASON_SELECTION_AMBIGUOUS
    try:
        handler = _track_handler(raw, traks[selected_stream_index])
    except (IndexError, struct.error, TypeError, ValueError, BufferError):
        handler = None
    row = probe_streams[selected_stream_index]
    if not _selected_probe_and_container_are_video(handler, row, selected_stream_index):
        return REASON_SELECTED_NOT_VIDEO
    return None


def _selected_probe_and_container_are_video(handler, row, selected_stream_index):
    return (
        handler == b"vide"
        and row["codec_type"] == "video"
        and row["index"] == selected_stream_index
    )


def _track_children(raw, moov_box):
    moov_payload, moov_end = moov_box[1], moov_box[2]
    return [box for box in container._boxes(raw, moov_payload, moov_end)
            if box[0] == b"trak"]


def _read_track_header(raw, tkhd_box):
    _kind, payload_start, box_end, box_start = tkhd_box
    raw_size = struct.unpack_from(">I", raw, box_start)[0]
    box_size = box_end - box_start
    if raw_size in (0, 1):
        raise ValueError("unsupported tkhd size form")
    if raw_size != box_size or payload_start > box_end:
        raise ValueError("tkhd size does not match its bounds")
    track_id_at = _track_id_field_offset(raw, payload_start, box_end, box_size)
    if track_id_at + 4 > box_end:
        raise ValueError("tkhd track_ID field is outside its box")
    return struct.unpack_from(">I", raw, track_id_at)[0]


def _track_id_field_offset(raw, payload_start, box_end, box_size):
    if payload_start + 4 > box_end:
        raise ValueError("tkhd full-box header is truncated")
    version = raw[payload_start]
    if version not in _TKHD_TRACK_ID_OFFSETS:
        raise ValueError("unsupported tkhd version")
    if box_size < _TKHD_MIN_SIZES[version]:
        raise ValueError("tkhd is shorter than the supported header")
    return payload_start + _TKHD_TRACK_ID_OFFSETS[version]


def _track_handler(raw, trak_box):
    trak_payload, trak_end = trak_box[1], trak_box[2]
    mdias = [box for box in container._boxes(raw, trak_payload, trak_end)
             if box[0] == b"mdia"]
    if len(mdias) != 1:
        return None
    _kind, mdia_payload, mdia_end, _mdia_start = mdias[0]
    handlers = [box for box in container._boxes(raw, mdia_payload, mdia_end)
                if box[0] == b"hdlr"]
    if len(handlers) != 1:
        return None
    try:
        return container._parse_hdlr(raw, handlers[0][1])
    except (IndexError, struct.error, ValueError):
        return None


def evaluate_stream_identity(*, container_bytes, container_sha256, probe_streams,
                             probe_digest, probe_provenance,
                             selected_stream_index) -> StreamIdentityEvidence:
    """Evaluate the approved ordered, structural identity predicate."""
    context = _IdentityContext(
        container_sha256 if isinstance(container_sha256, str) else "",
        probe_digest if isinstance(probe_digest, str) else "",
        probe_provenance if isinstance(probe_provenance, str) else "",
    )
    try:
        actual_container_sha256 = hashlib.sha256(container_bytes).hexdigest()
    except (TypeError, ValueError, BufferError):
        return _refuse(context, REASON_BOUND_EVIDENCE_UNAVAILABLE)
    if container_sha256 != actual_container_sha256:
        return _refuse(context, REASON_BOUND_EVIDENCE_UNAVAILABLE)

    if not _probe_evidence_is_usable(probe_streams, probe_digest, probe_provenance):
        return _refuse(context, REASON_BOUND_EVIDENCE_UNAVAILABLE)

    return _evaluate_bound_identity(
        context, container_bytes, probe_streams, selected_stream_index,
    )


def _evaluate_bound_identity(context, container_bytes, probe_streams,
                             selected_stream_index):
    # Keep the fail-closed order explicit: structure before IDs, count, and selection.
    traks, tkhd_by_trak = _enumerate_tracks_and_tkhds(container_bytes)
    if traks is None:
        return _refuse(context, REASON_NO_TKHD)

    track_ids = _read_track_ids(container_bytes, tkhd_by_trak)
    if track_ids is None:
        return _refuse(context, REASON_TKHD_HEADER_UNSUPPORTED)
    observation = _IdentityObservation(track_ids=track_ids)

    reason = _track_id_refusal(track_ids)
    if reason is not None:
        return _refuse(context, reason, observation)

    if len(probe_streams) != len(traks):
        return _refuse(context, REASON_COUNT_MISMATCH, observation)

    return _evaluate_probe_identity(
        context,
        _SelectionInputs(container_bytes, traks, probe_streams, selected_stream_index),
        observation,
    )


def _evaluate_probe_identity(context, selection, observation):
    probe_ids = _parse_probe_ids(selection.probe_streams)
    if probe_ids is None:
        return _refuse(context, REASON_PROBE_ID_UNUSABLE, observation)
    observation = _IdentityObservation(track_ids=observation.track_ids, probe_ids=probe_ids)

    if any(
        track_id != probe_id
        for track_id, probe_id in zip(observation.track_ids, probe_ids)
    ):
        return _refuse(context, REASON_POSITIONAL_MISMATCH, observation)

    reason = _selected_stream_refusal(
        selection.container_bytes, selection.traks, selection.probe_streams,
        selection.selected_stream_index,
    )
    if reason is not None:
        if reason == REASON_SELECTION_AMBIGUOUS:
            return _refuse(context, reason, observation)
        observation = _IdentityObservation(
            selection.selected_stream_index, observation.track_ids, probe_ids,
        )
        return _refuse(context, reason, observation)
    return _record(
        context, "PROVEN", None,
        _IdentityObservation(
            selection.selected_stream_index, observation.track_ids, probe_ids,
        ),
    )


def require_stream_identity(**kwargs) -> StreamIdentityEvidence:
    """Return proven evidence or raise a typed refusal carrying the evidence."""
    evidence = evaluate_stream_identity(**kwargs)
    if evidence.state != "PROVEN":
        raise StreamIdentityUnproven(evidence.reason, evidence)
    return evidence
