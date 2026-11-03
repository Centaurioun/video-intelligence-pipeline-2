"""Closed, model-free identity contract for VIP's three representation profiles.

Profiles describe identity only. They do not load models, inspect local bundles,
authorize source access, or provide a remote acquisition path. The V2 text IDs
below are synthetic identity labels, not validated tokenizer specifications.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from . import model_space

_PROFILE_SPECS = {
    "vip-v1-siglip-base-224": (
        "google/siglip-base-patch16-224", "siglip", 224, 16, 768, "siglip-v1"
    ),
    "vip-v2-siglip2-base-224": (
        "google/siglip2-base-patch16-224", "siglip2", 224, 16, 768, "siglip2-auto"
    ),
    "vip-v2-siglip2-so400m-384": (
        "google/siglip2-so400m-patch14-384", "siglip2", 384, 14, 1152, "siglip2-auto"
    ),
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVISION = re.compile(r"^[0-9a-f]{40}$")
_IDENTITY_MAPPING_VERSION = "vip-model-profile-semantic-identity-v1"
_ASSET_MAPPING_VERSION = "vip-processor-assets-v1"
_SUPPORTED_DEVICE_BACKENDS = frozenset({"cpu", "pytorch-cpu", "pytorch-mps"})
_SUPPORTED_PRECISION_POLICY_VERSIONS = {
    "v1-float32": frozenset({1}),
    "siglip2-fp16-compute-fp32-output": frozenset({1}),
    "siglip2-fp32-compute-fp32-output": frozenset({1}),
    "siglip2-q4-mixed-272-328-group32-fp16-compute": frozenset({1}),
}
_TEXT_CONTRACT_IDENTITIES = {
    "vip-v1-siglip-base-224": "padding=max_length",
    "vip-v2-siglip2-base-224": "vip-v2-siglip2-base-224:text-synthetic:v1",
    "vip-v2-siglip2-so400m-384": "vip-v2-siglip2-so400m-384:text-synthetic:v1",
}


@dataclass(frozen=True)
class ModelProfile:
    """Immutable, closed profile describing one vector representation."""

    profile_id: str
    model_id: str
    family: str
    frozen_revision: str
    weights_sha256: str
    processor_asset_digests: tuple[tuple[str, str], ...]
    processor_digest: str
    image_preprocessing_digest: str
    text_preprocessing_contract: str
    image_size: int
    patch_size: int
    embedding_dim: int
    output_dtype: str
    normalization: str
    loader_kind: str
    device_backend: str
    precision_policy_id: str
    precision_policy_version: int


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def validate_model_profile(profile: ModelProfile) -> None:
    """Reject unknown, incomplete, mutable, or internally inconsistent profiles."""
    if not isinstance(profile, ModelProfile):
        raise ValueError("MODEL_PROFILE_TYPE_UNSUPPORTED")
    if not isinstance(profile.profile_id, str):
        raise ValueError("MODEL_PROFILE_UNSUPPORTED")
    expected = _PROFILE_SPECS.get(profile.profile_id)
    if expected is None:
        raise ValueError("MODEL_PROFILE_UNSUPPORTED")
    model_id, family, image_size, patch_size, embedding_dim, loader_kind = expected
    fixed = (
        ("model_id", profile.model_id, model_id),
        ("family", profile.family, family),
        ("image_size", profile.image_size, image_size),
        ("patch_size", profile.patch_size, patch_size),
        ("embedding_dim", profile.embedding_dim, embedding_dim),
        ("loader_kind", profile.loader_kind, loader_kind),
        ("output_dtype", profile.output_dtype, "float32"),
        ("normalization", profile.normalization, "l2"),
    )
    for field, actual, required in fixed:
        if actual != required:
            raise ValueError(f"MODEL_PROFILE_UNSUPPORTED:{field}")
    if not isinstance(profile.frozen_revision, str) or not _REVISION.fullmatch(profile.frozen_revision):
        raise ValueError("MODEL_PROFILE_REVISION_INVALID")
    for field, value in (
        ("weights_sha256", profile.weights_sha256),
        ("processor_digest", profile.processor_digest),
        ("image_preprocessing_digest", profile.image_preprocessing_digest),
    ):
        if not _is_digest(value):
            raise ValueError(f"MODEL_PROFILE_DIGEST_INVALID:{field}")
    if (
        type(profile.text_preprocessing_contract) is not str
        or profile.text_preprocessing_contract
        != _TEXT_CONTRACT_IDENTITIES[profile.profile_id]
    ):
        raise ValueError("MODEL_PROFILE_TEXT_CONTRACT_INVALID")
    if (
        not isinstance(profile.device_backend, str)
        or profile.device_backend not in _SUPPORTED_DEVICE_BACKENDS
    ):
        raise ValueError("MODEL_PROFILE_DEVICE_BACKEND_INVALID")
    if not isinstance(profile.precision_policy_id, str):
        raise ValueError("MODEL_PROFILE_PRECISION_POLICY_INVALID")
    supported_versions = _SUPPORTED_PRECISION_POLICY_VERSIONS.get(profile.precision_policy_id)
    if supported_versions is None:
        raise ValueError("MODEL_PROFILE_PRECISION_POLICY_INVALID")
    if (
        type(profile.precision_policy_version) is not int
        or profile.precision_policy_version not in supported_versions
    ):
        raise ValueError("MODEL_PROFILE_PRECISION_VERSION_INVALID")
    if profile.profile_id == "vip-v1-siglip-base-224" and (
        profile.device_backend != "cpu"
        or profile.precision_policy_id != "v1-float32"
        or profile.precision_policy_version != 1
    ):
        raise ValueError("MODEL_PROFILE_V1_REPRESENTATION_POLICY_UNSUPPORTED")
    assets = profile.processor_asset_digests
    if not isinstance(assets, tuple) or not assets:
        raise ValueError("MODEL_PROFILE_ASSETS_INVALID")
    names: set[str] = set()
    for item in assets:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("MODEL_PROFILE_ASSETS_INVALID")
        name, digest = item
        if (
            not isinstance(name, str)
            or not name
            or name in {".", ".."}
            or "/" in name
            or "\\" in name
            or name in names
            or not _is_digest(digest)
        ):
            raise ValueError("MODEL_PROFILE_ASSETS_INVALID")
        names.add(name)
    if profile.profile_id != "vip-v1-siglip-base-224":
        asset_identity = {
            "identity_mapping": _ASSET_MAPPING_VERSION,
            "assets": [{"name": name, "sha256": digest} for name, digest in sorted(assets)],
        }
        canonical = json.dumps(
            asset_identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        expected_processor_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if profile.processor_digest != expected_processor_digest:
            raise ValueError("MODEL_PROFILE_PROCESSOR_ASSET_DIGEST_MISMATCH")


def _effective_image_preprocessing_digest(profile: ModelProfile) -> str:
    """Bind V2's effective representation inputs using an explicit v1 mapping.

    V1 retains the historical raw preprocessing digest byte-for-byte. V2's
    effective image-to-vector transform also depends on the selected device
    backend and versioned precision policy, so those fields enter this mapping.
    """
    if profile.profile_id == "vip-v1-siglip-base-224":
        return profile.image_preprocessing_digest
    identity = {
        "identity_mapping": _IDENTITY_MAPPING_VERSION,
        "profile_id": profile.profile_id,
        "image_preprocessing_digest": profile.image_preprocessing_digest,
        "device_backend": profile.device_backend,
        "precision_policy_id": profile.precision_policy_id,
        "precision_policy_version": profile.precision_policy_version,
    }
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def profile_semantic_space(profile: ModelProfile) -> model_space.SemanticSpace:
    """Map a validated profile to the existing persisted SemanticSpace shape."""
    validate_model_profile(profile)
    return model_space.SemanticSpace(
        model_identity=profile.model_id,
        frozen_revision=profile.frozen_revision,
        weights_sha256=profile.weights_sha256,
        processor_digest=profile.processor_digest,
        image_preprocessing_digest=_effective_image_preprocessing_digest(profile),
        text_preprocessing_contract=profile.text_preprocessing_contract,
        embedding_dim=profile.embedding_dim,
        dtype=profile.output_dtype,
        normalization=profile.normalization,
    )


def profile_row_width_bytes(profile: ModelProfile) -> int:
    """Return the validated float32 row size for this profile."""
    validate_model_profile(profile)
    return profile.embedding_dim * 4
