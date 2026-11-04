"""Regression tests for Wave MEGA-05 (P05a, P05b, P05c): Gate-1 Model Assets,
Runtime Authority State Machine, and Three-Arm Benchmark Entry Guard.
"""

from __future__ import annotations

from typing import Any

from vip_fvs.synthetic_profiles import CLOSED_SYNTHETIC_PROFILE_IDS
from vip_lab.common import ReadinessStatus
from vip_lab.mega05 import (
    RUNTIME_AUTHORITY_STAGES,
    inspect_benchmark_entry,
    inspect_model_asset_claims,
    inspect_runtime_authority,
)


def _make_three_arm_claims() -> list[dict[str, Any]]:
    common_proto = {
        "corpus_snapshot_digest": "1" * 64,
        "query_set_digest": "2" * 64,
        "window_policy_digest": "3" * 64,
        "top_k": 5,
    }
    return [
        {"profile_id": "vip-v1-siglip-base-224", **common_proto},
        {"profile_id": "vip-v2-siglip2-base-224", **common_proto},
        {"profile_id": "vip-v2-siglip2-so400m-384", **common_proto},
    ]


class TestMega05ModelAssetClaims:
    def test_three_profiles_validated_with_distinct_semantic_spaces(self) -> None:
        pkt = inspect_model_asset_claims({"profiles": _make_three_arm_claims()})
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.execution_authorized is False
        assert pkt.summary["authentic_model_execution"] is False
        assert pkt.summary["authentic_weights_verified"] is False

        validated = {
            row["profile_id"]: row for row in pkt.summary["validated_profiles"]
        }
        assert set(validated.keys()) == set(CLOSED_SYNTHETIC_PROFILE_IDS)
        assert validated["vip-v1-siglip-base-224"]["embedding_dim"] == 768
        assert validated["vip-v1-siglip-base-224"]["device_backend"] == "cpu"
        assert validated["vip-v1-siglip-base-224"]["precision_policy_id"] == "v1-float32"
        assert validated["vip-v2-siglip2-base-224"]["embedding_dim"] == 768
        assert validated["vip-v2-siglip2-so400m-384"]["embedding_dim"] == 1152
        assert validated["vip-v2-siglip2-so400m-384"]["row_width_bytes"] == 4608
        assert validated["vip-v2-siglip2-so400m-384"]["authentic_model_evidence"] == "NOT_OBSERVED"

        # 768D V1 and 768D V2 Base must never share a semantic_space_id
        assert (
            validated["vip-v1-siglip-base-224"]["semantic_space_id"]
            != validated["vip-v2-siglip2-base-224"]["semantic_space_id"]
        )

    def test_refuses_semantic_space_collision_download_and_authentic_claim(
        self,
    ) -> None:
        claims = _make_three_arm_claims()
        claims[0]["semantic_space_id"] = "shared_768d_space"
        claims[1]["semantic_space_id"] = "shared_768d_space"
        collision_pkt = inspect_model_asset_claims({"profiles": claims})
        assert collision_pkt.status == ReadinessStatus.INVALID
        assert "MODEL_PROFILE_SEMANTIC_SPACE_ID_MISMATCH" in collision_pkt.blockers

        dl_claims = _make_three_arm_claims()
        dl_claims[2]["allow_download"] = True
        dl_pkt = inspect_model_asset_claims({"profiles": dl_claims})
        assert dl_pkt.status == ReadinessStatus.BLOCKED
        assert "MODEL_DOWNLOAD_FORBIDDEN" in dl_pkt.blockers

        auth_claims = _make_three_arm_claims()
        auth_claims[2]["claim_authentic_execution"] = True
        auth_pkt = inspect_model_asset_claims({"profiles": auth_claims})
        assert auth_pkt.status == ReadinessStatus.BLOCKED
        assert "SYNTHETIC_EMBEDDING_NOT_AUTHENTIC_MODEL" in auth_pkt.blockers

        bad_prof_claims = _make_three_arm_claims()
        bad_prof_claims[0]["device_backend"] = "pytorch-mps"
        bad_prof_pkt = inspect_model_asset_claims({"profiles": bad_prof_claims})
        assert bad_prof_pkt.status == ReadinessStatus.BLOCKED
        assert "MODEL_PROFILE_CONTRACT_VIOLATION" in bad_prof_pkt.blockers


class TestMega05RuntimeAuthority:
    def test_runtime_authority_never_invokes_callback_and_refuses_execution(
        self,
    ) -> None:
        callback_called = False

        def _forbidden_runtime_callback() -> None:
            nonlocal callback_called
            callback_called = True
            raise AssertionError("runtime_callback must never be invoked")

        pkt = inspect_runtime_authority(
            {
                "provenance_digest": "a" * 64,
                "trusted": True,
                "execution_authorized": True,
            },
            runtime_callback=_forbidden_runtime_callback,
        )
        assert callback_called is False
        assert pkt.status == ReadinessStatus.NOT_AUTHORIZED
        assert pkt.execution_authorized is False
        assert pkt.summary["callback_provided"] is True
        assert pkt.summary["callback_invoked"] is False
        assert pkt.summary["can_propose_execution"] is False
        assert pkt.summary["ordered_stages"] == [
            s.value for s in RUNTIME_AUTHORITY_STAGES
        ]
        assert pkt.summary["first_refusal_stage"] == "SOURCE_USE_AUTHORIZED"


class TestMega05BenchmarkEntryGuard:
    def test_valid_three_arm_benchmark_entry_remains_not_run(self) -> None:
        pkt = inspect_benchmark_entry(
            {
                "arms": _make_three_arm_claims(),
                "provenance_digest": "b" * 64,
            }
        )
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.execution_authorized is False
        assert pkt.summary["benchmark_status"] == "NOT_RUN"
        assert pkt.summary["winner"] is None
        assert pkt.summary["selected_model"] is None
        assert pkt.summary["gate_decision"] == "NOT_AUTHORIZED"
        assert pkt.summary["authentic_benchmark_executed"] is False

    def test_protocol_drift_or_premature_winner_blocked(self) -> None:
        drifted_arms = _make_three_arm_claims()
        drifted_arms[1]["query_set_digest"] = "9" * 64
        drift_pkt = inspect_benchmark_entry({"arms": drifted_arms})
        assert drift_pkt.status == ReadinessStatus.BLOCKED
        assert "BENCHMARK_PROTOCOL_DRIFT" in drift_pkt.blockers

        winner_pkt = inspect_benchmark_entry(
            {
                "arms": _make_three_arm_claims(),
                "winner": "vip-v2-siglip2-so400m-384",
            }
        )
        assert winner_pkt.status == ReadinessStatus.BLOCKED
        assert "BENCHMARK_PREMATURE_WINNER_FORBIDDEN" in winner_pkt.blockers
