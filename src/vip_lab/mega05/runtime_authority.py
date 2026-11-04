"""Packet P05b: Side-Effect-Free Runtime Authority State Machine.

Evaluates the mandatory five-stage Gate-1 runtime authorization progression:
1. ``PROVENANCE_OBSERVED``
2. ``SOURCE_USE_AUTHORIZED``
3. ``MODEL_ASSETS_VERIFIED``
4. ``RUNTIME_PERMITTED``
5. ``CAN_PROPOSE_EXECUTION``

In synthetic lab mode, transition to authentic runtime execution is always
refused BEFORE any runtime callback is invoked (``callback_invoked=False``).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Mapping

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-05.RUNTIME_AUTHORITY"


class RuntimeAuthorityStage(str, Enum):
    PROVENANCE_OBSERVED = "PROVENANCE_OBSERVED"
    SOURCE_USE_AUTHORIZED = "SOURCE_USE_AUTHORIZED"
    MODEL_ASSETS_VERIFIED = "MODEL_ASSETS_VERIFIED"
    RUNTIME_PERMITTED = "RUNTIME_PERMITTED"
    CAN_PROPOSE_EXECUTION = "CAN_PROPOSE_EXECUTION"


RUNTIME_AUTHORITY_STAGES: tuple[RuntimeAuthorityStage, ...] = (
    RuntimeAuthorityStage.PROVENANCE_OBSERVED,
    RuntimeAuthorityStage.SOURCE_USE_AUTHORIZED,
    RuntimeAuthorityStage.MODEL_ASSETS_VERIFIED,
    RuntimeAuthorityStage.RUNTIME_PERMITTED,
    RuntimeAuthorityStage.CAN_PROPOSE_EXECUTION,
)


def inspect_runtime_authority(
    payload: Mapping[str, Any],
    *,
    runtime_callback: Callable[[], Any] | None = None,
) -> ReadinessPacket:
    """Evaluate the 5-stage runtime authority chain without invoking ``runtime_callback``."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "RUNTIME_AUTHORITY_NOT_MAPPING",
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
                code="RUNTIME_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Self-declared runtime authority flags were stripped in synthetic lab",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    stage_results: dict[str, str] = {}
    first_refusal_stage: str | None = None

    # Stage 1: PROVENANCE_OBSERVED (can be satisfied synthetically if provenance_digest is valid 64-hex)
    prov_digest = cleaned.get("provenance_digest")
    if (
        isinstance(prov_digest, str)
        and len(prov_digest) == 64
        and all(c in "0123456789abcdef" for c in prov_digest)
    ):
        stage_results[RuntimeAuthorityStage.PROVENANCE_OBSERVED.value] = (
            "OBSERVED_SYNTHETIC"
        )
    else:
        stage_results[RuntimeAuthorityStage.PROVENANCE_OBSERVED.value] = "REFUSED"
        first_refusal_stage = RuntimeAuthorityStage.PROVENANCE_OBSERVED.value
        code = "RUNTIME_PROVENANCE_MISSING_OR_INVALID"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Stage PROVENANCE_OBSERVED failed: valid 64-hex provenance_digest required",
                field_path="provenance_digest",
            )
        )

    # Stage 2: SOURCE_USE_AUTHORIZED — requires real owner source-use authorization,
    # which is never granted in synthetic lab mode.
    stage_results[RuntimeAuthorityStage.SOURCE_USE_AUTHORIZED.value] = (
        "NOT_AUTHORIZED_IN_SYNTHETIC_LAB"
    )
    if first_refusal_stage is None:
        first_refusal_stage = RuntimeAuthorityStage.SOURCE_USE_AUTHORIZED.value
    reasons.append("SOURCE_USE_NOT_AUTHORIZED")
    blockers.append("SOURCE_USE_NOT_AUTHORIZED")
    findings.append(
        ReadinessFinding(
            code="SOURCE_USE_NOT_AUTHORIZED",
            status=ReadinessStatus.NOT_AUTHORIZED,
            message="Stage SOURCE_USE_AUTHORIZED refused: real archive source use is not authorized",
            field_path="source_use_authorized",
        )
    )

    # Stage 3: MODEL_ASSETS_VERIFIED — authentic weights are not loaded in synthetic lab
    stage_results[RuntimeAuthorityStage.MODEL_ASSETS_VERIFIED.value] = (
        "SYNTHETIC_ONLY_NOT_AUTHENTIC"
    )
    reasons.append("AUTHENTIC_MODEL_ASSETS_NOT_VERIFIED")
    blockers.append("AUTHENTIC_MODEL_ASSETS_NOT_VERIFIED")
    findings.append(
        ReadinessFinding(
            code="AUTHENTIC_MODEL_ASSETS_NOT_VERIFIED",
            status=ReadinessStatus.NOT_AUTHORIZED,
            message="Stage MODEL_ASSETS_VERIFIED refused: authentic model weights are not verified on disk",
            field_path="model_assets_verified",
        )
    )

    # Stage 4: RUNTIME_PERMITTED
    stage_results[RuntimeAuthorityStage.RUNTIME_PERMITTED.value] = "REFUSED"
    reasons.append("RUNTIME_EXECUTION_NOT_PERMITTED")
    blockers.append("RUNTIME_EXECUTION_NOT_PERMITTED")

    # Stage 5: CAN_PROPOSE_EXECUTION
    stage_results[RuntimeAuthorityStage.CAN_PROPOSE_EXECUTION.value] = "REFUSED"
    reasons.append("CAN_PROPOSE_EXECUTION_FALSE")
    blockers.append("CAN_PROPOSE_EXECUTION_FALSE")

    # Hard guarantee: runtime_callback is NEVER called.
    callback_provided = runtime_callback is not None
    callback_invoked = False

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=ReadinessStatus.NOT_AUTHORIZED,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_AUTHORIZED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "ordered_stages": [s.value for s in RUNTIME_AUTHORITY_STAGES],
            "stage_results": stage_results,
            "first_refusal_stage": first_refusal_stage,
            "can_propose_execution": False,
            "callback_provided": callback_provided,
            "callback_invoked": callback_invoked,
        },
    )
