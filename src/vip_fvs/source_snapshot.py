"""Private, digest-verified custody for authorized local source bytes.

Successful snapshots are durable evidence inputs and are never automatically
expired or evicted. POSIX permissions and digest checks protect against
accidental changes and other users, not a malicious process under this user.
"""
from __future__ import annotations

from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import uuid
from typing import Any


class SourceSnapshotError(ValueError):
    """Raised when source bytes cannot be safely captured or consumed."""


@dataclass(frozen=True)
class VerifiedSourceSnapshot:
    source_locator: str
    snapshot_path: Path
    manifest_path: Path
    sha256: str
    byte_count: int
    authorization_id: str
    source_revision_id: str | None
    manifest_sha256: str
    max_source_bytes: int
    max_store_bytes: int

    def as_evidence(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_path.parent.name,
            "snapshot_path": str(self.snapshot_path),
            "manifest_path": str(self.manifest_path),
            "snapshot_sha256": self.sha256,
            "source_byte_count": self.byte_count,
            "source_locator": self.source_locator,
            "authorization_id": self.authorization_id,
            "source_revision_id": self.source_revision_id,
            "snapshot_manifest_sha256": self.manifest_sha256,
            "max_source_bytes": self.max_source_bytes,
            "max_store_bytes": self.max_store_bytes,
        }


@dataclass(frozen=True)
class VerifiedSourceTemporalBinding:
    """Measured temporal identity tied to one verified source snapshot."""

    snapshot_id: str
    snapshot_manifest_sha256: str
    source_revision_id: str
    source_sha256: str
    source_byte_count: int
    selected_stream_index: int
    stream_count: int
    timebase_num: int
    timebase_den: int
    pts_ticks: tuple[int, ...]
    dts_ticks: tuple[int, ...]
    declared_vfr: bool
    declared_reordering: bool
    evidence_sha256: str

    def as_evidence(self) -> dict[str, Any]:
        body = {
            "schema_version": 1,
            "snapshot_id": self.snapshot_id,
            "snapshot_manifest_sha256": self.snapshot_manifest_sha256,
            "source_revision_id": self.source_revision_id,
            "source_sha256": self.source_sha256,
            "source_byte_count": self.source_byte_count,
            "selected_stream_index": self.selected_stream_index,
            "stream_count": self.stream_count,
            "timebase": {"num": self.timebase_num, "den": self.timebase_den},
            "pts_ticks": list(self.pts_ticks),
            "dts_ticks": list(self.dts_ticks),
            "declared_vfr": self.declared_vfr,
            "declared_reordering": self.declared_reordering,
        }
        body["evidence_sha256"] = self.evidence_sha256
        return body


@dataclass(frozen=True)
class VerifiedSourceTemporalBindingV2:
    """Schema-v2 measured temporal identity for one verified source snapshot.

    Owner-approved bounded A'-7 decision D-1/D-2: this is an additive receipt.  It
    keeps the whole historical v1 body and seals exactly seven additional measured
    container facts measured from the retained snapshot bytes, including signed
    per-sample composition offsets aligned one-to-one with the decode-order
    enumeration.  Declarations are never measurements: VFR is classified from the
    measured presentation deltas only.
    """

    snapshot_id: str
    snapshot_manifest_sha256: str
    source_revision_id: str
    source_sha256: str
    source_byte_count: int
    selected_stream_index: int
    stream_count: int
    timebase_num: int
    timebase_den: int
    pts_ticks: tuple[int, ...]
    dts_ticks: tuple[int, ...]
    declared_vfr: bool
    declared_reordering: bool
    duration_ts: int
    duration_consistency: str
    tail_duration_ticks: int
    presentation_origin_ticks: int
    stream_handler: str
    stream_identity_derivation: str
    composition_offsets: tuple[int, ...]
    evidence_sha256: str

    def as_evidence(self) -> dict[str, Any]:
        body = {
            "schema_version": 2,
            "snapshot_id": self.snapshot_id,
            "snapshot_manifest_sha256": self.snapshot_manifest_sha256,
            "source_revision_id": self.source_revision_id,
            "source_sha256": self.source_sha256,
            "source_byte_count": self.source_byte_count,
            "selected_stream_index": self.selected_stream_index,
            "stream_count": self.stream_count,
            "timebase": {"num": self.timebase_num, "den": self.timebase_den},
            "pts_ticks": list(self.pts_ticks),
            "dts_ticks": list(self.dts_ticks),
            "declared_vfr": self.declared_vfr,
            "declared_reordering": self.declared_reordering,
            "duration_ts": self.duration_ts,
            "duration_consistency": self.duration_consistency,
            "tail_duration_ticks": self.tail_duration_ticks,
            "presentation_origin_ticks": self.presentation_origin_ticks,
            "stream_handler": self.stream_handler,
            "stream_identity_derivation": self.stream_identity_derivation,
            "composition_offsets": list(self.composition_offsets),
        }
        body["evidence_sha256"] = self.evidence_sha256
        return body


def _error(code: str) -> SourceSnapshotError:
    return SourceSnapshotError(code)


_V1_EVIDENCE_FIELDS = frozenset({
    "schema_version", "snapshot_id", "snapshot_manifest_sha256", "source_revision_id",
    "source_sha256", "source_byte_count", "selected_stream_index", "stream_count",
    "timebase", "pts_ticks", "dts_ticks", "declared_vfr", "declared_reordering",
    "evidence_sha256",
})

# Owner-approved bounded A'-7 decision D-2: exactly seven additional measured
# container facts, and nothing else, extend the v1 body.  The frame-count fact the
# parser also reports stays excluded because it is derivable from the enumeration.
_V2_ADDITIONAL_EVIDENCE_FIELDS = frozenset({
    "duration_ts",
    "duration_consistency",
    "tail_duration_ticks",
    "presentation_origin_ticks",
    "stream_handler",
    "stream_identity_derivation",
    "composition_offsets",
})

_V2_EVIDENCE_FIELDS = _V1_EVIDENCE_FIELDS | _V2_ADDITIONAL_EVIDENCE_FIELDS

_DURATION_CONSISTENCY_STATES = ("MATCH", "MISMATCH")

