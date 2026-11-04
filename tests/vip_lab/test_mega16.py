"""Unit and adversarial regression tests for MEGA-16 (`vip_lab.mega16`).

Covers against ACTUAL repository contracts:
- MEGA-16.1: `RenderPreflightSpecification`, `_REQUIRED_FIELDS` alignment with
  `vip_fvs.real_preview_receipt`, FFmpeg/media output/render execution refusals,
  and preview-as-production escalation refusal.
- MEGA-16.2: `QcRequirementsBundle`, `MEASURED` / `VISUALLY_OBSERVED` / `AUDIO_OBSERVED`
  evidence class separation, synthetic QC pass refusal, and QC blocker removal refusal.
- MEGA-16.3: `ReleaseRefusalCertificate`, all 6 `CANONICAL_RELEASE_BLOCKER_CODES`,
  untrusted authority key stripping, owner forgery refusal, production export refusal,
  and Gate promotion refusal.
- MEGA-16.4: Closed offline CLI (`run-offline`, `verify-report`), default `sys.argv`
  handling when `argv=None`, forbidden flag refusal, URL refusal, atomic no-clobber
  output safety, symlink refusal, media extension refusal, and tampered JSON refusal.
"""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys
from typing import Any
import pytest
import vip_lab.mega16.cli as mega16_cli_module

from vip_fvs.real_preview_receipt import (
    _FIELDS as REAL_PREVIEW_RECEIPT_REQUIRED_FIELDS,
    SCOPE as PREVIEW_NON_PRODUCTION_MARKER,
)
from vip_lab.common import ReadinessPacket, VipLabError
from vip_lab.mega10 import (
    build_temporal_refinement_request,
    evaluate_pts_fixture_diagnostic,
)
from vip_lab.mega11 import (
    advance_proposal_revision,
    build_editorial_proposal,
)
from vip_lab.mega13 import (
    CANONICAL_RELEASE_BLOCKER_CODES,
    audit_cross_stage_lineage,
    build_release_blocker_summary,
    evaluate_qc_readiness,
)
from vip_lab.mega15 import (
    audit_mega15_lineage,
    build_editorial_handoff_envelope,
    build_gate3_offline_preparation_packet,
    build_temporal_preparation_record,
)
from vip_lab.mega16 import (
    FORBIDDEN_CLI_FLAGS,
    REFUSAL_BLOCKER_SET_INCOMPLETE,
    REFUSAL_CLI_FORBIDDEN_FLAG,
    REFUSAL_CLI_INPUT_PATH_UNSAFE,
    REFUSAL_CLI_OUTPUT_PATH_UNSAFE,
    REFUSAL_CLI_URL_FORBIDDEN,
    REFUSAL_FFMPEG_INVOCATION_FORBIDDEN,
    REFUSAL_GATE_PROMOTION_FORBIDDEN,
    REFUSAL_OWNER_AUTHORITY_FORGERY,
    REFUSAL_PREVIEW_AS_PRODUCTION_FORBIDDEN,
    REFUSAL_PRODUCTION_EXPORT_FORBIDDEN,
    REFUSAL_QC_BLOCKER_REMOVAL,
    REFUSAL_QC_EVIDENCE_CLASS_CONFUSION,
    REFUSAL_RENDER_EXECUTION_FORBIDDEN,
    REFUSAL_RENDER_OUTPUT_PATH_FORBIDDEN,
    REFUSAL_SYNTHETIC_AUDIO_QC_PASS,
    REFUSAL_SYNTHETIC_TECHNICAL_QC_PASS,
    REFUSAL_SYNTHETIC_VISUAL_QC_PASS,
    build_mega15_16_offline_report,
    build_qc_requirements_bundle,
    build_release_refusal_certificate,
    build_render_preflight_specification,
    mega16_cli_main,
    refuse_production_export_or_gate_promotion,
    refuse_render_or_ffmpeg_execution,
    refuse_synthetic_qc_pass_or_class_confusion,
    verify_mega15_16_offline_report,
    verify_qc_requirements_bundle,
    verify_release_refusal_certificate,
    verify_render_preflight_specification,
)
from vip_lab.mega16.release_refusal import run_mega15_16_offline_pipeline
from tests.vip_lab.test_mega15 import _make_three_item_queue_with_duplicates


