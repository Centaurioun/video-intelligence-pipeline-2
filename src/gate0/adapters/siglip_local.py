"""Local, offline, CPU-only SigLIP adapter for the Stage-A feasibility run.

The adapter intentionally targets the frozen Transformers 5.17 API.  In that
API the feature methods return ``BaseModelOutputWithPooling``; only its
``pooler_output`` member is part of the embedding seam.
"""
from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gate0.adapters.embedding import EmbeddingAdapter, EmbeddingResult


@dataclass(frozen=True)
class SiglipAssetIdentity:
    model_root: str
    revision: str
    weights_sha256: str
    processor_digest: str
    preprocessing_digest: str
    dimension: int


class LocalSiglipEmbeddingAdapter(EmbeddingAdapter):
    """Run frozen SigLIP feature extraction using an explicitly local model."""

    def __init__(self, model: Any, processor: Any, *, device: str = "cpu", asset_identity: SiglipAssetIdentity | None = None):
        if device != "cpu":
            raise ValueError("CPU_ONLY")
        self.model = model
        self.processor = processor
        self.device = device
        self.asset_identity = asset_identity

    @classmethod
    def load_cpu(cls, model_root: Path, *, expected_weights_sha256: str, revision: str = "") -> "LocalSiglipEmbeddingAdapter":
        root = Path(model_root)
        if not root.is_absolute():
            raise ValueError("MODEL_PATH_MUST_BE_ABSOLUTE")
        if not root.is_dir():
            raise ValueError("MODEL_ROOT_NOT_FOUND")
        weights = root / "model.safetensors"
        if not weights.is_file():
            raise ValueError("MODEL_WEIGHTS_NOT_FOUND")
        digest = hashlib.sha256(weights.read_bytes()).hexdigest()
        if digest != expected_weights_sha256:
            raise ValueError("MODEL_WEIGHTS_DIGEST_MISMATCH")

        # Offline flags are an explicit loading invariant, not a fallback.
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        try:
            from transformers import SiglipModel, SiglipProcessor
        except ImportError as exc:  # pragma: no cover - exercised by environment
            raise RuntimeError("TRANSFORMERS_REQUIRED") from exc
        model = SiglipModel.from_pretrained(
            str(root), local_files_only=True, trust_remote_code=False, use_safetensors=True
        )
        processor = SiglipProcessor.from_pretrained(
            str(root), local_files_only=True, trust_remote_code=False
        )
        model = model.to("cpu")
        model.eval()
        return cls(
            model,
            processor,
            device="cpu",
            asset_identity=SiglipAssetIdentity(str(root), revision, digest, "NOT_OBSERVED", "NOT_OBSERVED", 768),
        )

    @staticmethod
    def _failure(reason: str) -> EmbeddingResult:
        return EmbeddingResult(None, "FAILED", reason)

    def _result_from_output(self, output: Any) -> EmbeddingResult:
        pooled = getattr(output, "pooler_output", None)
        if pooled is None:
            return self._failure("MISSING_POOLER_OUTPUT")
        device = getattr(getattr(pooled, "device", None), "type", "cpu")
        if device != "cpu":
            return self._failure("NON_CPU_POOLER_OUTPUT")
        # Do not accept the complete model-output object, lists, or scalars.
        if not (hasattr(pooled, "detach") and hasattr(pooled, "tolist")):
            return self._failure("POOLER_OUTPUT_NOT_TENSOR")
        try:
            values = pooled.detach().to("cpu").reshape(-1).tolist()
            # Real torch tensors are flat after reshape; this recursive
            # normalization also keeps the seam deterministic for lightweight
            # tensor fakes used by unit tests.
            while isinstance(values, (list, tuple)) and values and isinstance(values[0], (list, tuple)):
                values = [item for row in values for item in row]
            vector = tuple(float(value) for value in values)
        except (AttributeError, TypeError, ValueError, RuntimeError):
            return self._failure("POOLER_OUTPUT_NOT_NUMERIC")
        if not vector or any(not math.isfinite(value) for value in vector):
            return self._failure("NON_FINITE_POOLER_OUTPUT")
        if all(value == 0.0 for value in vector):
            return self._failure("ZERO_POOLER_OUTPUT")
        return EmbeddingResult(vector)

    def embed(self, kind: str, value: Any) -> EmbeddingResult:
        if kind not in ("text", "pixels"):
            return self._failure("UNSUPPORTED_KIND")
        if kind == "text" and not isinstance(value, str):
            return self._failure("INVALID_TEXT_INPUT")
        if kind == "pixels" and not isinstance(value, (bytes, bytearray, memoryview)):
            return self._failure("INVALID_PIXELS_INPUT")
        try:
            if kind == "text":
                inputs = self.processor(text=value, padding="max_length", return_tensors="pt")
                with self._inference_mode():
                    output = self.model.get_text_features(**dict(inputs))
            else:
                from PIL import Image
                from io import BytesIO

                image = Image.open(BytesIO(bytes(value))).convert("RGB")
                inputs = self.processor(images=image, return_tensors="pt")
                with self._inference_mode():
                    output = self.model.get_image_features(**dict(inputs))
            return self._result_from_output(output)
        except Exception as exc:
            if isinstance(exc, (ValueError, TypeError)) and str(exc) in {"CPU_ONLY"}:
                raise
            return self._failure(f"FEATURE_EXTRACTION_FAILED:{type(exc).__name__}")

    @staticmethod
    def _inference_mode():
        try:
            import torch
            return torch.inference_mode()
        except ImportError:
            from contextlib import nullcontext
            return nullcontext()
