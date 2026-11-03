"""SQLite lifecycle store, fixed-width vector file, and crash-tail recovery.

Authority: approved design sections 5, 8, 9, 14 and plan Task 2.

Central invariant: **SQLite is authoritative for mutable commit state.**  It stores
the committed row count and the committed vector byte length.  Bytes in
``vectors.f32`` beyond the committed byte length are an interrupted/uncommitted
tail: they are never searchable and are truncated only by the controlled
single-writer resume path.  ``manifest.json`` mirrors ``committed_rows`` for
human inspection but is not the authority.
"""
from __future__ import annotations

import fcntl
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

from persistent_local_index.model_space import (
    GenerationSpec,
    _SPACE_FIELDS,
    generation_spec_from_manifest,
    load_manifest,
    read_manifest_committed_rows,
    semantic_space_id,
    validate_manifest_compatibility,
    write_manifest,
)

#: L2-normalized rows must sit on the unit sphere; allow only float32 tolerance.
_UNIT_NORM_TOLERANCE = 1e-4

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS generation_state (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    generation_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    space_id TEXT NOT NULL,
    sampling_policy_id TEXT NOT NULL,
    sampling_policy_version INTEGER NOT NULL,
    sampling_interval_seconds REAL NOT NULL,
    committed_row_count INTEGER NOT NULL,
    committed_vector_bytes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS source_objects (
    source_sha256 TEXT PRIMARY KEY,
    source_revision TEXT,
    size_bytes INTEGER NOT NULL,
    stream_index INTEGER NOT NULL,
    codec TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    timebase_num INTEGER NOT NULL,
    timebase_den INTEGER NOT NULL,
    duration_seconds REAL,
    state TEXT NOT NULL CHECK (state IN ('IN_PROGRESS','COMPLETE','FAILED','SUPERSEDED')),
    row_start INTEGER,
    row_end INTEGER,
    indexed_at TEXT,
    active INTEGER NOT NULL CHECK (active IN (0,1))
);

CREATE TABLE IF NOT EXISTS source_locations (
    path TEXT PRIMARY KEY,
    source_sha256 TEXT NOT NULL REFERENCES source_objects(source_sha256),
    last_observed_size INTEGER NOT NULL,
    last_observed_mtime_ns INTEGER NOT NULL,
    last_observed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS samples (
    row_id INTEGER PRIMARY KEY,
    source_sha256 TEXT NOT NULL REFERENCES source_objects(source_sha256),
    stream_index INTEGER NOT NULL,
    pts INTEGER NOT NULL,
    timebase_num INTEGER NOT NULL,
    timebase_den INTEGER NOT NULL,
    pts_time REAL NOT NULL,
    timestamp_human TEXT NOT NULL,
    thumbnail_relpath TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0,1))
);

CREATE INDEX IF NOT EXISTS samples_source_idx ON samples(source_sha256);
CREATE INDEX IF NOT EXISTS samples_active_idx ON samples(active, row_id);
CREATE INDEX IF NOT EXISTS source_locations_sha_idx ON source_locations(source_sha256);
"""

_GENERATION_STATE_COLUMNS = (
    "generation_id",
    "schema_version",
    "space_id",
    "sampling_policy_id",
    "sampling_policy_version",
    "sampling_interval_seconds",
    "committed_row_count",
    "committed_vector_bytes",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class GenerationPaths:
    root: Path
    manifest: Path
    database: Path
    vectors: Path
    thumbs: Path
    staging: Path
    lock: Path


@dataclass(frozen=True)
class PersistedSample:
    """One sample's measured temporal provenance plus its staged thumbnail."""

    pts: int
    timebase_num: int
    timebase_den: int
    pts_time: float
    timestamp_human: str
    thumbnail_stage_path: Path


def generation_paths(generation_root: Path) -> GenerationPaths:
    root = Path(generation_root)
    return GenerationPaths(
        root=root,
        manifest=root / "manifest.json",
        database=root / "index.sqlite",
        vectors=root / "vectors.f32",
        thumbs=root / "thumbs",
        staging=root / "staging",
        lock=root / "writer.lock",
    )


