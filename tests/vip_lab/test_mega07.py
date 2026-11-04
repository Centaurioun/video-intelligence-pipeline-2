"""Regression tests for Wave MEGA-07 (P07a, P07b, P07c): Gate-3 Candidate->Temporal Gate,
Editorial Lineage Verification, and Technical/Editorial QC & Export Refusal.
"""

from __future__ import annotations

import hashlib
from typing import Any

from vip_fvs.human_decision import (
    RECORD_TYPE as HD_RECORD_TYPE,
    SCHEMA_VERSION as HD_SCHEMA_VERSION,
)
from vip_fvs.review_bundle import (
    RECORD_TYPE as RB_RECORD_TYPE,
    V1_SCHEMA_VERSION,
    dependency_digest,
    record_digest,
)
from vip_lab.common import ReadinessStatus, canonical_json_dumps
from vip_lab.mega07 import (
    inspect_candidate_temporal,
    inspect_editorial_lineage,
    inspect_qc_export_readiness,
)


def _make_v1_bundle_record() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "bundle_id": "bundle_g3_01",
        "run_id": "run_g3_01",
        "created_at": "2026-10-30T12:00:00Z",
        "review_status": "AWAITING_EDITORIAL_DECISION",
        "source": {
            "source_revision_id": "rev_001",
            "source_sha256": "a" * 64,
            "source_byte_count": 1024,
            "selected_stream_index": 0,
            "timebase": {"num": 1, "den": 90000},
            "probe_artifact_ref": "/nonexistent/probe.json",
            "probe_digest": "1" * 64,
        },
        "authorization": {
            "discovery_policy_ref": "pol_disc_01",
            "refinement_policy_ref": "pol_ref_01",
            "policy_digest": "3" * 64,
            "scope_digest": "4" * 64,
        },
        "query": {
            "query_id": "q_01",
            "text": "pirouette",
            "digest": "5" * 64,
        },
        "generation": {
            "attempt_id": "att_001",
            "generation_id": "gen_001",
            "semantic_space_id": "vip-v1-siglip-base-224:768",
            "model_identity": "siglip-base-patch16-224",
            "model_revision": "rev1",
            "weights_digest": "6" * 64,
            "processor_digest": "7" * 64,
            "index_ref": "idx_001",
            "index_digest": "8" * 64,
            "input_digest": "9" * 64,
        },
        "candidate": {
            "candidate_id": "cand_001",
            "rank": 1,
            "score": 0.95,
            "evidence_class": "MATCHED",
            "binding_eligible": False,
            "assertion_digest": "b" * 64,
            "semantic_interval": {
                "start": 1.0,
                "end": 2.0,
                "time_domain": "semantic_seconds",
                "endpoint_semantics": "half_open",
            },
        },
        "refinement": {
            "refinement_id": "ref_001",
            "status": "MEASURED",
            "source_revision_id": "rev_001",
            "selected_stream_index": 0,
            "source_pts_interval": {
                "start": 90000,
                "end": 180000,
                "time_domain": "source_pts",
                "endpoint_semantics": "half_open",
            },
            "timebase": {"num": 1, "den": 90000},
            "attempt_id": "att_001",
            "evidence_artifact_ref": "/nonexistent/e01.json",
            "evidence_digest": "2" * 64,
            "evidence_class": "MEASURED",
        },
        "presentation": {
            "display_only": True,
            "start_seconds": 1.0,
            "end_seconds": 2.0,
        },
        "dependency_digest": "0" * 64,
        "decision": None,
    }
    payload["dependency_digest"] = dependency_digest(payload)
    rec = {
        "record_id": "bundle_g3_01",
        "record_type": RB_RECORD_TYPE,
        "record_schema_version": V1_SCHEMA_VERSION,
        "record_digest": "0" * 64,
        "payload": payload,
    }
    rec["record_digest"] = record_digest(rec)
    return rec


