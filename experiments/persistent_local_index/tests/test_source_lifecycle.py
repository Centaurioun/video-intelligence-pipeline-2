"""TDD Task 5: source identity, duplicate reuse, change detection, restartability.

The lifecycle rules under test come from the approved design sections 7 and 8:

* SHA-256 is byte identity; path is location metadata only;
* an already-COMPLETE digest is reused without a second embedding pass;
* a changed path moves its association only after the new source is COMPLETE;
* old rows become inactive only when no remaining location refers to the old digest;
* a stale IN_PROGRESS source is redone and exposes no partial searchable rows;
* a per-source failure never invalidates earlier COMPLETE sources;
* source media bytes are never modified.
"""
from __future__ import annotations

import os
import shutil
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from persistent_local_index.indexer import (
    discover_inputs,
    index_inputs,
    index_one_source,
)
from persistent_local_index.media import sha256_file
from persistent_local_index.model_space import load_manifest
from persistent_local_index.storage import (
    connect_db,
    open_or_create_generation,
    read_committed_counts,
)

from conftest import (  # noqa: E402
    deterministic_vector,
    make_image_embedder,
    make_spec,
    requires_ffmpeg,
    synth_video,
)

pytestmark = requires_ffmpeg


@pytest.fixture()
def index_root(tmp_path: Path) -> Path:
    return tmp_path / "index-root"


def _rows(conn, sha: str):
    return conn.execute(
        "SELECT row_id FROM samples WHERE source_sha256=? ORDER BY row_id", (sha,)
    ).fetchall()


def _obj(conn, sha: str):
    row = conn.execute(
        "SELECT state, row_start, row_end, active FROM source_objects WHERE source_sha256=?",
        (sha,),
    ).fetchone()
    return tuple(row) if row else None


def _loc(conn, path: Path):
    row = conn.execute(
        "SELECT source_sha256 FROM source_locations WHERE path=?", (str(path),)
    ).fetchone()
    return row[0] if row else None


# --- discovery -------------------------------------------------------------


def test_discover_file_input_is_exact_file(tmp_path: Path):
    media = tmp_path / "media"
    video = synth_video(media / "a.mp4")
    synth_video(media / "b.mp4")
    assert discover_inputs(video) == (video,)


def test_discover_directory_is_recursive_allowlisted_and_sorted(tmp_path: Path):
    media = tmp_path / "media"
    a = synth_video(media / "a.mp4")
    b = synth_video(media / "nested" / "b.mov")
    c = synth_video(media / "c.mkv")
    (media / "notes.txt").write_text("ignore me", encoding="utf-8")
    found = discover_inputs(media)
    assert set(found) == {a, b, c}
    assert list(found) == sorted(found, key=lambda p: str(p).encode("utf-8"))


def test_discover_directory_ignores_unallowed_extensions(tmp_path: Path):
    media = tmp_path / "media"
    media.mkdir(parents=True)
    (media / "x.wav").write_bytes(b"audio")
    (media / "y.jpg").write_bytes(b"image")
    assert discover_inputs(media) == ()


# --- basic indexing --------------------------------------------------------


def test_index_one_source_appends_rows_and_commits(index_root: Path, tmp_path: Path):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    sha = sha256_file(video)
    result = index_one_source(video, generation, spec, make_image_embedder())
    assert result.disposition == "INDEXED"
    assert result.source_sha256 == sha
    assert result.row_start == 0
    assert result.row_end > 0
    assert result.error is None
    conn = connect_db(generation)
    assert read_committed_counts(conn)[0] == result.row_end
    assert _obj(conn, sha)[0] == "COMPLETE"
    assert len(_rows(conn, sha)) == result.row_end
    conn.close()


def test_indexed_samples_carry_measured_pts_and_timebase(index_root: Path, tmp_path: Path):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(video, generation, spec, make_image_embedder())
    conn = connect_db(generation)
    rows = conn.execute(
        "SELECT pts, timebase_num, timebase_den, pts_time, timestamp_human, "
        "thumbnail_relpath FROM samples ORDER BY row_id"
    ).fetchall()
    assert rows
    for row in rows:
        assert row["timebase_num"] > 0 and row["timebase_den"] > 0
        expected = row["pts"] * row["timebase_num"] / row["timebase_den"]
        assert row["pts_time"] == pytest.approx(expected, abs=1e-6)
        assert row["timestamp_human"]
    conn.close()