def open_or_create_generation(index_root: Path, spec: GenerationSpec) -> GenerationPaths:
    """Create or resume exactly the generation ``spec`` identifies.

    The index root is explicitly supplied by the operator and is never inferred
    from the source-media tree.  An existing generation whose manifest pins a
    different generation/space fails closed rather than being reused.
    """
    index_root = Path(index_root)
    generations_dir = index_root / "generations"
    generation_root = generations_dir / spec.generation_id
    paths = generation_paths(generation_root)
    for directory in (generation_root, paths.thumbs, paths.staging):
        directory.mkdir(parents=True, exist_ok=True)

    if paths.manifest.is_file():
        # Validate BEFORE touching the database so a foreign generation cannot
        # be silently adopted.
        manifest = load_manifest(paths.manifest)
        validate_manifest_compatibility(manifest, spec)
    else:
        # A different generation_id is expected when the semantic space or
        # sampling policy changes (that is the point of generation identity).
        # What must fail closed is reusing THIS index root for a generation whose
        # existing manifests pin an incompatible space under a sibling id: v1
        # never mixes generations and never migrates automatically.
        _reject_sibling_generation_with_other_space(generations_dir, spec)
        write_manifest(paths.manifest, spec, committed_rows=0)

    paths.vectors.touch(exist_ok=True)
    paths.lock.touch(exist_ok=True)

    conn = connect_db(paths)
    try:
        with conn:
            _ensure_generation_state(conn, spec)
    finally:
        conn.close()
    return paths


def _reject_sibling_generation_with_other_space(
    generations_dir: Path, spec: GenerationSpec
) -> None:
    """Refuse to open a new generation in an index root that pins another space.

    v1 has no cross-generation mixing and no automatic migration.  A semantic
    space change requires a new generation *and* an explicit operator decision
    about the index root; silently creating a sibling generation that a query
    could never legally join is not useful, so this fails closed and names the
    conflicting field.
    """
    if not generations_dir.is_dir():
        return
    for candidate in sorted(generations_dir.iterdir()):
        manifest_path = candidate / "manifest.json"
        if not manifest_path.is_file():
            continue
        existing = load_manifest(manifest_path)
        if existing.get("generation_id") == spec.generation_id:
            continue
        existing_space = existing.get("space")
        if not isinstance(existing_space, Mapping):
            raise ValueError("MANIFEST_SPACE_NOT_OBJECT")
        for field in _SPACE_FIELDS:
            if existing_space.get(field) != getattr(spec.space, field):
                raise ValueError(
                    f"SEMANTIC_SPACE_MISMATCH:{field}:"
                    f"expected={getattr(spec.space, field)!r}:"
                    f"existing={existing_space.get(field)!r}"
                )
        raise ValueError(
            f"GENERATION_MISMATCH:generation_id:expected={spec.generation_id!r}:"
            f"existing={existing.get('generation_id')!r}"
        )


def _ensure_generation_state(conn: sqlite3.Connection, spec: GenerationSpec) -> None:
    row = conn.execute(
        "SELECT generation_id, space_id FROM generation_state WHERE singleton=1"
    ).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO generation_state ("
            "singleton, generation_id, schema_version, space_id, sampling_policy_id,"
            " sampling_policy_version, sampling_interval_seconds, committed_row_count,"
            " committed_vector_bytes) VALUES (1,?,?,?,?,?,?,0,0)",
            (
                spec.generation_id,
                spec.schema_version,
                spec.space_id,
                spec.sampling_policy_id,
                spec.sampling_policy_version,
                spec.sampling_interval_seconds,
            ),
        )
        return
    if row[0] != spec.generation_id:
        raise ValueError(
            f"GENERATION_MISMATCH:generation_id:expected={spec.generation_id!r}:found={row[0]!r}"
        )
    if row[1] != spec.space_id:
        raise ValueError(
            f"GENERATION_MISMATCH:space_id:expected={spec.space_id!r}:found={row[1]!r}"
        )


