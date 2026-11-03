"""Immutable lifecycle receipt for the explicitly local REAL FVS boundary.

This receipt is intentionally separate from ``gate3.receipt``.  It records a
measured preparation/editorial hand-off (and, after an ACCEPT, a plan build),
but never claims rendering, export, Gate-3 verification, or production QC.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

SCHEMA_V1 = "vip_fvs.real_receipt.v1"
SCHEMA_V2 = "vip_fvs.real_receipt.v2"
SCHEMA = SCHEMA_V2
NOT_OBSERVED = [
    "editorial acceptance before resume",
    "rendering or export",
    "frame-accurate editorial suitability",
    "provider or cloud inference",
    "model download or model execution beyond the injected local runtime",
    "archive-wide quality or coverage",
]
_FIELDS = {"schema", "receipt_id", "run_id", "attempt_id", "status", "scope",
           "source", "authorization", "artifacts", "decision", "plan",
           "export_eligible", "network_allowed", "model_download_allowed",
           "NOT_OBSERVED", "refusal"}
_SOURCE_FIELDS = {"source_revision_id", "source_sha256", "source_byte_count",
                  "selected_stream_index", "timebase", "probe_artifact_ref",
                  "probe_digest"}
_SOURCE_V2_FIELDS = _SOURCE_FIELDS | {"source_locator", "snapshot"}
_AUTHORIZATION_FIELDS = {"discovery_policy_ref", "refinement_policy_ref",
                         "policy_digest", "scope_digest"}
_ARTIFACT_FIELDS = {"review_bundle_ref", "review_bundle_digest",
                    "review_bundle_dependency_digest", "probe_ref", "probe_digest",
                    "decision_ref", "decision_digest", "decision_class",
                    "disposition", "plan_ref", "plan_digest", "mapping_digest",
                    "placement_digest"}
_DECISION_FIELDS = {"decision_ref", "decision_digest", "decision_class", "disposition"}
_PLAN_FIELDS = {"plan_ref", "plan_digest", "mapping_digest", "placement_digest"}
_REFUSAL_FIELDS = {"reason_code", "message"}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def receipt_digest(record: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical({k: record[k] for k in _FIELDS})).hexdigest()


def _id(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _digest(value: Any, name: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(f"{name} must be a SHA-256 digest")


def _closed_mapping(value: Any, allowed: set[str], name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    if not allow_empty and set(value) != allowed:
        raise ValueError(f"{name} keys mismatch")
    if allow_empty and not set(value) <= allowed:
        raise ValueError(f"{name} contains unknown fields")


@dataclass(frozen=True)
class RealReceipt:
    record: dict[str, Any]
    record_digest: str

    @classmethod
    def create(cls, record: Mapping[str, Any]) -> "RealReceipt":
        value = dict(record)
        if set(value) != _FIELDS:
            raise ValueError("real receipt fields mismatch")
        if value["schema"] not in {SCHEMA_V1, SCHEMA_V2}:
            raise ValueError("unexpected real receipt schema")
        for key in ("receipt_id", "run_id", "attempt_id", "scope", "status"):
            _id(value[key], key)
        if value["scope"] != "REAL_LOCAL_ONLY":
            raise ValueError("real receipt scope required")
        if value["status"] not in {"PREPARED", "AWAITING_EDITORIAL_DECISION", "DECISION_RECORDED", "PLAN_BUILT", "REJECTED", "MODIFICATION_REQUESTED", "REFUSED"}:
            raise ValueError("invalid real receipt status")
        if value["export_eligible"] is not False or value["network_allowed"] is not False or value["model_download_allowed"] is not False:
            raise ValueError("real receipt must remain non-production and local-only")
        if not isinstance(value["NOT_OBSERVED"], list) or not value["NOT_OBSERVED"]:
            raise ValueError("NOT_OBSERVED must be explicit")
        source_fields = _SOURCE_V2_FIELDS if value["schema"] == SCHEMA_V2 else _SOURCE_FIELDS
        _closed_mapping(value["source"], source_fields, "source")
        auth = value["authorization"]
        _closed_mapping(auth, _AUTHORIZATION_FIELDS, "authorization")
        _closed_mapping(value["artifacts"], _ARTIFACT_FIELDS, "artifacts", allow_empty=True)
        source = value["source"]
        if not isinstance(source["source_byte_count"], int) or isinstance(source["source_byte_count"], bool) or source["source_byte_count"] < 0:
            raise ValueError("source.source_byte_count must be a non-negative integer")
        if not isinstance(source["selected_stream_index"], int) or isinstance(source["selected_stream_index"], bool) or source["selected_stream_index"] < 0:
            raise ValueError("source.selected_stream_index must be a non-negative integer")
        _closed_mapping(source["timebase"], {"num", "den"}, "source.timebase")
        for key in ("num", "den"):
            if not isinstance(source["timebase"][key], int) or isinstance(source["timebase"][key], bool) or source["timebase"][key] < 1:
                raise ValueError(f"source.timebase.{key} must be a positive integer")
        for key in ("probe_artifact_ref",):
            _id(source[key], f"source.{key}")
        if "source_sha256" in source:
            _digest(source["source_sha256"], "source.source_sha256")
        if value["schema"] == SCHEMA_V2:
            _id(source["source_locator"], "source.source_locator")
            from .source_snapshot import verify_snapshot_evidence
            verify_snapshot_evidence(source["snapshot"])
            if (source["snapshot"].get("source_locator") != source["source_locator"]
                    or source["snapshot"].get("snapshot_sha256") != source["source_sha256"]
                    or source["snapshot"].get("source_byte_count") != source["source_byte_count"]):
                raise ValueError("receipt snapshot identity does not match source")
        _digest(auth["policy_digest"], "authorization.policy_digest")
        _digest(auth["scope_digest"], "authorization.scope_digest")
        for key in ("discovery_policy_ref", "refinement_policy_ref"):
            _id(auth[key], f"authorization.{key}")
        for key in ("probe_digest",):
            _digest(source[key], f"source.{key}")
        for key in ("review_bundle_ref", "probe_ref"):
            if key in value["artifacts"]:
                _id(value["artifacts"][key], f"artifacts.{key}")
        for key in ("review_bundle_digest", "review_bundle_dependency_digest"):
            if key in value["artifacts"] and value["artifacts"][key] is not None:
                _digest(value["artifacts"][key], f"artifacts.{key}")
        if value["decision"] is not None:
            _closed_mapping(value["decision"], _DECISION_FIELDS, "decision")
            _id(value["decision"]["decision_ref"], "decision.decision_ref")
            _digest(value["decision"]["decision_digest"], "decision.decision_digest")
            if value["decision"]["decision_class"] not in {"ACCEPT", "REJECT", "MODIFY"}:
                raise ValueError("decision.decision_class is invalid")
            _id(value["decision"]["disposition"], "decision.disposition")
        if value["plan"] is not None:
            _closed_mapping(value["plan"], _PLAN_FIELDS, "plan")
            _id(value["plan"]["plan_ref"], "plan.plan_ref")
            for key in ("plan_digest", "mapping_digest", "placement_digest"):
                _digest(value["plan"][key], f"plan.{key}")
        if value["refusal"] is not None:
            _closed_mapping(value["refusal"], _REFUSAL_FIELDS, "refusal")
        # Gate-3 and synthetic orchestration claims have no place in this
        # lifecycle receipt, even when nested under an otherwise known object.
        forbidden = {"gate3_receipt", "synthetic", "synthetic_receipt",
                     "render", "rendered_output", "verification", "technical_qc",
                     "qc", "export", "production_eligible"}
        def reject_claims(item: Any, path: str = "receipt") -> None:
            if isinstance(item, Mapping):
                if forbidden.intersection(item):
                    raise ValueError(f"{path} contains non-REAL claim")
                for key, nested in item.items():
                    reject_claims(nested, f"{path}.{key}")
            elif isinstance(item, list):
                for index, nested in enumerate(item):
                    reject_claims(nested, f"{path}[{index}]")
        reject_claims(value)
        return cls(value, receipt_digest(value))

    def to_record(self) -> dict[str, Any]:
        return {**self.record, "record_digest": self.record_digest}


def build_preparation_receipt(result: Any, *, run_id: str, attempt_id: str,
                              authorization: Mapping[str, Any] | None = None) -> RealReceipt:
    bundle = result.bundle
    payload = bundle.payload
    source = payload["source"]
    return RealReceipt.create({
        "schema": SCHEMA, "receipt_id": f"receipt:{attempt_id}", "run_id": run_id,
        "attempt_id": attempt_id, "status": "AWAITING_EDITORIAL_DECISION",
        "scope": "REAL_LOCAL_ONLY", "source": dict(source),
        "authorization": dict(authorization or payload["authorization"]),
        "artifacts": {"review_bundle_ref": str(result.bundle_path),
                       "review_bundle_digest": bundle.record_digest,
                       "review_bundle_dependency_digest": bundle.dependency_digest,
                       "probe_ref": result.probe.probe_artifact_ref,
                       "probe_digest": result.probe.probe_digest},
        "decision": None, "plan": None, "export_eligible": False,
        "network_allowed": False, "model_download_allowed": False,
        "NOT_OBSERVED": list(NOT_OBSERVED), "refusal": None})


def build_decision_receipt(*, bundle: Any, decision: Any, run_id: str, attempt_id: str,
                           bundle_path: Path, decision_path: Path, plan: Any = None,
                           plan_path: Path | None = None) -> RealReceipt:
    dp = decision.payload
    status = {"ACCEPT": "PLAN_BUILT", "REJECT": "REJECTED", "MODIFY": "MODIFICATION_REQUESTED"}[dp["decision_class"]]
    pp = {"decision_ref": str(decision_path), "decision_digest": decision.record_digest,
          "decision_class": dp["decision_class"], "disposition": dp["disposition"]}
    plan_section = None
    artifacts = {"review_bundle_ref": str(bundle_path), "review_bundle_digest": bundle.record_digest,
                 "review_bundle_dependency_digest": bundle.dependency_digest, **pp}
    if plan is not None:
        plan_section = {"plan_ref": str(plan_path) if plan_path else None,
                        "plan_digest": plan.plan_digest, "mapping_digest": plan.mapping_digest,
                        "placement_digest": plan.placement_digest}
        artifacts.update(plan_section)
    receipt_schema = SCHEMA_V2 if "snapshot" in bundle.payload["source"] else SCHEMA_V1
    return RealReceipt.create({"schema": receipt_schema, "receipt_id": f"receipt:{attempt_id}",
        "run_id": run_id, "attempt_id": attempt_id, "status": status,
        "scope": "REAL_LOCAL_ONLY", "source": dict(bundle.payload["source"]),
        "authorization": dict(bundle.payload["authorization"]), "artifacts": artifacts,
        "decision": pp, "plan": plan_section, "export_eligible": False,
        "network_allowed": False, "model_download_allowed": False,
        "NOT_OBSERVED": list(NOT_OBSERVED), "refusal": None})


def save_real_receipt(receipt: RealReceipt, path: str | os.PathLike[str]) -> Path:
    if not isinstance(receipt, RealReceipt):
        raise TypeError("receipt must be RealReceipt")
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    data = _canonical(receipt.to_record()) + b"\n"
    if target.exists():
        existing = load_real_receipt(target)
        if existing.record_digest == receipt.record_digest:
            return target
        raise ValueError("sealed real receipt differs")
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    with os.fdopen(fd, "wb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    try:
        os.link(temporary, target)
    except FileExistsError:
        existing = load_real_receipt(target)
        if existing.record_digest != receipt.record_digest:
            raise ValueError("sealed real receipt differs")
    finally:
        try: os.unlink(temporary)
        except FileNotFoundError: pass
    return target


def load_real_receipt(path: str | os.PathLike[str]) -> RealReceipt:
    raw = Path(path).read_bytes()
    if not raw.endswith(b"\n"):
        raise ValueError("real receipt is not canonical sealed JSON")
    record = json.loads(raw[:-1].decode("utf-8"))
    supplied = record.pop("record_digest", None)
    receipt = RealReceipt.create(record)
    if supplied != receipt.record_digest or _canonical({**record, "record_digest": supplied}) + b"\n" != raw:
        raise ValueError("real receipt digest or canonical encoding mismatch")
    return receipt


__all__ = ["RealReceipt", "build_preparation_receipt", "build_decision_receipt", "save_real_receipt", "load_real_receipt", "NOT_OBSERVED"]
