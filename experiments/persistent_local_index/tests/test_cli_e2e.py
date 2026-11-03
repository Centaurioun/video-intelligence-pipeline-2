"""TDD Task 7: synthetic end-to-end proof of the index -> query workflow.

Everything here is synthetic: tiny generated videos, deterministic fake
embeddings, and a temporary index root.  No real user media, no network, no
model download.  The real frozen local model is exercised separately in the
bounded smoke described in the evidence record.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from persistent_local_index.cli import main
from persistent_local_index.indexer import index_inputs
from persistent_local_index.media import sha256_file
from persistent_local_index.model_space import build_generation_spec, load_manifest
from persistent_local_index.storage import connect_db, open_or_create_generation, read_committed_counts

from conftest import (  # noqa: E402
    canonical_cli_identity,
    deterministic_vector,
    make_image_embedder,
    make_model_root,
    make_semantic_space,
    make_text_embedder,
    requires_ffmpeg,
    synth_video,
)

pytestmark = requires_ffmpeg

ROW_WIDTH = 768 * 4


@pytest.fixture()
def synthetic_media(tmp_path: Path) -> Path:
    media = tmp_path / "media"
    synth_video(media / "a.mp4", colour="red", seconds=10.0)
    synth_video(media / "b.mp4", colour="blue", seconds=10.0)
    return media


# --- end-to-end via the library surface ------------------------------------


def test_index_twice_query_twice_is_stable_and_read_only(synthetic_media, tmp_path):
    index_root = tmp_path / "idx"
    spec = build_generation_spec(make_semantic_space())
    embedder = make_image_embedder()

    first = index_inputs(synthetic_media, index_root, spec, embedder)
    assert first.indexed == 2
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    rows_after_first, bytes_after_first = read_committed_counts(conn)
    conn.close()

    # 2) rerun index unchanged -> no rows appended
    second = index_inputs(synthetic_media, index_root, spec, embedder)
    assert second.indexed == 0
    assert second.skipped == 2
    conn = connect_db(generation)
    assert read_committed_counts(conn) == (rows_after_first, bytes_after_first)
    conn.close()

    # 3) query twice; must not mutate vector/SQLite files
    from persistent_local_index.search import query_generation

    vectors_before = generation.vectors.read_bytes()
    db_before = generation.database.read_bytes()
    for _ in range(2):
        results = query_generation(
            index_root, spec, ["a red scene", "a blue scene"], make_text_embedder(), top_k=3
        )
        assert set(results) == {"a red scene", "a blue scene"}
        assert all(results.values())
    assert generation.vectors.read_bytes() == vectors_before
    assert generation.database.read_bytes() == db_before


def test_duplicate_source_at_second_path_appends_no_rows(synthetic_media, tmp_path):
    index_root = tmp_path / "idx"
    spec = build_generation_spec(make_semantic_space())
    embedder = make_image_embedder()
    index_inputs(synthetic_media, index_root, spec, embedder)
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    rows_before, _ = read_committed_counts(conn)
    conn.close()

    copy = synthetic_media / "a-copy.mp4"
    shutil.copy2(synthetic_media / "a.mp4", copy)
    summary = index_inputs(synthetic_media, index_root, spec, embedder)
    assert summary.reused == 1
    conn = connect_db(generation)
    assert read_committed_counts(conn)[0] == rows_before, "duplicate appended rows"
    conn.close()


def test_replaced_bytes_append_rows_and_preserve_historical_rows(
    synthetic_media, tmp_path
):
    index_root = tmp_path / "idx"
    spec = build_generation_spec(make_semantic_space())
    embedder = make_image_embedder()
    target = synthetic_media / "a.mp4"
    old_sha = sha256_file(target)
    index_inputs(synthetic_media, index_root, spec, embedder)
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    rows_before, _ = read_committed_counts(conn)
    old_rows = conn.execute(
        "SELECT COUNT(*) FROM samples WHERE source_sha256=?", (old_sha,)
    ).fetchone()[0]
    conn.close()

    synth_video(target, colour="green", seconds=10.0)
    assert sha256_file(target) != old_sha
    index_inputs(synthetic_media, index_root, spec, embedder)

    conn = connect_db(generation)
    rows_after, _ = read_committed_counts(conn)
    assert rows_after > rows_before, "changed source did not append"
    # historical rows remain physically present
    assert (
        conn.execute("SELECT COUNT(*) FROM samples WHERE source_sha256=?", (old_sha,)).fetchone()[0]
        == old_rows
    )
    # old activity follows the location-reference rule
    assert conn.execute(
        "SELECT active FROM source_objects WHERE source_sha256=?", (old_sha,)
    ).fetchone()[0] == 0
    assert conn.execute(
        "SELECT COUNT(*) FROM samples WHERE source_sha256=? AND active=1", (old_sha,)
    ).fetchone()[0] == 0
    conn.close()


def test_crash_tail_recovered_on_next_index(synthetic_media, tmp_path):
    index_root = tmp_path / "idx"
    spec = build_generation_spec(make_semantic_space())
    embedder = make_image_embedder()
    index_inputs(synthetic_media, index_root, spec, embedder)
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    committed_rows, committed_bytes = read_committed_counts(conn)
    conn.close()

    with generation.vectors.open("ab") as fh:
        fh.write(b"\x00" * (4 * ROW_WIDTH))

    # a fresh index invocation must truncate the uncommitted tail
    index_inputs(synthetic_media, index_root, spec, embedder)
    conn = connect_db(generation)
    assert read_committed_counts(conn) == (committed_rows, committed_bytes)
    conn.close()
    assert generation.vectors.stat().st_size == committed_bytes


# --- CLI surface -----------------------------------------------------------


def test_cli_module_index_accepts_input_and_fake_embedder(
    synthetic_media, tmp_path, synthetic_model_root
):
    """The documented subprocess surface must retain synthetic ``--input`` support."""
    identity = canonical_cli_identity(synthetic_model_root)
    env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[3]
    env["PYTHONPATH"] = os.pathsep.join(
        (str(repo_root / "experiments"), env.get("PYTHONPATH", ""))
    ).rstrip(os.pathsep)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "persistent_local_index.cli",
            "index",
            "--input",
            str(synthetic_media),
            "--index-root",
            str(tmp_path / "idx"),
            "--model-root",
            str(synthetic_model_root),
            "--weights-sha256",
            identity["weights_sha256"],
            "--model-identity",
            identity["model_identity"],
            "--model-revision",
            identity["frozen_revision"],
            "--device",
            "cpu",
            "--fake-embedder",
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["indexed"] == 2
    assert payload["failed"] == 0
    assert payload["ok"] is True


def test_cli_index_writes_json_summary(synthetic_media, tmp_path, capsys, synthetic_model_root, monkeypatch):
    index_root = tmp_path / "idx"
    monkeypatch.setattr(
        "persistent_local_index.cli._build_image_embedder",
        lambda *a, **k: make_image_embedder(),
    )
    code = main(
        [
            "index",
            "--input", str(synthetic_media),
            "--index-root", str(index_root),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--device", "cpu",
            "--fake-embedder",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["indexed"] == 2
    assert payload["failed"] == 0
    assert payload["generation_id"]


def test_cli_query_writes_json_hits(synthetic_media, tmp_path, capsys, synthetic_model_root, monkeypatch):
    index_root = tmp_path / "idx"
    spec = build_generation_spec(make_semantic_space(**canonical_cli_identity(synthetic_model_root)))
    index_inputs(synthetic_media, index_root, spec, make_image_embedder())
    monkeypatch.setattr(
        "persistent_local_index.cli._build_text_embedder",
        lambda *a, **k: make_text_embedder(),
    )
    code = main(
        [
            "query",
            "--index-root", str(index_root),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--query", "a red scene",
            "--query", "a blue scene",
            "--top-k", "2",
            "--device", "cpu",
            "--fake-embedder",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert set(payload["queries"]) == {"a red scene", "a blue scene"}
    for query in payload["queries"].values():
        assert len(query["hits"]) == 2
        for hit in query["hits"]:
            assert hit["source_sha256"]
            assert hit["pts"] is not None
            assert hit["timebase_den"] > 0
            assert hit["timestamp_human"]


def test_cli_query_uses_pinned_sampling_policy_from_index(synthetic_media, tmp_path, capsys, synthetic_model_root, monkeypatch):
    """The CLI must derive the live spec from the index, not assume defaults."""
    index_root = tmp_path / "idx"
    spec = build_generation_spec(
        make_semantic_space(**canonical_cli_identity(synthetic_model_root)),
        sampling_interval_seconds=9.0,
    )
    index_inputs(synthetic_media, index_root, spec, make_image_embedder())
    monkeypatch.setattr(
        "persistent_local_index.cli._build_text_embedder",
        lambda *a, **k: make_text_embedder(),
    )
    # CLI derives the generation from the manifest of the single existing generation
    code = main(
        [
            "query",
            "--index-root", str(index_root),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--query", "q",
            "--top-k", "1",
            "--device", "cpu",
            "--fake-embedder",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["generation_id"] == spec.generation_id


def test_cli_query_never_decodes_video(synthetic_media, tmp_path, capsys, synthetic_model_root, monkeypatch):
    index_root = tmp_path / "idx"
    spec = build_generation_spec(make_semantic_space(**canonical_cli_identity(synthetic_model_root)))
    index_inputs(synthetic_media, index_root, spec, make_image_embedder())
    monkeypatch.setattr(
        "persistent_local_index.cli._build_text_embedder",
        lambda *a, **k: make_text_embedder(),
    )

    calls: list[object] = []
    real_run = subprocess.run

    def spy(cmd, *a, **k):
        calls.append(cmd)
        return real_run(cmd, *a, **k)

    monkeypatch.setattr(subprocess, "run", spy)
    code = main(
        [
            "query",
            "--index-root", str(index_root),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--query", "q",
            "--top-k", "1",
            "--device", "cpu",
            "--fake-embedder",
        ]
    )
    assert code == 0
    flat = " ".join(
        " ".join(map(str, c)) if isinstance(c, (list, tuple)) else str(c) for c in calls
    )
    assert "ffmpeg" not in flat
    assert "ffprobe" not in flat


def test_cli_rejects_unavailable_mps_loudly(tmp_path, capsys, synthetic_model_root, monkeypatch):
    import persistent_local_index.embedding as embedding

    monkeypatch.setattr(embedding, "_mps_available", lambda: False)
    code = main(
        [
            "query",
            "--index-root", str(tmp_path / "idx"),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--query", "q",
            "--top-k", "1",
            "--device", "mps",
        ]
    )
    assert code != 0
    captured = capsys.readouterr()
    assert "MPS_REQUESTED_BUT_UNAVAILABLE" in (captured.err + captured.out)


def test_cli_index_requires_an_input_that_exists(tmp_path, capsys, synthetic_model_root):
    code = main(
        [
            "index",
            "--input", str(tmp_path / "nope.mp4"),
            "--index-root", str(tmp_path / "idx"),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--device", "cpu",
            "--fake-embedder",
        ]
    )
    assert code != 0


def test_cli_index_reports_per_source_failure_without_aborting(synthetic_media, tmp_path, capsys, synthetic_model_root, monkeypatch):
    (synthetic_media / "broken.mp4").write_bytes(b"not a video")
    index_root = tmp_path / "idx"
    monkeypatch.setattr(
        "persistent_local_index.cli._build_image_embedder",
        lambda *a, **k: make_image_embedder(),
    )
    code = main(
        [
            "index",
            "--input", str(synthetic_media),
            "--index-root", str(index_root),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--device", "cpu",
            "--fake-embedder",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["indexed"] == 2
    assert payload["failed"] == 1


def test_cli_index_does_not_modify_source_media(synthetic_media, tmp_path, capsys, synthetic_model_root, monkeypatch):
    before = {p.name: sha256_file(p) for p in sorted(synthetic_media.glob("*.mp4"))}
    monkeypatch.setattr(
        "persistent_local_index.cli._build_image_embedder",
        lambda *a, **k: make_image_embedder(),
    )
    main(
        [
            "index",
            "--input", str(synthetic_media),
            "--index-root", str(tmp_path / "idx"),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--device", "cpu",
            "--fake-embedder",
        ]
    )
    after = {p.name: sha256_file(p) for p in sorted(synthetic_media.glob("*.mp4"))}
    assert after == before, "SOURCE_MEDIA_MUTATED"


def test_cli_manifest_mirror_tracks_sqlite_after_index(synthetic_media, tmp_path, synthetic_model_root, monkeypatch):
    index_root = tmp_path / "idx"
    monkeypatch.setattr(
        "persistent_local_index.cli._build_image_embedder",
        lambda *a, **k: make_image_embedder(),
    )
    main(
        [
            "index",
            "--input", str(synthetic_media),
            "--index-root", str(index_root),
            "--model-root", str(synthetic_model_root),
            "--weights-sha256", canonical_cli_identity(synthetic_model_root)["weights_sha256"],
            "--model-identity", "google/siglip-base-patch16-224",
            "--model-revision", "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
            "--device", "cpu",
            "--fake-embedder",
        ]
    )
    spec = build_generation_spec(
        make_semantic_space(**canonical_cli_identity(synthetic_model_root))
    )
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    rows, _ = read_committed_counts(conn)
    conn.close()
    assert load_manifest(generation.manifest)["committed_rows"] == rows
