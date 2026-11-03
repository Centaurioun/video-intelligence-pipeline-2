from dataclasses import dataclass
import hashlib
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest

import persistent_local_index.indexer as persistent_indexer
from persistent_local_index.media import SampledFrame, StreamInfo
from persistent_local_index.model_space import SemanticSpace
from persistent_local_index.storage import connect_db, open_or_create_generation
from vip_fvs.semantic_index import PersistentLocalSemanticIndexEngine
from vip_fvs.multi_source_index import index_multi_source_manifest
from vip_fvs.source_adapter import MultiSourceManifest, SourceManifestEntry

from vip_fvs.multi_source_lifecycle import (
    plan_multi_source_reconciliation,
    reconcile_multi_source_index,
    reconcile_multi_source_manifests,
)


@dataclass(frozen=True)
class Entry:
    source_path: Path
    source_sha256: str
    revision_id: str


@dataclass(frozen=True)
class Manifest:
    entries: tuple[Entry, ...]
    manifest_digest: str


def entry(path, digest, revision=None):
    return Entry(Path(path), digest, revision or f"revision:{path}")


def manifest(label, *entries):
    return Manifest(tuple(entries), label * 64)


def source_entry(path, revision, payload):
    return SourceManifestEntry(
        revision_id=revision, content_id=f"content:{revision}", source_path=path,
        source_sha256=hashlib.sha256(payload).hexdigest(), selected_stream_index=0,
        selection_source="generated-fixture", inventory_digest="1" * 64,
        policy_decision_ref="fixture-policy", custody_state="PRESERVED",
    )


def persistent_harness(monkeypatch):
    def probe(_path):
        return StreamInfo(0, "synthetic", 16, 16, 1, 1000, 1.0)
    def sample(path, _interval, staging_dir):
        staging_dir = Path(staging_dir)
        staging_dir.mkdir(parents=True, exist_ok=True)
        frame = staging_dir / "frame.png"
        frame.write_bytes(b"frame:" + Path(path).read_bytes())
        return [SampledFrame(0, 0.0, 1, 1000, "00:00:00", frame)]
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
            row = np.zeros(768, dtype=np.float32)
            row[0] = 1.0
            row[1] = hashlib.sha256(Path(path).read_bytes()).digest()[0] / 255.0
            row /= np.linalg.norm(row)
            rows.append(row)
        return np.stack(rows)
    return PersistentLocalSemanticIndexEngine(), space, embed


def closed_manifest(*entries):
    ordered = tuple(sorted(entries, key=lambda item: (item.revision_id.encode(), str(item.source_path).encode())))
    return MultiSourceManifest(ordered, "2" * 64)


def test_manifest_delta_classifies_unchanged_added_changed_removed_deterministically():
    old = manifest("a", entry("z", "same"), entry("change", "old"), entry("gone", "gone"))
    new = manifest("b", entry("z", "same"), entry("change", "new"), entry("added", "fresh"))
    plan = plan_multi_source_reconciliation(old, new)
    assert [(op.locator, op.kind) for op in plan.operations] == [
        ("added", "ADDED"), ("change", "CHANGED"),
        ("z", "UNCHANGED"), ("gone", "REMOVED"),
    ]
    assert plan == plan_multi_source_reconciliation(old, new)
    assert plan.operations[1].current_entry.revision_id == "revision:change"


def test_same_digest_move_adds_new_location_before_removing_old_location():
    old, new = manifest("a", entry("A", "d")), manifest("b", entry("B", "d"))
    calls = []
    result = reconcile_multi_source_manifests(
        old, new,
        index_entry=lambda item: calls.append(("index", str(item.source_path))) or type("R", (), {"disposition": "REUSED_DUPLICATE"})(),
        remove_location=lambda locator: calls.append(("remove", locator)),
        generation_id="g", space_id="s",
    )
    assert calls == [("index", "B"), ("remove", "A")]
    assert result.deferred_removals == ()
    assert result.previous_manifest_digest == "a" * 64


def test_failed_same_digest_replacement_defers_old_location_removal():
    old, new = manifest("a", entry("A", "d")), manifest("b", entry("B", "d"))
    removals = []
    result = reconcile_multi_source_manifests(
        old, new,
        index_entry=lambda _: (_ for _ in ()).throw(RuntimeError("no replacement")),
        remove_location=removals.append, generation_id="g", space_id="s",
    )
    assert result.deferred_removals == ("A",)
    assert removals == []


def test_unrelated_removal_can_complete_when_another_addition_fails():
    old = manifest("a", entry("A", "move"), entry("unrelated", "x"))
    new = manifest("b", entry("B", "move"), entry("new", "new"))
    removed = []
    def index(item):
        if str(item.source_path) == "B":
            raise RuntimeError("replacement failed")
        return type("R", (), {"disposition": "INDEXED"})()
    result = reconcile_multi_source_manifests(
        old, new, index_entry=index, remove_location=removed.append,
        generation_id="g", space_id="s",
    )
    assert result.deferred_removals == ("A",)
    assert removed == ["unrelated"]


