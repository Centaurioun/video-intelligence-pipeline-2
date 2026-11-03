"""TDD Task 2: SQLite commit authority, fixed-width vectors, crash-tail recovery."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from persistent_local_index.model_space import SemanticSpace, build_generation_spec
from persistent_local_index.storage import (
    GenerationPaths,
    PersistedSample,
    WriterLock,
    append_source_segment,
    connect_db,
    open_or_create_generation,
    read_committed_counts,
    reconcile_vector_tail,
)

ROW_WIDTH = 768 * 4


def _space() -> SemanticSpace:
    return SemanticSpace(
        model_identity="google/siglip-base-patch16-224",
        frozen_revision="7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
        weights_sha256="2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8",
        processor_digest="proc",
        image_preprocessing_digest="image",
        text_preprocessing_contract="padding=max_length",
        embedding_dim=768,
        dtype="float32",
        normalization="l2",
    )


def _spec(dim: int = 768):
    return build_generation_spec(replace(_space(), embedding_dim=dim))


def _unit(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(768).astype(np.float32)
    return vec / np.linalg.norm(vec)


def _unit_dim(seed: int, dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(dim).astype(np.float32)
    return vec / np.linalg.norm(vec)


def _vectors(n: int, seed: int = 0) -> np.ndarray:
    return np.stack([_unit(seed + i) for i in range(n)]).astype(np.float32)


def _vectors_dim(n: int, dim: int, seed: int = 0) -> np.ndarray:
    return np.stack([_unit_dim(seed + i, dim) for i in range(n)]).astype(np.float32)


def _samples(n: int, *, start_pts: int = 0, step: int = 225000) -> list[PersistedSample]:
    out = []
    for i in range(n):
        pts = start_pts + i * step
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


def _meta(size: int = 1024) -> dict:
    return {
        "size_bytes": size,
        "stream_index": 0,
        "codec": "h264",
        "width": 64,
        "height": 64,
        "timebase_num": 1,
        "timebase_den": 90000,
        "duration_seconds": 9.0,
        "source_revision": None,
    }


@pytest.fixture()
def paths(tmp_path: Path) -> GenerationPaths:
    return open_or_create_generation(tmp_path / "idx", _spec())


# --- layout ----------------------------------------------------------------


def test_open_or_create_generation_layout(paths: GenerationPaths):
    assert paths.manifest.is_file()
    assert paths.database.is_file()
    assert paths.vectors.is_file()
    assert paths.thumbs.is_dir()
    assert paths.staging.is_dir()


def test_open_or_create_generation_is_idempotent(tmp_path: Path):
    a = open_or_create_generation(tmp_path / "idx", _spec())
    b = open_or_create_generation(tmp_path / "idx", _spec())
    assert a.root == b.root
    conn = connect_db(b)
    assert read_committed_counts(conn) == (0, 0)
    conn.close()


def test_open_generation_rejects_incompatible_manifest(tmp_path: Path):
    """A space change must not be silently adopted under the same index root."""
    open_or_create_generation(tmp_path / "idx", _spec())
    other = build_generation_spec(replace(_space(), embedding_dim=512))
    with pytest.raises(ValueError, match="embedding_dim"):
        open_or_create_generation(tmp_path / "idx", other)


def test_schema_has_required_tables(paths: GenerationPaths):
    conn = connect_db(paths)
    names = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    assert {"generation_state", "source_objects", "source_locations", "samples"} <= names


def test_foreign_keys_enabled(paths: GenerationPaths):
    conn = connect_db(paths)
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    conn.close()


# --- writer lock -----------------------------------------------------------


def test_second_writer_lock_fails_closed(paths: GenerationPaths):
    with WriterLock(paths.lock):
        with pytest.raises(RuntimeError, match="CONCURRENT_WRITER"):
            with WriterLock(paths.lock):
                pass


def test_writer_lock_released_after_exit(paths: GenerationPaths):
    with WriterLock(paths.lock):
        pass
    with WriterLock(paths.lock):
        pass


def test_writer_lock_excludes_a_separate_process(paths: GenerationPaths):
    """The lock must coordinate independent processes, not only instances."""
    code = (
        "from persistent_local_index.storage import WriterLock\n"
        "import sys\n"
        "try:\n"
        "    with WriterLock(sys.argv[1]): pass\n"
        "except RuntimeError as exc:\n"
        "    print(str(exc))\n"
        "    raise SystemExit(0)\n"
        "raise SystemExit(3)\n"
    )
    with WriterLock(paths.lock):
        result = subprocess.run(
            [sys.executable, "-c", code, str(paths.lock)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    assert result.returncode == 0, result.stderr
    assert "CONCURRENT_WRITER" in result.stdout


# --- append + commit authority --------------------------------------------


def test_append_advances_sqlite_commit_authority(paths: GenerationPaths):
    conn = connect_db(paths)
    vectors = _vectors(3, seed=10)
    start, end = append_source_segment(
        paths,
        conn,
        source_sha256="a" * 64,
        source_metadata=_meta(),
        samples=_samples(3),
        normalized_vectors=vectors,
        expected_dim=768,
    )
    assert (start, end) == (0, 3)
    assert read_committed_counts(conn) == (3, 3 * ROW_WIDTH)
    assert paths.vectors.stat().st_size == 3 * ROW_WIDTH
    row = conn.execute(
        "SELECT state, row_start, row_end, active FROM source_objects WHERE source_sha256=?",
        ("a" * 64,),
    ).fetchone()
    assert tuple(row) == ("COMPLETE", 0, 3, 1)
    assert conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0] == 3
    conn.close()


def test_sqlite_committed_rows_and_bytes_match_persisted_vector_file(paths: GenerationPaths):
    """Check the persisted commit ledger against independent file-size evidence."""
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="z" * 64, source_metadata=_meta(),
        samples=_samples(2), normalized_vectors=_vectors(2, seed=150),
        expected_dim=768,
    )
    append_source_segment(
        paths, conn, source_sha256="y" * 64, source_metadata=_meta(),
        samples=_samples(3, start_pts=900000), normalized_vectors=_vectors(3, seed=160),
        expected_dim=768,
    )
    row_count, byte_count = conn.execute(
        "SELECT committed_row_count, committed_vector_bytes FROM generation_state WHERE singleton=1"
    ).fetchone()
    assert row_count == conn.execute("SELECT COUNT(*) FROM samples WHERE active=1").fetchone()[0]
    assert byte_count == row_count * ROW_WIDTH
    assert paths.vectors.stat().st_size == byte_count
    conn.close()


def test_append_records_exact_sqlite_pts_provenance(paths: GenerationPaths):
    conn = connect_db(paths)
    append_source_segment(
        paths,
        conn,
        source_sha256="b" * 64,
        source_metadata=_meta(),
        samples=_samples(2, start_pts=90000, step=450000),
        normalized_vectors=_vectors(2, seed=20),
        expected_dim=768,
    )
    rows = conn.execute(
        "SELECT row_id, pts, timebase_num, timebase_den, pts_time, timestamp_human, "
        "thumbnail_relpath, active FROM samples ORDER BY row_id"
    ).fetchall()
    assert rows[0][0] == 0 and rows[0][1] == 90000
    assert rows[0][2] == 1 and rows[0][3] == 90000
    assert rows[0][4] == pytest.approx(1.0)
    assert rows[1][1] == 540000
    assert all(r[7] == 1 for r in rows)
    conn.close()


def test_append_vector_bytes_are_exact_row_major_float32(paths: GenerationPaths):
    conn = connect_db(paths)
    vectors = _vectors(4, seed=30)
    append_source_segment(
        paths,
        conn,
        source_sha256="c" * 64,
        source_metadata=_meta(),
        samples=_samples(4),
        normalized_vectors=vectors,
        expected_dim=768,
    )
    raw = paths.vectors.read_bytes()
    assert len(raw) == 4 * ROW_WIDTH
    decoded = np.frombuffer(raw, dtype="<f4").reshape(4, 768)
    np.testing.assert_allclose(decoded, vectors, rtol=0, atol=0)
    conn.close()


def test_second_source_appends_contiguously(paths: GenerationPaths):
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="d" * 64, source_metadata=_meta(),
        samples=_samples(2), normalized_vectors=_vectors(2, seed=40),
        expected_dim=768,
    )
    start, end = append_source_segment(
        paths, conn, source_sha256="e" * 64, source_metadata=_meta(),
        samples=_samples(3), normalized_vectors=_vectors(3, seed=50),
        expected_dim=768,
    )
    assert (start, end) == (2, 5)
    assert read_committed_counts(conn) == (5, 5 * ROW_WIDTH)
    conn.close()


# --- validation ------------------------------------------------------------


def test_append_rejects_non_normalized_vectors(paths: GenerationPaths):
    conn = connect_db(paths)
    bad = np.full((2, 768), 0.5, dtype=np.float32)
    with pytest.raises(ValueError, match="NOT_UNIT_NORM"):
        append_source_segment(
            paths, conn, source_sha256="f" * 64, source_metadata=_meta(),
            samples=_samples(2), normalized_vectors=bad,
            expected_dim=768,
        )
    assert read_committed_counts(conn) == (0, 0)
    conn.close()


def test_append_rejects_wrong_shape_and_dtype(paths: GenerationPaths):
    conn = connect_db(paths)
    with pytest.raises(ValueError, match="VECTOR_SHAPE"):
        append_source_segment(
            paths, conn, source_sha256="g" * 64, source_metadata=_meta(),
            samples=_samples(2), normalized_vectors=np.zeros((2, 10), dtype=np.float32),
            expected_dim=768,
        )
    with pytest.raises(ValueError, match="VECTOR_DTYPE"):
        append_source_segment(
            paths, conn, source_sha256="g" * 64, source_metadata=_meta(),
            samples=_samples(2), normalized_vectors=np.zeros((2, 768), dtype=np.float64),
            expected_dim=768,
        )
    with pytest.raises(ValueError, match="VECTOR_SHAPE"):
        append_source_segment(
            paths, conn, source_sha256="g" * 64, source_metadata=_meta(),
            samples=_samples(3), normalized_vectors=_vectors(2, seed=60),
            expected_dim=768,
        )
    conn.close()


def test_append_rejects_non_finite_vectors(paths: GenerationPaths):
    conn = connect_db(paths)
    bad = _vectors(2, seed=70)
    bad[0, 0] = np.nan
    with pytest.raises(ValueError, match="NON_FINITE"):
        append_source_segment(
            paths, conn, source_sha256="h" * 64, source_metadata=_meta(),
            samples=_samples(2), normalized_vectors=bad,
            expected_dim=768,
        )
    conn.close()


def test_append_rejects_empty_source(paths: GenerationPaths):
    conn = connect_db(paths)
    with pytest.raises(ValueError, match="NO_SAMPLES"):
        append_source_segment(
            paths, conn, source_sha256="i" * 64, source_metadata=_meta(),
            samples=[], normalized_vectors=np.zeros((0, 768), dtype=np.float32),
            expected_dim=768,
        )
    conn.close()


# --- crash tail recovery ---------------------------------------------------


def test_vector_tail_beyond_sqlite_commit_is_truncated_on_writer_resume(paths: GenerationPaths):
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="j" * 64, source_metadata=_meta(),
        samples=_samples(2), normalized_vectors=_vectors(2, seed=80),
        expected_dim=768,
    )
    # simulate a crash between vector fsync and the SQLite commit
    with paths.vectors.open("ab") as fh:
        fh.write(b"\x00" * (2 * ROW_WIDTH))
        fh.flush()
    assert paths.vectors.stat().st_size == 4 * ROW_WIDTH
    reconcile_vector_tail(paths, conn, ROW_WIDTH)
    assert paths.vectors.stat().st_size == 2 * ROW_WIDTH
    assert read_committed_counts(conn) == (2, 2 * ROW_WIDTH)
    conn.close()


def test_reconcile_is_a_noop_when_lengths_agree(paths: GenerationPaths):
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="k" * 64, source_metadata=_meta(),
        samples=_samples(2), normalized_vectors=_vectors(2, seed=90),
        expected_dim=768,
    )
    before = paths.vectors.stat().st_size
    reconcile_vector_tail(paths, conn, ROW_WIDTH)
    assert paths.vectors.stat().st_size == before
    conn.close()


def test_vector_file_shorter_than_committed_length_fails_closed(paths: GenerationPaths):
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="l" * 64, source_metadata=_meta(),
        samples=_samples(3), normalized_vectors=_vectors(3, seed=100),
        expected_dim=768,
    )
    with paths.vectors.open("r+b") as fh:
        fh.truncate(2 * ROW_WIDTH)
    with pytest.raises(ValueError, match="VECTOR_FILE_SHORTER_THAN_COMMITTED"):
        reconcile_vector_tail(paths, conn, ROW_WIDTH)
    conn.close()


def test_committed_bytes_not_divisible_by_row_width_fails_closed(paths: GenerationPaths):
    conn = connect_db(paths)
    with conn:
        conn.execute(
            "UPDATE generation_state SET committed_vector_bytes=?, committed_row_count=0",
            (ROW_WIDTH - 1,),
        )
    with pytest.raises(ValueError, match="COMMITTED_BYTES_NOT_ROW_ALIGNED"):
        reconcile_vector_tail(paths, conn, ROW_WIDTH)
    conn.close()


def test_reader_memmaps_only_sqlite_committed_prefix(paths: GenerationPaths):
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="m" * 64, source_metadata=_meta(),
        samples=_samples(2), normalized_vectors=_vectors(2, seed=110),
        expected_dim=768,
    )
    with paths.vectors.open("ab") as fh:
        fh.write(b"\x00" * ROW_WIDTH)
    import persistent_local_index.storage as storage

    array, close = storage.memmap_committed_prefix(paths, conn, ROW_WIDTH)
    assert array.shape == (2, 768)
    assert paths.vectors.stat().st_size == 3 * ROW_WIDTH, "reader must not mutate the file"
    close()


# --- commit authority / manifest mirror -----------------------------------


def test_sqlite_is_authority_and_manifest_mirror_is_refreshed(paths: GenerationPaths):
    from persistent_local_index.model_space import load_manifest

    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="n" * 64, source_metadata=_meta(),
        samples=_samples(3), normalized_vectors=_vectors(3, seed=120),
        expected_dim=768,
    )
    assert load_manifest(paths.manifest)["committed_rows"] == 3
    conn.close()


def test_stale_lower_manifest_mirror_is_repairable_by_next_writer(paths: GenerationPaths):
    from persistent_local_index.model_space import load_manifest

    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="o" * 64, source_metadata=_meta(),
        samples=_samples(2), normalized_vectors=_vectors(2, seed=130),
        expected_dim=768,
    )
    # simulate a crash after DB commit but before manifest refresh
    import json

    raw = json.loads(paths.manifest.read_text(encoding="utf-8"))
    raw["committed_rows"] = 0
    paths.vectors  # noqa: B018
    paths.manifest.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    assert load_manifest(paths.manifest)["committed_rows"] == 0
    reconcile_vector_tail(paths, conn, ROW_WIDTH)
    assert load_manifest(paths.manifest)["committed_rows"] == 2
    conn.close()


def test_manifest_mirror_larger_than_sqlite_fails_closed(paths: GenerationPaths):
    import json

    conn = connect_db(paths)
    raw = json.loads(paths.manifest.read_text(encoding="utf-8"))
    raw["committed_rows"] = 5
    paths.manifest.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="MANIFEST_COMMITTED_ROWS_AHEAD_OF_SQLITE"):
        reconcile_vector_tail(paths, conn, ROW_WIDTH)
    conn.close()


def test_direct_append_fails_closed_before_mutation_when_manifest_ahead(paths: GenerationPaths):
    import json

    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="a" * 64, source_metadata=_meta(),
        samples=_samples(1), normalized_vectors=_vectors(1, seed=145),
        expected_dim=768,
    )
    # Simulate a manifest that claims more committed data than SQLite, plus a
    # crash tail which append must leave untouched on this inconsistent state.
    raw = json.loads(paths.manifest.read_text(encoding="utf-8"))
    raw["committed_rows"] = 2
    paths.manifest.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    with paths.vectors.open("ab") as handle:
        handle.write(b"tail")
    before_vectors = paths.vectors.read_bytes()
    before_manifest = paths.manifest.read_bytes()
    before_counts = read_committed_counts(conn)
    with pytest.raises(ValueError, match="MANIFEST_COMMITTED_ROWS_AHEAD_OF_SQLITE"):
        append_source_segment(
            paths, conn, source_sha256="b" * 64, source_metadata=_meta(),
            samples=_samples(1, start_pts=900000), normalized_vectors=_vectors(1, seed=146),
            expected_dim=768,
        )
    assert paths.vectors.read_bytes() == before_vectors
    assert read_committed_counts(conn) == before_counts
    assert paths.manifest.read_bytes() == before_manifest
    conn.close()


def test_db_commit_failure_leaves_uncommitted_tail(paths: GenerationPaths):
    """A failed transaction must not advance authority; the tail is truncated later."""
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="p" * 64, source_metadata=_meta(),
        samples=_samples(1), normalized_vectors=_vectors(1, seed=140),
        expected_dim=768,
    )
    before = paths.vectors.stat().st_size
    with paths.vectors.open("ab") as fh:
        fh.write(b"\x00" * ROW_WIDTH)
    assert paths.vectors.stat().st_size == before + ROW_WIDTH
    assert read_committed_counts(conn) == (1, ROW_WIDTH)
    reconcile_vector_tail(paths, conn, ROW_WIDTH)
    assert paths.vectors.stat().st_size == before
    conn.close()


def test_1152_append_commits_4608_bytes_per_row(tmp_path: Path):
    paths = open_or_create_generation(tmp_path / "idx-1152", _spec(1152))
    conn = connect_db(paths)
    vectors = _vectors_dim(2, 1152, seed=900)
    append_source_segment(
        paths, conn, source_sha256="q" * 64, source_metadata=_meta(),
        samples=_samples(2), normalized_vectors=vectors, expected_dim=1152,
    )
    assert read_committed_counts(conn) == (2, 2 * 4608)
    assert paths.vectors.stat().st_size == 2 * 4608
    conn.close()
    reopened = connect_db(open_or_create_generation(tmp_path / "idx-1152", _spec(1152)))
    assert read_committed_counts(reopened) == (2, 2 * 4608)
    assert paths.vectors.stat().st_size == 2 * 4608
    reopened.close()


def test_1152_tail_reconciles_only_uncommitted_bytes(tmp_path: Path):
    paths = open_or_create_generation(tmp_path / "idx-1152", _spec(1152))
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="r" * 64, source_metadata=_meta(),
        samples=_samples(2), normalized_vectors=_vectors_dim(2, 1152, seed=910),
        expected_dim=1152,
    )
    committed_prefix = paths.vectors.read_bytes()
    with paths.vectors.open("ab") as handle:
        handle.write(b"tail" * 17)
    reconcile_vector_tail(paths, conn, 1152 * 4)
    assert paths.vectors.read_bytes() == committed_prefix
    assert read_committed_counts(conn) == (2, 2 * 4608)
    conn.close()


def test_1152_wrong_width_rejected_before_write(tmp_path: Path):
    paths = open_or_create_generation(tmp_path / "idx-1152", _spec(1152))
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="u" * 64, source_metadata=_meta(),
        samples=_samples(1), normalized_vectors=_vectors_dim(1, 1152, seed=919),
        expected_dim=1152,
    )
    committed_prefix = paths.vectors.read_bytes()
    with pytest.raises(ValueError, match="VECTOR_SHAPE"):
        append_source_segment(
            paths, conn, source_sha256="s" * 64, source_metadata=_meta(),
            samples=_samples(2), normalized_vectors=_vectors(2, seed=920),
            expected_dim=1152,
        )
    assert read_committed_counts(conn) == (1, 4608)
    assert paths.vectors.read_bytes() == committed_prefix
    conn.close()


def test_768_legacy_append_and_restart_preserved(tmp_path: Path):
    paths = open_or_create_generation(tmp_path / "idx-768", _spec(768))
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="t" * 64, source_metadata=_meta(),
        samples=_samples(1), normalized_vectors=_vectors(1, seed=930),
        expected_dim=768,
    )
    conn.close()
    reopened = connect_db(open_or_create_generation(tmp_path / "idx-768", _spec(768)))
    assert read_committed_counts(reopened) == (1, ROW_WIDTH)
    assert paths.vectors.stat().st_size == ROW_WIDTH
    reopened.close()


def test_append_expected_dim_must_match_persisted_generation(tmp_path: Path):
    paths = open_or_create_generation(tmp_path / "idx-1152", _spec(1152))
    conn = connect_db(paths)
    with pytest.raises(ValueError, match="GENERATION_DIMENSION_MISMATCH"):
        append_source_segment(
            paths, conn, source_sha256="v" * 64, source_metadata=_meta(),
            samples=_samples(1), normalized_vectors=_vectors(1, seed=940),
            expected_dim=768,
        )
    assert read_committed_counts(conn) == (0, 0)
    assert paths.vectors.stat().st_size == 0
    conn.close()


def test_append_rejects_committed_row_byte_mismatch_before_truncating(tmp_path: Path):
    paths = open_or_create_generation(tmp_path / "idx-1152", _spec(1152))
    conn = connect_db(paths)
    append_source_segment(
        paths, conn, source_sha256="w" * 64, source_metadata=_meta(),
        samples=_samples(1), normalized_vectors=_vectors_dim(1, 1152, seed=950),
        expected_dim=1152,
    )
    with conn:
        conn.execute(
            "UPDATE generation_state SET committed_vector_bytes=? WHERE singleton=1",
            (2 * 1152 * 4,),
        )
    with paths.vectors.open("ab") as handle:
        handle.write(b"uncommitted-tail" * 512)
    file_before = paths.vectors.read_bytes()
    with pytest.raises(ValueError, match="COMMITTED_ROWS_BYTES_DISAGREE"):
        append_source_segment(
            paths, conn, source_sha256="x" * 64, source_metadata=_meta(),
            samples=_samples(1), normalized_vectors=_vectors_dim(1, 1152, seed=960),
            expected_dim=1152,
        )
    assert read_committed_counts(conn) == (1, 2 * 1152 * 4)
    assert paths.vectors.read_bytes() == file_before
    conn.close()
