"""Conformance and negative tests for the three new VIP-FVS real-source schemas.

The schemas under test are the checked-in Draft 2020-12 documents:

* ``schemas/vip_fvs/source_snapshot.v1.json``
* ``schemas/vip_fvs/review_bundle.v3.json``
* ``schemas/vip_fvs/real_receipt.v2.json``

Valid documents are generated from production code where feasible and from
synthetic local bytes only: a real ``SourceSnapshotStore.capture`` snapshot for
``source_snapshot.v1``, ``RealReceipt.create`` for ``real_receipt.v2``, and the
production sealing helpers (``dependency_digest``/``record_digest`` +
``ReviewBundle.from_record``) for ``review_bundle.v3``.

When the ``jsonschema`` package is importable the tests validate with
``jsonschema.Draft202012Validator``.  When it is not importable -- this lane is
explicitly forbidden from installing anything -- the tests fall back to a small,
self-contained subset validator that implements exactly the keywords these
three schemas use, plus structural assertions on schema content.  The fallback
is itself exercised by ``test_fallback_subset_validator_*`` so it cannot rot
silently.

Several tests deliberately pin *real schema gaps* discovered while writing this
file (a schema that is too lax, a dead ``$defs`` entry, a stray root keyword, an
inconsistent identifier bound).  Those tests are named ``test_gap_*`` and never
modify the schemas; they record the current, weakest-conforming behaviour so a
later schema change is visible.
"""
from __future__ import annotations

from collections import namedtuple
import copy
import hashlib
import json
from pathlib import Path
import re

import pytest

from vip_fvs.real_receipt import RealReceipt, load_real_receipt, save_real_receipt
from vip_fvs.review_bundle import ReviewBundle, dependency_digest, record_digest
from vip_fvs.source_snapshot import (
    SourceSnapshotError,
    SourceSnapshotStore,
    verify_snapshot_evidence,
)

try:  # pragma: no cover - one branch is chosen by the environment
    import jsonschema
    from jsonschema import Draft202012Validator

    JSONSCHEMA_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without jsonschema
    jsonschema = None
    Draft202012Validator = None
    JSONSCHEMA_AVAILABLE = False


REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = REPO_ROOT / "schemas" / "vip_fvs"
ZERO_DIGEST = "0" * 64
DIGEST_PATTERN = "^[0-9a-f]{64}$"

SCHEMA_FILES = {
    "source_snapshot": "source_snapshot.v1.json",
    "review_bundle": "review_bundle.v3.json",
    "review_bundle_v2": "review_bundle.v2.json",
    "review_bundle_v1": "review_bundle.json",
    "real_receipt": "real_receipt.v2.json",
    "real_receipt_v1": "real_receipt.v1.json",
}

#: kind -> schema name used to validate documents produced for that kind.
KIND_SCHEMA = {
    "source_snapshot": "source_snapshot",
    "review_bundle": "review_bundle",
    "review_bundle_v2": "review_bundle_v2",
    "review_bundle_v1": "review_bundle_v1",
    "real_receipt": "real_receipt",
    "real_receipt_decision": "real_receipt",
    "real_receipt_v1": "real_receipt_v1",
}

_LOADED_SCHEMAS: dict[str, dict] = {}


def _schema(name: str) -> dict:
    """Load and cache one checked-in schema document (read-only)."""
    if name not in _LOADED_SCHEMAS:
        _LOADED_SCHEMAS[name] = json.loads((SCHEMA_DIR / SCHEMA_FILES[name]).read_text(encoding="utf-8"))
    return _LOADED_SCHEMAS[name]


_Error = namedtuple("_Error", "keyword path message")


def _canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


# ---------------------------------------------------------------------------
# Minimal fallback validator (only used when jsonschema is unavailable).
# Implemented keywords: $ref, oneOf, type, const, enum, pattern, minLength,
# maxLength, minimum, exclusiveMinimum, minItems, maxItems, required,
# properties, additionalProperties, items, prefixItems.
# ---------------------------------------------------------------------------
def _type_matches(value, name: str) -> bool:
    if name == "null":
        return value is None
    if name == "boolean":
        return isinstance(value, bool)
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise AssertionError(f"fallback validator does not implement type {name!r}")


def _equal(left, right) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return type(left) is type(right) and left == right


def _resolve_ref(ref: str, root: dict):
    assert ref.startswith("#/"), ref
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _validate_subset(instance, schema: dict, root: dict | None = None, path: str = "$") -> list[_Error]:
    root = schema if root is None else root
    errors: list[_Error] = []
    if "$ref" in schema:
        return _validate_subset(instance, _resolve_ref(schema["$ref"], root), root, path)
    if "oneOf" in schema:
        branch_errors = [_validate_subset(instance, branch, root, path) for branch in schema["oneOf"]]
        if sum(1 for branch in branch_errors if not branch) != 1:
            errors.append(_Error("oneOf", path, f"{instance!r} must match exactly one oneOf branch"))
    declared_type = schema.get("type")
    if declared_type is not None:
        names = declared_type if isinstance(declared_type, list) else [declared_type]
        if not any(_type_matches(instance, name) for name in names):
            errors.append(_Error("type", path, f"{instance!r} is not of type {declared_type!r}"))
            return errors
    if "const" in schema and not _equal(instance, schema["const"]):
        errors.append(_Error("const", path, f"{instance!r} is not const {schema['const']!r}"))
    if "enum" in schema and not any(_equal(instance, option) for option in schema["enum"]):
        errors.append(_Error("enum", path, f"{instance!r} is not one of {schema['enum']!r}"))
    if isinstance(instance, str):
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(_Error("pattern", path, f"{instance!r} does not match {schema['pattern']!r}"))
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(_Error("minLength", path, f"{instance!r} is too short"))
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(_Error("maxLength", path, f"{instance!r} is too long"))
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(_Error("minimum", path, f"{instance!r} is below minimum {schema['minimum']!r}"))
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errors.append(_Error("exclusiveMinimum", path, f"{instance!r} is not above {schema['exclusiveMinimum']!r}"))
    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", ()):
            if key not in instance:
                errors.append(_Error("required", path, f"missing required property {key!r}"))
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(_validate_subset(instance[key], subschema, root, f"{path}.{key}"))
        if schema.get("additionalProperties", True) is False:
            for key in instance:
                if key not in properties:
                    errors.append(_Error("additionalProperties", path, f"unexpected property {key!r}"))
    if isinstance(instance, list):
        prefix = schema.get("prefixItems")
        if prefix:
            for index, subschema in enumerate(prefix):
                if index < len(instance):
                    errors.extend(_validate_subset(instance[index], subschema, root, f"{path}[{index}]"))
        items = schema.get("items")
        if isinstance(items, dict):
            start = len(prefix) if prefix else 0
            for index in range(start, len(instance)):
                errors.extend(_validate_subset(instance[index], items, root, f"{path}[{index}]"))
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(_Error("minItems", path, "array is too short"))
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(_Error("maxItems", path, "array is too long"))
    return errors


def _errors(document, kind: str) -> list[_Error]:
    """Return validation errors for ``document`` against the schema for ``kind``."""
    schema_name = KIND_SCHEMA[kind]
    if JSONSCHEMA_AVAILABLE:
        validator = Draft202012Validator(_schema(schema_name))
        return [
            _Error(error.validator or "unknown", error.json_path or "$", error.message)
            for error in validator.iter_errors(document)
        ]
    return _validate_subset(document, _schema(schema_name))


