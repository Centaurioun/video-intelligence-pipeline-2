from __future__ import annotations

import hashlib
import json
import os
from dataclasses import FrozenInstanceError, replace

import pytest

from gate0.policy import PolicyDecision
from vip_fvs import source_adapter

SourceBinding = source_adapter.SourceBinding
inventory_source = source_adapter.inventory_source


def _manifest_api(name):
    value = getattr(source_adapter, name, None)
    assert value is not None, f"source_adapter must provide {name}"
    return value


def _policy(revision: str = "rev_synthetic") -> PolicyDecision:
    return PolicyDecision(
        policy_decision_id="policy_fvs_source",
        revision_scope=(revision,),
        purpose="DISCOVER",
        sensitivity_consent="SYNTHETIC",
        allowed_artifact_types=("source_manifest", "discovery_authorization"),
        provider_model_boundary="local_only",
        retention_class="SOURCE_REFERENCE",
        expires_at="2099-01-01T00:00:00Z",
        revocation_ref=None,
        egress_manifest_digest="a" * 64,
        decision="ALLOW",
        effective_at_use=True,
    )


def test_inventory_source_records_digest_and_preserves_bytes(tmp_path):
    source = tmp_path / "synthetic.mp4"
    source.write_bytes(b"synthetic source bytes")
    before = source.read_bytes()

    binding = inventory_source(source, tmp_path / "run", _policy())

    assert isinstance(binding, SourceBinding)
    assert binding.source_path == source
    assert binding.source_sha256 == hashlib.sha256(before).hexdigest()
    assert binding.revision_ref.revision_id
    assert binding.revision_ref.content_id
    assert binding.revision_ref.revision_id != binding.source_sha256
    assert binding.policy_decision_ref == "policy_fvs_source"
    assert binding.custody_state == "PRESERVED"
    assert binding.inventory.revision_refs[0] == binding.revision_ref
    assert binding.inventory.source_records[0]["payload"]["custody"]["state"] == "PRESERVED"
    assert source.read_bytes() == before
    assert (tmp_path / "run" / "source_manifest.json").exists()


def test_digest_is_separate_from_logical_revision(tmp_path):
    source = tmp_path / "clip.bin"
    source.write_bytes(b"same bytes")
    binding = inventory_source(source, tmp_path / "run", _policy())

    record = binding.inventory.source_records[0]["payload"]
    assert record["revision_id"] == binding.revision_ref.revision_id
    assert record["content_digest"] == binding.source_sha256
    assert "source_sha256" not in binding.revision_ref.__dict__


def _binding(tmp_path, name: str, revision: str, content: bytes) -> SourceBinding:
    source = tmp_path / name
    source.write_bytes(content)
    return inventory_source(source, tmp_path / f"run-{revision}", _policy(revision))


def test_multi_source_manifest_is_canonically_ordered_and_digest_stable(tmp_path):
    MultiSourceManifest = _manifest_api("MultiSourceManifest")
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    zulu = _binding(tmp_path, "zulu.mp4", "rev_z", b"z bytes")
    alpha = _binding(tmp_path, "alpha.mp4", "rev_a", b"a bytes")

    forward = build_multi_source_manifest((zulu, alpha))
    reverse = build_multi_source_manifest((alpha, zulu))

    assert isinstance(forward, MultiSourceManifest)
    assert tuple(entry.revision_id for entry in forward.entries) == ("rev_a", "rev_z")
    assert forward.entries == reverse.entries
    assert forward.manifest_digest == reverse.manifest_digest
    with pytest.raises(FrozenInstanceError):
        forward.manifest_digest = "0" * 64


def test_multi_source_manifest_allows_same_digest_at_distinct_locators_without_collapsing_revision_identity(tmp_path):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    first = _binding(tmp_path, "copy-1.mp4", "rev_one", b"identical bytes")
    second = _binding(tmp_path, "copy-2.mp4", "rev_two", b"identical bytes")

    manifest = build_multi_source_manifest((first, second))

    assert len(manifest.entries) == 2
    assert {entry.source_sha256 for entry in manifest.entries} == {first.source_sha256}
    assert {entry.revision_id for entry in manifest.entries} == {"rev_one", "rev_two"}
    assert {entry.source_path for entry in manifest.entries} == {first.source_path, second.source_path}


