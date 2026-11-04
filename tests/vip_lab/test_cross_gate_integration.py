"""Regression tests for Packet PX Cross-Gate Integration (src/vip_lab/integration.py)."""

from __future__ import annotations

from typing import Any

from gate0.config_freeze import POLICY_ROOT_IDENTITY, SCHEMA_VERSION
from vip_lab.common import LAB_PROGRAM_VERSION, ReadinessStatus
from vip_lab.integration import summarize_program


def _make_full_synthetic_program_payload() -> dict[str, Any]:
    digests = {
        "corpus_snapshot_digest": "1" * 64,
        "split_manifest_digest": "2" * 64,
        "query_set_digest": "3" * 64,
        "gold_event_digest": "4" * 64,
        "model_bundle_digest": "5" * 64,
        "prompt_template_digest": "6" * 64,
    }
    common_proto = {
        "corpus_snapshot_digest": "1" * 64,
        "query_set_digest": "2" * 64,
        "window_policy_digest": "3" * 64,
        "top_k": 5,
    }
    return {
        "mega03": {
            "s5_declaration": {
                "source_id": "src_01",
                "source_revision": "rev_001",
                "declared_sha256": "a" * 64,
                "declared_size": 128,
                "relative_path": "clips/ballet_01.mp4",
            },
            "stream_namespace": {
                "ffprobe_stream_index": 0,
                "mp4_track_index": 0,
                "mp4_trak_count": 1,
            },
            "expect_negative_stream_refusal": True,
        },
        "mega04": {
            "config": {
                "schema_version": SCHEMA_VERSION,
                "policy_root_identity": POLICY_ROOT_IDENTITY,
                **digests,
                "window_policy": {"window_sec": 4, "stride_sec": 2},
                "keyframes_per_window": 4,
                "preprocess_id": "siglip_224_rgb",
                "similarity_metric": "cosine",
                "top_k": 5,
            },
            "observed_digests": digests,
        },
        "mega05": {
            "arms": [
                {
                    "profile_id": "vip-v1-siglip-base-224",
                    "weights_sha256": "a" * 64,
                    **common_proto,
                },
                {
                    "profile_id": "vip-v2-siglip2-base-224",
                    "weights_sha256": "b" * 64,
                    **common_proto,
                },
                {
                    "profile_id": "vip-v2-siglip2-so400m-384",
                    "weights_sha256": "c" * 64,
                    **common_proto,
                },
            ]
        },
        "mega06": {
            "workload_plan": {
                "seed": 11,
                "jobs": 3,
                "stages": 2,
                "artifact_bytes": 64,
                "f01_sha": "1" * 40,
                "c04_sha": "2" * 40,
                "e05_sha": "3" * 40,
                "config_digest": "a" * 64,
            },
            "measurement_review": {
                "measurements": [
                    {
                        "metric_id": "query_p95_ms",
                        "unit": "ms",
                        "value": 9.5,
                        "evidence_class": "MEASURED",
                        "status": "OBSERVED",
                        "provenance_digest": "d" * 64,
                    }
                ]
            },
        },
        "mega07": {
            "candidate_temporal": {
                "candidate": {
                    "evidence_class": "MATCHED",
                    "frame_accurate": False,
                    "start_sec": 1,
                    "end_sec": 2,
                },
                "time_base": {"num": 1, "den": 90000},
                "pts_ticks": [i * 3000 for i in range(91)],
            },
            "qc_export": {
                "qc_report": {
                    "origin": "SYNTHETIC_FIXTURE",
                    "technical_checks": {"pts_monotonic": True},
                    "editorial_checks": {"human_decision_linked": True},
                }
            },
        },
        "owner_approved": True,
        "execution_authorized": True,
    }


class TestCrossGateIntegration:
    def test_summarize_program_all_five_waves_ready_synthetic_never_authorizes(
        self,
    ) -> None:
        payload = _make_full_synthetic_program_payload()
        pkt = summarize_program(payload)
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.synthetic_only is True
        assert pkt.execution_authorized is False
        assert pkt.owner_approval_status == "NOT_GRANTED"
        assert pkt.gate_verdict == "NOT_APPROVED"
        assert pkt.summary["program_version"] == LAB_PROGRAM_VERSION
        assert pkt.summary["git_snapshot_identity"] == "NOT_OBSERVED (GIT_DIR_ABSENT)"
        assert pkt.summary["pr258_status"] == "EXTERNAL_PR_NOT_MERGED_IN_SNAPSHOT"
        assert pkt.summary["authentic_model_execution"] is False
        assert pkt.summary["real_archive_observed"] is False
        assert pkt.summary["production_export_authorized"] is False
        assert pkt.summary["gate0_verdict"] == "NOT_RUN"
        assert pkt.summary["gate1_verdict"] == "NOT_AUTHORIZED"
        assert pkt.summary["gate2_verdict"] == "NOT_DETERMINED"
        assert pkt.summary["gate3_export_status"] == "REFUSED_NOT_AUTHORIZED"
        assert set(pkt.summary["stage_statuses"].keys()) == {
            "MEGA-03",
            "MEGA-04",
            "MEGA-05",
            "MEGA-06",
            "MEGA-07",
        }

    def test_upstream_mega03_blocker_taints_downstream_mega07(self) -> None:
        payload = _make_full_synthetic_program_payload()
        # Do not allow negative stream refusal -> MEGA-03 becomes BLOCKED
        payload["mega03"]["expect_negative_stream_refusal"] = False
        pkt = summarize_program(payload)
        assert pkt.status == ReadinessStatus.BLOCKED
        assert "DOWNSTREAM_MEGA07_TAINTED_BY_MEGA03_BLOCKER" in pkt.blockers
