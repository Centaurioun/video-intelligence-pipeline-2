"""Contract tests for manifest-bound, read-only multi-source retrieval."""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Sequence

import numpy as np
import pytest

from vip_fvs.semantic_index import GenerationSpec, IndexSummary, SearchHit, SemanticSpace
from vip_fvs.source_adapter import MultiSourceManifest, SourceManifestEntry


def _space() -> SemanticSpace:
    return SemanticSpace(
        model_identity="fixture-model", frozen_revision="fixture-r1",
        weights_sha256="1" * 64, processor_digest="2" * 64,
        image_preprocessing_digest="3" * 64,
        text_preprocessing_contract="padding=max_length", embedding_dim=2,
        dtype="float32", normalization="l2",
    )


class QueryEngine:
    """Deterministic index seam fixture; query can return controlled hits."""

    def __init__(self, hits: Sequence[SearchHit] | None = None) -> None:
        from persistent_local_index.model_space import build_generation_spec

        self.spec = build_generation_spec(_space())
        self.hits = tuple(hits or ())
        self.index_calls: list[tuple] = []
        self.query_calls: list[tuple] = []

    def build_generation_spec(self, space: SemanticSpace) -> GenerationSpec:
        assert space == _space()
        return self.spec

    def index_source(self, input_path: Path, index_root: Path, spec: GenerationSpec, image_embedder):
        self.index_calls.append((input_path, index_root, spec, image_embedder))
        return IndexSummary(self.spec.generation_id, 1, 0, 0, 0, ())

    def query(self, index_root: Path, spec: GenerationSpec, texts, text_embedder, *, top_k: int):
        self.query_calls.append((Path(index_root), spec, tuple(texts), text_embedder, top_k))
        return {text: tuple(dataclasses.replace(hit, query=text) for hit in self.hits[:top_k])
                for text in texts}


def _runtime():
    from vip_fvs.local_semantic import checked_runtime

    image_calls: list[tuple[Path, ...]] = []

    def image_embedder(paths: Sequence[Path]) -> np.ndarray:
        image_calls.append(tuple(paths))
        return np.ones((len(paths), 2), dtype=np.float32)

    def text_embedder(texts: Sequence[str]) -> np.ndarray:
        return np.ones((len(texts), 2), dtype=np.float32)

    runtime = checked_runtime(image_embedder=image_embedder, text_embedder=text_embedder,
                              semantic_space=_space(), fake=True,
                              runtime_identity="fixture-runtime")
    return runtime, image_calls


def _entry(path: Path, *, revision: str = "revision-a", content: str = "content-a",
           digest: str = "a" * 64) -> SourceManifestEntry:
    return SourceManifestEntry(
        revision_id=revision, content_id=content, source_path=path,
        source_sha256=digest, selected_stream_index=0,
        selection_source="explicit", inventory_digest="b" * 64,
        policy_decision_ref="policy-fixture", custody_state="synthetic",
    )


def _manifest(*entries: SourceManifestEntry) -> MultiSourceManifest:
    return MultiSourceManifest(tuple(sorted(entries, key=lambda e: (e.revision_id.encode(), str(e.source_path).encode()))), "c" * 64)


def _hit(path: Path, digest: str = "a" * 64, *, rank: int = 1, score: float = .875) -> SearchHit:
    return SearchHit(
        query="harbor", rank=rank, score=score, row_id=rank,
        source_path=str(path), source_sha256=digest, pts=9000 + rank,
        timebase_num=1, timebase_den=90000,
        timestamp_human="00:00:00.100", thumbnail_path=None,
        thumbnail_status="MISSING",
    )


def _retrieve(manifest, engine, runtime=None, **kwargs):
    from vip_fvs.multi_source_retrieval import retrieve_multi_source

    runtime = runtime or _runtime()[0]
    return retrieve_multi_source(
        Path("synthetic-index"), manifest, "harbor", runtime=runtime,
        semantic_space=runtime.semantic_space, engine=engine, top_k=5, **kwargs,
    )


def test_multi_source_query_returns_ranked_candidates_bound_to_exact_manifest_revision_and_digest():
    path_a, path_b = Path("/fixture/a.mp4"), Path("/fixture/b.mp4")
    entries = (_entry(path_a), _entry(path_b, revision="revision-b", content="content-b", digest="d" * 64))
    engine = QueryEngine((_hit(path_a, rank=1, score=.9), _hit(path_b, "d" * 64, rank=2, score=.7)))

    result = _retrieve(_manifest(*entries), engine)

    candidates = result.candidates
    assert [candidate.rank for candidate in candidates] == [1, 2]
    assert [(candidate.revision_id, candidate.content_id, candidate.source_sha256) for candidate in candidates] == [
        ("revision-a", "content-a", "a" * 64), ("revision-b", "content-b", "d" * 64),
    ]
    assert [candidate.source_path for candidate in candidates] == [str(path_a), str(path_b)]
    assert [candidate.score for candidate in candidates] == [.9, .7]


@pytest.mark.parametrize("hit", [
    _hit(Path("/outside/not-in-manifest.mp4")),
    _hit(Path("/fixture/a.mp4"), "e" * 64),
])
def test_hit_outside_manifest_or_path_digest_mismatch_refuses(hit: SearchHit):
    manifest = _manifest(_entry(Path("/fixture/a.mp4")))

    with pytest.raises((ValueError, RuntimeError), match="(?i)(manifest|provenance|locator|digest|binding)"):
        _retrieve(manifest, QueryEngine((hit,)))


