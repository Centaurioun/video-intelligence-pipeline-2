"""Opaque identifiers and byte-scoped SHA-256 identity helpers.

Identifiers are deliberately not content digests.  This module is the single
authority for their syntax so callers cannot accidentally use path/provider
identifiers as record identity.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from .canonical_json import canonical_bytes

OPAQUE_ID_PATTERN = r"^[a-z0-9][a-z0-9_-]{0,127}$"
_ID = re.compile(OPAQUE_ID_PATTERN, re.ASCII)
SHA256_PATTERN = r"^[0-9a-f]{64}$"
_SHA256 = re.compile(SHA256_PATTERN, re.ASCII)


def digest_bytes(value: bytes) -> str:
    if not isinstance(value, bytes):
        raise TypeError("digest input must be bytes")
    return hashlib.sha256(value).hexdigest()


def digest_json(value: Any) -> str:
    return digest_bytes(canonical_bytes(value))


def validate_digest(value: str) -> bool:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError("digest must be lowercase SHA-256 hex")
    return True


def validate_opaque_id(value: str) -> bool:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        raise ValueError("malformed opaque identifier")
    return True


def opaque_id(kind: str, seed: Any) -> str:
    if not isinstance(kind, str) or re.fullmatch(r"[a-z][a-z0-9]{0,31}", kind, re.ASCII) is None:
        raise ValueError("invalid opaque identifier kind")
    material = seed if isinstance(seed, bytes) else canonical_bytes(seed)
    result = f"{kind}_{digest_bytes(material)[:32]}"
    validate_opaque_id(result)
    return result
