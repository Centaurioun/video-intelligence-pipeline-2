"""Fail-closed validation for preregistered Gate-1 comparisons.

This module validates declarations only. It has no provider, model, network, or
media execution dependencies. In the current H0 authority, REAL comparisons are
always refused; historical dependency hashes cannot grant execution authority.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import re
from typing import Any

LABEL_NAMES = ("judgment", "label", "gold", "relevance", "relevant", "adjudicat")
PRODUCTION_INPUT_KINDS = frozenset({"query", "candidate", "representation"})
RUN_MANIFEST_FIELDS = frozenset({
    "schema_version", "run_id", "comparison_id", "execution_mode", "spec_sha",
    "execution_authority_sha", "canonical_contract_blob", "source_partitions",
    "candidate_production_inputs", "provenance", "backend_observation",
    "contract_digest", "descriptor_digest", "policy_digest", "frozen_protocol_digest",
    "synthetic_fault", "status",
})
IDENTITY_FIELDS = frozenset({"record_id", "arm_id", "policy_decision_id"})
REQUIRED_CONTROLS = frozenset({"operation", "input_mode", "window_profile_digest", "metric",
                              "normalization", "provider_family"})
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Raised when a comparison cannot be shown eligible under its contract."""


def _get(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(key, default)
    return getattr(value, key, default)


def _need(ok: Any, message: str) -> None:
    if not ok:
        raise ContractError(message)


def _keys(value: Any) -> set[str]:
    if isinstance(value, Mapping):
        return set(value)
    if hasattr(value, "__dataclass_fields__"):
        return set(value.__dataclass_fields__)
    if hasattr(value, "__dict__"):
        return set(vars(value))
    return set()


def _sequence(value: Any, name: str) -> Sequence:
    _need(isinstance(value, Sequence) and not isinstance(value, (str, bytes)),
          f"{name} must be a sequence")
    return value


def _validate_partition(partitions: Any) -> None:
    _need(isinstance(partitions, Mapping), "source_partitions must be a mapping")
    _need(set(partitions) == {"development", "evaluation"},
          "source_partitions fields must be exactly development and evaluation")
    _need("development" in partitions and "evaluation" in partitions,
          "source_partitions must declare development and evaluation")
    development = _sequence(partitions["development"], "development sources")
    evaluation = _sequence(partitions["evaluation"], "evaluation sources")
    _need(development and evaluation, "source partitions must not be empty")
    for name, values in (("development", development), ("evaluation", evaluation)):
        _need(all(isinstance(v, str) and v.strip() for v in values),
              f"{name} source identities must be non-empty strings")
        _need(len(set(values)) == len(values), f"{name} source identities must be unique")
    overlap = set(development) & set(evaluation)
    _need(not overlap, f"source partitions overlap: {sorted(overlap)}")


def _validate_policy(policies: Sequence, descriptors: Sequence, contract: Any) -> None:
    by_id: dict[str, Any] = {}
    for policy in policies:
        policy_id = _get(policy, "policy_decision_id")
        _need(isinstance(policy_id, str) and policy_id, "policy decision id is required")
        _need(policy_id not in by_id, f"duplicate policy decision id {policy_id!r}")
        by_id[policy_id] = policy
        decision = _get(policy, "decision")
        _need(decision == "ALLOW", f"policy {policy_id!r} is not currently allowed ({decision!r})")
        _need(not _get(policy, "revoked", False), f"policy {policy_id!r} is revoked")
        expires = _get(policy, "expires_at")
        if expires is not None:
            _need(isinstance(expires, str), f"policy {policy_id!r} expiry must be an ISO timestamp")
            try:
                expiry = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=timezone.utc)
            except ValueError as exc:
                raise ContractError(f"policy {policy_id!r} expiry is malformed") from exc
            _need(expiry > datetime.now(timezone.utc), f"policy {policy_id!r} is expired")

    eligibility = _get(contract, "policy_eligibility")
    _need(isinstance(eligibility, Mapping), "policy_eligibility must be a mapping")
    for arm_id in (_get(contract, "arm_ids") or ()):
        policy_id = eligibility.get(arm_id)
        _need(policy_id in by_id, f"arm {arm_id!r} has no resolvable current policy")
    for desc in descriptors:
        _need(_get(desc, "policy_decision_id") in by_id,
              f"descriptor for arm {_get(desc, 'arm_id')!r} has no resolvable policy")
        arm_id = _get(desc, "arm_id")
        _need(_get(desc, "policy_decision_id") == eligibility.get(arm_id),
              f"descriptor policy does not match arm {arm_id!r} policy declaration")


