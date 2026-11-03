"""Read-only D-2 Owner-input intake validator (deterministic, text-only).

This module evaluates an abstract D-2 intake package against the thirty stable
field IDs of ``docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md`` Part B
and the deterministic state rules of Part C.  It is deliberately *isolated*: it
is not wired into the Gate-0 run CLI, any stage pipeline, or any real-source
execution path, and it never resolves, stat-s, opens, lists, hashes or decodes a
declared corpus/media path.  Only files that resolve (symlinks included) inside
the package directory are read at all.  The package it consumes contains
identifiers, digests, declared values and evidence references only.

Evidence vocabulary: this report describes **input attestation state**, never an
assertion-level evidence class. The only canonical assertion evidence classes
remain MEASURED, MATCHED, VISUALLY_OBSERVED, AUDIO_OBSERVED and
EDITORIAL_INFERENCE. These are not populated or strengthened by this tool.

State semantics (checklist Part C, implemented faithfully):

* ``NOT_OBSERVED`` -- the row requires human judgement or a post-run outcome and
  the observation is not authorized/available; availability, never a pass.
* ``BLOCKED`` -- a required schema field, format, validator or contract-owner
  ruling is missing, or closure depends on a not-authorized operation.  BLOCKED
  outranks PENDING and cannot be overridden by any declaration.
* ``PENDING`` -- no evidence, incomplete evidence, a failed deterministic check,
  or evidence that is deterministically valid but only synthetically attested.
* ``VERIFIED`` -- the deterministic check passed, digest-bound evidence is
  present and Owner authenticity is independently confirmed by a trusted
  external attestation. This source-only validator has no such trust boundary
  and therefore cannot presently emit VERIFIED for an input row.

No output state value may ever be ``AUTHORIZED`` / ``GRANTED`` / ``FROZEN`` /
``PASS``, and no input can grant D-3 authority.  A package that claims an
authorization (in a structured member, free-text notes, mapping keys, or inside a
referenced artifact value -- including free-text values), a placeholder digest, an
absolute/media path, or an unknown/duplicate/missing field ID is refused with
exit 2 rather than partially classified.

Authenticity boundary: software cannot authenticate a text declaration.
Both ``SYNTHETIC_FIXTURE`` and untrusted ``OWNER_SIGNED`` package claims cap
passing rows at PENDING (deterministic checks are reported as VALID). The latter
is ``DECLARED_NOT_AUTHENTICATED``, with ``owner_approval_claimed`` False.
Genuine Owner approval requires a separate independently authenticated
evidence/authority boundary; this validator never manufactures it.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from gate0 import execution, labels
from gate0.canonical_json import canonical_bytes, canonical_text
from gate0.identity import validate_opaque_id

D2_PACKAGE_FILE = "d2-package.json"
D2_PACKAGE_SCHEMA_VERSION = "gate0.d2-intake-package.v1"
D2_REPORT_SCHEMA_VERSION = "gate0.d2-intake-report.v1"
D2_TOOL_VERSION = "gate0.d2-intake-validator.v1"

STATE_VERIFIED = "VERIFIED"
STATE_PENDING = "PENDING"
STATE_BLOCKED = "BLOCKED"
STATE_NOT_OBSERVED = "NOT_OBSERVED"
STATES = (STATE_VERIFIED, STATE_PENDING, STATE_BLOCKED, STATE_NOT_OBSERVED)

RULE_EVIDENCE = "EVIDENCE"
RULE_RULING = "RULING"
RULE_OBSERVATION = "OBSERVATION"

ATTESTATION_SYNTHETIC = "SYNTHETIC_FIXTURE"
ATTESTATION_DECLARED = "DECLARED_NOT_AUTHENTICATED"
AUTHENTICITY_DECLARED = "DECLARED_NOT_AUTHENTICATED"

D2_REASON_SYNTHETIC = "SYNTHETIC_EVIDENCE_CANNOT_VERIFY"
D2_REASON_UNAUTHENTICATED = "DECLARED_EVIDENCE_NOT_AUTHENTICATED"
D2_REASON_OBSERVATION = "OBSERVATION_ONLY_NOT_YET_AUTHORIZED"
D2_REASON_EVIDENCE_MISSING = "EVIDENCE_MISSING"
D2_REASON_ARTIFACT_MISSING = "EVIDENCE_ARTIFACT_MISSING"
D2_REASON_DIGEST_MISMATCH = "EVIDENCE_DIGEST_MISMATCH"
D2_REASON_DECLARATION_INCONSISTENT = "DECLARED_ABSENT_BUT_EVIDENCE_PRESENT"

#: Declared values that are placeholders, never evidence (checklist Part C).
PLACEHOLDER_TOKENS = frozenset({
    "",
    "NOT_OBSERVED",
    "TODO",
    "TBD",
    "PLACEHOLDER",
    "UNKNOWN",
    "NONE",
    "N/A",
    "PENDING",
    "gate0-owner",
})
ZERO_DIGEST = "0" * 64

FORBIDDEN_OUTPUT_STATES = frozenset({"AUTHORIZED", "GRANTED", "FROZEN", "PASS"})
DECLARED_STATUSES = frozenset({"COMPLETE", "PARTIAL", "ABSENT"})

_MEDIA_SUFFIXES = frozenset({
    ".mp4", ".mov", ".mkv", ".avi", ".mxf", ".webm", ".m4v",
    ".wav", ".mp3", ".flac", ".aac", ".m4a", ".aiff",
    ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif",
})
_ATTESTER_KINDS = frozenset({"OWNER_SIGNED", "SYNTHETIC_FIXTURE"})

#: Free-text claim scan (independent review F1).  A D-2 package is metadata; it
#: may not assert a D-3 grant, an absolute corpus root or a media path, whether
#: in ``notes`` or inside a referenced JSON artifact.
_D3_CLAIM_TOKEN = re.compile(r"(?i)\bd-?3[-_ ]?auth")
#: A grant claim needs both an authorization verb *and* a D-3 / operation target
#: nearby.  Requiring the pair keeps ordinary prose ("corpus approved for use")
#: out while still refusing "granted execution authorization" in free-text values.
_CLAIM_VERB = re.compile(
    r"(?i)\b(?:grants?|granted|granting|authori[sz]\w*|permission|approved|frozen|promoted?)\b"
)
#: Targets that turn an authorization verb into a *claim*.  They are
#: authorization objects (``execution authorization``, ``D-3``, corpus access,
#: authorized root), not bare operation nouns, so ordinary prose such as
#: "approved the execution of the jump" is not misread as a grant (round-3 N8).
_CLAIM_TARGET = re.compile(
    r"(?i)\bd-?3(?:[-_ ]?auth\w*)?\b"
    r"|\b(?:execution|processing|discovery)\s+authori[sz]\w*"
    r"|\bcorpus\s+access\b"
    r"|\baccess\s+to\s+(?:the\s+)?(?:real\s+)?corpus\b"
    r"|\bauthori[sz]ed\s+root\b"
    r"|\broot\s+discovery\b"
)
_MEDIA_MENTION = re.compile(
    r"(?i)(?:" + "|".join(re.escape(suffix) for suffix in sorted(_MEDIA_SUFFIXES)) + r")\b"
)
#: Absolute path anywhere in a string, including glued forms (``root=/Users/x``)
#: and standalone tokens; used for notes, mapping keys and artifact values.
_ABSOLUTE_PATH_ANYWHERE = re.compile(
    r"""(?:^|[\s"'`(=:,\[])"""
    r"""(?:/|~[/\\]?|[A-Za-z]:[\\/]|\\\\)"""
    r"""[^\s"'`)\],;]+"""
)

D2_BASELINE_STATES: Mapping[str, str] = {
    "G0-D2-01": STATE_PENDING,
    "G0-D2-02": STATE_BLOCKED,
    "G0-D2-03": STATE_BLOCKED,
    "G0-D2-04": STATE_BLOCKED,
    "G0-D2-05": STATE_BLOCKED,
    "G0-D2-06": STATE_BLOCKED,
    "G0-D2-07": STATE_BLOCKED,
    "G0-D2-08": STATE_BLOCKED,
    "G0-D2-09": STATE_BLOCKED,
    "G0-D2-10": STATE_PENDING,
    "G0-D2-11": STATE_PENDING,
    "G0-D2-12": STATE_PENDING,
    "G0-D2-13": STATE_BLOCKED,
    "G0-D2-14": STATE_PENDING,
    "G0-D2-15": STATE_BLOCKED,
    "G0-D2-16": STATE_BLOCKED,
    "G0-D2-17": STATE_PENDING,
    "G0-D2-18": STATE_NOT_OBSERVED,
    "G0-D2-19": STATE_NOT_OBSERVED,
    "G0-D2-20": STATE_BLOCKED,
    "G0-D2-21": STATE_BLOCKED,
    "G0-D2-22": STATE_BLOCKED,
    "G0-D2-23": STATE_BLOCKED,
    "G0-D2-24": STATE_BLOCKED,
    "G0-D2-25": STATE_BLOCKED,
    "G0-D2-26": STATE_PENDING,
    "G0-D2-27": STATE_BLOCKED,
    "G0-D2-28": STATE_BLOCKED,
    "G0-D2-29": STATE_BLOCKED,
    "G0-D2-30": STATE_BLOCKED,
}

_CHECKLIST = "docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md"


class D2IntakeError(ValueError):
    """Fail-closed D-2 intake refusal carrying a stable reason code."""

    exit_code = 2

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else f"{reason}: {detail}")