def _set_test_report_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    root = tmp_path / "trusted-synthetic-reports"
    monkeypatch.setattr(mega16_cli_module, "_TRUSTED_SYNTHETIC_REPORT_ROOT", root)
    return root


def _build_mega15_fixture() -> tuple[Any, ...]:
    queue = _make_three_item_queue_with_duplicates()
    t_reqs = []
    t_recs = []
    p_chains = []
    h_envs = []

    for item in queue.items:
        pts_ticks = (0, 1000, 2000, 3000, 4000)
        req = build_temporal_refinement_request(
            item,
            upstream_queue_digest=queue.queue_digest,
            selected_stream_index=0,
            requested_start_pts=1000,
            requested_end_pts=3000,
            pts_ticks=pts_ticks,
        )
        diag = evaluate_pts_fixture_diagnostic(
            timebase_num=item.source_timebase_num,
            timebase_den=item.source_timebase_den,
            pts_ticks=pts_ticks,
            requested_start_pts=1000,
            requested_end_pts=3000,
        )
        t_rec = build_temporal_preparation_record(refinement_request=req, pts_diagnostic=diag)
        v1 = build_editorial_proposal(
            queue_item=item,
            temporal_request=req,
            proposed_action="REVIEW_CANDIDATE",
            rationale_note=f"v1 for {item.queue_item_id}",
        )
        v2 = advance_proposal_revision(
            prior_proposal=v1,
            proposed_action="REQUEST_MEASUREMENT",
            rationale_note=f"v2 for {item.queue_item_id}",
        )
        env = build_editorial_handoff_envelope(
            candidate_item=item,
            temporal_record=t_rec,
            proposal_revisions=(v1, v2),
        )
        t_reqs.append(req)
        t_recs.append(t_rec)
        p_chains.append((v1, v2))
        h_envs.append(env)

    prep_packet = build_gate3_offline_preparation_packet(
        candidate_queue=queue,
        temporal_records=t_recs,
        handoff_envelopes=h_envs,
    )
    m13_lineage = audit_cross_stage_lineage(
        candidate_queue=queue,
        temporal_request=t_reqs[0],
        editorial_proposal=p_chains[0][-1],
        proposal_revision_chain=p_chains[0],
    )
    m15_lineage = audit_mega15_lineage(
        queue=queue,
        temporal_requests=t_reqs,
        proposal_chains=p_chains,
        preparation_packet=prep_packet,
        upstream_lineage_receipt=m13_lineage,
    )
    m13_qc_readiness = evaluate_qc_readiness(
        {
            "candidate_queue": queue.to_dict(),
            "temporal_request": t_reqs[0].to_dict(),
            "editorial_proposal": p_chains[0][-1].to_dict(),
            "proposal_revision_chain": [p.to_dict() for p in p_chains[0]],
        }
    )
    m13_blocker_summary = build_release_blocker_summary(
        lineage_receipt=m13_lineage,
        qc_packet=m13_qc_readiness,
    )
    return prep_packet, m15_lineage, m13_qc_readiness, m13_blocker_summary


