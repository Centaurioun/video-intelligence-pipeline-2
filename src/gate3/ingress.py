"""Evidence-preserving Gate-3 candidate ingress.

Reject malformed/canonical-invalid input first. Repairable coordinate/provenance omissions are downgraded
without deleting the original claim. An ingress candidate is never binding-eligible.
"""
from __future__ import annotations
import hashlib
from collections.abc import Mapping
from gate3.temporal import PRECISION_TOKENS

DISPOSITIONS=("ADMITTED","REJECTED","DOWNGRADED")
CANONICAL_DOMAINS=("semantic_seconds","technical_window","matched_offset","source_pts","source_frame","proxy_time","timeline_time","rendered_output")
CANONICAL_EVIDENCE_CLASSES=("MEASURED","MATCHED","VISUALLY_OBSERVED","AUDIO_OBSERVED","EDITORIAL_INFERENCE")
CANONICAL_PRODUCER_KINDS=("human","deterministic_tool","model","comparison_method")
ASSERTION_STATUS=("ACTIVE","UNCERTAIN","NOT_OBSERVED","SUPERSEDED")
REFINEMENT_ELIGIBILITY=("ELIGIBLE","NOT_ELIGIBLE","BLOCKED")
PROVIDER_STATUS=("SUCCESS","PARTIAL","FAILED","UNSUPPORTED","ESCALATED")
METHOD_KINDS=("deterministic","model_scored","human_judged")
SOURCE_DOMAINS=("source_pts","source_frame")
MAPPED_DOMAINS=("proxy_time","timeline_time","rendered_output")
INVOCATION_PROVENANCE_SHAPE=("method_kind","tool","derivation","config_digest")
# A.1 declares these as OPTIONAL members of the same closed object (plan lines 7830-7831).
INVOCATION_PROVENANCE_OPTIONAL=("rank","score")
A1_REQUIRED_FIELDS=("assertion_id","source_revision_id","interval_id","stream_index","time_domain","origin_description","start","end","endpoint_semantics","evidence_assertion_refs","producer_attempt_id","evidence_class","producer_kind","invocation_ref","precision","uncertainty","assertion_status","refinement_eligibility","observation_group_key","binding_eligible")
A1_OPTIONAL_FIELDS=("time_base_or_rate","mapping_artifact_ref","config_digest","original_claim","invocation_provenance","asserts_policy_authorization","provider_status","input_coverage")

def _canonical_component(value):
    """Total, deterministic string form for any group-key participant (FR-05: never raise)."""
    if value is None: return ""
    if isinstance(value,str): return value
    if isinstance(value,bool): return "true" if value else "false"
    if isinstance(value,bytes): return "bytes:"+value.hex()
    if isinstance(value,(int,float,complex)): return repr(value)
    if isinstance(value,(list,tuple)): return "["+",".join(_canonical_component(v) for v in value)+"]"
    if isinstance(value,(set,frozenset)): return "{"+",".join(sorted(_canonical_component(v) for v in value))+"}"
    if isinstance(value,Mapping):
        items=sorted(value.items(),key=lambda kv:(_canonical_component(kv[0]),_canonical_component(kv[1])))
        return "{"+",".join(_canonical_component(k)+":"+_canonical_component(v) for k,v in items)+"}"
    return "<%s>"%type(value).__name__

def _canonical_digests(input_digests):
    """Sorted canonical components of the input-digest set; total for any iterable/None."""
    if input_digests is None: return []
    if isinstance(input_digests,(str,bytes)): return [_canonical_component(input_digests)]
    try: items=list(input_digests)
    except TypeError: return [_canonical_component(input_digests)]
    return sorted(_canonical_component(x) for x in items)

def observation_group_key(producer_kind,invocation_ref,config_digest,input_digests,*,stage_idempotency_key=None):
    """Derived, NOT producer-declared. Binds to the canonical Stage-attempt idempotency key.

    ``stage_idempotency_key`` is the run-manifest ``idempotency_key`` (the logical Stage-attempt
    identity, CANONICAL_CONTRACTS.md:153-154), NOT the attempt ID; it is never persisted into the
    A.1 record. Every participant is canonicalized so the helper is total: malformed container
    forms must produce a deterministic digest instead of raising.
    """
    payload="|".join([_canonical_component(producer_kind),_canonical_component(invocation_ref),
                      _canonical_component(config_digest),_canonical_component(stage_idempotency_key),
                      *_canonical_digests(input_digests)])
    return hashlib.sha256(payload.encode()).hexdigest()

