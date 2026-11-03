"""Gate-3-local emission/consumption rules."""
METHOD_KINDS=("deterministic","model_scored","human_judged")
VERIFIER_PROVENANCE_FIELDS=("attestation_id","verifier_attempt_id","verifier_entry_point_id","producing_entry_point_ids","named_inputs","named_input_digest","method","configuration_digest","observations")
A10_REQUIRED_FIELDS=("subject_assertion_refs","observed_result","NOT_OBSERVED","agreement")
A10_REQUIRED_PRESENT=("independent_of_producer",)
MATCH_EVIDENCE_REQUIRED_FIELDS=("match_relation_ref","mapping_artifact_ref",
                                "mapping_evidence_digest","subjects","relation")

def _resolve(record,*,kind,ref,origin_resolver):
    """Resolve one declared origin through a PLAIN mapping. Never calls a caller method.

    ``origin_resolver`` must be an actual mapping (``dict`` user code, or any
    ``collections.abc.Mapping``).  The plan's ``hasattr(origin_resolver,"get")`` form would call a
    ``.get`` method on any caller-supplied OBJECT; the hard constraint is that this protocol never
    invokes a caller method, so an arbitrary object -- even one exposing ``get`` -- fails closed.
    """
    from collections.abc import Mapping
    if not isinstance(ref,str) or not ref.strip():return None
    if not isinstance(origin_resolver,Mapping):return None
    return origin_resolver.get((kind,ref))

def matched_support_authority(record,*,origin_resolver,admitted_mapping_digests):
    """R-9 / Spec §10: a MATCHED support item needs subject evidence AND a match artifact.

    A byte-bound MEASURED/C2 record does NOT become authoritative MATCHED evidence because its
    ``evidence_class`` says MATCHED.  The match itself must be attributable.
    """
    from gate3.authority import (Admission,ORIGIN_MATCH_RELATION,ORIGIN_NAMED_BYTES,
                                 R_EVIDENCE_NOT_OBSERVED,R_ORIGIN_NOT_PRESENT,
                                 R_ORIGIN_RESOLUTION_FAILED,refuse)
    for field in MATCH_EVIDENCE_REQUIRED_FIELDS:
        if not record.get(field):return Admission(False,None,None,refuse(R_ORIGIN_NOT_PRESENT,detail=field))
    subjects=record.get("subjects")
    if not isinstance(subjects,(list,tuple)) or len(subjects)<2:
        return Admission(False,None,None,refuse(R_EVIDENCE_NOT_OBSERVED,detail="subjects"))
    origins=record.get("subject_origins")
    if not isinstance(origins,(list,tuple)) or len(origins)<2:
        return Admission(False,None,None,refuse(R_EVIDENCE_NOT_OBSERVED,detail="subject_origins"))
    for declared in origins:
        if not isinstance(declared,dict):return Admission(False,None,None,refuse(R_ORIGIN_NOT_PRESENT,detail="subject_origin"))
        if declared.get("kind")!=ORIGIN_NAMED_BYTES:return Admission(False,None,None,refuse(R_ORIGIN_NOT_PRESENT,detail="subject_origin_kind"))
        if _resolve(record,kind=ORIGIN_NAMED_BYTES,ref=declared.get("ref"),origin_resolver=origin_resolver) is None:
            return Admission(False,None,None,refuse(R_ORIGIN_RESOLUTION_FAILED,detail=declared.get("ref")))
    declared_match=record.get("origin")
    if not isinstance(declared_match,dict) or declared_match.get("kind")!=ORIGIN_MATCH_RELATION:
        return Admission(False,None,None,refuse(R_ORIGIN_NOT_PRESENT,detail="match_relation"))
    match_digest=_resolve(record,kind=ORIGIN_MATCH_RELATION,ref=declared_match.get("ref"),origin_resolver=origin_resolver)
    if not isinstance(match_digest,str) or not match_digest:
        return Admission(False,None,None,refuse(R_ORIGIN_RESOLUTION_FAILED,detail=declared_match.get("ref")))
    mapping_digest=record.get("mapping_evidence_digest")
    if not isinstance(admitted_mapping_digests,(set,frozenset,dict,list,tuple)) or mapping_digest not in admitted_mapping_digests:
        return Admission(False,None,None,refuse(R_ORIGIN_RESOLUTION_FAILED,detail="mapping_evidence_digest"))
    from gate3.authority import Origin
    return Admission(True,Origin(kind=ORIGIN_MATCH_RELATION,ref=declared_match["ref"],resolved_digest=match_digest),mapping_digest,None)

def method_kind_of(r):return r.get("method_kind","model_scored")
def _named_inputs_digest_ok(a):
    """A forged named_input_digest must not be accepted: re-hash the named input bytes."""
    import hashlib,pathlib
    digest=a.get("named_input_digest");inputs=a.get("named_inputs")
    if not isinstance(inputs,list) or not inputs or not isinstance(digest,str) or not digest:return False
    for rel in inputs:
        if not isinstance(rel,str):return False
        p=pathlib.Path(rel)
        if not p.is_file():return False
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:return False
    return True

