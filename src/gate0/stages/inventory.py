"""Inventory stage orchestration and atomic local publication seam."""
from __future__ import annotations

from pathlib import Path
import tempfile
import json
from typing import Any, Mapping

from gate0.canonical_json import canonical_bytes, canonical_jsonl_bytes
from gate0.inventory import InventoryPayload, SourceOccurrence, ProbeEvidence, build_inventory
from gate0.policy import PolicyDecision


def inventory(*, occurrences: tuple[SourceOccurrence, ...] | list[SourceOccurrence], probe_by_revision: Mapping[str, ProbeEvidence], authorization: PolicyDecision, output_root: Path | None = None, attempt_id: str = "attempt_inventory", selected_stream_index: int | None = None, now: str = "1970-01-01T00:00:00Z") -> "InventoryResult":
    payload = build_inventory(occurrences, probe_by_revision, authorization, selected_stream_index, now=now)
    if output_root is not None:
        output_root = Path(output_root)
        output_root.parent.mkdir(parents=True, exist_ok=True)
        # Policy is serialized first; discovery artifacts are published only
        # after all foreign-key checks have completed.
        policy_record = {"record_id": authorization.policy_decision_id, "record_type": "policy_decision", "record_schema_version": "gate0.v1", "record_digest": "", "payload": authorization.to_dict()}
        from gate0.contracts.types import record_digest
        policy_record["record_digest"] = record_digest(policy_record)
        policy_bytes = canonical_jsonl_bytes([policy_record])
        source_bytes = canonical_bytes({"records": list(payload.source_records), "revision_ids": [o.revision_id for o in occurrences]})
        auth_bytes = canonical_jsonl_bytes(payload.discovery_records)
        # Stage all files outside the destination, then rename the complete
        # set. A failed write cannot expose a partial discovery artifact set.
        with tempfile.TemporaryDirectory(prefix="gate0-inventory-", dir=output_root.parent) as staging:
            staging_path = Path(staging)
            (staging_path / "policy_decisions.jsonl").write_bytes(policy_bytes)
            (staging_path / "source_manifest.json").write_bytes(source_bytes)
            (staging_path / "discovery_authorizations.jsonl").write_bytes(auth_bytes)
            existed = output_root.exists()
            output_root.mkdir(parents=True, exist_ok=True)
            names = ("policy_decisions.jsonl", "source_manifest.json", "discovery_authorizations.jsonl")
            prior = {name: (output_root / name).read_bytes() if (output_root / name).exists() else None for name in names}
            replaced: list[str] = []
            try:
                for name in names:
                    _replace(staging_path / name, output_root / name)
                    replaced.append(name)
            except Exception:
                for name in replaced:
                    target = output_root / name
                    if prior[name] is None:
                        target.unlink(missing_ok=True)
                    else:
                        target.write_bytes(prior[name])
                if not existed:
                    try:
                        output_root.rmdir()
                    except OSError:
                        pass
                raise
    return InventoryResult("SUCCEEDED", 0, attempt_id, (), (), payload)


class InventoryResult:
    def __init__(self, stage_status: str, exit_code: int, attempt_id: str, output_artifact_refs: tuple[object, ...], failure_refs: tuple[str, ...], payload: InventoryPayload):
        self.stage_status, self.exit_code, self.attempt_id = stage_status, exit_code, attempt_id
        self.output_artifact_refs, self.failure_refs, self.payload = output_artifact_refs, failure_refs, payload


def _atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _replace(source: Path, target: Path) -> None:
    source.replace(target)