# D-2: the only stream handler admissible for a timing-bearing video trak.
_VIDEO_STREAM_HANDLER = "vide"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _positive_limit(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise _error(f"{name}_MUST_BE_POSITIVE_FINITE_INTEGER")
    return value


def _digest(value: str) -> bool:
    return (isinstance(value, str) and len(value) == 64
            and all(ch in "0123456789abcdef" for ch in value))


def _validate_iso_bmff_timing_bounds(raw: bytes | bytearray | memoryview) -> None:
    """Reject timing fields that extend past their own ISO-BMFF boxes.

    ``raw`` is the already-materialized snapshot byte view supplied by the caller,
    so validation and timing measurement share one read of the digest-verified
    snapshot instead of materializing it twice.
    """
    containers = {b"moov", b"trak", b"mdia", b"minf", b"stbl", b"edts"}

    def walk(start: int, end: int) -> None:
        pos = start
        while pos < end:
            if end - pos < 8:
                raise _error("SNAPSHOT_TEMPORAL_BOX_BOUNDS_INVALID")
            size, kind = struct.unpack_from(">I4s", raw, pos)
            header = 8
            if size == 1:
                if end - pos < 16:
                    raise _error("SNAPSHOT_TEMPORAL_BOX_BOUNDS_INVALID")
                size = struct.unpack_from(">Q", raw, pos + 8)[0]
                header = 16
            elif size == 0:
                size = end - pos
            if size < header or size > end - pos:
                raise _error("SNAPSHOT_TEMPORAL_BOX_BOUNDS_INVALID")
            box_end = pos + size
            payload = pos + header
            if kind == b"mdhd":
                version = raw[payload] if payload < box_end else -1
                required_size = 32 if version == 0 else 44 if version == 1 else 1 << 63
                if size < required_size:
                    raise struct.error("mdhd timing fields exceed the declared box")
            elif kind in {b"stts", b"elst"}:
                if box_end - payload < 8:
                    raise struct.error(f"{kind.decode('ascii')} header exceeds the declared box")
                version = raw[payload]
                count = struct.unpack_from(">I", raw, payload + 4)[0]
                if kind == b"stts":
                    required_payload = 8 + 8 * count
                elif version == 0:
                    required_payload = 8 + 12 * count
                elif version == 1:
                    required_payload = 8 + 20 * count
                else:
                    raise struct.error("elst version is outside its supported timing layouts")
                if box_end - payload < required_payload:
                    raise struct.error(f"{kind.decode('ascii')} entries exceed the declared box")
            if kind in containers:
                walk(payload, box_end)
            pos = box_end

    walk(0, len(raw))


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise _error("SNAPSHOT_WRITE_FAILED")
        view = view[written:]


def _fsync_dir(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _discard_published_snapshot(directory: Path) -> None:
    """Best-effort removal of a snapshot directory created by this process.

    Only regular files inside a non-symlink directory are unlinked, mirroring the
    staging cleanup path; any unexpected entry is left in place rather than
    followed.
    """
    try:
        info = directory.lstat()
    except OSError:
        return
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
        return
    for child in directory.iterdir():
        if child.is_file() and not child.is_symlink():
            try:
                child.chmod(0o600)
                child.unlink()
            except OSError:
                pass
    try:
        directory.rmdir()
    except OSError:
        pass


def _open_regular_nofollow(path: Path, *, writable: bool = False) -> int:
    flags = (os.O_RDWR if writable else os.O_RDONLY) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise _error("SNAPSHOT_PATH_OPEN_FAILED") from exc
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode):
        os.close(fd)
        raise _error("SNAPSHOT_PATH_NOT_REGULAR_NOFOLLOW")
    return fd


def _digest_fd(fd: int, *, limit: int | None = None) -> tuple[int, str]:
    digest = hashlib.sha256()
    total = 0
    os.lseek(fd, 0, os.SEEK_SET)
    while True:
        block = os.read(fd, 1024 * 1024)
        if not block:
            break
        total += len(block)
        if limit is not None and total > limit:
            raise _error("SOURCE_QUOTA_EXCEEDED")
        digest.update(block)
    return total, digest.hexdigest()


def _read_snapshot_bytes(path: Path, *, limit: int) -> memoryview:
    """Materialize snapshot bytes once through an O_NOFOLLOW descriptor.

    Returns a read-only view so the box-bounds validator and the timing parser
    observe the same single materialization; the read is bounded by ``limit`` so
    an oversized snapshot fails closed like the digest path does.
    """
    fd = _open_regular_nofollow(path)
    try:
        size = os.fstat(fd).st_size
        if size > limit:
            raise _error("SOURCE_QUOTA_EXCEEDED")
        buffer = bytearray(size)
        view = memoryview(buffer)
        total = 0
        while total < size:
            # Bounded read chunks: ``os.read`` returns a ``bytes`` copy, so an
            # unbounded read would transiently hold a second copy of the whole
            # snapshot and defeat the single-copy peak contract.
            chunk = os.read(fd, min(size - total, 1 << 20))
            if not chunk:
                break
            buffer[total : total + len(chunk)] = chunk
            total += len(chunk)
        if total != size:
            raise _error("SNAPSHOT_READ_INCOMPLETE")
        return view.toreadonly()
    finally:
        os.close(fd)


def _owned_private_dir(path: Path, *, create: bool) -> None:
    try:
        path.mkdir(mode=0o700, parents=False, exist_ok=True) if create else None
        info = path.lstat()
    except OSError as exc:
        raise _error("SNAPSHOT_STORE_UNAVAILABLE") from exc
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise _error("SNAPSHOT_STORE_NOT_PRIVATE_DIRECTORY")
    if info.st_uid != os.getuid():
        raise _error("SNAPSHOT_STORE_OWNER_MISMATCH")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise _error("SNAPSHOT_STORE_PERMISSIONS_UNSAFE")


class SourceSnapshotStore:
    """Serialized finite-quota snapshot store with durable successful objects."""

    def __init__(self, root: Path, *, max_source_bytes: int, max_store_bytes: int) -> None:
        self.root = Path(root)
        if not self.root.is_absolute():
            raise _error("SNAPSHOT_ROOT_MUST_BE_ABSOLUTE")
        if self.root.resolve(strict=False) != self.root:
            raise _error("SNAPSHOT_ROOT_PATH_SUBSTITUTED")
        self.max_source_bytes = _positive_limit(max_source_bytes, "MAX_SOURCE_BYTES")
        self.max_store_bytes = _positive_limit(max_store_bytes, "MAX_STORE_BYTES")
        # The configured parent must already exist. This avoids silently
        # creating an unbounded chain outside the service-owned boundary.
        if not self.root.parent.is_dir() or self.root.parent.is_symlink():
            raise _error("SNAPSHOT_ROOT_PARENT_UNAVAILABLE")
        _owned_private_dir(self.root, create=True)
        self.snapshots = self.root / "snapshots"
        self.staging = self.root / "staging"
        _owned_private_dir(self.snapshots, create=True)
        _owned_private_dir(self.staging, create=True)
        self.lock_path = self.root / ".snapshot-store.lock"
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(self.lock_path, flags, 0o600)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise _error("SNAPSHOT_LOCK_NOT_REGULAR")
            os.fchmod(fd, 0o600)
            os.close(fd)
        except OSError as exc:
            raise _error("SNAPSHOT_STORE_LOCK_UNAVAILABLE") from exc
        _fsync_dir(self.root)

    def _lock(self) -> int:
        fd = os.open(self.lock_path, os.O_RDWR | getattr(os, "O_NOFOLLOW", 0))
        fcntl.flock(fd, fcntl.LOCK_EX)
        return fd

    @staticmethod
    def _manifest_bytes(payload: dict[str, Any]) -> bytes:
        body = dict(payload)
        body["manifest_sha256"] = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        return (json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

    def _retained_bytes(self) -> int:
        total = 0
        for parent in (self.snapshots, self.staging):
            for child in parent.iterdir():
                if child.is_symlink() or not child.is_dir():
                    raise _error("SNAPSHOT_STORE_ENTRY_INVALID")
                for item in child.iterdir():
                    if item.is_symlink() or not item.is_file():
                        raise _error("SNAPSHOT_STORE_ENTRY_INVALID")
                    total += item.lstat().st_size
        return total

    def capture(
        self,
        source_path: Path,
        *,
        expected_sha256: str,
        authorization_id: str,
        source_revision_id: str | None = None,
    ) -> VerifiedSourceSnapshot:
        """Capture only after caller has completed preliminary authorization."""
        source = Path(source_path)
        if not source.is_absolute():
            raise _error("SOURCE_PATH_SUBSTITUTED")
        try:
            source_stat = source.lstat()
        except OSError as exc:
            raise _error("SOURCE_PATH_NOT_REGULAR_NOFOLLOW") from exc
        if not stat.S_ISREG(source_stat.st_mode) or stat.S_ISLNK(source_stat.st_mode):
            raise _error("SOURCE_PATH_NOT_REGULAR_NOFOLLOW")
        if source.resolve(strict=True) != source:
            raise _error("SOURCE_PATH_SUBSTITUTED")
        if not _digest(expected_sha256):
            raise _error("AUTHORIZED_SOURCE_DIGEST_INVALID")
        if not isinstance(authorization_id, str) or not authorization_id.strip():
            raise _error("AUTHORIZATION_ID_REQUIRED")
        if source_stat.st_size > self.max_source_bytes:
            raise _error("SOURCE_QUOTA_EXCEEDED")

        lock_fd = self._lock()
        stage_dir = self.staging / uuid.uuid4().hex
        stage_fd = source_fd = out_fd = -1
        published = False
        try:
            retained_before = self._retained_bytes()
            # Reserve bounded room for the manifest as well as captured bytes.
            # This is conservative by design: capacity is never assumed based
            # only on media bytes while omitting replay metadata.
            if retained_before + source_stat.st_size + 4096 > self.max_store_bytes:
                raise _error("STORE_QUOTA_EXCEEDED")
            try:
                stage_dir.mkdir(mode=0o700)
                source_fd = _open_regular_nofollow(source)
                opened = os.fstat(source_fd)
                if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (source_stat.st_dev, source_stat.st_ino):
                    raise _error("SOURCE_PATH_IDENTITY_CHANGED")
                stage_fd = os.open(stage_dir, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
                suffix = source.suffix.lower()
                if suffix and (len(suffix) > 16 or not suffix[1:].isalnum()):
                    suffix = ""
                snapshot_name = f"source{suffix}"
                out_fd = os.open(
                    stage_dir / snapshot_name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                )
                digest = hashlib.sha256()
                count = 0
                while True:
                    block = os.read(source_fd, 1024 * 1024)
                    if not block:
                        break
                    count += len(block)
                    if count > self.max_source_bytes or retained_before + count > self.max_store_bytes:
                        raise _error("SOURCE_QUOTA_EXCEEDED" if count > self.max_source_bytes else "STORE_QUOTA_EXCEEDED")
                    digest.update(block)
                    _write_all(out_fd, block)
                final_source = os.fstat(source_fd)
                if (final_source.st_dev, final_source.st_ino, final_source.st_size) != (opened.st_dev, opened.st_ino, count):
                    raise _error("SOURCE_CHANGED_DURING_CAPTURE")
                if digest.hexdigest() != expected_sha256:
                    raise _error("SOURCE_DIGEST_MISMATCH")
                os.fchmod(out_fd, 0o400)
                os.fsync(out_fd)
                manifest = {
                    "schema_version": 1,
                    "snapshot_id": stage_dir.name,
                    "source_locator": str(source),
                    "source_revision_id": source_revision_id,
                    "authorization_id": authorization_id,
                    "snapshot_sha256": digest.hexdigest(),
                    "source_byte_count": count,
                    "max_source_bytes": self.max_source_bytes,
                    "max_store_bytes": self.max_store_bytes,
                    "retention": "retain_while_evidence_replayable",
                    "threat_model": "protects_against_other_users_and_accidental_changes_not_malicious_same_user_processes",
                }
                manifest_bytes = self._manifest_bytes(manifest)
                if retained_before + count + len(manifest_bytes) > self.max_store_bytes:
                    raise _error("STORE_QUOTA_EXCEEDED")
                manifest_fd = os.open(
                    stage_dir / "manifest.json",
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                )
                try:
                    _write_all(manifest_fd, manifest_bytes)
                    os.fchmod(manifest_fd, 0o400)
                    os.fsync(manifest_fd)
                finally:
                    os.close(manifest_fd)
                _fsync_dir(stage_dir)
                snapshot_dir = self.snapshots / stage_dir.name
                if snapshot_dir.exists() or snapshot_dir.is_symlink():
                    raise _error("SNAPSHOT_ID_COLLISION")
                os.rename(stage_dir, snapshot_dir)
                published = True
                _fsync_dir(self.snapshots)
                result = VerifiedSourceSnapshot(
                    source_locator=str(source),
                    snapshot_path=snapshot_dir / snapshot_name,
                    manifest_path=snapshot_dir / "manifest.json",
                    sha256=digest.hexdigest(),
                    byte_count=count,
                    authorization_id=authorization_id,
                    source_revision_id=source_revision_id,
                    manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                    max_source_bytes=self.max_source_bytes,
                    max_store_bytes=self.max_store_bytes,
                )
                try:
                    self.verify(result)
                    return result
                except BaseException:
                    # A published-but-unverifiable snapshot is not evidence and
                    # must not be retained: it would otherwise count toward the
                    # store quota and be reported as a successful capture.
                    _discard_published_snapshot(snapshot_dir)
                    _fsync_dir(self.snapshots)
                    raise
            except SourceSnapshotError:
                raise
            except OSError as exc:
                raise _error("SOURCE_SNAPSHOT_CAPTURE_FAILED") from exc
        finally:
            for fd in (out_fd, source_fd, stage_fd):
                if fd >= 0:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
            if not published and stage_dir.exists() and not stage_dir.is_symlink():
                # This path is a fresh UUID created by this call only.
                for child in stage_dir.iterdir():
                    if child.is_file() and not child.is_symlink():
                        try:
                            child.chmod(0o600)
                            child.unlink()
                        except OSError:
                            pass
                try:
                    stage_dir.rmdir()
                except OSError:
                    pass
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)

    def verify(self, snapshot: VerifiedSourceSnapshot) -> None:
        """Revalidate snapshot bytes and manifest immediately before consumption."""
        expected_dir = self.snapshots / snapshot.snapshot_path.parent.name
        if snapshot.snapshot_path.parent != expected_dir or snapshot.manifest_path != expected_dir / "manifest.json":
            raise _error("SNAPSHOT_PATH_OUTSIDE_STORE")
        try:
            dstat = expected_dir.lstat()
            if not stat.S_ISDIR(dstat.st_mode) or stat.S_IMODE(dstat.st_mode) & 0o077:
                raise _error("SNAPSHOT_DIRECTORY_PERMISSIONS_UNSAFE")
            source_fd = _open_regular_nofollow(snapshot.snapshot_path)
            manifest_fd = _open_regular_nofollow(snapshot.manifest_path)
            try:
                source_stat = os.fstat(source_fd)
                manifest_stat = os.fstat(manifest_fd)
                if stat.S_IMODE(source_stat.st_mode) != 0o400 or stat.S_IMODE(manifest_stat.st_mode) != 0o400:
                    raise _error("SNAPSHOT_FILE_PERMISSIONS_UNSAFE")
                source_count, digest = _digest_fd(source_fd, limit=self.max_source_bytes)
                manifest_count, manifest_file_digest = _digest_fd(manifest_fd, limit=1024 * 1024)
                if manifest_count > 1024 * 1024:
                    raise _error("SNAPSHOT_MANIFEST_TOO_LARGE")
                os.lseek(manifest_fd, 0, os.SEEK_SET)
                manifest_data = os.read(manifest_fd, manifest_count + 1)
            finally:
                os.close(source_fd)
                os.close(manifest_fd)
            manifest = json.loads(manifest_data)
        except SourceSnapshotError:
            raise
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise _error("SNAPSHOT_EVIDENCE_UNREADABLE") from exc
        if digest != snapshot.sha256 or source_count != snapshot.byte_count:
            raise _error("SNAPSHOT_DIGEST_MISMATCH")
        if manifest_file_digest != snapshot.manifest_sha256:
            raise _error("SNAPSHOT_MANIFEST_DIGEST_MISMATCH")
        if (not isinstance(manifest, dict) or manifest.get("snapshot_sha256") != digest
                or type(manifest.get("schema_version")) is not int
                or manifest.get("schema_version") != 1
                or manifest.get("retention") != "retain_while_evidence_replayable"
                or any(type(manifest.get(key)) is not int for key in (
                    "source_byte_count", "max_source_bytes", "max_store_bytes"))
                or manifest.get("source_byte_count") != source_count
                or manifest.get("source_locator") != snapshot.source_locator
                or manifest.get("authorization_id") != snapshot.authorization_id
                or manifest.get("source_revision_id") != snapshot.source_revision_id
                or manifest.get("max_source_bytes") != snapshot.max_source_bytes
                or manifest.get("max_store_bytes") != snapshot.max_store_bytes
                or manifest.get("snapshot_id") != expected_dir.name):
            raise _error("SNAPSHOT_MANIFEST_MISMATCH")
        supplied_manifest_digest = manifest.pop("manifest_sha256", None)
        calculated = hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        if supplied_manifest_digest != calculated:
            raise _error("SNAPSHOT_MANIFEST_DIGEST_MISMATCH")

    def load_verified_snapshot(self, snapshot_id: str) -> VerifiedSourceSnapshot:
        """Load and revalidate one existing snapshot without capturing another copy."""
        if not isinstance(snapshot_id, str) or re.fullmatch(r"[0-9a-f]{32}", snapshot_id) is None:
            raise _error("SNAPSHOT_ID_INVALID")
        snapshot_dir = self.snapshots / snapshot_id
        _owned_private_dir(snapshot_dir, create=False)
        manifest_path = snapshot_dir / "manifest.json"
        try:
            manifest_fd = _open_regular_nofollow(manifest_path)
            try:
                manifest_count, manifest_sha256 = _digest_fd(manifest_fd, limit=1024 * 1024)
                if manifest_count > 1024 * 1024:
                    raise _error("SNAPSHOT_MANIFEST_TOO_LARGE")
                os.lseek(manifest_fd, 0, os.SEEK_SET)
                manifest_bytes = os.read(manifest_fd, manifest_count + 1)
            finally:
                os.close(manifest_fd)
            manifest = json.loads(manifest_bytes)
            entries = list(snapshot_dir.iterdir())
        except SourceSnapshotError:
            raise
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise _error("SNAPSHOT_EVIDENCE_UNREADABLE") from exc

        required = {
            "schema_version", "snapshot_id", "source_locator", "source_revision_id",
            "authorization_id", "snapshot_sha256", "source_byte_count",
            "max_source_bytes", "max_store_bytes", "retention", "threat_model",
            "manifest_sha256",
        }
        if (not isinstance(manifest, dict) or set(manifest) != required
                or type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1
                or manifest.get("snapshot_id") != snapshot_id
                or manifest.get("retention") != "retain_while_evidence_replayable"
                or manifest.get("threat_model") != "protects_against_other_users_and_accidental_changes_not_malicious_same_user_processes"
                or not isinstance(manifest.get("source_locator"), str)
                or not Path(manifest["source_locator"]).is_absolute()
                or not isinstance(manifest.get("authorization_id"), str)
                or not manifest["authorization_id"].strip()
                or (manifest.get("source_revision_id") is not None
                    and (not isinstance(manifest.get("source_revision_id"), str)
                         or not manifest["source_revision_id"].strip()))
                or not _digest(manifest.get("snapshot_sha256"))
                or type(manifest.get("source_byte_count")) is not int
                or manifest["source_byte_count"] < 0
                or type(manifest.get("max_source_bytes")) is not int
                or manifest["max_source_bytes"] <= 0
                or type(manifest.get("max_store_bytes")) is not int
                or manifest["max_store_bytes"] <= 0
                or not _digest(manifest.get("manifest_sha256"))):
            raise _error("SNAPSHOT_MANIFEST_MISMATCH")
        if (manifest["source_byte_count"] > self.max_source_bytes
                or manifest["max_source_bytes"] > self.max_source_bytes
                or manifest["max_store_bytes"] > self.max_store_bytes
                or self._retained_bytes() > self.max_store_bytes):
            raise _error("SOURCE_QUOTA_EXCEEDED" if manifest["source_byte_count"] > self.max_source_bytes
                         or manifest["max_source_bytes"] > self.max_source_bytes
                         else "STORE_QUOTA_EXCEEDED")
        source_files = [item for item in entries if item.name != "manifest.json"]
        if (len(source_files) != 1 or not source_files[0].name.startswith("source")
                or source_files[0].is_symlink() or not source_files[0].is_file()):
            raise _error("SNAPSHOT_ENTRY_INVALID")
        snapshot = VerifiedSourceSnapshot(
            source_locator=manifest["source_locator"],
            snapshot_path=source_files[0], manifest_path=manifest_path,
            sha256=manifest["snapshot_sha256"], byte_count=manifest["source_byte_count"],
            authorization_id=manifest["authorization_id"],
            source_revision_id=manifest["source_revision_id"],
            manifest_sha256=manifest_sha256,
            max_source_bytes=manifest["max_source_bytes"],
            max_store_bytes=manifest["max_store_bytes"],
        )
        self.verify(snapshot)
        return snapshot

    def bind_temporal_authority(
        self,
        snapshot: VerifiedSourceSnapshot,
        *,
        selected_stream_index: int,
        declared_vfr: bool,
        declared_reordering: bool,
    ) -> VerifiedSourceTemporalBinding:
        """Measure exact temporal identity from the snapshot bytes and bind declarations.

        Timing facts are recomputed from the retained snapshot. Caller-supplied PTS or
        stream metadata is never accepted as the measurement basis.

        A-9 strict V1: a nonzero ``elst`` media time (presentation origin) is
        refused as ``EDIT_LIST_ORIGIN_NOT_APPLIED``; it is never normalized.
        """
        self.verify(snapshot)
        if (type(selected_stream_index) is not int or selected_stream_index < 0
                or type(declared_vfr) is not bool
                or type(declared_reordering) is not bool
                or type(snapshot.source_revision_id) is not str
                or not snapshot.source_revision_id.strip()):
            raise _error("SNAPSHOT_TEMPORAL_DECLARATION_INVALID")
        try:
            from gate3.container import parse_iso_bmff_timing_bytes

            raw = _read_snapshot_bytes(
                snapshot.snapshot_path, limit=snapshot.max_source_bytes,
            )
            _validate_iso_bmff_timing_bounds(raw)
            measured = parse_iso_bmff_timing_bytes(
                raw, selected_stream_index=selected_stream_index,
            )
        except (OSError, ValueError, struct.error) as exc:
            raise _error("SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED") from exc
        if measured.get("source_bytes_sha256") != snapshot.sha256:
            raise _error("SNAPSHOT_TEMPORAL_DIGEST_MISMATCH")
        if measured.get("stream_index") != selected_stream_index:
            raise _error("SNAPSHOT_TEMPORAL_STREAM_MISMATCH")
        pts = measured.get("pts_ticks")
        dts = measured.get("dts_ticks")
        timescale = measured.get("media_timescale")
        stream_count = measured.get("stream_count")
        tail = measured.get("tail_duration_ticks")
        origin = measured.get("presentation_origin_ticks")
        if (not isinstance(pts, tuple) or not pts
                or any(type(tick) is not int for tick in pts)
                or not isinstance(dts, tuple) or len(dts) != len(pts)
                or any(type(tick) is not int for tick in dts)
                or type(timescale) is not int or timescale <= 0
                or type(stream_count) is not int or stream_count <= 0
                or selected_stream_index >= stream_count
                or type(tail) is not int or tail <= 0
                or type(origin) is not int):
            raise _error("SNAPSHOT_TEMPORAL_FACTS_INVALID")
        if origin != 0:
            raise _error("EDIT_LIST_ORIGIN_NOT_APPLIED")
        if any(later <= earlier for earlier, later in zip(dts, dts[1:])):
            raise _error("SNAPSHOT_DECODE_TIMESTAMPS_INVALID")
        durations = tuple(b - a for a, b in zip(dts, dts[1:])) + (tail,)
        observed_vfr = len(set(durations)) > 1
        observed_reordering = pts != dts
        if declared_vfr != observed_vfr:
            raise _error("SNAPSHOT_VFR_DECLARATION_MISMATCH")
        if declared_reordering != observed_reordering:
            raise _error("SNAPSHOT_REORDERING_DECLARATION_MISMATCH")
        self.verify(snapshot)
        body = {
            "schema_version": 1,
            "snapshot_id": snapshot.snapshot_path.parent.name,
            "snapshot_manifest_sha256": snapshot.manifest_sha256,
            "source_revision_id": snapshot.source_revision_id,
            "source_sha256": snapshot.sha256,
            "source_byte_count": snapshot.byte_count,
            "selected_stream_index": selected_stream_index,
            "stream_count": stream_count,
            "timebase": {"num": 1, "den": timescale},
            "pts_ticks": list(pts),
            "dts_ticks": list(dts),
            "declared_vfr": declared_vfr,
            "declared_reordering": declared_reordering,
        }
        evidence_sha256 = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        return VerifiedSourceTemporalBinding(
            snapshot_id=body["snapshot_id"],
            snapshot_manifest_sha256=snapshot.manifest_sha256,
            source_revision_id=snapshot.source_revision_id,
            source_sha256=snapshot.sha256,
            source_byte_count=snapshot.byte_count,
            selected_stream_index=selected_stream_index,
            stream_count=body["stream_count"],
            timebase_num=1,
            timebase_den=timescale,
            pts_ticks=pts,
            dts_ticks=dts,
            declared_vfr=declared_vfr,
            declared_reordering=declared_reordering,
            evidence_sha256=evidence_sha256,
        )

    def bind_temporal_authority_v2(
        self,
        snapshot: VerifiedSourceSnapshot,
        *,
        selected_stream_index: int,
        declared_vfr: bool,
        declared_reordering: bool,
    ) -> VerifiedSourceTemporalBindingV2:
        """Measure and bind schema-v2 temporal authority from the retained snapshot.

        Owner-approved bounded A'-7: this additive entry point keeps the exact v1
        call contract and measures every temporal fact itself.  No caller-supplied
        position, duration, composition, or stream metadata is accepted, and the
        retained bytes are digest-verified before and after measurement.

        A-9 strict V1 still holds: a nonzero edit-list presentation origin is
        refused as ``EDIT_LIST_ORIGIN_NOT_APPLIED`` and is never normalized.

        VFR is classified from the measured presentation deltas only.  The
        duration/presentation disagreement is sealed as a measured fact; deciding
        it is the separately authorized A-12 policy and is not implemented here.
        """
        self.verify(snapshot)
        if (type(selected_stream_index) is not int or selected_stream_index < 0
                or type(declared_vfr) is not bool
                or type(declared_reordering) is not bool
                or type(snapshot.source_revision_id) is not str
                or not snapshot.source_revision_id.strip()):
            raise _error("SNAPSHOT_TEMPORAL_DECLARATION_INVALID")
        try:
            from gate3.container import parse_iso_bmff_timing_bytes

            raw = _read_snapshot_bytes(
                snapshot.snapshot_path, limit=snapshot.max_source_bytes,
            )
            _validate_iso_bmff_timing_bounds(raw)
            measured = parse_iso_bmff_timing_bytes(
                raw, selected_stream_index=selected_stream_index,
            )
        except (OSError, ValueError, struct.error) as exc:
            raise _error("SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED") from exc
        if measured.get("source_bytes_sha256") != snapshot.sha256:
            raise _error("SNAPSHOT_TEMPORAL_DIGEST_MISMATCH")
        if measured.get("stream_index") != selected_stream_index:
            raise _error("SNAPSHOT_TEMPORAL_STREAM_MISMATCH")
        pts = measured.get("pts_ticks")
        dts = measured.get("dts_ticks")
        timescale = measured.get("media_timescale")
        stream_count = measured.get("stream_count")
        tail = measured.get("tail_duration_ticks")
        origin = measured.get("presentation_origin_ticks")
        duration = measured.get("duration_ts")
        consistency = measured.get("duration_consistency")
        handler = measured.get("stream_handler")
        identity = measured.get("stream_identity_derivation")
        offsets = measured.get("composition_offsets")
        if (not isinstance(pts, tuple) or not pts
                or any(type(tick) is not int for tick in pts)
                or not isinstance(dts, tuple) or len(dts) != len(pts)
                or any(type(tick) is not int for tick in dts)
                or type(timescale) is not int or timescale <= 0
                or type(stream_count) is not int or stream_count <= 0
                or selected_stream_index >= stream_count
                or type(tail) is not int or tail <= 0
                or type(origin) is not int
                or type(duration) is not int or duration < 0
                or type(consistency) is not str
                or consistency not in _DURATION_CONSISTENCY_STATES
                or handler != _VIDEO_STREAM_HANDLER
                or not isinstance(identity, str) or not identity.strip()
                or not isinstance(offsets, tuple) or len(offsets) != len(dts)
                or any(type(offset) is not int for offset in offsets)):
            raise _error("SNAPSHOT_TEMPORAL_FACTS_INVALID")
        # The consistency label is a derived comparison, never an independent
        # observation: it must agree with the measured duration and presentation span.
        expected_consistency = "MATCH" if duration == pts[-1] + tail else "MISMATCH"
        if consistency != expected_consistency:
            raise _error("SNAPSHOT_TEMPORAL_FACTS_INVALID")
        # Signed composition is exact in decode order and preserves duplicate
        # presentation ticks; no set, dedupe, or nominal-rate reconstruction.
        composed = tuple(sorted(tick + offset for tick, offset in zip(dts, offsets)))
        if composed != pts:
            raise _error("SNAPSHOT_TEMPORAL_FACTS_INVALID")
        if origin != 0:
            raise _error("EDIT_LIST_ORIGIN_NOT_APPLIED")
        if any(later <= earlier for earlier, later in zip(dts, dts[1:])):
            raise _error("SNAPSHOT_DECODE_TIMESTAMPS_INVALID")
        presentation_deltas = tuple(later - earlier for earlier, later in zip(pts, pts[1:]))
        observed_vfr = len(set(presentation_deltas)) > 1
        observed_reordering = pts != dts
        if declared_vfr != observed_vfr:
            raise _error("SNAPSHOT_VFR_DECLARATION_MISMATCH")
        if declared_reordering != observed_reordering:
            raise _error("SNAPSHOT_REORDERING_DECLARATION_MISMATCH")
        self.verify(snapshot)
        body = {
            "schema_version": 2,
            "snapshot_id": snapshot.snapshot_path.parent.name,
            "snapshot_manifest_sha256": snapshot.manifest_sha256,
            "source_revision_id": snapshot.source_revision_id,
            "source_sha256": snapshot.sha256,
            "source_byte_count": snapshot.byte_count,
            "selected_stream_index": selected_stream_index,
            "stream_count": stream_count,
            "timebase": {"num": 1, "den": timescale},
            "pts_ticks": list(pts),
            "dts_ticks": list(dts),
            "declared_vfr": declared_vfr,
            "declared_reordering": declared_reordering,
            "duration_ts": duration,
            "duration_consistency": consistency,
            "tail_duration_ticks": tail,
            "presentation_origin_ticks": origin,
            "stream_handler": handler,
            "stream_identity_derivation": identity,
            "composition_offsets": list(offsets),
        }
        evidence_sha256 = hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()
        return VerifiedSourceTemporalBindingV2(
            snapshot_id=body["snapshot_id"],
            snapshot_manifest_sha256=snapshot.manifest_sha256,
            source_revision_id=snapshot.source_revision_id,
            source_sha256=snapshot.sha256,
            source_byte_count=snapshot.byte_count,
            selected_stream_index=selected_stream_index,
            stream_count=stream_count,
            timebase_num=1,
            timebase_den=timescale,
            pts_ticks=pts,
            dts_ticks=dts,
            declared_vfr=declared_vfr,
            declared_reordering=declared_reordering,
            duration_ts=duration,
            duration_consistency=consistency,
            tail_duration_ticks=tail,
            presentation_origin_ticks=origin,
            stream_handler=handler,
            stream_identity_derivation=identity,
            composition_offsets=offsets,
            evidence_sha256=evidence_sha256,
        )

    def verify_temporal_authority(
        self, snapshot: VerifiedSourceSnapshot, evidence: Any,
    ) -> VerifiedSourceTemporalBinding | VerifiedSourceTemporalBindingV2:
        """Recompute and compare a temporal binding before a consumer uses it.

        Owner-approved bounded A'-7 D-3: the receipt's version pins the measurement
        and the closed field set.  Versions are dispatched *before* any
        version-specific field gate, so a v1 receipt relabelled as v2 can never be
        silently upgraded, and a v2 receipt can never be downgraded to v1.
        """
        if not isinstance(evidence, dict) or "schema_version" not in evidence:
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID")
        version = evidence["schema_version"]
        if type(version) is not int:
            # Historical type-layer refusal is preserved for a malformed version label.
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_TYPES_INVALID")
        if version == 1:
            binding = self._verify_temporal_evidence_v1(snapshot, evidence)
        elif version == 2:
            if set(evidence) == _V1_EVIDENCE_FIELDS:
                # A v1 receipt with only its version label changed is not v2 evidence.
                raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH")
            binding = self._verify_temporal_evidence_v2(snapshot, evidence)
        else:
            if set(evidence) == _V1_EVIDENCE_FIELDS:
                raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH")
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID")
        if _canonical_json(binding.as_evidence()) != _canonical_json(evidence):
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH")
        return binding

    def _verify_temporal_evidence_v1(
        self, snapshot: VerifiedSourceSnapshot, evidence: dict[str, Any],
    ) -> VerifiedSourceTemporalBinding:
        """Schema-v1 field/type/declaration gates plus a v1 re-measurement."""
        if set(evidence) != _V1_EVIDENCE_FIELDS:
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID")
        if (type(evidence.get("schema_version")) is not int
                or type(evidence.get("selected_stream_index")) is not int
                or type(evidence.get("stream_count")) is not int
                or type(evidence.get("source_byte_count")) is not int
                or not isinstance(evidence.get("timebase"), dict)
                or set(evidence["timebase"]) != {"num", "den"}
                or any(type(value) is not int for value in evidence["timebase"].values())
                or not isinstance(evidence.get("pts_ticks"), list)
                or not isinstance(evidence.get("dts_ticks"), list)
                or any(type(value) is not int for value in evidence["pts_ticks"] + evidence["dts_ticks"])
                or not _digest(evidence.get("evidence_sha256"))):
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_TYPES_INVALID")
        if type(evidence.get("declared_vfr")) is not bool or type(evidence.get("declared_reordering")) is not bool:
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_DECLARATION_INVALID")
        return self.bind_temporal_authority(
            snapshot,
            selected_stream_index=evidence.get("selected_stream_index"),
            declared_vfr=evidence["declared_vfr"],
            declared_reordering=evidence["declared_reordering"],
        )

    def _verify_temporal_evidence_v2(
        self, snapshot: VerifiedSourceSnapshot, evidence: dict[str, Any],
    ) -> VerifiedSourceTemporalBindingV2:
        """Schema-v2 closed field/type/declaration gates plus a v2 re-measurement."""
        if set(evidence) != _V2_EVIDENCE_FIELDS:
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID")
        pts = evidence.get("pts_ticks")
        dts = evidence.get("dts_ticks")
        offsets = evidence.get("composition_offsets")
        timebase = evidence.get("timebase")
        if (type(evidence.get("selected_stream_index")) is not int
                or type(evidence.get("stream_count")) is not int
                or type(evidence.get("source_byte_count")) is not int
                or not isinstance(timebase, dict)
                or set(timebase) != {"num", "den"}
                or any(type(value) is not int for value in timebase.values())
                or not isinstance(pts, list)
                or not isinstance(dts, list)
                or not isinstance(offsets, list)
                or any(type(value) is not int for value in (*pts, *dts, *offsets))
                or type(evidence.get("duration_ts")) is not int
                or type(evidence.get("duration_consistency")) is not str
                or type(evidence.get("tail_duration_ticks")) is not int
                or type(evidence.get("presentation_origin_ticks")) is not int
                or not isinstance(evidence.get("stream_handler"), str)
                or not isinstance(evidence.get("stream_identity_derivation"), str)
                or not _digest(evidence.get("evidence_sha256"))):
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_TYPES_INVALID")
        if type(evidence.get("declared_vfr")) is not bool or type(evidence.get("declared_reordering")) is not bool:
            raise _error("SNAPSHOT_TEMPORAL_EVIDENCE_DECLARATION_INVALID")
        return self.bind_temporal_authority_v2(
            snapshot,
            selected_stream_index=evidence.get("selected_stream_index"),
            declared_vfr=evidence["declared_vfr"],
            declared_reordering=evidence["declared_reordering"],
        )


def verify_snapshot_evidence(evidence: Any) -> None:
    """Verify a persisted snapshot evidence projection without changing state."""
    if not isinstance(evidence, dict):
        raise SourceSnapshotError("SNAPSHOT_EVIDENCE_INVALID")
    required = {
        "snapshot_id", "snapshot_path", "manifest_path", "snapshot_sha256",
        "source_byte_count", "source_locator", "authorization_id", "source_revision_id",
        "snapshot_manifest_sha256", "max_source_bytes", "max_store_bytes",
    }
    if set(evidence) != required:
        raise SourceSnapshotError("SNAPSHOT_EVIDENCE_FIELDS_INVALID")
    if (not _digest(evidence["snapshot_sha256"])
            or not _digest(evidence["snapshot_manifest_sha256"])
            or type(evidence["source_byte_count"]) is not int
            or type(evidence["max_source_bytes"]) is not int
            or type(evidence["max_store_bytes"]) is not int
            or evidence["source_byte_count"] < 0
            or evidence["max_source_bytes"] <= 0
            or evidence["max_store_bytes"] <= 0
            or evidence["source_byte_count"] > evidence["max_source_bytes"]
            or evidence["source_byte_count"] > evidence["max_store_bytes"]):
        raise SourceSnapshotError("SNAPSHOT_EVIDENCE_LIMIT_OR_DIGEST_INVALID")
    snapshot_path = Path(evidence["snapshot_path"])
    manifest_path = Path(evidence["manifest_path"])
    snapshot_dir = snapshot_path.parent
    if (not snapshot_path.is_absolute() or not manifest_path.is_absolute()
            or snapshot_dir.name != evidence["snapshot_id"]
            or snapshot_dir.parent.name != "snapshots"
            or manifest_path != snapshot_dir / "manifest.json"):
        raise SourceSnapshotError("SNAPSHOT_PATH_BINDING_INVALID")
    # Enforce the private path components without following symlinks.
    for directory in (snapshot_dir.parent.parent, snapshot_dir.parent, snapshot_dir):
        info = directory.lstat()
        if (not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o700
                or info.st_uid != os.getuid()):
            raise SourceSnapshotError("SNAPSHOT_DIRECTORY_PERMISSIONS_UNSAFE")
    store_root = snapshot_dir.parent.parent
    if store_root.is_symlink() or store_root.parent.is_symlink():
        raise SourceSnapshotError("SNAPSHOT_STORE_PATH_SUBSTITUTED")
    source_fd = _open_regular_nofollow(snapshot_path)
    manifest_fd = _open_regular_nofollow(manifest_path)
    try:
        source_count, source_digest = _digest_fd(source_fd, limit=evidence["max_source_bytes"])
        manifest_count, manifest_digest = _digest_fd(manifest_fd, limit=1024 * 1024)
        os.lseek(manifest_fd, 0, os.SEEK_SET)
        manifest_raw = os.read(manifest_fd, manifest_count + 1)
        if stat.S_IMODE(os.fstat(source_fd).st_mode) != 0o400 or stat.S_IMODE(os.fstat(manifest_fd).st_mode) != 0o400:
            raise SourceSnapshotError("SNAPSHOT_FILE_PERMISSIONS_UNSAFE")
    finally:
        os.close(source_fd)
        os.close(manifest_fd)
    if source_count != evidence["source_byte_count"] or source_digest != evidence["snapshot_sha256"]:
        raise SourceSnapshotError("SNAPSHOT_DIGEST_MISMATCH")
    if manifest_digest != evidence["snapshot_manifest_sha256"]:
        raise SourceSnapshotError("SNAPSHOT_MANIFEST_DIGEST_MISMATCH")
    try:
        manifest = json.loads(manifest_raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SourceSnapshotError("SNAPSHOT_MANIFEST_UNREADABLE") from exc
    if (type(manifest.get("schema_version")) is not int
            or manifest.get("schema_version") != 1
            or manifest.get("retention") != "retain_while_evidence_replayable"
            or any(type(manifest.get(key)) is not int for key in (
                "source_byte_count", "max_source_bytes", "max_store_bytes"))
            or manifest.get("snapshot_sha256") != source_digest
            or manifest.get("source_byte_count") != source_count
            or manifest.get("source_locator") != evidence["source_locator"]
            or manifest.get("source_revision_id") != evidence["source_revision_id"]
            or manifest.get("authorization_id") != evidence["authorization_id"]
            or manifest.get("max_source_bytes") != evidence["max_source_bytes"]
            or manifest.get("max_store_bytes") != evidence["max_store_bytes"]
            or manifest.get("snapshot_id") != evidence["snapshot_id"]):
        raise SourceSnapshotError("SNAPSHOT_MANIFEST_BINDING_MISMATCH")
    supplied = manifest.pop("manifest_sha256", None)
    expected = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    if supplied != expected:
        raise SourceSnapshotError("SNAPSHOT_MANIFEST_CONTENT_DIGEST_MISMATCH")
