"""Fail-closed BR-1..BR-9 evidence-to-mechanism decision logic for H3-F03."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from gate0.identity import digest_json


_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_HEX_40 = re.compile(r"^[0-9a-f]{40}$")
# Bound the completion set so a caller cannot make the coverage check allocate
# an unbounded repetition sequence (fail closed on absurd declarations).
_MAX_REPETITIONS = 100
_EVIDENCE_CLASSES = frozenset({
    "MEASURED", "MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED",
    "EDITORIAL_INFERENCE",
})


class DeficitClass(str, Enum):
    C1 = "C1-capacity"
    C2 = "C2-latency"
    C3 = "C3-durability"
    C4 = "C4-concurrency"
    C5 = "C5-recovery-time"
    C6 = "C6-failure-amplification"
    C7 = "C7-observability"


class Disposition(str, Enum):
    NO_DEFICIT_OBSERVED = "BR-1"
    RUN_INVALID_POLICY_OR_IDENTITY = "BR-2"
    PROTOCOL_INVALID = "BR-3"
    DEFICIT_NOT_REPRODUCED = "BR-4"
    CLASSIFICATION_AMBIGUOUS = "BR-5"
    NO_MECHANISM_MAPPED = "BR-6"
    INSUFFICIENT_OBSERVABILITY = "BR-7"
    MECHANISM_ELIGIBLE_FOR_LATER_EVALUATION = "BR-8"
    PRECONDITION_UNMET = "BR-9"


MECHANISMS: tuple[str, ...] = (
    "persistence", "cache", "queue", "scheduler", "retry-backoff", "lease",
    "vector-persistence", "drive-materialization", "proxy-lifecycle",
)

MECHANISM_BY_CLASS: dict[DeficitClass, tuple[str, ...]] = {
    DeficitClass.C1: (),
    DeficitClass.C2: ("scheduler",),
    DeficitClass.C3: ("persistence",),
    DeficitClass.C4: ("lease",),
    DeficitClass.C5: ("retry-backoff",),
    DeficitClass.C6: ("queue",),
    DeficitClass.C7: (),
}

REQUIRED_MEASURED_PATTERN: dict[str, str] = {
    "persistence": "a SUCCEEDED attempt's declared output absent after a preregistered interruption and not exactly rebuildable, with conservation broken",
    "cache": "repeated work over identical idempotency keys exceeding a preregistered share",
    "queue": "measured arrival rate exceeding deterministic service rate under the frozen workload",
    "scheduler": "measured starvation of a declared target, or a makespan regression against the serial baseline",
    "retry-backoff": "measured recurrence of a transient failure class where retry-as-new-attempt succeeds",
    "lease": "measured duplicate execution of one idempotency key by two or more executors",
    "vector-persistence": "measured rebuild-time share above the preregistered bound with representation digests fixed",
    "drive-materialization": "measured coverage shortfall attributable to unavailable bytes, with an effective ALLOW decision",
    "proxy-lifecycle": "measured orphan/leak count above zero after a preregistered lifecycle protocol",
}

# Exact heads supplied by the verified H3-F03 launch overlay. The caller must
# pass them explicitly; observations bind to one of these immutable inputs.


@dataclass(frozen=True)
class DecisionResult:
    disposition: Disposition
    mechanism_eligible: bool
    smallest_missing_mechanism: str | None
    mechanisms: tuple[dict[str, Any], ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        document: dict[str, Any] = {
            "disposition": self.disposition.value,
            "mechanism_eligible": self.mechanism_eligible,
            "smallest_missing_mechanism": self.smallest_missing_mechanism,
            "mechanisms": list(self.mechanisms),
            "notes": list(self.notes),
            "production_eligible": False,
            "gate_promotion": False,
            "mechanism_adopted": False,
        }
        document["disposition_digest"] = digest_json(document)
        return document


def _rows(eligible_for: str | None) -> tuple[dict[str, Any], ...]:
    return tuple({
        "mechanism": name,
        "adoption": False,
        "eligible_for_later_evaluation": name == eligible_for,
        "required_measured_pattern": REQUIRED_MEASURED_PATTERN[name],
    } for name in MECHANISMS)


def _result(disposition: Disposition, note: str,
            eligible: str | None = None) -> DecisionResult:
    return DecisionResult(disposition, eligible is not None, eligible, _rows(eligible), (note,))


def _valid_digest(value: Any) -> bool:
    return isinstance(value, str) and _HEX_64.fullmatch(value) is not None


def _valid_heads(heads: Any) -> bool:
    if not isinstance(heads, Mapping) or set(heads) != {"H3-F01", "H3-F02"}:
        return False
    for entry in heads.values():
        if not isinstance(entry, Mapping):
            return False
        if not isinstance(entry.get("sha"), str) or _HEX_40.fullmatch(entry["sha"]) is None:
            return False
        if not isinstance(entry.get("tree"), str) or _HEX_40.fullmatch(entry["tree"]) is None:
            return False
    return True


def _carrier_state(rows: Any, *, metric_id: str, dependency_heads: Mapping[str, Any],
                   freeze_digest: str, workload_digest: str, config_digest: str,
                   fault_schedule_digest: str,
                   expected_repetitions: int | None) -> tuple[list[float], bool, bool]:
    """Return measured values, missing-carrier flag, and malformed flag."""
    if isinstance(rows, Mapping):
        sequence: Sequence[Any] = (rows,)
    elif isinstance(rows, (tuple, list)):
        sequence = rows
    else:
        return [], True, True
    if not sequence:
        return [], True, True

    values: list[float] = []
    missing = False
    seen: set[int] = set()
    for row in sequence:
        if not isinstance(row, Mapping) or row.get("metric_id") != metric_id:
            return [], missing, True
        repetition = row.get("repetition")
        if isinstance(repetition, bool) or not isinstance(repetition, int) or repetition < 1 or repetition in seen:
            return [], missing, True
        seen.add(repetition)
        dependency_id = row.get("dependency_id")
        if not isinstance(dependency_id, str):
            return [], missing, True
        dependency_parts = dependency_id.split("+")
        if (not dependency_parts or len(set(dependency_parts)) != len(dependency_parts) or
                any(part not in dependency_heads for part in dependency_parts)):
            return [], missing, True
        # A joint F01+F02 measurement is executed/materialized against F02,
        # while its provenance remains bound to both pinned inputs.
        pinned = dependency_heads[dependency_parts[-1]]
        if row.get("candidate_sha") != pinned["sha"] or row.get("candidate_tree") != pinned["tree"]:
            return [], missing, True
        if (row.get("freeze_digest") != freeze_digest or
                row.get("workload_digest") != workload_digest or
                row.get("config_digest") != config_digest or
                row.get("fault_schedule_digest") != fault_schedule_digest):
            return [], missing, True
        status = row.get("status")
        if status == "NOT_OBSERVED":
            if row.get("value") is not None or row.get("evidence_class") is not None:
                return [], missing, True
            if row.get("carrier_path") is not None or row.get("carrier_sha256") is not None:
                return [], missing, True
            missing = True
            continue
        if status != "MEASURED":
            return [], missing, True
        value = row.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return [], missing, True
        if row.get("evidence_class") not in _EVIDENCE_CLASSES or row.get("evidence_class") != "MEASURED":
            return [], missing, True
        if not isinstance(row.get("unit"), str) or not row["unit"].strip() or row["unit"] == "n/a":
            return [], missing, True
        if not isinstance(row.get("carrier_path"), str) or not row["carrier_path"].strip():
            return [], missing, True
        if not _valid_digest(row.get("carrier_sha256")):
            return [], missing, True
        values.append(float(value))
    if expected_repetitions is not None:
        if (isinstance(expected_repetitions, bool) or not isinstance(expected_repetitions, int)
                or expected_repetitions < 1 or expected_repetitions > _MAX_REPETITIONS):
            return [], missing, True
        if seen != set(range(1, expected_repetitions + 1)):
            return [], True, False
    return values, missing, False


def decide(*, bounds: Mapping[str, float], observations: Mapping[str, Any],
           classification: Mapping[str, Any], dependency_heads: Mapping[str, Any],
           freeze_digest: str, workload_digest: str, config_digest: str,
           fault_schedule_digest: str,
           expected_repetitions: Mapping[str, int] | None = None,
           unmet_preconditions: tuple[str, ...] = (),
           policy_decision: str = "ALLOW", crossing_reproduced: bool = True,
           protocol_valid: bool = True, evidence_valid: bool = False) -> DecisionResult:
    """Apply BR-1..BR-9 to frozen, current-run-bound evidence.

    ``classification`` must be derived from verified preregistration data. No
    request-provided mechanism or class selection is accepted here.
    """
    if unmet_preconditions:
        return _result(Disposition.PRECONDITION_UNMET,
                       f"unmet preconditions: {','.join(map(str, unmet_preconditions))}")
    if policy_decision != "ALLOW" or not evidence_valid:
        return _result(Disposition.RUN_INVALID_POLICY_OR_IDENTITY,
                       "policy, identity, or evidence authority is invalid")
    if not protocol_valid:
        return _result(Disposition.PROTOCOL_INVALID,
                       "protocol, coverage, or evidence-shape validation failed")
    if (not isinstance(bounds, Mapping) or not bounds or not isinstance(observations, Mapping) or
            not isinstance(classification, Mapping) or not _valid_heads(dependency_heads) or
            not all(_valid_digest(x) for x in (freeze_digest, workload_digest, config_digest, fault_schedule_digest))):
        return _result(Disposition.PROTOCOL_INVALID, "required frozen identities or metric mappings are invalid")

    checked_bounds: dict[str, float] = {}
    for metric_id, bound in bounds.items():
        if (not isinstance(metric_id, str) or not metric_id.strip() or isinstance(bound, bool) or
                not isinstance(bound, (int, float)) or not math.isfinite(bound) or bound < 0):
            return _result(Disposition.PROTOCOL_INVALID, "metric identity or bound is invalid")
        checked_bounds[metric_id] = float(bound)

    crossing: list[DeficitClass] = []
    carrier_missing = False
    for metric_id, bound in checked_bounds.items():
        if metric_id not in observations:
            carrier_missing = True
            continue
        if expected_repetitions is not None:
            try:
                expected = expected_repetitions.get(metric_id)
            except (KeyError, TypeError, AttributeError):
                return _result(Disposition.PROTOCOL_INVALID,
                               "expected repetition map is not a valid mapping")
        else:
            expected = None
        values, missing, malformed = _carrier_state(
            observations[metric_id], metric_id=metric_id, dependency_heads=dependency_heads,
            freeze_digest=freeze_digest, workload_digest=workload_digest,
            config_digest=config_digest, fault_schedule_digest=fault_schedule_digest,
            expected_repetitions=expected,
        )
        if malformed:
            return _result(Disposition.PROTOCOL_INVALID,
                           f"metric carrier binding invalid for {metric_id}")
        carrier_missing |= missing
        if not values or all(value <= bound for value in values):
            continue
        try:
            mapped = classification.get(metric_id)
        except (KeyError, TypeError, AttributeError):
            return _result(Disposition.PROTOCOL_INVALID,
                           "frozen deficit classification is not a valid mapping")
        if isinstance(mapped, DeficitClass):
            crossing.append(mapped)
        elif isinstance(mapped, (tuple, list, set, frozenset)) and mapped and all(isinstance(item, DeficitClass) for item in mapped):
            crossing.extend(mapped)
        else:
            return _result(Disposition.CLASSIFICATION_AMBIGUOUS,
                           f"no single valid frozen deficit class for {metric_id}")

    if crossing and carrier_missing:
        return _result(Disposition.INSUFFICIENT_OBSERVABILITY,
                       "at least one required current metric carrier is missing")
    if not crossing:
        if carrier_missing:
            return _result(Disposition.INSUFFICIENT_OBSERVABILITY,
                           "one or more preregistered metric carriers are absent")
        return _result(Disposition.NO_DEFICIT_OBSERVED,
                       "the simpler design met every preregistered bound")
    if not crossing_reproduced:
        return _result(Disposition.DEFICIT_NOT_REPRODUCED, "the crossing did not reproduce")
    distinct = set(crossing)
    if len(distinct) != 1:
        return _result(Disposition.CLASSIFICATION_AMBIGUOUS,
                       "more than one deficit class survived falsification")
    deficit_class = next(iter(distinct))
    if deficit_class is DeficitClass.C7:
        return _result(Disposition.INSUFFICIENT_OBSERVABILITY,
                       "observability deficit terminates at BR-7 and justifies no mechanism")
    mapped = MECHANISM_BY_CLASS.get(deficit_class, ())
    if not mapped:
        return _result(Disposition.NO_MECHANISM_MAPPED,
                       f"no listed mechanism addresses {deficit_class.value}")
    return _result(Disposition.MECHANISM_ELIGIBLE_FOR_LATER_EVALUATION,
                   "a separate authorized preregistered comparison is required; adoption remains false",
                   eligible=mapped[0])
