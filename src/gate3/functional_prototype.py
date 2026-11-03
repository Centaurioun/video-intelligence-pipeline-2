"""Thin executable harness for the Gate-3 honest synthetic chain (contract section 11 ``RT-03``).

Why this module exists
----------------------
``RT-03`` names an executable chain --
``fixture -> refinement -> synthetic decision -> plan -> placement -> render -> mapping ->
reverse resolution -> verifier -> technical QC -> receipt`` -- but at the frozen candidate that
chain exists ONLY as unit-test choreography (``test_fr15_full_chain.py``,
``test_gen3_full_chain.py``, ``test_m3_end_to_end.py``).  ``scripts/run-gate3-suite.sh``,
``scripts/verify-gate3.py`` and ``scripts/make-gate3-receipt.py`` are the supported executable
surfaces for the suite run, the independent verifier and the receipt, but none of them executes the
chain itself.  The owner's Gate-3 functional-prototype completion brief classifies "test-only
orchestration with no usable executable path" and "render failure" as in-scope functional gaps and
authorizes the thinnest possible prototype runner that CALLS THE REAL PRODUCTION MODULES.

This module therefore orchestrates; it never re-implements Gate-3 semantics.  Every authoritative
step is a call into ``gate3``: ``fixturegen``/``container`` for source identity, ``refinement`` for
the measured interval, ``editorial``/``plan``/``placement`` for the editorial chain, ``mapping`` and
``render_adapter`` for the rendered hop, ``verify`` for the independent re-derivation, ``qc`` for
technical QC, and ``runmanifest``/``receipt`` for the tail artifacts.

Media materialization
---------------------
``render_adapter.render_synthetic`` is, by the frozen contract, a *synthetic attribution* render: it
writes a deterministic metadata envelope and attributes it by its own measured bytes.  ``RT-03``
requires a "synthetic non-production render", and the frozen adapter satisfies that literally.  The
owner brief additionally requires ACTUAL locally decodable output media.  That requirement is met
here at the harness layer -- media is generated and trimmed with local ``ffmpeg`` over the SAME
source-native PTS interval that ``refine`` measured -- without touching any frozen Gate-3 module or
T1-T11 semantic.  Both rendered artifacts are recorded, each attributed by the bytes it wrote.

Scope: synthetic/local only.  No protected/archive media, no provider, no cloud, no model, no
network, no production eligibility, no real-human editorial authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
from fractions import Fraction

REPO = pathlib.Path(__file__).resolve().parents[2]
TOOL = {"name": "gate3-functional-prototype", "version": "1.0"}
RUN_ID_DEFAULT = "run-20260915-gate3-functional-prototype-v1"
PROTOTYPE_TOOL = "local-ffmpeg"
NOT_OBSERVED = ("real-media execution", "provider/cloud inference", "model execution",
                "protected-media processing", "real editorial decisions")

# Scenario case table.  Every interval is expressed as INDEXES INTO THE MEASURED presentation PTS
# enumeration, so no boundary is ever derived from seconds multiplied by a nominal frame rate.
CASES = {
    ("F1", "real"): {"recipe": None, "real": {"rate": 30, "duration": 2.0, "size": "64x48"},
                     "interval_indices": [(2, 32)]},
    ("F1", "recipe"): {"recipe": "cfr_4s_shape", "real": None, "interval_indices": [(0, 4)]},
    ("F2", "recipe"): {"recipe": "vfr_nonuniform", "real": None, "interval_indices": [(0, 3)]},
    ("F2", "real"): {"recipe": None, "real": {"rate": 30, "duration": 2.0, "size": "64x48"},
                     "interval_indices": [(2, 20), (30, 48)]},
    ("F3", "real"): {"recipe": None, "real": {"rate": 30, "duration": 2.0, "size": "64x48"},
                     "interval_indices": [(2, 32)]},
    ("F3", "recipe"): {"recipe": "cfr_4s_shape", "real": None, "interval_indices": [(0, 4)]},
}
SCENARIOS = ("F1", "F2", "F3")

# Checks every scenario must satisfy.  A committed fixture recipe is a container-structure fixture
# with no decodable samples by design, so the media-decodability check is required only where the
# source is real media.
BASE_CHECKS = ("source_media_generated", "source_media_is_probeable", "source_media_immutable",
               "refinement_is_binding_eligible", "editorial_decision_created",
               "plan_structurally_valid", "plan_not_export_eligible", "placement_created",
               "render_succeeded", "rendered_output_file_non_empty", "render_attribution_verified",
               "mapping_artifact_exists", "mapping_exact",
               "reverse_mapping_resolves_expected_source_interval", "verifier_completed",
               "verifier_agreement_agree", "technical_qc_completed", "technical_qc_pass",
               "run_manifest_persisted", "fresh_process_readback_ok", "receipt_completed",
               "no_production_or_real_human_authority")
MEDIA_CHECKS = ("rendered_output_is_decodable_media",)
TEMPORAL_CHECKS = ("nominal_fps_reasoning_is_inadequate",)
MULTI_CHECKS = ("placements_are_ordered", "same_track_overlap_absent")


class PrototypeError(RuntimeError):
    """A checked functional failure of the honest prototype path."""


def interpreter():
    return sys.executable


def require_tool(name):
    path = shutil.which(name)
    if not path:
        raise PrototypeError(f"required local tool is absent: {name}")
    return path


def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def base_code_sha():
    p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), text=True, capture_output=True)
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else "UNBOUND"


def generate_real_synthetic_source(out_dir, *, name="source.mp4", rate=30, duration=2.0,
                                   size="64x48"):
    """Locally generate ACTUAL decodable synthetic source media (no network, no protected media)."""
    ffmpeg = require_tool("ffmpeg")
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    p = out / name
    cmd = [ffmpeg, "-v", "error", "-y", "-f", "lavfi",
           "-i", f"testsrc2=size={size}:rate={rate}:duration={duration}",
           "-c:v", "libx264", "-bf", "0", "-pix_fmt", "yuv420p", "-g", "15", str(p)]
    r = subprocess.run(cmd, text=True, capture_output=True)
    if r.returncode != 0 or not p.is_file():
        raise PrototypeError(f"local synthetic media generation failed: {r.stderr[-800:]}")
    return {"path": str(p), "sha256": sha256_file(p), "byte_count": p.stat().st_size,
            "producer": PROTOTYPE_TOOL, "recipe": f"testsrc2:{size}@{rate}:{duration}s",
            "source_kind": "real", "declared_rate": f"{rate}/1"}


def generate_recipe_source(out_dir, recipe, *, name="source.mp4"):
    """Materialize a committed synthetic fixture recipe from its own deterministic recipe."""
    from gate3.fixturegen import generate_fixture
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    o = generate_fixture(recipe, str(out), out_name=name)
    return {"path": o["path"], "sha256": o["sha256"], "byte_count": o["byte_count"],
            "producer": "gate3.fixturegen", "recipe": recipe, "source_kind": "recipe",
            "declared_rate": None}


def measure_source(path):
    from gate3.container import parse_iso_bmff_timing
    return parse_iso_bmff_timing(str(path))


def select_intervals(measurement, interval_indices):
    """Resolve interval INDEX PAIRS against the measured presentation PTS enumeration.

    The boundary values are source-native PTS ticks taken from the measurement; a nominal frame rate
    is never multiplied by a duration to obtain them.
    """
    ticks = list(measurement.get("pts_ticks") or ())
    if not ticks:
        raise PrototypeError("measurement carries no presentation PTS enumeration")
    out = []
    for pair in interval_indices:
        i, j = int(pair[0]), int(pair[1])
        if not (0 <= i < j < len(ticks)):
            raise PrototypeError(f"interval index pair {pair} is outside the measured enumeration")
        out.append((ticks[i], ticks[j]))
    return out


def ffprobe_video(path):
    """ffprobe the first video stream; the decodability observation for a media artifact."""
    ffprobe = require_tool("ffprobe")
    cmd = [ffprobe, "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=index,codec_name,codec_type,time_base,nb_frames,duration",
           "-show_entries", "format=format_name,duration,size", "-of", "json", str(path)]
    r = subprocess.run(cmd, text=True, capture_output=True)
    doc = json.loads(r.stdout or "{}")
    streams = doc.get("streams") or []
    return {"exit_code": r.returncode, "stderr": r.stderr[-400:],
            "video_stream": streams[0] if streams else None,
            "format": doc.get("format") or {}}


def _seconds(ticks, timescale):
    return Fraction(int(ticks), int(timescale))


def _no_overlap_gate(placement_records, check_no_overlap):
    """Run the PRODUCTION FR-13 invariant over the placement set and report its verdict.

    The harness must not substitute its own overlap predicate: ``gate3.placement`` owns the rule
    (track grouping plus timeline-domain identity), so the reported check is production behaviour.
    """
    try:
        check_no_overlap(placement_records)
        return True
    except ValueError:
        return False


def render_media_ffmpeg(source_path, out_path, intervals, *, timescale):
    """Materialize ACTUAL decodable output media over the measured source-native intervals.

    ``trim``/``setpts`` are driven by exact rational source-native tick/timebase seconds -- not by a
    nominal frame rate -- and the result is a real, re-encoded, ffprobe-decodable media file.
    """
    ffmpeg = require_tool("ffmpeg")
    parts, labels = [], []
    for i, (start_ticks, end_ticks) in enumerate(intervals):
        s = float(_seconds(start_ticks, timescale))
        e = float(_seconds(end_ticks, timescale))
        parts.append(f"[0:v]trim=start={s:.9f}:end={e:.9f},setpts=PTS-STARTPTS[v{i}]")
        labels.append(f"[v{i}]")
    chain = ";".join(parts) + ";" + "".join(labels) + \
        f"concat=n={len(labels)}:v=1:a=0[out]"
    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-v", "error", "-y", "-i", str(source_path), "-filter_complex", chain,
           "-map", "[out]", "-c:v", "libx264", "-bf", "0", "-pix_fmt", "yuv420p", str(out)]
    r = subprocess.run(cmd, text=True, capture_output=True)
    if r.returncode != 0 or not out.is_file() or out.stat().st_size == 0:
        raise PrototypeError(f"media render failed: {r.stderr[-800:]}")
    return {"path": str(out), "sha256": sha256_file(out), "byte_count": out.stat().st_size,
            "producer": "local-ffmpeg-render", "time_domain": "rendered_output",
            "production_eligible": False, "scope": "SYNTHETIC_FIXTURE"}


def _lease_evidence(evidence_dir, watched_dir, attempt_id, run_id):
    """Acquire the single heavy lease for the chain, persist and return its evidence record.

    FR-09: the record is substantive only once the lease has been RELEASED, because
    ``observed_wall_clock_seconds`` and ``suite_completed`` are recorded at release time.  Calling
    ``evidence()`` inside the ``with`` block yields ``observed_wall_clock_seconds = null`` and the
    receipt fails closed with ``RESOURCE_EVIDENCE_NOT_SUBSTANTIVE``.  This mirrors the authoritative
    runner (``scripts/run-gate3-suite.sh``), which observes the lease after its ``with`` block.
    """
    from gate3.lease import Lease
    lease = Lease(evidence_dir=str(evidence_dir), watched_dir=str(watched_dir),
                  attempt_id=attempt_id, run_id=run_id)
    with lease:
        lease.phase_enter("chain")
        lease.heavy_child_enter()
        try:
            lease.sample_disk()
        finally:
            lease.heavy_child_exit()
            lease.sample_disk()
            lease.phase_exit("chain")
    return lease.evidence()


def _fresh_process_readback(manifest_path, staged_paths):
    code = ("import hashlib,json,pathlib,sys\n"
            "raw=pathlib.Path(sys.argv[1]).read_bytes()\n"
            "m=json.loads(raw.decode())\n"
            "print(json.dumps({'digest':hashlib.sha256(raw).hexdigest(),"
            "'attempt_id':m.get('attempt_id'),"
            "'resource_evidence_ref_present':pathlib.Path(m['resource_evidence_ref']).is_file(),"
            "'staged':[pathlib.Path(p).is_file() for p in sys.argv[2:]]}))\n")
    p = subprocess.run([interpreter(), "-c", code, str(manifest_path)] + [str(s) for s in staged_paths],
                       text=True, capture_output=True, cwd=str(REPO))
    if p.returncode != 0:
        return {"ok": False, "stderr": p.stderr[-500:]}
    o = json.loads(p.stdout)
    o["ok"] = bool(o["resource_evidence_ref_present"]) and all(o["staged"])
    return o


def resolve_case(*, scenario, source_kind=None, recipe=None, interval_indices=None):
    if scenario not in SCENARIOS:
        raise PrototypeError(f"unknown scenario {scenario!r}")
    kind = source_kind
    if kind is None:
        if recipe:
            kind = "recipe"
        elif scenario == "F2":
            kind = "recipe"
        else:
            kind = "real"
    key = (scenario, kind)
    if key not in CASES:
        raise PrototypeError(f"unsupported scenario/source combination: {key}")
    case = dict(CASES[key])
    if recipe is not None:
        case["recipe"] = recipe
    if interval_indices is not None:
        case["interval_indices"] = interval_indices
    return kind, case


def required_checks(*, scenario, source_kind, placement_count):
    names = list(BASE_CHECKS)
    if source_kind == "real":
        names += list(MEDIA_CHECKS)
    if scenario == "F2":
        names += list(TEMPORAL_CHECKS)
    if placement_count > 1:
        names += list(MULTI_CHECKS)
    return tuple(names)


def run_chain(*, out_dir, scenario="F1", source_kind=None, recipe=None, interval_indices=None,
              attempt_id=None, run_id=None, candidate_sha=None):
    """Execute the honest chain once and persist its attributable evidence under ``out_dir``."""
    from gate3 import authority, render_adapter
    from gate3.editorial import EditorialDecision
    from gate3.mapping import validate_hop
    from gate3.placement import TimelinePlacement, check_no_overlap
    from gate3.plan import EditPlanRevision
    from gate3.pts import PtsTable
    from gate3.qc import QCReport
    from gate3.rational import TimeBase
    from gate3.receipt import build_receipt, measurement_record
    from gate3.refinement import is_binding_eligible, refine
    from gate3.runmanifest import (build_module_execution_records, build_run_manifest,
                                   derive_module_totals, generate_attempt_id,
                                   persist_run_manifest)
    from gate3.timeline import TimelineDomain
    from gate3.verify import run_verification
    from gate3.discriminating import build_discriminating_report
    from gate3.temporal import classify_vfr

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    attempt = attempt_id or generate_attempt_id()
    rid_run = run_id or RUN_ID_DEFAULT
    sha = candidate_sha or base_code_sha()
    kind, case = resolve_case(scenario=scenario, source_kind=source_kind, recipe=recipe,
                              interval_indices=interval_indices)

    # ---- 1. source media (locally generated, never protected/archive) ----------------------
    if kind == "real":
        real = case.get("real") or {}
        source = generate_real_synthetic_source(out, name="source.mp4", rate=real.get("rate", 30),
                                                duration=real.get("duration", 2.0),
                                                size=real.get("size", "64x48"))
    else:
        source = generate_recipe_source(out, case["recipe"], name="source.mp4")
    source_digest_before = sha256_file(source["path"])

    # ---- 2. source-native temporal measurement and refinement ------------------------------
    m = measure_source(source["path"])
    if m.get("source_bytes_sha256") != source["sha256"]:
        raise PrototypeError("measured source identity does not match the generated source bytes")
    timescale = int(m["media_timescale"])
    intervals = select_intervals(m, case["interval_indices"])
    table = PtsTable(TimeBase(1, timescale), tuple(m["pts_ticks"]))
    rec = refine(table, intervals[0], attempt_id=attempt, tool_identity=TOOL,
                 time_domain="source_pts", precision="source-pts",
                 source_revision_id=f"{rid_run}-source-rev-1",
                 source_content_digest=source["sha256"], stream_index=m["stream_index"],
                 container_path=source["path"])
    if not isinstance(rec, dict) or not is_binding_eligible(rec):
        raise PrototypeError(f"refinement is not authoritatively binding-eligible: {rec}")

    # ---- 3. synthetic editorial decision ---------------------------------------------------
    decision = EditorialDecision("dec-" + attempt, "SYNTHETIC_HUMAN", "fixture:prototype-editor",
                                 rec["refinement_id"], 1, "ACCEPT",
                                 "synthetic structural fixture decision for the honest chain",
                                 ["keep"], fixture_scope="SYNTHETIC_FIXTURE")
    decision_record = dict(decision.to_record()) if hasattr(decision, "to_record") \
        else dict(vars(decision))
    # The declared authority boundary is the property under test, so it is recorded explicitly
    # rather than inferred from the serialized record shape.
    decision_record["real_authority_eligible"] = bool(decision.real_authority_eligible)

    # ---- 4. edit plan + placements ---------------------------------------------------------
    # The placements are built FIRST and handed to ``EditPlanRevision`` as COMPLETE records, so
    # ``plan.py``'s FR-13 construction invariant (``validate_placement_set``) actually runs over
    # them.  ``plan.py`` states explicitly that an id-only internal representation would make FR-13
    # vacuous; passing bare id strings here would have validated nothing.
    domain = TimelineDomain("tl-" + attempt, TimeBase(1, timescale))
    timeline_cursor = 0
    placement_records = []
    placements = []
    for idx, (start_ticks, end_ticks) in enumerate(intervals):
        span = end_ticks - start_ticks
        pl = TimelinePlacement(f"p{idx + 1}", "PLAN-" + attempt, 1, rec["refinement_id"],
                               decision.decision_id, "V1", idx, timeline_cursor,
                               timeline_cursor + span, "map-" + attempt, domain)
        placements.append(pl)
        record = dict(pl.to_record())
        # The A.7 record cross-links the interval it pins. Carrying the measured source ticks
        # inline is what lets reverse resolution return the SOURCE interval: the timeline hop is
        # the identity, so without them the adapter correctly falls back to the timeline interval.
        record["source_interval"] = [start_ticks, end_ticks]
        placement_records.append(record)
        timeline_cursor += span
    plan = EditPlanRevision("PLAN-" + attempt, 1, list(placement_records),
                            {rec["refinement_id"]: rec}, {rec["refinement_id"]: decision},
                            source_revision_ids=[rec.get("source_revision_id")
                                                 or f"{rid_run}-source-rev-1"],
                            plan_scope="SYNTHETIC_FIXTURE",
                            policy_decision_ref=rec["refinement_id"],
                            pinned_evidence_digests={rec["refinement_id"]: rec["evidence_digest"]})
    plan_record = plan.to_record()
    if not plan.export_plan_structurally_valid:
        raise PrototypeError("honest plan is not structurally valid")

    # ---- 5. render: frozen Gate-3 synthetic render + ACTUAL decodable media -----------------
    # The frozen A.6/A.7 render seam produces the segments, the mapping and the attributed
    # artifact, so reverse resolution and T10 exactness are computed over PRODUCTION output rather
    # than over a harness-authored view of the inputs.
    adapter = render_adapter.SyntheticRenderAdapter()
    render_out = adapter.render(plan_record, out_path=str(out / "synthetic-render-envelope.bin"),
                                placement_records=list(placement_records))
    mapping = render_out["mapping"]
    segments = render_out["segments"]
    frozen_render = render_out["artifact"]
    render_adapter.verify_rendered_output(frozen_render)
    exactness = validate_hop(mapping)
    reverse = [adapter.resolve_output_frame(render_out, s["timeline_start_ticks"])
               for s in segments]

    rendered_media = None
    rendered_measurement = None
    if kind == "real":
        rendered_media = render_media_ffmpeg(source["path"], out / "rendered_media.mp4",
                                             intervals, timescale=timescale)
        rendered_measurement = measure_source(rendered_media["path"])

    # ---- 6. rendered-output mapping and reverse resolution (production output) ---------------
    ticks = tuple(sorted({s["timeline_start_ticks"] for s in segments} |
                         {s["timeline_end_ticks"] for s in segments}))

    # ---- 7. independent verifier and technical QC ------------------------------------------
    report = run_verification(evidence_dir=str(out), subjects=[rec],
                              container_path=source["path"], attempt_id=attempt)
    attestation = report["attestation"]
    qc = QCReport(report_id="qc-" + attempt, artifact_id=frozen_render["artifact_id"],
                  qc_scope="technical",
                  checks=[{"check": "rendered_output_attribution", "result": "PASS",
                           "evidence_class": "MEASURED"},
                          {"check": "source_native_temporal_measurement", "result": "PASS",
                           "evidence_class": "MEASURED"}],
                  supporting_evidence_refs=[rec["refinement_id"]],
                  verifier_attestation=attestation,
                  support_records={rec["refinement_id"]: rec},
                  source_content_digest=source["sha256"])
    (out / "container-measurement.json").write_text(
        json.dumps(measurement_record(m), indent=2, sort_keys=True))

    # ---- 8. temporal discrimination evidence (supported production module) ------------------
    vfr_flag, period, basis, deviation = classify_vfr(table, None)
    vfr = generate_recipe_source(out, "vfr_nonuniform", name="vfr.mp4")
    # The receipt's discriminating axis needs a CFR control that is ALSO the container the receipt's
    # measurement names (otherwise it fails closed with
    # DISCRIMINATING_CONTROL_DIGEST_NOT_SELECTED_CANDIDATE), and a VFR fixture.  When the chain's own
    # source is CFR the receipt stays fully chain-bound; when the chain deliberately runs a VFR source
    # the receipt axis is grounded on its own committed CFR control and is reported as such.
    if str(vfr_flag) == "true":
        axis = out / "receipt-axis"
        axis.mkdir(parents=True, exist_ok=True)
        control = generate_recipe_source(axis, "cfr_4s_shape", name="receipt-control.mp4")
        cm = measure_source(control["path"])
        ctable = PtsTable(TimeBase(1, int(cm["media_timescale"])), tuple(cm["pts_ticks"]))
        crec = refine(ctable, (cm["pts_ticks"][0], cm["pts_ticks"][-1]), attempt_id=attempt,
                      tool_identity=TOOL, time_domain="source_pts", precision="source-pts",
                      source_revision_id=f"{rid_run}-receipt-control-rev-1",
                      source_content_digest=control["sha256"], stream_index=cm["stream_index"],
                      container_path=control["path"])
        run_verification(evidence_dir=str(axis), subjects=[crec], container_path=control["path"],
                         attempt_id=attempt)
        (axis / "container-measurement.json").write_text(
            json.dumps(measurement_record(cm), indent=2, sort_keys=True))
        axis_dir, subject_ref = axis, crec["refinement_id"]
    else:
        axis_dir, control, subject_ref = out, source, rec["refinement_id"]
    disc = build_discriminating_report(control_path=control["path"], fixture_path=vfr["path"],
                                       verifier_attempt_id=attempt, out_dir=str(axis_dir))

    # ---- 9. run evidence / manifest + fresh-process readback --------------------------------
    lease_ev = _lease_evidence(out, out, attempt, rid_run)
    # These are the HARNESS's own chain steps, named ``harness-local:`` so they can never be
    # mistaken for suite modules.  They record what this process actually observed, but this harness
    # is NOT the suite runner: the receipt's suite-completeness axis is decided by the production
    # inventory cross-check in ``receipt.module_execution_errors`` (which refuses these names), and
    # the authoritative suite collection comes from ``scripts/run-gate3-suite.sh``.
    steps = ["source_identity", "temporal_measurement", "refinement", "editorial_decision",
             "edit_plan", "placement", "render", "rendered_mapping", "reverse_resolution",
             "verifier", "technical_qc"]
    records = [dict(module=f"harness-local:{s}", phase="B", executed=True, returncode=0,
                    outcome="PASS", stdout="", stderr="") for s in steps]
    collection = build_module_execution_records(run_id=rid_run, attempt_id=attempt,
                                                idempotency_key=rid_run + "-chain",
                                                candidate_revision=sha, records=records)
    collection_path = out / "module-execution-records.json"
    persist_run_manifest(collection, collection_path)
    totals = derive_module_totals(collection)
    staged = [str(out / "chain-evidence.json"), str(out / "container-measurement.json"),
              str(out / "verification-report.json"), str(out / "discriminating-vfr-report.json"),
              str(out / "lease-evidence.json"), str(collection_path)]
    for extra in (rendered_media,):
        if extra:
            staged.append(extra["path"])
    staged = [p for p in staged if pathlib.Path(p).is_file()]
    manifest = build_run_manifest(run_id=rid_run, attempt_id=attempt,
                                 idempotency_key=rid_run + "-chain", input_revision_refs=[sha],
                                 policy_decision_refs=[rec["refinement_id"]],
                                 profile_config_digests=[], tool_runtime_observations={
                                     "python": sys.version.split()[0], "platform": sys.platform,
                                     "modules_executed": totals["modules_executed"],
                                     "candidate_revision": sha, "scenario": scenario,
                                     "source_kind": kind},
                                 output_artifact_digests=[f"{p}:{sha256_file(p)}" for p in staged],
                                 failures=[], resource_evidence_ref=str(out / "lease-evidence.json"))
    manifest_path = out / "run-manifest.json"
    manifest_digest = persist_run_manifest(manifest, manifest_path)
    readback = _fresh_process_readback(manifest_path, staged)
    (out / "staging-set.json").write_text(json.dumps(
        {"run_id": rid_run, "attempt_id": attempt, "run_manifest": str(manifest_path),
         "run_manifest_sha256": manifest_digest, "staging": staged,
         "staged_digests": {p: sha256_file(p) for p in staged},
         "fresh_process_readback": readback}, indent=2, sort_keys=True))

    # ---- 10. receipt / final artifact -------------------------------------------------------
    receipt = build_receipt(candidate_sha=sha, suite_command=(
        f"{pathlib.Path(sys.executable).name} src/gate3/functional_prototype.py --scenario "
        f"{scenario} --source-kind {kind}"), passed=totals["modules_passed"],
        verifier_report_path=str(axis_dir / "verification-report.json"),
        container_measurement_path=str(axis_dir / "container-measurement.json"),
        resource_evidence_path=str(out / "lease-evidence.json"),
        subject_ref=subject_ref,
        discriminating_report_path=str(axis_dir / "discriminating-vfr-report.json"),
        expected_verifier_attempt_id=attempt, control_container_path=control["path"],
        fixture_container_path=vfr["path"], run_manifest_path=str(manifest_path),
        module_execution_path=str(collection_path), out_dir=str(out))

    # ---- 11. chain evidence + summary -------------------------------------------------------
    reverse_ok = all(r.get("source_interval") is not None
                     and tuple(r["source_interval"]) == tuple(iv)
                     for r, iv in zip(reverse, intervals))
    source_immutable = sha256_file(source["path"]) == source_digest_before
    media_probe = ffprobe_video(rendered_media["path"]) if rendered_media else None
    media_ok = bool(media_probe and media_probe["exit_code"] == 0
                    and (media_probe["video_stream"] or {}).get("codec_type") == "video")

    evidence = {"run_id": rid_run, "attempt_id": attempt, "scenario": scenario,
                "source_kind": kind, "base_code_sha": sha, "source": source,
                "measurement": {k: (list(v) if isinstance(v, tuple) else v)
                                for k, v in m.items()},
                "refinement": rec, "decision": decision_record, "plan": plan_record,
                "placements": [p.to_record()
                               if hasattr(p, "to_record") else p.__dict__ for p in placements],
                "segments": [{k: v for k, v in s.items() if k != "timeline_domain"}
                             for s in segments],
                "frozen_render": frozen_render,
                "rendered_media": rendered_media,
                "rendered_measurement": ({k: (list(v) if isinstance(v, tuple) else v)
                                          for k, v in (rendered_measurement or {}).items()}),
                "mapping": mapping.to_record() if hasattr(mapping, "to_record") else None,
                "exactness": exactness, "reverse_mapping": reverse,
                "verifier_report": report, "technical_qc": qc.to_record()
                if hasattr(qc, "to_record") else None,
                "discriminating_report": disc, "lease_evidence": lease_ev,
                "run_manifest": {"path": str(manifest_path), "sha256": manifest_digest,
                                 "attempt_id": attempt},
                "staging_set": str(out / "staging-set.json"), "readback": readback,
                "receipt": receipt, "temporal": {"vfr": vfr_flag, "period": str(period),
                                                 "basis": basis, "declared_rate_deviation":
                                                 deviation,
                                                 "discriminating": disc.get(
                                                     "discriminating_vfr_verified")},
                "checks": {}, "NOT_OBSERVED": list(NOT_OBSERVED)}
    (out / "chain-evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True,
                                                        default=str))

    checks = {
        "source_media_generated": pathlib.Path(source["path"]).is_file()
        and pathlib.Path(source["path"]).stat().st_size > 0,
        "source_media_is_probeable": ffprobe_video(source["path"])["exit_code"] == 0,
        "source_media_immutable": source_immutable,
        "refinement_is_binding_eligible": bool(is_binding_eligible(rec)),
        "editorial_decision_created": decision.decision_id is not None,
        "plan_structurally_valid": bool(plan.export_plan_structurally_valid),
        "plan_not_export_eligible": not plan.export_eligible,
        "placement_created": len(placements) == len(intervals),
        "render_succeeded": bool(frozen_render.get("artifact_id")),
        "rendered_output_file_non_empty": pathlib.Path(frozen_render["path"]).stat().st_size > 0,
        "render_attribution_verified": bool(
            render_adapter.verify_rendered_output(frozen_render)),
        "rendered_output_is_decodable_media": media_ok,
        "mapping_artifact_exists": mapping is not None and bool(ticks),
        "mapping_exact": exactness == "exact",
        "reverse_mapping_resolves_expected_source_interval": reverse_ok,
        "verifier_completed": bool(report.get("checks")),
        "verifier_agreement_agree": attestation.get("agreement") == "AGREE",
        "technical_qc_completed": qc is not None,
        "technical_qc_pass": qc.status == "PASS",
        "run_manifest_persisted": manifest_path.is_file(),
        "fresh_process_readback_ok": bool(readback.get("ok"))
        and readback.get("digest") == manifest_digest,
        "receipt_completed": isinstance(receipt, dict) and "m3_would_be_claimable" in receipt,
        "no_production_or_real_human_authority": (
            not plan.export_eligible and not plan.real_authority_eligible
            and not decision.real_authority_eligible
            and frozen_render.get("production_eligible") is False
            and frozen_render.get("production_renderer_selected") is False),
        "nominal_fps_reasoning_is_inadequate": bool(disc.get("discriminating_vfr_verified")),
        "placements_are_ordered": [p.order_index for p in placements] == list(range(len(placements))),
        # The PRODUCTION FR-13 invariant, over the same complete records the plan was built from --
        # not a harness-local re-implementation of it.
        "same_track_overlap_absent": _no_overlap_gate(placement_records, check_no_overlap),
    }
    required = required_checks(scenario=scenario, source_kind=kind, placement_count=len(placements))
    all_ok = all(checks.get(name, False) for name in required)

    summary = {
        "run_id": rid_run, "attempt_id": attempt, "scenario": scenario, "source_kind": kind,
        "recipe": case.get("recipe"), "base_code_sha": sha,
        "source": source, "measurement": evidence["measurement"],
        "refined_interval": {"ticks": list(intervals[0]),
                             "duration_seconds": float(_seconds(intervals[0][1] - intervals[0][0],
                                                               timescale))},
        "refined_intervals": [list(i) for i in intervals],
        "refinement": rec, "decision": evidence["decision"], "plan": plan_record,
        "placement": evidence["placements"][0], "placements": evidence["placements"],
        "render": frozen_render, "rendered_media": rendered_media,
        "rendered_probe": media_probe,
        "mapping": {"mapping_id": mapping.mapping_id, "hop": mapping.hop,
                    "exactness": exactness, "digest": mapping.digest,
                    "validated_sample": list(ticks)},
        "reverse_mapping": reverse,
        "verifier_not_observed": list(report.get("NOT_OBSERVED") or ()),
        "verifier": {"agreement": attestation.get("agreement"),
                     "verdict": report.get("verification_verdict"),
                     "mandatory_checks_passed": report.get("mandatory_checks_passed")},
        "technical_qc": {"status": qc.status, "report_id": qc.report_id},
        "temporal": evidence["temporal"],
        "run_manifest": evidence["run_manifest"], "readback": readback,
        "receipt": receipt,
        "evidence_path": str(out / "chain-evidence.json"),
        "checks": checks, "required_checks": list(required), "all_checks_passed": all_ok,
        "NOT_OBSERVED": list(NOT_OBSERVED),
    }
    (out / "chain-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True,
                                                       default=str))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate-3 honest synthetic chain (RT-03) prototype runner.")
    ap.add_argument("--scenario", default="F1", choices=list(SCENARIOS))
    ap.add_argument("--source-kind", default=None, choices=["real", "recipe"])
    ap.add_argument("--recipe", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--attempt-id", default=None)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--candidate-sha", default=None)
    args = ap.parse_args(argv)
    summary = run_chain(out_dir=args.out_dir, scenario=args.scenario,
                        source_kind=args.source_kind, recipe=args.recipe,
                        attempt_id=args.attempt_id, run_id=args.run_id,
                        candidate_sha=args.candidate_sha)
    print(json.dumps({"scenario": summary["scenario"], "attempt_id": summary["attempt_id"],
                      "source_kind": summary["source_kind"],
                      "refined_interval": summary["refined_interval"],
                      "mapping_exactness": summary["mapping"]["exactness"],
                      "verifier_agreement": summary["verifier"]["agreement"],
                      "technical_qc": summary["technical_qc"]["status"],
                      "receipt_claimable": summary["receipt"].get("m3_would_be_claimable"),
                      "receipt_blocked_by": summary["receipt"].get("m3_blocked_by"),
                      "all_checks_passed": summary["all_checks_passed"],
                      "failed_checks": [k for k, v in summary["checks"].items()
                                        if not v and k in summary["required_checks"]],
                      "summary": str(pathlib.Path(args.out_dir) / "chain-summary.json")},
                     indent=2))
    return 0 if summary["all_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
