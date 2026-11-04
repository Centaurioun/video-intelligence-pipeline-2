"""Packet P05a: Gate-1 Model Asset & Profile Semantic-Space Preflight.

Reuses ``vip_fvs.synthetic_profiles`` and ``persistent_local_index.model_profile``
to validate synthetic model asset declarations across the three Gate-1 profiles:
- ``vip-v1-siglip-base-224`` (768D, ``cpu``, ``v1-float32``)
- ``vip-v2-siglip2-base-224`` (768D, distinct semantic space)
- ``vip-v2-siglip2-so400m-384`` (1152D, row width 4608 bytes)

Refuses:
- Cross-profile semantic space collisions (especially V1 768D vs V2 Base 768D)
- Network/remote download requests (``allow_download=True`` or ``remote_url``)
- Claims that synthetic embeddings prove authentic model weight execution
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from persistent_local_index.model_profile import (
    ModelProfile,
    profile_row_width_bytes,
    profile_semantic_space,
    validate_model_profile,
)
from vip_fvs.synthetic_profiles import (
    CLOSED_SYNTHETIC_PROFILE_IDS,
    build_synthetic_profile_runtime,
    make_synthetic_profile,
)

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)


STAGE_ID = "MEGA-05.MODEL_ASSETS_PREFLIGHT"
SYNTHETIC_PROFILE_IDS = CLOSED_SYNTHETIC_PROFILE_IDS

_ALLOWED_PROFILE_OVERRIDE_KEYS = (
    "model_id",
    "family",
    "frozen_revision",
    "weights_sha256",
    "processor_asset_digests",
    "processor_digest",
    "image_preprocessing_digest",
    "text_preprocessing_contract",
    "image_size",
    "patch_size",
    "embedding_dim",
    "output_dtype",
    "normalization",
    "loader_kind",
    "device_backend",
    "precision_policy_id",
    "precision_policy_version",
)


def _inspect_single_asset_claim(
    claim: Mapping[str, Any],
    idx: int,
) -> tuple[dict[str, Any] | None, list[ReadinessFinding], list[str]]:
    findings: list[ReadinessFinding] = []
    blockers: list[str] = []
    path_prefix = f"profiles[{idx}]"

    profile_id = claim.get("profile_id")
    if not isinstance(profile_id, str) or profile_id not in CLOSED_SYNTHETIC_PROFILE_IDS:
        code = "MODEL_PROFILE_ID_UNKNOWN"
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message=f"Unsupported or missing profile_id {profile_id!r}",
                field_path=f"{path_prefix}.profile_id",
            )
        )
        return None, findings, blockers

    if bool(claim.get("allow_download", False)) or claim.get("remote_url") is not None:
        code = "MODEL_DOWNLOAD_FORBIDDEN"
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message=f"Network model download or remote_url is forbidden for {profile_id}",
                field_path=f"{path_prefix}.allow_download",
            )
        )

    if bool(claim.get("claim_authentic_execution", False)) or bool(
        claim.get("authentic_weights_loaded", False)
    ):
        code = "SYNTHETIC_EMBEDDING_NOT_AUTHENTIC_MODEL"
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message=(
                    f"Synthetic profile {profile_id} (including 1152D SO400M) never proves "
                    "authentic model weight execution"
                ),
                field_path=f"{path_prefix}.claim_authentic_execution",
            )
        )

    for digest_field in (
        "weights_sha256",
        "processor_digest",
        "image_preprocessing_digest",
        "tokenizer_sha256",
        "preprocess_sha256",
    ):
        if digest_field in claim:
            try:
                validate_hex_digest(
                    claim.get(digest_field),
                    length=64,
                    field_name=f"{path_prefix}.{digest_field}",
                    error_code="MODEL_ASSET_DIGEST_INVALID",
                )
            except VipLabError as exc:
                blockers.append(exc.code)
                findings.append(
                    ReadinessFinding(
                        code=exc.code,
                        status=ReadinessStatus.INVALID,
                        message=exc.message,
                        field_path=exc.field_path,
                    )
                )

    if "frozen_revision" in claim:
        try:
            validate_hex_digest(
                claim.get("frozen_revision"),
                length=40,
                field_name=f"{path_prefix}.frozen_revision",
                error_code="MODEL_ASSET_DIGEST_INVALID",
            )
        except VipLabError as exc:
            blockers.append(exc.code)
            findings.append(
                ReadinessFinding(
                    code=exc.code,
                    status=ReadinessStatus.INVALID,
                    message=exc.message,
                    field_path=exc.field_path,
                )
            )

    canonical_prof = make_synthetic_profile(profile_id)
    override_kwargs: dict[str, Any] = {}
    for key in _ALLOWED_PROFILE_OVERRIDE_KEYS:
        if key in claim:
            override_kwargs[key] = claim[key]

    # Map legacy alias fields if caller supplied them without canonical names
    if "processor_digest" not in override_kwargs and "tokenizer_sha256" in claim:
        override_kwargs["processor_digest"] = claim["tokenizer_sha256"]
    if "image_preprocessing_digest" not in override_kwargs and "preprocess_sha256" in claim:
        override_kwargs["image_preprocessing_digest"] = claim["preprocess_sha256"]

    candidate_prof = ModelProfile(
        profile_id=canonical_prof.profile_id,
        model_id=str(override_kwargs.get("model_id", canonical_prof.model_id)),
        family=str(override_kwargs.get("family", canonical_prof.family)),
        frozen_revision=str(
            override_kwargs.get("frozen_revision", canonical_prof.frozen_revision)
        ),
        weights_sha256=str(
            override_kwargs.get("weights_sha256", canonical_prof.weights_sha256)
        ),
        processor_asset_digests=tuple(
            override_kwargs.get(
                "processor_asset_digests", canonical_prof.processor_asset_digests
            )
        ),
        processor_digest=str(
            override_kwargs.get("processor_digest", canonical_prof.processor_digest)
        ),
        image_preprocessing_digest=str(
            override_kwargs.get(
                "image_preprocessing_digest", canonical_prof.image_preprocessing_digest
            )
        ),
        text_preprocessing_contract=str(
            override_kwargs.get(
                "text_preprocessing_contract",
                canonical_prof.text_preprocessing_contract,
            )
        ),
        image_size=int(override_kwargs.get("image_size", canonical_prof.image_size)),
        patch_size=int(override_kwargs.get("patch_size", canonical_prof.patch_size)),
        embedding_dim=int(
            override_kwargs.get("embedding_dim", canonical_prof.embedding_dim)
        ),
        output_dtype=str(
            override_kwargs.get("output_dtype", canonical_prof.output_dtype)
        ),
        normalization=str(
            override_kwargs.get("normalization", canonical_prof.normalization)
        ),
        loader_kind=str(override_kwargs.get("loader_kind", canonical_prof.loader_kind)),
        device_backend=str(
            override_kwargs.get("device_backend", canonical_prof.device_backend)
        ),
        precision_policy_id=str(
            override_kwargs.get(
                "precision_policy_id", canonical_prof.precision_policy_id
            )
        ),
        precision_policy_version=int(
            override_kwargs.get(
                "precision_policy_version", canonical_prof.precision_policy_version
            )
        ),
    )

    try:
        validate_model_profile(candidate_prof)
        bundle = build_synthetic_profile_runtime(candidate_prof)
    except ValueError as exc:
        code = "MODEL_PROFILE_CONTRACT_VIOLATION"
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=str(exc),
                field_path=path_prefix,
            )
        )
        return None, findings, blockers

    sem_space_dict = profile_semantic_space(candidate_prof)
    sem_space = str(claim.get("semantic_space_id") or sem_space_dict["space_id"])
    row_bytes = profile_row_width_bytes(candidate_prof)

    info = {
        "profile_id": candidate_prof.profile_id,
        "model_id": candidate_prof.model_id,
        "family": candidate_prof.family,
        "frozen_revision": candidate_prof.frozen_revision,
        "embedding_dim": candidate_prof.embedding_dim,
        "row_width_bytes": row_bytes,
        "device_backend": candidate_prof.device_backend,
        "precision_policy_id": candidate_prof.precision_policy_id,
        "precision_policy_version": candidate_prof.precision_policy_version,
        "semantic_space_id": sem_space,
        "synthetic_only": bundle.synthetic_only,
        "authentic_model_evidence": bundle.authentic_model_evidence,
        "authentic_weights_verified": False,
        "authentic_model_execution": False,
    }
    return info, findings, blockers


def inspect_model_asset_claims(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Validate synthetic Gate-1 model asset declarations and semantic-space isolation."""
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "MODEL_ASSETS_PAYLOAD_NOT_MAPPING",
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
                code="MODEL_ASSETS_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted self-declared authority flags in model asset payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    raw_profiles = cleaned.get("profiles")
    if not isinstance(raw_profiles, Sequence) or len(raw_profiles) == 0:
        code = "MODEL_ASSETS_PROFILES_MISSING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="profiles must be a non-empty sequence of profile claim mappings",
                field_path="profiles",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"validated_profiles": [], "authentic_model_execution": False},
        )

    validated_profiles: list[dict[str, Any]] = []
    seen_spaces: dict[str, str] = {}

    for idx, item in enumerate(raw_profiles):
        if not isinstance(item, Mapping):
            code = "MODEL_ASSET_CLAIM_NOT_MAPPING"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message=f"profiles[{idx}] must be a mapping",
                    field_path=f"profiles[{idx}]",
                )
            )
            continue
        info, item_findings, item_blockers = _inspect_single_asset_claim(item, idx)
        findings.extend(item_findings)
        for b in item_blockers:
            if b not in blockers:
                blockers.append(b)
            if b not in reasons:
                reasons.append(b)
        if info is not None:
            sem_space = info["semantic_space_id"]
            prof_id = info["profile_id"]
            if sem_space in seen_spaces and seen_spaces[sem_space] != prof_id:
                code = "MODEL_PROFILE_CROSS_SPACE_COLLISION"
                reasons.append(code)
                blockers.append(code)
                findings.append(
                    ReadinessFinding(
                        code=code,
                        status=ReadinessStatus.BLOCKED,
                        message=(
                            f"Profiles {seen_spaces[sem_space]!r} and {prof_id!r} cannot "
                            f"share semantic_space_id {sem_space!r}"
                        ),
                        field_path=f"profiles[{idx}].semantic_space_id",
                    )
                )
            else:
                seen_spaces[sem_space] = prof_id
            validated_profiles.append(info)

    if not blockers:
        reasons.append("MODEL_ASSET_SYNTHETIC_CLAIMS_VALID_NOT_AUTHENTIC")
        findings.append(
            ReadinessFinding(
                code="MODEL_ASSETS_SYNTHETIC_ISOLATION_VERIFIED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Validated synthetic profile shapes, row widths, and semantic-space isolation",
                details={"profile_count": len(validated_profiles)},
            )
        )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC

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
            "validated_profiles": validated_profiles,
            "semantic_spaces": dict(seen_spaces),
            "authentic_weights_verified": False,
            "authentic_model_execution": False,
            "network_download_permitted": False,
        },
    )
