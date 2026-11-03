"""Gate-1 TDD: fail-closed committed geometry on the read paths.

The writer paths already refuse a SQLite row/byte disagreement
(``COMMITTED_ROWS_BYTES_DISAGREE``).  The reader paths must refuse the same
corrupt state instead of silently memmapping a wrong-shaped prefix: with
``committed_vector_bytes`` an integer multiple of the row width but not equal to
``committed_rows * row_width``, a memmap of ``committed_rows`` can read past EOF
or drop committed rows from the searchable prefix.

These tests exercise the public read entry points only, with test-managed temp
generations and synthetic unit vectors.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from persistent_local_index import storage
from persistent_local_index.model_space import SemanticSpace, build_generation_spec
from persistent_local_index.search import open_generation_for_query
from persistent_local_index.storage import (
    PersistedSample,
    append_source_segment,
    connect_db,
    open_or_create_generation,
)

ROW_WIDTH_768 = 768 * 4
ROW_WIDTH_1152 = 1152 * 4


def _space(dim: int = 768) -> SemanticSpace:
    return SemanticSpace(
        model_identity="google/siglip-base-patch16-224",
        frozen_revision="7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
        weights_sha256="2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8",
        processor_digest="proc",
        image_preprocessing_digest="image",
        text_preprocessing_contract="padding=max_length",
        embedding_dim=dim,
        dtype="float32",
        normalization="l2",
    )


def _spec(dim: int = 768):
    return build_generation_spec(_space(dim))


def _unit(seed: int, dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vector = rng.standard_normal(dim).astype(np.float32)
    return vector / np.linalg.norm(vector)


def _vectors(n: int, dim: int = 768, seed: int = 0) -> np.ndarray:
    return np.stack([_unit(seed + i, dim) for i in range(n)]).astype(np.float32)


def _samples(n: int) -> list[PersistedSample]:
    out = []
    for i in range(n):
        pts = i * 225000
        pts_time = pts * 1 / 90000
        out.append(
            PersistedSample(
                pts=pts,
                timebase_num=1,
                timebase_den=90000,
                pts_time=pts_time,
                timestamp_human=f"00:00:{pts_time:06.3f}",
                thumbnail_stage_path=Path(f"stage_{i}.jpg"),
            )
        )
    return out


def _meta() -> dict:
    return {
        "size_bytes": 1024,
        "stream_index": 0,
        "codec": "h264",
        "width": 64,
        "height": 64,
        "timebase_num": 1,
        "timebase_den": 90000,
        "duration_seconds": 9.0,
        "source_revision": None,
    }


def _corrupt_rows_bytes_mismatch(conn, *, row_count: int, committed_bytes: int) -> None:
    with conn:
        conn.execute(
            "UPDATE generation_state SET committed_row_count=?, committed_vector_bytes=? "
            "WHERE singleton=1",
            (row_count, committed_bytes),
        )


# --- reader memmap path ----------------------------------------------------


def test_memmap_refuses_rows_bytes_disagreement(tmp_path: Path):
    """bytes are row-aligned but disagree with the row count -> refuse, do not map."""
    paths = open_or_create_generation(tmp_path / "idx", _spec())
    conn = connect_db(paths)
    append_source_segment(
        paths,
        conn,
        source_sha256="m" * 64,
        source_metadata=_meta(),
        samples=_samples(2),
        normalized_vectors=_vectors(2, seed=110),
        expected_dim=768,
    )
    _corrupt_rows_bytes_mismatch(conn, row_count=2, committed_bytes=ROW_WIDTH_768)

    with pytest.raises(
        ValueError, match=r"COMMITTED_ROWS_BYTES_DISAGREE:rows=2:bytes=3072"
    ):
        storage.memmap_committed_prefix(paths, conn, ROW_WIDTH_768)
    conn.close()


def test_memmap_refuses_1152_wider_rows_bytes_disagreement(tmp_path: Path):
    paths = open_or_create_generation(tmp_path / "idx-1152", _spec(1152))
    conn = connect_db(paths)
    append_source_segment(
        paths,
        conn,
        source_sha256="n" * 64,
        source_metadata=_meta(),
        samples=_samples(1),
        normalized_vectors=_vectors(1, 1152, seed=120),
        expected_dim=1152,
    )
    _corrupt_rows_bytes_mismatch(conn, row_count=1, committed_bytes=2 * ROW_WIDTH_1152)

    with pytest.raises(
        ValueError, match=r"COMMITTED_ROWS_BYTES_DISAGREE:rows=1:bytes=9216"
    ):
        storage.memmap_committed_prefix(paths, conn, ROW_WIDTH_1152)
    conn.close()


# --- read-only query open path --------------------------------------------


def test_query_open_refuses_rows_bytes_disagreement(tmp_path: Path):
    index_root = tmp_path / "idx"
    paths = open_or_create_generation(index_root, _spec())
    conn = connect_db(paths)
    append_source_segment(
        paths,
        conn,
        source_sha256="q" * 64,
        source_metadata=_meta(),
        samples=_samples(2),
        normalized_vectors=_vectors(2, seed=130),
        expected_dim=768,
    )
    conn.close()
    # The manifest mirror still says committed_rows=2, so the manifest-ahead
    # check passes; only the row/byte invariant can catch this corruption.
    conn = connect_db(paths)
    _corrupt_rows_bytes_mismatch(conn, row_count=2, committed_bytes=ROW_WIDTH_768)
    conn.close()

    with pytest.raises(
        ValueError, match=r"COMMITTED_ROWS_BYTES_DISAGREE:rows=2:bytes=3072"
    ):
        open_generation_for_query(index_root, _spec())


def test_query_open_refuses_1152_rows_bytes_disagreement(tmp_path: Path):
    index_root = tmp_path / "idx-1152"
    paths = open_or_create_generation(index_root, _spec(1152))
    conn = connect_db(paths)
    append_source_segment(
        paths,
        conn,
        source_sha256="r" * 64,
        source_metadata=_meta(),
        samples=_samples(1),
        normalized_vectors=_vectors(1, 1152, seed=140),
        expected_dim=1152,
    )
    conn.close()
    conn = connect_db(paths)
    _corrupt_rows_bytes_mismatch(conn, row_count=1, committed_bytes=2 * ROW_WIDTH_1152)
    conn.close()

    with pytest.raises(
        ValueError, match=r"COMMITTED_ROWS_BYTES_DISAGREE:rows=1:bytes=9216"
    ):
        open_generation_for_query(index_root, _spec(1152))


# --- preserved positive behaviour -----------------------------------------


def test_memmap_refuses_negative_committed_counts(tmp_path: Path):
    """A negative pair can satisfy rows*width == bytes; it is still corrupt."""
    paths = open_or_create_generation(tmp_path / "idx-negative", _spec())
    conn = connect_db(paths)
    append_source_segment(
        paths,
        conn,
        source_sha256="t" * 64,
        source_metadata=_meta(),
        samples=_samples(1),
        normalized_vectors=_vectors(1, seed=160),
        expected_dim=768,
    )
    _corrupt_rows_bytes_mismatch(conn, row_count=-1, committed_bytes=-ROW_WIDTH_768)

    with pytest.raises(
        ValueError, match=r"COMMITTED_COUNTS_NEGATIVE:rows=-1:bytes=-3072"
    ):
        storage.memmap_committed_prefix(paths, conn, ROW_WIDTH_768)
    conn.close()


def test_valid_768_generation_still_reads_exact_committed_prefix(tmp_path: Path):
    index_root = tmp_path / "idx"
    paths = open_or_create_generation(index_root, _spec())
    conn = connect_db(paths)
    append_source_segment(
        paths,
        conn,
        source_sha256="s" * 64,
        source_metadata=_meta(),
        samples=_samples(3),
        normalized_vectors=_vectors(3, seed=150),
        expected_dim=768,
    )
    array, close = storage.memmap_committed_prefix(paths, conn, ROW_WIDTH_768)
    assert array.shape == (3, 768)
    assert array.dtype == np.dtype("<f4")
    close()
    conn.close()

    generation, matrix, active_mask, close = open_generation_for_query(
        index_root, _spec()
    )
    try:
        assert matrix.shape == (3, 768)
        assert active_mask.all()
    finally:
        close()


def test_valid_1152_generation_query_reads_exact_committed_prefix(tmp_path: Path):
    index_root = tmp_path / "idx-1152-valid"
    paths = open_or_create_generation(index_root, _spec(1152))
    conn = connect_db(paths)
    append_source_segment(
        paths,
        conn,
        source_sha256="u" * 64,
        source_metadata=_meta(),
        samples=_samples(2),
        normalized_vectors=_vectors(2, 1152, seed=170),
        expected_dim=1152,
    )
    conn.close()

    generation, matrix, active_mask, close = open_generation_for_query(
        index_root, _spec(1152)
    )
    try:
        assert matrix.shape == (2, 1152)
        assert active_mask.shape == (2,)
        assert active_mask.all()
    finally:
        close()


def test_empty_generation_query_reads_zero_rows(tmp_path: Path):
    index_root = tmp_path / "idx-empty"
    open_or_create_generation(index_root, _spec())

    generation, matrix, active_mask, close = open_generation_for_query(
        index_root, _spec()
    )
    try:
        assert matrix.shape == (0, 768)
        assert matrix.dtype == np.float32
        assert active_mask.shape == (0,)
    finally:
        close()