@dataclass(frozen=True)
class D2FieldSpec:
    """One frozen row of the thirty-field D-2 matrix."""

    field_id: str
    ordinal: int
    domain: str
    title: str
    controlling_authority: str
    expected_evidence: str
    unresolved_ruling: str
    state_rule: str
    validator: str
    observation_only: bool = False


def _field(field_id, ordinal, domain, title, authority, evidence, ruling,
           state_rule, validator="", observation_only=False) -> D2FieldSpec:
    return D2FieldSpec(
        field_id=field_id,
        ordinal=ordinal,
        domain=domain,
        title=title,
        controlling_authority=authority,
        expected_evidence=evidence,
        unresolved_ruling=ruling,
        state_rule=state_rule,
        validator=validator,
        observation_only=observation_only,
    )


_RULING = RULE_RULING
_OBSERVATION = RULE_OBSERVATION
_EVIDENCE = RULE_EVIDENCE

D2_FIELDS: tuple[D2FieldSpec, ...] = (
    _field("G0-D2-01", 1, "B.1", "Authorized corpus designation (60-120 min, >=3 sessions, >=6 revisions, family coverage)",
           _CHECKLIST + " B.1; docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md (Owner corpus approval)",
           "Text session/revision duration/split/family table plus its recorded digest",
           "", _EVIDENCE, "corpus_designation"),
    _field("G0-D2-02", 2, "B.1", "Rights/ownership basis and attesting authority",
           _CHECKLIST + " B.1; readiness report 5.1 D2-A2 (no accepted rights-basis format)",
           "Signed rights/ownership statement naming authority, scope and constraints",
           "R-03", _RULING),
    _field("G0-D2-03", 3, "B.1", "Source-use and retention policy binding per revision",
           _CHECKLIST + " B.1; config/gate0/default.json retention classes",
           "Per-revision retention class/expiry/reader/cleanup table bound to the declaration",
           "R-04", _RULING),
    _field("G0-D2-04", 4, "B.1", "Sensitivity/consent state",
           _CHECKLIST + " B.1; sensitivity_consent exists only in the runtime schema",
           "Declared sensitivity/consent enum plus constraint note in an Owner record",
           "R-16", _RULING),
    _field("G0-D2-05", 5, "B.1", "Purpose-scoped ALLOW separating discovery from processing",
           _CHECKLIST + " B.1; docs/architecture/CANONICAL_CONTRACTS.md (discovery vs processing)",
           "Owner-authored purpose-scoped ALLOW record with distinct discovery/processing scopes",
           "R-09/R-10", _RULING),
    _field("G0-D2-06", 6, "B.1", "Egress-manifest content plus no-egress policy",
           _CHECKLIST + " B.1; schemas/gate0/config.json policy.egress_manifest_digest only",
           "Egress manifest rows plus policy text and canonical digest",
           "R-05", _RULING),
    _field("G0-D2-07", 7, "B.1", "Inclusion/exclusion decisions per revision",
           _CHECKLIST + " B.1; authorized-local declaration has no reason field",
           "Per-revision exclusion reason list",
           "R-14", _RULING),
    _field("G0-D2-08", 8, "B.1", "Relation grouping (exact-byte / transformed / partial-copy / same-session)",
           _CHECKLIST + " B.1; relation_kind enum undefined",
           "Relation pairs with a defined relation_kind vocabulary",
           "R-16", _RULING),
    _field("G0-D2-09", 9, "B.1", "Source-disjoint development/evaluation partition (development 10-15 min)",
           _CHECKLIST + " B.1; readiness report section 3 (inventory requires separate D-3 grant)",
           "D-3 source inventory plus frozen split table",
           "R-14/D-3-AUTH-1", _RULING),
    _field("G0-D2-10", 10, "B.2", "24 positive editor queries, 6 per family",
           _CHECKLIST + " B.2; src/gate0/execution.py load_editor_queries + labels.build_queries",
           "Canonical editor-queries artifact passing the existing loaders (24 positives, 6 per family)",
           "", _EVIDENCE, "editor_query_matrix"),
    _field("G0-D2-11", 11, "B.2", "8 plausible-absent editor queries",
           _CHECKLIST + " B.2; src/gate0/labels.py PRESENCE/absent cardinality",
           "Canonical editor-queries artifact with exactly 8 EVALUATION ABSENT rows",
           "", _EVIDENCE, "editor_query_absent"),
    _field("G0-D2-12", 12, "B.2", "8 development queries distinct from evaluation",
           _CHECKLIST + " B.2; src/gate0/labels.py development cardinality",
           "Canonical editor-queries artifact with exactly 8 DEVELOPMENT rows disjoint from EVALUATION",
           "", _EVIDENCE, "editor_query_development"),
    _field("G0-D2-13", 13, "B.2", "Frozen query/split/gold/rubric/reviewer/config/threshold digests",
           _CHECKLIST + " B.2; readiness report 2.2 (no freeze-approval format or config anchor)",
           "Approved freeze record anchored to an approved canonical config digest",
           "R-11", _RULING),
    _field("G0-D2-14", 14, "B.3", "Two named reviewers",
           _CHECKLIST + " B.3; config/gate0/default.json policy.reviewer_ids; reviewer envelope two-identity rule",
           "Reviewer appointment artifact naming exactly two distinct opaque reviewer ids",
           "", _EVIDENCE, "reviewer_appointment"),
    _field("G0-D2-15", 15, "B.3", "Reviewer independence criteria and declaration",
           _CHECKLIST + " B.3; readiness report ruling queue R-01",
           "Independence declaration per reviewer under a defined criteria set",
           "R-01", _RULING),
    _field("G0-D2-16", 16, "B.3", "Adjudicator appointment and procedure",
           _CHECKLIST + " B.3; no adjudication schema field exists",
           "Adjudicator appointment plus provenance/procedure record",
           "R-02", _RULING),
    _field("G0-D2-17", 17, "B.3", "Blinding values, token map and access scope",
           _CHECKLIST + " B.3; config/gate0/default.json blinding.token_map",
           "Two blind arm tokens mapped to two distinct arm ids with visible/hidden field scope",
           "", _EVIDENCE, "blinding_declaration"),
    _field("G0-D2-18", 18, "B.3", "Two-reviewer full-corpus catalog grades 0/1/2 with interval uncertainty",
           _CHECKLIST + " B.3; requires real reviewer media access (D-3-AUTH-2)",
           "Authentic two-reviewer graded catalog under a frozen label version",
           "D-3-AUTH-2", _OBSERVATION, observation_only=True),
    _field("G0-D2-19", 19, "B.3", "Post-ranking blinded top-ten-union audit",
           _CHECKLIST + " B.3; audit format undefined and requires a scored run",
           "Post-run blinded audit record under the approved audit format",
           "R-18", _OBSERVATION, observation_only=True),
    _field("G0-D2-20", 20, "B.4", "Offline model identity/weights/processor/dimension plus public licence",
           _CHECKLIST + " B.4; schemas/gate0/config.json model block lacks licence",
           "Model identity table, weights SHA-256, processor digest, dimension and vendor licence evidence",
           "R-06", _RULING),
    _field("G0-D2-21", 21, "B.4", "Runtime precision, preprocessing, pooling, space id and tie rule frozen",
           _CHECKLIST + " B.4; frozen model schema lacks runtime_precision/preprocessing_digest/model_root/revision",
           "Frozen runtime/preprocessing definition carried by an approved schema binding",
           "R-06", _RULING),
    _field("G0-D2-22", 22, "B.4", "Host and sandbox/child-boundary attestation",
           _CHECKLIST + " B.4; sandbox schema forbids sandbox_id; preflight binding exits 20",
           "Host choice record plus sandbox/child-boundary attestation under an approved schema",
           "R-07/R-08", _RULING),
    _field("G0-D2-23", 23, "B.4", "Dependency lock, no-install, BLAS and cache discipline",
           _CHECKLIST + " B.4; requirements/gate0.lock pins pytest only",
           "Full dependency lock plus no-install/BLAS/cache evidence under a separate authorization",
           "dependency-authorization", _RULING),
    _field("G0-D2-24", 24, "B.5", "Configuration freeze approval",
           _CHECKLIST + " B.5; readiness report 2.2 (no freeze-approval format)",
           "Approved configuration-freeze record anchored to the approved config digest",
           "R-11", _RULING),
    _field("G0-D2-25", 25, "B.5", "Explicit execution authorization",
           _CHECKLIST + " B.5; D-3 remains NOT_AUTHORIZED (no artifact format exists)",
           "A separately granted D-3 execution authorization record",
           "R-10/D-3-AUTH-3", _RULING),
    _field("G0-D2-26", 26, "B.5", "gate_owner_id bound and equal across config and manifest",
           _CHECKLIST + " B.5; config/gate0/default.json carries the placeholder gate0-owner",
           "Owner-binding artifact with equal, non-placeholder config and manifest gate_owner_id",
           "", _EVIDENCE, "owner_binding"),
    _field("G0-D2-27", 27, "B.5", "Post-run Owner acceptance and signed promotion record",
           _CHECKLIST + " B.5; promotion/acceptance record format undefined",
           "Signed post-run Owner acceptance/promotion record",
           "R-15", _RULING),
    _field("G0-D2-28", 28, "B.5", "Real review_input.authorized_root and file digest",
           _CHECKLIST + " B.5; current root is a test fixture; erratum-bound format only",
           "Real authorized root plus digest bound by a later authorized erratum/grant",
           "D-3-AUTH-2", _RULING),
    _field("G0-D2-29", 29, "B.5", "Retention/cleanup/tombstone execution authority",
           _CHECKLIST + " B.5; no retention execution authority exists",
           "Retention/cleanup/tombstone execution authorization",
           "R-04/D-3-AUTH-3", _RULING),
    _field("G0-D2-30", 30, "B.5", "Discovery authorization scope (DISCOVER/HASH/PROBE only)",
           _CHECKLIST + " B.5; schemas/gate0/discovery_authorizations.json is PDP-emitted, not Owner intake",
           "Owner-authored discovery authorization with a named root and DISCOVER/HASH/PROBE scope",
           "R-09", _RULING),
)

