"""Shared synthetic-only primitives, canonical JSON helpers, and readiness models.

Packet P00 — Shared Infrastructure (LAB-MEGA-03-07-v1.1.0).

Invariants enforced here:
- Canonical JSON serialization rejects non-string mapping keys, NaN/Infinity,
  and non-JSON types; emits sorted keys with compact separators ``(",", ":")``.
- Strict JSON parsing rejects duplicate object keys, NaN/Infinity constants,
  and inputs exceeding ``MAX_LAB_JSON_BYTES`` (2 MiB default).
- File loading uses ``os.O_NOFOLLOW`` where available, verifies regular-file
  status via ``os.fstat``, and bounds reads to ``max_bytes + 1`` bytes.
- ``SyntheticContextMarker`` is a closed synthetic-only runtime marker. External
  JSON inputs claiming ``trusted=True``, ``approved=True``, ``authentic=True``,
  ``owner_signed=True``, or ``production_ready=True`` never escalate synthetic
  lab evaluations into owner-authorized or authentic execution states.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import os
from pathlib import Path
import stat
from typing import Any, Mapping, Sequence


LAB_PROGRAM_VERSION = "LAB-MEGA-03-07-v1.1.0"
SYNTHETIC_CONTEXT_TOKEN = "VIP_LAB_SYNTHETIC_ONLY_V1"
MAX_LAB_JSON_BYTES = 2 * 1024 * 1024  # 2 MiB hard ceiling for lab preflight JSON

CANONICAL_EVIDENCE_CLASSES = frozenset(
    {
        "MEASURED",
        "MATCHED",
        "VISUALLY_OBSERVED",
        "AUDIO_OBSERVED",
        "EDITORIAL_INFERENCE",
    }
)
NOT_OBSERVED = "NOT_OBSERVED"

FORBIDDEN_EXTERNAL_AUTHORITY_KEYS = frozenset(
    {
        "trusted",
        "approved",
        "authentic",
        "owner_signed",
        "owner_approved",
        "production_authorized",
        "gate_approved",
        "execution_authorized",
    }
)


class VipLabError(ValueError):
    """Structured fail-closed error raised by vip_lab preflight helpers."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        field_path: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        if not isinstance(code, str) or not code.strip():
            raise ValueError("VipLabError requires a non-empty error code")
        super().__init__(f"{code}: {message}")
        self.code = code.strip()
        self.message = message
        self.field_path = field_path
        self.details = dict(details) if details is not None else {}

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.field_path is not None:
            payload["field_path"] = self.field_path
        if self.details:
            payload["details"] = dict(self.details)
        return payload


class ReadinessStatus(str, Enum):
    """Closed readiness status enumeration for synthetic lab packets."""

    READY_SYNTHETIC = "READY_SYNTHETIC"
    BLOCKED = "BLOCKED"
    NOT_OBSERVED = "NOT_OBSERVED"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    INVALID = "INVALID"


_FINAL_SYNTHETIC_MARK = object()


