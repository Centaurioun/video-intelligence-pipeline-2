"""Negative coverage for Gate-3 source-snapshot refusal paths and store rollback.

These tests pin refusal codes that the PR #139 implementation raises but did not
assert (temporal declaration validation, temporal evidence field/type/declaration
validation), and the store invariant that a snapshot which is published but then
fails its own post-publish verification must not be retained as evidence.

All fixtures are synthetic ISO-BMFF bytes; no real media, provider, or network
activity is involved.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from gate3.fixturegen import build_mp4
from vip_fvs.source_snapshot import (
    SourceSnapshotError,
    SourceSnapshotStore,
    VerifiedSourceSnapshot,
)

_MP4_BYTES = build_mp4(
    media_timescale=1000,
    sample_deltas=(40, 40, 80, 80),
    ctts_offsets=(0, 80, -40, -40),
)


def _store(tmp_path: Path, name: str = "snapshot-store") -> SourceSnapshotStore:
    return SourceSnapshotStore(
        tmp_path / name, max_source_bytes=64_000, max_store_bytes=128_000
    )


def _capture_mp4(tmp_path: Path, store: SourceSnapshotStore):
    source = tmp_path / "synthetic-source.mp4"
    source.write_bytes(_MP4_BYTES)
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(_MP4_BYTES).hexdigest(),
        authorization_id="authorization:synthetic",
        source_revision_id="revision:synthetic",
    )
    return source, snapshot


def _bind(store: SourceSnapshotStore, snapshot) -> dict:
    binding = store.bind_temporal_authority(
        snapshot,
        selected_stream_index=0,
        declared_vfr=True,
        declared_reordering=True,
    )
    return binding.as_evidence()


def test_temporal_declaration_refusal_uses_prefixed_refusal_code(tmp_path: Path) -> None:
    """A boolean-substitute declaration is refused with a namespaced code."""
    store = _store(tmp_path)
    _source, snapshot = _capture_mp4(tmp_path, store)

    with pytest.raises(SourceSnapshotError, match="^SNAPSHOT_TEMPORAL_DECLARATION_INVALID$"):
        store.bind_temporal_authority(
            snapshot,
            selected_stream_index=0,
            declared_vfr=1,  # type: ignore[arg-type]  # deliberate bool substitute
            declared_reordering=True,
        )


def test_temporal_declaration_refusal_covers_unmeasured_stream_index(tmp_path: Path) -> None:
    store = _store(tmp_path, name="stream-index-store")
    _source, snapshot = _capture_mp4(tmp_path, store)

    with pytest.raises(SourceSnapshotError, match="^SNAPSHOT_TEMPORAL_DECLARATION_INVALID$"):
        store.bind_temporal_authority(
            snapshot,
            selected_stream_index=True,  # type: ignore[arg-type]
            declared_vfr=True,
            declared_reordering=True,
        )


def test_failed_post_publish_verification_does_not_retain_snapshot(tmp_path: Path) -> None:
    """A published snapshot that fails re-verification must be removed, not kept.

    Without rollback the unverified directory stays in the private store, keeps
    counting toward ``max_store_bytes`` and can force later ``STORE_QUOTA_EXCEEDED``
    failures for unrelated captures.
    """

    class _VerifyFailsAfterPublish(SourceSnapshotStore):
        def verify(self, snapshot: VerifiedSourceSnapshot) -> None:  # noqa: D401
            raise SourceSnapshotError("SNAPSHOT_DIGEST_MISMATCH")

    store = _VerifyFailsAfterPublish(
        tmp_path / "rollback-store", max_source_bytes=64_000, max_store_bytes=128_000
    )
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_DIGEST_MISMATCH"):
        _capture_mp4(tmp_path, store)

    assert list(store.snapshots.iterdir()) == []
    assert list(store.staging.iterdir()) == []
    assert store._retained_bytes() == 0


def test_temporal_evidence_field_layer_is_refused(tmp_path: Path) -> None:
    store = _store(tmp_path, name="fields-store")
    _source, snapshot = _capture_mp4(tmp_path, store)
    evidence = _bind(store, snapshot)

    extra = dict(evidence)
    extra["unexpected_field"] = 1
    with pytest.raises(SourceSnapshotError, match="^SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID$"):
        store.verify_temporal_authority(snapshot, extra)

    missing = dict(evidence)
    missing.pop("evidence_sha256")
    with pytest.raises(SourceSnapshotError, match="^SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID$"):
        store.verify_temporal_authority(snapshot, missing)


@pytest.mark.parametrize(
    ("label", "mutation"),
    [
        ("timebase-not-dict", lambda ev: ev.__setitem__("timebase", 1000)),
        ("timebase-extra-key", lambda ev: ev["timebase"].__setitem__("extra", 1)),
        ("timebase-numerator-string", lambda ev: ev["timebase"].__setitem__("num", "1")),
        ("schema-version-string", lambda ev: ev.__setitem__("schema_version", "1")),
        ("byte-count-string", lambda ev: ev.__setitem__("source_byte_count", "12")),
        ("pts-ticks-not-list", lambda ev: ev.__setitem__("pts_ticks", (0, 40))),
        ("pts-tick-boolean", lambda ev: ev["pts_ticks"].__setitem__(0, True)),
        ("evidence-digest-not-sha256", lambda ev: ev.__setitem__("evidence_sha256", "zz" * 32)),
    ],
)
def test_temporal_evidence_type_layer_is_refused(tmp_path: Path, label: str, mutation) -> None:
    store = _store(tmp_path, name=f"types-store-{label}")
    _source, snapshot = _capture_mp4(tmp_path, store)
    evidence = _bind(store, snapshot)
    forged = copy.deepcopy(evidence)
    mutation(forged)

    with pytest.raises(SourceSnapshotError, match="^SNAPSHOT_TEMPORAL_EVIDENCE_TYPES_INVALID$"):
        store.verify_temporal_authority(snapshot, forged)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("declared_vfr", "yes"),
        ("declared_vfr", 1),
        ("declared_reordering", None),
    ],
)
def test_temporal_evidence_declaration_layer_is_refused(
    tmp_path: Path, field: str, value: object,
) -> None:
    store = _store(tmp_path, name=f"declarations-store-{field}-{value!r}".replace("'", ""))
    _source, snapshot = _capture_mp4(tmp_path, store)
    evidence = _bind(store, snapshot)
    forged = copy.deepcopy(evidence)
    forged[field] = value

    with pytest.raises(
        SourceSnapshotError, match="^SNAPSHOT_TEMPORAL_EVIDENCE_DECLARATION_INVALID$"
    ):
        store.verify_temporal_authority(snapshot, forged)


def test_valid_temporal_evidence_still_round_trips(tmp_path: Path) -> None:
    """The layered refusals above must not reject a well-formed binding."""
    store = _store(tmp_path, name="round-trip-store")
    _source, snapshot = _capture_mp4(tmp_path, store)
    evidence = _bind(store, snapshot)

    binding = store.verify_temporal_authority(snapshot, evidence)
    assert binding.as_evidence() == evidence
    assert json.loads(json.dumps(evidence)) == evidence
