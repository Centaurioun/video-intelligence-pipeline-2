"""Independent Gate-3 verifier; re-derives source identity/timing from named bytes."""
from __future__ import annotations
import hashlib,json,pathlib,sys,time
from gate3.gate_guard import find_forbidden_gate_imports,scan_gate_sources
VERIFIER_ID="gate3.verify.run_verification";PRODUCING_IDS=("gate3.refinement.refine","gate3.fixturegen.generate_fixture")
CONTRACT_CHECK="canonical_contract_blob_unchanged"
CONTRACT_REL="docs/architecture/CANONICAL_CONTRACTS.md"
CONTRACT_BLOB="c0b665d70b311dd98b7ff9f4f564b2d5750ed17b"
MANDATORY_VERIFIER_CHECKS=("gate3_does_not_import_other_gates","independent_re_derivation","source_stream_and_tail_identity",CONTRACT_CHECK)
# A.10 required set: a frozen verifier representation must carry every one of these.
REQUIRED_ATTESTATION_FIELDS=("attestation_id","verifier_attempt_id","verifier_entry_point_id","producing_entry_point_ids","named_inputs","named_input_digest","method","configuration_digest","observations","observed_result","subject_assertion_refs","agreement","independent_of_producer","tool_and_runtime_identity","residual","NOT_OBSERVED")

def canonical_contract_blob_digest(path=None):
    """git-blob sha1 of the canonical shared contract (FR-06 canonical-contract blob self-check)."""
    p=pathlib.Path(path or CONTRACT_REL)
    data=p.read_bytes()
    return hashlib.sha1(b"blob %d\0"%len(data)+data).hexdigest()

def _evidence_ref(refinement):
    """The record's own evidence identity, so an attestation can name WHAT it verified."""
    try:
        from gate3 import authority
        if not isinstance(refinement,dict):return None
        declared=refinement.get("evidence_digest")
        if isinstance(declared,str) and declared:return declared
        return authority.evidence_digest(authority.RECORD_KIND_REFINEMENT,refinement)
    except Exception:
        return None

def _re_derive(refinement,container_path):
    from gate3.container import parse_iso_bmff_timing
    from gate3.pts import PtsTable
    from gate3.rational import TimeBase
    from gate3.temporal import tail_end
    m=parse_iso_bmff_timing(container_path);pts=m["pts_ticks"]
    if not isinstance(refinement,dict) or "start_ticks" not in refinement or "end_ticks" not in refinement:
        # A subject that cannot even be re-derived (e.g. a non-binding/blocked refinement, or a
        # wrong-stream record FR-01 refuses) fails closed: DISAGREE, never an exception.
        return {"endpoints_are_pts_members":False,"source_bytes_match":False,"stream_identity_matches":False,
                "declared_source_digest":None,"measured_source_digest":m["source_bytes_sha256"],
                "claimed_stream_index":None,"measured_stream_index":m.get("stream_index"),
                "derived_tail_end_ticks":None,"tail_matches_measured_tail":False,
                "producer_entry_point_id":None,"unmeasurable_subject":True,
                "observed_evidence_ref":None,}
    start=refinement["start_ticks"];end=refinement["end_ticks"]
    # FR-10/FR-02 (gen-2 MAJOR-B): stream identity is an EXACT INTEGER identity. A bare `==` admits
    # Python coercion (`False == 0`, `True == 1`, `1.0 == 1`), so the declared and measured stream
    # indices must both be genuine integers before they may be reported as matching.
    declared_stream=refinement.get("stream_index");measured_stream=m.get("stream_index")
    stream_ok=(isinstance(declared_stream,int) and not isinstance(declared_stream,bool)
               and isinstance(measured_stream,int) and not isinstance(measured_stream,bool)
               and declared_stream==measured_stream)
    digest_ok=refinement.get("source_content_digest")==m["source_bytes_sha256"]
    tail_match=None;derived_tail=None
    if refinement.get("end_is_stream_tail"):
        t=PtsTable(TimeBase(1,m["media_timescale"]),tuple(pts));facts={k:m.get(k) for k in ("nb_frames","duration_ts","duration_consistency")}
        try:te=tail_end(t,container_facts=facts);derived_tail=te.end_ticks if te.binding_eligible else None
        except ValueError:derived_tail=None
        tail_match=derived_tail==end and derived_tail is not None;endpoints=start in pts
    else:endpoints=start in pts and end in pts
    return {"endpoints_are_pts_members":endpoints,"source_bytes_match":digest_ok,"stream_identity_matches":stream_ok,"declared_source_digest":refinement.get("source_content_digest"),"measured_source_digest":m["source_bytes_sha256"],"claimed_stream_index":refinement.get("stream_index"),"measured_stream_index":m.get("stream_index"),"derived_tail_end_ticks":derived_tail,"tail_matches_measured_tail":tail_match,"producer_entry_point_id":refinement.get("producer_entry_point_id"),"observed_evidence_ref":_evidence_ref(refinement)}

