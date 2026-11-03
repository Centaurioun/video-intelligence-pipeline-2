"""Measured-media input surface for the executable Gate-0 pipeline.

This module is the *only* place where generated, non-protected local media is
turned into Gate-0 evidence.  It does not replace or duplicate the source
provenance system: it produces exactly the same :class:`ProbeEvidence` and
:class:`RevisionRef` records the synthetic path already consumes, by running the
bounded local ``ffprobe``/:mod:`gate0.media.decode` adapters over files that were
generated on this host.

Guarantees (all enforced here, not inferred downstream):

* sources are declared explicitly, one revision per file, with a relative
  locator inside the input root;
* the selected video stream is explicit or uniquely determined by the probe;
  ambiguity is a hard failure, never a guess;
* presentation timestamps come from decoded frame evidence, expressed as exact
  integer ticks over the measured time base;
* no frame index is ever derived from ``seconds * nominal FPS`` and no DTS value
  is ever substituted for a presentation timestamp;
* a window plan is accepted only when the measured stream duration actually
  covers ``window_count * window_seconds``; otherwise the run fails closed;
* source access is quota-bounded and ``O_NOFOLLOW`` (see
  :mod:`gate0.media.source_guard`): the declared locator must resolve to a
  regular single-link file under the accepted root, is hashed while streamed,
  and its identity/size/digest are bound before and after each measurement;
* a corpus is only accepted as generated-fixture provenance when its declared
  locator digests belong to the digest-bound fixture manifest written by the
  local generation operation.  A generator *name* in the corpus JSON is
  recorded as ``UNVERIFIED_DECLARATIVE`` and never grants trust on its own.

Memory/safety envelope: this resists path, symlink/hardlink, quota, digest, and
inode/mtime tampering around a measurement.  It is *not* a hostile-media parser
and makes no claim about malicious bitstreams.

Anything this module measures is ``MEASURED`` evidence about generated media.
It is not authorized-corpus experiment evidence and it never promotes a Gate-0
decision.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from gate0.identity import validate_digest, validate_opaque_id
from gate0.inventory import ProbeEvidence, RevisionRef
from gate0.media.decode import FrameSequence, decode_frames
from gate0.media.probe import FfprobeAdapter, ProbeCapture
from gate0.media.source_guard import (
    DEFAULT_MAX_SOURCE_BYTES,
    FIXTURE_MANIFEST_FILE,
    FIXTURE_MANIFEST_SCHEMA_VERSION,
    SourceGuardError,
    SourceSnapshot,
    fixture_manifest_digest,
    read_path_bytes,
    snapshot_source,
    verify_source,
)
from gate0.media.tool_identity import ToolIdentity

MEDIA_CORPUS_FILE = "media-corpus.json"
MEDIA_CORPUS_SCHEMA_VERSION = "gate0.media-corpus.v1"
MEDIA_CORPUS_KIND = "generated_synthetic_media_not_experiment_evidence"
MEDIA_EVIDENCE_CLASS = "MEASURED"
MEDIA_MEASUREMENT_ORIGIN = "LOCAL_GENERATED_MEDIA"
MEDIA_PROVENANCE_GENERATOR_STATUS = "UNVERIFIED_DECLARATIVE"
MEDIA_PROVENANCE_BOUND = "GENERATED_FIXTURE_SET_DIGEST_BOUND"
MEDIA_PROVENANCE_UNVERIFIED = "UNVERIFIED_GENERATED_FIXTURE_PROVENANCE"
#: Locations searched for the generated-fixture manifest, relative to the
#: accepted input root.  The fixture builder writes it beside the media.
_FIXTURE_MANIFEST_LOCATIONS = (("media", FIXTURE_MANIFEST_FILE), (FIXTURE_MANIFEST_FILE,))

_SPLITS = ("EVALUATION", "DEVELOPMENT")
_STREAM_TYPES = ("video", "audio", "data", "subtitle")

# ---------------------------------------------------------------------------
# Authorized-local corpus declaration (Gate-0 D-1 preparation seam)
#
# This is deliberately NOT the generated-fixture corpus above.  Gate-0 D-1
# authorizes source-code preparation for a real, owner-authorized local corpus
# while D-2 (genuine inputs/rights) and D-3 (execution) remain unattested.  The
# declaration is therefore a *separate*, explicitly-labelled mode whose loader
# performs lexical validation of declared identity only: it must never open,
# stat, hash, probe or decode any declared source path, and it can never be
# mistaken for generated-fixture provenance.
# ---------------------------------------------------------------------------
AUTHORIZED_CORPUS_FILE = "authorized-corpus.json"
AUTHORIZED_CORPUS_SCHEMA_VERSION = "gate0.authorized-corpus.v1"
AUTHORIZED_CORPUS_KIND = "authorized_local_corpus_not_experiment_evidence"
AUTHORIZED_EVIDENCE_CLASS = "NOT_OBSERVED"
AUTHORIZED_MANIFEST_OBSERVED_FIELDS = frozenset(
    {"revision_id", "content_id", "byte_count", "content_sha256", "evidence_state"})
AUTHORIZED_DECLARATION_MAX_BYTES = 2 * 1024 * 1024
AUTHORIZED_PROVENANCE_STATUS = "AUTHORIZED_LOCAL_DECLARED_NOT_OBSERVED"
AUTHORIZED_PREPARATION_SCHEMA_VERSION = "gate0.authorized-local-preparation.v1"
#: D-2/D-3 blockers that are always present until the Owner attests the inputs
#: and authorizes execution.  They are identities, not warnings to be cleared by
#: writing more software.
AUTHORIZED_EXECUTION_BLOCKERS = (
    "D2_AUTHORIZED_CORPUS_INPUTS_PENDING",
    "D3_EXECUTION_NOT_AUTHORIZED",
)
#: Any of these markers anywhere in a declaration means it is really a
#: generated-fixture document wearing an authorized-local label.
_GENERATED_FIXTURE_MARKERS = (
    "generated_synthetic_media",
    "media-fixtures",
    "LOCAL_GENERATED_MEDIA",
    "UNVERIFIED_GENERATED_FIXTURE_PROVENANCE",
)
_AUTHORIZED_REVISION_FIELDS = (
    "revision_id",
    "occurrence_id",
    "content_id",
    "locator",
    "relation_ids",
    "split",
    "window_count",
    "selected_stream_index",
    "declared_byte_count",
    "declared_content_sha256",
)


class MediaInputError(ValueError):
    """Fail-closed media-input error with a stable reason code."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else f"{reason}: {detail}")


class AuthorizedLocalError(MediaInputError):
    """Fail-closed authorized-local error, reusing media reason semantics."""


