from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from vip_fvs.source_snapshot import (
    SourceSnapshotError,
    SourceSnapshotStore,
    verify_snapshot_evidence,
)


def test_capture_publishes_digest_bound_private_snapshot_and_provenance(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"synthetic-source-bytes")
    store = SourceSnapshotStore(
        tmp_path / "private-store", max_source_bytes=128, max_store_bytes=8192
    )

    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        authorization_id="auth:test-001",
    )

    assert snapshot.source_locator == str(source)
    assert snapshot.snapshot_path != source
    assert snapshot.snapshot_path.read_bytes() == source.read_bytes()
    assert snapshot.byte_count == len(source.read_bytes())
    assert snapshot.sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
    assert snapshot.snapshot_path.stat().st_mode & 0o777 == 0o400
    assert snapshot.snapshot_path.parent.stat().st_mode & 0o777 == 0o700
    manifest = json.loads(snapshot.manifest_path.read_text())
    assert manifest["snapshot_sha256"] == snapshot.sha256
    assert manifest["source_locator"] == str(source)
    assert manifest["authorization_id"] == "auth:test-001"


def test_load_verified_snapshot_reuses_existing_object_without_copy(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"synthetic-source-bytes")
    store = SourceSnapshotStore(
        tmp_path / "private-store", max_source_bytes=128, max_store_bytes=8192
    )
    original = store.capture(
        source,
        expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        authorization_id="auth:test-reuse",
        source_revision_id="revision-reuse",
    )
    before = sorted(path.name for path in store.snapshots.iterdir())

    reused = store.load_verified_snapshot(original.snapshot_path.parent.name)

    assert reused == original
    assert sorted(path.name for path in store.snapshots.iterdir()) == before
    assert reused.snapshot_path == original.snapshot_path


@pytest.mark.parametrize(("field", "value"), [
    ("schema_version", 2),
    ("schema_version", True),
    ("retention", "expire_after_days:30"),
])
def test_verify_rejects_unknown_manifest_schema_or_retention(
    tmp_path: Path, field: str, value: object,
) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"synthetic-source-bytes")
    store = SourceSnapshotStore(
        tmp_path / "private-store", max_source_bytes=128, max_store_bytes=8192
    )
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        authorization_id="auth:test-manifest-contract",
    )
    manifest = json.loads(snapshot.manifest_path.read_text())
    manifest[field] = value
    body = dict(manifest)
    body.pop("manifest_sha256", None)
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    encoded = (json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
    snapshot.manifest_path.chmod(0o600)
    snapshot.manifest_path.write_bytes(encoded)
    snapshot.manifest_path.chmod(0o400)
    forged_snapshot = replace(snapshot, manifest_sha256=hashlib.sha256(encoded).hexdigest())

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_MANIFEST_MISMATCH"):
        store.verify(forged_snapshot)

    evidence = snapshot.as_evidence()
    evidence["snapshot_manifest_sha256"] = hashlib.sha256(encoded).hexdigest()
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_MANIFEST_BINDING_MISMATCH"):
        verify_snapshot_evidence(evidence)


def test_capture_preserves_all_chunks_for_multiblock_source(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    content = bytes(range(251)) * 12000
    source.write_bytes(content)
    store = SourceSnapshotStore(
        tmp_path / "private-store", max_source_bytes=4_000_000, max_store_bytes=4_000_000
    )

    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(content).hexdigest(),
        authorization_id="auth:test-multiblock",
    )

    assert snapshot.snapshot_path.read_bytes() == content
    assert snapshot.byte_count == len(content)


def test_capture_rejects_digest_mismatch_without_publishing_success(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"synthetic-source-bytes")
    root = tmp_path / "private-store"
    store = SourceSnapshotStore(root, max_source_bytes=128, max_store_bytes=8192)

    with pytest.raises(SourceSnapshotError, match="SOURCE_DIGEST_MISMATCH"):
        store.capture(source, expected_sha256="0" * 64, authorization_id="auth:test-002")

    assert not list(root.glob("snapshots/*/manifest.json"))


def test_capture_rejects_symlink_source_before_reading_content(tmp_path: Path) -> None:
    target = tmp_path / "target.bin"
    target.write_bytes(b"synthetic-source-bytes")
    link = tmp_path / "source-link.bin"
    link.symlink_to(target)
    store = SourceSnapshotStore(
        tmp_path / "private-store", max_source_bytes=128, max_store_bytes=8192
    )

    with pytest.raises(SourceSnapshotError, match="SOURCE_PATH_NOT_REGULAR_NOFOLLOW"):
        store.capture(
            link,
            expected_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
            authorization_id="auth:test-003",
        )


def test_capture_enforces_finite_source_and_store_quotas(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"x" * 17)
    store = SourceSnapshotStore(
        tmp_path / "private-store", max_source_bytes=16, max_store_bytes=32
    )

    with pytest.raises(SourceSnapshotError, match="SOURCE_QUOTA_EXCEEDED"):
        store.capture(
            source,
            expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            authorization_id="auth:test-004",
        )

    assert not list((tmp_path / "private-store" / "snapshots").iterdir())


def test_consume_revalidates_snapshot_bytes_before_returning_path(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"synthetic-source-bytes")
    store = SourceSnapshotStore(
        tmp_path / "private-store", max_source_bytes=128, max_store_bytes=8192
    )
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        authorization_id="auth:test-005",
    )
    snapshot.snapshot_path.chmod(0o600)
    snapshot.snapshot_path.write_bytes(b"changed")
    snapshot.snapshot_path.chmod(0o400)

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_DIGEST_MISMATCH"):
        store.verify(snapshot)


def test_store_refuses_new_capture_when_existing_successes_exhaust_quota(tmp_path: Path) -> None:
    source_a = tmp_path / "a.bin"
    source_b = tmp_path / "b.bin"
    source_a.write_bytes(b"a" * 8)
    source_b.write_bytes(b"b" * 1000)
    store = SourceSnapshotStore(
        tmp_path / "private-store", max_source_bytes=2000, max_store_bytes=4500
    )
    store.capture(
        source_a,
        expected_sha256=hashlib.sha256(source_a.read_bytes()).hexdigest(),
        authorization_id="auth:test-006a",
    )

    with pytest.raises(SourceSnapshotError, match="STORE_QUOTA_EXCEEDED"):
        store.capture(
            source_b,
            expected_sha256=hashlib.sha256(source_b.read_bytes()).hexdigest(),
            authorization_id="auth:test-006b",
        )


def test_capture_requires_positive_finite_quotas(tmp_path: Path) -> None:
    for value in (0, -1, None, float("inf"), True):
        with pytest.raises((SourceSnapshotError, TypeError, ValueError)):
            SourceSnapshotStore(
                tmp_path / f"store-{str(value)}", max_source_bytes=value, max_store_bytes=32
            )
