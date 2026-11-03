"""Gate-0 Revision-18 project-owned closed Mach-O native-container parser.

This module implements the frozen Revision-18 specification tables:

* ``TABLE-MACHO-CONTAINER-SLICE-POLICY`` -- first-four-byte container classification;
* ``TABLE-MACHO-HEADER64-V1`` -- the only supported thin encoding and header layout;
* the complete supported FAT outer grammar;
* ``TABLE-MACHO-LOAD-COMMAND-POLICY`` -- the closed 54-row numeric command policy;
* ``TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1`` -- the 43 accepted structural rows.

The parser is bytes-only and purely mathematical.  It performs no host inspection,
spawns no process, loads no external parser and never consults ``otool`` or
``/usr/bin/file``.  All validation arithmetic is carried out on mathematical
non-negative integers after fixed-width decode, so native machine-word overflow
never participates in validity.

Every deviation from the closed grammar fails closed.  The single failure surface
is :class:`EvidenceDagError` carrying ``DEPENDENCY_INVENTORY_DERIVATION_INVALID``.
"""
from __future__ import annotations

from gate0.feasibility.macos_stage_b_evidence_constants import (
    EvidenceDagError,
    EvidenceFailureCode,
    LoadCommandDisposition,
    MachOHeader64,
    ParsedLoadCommand,
    ParsedMachO,
)

__all__ = [
    "MACHO_CONTAINER_SLICE_POLICY_V1",
    "MACHO_HEADER64_SIZE_V1",
    "MACHO_LOAD_COMMAND_POLICY_V1",
    "MACHO_LOAD_COMMAND_STRUCTURE_V1",
    "MACHO_CPU_TYPE_ARM64",
    "MACHO_CPU_SUBTYPE_ARM64_ALLOWED",
    "MACHO_SUPPORTED_THIN_MAGIC",
    "MACHO_SUPPORTED_FAT_MAGICS",
    "MACHO_LOAD_COMMAND_REGION_START_V1",
    "MACHO_LOAD_COMMANDS_ARE_CLOSED",
    "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "macho_container_slice_disposition",
]

# --------------------------------------------------------------------------
# Container / slice policy (TABLE-MACHO-CONTAINER-SLICE-POLICY)
# --------------------------------------------------------------------------

MACHO_CONTAINER_SLICE_POLICY_V1: tuple[tuple[bytes, str, str], ...] = (
    (b"\xcf\xfa\xed\xfe", "MH_MAGIC_64", "SUPPORTED"),
    (b"\xfe\xed\xfa\xcf", "MH_CIGAM_64", "REJECT_UNSUPPORTED"),
    (b"\xce\xfa\xed\xfe", "MH_MAGIC", "REJECT_UNSUPPORTED"),
    (b"\xfe\xed\xfa\xce", "MH_CIGAM", "REJECT_UNSUPPORTED"),
    (b"\xca\xfe\xba\xbe", "FAT_MAGIC", "SUPPORTED"),
    (b"\xbe\xba\xfe\xca", "FAT_CIGAM", "REJECT_UNSUPPORTED"),
    (b"\xca\xfe\xba\xbf", "FAT_MAGIC_64", "SUPPORTED"),
    (b"\xbf\xba\xfe\xca", "FAT_CIGAM_64", "REJECT_UNSUPPORTED"),
)

