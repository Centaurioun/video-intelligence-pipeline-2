"""Atomic, manifest-bound restart journal for multi-source reconciliation."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable, Mapping, Sequence

from .multi_source_lifecycle import plan_multi_source_reconciliation

SCHEMA = "vip_fvs.multi_source_run_journal.v1"
_TOP_KEYS = {"schema", "previous_manifest_digest", "current_manifest_digest", "generation_id", "space_id", "operations"}
_OP_KEYS = {"operation_id", "action", "locator", "old_digest", "old_revision", "new_digest", "new_revision", "state", "error"}


class JournalRefusal(RuntimeError):
    """Journal is corrupt, incompatible, or bound to different inputs."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _operation_payload(action: str, locator: str, old: Any, new: Any) -> dict[str, Any]:
    return {
        "action": action,
        "locator": locator,
        "old_digest": getattr(old, "source_sha256", None),
        "old_revision": getattr(old, "revision_id", None),
        "new_digest": getattr(new, "source_sha256", None),
        "new_revision": getattr(new, "revision_id", None),
    }


@dataclass
class OperationRecord:
    operation_id: str
    action: str
    locator: str
    old_digest: str | None
    old_revision: str | None
    new_digest: str | None
    new_revision: str | None
    state: str = "PENDING"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in sorted(_OP_KEYS)}


@dataclass
class MultiSourceRunJournal:
    path: Path
    previous_manifest_digest: str
    current_manifest_digest: str
    generation_id: str
    space_id: str
    operations: list[OperationRecord]
    _previous: Any = field(repr=False)
    _current: Any = field(repr=False)
    _synthetic_attestations: Sequence[Mapping[str, Any]] | None = field(default=None, repr=False)
    _synthetic_authorizations: Sequence[Mapping[str, Any]] | None = field(default=None, repr=False)
    _authorize_source: Callable[[Any], bool] | None = field(default=None, repr=False)
    _preflight_output_root: Path | None = field(default=None, repr=False)

    def _require_fresh_preflight(self) -> None:
        opted_in = self._synthetic_attestations is not None or self._synthetic_authorizations is not None
        if not opted_in:
            return
        if self._authorize_source is None or self._preflight_output_root is None:
            from .corpus_admission import CorpusAdmissionError
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        from .multi_source_index import _preflight_batch, _preflight_source_bytes
        plan = plan_multi_source_reconciliation(self._previous, self._current)
        body = [{"locator": op.locator, "kind": op.kind,
                 "old_revision": getattr(op.previous_entry, "revision_id", None),
                 "old_digest": getattr(op.previous_entry, "source_sha256", None),
                 "new_revision": getattr(op.current_entry, "revision_id", None),
                 "new_digest": getattr(op.current_entry, "source_sha256", None)}
                for op in plan.operations]
        plan_digest = hashlib.sha256(_canonical(body)).hexdigest()
        _preflight_batch(
            self._current.entries, attestations=self._synthetic_attestations,
            authorizations=self._synthetic_authorizations, operation="multi-source-reconcile",
            output_root=self._preflight_output_root,
            manifest_digest=self._current.manifest_digest, plan_digest=plan_digest,
        )
        _preflight_source_bytes(self._current.entries, self._authorize_source)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "previous_manifest_digest": self.previous_manifest_digest,
            "current_manifest_digest": self.current_manifest_digest,
            "generation_id": self.generation_id,
            "space_id": self.space_id,
            "operations": [item.to_dict() for item in self.operations],
        }

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = _canonical(self.to_dict())
        fd, temp_name = tempfile.mkstemp(prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, self.path)
            try:
                dir_fd = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            except OSError:
                pass
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def run(self, index_entry: Callable[[Any], Any], remove_location: Callable[[str], Any]) -> "MultiSourceRunJournal":
        if not callable(index_entry) or not callable(remove_location):
            raise ValueError("index_entry and remove_location callbacks are required")
        self._require_fresh_preflight()
        prior = {str(item.source_path): item for item in self._previous.entries}
        current = {str(item.source_path): item for item in self._current.entries}
        errors: list[Exception] = []
        records = {item.operation_id: item for item in self.operations}

        def mark(record: OperationRecord, state: str, error: str | None = None) -> None:
            record.state, record.error = state, error
            self._persist()

        # Existing deterministic plan orders additions/changes before removals.
        plan = plan_multi_source_reconciliation(self._previous, self._current)
        for planned in plan.operations:
            payload = _operation_payload(planned.kind, planned.locator, planned.previous_entry, planned.current_entry)
            operation_id = hashlib.sha256(_canonical(payload)).hexdigest()
            record = records[operation_id]
            if record.state == "COMPLETE":
                continue
            # FAILED/DEFERRED are visible durable outcomes but are eligible for replay.
            if planned.kind == "UNCHANGED":
                mark(record, "COMPLETE")
                continue
            if planned.kind in {"ADDED", "CHANGED"}:
                mark(record, "PENDING")
                try:
                    outcome = index_entry(current[planned.locator])
                    disposition = getattr(outcome, "disposition", outcome)
                    if disposition in {"FAILED", "REFUSED"}:
                        detail = getattr(outcome, "error", None)
                        reason = f"{disposition}:{detail}" if detail else str(disposition)
                        mark(record, "FAILED", reason)
                        errors.append(RuntimeError(reason))
                    else:
                        mark(record, "COMPLETE")
                except Exception as exc:
                    mark(record, "FAILED", f"{type(exc).__name__}:{exc}")
                    errors.append(exc)
        replacements: dict[str, list[OperationRecord]] = {}
        for planned in plan.operations:
            if planned.kind in {"ADDED", "CHANGED"} and planned.current_entry is not None:
                replacements.setdefault(planned.current_entry.source_sha256, []).append(records[hashlib.sha256(_canonical(_operation_payload(planned.kind, planned.locator, planned.previous_entry, planned.current_entry))).hexdigest()])
        for planned in plan.operations:
            if planned.kind != "REMOVED":
                continue
            payload = _operation_payload(planned.kind, planned.locator, planned.previous_entry, planned.current_entry)
            record = records[hashlib.sha256(_canonical(payload)).hexdigest()]
            if record.state == "COMPLETE":
                continue
            alternatives = replacements.get(planned.previous_entry.source_sha256, [])
            if alternatives and not any(item.state == "COMPLETE" for item in alternatives):
                mark(record, "DEFERRED", "DEFERRED_REPLACEMENT_FAILED")
                continue
            try:
                mark(record, "PENDING")
                remove_location(planned.locator)
                mark(record, "COMPLETE")
            except Exception as exc:
                mark(record, "FAILED", f"{type(exc).__name__}:{exc}")
                errors.append(exc)
        if errors:
            raise errors[0]
        return self


