"""TDD Task 5: index-level integrity — contiguous rows, exact provenance, invariants.

These tests assert the properties that make the index trustworthy rather than
merely populated: half-open contiguous row ranges, one vector row per sample row,
vectors bound to their own samples, digest-addressable reuse, and no cross-source
row aliasing.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest

import persistent_local_index.indexer as indexer_module
from persistent_local_index.indexer import (
    discover_inputs,
    index_inputs,
    index_one_source,
)
from persistent_local_index.media import sha256_file
from persistent_local_index.model_space import load_manifest
from persistent_local_index.storage import (
    WriterLock,
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

ROW_WIDTH = 768 * 4


@pytest.fixture()
def index_root(tmp_path: Path) -> Path:
    return tmp_path / "index-root"


def test_row_ranges_are_half_open_and_contiguous(index_root: Path, tmp_path: Path):
    media = tmp_path / "media"
    a = synth_video(media / "a.mp4", colour="red", seconds=10.0)
    b = synth_video(media / "b.mp4", colour="blue", seconds=10.0)
    c = synth_video(media / "c.mp4", colour="green", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()

    results = [index_one_source(v, generation, spec, embedder) for v in (a, b, c)]
    assert [r.disposition for r in results] == ["INDEXED"] * 3
    assert results[0].row_start == 0
    for previous, current in zip(results, results[1:]):
        assert current.row_start == previous.row_end, "row ranges must be contiguous"
    conn = connect_db(generation)
    rows, byte_count = read_committed_counts(conn)
    assert rows == results[-1].row_end
    assert byte_count == rows * ROW_WIDTH
    spans = conn.execute(
        "SELECT row_start, row_end FROM source_objects ORDER BY row_start"
    ).fetchall()
    assert [(s[0], s[1]) for s in spans] == [
        (r.row_start, r.row_end) for r in results
    ]
    conn.close()


def test_1152_indexing_uses_profile_derived_row_geometry(
    index_root: Path, tmp_path: Path
):
    video = synth_video(tmp_path / "media" / "wide.mp4", seconds=5.0)
    spec = make_spec(embedding_dim=1152)

    def embedder(paths):
        row = np.full(1152, 1 / np.sqrt(1152), dtype=np.float32)
        return np.stack([row for _ in paths])

    generation = open_or_create_generation(index_root, spec)
    result = index_one_source(video, generation, spec, embedder)
    assert result.disposition == "INDEXED"
    conn = connect_db(generation)
    committed_rows, committed_bytes = read_committed_counts(conn)
    assert committed_rows == result.row_end
    assert committed_bytes == committed_rows * 1152 * 4
    assert generation.vectors.stat().st_size == committed_bytes
    conn.close()


def test_one_vector_row_per_sample_row(index_root: Path, tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    synth_video(media / "b.mp4", colour="blue", seconds=10.0)
    spec = make_spec()
    summary = index_inputs(media, index_root, spec, make_image_embedder())
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    sample_rows = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
    committed_rows, committed_bytes = read_committed_counts(conn)
    conn.close()
    assert summary.indexed == 2
    assert committed_rows == sample_rows
    assert committed_bytes == committed_rows * ROW_WIDTH


def test_committed_vector_prefix_matches_staged_embedding_order(
    index_root: Path, tmp_path: Path
):
    """Row i's persisted vector is the embedding of row i's own embedded image.

    The embedder records the byte digest of each image it was handed, so the
    persisted matrix can be checked position-by-position against the embedding
    that produced it.
    """
    media = tmp_path / "media"
    a = synth_video(media / "a.mp4", colour="red", seconds=10.0)
    b = synth_video(media / "b.mp4", colour="blue", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    results = []
    for video in (a, b):
        results.append(index_one_source(video, generation, spec, embedder))

    conn = connect_db(generation)
    committed_rows, _ = read_committed_counts(conn)
    vectors = np.frombuffer(generation.vectors.read_bytes(), dtype="<f4").reshape(
        committed_rows, 768
    )
    rows = conn.execute(
        "SELECT row_id, source_sha256, thumbnail_relpath FROM samples ORDER BY row_id"
    ).fetchall()
    conn.close()

    assert len(rows) == committed_rows
    # Sources are indexed sequentially, so concatenating each call's recorded
    # digests in call order reproduces the exact persisted row order.
    expected_digests: list[str] = [
        digest for call_digests in embedder.digests for digest in call_digests
    ]
    assert len(expected_digests) == committed_rows
    for row in rows:
        thumb = generation.root / row["thumbnail_relpath"]
        assert thumb.is_file(), "thumbnail must be published for every row"
        expected = deterministic_vector(expected_digests[row["row_id"]])
        np.testing.assert_allclose(
            vectors[row["row_id"]], expected, rtol=0, atol=1e-6,
            err_msg=f"vector row {row['row_id']} does not match its own embedded image",
        )


def test_duplicate_reuse_preserves_original_vector_rows(index_root: Path, tmp_path: Path):
    """Reusing a digest must not rewrite or shift the original vector rows."""
    media = tmp_path / "media"
    a = synth_video(media / "a.mp4", colour="red", seconds=10.0)
    copy = media / "a-copy.mp4"
    shutil.copy2(a, copy)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    first = index_one_source(a, generation, spec, embedder)
    before = generation.vectors.read_bytes()
    second = index_one_source(copy, generation, spec, embedder)
    assert second.disposition == "REUSED_DUPLICATE"
    assert generation.vectors.read_bytes() == before, "duplicate reuse rewrote vectors"
    assert (second.row_start, second.row_end) == (first.row_start, first.row_end)


def test_duplicate_source_does_not_alias_other_sources_rows(
    index_root: Path, tmp_path: Path
):
    media = tmp_path / "media"
    a = synth_video(media / "a.mp4", colour="red", seconds=10.0)
    b = synth_video(media / "b.mp4", colour="blue", seconds=10.0)
    a_copy = media / "a-copy.mp4"
    shutil.copy2(a, a_copy)

    spec = make_spec()
    embedder = make_image_embedder()
    summary = index_inputs(media, index_root, spec, embedder)
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    committed_rows, _ = read_committed_counts(conn)

    # a and a_copy share one range; b owns a disjoint range
    a_sha, b_sha = sha256_file(a), sha256_file(b)
    range_a = conn.execute(
        "SELECT row_start, row_end FROM source_objects WHERE source_sha256=?", (a_sha,)
    ).fetchone()
    range_b = conn.execute(
        "SELECT row_start, row_end FROM source_objects WHERE source_sha256=?", (b_sha,)
    ).fetchone()
    conn.close()

    assert summary.indexed == 2
    assert summary.reused == 1
    assert len(embedder.calls) == 2, "duplicate must not be re-embedded"
    assert range_a["row_end"] <= range_b["row_start"] or range_b["row_end"] <= range_a["row_start"]
    # exactly one set of rows for the shared digest
    assert range_a["row_end"] - range_a["row_start"] + (
        range_b["row_end"] - range_b["row_start"]
    ) == committed_rows


def test_generation_is_stable_across_invocations(index_root: Path, tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", seconds=10.0)
    spec = make_spec()
    first = index_inputs(media, index_root, spec, make_image_embedder())
    second = index_inputs(media, index_root, spec, make_image_embedder())
    assert first.generation_id == second.generation_id == spec.generation_id
    generation = open_or_create_generation(index_root, spec)
    assert generation.root.name == spec.generation_id
    assert load_manifest(generation.manifest)["generation_id"] == spec.generation_id


def test_two_specs_create_two_isolated_generations(tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", seconds=10.0)
    index_root = tmp_path / "shared-root"
    spec_a = make_spec(processor_digest="proc-a")
    spec_b = make_spec(processor_digest="proc-b")
    assert spec_a.generation_id != spec_b.generation_id

    # v1 refuses to co-locate a second, incompatible space under one index root.
    index_inputs(media, index_root, spec_a, make_image_embedder())
    with pytest.raises(ValueError, match="processor_digest"):
        open_or_create_generation(index_root, spec_b)

    # separate roots are the supported isolation: an independent, self-contained space
    other_root = tmp_path / "other-root"
    summary_b = index_inputs(media, other_root, spec_b, make_image_embedder())
    assert summary_b.generation_id == spec_b.generation_id
    assert summary_b.indexed == 1
    generation_a = open_or_create_generation(index_root, spec_a)
    generation_b = open_or_create_generation(other_root, spec_b)
    conn_a = connect_db(generation_a)
    conn_b = connect_db(generation_b)
    rows_a, bytes_a = read_committed_counts(conn_a)
    rows_b, bytes_b = read_committed_counts(conn_b)
    conn_a.close()
    conn_b.close()
    assert (rows_a, bytes_a) == (rows_b, bytes_b), "generations must be independent"
    assert generation_a.root != generation_b.root
    # and each generation's own vectors file holds exactly its own committed prefix
    assert generation_a.vectors.stat().st_size == bytes_a
    assert generation_b.vectors.stat().st_size == bytes_b


def test_failed_source_is_reported_in_summary(index_root: Path, tmp_path: Path):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    (media / "broken.mp4").write_bytes(b"not a video at all")
    summary = index_inputs(media, index_root, make_spec(), make_image_embedder())
    assert summary.indexed == 1
    assert summary.failed == 1
    failures = [r for r in summary.results if r.disposition == "FAILED"]
    assert len(failures) == 1
    assert failures[0].error
    assert failures[0].row_start is None


def test_staging_creation_failure_isolated_and_later_source_continues(
    index_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    media = tmp_path / "media"
    failed_source = synth_video(media / "a-fails-at-staging.mp4", seconds=5.0)
    later_source = synth_video(media / "b-indexes.mp4", colour="blue", seconds=5.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    original_mkdir = Path.mkdir
    injected = []

    def broken_failure_recorder(*_args, **_kwargs):
        raise RuntimeError("synthetic failure recorder failure")

    def fail_after_partial_staging_creation(
        path: Path, mode=0o777, parents=False, exist_ok=False
    ):
        path = Path(path)
        if (
            path.parent == generation.staging
            and path.name.startswith("source-")
            and not injected
        ):
            original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)
            injected.append(path)
            raise OSError("synthetic staging mkdir failure " + "x" * 600)
        return original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", fail_after_partial_staging_creation)
    monkeypatch.setattr(indexer_module, "_record_failure", broken_failure_recorder)

    summary = index_inputs(media, index_root, spec, make_image_embedder())

    assert [result.path for result in summary.results] == [
        str(failed_source), str(later_source)
    ]
    assert [result.disposition for result in summary.results] == ["FAILED", "INDEXED"]
    assert summary.failed == summary.indexed == 1
    assert len(summary.results[0].error or "") == 500
    assert (summary.results[0].error or "").startswith(
        "OSError:synthetic staging mkdir failure"
    )
    assert injected and not injected[0].exists()

    failed_digest = sha256_file(failed_source)
    later_digest = sha256_file(later_source)
    conn = connect_db(generation)
    try:
        assert conn.execute(
            "SELECT 1 FROM source_locations WHERE path=?", (str(failed_source),)
        ).fetchone() is None
        assert conn.execute(
            "SELECT 1 FROM source_locations WHERE path=?", (str(later_source),)
        ).fetchone() is not None
        assert conn.execute(
            "SELECT 1 FROM source_objects WHERE source_sha256=?", (failed_digest,)
        ).fetchone() is None
        assert conn.execute(
            "SELECT state FROM source_objects WHERE source_sha256=?", (later_digest,)
        ).fetchone()[0] == "COMPLETE"
        assert conn.execute(
            "SELECT COUNT(*) FROM samples WHERE source_sha256=?", (failed_digest,)
        ).fetchone()[0] == 0
        assert conn.execute(
            "SELECT COUNT(*) FROM samples WHERE source_sha256=?", (later_digest,)
        ).fetchone()[0] > 0
    finally:
        conn.close()


def test_empty_directory_yields_empty_summary(index_root: Path, tmp_path: Path):
    media = tmp_path / "media"
    media.mkdir(parents=True)
    summary = index_inputs(media, index_root, make_spec(), make_image_embedder())
    assert summary.indexed == summary.skipped == summary.failed == 0
    assert summary.results == ()


def test_discovery_never_escapes_the_input_root(tmp_path: Path):
    root = tmp_path / "authorized"
    outside = tmp_path / "outside"
    synth_video(outside / "secret.mp4", seconds=5.0)
    root.mkdir(parents=True)
    # a symlink pointing outside the authorized root must not be traversed
    (root / "link").symlink_to(outside, target_is_directory=True)
    (root / "video.mp4").symlink_to(outside / "secret.mp4")
    found = discover_inputs(root)
    assert found == (), f"discovery escaped the authorized root: {found}"


def test_vectors_file_never_shrinks_below_committed_across_runs(
    index_root: Path, tmp_path: Path
):
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    first = index_one_source(media / "a.mp4", generation, spec, embedder)
    size_after_first = generation.vectors.stat().st_size
    index_one_source(media / "a.mp4", generation, spec, embedder)
    assert generation.vectors.stat().st_size == size_after_first
    assert size_after_first == first.row_end * ROW_WIDTH


def test_remove_nonlast_duplicate_location_keeps_object_and_samples_active(
    index_root: Path, tmp_path: Path
):
    media = tmp_path / "media"
    original = synth_video(media / "original.mp4", seconds=10.0)
    alias = media / "alias.mp4"
    shutil.copy2(original, alias)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    embedder = make_image_embedder()
    index_one_source(original, generation, spec, embedder)
    index_one_source(alias, generation, spec, embedder)

    result = indexer_module.remove_source_location(index_root, spec, alias)

    conn = connect_db(generation)
    obj = conn.execute(
        "SELECT state, active FROM source_objects WHERE source_sha256=?",
        (sha256_file(original),),
    ).fetchone()
    active_samples = conn.execute(
        "SELECT COUNT(*) FROM samples WHERE source_sha256=? AND active=1",
        (sha256_file(original),),
    ).fetchone()[0]
    locations = conn.execute(
        "SELECT path FROM source_locations WHERE source_sha256=?",
        (sha256_file(original),),
    ).fetchall()
    conn.close()

    assert result.removed is True
    assert result.object_superseded is False
    assert (obj["state"], obj["active"]) == ("COMPLETE", 1)
    assert active_samples > 0
    assert [row["path"] for row in locations] == [str(original)]


def test_remove_last_location_supersedes_object_and_deactivates_samples(
    index_root: Path, tmp_path: Path
):
    source = synth_video(tmp_path / "media" / "only.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(source, generation, spec, make_image_embedder())

    result = indexer_module.remove_source_location(index_root, spec, source)

    conn = connect_db(generation)
    obj = conn.execute(
        "SELECT state, active FROM source_objects WHERE source_sha256=?",
        (sha256_file(source),),
    ).fetchone()
    active_samples = conn.execute(
        "SELECT COUNT(*) FROM samples WHERE source_sha256=? AND active=1",
        (sha256_file(source),),
    ).fetchone()[0]
    conn.close()
    assert result.removed is True
    assert result.object_superseded is True
    assert (obj["state"], obj["active"]) == ("SUPERSEDED", 0)
    assert active_samples == 0


def test_remove_unknown_location_is_idempotent_and_preserves_counts(
    index_root: Path, tmp_path: Path
):
    source = synth_video(tmp_path / "media" / "indexed.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(source, generation, spec, make_image_embedder())
    vectors_before = generation.vectors.read_bytes()
    manifest_before = load_manifest(generation.manifest)
    conn = connect_db(generation)
    counts_before = read_committed_counts(conn)
    conn.close()

    missing = tmp_path / "media" / "never-indexed.mp4"
    result = indexer_module.remove_source_location(index_root, spec, missing)
    repeated = indexer_module.remove_source_location(index_root, spec, missing)

    conn = connect_db(generation)
    counts_after = read_committed_counts(conn)
    active_before_after = conn.execute(
        "SELECT source_sha256, active FROM source_objects ORDER BY source_sha256"
    ).fetchall()
    conn.close()
    assert result.removed is repeated.removed is False
    assert result.source_sha256 is repeated.source_sha256 is None
    assert result.object_superseded is repeated.object_superseded is False
    assert counts_after == counts_before
    assert [(r["source_sha256"], r["active"]) for r in active_before_after] == [
        (sha256_file(source), 1)
    ]
    assert generation.vectors.read_bytes() == vectors_before
    assert load_manifest(generation.manifest)["generation_id"] == manifest_before["generation_id"]


def test_remove_location_does_not_decode_embed_or_mutate_vector_prefix(
    index_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source = synth_video(tmp_path / "media" / "indexed.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(source, generation, spec, make_image_embedder())
    vectors_before = generation.vectors.read_bytes()

    def forbidden(*args, **kwargs):
        raise AssertionError("source processing must not run during location removal")

    monkeypatch.setattr(indexer_module, "probe_stream", forbidden)
    monkeypatch.setattr(indexer_module, "sample_one_pass", forbidden)
    monkeypatch.setattr(indexer_module, "make_thumbnail", forbidden)
    result = indexer_module.remove_source_location(index_root, spec, source)

    assert result.removed is True
    assert generation.vectors.read_bytes() == vectors_before


def test_remove_location_uses_existing_writer_lock(index_root: Path, tmp_path: Path):
    source = synth_video(tmp_path / "media" / "indexed.mp4", seconds=10.0)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    index_one_source(source, generation, spec, make_image_embedder())

    with WriterLock(generation.lock):
        with pytest.raises(RuntimeError, match="CONCURRENT_WRITER"):
            indexer_module.remove_source_location(index_root, spec, source)


def test_index_one_source_persists_nonzero_video_stream_index_and_non_unit_timebase(
    index_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json
    import subprocess
    from PIL import Image
    import persistent_local_index.media as media_module

    source = tmp_path / "media" / "audio_then_video_ntsc.mp4"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"synthetic audio+video ntsc container")

    def fake_run(cmd, *args, **kwargs):
        if cmd[0] == "ffprobe":
            payload = {
                "streams": [
                    {
                        "index": 0,
                        "codec_type": "audio",
                        "codec_name": "aac",
                        "time_base": "1/48000",
                    },
                    {
                        "index": 1,
                        "codec_type": "video",
                        "codec_name": "h264",
                        "width": 64,
                        "height": 64,
                        "time_base": "1001/30000",
                        "duration": "6.006",
                    },
                ]
            }
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")
        if cmd[0] == "ffmpeg":
            assert "-map" in cmd
            assert cmd[cmd.index("-map") + 1] == "0:1"
            out_pattern = Path(cmd[-1])
            out_dir = out_pattern.parent
            for idx, colour in enumerate(((220, 20, 20), (20, 220, 20), (20, 20, 220)), start=1):
                Image.new("RGB", (64, 64), colour).save(
                    out_dir / f"s_{idx:06d}.png", format="PNG"
                )
            stderr = (
                "[Parsed_showinfo_1 @ 0x1] config in time_base: 1001/30000\n"
                "[Parsed_showinfo_1 @ 0x1] n: 0 pts: 0 pts_time:0\n"
                "[Parsed_showinfo_1 @ 0x1] n: 1 pts: 60 pts_time:2.002\n"
                "[Parsed_showinfo_1 @ 0x1] n: 2 pts: 120 pts_time:4.004\n"
            )
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr=stderr)
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr(media_module.subprocess, "run", fake_run)
    spec = make_spec()
    generation = open_or_create_generation(index_root, spec)
    outcome = index_one_source(source, generation, spec, make_image_embedder())
    assert outcome.disposition == "INDEXED"
    assert outcome.samples_written == 3

    conn = connect_db(generation)
    try:
        src_row = conn.execute(
            "SELECT stream_index, timebase_num, timebase_den FROM sources WHERE source_sha256 = ?",
            (outcome.source_sha256,),
        ).fetchone()
        sample_rows = conn.execute(
            "SELECT frame_ordinal, pts, pts_time, timebase_num, timebase_den, timestamp_human "
            "FROM samples WHERE source_sha256 = ? ORDER BY frame_ordinal",
            (outcome.source_sha256,),
        ).fetchall()
    finally:
        conn.close()

    assert src_row is not None
    assert src_row["stream_index"] == 1
    assert (src_row["timebase_num"], src_row["timebase_den"]) == (1001, 30000)
    assert [row["pts"] for row in sample_rows] == [0, 60, 120]
    assert [row["pts_time"] for row in sample_rows] == pytest.approx([0.0, 2.002, 4.004])
    assert all(
        (row["timebase_num"], row["timebase_den"]) == (1001, 30000) for row in sample_rows
    )


def test_index_inputs_records_failed_count_when_stream_or_pts_refused(
    index_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad_source = tmp_path / "media" / "bad_stream.mp4"
    bad_source.parent.mkdir(parents=True, exist_ok=True)
    bad_source.write_bytes(b"corrupt stream index")

    def refusing_probe(_path: Path):
        raise ValueError("MISSING_STREAM_INDEX")

    monkeypatch.setattr(indexer_module, "probe_stream", refusing_probe)
    spec = make_spec()
    summary = index_inputs([bad_source], index_root, spec, make_image_embedder())
    assert summary.indexed == 0
    assert summary.skipped == 0
    assert summary.reused == 0
    assert summary.failed == 1
    assert summary.outcomes[0].disposition == "FAILED"
    assert "MISSING_STREAM_INDEX" in (summary.outcomes[0].error or "")

