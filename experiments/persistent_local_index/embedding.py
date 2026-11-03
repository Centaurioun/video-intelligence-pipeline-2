"""Frozen local SigLIP embedding seam for indexing and query.

Authority: approved design sections 2.2, 11 and plan Task 4.

This is a thin experimental wrapper around the existing Gate-0 adapter
(``src/gate0/adapters/siglip_local.py``).  It deliberately reuses the existing
weights-digest verification and the proven ``padding="max_length"`` text
contract instead of introducing a second, divergent model path.

Device discipline: ``mps`` must be explicitly available, otherwise the call
fails loudly with ``MPS_REQUESTED_BUT_UNAVAILABLE``.  There is no silent CPU
fallback, because a silent fallback would make measured runs unreproducible.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from persistent_local_index.model_space import (
    EMBEDDING_DIM,
    TEXT_PREPROCESSING_CONTRACT,
)

_SUPPORTED_DEVICES = ("cpu", "mps")

#: `padding="max_length"` is SigLIP's trained text contract, not a preference.
#: The preserved spike showed that omitting it produced 7/7 MISS on a real source.
TEXT_PADDING = "max_length"


@dataclass
class LocalSiglipSession:
    adapter: object
    device: str
    dimension: int


def _mps_available() -> bool:
    try:
        import torch
    except ImportError:  # pragma: no cover - torch is a hard runtime dependency
        return False
    return bool(torch.backends.mps.is_built() and torch.backends.mps.is_available())


def require_device(device: str) -> str:
    """Validate an explicitly requested device.  Never falls back silently."""
    if device not in _SUPPORTED_DEVICES:
        raise ValueError(f"UNSUPPORTED_DEVICE:{device!r}")
    if device == "mps" and not _mps_available():
        raise RuntimeError("MPS_REQUESTED_BUT_UNAVAILABLE")
    return device


def _digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _load_adapter(model_root: Path, expected_weights_sha256: str):
    """Load the real local adapter.  Kept as a seam so tests can intercept it."""
    import sys

    repository_root = Path(__file__).resolve().parents[2]
    source_root = str(repository_root / "src")
    if source_root not in sys.path:
        sys.path.insert(0, source_root)
    from gate0.adapters.siglip_local import LocalSiglipEmbeddingAdapter

    return LocalSiglipEmbeddingAdapter.load_cpu(
        Path(model_root), expected_weights_sha256=expected_weights_sha256
    )


def load_session(
    model_root: Path, expected_weights_sha256: str, *, device: str
) -> LocalSiglipSession:
    """Load the frozen local model for an explicitly requested device.

    The weights digest is verified *before* any model load is attempted, so a
    wrong or substituted checkpoint fails closed and cheaply.
    """
    device = require_device(device)
    model_root = Path(model_root)
    if not model_root.is_absolute():
        raise ValueError("MODEL_PATH_MUST_BE_ABSOLUTE")
    weights = model_root / "model.safetensors"
    if not weights.is_file():
        raise ValueError("MODEL_WEIGHTS_NOT_FOUND")
    if _digest_file(weights) != expected_weights_sha256:
        raise ValueError("MODEL_WEIGHTS_DIGEST_MISMATCH")

    adapter = _load_adapter(model_root, expected_weights_sha256)
    if device == "mps":
        # The Gate-0 adapter is CPU-only by contract.  This experimental wrapper
        # performs the move on the caller's behalf; the adapter itself is not
        # modified, so no Gate-0 contract changes.
        import torch

        adapter.model.to(torch.device("mps")).eval()
        adapter.device = "mps"
    return LocalSiglipSession(adapter=adapter, device=device, dimension=EMBEDDING_DIM)


def _pooled_rows(output) -> np.ndarray:
    pooled = getattr(output, "pooler_output", None)
    if pooled is None:
        raise ValueError("MISSING_POOLER_OUTPUT")
    array = pooled.detach().to("cpu").float().numpy()
    if array.ndim == 1:
        array = array.reshape(1, -1)
    return np.ascontiguousarray(array, dtype=np.float32)


def _to_device(inputs, device: str):
    import torch

    target = torch.device(device)
    return {
        key: (value.to(target) if hasattr(value, "to") else value)
        for key, value in dict(inputs).items()
    }


def _synchronize(device: str) -> None:
    if device == "mps":
        import torch

        torch.mps.synchronize()


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalization to float32, with explicit fail-closed guards."""
    array = np.asarray(matrix)
    if array.size == 0 or array.ndim != 2 or array.shape[0] == 0:
        raise ValueError(f"EMPTY_MATRIX:{getattr(array, 'shape', None)}")
    if not np.isfinite(array).all():
        raise ValueError("NON_FINITE_INPUT")
    norms = np.linalg.norm(array.astype(np.float64), axis=1, keepdims=True)
    if np.any(norms == 0.0):
        raise ValueError("ZERO_VECTOR_INPUT")
    return np.ascontiguousarray(array / norms, dtype=np.float32)