MACHO_SUPPORTED_THIN_MAGIC = b"\xcf\xfa\xed\xfe"
MACHO_SUPPORTED_FAT_MAGICS = (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf")

MACHO_HEADER64_SIZE_V1 = 32
MACHO_LOAD_COMMAND_REGION_START_V1 = MACHO_HEADER64_SIZE_V1

MACHO_MAGIC_64 = 0xFEEDFACF
MACHO_CPU_TYPE_ARM64 = 0x0100000C
MACHO_CPU_SUBTYPE_ARM64_ALLOWED = (0, 1)

#: The command walk is closed: no unlisted numeric value may ever be admitted.
MACHO_LOAD_COMMANDS_ARE_CLOSED = True

_FAILURE = EvidenceFailureCode.DEPENDENCY_INVENTORY_DERIVATION_INVALID


def _fail(detail: str) -> "EvidenceDagError":
    return EvidenceDagError(_FAILURE, detail)


# --------------------------------------------------------------------------
# Numeric load-command policy (TABLE-MACHO-LOAD-COMMAND-POLICY)
# --------------------------------------------------------------------------

_DEPENDENCY_EDGE = LoadCommandDisposition.DEPENDENCY_EDGE
_SUPPORTED_NONEDGE = LoadCommandDisposition.SUPPORTED_NONEDGE
_REJECT_UNSUPPORTED = LoadCommandDisposition.REJECT_UNSUPPORTED


def _policy_row(value: int, name: str, disposition: LoadCommandDisposition):
    return value, name, disposition


MACHO_LOAD_COMMAND_POLICY_V1: tuple[tuple[int, str, LoadCommandDisposition], ...] = (
    _policy_row(0x00000001, "LC_SEGMENT", _SUPPORTED_NONEDGE),
    _policy_row(0x00000002, "LC_SYMTAB", _SUPPORTED_NONEDGE),
    _policy_row(0x00000003, "LC_SYMSEG", _SUPPORTED_NONEDGE),
    _policy_row(0x00000004, "LC_THREAD", _SUPPORTED_NONEDGE),
    _policy_row(0x00000005, "LC_UNIXTHREAD", _SUPPORTED_NONEDGE),
    _policy_row(0x00000006, "LC_LOADFVMLIB", _REJECT_UNSUPPORTED),
    _policy_row(0x00000007, "LC_IDFVMLIB", _REJECT_UNSUPPORTED),
    _policy_row(0x00000008, "LC_IDENT", _SUPPORTED_NONEDGE),
    _policy_row(0x00000009, "LC_FVMFILE", _REJECT_UNSUPPORTED),
    _policy_row(0x0000000A, "LC_PREPAGE", _REJECT_UNSUPPORTED),
    _policy_row(0x0000000B, "LC_DYSYMTAB", _SUPPORTED_NONEDGE),
    _policy_row(0x0000000C, "LC_LOAD_DYLIB", _DEPENDENCY_EDGE),
    _policy_row(0x0000000D, "LC_ID_DYLIB", _SUPPORTED_NONEDGE),
    _policy_row(0x0000000E, "LC_LOAD_DYLINKER", _SUPPORTED_NONEDGE),
    _policy_row(0x0000000F, "LC_ID_DYLINKER", _SUPPORTED_NONEDGE),
    _policy_row(0x00000010, "LC_PREBOUND_DYLIB", _REJECT_UNSUPPORTED),
    _policy_row(0x00000011, "LC_ROUTINES", _SUPPORTED_NONEDGE),
    _policy_row(0x00000012, "LC_SUB_FRAMEWORK", _REJECT_UNSUPPORTED),
    _policy_row(0x00000013, "LC_SUB_UMBRELLA", _REJECT_UNSUPPORTED),
    _policy_row(0x00000014, "LC_SUB_CLIENT", _REJECT_UNSUPPORTED),
    _policy_row(0x00000015, "LC_SUB_LIBRARY", _REJECT_UNSUPPORTED),
    _policy_row(0x00000016, "LC_TWOLEVEL_HINTS", _SUPPORTED_NONEDGE),
    _policy_row(0x00000017, "LC_PREBIND_CKSUM", _SUPPORTED_NONEDGE),
    _policy_row(0x80000018, "LC_LOAD_WEAK_DYLIB", _DEPENDENCY_EDGE),
    _policy_row(0x00000019, "LC_SEGMENT_64", _SUPPORTED_NONEDGE),
    _policy_row(0x0000001A, "LC_ROUTINES_64", _SUPPORTED_NONEDGE),
    _policy_row(0x0000001B, "LC_UUID", _SUPPORTED_NONEDGE),
    _policy_row(0x8000001C, "LC_RPATH", _SUPPORTED_NONEDGE),
    _policy_row(0x0000001D, "LC_CODE_SIGNATURE", _SUPPORTED_NONEDGE),
    _policy_row(0x0000001E, "LC_SEGMENT_SPLIT_INFO", _SUPPORTED_NONEDGE),
    _policy_row(0x8000001F, "LC_REEXPORT_DYLIB", _DEPENDENCY_EDGE),
    _policy_row(0x00000020, "LC_LAZY_LOAD_DYLIB", _DEPENDENCY_EDGE),
    _policy_row(0x00000021, "LC_ENCRYPTION_INFO", _SUPPORTED_NONEDGE),
    _policy_row(0x00000022, "LC_DYLD_INFO", _SUPPORTED_NONEDGE),
    _policy_row(0x80000022, "LC_DYLD_INFO_ONLY", _SUPPORTED_NONEDGE),
    _policy_row(0x80000023, "LC_LOAD_UPWARD_DYLIB", _DEPENDENCY_EDGE),
    _policy_row(0x00000024, "LC_VERSION_MIN_MACOSX", _SUPPORTED_NONEDGE),
    _policy_row(0x00000025, "LC_VERSION_MIN_IPHONEOS", _SUPPORTED_NONEDGE),
    _policy_row(0x00000026, "LC_FUNCTION_STARTS", _SUPPORTED_NONEDGE),
    _policy_row(0x00000027, "LC_DYLD_ENVIRONMENT", _REJECT_UNSUPPORTED),
    _policy_row(0x80000028, "LC_MAIN", _SUPPORTED_NONEDGE),
    _policy_row(0x00000029, "LC_DATA_IN_CODE", _SUPPORTED_NONEDGE),
    _policy_row(0x0000002A, "LC_SOURCE_VERSION", _SUPPORTED_NONEDGE),
    _policy_row(0x0000002B, "LC_DYLIB_CODE_SIGN_DRS", _SUPPORTED_NONEDGE),
    _policy_row(0x0000002C, "LC_ENCRYPTION_INFO_64", _SUPPORTED_NONEDGE),
    _policy_row(0x0000002D, "LC_LINKER_OPTION", _SUPPORTED_NONEDGE),
    _policy_row(0x0000002E, "LC_LINKER_OPTIMIZATION_HINT", _SUPPORTED_NONEDGE),
    _policy_row(0x0000002F, "LC_VERSION_MIN_TVOS", _SUPPORTED_NONEDGE),
    _policy_row(0x00000030, "LC_VERSION_MIN_WATCHOS", _SUPPORTED_NONEDGE),
    _policy_row(0x00000031, "LC_NOTE", _SUPPORTED_NONEDGE),
    _policy_row(0x00000032, "LC_BUILD_VERSION", _SUPPORTED_NONEDGE),
    _policy_row(0x80000033, "LC_DYLD_EXPORTS_TRIE", _SUPPORTED_NONEDGE),
    _policy_row(0x80000034, "LC_DYLD_CHAINED_FIXUPS", _SUPPORTED_NONEDGE),
    _policy_row(0x80000035, "LC_FILESET_ENTRY", _REJECT_UNSUPPORTED),
)

_POLICY_BY_VALUE = {row[0]: row for row in MACHO_LOAD_COMMAND_POLICY_V1}


# --------------------------------------------------------------------------
# Accepted-command structural policy (TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1)
# --------------------------------------------------------------------------

class _Row:
    """One accepted structural row, encoded as data rather than as parser branches."""

    __slots__ = (
        "value", "name", "disposition", "fixed_bytes", "formula",
        "reserved_offsets", "string_offset_at", "string_count_at",
        "thread_blocks", "string_table",
    )

    def __init__(
        self, value, name, disposition, fixed_bytes, formula=None,
        reserved_offsets=(), string_offset_at=None, string_count_at=None,
        thread_blocks=False, string_table=False,
    ):
        self.value = value
        self.name = name
        self.disposition = disposition
        self.fixed_bytes = fixed_bytes
        self.formula = formula
        self.reserved_offsets = tuple(reserved_offsets)
        self.string_offset_at = string_offset_at
        self.string_count_at = string_count_at
        self.thread_blocks = thread_blocks
        self.string_table = string_table


def _segments32(nsects):
    return 56 + nsects * 68


def _segments64(nsects):
    return 72 + nsects * 80


def _build_version(ntools):
    return 24 + ntools * 8


def _pad_size(size):
    """Exact command size for a fixed prefix followed only by zero padding."""
    return lambda _count: size


def _row(value, name, disposition, fixed_bytes, **kwargs):
    return value, _Row(value, name, disposition, fixed_bytes, **kwargs)

MACHO_LOAD_COMMAND_STRUCTURE_V1 = dict((
    _row(0x00000001, "LC_SEGMENT", _SUPPORTED_NONEDGE, 56,
         formula=("nsects", 48, 68, _segments32)),
    _row(0x00000002, "LC_SYMTAB", _SUPPORTED_NONEDGE, 24),
    _row(0x00000003, "LC_SYMSEG", _SUPPORTED_NONEDGE, 16),
    _row(0x00000004, "LC_THREAD", _SUPPORTED_NONEDGE, 8, thread_blocks=True),
    _row(0x00000005, "LC_UNIXTHREAD", _SUPPORTED_NONEDGE, 8, thread_blocks=True),
    _row(0x00000008, "LC_IDENT", _SUPPORTED_NONEDGE, 8, string_table=True),
    _row(0x0000000B, "LC_DYSYMTAB", _SUPPORTED_NONEDGE, 80),
    _row(0x0000000C, "LC_LOAD_DYLIB", _DEPENDENCY_EDGE, 24, string_offset_at=8),
    _row(0x0000000D, "LC_ID_DYLIB", _SUPPORTED_NONEDGE, 24, string_offset_at=8),
    _row(0x0000000E, "LC_LOAD_DYLINKER", _SUPPORTED_NONEDGE, 12, string_offset_at=8),
    _row(0x0000000F, "LC_ID_DYLINKER", _SUPPORTED_NONEDGE, 12, string_offset_at=8),
    _row(0x00000011, "LC_ROUTINES", _SUPPORTED_NONEDGE, 40,
         reserved_offsets=tuple(range(16, 40, 4))),
    _row(0x00000016, "LC_TWOLEVEL_HINTS", _SUPPORTED_NONEDGE, 16),
    _row(0x00000017, "LC_PREBIND_CKSUM", _SUPPORTED_NONEDGE, 12,
         formula=(None, None, None, _pad_size(16)), reserved_offsets=(12,)),
    _row(0x80000018, "LC_LOAD_WEAK_DYLIB", _DEPENDENCY_EDGE, 24, string_offset_at=8),
    _row(0x00000019, "LC_SEGMENT_64", _SUPPORTED_NONEDGE, 72,
         formula=("nsects", 64, 80, _segments64)),
    _row(0x0000001A, "LC_ROUTINES_64", _SUPPORTED_NONEDGE, 72,
         reserved_offsets=tuple(range(24, 72, 8))),
    _row(0x0000001B, "LC_UUID", _SUPPORTED_NONEDGE, 24),
    _row(0x8000001C, "LC_RPATH", _SUPPORTED_NONEDGE, 12, string_offset_at=8),
    _row(0x0000001D, "LC_CODE_SIGNATURE", _SUPPORTED_NONEDGE, 16),
    _row(0x0000001E, "LC_SEGMENT_SPLIT_INFO", _SUPPORTED_NONEDGE, 16),
    _row(0x8000001F, "LC_REEXPORT_DYLIB", _DEPENDENCY_EDGE, 24, string_offset_at=8),
    _row(0x00000020, "LC_LAZY_LOAD_DYLIB", _DEPENDENCY_EDGE, 24, string_offset_at=8),
    _row(0x00000021, "LC_ENCRYPTION_INFO", _SUPPORTED_NONEDGE, 20,
         formula=(None, None, None, _pad_size(24)), reserved_offsets=(20,)),
    _row(0x00000022, "LC_DYLD_INFO", _SUPPORTED_NONEDGE, 48),
    _row(0x80000022, "LC_DYLD_INFO_ONLY", _SUPPORTED_NONEDGE, 48),
    _row(0x80000023, "LC_LOAD_UPWARD_DYLIB", _DEPENDENCY_EDGE, 24, string_offset_at=8),
    _row(0x00000024, "LC_VERSION_MIN_MACOSX", _SUPPORTED_NONEDGE, 16),
    _row(0x00000025, "LC_VERSION_MIN_IPHONEOS", _SUPPORTED_NONEDGE, 16),
    _row(0x00000026, "LC_FUNCTION_STARTS", _SUPPORTED_NONEDGE, 16),
    _row(0x80000028, "LC_MAIN", _SUPPORTED_NONEDGE, 24),
    _row(0x00000029, "LC_DATA_IN_CODE", _SUPPORTED_NONEDGE, 16),
    _row(0x0000002A, "LC_SOURCE_VERSION", _SUPPORTED_NONEDGE, 16),
    _row(0x0000002B, "LC_DYLIB_CODE_SIGN_DRS", _SUPPORTED_NONEDGE, 16),
    _row(0x0000002C, "LC_ENCRYPTION_INFO_64", _SUPPORTED_NONEDGE, 24,
         reserved_offsets=(20,)),
    _row(0x0000002D, "LC_LINKER_OPTION", _SUPPORTED_NONEDGE, 12,
         string_count_at=8),
    _row(0x0000002E, "LC_LINKER_OPTIMIZATION_HINT", _SUPPORTED_NONEDGE, 16),
    _row(0x0000002F, "LC_VERSION_MIN_TVOS", _SUPPORTED_NONEDGE, 16),
    _row(0x00000030, "LC_VERSION_MIN_WATCHOS", _SUPPORTED_NONEDGE, 16),
    _row(0x00000031, "LC_NOTE", _SUPPORTED_NONEDGE, 40),
    _row(0x00000032, "LC_BUILD_VERSION", _SUPPORTED_NONEDGE, 24,
         formula=("ntools", 20, 8, _build_version)),
    _row(0x80000033, "LC_DYLD_EXPORTS_TRIE", _SUPPORTED_NONEDGE, 16),
    _row(0x80000034, "LC_DYLD_CHAINED_FIXUPS", _SUPPORTED_NONEDGE, 16),
))

_ACCEPTED_VALUES = frozenset(
    value for value, (_, _, disposition) in _POLICY_BY_VALUE.items()
    if disposition is not _REJECT_UNSUPPORTED
)

# Closed-table invariants.  These are raised as explicit errors rather than left as
# bare ``assert`` statements so that ``python -O`` cannot strip the bijection check.
if _ACCEPTED_VALUES != frozenset(MACHO_LOAD_COMMAND_STRUCTURE_V1):
    raise RuntimeError(
        "accepted policy set and structural table set must be equal")
if len(MACHO_LOAD_COMMAND_POLICY_V1) != 54:
    raise RuntimeError("numeric load-command policy must have exactly 54 rows")
if len(MACHO_LOAD_COMMAND_STRUCTURE_V1) != 43:
    raise RuntimeError("accepted structural policy must have exactly 43 rows")


# --------------------------------------------------------------------------
# Fixed-width decode helpers (mathematical non-negative integers)
# --------------------------------------------------------------------------

def _u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 4], "little")


