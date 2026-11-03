"""TDD Task 6: read-only exact query with deterministic ordering and no decode.

The query surface is the cheapest and most reused part of the system, so its
*non-actions* are asserted as strictly as its actions:

* it must never invoke FFmpeg / decode source video;
* it must never image-re-embed indexed media (no `image_embedder` dependency);
* it must never mutate index state;
* inactive/superseded rows must never win;
* ties must order deterministically without float timestamp comparison.
"""
from __future__ import annotations

import hashlib
import inspect
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

import persistent_local_index.search as search
from persistent_local_index.indexer import index_inputs, index_one_source
from persistent_local_index.media import sha256_file
from persistent_local_index.model_space import build_generation_spec
from persistent_local_index.search import (
    SampleMeta,
    SearchHit,
    exact_top_k,
    exact_top_k_indexed,
    query_generation,
)
from persistent_local_index.storage import (
    connect_db,
    open_or_create_generation,
    read_committed_counts,
)

from conftest import (  # noqa: E402
    deterministic_vector,
    make_image_embedder,
    make_spec,
    make_text_embedder,
    requires_ffmpeg,
    synth_video,
)

ROW_WIDTH = 768 * 4


# --- hand-built fixtures (no video needed) ---------------------------------


def _meta(row_id: int, *, active: bool = True, sha: str = "a" * 64,
          pts: int = 0, num: int = 1, den: int = 1000) -> SampleMeta:
    return SampleMeta(
        row_id=row_id,
        source_sha256=sha,
        source_path=f"/media/{sha[:4]}.mp4",
        pts=pts,
        timebase_num=num,
        timebase_den=den,
        timestamp_human=f"00:00:{pts * num / den:06.3f}",
        thumbnail_path=f"thumbs/{row_id}.jpg",
        active=active,
    )


def _matrix(*vectors) -> np.ndarray:
    return np.stack([np.asarray(v, dtype=np.float32) for v in vectors]).astype(np.float32)


def _axis(index: int, value: float = 1.0) -> np.ndarray:
    vector = np.zeros(768, dtype=np.float32)
    vector[index] = value
    return vector


# --- exact search ----------------------------------------------------------


def test_exact_top_k_returns_descending_scores():
    query = _axis(0)
    vectors = _matrix(_axis(0), _axis(0) * 0.5, _axis(1))
    metadata = {0: _meta(0), 1: _meta(1), 2: _meta(2)}
    hits = exact_top_k(vectors, query, metadata, 3)
    assert [h.rank for h in hits] == [1, 2, 3]
    assert hits[0].row_id == 0
    assert hits[0].score == pytest.approx(1.0)
    assert hits[0].score >= hits[1].score >= hits[2].score


def test_exact_top_k_respects_top_k_limit():
    vectors = _matrix(*[_axis(0, 1.0 - i * 0.01) for i in range(10)])
    metadata = {i: _meta(i) for i in range(10)}
    assert len(exact_top_k(vectors, _axis(0), metadata, 3)) == 3
    assert len(exact_top_k(vectors, _axis(0), metadata, 50)) == 10