def test_index_publishes_thumbnails_for_every_row(index_root: Path, tmp_path: Path):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    result = index_one_source(video, generation, spec, make_image_embedder())
    conn = connect_db(generation)
    rels = [
        r[0] for r in conn.execute(
            "SELECT thumbnail_relpath FROM samples WHERE source_sha256=?",
            (result.source_sha256,),
        )
    ]
    conn.close()
    assert rels
    for rel in rels:
        assert (generation.root / rel).is_file(), f"missing published thumbnail {rel}"


def test_index_removes_source_staging(index_root: Path, tmp_path: Path):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=5.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(video, generation, spec, make_image_embedder())
    leftovers = [p for p in generation.staging.rglob("*") if p.is_file()]
    assert leftovers == [], f"staging not cleaned: {leftovers}"


def test_source_media_bytes_unchanged_by_indexing(index_root: Path, tmp_path: Path):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=5.0)
    before = sha256_file(video)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(video, generation, spec, make_image_embedder())
    assert sha256_file(video) == before, "SOURCE_MEDIA_MUTATED"


# --- unchanged skip --------------------------------------------------------


def test_unchanged_digest_skips_sampler_and_embedder(index_root: Path, tmp_path: Path):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    first = index_one_source(video, generation, spec, embedder)
    assert first.disposition == "INDEXED"
    assert len(embedder.calls) == 1

    second = index_one_source(video, generation, spec, embedder)
    assert second.disposition == "SKIPPED_UNCHANGED"
    assert second.row_start == first.row_start
    assert second.row_end == first.row_end
    assert len(embedder.calls) == 1, "unchanged source re-embedded"

    conn = connect_db(generation)
    assert read_committed_counts(conn)[0] == first.row_end, "rows appended on skip"
    conn.close()


# --- duplicate reuse -------------------------------------------------------


def test_duplicate_digest_at_another_path_reuses_rows(index_root: Path, tmp_path: Path):
    original = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    duplicate = tmp_path / "media" / "copy-of-a.mp4"
    shutil.copy2(original, duplicate)
    assert sha256_file(original) == sha256_file(duplicate)

    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    first = index_one_source(original, generation, spec, embedder)
    assert first.disposition == "INDEXED"
    calls_after_first = len(embedder.calls)

    second = index_one_source(duplicate, generation, spec, embedder)
    assert second.disposition == "REUSED_DUPLICATE"
    assert second.source_sha256 == first.source_sha256
    assert (second.row_start, second.row_end) == (first.row_start, first.row_end)
    assert len(embedder.calls) == calls_after_first, "duplicate re-embedded"
    assert len(embedder.calls) == 1

    conn = connect_db(generation)
    assert read_committed_counts(conn)[0] == first.row_end, "duplicate appended rows"
    assert _loc(conn, original) == first.source_sha256
    assert _loc(conn, duplicate) == first.source_sha256
    conn.close()


# --- changed source / supersession ----------------------------------------


def test_changed_bytes_at_same_path_appends_and_moves_location_only_after_complete(
    index_root: Path, tmp_path: Path
):
    media = tmp_path / "media"
    path = synth_video(media / "a.mp4", colour="red", seconds=10.0)
    old_sha = sha256_file(path)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    first = index_one_source(path, generation, spec, embedder)

    # same path, different bytes
    synth_video(path, colour="green", seconds=10.0)
    new_sha = sha256_file(path)
    assert new_sha != old_sha

    second = index_one_source(path, generation, spec, embedder)
    assert second.disposition == "INDEXED"
    assert second.source_sha256 == new_sha
    assert second.row_start == first.row_end, "new rows must append after old rows"

    conn = connect_db(generation)
    assert _loc(conn, path) == new_sha
    assert _obj(conn, old_sha)[0] == "SUPERSEDED"
    assert _obj(conn, old_sha)[3] == 0, "old object must be inactive"
    old_rows = conn.execute(
        "SELECT active FROM samples WHERE source_sha256=?", (old_sha,)
    ).fetchall()
    assert old_rows and all(r[0] == 0 for r in old_rows), "old rows must be inactive"
    new_rows = conn.execute(
        "SELECT active FROM samples WHERE source_sha256=?", (new_sha,)
    ).fetchall()
    assert new_rows and all(r[0] == 1 for r in new_rows)
    # historical rows remain physically present and searchable-by-row
    assert len(_rows(conn, old_sha)) > 0
    assert read_committed_counts(conn)[0] == second.row_end
    conn.close()