def _u32_be(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 4], "big")


def _u64_be(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 8], "big")


def macho_container_slice_disposition(first_four: bytes):
    """Classify ``first_four`` against the closed container/slice table.

    Returns the symbolic magic and disposition, or ``(None, 'REJECT_UNSUPPORTED')``
    for an unlisted encoding or when fewer than four bytes are available.
    """
    if len(first_four) < 4:
        return None, "REJECT_UNSUPPORTED"
    for magic_bytes, symbolic, disposition in MACHO_CONTAINER_SLICE_POLICY_V1:
        if first_four[:4] == magic_bytes:
            return symbolic, disposition
    return None, "REJECT_UNSUPPORTED"


# --------------------------------------------------------------------------
# Structural validation of one accepted command
# --------------------------------------------------------------------------

def _validate_string_field(command: bytes, row: _Row, field_offset: int):
    if len(command) < field_offset + 4:
        raise _fail(f"{row.name}: truncated lc_str field")
    declared = _u32(command, field_offset)
    if declared != row.fixed_bytes:
        raise _fail(f"{row.name}: lc_str offset is not exact")
    text = command[row.fixed_bytes:]
    if not text:
        raise _fail(f"{row.name}: declared lc_str payload is absent")
    terminator = text.find(b"\x00")
    if terminator < 0:
        raise _fail(f"{row.name}: missing NUL terminator")
    padding = text[terminator + 1:]
    if any(byte != 0 for byte in padding):
        raise _fail(f"{row.name}: non-zero terminal padding")
    name = text[:terminator]
    if not name:
        raise _fail(f"{row.name}: declared lc_str name is empty")
    try:
        name.decode("utf-8")
    except UnicodeDecodeError:
        raise _fail(f"{row.name}: install name is not lossless UTF-8") from None
    return name


