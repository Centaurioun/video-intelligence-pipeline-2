"""End-to-end synthetic integration tests across MEGA-08 through MEGA-14."""

from __future__ import annotations

from pathlib import Path

from vip_fvs.three_arm_batch import DECLARED_ARM_ORDER
from vip_lab.common import NOT_OBSERVED, ReadinessStatus, canonical_json_dumps
from vip_lab.mega14 import (
    MEGA_08_14_SPEC_VERSION,
    default_single_arm_scenario,
    default_three_arm_scenario,
    run_end_to_end_synthetic_lab,
    verify_e2e_lab_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_end_to_end_three_arm_pipeline_connects_all_waves_deterministically() -> None:
    scenario = default_three_arm_scenario()
    report_a = run_end_to_end_synthetic_lab(scenario, workspace_root=REPO_ROOT)
    report_b = run_end_to_end_synthetic_lab(scenario, workspace_root=REPO_ROOT)

    # Byte-identical deterministic output across repeated runs
    assert report_a.report_digest == report_b.report_digest
    assert canonical_json_dumps(report_a.to_dict()) == canonical_json_dumps(report_b.to_dict())

    assert report_a.spec_version == MEGA_08_14_SPEC_VERSION
    assert report_a.status == ReadinessStatus.READY_SYNTHETIC.value
    assert report_a.synthetic_only is True
    assert report_a.execution_authorized is False
    assert report_a.authentic_model_evidence is False
    assert report_a.real_media_accessed is False
    assert report_a.production_export_authorized is False
    assert report_a.export_status == "REFUSED_NOT_AUTHORIZED"
    assert report_a.all_gates_verdict == "NOT_APPROVED"
    assert report_a.workspace_git_sha == NOT_OBSERVED

    artifacts = report_a.artifacts
    inv = artifacts["capability_inventory"]
    batch_rep = artifacts["batch_report"]
    queue = artifacts["candidate_queue"]
    temp_req = artifacts["temporal_request"]
    proposal = artifacts["editorial_proposal"]
    rev_chain = artifacts["proposal_revision_chain"]
    replay_graph = artifacts["replay_graph"]
    lineage_receipt = artifacts["lineage_receipt"]
    blocker_summary = artifacts["release_blocker_summary"]

    # Cross-stage digest linkage
    assert inv["workspace_git_sha"] == NOT_OBSERVED
    assert queue["upstream_report_digest"] == batch_rep["report_digest"]
    assert tuple(queue["arm_ids"]) == DECLARED_ARM_ORDER
    assert queue["cross_arm_winner"] is None
    assert temp_req["upstream_queue_digest"] == queue["queue_digest"]
    assert temp_req["measurement_needed"] is True
    assert temp_req["source_pts_evidence_state"] == NOT_OBSERVED
    assert temp_req["binding_eligible"] is False
    assert proposal["upstream_queue_digest"] == queue["queue_digest"]
    assert proposal["upstream_temporal_request_digest"] == temp_req["request_digest"]
    assert proposal["proposal_version"] == 2
    assert len(rev_chain) == 2
    assert proposal["accepted_authority"] is False
    assert proposal["is_edit_plan"] is False
    assert replay_graph["idempotent_replay_verified"] is True
    assert replay_graph["duplicate_side_effects"] == 0
    assert lineage_receipt["lineage_valid"] is True
    assert lineage_receipt["queue_digest"] == queue["queue_digest"]
    assert lineage_receipt["temporal_request_digest"] == temp_req["request_digest"]
    assert lineage_receipt["proposal_digest"] == proposal["proposal_digest"]
    assert lineage_receipt["replay_graph_digest"] == replay_graph["graph_digest"]
    assert blocker_summary["production_export_authorized"] is False
    assert blocker_summary["export_status"] == "REFUSED_NOT_AUTHORIZED"
    assert artifacts["stage_packets"]["mega12"]["evidence_state"] == NOT_OBSERVED
    assert (
        artifacts["stage_packets"]["mega12"]["summary"]["observation_domain"]
        == "SYNTHETIC_FIXTURE_ONLY"
    )

    # Stretch S2 full cross-artifact verification passes
    verified = verify_e2e_lab_report(report_a.to_dict())
    assert verified["report_digest"] == report_a.report_digest


def test_end_to_end_single_arm_pipeline_preserves_duplicate_sources_and_queries() -> None:
    scenario = default_single_arm_scenario()
    report = run_end_to_end_synthetic_lab(scenario, workspace_root=REPO_ROOT)

    queue = report.artifacts["candidate_queue"]
    assert queue["kind"] == "SINGLE_ARM_SYNTHETIC_BATCH"
    # 3 queries (including 2 with identical query text) * 2 byte-identical source paths = 6 items
    assert queue["item_count"] == 6
    q01_paths = [
        item["source_path"] for item in queue["items"] if item["query_id"] == "q-01"
    ]
    assert q01_paths == [
        "/synthetic/archive/cam_a.mp4",
        "/synthetic/archive/cam_b_copy.mp4",
    ]
    verified = verify_e2e_lab_report(report.to_dict())
    assert verified["report_digest"] == report.report_digest
