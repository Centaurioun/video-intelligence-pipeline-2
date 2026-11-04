"""Quota-bounded, no-follow source access for locally generated media.

Gate-0 Task 6 replaces unrestricted ``Path.read_bytes()`` on a declared media
source with a *bounded handle*:

* every path component below an accepted root is opened with ``O_NOFOLLOW`` so
  a symlink cannot redirect the read outside that root;
* the opened descriptor must be a regular file with a single link (a hardlink
  alias would let the same bytes be edited through a path the corpus never
  declared);
* the configured byte quota is enforced from ``fstat`` *before* reading and
  again while the file is streamed through SHA-256, so an oversized (or
  growing) file is refused instead of being fully materialised;
* the descriptor identity (device/inode/size/mtime) recorded before the read
  must still match after it, and a later :func:`verify_source` call re-opens
  the same locator and refuses if the identity or digest changed while the
  measurement tool ran.

Limits of this envelope: it resists path/link/quota/digest/inode tampering and
detects changes around a measurement.  It is *not* a hostile-media parser and
makes no claim about malicious bitstreams.
"""

from __future__ import annotations

from dataclasses import dataclass
import errno
import hashlib
import os
import stat
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

__all__ = [
    "DEFAULT_MAX_SOURCE_BYTES",
    "FIXTURE_MANIFEST_GENERATOR_MODULE",
    "FIXTURE_MANIFEST_FILE",
    "FIXTURE_MANIFEST_SCHEMA_VERSION",
    "READ_CHUNK_BYTES",
    "SourceGuardError",
    "SourceIdentity",
    "SourceSnapshot",
    "snapshot_path",
    "snapshot_source",
    "read_path_bytes",
    "verify_path",
    "verify_source",
]

#: Default per-source byte quota (256 MiB).  Small generated fixtures are far
#: below this; the cap exists so a declared locator cannot force an unbounded
#: read.  Callers may lower it explicitly (e.g. the tests use 1 KiB).
DEFAULT_MAX_SOURCE_BYTES = 256 * 1024 * 1024

#: Streamed read chunk.  The file is hashed as it is read; it is never mutated.
READ_CHUNK_BYTES = 1024 * 1024

#: Generated-fixture provenance sidecar written next to generated media.
FIXTURE_MANIFEST_FILE = ".gate0-generated-fixture-manifest.json"
FIXTURE_MANIFEST_SCHEMA_VERSION = "gate0.generated-media-fixture-manifest.v1"

#: The fixture generator this repository ships.  Recorded in the manifest for
#: auditability only; a declared module name never grants trust by itself.
FIXTURE_MANIFEST_GENERATOR_MODULE = "tests/gate0/media/generated_media.py"

_O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_SYMLINK_ERRNOS = {errno.ELOOP}
if hasattr(errno, "EMLINK"):  # pragma: no cover - platform-specific spelling
    _SYMLINK_ERRNOS.add(errno.EMLINK)


