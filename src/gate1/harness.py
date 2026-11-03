"""Generated-only Gate-1 harness for exercising D01-D04 contracts.

This module has no runtime/provider/media execution path. Candidate vectors are
generated from the deterministic catalog defined below (moved in-tree from the
test fixtures so production code never imports ``tests``) and all artifact
identities are deterministic. It also hosts the synthetic-only three-arm
compatibility adapter (formerly ``gate1.three_arm_compat``): that adapter
performs SYNTHETIC PROTOCOL COMPATIBILITY ONLY and is not an operational
three-arm B00-B18 evaluation.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

from gate1.canonical_json import sha256_digest
from gate1.artifacts import (
    ARTIFACT_FILENAMES,
    comparison_contract_from_payload,
    embedding_record_payload,
    failure_ledger_payload,
    frozen_protocol_digest,
    derived_run_id,
    judgment_payload,
    ranked_candidate_payload,
    write_artifact_root,
    contract_digest,
    descriptor_digest,
    policy_digest,
)
from gate1.contracts.types import (
    BenchmarkEnvelope,
    EmbeddingPayload,
    EmbeddingRecord,
    Judgment,
    RankedCandidate,
)
from gate1.contracts.validator import ContractError, validate_comparison
from gate1.evaluation import evaluate_comparison
from gate1.ranking import rank_arm
from gate1.verify import verify_artifact_set, verify_path


# --- Synthetic three-arm compatibility adapter (S-09 in-tree move) ---------
#
# SYNTHETIC PROTOCOL COMPATIBILITY ONLY. This adapter orchestrates three
# pairwise comparisons through the accepted v1 comparison contract and
# evaluation code. It does not implement operational three-arm B00-B18
# evaluation and must never be read as model evidence, benchmark readiness,
# a winner, or a Gate-1 promotion.

CHARTER_ARMS = ("VIP_V1_BASE", "VIP_V2_BASE", "VIP_V2_SO400M")
CHARTER_PAIRS = ((CHARTER_ARMS[0], CHARTER_ARMS[1]),
                 (CHARTER_ARMS[0], CHARTER_ARMS[2]),
                 (CHARTER_ARMS[1], CHARTER_ARMS[2]))
EVIDENCE_STATUS = "SYNTHETIC_NOT_MODEL_EVIDENCE"
JUDGMENT_EVIDENCE_CLASS = "NOT_APPLICABLE_SYNTHETIC"
EVALUATION_SCOPE = "SYNTHETIC_PROTOCOL_COMPATIBILITY_ONLY"
OPERATIONAL_EVALUATION_STATUS = "NOT_IMPLEMENTED"
BENCHMARK_READINESS = "NOT_BENCHMARK_READY"
LIMITATIONS = (
    "SYNTHETIC_PROTOCOL_COMPATIBILITY_ONLY",
    "NOT_OPERATIONAL_THREE_ARM_B00_B18_EVALUATION",
    "NO_MODEL_EVIDENCE",
    "NO_WINNER_SELECTION",
    "NO_GATE1_PROMOTION",
)
# The third charter arm is a synthetic projection/clone of the second source
# arm; every arm states where it was derived from.
ARM_DERIVATIONS = (
    {"arm_id": CHARTER_ARMS[0], "derived_from_arm_id": "arm_a", "synthetic_projection": False},
    {"arm_id": CHARTER_ARMS[1], "derived_from_arm_id": "arm_b", "synthetic_projection": False},
    {"arm_id": CHARTER_ARMS[2], "derived_from_arm_id": "arm_b", "synthetic_projection": True},
)
_ARM_DERIVATION_FIELDS = {"arm_id", "derived_from_arm_id", "synthetic_projection"}
_B07_EXPECTED_REASONS = {
    "recall_at_5": "POOLED_GROUND_TRUTH",
    "ndcg_at_10": "METRIC_NOT_IMPLEMENTED",
}
_CODE_SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class CompatibilityError(ValueError):
    """Raised when a three-arm synthetic comparison is not pair-compatible."""


def _sequence(value: Any, name: str) -> Sequence:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise CompatibilityError(f"{name} must be a sequence")
    return value


def _validated_arm_derivations(arm_derivations: Any) -> list[dict[str, Any]]:
    """Validate the per-arm synthetic-derivation record (S-06)."""
    rows = _sequence(arm_derivations, "arm_derivations")
    if len(rows) != len(CHARTER_ARMS):
        raise CompatibilityError("arm_derivations must cover exactly the three charter arms")
    validated: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping) or set(row) != _ARM_DERIVATION_FIELDS:
            raise CompatibilityError("arm derivation records must have exactly the frozen fields")
        if row.get("arm_id") != CHARTER_ARMS[index]:
            raise CompatibilityError("arm derivation order must match the frozen charter order")
        derived_from = row.get("derived_from_arm_id")
        if not isinstance(derived_from, str) or not derived_from:
            raise CompatibilityError("arm derived_from_arm_id must be a non-empty string")
        projection = row.get("synthetic_projection")
        if not isinstance(projection, bool):
            raise CompatibilityError("synthetic_projection must be a boolean")
        if projection is not (index == len(CHARTER_ARMS) - 1):
            raise CompatibilityError(
                "only the third charter arm is a synthetic projection of its source arm"
            )
        validated.append({
            "arm_id": row["arm_id"],
            "derived_from_arm_id": derived_from,
            "synthetic_projection": projection,
        })
    return validated


def _validated_metric_states(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Require the explicit, metric-id-keyed B07 NOT_COMPUTABLE markers."""
    metric_states = contract.get("b07_metric_states")
    if not isinstance(metric_states, Sequence) or isinstance(metric_states, (str, bytes)):
        raise CompatibilityError("b07_metric_states must be a required sequence")
    if len(metric_states) != len(_B07_EXPECTED_REASONS):
        raise CompatibilityError("b07_metric_states must cover every B07 metric exactly once")
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for state in metric_states:
        if (not isinstance(state, Mapping)
                or set(state) != {"metric_id", "status", "reason"}):
            raise CompatibilityError("B07 metric states must preserve explicit NOT_COMPUTABLE markers")
        metric_id = state.get("metric_id")
        if metric_id not in _B07_EXPECTED_REASONS or metric_id in seen:
            raise CompatibilityError("B07 metric_id must be a unique implemented-gap metric id")
        if state.get("status") != "NOT_COMPUTABLE":
            raise CompatibilityError("B07 metric states must be NOT_COMPUTABLE")
        if state.get("reason") != _B07_EXPECTED_REASONS[metric_id]:
            raise CompatibilityError(f"B07 reason for {metric_id} must name the real gap")
        seen.add(metric_id)
        validated.append({
            "metric_id": metric_id,
            "status": "NOT_COMPUTABLE",
            "reason": _B07_EXPECTED_REASONS[metric_id],
        })
    return validated


