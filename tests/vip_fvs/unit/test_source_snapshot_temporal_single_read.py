"""Single-read temporal binding coverage (PR #146 review residual issue).

Before this change ``bind_temporal_authority`` materialized the whole snapshot
twice: ``_validate_iso_bmff_timing_bounds`` and ``parse_iso_bmff_timing`` each
called ``Path.read_bytes``.  The review recorded the resulting 2x snapshot-size
peak as a residual technical issue.  These tests pin the single-materialization
contract, exact PTS/timebase equality with the pre-change output, and the
unchanged public refusal semantics.

All fixtures are synthetic ISO-BMFF bytes; no real media, provider, or network
activity is involved.
"""
from __future__ import annotations

import hashlib
import pathlib
import struct
import tracemalloc
from pathlib import Path

import pytest

from gate3.fixturegen import build_mp4
import vip_fvs.source_snapshot as source_snapshot
from vip_fvs.source_snapshot import (
    SourceSnapshotError,
    SourceSnapshotStore,
)


# A 4-sample ``ctts`` reorder fixture (composition offsets reorder presentation PTS).
_REORDER_BYTES = build_mp4(
    media_timescale=1000,
    sample_deltas=(40, 40, 80, 80),
    ctts_offsets=(0, 80, -40, -40),
)

# Frozen pre-change measurement of ``_REORDER_BYTES``; the single-read path must
# reproduce it byte-for-byte, including exact PTS/timebase interpretation.
_FROZEN_PARSE = {
    "composition_offsets": (0, 80, -40, -40),
    "derivation": "iso-bmff: mdhd.timescale + stts + elst + ctts composition offsets",
    "dts_ticks": (0, 40, 80, 160),
    "duration_consistency": "MISMATCH",
    "duration_ts": 240,
    "has_b_frames": 1,
    "media_time_offset": 0,
    "media_timescale": 1000,
    "nb_frames": 4,
    "presentation_origin_ticks": 0,
    "presentation_pts_ticks": (0, 40, 120, 120),
    "pts_equals_dts": False,
    "pts_ticks": (0, 40, 120, 120),
    "selected_stream_index": 0,
    "source_bytes_sha256": "31d15b1c0e8c3446d0edb66238cd7847a2afa1bb6e8fbe7c7bd32e42542a2b50",
    "stream_count": 1,
    "stream_handler": "vide",
    "stream_identity_derivation": "sole_timing_bearing_video_trak",
    "stream_index": 0,
    "tail_duration_ticks": 80,
}

_FROZEN_BINDING = {
    "declared_reordering": True,
    "declared_vfr": True,
    "dts_ticks": (0, 40, 80, 160),
    "pts_ticks": (0, 40, 120, 120),
    "source_byte_count": len(_REORDER_BYTES),
    "source_revision_id": "revision:synthetic",
    "source_sha256": "31d15b1c0e8c3446d0edb66238cd7847a2afa1bb6e8fbe7c7bd32e42542a2b50",
    "stream_count": 1,
    "selected_stream_index": 0,
    "timebase_num": 1,
    "timebase_den": 1000,
}


def _store(tmp_path: Path, name: str = "store", *, max_source_bytes: int = 64_000) -> SourceSnapshotStore:
    return SourceSnapshotStore(
        tmp_path / name,
        max_source_bytes=max_source_bytes,
        max_store_bytes=max_source_bytes * 4,
    )


def _capture(tmp_path: Path, blob: bytes = _REORDER_BYTES, *, name: str = "snapshot-store"):
    store = _store(tmp_path, name, max_source_bytes=max(64_000, len(blob) * 2))
    source = tmp_path / f"{name}-source.mp4"
    source.write_bytes(blob)
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(blob).hexdigest(),
        authorization_id="authorization:synthetic",
        source_revision_id="revision:synthetic",
    )
    return store, source, snapshot


def _bind(store: SourceSnapshotStore, snapshot):
    return store.bind_temporal_authority(
        snapshot,
        selected_stream_index=0,
        declared_vfr=True,
        declared_reordering=True,
    )


# ---------------------------------------------------------------------------
# 1. The timing measurement must not re-read the snapshot through the filesystem.
# ---------------------------------------------------------------------------