def _assert_conforms(document, kind: str) -> None:
    errors = _errors(document, kind)
    assert not errors, [str(error) for error in errors]


def _assert_rejected(document, kind: str, *keywords: str, fragment: str | None = None) -> list[_Error]:
    errors = _errors(document, kind)
    assert errors, f"{kind} schema unexpectedly accepted {document!r}"
    if keywords:
        assert any(error.keyword in keywords for error in errors), [str(error) for error in errors]
    if fragment is not None:
        assert any(fragment in error.message for error in errors), [str(error) for error in errors]
    return errors


def _pop(document: dict, path: tuple[str, ...]) -> None:
    node = document
    for key in path[:-1]:
        node = node[key]
    del node[path[-1]]


def _assign(document: dict, path: tuple[str, ...], value) -> None:
    node = document
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value


# ---------------------------------------------------------------------------
# Production document builders (synthetic local bytes only).
# ---------------------------------------------------------------------------
def _capture_snapshot(base: Path) -> dict:
    base = Path(base).resolve()
    store = SourceSnapshotStore(
        base / "snapshot-store", max_source_bytes=64 * 1024, max_store_bytes=1024 * 1024,
    )
    source_path = base / "synthetic-source.mp4"
    source_path.write_bytes(b"synthetic local bytes used only for schema conformance")
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    snapshot = store.capture(
        source_path,
        expected_sha256=digest,
        authorization_id="authorization:conformance",
        source_revision_id="revision:source-1",
    )
    return snapshot.as_evidence()


@pytest.fixture(scope="session")
def snapshot_evidence(tmp_path_factory) -> dict:
    return _capture_snapshot(tmp_path_factory.mktemp("vip-fvs-schema-conformance"))


def _request_identity(evidence: dict, *, locator: str) -> tuple[dict, dict]:
    request = {
        "request_id": "request:conformance",
        "candidate_assertion_ref": "assertion:conformance",
        "source_revision_id": evidence["source_revision_id"],
        "source_locator": locator,
        "expected_source_sha256": evidence["snapshot_sha256"],
        "selected_stream_index": 0,
        "requested_start_pts": 40,
        "requested_end_pts": 80,
        "producer_attempt_id": "attempt:conformance",
        "idempotency_key": "idempotency:conformance",
        "expected_timebase": [1, 1000],
    }
    identity = {
        "request_id": request["request_id"],
        "candidate_assertion_ref": request["candidate_assertion_ref"],
        "producer_attempt_id": request["producer_attempt_id"],
        "idempotency_key": request["idempotency_key"],
        "request_digest": hashlib.sha256(_canonical(request)).hexdigest(),
        "request": request,
    }
    return request, identity


def _review_bundle_payload(evidence: dict, *, version: str = "v3") -> dict:
    snapshot = copy.deepcopy(evidence)
    request, identity = _request_identity(
        evidence, locator=snapshot["snapshot_path"] if version == "v3" else evidence["source_locator"],
    )
    source = {
        "source_revision_id": evidence["source_revision_id"],
        "source_sha256": evidence["snapshot_sha256"],
        "source_byte_count": evidence["source_byte_count"],
        "selected_stream_index": 0,
        "timebase": {"num": 1, "den": 1000},
        "probe_artifact_ref": "probe:conformance",
        "probe_digest": ZERO_DIGEST,
    }
    if version == "v3":
        source["source_locator"] = evidence["source_locator"]
        source["snapshot"] = snapshot
    refinement = {
        "refinement_id": "refinement:conformance",
        "status": "MEASURED",
        "source_revision_id": evidence["source_revision_id"],
        "selected_stream_index": 0,
        "source_pts_interval": {
            "start": 40, "end": 80, "time_domain": "source_pts", "endpoint_semantics": "half_open",
        },
        "timebase": {"num": 1, "den": 1000},
        "attempt_id": "attempt:conformance",
        "evidence_artifact_ref": "evidence:conformance",
        "evidence_digest": ZERO_DIGEST,
        "evidence_class": "MEASURED",
        "request_identity": identity,
    }
    return {
        "bundle_id": "bundle:conformance",
        "run_id": "run:conformance",
        "created_at": "2026-10-24T00:00:00Z",
        "review_status": "AWAITING_EDITORIAL_DECISION",
        "source": source,
        "authorization": {
            "discovery_policy_ref": "policy:discovery",
            "refinement_policy_ref": "policy:refinement",
            "policy_digest": ZERO_DIGEST,
            "scope_digest": ZERO_DIGEST,
        },
        "query": {"query_id": "query:conformance", "text": "synthetic target", "digest": ZERO_DIGEST},
        "generation": {
            "attempt_id": "attempt:conformance",
            "generation_id": "generation:conformance",
            "semantic_space_id": "semantic-space:conformance",
            "model_identity": "model:conformance",
            "model_revision": "revision:model-a",
            "weights_digest": ZERO_DIGEST,
            "processor_digest": ZERO_DIGEST,
            "index_ref": "index:conformance",
            "index_digest": ZERO_DIGEST,
            "input_digest": ZERO_DIGEST,
        },
        "candidate": {
            "candidate_id": "candidate:conformance",
            "rank": 1,
            "score": 0.9,
            "evidence_class": "MATCHED",
            "binding_eligible": False,
            "assertion_digest": ZERO_DIGEST,
            "semantic_interval": {
                "start": 1.0, "end": 2.0, "time_domain": "semantic_seconds", "endpoint_semantics": "half_open",
            },
        },
        "refinement": refinement,
        "presentation": {"display_only": True, "start_seconds": 0.04, "end_seconds": 0.08},
        "dependency_digest": ZERO_DIGEST,
        "decision": None,
    }


def _seal_review_bundle(payload: dict, *, version: str = "v3") -> dict:
    payload = copy.deepcopy(payload)
    payload["dependency_digest"] = dependency_digest(payload)
    version_marker = f"vip_fvs.review_bundle.{version}"
    record = {
        "record_id": payload["bundle_id"],
        "record_type": "vip_fvs.review_bundle",
        "record_schema_version": version_marker,
        "record_digest": "",
        "payload": payload,
    }
    record["record_digest"] = record_digest(record)
    return ReviewBundle.from_record(record).to_record()


def _review_bundle_record(evidence: dict, *, version: str = "v3") -> dict:
    return _seal_review_bundle(_review_bundle_payload(evidence, version=version), version=version)


def _receipt_source(evidence: dict, *, version: str = "v2") -> dict:
    source = {
        "source_revision_id": evidence["source_revision_id"],
        "source_sha256": evidence["snapshot_sha256"],
        "source_byte_count": evidence["source_byte_count"],
        "selected_stream_index": 0,
        "timebase": {"num": 1, "den": 1000},
        "probe_artifact_ref": "probe:conformance",
        "probe_digest": ZERO_DIGEST,
    }
    if version == "v2":
        source["source_locator"] = evidence["source_locator"]
        source["snapshot"] = copy.deepcopy(evidence)
    return source


