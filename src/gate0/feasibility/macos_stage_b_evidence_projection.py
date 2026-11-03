"""Private descriptor-anchored Task-3 source capture implementation."""
from __future__ import annotations

from dataclasses import dataclass, field
import os
import stat
import struct
import threading
import hashlib
import json

from gate0.feasibility.macos_stage_b_evidence_constants import (
    CodeDirectoryIdentity,
    EvidenceDagError,
    N4ABoundaryPrimitive,
    SignedImageProjection,
    VerifiedSignedImageProjectionSource,
)


_GRAPH = (
    (None, None, "directory", "root"),
    (0, ".stage-b-build", "directory", "build"),
    (1, None, "directory", "generation"),
    (2, "StageBSandboxRunner.app", "directory", "application"),
    (3, "Contents", "directory", "Contents"),
    (4, "MacOS", "directory", "MacOS"),
    (4, "_CodeSignature", "directory", "_CodeSignature"),
    (5, "StageBSandboxRunner", "file", "executable"),
    (4, "Info.plist", "file", "info_plist"),
    (6, "CodeResources", "file", "code_resources"),
)
_DIRECTORY = "directory"
_FILE = "file"


def _fail(reason: str) -> EvidenceDagError:
    from gate0.feasibility import macos_stage_b_evidence_boundary as boundary
    return boundary._fail(reason)


@dataclass
class _GraphEntry:
    index: int
    parent_index: int | None
    name: str | None
    kind: str
    role: str
    fd: int
    identity: tuple[int, int, int] | None
    stat_snapshot: os.stat_result | None


@dataclass
class _CaptureSession:
    context: object
    application: object
    generation: str
    entries: list[_GraphEntry] = field(default_factory=list)
    role_fds: dict[str, int] = field(default_factory=dict)
    origin_live: bool = True
    release_requested: bool = False
    released: bool = False
    release_attempted: bool = False
    accepted: bool = False
    refusal_reason: str | None = None
    operation_lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def descriptors(self) -> tuple[int, ...]:
        return tuple(entry.fd for entry in self.entries)


def _identity(st: os.stat_result) -> tuple[int, int, int]:
    return st.st_dev, st.st_ino, stat.S_IFMT(st.st_mode)


def _required_platform_semantics() -> None:
    required_flags = ("O_RDONLY", "O_CLOEXEC", "O_NOFOLLOW", "O_DIRECTORY")
    nonzero_flags = ("O_CLOEXEC", "O_NOFOLLOW", "O_DIRECTORY")
    if any(not hasattr(os, flag) for flag in required_flags) or any(
            getattr(os, flag) == 0 for flag in nonzero_flags):
        raise _fail("NOT_OBSERVED: required no-follow descriptor flags are unavailable")
    if os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd:
        raise _fail("NOT_OBSERVED: directory-relative open/stat is unavailable")
    if os.stat not in os.supports_follow_symlinks:
        raise _fail("NOT_OBSERVED: no-follow namespace stat is unavailable")


def _open_flags(kind: str) -> int:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    if kind == _DIRECTORY:
        flags |= os.O_DIRECTORY
    return flags


def _record_entry(session: _CaptureSession, parent_index: int | None,
                  name: str | None, kind: str, role: str, fd: int) -> _GraphEntry:
    entry = _GraphEntry(len(session.entries), parent_index, name, kind, role, fd, None, None)
    session.entries.append(entry)
    st = os.fstat(fd)
    expected = stat.S_ISDIR(st.st_mode) if kind == _DIRECTORY else stat.S_ISREG(st.st_mode)
    if not expected or st.st_nlink < 1:
        raise _fail(f"NOT_OBSERVED: required {role} object has invalid type or availability")
    entry.identity = _identity(st)
    entry.stat_snapshot = st
    if kind == _FILE:
        session.role_fds[role] = fd
    return entry


