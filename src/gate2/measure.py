"""Typed, deterministic measurement records for Gate 2 evidence capture."""
from __future__ import annotations

import re
import statistics
import math
from dataclasses import dataclass, field
from typing import Any

from gate0.identity import digest_json

CANONICAL_EVIDENCE_CLASSES = frozenset({
    "MEASURED", "MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED",
    "EDITORIAL_INFERENCE",
})
_DECISION_LABEL = re.compile(
    r"(?<![A-Z0-9])(?:BR-[A-Z0-9_-]+|C[1-7]|T[1-9])(?![A-Z0-9])",
    re.IGNORECASE | re.ASCII,
)
_METRIC_ID_PLACEHOLDERS = frozenset({
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
})
_METRIC_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}$", re.ASCII)


def _valid_metric_id(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _METRIC_ID.fullmatch(value.strip()) is not None
        and not (value.strip().isascii() and value.strip().lower() in _METRIC_ID_PLACEHOLDERS)
    )


class _NotObserved:
    __slots__ = ()

    def __repr__(self) -> str:
        return "NOT_OBSERVED"

    def __bool__(self) -> bool:
        return False


NOT_OBSERVED = _NotObserved()


def _is_decision_label(value: Any) -> bool:
    return isinstance(value, str) and _DECISION_LABEL.search(value) is not None


@dataclass(frozen=True)
class Measurement:
    metric_id: str
    unit: str
    value: Any
    evidence_class: str | None
    derivation: str
    reason: str | None = None

    @classmethod
    def measured(cls, *, metric_id: str, value: Any, unit: str,
                 derivation: str, evidence_class: str = "MEASURED") -> "Measurement":
        if not _valid_metric_id(metric_id):
            raise ValueError("a measurement requires a descriptive metric identity")
        if not isinstance(unit, str) or not unit.strip():
            raise ValueError("a measurement requires a unit")
        if not isinstance(derivation, str) or not derivation.strip():
            raise ValueError("a measured value requires a stated derivation")
        if evidence_class not in CANONICAL_EVIDENCE_CLASSES:
            raise ValueError(f"invalid evidence class: {evidence_class!r}")
        if value is NOT_OBSERVED:
            raise ValueError("NOT_OBSERVED values use Measurement.not_observed")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("measurement values must be numeric")
        if not math.isfinite(value):
            raise ValueError("measurement values must be finite")
        if _is_decision_label(value):
            raise ValueError("a decision label may not stand in for a measurement")
        return cls(metric_id.strip(), unit.strip(), value, evidence_class, derivation.strip())

    @classmethod
    def not_observed(cls, *, metric_id: str, reason: str) -> "Measurement":
        if not _valid_metric_id(metric_id):
            raise ValueError("a NOT_OBSERVED value requires a descriptive metric identity")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("a NOT_OBSERVED value requires a stated reason")
        if _is_decision_label(reason.strip()):
            raise ValueError("a decision label may not serve as a NOT_OBSERVED reason")
        return cls(metric_id.strip(), "n/a", NOT_OBSERVED, None, "not measured", reason.strip())

    def to_dict(self) -> dict[str, Any]:
        result = {
            "metric_id": self.metric_id,
            "unit": self.unit,
            "value": None if self.value is NOT_OBSERVED else self.value,
            "derivation": self.derivation,
        }
        if self.value is NOT_OBSERVED:
            result["status"] = "NOT_OBSERVED"
            result["reason"] = self.reason
        else:
            result["evidence_class"] = self.evidence_class
        return result


@dataclass
class MeasurementSet:
    measurements: list[Measurement] = field(default_factory=list)

    def add(self, measurement: Measurement) -> None:
        if not isinstance(measurement, Measurement):
            raise TypeError("measurement set accepts Measurement records only")
        self.measurements.append(measurement)

    def measured(self) -> tuple[Measurement, ...]:
        return tuple(m for m in self.measurements if m.value is not NOT_OBSERVED)

    def not_observed(self) -> tuple[Measurement, ...]:
        return tuple(m for m in self.measurements if m.value is NOT_OBSERVED)

    def summarize(self, metric_id: str) -> dict[str, Any]:
        values = [m.value for m in self.measured() if m.metric_id == metric_id]
        if not values:
            raise ValueError(f"no measured values for {metric_id}")
        try:
            ordered = sorted(values)
            median = statistics.median(ordered)
            minimum, maximum = min(ordered), max(ordered)
        except TypeError as exc:
            raise ValueError("summary requires mutually comparable values") from exc
        return {
            "metric_id": metric_id,
            "n": len(values),
            "min": minimum,
            "median": median,
            "max": maximum,
            "is_distribution": len(values) >= 2,
        }

    def to_dict(self) -> dict[str, Any]:
        document = {
            "schema_version": "gate2.measurement.v1",
            "measured": [m.to_dict() for m in self.measured()],
            "not_observed": [m.to_dict() for m in self.not_observed()],
        }
        document["measurement_set_digest"] = digest_json(document)
        return document
