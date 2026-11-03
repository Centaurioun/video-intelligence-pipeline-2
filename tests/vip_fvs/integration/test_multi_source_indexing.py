"""Focused contract tests for explicit-manifest multi-source indexing.

All source bytes in this module are generated fixtures.  The fake engine makes
ordering, authorization, digest checks, reuse, and isolation observable without
loading a model or invoking a media decoder.
"""
from __future__ import annotations

import hashlib
import importlib
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest

import persistent_local_index.indexer as persistent_indexer
from persistent_local_index.media import SampledFrame, StreamInfo
from persistent_local_index.model_space import SemanticSpace, build_generation_spec
from persistent_local_index.storage import connect_db, open_or_create_generation, read_committed_counts
from vip_fvs.semantic_index import PersistentLocalSemanticIndexEngine
from vip_fvs.source_adapter import MultiSourceManifest, SourceManifestEntry


def _entry(path: Path, revision: str, payload: bytes) -> SourceManifestEntry:
    digest = hashlib.sha256(payload).hexdigest()
    return SourceManifestEntry(
        revision_id=revision,
        content_id=f"content-{revision}",
        source_path=path,
        source_sha256=digest,
        selected_stream_index=0,
        selection_source="generated-fixture",
        inventory_digest="1" * 64,
        policy_decision_ref="discovery-policy-fixture",
        custody_state="PRESERVED",
    )


def _manifest(entries: tuple[SourceManifestEntry, ...]) -> MultiSourceManifest:
    # The orchestrator contract treats this as an already-validated manifest;
    # its digest is a deterministic stand-in for these orchestration tests.
    return MultiSourceManifest(entries=entries, manifest_digest="2" * 64)


def _canonical_manifest(entries: tuple[SourceManifestEntry, ...]) -> MultiSourceManifest:
    from vip_fvs.source_adapter import _canonical_manifest_bytes, _manifest_body
    digest = hashlib.sha256(_canonical_manifest_bytes(_manifest_body(entries))).hexdigest()
    return MultiSourceManifest(entries=entries, manifest_digest=digest)


class _Engine:
    def __init__(self, outcomes=None):
        self.calls = []
        self.outcomes = outcomes or {}

    def build_generation_spec(self, space):
        self.calls.append(("build", space))
        return SimpleNamespace(generation_id="generation-fixture", space_id="space-fixture")

    def index_source(self, input_path, index_root, spec, image_embedder):
        self.calls.append(("index", Path(input_path)))
        outcome = self.outcomes.get(Path(input_path))
        if isinstance(outcome, Exception):
            raise outcome
        return outcome or SimpleNamespace(
            path=str(input_path),
            source_sha256=hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
            disposition="INDEXED",
            row_start=0, row_end=1, error=None,
        )

    def query(self, *args, **kwargs):
        pytest.fail("multi-source indexing must not query")


def _api():
    try:
        from vip_fvs.multi_source_index import index_multi_source_manifest
    except ModuleNotFoundError as exc:
        if exc.name == "vip_fvs.multi_source_index":
            pytest.fail("required multi-source indexing entrypoint is not implemented")
        raise
    return index_multi_source_manifest


def test_multi_source_index_entrypoint_exists():
    assert callable(_api())


def _invoke(manifest, engine, index_root, authorizer, *, space=None):
    return _api()(
        manifest,
        index_root=index_root,
        engine=engine,
        semantic_space=space or object(),
        image_embedder=lambda paths: pytest.fail("fake engine should not embed"),
        authorize_source=authorizer,
    )


def test_multi_source_index_processes_exact_manifest_order_only(tmp_path: Path):
    first = tmp_path / "first.bin"
    second = tmp_path / "second.bin"
    extra = tmp_path / "not-in-manifest.bin"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    extra.write_bytes(b"must not be discovered")
    entries = tuple(sorted((_entry(first, "rev-a", b"first"), _entry(second, "rev-b", b"second")), key=lambda e: e.revision_id))
    engine = _Engine()
    authorizations = []

    _invoke(_manifest(entries), engine, tmp_path / "index", lambda entry: authorizations.append(entry.revision_id) or True)

    assert authorizations == [entry.revision_id for entry in entries]
    assert [path for kind, path in engine.calls if kind == "index"] == [entry.source_path for entry in entries]
    assert extra not in [path for kind, path in engine.calls if kind == "index"]