def _acquire_origin_graph(context, application) -> _CaptureSession:
    """Anchor and retain the complete fixed graph without reading source bytes."""
    _required_platform_semantics()
    session = _CaptureSession(context, application, context.generation_identity)
    root_path = context.canonical_root
    try:
        for index, (parent_index, name, kind, role) in enumerate(_GRAPH):
            if index == 0:
                fd = os.open(root_path, _open_flags(kind))
            else:
                if role == "generation":
                    name = session.generation
                parent = session.entries[parent_index]
                fd = os.open(name, _open_flags(kind), dir_fd=parent.fd)
            entry = _record_entry(session, parent_index, name, kind, role, fd)
            if role == "root" and (entry.identity[0] != context.root_device
                                    or entry.identity[1] != context.root_inode):
                raise _fail("NOT_OBSERVED: repository root differs from registered context")
            if role == "application" and os.fstat(fd).st_ino != os.stat(
                    application._subject_path.name,
                    dir_fd=session.entries[2].fd,
                    follow_symlinks=False,
            ).st_ino:
                raise _fail("NOT_OBSERVED: application binding differs from registered subject")
        _validate_origin_graph(session)
        return session
    except EvidenceDagError as exc:
        session.origin_live = False
        session.refusal_reason = str(exc)
    except (OSError, NotImplementedError, TypeError, ValueError) as exc:
        session.origin_live = False
        session.refusal_reason = f"NOT_OBSERVED: descriptor graph acquisition failed: {type(exc).__name__}"
    except BaseException as exc:
        session.origin_live = False
        session.refusal_reason = f"NOT_OBSERVED: descriptor graph acquisition failed: {type(exc).__name__}"
        from gate0.feasibility import macos_stage_b_evidence_boundary as boundary
        with boundary._SOURCE_LIFECYCLE_LOCK:
            binding = boundary._CAPTURE_BINDINGS.get(id(application))
            if binding is not None and binding.application is application:
                binding.session = session
                binding.state = "REFUSED"
                binding.refusal_reason = session.refusal_reason
                binding.eligibility_version += 1
        try:
            _release_origin_graph(session)
        except BaseException as cleanup_error:
            session.refusal_reason += (
                f"; NOT_OBSERVED: descriptor cleanup remains unresolved: "
                f"{type(cleanup_error).__name__}"
            )
        raise
    if session.refusal_reason is not None:
        try:
            _release_origin_graph(session)
        except EvidenceDagError as cleanup_error:
            session.refusal_reason = f"{session.refusal_reason}; {cleanup_error.reason}"
    return session


def _validate_origin_graph(session: _CaptureSession) -> None:
    if session.released or not session.origin_live or len(session.entries) != len(_GRAPH):
        raise _fail("NOT_OBSERVED: registration-origin descriptor lifetime is unavailable")
    for entry in session.entries:
        if entry.identity is None or entry.stat_snapshot is None:
            session.origin_live = False
            raise _fail(f"NOT_OBSERVED: retained {entry.role} descriptor metadata is unavailable")
        try:
            held = os.fstat(entry.fd)
        except OSError as exc:
            session.origin_live = False
            session.refusal_reason = "NOT_OBSERVED: retained origin descriptor was lost"
            raise _fail(session.refusal_reason) from exc
        if (_identity(held) != entry.identity or held.st_nlink < 1
                or (stat.S_ISDIR(held.st_mode) != (entry.kind == _DIRECTORY))
                or held.st_size != entry.stat_snapshot.st_size
                or held.st_mtime_ns != entry.stat_snapshot.st_mtime_ns):
            raise _fail(f"NOT_OBSERVED: retained {entry.role} object changed")
        if entry.parent_index is not None:
            parent = session.entries[entry.parent_index]
            try:
                current = os.stat(entry.name, dir_fd=parent.fd, follow_symlinks=False)
            except (OSError, NotImplementedError) as exc:
                raise _fail(f"NOT_OBSERVED: current {entry.role} binding is unavailable") from exc
            if (_identity(current) != entry.identity or current.st_nlink < 1
                    or stat.S_ISLNK(current.st_mode)):
                raise _fail(f"NOT_OBSERVED: current {entry.role} binding differs from origin")
    root = session.entries[0]
    try:
        current_root = os.stat(session.context.canonical_root, follow_symlinks=False)
    except (OSError, NotImplementedError) as exc:
        raise _fail("NOT_OBSERVED: repository root binding is unavailable") from exc
    if _identity(current_root) != root.identity or stat.S_ISLNK(current_root.st_mode):
        raise _fail("NOT_OBSERVED: repository root binding differs from origin")