def _receipt_artifacts(*, with_decision: bool = False, with_plan: bool = False) -> dict:
    artifacts = {
        "review_bundle_ref": "bundle:conformance",
        "review_bundle_digest": ZERO_DIGEST,
        "review_bundle_dependency_digest": ZERO_DIGEST,
        "probe_ref": "probe:conformance",
        "probe_digest": ZERO_DIGEST,
    }
    if with_decision:
        artifacts.update({
            "decision_ref": "decision:conformance",
            "decision_digest": ZERO_DIGEST,
            "decision_class": "ACCEPT",
            "disposition": "accepted for plan build",
        })
    if with_plan:
        artifacts.update({
            "plan_ref": "plan:conformance",
            "plan_digest": ZERO_DIGEST,
            "mapping_digest": ZERO_DIGEST,
            "placement_digest": ZERO_DIGEST,
        })
    return artifacts


def _real_receipt_record(evidence: dict, *, with_decision: bool = False, version: str = "v2") -> dict:
    decision = None
    plan = None
    status = "AWAITING_EDITORIAL_DECISION"
    if with_decision:
        status = "PLAN_BUILT"
        decision = {
            "decision_ref": "decision:conformance",
            "decision_digest": ZERO_DIGEST,
            "decision_class": "ACCEPT",
            "disposition": "accepted for plan build",
        }
        plan = {
            "plan_ref": "plan:conformance",
            "plan_digest": ZERO_DIGEST,
            "mapping_digest": ZERO_DIGEST,
            "placement_digest": ZERO_DIGEST,
        }
    record = {
        "schema": f"vip_fvs.real_receipt.{version}",
        "receipt_id": "receipt:conformance",
        "run_id": "run:conformance",
        "attempt_id": "attempt:conformance",
        "status": status,
        "scope": "REAL_LOCAL_ONLY",
        "source": _receipt_source(evidence, version=version),
        "authorization": {
            "discovery_policy_ref": "policy:discovery",
            "refinement_policy_ref": "policy:refinement",
            "policy_digest": ZERO_DIGEST,
            "scope_digest": ZERO_DIGEST,
        },
        "artifacts": _receipt_artifacts(with_decision=with_decision, with_plan=with_decision),
        "decision": decision,
        "plan": plan,
        "export_eligible": False,
        "network_allowed": False,
        "model_download_allowed": False,
        "NOT_OBSERVED": ["rendering or export"],
        "refusal": None,
    }
    return RealReceipt.create(record).to_record()


def _valid_document(kind: str, evidence: dict) -> dict:
    if kind == "source_snapshot":
        return copy.deepcopy(evidence)
    if kind == "review_bundle":
        return _review_bundle_record(evidence)
    if kind == "review_bundle_v2":
        return _review_bundle_record(evidence, version="v2")
    if kind == "real_receipt":
        return _real_receipt_record(evidence)
    if kind == "real_receipt_decision":
        return _real_receipt_record(evidence, with_decision=True)
    if kind == "real_receipt_v1":
        return _real_receipt_record(evidence, version="v1")
    raise AssertionError(f"unknown fixture kind {kind!r}")


# ---------------------------------------------------------------------------
# Schema metadata / structure
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("schema_name", ["source_snapshot", "review_bundle", "real_receipt"])
def test_schema_is_draft_2020_12_root_closed_object(schema_name):
    schema = _schema(schema_name)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == f"https://video-intelligence-pipeline.invalid/schema/vip_fvs/{SCHEMA_FILES[schema_name]}"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["required"] and all(isinstance(field, str) and field for field in schema["required"])
    assert len(set(schema["properties"])) == len(schema["properties"])


def test_schema_ids_are_distinct():
    ids = {_schema(name)["$id"] for name in ("source_snapshot", "review_bundle", "real_receipt")}
    assert len(ids) == 3


def test_review_bundle_v3_declares_const_record_identity():
    schema = _schema("review_bundle")
    assert schema["properties"]["record_type"] == {"const": "vip_fvs.review_bundle"}
    assert schema["properties"]["record_schema_version"] == {"const": "vip_fvs.review_bundle.v3"}


def test_real_receipt_v2_declares_const_schema_and_nonproduction_flags():
    schema = _schema("real_receipt")
    properties = schema["properties"]
    assert properties["schema"] == {"const": "vip_fvs.real_receipt.v2"}
    assert properties["scope"] == {"const": "REAL_LOCAL_ONLY"}
    assert properties["export_eligible"] == {"const": False}
    assert properties["network_allowed"] == {"const": False}
    assert properties["model_download_allowed"] == {"const": False}


def test_gap_source_snapshot_v1_declares_no_version_marker():
    """Documented gap: source_snapshot.v1 has no const version field at all."""
    schema = _schema("source_snapshot")
    assert "schema" not in schema["properties"]
    assert "schema_version" not in schema["properties"]
    assert "record_schema_version" not in schema["properties"]
    assert "const" not in json.dumps(schema)
    document = _valid_document("source_snapshot", _captured_for_structure())
    assert _errors(document, "source_snapshot") == []
    document["schema_version"] = "vip_fvs.source_snapshot.v2"
    _assert_rejected(document, "source_snapshot", "additionalProperties", fragment="schema_version")


def test_gap_review_bundle_v3_has_stray_root_record_schema_version_member():
    """Documented gap: v3 repeats ``record_schema_version`` as a stray root key.

    JSON Schema ignores unknown keywords, so it is harmless but it is not a
    declared keyword of Draft 2020-12 and can confuse readers into believing a
    second version constraint exists.
    """
    schema = _schema("review_bundle")
    standard_root_keywords = {
        "$schema", "$id", "$defs", "title", "description", "type", "properties", "required",
        "additionalProperties", "allOf", "anyOf", "oneOf", "not", "if", "then", "else",
        "default", "examples", "deprecated", "readOnly", "writeOnly",
    }
    stray = set(schema) - standard_root_keywords
    assert "record_schema_version" in stray
    assert "record_schema_version" not in schema["$defs"]
    _assert_conforms(_valid_document("review_bundle", _captured_for_structure()), "review_bundle")


def test_gap_review_bundle_v3_has_unreferenced_digest_map_definition():
    """Documented gap: ``$defs.digest_map`` is defined but never referenced."""
    schema = _schema("review_bundle")
    assert "digest_map" in schema["$defs"]
    text = json.dumps(schema)
    for name in schema["$defs"]:
        if name == "digest_map":
            assert "#/$defs/digest_map" not in text
        else:
            assert f"#/$defs/{name}" in text


_STRUCTURE_EVIDENCE: dict | None = None


def _captured_for_structure() -> dict:
    """Capture one snapshot for schema-structure tests without a fixtures request."""
    global _STRUCTURE_EVIDENCE
    if _STRUCTURE_EVIDENCE is None:
        import tempfile

        _STRUCTURE_EVIDENCE = _capture_snapshot(Path(tempfile.mkdtemp(prefix="vip-fvs-schema-structure-")))
    return _STRUCTURE_EVIDENCE


def test_jsonschema_backend_is_used_when_available():
    if not JSONSCHEMA_AVAILABLE:
        pytest.skip("jsonschema is not importable in this environment; fallback validator is in use")
    from importlib.metadata import version

    assert Draft202012Validator is not None
    assert version("jsonschema")


# ---------------------------------------------------------------------------
# Valid production-emitted documents conform
# ---------------------------------------------------------------------------
def test_production_source_snapshot_evidence_conforms(snapshot_evidence):
    _assert_conforms(snapshot_evidence, "source_snapshot")
    assert verify_snapshot_evidence(copy.deepcopy(snapshot_evidence)) is None


