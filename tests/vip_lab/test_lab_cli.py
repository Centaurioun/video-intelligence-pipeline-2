"""Regression tests for Packet PX Lab CLI (src/vip_lab/cli.py)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gate0.config_freeze import POLICY_ROOT_IDENTITY, SCHEMA_VERSION
from vip_lab.cli import (
    EXIT_BLOCKED,
    EXIT_INVALID,
    EXIT_READY_SYNTHETIC,
    run_cli,
)
from vip_lab.common import canonical_json_dumps


def _make_cli_program_payload() -> dict[str, Any]:
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