def _report_payload(report: Any) -> dict[str, Any]:
    """Split v1 validity (protocol truth) from benchmark outcome (S-13)."""
    if report.validity == "VALID":
        if report.benchmark_status not in {"PASS", "FAIL"}:
            raise CompatibilityError("a valid v1 comparison must yield a PASS/FAIL outcome")
        outcome = report.benchmark_status
    elif report.validity == "INVALID_PROTOCOL":
        if report.benchmark_status != "INVALID_PROTOCOL":
            raise CompatibilityError("an invalid protocol must not carry a benchmark outcome")
        outcome = "NOT_EVALUATED"
    else:
        raise CompatibilityError(f"unknown v1 validity state: {report.validity}")
    return {
        "comparison_id": report.comparison_id,
        "validity": report.validity,
        "benchmark_status": report.benchmark_status,
        "outcome": outcome,
        "primary_metric_id": report.primary_metric_id,
        "primary_value": report.primary_value,
        "arm_values": dict(report.arm_values),
        "coverage": dict(report.coverage),
        "failure_class": report.failure_class,
        "conclusion": report.conclusion,
    }


def build_three_arm_compat_report(
    contract: Mapping[str, Any],
    descriptors: Sequence[Mapping[str, Any]],
    policies: Sequence[Mapping[str, Any]],
    run_manifest: Mapping[str, Any],
    rankings_by_arm: Mapping[str, Sequence[RankedCandidate]],
    judgments: Sequence[Any],
    failures: Sequence[Mapping[str, Any]],
    *,
    query_ids: Sequence[str],
    fixture_id: str,
    code_sha: str,
    arm_derivations: Sequence[Mapping[str, Any]],
    synthetic_fault: str = "NONE",
    protocol_validity: str = "VALID",
) -> dict[str, Any]:
    """Validate the three-arm envelope and evaluate its three charter pairs.

    ``contract.pair_contract_template`` is an existing v1 two-arm contract.
    Its pair-specific IDs and policy map are projected per pair; validation
    and metric evaluation remain owned by the existing v1 implementations.

    The report is explicitly SYNTHETIC_NOT_MODEL_EVIDENCE: it records its
    fixture, producing-code digest, compatibility-contract digest, and the
    synthetic derivation of every arm.
    """
    if not isinstance(contract, Mapping):
        raise CompatibilityError("contract must be an object")
    if contract.get("schema_version") != 2:
        raise CompatibilityError("compatibility schema_version must be 2")
    if contract.get("execution_mode") != "SYNTHETIC":
        raise CompatibilityError("three-arm compatibility is synthetic-only")
    declared_arms = contract.get("arm_ids")
    if (not isinstance(declared_arms, Sequence)
            or isinstance(declared_arms, (str, bytes))
            or tuple(declared_arms) != CHARTER_ARMS):
        raise CompatibilityError("arm_ids must match the frozen B00 charter order")
    if not isinstance(fixture_id, str) or not fixture_id:
        raise CompatibilityError("fixture_id must be a non-empty generated case id")
    if not isinstance(code_sha, str) or not _CODE_SHA_PATTERN.match(code_sha):
        raise CompatibilityError("code_sha must be a deterministic lowercase sha256 digest")
    if protocol_validity not in {"VALID", "INVALID_PROTOCOL"}:
        raise CompatibilityError("protocol_validity must be VALID or INVALID_PROTOCOL")
    derivation_rows = _validated_arm_derivations(arm_derivations)

    descriptors = _sequence(descriptors, "descriptors")
    policies = _sequence(policies, "policies")
    failures = _sequence(failures, "failures")
    judgments = _sequence(judgments, "judgments")
    query_ids = _sequence(query_ids, "query_ids")
    if len(descriptors) != len(CHARTER_ARMS):
        raise CompatibilityError("exactly three arm descriptors are required")
    if any(not isinstance(row, Mapping) for row in descriptors):
        raise CompatibilityError("arm descriptors must be objects")
    if any(not isinstance(policy, Mapping) for policy in policies):
        raise CompatibilityError("policy declarations must be objects")
    if any(not isinstance(failure, Mapping) for failure in failures):
        raise CompatibilityError("failure declarations must be objects")
    if any(not isinstance(judgment, Judgment) for judgment in judgments):
        raise CompatibilityError("judgments must use existing Gate-1 Judgment records")
    if any(not judgment.synthetic or judgment.evidence_class != JUDGMENT_EVIDENCE_CLASS
           for judgment in judgments):
        raise CompatibilityError(
            "synthetic judgments must declare synthetic NOT_APPLICABLE_SYNTHETIC evidence"
        )
    descriptor_arm_ids = [row.get("arm_id") for row in descriptors]
    if any(not isinstance(arm_id, str) or not arm_id for arm_id in descriptor_arm_ids):
        raise CompatibilityError("descriptor arm_id values must be non-empty strings")
    descriptor_by_arm = {row["arm_id"]: row for row in descriptors}
    if len(descriptor_by_arm) != len(CHARTER_ARMS) or set(descriptor_by_arm) != set(CHARTER_ARMS):
        raise CompatibilityError("descriptors must uniquely match the three charter arms")
    spaces = [descriptor_by_arm[arm].get("space_id") for arm in CHARTER_ARMS]
    if any(not isinstance(space, str) or not space for space in spaces):
        raise CompatibilityError("each arm requires a non-empty semantic space")
    if len(set(spaces)) != len(CHARTER_ARMS):
        raise CompatibilityError("the three arms must use distinct semantic spaces")

    if not isinstance(rankings_by_arm, Mapping) or set(rankings_by_arm) != set(CHARTER_ARMS):
        raise CompatibilityError("rankings must be present for exactly the three charter arms")
    frozen_queries = tuple(query_ids)
    if not frozen_queries or any(not isinstance(q, str) or not q for q in frozen_queries):
        raise CompatibilityError("query_ids must contain non-empty frozen query IDs")
    if len(set(frozen_queries)) != len(frozen_queries):
        raise CompatibilityError("query_ids must be unique")

    observed_queries: dict[str, set[str]] = {}
    for arm in CHARTER_ARMS:
        rows = _sequence(rankings_by_arm[arm], f"rankings_by_arm[{arm}]")
        observed_queries[arm] = set()
        for row in rows:
            if not isinstance(row, RankedCandidate):
                raise CompatibilityError("rankings must use existing RankedCandidate records")
            if row.arm_id != arm or row.space_id != descriptor_by_arm[arm].get("space_id"):
                raise CompatibilityError(f"ranking row identity/space mismatch for {arm}")
            if not isinstance(row.query_id, str) or not row.query_id:
                raise CompatibilityError("ranking query_id values must be non-empty strings")
            observed_queries[arm].add(row.query_id)
        if observed_queries[arm] != set(frozen_queries):
            raise CompatibilityError(f"ranked query coverage does not match frozen queries for {arm}")

    template = contract.get("pair_contract_template")
    if not isinstance(template, Mapping):
        raise CompatibilityError("pair_contract_template must be a v1 comparison contract")
    base_comparison_id = template.get("comparison_id")
    eligibility = template.get("policy_eligibility")
    if not isinstance(base_comparison_id, str) or not base_comparison_id:
        raise CompatibilityError("pair contract requires comparison_id")
    if not isinstance(eligibility, Mapping):
        raise CompatibilityError("pair contract requires arm policy eligibility")
    if not isinstance(run_manifest, Mapping):
        raise CompatibilityError("run_manifest must be an object")

    manifest_inputs = run_manifest.get("candidate_production_inputs")
    if not isinstance(manifest_inputs, Sequence) or isinstance(manifest_inputs, (str, bytes)):
        raise CompatibilityError("run manifest must declare typed candidate production inputs")
    if any(not isinstance(item, Mapping) for item in manifest_inputs):
        raise CompatibilityError("candidate production declarations must be objects")

    metric_states = _validated_metric_states(contract)
    pair_reports: list[dict[str, Any]] = []
    for pair_index, pair in enumerate(CHARTER_PAIRS):
        pair_contract = deepcopy(dict(template))
        pair_contract.pop("b07_metric_states", None)
        pair_contract["comparison_id"] = f"{base_comparison_id}:pair-{pair_index + 1}"
        pair_contract["arm_ids"] = list(pair)
        pair_contract["policy_eligibility"] = {arm: eligibility[arm] for arm in pair
                                                if arm in eligibility}
        if set(pair_contract["policy_eligibility"]) != set(pair):
            raise CompatibilityError(f"pair policy eligibility is missing an arm for {pair}")
        pair_descriptors = [descriptor_by_arm[arm] for arm in pair]
        pair_policies = [policy for policy in policies
                         if policy.get("policy_decision_id") in pair_contract["policy_eligibility"].values()]
        pair_manifest = deepcopy(dict(run_manifest))
        pair_manifest["comparison_id"] = pair_contract["comparison_id"]
        pair_manifest["candidate_production_inputs"] = [
            item for item in manifest_inputs
            if item.get("kind") != "representation" or item.get("arm_id") in pair
        ]
        try:
            validate_comparison(pair_contract, pair_descriptors, pair_policies, pair_manifest)
            pair_model = comparison_contract_from_payload(pair_contract)
            pair_report = evaluate_comparison(
                pair_model,
                {arm: rankings_by_arm[arm] for arm in pair},
                judgments,
                failures,
                query_ids=frozen_queries,
                protocol_validity=protocol_validity,
                synthetic_fault=synthetic_fault,
            )
        except (ContractError, ValueError, KeyError, TypeError) as exc:
            raise CompatibilityError(f"pair {pair} failed current v1 validation/evaluation: {exc}") from exc
        pair_reports.append({"arm_ids": list(pair), **_report_payload(pair_report)})

    return {
        "schema_version": 2,
        "execution_mode": "SYNTHETIC",
        "fixture_id": fixture_id,
        "code_sha": code_sha,
        "contract_digest": contract_digest(contract),
        "evidence_status": EVIDENCE_STATUS,
        "judgment_evidence_class": JUDGMENT_EVIDENCE_CLASS,
        "evaluation_scope": EVALUATION_SCOPE,
        "operational_evaluation_status": OPERATIONAL_EVALUATION_STATUS,
        "compatibility_status": "COMPATIBLE",
        "benchmark_readiness": BENCHMARK_READINESS,
        "pairwise_evaluations": pair_reports,
        "b07_metric_states": metric_states,
        "arm_derivations": derivation_rows,
        "winner_status": "NOT_EVALUATED",
        "limitations": list(LIMITATIONS),
    }

