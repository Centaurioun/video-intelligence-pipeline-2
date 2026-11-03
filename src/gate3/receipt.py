"""Gate-3 implementation receipt consuming persisted evidence; no maturity promotion."""
from __future__ import annotations
import hashlib,json,pathlib
from gate3.discriminating import load_discriminating_report,verify_discriminating_report
from gate3 import runmanifest
# Task 20 / FR-07 (Spec §17.2 item 7): the receipt is the consumption surface for the per-module
# execution evidence, so `suite_completeness_errors` and the two record helpers it derives from are
# re-exported here from their single producer (`runmanifest`, Task 19).  T18's frozen N36-N41
# negative controls import `module_execution_errors` from this module by design; re-exporting is
# explicitly reserved to this task by the T19 lane memo.  No derivation logic is duplicated.
from gate3.runmanifest import derive_module_totals,module_execution_errors  # noqa: F401
from gate3 import authority
from gate3.evidence import is_verifier_produced
from gate3.lease import resource_consistency_errors
def _is_number(value):return isinstance(value,(int,float)) and not isinstance(value,bool)
NON_CLAIMS=["no real-media execution","no editorial PASS","no production renderer selection","no AI/model QC claim","no archive-scale readiness"]
NOT_OBSERVED=["protected-media processing","provider/cloud inference","model download/change","real human editorial decisions","real-media frame accuracy","OTIO/Premiere round-trip precision"]
def load_persisted_json(path,*,kind):
    if not path:return None,[f"{kind}_PATH_MISSING"]
    p=pathlib.Path(path)
    if not p.is_file():return None,[f"{kind}_FILE_ABSENT"]
    try:return json.loads(p.read_text()),[]
    except Exception as e:return None,[f"{kind}_UNPARSEABLE:{type(e).__name__}"]
def measurement_record(m):return {"source_bytes_sha256":m["source_bytes_sha256"],"media_timescale":m["media_timescale"],"nb_frames":m["nb_frames"],"duration_ts":m["duration_ts"],"duration_consistency":m["duration_consistency"],"pts_ticks":list(m["pts_ticks"]),"stream_index":m["stream_index"],"stream_count":m["stream_count"]}
# FX-1 residual (lane R6): an authority-required typed provenance field that is ABSENT must never be
# treated as agreement -- `None == None` is not a match.  Absence gets its own distinct axis per
# field so it is diagnosable as absence, rather than being reported as a generic mismatch or (worse)
# silently passing the derivation term.  A key present with a `None` value counts as absent.
ABSENT_TYPED_FIELD_AXES={
    "source_bytes_match":"ATTESTATION_OBSERVATION_SOURCE_BYTES_MATCH_ABSENT",
    "stream_identity_matches":"ATTESTATION_OBSERVATION_STREAM_IDENTITY_MATCHES_ABSENT",
    "declared_source_digest":"ATTESTATION_OBSERVATION_DECLARED_SOURCE_DIGEST_ABSENT",
    "measured_source_digest":"ATTESTATION_OBSERVATION_MEASURED_SOURCE_DIGEST_ABSENT",
    "claimed_stream_index":"ATTESTATION_OBSERVATION_CLAIMED_STREAM_INDEX_ABSENT",
    "measured_stream_index":"ATTESTATION_OBSERVATION_MEASURED_STREAM_INDEX_ABSENT",
}
def absent_typed_field_names(o):
    """Authority-required typed provenance fields the observation does not actually carry."""
    return [f for f in ABSENT_TYPED_FIELD_AXES if o.get(f) is None]