def connect_db(paths: GenerationPaths, *, readonly: bool = False) -> sqlite3.Connection:
    """Open the generation database.  A read-only open never mutates schema."""
    if readonly:
        uri = f"file:{paths.database}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    conn = sqlite3.connect(str(paths.database))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


# --------------------------------------------------------------------------
# single-writer lock
# --------------------------------------------------------------------------


class WriterLock:
    """Exclusive advisory writer lock.  A second writer fails closed."""

    def __init__(self, lock_path: Path):
        self._path = Path(lock_path)
        self._fd: int | None = None

    def __enter__(self) -> "WriterLock":
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self._path), os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise RuntimeError("CONCURRENT_WRITER") from exc
        self._fd = fd
        return self

    def __exit__(self, *exc_info) -> None:
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
            finally:
                os.close(self._fd)
                self._fd = None


# --------------------------------------------------------------------------
# committed state
# --------------------------------------------------------------------------


def read_committed_counts(conn: sqlite3.Connection) -> tuple[int, int]:
    """Read SQLite's authoritative ``(committed_row_count, committed_vector_bytes)``."""
    row = conn.execute(
        "SELECT committed_row_count, committed_vector_bytes FROM generation_state "
        "WHERE singleton=1"
    ).fetchone()
    if row is None:
        raise ValueError("GENERATION_STATE_MISSING")
    return int(row[0]), int(row[1])


def read_generation_state(conn: sqlite3.Connection) -> Mapping[str, object]:
    row = conn.execute("SELECT * FROM generation_state WHERE singleton=1").fetchone()
    if row is None:
        raise ValueError("GENERATION_STATE_MISSING")
    return dict(row)


def require_committed_geometry(
    committed_rows: int, committed_bytes: int, row_width_bytes: int
) -> None:
    """Fail closed unless SQLite's committed row and byte counts describe one prefix.

    SQLite is the commit authority for BOTH counts, so they must agree.  A
    reader that memmaps ``committed_rows`` rows without this check can read past
    EOF or past the committed prefix (exposing uncommitted or unrelated bytes),
    so the writer and read paths share this single invariant.
    """
    if committed_rows < 0 or committed_bytes < 0:
        raise ValueError(
            f"COMMITTED_COUNTS_NEGATIVE:rows={committed_rows}:bytes={committed_bytes}"
        )
    if row_width_bytes <= 0 or committed_bytes % row_width_bytes != 0:
        raise ValueError(
            f"COMMITTED_BYTES_NOT_ROW_ALIGNED:{committed_bytes}:{row_width_bytes}"
        )
    if committed_bytes != committed_rows * row_width_bytes:
        raise ValueError(
            f"COMMITTED_ROWS_BYTES_DISAGREE:rows={committed_rows}:bytes={committed_bytes}"
        )


def reconcile_vector_tail(
    paths: GenerationPaths, conn: sqlite3.Connection, row_width_bytes: int
) -> tuple[int, int]:
    """Repair the uncommitted vector tail and stale manifest mirror.

    Order of checks (fail closed before any mutation):

    1. committed rows and bytes agree on one row width;
    2. manifest mirror not *ahead* of SQLite;
    3. physical file not *shorter* than committed bytes;
    4. truncate any physical excess to the committed byte length and fsync.

    A stale (lower) manifest mirror is informational and is repaired.
    """
    committed_rows, committed_bytes = read_committed_counts(conn)
    require_committed_geometry(committed_rows, committed_bytes, row_width_bytes)

    manifest = load_manifest(paths.manifest)
    mirror = read_manifest_committed_rows(manifest)
    if mirror > committed_rows:
        raise ValueError(
            f"MANIFEST_COMMITTED_ROWS_AHEAD_OF_SQLITE:{mirror}>{committed_rows}"
        )

    physical = paths.vectors.stat().st_size if paths.vectors.exists() else 0
    if physical < committed_bytes:
        raise ValueError(
            f"VECTOR_FILE_SHORTER_THAN_COMMITTED:{physical}<{committed_bytes}"
        )
    if physical > committed_bytes:
        with paths.vectors.open("r+b") as handle:
            handle.truncate(committed_bytes)
            handle.flush()
            os.fsync(handle.fileno())

    if mirror != committed_rows:
        _write_manifest_mirror_from_paths(paths, conn, committed_rows)

    return committed_rows, committed_bytes


