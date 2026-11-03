from dataclasses import dataclass,field
from gate3.evidence import _exact_int,is_verifier_produced,may_consume_for_pass,subject_identity
from gate3.verify import observation_identity_errors

def _named_bytes_stream_index(att):
    """Re-measure the attestation's named container bytes.

    FX-4: `measured_stream_index`/`claimed_stream_index` are claims made by the same attestation
    that is being consumed, so a forger can make them agree with each other and with the support
    record while contradicting the named bytes (probe4 case vii). The named bytes decide the
    selected stream; an unmeasurable named input fails closed.
    """
    inputs=att.get("named_inputs")
    if not isinstance(inputs,list) or not inputs or not isinstance(inputs[0],str) or not inputs[0]:
        return None,"QC_NAMED_INPUTS_MISSING"
    from gate3.container import parse_iso_bmff_timing
    try:measured=parse_iso_bmff_timing(inputs[0])
    except (OSError,ValueError):return None,"QC_NAMED_BYTES_UNMEASURABLE"
    stream=measured.get("stream_index")
    if not _exact_int(stream):return None,"QC_NAMED_BYTES_STREAM_UNMEASURED"
    return stream,None

def _consumed_subject_identity_ok(att,record,*,digest,named_stream):
    """The consumed subject's OWN observation must record identity against the named bytes.

    MAJOR-B: stream identity is compared TYPE-AWARE. A bare ``==``/``!=`` coerces, so ``0 == 0.0``
    and ``0 == False`` are ``True`` and a record/observation carrying a float or boolean "stream"
    would be accepted as identical to the named stream. Both sides must be EXACT integers.
    """
    sid=subject_identity(record)
    if not sid:return False
    matching=[o for o in (att.get("observations") or []) if isinstance(o,dict) and o.get("refinement_id")==sid]
    if len(matching)!=1:return False
    observation=matching[0]
    if observation.get("measured_source_digest")!=digest:return False
    observed_stream=observation.get("measured_stream_index");record_stream=record.get("stream_index")
    if not _exact_int(observed_stream) or not _exact_int(record_stream):return False
    if not _exact_int(named_stream):return False
    if observed_stream!=named_stream:return False
    if record_stream!=named_stream:return False
    return True

def may_consume_for_binding_origin(record,attestation,*,source_content_digest):
    """The consumed item's own RECOMPUTED evidence identity, or None when it is not identified.

    A support item that cannot name its own evidence cannot be consumed for a technical PASS: the
    subject key is not an evidence identity (Spec §13.2 item 3).  This is the CONSUMING SEAM for
    Task 10's ``observed_evidence_ref`` interface, so three properties are required beyond the
    item's shape:

    * the record must be bound to the same resolved bytes this report consumes
      (``source_content_digest``), so the identity returned is an identity OF that byte source;
    * the attestation must actually RECORD the evidence it observed for this item's subject -- an
      observation bound to the subject whose ``observed_evidence_ref`` is a 64-hex evidence
      identity.  An observation that names no evidence never supports consuming the item; and
    * the identity returned is RECOMPUTED from the record's own evidence projection.  A
      self-declared ``evidence_digest`` is a *check*, never an assertion (Spec §15.5): if it is
      present it must equal the recomputation, otherwise the record is not evidence-identified
      (§15.6).  Trusting the declaration would let a forger hand two copies of ONE evidence two
      different identities and defeat the per-evidence coverage set outright.
    """
    if not isinstance(record,dict):return None
    from gate3 import authority
    from gate3.evidence import subject_identity
    if record.get("source_content_digest")!=source_content_digest:return None
    sid=subject_identity(record)
    if not sid:return None
    observations=attestation.get("observations") if isinstance(attestation,dict) else None
    if not isinstance(observations,list):return None
    observed=[o for o in observations
              if isinstance(o,dict) and o.get("refinement_id")==sid
              and isinstance(o.get("observed_evidence_ref"),str)
              and len(o["observed_evidence_ref"])==64]
    if len(observed)!=1:return None
    kind=(authority.RECORD_KIND_MATCHED
          if record.get("evidence_class")=="MATCHED"
          else authority.RECORD_KIND_REFINEMENT)
    try:identity=authority.evidence_digest(kind,record)
    except Exception:return None
    if not identity:return None
    declared=record.get("evidence_digest")
    if declared is not None and declared!=identity:return None
    return identity