def test_multi_source_index_requires_explicit_authorizer_before_source_read_or_index(tmp_path: Path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"generated")
    entry = _entry(source, "rev-a", b"generated")
    engine = _Engine()

    with pytest.raises((TypeError, ValueError), match="authoriz|authorization"):
        _api()(
            _manifest((entry,)), index_root=tmp_path / "index", engine=engine,
            semantic_space=object(), image_embedder=lambda paths: None,
        )
    assert engine.calls == []

    result = _invoke(_manifest((entry,)), engine, tmp_path / "index", lambda _entry: False)
    assert not [call for call in engine.calls if call[0] == "index"]
    assert result.results[0].disposition in {"REFUSED", "FAILED"}


def _admission_fixture(**kwargs):
    # Frozen synthetic P1 fixture; never represents real admission.
    unit_path = str(Path(__file__).resolve().parents[1] / "unit")
    inserted = unit_path not in sys.path
    if inserted:
        sys.path.insert(0, unit_path)
    try:
        p2_fixture = importlib.import_module("test_corpus_admission")
        return p2_fixture._valid_synthetic_attestation(**kwargs)
    finally:
        if inserted:
            sys.path.remove(unit_path)


def test_opt_in_preflight_rejects_late_binding_before_spec_source_read_or_index(tmp_path: Path, monkeypatch):
    from vip_fvs import multi_source_index as module
    attestation, authorization = _admission_fixture()
    first, second = tmp_path / "first.bin", tmp_path / "second.bin"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    entry_type = type(_entry(first, "candidate-c", b"first"))
    entries = (entry_type(
        revision_id="candidate-c", content_id="content-c", source_path=first,
        source_sha256="d" * 64, selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="discovery-policy-fixture", custody_state="PRESERVED",
    ), entry_type(
        revision_id="rev-second", content_id="content-second", source_path=second,
        source_sha256="e" * 64, selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="discovery-policy-fixture", custody_state="PRESERVED",
    ))
    engine = _Engine()
    reads = []
    monkeypatch.setattr(module, "_digest_file", lambda path: reads.append(path) or "0" * 64)
    with pytest.raises(ValueError, match="CORPUS_SEPARATION_"):
        module.index_multi_source_manifest(
            _canonical_manifest(entries), index_root=tmp_path / "index", engine=engine, semantic_space=object(),
            image_embedder=lambda paths: None, authorize_source=lambda _entry: True,
            synthetic_attestations=(attestation, attestation),
            synthetic_authorizations=(authorization, authorization),
        )
    assert engine.calls == []
    assert reads == []


def test_opt_in_preflight_digest_checks_whole_batch_before_engine_spec(tmp_path: Path):
    from vip_fvs import multi_source_index as module
    attestation, authorization = _admission_fixture()
    source = tmp_path / "candidate.bin"
    source.write_bytes(b"changed since synthetic evidence")
    entry = type(_entry(source, "candidate-c", b"unused"))(
        revision_id="candidate-c", content_id="content-c", source_path=source,
        source_sha256="d" * 64, selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="discovery-policy-fixture", custody_state="PRESERVED",
    )
    manifest = _canonical_manifest((entry,))
    engine = _Engine()
    with pytest.raises(ValueError, match="CORPUS_SEPARATION_"):
        module.index_multi_source_manifest(
            manifest, index_root=tmp_path / "index", engine=engine, semantic_space=object(),
            image_embedder=lambda paths: None, authorize_source=lambda _entry: True,
            synthetic_attestations=(attestation,), synthetic_authorizations=(authorization,),
        )
    assert engine.calls == []
    assert not (tmp_path / "index").exists()


def test_opt_in_preflight_rejects_noncanonical_manifest_digest_before_entry_checks(tmp_path: Path, monkeypatch):
    from vip_fvs import multi_source_index as module
    from vip_fvs.corpus_admission import CorpusAdmissionError
    from vip_fvs.source_adapter import MultiSourceManifest

    attestation, authorization = _admission_fixture()
    source = tmp_path / "candidate.bin"
    source.write_bytes(b"synthetic fixture")
    base = _entry(source, "candidate-c", b"placeholder")
    entry = type(base)(
        revision_id="candidate-c", content_id=base.content_id, source_path=source,
        source_sha256="d" * 64, selected_stream_index=base.selected_stream_index,
        selection_source=base.selection_source, inventory_digest=base.inventory_digest,
        policy_decision_ref=base.policy_decision_ref, custody_state=base.custody_state,
    )
    manifest = MultiSourceManifest((entry,), "0" * 64)
    engine = _Engine()
    byte_checks = []
    monkeypatch.setattr(module, "_digest_file", lambda _path: byte_checks.append("hash") or "d" * 64)

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        module.index_multi_source_manifest(
            manifest, index_root=tmp_path / "index", engine=engine, semantic_space=object(),
            image_embedder=lambda paths: None, authorize_source=lambda _entry: True,
            synthetic_attestations=(attestation,), synthetic_authorizations=(authorization,),
        )

    assert byte_checks == []
    assert engine.calls == []


