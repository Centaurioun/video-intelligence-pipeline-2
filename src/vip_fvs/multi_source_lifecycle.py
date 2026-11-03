"""Deterministic, explicit-snapshot reconciliation for multi-source indexes.

This module does no discovery and owns no mutable state. Callers provide the
H3-C02 indexing and H3-B02 exact-location removal operations.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


@dataclass(frozen=True)
class ReconciliationOperation:
    locator: str
    kind: str
    previous_entry: Any | None
    current_entry: Any | None


@dataclass(frozen=True)
class MultiSourceReconciliationPlan:
    operations: tuple[ReconciliationOperation, ...]


@dataclass(frozen=True)
class OperationDisposition:
    locator: str
    kind: str
    disposition: str


@dataclass(frozen=True)
class MultiSourceReconciliationResult:
    plan: MultiSourceReconciliationPlan
    dispositions: tuple[OperationDisposition, ...]
    deferred_removals: tuple[str, ...]
    previous_manifest_digest: str
    current_manifest_digest: str
    generation_id: str
    space_id: str


def _entries_by_locator(manifest: Any) -> dict[str, Any]:
    entries = getattr(manifest, "entries", None)
    if not isinstance(entries, tuple):
        raise TypeError("manifest entries must be a tuple")
    by_locator: dict[str, Any] = {}
    for entry in entries:
        locator = str(entry.source_path)
        if locator in by_locator:
            raise ValueError("duplicate locator")
        by_locator[locator] = entry
    return by_locator


def plan_multi_source_reconciliation(previous: Any, current: Any) -> MultiSourceReconciliationPlan:
    """Classify exact locator strings and order additions/changes before removals."""
    old, new = _entries_by_locator(previous), _entries_by_locator(current)
    operations: list[ReconciliationOperation] = []
    for locator in sorted(old.keys() | new.keys(), key=lambda value: value.encode("utf-8")):
        before, after = old.get(locator), new.get(locator)
        if before is None:
            kind = "ADDED"
        elif after is None:
            kind = "REMOVED"
        elif before.source_sha256 == after.source_sha256:
            kind = "UNCHANGED"
        else:
            kind = "CHANGED"
        operations.append(ReconciliationOperation(locator, kind, before, after))
    order = {"ADDED": 0, "CHANGED": 0, "UNCHANGED": 1, "REMOVED": 2}
    operations.sort(key=lambda op: (order[op.kind], op.locator.encode("utf-8")))
    return MultiSourceReconciliationPlan(tuple(operations))


def reconcile_multi_source_manifests(
    previous: Any,
    current: Any,
    *,
    index_entry: Callable[[Any], Any],
    remove_location: Callable[[str], Any],
    generation_id: str,
    space_id: str,
    synthetic_attestations: Sequence[Mapping[str, Any]] | None = None,
    synthetic_authorizations: Sequence[Mapping[str, Any]] | None = None,
    authorize_source: Callable[[Any], bool] | None = None,
    preflight_output_root: str | Path | None = None,
) -> MultiSourceReconciliationResult:
    """Apply a plan with add/change-before-remove ordering and move protection.

    ``index_entry`` must bind the manifest entry to the accepted H3-C02 API;
    ``remove_location`` must call the H3-B02 exact location-removal API. The
    callbacks make side effects explicit and keep this function testable.
    """
    if not callable(index_entry) or not callable(remove_location):
        raise ValueError("index_entry and remove_location callbacks are required")
    plan = plan_multi_source_reconciliation(previous, current)
    opted_in = synthetic_attestations is not None or synthetic_authorizations is not None
    if opted_in:
        if authorize_source is None or preflight_output_root is None:
            from .corpus_admission import CorpusAdmissionError
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        from .multi_source_index import _preflight_batch, _preflight_source_bytes
        plan_body = [{"locator": op.locator, "kind": op.kind,
                      "old_revision": getattr(op.previous_entry, "revision_id", None),
                      "old_digest": getattr(op.previous_entry, "source_sha256", None),
                      "new_revision": getattr(op.current_entry, "revision_id", None),
                      "new_digest": getattr(op.current_entry, "source_sha256", None)}
                     for op in plan.operations]
        plan_digest = hashlib.sha256(json.dumps(plan_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        _preflight_batch(
            current.entries, attestations=synthetic_attestations,
            authorizations=synthetic_authorizations, operation="multi-source-reconcile",
            output_root=Path(preflight_output_root), manifest_digest=current.manifest_digest,
            plan_digest=plan_digest,
        )
        _preflight_source_bytes(current.entries, authorize_source)
    indexed: dict[str, bool] = {}
    outcomes: list[OperationDisposition] = []
    deferred: list[str] = []
    added_or_changed = [op for op in plan.operations if op.kind in {"ADDED", "CHANGED"}]
    unchanged = [op for op in plan.operations if op.kind == "UNCHANGED"]
    removals = [op for op in plan.operations if op.kind == "REMOVED"]
    for op in added_or_changed:
        try:
            detail = index_entry(op.current_entry)
            disposition = getattr(detail, "disposition", detail if isinstance(detail, str) else "SUCCEEDED")
            ok = disposition not in {"FAILED", "REFUSED"}
            indexed[op.locator] = ok
            outcomes.append(OperationDisposition(op.locator, op.kind, str(disposition)))
        except Exception as exc:  # isolate independent operations
            indexed[op.locator] = False
            outcomes.append(OperationDisposition(op.locator, op.kind, f"FAILED:{type(exc).__name__}:{exc}"))
    outcomes.extend(OperationDisposition(op.locator, op.kind, "UNCHANGED") for op in unchanged)

    replacement_by_digest: dict[str, list[ReconciliationOperation]] = {}
    old_digest_by_removal: dict[str, str] = {}
    for op in added_or_changed:
        if op.current_entry is not None:
            replacement_by_digest.setdefault(op.current_entry.source_sha256, []).append(op)
    for op in removals:
        old_digest_by_removal[op.locator] = op.previous_entry.source_sha256

    for op in removals:
        prior_digest = old_digest_by_removal[op.locator]
        replacements = replacement_by_digest.get(prior_digest, [])
        if replacements and not any(indexed.get(repl.locator, False) for repl in replacements):
            deferred.append(op.locator)
            outcomes.append(OperationDisposition(op.locator, op.kind, "DEFERRED_REPLACEMENT_FAILED"))
            continue
        try:
            detail = remove_location(op.locator)
            removed = getattr(detail, "removed", None)
            disposition = "ALREADY_ABSENT" if removed is False else "REMOVED"
            outcomes.append(OperationDisposition(op.locator, op.kind, disposition))
        except Exception as exc:
            outcomes.append(OperationDisposition(op.locator, op.kind, f"FAILED:{type(exc).__name__}:{exc}"))

    return MultiSourceReconciliationResult(
        plan=plan,
        dispositions=tuple(outcomes),
        deferred_removals=tuple(deferred),
        previous_manifest_digest=previous.manifest_digest,
        current_manifest_digest=current.manifest_digest,
        generation_id=generation_id,
        space_id=space_id,
    )


def reconcile_multi_source_index(
    previous: Any,
    current: Any,
    *,
    index_root: Path,
    engine: Any,
    semantic_space: Any,
    image_embedder: Any,
    authorize_source: Callable[[Any], bool],
    synthetic_attestations: Sequence[Mapping[str, Any]] | None = None,
    synthetic_authorizations: Sequence[Mapping[str, Any]] | None = None,
) -> MultiSourceReconciliationResult:
    """Bind reconciliation to the accepted H3-C02 and H3-B02 APIs."""
    from persistent_local_index.indexer import remove_source_location
    from .multi_source_index import index_multi_source_manifest
    from .source_adapter import MultiSourceManifest

    opted_in = synthetic_attestations is not None or synthetic_authorizations is not None
    if opted_in:
        from .multi_source_index import _preflight_batch, _preflight_source_bytes
        plan = plan_multi_source_reconciliation(previous, current)
        plan_body = [{"locator": op.locator, "kind": op.kind,
                      "old_revision": getattr(op.previous_entry, "revision_id", None),
                      "old_digest": getattr(op.previous_entry, "source_sha256", None),
                      "new_revision": getattr(op.current_entry, "revision_id", None),
                      "new_digest": getattr(op.current_entry, "source_sha256", None)}
                     for op in plan.operations]
        plan_digest = hashlib.sha256(json.dumps(plan_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        _preflight_batch(
            current.entries, attestations=synthetic_attestations,
            authorizations=synthetic_authorizations, operation="multi-source-reconcile",
            output_root=Path(index_root), manifest_digest=current.manifest_digest,
            plan_digest=plan_digest,
        )
        _preflight_source_bytes(current.entries, authorize_source)

    spec = engine.build_generation_spec(semantic_space)
    if opted_in:
        # Generation setup is caller-controlled and may change a bound source.
        # Revalidate the full current batch before indexing or removals begin.
        from .multi_source_index import _preflight_source_bytes
        _preflight_source_bytes(current.entries, authorize_source)

    def index_entry(entry: Any) -> Any:
        # The C02 API consumes a closed manifest snapshot. Preserve the exact
        # entry, and use a deterministic digest for this one-operation view.
        body = {
            "locator": str(entry.source_path),
            "revision_id": entry.revision_id,
            "source_sha256": entry.source_sha256,
        }
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        one = MultiSourceManifest((entry,), digest)
        outcome = index_multi_source_manifest(
            one, index_root=Path(index_root), engine=engine,
            semantic_space=semantic_space, image_embedder=image_embedder,
            authorize_source=authorize_source,
        )
        if len(outcome.results) != 1:
            raise ValueError("ENGINE_RESULT_CARDINALITY_MISMATCH")
        return outcome.results[0]

    return reconcile_multi_source_manifests(
        previous, current,
        index_entry=index_entry,
        remove_location=lambda locator: remove_source_location(Path(index_root), spec, Path(locator)),
        generation_id=spec.generation_id,
        space_id=spec.space_id,
    )


__all__ = [
    "MultiSourceReconciliationPlan", "MultiSourceReconciliationResult",
    "OperationDisposition", "ReconciliationOperation",
    "plan_multi_source_reconciliation", "reconcile_multi_source_manifests",
    "reconcile_multi_source_index",
]