D2_FIELD_IDS: tuple[str, ...] = tuple(field.field_id for field in D2_FIELDS)
D2_FIELD_BY_ID: Mapping[str, D2FieldSpec] = {field.field_id: field for field in D2_FIELDS}
assert len(D2_FIELDS) == 30
assert len(D2_FIELD_BY_ID) == 30


# ---------------------------------------------------------------------------
# package loading (fail-closed; only package files are ever touched)
# ---------------------------------------------------------------------------

def _canonical_document_bytes(document: Any) -> bytes:
    return canonical_bytes(document)


def _document_digest(document: Any) -> str:
    return hashlib.sha256(_canonical_document_bytes(document)).hexdigest()


def _require(condition: bool, reason: str, detail: str = "") -> None:
    if not condition:
        raise D2IntakeError(reason, detail)


def _is_hex_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value != ZERO_DIGEST
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value.strip() in PLACEHOLDER_TOKENS


def _validate_artifact_reference(artifact: Any, field_id: str) -> str:
    _require(isinstance(artifact, str) and bool(artifact), "D2_PACKAGE_INVALID",
             f"{field_id}: evidence artifact must be a non-empty string")
    if artifact.startswith("/") or ":" in artifact.split("/")[0]:
        raise D2IntakeError("D2_PACKAGE_PATH_ESCAPE", f"{field_id}: {artifact}")
    parts = artifact.split("/")
    if any(part in {"..", ""} for part in parts):
        raise D2IntakeError("D2_PACKAGE_PATH_ESCAPE", f"{field_id}: {artifact}")
    if Path(artifact).suffix.lower() in _MEDIA_SUFFIXES:
        raise D2IntakeError("D2_MEDIA_PATH_DECLARED", f"{field_id}: {artifact}")
    return artifact