# --- Deterministic generated-case catalog (S-09 in-tree move) --------------

CASE_IDS = (
    "positive_one_axis",
    "tie_no_superiority",
    "partial_coverage",
    "quality_failure",
    "resource_failure",
    "invalid_multi_axis",
    "invalid_pinned_control",
    "source_overlap",
    "label_leakage_declaration",
    "incompatible_space",
    "policy_ineligible",
    "fabricated_backend",
    "frozen_protocol_mutation",
)

_HEX_A = "a" * 64
_HEX_B = "b" * 64
_HEX_C = "c" * 64


def _baseline(case_id: str) -> dict[str, Any]:
    """Return a fresh valid synthetic comparison before case-specific edits."""
    arms = ["arm_a", "arm_b"]
    controls = {
        "operation": "embedding",
        "input_mode": "text",
        "window_profile_digest": _HEX_A,
        "metric": "cosine",
        "normalization": "l2",
        "provider_family": "local_fake",
    }
    descriptors = [
        {
            "record_id": "descriptor_a", "arm_id": arms[0],
            "capability_revision": "fake-capability-v1", "provider_family": "local_fake",
            "operation": "embedding", "input_mode": "text", "requested_model": "fake-a",
            "resolved_backend": "NOT_OBSERVED", "runtime_revision": "NOT_OBSERVED",
            "config_digest": _HEX_B, "space_id": "space_a", "policy_decision_id": "policy_a",
            "window_profile_digest": _HEX_A, "metric": "cosine", "normalization": "l2",
        },
        {
            "record_id": "descriptor_b", "arm_id": arms[1],
            "capability_revision": "fake-capability-v1", "provider_family": "local_fake",
            "operation": "embedding", "input_mode": "text", "requested_model": "fake-b",
            "resolved_backend": "NOT_OBSERVED", "runtime_revision": "NOT_OBSERVED",
            "config_digest": _HEX_B, "space_id": "space_b", "policy_decision_id": "policy_b",
            "window_profile_digest": _HEX_A, "metric": "cosine", "normalization": "l2",
        },
    ]
    contract = {
        "comparison_id": f"cmp_{case_id}", "execution_mode": "SYNTHETIC",
        "question": "Does the declared representation change retrieval?",
        "estimand": "paired macro hit-at-1 difference", "changed_axis": "space_id",
        "pinned_controls": controls, "arm_ids": arms, "operation": "embedding",
        "primary_metric": {"metric_id": "macro_hit_at_1", "k": 1, "min_delta": 0.25,
                           "require_complete_coverage": False},
        "decision_rule": {"minimum_delta": 0.25}, "validity_rules": {"fail_closed": True},
        "dependency_refs": {"fixture": "generated-only"},
        "policy_eligibility": {"arm_a": "policy_a", "arm_b": "policy_b"},
        "tie_rule": "stable_candidate_id_utf8", "retry_policy": "no_retry",
        "resource_budget": {"max_attempts": 1}, "owner_approval_ref": "synthetic-fixture-only",
    }
    policies = [
        {"record_id": "policy-record-a", "policy_decision_id": "policy_a", "decision": "ALLOW",
         "processing_boundary": "LOCAL_SYNTHETIC", "expires_at": None, "revoked": False},
        {"record_id": "policy-record-b", "policy_decision_id": "policy_b", "decision": "ALLOW",
         "processing_boundary": "LOCAL_SYNTHETIC", "expires_at": None, "revoked": False},
    ]
    run = {
        "schema_version": "gate1.v1", "run_id": f"run_{case_id}",
        "comparison_id": f"cmp_{case_id}", "execution_mode": "SYNTHETIC",
        "spec_sha": "d39fad8412b904d7d79cad8e15688bd4b348991f",
        "execution_authority_sha": "synthetic-only", "canonical_contract_blob": _HEX_C,
        "source_partitions": {"development": ["generated-dev-1"],
                              "evaluation": ["generated-eval-1"]},
        "candidate_production_inputs": [
            {"kind": "query", "input_id": "query-1"},
            {"kind": "candidate", "input_id": "candidate-1"},
            {"kind": "representation", "input_id": "rep-a", "arm_id": "arm_a", "space_id": "space_a"},
            {"kind": "representation", "input_id": "rep-b", "arm_id": "arm_b", "space_id": "space_b"},
        ],
        "provenance": {"run_id": f"run_{case_id}", "attempt_id": "attempt-1", "config_digest": _HEX_B},
        "backend_observation": "NOT_OBSERVED", "contract_digest": "", "descriptor_digest": "",
        "policy_digest": "", "frozen_protocol_digest": "", "synthetic_fault": "NONE", "status": "PLANNED",
    }
    # Candidate production is fixed before the independent judgments below.
    vectors = {
        "arm_a": {"query-1": [1.0, 0.0], "candidate-1": [0.0, 1.0], "candidate-2": [1.0, 0.0]},
        "arm_b": {"query-1": [1.0, 0.0], "candidate-1": [1.0, 0.0], "candidate-2": [0.0, 1.0]},
    }
    judgments = [{"record_id": "judgment-1", "query_id": "query-1", "candidate_id": "candidate-1",
                  "relevant": True, "reviewer_id": "synthetic-fixture", "synthetic": True,
                  "evidence_class": "EDITORIAL_INFERENCE"}]
    return {
        "case_id": case_id,
        "comparison": contract,
        "descriptors": descriptors,
        "policies": policies,
        "run_manifest": run,
        "production": {"query_ids": ["query-1"], "candidate_ids": ["candidate-1", "candidate-2"],
                        "vectors": vectors},
        "judgments": judgments,
        "failures": [],
        "synthetic_fault": "NONE",
        "frozen_artifact_mutation": None,
        "expected": {"protocol_validity": "VALID", "benchmark_status": "PASS",
                     "failure_class": None, "primary_value": 1.0,
                     "arm_values": {"arm_a": 0.0, "arm_b": 1.0},
                     "coverage": {"arm_a::SELECTED": 2, "arm_a::FAILED": 0, "arm_a::OMITTED": 0,
                                  "arm_a::QUARANTINED": 0, "arm_b::SELECTED": 2,
                                  "arm_b::FAILED": 0, "arm_b::OMITTED": 0, "arm_b::QUARANTINED": 0}},
    }


