"""Deterministic UTF-8 JSON, JSONL, and Markdown digest scopes."""
from __future__ import annotations

import json
import math
from collections.abc import Iterable, Mapping
from typing import Any


def _finite(value: Any, path: str = "$") -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"canonical JSON does not permit non-finite numbers at {path}")
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError(f"canonical JSON object keys must be strings at {path}")
        return {key: _finite(item, f"{path}.{key}") for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_finite(item, f"{path}[{i}]") for i, item in enumerate(value)]
    return value


def canonical_text(value: Any, *, trailing_lf: bool = True) -> str:
    text = json.dumps(_finite(value), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)
    return text + ("\n" if trailing_lf else "")


def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON object bytes (without a record/file terminator)."""
    return canonical_text(value, trailing_lf=False).encode("utf-8")


# Compatibility name used by the canonical JSON unit-test/API surface.
canonical_json_bytes = canonical_bytes


def canonical_jsonl(records: Iterable[Any]) -> str:
    rows = list(records)
    ids = [row.get("record_id") if isinstance(row, Mapping) else None for row in rows]
    if any(not isinstance(value, str) for value in ids):
        raise ValueError("JSONL records require string record_id")
    if ids != sorted(ids):
        raise ValueError("JSONL records must be ordered by record_id")
    if len(set(ids)) != len(ids):
        raise ValueError("JSONL record_id values must be unique")
    return "".join(canonical_text(row) for row in rows)


def canonical_jsonl_bytes(records: Iterable[Any]) -> bytes:
    return canonical_jsonl(records).encode("utf-8")


def normalize_jsonl_bytes(value: bytes) -> bytes:
    if not isinstance(value, bytes) or b"\r" in value:
        raise ValueError("JSONL must be UTF-8 LF text")
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("JSONL must be UTF-8") from exc
    if text == "" or not text.endswith("\n") or "\n\n" in text:
        raise ValueError("JSONL must be LF-terminated with no blank lines")
    records = []
    for line in text.splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError("invalid JSONL line") from exc
    expected = canonical_jsonl_bytes(records)
    if expected != value:
        raise ValueError("JSONL is not canonical")
    return value


def normalize_markdown_bytes(value: bytes) -> bytes:
    if not isinstance(value, bytes) or b"\r" in value:
        raise ValueError("Markdown must be UTF-8 LF text")
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Markdown must be UTF-8") from exc
    # Trailing whitespace is removed per physical line; exactly one LF is used.
    return ("\n".join(line.rstrip() for line in text.splitlines()) + "\n").encode("utf-8")