def verifier_observation_errors(att,*,subject_ref,stream_index=None):
    """FX-1: `agreement == "AGREE"` is a label, not evidence.

    Every observation's recorded outcome is re-derived from the observation's OWN typed fields
    before it is believed, and the observation is then required to agree with the persisted
    measurement:

    * `source_bytes_match` must be true AND must equal `declared_source_digest == measured_source_digest`;
    * `stream_identity_matches` must be true AND must equal `claimed_stream_index == measured_stream_index`
      (a forger that tampers `measured_stream_index` to a stream the named bytes do not have would
      otherwise ride on an unchanged summary boolean -- reproduced as `FX-1` attack D);
    * `endpoints_are_pts_members` must be true;
    * `tail_matches_measured_tail`, where the producer recorded one, must not be false;
    * every observation's `measured_stream_index` must equal the persisted measurement's stream.

    FX-1 residual (lane R6): each authority-required typed field has exactly three states --
    present-and-equal (accepted), present-and-unequal (fails the derivation term), and ABSENT
    (fails closed under its own `..._ABSENT` axis, and can never satisfy the derivation term via
    `None == None`).

    Each finding carries the stable `ATTESTATION_OBSERVATION_INCONSISTENT` axis (with a per-finding
    detail suffix), a per-field `ABSENT_TYPED_FIELD_AXES` axis, or the pre-existing
    `MEASUREMENT_STREAM_INDEX_MISMATCH` axis.
    """
    errors=[];obs=[o for o in (att.get("observations") or []) if isinstance(o,dict)]
    if not obs:errors.append("ATTESTATION_OBSERVATION_INCONSISTENT:NO_OBSERVATIONS")
    for o in obs:
        ref=o.get("refinement_id")
        for field in absent_typed_field_names(o):
            errors.append(f"{ABSENT_TYPED_FIELD_AXES[field]}:{ref}")
        declared,measured=o.get("declared_source_digest"),o.get("measured_source_digest")
        if o.get("source_bytes_match") is not True or declared is None or measured is None or declared!=measured:
            errors.append(f"ATTESTATION_OBSERVATION_INCONSISTENT:SOURCE_BYTES_NOT_VERIFIED:{ref}")
        claimed,observed_stream=o.get("claimed_stream_index"),o.get("measured_stream_index")
        # FR-10/FR-02 (gen-2 MAJOR-B): stream identity is an EXACT INTEGER identity. A bare `!=`
        # admits Python coercion (`False == 0`, `True == 1`, `1.0 == 1`), so both indices must be
        # genuine integers before the observation may agree.
        if (o.get("stream_identity_matches") is not True
                or not (isinstance(claimed,int) and not isinstance(claimed,bool))
                or not (isinstance(observed_stream,int) and not isinstance(observed_stream,bool))
                or claimed!=observed_stream):
            errors.append(f"ATTESTATION_OBSERVATION_INCONSISTENT:STREAM_IDENTITY_NOT_VERIFIED:{ref}")
        if o.get("endpoints_are_pts_members") is not True:
            errors.append(f"ATTESTATION_OBSERVATION_INCONSISTENT:ENDPOINTS_NOT_PTS_MEMBERS:{ref}")
        if o.get("tail_matches_measured_tail") is False:
            errors.append(f"ATTESTATION_OBSERVATION_INCONSISTENT:TAIL_NOT_MATCHED:{ref}")
        # FR-10/FR-02 (gen-2 MAJOR-B): the persisted measurement's stream is compared as an exact
        # integer too, so a coerced bool/float observation cannot satisfy it.
        if stream_index is not None and (
                not (isinstance(stream_index,int) and not isinstance(stream_index,bool))
                or not (isinstance(observed_stream,int) and not isinstance(observed_stream,bool))
                or observed_stream!=stream_index):
            errors.append(f"MEASUREMENT_STREAM_INDEX_MISMATCH:{ref}")
    if stream_index is not None and subject_ref not in [o.get("refinement_id") for o in obs]:
        errors.append("MEASUREMENT_STREAM_INDEX_MISMATCH:SUBJECT_NOT_OBSERVED")
    return errors
# ENFORCED (owner D1(c)): the attestation's `verifier_attempt_id` must equal the expected run
# attempt. `gate3.verify.build_verifier_attestation_from_re_derivation` now records a
# caller/run-supplied `attempt_id` verbatim, so every honest caller supplies the run manifest's
# `attempt_id`; a producer that minted its own identity instead can no longer be presented as if
# it verified the expected attempt.
def verify_verifier_report(report,*,subject_ref,source_content_digest,stream_index=None,expected_verifier_attempt_id=None):
    errors=[]
    if not isinstance(report,dict):return None,["VERIFIER_REPORT_NOT_OBJECT"]
    from gate3.verify import mandatory_checks_passed
    ok,fail=mandatory_checks_passed(report)
    if not ok:errors.extend("MANDATORY_CHECK_NOT_PASS:"+x for x in fail)
    att=report.get("attestation")
    if not is_verifier_produced(att):return None,errors+["ATTESTATION_INVALID"]
    if subject_ref not in att["subject_assertion_refs"]:errors.append("SUBJECT_NOT_COVERED")
    if att.get("named_input_digest")!=source_content_digest:errors.append("NAMED_INPUT_DIGEST_MISMATCH")
    if att.get("agreement")!="AGREE" or att.get("independent_of_producer") is not True:errors.append("VERIFIER_DID_NOT_AGREE")
    if expected_verifier_attempt_id is None:
        errors.append("VERIFIER_ATTEMPT_ID_UNBOUND")
    elif att.get("verifier_attempt_id")!=expected_verifier_attempt_id:
        errors.append("VERIFIER_ATTEMPT_ID_NOT_BOUND_TO_RUN_ATTEMPT")
    errors.extend(verifier_observation_errors(att,subject_ref=subject_ref,stream_index=stream_index))
    return (att if not errors else None),errors