def _expected_ranked_candidates(*, partial: bool = False,
                                arms_match: bool = False) -> dict[str, dict[str, dict[str, Any]]]:
    """Static expected ranking projection, independent of harness execution."""
    arm_a = {
        "candidate-1": {"score": 0.0, "rank": 2, "tie_key": [-0.0, "candidate-1"], "coverage_status": "SELECTED"},
        "candidate-2": {"score": 1.0, "rank": 1, "tie_key": [-1.0, "candidate-2"], "coverage_status": "SELECTED"},
    }
    arm_b = deepcopy(arm_a) if arms_match else {
        "candidate-1": {"score": 1.0, "rank": 1, "tie_key": [-1.0, "candidate-1"], "coverage_status": "SELECTED"},
        "candidate-2": {"score": 0.0, "rank": 2, "tie_key": [-0.0, "candidate-2"], "coverage_status": "SELECTED"},
    }
    if partial:
        arm_b["candidate-2"] = {"score": None, "rank": None, "tie_key": None, "coverage_status": "OMITTED"}
    return {"arm_a": arm_a, "arm_b": arm_b}


def _expected_benchmark_report(case_id: str, *, status: str, primary_value: float,
                               arm_values: dict[str, float], coverage: dict[str, int],
                               failure_class: str | None) -> dict[str, Any]:
    """Frozen report projection from fixture declarations and judgments."""
    return {
        "comparison_id": f"cmp_{case_id}",
        "validity": "VALID",
        "benchmark_status": status,
        "primary_metric_id": "macro_hit_at_1",
        "primary_value": primary_value,
        "arm_values": deepcopy(arm_values),
        "coverage": deepcopy(coverage),
        "failure_class": failure_class,
        "conclusion": "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM",
    }


