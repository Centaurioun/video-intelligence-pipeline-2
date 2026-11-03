"""Synthetic integration coverage for snapshot-bound temporal identity."""
from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import struct

import pytest

from gate3.fixturegen import build_mp4
from vip_fvs.refinement_adapter import refine_retrieval_candidate
from vip_fvs.source_snapshot import SourceSnapshotError, SourceSnapshotStore


def _capture(tmp_path: Path, *, revision: str = "revision:synthetic-a"):
    source = tmp_path / "generated-vfr-reordered.mp4"
    source.write_bytes(build_mp4(
        media_timescale=1000,
        sample_deltas=(40, 40, 80, 80),
        ctts_offsets=(0, 80, -40, -40),
    ))
    store = SourceSnapshotStore(
        tmp_path / "snapshot-store", max_source_bytes=64_000, max_store_bytes=128_000,
    )
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        authorization_id="authorization:synthetic-a",
        source_revision_id=revision,
    )
    return store, source, snapshot


def _truncate_mdhd_payload(container: bytes) -> bytes:
    """Put a short mdhd last so unpacking cannot read beyond its box from later bytes."""
    mdhd_start = container.index(b"mdhd") - 4
    mdhd_size = struct.unpack_from(">I", container, mdhd_start)[0]
    hdlr_start = mdhd_start + mdhd_size
    hdlr_size = struct.unpack_from(">I", container, hdlr_start)[0]
    minf_start = hdlr_start + hdlr_size
    minf_size = struct.unpack_from(">I", container, minf_start)[0]
    mdia_start = container.index(b"mdia") - 4
    mdia_size = struct.unpack_from(">I", container, mdia_start)[0]
    mdia_end = mdia_start + mdia_size
    mdat_start = container.index(b"mdat") - 4
    removed = mdhd_size - 20
    truncated_mdhd = bytearray(container[mdhd_start:mdhd_start + 20])
    struct.pack_into(">I", truncated_mdhd, 0, 20)
    result = bytearray(
        container[:mdhd_start]
        + container[hdlr_start:minf_start + minf_size]
        + truncated_mdhd
        + container[mdia_end:mdat_start]
    )
    for parent in (b"mdia", b"trak", b"moov"):
        parent_start = container.index(parent) - 4
        parent_size = struct.unpack_from(">I", container, parent_start)[0]
        struct.pack_into(">I", result, parent_start, parent_size - removed)
    return bytes(result)


def _truncate_timing_box(container: bytes, kind: bytes, *, remove: int) -> bytes:
    """Truncate a timing leaf and adjust its enclosing ISO-BMFF box sizes."""
    start = container.index(kind) - 4
    size = struct.unpack_from(">I", container, start)[0]
    assert size > 8 + remove
    result = bytearray(container[:start + size - remove] + container[start + size:])
    struct.pack_into(">I", result, start, size - remove)
    parents = {
        b"mdhd": (b"moov", b"trak", b"mdia"),
        b"stts": (b"moov", b"trak", b"mdia", b"minf", b"stbl"),
        b"elst": (b"moov", b"trak", b"edts"),
    }[kind]
    for parent in parents:
        parent_start = container.index(parent) - 4
        parent_size = struct.unpack_from(">I", container, parent_start)[0]
        struct.pack_into(">I", result, parent_start, parent_size - remove)
    return bytes(result)


def _capture_bytes(tmp_path: Path, source_bytes: bytes, name: str):
    source = tmp_path / name
    source.write_bytes(source_bytes)
    store = SourceSnapshotStore(
        tmp_path / "snapshot-store", max_source_bytes=64_000, max_store_bytes=128_000,
    )
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(source_bytes).hexdigest(),
        authorization_id=f"authorization:{name}",
        source_revision_id=f"revision:{name}",
    )
    return store, snapshot


def test_temporal_binding_remeasures_snapshot_identity_and_declared_constraints(
    tmp_path: Path,
) -> None:
    store, source, snapshot = _capture(tmp_path)

    binding = store.bind_temporal_authority(
        snapshot,
        selected_stream_index=0,
        declared_vfr=True,
        declared_reordering=True,
    )
    evidence = binding.as_evidence()

    assert binding.source_revision_id == "revision:synthetic-a"
    assert binding.source_sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
    assert binding.source_byte_count == len(source.read_bytes())
    assert binding.snapshot_id == snapshot.snapshot_path.parent.name
    assert binding.snapshot_manifest_sha256 == snapshot.manifest_sha256
    assert binding.selected_stream_index == 0
    assert binding.timebase_num == 1 and binding.timebase_den == 1000
    assert binding.pts_ticks == (0, 40, 120, 120)
    assert binding.dts_ticks == (0, 40, 80, 160)
    assert evidence["declared_vfr"] is True
    assert evidence["declared_reordering"] is True
    assert store.verify_temporal_authority(snapshot, evidence) == binding