def _declares_same_producer(r):
    """A subject that names the verifier itself as its producer is not independently verified."""
    names={r.get("producer_entry_point_id")}
    method=r.get("method")
    if isinstance(method,dict):
        tool=method.get("tool")
        if isinstance(tool,str):names.add(tool)
        elif isinstance(tool,dict):names.add(tool.get("name"))
    return VERIFIER_ID in names

def observation_identity_errors(att):
    """FX-4: re-derive every observation's recorded outcome from its OWN typed fields.

    `source_bytes_match`, `stream_identity_matches`, `endpoints_are_pts_members` and
    `tail_matches_measured_tail` are summary booleans inside the free-form observation item. A
    summary boolean that its own typed claims contradict -- or that is simply false -- means the
    attestation records an identity failure, and evidence that records its own identity failure can
    never support a technical-QC PASS (FR-14) or satisfy the verifier self-check (FR-06). The
    observation is therefore never believed on its label alone.
    """
    if not isinstance(att,dict):return ["attestation: NOT_AN_OBJECT"]
    observations=att.get("observations")
    if not isinstance(observations,list) or not observations:
        return ["attestation.observations: MISSING_OR_EMPTY"]
    errors=[]
    for index,o in enumerate(observations):
        if not isinstance(o,dict):
            errors.append(f"attestation.observations[{index}]: NOT_AN_OBJECT");continue
        ref=o.get("refinement_id") or f"index_{index}"
        if o.get("source_bytes_match") is not True or o.get("declared_source_digest")!=o.get("measured_source_digest"):
            errors.append(f"attestation.observations[{ref}].source_bytes_match: NOT_VERIFIED")
        # FR-10/FR-02 (gen-2 MAJOR-B): the claimed and measured stream indices must both be exact
        # integers AND equal; a coerced bool/float pair (`False`/`0`, `1.0`/`1`) is NOT verified.
        claimed_stream=o.get("claimed_stream_index");measured_stream=o.get("measured_stream_index")
        if (o.get("stream_identity_matches") is not True
                or not (isinstance(claimed_stream,int) and not isinstance(claimed_stream,bool))
                or not (isinstance(measured_stream,int) and not isinstance(measured_stream,bool))
                or claimed_stream!=measured_stream):
            errors.append(f"attestation.observations[{ref}].stream_identity_matches: NOT_VERIFIED")
        if o.get("endpoints_are_pts_members") is not True:
            errors.append(f"attestation.observations[{ref}].endpoints_are_pts_members: NOT_TRUE")
        if o.get("tail_matches_measured_tail") is False:
            errors.append(f"attestation.observations[{ref}].tail_matches_measured_tail: FALSE")
    return errors