@dataclass(frozen=True)
class SyntheticContextMarker:
    """Closed synthetic-context capability marker that cannot be forged from JSON."""

    token: str = SYNTHETIC_CONTEXT_TOKEN
    synthetic_only: bool = True
    authentic_authority_granted: bool = False
    _seal: object = field(default=_FINAL_SYNTHETIC_MARK, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._seal is not _FINAL_SYNTHETIC_MARK:
            raise VipLabError(
                "LAB_FORGED_CONTEXT_MARKER",
                "SyntheticContextMarker must be constructed through SyntheticContextMarker.create()",
            )
        if self.token != SYNTHETIC_CONTEXT_TOKEN or self.synthetic_only is not True:
            raise VipLabError(
                "LAB_INVALID_CONTEXT_MARKER",
                "SyntheticContextMarker must remain synthetic_only=True with canonical token",
            )
        if self.authentic_authority_granted is not False:
            raise VipLabError(
                "LAB_AUTHORITY_ESCALATION_FORBIDDEN",
                "SyntheticContextMarker can never grant authentic execution or owner authority",
            )

    @classmethod
    def create(cls) -> "SyntheticContextMarker":
        return cls(
            token=SYNTHETIC_CONTEXT_TOKEN,
            synthetic_only=True,
            authentic_authority_granted=False,
            _seal=_FINAL_SYNTHETIC_MARK,
        )


def _validate_canonical_value(value: Any, path: str = "$") -> Any:
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise VipLabError(
                "LAB_NONFINITE_NUMBER",
                f"Non-finite float is forbidden in canonical JSON at {path}",
                field_path=path,
            )
        return value
    if isinstance(value, Enum):
        return _validate_canonical_value(value.value, path)
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise VipLabError(
                    "LAB_NONSTRING_JSON_KEY",
                    f"JSON object keys must be strings at {path} (got {type(k).__name__})",
                    field_path=path,
                )
            normalized[k] = _validate_canonical_value(v, f"{path}.{k}")
        return normalized
    if isinstance(value, (list, tuple)):
        return [
            _validate_canonical_value(item, f"{path}[{idx}]")
            for idx, item in enumerate(value)
        ]
    raise VipLabError(
        "LAB_UNSERIALIZABLE_JSON_VALUE",
        f"Unsupported type {type(value).__name__} in canonical JSON at {path}",
        field_path=path,
    )


def canonical_json_dumps(value: Any) -> str:
    """Serialize ``value`` into deterministic UTF-8 JSON with sorted keys."""
    validated = _validate_canonical_value(value)
    return json.dumps(
        validated,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return canonical UTF-8 JSON bytes for ``value``."""
    return canonical_json_dumps(value).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    """Return lowercase 64-hex SHA-256 over canonical UTF-8 JSON bytes of ``value``."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _reject_duplicate_object_pairs(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, val in pairs:
        if not isinstance(key, str):
            raise VipLabError("LAB_NONSTRING_JSON_KEY", "JSON object key must be str")
        if key in result:
            raise VipLabError(
                "LAB_DUPLICATE_JSON_KEY",
                f"Duplicate JSON object key {key!r} is forbidden",
                field_path=key,
            )
        result[key] = val
    return result


def _reject_parse_constant(constant: str) -> Any:
    raise VipLabError(
        "LAB_NONFINITE_JSON_CONSTANT",
        f"Non-standard JSON constant {constant!r} is forbidden",
    )


def parse_strict_json_text(
    text: str,
    *,
    max_bytes: int = MAX_LAB_JSON_BYTES,
    require_mapping: bool = True,
) -> Any:
    """Parse JSON text strictly, rejecting duplicate keys, NaN/Infinity, and oversized inputs."""
    if not isinstance(text, str):
        raise VipLabError("LAB_JSON_TYPE_ERROR", "JSON input must be a string")
    raw = text.encode("utf-8")
    return parse_strict_json_bytes(
        raw, max_bytes=max_bytes, require_mapping=require_mapping
    )


def parse_strict_json_bytes(
    raw: bytes,
    *,
    max_bytes: int = MAX_LAB_JSON_BYTES,
    require_mapping: bool = True,
) -> Any:
    """Parse UTF-8 JSON bytes strictly with size cap and duplicate-key rejection."""
    if not isinstance(raw, (bytes, bytearray, memoryview)):
        raise VipLabError("LAB_JSON_BYTES_ERROR", "JSON byte input must be bytes-like")
    data = bytes(raw)
    if max_bytes <= 0:
        raise VipLabError("LAB_INVALID_BYTE_LIMIT", "max_bytes must be positive")
    if len(data) > max_bytes:
        raise VipLabError(
            "LAB_JSON_SIZE_EXCEEDED",
            f"JSON input of {len(data)} bytes exceeds limit of {max_bytes} bytes",
            details={"observed_bytes": len(data), "max_bytes": max_bytes},
        )
    try:
        decoded_text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VipLabError(
            "LAB_JSON_UTF8_ERROR",
            f"Invalid UTF-8 in JSON payload: {exc}",
        ) from exc

    try:
        parsed = json.loads(
            decoded_text,
            object_pairs_hook=_reject_duplicate_object_pairs,
            parse_constant=_reject_parse_constant,
        )
    except VipLabError:
        raise
    except json.JSONDecodeError as exc:
        raise VipLabError(
            "LAB_JSON_SYNTAX_ERROR",
            f"Malformed JSON at line {exc.lineno} col {exc.colno}: {exc.msg}",
        ) from exc

    if require_mapping and not isinstance(parsed, Mapping):
        raise VipLabError(
            "LAB_JSON_ROOT_NOT_OBJECT",
            f"Expected top-level JSON object, got {type(parsed).__name__}",
        )
    return parsed


def load_bounded_json_file(
    path: str | Path,
    *,
    max_bytes: int = MAX_LAB_JSON_BYTES,
    require_mapping: bool = True,
) -> Any:
    """Load a regular UTF-8 JSON file using O_NOFOLLOW and a strict byte ceiling."""
    file_path = Path(path)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC

    try:
        fd = os.open(str(file_path), flags)
    except FileNotFoundError as exc:
        raise VipLabError(
            "LAB_FILE_NOT_FOUND",
            f"JSON file does not exist: {file_path}",
            field_path=str(file_path),
        ) from exc
    except OSError as exc:
        raise VipLabError(
            "LAB_FILE_OPEN_REFUSED",
            f"Refused to open {file_path}: {exc}",
            field_path=str(file_path),
        ) from exc

    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise VipLabError(
                "LAB_NON_REGULAR_FILE",
                f"Refused non-regular file: {file_path}",
                field_path=str(file_path),
            )
        if st.st_size > max_bytes:
            raise VipLabError(
                "LAB_JSON_SIZE_EXCEEDED",
                f"File {file_path} size {st.st_size} exceeds limit {max_bytes}",
                field_path=str(file_path),
                details={"observed_bytes": st.st_size, "max_bytes": max_bytes},
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, max_bytes - total + 1))
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise VipLabError(
                    "LAB_JSON_SIZE_EXCEEDED",
                    f"File {file_path} grew past {max_bytes} bytes while reading",
                    field_path=str(file_path),
                )
            chunks.append(chunk)
        raw = b"".join(chunks)
    finally:
        os.close(fd)

    return parse_strict_json_bytes(
        raw, max_bytes=max_bytes, require_mapping=require_mapping
    )


def validate_hex_digest(
    value: Any,
    *,
    length: int = 64,
    field_name: str = "digest",
    error_code: str = "LAB_INVALID_HEX_DIGEST",
) -> str:
    """Validate that ``value`` is a lowercase hexadecimal string of ``length`` chars."""
    if not isinstance(value, str) or len(value) != length:
        raise VipLabError(
            error_code,
            f"{field_name} must be a {length}-char lowercase hex string",
            field_path=field_name,
        )
    if any(ch not in "0123456789abcdef" for ch in value):
        raise VipLabError(
            error_code,
            f"{field_name} must contain only lowercase hexadecimal characters",
            field_path=field_name,
        )
    return value


def sanitize_untrusted_authority_claims(
    payload: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Inspect a mapping for untrusted self-declared authority flags.

    Returns a shallow copy without trusting external authority booleans and a
    sorted tuple of detected self-declared authority keys that attempted to
    assert ``True`` or positive authority.
    """
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "LAB_INVALID_MAPPING",
            "Expected mapping when inspecting untrusted authority claims",
        )
    detected: list[str] = []
    cleaned = dict(payload)
    for key in sorted(FORBIDDEN_EXTERNAL_AUTHORITY_KEYS):
        if key in cleaned and bool(cleaned[key]):
            detected.append(key)
    return cleaned, tuple(detected)


@dataclass(frozen=True)
class ReadinessFinding:
    """Single deterministic check/refusal/blocker finding inside a ReadinessPacket."""

    code: str
    status: ReadinessStatus
    message: str
    field_path: str | None = None
    evidence_state: str = NOT_OBSERVED
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not self.code.strip():
            raise VipLabError("LAB_INVALID_FINDING_CODE", "Finding code must be non-empty")
        if not isinstance(self.status, ReadinessStatus):
            object.__setattr__(self, "status", ReadinessStatus(self.status))
        if (
            self.evidence_state != NOT_OBSERVED
            and self.evidence_state not in CANONICAL_EVIDENCE_CLASSES
        ):
            raise VipLabError(
                "LAB_INVALID_EVIDENCE_CLASS",
                f"Unsupported evidence_state {self.evidence_state!r}",
                field_path="evidence_state",
            )
        object.__setattr__(self, "details", _validate_canonical_value(dict(self.details)))

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "code": self.code,
            "status": self.status.value,
            "message": self.message,
            "evidence_state": self.evidence_state,
        }
        if self.field_path is not None:
            out["field_path"] = self.field_path
        if self.details:
            out["details"] = dict(self.details)
        return out


@dataclass(frozen=True)
class ReadinessPacket:
    """Canonical immutable readiness output for MEGA-03..07 lab evaluators."""

    stage_id: str
    status: ReadinessStatus
    synthetic_only: bool = True
    execution_authorized: bool = False
    owner_approval_status: str = "NOT_GRANTED"
    gate_verdict: str = "NOT_APPROVED"
    evidence_state: str = NOT_OBSERVED
    reasons: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    findings: tuple[ReadinessFinding, ...] = ()
    summary: Mapping[str, Any] = field(default_factory=dict)
    context_marker: SyntheticContextMarker = field(
        default_factory=SyntheticContextMarker.create,
        repr=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.stage_id, str) or not self.stage_id.strip():
            raise VipLabError("LAB_INVALID_STAGE_ID", "stage_id must be a non-empty string")
        if not isinstance(self.status, ReadinessStatus):
            object.__setattr__(self, "status", ReadinessStatus(self.status))
        if not isinstance(self.context_marker, SyntheticContextMarker):
            raise VipLabError(
                "LAB_FORGED_CONTEXT_MARKER",
                "ReadinessPacket requires a valid SyntheticContextMarker",
            )
        if self.synthetic_only is not True:
            raise VipLabError(
                "LAB_SYNTHETIC_ONLY_VIOLATION",
                "ReadinessPacket in vip_lab must always remain synthetic_only=True",
            )
        if self.execution_authorized is not False:
            raise VipLabError(
                "LAB_AUTHORITY_ESCALATION_FORBIDDEN",
                "vip_lab ReadinessPacket can never set execution_authorized=True",
            )
        if (
            self.evidence_state != NOT_OBSERVED
            and self.evidence_state not in CANONICAL_EVIDENCE_CLASSES
        ):
            raise VipLabError(
                "LAB_INVALID_EVIDENCE_CLASS",
                f"Invalid evidence_state {self.evidence_state!r}",
            )
        object.__setattr__(self, "reasons", tuple(str(r) for r in self.reasons))
        object.__setattr__(self, "blockers", tuple(str(b) for b in self.blockers))
        object.__setattr__(self, "findings", tuple(self.findings))
        object.__setattr__(
            self, "summary", _validate_canonical_value(dict(self.summary))
        )

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "program_version": LAB_PROGRAM_VERSION,
            "stage_id": self.stage_id,
            "status": self.status.value,
            "synthetic_only": self.synthetic_only,
            "execution_authorized": self.execution_authorized,
            "owner_approval_status": self.owner_approval_status,
            "gate_verdict": self.gate_verdict,
            "evidence_state": self.evidence_state,
            "reasons": list(self.reasons),
            "blockers": list(self.blockers),
            "findings": [f.to_dict() for f in self.findings],
            "summary": dict(self.summary),
            "context_token": self.context_marker.token,
        }

    @property
    def packet_digest(self) -> str:
        return canonical_sha256(self.payload_without_digest())

    def to_dict(self) -> dict[str, Any]:
        payload = self.payload_without_digest()
        payload["packet_digest"] = self.packet_digest
        return payload

    def to_canonical_json(self) -> str:
        return canonical_json_dumps(self.to_dict())