@pytest.mark.parametrize("active_flags", [[True] * 6, [True, False, True, False, True, True]])
def test_indexed_top_k_matches_reference_with_full_and_mixed_activity(active_flags):
    # Includes ties at the cut, which require metadata-based tie ordering.
    vectors = _matrix(*[_axis(0) for _ in active_flags])
    metadata = {
        i: _meta(i, active=active_flags[i], sha=("a" if i % 2 else "b") * 64,
                 pts=i // 2)
        for i in range(len(active_flags))
    }
    active_mask = np.asarray(active_flags, dtype=bool)
    expected = exact_top_k(vectors, _axis(0), metadata, 3)
    fetched = []

    def fetch(row_ids):
        fetched.extend(row_ids)
        return {row: metadata[row] for row in row_ids}

    actual = exact_top_k_indexed(vectors, _axis(0), active_mask, fetch, 3)
    assert actual == expected
    assert len(fetched) >= len(actual)  # includes any rows tied at the Top-K boundary
    assert all(active_flags[row] for row in fetched)


def test_indexed_search_masks_inactive_exact_query_vector_and_expands_boundary_ties():
    # The inactive row exactly equals the query and outranks every active row.
    vectors = _matrix(_axis(0), _axis(0), _axis(0), _axis(0) * 0.25)
    metadata = {i: _meta(i, active=(i != 0), sha=("a" if i < 3 else "b") * 64)
                for i in range(4)}
    active = np.asarray([False, True, True, True])
    requested = []

    def fetch(rows):
        requested.append(tuple(rows))
        return {row: metadata[row] for row in rows}

    expected = exact_top_k(vectors, _axis(0), metadata, 1)
    actual = exact_top_k_indexed(vectors, _axis(0), active, fetch, 1)
    assert actual == expected
    assert actual[0].row_id == 1
    assert len(requested) == 1
    assert set(requested[0]) == {1, 2}  # row 2 ties the cutoff score
    assert 0 not in requested[0]


def test_indexed_search_fetch_is_top_k_bounded_without_boundary_ties():
    vectors = _matrix(*[_axis(0, 1.0 - i * 0.1) for i in range(8)])
    metadata = {i: _meta(i) for i in range(8)}
    fetched = []

    def fetch(rows):
        fetched.extend(rows)
        return {row: metadata[row] for row in rows}

    hits = exact_top_k_indexed(vectors, _axis(0), np.ones(8, dtype=bool), fetch, 2)
    assert [hit.row_id for hit in hits] == [0, 1]
    assert len(fetched) == 2


@pytest.mark.parametrize("top_k", [0, -1])
def test_indexed_search_rejects_invalid_top_k(top_k):
    with pytest.raises(ValueError, match="INVALID_TOP_K"):
        exact_top_k_indexed(_matrix(_axis(0)), _axis(0), np.ones(1, dtype=bool), {}, top_k)


def test_indexed_search_rejects_query_and_activity_shape_mismatch():
    vectors = _matrix(_axis(0))
    with pytest.raises(ValueError, match="QUERY_SHAPE"):
        exact_top_k_indexed(vectors, np.zeros(10), np.ones(1, dtype=bool), {}, 1)
    with pytest.raises(ValueError, match="ACTIVE_MASK_SHAPE"):
        exact_top_k_indexed(vectors, _axis(0), np.ones(2, dtype=bool), {}, 1)


def test_exact_top_k_masks_inactive_rows():
    query = _axis(0)
    # row 0 would win on score but is inactive
    vectors = _matrix(_axis(0), _axis(0) * 0.5)
    metadata = {0: _meta(0, active=False), 1: _meta(1)}
    hits = exact_top_k(vectors, query, metadata, 5)
    assert [h.row_id for h in hits] == [1]
    assert all(h.score > -np.inf for h in hits)


def test_unknown_or_inactive_rows_are_never_returned():
    vectors = _matrix(_axis(0))
    metadata = {99: _meta(99)}  # row_id 99 does not exist in the matrix
    hits = exact_top_k(vectors, _axis(0), metadata, 5)
    assert hits == ()


def test_ties_break_deterministically_by_source_then_pts_then_row():
    query = _axis(0)
    # All four rows have identical score 1.0.
    vectors = _matrix(_axis(0), _axis(0), _axis(0), _axis(0))
    metadata = {
        0: _meta(0, sha="b" * 64, pts=100),
        1: _meta(1, sha="a" * 64, pts=200),
        2: _meta(2, sha="a" * 64, pts=100),
        3: _meta(3, sha="a" * 64, pts=100),
    }
    first = exact_top_k(vectors, query, metadata, 4)
    assert [h.row_id for h in first] == [2, 3, 1, 0]
    for _ in range(5):
        assert [h.row_id for h in exact_top_k(vectors, query, metadata, 4)] == [2, 3, 1, 0]


def test_tie_order_uses_normalized_rational_pts_not_float_seconds():
    """1/3 s and 2/6 s are the same instant; ordering must be exact-rational."""
    query = _axis(0)
    vectors = _matrix(_axis(0), _axis(0), _axis(0))
    metadata = {
        0: _meta(0, sha="a" * 64, pts=2, num=1, den=6),   # 0.3333...
        1: _meta(1, sha="a" * 64, pts=1, num=1, den=3),   # 0.3333... (same instant)
        2: _meta(2, sha="a" * 64, pts=1, num=1, den=6),   # 0.1666... (earlier)
    }
    hits = exact_top_k(vectors, query, metadata, 11)
    # earlier instant first; the two equal instants then order by row_id
    assert [h.row_id for h in hits] == [2, 0, 1]


def test_pts_time_is_not_compared_as_float():
    """Guard against reintroducing float timestamp comparison for ordering."""
    source = inspect.getsource(search)
    assert "Fraction" in source, "rational PTS comparison must use exact arithmetic"


def test_exact_top_k_rejects_empty_matrix_and_bad_top_k():
    assert exact_top_k(np.zeros((0, 768), dtype=np.float32), _axis(0), {}, 5) == ()
    vectors = _matrix(_axis(0))
    with pytest.raises(ValueError, match="INVALID_TOP_K"):
        exact_top_k(vectors, _axis(0), {0: _meta(0)}, 0)


def test_exact_top_k_rejects_query_shape_mismatch():
    with pytest.raises(ValueError, match="QUERY_SHAPE"):
        exact_top_k(_matrix(_axis(0)), np.zeros(10, dtype=np.float32), {0: _meta(0)}, 1)


def test_hit_carries_full_provenance():
    vectors = _matrix(_axis(0))
    metadata = {0: _meta(0, sha="c" * 64, pts=1234)}
    hit = exact_top_k(vectors, _axis(0), metadata, 1)[0]
    assert isinstance(hit, SearchHit)
    assert hit.source_sha256 == "c" * 64
    assert hit.pts == 1234
    assert hit.timebase_den == 1000
    assert hit.thumbnail_path == "thumbs/0.jpg"
    assert hit.thumbnail_status == "PRESENT"
    assert hit.query != "" or hit.query == ""


# --- query surface non-actions --------------------------------------------


@requires_ffmpeg
def test_query_api_has_no_image_embedder_dependency():
    """Query must be structurally incapable of image re-embedding."""
    signature = inspect.signature(query_generation)
    parameters = set(signature.parameters)
    assert "text_embedder" in parameters
    assert not any("image" in name for name in parameters), (
        f"query surface exposes an image dependency: {sorted(parameters)}"
    )


@requires_ffmpeg
def test_query_never_invokes_ffmpeg_or_video_decode(monkeypatch, tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(media / "a.mp4", generation, spec, make_image_embedder())

    calls: list[object] = []
    real_run = subprocess.run

    def spy(cmd, *a, **k):
        calls.append(cmd)
        return real_run(cmd, *a, **k)

    monkeypatch.setattr(subprocess, "run", spy)
    hits = query_generation(
        index_root, spec, ["anything"], make_text_embedder(), top_k=3
    )
    assert hits
    flat = " ".join(
        " ".join(map(str, c)) if isinstance(c, (list, tuple)) else str(c) for c in calls
    )
    assert "ffmpeg" not in flat, "QUERY_DECODED_VIDEO"
    assert "ffprobe" not in flat, "QUERY_PROBED_VIDEO"
    assert "-show_frames" not in flat


@requires_ffmpeg
def test_query_does_not_mutate_index_state(tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(media / "a.mp4", generation, spec, make_image_embedder())

    vectors_before = generation.vectors.read_bytes()
    db_before = generation.database.read_bytes()
    thumbnails_before = sorted(p.name for p in generation.thumbs.iterdir())

    query_generation(index_root, spec, ["q1", "q2"], make_text_embedder(), top_k=3)

    assert generation.vectors.read_bytes() == vectors_before, "query rewrote vectors"
    assert generation.database.read_bytes() == db_before, "query rewrote the database"
    assert sorted(p.name for p in generation.thumbs.iterdir()) == thumbnails_before


@requires_ffmpeg
def test_query_rejects_semantic_space_mismatch_before_scoring(tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    index_one_source(
        media / "a.mp4", open_or_create_generation(index_root, spec), spec, make_image_embedder()
    )
    other = build_generation_spec(
        _space_with_other_processor()
    )
    called = []

    def exploding(texts):
        called.append(texts)
        raise AssertionError("text embedding must not run on a space mismatch")

    with pytest.raises(ValueError, match="processor_digest"):
        query_generation(index_root, other, ["q"], exploding, top_k=3)
    assert called == [], "space mismatch was detected only after embedding"


def _space_with_other_processor():
    from dataclasses import replace

    from conftest import make_semantic_space

    return replace(make_semantic_space(), processor_digest="different-processor")


@requires_ffmpeg
def test_missing_thumbnail_is_reported_without_source_decode(
    monkeypatch, tmp_path: Path
):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(media / "a.mp4", generation, spec, make_image_embedder())

    # delete every retained thumbnail: cache loss, not evidence loss
    for thumb in generation.thumbs.iterdir():
        thumb.unlink()

    calls: list[object] = []
    real_run = subprocess.run

    def spy(cmd, *a, **k):
        calls.append(cmd)
        return real_run(cmd, *a, **k)

    monkeypatch.setattr(subprocess, "run", spy)
    hits = query_generation(index_root, spec, ["q"], make_text_embedder(), top_k=3)["q"]
    assert hits
    assert all(hit.thumbnail_status == "MISSING" for hit in hits)
    flat = " ".join(
        " ".join(map(str, c)) if isinstance(c, (list, tuple)) else str(c) for c in calls
    )
    assert "ffmpeg" not in flat, "query decoded source to repair a missing thumbnail"


@requires_ffmpeg
def test_inactive_rows_cannot_win_after_supersession(tmp_path: Path):
    media = tmp_path / "media"
    path = synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    first = index_one_source(path, generation, spec, embedder)
    old_sha = first.source_sha256

    synth_video(path, colour="green", seconds=10.0)
    second = index_one_source(path, generation, spec, embedder)
    assert second.source_sha256 != old_sha

    # Query with the OLD digest's own embedding: it must not surface old rows.
    query = deterministic_vector(embedder.digests[0][0]).reshape(1, 768)
    results = query_generation(index_root, spec, ["q"], lambda texts: query, top_k=50)
    hits = results["q"]
    assert hits
    assert all(hit.source_sha256 != old_sha for hit in hits), "inactive rows won search"
    conn = connect_db(generation)
    old_active = conn.execute(
        "SELECT COUNT(*) FROM samples WHERE source_sha256=? AND active=1", (old_sha,)
    ).fetchone()[0]
    conn.close()
    assert old_active == 0


@requires_ffmpeg
def test_manifest_commit_count_larger_than_sqlite_fails_closed(tmp_path: Path):
    import json

    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(media / "a.mp4", generation, spec, make_image_embedder())

    raw = json.loads(generation.manifest.read_text(encoding="utf-8"))
    raw["committed_rows"] = raw["committed_rows"] + 5
    generation.manifest.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="MANIFEST_COMMITTED_ROWS_AHEAD_OF_SQLITE"):
        query_generation(index_root, spec, ["q"], make_text_embedder(), top_k=3)


@requires_ffmpeg
def test_stale_lower_manifest_mirror_is_tolerated_read_only(tmp_path: Path):
    import json

    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    result = index_one_source(media / "a.mp4", generation, spec, make_image_embedder())

    raw = json.loads(generation.manifest.read_text(encoding="utf-8"))
    raw["committed_rows"] = 0
    generation.manifest.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    manifest_bytes = generation.manifest.read_bytes()

    hits = query_generation(index_root, spec, ["q"], make_text_embedder(), top_k=5)["q"]
    assert hits, "stale-lower mirror must still serve the SQLite-committed prefix"
    assert generation.manifest.read_bytes() == manifest_bytes, (
        "read-only query repaired the manifest mirror"
    )


@requires_ffmpeg
def test_vector_file_shorter_than_committed_fails_closed(tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(media / "a.mp4", generation, spec, make_image_embedder())
    with generation.vectors.open("r+b") as fh:
        fh.truncate(ROW_WIDTH // 2)
    with pytest.raises(ValueError, match="VECTOR_FILE_SHORTER_THAN_COMMITTED"):
        query_generation(index_root, spec, ["q"], make_text_embedder(), top_k=3)


@requires_ffmpeg
def test_multiple_queries_share_one_embedding_batch(tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(media / "a.mp4", generation, spec, make_image_embedder())

    batches: list[list[str]] = []

    def recorder(texts):
        batches.append(list(texts))
        return np.stack([deterministic_vector(t) for t in texts]).astype(np.float32)

    results = query_generation(index_root, spec, ["one", "two", "three"], recorder, top_k=2)
    assert set(results) == {"one", "two", "three"}
    assert len(batches) == 1, "queries must be embedded in one process-wide batch"


@requires_ffmpeg
def test_query_returns_provenance_for_every_hit(tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    index_root = tmp_path / "idx"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    result = index_one_source(media / "a.mp4", generation, spec, make_image_embedder())

    hits = query_generation(index_root, spec, ["q"], make_text_embedder(), top_k=3)[ "q"]
    assert len(hits) == min(3, result.row_end)
    for hit in hits:
        assert hit.source_sha256 == result.source_sha256
        assert hit.timebase_num > 0 and hit.timebase_den > 0
        assert isinstance(hit.pts, int)
        assert hit.timestamp_human
        assert hit.rank >= 1