@dataclass(frozen=True)
class QCReport:
    report_id:str;artifact_id:str;qc_scope:str;checks:list=field(default_factory=list);supporting_evidence_refs:list=field(default_factory=list);verifier_attestation:dict|None=None;verifier_attestation_ref:str|None=None;support_records:dict=field(default_factory=dict);source_content_digest:str|None=None
    def __post_init__(self):
        if self.qc_scope not in ("technical","editorial"):raise ValueError("bad qc_scope")
        for c in self.checks:
            if c.get("result") not in ("PASS","FAIL","NOT_RUN"):raise ValueError("bad result")
            if c.get("evidence_class") not in ("MEASURED","MATCHED","VISUALLY_OBSERVED","AUDIO_OBSERVED","EDITORIAL_INFERENCE"):raise ValueError("bad evidence class")
            if self.qc_scope=="technical" and c.get("evidence_class")!="MEASURED":raise ValueError("technical qc must measured")
        if is_verifier_produced(self.verifier_attestation):object.__setattr__(self,"verifier_attestation_ref",self.verifier_attestation["attestation_id"])
    def _consumed_digest(self):
        """The digest every consumed support item must be admissible under.

        R-02.b: the explicit source_content_digest wins, else the attestation's named_input_digest;
        an explicit digest that CONTRADICTS the attestation is itself blocking.
        """
        att=self.verifier_attestation
        named=att.get("named_input_digest") if isinstance(att,dict) else None
        if self.source_content_digest is not None and named is not None and self.source_content_digest!=named:
            return None,"QC_SOURCE_DIGEST_CONTRADICTS_ATTESTATION"
        if self.source_content_digest is not None:return self.source_content_digest,None
        return named,None
    @property
    def status(self):
        if self.qc_scope=="editorial":return "BLOCKED"
        if not self.checks:return "DRAFT"
        if not all(c.get("result")=="PASS" for c in self.checks):return "REVISE"
        if not is_verifier_produced(self.verifier_attestation):return "BLOCKED"
        if self.verifier_attestation["agreement"]!="AGREE" or self.verifier_attestation["independent_of_producer"] is not True:return "BLOCKED"
        # FR-14: EVERY deterministic support item consumed for a technical PASS must be independently
        # admissibly verified. The previous set-intersection test let one covered subject carry
        # unlimited unverified supports, so it is REPLACED (never kept as a fallback).
        # FX-4: the attestation is load-bearing evidence for the WHOLE report, so a summary
        # `agreement == "AGREE"` label may not ride on any observation that records its own identity
        # failure -- consumed or not -- and the named bytes (not the attestation's own claim) decide
        # the selected stream. The per-item loop then re-measures each consumed subject against
        # those bytes.
        refs=list(self.supporting_evidence_refs)
        if not refs:return "BLOCKED"
        digest,err=self._consumed_digest()
        if err is not None or digest is None:return "BLOCKED"
        if observation_identity_errors(self.verifier_attestation):return "BLOCKED"
        named_stream,stream_err=_named_bytes_stream_index(self.verifier_attestation)
        if stream_err is not None:return "BLOCKED"
        # FR-14 / Spec §13.2: the consumed set is CLOSED and ENUMERATED, and EVERY load-bearing
        # item is admitted under its own domain-specific protocol.  Coverage is per-subject AND
        # per-evidence: a shared subject key is not shared coverage (the ADJ-1 laundering vector).
        admitted_evidence=set()
        for ref in refs:
            record=self.support_records.get(ref)
            if not isinstance(record,dict):return "BLOCKED"
            origin=may_consume_for_binding_origin(record,self.verifier_attestation,
                                                 source_content_digest=digest)
            if origin is None:return "BLOCKED"
            # BLOCKER-4/G-C: the per-item predicate also enforces the record's OWN
            # `source_content_digest` against this resolved `digest` and, for MEASURED support,
            # the record's own re-measurable byte authority (FR-01). Neither the origin identity
            # above nor the observation-side identity check below is a substitute: they validate
            # the record's identity and the attestation's claim about the subject, never the byte
            # source the consumed record itself was derived from.
            if not may_consume_for_pass(record,self.verifier_attestation,source_content_digest=digest):return "BLOCKED"
            if not _consumed_subject_identity_ok(self.verifier_attestation,record,digest=digest,named_stream=named_stream):return "BLOCKED"
            identity=origin
            if identity in admitted_evidence:return "BLOCKED"
            admitted_evidence.add(identity)
        return "PASS"
    def to_record(self):
        # A.9 does not declare support_records/source_content_digest (R-09.a): they are status
        # derivation inputs only and must NOT be persisted into the record.
        r={"report_id":self.report_id,"artifact_id":self.artifact_id,"qc_scope":self.qc_scope,"edit_qc_status":self.status,"checks":[dict(c) for c in self.checks],"supporting_evidence_refs":list(self.supporting_evidence_refs)}
        if self.verifier_attestation_ref:r["verifier_attestation_ref"]=self.verifier_attestation_ref
        return r
def bare_pass_is_insufficient(r):return r.get("edit_qc_status")=="PASS" and not (r.get("qc_scope") and r.get("supporting_evidence_refs"))