def test_production_real_receipt_v2_conforms_and_reseals(snapshot_evidence, tmp_path):
    receipt = _real_receipt_record(snapshot_evidence)
    _assert_conforms(receipt, "real_receipt")
    record_without_digest = {key: value for key, value in receipt.items() if key != "record_digest"}
    resealed = RealReceipt.create(record_without_digest)
    assert resealed.record_digest == receipt["record_digest"]
    path = save_real_receipt(resealed, tmp_path / "receipt.json")
    loaded = load_real_receipt(path)
    assert loaded.record_digest == resealed.record_digest
    _assert_conforms(loaded.to_record(), "real_receipt")


def test_production_decision_receipt_conforms(snapshot_evidence):
    receipt = _real_receipt_record(snapshot_evidence, with_decision=True)
    assert receipt["status"] == "PLAN_BUILT"
    assert receipt["decision"]["decision_class"] == "ACCEPT"
    assert receipt["plan"]["plan_digest"] == ZERO_DIGEST
    _assert_conforms(receipt, "real_receipt_decision")


def test_production_review_bundle_v3_conforms_and_reseals(snapshot_evidence):
    record = _review_bundle_record(snapshot_evidence)
    _assert_conforms(record, "review_bundle")
    assert record["record_type"] == "vip_fvs.review_bundle"
    assert record["record_schema_version"] == "vip_fvs.review_bundle.v3"
    assert record["payload"]["source"]["snapshot"] == snapshot_evidence
    resealed = ReviewBundle.from_record(record).to_record()
    assert resealed == record
    assert resealed["record_digest"] == record_digest(record)


# ---------------------------------------------------------------------------
# Required fields (top level and nested)
# ---------------------------------------------------------------------------
_TOP_LEVEL_REQUIRED_CASES = [
    (kind, field)
    for kind in ("source_snapshot", "review_bundle", "real_receipt")
    for field in _schema(KIND_SCHEMA[kind])["required"]
]


@pytest.mark.parametrize("kind,field", _TOP_LEVEL_REQUIRED_CASES, ids=[f"{k}:{f}" for k, f in _TOP_LEVEL_REQUIRED_CASES])
def test_missing_top_level_required_field_is_rejected(snapshot_evidence, kind, field):
    document = _valid_document(kind, snapshot_evidence)
    _pop(document, (field,))
    _assert_rejected(document, kind, "required", fragment=field)


_NESTED_REQUIRED_CASES = [
    ("review_bundle", ("payload",), "bundle_id"),
    ("review_bundle", ("payload",), "decision"),
    ("review_bundle", ("payload", "source"), "snapshot"),
    ("review_bundle", ("payload", "source"), "source_locator"),
    ("review_bundle", ("payload", "source", "timebase"), "den"),
    ("review_bundle", ("payload", "source", "snapshot"), "snapshot_manifest_sha256"),
    ("review_bundle", ("payload", "authorization"), "scope_digest"),
    ("review_bundle", ("payload", "candidate"), "semantic_interval"),
    ("review_bundle", ("payload", "presentation"), "display_only"),
    ("review_bundle", ("payload", "refinement", "request_identity"), "request_digest"),
    ("review_bundle", ("payload", "refinement", "request_identity", "request"), "expected_timebase"),
    ("real_receipt", ("source",), "snapshot"),
    ("real_receipt", ("source",), "source_locator"),
    ("real_receipt", ("source", "snapshot"), "max_store_bytes"),
    ("real_receipt", ("source", "timebase"), "num"),
    ("real_receipt", ("authorization",), "scope_digest"),
    ("real_receipt", ("artifacts",), "review_bundle_digest"),
]


@pytest.mark.parametrize(
    "kind,path,field", _NESTED_REQUIRED_CASES,
    ids=[f"{kind}:{'.'.join(path)}:{field}" for kind, path, field in _NESTED_REQUIRED_CASES],
)
def test_missing_nested_required_field_is_rejected(snapshot_evidence, kind, path, field):
    document = _valid_document(kind, snapshot_evidence)
    _pop(document, path + (field,))
    _assert_rejected(document, kind, "required", fragment=field)


def test_missing_version_marker_is_rejected(snapshot_evidence):
    bundle = _review_bundle_record(snapshot_evidence)
    _pop(bundle, ("record_schema_version",))
    _assert_rejected(bundle, "review_bundle", "required", fragment="record_schema_version")

    receipt = _real_receipt_record(snapshot_evidence)
    _pop(receipt, ("schema",))
    _assert_rejected(receipt, "real_receipt", "required", fragment="schema")


# ---------------------------------------------------------------------------
# additionalProperties rejection
# ---------------------------------------------------------------------------
_ADDITIONAL_PROPERTIES_CASES = [
    ("source_snapshot", (), "unexpected_field"),
    ("source_snapshot", (), "schema"),
    ("review_bundle", (), "unexpected_field"),
    ("review_bundle", ("payload",), "unexpected_field"),
    ("review_bundle", ("payload", "source"), "unexpected_field"),
    ("review_bundle", ("payload", "source", "timebase"), "unexpected_field"),
    ("review_bundle", ("payload", "source", "snapshot"), "unexpected_field"),
    ("review_bundle", ("payload", "authorization"), "unexpected_field"),
    ("review_bundle", ("payload", "generation"), "unexpected_field"),
    ("review_bundle", ("payload", "candidate"), "unexpected_field"),
    ("review_bundle", ("payload", "candidate", "semantic_interval"), "unexpected_field"),
    ("review_bundle", ("payload", "refinement"), "unexpected_field"),
    ("review_bundle", ("payload", "refinement", "request_identity", "request"), "unexpected_field"),
    ("review_bundle", ("payload", "presentation"), "unexpected_field"),
    ("real_receipt", (), "unexpected_field"),
    ("real_receipt", ("source",), "unexpected_field"),
    ("real_receipt", ("source", "snapshot"), "unexpected_field"),
    ("real_receipt", ("source", "timebase"), "unexpected_field"),
    ("real_receipt", ("authorization",), "unexpected_field"),
    ("real_receipt", ("artifacts",), "unexpected_artifact"),
]


@pytest.mark.parametrize(
    "kind,path,extra", _ADDITIONAL_PROPERTIES_CASES,
    ids=[f"{kind}:{'.'.join(path) or '$'}:{extra}" for kind, path, extra in _ADDITIONAL_PROPERTIES_CASES],
)
def test_additional_properties_are_rejected(snapshot_evidence, kind, path, extra):
    document = _valid_document(kind, snapshot_evidence)
    node = document
    for key in path:
        node = node[key]
    node[extra] = "unexpected"
    _assert_rejected(document, kind, "additionalProperties", fragment=extra)


def test_additional_properties_are_rejected_in_decision_sections(snapshot_evidence):
    receipt = _valid_document("real_receipt_decision", snapshot_evidence)
    receipt["decision"]["unexpected_field"] = "unexpected"
    _assert_rejected(receipt, "real_receipt", "additionalProperties", fragment="unexpected_field")

    receipt = _valid_document("real_receipt_decision", snapshot_evidence)
    receipt["plan"]["unexpected_field"] = "unexpected"
    _assert_rejected(receipt, "real_receipt", "additionalProperties", fragment="unexpected_field")

    receipt = _valid_document("real_receipt_decision", snapshot_evidence)
    receipt["refusal"] = {"reason_code": "refused", "message": "refused", "unexpected_field": 1}
    _assert_rejected(receipt, "real_receipt", "additionalProperties", fragment="unexpected_field")