def test_opt_in_preflight_rechecks_all_source_bytes_after_generation_spec_before_index(tmp_path: Path):
    from vip_fvs import multi_source_index as module
    from vip_fvs.corpus_admission import CorpusAdmissionError

    source = tmp_path / "candidate.bin"
    original_bytes = b"bound synthetic candidate"
    source.write_bytes(original_bytes)
    source_digest = hashlib.sha256(original_bytes).hexdigest()
    attestation, authorization = _admission_fixture(source_sha256=source_digest)
    base = _entry(source, "candidate-c", original_bytes)
    entry = type(base)(
        revision_id=base.revision_id, content_id=base.content_id, source_path=source,
        source_sha256=source_digest, selected_stream_index=base.selected_stream_index,
        selection_source=base.selection_source, inventory_digest=base.inventory_digest,
        policy_decision_ref=base.policy_decision_ref, custody_state=base.custody_state,
    )

    class MutatingEngine(_Engine):
        def build_generation_spec(self, space):
            spec = super().build_generation_spec(space)
            source.write_bytes(b"changed after preflight")
            return spec

    engine = MutatingEngine()
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        module.index_multi_source_manifest(
            _canonical_manifest((entry,)), index_root=tmp_path / "index", engine=engine,
            semantic_space=object(), image_embedder=lambda _paths: None,
            authorize_source=lambda _entry: True,
            synthetic_attestations=(attestation,),
            synthetic_authorizations=(authorization,),
        )

    assert [kind for kind, _ in engine.calls] == ["build"]
    assert not (tmp_path / "index").exists()


def test_source_digest_change_refuses_that_entry_without_touching_unrelated_complete_entries(tmp_path: Path):
    changed = tmp_path / "changed.bin"
    good = tmp_path / "good.bin"
    changed.write_bytes(b"changed-after-snapshot")
    good.write_bytes(b"still-valid")
    entries = tuple(sorted((
        _entry(changed, "rev-a", b"snapshot-bytes"),
        _entry(good, "rev-b", b"still-valid"),
    ), key=lambda e: e.revision_id))
    indexed_good = SimpleNamespace(path=str(good), source_sha256=entries[1].source_sha256,
                                   disposition="SKIPPED_UNCHANGED", row_start=7, row_end=9, error=None)
    engine = _Engine({good: indexed_good})

    result = _invoke(_manifest(entries), engine, tmp_path / "index", lambda _entry: True)

    assert result.results[0].disposition in {"REFUSED", "FAILED"}
    assert (result.results[1].disposition, result.results[1].row_start, result.results[1].row_end) == ("SKIPPED_UNCHANGED", 7, 9)
    assert [path for kind, path in engine.calls if kind == "index"] == [good]


def test_engine_observed_digest_mismatch_is_not_reported_as_indexed(tmp_path: Path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"manifest-authorized")
    entry = _entry(source, "rev-a", b"manifest-authorized")
    engine = _Engine({source: SimpleNamespace(
        path=str(source), source_sha256="9" * 64, disposition="INDEXED",
        row_start=0, row_end=1, error=None,
    )})

    result = _invoke(_manifest((entry,)), engine, tmp_path / "index", lambda _entry: True)

    assert result.results[0].disposition == "REFUSED"
    assert result.results[0].error == "SOURCE_DIGEST_MISMATCH_AFTER_INDEX"


