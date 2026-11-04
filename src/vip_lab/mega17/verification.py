"""MEGA-17 Cross-Workstream Report Verification & Foreign-Key Validator."""

from __future__ import annotations

from typing import Any, Mapping

from vip_lab.common import (
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)
from vip_lab.mega17.canonical_integration import verify_canonical_integration_readiness
from vip_lab.mega17.editorial_readiness import verify_editorial_workflow_readiness_packet
from vip_lab.mega17.gate0_readiness import verify_gate0_experiment_readiness_receipt
from vip_lab.mega17.orchestrator import (
    MATURITY_LEVELS,
    MEGA17_REPORT_SCHEMA_VERSION,
    MEGA_17_SPEC_VERSION,
    Mega17ProductReadinessReport,
)
from vip_lab.mega17.release_readiness import verify_release_readiness_verification_packet
from vip_lab.mega17.source_readiness import verify_source_readiness_packet


EXPECTED_READINESS_DIMENSIONS: dict[str, bool] = {
    "software_available": True,
    "synthetic_tests_authored": True,
    "hosted_ci_verified": False,
    "canonical_integration_verified": False,
    "real_media_authorized": False,
    "real_experiment_executed": False,
    "human_evidence_observed": False,
    "production_export_authorized": False,
}


def verify_mega17_product_readiness_report(
    report: Mega17ProductReadinessReport | Mapping[str, Any],
) -> dict[str, Any]:
    """Verify schema, sub-packets, foreign-key digests, maturity ceilings, and report digest."""
    raw = (
        report.to_dict()
        if isinstance(report, Mega17ProductReadinessReport)
        else dict(report)
    )
    if raw.get("schema_version") != MEGA17_REPORT_SCHEMA_VERSION:
        raise VipLabError(
            "MEGA17_REPORT_SCHEMA_MISMATCH",
            f"Expected {MEGA17_REPORT_SCHEMA_VERSION}, got {raw.get('schema_version')!r}",
        )
    if raw.get("spec_version") != MEGA_17_SPEC_VERSION:
        raise VipLabError(
            "MEGA17_REPORT_SPEC_VERSION_MISMATCH",
            f"Expected {MEGA_17_SPEC_VERSION}, got {raw.get('spec_version')!r}",
        )

    dims = raw.get("readiness_dimensions")
    if not isinstance(dims, Mapping) or dict(dims) != EXPECTED_READINESS_DIMENSIONS:
        raise VipLabError(
            "MEGA17_READINESS_DIMENSIONS_VIOLATION",
            f"readiness_dimensions violated mandatory Section 11 truth values: {dims!r}",
        )

    ws_mat = raw.get("workstream_maturity")
    if not isinstance(ws_mat, Mapping) or not ws_mat:
        raise VipLabError(
            "MEGA17_WORKSTREAM_MATURITY_INVALID",
            "workstream_maturity must be a non-empty mapping",
        )
    for ws_k, mat_v in ws_mat.items():
        if mat_v not in MATURITY_LEVELS:
            raise VipLabError(
                "MEGA17_MATURITY_LEVEL_UNKNOWN",
                f"Unknown maturity level {mat_v!r} for {ws_k!r}",
            )
        # Newly authored MEGA-17 workstreams in AI Studio must not claim M3/M4/M5 before hosted CI
        if mat_v in (
            "M3_HOSTED_SYNTHETIC_VERIFIED",
            "M4_AUTHORIZED_LOCAL_VALIDATED",
            "M5_GATE_EVIDENCE_COMPLETE",
        ):
            raise VipLabError(
                "MEGA17_MATURITY_CEILING_EXCEEDED",
                f"Workstream {ws_k!r} cannot claim {mat_v!r} before hosted CI / real execution.",
            )

    gate_mat = raw.get("gate_maturity")
    if not isinstance(gate_mat, Mapping) or not gate_mat:
        raise VipLabError(
            "MEGA17_GATE_MATURITY_INVALID",
            "gate_maturity must be a non-empty mapping",
        )
    for g_k, g_v in gate_mat.items():
        if g_v not in MATURITY_LEVELS or g_v in (
            "M4_AUTHORIZED_LOCAL_VALIDATED",
            "M5_GATE_EVIDENCE_COMPLETE",
        ):
            raise VipLabError(
                "MEGA17_GATE_MATURITY_CEILING_EXCEEDED",
                f"Gate {g_k!r} cannot claim {g_v!r} in synthetic LAB mode.",
            )

    ws_a_dict = verify_canonical_integration_readiness(raw.get("workstream_a", {}))
    ws_b_dict = verify_source_readiness_packet(raw.get("workstream_b", {}))
    ws_c_dict = verify_gate0_experiment_readiness_receipt(raw.get("workstream_c", {}))
    ws_d_dict = verify_editorial_workflow_readiness_packet(raw.get("workstream_d", {}))
    ws_e_dict = verify_release_readiness_verification_packet(raw.get("workstream_e", {}))

    stage_digests = raw.get("stage_digests")
    if not isinstance(stage_digests, Mapping):
        raise VipLabError(
            "MEGA17_STAGE_DIGESTS_MISSING",
            "stage_digests must be a mapping",
        )

    expected_stage_links = {
        "workstream_a_digest": ws_a_dict["packet_digest"],
        "workstream_b_digest": ws_b_dict["packet_digest"],
        "workstream_c_digest": ws_c_dict["receipt_digest"],
        "workstream_d_digest": ws_d_dict["packet_digest"],
        "workstream_e_digest": ws_e_dict["packet_digest"],
        "mega15_preparation_packet_digest": ws_d_dict["consumed_mega15_summary"][
            "preparation_packet_digest"
        ],
        "mega15_lineage_receipt_digest": ws_d_dict["consumed_mega15_summary"][
            "mega15_lineage_receipt_digest"
        ],
        "mega16_render_preflight_digest": ws_e_dict["consumed_mega16_summary"][
            "render_preflight_digest"
        ],
        "mega16_qc_bundle_digest": ws_e_dict["consumed_mega16_summary"]["qc_bundle_digest"],
        "mega16_release_refusal_digest": ws_e_dict["consumed_mega16_summary"][
            "release_refusal_certificate_digest"
        ],
        "mega15_16_offline_report_digest": ws_e_dict["consumed_mega16_summary"][
            "mega15_16_report_digest"
        ],
    }

    for key, exp_val in expected_stage_links.items():
        actual_val = stage_digests.get(key)
        if actual_val != exp_val:
            raise VipLabError(
                "MEGA17_FOREIGN_DIGEST_MISMATCH",
                f"stage_digests[{key!r}] mismatch: {actual_val!r} != {exp_val!r}",
                field_path=f"stage_digests.{key}",
            )

    declared_digest = validate_hex_digest(
        str(raw.get("report_digest", "")),
        field_name="report_digest",
    )
    body = {k: v for k, v in raw.items() if k != "report_digest"}
    computed = canonical_sha256(body)
    if declared_digest != computed:
        raise VipLabError(
            "MEGA17_REPORT_DIGEST_MISMATCH",
            f"report_digest mismatch: declared {declared_digest} != computed {computed}",
        )
    return raw
