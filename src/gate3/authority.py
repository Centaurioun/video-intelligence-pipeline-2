"""Gate-3-local evidence-origin admission protocol (Spec §5-§8).

Design constraints (approved spec):
* no universal provenance record — obligation composition only;
* no stored authority flag — admissibility is derived, never persisted;
* shape-only predicates never confer authority;
* caller-provided scalar equality is necessary and never sufficient;
* missing/unresolvable/mismatched provenance fails closed;
* origin traversal is bounded (depth 2) with cycle refusal;
* this module never calls a caller-supplied method;
* this module never imports a structural predicate.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass

# --- origin kinds -----------------------------------------------------------
ORIGIN_NAMED_BYTES = "named_bytes"
ORIGIN_MEASUREMENT_ARTIFACT = "measurement_artifact"
ORIGIN_MAPPING_ARTIFACT = "mapping_artifact"
ORIGIN_MATCH_RELATION = "match_relation"
ORIGIN_VERIFIER_RE_DERIVATION = "verifier_re_derivation"
ORIGIN_RUNNER_EXECUTION_RECORD = "runner_execution_record"

#: Origin kinds that terminate bounded traversal: they are content-addressed
#: directly (named bytes by re-hashing; the runner collection by its own digest).
TERMINAL_ORIGIN_KINDS = (ORIGIN_NAMED_BYTES, ORIGIN_RUNNER_EXECUTION_RECORD)

ORIGIN_DEPTH_BOUND = 2

# --- fail-closed reason vocabulary (Spec §5.3) ------------------------------
R_ORIGIN_UNRESOLVED = "AUTHORITY_ORIGIN_UNRESOLVED"
R_ORIGIN_NOT_PRESENT = "AUTHORITY_ORIGIN_NOT_PRESENT"
R_ORIGIN_KIND_NOT_ADMITTED = "AUTHORITY_ORIGIN_KIND_NOT_ADMITTED"
R_ORIGIN_RESOLUTION_FAILED = "AUTHORITY_ORIGIN_RESOLUTION_FAILED"
R_SUBJECT_MISMATCH = "AUTHORITY_SUBJECT_MISMATCH"
R_ATTRIBUTION_NOT_INDEPENDENT = "AUTHORITY_ATTRIBUTION_NOT_INDEPENDENT"
R_EVIDENCE_NOT_OBSERVED = "AUTHORITY_EVIDENCE_NOT_OBSERVED"
R_REPLAY_FAILED = "AUTHORITY_REPLAY_FAILED"
R_EVIDENCE_DIGEST_ABSENT = "AUTHORITY_EVIDENCE_DIGEST_ABSENT"
R_EVIDENCE_DIGEST_MISMATCH = "AUTHORITY_EVIDENCE_DIGEST_MISMATCH"
R_ORIGIN_CYCLE = "AUTHORITY_ORIGIN_CYCLE"
R_ORIGIN_DEPTH_EXCEEDED = "AUTHORITY_ORIGIN_DEPTH_EXCEEDED"
R_ORIGIN_ALIAS_FORBIDDEN = "AUTHORITY_ORIGIN_ALIAS_FORBIDDEN"


@dataclass(frozen=True)
class Origin:
    """A resolved, typed origin. ``resolved_digest`` is computed by the CONSUMER."""
    kind: str
    ref: str
    resolved_digest: str


@dataclass(frozen=True)
class Refusal:
    reason: str
    detail: str | None = None


@dataclass(frozen=True)
class Admission:
    admitted: bool
    origin: Origin | None
    evidence_digest: str | None
    refusal: Refusal | None


def refuse(reason: str, detail: str | None = None) -> Refusal:
    return Refusal(reason=reason, detail=detail)


def is_refusal(value) -> bool:
    return isinstance(value, Refusal)


def _reject_non_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("canonical_json refuses NaN/Infinity")
    if isinstance(value, dict):
        for v in value.values():
            _reject_non_finite(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            _reject_non_finite(v)


def canonical_json(value) -> str:
    """Deterministic canonical JSON (Spec §15.3).

    Sorted keys, compact separators, UTF-8, sequence order preserved, sets sorted
    by the caller, NaN/Infinity refused.
    """
    _reject_non_finite(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


_ORIGIN_FIELD_CANDIDATES = ("origin", "byte_authority", "mapping_artifact_ref", "match_relation_ref",
                            "verifier_attestation_ref", "run_evidence_ref")


def _declared_origin(record) -> tuple[str, str] | None:
    """The record's declared origin as ``(kind, ref)``, or ``None``."""
    if not isinstance(record, dict):
        return None
    raw = record.get("origin")
    if isinstance(raw, dict):
        kind = raw.get("kind")
        ref = raw.get("ref")
        if isinstance(kind, str) and kind.strip() and isinstance(ref, str) and ref.strip():
            return kind, ref
    return None