@pytest.mark.parametrize("duplicate", ["revision", "locator"])
def test_multi_source_manifest_rejects_duplicate_revision_and_duplicate_current_locator(tmp_path, duplicate):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    first = _binding(tmp_path, "same.mp4", "rev_one", b"same bytes")
    if duplicate == "revision":
        second = _binding(tmp_path, "other.mp4", "rev_one", b"other bytes")
    else:
        second = _binding(tmp_path, "same.mp4", "rev_two", b"same bytes")

    with pytest.raises(ValueError):
        build_multi_source_manifest((first, second))


def test_multi_source_manifest_rejects_empty_snapshot():
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    with pytest.raises(ValueError):
        build_multi_source_manifest(())


def test_manifest_round_trip_preserves_closed_fields_and_rejects_tampered_digest_or_extra_fields(tmp_path):
    SourceManifestEntry = _manifest_api("SourceManifestEntry")
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    load_multi_source_manifest = _manifest_api("load_multi_source_manifest")
    save_multi_source_manifest = _manifest_api("save_multi_source_manifest")
    binding = _binding(tmp_path, "one.mp4", "rev_one", b"source")
    manifest = build_multi_source_manifest((binding,))
    destination = tmp_path / "manifest.json"

    save_multi_source_manifest(manifest, destination)
    raw = destination.read_bytes()
    loaded = load_multi_source_manifest(destination)

    assert raw.decode("utf-8") == json.dumps(
        json.loads(raw.decode("utf-8")), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    assert loaded == manifest
    assert loaded.entries[0] == SourceManifestEntry(
        revision_id=binding.revision_ref.revision_id,
        content_id=binding.revision_ref.content_id,
        source_path=binding.source_path,
        source_sha256=binding.source_sha256,
        selected_stream_index=binding.revision_ref.selected_stream_index,
        selection_source=binding.revision_ref.selection_source,
        inventory_digest=binding.inventory.inventory_digest,
        policy_decision_ref=binding.policy_decision_ref,
        custody_state=binding.custody_state,
        inventory_artifact_id=binding.inventory_envelope.artifact_id,
        inventory_payload_digest=binding.inventory_envelope.payload_digest,
    )

    document = json.loads(raw.decode("utf-8"))
    tampered = dict(document, manifest_digest="0" * 64)
    destination.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError):
        load_multi_source_manifest(destination)

    extra_field = dict(document, unexpected="closed schema")
    destination.write_text(json.dumps(extra_field), encoding="utf-8")
    with pytest.raises(ValueError):
        load_multi_source_manifest(destination)


def test_manifest_load_does_not_open_or_probe_source_paths(tmp_path, monkeypatch):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    load_multi_source_manifest = _manifest_api("load_multi_source_manifest")
    save_multi_source_manifest = _manifest_api("save_multi_source_manifest")
    binding = _binding(tmp_path, "source.mp4", "rev_one", b"source bytes")
    manifest_path = tmp_path / "manifest.json"
    source_path = binding.source_path

    original_read_bytes = type(source_path).read_bytes
    original_open = type(source_path).open

    def fail_on_source(self):
        if self == source_path:
            raise AssertionError("manifest operation reopened a source path")
        return original_read_bytes(self)

    def fail_open_on_source(self, *args, **kwargs):
        if self == source_path:
            raise AssertionError("manifest operation opened a source path")
        return original_open(self, *args, **kwargs)

    def fail_probe(*args, **kwargs):
        raise AssertionError("manifest operation probed a source")

    monkeypatch.setattr(type(source_path), "read_bytes", fail_on_source)
    monkeypatch.setattr(type(source_path), "open", fail_open_on_source)
    monkeypatch.setattr(source_adapter, "_synthetic_probe", fail_probe)
    monkeypatch.setattr(source_adapter, "probe_real_source", fail_probe)
    manifest = build_multi_source_manifest((binding,))
    save_multi_source_manifest(manifest, manifest_path)
    loaded = load_multi_source_manifest(manifest_path)

    assert loaded.entries[0].source_path == source_path
    assert loaded.entries[0].source_sha256 == binding.source_sha256