def _validate_thread_blocks(command: bytes, row: _Row):
    offset = 8
    total = len(command)
    while offset < total:
        if offset + 8 > total:
            raise _fail(f"{row.name}: truncated thread block header")
        count = _u32(command, offset + 4)
        block_end = offset + 8 + count * 4
        if block_end > total:
            raise _fail(f"{row.name}: thread block overruns command")
        offset = block_end
    if offset != total:
        raise _fail(f"{row.name}: thread block walk does not end at cmdsize")


def _validate_string_table(command: bytes, row: _Row):
    payload = command[row.fixed_bytes:]
    if not payload:
        # The optional bounded string table is absent: the normative law permits an
        # IDENT command that is exactly its 8-byte prefix.
        return
    if payload[-1] != 0:
        raise _fail(f"{row.name}: string table does not end in NUL")
    for entry in payload.split(b"\x00")[:-1]:
        try:
            entry.decode("utf-8")
        except UnicodeDecodeError:
            raise _fail(f"{row.name}: string table entry is not lossless UTF-8") from None


def _validate_linker_options(command: bytes, row: _Row):
    count = _u32(command, row.string_count_at)
    offset = row.fixed_bytes
    for _ in range(count):
        terminator = command.find(b"\x00", offset)
        if terminator < 0:
            raise _fail(f"{row.name}: linker option string is unterminated")
        try:
            command[offset:terminator].decode("utf-8")
        except UnicodeDecodeError:
            raise _fail(f"{row.name}: linker option is not lossless UTF-8") from None
        offset = terminator + 1
    if any(byte != 0 for byte in command[offset:]):
        raise _fail(f"{row.name}: linker option terminal padding is not zero")


