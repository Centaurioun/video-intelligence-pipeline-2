"""Frozen Gate-1 public runtime types and authority constants.

Implemented exactly as specified by the approved v2 plan Section 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

BENCHMARK_STATUSES = frozenset({"PLANNED", "VALID", "INVALID_PROTOCOL", "PASS", "FAIL", "NOT_RUN"})

PROVIDER_STATUSES = frozenset({"SUCCESS", "PARTIAL", "FAILED", "UNSUPPORTED", "ESCALATED"})

EVIDENCE_CLASSES = frozenset(
    {"MEASURED", "MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED", "EDITORIAL_INFERENCE"}
)

INITIAL_OPERATION = "embedding"

#: Immutable canonical shared-contract binding for this Gate-1 epoch.
EXPECTED_CANONICAL_CONTRACT_BLOB = "c0b665d70b311dd98b7ff9f4f564b2d5750ed17b"

#: Owner-approved design specification commit.
SPEC_SHA = "d39fad8412b904d7d79cad8e15688bd4b348991f"

#: Synthetic records may never claim an observed backend.
SYNTHETIC_BACKEND = "NOT_OBSERVED"


@dataclass(frozen=True)
class ComparisonContract:
    comparison_id: str
    execution_mode: str
    question: str
    estimand: str
    changed_axis: str
    pinned_controls: Mapping[str, Any]
    arm_ids: tuple[str, str]
    operation: str
    primary_metric: Mapping[str, Any]
    decision_rule: Mapping[str, Any]
    validity_rules: Mapping[str, Any]
    dependency_refs: Mapping[str, Any]
    policy_eligibility: Mapping[str, str]
    tie_rule: str
    retry_policy: str
    resource_budget: Mapping[str, Any]
    owner_approval_ref: str


@dataclass(frozen=True)
class CapabilityDescriptor:
    record_id: str
    arm_id: str
    capability_revision: str
    provider_family: str
    operation: str
    input_mode: str
    requested_model: str
    resolved_backend: str
    runtime_revision: str
    config_digest: str
    space_id: str
    policy_decision_id: str
    window_profile_digest: str
    metric: str
    normalization: str


@dataclass(frozen=True)
class PolicyDecision:
    record_id: str
    policy_decision_id: str
    decision: str
    processing_boundary: str
    expires_at: str | None = None
    revoked: bool = False


@dataclass(frozen=True)
class BenchmarkEnvelope:
    record_id: str
    comparison_id: str
    run_id: str
    attempt_id: str
    arm_id: str
    input_refs: tuple[str, ...]
    consumed_coverage: Mapping[str, int]
    raw_response_artifact_ref: str | None
    absence_reason: str | None
    requested_model: str
    resolved_backend: str
    config_digest: str
    policy_decision_id: str
    request_ref: str | None
    judgment_version_refs: tuple[str, ...]
    resource_observations: Mapping[str, Any]
    validity_ref: str | None
    outcome_ref: str | None
    provider_status: str
    per_item_errors: tuple[str, ...]
    wall_time_ms: float | None


@dataclass(frozen=True)
class EmbeddingPayload:
    space_id: str
    representation_id: str
    query_id: str | None
    candidate_id: str | None
    kind: str
    vector: tuple[float, ...] | None
    failure_reason: str | None


@dataclass(frozen=True)
class EmbeddingRecord:
    envelope: BenchmarkEnvelope
    payload: EmbeddingPayload


@dataclass(frozen=True)
class RankedCandidate:
    record_id: str
    arm_id: str
    query_id: str
    candidate_id: str
    representation_id: str
    space_id: str
    score: float | None
    rank: int | None
    tie_key: tuple[Any, ...] | None
    coverage_status: str


@dataclass(frozen=True)
class Judgment:
    record_id: str
    query_id: str
    candidate_id: str
    relevant: bool
    reviewer_id: str
    synthetic: bool
    evidence_class: str


@dataclass(frozen=True)
class BenchmarkReport:
    comparison_id: str
    validity: str
    benchmark_status: str
    primary_metric_id: str
    primary_value: float | None
    arm_values: Mapping[str, float]
    coverage: Mapping[str, int]
    failure_class: str | None
    conclusion: str