def _is_grant_claim(text: str) -> bool:
    """True when an authorization verb sits near a D-3 / operation target."""

    for match in _CLAIM_VERB.finditer(text):
        window = text[max(0, match.start() - 48): match.end() + 60]
        if _CLAIM_TARGET.search(window):
            return True
    return False


def _scan_text_claims(text: str, where: str) -> None:
    """Refuse D-3 grants, absolute roots and media paths inside package text.

    Applied to every string leaf, mapping key and note -- including free-text
    prose -- so a claim cannot hide behind a key named ``text``.
    """

    for segment in text.replace("\r", "\n").split("\n"):
        stripped = segment.strip()
        if not stripped:
            continue
        if _ABSOLUTE_PATH_ANYWHERE.search(stripped):
            raise D2IntakeError("D2_PACKAGE_PATH_ESCAPE", where)
        if _MEDIA_MENTION.search(stripped):
            raise D2IntakeError("D2_MEDIA_PATH_DECLARED", where)
        if _D3_CLAIM_TOKEN.search(stripped):
            raise D2IntakeError("D2_AUTHORIZATION_CLAIMED", where)
        if _is_grant_claim(stripped):
            raise D2IntakeError("D2_AUTHORIZATION_CLAIMED", where)


def _scan_document_claims(document: Any, where: str) -> None:
    """Recursively scan a package artifact for D-3 grants and real media roots."""

    stack: list[tuple[str, Any]] = [("", document)]
    while stack:
        path, node = stack.pop()
        if isinstance(node, Mapping):
            for key, value in node.items():
                key_text = str(key)
                if any(fragment in key_text.lower() for fragment in _SUSPICIOUS_KEY_FRAGMENTS):
                    raise D2IntakeError("D2_AUTHORIZATION_CLAIMED", f"{where}{path}/{key_text}")
                # Keys are data too: the full claim/path/media scan applies, so
                # a D-3 token, absolute/media path or grant wording cannot be a
                # key (round-3 N2/N7).
                _scan_text_claims(key_text, f"{where}{path}/{key_text}")
                stack.append((f"{path}/{key_text}", value))
        elif isinstance(node, list):
            for item in node:
                stack.append((path, item))
        elif isinstance(node, str):
            _scan_text_claims(node, f"{where}{path}")


class _StrictObject(dict):
    """JSON object that records duplicate member names."""


def _strict_object(pairs: Sequence[tuple[str, Any]]) -> _StrictObject:
    result = _StrictObject()
    duplicates: list[str] = []
    for key, value in pairs:
        if key in result:
            duplicates.append(key)
        result[key] = value
    result.duplicate_keys = tuple(duplicates)
    return result


def _nested_duplicate_members(document: Any) -> tuple[str, ...]:
    """Duplicate member names at any depth (``json`` calls the hook recursively)."""

    found: set[str] = set()
    stack: list[Any] = [document]
    while stack:
        node = stack.pop()
        if isinstance(node, Mapping):
            found.update(getattr(node, "duplicate_keys", ()))
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return tuple(sorted(found))