def resolve_origin(record, *, consumer: str, admitted_kinds, resolver) -> "Origin | Refusal":
    """Resolve a record's declared origin for one consumer (Spec §5.4, §6 O-1)."""
    declared = _declared_origin(record)
    if declared is None:
        return refuse(R_ORIGIN_NOT_PRESENT)
    kind, ref = declared
    if kind not in tuple(admitted_kinds):
        return refuse(R_ORIGIN_KIND_NOT_ADMITTED, detail=kind)
    resolved = resolver.get((kind, ref)) if hasattr(resolver, "get") else None
    if not isinstance(resolved, str) or not resolved:
        return refuse(R_ORIGIN_RESOLUTION_FAILED, detail="ORIGIN_REF_UNRESOLVED")
    return Origin(kind=kind, ref=ref, resolved_digest=resolved)


def traverse_origins(start_ref, *, kind_of, resolver, parent_of) -> "tuple[Origin, ...] | Refusal":
    """Bounded, cycle-refusing origin traversal (Spec §7.3).

    Depth bound is ``ORIGIN_DEPTH_BOUND``; terminal kinds are
    ``TERMINAL_ORIGIN_KINDS``. Any revisit refuses with ``R_ORIGIN_CYCLE``.
    """
    out: list[Origin] = []
    visited: set[tuple[str, str]] = set()
    ref = start_ref
    depth = 0
    while ref is not None:
        kind = kind_of(ref)
        if not isinstance(kind, str) or not kind:
            return refuse(R_ORIGIN_RESOLUTION_FAILED, detail="ORIGIN_KIND_UNKNOWN")
        key = (kind, ref)
        if key in visited:
            return refuse(R_ORIGIN_CYCLE, detail=ref)
        visited.add(key)
        digest = resolver(key[0], ref) if callable(resolver) else None
        if not isinstance(digest, str) or not digest:
            return refuse(R_ORIGIN_RESOLUTION_FAILED, detail="ORIGIN_REF_UNRESOLVED")
        out.append(Origin(kind=kind, ref=ref, resolved_digest=digest))
        if kind in TERMINAL_ORIGIN_KINDS:
            return tuple(out)
        depth += 1
        if depth > ORIGIN_DEPTH_BOUND:
            return refuse(R_ORIGIN_DEPTH_EXCEEDED, detail=f"depth>{ORIGIN_DEPTH_BOUND}")
        ref = parent_of(ref)
    return tuple(out)


import hashlib

RECORD_KIND_REFINEMENT = "refinement"
RECORD_KIND_MAPPING = "mapping_artifact"
RECORD_KIND_MATCHED = "matched_support"
RECORD_KIND_ATTESTATION = "verifier_attestation"
RECORD_KIND_RUN_EVIDENCE = "module_execution_collection"

_REFINEMENT_EVIDENCE_FIELDS = ("evidence_class", "time_domain", "precision",
                               "source_content_digest", "stream_index", "start_ticks",
                               "end_ticks", "endpoint_semantics", "end_is_stream_tail",
                               "time_base", "frame_ordinal_basis")
_C2_CHECK = "C2_named_byte_binding"
_NON_EVIDENCE_VALIDATION_CHECKS = ("T7_vfr_classification", "T8_dts_reorder_evidence")
_MAPPING_EVIDENCE_FIELDS = ("mapping_id", "from_domain", "to_domain", "hop", "method",
                            "mapping_form", "params", "validated_sample", "residual",
                            "reconstruction")
_MATCHED_EVIDENCE_FIELDS = ("match_relation_ref", "mapping_artifact_ref",
                            "mapping_evidence_digest", "subjects", "relation",
                            "coordinate_space_key")
_ATTESTATION_EVIDENCE_FIELDS = ("subject_assertion_refs", "named_inputs", "named_input_digest",
                                "method", "configuration_digest", "observed_result", "agreement",
                                "independent_of_producer", "tool_and_runtime_identity",
                                "observations")