def _validate_formula(command: bytes, row: _Row):
    field_name, count_offset, item_size, formula = row.formula
    count = 0 if count_offset is None else _u32(command, count_offset)
    if len(command) != formula(count):
        raise _fail(f"{row.name}: cmdsize does not equal the exact {field_name} formula")


def _validate_structure(command: bytes, value: int):
    row = MACHO_LOAD_COMMAND_STRUCTURE_V1.get(value)
    if row is None:
        raise _fail("command is not an accepted structural row")
    if len(command) != _u32(command, 4):
        raise _fail(f"{row.name}: declared cmdsize differs from supplied length")
    if row.string_offset_at is not None:
        # Variable-length row with an exact fixed prefix: only a declared minimum,
        # never an exact fixed size.  The lc_str offset itself is exact.
        if len(command) < row.fixed_bytes:
            raise _fail(f"{row.name}: cmdsize is below the exact fixed prefix")
    elif row.string_count_at is not None:
        if len(command) < row.fixed_bytes:
            raise _fail(f"{row.name}: cmdsize is below the exact fixed prefix")
    elif row.thread_blocks:
        if len(command) < row.fixed_bytes:
            raise _fail(f"{row.name}: cmdsize is below the exact fixed prefix")
    elif row.string_table:
        if len(command) < row.fixed_bytes:
            raise _fail(f"{row.name}: cmdsize is below the exact fixed prefix")
    elif row.formula is not None:
        _validate_formula(command, row)
    elif len(command) != row.fixed_bytes:
        raise _fail(f"{row.name}: cmdsize is not the exact fixed size")
    for offset in row.reserved_offsets:
        if _u32(command, offset) != 0:
            raise _fail(f"{row.name}: project-reserved field is non-zero")
    if row.string_offset_at is not None:
        return _validate_string_field(command, row, row.string_offset_at)
    if row.thread_blocks:
        _validate_thread_blocks(command, row)
    if row.string_table:
        _validate_string_table(command, row)
    if row.string_count_at is not None:
        _validate_linker_options(command, row)
    return None