def _release_origin_graph(session: _CaptureSession) -> None:
    if session.released:
        return
    if session.release_attempted:
        raise _fail(session.refusal_reason or "NOT_OBSERVED: descriptor cleanup remains unresolved")
    if not session.accepted:
        from gate0.feasibility import macos_stage_b_evidence_boundary as boundary
        boundary._request_capture_invalidation(
            session.application, "NOT_OBSERVED: retained origin was released before acceptance",
        )
    session.release_attempted = True
    first_error = None
    unresolved = set()
    for entry in reversed(session.entries):
        try:
            os.close(entry.fd)
        except OSError as exc:
            first_error = first_error or exc
            unresolved.add(entry.index)
    if first_error is None:
        session.entries.clear()
        session.role_fds.clear()
    else:
        session.entries[:] = [entry for entry in session.entries if entry.index in unresolved]
        session.role_fds = {
            role: fd for role, fd in session.role_fds.items()
            if any(entry.fd == fd for entry in session.entries)
        }
    session.released = first_error is None
    session.origin_live = False
    if first_error is not None:
        session.refusal_reason = "NOT_OBSERVED: descriptor cleanup failed"
        raise _fail(session.refusal_reason) from first_error


def _read_complete_physical_input(session: _CaptureSession, role: str) -> bytes:
    """Read one nonempty physical input only through its retained descriptor."""
    boundary = __import__("gate0.feasibility.macos_stage_b_evidence_boundary",
                          fromlist=["_fail"])
    if role not in {"executable", "info_plist", "code_resources"}:
        raise boundary._fail("NOT_OBSERVED: unknown physical input role")
    entry = next((item for item in session.entries if item.role == role), None)
    if entry is None or entry.kind != _FILE or session.role_fds.get(role) != entry.fd:
        raise boundary._fail(f"NOT_OBSERVED: retained {role} descriptor is unavailable")
    try:
        before = os.fstat(entry.fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_size <= 0
                or _identity(before) != entry.identity
                or before.st_size != entry.stat_snapshot.st_size
                or before.st_mtime_ns != entry.stat_snapshot.st_mtime_ns):
            raise boundary._fail(f"NOT_OBSERVED: retained {role} input size/type changed")
        chunks = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(entry.fd, remaining)
            if not chunk:
                raise boundary._fail(f"NOT_OBSERVED: retained {role} input ended early")
            chunks.append(chunk)
            remaining -= len(chunk)
        after = os.fstat(entry.fd)
        if (_identity(after) != entry.identity or after.st_size != before.st_size
                or after.st_mtime_ns != before.st_mtime_ns or after.st_nlink < 1):
            raise boundary._fail(f"NOT_OBSERVED: retained {role} input changed during read")
        return b"".join(chunks)
    except EvidenceDagError:
        raise
    except (OSError, NotImplementedError, TypeError, ValueError) as exc:
        raise boundary._fail(f"NOT_OBSERVED: retained {role} input read failed") from exc


