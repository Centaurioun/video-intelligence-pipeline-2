"""Deterministic UTF-8 canonical JSON and JSONL serialization for Gate 1."""
from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping
from typing import Any


def _checked(value: Any, path: str = "$") -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"canonical JSON does not permit non-finite numbers at {path}")
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError(f"canonical JSON object keys must be strings at {path}")
        return {key: _checked(item, f"{path}.{key}") for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_checked(item, f"{path}[{index}]") for index, item in enumerate(value)]
    return value


def canonical_bytes(value: Any) -> bytes:
    """Serialize a JSON value to compact, sorted-key UTF-8 bytes."""
    text = json.dumps(
        _checked(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return text.encode("utf-8")


def _record_id(row: Any) -> str:
    if not isinstance(row, Mapping):
        raise ValueError("JSONL records must be JSON objects")
    record_id = row.get("record_id")
    if record_id is None and isinstance(row.get("envelope"), Mapping):
        record_id = row["envelope"].get("record_id")
    if not isinstance(record_id, str) or not record_id:
        raise ValueError("JSONL records require a string record_id")
    return record_id


def canonical_jsonl(records: Iterable[Any]) -> str:
    """Serialize rows in ascending unique record_id order, LF terminated."""
    rows = list(records)
    ids = [_record_id(row) for row in rows]
    if ids != sorted(ids):
        raise ValueError("JSONL records must be ordered by record_id")
    if len(set(ids)) != len(ids):
        raise ValueError("JSONL record_id values must be unique")
    return "".join(canonical_bytes(row).decode("utf-8") + "\n" for row in rows)


def canonical_jsonl_bytes(records: Iterable[Any]) -> bytes:
    return canonical_jsonl(records).encode("utf-8")


def sha256_digest(value: Any) -> str:
    """Return the lowercase SHA-256 digest of a value's canonical JSON bytes."""
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_digest_bytes(value: bytes) -> str:
    """Return the lowercase SHA-256 digest of raw bytes."""
    return hashlib.sha256(value).hexdigest()