# --------------------------------------------------------------------------
# Header64 and FAT grammar
# --------------------------------------------------------------------------

def _parse_header64(slice_bytes: bytes) -> MachOHeader64:
    if len(slice_bytes) < MACHO_HEADER64_SIZE_V1:
        raise _fail("selected slice is shorter than the 32-byte Header64")
    header = MachOHeader64(
        magic=_u32(slice_bytes, 0),
        cputype=_u32(slice_bytes, 4),
        cpusubtype=_u32(slice_bytes, 8),
        filetype=_u32(slice_bytes, 12),
        ncmds=_u32(slice_bytes, 16),
        sizeofcmds=_u32(slice_bytes, 20),
        flags=_u32(slice_bytes, 24),
        reserved=_u32(slice_bytes, 28),
    )
    if header.magic != MACHO_MAGIC_64:
        raise _fail("header magic is not MH_MAGIC_64")
    if header.cputype != MACHO_CPU_TYPE_ARM64:
        raise _fail("header cputype is not CPU_TYPE_ARM64")
    if header.cpusubtype not in MACHO_CPU_SUBTYPE_ARM64_ALLOWED:
        raise _fail("header cpusubtype is not an allowed ARM64 subtype")
    region_end = MACHO_LOAD_COMMAND_REGION_START_V1 + header.sizeofcmds
    if region_end > len(slice_bytes):
        raise _fail("declared command region exceeds the selected slice")
    return header


