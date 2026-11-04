"""Closed, bounded lab text-query catalog and deterministic input identity.

Authority: VIP-LAB-MEGA-02 Workstream W1.

A query catalog is a lab-only text input structure. Its SHA-256 digest records
canonical input byte identity only; it does not establish Gate-0 corpus freeze,
human relevance labels, source media identity, or model weights provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

QUERY_CATALOG_SCHEMA_VERSION = "vip-lab-query-catalog-v1"
MAX_CATALOG_BYTES = 2 * 1024 * 1024
MIN_QUERY_COUNT = 1
MAX_QUERY_COUNT = 64
MIN_TOP_K = 1
MAX_TOP_K = 50
MAX_CATALOG_ID_LENGTH = 128
MAX_QUERY_ID_LENGTH = 128
MAX_QUERY_TEXT_LENGTH = 2048

_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA256_HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_LOWER_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TOP_LEVEL_FIELDS = frozenset({"schema_version", "catalog_id", "queries"})
_QUERY_ITEM_FIELDS = frozenset({"query_id", "text"})


def _is_valid_identifier(value: object, *, max_length: int) -> bool:
    if type(value) is not str or not value or len(value) > max_length:
        return False
    if value != value.strip():
        return False
    if "\x00" in value or "/" in value or "\\" in value or ":" in value or ".." in value:
        return False
    if value in {".", ".."}:
        return False
    return _IDENTIFIER_RE.fullmatch(value) is not None


def _validate_query_text(text: object) -> str:
    if type(text) is not str:
        raise ValueError("QUERY_CATALOG_QUERY_TEXT_INVALID:not_string")
    if not text or not text.strip():
        raise ValueError("QUERY_CATALOG_QUERY_TEXT_INVALID:blank")
    if len(text) > MAX_QUERY_TEXT_LENGTH:
        raise ValueError("QUERY_CATALOG_QUERY_TEXT_INVALID:length_exceeded")
    if "\x00" in text:
        raise ValueError("QUERY_CATALOG_QUERY_TEXT_INVALID:nul_byte")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("QUERY_CATALOG_QUERY_TEXT_INVALID:utf8_surrogate") from exc
    return text


def validate_lab_top_k(top_k: object) -> int:
    """Validate bounded lab ``top_k`` while guarding against boolean ints."""
    if type(top_k) is not int or top_k < MIN_TOP_K or top_k > MAX_TOP_K:
        raise ValueError(f"QUERY_BATCH_TOP_K_INVALID:{top_k!r}")
    return top_k


@dataclass(frozen=True)
class QueryCatalogItem:
    """One immutable, ordered text query entry inside a lab query catalog."""

    query_id: str
    text: str

    def __post_init__(self) -> None:
        if not _is_valid_identifier(self.query_id, max_length=MAX_QUERY_ID_LENGTH):
            raise ValueError(f"QUERY_CATALOG_QUERY_ID_INVALID:{self.query_id!r}")
        if _SHA256_HEX_RE.fullmatch(self.query_id) is not None:
            raise ValueError("QUERY_CATALOG_QUERY_ID_INVALID: resembles_sha256_digest")
        _validate_query_text(self.text)

    def to_dict(self) -> dict[str, str]:
        return {"query_id": self.query_id, "text": self.text}


def _canonical_catalog_payload(
    schema_version: str,
    catalog_id: str,
    queries: tuple[QueryCatalogItem, ...],
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "catalog_id": catalog_id,
        "queries": [item.to_dict() for item in queries],
    }


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    try:
        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("QUERY_CATALOG_CANONICALIZATION_FAILED") from exc
    return serialized.encode("utf-8")


def compute_query_catalog_digest(
    schema_version: str,
    catalog_id: str,
    queries: tuple[QueryCatalogItem, ...],
) -> str:
    """Compute the deterministic SHA-256 digest of a validated catalog payload."""
    payload = _canonical_catalog_payload(schema_version, catalog_id, queries)
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


@dataclass(frozen=True)
class QueryCatalog:
    """Validated, immutable, bounded text-query catalog for synthetic lab runs."""

    schema_version: str
    catalog_id: str
    queries: tuple[QueryCatalogItem, ...]
    catalog_digest: str

    def __post_init__(self) -> None:
        if type(self.schema_version) is not str or self.schema_version != QUERY_CATALOG_SCHEMA_VERSION:
            raise ValueError(f"QUERY_CATALOG_SCHEMA_INVALID:{self.schema_version!r}")
        if not _is_valid_identifier(self.catalog_id, max_length=MAX_CATALOG_ID_LENGTH):
            raise ValueError(f"QUERY_CATALOG_ID_INVALID:{self.catalog_id!r}")
        if _SHA256_HEX_RE.fullmatch(self.catalog_id) is not None:
            raise ValueError("QUERY_CATALOG_ID_INVALID:resembles_sha256_digest")
        if type(self.queries) is not tuple:
            raise ValueError("QUERY_CATALOG_QUERIES_INVALID:not_tuple")
        if not (MIN_QUERY_COUNT <= len(self.queries) <= MAX_QUERY_COUNT):
            raise ValueError(f"QUERY_CATALOG_COUNT_OUT_OF_BOUNDS:{len(self.queries)}")
        if any(type(item) is not QueryCatalogItem for item in self.queries):
            raise ValueError("QUERY_CATALOG_QUERIES_INVALID:item_type")

        seen_ids: set[str] = set()
        for item in self.queries:
            if item.query_id in seen_ids:
                raise ValueError(f"QUERY_CATALOG_DUPLICATE_QUERY_ID:{item.query_id}")
            seen_ids.add(item.query_id)

        if type(self.catalog_digest) is not str or _LOWER_SHA256_RE.fullmatch(self.catalog_digest) is None:
            raise ValueError("QUERY_CATALOG_DIGEST_INVALID")
        expected_digest = compute_query_catalog_digest(
            self.schema_version, self.catalog_id, self.queries
        )
        if self.catalog_digest != expected_digest:
            raise ValueError(
                f"QUERY_CATALOG_DIGEST_MISMATCH:{self.catalog_digest}!={expected_digest}"
            )

    @property
    def query_ids(self) -> tuple[str, ...]:
        """Return ordered query IDs exactly as declared in the catalog."""
        return tuple(item.query_id for item in self.queries)

    def distinct_texts(self) -> tuple[str, ...]:
        """Return unique query texts in first-seen order without collapsing IDs."""
        seen: set[str] = set()
        ordered: list[str] = []
        for item in self.queries:
            if item.text not in seen:
                seen.add(item.text)
                ordered.append(item.text)
        return tuple(ordered)

    def to_dict(self) -> dict[str, Any]:
        return _canonical_catalog_payload(
            self.schema_version, self.catalog_id, self.queries
        )

    def canonical_bytes(self) -> bytes:
        return _canonical_json_bytes(self.to_dict())


def parse_query_catalog_mapping(payload: Mapping[str, Any]) -> QueryCatalog:
    """Validate an in-memory mapping and return a closed :class:`QueryCatalog`."""
    if not isinstance(payload, Mapping):
        raise ValueError("QUERY_CATALOG_NOT_OBJECT")
    actual_keys = set(payload.keys())
    if actual_keys != _TOP_LEVEL_FIELDS:
        raise ValueError("QUERY_CATALOG_FIELDS_INVALID")

    schema_version = payload["schema_version"]
    catalog_id = payload["catalog_id"]
    raw_queries = payload["queries"]
    if type(raw_queries) is not list:
        raise ValueError("QUERY_CATALOG_QUERIES_INVALID:not_list")
    if not (MIN_QUERY_COUNT <= len(raw_queries) <= MAX_QUERY_COUNT):
        raise ValueError(f"QUERY_CATALOG_COUNT_OUT_OF_BOUNDS:{len(raw_queries)}")

    items: list[QueryCatalogItem] = []
    for raw_item in raw_queries:
        if type(raw_item) is not dict:
            raise ValueError("QUERY_CATALOG_ITEM_NOT_OBJECT")
        if set(raw_item.keys()) != _QUERY_ITEM_FIELDS:
            raise ValueError("QUERY_CATALOG_ITEM_FIELDS_INVALID")
        items.append(
            QueryCatalogItem(
                query_id=raw_item["query_id"],
                text=raw_item["text"],
            )
        )

    query_tuple = tuple(items)
    if type(schema_version) is not str or schema_version != QUERY_CATALOG_SCHEMA_VERSION:
        raise ValueError(f"QUERY_CATALOG_SCHEMA_INVALID:{schema_version!r}")
    if not _is_valid_identifier(catalog_id, max_length=MAX_CATALOG_ID_LENGTH):
        raise ValueError(f"QUERY_CATALOG_ID_INVALID:{catalog_id!r}")
    if _SHA256_HEX_RE.fullmatch(catalog_id) is not None:
        raise ValueError("QUERY_CATALOG_ID_INVALID:resembles_sha256_digest")

    digest = compute_query_catalog_digest(schema_version, catalog_id, query_tuple)
    return QueryCatalog(
        schema_version=schema_version,
        catalog_id=catalog_id,
        queries=query_tuple,
        catalog_digest=digest,
    )


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"QUERY_CATALOG_DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def _reject_non_finite_json_constant(token: str) -> Any:
    raise ValueError(f"QUERY_CATALOG_NON_FINITE_NUMBER:{token}")


def parse_query_catalog_bytes(raw: bytes) -> QueryCatalog:
    """Parse and validate raw UTF-8 JSON bytes into a :class:`QueryCatalog`."""
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("QUERY_CATALOG_BYTES_REQUIRED")
    if len(raw) == 0:
        raise ValueError("QUERY_CATALOG_EMPTY_BYTES")
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError(f"QUERY_CATALOG_SIZE_EXCEEDED:{len(raw)}>{MAX_CATALOG_BYTES}")
    if b"\x00" in raw:
        raise ValueError("QUERY_CATALOG_NUL_BYTE_FORBIDDEN")
    try:
        text = bytes(raw).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("QUERY_CATALOG_UTF8_INVALID") from exc
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_non_finite_json_constant,
        )
    except ValueError as exc:
        msg = str(exc)
        if msg.startswith("QUERY_CATALOG_"):
            raise
        raise ValueError("QUERY_CATALOG_JSON_INVALID") from exc
    if type(parsed) is not dict:
        raise ValueError("QUERY_CATALOG_NOT_OBJECT")
    return parse_query_catalog_mapping(parsed)


def load_query_catalog(path: str | Path) -> QueryCatalog:
    """Read ONLY the explicitly named query catalog file within bounded size."""
    if not isinstance(path, (str, Path)):
        raise TypeError("QUERY_CATALOG_PATH_INVALID")
    target = Path(path)
    try:
        with target.open("rb") as handle:
            raw = handle.read(MAX_CATALOG_BYTES + 1)
    except OSError as exc:
        raise ValueError("QUERY_CATALOG_UNREADABLE") from exc
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError(f"QUERY_CATALOG_SIZE_EXCEEDED:{len(raw)}>{MAX_CATALOG_BYTES}")
    return parse_query_catalog_bytes(raw)


__all__ = [
    "MAX_CATALOG_BYTES",
    "MAX_CATALOG_ID_LENGTH",
    "MAX_QUERY_COUNT",
    "MAX_QUERY_ID_LENGTH",
    "MAX_QUERY_TEXT_LENGTH",
    "MAX_TOP_K",
    "MIN_QUERY_COUNT",
    "MIN_TOP_K",
    "QUERY_CATALOG_SCHEMA_VERSION",
    "QueryCatalog",
    "QueryCatalogItem",
    "compute_query_catalog_digest",
    "load_query_catalog",
    "parse_query_catalog_bytes",
    "parse_query_catalog_mapping",
    "validate_lab_top_k",
]
