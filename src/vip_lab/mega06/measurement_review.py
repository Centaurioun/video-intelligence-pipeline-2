"""Packet P06c: Gate-2 Measurement & Mechanism-Justification Review.

Delegates to ``gate2.measure`` (``Measurement``, ``MeasurementSet``,
``CANONICAL_EVIDENCE_CLASSES``, ``NOT_OBSERVED``) and ``gate2.decision``
(``DeficitClass``, ``Disposition``, ``MECHANISMS``, ``decide``).

Enforces the strict Gate-2 synthetic-vs-authentic boundary:
- Synthetic generated observations never establish real host workload evidence,
  authentic model/runtime provenance, or production threshold suitability.
- Therefore ``real_workload_evidence="NOT_OBSERVED"``,
  ``model_runtime_provenance="NOT_OBSERVED"``,
  ``threshold_suitability="NOT_OBSERVED"``,
  ``mechanism_needed="NOT_DETERMINED"``, and ``approved_mechanisms=[]``.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from gate2.decision import MECHANISMS
from gate2.measure import (
    CANONICAL_EVIDENCE_CLASSES,
    NOT_OBSERVED as GATE2_NOT_OBSERVED,
    Measurement,
    MeasurementSet,
)

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-06.MEASUREMENT_REVIEW"


def inspect_measurement_review(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Validate Gate-2 measurements and refuse mechanism justification from synthetic runs."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "MEASUREMENT_REVIEW_NOT_MAPPING",
            "payload must be a mapping",
        )

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="MEASUREMENT_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted self-declared authority flags in measurement review were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(cleaned.get("claim_production_mechanism_justified", False)) or cleaned.get(
        "claimed_approved_mechanisms"
    ):
        code = "SYNTHETIC_WORKLOAD_CANNOT_JUSTIFY_MECHANISM"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=(
                    "Synthetic Gate-2 counters cannot justify ANN, queueing, caching, "
                    "index recovery, or additional services"
                ),
                field_path="claim_production_mechanism_justified",
            )
        )

    raw_measurements = cleaned.get("measurements", ())
    if not isinstance(raw_measurements, Sequence):
        code = "MEASUREMENT_LIST_NOT_SEQUENCE"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="measurements must be a sequence",
                field_path="measurements",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"mechanism_needed": "NOT_DETERMINED", "approved_mechanisms": []},
        )

    mset = MeasurementSet()
    for idx, item in enumerate(raw_measurements):
        if not isinstance(item, Mapping):
            code = "MEASUREMENT_ITEM_NOT_MAPPING"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message=f"measurements[{idx}] must be a mapping",
                    field_path=f"measurements[{idx}]",
                )
            )
            continue
        try:
            raw_status = str(item.get("status", "MEASURED"))
            raw_ev_class = item.get("evidence_class")
            if (
                raw_status == GATE2_NOT_OBSERVED
                or raw_ev_class == GATE2_NOT_OBSERVED
                or item.get("value") is None
            ):
                m = Measurement.not_observed(
                    metric_id=str(item.get("metric_id", "")),
                    reason=str(item.get("reason") or "synthetic_not_observed"),
                )
            else:
                # Accept legacy "OBSERVED" alias as "MEASURED" when value is numeric
                norm_status = "MEASURED" if raw_status in ("MEASURED", "OBSERVED") else raw_status
                if norm_status != "MEASURED":
                    raise ValueError(f"invalid status: {raw_status!r}")
                m = Measurement.measured(
                    metric_id=str(item.get("metric_id", "")),
                    value=item.get("value"),  # type: ignore[arg-type]
                    unit=str(item.get("unit", "")),
                    derivation=str(
                        item.get("derivation")
                        or item.get("provenance_digest")
                        or "synthetic_lab_declaration"
                    ),
                    evidence_class=str(raw_ev_class or "MEASURED"),
                )
            mset.add(m)
        except ValueError as exc:
            code = "MEASUREMENT_SCHEMA_VIOLATION"
            if code not in blockers:
                blockers.append(code)
                reasons.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message=str(exc),
                    field_path=f"measurements[{idx}]",
                )
            )

    if not blockers:
        reasons.append("SYNTHETIC_MEASUREMENT_ENVELOPE_VALID")
        reasons.append("MECHANISM_JUSTIFICATION_DEFERRED_TO_REAL_WORKLOAD")
        findings.append(
            ReadinessFinding(
                code="GATE2_SYNTHETIC_OBSERVATIONS_RECORDED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message=(
                    "Synthetic measurements validated; real workload evidence, runtime "
                    "provenance, and threshold suitability remain NOT_OBSERVED"
                ),
                details={
                    "measurement_count": len(mset.measurements),
                    "canonical_evidence_classes": sorted(CANONICAL_EVIDENCE_CLASSES),
                    "candidate_mechanisms": list(MECHANISMS),
                },
            )
        )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_AUTHORIZED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "measurement_count": len(mset.measurements),
            "synthetic_generated_only": True,
            "real_workload_evidence": NOT_OBSERVED,
            "model_runtime_provenance": NOT_OBSERVED,
            "threshold_suitability": NOT_OBSERVED,
            "mechanism_needed": "NOT_DETERMINED",
            "approved_mechanisms": [],
        },
    )
