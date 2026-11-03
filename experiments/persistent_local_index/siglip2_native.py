"""Model-free boundaries for the synthetic SigLIP2 adapter and native session.

This module deliberately has no default factory, runtime loader, or authentic
processor/tokenizer/model implementation.  Callers must inject an implementation,
which keeps this source-only slice independent of model, processor, device,
asset, cache, and network access.

Two boundaries exist:

* :class:`Siglip2Adapter` / :func:`create_adapter` — the pre-existing injected
  embedding-method double used by synthetic slice tests.
* :class:`Siglip2Session` / :func:`open_siglip2_session` — the plan-named native
  runtime surface (``encode_image_paths`` / ``encode_texts``).  Only the guarded
  SOURCE boundary is implemented here; the genuine authentic runtime remains
  PENDING separate owner authorization and native acceptance.  An injected
  double may never claim ``authentic=True``.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol, Sequence, runtime_checkable

import numpy as np

from .model_profile import ModelProfile, validate_model_profile

_PROFILE_DEVICE = {
    "cpu": "cpu",
    "pytorch-cpu": "cpu",
    "pytorch-mps": "mps",
}

_SESSION_METHODS = ("encode_image_paths", "encode_texts")

# Requirements that only a separately authorized, native-accepted implementation
# can satisfy.  Recorded as data so later native work has a stable checklist; NO
# value here is observed, measured, or claimed as implemented.
AUTHENTIC_SESSION_REQUIREMENTS = (
    "processor_and_tokenizer_assets_digest_verified_before_open",
    "text_special_token_ids_resolved_49406_49407_discrepancy",
    "image_preprocessing_bound_to_profile_image_size_and_patch_size",
    "pooled_embedding_extraction_contract_pinned",
    "profile_precision_policy_applied",
    "device_backend_matches_profile_without_silent_cpu_fallback",
    "local_files_only_true_trust_remote_code_false_use_safetensors_true",
    "session_identity_bound_to_asset_digests_before_and_after_open",
)


@dataclass(frozen=True)
class Siglip2Adapter:
    """Validated profile paired with an explicitly injected adapter double."""

    profile: ModelProfile
    implementation: Any

    def embed_images(self, images: Sequence[Any]) -> np.ndarray:
        return _validate_rows(
            self.implementation.embed_images(images), len(images), self.profile.embedding_dim
        )

    def embed_texts(self, texts: Sequence[str]) -> np.ndarray:
        return _validate_rows(
            self.implementation.embed_texts(texts), len(texts), self.profile.embedding_dim
        )


def _validate_rows(value: Any, expected_rows: int, dimension: int) -> np.ndarray:
    rows = np.asarray(value)
    if rows.ndim != 2 or rows.shape != (expected_rows, dimension):
        raise ValueError(
            f"ADAPTER_OUTPUT_SHAPE_INVALID:{rows.shape}!={(expected_rows, dimension)}"
        )
    if (
        not np.issubdtype(rows.dtype, np.number)
        or np.iscomplexobj(rows)
        or not np.isfinite(rows).all()
    ):
        raise ValueError("ADAPTER_OUTPUT_VALUES_INVALID")
    with np.errstate(over="ignore"):
        converted = np.ascontiguousarray(rows, dtype=np.float32)
    if not np.isfinite(converted).all():
        raise ValueError("ADAPTER_OUTPUT_VALUES_INVALID")
    return converted


def create_adapter(
    profile: ModelProfile, factory: Callable[[ModelProfile], Any]
) -> Siglip2Adapter:
    """Validate a V2 profile before constructing an injected implementation."""
    validate_model_profile(profile)
    if profile.family != "siglip2":
        raise ValueError("SIGLIP2_PROFILE_REQUIRED")
    if not callable(factory):
        raise ValueError("ADAPTER_FACTORY_REQUIRED")
    implementation = factory(profile)
    if not callable(getattr(implementation, "embed_images", None)):
        raise ValueError("ADAPTER_IMAGE_INTERFACE_REQUIRED")
    if not callable(getattr(implementation, "embed_texts", None)):
        raise ValueError("ADAPTER_TEXT_INTERFACE_REQUIRED")
    return Siglip2Adapter(profile=profile, implementation=implementation)


# --------------------------------------------------------------------------
# native session SOURCE boundary
# --------------------------------------------------------------------------


@runtime_checkable
class Siglip2Session(Protocol):
    """V2 encode surface named by the approved migration plan.

    A real implementation must also satisfy :data:`AUTHENTIC_SESSION_REQUIREMENTS`;
    nothing in this module loads or inspects a real bundle.
    """

    profile: ModelProfile
    runtime_identity: str
    authentic: bool

    def encode_image_paths(self, paths: Sequence[Path]) -> np.ndarray:
        """Return one L2-normalizable float row per input image path."""

    def encode_texts(self, texts: Sequence[str]) -> np.ndarray:
        """Return one L2-normalizable float row per input text."""


@dataclass(frozen=True)
class _InjectedSiglip2Session:
    """Guarded wrapper around an explicitly injected, non-authentic session."""

    profile: ModelProfile
    runtime_identity: str
    implementation: Any

    @property
    def authentic(self) -> bool:
        return False

    def encode_image_paths(self, paths: Sequence[Path]) -> np.ndarray:
        materialized = list(paths)
        return _validate_rows(
            self.implementation.encode_image_paths(materialized),
            len(materialized),
            self.profile.embedding_dim,
        )

    def encode_texts(self, texts: Sequence[str]) -> np.ndarray:
        materialized = list(texts)
        return _validate_rows(
            self.implementation.encode_texts(materialized),
            len(materialized),
            self.profile.embedding_dim,
        )


def _expected_device(profile: ModelProfile) -> str:
    expected = _PROFILE_DEVICE.get(profile.device_backend)
    if expected is None:
        raise ValueError(
            f"SIGLIP2_DEVICE_BACKEND_UNSUPPORTED:{profile.device_backend}"
        )
    return expected


def open_siglip2_session(
    profile: ModelProfile,
    model_root: Path,
    *,
    device: str,
    loader: Callable[[Path, str], Any] | None = None,
) -> Siglip2Session:
    """Open the guarded SOURCE-only V2 session boundary.

    Validates the closed profile, the absolute existing model root, and the
    profile-pinned device backend, then delegates construction to the injected
    ``loader`` and validates the returned implementation and its outputs.  It
    never reads a model/processor/tokenizer asset and never imports a model
    runtime.

    ``loader`` is mandatory: this slice deliberately provides no default
    authentic loader.  Passing ``None`` fails closed with
    ``SIGLIP2_AUTHENTIC_RUNTIME_UNAVAILABLE`` until a separately authorized,
    native-accepted runtime exists.
    """
    validate_model_profile(profile)
    if profile.family != "siglip2":
        raise ValueError("SIGLIP2_PROFILE_REQUIRED")
    root = Path(model_root)
    if not root.is_absolute():
        raise ValueError("SIGLIP2_MODEL_ROOT_MUST_BE_ABSOLUTE")
    if not root.is_dir():
        raise ValueError("SIGLIP2_MODEL_ROOT_NOT_FOUND")
    expected_device = _expected_device(profile)
    if device != expected_device:
        raise ValueError(
            f"SIGLIP2_DEVICE_PROFILE_MISMATCH:{device}!={expected_device}"
        )
    if loader is None:
        raise ValueError(
            "SIGLIP2_AUTHENTIC_RUNTIME_UNAVAILABLE:source_only_loader_required"
        )
    if not callable(loader):
        raise ValueError("SIGLIP2_LOADER_REQUIRED")
    implementation = loader(root, device)
    if implementation is None:
        raise ValueError("SIGLIP2_SESSION_IMPLEMENTATION_REQUIRED")
    missing = [
        name for name in _SESSION_METHODS
        if not callable(getattr(implementation, name, None))
    ]
    if missing:
        raise ValueError("SIGLIP2_SESSION_INTERFACE_INCOMPLETE:" + ",".join(missing))
    identity = getattr(implementation, "runtime_identity", None)
    if not isinstance(identity, str) or not identity:
        raise ValueError("SIGLIP2_SESSION_IDENTITY_REQUIRED")
    # The session must declare which closed profile it encodes for; silently
    # assuming the requested profile would let a mismatched runtime produce
    # rows that the caller then attributes to the wrong representation.
    if getattr(implementation, "profile", None) != profile:
        raise ValueError("SIGLIP2_SESSION_PROFILE_MISMATCH")
    if getattr(implementation, "authentic", False) is not False:
        # A double silently claiming authentic identity would let synthetic
        # evidence masquerade as native acceptance.
        raise ValueError("SIGLIP2_AUTHENTIC_HANDOFF_REQUIRES_NATIVE_ACCEPTANCE")
    return _InjectedSiglip2Session(
        profile=profile, runtime_identity=identity, implementation=implementation
    )