def _walk_commands(slice_bytes: bytes, header: MachOHeader64):
    region_start = MACHO_LOAD_COMMAND_REGION_START_V1
    region_end = region_start + header.sizeofcmds
    offset = region_start
    commands: list[ParsedLoadCommand] = []
    edges: list[bytes] = []
    for _ in range(header.ncmds):
        if offset + 8 > region_end:
            raise _fail("command prefix overruns the declared command region")
        value = _u32(slice_bytes, offset)
        size = _u32(slice_bytes, offset + 4)
        if size < 8:
            raise _fail("cmdsize is below the 8-byte command prefix")
        if size % 8 != 0:
            raise _fail("cmdsize is not a multiple of 8")
        if offset + size > region_end:
            raise _fail("command interval overruns the declared command region")
        policy = _POLICY_BY_VALUE.get(value)
        if policy is None or policy[2] is _REJECT_UNSUPPORTED:
            raise _fail("command numeric value is not supported")
        command = slice_bytes[offset:offset + size]
        name = _validate_structure(command, value)
        install_name = name if policy[2] is _DEPENDENCY_EDGE else None
        rpath_value = name if value == 0x8000001C else None
        commands.append(ParsedLoadCommand(
            command_value=value,
            command_size=size,
            disposition=policy[2],
            dependency_install_name=install_name,
            rpath_value=rpath_value,
        ))
        if install_name is not None:
            edges.append(install_name)
        offset += size
    if offset != region_end:
        raise _fail("command walk did not consume exactly sizeofcmds bytes")
    return tuple(commands), tuple(edges)


