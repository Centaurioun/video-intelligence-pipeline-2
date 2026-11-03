"""Local-only tests for the authorization-gated preview adapter.

The runner is an in-memory subprocess double: no ffmpeg, ffprobe, source media,
provider, network, or model is used by this test.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
from dataclasses import replace

import pytest

from tests.vip_fvs.unit.test_real_plan import _bundle
from vip_fvs.human_decision import create_human_decision
from vip_fvs.local_preview import (LocalPreviewAdapter, PreviewArtifact, PreviewAuthorization, PreviewRefusal,
                                    tool_configuration_digest)
from vip_fvs.local_preview import (PreviewSourcePin, canonical_digest, composition_digest,
                                    placement_set_digest, source_set_digest)
from vip_fvs.real_plan import build_real_edit_plan
from vip_fvs.review_bundle import ReviewBundle


def test_aggregate_digest_preimages_are_canonical_and_ordered():
    plan_digest = "a" * 64
    placements = ({"order_index": 0, "placement_digest": "b" * 64, "mapping_digest": "c" * 64},
                  {"order_index": 1, "placement_digest": "d" * 64, "mapping_digest": "e" * 64})
    placement_preimage = {"domain": "vip_fvs.preview-placement-set.v1", "plan_digest": plan_digest,
                          "placements": list(placements)}
    assert placement_set_digest(plan_digest, placements) == hashlib.sha256(
        json.dumps(placement_preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                   allow_nan=False).encode("utf-8")).hexdigest()
    sources = (PreviewSourcePin("rev-1", "f" * 64, 12), PreviewSourcePin("rev-2", "0" * 64, 34))
    source_preimage = {"domain": "vip_fvs.preview-source-set.v1", "sources": [
        {"source_revision_id": "rev-1", "source_sha256": "f" * 64, "byte_count": 12},
        {"source_revision_id": "rev-2", "source_sha256": "0" * 64, "byte_count": 34}]}
    assert source_set_digest(sources) == canonical_digest(source_preimage)
    assert source_set_digest(tuple(reversed(sources))) != source_set_digest(sources)
    composition = {"domain": "vip_fvs.preview-composition.v1", "plan_digest": plan_digest,
                   "timeline_domain": {"domain_id": "timeline-1", "time_base": {"num": 1, "den": 1000}},
                   "audio_policy": "VIDEO_ONLY_DROP_AUDIO_V1", "placements": [
        {"order_index": 0, "placement_id": "p0", "placement_digest": "b" * 64, "mapping_digest": "c" * 64,
         "source_revision_id": "rev-1", "source_sha256": "f" * 64, "stream_index": 0,
         "source_timebase": {"num": 1, "den": 1000}, "source_pts_start": 2,
         "source_pts_end_exclusive": 8, "timeline_start_ticks": 0, "timeline_end_ticks": 6}]}
    assert composition_digest(composition["plan_digest"], composition["timeline_domain"],
                              composition["placements"]) == canonical_digest(composition)


def test_v1_authorization_digest_preimage_remains_byte_compatible(tmp_path):
    auth = PreviewAuthorization(
        authorization_id="compat", policy_identity="policy", scope="NON_PRODUCTION_PREVIEW",
        plan_digest="a" * 64, source_revision_id="rev-1", source_sha256="b" * 64,
        placement_digest="c" * 64, mapping_digest="d" * 64, output_root=tmp_path,
        ffprobe_tool_digest="e" * 64, ffmpeg_tool_digest="f" * 64, tool_config_digest="0" * 64)
    preimage = {"authorization_id": "compat", "policy_identity": "policy", "scope": "NON_PRODUCTION_PREVIEW",
                "plan_digest": "a" * 64, "source_revision_id": "rev-1", "source_sha256": "b" * 64,
                "placement_digest": "c" * 64, "mapping_digest": "d" * 64, "output_root": str(tmp_path),
                "issued_at": "", "expires_at": None, "revoked": False, "production_eligible": False,
                "export_eligible": False, "timeout_seconds": 60.0, "max_output_bytes": 100_000_000,
                "ffprobe_tool_digest": "e" * 64, "ffmpeg_tool_digest": "f" * 64,
                "tool_config_digest": "0" * 64, "review_bundle_record_digest": "",
                "review_bundle_dependency_digest": "", "human_decision_digest": "",
                "review_bundle_ref": "", "decision_ref": ""}
    legacy_bytes = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                              allow_nan=False).encode("utf-8")
    assert auth.schema_version == "v1"
    assert auth.compute_digest() == hashlib.sha256(legacy_bytes).hexdigest()


def test_v2_authorization_rejects_malformed_aggregate_pins(tmp_path):
    with pytest.raises(ValueError, match="placement_set_digest"):
        PreviewAuthorization(
            authorization_id="v2", policy_identity="policy", scope="NON_PRODUCTION_PREVIEW",
            plan_digest="a" * 64, source_revision_id="", source_sha256="b" * 64,
            placement_digest="c" * 64, mapping_digest="d" * 64, output_root=tmp_path,
            ffprobe_tool_digest="1" * 64, ffmpeg_tool_digest="2" * 64, tool_config_digest="3" * 64,
            schema_version="v2", placement_set_digest="bad", source_set_digest="e" * 64,
            composition_digest="f" * 64, ordered_source_pins=(PreviewSourcePin("rev-1", "0" * 64, 1),))


def _plan(monkeypatch):
    bundle = _bundle()
    decision = create_human_decision(
        bundle=bundle, decision_id="decision-1", principal_kind="human", principal_ref="human:editor-1",
        decision_class="ACCEPT", rationale="Reviewed measured source interval.", target_plan_revision=1,
    )
    return build_real_edit_plan(bundle, decision, plan_id="plan-preview", plan_revision=1)


def _auth(artifacts, source: Path, output: Path) -> PreviewAuthorization:
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    probe_id = {"sha256": hashlib.sha256(b"probe-tool").hexdigest()}
    ffmpeg_id = {"sha256": hashlib.sha256(b"ffmpeg-tool").hexdigest()}
    return PreviewAuthorization(
        authorization_id="preview-auth-1", policy_identity="policy-preview-1",
        scope="NON_PRODUCTION_PREVIEW", plan_digest=artifacts.plan.digest,
        source_revision_id="rev-1", source_sha256=digest,
        placement_digest=hashlib.sha256(json.dumps(artifacts.placement.to_record(), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        mapping_digest=artifacts.mapping.record_digest, output_root=output,
        ffprobe_tool_digest=probe_id["sha256"], ffmpeg_tool_digest=ffmpeg_id["sha256"],
        tool_config_digest=tool_configuration_digest(probe_id, ffmpeg_id),
        expires_at="2099-01-01T00:00:00Z",
    )


class Runner:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, argv, **kwargs):
        self.calls.append(list(argv))
        from subprocess import CompletedProcess
        if argv[0].endswith("ffprobe"):
            return CompletedProcess(argv, 0, stdout=json.dumps({"streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000", "duration_ts": 40}]}).encode(), stderr=b"")
        Path(argv[-1]).write_bytes(b"preview-bytes")
        return CompletedProcess(argv, 0, stdout=b"", stderr=b"")


def test_preview_uses_source_pts_and_publishes_hash_bound_nonproduction_artifact(monkeypatch, tmp_path: Path):
    artifacts = _plan(monkeypatch)
    source, output = tmp_path / "source.mp4", tmp_path / "previews"
    source.write_bytes((Path(tempfile.gettempdir()) / "vip-fvs-v3-plan-fixture.mp4").read_bytes())
    ffprobe, ffmpeg = tmp_path / "ffprobe", tmp_path / "ffmpeg"
    ffprobe.write_bytes(b"probe-tool"); ffmpeg.write_bytes(b"ffmpeg-tool")
    runner = Runner()
    artifact = LocalPreviewAdapter(runner=runner).render_preview(
        artifacts, authorization=_auth(artifacts, source, output), source_path=source,
        output_root=output, ffprobe_executable=ffprobe, ffmpeg_executable=ffmpeg,
    )
    assert artifact.output_path.is_file()
    assert artifact.output_bytes == len(b"preview-bytes")
    assert artifact.source_sha256_before == artifact.source_sha256_after
    assert artifact.source_start_pts == 40 and artifact.source_end_pts == 80
    assert artifact.production_eligible is False and artifact.export_eligible is False
    assert artifact.mapping_state == "NOT_OBSERVED"
    assert len(runner.calls) == 3
    ffmpeg_call = runner.calls[1]
    assert "-copyts" in ffmpeg_call
    assert "-vf" in ffmpeg_call
    assert "trim=start_pts=40:end_pts=80,setpts=PTS-STARTPTS" in ffmpeg_call
    assert "-c:v" in ffmpeg_call and "libx264" in ffmpeg_call
    assert "-video_track_timescale" in ffmpeg_call and "1000" in ffmpeg_call
    assert "-c" not in ffmpeg_call


def test_ffmpeg_failure_preserves_bounded_diagnostic(monkeypatch, tmp_path: Path):
    artifacts = _plan(monkeypatch)
    source, output = tmp_path / "source.mp4", tmp_path / "previews"
    source.write_bytes((Path(tempfile.gettempdir()) / "vip-fvs-v3-plan-fixture.mp4").read_bytes())
    ffprobe, ffmpeg = tmp_path / "ffprobe", tmp_path / "ffmpeg"
    ffprobe.write_bytes(b"probe-tool"); ffmpeg.write_bytes(b"ffmpeg-tool")

    class FailingRunner(Runner):
        def __call__(self, argv, **kwargs):
            self.calls.append(list(argv))
            from subprocess import CompletedProcess
            if argv[0].endswith("ffprobe"):
                return CompletedProcess(argv, 0, stdout=json.dumps({"streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}]}).encode(), stderr=b"")
            return CompletedProcess(argv, 234, stdout=b"", stderr=b"Invalid duration for option ss: 40/1000\n" * 100)

    with pytest.raises(PreviewRefusal, match=r"^RENDER_FAILED") as excinfo:
        LocalPreviewAdapter(runner=FailingRunner()).render_preview(
            artifacts, authorization=_auth(artifacts, source, output), source_path=source,
            output_root=output, ffprobe_executable=ffprobe, ffmpeg_executable=ffmpeg,
        )
    message = str(excinfo.value)
    assert "returncode=234" in message
    assert len(message) < 1400


@pytest.mark.parametrize("field", [
    "output_bytes", "output_video_stream_count", "output_timebase_num",
    "output_timebase_den", "output_duration_ticks",
])
def test_v2_artifact_rejects_bool_output_integer_fields(field):
    artifact = PreviewArtifact(
        output_path=Path("/tmp/preview.mp4"), output_bytes=10, output_sha256="a" * 64,
        source_sha256_before="b" * 64, source_sha256_after="b" * 64,
        source_byte_count_before=20, source_byte_count_after=20, source_revision_id="rev-1",
        selected_stream_index=0, source_timebase_num=1, source_timebase_den=1000,
        source_start_pts=0, source_end_pts=10, plan_digest="c" * 64,
        placement_digest="d" * 64, mapping_digest="e" * 64, authorization_digest="f" * 64,
        ffprobe_argv=("ffprobe",), ffmpeg_argv=("ffmpeg",),
        ffprobe_tool={"sha256": "1" * 64}, ffmpeg_tool={"sha256": "2" * 64},
        schema_version="v2", ordered_inputs=({"source_revision_id": "rev-1"},),
        placement_set_digest="3" * 64, source_set_digest="4" * 64,
        composition_digest="5" * 64, tool_config_digest="6" * 64,
        ffprobe_argv_digest="7" * 64, ffmpeg_argv_digest="8" * 64,
        output_video_stream_count=1, output_timebase_num=1,
        output_timebase_den=1000, output_duration_ticks=10,
    )
    with pytest.raises(ValueError, match="integer"):
        replace(artifact, **{field: True, "record_digest": ""})


def test_zero_code_invalid_output_preserves_temp_state_and_argv_digest(monkeypatch, tmp_path: Path):
    artifacts = _plan(monkeypatch)
    source, output = tmp_path / "source.mp4", tmp_path / "previews"
    source.write_bytes((Path(tempfile.gettempdir()) / "vip-fvs-v3-plan-fixture.mp4").read_bytes())
    ffprobe, ffmpeg = tmp_path / "ffprobe", tmp_path / "ffmpeg"
    ffprobe.write_bytes(b"probe-tool"); ffmpeg.write_bytes(b"ffmpeg-tool")

    class MissingOutputRunner(Runner):
        def __call__(self, argv, **kwargs):
            self.calls.append(list(argv))
            from subprocess import CompletedProcess
            if argv[0].endswith("ffprobe"):
                return CompletedProcess(argv, 0, stdout=json.dumps({"streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}]}).encode(), stderr=b"")
            return CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    with pytest.raises(PreviewRefusal, match=r"temp_exists=False"):
        LocalPreviewAdapter(runner=MissingOutputRunner()).render_preview(
            artifacts, authorization=_auth(artifacts, source, output), source_path=source,
            output_root=output, ffprobe_executable=ffprobe, ffmpeg_executable=ffmpeg,
        )


def test_missing_or_stale_authorization_refuses_before_subprocess(monkeypatch, tmp_path: Path):
    artifacts = _plan(monkeypatch)
    source, output = tmp_path / "source.mp4", tmp_path / "previews"
    source.write_bytes((Path(tempfile.gettempdir()) / "vip-fvs-v3-plan-fixture.mp4").read_bytes())
    ffprobe, ffmpeg = tmp_path / "ffprobe", tmp_path / "ffmpeg"
    ffprobe.write_bytes(b"probe-tool"); ffmpeg.write_bytes(b"ffmpeg-tool")
    runner = Runner()
    with pytest.raises(PreviewRefusal, match="STALE"):
        LocalPreviewAdapter(runner=runner).render_preview(
            artifacts, authorization=PreviewAuthorization(
                authorization_id="preview-auth-1", policy_identity="policy-preview-1",
                scope="NON_PRODUCTION_PREVIEW", plan_digest="0" * 64,
                source_revision_id="rev-1", source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                placement_digest="0" * 64, mapping_digest="0" * 64, output_root=output,
                ffprobe_tool_digest="0" * 64, ffmpeg_tool_digest="0" * 64, tool_config_digest="0" * 64,
                expires_at="2099-01-01T00:00:00Z",
            ), source_path=source, output_root=output, ffprobe_executable=ffprobe,
            ffmpeg_executable=ffmpeg,
        )
    assert runner.calls == []


def test_expired_authorization_refuses_before_source_probe(monkeypatch, tmp_path: Path):
    artifacts = _plan(monkeypatch)
    source, output = tmp_path / "source.mp4", tmp_path / "previews"
    source.write_bytes((Path(tempfile.gettempdir()) / "vip-fvs-v3-plan-fixture.mp4").read_bytes())
    ffprobe, ffmpeg = tmp_path / "ffprobe", tmp_path / "ffmpeg"
    ffprobe.write_bytes(b"probe-tool"); ffmpeg.write_bytes(b"ffmpeg-tool")
    runner = Runner()
    auth = _auth(artifacts, source, output)
    expired = PreviewAuthorization(**{**auth.__dict__, "expires_at": "2000-01-01T00:00:00Z", "record_digest": ""})
    with pytest.raises(PreviewRefusal, match="STALE"):
        LocalPreviewAdapter(runner=runner).render_preview(
            artifacts, authorization=expired, source_path=source, output_root=output,
            ffprobe_executable=ffprobe, ffmpeg_executable=ffmpeg,
        )
    assert runner.calls == []
