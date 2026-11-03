"""Gate-0 Revision-18 Task-3 M1R wrapper, total path resolver and stable census.

This module owns exactly three governed public callables plus the closed
``CensusFS`` five-method protocol of plan §5.4:

* ``M1R_NATIVE_CANDIDATE_CLASSIFIER_V1`` — the only native/non-native
  classification entry used by Census A and Census B (spec §12.2.1);
* ``canonicalize_path_v1`` — the total ``PATH_CANONICALIZATION_V1`` resolver with
  the project-owned 32-expansion ceiling (spec §12.2.1, plan §8.2);
* ``capture_stable_census`` / ``serialize_native_manifest`` —
  ``PYTHON_NATIVE_CLOSURE_STABLE_CENSUS_V1`` and its exact canonical
  serialization (spec §12.2.1, plan §8.3/§8.4).

``_OSBackedCensusFS.list_entries`` is the sole bounded traversal leaf and is the
only place in this file that opens a directory.  ``lstat_kind`` therefore
classifies every entry with ``os.lstat`` before any symlink is followed, so the
census can never traverse a directory symlink.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import replace
from pathlib import PurePath
from typing import Protocol

from gate0.feasibility.macos_stage_b_evidence_constants import (
    CanonicalizationFailureReason,
    CanonicalizationResult,
    CanonicalizationTerminalFamily,
    CensusNamespaceRow,
    CensusScopeTag,
    EntryKind,
    EvidenceDagError,
    EvidenceFailureCode,
    FSEntryObservation,
    NativeCandidateClassification,
    NativeManifestRow,
    PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1,
    PYTHON_NATIVE_RUNTIME_CLOSURE_V1,
    StableCensusResult,
)
from gate0.feasibility.macos_stage_b_evidence_macho import (
    MACHO_CONTAINER_SLICE_POLICY_V1,
    MACHO_NATIVE_CONTAINER_PARSE_V1,
    macho_container_slice_disposition,
)

_FAILURE = EvidenceFailureCode.DEPENDENCY_INVENTORY_DERIVATION_INVALID

_MAX_U16 = 0xFFFF
_MAX_U32 = 0xFFFFFFFF
_MAX_U64 = 0xFFFFFFFFFFFFFFFF

#: POSIX ``stat`` file-type masks.  Spelled out here so the plan-owned
#: safe-import closure stays exact (``stat`` is not an approved import prefix).
_S_IFMT = 0o170000
_S_IFDIR = 0o040000
_S_IFREG = 0o100000
_S_IFLNK = 0o120000


def _fail(detail: str) -> EvidenceDagError:
    return EvidenceDagError(_FAILURE, detail)


class CensusFS(Protocol):
    """Injected, bounded filesystem observation surface of the stable census."""

    def list_entries(self, directory: PurePath) -> tuple[FSEntryObservation, ...]:
        ...

    def lstat_kind(self, path: PurePath) -> EntryKind:
        ...

    def readlink_bytes(self, path: PurePath) -> bytes:
        ...

    def read_file_bytes(self, path: PurePath) -> bytes:
        ...

    def path_exists(self, path: PurePath) -> bool:
        ...


# ---------------------------------------------------------------------------
# M1R ordinary-file entry — M1R_NATIVE_CANDIDATE_CLASSIFIER_V1
# ---------------------------------------------------------------------------

def M1R_NATIVE_CANDIDATE_CLASSIFIER_V1(data: bytes) -> NativeCandidateClassification:
    """Classify one bounded-root regular-file byte image (spec §12.2.1).

    Fewer than four bytes, or a first-four-byte value matching no row of the
    closed container table, is ordinary ``NON_NATIVE`` content and never reaches
    the native parser.  A listed ``REJECT_UNSUPPORTED`` row is
    ``UNSUPPORTED_MACHO_CANDIDATE``.  A listed ``SUPPORTED`` row must satisfy the
    complete project grammar; any grammar failure is ``UNSUPPORTED_MACHO_CANDIDATE``
    and never degrades to ``NON_NATIVE``.
    """
    if type(data) is not bytes:
        raise _fail("M1R classifier input must be an immutable byte image")
    if len(data) < 4:
        return NativeCandidateClassification.NON_NATIVE
    first_four = bytes(data[:4])
    listed = any(row[0] == first_four for row in MACHO_CONTAINER_SLICE_POLICY_V1)
    if not listed:
        return NativeCandidateClassification.NON_NATIVE
    _symbolic, disposition = macho_container_slice_disposition(first_four)
    if disposition != "SUPPORTED":
        return NativeCandidateClassification.UNSUPPORTED_MACHO_CANDIDATE
    try:
        MACHO_NATIVE_CONTAINER_PARSE_V1(bytes(data))
    except EvidenceDagError:
        return NativeCandidateClassification.UNSUPPORTED_MACHO_CANDIDATE
    return NativeCandidateClassification.NATIVE_MEMBER


# ---------------------------------------------------------------------------
# Total symlink resolver — PATH_CANONICALIZATION_V1
# ---------------------------------------------------------------------------

def _normalize(path: PurePath) -> PurePath | None:
    """Return the lexical canonical form of ``path`` or ``None`` when invalid."""
    parts: list[str] = []
    for part in path.parts:
        if part == "/":
            parts = ["/"]
        elif part in ("", "."):
            continue
        elif part == "..":
            if len(parts) <= 1:
                return None
            parts.pop()
        else:
            parts.append(part)
    if not parts:
        return None
    if parts[0] == "/":
        return PurePath("/", *parts[1:]) if len(parts) > 1 else PurePath("/")
    return PurePath(*parts)


def _target_path(raw: bytes, containing_directory: PurePath) -> PurePath | None:
    if not raw or b"\x00" in raw:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    target = PurePath(text)
    if not target.is_absolute():
        target = containing_directory / target
    return _normalize(target)


def _path_exists(fs: CensusFS, path: PurePath) -> bool:
    try:
        return bool(fs.path_exists(path))
    except OSError:
        return False


def canonicalize_path_v1(path: PurePath, fs: CensusFS) -> CanonicalizationResult:
    """Total resolver for one encountered symlink pathname (spec §12.2.1).

    The project-owned hop ceiling is checked *before* each expansion and
    therefore precedes the repeated-pathname rule: an already visited pathname
    observed at ``symlink_hops == 32`` is ``CANONICALIZATION_FAILURE`` with
    reason ``CANONICALIZATION_FAILURE_HOP_LIMIT``, not ``SYMLINK_CYCLE``.
    """
    symlink_hops = 0
    visited_symlink_pathnames: set[PurePath] = set()
    current = _normalize(PurePath(path))
    if current is None:
        return CanonicalizationResult(
            CanonicalizationTerminalFamily.CANONICALIZATION_FAILURE, None, None, symlink_hops,
        )
    while True:
        try:
            kind = fs.lstat_kind(current)
        except OSError:
            if _path_exists(fs, current):
                return CanonicalizationResult(
                    CanonicalizationTerminalFamily.CANONICALIZATION_FAILURE, None, None, symlink_hops,
                )
            return CanonicalizationResult(
                CanonicalizationTerminalFamily.DANGLING, None, None, symlink_hops,
            )
        if kind is EntryKind.DIRECTORY:
            return CanonicalizationResult(
                CanonicalizationTerminalFamily.RESOLVED_DIRECTORY, None, current, symlink_hops,
            )
        if kind is EntryKind.REGULAR_FILE:
            return CanonicalizationResult(
                CanonicalizationTerminalFamily.RESOLVED_REGULAR_FILE, None, current, symlink_hops,
            )
        if kind is not EntryKind.SYMLINK:
            return CanonicalizationResult(
                CanonicalizationTerminalFamily.RESOLVED_UNSUPPORTED_OBJECT, None, current, symlink_hops,
            )
        if symlink_hops == PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1:
            return CanonicalizationResult(
                CanonicalizationTerminalFamily.CANONICALIZATION_FAILURE,
                CanonicalizationFailureReason.CANONICALIZATION_FAILURE_HOP_LIMIT,
                None,
                symlink_hops,
            )
        symlink_hops += 1
        if current in visited_symlink_pathnames:
            return CanonicalizationResult(
                CanonicalizationTerminalFamily.SYMLINK_CYCLE, None, None, symlink_hops,
            )
        visited_symlink_pathnames.add(current)
        try:
            raw = fs.readlink_bytes(current)
        except OSError:
            return CanonicalizationResult(
                CanonicalizationTerminalFamily.CANONICALIZATION_FAILURE, None, None, symlink_hops,
            )
        target = _target_path(raw, current.parent)
        if target is None:
            return CanonicalizationResult(
                CanonicalizationTerminalFamily.CANONICALIZATION_FAILURE, None, None, symlink_hops,
            )
        current = target


# ---------------------------------------------------------------------------
# Private OS-backed census filesystem
# ---------------------------------------------------------------------------

class _OSBackedCensusFS:
    """Private concrete ``CensusFS`` for a real bounded Python-runtime census."""

    _READ_CHUNK = 1 << 16

    def list_entries(self, directory: PurePath) -> tuple[FSEntryObservation, ...]:
        """Sole bounded traversal leaf: ``os.scandir`` on an already-validated directory."""
        observations = []
        with os.scandir(str(directory)) as iterator:
            for child in iterator:
                path = PurePath(child.path)
                if child.is_symlink():
                    raw = os.readlink(child.path)
                    if not isinstance(raw, bytes):
                        raw = raw.encode("utf-8", "surrogateescape")
                    observations.append(FSEntryObservation(path, EntryKind.SYMLINK, raw))
                elif child.is_dir(follow_symlinks=False):
                    observations.append(FSEntryObservation(path, EntryKind.DIRECTORY, None))
                elif child.is_file(follow_symlinks=False):
                    observations.append(FSEntryObservation(path, EntryKind.REGULAR_FILE, None))
                else:
                    raise OSError(f"unsupported filesystem object: {path}")
        return tuple(observations)

    def lstat_kind(self, path: PurePath) -> EntryKind:
        mode = os.lstat(str(path)).st_mode & _S_IFMT
        if mode == _S_IFLNK:
            return EntryKind.SYMLINK
        if mode == _S_IFDIR:
            return EntryKind.DIRECTORY
        if mode == _S_IFREG:
            return EntryKind.REGULAR_FILE
        raise OSError(f"unsupported filesystem object: {path}")

    def readlink_bytes(self, path: PurePath) -> bytes:
        raw = os.readlink(str(path))
        if isinstance(raw, bytes):
            return raw
        return raw.encode("utf-8", "surrogateescape")

    def read_file_bytes(self, path: PurePath) -> bytes:
        descriptor = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
        try:
            chunks = []
            while True:
                chunk = os.read(descriptor, self._READ_CHUNK)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(descriptor)

    def path_exists(self, path: PurePath) -> bool:
        return os.path.lexists(str(path))


# ---------------------------------------------------------------------------
# PYTHON_NATIVE_CLOSURE_STABLE_CENSUS_V1
# ---------------------------------------------------------------------------

class _CensusPass:
    """Transient accumulator of exactly one complete two-root traversal."""

    def __init__(self):
        self.rows: list[CensusNamespaceRow] = []
        self.classifications: dict[PurePath, NativeCandidateClassification] = {}
        self.reads: dict[PurePath, bytes] = {}
        self.images: dict[PurePath, bytes] = {}
        self.subjects: dict[PurePath, tuple[CensusScopeTag, bytes]] = {}


def _relative_bytes(root: PurePath, path: PurePath) -> bytes:
    return path.relative_to(root).as_posix().encode("utf-8")


def _validated_root(root: PurePath, fs: CensusFS) -> PurePath:
    normalized = _normalize(PurePath(root))
    if normalized is None:
        raise _fail("census root is not a canonical path")
    try:
        kind = fs.lstat_kind(normalized)
    except OSError as exc:
        raise _fail("census root is absent or unreadable") from exc
    if kind is not EntryKind.DIRECTORY:
        raise _fail("census root is not a real directory")
    return normalized


def _require_disjoint(first: PurePath, second: PurePath) -> None:
    if first == second or first in second.parents or second in first.parents:
        raise _fail("census roots are not disjoint and non-nested")


def _owning_scope(target: PurePath, base: PurePath, venv: PurePath) -> tuple[CensusScopeTag, PurePath]:
    owners = [
        (scope_tag, root)
        for scope_tag, root in (
            (CensusScopeTag.BASE_RUNTIME, base),
            (CensusScopeTag.RUN_SCOPED_VENV, venv),
        )
        if target == root or root in target.parents
    ]
    if not owners:
        raise _fail("canonical target lies outside both census roots")
    if len(owners) != 1:
        raise _fail("canonical target belongs to both census roots")
    return owners[0]


def _classify_subject(subject: PurePath, scope_tag: CensusScopeTag, root: PurePath,
                      fs: CensusFS, pass_: _CensusPass, collect_images: bool
                      ) -> NativeCandidateClassification:
    existing = pass_.classifications.get(subject)
    if existing is not None:
        return existing
    try:
        data = fs.read_file_bytes(subject)
    except OSError as exc:
        raise _fail("regular-file read failed during the census") from exc
    pass_.reads[subject] = data
    classification = M1R_NATIVE_CANDIDATE_CLASSIFIER_V1(data)
    if classification is NativeCandidateClassification.UNSUPPORTED_MACHO_CANDIDATE:
        raise _fail("unsupported mach-o candidate encountered during the census")
    pass_.classifications[subject] = classification
    if classification is NativeCandidateClassification.NATIVE_MEMBER:
        if collect_images:
            pass_.images[subject] = data
        pass_.subjects[subject] = (scope_tag, _relative_bytes(root, subject))
    return classification


def _census_pass(base: PurePath, venv: PurePath, fs: CensusFS, *,
                 collect_images: bool) -> _CensusPass:
    pass_ = _CensusPass()
    for scope_tag, root in (
        (CensusScopeTag.BASE_RUNTIME, base),
        (CensusScopeTag.RUN_SCOPED_VENV, venv),
    ):
        stack = [root]
        while stack:
            directory = stack.pop()
            try:
                kind = fs.lstat_kind(directory)
            except OSError as exc:
                raise _fail("directory lstat failed during the census") from exc
            if kind is not EntryKind.DIRECTORY:
                raise _fail("directory recursion target is not a real directory")
            try:
                entries = fs.list_entries(directory)
            except OSError as exc:
                raise _fail("directory enumeration failed during the census") from exc
            for observation in entries:
                entry_path = observation.path
                relative = _relative_bytes(root, entry_path)
                if observation.kind is EntryKind.DIRECTORY:
                    pass_.rows.append(CensusNamespaceRow(
                        scope_tag, relative, EntryKind.DIRECTORY, None, None, None,
                    ))
                    stack.append(entry_path)
                elif observation.kind is EntryKind.REGULAR_FILE:
                    pass_.rows.append(CensusNamespaceRow(
                        scope_tag, relative, EntryKind.REGULAR_FILE, None, None, None,
                    ))
                    _classify_subject(entry_path, scope_tag, root, fs, pass_, collect_images)
                elif observation.kind is EntryKind.SYMLINK:
                    if observation.raw_link_target is None:
                        raise _fail("symlink entry is missing its exact raw link target")
                    resolution = canonicalize_path_v1(entry_path, fs)
                    pass_.rows.append(CensusNamespaceRow(
                        scope_tag, relative, EntryKind.SYMLINK, observation.raw_link_target,
                        resolution, resolution.canonical_target,
                    ))
                    if resolution.family is CanonicalizationTerminalFamily.RESOLVED_DIRECTORY:
                        raise _fail("directory symlink is never traversed")
                    if resolution.family is not CanonicalizationTerminalFamily.RESOLVED_REGULAR_FILE:
                        raise _fail("symlink resolution failed the census law")
                    target_scope, target_root = _owning_scope(resolution.canonical_target, base, venv)
                    _classify_subject(
                        resolution.canonical_target, target_scope, target_root, fs, pass_, collect_images,
                    )
                else:
                    raise _fail("unsupported filesystem object encountered during the census")
    return pass_


def _row_sort_key(row: CensusNamespaceRow):
    return (row.scope_tag.value.encode("utf-8"), row.relative_path_utf8, row.entry_kind.value)


def _manifest_sort_key(row: NativeManifestRow):
    return (row.scope_tag.value.encode("utf-8"), row.relative_path_utf8, row.sha256_hex)


def capture_stable_census(base_root: PurePath, venv_root: PurePath, fs: CensusFS) -> StableCensusResult:
    """One logical stable-census capture (spec §12.2.1).

    A successful capture is exactly namespace-set equality plus all required
    native classification/digest equalities.  It makes no atomic historical
    filesystem-snapshot claim.
    """
    base = _validated_root(base_root, fs)
    venv = _validated_root(venv_root, fs)
    _require_disjoint(base, venv)

    census_a = _census_pass(base, venv, fs, collect_images=True)
    census_b = _census_pass(base, venv, fs, collect_images=False)

    if set(census_a.rows) != set(census_b.rows):
        raise _fail("namespace sets differ between census A and census B")

    for subject, classification in census_a.classifications.items():
        other = census_b.classifications.get(subject)
        if classification is NativeCandidateClassification.NATIVE_MEMBER:
            if other is not NativeCandidateClassification.NATIVE_MEMBER:
                raise _fail("native member reclassification failed in census B")
            image = census_a.images.get(subject)
            stability = census_b.reads.get(subject)
            if image is None or stability is None:
                raise _fail("native digest differs between census A and census B")
            if hashlib.sha256(stability).digest() != hashlib.sha256(image).digest():
                raise _fail("native digest differs between census A and census B")
        elif other is NativeCandidateClassification.NATIVE_MEMBER:
            raise _fail("non-native subject became native in census B")

    manifest_rows = tuple(
        NativeManifestRow(scope_tag, relative_path, hashlib.sha256(census_a.images[subject]).hexdigest())
        for subject, (scope_tag, relative_path) in census_a.subjects.items()
    )
    partial = StableCensusResult(
        namespace_a=tuple(sorted(census_a.rows, key=_row_sort_key)),
        namespace_b=tuple(sorted(census_b.rows, key=_row_sort_key)),
        census_a_native_images=tuple(sorted(census_a.images.items(), key=lambda item: item[0].as_posix())),
        native_manifest_rows=tuple(sorted(manifest_rows, key=_manifest_sort_key)),
        native_manifest_bytes=b"",
        native_manifest_sha256="",
        native_member_count=len(manifest_rows),
    )
    data = serialize_native_manifest(partial)
    return replace(
        partial,
        native_manifest_bytes=data,
        native_manifest_sha256=hashlib.sha256(data).hexdigest(),
    )


# ---------------------------------------------------------------------------
# PYTHON_NATIVE_RUNTIME_CLOSURE_V1 serialization
# ---------------------------------------------------------------------------

def _scope_bytes(scope_tag) -> bytes:
    value = getattr(scope_tag, "value", scope_tag)
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


def _digest_bytes(sha256_hex) -> bytes:
    if not isinstance(sha256_hex, str) or len(sha256_hex) != 64:
        raise _fail("native manifest digest is not lowercase sha256 hex")
    if any(character not in "0123456789abcdef" for character in sha256_hex):
        raise _fail("native manifest digest is not lowercase sha256 hex")
    return bytes.fromhex(sha256_hex)


def serialize_native_manifest(result: StableCensusResult) -> bytes:
    """Exact canonical profile serialization (spec §12.2.1, plan §8.4)."""
    rows = tuple(result.native_manifest_rows)
    count = result.native_member_count
    if isinstance(count, bool) or not isinstance(count, int) or count < 0 or count > _MAX_U64:
        raise _fail("native manifest member count is not an unsigned 64-bit integer")
    if count != len(rows):
        raise _fail("native manifest member count disagrees with its rows")
    encoded = []
    seen: set[tuple[bytes, bytes]] = set()
    for row in rows:
        scope_bytes = _scope_bytes(row.scope_tag)
        path_bytes = row.relative_path_utf8
        if len(scope_bytes) > _MAX_U16:
            raise _fail("native manifest scope tag exceeds the u16 length bound")
        if len(path_bytes) > _MAX_U32:
            raise _fail("native manifest relative path exceeds the u32 length bound")
        digest = _digest_bytes(row.sha256_hex)
        key = (scope_bytes, bytes(path_bytes))
        if key in seen:
            raise _fail("duplicate canonical native manifest row after target de-duplication")
        seen.add(key)
        encoded.append((scope_bytes, bytes(path_bytes), digest))
    encoded.sort(key=lambda item: (item[0], item[1], item[2]))
    output = bytearray()
    output += PYTHON_NATIVE_RUNTIME_CLOSURE_V1.encode("utf-8")
    output += b"\x00"
    output += count.to_bytes(8, "big")
    for scope_bytes, path_bytes, digest in encoded:
        output += len(scope_bytes).to_bytes(2, "big")
        output += scope_bytes
        output += len(path_bytes).to_bytes(4, "big")
        output += path_bytes
        output += digest
    return bytes(output)