def test_duplicate_bytes_at_second_locator_preserve_reused_duplicate_disposition_and_row_range(tmp_path: Path):
    one, two = tmp_path / "one.bin", tmp_path / "two.bin"
    one.write_bytes(b"same bytes")
    two.write_bytes(b"same bytes")
    entries = tuple(sorted((_entry(one, "rev-a", b"same bytes"), _entry(two, "rev-b", b"same bytes")), key=lambda e: e.revision_id))
    duplicate = SimpleNamespace(path=str(two), source_sha256=entries[1].source_sha256,
                                disposition="REUSED_DUPLICATE", row_start=3, row_end=8, error=None)
    engine = _Engine({two: duplicate})

    result = _invoke(_manifest(entries), engine, tmp_path / "index", lambda _entry: True)

    assert result.results[1].disposition == "REUSED_DUPLICATE"
    assert (result.results[1].row_start, result.results[1].row_end) == (3, 8)
    assert [path for kind, path in engine.calls if kind == "index"] == [one, two]


def test_one_source_failure_is_recorded_and_later_independent_entries_continue(tmp_path: Path):
    paths = [tmp_path / f"{name}.bin" for name in ("a", "b", "c")]
    for path in paths:
        path.write_bytes(path.name.encode())
    entries = tuple(_entry(path, f"rev-{i}", path.name.encode()) for i, path in enumerate(paths))
    engine = _Engine({paths[1]: RuntimeError("synthetic source failure")})

    result = _invoke(_manifest(entries), engine, tmp_path / "index", lambda _entry: True)

    assert [row.disposition for row in result.results] == ["INDEXED", "FAILED", "INDEXED"]
    assert [path for kind, path in engine.calls if kind == "index"] == paths


def test_multi_source_index_returns_one_result_per_manifest_entry_with_generation_and_space_identity(tmp_path: Path):
    paths = [tmp_path / "a.bin", tmp_path / "b.bin"]
    for path in paths:
        path.write_bytes(path.name.encode())
    entries = tuple(_entry(path, f"rev-{i}", path.name.encode()) for i, path in enumerate(paths))
    engine = _Engine()

    result = _invoke(_manifest(entries), engine, tmp_path / "index", lambda _entry: True)

    assert result.manifest_digest == "2" * 64
    assert result.generation_id == "generation-fixture"
    assert result.space_id == "space-fixture"
    assert len(result.results) == len(entries)
    assert [row.revision_id for row in result.results] == [entry.revision_id for entry in entries]


def test_multi_source_index_never_queries_refines_renders_or_mutates_source_bytes(tmp_path: Path):
    source = tmp_path / "source.bin"
    original = b"immutable generated source"
    source.write_bytes(original)
    entry = _entry(source, "rev-a", original)
    engine = _Engine()
    before = hashlib.sha256(source.read_bytes()).hexdigest()

    _invoke(_manifest((entry,)), engine, tmp_path / "index", lambda _entry: True)

    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert source.read_bytes() == original
    assert all(kind in {"build", "index"} for kind, *_ in engine.calls)


def _persistent_harness(monkeypatch, *, index_root: Path, on_sample=None):
    """Run the real indexer with generated source bytes and fake media seams."""
    observed_media_inputs = []

    def probe(path):
        path = Path(path)
        observed_media_inputs.append(("probe", path, path.read_bytes()))
        return StreamInfo(0, "synthetic", 16, 16, 1, 1000, 1.0)

    def sample(path, _interval, staging_dir):
        path = Path(path)
        payload = path.read_bytes()
        observed_media_inputs.append(("sample", path, payload))
        if on_sample is not None:
            on_sample(path, payload)
        staging_dir = Path(staging_dir)
        staging_dir.mkdir(parents=True, exist_ok=True)
        frame_path = staging_dir / "frame.png"
        frame_path.write_bytes(b"synthetic frame derived from:" + payload)
        return [SampledFrame(0, 0.0, 1, 1000, "00:00:00.000", frame_path)]

    def thumbnail(src, dst):
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        Path(dst).write_bytes(Path(src).read_bytes())

    monkeypatch.setattr(persistent_indexer, "probe_stream", probe)
    monkeypatch.setattr(persistent_indexer, "sample_one_pass", sample)
    monkeypatch.setattr(persistent_indexer, "make_thumbnail", thumbnail)
    space = SemanticSpace(
        model_identity="generated-fixture", frozen_revision="fixture-v1",
        weights_sha256="1" * 64, processor_digest="2" * 64,
        image_preprocessing_digest="3" * 64,
        text_preprocessing_contract="padding=max_length", embedding_dim=768,
        dtype="float32", normalization="l2",
    )

    def embed(paths):
        rows = []
        for path in paths:
            seed = hashlib.sha256(Path(path).read_bytes()).digest()
            row = np.zeros(768, dtype=np.float32)
            row[0] = 1.0
            row[1] = seed[0] / 255.0
            row /= np.linalg.norm(row)
            rows.append(row)
        return np.stack(rows).astype(np.float32)

    return (PersistentLocalSemanticIndexEngine(), space, embed, observed_media_inputs)


