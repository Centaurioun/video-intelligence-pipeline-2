"""Digest-sealed receipt for one local REAL non-production preview.

This profile is intentionally separate from :mod:`real_receipt`, which records
preparation/editorial history.  It records only measured technical preview
evidence and never confers export, production, Gate-3, or synthetic authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from .human_decision import load_human_decision
from .real_plan import load_real_plan
from .review_bundle import load_review_bundle

SCHEMA = "vip_fvs.real_preview_receipt.v1"
SCOPE = "LOCAL_REAL_NON_PRODUCTION_PREVIEW"
_FIELDS = {"schema", "receipt_id", "run_id", "attempt_id", "status", "scope", "source", "lifecycle", "authorization", "preview", "verifier", "technical_qc", "tooling", "production_eligible", "export_eligible", "NOT_OBSERVED"}
_DIGEST_FIELDS = ("source_sha256", "review_bundle_digest", "decision_digest", "plan_digest", "placement_digest", "mapping_digest", "authorization_digest", "output_sha256", "source_sha256_before", "source_sha256_after", "preview_digest", "digest", "ffprobe_digest", "ffmpeg_digest", "configuration_digest")
_FORBIDDEN = {"gate3", "gate3_receipt", "m3", "M3", "synthetic", "synthetic_suite", "rendered_output", "production_claim", "visual_claim", "audio_claim", "technical_qc_claim"}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def receipt_digest(record: Mapping[str, Any]) -> str:
    return _digest({k: record[k] for k in _FIELDS})


def _required_map(value: Any, keys: set[str], name: str) -> None:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise ValueError(f"{name} fields mismatch")


def _sha(value: Any, name: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(f"{name} must be a SHA-256 digest")


def _file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _success_artifact_boundary(value: Mapping[str, Any], *, authorized_output_root: str | os.PathLike[str] | None = None) -> None:
    """Revalidate every success artifact and keep it in one output directory."""
    preview = value["preview"]
    output_ref = Path(preview["output_ref"])
    verifier_ref = Path(value["verifier"]["artifact_ref"])
    qc_ref = Path(value["technical_qc"]["artifact_ref"])
    if not output_ref.is_absolute():
        raise ValueError("SUCCEEDED preview output_ref must be absolute")
    if not verifier_ref.is_absolute() or not qc_ref.is_absolute():
        raise ValueError("SUCCEEDED preview attestation refs must be absolute")
    output = output_ref.resolve()
    verifier = verifier_ref.resolve()
    qc = qc_ref.resolve()
    if not output.is_file():
        raise ValueError(f"SUCCEEDED preview output missing: {output}")
    if not verifier.is_file() or not qc.is_file():
        raise ValueError("SUCCEEDED preview attestation artifact missing")
    if authorized_output_root is None:
        raise ValueError("SUCCEEDED preview authorized_output_root is required")
    root = Path(authorized_output_root).resolve()
    for name, path in (("output", output), ("verifier", verifier), ("technical_qc", qc)):
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"SUCCEEDED preview {name} outside authorized output root") from exc
    actual_bytes = output.stat().st_size
    actual_sha = _file_sha256(output)
    if actual_bytes != preview["output_byte_count"] or actual_sha != preview["output_sha256"]:
        raise ValueError("SUCCEEDED preview output digest or byte-count mismatch")
    for name in ("verifier", "technical_qc"):
        artifact = Path(value[name]["artifact_ref"])
        if _file_sha256(artifact) != value[name]["digest"]:
            raise ValueError(f"SUCCEEDED preview receipt artifact digest mismatch: {artifact}")


def _scan(value: Any, path: str = "receipt") -> None:
    if isinstance(value, Mapping):
        if _FORBIDDEN.intersection(value):
            raise ValueError(f"{path} contains non-preview claim")
        for k, v in value.items():
            _scan(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _scan(v, f"{path}[{i}]")


class RealPreviewReceipt:
    def __init__(self, record: dict[str, Any], record_digest: str):
        self.record, self.record_digest = record, record_digest

    @classmethod
    def create(cls, record: Mapping[str, Any], *, authorized_output_root: str | os.PathLike[str] | None = None) -> "RealPreviewReceipt":
        value = dict(record)
        if set(value) != _FIELDS:
            raise ValueError("real preview receipt fields mismatch")
        if value["schema"] != SCHEMA or value["scope"] != SCOPE:
            raise ValueError("unexpected real preview receipt identity")
        for key in ("receipt_id", "run_id", "attempt_id", "status"):
            if not isinstance(value[key], str) or not value[key].strip():
                raise ValueError(f"{key} must be non-empty")
        if value["status"] not in {"SUCCEEDED", "REFUSED", "FAILED"}:
            raise ValueError("invalid preview status")
        if value["production_eligible"] is not False or value["export_eligible"] is not False:
            raise ValueError("preview receipt cannot grant production/export authority")
        _required_map(value["source"], {"source_revision_id", "source_sha256", "source_byte_count", "selected_stream_index", "timebase"}, "source")
        _required_map(value["lifecycle"], {"review_bundle_ref", "review_bundle_digest", "review_bundle_dependency_digest", "decision_ref", "decision_digest", "plan_ref", "plan_digest", "placement_digest", "mapping_digest"}, "lifecycle")
        _required_map(value["authorization"], {"authorization_id", "authorization_digest", "policy_identity", "scope"}, "authorization")
        _required_map(value["preview"], {"output_ref", "output_sha256", "output_byte_count", "source_sha256_before", "source_sha256_after", "source_byte_count_before", "source_byte_count_after", "source_start_pts", "source_end_pts", "preview_digest"}, "preview")
        _required_map(value["verifier"], {"status", "attempt_id", "digest", "artifact_ref", "evidence_class"}, "verifier")
        _required_map(value["technical_qc"], {"status", "attempt_id", "digest", "artifact_ref", "evidence_class"}, "technical_qc")
        if value["verifier"]["evidence_class"] != "MEASURED" or value["technical_qc"]["evidence_class"] != "MEASURED":
            raise ValueError("preview verifier and QC must be MEASURED evidence")
        for name in ("verifier", "technical_qc"):
            if value[name]["status"] not in {"PASS", "FAIL", "NOT_OBSERVED"}:
                raise ValueError(f"{name}.status is not schema-compatible")
        _required_map(value["tooling"], {"ffprobe_digest", "ffmpeg_digest", "configuration_digest"}, "tooling")
        if value["authorization"]["scope"] != "NON_PRODUCTION_PREVIEW":
            raise ValueError("invalid preview authorization scope")
        if not isinstance(value["NOT_OBSERVED"], list) or not value["NOT_OBSERVED"]:
            raise ValueError("NOT_OBSERVED must record unavailable inspection")
        for container_name in ("source", "lifecycle", "authorization", "preview", "verifier", "technical_qc", "tooling"):
            for key, item in value[container_name].items():
                if key in _DIGEST_FIELDS:
                    _sha(item, f"{container_name}.{key}")
        for name in ("source_byte_count", "selected_stream_index", "output_byte_count", "source_byte_count_before", "source_byte_count_after", "source_start_pts", "source_end_pts"):
            container = "source" if name in value["source"] else "preview"
            if not isinstance(value[container][name], int) or isinstance(value[container][name], bool) or value[container][name] < 0:
                raise ValueError(f"{container}.{name} must be a non-negative integer")
        _required_map(value["source"]["timebase"], {"num", "den"}, "source.timebase")
        num, den = value["source"]["timebase"]["num"], value["source"]["timebase"]["den"]
        if (isinstance(num, bool) or not isinstance(num, int) or num < 1
                or isinstance(den, bool) or not isinstance(den, int) or den < 1):
            raise ValueError("timebase must be positive integers")
        if value["status"] == "SUCCEEDED":
            if value["verifier"]["status"] != "PASS" or value["technical_qc"]["status"] != "PASS":
                raise ValueError("SUCCEEDED preview receipt requires verifier and technical QC PASS")
            if (value["verifier"]["attempt_id"] != value["attempt_id"]
                    or value["technical_qc"]["attempt_id"] != value["attempt_id"]):
                raise ValueError("SUCCEEDED preview receipt attempt identity mismatch")
            _success_artifact_boundary(value, authorized_output_root=authorized_output_root)
            # The digest proves bytes are unchanged; these checks prove those
            # bytes attest to this exact successful attempt.
            for name in ("verifier", "technical_qc"):
                try:
                    evidence = json.loads(Path(value[name]["artifact_ref"]).read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError(f"SUCCEEDED preview {name} artifact is unreadable") from exc
                if (not isinstance(evidence, Mapping) or evidence.get("status") != "PASS"
                        or not isinstance(evidence.get("attempt_id"), str)
                        or not evidence.get("attempt_id").strip()
                        or evidence.get("attempt_id") != value["attempt_id"]):
                    raise ValueError(f"SUCCEEDED preview {name} attempt/status mismatch")
        _scan(value)
        return cls(value, receipt_digest(value))

    def to_record(self) -> dict[str, Any]:
        return {**self.record, "record_digest": self.record_digest}


def save_real_preview_receipt(receipt: RealPreviewReceipt, path: str | os.PathLike[str], *, authorized_output_root: str | os.PathLike[str] | None = None) -> Path:
    if not isinstance(receipt, RealPreviewReceipt):
        raise TypeError("receipt must be RealPreviewReceipt")
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    root = authorized_output_root if authorized_output_root is not None else target.parent
    data = _canonical(receipt.to_record()) + b"\n"
    if target.exists():
        if load_real_preview_receipt(target, authorized_output_root=root).record_digest != receipt.record_digest:
            raise ValueError("sealed preview receipt differs")
        return target
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    with os.fdopen(fd, "wb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    try:
        os.link(temporary, target)
    except FileExistsError:
        if load_real_preview_receipt(target, authorized_output_root=root).record_digest != receipt.record_digest:
            raise ValueError("sealed preview receipt differs")
    finally:
        try: os.unlink(temporary)
        except FileNotFoundError: pass
    return target


def load_real_preview_receipt(path: str | os.PathLike[str], *, authorized_output_root: str | os.PathLike[str] | None = None) -> RealPreviewReceipt:
    raw = Path(path).read_bytes()
    if not raw.endswith(b"\n"):
        raise ValueError("preview receipt is not canonical sealed JSON")
    record = json.loads(raw[:-1].decode("utf-8"))
    supplied = record.pop("record_digest", None)
    receipt = RealPreviewReceipt.create(record, authorized_output_root=authorized_output_root)
    if supplied != receipt.record_digest or _canonical({**record, "record_digest": supplied}) + b"\n" != raw:
        raise ValueError("preview receipt digest or canonical encoding mismatch")
    return receipt


def build_real_preview_receipt(*, plan_artifacts: Any, authorization: Any, preview: Any,
                               verifier: Mapping[str, Any], technical_qc: Mapping[str, Any],
                               run_id: str, attempt_id: str,
                               plan_ref: str, verifier_ref: str = "verifier.json",
                               technical_qc_ref: str = "technical-qc.json") -> RealPreviewReceipt:
    """Compose the closed preview receipt from measured chain observations."""
    for name in ("review_bundle_record_digest", "review_bundle_dependency_digest", "human_decision_digest"):
        if not getattr(authorization, name, ""):
            raise ValueError("PREVIEW_PROVENANCE_REQUIRED:" + name)
    if verifier.get("status") == "PASS" and technical_qc.get("status") == "PASS":
        bundle_ref = getattr(authorization, "review_bundle_ref", "")
        decision_ref = getattr(authorization, "decision_ref", "")
        if (not bundle_ref or not decision_ref or not Path(bundle_ref).is_file()
                or not Path(decision_ref).is_file() or not Path(plan_ref).is_file()):
            raise ValueError("UPSTREAM_LIFECYCLE_UNRESOLVED")
        sealed_plan = load_real_plan(plan_ref)
        if (sealed_plan.plan_digest != plan_artifacts.plan_digest
                or sealed_plan.placement_digest != plan_artifacts.placement_digest
                or sealed_plan.mapping_digest != plan_artifacts.mapping_digest):
            raise ValueError("PLAN_DIGEST_MISMATCH")
        bundle = load_review_bundle(bundle_ref)
        decision = load_human_decision(decision_ref, bundle_path=bundle_ref)
        if bundle.record_digest != authorization.review_bundle_record_digest or bundle.dependency_digest != authorization.review_bundle_dependency_digest:
            raise ValueError("REVIEW_BUNDLE_DIGEST_MISMATCH")
        if decision.record_digest != authorization.human_decision_digest:
            raise ValueError("HUMAN_DECISION_DIGEST_MISMATCH")
        bp, dp = bundle.payload, decision.payload
        refinement_id = getattr(plan_artifacts.mapping, "source_refinement_id", "")
        refinement = plan_artifacts.plan.pinned_refinements.get(refinement_id)
        if (dp.get("decision_class") != "ACCEPT" or dp.get("disposition") != "ACCEPTED_FOR_PLAN"
                or dp.get("bundle_record_digest") != bundle.record_digest
                or dp.get("bundle_dependency_digest") != bundle.dependency_digest
                or dp.get("refinement_id") != refinement_id
                or dp.get("source_revision_id") != bp["source"]["source_revision_id"]
                or dp.get("source_sha256") != bp["source"]["source_sha256"]
                or bp["source"]["source_sha256"] != getattr(authorization, "source_sha256", None)
                or refinement is None
                or refinement.get("evidence_digest") != bp["refinement"]["evidence_digest"]
                or dp.get("refinement_evidence_digest") != bp["refinement"]["evidence_digest"]
                or refinement.get("source_revision_id") != bp["source"]["source_revision_id"]
                or refinement.get("selected_stream_index") != bp["source"]["selected_stream_index"]
                or refinement.get("timebase") != bp["source"]["timebase"]
                or getattr(plan_artifacts.projected_decision, "decision_id", None) != decision.payload["decision_id"]):
            raise ValueError("UPSTREAM_LIFECYCLE_LINEAGE_MISMATCH")
    for name, evidence in (("verifier", verifier), ("technical_qc", technical_qc)):
        if "attempt_id" in evidence and evidence.get("attempt_id") != attempt_id:
            raise ValueError(f"{name.upper()}_ATTEMPT_MISMATCH")
    def digest(value: Any) -> str:
        return _digest(value)
    verifier_record = dict(verifier)
    qc_record = dict(technical_qc)
    def artifact_digest(ref: str) -> str:
        path = Path(ref)
        if path.is_file():
            return _file_sha256(path)
        return digest(verifier_record if ref == verifier_ref else qc_record)
    is_v2 = getattr(preview, "schema_version", "v1") == "v2"
    ordered_source_digest = getattr(authorization, "source_set_digest", "")
    ordered_review_digest = digest(list(getattr(authorization, "review_bundle_record_digests", ())))
    ordered_review_dependencies = digest(list(getattr(authorization, "review_bundle_dependency_digests", ())))
    ordered_decisions = digest(list(getattr(authorization, "human_decision_digests", ())))
    source = {
        "source_revision_id": preview.source_revision_id,
        "source_sha256": ordered_source_digest if is_v2 else preview.source_sha256_before,
        "source_byte_count": preview.source_byte_count_before,
        "selected_stream_index": preview.selected_stream_index,
        "timebase": {"num": preview.source_timebase_num, "den": preview.source_timebase_den},
    }
    record = {
        "schema": SCHEMA, "receipt_id": f"preview-receipt:{attempt_id}", "run_id": run_id,
        "attempt_id": attempt_id, "status": "SUCCEEDED" if verifier.get("status") == "PASS" and technical_qc.get("status") == "PASS" else "FAILED",
        "scope": SCOPE, "source": source,
        "lifecycle": {
            "review_bundle_ref": getattr(authorization, "review_bundle_ref", "review-bundle:sealed"),
            "review_bundle_digest": ordered_review_digest if is_v2 else authorization.review_bundle_record_digest,
            "review_bundle_dependency_digest": ordered_review_dependencies if is_v2 else authorization.review_bundle_dependency_digest,
            "decision_ref": getattr(authorization, "decision_ref", "human-decision:sealed"),
            "decision_digest": ordered_decisions if is_v2 else authorization.human_decision_digest,
            "plan_ref": plan_ref, "plan_digest": plan_artifacts.plan_digest,
            "placement_digest": getattr(authorization, "placement_set_digest", "") if is_v2 else plan_artifacts.placement_digest,
            "mapping_digest": getattr(authorization, "composition_digest", "") if is_v2 else plan_artifacts.mapping_digest,
        },
        "authorization": {"authorization_id": authorization.authorization_id,
                           "authorization_digest": authorization.record_digest,
                           "policy_identity": authorization.policy_identity,
                           "scope": authorization.scope},
        "preview": {
            "output_ref": str(preview.output_path), "output_sha256": preview.output_sha256,
            "output_byte_count": preview.output_bytes, "source_sha256_before": preview.source_sha256_before,
            "source_sha256_after": preview.source_sha256_after,
            "source_byte_count_before": preview.source_byte_count_before,
            "source_byte_count_after": preview.source_byte_count_after,
            "source_start_pts": preview.source_start_pts, "source_end_pts": preview.source_end_pts,
            "preview_digest": (preview.record_digest if is_v2 else
                               digest({"output_sha256": preview.output_sha256, "output_bytes": preview.output_bytes,
                                       "plan_digest": plan_artifacts.plan_digest})),
        },
        "verifier": {"status": verifier.get("status", "FAIL") if verifier.get("status") in {"PASS", "FAIL", "NOT_OBSERVED"} else "FAIL", "attempt_id": attempt_id,
                      "digest": artifact_digest(verifier_ref), "artifact_ref": verifier_ref, "evidence_class": "MEASURED"},
        "technical_qc": {"status": technical_qc.get("status", "FAIL") if technical_qc.get("status") in {"PASS", "FAIL", "NOT_OBSERVED"} else "FAIL", "attempt_id": attempt_id,
                         "digest": artifact_digest(technical_qc_ref), "artifact_ref": technical_qc_ref, "evidence_class": "MEASURED"},
        "tooling": {"ffprobe_digest": preview.ffprobe_tool["sha256"], "ffmpeg_digest": preview.ffmpeg_tool["sha256"],
                     "configuration_digest": preview.tool_config_digest if is_v2 else
                     digest({"ffprobe_argv": list(preview.ffprobe_argv), "ffmpeg_argv": list(preview.ffmpeg_argv)})},
        "production_eligible": False, "export_eligible": False,
        "NOT_OBSERVED": ["VISUALLY_OBSERVED", "AUDIO_OBSERVED", "provider/cloud inference", "production/export authority"],
    }
    return RealPreviewReceipt.create(record, authorized_output_root=authorization.output_root)


FIXTURE_SCHEMA = "vip_fvs.fixture_preview_receipt.v1"
FIXTURE_SCOPE = "LOCAL_FIXTURE_NON_PRODUCTION_PREVIEW"
_FIXTURE_LIFECYCLE_FIELDS = {
    "decision_digest", "decision_id", "principal_kind", "fixture_scope",
    "refinement_id", "refinement_evidence_digest", "plan_ref", "plan_digest",
    "placement_digest", "mapping_digest", "plan_scope",
}
FIXTURE_NOT_OBSERVED_REQUIRED = (
    "human editorial authority",
    "visual editorial suitability",
    "audio observation",
    "production render capability",
    "provider/cloud inference",
)


def fixture_receipt_digest(record: Mapping[str, Any]) -> str:
    return _digest({k: record[k] for k in _FIELDS})


def _fixture_evidence_check(value: Mapping[str, Any], attempt_id: str) -> None:
    """Re-read one sealed attestation and require PASS under the bound attempt."""
    path = Path(value["artifact_ref"])
    payload = json.loads(path.read_bytes().decode("utf-8"))
    if payload.get("status") != "PASS" or payload.get("attempt_id") != attempt_id:
        raise ValueError("fixture preview attestation status or attempt mismatch")


class FixturePreviewReceipt:
    """Digest-sealed receipt for one generated-media fixture preview.

    This profile is disjoint from :class:`RealPreviewReceipt`: it records only
    fixture-scoped measured-technical evidence, and it can never be loaded as a
    REAL receipt (or vice versa) because schema and scope are identity-checked.
    """

    def __init__(self, record: dict[str, Any], record_digest: str):
        self.record, self.record_digest = record, record_digest

    @classmethod
    def create(cls, record: Mapping[str, Any], *,
               authorized_output_root: str | os.PathLike[str] | None = None) -> "FixturePreviewReceipt":
        value = dict(record)
        if set(value) != _FIELDS:
            raise ValueError("fixture preview receipt fields mismatch")
        if value["schema"] != FIXTURE_SCHEMA or value["scope"] != FIXTURE_SCOPE:
            raise ValueError("unexpected fixture preview receipt identity")
        for key in ("receipt_id", "run_id", "attempt_id", "status"):
            if not isinstance(value[key], str) or not value[key].strip():
                raise ValueError(f"{key} must be non-empty")
        if value["status"] not in {"SUCCEEDED", "REFUSED", "FAILED"}:
            raise ValueError("invalid fixture preview status")
        if value["production_eligible"] is not False or value["export_eligible"] is not False:
            raise ValueError("fixture preview receipt cannot grant production/export authority")
        _required_map(value["source"], {"source_revision_id", "source_sha256", "source_byte_count",
                                        "selected_stream_index", "timebase"}, "source")
        _sha(value["source"]["source_sha256"], "source.source_sha256")
        for key in ("source_byte_count", "selected_stream_index"):
            if not isinstance(value["source"][key], int) or isinstance(value["source"][key], bool) or value["source"][key] < 0:
                raise ValueError(f"source.{key} must be a non-negative integer")
        _required_map(value["source"]["timebase"], {"num", "den"}, "source.timebase")
        for key in ("num", "den"):
            if not isinstance(value["source"]["timebase"][key], int) or isinstance(value["source"]["timebase"][key], bool) or value["source"]["timebase"][key] <= 0:
                raise ValueError("source.timebase must be positive integers")
        _required_map(value["lifecycle"], _FIXTURE_LIFECYCLE_FIELDS, "lifecycle")
        lifecycle = value["lifecycle"]
        if lifecycle["principal_kind"] != "SYNTHETIC_HUMAN":
            raise ValueError("FIXTURE_PRINCIPAL_REQUIRED: fixture receipts cannot claim a human principal")
        if lifecycle["fixture_scope"] != "SYNTHETIC_FIXTURE" or lifecycle["plan_scope"] != "SYNTHETIC_FIXTURE":
            raise ValueError("FIXTURE_PLAN_SCOPE_REQUIRED: fixture receipts require SYNTHETIC_FIXTURE scope")
        for key in ("decision_id", "refinement_id", "plan_ref"):
            if not isinstance(lifecycle[key], str) or not lifecycle[key].strip():
                raise ValueError(f"lifecycle.{key} must be non-empty")
        for key in ("decision_digest", "refinement_evidence_digest", "plan_digest",
                    "placement_digest", "mapping_digest"):
            _sha(lifecycle[key], f"lifecycle.{key}")
        _required_map(value["authorization"], {"authorization_id", "authorization_digest",
                                               "policy_identity", "scope"}, "authorization")
        if value["authorization"]["scope"] != "NON_PRODUCTION_PREVIEW":
            raise ValueError("fixture preview authorization scope must be NON_PRODUCTION_PREVIEW")
        _sha(value["authorization"]["authorization_digest"], "authorization.authorization_digest")
        _required_map(value["preview"], {"output_ref", "output_sha256", "output_byte_count",
                                         "source_sha256_before", "source_sha256_after",
                                         "source_byte_count_before", "source_byte_count_after",
                                         "source_start_pts", "source_end_pts", "preview_digest"}, "preview")
        for key in ("output_sha256", "source_sha256_before", "source_sha256_after", "preview_digest"):
            _sha(value["preview"][key], f"preview.{key}")
        for key in ("output_byte_count", "source_byte_count_before", "source_byte_count_after",
                    "source_start_pts", "source_end_pts"):
            if not isinstance(value["preview"][key], int) or isinstance(value["preview"][key], bool) or value["preview"][key] < 0:
                raise ValueError(f"preview.{key} must be a non-negative integer")
        if value["preview"]["source_byte_count_before"] != value["source"]["source_byte_count"] or value["preview"]["source_byte_count_after"] != value["source"]["source_byte_count"]:
            raise ValueError("fixture preview source byte-count mismatch")
        if value["preview"]["source_sha256_before"] != value["source"]["source_sha256"] or value["preview"]["source_sha256_after"] != value["source"]["source_sha256"]:
            raise ValueError("fixture preview source digest mismatch")
        for name in ("verifier", "technical_qc"):
            _required_map(value[name], {"status", "attempt_id", "digest", "artifact_ref", "evidence_class"}, name)
            if value[name]["evidence_class"] != "MEASURED":
                raise ValueError(f"fixture preview {name} evidence_class must be MEASURED")
            if value[name]["status"] not in {"PASS", "FAIL", "NOT_OBSERVED"}:
                raise ValueError(f"invalid fixture preview {name} status")
            _sha(value[name]["digest"], f"{name}.digest")
        _required_map(value["tooling"], {"ffprobe_digest", "ffmpeg_digest", "configuration_digest"}, "tooling")
        for key in ("ffprobe_digest", "ffmpeg_digest", "configuration_digest"):
            _sha(value["tooling"][key], f"tooling.{key}")
        not_observed = value["NOT_OBSERVED"]
        if not isinstance(not_observed, list) or not not_observed:
            raise ValueError("fixture preview NOT_OBSERVED must be a non-empty list")
        missing = [entry for entry in FIXTURE_NOT_OBSERVED_REQUIRED if entry not in not_observed]
        if missing:
            raise ValueError("FIXTURE_NOT_OBSERVED_INCOMPLETE: " + ", ".join(missing))
        if value["status"] == "SUCCEEDED":
            if value["verifier"]["status"] != "PASS" or value["technical_qc"]["status"] != "PASS":
                raise ValueError("SUCCEEDED fixture preview requires PASS attestations")
            for name in ("verifier", "technical_qc"):
                if value[name]["attempt_id"] != value["attempt_id"]:
                    raise ValueError(f"FIXTURE_{name.upper()}_ATTEMPT_MISMATCH")
            _success_artifact_boundary(value, authorized_output_root=authorized_output_root)
            _fixture_evidence_check(value["verifier"], value["attempt_id"])
            _fixture_evidence_check(value["technical_qc"], value["attempt_id"])
        _scan(value)
        return cls(value, fixture_receipt_digest(value))

    def to_record(self) -> dict[str, Any]:
        return {**self.record, "record_digest": self.record_digest}


def _load_sealed_fixture_receipt(path: str | os.PathLike[str], *,
                                 authorized_output_root: str | os.PathLike[str] | None = None) -> FixturePreviewReceipt:
    raw = Path(path).read_bytes()
    if not raw.endswith(b"\n"):
        raise ValueError("fixture preview receipt is not canonical sealed JSON")
    record = json.loads(raw[:-1].decode("utf-8"))
    supplied = record.pop("record_digest", None)
    receipt = FixturePreviewReceipt.create(record, authorized_output_root=authorized_output_root)
    if supplied != receipt.record_digest or _canonical({**record, "record_digest": supplied}) + b"\n" != raw:
        raise ValueError("fixture preview receipt digest or canonical encoding mismatch")
    return receipt


def save_fixture_preview_receipt(receipt: FixturePreviewReceipt, path: str | os.PathLike[str], *,
                                 authorized_output_root: str | os.PathLike[str] | None = None) -> Path:
    if not isinstance(receipt, FixturePreviewReceipt):
        raise TypeError("fixture preview receipt required")
    FixturePreviewReceipt.create(receipt.record, authorized_output_root=authorized_output_root)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        existing = _load_sealed_fixture_receipt(target, authorized_output_root=authorized_output_root)
        if existing.record_digest == receipt.record_digest:
            return target
        raise ValueError("sealed fixture preview receipt differs")
    fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(receipt.to_record(), ensure_ascii=False, sort_keys=True,
                            separators=(",", ":")) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    try:
        os.link(tmp, target)
    except FileExistsError:
        existing = _load_sealed_fixture_receipt(target, authorized_output_root=authorized_output_root)
        if existing.record_digest == receipt.record_digest:
            return target
        raise ValueError("sealed fixture preview receipt differs")
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
    directory_fd = os.open(target.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return target


def load_fixture_preview_receipt(path: str | os.PathLike[str], *,
                                 authorized_output_root: str | os.PathLike[str] | None = None) -> FixturePreviewReceipt:
    return _load_sealed_fixture_receipt(path, authorized_output_root=authorized_output_root)


def build_fixture_preview_receipt(*, plan_artifacts: Any, authorization: Any, preview: Any,
                                  verifier: Mapping[str, Any], technical_qc: Mapping[str, Any],
                                  run_id: str, attempt_id: str, plan_ref: str,
                                  verifier_ref: str = "verifier.json",
                                  technical_qc_ref: str = "technical-qc.json") -> FixturePreviewReceipt:
    """Compose the sealed fixture receipt from fixture-chain observations only.

    No ReviewBundle, HumanDecisionArtifact, human provenance pin, model or
    provider reference is accepted; the lifecycle identity is the fixture
    EditorialDecision plus its MEASURED refinement evidence digest.
    """
    plan = getattr(plan_artifacts, "plan", None)
    decision = getattr(plan_artifacts, "projected_decision", None)
    if getattr(plan, "plan_scope", None) != "SYNTHETIC_FIXTURE":
        raise ValueError("FIXTURE_PLAN_SCOPE_REQUIRED")
    if (getattr(decision, "principal_kind", None) != "SYNTHETIC_HUMAN"
            or getattr(decision, "fixture_scope", None) != "SYNTHETIC_FIXTURE"):
        raise ValueError("FIXTURE_PRINCIPAL_REQUIRED")
    for name, evidence in (("verifier", verifier), ("technical_qc", technical_qc)):
        if "attempt_id" in evidence and evidence.get("attempt_id") != attempt_id:
            raise ValueError(f"FIXTURE_{name.upper()}_ATTEMPT_MISMATCH")
    refinement_id = getattr(plan_artifacts.mapping, "source_refinement_id", "")
    refinement = plan.pinned_refinements.get(refinement_id)
    if not isinstance(refinement, Mapping):
        raise ValueError("FIXTURE_REFINEMENT_AUTHORITY_MISSING")
    decision_to_record = getattr(decision, "to_record", None)
    decision_record = decision_to_record() if callable(decision_to_record) else dict(decision)
    source = {
        "source_revision_id": preview.source_revision_id,
        "source_sha256": preview.source_sha256_before,
        "source_byte_count": preview.source_byte_count_before,
        "selected_stream_index": preview.selected_stream_index,
        "timebase": {"num": preview.source_timebase_num, "den": preview.source_timebase_den},
    }
    lifecycle = {
        "decision_digest": _digest(decision_record),
        "decision_id": getattr(decision, "decision_id", ""),
        "principal_kind": getattr(decision, "principal_kind", ""),
        "fixture_scope": getattr(decision, "fixture_scope", ""),
        "refinement_id": refinement_id,
        "refinement_evidence_digest": refinement["evidence_digest"],
        "plan_ref": plan_ref,
        "plan_digest": plan_artifacts.plan_digest,
        "placement_digest": plan_artifacts.placement_digest,
        "mapping_digest": plan_artifacts.mapping_digest,
        "plan_scope": plan.plan_scope,
    }

    def artifact_digest(ref: str, evidence: Mapping[str, Any]) -> str:
        path = Path(ref)
        if path.is_file():
            return _file_sha256(path)
        return _digest(dict(evidence))

    record = {
        "schema": FIXTURE_SCHEMA,
        "receipt_id": f"fixture-preview-receipt:{attempt_id}",
        "run_id": run_id,
        "attempt_id": attempt_id,
        "status": "SUCCEEDED" if verifier.get("status") == "PASS" and technical_qc.get("status") == "PASS" else "FAILED",
        "scope": FIXTURE_SCOPE,
        "source": source,
        "lifecycle": lifecycle,
        "authorization": {"authorization_id": authorization.authorization_id,
                          "authorization_digest": authorization.record_digest,
                          "policy_identity": authorization.policy_identity,
                          "scope": authorization.scope},
        "preview": {
            "output_ref": str(preview.output_path),
            "output_sha256": preview.output_sha256,
            "output_byte_count": preview.output_bytes,
            "source_sha256_before": preview.source_sha256_before,
            "source_sha256_after": preview.source_sha256_after,
            "source_byte_count_before": preview.source_byte_count_before,
            "source_byte_count_after": preview.source_byte_count_after,
            "source_start_pts": preview.source_start_pts,
            "source_end_pts": preview.source_end_pts,
            "preview_digest": _digest({"output_sha256": preview.output_sha256,
                                       "output_bytes": preview.output_bytes,
                                       "plan_digest": plan_artifacts.plan_digest}),
        },
        "verifier": {"status": verifier.get("status", "FAIL") if verifier.get("status") in {"PASS", "FAIL", "NOT_OBSERVED"} else "FAIL",
                     "attempt_id": attempt_id, "digest": artifact_digest(verifier_ref, verifier),
                     "artifact_ref": verifier_ref, "evidence_class": "MEASURED"},
        "technical_qc": {"status": technical_qc.get("status", "FAIL") if technical_qc.get("status") in {"PASS", "FAIL", "NOT_OBSERVED"} else "FAIL",
                         "attempt_id": attempt_id, "digest": artifact_digest(technical_qc_ref, technical_qc),
                         "artifact_ref": technical_qc_ref, "evidence_class": "MEASURED"},
        "tooling": {"ffprobe_digest": preview.ffprobe_tool["sha256"],
                    "ffmpeg_digest": preview.ffmpeg_tool["sha256"],
                    "configuration_digest": _digest({"ffprobe_argv": list(preview.ffprobe_argv),
                                                     "ffmpeg_argv": list(preview.ffmpeg_argv)})},
        "production_eligible": False,
        "export_eligible": False,
        "NOT_OBSERVED": list(FIXTURE_NOT_OBSERVED_REQUIRED),
    }
    return FixturePreviewReceipt.create(record, authorized_output_root=authorization.output_root)


__all__ = ["RealPreviewReceipt", "receipt_digest", "save_real_preview_receipt", "load_real_preview_receipt",
           "build_real_preview_receipt", "FixturePreviewReceipt", "FIXTURE_SCHEMA", "FIXTURE_SCOPE",
           "FIXTURE_NOT_OBSERVED_REQUIRED", "fixture_receipt_digest", "save_fixture_preview_receipt",
           "load_fixture_preview_receipt", "build_fixture_preview_receipt"]