def _contains_label_semantics(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            any(token in str(key).lower() for token in LABEL_NAMES)
            or _contains_label_semantics(item)
            for key, item in value.items()
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_label_semantics(item) for item in value)
    return isinstance(value, str) and any(token in value.lower() for token in LABEL_NAMES)


def _validate_firewall(run: Mapping[str, Any]) -> None:
    unknown_fields = set(run) - RUN_MANIFEST_FIELDS
    _need(not unknown_fields,
          f"unknown run-manifest fields are forbidden: {sorted(unknown_fields)}")
    sensitive_fields = [key for key in run if any(token in str(key).lower() for token in LABEL_NAMES)]
    _need(not sensitive_fields,
          f"label-bearing run-manifest fields are forbidden during candidate production: {sensitive_fields}")
    _need(not _contains_label_semantics(run),
          "label-bearing data is forbidden anywhere in candidate-production run inputs")
    _need("ranking_input_artifacts" not in run,
          "ranking_input_artifacts is not a canonical typed candidate input declaration")
    for field in ("judgments", "labels", "gold_labels", "judgment_refs"):
        _need(field not in run, f"{field} must not be present in candidate-production run inputs")

    inputs = _sequence(run.get("candidate_production_inputs"), "candidate_production_inputs")
    _need(bool(inputs), "candidate_production_inputs must not be empty")
    for item in inputs:
        _need(isinstance(item, Mapping),
              "candidate input declarations must be typed objects with a kind and input_id")
        kind = item.get("kind")
        _need(kind in PRODUCTION_INPUT_KINDS,
              "candidate input kind is not an allowed query, candidate, or representation")
        expected_fields = ({"kind", "input_id", "arm_id", "space_id"}
                           if kind == "representation" else {"kind", "input_id"})
        _need(set(item) == expected_fields,
              "candidate input declaration fields do not match its closed kind schema")
        input_id = item.get("input_id")
        _need(isinstance(input_id, str) and input_id.strip()
              and "/" not in input_id and "\\" not in input_id,
              "candidate input id must be a non-path logical identity")
        _need(not _contains_label_semantics(item),
              f"judgment/label-bearing candidate input {item!r} is forbidden")


