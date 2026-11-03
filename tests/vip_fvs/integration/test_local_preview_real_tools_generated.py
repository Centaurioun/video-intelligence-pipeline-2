"""Adapter-bound lifecycle coverage with generated media and real local tools."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import copy
import subprocess
from dataclasses import replace

import pytest

from tests.vip_fvs.unit.test_review_bundle import payload
from tests.vip_fvs.unit.test_real_plan import _accept, _bundle
from vip_fvs.human_decision import create_human_decision
from vip_fvs.real_plan import (RealPlanSelection, build_real_edit_plan, build_real_edit_plan_from_selections,
                               build_real_edit_plan_from_selections_with_lineage, rebind_real_plan_selections)
from vip_fvs.review_bundle import ReviewBundle
from vip_fvs.local_preview import (LocalPreviewAdapter, PreviewAuthorization, PreviewRefusal, PreviewSourcePin,
                                   tool_configuration_digest, placement_set_digest, source_set_digest,
                                   composition_digest, canonical_digest)
from gate3.container import parse_iso_bmff_timing
from gate3.pts import PtsTable
from gate3.rational import TimeBase
from gate3.refinement import refine
from gate3.authority import RECORD_KIND_REFINEMENT, evidence_digest as refinement_evidence_digest
from tests.vip_fvs.unit.test_real_source_temporal_authority import _identity_for_measured_request


FFMPEG = Path("/opt/homebrew/bin/ffmpeg")
FFPROBE = Path("/opt/homebrew/bin/ffprobe")


def _authorization(artifacts, source: Path, output_root: Path) -> PreviewAuthorization:
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    probe = {"sha256": hashlib.sha256(FFPROBE.read_bytes()).hexdigest()}
    ffmpeg = {"sha256": hashlib.sha256(FFMPEG.read_bytes()).hexdigest()}
    refinement = artifacts.plan.pinned_refinements[artifacts.mapping.source_refinement_id]
    return PreviewAuthorization(
        authorization_id="generated-adapter-real-tools-v1",
        policy_identity="local-generated-integration",
        scope="NON_PRODUCTION_PREVIEW",
        plan_digest=artifacts.plan.digest,
        source_revision_id=refinement["source_revision_id"],
        source_sha256=source_sha,
        placement_digest=hashlib.sha256(json.dumps(
            artifacts.placement.to_record(), sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest(),
        mapping_digest=artifacts.mapping.record_digest,
        output_root=output_root,
        ffprobe_tool_digest=probe["sha256"],
        ffmpeg_tool_digest=ffmpeg["sha256"],
        tool_config_digest=tool_configuration_digest(probe, ffmpeg),
        expires_at="2099-01-01T00:00:00Z",
    )


def _multi_authorization(artifacts, selections, source_paths, output_root: Path) -> PreviewAuthorization:
    checked = rebind_real_plan_selections(artifacts, selections)
    placements, mappings = artifacts.placements, artifacts.mappings
    placement_records = tuple({"order_index": i, "placement_digest": canonical_digest(p.to_record()),
                               "mapping_digest": m.record_digest}
                              for i, (p, m) in enumerate(zip(placements, mappings)))
    pins = tuple(PreviewSourcePin(s.bundle.payload["source"]["source_revision_id"],
                                  hashlib.sha256(Path(source_paths[s.bundle.payload["source"]["source_revision_id"]]).read_bytes()).hexdigest(),
                                  Path(source_paths[s.bundle.payload["source"]["source_revision_id"]]).stat().st_size)
                 for s in checked)
    composition = []
    for i, (selection, placement, mapping, pin) in enumerate(zip(checked, placements, mappings, pins)):
        ref = artifacts.plan.pinned_refinements[mapping.source_refinement_id]
        interval = ref["source_pts_interval"]
        composition.append({"order_index": i, "placement_id": placement.placement_id,
            "placement_digest": canonical_digest(placement.to_record()), "mapping_digest": mapping.record_digest,
            "source_revision_id": pin.source_revision_id, "source_sha256": pin.source_sha256,
            "stream_index": ref["selected_stream_index"], "source_timebase": dict(ref["timebase"]),
            "source_pts_start": interval["start"], "source_pts_end_exclusive": interval["end"],
            "timeline_start_ticks": placement.timeline_start_ticks, "timeline_end_ticks": placement.timeline_end_ticks})
    probe = {"sha256": hashlib.sha256(FFPROBE.read_bytes()).hexdigest()}
    ffmpeg = {"sha256": hashlib.sha256(FFMPEG.read_bytes()).hexdigest()}
    domain = {"domain_id": placements[0].timeline_domain.domain_id,
              "time_base": {"num": placements[0].timeline_domain.time_base.num,
                            "den": placements[0].timeline_domain.time_base.den}}
    return PreviewAuthorization(
        authorization_id="generated-adapter-real-tools-v2", policy_identity="local-generated-integration",
        scope="NON_PRODUCTION_PREVIEW", plan_digest=artifacts.plan.digest, source_revision_id="",
        source_sha256="", placement_digest="", mapping_digest="", output_root=output_root,
        ffprobe_tool_digest=probe["sha256"], ffmpeg_tool_digest=ffmpeg["sha256"],
        tool_config_digest=tool_configuration_digest(probe, ffmpeg, multi_placement=True), expires_at="2099-01-01T00:00:00Z",
        schema_version="v2", placement_set_digest=placement_set_digest(artifacts.plan.digest, placement_records),
        source_set_digest=source_set_digest(pins), ordered_source_pins=pins,
        composition_digest=composition_digest(artifacts.plan.digest, domain, composition),
        review_bundle_record_digests=tuple(s.bundle.record_digest for s in checked),
        review_bundle_dependency_digests=tuple(s.bundle.dependency_digest for s in checked),
        human_decision_digests=tuple(s.decision.record_digest for s in checked))


def _generated_selection(tmp_path: Path, label: str, revision_id: str, *, target_revision: int) -> tuple[RealPlanSelection, Path]:
    source = tmp_path / f"{label}.mp4"
    subprocess.run([str(FFMPEG), "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=160x90:rate=25",
                    "-frames:v", "3", "-c:v", "mpeg4", "-g", "3", "-pix_fmt", "yuv420p",
                    "-video_track_timescale", "1000", str(source)], check=True, capture_output=True)
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    raw_probe = subprocess.run([str(FFPROBE), "-v", "error", "-of", "json", "-show_streams", "-show_format",
                                "-show_frames", str(source)], check=True, capture_output=True).stdout
    probe_payload = json.loads(raw_probe)
    pts = tuple(sorted({int(frame["best_effort_timestamp"]) for frame in probe_payload["frames"]
                        if frame.get("stream_index") == 0 and frame.get("best_effort_timestamp") is not None}))
    assert pts == (0, 40, 80)
    probe = tmp_path / f"{label}-probe.json"; probe.write_bytes(raw_probe)
    probe_digest = hashlib.sha256(raw_probe).hexdigest()
    request_identity = _identity_for_measured_request({}, source_revision_id=revision_id,
        source_locator=str(source.resolve()), source_digest=source_sha, stream_index=0, start_pts=40, end_pts=80)
    refinement = refine(PtsTable(TimeBase(1, 1000), pts), (40, 80), attempt_id=request_identity["producer_attempt_id"],
        tool_identity={"tool": "generated-fixture"}, time_domain="source_pts", precision="source-pts",
        source_revision_id=revision_id, source_content_digest=source_sha, stream_index=0,
        container_path=str(source), request_identity=request_identity)
    assert not refinement.get("blocked")
    refinement["source_probe_artifact_ref"] = str(probe); refinement["source_probe_digest"] = probe_digest
    refinement["evidence_digest"] = refinement_evidence_digest(RECORD_KIND_REFINEMENT, refinement)
    evidence = tmp_path / f"{label}-refinement.json"
    evidence.write_text(json.dumps(refinement, sort_keys=True, separators=(",", ":")) + "\n")
    raw = copy.deepcopy(payload())
    raw["source"].update({"source_sha256": source_sha, "source_byte_count": source.stat().st_size,
        "source_revision_id": revision_id, "probe_artifact_ref": str(probe), "probe_digest": probe_digest,
        "timebase": {"num": 1, "den": 1000}})
    raw["generation"]["attempt_id"] = refinement["attempt_id"]
    raw["refinement"].update({"refinement_id": refinement["refinement_id"], "source_revision_id": revision_id,
        "selected_stream_index": 0, "source_pts_interval": {"start": 40, "end": 80,
        "time_domain": "source_pts", "endpoint_semantics": "half_open"}, "timebase": {"num": 1, "den": 1000},
        "attempt_id": refinement["attempt_id"], "evidence_artifact_ref": str(evidence),
        "evidence_digest": refinement["evidence_digest"]})
    bundle = ReviewBundle.create(raw, run_id=f"{label}-run", bundle_id=f"{label}-bundle",
                                 created_at="2026-10-06T12:00:00Z")
    decision = create_human_decision(bundle=bundle, decision_id=f"{label}-decision", principal_kind="human",
        principal_ref="human:test", decision_class="ACCEPT", rationale="Generated local preview fixture.",
        target_plan_revision=target_revision)
    return RealPlanSelection(bundle, decision), source


def _multi_plan_fixture(tmp_path: Path):
    first, source_a = _generated_selection(tmp_path, "generated-multi-a", "rev-generated-multi-a", target_revision=2)
    second, source_b = _generated_selection(tmp_path, "generated-multi-b", "rev-generated-multi-b", target_revision=2)
    prior = build_real_edit_plan_from_selections(
        [RealPlanSelection(first.bundle, _accept(first.bundle, decision_id="generated-multi-prior"))],
        plan_id="generated-multi-plan", plan_revision=1)
    selections = [RealPlanSelection(first.bundle, first.decision, timeline_start_ticks=0),
                  RealPlanSelection(second.bundle, second.decision, timeline_start_ticks=40)]
    artifacts = build_real_edit_plan_from_selections_with_lineage(
        selections, plan_id="generated-multi-plan", plan_revision=2, prior_revision=prior.plan)
    source_paths = {"rev-generated-multi-a": source_a, "rev-generated-multi-b": source_b}
    output_root = tmp_path / "generated-multi-output"
    authorization = _multi_authorization(artifacts, selections, source_paths, output_root)
    return artifacts, selections, source_paths, authorization


def test_two_placement_generated_plan_preview_is_supported(tmp_path: Path):
    """A generated, sealed two-placement successor reaches the preview renderer."""
    artifacts, selections, source_paths, authorization = _multi_plan_fixture(tmp_path)
    preview = LocalPreviewAdapter().render_plan_preview(
        artifacts, authorization=authorization,
        source_paths=source_paths, selections=selections,
        output_root=authorization.output_root, ffprobe_executable=FFPROBE,
        ffmpeg_executable=FFMPEG, producer_attempt_id="generated-multi-plan-producer",
    )
    assert preview.output_path.is_file()
    assert preview.schema_version == "v2"
    assert preview.output_video_stream_count == 1
    assert preview.output_timebase_num == 1 and preview.output_timebase_den == 1000
    assert preview.output_duration_ticks == 80
    assert len(preview.ordered_inputs) == 2
    assert preview.production_eligible is False and preview.export_eligible is False


@pytest.mark.parametrize("selection_case", ["missing", "extra", "duplicate", "reordered"])
def test_multi_preview_rejects_selection_cardinality_and_order(tmp_path: Path, selection_case: str):
    artifacts, selections, source_paths, authorization = _multi_plan_fixture(tmp_path)
    if selection_case == "missing": supplied = selections[:1]
    elif selection_case == "extra": supplied = [*selections, selections[0]]
    elif selection_case == "duplicate": supplied = [selections[0], selections[0]]
    else: supplied = list(reversed(selections))
    with pytest.raises(PreviewRefusal, match="REAL_PLAN_LINEAGE_MISMATCH|SOURCE_REVISION_SET_MISMATCH"):
        LocalPreviewAdapter().render_plan_preview(artifacts, authorization=authorization,
            source_paths=source_paths, selections=supplied, output_root=authorization.output_root,
            ffprobe_executable=FFPROBE, ffmpeg_executable=FFMPEG)


def test_multi_preview_rejects_alternate_sealed_decision_with_same_projection(tmp_path: Path):
    artifacts, selections, source_paths, authorization = _multi_plan_fixture(tmp_path)
    original = selections[0]
    alternate = create_human_decision(bundle=original.bundle, decision_id="generated-multi-a-alternate",
        principal_kind="human", principal_ref="human:test", decision_class="ACCEPT",
        rationale=original.decision.payload["rationale"], target_plan_revision=2,
        supersedes="f" * 64)
    assert alternate.payload["decision_class"] == original.decision.payload["decision_class"]
    assert alternate.record_digest != original.decision.record_digest
    supplied = [RealPlanSelection(original.bundle, alternate, timeline_start_ticks=0), selections[1]]
    with pytest.raises(PreviewRefusal, match="REAL_PLAN_LINEAGE_MISMATCH"):
        LocalPreviewAdapter().render_plan_preview(artifacts, authorization=authorization,
            source_paths=source_paths, selections=supplied, output_root=authorization.output_root,
            ffprobe_executable=FFPROBE, ffmpeg_executable=FFMPEG)


def test_multi_preview_rejects_alternate_bundle_record_with_same_dependency_projection(tmp_path: Path):
    artifacts, selections, source_paths, authorization = _multi_plan_fixture(tmp_path)
    original = selections[0]
    altered_payload = original.bundle.payload
    altered_payload["presentation"]["start_seconds"] = 0.041
    alternate_bundle = ReviewBundle.create(altered_payload, run_id=altered_payload["run_id"],
        bundle_id=altered_payload["bundle_id"], created_at=altered_payload["created_at"])
    alternate_decision = create_human_decision(bundle=alternate_bundle,
        decision_id=original.decision.payload["decision_id"], principal_kind="human",
        principal_ref=original.decision.payload["principal_ref"], decision_class="ACCEPT",
        rationale=original.decision.payload["rationale"], target_plan_revision=2)
    assert alternate_bundle.dependency_digest == original.bundle.dependency_digest
    assert alternate_bundle.record_digest != original.bundle.record_digest
    assert alternate_decision.record_digest != original.decision.record_digest
    supplied = [RealPlanSelection(alternate_bundle, alternate_decision, timeline_start_ticks=0), selections[1]]
    with pytest.raises(PreviewRefusal, match="REAL_PLAN_LINEAGE_MISMATCH"):
        LocalPreviewAdapter().render_plan_preview(artifacts, authorization=authorization,
            source_paths=source_paths, selections=supplied, output_root=authorization.output_root,
            ffprobe_executable=FFPROBE, ffmpeg_executable=FFMPEG)


def test_multi_preview_rejects_authorization_record_pin_mismatch(tmp_path: Path):
    artifacts, selections, source_paths, authorization = _multi_plan_fixture(tmp_path)
    changed = replace(authorization, review_bundle_record_digests=("0" * 64, *authorization.review_bundle_record_digests[1:]),
                      record_digest="")
    with pytest.raises(PreviewRefusal, match="SEALED_RECORD_PIN_MISMATCH"):
        LocalPreviewAdapter().render_plan_preview(artifacts, authorization=changed,
            source_paths=source_paths, selections=selections, output_root=changed.output_root,
            ffprobe_executable=FFPROBE, ffmpeg_executable=FFMPEG)


@pytest.mark.parametrize("lineage_field", ["placement_id", "refinement_id", "decision_id"])
def test_multi_preview_rejects_mismatched_real_plan_lineage(tmp_path: Path, lineage_field: str):
    artifacts, selections, source_paths, authorization = _multi_plan_fixture(tmp_path)
    altered_lineage = replace(artifacts.lineage[0], **{lineage_field: "mismatched-lineage-id"})
    altered_artifacts = replace(artifacts, lineage=(altered_lineage, *artifacts.lineage[1:]))
    with pytest.raises(PreviewRefusal, match="REAL_PLAN_LINEAGE_MISMATCH"):
        LocalPreviewAdapter().render_plan_preview(altered_artifacts, authorization=authorization,
            source_paths=source_paths, selections=selections, output_root=authorization.output_root,
            ffprobe_executable=FFPROBE, ffmpeg_executable=FFMPEG)


def test_multi_preview_rejects_source_changed_after_authorization(tmp_path: Path):
    artifacts, selections, source_paths, authorization = _multi_plan_fixture(tmp_path)
    source_paths["rev-generated-multi-b"].write_bytes(source_paths["rev-generated-multi-b"].read_bytes() + b"changed")
    with pytest.raises(PreviewRefusal, match="REAL_PLAN_LINEAGE_MISMATCH|SOURCE_DIGEST_MISMATCH"):
        LocalPreviewAdapter().render_plan_preview(artifacts, authorization=authorization,
            source_paths=source_paths, selections=selections, output_root=authorization.output_root,
            ffprobe_executable=FFPROBE, ffmpeg_executable=FFMPEG)


@pytest.mark.skipif(not FFMPEG.is_file() or not FFPROBE.is_file(), reason="local ffmpeg/ffprobe unavailable")
def test_adapter_real_tools_generated_media_lifecycle(tmp_path: Path):
    """Exercise source probe, exact PTS cut, publication, cleanup, and rerun refusal."""
    source = tmp_path / "generated-decodable.mp4"
    subprocess.run(
        [str(FFMPEG), "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=160x90:rate=25",
         "-frames:v", "3", "-c:v", "mpeg4", "-g", "3", "-pix_fmt", "yuv420p",
         "-video_track_timescale", "1000", str(source)], check=True, capture_output=True,
    )
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    measured = parse_iso_bmff_timing(source)
    assert measured["source_bytes_sha256"] == source_sha
    assert measured["stream_index"] == 0
    assert measured["media_timescale"] == 1000
    assert tuple(measured["pts_ticks"]) == (0, 40, 80)
    raw_probe = subprocess.run(
        [str(FFPROBE), "-v", "error", "-of", "json", "-show_streams", "-show_format",
         "-show_frames", str(source)], check=True, capture_output=True,
    ).stdout
    observed_probe = json.loads(raw_probe)
    assert observed_probe["streams"][0]["time_base"] == "1/1000"
    observed_pts = tuple(sorted({int(frame["best_effort_timestamp"])
                                 for frame in observed_probe["frames"]
                                 if frame.get("stream_index") == 0 and frame.get("best_effort_timestamp") is not None}))
    assert observed_pts == tuple(measured["pts_ticks"])
    probe = tmp_path / "source-probe.json"
    probe.write_bytes(raw_probe)
    probe_digest = hashlib.sha256(probe.read_bytes()).hexdigest()
    request_identity = _identity_for_measured_request(
        {}, source_revision_id="generated-real-tools-rev", source_locator=str(source.resolve()),
        source_digest=source_sha, stream_index=0, start_pts=40, end_pts=80,
    )
    refinement = refine(
        PtsTable(TimeBase(1, measured["media_timescale"]), tuple(measured["pts_ticks"])), (40, 80),
        attempt_id="attempt-refinement-1", tool_identity={"tool": "generated-fixture"},
        time_domain="source_pts", precision="source-pts", source_revision_id="generated-real-tools-rev",
        source_content_digest=source_sha, stream_index=0, container_path=str(source),
        request_identity=request_identity,
    )
    assert not refinement.get("blocked")
    refinement["source_probe_artifact_ref"] = str(probe)
    refinement["source_probe_digest"] = probe_digest
    refinement["evidence_digest"] = refinement_evidence_digest(RECORD_KIND_REFINEMENT, refinement)
    evidence = tmp_path / "source-refinement.json"
    evidence.write_text(json.dumps(refinement, sort_keys=True, separators=(",", ":")) + "\n")
    evidence_digest = refinement["evidence_digest"]
    raw = copy.deepcopy(payload())
    raw["source"].update({"source_sha256": source_sha, "source_byte_count": source.stat().st_size,
                           "source_revision_id": "generated-real-tools-rev", "probe_artifact_ref": str(probe),
                           "probe_digest": probe_digest, "timebase": {"num": 1, "den": 1000}})
    raw["generation"]["attempt_id"] = refinement["attempt_id"]
    raw["refinement"].update({"refinement_id": refinement["refinement_id"],
                               "source_revision_id": "generated-real-tools-rev",
                               "selected_stream_index": refinement["stream_index"],
                               "source_pts_interval": {"start": refinement["start_ticks"],
                                                       "end": refinement["end_ticks"],
                                                       "time_domain": "source_pts",
                                                       "endpoint_semantics": "half_open"},
                               "timebase": refinement["time_base"],
                               "attempt_id": refinement["attempt_id"],
                               "evidence_artifact_ref": str(evidence), "evidence_digest": evidence_digest})
    bundle = ReviewBundle.create(raw, run_id="generated-real-tools-run", bundle_id="generated-real-tools-bundle",
                                 created_at="2026-09-21T12:00:00Z")
    decision = create_human_decision(bundle=bundle, decision_id="generated-real-tools-decision",
                                     principal_kind="human", principal_ref="human:test",
                                     decision_class="ACCEPT", rationale="Generated adapter lifecycle.", target_plan_revision=1)
    artifacts = build_real_edit_plan(bundle, decision, plan_id="generated-real-tools-plan", plan_revision=1)
    successor_decision = create_human_decision(
        bundle=bundle, decision_id="generated-real-tools-decision-r2", principal_kind="human",
        principal_ref="human:test", decision_class="ACCEPT", rationale="Generated plan revision preview.",
        target_plan_revision=2,
    )
    successor = build_real_edit_plan_from_selections(
        [RealPlanSelection(bundle, successor_decision, timeline_start_ticks=0)],
        plan_id="generated-real-tools-plan", plan_revision=2, prior_revision=artifacts.plan,
    )
    successor_auth = _authorization(successor, source, tmp_path / "successor-preview-output")
    successor_preview = LocalPreviewAdapter().render_plan_preview(
        successor, authorization=successor_auth, source_paths={"generated-real-tools-rev": source},
        output_root=successor_auth.output_root, ffprobe_executable=FFPROBE,
        ffmpeg_executable=FFMPEG, producer_attempt_id="generated-real-tools-plan-producer",
    )
    assert successor_preview.output_path.is_file()
    assert successor_preview.plan_digest == successor.plan_digest
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    output_root = tmp_path / "preview-output"
    authorization = _authorization(artifacts, source, output_root)

    preview = LocalPreviewAdapter().render_preview(
        artifacts, authorization=authorization, source_path=source,
        output_root=output_root, ffprobe_executable=FFPROBE,
        ffmpeg_executable=FFMPEG, producer_attempt_id="generated-real-tools-producer",
    )
    assert preview.output_path.is_file()
    assert preview.source_sha256_before == preview.source_sha256_after == before
    assert preview.source_start_pts == 40 and preview.source_end_pts == 80
    assert preview.output_bytes == preview.output_path.stat().st_size
    assert not list(output_root.glob(".*")), "private staging directory must be cleaned"

    probe = subprocess.run(
        [str(FFPROBE), "-v", "error", "-of", "json", "-show_streams", "-show_format", str(preview.output_path)],
        check=True, capture_output=True, text=True,
    )
    probe_payload = json.loads(probe.stdout)
    videos = [stream for stream in probe_payload["streams"] if stream.get("codec_type") == "video"]
    assert len(videos) == 1
    assert videos[0]["time_base"] == "1/1000"
    assert int(videos[0]["duration_ts"]) == 40

    with pytest.raises(PreviewRefusal, match="OUTPUT_EXISTS"):
        LocalPreviewAdapter().render_preview(
            artifacts, authorization=authorization, source_path=source,
            output_root=output_root, ffprobe_executable=FFPROBE,
            ffmpeg_executable=FFMPEG, producer_attempt_id="generated-real-tools-rerun",
        )
    assert preview.output_path.is_file()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
