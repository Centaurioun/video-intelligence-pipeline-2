"""Deterministic synthetic fault injectors for the H3-F02 apparatus."""

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping


class Capability(str, Enum):
    HARNESSED = "HARNESSED"
    NOT_YET_HARNESSED = "NOT_YET_HARNESSED"
    UNREACHABLE = "UNREACHABLE"


class FaultClass(str, Enum):
    A_BEFORE_STAGE_START = "a"
    B_DURING_ATTEMPT = "b"
    C_PARTIAL_ARTIFACT = "c"
    D_RETRY_FAILED_JOB = "d"
    E_REPEATED_IDEMPOTENCY_KEY = "e"
    F_RESTART_RECONSTRUCTION = "f"
    G_PROJECTION_REBUILD = "g"
    H_INTERRUPTED_RECOVERY = "h"
    I_CORRUPT_AT_REST = "i"
    J_POST_SUCCESS_INVALIDATION = "j"
    K_IDENTITY_DRIFT = "k"
    L_CONCURRENT_WRITER = "l"
    M_REFERENTIAL_DIVERGENCE = "m"


class InjectionError(ValueError):
    pass


FAULT_CLASSES = tuple(FaultClass)
_UNREACHABLE = {FaultClass.D_RETRY_FAILED_JOB, FaultClass.G_PROJECTION_REBUILD}
_NOT_YET_HARNESSED = {FaultClass.B_DURING_ATTEMPT, FaultClass.C_PARTIAL_ARTIFACT}
_HARNESSED = set(FAULT_CLASSES) - _UNREACHABLE - _NOT_YET_HARNESSED


@dataclass(frozen=True)
class InjectionResult:
    fault_class: FaultClass
    disposition: str
    detected: bool
    details: Mapping[str, Any]
    payload_digest: str


def _fault(value: FaultClass | str) -> FaultClass:
    if isinstance(value, FaultClass):
        return value
    try:
        return FaultClass(value)
    except (ValueError, TypeError) as exc:
        raise InjectionError(f"unknown fault class: {value!r}") from exc


def capability(fault_class: FaultClass | str) -> Capability:
    fault_class = _fault(fault_class)
    if fault_class in _HARNESSED:
        return Capability.HARNESSED
    if fault_class in _NOT_YET_HARNESSED:
        return Capability.NOT_YET_HARNESSED
    return Capability.UNREACHABLE


def inject(fault_class: FaultClass | str, payload: Mapping[str, Any]) -> InjectionResult:
    """Evaluate a deterministic synthetic condition without mutating its payload."""
    fault_class = _fault(fault_class)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    state = capability(fault_class)
    if state is not Capability.HARNESSED:
        return InjectionResult(fault_class, state.value, False, {}, digest)

    details: dict[str, Any] = {}
    detected = False
    if fault_class is FaultClass.A_BEFORE_STAGE_START:
        detected = not bool(payload.get("predecessor_succeeded", False))
        details["disposition"] = "BLOCKED_PREREQUISITE" if detected else "ADMITTED"
    elif fault_class is FaultClass.E_REPEATED_IDEMPOTENCY_KEY:
        detected = bool(payload.get("second_submission", False))
        details["disposition"] = "EQUAL_NO_MUTATION" if detected else "FIRST_SUBMISSION"
    elif fault_class is FaultClass.F_RESTART_RECONSTRUCTION:
        detected = payload.get("decision_vector_a") != payload.get("decision_vector_b")
        details["disposition"] = "BLOCKED_PREREQUISITE" if detected else "MATCHED"
    elif fault_class is FaultClass.H_INTERRUPTED_RECOVERY:
        interruption_observed = payload.get("interruption_observed") is True
        recovery_swallowed = payload.get("recovery_swallowed")
        detected = interruption_observed and (
            recovery_swallowed is False or recovery_swallowed is True
        )
        if interruption_observed and recovery_swallowed is True:
            details.update(disposition="FALSE_SUCCESS", false_success=True)
        elif interruption_observed and recovery_swallowed is not False:
            details.update(
                disposition="RECOVERY_OUTCOME_NOT_OBSERVED", false_success=False
            )
        else:
            details.update(
                disposition="BLOCKED_PREREQUISITE" if detected else "ACCEPTED",
                false_success=False,
            )
    elif fault_class is FaultClass.I_CORRUPT_AT_REST:
        text = str(payload.get("payload", ""))
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError:
            detected = True
        else:
            nested = decoded.get("payload") if isinstance(decoded, dict) else None
            if isinstance(nested, str) and nested.lstrip().startswith("{"):
                try:
                    json.loads(nested)
                except json.JSONDecodeError:
                    detected = True
        details["disposition"] = "BLOCKED_PREREQUISITE" if detected else "ACCEPTED"
    elif fault_class is FaultClass.J_POST_SUCCESS_INVALIDATION:
        chain = list(payload.get("chain", []))
        allowed = {"AVAILABLE": {"QUARANTINED"}, "QUARANTINED": {"CLEANUP_PENDING"},
                   "CLEANUP_PENDING": {"CLEANED", "TOMBSTONED"}}
        legal = bool(not chain or chain[0] == "AVAILABLE") and all(
            after in allowed.get(before, set()) for before, after in zip(chain, chain[1:]))
        detected = not legal
        details["disposition"] = "ILLEGAL_TRANSITION" if detected else "ADVANCED"
    elif fault_class is FaultClass.K_IDENTITY_DRIFT:
        detected = payload.get("sealed_digest") != payload.get("observed_digest")
        details["disposition"] = "BLOCKED_PREREQUISITE" if detected else "EQUAL"
    elif fault_class is FaultClass.L_CONCURRENT_WRITER:
        writers = sorted(str(writer) for writer in payload.get("writers", []))
        schedule = tuple((writer, turn) for turn, writer in enumerate(writers))
        detected = len(writers) > 1 and len(set(writers)) > 1
        details.update(schedule=schedule, disposition="WRITE_CONFLICT" if detected else "NO_CONFLICT")
    elif fault_class is FaultClass.M_REFERENTIAL_DIVERGENCE:
        known = {str(row["attempt_id"]) for row in payload.get("attempts", [])}
        divergent = tuple(sorted(set(map(str, payload.get("referenced_attempt_ids", []))) - known))
        detected = bool(divergent)
        details.update(divergent_attempt_ids=divergent,
                       disposition="BLOCKED_PREREQUISITE" if detected else "CONSISTENT")

    # PASS is reserved for a HARNESSED injector that detected the requested fault.
    disposition = "PASS" if detected else "NOT_TRIGGERED"
    return InjectionResult(fault_class, disposition, detected, details, digest)
