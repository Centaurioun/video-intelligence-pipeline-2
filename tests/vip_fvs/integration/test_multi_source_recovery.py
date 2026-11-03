"""Crash recovery contract for file-backed multi-source reconciliation."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from vip_fvs.multi_source_lifecycle import plan_multi_source_reconciliation


class Entry:
    def __init__(self, locator: str, digest: str, revision: str):
        self.source_path = Path(locator)
        self.source_sha256 = digest
        self.revision_id = revision


class Manifest:
    def __init__(self, label: str, *entries: Entry):
        self.entries = tuple(entries)
        self.manifest_digest = hashlib.sha256(label.encode()).hexdigest()


def api():
    module = importlib.import_module("vip_fvs.multi_source_recovery")
    assert callable(getattr(module, "start_or_resume", None)), "missing start_or_resume journal behavior"
    return module


def pair():
    old = Manifest("old", Entry("A", "a" * 64, "r1"), Entry("gone", "b" * 64, "r2"))
    new = Manifest("new", Entry("A", "c" * 64, "r3"), Entry("added", "b" * 64, "r4"))
    return old, new


def test_run_journal_operation_ids_and_bytes_are_deterministic(tmp_path):
    recovery = api()
    old, new = pair()
    first_path, second_path = tmp_path / "one.json", tmp_path / "two.json"
    first = recovery.start_or_resume(first_path, old, new, generation_id="g", space_id="s")
    second = recovery.start_or_resume(second_path, old, new, generation_id="g", space_id="s")
    assert [item.operation_id for item in first.operations] == [item.operation_id for item in second.operations]
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first_path.read_bytes() == json.dumps(first.to_dict(), sort_keys=True, separators=(",", ":")).encode()


def test_resume_refuses_manifest_generation_or_space_mismatch(tmp_path):
    recovery = api()
    old, new = pair()
    path = tmp_path / "journal.json"
    recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")
    with pytest.raises(recovery.JournalRefusal):
        recovery.start_or_resume(path, old, new, generation_id="other", space_id="s")
    with pytest.raises(recovery.JournalRefusal):
        recovery.start_or_resume(path, old, new, generation_id="g", space_id="other")
    with pytest.raises(recovery.JournalRefusal):
        recovery.start_or_resume(path, old, Manifest("changed", *new.entries), generation_id="g", space_id="s")


def test_crash_before_action_replays_once(tmp_path):
    recovery = api()
    old, new = pair()
    path = tmp_path / "journal.json"
    journal = recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")
    calls = []
    def crash_before(entry):
        calls.append(str(entry.source_path))
        if str(entry.source_path) == "added":
            raise SystemExit("simulated abrupt stop before action")
        return "INDEXED"

    with pytest.raises(SystemExit, match="before action"):
        journal.run(crash_before, lambda _: None)
    assert calls == ["A", "added"]
    resumed = recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")
    resumed.run(lambda entry: calls.append(str(entry.source_path)), lambda _: None)
    assert calls.count("added") == 2


def test_crash_after_side_effect_before_complete_record_converges_idempotently(tmp_path):
    recovery = api()
    old, new = pair()
    path = tmp_path / "journal.json"
    journal = recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")
    effects = []
    def crash_after(entry):
        effects.append(str(entry.source_path))
        if str(entry.source_path) == "added":
            raise SystemExit("simulated abrupt stop after side effect")
        return "INDEXED"

    with pytest.raises(SystemExit, match="after side effect"):
        journal.run(crash_after, lambda _: None)
    resumed = recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")
    assert next(item for item in resumed.operations if item.locator == "added").state == "PENDING"
    resumed.run(lambda entry: effects.append(str(entry.source_path)), lambda _: None)
    assert effects.count("added") == 2


def test_completed_operation_is_not_rerun_on_resume(tmp_path):
    recovery = api()
    old, new = pair()
    path = tmp_path / "journal.json"
    journal = recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")
    calls = []
    journal.run(lambda entry: calls.append(str(entry.source_path)), lambda _: None)
    before = list(calls)
    recovery.start_or_resume(path, old, new, generation_id="g", space_id="s").run(
        lambda entry: calls.append(str(entry.source_path)), lambda _: None
    )
    assert calls == before


def test_corrupt_or_partial_journal_fails_closed(tmp_path):
    recovery = api()
    old, new = pair()
    path = tmp_path / "journal.json"
    path.write_bytes(b'{"schema_version":')
    with pytest.raises(recovery.JournalRefusal):
        recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")


def test_vector_tail_recovery_remains_sqlite_authoritative_before_resume(tmp_path, monkeypatch):
    api()
    import numpy as np
    import persistent_local_index.indexer as indexer
    from persistent_local_index.media import SampledFrame, StreamInfo
    from persistent_local_index.model_space import SemanticSpace
    from vip_fvs.multi_source_recovery import MultiSourceRunJournal
    from vip_fvs.real_source_service import resume_multi_source_reconciliation
    from vip_fvs.source_adapter import MultiSourceManifest, SourceManifestEntry
    from vip_fvs.semantic_index import PersistentLocalSemanticIndexEngine

    source = tmp_path / "source.bin"
    source.write_bytes(b"generated source bytes")
    entry = SourceManifestEntry(
        revision_id="rev", content_id="content:rev", source_path=source,
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="fixture-policy",
        custody_state="PRESERVED",
    )
    old = Manifest("empty")
    new = MultiSourceManifest((entry,), "e" * 64)
    space = SemanticSpace(
        model_identity="generated-fixture", frozen_revision="fixture-v1",
        weights_sha256="1" * 64, processor_digest="2" * 64,
        image_preprocessing_digest="3" * 64,
        text_preprocessing_contract="padding=max_length", embedding_dim=768,
        dtype="float32", normalization="l2",
    )
    engine = PersistentLocalSemanticIndexEngine()
    events = []
    original_tail = indexer.reconcile_vector_tail
    original_persist = MultiSourceRunJournal._persist

    def observe_tail(*args, **kwargs):
        events.append("sqlite_tail_reconciled")
        return original_tail(*args, **kwargs)

    def observe_persist(self):
        if any(item.state == "COMPLETE" for item in self.operations):
            events.append("journal_complete")
        return original_persist(self)

    monkeypatch.setattr(indexer, "reconcile_vector_tail", observe_tail)
    monkeypatch.setattr(MultiSourceRunJournal, "_persist", observe_persist)
    monkeypatch.setattr(indexer, "probe_stream", lambda _path: StreamInfo(0, "synthetic", 16, 16, 1, 1000, 1.0))

    def sample(path, _interval, staging_dir):
        staging_dir = Path(staging_dir)
        staging_dir.mkdir(parents=True, exist_ok=True)
        frame = staging_dir / "frame.png"
        frame.write_bytes(Path(path).read_bytes())
        return [SampledFrame(0, 0.0, 1, 1000, "00:00:00", frame)]

    monkeypatch.setattr(indexer, "sample_one_pass", sample)
    def thumbnail(src, dst):
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        Path(dst).write_bytes(Path(src).read_bytes())

    monkeypatch.setattr(indexer, "make_thumbnail", thumbnail)

    def embed(paths):
        row = np.zeros((len(paths), 768), dtype=np.float32)
        row[:, 0] = 1
        return row

    resume_multi_source_reconciliation(
        tmp_path / "journal.json", old, new, index_root=tmp_path / "index",
        engine=engine, semantic_space=space, image_embedder=embed,
        authorize_source=lambda _entry: True,
    )
    assert "sqlite_tail_reconciled" in events
    assert "journal_complete" in events
    assert events.index("sqlite_tail_reconciled") < events.index("journal_complete")


def test_failed_and_deferred_operations_remain_explicit_and_resumable(tmp_path):
    recovery = api()
    old, new = pair()
    path = tmp_path / "journal.json"
    journal = recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")
    with pytest.raises(RuntimeError):
        journal.run(lambda entry: (_ for _ in ()).throw(RuntimeError("index failed")), lambda _: None)
    observed = recovery.start_or_resume(path, old, new, generation_id="g", space_id="s")
    assert any(item.state == "FAILED" for item in observed.operations)
    assert any(item.state == "DEFERRED" for item in observed.operations)
    observed.run(lambda entry: "INDEXED", lambda _: None)
    assert all(item.state == "COMPLETE" for item in observed.operations)


def _admission_fixture():
    unit_path = str(Path(__file__).resolve().parents[1] / "unit")
    inserted = unit_path not in sys.path
    if inserted:
        sys.path.insert(0, unit_path)
    try:
        p2_fixture = importlib.import_module("test_corpus_admission")
        return p2_fixture._valid_synthetic_attestation()
    finally:
        if inserted:
            sys.path.remove(unit_path)


def _canonical_candidate_manifest(source: Path, digest: str, revision: str):
    from vip_fvs.source_adapter import (
        MultiSourceManifest, SourceManifestEntry, _canonical_manifest_bytes, _manifest_body,
    )

    entry = SourceManifestEntry(
        revision_id=revision, content_id=f"content:{revision}", source_path=source,
        source_sha256=digest, selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="synthetic-policy",
        custody_state="PRESERVED",
    )
    entries = (entry,)
    manifest_digest = hashlib.sha256(_canonical_manifest_bytes(_manifest_body(entries))).hexdigest()
    return MultiSourceManifest(entries, manifest_digest)


def test_opt_in_resume_refuses_stale_batch_before_journal_creation(tmp_path):
    recovery = api()
    attestation, authorization = _admission_fixture()
    source = tmp_path / "candidate.bin"
    source.write_bytes(b"stale bytes")
    old = Manifest("old", Entry("removed", "a" * 64, "old-revision"))
    current = _canonical_candidate_manifest(source, "d" * 64, "candidate-c")
    journal_path = tmp_path / "journal.json"
    with pytest.raises(ValueError, match="CORPUS_SEPARATION_"):
        recovery.start_or_resume(
            journal_path, old, current, generation_id="g", space_id="s",
            synthetic_attestations=(attestation,), synthetic_authorizations=(authorization,),
            authorize_source=lambda _entry: True, preflight_output_root=tmp_path / "index",
        )
    assert not journal_path.exists()
    assert not (tmp_path / "index").exists()


def test_opt_in_replay_rechecks_digest_before_journal_or_callbacks(tmp_path, monkeypatch):
    recovery = api()
    attestation, authorization = _admission_fixture()
    source = tmp_path / "candidate.bin"
    source.write_bytes(b"fixture")
    old = Manifest("old", Entry("removed", "a" * 64, "old-revision"))
    current = _canonical_candidate_manifest(source, "d" * 64, "candidate-c")
    monkeypatch.setattr("vip_fvs.multi_source_index._digest_file", lambda _path: "d" * 64)
    kwargs = dict(
        generation_id="g", space_id="s", synthetic_attestations=(attestation,),
        synthetic_authorizations=(authorization,), authorize_source=lambda _entry: True,
        preflight_output_root=tmp_path / "index",
    )
    journal = recovery.start_or_resume(tmp_path / "journal.json", old, current, **kwargs)
    before = journal.path.read_bytes()
    monkeypatch.setattr("vip_fvs.multi_source_index._digest_file", lambda _path: "f" * 64)
    calls = []
    with pytest.raises(ValueError, match="CORPUS_SEPARATION_"):
        journal.run(lambda _entry: calls.append("index"), lambda _locator: calls.append("remove"))
    assert calls == []
    assert journal.path.read_bytes() == before
