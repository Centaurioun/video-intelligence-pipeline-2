"""Packet P05c: Gate-1 Three-Arm Benchmark Entry Guard.

Validates synthetic three-arm Gate-1 benchmark readiness across:
- ``vip-v1-siglip-base-224``
- ``vip-v2-siglip2-base-224``
- ``vip-v2-siglip2-so400m-384``

Ensures protocol parity across arms, semantic-space non-collision, and keeps:
- ``benchmark_status = "NOT_RUN"``
- ``winner = None``
- ``selected_model = None``
- ``gate_decision = "NOT_AUTHORIZED"``
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from vip_fvs.synthetic_profiles import SYNTHETIC_PROFILE_IDS

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)
from .model_assets import inspect_model_asset_claims
from .runtime_authority import inspect_runtime_authority


STAGE_ID = "MEGA-05.BENCHMARK_ENTRY_GUARD"
REQUIRED_PROTOCOL_DIGEST_KEYS = (
    "corpus_snapshot_digest",
    "query_set_digest",
    "window_policy_digest",
)


def inspect_benchmark_entry(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Inspect a three-arm Gate-1 benchmark entry specification in synthetic lab mode."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "BENCHMARK_ENTRY_NOT_MAPPING",
            "payload must be a mapping",
        )

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="BENCHMARK_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted self-declared authority flags in benchmark entry payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if cleaned.get("winner") is not None or cleaned.get("selected_model") is not None:
        code = "BENCHMARK_PREMATURE_WINNER_FORBIDDEN"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Synthetic benchmark entry cannot declare a winner or selected_model",
                field_path="winner",
            )
        )

    arms = cleaned.get("arms")
    if not isinstance(arms, Sequence) or len(arms) != 3:
        code = "BENCHMARK_THREE_ARMS_REQUIRED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="Gate-1 three-arm benchmark entry requires exactly 3 arm specifications",
                field_path="arms",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            owner_approval_status="NOT_GRANTED",
            gate_verdict="NOT_AUTHORIZED",
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "benchmark_status": "NOT_RUN",
                "winner": None,
                "selected_model": None,
                "gate_decision": "NOT_AUTHORIZED",
            },
        )

    profile_claims: list[Mapping[str, Any]] = []
    reference_protocol: dict[str, Any] | None = None
    observed_profile_ids: list[str] = []

    for idx, arm in enumerate(arms):
        if not isinstance(arm, Mapping):
            code = "BENCHMARK_ARM_NOT_MAPPING"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message=f"arms[{idx}] must be a mapping",
                    field_path=f"arms[{idx}]",
                )
            )
            continue

        prof_id = str(arm.get("profile_id", ""))
        observed_profile_ids.append(prof_id)
        profile_claims.append(arm)

        # Validate protocol parity across all 3 arms
        arm_proto: dict[str, Any] = {}
        for k in REQUIRED_PROTOCOL_DIGEST_KEYS:
            val = arm.get(k)
            try:
                validate_hex_digest(
                    val,
                    length=64,
                    field_name=f"arms[{idx}].{k}",
                    error_code="BENCHMARK_PROTOCOL_DIGEST_INVALID",
                )
                arm_proto[k] = val
            except VipLabError as exc:
                if exc.code not in blockers:
                    blockers.append(exc.code)
                    reasons.append(exc.code)
                findings.append(
                    ReadinessFinding(
                        code=exc.code,
                        status=ReadinessStatus.INVALID,
                        message=exc.message,
                        field_path=exc.field_path,
                    )
                )

        top_k = arm.get("top_k", 5)
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
            code = "BENCHMARK_INVALID_TOP_K"
            if code not in blockers:
                blockers.append(code)
                reasons.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message=f"arms[{idx}].top_k must be a positive integer",
                    field_path=f"arms[{idx}].top_k",
                )
            )
        arm_proto["top_k"] = top_k

        if reference_protocol is None:
            reference_protocol = arm_proto
        elif arm_proto != reference_protocol:
            code = "BENCHMARK_PROTOCOL_DRIFT"
            if code not in blockers:
                blockers.append(code)
                reasons.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=f"Protocol mismatch between arm 0 and arm {idx}",
                    field_path=f"arms[{idx}]",
                )
            )

    if set(observed_profile_ids) != set(SYNTHETIC_PROFILE_IDS):
        code = "BENCHMARK_PROFILE_SET_MISMATCH"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=(
                    f"Expected exact three profiles {list(SYNTHETIC_PROFILE_IDS)}, "
                    f"got {observed_profile_ids}"
                ),
                field_path="arms",
            )
        )

    asset_pkt = inspect_model_asset_claims({"profiles": profile_claims})
    if asset_pkt.status != ReadinessStatus.READY_SYNTHETIC:
        for b in asset_pkt.blockers:
            if b not in blockers:
                blockers.append(b)
                reasons.append(b)
        findings.extend(asset_pkt.findings)

    runtime_pkt = inspect_runtime_authority(
        {"provenance_digest": cleaned.get("provenance_digest", "a" * 64)}
    )
    reasons.append("AUTHENTIC_BENCHMARK_EXECUTION_NOT_AUTHORIZED")

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("BENCHMARK_SYNTHETIC_THREE_ARM_ENTRY_READY")

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_AUTHORIZED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "benchmark_status": "NOT_RUN",
            "winner": None,
            "selected_model": None,
            "gate_decision": "NOT_AUTHORIZED",
            "authentic_benchmark_executed": False,
            "observed_profile_ids": observed_profile_ids,
            "model_assets": dict(asset_pkt.summary),
            "runtime_authority": dict(runtime_pkt.summary),
        },
    )
