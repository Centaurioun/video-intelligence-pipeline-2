"""Read-only generation validation, memmap exact cosine, deterministic top-K.

Authority: approved design sections 2.2, 11, 12, 14 and plan Task 6.

This module is deliberately *read-only* and deliberately incapable of decoding
video or image-embedding indexed media: it takes a ``text_embedder`` and never an
image embedder.  There is no code path here that can invoke FFmpeg.

Ordering is a deterministic total order:

1. descending cosine score;
2. ``source_sha256`` UTF-8 bytes;
3. the measured rational PTS instant, compared exactly (gcd-normalized
   ``Fraction``), never as a lossy float;
4. ``row_id``.

Rational comparison is exact so that ``1/3 s`` and ``2/6 s`` order as the same
instant rather than by accumulated float error.

Two entry points exist by design:

* :func:`exact_top_k` is the *reference* semantics.  It takes a complete
  ``row_id -> SampleMeta`` map and is kept as the frozen oracle for equivalence
  testing; it materializes one ``SearchHit`` per active row.
* :func:`exact_top_k_indexed` is the *production* query path.  It keeps only a
  compact boolean activity mask, scores all committed vectors, selects the
  winning row ids first, and materializes ``SampleMeta``/``SearchHit`` objects
  only for rows that can actually be returned.  Ordering, scores, masking, and
  the returned provenance are required to be identical to the reference.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable, Mapping, Sequence

import numpy as np

from persistent_local_index.model_space import (
    GenerationSpec,
    load_manifest,
    read_manifest_committed_rows,
    validate_manifest_compatibility,
)
from persistent_local_index.storage import (
    GenerationPaths,
    connect_db,
    open_or_create_generation,
    read_committed_counts,
    require_committed_geometry,
)

THUMBNAIL_PRESENT = "PRESENT"
THUMBNAIL_MISSING = "MISSING"


@dataclass(frozen=True)
class SampleMeta:
    row_id: int
    source_sha256: str
    source_path: str | None
    pts: int
    timebase_num: int
    timebase_den: int
    timestamp_human: str
    thumbnail_path: str | None
    active: bool
    thumbnail_status: str = THUMBNAIL_PRESENT


@dataclass(frozen=True)
class SearchHit:
    query: str
    rank: int
    score: float
    row_id: int
    source_path: str | None
    source_sha256: str
    pts: int
    timebase_num: int
    timebase_den: int
    timestamp_human: str
    thumbnail_path: str | None
    thumbnail_status: str


def pts_instant(pts: int, timebase_num: int, timebase_den: int) -> Fraction:
    """Exact rational presentation instant for a measured PTS.

    Never ``pts / fps``: the source-native timebase is the only authority.
    """
    if timebase_den == 0:
        raise ValueError("ZERO_TIMEBASE_DENOMINATOR")
    return Fraction(pts * timebase_num, timebase_den)


def _sort_key(hit: SearchHit) -> tuple:
    """Deterministic total order.  Exact rational instant, never float seconds."""
    return (
        -hit.score,
        hit.source_sha256.encode("utf-8"),
        pts_instant(hit.pts, hit.timebase_num, hit.timebase_den),
        hit.row_id,
    )


def exact_top_k(
    vectors: np.ndarray,
    query: np.ndarray,
    metadata: Mapping[int, SampleMeta],
    top_k: int,
) -> tuple[SearchHit, ...]:
    """Frozen reference exact top-K over a committed vector prefix.

    Inactive or unknown rows are masked to ``-inf`` and can never be returned.
    Kept as the equivalence oracle for the production indexed path; it is not
    used by ``query_generation``.
    """
    if top_k < 1:
        raise ValueError(f"INVALID_TOP_K:{top_k}")
    matrix = np.asarray(vectors)
    query_vector = np.asarray(query).reshape(-1)
    if matrix.ndim != 2:
        raise ValueError(f"VECTOR_SHAPE:{matrix.shape}")
    if query_vector.shape[0] != matrix.shape[1]:
        raise ValueError(
            f"QUERY_SHAPE:{query_vector.shape[0]}!={matrix.shape[1]}"
        )
    row_count = matrix.shape[0]
    if row_count == 0:
        return ()

    # Vectors and query are already L2-normalized, so cosine is one matvec.
    scores = _scores_for(matrix, query_vector)

    candidates: list[SearchHit] = []
    for row_id in range(row_count):
        meta = metadata.get(row_id)
        if meta is None or not meta.active:
            # inactive / unknown rows are unsearchable
            continue
        candidates.append(
            SearchHit(
                query="",
                rank=0,
                score=float(scores[row_id]),
                row_id=row_id,
                source_path=meta.source_path,
                source_sha256=meta.source_sha256,
                pts=meta.pts,
                timebase_num=meta.timebase_num,
                timebase_den=meta.timebase_den,
                timestamp_human=meta.timestamp_human,
                thumbnail_path=meta.thumbnail_path,
                thumbnail_status=meta.thumbnail_status,
            )
        )

    candidates.sort(key=_sort_key)
    ordered = candidates[:top_k]
    return tuple(
        SearchHit(
            query=hit.query,
            rank=index,
            score=hit.score,
            row_id=hit.row_id,
            source_path=hit.source_path,
            source_sha256=hit.source_sha256,
            pts=hit.pts,
            timebase_num=hit.timebase_num,
            timebase_den=hit.timebase_den,
            timestamp_human=hit.timestamp_human,
            thumbnail_path=hit.thumbnail_path,
            thumbnail_status=hit.thumbnail_status,
        )
        for index, hit in enumerate(ordered, start=1)
    )


def _validate_query_arguments(
    vectors: np.ndarray, query: np.ndarray, top_k: int
) -> tuple[np.ndarray, np.ndarray]:
    """Shared validation for both exact-search entry points."""
    if top_k < 1:
        raise ValueError(f"INVALID_TOP_K:{top_k}")
    matrix = np.asarray(vectors)
    query_vector = np.asarray(query).reshape(-1)
    if matrix.ndim != 2:
        raise ValueError(f"VECTOR_SHAPE:{matrix.shape}")
    if query_vector.shape[0] != matrix.shape[1]:
        raise ValueError(
            f"QUERY_SHAPE:{query_vector.shape[0]}!={matrix.shape[1]}"
        )
    return matrix, query_vector


def _scores_for(matrix: np.ndarray, query_vector: np.ndarray) -> np.ndarray:
    """Exact cosine scores for a committed vector prefix.

    Vectors and query are already L2-normalized before persistence, so cosine is
    one float32 matvec promoted to float64 — the same arithmetic the reference
    ``exact_top_k`` performs, so both paths agree bit-for-bit.
    """
    return (matrix.astype(np.float32) @ query_vector.astype(np.float32)).astype(np.float64)


def exact_top_k_indexed(
    vectors: np.ndarray,
    query: np.ndarray,
    active_mask: np.ndarray,
    fetch_metadata: Callable[[Sequence[int]], Mapping[int, SampleMeta]],
    top_k: int,
    *,
    scores: np.ndarray | None = None,
) -> tuple[SearchHit, ...]:
    """Exact top-K that materializes metadata/hits only for returnable rows.

    Behavioural contract (must equal :func:`exact_top_k`):

    * identical scores and identical deterministic ordering;
    * inactive rows can never be returned and are not even considered;
    * rows whose metadata the fetcher does not return are treated as unsearchable,
      exactly like unknown rows in the reference implementation;
    * row ids outside the committed prefix never participate.

    Materialization contract: candidate row ids are selected from scores alone
    in descending cohorts that include every tie at each cohort boundary.
    Metadata is fetched only for those candidates, expanding to lower cohorts
    only when missing/inactive metadata leaves fewer than ``top_k`` hits.
    ``SearchHit`` objects are built only for returned hits.

    ``scores`` may be supplied by a caller that already computed them (the
    multi-query path scores once and reuses), and must then be the exact output
    of :func:`_scores_for` for the same matrix and query.
    """
    matrix, query_vector = _validate_query_arguments(vectors, query, top_k)
    row_count = matrix.shape[0]
    active = np.asarray(active_mask)
    if active.shape[0] != row_count:
        raise ValueError(f"ACTIVE_MASK_SHAPE:{active.shape[0]}!={row_count}")
    if row_count == 0:
        return ()

    if scores is None:
        scores = _scores_for(matrix, query_vector)
    candidates: list[SearchHit] = []
    remaining = np.asarray(active, dtype=bool).copy()
    while np.any(remaining):
        needed = top_k - len(candidates)
        candidate_rows = _select_candidate_rows(scores, remaining, needed)
        if not candidate_rows:
            break
        metadata = fetch_metadata(candidate_rows)
        for row_id in candidate_rows:
            remaining[row_id] = False
            meta = metadata.get(row_id)
            if meta is None or not meta.active:
                # Unknown or inactive metadata cannot consume a result slot.
                continue
            candidates.append(
                SearchHit(
                    query="",
                    rank=0,
                    score=float(scores[row_id]),
                    row_id=row_id,
                    source_path=meta.source_path,
                    source_sha256=meta.source_sha256,
                    pts=meta.pts,
                    timebase_num=meta.timebase_num,
                    timebase_den=meta.timebase_den,
                    timestamp_human=meta.timestamp_human,
                    thumbnail_path=meta.thumbnail_path,
                    thumbnail_status=meta.thumbnail_status,
                )
            )
        if len(candidates) >= top_k:
            break

    candidates.sort(key=_sort_key)
    ordered = candidates[:top_k]
    return tuple(
        SearchHit(
            query=hit.query,
            rank=index,
            score=hit.score,
            row_id=hit.row_id,
            source_path=hit.source_path,
            source_sha256=hit.source_sha256,
            pts=hit.pts,
            timebase_num=hit.timebase_num,
            timebase_den=hit.timebase_den,
            timestamp_human=hit.timestamp_human,
            thumbnail_path=hit.thumbnail_path,
            thumbnail_status=hit.thumbnail_status,
        )
        for index, hit in enumerate(ordered, start=1)
    )


def _select_candidate_rows(
    scores: np.ndarray, active: np.ndarray, top_k: int
) -> list[int]:
    """Winning (and boundary-tied) row ids, from scores and the activity mask alone.

    Raises nothing and materializes no metadata.  When fewer than ``top_k``
    active rows carry a finite score the full active set is returned, because
    non-finite/non-returnable scores must be filtered with their metadata in
    hand to reproduce the reference ordering exactly.
    """
    active_rows = np.flatnonzero(active)
    if active_rows.size == 0:
        return []
    if active_rows.size <= top_k:
        return [int(row) for row in active_rows]

    active_scores = scores[active_rows]
    # Select the k-th largest value.  ``np.argpartition`` accepts a *non-negative*
    # kth index, so the k-th largest lives at ``size - top_k`` (``top_k - 1`` is a
    # valid kth only from the front, and a negative value means "from the end").
    kth = active_scores.size - top_k
    if kth < 0:
        return [int(row) for row in active_rows]
    order = np.argpartition(active_scores, kth)
    threshold = active_scores[order[kth]]
    if not np.isfinite(threshold):
        return [int(row) for row in active_rows]
    selected = active_rows[active_scores >= threshold]
    return sorted(int(row) for row in selected)


# --------------------------------------------------------------------------
# generation loading
# --------------------------------------------------------------------------


_ROW_METADATA_SQL = (
    "SELECT s.row_id, s.source_sha256, s.pts, s.timebase_num, s.timebase_den,"
    " s.timestamp_human, s.thumbnail_relpath, s.active,"
    " (SELECT path FROM source_locations WHERE source_sha256=s.source_sha256"
    "  ORDER BY path LIMIT 1) AS source_path"
    " FROM samples s WHERE s.row_id < ? AND s.row_id IN ({placeholders})"
)


def _sample_meta_from_row(generation: GenerationPaths, row) -> SampleMeta:
    """Build one SampleMeta, including the on-disk thumbnail presence check."""
    relpath = row["thumbnail_relpath"]
    thumbnail = generation.root / relpath if relpath else None
    status = (
        THUMBNAIL_PRESENT
        if thumbnail is not None and thumbnail.is_file()
        else THUMBNAIL_MISSING
    )
    return SampleMeta(
        row_id=int(row["row_id"]),
        source_sha256=str(row["source_sha256"]),
        source_path=row["source_path"],
        pts=int(row["pts"]),
        timebase_num=int(row["timebase_num"]),
        timebase_den=int(row["timebase_den"]),
        timestamp_human=str(row["timestamp_human"]),
        thumbnail_path=relpath if status == THUMBNAIL_PRESENT else None,
        active=bool(row["active"]),
        thumbnail_status=status,
    )


def fetch_sample_metadata(
    generation: GenerationPaths, committed_rows: int, row_ids: Sequence[int]
) -> dict[int, SampleMeta]:
    """Fetch full metadata for an explicit, bounded set of committed row ids.

    This is the only metadata reader on the query path.  Rows that are not
    requested are never selected, never deserialized, and never turned into
    Python objects.  Row ids outside the committed prefix are ignored, matching
    the reference path's "unknown rows are unsearchable" rule.
    """
    wanted = sorted(
        {int(row_id) for row_id in row_ids if 0 <= int(row_id) < committed_rows}
    )
    if not wanted:
        return {}
    placeholders = ",".join("?" * len(wanted))
    conn = connect_db(generation, readonly=True)
    try:
        rows = conn.execute(
            _ROW_METADATA_SQL.format(placeholders=placeholders),
            (committed_rows, *wanted),
        ).fetchall()
    finally:
        conn.close()
    return {int(row["row_id"]): _sample_meta_from_row(generation, row) for row in rows}


def load_active_row_mask(
    generation: GenerationPaths, committed_rows: int
) -> np.ndarray:
    """Compact boolean activity mask for the committed prefix.

    One integer column and no joins: this is the only per-row state the exact
    scan needs, so the query path never has to build a full metadata map to know
    which vectors may win.
    """
    mask = np.zeros(committed_rows, dtype=bool)
    if committed_rows == 0:
        return mask
    conn = connect_db(generation, readonly=True)
    try:
        rows = conn.execute(
            "SELECT row_id FROM samples WHERE row_id < ? AND active=1",
            (committed_rows,),
        ).fetchall()
    finally:
        conn.close()
    if rows:
        mask[np.fromiter((int(row[0]) for row in rows), dtype=np.int64, count=len(rows))] = True
    return mask


def open_generation_for_query(
    index_root: Path, live_spec: GenerationSpec
) -> tuple[GenerationPaths, np.ndarray, np.ndarray, Callable[[], None]]:
    """Validate and open a generation read-only, returning the committed prefix.

    Returns ``(paths, matrix, active_mask, close)``.  The third element is the
    compact activity mask rather than a full metadata map, so opening an index
    does not materialize one object per committed row.

    Fails closed on semantic-space mismatch, committed rows/bytes that disagree
    with one row width, a vector file shorter than the committed length, and a
    manifest mirror *ahead* of SQLite.  A stale-lower manifest mirror is
    tolerated read-only (SQLite is the authority) and is never repaired here.
    """
    index_root = Path(index_root)
    generation_root = index_root / "generations" / live_spec.generation_id
    generation = GenerationPaths(
        root=generation_root,
        manifest=generation_root / "manifest.json",
        database=generation_root / "index.sqlite",
        vectors=generation_root / "vectors.f32",
        thumbs=generation_root / "thumbs",
        staging=generation_root / "staging",
        lock=generation_root / "writer.lock",
    )
    if not generation.manifest.is_file():
        # A query for a semantic space with no generation here is a space
        # mismatch, not merely a missing file: name the conflicting space.
        _raise_if_sibling_space_conflicts(index_root, live_spec)
        raise ValueError(f"MANIFEST_MISSING:{generation.manifest}")
    manifest = load_manifest(generation.manifest)
    validate_manifest_compatibility(manifest, live_spec)

    conn = connect_db(generation, readonly=True)
    try:
        committed_rows, committed_bytes = read_committed_counts(conn)
        require_committed_geometry(
            committed_rows, committed_bytes, live_spec.space.embedding_dim * 4
        )
        mirror = read_manifest_committed_rows(manifest)
        if mirror > committed_rows:
            raise ValueError(
                f"MANIFEST_COMMITTED_ROWS_AHEAD_OF_SQLITE:{mirror}>{committed_rows}"
            )
        physical = generation.vectors.stat().st_size if generation.vectors.exists() else 0
        if physical < committed_bytes:
            raise ValueError(
                f"VECTOR_FILE_SHORTER_THAN_COMMITTED:{physical}<{committed_bytes}"
            )
    finally:
        conn.close()

    row_width = live_spec.space.embedding_dim * 4
    columns = live_spec.space.embedding_dim
    if committed_rows == 0:
        return (
            generation,
            np.zeros((0, columns), dtype=np.float32),
            np.zeros(0, dtype=bool),
            lambda: None,
        )

    handle = generation.vectors.open("rb")
    try:
        matrix = np.memmap(handle, dtype="<f4", mode="r", shape=(committed_rows, columns))
    except BaseException:
        handle.close()
        raise

    holder = [matrix]

    def _close() -> None:
        holder.clear()
        handle.close()

    active_mask = load_active_row_mask(generation, committed_rows)
    return generation, matrix, active_mask, _close


# --------------------------------------------------------------------------
# query
# --------------------------------------------------------------------------


def _metadata_lookup(
    metadata: Mapping[int, SampleMeta],
) -> Callable[[Sequence[int]], Mapping[int, SampleMeta]]:
    """Adapt a pre-fetched metadata map to the ``fetch_metadata`` contract.

    Used by the multi-query path so provenance is fetched once for the union of
    candidate rows while each query still selects its own Top-K.
    """

    def lookup(row_ids: Sequence[int]) -> Mapping[int, SampleMeta]:
        return {
            row_id: metadata[row_id] for row_id in row_ids if row_id in metadata
        }

    return lookup


def _raise_if_sibling_space_conflicts(
    index_root: Path, live_spec: GenerationSpec
) -> None:
    """If another generation in this index root pins a different space, say so."""
    from persistent_local_index.model_space import _SPACE_FIELDS

    generations = index_root / "generations"
    if not generations.is_dir():
        return
    for candidate in sorted(generations.iterdir()):
        manifest_path = candidate / "manifest.json"
        if not manifest_path.is_file():
            continue
        existing = load_manifest(manifest_path)
        if existing.get("generation_id") == live_spec.generation_id:
            continue
        existing_space = existing.get("space")
        if not isinstance(existing_space, Mapping):
            continue
        for field in _SPACE_FIELDS:
            if existing_space.get(field) != getattr(live_spec.space, field):
                raise ValueError(
                    f"SEMANTIC_SPACE_MISMATCH:{field}:"
                    f"expected={getattr(live_spec.space, field)!r}:"
                    f"existing={existing_space.get(field)!r}"
                )
        raise ValueError(
            f"GENERATION_MISMATCH:generation_id:expected={live_spec.generation_id!r}:"
            f"existing={existing.get('generation_id')!r}"
        )


def query_generation(
    index_root: Path,
    live_spec: GenerationSpec,
    texts: Sequence[str],
    text_embedder: Callable[[Sequence[str]], np.ndarray],
    *,
    top_k: int,
) -> dict[str, tuple[SearchHit, ...]]:
    """Answer repeated text queries against persisted vectors read-only.

    Image re-embedding is impossible here by construction: this function has no
    image input and never opens source media.
    """
    queries = [str(text) for text in texts]
    if not queries:
        raise ValueError("NO_QUERIES")

    generation, matrix, active_mask, close = open_generation_for_query(index_root, live_spec)
    try:
        # One embedding batch for all queries: model cold-load is amortized
        # without introducing a daemon.
        query_matrix = np.asarray(text_embedder(queries))
        if query_matrix.ndim == 1:
            query_matrix = query_matrix.reshape(1, -1)
        if query_matrix.shape[0] != len(queries):
            raise ValueError(
                f"QUERY_EMBED_COUNT_MISMATCH:{query_matrix.shape[0]}!={len(queries)}"
            )
        expected_dim = live_spec.space.embedding_dim
        if query_matrix.shape[1] != expected_dim:
            raise ValueError(
                f"QUERY_DIMENSION_MISMATCH:{query_matrix.shape[1]}!={expected_dim}"
            )

        committed_rows = int(matrix.shape[0])
        # Pass 1: score each query ONCE and keep only the row ids that could be
        # returned (winning rows plus any tie straddling the Top-K cut).
        scores_per_query = [
            _scores_for(matrix, query_matrix[index]) for index in range(len(queries))
        ]
        selected_per_query = [
            _select_candidate_rows(scores_per_query[index], active_mask, top_k)
            for index in range(len(queries))
        ]
        union: set[int] = set()
        for row_ids in selected_per_query:
            union.update(row_ids)

        # Fetch the first winner union together. If missing rows require a
        # lower score cohort, cache every requested id (including missing
        # metadata) and fetch only newly needed ids as the exact scan expands.
        metadata = fetch_sample_metadata(generation, committed_rows, sorted(union))
        fetched = set(union)

        def cached_fetch(row_ids: Sequence[int]) -> Mapping[int, SampleMeta]:
            missing = sorted(set(row_ids) - fetched)
            if missing:
                metadata.update(
                    fetch_sample_metadata(generation, committed_rows, missing)
                )
                fetched.update(missing)
            return _metadata_lookup(metadata)(row_ids)

        results: dict[str, tuple[SearchHit, ...]] = {}
        for index, query_text in enumerate(queries):
            hits = exact_top_k_indexed(
                matrix,
                query_matrix[index],
                active_mask,
                cached_fetch,
                top_k,
                scores=scores_per_query[index],
            )
            results[query_text] = tuple(
                SearchHit(
                    query=query_text,
                    rank=hit.rank,
                    score=hit.score,
                    row_id=hit.row_id,
                    source_path=hit.source_path,
                    source_sha256=hit.source_sha256,
                    pts=hit.pts,
                    timebase_num=hit.timebase_num,
                    timebase_den=hit.timebase_den,
                    timestamp_human=hit.timestamp_human,
                    thumbnail_path=hit.thumbnail_path,
                    thumbnail_status=hit.thumbnail_status,
                )
                for hit in hits
            )
        return results
    finally:
        close()