def _extract_source_fields(executable: bytes, info: bytes, resources: bytes) -> dict[str, object]:
    """Extract the frozen Task-3 source inventory from one immutable image buffer."""
    from gate0.feasibility.macos_stage_b_evidence_constants import CodeDirectoryIdentity

    def bad(message):
        raise _fail(f"NOT_OBSERVED: {message}")

    if any(type(value) is not bytes or not value for value in (executable, info, resources)):
        bad("required physical input is empty or mutable")
    if len(executable) < 32:
        bad("Mach-O header is truncated")
    magic = executable[:4]
    if magic == b"\xcf\xfa\xed\xfe":
        endian = "<"
    elif magic == b"\xfe\xed\xfa\xcf":
        endian = ">"
    else:
        bad("unsupported Mach-O magic")
    try:
        _, _, _, _, command_count, commands_size, _, _ = struct.unpack_from(endian + "IiiIIIII", executable, 0)
        commands_end = 32 + commands_size
        if command_count < 1 or commands_end > len(executable) or commands_end < 32:
            bad("Mach-O load command extent is invalid")
        offset = 32
        signature = None
        for _ in range(command_count):
            if offset + 8 > commands_end:
                bad("Mach-O load command is truncated")
            command, command_size = struct.unpack_from(endian + "II", executable, offset)
            if command_size < 8 or offset + command_size > commands_end:
                bad("Mach-O load command size is invalid")
            if command == 0x1D:
                if signature is not None or command_size != 16:
                    bad("LC_CODE_SIGNATURE is duplicate or malformed")
                signature = struct.unpack_from(endian + "II", executable, offset + 8)
            offset += command_size
        if offset != commands_end or signature is None:
            bad("Mach-O signature command is absent or ambiguous")
        data_offset, data_size = signature
        if data_offset < commands_end or data_size < 52 or data_offset + data_size > len(executable):
            bad("Mach-O signature extent is invalid")
        signature_bytes = executable[data_offset:data_offset + data_size]
        magic_sb, total_length, count = struct.unpack_from(">III", signature_bytes, 0)
        if magic_sb != 0xFADE0CC0 or total_length != len(signature_bytes) or count != 5:
            bad("embedded signature superblob header is invalid")
        index_length = 12 + count * 8
        if index_length != 52:
            bad("embedded signature index length is invalid")
        entries = {}
        ranges = []
        for idx in range(count):
            slot_type, blob_offset = struct.unpack_from(">II", signature_bytes, 12 + idx * 8)
            if slot_type in entries or blob_offset < index_length or blob_offset + 8 > total_length:
                bad("embedded signature index entry is duplicate or out of range")
            blob_magic, blob_length = struct.unpack_from(">II", signature_bytes, blob_offset)
            if blob_length < 8 or blob_offset + blob_length > total_length:
                bad("embedded signature blob extent is invalid")
            blob = signature_bytes[blob_offset:blob_offset + blob_length]
            if struct.unpack_from(">I", blob, 0)[0] != blob_magic:
                bad("embedded signature blob magic is inconsistent")
            entries[slot_type] = blob
            ranges.append((blob_offset, blob_offset + blob_length))
        if set(entries) != {0, 2, 5, 7, 0x10000}:
            bad("embedded signature blob inventory is incomplete")
        expected_blob_magic = {
            0: 0xFADE0C02,
            2: 0xFADE0C01,
            5: 0xFADE7171,
            7: 0xFADE7172,
            0x10000: 0xFADE0B01,
        }
        for slot_type, expected_magic in expected_blob_magic.items():
            if struct.unpack_from(">I", entries[slot_type], 0)[0] != expected_magic:
                bad("embedded signature blob magic does not match its slot type")
        ordered_ranges = sorted(ranges)
        if any(left[1] > right[0] for left, right in zip(ordered_ranges, ordered_ranges[1:])):
            bad("embedded signature blobs overlap")
        cd = entries[0]
        if struct.unpack_from(">I", cd, 0)[0] != 0xFADE0C02 or len(cd) < 44:
            bad("CodeDirectory header is malformed")
        (cd_magic, cd_length, cd_version, cd_flags, hash_offset, ident_offset,
         special_count, code_count, code_limit, hash_size, hash_type,
         platform, page_size_log2, spare2) = struct.unpack_from(">9I4BI", cd, 0)
        if (cd_length != len(cd) or cd_version != 0x20001 or hash_size != 32 or hash_type != 2
                or special_count != 7 or page_size_log2 > 30 or code_limit != data_offset
                or code_limit <= 0):
            bad("CodeDirectory parameters are unsupported or inconsistent")
        page_size = 1 << page_size_log2
        expected_code_count = (code_limit + page_size - 1) // page_size
        if code_count != expected_code_count or ident_offset < 44 or ident_offset >= hash_offset:
            bad("CodeDirectory hash extents are inconsistent")
        special_start = hash_offset - special_count * hash_size
        code_hash_end = hash_offset + code_count * hash_size
        if special_start < ident_offset or code_hash_end > len(cd):
            bad("CodeDirectory slot extent is out of range")
        ident_end = cd.find(b"\x00", ident_offset, special_start)
        if ident_end < 0:
            bad("CodeDirectory identifier is unterminated")
        code_hashes = []
        for slot in range(code_count):
            start = slot * page_size
            page = executable[start:min(start + page_size, code_limit)]
            expected_hash = hashlib.sha256(page).digest()
            stored_hash = cd[hash_offset + slot * hash_size:hash_offset + (slot + 1) * hash_size]
            if stored_hash != expected_hash:
                bad("CodeDirectory code page hash does not match captured bytes")
            code_hashes.append(expected_hash.hex())
        special_values = {}
        special_state = []
        special_hashes = []
        for slot in range(1, special_count + 1):
            start = hash_offset - slot * hash_size
            value = cd[start:start + hash_size]
            special_values[slot] = value
            special_state.append((-slot, value))
            special_hashes.append((-slot, None if slot in (4, 6) else value.hex()))
        expected_special = {
            1: hashlib.sha256(info).digest(),
            2: hashlib.sha256(entries[2]).digest(),
            3: hashlib.sha256(resources).digest(),
            4: bytes(32),
            5: hashlib.sha256(entries[5]).digest(),
            6: bytes(32),
            7: hashlib.sha256(entries[7]).digest(),
        }
        if special_values != expected_special:
            bad("CodeDirectory special slot hashes do not match captured inputs")
        identity = CodeDirectoryIdentity(
            sha256=hashlib.sha256(cd).hexdigest(), code_limit=code_limit,
            page_size=page_size, code_slot_sha256=tuple(code_hashes),
            special_slot_sha256=tuple(special_hashes),
        )
        return {
            "executable_code_region_bytes": bytes(executable[:code_limit]),
            "info_plist_bytes": bytes(info),
            "code_resources_bytes": bytes(resources),
            "superblob_index_bytes": bytes(signature_bytes[:index_length]),
            "code_directory_bytes": bytes(cd),
            "entitlements_blob_bytes": bytes(entries[5]),
            "der_entitlements_blob_bytes": bytes(entries[7]),
            "requirements_blob_sha256": hashlib.sha256(entries[2]).hexdigest(),
            "cms_signature_blob_sha256": hashlib.sha256(entries[0x10000]).hexdigest(),
            "special_slot_state": tuple(special_state),
            "code_directory_identity": identity,
        }
    except EvidenceDagError:
        raise
    except (IndexError, OverflowError, struct.error, TypeError, ValueError) as exc:
        raise _fail("NOT_OBSERVED: malformed embedded image structure") from exc