def validate_comparison(contract: Any, descriptors: Sequence, policies: Sequence,
                        run_manifest: Mapping[str, Any]) -> None:
    """Validate arm declarations, source isolation, label firewall, policy and provenance.

    The function raises :class:`ContractError` on any uncertainty. It performs
    no side effects and intentionally returns no winner/promotion status.
    """
    _need(isinstance(run_manifest, Mapping), "run_manifest must be a mapping")
    descriptors = _sequence(descriptors, "descriptors")
    policies = _sequence(policies, "policies")
    mode = _get(contract, "execution_mode")
    _need(mode in {"SYNTHETIC", "REAL"}, "execution mode must be SYNTHETIC or REAL")
    # Deliberately precedes historical SHA/provenance inspection: a hash cannot
    # change the current authority boundary.
    if mode == "REAL":
        raise ContractError("REAL comparison refused: current authority is not granted")

    _need(_get(run_manifest, "execution_mode") == mode, "contract/run execution mode mismatch")
    arm_ids = _get(contract, "arm_ids")
    _need(isinstance(arm_ids, Sequence) and not isinstance(arm_ids, (str, bytes)) and len(arm_ids) == 2,
          "exactly two declared arms are required")
    _need(len(set(arm_ids)) == 2 and all(isinstance(x, str) and x for x in arm_ids),
          "declared arm ids must be unique non-empty strings")
    _need(len(descriptors) == 2, "exactly two arm descriptors are required")
    actual_arms = [_get(d, "arm_id") for d in descriptors]
    _need(len(set(actual_arms)) == 2 and set(actual_arms) == set(arm_ids),
          "arm descriptors must uniquely match declared arms")

    axis = _get(contract, "changed_axis")
    _need(isinstance(axis, str) and axis and axis not in IDENTITY_FIELDS,
          "a material changed_axis must be declared")
    control_values = _get(contract, "pinned_controls")
    _need(isinstance(control_values, Mapping) and control_values,
          "pinned_controls must be a non-empty mapping")
    _need(axis not in control_values, "changed axis cannot also be a pinned control")
    missing_controls = REQUIRED_CONTROLS - set(control_values) - {axis}
    _need(not missing_controls, f"required pinned controls are missing: {sorted(missing_controls)}")
    axis_values = [_get(d, axis) for d in descriptors]
    _need(all(v is not None for v in axis_values) and axis_values[0] != axis_values[1],
          "declared changed axis must be present and differ across arms")

    descriptor_fields = [_keys(d) - IDENTITY_FIELDS for d in descriptors]
    _need(descriptor_fields[0] == descriptor_fields[1],
          "arm descriptor fields must match exactly outside identity fields")
    common_fields = descriptor_fields[0]
    _need(axis in common_fields, "changed axis is not part of descriptor contract")
    for field in common_fields:
        values = [_get(d, field) for d in descriptors]
        if field == axis:
            continue
        _need(values[0] == values[1], f"undeclared material axis {field!r} differs between arms")
    for name, expected in control_values.items():
        values = [_get(d, name, object()) for d in descriptors]
        _need(all(v == expected for v in values), f"pinned control {name!r} is missing or differs")

    operation = _get(contract, "operation")
    _need(isinstance(operation, str) and operation, "operation must be declared")
    _need(all(_get(d, "operation") == operation for d in descriptors),
          "descriptor operation differs from comparison operation")
    _validate_partition(_get(run_manifest, "source_partitions"))
    _validate_firewall(run_manifest)
    for item in run_manifest["candidate_production_inputs"]:
        if item["kind"] == "representation":
            descriptor = next((d for d in descriptors if _get(d, "arm_id") == item["arm_id"]), None)
            _need(descriptor is not None and item["space_id"] == _get(descriptor, "space_id"),
                  "representation space is incompatible with its arm descriptor")
    _validate_policy(policies, descriptors, contract)

    provenance = _get(run_manifest, "provenance")
    _need(isinstance(provenance, Mapping), "provenance must be a mapping")
    _need(set(provenance) == {"run_id", "attempt_id", "config_digest"},
          "provenance fields must be exactly run_id, attempt_id, and config_digest")
    for required in ("run_id", "attempt_id", "config_digest"):
        _need(isinstance(provenance.get(required), str) and provenance[required],
              f"provenance.{required} is required")
    _need(bool(HEX64.fullmatch(provenance["config_digest"])),
          "provenance.config_digest must be a lowercase SHA-256 digest")
    for desc in descriptors:
        for required in ("record_id", "capability_revision", "config_digest", "space_id"):
            value = _get(desc, required)
            _need(isinstance(value, str) and value, f"descriptor {required} is required")
        _need(bool(HEX64.fullmatch(_get(desc, "config_digest"))),
              "descriptor config_digest must be a lowercase SHA-256 digest")
        _need(_get(desc, "resolved_backend") == "NOT_OBSERVED",
              "synthetic descriptor cannot claim a resolved backend observation")
        _need(_get(desc, "runtime_revision") == "NOT_OBSERVED",
              "synthetic descriptor cannot claim an unobserved runtime revision")
        for field in ("resource_observations", "resource_observation", "runtime_observations"):
            observation = _get(desc, field)
            if observation is not None:
                _need(observation == "NOT_OBSERVED" or
                      (isinstance(observation, Mapping) and
                       all(value == "NOT_OBSERVED" for value in observation.values())),
                      f"synthetic descriptor cannot fabricate {field}")
    _need(_get(run_manifest, "backend_observation") == "NOT_OBSERVED",
          "synthetic run cannot fabricate a backend observation")
    for field in ("resource_observations", "resource_observation", "runtime_observations"):
        observation = _get(run_manifest, field)
        if observation is not None:
            _need(observation == "NOT_OBSERVED" or
                  (isinstance(observation, Mapping) and
                   all(value == "NOT_OBSERVED" for value in observation.values())),
                  f"synthetic run cannot fabricate {field}")