def _recorded_provenance(raw):
    method=raw.get("method")
    if not isinstance(method,dict): return None
    recorded={"method_kind":method.get("method_kind","model_scored"),"tool":method.get("tool"),"derivation":method.get("derivation"),"config_digest":method.get("config_digest",raw.get("config_digest"))}
    # Design §6: provider rank/score are demoted to invocation-scoped provenance, so they must
    # survive normalization for the A.1 record to express the demotion.
    for key in INVOCATION_PROVENANCE_OPTIONAL:
        if raw.get(key) is not None: recorded[key]=raw[key]
    return recorded

def _valid_provenance(p):
    if not isinstance(p,dict): return False
    keys=set(p)
    if not set(INVOCATION_PROVENANCE_SHAPE)<=keys: return False
    if keys-set(INVOCATION_PROVENANCE_SHAPE)-set(INVOCATION_PROVENANCE_OPTIONAL): return False
    if p.get("method_kind") not in METHOD_KINDS: return False
    rank=p.get("rank")
    if rank is not None and (not isinstance(rank,int) or isinstance(rank,bool)): return False
    score=p.get("score")
    if score is not None and (not isinstance(score,(int,float)) or isinstance(score,bool)): return False
    return all(isinstance(p.get(k),str) and p.get(k) for k in ("tool","derivation","config_digest"))

def _recorded_deterministic(raw):
    p=_recorded_provenance(raw)
    return _valid_provenance(p) and p["method_kind"]=="deterministic"

def reject_predicate(raw):
    if not isinstance(raw,Mapping): return ["CANDIDATE_NOT_A_MAPPING"]
    reasons=[]
    required=("assertion_id","source_revision_id","interval_id","stream_index","time_domain","origin_description","start","end","endpoint_semantics","evidence_assertion_refs","producer_attempt_id","evidence_class","producer_kind","invocation_ref","precision","assertion_status","refinement_eligibility")
    for k in required:
        if k not in raw or raw[k] in (None,""): reasons.append(f"MISSING_{k.upper()}")
    # FR-05: a non-string invocation_ref must reject here; otherwise it reaches the group-key
    # join and escapes validate_candidate as a TypeError.
    if raw.get("invocation_ref") is not None and not isinstance(raw.get("invocation_ref"),str):
        reasons.append("INVOCATION_REF_NOT_STRING")
    start,end=raw.get("start"),raw.get("end")
    if not isinstance(start,int) or isinstance(start,bool) or not isinstance(end,int) or isinstance(end,bool):
        reasons.append("INTERVAL_ENDPOINTS_NOT_INTEGERS")
    elif end<=start: reasons.append("DEGENERATE_INTERVAL")
    if raw.get("endpoint_semantics")!="half_open": reasons.append("ABSENT_ENDPOINT_SEMANTICS")
    if raw.get("time_domain") not in CANONICAL_DOMAINS: reasons.append("DOMAIN_OUTSIDE_CANONICAL_SET")
    if raw.get("evidence_class") not in CANONICAL_EVIDENCE_CLASSES: reasons.append("EVIDENCE_CLASS_OUTSIDE_CANONICAL_SET")
    if raw.get("producer_kind") not in CANONICAL_PRODUCER_KINDS: reasons.append("PRODUCER_KIND_OUTSIDE_CANONICAL_SET")
    if raw.get("assertion_status") not in ASSERTION_STATUS: reasons.append("ASSERTION_STATUS_OUTSIDE_CANONICAL_SET")
    if raw.get("refinement_eligibility") not in REFINEMENT_ELIGIBILITY: reasons.append("REFINEMENT_ELIGIBILITY_OUTSIDE_CANONICAL_SET")
    if "provider_status" in raw and raw.get("provider_status") not in PROVIDER_STATUS: reasons.append("PROVIDER_STATUS_OUTSIDE_CANONICAL_SET")
    if raw.get("provider_status")=="PARTIAL" and not raw.get("input_coverage"): reasons.append("COVERAGE_DROPPED_UNDER_PARTIAL")
    si=raw.get("stream_index")
    if not isinstance(si,int) or isinstance(si,bool) or si<0: reasons.append("STREAM_INDEX_NOT_A_NON_NEGATIVE_INTEGER")
    refs=raw.get("evidence_assertion_refs")
    if not isinstance(refs,list) or any(not isinstance(x,str) for x in refs): reasons.append("EVIDENCE_ASSERTION_REFS_NOT_STRING_LIST")
    cov=raw.get("input_coverage")
    if cov is not None and (not isinstance(cov,list) or any(not isinstance(x,str) for x in cov)): reasons.append("INPUT_COVERAGE_NOT_STRING_LIST")
    cfg=raw.get("config_digest")
    if cfg is not None and not isinstance(cfg,str): reasons.append("CONFIG_DIGEST_NOT_STRING")
    method=raw.get("method")
    if method is not None and not _valid_provenance(_recorded_provenance(raw)): reasons.append("INVOCATION_PROVENANCE_INVALID")
    # A caller-supplied top-level `invocation_provenance` is the A.1 spelling of the same closed
    # object; admitting it without validation would emit a record that fails A.1 afterwards.
    if "invocation_provenance" in raw and not _valid_provenance(raw.get("invocation_provenance")): reasons.append("INVOCATION_PROVENANCE_INVALID")
    # FX-8 / A.1 (`schemas/gate3/ingress_candidate.json:42`): the field is pinned to
    # `{"const": false}`, so this producer seam must apply boolean IDENTITY, never Python
    # truthiness. JSON Schema `const` equality is type-aware: only the genuine boolean `False`
    # is admissible. A non-boolean value (0, 0.0, "", [], {}, None, ...) lies outside the
    # field's boolean value domain and could only reach the emitted record as an A.1-invalid
    # value, so it is rejected under a distinct type code rather than mislabelled as a policy
    # assertion. A genuine `True` is exactly the assertion A.1 forbids.
    if "asserts_policy_authorization" in raw:
        asserted=raw["asserts_policy_authorization"]
        if not isinstance(asserted,bool): reasons.append("ASSERTS_POLICY_AUTHORIZATION_NOT_BOOLEAN")
        elif asserted: reasons.append("CANDIDATE_MAY_NOT_ASSERT_POLICY")
    return sorted(set(reasons))