def _persistent_invoke(manifest, harness, index_root, *, authorize=lambda _entry: True):
    engine, space, embed, _observed = harness
    return _api()(
        manifest, index_root=index_root, engine=engine, semantic_space=space,
        image_embedder=embed, authorize_source=authorize,
    )


def test_indexer_refuses_locator_change_after_snapshot_without_persisting_source_rows(
    tmp_path: Path, monkeypatch,
):
    seed = tmp_path / "seed.mp4"
    changed = tmp_path / "changed.mp4"
    good = tmp_path / "good.mp4"
    seed.write_bytes(b"same-content")
    changed.write_bytes(b"same-content")
    good.write_bytes(b"independent-content")
    index_root = tmp_path / "index"
    harness = _persistent_harness(monkeypatch, index_root=index_root)
    _persistent_invoke(_manifest((_entry(seed, "seed", seed.read_bytes()),)), harness, index_root)

    original_is_new_location = persistent_indexer._is_new_location

    def mutate_after_snapshot(conn, path, digest):
        is_new = original_is_new_location(conn, path, digest)
        if Path(path) == changed:
            changed.write_bytes(b"replaced-after-snapshot")
        return is_new

    monkeypatch.setattr(persistent_indexer, "_is_new_location", mutate_after_snapshot)
    result = _persistent_invoke(
        _manifest((_entry(changed, "changed", b"same-content"),
                   _entry(good, "good", b"independent-content"))),
        harness, index_root,
    )

    assert result.results[0].disposition == "FAILED"
    assert "SOURCE_CHANGED_DURING_INDEXING" in (result.results[0].error or "")
    assert result.results[1].disposition == "INDEXED"
    generation = open_or_create_generation(index_root, build_generation_spec(harness[1]))
    conn = connect_db(generation)
    assert conn.execute("SELECT 1 FROM source_locations WHERE path=?", (str(changed),)).fetchone() is None
    assert conn.execute("SELECT COUNT(*) FROM samples WHERE source_sha256=?",
                        (hashlib.sha256(b"same-content").hexdigest(),)).fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM source_locations WHERE path=?", (str(good),)).fetchone()[0] == 1
    conn.close()


def test_association_write_uses_pre_mutation_snapshot_observation(tmp_path: Path, monkeypatch):
    source = tmp_path / "source.mp4"
    original = b"authorized-synthetic-content"
    replacement = b"replacement-bytes-with-a-different-size"
    source.write_bytes(original)
    os.utime(source, ns=(1_700_000_000_000_000_000, 1_700_000_000_000_000_000))
    observed_size = source.stat().st_size
    observed_mtime_ns = source.stat().st_mtime_ns
    index_root = tmp_path / "index"
    harness = _persistent_harness(monkeypatch, index_root=index_root)
    original_upsert = persistent_indexer._upsert_location

    def replace_after_final_guard(conn, *args):
        observation_or_path = args[0]
        path = (observation_or_path.source_path
                if hasattr(observation_or_path, "source_path") else observation_or_path)
        Path(path).write_bytes(replacement)
        os.utime(path, ns=(1_800_000_000_000_000_000, 1_800_000_000_000_000_000))
        return original_upsert(conn, *args)

    monkeypatch.setattr(persistent_indexer, "_upsert_location", replace_after_final_guard)
    monkeypatch.setattr(
        persistent_indexer, "_utc_now",
        lambda: "T_OBS" if source.read_bytes() == original else "T_AFTER",
    )
    result = _persistent_invoke(
        _manifest((_entry(source, "source", original),)), harness, index_root
    )

    assert result.results[0].disposition == "INDEXED"
    assert harness[3]
    assert all(path != source and payload == original
               for _kind, path, payload in harness[3])
    generation = open_or_create_generation(index_root, build_generation_spec(harness[1]))
    conn = connect_db(generation)
    row = conn.execute(
        "SELECT source_sha256,last_observed_size,last_observed_mtime_ns,last_observed_at "
        "FROM source_locations WHERE path=?", (str(source),),
    ).fetchone()
    conn.close()
    assert tuple(row) == (
        hashlib.sha256(original).hexdigest(), observed_size, observed_mtime_ns, "T_OBS"
    )


