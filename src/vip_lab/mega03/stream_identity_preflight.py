"""Packet P03b: Stream-Identity Negative Preflight over metadata-only synthetic indices.

Enforces the negative namespace guardrails from:
- ``src/gate3/stream_identity.py``
- ``src/vip_fvs/stream_identity_gate.py``
- ``docs/decisions/2026-10-25-g3-a7-stream-namespace-positive-mapping-disposition.md``

Specifically:
1. ``ffprobe.streams[*].index``, ``mp4_track_index`` (0-based ``moov/trak`` ordinal),
   and ISO-BMFF ``tkhd.track_ID`` are distinct opaque namespaces.
2. Numeric coincidence (e.g. ``ffprobe_stream_index == 0`` and ``mp4_track_index == 0``)
   is NEVER proof of stream identity (``POSITIONAL_IDENTITY_DERIVATION`` refused).
3. Multi-``trak`` containers or ambiguous candidate tracks are refused.
4. Any claim of positive ISO-BMFF ``tkhd.track_ID`` <-> ``ffprobe.stream.index``
   correspondence without a verified ``gate3.stream_identity.v1`` proof is refused.
"""

from __future__ import annotations

from typing import Any, Mapping

from gate3.stream_identity import (
    POSITIONAL_IDENTITY_DERIVATION,
    REASON_POSITIONAL_STREAM_IDENTITY_FORBIDDEN,
    evaluate_stream_identity,
)

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-03.STREAM_IDENTITY_PREFLIGHT"


def _is_nonneg_int(val: Any) -> bool:
    return isinstance(val, int) and not isinstance(val, bool) and val >= 0


def inspect_stream_namespace(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Run negative stream-identity preflight on metadata-only namespace claims
    or delegated ``snapshot_record`` + ``binding_record`` pairs.
    """
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "STREAM_PREFLIGHT_NOT_MAPPING",
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
                code="STREAM_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Self-declared authority flags in stream namespace payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    # Path 1: If full snapshot_record and binding_record are supplied, delegate
    # directly to gate3.stream_identity.evaluate_stream_identity as well.
    snapshot_record = cleaned.get("snapshot_record")
    binding_record = cleaned.get("binding_record")
    delegated_ev = None
    if isinstance(snapshot_record, Mapping) and isinstance(binding_record, Mapping):
        delegated_ev = evaluate_stream_identity(
            dict(snapshot_record), dict(binding_record)
        )
        if not delegated_ev.verified:
            for r_code in delegated_ev.reason_codes:
                reasons.append(r_code)
                blockers.append(r_code)
                findings.append(
                    ReadinessFinding(
                        code=r_code,
                        status=ReadinessStatus.BLOCKED,
                        message=f"gate3.stream_identity refused binding: {r_code}",
                        field_path="snapshot_record.stream_identity",
                    )
                )

    ffprobe_idx = cleaned.get("ffprobe_stream_index")
    mp4_track_idx = cleaned.get("mp4_track_index")
    mp4_track_id = cleaned.get("mp4_track_id")
    trak_count = cleaned.get("mp4_trak_count", 1)
    derivation = cleaned.get("identity_derivation")
    claim_positive_mapping = bool(cleaned.get("claim_positive_track_id_mapping", False))

    if not _is_nonneg_int(ffprobe_idx) or not _is_nonneg_int(mp4_track_idx):
        code = "STREAM_IDENTITY_MISSING_NAMESPACE_INDEX"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="Both ffprobe_stream_index and mp4_track_index must be non-negative integers",
                field_path="ffprobe_stream_index",
            )
        )

    if (
        not isinstance(trak_count, int)
        or isinstance(trak_count, bool)
        or trak_count <= 0
    ):
        code = "STREAM_IDENTITY_INVALID_TRAK_COUNT"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="mp4_trak_count must be a positive integer",
                field_path="mp4_trak_count",
            )
        )
    elif trak_count > 1:
        code = "STREAM_IDENTITY_MULTI_TRAK_AMBIGUOUS"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=f"Multi-trak container (mp4_trak_count={trak_count}) is ambiguous without proven stream correspondence",
                field_path="mp4_trak_count",
                details={"mp4_trak_count": trak_count},
            )
        )

    if derivation == POSITIONAL_IDENTITY_DERIVATION or bool(
        cleaned.get("assume_positional_equality", False)
    ):
        code = REASON_POSITIONAL_STREAM_IDENTITY_FORBIDDEN
        if code not in reasons:
            reasons.append(code)
            blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="Positional equality between ffprobe_stream_index and mp4_track_index is forbidden",
                field_path="identity_derivation",
            )
        )

    if claim_positive_mapping:
        code = "STREAM_NAMESPACE_POSITIVE_MAPPING_DEFERRED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message=(
                    "Positive ISO-BMFF tkhd.track_ID <-> ffprobe.stream.index mapping "
                    "is deferred per 2026-10-25-g3-a7-stream-namespace-positive-mapping-disposition.md"
                ),
                field_path="claim_positive_track_id_mapping",
            )
        )

    # Even if numbers match (e.g. ffprobe_stream_index == 0 and mp4_track_index == 0),
    # metadata-only indices alone NEVER prove stream correspondence unless backed by
    # a verified gate3.stream_identity.v1 proof (delegated_ev.verified == True).
    if delegated_ev is None or not delegated_ev.verified:
        code = "STREAM_IDENTITY_METADATA_ONLY_UNPROVEN"
        if code not in reasons:
            reasons.append(code)
            blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=(
                    "Opaque ffprobe_stream_index / mp4_track_index / mp4_track_id metadata "
                    "cannot prove stream correspondence without verified gate3.stream_identity.v1 evidence"
                ),
                details={
                    "ffprobe_stream_index": ffprobe_idx,
                    "mp4_track_index": mp4_track_idx,
                    "mp4_track_id": mp4_track_id,
                },
            )
        )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("STREAM_IDENTITY_DELEGATED_PROOF_VERIFIED")

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        evidence_state="MEASURED" if (delegated_ev and delegated_ev.verified) else NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "ffprobe_stream_index": ffprobe_idx,
            "mp4_track_index": mp4_track_idx,
            "mp4_track_id": mp4_track_id,
            "mp4_trak_count": trak_count,
            "identity_derivation": derivation,
            "stream_identity_verified": bool(delegated_ev and delegated_ev.verified),
            "positive_mapping_invented": False,
        },
    )