# --------------------------------------------------------------------------
# append
# --------------------------------------------------------------------------


def _validate_vectors(
    normalized_vectors: np.ndarray, expected_rows: int, *, expected_dim: int
) -> np.ndarray:
    array = np.asarray(normalized_vectors)
    if type(expected_dim) is not int or expected_dim <= 0:
        raise ValueError(f"VECTOR_DIM_INVALID:{expected_dim}")
    if array.ndim != 2 or array.shape[1] != expected_dim:
        raise ValueError(f"VECTOR_SHAPE:{array.shape}")
    if array.shape[0] != expected_rows:
        raise ValueError(f"VECTOR_SHAPE:rows={array.shape[0]}:samples={expected_rows}")
    if array.dtype != np.float32:
        raise ValueError(f"VECTOR_DTYPE:{array.dtype}")
    if not np.isfinite(array).all():
        raise ValueError("VECTOR_NON_FINITE")
    norms = np.linalg.norm(array, axis=1)
    if not np.allclose(norms, 1.0, atol=_UNIT_NORM_TOLERANCE, rtol=0):
        raise ValueError(f"VECTOR_NOT_UNIT_NORM:max_deviation={float(np.abs(norms - 1).max())}")
    return np.ascontiguousarray(array, dtype=np.float32)


def _validate_generation_dimension(
    paths: GenerationPaths, conn: sqlite3.Connection, expected_dim: int
) -> int:
    manifest = load_manifest(paths.manifest)
    spec = generation_spec_from_manifest(manifest)
    state = read_generation_state(conn)
    if (
        state["generation_id"] != spec.generation_id
        or state["space_id"] != spec.space_id
        or semantic_space_id(spec.space) != spec.space_id
    ):
        raise ValueError("GENERATION_MANIFEST_STATE_MISMATCH")
    if spec.space.dtype != "float32":
        raise ValueError(f"VECTOR_DTYPE_UNSUPPORTED:{spec.space.dtype}")
    generation_dim = spec.space.embedding_dim
    if type(generation_dim) is not int or generation_dim <= 0:
        raise ValueError(f"VECTOR_DIM_INVALID:{generation_dim}")
    if expected_dim != generation_dim:
        raise ValueError(
            f"GENERATION_DIMENSION_MISMATCH:expected={generation_dim}:found={expected_dim}"
        )
    return generation_dim