def is_verifier_produced(a):
    if not isinstance(a,dict):return False
    for f in (*VERIFIER_PROVENANCE_FIELDS,*A10_REQUIRED_FIELDS):
        if not a.get(f):return False
    for f in A10_REQUIRED_PRESENT:
        if f not in a:return False
    # A.10 normatively names a single tool_and_runtime_identity object (FR-06).
    tri=a.get("tool_and_runtime_identity")
    if not isinstance(tri,dict) or not tri:return False
    if a["verifier_entry_point_id"] in a["producing_entry_point_ids"]:return False
    if not _named_inputs_digest_ok(a):return False
    return isinstance(a["observations"],list) and bool(a["observations"])
def subject_identity(r):return r.get("refinement_id") or r.get("assertion_id")
def attestation_covers(a,r,source_content_digest):
    return bool(is_verifier_produced(a) and subject_identity(r) in a["subject_assertion_refs"] and source_content_digest and a["named_input_digest"]==source_content_digest)
def may_consume_for_binding(r):
    # FR-01 + the FX-2 owner ruling: consuming a record for binding requires the *authoritative*
    # predicate, which re-measures the named source bytes (or the persisted byte-bound measurement
    # artifact) the C2 entry names. A self-declared MEASURED/source_* shape — even one carrying a
    # self-consistent C2 entry — is not enough, and `is_structurally_eligible` must never be
    # substituted here.
    from gate3.refinement import is_binding_eligible
    return bool(is_binding_eligible(r))
def _observation_for(a,r):
    sid=subject_identity(r)
    for o in a.get("observations") or []:
        if isinstance(o,dict) and o.get("refinement_id")==sid:return o
    return None

def _exact_int(v):
    """An EXACT Python integer, never a ``bool`` (``bool`` is an ``int`` subclass).

    MAJOR-B (gen-2 G-C): stream identity is a typed domain, so a declared identity must be the
    same *kind* of thing on both sides before it is compared.  The in-repo normative pattern is
    ``container.py:93-94`` and ``ordinal.py:14``; ``True``/``False``/``0.0``/``"0"``/``None`` are
    not stream indices.
    """
    return isinstance(v,int) and not isinstance(v,bool)

def _stream_binding_ok(a,r):
    """A subject's stream must match the stream the verifier actually measured (FR-06).

    MAJOR-B: the previous bare ``!=`` let Python coercion admit a foreign identity --
    ``False != 0.0`` is ``False`` (i.e. "equal"), so ``stream_index=0.0``/``False`` and
    ``measured_stream_index=0`` were treated as the same stream.  Both sides must now be EXACT
    integers; anything else (bool, float, str, None, missing) fails closed.
    """
    o=_observation_for(a,r)
    if o is None:return False
    measured=o.get("measured_stream_index");declared=r.get("stream_index")
    if not _exact_int(measured) or not _exact_int(declared):return False
    return measured==declared

def may_consume_for_pass(r,a,*,source_content_digest=None):
    # FR-14 / FR-06 (BLOCKER-4, gen-2 G-C): a technical PASS may consume a support item only when
    # the item is (1) the right class/method/replay shape, (2) covered by the attestation for THIS
    # subject, and (3) bound to the SAME bytes the attestation was resolved against.
    #
    # The pre-repair predicate stopped after (2): it never compared the record's own
    # `source_content_digest` with the resolved report digest and never consulted the record's own
    # byte authority, so a record bound to a different byte source (or stripped of byte authority)
    # could ride a shared `refinement_id` to PASS. Identity equality is not evidence equivalence:
    # a matching coverage key is NOT a substitute for matching, re-measurable bytes.
    if not (r.get("evidence_class") in ("MEASURED","MATCHED")
            and method_kind_of(r)=="deterministic"
            and r.get("replay_availability")=="replayable"
            and attestation_covers(a,r,source_content_digest)
            and a["agreement"]=="AGREE"
            and a["independent_of_producer"] is True
            and _stream_binding_ok(a,r)):return False
    # Fail-closed byte-source identity: the record's own declared digest must be present and
    # EQUAL to the digest resolved for the report. A missing/None/empty/non-string digest is
    # blocking, never "pass by omission"; a mismatching digest is the cross-byte-source case.
    declared=r.get("source_content_digest")
    if not isinstance(declared,str) or not declared or declared!=source_content_digest:return False
    # Authoritative byte authority for MEASURED support: the record's C2 declaration must survive
    # re-measurement of the bytes it names (FR-01). This is deliberately NOT applied to MATCHED
    # support, because `is_binding_eligible`/`is_structurally_eligible` are MEASURED-only shapes
    # and `is_structurally_eligible` must never be substituted here.
    if r.get("evidence_class")=="MEASURED":
        if not may_consume_for_binding(r):return False
        return True
    # R-9 / Spec §10: MATCHED support is admitted only when the MATCH ITSELF is attributable.
    # The previous unconditional exemption is REPLACED (never kept as a fallback): a relabelled
    # byte-bound MEASURED record is not authoritative MATCHED evidence, and a fabricated
    # nine-scalar record was the exact GEN2-BLK-1 exploit.
    resolver=r.get("_origin_resolver") or {}
    admitted=r.get("_admitted_mapping_digests") or set()
    return bool(matched_support_authority(r,origin_resolver=resolver,
                                          admitted_mapping_digests=admitted).admitted)