def test_render_preflight_specification_and_refusals() -> None:
    prep_packet, m15_lineage, _, _ = _build_mega15_fixture()
    spec = build_render_preflight_specification(
        preparation_packet=prep_packet,
        lineage_receipt=m15_lineage,
    )
    assert spec.render_execution_state == "PREFLIGHT_ONLY_NOT_EXECUTED"
    assert spec.preview_eligible is False
    assert spec.production_export_authorized is False
    assert spec.ffmpeg_invocation_permitted is False
    assert spec.media_write_permitted is False
    assert spec.expected_non_production_marker == PREVIEW_NON_PRODUCTION_MARKER
    assert set(spec.gate3_render_receipt_required_fields) == set(
        REAL_PREVIEW_RECEIPT_REQUIRED_FIELDS
    )
    assert all(w.media_output_path is None for w in spec.windows)
    assert verify_render_preflight_specification(spec.to_dict()) == spec

    with pytest.raises(VipLabError, match=REFUSAL_RENDER_EXECUTION_FORBIDDEN):
        refuse_render_or_ffmpeg_execution(execute_render=True)
    with pytest.raises(VipLabError, match=REFUSAL_FFMPEG_INVOCATION_FORBIDDEN):
        refuse_render_or_ffmpeg_execution(ffmpeg_argv=["ffmpeg", "-i", "in.mp4", "out.mp4"])
    with pytest.raises(VipLabError, match=REFUSAL_RENDER_OUTPUT_PATH_FORBIDDEN):
        refuse_render_or_ffmpeg_execution(media_output_path="/tmp/out.mp4")
    with pytest.raises(VipLabError, match=REFUSAL_PREVIEW_AS_PRODUCTION_FORBIDDEN):
        refuse_render_or_ffmpeg_execution(treat_preview_as_production=True)


def test_qc_requirements_bundle_and_evidence_class_refusals() -> None:
    prep_packet, m15_lineage, m13_qc_readiness, _ = _build_mega15_fixture()
    render_spec = build_render_preflight_specification(
        preparation_packet=prep_packet,
        lineage_receipt=m15_lineage,
    )
    qc_bundle = build_qc_requirements_bundle(
        render_specification=render_spec,
        qc_readiness_packet=m13_qc_readiness,
    )
    assert qc_bundle.technical_qc_required_evidence_class == "MEASURED"
    assert qc_bundle.visual_editorial_qc_required_evidence_class == "VISUALLY_OBSERVED"
    assert qc_bundle.audio_editorial_qc_required_evidence_class == "AUDIO_OBSERVED"
    assert qc_bundle.technical_qc_state == "NOT_OBSERVED"
    assert qc_bundle.visual_editorial_qc_state == "NOT_OBSERVED"
    assert qc_bundle.audio_editorial_qc_state == "NOT_OBSERVED"
    assert qc_bundle.overall_qc_gate_status == "BLOCKED_QC_NOT_OBSERVED"
    assert verify_qc_requirements_bundle(qc_bundle.to_dict()) == qc_bundle

    with pytest.raises(VipLabError, match=REFUSAL_SYNTHETIC_TECHNICAL_QC_PASS):
        refuse_synthetic_qc_pass_or_class_confusion(claim_technical_qc_pass=True)
    with pytest.raises(VipLabError, match=REFUSAL_SYNTHETIC_VISUAL_QC_PASS):
        refuse_synthetic_qc_pass_or_class_confusion(claim_visual_qc_pass=True)
    with pytest.raises(VipLabError, match=REFUSAL_SYNTHETIC_AUDIO_QC_PASS):
        refuse_synthetic_qc_pass_or_class_confusion(claim_audio_qc_pass=True)
    with pytest.raises(VipLabError, match=REFUSAL_QC_EVIDENCE_CLASS_CONFUSION):
        refuse_synthetic_qc_pass_or_class_confusion(technical_evidence_class="MATCHED")
    with pytest.raises(VipLabError, match=REFUSAL_QC_EVIDENCE_CLASS_CONFUSION):
        refuse_synthetic_qc_pass_or_class_confusion(
            visual_evidence_class="EDITORIAL_INFERENCE"
        )
    with pytest.raises(VipLabError, match=REFUSAL_QC_EVIDENCE_CLASS_CONFUSION):
        refuse_synthetic_qc_pass_or_class_confusion(
            audio_evidence_class="VISUALLY_OBSERVED"
        )

    # Removing QC refusal / escalating preview_eligible on ReadinessPacket must be refused
    bad_ready = replace(
        m13_qc_readiness,
        summary={**dict(m13_qc_readiness.summary), "preview_eligible": True},
    )
    with pytest.raises(VipLabError, match=REFUSAL_QC_BLOCKER_REMOVAL):
        build_qc_requirements_bundle(
            render_specification=render_spec,
            qc_readiness_packet=bad_ready,
        )


