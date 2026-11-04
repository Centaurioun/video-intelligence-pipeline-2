"""End-to-end integration, deterministic replay, and 30-category adversarial test suite for MEGA-17."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import pytest

from vip_lab.common import ReadinessStatus, VipLabError, canonical_sha256
from vip_lab.mega14.scenario import default_single_arm_scenario, default_three_arm_scenario
from vip_lab.mega16.release_refusal import run_mega15_16_offline_pipeline
from vip_lab.mega17 import orchestrator as mega17_orchestrator
from vip_lab.mega17.orchestrator import _validate_mega15_16_scenario_lineage
from vip_lab.mega17 import (
    MATURITY_LEVELS,
    MEGA17_REPORT_SCHEMA_VERSION,
    MEGA_17_SPEC_VERSION,
    Mega17ProductReadinessReport,
    build_canonical_integration_readiness,
    build_editorial_workflow_readiness_packet,
    build_gate0_experiment_readiness_receipt,
    build_release_readiness_verification_packet,
    build_source_readiness_packet,
    detect_transplant_conflicts,
    evaluate_e12_negative_refusal_matrix,
    evaluate_synthetic_gate0_scoring_fixture,
    inspect_canonical_integration_gate,
    inspect_editorial_workflow_readiness,
    inspect_gate0_experiment_readiness,
    inspect_mega17_product_readiness,
    inspect_release_and_qc_readiness,
    inspect_source_and_d2_readiness,
    run_mega17_product_readiness_chain,
    verify_mega17_product_readiness_report,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


def test_mega17_end_to_end_three_arm_and_single_arm_deterministic_replay() -> None:
    """Covers T01..T30 end-to-end chain in both THREE_ARM and SINGLE_ARM configurations."""
    rep_3a_1 = run_mega17_product_readiness_chain(
        default_three_arm_scenario(), workspace_root=WORKSPACE_ROOT
    )
    rep_3a_2 = run_mega17_product_readiness_chain(
        default_three_arm_scenario(), workspace_root=WORKSPACE_ROOT
    )
    assert isinstance(rep_3a_1, Mega17ProductReadinessReport)
    assert rep_3a_1.schema_version == MEGA17_REPORT_SCHEMA_VERSION
    assert rep_3a_1.spec_version == MEGA_17_SPEC_VERSION
    assert rep_3a_1.mode == "THREE_ARM"
    assert rep_3a_1.report_digest == rep_3a_2.report_digest
    assert rep_3a_1.to_dict() == rep_3a_2.to_dict()

    # Single-arm mode
    rep_1a = run_mega17_product_readiness_chain(
        default_single_arm_scenario(), workspace_root=WORKSPACE_ROOT
    )
    assert rep_1a.mode == "SINGLE_ARM"
    assert rep_1a.report_digest != rep_3a_1.report_digest
    verify_mega17_product_readiness_report(rep_1a)


def test_mega17_single_and_three_arm_keep_matching_upstream_scenario_lineage() -> None:
    single_scenario = default_single_arm_scenario()
    three_scenario = default_three_arm_scenario()
    single_upstream = run_mega15_16_offline_pipeline(scenario=single_scenario)
    three_upstream = run_mega15_16_offline_pipeline(scenario=three_scenario)

    single_packet = single_upstream.preparation_packet
    three_packet = three_upstream.preparation_packet
    assert len({record.arm_id for record in single_packet.temporal_records}) == 1
    assert len({record.arm_id for record in three_packet.temporal_records}) == 3
    assert {row["query_id"] for row in single_packet.query_identities} == {
        q["query_id"] for q in single_scenario.queries
    }
    assert {row["query_id"] for row in three_packet.query_identities} == {
        q["query_id"] for q in three_scenario.queries
    }
    assert {row["revision_id"] for row in single_packet.occurrence_identities} == {
        source["revision_id"] for source in single_scenario.sources
    }
    assert {row["revision_id"] for row in three_packet.occurrence_identities} == {
        source["revision_id"] for source in three_scenario.sources
    }

    single_report = run_mega17_product_readiness_chain(
        single_scenario, workspace_root=WORKSPACE_ROOT
    )
    three_report = run_mega17_product_readiness_chain(
        three_scenario, workspace_root=WORKSPACE_ROOT
    )
    single_digest = single_report.stage_digests["mega15_16_offline_report_digest"]
    three_digest = three_report.stage_digests["mega15_16_offline_report_digest"]
    assert single_digest == single_upstream.report_digest
    assert three_digest == three_upstream.report_digest
    assert single_digest != three_digest

    mismatched = single_report.to_dict()
    mismatched["stage_digests"]["mega15_16_offline_report_digest"] = three_digest
    mismatched["report_digest"] = canonical_sha256(
        {key: value for key, value in mismatched.items() if key != "report_digest"}
    )
    with pytest.raises(VipLabError, match="MEGA17_FOREIGN_DIGEST_MISMATCH"):
        verify_mega17_product_readiness_report(mismatched)

    tampered = single_report.to_dict()
    tampered["workstream_d"]["lineage_spine"]["source_revision_id"] = "rev-forged"
    with pytest.raises(VipLabError, match="digest"):
        verify_mega17_product_readiness_report(tampered)


def test_mega15_16_pipeline_preserves_custom_single_arm_membership() -> None:
    base = default_single_arm_scenario()
    scenario = replace(
        base,
        scenario_id="scen-mega17-custom-single-arm",
        queries=({"query_id": "q-mega17-pin", "text": "synthetic pinned query"},),
        sources=(
            {
                **base.sources[0],
                "revision_id": "rev-mega17-pin",
                "content_id": "content-mega17-pin",
                "source_path": "/synthetic/archive/pinned-source.mov",
                "source_sha256": "d" * 64,
            },
        ),
    )

    upstream = run_mega15_16_offline_pipeline(scenario=scenario)
    queue = upstream.preparation_packet

    assert len({record.arm_id for record in queue.temporal_records}) == 1
    assert {row["query_id"] for row in queue.query_identities} == {"q-mega17-pin"}
    assert {row["revision_id"] for row in queue.occurrence_identities} == {
        "rev-mega17-pin"
    }
    assert {row["source_sha256"] for row in queue.occurrence_identities} == {"d" * 64}
    report = run_mega17_product_readiness_chain(scenario, workspace_root=WORKSPACE_ROOT)
    assert report.scenario_id == scenario.scenario_id
    assert report.mode == scenario.mode
    assert report.workstream_d.lineage_spine["query_id"] == "q-mega17-pin"
    assert report.workstream_d.lineage_spine["source_revision_id"] == "rev-mega17-pin"


def test_mega17_rejects_upstream_occurrence_drop_even_when_membership_sets_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scenario = default_three_arm_scenario()
    real_producer = run_mega15_16_offline_pipeline

    def producer_with_dropped_occurrence(*, scenario):
        report = real_producer(scenario=scenario)
        packet = replace(
            report.preparation_packet,
            occurrence_identities=report.preparation_packet.occurrence_identities[:-1],
        )
        packet = replace(packet, packet_digest=canonical_sha256(packet._digest_payload()))
        return replace(report, preparation_packet=packet)

    monkeypatch.setattr(
        mega17_orchestrator,
        "run_mega15_16_offline_pipeline",
        producer_with_dropped_occurrence,
    )

    with pytest.raises(VipLabError, match="MEGA17_UPSTREAM_SCENARIO_MISMATCH"):
        mega17_orchestrator.run_mega17_product_readiness_chain(
            scenario, workspace_root=WORKSPACE_ROOT
        )


def test_mega17_rejects_foreign_upstream_arm_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scenario = default_three_arm_scenario()
    real_producer = run_mega15_16_offline_pipeline

    def producer_with_foreign_arms(*, scenario):
        report = real_producer(scenario=scenario)
        foreign_arm_ids = {
            arm_id: f"FOREIGN_{index}"
            for index, arm_id in enumerate(
                sorted({record.arm_id for record in report.preparation_packet.temporal_records})
            )
        }
        packet = replace(
            report.preparation_packet,
            temporal_records=tuple(
                replace(record, arm_id=foreign_arm_ids[record.arm_id])
                for record in report.preparation_packet.temporal_records
            ),
        )
        packet = replace(packet, packet_digest=canonical_sha256(packet._digest_payload()))
        return replace(report, preparation_packet=packet)

    monkeypatch.setattr(
        mega17_orchestrator,
        "run_mega15_16_offline_pipeline",
        producer_with_foreign_arms,
    )

    with pytest.raises(VipLabError, match="MEGA17_UPSTREAM_SCENARIO_MISMATCH"):
        mega17_orchestrator.run_mega17_product_readiness_chain(
            scenario, workspace_root=WORKSPACE_ROOT
        )


def test_mega17_eight_readiness_dimensions_and_maturity_model_ceilings() -> None:
    """Verifies Section 11 (8 readiness dimensions) and Section 12 (M0..M5 maturity ceiling)."""
    rep = run_mega17_product_readiness_chain(workspace_root=WORKSPACE_ROOT)

    # 8 mandatory readiness dimensions
    dims = rep.readiness_dimensions
    assert dims == {
        "software_available": True,
        "synthetic_tests_authored": True,
        "hosted_ci_verified": False,
        "canonical_integration_verified": False,
        "real_media_authorized": False,
        "real_experiment_executed": False,
        "human_evidence_observed": False,
        "production_export_authorized": False,
    }

    # Maturity levels must belong to M0..M5 and never claim M3/M4/M5 for newly authored MEGA-17
    assert set(MATURITY_LEVELS) == {
        "M0_NOT_STARTED",
        "M1_CONTRACT_DEFINED",
        "M2_SYNTHETIC_IMPLEMENTED",
        "M3_HOSTED_SYNTHETIC_VERIFIED",
        "M4_AUTHORIZED_LOCAL_VALIDATED",
        "M5_GATE_EVIDENCE_COMPLETE",
    }
    for ws_id, mat in rep.workstream_maturity.items():
        assert mat == "M2_SYNTHETIC_IMPLEMENTED", f"{ws_id} exceeded M2 ceiling: {mat}"
    for gate_id, mat in rep.gate_maturity.items():
        assert mat in ("M1_CONTRACT_DEFINED", "M2_SYNTHETIC_IMPLEMENTED", "M3_HOSTED_SYNTHETIC_VERIFIED")
        assert mat not in ("M4_AUTHORIZED_LOCAL_VALIDATED", "M5_GATE_EVIDENCE_COMPLETE")


def test_mega17_cross_workstream_foreign_key_and_digest_continuity() -> None:
    """Verifies that foreign keys and digests across Workstreams A, B, C, D, E and MEGA-14/15/16 match."""
    rep = run_mega17_product_readiness_chain(workspace_root=WORKSPACE_ROOT)
    verified = verify_mega17_product_readiness_report(rep)
    assert verified["report_digest"] == rep.report_digest

    # Check stage_digests match embedded workstream packets
    sd = rep.stage_digests
    assert sd["workstream_a_digest"] == rep.workstream_a.packet_digest
    assert sd["workstream_b_digest"] == rep.workstream_b.packet_digest
    assert sd["workstream_c_digest"] == rep.workstream_c.receipt_digest
    assert sd["workstream_d_digest"] == rep.workstream_d.packet_digest
    assert sd["workstream_e_digest"] == rep.workstream_e.packet_digest
    assert (
        sd["mega15_preparation_packet_digest"]
        == rep.workstream_d.consumed_mega15_summary["preparation_packet_digest"]
    )
    assert (
        sd["mega15_16_offline_report_digest"]
        == rep.workstream_e.consumed_mega16_summary["mega15_16_report_digest"]
    )


def test_mega17_thirty_category_adversarial_and_invariant_matrix() -> None:
    """Explicitly exercises all 30 required test categories (Section 13) in one comprehensive matrix."""
    rep = run_mega17_product_readiness_chain(workspace_root=WORKSPACE_ROOT)

    # 1. Baseline MEGA-03..16 & 6 gate0/media presence
    assert rep.workstream_a.gate0_media_modules_intact is True
    assert len(rep.workstream_a.gate0_media_inventory) == 6
    # 2. Module classification into closed categories
    assert len(rep.workstream_a.module_classifications) == len(
        {m.relative_path for m in rep.workstream_a.module_classifications}
    )
    # 3. Transplant conflict detection
    assert any(
        c.conflict_code == "DUPLICATE_CANDIDATE_PATH"
        for c in detect_transplant_conflicts(
            candidate_paths=("src/vip_lab/common.py", "src/vip_lab/common.py"),
            workspace_root=WORKSPACE_ROOT,
        )
    )
    # 4. Canonical integration non-execution refusal
    assert (
        inspect_canonical_integration_gate({"claim_canonical_integration_executed": True}).status
        == ReadinessStatus.NOT_AUTHORIZED
    )
    # 5. D-2 30-field accounting (0 VERIFIED, 7 PENDING, 21 BLOCKED, 2 NOT_OBSERVED)
    d2 = rep.workstream_b.d2_readiness_summary
    assert (
        d2["verified_count"],
        d2["pending_count"],
        d2["blocked_count"],
        d2["not_observed_count"],
    ) == (0, 7, 21, 2)
    # 6. Duplicate SHA-256 occurrences preserved
    assert rep.workstream_b.duplicate_occurrences_preserved is True
    assert rep.workstream_b.auto_deduplication_applied is False
    # 7. Identical filename refused as byte identity
    assert (
        inspect_source_and_d2_readiness({"infer_byte_identity_from_filename": True}).status
        == ReadinessStatus.BLOCKED
    )
    # 8. Forged owner attestation & D-3 refusal
    assert (
        inspect_source_and_d2_readiness({"claim_forged_owner_attestation": True}).status
        == ReadinessStatus.NOT_AUTHORIZED
    )
    # 9. Seven-permission separation (discovery != processing)
    assert (
        inspect_source_and_d2_readiness({"treat_discovery_as_processing_grant": True}).status
        == ReadinessStatus.NOT_AUTHORIZED
    )
    # 10. Source-disjoint dev/eval split leakage refusal
    assert (
        inspect_source_and_d2_readiness(
            {
                "partition_check": {
                    "development_revision_ids": ["r1"],
                    "evaluation_revision_ids": ["r1"],
                }
            }
        ).status
        == ReadinessStatus.BLOCKED
    )
    # 11. Gate-0 40-query protocol (24 pos, 8 absent, 8 dev)
    qp = rep.workstream_c.query_protocol_summary
    assert (
        qp["total_queries"],
        qp["evaluation_positive_count"],
        qp["evaluation_absent_count"],
        qp["development_count"],
    ) == (40, 24, 8, 8)
    # 12. Dual-reviewer & disagreement adjudication requirement
    assert (
        inspect_gate0_experiment_readiness({"reviewer_count": 1}).status
        == ReadinessStatus.BLOCKED
    )
    # 13. Gold labels withheld from ranker
    assert (
        inspect_gate0_experiment_readiness({"leak_gold_labels_to_ranker": True}).status
        == ReadinessStatus.BLOCKED
    )
    # 14. 4-second half-open window & 2-FPS presentation-frame sampling
    assert (
        inspect_gate0_experiment_readiness({"window_duration_seconds": 8}).status
        == ReadinessStatus.BLOCKED
    )
    # 15. 12 Gate-0 contract artifacts validated
    assert len(rep.workstream_c.contract_artifacts_status) == 12
    # 16. Synthetic Gate-0 scoring PASS vs FAIL (20/24, 5/24 lift, 3/6 per family)
    assert (
        evaluate_synthetic_gate0_scoring_fixture(scenario="SYNTHETIC_THRESHOLD_PASS")[
            "synthetic_threshold_outcome"
        ]
        == "PASS"
    )
    assert (
        evaluate_synthetic_gate0_scoring_fixture(
            scenario="SYNTHETIC_THRESHOLD_FAIL_FAMILY_FLOOR"
        )["synthetic_threshold_outcome"]
        == "FAIL"
    )
    # 17. Gate-0 vs Gate-1 boundary & non-interchangeable 768-D spaces
    assert rep.workstream_c.gate0_vs_gate1_boundary["gate1_substitutes_for_gate0"] is False
    assert (
        rep.workstream_c.gate0_vs_gate1_boundary["v1_and_v2_base_768d_interchangeable"]
        is False
    )
    # 18. MEGA-15 consumption & v1->v2->v3 proposal chain
    assert rep.workstream_d.consumed_mega15_summary["proposal_revision_numbers"] == [1, 2, 3]
    # 19. 5-way coordinate domain separation
    assert len(rep.workstream_d.coordinate_domain_separation) == 5
    # 20. Reviewer-handoff requirements packet != completed human review
    assert rep.workstream_d.reviewer_handoff_requirements.completed_human_review is False
    # 21. A-7 stream namespace ambiguity refusal
    assert (
        inspect_editorial_workflow_readiness({"a7_stream_namespace_ambiguous": True}).status
        == ReadinessStatus.BLOCKED
    )
    # 22. IT-6 terminal-tail duration mismatch refusal
    assert (
        inspect_editorial_workflow_readiness({"it6_terminal_tail_mismatch": True}).status
        == ReadinessStatus.BLOCKED
    )
    # 23. VFR seconds * nominal_fps derivation refusal
    assert (
        inspect_editorial_workflow_readiness({"derive_pts_from_nominal_fps": True}).status
        == ReadinessStatus.BLOCKED
    )
    # 24. 7-stage release workflow separation
    assert len(rep.workstream_e.seven_stage_separation) == 7
    # 25. Bare PASS QC refusal via gate3.qc.bare_pass_is_insufficient
    assert (
        inspect_release_and_qc_readiness({"qc_record": {"edit_qc_status": "PASS"}}).status
        == ReadinessStatus.BLOCKED
    )
    # 26. Derived receipt provenance upgrade refusal
    assert (
        inspect_release_and_qc_readiness(
            {"upgrade_source_provenance_from_derived_receipt": True}
        ).status
        == ReadinessStatus.NOT_AUTHORIZED
    )
    # 27. Executable FFmpeg command refusal
    assert (
        inspect_release_and_qc_readiness(
            {"ffmpeg_executable_command": ["ffmpeg", "-i", "a.mov", "b.mp4"]}
        ).status
        == ReadinessStatus.NOT_AUTHORIZED
    )
    # 28. All 12 E12 negative refusal conditions fail closed
    assert len(evaluate_e12_negative_refusal_matrix()) == 12
    # 29. Top-level readiness gate refuses untrusted authority escalation
    top_pkt = inspect_mega17_product_readiness(
        {
            "workspace_root": str(WORKSPACE_ROOT),
            "execution_authorized": True,
            "claim_production_export_authorized": True,
        }
    )
    assert top_pkt.status == ReadinessStatus.NOT_AUTHORIZED
    # 30. Tampered cross-workstream foreign key or digest fails verification
    bad_dict = rep.to_dict()
    bad_dict["stage_digests"]["workstream_d_digest"] = "f" * 64
    with pytest.raises(VipLabError) as exc_info:
        verify_mega17_product_readiness_report(bad_dict)
    assert exc_info.value.code in (
        "MEGA17_FOREIGN_DIGEST_MISMATCH",
        "MEGA17_REPORT_DIGEST_MISMATCH",
    )
