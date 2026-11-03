"""Immutable Gate-0 failure, invalidation, retention, and rollback records."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from gate0.identity import digest_bytes, opaque_id, validate_digest

RETENTION_CLASSES = ("SOURCE_REFERENCE", "DERIVED_REPLAYABLE", "DERIVED_RESTRICTED", "AUDIT_MINIMUM", "TOMBSTONE")
ROLLBACK_STATES = ("AVAILABLE", "QUARANTINED", "CLEANUP_PENDING", "CLEANED", "TOMBSTONED")


def membership_digest(refs: tuple[str, ...] | list[str]) -> str:
    values = tuple(sorted(set(refs)))
    if len(values) != len(refs):
        raise ValueError("affected membership must be unique")
    return digest_bytes(("\n".join(values)).encode("utf-8"))


def retention_transition(before: str, after: str) -> str:
    legal = {"AVAILABLE": {"QUARANTINED"}, "QUARANTINED": {"CLEANUP_PENDING"}, "CLEANUP_PENDING": {"CLEANED", "TOMBSTONED"}}
    if after not in ROLLBACK_STATES or after not in legal.get(before, set()):
        raise ValueError(f"illegal retention transition {before}->{after}")
    return after


def rollback_status(status: str, *, cleanup_succeeded: bool, rebuildable: bool = True) -> str:
    if status == "AVAILABLE":
        return retention_transition(status, "QUARANTINED")
    if status == "QUARANTINED":
        return retention_transition(status, "CLEANUP_PENDING")
    if status == "CLEANUP_PENDING":
        if not cleanup_succeeded:
            return status
        return retention_transition(status, "CLEANED" if rebuildable else "TOMBSTONED")
    if status in {"CLEANED", "TOMBSTONED"}:
        return status
    raise ValueError("unknown rollback state")


@dataclass(frozen=True)
class AttemptRecord:
    attempt_id: str
    run_id: str
    stage: str
    idempotency_key: str
    input_digest: str
    config_digest: str
    tool_environment_digest: str
    target_set_digest: str
    error_class: str | None = None
    retry_of: str | None = None
    sealed: bool = True
    stage_status: str = "FAILED"
    exit_code: int = 40
    policy_decision_id: str | None = None
    started_at: str = "1970-01-01T00:00:00Z"
    ended_at: str | None = None
    output_artifact_refs: tuple[Any, ...] = ()
    failure_refs: tuple[str, ...] = ()

    @classmethod
    def create(cls, run_id: str, stage: str, input_digest: str, config_digest: str, tool_environment_digest: str, target_set_digest: str, *, retry_of: str | None = None, error_class: str | None = None, attempt_id: str | None = None, stage_status: str = "FAILED", exit_code: int = 40) -> "AttemptRecord":
        parts = (run_id, stage, input_digest, config_digest, tool_environment_digest)
        joined = b"".join(len(part.encode("utf-8")).to_bytes(8, "big") + part.encode("utf-8") for part in parts)
        key = digest_bytes(joined)
        seed = {"key": key, "retry_of": retry_of or "none"}
        return cls(attempt_id or opaque_id("attempt", seed), run_id, stage, key, input_digest, config_digest, tool_environment_digest, target_set_digest, error_class, retry_of, True, stage_status, exit_code)

    def to_dict(self) -> dict[str, Any]:
        return {"attempt_id": self.attempt_id, "run_id": self.run_id, "stage": self.stage, "idempotency_key": self.idempotency_key, "input_digest": self.input_digest, "config_digest": self.config_digest, "policy_decision_id": self.policy_decision_id, "started_at": self.started_at, "ended_at": self.ended_at, "exit_code": self.exit_code, "stage_status": self.stage_status, "output_artifact_refs": list(self.output_artifact_refs), "retry_of": self.retry_of, "failure_refs": list(self.failure_refs), "tool_environment_digest": self.tool_environment_digest}


@dataclass(frozen=True)
class FailureEvent:
    event_id: str
    event_type: str
    attempt_id: str
    affected_refs: tuple[str, ...]
    reason: str
    before_status: str | None
    after_status: str | None
    authority: str | None
    occurred_at: str
    idempotency_key: str | None = None
    membership_digest: str | None = None
    payload_ref: str | None = None
    trigger: str | None = None
    quarantine_destination: str | None = None
    actor: str | None = None
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"event_id": self.event_id, "event_type": self.event_type, "attempt_id": self.attempt_id, "affected_refs": list(self.affected_refs), "reason": self.reason, "before_status": self.before_status, "after_status": self.after_status, "authority": self.authority, "occurred_at": self.occurred_at, "idempotency_key": self.idempotency_key, "membership_digest": self.membership_digest, "payload_ref": self.payload_ref, "trigger": self.trigger, "quarantine_destination": self.quarantine_destination, "actor": self.actor, "errors": list(self.errors)}


def invalidation_event(attempt_id: str, affected_refs: list[str] | tuple[str, ...], *, reason: str, authority: str, now: str, trigger: str = "invalidation", quarantine_destination: str = "quarantine", errors: tuple[str, ...] = ()) -> FailureEvent:
    refs = tuple(sorted(affected_refs))
    digest = membership_digest(refs)
    key = digest_bytes((attempt_id + "|INVALIDATION|" + digest).encode())
    return FailureEvent(opaque_id("event", {"attempt": attempt_id, "type": "INVALIDATION", "refs": refs}), "INVALIDATION", attempt_id, refs, reason, "AVAILABLE", "QUARANTINED", authority, now, idempotency_key=key, membership_digest=digest, trigger=trigger, quarantine_destination=quarantine_destination, actor=authority, errors=tuple(errors))

def rollback_event(attempt_id: str, affected_refs: list[str] | tuple[str, ...], *, before_status: str, after_status: str, trigger: str, actor: str, quarantine_destination: str, now: str, errors: tuple[str, ...] = ()) -> FailureEvent:
    if (before_status, after_status) not in {("AVAILABLE", "QUARANTINED"), ("QUARANTINED", "CLEANUP_PENDING"), ("CLEANUP_PENDING", "CLEANED"), ("CLEANUP_PENDING", "TOMBSTONED")}:
        raise ValueError("illegal rollback transition")
    refs = tuple(sorted(affected_refs)); digest = membership_digest(refs)
    key = digest_bytes((attempt_id + "|ROLLBACK|" + digest + "|" + before_status + "|" + after_status).encode())
    return FailureEvent(opaque_id("event", {"attempt": attempt_id, "type": "ROLLBACK", "refs": refs, "before": before_status, "after": after_status}), "ROLLBACK", attempt_id, refs, "ROLLBACK", before_status, after_status, actor, now, idempotency_key=key, membership_digest=digest, trigger=trigger, quarantine_destination=quarantine_destination, actor=actor, errors=tuple(errors))


def conserve_targets(planned: int, *, succeeded: int, failed: int, omitted: int, quarantined: int) -> bool:
    values = (planned, succeeded, failed, omitted, quarantined)
    if any(not isinstance(value, int) or value < 0 for value in values):
        raise ValueError("target counts must be non-negative integers")
    if planned != succeeded + failed + omitted + quarantined:
        raise ValueError("target conservation violated")
    return True


def preserve_source(source_before: bytes | str, source_after: bytes | str) -> bool:
    if source_before != source_after:
        raise ValueError("source media was modified")
    return True


_PROVENANCE_FIELDS = {"provenance_ref", "artifact_digest", "revision_id", "parent_refs"}


def sanitize_provenance(fields: Mapping[str, Any]) -> dict[str, Any]:
    """Keep only explicit opaque provenance references and digest metadata."""
    if not isinstance(fields, Mapping) or not set(fields).issubset(_PROVENANCE_FIELDS):
        raise ValueError("undeclared tombstone provenance field")
    result = dict(fields)
    for key, value in result.items():
        if key == "artifact_digest":
            validate_digest(value)
        elif key == "parent_refs":
            if not isinstance(value, (tuple, list)) or any(not isinstance(item, str) or "/" in item or "\\" in item for item in value):
                raise ValueError("invalid provenance parent references")
        elif not isinstance(value, str) or not value or any(token in value.casefold() for token in ("query", "password", "secret", "credential", "token")) or "/" in value or "\\" in value:
            raise ValueError("unsafe tombstone provenance value")
    return result


@dataclass(frozen=True)
class Tombstone:
    tombstone_id: str
    artifact_id: str
    revision_id: str
    parent_refs: tuple[str, ...]
    permitted_digest: str
    byte_count: int
    reason: str
    policy_ref: str
    run_id: str
    attempt_id: str
    deleted_at: str
    rebuildability: str
    searchable: bool = False
    schema_version: str = "gate0.v1"
    provenance_ref: str | None = None
    permitted_fields: tuple[str, ...] = ()

    @classmethod
    def create(cls, artifact_id: str, revision_id: str, parent_refs: tuple[str, ...], *, digest: str, byte_count: int, reason: str, policy_ref: str, run_id: str, attempt_id: str, deleted_at: str, rebuildability: str, raw_media: bytes | None = None, locator: str | None = None, provenance_ref: str | None = None, provenance_fields: Mapping[str, Any] | None = None, permitted_fields: tuple[str, ...] = (), schema_version: str = "gate0.v1") -> "Tombstone":
        validate_digest(digest)
        if raw_media is not None:
            raise ValueError("tombstone cannot contain raw media")
        if locator is not None and "locator" not in permitted_fields:
            raise ValueError("locator is not permitted by retention policy")
        if provenance_ref is not None and ("/" in provenance_ref or "\\" in provenance_ref or " " in provenance_ref):
            raise ValueError("provenance reference must not contain a path")
        if provenance_fields is not None:
            sanitize_provenance(provenance_fields)
        if byte_count < 0 or rebuildability not in {"rebuildable", "not_rebuildable"}:
            raise ValueError("invalid tombstone")
        seed = {"artifact_id": artifact_id, "revision_id": revision_id, "digest": digest, "deleted_at": deleted_at}
        return cls(opaque_id("tombstone", seed), artifact_id, revision_id, tuple(sorted(parent_refs)), digest, byte_count, reason, policy_ref, run_id, attempt_id, deleted_at, rebuildability, False, schema_version, provenance_ref, tuple(sorted(permitted_fields)))

    def to_dict(self) -> dict[str, Any]:
        return {"tombstone_id": self.tombstone_id, "artifact_id": self.artifact_id, "revision_id": self.revision_id, "parent_refs": list(self.parent_refs), "permitted_digest": self.permitted_digest, "byte_count": self.byte_count, "reason": self.reason, "policy_ref": self.policy_ref, "run_id": self.run_id, "attempt_id": self.attempt_id, "deleted_at": self.deleted_at, "rebuildability": self.rebuildability, "searchable": False, "schema_version": self.schema_version, "provenance_ref": self.provenance_ref, "permitted_fields": list(self.permitted_fields)}