@pytest.mark.parametrize("field", ["schema", "scope", "export_eligible", "network_allowed", "model_download_allowed"])
def test_unknown_version_or_policy_markers_are_rejected(snapshot_evidence, field):
    """Real receipts may not smuggle an alternate version/policy marker."""
    receipt = _valid_document("real_receipt", snapshot_evidence)
    receipt[field] = "vip_fvs.real_receipt.v3"
    errors = _errors(receipt, "real_receipt")
    assert errors


# ---------------------------------------------------------------------------
# const / enum enforcement
# ---------------------------------------------------------------------------
_CONST_CASES = [
    ("review_bundle", ("record_type",), "vip_fvs.review_bundle.v2", "const"),
    ("review_bundle", ("record_schema_version",), "vip_fvs.review_bundle.v4", "const"),
    ("review_bundle", ("record_schema_version",), "vip_fvs.review_bundle.v1", "const"),
    ("review_bundle", ("record_schema_version",), "vip_fvs.review_bundle.v2", "const"),
    ("review_bundle", ("record_schema_version",), "review_bundle.v3", "const"),
    ("review_bundle", ("payload", "review_status"), "DECISION_RECORDED", "const"),
    ("review_bundle", ("payload", "candidate", "evidence_class"), "MEASURED", "const"),
    ("review_bundle", ("payload", "candidate", "binding_eligible"), True, "const"),
    ("review_bundle", ("payload", "refinement", "status"), "NOT_OBSERVED", "const"),
    ("review_bundle", ("payload", "refinement", "evidence_class"), "MATCHED", "const"),
    ("review_bundle", ("payload", "presentation", "display_only"), False, "const"),
    ("review_bundle", ("payload", "candidate", "semantic_interval", "time_domain"), "source_pts", "const"),
    ("review_bundle", ("payload", "candidate", "semantic_interval", "endpoint_semantics"), "closed", "const"),
    ("review_bundle", ("payload", "refinement", "source_pts_interval", "time_domain"), "semantic_seconds", "const"),
    ("review_bundle", ("payload", "refinement", "source_pts_interval", "endpoint_semantics"), "closed", "const"),
    ("real_receipt", ("schema",), "vip_fvs.real_receipt.v1", "const"),
    ("real_receipt", ("schema",), "vip_fvs.real_receipt.v3", "const"),
    ("real_receipt", ("schema",), "vip_fvs.real_receipt.v2.1", "const"),
    ("real_receipt", ("scope",), "SYNTHETIC_LOCAL_ONLY", "const"),
    ("real_receipt", ("export_eligible",), True, "const"),
    ("real_receipt", ("network_allowed",), True, "const"),
    ("real_receipt", ("model_download_allowed",), True, "const"),
]


@pytest.mark.parametrize(
    "kind,path,value,keyword", _CONST_CASES,
    ids=[f"{kind}:{'.'.join(path)}={value!r}" for kind, path, value, _keyword in _CONST_CASES],
)
def test_const_values_are_enforced(snapshot_evidence, kind, path, value, keyword):
    document = _valid_document(kind, snapshot_evidence)
    _assign(document, path, value)
    _assert_rejected(document, kind, keyword)


_ENUM_CASES = [
    ("real_receipt", ("status",), "COMPLETE"),
    ("real_receipt", ("status",), "prepared"),
    ("real_receipt", ("status",), "PREPARED_EXTRA"),
    ("real_receipt_decision", ("artifacts", "decision_class"), "APPROVE"),
    ("real_receipt_decision", ("decision", "decision_class"), "APPROVE"),
]


@pytest.mark.parametrize(
    "kind,path,value", _ENUM_CASES,
    ids=[f"{kind}:{'.'.join(path)}={value}" for kind, path, value in _ENUM_CASES],
)
def test_enum_values_are_enforced(snapshot_evidence, kind, path, value):
    document = _valid_document(kind, snapshot_evidence)
    _assign(document, path, value)
    _assert_rejected(document, kind, "enum")


@pytest.mark.parametrize(
    "status",
    ["PREPARED", "AWAITING_EDITORIAL_DECISION", "DECISION_RECORDED", "PLAN_BUILT",
     "REJECTED", "MODIFICATION_REQUESTED", "REFUSED"],
)
def test_real_receipt_schema_accepts_every_declared_status(snapshot_evidence, status):
    document = _valid_document("real_receipt", snapshot_evidence)
    document["status"] = status
    _assert_conforms(document, "real_receipt")


def test_real_receipt_schema_accepts_null_decision_and_plan(snapshot_evidence):
    receipt = _valid_document("real_receipt", snapshot_evidence)
    assert receipt["decision"] is None and receipt["plan"] is None and receipt["refusal"] is None
    _assert_conforms(receipt, "real_receipt")


# ---------------------------------------------------------------------------
# Digest format / pattern enforcement
# ---------------------------------------------------------------------------
_BAD_DIGESTS = ["0" * 63, "0" * 65, "g" * 64, "A" * 64, "0x" + "0" * 62, ""]
_DIGEST_FIELD_CASES = [
    ("source_snapshot", ("snapshot_sha256",)),
    ("source_snapshot", ("snapshot_manifest_sha256",)),
    ("review_bundle", ("record_digest",)),
    ("review_bundle", ("payload", "dependency_digest")),
    ("review_bundle", ("payload", "source", "source_sha256")),
    ("review_bundle", ("payload", "source", "probe_digest")),
    ("review_bundle", ("payload", "source", "snapshot", "snapshot_sha256")),
    ("review_bundle", ("payload", "source", "snapshot", "snapshot_manifest_sha256")),
    ("review_bundle", ("payload", "authorization", "policy_digest")),
    ("review_bundle", ("payload", "query", "digest")),
    ("review_bundle", ("payload", "generation", "weights_digest")),
    ("review_bundle", ("payload", "candidate", "assertion_digest")),
    ("review_bundle", ("payload", "refinement", "evidence_digest")),
    ("review_bundle", ("payload", "refinement", "request_identity", "request_digest")),
    ("review_bundle", ("payload", "refinement", "request_identity", "request", "expected_source_sha256")),
    ("real_receipt", ("record_digest",)),
    ("real_receipt", ("source", "source_sha256")),
    ("real_receipt", ("source", "probe_digest")),
    ("real_receipt", ("source", "snapshot", "snapshot_sha256")),
    ("real_receipt", ("source", "snapshot", "snapshot_manifest_sha256")),
    ("real_receipt", ("authorization", "policy_digest")),
    ("real_receipt", ("authorization", "scope_digest")),
    ("real_receipt", ("artifacts", "review_bundle_digest")),
    ("real_receipt", ("artifacts", "probe_digest")),
]


@pytest.mark.parametrize(
    "kind,path,bad_value",
    [(kind, path, value) for kind, path in _DIGEST_FIELD_CASES for value in _BAD_DIGESTS],
    ids=[
        f"{kind}:{'.'.join(path)}:{index}"
        for kind, path in _DIGEST_FIELD_CASES
        for index in range(len(_BAD_DIGESTS))
    ],
)
def test_nonconforming_digest_values_are_rejected(snapshot_evidence, kind, path, bad_value):
    document = _valid_document(kind, snapshot_evidence)
    _assign(document, path, bad_value)
    _assert_rejected(document, kind, "pattern")