def test_changed_path_indexes_new_digest_without_pre_removing_old_location():
    old, new = manifest("a", entry("A", "old")), manifest("b", entry("A", "new"))
    calls = []
    reconcile_multi_source_manifests(
        old, new,
        index_entry=lambda item: calls.append(("index", item.source_sha256)) or type("R", (), {"disposition": "INDEXED"})(),
        remove_location=lambda locator: calls.append(("remove", locator)),
        generation_id="g", space_id="s",
    )
    assert calls == [("index", "new")]


def test_reconciliation_is_idempotent_when_reapplied_to_same_previous_current_pair():
    old, new = manifest("a", entry("A", "old")), manifest("b", entry("A", "new"))
    def run():
        return reconcile_multi_source_manifests(
            old, new,
            index_entry=lambda _: "SKIPPED_UNCHANGED",
            remove_location=lambda _: None, generation_id="g", space_id="s",
        )
    assert run() == run()


def test_same_digest_move_reuses_location_before_exact_old_location_removal(tmp_path, monkeypatch):
    a, b = tmp_path / "A.bin", tmp_path / "B.bin"
    a.write_bytes(b"same generated bytes")
    b.write_bytes(a.read_bytes())
    old = closed_manifest(source_entry(a, "rev-a", a.read_bytes()))
    new = closed_manifest(source_entry(b, "rev-b", b.read_bytes()))
    engine, space, embed = persistent_harness(monkeypatch)
    root = tmp_path / "index"
    index_multi_source_manifest(
        old, index_root=root, engine=engine, semantic_space=space,
        image_embedder=embed, authorize_source=lambda _entry: True,
    )
    reconcile_multi_source_index(
        old, new, index_root=root, engine=engine, semantic_space=space,
        image_embedder=embed, authorize_source=lambda _entry: True,
    )
    spec = engine.build_generation_spec(space)
    generation = open_or_create_generation(root, spec)
    conn = connect_db(generation)
    assert conn.execute("SELECT source_sha256 FROM source_locations WHERE path=?", (str(a),)).fetchone() is None
    assert conn.execute("SELECT source_sha256 FROM source_locations WHERE path=?", (str(b),)).fetchone()[0] == hashlib.sha256(b.read_bytes()).hexdigest()
    assert conn.execute("SELECT state, active FROM source_objects").fetchone()[:] == ("COMPLETE", 1)
    conn.close()


def test_successful_reconciliation_removing_last_digest_location_supersedes_it(tmp_path, monkeypatch):
    a, b = tmp_path / "A.bin", tmp_path / "B.bin"
    a.write_bytes(b"old generated bytes")
    b.write_bytes(b"new unrelated bytes")
    old = closed_manifest(source_entry(a, "rev-a", a.read_bytes()))
    current = closed_manifest(source_entry(b, "rev-b", b.read_bytes()))
    engine, space, embed = persistent_harness(monkeypatch)
    root = tmp_path / "index"
    index_multi_source_manifest(
        old, index_root=root, engine=engine, semantic_space=space,
        image_embedder=embed, authorize_source=lambda _entry: True,
    )
    reconcile_multi_source_index(
        old, current, index_root=root, engine=engine, semantic_space=space,
        image_embedder=embed, authorize_source=lambda _entry: True,
    )
    spec = engine.build_generation_spec(space)
    generation = open_or_create_generation(root, spec)
    conn = connect_db(generation)
    old_digest = hashlib.sha256(a.read_bytes()).hexdigest()
    assert conn.execute("SELECT state, active FROM source_objects WHERE source_sha256=?", (old_digest,)).fetchone()[:] == ("SUPERSEDED", 0)
    assert conn.execute("SELECT active FROM samples WHERE source_sha256=?", (old_digest,)).fetchone()[0] == 0
    conn.close()


def test_repeated_real_index_removal_reports_already_absent(tmp_path, monkeypatch):
    source = tmp_path / "present.bin"
    source.write_bytes(b"synthetic source bytes")
    replacement = tmp_path / "replacement.bin"
    replacement.write_bytes(b"different synthetic bytes")
    old = closed_manifest(source_entry(source, "rev-a", source.read_bytes()))
    current = closed_manifest(source_entry(replacement, "rev-b", replacement.read_bytes()))
    engine, space, embed = persistent_harness(monkeypatch)
    root = tmp_path / "index"
    index_multi_source_manifest(
        old, index_root=root, engine=engine, semantic_space=space,
        image_embedder=embed, authorize_source=lambda _entry: True,
    )

    first = reconcile_multi_source_index(
        old, current, index_root=root, engine=engine, semantic_space=space,
        image_embedder=embed, authorize_source=lambda _entry: True,
    )
    second = reconcile_multi_source_index(
        old, current, index_root=root, engine=engine, semantic_space=space,
        image_embedder=embed, authorize_source=lambda _entry: True,
    )

    removal_dispositions = [
        next(item.disposition for item in result.dispositions if item.kind == "REMOVED")
        for result in (first, second)
    ]
    assert removal_dispositions == ["REMOVED", "ALREADY_ABSENT"]