def build_verifier_attestation_from_re_derivation(*,subjects,container_path,config_digest="gate3-default",expected_total_tests=None,attempt_id=None):
    obs=[];oks=[];same_path=False
    for index,r in enumerate(subjects):
        o=_re_derive(r,container_path)
        # A subject FR-01 refuses (blocked/wrong-stream) has no refinement_id; name it deterministically
        # so the attestation stays total and records DISAGREE instead of raising.
        o["refinement_id"]=(r.get("refinement_id") if isinstance(r,dict) else None) or f"unbound_subject_{index}"
        # A.10 declares no `tolerance` property, so residual/tolerance live in the free-form observation.
        o["residual"]=0;o["tolerance"]=0
        obs.append(o)
        if _declares_same_producer(r):same_path=True
        ok=o["endpoints_are_pts_members"] and o["source_bytes_match"] and o["stream_identity_matches"]
        if r.get("end_is_stream_tail"):ok=ok and bool(o["tail_matches_measured_tail"])
        oks.append(ok)
    measured=hashlib.sha256(pathlib.Path(container_path).read_bytes()).hexdigest()
    agreement="DISAGREE" if (same_path or not oks or not all(oks)) else "AGREE"
    ids=[o["refinement_id"] for o in obs]
    # FR-07 D1(c): the attempt identity is a CALLER/RUN-SUPPLIED binding, not a private label.
    # The canonical identity is the run manifest's `attempt_id` (A.12 / FR-08) -- the same value the
    # receipt's `expected_verifier_attempt_id` and the B2 report carry -- so a caller that knows the
    # run attempt records exactly that. With no caller attempt the producer may still mint a unique
    # per-attempt identity; that minted value is NOT bindable, so a receipt expecting a run attempt
    # must then block rather than be handed the expectation it cannot verify.
    supplied=attempt_id if isinstance(attempt_id,str) and attempt_id.strip() else None
    attempt=supplied or ("vatt_"+hashlib.sha256(f"{measured}|{VERIFIER_ID}|{'|'.join(ids)}|{time.time_ns()}".encode()).hexdigest()[:16])
    att={"attestation_id":"att_"+hashlib.sha256('|'.join(ids).encode()).hexdigest()[:16],"verifier_attempt_id":attempt,"verifier_entry_point_id":VERIFIER_ID,"producing_entry_point_ids":list(PRODUCING_IDS),"named_inputs":[container_path],"named_input_digest":measured,"method":"re-derive-source-pts-stream-tail-from-container","configuration_digest":config_digest,"tool_and_runtime_identity":{"verifier":VERIFIER_ID,"python":sys.version.split()[0],"platform":sys.platform},"observations":obs,"observed_result":obs,"subject_assertion_refs":ids,"NOT_OBSERVED":["real-media execution","provider inference","model execution","protected-media processing","real editorial decisions"],"agreement":agreement,"independent_of_producer":(not same_path) and VERIFIER_ID not in PRODUCING_IDS,"residual":0,"expected_total_tests":expected_total_tests}
    from gate3 import authority as _authority
    att["evidence_digest"]=_authority.evidence_digest(_authority.RECORD_KIND_ATTESTATION,att)
    return att

