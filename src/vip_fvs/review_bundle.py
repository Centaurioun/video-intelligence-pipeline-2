"""Immutable, local-only ReviewBundle records for the real-source FVS.

The bundle is deliberately a small record-envelope boundary.  It contains no
editorial decision and no execution side effect; once published it is sealed
and can only be read back or replaced by a new bundle identity.
"""
from __future__ import annotations

from dataclasses import dataclass
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping
import re


RECORD_TYPE = "vip_fvs.review_bundle"
V1_SCHEMA_VERSION = "vip_fvs.review_bundle.v1"
V2_SCHEMA_VERSION = "vip_fvs.review_bundle.v2"
V3_SCHEMA_VERSION = "vip_fvs.review_bundle.v3"
SCHEMA_VERSION = V3_SCHEMA_VERSION
_RECORD_FIELDS = {"record_id", "record_type", "record_schema_version", "record_digest", "payload"}
_DIGEST = lambda value: hashlib.sha256(value).hexdigest()
_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _id(value: Any, name: str) -> None:
    if not isinstance(value, str) or not 1 <= len(value) <= 256:
        raise ValueError(f"{name} must be a non-empty string of at most 256 characters")


def _digest(value: Any, name: str) -> None:
    if not isinstance(value, str) or _HEX_DIGEST.fullmatch(value) is None:
        raise ValueError(f"{name} must be a SHA-256 hex digest")


