"""A-9 strict-V1 edit-list origin enforcement for temporal binding.

Authority: ``docs/agent-runs/2026-10-25-g3-cprime-v1/authority-disposition-matrix.md``
row A-9 (Owner-resolved, authorized (b)) requires ``elst.media_time == 0``;
a nonzero origin is refused as ``EDIT_LIST_ORIGIN_NOT_APPLIED`` on both routes
(``bind_temporal_authority`` and ``verify_temporal_authority``) and is never
normalized or silently subtracted.  The frozen V1 evidence payload shape is
unchanged: this is a fail-closed refusal, not a schema change.

All fixtures are synthetic ISO-BMFF bytes built in-process; no real media,
provider, network, or model activity is involved.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from gate3.fixturegen import build_mp4
from gate3 import container as container_module
from vip_fvs.source_snapshot import (
    SourceSnapshotError,
    SourceSnapshotStore,
)

# Uniform decode deltas, so declared_vfr=False and declared_reordering=False.
_SAMPLE_DELTAS = (40, 40, 40, 40)

_ORIGIN_ZERO_BYTES = build_mp4(
    media_timescale=1000,
    sample_deltas=_SAMPLE_DELTAS,
)
_ORIGIN_NONZERO_BYTES = build_mp4(
    media_timescale=1000,
    sample_deltas=_SAMPLE_DELTAS,
    media_time_offset=100,
)

# The V1 evidence field set is frozen; an origin field must never appear here.
_V1_EVIDENCE_FIELDS = {
    "schema_version", "snapshot_id", "snapshot_manifest_sha256",
    "source_revision_id", "source_sha256", "source_byte_count",
    "selected_stream_index", "stream_count", "timebase",
    "pts_ticks", "dts_ticks", "declared_vfr", "declared_reordering",
    "evidence_sha256",
}


def _store(tmp_path: Path, name: str) -> SourceSnapshotStore:
    return SourceSnapshotStore(
        tmp_path / name,
        max_source_bytes=64_000,
        max_store_bytes=256_000,
    )


def _capture(tmp_path: Path, blob: bytes, *, name: str):
    store = _store(tmp_path, name)
    source = tmp_path / f"{name}-source.mp4"
    source.write_bytes(blob)
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(blob).hexdigest(),
        authorization_id="authorization:synthetic",
        source_revision_id="revision:synthetic",
    )
    return store, snapshot


def _bind(store: SourceSnapshotStore, snapshot):
    return store.bind_temporal_authority(
        snapshot,
        selected_stream_index=0,
        declared_vfr=False,
        declared_reordering=False,
    )


# ---------------------------------------------------------------------------
# 1. Nonzero elst media_time on the selected video track is refused.
# ---------------------------------------------------------------------------


def test_nonzero_edit_list_media_time_refuses_binding(tmp_path: Path) -> None:
    """Strict V1 supports only an origin of zero; nonzero is a refusal."""
    store, snapshot = _capture(tmp_path, _ORIGIN_NONZERO_BYTES, name="nonzero-store")

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot)

    assert str(excinfo.value) == "EDIT_LIST_ORIGIN_NOT_APPLIED"


# ---------------------------------------------------------------------------
# 2. The default (origin zero) fixture still binds with the frozen V1 shape.
# ---------------------------------------------------------------------------


def test_zero_origin_binding_succeeds_with_unchanged_v1_evidence(tmp_path: Path) -> None:
    """Zero origin keeps today's success path byte-identical in evidence shape."""
    store, snapshot = _capture(tmp_path, _ORIGIN_ZERO_BYTES, name="zero-store")

    binding = _bind(store, snapshot)
    evidence = binding.as_evidence()

    assert evidence["schema_version"] == 1
    assert set(evidence) == _V1_EVIDENCE_FIELDS
    assert "presentation_origin_ticks" not in evidence
    assert "media_time_offset" not in evidence
    assert evidence["pts_ticks"] == [0, 40, 80, 120]
    assert evidence["dts_ticks"] == [0, 40, 80, 120]
    # The frozen evidence digest is computed over the unchanged field set.
    assert isinstance(evidence["evidence_sha256"], str)
    assert len(evidence["evidence_sha256"]) == 64


def test_zero_origin_evidence_survives_verify_temporal_authority(tmp_path: Path) -> None:
    store, snapshot = _capture(tmp_path, _ORIGIN_ZERO_BYTES, name="zero-verify-store")
    binding = _bind(store, snapshot)

    rebound = store.verify_temporal_authority(snapshot, binding.as_evidence())

    assert rebound.pts_ticks == (0, 40, 80, 120)
    assert rebound.as_evidence() == binding.as_evidence()


# ---------------------------------------------------------------------------
# 3. verify_temporal_authority rebinds and must refuse the nonzero origin too.
# ---------------------------------------------------------------------------


def test_verify_temporal_authority_refuses_nonzero_origin_snapshot(tmp_path: Path) -> None:
    """The rebinding route cannot admit a snapshot that bind itself refuses."""
    zero_store, zero_snapshot = _capture(tmp_path, _ORIGIN_ZERO_BYTES, name="zero-ev-store")
    evidence = _bind(zero_store, zero_snapshot).as_evidence()
    nonzero_store, nonzero_snapshot = _capture(
        tmp_path, _ORIGIN_NONZERO_BYTES, name="nonzero-ev-store",
    )

    with pytest.raises(SourceSnapshotError) as excinfo:
        nonzero_store.verify_temporal_authority(nonzero_snapshot, evidence)

    assert str(excinfo.value) == "EDIT_LIST_ORIGIN_NOT_APPLIED"


# ---------------------------------------------------------------------------
# 4. An absent edit list measures origin zero and therefore still binds.
# ---------------------------------------------------------------------------


def test_absent_edit_list_measures_zero_origin_and_binds(tmp_path: Path) -> None:
    assert b"elst" not in _ORIGIN_ZERO_BYTES
    measured = container_module.parse_iso_bmff_timing_bytes(
        _ORIGIN_ZERO_BYTES, selected_stream_index=0,
    )
    assert measured["presentation_origin_ticks"] == 0
    assert measured["media_time_offset"] == 0

    store, snapshot = _capture(tmp_path, _ORIGIN_ZERO_BYTES, name="absent-elst-store")
    binding = _bind(store, snapshot)
    assert binding.pts_ticks == (0, 40, 80, 120)


# ---------------------------------------------------------------------------
# 5. A missing or wrongly typed measured origin fails closed, not open.
# ---------------------------------------------------------------------------


def _patched_parse(monkeypatch: pytest.MonkeyPatch, mutate) -> None:
    real_parse = container_module.parse_iso_bmff_timing_bytes

    def fake_parse(raw, *, selected_stream_index=None):
        measured = real_parse(raw, selected_stream_index=selected_stream_index)
        mutate(measured)
        return measured

    monkeypatch.setattr(container_module, "parse_iso_bmff_timing_bytes", fake_parse)


def test_missing_measured_origin_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, snapshot = _capture(tmp_path, _ORIGIN_ZERO_BYTES, name="missing-origin-store")
    _patched_parse(monkeypatch, lambda measured: measured.pop("presentation_origin_ticks"))

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot)

    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_FACTS_INVALID"


def test_boolean_measured_origin_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, snapshot = _capture(tmp_path, _ORIGIN_ZERO_BYTES, name="bool-origin-store")

    def mutate(measured):
        measured["presentation_origin_ticks"] = False

    _patched_parse(monkeypatch, mutate)

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot)

    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_FACTS_INVALID"
