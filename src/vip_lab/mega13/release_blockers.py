"""Deterministic release and export blocker enumeration for MEGA-13."""

from __future__ import annotations

from typing import Any, Mapping

from vip_lab.common import NOT_OBSERVED, ReadinessPacket, canonical_sha256
from vip_lab.mega13.lineage_audit import LineageAuditReceipt

CANONICAL_RELEASE_BLOCKER_CODES: tuple[str, ...] = (
    "GATE0_D3_REAL_CORPUS_EXPERIMENT_PENDING",
    "GATE1_AUTHENTIC_MODEL_BENCHMARK_PENDING",
    "GATE2_REAL_ARCHIVE_WORKLOAD_PENDING",
    "GATE3_A7_S5_BOUNDED_ADMISSION_PENDING",
    "GATE3_SOURCE_NATIVE_PTS_MEASUREMENT_NOT_OBSERVED",
    "GATE3_HUMAN_EDITORIAL_DECISION_NOT_OBSERVED",
    "GATE3_TECHNICAL_AND_EDITORIAL_QC_NOT_OBSERVED",
    "GATE3_PRODUCTION_EXPORT_NOT_AUTHORIZED",
)


def build_release_blocker_summary(
    *,
    lineage_receipt: LineageAuditReceipt | Mapping[str, Any] | None,
    qc_packet: ReadinessPacket,
) -> dict[str, Any]:
    receipt_dict = (
        lineage_receipt.to_dict()
        if isinstance(lineage_receipt, LineageAuditReceipt)
        else (dict(lineage_receipt) if isinstance(lineage_receipt, Mapping) else None)
    )
    active_blockers = list(CANONICAL_RELEASE_BLOCKER_CODES)
    for b in qc_packet.blockers:
        if b not in active_blockers:
            active_blockers.append(b)

    body: dict[str, Any] = {
        "lineage_valid": bool(receipt_dict and receipt_dict.get("lineage_valid") is True),
        "lineage_receipt_digest": (
            receipt_dict.get("receipt_digest") if receipt_dict is not None else None
        ),
        "qc_stage_status": qc_packet.status.value,
        "qc_state": NOT_OBSERVED,
        "technical_qc_evidence": NOT_OBSERVED,
        "editorial_qc_evidence": NOT_OBSERVED,
        "preview_eligible": False,
        "production_export_authorized": False,
        "export_status": "REFUSED_NOT_AUTHORIZED",
        "release_blockers": active_blockers,
    }
    body["summary_digest"] = canonical_sha256(body)
    return body
