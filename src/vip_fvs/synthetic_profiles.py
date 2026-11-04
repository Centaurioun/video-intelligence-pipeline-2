"""Three-model synthetic runtime factory over validated closed model profiles.

Authority: VIP-LAB-MEGA-02 Workstream W2.

This module is strictly synthetic and model-free. It binds validated
:class:`persistent_local_index.model_profile.ModelProfile` descriptors to
explicitly fake :class:`vip_fvs.local_semantic.CheckedLocalSemanticRuntime`
instances without loading weights, processors, tokenizers, devices, or media.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from persistent_local_index.embedding import build_fake_profile_runtime
from persistent_local_index.model_profile import (
    ModelProfile,
    profile_row_width_bytes,
    profile_semantic_space,
    validate_model_profile,
)
from persistent_local_index.model_space import (
    TEXT_PREPROCESSING_CONTRACT,
    SemanticSpace,
    semantic_space_id,
)
from . import local_semantic, retrieval_adapter

V1_PROFILE_ID = "vip-v1-siglip-base-224"
V2_BASE_PROFILE_ID = "vip-v2-siglip2-base-224"
V2_SO400M_PROFILE_ID = "vip-v2-siglip2-so400m-384"

CLOSED_SYNTHETIC_PROFILE_IDS: tuple[str, str, str] = (
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
)

MAX_PROFILE_JSON_BYTES = 256 * 1024

_MODEL_PROFILE_FIELDS = frozenset({
    "profile_id",
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
})
_INT_PROFILE_FIELDS = (
    "image_size",
    "patch_size",
    "embedding_dim",
    "precision_policy_version",
)


def compute_processor_digest(assets: Sequence[tuple[str, str]]) -> str:
    """Compute the canonical processor asset mapping SHA-256 digest."""
    payload = json.dumps(
        {
            "identity_mapping": "vip-processor-assets-v1",
            "assets": [
                {"name": name, "sha256": digest}
                for name, digest in sorted(assets, key=lambda item: item[0])
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_synthetic_profile_payload(
    profile_id: str, **overrides: Any
) -> dict[str, Any]:
    """Construct a deterministic, unmistakably synthetic profile JSON payload."""
    if profile_id == V1_PROFILE_ID:
        assets = (("tokenizer.json", "1" * 64),)
        base: dict[str, Any] = {
            "profile_id": V1_PROFILE_ID,
            "model_id": "google/siglip-base-patch16-224",
            "family": "siglip",
            "frozen_revision": "a" * 40,
            "weights_sha256": "2" * 64,
            "processor_asset_digests": [list(item) for item in assets],
            "processor_digest": compute_processor_digest(assets),
            "image_preprocessing_digest": "3" * 64,
            "text_preprocessing_contract": TEXT_PREPROCESSING_CONTRACT,
            "image_size": 224,
            "patch_size": 16,
            "embedding_dim": 768,
            "output_dtype": "float32",
            "normalization": "l2",
            "loader_kind": "siglip-v1",
            "device_backend": "cpu",
            "precision_policy_id": "v1-float32",
            "precision_policy_version": 1,
        }
    elif profile_id == V2_BASE_PROFILE_ID:
        assets = (("tokenizer.json", "4" * 64),)
        base = {
            "profile_id": V2_BASE_PROFILE_ID,
            "model_id": "google/siglip2-base-patch16-224",
            "family": "siglip2",
            "frozen_revision": "b" * 40,
            "weights_sha256": "5" * 64,
            "processor_asset_digests": [list(item) for item in assets],
            "processor_digest": compute_processor_digest(assets),
            "image_preprocessing_digest": "6" * 64,
            "text_preprocessing_contract": f"{V2_BASE_PROFILE_ID}:text-synthetic:v1",
            "image_size": 224,
            "patch_size": 16,
            "embedding_dim": 768,
            "output_dtype": "float32",
            "normalization": "l2",
            "loader_kind": "siglip2-auto",
            "device_backend": "pytorch-cpu",
            "precision_policy_id": "siglip2-fp16-compute-fp32-output",
            "precision_policy_version": 1,
        }
    elif profile_id == V2_SO400M_PROFILE_ID:
        assets = (("tokenizer.json", "7" * 64),)
        base = {
            "profile_id": V2_SO400M_PROFILE_ID,
            "model_id": "google/siglip2-so400m-patch14-384",
            "family": "siglip2",
            "frozen_revision": "c" * 40,
            "weights_sha256": "8" * 64,
            "processor_asset_digests": [list(item) for item in assets],
            "processor_digest": compute_processor_digest(assets),
            "image_preprocessing_digest": "9" * 64,
            "text_preprocessing_contract": f"{V2_SO400M_PROFILE_ID}:text-synthetic:v1",
            "image_size": 384,
            "patch_size": 14,
            "embedding_dim": 1152,
            "output_dtype": "float32",
            "normalization": "l2",
            "loader_kind": "siglip2-auto",
            "device_backend": "pytorch-cpu",
            "precision_policy_id": "siglip2-fp16-compute-fp32-output",
            "precision_policy_version": 1,
        }
    else:
        raise ValueError(f"MODEL_PROFILE_UNSUPPORTED:{profile_id!r}")

    if "processor_asset_digests" in overrides and "processor_digest" not in overrides:
        raw_assets = overrides["processor_asset_digests"]
        if isinstance(raw_assets, Sequence) and not isinstance(raw_assets, (str, bytes)):
            try:
                tuple_assets = tuple((str(k), str(v)) for k, v in raw_assets)
                overrides["processor_digest"] = compute_processor_digest(tuple_assets)
            except (TypeError, ValueError):
                pass
    base.update(overrides)
    return base


def make_synthetic_profile(profile_id: str, **overrides: Any) -> ModelProfile:
    """Construct and validate a synthetic :class:`ModelProfile`."""
    payload = make_synthetic_profile_payload(profile_id, **overrides)
    return parse_model_profile_mapping(payload)


@dataclass(frozen=True)
class SyntheticProfileBundle:
    """Validated closed profile bound to its explicitly fake checked runtime."""

    profile: ModelProfile
    runtime: local_semantic.CheckedLocalSemanticRuntime
    semantic_space: SemanticSpace
    space_id: str
    row_width_bytes: int
    synthetic_only: bool = True
    authentic_model_evidence: bool = False

    def __post_init__(self) -> None:
        validate_model_profile(self.profile)
        if not isinstance(self.runtime, local_semantic.CheckedLocalSemanticRuntime):
            raise ValueError("SYNTHETIC_PROFILE_CHECKED_RUNTIME_REQUIRED")
        if self.runtime.fake is not True:
            raise ValueError("SYNTHETIC_PROFILE_FAKE_RUNTIME_REQUIRED")
        expected_space = profile_semantic_space(self.profile)
        if self.semantic_space != expected_space or self.runtime.semantic_space != expected_space:
            raise ValueError("SYNTHETIC_PROFILE_SPACE_MISMATCH")
        expected_space_id = semantic_space_id(expected_space)
        if self.space_id != expected_space_id:
            raise ValueError("SYNTHETIC_PROFILE_SPACE_ID_MISMATCH")
        expected_row_width = profile_row_width_bytes(self.profile)
        if type(self.row_width_bytes) is not int or self.row_width_bytes != expected_row_width:
            raise ValueError("SYNTHETIC_PROFILE_ROW_WIDTH_MISMATCH")
        if self.synthetic_only is not True or self.authentic_model_evidence is not False:
            raise ValueError("SYNTHETIC_PROFILE_CLAIM_BOUNDARY_VIOLATION")


def build_synthetic_profile_runtime(profile: ModelProfile) -> SyntheticProfileBundle:
    """Build a model-free checked runtime bundle for any of the 3 closed profiles."""
    validate_model_profile(profile)
    space = profile_semantic_space(profile)
    row_width = profile_row_width_bytes(profile)

    if profile.family == "siglip2":
        runtime = build_fake_profile_runtime(profile)
    elif profile.profile_id == V1_PROFILE_ID and profile.family == "siglip":
        runtime = local_semantic.checked_runtime(
            image_embedder=retrieval_adapter.fake_image_embedder,
            text_embedder=retrieval_adapter.fake_text_embedder,
            semantic_space=space,
            fake=True,
            runtime_identity=f"vip-profile-fake/v1:{profile.profile_id}",
        )
    else:  # pragma: no cover - validate_model_profile already closes family/profile_id
        raise ValueError("MODEL_PROFILE_UNSUPPORTED")

    if not runtime.fake:
        raise ValueError("SYNTHETIC_PROFILE_FAKE_RUNTIME_REQUIRED")
    return SyntheticProfileBundle(
        profile=profile,
        runtime=runtime,
        semantic_space=space,
        space_id=semantic_space_id(space),
        row_width_bytes=row_width,
        synthetic_only=True,
        authentic_model_evidence=False,
    )


def parse_model_profile_mapping(payload: Mapping[str, Any]) -> ModelProfile:
    """Validate an in-memory profile mapping and return a :class:`ModelProfile`."""
    if not isinstance(payload, Mapping):
        raise ValueError("MODEL_PROFILE_JSON_NOT_OBJECT")
    if set(payload.keys()) != _MODEL_PROFILE_FIELDS:
        raise ValueError("MODEL_PROFILE_JSON_INVALID")

    for int_field in _INT_PROFILE_FIELDS:
        if type(payload[int_field]) is bool or not isinstance(payload[int_field], int):
            raise ValueError(f"MODEL_PROFILE_JSON_INVALID:{int_field}")

    raw_assets = payload.get("processor_asset_digests")
    if not isinstance(raw_assets, (list, tuple)) or not raw_assets:
        raise ValueError("MODEL_PROFILE_ASSETS_INVALID")
    converted_assets: list[tuple[str, str]] = []
    for item in raw_assets:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError("MODEL_PROFILE_ASSETS_INVALID")
        name, digest = item
        if type(name) is not str or type(digest) is not str:
            raise ValueError("MODEL_PROFILE_ASSETS_INVALID")
        converted_assets.append((name, digest))

    try:
        profile = ModelProfile(
            **{
                **payload,
                "processor_asset_digests": tuple(converted_assets),
            }
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("MODEL_PROFILE_JSON_INVALID") from exc

    validate_model_profile(profile)
    return profile


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"MODEL_PROFILE_JSON_DUPLICATE_KEY:{key}")
        result[key] = value
    return result


def _reject_non_finite_json_constant(token: str) -> Any:
    raise ValueError(f"MODEL_PROFILE_JSON_NON_FINITE:{token}")


def load_model_profile_json(profile_path: str | Path) -> ModelProfile:
    """Load and validate a closed synthetic :class:`ModelProfile` from JSON."""
    if not isinstance(profile_path, (str, Path)):
        raise TypeError("MODEL_PROFILE_PATH_INVALID")
    target = Path(profile_path)
    try:
        with target.open("rb") as handle:
            raw = handle.read(MAX_PROFILE_JSON_BYTES + 1)
    except OSError as exc:
        raise ValueError("MODEL_PROFILE_JSON_UNREADABLE") from exc
    if not raw or len(raw) > MAX_PROFILE_JSON_BYTES or b"\x00" in raw:
        raise ValueError("MODEL_PROFILE_JSON_UNREADABLE")
    try:
        text = raw.decode("utf-8")
        parsed = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_non_finite_json_constant,
        )
    except ValueError as exc:
        msg = str(exc)
        if msg.startswith("MODEL_PROFILE_"):
            raise
        raise ValueError("MODEL_PROFILE_JSON_UNREADABLE") from exc
    if type(parsed) is not dict:
        raise ValueError("MODEL_PROFILE_JSON_NOT_OBJECT")
    return parse_model_profile_mapping(parsed)


def load_synthetic_profile_bundle(profile_path: str | Path) -> SyntheticProfileBundle:
    """Load a closed profile JSON file and construct its checked fake runtime bundle."""
    profile = load_model_profile_json(profile_path)
    return build_synthetic_profile_runtime(profile)


__all__ = [
    "CLOSED_SYNTHETIC_PROFILE_IDS",
    "MAX_PROFILE_JSON_BYTES",
    "SyntheticProfileBundle",
    "V1_PROFILE_ID",
    "V2_BASE_PROFILE_ID",
    "V2_SO400M_PROFILE_ID",
    "build_synthetic_profile_runtime",
    "compute_processor_digest",
    "load_model_profile_json",
    "load_synthetic_profile_bundle",
    "make_synthetic_profile",
    "make_synthetic_profile_payload",
    "parse_model_profile_mapping",
]