def _make_human_decision_record(
    bundle_rec: dict[str, Any],
    *,
    decision_class: str = "ACCEPT",
) -> dict[str, Any]:
    bp = bundle_rec["payload"]
    if decision_class == "ACCEPT":
        disposition = "ACCEPTED_FOR_PLAN"
        plan_action = "BUILD_REAL_PLAN"
        req_mod = None
    elif decision_class == "REJECT":
        disposition = "REJECTED"
        plan_action = "NONE"
        req_mod = None
    else:
        disposition = "MODIFICATION_REQUESTED"
        plan_action = "NONE"
        req_mod = "Shift cut 3 frames later"

    payload: dict[str, Any] = {
        "decision_id": "dec_001",
        "bundle_record_digest": bundle_rec["record_digest"],
        "bundle_dependency_digest": bp["dependency_digest"],
        "principal_kind": "human",
        "principal_ref": "editor_aylin",
        "refinement_id": bp["refinement"]["refinement_id"],
        "refinement_evidence_digest": bp["refinement"]["evidence_digest"],
        "source_revision_id": bp["source"]["source_revision_id"],
        "source_sha256": bp["source"]["source_sha256"],
        "target_plan_revision": 1,
        "decision_class": decision_class,
        "rationale": "Exact musical phrase entrance verified on PTS boundary",
        "disposition": disposition,
        "plan_action": plan_action,
        "evidence_class": "EDITORIAL_INFERENCE",
        "requested_modification": req_mod,
        "accepted_sub_interval_ref": bp["refinement"]["refinement_id"],
        "supersedes": None,
    }
    rec: dict[str, Any] = {
        "record_id": "dec_001",
        "record_type": HD_RECORD_TYPE,
        "record_schema_version": HD_SCHEMA_VERSION,
        "payload": payload,
    }
    rec["record_digest"] = hashlib.sha256(
        canonical_json_dumps(rec).encode("utf-8")
    ).hexdigest()
    return rec


class TestMega07CandidateTemporalGate:
    def test_monotonic_pts_refinement_resolves_ticks_without_granting_binding(
        self,
    ) -> None:
        pts_ticks = [i * 3000 for i in range(91)]  # 0 .. 270000 (3 seconds at 30fps)
        pkt = inspect_candidate_temporal(
            {
                "candidate": {
                    "candidate_id": "cand_01",
                    "evidence_class": "MATCHED",
                    "frame_accurate": False,
                    "start_sec": {"num": 1, "den": 1},
                    "end_sec": {"num": 2, "den": 1},
                },
                "time_base": {"num": 1, "den": 90000},
                "pts_ticks": pts_ticks,
            }
        )
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.evidence_state == "NOT_OBSERVED"
        assert pkt.summary["temporal_refined"] is True
        assert pkt.summary["binding_eligible"] is False
        assert pkt.summary["refinement_status"] == "SYNTHETIC_DIAGNOSTIC_ONLY"
        assert pkt.summary["refinement_evidence_state"] == "NOT_OBSERVED"
        assert pkt.summary["start_pts"] == 90000
        # Half-open resolve_end: first PTS strictly after 180000 is 183000 (ordinal 61)
        assert pkt.summary["end_pts"] == 183000
        assert pkt.summary["start_frame_ordinal"] == 30
        assert pkt.summary["end_frame_ordinal"] == 61
        assert pkt.summary["is_vfr"] is False

    def test_refuses_nominal_fps_multiplication_and_ambiguous_pts(self) -> None:
        vfr_pkt = inspect_candidate_temporal(
            {
                "candidate": {
                    "evidence_class": "MATCHED",
                    "frame_accurate": False,
                    "start_sec": 1,
                    "end_sec": 2,
                },
                "derivation_method": "SECONDS_TIMES_NOMINAL_FPS",
                "pts_ticks": [0, 3000, 6000, 9000],
            }
        )
        assert vfr_pkt.status == ReadinessStatus.BLOCKED
        assert "VFR_NOMINAL_FPS_MULTIPLICATION_FORBIDDEN" in vfr_pkt.blockers

        non_mono_pkt = inspect_candidate_temporal(
            {
                "candidate": {
                    "evidence_class": "MATCHED",
                    "frame_accurate": False,
                    "start_sec": 0,
                    "end_sec": 1,
                },
                "pts_ticks": [0, 6000, 3000, 9000],
            }
        )
        assert non_mono_pkt.status == ReadinessStatus.BLOCKED
        assert "PTS_TABLE_NON_MONOTONIC_OR_AMBIGUOUS" in non_mono_pkt.blockers

        dup_pkt = inspect_candidate_temporal(
            {
                "candidate": {
                    "evidence_class": "MATCHED",
                    "frame_accurate": False,
                    "start_sec": 0,
                    "end_sec": 1,
                },
                "pts_ticks": [0, 3000, 3000, 6000],
            }
        )
        assert dup_pkt.status == ReadinessStatus.BLOCKED
        assert "PTS_TABLE_NON_MONOTONIC_OR_AMBIGUOUS" in dup_pkt.blockers


