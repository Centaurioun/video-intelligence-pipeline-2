"""Packet P03a: metadata-only synthetic S5 declaration preflight.

Never opens source files, reads snapshot evidence from disk, or grants admission.
Source digests, temporal records and source paths are untrusted declarations.
"""

from __future__ import annotations

import hashlib
from pathlib import PurePosixPath
from typing import Any, Mapping

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    canonical_json_dumps,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)


DEFAULT_S5_MAX_BYTES = 1024 * 1024  # 1 MiB bounded synthetic S5 read ceiling
STAGE_ID = "MEGA-03.S5_PREFLIGHT"


def _validate_relative_source_path(raw_path: Any) -> str:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise VipLabError(
            "S5_RELATIVE_PATH_MISSING",
            "relative_path must be a non-empty string",
            field_path="relative_path",
        )
    if "\x00" in raw_path:
        raise VipLabError(
            "S5_PATH_NUL_BYTE",
            "relative_path must not contain NUL bytes",
            field_path="relative_path",
        )
    if raw_path.startswith("/") or raw_path.startswith("\\"):
        raise VipLabError(
            "S5_PATH_TRAVERSAL_OR_ABSOLUTE",
            f"relative_path must be relative, got {raw_path!r}",
            field_path="relative_path",
        )
    if "\\" in raw_path:
        raise VipLabError(
            "S5_PATH_BACKSLASH_FORBIDDEN",
            "relative_path must use POSIX forward slashes",
            field_path="relative_path",
        )
    posix = PurePosixPath(raw_path)
    if posix.is_absolute() or not posix.parts:
        raise VipLabError(
            "S5_PATH_TRAVERSAL_OR_ABSOLUTE",
            f"relative_path is not a valid relative path: {raw_path!r}",
            field_path="relative_path",
        )
    for part in posix.parts:
        if part in ("", ".", ".."):
            raise VipLabError(
                "S5_PATH_TRAVERSAL_OR_ABSOLUTE",
                f"relative_path contains forbidden segment {part!r}: {raw_path!r}",
                field_path="relative_path",
            )
    return str(posix)


def _verify_temporal_binding_dict(
    tb_payload: Mapping[str, Any],
    *,
    expected_revision: str,
    expected_sha256: str,
    expected_size: int,
) -> tuple[int, str]:
    version = tb_payload.get("schema_version")
    if version not in (1, 2) or isinstance(version, bool):
        raise VipLabError(
            "S5_TEMPORAL_BINDING_INVALID",
            f"temporal_binding schema_version must be integer 1 or 2, got {version!r}",
            field_path="temporal_binding.schema_version",
        )
    ev_sha = validate_hex_digest(
        tb_payload.get("evidence_sha256"),
        length=64,
        field_name="temporal_binding.evidence_sha256",
        error_code="S5_TEMPORAL_BINDING_INVALID",
    )
    body = {k: v for k, v in tb_payload.items() if k != "evidence_sha256"}
    computed_sha = hashlib.sha256(canonical_json_dumps(body).encode("utf-8")).hexdigest()
    if computed_sha != ev_sha:
        raise VipLabError(
            "S5_TEMPORAL_BINDING_DIGEST_MISMATCH",
            "temporal_binding evidence_sha256 does not match canonical body digest",
            field_path="temporal_binding.evidence_sha256",
        )
    if (
        tb_payload.get("source_revision_id") != expected_revision
        or tb_payload.get("source_sha256") != expected_sha256
        or tb_payload.get("source_byte_count") != expected_size
    ):
        raise VipLabError(
            "S5_TEMPORAL_BINDING_MISMATCH",
            "temporal_binding source identity/digest/size does not match S5 declaration",
            field_path="temporal_binding",
        )
    return int(version), ev_sha


