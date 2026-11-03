"""Fail-closed, deterministic Gate-2 preregistration freeze contract.

This module seals declarations only. It does not execute workloads or select a
mechanism. All submitted mappings use closed, versioned field sets.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import Any, Mapping


class PreregistrationError(ValueError):
    """A preregistration is incomplete, stale, malformed, or preselected."""


_EVIDENCE_CLASSES = {
    "MEASURED", "MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED",
    "EDITORIAL_INFERENCE",
}
_PLACEHOLDERS = {"", "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example"}
_TOP_KEYS = {
    "schema_version", "workload_identity", "configuration_identity",
    "dependency_generations", "fault_schedule", "metrics", "numeric_bounds",
    "classification_rule", "evidence_declarations", "run_attempt_identity",
    "policy_authority", "resource_request", "baseline", "contract_fingerprints",
    "resource_policy_identity",
}
_FROZEN_CONTRACT_IDS = frozenset({
    "gate2_synthetic_candidate",
    "gate2_reconciliation",
    "canonical_contracts",
    "resource_policy_v5",
    "gate2_protocol_candidate",
    "gate2_measure_candidate",
    "gate2_preregistration_schema_candidate",
    "gate2_measurement_schema_candidate",
})
_SHAPES = {
    "workload_identity": {"workload_id", "digest"},
    "configuration_identity": {"config_id", "digest"},
    "fault_schedule": {"seed", "repetitions", "events"},
    "classification_rule": {"rule_id", "threshold"},
    "run_attempt_identity": {"run_id", "attempt_id"},
    "policy_authority": {"policy_id", "authority"},
    "resource_request": {"resource_class", "concurrency"},
    "baseline": {"storage", "index"},
}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER_PLACEHOLDERS = frozenset({
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
})
_IDENTIFIER = re.compile(
    r"^(?!\s)(?!.*\s$)[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}$"
)


def _is_identifier_placeholder(value: str) -> bool:
    # Identifier syntax is ASCII-only; lower() therefore implements the
    # explicitly ASCII-case-insensitive token policy without Unicode folding.
    return value.isascii() and value.lower() in _IDENTIFIER_PLACEHOLDERS


def _validate_identifier(value: Any, path: str) -> None:
    if (not isinstance(value, str) or not _IDENTIFIER.fullmatch(value)
            or _is_identifier_placeholder(value)):
        raise PreregistrationError(f"{path} must match the preregistration identifier schema")


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise PreregistrationError("payload is not canonical JSON data") from exc


def _closed(mapping: Any, expected: set[str], path: str) -> None:
    if not isinstance(mapping, Mapping):
        raise PreregistrationError(f"{path} must be an object")
    actual = set(mapping)
    if actual != expected:
        missing, unknown = expected - actual, actual - expected
        raise PreregistrationError(f"{path} fields invalid; missing={sorted(missing)}, unknown={sorted(unknown)}")


def _validate_values(value: Any, path: str = "payload") -> None:
    if value is None:
        raise PreregistrationError(f"null value at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise PreregistrationError(f"non-string key at {path}")
            normalized = key.casefold()
            if normalized in {"desired_mechanism", "adoption", "disposition"}:
                raise PreregistrationError(f"preselection field at {path}.{key}")
            _validate_values(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            _validate_values(item, f"{path}[{i}]")
    elif isinstance(value, str):
        stripped = value.strip()
        if (stripped.isascii() and stripped.lower() in _PLACEHOLDERS) or stripped == "0" * 64:
            raise PreregistrationError(f"placeholder value at {path}")
    elif isinstance(value, float) and not math.isfinite(value):
        raise PreregistrationError(f"non-finite number at {path}")


def _validate_payload(data: Mapping[str, Any], consumed: Mapping[str, str], policy: Mapping[str, Any]) -> dict[str, Any]:
    _closed(data, _TOP_KEYS, "payload")
    if data["schema_version"] != "gate2.preregistration.v1":
        raise PreregistrationError("unsupported schema_version")
    _validate_values(data)
    for name, fields in _SHAPES.items():
        _closed(data[name], fields, name)
    for name in ("workload_identity", "configuration_identity"):
        digest = data[name]["digest"]
        if not isinstance(digest, str) or not _HEX64.fullmatch(digest):
            raise PreregistrationError(f"{name}.digest must be lowercase SHA-256")
    for name in ("dependency_generations", "numeric_bounds", "evidence_declarations", "contract_fingerprints"):
        if not isinstance(data[name], Mapping) or not data[name]:
            raise PreregistrationError(f"{name} must be a nonempty object")
    for name, generation in data["dependency_generations"].items():
        _validate_identifier(name, "dependency_generations name")
        _validate_identifier(generation, f"dependency_generations[{name!r}]")
    _validate_identifier(data["workload_identity"]["workload_id"], "workload_identity.workload_id")
    _validate_identifier(data["configuration_identity"]["config_id"], "configuration_identity.config_id")
    for field in ("run_id", "attempt_id"):
        _validate_identifier(data["run_attempt_identity"][field], f"run_attempt_identity.{field}")
    _validate_identifier(data["policy_authority"]["policy_id"], "policy_authority.policy_id")
    for section in ("numeric_bounds", "evidence_declarations"):
        for name in data[section]:
            _validate_identifier(name, f"{section} name")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in data["numeric_bounds"].values()):
        raise PreregistrationError("numeric_bounds values must be finite numbers")
    if any(v not in _EVIDENCE_CLASSES for v in data["evidence_declarations"].values()):
        raise PreregistrationError("evidence declaration has a non-canonical class")
    for name, expected in (("fault_schedule", {"seed", "repetitions", "events"}),):
        _closed(data[name], expected, name)
    schedule = data["fault_schedule"]
    if isinstance(schedule["seed"], bool) or not isinstance(schedule["seed"], int) or isinstance(schedule["repetitions"], bool) or not isinstance(schedule["repetitions"], int) or schedule["repetitions"] < 1:
        raise PreregistrationError("fault schedule requires an integer seed and positive repetitions")
    if not isinstance(schedule["events"], list):
        raise PreregistrationError("fault schedule events must be a list")
    for i, event in enumerate(schedule["events"]):
        _closed(event, {"at", "fault"}, f"fault_schedule.events[{i}]")
        if isinstance(event["at"], bool) or not isinstance(event["at"], int) or event["at"] < 0:
            raise PreregistrationError("fault event at must be a nonnegative integer")
        if not isinstance(event["fault"], str) or not event["fault"].strip():
            raise PreregistrationError("fault event fault must be a nonempty string")
    if not isinstance(data["metrics"], list) or not data["metrics"]:
        raise PreregistrationError("metrics must be a nonempty list")
    for i, metric in enumerate(data["metrics"]):
        _closed(metric, {"name", "unit", "aggregation"}, f"metrics[{i}]")
        if any(not isinstance(metric[field], str) or not metric[field].strip()
               for field in ("name", "unit", "aggregation")):
            raise PreregistrationError("metric name, unit, and aggregation must be nonempty strings")
        if (not _IDENTIFIER.fullmatch(metric["name"])
                or _is_identifier_placeholder(metric["name"])):
            raise PreregistrationError("metric name must match the preregistration identifier schema")
    for section in ("workload_identity", "configuration_identity", "run_attempt_identity", "policy_authority", "baseline"):
        if any(not isinstance(v, str) for v in data[section].values()):
            raise PreregistrationError(f"{section} values must be strings")
    rule_id = data["classification_rule"]["rule_id"]
    if (not isinstance(rule_id, str) or not _IDENTIFIER.fullmatch(rule_id)
            or _is_identifier_placeholder(rule_id)):
        raise PreregistrationError("classification_rule.rule_id must match the preregistration identifier schema")
    threshold = data["classification_rule"]["threshold"]
    if isinstance(threshold, bool) or not (
        isinstance(threshold, (int, float)) and math.isfinite(threshold)
        or isinstance(threshold, str) and threshold.strip()
    ):
        raise PreregistrationError("classification_rule.threshold must be a finite number or nonempty string")
    if data["resource_policy_identity"] != consumed.get("resource_policy_v5"):
        raise PreregistrationError("resource policy identity is stale")
    if dict(data["contract_fingerprints"]) != dict(consumed):
        raise PreregistrationError("consumed-contract fingerprints are stale or incomplete")
    leases = policy.get("resource_leases") if isinstance(policy, Mapping) else None
    request = data["resource_request"]
    if not isinstance(leases, Mapping) or request["resource_class"] not in leases:
        raise PreregistrationError("resource class is absent from supplied resource policy")
    concurrency = request["concurrency"]
    if isinstance(concurrency, bool) or not isinstance(concurrency, int) or concurrency < 1:
        raise PreregistrationError("resource concurrency must be a positive integer")
    lease = leases[request["resource_class"]]
    if not isinstance(lease, Mapping):
        raise PreregistrationError("resource lease policy must be an object")
    # Adaptive lightweight work has no static ceiling. Measured heavy leases are
    # bounded by the policy's current calibration target; fixed quotas use their cap.
    if lease.get("policy") == "CALIBRATE_SEPARATELY":
        raise PreregistrationError("resource class requires calibration before preregistration")
    if "max_concurrent" in lease:
        cap = lease.get("max_concurrent")
        if not isinstance(cap, int) or concurrency > cap:
            raise PreregistrationError("requested concurrency exceeds supplied resource policy maximum")
    elif lease.get("policy") == "ADAPTIVE_MEASURED_LEASE":
        cap = lease.get("calibration_target_max_concurrent", lease.get("initial_max_concurrent"))
        if not isinstance(cap, int) or concurrency > cap:
            raise PreregistrationError("requested concurrency exceeds supplied adaptive lease target")
    elif lease.get("policy") == "ADAPTIVE_READY_WORK":
        pass
    elif lease.get("fixed_quota") is True:
        raise PreregistrationError("fixed resource quota lacks max_concurrent")
    else:
        raise PreregistrationError("resource policy has no usable concurrency semantics")
    return json.loads(_canonical(data))


@dataclass(frozen=True, init=False)
class FrozenPreregistration:
    _payload_bytes: bytes
    freeze_digest: str

    def __init__(self, payload: Mapping[str, Any], freeze_digest: str):
        object.__setattr__(self, "_payload_bytes", _canonical(payload))
        object.__setattr__(self, "freeze_digest", freeze_digest)

    @property
    def payload(self) -> dict[str, Any]:
        # Each access returns an independent view; callers cannot mutate the
        # sealed canonical bytes while leaving the digest unchanged.
        return json.loads(self._payload_bytes)

    def to_dict(self) -> dict[str, Any]:
        return {**self.payload, "freeze_digest": self.freeze_digest}

    def canonical_bytes(self) -> bytes:
        return _canonical(self.to_dict())


@dataclass(frozen=True)
class Preregistration:
    _payload: Mapping[str, Any]
    _consumed_contracts: Mapping[str, str]
    _resource_policy: Mapping[str, Any]

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], *, consumed_contracts: Mapping[str, str], resource_policy: Mapping[str, Any]) -> "Preregistration":
        if not isinstance(consumed_contracts, Mapping) or not consumed_contracts or any(not isinstance(k, str) or not isinstance(v, str) or not v for k, v in consumed_contracts.items()):
            raise PreregistrationError("consumed_contracts must be a nonempty exact fingerprint map")
        if set(consumed_contracts) != _FROZEN_CONTRACT_IDS:
            raise PreregistrationError("all frozen consumed contracts must be supplied")
        if not isinstance(resource_policy, Mapping) or resource_policy.get("schema_version") != 5:
            raise PreregistrationError("resource policy v5 is required")
        clean = _validate_payload(payload, consumed_contracts, resource_policy)
        return cls(clean, dict(consumed_contracts), json.loads(_canonical(resource_policy)))

    def seal(self) -> FrozenPreregistration:
        body = _canonical(self._payload)
        digest = hashlib.sha256(body).hexdigest()
        return FrozenPreregistration(self._payload, digest)
