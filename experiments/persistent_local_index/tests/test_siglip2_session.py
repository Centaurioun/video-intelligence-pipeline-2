"""Gate-1 TDD: model-free SigLIP2 session SOURCE boundary.

The plan-named native adapter entry points (``open_siglip2_session`` /
``Siglip2Session.encode_image_paths`` / ``encode_texts``) do not exist yet.  This
module defines the *source* boundary only: no authentic tokenizer, processor,
model, device, cache, or network access.  The genuine native runtime remains
PENDING separate owner authorization and native acceptance.

Tests inject in-memory doubles; they never open a real model bundle.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pytest

from persistent_local_index.model_profile import ModelProfile
from persistent_local_index.siglip2_native import (
    Siglip2Session,
    open_siglip2_session,
)


def _siglip2_profile(
    profile_id: str = "vip-v2-siglip2-base-224",
    *,
    device_backend: str = "pytorch-mps",
) -> ModelProfile:
    if profile_id == "vip-v2-siglip2-so400m-384":
        model_id, dim, size, patch = (
            "google/siglip2-so400m-patch14-384",
            1152,
            384,
            14,
        )
        text_contract = "vip-v2-siglip2-so400m-384:text-synthetic:v1"
    else:
        model_id, dim, size, patch = (
            "google/siglip2-base-patch16-224",
            768,
            224,
            16,
        )
        text_contract = "vip-v2-siglip2-base-224:text-synthetic:v1"
    assets = (("tokenizer.json", "d" * 64),)
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
        family="siglip2",
        frozen_revision="1" * 40,
        weights_sha256="c" * 64,
        processor_asset_digests=assets,
        processor_digest=hashlib.sha256(processor_payload.encode("utf-8")).hexdigest(),
        image_preprocessing_digest="b" * 64,
        text_preprocessing_contract=text_contract,
        image_size=size,
        patch_size=patch,
        embedding_dim=dim,
        output_dtype="float32",
        normalization="l2",
        loader_kind="siglip2-auto",
        device_backend=device_backend,
        precision_policy_id="siglip2-fp16-compute-fp32-output",
        precision_policy_version=1,
    )


def _unit(seed: str, dim: int) -> np.ndarray:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    vector = rng.standard_normal(dim).astype(np.float32)
    return vector / np.linalg.norm(vector)


class _FakeImplementation:
    """In-memory double: deterministic rows, records injected inputs."""

    def __init__(
        self,
        profile: ModelProfile,
        *,
        runtime_identity: str = "source-only-test-double/v1",
        authentic: bool = False,
    ) -> None:
        self.profile = profile
        self.runtime_identity = runtime_identity
        self.authentic = authentic
        self.image_calls: list[list[Any]] = []
        self.text_calls: list[list[str]] = []

    def encode_image_paths(self, paths: Sequence[Any]) -> np.ndarray:
        self.image_calls.append(list(paths))
        rows = [_unit(f"image:{path}", self.profile.embedding_dim) for path in paths]
        return np.stack(rows).astype(np.float32)

    def encode_texts(self, texts: Sequence[str]) -> np.ndarray:
        self.text_calls.append(list(texts))
        rows = [_unit(f"text:{text}", self.profile.embedding_dim) for text in texts]
        return np.stack(rows).astype(np.float32)


def _loader_for(implementation: Any):
    calls: list[tuple[Path, str]] = []

    def loader(model_root: Path, device: str) -> Any:
        calls.append((Path(model_root), device))
        return implementation

    loader.calls = calls  # type: ignore[attr-defined]
    return loader


def _model_root(tmp_path: Path) -> Path:
    root = tmp_path / "model"
    root.mkdir()
    return root


# --- open-time fail-closed boundary ---------------------------------------


def test_open_requires_an_injected_loader(tmp_path: Path):
    """No default authentic loader: source-only slice cannot silently load."""
    with pytest.raises(ValueError, match="SIGLIP2_AUTHENTIC_RUNTIME_UNAVAILABLE"):
        open_siglip2_session(_siglip2_profile(), _model_root(tmp_path), device="mps")


def _v1_profile() -> ModelProfile:
    """Valid V1 profile: a real profile, but not a SigLIP2 adapter target."""
    return ModelProfile(
        profile_id="vip-v1-siglip-base-224",
        model_id="google/siglip-base-patch16-224",
        family="siglip",
        frozen_revision="7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
        weights_sha256="2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8",
        processor_asset_digests=(
            ("processor", "4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980"),
        ),
        processor_digest="4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980",
        image_preprocessing_digest="d11ccb80f15d358a11bdb070e92e2d889005874b7db15823d5f10d9b2533b14a",
        text_preprocessing_contract="padding=max_length",
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


def test_open_rejects_non_siglip2_profile(tmp_path: Path):
    with pytest.raises(ValueError, match="SIGLIP2_PROFILE_REQUIRED"):
        open_siglip2_session(
            _v1_profile(), _model_root(tmp_path), device="cpu", loader=lambda r, d: None
        )


def test_open_rejects_relative_model_root(tmp_path: Path):
    with pytest.raises(ValueError, match="SIGLIP2_MODEL_ROOT_MUST_BE_ABSOLUTE"):
        open_siglip2_session(
            _siglip2_profile(), Path("model"), device="mps", loader=lambda r, d: None
        )


def test_open_rejects_missing_model_root(tmp_path: Path):
    with pytest.raises(ValueError, match="SIGLIP2_MODEL_ROOT_NOT_FOUND"):
        open_siglip2_session(
            _siglip2_profile(),
            tmp_path / "missing",
            device="mps",
            loader=lambda r, d: None,
        )


def test_open_rejects_device_disagreeing_with_profile(tmp_path: Path):
    """The profile pins device_backend because it enters representation identity."""
    with pytest.raises(
        ValueError, match=r"SIGLIP2_DEVICE_PROFILE_MISMATCH:cpu!=mps"
    ):
        open_siglip2_session(
            _siglip2_profile(),
            _model_root(tmp_path),
            device="cpu",
            loader=lambda r, d: None,
        )


def test_open_rejects_non_callable_loader(tmp_path: Path):
    with pytest.raises(ValueError, match="SIGLIP2_LOADER_REQUIRED"):
        open_siglip2_session(
            _siglip2_profile(), _model_root(tmp_path), device="mps", loader="nope"
        )


def test_open_rejects_incomplete_session_interface(tmp_path: Path):
    class OnlyImages:
        runtime_identity = "partial/v1"

        def encode_image_paths(self, paths):
            return np.zeros((len(paths), 768), dtype=np.float32)

    with pytest.raises(
        ValueError, match=r"SIGLIP2_SESSION_INTERFACE_INCOMPLETE:encode_texts"
    ):
        open_siglip2_session(
            _siglip2_profile(),
            _model_root(tmp_path),
            device="mps",
            loader=lambda r, d: OnlyImages(),
        )


def test_open_rejects_implementation_without_runtime_identity(tmp_path: Path):
    implementation = _FakeImplementation(_siglip2_profile())
    implementation.runtime_identity = ""
    with pytest.raises(ValueError, match="SIGLIP2_SESSION_IDENTITY_REQUIRED"):
        open_siglip2_session(
            _siglip2_profile(),
            _model_root(tmp_path),
            device="mps",
            loader=lambda r, d: implementation,
        )


def test_open_refuses_authentic_claim_from_injected_double(tmp_path: Path):
    """A double may not impersonate an authentic runtime without native acceptance."""
    implementation = _FakeImplementation(_siglip2_profile(), authentic=True)
    with pytest.raises(
        ValueError, match="SIGLIP2_AUTHENTIC_HANDOFF_REQUIRES_NATIVE_ACCEPTANCE"
    ):
        open_siglip2_session(
            _siglip2_profile(),
            _model_root(tmp_path),
            device="mps",
            loader=lambda r, d: implementation,
        )


def test_open_rejects_implementation_without_declared_profile(tmp_path: Path):
    """An implementation that cannot declare its profile identity must fail closed."""

    class _NoProfile:
        runtime_identity = "synthetic:no-profile"

        def encode_image_paths(self, paths):
            return np.zeros((len(paths), 768), dtype=np.float32)

        def encode_texts(self, texts):
            return np.zeros((len(texts), 768), dtype=np.float32)

    with pytest.raises(ValueError, match="SIGLIP2_SESSION_PROFILE_MISMATCH"):
        open_siglip2_session(
            _siglip2_profile(),
            _model_root(tmp_path),
            device="mps",
            loader=lambda r, d: _NoProfile(),
        )


def test_open_rejects_implementation_for_another_profile(tmp_path: Path):
    other = _siglip2_profile("vip-v2-siglip2-so400m-384")
    with pytest.raises(ValueError, match="SIGLIP2_SESSION_PROFILE_MISMATCH"):
        open_siglip2_session(
            _siglip2_profile(),
            _model_root(tmp_path),
            device="mps",
            loader=lambda r, d: _FakeImplementation(other),
        )


# --- construction + output validation -------------------------------------


def test_open_passes_root_and_device_to_the_injected_loader(tmp_path: Path):
    profile = _siglip2_profile()
    root = _model_root(tmp_path)
    loader = _loader_for(_FakeImplementation(profile))
    session = open_siglip2_session(profile, root, device="mps", loader=loader)
    assert loader.calls == [(root, "mps")]
    assert session.profile is profile
    assert session.authentic is False


def test_session_encodes_768_rows_at_profile_width(tmp_path: Path):
    profile = _siglip2_profile()
    session = open_siglip2_session(
        profile,
        _model_root(tmp_path),
        device="mps",
        loader=lambda r, d: _FakeImplementation(profile),
    )
    images = session.encode_image_paths([tmp_path / "a.jpg", tmp_path / "b.jpg"])
    texts = session.encode_texts(["a query", "another query", "third"])
    assert images.shape == (2, 768) and images.dtype == np.float32
    assert texts.shape == (3, 768) and texts.dtype == np.float32


def test_session_encodes_1152_rows_at_profile_width(tmp_path: Path):
    profile = _siglip2_profile("vip-v2-siglip2-so400m-384")
    session = open_siglip2_session(
        profile,
        _model_root(tmp_path),
        device="mps",
        loader=lambda r, d: _FakeImplementation(profile),
    )
    assert session.encode_image_paths([tmp_path / "a.jpg"]).shape == (1, 1152)
    assert session.encode_texts(["q"]).shape == (1, 1152)


def test_session_rejects_wrong_row_count(tmp_path: Path):
    profile = _siglip2_profile()

    class WrongRows(_FakeImplementation):
        def encode_texts(self, texts):
            return np.zeros((1, 768), dtype=np.float32)

    session = open_siglip2_session(
        profile,
        _model_root(tmp_path),
        device="mps",
        loader=lambda r, d: WrongRows(profile),
    )
    with pytest.raises(ValueError, match="ADAPTER_OUTPUT_SHAPE_INVALID"):
        session.encode_texts(["one", "two"])


def test_session_rejects_wrong_width(tmp_path: Path):
    profile = _siglip2_profile()

    class WrongWidth(_FakeImplementation):
        def encode_image_paths(self, paths):
            return np.zeros((len(paths), 767), dtype=np.float32)

    session = open_siglip2_session(
        profile,
        _model_root(tmp_path),
        device="mps",
        loader=lambda r, d: WrongWidth(profile),
    )
    with pytest.raises(ValueError, match="ADAPTER_OUTPUT_SHAPE_INVALID"):
        session.encode_image_paths([tmp_path / "a.jpg"])


@pytest.mark.parametrize(
    "payload",
    [
        np.array([[np.nan] * 768], dtype=np.float32),
        np.array([[np.inf] * 768], dtype=np.float32),
        np.array([[1 + 2j] * 768], dtype=np.complex64),
        np.array([["not-a-number"] * 768]),
    ],
)
def test_session_rejects_invalid_values(tmp_path: Path, payload: np.ndarray):
    profile = _siglip2_profile()

    class BadValues(_FakeImplementation):
        def encode_texts(self, texts):
            return payload

    session = open_siglip2_session(
        profile,
        _model_root(tmp_path),
        device="mps",
        loader=lambda r, d: BadValues(profile),
    )
    with pytest.raises(ValueError, match="ADAPTER_OUTPUT_VALUES_INVALID"):
        session.encode_texts(["q"])


def test_session_normalizes_dtype_to_float32(tmp_path: Path):
    profile = _siglip2_profile()

    class Float64(_FakeImplementation):
        def encode_texts(self, texts):
            return np.ones((len(texts), 768), dtype=np.float64)

    session = open_siglip2_session(
        profile,
        _model_root(tmp_path),
        device="mps",
        loader=lambda r, d: Float64(profile),
    )
    rows = session.encode_texts(["q"])
    assert rows.dtype == np.float32
    assert rows.flags["C_CONTIGUOUS"]


# --- source-only proof -----------------------------------------------------


def test_open_and_encode_never_read_model_assets(tmp_path: Path, monkeypatch):
    """The source boundary must not open files inside the model root."""
    profile = _siglip2_profile()
    root = _model_root(tmp_path)
    (root / "tokenizer.json").write_bytes(b"sentinel")

    def _deny(self, *args, **kwargs):  # noqa: ANN001
        raise AssertionError(f"model asset opened by source-only boundary: {self}")

    monkeypatch.setattr(Path, "open", _deny)
    monkeypatch.setattr(Path, "read_bytes", _deny)
    monkeypatch.setattr(Path, "read_text", _deny)

    session = open_siglip2_session(
        profile,
        root,
        device="mps",
        loader=lambda r, d: _FakeImplementation(profile),
    )
    assert session.encode_texts(["q"])[0] is not None
    assert np.isfinite(session.encode_image_paths([tmp_path / "absent.jpg"])).all()


def test_open_does_not_call_loader_when_prevalidation_fails(tmp_path: Path):
    """Profile/root/device failures must refuse before any injected loader runs."""
    loader = _loader_for(_FakeImplementation(_siglip2_profile()))

    with pytest.raises(ValueError, match="SIGLIP2_DEVICE_PROFILE_MISMATCH"):
        open_siglip2_session(
            _siglip2_profile(), _model_root(tmp_path), device="cpu", loader=loader
        )
    with pytest.raises(ValueError, match="SIGLIP2_MODEL_ROOT_NOT_FOUND"):
        open_siglip2_session(
            _siglip2_profile(), tmp_path / "absent", device="mps", loader=loader
        )
    assert loader.calls == []


def test_open_accepts_implementation_without_authentic_attribute(tmp_path: Path):
    """A missing `authentic` flag is a non-claim; the wrapper still reports False."""
    profile = _siglip2_profile()
    implementation = _FakeImplementation(profile)
    del implementation.authentic

    session = open_siglip2_session(
        profile, _model_root(tmp_path), device="mps", loader=_loader_for(implementation)
    )

    assert session.authentic is False


def test_open_accepts_equal_value_profile_from_implementation(tmp_path: Path):
    """Value equality is the identity contract for a frozen profile dataclass."""
    profile = _siglip2_profile()
    equal_copy = _siglip2_profile()
    assert equal_copy == profile
    assert equal_copy is not profile

    session = open_siglip2_session(
        profile,
        _model_root(tmp_path),
        device="mps",
        loader=_loader_for(_FakeImplementation(equal_copy)),
    )

    assert session.profile is profile


def test_open_wrapper_reports_non_authentic_and_validates_width(tmp_path: Path):
    profile = _siglip2_profile()
    session = open_siglip2_session(
        profile,
        _model_root(tmp_path),
        device="mps",
        loader=_loader_for(_FakeImplementation(profile)),
    )

    assert session.authentic is False
    assert session.encode_image_paths([Path("a.jpg")]).shape == (1, 768)
    assert session.encode_texts(["a", "b"]).shape == (2, 768)
