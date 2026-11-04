"""Regression tests for Packet PX Lab CLI (src/vip_lab/cli.py)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gate0.identity import digest_bytes, digest_json
from vip_lab.cli import (
    EXIT_BLOCKED,
    EXIT_INVALID,
    EXIT_READY_SYNTHETIC,
    run_cli,
)
from vip_lab.common import canonical_json_dumps


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


def _make_cli_program_payload() -> dict[str, Any]:
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
            }
        },
        "mega07": {
            "qc_export": {
                "qc_report": {
                    "origin": "SYNTHETIC_FIXTURE",
                    "technical_checks": {"pts_monotonic": True},
                    "editorial_checks": {"human_decision_linked": True},
                }
            }
        },
    }


class TestLabCli:
    def test_cli_preflight_s5_and_summarize_program_exit_codes(
        self, tmp_path: Path
    ) -> None:
        s5_file = tmp_path / "s5.json"
        s5_file.write_text(
            canonical_json_dumps(
                {
                    "source_id": "src_01",
                    "source_revision": "rev_1",
                    "declared_sha256": "a" * 64,
                    "declared_size": 64,
                    "relative_path": "clips/clip.mp4",
                }
            ),
            encoding="utf-8",
        )
        code, out = run_cli(["preflight-s5", "--input", str(s5_file)])
        assert code == EXIT_READY_SYNTHETIC
        assert out["status"] == "READY_SYNTHETIC"
        assert out["execution_authorized"] is False

        prog_file = tmp_path / "prog.json"
        prog_file.write_text(
            canonical_json_dumps(_make_cli_program_payload()),
            encoding="utf-8",
        )
        code_prog, out_prog = run_cli(
            ["summarize-program", "--input", str(prog_file)]
        )
        assert code_prog == EXIT_READY_SYNTHETIC
        assert out_prog["status"] == "READY_SYNTHETIC"

    def test_cli_blocked_and_invalid_exit_codes(self, tmp_path: Path) -> None:
        # Gate-3 bare PASS QC -> BLOCKED (exit code 10)
        g3_blocked = tmp_path / "g3_blocked.json"
        g3_blocked.write_text(
            canonical_json_dumps({"qc_export": {"qc_report": "PASS"}}),
            encoding="utf-8",
        )
        code_blk, out_blk = run_cli(
            ["preflight-gate3", "--input", str(g3_blocked)]
        )
        assert code_blk == EXIT_BLOCKED
        assert out_blk["status"] == "BLOCKED"

        # Duplicate JSON key -> INVALID (exit code 30)
        dup_file = tmp_path / "dup.json"
        dup_file.write_text('{"a": 1, "a": 2}', encoding="utf-8")
        code_inv, out_inv = run_cli(
            ["preflight-gate0", "--input", str(dup_file)]
        )
        assert code_inv == EXIT_INVALID
        assert out_inv["status"] == "INVALID"