def suite_completeness_errors(manifest,att,passed,*,module_execution=None,expected_modules=None):
    """FR-07: suite completeness/success must be DERIVED from attributable evidence.

    The caller's `passed` scalar is never sufficient on its own. The persisted run manifest is the
    attributable suite record: its `failures` must be an EMPTY list and its
    `tool_runtime_observations.modules_executed` must be recorded. The verifier attestation's
    `expected_total_tests`, when present, bounds what the caller may claim.

    Task 20 / FR-07 (Spec §17.2 item 5, §18.2): the manifest's own aggregates are CROSS-CHECKS
    only. Completeness and success are DERIVED from the persisted per-module execution records, so
    a caller-authored (or self-reported, internally consistent) aggregate scalar can no longer
    manufacture claimability. Absent the record collection the suite axis fails closed. The checks
    below the derivation remain and now run as ADDITIONAL cross-checks.
    """
    # FR-07 / Spec §17.2 item 5, §18.2: completeness and success are DERIVED from the persisted
    # per-module execution records.  The manifest's aggregates are CROSS-CHECKS only; a
    # caller-authored aggregate scalar can no longer manufacture claimability (MAJOR-A2).
    if module_execution is None:
        return ["SUITE_COMPLETENESS_NOT_DERIVED:MODULE_EXECUTION_EVIDENCE_ABSENT"]
    record_errors=module_execution_errors(module_execution,manifest,
                                          expected_modules=expected_modules if expected_modules is not None else ())
    if record_errors:
        return list(record_errors)
    totals=derive_module_totals(module_execution)
    if totals["modules_executed"]<1:
        return ["SUITE_COMPLETENESS_NOT_DERIVED:MODULES_EXECUTED_NOT_RECORDED"]
    if totals["failures"]:
        return ["SUITE_COMPLETENESS_NOT_DERIVED:RUN_MANIFEST_RECORDS_FAILURES"]
    if isinstance(passed,int) and not isinstance(passed,bool) and passed!=totals["modules_passed"]:
        return [f"SUITE_COMPLETENESS_NOT_DERIVED:PASS_COUNT_NOT_ATTRIBUTABLE:{passed}!={totals['modules_passed']}"]
    if not isinstance(manifest,dict):return ["SUITE_COMPLETENESS_NOT_DERIVED:NO_ATTRIBUTABLE_RUN_MANIFEST"]
    if not isinstance(manifest.get("failures"),list) or manifest["failures"]:
        return ["SUITE_COMPLETENESS_NOT_DERIVED:RUN_MANIFEST_RECORDS_FAILURES"]
    observations=manifest.get("tool_runtime_observations")
    if not isinstance(observations,dict):observations={}
    # BLOCKER-5 (FR-07): the runner's own invariant (`scripts/run-gate3-suite.sh:49`) is
    # `tests_passed <= modules_executed` over an integer module inventory the runner just executed.
    # A self-reported pass count may not be adopted when that arithmetic cannot hold: a truthy
    # non-integer, a bool, or zero modules executed is not an attributable module inventory, and
    # `tests_passed > modules_executed` is arithmetically impossible for any real execution.
    modules_executed=observations.get("modules_executed")
    if not isinstance(modules_executed,int) or isinstance(modules_executed,bool) or modules_executed<1:
        return ["SUITE_COMPLETENESS_NOT_DERIVED:MODULES_EXECUTED_NOT_RECORDED"]
    observed_passed=observations.get("tests_passed")
    if not isinstance(observed_passed,int) or isinstance(observed_passed,bool):
        observed_passed=None
    elif observed_passed>modules_executed:
        return [f"SUITE_COMPLETENESS_NOT_DERIVED:PASS_COUNT_EXCEEDS_MODULES_EXECUTED:{observed_passed}>{modules_executed}"]
    expected=(att or {}).get("expected_total_tests")
    if expected is not None:
        if not isinstance(expected,int) or isinstance(expected,bool) or expected<0:
            return ["SUITE_COMPLETENESS_NOT_DERIVED:EXPECTED_TOTAL_TESTS_INVALID"]
        if not isinstance(passed,int) or isinstance(passed,bool) or passed>expected:
            return [f"SUITE_COMPLETENESS_NOT_DERIVED:PASS_COUNT_EXCEEDS_EXPECTED_TOTAL_TESTS:{passed}>{expected}"]
    # FR-07: the caller's pass count is a CROSS-CHECK, never the authority. It must be attributable to
    # the persisted manifest; if the manifest records no pass count and no expected total is available,
    # the claim cannot be attributed at all.
    if observed_passed is not None:
        if passed!=observed_passed:
            return [f"SUITE_COMPLETENESS_NOT_DERIVED:PASS_COUNT_NOT_ATTRIBUTABLE:{passed}!={observed_passed}"]
    elif expected is None:
        return ["SUITE_COMPLETENESS_NOT_DERIVED:PASS_COUNT_NOT_ATTRIBUTABLE"]
    return []
