"""Fail-closed authorization boundary for a developer-local semantic pilot.

The authorization file is an owner-created control artifact.  Product code
only reads and validates it; it never manufactures one.  This module is kept
independent of the model loader so that an invalid authorization can be
rejected before decode, model construction, or index mutation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


class PilotAuthorizationError(ValueError):
    """Raised when a pilot authorization cannot be proven valid."""


_FIELDS = frozenset(
    {
        "source_path",
        "source_sha256",
        "purpose",
        "model_root",
        "model_revision",
        "weights_sha256",
        "runtime_root",
        "index_root",
        "output_root",
        "allowed_stages",
    }
)
_PREPARE_FIELDS = frozenset({"authorization_id", "source_revision_id", "query_digest", "semantic_space_id", "model_identity",
                             "index_digest", "local_only", "expires_at", "revoked", "selected_stream_index",
                             "record_digest", "policy_digest", "scope_digest"})
_SHA256 = 64
_REQUIRED_STAGES = frozenset({"decode", "embed", "index"})
_CORPUS_REF_FIELD = "corpus_separation_ref"
_AUTHORIZATION_V2 = "vip_fvs.pilot_authorization.v2"
_RFC3339_DATETIME = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$")


def _fail(reason: str) -> PilotAuthorizationError:
    return PilotAuthorizationError(reason)


def _absolute_path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise _fail(f"PILOT_AUTHORIZATION_{field.upper()}_INVALID")
    path = Path(value)
    if not path.is_absolute():
        raise _fail(f"PILOT_AUTHORIZATION_{field.upper()}_MUST_BE_ABSOLUTE")
    return path


def _digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != _SHA256:
        raise _fail(f"PILOT_AUTHORIZATION_{field.upper()}_INVALID")
    if any(char not in "0123456789abcdef" for char in value):
        raise _fail(f"PILOT_AUTHORIZATION_{field.upper()}_INVALID")
    return value


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _fail("PILOT_AUTHORIZATION_SCHEMA_INVALID")
        result[key] = value
    return result


@dataclass(frozen=True)
class PilotAuthorization:
    """Exact single-file authorization for one developer-local source file."""

    source_path: Path
    source_sha256: str
    purpose: str
    model_root: Path
    model_revision: str
    weights_sha256: str
    runtime_root: Path
    index_root: Path
    output_root: Path
    allowed_stages: tuple[str, ...]
    authorization_id: str | None = None
    source_revision_id: str | None = None
    model_identity: str | None = None
    query_digest: str | None = None
    semantic_space_id: str | None = None
    index_digest: str | None = None
    local_only: bool | None = None
    expires_at: str | None = None
    revoked: bool = False
    selected_stream_index: int | None = None
    record_digest: str | None = None
    policy_digest: str | None = None
    scope_digest: str | None = None
    corpus_separation_ref: Mapping[str, Any] | None = None
    schema_version: str | None = None

    def __post_init__(self) -> None:
        if self.schema_version is not None and self.schema_version != _AUTHORIZATION_V2:
            raise _fail("PILOT_AUTHORIZATION_SCHEMA_INVALID")
        if type(self.revoked) is not bool:
            raise _fail("PILOT_AUTHORIZATION_REVOCATION_FLAG_INVALID")
        for name in ("source_path", "model_root", "runtime_root", "index_root", "output_root"):
            value = getattr(self, name)
            if not isinstance(value, Path) or not value.is_absolute():
                raise _fail(f"PILOT_AUTHORIZATION_{name.upper()}_MUST_BE_ABSOLUTE")
        if not self.source_path.is_file():
            raise _fail("PILOT_AUTHORIZATION_SOURCE_NOT_REGULAR_FILE")
        if not isinstance(self.purpose, str) or not self.purpose.strip():
            raise _fail("PILOT_AUTHORIZATION_PURPOSE_REQUIRED")
        if not isinstance(self.model_revision, str) or not self.model_revision.strip():
            raise _fail("PILOT_AUTHORIZATION_MODEL_REVISION_REQUIRED")
        _digest(self.source_sha256, "source_sha256")
        _digest(self.weights_sha256, "weights_sha256")
        if not self.allowed_stages or any(not isinstance(stage, str) or not stage for stage in self.allowed_stages):
            raise _fail("PILOT_AUTHORIZATION_ALLOWED_STAGES_REQUIRED")
        if len(set(self.allowed_stages)) != len(self.allowed_stages):
            raise _fail("PILOT_AUTHORIZATION_ALLOWED_STAGES_DUPLICATED")
        if not _REQUIRED_STAGES.issubset(self.allowed_stages):
            raise _fail("PILOT_AUTHORIZATION_REQUIRED_STAGE_ABSENT")
        if self.query_digest is not None: _digest(self.query_digest, "query_digest")
        if self.index_digest is not None: _digest(self.index_digest, "index_digest")
        if self.policy_digest is not None: _digest(self.policy_digest, "policy_digest")
        if self.scope_digest is not None: _digest(self.scope_digest, "scope_digest")
        if self.corpus_separation_ref is not None:
            if self.schema_version != _AUTHORIZATION_V2:
                raise _fail("PILOT_AUTHORIZATION_SCHEMA_INVALID")
            from .corpus_separation import parse_reference
            object.__setattr__(self, "corpus_separation_ref", parse_reference(self.corpus_separation_ref))
        for name in ("authorization_id", "source_revision_id", "model_identity", "semantic_space_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise _fail(f"PILOT_AUTHORIZATION_{name.upper()}_INVALID")
        if self.expires_at is not None:
            if not isinstance(self.expires_at, str) or not _RFC3339_DATETIME.fullmatch(self.expires_at):
                raise _fail("PILOT_AUTHORIZATION_EXPIRY_INVALID")
            try:
                expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise _fail("PILOT_AUTHORIZATION_EXPIRY_INVALID") from exc
            if expiry.tzinfo is None or expiry.utcoffset() is None:
                raise _fail("PILOT_AUTHORIZATION_EXPIRY_INVALID")
        if self.local_only is not None and self.local_only is not True:
            raise _fail("PILOT_AUTHORIZATION_LOCAL_ONLY_REQUIRED")
        if self.selected_stream_index is not None and (type(self.selected_stream_index) is not int or self.selected_stream_index < 0):
            raise _fail("PILOT_AUTHORIZATION_STREAM_INVALID")


def load_pilot_authorization(path: Path) -> PilotAuthorization:
    """Load exactly one JSON object from a regular local authorization file."""

    candidate = Path(path)
    if not candidate.is_file():
        raise _fail("REAL_MEDIA_AUTHORIZATION_REQUIRED")
    try:
        raw = json.loads(candidate.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_object)
    except PilotAuthorizationError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail("PILOT_AUTHORIZATION_UNREADABLE") from exc
    base_fields = _FIELDS
    prepare_fields = _FIELDS | _PREPARE_FIELDS
    prepare_with_ref = prepare_fields | {_CORPUS_REF_FIELD, "schema_version"}
    extended = isinstance(raw, Mapping) and set(raw) in (prepare_fields, prepare_with_ref)
    if not isinstance(raw, Mapping) or set(raw) not in (base_fields, prepare_fields, prepare_with_ref):
        raise _fail("PILOT_AUTHORIZATION_SCHEMA_INVALID")
    if extended:
        if type(raw.get("revoked")) is not bool:
            raise _fail("PILOT_AUTHORIZATION_REVOCATION_FLAG_INVALID")
        supplied = raw.get("record_digest")
        body = dict(raw); body.pop("record_digest", None)
        expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        if supplied != expected:
            raise _fail("PILOT_AUTHORIZATION_RECORD_DIGEST_MISMATCH")
        if _CORPUS_REF_FIELD in raw and raw.get("schema_version") != _AUTHORIZATION_V2:
            raise _fail("PILOT_AUTHORIZATION_SCHEMA_INVALID")
    stages = raw["allowed_stages"]
    if not isinstance(stages, list) or any(not isinstance(item, str) for item in stages):
        raise _fail("PILOT_AUTHORIZATION_ALLOWED_STAGES_INVALID")
    return PilotAuthorization(
        source_path=_absolute_path(raw["source_path"], "source_path"),
        source_sha256=_digest(raw["source_sha256"], "source_sha256"),
        purpose=raw["purpose"] if isinstance(raw["purpose"], str) else "",
        model_root=_absolute_path(raw["model_root"], "model_root"),
        model_revision=raw["model_revision"] if isinstance(raw["model_revision"], str) else "",
        weights_sha256=_digest(raw["weights_sha256"], "weights_sha256"),
        runtime_root=_absolute_path(raw["runtime_root"], "runtime_root"),
        index_root=_absolute_path(raw["index_root"], "index_root"),
        output_root=_absolute_path(raw["output_root"], "output_root"),
        allowed_stages=tuple(stages),
        authorization_id=raw.get("authorization_id"), source_revision_id=raw.get("source_revision_id"),
        model_identity=raw.get("model_identity"),
        query_digest=raw.get("query_digest"), semantic_space_id=raw.get("semantic_space_id"),
        index_digest=raw.get("index_digest"), local_only=raw.get("local_only"),
        expires_at=raw.get("expires_at"), revoked=raw.get("revoked", False),
        selected_stream_index=raw.get("selected_stream_index"), record_digest=raw.get("record_digest"),
        policy_digest=raw.get("policy_digest"), scope_digest=raw.get("scope_digest"),
        corpus_separation_ref=raw.get(_CORPUS_REF_FIELD),
        schema_version=raw.get("schema_version"),
    )


def _contract_value(contract: Any, *names: str) -> Any:
    for name in names:
        if hasattr(contract, name):
            return getattr(contract, name)
    raise _fail("PILOT_AUTHORIZATION_MODEL_CONTRACT_INVALID")


def _same_path(left: Path, right: Path) -> bool:
    return left.resolve(strict=False) == right.resolve(strict=False)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise _fail("PILOT_AUTHORIZATION_SOURCE_UNREADABLE") from exc
    return digest.hexdigest()


def require_pilot_authorization(
    authorization: PilotAuthorization | None,
    *,
    source_path: Path,
    model_contract: Any,
    index_root: Path,
    output_root: Path,
    verify_source_digest: bool = True,
) -> None:
    """Validate authorization and current source identity immediately pre-use."""

    if authorization is None:
        raise _fail("REAL_MEDIA_AUTHORIZATION_REQUIRED")
    if authorization.revoked:
        raise _fail("PILOT_AUTHORIZATION_REVOKED")
    if authorization.local_only is False:
        raise _fail("PILOT_AUTHORIZATION_LOCAL_ONLY_REQUIRED")
    if authorization.expires_at is not None:
        try:
            expiry = datetime.fromisoformat(str(authorization.expires_at).replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise _fail("PILOT_AUTHORIZATION_EXPIRY_INVALID") from exc
        if expiry.tzinfo is None or expiry.utcoffset() is None:
            raise _fail("PILOT_AUTHORIZATION_EXPIRY_INVALID")
        if expiry <= datetime.now(timezone.utc):
            raise _fail("PILOT_AUTHORIZATION_EXPIRED")
    source = Path(source_path)
    if not source.is_file() or not _same_path(authorization.source_path, source):
        raise _fail("PILOT_AUTHORIZATION_SOURCE_PATH_MISMATCH")
    # All non-content scope predicates must be checked before the caller opens
    # source bytes. The default retains the historical one-call API, but hashes
    # only after every identity predicate below has passed.
    if not _same_path(authorization.index_root, Path(index_root)):
        raise _fail("PILOT_AUTHORIZATION_INDEX_ROOT_MISMATCH")
    if not _same_path(authorization.output_root, Path(output_root)):
        raise _fail("PILOT_AUTHORIZATION_OUTPUT_ROOT_MISMATCH")
    try:
        contract_root = Path(_contract_value(model_contract, "model_root"))
        revision = _contract_value(model_contract, "model_revision", "revision")
        weights = _contract_value(model_contract, "weights_sha256")
    except (TypeError, ValueError):
        raise
    if not _same_path(authorization.model_root, contract_root):
        raise _fail("PILOT_AUTHORIZATION_MODEL_ROOT_MISMATCH")
    if revision != authorization.model_revision:
        raise _fail("PILOT_AUTHORIZATION_MODEL_REVISION_MISMATCH")
    if weights != authorization.weights_sha256:
        raise _fail("PILOT_AUTHORIZATION_WEIGHTS_DIGEST_MISMATCH")
    if verify_source_digest and _sha256(source) != authorization.source_sha256:
        raise _fail("PILOT_AUTHORIZATION_SOURCE_DIGEST_MISMATCH")


def require_prepare_authorization(
    authorization: PilotAuthorization | None,
    *,
    source_path: Path,
    source_revision_id: str,
    query: str,
    model_root: Path,
    model_identity: str,
    model_revision: str,
    weights_sha256: str,
    semantic_space_id: str | None = None,
    index_root: Path,
    output_root: Path,
    selected_stream_index: int | None = None,
    now: datetime | None = None,
    verify_source_digest: bool = True,
) -> None:
    """Validate the extended REAL prepare envelope before model construction."""
    if authorization is None or authorization.record_digest is None:
        raise _fail("PREPARE_AUTHORIZATION_RECORD_DIGEST_REQUIRED")
    required = ("authorization_id", "source_revision_id", "query_digest", "semantic_space_id",
                "model_identity", "index_digest", "local_only", "expires_at", "policy_digest", "scope_digest")
    if any(getattr(authorization, field, None) is None for field in required):
        raise _fail("PREPARE_AUTHORIZATION_EXACT_SCOPE_REQUIRED")
    if not authorization.local_only or authorization.revoked:
        raise _fail("PREPARE_AUTHORIZATION_REVOKED" if authorization.revoked else "PREPARE_AUTHORIZATION_LOCAL_ONLY_REQUIRED")
    source = Path(source_path)
    if not _same_path(authorization.source_path, source):
        raise _fail("PREPARE_AUTHORIZATION_SOURCE_PATH_MISMATCH")
    # Source-content identity is deliberately checked last. Callers that own a
    # verified snapshot pass verify_source_digest=False here, then capture and
    # compare source bytes only after this complete scope validation succeeds.
    if source_revision_id != authorization.source_revision_id:
        raise _fail("PREPARE_AUTHORIZATION_SOURCE_REVISION_ID_MISMATCH")
    query_digest = hashlib.sha256(json.dumps(query, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if query_digest != authorization.query_digest:
        raise _fail("PREPARE_AUTHORIZATION_QUERY_DIGEST_MISMATCH")
    if not _same_path(authorization.model_root, Path(model_root)):
        raise _fail("PREPARE_AUTHORIZATION_MODEL_ROOT_MISMATCH")
    if model_identity != authorization.model_identity:
        raise _fail("PREPARE_AUTHORIZATION_MODEL_IDENTITY_MISMATCH")
    if model_revision != authorization.model_revision:
        raise _fail("PREPARE_AUTHORIZATION_MODEL_REVISION_MISMATCH")
    if weights_sha256 != authorization.weights_sha256:
        raise _fail("PREPARE_AUTHORIZATION_WEIGHTS_DIGEST_MISMATCH")
    if semantic_space_id is not None and authorization.semantic_space_id != semantic_space_id:
        raise _fail("PREPARE_AUTHORIZATION_SEMANTIC_SPACE_ID_MISMATCH")
    if not _same_path(authorization.index_root, Path(index_root)):
        raise _fail("PREPARE_AUTHORIZATION_INDEX_ROOT_MISMATCH")
    if authorization.index_digest != hashlib.sha256(json.dumps(str(Path(index_root).resolve()), sort_keys=True, separators=(",", ":")).encode()).hexdigest():
        raise _fail("PREPARE_AUTHORIZATION_INDEX_DIGEST_MISMATCH")
    if not _same_path(authorization.output_root, Path(output_root)):
        raise _fail("PREPARE_AUTHORIZATION_OUTPUT_ROOT_MISMATCH")
    if selected_stream_index is not None and authorization.selected_stream_index != selected_stream_index:
        raise _fail("PREPARE_AUTHORIZATION_STREAM_SCOPE_MISMATCH")
    try:
        expiry = datetime.fromisoformat(str(authorization.expires_at).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise _fail("PREPARE_AUTHORIZATION_EXPIRY_INVALID") from exc
    if expiry.tzinfo is None:
        raise _fail("PREPARE_AUTHORIZATION_EXPIRY_INVALID")
    if expiry <= (now or datetime.now(timezone.utc)):
        raise _fail("PREPARE_AUTHORIZATION_EXPIRED")
    stages = set(authorization.allowed_stages)
    required_stages = {"decode", "embed", "index", "probe", "retrieve", "refine"}
    if not required_stages.issubset(stages):
        raise _fail("PREPARE_AUTHORIZATION_OPERATION_SCOPE_MISMATCH")
    if verify_source_digest and _sha256(source) != authorization.source_sha256:
        raise _fail("PREPARE_AUTHORIZATION_SOURCE_DIGEST_MISMATCH")


def require_snapshot_lifecycle(authorization: PilotAuthorization | None, *, required_stages: set[str]) -> None:
    """Require explicit active local lifecycle/scope fields before snapshot capture."""
    if not isinstance(authorization, PilotAuthorization):
        raise _fail("PILOT_AUTHORIZATION_REQUIRED")
    if not authorization.authorization_id or not authorization.source_revision_id:
        raise _fail("PILOT_AUTHORIZATION_SNAPSHOT_BINDING_REQUIRED")
    if authorization.local_only is not True:
        raise _fail("PILOT_AUTHORIZATION_LOCAL_ONLY_REQUIRED")
    if type(authorization.revoked) is not bool or authorization.revoked:
        raise _fail("PILOT_AUTHORIZATION_REVOKED")
    if not isinstance(authorization.expires_at, str) or not authorization.expires_at:
        raise _fail("PILOT_AUTHORIZATION_EXPIRY_REQUIRED")
    try:
        expiry = datetime.fromisoformat(authorization.expires_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _fail("PILOT_AUTHORIZATION_EXPIRY_INVALID") from exc
    if expiry.tzinfo is None or expiry.utcoffset() is None:
        raise _fail("PILOT_AUTHORIZATION_EXPIRY_INVALID")
    if expiry <= datetime.now(timezone.utc):
        raise _fail("PILOT_AUTHORIZATION_EXPIRED")
    if not required_stages.issubset(set(authorization.allowed_stages)):
        raise _fail("PILOT_AUTHORIZATION_OPERATION_SCOPE_MISMATCH")


__all__ = ["PilotAuthorization", "PilotAuthorizationError", "load_pilot_authorization", "require_pilot_authorization", "require_prepare_authorization", "require_snapshot_lifecycle"]
