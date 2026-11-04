from __future__ import annotations

from pathlib import Path

import pytest

from gate3.qc import bare_pass_is_insufficient
from vip_fvs.real_preview_receipt import FIXTURE_NOT_OBSERVED_REQUIRED
from vip_lab.common import NOT_OBSERVED, VipLabError, canonical_json_dumps
from vip_lab.mega13 import (
    CANONICAL_RELEASE_BLOCKER_CODES,
    audit_cross_stage_lineage,
    build_release_blocker_summary,
    evaluate_qc_readiness,
)
from vip_lab.mega15 import (
    build_gate3_preparation_packet,
    build_temporal_preparation_record,
    verify_cross_stage_gate3_lineage,
)
from vip_lab.mega16 import (
    ExportReadinessPacket,
    InertDryRunRenderIntent,
    MEGA15_16_PROGRAM_VERSION,
    QCDimensionRequirement,
    QCRequirementManifest,
    REFUSAL_BARE_QC_PASS_INSUFFICIENT,
    REFUSAL_FORGED_SENSORY_OR_MEASURED_QC,
    REFUSAL_PRODUCTION_EXPORT_NOT_AUTHORIZED,
    REFUSAL_RENDER_EXECUTION_FORBIDDEN,
    RenderPreflightReport,
    build_export_readiness_packet,
    build_qc_requirement_manifest,
    build_render_preflight_report,
    validate_qc_claim_or_refuse,
    verify_export_readiness_packet,
    verify_qc_requirement_manifest,
    verify_render_preflight_report,
)
from vip_lab.mega16.cli import main as mega16_cli_main
from tests.vip_lab.test_mega15 import _build_fixture_queue_and_chains


def _build_mega15_inputs():
    queue, requests, diagnostics, proposal_chains = _build_fixture_queue_and_chains()
    temporal_records = [
        build_temporal_preparation_record(refinement_request=r, pts_diagnostic=d)
        for r, d in zip(requests, diagnostics, strict=True)
    ]
    prep_packet = build_gate3_preparation_packet(
        packet_id="g3_prep_m16_001",
        queue=queue,
        temporal_records=temporal_records,
        proposal_chains=proposal_chains,
    )
    lineage_cert = verify_cross_stage_gate3_lineage(
        certificate_id="g3_cert_m16_001",
        queue=queue,
        refinement_requests=requests,
        pts_diagnostics=diagnostics,
        proposal_chains=proposal_chains,
        preparation_packet=prep_packet,
    )
    m13_receipt = audit_cross_stage_lineage(
        audit_id="m13_audit_m16_001",
        queue=queue,
        refinement_requests=requests,
        pts_diagnostics=diagnostics,
        proposal_chains=proposal_chains,
    )
    qc_checklist = evaluate_qc_readiness(
        checklist_id="m13_qc_m16_001",
        lineage_receipt=m13_receipt,
    )
    blocker_summary = build_release_blocker_summary(
        summary_id="m13_blockers_m16_001",
        lineage_receipt=m13_receipt,
        qc_checklist=qc_checklist,
    )
    return prep_packet, lineage_cert, blocker_summary


def test_mega16_render_preflight_is_inert_and_refuses_execution() -> None:
    prep_packet, lineage_cert, _ = _build_mega15_inputs()

    report = build_render_preflight_report(
        preflight_id="render_preflight_001",
        preparation_packet=prep_packet,
        lineage_certificate=lineage_cert,
    )
    verify_render_preflight_report(report)

    assert report.preview_policy_authorized is False
    assert report.render_executed is False
    assert report.production_export_authorized is False
    assert report.export_status == "REFUSED_NOT_AUTHORIZED"
    assert len(report.dry_run_intents) == 3

    for intent in report.dry_run_intents:
        assert isinstance(intent, InertDryRunRenderIntent)
        assert intent.execution_mode == "INERT_DECLARATIVE_DRY_RUN_ONLY"
        assert intent.ffmpeg_invocation_permitted is False
        assert intent.media_file_creation_permitted is False
        assert intent.subprocess_execution_permitted is False
        assert intent.render_executed is False

    reloaded = RenderPreflightReport.from_dict(report.to_dict())
    assert reloaded.report_digest == report.report_digest

    # Attempting to request actual render/FFmpeg/preview execution via overrides fails closed
    with pytest.raises(VipLabError, match=REFUSAL_RENDER_EXECUTION_FORBIDDEN):
        build_render_preflight_report(
            preflight_id="render_preflight_bad",
            preparation_packet=prep_packet,
            lineage_certificate=lineage_cert,
            untrusted_overrides={"render_executed": True},
        )

    with pytest.raises(VipLabError, match=REFUSAL_RENDER_EXECUTION_FORBIDDEN):
        build_render_preflight_report(
            preflight_id="render_preflight_bad2",
            preparation_packet=prep_packet,
            lineage_certificate=lineage_cert,
            untrusted_overrides={"ffmpeg_invocation_permitted": True},
        )


