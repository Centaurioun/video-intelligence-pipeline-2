"""TDD Task 1: deterministic semantic-space identity and fail-closed compatibility."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from persistent_local_index.model_space import (
    GenerationSpec,
    SemanticSpace,
    assert_same_space,
    build_generation_spec,
    digest_file,
    digest_processor_assets,
    load_manifest,
    semantic_space_id,
    validate_manifest_compatibility,
    write_manifest,
)


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


def test_space_id_is_deterministic_and_field_sensitive():
    a = _space()
    assert semantic_space_id(a) == semantic_space_id(a)
    assert semantic_space_id(a) != semantic_space_id(replace(a, processor_digest="changed"))


def test_space_id_matches_pinned_canonical_serialization_digest():
    # Independent reference calculation: SHA-256 of sorted-key, compact,
    # UTF-8 JSON for the fixture fields. Keep this digest fixed so a coordinated
    # implementation/fixture change cannot silently redefine identity.
    assert semantic_space_id(_space()) == (
        "f4564a3d4bb124d2eb9b0d2ce9394edba174eda4d44ef422daf60aad3ce5b100"
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("model_identity", "other/model"),
        ("frozen_revision", "deadbeef"),
        ("weights_sha256", "0" * 64),
        ("processor_digest", "other"),
        ("image_preprocessing_digest", "other"),
        ("text_preprocessing_contract", "padding=none"),
        ("embedding_dim", 512),
        ("dtype", "float16"),
        ("normalization", "none"),
    ],
)
def test_space_id_changes_for_every_identity_field(field, value):
    a = _space()
    assert semantic_space_id(a) != semantic_space_id(replace(a, **{field: value}))


def test_space_mismatch_fails_closed_and_names_field():
    expected = _space()
    live = replace(expected, text_preprocessing_contract="padding=none")
    with pytest.raises(ValueError, match="text_preprocessing_contract"):
        assert_same_space(expected, live)


def test_assert_same_space_accepts_identical():
    a = _space()
    assert assert_same_space(a, a) is None


# --- generation spec -------------------------------------------------------


def test_build_generation_spec_pins_v1_values():
    spec = build_generation_spec(_space())
    assert isinstance(spec, GenerationSpec)
    assert spec.schema_version == 1
    assert spec.sampling_policy_id == "coarse-pts-4.5s"
    assert spec.sampling_policy_version == 1
    assert spec.sampling_interval_seconds == 4.5
    assert spec.selected_stream_policy == "first-video-stream"
    assert spec.space_id == semantic_space_id(_space())


def test_generation_id_is_deterministic_and_not_wall_clock():
    spec_a = build_generation_spec(_space())
    spec_b = build_generation_spec(_space())
    assert spec_a.generation_id == spec_b.generation_id
    assert len(spec_a.generation_id) == 64


def test_generation_id_matches_pinned_canonical_policy_digest():
    # Reference payload includes the pinned semantic-space digest plus the v1
    # schema and sampling policy fields serialized as sorted-key compact JSON.
    assert build_generation_spec(_space()).generation_id == (
        "a9af2908a00381b0b96c426ff310541f8f3d1ccec076cf37b2f7d934eddbb995"
    )


def test_generation_id_changes_with_sampling_policy_and_space():
    base = build_generation_spec(_space())
    other_interval = build_generation_spec(_space(), sampling_interval_seconds=9.0)
    other_space = build_generation_spec(replace(_space(), embedding_dim=512))
    assert base.generation_id != other_interval.generation_id
    assert base.generation_id != other_space.generation_id


# --- processor asset digest ------------------------------------------------


def _write_assets(root: Path, missing: str | None = None) -> None:
    names = (
        "config.json",
        "preprocessor_config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "spiece.model",
    )
    for name in names:
        if name == missing:
            continue
        (root / name).write_bytes(f"content-of-{name}".encode())


def test_digest_processor_assets_is_order_and_name_bound(tmp_path):
    _write_assets(tmp_path)
    first = digest_processor_assets(tmp_path)
    assert first == digest_processor_assets(tmp_path)
    # renaming a file changes the digest because names are hashed too
    (tmp_path / "spiece.model").rename(tmp_path / "spiece2.model")
    (tmp_path / "spiece2.model").rename(tmp_path / "renamed.model")
    (tmp_path / "renamed.model").rename(tmp_path / "spiece.model")
    assert digest_processor_assets(tmp_path) == first
    (tmp_path / "config.json").write_bytes(b"different")
    assert digest_processor_assets(tmp_path) != first


def test_digest_processor_assets_fails_closed_on_missing(tmp_path):
    _write_assets(tmp_path, missing="tokenizer.json")
    with pytest.raises(ValueError, match="PROCESSOR_ASSET_MISSING:tokenizer.json"):
        digest_processor_assets(tmp_path)


def test_digest_file_matches_hashlib(tmp_path):
    import hashlib

    p = tmp_path / "blob.bin"
    p.write_bytes(b"hello world")
    assert digest_file(p) == hashlib.sha256(b"hello world").hexdigest()


# --- manifest round trip ---------------------------------------------------


def test_manifest_round_trip_preserves_all_fields(tmp_path):
    spec = build_generation_spec(_space())
    path = tmp_path / "manifest.json"
    write_manifest(path, spec, committed_rows=7)
    manifest = load_manifest(path)
    assert manifest["generation_id"] == spec.generation_id
    assert manifest["space_id"] == spec.space_id
    assert manifest["schema_version"] == 1
    assert manifest["sampling_policy_id"] == "coarse-pts-4.5s"
    assert manifest["sampling_policy_version"] == 1
    assert manifest["sampling_interval_seconds"] == 4.5
    assert manifest["selected_stream_policy"] == "first-video-stream"
    assert manifest["committed_rows"] == 7
    assert manifest["space"]["embedding_dim"] == 768
    assert manifest["space"]["dtype"] == "float32"
    assert manifest["space"]["normalization"] == "l2"
    assert manifest["space"]["text_preprocessing_contract"] == "padding=max_length"
    assert "created_at" in manifest
    validate_manifest_compatibility(manifest, spec)


def test_manifest_write_is_atomic_and_valid_json(tmp_path):
    spec = build_generation_spec(_space())
    path = tmp_path / "manifest.json"
    write_manifest(path, spec, committed_rows=0)
    json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "field,value",
    [
        ("space_id", "0" * 64),
        ("schema_version", 99),
        ("generation_id", "0" * 64),
        ("sampling_policy_id", "other"),
        ("sampling_policy_version", 2),
        ("sampling_interval_seconds", 9.0),
        ("selected_stream_policy", "other"),
    ],
)
def test_manifest_mismatch_names_field(tmp_path, field, value):
    spec = build_generation_spec(_space())
    manifest = write_and_load(tmp_path, spec)
    manifest[field] = value
    with pytest.raises(ValueError, match=field):
        validate_manifest_compatibility(manifest, spec)


@pytest.mark.parametrize(
    "field,value",
    [
        ("model_identity", "other"),
        ("frozen_revision", "0" * 40),
        ("weights_sha256", "0" * 64),
        ("processor_digest", "other"),
        ("image_preprocessing_digest", "other"),
        ("text_preprocessing_contract", "padding=none"),
        ("embedding_dim", 512),
        ("dtype", "float16"),
        ("normalization", "none"),
    ],
)
def test_manifest_space_mismatch_names_field(tmp_path, field, value):
    spec = build_generation_spec(_space())
    manifest = write_and_load(tmp_path, spec)
    manifest["space"][field] = value
    with pytest.raises(ValueError, match=field):
        validate_manifest_compatibility(manifest, spec)


def test_manifest_missing_required_key_fails_closed(tmp_path):
    spec = build_generation_spec(_space())
    manifest = write_and_load(tmp_path, spec)
    del manifest["space_id"]
    with pytest.raises(ValueError, match="space_id"):
        validate_manifest_compatibility(manifest, spec)


def test_load_manifest_missing_file_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="MANIFEST"):
        load_manifest(tmp_path / "nope.json")


def test_load_manifest_corrupt_json_fails_closed(tmp_path):
    p = tmp_path / "manifest.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="MANIFEST"):
        load_manifest(p)


def write_and_load(tmp_path: Path, spec: GenerationSpec) -> dict:
    path = tmp_path / "manifest.json"
    write_manifest(path, spec, committed_rows=0)
    return load_manifest(path)
