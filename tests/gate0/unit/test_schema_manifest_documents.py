"""Closed multi-record document contract tests for the two Gate-0 file manifests.

``source_manifest.json`` and ``split_manifest.json`` are *file documents*, not
JSONL record streams: the producer writes ``{"records": [...]}`` (plus
``revision_ids`` for the source manifest).  The checked-in schemas used to
describe a *bare* record envelope, so the real emitted documents were refused
with ``Additional properties are not allowed ('records', 'revision_ids' were
unexpected)``.

These tests pin the intended contract (contract-owner proposal D6 / Task 2):

* the top-level document is a closed wrapper requiring a non-empty ``records``
  array whose items are the unchanged record envelope schema in
  ``$defs/record``;
* ``source_manifest.json`` keeps its authorized ``revision_ids`` inventory
  (unique ids); ``split_manifest.json`` is closed and has no ``revision_ids``;
* every existing per-record envelope semantic is preserved inside ``records``
  (no bare payloads, closed records/payloads, pinned record types, enums).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = ROOT / "schemas" / "gate0"


def _validator(name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _source_record() -> dict:
    return {
        "record_id": "occurrence_rev_a",
        "record_type": "occurrence_revision",
        "record_schema_version": "gate0.v1",
        "record_digest": "0" * 64,
        "payload": {
            "occurrence_id": "occ_a",
            "revision_id": "rev_a",
            "content_id": "content_a",
            "locator": "media/a.mp4",
            "byte_count": 10,
            "digest_algorithm": "sha256",
            "content_digest": "1" * 64,
            "stream_refs": [{"stream_index": 0, "stream_type": "video"}],
            "probe_ref": "probe_a",
            "discovery_authorization_id": "auth_a",
            "source_status": "INCLUDED",
            "relation_ids": [],
        },
    }


def _split_record() -> dict:
    return {
        "record_id": "split_a",
        "record_type": "split_allocation",
        "record_schema_version": "gate0.v1",
        "record_digest": "2" * 64,
        "payload": {
            "split_version": "split-v1",
            "relation_component_id": "component_a",
            "allocation": "EVALUATION",
            "frozen_at": "1970-01-01T00:00:00Z",
            "relation_inventory_digest": "3" * 64,
            "leakage_status": "VALID",
        },
    }


def _source_document() -> dict:
    return {"records": [_source_record()], "revision_ids": ["rev_a"]}


def _split_document() -> dict:
    return {"records": [_split_record()]}


def _errors(validator: Draft202012Validator, document: object) -> list[str]:
    return [error.message for error in validator.iter_errors(document)]


# ---------------------------------------------------------------------------
# positive contract: the real emitted document shape must be admissible
# ---------------------------------------------------------------------------

def test_source_manifest_multi_record_document_is_admissible() -> None:
    """RED before D6: the emitted provider document was refused at the root."""
    errors = _errors(_validator("source_manifest.json"), _source_document())
    assert errors == [], errors


def test_split_manifest_multi_record_document_is_admissible() -> None:
    errors = _errors(_validator("split_manifest.json"), _split_document())
    assert errors == [], errors


def test_source_manifest_admits_its_authorized_revision_inventory() -> None:
    document = _source_document()
    document["revision_ids"] = ["rev_a", "rev_b"]
    assert _errors(_validator("source_manifest.json"), document) == []


def test_source_manifest_revision_ids_must_be_unique_ids() -> None:
    validator = _validator("source_manifest.json")
    duplicate = _source_document()
    duplicate["revision_ids"] = ["rev_a", "rev_a"]
    assert _errors(validator, duplicate)
    bad_id = _source_document()
    bad_id["revision_ids"] = ["Rev.A"]
    assert _errors(validator, bad_id)


# ---------------------------------------------------------------------------
# negative contract: closed document wrapper
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "name, factory",
    [("source_manifest.json", _source_document), ("split_manifest.json", _split_document)],
)
def test_document_without_records_is_refused(name: str, factory) -> None:
    validator = _validator(name)
    assert _errors(validator, {})
    # A bare record envelope is a JSONL row, not a file document.
    record = factory()["records"][0]
    assert _errors(validator, record)


@pytest.mark.parametrize(
    "name, factory",
    [("source_manifest.json", _source_document), ("split_manifest.json", _split_document)],
)
def test_empty_records_array_is_refused(name: str, factory) -> None:
    document = factory()
    document["records"] = []
    assert _errors(_validator(name), document)


@pytest.mark.parametrize(
    "name, factory",
    [("source_manifest.json", _source_document), ("split_manifest.json", _split_document)],
)
def test_unknown_top_level_property_is_refused(name: str, factory) -> None:
    document = factory()
    document["unexpected_field"] = "value"
    assert _errors(_validator(name), document)


def test_split_manifest_has_no_revision_ids_inventory() -> None:
    document = _split_document()
    document["revision_ids"] = ["rev_a"]
    assert _errors(_validator("split_manifest.json"), document)


# ---------------------------------------------------------------------------
# negative contract: nested record envelopes are unchanged / still strict
# ---------------------------------------------------------------------------

def test_source_record_missing_required_envelope_field_is_refused() -> None:
    document = _source_document()
    del document["records"][0]["record_digest"]
    assert _errors(_validator("source_manifest.json"), document)


def test_source_record_extra_field_is_refused() -> None:
    document = _source_document()
    document["records"][0]["unexpected_field"] = "value"
    assert _errors(_validator("source_manifest.json"), document)


def test_source_record_wrong_record_type_is_refused() -> None:
    document = _source_document()
    document["records"][0]["record_type"] = "split_allocation"
    assert _errors(_validator("source_manifest.json"), document)


def test_split_record_wrong_record_type_is_refused() -> None:
    document = _split_document()
    document["records"][0]["record_type"] = "occurrence_revision"
    assert _errors(_validator("split_manifest.json"), document)


def test_source_record_bad_payload_type_is_refused() -> None:
    document = _source_document()
    document["records"][0]["payload"]["byte_count"] = "ten"
    assert _errors(_validator("source_manifest.json"), document)


def test_split_record_bad_payload_enum_is_refused() -> None:
    document = _split_document()
    document["records"][0]["payload"]["allocation"] = "TEST"
    assert _errors(_validator("split_manifest.json"), document)


def test_records_must_be_record_envelopes_not_bare_payloads() -> None:
    document = _source_document()
    document["records"] = [document["records"][0]["payload"]]
    assert _errors(_validator("source_manifest.json"), document)


def test_duplicate_record_entries_are_refused() -> None:
    """Identical duplicate records are rejected by ``uniqueItems``.

    JSON Schema (Draft 2020-12) cannot express uniqueness of a nested
    ``record_id`` value, so duplicate *ids* with differing digests are beyond
    schema expressiveness; the record-level structural duplication is refused
    here and identity uniqueness remains a cross-artifact validator concern.
    """
    document = _split_document()
    document["records"] = [document["records"][0], document["records"][0]]
    assert _errors(_validator("split_manifest.json"), document)


# ---------------------------------------------------------------------------
# structural assertions: the record schema was moved, not weakened
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["source_manifest.json", "split_manifest.json"])
def test_record_schema_lives_in_defs_and_is_closed(name: str) -> None:
    schema = json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["records"]
    assert schema["properties"]["records"]["type"] == "array"
    assert schema["properties"]["records"]["items"] == {"$ref": "#/$defs/record"}
    record = schema["$defs"]["record"]
    assert record["additionalProperties"] is False
    assert record["required"] == [
        "record_id", "record_type", "record_schema_version", "record_digest", "payload"
    ]
    assert record["properties"]["payload"]["additionalProperties"] is False


def test_source_manifest_preserves_record_semantics_byte_for_byte() -> None:
    schema = json.loads((SCHEMA_ROOT / "source_manifest.json").read_text(encoding="utf-8"))
    record = schema["$defs"]["record"]
    assert record["properties"]["record_type"] == {"const": "occurrence_revision"}
    assert record["properties"]["record_schema_version"] == {"const": "gate0.v1"}
    payload = record["properties"]["payload"]
    assert payload["required"] == [
        "occurrence_id", "revision_id", "content_id", "locator", "byte_count",
        "digest_algorithm", "content_digest", "stream_refs", "probe_ref",
        "discovery_authorization_id", "source_status", "relation_ids",
    ]
    assert payload["properties"]["source_status"]["enum"] == [
        "INCLUDED", "EXCLUDED_AFTER_PROBE", "NOT_OBSERVED"
    ]
    assert schema["properties"]["revision_ids"]["uniqueItems"] is True


def test_split_manifest_preserves_record_semantics_byte_for_byte() -> None:
    schema = json.loads((SCHEMA_ROOT / "split_manifest.json").read_text(encoding="utf-8"))
    record = schema["$defs"]["record"]
    assert record["properties"]["record_type"] == {"const": "split_allocation"}
    assert record["properties"]["record_schema_version"] == {"const": "gate0.v1"}
    payload = record["properties"]["payload"]
    assert payload["required"] == [
        "split_version", "relation_component_id", "allocation", "frozen_at",
        "relation_inventory_digest", "leakage_status",
    ]
    assert payload["properties"]["allocation"]["enum"] == ["DEVELOPMENT", "EVALUATION"]