def test_old_digest_stays_active_while_another_location_references_it(
    index_root: Path, tmp_path: Path
):
    media = tmp_path / "media"
    original = synth_video(media / "a.mp4", colour="red", seconds=10.0)
    duplicate = media / "copy-a.mp4"
    shutil.copy2(original, duplicate)
    old_sha = sha256_file(original)

    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    index_one_source(original, generation, spec, embedder)
    index_one_source(duplicate, generation, spec, embedder)

    # change ONLY the first path; the duplicate still refers to old_sha
    synth_video(original, colour="green", seconds=10.0)
    new_sha = sha256_file(original)
    index_one_source(original, generation, spec, embedder)

    conn = connect_db(generation)
    assert _loc(conn, original) == new_sha
    assert _loc(conn, duplicate) == old_sha
    assert _obj(conn, old_sha)[0] == "COMPLETE", "old digest must stay COMPLETE"
    assert _obj(conn, old_sha)[3] == 1, "old digest must stay active"
    old_rows = conn.execute(
        "SELECT active FROM samples WHERE source_sha256=?", (old_sha,)
    ).fetchall()
    assert all(r[0] == 1 for r in old_rows), "old rows must remain active"
    conn.close()


def test_old_digest_superseded_only_when_no_location_references_it(
    index_root: Path, tmp_path: Path
):
    media = tmp_path / "media"
    a = synth_video(media / "a.mp4", colour="red", seconds=10.0)
    b = media / "b.mp4"
    shutil.copy2(a, b)
    old_sha = sha256_file(a)

    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    index_one_source(a, generation, spec, embedder)
    index_one_source(b, generation, spec, embedder)

    # move BOTH paths onto new bytes -> no location refers to old_sha
    synth_video(a, colour="green", seconds=10.0)
    synth_video(b, colour="blue", seconds=10.0)
    new_a = sha256_file(a)
    new_b = sha256_file(b)
    index_one_source(a, generation, spec, embedder)
    index_one_source(b, generation, spec, embedder)

    conn = connect_db(generation)
    assert _loc(conn, a) == new_a
    assert _loc(conn, b) == new_b
    assert _obj(conn, old_sha)[0] == "SUPERSEDED"
    assert _obj(conn, old_sha)[3] == 0
    old_rows = conn.execute(
        "SELECT active FROM samples WHERE source_sha256=?", (old_sha,)
    ).fetchall()
    assert all(r[0] == 0 for r in old_rows)
    conn.close()


# --- restartability --------------------------------------------------------


def test_stale_in_progress_source_is_redone_with_no_partial_rows(
    index_root: Path, tmp_path: Path
):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    sha = sha256_file(video)

    # Simulate a crash: an IN_PROGRESS row with no committed vectors.
    conn = connect_db(generation)
    with conn:
        conn.execute(
            "INSERT INTO source_objects (source_sha256, size_bytes, stream_index, codec,"
            " width, height, timebase_num, timebase_den, state, active)"
            " VALUES (?,?,?,?,?,?,?,?, 'IN_PROGRESS', 0)",
            (sha, video.stat().st_size, 0, "h264", 64, 48, 1, 1000),
        )
    assert read_committed_counts(conn) == (0, 0)
    conn.close()

    result = index_one_source(video, generation, spec, make_image_embedder())
    assert result.disposition == "INDEXED"
    conn = connect_db(generation)
    assert _obj(conn, sha)[0] == "COMPLETE"
    assert read_committed_counts(conn)[0] == result.row_end
    conn.close()


def test_interrupted_append_leaves_no_searchable_rows_until_commit(
    index_root: Path, tmp_path: Path
):
    """A crashed run's uncommitted tail must not become searchable rows."""
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    sha = sha256_file(video)

    conn = connect_db(generation)
    with conn:
        conn.execute(
            "INSERT INTO source_objects (source_sha256, size_bytes, stream_index, codec,"
            " width, height, timebase_num, timebase_den, state, active)"
            " VALUES (?,?,?,?,?,?,?,?, 'IN_PROGRESS', 0)",
            (sha, video.stat().st_size, 0, "h264", 64, 48, 1, 1000),
        )
    conn.close()
    # crash artifact: bytes written with no SQLite commit
    with generation.vectors.open("ab") as fh:
        fh.write(b"\x00" * (3 * 768 * 4))

    conn = connect_db(generation)
    assert read_committed_counts(conn) == (0, 0)
    assert conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0] == 0
    conn.close()

    result = index_one_source(video, generation, spec, make_image_embedder())
    conn = connect_db(generation)
    rows, byte_count = read_committed_counts(conn)
    assert rows == result.row_end
    assert byte_count == rows * 768 * 4, "uncommitted tail survived the next append"
    conn.close()