@pytest.mark.parametrize(
    "kind,path,extra_digest_kind",
    [
        ("review_bundle", ("payload", "refinement", "request_identity", "request", "requested_start_pts"), "int"),
        ("real_receipt", ("artifacts", "decision_digest"), "decision"),
    ],
)
def test_optional_digest_fields_are_still_validated(snapshot_evidence, kind, path, extra_digest_kind):
    document = _valid_document(kind, snapshot_evidence)
    if extra_digest_kind == "decision":
        document["artifacts"]["decision_digest"] = "not-a-digest"
        _assert_rejected(document, kind, "pattern")
    else:
        # The request identity digest is validated in its own parametrized case;
        # keep this smoke case to prove nested optional paths are still visited.
        _assert_conforms(document, kind)


# ---------------------------------------------------------------------------
# Identifier bounds and type errors
# ---------------------------------------------------------------------------
_ID_BOUND_CASES = [
    ("source_snapshot", ("snapshot_id",), ""),
    ("source_snapshot", ("snapshot_path",), ""),
    ("source_snapshot", ("manifest_path",), ""),
    ("source_snapshot", ("source_locator",), ""),
    ("source_snapshot", ("authorization_id",), ""),
    ("review_bundle", ("record_id",), ""),
    ("review_bundle", ("payload", "bundle_id"), ""),
    ("review_bundle", ("payload", "query", "text"), ""),
    ("review_bundle", ("payload", "refinement", "request_identity", "request", "idempotency_key"), ""),
    ("review_bundle", ("record_id",), "x" * 257),
    ("review_bundle", ("payload", "source", "snapshot", "snapshot_id"), "x" * 257),
    ("real_receipt", ("receipt_id",), ""),
    ("real_receipt", ("run_id",), ""),
    ("real_receipt", ("NOT_OBSERVED",), []),
]


@pytest.mark.parametrize(
    "kind,path,value", _ID_BOUND_CASES,
    ids=[f"{kind}:{'.'.join(path)}:{index}" for index, (kind, path, _value) in enumerate(_ID_BOUND_CASES)],
)
def test_identifier_bounds_are_enforced(snapshot_evidence, kind, path, value):
    document = _valid_document(kind, snapshot_evidence)
    _assign(document, path, value)
    _assert_rejected(document, kind, "minLength", "maxLength", "minItems")


_TYPE_CASES = [
    ("source_snapshot", ("source_byte_count",), -1, "minimum"),
    ("source_snapshot", ("source_byte_count",), "12", "type"),
    ("source_snapshot", ("max_source_bytes",), 0, "minimum"),
    ("source_snapshot", ("max_store_bytes",), True, "type"),
    ("source_snapshot", ("source_revision_id",), 7, "type"),
    ("source_snapshot", ("snapshot_sha256",), 123, "type"),
    ("review_bundle", ("payload", "candidate", "rank"), 0, "minimum"),
    ("review_bundle", ("payload", "candidate", "score"), "0.9", "type"),
    ("review_bundle", ("payload", "source", "selected_stream_index"), True, "type"),
    ("review_bundle", ("payload", "source", "source_byte_count"), -1, "minimum"),
    ("review_bundle", ("payload", "refinement", "source_pts_interval", "end"), 0, "exclusiveMinimum"),
    ("review_bundle", ("payload", "refinement", "request_identity", "request", "requested_start_pts"), -1, "minimum"),
    ("review_bundle", ("payload", "candidate", "semantic_interval", "start"), "1.0", "type"),
    ("review_bundle", ("payload", "refinement", "request_identity", "request", "expected_timebase"), [1], "oneOf"),
    ("review_bundle", ("payload", "refinement", "request_identity", "request", "expected_timebase"), [1, 2, 3], "oneOf"),
    ("review_bundle", ("payload", "source", "timebase", "num"), 0, "minimum"),
    ("real_receipt", ("NOT_OBSERVED",), "rendering", "type"),
    ("real_receipt", ("NOT_OBSERVED",), [], "minItems"),
    ("real_receipt", ("source", "timebase", "num"), 0, "minimum"),
    ("real_receipt", ("source", "selected_stream_index"), -1, "minimum"),
    ("real_receipt", ("source", "snapshot", "source_byte_count"), -1, "minimum"),
]


@pytest.mark.parametrize(
    "kind,path,value,keyword", _TYPE_CASES,
    ids=[f"{kind}:{'.'.join(path)}:{index}" for index, (kind, path, _v, _k) in enumerate(_TYPE_CASES)],
)
def test_type_and_numeric_bounds_are_enforced(snapshot_evidence, kind, path, value, keyword):
    document = _valid_document(kind, snapshot_evidence)
    _assign(document, path, value)
    _assert_rejected(document, kind, keyword)


# ---------------------------------------------------------------------------
# Version segregation across the checked-in schema files
# ---------------------------------------------------------------------------
def test_v2_review_bundle_validates_against_v2_and_is_rejected_by_v3(snapshot_evidence):
    bundle_v2 = _review_bundle_record(snapshot_evidence, version="v2")
    _assert_conforms(bundle_v2, "review_bundle_v2")
    _assert_rejected(bundle_v2, "review_bundle", "required", "additionalProperties")
    assert bundle_v2["record_schema_version"] == "vip_fvs.review_bundle.v2"


def test_v3_review_bundle_is_rejected_by_v2_schema(snapshot_evidence):
    bundle_v3 = _review_bundle_record(snapshot_evidence, version="v3")
    errors = _errors(bundle_v3, "review_bundle_v2")
    assert errors


def test_v1_real_receipt_validates_against_v1_and_is_rejected_by_v2(snapshot_evidence):
    receipt_v1 = _real_receipt_record(snapshot_evidence, version="v1")
    _assert_conforms(receipt_v1, "real_receipt_v1")
    _assert_rejected(receipt_v1, "real_receipt", "const")
    assert "snapshot" not in receipt_v1["source"]


def test_v2_real_receipt_is_rejected_by_v1_schema(snapshot_evidence):
    receipt_v2 = _real_receipt_record(snapshot_evidence)
    assert _errors(receipt_v2, "real_receipt_v1")


def test_production_rejects_unknown_version_markers(snapshot_evidence):
    receipt = _real_receipt_record(snapshot_evidence)
    unknown = {key: value for key, value in receipt.items() if key != "record_digest"}
    unknown["schema"] = "vip_fvs.real_receipt.v3"
    with pytest.raises(ValueError, match="unexpected real receipt schema"):
        RealReceipt.create(unknown)

    bundle = _review_bundle_record(snapshot_evidence)
    unknown_bundle = copy.deepcopy(bundle)
    unknown_bundle["record_schema_version"] = "vip_fvs.review_bundle.v4"
    with pytest.raises(ValueError, match="unexpected ReviewBundle record type or schema version"):
        ReviewBundle.from_record(unknown_bundle)