class SourceGuardError(ValueError):
    """A fail-closed source-integrity refusal with a stable reason code."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else f"{reason}: {detail}")


@dataclass(frozen=True)
class SourceIdentity:
    """Filesystem identity bound across one measurement."""

    device: int
    inode: int
    size: int
    mode: int
    mtime_ns: int


@dataclass(frozen=True)
class SourceSnapshot:
    """Digest-bound snapshot of a regular, quota-bounded source file."""

    path: str
    relative_locator: str | None
    byte_count: int
    digest: str
    identity: SourceIdentity


# ---------------------------------------------------------------------------
# path handling
# ---------------------------------------------------------------------------
def _resolved_root(root: Path) -> Path:
    root = Path(root)
    root = root.resolve()
    if not root.is_dir():
        raise SourceGuardError("SOURCE_ROOT_UNREADABLE", f"input root is not a directory: {root}")
    return root


def _locator_parts(locator: str) -> tuple[str, ...]:
    if not isinstance(locator, str) or not locator.strip():
        raise SourceGuardError("MEDIA_CORPUS_INVALID", "locator is not a non-empty string")
    if "\x00" in locator:
        raise SourceGuardError("MEDIA_CORPUS_INVALID", "locator contains a NUL byte")
    path = PurePosixPath(locator)
    if path.is_absolute():
        raise SourceGuardError("MEDIA_CORPUS_INVALID", f"locator must be relative: {locator!r}")
    parts = path.parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise SourceGuardError(
            "MEDIA_CORPUS_INVALID", f"locator is not a plain relative file path: {locator!r}"
        )
    return parts


def _open_regular_beneath(root: Path, parts: Sequence[str], display: str) -> int:
    """Open ``root/parts`` component-by-component with ``O_NOFOLLOW``."""
    descriptor = os.open(str(root), os.O_RDONLY | _O_DIRECTORY | _O_CLOEXEC)
    try:
        for name in parts[:-1]:
            # ``lstat`` with ``dir_fd`` reports a symlinked *intermediate*
            # component as a symlink explicitly; ``O_NOFOLLOW`` on a directory
            # symlink surfaces as ENOTDIR on some platforms, which would
            # otherwise be conflated with "file used as a directory".
            try:
                info = os.lstat(name, dir_fd=descriptor)
            except OSError as exc:
                raise _path_error(exc, display) from exc
            if stat.S_ISLNK(info.st_mode):
                raise SourceGuardError(
                    "SOURCE_SYMLINK", f"path component is a symlink: {display}"
                )
            try:
                child = os.open(
                    name,
                    os.O_RDONLY | _O_DIRECTORY | _O_NOFOLLOW | _O_CLOEXEC,
                    dir_fd=descriptor,
                )
            except OSError as exc:
                raise _path_error(exc, display) from exc
            os.close(descriptor)
            descriptor = child
        try:
            leaf = os.open(
                parts[-1],
                os.O_RDONLY | _O_NOFOLLOW | _O_CLOEXEC,
                dir_fd=descriptor,
            )
        except OSError as exc:
            raise _path_error(exc, display) from exc
    finally:
        os.close(descriptor)
    return leaf


def _absolute_leaf_parts(path: str | Path) -> tuple[tuple[str, ...], Path]:
    """Split an absolute path into protected parent components plus the leaf name.

    Only the *directory* part is resolved: the leaf itself is never resolved,
    because ``Path.resolve()`` follows a leaf symlink and would defeat the
    no-follow guarantee for the absolute-path entry points (independent review
    F5, 2026-10-25).  The leaf is opened with ``O_NOFOLLOW`` below.
    """
    text = os.fspath(path)
    if "\x00" in text:
        raise SourceGuardError("SOURCE_UNREADABLE", "source path contains a NUL byte")
    raw = Path(text)
    if not raw.is_absolute():
        raise SourceGuardError("SOURCE_UNREADABLE", f"source path is not absolute: {text!r}")
    name = raw.name
    if name in {"", ".", ".."}:
        raise SourceGuardError("SOURCE_UNREADABLE", f"source path has no file name: {text!r}")
    try:
        parent = raw.parent.resolve()
    except (OSError, ValueError) as exc:
        raise SourceGuardError("SOURCE_UNREADABLE", f"cannot resolve source parent: {text!r}") from exc
    if not parent.is_dir():
        raise SourceGuardError("SOURCE_ROOT_UNREADABLE", f"source parent is not a directory: {text!r}")
    return parent.parts[1:] + (name,), raw


def read_path_bytes(path: str | Path, *, max_bytes: int = DEFAULT_MAX_SOURCE_BYTES) -> bytes:
    """Read one absolute file through the same bounded, no-follow handle.

    Used for small metadata (e.g. the fixture manifest); never for media
    payloads that can be streamed instead.
    """
    parts, raw = _absolute_leaf_parts(path)
    descriptor = _open_regular_beneath(Path(os.sep), parts, str(raw))
    try:
        _, _, _, payload = _read_descriptor(
            descriptor, str(raw), max_bytes=max_bytes, keep_bytes=True
        )
    finally:
        os.close(descriptor)
    assert payload is not None
    return payload


def fixture_manifest_digest(document: Mapping[str, Any]) -> str:
    """Canonical digest of the manifest body (self-describing, tamper-evident).

    This is an integrity check of the sidecar body, not an authenticity proof:
    a writer who controls the whole input root can rewrite both the body and
    this digest.  Trust is granted only by matching the declared source bytes
    against the digest set, never by the declared generator name.
    """
    from gate0.identity import digest_json

    material = {key: document.get(key) for key in ("schema_version", "generation", "fixtures")}
    return digest_json(material)


def _path_error(exc: OSError, display: str) -> SourceGuardError:
    if exc.errno in _SYMLINK_ERRNOS:
        return SourceGuardError("SOURCE_SYMLINK", f"symlink traversal is not allowed: {display}")
    if exc.errno in (errno.ENOENT, errno.EACCES, errno.EPERM):
        return SourceGuardError("SOURCE_UNREADABLE", f"cannot read {display}: {exc.strerror}")
    if exc.errno in (errno.ENOTDIR, errno.EISDIR):
        return SourceGuardError("SOURCE_NOT_REGULAR", f"not a regular file: {display}")
    return SourceGuardError("SOURCE_UNREADABLE", f"cannot open {display}: {exc.strerror}")


def _identity(value: os.stat_result) -> SourceIdentity:
    return SourceIdentity(
        device=value.st_dev,
        inode=value.st_ino,
        size=value.st_size,
        mode=stat.S_IMODE(value.st_mode),
        mtime_ns=value.st_mtime_ns,
    )


def _read_descriptor(
    descriptor: int, display: str, *, max_bytes: int, keep_bytes: bool = False
) -> tuple[int, str, SourceIdentity, bytes | None]:
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
        raise ValueError("max_bytes must be a positive integer")
    before = os.fstat(descriptor)
    if not stat.S_ISREG(before.st_mode):
        raise SourceGuardError("SOURCE_NOT_REGULAR", f"not a regular file: {display}")
    if before.st_nlink != 1:
        raise SourceGuardError(
            "SOURCE_HARDLINK",
            f"source has {before.st_nlink} hard links; an undeclared alias could edit it: {display}",
        )
    if before.st_size > max_bytes:
        raise SourceGuardError(
            "SOURCE_QUOTA_EXCEEDED",
            f"source is {before.st_size} bytes, quota is {max_bytes}: {display}",
        )

    hasher = hashlib.sha256()
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, READ_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise SourceGuardError(
                "SOURCE_QUOTA_EXCEEDED",
                f"source grew past the {max_bytes}-byte quota while reading: {display}",
            )
        hasher.update(chunk)
        if keep_bytes:
            chunks.append(chunk)

    after = os.fstat(descriptor)
    if _identity(after) != _identity(before):
        raise SourceGuardError(
            "SOURCE_MUTATED", f"source identity changed while it was read: {display}"
        )
    return total, hasher.hexdigest(), _identity(before), (b"".join(chunks) if keep_bytes else None)


def _check_unchanged(display: str, before: SourceSnapshot, current: SourceSnapshot) -> None:
    if current.identity != before.identity:
        raise SourceGuardError(
            "SOURCE_MUTATED", f"source identity changed after measurement: {display}"
        )
    if current.digest != before.digest or current.byte_count != before.byte_count:
        raise SourceGuardError("SOURCE_MUTATED", f"source bytes changed after measurement: {display}")


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------
def snapshot_source(
    root: Path,
    locator: str,
    *,
    max_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> SourceSnapshot:
    """Snapshot one declared locator inside an accepted input root."""
    root_path = _resolved_root(root)
    parts = _locator_parts(locator)
    candidate = root_path.joinpath(*parts)
    root_parts = root_path.parts
    if candidate.parts[: len(root_parts)] != root_parts:  # pragma: no cover - guarded above
        raise SourceGuardError("MEDIA_CORPUS_INVALID", f"locator escapes the input root: {locator!r}")

    descriptor = _open_regular_beneath(root_path, parts, locator)
    try:
        byte_count, digest, identity, _ = _read_descriptor(descriptor, locator, max_bytes=max_bytes)
    finally:
        os.close(descriptor)
    return SourceSnapshot(
        path=str(candidate),
        relative_locator=locator,
        byte_count=byte_count,
        digest=digest,
        identity=identity,
    )


def verify_source(
    root: Path,
    locator: str,
    snapshot: SourceSnapshot,
    *,
    max_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> SourceSnapshot:
    """Re-read a declared locator and refuse if it changed since ``snapshot``."""
    current = snapshot_source(root, locator, max_bytes=max_bytes)
    _check_unchanged(locator, snapshot, current)
    return current


def snapshot_path(path: str | Path, *, max_bytes: int = DEFAULT_MAX_SOURCE_BYTES) -> SourceSnapshot:
    """Snapshot an absolute source path (resolved once, then opened no-follow)."""
    parts, raw = _absolute_leaf_parts(path)
    descriptor = _open_regular_beneath(Path(os.sep), parts, str(raw))
    try:
        byte_count, digest, identity, _ = _read_descriptor(
            descriptor, str(raw), max_bytes=max_bytes
        )
    finally:
        os.close(descriptor)
    return SourceSnapshot(
        path=str(raw),
        relative_locator=None,
        byte_count=byte_count,
        digest=digest,
        identity=identity,
    )


def verify_path(
    path: str | Path,
    snapshot: SourceSnapshot,
    *,
    max_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> SourceSnapshot:
    """Re-read an absolute source path and refuse if it changed."""
    current = snapshot_path(path, max_bytes=max_bytes)
    _check_unchanged(str(path), snapshot, current)
    return current