def manifest_identity_errors(manifest,*,candidate_sha,expected_verifier_attempt_id):
    """FR-07 / BLOCKER-7: typed, distinct, correctly CROSS-BOUND run identities.

    The accepted candidate identity is the manifest's REVISION identity
    (``input_revision_refs``) and nothing else. ``idempotency_key`` is a stable logical-run label
    (``runmanifest.build_run_manifest`` / ``scripts/run-gate3-suite.sh:49`` set it to the constant
    ``gate3-synthetic-implementation-suite``) and ``attempt_id`` is a per-execution unique id
    (``runmanifest.py`` ``generate_attempt_id``); neither is a candidate revision SHA, so neither
    may be adopted as one. They are not deleted -- they are reclassified under their own distinct
    typed checks: the idempotency label must be a non-empty string, and the manifest's run
    ``attempt_id`` must equal the verifier run attempt the receipt expects.
    """
    errors=[]
    if candidate_sha=="UNBOUND":errors.append("CANDIDATE_SHA_UNBOUND")
    if not isinstance(manifest,dict):
        errors.append("RUN_MANIFEST_FILE_ABSENT");return errors
    revision_refs=manifest.get("input_revision_refs")
    if not isinstance(revision_refs,list) or not revision_refs or not all(isinstance(r,str) and r.strip() for r in revision_refs):
        errors.append("CANDIDATE_REVISION_IDENTITY_UNBOUND")
    elif not isinstance(candidate_sha,str) or candidate_sha not in revision_refs:
        errors.append("CANDIDATE_SHA_NOT_RUN_MANIFEST_SHA")
    idempotency_key=manifest.get("idempotency_key")
    if not isinstance(idempotency_key,str) or not idempotency_key.strip():
        errors.append("RUN_MANIFEST_IDEMPOTENCY_KEY_IDENTITY_INVALID")
    # FR-07 / BLOCKER-7 (repair of T18 node N44, which was red at the T19 integration base): the
    # per-run revision identity and the stable logical-run label are DISTINCT typed domains, so a
    # manifest can never admit its own logical-run label as the candidate revision.  Without this,
    # a manifest that self-consistently lists its label inside `input_revision_refs` satisfied the
    # exact-membership test above and the run was admitted with no revision identity at all.
    # No string-shape heuristic: this is a pure domain-distinctness refusal.  An honest caller
    # records a real revision in `input_revision_refs` and the runner's constant label (or another
    # logical-run label) in `idempotency_key`; a genuine revision that IS also used as the label is
    # indistinguishable from a label used as a revision without an explicit distinct
    # revision-identity field on the manifest schema, so it refuses closed (tested in N44).
    elif candidate_sha==idempotency_key:
        errors.append("RUN_MANIFEST_IDEMPOTENCY_KEY_NOT_A_CANDIDATE_REVISION")
    attempt_id=manifest.get("attempt_id")
    if not isinstance(attempt_id,str) or not attempt_id.strip():
        errors.append("RUN_MANIFEST_ATTEMPT_IDENTITY_ABSENT")
    elif expected_verifier_attempt_id is None:
        errors.append("RUN_MANIFEST_ATTEMPT_ID_NOT_BOUND_TO_VERIFIER_ATTEMPT")
    elif attempt_id!=expected_verifier_attempt_id:
        errors.append("RUN_MANIFEST_ATTEMPT_ID_NOT_BOUND_TO_EXPECTED_VERIFIER_ATTEMPT")
    return errors