def capture_signed_image_projection_source(application):
    """Capture and verify a source from the exact registration-origin graph."""
    from gate0.feasibility import macos_stage_b_evidence_boundary as boundary

    binding = boundary._begin_capture(application)
    session = binding.session
    if session is None:
        boundary._refuse_capture(binding, "NOT_OBSERVED: capture session is unavailable")
        raise boundary._fail("NOT_OBSERVED: capture session is unavailable")
    try:
        with session.operation_lock:
            _validate_origin_graph(session)
            executable = _read_complete_physical_input(session, "executable")
            info = _read_complete_physical_input(session, "info_plist")
            resources = _read_complete_physical_input(session, "code_resources")
            _validate_origin_graph(session)
            fields = _extract_source_fields(executable, info, resources)
            _validate_origin_graph(session)
            source = boundary._publish_capture(binding, fields)
            _release_origin_graph(session)
            return source
    except EvidenceDagError as exc:
        boundary._refuse_capture(binding, exc.reason)
        if not session.released:
            try:
                _release_origin_graph(session)
            except EvidenceDagError as cleanup_error:
                boundary._refuse_capture(binding, cleanup_error.reason)
                raise cleanup_error from exc
        raise
    except (OSError, NotImplementedError, TypeError, ValueError, struct.error) as exc:
        boundary._refuse_capture(binding, f"NOT_OBSERVED: capture failed: {type(exc).__name__}")
        try:
            _release_origin_graph(session)
        except EvidenceDagError as cleanup_error:
            raise cleanup_error from exc
        raise boundary._fail(f"NOT_OBSERVED: capture failed: {type(exc).__name__}") from exc


@dataclass(frozen=True)
class _ParsedSignedImageProjection:
    """Identity-preserving private handoff of values already retained by Task 3."""

    source: VerifiedSignedImageProjectionSource
    measured_primitive: N4ABoundaryPrimitive
    source_application: object
    repository_context: object
    generation_identity: str
    executable_code_region_bytes: bytes
    info_plist_bytes: bytes
    code_resources_bytes: bytes
    superblob_index_bytes: bytes
    code_directory_bytes: bytes
    entitlements_blob_bytes: bytes
    der_entitlements_blob_bytes: bytes
    requirements_blob_sha256: str
    cms_signature_blob_sha256: str
    special_slot_state: tuple[tuple[int, bytes], ...]
    code_directory_identity: CodeDirectoryIdentity


