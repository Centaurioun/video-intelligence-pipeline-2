"""Exact Gate-1 artifact closure, serialization, and frozen protocol digests.

The closure is exactly ten files. Digests are content-bound and computed over
canonical JSON, so any post-freeze edit to a covered field is detectable.
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from gate1.canonical_json import canonical_bytes, canonical_jsonl, sha256_digest
from gate1.contracts.types import (
    BenchmarkEnvelope,
    CapabilityDescriptor,
    ComparisonContract,
    EmbeddingPayload,
    EmbeddingRecord,
    Judgment,
    PolicyDecision,
    RankedCandidate,
)

ARTIFACT_FILENAMES: tuple[str, ...] = (
    "benchmark_report.json",
    "capability_descriptors.jsonl",
    "comparison_contract.json",
    "embedding_results.jsonl",
    "failure_ledger.json",
    "judgments.jsonl",
    "policy_decisions.jsonl",
    "ranked_candidates.jsonl",
    "run_manifest.json",
    "synthetic_receipt.json",
)

JSONL_ARTIFACTS = frozenset(name for name in ARTIFACT_FILENAMES if name.endswith(".jsonl"))

#: Envelope-owned fields that an operation payload may never carry.
ENVELOPE_OWNED_FIELDS = frozenset(
    {
        "record_id",
        "comparison_id",
        "run_id",
        "attempt_id",
        "arm_id",
        "input_refs",
        "consumed_coverage",
        "raw_response_artifact_ref",
        "absence_reason",
        "requested_model",
        "resolved_backend",
        "config_digest",
        "policy_decision_id",
        "provider_status",
        "per_item_errors",
        "wall_time_ms",
    }
)

EMBEDDING_PAYLOAD_FIELDS = (
    "space_id",
    "representation_id",
    "query_id",
    "candidate_id",
    "kind",
    "vector",
    "failure_reason",
)


class ArtifactError(ValueError):
    """Raised when an artifact root is malformed or incomplete."""


# --------------------------------------------------------------------------- #
# Record -> canonical payload
# --------------------------------------------------------------------------- #

def envelope_payload(envelope: BenchmarkEnvelope) -> dict[str, Any]:
    return {
        "record_id": envelope.record_id,
        "comparison_id": envelope.comparison_id,
        "run_id": envelope.run_id,
        "attempt_id": envelope.attempt_id,
        "arm_id": envelope.arm_id,
        "input_refs": list(envelope.input_refs),
        "consumed_coverage": dict(envelope.consumed_coverage),
        "raw_response_artifact_ref": envelope.raw_response_artifact_ref,
        "absence_reason": envelope.absence_reason,
        "requested_model": envelope.requested_model,
        "resolved_backend": envelope.resolved_backend,
        "config_digest": envelope.config_digest,
        "policy_decision_id": envelope.policy_decision_id,
        "request_ref": envelope.request_ref,
        "judgment_version_refs": list(envelope.judgment_version_refs),
        "resource_observations": dict(envelope.resource_observations),
        "validity_ref": envelope.validity_ref,
        "outcome_ref": envelope.outcome_ref,
        "provider_status": envelope.provider_status,
        "per_item_errors": list(envelope.per_item_errors),
        "wall_time_ms": envelope.wall_time_ms,
    }


def embedding_payload_payload(payload: EmbeddingPayload) -> dict[str, Any]:
    return {
        "space_id": payload.space_id,
        "representation_id": payload.representation_id,
        "query_id": payload.query_id,
        "candidate_id": payload.candidate_id,
        "kind": payload.kind,
        "vector": list(payload.vector) if payload.vector is not None else None,
        "failure_reason": payload.failure_reason,
    }


def embedding_record_payload(record: EmbeddingRecord) -> dict[str, Any]:
    return {
        "envelope": envelope_payload(record.envelope),
        "payload": embedding_payload_payload(record.payload),
    }


def _jsonable(value: Any) -> Any:
    """Decode bytes to UTF-8 text so canonical JSON can serialize the value."""
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def ranked_candidate_payload(candidate: RankedCandidate) -> dict[str, Any]:
    return {
        "record_id": candidate.record_id,
        "arm_id": candidate.arm_id,
        "query_id": candidate.query_id,
        "candidate_id": candidate.candidate_id,
        "representation_id": candidate.representation_id,
        "space_id": candidate.space_id,
        "score": candidate.score,
        "rank": candidate.rank,
        "tie_key": _jsonable(candidate.tie_key) if candidate.tie_key is not None else None,
        "coverage_status": candidate.coverage_status,
    }


def failure_ledger_payload(
    *,
    run_id: str,
    comparison_id: str,
    attempt_id: str,
    event_type: str,
    reason: str,
    affected_refs: Sequence[str] = (),
    record_id: str = "failure-1",
) -> dict[str, Any]:
    """Build the run-bound failure/omission ledger record.

    The ledger is an output even when nothing failed: `event_type="NONE"` plus
    an explicit reason makes the absence a record rather than an empty row set.
    """
    return {
        "record_id": record_id,
        "run_id": run_id,
        "comparison_id": comparison_id,
        "event_type": event_type,
        "attempt_id": attempt_id,
        "affected_refs": list(affected_refs),
        "reason": reason,
        "occurred_at": "SYNTHETIC_FIXED",
    }


def judgment_payload(judgment: Judgment) -> dict[str, Any]:
    return {
        "record_id": judgment.record_id,
        "query_id": judgment.query_id,
        "candidate_id": judgment.candidate_id,
        "relevant": judgment.relevant,
        "reviewer_id": judgment.reviewer_id,
        "synthetic": judgment.synthetic,
        "evidence_class": judgment.evidence_class,
    }


# --------------------------------------------------------------------------- #
# Canonical payload -> record (inverse of the serializers above)
# --------------------------------------------------------------------------- #

def comparison_contract_from_payload(payload: Mapping[str, Any]) -> ComparisonContract:
    return ComparisonContract(
        comparison_id=payload["comparison_id"],
        execution_mode=payload["execution_mode"],
        question=payload["question"],
        estimand=payload["estimand"],
        changed_axis=payload["changed_axis"],
        pinned_controls=dict(payload["pinned_controls"]),
        arm_ids=tuple(payload["arm_ids"]),
        operation=payload["operation"],
        primary_metric=dict(payload["primary_metric"]),
        decision_rule=dict(payload["decision_rule"]),
        validity_rules=dict(payload["validity_rules"]),
        dependency_refs=dict(payload["dependency_refs"]),
        policy_eligibility=dict(payload["policy_eligibility"]),
        tie_rule=payload["tie_rule"],
        retry_policy=payload["retry_policy"],
        resource_budget=dict(payload["resource_budget"]),
        owner_approval_ref=payload["owner_approval_ref"],
    )


def capability_descriptor_from_payload(payload: Mapping[str, Any]) -> CapabilityDescriptor:
    return CapabilityDescriptor(
        record_id=payload["record_id"],
        arm_id=payload["arm_id"],
        capability_revision=payload["capability_revision"],
        provider_family=payload["provider_family"],
        operation=payload["operation"],
        input_mode=payload["input_mode"],
        requested_model=payload["requested_model"],
        resolved_backend=payload["resolved_backend"],
        runtime_revision=payload["runtime_revision"],
        config_digest=payload["config_digest"],
        space_id=payload["space_id"],
        policy_decision_id=payload["policy_decision_id"],
        window_profile_digest=payload["window_profile_digest"],
        metric=payload["metric"],
        normalization=payload["normalization"],
    )


def policy_decision_from_payload(payload: Mapping[str, Any]) -> PolicyDecision:
    return PolicyDecision(
        record_id=payload["record_id"],
        policy_decision_id=payload["policy_decision_id"],
        decision=payload["decision"],
        processing_boundary=payload["processing_boundary"],
    )


def judgment_from_payload(payload: Mapping[str, Any]) -> Judgment:
    return Judgment(
        record_id=payload["record_id"],
        query_id=payload["query_id"],
        candidate_id=payload["candidate_id"],
        relevant=bool(payload["relevant"]),
        reviewer_id=payload["reviewer_id"],
        synthetic=bool(payload["synthetic"]),
        evidence_class=payload["evidence_class"],
    )


def embedding_record_from_payload(payload: Mapping[str, Any]) -> EmbeddingRecord:
    envelope = payload["envelope"]
    body = payload["payload"]
    return EmbeddingRecord(
        envelope=BenchmarkEnvelope(
            record_id=envelope["record_id"],
            comparison_id=envelope["comparison_id"],
            run_id=envelope["run_id"],
            attempt_id=envelope["attempt_id"],
            arm_id=envelope["arm_id"],
            input_refs=tuple(envelope["input_refs"]),
            consumed_coverage=dict(envelope["consumed_coverage"]),
            raw_response_artifact_ref=envelope["raw_response_artifact_ref"],
            absence_reason=envelope["absence_reason"],
            requested_model=envelope["requested_model"],
            resolved_backend=envelope["resolved_backend"],
            config_digest=envelope["config_digest"],
            policy_decision_id=envelope["policy_decision_id"],
            request_ref=envelope["request_ref"],
            judgment_version_refs=tuple(envelope["judgment_version_refs"]),
            resource_observations=dict(envelope["resource_observations"]),
            validity_ref=envelope["validity_ref"],
            outcome_ref=envelope["outcome_ref"],
            provider_status=envelope["provider_status"],
            per_item_errors=tuple(envelope["per_item_errors"]),
            wall_time_ms=envelope["wall_time_ms"],
        ),
        payload=EmbeddingPayload(
            space_id=body["space_id"],
            representation_id=body["representation_id"],
            query_id=body["query_id"],
            candidate_id=body["candidate_id"],
            kind=body["kind"],
            vector=tuple(body["vector"]) if body["vector"] is not None else None,
            failure_reason=body["failure_reason"],
        ),
    )


# --------------------------------------------------------------------------- #
# Frozen digests
# --------------------------------------------------------------------------- #

def contract_digest(contract: Mapping[str, Any]) -> str:
    return sha256_digest(contract)


def descriptor_digest(descriptors: Sequence[Mapping[str, Any]]) -> str:
    return sha256_digest(list(descriptors))


def policy_digest(policies: Sequence[Mapping[str, Any]]) -> str:
    return sha256_digest(list(policies))


def frozen_protocol_payload(
    contract: Mapping[str, Any],
    descriptors: Sequence[Mapping[str, Any]],
    policies: Sequence[Mapping[str, Any]],
    run_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """The exact scientific identity of a frozen comparison.

    Covers the canonical contract, ordered descriptors and policies, source
    partitions, the declared ranking inputs, the tie/retry/resource controls, and the
    synthetic fault control. It excludes the execution-authority SHA, paths,
    time, PID, and resource observations, so legitimate canonical-main
    advancement cannot change a frozen synthetic scientific result.
    """
    return {
        "comparison_contract": contract,
        "capability_descriptors": list(descriptors),
        "policy_decisions": list(policies),
        "source_partitions": run_manifest["source_partitions"],
        "ranking_input_declarations": list(run_manifest["candidate_production_inputs"]),
        "tie_rule": contract["tie_rule"],
        "retry_policy": contract["retry_policy"],
        "resource_budget": contract["resource_budget"],
        "synthetic_fault": run_manifest["synthetic_fault"],
    }


def frozen_protocol_digest(
    contract: Mapping[str, Any],
    descriptors: Sequence[Mapping[str, Any]],
    policies: Sequence[Mapping[str, Any]],
    run_manifest: Mapping[str, Any],
) -> str:
    return sha256_digest(frozen_protocol_payload(contract, descriptors, policies, run_manifest))


def derived_run_id(frozen_digest: str) -> str:
    """`syn-` plus the first 16 hex characters of the frozen protocol digest."""
    return f"syn-{frozen_digest[:16]}"


# --------------------------------------------------------------------------- #
# Artifact root I/O
# --------------------------------------------------------------------------- #

def write_artifact_root(root: Path, candidate: Mapping[str, object]) -> None:
    """Write exactly the ten artifacts, refusing a non-empty destination."""
    destination = Path(root)
    if set(candidate) != set(ARTIFACT_FILENAMES):
        raise ArtifactError("candidate artifact set must be exactly the ten named files")
    if destination.exists():
        if not destination.is_dir():
            raise ArtifactError(f"{destination} exists and is not a directory")
        if any(destination.iterdir()):
            raise ArtifactError(f"{destination} is not empty; refusing to write")
    destination.mkdir(parents=True, exist_ok=True)
    for name in ARTIFACT_FILENAMES:
        content = candidate[name]
        if name in JSONL_ARTIFACTS:
            if not isinstance(content, list):
                raise ArtifactError(f"{name} must be a list of records")
            text = canonical_jsonl(content)
        else:
            if not isinstance(content, Mapping):
                raise ArtifactError(f"{name} must be a JSON object")
            text = json.dumps(content, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":"), allow_nan=False) + "\n"
        (destination / name).write_text(text, encoding="utf-8")


def load_artifact_root(path: Path) -> dict[str, object]:
    """Load an artifact root, requiring the exact ten-file closure."""
    _validate_artifact_registry()
    root = Path(path)
    if not root.is_dir():
        raise ArtifactError(f"artifact root {root} does not exist")
    entries = list(root.iterdir())
    present = {entry.name for entry in entries if entry.is_file()}
    invalid_entries = sorted(entry.name for entry in entries if not entry.is_file())
    missing = set(ARTIFACT_FILENAMES) - present
    extra = present - set(ARTIFACT_FILENAMES)
    if missing or extra or invalid_entries:
        raise ArtifactError(
            f"artifact closure mismatch; missing={sorted(missing)} extra={sorted(extra)} "
            f"invalid_entries={invalid_entries}"
        )

    loaded: dict[str, object] = {}
    for name in ARTIFACT_FILENAMES:
        raw = (root / name).read_text(encoding="utf-8")
        try:
            if name in JSONL_ARTIFACTS:
                rows: list[Any] = []
                for line in raw.splitlines():
                    if line.strip() == "":
                        continue
                    rows.append(json.loads(line))
                canonical = canonical_jsonl(rows)
                if raw != canonical:
                    raise ArtifactError(f"{name} is not canonical ordered JSONL")
                loaded[name] = rows
            else:
                value = json.loads(raw)
                if not isinstance(value, Mapping):
                    raise ArtifactError(f"{name} must contain a JSON object")
                canonical = json.dumps(value, ensure_ascii=False, sort_keys=True,
                                       separators=(",", ":"), allow_nan=False) + "\n"
                if raw != canonical:
                    raise ArtifactError(f"{name} is not canonical JSON")
                loaded[name] = value
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            if isinstance(exc, ArtifactError):
                raise
            raise ArtifactError(f"{name} cannot be loaded canonically: {exc}") from exc
    return loaded


def _validate_artifact_registry() -> None:
    """Require the checked-in Gate-1 registry to define this exact closure."""
    registry_path = Path(__file__).resolve().parents[2] / "schemas" / "gate1" / "registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArtifactError(f"cannot load Gate-1 artifact registry: {exc}") from exc
    registered = registry.get("artifacts") if isinstance(registry, Mapping) else None
    if (not isinstance(registered, list) or len(registered) != len(ARTIFACT_FILENAMES)
            or set(registered) != set(ARTIFACT_FILENAMES)):
        raise ArtifactError("Gate-1 schema registry does not declare the canonical ten-file closure")
    schemas = registry.get("schemas")
    if not isinstance(schemas, Mapping) or set(schemas) != set(ARTIFACT_FILENAMES):
        raise ArtifactError("Gate-1 schema registry mappings do not match the artifact closure")
    schema_root = registry_path.parent
    if any(not isinstance(name, str) or not (schema_root / name).is_file() for name in schemas.values()):
        raise ArtifactError("Gate-1 schema registry references a missing schema")


# --------------------------------------------------------------------------- #
# Deterministic identity and rebuildability
# --------------------------------------------------------------------------- #

#: Fields recording volatile runtime/resource observations. They are excluded
#: from identity digests: a wall-clock or resource measurement is an observation,
#: never a scientific identity input.
VOLATILE_FIELDS = frozenset({"wall_time_ms"})

EXACT_REBUILD_AVAILABLE = "EXACT_REBUILD_AVAILABLE"
EXACT_REBUILD_UNAVAILABLE = "EXACT_REBUILD_UNAVAILABLE"
NOT_A_RUN = "NOT_A_RUN"

TOMBSTONE_FIELDS = (
    "artifact_id",
    "artifact_type",
    "payload_digest",
    "producer_ref",
    "availability",
    "rebuildability",
)

TOMBSTONE_AVAILABILITY = "REMOVED_BY_RETENTION"


def _without_volatile(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _without_volatile(item) for key, item in value.items()
                if key not in VOLATILE_FIELDS}
    if isinstance(value, (list, tuple)):
        return [_without_volatile(item) for item in value]
    return value


def identity_digest_map(root: Path) -> dict[str, str]:
    """Content digest of every present artifact after volatile stripping."""
    source = Path(root)
    digests: dict[str, str] = {}
    for name in ARTIFACT_FILENAMES:
        path = source / name
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        if name in JSONL_ARTIFACTS:
            payload: Any = [json.loads(line) for line in raw.splitlines() if line.strip()]
        else:
            payload = json.loads(raw)
        digests[name] = sha256_digest(_without_volatile(payload))
    return digests


def _tombstones(source: Path) -> list[Mapping[str, Any]]:
    ledger_path = source / "failure_ledger.json"
    if not ledger_path.is_file():
        return []
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    records = ledger.get("tombstones") or []
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, Mapping)]


def rebuildability_status(root: Path) -> str:
    """Report whether exact rebuildability is claimable for this root.

    A complete ten-artifact root is exactly rebuildable. A root missing only
    tombstoned artifacts is refused: the retention record preserves provenance
    but the exact rebuild claim is unavailable.
    """
    source = Path(root)
    if not source.is_dir():
        return NOT_A_RUN
    present = {
        entry.name
        for entry in source.iterdir()
        if entry.is_file() and not entry.name.startswith(".")
    }
    missing = set(ARTIFACT_FILENAMES) - present
    if not missing:
        return EXACT_REBUILD_AVAILABLE

    records = _tombstones(source)
    tombstoned = {record.get("artifact_id") for record in records}
    refusal = any(
        record.get("rebuildability") == EXACT_REBUILD_UNAVAILABLE for record in records
    )
    if missing <= tombstoned and refusal:
        return EXACT_REBUILD_UNAVAILABLE
    return NOT_A_RUN