def test_release_refusal_certificate_and_untrusted_authority_sanitization() -> None:
    prep_packet, m15_lineage, m13_qc_readiness, m13_blocker_summary = _build_mega15_fixture()
    render_spec = build_render_preflight_specification(
        preparation_packet=prep_packet,
        lineage_receipt=m15_lineage,
    )
    qc_bundle = build_qc_requirements_bundle(
        render_specification=render_spec,
        qc_readiness_packet=m13_qc_readiness,
    )

    untrusted_payload = {
        "note": "benign note",
        "human_approved": True,
        "owner_approved": True,
        "production_export_authorized": True,
        "gate_promoted": True,
    }
    cert = build_release_refusal_certificate(
        preparation_packet=prep_packet,
        mega15_lineage_receipt=m15_lineage,
        render_specification=render_spec,
        qc_bundle=qc_bundle,
        upstream_blocker_summary=m13_blocker_summary,
        untrusted_authority_payload=untrusted_payload,
    )
    assert cert.production_export_authorized is False
    assert cert.preview_eligible is False
    assert cert.gate_promotion_authorized is False
    assert cert.export_status == "REFUSED_NOT_AUTHORIZED"
    assert set(CANONICAL_RELEASE_BLOCKER_CODES).issubset(
        set(cert.active_release_blocker_codes)
    )
    assert "human_approved" in cert.stripped_untrusted_authority_keys
    assert "owner_approved" in cert.stripped_untrusted_authority_keys
    assert "production_export_authorized" in cert.stripped_untrusted_authority_keys
    assert "gate_promoted" in cert.stripped_untrusted_authority_keys
    assert verify_release_refusal_certificate(cert.to_dict()) == cert

    with pytest.raises(VipLabError, match=REFUSAL_PRODUCTION_EXPORT_FORBIDDEN):
        refuse_production_export_or_gate_promotion(request_production_export=True)
    with pytest.raises(VipLabError, match=REFUSAL_GATE_PROMOTION_FORBIDDEN):
        refuse_production_export_or_gate_promotion(request_gate_promotion=True)
    with pytest.raises(VipLabError, match=REFUSAL_OWNER_AUTHORITY_FORGERY):
        refuse_production_export_or_gate_promotion(claim_owner_approval=True)

    # Removing any canonical release blocker from upstream summary must fail closed
    incomplete_summary = {
        **m13_blocker_summary,
        "release_blockers": list(CANONICAL_RELEASE_BLOCKER_CODES[:-1]),
    }
    with pytest.raises(VipLabError, match=REFUSAL_BLOCKER_SET_INCOMPLETE):
        build_release_refusal_certificate(
            preparation_packet=prep_packet,
            mega15_lineage_receipt=m15_lineage,
            render_specification=render_spec,
            qc_bundle=qc_bundle,
            upstream_blocker_summary=incomplete_summary,
        )

    report = build_mega15_16_offline_report(
        preparation_packet=prep_packet,
        mega15_lineage_receipt=m15_lineage,
        render_specification=render_spec,
        qc_bundle=qc_bundle,
        refusal_certificate=cert,
    )
    assert verify_mega15_16_offline_report(report.to_dict()) == report