def test_opt_in_reconciliation_checks_all_source_bytes_before_spec_or_removal(tmp_path, monkeypatch):
    from vip_fvs import multi_source_lifecycle as lifecycle
    from vip_fvs.source_adapter import (
        MultiSourceManifest, _canonical_manifest_bytes, _manifest_body,
    )

    unit_path = str(Path(__file__).resolve().parents[1] / "unit")
    inserted = unit_path not in sys.path
    if inserted:
        sys.path.insert(0, unit_path)
    try:
        p2_fixture = importlib.import_module("test_corpus_admission")
        attestation, authorization = p2_fixture._valid_synthetic_attestation()
    finally:
        if inserted:
            sys.path.remove(unit_path)
    source = tmp_path / "candidate.bin"
    source.write_bytes(b"not the attested digest")
    candidate = SourceManifestEntry(
        revision_id="candidate-c", content_id="content-c", source_path=source,
        source_sha256="d" * 64, selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="discovery-policy-fixture", custody_state="PRESERVED",
    )
    previous_entry = SourceManifestEntry(
        revision_id="previous", content_id="previous-content", source_path=tmp_path / "removed.bin",
        source_sha256="a" * 64, selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="fixture-policy", custody_state="PRESERVED",
    )
    previous = MultiSourceManifest((previous_entry,), "3" * 64)
    candidate_entries = (candidate,)
    current_digest = hashlib.sha256(_canonical_manifest_bytes(_manifest_body(candidate_entries))).hexdigest()
    current = MultiSourceManifest(candidate_entries, current_digest)
    calls = []
    class Engine:
        def build_generation_spec(self, _space):
            calls.append("spec")
            return SimpleNamespace(generation_id="g", space_id="s")
        def index_source(self, *_args):
            calls.append("index")
    monkeypatch.setattr("persistent_local_index.indexer.remove_source_location", lambda *_args: calls.append("remove"))
    with pytest.raises(ValueError, match="CORPUS_SEPARATION_"):
        lifecycle.reconcile_multi_source_index(
            previous, current, index_root=tmp_path / "index", engine=Engine(), semantic_space=object(),
            image_embedder=lambda _paths: None, authorize_source=lambda _entry: True,
            synthetic_attestations=(attestation,), synthetic_authorizations=(authorization,),
        )
    assert calls == []
    assert not (tmp_path / "index").exists()


def test_opt_in_reconciliation_rechecks_batch_after_generation_spec_before_removal(tmp_path, monkeypatch):
    from vip_fvs import multi_source_lifecycle as lifecycle
    from vip_fvs.corpus_admission import CorpusAdmissionError
    from vip_fvs.source_adapter import (
        MultiSourceManifest, _canonical_manifest_bytes, _manifest_body,
    )

    unit_path = str(Path(__file__).resolve().parents[1] / "unit")
    inserted = unit_path not in sys.path
    if inserted:
        sys.path.insert(0, unit_path)
    try:
        p2_fixture = importlib.import_module("test_corpus_admission")
        original = b"bound reconciliation source"
        source_digest = hashlib.sha256(original).hexdigest()
        attestation, authorization = p2_fixture._valid_synthetic_attestation(source_sha256=source_digest)
    finally:
        if inserted:
            sys.path.remove(unit_path)

    source = tmp_path / "candidate.bin"
    source.write_bytes(original)
    candidate = SourceManifestEntry(
        revision_id="candidate-c", content_id="content-c", source_path=source,
        source_sha256=source_digest, selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="discovery-policy-fixture", custody_state="PRESERVED",
    )
    removed_entry = SourceManifestEntry(
        revision_id="previous", content_id="previous-content", source_path=tmp_path / "removed.bin",
        source_sha256="a" * 64, selected_stream_index=0, selection_source="generated-fixture",
        inventory_digest="1" * 64, policy_decision_ref="fixture-policy", custody_state="PRESERVED",
    )
    previous_entries = (removed_entry,)
    current_entries = (candidate,)
    previous_digest = hashlib.sha256(_canonical_manifest_bytes(_manifest_body(previous_entries))).hexdigest()
    current_digest = hashlib.sha256(_canonical_manifest_bytes(_manifest_body(current_entries))).hexdigest()
    previous = MultiSourceManifest(previous_entries, previous_digest)
    current = MultiSourceManifest(current_entries, current_digest)
    calls = []

    class MutatingEngine:
        def build_generation_spec(self, _space):
            calls.append("spec")
            if calls.count("spec") == 1:
                source.write_bytes(b"changed during generation setup")
            return SimpleNamespace(generation_id="g", space_id="s")

        def index_source(self, *_args):
            calls.append("index")
            raise AssertionError("changed batch must not reach index")

    monkeypatch.setattr("persistent_local_index.indexer.remove_source_location",
                        lambda *_args: calls.append("remove"))
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        lifecycle.reconcile_multi_source_index(
            previous, current, index_root=tmp_path / "index", engine=MutatingEngine(),
            semantic_space=object(), image_embedder=lambda _paths: None,
            authorize_source=lambda _entry: True,
            synthetic_attestations=(attestation,), synthetic_authorizations=(authorization,),
        )

    assert calls == ["spec"]
    assert not (tmp_path / "index").exists()
