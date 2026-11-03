from pathlib import Path
from types import SimpleNamespace

import numpy as np

from vip_fvs import retrieval_adapter as adapter


def test_fake_embeddings_are_stable_normalized_and_model_free():
    first = adapter.fake_text_embedder(["target phrase"])
    second = adapter.fake_text_embedder(["target phrase"])
    assert first.dtype == np.float32
    assert first.shape == (1, 768)
    np.testing.assert_array_equal(first, second)
    np.testing.assert_allclose(np.linalg.norm(first, axis=1), [1.0], atol=1e-6)


def test_retrieve_preserves_raw_hit_fields_and_provenance(monkeypatch, tmp_path):
    hit = adapter.SearchHit(
        query="target phrase", rank=0, score=0.875, row_id=7,
        source_path="/tmp/synthetic.mp4", source_sha256="a" * 64,
        pts=123, timebase_num=1, timebase_den=90000,
        timestamp_human="00:00:01.366", thumbnail_path="thumbs/7.jpg",
        thumbnail_status="PRESENT",
    )
    calls = {}

    def fake_index(self, path, root, spec, image_embedder):
        calls["index"] = (Path(path), Path(root), spec, image_embedder)
        assert image_embedder([Path("frame.jpg")]).shape == (1, 768)

    def fake_query(self, root, spec, texts, text_embedder, *, top_k):
        calls["query"] = (Path(root), spec, list(texts), text_embedder, top_k)
        assert text_embedder([texts[0]]).shape == (1, 768)
        return {texts[0]: (hit,)}

    monkeypatch.setattr(adapter.PersistentLocalSemanticIndexEngine, "index_source", fake_index)
    monkeypatch.setattr(adapter.PersistentLocalSemanticIndexEngine, "query", fake_query)

    result = adapter.retrieve(
        {"source_path": tmp_path / "synthetic.mp4", "source_sha256": "a" * 64},
        "target phrase", tmp_path / "index", fake_embedder=True,
        invocation_ref="run-1/attempt-1",
    )

    assert result.fake_embedder_used is True
    assert result.invocation_ref == "run-1/attempt-1"
    assert result.hits == (hit,)
    preserved_hit = result.hits[0]
    assert (
        preserved_hit.query,
        preserved_hit.rank,
        preserved_hit.score,
        preserved_hit.source_path,
        preserved_hit.source_sha256,
        preserved_hit.pts,
        preserved_hit.timebase_num,
        preserved_hit.timebase_den,
        preserved_hit.timestamp_human,
        preserved_hit.thumbnail_path,
        preserved_hit.thumbnail_status,
    ) == (
        "target phrase",
        0,
        0.875,
        "/tmp/synthetic.mp4",
        "a" * 64,
        123,
        1,
        90000,
        "00:00:01.366",
        "thumbs/7.jpg",
        "PRESENT",
    )
    assert result.generation_id == calls["index"][2].generation_id
    assert result.space_id == calls["index"][2].space_id
    assert calls["query"][4] == 5


def test_retrieve_delegates_index_and_query_to_injected_stable_engine(tmp_path):
    hit = adapter.SearchHit(
        query="target phrase", rank=0, score=0.875, row_id=7,
        source_path="/tmp/synthetic.mp4", source_sha256="a" * 64,
        pts=123, timebase_num=1, timebase_den=90000,
        timestamp_human="00:00:01.366", thumbnail_path="thumbs/7.jpg",
        thumbnail_status="PRESENT",
    )
    calls = []

    class Engine:
        def build_generation_spec(self, space):
            calls.append(("build", space))
            return SimpleNamespace(generation_id="generation-1", space_id="space-1")

        def index_source(self, input_path, index_root, spec, image_embedder):
            calls.append(("index", Path(input_path), Path(index_root), spec, image_embedder))
            return object()

        def query(self, index_root, spec, texts, text_embedder, *, top_k):
            calls.append(("query", Path(index_root), spec, tuple(texts), text_embedder, top_k))
            return {text: (hit,) for text in texts}

    result = adapter.retrieve(
        {"source_path": tmp_path / "synthetic.mp4", "source_sha256": "a" * 64},
        ["target phrase", "second phrase"], tmp_path / "index",
        fake_embedder=True, invocation_ref="run-1/attempt-1", engine=Engine(),
    )

    assert [call[0] for call in calls] == ["build", "index", "query"]
    assert calls[0][1] == adapter.fake_semantic_space()
    assert calls[1][1:3] == (tmp_path / "synthetic.mp4", tmp_path / "index")
    assert calls[2][3] == ("target phrase", "second phrase")
    assert calls[2][5] == 5
    assert result.hits == (hit, hit)
    assert result.invocation_ref == "run-1/attempt-1"
    assert result.fake_embedder_used is True


def test_real_mode_requires_explicit_seams():
    try:
        adapter.retrieve({"source_path": "source.mp4"}, "q", Path("index"))
    except ValueError as exc:
        assert str(exc) == "EMBEDDERS_REQUIRED"
    else:  # pragma: no cover
        raise AssertionError("real mode must not silently load a model")