def _load_strict_json(path: Path) -> Mapping[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise D2IntakeError("D2_PACKAGE_NOT_FOUND", str(path)) from exc
    try:
        document = json.loads(text, object_pairs_hook=_strict_object)
    except json.JSONDecodeError as exc:
        raise D2IntakeError("D2_PACKAGE_INVALID", f"package manifest is not valid JSON: {exc}") from exc
    _require(isinstance(document, Mapping), "D2_PACKAGE_INVALID", "package manifest must be an object")
    stack: list[Any] = [document]
    while stack:
        node = stack.pop()
        if isinstance(node, _StrictObject):
            for key in node.duplicate_keys:
                if key.startswith("G0-D2-"):
                    raise D2IntakeError("D2_FIELD_ID_DUPLICATE", key)
                raise D2IntakeError("D2_PACKAGE_INVALID", f"duplicate member {key}")
            stack.extend(node.values())
        elif isinstance(node, Mapping):
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return document


@dataclass(frozen=True)
class D2Package:
    """Lexically validated D-2 intake package (declared, never observed)."""

    package_dir: Path
    package_id: str
    fixture: bool
    attester_id: str
    attester_kind: str
    package_digest: str
    field_records: Mapping[str, Mapping[str, Any]]
    artifact_names: tuple[str, ...]

    def artifact_path(self, name: str) -> Path:
        """Resolve a package-relative artifact, refusing any escape or symlink.

        The resolved real path must stay inside the package directory, so a
        symlinked artifact cannot be followed outside it.
        """

        root = self.package_dir.resolve()
        try:
            resolved = (self.package_dir / name).resolve(strict=True)
        except FileNotFoundError as exc:
            raise D2IntakeError(D2_REASON_ARTIFACT_MISSING, name) from exc
        except OSError as exc:
            raise D2IntakeError("D2_ARTIFACT_INVALID", f"{name}: {exc}") from exc
        if not resolved.is_relative_to(root):
            raise D2IntakeError("D2_PACKAGE_PATH_ESCAPE", name)
        if not resolved.is_file():
            raise D2IntakeError("D2_ARTIFACT_INVALID", f"{name}: not a regular file")
        return resolved

    def artifact_json(self, name: str) -> Mapping[str, Any]:
        path = self.artifact_path(name)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise D2IntakeError("D2_ARTIFACT_INVALID", f"{name}: {exc}") from exc
        try:
            document = json.loads(text, object_pairs_hook=_strict_object)
        except json.JSONDecodeError as exc:
            raise D2IntakeError("D2_ARTIFACT_INVALID", f"{name}: not valid JSON: {exc}") from exc
        duplicates = _nested_duplicate_members(document)
        if duplicates:
            raise D2IntakeError("D2_ARTIFACT_INVALID",
                                f"{name}: duplicate members {sorted(duplicates)}")
        _require(isinstance(document, Mapping), "D2_ARTIFACT_INVALID",
                 f"{name}: artifact must be a JSON object")
        _scan_document_claims(document, name)
        return document

    def artifact_digest(self, name: str) -> str:
        return _document_digest(self.artifact_json(name))


_ALLOWED_PACKAGE_KEYS = frozenset({
    "schema_version", "package_id", "fixture", "attestation", "fields", "notes",
})
_ALLOWED_FIELD_KEYS = frozenset({"declared_status", "evidence", "notes"})
_ATTESTATION_KEYS = frozenset({"attester_id", "attester_kind"})
_EVIDENCE_KEYS = frozenset({"artifact", "digest"})
_SUSPICIOUS_KEY_FRAGMENTS = ("authoriz", "grant", "approv", "frozen", "d3_")


def load_d2_package(package_dir: str | Path) -> D2Package:
    """Load and lexically validate a D-2 intake package directory.

    Nothing outside ``package_dir`` is read, and no declared corpus path is ever
    resolved.  Malformed packages are refused with :class:`D2IntakeError`.
    """

    root = Path(package_dir)
    if not root.is_dir():
        raise D2IntakeError("D2_PACKAGE_NOT_FOUND", str(root))
    manifest_path = root / D2_PACKAGE_FILE
    if not manifest_path.is_file():
        raise D2IntakeError("D2_PACKAGE_NOT_FOUND", str(manifest_path))

    document = _load_strict_json(manifest_path)
    unknown = set(document) - _ALLOWED_PACKAGE_KEYS
    if unknown:
        detail = ", ".join(sorted(unknown))
        if any(fragment in key.lower() for key in unknown for fragment in _SUSPICIOUS_KEY_FRAGMENTS):
            raise D2IntakeError("D2_AUTHORIZATION_CLAIMED", detail)
        raise D2IntakeError("D2_PACKAGE_INVALID", f"unknown package members: {detail}")

    _require(document.get("schema_version") == D2_PACKAGE_SCHEMA_VERSION,
             "D2_PACKAGE_SCHEMA_MISMATCH", str(document.get("schema_version")))

    package_id = document.get("package_id")
    _require(isinstance(package_id, str), "D2_PACKAGE_INVALID", "package_id must be a string")
    try:
        validate_opaque_id(package_id)
    except ValueError as exc:
        raise D2IntakeError("D2_PACKAGE_INVALID", f"package_id: {exc}") from exc

    fixture = document.get("fixture")
    _require(isinstance(fixture, bool), "D2_PACKAGE_INVALID", "fixture must be a boolean")

    package_notes = document.get("notes", "")
    _require(isinstance(package_notes, str), "D2_PACKAGE_INVALID", "notes must be text")
    _scan_text_claims(package_notes, "package notes")

    attestation = document.get("attestation")
    _require(isinstance(attestation, Mapping), "D2_ATTESTATION_INVALID",
             "attestation must be an object")
    _require(set(attestation) == _ATTESTATION_KEYS, "D2_ATTESTATION_INVALID",
             "attestation members are exactly attester_id and attester_kind")
    attester_id = attestation["attester_id"]
    attester_kind = attestation["attester_kind"]
    _require(isinstance(attester_id, str), "D2_ATTESTATION_INVALID", "attester_id must be a string")
    try:
        validate_opaque_id(attester_id)
    except ValueError as exc:
        raise D2IntakeError("D2_ATTESTATION_INVALID", f"attester_id: {exc}") from exc
    _require(attester_kind in _ATTESTER_KINDS, "D2_ATTESTATION_INVALID",
             f"attester_kind must be one of {sorted(_ATTESTER_KINDS)}")
    _require(fixture == (attester_kind == "SYNTHETIC_FIXTURE"), "D2_ATTESTATION_INVALID",
             "fixture marker must match attester_kind")

    fields = document.get("fields")
    _require(isinstance(fields, Mapping), "D2_PACKAGE_INVALID", "fields must be an object")
    field_ids = list(fields)
    unknown_fields = [field_id for field_id in field_ids if field_id not in D2_FIELD_BY_ID]
    if unknown_fields:
        raise D2IntakeError("D2_FIELD_ID_UNKNOWN", ", ".join(sorted(unknown_fields)))
    missing_fields = [field_id for field_id in D2_FIELD_IDS if field_id not in fields]
    if missing_fields:
        raise D2IntakeError("D2_FIELD_ID_MISSING", ", ".join(missing_fields))

    records: dict[str, Mapping[str, Any]] = {}
    artifact_names: set[str] = set()
    for field_id in D2_FIELD_IDS:
        record = fields[field_id]
        _require(isinstance(record, Mapping), "D2_FIELD_RECORD_INVALID",
                 f"{field_id}: record must be an object")
        declarable = set(record) - _ALLOWED_FIELD_KEYS
        if declarable:
            detail = ", ".join(sorted(declarable))
            if any(fragment in key.lower() for key in declarable
                   for fragment in _SUSPICIOUS_KEY_FRAGMENTS):
                raise D2IntakeError("D2_AUTHORIZATION_CLAIMED", f"{field_id}: {detail}")
            raise D2IntakeError("D2_FIELD_RECORD_INVALID", f"{field_id}: {detail}")
        declared_status = record.get("declared_status", "ABSENT")
        if declared_status in FORBIDDEN_OUTPUT_STATES:
            raise D2IntakeError("D2_AUTHORIZATION_CLAIMED", f"{field_id}: {declared_status}")
        _require(declared_status in DECLARED_STATUSES, "D2_FIELD_RECORD_INVALID",
                 f"{field_id}: unsupported declared_status {declared_status!r}")
        notes = record.get("notes", "")
        _require(isinstance(notes, str), "D2_FIELD_RECORD_INVALID", f"{field_id}: notes must be text")
        _scan_text_claims(notes, f"{field_id} notes")
        evidence = record.get("evidence", [])
        _require(isinstance(evidence, list), "D2_FIELD_RECORD_INVALID",
                 f"{field_id}: evidence must be a list")
        for entry in evidence:
            _require(isinstance(entry, Mapping) and set(entry) == _EVIDENCE_KEYS,
                     "D2_EVIDENCE_INVALID",
                     f"{field_id}: evidence entries are exactly artifact and digest")
            artifact = _validate_artifact_reference(entry["artifact"], field_id)
            if not _is_hex_digest(entry["digest"]):
                raise D2IntakeError("D2_PLACEHOLDER_EVIDENCE",
                                    f"{field_id}: {artifact} digest is a placeholder or malformed")
            artifact_names.add(artifact)
        records[field_id] = {
            "declared_status": declared_status,
            "evidence": tuple(dict(entry) for entry in evidence),
            "notes": notes,
        }

    package = D2Package(
        package_dir=root,
        package_id=package_id,
        fixture=fixture,
        attester_id=attester_id,
        attester_kind=attester_kind,
        package_digest=_document_digest(document),
        field_records=records,
        artifact_names=tuple(sorted(artifact_names)),
    )
    # Pre-load every referenced artifact so a D-3 grant, absolute root, media
    # path, symlink escape or malformed artifact refuses the whole package
    # (exit 2) instead of only degrading one row to PENDING.  A *missing*
    # artifact stays a per-row PENDING condition.
    for artifact in package.artifact_names:
        try:
            package.artifact_json(artifact)
        except D2IntakeError as exc:
            if exc.reason == D2_REASON_ARTIFACT_MISSING:
                continue
            raise
    return package


# ---------------------------------------------------------------------------
# deterministic per-field checks (pure lexical/artifact validation)
# ---------------------------------------------------------------------------

def _fail(reason: str, detail: str = "") -> tuple[bool, tuple[str, ...]]:
    """Return an exact machine-readable failure code (detail is advisory only)."""
    del detail
    return False, (reason,)


def _pass() -> tuple[bool, tuple[str, ...]]:
    return True, ()


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _opaque(value: Any) -> bool:
    if not isinstance(value, str) or _is_placeholder(value):
        return False
    try:
        validate_opaque_id(value)
    except ValueError:
        return False
    return True


def _check_corpus_designation(package: D2Package):
    try:
        document = package.artifact_json("corpus-designation.json")
    except D2IntakeError as exc:
        return _fail(exc.reason)
    sessions = document.get("sessions")
    revisions = document.get("revisions")
    coverage = document.get("family_coverage")
    if not isinstance(sessions, list) or not isinstance(revisions, list):
        return _fail("D2_CORPUS_DESIGNATION_INVALID", "sessions/revisions must be lists")
    if not isinstance(coverage, list) or set(coverage) != set(labels.FAMILIES):
        return _fail("D2_CORPUS_FAMILY_COVERAGE_INVALID", "all four label families are required")
    session_ids = []
    for session in sessions:
        if not isinstance(session, Mapping):
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "session must be an object")
        if not _opaque(session.get("session_id")):
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "session_id must be an opaque id")
        if not _is_int(session.get("duration_minutes")) or session["duration_minutes"] <= 0:
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "session duration must be positive integer minutes")
        session_ids.append(session["session_id"])
    if len(sessions) < 3:
        return _fail("D2_CORPUS_SESSION_COUNT_INVALID", "at least three sessions are required")
    if len(set(session_ids)) != len(session_ids):
        return _fail("D2_CORPUS_DESIGNATION_INVALID", "duplicate session identity")
    revision_ids = []
    covered_families: set[str] = set()
    total_minutes = 0
    for revision in revisions:
        if not isinstance(revision, Mapping):
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "revision must be an object")
        if not _opaque(revision.get("revision_id")):
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "revision_id must be an opaque id")
        if revision.get("session_id") not in set(session_ids):
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "revision references an unknown session")
        if not _is_int(revision.get("duration_minutes")) or revision["duration_minutes"] <= 0:
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "revision duration must be positive integer minutes")
        if revision.get("split") not in {"EVALUATION", "DEVELOPMENT"}:
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "split must be EVALUATION or DEVELOPMENT")
        families = revision.get("families")
        if not isinstance(families, list) or not families or set(families) - set(labels.FAMILIES):
            return _fail("D2_CORPUS_DESIGNATION_INVALID", "revision families must be label families")
        covered_families |= set(families)
        revision_ids.append(revision["revision_id"])
        total_minutes += revision["duration_minutes"]
    if len(revisions) < 6:
        return _fail("D2_CORPUS_REVISION_COUNT_INVALID", "at least six revisions are required")
    if len(set(revision_ids)) != len(revision_ids):
        return _fail("D2_CORPUS_DESIGNATION_INVALID", "duplicate revision identity")
    if not 60 <= total_minutes <= 120:
        return _fail("D2_CORPUS_DURATION_INVALID", f"declared total {total_minutes} not in 60..120")
    if covered_families != set(labels.FAMILIES):
        return _fail("D2_CORPUS_FAMILY_COVERAGE_INVALID", "not every family has a designated revision")
    if sum(row["split"] == "DEVELOPMENT" for row in revisions) < 1:
        return _fail("D2_CORPUS_DESIGNATION_INVALID", "a development revision is required")
    return _pass()