def _build_cases() -> dict[str, dict[str, Any]]:
    cases = {case_id: _baseline(case_id) for case_id in CASE_IDS}

    case = cases["tie_no_superiority"]
    case["production"]["vectors"]["arm_b"] = deepcopy(case["production"]["vectors"]["arm_a"])
    case["expected"].update(benchmark_status="FAIL", failure_class="QUALITY", primary_value=0.0,
                            arm_values={"arm_a": 0.0, "arm_b": 0.0},
                            conclusion="SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM")

    # One valid omitted candidate; no provider failure state or item error is invented.
    case = cases["partial_coverage"]
    case["comparison"]["primary_metric"]["require_complete_coverage"] = True
    case["production"]["vectors"]["arm_b"].pop("candidate-2")
    case["production"]["omitted"] = [{"arm_id": "arm_b", "candidate_id": "candidate-2",
                                       "absence_reason": "FIXTURE_OMISSION", "provider_status": "SUCCESS",
                                       "per_item_errors": [], "failure_reason": None}]
    case["expected"].update(benchmark_status="FAIL", failure_class="COVERAGE_INCOMPLETE",
                            conclusion="SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM",
                            coverage={"arm_a::SELECTED": 2, "arm_a::FAILED": 0, "arm_a::OMITTED": 0,
                                      "arm_a::QUARANTINED": 0, "arm_b::SELECTED": 1,
                                      "arm_b::FAILED": 0, "arm_b::OMITTED": 1,
                                      "arm_b::QUARANTINED": 0},
                            omission_accounting={"arm_b": 1, "candidate_ids": ["candidate-2"],
                                                "provider_status": "SUCCESS", "per_item_errors": [],
                                                "failure_reason": None})

    case = cases["quality_failure"]
    case["production"]["vectors"]["arm_b"] = deepcopy(case["production"]["vectors"]["arm_a"])
    case["expected"].update(benchmark_status="FAIL", failure_class="QUALITY", primary_value=0.0,
                            arm_values={"arm_a": 0.0, "arm_b": 0.0},
                            conclusion="SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM")

    case = cases["resource_failure"]
    case["synthetic_fault"] = "RESOURCE_OPERABILITY"
    case["failures"] = [{"event_type": "RESOURCE_OPERABILITY", "reason": "synthetic resource fault"}]
    case["expected"].update(benchmark_status="FAIL", failure_class="RESOURCE_OPERABILITY",
                            conclusion="SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM")

    # Explicit oracles cover every valid executable case. Their contents are
    # fixed from these synthetic declarations, never sampled from harness output.
    report_oracles = {
        "positive_one_axis": ("PASS", 1.0, {"arm_a": 0.0, "arm_b": 1.0}, {"arm_a": 2, "arm_b": 2}, None),
        "tie_no_superiority": ("FAIL", 0.0, {"arm_a": 0.0, "arm_b": 0.0}, {"arm_a": 2, "arm_b": 2}, "QUALITY"),
        "partial_coverage": ("FAIL", 1.0, {"arm_a": 0.0, "arm_b": 1.0}, {"arm_a": 2, "arm_b": 1}, "COVERAGE_INCOMPLETE"),
        "quality_failure": ("FAIL", 0.0, {"arm_a": 0.0, "arm_b": 0.0}, {"arm_a": 2, "arm_b": 2}, "QUALITY"),
        "resource_failure": ("FAIL", 1.0, {"arm_a": 0.0, "arm_b": 1.0}, {"arm_a": 2, "arm_b": 2}, "RESOURCE_OPERABILITY"),
    }
    for case_id, (status, value, arm_values, selected_counts, failure_class) in report_oracles.items():
        expected = cases[case_id]["expected"]
        expected["conclusion"] = "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"
        expected["ranked_candidates"] = _expected_ranked_candidates(
            partial=case_id == "partial_coverage",
            arms_match=case_id in {"tie_no_superiority", "quality_failure"},
        )
        expected["benchmark_report"] = _expected_benchmark_report(
            case_id,
            status=status,
            primary_value=value,
            arm_values=arm_values,
            coverage=selected_counts,
            failure_class=failure_class,
        )

    case = cases["invalid_multi_axis"]
    case["descriptors"][1]["provider_family"] = "other_fake"
    case["expected"].update(protocol_validity="INVALID_PROTOCOL", benchmark_status="INVALID_PROTOCOL",
                            failure_class=None, primary_value=None, arm_values={},
                            conclusion="COMPARISON_INVALID_NO_OUTCOME_CLAIM")

    case = cases["invalid_pinned_control"]
    case["descriptors"][1]["metric"] = "dot"
    case["expected"].update(protocol_validity="INVALID_PROTOCOL", benchmark_status="INVALID_PROTOCOL",
                            failure_class=None, primary_value=None, arm_values={},
                            conclusion="COMPARISON_INVALID_NO_OUTCOME_CLAIM")

    case = cases["source_overlap"]
    case["run_manifest"]["source_partitions"]["evaluation"] = ["generated-dev-1"]
    case["expected"].update(protocol_validity="INVALID_PROTOCOL", benchmark_status="INVALID_PROTOCOL",
                            failure_class=None, primary_value=None, arm_values={},
                            conclusion="COMPARISON_INVALID_NO_OUTCOME_CLAIM")

    case = cases["label_leakage_declaration"]
    case["run_manifest"]["candidate_production_inputs"].append(
        {"kind": "judgment", "input_id": "judgment-1"})
    case["expected"].update(protocol_validity="INVALID_PROTOCOL", benchmark_status="INVALID_PROTOCOL",
                            failure_class=None, primary_value=None, arm_values={},
                            conclusion="COMPARISON_INVALID_NO_OUTCOME_CLAIM")

    case = cases["incompatible_space"]
    case["run_manifest"]["candidate_production_inputs"][2]["space_id"] = "space_b"
    case["expected"].update(protocol_validity="INVALID_PROTOCOL", benchmark_status="INVALID_PROTOCOL",
                            failure_class=None, primary_value=None, arm_values={},
                            conclusion="COMPARISON_INVALID_NO_OUTCOME_CLAIM")

    case = cases["policy_ineligible"]
    case["policies"][1]["decision"] = "DENY"
    case["expected"].update(protocol_validity="INVALID_PROTOCOL", benchmark_status="INVALID_PROTOCOL",
                            failure_class=None, primary_value=None, arm_values={},
                            conclusion="COMPARISON_INVALID_NO_OUTCOME_CLAIM")

    case = cases["fabricated_backend"]
    case["descriptors"][1]["resolved_backend"] = "fake-runtime-claimed-observed"
    case["expected"].update(protocol_validity="INVALID_PROTOCOL", benchmark_status="INVALID_PROTOCOL",
                            failure_class=None, primary_value=None, arm_values={},
                            conclusion="COMPARISON_INVALID_NO_OUTCOME_CLAIM")

    case = cases["frozen_protocol_mutation"]
    case["frozen_artifact_mutation"] = {"artifact": "comparison_contract.json",
                                        "path": "changed_axis", "value": "provider_family"}
    case["expected"].update(protocol_validity="VALID", benchmark_status="REJECT_MUTATED_ARTIFACT",
                            failure_class=None, mutation_rejected=True,
                            conclusion="FROZEN_PROTOCOL_MUTATION_REJECTED")
    return cases


_CASES = _build_cases()


def get_case(case_id: str) -> dict[str, Any]:
    """Return an isolated deep copy of one fixture case."""
    try:
        return deepcopy(_CASES[case_id])
    except KeyError:
        raise KeyError(f"unknown generated Gate-1 case: {case_id}") from None


def all_cases() -> dict[str, dict[str, Any]]:
    """Return all catalog entries as an isolated deep copy."""
    return deepcopy(_CASES)


