"""Versioned, local/synthetic-only report envelope."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA_VERSION = "vip_fvs.pilot_report.v1"
EVIDENCE_CLASSES = ("MEASURED", "MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED", "EDITORIAL_INFERENCE")
NOT_OBSERVED = "NOT_OBSERVED"
SYNTHETIC_SCOPE = "LOCAL_SYNTHETIC_ONLY"
SYNTHETIC_LABEL = "SYNTHETIC_PLUMBING_ONLY"
DEFAULT_NON_CLAIMS = ("real-media quality", "archive-wide quality or coverage", "production latency, throughput, or capacity", "provider/cloud inference behavior", "frame-accurate editorial suitability")

class PilotReportError(ValueError):
    """Raised when a report violates the versioned pilot contract."""

def _text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PilotReportError(f"{name} must be a non-empty string")
    return value.strip()

def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not value == value or value in (float("inf"), float("-inf")):
            raise PilotReportError("metric value must be finite")
        return value
    raise PilotReportError("report values must be JSON-compatible scalars or null")

@dataclass(frozen=True)
class Observation:
    """Legacy typed observation retained for callers of the original API."""
    metric_id: str
    value: Any
    unit: str | None
    evidence_class: str
    status: str = "OBSERVED"
    note: str | None = None
    def __post_init__(self) -> None:
        _text("metric_id", self.metric_id)
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise PilotReportError(f"unsupported evidence class: {self.evidence_class}")
        if self.status not in {"OBSERVED", NOT_OBSERVED}:
            raise PilotReportError("status must be OBSERVED or NOT_OBSERVED")
        if self.status == NOT_OBSERVED and self.value is not None:
            raise PilotReportError("NOT_OBSERVED observations must have a null value")
        if self.status == "OBSERVED" and self.value is None:
            raise PilotReportError("OBSERVED observations must have a value")
        _json_value(self.value)
    def to_dict(self) -> dict[str, Any]:
        row = {"metric_id": self.metric_id, "value": self.value, "unit": self.unit, "evidence_class": self.evidence_class, "status": self.status}
        if self.note is not None:
            row["note"] = self.note
        return row

def observation(metric_id: str, value: Any = None, *, unit: str | None = None, evidence_class: str = "MEASURED", status: str | None = None, note: str | None = None) -> Observation:
    return Observation(metric_id, value, unit, evidence_class, NOT_OBSERVED if value is None else (status or "OBSERVED"), note)

class PilotReport(dict):
    """Mapping report with properties used by the pre-existing dataclass API."""
    def __init__(self, payload: dict[str, Any], *, quality: tuple[Observation, ...] = (), performance: tuple[Observation, ...] = (), report_id: str = "", run_id: str = "") -> None:
        super().__init__(payload)
        self._quality, self._performance = quality, performance
        self.report_id, self.run_id, self.scope = report_id, run_id, payload["scope"]
        self.non_claims, self.NOT_OBSERVED = tuple(payload["non_claims"]), tuple(payload["NOT_OBSERVED"])
        self.export_eligible = False
    @property
    def quality(self) -> tuple[Observation, ...]: return self._quality
    @property
    def performance(self) -> tuple[Observation, ...]: return self._performance
    @property
    def schema_version(self) -> str: return self["schema"]
    def to_dict(self) -> dict[str, Any]: return dict(self)
    def to_json(self) -> str: return json.dumps(self, sort_keys=True, separators=(",", ":")) + "\n"

def _legacy_rows(values: Mapping[str, Any] | Sequence[Observation] | None) -> tuple[Observation, ...]:
    if values is None: return ()
    if isinstance(values, Mapping):
        rows = []
        for key, value in values.items():
            if isinstance(value, Observation): rows.append(value)
            elif isinstance(value, Mapping): rows.append(observation(str(key), value.get("value"), unit=value.get("unit"), evidence_class=value.get("evidence_class", "MEASURED"), status=value.get("status"), note=value.get("note")))
            else: rows.append(observation(str(key), value))
        return tuple(rows)
    rows = tuple(values)
    if any(not isinstance(row, Observation) for row in rows): raise PilotReportError("legacy observations must be Observation values")
    return rows

def build_pilot_report(*, run_id: str, source_identity: Mapping[str, Any] | None = None, generation_identity: Mapping[str, Any] | None = None, observations: Sequence[Mapping[str, Any]] | None = None, measurements: Mapping[str, Any] | None = None, synthetic: bool = True, quality: Mapping[str, Any] | Sequence[Observation] | None = None, performance: Mapping[str, Any] | Sequence[Observation] | None = None, report_id: str | None = None, non_claims: Sequence[str] = DEFAULT_NON_CLAIMS, not_observed: Sequence[str] = ()) -> PilotReport:
    """Build a deterministic local/synthetic report without runtime or network access."""
    run_id = _text("run_id", run_id)
    if synthetic is not True: raise PilotReportError("pilot reports require synthetic=True")
    source, generation = dict(source_identity or {}), dict(generation_identity or {})
    raw_observations = []
    for row in observations or ():
        if not isinstance(row, Mapping): raise PilotReportError("observations must be mappings")
        raw_observations.append(dict(row))
    raw_measurements = dict(measurements or {})
    configured = raw_measurements.get("query_count_configured")
    observed = [row for row in raw_observations if row.get("observed") is True and row.get("status") != NOT_OBSERVED]
    missing = list(not_observed)
    missing.extend(key for key, value in raw_measurements.items() if value is None and key not in missing)
    missing.extend(f"query:{row.get('query_id')}" for row in raw_observations if row.get("observed") is False and row.get("query_id") is not None)
    payload = {"schema": SCHEMA_VERSION, "run_label": SYNTHETIC_LABEL, "scope": SYNTHETIC_SCOPE, "synthetic": True, "quality_labels": list(EVIDENCE_CLASSES), "non_claims": list(non_claims), "identity": {"run_id": run_id, "source": source, "generation": generation}, "observations": raw_observations, "measurements": raw_measurements, "summary": {"observed_query_count": len(observed), "query_denominator": len(observed), "configured_query_count": configured}, "NOT_OBSERVED": sorted(set(missing))}
    legacy_quality, legacy_performance = _legacy_rows(quality), _legacy_rows(performance)
    if report_id is None:
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
        report_id = f"pilot-report-{digest}"
    return PilotReport(payload, quality=legacy_quality, performance=legacy_performance, report_id=_text("report_id", report_id), run_id=run_id)

__all__ = ["EVIDENCE_CLASSES", "NOT_OBSERVED", "Observation", "PilotReport", "PilotReportError", "SCHEMA_VERSION", "SYNTHETIC_SCOPE", "build_pilot_report", "observation"]