def _load_query_matrix(package: D2Package):
    path = package.artifact_path("editor-queries.json")
    try:
        document = package.artifact_json("editor-queries.json")
        rows = execution.load_editor_queries(path)
        query_version = document.get("query_version")
        if not isinstance(query_version, str) or not query_version:
            return None, _fail("AUTHORIZED_EDITOR_QUERIES_INVALID", "query_version")
        specs = [(row["query_id"], row["text"], (row["family"], row["presence"])) for row in rows]
        split_by_id = {row["query_id"]: row["split"] for row in rows}
        labels.build_queries(specs, split_by_id, query_version)
    except D2IntakeError as exc:
        return None, _fail(exc.reason)
    except execution.AuthorizedLocalError as exc:
        return None, _fail(exc.reason)
    except ValueError as exc:
        return None, _fail("D2_EDITOR_QUERY_INVALID", str(exc))
    return rows, _pass()


def _check_editor_query_matrix(package: D2Package):
    rows, verdict = _load_query_matrix(package)
    if rows is None:
        return verdict
    try:
        execution._authorized_query_cardinality(rows)
    except execution.AuthorizedLocalError as exc:
        return _fail(exc.reason, exc.detail)
    return _pass()


def _check_editor_query_absent(package: D2Package):
    rows, verdict = _load_query_matrix(package)
    if rows is None:
        return verdict
    absent = [row for row in rows if row["presence"] == "ABSENT"]
    if len(absent) != execution.EVALUATION_ABSENT_COUNT:
        return _fail("D2_EDITOR_ABSENT_COUNT_INVALID",
                     f"{len(absent)} absent rows, expected {execution.EVALUATION_ABSENT_COUNT}")
    if any(row["split"] != "EVALUATION" for row in absent):
        return _fail("D2_EDITOR_ABSENT_COUNT_INVALID", "absent rows must be EVALUATION split")
    return _pass()


