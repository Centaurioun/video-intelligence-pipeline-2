"""File-bound invocation policy for Gate-3 stream identity evidence."""
from __future__ import annotations

import hashlib
import json
import struct
from collections.abc import Mapping
from pathlib import Path

from gate3.stream_identity import (
    REASON_BOUND_EVIDENCE_UNAVAILABLE,
    REASON_SELECTED_NOT_VIDEO,
    REASON_SELECTION_AMBIGUOUS,
    StreamIdentityEvidence,
    StreamIdentityUnproven,
    _single_moov_box,
    _single_tkhd_per_track,
    _track_children,
    _track_handler,
    require_stream_identity,
)


def _refusal(
    *,
    reason: str,
    container_sha256: str,
    probe_digest: str = "",
    probe_provenance: str = "",
) -> StreamIdentityUnproven:
    evidence = StreamIdentityEvidence(
        state="REFUSED",
        reason=reason,
        derivation=None,
        selected_position=None,
        track_ids=None,
        probe_ids=None,
        container_sha256=container_sha256,
        probe_digest=probe_digest,
        probe_provenance=probe_provenance,
        probe_source_binding="",
        demuxer_build_state="NOT_OBSERVED",
    )
    return StreamIdentityUnproven(reason, evidence)


def _legacy_single_track_evidence(
    *, container_sha256: str, selected_stream_index: object, handler
) -> StreamIdentityEvidence:
    if type(selected_stream_index) is not int or selected_stream_index != 0:
        raise _refusal(
            reason=REASON_SELECTION_AMBIGUOUS,
            container_sha256=container_sha256,
        )
    if handler != b"vide":
        raise _refusal(
            reason=REASON_SELECTED_NOT_VIDEO,
            container_sha256=container_sha256,
        )
    # Reuse the existing success state for compatibility, but leave derivation
    # and probe fields empty so this cannot imply a probe-to-source pairing.
    return StreamIdentityEvidence(
        state="PROVEN",
        reason=None,
        derivation=None,
        selected_position=0,
        track_ids=None,
        probe_ids=None,
        container_sha256=container_sha256,
        probe_digest="",
        probe_provenance="",
        probe_source_binding="",
        demuxer_build_state="NOT_OBSERVED",
    )


def _read_verified_container(container_path, expected_sha256):
    try:
        container_bytes = Path(container_path).read_bytes()
    except (OSError, TypeError, ValueError) as exc:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=expected_sha256 if isinstance(expected_sha256, str) else "",
        ) from exc

    actual_sha256 = hashlib.sha256(container_bytes).hexdigest()
    if expected_sha256 != actual_sha256:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=expected_sha256 if isinstance(expected_sha256, str) else "",
        )
    return container_bytes, actual_sha256


def _direct_tracks(container_bytes, container_sha256):
    try:
        moov = _single_moov_box(container_bytes)
        traks = _track_children(container_bytes, moov) if moov is not None else None
    except (LookupError, ValueError, IndexError, struct.error, TypeError, BufferError) as exc:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=container_sha256,
        ) from exc
    if not traks:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=container_sha256,
        )
    return traks


def _single_track_result(container_bytes, container_sha256, trak, selected_stream_index):
    try:
        tkhds = _single_tkhd_per_track(container_bytes, [trak])
        handler = _track_handler(container_bytes, trak) if tkhds is not None else None
    except (LookupError, ValueError, IndexError, struct.error, TypeError, BufferError) as exc:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=container_sha256,
        ) from exc
    if tkhds is None:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=container_sha256,
        )
    return _legacy_single_track_evidence(
        container_sha256=container_sha256,
        selected_stream_index=selected_stream_index,
        handler=handler,
    )


def _read_verified_probe_bytes(probe_artifact_path, probe_digest, container_sha256):
    provenance = str(probe_artifact_path) if probe_artifact_path is not None else ""
    try:
        probe_bytes = Path(probe_artifact_path).read_bytes()
    except (OSError, TypeError, ValueError) as exc:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=container_sha256,
            probe_digest=probe_digest if isinstance(probe_digest, str) else "",
            probe_provenance=provenance,
        ) from exc

    actual_digest = hashlib.sha256(probe_bytes).hexdigest()
    if probe_digest != actual_digest:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=container_sha256,
            probe_digest=probe_digest if isinstance(probe_digest, str) else "",
            probe_provenance=provenance,
        )
    return probe_bytes, actual_digest, provenance


def _parse_probe_streams(probe_bytes, probe_digest, probe_provenance, container_sha256):
    try:
        payload = json.loads(probe_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _refusal(
            reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
            container_sha256=container_sha256,
            probe_digest=probe_digest,
            probe_provenance=probe_provenance,
        ) from exc
    streams = payload.get("streams") if isinstance(payload, Mapping) else None
    return streams


def require_bound_stream_identity(
    *,
    container_path,
    container_sha256,
    probe_artifact_path,
    probe_digest,
    selected_stream_index,
) -> StreamIdentityEvidence:
    """Verify named bytes, preserve sole-track compatibility, or require S2 proof."""
    container_bytes, actual_container_sha256 = _read_verified_container(
        container_path, container_sha256
    )
    traks = _direct_tracks(container_bytes, actual_container_sha256)
    if len(traks) == 1:
        return _single_track_result(
            container_bytes,
            actual_container_sha256,
            traks[0],
            selected_stream_index,
        )

    probe_bytes, actual_probe_digest, probe_provenance = _read_verified_probe_bytes(
        probe_artifact_path, probe_digest, actual_container_sha256
    )
    probe_streams = _parse_probe_streams(
        probe_bytes, actual_probe_digest, probe_provenance, actual_container_sha256
    )
    return require_stream_identity(
        container_bytes=container_bytes,
        container_sha256=actual_container_sha256,
        probe_streams=probe_streams,
        probe_digest=actual_probe_digest,
        probe_provenance=probe_provenance,
        selected_stream_index=selected_stream_index,
    )
