"""Local/synthetic source identity and Gate-0 inventory boundary.

The adapter deliberately keeps the logical revision handle separate from the
observed byte digest.  It delegates inventory validation and publication to
Gate-0, so source bytes remain read-only and all policy/custody records retain
their native contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from gate0.canonical_json import canonical_bytes
from gate0.contracts.types import ArtifactEnvelope, record_digest
from gate0.identity import digest_bytes, opaque_id
from gate0.inventory import InventoryPayload, ProbeEvidence, RevisionRef, SourceOccurrence
from gate0.policy import PolicyDecision
from gate0.stages.inventory import inventory
from .real_source_probe import ProbeFailure, probe_real_source


@dataclass(frozen=True)
class SourceBinding:
    """Immutable source identity passed from Gate-0 to later FVS adapters."""

    revision_ref: RevisionRef
    source_path: Path
    source_sha256: str
    inventory: InventoryPayload
    policy_decision_ref: str
    custody_state: str
    inventory_envelope: ArtifactEnvelope | None = None

    @property
    def revision_id(self) -> str:
        return self.revision_ref.revision_id

    def to_dict(self) -> dict[str, Any]:
        """Return a provenance-safe summary without copying source bytes."""
        return {
            "revision_ref": {
                "revision_id": self.revision_ref.revision_id,
                "content_id": self.revision_ref.content_id,
                "locator": self.revision_ref.locator,
                "selected_stream_index": self.revision_ref.selected_stream_index,
                "selection_source": self.revision_ref.selection_source,
            },
            "source_path": str(self.source_path),
            "source_sha256": self.source_sha256,
            "inventory_digest": self.inventory.inventory_digest,
            "policy_decision_ref": self.policy_decision_ref,
            "custody_state": self.custody_state,
            "inventory_envelope": self.inventory_envelope.to_dict() if self.inventory_envelope else None,
        }


@dataclass(frozen=True)
class SourceManifestEntry:
    """One inventory-backed source occurrence in a persisted snapshot."""

    revision_id: str
    content_id: str
    source_path: Path
    source_sha256: str
    selected_stream_index: int
    selection_source: str
    inventory_digest: str
    policy_decision_ref: str
    custody_state: str
    inventory_artifact_id: str | None = None
    inventory_payload_digest: str | None = None

    def __post_init__(self) -> None:
        for name in ("revision_id", "content_id", "selection_source",
                     "policy_decision_ref", "custody_state"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} must be a non-empty string")
        if re.fullmatch(r"[0-9a-fA-F]{64}", self.revision_id):
            raise ValueError("revision_id must remain distinct from a content digest")
        for name in ("source_sha256", "inventory_digest"):
            value = getattr(self, name)
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                raise ValueError(f"{name} must be a lowercase SHA-256 digest")
        if not isinstance(self.source_path, Path):
            raise ValueError("source_path must be a Path")
        if isinstance(self.selected_stream_index, bool) or not isinstance(self.selected_stream_index, int) or self.selected_stream_index < 0:
            raise ValueError("selected_stream_index must be a non-negative integer")
        for name in ("inventory_artifact_id", "inventory_payload_digest"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value):
                raise ValueError(f"{name} must be a non-empty string or None")
        if (self.inventory_artifact_id is None) != (self.inventory_payload_digest is None):
            raise ValueError("inventory artifact id and payload digest must be paired")
        if self.inventory_payload_digest is not None and re.fullmatch(r"[0-9a-f]{64}", self.inventory_payload_digest) is None:
            raise ValueError("inventory_payload_digest must be a lowercase SHA-256 digest")


@dataclass(frozen=True)
class MultiSourceManifest:
    """Closed, deterministic snapshot of inventory-backed source bindings."""

    entries: tuple[SourceManifestEntry, ...]
    manifest_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.entries, tuple) or not self.entries or any(not isinstance(e, SourceManifestEntry) for e in self.entries):
            raise ValueError("entries must be a non-empty tuple of SourceManifestEntry")
        if len({entry.revision_id for entry in self.entries}) != len(self.entries):
            raise ValueError("duplicate revision_id")
        if len({str(entry.source_path) for entry in self.entries}) != len(self.entries):
            raise ValueError("duplicate locator")
        ordered = tuple(sorted(self.entries, key=lambda entry: (entry.revision_id.encode("utf-8"), str(entry.source_path).encode("utf-8"))))
        if ordered != self.entries:
            raise ValueError("manifest entries are not canonically ordered")
        if not isinstance(self.manifest_digest, str) or re.fullmatch(r"[0-9a-f]{64}", self.manifest_digest) is None:
            raise ValueError("manifest_digest must be a lowercase SHA-256 digest")

    def find_entry(self, locator: str | Path, source_sha256: str) -> SourceManifestEntry | None:
        """Find only an exact locator and byte-digest pair; do not normalize locators."""
        locator_text = str(locator)
        return next((entry for entry in self.entries
                     if str(entry.source_path) == locator_text and entry.source_sha256 == source_sha256), None)


_MULTI_SOURCE_SCHEMA = "vip_fvs.multi_source_manifest.v1"
_ENTRY_FIELDS = (
    "revision_id", "content_id", "source_path", "source_sha256",
    "selected_stream_index", "selection_source", "inventory_digest",
    "policy_decision_ref", "custody_state", "inventory_artifact_id",
    "inventory_payload_digest",
)


def _entry_dict(entry: SourceManifestEntry) -> dict[str, Any]:
    return {
        "revision_id": entry.revision_id,
        "content_id": entry.content_id,
        "source_path": str(entry.source_path),
        "source_sha256": entry.source_sha256,
        "selected_stream_index": entry.selected_stream_index,
        "selection_source": entry.selection_source,
        "inventory_digest": entry.inventory_digest,
        "policy_decision_ref": entry.policy_decision_ref,
        "custody_state": entry.custody_state,
        "inventory_artifact_id": entry.inventory_artifact_id,
        "inventory_payload_digest": entry.inventory_payload_digest,
    }


def _manifest_body(entries: tuple[SourceManifestEntry, ...]) -> dict[str, Any]:
    return {"entries": [_entry_dict(entry) for entry in entries], "schema_version": _MULTI_SOURCE_SCHEMA}


def _canonical_manifest_bytes(document: dict[str, Any]) -> bytes:
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_multi_source_manifest(bindings: Any) -> MultiSourceManifest:
    """Build a snapshot from exact Gate-0 SourceBinding values without source I/O."""
    values = tuple(bindings)
    if not values:
        raise ValueError("manifest requires a non-empty snapshot")
    if any(type(binding) is not SourceBinding for binding in values):
        raise TypeError("manifest accepts SourceBinding values only")
    revisions = [binding.revision_ref.revision_id for binding in values]
    locators = [binding.revision_ref.locator for binding in values]
    if len(set(revisions)) != len(revisions):
        raise ValueError("duplicate revision_id")
    if len(set(locators)) != len(locators):
        raise ValueError("duplicate locator")
    entries = []
    for binding in values:
        if str(binding.source_path) != binding.revision_ref.locator:
            raise ValueError("source path and inventory locator disagree")
        inventory = binding.inventory
        if type(inventory) is not InventoryPayload:
            raise ValueError("binding inventory has an invalid type")
        policy_ref = inventory.policy_decision.policy_decision_id
        if policy_ref != binding.policy_decision_ref:
            raise ValueError("policy decision reference disagrees with inventory")
        inventory_records = (*inventory.source_records, *inventory.discovery_records)
        for row in inventory_records:
            if not isinstance(row, dict):
                raise ValueError("inventory record has an invalid type")
            try:
                expected_record_digest = record_digest(row)
            except (TypeError, ValueError) as exc:
                raise ValueError("inventory record envelope is invalid") from exc
            if row.get("record_digest") != expected_record_digest:
                raise ValueError("inventory record digest mismatch")
        inventory_body = {
            "source_records": list(inventory.source_records),
            "discovery_records": list(inventory.discovery_records),
            "policy_decision_id": policy_ref,
        }
        expected_inventory_digest = digest_bytes(canonical_bytes(inventory_body))
        if inventory.inventory_digest != expected_inventory_digest:
            raise ValueError("inventory digest mismatch")
        records = [
            row.get("payload") for row in inventory.source_records
            if isinstance(row, dict) and isinstance(row.get("payload"), dict)
            and row["payload"].get("revision_id") == binding.revision_ref.revision_id
            and row["payload"].get("locator") == binding.revision_ref.locator
        ]
        if len(records) != 1:
            raise ValueError("binding must resolve to exactly one inventory record")
        record = records[0]
        if (record.get("content_id") != binding.revision_ref.content_id
                or record.get("content_digest") != binding.source_sha256
                or record.get("custody", {}).get("state") != binding.custody_state
                or binding.revision_ref not in inventory.revision_refs):
            raise ValueError("binding fields disagree with inventory provenance")
        envelope = binding.inventory_envelope
        if envelope is not None:
            envelope_payload = {"records": list(inventory.source_records), "revision_ids": [binding.revision_ref.revision_id]}
            if envelope.policy_decision_id != binding.policy_decision_ref or not envelope.binds(envelope_payload):
                raise ValueError("inventory artifact does not bind the source inventory")
        entries.append(SourceManifestEntry(
            revision_id=binding.revision_ref.revision_id,
            content_id=binding.revision_ref.content_id,
            source_path=binding.source_path,
            source_sha256=binding.source_sha256,
            selected_stream_index=binding.revision_ref.selected_stream_index,
            selection_source=binding.revision_ref.selection_source,
            inventory_digest=binding.inventory.inventory_digest,
            policy_decision_ref=binding.policy_decision_ref,
            custody_state=binding.custody_state,
            inventory_artifact_id=envelope.artifact_id if envelope else None,
            inventory_payload_digest=envelope.payload_digest if envelope else None,
        ))
    ordered = tuple(sorted(entries, key=lambda entry: (entry.revision_id.encode("utf-8"), str(entry.source_path).encode("utf-8"))))
    digest = hashlib.sha256(_canonical_manifest_bytes(_manifest_body(ordered))).hexdigest()
    return MultiSourceManifest(ordered, digest)


def save_multi_source_manifest(manifest: MultiSourceManifest, destination: str | Path) -> None:
    """Persist canonical JSON and refuse a destination that aliases a source."""
    if not isinstance(manifest, MultiSourceManifest):
        raise TypeError("manifest must be MultiSourceManifest")
    target = Path(destination)
    for entry in manifest.entries:
        if str(target) == str(entry.source_path):
            raise ValueError("manifest destination overlaps a source locator")
        try:
            if target.samefile(entry.source_path):
                raise ValueError("manifest destination aliases a source file")
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise ValueError("cannot verify manifest destination is separate from source files") from exc
    body = _manifest_body(manifest.entries)
    expected = hashlib.sha256(_canonical_manifest_bytes(body)).hexdigest()
    if manifest.manifest_digest != expected:
        raise ValueError("manifest digest mismatch")
    document = dict(body, manifest_digest=manifest.manifest_digest)
    target.write_bytes(_canonical_manifest_bytes(document))


def load_multi_source_manifest(source: str | Path) -> MultiSourceManifest:
    """Load and verify canonical manifest JSON without opening any listed source."""
    raw = Path(source).read_bytes()

    def reject_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON object key")
            result[key] = value
        return result

    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("invalid manifest JSON") from exc
    if not isinstance(document, dict) or set(document) != {"schema_version", "entries", "manifest_digest"}:
        raise ValueError("manifest fields mismatch")
    if document["schema_version"] != _MULTI_SOURCE_SCHEMA or not isinstance(document["entries"], list):
        raise ValueError("manifest schema mismatch")
    entries = []
    for item in document["entries"]:
        if not isinstance(item, dict) or set(item) != set(_ENTRY_FIELDS):
            raise ValueError("manifest entry fields mismatch")
        if not isinstance(item["source_path"], str):
            raise ValueError("source_path must be a string")
        try:
            entries.append(SourceManifestEntry(**{**item, "source_path": Path(item["source_path"])}))
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid manifest entry") from exc
    entry_tuple = tuple(entries)
    if not entry_tuple:
        raise ValueError("manifest requires a non-empty snapshot")
    if len({entry.revision_id for entry in entry_tuple}) != len(entry_tuple):
        raise ValueError("duplicate revision_id")
    if len({str(entry.source_path) for entry in entry_tuple}) != len(entry_tuple):
        raise ValueError("duplicate locator")
    ordered = tuple(sorted(entry_tuple, key=lambda entry: (entry.revision_id.encode("utf-8"), str(entry.source_path).encode("utf-8"))))
    if ordered != entry_tuple:
        raise ValueError("manifest entries are not canonically ordered")
    body = _manifest_body(entry_tuple)
    expected = hashlib.sha256(_canonical_manifest_bytes(body)).hexdigest()
    if not isinstance(document["manifest_digest"], str) or document["manifest_digest"] != expected:
        raise ValueError("manifest digest mismatch")
    if raw != _canonical_manifest_bytes(dict(body, manifest_digest=expected)):
        raise ValueError("manifest JSON is not canonical")
    return MultiSourceManifest(entry_tuple, expected)


def _synthetic_probe() -> ProbeEvidence:
    """Provide the minimal local probe required for a synthetic source.

    This is structural probe evidence, not a claim about a decoded media
    stream. Real media probing remains outside Gate-0/FVS scope.
    """
    return ProbeEvidence(
        ffprobe_json={"streams": [{"index": 0, "codec_type": "video"}]},
        time_base=(1, 1),
        probe_ref="synthetic_probe",
    )


def inventory_source(
    source_path: str | Path,
    run_dir: str | Path,
    policy: PolicyDecision,
    *,
    occurrence_id: str | None = None,
    revision_id: str | None = None,
    content_id: str | None = None,
    selected_stream_index: int = 0,
    now: str = "1970-01-01T00:00:00Z",
) -> SourceBinding:
    """Inventory one local source under an already-issued discovery policy.

    The source is opened only for hashing and Gate-0 inventory.  No copy,
    rewrite, canonicalization, or deletion is performed on the source path.
    """
    path = Path(source_path)
    if not path.is_file():
        raise ValueError("SOURCE_UNREADABLE")
    source_sha256 = digest_bytes(path.read_bytes())

    if revision_id is None:
        if len(policy.revision_scope) != 1:
            raise ValueError("REVISION_ID_REQUIRED_FOR_MULTI_SCOPE_POLICY")
        revision_id = policy.revision_scope[0]
    if re.fullmatch(r"[0-9a-fA-F]{64}", str(revision_id)):
        raise ValueError("revision identifier must remain a logical revision, not a content digest")
    if revision_id not in policy.revision_scope:
        raise ValueError("REVISION_OUTSIDE_POLICY_SCOPE")
    content_id = content_id or opaque_id("content", {"path": str(path), "digest": source_sha256})
    occurrence_id = occurrence_id or opaque_id("occurrence", {"revision": revision_id, "path": str(path)})
    occurrence = SourceOccurrence(occurrence_id, revision_id, content_id, path)
    payload = inventory(
        occurrences=(occurrence,),
        probe_by_revision={revision_id: _synthetic_probe()},
        authorization=policy,
        output_root=Path(run_dir),
        selected_stream_index=selected_stream_index,
        now=now,
    ).payload
    revision_ref = payload.revision_refs[0]
    manifest_payload = {"records": list(payload.source_records), "revision_ids": [revision_id]}
    envelope = ArtifactEnvelope.create(
        "source_manifest.json",
        manifest_payload,
        producer_attempt_id=opaque_id("attempt", {"source": source_sha256, "revision": revision_id}),
        policy_decision_id=policy.policy_decision_id,
        retention_class="SOURCE_REFERENCE",
        created_at=now,
    )
    return SourceBinding(
        revision_ref=revision_ref,
        source_path=path,
        source_sha256=source_sha256,
        inventory=payload,
        policy_decision_ref=policy.policy_decision_id,
        custody_state="PRESERVED",
        inventory_envelope=envelope,
    )
