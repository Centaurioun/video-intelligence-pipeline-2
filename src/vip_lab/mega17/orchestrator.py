"""MEGA-17 Cross-Workstream Product-Readiness Orchestrator.

Connects Workstreams A, B, C, D, and E into one deterministic, generated-only
integration chain over both single-arm and three-arm LAB retrieval configurations,
producing a versioned, digest-verified ``Mega17ProductReadinessReport``.

Explicitly distinguishes the 8 mandatory readiness dimensions (Section 11):
- ``software_available = True``
- ``synthetic_tests_authored = True``
- ``hosted_ci_verified = False``
- ``canonical_integration_verified = False``
- ``real_media_authorized = False``
- ``real_experiment_executed = False``
- ``human_evidence_observed = False``
- ``production_export_authorized = False``

And tracks the 6 maturity levels (Section 12):
- ``M0_NOT_STARTED``
- ``M1_CONTRACT_DEFINED``
- ``M2_SYNTHETIC_IMPLEMENTED``
- ``M3_HOSTED_SYNTHETIC_VERIFIED``
- ``M4_AUTHORIZED_LOCAL_VALIDATED``
- ``M5_GATE_EVIDENCE_COMPLETE``
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from vip_lab.common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
    canonical_sha256,
)
from vip_lab.mega14.scenario import (
    SyntheticLabScenario,
    default_three_arm_scenario,
    parse_e2e_scenario_mapping,
)
from vip_lab.mega16.release_refusal import run_mega15_16_offline_pipeline
from vip_lab.mega17.canonical_integration import (
    CanonicalIntegrationReadinessPacket,
    build_canonical_integration_readiness,
)
from vip_lab.mega17.editorial_readiness import (
    EditorialWorkflowReadinessPacket,
    build_editorial_workflow_readiness_packet,
)
from vip_lab.mega17.gate0_readiness import (
    Gate0ExperimentReadinessReceipt,
    build_gate0_experiment_readiness_receipt,
)
from vip_lab.mega17.release_readiness import (
    ReleaseReadinessVerificationPacket,
    build_release_readiness_verification_packet,
)
from vip_lab.mega17.source_readiness import (
    SourceReadinessPacket,
    build_source_readiness_packet,
)


STAGE_ID = "MEGA-17.CROSS_WORKSTREAM_PRODUCT_READINESS"
MEGA_17_SPEC_VERSION = "LAB-MEGA-17-v1.0.0"
MEGA17_REPORT_SCHEMA_VERSION = "vip_lab.mega17.product_readiness_report.v1"

MATURITY_LEVELS: tuple[str, ...] = (
    "M0_NOT_STARTED",
    "M1_CONTRACT_DEFINED",
    "M2_SYNTHETIC_IMPLEMENTED",
    "M3_HOSTED_SYNTHETIC_VERIFIED",
    "M4_AUTHORIZED_LOCAL_VALIDATED",
    "M5_GATE_EVIDENCE_COMPLETE",
)


def _validate_mega15_16_scenario_lineage(
    scenario: SyntheticLabScenario,
    preparation_packet: Any,
) -> None:
    """Require complete query/source/arm membership for the selected scenario."""
    query_rows = preparation_packet.query_identities
    occurrence_rows = preparation_packet.occurrence_identities
    temporal_records = preparation_packet.temporal_records

    query_by_item = {
        row["queue_item_id"]: (row["query_id"], row["query_text"])
        for row in query_rows
    }
    occurrence_by_item = {
        row["queue_item_id"]: (
            row["revision_id"],
            row["content_id"],
            row["source_path"],
            row["source_sha256"],
        )
        for row in occurrence_rows
    }
    arm_by_item = {record.queue_item_id: record.arm_id for record in temporal_records}
    item_ids = set(query_by_item)
    actual_arms = set(arm_by_item.values())
    expected_arm_count = 1 if scenario.mode == "SINGLE_ARM" else 3

    if (
        len(query_by_item) != len(query_rows)
        or len(occurrence_by_item) != len(occurrence_rows)
        or len(arm_by_item) != len(temporal_records)
        or set(occurrence_by_item) != item_ids
        or set(arm_by_item) != item_ids
        or len(actual_arms) != expected_arm_count
    ):
        raise VipLabError(
            "MEGA17_UPSTREAM_SCENARIO_MISMATCH",
            "MEGA-15/16 queue-item, query, occurrence, or arm lineage is incomplete or duplicated.",
        )

    actual_membership = Counter(
        (
            query_by_item[item_id],
            occurrence_by_item[item_id],
            arm_by_item[item_id],
        )
        for item_id in item_ids
    )
    expected_membership = Counter(
        (
            (str(query["query_id"]), str(query["text"])),
            (
                str(source["revision_id"]),
                str(source["content_id"]),
                str(source["source_path"]),
                str(source["source_sha256"]),
            ),
            arm_id,
        )
        for query in scenario.queries
        for source in scenario.sources[: scenario.top_k]
        for arm_id in actual_arms
    )
    if actual_membership != expected_membership:
        raise VipLabError(
            "MEGA17_UPSTREAM_SCENARIO_MISMATCH",
            "MEGA-15/16 candidate lineage does not preserve the scenario's complete query/source/arm membership.",
        )


@dataclass(frozen=True)
class Mega17ProductReadinessReport:
    """Immutable cross-workstream MEGA-17 product-readiness report."""

    schema_version: str
    spec_version: str
    report_id: str
    scenario_id: str
    mode: str
    status: str
    workspace_git_sha: str
    declared_lab_baseline_sha: str
    canonical_reference_sha: str
    readiness_dimensions: Mapping[str, bool]
    workstream_maturity: Mapping[str, str]
    gate_maturity: Mapping[str, str]
    workstream_a: CanonicalIntegrationReadinessPacket
    workstream_b: SourceReadinessPacket
    workstream_c: Gate0ExperimentReadinessReceipt
    workstream_d: EditorialWorkflowReadinessPacket
    workstream_e: ReleaseReadinessVerificationPacket
    stage_digests: Mapping[str, str]
    report_digest: str

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "spec_version": self.spec_version,
            "report_id": self.report_id,
            "scenario_id": self.scenario_id,
            "mode": self.mode,
            "status": self.status,
            "workspace_git_sha": self.workspace_git_sha,
            "declared_lab_baseline_sha": self.declared_lab_baseline_sha,
            "canonical_reference_sha": self.canonical_reference_sha,
            "readiness_dimensions": dict(self.readiness_dimensions),
            "workstream_maturity": dict(self.workstream_maturity),
            "gate_maturity": dict(self.gate_maturity),
            "workstream_a": self.workstream_a.to_dict(),
            "workstream_b": self.workstream_b.to_dict(),
            "workstream_c": self.workstream_c.to_dict(),
            "workstream_d": self.workstream_d.to_dict(),
            "workstream_e": self.workstream_e.to_dict(),
            "stage_digests": dict(self.stage_digests),
        }

    def to_dict(self) -> dict[str, Any]:
        out = self.payload_without_digest()
        out["report_digest"] = self.report_digest
        return out


def run_mega17_product_readiness_chain(
    scenario: SyntheticLabScenario | Mapping[str, Any] | None = None,
    *,
    workspace_root: str | Path | None = None,
) -> Mega17ProductReadinessReport:
    """Execute the deterministic 5-workstream MEGA-17 product-readiness chain."""
    from vip_lab.mega17.verification import verify_mega17_product_readiness_report

    if scenario is None:
        scen = default_three_arm_scenario()
    elif isinstance(scenario, SyntheticLabScenario):
        scen = scenario
    else:
        scen = parse_e2e_scenario_mapping(scenario)

    root_path = (
        Path(workspace_root).resolve()
        if workspace_root is not None
        else Path(__file__).resolve().parents[3]
    )

    # Run upstream MEGA-14/15/16 offline pipeline once so Workstreams D and E share the exact same lineage
    mega15_16_rep = run_mega15_16_offline_pipeline(scenario=scen)
    upstream_packet = mega15_16_rep.preparation_packet
    _validate_mega15_16_scenario_lineage(scen, upstream_packet)

    ws_a = build_canonical_integration_readiness(root_path)
    ws_b = build_source_readiness_packet()
    ws_c = build_gate0_experiment_readiness_receipt()
    ws_d = build_editorial_workflow_readiness_packet(
        mega15_16_report=mega15_16_rep,
        scenario=scen,
        workspace_root=root_path,
    )
    ws_e = build_release_readiness_verification_packet(
        mega15_16_report=mega15_16_rep,
        scenario=scen,
        workspace_root=root_path,
    )

    readiness_dimensions = {
        "software_available": True,
        "synthetic_tests_authored": True,
        "hosted_ci_verified": False,
        "canonical_integration_verified": False,
        "real_media_authorized": False,
        "real_experiment_executed": False,
        "human_evidence_observed": False,
        "production_export_authorized": False,
    }

    workstream_maturity = {
        "WORKSTREAM_A_CANONICAL_INTEGRATION": "M2_SYNTHETIC_IMPLEMENTED",
        "WORKSTREAM_B_SOURCE_AND_D2_READINESS": "M2_SYNTHETIC_IMPLEMENTED",
        "WORKSTREAM_C_GATE0_EXPERIMENT_READINESS": "M2_SYNTHETIC_IMPLEMENTED",
        "WORKSTREAM_D_EDITORIAL_WORKFLOW_READINESS": "M2_SYNTHETIC_IMPLEMENTED",
        "WORKSTREAM_E_RELEASE_AND_QC_READINESS": "M2_SYNTHETIC_IMPLEMENTED",
    }

    gate_maturity = {
        "GATE_0_DIAGNOSTIC_RETRIEVAL": "M3_HOSTED_SYNTHETIC_VERIFIED",
        "GATE_1_REPRESENTATION_BENCHMARK": "M3_HOSTED_SYNTHETIC_VERIFIED",
        "GATE_2_RELIABILITY_AND_SCALE": "M3_HOSTED_SYNTHETIC_VERIFIED",
        "GATE_3_EDITING_AND_QC": "M3_HOSTED_SYNTHETIC_VERIFIED",
    }

    stage_digests = {
        "workstream_a_digest": ws_a.packet_digest,
        "workstream_b_digest": ws_b.packet_digest,
        "workstream_c_digest": ws_c.receipt_digest,
        "workstream_d_digest": ws_d.packet_digest,
        "workstream_e_digest": ws_e.packet_digest,
        "mega15_preparation_packet_digest": mega15_16_rep.preparation_packet.packet_digest,
        "mega15_lineage_receipt_digest": mega15_16_rep.mega15_lineage_receipt.receipt_digest,
        "mega16_render_preflight_digest": (
            mega15_16_rep.render_specification.specification_digest
        ),
        "mega16_qc_bundle_digest": mega15_16_rep.qc_requirements_bundle.bundle_digest,
        "mega16_release_refusal_digest": (
            mega15_16_rep.release_refusal_certificate.certificate_digest
        ),
        "mega15_16_offline_report_digest": mega15_16_rep.report_digest,
    }

    report_id_seed = canonical_sha256(
        {
            "scenario_id": scen.scenario_id,
            "mode": scen.mode,
            "stage_digests": stage_digests,
        }
    )[:16]

    provisional = Mega17ProductReadinessReport(
        schema_version=MEGA17_REPORT_SCHEMA_VERSION,
        spec_version=MEGA_17_SPEC_VERSION,
        report_id=f"m17-rep-{report_id_seed}",
        scenario_id=scen.scenario_id,
        mode=scen.mode,
        status=ReadinessStatus.READY_SYNTHETIC.value,
        workspace_git_sha=ws_a.workspace_git_sha,
        declared_lab_baseline_sha=ws_a.declared_lab_baseline_sha,
        canonical_reference_sha=ws_a.canonical_reference_sha,
        readiness_dimensions=readiness_dimensions,
        workstream_maturity=workstream_maturity,
        gate_maturity=gate_maturity,
        workstream_a=ws_a,
        workstream_b=ws_b,
        workstream_c=ws_c,
        workstream_d=ws_d,
        workstream_e=ws_e,
        stage_digests=stage_digests,
        report_digest="0" * 64,
    )
    digest = canonical_sha256(provisional.payload_without_digest())
    final_rep = Mega17ProductReadinessReport(
        schema_version=provisional.schema_version,
        spec_version=provisional.spec_version,
        report_id=provisional.report_id,
        scenario_id=provisional.scenario_id,
        mode=provisional.mode,
        status=provisional.status,
        workspace_git_sha=provisional.workspace_git_sha,
        declared_lab_baseline_sha=provisional.declared_lab_baseline_sha,
        canonical_reference_sha=provisional.canonical_reference_sha,
        readiness_dimensions=provisional.readiness_dimensions,
        workstream_maturity=provisional.workstream_maturity,
        gate_maturity=provisional.gate_maturity,
        workstream_a=provisional.workstream_a,
        workstream_b=provisional.workstream_b,
        workstream_c=provisional.workstream_c,
        workstream_d=provisional.workstream_d,
        workstream_e=provisional.workstream_e,
        stage_digests=provisional.stage_digests,
        report_digest=digest,
    )
    verify_mega17_product_readiness_report(final_rep)
    return final_rep


def inspect_mega17_product_readiness(
    payload: Mapping[str, Any] | None = None,
) -> ReadinessPacket:
    """Top-level MEGA-17 readiness inspector enforcing cross-workstream authority boundaries."""
    raw_payload = dict(payload) if isinstance(payload, Mapping) else {}
    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(raw_payload)

    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        blockers.append("MEGA17_UNTRUSTED_AUTHORITY_ESCALATION_REFUSED")
        findings.append(
            ReadinessFinding(
                code="MEGA17_UNTRUSTED_AUTHORITY_ESCALATION_REFUSED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Ignored and refused untrusted authority flags in MEGA-17 payload.",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(raw_payload.get("claim_production_export_authorized", False)):
        code = "MEGA17_PRODUCTION_EXPORT_NOT_AUTHORIZED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Production export is strictly refused in MEGA-17 preparation mode.",
            )
        )

    ws_root = cleaned.get("workspace_root")
    rep = run_mega17_product_readiness_chain(workspace_root=ws_root)

    has_auth_refusal = any(f.status == ReadinessStatus.NOT_AUTHORIZED for f in findings)
    if has_auth_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("MEGA17_FIVE_WORKSTREAM_SYNTHETIC_READINESS_VERIFIED")
        findings.append(
            ReadinessFinding(
                code="MEGA17_FIVE_WORKSTREAM_SYNTHETIC_READINESS_VERIFIED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Verified all 5 MEGA-17 workstreams; real execution, human review, and production export remain refused/unexecuted.",
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_AUTHORIZED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "report_id": rep.report_id,
            "report_digest": rep.report_digest,
            "readiness_dimensions": dict(rep.readiness_dimensions),
            "workstream_maturity": dict(rep.workstream_maturity),
            "gate_maturity": dict(rep.gate_maturity),
            "stage_digests": dict(rep.stage_digests),
        },
    )