class TestMega07EditorialLineage:
    def test_valid_accept_lineage_and_plan_pinning(self) -> None:
        rb = _make_v1_bundle_record()
        hd = _make_human_decision_record(rb, decision_class="ACCEPT")
        pkt = inspect_editorial_lineage(
            {
                "review_bundle": rb,
                "human_decision": hd,
                "plan_lineage": {
                    "review_bundle_digest": rb["record_digest"],
                    "human_decision_digest": hd["record_digest"],
                },
            }
        )
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.summary["lineage_valid"] is True
        assert pkt.summary["decision_class"] == "ACCEPT"

    def test_reject_decision_ai_suggestion_or_digest_mismatch_blocked(self) -> None:
        rb = _make_v1_bundle_record()
        hd_reject = _make_human_decision_record(rb, decision_class="REJECT")
        rej_pkt = inspect_editorial_lineage(
            {
                "review_bundle": rb,
                "human_decision": hd_reject,
            }
        )
        assert rej_pkt.status == ReadinessStatus.BLOCKED
        assert "HUMAN_DECISION_REJECTED_CANDIDATE" in rej_pkt.blockers

        hd_accept = _make_human_decision_record(rb, decision_class="ACCEPT")
        ai_pkt = inspect_editorial_lineage(
            {
                "review_bundle": rb,
                "human_decision": hd_accept,
                "ai_generated_decision": True,
            }
        )
        assert ai_pkt.status == ReadinessStatus.BLOCKED
        assert "AI_SUGGESTION_NOT_HUMAN_DECISION" in ai_pkt.blockers

        bad_plan_pkt = inspect_editorial_lineage(
            {
                "review_bundle": rb,
                "human_decision": hd_accept,
                "plan_lineage": {
                    "review_bundle_digest": rb["record_digest"],
                    "human_decision_digest": "f" * 64,
                },
            }
        )
        assert bad_plan_pkt.status == ReadinessStatus.BLOCKED
        assert "PLAN_LINEAGE_DIGEST_MISMATCH" in bad_plan_pkt.blockers


class TestMega07QcExportReadiness:
    def test_bare_pass_and_missing_editorial_qc_refused(self) -> None:
        bare_pkt = inspect_qc_export_readiness({"qc_report": "PASS"})
        assert bare_pkt.status == ReadinessStatus.BLOCKED
        assert "BARE_PASS_QC_INSUFFICIENT" in bare_pkt.blockers

        tech_only_pkt = inspect_qc_export_readiness(
            {
                "qc_report": {
                    "origin": "SYNTHETIC_FIXTURE",
                    "technical_checks": {
                        "pts_monotonic": True,
                        "duration_match": True,
                    },
                }
            }
        )
        assert tech_only_pkt.status == ReadinessStatus.BLOCKED
        assert "EDITORIAL_QC_CHECKS_MISSING" in tech_only_pkt.blockers

    def test_dual_axis_qc_passes_synthetic_but_always_refuses_production_export(
        self,
    ) -> None:
        qc_payload = {
            "origin": "SYNTHETIC_FIXTURE",
            "technical_checks": {
                "pts_monotonic": True,
                "duration_match": True,
            },
            "editorial_checks": {
                "human_decision_linked": True,
                "boundary_intent_preserved": True,
            },
        }
        pkt = inspect_qc_export_readiness({"qc_report": qc_payload})
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.summary["production_export_authorized"] is False
        assert pkt.summary["export_status"] == "REFUSED_NOT_AUTHORIZED"
        assert pkt.summary["binding_consumable"] is False

        export_req_pkt = inspect_qc_export_readiness(
            {
                "qc_report": qc_payload,
                "request_production_export": True,
            }
        )
        assert export_req_pkt.status == ReadinessStatus.BLOCKED
        assert "PRODUCTION_EXPORT_NOT_AUTHORIZED" in export_req_pkt.blockers
        assert export_req_pkt.summary["production_export_authorized"] is False
