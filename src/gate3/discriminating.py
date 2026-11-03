"""Persisted B2 discriminating-VFR evidence re-measured from named container bytes."""
from __future__ import annotations
import hashlib,json,pathlib
from gate3.container import parse_iso_bmff_timing
from gate3.pts import PtsTable
from gate3.rational import TimeBase
from gate3.temporal import classify_vfr
PRODUCER_ID="gate3.discriminating.build_discriminating_report";REPORT_NAME="discriminating-vfr-report.json"
EXPECTED_CONTROL_VFR="false";EXPECTED_FIXTURE_VFR="true"
REQUIRED_CHECKS=("control_measured_from_bytes","fixture_measured_from_bytes","control_is_cfr","fixture_is_vfr","fixture_is_discriminating")
def classify_container(path):
    m=parse_iso_bmff_timing(path);t=PtsTable(TimeBase(1,m["media_timescale"]),m["pts_ticks"]);v,p,b,d=classify_vfr(t,None)
    return {**m,"pts_ticks":list(m["pts_ticks"]),"vfr":v,"governing_basis":b,"measured_reference_period":f"{p.numerator}/{p.denominator}" if p else None,"declared_rate_deviation":d}
def _naive_vs_lookup_discriminates(path):
    m=parse_iso_bmff_timing(path);t=PtsTable(TimeBase(1,m["media_timescale"]),m["pts_ticks"])
    # Compare a late point inside the final sample. Nominal-25-fps arithmetic is intentionally only
    # an adversarial comparator; it NEVER supplies a source-frame binding.
    target_ticks=max(0,m["duration_ts"]-1);target_ms=target_ticks*1000//m["media_timescale"];naive=target_ms*25//1000
    tick=t.covering_tick(target_ticks);correct=t.ordinal_of(tick) if tick is not None else None
    return (correct is not None and naive!=correct),{"target_ticks":target_ticks,"naive_ordinal":naive,"correct_ordinal":correct,"frame_count":len(t.ticks)}
def build_discriminating_report(*,control_path,fixture_path,verifier_attempt_id,config_digest="gate3-default",out_dir=None):
    c=classify_container(control_path);f=classify_container(fixture_path);disc,detail=_naive_vs_lookup_discriminates(fixture_path)
    checks=[{"check":"control_measured_from_bytes","result":"PASS" if c.get("source_bytes_sha256") else "FAIL"},{"check":"fixture_measured_from_bytes","result":"PASS" if f.get("source_bytes_sha256") else "FAIL"},{"check":"control_is_cfr","result":"PASS" if c["vfr"]=="false" else "FAIL"},{"check":"fixture_is_vfr","result":"PASS" if f["vfr"]=="true" else "FAIL"},{"check":"fixture_is_discriminating","result":"PASS" if disc else "FAIL","detail":detail}]
    r={"report_id":"dvr_"+hashlib.sha256((c["source_bytes_sha256"]+f["source_bytes_sha256"]+verifier_attempt_id).encode()).hexdigest()[:16],"producing_entry_point_id":PRODUCER_ID,"verifier_attempt_id":verifier_attempt_id,"configuration_digest":config_digest,"control_source_sha256":c["source_bytes_sha256"],"fixture_source_sha256":f["source_bytes_sha256"],"control_measurement":c,"fixture_measurement":f,"checks":checks,"mandatory_checks_passed":all(x["result"]=="PASS" for x in checks),"discriminating_vfr_verified":disc and c["vfr"]=="false" and f["vfr"]=="true","NOT_OBSERVED":["real-media execution","provider/cloud inference","model execution"]}
    if out_dir:
        p=pathlib.Path(out_dir);p.mkdir(parents=True,exist_ok=True);(p/REPORT_NAME).write_text(json.dumps(r,indent=2,sort_keys=True))
    return r
def load_discriminating_report(path):
    if not path or not pathlib.Path(path).is_file():return None,["NO_DISCRIMINATING_VFR"]
    try:return json.loads(pathlib.Path(path).read_text()),[]
    except Exception as e:return None,[f"DISCRIMINATING_REPORT_UNPARSEABLE:{type(e).__name__}"]
def verify_discriminating_report(report,*,expected_run_attempt=None,control_path=None,fixture_path=None):
    errors=[]
    if not isinstance(report,dict):return False,["NO_DISCRIMINATING_VFR"]
    if not control_path or not fixture_path:return False,["DISCRIMINATING_MEASUREMENT_PATHS_REQUIRED"]
    try:mc=classify_container(control_path);mf=classify_container(fixture_path)
    except (OSError,ValueError) as e:return False,[f"DISCRIMINATING_MEASUREMENT_UNMEASURABLE:{e}"]
    c=report.get("control_measurement") or {};f=report.get("fixture_measurement") or {}
    if c.get("vfr")!=mc["vfr"]:errors.append("REPORTED_CONTROL_VFR_CONTRADICTS_MEASUREMENT")
    if f.get("vfr")!=mf["vfr"]:errors.append("REPORTED_FIXTURE_VFR_CONTRADICTS_MEASUREMENT")
    if mc["vfr"]!="false":errors.append("MEASURED_CONTROL_IS_NOT_CFR")
    if mf["vfr"]!="true":errors.append("MEASURED_FIXTURE_IS_NOT_VFR")
    if report.get("control_source_sha256")!=mc["source_bytes_sha256"] or c.get("source_bytes_sha256")!=mc["source_bytes_sha256"]:errors.append("CONTROL_EVIDENCE_DIGEST_DISAGREES_WITH_MEASURED_BYTES")
    if report.get("fixture_source_sha256")!=mf["source_bytes_sha256"] or f.get("source_bytes_sha256")!=mf["source_bytes_sha256"]:errors.append("FIXTURE_EVIDENCE_DIGEST_DISAGREES_WITH_MEASURED_BYTES")
    disc,detail=_naive_vs_lookup_discriminates(fixture_path)
    if not disc:errors.append(f"FIXTURE_IS_NOT_DISCRIMINATING:{detail}")
    by={x.get("check"):x.get("result") for x in report.get("checks",[]) if isinstance(x,dict)}
    for name in REQUIRED_CHECKS:
        if by.get(name)!="PASS":errors.append(f"MANDATORY_CHECK_NOT_PASS:{name}")
    if expected_run_attempt is not None and report.get("verifier_attempt_id")!=expected_run_attempt:errors.append("WRONG_RUN_ATTEMPT")
    return not errors,errors