def test_per_source_failure_does_not_invalidate_complete_sources(
    index_root: Path, tmp_path: Path
):
    good = synth_video(tmp_path / "media" / "good.mp4", colour="red", seconds=10.0)
    bad = tmp_path / "media" / "bad.mp4"
    bad.write_bytes(b"this is definitely not a video")

    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    good_result = index_one_source(good, generation, spec, embedder)
    assert good_result.disposition == "INDEXED"
    good_sha = good_result.source_sha256

    bad_result = index_one_source(bad, generation, spec, embedder)
    assert bad_result.disposition == "FAILED"
    assert bad_result.error
    assert bad_result.row_start is None

    conn = connect_db(generation)
    assert _obj(conn, good_sha)[0] == "COMPLETE"
    assert _obj(conn, good_sha)[3] == 1
    assert read_committed_counts(conn)[0] == good_result.row_end
    good_rows = conn.execute(
        "SELECT active FROM samples WHERE source_sha256=?", (good_sha,)
    ).fetchall()
    assert good_rows and all(r[0] == 1 for r in good_rows)
    conn.close()


def test_embedder_failure_rolls_back_without_partial_source(
    index_root: Path, tmp_path: Path
):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)

    def exploding(paths):
        raise RuntimeError("embedder exploded")

    result = index_one_source(video, generation, spec, exploding)
    assert result.disposition == "FAILED"
    conn = connect_db(generation)
    assert read_committed_counts(conn) == (0, 0)
    assert conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0] == 0
    conn.close()


def test_source_change_during_embedding_is_rejected_without_commit(
    index_root: Path, tmp_path: Path
):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    original_sha = sha256_file(video)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embed = make_image_embedder()

    def mutate_then_embed(paths):
        video.write_bytes(video.read_bytes() + b"changed during indexing")
        return embed(paths)

    result = index_one_source(video, generation, spec, mutate_then_embed)

    assert result.disposition == "FAILED"
    assert result.source_sha256 == original_sha
    conn = connect_db(generation)
    assert read_committed_counts(conn) == (0, 0)
    assert conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0] == 0
    assert _obj(conn, original_sha)[0] != "COMPLETE"
    assert _loc(conn, video) is None
    conn.close()


