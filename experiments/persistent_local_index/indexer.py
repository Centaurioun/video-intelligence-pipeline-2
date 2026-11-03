"""Discovery, digest reuse/change logic, staging, per-source commit and resume.

Authority: approved design sections 7, 8, 13.1 and plan Task 5.

v1 uses exactly **one writer** for the whole indexing invocation.  Within that
lock, a stale vector tail / stale manifest mirror is repaired before any source
is processed, and every expensive step (decode, thumbnail, embedding) is serial.

Per-source ordering (design section 8) is preserved exactly:

1. copy the locator into a private source snapshot and compute its SHA-256;
2. probe stream metadata without full-frame enumeration from that snapshot;
3. one-pass measured-PTS sampling into source staging from that snapshot;
4. thumbnails in source staging;
5. local image embeddings, L2-normalized;
6. append staged vector bytes to ``vectors.f32`` and fsync;
7. in ONE SQLite transaction: insert samples, record ``[row_start,row_end)``,
   advance committed counts, move the location association, promote COMPLETE,
   and recompute old-digest activity;
8. atomically refresh the manifest committed-row mirror;
9. publish thumbnails via ``os.replace``;
10. remove staging.

A thumbnail publication failure after commit leaves the source COMPLETE, because
a missing thumbnail is a regenerable cache defect, not evidence rollback.
"""
from __future__ import annotations

import os
import shutil
import traceback
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence

import numpy as np

from persistent_local_index.media import (
    make_thumbnail,
    probe_stream,
    sample_one_pass,
    sha256_file,
)
from persistent_local_index.model_space import GenerationSpec
from persistent_local_index.storage import (
    GenerationPaths,
    PersistedSample,
    WriterLock,
    append_source_segment,
    connect_db,
    open_or_create_generation,
    reconcile_vector_tail,
)

#: Only these container extensions are discovered.  Never widen implicitly.
ALLOWED_EXTENSIONS = (".mp4", ".mov", ".m4v", ".mkv")


def _row_width_bytes(spec: GenerationSpec) -> int:
    if spec.space.dtype != "float32":
        raise ValueError(f"VECTOR_DTYPE_UNSUPPORTED:{spec.space.dtype}")
    if type(spec.space.embedding_dim) is not int or spec.space.embedding_dim <= 0:
        raise ValueError(f"VECTOR_DIM_INVALID:{spec.space.embedding_dim}")
    return spec.space.embedding_dim * np.dtype(np.float32).itemsize


@dataclass(frozen=True)
class SourceIndexResult:
    path: str
    source_sha256: str
    disposition: str  # INDEXED / SKIPPED_UNCHANGED / REUSED_DUPLICATE / FAILED
    row_start: int | None
    row_end: int | None
    error: str | None


@dataclass(frozen=True)
class IndexSummary:
    generation_id: str
    indexed: int
    skipped: int
    reused: int
    failed: int
    results: tuple[SourceIndexResult, ...]


@dataclass(frozen=True)
class LocationRemovalResult:
    source_path: Path
    removed: bool
    source_sha256: str | None
    object_superseded: bool


@dataclass(frozen=True)
class _LocatorObservation:
    """Captured last-observed locator occurrence, separate from snapshot bytes."""

    source_path: Path
    source_sha256: str
    last_observed_size: int
    last_observed_mtime_ns: int
    last_observed_at: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover_inputs(input_path: Path) -> tuple[Path, ...]:
    """Deterministic authorized discovery.

    A file input indexes only that exact file.  A directory input recursively
    enumerates regular files with an allowlisted extension, sorted by UTF-8 path
    bytes.  Symlinked directories are never followed and the search never leaves
    the supplied root.
    """
    input_path = Path(input_path)
    if input_path.is_file():
        return (input_path,)
    if not input_path.is_dir():
        raise ValueError(f"INPUT_NOT_FOUND:{input_path}")
    root = input_path.resolve()
    found: list[Path] = []
    for directory, subdirectories, filenames in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        # Prune symlinked directories explicitly: never traverse outside root.
        subdirectories[:] = sorted(
            name
            for name in subdirectories
            if not (directory_path / name).is_symlink()
        )
        for name in filenames:
            candidate = directory_path / name
            if candidate.is_symlink() or not candidate.is_file():
                continue
            if candidate.suffix.lower() in ALLOWED_EXTENSIONS:
                found.append(candidate)
    found.sort(key=lambda p: str(p).encode("utf-8"))
    return tuple(found)


# --------------------------------------------------------------------------
# per-source lifecycle
# --------------------------------------------------------------------------