_COLLECTION_EVIDENCE_FIELDS = ("run_id", "attempt_id", "idempotency_key", "candidate_revision",
                               "records")
_COLLECTION_RECORD_FIELDS = ("module", "phase", "executed", "returncode", "outcome",
                             "stdout_sha256", "stderr_sha256", "record_digest")

_HEX64 = set("0123456789abcdef")


def _is_hex64(value) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX64


def _pick(record, fields) -> dict:
    if not isinstance(record, dict):
        return {}
    return {f: record[f] for f in fields if f in record}


def refinement_evidence_projection(record) -> dict:
    """Evidence-only projection of a C2 refinement (Spec §15.2).

    Includes the evidence-bearing fields and the FULL C2 binding entry; excludes the
    digest field, derived/status validation entries, and tool display metadata.
    """
    proj = _pick(record, _REFINEMENT_EVIDENCE_FIELDS)
    method = record.get("method") if isinstance(record, dict) else None
    if isinstance(method, dict):
        proj["method"] = _pick(method, ("derivation", "retained_enumeration"))
    c2 = None
    for entry in (record.get("validation_results") or []) if isinstance(record, dict) else []:
        if isinstance(entry, dict) and entry.get("check") == _C2_CHECK:
            c2 = {k: v for k, v in entry.items() if k not in ("check",)}
            c2["check"] = _C2_CHECK
            break
    if c2 is not None:
        proj["c2_binding_entry"] = c2
    return proj


def mapping_artifact_evidence_projection(record) -> dict:
    """Transform evidence only; custody fields and recomputed ``exactness`` excluded."""
    return _pick(record, _MAPPING_EVIDENCE_FIELDS)


def matched_support_evidence_projection(record) -> dict:
    """The MATCHED assertion's own evidence: subjects, relation and the mapping identity."""
    return _pick(record, _MATCHED_EVIDENCE_FIELDS)


def verifier_attestation_evidence_projection(record) -> dict:
    """What the verifier observed, including each observation's evidence reference."""
    proj = _pick(record, _ATTESTATION_EVIDENCE_FIELDS)
    obs = record.get("observations") if isinstance(record, dict) else None
    if isinstance(obs, list):
        proj["observations"] = [
            {k: o[k] for k in sorted(o)} if isinstance(o, dict) else o for o in obs
        ]
    return proj


def module_execution_collection_evidence_projection(record) -> dict:
    """Run identity plus the ORDERED per-module records (Spec §17.3).

    Writer wall-clock timestamps are excluded: a run's identity is its attempt.
    """
    proj = _pick(record, _COLLECTION_EVIDENCE_FIELDS)
    records = record.get("records") if isinstance(record, dict) else None
    if isinstance(records, list):
        proj["records"] = [ _pick(r, _COLLECTION_RECORD_FIELDS) for r in records ]
    return proj


_PROJECTIONS = {
    RECORD_KIND_REFINEMENT: refinement_evidence_projection,
    RECORD_KIND_MAPPING: mapping_artifact_evidence_projection,
    RECORD_KIND_MATCHED: matched_support_evidence_projection,
    RECORD_KIND_ATTESTATION: verifier_attestation_evidence_projection,
    RECORD_KIND_RUN_EVIDENCE: module_execution_collection_evidence_projection,
}


def evidence_projection(kind: str, record) -> dict:
    fn = _PROJECTIONS.get(kind)
    if fn is None:
        raise ValueError(f"unknown authority record kind: {kind!r}")
    return fn(record)


def evidence_digest(kind: str, record) -> str:
    """``sha256`` over ``canonical_json(evidence_projection(kind, record))``."""
    return hashlib.sha256(canonical_json(evidence_projection(kind, record)).encode("utf-8")).hexdigest()


def assert_evidence_digest(kind: str, record) -> "str | Refusal":
    """Recompute the evidence identity and compare it to the declared value."""
    declared = record.get("evidence_digest") if isinstance(record, dict) else None
    if not _is_hex64(declared):
        return refuse(R_EVIDENCE_DIGEST_ABSENT)
    computed = evidence_digest(kind, record)
    if computed != declared:
        return refuse(R_EVIDENCE_DIGEST_MISMATCH, detail=computed)
    return declared