def _downgrade_predicate(raw):
    out=[]
    if raw.get("time_domain") in SOURCE_DOMAINS:
        if not _recorded_deterministic(raw): out.append("EXACTNESS_WITHOUT_RECORDED_DETERMINISTIC_PROVENANCE")
        if not raw.get("time_base_or_rate"): out.append("SOURCE_DOMAIN_WITHOUT_TIME_BASE")
    if raw.get("time_domain") in MAPPED_DOMAINS and not raw.get("mapping_artifact_ref"): out.append("MAPPED_DOMAIN_WITHOUT_MAPPING_ARTIFACT")
    if raw.get("precision") not in PRECISION_TOKENS: out.append("UNRECOGNISED_PRECISION")
    if raw.get("rank") is not None or raw.get("score") is not None: out.append("RANK_OR_SCORE_DEMOTED_TO_INVOCATION_PROVENANCE")
    if raw.get("uncertainty") is None: out.append("OMITTED_UNCERTAINTY_DEFAULTED_TO_UNKNOWN")
    return out

def validate_candidate(raw,*,stage_idempotency_key=None):
    reasons=reject_predicate(raw)
    if reasons: return {"disposition":"REJECTED","reason_codes":reasons,"downgrades":[],"record":None}
    downgrades=_downgrade_predicate(raw)
    admitted=set(A1_REQUIRED_FIELDS)|set(A1_OPTIONAL_FIELDS)
    record={k:v for k,v in raw.items() if k in admitted}
    p=_recorded_provenance(raw)
    if p is not None: record["invocation_provenance"]=p
    record.setdefault("uncertainty","unknown")
    record["binding_eligible"]=False
    # R-04.d/R-09.d.1: the logical Stage-attempt idempotency identity is a keyword-only input,
    # threaded from this single call site and never persisted into the A.1 record.
    record["observation_group_key"]=observation_group_key(raw["producer_kind"],raw["invocation_ref"],raw.get("config_digest",""),raw.get("input_coverage") or [],stage_idempotency_key=stage_idempotency_key)
    # Preserve the raw upstream assertion whenever normalization/downgrade was needed.
    if downgrades or any(k not in admitted for k in raw) or "method" in raw:
        record["original_claim"]=dict(raw)
    if downgrades:
        record["time_domain"]="semantic_seconds"; record["precision"]="semantic-window"; record["assertion_status"]="UNCERTAIN"; record["refinement_eligibility"]="NOT_ELIGIBLE"
        return {"disposition":"DOWNGRADED","reason_codes":[],"downgrades":downgrades,"record":record}
    return {"disposition":"ADMITTED","reason_codes":[],"downgrades":[],"record":record}
