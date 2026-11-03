"""Read-only, deterministic synthetic/local source inventory."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import json

from gate0.canonical_json import canonical_bytes
from gate0.contracts.types import record_digest
from gate0.identity import digest_bytes, digest_json, opaque_id
from gate0.policy import PolicyDecision, PolicyDenied, PolicyUseContext, require_allow


@dataclass(frozen=True)
class SourceOccurrence:
    occurrence_id: str
    revision_id: str
    content_id: str
    locator: Path | str
    relation_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProbeEvidence:
    ffprobe_json: Mapping[str, Any]
    time_base: tuple[int, int] = (1, 1)
    probe_ref: str | None = None
    failure: str | None = None


@dataclass(frozen=True)
class RevisionRef:
    """Resolved immutable source identity consumed by downstream stages."""
    revision_id: str
    content_id: str
    locator: str
    selected_stream_index: int
    selection_source: str


@dataclass(frozen=True)
class InventoryPayload:
    source_records: tuple[dict[str, Any], ...]
    discovery_records: tuple[dict[str, Any], ...]
    policy_decision: PolicyDecision
    inventory_digest: str
    selected_streams: tuple[tuple[str, int, str], ...] = ()
    revision_refs: tuple[RevisionRef, ...] = ()


def _record(record_type: str, payload: dict[str, Any], seed: Any) -> dict[str, Any]:
    record_id = opaque_id({"occurrence_revision": "occurrence", "discovery_authorization": "authorization", "policy_decision": "policy"}.get(record_type, "record"), seed)
    record = {"record_id": record_id, "record_type": record_type, "record_schema_version": "gate0.v1", "record_digest": "", "payload": payload}
    record["record_digest"] = record_digest(record)
    return record


def _stream_refs(probe: ProbeEvidence) -> tuple[dict[str, Any], ...]:
    streams = probe.ffprobe_json.get("streams", [])
    return tuple({"stream_index": int(s["index"]), "stream_type": str(s["codec_type"])} for s in streams)


def _selected_stream(probe: ProbeEvidence, configured: int | None) -> tuple[int, str]:
    eligible = [int(s["index"]) for s in probe.ffprobe_json.get("streams", []) if s.get("codec_type") == "video"]
    if configured is not None:
        if configured not in eligible:
            raise ValueError("SELECTED_STREAM_NOT_ELIGIBLE")
        return configured, "config"
    if len(eligible) != 1:
        raise ValueError("AMBIGUOUS_STREAM")
    return eligible[0], "unique_probe"


def build_inventory(occurrences: tuple[SourceOccurrence, ...] | list[SourceOccurrence], probe_by_revision: Mapping[str, ProbeEvidence], authorization: PolicyDecision, selected_stream_index: int | None = None, *, now: str = "1970-01-01T00:00:00Z", expected_egress_manifest_digest: str | None = None) -> InventoryPayload:
    occurrences = tuple(occurrences)
    revisions = tuple(o.revision_id for o in occurrences)
    if not occurrences or len(set(revisions)) != len(revisions):
        raise ValueError("inventory requires unique non-empty revisions")
    if authorization.purpose != "DISCOVER":
        raise PolicyDenied("discovery policy purpose mismatch")
    if authorization.allowed_artifact_types != ("source_manifest", "discovery_authorization"):
        raise PolicyDenied("allowed artifact types mismatch")
    require_allow(PolicyUseContext(revisions[0], "DISCOVER", "DISCOVER", "source_manifest", authorization.provider_model_boundary, authorization.retention_class, now, expected_egress_manifest_digest or authorization.egress_manifest_digest, authorization, None))
    if tuple(authorization.revision_scope) != revisions:
        raise PolicyDenied("discovery policy scope mismatch")
    source_records: list[dict[str, Any]] = []
    auth_rows: list[dict[str, Any]] = []
    selected_streams: list[tuple[str, int, str]] = []
    revision_refs: list[RevisionRef] = []
    for occurrence in occurrences:
        probe = probe_by_revision.get(occurrence.revision_id)
        if probe is None:
            raise ValueError("PROBE_MISSING")
        if probe.failure:
            raise ValueError("PROBE_FAILED")
        selected, selection_source = _selected_stream(probe, selected_stream_index)
        path = Path(occurrence.locator)
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise ValueError("SOURCE_UNREADABLE") from exc
        selected_streams.append((occurrence.revision_id, selected, selection_source))
        revision_refs.append(RevisionRef(occurrence.revision_id, occurrence.content_id, str(path), selected, selection_source))
        payload = {"occurrence_id": occurrence.occurrence_id, "revision_id": occurrence.revision_id, "content_id": occurrence.content_id, "locator": str(path), "byte_count": len(content), "digest_algorithm": "sha256", "content_digest": digest_bytes(content), "stream_refs": list(_stream_refs(probe)), "probe_ref": probe.probe_ref or digest_json(probe.ffprobe_json), "discovery_authorization_id": opaque_id("authorization", occurrence.revision_id), "source_status": "INCLUDED", "relation_ids": list(occurrence.relation_ids), "custody": {"state": "PRESERVED", "authority": "gate0", "recorded_at": now}}
        source_records.append(_record("occurrence_revision", payload, occurrence.revision_id))
        auth_payload = {"discovery_authorization_id": payload["discovery_authorization_id"], "occurrence_scope": [occurrence.occurrence_id], "locator_scope": [str(path)], "authority": "gate0", "purpose": "DISCOVER", "operations": ["DISCOVER", "HASH", "PROBE"], "expires_at": authorization.expires_at, "decision": authorization.decision, "decision_digest": digest_json(authorization.to_dict()), "policy_decision_id": authorization.policy_decision_id, "custody": payload["custody"]}
        auth_rows.append(_record("discovery_authorization", auth_payload, occurrence.revision_id))
    # JSONL publication requires record_id ordering; multi-revision inventories
    # otherwise publish authorizations in occurrence order and fail canonicality.
    discovery_records = tuple(sorted(auth_rows, key=lambda row: row["record_id"]))
    inventory_digest = digest_bytes(canonical_bytes({"source_records": source_records, "discovery_records": auth_rows, "policy_decision_id": authorization.policy_decision_id}))
    return InventoryPayload(tuple(source_records), discovery_records, authorization, inventory_digest, tuple(selected_streams), tuple(revision_refs))