def manifest_inventory_errors(manifest,root="."):
    """FR-08 / BLOCKER-6: present, complete and recompute-verified load-bearing inventory.

    ``run_manifest.json`` makes ``output_artifact_digests`` a REQUIRED property, and the
    authoritative producer ``runmanifest.build_run_manifest`` always completes the inventory via
    ``reconcile_output_artifact_digests``, which recomputes every caller-declared digest and fails
    closed on an unresolvable entry. The receipt re-derives that inventory from the persisted
    artifacts before it may claim the run: a forged digest, an unresolvable/malformed entry, an
    absent key and a present-but-empty key all block. ``root`` is the same repository root the
    producer inventories against (the authoritative runner uses ``pathlib.Path.cwd()``).
    """
    declared=manifest.get("output_artifact_digests")
    if not isinstance(declared,list) or not declared:
        return ["RUN_MANIFEST_INVENTORY_ABSENT"]
    _entries,failures=runmanifest.reconcile_output_artifact_digests(declared,root=root)
    if failures:
        kinds=sorted({str(f.get("kind")) for f in failures if isinstance(f,dict)}) or ["UNVERIFIABLE"]
        return ["RUN_MANIFEST_INVENTORY_INCONSISTENT:"+",".join(kinds)]
    declared_paths={entry.rsplit(":",1)[0] for entry in declared if isinstance(entry,str) and ":" in entry}
    missing=sorted(set(runmanifest.load_bearing_files(root))-declared_paths)
    if missing:
        return [f"RUN_MANIFEST_INVENTORY_INCOMPLETE:{len(missing)}_LOAD_BEARING_PATH(S)_UNDECLARED"]
    return []
def resource_evidence_substance_errors(record):
    """FR-09 / MAJOR-A: absence of resource evidence is not absence of a resource violation.

    ``lease.resource_consistency_errors`` deliberately treats an unobserved field as NOT_OBSERVED
    and skips it, so a record that observes NOTHING was admitted vacuously. Before the resource
    axis may be acceptable the record must carry the ceilings-vs-observed recomputation basis: the
    declared policy limits AND the observed magnitudes the recomputation checks them against.
    ``observed_max_heavy_children`` is deliberately NOT required -- the authoritative
    ``Lease.evidence()`` records ``None`` there when no heavy child ran, which is a genuine
    NOT_OBSERVED value rather than an omission.
    """
    if not isinstance(record,dict):return ["RESOURCE_EVIDENCE_NOT_SUBSTANTIVE:NOT_OBJECT"]
    errors=[]
    limits=record.get("ceilings")
    if not isinstance(limits,dict):
        errors.append("RESOURCE_EVIDENCE_NOT_SUBSTANTIVE:DECLARED_LIMITS_ABSENT")
    else:
        for key in ("wall_clock_seconds","disk_mib","concurrency"):
            if not _is_number(limits.get(key)):
                errors.append(f"RESOURCE_EVIDENCE_NOT_SUBSTANTIVE:DECLARED_LIMIT_ABSENT:{key}")
    for key in ("observed_wall_clock_seconds","observed_peak_disk_mib","configured_concurrency"):
        if not _is_number(record.get(key)):
            errors.append(f"RESOURCE_EVIDENCE_NOT_SUBSTANTIVE:OBSERVATION_ABSENT:{key}")
    return errors
def expected_module_inventory(manifest):
    """The load-bearing executed-module inventory the runner persisted, or `None` if unresolvable.

    Task 20 / FR-07: the authoritative runner (`scripts/run-gate3-suite.sh:8`) executes exactly
    ``p.stem for p in tests/gate3/test_*.py`` and persists its complete recursive load-bearing
    inventory into ``output_artifact_digests`` (FR-08).  The executed-module set is therefore
    recoverable from that persisted inventory as the ``tests/gate3/test_<stem>.py`` entries.

    Returns `None` when the inventory key is absent/malformed/empty, or when it carries no
    executed-module entry at all.  Callers must then let `module_execution_errors` skip ONLY the
    inventory cross-check -- never the record checks (Task 20 Step 3).
    """
    entries=manifest.get("output_artifact_digests") if isinstance(manifest,dict) else None
    if not isinstance(entries,list):
        return None
    names=set()
    for entry in entries:
        if not isinstance(entry,str) or ":" not in entry:
            continue
        rel=entry.rsplit(":",1)[0]
        parts=rel.split("/")
        if len(parts)==3 and parts[0]=="tests" and parts[1]=="gate3" and parts[2].startswith("test_") and parts[2].endswith(".py"):
            names.add(parts[2][:-len(".py")])
    return names or None