def _parse_signed_image_projection_source(
        source: VerifiedSignedImageProjectionSource,
        measured_primitive: N4ABoundaryPrimitive,
) -> _ParsedSignedImageProjection:
    """Validate retained Task-3 values and pass their exact objects to Task 5."""

    def bad(reason: str) -> None:
        raise _fail(f"NOT_OBSERVED: retained projection {reason}")

    if type(source) is not VerifiedSignedImageProjectionSource:
        bad("source has an unsupported type")
    if type(measured_primitive) is not N4ABoundaryPrimitive:
        bad("measured primitive has an unsupported type")
    if type(source.generation_identity) is not str:
        bad("generation identity is not an exact string")

    byte_names = (
        "executable_code_region_bytes", "info_plist_bytes", "code_resources_bytes",
        "superblob_index_bytes", "code_directory_bytes", "entitlements_blob_bytes",
        "der_entitlements_blob_bytes",
    )
    for name in byte_names:
        if type(getattr(source, name)) is not bytes:
            bad(f"{name} is not exact bytes")
    if len(source.superblob_index_bytes) != 52:
        bad("superblob index does not have the retained 52-byte shape")

    def is_sha256(value: object) -> bool:
        return (type(value) is str and len(value) == 64
                and all(char in "0123456789abcdef" for char in value))

    for name in ("requirements_blob_sha256", "cms_signature_blob_sha256"):
        if not is_sha256(getattr(source, name)):
            bad(f"{name} is not a lowercase SHA-256 value")

    slots = source.special_slot_state
    expected_slots = tuple(range(-1, -8, -1))
    if type(slots) is not tuple or len(slots) != 7:
        bad("special-slot state is not a seven-entry tuple")
    for expected_slot, entry in zip(expected_slots, slots):
        if (type(entry) is not tuple or len(entry) != 2
                or type(entry[0]) is not int or entry[0] != expected_slot
                or type(entry[1]) is not bytes or len(entry[1]) != 32):
            bad("special-slot state labels or values are malformed")

    identity = source.code_directory_identity
    if type(identity) is not CodeDirectoryIdentity:
        bad("CodeDirectory identity has an unsupported type")
    if not is_sha256(identity.sha256):
        bad("CodeDirectory identity digest is malformed")
    if (type(identity.code_limit) is not int or identity.code_limit <= 0
            or type(identity.page_size) is not int or identity.page_size <= 0):
        bad("CodeDirectory identity limits are malformed")
    if identity.code_limit != len(source.executable_code_region_bytes):
        bad("CodeDirectory code limit differs from the retained executable region")
    if type(identity.code_slot_sha256) is not tuple:
        bad("CodeDirectory code-slot digests are not an exact tuple")
    if len(identity.code_slot_sha256) != (identity.code_limit + identity.page_size - 1) // identity.page_size:
        bad("CodeDirectory code-slot count differs from retained limits")
    if any(
            not is_sha256(value) for value in identity.code_slot_sha256):
        bad("CodeDirectory code-slot digests are malformed")

    special_digests = identity.special_slot_sha256
    if type(special_digests) is not tuple or len(special_digests) != 7:
        bad("CodeDirectory special-slot digests are not a seven-entry tuple")
    for expected_slot, state, digest_entry in zip(expected_slots, slots, special_digests):
        if (type(digest_entry) is not tuple or len(digest_entry) != 2
                or type(digest_entry[0]) is not int or digest_entry[0] != expected_slot):
            bad("CodeDirectory special-slot labels are malformed")
        digest = digest_entry[1]
        if expected_slot in (-4, -6):
            if digest is not None or any(state[1]):
                bad("structural-zero special slots are inconsistent")
        elif not is_sha256(digest) or digest != state[1].hex():
            bad("CodeDirectory special-slot digest differs from retained slot bytes")
    requirements_entry = special_digests[1]
    if (source.requirements_blob_sha256 != requirements_entry[1]
            or source.requirements_blob_sha256 != slots[1][1].hex()):
        bad("Requirements digest differs from retained special-slot values")

    return _ParsedSignedImageProjection(
        source=source,
        measured_primitive=measured_primitive,
        source_application=source.source_application,
        repository_context=source.repository_context,
        generation_identity=source.generation_identity,
        executable_code_region_bytes=source.executable_code_region_bytes,
        info_plist_bytes=source.info_plist_bytes,
        code_resources_bytes=source.code_resources_bytes,
        superblob_index_bytes=source.superblob_index_bytes,
        code_directory_bytes=source.code_directory_bytes,
        entitlements_blob_bytes=source.entitlements_blob_bytes,
        der_entitlements_blob_bytes=source.der_entitlements_blob_bytes,
        requirements_blob_sha256=source.requirements_blob_sha256,
        cms_signature_blob_sha256=source.cms_signature_blob_sha256,
        special_slot_state=source.special_slot_state,
        code_directory_identity=source.code_directory_identity,
    )