def test_cli_run_verify_and_refusals(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_root = _set_test_report_root(tmp_path, monkeypatch)
    out_file = report_root / "mega15_16_report.json"
    rc = mega16_cli_main(["run-offline", "--seed", "20261102", "--output", str(out_file)])
    assert rc == 0
    assert out_file.exists()
    report_before_verify = out_file.read_bytes()

    rc_ver = mega16_cli_main(["verify-report", "--input", str(out_file)])
    assert rc_ver == 0
    assert out_file.read_bytes() == report_before_verify
    captured = capsys.readouterr()
    summary = json.loads(captured.out.strip().splitlines()[-1])
    assert summary["verified"] is True
    assert summary["export_status"] == "REFUSED_NOT_AUTHORIZED"
    assert summary["production_export_authorized"] is False

    # Default sys.argv handling when argv=None
    monkeypatch.setattr(sys, "argv", ["vip-lab-mega16", "verify-report", "--input", str(out_file)])
    rc_default_argv = mega16_cli_main()
    assert rc_default_argv == 0
    _ = capsys.readouterr()

    # Overwriting an existing file must fail closed (atomic no-clobber)
    rc_clobber = mega16_cli_main(["run-offline", "--output", str(out_file)])
    assert rc_clobber == 2
    err_clobber = capsys.readouterr().err
    assert REFUSAL_CLI_OUTPUT_PATH_UNSAFE in err_clobber

    # Media file extension on --output must fail closed
    media_out = report_root / "render_output.mp4"
    rc_media = mega16_cli_main(["run-offline", "--output", str(media_out)])
    assert rc_media == 2
    err_media = capsys.readouterr().err
    assert REFUSAL_CLI_OUTPUT_PATH_UNSAFE in err_media

    # Parent directory traversal on --output must fail closed
    rc_trav = mega16_cli_main(["run-offline", "--output", "../escape_report.json"])
    assert rc_trav == 2
    err_trav = capsys.readouterr().err
    assert REFUSAL_CLI_OUTPUT_PATH_UNSAFE in err_trav

    # Symlink target on --output and --input must fail closed
    symlink_path = report_root / "symlink_report.json"
    symlink_path.symlink_to(out_file)
    rc_sym_out = mega16_cli_main(["run-offline", "--output", str(symlink_path)])
    assert rc_sym_out == 2
    assert REFUSAL_CLI_OUTPUT_PATH_UNSAFE in capsys.readouterr().err

    rc_sym_in = mega16_cli_main(["verify-report", "--input", str(symlink_path)])
    assert rc_sym_in == 2
    assert REFUSAL_CLI_INPUT_PATH_UNSAFE in capsys.readouterr().err

    # Tampered report file must fail verification with exit code 2
    tampered_data = json.loads(out_file.read_text(encoding="utf-8"))
    tampered_data["release_refusal_certificate"]["production_export_authorized"] = True
    tampered_file = report_root / "tampered.json"
    tampered_file.write_text(json.dumps(tampered_data), encoding="utf-8")
    assert mega16_cli_main(["verify-report", "--input", str(tampered_file)]) == 2

    # Forbidden CLI flags must return exit code 2
    for flag in FORBIDDEN_CLI_FLAGS:
        assert mega16_cli_main(["run-offline", flag]) == 2

    # URL arguments must return exit code 2
    assert (
        mega16_cli_main(["verify-report", "--input", "https://example.com/report.json"])
        == 2
    )
    assert (
        mega16_cli_main(["run-offline", "--output=s3://bucket/report.json"]) == 2
    )


def test_cli_verify_missing_report_does_not_create_parent_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report_root = _set_test_report_root(tmp_path, monkeypatch)
    missing_report = report_root / "missing-parent" / "nested" / "report.json"
    assert not missing_report.parent.exists()

    assert mega16_cli_main(["verify-report", "--input", str(missing_report)]) == 2

    assert not missing_report.parent.exists()


def test_cli_output_refuses_absolute_path_outside_trusted_report_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trusted_root = _set_test_report_root(tmp_path, monkeypatch)
    outside_path = tmp_path / "outside" / "nested" / "report.json"
    real_is_symlink = Path.is_symlink
    real_exists = Path.exists

    def refuse_outside_metadata_access(path: Path) -> bool:
        if path == outside_path:
            raise AssertionError("outside report target was statted before refusal")
        return real_is_symlink(path)

    def refuse_outside_exists_check(path: Path) -> bool:
        if path == outside_path:
            raise AssertionError("outside report target was statted before refusal")
        return real_exists(path)

    monkeypatch.setattr(Path, "is_symlink", refuse_outside_metadata_access)
    monkeypatch.setattr(Path, "exists", refuse_outside_exists_check)

    assert mega16_cli_main(["run-offline", "--output", str(outside_path)]) == 2
    assert not outside_path.parent.exists()
    assert not trusted_root.exists()


def test_cli_input_refuses_absolute_path_outside_trusted_report_root_before_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _set_test_report_root(tmp_path, monkeypatch)
    outside_path = tmp_path / "outside" / "valid-report.json"
    outside_path.parent.mkdir()
    outside_path.write_text(
        json.dumps(run_mega15_16_offline_pipeline().to_dict()), encoding="utf-8"
    )
    real_is_symlink = Path.is_symlink
    real_exists = Path.exists

    def refuse_outside_metadata_access(path: Path) -> bool:
        if path == outside_path:
            raise AssertionError("outside report target was statted before refusal")
        return real_is_symlink(path)

    def refuse_outside_exists_check(path: Path) -> bool:
        if path == outside_path:
            raise AssertionError("outside report target was statted before refusal")
        return real_exists(path)

    monkeypatch.setattr(Path, "is_symlink", refuse_outside_metadata_access)
    monkeypatch.setattr(Path, "exists", refuse_outside_exists_check)
    reads = 0
    real_read = mega16_cli_module.os.read

    def track_read(fd: int, size: int) -> bytes:
        nonlocal reads
        reads += 1
        return real_read(fd, size)

    monkeypatch.setattr(mega16_cli_module.os, "read", track_read)

    assert mega16_cli_main(["verify-report", "--input", str(outside_path)]) == 2
    assert reads == 0


def test_cli_relative_report_paths_are_rooted_in_trusted_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report_root = _set_test_report_root(tmp_path, monkeypatch)
    relative_path = "nested/report.json"

    assert mega16_cli_main(["run-offline", "--output", relative_path]) == 0
    assert (report_root / relative_path).is_file()
    assert mega16_cli_main(["verify-report", "--input", relative_path]) == 0


def test_cli_output_refuses_symlinked_ancestor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report_root = _set_test_report_root(tmp_path, monkeypatch)
    report_root.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    link = report_root / "linked-parent"
    link.symlink_to(outside, target_is_directory=True)
    output = link / "nested" / "report.json"

    assert mega16_cli_main(["run-offline", "--output", str(output)]) == 2
    assert not (outside / "nested" / "report.json").exists()


def test_cli_output_retries_partial_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report_root = _set_test_report_root(tmp_path, monkeypatch)
    output = report_root / "partial-write-report.json"
    real_write = mega16_cli_module.os.write

    def partial_write(fd: int, data: bytes | bytearray | memoryview) -> int:
        return real_write(fd, data[:7])

    monkeypatch.setattr(mega16_cli_module.os, "write", partial_write)
    assert mega16_cli_main(["run-offline", "--output", str(output)]) == 0
    parsed = json.loads(output.read_text(encoding="utf-8"))
    assert (
        parsed["release_refusal_certificate"]["export_status"]
        == "REFUSED_NOT_AUTHORIZED"
    )


def test_cli_output_removes_incomplete_file_after_write_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report_root = _set_test_report_root(tmp_path, monkeypatch)
    output = report_root / "failed-write-report.json"
    real_write = mega16_cli_module.os.write
    calls = 0

    def fail_after_partial_write(
        fd: int, data: bytes | bytearray | memoryview
    ) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return real_write(fd, data[:7])
        raise OSError("simulated disk write failure")

    monkeypatch.setattr(mega16_cli_module.os, "write", fail_after_partial_write)
    assert mega16_cli_main(["run-offline", "--output", str(output)]) == 2
    assert not output.exists()


def test_cli_verify_rejects_media_paths_before_reading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report_root = _set_test_report_root(tmp_path, monkeypatch)
    report_root.mkdir(parents=True)
    media_path = report_root / "source.mp4"
    media_path.write_bytes(b"not a report")
    read_calls = 0
    real_read = mega16_cli_module.os.read

    def track_read(fd: int, size: int) -> bytes:
        nonlocal read_calls
        read_calls += 1
        return real_read(fd, size)

    monkeypatch.setattr(mega16_cli_module.os, "read", track_read)
    assert mega16_cli_main(["verify-report", "--input", str(media_path)]) == 2
    assert read_calls == 0