def _integer(value: Any, name: str, *, minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def _number(value: Any, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")


def _object(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _timebase(value: Any, name: str) -> None:
    value = _object(value, name)
    _require_keys(value, {"num", "den"}, name)
    _integer(value["num"], f"{name}.num", minimum=1)
    _integer(value["den"], f"{name}.den", minimum=1)


def _interval(value: Any, name: str, *, pts: bool) -> None:
    value = _object(value, name)
    _require_keys(value, {"start", "end", "time_domain", "endpoint_semantics"}, name)
    if pts:
        _integer(value["start"], f"{name}.start")
        _integer(value["end"], f"{name}.end", minimum=1)
        if value["time_domain"] != "source_pts":
            raise ValueError(f"{name}.time_domain must be source_pts")
    else:
        _number(value["start"], f"{name}.start")
        _number(value["end"], f"{name}.end")
        if value["time_domain"] != "semantic_seconds":
            raise ValueError(f"{name}.time_domain must be semantic_seconds")
    if value["endpoint_semantics"] != "half_open":
        raise ValueError(f"{name}.endpoint_semantics must be half_open")


def _canonical(value: Any) -> bytes:
    """Return deterministic JSON bytes and reject non-finite values."""
    def check(item: Any, path: str = "$") -> Any:
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError(f"non-finite number at {path}")
        if isinstance(item, Mapping):
            if any(not isinstance(k, str) for k in item):
                raise ValueError(f"object keys must be strings at {path}")
            return {k: check(v, f"{path}.{k}") for k, v in item.items()}
        if isinstance(item, (list, tuple)):
            return [check(v, f"{path}[{i}]") for i, v in enumerate(item)]
        return item
    return json.dumps(check(value), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(value: Any) -> str:
    return _DIGEST(_canonical(value))


def _require_keys(value: Mapping[str, Any], required: set[str], name: str) -> None:
    if set(value) != required:
        missing = sorted(required - set(value)); extra = sorted(set(value) - required)
        raise ValueError(f"{name} keys mismatch (missing={missing}, extra={extra})")


def _validate_payload(payload: Mapping[str, Any], *, version: str = V1_SCHEMA_VERSION) -> None:
    keys = {"bundle_id", "run_id", "created_at", "review_status", "source", "authorization",
            "query", "generation", "candidate", "refinement", "presentation", "dependency_digest", "decision"}
    _require_keys(payload, keys, "payload")
    if payload["review_status"] != "AWAITING_EDITORIAL_DECISION" or payload["decision"] is not None:
        raise ValueError("ReviewBundle must await an editorial decision and have null decision")
    _id(payload["bundle_id"], "bundle_id")
    _id(payload["run_id"], "run_id")
    if not isinstance(payload["created_at"], str) or not payload["created_at"]:
        raise ValueError("created_at must be a non-empty string")
    _digest(payload["dependency_digest"], "dependency_digest")
    for key in ("source", "authorization", "query", "generation", "candidate", "refinement", "presentation"):
        if not isinstance(payload[key], Mapping):
            raise ValueError(f"{key} must be an object")
    # Keep the schema closed even when jsonschema is not installed in the tiny
    # runtime used for this package.  Nested values are checked by the checked-in
    # schema's exact key sets and the invariants below.
    expected = {
        "source": {"source_revision_id", "source_sha256", "source_byte_count", "selected_stream_index", "timebase", "probe_artifact_ref", "probe_digest"},
        "authorization": {"discovery_policy_ref", "refinement_policy_ref", "policy_digest", "scope_digest"},
        "query": {"query_id", "text", "digest"},
        "generation": {"attempt_id", "generation_id", "semantic_space_id", "model_identity", "model_revision", "weights_digest", "processor_digest", "index_ref", "index_digest", "input_digest"},
        "candidate": {"candidate_id", "rank", "score", "evidence_class", "binding_eligible", "assertion_digest", "semantic_interval"},
        "refinement": {"refinement_id", "status", "source_revision_id", "selected_stream_index", "source_pts_interval", "timebase", "attempt_id", "evidence_artifact_ref", "evidence_digest", "evidence_class"},
        "presentation": {"display_only", "start_seconds", "end_seconds"},
    }
    if version in {V2_SCHEMA_VERSION, V3_SCHEMA_VERSION}:
        expected["refinement"] = expected["refinement"] | {"request_identity"}
    if version == V3_SCHEMA_VERSION:
        expected["source"] = expected["source"] | {"source_locator", "snapshot"}
    elif version not in {V1_SCHEMA_VERSION, V2_SCHEMA_VERSION, V3_SCHEMA_VERSION}:
        raise ValueError("unsupported ReviewBundle schema version")
    for name, required in expected.items():
        _require_keys(payload[name], required, name)
    source = payload["source"]
    _id(source["source_revision_id"], "source.source_revision_id")
    _digest(source["source_sha256"], "source.source_sha256")
    if version == V3_SCHEMA_VERSION:
        _id(source["source_locator"], "source.source_locator")
        from .source_snapshot import verify_snapshot_evidence
        verify_snapshot_evidence(source["snapshot"])
        if (source["snapshot"].get("source_locator") != source["source_locator"]
                or source["snapshot"].get("snapshot_sha256") != source["source_sha256"]
                or source["snapshot"].get("source_byte_count") != source["source_byte_count"]):
            raise ValueError("source snapshot identity does not match source")
    _integer(source["source_byte_count"], "source.source_byte_count")
    _integer(source["selected_stream_index"], "source.selected_stream_index")
    _timebase(source["timebase"], "source.timebase")
    _id(source["probe_artifact_ref"], "source.probe_artifact_ref")
    _digest(source["probe_digest"], "source.probe_digest")

    auth = payload["authorization"]
    _id(auth["discovery_policy_ref"], "authorization.discovery_policy_ref")
    _id(auth["refinement_policy_ref"], "authorization.refinement_policy_ref")
    _digest(auth["policy_digest"], "authorization.policy_digest")
    _digest(auth["scope_digest"], "authorization.scope_digest")

    query = payload["query"]
    _id(query["query_id"], "query.query_id")
    if not isinstance(query["text"], str) or not query["text"]:
        raise ValueError("query.text must be a non-empty string")
    _digest(query["digest"], "query.digest")

    generation = payload["generation"]
    for key in ("attempt_id", "generation_id", "semantic_space_id", "model_identity", "model_revision", "index_ref"):
        _id(generation[key], f"generation.{key}")
    for key in ("weights_digest", "processor_digest", "index_digest", "input_digest"):
        _digest(generation[key], f"generation.{key}")

    candidate = payload["candidate"]
    _id(candidate["candidate_id"], "candidate.candidate_id")
    _integer(candidate["rank"], "candidate.rank", minimum=1)
    _number(candidate["score"], "candidate.score")
    _digest(candidate["assertion_digest"], "candidate.assertion_digest")
    _interval(candidate["semantic_interval"], "candidate.semantic_interval", pts=False)

    refinement = payload["refinement"]
    _id(refinement["refinement_id"], "refinement.refinement_id")
    _id(refinement["source_revision_id"], "refinement.source_revision_id")
    _integer(refinement["selected_stream_index"], "refinement.selected_stream_index")
    _interval(refinement["source_pts_interval"], "refinement.source_pts_interval", pts=True)
    _timebase(refinement["timebase"], "refinement.timebase")
    _id(refinement["attempt_id"], "refinement.attempt_id")
    _id(refinement["evidence_artifact_ref"], "refinement.evidence_artifact_ref")
    _digest(refinement["evidence_digest"], "refinement.evidence_digest")
    if version in {V2_SCHEMA_VERSION, V3_SCHEMA_VERSION}:
        _validate_request_identity(refinement["request_identity"], payload)

    presentation = payload["presentation"]
    _number(presentation["start_seconds"], "presentation.start_seconds")
    _number(presentation["end_seconds"], "presentation.end_seconds")
    if payload["candidate"]["evidence_class"] != "MATCHED" or payload["candidate"]["binding_eligible"] is not False:
        raise ValueError("candidate must remain non-binding MATCHED evidence")
    if payload["refinement"]["status"] != "MEASURED" or payload["refinement"]["evidence_class"] != "MEASURED":
        raise ValueError("refinement must be MEASURED")
    if payload["presentation"]["display_only"] is not True:
        raise ValueError("presentation is display-only")
    if (refinement["source_revision_id"] != source["source_revision_id"] or
            refinement["selected_stream_index"] != source["selected_stream_index"] or
            refinement["timebase"] != source["timebase"] or
            refinement["attempt_id"] != generation["attempt_id"]):
        raise ValueError("refinement source identity must match source and generation")
    _validate_finite(payload)


def _validate_request_identity(identity: Any, payload: Mapping[str, Any]) -> None:
    fields = {"request_id", "candidate_assertion_ref", "producer_attempt_id", "idempotency_key", "request_digest", "request"}
    if not isinstance(identity, Mapping):
        raise ValueError("refinement.request_identity must be an object")
    _require_keys(identity, fields, "refinement.request_identity")
    for field in fields - {"request"}:
        _id(identity[field], f"refinement.request_identity.{field}")
    _digest(identity["request_digest"], "refinement.request_identity.request_digest")
    request = identity["request"]
    request_fields = {"request_id", "candidate_assertion_ref", "source_revision_id", "source_locator", "expected_source_sha256",
                      "selected_stream_index", "requested_start_pts", "requested_end_pts", "producer_attempt_id", "idempotency_key", "expected_timebase"}
    if not isinstance(request, Mapping):
        raise ValueError("refinement.request_identity.request must be an object")
    _require_keys(request, request_fields, "refinement.request_identity.request")
    for field in ("request_id", "candidate_assertion_ref", "source_revision_id", "source_locator", "producer_attempt_id", "idempotency_key"):
        _id(request[field], f"refinement.request_identity.request.{field}")
    _digest(request["expected_source_sha256"], "refinement.request_identity.request.expected_source_sha256")
    _integer(request["selected_stream_index"], "refinement.request_identity.request.selected_stream_index")
    _integer(request["requested_start_pts"], "refinement.request_identity.request.requested_start_pts")
    _integer(request["requested_end_pts"], "refinement.request_identity.request.requested_end_pts", minimum=1)
    if request["requested_end_pts"] <= request["requested_start_pts"]:
        raise ValueError("request interval must be non-degenerate")
    expected_timebase = request["expected_timebase"]
    if expected_timebase is not None:
        if not isinstance(expected_timebase, (list, tuple)) or len(expected_timebase) != 2:
            raise ValueError("expected_timebase must be null or a two-integer pair")
        for index, part in enumerate(expected_timebase):
            _integer(part, f"expected_timebase[{index}]", minimum=1)
    if any(identity[key] != request[key] for key in ("request_id", "candidate_assertion_ref", "producer_attempt_id", "idempotency_key")):
        raise ValueError("request identity fields do not match nested request")
    if hashlib.sha256(_canonical(dict(request))).hexdigest() != identity["request_digest"]:
        raise ValueError("request identity digest mismatch")
    source, refinement = payload["source"], payload["refinement"]
    if (request["source_revision_id"] != source["source_revision_id"] or
            request["expected_source_sha256"] != source["source_sha256"] or
            request["selected_stream_index"] != source["selected_stream_index"] or
            request["requested_start_pts"] != refinement["source_pts_interval"]["start"] or
            request["requested_end_pts"] != refinement["source_pts_interval"]["end"] or
            request["producer_attempt_id"] != refinement["attempt_id"]):
        raise ValueError("request identity does not match bundle source/refinement")
    if "snapshot" in source and request["source_locator"] != source["snapshot"]["snapshot_path"]:
        raise ValueError("request identity must name verified snapshot path")
    if (source["timebase"].get("num") != 1 or refinement["timebase"].get("num") != 1 or
            source["timebase"] != refinement["timebase"]):
        raise ValueError("v2 source and refinement timebases must be equal canonical 1/timescale pairs")
    if expected_timebase is not None and list(expected_timebase) != [1, source["timebase"]["den"]]:
        raise ValueError("request timebase must use the byte-measured canonical rational")


def _validate_finite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite numeric value")
    if isinstance(value, Mapping):
        for item in value.values(): _validate_finite(item)
    elif isinstance(value, (list, tuple)):
        for item in value: _validate_finite(item)


def _dependency_projection(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Project only identities that can change the reviewed source/refinement."""
    source = payload["source"]
    auth = payload["authorization"]
    query = payload["query"]
    generation = payload["generation"]
    candidate = payload["candidate"]
    refinement = payload["refinement"]
    projection = {
        "source": {k: source[k] for k in ("source_revision_id", "source_sha256", "source_byte_count", "selected_stream_index", "timebase", "probe_digest")},
        "authorization": {k: auth[k] for k in ("policy_digest", "scope_digest")},
        "query": {"query_id": query["query_id"], "digest": query["digest"]},
        "generation": {k: generation[k] for k in ("attempt_id", "generation_id", "semantic_space_id", "model_identity", "model_revision", "weights_digest", "processor_digest", "index_digest", "input_digest")},
        "candidate": {k: candidate[k] for k in ("candidate_id", "rank", "score", "evidence_class", "binding_eligible", "assertion_digest", "semantic_interval")},
        "refinement": {k: refinement[k] for k in ("refinement_id", "status", "source_revision_id", "selected_stream_index", "source_pts_interval", "timebase", "attempt_id", "evidence_digest", "evidence_class")},
    }
    if "snapshot" in source:
        projection["source"]["source_locator"] = source["source_locator"]
        projection["source"]["snapshot"] = copy.deepcopy(source["snapshot"])
    if "request_identity" in refinement:
        projection["refinement"]["request_identity"] = copy.deepcopy(refinement["request_identity"])
    return projection


def dependency_digest(payload: Mapping[str, Any]) -> str:
    """Return the digest of the load-bearing dependency projection."""
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be an object")
    inferred_version = V3_SCHEMA_VERSION if "snapshot" in payload.get("source", {}) else V2_SCHEMA_VERSION if "request_identity" in payload.get("refinement", {}) else V1_SCHEMA_VERSION
    _validate_payload(payload, version=inferred_version)
    return _sha(_dependency_projection(payload))


def record_digest(record: Mapping[str, Any]) -> str:
    """Return the canonical envelope digest with only ``record_digest`` omitted."""
    if not isinstance(record, Mapping) or set(record) != _RECORD_FIELDS:
        raise ValueError("record envelope has exactly five fields")
    return _sha({key: record[key] for key in ("record_id", "record_type", "record_schema_version", "payload")})


def _validate_record_envelope(record: Mapping[str, Any]) -> None:
    if not isinstance(record, Mapping) or set(record) != _RECORD_FIELDS:
        raise ValueError("record envelope has exactly five fields")
    _id(record["record_id"], "record_id")
    if record["record_type"] != RECORD_TYPE or record["record_schema_version"] not in {V1_SCHEMA_VERSION, V2_SCHEMA_VERSION, V3_SCHEMA_VERSION}:
        raise ValueError("unexpected ReviewBundle record type or schema version")
    _digest(record["record_digest"], "record_digest")
    if not isinstance(record["payload"], Mapping):
        raise ValueError("payload must be an object")
    _validate_payload(record["payload"], version=record["record_schema_version"])


def _resolve_artifact_identity(payload: Mapping[str, Any]) -> dict[str, Any]:
    refinement = payload["refinement"]
    path = Path(refinement["evidence_artifact_ref"])
    try:
        raw = path.read_bytes()
        artifact = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("persisted refinement artifact is unavailable or invalid") from exc
    if not isinstance(artifact, Mapping):
        raise ValueError("persisted refinement artifact must be an object")
    canonical_artifact = _canonical(artifact)
    if raw not in {canonical_artifact, canonical_artifact + b"\n"}:
        raise ValueError("persisted refinement artifact is not canonical JSON")
    if artifact.get("evidence_digest") != refinement["evidence_digest"]:
        raise ValueError("persisted refinement evidence digest does not match bundle")
    from gate3 import authority
    from gate3.refinement import is_binding_eligible
    try:
        if authority.assert_evidence_digest(authority.RECORD_KIND_REFINEMENT, artifact) != refinement["evidence_digest"]:
            raise ValueError("persisted refinement evidence digest is invalid")
        if not is_binding_eligible(artifact):
            raise ValueError("persisted refinement is not currently byte-authoritative")
    except Exception as exc:
        raise ValueError("persisted refinement failed current E01 revalidation") from exc
    binding = next((entry for entry in artifact.get("validation_results", ())
                    if isinstance(entry, Mapping) and entry.get("check") == "C2_named_byte_binding"), None)
    if "snapshot" in payload["source"]:
        byte_authority = binding.get("byte_authority") if isinstance(binding, Mapping) else None
        if (not isinstance(byte_authority, Mapping)
                or byte_authority.get("snapshot_evidence") != payload["source"]["snapshot"]):
            raise ValueError("persisted refinement snapshot identity does not match bundle")
    identity = binding.get("request_identity") if isinstance(binding, Mapping) else None
    _validate_request_identity(identity, payload)
    interval = refinement["source_pts_interval"]
    if (artifact.get("refinement_id") != refinement["refinement_id"] or
            artifact.get("attempt_id") != refinement["attempt_id"] or
            artifact.get("source_revision_id") != refinement["source_revision_id"] or
            artifact.get("source_content_digest") != payload["source"]["source_sha256"] or
            artifact.get("stream_index") != refinement["selected_stream_index"] or
            artifact.get("time_domain") != "source_pts" or
            artifact.get("start_ticks") != interval["start"] or artifact.get("end_ticks") != interval["end"] or
            artifact.get("time_base") != refinement["timebase"]):
        raise ValueError("persisted refinement identity does not match bundle")
    return copy.deepcopy(dict(identity))


@dataclass(frozen=True)
class ReviewBundle:
    _payload: dict[str, Any]
    record_digest: str
    _version: str = V1_SCHEMA_VERSION
    _current_e01_validated: bool = False

    @classmethod
    def create(cls, payload: Mapping[str, Any], *, run_id: str, bundle_id: str, created_at: str) -> "ReviewBundle":
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be an object")
        value = copy.deepcopy(dict(payload))
        value.update({"run_id": run_id, "bundle_id": bundle_id, "created_at": created_at})
        artifact_path = Path(value["refinement"]["evidence_artifact_ref"])
        if not artifact_path.exists():
            raise ValueError("new ReviewBundle requires a persisted E01 refinement artifact")
        resolved_identity = _resolve_artifact_identity(value)
        if "request_identity" in value["refinement"] and value["refinement"]["request_identity"] != resolved_identity:
            raise ValueError("caller-supplied request identity does not match persisted artifact")
        value["refinement"]["request_identity"] = resolved_identity
        version = V3_SCHEMA_VERSION if "snapshot" in value.get("source", {}) else V2_SCHEMA_VERSION
        _validate_payload(value, version=version)
        dependency = dependency_digest(value)
        if value["dependency_digest"] not in {dependency, "0" * 64}:
            raise ValueError("dependency_digest does not match payload dependencies")
        value["dependency_digest"] = dependency
        record = {"record_id": bundle_id, "record_type": RECORD_TYPE,
                  "record_schema_version": version, "payload": value}
        digest = record_digest({**record, "record_digest": ""})
        return cls(value, digest, version, version in {V2_SCHEMA_VERSION, V3_SCHEMA_VERSION})

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "ReviewBundle":
        _validate_record_envelope(record)
        expected = record_digest(record)
        if record["record_digest"] != expected:
            raise ValueError("record digest mismatch")
        if record["record_id"] != record["payload"]["bundle_id"]:
            raise ValueError("record_id must equal payload bundle_id")
        dependency = dependency_digest(record["payload"])
        if record["payload"]["dependency_digest"] != dependency:
            raise ValueError("dependency digest mismatch")
        payload = copy.deepcopy(dict(record["payload"]))
        version = record["record_schema_version"]
        validated = False
        try:
            _resolve_artifact_identity(payload)
            validated = True
        except (OSError, ValueError, TypeError, KeyError):
            validated = False
        return cls(payload, expected, version, validated)

    @property
    def dependency_digest(self) -> str:
        return self._payload["dependency_digest"]

    @property
    def current_e01_validated(self) -> bool:
        return self._current_e01_validated

    @property
    def payload(self) -> dict[str, Any]:
        return copy.deepcopy(self._payload)

    def to_record(self) -> dict[str, Any]:
        return {"record_id": self._payload["bundle_id"], "record_type": RECORD_TYPE,
                "record_schema_version": self._version, "record_digest": self.record_digest,
                "payload": self.payload}


def save_review_bundle(bundle: ReviewBundle, path: str | os.PathLike[str]) -> Path:
    if not isinstance(bundle, ReviewBundle):
        raise TypeError("bundle must be a ReviewBundle")
    if bundle._version not in {V2_SCHEMA_VERSION, V3_SCHEMA_VERSION}:
        raise ValueError("historical v1 ReviewBundle is immutable and cannot be republished")
    identity = _resolve_artifact_identity(bundle.payload)
    if identity != bundle.payload["refinement"].get("request_identity"):
        raise ValueError("persisted refinement request identity changed before publication")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = _canonical(bundle.to_record()) + b"\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        try:
            # A hard link is an atomic, OS-level exclusive publication of the
            # already-fsynced temporary inode.  Unlike check-then-replace, a
            # concurrent publisher cannot clobber the first sealed bundle.
            os.link(temp_name, target)
        except FileExistsError:
            existing = load_review_bundle(target)
            if existing.record_digest == bundle.record_digest:
                return target
            raise ValueError("sealed ReviewBundle already exists with a different digest")
        finally:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
        directory_fd = os.open(target.parent, os.O_RDONLY)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
    except BaseException:
        try: os.unlink(temp_name)
        except FileNotFoundError: pass
        raise
    return target


def load_review_bundle(path: str | os.PathLike[str]) -> ReviewBundle:
    target = Path(path)
    raw = target.read_bytes()
    try: record = json.loads(raw[:-1].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        # A common tamper mode is a normal JSON rewrite without the canonical
        # trailing LF.  Parse it when possible so the digest mismatch remains
        # the useful failure reported to callers.
        try: record = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("invalid ReviewBundle JSON") from exc
    bundle = ReviewBundle.from_record(record)
    if not raw.endswith(b"\n") or raw[:-1].find(b"\n") >= 0:
        raise ValueError("ReviewBundle is not canonical sealed JSON")
    if _canonical(record) + b"\n" != raw:
        raise ValueError("ReviewBundle is not canonical sealed JSON")
    return bundle


def find_sealed_bundle(directory: str | os.PathLike[str], dependency_digest: str) -> ReviewBundle | None:
    root = Path(directory)
    if not isinstance(dependency_digest, str) or len(dependency_digest) != 64:
        return None
    for path in sorted(root.glob("*.json")):
        try:
            bundle = load_review_bundle(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if bundle.dependency_digest == dependency_digest:
            return bundle
    return None