def _select_fat_slice(data: bytes):
    magic = data[:4]
    is_fat64 = magic == b"\xca\xfe\xba\xbf"
    entry_size = 32 if is_fat64 else 20
    if len(data) < 8:
        raise _fail("FAT header is truncated")
    nfat_arch = _u32_be(data, 4)
    if nfat_arch < 1:
        raise _fail("FAT nfat_arch must be at least one")
    metadata_end = 8 + nfat_arch * entry_size
    file_length = len(data)
    if metadata_end > file_length:
        raise _fail("FAT architecture table exceeds the file length")
    ranges = []
    selected = []
    for index in range(nfat_arch):
        base = 8 + index * entry_size
        cputype = _u32_be(data, base)
        cpusubtype = _u32_be(data, base + 4)
        if is_fat64:
            offset = _u64_be(data, base + 8)
            size = _u64_be(data, base + 16)
            align = _u32_be(data, base + 24)
            reserved = _u32_be(data, base + 28)
            if reserved != 0:
                raise _fail("FAT64 entry reserved field is non-zero")
        else:
            offset = _u32_be(data, base + 8)
            size = _u32_be(data, base + 12)
            align = _u32_be(data, base + 16)
        if size == 0:
            raise _fail("FAT slice size must be positive")
        if offset < metadata_end:
            raise _fail("FAT slice offset precedes the architecture table")
        if offset + size > file_length:
            raise _fail("FAT slice range exceeds the file length")
        if align > 63:
            raise _fail("FAT align field exceeds 63")
        if offset % (1 << align) != 0:
            raise _fail("FAT slice offset violates its declared alignment")
        ranges.append((offset, offset + size))
        if cputype == MACHO_CPU_TYPE_ARM64:
            selected.append((index, cpusubtype, offset, size))
    for i in range(len(ranges)):
        for j in range(i + 1, len(ranges)):
            low_a, high_a = ranges[i]
            low_b, high_b = ranges[j]
            if low_a < high_b and low_b < high_a:
                raise _fail("FAT slice ranges overlap")
    allowed = [entry for entry in selected if entry[1] in MACHO_CPU_SUBTYPE_ARM64_ALLOWED]
    if len(allowed) != 1:
        raise _fail("exactly one allowed ARM64 slice is required")
    _, subtype, offset, size = allowed[0]
    inner = data[offset:offset + size]
    header = _parse_header64(inner)
    if header.cputype != MACHO_CPU_TYPE_ARM64 or header.cpusubtype != subtype:
        raise _fail("selected slice inner CPU identity differs from its FAT entry")
    return offset, size, inner, header


def MACHO_NATIVE_CONTAINER_PARSE_V1(data: bytes) -> ParsedMachO:
    """Parse a native container under the closed Revision-18 project grammar.

    Raises :class:`EvidenceDagError` carrying
    ``DEPENDENCY_INVENTORY_DERIVATION_INVALID`` for every malformed, unsupported
    or unlisted input.  A subject is never the ordinary ``NON_NATIVE`` case here:
    reaching this entry means the subject was already classified native.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise _fail("native parser input must be an immutable byte image")
    data = bytes(data)
    if len(data) < 4:
        raise _fail("fewer than four bytes available at the native parser entry")
    magic = data[:4]
    if magic == MACHO_SUPPORTED_THIN_MAGIC:
        header = _parse_header64(data)
        commands, edges = _walk_commands(data, header)
        return ParsedMachO(
            selected_slice_offset=0,
            selected_slice_length=len(data),
            header=header,
            load_commands=commands,
            dependency_edges=edges,
        )
    if magic in MACHO_SUPPORTED_FAT_MAGICS:
        offset, size, inner, header = _select_fat_slice(data)
        commands, edges = _walk_commands(inner, header)
        return ParsedMachO(
            selected_slice_offset=offset,
            selected_slice_length=size,
            header=header,
            load_commands=commands,
            dependency_edges=edges,
        )
    raise _fail("first four bytes are not a supported container encoding")