def test_duplicate_content_keeps_distinct_locator_observations_deterministically(
    tmp_path: Path, monkeypatch,
):
    one, two = tmp_path / "one.mp4", tmp_path / "two.mp4"
    payload = b"one-content-two-locators"
    one.write_bytes(payload)
    two.write_bytes(payload)
    os.utime(one, ns=(1_700_000_000_000_000_000, 1_700_000_000_000_000_000))
    os.utime(two, ns=(1_710_000_000_000_000_000, 1_710_000_000_000_000_000))
    expected = {one: (one.stat().st_size, one.stat().st_mtime_ns),
                two: (two.stat().st_size, two.stat().st_mtime_ns)}
    index_root = tmp_path / "index"
    harness = _persistent_harness(monkeypatch, index_root=index_root)
    manifest = _manifest((_entry(one, "a", payload), _entry(two, "b", payload)))

    first = _persistent_invoke(manifest, harness, index_root)
    second = _persistent_invoke(manifest, harness, index_root)
    assert [row.disposition for row in first.results] == ["INDEXED", "REUSED_DUPLICATE"]
    assert [row.disposition for row in second.results] == ["SKIPPED_UNCHANGED", "SKIPPED_UNCHANGED"]
    assert [row.source_path for row in first.results] == [one, two]
    generation = open_or_create_generation(index_root, build_generation_spec(harness[1]))
    conn = connect_db(generation)
    assert read_committed_counts(conn)[0] == 1
    rows = conn.execute(
        "SELECT path,source_sha256,last_observed_size,last_observed_mtime_ns "
        "FROM source_locations ORDER BY path"
    ).fetchall()
    assert len(rows) == 2
    assert {Path(row["path"]): (row["last_observed_size"], row["last_observed_mtime_ns"])
            for row in rows} == expected
    assert len({row["source_sha256"] for row in rows}) == 1
    conn.close()


def test_removal_last_location_and_restart_preserve_historical_observation(
    tmp_path: Path, monkeypatch,
):
    one, two = tmp_path / "one.mp4", tmp_path / "two.mp4"
    payload = b"duplicate-content"
    one.write_bytes(payload)
    two.write_bytes(payload)
    index_root = tmp_path / "index"
    harness = _persistent_harness(monkeypatch, index_root=index_root)
    manifest = _manifest((_entry(one, "a", payload), _entry(two, "b", payload)))
    _persistent_invoke(manifest, harness, index_root)
    spec = build_generation_spec(harness[1])
    generation = open_or_create_generation(index_root, spec)
    conn = connect_db(generation)
    before = tuple(conn.execute(
        "SELECT source_sha256,last_observed_size,last_observed_mtime_ns,last_observed_at "
        "FROM source_locations WHERE path=?", (str(two),),
    ).fetchone())
    conn.close()

    two.write_bytes(b"mutable-path-now-different")
    reopened = open_or_create_generation(index_root, spec)
    conn = connect_db(reopened)
    after = tuple(conn.execute(
        "SELECT source_sha256,last_observed_size,last_observed_mtime_ns,last_observed_at "
        "FROM source_locations WHERE path=?", (str(two),),
    ).fetchone())
    conn.close()
    assert after == before

    remove_one = persistent_indexer.remove_source_location(index_root, spec, one)
    conn = connect_db(reopened)
    digest = hashlib.sha256(payload).hexdigest()
    obj = conn.execute("SELECT state,active FROM source_objects WHERE source_sha256=?", (digest,)).fetchone()
    assert obj["state"] == "COMPLETE" and obj["active"] == 1
    assert conn.execute("SELECT COUNT(*) FROM samples WHERE source_sha256=? AND active=1", (digest,)).fetchone()[0] == 1
    conn.close()
    assert remove_one.removed is True and remove_one.object_superseded is False

    remove_two = persistent_indexer.remove_source_location(index_root, spec, two)
    repeated = persistent_indexer.remove_source_location(index_root, spec, two)
    conn = connect_db(reopened)
    obj = conn.execute("SELECT state,active FROM source_objects WHERE source_sha256=?", (digest,)).fetchone()
    assert obj["state"] == "SUPERSEDED" and obj["active"] == 0
    assert conn.execute("SELECT COUNT(*) FROM samples WHERE source_sha256=? AND active=1", (digest,)).fetchone()[0] == 0
    conn.close()
    assert remove_two.removed is True and remove_two.object_superseded is True
    assert repeated.removed is False and repeated.object_superseded is False
