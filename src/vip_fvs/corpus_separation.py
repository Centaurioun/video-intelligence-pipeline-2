"""Bounded, metadata-only P1 verifier for explicitly synthetic evidence.

This module does not authorize real admission. A synthetic trust-policy double
is mandatory, and every successful result is marked ``SYNTHETIC_ONLY``.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any
from datetime import datetime

from gate0.identity import opaque_id
from gate0.split import relation_components

REF_VERSION = "vip_fvs.corpus_separation_ref.v1"
EVIDENCE_VERSION = "vip_fvs.corpus_separation_evidence.v1"
AUTH_VERSION = "vip_fvs.pilot_authorization.v2"
_REF_FIELDS = {"schema_version", "artifact_id", "artifact_schema_version", "canonical_content_sha256", "authorized_root_id", "issuer_policy_ref"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ATTESTATION_INPUT_KEYS = (
    "schema_version", "corpus_id", "corpus_role", "excluded_corpus_ids", "excluded_label_versions",
    "gate0_eval_manifest_digest", "gate0_dev_manifest_digest", "gate0_inventory_digest",
    "gate0_split_allocation_digest", "gate0_eval_relation_digest", "gate0_dev_relation_digest",
    "gate0_label_version_digest", "source_authority_refs", "candidate_source_sha256",
    "candidate_revision_id", "candidate_authorization_digest", "candidate_relation_manifest_digest",
)
_ATTESTATION_FIELDS = frozenset(_ATTESTATION_INPUT_KEYS) | frozenset({
    "candidate_relation_coverage", "digest_intersection", "relation_component_intersection",
    "byte_disjoint_status", "declared_relations_status", "authenticity_status",
    "transform_equivalence_status", "judgment_separation_status", "checked_at",
    "deterministic_input_digest", "attestation_digest",
})


class CorpusSeparationError(ValueError):
    """Fail-closed P1 refusal, with a stable code in the message."""


def _refuse(code: str) -> CorpusSeparationError:
    return CorpusSeparationError(f"CORPUS_SEPARATION_{code}")


def canonical_bytes(value: Any) -> bytes:
    """Repository canonical JSON: UTF-8, sorted keys, compact and finite."""
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise _refuse("DECLARATION_INVALID") from exc


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _refuse("DECLARATION_INVALID")
        result[key] = value
    return result


def parse_json(data: bytes | str) -> Any:
    try:
        text = data.decode("utf-8", errors="strict") if isinstance(data, bytes) else data
        value = json.loads(text, object_pairs_hook=_pairs_no_duplicates, parse_constant=lambda _x: (_ for _ in ()).throw(_refuse("DECLARATION_INVALID")))
    except CorpusSeparationError:
        raise
    except (UnicodeError, json.JSONDecodeError, TypeError) as exc:
        raise _refuse("DECLARATION_INVALID") from exc
    if canonical_bytes(value) != (data if isinstance(data, bytes) else data.encode("utf-8")):
        raise _refuse("DECLARATION_INVALID")
    return value


def _id(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 512


def _sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def parse_reference(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _REF_FIELDS:
        raise _refuse("DECLARATION_INVALID")
    result = dict(value)
    if result["schema_version"] != REF_VERSION or result["artifact_schema_version"] != EVIDENCE_VERSION:
        raise _refuse("DECLARATION_INVALID")
    if not all(_id(result[k]) for k in ("artifact_id", "authorized_root_id", "issuer_policy_ref")) or not _sha(result["canonical_content_sha256"]):
        raise _refuse("DECLARATION_INVALID")
    return result


def resolve_artifact(root: Path, relative_path: str, *, protected_roots: tuple[Path, ...] = ()) -> Path:
    """Resolve a regular metadata file below one preconfigured root; reject all symlink components."""
    base = Path(root)
    rel = Path(relative_path) if isinstance(relative_path, str) else Path(".")
    if not isinstance(relative_path, str) or not relative_path or rel.is_absolute() or any(part in {"..", ""} for part in rel.parts):
        raise _refuse("OUTPUT_PATH_INVALID")
    if base.is_symlink() or not base.is_dir():
        raise _refuse("OUTPUT_PATH_INVALID")
    current = base
    for part in rel.parts:
        current = current / part
        try:
            info = current.lstat()
        except OSError as exc:
            raise _refuse("EVIDENCE_INCOMPLETE") from exc
        if stat.S_ISLNK(info.st_mode):
            raise _refuse("OUTPUT_PATH_INVALID")
    if not stat.S_ISREG(current.lstat().st_mode):
        raise _refuse("OUTPUT_PATH_INVALID")
    try:
        if os.path.commonpath((str(base.resolve()), str(current.resolve()))) != str(base.resolve()):
            raise _refuse("OUTPUT_PATH_INVALID")
        candidate_identity = current.resolve()
        for protected in protected_roots:
            protected_path = Path(protected)
            protected_identity = protected_path.resolve()
            if os.path.commonpath((str(candidate_identity), str(protected_identity))) == str(protected_identity):
                raise _refuse("OUTPUT_PATH_INVALID")
    except (OSError, ValueError) as exc:
        raise _refuse("OUTPUT_PATH_INVALID") from exc
    return current


def _open_absolute_directory_no_symlinks(path: Path) -> tuple[int, Path]:
    """Bind a configured directory to a descriptor while rejecting symlink components."""
    absolute = Path(os.path.abspath(path))
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    current_fd = os.open(os.sep, directory_flags)
    try:
        for part in absolute.parts[1:]:
            next_fd = os.open(part, directory_flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        info = os.stat(absolute, follow_symlinks=False)
        opened = os.fstat(current_fd)
        if not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino) != (opened.st_dev, opened.st_ino):
            raise _refuse("OUTPUT_PATH_INVALID")
        result, current_fd = current_fd, -1
        return result, absolute
    finally:
        if current_fd >= 0:
            os.close(current_fd)


def _open_relative_metadata(root_fd: int, relative_path: str, protected_ids: set[tuple[int, int]]) -> int:
    """Open a regular file relative to the already checked root descriptor."""
    rel = Path(relative_path)
    if not relative_path or rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        raise _refuse("OUTPUT_PATH_INVALID")
    current_fd = os.dup(root_fd)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        if (os.fstat(current_fd).st_dev, os.fstat(current_fd).st_ino) in protected_ids:
            raise _refuse("OUTPUT_PATH_INVALID")
        for part in rel.parts[:-1]:
            next_fd = os.open(part, directory_flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
            info = os.fstat(current_fd)
            if (info.st_dev, info.st_ino) in protected_ids:
                raise _refuse("OUTPUT_PATH_INVALID")
        file_fd = os.open(rel.parts[-1], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0), dir_fd=current_fd)
        if not stat.S_ISREG(os.fstat(file_fd).st_mode):
            os.close(file_fd)
            raise _refuse("OUTPUT_PATH_INVALID")
        return file_fd
    finally:
        os.close(current_fd)


def load_referenced_metadata(reference: Mapping[str, Any], roots: Mapping[str, Path], relative_path: str, *, protected_roots: tuple[Path, ...]) -> tuple[Path, Any]:
    """Load canonical JSON metadata only from the configured root named by Option R."""
    ref = parse_reference(reference)
    if not protected_roots:
        raise _refuse("EVIDENCE_INCOMPLETE")
    root = roots.get(ref["authorized_root_id"])
    if root is None:
        raise _refuse("EVIDENCE_INCOMPLETE")
    root_fd = -1
    protected_fds: list[int] = []
    try:
        root_fd, root_real = _open_absolute_directory_no_symlinks(Path(root))
        protected_real: list[Path] = []
        protected_ids: set[tuple[int, int]] = set()
        for protected_root in protected_roots:
            protected_fd, protected_path = _open_absolute_directory_no_symlinks(Path(protected_root))
            protected_fds.append(protected_fd)
            protected_real.append(protected_path)
            info = os.fstat(protected_fd)
            protected_ids.add((info.st_dev, info.st_ino))
            if os.path.commonpath((str(root_real), str(protected_path))) == str(protected_path):
                raise _refuse("OUTPUT_PATH_INVALID")
        # Keep this metadata-only path check after opening the configured roots.
        # File bytes are then read relative to the same verified directory fd.
        path = resolve_artifact(root, relative_path, protected_roots=protected_roots)
        fd = _open_relative_metadata(root_fd, relative_path, protected_ids)
        with os.fdopen(fd, "rb") as stream:
            raw = stream.read(4 * 1024 * 1024 + 1)
    except OSError as exc:
        raise _refuse("EVIDENCE_INCOMPLETE") from exc
    finally:
        if root_fd >= 0:
            os.close(root_fd)
        for protected_fd in protected_fds:
            os.close(protected_fd)
    if len(raw) > 4 * 1024 * 1024:
        raise _refuse("EVIDENCE_INCOMPLETE")
    value = parse_json(raw)
    if hashlib.sha256(raw).hexdigest() != ref["canonical_content_sha256"]:
        raise _refuse("EVIDENCE_INCOMPLETE")
    if not isinstance(value, dict) or value.get("schema_version") != ref["artifact_schema_version"]:
        raise _refuse("EVIDENCE_INCOMPLETE")
    return path, value


def authorization_scope_digest(authorization: Mapping[str, Any]) -> str:
    """Cycle-free scope digest omitting record_digest and the evidence reference."""
    excluded = {"record_digest", "corpus_separation_ref"}
    projection = {key: value for key, value in authorization.items() if key not in excluded}
    return hashlib.sha256(canonical_bytes(projection)).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise _refuse(code)


def _attestation_digest(value: Mapping[str, Any]) -> str:
    body = dict(value)
    body.pop("attestation_digest", None)
    return _digest(body)


def validate_attestation(attestation: Mapping[str, Any]) -> None:
    if not isinstance(attestation, Mapping) or set(attestation) != _ATTESTATION_FIELDS or attestation.get("schema_version") != "vip_fvs.corpus_separation_attestation.v1":
        raise _refuse("ATTESTATION_DIGEST_MISMATCH")
    try:
        expected_digest = _attestation_digest(attestation)
    except CorpusSeparationError as exc:
        raise _refuse("ATTESTATION_DIGEST_MISMATCH") from exc
    if attestation.get("attestation_digest") != expected_digest:
        raise _refuse("ATTESTATION_DIGEST_MISMATCH")
    if not set(_ATTESTATION_INPUT_KEYS).issubset(attestation):
        raise _refuse("ATTESTATION_DIGEST_MISMATCH")
    projection = {key: attestation[key] for key in _ATTESTATION_INPUT_KEYS}
    coverage = attestation.get("candidate_relation_coverage")
    projection_keys = {"declared_universe_digest", "declared_node_count", "claimed_coverage_status", "method_ref"}
    coverage_keys = projection_keys | {"verified_coverage_status"}
    if not isinstance(coverage, Mapping) or set(coverage) != coverage_keys:
        raise _refuse("ATTESTATION_DIGEST_MISMATCH")
    if (not _sha(coverage.get("declared_universe_digest"))
            or isinstance(coverage.get("declared_node_count"), bool)
            or not isinstance(coverage.get("declared_node_count"), int)
            or coverage["declared_node_count"] < 0
            or coverage.get("claimed_coverage_status") != "COMPLETE"
            or not _id(coverage.get("method_ref"))
            or coverage.get("verified_coverage_status") != "VERIFIED_SYNTHETIC"):
        raise _refuse("ATTESTATION_DIGEST_MISMATCH")
    projection["candidate_relation_coverage"] = {key: coverage[key] for key in ("declared_universe_digest", "declared_node_count", "claimed_coverage_status", "method_ref")}
    if attestation.get("deterministic_input_digest") != _digest(projection):
        raise _refuse("ATTESTATION_DIGEST_MISMATCH")


def verify_synthetic(
    evidence: Mapping[str, Any], reference: Mapping[str, Any], *, authorization: Mapping[str, Any],
    checked_at: str, trust_policy: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Verify one complete synthetic fixture. Never emits real-admission authority."""
    ref = parse_reference(reference)
    if isinstance(authorization, Mapping) and authorization.get("schema_version") == AUTH_VERSION:
        try:
            authorization_ref = parse_reference(authorization.get("corpus_separation_ref"))
        except CorpusSeparationError as exc:
            raise _refuse("EVIDENCE_INCOMPLETE") from exc
        _require(authorization_ref == ref, "EVIDENCE_INCOMPLETE")
    else:
        raise _refuse("EVIDENCE_INCOMPLETE")
    _require(isinstance(evidence, Mapping) and evidence.get("schema_version") == EVIDENCE_VERSION, "EVIDENCE_INCOMPLETE")
    allowed_evidence_fields = {"schema_version", "artifact_id", "evidence_state", "issuer_policy_ref", "run_id", "corpus_id", "inventory", "relation_inventory", "split", "evaluation_membership", "development_membership", "label_version_refs", "policy_rights_refs", "candidate", "candidate_relation", "trust"}
    _require(set(evidence).issubset(allowed_evidence_fields), "DECLARATION_INVALID")
    _require(evidence.get("evidence_state") == "SYNTHETIC_ONLY", "EVIDENCE_INCOMPLETE")
    _require(evidence.get("artifact_id") == ref["artifact_id"], "EVIDENCE_INCOMPLETE")
    _require(ref["canonical_content_sha256"] == _digest(evidence), "EVIDENCE_INCOMPLETE")
    trust = evidence.get("trust")
    _require(isinstance(trust, Mapping) and set(trust).issubset({"issuer_ref", "acceptance_ref", "revocation_ref", "accepted", "revoked", "accepted_producer_ids", "evidence_state"}), "EVIDENCE_INCOMPLETE")
    _require(isinstance(trust, Mapping) and trust.get("evidence_state", "SYNTHETIC_ONLY") == "SYNTHETIC_ONLY"
             and _id(trust.get("issuer_ref")) and _id(trust.get("acceptance_ref")) and _id(trust.get("revocation_ref"))
             and trust.get("accepted") is True and trust.get("revoked") is False,
             "EVIDENCE_INCOMPLETE")
    _require(ref["issuer_policy_ref"] == evidence.get("issuer_policy_ref"), "EVIDENCE_INCOMPLETE")
    # This injectable is a synthetic test double seam, never a real trust anchor.
    try:
        decision = trust_policy(evidence, ref) if callable(trust_policy) else None
    except Exception as exc:
        raise _refuse("EVIDENCE_INCOMPLETE") from exc
    expected_decision = {
        "issuer_ref": trust.get("issuer_ref"), "issuer_policy_ref": ref["issuer_policy_ref"],
        "artifact_id": ref["artifact_id"], "canonical_content_sha256": ref["canonical_content_sha256"],
        "run_id": evidence.get("run_id"), "accepted_producer_ids": trust.get("accepted_producer_ids"),
        "acceptance_ref": trust.get("acceptance_ref"), "revocation_ref": trust.get("revocation_ref"),
        "accepted": True, "revoked": False, "evidence_state": "SYNTHETIC_ONLY",
    }
    _require(isinstance(decision, Mapping) and dict(decision) == expected_decision, "EVIDENCE_INCOMPLETE")
    _require(_id(evidence.get("run_id")) and _id(evidence.get("corpus_id")), "EVIDENCE_INCOMPLETE")
    try:
        observed_time = datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise _refuse("DECLARATION_INVALID") from exc
    _require(observed_time.tzinfo is not None and observed_time.utcoffset() is not None, "DECLARATION_INVALID")
    if "evaluation_membership" not in evidence or "development_membership" not in evidence or evidence.get("evaluation_membership") is None or evidence.get("development_membership") is None:
        raise _refuse("ATTESTATION_REQUIRED")
    if "candidate" not in evidence:
        raise _refuse("CANDIDATE_IDENTITY_REQUIRED")
    _require(set(evidence) == allowed_evidence_fields, "EVIDENCE_INCOMPLETE")
    accepted_producers = trust.get("accepted_producer_ids", ())
    _require(isinstance(accepted_producers, list) and accepted_producers and all(_id(x) for x in accepted_producers), "EVIDENCE_INCOMPLETE")
    def linked(child: Any) -> bool:
        return isinstance(child, Mapping) and child.get("run_id") == evidence["run_id"] and child.get("producer_id") in accepted_producers
    for key in ("inventory", "relation_inventory", "split", "evaluation_membership", "development_membership"):
        _require(linked(evidence.get(key)), "EVIDENCE_INCOMPLETE")
    _require(linked(evidence.get("candidate_relation")), "RELATION_COVERAGE_UNVERIFIED")
    for key in ("label_version_refs", "policy_rights_refs"):
        rows = evidence.get(key)
        if key == "label_version_refs" and not rows:
            continue
        _require(isinstance(rows, list) and rows and all(linked(row) for row in rows), "EVIDENCE_INCOMPLETE")
    candidate = evidence.get("candidate")
    _require(isinstance(candidate, Mapping), "CANDIDATE_IDENTITY_REQUIRED")
    _require(set(candidate).issubset({"revision_id", "source_sha256", "locator", "corpus_role"}) and {"revision_id", "source_sha256"}.issubset(candidate), "DECLARATION_INVALID")
    _require(all(isinstance(candidate[key], str) for key in ("locator", "corpus_role") if key in candidate), "DECLARATION_INVALID")
    _require(not any(key in candidate and not isinstance(candidate[key], str) for key in ("revision_id", "source_sha256")), "DECLARATION_INVALID")
    _require(_id(candidate.get("revision_id")), "CANDIDATE_IDENTITY_REQUIRED")
    if "corpus_role" in candidate:
        _require(candidate["corpus_role"] == "GATE3_PILOT_CANDIDATE", "DECLARATION_INVALID")
    _require(not any(not isinstance(candidate.get(key), str) for key in ("revision_id", "source_sha256") if key in candidate), "DECLARATION_INVALID")
    _require(_sha(candidate.get("source_sha256")), "DECLARATION_INVALID")
    _require(authorization.get("source_revision_id") == candidate["revision_id"] and authorization.get("source_sha256") == candidate["source_sha256"], "CANDIDATE_IDENTITY_REQUIRED")

    inventory_obj = evidence.get("inventory")
    _require(isinstance(inventory_obj, Mapping) and isinstance(inventory_obj.get("records"), list) and inventory_obj["records"], "EVIDENCE_INCOMPLETE")
    _require(set(inventory_obj) == {"records", "digest", "run_id", "producer_id"}, "DECLARATION_INVALID")
    inventory = inventory_obj["records"]
    _require(inventory_obj.get("digest") == _digest(inventory), "EVIDENCE_INCOMPLETE")
    ids: list[str] = []
    byte_digests: dict[str, str] = {}
    for row in inventory:
        _require(isinstance(row, Mapping) and set(row) == {"revision_id", "source_sha256", "status"} and _id(row.get("revision_id")) and _sha(row.get("source_sha256")) and row.get("status") in {"INCLUDED", "EXCLUDED", "NOT_OBSERVED"}, "EVIDENCE_INCOMPLETE")
        _require(row["revision_id"] not in byte_digests, "EVIDENCE_INCOMPLETE")
        byte_digests[row["revision_id"]] = row["source_sha256"]
        if row["status"] == "INCLUDED":
            ids.append(row["revision_id"])
    _require(ids and len(ids) == len(set(ids)), "EVIDENCE_INCOMPLETE")

    rel = evidence.get("relation_inventory")
    _require(isinstance(rel, Mapping) and isinstance(rel.get("nodes"), list) and isinstance(rel.get("edges"), list), "EVIDENCE_INCOMPLETE")
    _require(set(rel) == {"nodes", "edges", "digest", "run_id", "producer_id"}, "DECLARATION_INVALID")
    _require(all(_id(node) for node in rel["nodes"]) and len(rel["nodes"]) == len(set(rel["nodes"])), "EVIDENCE_INCOMPLETE")
    _require(all(isinstance(edge, list) and len(edge) == 2 and all(_id(node) for node in edge) for edge in rel["edges"]), "EVIDENCE_INCOMPLETE")
    _require(set(rel["nodes"]) == set(ids) and rel.get("digest") == _digest({"nodes": rel["nodes"], "edges": rel["edges"]}), "EVIDENCE_INCOMPLETE")
    try:
        components = relation_components(ids, [tuple(edge) for edge in rel["edges"]])
    except (ValueError, TypeError) as exc:
        raise _refuse("EVIDENCE_INCOMPLETE") from exc
    comp_id_for: dict[str, str] = {}
    for component in components:
        component_id = opaque_id("component", tuple(sorted(component)))
        for revision in component:
            comp_id_for[revision] = component_id
    split = evidence.get("split")
    _require(isinstance(split, Mapping) and split.get("relation_inventory_digest") == rel["digest"] and isinstance(split.get("allocations"), Mapping), "EVIDENCE_INCOMPLETE")
    _require(set(split) == {"allocations", "relation_inventory_digest", "run_id", "producer_id"}, "DECLARATION_INVALID")
    allocations = split["allocations"]
    _require(set(allocations) == {opaque_id("component", tuple(sorted(c))) for c in components}, "EVIDENCE_INCOMPLETE")
    role_ids = {"EVALUATION": set(), "DEVELOPMENT": set()}
    for revision, component_id in comp_id_for.items():
        role = allocations.get(component_id)
        _require(isinstance(role, str), "EVIDENCE_INCOMPLETE")
        _require(role in role_ids, "EVIDENCE_INCOMPLETE")
        role_ids[role].add(revision)
    _require(role_ids["EVALUATION"] and role_ids["DEVELOPMENT"] and role_ids["EVALUATION"].isdisjoint(role_ids["DEVELOPMENT"]), "EVIDENCE_INCOMPLETE")
    for role, key in (("EVALUATION", "evaluation_membership"), ("DEVELOPMENT", "development_membership")):
        if key not in evidence or evidence[key] is None:
            raise _refuse("ATTESTATION_REQUIRED")
        membership = evidence.get(key)
        _require(isinstance(membership, Mapping) and isinstance(membership.get("revision_ids"), list), "EVIDENCE_INCOMPLETE")
        _require(set(membership) == {"revision_ids", "count", "run_id", "producer_id"}, "DECLARATION_INVALID")
        values = membership["revision_ids"]
        _require(all(_id(value) for value in values), "EVIDENCE_INCOMPLETE")
        _require(len(values) == len(set(values)) and set(values) == role_ids[role]
                 and type(membership.get("count")) is int and membership["count"] == len(values), "EVIDENCE_INCOMPLETE")

    labels = evidence.get("label_version_refs")
    rights = evidence.get("policy_rights_refs")
    _require(not isinstance(labels, list) or all(isinstance(x, Mapping) and set(x) == {"artifact_id", "digest", "run_id", "producer_id"} for x in labels), "LABEL_VERSION_UNBOUND")
    _require(not isinstance(rights, list) or all(isinstance(x, Mapping) and set(x) == {"artifact_id", "status", "run_id", "producer_id"} for x in rights), "EVIDENCE_INCOMPLETE")
    _require(isinstance(labels, list) and labels and all(isinstance(x, Mapping) and _id(x.get("artifact_id")) and _sha(x.get("digest")) for x in labels), "LABEL_VERSION_UNBOUND")
    _require(isinstance(rights, list) and rights and all(isinstance(x, Mapping) and x.get("status") == "ALLOW" for x in rights), "EVIDENCE_INCOMPLETE")
    candidate_relation = evidence.get("candidate_relation")
    _require(isinstance(candidate_relation, Mapping) and candidate_relation.get("claimed_complete") is True and _id(candidate_relation.get("method_ref")), "RELATION_COVERAGE_UNVERIFIED")
    _require(set(candidate_relation) == {"nodes", "edges", "claimed_complete", "method_ref", "authorization_scope_digest", "run_id", "producer_id", "inventory_digest", "split_digest", "gate0_relation_digest"}, "RELATION_COVERAGE_UNVERIFIED")
    _require(candidate_relation.get("authorization_scope_digest") == authorization_scope_digest(authorization), "RELATION_COVERAGE_UNVERIFIED")
    _require(candidate_relation.get("inventory_digest") == inventory_obj["digest"]
             and candidate_relation.get("split_digest") == _digest(split)
             and candidate_relation.get("gate0_relation_digest") == rel["digest"], "RELATION_COVERAGE_UNVERIFIED")
    cr_nodes, cr_edges = candidate_relation.get("nodes"), candidate_relation.get("edges")
    _require(isinstance(cr_nodes, list) and isinstance(cr_edges, list), "RELATION_COVERAGE_UNVERIFIED")
    _require(all(_id(node) for node in cr_nodes) and len(cr_nodes) == len(set(cr_nodes)), "RELATION_COVERAGE_UNVERIFIED")
    _require(all(isinstance(edge, list) and len(edge) == 2 and all(_id(node) for node in edge) for edge in cr_edges), "RELATION_COVERAGE_UNVERIFIED")
    _require(set(cr_nodes).issuperset(set(ids) | {candidate["revision_id"]}), "RELATION_COVERAGE_UNVERIFIED")
    _require(all(set(edge).issubset(set(cr_nodes)) for edge in cr_edges), "RELATION_COVERAGE_UNVERIFIED")
    for row in inventory:
        if row["status"] == "INCLUDED" and row["source_sha256"] == candidate["source_sha256"]:
            raise _refuse("DIGEST_COLLISION")
    try:
        graph_components = relation_components(cr_nodes, [tuple(edge) for edge in cr_edges])
    except (ValueError, TypeError) as exc:
        raise _refuse("RELATION_COVERAGE_UNVERIFIED") from exc
    candidate_group = next(group for group in graph_components if candidate["revision_id"] in group)
    for group in graph_components:
        members = set(group)
        _require(not (members & role_ids["EVALUATION"] and members & role_ids["DEVELOPMENT"]), "GROUP_COLLISION")
    _require(not (set(candidate_group) & set(ids)), "GROUP_COLLISION")

    eval_membership, dev_membership = evidence["evaluation_membership"], evidence["development_membership"]
    eval_digest, dev_digest = _digest(eval_membership), _digest(dev_membership)
    auth_scope = authorization_scope_digest(authorization)
    coverage = {"declared_universe_digest": _digest(sorted(cr_nodes)), "declared_node_count": len(cr_nodes),
                "claimed_coverage_status": "COMPLETE", "method_ref": candidate_relation["method_ref"], "verified_coverage_status": "VERIFIED_SYNTHETIC"}
    values: dict[str, Any] = {
        "schema_version": "vip_fvs.corpus_separation_attestation.v1", "corpus_id": evidence["corpus_id"],
        "corpus_role": "GATE3_PILOT_CANDIDATE", "excluded_corpus_ids": ["GATE0_EVALUATION", "GATE0_DEVELOPMENT"],
        "excluded_label_versions": labels, "gate0_eval_manifest_digest": eval_digest, "gate0_dev_manifest_digest": dev_digest,
        "gate0_inventory_digest": inventory_obj["digest"], "gate0_split_allocation_digest": _digest(split),
        "gate0_eval_relation_digest": rel["digest"], "gate0_dev_relation_digest": rel["digest"],
        "gate0_label_version_digest": _digest(labels), "source_authority_refs": {"issuer_policy_ref": ref["issuer_policy_ref"], "rights": rights, "run_id": evidence["run_id"]},
        "candidate_source_sha256": candidate["source_sha256"], "candidate_revision_id": candidate["revision_id"],
        "candidate_authorization_digest": auth_scope, "candidate_relation_manifest_digest": _digest(candidate_relation),
        "candidate_relation_coverage": coverage, "digest_intersection": [], "relation_component_intersection": [],
        "byte_disjoint_status": "VERIFIED_DISJOINT_SYNTHETIC", "declared_relations_status": "VERIFIED_DISJOINT_SYNTHETIC",
        "authenticity_status": "SYNTHETIC_TRUST_DOUBLE_ONLY", "transform_equivalence_status": "NOT_OBSERVED",
        "judgment_separation_status": "NOT_OBSERVED", "checked_at": checked_at,
    }
    projection = {key: values[key] for key in _ATTESTATION_INPUT_KEYS}
    projection["candidate_relation_coverage"] = {key: coverage[key] for key in ("declared_universe_digest", "declared_node_count", "claimed_coverage_status", "method_ref")}
    values["deterministic_input_digest"] = _digest(projection)
    values["attestation_digest"] = _attestation_digest(values)
    validate_attestation(values)
    return values