@dataclass(frozen=True)
class AuthorizedLocalRevision:
    """One declared real-corpus revision.  Nothing here is observed content."""

    revision_id: str
    occurrence_id: str
    content_id: str
    locator: str
    relation_ids: tuple[str, ...]
    split: str
    window_count: int
    selected_stream_index: int
    declared_byte_count: int | None
    declared_content_sha256: str | None


@dataclass(frozen=True)
class AuthorizedLocalCorpus:
    """Lexically validated authorized-local declaration (declared, not observed)."""

    schema_version: str
    corpus_kind: str
    revisions: tuple[AuthorizedLocalRevision, ...]
    relations: tuple[tuple[str, str], ...]
    evaluation_revision_ids: tuple[str, ...]
    development_revision_id: str
    provenance: Mapping[str, Any]
    policy: Mapping[str, Any]
    declaration_digest: str

    def revision(self, revision_id: str) -> AuthorizedLocalRevision:
        for row in self.revisions:
            if row.revision_id == revision_id:
                return row
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_REVISION_UNKNOWN", revision_id)

    def preparation_record(self) -> dict[str, Any]:
        """Non-executable preparation projection.

        Deliberately carries no source-derived identity: no byte counts, no
        content digests, no durations.  ``source_access_attempted`` is a constant
        ``False`` because this path never touches a declared source.
        """
        return {
            "schema_version": AUTHORIZED_PREPARATION_SCHEMA_VERSION,
            "corpus_kind": AUTHORIZED_CORPUS_KIND,
            "evidence_class": AUTHORIZED_EVIDENCE_CLASS,
            "execution_authorized": False,
            "declaration_digest": self.declaration_digest,
            "source_access_attempted": False,
            "revision_count": len(self.revisions),
        }


def _authorized_require(condition: bool, reason: str, detail: str = "") -> None:
    if not condition:
        raise AuthorizedLocalError(reason, detail)