_IDENTITY_MEMBERS = {
    "executable_code_region": "executable-code-region.bin",
    "info_plist": "Info.plist",
    "code_resources": "CodeResources",
    "superblob_index": "superblob-index.bin",
    "code_directory": "CodeDirectory",
    "entitlements_blob": "Entitlements.blob",
    "der_entitlements_blob": "DER-Entitlements.blob",
    "identity": "identity.json",
}
_IDENTITY_SOURCE_MAPPING = {
    "executable_code_region": "Contents/MacOS/StageBSandboxRunner@[0,codeLimit)",
    "info_plist": "Contents/Info.plist",
    "code_resources": "Contents/_CodeSignature/CodeResources",
    "superblob_index": "Contents/MacOS/StageBSandboxRunner@LC_CODE_SIGNATURE.dataoff[0,52)",
    "code_directory": "LC_CODE_SIGNATURE.superblob.type=CodeDirectory",
    "entitlements_blob": "LC_CODE_SIGNATURE.superblob.type=Entitlements",
    "der_entitlements_blob": "LC_CODE_SIGNATURE.superblob.type=DER-Entitlements",
    "identity": "S9/identity.json",
}
_IDENTITY_TOP_KEYS = frozenset({
    "schema_version", "members", "source_member_mapping", "code_directory_identity",
    "requirements_blob_sha256", "cms_signature_blob_sha256", "n4a_boundary_primitive",
})
_CODE_DIRECTORY_KEYS = frozenset({
    "sha256", "code_limit", "page_size", "code_slot_sha256", "special_slot_sha256",
})
_PRIMITIVE_KEYS = frozenset({
    "format", "renderer_input_sha256", "renderer_input_octets",
    "signer_entitlements_sha256", "signer_entitlements_octets",
})


def _identity_object(value: object, expected_keys: frozenset[str], label: str) -> dict:
    """Validate a closed JSON object, preserving pair sequences to detect duplicates."""
    if type(value) is dict:
        pairs = tuple(value.items())
    elif type(value) is tuple and all(
            type(pair) is tuple and len(pair) == 2 for pair in value):
        pairs = value
    else:
        raise _fail(f"NOT_OBSERVED: identity {label} is not an object")
    result = {}
    for key, item in pairs:
        if type(key) is not str or key in result:
            raise _fail(f"NOT_OBSERVED: identity {label} has an invalid or duplicate key")
        result[key] = item
    if frozenset(result) != expected_keys:
        raise _fail(f"NOT_OBSERVED: identity {label} has an open or incomplete schema")
    return result


def _valid_sha256(value: object) -> bool:
    return (type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value))


def _validated_identity_document(document: object) -> dict:
    top = _identity_object(document, _IDENTITY_TOP_KEYS, "document")
    if type(top["schema_version"]) is not str or top["schema_version"] != "G0_S9_IDENTITY_V1":
        raise _fail("NOT_OBSERVED: identity schema version is invalid")

    for name, expected in (("members", _IDENTITY_MEMBERS),
                           ("source_member_mapping", _IDENTITY_SOURCE_MAPPING)):
        actual = _identity_object(top[name], frozenset(expected), name)
        if any(type(actual[key]) is not str or actual[key] != item
               for key, item in expected.items()):
            raise _fail(f"NOT_OBSERVED: identity {name} values are invalid")
        top[name] = actual

    cd = _identity_object(top["code_directory_identity"], _CODE_DIRECTORY_KEYS,
                          "code_directory_identity")
    if (not _valid_sha256(cd["sha256"])
            or type(cd["code_limit"]) is not int or cd["code_limit"] <= 0
            or type(cd["page_size"]) is not int or cd["page_size"] <= 0):
        raise _fail("NOT_OBSERVED: identity CodeDirectory scalar fields are invalid")
    code_slots = cd["code_slot_sha256"]
    if type(code_slots) is not list or not code_slots or any(
            not _valid_sha256(value) for value in code_slots):
        raise _fail("NOT_OBSERVED: identity CodeDirectory code slots are invalid")
    if len(code_slots) != (cd["code_limit"] + cd["page_size"] - 1) // cd["page_size"]:
        raise _fail("NOT_OBSERVED: identity CodeDirectory code-slot count is inconsistent")
    special_slots = cd["special_slot_sha256"]
    if type(special_slots) is not list or len(special_slots) != 7:
        raise _fail("NOT_OBSERVED: identity CodeDirectory special slots are invalid")
    normalized_special = []
    for expected_slot, entry in zip(range(-1, -8, -1), special_slots):
        pair = _identity_object(entry, frozenset({"slot", "sha256"}),
                                "special_slot_sha256 entry")
        digest = pair["sha256"]
        if (type(pair["slot"]) is not int or pair["slot"] != expected_slot
                or (expected_slot in (-4, -6) and digest is not None)
                or (expected_slot not in (-4, -6) and not _valid_sha256(digest))):
            raise _fail("NOT_OBSERVED: identity CodeDirectory special slot is malformed")
        normalized_special.append(pair)
    cd["code_slot_sha256"] = code_slots
    cd["special_slot_sha256"] = normalized_special
    top["code_directory_identity"] = cd

    requirements_digest = top["requirements_blob_sha256"]
    cms_digest = top["cms_signature_blob_sha256"]
    if (not _valid_sha256(requirements_digest) or not _valid_sha256(cms_digest)
            or requirements_digest != normalized_special[1]["sha256"]):
        raise _fail("NOT_OBSERVED: identity elided digest fields are invalid")

    primitive = _identity_object(top["n4a_boundary_primitive"], _PRIMITIVE_KEYS,
                                 "n4a_boundary_primitive")
    if (type(primitive["format"]) is not str
            or primitive["format"] != "N4A_BOUNDARY_PRIMITIVE_V1"
            or not _valid_sha256(primitive["renderer_input_sha256"])
            or type(primitive["renderer_input_octets"]) is not int
            or primitive["renderer_input_octets"] < 0
            or not _valid_sha256(primitive["signer_entitlements_sha256"])
            or type(primitive["signer_entitlements_octets"]) is not int
            or primitive["signer_entitlements_octets"] < 0):
        raise _fail("NOT_OBSERVED: identity N4A primitive fields are invalid")
    top["n4a_boundary_primitive"] = primitive
    return top


