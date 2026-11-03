"""Model-free contract tests for the fake-injected SigLIP2 adapter boundary."""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

from persistent_local_index.model_profile import ModelProfile
from persistent_local_index import siglip2_native


def _profile(profile_id: str = "vip-v2-siglip2-base-224") -> ModelProfile:
    if profile_id == "vip-v1-siglip-base-224":
        return ModelProfile(
            profile_id=profile_id, model_id="google/siglip-base-patch16-224",
            family="siglip", frozen_revision="7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            weights_sha256="2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8",
            processor_asset_digests=(("processor", "4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980"),),
            processor_digest="4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980",
            image_preprocessing_digest="d11ccb80f15d358a11bdb070e92e2d889005874b7db15823d5f10d9b2533b14a",
            text_preprocessing_contract="padding=max_length", image_size=224, patch_size=16,
            embedding_dim=768, output_dtype="float32", normalization="l2",
            loader_kind="siglip-v1", device_backend="cpu", precision_policy_id="v1-float32",
            precision_policy_version=1,
        )
    if profile_id == "vip-v2-siglip2-so400m-384":
        model_id, dim, size, patch = "google/siglip2-so400m-patch14-384", 1152, 384, 14
    else:
        model_id, dim, size, patch = "google/siglip2-base-patch16-224", 768, 224, 16
    assets = (("tokenizer.json", "a" * 64),)
    payload = json.dumps(
        {"identity_mapping": "vip-processor-assets-v1", "assets": [{"name": n, "sha256": d} for n, d in assets]},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    return ModelProfile(
        profile_id=profile_id, model_id=model_id, family="siglip2",
        frozen_revision="1" * 40, weights_sha256="b" * 64,
        processor_asset_digests=assets,
        processor_digest=hashlib.sha256(payload.encode()).hexdigest(),
        image_preprocessing_digest="c" * 64,
        text_preprocessing_contract=f"{profile_id}:text-synthetic:v1",
        image_size=size, patch_size=patch, embedding_dim=dim,
        output_dtype="float32", normalization="l2", loader_kind="siglip2-auto",
        device_backend="pytorch-cpu", precision_policy_id="siglip2-fp32-compute-fp32-output",
        precision_policy_version=1,
    )


class _Fake:
    def __init__(self, dimension):
        self.dimension = dimension

    def embed_images(self, images):
        return np.ones((len(images), self.dimension), dtype=np.float32)

    def embed_texts(self, texts):
        return np.ones((len(texts), self.dimension), dtype=np.float32)


def test_factory_is_called_only_after_v2_profile_validation():
    calls = []
    profile = _profile()
    adapter = siglip2_native.create_adapter(profile, lambda value: calls.append(value) or _Fake(value.embedding_dim))
    assert calls == [profile]
    assert adapter.profile == profile


def test_invalid_profile_fails_before_injected_factory():
    calls = []
    invalid = _profile()
    object.__setattr__(invalid, "model_id", "untrusted/model")
    with pytest.raises(ValueError, match="MODEL_PROFILE_UNSUPPORTED:model_id"):
        siglip2_native.create_adapter(invalid, lambda profile: calls.append(profile))
    assert calls == []


@pytest.mark.parametrize("profile_id,dimension", [
    ("vip-v2-siglip2-base-224", 768),
    ("vip-v2-siglip2-so400m-384", 1152),
])
def test_fake_adapter_outputs_are_dimension_checked(profile_id, dimension):
    adapter = siglip2_native.create_adapter(_profile(profile_id), lambda p: _Fake(p.embedding_dim))
    assert adapter.embed_images(["synthetic-image"]).shape == (1, dimension)
    assert adapter.embed_texts(["synthetic-query"]).shape == (1, dimension)


def test_v1_profile_is_rejected_before_factory():
    calls = []
    with pytest.raises(ValueError, match="SIGLIP2_PROFILE_REQUIRED"):
        siglip2_native.create_adapter(_profile("vip-v1-siglip-base-224"), lambda p: calls.append(p))
    assert calls == []


@pytest.mark.parametrize(
    "output,match",
    [
        (np.full((1, 768), 1 + 2j), "ADAPTER_OUTPUT_VALUES_INVALID"),
        (np.ones((1, 767)), "ADAPTER_OUTPUT_SHAPE_INVALID"),
        (np.full((1, 768), np.nan), "ADAPTER_OUTPUT_VALUES_INVALID"),
        (np.full((1, 768), "not-a-number"), "ADAPTER_OUTPUT_VALUES_INVALID"),
    ],
)
def test_malformed_fake_outputs_fail_closed(output, match):
    class ReturningFake:
        def embed_images(self, images):
            return output

        def embed_texts(self, texts):
            return output

    adapter = siglip2_native.create_adapter(_profile(), lambda p: ReturningFake())
    with pytest.raises(ValueError, match=match):
        adapter.embed_images(["synthetic-image"])


@pytest.mark.parametrize("method,input_value", [
    ("embed_images", ["synthetic-image"]),
    ("embed_texts", ["synthetic-query"]),
])
def test_finite_float64_values_that_overflow_float32_are_rejected(method, input_value):
    output = np.full((1, 768), np.finfo(np.float64).max, dtype=np.float64)

    class ReturningFake:
        def embed_images(self, images):
            return output

        def embed_texts(self, texts):
            return output

    adapter = siglip2_native.create_adapter(_profile(), lambda p: ReturningFake())
    with pytest.raises(ValueError, match="ADAPTER_OUTPUT_VALUES_INVALID"):
        getattr(adapter, method)(input_value)


@pytest.mark.parametrize("method,input_value", [
    ("embed_images", ["synthetic-image"]),
    ("embed_texts", ["synthetic-query"]),
])
def test_finite_float32_adapter_output_is_returned_as_finite_float32(method, input_value):
    output = np.full((1, 768), 0.5, dtype=np.float32)

    class ReturningFake:
        def embed_images(self, images):
            return output

        def embed_texts(self, texts):
            return output

    adapter = siglip2_native.create_adapter(_profile(), lambda p: ReturningFake())
    result = getattr(adapter, method)(input_value)

    assert result.dtype == np.float32
    assert result.flags.c_contiguous
    assert np.isfinite(result).all()
    np.testing.assert_array_equal(result, output)


@pytest.mark.parametrize(
    "implementation,match",
    [
        (type("NoImageMethod", (), {"embed_texts": lambda self, texts: []})(), "ADAPTER_IMAGE_INTERFACE_REQUIRED"),
        (type("NoTextMethod", (), {"embed_images": lambda self, images: []})(), "ADAPTER_TEXT_INTERFACE_REQUIRED"),
    ],
)
def test_missing_fake_methods_are_rejected(implementation, match):
    with pytest.raises(ValueError, match=match):
        siglip2_native.create_adapter(_profile(), lambda p: implementation)