def _source_metadata(video: Path, stream) -> dict[str, object]:
    return {
        "size_bytes": video.stat().st_size,
        "stream_index": stream.stream_index,
        "codec": stream.codec,
        "width": stream.width,
        "height": stream.height,
        "timebase_num": stream.timebase_num,
        "timebase_den": stream.timebase_den,
        "duration_seconds": stream.duration_seconds,
        "source_revision": None,
    }


def _source_stat_fingerprint(video: Path) -> tuple[int, int, int, int, int]:
    """Return metadata used to detect replacement and transient in-place writes.

    ctime is filesystem supplied; filesystems with coarse ctime resolution can
    miss multiple writes within one timestamp tick, so the digest check remains
    necessary and metadata is a supplementary mutation guard.
    """
    stat = video.stat()
    return (
        stat.st_dev,
        stat.st_ino,
        stat.st_size,
        stat.st_mtime_ns,
        stat.st_ctime_ns,
    )


def _copy_source_snapshot(
    locator: Path, snapshot: Path
) -> tuple[_LocatorObservation, tuple[int, int, int, int, int]]:
    """Capture bytes privately and record metadata observed around that copy."""
    locator = Path(locator)
    snapshot = Path(snapshot)
    before = _source_stat_fingerprint(locator)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    with locator.open("rb") as source, snapshot.open("wb") as destination:
        shutil.copyfileobj(source, destination, length=1024 * 1024)
        destination.flush()
        os.fsync(destination.fileno())
    after = _source_stat_fingerprint(locator)
    if after != before:
        raise ValueError("SOURCE_CHANGED_DURING_SNAPSHOT")

    source_sha256 = sha256_file(snapshot)
    observation = _LocatorObservation(
        source_path=locator,
        source_sha256=source_sha256,
        last_observed_size=after[2],
        last_observed_mtime_ns=after[3],
        last_observed_at=_utc_now(),
    )
    return observation, before


def _check_locator_for_change_detection(
    observation: _LocatorObservation,
    initial_fingerprint: tuple[int, int, int, int, int],
) -> None:
    """Best-effort change detection only; it does not make SQLite atomic."""
    locator = observation.source_path
    if (
        _source_stat_fingerprint(locator) != initial_fingerprint
        or sha256_file(locator) != observation.source_sha256
    ):
        raise ValueError("SOURCE_CHANGED_DURING_INDEXING")


def index_one_source(
    video: Path,
    generation: GenerationPaths,
    spec: GenerationSpec,
    image_embedder: Callable[[Sequence[Path]], np.ndarray],
) -> SourceIndexResult:
    """Index one source, or explain why it was skipped/reused/failed."""
    video = Path(video)
    display_path = str(video)
    source_sha256 = ""
    staging = generation.staging / f"source-{uuid.uuid4().hex[:12]}"
    try:
        row_width_bytes = _row_width_bytes(spec)
        staging.mkdir(parents=True, exist_ok=True)
        observation, initial_fingerprint = _copy_source_snapshot(
            video, staging / "source.snapshot"
        )
        source_sha256 = observation.source_sha256
        snapshot = staging / "source.snapshot"

        conn = connect_db(generation)
        try:
            reconcile_vector_tail(generation, conn, row_width_bytes)
            existing = conn.execute(
                "SELECT state, row_start, row_end, active FROM source_objects WHERE source_sha256=?",
                (source_sha256,),
            ).fetchone()
            if existing is not None and existing["state"] == "COMPLETE":
                disposition = (
                    "REUSED_DUPLICATE"
                    if _is_new_location(conn, video, source_sha256)
                    else "SKIPPED_UNCHANGED"
                )
                # This bounded recheck detects changes observed before association.
                # A change after it and before SQLite commit remains possible.
                _check_locator_for_change_detection(observation, initial_fingerprint)
                with conn:
                    _upsert_location(conn, observation)
                return SourceIndexResult(
                    display_path, source_sha256, disposition,
                    int(existing["row_start"]), int(existing["row_end"]), None,
                )
        finally:
            conn.close()

        stream = probe_stream(snapshot)
        frames = sample_one_pass(snapshot, spec.sampling_interval_seconds, staging / "frames")
        if not frames:
            raise ValueError("NO_SAMPLES")

        thumbnail_paths: list[Path] = []
        samples: list[PersistedSample] = []
        for index, frame in enumerate(frames):
            thumbnail = staging / "thumbs" / f"{index:06d}.jpg"
            make_thumbnail(frame.image_path, thumbnail)
            thumbnail_paths.append(thumbnail)
            samples.append(
                PersistedSample(
                    pts=frame.pts,
                    timebase_num=frame.timebase_num,
                    timebase_den=frame.timebase_den,
                    pts_time=frame.pts_time,
                    timestamp_human=frame.timestamp_human,
                    thumbnail_stage_path=thumbnail,
                )
            )

        vectors = np.asarray(image_embedder([f.image_path for f in frames]))

        conn = connect_db(generation)
        try:
            # The external recheck is change detection only, not an atomic
            # binding between the locator and the SQLite commit.
            _check_locator_for_change_detection(observation, initial_fingerprint)
            _mark_in_progress(conn, snapshot, source_sha256, stream)
            reconcile_vector_tail(generation, conn, row_width_bytes)
            row_start, row_end = append_source_segment(
                generation,
                conn,
                source_sha256=source_sha256,
                source_metadata=_source_metadata(snapshot, stream),
                samples=samples,
                normalized_vectors=vectors,
                expected_dim=spec.space.embedding_dim,
                stream_index=stream.stream_index,
            )
            with conn:
                _upsert_location(conn, observation)
                _supersede_unreferenced_objects(conn, source_sha256)
        finally:
            conn.close()

        _publish_thumbnails(generation, row_start, thumbnail_paths)
        return SourceIndexResult(display_path, source_sha256, "INDEXED", row_start, row_end, None)
    except Exception as exc:  # noqa: BLE001 - a per-source failure must not abort the run
        try:
            _record_failure(generation, video, source_sha256, exc)
        except Exception:  # failure recording must not replace the source failure
            pass
        error = f"{type(exc).__name__}:{exc}"
        if len(error) > 500:
            error = error[:497] + "..."
        return SourceIndexResult(
            display_path, source_sha256, "FAILED", None, None, error
        )
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _is_new_location(conn, video: Path, source_sha256: str) -> bool:
    row = conn.execute(
        "SELECT source_sha256 FROM source_locations WHERE path=?", (str(video),)
    ).fetchone()
    return row is None or row[0] != source_sha256


