"""RED-first contract tests for the frozen, local-only model bundle.

These tests intentionally define the seam for the local semantic-model loader;
they do not download weights, instantiate a real transformer, or touch media.
The loader must validate identity and all required assets before delegating to
the model runtime.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from persistent_local_index import local_model


def _bundle(root: Path, *, revision: str = "rev-local-1", weights: bytes = b"weights") -> tuple[Path, str]:
    root.mkdir(parents=True)
    for name in (
        "config.json",
        "preprocessor_config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "spiece.model",
    ):
        (root / name).write_bytes(("asset:" + name).encode())
    (root / "revision.txt").write_text(revision, encoding="utf-8")
    (root / "model.safetensors").write_bytes(weights)
    return root, hashlib.sha256(weights).hexdigest()


def _stub_runtime(monkeypatch):
    """Keep contract tests offline while exposing the loader boundary."""
    calls = []

    def load(*args, **kwargs):
        calls.append((args, kwargs))
        return object()

    monkeypatch.setattr(local_model, "_load_runtime", load)
    return calls


def test_loader_requires_absolute_model_root(tmp_path: Path):
    with pytest.raises(ValueError, match="MODEL_ROOT_MUST_BE_ABSOLUTE"):
        local_model.load_local_model(
            Path("relative/model"), expected_weights_sha256="0" * 64,
            expected_revision="rev-local-1", device="cpu", offline=True,
        )


def test_loader_validates_digest_and_revision_before_runtime(monkeypatch, tmp_path: Path):
    root, digest = _bundle(tmp_path / "model")
    calls = _stub_runtime(monkeypatch)

    with pytest.raises(ValueError, match="MODEL_WEIGHTS_DIGEST_MISMATCH"):
        local_model.load_local_model(
            root, expected_weights_sha256="0" * 64,
            expected_revision="rev-local-1", device="cpu", offline=True,
        )
    assert calls == []

    with pytest.raises(ValueError, match="MODEL_REVISION_MISMATCH"):
        local_model.load_local_model(
            root, expected_weights_sha256=digest,
            expected_revision="different-revision", device="cpu", offline=True,
        )
    assert calls == []


def test_loader_requires_complete_processor_assets(monkeypatch, tmp_path: Path):
    root, digest = _bundle(tmp_path / "model")
    (root / "tokenizer.json").unlink()
    calls = _stub_runtime(monkeypatch)

    with pytest.raises(ValueError, match="PROCESSOR_ASSET_MISSING:tokenizer.json"):
        local_model.load_local_model(
            root, expected_weights_sha256=digest,
            expected_revision="rev-local-1", device="cpu", offline=True,
        )
    assert calls == []


def test_loader_exposes_processor_asset_digest_and_identity(monkeypatch, tmp_path: Path):
    root, digest = _bundle(tmp_path / "model")
    calls = _stub_runtime(monkeypatch)
    loaded = local_model.load_local_model(
        root, expected_weights_sha256=digest,
        expected_revision="rev-local-1", device="cpu", offline=True,
    )
    assert loaded.model_root == root.resolve()
    assert loaded.frozen_revision == "rev-local-1"
    assert loaded.weights_sha256 == digest
    assert len(loaded.processor_digest) == 64
    assert calls and calls[0][1].get("local_files_only") is True


def test_revalidate_rejects_mutated_weights_or_processor_assets(monkeypatch, tmp_path: Path):
    root, digest = _bundle(tmp_path / "model")
    _stub_runtime(monkeypatch)
    loaded = local_model.load_local_model(
        root, expected_weights_sha256=digest,
        expected_revision="rev-local-1", device="cpu", offline=True,
    )

    (root / "model.safetensors").write_bytes(b"changed")
    with pytest.raises(ValueError, match="MODEL_REVALIDATION_FAILED"):
        local_model.revalidate_local_model(loaded)


def test_requested_mps_never_falls_back_to_cpu(monkeypatch, tmp_path: Path):
    root, digest = _bundle(tmp_path / "model")
    calls = _stub_runtime(monkeypatch)
    monkeypatch.setattr(local_model, "_mps_available", lambda: False)

    with pytest.raises(RuntimeError, match="MPS_REQUESTED_BUT_UNAVAILABLE"):
        local_model.load_local_model(
            root, expected_weights_sha256=digest,
            expected_revision="rev-local-1", device="mps", offline=True,
        )
    assert calls == []


def test_offline_mode_is_explicit_and_forbids_network_fallback(monkeypatch, tmp_path: Path):
    root, digest = _bundle(tmp_path / "model")
    calls = _stub_runtime(monkeypatch)
    with pytest.raises(ValueError, match="OFFLINE_REQUIRED"):
        local_model.load_local_model(
            root, expected_weights_sha256=digest,
            expected_revision="rev-local-1", device="cpu", offline=False,
        )
    assert calls == []


def test_missing_weights_fails_closed_before_runtime(monkeypatch, tmp_path: Path):
    root, _ = _bundle(tmp_path / "model")
    (root / "model.safetensors").unlink()
    calls = _stub_runtime(monkeypatch)
    with pytest.raises(ValueError, match="MODEL_WEIGHTS_NOT_FOUND"):
        local_model.load_local_model(
            root, expected_weights_sha256="0" * 64,
            expected_revision="rev-local-1", device="cpu", offline=True,
        )
    assert calls == []
