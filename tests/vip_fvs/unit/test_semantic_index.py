import ast
from pathlib import Path

import pytest

from vip_fvs import semantic_index
from persistent_local_index.model_space import SemanticSpace


def _space() -> SemanticSpace:
    return SemanticSpace(
        model_identity="test", frozen_revision="r1", weights_sha256="a" * 64,
        processor_digest="b" * 64, image_preprocessing_digest="c" * 64,
        text_preprocessing_contract="padding=max_length", embedding_dim=768,
        dtype="float32", normalization="l2",
    )


def test_protocol_and_adapter_delegate_without_loading_models(monkeypatch):
    spec = object()
    summary = object()
    result = {"q": ()}
    calls = []

    def build(space):
        calls.append(("build", space))
        return spec

    def index(path, root, got_spec, embedder):
        calls.append(("index", path, root, got_spec, embedder))
        return summary

    def query(root, got_spec, texts, embedder, *, top_k):
        calls.append(("query", root, got_spec, texts, embedder, top_k))
        return result

    monkeypatch.setattr(semantic_index.model_space, "build_generation_spec", build)
    monkeypatch.setattr(semantic_index.indexer, "index_inputs", index)
    monkeypatch.setattr(semantic_index.search, "query_generation", query)
    engine = semantic_index.PersistentLocalSemanticIndexEngine()
    image_embedder = object()
    text_embedder = object()

    assert engine.build_generation_spec(_space()) is spec
    assert engine.index_source("input", "root", spec, image_embedder) is summary
    assert engine.query("root", spec, ["q"], text_embedder, top_k=3) is result
    assert [call[0] for call in calls] == ["build", "index", "query"]
    assert calls[1][1:] == ("input", "root", spec, image_embedder)
    assert calls[2][1:] == ("root", spec, ["q"], text_embedder, 3)
    assert semantic_index.SemanticSpace is SemanticSpace


def test_protocol_declares_stable_operations():
    assert hasattr(semantic_index.SemanticIndexEngine, "build_generation_spec")
    assert hasattr(semantic_index.SemanticIndexEngine, "index_source")
    assert hasattr(semantic_index.SemanticIndexEngine, "query")
    assert isinstance(semantic_index.PersistentLocalSemanticIndexEngine(), semantic_index.SemanticIndexEngine)


@pytest.mark.parametrize("module", ["retrieval_adapter.py", "local_semantic.py"])
def test_product_callers_do_not_import_engine_modules_directly(module):
    source = Path(__file__).parents[3] / "src" / "vip_fvs" / module
    tree = ast.parse(source.read_text(encoding="utf-8"))
    forbidden = {"persistent_local_index.indexer", "persistent_local_index.search", "persistent_local_index.model_space"}
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in forbidden:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names if alias.name in forbidden)
    assert imports == []