SPEC_SHA = "d39fad8412b904d7d79cad8e15688bd4b348991f"
EXECUTION_AUTHORITY_SHA = "1bdf57b423ae84034184b8c4d2c441616c78301f"
CANONICAL_CONTRACT_BLOB = "c0b665d70b311dd98b7ff9f4f564b2d5750ed17b"
CONFIG_DIGEST = "b" * 64
_ALLOWED_CASES = frozenset({
    "positive_one_axis", "tie_no_superiority", "partial_coverage",
    "quality_failure", "resource_failure",
})
THREE_ARM_REPORT_FILENAME = "three_arm_compat_report.json"
THREE_ARM_RECEIPT_FILENAME = "three_arm_compat_receipt.json"
B07_NOT_COMPUTABLE = (
    {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE", "reason": "POOLED_GROUND_TRUTH"},
    {"metric_id": "ndcg_at_10", "status": "NOT_COMPUTABLE", "reason": "METRIC_NOT_IMPLEMENTED"},
)
# Deterministic producing-code identity (S-12): SHA-256 over canonical JSON of
# sorted [relative POSIX path, SHA-256 hex of module bytes] pairs for the
# Gate-1 modules that produce the compatibility report. It is derived only
# from checked-in module bytes/config, never from wall-clock or environment.
_PRODUCING_MODULE_PATHS = (
    "__init__.py",
    "artifacts.py",
    "canonical_json.py",
    "contracts/__init__.py",
    "contracts/types.py",
    "contracts/validator.py",
    "evaluation.py",
    "harness.py",
    "ranking.py",
    "verify.py",
)


def gate1_code_sha() -> str:
    """Return the deterministic sha256 identity of the producing Gate-1 code.

    Digest method: sha256 over the canonical JSON encoding (sorted keys,
    compact separators, UTF-8) of a path-sorted list of
    ``[relative_path, sha256_hex(file_bytes)]`` pairs covering every module in
    ``_PRODUCING_MODULE_PATHS``. Only checked-out tracked module/config bytes
    feed the digest - never wall-clock time, host identity, environment, or
    run identifiers - so the same source tree always yields the same
    ``code_sha``. Any edit to a producing module changes the value.
    """
    package_root = Path(__file__).resolve().parent
    entries = []
    for relative_path in _PRODUCING_MODULE_PATHS:
        path = package_root / relative_path
        entries.append([
            relative_path,
            hashlib.sha256(path.read_bytes()).hexdigest(),
        ])
    entries.sort(key=lambda item: item[0])
    return sha256_digest(entries)


def _json_copy(value: Any) -> Any:
    """Return a detached JSON-compatible value without fixture aliases."""
    return json.loads(json.dumps(value, sort_keys=True, allow_nan=False))


def _descriptor_rows(case: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _json_copy(case["descriptors"])
    # Case declarations carry identity values; the execution contract uses
    # these stable generated identities and the fixture's axis values.
    return rows


def _valid_declarations(case: dict[str, Any], case_id: str) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, list[dict[str, Any]]]
]:
    """Make validated synthetic declarations and deterministic vector records."""
    contract = _json_copy(case["comparison"])
    descriptors = _descriptor_rows(case)
    policies = _json_copy(case["policies"])
    production = _json_copy(case["production"])
    arms = list(contract["arm_ids"])
    for policy in policies:
        policy["processing_boundary"] = "SYNTHETIC_TEST_ONLY"

    # A generated comparison changes only its declared representation space;
    # model identity is held constant even though these fake descriptors are
    # never dispatched to a runtime.
    for descriptor in descriptors:
        descriptor["requested_model"] = "fake-generated"
    contract["pinned_controls"]["requested_model"] = "fake-generated"
    contract["decision_rule"] = {
        "comparison": "difference",
        "threshold": float(contract["primary_metric"]["min_delta"]),
        "direction": "higher_is_better",
    }
    contract["dependency_refs"] = {
        "spec_sha": SPEC_SHA,
        "canonical_contract_blob": CANONICAL_CONTRACT_BLOB,
    }
    contract["validity_rules"] = {
        "require_complete_coverage": bool(
            contract["primary_metric"].get("require_complete_coverage", False)
        )
    }

    # The partial case is deliberately a valid negative coverage result.
    if case_id == "partial_coverage":
        contract["primary_metric"]["require_complete_coverage"] = True
        contract["validity_rules"]["require_complete_coverage"] = True

    # Derive the complete, label-free production declaration from the generated
    # vector universe. Labels are intentionally not accessed in this function.
    query_ids = list(production["query_ids"])
    candidate_ids = sorted({
        candidate_id
        for per_arm in production["vectors"].values()
        for candidate_id in per_arm
        if candidate_id not in query_ids
    })
    declarations: list[dict[str, Any]] = [
        *({"kind": "query", "input_id": ident} for ident in sorted(query_ids)),
        *({"kind": "candidate", "input_id": ident} for ident in candidate_ids),
    ]
    for arm in arms:
        descriptor = next(row for row in descriptors if row["arm_id"] == arm)
        per_arm = production["vectors"][arm]
        for query_id in sorted(query_ids):
            repr_id = f"repr-{arm}-{query_id}"
            declarations.append({"kind": "representation", "input_id": repr_id,
                                 "arm_id": arm, "space_id": descriptor["space_id"]})
        for candidate_id in candidate_ids:
            repr_id = f"repr-{arm}-{candidate_id}"
            declarations.append({"kind": "representation", "input_id": repr_id,
                                 "arm_id": arm, "space_id": descriptor["space_id"]})
    declarations.sort(key=lambda item: (item["kind"], item["input_id"], item.get("arm_id", "")))

    synthetic_fault = case["synthetic_fault"]
    manifest = {
        "schema_version": "gate1.run.v1",
        "run_id": "", "comparison_id": contract["comparison_id"],
        "execution_mode": "SYNTHETIC", "spec_sha": SPEC_SHA,
        "execution_authority_sha": EXECUTION_AUTHORITY_SHA,
        "canonical_contract_blob": CANONICAL_CONTRACT_BLOB,
        "source_partitions": {"development": ["generated-dev-1"],
                              "evaluation": ["generated-eval-1"]},
        "candidate_production_inputs": declarations,
        "provenance": {"run_id": "generated-pending", "attempt_id": "attempt-1",
                       "config_digest": CONFIG_DIGEST},
        "backend_observation": "NOT_OBSERVED",
        "contract_digest": "", "descriptor_digest": "", "policy_digest": "",
        "frozen_protocol_digest": "", "synthetic_fault": synthetic_fault,
        "status": "NOT_RUN",
    }
    validate_comparison(contract, descriptors, policies, manifest)

    # The declaration is valid and the generated run proceeds to execution.
    # This is a protocol-validity status, independent of PASS/FAIL outcome.
    manifest["status"] = "VALID"
    manifest["contract_digest"] = contract_digest(contract)
    manifest["descriptor_digest"] = descriptor_digest(descriptors)
    manifest["policy_digest"] = policy_digest(policies)
    manifest["frozen_protocol_digest"] = frozen_protocol_digest(
        contract, descriptors, policies, manifest
    )
    manifest["run_id"] = derived_run_id(manifest["frozen_protocol_digest"])
    manifest["provenance"]["run_id"] = manifest["run_id"]

    records_by_arm: dict[str, list[EmbeddingRecord]] = {arm: [] for arm in arms}
    query_vector_map = production["vectors"]
    for arm in arms:
        descriptor = next(row for row in descriptors if row["arm_id"] == arm)
        for kind, identities in (("query", sorted(query_ids)), ("candidate", candidate_ids)):
            for ident in identities:
                repr_id = f"repr-{arm}-{ident}"
                vector = query_vector_map[arm].get(ident)
                omitted = kind == "candidate" and vector is None and case_id == "partial_coverage"
                if vector is None and not omitted:
                    raise ValueError(f"generated {kind} vector missing unexpectedly: {arm}/{ident}")
                consumed = int(vector is not None)
                envelope = BenchmarkEnvelope(
                    record_id=f"env-{arm}-{kind}-{ident}",
                    comparison_id=contract["comparison_id"], run_id=manifest["run_id"],
                    attempt_id="attempt-1", arm_id=arm, input_refs=(repr_id,),
                    consumed_coverage={"expected": 1, "consumed": consumed,
                                       "omitted": 1 - consumed if omitted else 0,
                                       "failed": 0},
                    raw_response_artifact_ref=None,
                    absence_reason="FIXTURE_OMISSION" if omitted else "SYNTHETIC_INLINE_VECTOR",
                    requested_model=descriptor["requested_model"],
                    resolved_backend="NOT_OBSERVED", config_digest=descriptor["config_digest"],
                    policy_decision_id=descriptor["policy_decision_id"], request_ref=None,
                    judgment_version_refs=(), resource_observations={}, validity_ref=None,
                    outcome_ref=None, provider_status="SUCCESS", per_item_errors=(), wall_time_ms=None,
                )
                payload = EmbeddingPayload(
                    space_id=descriptor["space_id"], representation_id=repr_id,
                    query_id=ident if kind == "query" else None,
                    candidate_id=ident if kind == "candidate" else None,
                    kind=kind, vector=tuple(vector) if vector is not None else None,
                    failure_reason=None,
                )
                records_by_arm[arm].append(EmbeddingRecord(envelope=envelope, payload=payload))
    return contract, descriptors, policies, manifest, records_by_arm


