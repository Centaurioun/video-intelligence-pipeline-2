"""Tests for MEGA-17 Workstream E: Render, Export, QC, and Release Readiness."""

from __future__ import annotations

import pytest

from vip_lab.common import ReadinessStatus, VipLabError
from vip_lab.mega17.release_readiness import (
    E12_NEGATIVE_REFUSAL_CONDITIONS,
    REFUSAL_DERIVED_RECEIPT_CANNOT_UPGRADE_PROVENANCE,
    REFUSAL_EXECUTABLE_FFMPEG_COMMAND_FORBIDDEN,
    SEVEN_RELEASE_WORKFLOW_STAGES,
    ReleaseReadinessVerificationPacket,
    build_release_readiness_verification_packet,
    evaluate_e12_negative_refusal_matrix,
    inspect_release_and_qc_readiness,
    verify_release_readiness_verification_packet,
)


def test_workstream_e_consumes_mega16_and_enforces_seven_stages_and_mandatory_flags() -> None:
    packet = build_release_readiness_verification_packet()
    assert isinstance(packet, ReleaseReadinessVerificationPacket)

    # Mandatory Section 10 flags
    assert packet.preview_executed is False
    assert packet.render_executed is False
    assert packet.technical_qc_observed == "NOT_OBSERVED"
    assert packet.visual_editorial_qc_observed == "NOT_OBSERVED"
    assert packet.audio_editorial_qc_observed == "NOT_OBSERVED"
    assert packet.production_export_authorized is False
    assert packet.export_status == "REFUSED_NOT_AUTHORIZED"

    # 7 distinct workflow stages
    assert set(packet.seven_stage_separation.keys()) == set(SEVEN_RELEASE_WORKFLOW_STAGES)
    assert len(SEVEN_RELEASE_WORKFLOW_STAGES) == 7
    assert (
        packet.seven_stage_separation["STAGE_1_PERMITTED_LOCAL_PREVIEW"]["executed"]
        is False
    )
    assert (
        packet.seven_stage_separation["STAGE_2_RENDER_PREPARATION"]["state"]
        == "DRY_RUN_SPECIFICATION_READY"
    )
    assert (
        packet.seven_stage_separation["STAGE_3_ACTUAL_RENDERING"]["executed"]
        is False
    )
    assert (
        packet.seven_stage_separation["STAGE_4_TECHNICAL_POST_RENDER_QC"]["evidence_state"]
        == "NOT_OBSERVED"
    )
    assert (
        packet.seven_stage_separation["STAGE_5_VISUAL_EDITORIAL_QC"]["evidence_state"]
        == "NOT_OBSERVED"
    )
    assert (
        packet.seven_stage_separation["STAGE_6_AUDIO_SYNC_QC"]["evidence_state"]
        == "NOT_OBSERVED"
    )
    assert (
        packet.seven_stage_separation["STAGE_7_FINAL_RELEASE_EXPORT_AUTHORIZATION"]["status"]
        == "REFUSED_NOT_AUTHORIZED"
    )

    # Consumes MEGA-16 artifacts without reimplementing them
    m16_ref = packet.consumed_mega16_summary
    assert len(m16_ref["mega15_16_report_digest"]) == 64
    assert len(m16_ref["render_preflight_digest"]) == 64
    assert len(m16_ref["qc_bundle_digest"]) == 64
    assert len(m16_ref["release_refusal_certificate_digest"]) == 64
    assert m16_ref["execution_mode"] == "DRY_RUN_SPECIFICATION_ONLY"
    assert m16_ref["subprocess_invoked"] is False

    # All 12 E12 negative refusal conditions verified
    assert len(packet.e12_negative_refusal_matrix) == 12
    assert set(packet.e12_negative_refusal_matrix.keys()) == set(
        E12_NEGATIVE_REFUSAL_CONDITIONS
    )
    for cond_key, cond_result in packet.e12_negative_refusal_matrix.items():
        assert cond_result["refused"] is True, f"Condition {cond_key} did not fail closed"
        assert cond_result["export_status"] == "REFUSED_NOT_AUTHORIZED"

    verified = verify_release_readiness_verification_packet(packet)
    assert verified["packet_digest"] == packet.packet_digest


def test_workstream_e_all_twelve_e12_negative_refusal_checks_individually() -> None:
    matrix = evaluate_e12_negative_refusal_matrix()
    assert len(matrix) == 12
    for cond_id in E12_NEGATIVE_REFUSAL_CONDITIONS:
        row = matrix[cond_id]
        assert row["condition_id"] == cond_id
        assert row["refused"] is True
        assert row["refusal_code"].startswith("REFUSAL_E12_")
        assert row["production_export_authorized"] is False


def test_workstream_e_refuses_derived_receipt_provenance_upgrade_and_executable_ffmpeg() -> None:
    pkt = inspect_release_and_qc_readiness(
        {
            "upgrade_source_provenance_from_derived_receipt": True,
            "ffmpeg_executable_command": ["ffmpeg", "-y", "-i", "in.mov", "out.mp4"],
            "qc_record": {"edit_qc_status": "PASS"},
            "trigger_e12_conditions": ["E12_09_FORGED_SENSORY_OBSERVATION", "E12_12_UNAUTHORIZED_EXPORT_REQUEST"],
        }
    )
    assert pkt.status == ReadinessStatus.NOT_AUTHORIZED
    assert REFUSAL_DERIVED_RECEIPT_CANNOT_UPGRADE_PROVENANCE in pkt.blockers
    assert REFUSAL_EXECUTABLE_FFMPEG_COMMAND_FORBIDDEN in pkt.blockers
    assert "REFUSAL_E12_10_BARE_PASS_QC" in pkt.blockers
    assert "REFUSAL_E12_09_FORGED_SENSORY_OBSERVATION" in pkt.blockers
    assert "REFUSAL_E12_12_UNAUTHORIZED_EXPORT_REQUEST" in pkt.blockers
    assert pkt.summary["production_export_authorized"] is False
    assert pkt.summary["export_status"] == "REFUSED_NOT_AUTHORIZED"


def test_workstream_e_tampered_packet_is_rejected() -> None:
    packet = build_release_readiness_verification_packet()
    raw = packet.to_dict()
    raw["production_export_authorized"] = True
    with pytest.raises(VipLabError):
        verify_release_readiness_verification_packet(raw)
