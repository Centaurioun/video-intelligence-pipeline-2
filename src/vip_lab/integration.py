"""Packet PX: Cross-Gate Synthetic Integration & Program Summary.

Composes MEGA-03 (A-7 S5 / Stream-Identity / ReviewBundle), MEGA-04 (Gate-0),
MEGA-05 (Gate-1), MEGA-06 (Gate-2), and MEGA-07 (Gate-3) into a deterministic
multi-gate readiness summary.

Enforces:
- Upstream stage failures/blocks are surfaced explicitly in the program summary.
- Even when every synthetic stage reports ``READY_SYNTHETIC``, no gate is ever
  marked ``PASSED``/``APPROVED``, ``execution_authorized`` remains ``False``,
  ``authentic_model_execution`` remains ``False``, and
  ``production_export_authorized`` remains ``False``.
"""

from __future__ import annotations

from typing import Any, Mapping

from .common import (
    LAB_PROGRAM_VERSION,
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)
from .mega03 import (
    inspect_review_bundle_record,
    inspect_s5_declaration,
    inspect_stream_namespace,
)
from .mega04 import inspect_gate0_entry
from .mega05 import inspect_benchmark_entry
from .mega06 import (
    inspect_measurement_review,
    inspect_recovery_scenario,
    inspect_workload_plan,
)
from .mega07 import (
    inspect_candidate_temporal,
    inspect_editorial_lineage,
    inspect_qc_export_readiness,
)


STAGE_ID = "MEGA-CROSS-GATE.PROGRAM_SUMMARY"


def evaluate_mega03_composite(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Evaluate MEGA-03 composite (S5 declaration + optional stream namespace + optional ReviewBundle)."""
    if not isinstance(payload, Mapping):
        raise VipLabError("MEGA03_COMPOSITE_NOT_MAPPING", "payload must be a mapping")

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = ["PR_258_DIRECT_CODE_ABSENT_IN_SNAPSHOT"]
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")

    subpackets: dict[str, dict[str, Any]] = {}

    s5_decl = cleaned.get("s5_declaration", cleaned if "source_id" in cleaned else None)
    if isinstance(s5_decl, Mapping):
        s5_pkt = inspect_s5_declaration(
            s5_decl,
            snapshot_root=cleaned.get("snapshot_root"),
        )
        subpackets["s5_preflight"] = s5_pkt.to_dict()
        findings.extend(s5_pkt.findings)
        for b in s5_pkt.blockers:
            blockers.append(f"S5:{b}")
            reasons.append(f"S5:{b}")

    stream_ns = cleaned.get("stream_namespace")
    if isinstance(stream_ns, Mapping):
        ns_pkt = inspect_stream_namespace(stream_ns)
        subpackets["stream_identity_preflight"] = ns_pkt.to_dict()
        findings.extend(ns_pkt.findings)
        # Note: negative stream-identity preflight is expected to refuse unproven
        # metadata-only indices unless allow_negative_stream_refusal=True
        if ns_pkt.status != ReadinessStatus.READY_SYNTHETIC and not bool(
            cleaned.get("expect_negative_stream_refusal", False)
        ):
            for b in ns_pkt.blockers:
                blockers.append(f"STREAM:{b}")
                reasons.append(f"STREAM:{b}")

    rb_rec = cleaned.get("review_bundle")
    if isinstance(rb_rec, Mapping):
        rb_pkt = inspect_review_bundle_record(
            rb_rec,
            require_e01_binding=bool(cleaned.get("require_e01_binding", False)),
        )
        subpackets["review_bundle_check"] = rb_pkt.to_dict()
        findings.extend(rb_pkt.findings)
        for b in rb_pkt.blockers:
            blockers.append(f"REVIEW_BUNDLE:{b}")
            reasons.append(f"REVIEW_BUNDLE:{b}")

    if not subpackets:
        code = "MEGA03_NO_SUBSTAGE_PROVIDED"
        reasons.append(code)
        blockers.append(code)
        return ReadinessPacket(
            stage_id="MEGA-03.COMPOSITE",
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"subpackets": {}},
        )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        status = ReadinessStatus.INVALID
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("MEGA03_COMPOSITE_SYNTHETIC_READY")

    return ReadinessPacket(
        stage_id="MEGA-03.COMPOSITE",
        status=status,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "subpackets": subpackets,
            "pr258_status": "EXTERNAL_PR_NOT_MERGED_IN_SNAPSHOT",
        },
    )


def evaluate_mega06_composite(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Evaluate Gate-2 composite (workload_plan + recovery_scenario + measurement_review)."""
    if not isinstance(payload, Mapping):
        raise VipLabError("MEGA06_COMPOSITE_NOT_MAPPING", "payload must be a mapping")

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []
    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")

    subpackets: dict[str, dict[str, Any]] = {}

    wp = cleaned.get("workload_plan", cleaned.get("workload"))
    if isinstance(wp, Mapping):
        wp_pkt = inspect_workload_plan(wp)
        subpackets["workload_plan"] = wp_pkt.to_dict()
        findings.extend(wp_pkt.findings)
        for b in wp_pkt.blockers:
            blockers.append(f"WORKLOAD:{b}")
            reasons.append(f"WORKLOAD:{b}")

    rec = cleaned.get("recovery_scenario")
    if isinstance(rec, Mapping):
        rec_pkt = inspect_recovery_scenario(rec)
        subpackets["recovery_matrix"] = rec_pkt.to_dict()
        findings.extend(rec_pkt.findings)
        for b in rec_pkt.blockers:
            blockers.append(f"RECOVERY:{b}")
            reasons.append(f"RECOVERY:{b}")

    meas = cleaned.get("measurement_review")
    if isinstance(meas, Mapping):
        meas_pkt = inspect_measurement_review(meas)
        subpackets["measurement_review"] = meas_pkt.to_dict()
        findings.extend(meas_pkt.findings)
        for b in meas_pkt.blockers:
            blockers.append(f"MEASUREMENT:{b}")
            reasons.append(f"MEASUREMENT:{b}")

    if not subpackets:
        code = "MEGA06_NO_SUBSTAGE_PROVIDED"
        return ReadinessPacket(
            stage_id="MEGA-06.COMPOSITE",
            status=ReadinessStatus.INVALID,
            reasons=(code,),
            blockers=(code,),
            summary={"subpackets": {}},
        )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        status = ReadinessStatus.INVALID
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("MEGA06_COMPOSITE_SYNTHETIC_READY")

    return ReadinessPacket(
        stage_id="MEGA-06.COMPOSITE",
        status=status,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "subpackets": subpackets,
            "real_workload_evidence": NOT_OBSERVED,
            "mechanism_needed": "NOT_DETERMINED",
        },
    )


