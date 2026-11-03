"""Model-free contract tests for the closed V1/V2 representation profiles."""
from __future__ import annotations

import hashlib
import json
from dataclasses import replace

import pytest

from persistent_local_index.model_profile import (
    ModelProfile,
    profile_row_width_bytes,
    profile_semantic_space,
    validate_model_profile,
)
from persistent_local_index.model_space import semantic_space_id


def _profile(
    profile_id: str = "vip-v2-siglip2-base-224",
    *,
    text_preprocessing_contract: str | None = None,
    processor_digest: str = "a" * 64,
    image_preprocessing_digest: str = "b" * 64,
    precision_policy_id: str = "siglip2-fp16-compute-fp32-output",
    precision_policy_version: int = 1,
) -> ModelProfile:
    if profile_id == "vip-v1-siglip-base-224":
        default_text_contract = "padding=max_length"
        return ModelProfile(
            profile_id=profile_id,
            model_id="google/siglip-base-patch16-224",
            family="siglip",
            frozen_revision="7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            weights_sha256="2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8",
            processor_asset_digests=(("processor", "4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980"),),
            processor_digest="4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980",
            image_preprocessing_digest="d11ccb80f15d358a11bdb070e92e2d889005874b7db15823d5f10d9b2533b14a",
            text_preprocessing_contract=(
                default_text_contract
                if text_preprocessing_contract is None
                else text_preprocessing_contract
            ),
            image_size=224,
            patch_size=16,
            embedding_dim=768,
            output_dtype="float32",
            normalization="l2",
            loader_kind="siglip-v1",
            device_backend="cpu",
            precision_policy_id="v1-float32",
            precision_policy_version=1,
        )
    if profile_id == "vip-v2-siglip2-so400m-384":
        model_id, family, dim, size, patch, loader = (
            "google/siglip2-so400m-patch14-384", "siglip2", 1152, 384, 14, "siglip2-auto"
        )
        default_text_contract = "vip-v2-siglip2-so400m-384:text-synthetic:v1"
    else:
        model_id, family, dim, size, patch, loader = (
            "google/siglip2-base-patch16-224", "siglip2", 768, 224, 16, "siglip2-auto"
        )
        default_text_contract = "vip-v2-siglip2-base-224:text-synthetic:v1"
    assets = (("tokenizer.json", processor_digest),)
    processor_payload = json.dumps(
        {
            "identity_mapping": "vip-processor-assets-v1",
            "assets": [{"name": name, "sha256": digest} for name, digest in sorted(assets)],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return ModelProfile(
        profile_id=profile_id,
        model_id=model_id,
        family=family,
        frozen_revision="1" * 40,
        weights_sha256="c" * 64,
        processor_asset_digests=assets,
        processor_digest=hashlib.sha256(processor_payload.encode("utf-8")).hexdigest(),
        image_preprocessing_digest=image_preprocessing_digest,
        text_preprocessing_contract=(
            default_text_contract
            if text_preprocessing_contract is None
            else text_preprocessing_contract
        ),
        image_size=size,
        patch_size=patch,
        embedding_dim=dim,
        output_dtype="float32",
        normalization="l2",
        loader_kind=loader,
        device_backend="pytorch-mps",
        precision_policy_id=precision_policy_id,
        precision_policy_version=precision_policy_version,
    )


def test_v1_profile_recreates_preserved_semantic_space():
    profile = _profile("vip-v1-siglip-base-224")
    space = profile_semantic_space(profile)
    assert (
        space.model_identity,
        space.frozen_revision,
        space.weights_sha256,
        space.processor_digest,
        space.image_preprocessing_digest,
        space.text_preprocessing_contract,
        space.embedding_dim,
        space.dtype,
        space.normalization,
    ) == (
        "google/siglip-base-patch16-224",
        "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
        "2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8",
        "4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980",
        "d11ccb80f15d358a11bdb070e92e2d889005874b7db15823d5f10d9b2533b14a",
        "padding=max_length",
        768,
        "float32",
        "l2",
    )
    assert semantic_space_id(space) == "3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a"


def test_v1_and_v2_base_768_spaces_never_match():
    v1 = profile_semantic_space(_profile("vip-v1-siglip-base-224"))
    v2 = profile_semantic_space(_profile())
    assert v1.embedding_dim == v2.embedding_dim == 768
    assert semantic_space_id(v1) != semantic_space_id(v2)


@pytest.mark.parametrize(
    ("profile_id", "contract"),
    [
        ("vip-v1-siglip-base-224", "padding=max_length"),
        ("vip-v2-siglip2-base-224", "vip-v2-siglip2-base-224:text-synthetic:v1"),
        (
            "vip-v2-siglip2-so400m-384",
            "vip-v2-siglip2-so400m-384:text-synthetic:v1",
        ),
    ],
)
def test_owner_approved_text_contract_identity_is_accepted_for_its_profile(profile_id, contract):
    profile = _profile(profile_id, text_preprocessing_contract=contract)
    validate_model_profile(profile)
    assert profile_semantic_space(profile).text_preprocessing_contract == contract


@pytest.mark.parametrize(
    "contract",
    [
        "",
        "arbitrary=unsupported;tokenizer=maybe",
        "padding=max_length",
        " VIP-V2-SIGLIP2-BASE-224:TEXT-SYNTHETIC:V1",
        " vip-v2-siglip2-base-224:text-synthetic:v1",
        "vip-v2-siglip2-base-224:text-synthetic:v1 ",
    ],
)
def test_v2_profile_rejects_unlisted_text_contract_identity(contract):
    with pytest.raises(ValueError, match="MODEL_PROFILE_TEXT_CONTRACT_INVALID"):
        validate_model_profile(_profile(text_preprocessing_contract=contract))


def test_v1_profile_rejects_text_contract_outside_preserved_identity():
    with pytest.raises(ValueError, match="MODEL_PROFILE_TEXT_CONTRACT_INVALID"):
        validate_model_profile(
            _profile(
                "vip-v1-siglip-base-224",
                text_preprocessing_contract="padding=longest",
            )
        )


@pytest.mark.parametrize(
    ("profile_id", "other_profile_contract"),
    [
        (
            "vip-v2-siglip2-base-224",
            "vip-v2-siglip2-so400m-384:text-synthetic:v1",
        ),
        (
            "vip-v2-siglip2-so400m-384",
            "vip-v2-siglip2-base-224:text-synthetic:v1",
        ),
    ],
)
def test_v2_text_contract_identity_cannot_be_reused_across_profiles(
    profile_id, other_profile_contract
):
    with pytest.raises(ValueError, match="MODEL_PROFILE_TEXT_CONTRACT_INVALID"):
        validate_model_profile(
            _profile(profile_id, text_preprocessing_contract=other_profile_contract)
        )


def test_v2_text_contract_identity_rejects_unrecognized_version():
    with pytest.raises(ValueError, match="MODEL_PROFILE_TEXT_CONTRACT_INVALID"):
        validate_model_profile(
            _profile(
                text_preprocessing_contract="vip-v2-siglip2-base-224:text-synthetic:v2"
            )
        )


def test_changing_text_contract_identity_changes_semantic_space_id():
    space = profile_semantic_space(_profile())
    changed_identity = replace(
        space,
        text_preprocessing_contract="vip-v2-siglip2-base-224:text-synthetic:v2",
    )
    assert semantic_space_id(changed_identity) != semantic_space_id(space)


def test_three_profile_spaces_preserve_distinct_dimensions_and_identities():
    v1 = profile_semantic_space(_profile("vip-v1-siglip-base-224"))
    v2_base = profile_semantic_space(_profile("vip-v2-siglip2-base-224"))
    so400m = profile_semantic_space(_profile("vip-v2-siglip2-so400m-384"))

    assert v1.embedding_dim == v2_base.embedding_dim == 768
    assert so400m.embedding_dim == 1152
    assert profile_row_width_bytes(_profile("vip-v1-siglip-base-224")) == 3072
    assert profile_row_width_bytes(_profile("vip-v2-siglip2-base-224")) == 3072
    assert profile_row_width_bytes(_profile("vip-v2-siglip2-so400m-384")) == 4608
    identities = {semantic_space_id(v1), semantic_space_id(v2_base), semantic_space_id(so400m)}
    assert len(identities) == 3


def test_so400m_profile_width_is_4608_bytes():
    profile = _profile("vip-v2-siglip2-so400m-384")
    validate_model_profile(profile)
    assert profile_row_width_bytes(profile) == 4608


@pytest.mark.parametrize(
    "changes",
    [
        {"weights_sha256": "NOT_OBSERVED"},
        {"frozen_revision": "main"},
        {"processor_digest": ""},
    ],
)
def test_incomplete_digest_or_revision_fails_closed(changes):
    with pytest.raises(ValueError):
        validate_model_profile(replace(_profile(), **changes))


def test_changed_tokenizer_or_precision_changes_space():
    base = _profile()
    changed_tokenizer = _profile(processor_digest="d" * 64)
    changed_precision = _profile(precision_policy_id="siglip2-fp32-compute-fp32-output")
    assert semantic_space_id(profile_semantic_space(base)) != semantic_space_id(
        profile_semantic_space(changed_tokenizer)
    )
    assert semantic_space_id(profile_semantic_space(base)) != semantic_space_id(
        profile_semantic_space(changed_precision)
    )
    assert profile_row_width_bytes(_profile("vip-v1-siglip-base-224")) == 3072


def test_v2_effective_space_identity_is_deterministic_and_backend_bound():
    profile = _profile()
    assert profile_semantic_space(profile) == profile_semantic_space(profile)
    changed_backend = replace(profile, device_backend="pytorch-cpu")
    assert semantic_space_id(profile_semantic_space(profile)) != semantic_space_id(
        profile_semantic_space(changed_backend)
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"profile_id": "vip-v2-siglip2-large-224"},
        {"model_id": "google/siglip2-so400m-patch14-384"},
        {"processor_asset_digests": (("../tokenizer.json", "a" * 64),)},
        {"processor_asset_digests": (("tokenizer.json", "NOT_OBSERVED"),)},
        {"output_dtype": "float16"},
    ],
)
def test_profile_validation_rejects_open_or_unsafe_metadata(changes):
    with pytest.raises(ValueError):
        validate_model_profile(replace(_profile(), **changes))


