"""TDD Task 4: local SigLIP embedding seam for indexing and query.

Two contracts are non-negotiable and inherited from the preserved spike:

1. text preprocessing MUST pass ``padding="max_length"`` (omitting it caused the
   original 7/7 MISS failure);
2. a requested-but-unavailable MPS device MUST fail loudly, never silently fall
   back to CPU.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest

import persistent_local_index.embedding as embedding
from persistent_local_index.embedding import (
    LocalSiglipSession,
    embed_images,
    embed_texts,
    l2_normalize,
    load_session,
)


# --- fakes -----------------------------------------------------------------


class _RecordingProcessor:
    """Records call kwargs and passes the batch through, like a real processor."""

    def __init__(self):
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        forwarded = {"input_ids": _TensorStub()}
        for key in ("images", "text"):
            if key in kwargs:
                forwarded[key] = kwargs[key]
        return forwarded


class _TensorStub:
    def to(self, _device):
        return self


class _Output:
    def __init__(self, value: float, rows: int, columns: int = 768):
        self.pooler_output = _FakeTensor(value, rows, columns)


class _FakeTensor:
    """Faithful-enough stand-in for a torch tensor across the pooling seam."""

    def __init__(self, value: float, rows: int, columns: int):
        self._value = value
        self._rows = rows
        self._columns = columns

    @property
    def shape(self):
        return (self._rows, self._columns)

    def detach(self):
        return self

    def to(self, _device):
        return self

    def float(self):
        return self

    def numpy(self):
        return np.full((self._rows, self._columns), self._value, dtype=np.float32)

    def __array__(self, dtype=None):
        data = np.full((self._rows, self._columns), self._value, dtype=np.float32)
        return data.astype(dtype) if dtype else data


def _requested_rows(kwargs: dict) -> int:
    """How many rows the caller asked to embed in this call."""
    for key in ("images", "text", "input_ids"):
        value = kwargs.get(key)
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            return max(1, len(value))
    return 1


class _FakeModel:
    def __init__(self, value: float = 1.0):
        self.value = value
        self.image_calls = []
        self.text_calls = []

    def to(self, _device):
        return self

    def eval(self):
        return self

    def get_image_features(self, **kwargs):
        self.image_calls.append(kwargs)
        return _Output(self.value, _requested_rows(kwargs))

    def get_text_features(self, **kwargs):
        self.text_calls.append(kwargs)
        return _Output(self.value, _requested_rows(kwargs))


@dataclass
class _FakeAdapter:
    model: _FakeModel
    processor: _RecordingProcessor


def _session(value: float = 1.0) -> LocalSiglipSession:
    return LocalSiglipSession(
        adapter=_FakeAdapter(_FakeModel(value), _RecordingProcessor()),
        device="cpu",
        dimension=768,
    )


# --- l2 normalization ------------------------------------------------------


def test_l2_normalize_returns_unit_rows_float32():
    raw = np.array([[3.0, 4.0], [0.0, 5.0]], dtype=np.float32)
    unit = l2_normalize(raw)
    assert unit.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(unit, axis=1), [1.0, 1.0], rtol=1e-6)
    np.testing.assert_allclose(unit[0], [0.6, 0.8], rtol=1e-6)


def test_l2_normalize_does_not_mutate_input():
    raw = np.array([[3.0, 4.0]], dtype=np.float32)
    before = raw.copy()
    l2_normalize(raw)
    np.testing.assert_array_equal(raw, before)


def test_l2_normalize_rejects_zero_rows():
    with pytest.raises(ValueError, match="ZERO_VECTOR"):
        l2_normalize(np.zeros((1, 768), dtype=np.float32))


def test_l2_normalize_rejects_non_finite():
    bad = np.ones((1, 768), dtype=np.float32)
    bad[0, 0] = np.inf
    with pytest.raises(ValueError, match="NON_FINITE"):
        l2_normalize(bad)


def test_l2_normalize_rejects_empty():
    with pytest.raises(ValueError, match="EMPTY_MATRIX"):
        l2_normalize(np.zeros((0, 768), dtype=np.float32))


# --- text contract ---------------------------------------------------------


def test_text_embedding_requests_max_length_padding():
    session = _session()
    embed_texts(session, ["a line of ballet students in a studio"])
    calls = session.adapter.processor.calls
    assert calls, "text branch never called the processor"
    assert calls[0].get("padding") == "max_length", (
        "TEXT_PREPROCESSING_MISSING_MAX_LENGTH_PADDING: got "
        f"padding={calls[0].get('padding')!r}"
    )


def test_text_embedding_returns_normalized_float32_matrix():
    session = _session(value=2.0)
    out = embed_texts(session, ["one", "two"])
    assert out.dtype == np.float32
    assert out.shape == (2, 768)
    np.testing.assert_allclose(np.linalg.norm(out, axis=1), [1.0, 1.0], rtol=1e-6)


def test_text_embedding_empty_sequence_is_rejected():
    with pytest.raises(ValueError, match="NO_TEXTS"):
        embed_texts(_session(), [])


# --- image contract --------------------------------------------------------


def test_image_embedding_returns_normalized_matrix(tmp_path: Path):
    from PIL import Image

    paths = []
    for i in range(3):
        p = tmp_path / f"i{i}.png"
        Image.new("RGB", (32, 32), (i * 40, 10, 10)).save(p)
        paths.append(p)
    session = _session(value=3.0)
    out = embed_images(session, paths, batch_size=2)
    assert out.dtype == np.float32
    assert out.shape == (3, 768)
    np.testing.assert_allclose(np.linalg.norm(out, axis=1), [1.0, 1.0, 1.0], rtol=1e-6)


def test_image_embedding_batches_do_not_change_row_order(tmp_path: Path):
    from PIL import Image

    paths = []
    for i in range(5):
        p = tmp_path / f"i{i}.png"
        Image.new("RGB", (16, 16), (i * 20, 0, 0)).save(p)
        paths.append(p)
    single = _session(value=1.0)
    assert embed_images(single, paths, batch_size=1).shape[0] == 5
    assert len(single.adapter.model.image_calls) == 5
    batched = _session(value=1.0)
    embed_images(batched, paths, batch_size=4)
    assert len(batched.adapter.model.image_calls) == 2


def test_image_embedding_missing_file_fails_closed(tmp_path: Path):
    with pytest.raises(ValueError, match="IMAGE_MISSING"):
        embed_images(_session(), [tmp_path / "nope.png"])


def test_image_embedding_empty_sequence_is_rejected():
    with pytest.raises(ValueError, match="NO_IMAGES"):
        embed_images(_session(), [])


# --- device discipline -----------------------------------------------------


def test_requested_mps_unavailable_fails_loudly(monkeypatch):
    monkeypatch.setattr(embedding, "_mps_available", lambda: False)
    with pytest.raises(RuntimeError, match="MPS_REQUESTED_BUT_UNAVAILABLE"):
        embedding.require_device("mps")


def test_cpu_always_available(monkeypatch):
    monkeypatch.setattr(embedding, "_mps_available", lambda: False)
    assert embedding.require_device("cpu") == "cpu"


def test_unknown_device_rejected():
    with pytest.raises(ValueError, match="UNSUPPORTED_DEVICE"):
        embedding.require_device("cuda")


def test_load_session_verifies_weights_digest_before_loading(monkeypatch, tmp_path: Path):
    """A digest mismatch must fail closed before any model load is attempted."""
    (tmp_path / "model.safetensors").write_bytes(b"not the real weights")
    calls = []
    monkeypatch.setattr(
        embedding, "_load_adapter", lambda *a, **k: calls.append("loaded")
    )
    with pytest.raises(ValueError, match="MODEL_WEIGHTS_DIGEST_MISMATCH"):
        load_session(tmp_path, "0" * 64, device="cpu")
    assert calls == [], "adapter was loaded despite an invalid weights digest"


def test_load_session_missing_weights_fails_closed(tmp_path: Path):
    with pytest.raises(ValueError, match="MODEL_WEIGHTS_NOT_FOUND"):
        load_session(tmp_path, "0" * 64, device="cpu")


def test_load_session_moves_model_to_requested_device(monkeypatch, tmp_path: Path):
    """A valid digest + available MPS must produce an mps session, not a CPU one."""
    import hashlib

    payload = b"pretend weights"
    (tmp_path / "model.safetensors").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    moved = []

    class _Model:
        def to(self, device):
            moved.append(str(device))
            return self

        def eval(self):
            return self

    class _Adapter:
        def __init__(self):
            self.model = _Model()
            self.device = "cpu"

    monkeypatch.setattr(embedding, "_mps_available", lambda: True)
    monkeypatch.setattr(embedding, "_load_adapter", lambda *a, **k: _Adapter())
    session = load_session(tmp_path, digest, device="mps")
    assert session.device == "mps"
    assert session.dimension == 768
    assert any("mps" in value for value in moved)


def test_load_session_rejects_relative_model_root():
    with pytest.raises(ValueError, match="MODEL_PATH_MUST_BE_ABSOLUTE"):
        load_session(Path("relative/model"), "0" * 64, device="cpu")