def build_receipt(*,candidate_sha,suite_command,passed,verifier_report_path=None,container_measurement_path=None,resource_evidence_path=None,subject_ref=None,discriminating_report_path=None,expected_verifier_attempt_id=None,control_container_path=None,fixture_container_path=None,out_dir=None,gate0_suite_executed=False,run_manifest_path=None,module_execution_path=None):
    report,re=load_persisted_json(verifier_report_path,kind="VERIFIER_REPORT");meas,me=load_persisted_json(container_measurement_path,kind="CONTAINER_MEASUREMENT");res,rr=load_persisted_json(resource_evidence_path,kind="RESOURCE_EVIDENCE");disc,de=load_discriminating_report(discriminating_report_path)
    measured_sha=meas.get("source_bytes_sha256") if isinstance(meas,dict) else None;stream=meas.get("stream_index") if isinstance(meas,dict) else None
    att,ae=verify_verifier_report(report,subject_ref=subject_ref,source_content_digest=measured_sha,stream_index=stream,expected_verifier_attempt_id=expected_verifier_attempt_id) if isinstance(report,dict) and measured_sha and subject_ref else (None,["VERIFIER_REPORT_INVALID"])
    if isinstance(meas,dict) and meas.get("duration_consistency")!="MATCH":me.append("DURATION_CONSISTENCY_NOT_MATCH")
    disc_ok,disc_errors=(False,["NO_DISCRIMINATING_VFR"])
    if isinstance(disc,dict):disc_ok,disc_errors=verify_discriminating_report(disc,expected_run_attempt=expected_verifier_attempt_id,control_path=control_container_path,fixture_path=fixture_container_path)
    res_errors=resource_consistency_errors(res) if isinstance(res,dict) else []
    # FR-09 / MAJOR-A: recompute the substance of the resource record, not merely its parseability.
    res_substance_errors=resource_evidence_substance_errors(res) if isinstance(res,dict) else []
    # FR-07: candidate identity and suite completeness derive from the EXACT persisted run manifest
    # for the exact selected candidate/attempt; a caller scalar alone can never establish identity.
    manifest=None
    if run_manifest_path and pathlib.Path(run_manifest_path).is_file():
        try:manifest=json.loads(pathlib.Path(run_manifest_path).read_text())
        except Exception:manifest=None
    cid_errors=manifest_identity_errors(manifest,candidate_sha=candidate_sha,expected_verifier_attempt_id=expected_verifier_attempt_id)
    # FR-08 / BLOCKER-6: the manifest's own load-bearing digest inventory is re-derived, not trusted.
    inventory_errors=manifest_inventory_errors(manifest) if isinstance(manifest,dict) else []
    cid_errors.extend(inventory_errors)
    # FR-07 D2: attributable suite completeness (a caller scalar is never sufficient on its own).
    # Reported as ERRORS so the suite axis survives another gate firing first.
    # Task 20: the persisted per-module execution collection is the DERIVATION source; the expected
    # module inventory is resolved from the runner's own persisted FR-08 inventory, and when it
    # cannot be resolved `module_execution_errors` skips ONLY the inventory cross-check.
    # Task 21: the load errors are surfaced too, so an unreadable/absent collection NAMES its
    # failure on the receipt rather than being silently indistinguishable from "no path given".
    module_execution,module_load_errors=load_persisted_json(module_execution_path,kind="module-execution-records") if module_execution_path else (None,[])
    suite_errors=suite_completeness_errors(manifest,att,passed,module_execution=module_execution,
                                           expected_modules=expected_module_inventory(manifest))
    cid_errors.extend(suite_errors)
    # Reported as ERRORS (not only as gates) so they survive another gate firing first.
    if expected_verifier_attempt_id is None:
        cid_errors.append("B2_EVIDENCE_ATTEMPT_UNBOUND")
    if isinstance(disc,dict) and measured_sha and disc.get("control_source_sha256")!=measured_sha:
        cid_errors.append("DISCRIMINATING_CONTROL_DIGEST_NOT_SELECTED_CANDIDATE")
    # The resource-consistency vocabulary is also reported under its FR-07 axis name (the FR-09
    # names stay authoritative and must not be renamed).
    if res_errors:
        cid_errors.append("RESOURCE_EVIDENCE_SELF_INCONSISTENT")
    errors=re+me+rr+ae+de+disc_errors+res_errors+res_substance_errors+module_load_errors+cid_errors
    gates=[("NO_VERIFIER_REPORT",isinstance(report,dict) and not re),("NO_CONTAINER_MEASUREMENT",isinstance(meas,dict) and not me),("NO_RESOURCE_EVIDENCE",isinstance(res,dict) and not rr),("RESOURCE_FAILURE",isinstance(res,dict) and not rr and not res_errors and res.get("resource_failure") is None),("RESOURCE_EVIDENCE_NOT_SUBSTANTIVE",not res_substance_errors),("SUITE_COMPLETENESS_NOT_DERIVED",not suite_errors),("CANDIDATE_IDENTITY_UNBOUND",not cid_errors),("NO_TESTS_PASSED",isinstance(passed,int) and not isinstance(passed,bool) and passed>0),("VERIFIER_REPORT_INVALID",att is not None),("NO_DISCRIMINATING_VFR",disc_ok)]
    blocked=next((n for n,ok in gates if not ok),None)
    def dig(path):
        p=pathlib.Path(path) if path else None
        return hashlib.sha256(p.read_bytes()).hexdigest() if p and p.is_file() else None
    # Task 21: surface the module-execution evidence (path, load errors and the DERIVATION
    # errors) so a blocked receipt NAMES the module-evidence failure, and never reports
    # claimable while any module-evidence error is present.  `suite_errors` is the
    # SUITE_COMPLETENESS_NOT_DERIVED gate, so `blocked is None` already implies `module_errs`
    # is empty; the explicit term makes the invariant local, independent of gate ordering.
    module_errs=list(module_load_errors)+list(suite_errors)
    r={"candidate_sha":candidate_sha,"suite_command":suite_command,"tests_passed":passed,"suite_completeness_evidence":{"derived_from":"persisted_run_manifest","manifest_failures":(manifest.get("failures") if isinstance(manifest,dict) else None),"modules_executed":((manifest.get("tool_runtime_observations") or {}).get("modules_executed") if isinstance(manifest,dict) else None),"expected_total_tests":(att or {}).get("expected_total_tests"),"suite_errors":suite_errors},"verifier_report_ref":verifier_report_path,"verifier_report_digest":dig(verifier_report_path),"container_measurement_ref":container_measurement_path,"container_measurement_digest":dig(container_measurement_path),"container_source_sha256":measured_sha,"resource_evidence_ref":resource_evidence_path,"resource_evidence_digest":dig(resource_evidence_path),"verifier_attestation_id":att.get("attestation_id") if att else None,"verifier_entry_point_id":att.get("verifier_entry_point_id") if att else None,"named_input_digest":att.get("named_input_digest") if att else None,"verifier_agreement":att.get("agreement") if att else None,"verifier_independent":att.get("independent_of_producer") if att else None,"verifier_subject_refs":list(att.get("subject_assertion_refs",[])) if att else [],"claimed_subject_ref":subject_ref,"discriminating_report_ref":discriminating_report_path,"discriminating_report_digest":dig(discriminating_report_path),"discriminating_vfr_verified":disc_ok,"module_execution_ref":module_execution_path,"module_execution_digest":dig(module_execution_path),"module_execution_evidence":{"path":str(module_execution_path) if module_execution_path else None,"errors":list(module_errs)},"maturity_claimed":"M1_CONTRACTED","m3_would_be_claimable":blocked is None and not module_errs,"m3_blocked_by":blocked,"evidence_errors":errors,"provenance_scope":"structural-content-addressed (NOT cryptographic non-forgeability)","promotion_requires":"explicit owner promotion record referencing this run","non_claims":NON_CLAIMS,"NOT_OBSERVED":NOT_OBSERVED,"gate0_suite_executed":gate0_suite_executed}
    if out_dir:
        d=pathlib.Path(out_dir);d.mkdir(parents=True,exist_ok=True);(d/"receipt.json").write_text(json.dumps(r,indent=2,sort_keys=True))
    return r
