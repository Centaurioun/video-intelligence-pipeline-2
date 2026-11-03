"""Blinded two-human reviewer-envelope assembly for Gate-0 (D-1 / P-05).

Purpose
-------
Build and validate the strictly blinded, two-independent-human input envelope
that ``gate0.evaluation.load_reviewer_input`` already consumes.  This module is
an *assembly and validation* tool only: it accepts caller-supplied review rows
and never invents, infers, repairs or re-grades a human judgment.  Callers are
responsible for supplying genuine human review; synthetic fixtures may be used
only to exercise the software path and must never be presented as authentic
human evidence.

Contract compatibility
----------------------
The frozen producer (``gate0.evaluation.load_reviewer_input``) is treated as
read-only.  The closed envelope is::

    {"schema_version", "input_digest", "blind_mapping_digest", "rows"}

with ``schema_version == "gate0.reviewer-input.v1"``, two blind tokens
(``arm-a``/``arm-b``), canonical SHA-256 digests reused from the existing
producer helpers, and reviewer-visible rows restricted to the producer's
allowed field set.  The assembler itself never places arm identity (``arm_id`` /
``revision_id``) in a reviewer-visible row, and the token map is bound only as a
digest.  Caller-supplied free text is additionally screened for the configured
``arm_id`` values and for any caller-declared ``forbidden_identifiers`` (revision
ids, ranker names, etc.); free-text identity leakage that the caller does not
declare cannot be detected here (see PENDING below).

Isolation
---------
This module does not import the ranker, the arms, the adapters or the label
builders.  It performs no media access and no filesystem reads.  The only
filesystem write is :func:`write_reviewer_envelope`, which requires an explicit
caller-provided authorized root.

PENDING contract-owner issues (loader-undetectable; never silently assumed)
--------------------------------------------------------------------------
The frozen producer cannot see any of the following, so this module records them
as PENDING rather than inventing a weaker or a stronger rule:

* PENDING (corpus correspondence): whether a row's ``assertion`` text, window or
  query genuinely corresponds to the frozen corpus.  Callers holding the frozen
  projections may pass ``known_query_ids`` / ``known_window_ids`` /
  ``forbidden_query_ids`` to enforce those boundaries explicitly.
* PENDING (adjudication-ref granularity): whether one ``adjudication_ref`` may
  legitimately span several judgment groups.
* PENDING (adjudication provenance): a shared ``adjudication_ref`` is required
  only within each two-reviewer group when present and must be identical there;
  it is not *provable* that a coinciding final grade was reached by
  adjudication rather than by independent agreement, because the frozen
  producer discards provenance once both recorded grades are equal.
* PENDING (revision/ranker identity): identity variants in caller free text are
  only screened when the caller declares them via ``forbidden_identifiers``.
* PENDING (cross-row assertion consistency): rows sharing a query/window are not
  required to carry the same assertion projection; the frozen producer treats
  ``assertion`` as opaque per row.

Coupling note: the canonical digest scopes are reused from the frozen producer's
private helpers ``_input_digest_for`` / ``_mapping_digest_for`` so this assembler
and the producer cannot drift; that private-API coupling is intentional and is
part of the frozen-contract boundary.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

from gate0.evaluation import TOKENS as _FROZEN_TOKENS
from gate0.evaluation import _input_digest_for, _mapping_digest_for

SCHEMA_VERSION = "gate0.reviewer-input.v1"
TOKENS = frozenset(_FROZEN_TOKENS)
ENVELOPE_FIELDS = frozenset({"schema_version", "input_digest", "blind_mapping_digest", "rows"})
ROW_REQUIRED_FIELDS = frozenset(
    {
        "assertion_id",
        "query_id",
        "window_id",
        "blind_arm_token",
        "reviewer_id",
        "grade",
        "ambiguity",
        "review_status",
        "assertion",
    }
)
ROW_OPTIONAL_FIELDS = frozenset({"adjudication_ref"})
ROW_ALLOWED_FIELDS = ROW_REQUIRED_FIELDS | ROW_OPTIONAL_FIELDS
GRADES = frozenset({0, 1, 2})
AMBIGUITIES = frozenset({"NONE", "UNCERTAIN", "AMBIGUOUS"})
REVIEW_STATUSES = frozenset({"UNREVIEWED", "ACCEPTED", "REJECTED", "AMBIGUOUS"})
FINAL_STATUS = "ACCEPTED"
FINAL_AMBIGUITY = "NONE"
ASSERTION_FIELDS = frozenset({"version", "text", "digest"})
SORT_FIELDS = ("query_id", "window_id", "blind_arm_token", "reviewer_id")
_TOKEN_MAP_FIELDS = frozenset({"blind_arm_token", "arm_id"})
_HEX64 = re.compile(r"[0-9a-f]{64}")

__all__ = [
    "AMBIGUITIES",
    "ASSERTION_FIELDS",
    "ENVELOPE_FIELDS",
    "GRADES",
    "REVIEW_STATUSES",
    "ROW_ALLOWED_FIELDS",
    "ROW_OPTIONAL_FIELDS",
    "ROW_REQUIRED_FIELDS",
    "SCHEMA_VERSION",
    "TOKENS",
    "build_reviewer_envelope",
    "validate_reviewer_envelope",
    "write_reviewer_envelope",
]


# ---------------------------------------------------------------------------
# primitive guards
# ---------------------------------------------------------------------------


def _as_text(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{field} must be a non-empty, non-padded string")
    return value


def _as_digest(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        raise ValueError(f"{field} must be a 64-character lowercase sha256 hex digest")
    return value


def _as_str_set(values: Iterable[str], *, field: str) -> frozenset[str]:
    if isinstance(values, (str, bytes, Mapping)) or values is None:
        raise ValueError(f"{field} must be an iterable of identifiers")
    try:
        items = list(values)
    except TypeError as exc:  # pragma: no cover - defensive
        raise ValueError(f"{field} must be an iterable of identifiers") from exc
    if any(not isinstance(item, str) for item in items):
        raise ValueError(f"{field} must contain only strings")
    return frozenset(items)


def _check_versions(mapping_version: Any, config_digest: Any) -> None:
    if not isinstance(mapping_version, str) or not mapping_version:
        raise ValueError("mapping_version must be a non-empty string")
    _as_digest(config_digest, field="config_digest")


# ---------------------------------------------------------------------------
# token map (blinding configuration)
# ---------------------------------------------------------------------------


def _normalized_token_map(token_map: Any) -> tuple[dict[str, str], ...]:
    if isinstance(token_map, (str, bytes, Mapping)) or token_map is None:
        raise ValueError("token_map must be a sequence of two blind-arm mappings")
    try:
        entries = list(token_map)
    except TypeError as exc:  # pragma: no cover - defensive
        raise ValueError("token_map must be a sequence of two blind-arm mappings") from exc
    if len(entries) != 2:
        raise ValueError("token_map must contain exactly two blind arm tokens")
    normalized: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError("token_map entries must be mappings")
        if set(entry) != _TOKEN_MAP_FIELDS:
            raise ValueError("token_map entries must carry exactly blind_arm_token and arm_id")
        token = _as_text(entry["blind_arm_token"], field="token_map blind_arm_token")
        arm_id = _as_text(entry["arm_id"], field="token_map arm_id")
        normalized.append({"blind_arm_token": token, "arm_id": arm_id})
    tokens = {entry["blind_arm_token"] for entry in normalized}
    if tokens != set(TOKENS):
        raise ValueError(f"token_map must use exactly the blind arm tokens {sorted(TOKENS)}")
    arm_ids = {entry["arm_id"] for entry in normalized}
    if len(arm_ids) != 2:
        raise ValueError("token_map arm_id values must be distinct")
    if arm_ids & set(TOKENS):
        raise ValueError("token_map arm_id must not equal a blind arm token")
    if len({entry["blind_arm_token"] for entry in normalized}) != 2:  # pragma: no cover
        raise ValueError("token_map blind arm tokens must be distinct")
    return tuple(normalized)


# ---------------------------------------------------------------------------
# row normalization and closed-field validation
# ---------------------------------------------------------------------------


def _copy_row(row: Mapping[str, Any]) -> dict[str, Any]:
    unknown = set(row) - ROW_ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"unknown reviewer field: {sorted(map(str, unknown))[0]}")
    missing = ROW_REQUIRED_FIELDS - set(row)
    if missing:
        raise ValueError("incomplete reviewer row")
    assertion = row["assertion"]
    if not isinstance(assertion, Mapping) or set(assertion) != ASSERTION_FIELDS:
        raise ValueError("invalid assertion projection")
    _as_text(assertion["version"], field="assertion version")
    _as_text(assertion["text"], field="assertion text")
    _as_digest(assertion["digest"], field="assertion digest")

    status = row["review_status"]
    if not isinstance(status, str) or status not in REVIEW_STATUSES:
        raise ValueError("invalid review status")
    ambiguity = row["ambiguity"]
    if not isinstance(ambiguity, str) or ambiguity not in AMBIGUITIES:
        raise ValueError("invalid reviewer ambiguity")
    grade = row["grade"]
    if isinstance(grade, bool) or not isinstance(grade, int) or grade not in GRADES:
        raise ValueError("invalid reviewer grade")

    copied: dict[str, Any] = {
        "assertion_id": _as_text(row["assertion_id"], field="assertion_id"),
        "query_id": _as_text(row["query_id"], field="query_id"),
        "window_id": _as_text(row["window_id"], field="window_id"),
        "blind_arm_token": _as_text(row["blind_arm_token"], field="blind_arm_token"),
        "reviewer_id": _as_text(row["reviewer_id"], field="reviewer_id"),
        "grade": grade,
        "ambiguity": ambiguity,
        "review_status": status,
        "assertion": {
            "version": assertion["version"],
            "text": assertion["text"],
            "digest": assertion["digest"],
        },
    }
    if "adjudication_ref" in row:
        reference = row["adjudication_ref"]
        if not isinstance(reference, str) or not reference or reference != reference.strip():
            raise ValueError(
                "adjudication_ref must be a non-empty, non-padded string shared by both reviewers"
            )
        copied["adjudication_ref"] = reference
    return copied


def _copy_rows(rows: Any) -> list[dict[str, Any]]:
    if isinstance(rows, (str, bytes, Mapping)) or rows is None:
        raise ValueError("reviewer rows must be a sequence of mappings")
    try:
        items = list(rows)
    except TypeError as exc:  # pragma: no cover - defensive
        raise ValueError("reviewer rows must be a sequence of mappings") from exc
    if not items:
        raise ValueError("reviewer rows must not be empty")
    copied: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise ValueError("reviewer row must be a mapping")
        copied.append(_copy_row(item))
    return copied


def _row_sort_key(row: Mapping[str, Any]) -> tuple[bytes, ...]:
    return tuple(str(row[field]).encode("utf-8") for field in SORT_FIELDS)


def _iter_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_strings(item)


# ---------------------------------------------------------------------------
# envelope-level validation
# ---------------------------------------------------------------------------


def _check_group_judgments(rows: Sequence[Mapping[str, Any]]) -> None:
    groups: dict[tuple[str, str, str], list[Mapping[str, Any]]] = {}
    seen: set[tuple[str, str, str, str]] = set()
    for row in rows:
        token = str(row["blind_arm_token"])
        if token not in TOKENS:
            raise ValueError(f"unknown blind arm token: {token}")
        key = (str(row["query_id"]), str(row["window_id"]), token, str(row["reviewer_id"]))
        if key in seen:
            raise ValueError("duplicate reviewer judgment key")
        seen.add(key)
        groups.setdefault(key[:3], []).append(row)

    for group_key, group in sorted(groups.items()):
        if len(group) != 2 or len({row["reviewer_id"] for row in group}) != 2:
            raise ValueError(
                "exactly two reviewers per judgment required "
                "(exactly two distinct reviewers)"
            )
        for row in group:
            if row["review_status"] != FINAL_STATUS or row["ambiguity"] != FINAL_AMBIGUITY:
                raise ValueError("reviewer judgment is not final")
        references = {row.get("adjudication_ref") for row in group}
        if len(references) != 1:
            raise ValueError("adjudication_ref must be recorded identically by both reviewers")
        grades = {row["grade"] for row in group}
        if len(grades) != 1:
            raise ValueError(
                "reviewer disagreement requires adjudication to an identical final grade"
            )

    reviewers = {row["reviewer_id"] for row in rows}
    if len(reviewers) != 2:
        raise ValueError("exactly two distinct reviewer identities required")


def _hidden_identifiers(
    token_map: Sequence[Mapping[str, str]],
    forbidden_identifiers: Iterable[str] | None,
) -> tuple[str, ...]:
    hidden = {str(entry["arm_id"]) for entry in token_map}
    if forbidden_identifiers is not None:
        declared = _as_str_set(forbidden_identifiers, field="forbidden_identifiers")
        hidden |= {identifier for identifier in declared if identifier}
    hidden.discard("")
    return tuple(sorted(hidden))


def _check_blinding(
    rows: Sequence[Mapping[str, Any]],
    token_map: Sequence[Mapping[str, str]],
    forbidden_identifiers: Iterable[str] | None = None,
) -> None:
    hidden = _hidden_identifiers(token_map, forbidden_identifiers)
    for row in rows:
        for text in _iter_strings(row):
            for identifier in hidden:
                if identifier in text:
                    raise ValueError(
                        "blinding violation: a hidden identity appears in "
                        "reviewer-visible row text"
                    )


def _check_boundaries(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_reviewer_ids: Iterable[str] | None,
    known_query_ids: Iterable[str] | None,
    known_window_ids: Iterable[str] | None,
    forbidden_query_ids: Iterable[str] | None,
) -> None:
    reviewers = {row["reviewer_id"] for row in rows}
    if expected_reviewer_ids is not None:
        expected = _as_str_set(expected_reviewer_ids, field="expected_reviewer_ids")
        if reviewers != expected:
            raise ValueError("reviewer identities do not match the declared reviewer set")
    if known_query_ids is not None:
        allowed = _as_str_set(known_query_ids, field="known_query_ids")
        for row in rows:
            if row["query_id"] not in allowed:
                raise ValueError(f"unknown query id in reviewer row: {row['query_id']}")
    if known_window_ids is not None:
        allowed = _as_str_set(known_window_ids, field="known_window_ids")
        for row in rows:
            if row["window_id"] not in allowed:
                raise ValueError(f"unknown window id in reviewer row: {row['window_id']}")
    if forbidden_query_ids is not None:
        forbidden = _as_str_set(forbidden_query_ids, field="forbidden_query_ids")
        for row in rows:
            if row["query_id"] in forbidden:
                raise ValueError(
                    "reviewer rows must not cross development/evaluation review boundary"
                )


def _check_tokens_present(rows: Sequence[Mapping[str, Any]]) -> None:
    present = {row["blind_arm_token"] for row in rows}
    if present != set(TOKENS):
        missing = sorted(set(TOKENS) - present)
        raise ValueError(f"exactly two blind arm tokens required; missing {missing}")


def validate_reviewer_envelope(
    envelope: Mapping[str, Any],
    *,
    token_map: Sequence[Mapping[str, str]],
    mapping_version: str = "gate0-v1",
    config_digest: str = "0" * 64,
    expected_input_digest: str | None = None,
    expected_mapping_digest: str | None = None,
    expected_reviewer_ids: Iterable[str] | None = None,
    known_query_ids: Iterable[str] | None = None,
    known_window_ids: Iterable[str] | None = None,
    forbidden_query_ids: Iterable[str] | None = None,
    forbidden_identifiers: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Validate a closed reviewer envelope against the frozen producer rules.

    Raises ``ValueError`` on any unknown/missing field, forged digest, invalid
    grade/status/ambiguity, non-final review, unadjudicated disagreement,
    arm-identity leak, malformed token map or caller-declared corpus-boundary
    violation.  Returns a fresh copy of the envelope; never writes anything.
    """
    normalized_map = _normalized_token_map(token_map)
    _check_versions(mapping_version, config_digest)
    if not isinstance(envelope, Mapping):
        raise ValueError("reviewer envelope must be a mapping")
    if set(envelope) != ENVELOPE_FIELDS:
        raise ValueError("reviewer input envelope has unknown or missing fields")
    if envelope["schema_version"] != SCHEMA_VERSION:
        raise ValueError("invalid reviewer input schema")

    rows = _copy_rows(envelope["rows"])

    computed_mapping = _mapping_digest_for(
        normalized_map, mapping_version=mapping_version, config_digest=config_digest
    )
    declared_mapping = _as_digest(envelope["blind_mapping_digest"], field="blind_mapping_digest")
    if declared_mapping != computed_mapping:
        raise ValueError("wrong blinding mapping digest")
    if expected_mapping_digest is not None:
        if declared_mapping != _as_digest(expected_mapping_digest, field="expected_mapping_digest"):
            raise ValueError("wrong blinding mapping digest")

    computed_input = _input_digest_for(SCHEMA_VERSION, rows)
    declared_input = _as_digest(envelope["input_digest"], field="input_digest")
    if declared_input != computed_input:
        raise ValueError("wrong reviewer input digest")
    if expected_input_digest is not None:
        if declared_input != _as_digest(expected_input_digest, field="expected_input_digest"):
            raise ValueError("wrong reviewer input digest")

    _check_group_judgments(rows)
    _check_blinding(rows, normalized_map, forbidden_identifiers)
    _check_tokens_present(rows)
    _check_boundaries(
        rows,
        expected_reviewer_ids=expected_reviewer_ids,
        known_query_ids=known_query_ids,
        known_window_ids=known_window_ids,
        forbidden_query_ids=forbidden_query_ids,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "input_digest": computed_input,
        "blind_mapping_digest": computed_mapping,
        "rows": rows,
    }


