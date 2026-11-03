"""Immutable human editorial decisions for the local FVS review boundary.

This module records a decision against a sealed :class:`ReviewBundle`; it does
not mutate the bundle and deliberately does not construct or execute a plan.
The resulting artifact is an ``EDITORIAL_INFERENCE`` with explicit provenance
pins, suitable for a later real-plan stage.
"""
from __future__ import annotations

from dataclasses import dataclass
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from .review_bundle import ReviewBundle, load_review_bundle

RECORD_TYPE = "vip_fvs.human_decision"
SCHEMA_VERSION = "vip_fvs.human_decision.v1"
_FIELDS = {"record_id", "record_type", "record_schema_version", "record_digest", "payload"}
_PAYLOAD_FIELDS = {
    "decision_id", "bundle_record_digest", "bundle_dependency_digest", "principal_kind",
    "principal_ref", "refinement_id", "refinement_evidence_digest", "source_revision_id",
    "source_sha256", "target_plan_revision", "decision_class", "rationale", "disposition",
    "plan_action", "evidence_class", "requested_modification", "accepted_sub_interval_ref",
    "supersedes",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _digest_record(record: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical({k: record[k] for k in
                                      ("record_id", "record_type", "record_schema_version", "payload")})).hexdigest()


def _digest(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _closed(value: Mapping[str, Any], expected: set[str], name: str) -> None:
    if set(value) != expected:
        raise ValueError(f"{name} keys mismatch")


def _validate_payload(payload: Mapping[str, Any], *, reviewed_refinement_id: str | None = None) -> None:
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be an object")
    _closed(payload, _PAYLOAD_FIELDS, "payload")
    for field in ("decision_id", "principal_ref", "refinement_id", "source_revision_id"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    for field in ("bundle_record_digest", "bundle_dependency_digest", "refinement_evidence_digest", "source_sha256"):
        if not _digest(payload[field]):
            raise ValueError(f"{field} must be a SHA-256 hex digest")
    if payload["principal_kind"] != "human":
        raise ValueError("only a real human principal is admitted")
    if payload["principal_ref"].lower().startswith(("fixture:", "synthetic:", "model:", "tool:")):
        raise ValueError("principal_ref must identify a non-fixture human")
    revision = payload["target_plan_revision"]
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError("target_plan_revision must be a positive integer")
    decision_class = payload["decision_class"]
    if decision_class not in {"ACCEPT", "REJECT", "MODIFY"}:
        raise ValueError("decision_class must be ACCEPT, REJECT, or MODIFY")
    if not isinstance(payload["rationale"], str) or not payload["rationale"].strip():
        raise ValueError("an explicit editorial rationale is required")
    if payload["evidence_class"] != "EDITORIAL_INFERENCE":
        raise ValueError("human decision evidence class must be EDITORIAL_INFERENCE")
    if decision_class == "ACCEPT":
        if payload["disposition"] != "ACCEPTED_FOR_PLAN" or payload["plan_action"] != "BUILD_REAL_PLAN":
            raise ValueError("ACCEPT must request BUILD_REAL_PLAN")
        if payload["requested_modification"] is not None:
            raise ValueError("ACCEPT cannot include a modification request")
    elif decision_class == "REJECT":
        if payload["disposition"] != "REJECTED" or payload["plan_action"] != "NONE":
            raise ValueError("REJECT is planless")
        if payload["requested_modification"] is not None:
            raise ValueError("REJECT cannot include a modification request")
    else:
        if payload["disposition"] != "MODIFICATION_REQUESTED" or payload["plan_action"] != "NONE":
            raise ValueError("MODIFY is planless")
        if not isinstance(payload["requested_modification"], str) or not payload["requested_modification"].strip():
            raise ValueError("MODIFY requires a requested modification")
    accepted_ref = payload["accepted_sub_interval_ref"]
    if accepted_ref is not None and (
            not isinstance(accepted_ref, str) or not accepted_ref.strip()):
        raise ValueError("accepted_sub_interval_ref must be a non-empty string or null")
    if accepted_ref is not None and reviewed_refinement_id is not None and accepted_ref != reviewed_refinement_id:
        raise ValueError("accepted_sub_interval_ref must equal the reviewed refinement_id")
    if payload["supersedes"] is not None and not _digest(payload["supersedes"]):
        raise ValueError("supersedes must be a decision digest or null")


@dataclass(frozen=True)
class HumanDecisionArtifact:
    _payload: dict[str, Any]
    record_digest: str

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "HumanDecisionArtifact":
        if not isinstance(record, Mapping) or set(record) != _FIELDS:
            raise ValueError("record envelope has exactly five fields")
        if record["record_type"] != RECORD_TYPE or record["record_schema_version"] != SCHEMA_VERSION:
            raise ValueError("unexpected HumanDecisionArtifact record type or schema version")
        _validate_payload(record["payload"])
        expected = _digest_record(record)
        if record["record_digest"] != expected:
            raise ValueError("record digest mismatch")
        if record["record_id"] != record["payload"]["decision_id"]:
            raise ValueError("record_id must equal decision_id")
        return cls(copy.deepcopy(dict(record["payload"])), expected)

    @property
    def payload(self) -> dict[str, Any]:
        return copy.deepcopy(self._payload)

    def to_record(self) -> dict[str, Any]:
        return {"record_id": self._payload["decision_id"], "record_type": RECORD_TYPE,
                "record_schema_version": SCHEMA_VERSION, "record_digest": self.record_digest,
                "payload": self.payload}


def create_human_decision(*, bundle: ReviewBundle, decision_id: str, principal_kind: str,
                          principal_ref: str, decision_class: str, rationale: str,
                          target_plan_revision: int, requested_modification: str | None = None,
                          accepted_sub_interval_ref: str | None = None,
                          supersedes: str | None = None) -> HumanDecisionArtifact:
    if not isinstance(bundle, ReviewBundle):
        raise TypeError("bundle must be a ReviewBundle")
    if not bundle.current_e01_validated:
        raise ValueError("current E01 byte-authority revalidation is required before editorial authority")
    bp = bundle.payload
    payload = {
        "decision_id": decision_id, "bundle_record_digest": bundle.record_digest,
        "bundle_dependency_digest": bundle.dependency_digest, "principal_kind": principal_kind,
        "principal_ref": principal_ref, "refinement_id": bp["refinement"]["refinement_id"],
        "refinement_evidence_digest": bp["refinement"]["evidence_digest"],
        "source_revision_id": bp["source"]["source_revision_id"], "source_sha256": bp["source"]["source_sha256"],
        "target_plan_revision": target_plan_revision, "decision_class": decision_class,
        "rationale": rationale.strip() if isinstance(rationale, str) else rationale,
        "disposition": {"ACCEPT": "ACCEPTED_FOR_PLAN", "REJECT": "REJECTED", "MODIFY": "MODIFICATION_REQUESTED"}.get(decision_class),
        "plan_action": "BUILD_REAL_PLAN" if decision_class == "ACCEPT" else "NONE",
        "evidence_class": "EDITORIAL_INFERENCE", "requested_modification": requested_modification,
        "accepted_sub_interval_ref": accepted_sub_interval_ref, "supersedes": supersedes,
    }
    _validate_payload(payload, reviewed_refinement_id=bp["refinement"]["refinement_id"])
    record = {"record_id": decision_id, "record_type": RECORD_TYPE,
              "record_schema_version": SCHEMA_VERSION, "payload": payload}
    return HumanDecisionArtifact(payload, _digest_record(record))


def _same_lineage(left: HumanDecisionArtifact, right: HumanDecisionArtifact) -> bool:
    left_payload = left.payload
    right_payload = right.payload
    return all(left_payload[field] == right_payload[field] for field in (
        "bundle_record_digest", "bundle_dependency_digest", "refinement_id",
        "refinement_evidence_digest", "source_revision_id", "source_sha256",
    ))


def _resolve_superseded(decision: HumanDecisionArtifact, target: Path) -> HumanDecisionArtifact:
    superseded_digest = decision.payload["supersedes"]
    if superseded_digest is None:
        raise ValueError("new HumanDecisionArtifact requires an existing superseded decision")
    records: dict[str, HumanDecisionArtifact] = {}
    for candidate in target.parent.iterdir():
        if candidate == target or not candidate.is_file() or candidate.suffix != ".json":
            continue
        try:
            prior = load_human_decision(candidate)
        except (OSError, ValueError):
            continue
        records[prior.record_digest] = prior
        if prior.record_digest == superseded_digest:
            if not _same_lineage(decision, prior):
                raise ValueError("superseded decision is not from the same lineage")
    prior = records.get(superseded_digest)
    if prior is None:
        raise ValueError("supersedes must identify an existing superseded decision")
    if prior.payload["decision_class"] in {"REJECT", "MODIFY"}:
        raise ValueError("REJECT and MODIFY require a new review artifact before resume")
    if any(value.payload["supersedes"] == superseded_digest for value in records.values()):
        raise ValueError("decision lineage cannot fork")
    seen: set[str] = set()
    cursor: str | None = superseded_digest
    while cursor is not None:
        if cursor in seen:
            raise ValueError("decision lineage contains a cycle")
        seen.add(cursor)
        ancestor = records.get(cursor)
        cursor = ancestor.payload["supersedes"] if ancestor is not None else None
    return prior


def _check_existing_target(decision: HumanDecisionArtifact, target: Path) -> Path:
    existing = load_human_decision(target)
    if existing.record_digest == decision.record_digest:
        return target
    if decision.payload["supersedes"] != existing.record_digest:
        raise ValueError("changed HumanDecisionArtifact must explicitly supersede the existing decision")
    raise ValueError("sealed HumanDecisionArtifact already exists with a different digest")


def _check_new_root(decision: HumanDecisionArtifact, target: Path) -> None:
    for candidate in target.parent.iterdir():
        if candidate == target or not candidate.is_file() or candidate.suffix != ".json":
            continue
        try:
            prior = load_human_decision(candidate)
        except (OSError, ValueError):
            continue
        if _same_lineage(decision, prior) and prior.payload["supersedes"] is None:
            raise ValueError("decision lineage cannot start a second root")


def save_human_decision(decision: HumanDecisionArtifact, path: str | os.PathLike[str]) -> Path:
    if not isinstance(decision, HumanDecisionArtifact):
        raise TypeError("decision must be a HumanDecisionArtifact")
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return _check_existing_target(decision, target)
    # A distinct output path is an append-only artifact.  A supersession link
    # is meaningful only when it resolves to a sealed, same-lineage prior
    # decision in this artifact directory.
    if decision.payload["supersedes"] is not None:
        _resolve_superseded(decision, target)
    else:
        _check_new_root(decision, target)
    data = _canonical(decision.to_record()) + b"\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        try:
            # Hard-link publication is exclusive: it cannot overwrite a file
            # that another writer sealed between our existence check and
            # publication.
            os.link(temporary, target)
        except FileExistsError:
            return _check_existing_target(decision, target)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
        directory_fd = os.open(target.parent, os.O_RDONLY)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
    except BaseException:
        try: os.unlink(temporary)
        except FileNotFoundError: pass
        raise
    return target


def load_human_decision(path: str | os.PathLike[str], *, bundle_path: str | os.PathLike[str] | None = None) -> HumanDecisionArtifact:
    target = Path(path); raw = target.read_bytes()
    try: record = json.loads(raw[:-1].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid HumanDecisionArtifact JSON") from exc
    decision = HumanDecisionArtifact.from_record(record)
    if not raw.endswith(b"\n") or _canonical(record) + b"\n" != raw:
        raise ValueError("HumanDecisionArtifact is not canonical sealed JSON")
    if bundle_path is not None:
        bundle = load_review_bundle(bundle_path)
        p = decision.payload
        if p["bundle_record_digest"] != bundle.record_digest or p["bundle_dependency_digest"] != bundle.dependency_digest:
            raise ValueError("decision bundle pins do not match sealed ReviewBundle")
        if p["accepted_sub_interval_ref"] is not None and p["accepted_sub_interval_ref"] != bundle.payload["refinement"]["refinement_id"]:
            raise ValueError("accepted_sub_interval_ref must equal the reviewed refinement_id")
        if bundle.payload["review_status"] != "AWAITING_EDITORIAL_DECISION" or bundle.payload["decision"] is not None:
            raise ValueError("ReviewBundle is not awaiting an editorial decision")
    return decision


def resolve_human_decision_resume(bundle_path: str | os.PathLike[str],
                                  decision_paths: list[str | os.PathLike[str]] | tuple[str | os.PathLike[str], ...]) -> HumanDecisionArtifact | None:
    """Return the single append-only decision head for a currently valid bundle."""
    bundle = load_review_bundle(bundle_path)
    if not bundle.current_e01_validated:
        raise ValueError("current E01 byte-authority revalidation is required before editorial resume")
    decisions: dict[str, HumanDecisionArtifact] = {}
    for path in sorted((Path(item) for item in decision_paths), key=lambda item: str(item)):
        decision = load_human_decision(path, bundle_path=bundle_path)
        decisions[decision.record_digest] = decision
    children: dict[str, list[str]] = {}
    for digest, decision in decisions.items():
        parent = decision.payload["supersedes"]
        if parent is None:
            continue
        prior = decisions.get(parent)
        if prior is None:
            raise ValueError("decision lineage has a dangling supersedes reference")
        if not _same_lineage(decision, prior):
            raise ValueError("decision lineage crosses bundle/source/refinement")
        if prior.payload["decision_class"] in {"REJECT", "MODIFY"}:
            raise ValueError("REJECT and MODIFY require a new review artifact before resume")
        children.setdefault(parent, []).append(digest)
    if any(len(values) > 1 for values in children.values()):
        raise ValueError("decision lineage cannot fork")
    for start in decisions:
        seen: set[str] = set()
        cursor: str | None = start
        while cursor is not None:
            if cursor in seen:
                raise ValueError("decision lineage contains a cycle")
            seen.add(cursor)
            current = decisions.get(cursor)
            cursor = current.payload["supersedes"] if current is not None else None
    heads = [decision for digest, decision in decisions.items() if digest not in children]
    if len(heads) > 1:
        raise ValueError("decision artifacts contain multiple current lineage heads")
    return heads[0] if heads else None


__all__ = ["HumanDecisionArtifact", "create_human_decision", "save_human_decision", "load_human_decision", "resolve_human_decision_resume"]