def _sort_identity_value(value: object) -> object:
    if type(value) is dict:
        return {
            key: _sort_identity_value(value[key])
            for key in sorted(value, key=lambda item: item.encode("utf-8"))
        }
    if type(value) is list:
        return [_sort_identity_value(item) for item in value]
    return value


def _serialize_canonical_identity_json(document: object) -> bytes:
    """Validate and serialize the frozen closed identity schema canonically."""
    validated = _validated_identity_document(document)
    try:
        return json.dumps(
            _sort_identity_value(validated), ensure_ascii=False, allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise _fail("NOT_OBSERVED: identity document cannot be serialized") from exc


def project_signed_image(
        source: VerifiedSignedImageProjectionSource,
        measured_primitive: N4ABoundaryPrimitive,
) -> SignedImageProjection:
    """Materialize Task-5 projection from the already validated Task-4 handoff."""
    parsed = _parse_signed_image_projection_source(source, measured_primitive)
    identity = parsed.code_directory_identity
    primitive = parsed.measured_primitive
    document = {
        "schema_version": "G0_S9_IDENTITY_V1",
        "members": dict(_IDENTITY_MEMBERS),
        "source_member_mapping": dict(_IDENTITY_SOURCE_MAPPING),
        "code_directory_identity": {
            "sha256": identity.sha256,
            "code_limit": identity.code_limit,
            "page_size": identity.page_size,
            "code_slot_sha256": list(identity.code_slot_sha256),
            "special_slot_sha256": [
                {"slot": slot, "sha256": digest}
                for slot, digest in identity.special_slot_sha256
            ],
        },
        "requirements_blob_sha256": parsed.requirements_blob_sha256,
        "cms_signature_blob_sha256": parsed.cms_signature_blob_sha256,
        "n4a_boundary_primitive": {
            "format": primitive.format,
            "renderer_input_sha256": primitive.renderer_input_sha256,
            "renderer_input_octets": primitive.renderer_input_octets,
            "signer_entitlements_sha256": primitive.signer_entitlements_sha256,
            "signer_entitlements_octets": primitive.signer_entitlements_octets,
        },
    }
    canonical_identity = _serialize_canonical_identity_json(document)
    return SignedImageProjection(
        executable_code_region_bytes=parsed.executable_code_region_bytes,
        info_plist_bytes=parsed.info_plist_bytes,
        code_resources_bytes=parsed.code_resources_bytes,
        superblob_index_bytes=parsed.superblob_index_bytes,
        code_directory_bytes=parsed.code_directory_bytes,
        entitlements_blob_bytes=parsed.entitlements_blob_bytes,
        der_entitlements_blob_bytes=parsed.der_entitlements_blob_bytes,
        requirements_blob_sha256=parsed.requirements_blob_sha256,
        cms_signature_blob_sha256=parsed.cms_signature_blob_sha256,
        special_slot_state=parsed.special_slot_state,
        signing_time_stable_code_directory_identity=parsed.code_directory_identity,
        canonical_identity_json_bytes=canonical_identity,
    )