@pytest.mark.parametrize("score", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_hit_score_is_rejected(score: float):
    path = Path("/fixture/a.mp4")
    with pytest.raises(ValueError, match="MULTI_SOURCE_HIT_SCORE_INVALID"):
        _retrieve(_manifest(_entry(path)), QueryEngine((_hit(path, score=score),)))


def test_duplicate_digest_at_two_paths_resolves_by_exact_locator_without_collapsing_occurrence_identity():
    path_a, path_b = Path("/fixture/occurrence-a.mp4"), Path("/fixture/occurrence-b.mp4")
    digest = "f" * 64
    manifest = _manifest(
        _entry(path_a, revision="revision-a", content="same-content", digest=digest),
        _entry(path_b, revision="revision-b", content="same-content", digest=digest),
    )
    engine = QueryEngine((_hit(path_b, digest, rank=1), _hit(path_a, digest, rank=2)))

    result = _retrieve(manifest, engine)

    assert [(c.revision_id, c.source_path) for c in result.candidates] == [
        ("revision-b", str(path_b)), ("revision-a", str(path_a)),
    ]
    assert result.candidates[0].content_id == result.candidates[1].content_id


def test_candidates_are_matched_nonbinding_and_preserve_pts_timebase_as_locator_only():
    path = Path("/fixture/a.mp4")
    candidate = _retrieve(_manifest(_entry(path)), QueryEngine((_hit(path),))).candidates[0]

    assert candidate.evidence_class == "MATCHED"
    assert candidate.binding_eligible is False
    assert candidate.source_sample_pts == 9001
    assert candidate.source_timebase_num == 1 and candidate.source_timebase_den == 90000
    assert not hasattr(candidate, "source_pts_interval")
    assert not hasattr(candidate, "frame_accurate_boundary")
    assert not hasattr(candidate, "editorial_decision")


def test_query_multi_is_read_only_and_never_indexes_decodes_probes_image_embeds_refines_or_renders(monkeypatch):
    path = Path("/fixture/a.mp4")
    engine = QueryEngine((_hit(path),))
    runtime, image_calls = _runtime()
    forbidden = ("index_local_source", "decode", "probe", "refine", "render")

    _retrieve(_manifest(_entry(path)), engine, runtime)

    assert engine.index_calls == []
    assert len(engine.query_calls) == 1
    assert image_calls == []
    assert engine.query_calls[0][3] is runtime.text_embedder
    assert all(not hasattr(engine, name) for name in forbidden)


def test_query_multi_cli_requires_manifest_not_source_path_and_emits_deterministic_json(monkeypatch, capsys, tmp_path: Path):
    import vip_fvs.cli as cli
    import vip_fvs.multi_source_retrieval as multi_source_retrieval
    import vip_fvs.source_adapter as source_adapter

    parser = cli._parser()
    args = parser.parse_args(["query-multi", "--manifest", "manifest.json", "--query", "harbor",
                              "--index-root", "index", "--fake-embedder"])
    assert args.command == "query-multi"
    assert args.manifest == "manifest.json"
    assert not hasattr(args, "source")

    candidate = {
        "query": "harbor", "rank": 1, "score": .875, "revision_id": "revision-a",
        "content_id": "content-a", "source_path": "/fixture/a.mp4", "source_sha256": "a" * 64,
        "generation_id": "generation-fixture", "space_id": "space-fixture",
        "source_sample_pts": 9001, "source_timebase_num": 1, "source_timebase_den": 90000,
        "timestamp_human": "00:00:00.100", "thumbnail_path": None,
        "thumbnail_status": "MISSING", "evidence_class": "MATCHED", "binding_eligible": False,
    }
    runtime = _runtime()[0]
    candidate_type = dataclasses.make_dataclass("FixtureCandidate", [(key, object) for key in candidate])
    result_type = dataclasses.make_dataclass(
        "FixtureResult", [("manifest_digest", str), ("generation_id", str),
                          ("space_id", str), ("candidates", tuple)], frozen=True,
    )
    monkeypatch.setattr(cli, "_product_runtime", lambda args, *, index_operation: (runtime, None))
    monkeypatch.setattr(source_adapter, "load_multi_source_manifest",
                        lambda path: _manifest(_entry(Path("/fixture/a.mp4"))))
    monkeypatch.setattr(multi_source_retrieval, "retrieve_multi_source", lambda *a, **k: result_type(
        "c" * 64, "generation-fixture", "space-fixture", (candidate_type(**candidate),),
    ))

    assert cli.main(["query-multi", "--manifest", str(tmp_path / "manifest.json"), "--query", "harbor",
                     "--index-root", "index", "--fake-embedder"]) == 0
    first = capsys.readouterr().out
    assert cli.main(["query-multi", "--manifest", str(tmp_path / "manifest.json"), "--query", "harbor",
                     "--index-root", "index", "--fake-embedder"]) == 0
    second = capsys.readouterr().out
    assert json.loads(first)["candidates"] == [candidate]
    assert first == second
    with pytest.raises(SystemExit):
        parser.parse_args(["query-multi", "--source", "source.mp4", "--query", "harbor", "--index-root", "index"])


def test_repeated_queries_preserve_generation_space_identity_and_do_not_mutate_index():
    path = Path("/fixture/a.mp4")
    engine = QueryEngine((_hit(path),))
    root = Path("synthetic-index")
    before = sorted(str(p) for p in root.rglob("*")) if root.exists() else []

    first = _retrieve(_manifest(_entry(path)), engine)
    second = _retrieve(_manifest(_entry(path)), engine)

    assert first == second
    assert first.generation_id == second.generation_id == engine.spec.generation_id
    assert first.space_id == second.space_id == engine.spec.space_id
    assert engine.index_calls == []
    assert len(engine.query_calls) == 2
    after = sorted(str(p) for p in root.rglob("*")) if root.exists() else []
    assert after == before
