"""Closed T01 identity, record-envelope, and artifact-envelope types."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, ClassVar

from gate0.canonical_json import canonical_bytes, canonical_jsonl_bytes, normalize_jsonl_bytes, normalize_markdown_bytes
from gate0.identity import digest_bytes, opaque_id, validate_digest, validate_opaque_id

ARTIFACT_TYPES = (
    "source_manifest.json", "discovery_authorizations.jsonl", "policy_decisions.jsonl",
    "split_manifest.json", "queries.jsonl", "gold_events.jsonl", "window_judgments.jsonl",
    "window_sample_manifest.jsonl", "run_manifest.json", "ranked_candidates.jsonl",
    "runtime_and_failure_ledger.json", "metrics.json", "gate_decision.md",
)
SCHEMA_VERSIONS = {name: "gate0.v1" for name in ARTIFACT_TYPES}
RECORD_TYPES = {name: name.removesuffix(".json").removesuffix(".jsonl") for name in ARTIFACT_TYPES if name.endswith("jsonl")}
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$", re.ASCII)
RETENTION = {"SOURCE_REFERENCE", "DERIVED_REPLAYABLE", "DERIVED_RESTRICTED", "AUDIT_MINIMUM", "TOMBSTONE"}
AVAILABILITY = {"AVAILABLE", "QUARANTINED", "CLEANUP_PENDING", "CLEANED", "TOMBSTONED"}


def validate_timestamp(value: str) -> bool:
    if not isinstance(value, str) or _TIMESTAMP.fullmatch(value) is None:
        raise ValueError("timestamp must be canonical RFC-3339 with timezone")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    return True


def payload_digest(payload: Any, artifact_type: str) -> str:
    if artifact_type.endswith(".jsonl"):
        if isinstance(payload, bytes):
            data = normalize_jsonl_bytes(payload)
        else:
            data = canonical_jsonl_bytes(payload)
    elif artifact_type == "gate_decision.md":
        data = normalize_markdown_bytes(payload if isinstance(payload, bytes) else str(payload).encode("utf-8"))
    else:
        data = canonical_bytes(payload)
    return digest_bytes(data)


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    payload_digest: str
    artifact_type: str

    def __post_init__(self) -> None:
        validate_opaque_id(self.artifact_id); validate_digest(self.payload_digest)
        if self.artifact_type not in ARTIFACT_TYPES:
            raise ValueError("unregistered artifact type")

    def to_dict(self) -> dict[str, str]:
        return {"artifact_id": self.artifact_id, "payload_digest": self.payload_digest, "artifact_type": self.artifact_type}


@dataclass(frozen=True)
class ArtifactEnvelope:
    artifact_id: str
    artifact_type: str
    schema_version: str
    digest_algorithm: str
    payload_digest: str
    producer_attempt_id: str
    input_artifact_refs: tuple[ArtifactRef, ...]
    policy_decision_id: str
    retention_class: str
    availability_status: str
    created_at: str

    FIELDS: ClassVar[tuple[str, ...]] = ("artifact_id", "artifact_type", "schema_version", "digest_algorithm", "payload_digest", "producer_attempt_id", "input_artifact_refs", "policy_decision_id", "retention_class", "availability_status", "created_at")

    def __post_init__(self) -> None:
        validate_opaque_id(self.artifact_id); validate_opaque_id(self.producer_attempt_id); validate_opaque_id(self.policy_decision_id)
        if self.artifact_type not in ARTIFACT_TYPES or self.schema_version != SCHEMA_VERSIONS[self.artifact_type]: raise ValueError("unregistered artifact schema version")
        if self.digest_algorithm != "SHA-256": raise ValueError("only SHA-256 is supported")
        validate_digest(self.payload_digest); validate_timestamp(self.created_at)
        if self.retention_class not in RETENTION or self.availability_status not in AVAILABILITY: raise ValueError("invalid envelope status")
        if not isinstance(self.input_artifact_refs, tuple) or any(not isinstance(ref, ArtifactRef) for ref in self.input_artifact_refs): raise ValueError("input refs must be typed ArtifactRef values")
        keys = [(ref.artifact_id, ref.artifact_type) for ref in self.input_artifact_refs]
        if keys != sorted(keys) or len(set(keys)) != len(keys): raise ValueError("input refs must be unique and bytewise sorted")

    @classmethod
    def create(cls, artifact_type: str, payload: Any, schema_version: str = "gate0.v1", *, producer_attempt_id: str | None = None, policy_decision_id: str | None = None, created_at: str = "1970-01-01T00:00:00Z", retention_class: str = "DERIVED_REPLAYABLE") -> "ArtifactEnvelope":
        digest = payload_digest(payload, artifact_type)
        return cls(opaque_id("artifact", {"type": artifact_type, "digest": digest}), artifact_type, schema_version, "SHA-256", digest, producer_attempt_id or opaque_id("attempt", digest), (), policy_decision_id or opaque_id("policy", digest), retention_class, "AVAILABLE", created_at)

    def to_dict(self) -> dict[str, Any]:
        return {"artifact_id": self.artifact_id, "artifact_type": self.artifact_type, "schema_version": self.schema_version, "digest_algorithm": self.digest_algorithm, "payload_digest": self.payload_digest, "producer_attempt_id": self.producer_attempt_id, "input_artifact_refs": [ref.to_dict() for ref in self.input_artifact_refs], "policy_decision_id": self.policy_decision_id, "retention_class": self.retention_class, "availability_status": self.availability_status, "created_at": self.created_at}

    def binds(self, payload: Any) -> bool:
        return payload_digest(payload, self.artifact_type) == self.payload_digest


def record_digest(record: dict[str, Any]) -> str:
    if set(record) != {"record_id", "record_type", "record_schema_version", "record_digest", "payload"}:
        raise ValueError("record envelope has exactly five fields")
    return digest_bytes(canonical_bytes({key: value for key, value in record.items() if key != "record_digest"}))