def mandatory_checks_passed(report):
    """The self-check must INSPECT the attestation, not merely read the top-level check list."""
    if not isinstance(report,dict):return False,["report: NOT_AN_OBJECT"]
    checks=report.get("checks")
    if not isinstance(checks,list):return False,["checks: MISSING"]
    by={c.get("check"):c.get("result") for c in checks if isinstance(c,dict)};fail=[]
    for name in MANDATORY_VERIFIER_CHECKS:
        if by.get(name)!="PASS":fail.append(f"{name}: {by.get(name,'MISSING')}")
    if report.get("verifier_entry_point_id")!=VERIFIER_ID:
        fail.append("verifier_entry_point_id: MISSING_OR_UNEXPECTED")
    att=report.get("attestation")
    if not isinstance(att,dict):
        fail.append("attestation: MISSING")
    else:
        att_id=att.get("verifier_entry_point_id")
        if att_id!=report.get("verifier_entry_point_id"):
            fail.append("verifier_entry_point_id: TOP_LEVEL_CONTRADICTS_ATTESTATION")
        if att_id in PRODUCING_IDS:
            fail.append("verifier_entry_point_id: NAMES_A_PRODUCER")
        # FX-4 / FR-06: producing and verifying entry points must be DISJOINT, not merely
        # "verifier is not one of the two frozen producer ids". An attestation that declares the
        # verifier as one of its own producers is not an independent verification.
        if att_id in (att.get("producing_entry_point_ids") or []):
            fail.append("verifier_entry_point_id: NOT_DISJOINT_FROM_PRODUCING_ENTRY_POINTS")
        tri=att.get("tool_and_runtime_identity")
        if not isinstance(tri,dict) or not tri:
            fail.append("attestation.tool_and_runtime_identity: MISSING")
        for field in REQUIRED_ATTESTATION_FIELDS:
            # NB: `residual` is legitimately 0, so test presence for it rather than truthiness.
            if field not in att or (field!="residual" and not att.get(field)):
                fail.append(f"attestation.{field}: MISSING")
        if not isinstance(att.get("observations"),list) or not att.get("observations"):
            fail.append("attestation.observations: MISSING")
        if att.get("agreement")!="AGREE":
            fail.append(f"attestation.agreement: {att.get('agreement','MISSING')}")
        if att.get("independent_of_producer") is not True:
            fail.append("attestation.independent_of_producer: NOT_TRUE")
        # FX-4: the recorded observation outcomes are re-derived from their own typed fields, so a
        # summary `agreement: AGREE` label cannot ride on observations that record identity failure.
        fail.extend(observation_identity_errors(att))
    return (not fail),fail

def run_verification(*,evidence_dir,subjects=None,container_path=None,config_digest="gate3-default",attempt_id=None):
    subjects=list(subjects or []);files,problem=scan_gate_sources();ownership=(problem is None and not find_forbidden_gate_imports(files))
    try:contract_ok=(canonical_contract_blob_digest()==CONTRACT_BLOB)
    except OSError:contract_ok=False
    if subjects and not container_path:att={"agreement":"DISAGREE"};rederived=False;identity=False
    elif subjects:
        att=build_verifier_attestation_from_re_derivation(subjects=subjects,container_path=container_path,config_digest=config_digest,attempt_id=attempt_id);rederived=att["agreement"]=="AGREE";identity=all(o["source_bytes_match"] and o["stream_identity_matches"] and (o["tail_matches_measured_tail"] is not False) for o in att["observations"])
    else:
        # Diagnostic no-subject run: not certification authority, but produces structurally explicit NOT_OBSERVED.
        att={"agreement":"DISAGREE"};rederived=False;identity=False
    checks=[{"check":"gate3_does_not_import_other_gates","result":"PASS" if ownership else "FAIL"},{"check":"independent_re_derivation","result":"PASS" if rederived else "FAIL"},{"check":"source_stream_and_tail_identity","result":"PASS" if identity else "FAIL"},{CONTRACT_CHECK:"",}]
    checks[-1]={"check":CONTRACT_CHECK,"result":"PASS" if contract_ok else "FAIL"}
    rep={"verifier_entry_point_id":VERIFIER_ID,"producing_entry_point_ids":list(PRODUCING_IDS),"checks":checks,"attestation":att,"NOT_OBSERVED":["protected-media processing","provider inference","model execution"]}
    ok,failures=mandatory_checks_passed(rep)
    rep["mandatory_checks_passed"]=bool(ok);rep["mandatory_check_failures"]=failures
    rep["verification_verdict"]="PASS" if ok else "FAIL"
    d=pathlib.Path(evidence_dir);d.mkdir(parents=True,exist_ok=True);(d/"verification-report.json").write_text(json.dumps(rep,indent=2,sort_keys=True));return rep