def test_binding_does_not_reread_snapshot_bytes_for_timing_measurement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Timing validation and parsing share one materialization of the snapshot.

    Pre-change the bounds validator and the ISO-BMFF parser each called
    ``Path.read_bytes``, so a binding performed two full-file materializations
    of an already digest-verified snapshot.
    """
    store, _source, snapshot = _capture(tmp_path)
    calls: list[str] = []
    real_read_bytes = pathlib.Path.read_bytes

    def counting_read_bytes(self) -> bytes:
        calls.append(str(self))
        return real_read_bytes(self)

    monkeypatch.setattr(pathlib.Path, "read_bytes", counting_read_bytes)
    binding = _bind(store, snapshot)

    assert calls == [], f"temporal binding re-read snapshot bytes via read_bytes: {calls}"
    assert binding.pts_ticks == (0, 40, 120, 120)
    assert binding.timebase_den == 1000


def test_binding_materializes_snapshot_bytes_exactly_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The shared read helper is invoked once, for the digest-verified snapshot path."""
    store, _source, snapshot = _capture(tmp_path)
    calls: list[pathlib.Path] = []
    real_reader = source_snapshot._read_snapshot_bytes

    def counting_reader(path: pathlib.Path, *args, **kwargs) -> bytes:
        calls.append(path)
        return real_reader(path, *args, **kwargs)

    monkeypatch.setattr(source_snapshot, "_read_snapshot_bytes", counting_reader)
    binding = _bind(store, snapshot)

    assert calls == [snapshot.snapshot_path]
    assert binding.source_sha256 == snapshot.sha256


def test_binding_peak_allocation_scales_with_one_snapshot_copy(
    tmp_path: Path,
) -> None:
    """A binding peaks near 1x the snapshot size, not the pre-change 2x.

    An 8 MiB fixture keeps the fixed ~2 MiB streaming-digest buffer (used by
    ``verify``) small relative to the snapshot: the single-read binding peaks at
    ~1.25x here, while the pre-change two-materialization binding peaked at 2x.
    """
    size = 8 * 1024 * 1024
    fixture = build_mp4(
        media_timescale=1000,
        sample_deltas=(40, 40, 80, 80),
        ctts_offsets=(0, 80, -40, -40),
    )
    padding = size - len(fixture) - 8
    blob = fixture + struct.pack(">I", 8 + padding) + b"free" + b"P" * padding
    assert len(blob) == size
    store, _source, snapshot = _capture(tmp_path, blob, name="peak-store")
    del blob

    tracemalloc.start()
    try:
        _bind(store, snapshot)
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    # Pre-change this peaked at 2x (two concurrent full-file materializations);
    # the single-read contract stays near one snapshot copy plus the bounded
    # streaming-digest buffer.
    assert peak < 1.5 * size, f"binding peak allocation {peak} exceeds one snapshot copy"