def start_or_resume(path: str | Path, previous: Any, current: Any, *, generation_id: str, space_id: str,
                    synthetic_attestations: Sequence[Mapping[str, Any]] | None = None,
                    synthetic_authorizations: Sequence[Mapping[str, Any]] | None = None,
                    authorize_source: Callable[[Any], bool] | None = None,
                    preflight_output_root: str | Path | None = None) -> MultiSourceRunJournal:
    """Load only a closed, exact-input journal or atomically create one."""
    target = Path(path)
    old_digest, new_digest = previous.manifest_digest, current.manifest_digest
    if not all(isinstance(value, str) and value for value in (old_digest, new_digest, generation_id, space_id)):
        raise JournalRefusal("manifest, generation, and space identities are required")
    plan = plan_multi_source_reconciliation(previous, current)
    opted_in = synthetic_attestations is not None or synthetic_authorizations is not None
    if opted_in:
        if authorize_source is None or preflight_output_root is None:
            from .corpus_admission import CorpusAdmissionError
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        from .multi_source_index import _preflight_batch, _preflight_source_bytes
        body = [{"locator": op.locator, "kind": op.kind,
                 "old_revision": getattr(op.previous_entry, "revision_id", None),
                 "old_digest": getattr(op.previous_entry, "source_sha256", None),
                 "new_revision": getattr(op.current_entry, "revision_id", None),
                 "new_digest": getattr(op.current_entry, "source_sha256", None)}
                for op in plan.operations]
        plan_digest = hashlib.sha256(_canonical(body)).hexdigest()
        _preflight_batch(
            current.entries, attestations=synthetic_attestations,
            authorizations=synthetic_authorizations, operation="multi-source-reconcile",
            output_root=Path(preflight_output_root), manifest_digest=current.manifest_digest,
            plan_digest=plan_digest,
        )
        _preflight_source_bytes(current.entries, authorize_source)
    expected = []
    for item in plan.operations:
        payload = _operation_payload(item.kind, item.locator, item.previous_entry, item.current_entry)
        expected.append(OperationRecord(hashlib.sha256(_canonical(payload)).hexdigest(), **payload))
    if target.exists():
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or set(raw) != _TOP_KEYS or raw.get("schema") != SCHEMA:
                raise ValueError("closed schema mismatch")
            if (raw["previous_manifest_digest"], raw["current_manifest_digest"], raw["generation_id"], raw["space_id"]) != (old_digest, new_digest, generation_id, space_id):
                raise JournalRefusal("journal identity mismatch")
            if not isinstance(raw["operations"], list) or len(raw["operations"]) != len(expected):
                raise ValueError("operation set mismatch")
            operations = []
            for saved, derived in zip(raw["operations"], expected):
                if not isinstance(saved, dict) or set(saved) != _OP_KEYS:
                    raise ValueError("operation closed schema mismatch")
                if any(saved[key] != derived.to_dict()[key] for key in _OP_KEYS - {"state", "error"}):
                    raise ValueError("operation identity mismatch")
                if saved["state"] not in {"PENDING", "COMPLETE", "FAILED", "DEFERRED"}:
                    raise ValueError("invalid operation state")
                operations.append(OperationRecord(**saved))
        except JournalRefusal:
            raise
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
            raise JournalRefusal(f"invalid journal: {exc}") from exc
    else:
        operations = expected
    journal = MultiSourceRunJournal(
        target, old_digest, new_digest, generation_id, space_id, operations, previous, current,
        synthetic_attestations, synthetic_authorizations, authorize_source,
        Path(preflight_output_root) if preflight_output_root is not None else None,
    )
    if not target.exists():
        journal._persist()
    return journal


__all__ = ["JournalRefusal", "MultiSourceRunJournal", "OperationRecord", "start_or_resume"]