def run_generated_case(case_id: str, output_root: Path) -> Path:
    """Run one named valid generated case and emit a verified ten-file closure.

    Invalid protocol catalog entries are validated against their declarations
    and raise ``ValueError`` before the output path is inspected or created.
    """
    case = get_case(case_id)
    if case_id not in _ALLOWED_CASES:
        # Preserve D01's own rejection evidence and fail closed before any
        # output side effect. The frozen D04 verifier does not accept arbitrary
        # invalid declarations as artifact outcomes.
        validate_comparison(
            case["comparison"], case["descriptors"], case["policies"], case["run_manifest"]
        )
        if case_id == "frozen_protocol_mutation":
            raise ValueError("frozen protocol mutation case requires verifier-only handling")
        raise ValueError(f"generated case is not executable by this harness: {case_id}")

    contract_data, descriptors, policies, manifest, records_by_arm = _valid_declarations(case, case_id)
    contract = comparison_contract_from_payload(contract_data)
    rankings_by_arm = {
        arm: rank_arm(
            next(record for record in records if record.payload.kind == "query"),
            [record for record in records if record.payload.kind == "candidate"],
        )
        for arm, records in records_by_arm.items()
    }

    # Judgment values are opened only after all arms have been produced and
    # ranked, preserving the D01 label firewall.
    judgments = [Judgment(**row) for row in _json_copy(case["judgments"])]
    failures = _json_copy(case["failures"])
    report = evaluate_comparison(
        contract, rankings_by_arm, judgments, failures,
        query_ids=case["production"]["query_ids"],
        synthetic_fault=manifest["synthetic_fault"],
    )
    # D04's frozen report projection exposes selected-row counts per arm and
    # a non-promotional conclusion. Preserve D03's computed values/statuses.
    report_payload = {
        "comparison_id": report.comparison_id,
        "validity": report.validity,
        "benchmark_status": report.benchmark_status,
        "primary_metric_id": report.primary_metric_id,
        "primary_value": report.primary_value,
        "arm_values": dict(report.arm_values),
        "coverage": {
            arm: sum(row.coverage_status == "SELECTED" for row in rankings_by_arm[arm])
            for arm in contract.arm_ids
        },
        "failure_class": report.failure_class,
        "conclusion": "COMPARISON_INVALID_NO_OUTCOME_CLAIM"
        if report.validity == "INVALID_PROTOCOL"
        else "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM",
    }
    embeddings = [embedding_record_payload(record)
                  for arm in contract.arm_ids for record in records_by_arm[arm]]
    embeddings.sort(key=lambda row: row["envelope"]["record_id"])
    ranked = [ranked_candidate_payload(row)
              for arm in contract.arm_ids for row in rankings_by_arm[arm]]
    ranked.sort(key=lambda row: row["record_id"])
    judgment_rows = [judgment_payload(row) for row in judgments]
    judgment_rows.sort(key=lambda row: row["record_id"])
    affected = sorted(row["envelope"]["record_id"] for row in embeddings)
    event_type = manifest["synthetic_fault"]
    ledger = failure_ledger_payload(
        run_id=manifest["run_id"], comparison_id=contract.comparison_id,
        attempt_id="attempt-1", event_type=event_type,
        reason="synthetic resource fault" if event_type != "NONE" else "no synthetic failures",
        affected_refs=affected if event_type != "NONE" else (),
    )
    candidate: dict[str, object] = {
        "benchmark_report.json": report_payload,
        "capability_descriptors.jsonl": descriptors,
        "comparison_contract.json": contract_data,
        "embedding_results.jsonl": embeddings,
        "failure_ledger.json": ledger,
        "judgments.jsonl": judgment_rows,
        "policy_decisions.jsonl": policies,
        "ranked_candidates.jsonl": ranked,
        "run_manifest.json": manifest,
        "synthetic_receipt.json": {
            "spec_sha": SPEC_SHA, "execution_authority_sha": EXECUTION_AUTHORITY_SHA,
            "canonical_contract_blob": CANONICAL_CONTRACT_BLOB,
            "execution_mode": "SYNTHETIC", "real_benchmark_executed": False,
            "provider_calls": 0, "network_egress_bytes": 0,
            "protected_media_used": False, "model_download_or_change": False,
            "winner_observed": False, "real_model_provider_claims": "NOT_OBSERVED",
            "gate0_terminal_sha": None, "gate_promotion": False,
        },
    }
    verify_artifact_set(candidate, mode="SYNTHETIC")
    destination = Path(output_root)
    write_artifact_root(destination, candidate)
    verify_path(destination, mode="SYNTHETIC")
    return destination