def _check_editor_query_development(package: D2Package):
    rows, verdict = _load_query_matrix(package)
    if rows is None:
        return verdict
    development = [row for row in rows if row["split"] == "DEVELOPMENT"]
    evaluation = [row for row in rows if row["split"] == "EVALUATION"]
    if len(development) != execution.DEVELOPMENT_QUERY_COUNT:
        return _fail("D2_EDITOR_DEVELOPMENT_COUNT_INVALID",
                     f"{len(development)} development rows, expected {execution.DEVELOPMENT_QUERY_COUNT}")
    evaluation_ids = {row["query_id"] for row in evaluation}
    evaluation_text = {row["text"] for row in evaluation}
    if any(row["query_id"] in evaluation_ids or row["text"] in evaluation_text for row in development):
        return _fail("D2_EDITOR_DEVELOPMENT_OVERLAP", "development rows overlap evaluation rows")
    return _pass()


def _check_reviewer_appointment(package: D2Package):
    try:
        document = package.artifact_json("reviewers.json")
    except D2IntakeError as exc:
        return _fail(exc.reason)
    reviewer_ids = document.get("reviewer_ids")
    if not isinstance(reviewer_ids, list) or len(reviewer_ids) != 2:
        return _fail("D2_REVIEWER_COUNT_INVALID", "exactly two named reviewers are required")
    if not all(_opaque(reviewer_id) for reviewer_id in reviewer_ids):
        return _fail("D2_REVIEWER_IDENTITY_INVALID", "reviewer ids must be opaque non-placeholder ids")
    if len(set(reviewer_ids)) != 2:
        return _fail("D2_REVIEWER_IDENTITY_INVALID", "reviewer ids must be distinct")
    authority = document.get("appointment_authority")
    if not isinstance(authority, str) or not authority.strip() or _is_placeholder(authority):
        return _fail("D2_REVIEWER_APPOINTMENT_INVALID", "appointment authority is required")
    return _pass()


def _check_blinding_declaration(package: D2Package):
    try:
        document = package.artifact_json("blinding.json")
    except D2IntakeError as exc:
        return _fail(exc.reason)
    token_map = document.get("token_map")
    if not isinstance(token_map, list) or len(token_map) != 2:
        return _fail("D2_BLINDING_TOKEN_MAP_INVALID", "exactly two blind arm tokens are required")
    tokens, arms = [], []
    for row in token_map:
        if not isinstance(row, Mapping) or set(row) != {"blind_arm_token", "arm_id"}:
            return _fail("D2_BLINDING_TOKEN_MAP_INVALID", "token_map rows are token/arm pairs")
        token, arm = row["blind_arm_token"], row["arm_id"]
        if not isinstance(token, str) or not token.strip() or _is_placeholder(token):
            return _fail("D2_BLINDING_TOKEN_MAP_INVALID", "blind_arm_token is required")
        if not _opaque(arm):
            return _fail("D2_BLINDING_TOKEN_MAP_INVALID", "arm_id must be a distinct opaque id")
        tokens.append(token)
        arms.append(arm)
    if len(set(tokens)) != 2 or len(set(arms)) != 2:
        return _fail("D2_BLINDING_TOKEN_MAP_INVALID", "tokens and arms must both be distinct")
    visible = document.get("reviewer_visible_fields")
    hidden = document.get("reviewer_hidden_fields")
    if not isinstance(visible, list) or not visible or set(visible) - {"blind_arm_token"}:
        return _fail("D2_BLINDING_TOKEN_MAP_INVALID",
                     "only blind_arm_token may be reviewer-visible")
    if not isinstance(hidden, list) or "arm_id" not in hidden:
        return _fail("D2_BLINDING_TOKEN_MAP_INVALID", "arm_id must be reviewer-hidden")
    if set(visible) & set(hidden):
        return _fail("D2_BLINDING_TOKEN_MAP_INVALID", "a field cannot be visible and hidden")
    return _pass()


def _check_owner_binding(package: D2Package):
    try:
        document = package.artifact_json("owner-binding.json")
    except D2IntakeError as exc:
        return _fail(exc.reason)
    config_owner = document.get("config_gate_owner_id")
    manifest_owner = document.get("manifest_gate_owner_id")
    if not isinstance(config_owner, str) or not isinstance(manifest_owner, str):
        return _fail("D2_OWNER_BINDING_INVALID", "both gate_owner_id values must be text")
    if _is_placeholder(config_owner) or _is_placeholder(manifest_owner):
        return _fail("D2_OWNER_BINDING_PLACEHOLDER", "gate_owner_id is a placeholder")
    if config_owner != manifest_owner:
        return _fail("D2_OWNER_BINDING_INVALID", "gate_owner_id must be equal across config and manifest")
    return _pass()


_FIELD_VALIDATORS = {
    "corpus_designation": _check_corpus_designation,
    "editor_query_matrix": _check_editor_query_matrix,
    "editor_query_absent": _check_editor_query_absent,
    "editor_query_development": _check_editor_query_development,
    "reviewer_appointment": _check_reviewer_appointment,
    "blinding_declaration": _check_blinding_declaration,
    "owner_binding": _check_owner_binding,
}


