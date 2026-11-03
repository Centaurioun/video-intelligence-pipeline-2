"""RED-first tests for the explicit local semantic retrieval seam.

These tests deliberately use tiny injected stubs.  They prove wiring and
provenance without loading model weights or making any provider/network call.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from persistent_local_index.model_space import (
    EMBEDDING_DIM,
    EMBEDDING_DTYPE,
    TEXT_PREPROCESSING_CONTRACT,
    SemanticSpace,
    build_generation_spec,
)
from vip_fvs import retrieval_adapter as adapter
from vip_fvs import semantic_index
from vip_fvs.local_semantic import CheckedLocalSemanticRuntime


def _real_space() -> SemanticSpace:
    """A completely explicit, test-only local model-space identity."""
    return SemanticSpace(
        model_identity="local-test-model",
        frozen_revision="test-revision",
        weights_sha256="1" * 64,
        processor_digest="2" * 64,
        image_preprocessing_digest="3" * 64,
        text_preprocessing_contract=TEXT_PREPROCESSING_CONTRACT,
        embedding_dim=EMBEDDING_DIM,
        dtype=EMBEDDING_DTYPE,
        normalization="l2",
    )


def test_local_runtime_uses_canonical_semantic_space_identity():
    """FVS runtime validation shares the stable seam's exact identity type."""
    space = _real_space()
    assert semantic_index.SemanticSpace is SemanticSpace
    assert isinstance(space, semantic_index.SemanticSpace)
    assert isinstance(
        CheckedLocalSemanticRuntime(_stub_image_embedder, _stub_text_embedder, space),
        CheckedLocalSemanticRuntime,
    )


def _stub_image_embedder(paths):
    values = list(paths)
    assert values
    return np.ones((len(values), EMBEDDING_DIM), dtype=np.float32)


def _stub_text_embedder(texts):
    values = list(texts)
    assert values
    return np.ones((len(values), EMBEDDING_DIM), dtype=np.float32)


def test_real_mode_requires_explicit_local_embedding_configuration(tmp_path):
    """No real invocation may silently become a fake-embedding invocation."""
    with pytest.raises(ValueError, match="EMBEDDERS_REQUIRED"):
        adapter.retrieve({"source_path": tmp_path / "source.mp4"}, "query", tmp_path / "index")

    with pytest.raises(ValueError, match="SEMANTIC_SPACE_REQUIRED"):
        adapter.retrieve(
            {"source_path": tmp_path / "source.mp4"},
            "query",
            tmp_path / "index",
            image_embedder=_stub_image_embedder,
            text_embedder=_stub_text_embedder,
        )


def test_real_mode_never_falls_back_to_fake_helpers(monkeypatch, tmp_path):
    """Explicit real seams are used even when the fake helpers are available."""
    calls = {"image": 0, "text": 0}

    def image(paths):
        calls["image"] += 1
        return _stub_image_embedder(paths)

    def text(texts):
        calls["text"] += 1
        return _stub_text_embedder(texts)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("fake embedding fallback was consulted")

    monkeypatch.setattr(adapter, "fake_image_embedder", forbidden)
    monkeypatch.setattr(adapter, "fake_text_embedder", forbidden)
    monkeypatch.setattr(adapter.PersistentLocalSemanticIndexEngine, "index_source", lambda *_args: None)
    monkeypatch.setattr(adapter.PersistentLocalSemanticIndexEngine, "query", lambda *_args, **_kwargs: {"query": ()})

    result = adapter.retrieve(
        {"source_path": tmp_path / "source.mp4"},
        "query",
        tmp_path / "index",
        image_embedder=image,
        text_embedder=text,
        semantic_space=_real_space(),
        fake_embedder=False,
    )

    assert result.fake_embedder_used is False
    assert calls == {"image": 0, "text": 0}


def test_explicit_real_configuration_cannot_be_overridden_by_fake_flag(monkeypatch, tmp_path):
    """A supplied real space must not be silently replaced by synthetic identity."""
    monkeypatch.setattr(adapter.PersistentLocalSemanticIndexEngine, "index_source", lambda *_args: None)
    monkeypatch.setattr(adapter.PersistentLocalSemanticIndexEngine, "query", lambda *_args, **_kwargs: {"query": ()})

    result = adapter.retrieve(
        {"source_path": tmp_path / "source.mp4"},
        "query",
        tmp_path / "index",
        image_embedder=_stub_image_embedder,
        text_embedder=_stub_text_embedder,
        semantic_space=_real_space(),
        fake_embedder=True,
    )

    assert result.fake_embedder_used is False
    assert result.space_id == build_generation_spec(_real_space()).space_id


def test_real_mode_propagates_semantic_space_and_invocation_ref(monkeypatch, tmp_path):
    space = _real_space()
    expected = build_generation_spec(space)
    observed = {}

    def index(_self, source, root, spec, image_embedder):
        observed["index"] = (Path(source), Path(root), spec, image_embedder)

    def query(_self, root, spec, texts, text_embedder, *, top_k):
        observed["query"] = (Path(root), spec, list(texts), text_embedder, top_k)
        return {texts[0]: ()}

    monkeypatch.setattr(adapter.PersistentLocalSemanticIndexEngine, "index_source", index)
    monkeypatch.setattr(adapter.PersistentLocalSemanticIndexEngine, "query", query)

    result = adapter.retrieve(
        {"source_path": tmp_path / "source.mp4"},
        "query",
        tmp_path / "index",
        top_k=3,
        image_embedder=_stub_image_embedder,
        text_embedder=_stub_text_embedder,
        semantic_space=space,
        invocation_ref="run-42/attempt-7",
    )

    assert observed["index"][2] == expected
    assert observed["query"][1] == expected
    assert observed["index"][2].space is space
    assert result.generation_id == expected.generation_id
    assert result.space_id == expected.space_id
    assert result.invocation_ref == "run-42/attempt-7"
    assert result.fake_embedder_used is False