def append_source_segment(
    paths: GenerationPaths,
    conn: sqlite3.Connection,
    *,
    source_sha256: str,
    source_metadata: Mapping[str, object],
    samples: Sequence[PersistedSample],
    normalized_vectors: np.ndarray,
    expected_dim: int,
    stream_index: int | None = None,
) -> tuple[int, int]:
    """Append one source's vectors and commit its provenance in one transaction.

    Returns the half-open ``[row_start, row_end)`` range of the new rows.
    """
    generation_dim = _validate_generation_dimension(paths, conn, expected_dim)
    if not samples:
        raise ValueError("NO_SAMPLES")
    vectors = _validate_vectors(
        normalized_vectors, len(samples), expected_dim=generation_dim
    )
    row_width = vectors.shape[1] * vectors.dtype.itemsize

    committed_rows, committed_bytes = read_committed_counts(conn)
    require_committed_geometry(committed_rows, committed_bytes, row_width)

    mirror = read_manifest_committed_rows(load_manifest(paths.manifest))
    if mirror > committed_rows:
        raise ValueError(
            f"MANIFEST_COMMITTED_ROWS_AHEAD_OF_SQLITE:{mirror}>{committed_rows}"
        )

    physical = paths.vectors.stat().st_size if paths.vectors.exists() else 0
    if physical < committed_bytes:
        raise ValueError(f"VECTOR_FILE_SHORTER_THAN_COMMITTED:{physical}<{committed_bytes}")
    if physical > committed_bytes:
        with paths.vectors.open("r+b") as handle:
            handle.truncate(committed_bytes)
            handle.flush()
            os.fsync(handle.fileno())

    payload = vectors.tobytes(order="C")
    with paths.vectors.open("ab") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())

    row_start = committed_rows
    row_end = committed_rows + len(samples)
    new_bytes = committed_bytes + len(payload)
    stream = int(stream_index if stream_index is not None else source_metadata["stream_index"])

    # One transaction: provenance + authoritative counts advance together.
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO source_objects ("
            "source_sha256, source_revision, size_bytes, stream_index, codec, width, height,"
            " timebase_num, timebase_den, duration_seconds, state, row_start, row_end,"
            " indexed_at, active) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)",
            (
                source_sha256,
                source_metadata.get("source_revision"),
                int(source_metadata["size_bytes"]),
                stream,
                str(source_metadata["codec"]),
                int(source_metadata["width"]),
                int(source_metadata["height"]),
                int(source_metadata["timebase_num"]),
                int(source_metadata["timebase_den"]),
                source_metadata.get("duration_seconds"),
                "COMPLETE",
                row_start,
                row_end,
                _utc_now(),
            ),
        )
        conn.executemany(
            "INSERT OR REPLACE INTO samples ("
            "row_id, source_sha256, stream_index, pts, timebase_num, timebase_den, pts_time,"
            " timestamp_human, thumbnail_relpath, active) VALUES (?,?,?,?,?,?,?,?,?,1)",
            [
                (
                    row_start + offset,
                    source_sha256,
                    stream,
                    int(sample.pts),
                    int(sample.timebase_num),
                    int(sample.timebase_den),
                    float(sample.pts_time),
                    sample.timestamp_human,
                    f"thumbs/{row_start + offset}.jpg",
                )
                for offset, sample in enumerate(samples)
            ],
        )
        conn.execute(
            "UPDATE generation_state SET committed_row_count=?, committed_vector_bytes=? "
            "WHERE singleton=1",
            (row_end, new_bytes),
        )

    # Mirror refresh happens strictly after the DB commit; a crash in between
    # leaves a stale-lower mirror that the next writer repairs.
    _write_manifest_mirror_from_paths(paths, conn, row_end)
    return row_start, row_end


def _write_manifest_mirror_from_paths(
    paths: GenerationPaths, conn: sqlite3.Connection, committed_rows: int
) -> None:
    """Atomically refresh only the informational manifest committed-row mirror.

    The manifest's immutable semantic/sampling identity is read back and reused
    verbatim, so a mirror refresh can never rewrite generation identity.
    """
    manifest = load_manifest(paths.manifest)
    spec = generation_spec_from_manifest(manifest)
    write_manifest(paths.manifest, spec, committed_rows)


def memmap_committed_prefix(
    paths: GenerationPaths, conn: sqlite3.Connection, row_width_bytes: int
) -> tuple[np.memmap, "object"]:
    """Read-only memmap of exactly the SQLite-committed vector prefix.

    Never mutates the file; a physical file longer than the commit is truncated
    only by :func:`reconcile_vector_tail` on the writer path.
    """
    committed_rows, committed_bytes = read_committed_counts(conn)
    require_committed_geometry(committed_rows, committed_bytes, row_width_bytes)
    physical = paths.vectors.stat().st_size
    if physical < committed_bytes:
        raise ValueError(f"VECTOR_FILE_SHORTER_THAN_COMMITTED:{physical}<{committed_bytes}")
    columns = row_width_bytes // 4
    if committed_rows == 0:
        empty = np.zeros((0, columns), dtype="<f4")
        return empty, lambda: None
    handle = paths.vectors.open("rb")
    try:
        array = np.memmap(
            handle, dtype="<f4", mode="r", shape=(committed_rows, columns)
        )
    except BaseException:
        handle.close()
        raise

    # The memmap owns a reference to `handle`; drop both explicitly so the
    # mapping is released deterministically (and never while still in use).
    holder = [array]

    def _close() -> None:
        holder.clear()
        handle.close()

    return array, _close