def evaluate_mega07_composite(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Evaluate Gate-3 composite (candidate_temporal + editorial_lineage + qc_export)."""
    if not isinstance(payload, Mapping):
        raise VipLabError("MEGA07_COMPOSITE_NOT_MAPPING", "payload must be a mapping")

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []
    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")

    subpackets: dict[str, dict[str, Any]] = {}

    ct = cleaned.get("candidate_temporal")
    if isinstance(ct, Mapping):
        ct_pkt = inspect_candidate_temporal(ct)
        subpackets["candidate_temporal"] = ct_pkt.to_dict()
        findings.extend(ct_pkt.findings)
        for b in ct_pkt.blockers:
            blockers.append(f"TEMPORAL:{b}")
            reasons.append(f"TEMPORAL:{b}")

    el = cleaned.get("editorial_lineage")
    if isinstance(el, Mapping):
        el_pkt = inspect_editorial_lineage(el)
        subpackets["editorial_lineage"] = el_pkt.to_dict()
        findings.extend(el_pkt.findings)
        for b in el_pkt.blockers:
            blockers.append(f"LINEAGE:{b}")
            reasons.append(f"LINEAGE:{b}")

    qc = cleaned.get("qc_export")
    if isinstance(qc, Mapping):
        qc_pkt = inspect_qc_export_readiness(qc)
        subpackets["qc_export"] = qc_pkt.to_dict()
        findings.extend(qc_pkt.findings)
        for b in qc_pkt.blockers:
            blockers.append(f"QC_EXPORT:{b}")
            reasons.append(f"QC_EXPORT:{b}")

    if not subpackets:
        code = "MEGA07_NO_SUBSTAGE_PROVIDED"
        return ReadinessPacket(
            stage_id="MEGA-07.COMPOSITE",
            status=ReadinessStatus.INVALID,
            reasons=(code,),
            blockers=(code,),
            summary={"subpackets": {}},
        )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        status = ReadinessStatus.INVALID
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("MEGA07_COMPOSITE_SYNTHETIC_READY")

    return ReadinessPacket(
        stage_id="MEGA-07.COMPOSITE",
        status=status,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "subpackets": subpackets,
            "production_export_authorized": False,
            "export_status": "REFUSED_NOT_AUTHORIZED",
        },
    )


def summarize_program(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Compose MEGA-03..MEGA-07 stage evaluations into a unified cross-gate summary."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "PROGRAM_SUMMARY_NOT_MAPPING",
            "payload must be a mapping",
        )

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = [
        "GIT_SNAPSHOT_NOT_OBSERVED_ZIP_IMPORT",
        "PR_258_DIRECT_CODE_ABSENT_IN_SNAPSHOT",
        "ALL_GATES_SYNTHETIC_PREFLIGHT_ONLY",
    ]
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="PROGRAM_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted top-level authority claims in program payload were stripped",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    stage_packets: dict[str, ReadinessPacket] = {}

    if isinstance(cleaned.get("mega03"), Mapping):
        stage_packets["MEGA-03"] = evaluate_mega03_composite(cleaned["mega03"])
    if isinstance(cleaned.get("mega04"), Mapping):
        stage_packets["MEGA-04"] = inspect_gate0_entry(cleaned["mega04"])
    if isinstance(cleaned.get("mega05"), Mapping):
        stage_packets["MEGA-05"] = inspect_benchmark_entry(cleaned["mega05"])
    if isinstance(cleaned.get("mega06"), Mapping):
        stage_packets["MEGA-06"] = evaluate_mega06_composite(cleaned["mega06"])
    if isinstance(cleaned.get("mega07"), Mapping):
        stage_packets["MEGA-07"] = evaluate_mega07_composite(cleaned["mega07"])

    if not stage_packets:
        code = "PROGRAM_NO_STAGES_PROVIDED"
        reasons.append(code)
        blockers.append(code)
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"stages": {}},
        )

    # Cross-gate dependency rule: if MEGA-03 is present and blocked/invalid,
    # MEGA-07 cannot be considered clean downstream.
    if (
        "MEGA-03" in stage_packets
        and stage_packets["MEGA-03"].status != ReadinessStatus.READY_SYNTHETIC
        and "MEGA-07" in stage_packets
    ):
        dep_code = "DOWNSTREAM_MEGA07_TAINTED_BY_MEGA03_BLOCKER"
        reasons.append(dep_code)
        blockers.append(dep_code)
        findings.append(
            ReadinessFinding(
                code=dep_code,
                status=ReadinessStatus.BLOCKED,
                message="MEGA-07 downstream stage tainted by upstream MEGA-03 blocker",
                field_path="mega07",
            )
        )

    stage_summaries: dict[str, Any] = {}
    stage_statuses: dict[str, str] = {}
    has_invalid = False

    for stage_name, pkt in stage_packets.items():
        stage_statuses[stage_name] = pkt.status.value
        stage_summaries[stage_name] = pkt.to_dict()
        if pkt.status == ReadinessStatus.INVALID:
            has_invalid = True
        if pkt.status != ReadinessStatus.READY_SYNTHETIC:
            for b in pkt.blockers:
                prefixed = f"{stage_name}:{b}"
                if prefixed not in blockers:
                    blockers.append(prefixed)
                    reasons.append(prefixed)

    if has_invalid:
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("CROSS_GATE_SYNTHETIC_PROGRAM_READY")

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_APPROVED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "program_version": LAB_PROGRAM_VERSION,
            "git_snapshot_identity": "NOT_OBSERVED (GIT_DIR_ABSENT)",
            "pr258_status": "EXTERNAL_PR_NOT_MERGED_IN_SNAPSHOT",
            "stage_statuses": stage_statuses,
            "stages": stage_summaries,
            "synthetic_only": True,
            "execution_authorized": False,
            "authentic_model_execution": False,
            "real_archive_observed": False,
            "production_export_authorized": False,
            "gate0_verdict": "NOT_RUN",
            "gate1_verdict": "NOT_AUTHORIZED",
            "gate2_verdict": "NOT_DETERMINED",
            "gate3_export_status": "REFUSED_NOT_AUTHORIZED",
        },
    )