def build_reviewer_envelope(
    rows: Sequence[Mapping[str, Any]],
    *,
    token_map: Sequence[Mapping[str, str]],
    mapping_version: str = "gate0-v1",
    config_digest: str = "0" * 64,
    expected_reviewer_ids: Iterable[str] | None = None,
    known_query_ids: Iterable[str] | None = None,
    known_window_ids: Iterable[str] | None = None,
    forbidden_query_ids: Iterable[str] | None = None,
    forbidden_identifiers: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Assemble a closed, canonically-digested blinded reviewer envelope.

    ``rows`` must already be genuine, final two-reviewer judgments supplied by
    the caller; this function never derives or alters a grade, adds a reviewer
    or fabricates a judgment.  Rows are emitted in canonical sort order so the
    digest is stable under caller row permutation.
    """
    normalized_map = _normalized_token_map(token_map)
    _check_versions(mapping_version, config_digest)
    prepared = sorted(_copy_rows(rows), key=_row_sort_key)
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "input_digest": _input_digest_for(SCHEMA_VERSION, prepared),
        "blind_mapping_digest": _mapping_digest_for(
            normalized_map, mapping_version=mapping_version, config_digest=config_digest
        ),
        "rows": prepared,
    }
    return validate_reviewer_envelope(
        envelope,
        token_map=normalized_map,
        mapping_version=mapping_version,
        config_digest=config_digest,
        expected_reviewer_ids=expected_reviewer_ids,
        known_query_ids=known_query_ids,
        known_window_ids=known_window_ids,
        forbidden_query_ids=forbidden_query_ids,
        forbidden_identifiers=forbidden_identifiers,
    )


def _fsync_directory(directory: Path) -> None:
    """Best-effort durability for the atomic replace (crash consistency only)."""
    try:
        descriptor = os.open(str(directory), os.O_RDONLY)
    except OSError:  # pragma: no cover - platform/filesystem dependent
        return
    try:
        os.fsync(descriptor)
    except OSError:  # pragma: no cover - platform/filesystem dependent
        pass
    finally:
        os.close(descriptor)


def write_reviewer_envelope(
    envelope: Mapping[str, Any],
    path: str | Path,
    *,
    authorized_root: str | Path,
    token_map: Sequence[Mapping[str, str]],
    mapping_version: str = "gate0-v1",
    config_digest: str = "0" * 64,
    expected_input_digest: str | None = None,
    expected_mapping_digest: str | None = None,
    expected_reviewer_ids: Iterable[str] | None = None,
    known_query_ids: Iterable[str] | None = None,
    known_window_ids: Iterable[str] | None = None,
    forbidden_query_ids: Iterable[str] | None = None,
    forbidden_identifiers: Iterable[str] | None = None,
) -> Path:
    """Atomically persist a validated envelope beneath a caller-provided root.

    The envelope is fully re-validated first, so an invalid envelope leaves the
    filesystem untouched.  The destination must resolve strictly beneath
    ``authorized_root`` (the same containment rule the frozen producer
    enforces) and must not already be a directory; existing regular files are
    replaced atomically via a same-directory temporary file with an
    fsync of the file and (best effort) of the containing directory.  The same
    optional caller-declared boundaries accepted by build/validate are forwarded
    here, so a boundary-violating envelope is refused before any filesystem
    change.  A SIGKILL between temporary-file creation and ``os.replace`` can
    leave a ``.reviewer-envelope-*.tmp`` file behind; it is never mistaken for
    the output path.
    """
    validated = validate_reviewer_envelope(
        envelope,
        token_map=token_map,
        mapping_version=mapping_version,
        config_digest=config_digest,
        expected_input_digest=expected_input_digest,
        expected_mapping_digest=expected_mapping_digest,
        expected_reviewer_ids=expected_reviewer_ids,
        known_query_ids=known_query_ids,
        known_window_ids=known_window_ids,
        forbidden_query_ids=forbidden_query_ids,
        forbidden_identifiers=forbidden_identifiers,
    )
    root = Path(authorized_root).resolve()
    target = Path(path).resolve()
    if root not in target.parents:
        raise ValueError("review output must be a regular file beneath authorized root")
    if target.exists() and not target.is_file():
        raise ValueError("review output must be a regular file beneath authorized root")
    if not target.parent.is_dir():
        raise ValueError("review output directory does not exist")

    payload = json.dumps(
        validated, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ) + "\n"
    descriptor, temporary = tempfile.mkstemp(
        dir=str(target.parent), prefix=".reviewer-envelope-", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        _fsync_directory(target.parent)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise
    return target

