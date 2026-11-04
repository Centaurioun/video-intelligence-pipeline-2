"""Packet P03a: Bounded synthetic S5 source-declaration and snapshot preflight.

Validates synthetic source declarations (source_id, source_revision,
declared_sha256, declared_size, relative_path) and optional bounded no-follow
byte admission inside a synthetic snapshot root without mutating vip_fvs.
Also delegates snapshot evidence verification to
``vip_fvs.source_snapshot.verify_snapshot_evidence`` when present.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any, Mapping

from vip_fvs.source_snapshot import (
    SourceSnapshotError,
    verify_snapshot_evidence,
)

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


def _admit_bounded_bytes_nofollow(
    root_dir: Path,
    relative_path: str,
    *,
    declared_size: int,
    declared_sha256: str,
    max_bytes: int,
) -> bytes:
    """Descriptor-relative / no-follow bounded read of synthetic candidate bytes."""
    if not root_dir.exists() or not root_dir.is_dir():
        raise VipLabError(
            "S5_SNAPSHOT_ROOT_INVALID",
            f"snapshot_root is not an existing directory: {root_dir}",
            field_path="snapshot_root",
        )
    if root_dir.is_symlink():
        raise VipLabError(
            "S5_SYMLINK_OR_NONREGULAR_REFUSED",
            f"snapshot_root must not be a symlink: {root_dir}",
            field_path="snapshot_root",
        )

    parts = PurePosixPath(relative_path).parts
    dir_flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        dir_flags |= os.O_NOFOLLOW
    if hasattr(os, "O_DIRECTORY"):
        dir_flags |= os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        dir_flags |= os.O_CLOEXEC

    file_flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        file_flags |= os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        file_flags |= os.O_CLOEXEC

    try:
        current_fd = os.open(str(root_dir), dir_flags)
    except OSError as exc:
        raise VipLabError(
            "S5_SNAPSHOT_ROOT_OPEN_REFUSED",
            f"Could not open snapshot_root {root_dir}: {exc}",
            field_path="snapshot_root",
        ) from exc

    try:
        for segment in parts[:-1]:
            try:
                next_fd = os.open(segment, dir_flags, dir_fd=current_fd)
            except OSError as exc:
                raise VipLabError(
                    "S5_SYMLINK_OR_NONREGULAR_REFUSED",
                    f"Refused intermediate path segment {segment!r}: {exc}",
                    field_path="relative_path",
                ) from exc
            os.close(current_fd)
            current_fd = next_fd

        leaf = parts[-1]
        try:
            file_fd = os.open(leaf, file_flags, dir_fd=current_fd)
        except FileNotFoundError as exc:
            raise VipLabError(
                "S5_SOURCE_FILE_MISSING",
                f"Declared synthetic source file does not exist: {relative_path}",
                field_path="relative_path",
            ) from exc
        except OSError as exc:
            raise VipLabError(
                "S5_SYMLINK_OR_NONREGULAR_REFUSED",
                f"Refused to open {relative_path!r} with O_NOFOLLOW: {exc}",
                field_path="relative_path",
            ) from exc

        try:
            st = os.fstat(file_fd)
            if not stat.S_ISREG(st.st_mode):
                raise VipLabError(
                    "S5_SYMLINK_OR_NONREGULAR_REFUSED",
                    f"Target {relative_path!r} is not a regular file",
                    field_path="relative_path",
                )
            if st.st_size > max_bytes:
                raise VipLabError(
                    "S5_MAX_BYTES_EXCEEDED",
                    f"File size {st.st_size} exceeds max_bytes {max_bytes}",
                    field_path="declared_size",
                    details={"observed_size": st.st_size, "max_bytes": max_bytes},
                )
            chunks: list[bytes] = []
            total = 0
            read_cap = min(max_bytes, declared_size) + 1
            while True:
                chunk = os.read(file_fd, min(65536, read_cap - total))
                if not chunk:
                    break
                total += len(chunk)
                chunks.append(chunk)
                if total >= read_cap:
                    break
            admitted = b"".join(chunks)
        finally:
            os.close(file_fd)
    finally:
        os.close(current_fd)

    if len(admitted) > max_bytes:
        raise VipLabError(
            "S5_MAX_BYTES_EXCEEDED",
            f"Read bytes ({len(admitted)}) exceeded max_bytes ({max_bytes})",
            field_path="declared_size",
        )
    if len(admitted) != declared_size:
        raise VipLabError(
            "S5_SIZE_MISMATCH",
            f"Observed byte length {len(admitted)} != declared_size {declared_size}",
            field_path="declared_size",
            details={"observed_size": len(admitted), "declared_size": declared_size},
        )
    actual_sha256 = hashlib.sha256(admitted).hexdigest()
    if actual_sha256 != declared_sha256:
        raise VipLabError(
            "S5_DIGEST_MISMATCH",
            f"Observed SHA-256 {actual_sha256} != declared_sha256 {declared_sha256}",
            field_path="declared_sha256",
            details={
                "observed_sha256": actual_sha256,
                "declared_sha256": declared_sha256,
            },
        )
    return admitted


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
    snapshot_root: str | Path | None = None,
    max_bytes: int = DEFAULT_S5_MAX_BYTES,
) -> ReadinessPacket:
    """Inspect a synthetic S5 source admission declaration and optional file/snapshot."""
    if not isinstance(declaration, Mapping):
        raise VipLabError(
            "S5_DECLARATION_NOT_MAPPING",
            "declaration must be a mapping",
        )
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
        raise VipLabError(
            "S5_INVALID_MAX_BYTES",
            "max_bytes must be a positive integer",
            field_path="max_bytes",
        )

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(declaration)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = ["PR_258_DIRECT_CODE_ABSENT_IN_SNAPSHOT"]
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="S5_UNTRUSTED_AUTHORITY_CLAIMS_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Self-declared authority flags in S5 declaration were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    source_id = cleaned.get("source_id")
    source_revision = cleaned.get("source_revision")
    declared_sha256 = cleaned.get("declared_sha256")
    declared_size = cleaned.get("declared_size")
    relative_path = cleaned.get("relative_path")

    try:
        if not isinstance(source_id, str) or not source_id.strip():
            raise VipLabError(
                "S5_SOURCE_ID_INVALID",
                "source_id must be a non-empty string",
                field_path="source_id",
            )
        if not isinstance(source_revision, str) or not source_revision.strip():
            raise VipLabError(
                "S5_SOURCE_REVISION_INVALID",
                "source_revision must be a non-empty string",
                field_path="source_revision",
            )
        validate_hex_digest(
            declared_sha256,
            length=64,
            field_name="declared_sha256",
            error_code="S5_DECLARED_DIGEST_INVALID",
        )
        if (
            not isinstance(declared_size, int)
            or isinstance(declared_size, bool)
            or declared_size <= 0
        ):
            raise VipLabError(
                "S5_DECLARED_SIZE_INVALID",
                "declared_size must be a positive integer",
                field_path="declared_size",
            )
        if declared_size > max_bytes:
            raise VipLabError(
                "S5_MAX_BYTES_EXCEEDED",
                f"declared_size {declared_size} exceeds max_bytes {max_bytes}",
                field_path="declared_size",
                details={"declared_size": declared_size, "max_bytes": max_bytes},
            )
        normalized_rel_path = _validate_relative_source_path(relative_path)
    except VipLabError as exc:
        findings.append(
            ReadinessFinding(
                code=exc.code,
                status=ReadinessStatus.INVALID,
                message=exc.message,
                field_path=exc.field_path,
                details=exc.details,
            )
        )
        reasons.append(exc.code)
        blockers.append(exc.code)
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={
                "admitted": False,
                "bytes_verified": False,
                "max_bytes": max_bytes,
                "pr258_status": "EXTERNAL_PR_NOT_MERGED_IN_SNAPSHOT",
            },
        )

    bytes_verified = False
    admitted_byte_count = 0

    if snapshot_root is not None:
        try:
            admitted_bytes = _admit_bounded_bytes_nofollow(
                Path(snapshot_root),
                normalized_rel_path,
                declared_size=declared_size,
                declared_sha256=declared_sha256,
                max_bytes=max_bytes,
            )
            bytes_verified = True
            admitted_byte_count = len(admitted_bytes)
            findings.append(
                ReadinessFinding(
                    code="S5_BOUNDED_BYTES_ADMITTED",
                    status=ReadinessStatus.READY_SYNTHETIC,
                    message="Bounded no-follow byte read verified size and SHA-256",
                    evidence_state="MEASURED",
                    details={
                        "admitted_bytes": admitted_byte_count,
                        "sha256": declared_sha256,
                    },
                )
            )
        except VipLabError as exc:
            findings.append(
                ReadinessFinding(
                    code=exc.code,
                    status=ReadinessStatus.BLOCKED,
                    message=exc.message,
                    field_path=exc.field_path,
                    details=exc.details,
                )
            )
            reasons.append(exc.code)
            blockers.append(exc.code)
            return ReadinessPacket(
                stage_id=STAGE_ID,
                status=ReadinessStatus.BLOCKED,
                reasons=tuple(reasons),
                blockers=tuple(blockers),
                findings=tuple(findings),
                summary={
                    "source_id": source_id,
                    "source_revision": source_revision,
                    "relative_path": normalized_rel_path,
                    "admitted": False,
                    "bytes_verified": False,
                    "max_bytes": max_bytes,
                    "pr258_status": "EXTERNAL_PR_NOT_MERGED_IN_SNAPSHOT",
                },
            )

    snapshot_verified = False
    if "snapshot" in cleaned and cleaned["snapshot"] is not None:
        snap_payload = cleaned["snapshot"]
        try:
            if not isinstance(snap_payload, Mapping):
                raise SourceSnapshotError("SNAPSHOT_EVIDENCE_INVALID")
            verify_snapshot_evidence(dict(snap_payload))
            if (
                snap_payload.get("source_revision_id") != source_revision
                or snap_payload.get("snapshot_sha256") != declared_sha256
                or snap_payload.get("source_byte_count") != declared_size
            ):
                raise VipLabError(
                    "S5_SNAPSHOT_DECLARATION_MISMATCH",
                    "Embedded snapshot evidence does not match S5 declaration fields",
                    field_path="snapshot",
                )
            snapshot_verified = True
            findings.append(
                ReadinessFinding(
                    code="S5_SNAPSHOT_RECORD_VERIFIED",
                    status=ReadinessStatus.READY_SYNTHETIC,
                    message="Snapshot evidence passed verify_snapshot_evidence and field checks",
                    evidence_state="MEASURED",
                    details={
                        "snapshot_id": snap_payload.get("snapshot_id"),
                        "snapshot_manifest_sha256": snap_payload.get(
                            "snapshot_manifest_sha256"
                        ),
                    },
                )
            )
        except (SourceSnapshotError, VipLabError) as exc:
            err_code = (
                exc.code if isinstance(exc, VipLabError) else "S5_SNAPSHOT_RECORD_INVALID"
            )
            findings.append(
                ReadinessFinding(
                    code=err_code,
                    status=ReadinessStatus.INVALID,
                    message=str(exc),
                    field_path="snapshot",
                )
            )
            reasons.append(err_code)
            blockers.append(err_code)
            return ReadinessPacket(
                stage_id=STAGE_ID,
                status=ReadinessStatus.INVALID,
                reasons=tuple(reasons),
                blockers=tuple(blockers),
                findings=tuple(findings),
                summary={
                    "source_id": source_id,
                    "source_revision": source_revision,
                    "admitted": False,
                    "bytes_verified": bytes_verified,
                    "snapshot_verified": False,
                },
            )

    temporal_binding_version: int | None = None
    if "temporal_binding" in cleaned and cleaned["temporal_binding"] is not None:
        tb_payload = cleaned["temporal_binding"]
        try:
            if not isinstance(tb_payload, Mapping):
                raise VipLabError(
                    "S5_TEMPORAL_BINDING_INVALID",
                    "temporal_binding must be a mapping",
                    field_path="temporal_binding",
                )
            ver, ev_sha = _verify_temporal_binding_dict(
                tb_payload,
                expected_revision=source_revision,
                expected_sha256=declared_sha256,
                expected_size=declared_size,
            )
            temporal_binding_version = ver
            findings.append(
                ReadinessFinding(
                    code="S5_TEMPORAL_BINDING_VERIFIED",
                    status=ReadinessStatus.READY_SYNTHETIC,
                    message=f"Verified temporal_binding v{ver} digest and identity consistency",
                    evidence_state="MEASURED",
                    details={"evidence_sha256": ev_sha, "schema_version": ver},
                )
            )
        except VipLabError as exc:
            findings.append(
                ReadinessFinding(
                    code=exc.code,
                    status=ReadinessStatus.INVALID,
                    message=exc.message,
                    field_path=exc.field_path,
                )
            )
            reasons.append(exc.code)
            blockers.append(exc.code)
            return ReadinessPacket(
                stage_id=STAGE_ID,
                status=ReadinessStatus.INVALID,
                reasons=tuple(reasons),
                blockers=tuple(blockers),
                findings=tuple(findings),
                summary={
                    "source_id": source_id,
                    "source_revision": source_revision,
                    "admitted": False,
                    "bytes_verified": bytes_verified,
                    "snapshot_verified": snapshot_verified,
                },
            )

    reasons.append("S5_DECLARATION_SYNTHETIC_READY")
    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=ReadinessStatus.READY_SYNTHETIC,
        evidence_state="MEASURED" if bytes_verified else NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=(),
        findings=tuple(findings),
        summary={
            "source_id": source_id,
            "source_revision": source_revision,
            "declared_sha256": declared_sha256,
            "declared_size": declared_size,
            "relative_path": normalized_rel_path,
            "admitted": True,
            "bytes_verified": bytes_verified,
            "admitted_byte_count": admitted_byte_count,
            "snapshot_verified": snapshot_verified,
            "temporal_binding_version": temporal_binding_version,
            "max_bytes": max_bytes,
            "pr258_status": "EXTERNAL_PR_NOT_MERGED_IN_SNAPSHOT",
        },
    )