def test_manifest_entry_keeps_locator_revision_content_and_digest_semantics_separate(tmp_path):
    SourceManifestEntry = _manifest_api("SourceManifestEntry")
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    first = _binding(tmp_path, "first.mp4", "rev_first", b"shared bytes")
    second = _binding(tmp_path, "second.mp4", "rev_second", b"shared bytes")
    manifest = build_multi_source_manifest((first, second))

    assert all(isinstance(entry, SourceManifestEntry) for entry in manifest.entries)
    assert first.source_sha256 == second.source_sha256
    assert first.revision_ref.content_id != second.revision_ref.content_id
    assert first.revision_ref.revision_id != second.revision_ref.revision_id
    assert first.source_path != second.source_path
    assert manifest.find_entry(first.source_path, first.source_sha256) == manifest.entries[0]
    assert manifest.find_entry(first.source_path, "f" * 64) is None
    assert manifest.find_entry(second.source_path, "f" * 64) is None
    assert manifest.find_entry(tmp_path / "missing.mp4", first.source_sha256) is None


def test_manifest_rejects_binding_whose_byte_digest_disagrees_with_inventory(tmp_path):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    binding = _binding(tmp_path, "source.mp4", "rev_one", b"source bytes")
    inconsistent = replace(binding, source_sha256="f" * 64)

    with pytest.raises(ValueError):
        build_multi_source_manifest((inconsistent,))


def test_manifest_load_rejects_non_digest_source_sha256_even_with_recomputed_manifest_digest(tmp_path):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    load_multi_source_manifest = _manifest_api("load_multi_source_manifest")
    save_multi_source_manifest = _manifest_api("save_multi_source_manifest")
    binding = _binding(tmp_path, "source.mp4", "rev_one", b"source bytes")
    manifest_path = tmp_path / "manifest.json"
    save_multi_source_manifest(build_multi_source_manifest((binding,)), manifest_path)
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document["entries"][0]["source_sha256"] = "not-a-sha256"
    body = {key: value for key, value in document.items() if key != "manifest_digest"}
    document["manifest_digest"] = hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_multi_source_manifest(manifest_path)


def test_manifest_save_refuses_a_source_locator_as_its_destination(tmp_path):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    save_multi_source_manifest = _manifest_api("save_multi_source_manifest")
    binding = _binding(tmp_path, "source.mp4", "rev_one", b"immutable source bytes")
    manifest = build_multi_source_manifest((binding,))
    before = binding.source_path.read_bytes()

    with pytest.raises(ValueError):
        save_multi_source_manifest(manifest, binding.source_path)

    assert binding.source_path.read_bytes() == before


def test_manifest_save_refuses_a_hardlink_to_a_source_as_its_destination(tmp_path):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    save_multi_source_manifest = _manifest_api("save_multi_source_manifest")
    binding = _binding(tmp_path, "source.mp4", "rev_one", b"immutable source bytes")
    manifest = build_multi_source_manifest((binding,))
    alias = tmp_path / "source-alias.mp4"
    os.link(binding.source_path, alias)
    before = binding.source_path.read_bytes()

    with pytest.raises(ValueError):
        save_multi_source_manifest(manifest, alias)

    assert binding.source_path.read_bytes() == before


def test_manifest_rejects_inventory_payload_with_stale_inventory_digest(tmp_path):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    binding = _binding(tmp_path, "source.mp4", "rev_one", b"source bytes")
    inconsistent_inventory = replace(binding.inventory, inventory_digest="f" * 64)
    inconsistent_binding = replace(binding, inventory=inconsistent_inventory)

    with pytest.raises(ValueError):
        build_multi_source_manifest((inconsistent_binding,))


def test_manifest_rejects_mutated_inventory_record_digest(tmp_path):
    build_multi_source_manifest = _manifest_api("build_multi_source_manifest")
    binding = _binding(tmp_path, "source.mp4", "rev_one", b"source bytes")
    binding.inventory.source_records[0]["payload"]["custody"]["authority"] = "changed"

    with pytest.raises(ValueError):
        build_multi_source_manifest((binding,))