def test_mega16_qc_requirement_manifest_and_bare_pass_rejection() -> None:
    prep_packet, _, _ = _build_mega15_inputs()

    # Confirm authoritative gate3.qc.bare_pass_is_insufficient behavior
    assert bare_pass_is_insufficient({"edit_qc_status": "PASS"}) is True

    manifest = build_qc_requirement_manifest(
        manifest_id="qc_manifest_001",
        preparation_packet=prep_packet,
    )
    verify_qc_requirement_manifest(manifest)

    assert manifest.technical_qc_observed == NOT_OBSERVED
    assert manifest.visual_editorial_qc_observed == NOT_OBSERVED
    assert manifest.audio_editorial_qc_observed == NOT_OBSERVED
    assert manifest.bare_pass_rejected is True
    assert manifest.fixture_not_observed_required == tuple(FIXTURE_NOT_OBSERVED_REQUIRED)
    assert manifest.overall_qc_status == "BLOCKED_NOT_OBSERVED"
    assert len(manifest.dimensions) == 3

    for dim in manifest.dimensions:
        assert isinstance(dim, QCDimensionRequirement)
        assert dim.current_observation_state == NOT_OBSERVED
        assert dim.satisfied is False

    # Bare QC PASS claim is refused
    with pytest.raises(VipLabError, match=REFUSAL_BARE_QC_PASS_INSUFFICIENT):
        validate_qc_claim_or_refuse({"edit_qc_status": "PASS"})

    # Forged sensory or measured QC claims are refused in synthetic offline preparation
    with pytest.raises(VipLabError, match=REFUSAL_FORGED_SENSORY_OR_MEASURED_QC):
        validate_qc_claim_or_refuse(
            {
                "edit_qc_status": "PASS",
                "qc_scope": "editorial_visual",
                "supporting_evidence_refs": ["ref_1"],
                "visual_editorial_qc_observed": "VISUALLY_OBSERVED",
            }
        )

    with pytest.raises(VipLabError, match=REFUSAL_FORGED_SENSORY_OR_MEASURED_QC):
        build_qc_requirement_manifest(
            manifest_id="qc_manifest_bad",
            preparation_packet=prep_packet,
            untrusted_qc_claim={"audio_editorial_qc_observed": "AUDIO_OBSERVED"},
        )


def test_mega16_export_readiness_packet_and_untrusted_authority_stripping() -> None:
    prep_packet, lineage_cert, blocker_summary = _build_mega15_inputs()
    render_report = build_render_preflight_report(
        preflight_id="render_preflight_001",
        preparation_packet=prep_packet,
        lineage_certificate=lineage_cert,
    )
    qc_manifest = build_qc_requirement_manifest(
        manifest_id="qc_manifest_001",
        preparation_packet=prep_packet,
    )

    untrusted_payload = {
        "note": "caller input",
        "human_approved": True,
        "owner_approved": True,
        "production_export_authorized": True,
        "gate_promoted": True,
    }
    readiness = build_export_readiness_packet(
        packet_id="export_readiness_001",
        preparation_packet=prep_packet,
        lineage_certificate=lineage_cert,
        render_preflight=render_report,
        qc_manifest=qc_manifest,
        release_blocker_summary=blocker_summary,
        untrusted_input=untrusted_payload,
    )
    verify_export_readiness_packet(readiness)

    assert readiness.lab_program_version == MEGA15_16_PROGRAM_VERSION
    assert readiness.real_human_decision_state == NOT_OBSERVED
    assert readiness.source_pts_evidence_state == NOT_OBSERVED
    assert readiness.source_native_exact_edit_eligible is False
    assert readiness.authoritative_edit_plan_created is False
    assert readiness.preview_policy_authorized is False
    assert readiness.render_executed is False
    assert readiness.technical_qc_observed == NOT_OBSERVED
    assert readiness.visual_editorial_qc_observed == NOT_OBSERVED
    assert readiness.audio_editorial_qc_observed == NOT_OBSERVED
    assert readiness.production_export_authorized is False
    assert readiness.export_status == "REFUSED_NOT_AUTHORIZED"
    assert set(readiness.blocker_codes) == set(CANONICAL_RELEASE_BLOCKER_CODES)
    assert set(readiness.stripped_untrusted_authority_keys) == {
        "gate_promoted",
        "human_approved",
        "owner_approved",
        "production_export_authorized",
    }

    reloaded = ExportReadinessPacket.from_dict(readiness.to_dict())
    assert reloaded.packet_digest == readiness.packet_digest

    # Tampering with production_export_authorized or export_status fails verification
    bad_dict = readiness.to_dict()
    bad_dict["production_export_authorized"] = True
    with pytest.raises(VipLabError, match=REFUSAL_PRODUCTION_EXPORT_NOT_AUTHORIZED):
        ExportReadinessPacket.from_dict(bad_dict)


def test_mega16_cli_creates_and_verifies_report_and_refuses_forbidden_flags(
    tmp_path: Path,
) -> None:
    out_file = tmp_path / "mega15_16_report.json"

    rc_create = mega16_cli_main(["--mode", "three_arm", "--output", str(out_file)])
    assert rc_create == 0
    assert out_file.is_file()

    rc_verify = mega16_cli_main(["--verify", str(out_file)])
    assert rc_verify == 0

    # Forbidden execution / network / export flags must return exit code 2
    for flag in ("--real", "--render", "--export", "--provider", "--download", "--upload"):
        assert mega16_cli_main([flag]) == 2

    # Forbidden URLs in arguments must return exit code 2
    for url in (
        "https://example.com/video.mp4",
        "http://example.com/video.mp4",
        "s3://bucket/video.mp4",
        "file:///tmp/video.mp4",
    ):
        assert mega16_cli_main(["--output", url]) == 2

    # Untrusted input JSON claiming real measurements or human approval is refused by --check-input
    bad_input_file = tmp_path / "untrusted_claim.json"
    bad_input_file.write_text(
        canonical_json_dumps(
            {
                "source_pts_evidence_state": "MEASURED",
                "real_human_decision_state": "ACCEPTED",
                "human_approved": True,
            }
        ),
        encoding="utf-8",
    )
    assert mega16_cli_main(["--check-input", str(bad_input_file)]) == 2