def _upsert_location(conn, observation: _LocatorObservation) -> None:
    conn.execute(
        "INSERT INTO source_locations (path, source_sha256, last_observed_size,"
        " last_observed_mtime_ns, last_observed_at) VALUES (?,?,?,?,?)"
        " ON CONFLICT(path) DO UPDATE SET source_sha256=excluded.source_sha256,"
        " last_observed_size=excluded.last_observed_size,"
        " last_observed_mtime_ns=excluded.last_observed_mtime_ns,"
        " last_observed_at=excluded.last_observed_at",
        (
            str(observation.source_path),
            observation.source_sha256,
            observation.last_observed_size,
            observation.last_observed_mtime_ns,
            observation.last_observed_at,
        ),
    )


def remove_source_location(
    index_root: Path, spec: GenerationSpec, source_path: Path
) -> LocationRemovalResult:
    """Remove the exact stored path association without touching vector data.

    The path key intentionally matches ``_upsert_location``'s ``str(Path)``
    convention. Location and last-reference lifecycle changes commit together
    under the generation's existing single-writer lock.
    """
    source_path = Path(source_path)
    generation = open_or_create_generation(index_root, spec)
    with WriterLock(generation.lock):
        conn = connect_db(generation)
        try:
            with conn:
                location = conn.execute(
                    "SELECT source_sha256 FROM source_locations WHERE path=?",
                    (str(source_path),),
                ).fetchone()
                if location is None:
                    return LocationRemovalResult(source_path, False, None, False)

                source_sha256 = str(location["source_sha256"])
                conn.execute(
                    "DELETE FROM source_locations WHERE path=?", (str(source_path),)
                )
                remaining = conn.execute(
                    "SELECT 1 FROM source_locations WHERE source_sha256=? LIMIT 1",
                    (source_sha256,),
                ).fetchone()
                obj = conn.execute(
                    "SELECT state FROM source_objects WHERE source_sha256=?",
                    (source_sha256,),
                ).fetchone()
                superseded = (
                    remaining is None
                    and obj is not None
                    and obj["state"] == "COMPLETE"
                )
                if superseded:
                    conn.execute(
                        "UPDATE source_objects SET state='SUPERSEDED', active=0 "
                        "WHERE source_sha256=? AND state='COMPLETE'",
                        (source_sha256,),
                    )
                    conn.execute(
                        "UPDATE samples SET active=0 WHERE source_sha256=?",
                        (source_sha256,),
                    )
            return LocationRemovalResult(source_path, True, source_sha256, superseded)
        finally:
            conn.close()


