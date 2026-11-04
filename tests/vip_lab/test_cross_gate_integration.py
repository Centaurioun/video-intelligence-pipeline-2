"""Regression tests for Packet PX Cross-Gate Integration (src/vip_lab/integration.py)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gate0.identity import digest_bytes, digest_json
from vip_lab.common import LAB_PROGRAM_VERSION, ReadinessStatus
from vip_lab.integration import summarize_program


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config/gate0/default.json"


def _synth_digest(label: str) -> str:
    return digest_json({"synthetic_metadata": label})


def _make_gate0_config_and_observed() -> tuple[dict[str, Any], dict[str, str]]:
    config: dict[str, Any] = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
    config["corpus"]["source_root"] = "/synthetic-input-root-that-must-not-be-opened"
    config["corpus"]["source_manifest_digest"] = _synth_digest("source-manifest-rev-1")
    config["model"].update(
        {
            "model_identity": "synthetic-local-model-identity",
            "weights_digest": _synth_digest("weights"),
            "processor_digest": _synth_digest("processor"),
            "space_id": "synthetic-embedding-space",
            "dimension": 64,
        }
    )
    config["policy"]["egress_manifest_digest"] = _synth_digest("egress-manifest")
    config["sandbox"].update(
        {
            "bwrap_version": "synthetic-bwrap-1.0",
            "bwrap_digest": _synth_digest("bwrap"),
            "interpreter_digest": _synth_digest("interpreter"),
        }
    )
    config["blinding"]["blind_mapping_digest"] = _synth_digest("blind-mapping")

    observed = {
        "post_inventory:corpus.source_manifest_digest": config["corpus"][
            "source_manifest_digest"
        ],
        "model:model.weights_digest": config["model"]["weights_digest"],
        "model:model.processor_digest": config["model"]["processor_digest"],
        "policy:policy.egress_manifest_digest": config["policy"][
            "egress_manifest_digest"
        ],
        "sandbox:sandbox.bwrap_digest": config["sandbox"]["bwrap_digest"],
        "sandbox:sandbox.interpreter_digest": config["sandbox"]["interpreter_digest"],
        "blinding:blinding.blind_mapping_digest": config["blinding"][
            "blind_mapping_digest"
        ],
        "policy:policy.review_input.authorized_root": digest_bytes(
            config["policy"]["review_input"]["authorized_root"].encode("utf-8")
        ),
    }
    return config, observed


def _make_full_synthetic_program_payload() -> dict[str, Any]:
    g0_cfg, g0_observed = _make_gate0_config_and_observed()
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
            "config": g0_cfg,
            "observed_digests": g0_observed,
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
                "cost_units": 10,
                "fault_position": 0,
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
                        "status": "MEASURED",
                        "derivation": "synthetic_timer",
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
