"""Gate-3 Appendix A.12 run-manifest producer (FR-08).

FR-08 required result: unique attempt identity separate from idempotency, a complete
recursive load-bearing digest inventory whose caller-declared entries are recompute-verified,
atomic persistence, and durable evidence staging.

Candidate-B DIRECT primitives (contract §5, R-02.e, L11 §5 D1/D2) are adopted here as
primitives only: `persist_run_manifest` (mkstemp + fsync + os.replace, returning the digest of
the persisted bytes) and `durable_artifact_paths` (manifest-first, deduplicated staging set).
No `gate3_challenger_b` namespace is introduced.
"""
from __future__ import annotations
import hashlib,json,os,pathlib,secrets,tempfile,time

#: Recursive load-bearing surface FR-08 must inventory, relative to the repository root.
LOAD_BEARING_SURFACES=("src/gate3","tests/gate3","schemas/gate3","scripts")
#: Compiled/interpreter caches are not load-bearing bytes and are not deterministic evidence.
_EXCLUDED_DIRS=frozenset({"__pycache__"})
_EXCLUDED_SUFFIXES=(".pyc",".pyo")


def _sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as fh:
        for chunk in iter(lambda:fh.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def load_bearing_files(root="."):
    """Recursive load-bearing file set as posix paths relative to `root`, sorted."""
    root=pathlib.Path(root)
    out=set()
    for surface in LOAD_BEARING_SURFACES:
        base=root/surface
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel=path.relative_to(root)
            if any(part in _EXCLUDED_DIRS for part in rel.parts):
                continue
            if path.suffix in _EXCLUDED_SUFFIXES:
                continue
            out.add(rel.as_posix())
    return sorted(out)


def load_bearing_digests(root="."):
    """Complete recursive load-bearing inventory as `"<posix-relpath>:<sha256-hex>"` entries."""
    root=pathlib.Path(root)
    return sorted("%s:%s"%(rel,_sha256_file(root/rel)) for rel in load_bearing_files(root))


def generate_attempt_id(prefix="attempt"):
    """Generate a unique per-execution attempt identity."""
    return "%s-%s-%s-%s"%(prefix,time.strftime("%Y%m%dT%H%M%SZ",time.gmtime()),os.getpid(),secrets.token_hex(8))


def _split_digest_entry(entry):
    if not isinstance(entry,str) or ":" not in entry:
        return None
    rel,digest=entry.rsplit(":",1)
    if not rel:
        return None
    return rel,digest


def reconcile_output_artifact_digests(declared,root="."):
    """Recompute-verify caller-declared digests and complete the load-bearing inventory.

    Returns `(entries, digest_failures)`. A caller digest for a real file is never accepted
    verbatim: the entry is rewritten to the recomputed sha256 and a `DIGEST_MISMATCH` failure is
    recorded when it disagreed. A declared entry whose file cannot be resolved is dropped and
    recorded as `DIGEST_UNVERIFIABLE` (fail-closed). The load-bearing surface is then added so
    the inventory is always complete.
    """
    root=pathlib.Path(root)
    verified={}
    failures=[]
    for entry in declared or ():
        parsed=_split_digest_entry(entry)
        if parsed is None:
            failures.append({"kind":"DIGEST_MALFORMED","entry":repr(entry)})
            continue
        rel,digest=parsed
        path=root/rel
        if not path.is_file():
            failures.append({"kind":"DIGEST_UNVERIFIABLE","path":rel,"declared":digest})
            continue
        actual=_sha256_file(path)
        if digest!=actual:
            failures.append({"kind":"DIGEST_MISMATCH","path":rel,"declared":digest,"recomputed":actual})
        verified[rel]=actual
    for rel in load_bearing_files(root):
        verified.setdefault(rel,_sha256_file(root/rel))
    return sorted("%s:%s"%(rel,verified[rel]) for rel in verified),failures


def persist_run_manifest(manifest,path):
    """Atomically persist canonical JSON and return the digest of the persisted bytes.

    DIRECT adoption of Candidate B's `persist_run_manifest` (`src/gate3_challenger_b/
    runmanifest.py:11-29` @ `5a983d14`, verbatim in L11 §5 D1): mkstemp in the destination
    directory, write, flush, fsync, `os.replace`. An incomplete write therefore never becomes
    visible at the final path.
    """
    target=pathlib.Path(path)
    target.parent.mkdir(parents=True,exist_ok=True)
    payload=(json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode("utf-8")
    fd,tmp_name=tempfile.mkstemp(prefix=target.name+".",dir=target.parent)
    try:
        with os.fdopen(fd,"wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name,target)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise
    return hashlib.sha256(target.read_bytes()).hexdigest()


def durable_artifact_paths(run_manifest_path,evidence_paths):
    """Return the explicit staging set, with the run manifest load-bearing and first.

    DIRECT adoption of Candidate B's `durable_artifact_paths` (`src/gate3_challenger_b/
    runmanifest.py:32-42` @ `5a983d14`, verbatim in L11 §5 D2). It is a pure string-set builder:
    it confers no evidence by itself; the authoritative runner must consume it.
    """
    manifest=str(run_manifest_path)
    seen={manifest}
    out=[manifest]
    for p in evidence_paths:
        s=str(p)
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out


def build_run_manifest(*,run_id,attempt_id=None,idempotency_key,input_revision_refs,policy_decision_refs,profile_config_digests,tool_runtime_observations,output_artifact_digests,failures,resource_evidence_ref,out_dir=None,declared_determinism_scope="deterministic-source-native",not_observed=("real-media execution","provider inference","model execution","protected-media processing","real editorial decisions")):
    """Build the Appendix A.12 run manifest.

    `attempt_id=None` generates a unique per-execution identity; an explicit string is honoured
    verbatim. `idempotency_key` is caller-supplied and stays stable across attempts of the same
    logical run, so a retry remains recognisable. `output_artifact_digests` is completed to the
    full recursive load-bearing inventory and every caller-declared digest for a real file is
    recompute-verified. When `out_dir` is given the manifest is persisted atomically through
    `persist_run_manifest`.
    """
    if attempt_id is None:
        attempt_id=generate_attempt_id()
    inventory,digest_failures=reconcile_output_artifact_digests(output_artifact_digests)
    m={"run_id":run_id,"attempt_id":attempt_id,"idempotency_key":idempotency_key,"input_revision_refs":list(input_revision_refs),"policy_decision_refs":list(policy_decision_refs),"profile_config_digests":list(profile_config_digests),"tool_runtime_observations":dict(tool_runtime_observations),"output_artifact_digests":inventory,"failures":list(failures)+digest_failures,"resource_evidence_ref":resource_evidence_ref,"declared_determinism_scope":declared_determinism_scope,"NOT_OBSERVED":list(not_observed)}
    if out_dir:
        persist_run_manifest(m,pathlib.Path(out_dir)/"run-manifest.json")
    return m


#: FR-07/FR-08 authority-protocol run evidence (Spec §17).  ONE attempt-bound collection.
COLLECTION_REL_PATH="docs/gate3/evidence/module-execution-records.json"
MODULE_OUTCOMES=("PASS","FAILED","TIMEOUT","SKIPPED","WALL_CLOCK_EXCEEDED")
_RECORD_DIGEST_FIELDS=("module","phase","executed","returncode","outcome",
                       "stdout_sha256","stderr_sha256")

def record_digest(*,attempt_id,record):
    """Per-record digest bound to the run attempt (Spec §17.2 item 3)."""
    from gate3 import authority
    payload={k:record.get(k) for k in _RECORD_DIGEST_FIELDS}
    payload["attempt_id"]=attempt_id
    return hashlib.sha256(authority.canonical_json(payload).encode("utf-8")).hexdigest()

def build_module_execution_record(*,attempt_id,module,phase,executed,returncode,outcome,
                                  stdout="",stderr=""):
    """One module's execution record, derived from the runner's own subprocess result."""
    if outcome not in MODULE_OUTCOMES:
        raise ValueError(f"unknown module outcome: {outcome!r}")
    if not isinstance(module,str) or not module.strip():
        raise ValueError("module must be a non-empty string")
    if not isinstance(executed,bool):
        raise ValueError("executed must be a bool")
    if not isinstance(returncode,int) or isinstance(returncode,bool):
        raise ValueError("returncode must be an exact integer")
    rec={"module":module,"phase":phase,"executed":executed,"returncode":returncode,
         "outcome":outcome,
         "stdout_sha256":hashlib.sha256((stdout or "").encode("utf-8")).hexdigest(),
         "stderr_sha256":hashlib.sha256((stderr or "").encode("utf-8")).hexdigest()}
    rec["record_digest"]=record_digest(attempt_id=attempt_id,record=rec)
    return rec

def build_module_execution_records(*,run_id,attempt_id,idempotency_key,candidate_revision,records):
    """Build the single persisted collection artifact (Spec §17.1)."""
    from gate3 import authority
    built=[]
    for raw in records:
        built.append(build_module_execution_record(attempt_id=attempt_id,**raw))
    doc={"run_id":run_id,"attempt_id":attempt_id,"idempotency_key":idempotency_key,
         "candidate_revision":candidate_revision,"records":built}
    doc["evidence_digest"]=authority.evidence_digest(authority.RECORD_KIND_RUN_EVIDENCE,doc)
    return doc

def derive_module_totals(collection):
    """Aggregates are DERIVED PROJECTIONS of the records, never the authority source."""
    records=(collection or {}).get("records") if isinstance(collection,dict) else None
    if not isinstance(records,list):return {"modules_executed":0,"modules_passed":0,"failures":[]}
    executed=[r for r in records if isinstance(r,dict) and r.get("executed") is True]
    passed=[r for r in executed if r.get("outcome")=="PASS"]
    failures=[r.get("module") for r in executed if r.get("outcome")!="PASS"]
    return {"modules_executed":len(executed),"modules_passed":len(passed),"failures":failures}

def module_execution_errors(collection,manifest,*,expected_modules):
    """Fail-closed consistency of the per-module execution evidence (Spec §17.2 item 7)."""
    from gate3 import authority
    errors=[]
    if not isinstance(collection,dict):
        return ["MODULE_EXECUTION_EVIDENCE_ABSENT"]
    records=collection.get("records")
    if not isinstance(records,list) or not records:
        return ["MODULE_EXECUTION_EVIDENCE_EMPTY"]
    attempt=collection.get("attempt_id")
    if not isinstance(attempt,str) or not attempt.strip():
        errors.append("MODULE_EXECUTION_ATTEMPT_IDENTITY_ABSENT")
    if isinstance(manifest,dict) and isinstance(manifest.get("attempt_id"),str):
        if attempt!=manifest["attempt_id"]:
            errors.append("MODULE_EXECUTION_ATTEMPT_ID_NOT_BOUND_TO_RUN_ATTEMPT")
    declared=collection.get("evidence_digest")
    if not isinstance(declared,str) or not declared:
        errors.append("MODULE_EXECUTION_EVIDENCE_DIGEST_ABSENT")
    else:
        recomputed=authority.evidence_digest(authority.RECORD_KIND_RUN_EVIDENCE,collection)
        if recomputed!=declared:
            errors.append("MODULE_EXECUTION_EVIDENCE_DIGEST_MISMATCH")
    seen=[]
    for rec in records:
        if not isinstance(rec,dict):
            errors.append("MODULE_EXECUTION_RECORD_NOT_AN_OBJECT");continue
        module=rec.get("module")
        if not isinstance(module,str) or not module.strip():
            errors.append("MODULE_EXECUTION_RECORD_MODULE_IDENTITY_ABSENT");continue
        if module in seen:
            errors.append(f"MODULE_EXECUTION_DUPLICATE_RECORD:{module}")
        seen.append(module)
        expected=record_digest(attempt_id=attempt,record=rec)
        if rec.get("record_digest")!=expected:
            errors.append(f"MODULE_EXECUTION_RECORD_DIGEST_MISMATCH:{module}")
        if rec.get("outcome") not in MODULE_OUTCOMES:
            errors.append(f"MODULE_EXECUTION_OUTCOME_INVALID:{module}")
    if isinstance(expected_modules,(set,frozenset,list,tuple)):
        expected_set=set(expected_modules)
        for module in sorted(expected_set-set(seen)):
            errors.append(f"MODULE_EXECUTION_RECORD_MISSING:{module}")
        for module in sorted(set(seen)-expected_set):
            errors.append(f"MODULE_EXECUTION_RECORD_NOT_IN_INVENTORY:{module}")
    totals=derive_module_totals(collection)
    observations=(manifest or {}).get("tool_runtime_observations") if isinstance(manifest,dict) else None
    if isinstance(observations,dict):
        declared_executed=observations.get("modules_executed")
        if isinstance(declared_executed,int) and not isinstance(declared_executed,bool):
            if declared_executed!=totals["modules_executed"]:
                errors.append(f"MODULE_EXECUTION_MODULES_EXECUTED_NOT_ATTRIBUTABLE:{declared_executed}!={totals['modules_executed']}")
        declared_passed=observations.get("tests_passed")
        if isinstance(declared_passed,int) and not isinstance(declared_passed,bool):
            if declared_passed!=totals["modules_passed"]:
                errors.append(f"SUITE_COMPLETENESS_NOT_DERIVED:PASS_COUNT_NOT_ATTRIBUTABLE:{declared_passed}!={totals['modules_passed']}")
    return errors