@pytest.mark.parametrize(
    "changes",
    [
        {"device_backend": "unreviewed-backend"},
        {"precision_policy_id": "unreviewed-precision"},
        {"precision_policy_version": 2},
    ],
)
def test_profile_validation_rejects_unknown_backend_or_precision_policy(changes):
    with pytest.raises(ValueError):
        validate_model_profile(replace(_profile(), **changes))


@pytest.mark.parametrize("contract", [7, ["padding=max_length"], None, (), {"padding": "max_length"}])
def test_text_contract_rejects_non_string_values_with_value_error(contract):
    profile = replace(_profile(), text_preprocessing_contract=contract)
    with pytest.raises(ValueError, match="MODEL_PROFILE_TEXT_CONTRACT_INVALID"):
        validate_model_profile(profile)


@pytest.mark.parametrize(
    "changes",
    [
        {"precision_policy_id": "siglip2-fp16-compute-fp32-output"},
        {"precision_policy_id": "siglip2-fp32-compute-fp32-output"},
        {"precision_policy_id": "siglip2-q4-mixed-272-328-group32-fp16-compute"},
        {"device_backend": "pytorch-cpu"},
        {"device_backend": "pytorch-mps"},
    ],
)
def test_v1_rejects_backend_or_precision_outside_preserved_policy(changes):
    profile = replace(_profile("vip-v1-siglip-base-224"), **changes)
    with pytest.raises(ValueError):
        validate_model_profile(profile)


def test_v1_historical_cpu_float32_identity_remains_unchanged():
    profile = _profile("vip-v1-siglip-base-224")
    assert profile.device_backend == "cpu"
    assert profile.precision_policy_id == "v1-float32"
    assert semantic_space_id(profile_semantic_space(profile)) == (
        "3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a"
    )