def test_transient_source_change_during_sampling_is_rejected_without_commit(
    index_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    import persistent_local_index.indexer as indexer

    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    original_bytes = video.read_bytes()
    original_sha = sha256_file(video)
    original_stat = video.stat()
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    real_sample = indexer.sample_one_pass
    restored_stat = None

    def transient_mutation_during_sampling(path, interval, output_dir):
        nonlocal restored_stat
        frames = real_sample(path, interval, output_dir)
        # Change then restore the exact bytes and mtime before sample_one_pass
        # returns, matching a transient in-place mutation during sampling.
        video.write_bytes(original_bytes + b"transient mutation")
        video.write_bytes(original_bytes)
        os.utime(video, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
        restored_stat = video.stat()
        return frames

    monkeypatch.setattr(indexer, "sample_one_pass", transient_mutation_during_sampling)
    assert sha256_file(video) == original_sha
    result = index_one_source(video, generation, spec, make_image_embedder())

    assert restored_stat is not None
    assert restored_stat.st_size == original_stat.st_size
    assert restored_stat.st_mtime_ns == original_stat.st_mtime_ns
    assert (restored_stat.st_dev, restored_stat.st_ino) == (
        original_stat.st_dev, original_stat.st_ino
    )
    assert restored_stat.st_ctime_ns != original_stat.st_ctime_ns
    assert result.disposition == "FAILED"
    assert result.source_sha256 == original_sha
    conn = connect_db(generation)
    assert read_committed_counts(conn) == (0, 0)
    assert conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0] == 0
    assert _obj(conn, original_sha)[0] != "COMPLETE"
    assert _loc(conn, video) is None
    conn.close()


def test_resume_after_failure_indexes_the_source_successfully(
    index_root: Path, tmp_path: Path
):
    video = synth_video(tmp_path / "media" / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    sha = sha256_file(video)

    def exploding(paths):
        raise RuntimeError("embedder exploded")

    assert index_one_source(video, generation, spec, exploding).disposition == "FAILED"
    resumed = index_one_source(video, generation, spec, make_image_embedder())
    assert resumed.disposition == "INDEXED"
    conn = connect_db(generation)
    assert _obj(conn, sha)[0] == "COMPLETE"
    assert read_committed_counts(conn)[0] == resumed.row_end
    conn.close()


# --- invocation-level ------------------------------------------------------


def test_index_inputs_summarizes_a_directory(index_root: Path, tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    synth_video(media / "b.mp4", colour="blue", seconds=10.0)
    spec = make_spec()
    embedder = make_image_embedder()
    summary = index_inputs(media, index_root, spec, embedder)
    assert summary.indexed == 2
    assert summary.skipped == 0
    assert summary.failed == 0
    assert summary.generation_id == spec.generation_id
    assert len(summary.results) == 2

    again = index_inputs(media, index_root, spec, embedder)
    assert again.indexed == 0
    assert again.skipped == 2
    assert len(embedder.calls) == 2, "second invocation re-embedded"


def test_index_inputs_holds_one_writer_lock(index_root: Path, tmp_path: Path):
    from persistent_local_index.storage import WriterLock

    media = tmp_path / "media"
    synth_video(media / "a.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    with WriterLock(generation.lock):
        with pytest.raises(RuntimeError, match="CONCURRENT_WRITER"):
            index_inputs(media, index_root, spec, make_image_embedder())


def test_index_inputs_manifest_mirror_matches_sqlite(index_root: Path, tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", seconds=10.0)
    spec = make_spec()
    index_inputs(media, index_root, spec, make_image_embedder())
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    rows, _ = read_committed_counts(conn)
    conn.close()
    assert load_manifest(generation.manifest)["committed_rows"] == rows


# --- explicit location removal (H3-B02) -----------------------------------


def _remove_location_api():
    """Resolve the frozen H3-B02 API at call time for behavioral RED tests."""
    from persistent_local_index import indexer

    return indexer.remove_source_location


def test_remove_nonlast_duplicate_location_keeps_object_and_samples_active(
    index_root: Path, tmp_path: Path
):
    original = synth_video(tmp_path / "media" / "a.mp4", seconds=5.0)
    alias = tmp_path / "media" / "alias.mp4"
    shutil.copy2(original, alias)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    indexed = index_one_source(original, generation, spec, make_image_embedder())
    index_one_source(alias, generation, spec, make_image_embedder())

    result = _remove_location_api()(index_root, spec, original)

    assert result.source_path == original
    assert result.removed is True
    assert result.source_sha256 == indexed.source_sha256
    assert result.object_superseded is False
    conn = connect_db(generation)
    assert _loc(conn, original) is None
    assert _loc(conn, alias) == indexed.source_sha256
    assert _obj(conn, indexed.source_sha256)[0] == "COMPLETE"
    assert _obj(conn, indexed.source_sha256)[3] == 1
    active = conn.execute(
        "SELECT active FROM samples WHERE source_sha256=?", (indexed.source_sha256,)
    ).fetchall()
    assert active and all(row[0] == 1 for row in active)
    conn.close()


def test_remove_last_location_supersedes_object_and_deactivates_samples(
    index_root: Path, tmp_path: Path
):
    source = synth_video(tmp_path / "media" / "only.mp4", seconds=5.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    indexed = index_one_source(source, generation, spec, make_image_embedder())

    result = _remove_location_api()(index_root, spec, source)

    assert result.source_path == source
    assert result.removed is True
    assert result.source_sha256 == indexed.source_sha256
    assert result.object_superseded is True
    conn = connect_db(generation)
    assert _loc(conn, source) is None
    assert _obj(conn, indexed.source_sha256)[0] == "SUPERSEDED"
    assert _obj(conn, indexed.source_sha256)[3] == 0
    active = conn.execute(
        "SELECT active FROM samples WHERE source_sha256=?", (indexed.source_sha256,)
    ).fetchall()
    assert active and all(row[0] == 0 for row in active)
    conn.close()


def test_remove_unknown_location_is_idempotent_and_preserves_counts(
    index_root: Path, tmp_path: Path
):
    source = synth_video(tmp_path / "media" / "present.mp4", seconds=5.0)
    unknown = tmp_path / "media" / "unknown.mp4"
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    indexed = index_one_source(source, generation, spec, make_image_embedder())
    before_manifest = load_manifest(generation.manifest)
    before_manifest_bytes = generation.manifest.read_bytes()
    before_vector_bytes = generation.vectors.read_bytes()
    conn = connect_db(generation)
    before_counts = read_committed_counts(conn)
    before_objects = [tuple(row) for row in conn.execute(
        "SELECT * FROM source_objects ORDER BY source_sha256"
    ).fetchall()]
    before_locations = [tuple(row) for row in conn.execute(
        "SELECT * FROM source_locations ORDER BY path"
    ).fetchall()]
    before_samples = [tuple(row) for row in conn.execute(
        "SELECT * FROM samples ORDER BY row_id"
    ).fetchall()]
    conn.close()
    before_generation_id = before_manifest["generation_id"]

    first = _remove_location_api()(index_root, spec, unknown)
    second = _remove_location_api()(index_root, spec, unknown)

    assert first.source_path == unknown and first.removed is False
    assert first.source_sha256 is None and first.object_superseded is False
    assert second == first
    assert generation.vectors.read_bytes() == before_vector_bytes
    assert load_manifest(generation.manifest) == before_manifest
    assert generation.manifest.read_bytes() == before_manifest_bytes
    conn = connect_db(generation)
    assert read_committed_counts(conn) == before_counts
    assert [tuple(row) for row in conn.execute(
        "SELECT * FROM source_objects ORDER BY source_sha256"
    ).fetchall()] == before_objects
    assert [tuple(row) for row in conn.execute(
        "SELECT * FROM source_locations ORDER BY path"
    ).fetchall()] == before_locations
    assert [tuple(row) for row in conn.execute(
        "SELECT * FROM samples ORDER BY row_id"
    ).fetchall()] == before_samples
    assert _loc(conn, source) == indexed.source_sha256
    assert _obj(conn, indexed.source_sha256)[0] == "COMPLETE"
    conn.close()
    assert load_manifest(generation.manifest)["generation_id"] == before_generation_id


def test_removed_last_location_is_not_searchable_but_nonlast_alias_remains_searchable(
    index_root: Path, tmp_path: Path
):
    from persistent_local_index.search import query_generation

    original = synth_video(tmp_path / "media" / "original.mp4", seconds=5.0)
    alias = tmp_path / "media" / "alias.mp4"
    shutil.copy2(original, alias)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    indexed = index_one_source(original, generation, spec, embedder)
    index_one_source(alias, generation, spec, embedder)
    query = deterministic_vector(embedder.digests[0][0]).reshape(1, 768)

    _remove_location_api()(index_root, spec, original)
    hits_with_alias = query_generation(
        index_root, spec, ["source-vector"], lambda _: query, top_k=indexed.row_end
    )["source-vector"]
    assert hits_with_alias
    assert all(hit.source_sha256 == indexed.source_sha256 for hit in hits_with_alias)

    _remove_location_api()(index_root, spec, alias)
    hits_without_locations = query_generation(
        index_root, spec, ["source-vector"], lambda _: query, top_k=indexed.row_end
    )["source-vector"]
    assert all(hit.source_sha256 != indexed.source_sha256 for hit in hits_without_locations)


def test_remove_location_under_writer_lock_rejects_concurrent_writer(
    index_root: Path, tmp_path: Path
):
    from persistent_local_index.storage import WriterLock

    source = synth_video(tmp_path / "media" / "locked.mp4", seconds=5.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    indexed = index_one_source(source, generation, spec, make_image_embedder())

    with WriterLock(generation.lock):
        with pytest.raises(RuntimeError, match="CONCURRENT_WRITER"):
            _remove_location_api()(index_root, spec, source)

    conn = connect_db(generation)
    assert _loc(conn, source) == indexed.source_sha256
    assert _obj(conn, indexed.source_sha256)[3] == 1
    conn.close()


def test_remove_location_preserves_vector_prefix_and_manifest_generation(
    index_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    import persistent_local_index.indexer as indexer

    source = synth_video(tmp_path / "media" / "removable.mp4", seconds=5.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    indexed = index_one_source(source, generation, spec, make_image_embedder())
    vector_prefix = generation.vectors.read_bytes()
    manifest_before = load_manifest(generation.manifest)

    def forbidden(*args, **kwargs):
        raise AssertionError("removal must not decode, sample, or embed media")

    monkeypatch.setattr(indexer, "sample_one_pass", forbidden)
    monkeypatch.setattr(indexer, "probe_stream", forbidden)
    result = _remove_location_api()(index_root, spec, source)

    assert result.source_sha256 == indexed.source_sha256
    assert generation.vectors.read_bytes() == vector_prefix
    manifest_after = load_manifest(generation.manifest)
    assert manifest_after["generation_id"] == manifest_before["generation_id"]
    assert manifest_after["space_id"] == manifest_before["space_id"]
    assert manifest_after["committed_rows"] == manifest_before["committed_rows"]