# ---------------------------------------------------------------------------
# state classification and report
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class D2FieldResult:
    field_id: str
    ordinal: int
    domain: str
    title: str
    state: str
    declared_status: str
    validator_check: str
    controlling_authority: str
    expected_evidence: str
    unresolved_ruling: str
    reasons: tuple[str, ...]
    evidence_digests: tuple[Mapping[str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "ordinal": self.ordinal,
            "domain": self.domain,
            "title": self.title,
            "state": self.state,
            "declared_status": self.declared_status,
            "validator_check": self.validator_check,
            "controlling_authority": self.controlling_authority,
            "expected_evidence": self.expected_evidence,
            "unresolved_ruling": self.unresolved_ruling,
            "reasons": list(self.reasons),
            "evidence_digests": [dict(entry) for entry in self.evidence_digests],
        }


@dataclass(frozen=True)
class D2IntakeReport:
    package_id: str
    package_digest: str
    attestation_state: str
    authenticity: str
    owner_approval_claimed: bool
    execution_authorized: bool
    counts: Mapping[str, int]
    complete: bool
    exit_code: int
    results: tuple[D2FieldResult, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": D2_REPORT_SCHEMA_VERSION,
            "tool_version": D2_TOOL_VERSION,
            "authority": (
                "docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md Part B/C; "
                "this report classifies text-only declarations and grants nothing"
            ),
            "package_id": self.package_id,
            "package_digest": self.package_digest,
            "attestation_state": self.attestation_state,
            "authenticity": self.authenticity,
            "owner_approval_claimed": self.owner_approval_claimed,
            "execution_authorized": self.execution_authorized,
            "d3_status": "NOT_AUTHORIZED",
            "states": list(STATES),
            "counts": dict(self.counts),
            "complete": self.complete,
            "exit_code": self.exit_code,
            "results": [row.as_dict() for row in self.results],
        }


def _evidence_binding(package: D2Package, evidence: Sequence[Mapping[str, str]]):
    if not evidence:
        return _fail(D2_REASON_EVIDENCE_MISSING, "no digest-bound evidence is recorded")
    digests = []
    for entry in evidence:
        artifact = entry["artifact"]
        try:
            computed = package.artifact_digest(artifact)
        except D2IntakeError as exc:
            return _fail(exc.reason, artifact)
        if computed != entry["digest"]:
            return _fail(D2_REASON_DIGEST_MISMATCH, artifact)
        digests.append({"artifact": artifact, "digest": computed})
    return True, tuple(digests)


def _evaluate_field(package: D2Package, spec: D2FieldSpec) -> D2FieldResult:
    record = package.field_records[spec.field_id]
    declared_status = record["declared_status"]
    evidence = record["evidence"]

    def result(state: str, check: str, reasons: tuple[str, ...],
               digests: tuple[Mapping[str, str], ...] = ()) -> D2FieldResult:
        return D2FieldResult(
            field_id=spec.field_id,
            ordinal=spec.ordinal,
            domain=spec.domain,
            title=spec.title,
            state=state,
            declared_status=declared_status,
            validator_check=check,
            controlling_authority=spec.controlling_authority,
            expected_evidence=spec.expected_evidence,
            unresolved_ruling=spec.unresolved_ruling,
            reasons=reasons,
            evidence_digests=digests,
        )

    if spec.state_rule == RULE_OBSERVATION:
        return result(STATE_NOT_OBSERVED, "NOT_APPLICABLE", (D2_REASON_OBSERVATION,))
    if spec.state_rule == RULE_RULING:
        return result(STATE_BLOCKED, "NOT_EVALUATED", (f"UNRESOLVED_RULING={spec.unresolved_ruling}",))

    if declared_status == "ABSENT" and evidence:
        # A row declared absent cannot be verified by evidence it says is absent.
        return result(STATE_PENDING, "INVALID", (D2_REASON_DECLARATION_INCONSISTENT,))

    binding = _evidence_binding(package, evidence)
    if binding[0] is False:
        return result(STATE_PENDING, "INVALID", binding[1])
    digests = binding[1]

    validator = _FIELD_VALIDATORS[spec.validator]
    try:
        passed, reasons = validator(package)
    except execution.AuthorizedLocalError as exc:
        passed, reasons = False, (exc.reason,)
    except ValueError as exc:
        passed, reasons = False, (f"D2_FIELD_CHECK_INVALID: {exc}",)
    if not passed:
        return result(STATE_PENDING, "INVALID", reasons, digests)
    if package.fixture:
        return result(STATE_PENDING, "VALID", (D2_REASON_SYNTHETIC,), digests)
    # A text-only "OWNER_SIGNED" string is a claim, not authenticated evidence.
    # Part C permits VERIFIED only once a trusted, external attestation boundary
    # has authenticated the Owner artifact; this validator has no such boundary.
    # Never silently promote a caller-authored string to assertion authority.
    return result(STATE_PENDING, "VALID", (D2_REASON_UNAUTHENTICATED,), digests)


def evaluate_d2_package(package_dir: str | Path) -> D2IntakeReport:
    """Classify the thirty D-2 rows and return a deterministic report."""

    package = load_d2_package(package_dir)
    results = tuple(_evaluate_field(package, spec) for spec in D2_FIELDS)
    counts = {state: 0 for state in STATES}
    for row in results:
        if row.state not in counts:
            raise D2IntakeError("D2_VALIDATOR_INTERNAL", f"unknown state {row.state}")
        counts[row.state] += 1
    if sum(counts.values()) != 30:
        raise D2IntakeError("D2_VALIDATOR_INTERNAL", "row count is not thirty")
    complete = counts[STATE_VERIFIED] == 30
    return D2IntakeReport(
        package_id=package.package_id,
        package_digest=package.package_digest,
        attestation_state=ATTESTATION_SYNTHETIC if package.fixture else ATTESTATION_DECLARED,
        authenticity=AUTHENTICITY_DECLARED,
        owner_approval_claimed=False,
        execution_authorized=False,
        counts=counts,
        complete=complete,
        exit_code=0 if complete else 1,
        results=results,
    )


def render_report_json(report: D2IntakeReport) -> str:
    """Deterministic machine-readable report (canonical JSON, trailing LF)."""

    return canonical_text(report.as_dict())


def render_report_markdown(report: D2IntakeReport) -> str:
    """Human-readable readiness report; carries the same determinism basis."""

    lines = [
        "# Gate-0 D-2 Owner-Input Readiness",
        "",
        f"- Package: `{report.package_id}`",
        f"- Package digest: `{report.package_digest}`",
        f"- Input attestation state: `{report.attestation_state}`",
        f"- Authenticity: `{report.authenticity}`",
        f"- Owner approval claimed: `{'true' if report.owner_approval_claimed else 'false'}`",
        f"- Execution authorized: `{'true' if report.execution_authorized else 'false'}`",
        f"- D-3 status: `NOT_AUTHORIZED`",
        f"- Complete: `{'true' if report.complete else 'false'}`",
        f"- Rows: VERIFIED {report.counts[STATE_VERIFIED]} / "
        f"PENDING {report.counts[STATE_PENDING]} / "
        f"BLOCKED {report.counts[STATE_BLOCKED]} / "
        f"NOT_OBSERVED {report.counts[STATE_NOT_OBSERVED]}",
        "",
        "| ID | Domain | State | Check | Declared | Ruling | Title |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.results:
        ruling = row.unresolved_ruling or "-"
        lines.append(
            f"| {row.field_id} | {row.domain} | {row.state} | {row.validator_check} | "
            f"{row.declared_status} | {ruling} | {row.title} |"
        )
    lines.extend([
        "",
        "## Reading this report",
        "",
        "- States are `VERIFIED` / `PENDING` / `BLOCKED` / `NOT_OBSERVED`; no row is "
        "`AUTHORIZED`, `GRANTED`, `FROZEN` or `PASS`.",
        "- `NOT_OBSERVED` is an availability condition, never evidence and never a pass.",
        "- `BLOCKED` outranks `PENDING`: a declaration cannot override a missing "
        "contract-owner ruling or an unrepresentable schema field.",
        "- A `SYNTHETIC_FIXTURE` package can show a `PASS` deterministic check but can "
        "never produce `VERIFIED` real-Owner evidence.",
        "- Gate-0 D-3 remains `NOT_AUTHORIZED`; this report grants no file, media, "
        "model, network or execution permission.",
        "",
    ])
    return "\n".join(lines)


def canonical_json_text(value: Any) -> str:
    """Canonical JSON text helper shared with the CLI error path."""

    return canonical_text(value)