def inspect_s5_declaration(
    declaration: Mapping[str, Any],
    *,
    snapshot_root: str | None = None,
    max_bytes: int = DEFAULT_S5_MAX_BYTES,
) -> ReadinessPacket:
    """Inspect strictly declared synthetic S5 metadata; never open source bytes.

    The legacy snapshot_root argument is deliberately refused rather than used.
    No successful packet establishes custody, source authenticity, or E01 authority.
    """
    if not isinstance(declaration, Mapping):
        raise VipLabError("S5_DECLARATION_NOT_MAPPING", "declaration must be a mapping")
    if type(max_bytes) is not int or max_bytes <= 0:
        raise VipLabError("S5_INVALID_MAX_BYTES", "max_bytes must be a positive integer")

    cleaned, ignored = sanitize_untrusted_authority_claims(declaration)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = ["PR_258_DIRECT_CODE_ABSENT_IN_SNAPSHOT"]
    blockers: list[str] = []
    if ignored:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(ReadinessFinding(
            code="S5_UNTRUSTED_AUTHORITY_CLAIMS_STRIPPED",
            status=ReadinessStatus.NOT_AUTHORIZED,
            message="Self-declared source authority has no effect",
            details={"ignored_keys": list(ignored)},
        ))

    source_id = cleaned.get("source_id")
    revision = cleaned.get("source_revision")
    digest = cleaned.get("declared_sha256")
    size = cleaned.get("declared_size")
    try:
        if not isinstance(source_id, str) or not source_id.strip():
            raise VipLabError("S5_SOURCE_ID_INVALID", "source_id must be nonempty")
        if not isinstance(revision, str) or not revision.strip():
            raise VipLabError("S5_SOURCE_REVISION_INVALID", "source_revision must be nonempty")
        validate_hex_digest(
            digest, length=64, field_name="declared_sha256",
            error_code="S5_DECLARED_DIGEST_INVALID",
        )
        if type(size) is not int or size <= 0:
            raise VipLabError("S5_DECLARED_SIZE_INVALID", "declared_size must be positive")
        if size > max_bytes:
            raise VipLabError("S5_MAX_BYTES_EXCEEDED", "declared_size exceeds lab metadata limit")
        relative_path = _validate_relative_source_path(cleaned.get("relative_path"))
    except VipLabError as exc:
        return ReadinessPacket(
            stage_id=STAGE_ID, status=ReadinessStatus.INVALID,
            reasons=tuple(reasons + [exc.code]),
            blockers=(exc.code,),
            findings=tuple(findings + [ReadinessFinding(
                code=exc.code, status=ReadinessStatus.INVALID, message=exc.message,
                field_path=exc.field_path, details=exc.details,
            )]),
            summary={"admitted": False, "bytes_verified": False,
                     "snapshot_verified": False, "max_bytes": max_bytes},
        )

    # Explicitly fail closed: even a valid descriptor-relative path may be REAL MEDIA.
    # Never perform stat(), open(), read(), digest or snapshot verification here.
    if snapshot_root is not None:
        code = "S5_SOURCE_BYTE_ADMISSION_NOT_AUTHORIZED"
        return ReadinessPacket(
            stage_id=STAGE_ID, status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons + [code]), blockers=(code,),
            findings=tuple(findings + [ReadinessFinding(
                code=code, status=ReadinessStatus.NOT_AUTHORIZED,
                message="Lab S5 may validate declarations only; source roots are forbidden",
            )]),
            summary={
                "source_id": source_id, "source_revision": revision,
                "relative_path": relative_path, "admitted": False,
                "bytes_verified": False, "snapshot_verified": False,
                "pr258_status": "EXTERNAL_PR_NOT_MERGED_IN_SNAPSHOT",
            },
        )

    snapshot_declared_consistent = False
    snap = cleaned.get("snapshot")
    if snap is not None:
        if not isinstance(snap, Mapping) or (
            snap.get("source_revision_id") != revision
            or snap.get("snapshot_sha256") != digest
            or snap.get("source_byte_count") != size
        ):
            code = "S5_SNAPSHOT_DECLARATION_MISMATCH"
            return ReadinessPacket(
                stage_id=STAGE_ID, status=ReadinessStatus.INVALID,
                reasons=tuple(reasons + [code]), blockers=(code,),
                findings=tuple(findings + [ReadinessFinding(
                    code=code, status=ReadinessStatus.INVALID,
                    message="Declared snapshot fields are missing or inconsistent",
                )]),
                summary={"admitted": False, "bytes_verified": False,
                         "snapshot_verified": False},
            )
        snapshot_declared_consistent = True
        findings.append(ReadinessFinding(
            code="S5_SNAPSHOT_DECLARATION_CONSISTENT",
            status=ReadinessStatus.READY_SYNTHETIC,
            message="Record fields agree; snapshot bytes were not examined",
            evidence_state=NOT_OBSERVED,
        ))

    temporal_version = None
    temporal = cleaned.get("temporal_binding")
    if temporal is not None:
        try:
            if not isinstance(temporal, Mapping):
                raise VipLabError("S5_TEMPORAL_BINDING_INVALID", "temporal binding must be a mapping")
            temporal_version, _digest = _verify_temporal_binding_dict(
                temporal, expected_revision=revision,
                expected_sha256=digest, expected_size=size,
            )
        except VipLabError as exc:
            return ReadinessPacket(
                stage_id=STAGE_ID, status=ReadinessStatus.INVALID,
                reasons=tuple(reasons + [exc.code]), blockers=(exc.code,),
                findings=tuple(findings + [ReadinessFinding(
                    code=exc.code, status=ReadinessStatus.INVALID, message=exc.message,
                )]),
                summary={"admitted": False, "bytes_verified": False,
                         "snapshot_verified": False},
            )
        findings.append(ReadinessFinding(
            code="S5_TEMPORAL_DECLARATION_DIGEST_CONSISTENT",
            status=ReadinessStatus.READY_SYNTHETIC,
            message="Self-declared temporal record is internally consistent, not source-measured",
            evidence_state=NOT_OBSERVED,
        ))

    reasons.append("S5_DECLARATION_SYNTHETIC_READY")
    return ReadinessPacket(
        stage_id=STAGE_ID, status=ReadinessStatus.READY_SYNTHETIC,
        evidence_state=NOT_OBSERVED, reasons=tuple(reasons),
        findings=tuple(findings),
        summary={
            "source_id": source_id, "source_revision": revision,
            "declared_sha256": digest, "declared_size": size,
            "relative_path": relative_path, "admitted": False,
            "bytes_verified": False, "admitted_byte_count": 0,
            "snapshot_verified": False,
            "snapshot_record_declared_consistent": snapshot_declared_consistent,
            "temporal_binding_version": temporal_version,
            "max_bytes": max_bytes,
            "pr258_status": "EXTERNAL_PR_NOT_MERGED_IN_SNAPSHOT",
        },
    )