def test_snapshot_binding_composes_with_refinement_without_coordinate_conversion(
    tmp_path: Path,
) -> None:
    store, _source, snapshot = _capture(tmp_path)
    binding = store.bind_temporal_authority(
        snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=True,
    )
    hit = {
        "source_path": str(snapshot.snapshot_path),
        "source_sha256": snapshot.sha256,
        "timebase_num": 1,
        "timebase_den": 1000,
        "rank": 1,
        "score": 0.9,
    }

    result = refine_retrieval_candidate(
        hit,
        source_path=snapshot.snapshot_path,
        source_revision_id="revision:synthetic-a",
        requested_pts=(40, 120),
        stream_index=0,
        attempt_id="attempt:synthetic-a",
        snapshot_evidence=snapshot.as_evidence(),
    )

    assert result.binding_eligible is True
    refinement = result.measured_refinement
    byte_entry = refinement["validation_results"][1]
    assert refinement["start_ticks"] == 40 and refinement["end_ticks"] == 120
    assert refinement["time_base"] == {"num": 1, "den": 1000}
    assert byte_entry["source_bytes_sha256"] == snapshot.sha256
    assert byte_entry["measured_stream_index"] == binding.selected_stream_index == 0
    assert byte_entry["pts_ticks"] == list(binding.pts_ticks) == [0, 40, 120, 120]
    assert byte_entry["dts_ticks"] == list(binding.dts_ticks) == [0, 40, 80, 160]
    assert byte_entry["byte_authority"]["container_path"] == str(snapshot.snapshot_path)
    assert byte_entry["byte_authority"]["snapshot_evidence"] == snapshot.as_evidence()


def test_temporal_binding_refuses_truncated_mdhd_with_typed_error(tmp_path: Path) -> None:
    source = tmp_path / "truncated-mdhd.mp4"
    valid = build_mp4(
        media_timescale=1000,
        sample_deltas=(40, 40, 80, 80),
        ctts_offsets=(0, 80, -40, -40),
    )
    source.write_bytes(_truncate_mdhd_payload(valid))
    store = SourceSnapshotStore(
        tmp_path / "snapshot-store", max_source_bytes=64_000, max_store_bytes=128_000,
    )
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        authorization_id="authorization:synthetic-truncated-mdhd",
        source_revision_id="revision:synthetic-truncated-mdhd",
    )

    with pytest.raises(
        SourceSnapshotError, match="SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED",
    ) as caught:
        store.bind_temporal_authority(
            snapshot,
            selected_stream_index=0,
            declared_vfr=True,
            declared_reordering=True,
        )

    assert isinstance(caught.value.__cause__, struct.error)


@pytest.mark.parametrize("kind", [b"stts", b"elst"])
def test_temporal_binding_refuses_truncated_timing_tables_with_typed_error(
    tmp_path: Path, kind: bytes,
) -> None:
    valid = build_mp4(
        media_timescale=1000,
        sample_deltas=(40, 40, 80, 80),
        ctts_offsets=(0, 80, -40, -40),
        media_time_offset=12 if kind == b"elst" else 0,
    )
    malformed = _truncate_timing_box(valid, kind, remove=4)
    store, snapshot = _capture_bytes(tmp_path, malformed, f"truncated-{kind.decode()}.mp4")

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED"):
        store.bind_temporal_authority(
            snapshot, selected_stream_index=0,
            declared_vfr=True, declared_reordering=True,
        )


def test_temporal_binding_rejects_fields_crossing_leaf_box_boundary(tmp_path: Path) -> None:
    valid = build_mp4(
        media_timescale=1000,
        sample_deltas=(40, 40, 80, 80),
        ctts_offsets=(0, 80, -40, -40),
    )
    malformed = _truncate_timing_box(valid, b"mdhd", remove=8)
    store, snapshot = _capture_bytes(tmp_path, malformed, "cross-box-mdhd.mp4")

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED"):
        store.bind_temporal_authority(
            snapshot, selected_stream_index=0,
            declared_vfr=True, declared_reordering=True,
        )


@pytest.mark.parametrize(
    ("declared_vfr", "declared_reordering", "error"),
    [
        (False, True, "SNAPSHOT_VFR_DECLARATION_MISMATCH"),
        (True, False, "SNAPSHOT_REORDERING_DECLARATION_MISMATCH"),
    ],
)
def test_temporal_binding_refuses_conflicting_declared_constraints(
    tmp_path: Path, declared_vfr: bool, declared_reordering: bool, error: str,
) -> None:
    store, _source, snapshot = _capture(tmp_path)

    with pytest.raises(SourceSnapshotError, match=error):
        store.bind_temporal_authority(
            snapshot,
            selected_stream_index=0,
            declared_vfr=declared_vfr,
            declared_reordering=declared_reordering,
        )


def test_temporal_binding_refuses_stale_or_copied_snapshot_identity(tmp_path: Path) -> None:
    store, _source, snapshot = _capture(tmp_path)
    evidence = store.bind_temporal_authority(
        snapshot, selected_stream_index=0,
        declared_vfr=True, declared_reordering=True,
    ).as_evidence()

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_MANIFEST_MISMATCH"):
        store.bind_temporal_authority(
            replace(snapshot, source_revision_id="revision:stale"),
            selected_stream_index=0,
            declared_vfr=True,
            declared_reordering=True,
        )

    copied_store = SourceSnapshotStore(
        tmp_path / "copied-store", max_source_bytes=64_000, max_store_bytes=128_000,
    )
    copied = copied_store.capture(
        snapshot.snapshot_path,
        expected_sha256=snapshot.sha256,
        authorization_id="authorization:copied",
        source_revision_id="revision:synthetic-a",
    )
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH"):
        copied_store.verify_temporal_authority(copied, evidence)


def test_temporal_binding_refuses_forged_pts_even_with_recomputed_digest(tmp_path: Path) -> None:
    store, _source, snapshot = _capture(tmp_path)
    evidence = store.bind_temporal_authority(
        snapshot, selected_stream_index=0,
        declared_vfr=True, declared_reordering=True,
    ).as_evidence()
    evidence["pts_ticks"] = [0, 40, 80, 160]
    body = dict(evidence)
    body.pop("evidence_sha256")
    import json

    evidence["evidence_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH"):
        store.verify_temporal_authority(snapshot, evidence)