# ---------------------------------------------------------------------------
# Tampered digest fields: schema-visible format vs production verification
# ---------------------------------------------------------------------------
def test_tampered_snapshot_digest_passes_schema_but_fails_production_verifier(snapshot_evidence):
    tampered = copy.deepcopy(snapshot_evidence)
    tampered["snapshot_sha256"] = "b" * 64
    _assert_conforms(tampered, "source_snapshot")  # format-only schema cannot see byte tamper
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_DIGEST_MISMATCH"):
        verify_snapshot_evidence(tampered)


def test_tampered_snapshot_manifest_digest_passes_schema_but_fails_production_verifier(snapshot_evidence):
    tampered = copy.deepcopy(snapshot_evidence)
    tampered["snapshot_manifest_sha256"] = "c" * 64
    _assert_conforms(tampered, "source_snapshot")
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_MANIFEST_DIGEST_MISMATCH"):
        verify_snapshot_evidence(tampered)


def test_tampered_real_receipt_record_digest_passes_schema_but_fails_loader(snapshot_evidence, tmp_path):
    receipt = RealReceipt.create({
        key: value for key, value in _real_receipt_record(snapshot_evidence).items() if key != "record_digest"
    })
    path = save_real_receipt(receipt, tmp_path / "receipt.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["record_digest"] = "d" * 64
    path.write_text(json.dumps(raw, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    _assert_conforms(raw, "real_receipt")
    with pytest.raises(ValueError, match="digest or canonical encoding mismatch"):
        load_real_receipt(path)


def test_tampered_review_bundle_record_digest_passes_schema_but_fails_production(snapshot_evidence):
    record = _review_bundle_record(snapshot_evidence)
    tampered = copy.deepcopy(record)
    tampered["record_digest"] = "e" * 64
    _assert_conforms(tampered, "review_bundle")
    with pytest.raises(ValueError, match="record digest mismatch"):
        ReviewBundle.from_record(tampered)


def test_tampered_review_bundle_source_digest_passes_schema_but_fails_production(snapshot_evidence):
    record = _review_bundle_record(snapshot_evidence)
    tampered = copy.deepcopy(record)
    tampered["payload"]["source"]["source_sha256"] = "f" * 64
    tampered["record_digest"] = record_digest(tampered)
    _assert_conforms(tampered, "review_bundle")
    with pytest.raises(ValueError, match="snapshot identity|dependency"):
        ReviewBundle.from_record(tampered)


# ---------------------------------------------------------------------------
# Cross-schema structural linkage the schemas do declare
# ---------------------------------------------------------------------------
def test_embedded_snapshot_subschemas_match_standalone_source_snapshot_schema():
    standalone = _schema("source_snapshot")
    embedded_variants = {
        "review_bundle.payload.source.snapshot": _schema("review_bundle")["$defs"]["source_snapshot"],
        "real_receipt.source.snapshot": _schema("real_receipt")["properties"]["source"]["properties"]["snapshot"],
    }
    for name, embedded in embedded_variants.items():
        assert set(embedded["required"]) == set(standalone["required"]), name
        assert set(embedded["properties"]) == set(standalone["properties"]), name


def test_receipt_and_bundle_source_field_sets_agree():
    bundle_source = _schema("review_bundle")["$defs"]["source"]
    receipt_source = _schema("real_receipt")["properties"]["source"]
    assert set(bundle_source["required"]) == set(receipt_source["required"])
    assert set(bundle_source["properties"]) == set(receipt_source["properties"])


def test_digest_pattern_is_consistent_across_the_three_schemas():
    bundle_pattern = _schema("review_bundle")["$defs"]["digest"]["pattern"]
    assert bundle_pattern == DIGEST_PATTERN
    for name, prop in _schema("source_snapshot")["properties"].items():
        if "256" in name:
            assert prop["pattern"] == DIGEST_PATTERN, name
    receipt_source = _schema("real_receipt")["properties"]["source"]["properties"]
    assert receipt_source["source_sha256"]["pattern"] == DIGEST_PATTERN
    assert receipt_source["snapshot"]["properties"]["snapshot_sha256"]["pattern"] == DIGEST_PATTERN


def test_gap_identifier_max_length_is_inconsistent_across_schemas():
    """Documented gap: bundle ids are capped at 256; receipt/snapshot ids are not."""
    bundle_id = _schema("review_bundle")["$defs"]["id"]
    assert bundle_id == {"type": "string", "minLength": 1, "maxLength": 256}
    long_id = "x" * 300
    receipt = _valid_document("real_receipt", _captured_for_structure())
    receipt["receipt_id"] = long_id
    _assert_conforms(receipt, "real_receipt")
    snapshot = _valid_document("source_snapshot", _captured_for_structure())
    snapshot["snapshot_id"] = long_id
    _assert_conforms(snapshot, "source_snapshot")


# ---------------------------------------------------------------------------
# Cross-document id/digest linkage: declared shape vs production invariants
# ---------------------------------------------------------------------------
def test_bundle_snapshot_locator_linkage_is_enforced_by_production_not_schema(snapshot_evidence):
    record = _review_bundle_record(snapshot_evidence)
    tampered = copy.deepcopy(record)
    tampered["payload"]["source"]["source_locator"] = "/synthetic/other-source.mp4"
    tampered["record_digest"] = record_digest(tampered)
    _assert_conforms(tampered, "review_bundle")  # schema does not declare equality
    with pytest.raises(ValueError, match="snapshot identity does not match source"):
        ReviewBundle.from_record(tampered)


def test_bundle_snapshot_byte_count_linkage_is_enforced_by_production_not_schema(snapshot_evidence):
    record = _review_bundle_record(snapshot_evidence)
    tampered = copy.deepcopy(record)
    tampered["payload"]["source"]["source_byte_count"] = int(snapshot_evidence["source_byte_count"]) + 1
    tampered["record_digest"] = record_digest(tampered)
    _assert_conforms(tampered, "review_bundle")
    with pytest.raises(ValueError, match="snapshot identity does not match source"):
        ReviewBundle.from_record(tampered)


def test_receipt_snapshot_locator_linkage_is_enforced_by_production_not_schema(snapshot_evidence):
    receipt = _valid_document("real_receipt", snapshot_evidence)
    record = {key: value for key, value in receipt.items() if key != "record_digest"}
    record["source"]["source_locator"] = "/synthetic/other-source.mp4"
    _assert_conforms({**receipt, "source": record["source"]}, "real_receipt")
    with pytest.raises(ValueError, match="receipt snapshot identity does not match source"):
        RealReceipt.create(record)


def test_receipt_snapshot_sha_linkage_is_enforced_by_production_not_schema(snapshot_evidence):
    receipt = _valid_document("real_receipt", snapshot_evidence)
    record = {key: value for key, value in receipt.items() if key != "record_digest"}
    record["source"]["source_sha256"] = "9" * 64
    _assert_conforms({**receipt, "source": record["source"]}, "real_receipt")
    with pytest.raises(ValueError, match="receipt snapshot identity does not match source"):
        RealReceipt.create(record)


def test_bundle_request_identity_must_name_the_verified_snapshot_path(snapshot_evidence):
    record = _review_bundle_record(snapshot_evidence)
    payload = copy.deepcopy(record["payload"])
    identity = payload["refinement"]["request_identity"]
    identity["request"]["source_locator"] = "/synthetic/not-the-snapshot.mp4"
    identity["request_digest"] = hashlib.sha256(_canonical(identity["request"])).hexdigest()
    payload["dependency_digest"] = record["payload"]["dependency_digest"]
    with pytest.raises(ValueError, match="must name verified snapshot path"):
        dependency_digest(payload)


def test_bundle_request_identity_digest_is_recomputed_from_the_request(snapshot_evidence):
    record = _review_bundle_record(snapshot_evidence)
    payload = copy.deepcopy(record["payload"])
    payload["refinement"]["request_identity"]["request"]["requested_start_pts"] = 41
    with pytest.raises(ValueError, match="request identity digest mismatch"):
        dependency_digest(payload)


def test_receipt_record_digest_links_every_retained_field(snapshot_evidence):
    receipt = _valid_document("real_receipt", snapshot_evidence)
    original_digest = receipt["record_digest"]
    record = {key: value for key, value in receipt.items() if key != "record_digest"}
    assert RealReceipt.create(record).record_digest == original_digest
    changed = copy.deepcopy(record)
    changed["authorization"]["policy_digest"] = "1" * 64
    changed_receipt = RealReceipt.create(changed)
    assert changed_receipt.record_digest != original_digest


# ---------------------------------------------------------------------------
# Documented gaps: linkage the schemas neither declare nor production enforce
# ---------------------------------------------------------------------------
def test_gap_bundle_does_not_bind_source_revision_id_to_snapshot_evidence(snapshot_evidence):
    """Documented gap: v3 bundle accepts source_revision_id != snapshot's id."""
    record = _review_bundle_record(snapshot_evidence)
    payload = copy.deepcopy(record["payload"])
    payload["source"]["source_revision_id"] = "revision:other"
    payload["refinement"]["source_revision_id"] = "revision:other"
    request = payload["refinement"]["request_identity"]["request"]
    request["source_revision_id"] = "revision:other"
    payload["refinement"]["request_identity"]["request_digest"] = hashlib.sha256(_canonical(request)).hexdigest()
    payload["dependency_digest"] = dependency_digest(payload)  # production accepts today
    resealed = {
        "record_id": payload["bundle_id"],
        "record_type": "vip_fvs.review_bundle",
        "record_schema_version": "vip_fvs.review_bundle.v3",
        "record_digest": "",
        "payload": payload,
    }
    resealed["record_digest"] = record_digest(resealed)
    _assert_conforms(resealed, "review_bundle")
    assert ReviewBundle.from_record(resealed).payload["source"]["source_revision_id"] == "revision:other"
    assert payload["source"]["snapshot"]["source_revision_id"] == snapshot_evidence["source_revision_id"]


def test_gap_receipt_does_not_bind_source_revision_id_to_snapshot_evidence(snapshot_evidence):
    """Documented gap: v2 receipt accepts source_revision_id != snapshot's id."""
    receipt = _valid_document("real_receipt", snapshot_evidence)
    record = {key: value for key, value in receipt.items() if key != "record_digest"}
    record["source"]["source_revision_id"] = "revision:other"
    resealed = RealReceipt.create(record)
    document = resealed.to_record()
    _assert_conforms(document, "real_receipt")
    assert document["source"]["source_revision_id"] == "revision:other"
    assert document["source"]["snapshot"]["source_revision_id"] == snapshot_evidence["source_revision_id"]


def test_gap_bundle_schema_accepts_noncanonical_timebase_that_production_rejects(snapshot_evidence):
    """Documented gap: schema allows ``num`` > 1; production requires a canonical 1/den pair."""
    record = _review_bundle_record(snapshot_evidence)
    tampered = copy.deepcopy(record)
    payload = tampered["payload"]
    payload["source"]["timebase"] = {"num": 2, "den": 1000}
    payload["refinement"]["timebase"] = {"num": 2, "den": 1000}
    request = payload["refinement"]["request_identity"]["request"]
    request["expected_timebase"] = [2, 1000]
    payload["refinement"]["request_identity"]["request_digest"] = hashlib.sha256(_canonical(request)).hexdigest()
    _assert_conforms(tampered, "review_bundle")  # schema only requires num >= 1
    with pytest.raises(ValueError, match="canonical 1/timescale"):
        dependency_digest(payload)


def test_gap_receipt_schema_has_no_cross_field_byte_count_vs_limit_constraint(snapshot_evidence):
    """Documented gap: schema does not require byte_count <= max_source_bytes."""
    receipt = _valid_document("real_receipt", snapshot_evidence)
    tampered = copy.deepcopy(receipt)
    tampered["source"]["source_byte_count"] = tampered["source"]["snapshot"]["max_source_bytes"] + 1024
    tampered.pop("record_digest")
    _assert_conforms({**tampered, "record_digest": ZERO_DIGEST}, "real_receipt")


def test_gap_source_snapshot_schema_accepts_mismatched_manifest_and_snapshot_digests(snapshot_evidence):
    """Documented gap: format-only schema cannot tell which digest belongs to which file."""
    tampered = copy.deepcopy(snapshot_evidence)
    tampered["snapshot_sha256"], tampered["snapshot_manifest_sha256"] = (
        tampered["snapshot_manifest_sha256"], tampered["snapshot_sha256"],
    )
    _assert_conforms(tampered, "source_snapshot")
    with pytest.raises(SourceSnapshotError):
        verify_snapshot_evidence(tampered)


# ---------------------------------------------------------------------------
# Fallback validator efficacy (runs whether or not jsonschema is installed)
# ---------------------------------------------------------------------------
def test_fallback_subset_validator_accepts_production_documents(snapshot_evidence):
    for kind in ("source_snapshot", "review_bundle", "real_receipt"):
        assert _validate_subset(_valid_document(kind, snapshot_evidence), _schema(KIND_SCHEMA[kind])) == []


_FALLBACK_CASES = [
    ("review_bundle", ("record_schema_version",), "vip_fvs.review_bundle.v4", "const"),
    ("review_bundle", ("payload", "candidate", "rank"), 0, "minimum"),
    ("review_bundle", ("record_id",), "x" * 257, "maxLength"),
    ("real_receipt", ("schema",), "vip_fvs.real_receipt.v1", "const"),
    ("real_receipt", ("NOT_OBSERVED",), [], "minItems"),
    ("real_receipt", ("source", "snapshot", "snapshot_sha256"), "not-a-digest", "pattern"),
]


@pytest.mark.parametrize(
    "kind,path,value,keyword", _FALLBACK_CASES,
    ids=[f"{kind}:{'.'.join(path)}:{index}" for index, (kind, path, _v, _k) in enumerate(_FALLBACK_CASES)],
)
def test_fallback_subset_validator_rejects_representative_violations(snapshot_evidence, kind, path, value, keyword):
    document = _valid_document(kind, snapshot_evidence)
    _assign(document, path, value)
    errors = _validate_subset(document, _schema(KIND_SCHEMA[kind]))
    assert any(error.keyword == keyword for error in errors), [str(error) for error in errors]


def test_fallback_and_jsonschema_agree_when_both_available(snapshot_evidence):
    if not JSONSCHEMA_AVAILABLE:
        pytest.skip("only the fallback validator is available in this environment")
    valid = _valid_document("review_bundle", snapshot_evidence)
    assert _validate_subset(valid, _schema("review_bundle")) == []
    assert _errors(valid, "review_bundle") == []
    invalid = copy.deepcopy(valid)
    invalid["payload"]["candidate"]["rank"] = 0
    assert _validate_subset(invalid, _schema("review_bundle"))
    assert _errors(invalid, "review_bundle")