def test_bounds_validation_and_parsing_share_one_byte_view(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The validator and the parser receive the very same materialized bytes."""
    store, _source, snapshot = _capture(tmp_path)
    seen: list[tuple[str, object]] = []
    real_bounds = source_snapshot._validate_iso_bmff_timing_bounds

    def recording_bounds(raw) -> None:
        seen.append(("bounds", raw))
        real_bounds(raw)

    from gate3 import container as container_module

    real_parse = container_module.parse_iso_bmff_timing_bytes

    def recording_parse(raw, *, selected_stream_index=None):
        seen.append(("parse", raw))
        return real_parse(raw, selected_stream_index=selected_stream_index)

    monkeypatch.setattr(source_snapshot, "_validate_iso_bmff_timing_bounds", recording_bounds)
    monkeypatch.setattr(container_module, "parse_iso_bmff_timing_bytes", recording_parse)
    _bind(store, snapshot)

    assert [name for name, _raw in seen] == ["bounds", "parse"]
    assert seen[0][1] is seen[1][1]


def _read_direct(path: Path):
    return source_snapshot._read_snapshot_bytes(path, limit=64_000)


def test_shared_read_refuses_symlinked_snapshot_path(tmp_path: Path) -> None:
    target = tmp_path / "target.mp4"
    target.write_bytes(_REORDER_BYTES)
    link = tmp_path / "link.mp4"
    link.symlink_to(target)

    with pytest.raises(SourceSnapshotError) as excinfo:
        _read_direct(link)
    assert str(excinfo.value) == "SNAPSHOT_PATH_OPEN_FAILED"


def test_shared_read_refuses_non_regular_snapshot_path(tmp_path: Path) -> None:
    with pytest.raises(SourceSnapshotError) as excinfo:
        _read_direct(tmp_path)
    assert str(excinfo.value) == "SNAPSHOT_PATH_NOT_REGULAR_NOFOLLOW"


def test_shared_read_refuses_snapshot_above_its_byte_budget(tmp_path: Path) -> None:
    target = tmp_path / "target.mp4"
    target.write_bytes(_REORDER_BYTES)

    with pytest.raises(SourceSnapshotError) as excinfo:
        source_snapshot._read_snapshot_bytes(target, limit=len(_REORDER_BYTES) - 1)
    assert str(excinfo.value) == "SOURCE_QUOTA_EXCEEDED"


# ---------------------------------------------------------------------------
# 2. Exact PTS/timebase equality with the pre-change output.
# ---------------------------------------------------------------------------


def test_iso_bmff_timing_measurement_is_unchanged(tmp_path: Path) -> None:
    store, _source, snapshot = _capture(tmp_path)
    from gate3.container import parse_iso_bmff_timing

    measured = parse_iso_bmff_timing(snapshot.snapshot_path)
    assert measured == _FROZEN_PARSE


def test_temporal_binding_facts_are_unchanged(tmp_path: Path) -> None:
    store, _source, snapshot = _capture(tmp_path)
    binding = _bind(store, snapshot)

    assert {
        "declared_reordering": binding.declared_reordering,
        "declared_vfr": binding.declared_vfr,
        "dts_ticks": binding.dts_ticks,
        "pts_ticks": binding.pts_ticks,
        "source_byte_count": binding.source_byte_count,
        "source_revision_id": binding.source_revision_id,
        "source_sha256": binding.source_sha256,
        "stream_count": binding.stream_count,
        "selected_stream_index": binding.selected_stream_index,
        "timebase_num": binding.timebase_num,
        "timebase_den": binding.timebase_den,
    } == _FROZEN_BINDING


# ---------------------------------------------------------------------------
# 3. Malformed temporal input keeps the public refusal contract.
# ---------------------------------------------------------------------------


def _corrupt_box_size(blob: bytes, kind: bytes, size: int) -> bytes:
    result = bytearray(blob)
    start = result.index(kind) - 4
    struct.pack_into(">I", result, start, size)
    return bytes(result)


def _inflate_stts_entry_count(blob: bytes) -> bytes:
    result = bytearray(blob)
    stts_start = result.index(b"stts") - 4
    count_offset = stts_start + 8 + 4
    count = struct.unpack_from(">I", result, count_offset)[0]
    struct.pack_into(">I", result, count_offset, count + 1)
    return bytes(result)


def test_box_bounds_violation_keeps_public_code_and_internal_reason(tmp_path: Path) -> None:
    """``SNAPSHOT_TEMPORAL_BOX_BOUNDS_INVALID`` stays an exact internal refusal reason.

    The public refusal code remains ``SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED``;
    the specific reason is carried, unchanged, on ``__cause__``.
    """
    malformed = _corrupt_box_size(_REORDER_BYTES, b"stsd", len(_REORDER_BYTES) + 4096)
    store, _source, snapshot = _capture(tmp_path, malformed, name="bounds-store")

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot)

    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED"
    assert isinstance(excinfo.value.__cause__, SourceSnapshotError)
    assert str(excinfo.value.__cause__) == "SNAPSHOT_TEMPORAL_BOX_BOUNDS_INVALID"


def test_stts_entry_count_violation_keeps_public_refusal_code(tmp_path: Path) -> None:
    malformed = _inflate_stts_entry_count(_REORDER_BYTES)
    store, _source, snapshot = _capture(tmp_path, malformed, name="stts-store")

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot)

    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED"


def test_shared_materialization_does_not_require_os_readinto(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The single-read path must not depend on the Python 3.14 ``os.readinto``.

    ``os.readinto`` was added in Python 3.14.  The repository declares no
    ``requires-python`` and its pinned-runtime documentation names Python
    3.11.9, so a binding that relies on the helper would turn temporal
    evidence into an uncaught ``AttributeError`` on those interpreters
    instead of a measured result or a typed refusal.
    """
    store, _source, snapshot = _capture(tmp_path)
    monkeypatch.delattr(source_snapshot.os, "readinto", raising=False)

    binding = _bind(store, snapshot)

    assert binding.pts_ticks == (0, 40, 120, 120)
    assert binding.timebase_den == 1000