def _authorized_digest(document: Mapping[str, Any]) -> str:
    """Canonical digest of the declaration document only (no source access)."""
    blob = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _authorized_mapping(value: Any, field: str) -> Mapping[str, Any]:
    _authorized_require(isinstance(value, Mapping), "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                        f"{field} must be an object")
    return dict(value)


def _authorized_string(value: Any, field: str, *, allow_empty: bool = False) -> str:
    _authorized_require(isinstance(value, str), "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                        f"{field} must be a string")
    _authorized_require(allow_empty or bool(value), "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                        f"{field} must be non-empty")
    return value


def _authorized_optional_int(value: Any, field: str) -> int | None:
    if value is None:
        return None
    _authorized_require(isinstance(value, int) and not isinstance(value, bool),
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH", f"{field} must be an integer or null")
    return value


def _authorized_identity(value: Any, field: str) -> str:
    """Declared identity is lexical only: opaque syntax, never a content digest."""
    text = _authorized_string(value, field)
    try:
        validate_opaque_id(text)
    except ValueError as exc:
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_INVALID_IDENTITY", f"{field}: {exc}") from exc
    return text


def _authorized_locator(value: Any) -> str:
    """A locator is a relative, portable string; it is never resolved or opened."""
    _authorized_require(isinstance(value, str), "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                        "locator must be a string")
    locator = value
    _authorized_require(bool(locator.strip()), "AUTHORIZED_CORPUS_INVALID_LOCATOR", "empty locator")
    if "\\" in locator or any(ord(char) < 0x20 for char in locator):
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_LOCATOR_INVALID", locator)
    pure = Path(locator)
    if pure.is_absolute() or locator.startswith("/") or locator.startswith("~"):
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_INVALID_LOCATOR", locator)
    parts = pure.parts
    if not parts or any(part in ("..", "") for part in parts) or ":" in locator.split("/")[0]:
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_INVALID_LOCATOR", locator)
    return locator


def _authorized_revision(row: Any, index: int) -> AuthorizedLocalRevision:
    _authorized_require(isinstance(row, Mapping), "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                        f"revisions[{index}] must be an object")
    keys = set(row)
    expected = set(_AUTHORIZED_REVISION_FIELDS)
    _authorized_require(keys == expected, "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                        f"revisions[{index}] fields {sorted(keys)} != {sorted(expected)}")
    relation_ids = row["relation_ids"]
    _authorized_require(isinstance(relation_ids, Sequence) and not isinstance(relation_ids, str),
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH", "relation_ids must be a list")
    split = _authorized_string(row["split"], "split")
    _authorized_require(split in _SPLITS, "AUTHORIZED_CORPUS_SPLIT_VIOLATION", split)

    window_count = row["window_count"]
    _authorized_require(isinstance(window_count, int) and not isinstance(window_count, bool)
                        and window_count > 0,
                        "AUTHORIZED_CORPUS_INVALID_WINDOW_COUNT", repr(window_count))
    stream_index = row["selected_stream_index"]
    _authorized_require(isinstance(stream_index, int) and not isinstance(stream_index, bool)
                        and stream_index >= 0,
                        "AUTHORIZED_CORPUS_INVALID_STREAM_INDEX", repr(stream_index))

    declared_byte_count = _authorized_optional_int(row["declared_byte_count"], "declared_byte_count")
    _authorized_require(declared_byte_count is None or declared_byte_count >= 0,
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH", "declared_byte_count must be >= 0")

    declared_sha256 = row["declared_content_sha256"]
    _authorized_require(declared_sha256 is None or isinstance(declared_sha256, str),
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                        "declared_content_sha256 must be a string or null")
    if declared_sha256 is not None:
        try:
            validate_digest(declared_sha256)
        except ValueError as exc:
            raise AuthorizedLocalError("AUTHORIZED_CORPUS_SCHEMA_MISMATCH", str(exc)) from exc

    return AuthorizedLocalRevision(
        revision_id=_authorized_identity(row["revision_id"], "revision_id"),
        occurrence_id=_authorized_identity(row["occurrence_id"], "occurrence_id"),
        content_id=_authorized_identity(row["content_id"], "content_id"),
        locator=_authorized_locator(row["locator"]),
        relation_ids=tuple(_authorized_identity(item, "relation_ids[]") for item in relation_ids),
        split=split,
        window_count=window_count,
        selected_stream_index=stream_index,
        declared_byte_count=declared_byte_count,
        declared_content_sha256=declared_sha256,
    )


_AUTHORIZED_PENDING_EVIDENCE = (
    "AUTHORIZED_CORPUS_RIGHTS_ATTESTATION_PENDING",
    "AUTHORIZED_CORPUS_CONTENT_SHA256_PENDING",
    "AUTHORIZED_CORPUS_RETENTION_POLICY_PENDING",
    "AUTHORIZED_CORPUS_MODEL_LICENCE_PENDING",
    "AUTHORIZED_CORPUS_SANDBOX_BINDING_PENDING",
)

_AUTHORIZED_PROVENANCE_PLACEHOLDERS = frozenset(
    {"NOT_OBSERVED", "TODO", "TBD", "PLACEHOLDER", "UNKNOWN", "N/A", "NONE", "PENDING"}
)


def _authorized_require_non_placeholder(value: Any) -> None:
    if isinstance(value, Mapping):
        for item in value.values():
            _authorized_require_non_placeholder(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _authorized_require_non_placeholder(item)
    elif isinstance(value, str):
        text = value.strip()
        _authorized_require(bool(text) and text.upper() not in _AUTHORIZED_PROVENANCE_PLACEHOLDERS,
                            "AUTHORIZED_CORPUS_PROVENANCE_PLACEHOLDER", value)


def _authorized_semantics(
    *,
    revisions: tuple[AuthorizedLocalRevision, ...],
    relations: tuple[tuple[str, str], ...],
    evaluation_revision_ids: tuple[str, ...],
    development_revision_id: str,
    provenance: Mapping[str, Any],
) -> None:
    """Split-group, duplicate and provenance checks over a lexical declaration."""
    revision_ids = [row.revision_id for row in revisions]
    _authorized_require(len(set(revision_ids)) == len(revision_ids),
                        "AUTHORIZED_CORPUS_DUPLICATE_REVISION", "revision_id repeated")
    locators = [row.locator for row in revisions]
    _authorized_require(len(set(locators)) == len(locators),
                        "AUTHORIZED_CORPUS_DUPLICATE_LOCATOR", "locator repeated")
    content_ids = [row.content_id for row in revisions]
    _authorized_require(len(set(content_ids)) == len(content_ids),
                        "AUTHORIZED_CORPUS_DUPLICATE_CONTENT", "content_id repeated")

    by_id = {row.revision_id: row for row in revisions}
    _authorized_require(len(set(evaluation_revision_ids)) == len(evaluation_revision_ids),
                        "AUTHORIZED_CORPUS_SPLIT_VIOLATION", "duplicate evaluation revision id")
    evaluation_ids = set(evaluation_revision_ids)
    for revision_id in evaluation_ids:
        row = by_id.get(revision_id)
        _authorized_require(row is not None and row.split == "EVALUATION",
                            "AUTHORIZED_CORPUS_SPLIT_VIOLATION", revision_id)
    development = by_id.get(development_revision_id)
    _authorized_require(development is not None and development.split == "DEVELOPMENT",
                        "AUTHORIZED_CORPUS_SPLIT_VIOLATION", development_revision_id)
    covered = evaluation_ids | {development_revision_id}
    _authorized_require(covered == set(revision_ids),
                        "AUTHORIZED_CORPUS_SPLIT_VIOLATION",
                        "revisions must belong to exactly one declared group")

    relation_members: set[str] = set()
    for left, right in relations:
        _authorized_require(left in by_id and right in by_id,
                            "AUTHORIZED_CORPUS_RELATION_UNKNOWN", f"{left} <-> {right}")
        _authorized_require(left != right, "AUTHORIZED_CORPUS_SPLIT_VIOLATION", "self relation")
        _authorized_require(by_id[left].split == by_id[right].split,
                            "AUTHORIZED_CORPUS_SPLIT_VIOLATION", f"{left} <-> {right}")
        relation_members.update((left, right))
    for row in revisions:
        for relation_id in row.relation_ids:
            _authorized_require(relation_id in relation_members,
                                "AUTHORIZED_CORPUS_RELATION_UNKNOWN", relation_id)

    _authorized_require(bool(provenance), "AUTHORIZED_CORPUS_PROVENANCE_PLACEHOLDER",
                        "provenance must not be empty")
    _authorized_require_non_placeholder(provenance)


def load_authorized_local_declaration(path: str | Path) -> AuthorizedLocalCorpus:
    """Load and lexically validate an ``authorized-corpus.json`` declaration.

    Only the declaration file itself is read.  Declared source locators are
    strings; no declared path is opened, stat'ed, hashed, probed or decoded.
    Anything that cannot be admitted as a distinct real-corpus declaration fails
    closed.  Being loadable grants no execution authority: D-2 inputs and D-3
    execution authorization remain separate Owner attestations.
    """
    declaration_path = Path(path)
    try:
        declaration_size = declaration_path.stat().st_size
    except OSError as exc:
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_DECLARATION_INVALID",
                                   type(exc).__name__) from exc
    _authorized_require(declaration_size <= AUTHORIZED_DECLARATION_MAX_BYTES,
                        "AUTHORIZED_CORPUS_DECLARATION_TOO_LARGE", str(declaration_size))
    try:
        raw = declaration_path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_DECLARATION_INVALID", type(exc).__name__) from exc
    _authorized_require(isinstance(document, Mapping), "AUTHORIZED_CORPUS_DECLARATION_INVALID",
                        "declaration must be a JSON object")
    document = dict(document)

    _authorized_require(document.get("schema_version") == AUTHORIZED_CORPUS_SCHEMA_VERSION,
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                        f"expected {AUTHORIZED_CORPUS_SCHEMA_VERSION}")
    _authorized_require(document.get("corpus_kind") == AUTHORIZED_CORPUS_KIND,
                        "AUTHORIZED_CORPUS_KIND_MISMATCH", f"expected {AUTHORIZED_CORPUS_KIND}")

    blob = json.dumps(document, sort_keys=True, ensure_ascii=True)
    for marker in _GENERATED_FIXTURE_MARKERS:
        _authorized_require(marker not in blob, "AUTHORIZED_CORPUS_FORGED_GENERATED_FIXTURE", marker)

    raw_revisions = document.get("revisions")
    _authorized_require(isinstance(raw_revisions, Sequence) and not isinstance(raw_revisions, str)
                        and len(raw_revisions) > 0,
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH", "revisions must be a non-empty list")
    revisions = tuple(_authorized_revision(row, index) for index, row in enumerate(raw_revisions))

    raw_relations = document.get("relations")
    _authorized_require(isinstance(raw_relations, Sequence) and not isinstance(raw_relations, str),
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH", "relations must be a list")
    relations: list[tuple[str, str]] = []
    for index, relation in enumerate(raw_relations):
        _authorized_require(isinstance(relation, Sequence) and not isinstance(relation, str)
                            and len(relation) == 2,
                            "AUTHORIZED_CORPUS_SCHEMA_MISMATCH", f"relations[{index}] must be a pair")
        relations.append((_authorized_string(relation[0], "relation[0]"),
                          _authorized_string(relation[1], "relation[1]")))

    raw_evaluation_ids = document.get("evaluation_revision_ids")
    _authorized_require(isinstance(raw_evaluation_ids, Sequence)
                        and not isinstance(raw_evaluation_ids, str),
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH", "evaluation_revision_ids must be a list")
    evaluation_revision_ids = tuple(
        _authorized_string(item, "evaluation_revision_ids[]") for item in raw_evaluation_ids)

    development_revision_id = _authorized_string(document.get("development_revision_id"),
                                                 "development_revision_id")
    provenance = _authorized_mapping(document.get("provenance"), "provenance")
    policy = _authorized_mapping(document.get("policy"), "policy")
    # D-1 is local-only: the declaration may carry nothing else.  A declaration
    # claiming a non-local or extended policy is refused at load time for
    # honesty, even though loading alone grants no capability.
    unknown_policy_keys = sorted(set(policy) - {"local_only"})
    if unknown_policy_keys:
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_POLICY_KEY_UNKNOWN",
                                   unknown_policy_keys[0])
    if policy.get("local_only") is not True:
        raise AuthorizedLocalError("AUTHORIZED_CORPUS_POLICY_NOT_LOCAL_ONLY",
                                   f"local_only {policy.get('local_only')!r}")
    _authorized_semantics(
        revisions=revisions,
        relations=tuple(relations),
        evaluation_revision_ids=evaluation_revision_ids,
        development_revision_id=development_revision_id,
        provenance=provenance,
    )

    return AuthorizedLocalCorpus(
        schema_version=AUTHORIZED_CORPUS_SCHEMA_VERSION,
        corpus_kind=AUTHORIZED_CORPUS_KIND,
        revisions=revisions,
        relations=tuple(relations),
        evaluation_revision_ids=evaluation_revision_ids,
        development_revision_id=development_revision_id,
        provenance=provenance,
        policy=policy,
        declaration_digest=_authorized_digest(document),
    )


def validate_authorized_local_declaration(corpus: AuthorizedLocalCorpus) -> tuple[str, ...]:
    """Missing-evidence blocker identities for D-2/D-3.

    Nothing here can be cleared by software: each identity names an Owner
    attestation that has not been observed.  A declaration may be structurally
    valid and still be non-executable.
    """
    blockers: list[str] = []
    blockers.extend(_AUTHORIZED_PENDING_EVIDENCE)
    blockers.extend(AUTHORIZED_EXECUTION_BLOCKERS)
    return tuple(blockers)


def build_source_manifest_from_declaration(
    *,
    corpus: AuthorizedLocalCorpus,
    observed: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Project the declaration into a *guarded* source manifest.

    The manifest is a declaration projection: every record carries
    ``evidence_state = NOT_OBSERVED`` and ``byte_count``/``content_sha256`` come
    only from the declaration itself (``None`` when not declared).  An
    ``observed`` row is a synthetic test seam that may only *cross-check* the
    declared identity (``content_id``, and ``byte_count``/``content_sha256``
    where declared); it can never promote the record's evidence state, supply
    an identity the declaration did not declare, or copy observed values.  Under
    D-1 nothing is measured: no declared source is opened, stat'ed or hashed.
    """
    _authorized_require(isinstance(corpus, AuthorizedLocalCorpus),
                        "AUTHORIZED_CORPUS_SCHEMA_MISMATCH", "corpus must be a declaration")
    observed_by_id: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(observed):
        _authorized_require(isinstance(row, Mapping), "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                            f"observed[{index}] must be an object")
        unknown = set(row) - AUTHORIZED_MANIFEST_OBSERVED_FIELDS
        if unknown:
            raise AuthorizedLocalError("AUTHORIZED_CORPUS_OBSERVED_FIELD_UNKNOWN",
                                       sorted(unknown)[0])
        revision_id = row.get("revision_id")
        _authorized_require(isinstance(revision_id, str) and revision_id,
                            "AUTHORIZED_CORPUS_SCHEMA_MISMATCH",
                            f"observed[{index}].revision_id must be a string")
        _authorized_require(revision_id not in observed_by_id,
                            "AUTHORIZED_CORPUS_OBSERVED_IDENTITY_MISMATCH",
                            f"observed revision repeated: {revision_id}")
        evidence_state = row.get("evidence_state")
        if evidence_state is not None and evidence_state != AUTHORIZED_EVIDENCE_CLASS:
            raise AuthorizedLocalError("AUTHORIZED_CORPUS_OBSERVED_EVIDENCE_CLASS_NOT_OBSERVED",
                                       f"{revision_id}: {evidence_state!r}")
        try:
            declared = corpus.revision(revision_id)
        except AuthorizedLocalError as exc:
            raise AuthorizedLocalError("AUTHORIZED_CORPUS_OBSERVED_UNKNOWN_REVISION",
                                       revision_id) from exc
        content_id = row.get("content_id")
        if content_id is not None:
            _authorized_require(content_id == declared.content_id,
                                "AUTHORIZED_CORPUS_OBSERVED_IDENTITY_MISMATCH",
                                f"{revision_id}: content_id {content_id!r} != {declared.content_id!r}")
        byte_count = row.get("byte_count")
        if byte_count is not None:
            if declared.declared_byte_count is None:
                raise AuthorizedLocalError("AUTHORIZED_CORPUS_OBSERVED_IDENTITY_UNDECLARED",
                                           f"{revision_id}: byte_count")
            _authorized_require(
                isinstance(byte_count, int) and not isinstance(byte_count, bool)
                and byte_count == declared.declared_byte_count,
                "AUTHORIZED_CORPUS_OBSERVED_IDENTITY_MISMATCH",
                f"{revision_id}: byte_count {byte_count!r} != "
                f"{declared.declared_byte_count!r}")
        content_sha256 = row.get("content_sha256")
        if content_sha256 is not None:
            if declared.declared_content_sha256 is None:
                raise AuthorizedLocalError("AUTHORIZED_CORPUS_OBSERVED_IDENTITY_UNDECLARED",
                                           f"{revision_id}: content_sha256")
            _authorized_require(isinstance(content_sha256, str)
                                and content_sha256 == declared.declared_content_sha256,
                                "AUTHORIZED_CORPUS_OBSERVED_IDENTITY_MISMATCH",
                                f"{revision_id}: content_sha256 mismatch")
        observed_by_id[revision_id] = row

    records: list[dict[str, Any]] = []
    for revision in corpus.revisions:
        records.append({
            "revision_id": revision.revision_id,
            "occurrence_id": revision.occurrence_id,
            "content_id": revision.content_id,
            "locator": revision.locator,
            "relation_ids": list(revision.relation_ids),
            "split": revision.split,
            "window_count": revision.window_count,
            "selected_stream_index": revision.selected_stream_index,
            "byte_count": revision.declared_byte_count,
            "content_sha256": revision.declared_content_sha256,
            "evidence_state": AUTHORIZED_EVIDENCE_CLASS,
        })
    return records


def validate_measured_window_extent(
    *,
    revision: AuthorizedLocalRevision,
    captured: Mapping[str, Any],
    window_seconds: int = 4,
) -> None:
    """Require *measured* extent to cover the declared technical windows.

    Extent is computed from the capture's exact integer rational
    ``duration_ts * time_base_num / time_base_den``.  Nominal-FPS arithmetic
    (``seconds * fps``) is never used, so VFR/non-member sample PTS cannot fake
    coverage.
    """

    def _reject(detail: str) -> None:
        raise MediaInputError("INVALID_WINDOW_COVERAGE", detail)

    if not isinstance(captured, Mapping):
        _reject("captured must be a mapping")

    def _positive_int(field: str) -> int:
        value = captured.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            _reject(f"{field} must be a positive integer")
        return value

    duration_ts = _positive_int("duration_ts")
    time_base_num = _positive_int("time_base_num")
    time_base_den = _positive_int("time_base_den")
    window_count = (revision.window_count if isinstance(revision, AuthorizedLocalRevision)
                    else revision.get("window_count"))
    if not isinstance(window_count, int) or isinstance(window_count, bool) or window_count <= 0:
        _reject("window_count must be a positive integer")
    if not isinstance(window_seconds, int) or isinstance(window_seconds, bool) or window_seconds <= 0:
        _reject("window_seconds must be a positive integer")

    measured = Fraction(duration_ts * time_base_num, time_base_den)
    required = Fraction(window_count * window_seconds)
    if measured < required:
        _reject(f"measured {measured} s < required {required} s "
                f"for {window_count} x {window_seconds} s window(s)")


@dataclass(frozen=True)
class MediaRevision:
    """One declared source revision backed by one generated local media file."""

    revision_id: str
    occurrence_id: str
    content_id: str
    locator: str
    relation_ids: tuple[str, ...]
    split: str
    window_count: int
    selected_stream_index: int | None


@dataclass(frozen=True)
class MediaProvenance:
    """Digest-bound generated-fixture provenance for one corpus path.

    ``generator_identity_status`` is always ``UNVERIFIED_DECLARATIVE``: a name
    in the manifest is not evidence that bytes were generated on this host.
    What *is* checked is that every declared locator resolves to a regular,
    no-follow, quota-bounded file whose digest belongs to the fixture set the
    generator wrote, and that the same digest set is recorded across probes.
    """

    status: str
    fixture_manifest: str
    fixture_set_digest: str
    generator_module: str | None
    generator_identity_status: str
    fixture_digests: tuple[str, ...]
    refusal_reason: str | None = None
    refusal_detail: str = ""


@dataclass(frozen=True)
class MediaCorpus:
    """Validated declaration of the generated-media corpus for one run."""

    schema_version: str
    evaluation_revisions: tuple[str, ...]
    development_revision: str
    relations: tuple[tuple[str, str], ...]
    revisions: tuple[MediaRevision, ...]
    generation: Mapping[str, Any]
    document: Mapping[str, Any]
    provenance: MediaProvenance | None = None

    def revision(self, revision_id: str) -> MediaRevision:
        for row in self.revisions:
            if row.revision_id == revision_id:
                return row
        raise MediaInputError("MEDIA_REVISION_UNKNOWN", revision_id)

    def execution_corpus(self) -> dict[str, Any]:
        """Project onto the internal corpus shape the stage code already uses.

        The projection is data-model only: it carries no probe JSON, no frames
        and no embedding vectors, because those are measured downstream.
        """
        return {
            "schema_version": "gate0.media-execution-corpus.v1",
            "corpus_mode": "media",
            "corpus_kind": MEDIA_CORPUS_KIND,
            "evaluation_revisions": list(self.evaluation_revisions),
            "development_revision": self.development_revision,
            "relations": [list(edge) for edge in self.relations],
            "generation": dict(self.generation),
            "revisions": [
                {
                    "revision_id": row.revision_id,
                    "occurrence_id": row.occurrence_id,
                    "content_id": row.content_id,
                    "locator": row.locator,
                    "relation_ids": list(row.relation_ids),
                    "split": row.split,
                    "window_count": row.window_count,
                }
                for row in self.revisions
            ],
        }


@dataclass(frozen=True)
class MediaMeasurement:
    """Measured probe + decode evidence for exactly one declared revision."""

    revision: MediaRevision
    capture: ProbeCapture
    sequence: FrameSequence
    selected_stream_index: int
    selection_source: str
    origin_pts_ticks: int
    window_count: int
    measured_duration: Fraction
    source_byte_count: int
    source_digest: str

    @property
    def time_base(self) -> tuple[int, int]:
        return self.capture.evidence.time_base

    def probe_evidence(self) -> ProbeEvidence:
        return self.capture.evidence

    def revision_ref(self) -> RevisionRef:
        return RevisionRef(
            self.revision.revision_id,
            self.revision.content_id,
            self.capture.source_path,
            self.selected_stream_index,
            self.selection_source,
        )

    def to_record(self) -> dict[str, Any]:
        """Digest-bound measured evidence record published with the run."""
        num, den = self.time_base
        frames = self.sequence.frames
        first_pts = frames[0].raw_pts_ticks if frames else None
        last_pts = frames[-1].raw_pts_ticks if frames else None
        return {
            "revision_id": self.revision.revision_id,
            "source_kind": MEDIA_MEASUREMENT_ORIGIN,
            "evidence_class": MEDIA_EVIDENCE_CLASS,
            "locator": self.revision.locator,
            "source_byte_count": self.source_byte_count,
            "source_digest": self.source_digest,
            "probe_ref": str(self.capture.evidence.probe_ref),
            "probe_raw_output_digest": self.capture.raw_output_digest,
            "selected_stream_index": self.selected_stream_index,
            "selection_source": self.selection_source,
            "time_base": {"numerator": num, "denominator": den},
            "origin_pts_ticks": self.origin_pts_ticks,
            "presentation_pts_ticks_first": first_pts,
            "presentation_pts_ticks_last": last_pts,
            "frame_count": self.sequence.frame_count,
            "decoded_frame_count": len(frames),
            "window_count": self.window_count,
            "measured_duration": _rational(self.measured_duration),
            "probe_tool": _tool_dict(self.capture.tool),
            # ``-show_frames`` is the presentation-evidence decoder; its identity is
            # the ffprobe that produced the frame rows (ffmpeg is not invoked unless
            # pixel decoding is explicitly requested).
            "frame_evidence_tool": _tool_dict(self.sequence.tool),
        }


def _tool_dict(tool: ToolIdentity) -> dict[str, Any]:
    return {
        "role": tool.role,
        "executable": tool.executable,
        "version": tool.version,
        "configuration": tool.configuration,
        "version_stdout_digest": tool.version_stdout_digest,
        "identity_digest": tool.identity_digest,
    }


def _rational(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _require(condition: bool, reason: str, detail: str = "") -> None:
    if not condition:
        raise MediaInputError(reason, detail)


def _opaque(value: Any, what: str) -> str:
    from gate0.identity import validate_opaque_id

    _require(isinstance(value, str), "MEDIA_CORPUS_INVALID", f"{what} is not a string")
    try:
        validate_opaque_id(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise MediaInputError("MEDIA_CORPUS_INVALID", f"{what} {value!r}: {exc}") from exc
    return value


def _relative_locator(value: Any) -> str:
    _require(isinstance(value, str) and value.strip() != "", "MEDIA_CORPUS_INVALID", "locator is not a non-empty string")
    path = Path(value)
    _require(not path.is_absolute(), "MEDIA_CORPUS_INVALID", f"locator must be relative: {value!r}")
    parts = path.parts
    _require(bool(parts), "MEDIA_CORPUS_INVALID", f"locator must name a file inside the input root: {value!r}")
    _require(all(part not in ("..",) for part in parts), "MEDIA_CORPUS_INVALID", f"locator escapes the input root: {value!r}")
    _require(not any(part.startswith("/") for part in parts), "MEDIA_CORPUS_INVALID", f"locator is absolute: {value!r}")
    return path.as_posix()


def load_media_corpus(document: Mapping[str, Any] | Path | str) -> MediaCorpus:
    """Validate a ``media-corpus.json`` document (or path) fail-closed."""
    corpus_path: Path | None = None
    if isinstance(document, (str, Path)):
        corpus_path = Path(document)
        try:
            text = corpus_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise MediaInputError("MEDIA_CORPUS_UNREADABLE", str(exc)) from exc
        try:
            document = json.loads(text)
        except json.JSONDecodeError as exc:
            raise MediaInputError("MEDIA_CORPUS_INVALID", f"not JSON: {exc}") from exc
    _require(isinstance(document, Mapping), "MEDIA_CORPUS_INVALID", "corpus document is not an object")
    _require(document.get("schema_version") == MEDIA_CORPUS_SCHEMA_VERSION,
             "MEDIA_CORPUS_INVALID", f"schema_version must be {MEDIA_CORPUS_SCHEMA_VERSION}")
    raw_revisions = document.get("revisions")
    _require(isinstance(raw_revisions, list) and raw_revisions, "MEDIA_CORPUS_INVALID", "revisions must be a non-empty array")

    revisions: list[MediaRevision] = []
    for row in raw_revisions:
        _require(isinstance(row, Mapping), "MEDIA_CORPUS_INVALID", "revision entry is not an object")
        revision_id = _opaque(row.get("revision_id"), "revision_id")
        occurrence_id = _opaque(row.get("occurrence_id"), "occurrence_id")
        content_id = _opaque(row.get("content_id"), "content_id")
        split = row.get("split")
        _require(split in _SPLITS, "MEDIA_CORPUS_INVALID", f"{revision_id} split must be one of {_SPLITS}")
        window_count = row.get("window_count")
        _require(isinstance(window_count, int) and not isinstance(window_count, bool) and window_count >= 1,
                 "MEDIA_CORPUS_INVALID", f"{revision_id} window_count must be a positive integer")
        selected = row.get("selected_stream_index")
        if selected is not None:
            _require(isinstance(selected, int) and not isinstance(selected, bool) and selected >= 0,
                     "MEDIA_CORPUS_INVALID", f"{revision_id} selected_stream_index must be a non-negative integer")
        relation_ids = row.get("relation_ids", ())
        _require(isinstance(relation_ids, list), "MEDIA_CORPUS_INVALID", f"{revision_id} relation_ids must be an array")
        relations = tuple(_opaque(item, "relation_id") for item in relation_ids)
        _require(len(set(relations)) == len(relations), "MEDIA_CORPUS_INVALID", f"{revision_id} relation_ids are not unique")
        revisions.append(MediaRevision(revision_id, occurrence_id, content_id, _relative_locator(row.get("locator")),
                                       relations, str(split), int(window_count), selected))

    ids = [row.revision_id for row in revisions]
    _require(len(set(ids)) == len(ids), "MEDIA_CORPUS_INVALID", "revision_id values are not unique")
    locators = [row.locator for row in revisions]
    _require(len(set(locators)) == len(locators), "MEDIA_CORPUS_INVALID", "two revisions declare the same locator")

    evaluation = document.get("evaluation_revisions")
    development = document.get("development_revision")
    _require(isinstance(evaluation, list) and evaluation, "MEDIA_CORPUS_INVALID", "evaluation_revisions must be a non-empty array")
    evaluation_ids = tuple(_opaque(item, "evaluation revision") for item in evaluation)
    _require(len(set(evaluation_ids)) == len(evaluation_ids), "MEDIA_CORPUS_INVALID", "evaluation_revisions are not unique")
    development_id = _opaque(development, "development_revision")

    by_id = {row.revision_id: row for row in revisions}
    for revision_id in evaluation_ids:
        _require(revision_id in by_id, "MEDIA_CORPUS_INVALID", f"evaluation revision {revision_id} is not declared")
        _require(by_id[revision_id].split == "EVALUATION", "MEDIA_CORPUS_INVALID", f"{revision_id} is not an EVALUATION split")
    _require(development_id in by_id, "MEDIA_CORPUS_INVALID", f"development revision {development_id} is not declared")
    _require(by_id[development_id].split == "DEVELOPMENT", "MEDIA_CORPUS_INVALID", f"{development_id} is not a DEVELOPMENT split")
    other_evaluation = sorted(row.revision_id for row in revisions if row.split == "EVALUATION")
    _require(tuple(other_evaluation) == tuple(sorted(evaluation_ids)),
             "MEDIA_CORPUS_INVALID", "evaluation_revisions disagrees with the declared splits")

    raw_relations = document.get("relations", [])
    _require(isinstance(raw_relations, list), "MEDIA_CORPUS_INVALID", "relations must be an array")
    relations_out: list[tuple[str, str]] = []
    for edge in raw_relations:
        _require(isinstance(edge, list) and len(edge) == 2, "MEDIA_CORPUS_INVALID", "each relation must be a two-element array")
        left, right = _opaque(edge[0], "relation revision"), _opaque(edge[1], "relation revision")
        _require(left != right, "MEDIA_CORPUS_INVALID", f"self relation {left}")
        _require(left in by_id and right in by_id, "MEDIA_CORPUS_INVALID", f"relation references unknown revision: {edge!r}")
        # Canonicalise the pair deterministically instead of demanding the caller
        # pre-sort it; the set of relations is what carries provenance.
        relations_out.append(tuple(sorted((left, right))))
    _require(len(set(relations_out)) == len(relations_out), "MEDIA_CORPUS_INVALID", "relations are not unique")

    generation = document.get("generation", {})
    _require(isinstance(generation, Mapping), "MEDIA_CORPUS_INVALID", "generation must be an object")

    corpus = MediaCorpus(
        schema_version=MEDIA_CORPUS_SCHEMA_VERSION,
        evaluation_revisions=tuple(sorted(evaluation_ids)),
        development_revision=development_id,
        relations=tuple(relations_out),
        revisions=tuple(sorted(revisions, key=lambda row: row.revision_id)),
        generation=dict(generation),
        document=dict(document),
    )
    if corpus_path is None:
        return corpus
    # The manifest is parsed and digest-checked here, but declared locators are
    # bound to the fixture digest set at measurement time (measure_revision),
    # where a refusal is already surfaced as a fail-closed stage body.
    return replace(corpus, provenance=_load_fixture_provenance(corpus_path.parent))


def _selection_source(declared: int | None) -> str:
    return "configured" if declared is not None else "unique_probe"


def _measured_duration(capture: ProbeCapture, selected_index: int, time_base: tuple[int, int]) -> Fraction:
    """Exact measured stream duration in seconds, from integer evidence only."""
    for stream in capture.streams:
        if stream.stream_index == selected_index and stream.duration_ts is not None:
            num, den = time_base
            return Fraction(int(stream.duration_ts) * num, den)
    format_block = capture.evidence.ffprobe_json.get("format")
    if isinstance(format_block, Mapping):
        raw = format_block.get("duration")
        if isinstance(raw, str):
            try:
                return Fraction(raw)
            except (ValueError, ZeroDivisionError):
                pass
    raise MediaInputError("DURATION_EVIDENCE_MISSING",
                          f"{capture.source_path}: no integer stream duration_ts or exact format duration")


def _refusal(exc: SourceGuardError) -> MediaInputError:
    return MediaInputError(exc.reason, exc.detail)


def _fixture_manifest_payload(input_root: Path) -> tuple[Path, Mapping[str, Any]]:
    """Locate and read the generated-fixture manifest through a bounded handle."""
    root = input_root.resolve()
    for relative_parts in _FIXTURE_MANIFEST_LOCATIONS:
        candidate = root.joinpath(*relative_parts)
        try:
            raw = read_path_bytes(candidate)
        except SourceGuardError as exc:
            if exc.reason == "SOURCE_UNREADABLE":
                continue
            raise MediaInputError("MEDIA_PROVENANCE_UNVERIFIED", f"{candidate}: {exc.detail}") from exc
        try:
            document = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MediaInputError(
                "MEDIA_PROVENANCE_UNVERIFIED", f"{candidate} is not a JSON document: {exc}"
            ) from exc
        _require(isinstance(document, Mapping), "MEDIA_PROVENANCE_UNVERIFIED",
                 f"{candidate} is not a JSON object")
        return candidate, document
    raise MediaInputError(
        "MEDIA_PROVENANCE_UNVERIFIED",
        f"no {FIXTURE_MANIFEST_FILE} beside the declared media: a declarative corpus cannot "
        "prove its locators are generated fixtures",
    )


def _load_fixture_provenance(input_root: Path) -> MediaProvenance:
    """Load the digest-bound generated-fixture provenance without raising.

    A corpus JSON that merely *declares* a generator is not evidence.  This
    function records ``MEDIA_PROVENANCE_UNVERIFIED`` (with the refusal reason)
    when no valid fixture manifest can be bound; callers that publish evidence
    must refuse rather than proceed on an unverified provenance.
    """
    root = Path(input_root).resolve()
    try:
        manifest_path, document = _fixture_manifest_payload(root)
        return _provenance_from_manifest(root, manifest_path, document)
    except MediaInputError as exc:
        return MediaProvenance(
            status=MEDIA_PROVENANCE_UNVERIFIED,
            fixture_manifest="",
            fixture_set_digest="",
            generator_module=None,
            generator_identity_status=MEDIA_PROVENANCE_GENERATOR_STATUS,
            fixture_digests=(),
            refusal_reason=exc.reason,
            refusal_detail=exc.detail or str(exc),
        )


def _provenance_from_manifest(
    root: Path, manifest_path: Path, document: Mapping[str, Any]
) -> MediaProvenance:
    """Validate one fixture manifest and record its digest-bound fixture set.

    The ``generation`` block is declarative and is recorded as
    ``UNVERIFIED_DECLARATIVE``; it never grants trust by itself.  Trust comes
    from the manifest body matching its own canonical digest and from declared
    locators matching the recorded fixture digests.
    """
    _require(document.get("schema_version") == FIXTURE_MANIFEST_SCHEMA_VERSION,
             "MEDIA_PROVENANCE_UNVERIFIED",
             f"fixture manifest schema_version must be {FIXTURE_MANIFEST_SCHEMA_VERSION}")
    generation = document.get("generation")
    _require(isinstance(generation, Mapping), "MEDIA_PROVENANCE_UNVERIFIED",
             "fixture manifest generation must be an object")
    _require(generation.get("identity_status") == MEDIA_PROVENANCE_GENERATOR_STATUS,
             "MEDIA_PROVENANCE_UNVERIFIED",
             f"generator identity_status must be {MEDIA_PROVENANCE_GENERATOR_STATUS}")
    generator_module = generation.get("module")
    _require(isinstance(generator_module, str) and generator_module.strip(),
             "MEDIA_PROVENANCE_UNVERIFIED", "fixture manifest generator module is missing")

    fixtures = document.get("fixtures")
    _require(isinstance(fixtures, list) and fixtures, "MEDIA_PROVENANCE_UNVERIFIED",
             "fixture manifest fixtures must be a non-empty array")
    digest_to_file: dict[str, str] = {}
    for row in fixtures:
        _require(isinstance(row, Mapping), "MEDIA_PROVENANCE_UNVERIFIED",
                 "fixture manifest row is not an object")
        digest = row.get("digest")
        try:
            validate_digest(digest)
        except ValueError as exc:
            raise MediaInputError("MEDIA_PROVENANCE_UNVERIFIED",
                                  f"fixture manifest digest is invalid: {exc}") from exc
        byte_count = row.get("byte_count")
        _require(isinstance(byte_count, int) and not isinstance(byte_count, bool) and byte_count >= 0,
                 "MEDIA_PROVENANCE_UNVERIFIED", "fixture manifest byte_count must be a non-negative integer")
        file_name = row.get("file")
        _require(isinstance(file_name, str) and file_name.strip() and "/" not in file_name,
                 "MEDIA_PROVENANCE_UNVERIFIED", "fixture manifest file must be a plain file name")
        digest_to_file.setdefault(str(digest), file_name)
    recorded_set_digest = document.get("fixture_set_digest")
    _require(isinstance(recorded_set_digest, str)
             and recorded_set_digest == fixture_manifest_digest(document),
             "MEDIA_PROVENANCE_UNVERIFIED",
             "fixture manifest digest does not match its body")

    try:
        manifest_relative = str(manifest_path.relative_to(root))
    except ValueError:  # pragma: no cover - manifest is always searched under root
        manifest_relative = str(manifest_path)
    return MediaProvenance(
        status=MEDIA_PROVENANCE_BOUND,
        fixture_manifest=manifest_relative,
        fixture_set_digest=str(recorded_set_digest),
        generator_module=str(generator_module),
        generator_identity_status=MEDIA_PROVENANCE_GENERATOR_STATUS,
        fixture_digests=tuple(sorted(digest_to_file)),
    )


def _require_source_provenance(
    input_root: Path, revision: MediaRevision, snapshot: SourceSnapshot
) -> MediaProvenance:
    """Refuse a declared locator that is not part of the generated fixture set."""
    provenance = _load_fixture_provenance(input_root)
    if provenance.status != MEDIA_PROVENANCE_BOUND:
        raise MediaInputError(
            provenance.refusal_reason or "MEDIA_PROVENANCE_UNVERIFIED",
            provenance.refusal_detail or "generated-fixture provenance could not be bound",
        )
    if snapshot.digest not in provenance.fixture_digests:
        raise MediaInputError(
            "SOURCE_DIGEST_MISMATCH",
            f"{revision.locator} digest {snapshot.digest} is not part of the generated fixture set",
        )
    return provenance


def _verify_bound_source(
    input_root: Path, locator: str, snapshot: SourceSnapshot, max_source_bytes: int
) -> None:
    try:
        verify_source(input_root, locator, snapshot, max_bytes=max_source_bytes)
    except SourceGuardError as exc:
        raise _refusal(exc) from exc


def measure_revision(
    revision: MediaRevision,
    *,
    input_root: Path,
    ffprobe_path: str = "ffprobe",
    ffmpeg_path: str = "ffmpeg",
    window_seconds: int = 4,
    probe_timeout_seconds: float = 20.0,
    decode_timeout_seconds: float = 60.0,
    adapter: FfprobeAdapter | None = None,
    max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> MediaMeasurement:
    """Probe and decode one declared revision into measured, digest-bound evidence.

    The source is opened through the bounded no-follow guard, its digest is
    matched against the generated-fixture manifest, and its identity/digest are
    re-verified after the probe and after the decode.  ``max_source_bytes`` may
    only tighten the default quota.
    """
    input_root = Path(input_root)
    try:
        snapshot = snapshot_source(input_root, revision.locator, max_bytes=max_source_bytes)
    except SourceGuardError as exc:
        raise _refusal(exc) from exc
    _require_source_provenance(input_root, revision, snapshot)
    source_path = Path(snapshot.path)

    probe_adapter = adapter or FfprobeAdapter(
        ffprobe_path=ffprobe_path,
        timeout_seconds=probe_timeout_seconds,
        max_source_bytes=max_source_bytes,
    )
    capture = probe_adapter.probe(
        source_path,
        selected_stream_index=revision.selected_stream_index,
        expected_digest=snapshot.digest,
        expected_byte_count=snapshot.byte_count,
    )
    _verify_bound_source(input_root, revision.locator, snapshot, max_source_bytes)
    declared = revision.selected_stream_index
    videos = [stream for stream in capture.streams if stream.stream_type == "video"]
    if declared is None:
        _require(len(videos) == 1, "AMBIGUOUS_STREAM", f"{source_path}: {len(videos)} video streams and no explicit selection")
        selected_index = videos[0].stream_index
    else:
        selected_index = declared
    selection_source = _selection_source(declared)
    time_base = capture.evidence.time_base

    source = RevisionRef(revision.revision_id, revision.content_id, str(source_path), selected_index, selection_source)
    sequence = decode_frames(
        source,
        ffprobe_path=ffprobe_path,
        ffmpeg_path=ffmpeg_path,
        timeout_seconds=decode_timeout_seconds,
        expected_source_digest=capture.source_digest,
        max_source_bytes=max_source_bytes,
    )
    _verify_bound_source(input_root, revision.locator, snapshot, max_source_bytes)
    _require(sequence.stream_index == selected_index, "SELECTED_STREAM_MISMATCH",
             f"{source_path}: decoded stream {sequence.stream_index} != selected {selected_index}")
    _require(tuple(sequence.time_base) == tuple(time_base), "TIME_BASE_MISMATCH",
             f"{source_path}: decoded time base {sequence.time_base} != probed {time_base}")
    _require(sequence.frame_count == len(sequence.frames), "FRAME_COUNT_MISMATCH",
             f"{source_path}: declared {sequence.frame_count} frames, decoded {len(sequence.frames)}")
    _require(len(sequence.frames) > 0, "MISSING_PTS", f"{source_path}: no decoded frames")
    origin = sequence.frames[0].raw_pts_ticks
    _require(isinstance(origin, int) and not isinstance(origin, bool), "MISSING_PTS",
             f"{source_path}: first decoded frame has no integer presentation timestamp")

    measured = _measured_duration(capture, selected_index, time_base)
    required = Fraction(int(window_seconds) * revision.window_count)
    _require(measured >= required, "INVALID_WINDOW_COVERAGE",
             f"{source_path}: measured duration {measured}s does not cover {revision.window_count} window(s) of {window_seconds}s")

    return MediaMeasurement(
        revision=revision,
        capture=capture,
        sequence=sequence,
        selected_stream_index=selected_index,
        selection_source=selection_source,
        origin_pts_ticks=origin,
        window_count=revision.window_count,
        measured_duration=measured,
        source_byte_count=capture.source_byte_count,
        source_digest=capture.source_digest,
    )


def measure_corpus(
    corpus: MediaCorpus,
    *,
    input_root: Path,
    ffprobe_path: str = "ffprobe",
    ffmpeg_path: str = "ffmpeg",
    window_seconds: int = 4,
    max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> tuple[MediaMeasurement, ...]:
    """Measure every declared revision, failing closed on the first bad source."""
    adapter = FfprobeAdapter(ffprobe_path=ffprobe_path, max_source_bytes=max_source_bytes)
    return tuple(
        measure_revision(row, input_root=input_root, ffprobe_path=ffprobe_path, ffmpeg_path=ffmpeg_path,
                         window_seconds=window_seconds, adapter=adapter,
                         max_source_bytes=max_source_bytes)
        for row in corpus.revisions
    )