def build_generated_three_arm_inputs(case_id: str) -> dict[str, Any]:
    """Build schema-closed three-arm inputs for one executable generated case.

    Non-executable generated cases are refused before any output path is
    touched. The returned compatibility contract is validated against
    ``schemas/gate1_compat_v2/three_arm_compat_contract.json`` by the tests.
    """
    case = get_case(case_id)
    if case_id not in _ALLOWED_CASES:
        # Negative generated cases are not executable by the three-arm harness;
        # refuse before any artifact directory is created. When the fixture
        # already violates the v1 protocol contract, preserve that diagnostic.
        try:
            validate_comparison(
                case["comparison"], case["descriptors"], case["policies"], case["run_manifest"]
            )
        except ContractError as exc:
            raise ValueError(
                f"generated case is not executable by this harness: {case_id}: {exc}"
            ) from exc
        raise ValueError(f"generated case is not executable by this harness: {case_id}")

    contract_data, source_descriptors, source_policies, manifest, source_records = (
        _valid_declarations(case, case_id)
    )
    source_arms = tuple(contract_data["arm_ids"])
    arm_sources = (source_arms[0], source_arms[1], source_arms[1])

    descriptor_by_arm = {row["arm_id"]: row for row in source_descriptors}
    policy_by_id = {row["policy_decision_id"]: row for row in source_policies}
    descriptors: list[dict[str, Any]] = []
    policies: list[dict[str, Any]] = []
    policy_by_charter: dict[str, str] = {}
    for index, (arm_id, source_arm) in enumerate(zip(CHARTER_ARMS, arm_sources), start=1):
        source_descriptor = descriptor_by_arm[source_arm]
        policy_id = f"generated-three-arm-policy-{index}"
        policy_by_charter[arm_id] = policy_id
        descriptor = _json_copy(source_descriptor)
        descriptor.update(
            record_id=f"generated-three-arm-descriptor-{index}",
            arm_id=arm_id,
            space_id=f"generated-three-arm-space-{index}",
            policy_decision_id=policy_id,
        )
        descriptors.append(descriptor)
        policy = _json_copy(policy_by_id[source_descriptor["policy_decision_id"]])
        policy.update(
            record_id=f"generated-three-arm-policy-record-{index}",
            policy_decision_id=policy_id,
        )
        policies.append(policy)

    pair_template = _json_copy(contract_data)
    pair_template["comparison_id"] = f"generated-three-arm-{case_id}"
    # S-08: the embedded template must be one frozen charter pair and its
    # policy keys must match the charter arms (not the source fixture arms).
    pair_template["arm_ids"] = list(CHARTER_PAIRS[0])
    pair_template["policy_eligibility"] = policy_by_charter
    pair_template["b07_metric_states"] = _json_copy(B07_NOT_COMPUTABLE)

    source_inputs = manifest["candidate_production_inputs"]
    declarations = [
        _json_copy(item) for item in source_inputs if item["kind"] in {"query", "candidate"}
    ]
    rankings_by_arm = {}
    for arm_id, source_arm in zip(CHARTER_ARMS, arm_sources):
        descriptor = next(row for row in descriptors if row["arm_id"] == arm_id)
        source_rows = source_records[source_arm]
        arm_rows = []
        for record in source_rows:
            kind = record.payload.kind
            identity = record.payload.query_id if kind == "query" else record.payload.candidate_id
            representation_id = f"repr-{arm_id}-{identity}"
            cloned = replace(
                record,
                envelope=replace(
                    record.envelope,
                    record_id=f"env-{arm_id}-{kind}-{identity}",
                    arm_id=arm_id,
                    input_refs=(representation_id,),
                    policy_decision_id=policy_by_charter[arm_id],
                ),
                payload=replace(
                    record.payload,
                    representation_id=representation_id,
                    space_id=descriptor["space_id"],
                ),
            )
            arm_rows.append(cloned)
        for item in source_inputs:
            if item["kind"] != "representation" or item["arm_id"] != source_arm:
                continue
            source_prefix = f"repr-{source_arm}-"
            suffix = item["input_id"][len(source_prefix):]
            declarations.append({
                "kind": "representation",
                "input_id": f"repr-{arm_id}-{suffix}",
                "arm_id": arm_id,
                "space_id": descriptor["space_id"],
            })
        query = next(row for row in arm_rows if row.payload.kind == "query")
        candidates = [row for row in arm_rows if row.payload.kind == "candidate"]
        rankings_by_arm[arm_id] = rank_arm(query, candidates)

    manifest["candidate_production_inputs"] = sorted(
        declarations, key=lambda item: (item["kind"], item["input_id"], item.get("arm_id", ""))
    )
    compat_contract = {
        "schema_version": 2,
        "execution_mode": "SYNTHETIC",
        "arm_ids": list(CHARTER_ARMS),
        "pair_contract_template": pair_template,
        "b07_metric_states": _json_copy(B07_NOT_COMPUTABLE),
    }
    judgments = [
        replace(Judgment(**row), evidence_class=JUDGMENT_EVIDENCE_CLASS)
        for row in _json_copy(case["judgments"])
    ]
    return {
        "fixture_id": case_id,
        "contract": compat_contract,
        "descriptors": descriptors,
        "policies": policies,
        "run_manifest": manifest,
        "rankings_by_arm": rankings_by_arm,
        "judgments": judgments,
        "failures": _json_copy(case["failures"]),
        "query_ids": case["production"]["query_ids"],
        "arm_sources": arm_sources,
    }


def run_generated_three_arm_case(case_id: str, output_root: Path) -> Path:
    """Run one generated case through the accepted three-arm adapter.

    The third charter arm is a deterministic synthetic projection of the
    generated second arm. No runtime is dispatched and no winner is selected.
    The report is written only after all case, pair, and adapter validation
    succeeds.
    """
    inputs = build_generated_three_arm_inputs(case_id)
    arm_sources = inputs["arm_sources"]
    runtime_derivations = [
        {
            "arm_id": CHARTER_ARMS[index],
            "derived_from_arm_id": arm_sources[index],
            "synthetic_projection": index == len(CHARTER_ARMS) - 1,
        }
        for index in range(len(CHARTER_ARMS))
    ]
    report = build_three_arm_compat_report(
        inputs["contract"],
        inputs["descriptors"],
        inputs["policies"],
        inputs["run_manifest"],
        inputs["rankings_by_arm"],
        inputs["judgments"],
        inputs["failures"],
        query_ids=inputs["query_ids"],
        fixture_id=inputs["fixture_id"],
        code_sha=gate1_code_sha(),
        arm_derivations=runtime_derivations,
        synthetic_fault=inputs["run_manifest"]["synthetic_fault"],
    )

    destination = Path(output_root)
    report_bytes = (
        json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    receipt = {
        "schema_version": 2,
        "execution_mode": "SYNTHETIC",
        "fixture_id": report["fixture_id"],
        "evidence_status": EVIDENCE_STATUS,
        "judgment_evidence_class": JUDGMENT_EVIDENCE_CLASS,
        "code_sha": report["code_sha"],
        "contract_digest": report["contract_digest"],
        "compat_contract": inputs["contract"],
        "report_filename": THREE_ARM_REPORT_FILENAME,
        "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        "claim_limits": list(LIMITATIONS),
        "real_benchmark_executed": False,
        "provider_calls": 0,
        "network_egress_bytes": 0,
        "protected_media_used": False,
        "model_download_or_change": False,
        "winner_observed": False,
        "gate_promotion": False,
    }
    receipt_bytes = (
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / THREE_ARM_REPORT_FILENAME
    report_path.write_bytes(report_bytes)
    (destination / THREE_ARM_RECEIPT_FILENAME).write_bytes(receipt_bytes)
    return report_path


def write_generated_fixtures(output_dir: Path) -> Path:
    """Write the JSON-only generated fixture catalog and a readiness summary."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    cases = all_cases()
    for case_id in CASE_IDS:
        path = destination / f"{case_id}.json"
        path.write_text(json.dumps(cases[case_id], ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False) + "\n",
                        encoding="utf-8")
    summary = {
        "case_ids": list(CASE_IDS),
        "generated_fixture_count": len(CASE_IDS),
        "execution_mode": "SYNTHETIC",
        "real_benchmark_executed": False,
        "provider_calls": 0,
        "network_egress_bytes": 0,
        "protected_media_used": False,
        "model_download_or_change": False,
        "winner_observed": False,
        "gate_promotion": False,
        "artifact_filenames": list(ARTIFACT_FILENAMES),
    }
    (destination / "readiness.json").write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return destination


__all__ = [
    "CASE_IDS",
    "CHARTER_ARMS",
    "CHARTER_PAIRS",
    "B07_NOT_COMPUTABLE",
    "CompatibilityError",
    "all_cases",
    "build_three_arm_compat_report",
    "get_case",
    "run_generated_case",
    "run_generated_three_arm_case",
    "write_generated_fixtures",
]
