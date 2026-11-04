"""Unit and CLI regression tests for MEGA-14: Scenario Parser, Stretch S2 Report Verifier & CLI."""

from __future__ import annotations

import copy
from pathlib import Path
import pytest

from vip_lab.common import NOT_OBSERVED, VipLabError, canonical_json_dumps
from vip_lab.mega14 import (
    E2E_REPORT_SCHEMA_VERSION,
    E2E_SCENARIO_SCHEMA_VERSION,
    EXIT_INVALID,
    EXIT_NOT_AUTHORIZED,
    EXIT_OK,
    EndToEndLabReport,
    SyntheticLabScenario,
    compute_e2e_report_digest,
    default_single_arm_scenario,
    default_three_arm_scenario,
    main as mega14_cli_main,
    parse_e2e_scenario_mapping,
    run_end_to_end_synthetic_lab,
    verify_e2e_lab_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_scenario_defaults_and_closed_schema_validation() -> None:
    s3 = default_three_arm_scenario()
    assert isinstance(s3, SyntheticLabScenario)
    assert s3.schema_version == E2E_SCENARIO_SCHEMA_VERSION
    assert s3.mode == "THREE_ARM"
    assert len(s3.queries) >= 2
    assert len(s3.sources) >= 2

    s1 = default_single_arm_scenario()
    assert s1.mode == "SINGLE_ARM"

    with pytest.raises(VipLabError) as exc_unk:
        parse_e2e_scenario_mapping(
            {
                **s1.to_dict(),
                "unknown_extra_field": 123,
            }
        )
    assert exc_unk.value.code == "SCENARIO_UNKNOWN_FIELD"

    with pytest.raises(VipLabError) as exc_flag:
        parse_e2e_scenario_mapping(
            {
                **s1.to_dict(),
                "real_media": True,
            }
        )
    assert exc_flag.value.code == "SCENARIO_FORBIDDEN_EXECUTION_FLAG"


def test_stretch_s2_report_verifier_detects_cross_stage_tampering() -> None:
    report = run_end_to_end_synthetic_lab(
        default_single_arm_scenario(),
        workspace_root=REPO_ROOT,
    )
    assert isinstance(report, EndToEndLabReport)
    assert report.schema_version == E2E_REPORT_SCHEMA_VERSION
    verified = verify_e2e_lab_report(report.to_dict())
    assert verified["report_digest"] == report.report_digest

    # Tamper with temporal_request upstream_queue_digest and recompute top-level report_digest
    broken = copy.deepcopy(report.to_dict())
    broken["artifacts"]["temporal_request"]["upstream_queue_digest"] = "f" * 64
    broken["report_digest"] = compute_e2e_report_digest(broken)
    with pytest.raises(VipLabError) as exc_tamper:
        verify_e2e_lab_report(broken)
    assert exc_tamper.value.code in {
        "TEMPORAL_REQUEST_DIGEST_MISMATCH",
        "E2E_CROSS_STAGE_DIGEST_MISMATCH",
        "LINEAGE_AUDIT_DIGEST_MISMATCH",
    }

    # Tamper with non-authority invariant
    escalated = copy.deepcopy(report.to_dict())
    escalated["production_export_authorized"] = True
    escalated["report_digest"] = compute_e2e_report_digest(escalated)
    with pytest.raises(VipLabError) as exc_auth:
        verify_e2e_lab_report(escalated)
    assert exc_auth.value.code == "E2E_AUTHORITY_VIOLATION"


def test_cli_run_and_verify_and_refuse_forbidden_flags(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out_file = tmp_path / "e2e_report.json"
    rc_run = mega14_cli_main(
        [
            "run-synthetic-scenario",
            "--mode",
            "single-arm",
            "--workspace-root",
            str(REPO_ROOT),
            "--output",
            str(out_file),
        ]
    )
    assert rc_run == EXIT_OK
    assert out_file.is_file()
    _ = capsys.readouterr()

    rc_verify = mega14_cli_main(["verify-report", "--report", str(out_file)])
    assert rc_verify == EXIT_OK
    verify_stdout = capsys.readouterr().out
    assert "READY_SYNTHETIC" in verify_stdout

    # Forbidden execution flags must fail closed with EXIT_NOT_AUTHORIZED (20)
    for forbidden_flag in ("--real", "--render", "--export", "--provider", "--download"):
        rc_refused = mega14_cli_main(["run-synthetic-scenario", forbidden_flag])
        assert rc_refused == EXIT_NOT_AUTHORIZED
        _ = capsys.readouterr()

    # Corrupt report file must fail with EXIT_INVALID (30)
    bad_file = tmp_path / "bad_report.json"
    bad_file.write_text('{"schema_version": "wrong"}', encoding="utf-8")
    rc_bad = mega14_cli_main(["verify-report", "--report", str(bad_file)])
    assert rc_bad == EXIT_INVALID
    _ = capsys.readouterr()