def build_fake_profile_runtime(profile):
    """Build a visibly fake runtime bound to a validated closed model profile.

    This test/development seam uses only path/text labels to generate vectors;
    it never opens image paths, model bundles, processors, caches, or devices.
    The Task 4 adapter validates profile binding and output shape/value.
    """
    from types import SimpleNamespace

    from .model_profile import profile_semantic_space
    from .siglip2_native import create_adapter
    from vip_fvs.local_semantic import checked_runtime

    def vectors(values, *, salt: str) -> np.ndarray:
        rows = []
        for value in values:
            raw = bytearray()
            counter = 0
            while len(raw) < profile.embedding_dim * 4:
                raw.extend(hashlib.sha256(
                    f"vip-profile-fake/v1:{profile.profile_id}:{salt}:{value}:{counter}".encode("utf-8")
                ).digest())
                counter += 1
            words = np.frombuffer(bytes(raw[:profile.embedding_dim * 4]), dtype="<u4")
            row = (words.astype(np.float64) / float(2**32 - 1)) * 2.0 - 1.0
            norm = np.linalg.norm(row)
            if norm == 0.0:
                raise ValueError("ZERO_SYNTHETIC_PROFILE_VECTOR")
            rows.append(np.ascontiguousarray(row / norm, dtype=np.float32))
        if not rows:
            raise ValueError("EMPTY_SYNTHETIC_PROFILE_INPUT")
        return np.stack(rows).astype(np.float32, copy=False)

    implementation = SimpleNamespace(
        embed_images=lambda paths: vectors((str(Path(path)) for path in paths), salt="image"),
        embed_texts=lambda texts: vectors((str(text) for text in texts), salt="text"),
    )
    adapter = create_adapter(profile, lambda _profile: implementation)
    return checked_runtime(
        image_embedder=adapter.embed_images,
        text_embedder=adapter.embed_texts,
        semantic_space=profile_semantic_space(profile),
        fake=True,
        runtime_identity=f"vip-profile-fake/v1:{profile.profile_id}",
    )


def embed_images(
    session: LocalSiglipSession, image_paths: Sequence[Path], *, batch_size: int = 8
) -> np.ndarray:
    """Embed images in batches, preserving input row order, L2-normalized."""
    paths = [Path(p) for p in image_paths]
    if not paths:
        raise ValueError("NO_IMAGES")
    if batch_size < 1:
        raise ValueError(f"INVALID_BATCH_SIZE:{batch_size}")
    for path in paths:
        if not path.is_file():
            raise ValueError(f"IMAGE_MISSING:{path}")

    import torch
    from PIL import Image

    rows: list[np.ndarray] = []
    with torch.inference_mode():
        for start in range(0, len(paths), batch_size):
            chunk = paths[start:start + batch_size]
            images = []
            for path in chunk:
                with Image.open(path) as handle:
                    images.append(handle.convert("RGB"))
            inputs = session.adapter.processor(images=images, return_tensors="pt")
            output = session.adapter.model.get_image_features(
                **_to_device(inputs, session.device)
            )
            _synchronize(session.device)
            rows.append(_pooled_rows(output))
    stacked = np.concatenate(rows, axis=0) if rows else np.zeros((0, session.dimension), np.float32)
    if stacked.shape[0] != len(paths):
        raise ValueError(f"IMAGE_EMBED_ROW_MISMATCH:{stacked.shape[0]}!={len(paths)}")
    if stacked.shape[1] != session.dimension:
        raise ValueError(
            f"EMBEDDING_DIM_MISMATCH:{stacked.shape[1]}!={session.dimension}"
        )
    return l2_normalize(stacked)


def embed_texts(session: LocalSiglipSession, texts: Sequence[str]) -> np.ndarray:
    """Embed text queries once, with the proven max-length padding contract."""
    values = [str(text) for text in texts]
    if not values:
        raise ValueError("NO_TEXTS")

    import torch

    with torch.inference_mode():
        inputs = session.adapter.processor(
            text=values, padding=TEXT_PADDING, return_tensors="pt"
        )
        output = session.adapter.model.get_text_features(
            **_to_device(inputs, session.device)
        )
        _synchronize(session.device)
        rows = _pooled_rows(output)

    if rows.shape[0] != len(values):
        raise ValueError(f"TEXT_EMBED_ROW_MISMATCH:{rows.shape[0]}!={len(values)}")
    if rows.shape[1] != session.dimension:
        raise ValueError(f"EMBEDDING_DIM_MISMATCH:{rows.shape[1]}!={session.dimension}")
    return l2_normalize(rows)


#: Re-exported so callers can assert the pinned contract without importing internals.
__all__ = [
    "LocalSiglipSession",
    "TEXT_PREPROCESSING_CONTRACT",
    "embed_images",
    "embed_texts",
    "build_fake_profile_runtime",
    "l2_normalize",
    "load_session",
    "require_device",
]
