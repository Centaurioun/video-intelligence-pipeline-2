"""Frozen output semantics and bounded-materialization regressions.

Authority: Attempt 4 bounded exact-search metadata/result materialization
optimization (evidence ledger section 10).  This module freezes the *current*
exact-search behaviour while the query path stops materializing one SampleMeta
and one SearchHit per committed row.

Two independent classes of evidence:

1. EQUIVALENCE — the optimized indexed path must return exactly what the frozen
   reference behaviour returned (row ids, ordering, scores, provenance,
   thumbnail status).  The reference oracle is the pre-existing ``exact_top_k``
   contract, which stays exported and unchanged.
2. BOUNDED MATERIALIZATION — the optimized query path must not construct
   metadata or SearchHit objects for rows it will discard.  These assertions are
   structural (call counts) and are measured against an index with far more
   committed rows than returned hits, so "bounded by results" and "bounded by
   committed rows" are distinguishable.  No timing assertion is used.

Everything here is hermetic: no video file, no ffmpeg, no model.  Samples are
written through the real storage contract with deterministic vectors.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import persistent_local_index.search as search
from persistent_local_index.search import (
    SearchHit,
    exact_top_k,
    exact_top_k_indexed,
    fetch_sample_metadata,
    load_active_row_mask,
    open_generation_for_query,
    query_generation,
)
from persistent_local_index.storage import (
    PersistedSample,
    append_source_segment,
    connect_db,
    open_or_create_generation,
)

from conftest import deterministic_vector, make_spec  # noqa: E402

COMMITTED_ROWS = 80
ROW_WIDTH = 768 * 4
TOP_K = 5


# --------------------------------------------------------------------------
# hand-built fixtures (no video, no ffmpeg, no model)
# --------------------------------------------------------------------------


def _axis(index: int, value: float = 1.0) -> np.ndarray:
    vector = np.zeros(768, dtype=np.float32)
    vector[index] = value
    return vector


def _matrix(*vectors) -> np.ndarray:
    return np.stack([np.asarray(v, dtype=np.float32) for v in vectors]).astype(np.float32)


def _metadata(*specs) -> dict[int, search.SampleMeta]:
    """Specs are ``(row_id, active, sha, pts, num, den, thumb_present)``."""
    out: dict[int, search.SampleMeta] = {}
    for row_id, active, sha, pts, num, den, thumb in specs:
        out[row_id] = search.SampleMeta(
            row_id=row_id,
            source_sha256=sha,
            source_path=f"/media/{sha[:4]}.mp4",
            pts=pts,
            timebase_num=num,
            timebase_den=den,
            timestamp_human=f"00:00:{pts * num / den:06.3f}",
            thumbnail_path=f"thumbs/{row_id}.jpg" if thumb else None,
            active=active,
            thumbnail_status=search.THUMBNAIL_PRESENT if thumb else search.THUMBNAIL_MISSING,
        )
    return out


def _mask(metadata: dict[int, search.SampleMeta]) -> np.ndarray:
    active = np.zeros(len(metadata), dtype=bool)
    for row_id, meta in metadata.items():
        active[row_id] = bool(meta.active)
    return active


def _fetch_from(metadata: dict[int, search.SampleMeta]):
    return lambda row_ids: {row_id: metadata[row_id] for row_id in row_ids}


def _assert_same_hits(indexed, reference) -> None:
    assert len(indexed) == len(reference)
    for left, right in zip(indexed, reference):
        assert left.rank == right.rank
        assert left.row_id == right.row_id
        assert left.score == right.score
        assert left.source_sha256 == right.source_sha256
        assert left.source_path == right.source_path
        assert left.pts == right.pts
        assert left.timebase_num == right.timebase_num
        assert left.timebase_den == right.timebase_den
        assert left.timestamp_human == right.timestamp_human
        assert left.thumbnail_path == right.thumbnail_path
        assert left.thumbnail_status == right.thumbnail_status


def _synthetic_index(
    tmp_path: Path,
    rows: int = COMMITTED_ROWS,
    *,
    active_from: int | None = None,
    embedding_dim: int = 768,
):
    """Write a real generation through the storage contract. No media involved.

    ``active_from`` (if given) marks every row at or above it inactive, writing
    exactly the same ``samples.active`` state the supersession lifecycle writes.
    """
    index_root = tmp_path / "idx"
    spec = make_spec(
        embedding_dim=embedding_dim,
        model_identity=(
            "google/siglip-base-patch16-224"
            if embedding_dim == 768
            else "synthetic/so400m"
        ),
    )
    generation = open_or_create_generation(index_root, spec)
    sha = "a" * 64
    samples = [
        PersistedSample(
            pts=row_id * 2700,
            timebase_num=1,
            timebase_den=600,
            pts_time=row_id * 4.5,
            timestamp_human=f"00:00:{row_id * 4.5:06.3f}",
            thumbnail_stage_path=tmp_path / f"stage-{row_id}.jpg",
        )
        for row_id in range(rows)
    ]
    vectors = np.stack(
        [
            _deterministic_vector(f"synthetic-row-{row_id}", embedding_dim)
            for row_id in range(rows)
        ]
    ).astype(np.float32)
    conn = connect_db(generation)
    try:
        append_source_segment(
            generation,
            conn,
            source_sha256=sha,
            source_metadata={
                "source_revision": None,
                "size_bytes": 1234,
                "stream_index": 0,
                "codec": "synthetic",
                "width": 64,
                "height": 48,
                "timebase_num": 1,
                "timebase_den": 600,
                "duration_seconds": rows * 4.5,
            },
            samples=samples,
            normalized_vectors=vectors,
            expected_dim=embedding_dim,
            stream_index=0,
        )
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO source_locations (path, source_sha256,"
                " last_observed_size, last_observed_mtime_ns, last_observed_at)"
                " VALUES (?,?,?,?,?)",
                ("/synthetic-fixture/source-000000.mp4", sha, 1234, 0, "2026-09-15T00:00:00+00:00"),
            )
            if active_from is not None:
                conn.execute(
                    "UPDATE samples SET active=0 WHERE row_id >= ?", (active_from,)
                )
    finally:
        conn.close()
    return index_root, spec, generation


def _deterministic_vector(seed: str, dimensions: int) -> np.ndarray:
    """Stable model-free unit vector with a profile-selected test width."""
    import hashlib

    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    vector = rng.standard_normal(dimensions).astype(np.float32)
    return (vector / np.linalg.norm(vector)).astype(np.float32)


@pytest.mark.parametrize("embedding_dim", [768, 1152])
def test_query_uses_profile_dimension_for_deterministic_exact_top_k(
    tmp_path: Path, embedding_dim: int
):
    index_root, spec, generation = _synthetic_index(
        tmp_path, rows=3, embedding_dim=embedding_dim
    )
    vectors = np.stack(
        [
            _deterministic_vector(f"synthetic-row-{row_id}", embedding_dim)
            for row_id in range(3)
        ]
    )
    query = _deterministic_vector("synthetic-row-1", embedding_dim)
    embedded = []

    def text_embedder(texts):
        embedded.extend(texts)
        return query.reshape(1, embedding_dim)

    actual = query_generation(
        index_root, spec, ["synthetic query"], text_embedder, top_k=3
    )["synthetic query"]
    metadata = {
        row_id: search.SampleMeta(
            row_id=row_id,
            source_sha256="a" * 64,
            source_path="/synthetic-fixture/source-000000.mp4",
            pts=row_id * 2700,
            timebase_num=1,
            timebase_den=600,
            timestamp_human=f"00:00:{row_id * 4.5:06.3f}",
            thumbnail_path=f"thumbs/{row_id}.jpg",
            active=True,
        )
        for row_id in range(3)
    }
    expected = exact_top_k(vectors, query, metadata, 3)

    assert embedded == ["synthetic query"]
    assert generation.vectors.stat().st_size == 3 * embedding_dim * 4
    assert [hit.row_id for hit in actual] == [hit.row_id for hit in expected]
    assert [hit.score for hit in actual] == [hit.score for hit in expected]


def test_query_rejects_text_vector_width_mismatch_before_scoring(
    tmp_path: Path
):
    index_root, spec, _ = _synthetic_index(
        tmp_path, rows=2, embedding_dim=1152
    )
    with pytest.raises(ValueError, match="QUERY_DIMENSION_MISMATCH:768!=1152"):
        query_generation(
            index_root,
            spec,
            ["wrong width"],
            lambda texts: np.zeros((len(texts), 768), dtype=np.float32),
            top_k=1,
        )


def test_query_rejects_sibling_semantic_space_before_embedding(
    tmp_path: Path
):
    index_root, _, _ = _synthetic_index(
        tmp_path, rows=1, embedding_dim=1152
    )
    called = []

    with pytest.raises(ValueError, match="SEMANTIC_SPACE_MISMATCH:"):
        query_generation(
            index_root,
            make_spec(),
            ["must not embed"],
            lambda texts: called.append(texts),
            top_k=1,
        )

    assert called == []


# --------------------------------------------------------------------------
# 1. equivalence with the frozen reference behaviour
# --------------------------------------------------------------------------


def test_all_active_rows_match_reference_ordering_and_scores():
    query = _axis(0)
    vectors = _matrix(_axis(0), _axis(0) * 0.5, _axis(1))
    metadata = _metadata(
        (0, True, "a" * 64, 0, 1, 1000, True),
        (1, True, "b" * 64, 0, 1, 1000, True),
        (2, True, "c" * 64, 0, 1, 1000, True),
    )
    reference = exact_top_k(vectors, query, metadata, 3)
    indexed = exact_top_k_indexed(vectors, query, _mask(metadata), _fetch_from(metadata), 3)
    _assert_same_hits(indexed, reference)
    assert [hit.row_id for hit in indexed] == [0, 1, 2]
    assert indexed[0].score == pytest.approx(1.0)


def test_inactive_row_with_best_possible_score_never_wins():
    query = _axis(0)
    vectors = _matrix(_axis(0), _axis(0) * 0.5)
    metadata = _metadata(
        (0, False, "a" * 64, 0, 1, 1000, True),  # exactly the query, inactive
        (1, True, "b" * 64, 0, 1, 1000, True),
    )
    indexed = exact_top_k_indexed(vectors, query, _mask(metadata), _fetch_from(metadata), 5)
    assert [hit.row_id for hit in indexed] == [1]
    assert all(hit.row_id != 0 for hit in indexed)


def test_mixed_active_and_inactive_rows_match_reference():
    query = _axis(0)
    vectors = _matrix(
        _axis(0),          # 0 inactive, perfect score
        _axis(0) * 0.9,    # 1 active
        _axis(0) * 0.8,    # 2 inactive
        _axis(0) * 0.7,    # 3 active
        _axis(1),          # 4 active, zero score
    )
    metadata = _metadata(
        (0, False, "a" * 64, 0, 1, 1000, True),
        (1, True, "b" * 64, 10, 1, 1000, True),
        (2, False, "c" * 64, 20, 1, 1000, True),
        (3, True, "d" * 64, 30, 1, 1000, True),
        (4, True, "e" * 64, 40, 1, 1000, True),
    )
    reference = exact_top_k(vectors, query, metadata, 5)
    indexed = exact_top_k_indexed(vectors, query, _mask(metadata), _fetch_from(metadata), 5)
    _assert_same_hits(indexed, reference)
    assert [hit.row_id for hit in indexed] == [1, 3, 4]


def test_missing_thumbnail_is_reported_identically():
    query = _axis(0)
    vectors = _matrix(_axis(0), _axis(1))
    metadata = _metadata(
        (0, True, "a" * 64, 0, 1, 1000, False),  # thumbnail missing
        (1, True, "b" * 64, 0, 1, 1000, True),
    )
    indexed = exact_top_k_indexed(vectors, query, _mask(metadata), _fetch_from(metadata), 5)
    assert indexed[0].thumbnail_status == search.THUMBNAIL_MISSING
    assert indexed[0].thumbnail_path is None
    _assert_same_hits(indexed, exact_top_k(vectors, query, metadata, 5))


def test_tie_order_is_preserved_exactly():
    """Frozen current tie order: source bytes, then exact rational instant, then row."""
    query = _axis(0)
    vectors = _matrix(_axis(0), _axis(0), _axis(0), _axis(0))
    metadata = _metadata(
        (0, True, "b" * 64, 100, 1, 1000, True),
        (1, True, "a" * 64, 200, 1, 1000, True),
        (2, True, "a" * 64, 100, 1, 1000, True),
        (3, True, "a" * 64, 100, 1, 1000, True),
    )
    reference = exact_top_k(vectors, query, metadata, 4)
    assert [hit.row_id for hit in reference] == [2, 3, 1, 0]
    for _ in range(3):
        indexed = exact_top_k_indexed(
            vectors, query, _mask(metadata), _fetch_from(metadata), 4
        )
        _assert_same_hits(indexed, reference)


def test_tie_at_the_top_k_boundary_is_resolved_identically():
    """A tie straddling the cut still selects by the frozen tie-break order."""
    query = _axis(0)
    vectors = _matrix(_axis(0), _axis(0), _axis(0), _axis(0))
    metadata = _metadata(
        (0, True, "c" * 64, 0, 1, 1000, True),
        (1, True, "b" * 64, 0, 1, 1000, True),
        (2, True, "a" * 64, 0, 1, 1000, True),
        (3, True, "d" * 64, 0, 1, 1000, True),
    )
    reference = exact_top_k(vectors, query, metadata, 2)
    indexed = exact_top_k_indexed(vectors, query, _mask(metadata), _fetch_from(metadata), 2)
    _assert_same_hits(indexed, reference)
    assert [hit.row_id for hit in indexed] == [2, 1]


def test_many_way_tie_at_the_boundary_matches_reference():
    """Twelve identical scores cut at five: selection must match the reference."""
    query = _axis(0)
    vectors = _matrix(*[_axis(0) for _ in range(12)])
    metadata = _metadata(
        *[(row_id, True, f"{row_id:02d}" + "a" * 62, row_id, 1, 1000, True) for row_id in range(12)]
    )
    reference = exact_top_k(vectors, query, metadata, 5)
    indexed = exact_top_k_indexed(vectors, query, _mask(metadata), _fetch_from(metadata), 5)
    _assert_same_hits(indexed, reference)
    assert [hit.row_id for hit in indexed] == [0, 1, 2, 3, 4]


def test_top_k_larger_and_smaller_than_active_rows():
    query = _axis(0)
    vectors = _matrix(_axis(0), _axis(0) * 0.5, _axis(0) * 0.25)
    metadata = _metadata(
        (0, True, "a" * 64, 0, 1, 1000, True),
        (1, False, "b" * 64, 0, 1, 1000, True),
        (2, True, "c" * 64, 0, 1, 1000, True),
    )
    for top_k in (1, 2, 3, 10):
        reference = exact_top_k(vectors, query, metadata, top_k)
        indexed = exact_top_k_indexed(
            vectors, query, _mask(metadata), _fetch_from(metadata), top_k
        )
        _assert_same_hits(indexed, reference)


def test_indexed_path_keeps_input_validation_contract():
    vectors = _matrix(_axis(0))
    with pytest.raises(ValueError, match="INVALID_TOP_K"):
        exact_top_k_indexed(vectors, _axis(0), np.ones(1, dtype=bool), lambda ids: {}, 0)
    with pytest.raises(ValueError, match="QUERY_SHAPE"):
        exact_top_k_indexed(
            vectors, np.zeros(10, dtype=np.float32), np.ones(1, dtype=bool), lambda ids: {}, 1
        )
    empty = np.zeros((0, 768), dtype=np.float32)
    assert exact_top_k_indexed(empty, _axis(0), np.zeros(0, dtype=bool), lambda ids: {}, 5) == ()
    with pytest.raises(ValueError, match="ACTIVE_MASK_SHAPE"):
        exact_top_k_indexed(vectors, _axis(0), np.ones(7, dtype=bool), lambda ids: {}, 1)


def test_missing_candidate_metadata_does_not_hide_next_returnable_row():
    """A missing high-score row is unknown and must not consume the Top-K slot."""
    vectors = _matrix(_axis(0), _axis(0) * 0.9)
    metadata = _metadata(
        (1, True, "b" * 64, 0, 1, 1000, True),
    )
    hits = exact_top_k_indexed(
        vectors,
        _axis(0),
        np.ones(2, dtype=bool),
        lambda row_ids: {row_id: metadata[row_id] for row_id in row_ids if row_id in metadata},
        1,
    )
    assert [hit.row_id for hit in hits] == [1]


def test_backfill_fetches_only_remaining_slots_and_expands_boundary_ties():
    """Backfill is bounded by open Top-K slots, including ties at that boundary."""
    scores = np.asarray([1.0, 0.95, 0.9, 0.8, 0.8, 0.7], dtype=np.float64)
    vectors = _matrix(*[_axis(0, float(score)) for score in scores])
    metadata = _metadata(
        (0, True, "a" * 64, 0, 1, 1000, True),
        (3, True, "d" * 64, 0, 1, 1000, True),
        (4, True, "e" * 64, 0, 1, 1000, True),
    )
    fetch_calls: list[list[int]] = []

    def fetch(row_ids):
        fetch_calls.append(list(row_ids))
        return {row_id: metadata[row_id] for row_id in row_ids if row_id in metadata}

    hits = exact_top_k_indexed(
        vectors,
        _axis(0),
        np.ones(6, dtype=bool),
        fetch,
        3,
        scores=scores,
    )

    assert [hit.row_id for hit in hits] == [0, 3, 4]
    assert fetch_calls == [[0, 1, 2], [3, 4]]


# --------------------------------------------------------------------------
# 2. equivalence on a real generation (storage contract, still no media)
# --------------------------------------------------------------------------


def test_real_generation_query_matches_reference_over_full_metadata(tmp_path: Path):
    index_root, spec, generation = _synthetic_index(tmp_path)
    generation_paths, matrix, active_mask, close = open_generation_for_query(index_root, spec)
    try:
        assert matrix.shape[0] == COMMITTED_ROWS
        assert active_mask.all()
        reference_metadata = fetch_sample_metadata(
            generation_paths, COMMITTED_ROWS, list(range(COMMITTED_ROWS))
        )
        query = deterministic_vector("query-vector").astype(np.float32)
        for top_k in (1, 3, TOP_K, 40, 200):
            reference = exact_top_k(matrix, query, reference_metadata, top_k)
            indexed = exact_top_k_indexed(
                matrix, query, active_mask, _metadata_lookup(reference_metadata), top_k
            )
            _assert_same_hits(indexed, reference)
    finally:
        close()


def test_inactive_rows_are_excluded_on_a_real_generation(tmp_path: Path):
    """The top-scoring committed rows are marked inactive; none may be returned."""
    index_root, spec, generation = _synthetic_index(tmp_path, active_from=COMMITTED_ROWS - 3)
    # Query with the exact vector of an inactive row: it must not win.
    query = deterministic_vector(f"synthetic-row-{COMMITTED_ROWS - 1}").astype(np.float32)
    results = query_generation(
        index_root, spec, ["q"], lambda texts: np.stack([query]), top_k=TOP_K
    )
    hits = results["q"]
    assert hits
    assert all(hit.row_id < COMMITTED_ROWS - 3 for hit in hits), "inactive row won"
    generation_paths, matrix, active_mask, close = open_generation_for_query(index_root, spec)
    try:
        reference_metadata = fetch_sample_metadata(
            generation_paths, COMMITTED_ROWS, list(range(COMMITTED_ROWS))
        )
        reference = exact_top_k(matrix, query, reference_metadata, TOP_K)
        _assert_same_hits(hits, reference)
    finally:
        close()


def test_active_mask_matches_sample_activity(tmp_path: Path):
    index_root, spec, generation = _synthetic_index(tmp_path, active_from=50)
    _, _, active_mask, close = open_generation_for_query(index_root, spec)
    try:
        assert active_mask.sum() == 50
        assert not active_mask[50:].any()
    finally:
        close()
    conn = connect_db(generation, readonly=True)
    try:
        active_rows = [
            int(row[0])
            for row in conn.execute("SELECT row_id FROM samples WHERE active=1 ORDER BY row_id")
        ]
    finally:
        conn.close()
    assert active_rows == list(range(50))


# --------------------------------------------------------------------------
# 3. bounded materialization (structural, not timing)
# --------------------------------------------------------------------------


def test_query_does_not_construct_one_search_hit_per_committed_row(monkeypatch, tmp_path: Path):
    index_root, spec, _ = _synthetic_index(tmp_path)
    calls: list[int] = []
    real_hit = search.SearchHit

    def counting_hit(*args, **kwargs):
        calls.append(1)
        return real_hit(*args, **kwargs)

    monkeypatch.setattr(search, "SearchHit", counting_hit)
    hits = query_generation(index_root, spec, ["q"], _fixed_query(), top_k=TOP_K)["q"]
    assert len(hits) == TOP_K
    assert len(calls) <= 4 * TOP_K, (
        f"constructed {len(calls)} SearchHit objects for {len(hits)} hits "
        f"over {COMMITTED_ROWS} committed rows"
    )
    assert len(calls) < COMMITTED_ROWS // 4


def test_query_does_not_fetch_metadata_for_every_committed_row(monkeypatch, tmp_path: Path):
    index_root, spec, _ = _synthetic_index(tmp_path)
    built: list[int] = []
    real_meta = search.SampleMeta

    def counting_meta(*args, **kwargs):
        built.append(1)
        return real_meta(*args, **kwargs)

    monkeypatch.setattr(search, "SampleMeta", counting_meta)
    hits = query_generation(index_root, spec, ["q"], _fixed_query(), top_k=TOP_K)["q"]
    assert len(hits) == TOP_K
    assert len(built) <= 2 * TOP_K, (
        f"built {len(built)} SampleMeta objects for {len(hits)} hits "
        f"over {COMMITTED_ROWS} committed rows"
    )
    assert len(built) < COMMITTED_ROWS // 4


def test_multi_query_metadata_fetch_is_bounded_by_union_of_winners(tmp_path: Path):
    index_root, spec, _ = _synthetic_index(tmp_path)
    built: list[int] = []
    real_meta = search.SampleMeta

    def counting_meta(*args, **kwargs):
        built.append(1)
        return real_meta(*args, **kwargs)

    original = search.SampleMeta
    search.SampleMeta = counting_meta
    try:
        results = query_generation(
            index_root,
            spec,
            ["one", "two", "three", "four", "five", "six", "seven"],
            _fixed_query(),
            top_k=TOP_K,
        )
    finally:
        search.SampleMeta = original

    returned = sum(len(hits) for hits in results.values())
    assert returned == 7 * TOP_K
    assert len(built) <= 7 * TOP_K, (
        f"built {len(built)} SampleMeta objects for {returned} returned hits "
        f"over {COMMITTED_ROWS} committed rows"
    )
    assert len(built) < COMMITTED_ROWS


def test_inactive_row_excluded_without_full_metadata_map(tmp_path: Path, monkeypatch):
    """An inactive row holding the query vector must not win, still bounded."""
    index_root, spec, _ = _synthetic_index(tmp_path, active_from=COMMITTED_ROWS - 1)
    inactive_vector = deterministic_vector(f"synthetic-row-{COMMITTED_ROWS - 1}").astype(np.float32)
    built: list[int] = []
    real_meta = search.SampleMeta

    def counting_meta(*args, **kwargs):
        built.append(1)
        return real_meta(*args, **kwargs)

    monkeypatch.setattr(search, "SampleMeta", counting_meta)
    hits = query_generation(
        index_root, spec, ["q"], lambda texts: np.stack([inactive_vector]), top_k=TOP_K
    )["q"]
    assert hits
    assert all(hit.row_id != COMMITTED_ROWS - 1 for hit in hits)
    assert len(built) <= 2 * TOP_K


def test_query_never_opens_registered_source_media(monkeypatch, tmp_path: Path):
    """Search may return source provenance but must not read source bytes."""
    index_root, spec, _ = _synthetic_index(tmp_path)
    source_path = "/synthetic-fixture/source-000000.mp4"
    real_open = Path.open
    opened_sources: list[str] = []

    def guarded_open(path: Path, *args, **kwargs):
        if str(path) == source_path:
            opened_sources.append(str(path))
            raise AssertionError("query opened registered source media")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)
    hits = query_generation(
        index_root, spec, ["q"], _fixed_query(), top_k=TOP_K
    )["q"]

    assert hits
    assert all(hit.source_path == source_path for hit in hits)
    assert opened_sources == []


def _fixed_query():
    vector = deterministic_vector("fixed-benchmark-query").astype(np.float32)

    def embedder(texts):
        return np.stack([vector for _ in texts]).astype(np.float32)

    return embedder


def _metadata_lookup(metadata):
    return search._metadata_lookup(metadata)