def _mark_in_progress(conn, video: Path, source_sha256: str, stream) -> None:
    """Record/refresh IN_PROGRESS WITHOUT moving an existing path association."""
    metadata = _source_metadata(video, stream)
    with conn:
        conn.execute(
            "INSERT INTO source_objects (source_sha256, source_revision, size_bytes,"
            " stream_index, codec, width, height, timebase_num, timebase_den,"
            " duration_seconds, state, active) VALUES (?,?,?,?,?,?,?,?,?,?, 'IN_PROGRESS', 0)"
            " ON CONFLICT(source_sha256) DO UPDATE SET"
            " size_bytes=excluded.size_bytes, stream_index=excluded.stream_index,"
            " codec=excluded.codec, width=excluded.width, height=excluded.height,"
            " timebase_num=excluded.timebase_num, timebase_den=excluded.timebase_den,"
            " duration_seconds=excluded.duration_seconds,"
            " state=CASE WHEN source_objects.state='COMPLETE' THEN 'COMPLETE' ELSE 'IN_PROGRESS' END",
            (
                source_sha256,
                metadata["source_revision"],
                metadata["size_bytes"],
                metadata["stream_index"],
                metadata["codec"],
                metadata["width"],
                metadata["height"],
                metadata["timebase_num"],
                metadata["timebase_den"],
                metadata["duration_seconds"],
            ),
        )


def _supersede_unreferenced_objects(conn, current_sha256: str) -> None:
    """Deactivate any COMPLETE object with no remaining location reference.

    An old digest stays active (and its rows stay searchable) as long as some
    currently active source location still refers to it.
    """
    conn.execute(
        "UPDATE source_objects SET state='SUPERSEDED', active=0"
        " WHERE state='COMPLETE' AND active=1"
        "   AND source_sha256 NOT IN (SELECT source_sha256 FROM source_locations)"
        "   AND source_sha256 != ?",
        (current_sha256,),
    )
    conn.execute(
        "UPDATE samples SET active=0 WHERE source_sha256 IN"
        " (SELECT source_sha256 FROM source_objects WHERE active=0)"
    )


def _publish_thumbnails(
    generation: GenerationPaths, row_start: int, staged: Sequence[Path]
) -> None:
    for offset, staged_path in enumerate(staged):
        destination = generation.thumbs / f"{row_start + offset}.jpg"
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged_path, destination)


def _record_failure(generation: GenerationPaths, video: Path, source_sha256: str, exc: Exception) -> None:
    """Record FAILED without disturbing any previously COMPLETE source."""
    if not source_sha256:
        return
    try:
        conn = connect_db(generation)
    except Exception:  # pragma: no cover - defensive
        return
    try:
        with conn:
            conn.execute(
                "INSERT INTO source_objects (source_sha256, size_bytes, stream_index,"
                " codec, width, height, timebase_num, timebase_den, state, active)"
                " VALUES (?,?,?,?,?,?,?,?, 'FAILED', 0)"
                " ON CONFLICT(source_sha256) DO UPDATE SET"
                " state=CASE WHEN source_objects.state='COMPLETE' THEN 'COMPLETE' ELSE 'FAILED' END",
                (
                    source_sha256,
                    video.stat().st_size if video.exists() else 0,
                    0, "UNKNOWN", 0, 0, 1, 1,
                ),
            )
    except Exception:  # pragma: no cover - defensive
        traceback.print_exc()
    finally:
        conn.close()


# --------------------------------------------------------------------------
# invocation-level
# --------------------------------------------------------------------------


def index_inputs(
    input_path: Path,
    index_root: Path,
    spec: GenerationSpec,
    image_embedder: Callable[[Sequence[Path]], np.ndarray],
) -> IndexSummary:
    """Index every authorized input under ONE writer lock for the invocation."""
    generation = open_or_create_generation(index_root, spec)
    with WriterLock(generation.lock):
        conn = connect_db(generation)
        try:
            reconcile_vector_tail(generation, conn, _row_width_bytes(spec))
        finally:
            conn.close()

        results = tuple(
            index_one_source(video, generation, spec, image_embedder)
            for video in discover_inputs(input_path)
        )

    return IndexSummary(
        generation_id=spec.generation_id,
        indexed=sum(1 for r in results if r.disposition == "INDEXED"),
        skipped=sum(1 for r in results if r.disposition == "SKIPPED_UNCHANGED"),
        reused=sum(1 for r in results if r.disposition == "REUSED_DUPLICATE"),
        failed=sum(1 for r in results if r.disposition == "FAILED"),
        results=results,
    )
