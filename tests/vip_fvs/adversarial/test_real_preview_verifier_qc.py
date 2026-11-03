from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path

import pytest

from vip_fvs.local_preview import PreviewArtifact
from vip_fvs.real_preview_qc import TechnicalQC
from vip_fvs.real_preview_verifier import PreviewVerification, verify_preview


def _artifact(source: Path, output: Path, *, attempt: str = "attempt-1") -> PreviewArtifact:
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    output_hash = hashlib.sha256(output.read_bytes()).hexdigest()
    return PreviewArtifact(
        output, output.stat().st_size, output_hash, source_hash, source_hash,
        source.stat().st_size, source.stat().st_size, "rev-1", 0, 1, 1000, 10, 40,
        "p" * 64, "l" * 64, "m" * 64, "a" * 64, ("ffprobe",), ("ffmpeg",),
        {"sha256": "b" * 64}, {"sha256": "c" * 64}, False, False, "MEASURED", attempt,
    )


def test_independent_verifier_rechecks_output_and_attempt_binding(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    artifact = _artifact(source, output, attempt="producer-attempt")

    verified = verify_preview(artifact, source_path=source, attempt_id="attempt-1")

    assert isinstance(verified, PreviewVerification)
    assert verified.status == "PASS"
    assert verified.source_sha256 == artifact.source_sha256_before
    assert verified.output_sha256 == artifact.output_sha256
    assert verified.attempt_id == "attempt-1"


def test_verifier_fails_closed_on_output_tamper(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    artifact = _artifact(source, output, attempt="producer-attempt")
    output.write_bytes(b"tampered")

    with pytest.raises(ValueError, match="OUTPUT_DIGEST_MISMATCH"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1")


def test_verifier_rejects_attempt_mismatch(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    with pytest.raises(ValueError, match="ATTEMPT_MISMATCH"):
        verify_preview(_artifact(source, output, attempt="attempt-1"), source_path=source, attempt_id="attempt-1")


def test_qc_does_not_promote_verifier_contradiction(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    verification = verify_preview(_artifact(source, output, attempt="producer-attempt"), source_path=source, attempt_id="attempt-1")
    report = TechnicalQC.evaluate(verification, measured_output_streams=0)
    assert report.status == "BLOCKED"
    assert "OUTPUT_STREAM_NOT_OBSERVED" in report.reason_codes


def test_qc_pass_requires_verified_nonproduction_artifact(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    verification = verify_preview(_artifact(source, output, attempt="producer-attempt"), source_path=source, attempt_id="attempt-1")
    verification = replace(verification, measured_output_streams=1,
                           measured_output_timebase="1/1000",
                           measured_output_duration_ticks=30,
                           expected_output_duration_ticks=30)
    report = TechnicalQC.evaluate(verification)
    assert report.status == "PASS"
    assert report.production_eligible is False
    assert report.export_eligible is False


def test_qc_rejects_measured_output_timing_contradiction(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    verification = replace(
        verify_preview(_artifact(source, output, attempt="producer-attempt"), source_path=source, attempt_id="attempt-1"),
        measured_output_streams=1, measured_output_timebase="1/1000", measured_output_duration_ticks=99,
        expected_output_duration_ticks=30,
    )
    report = TechnicalQC.evaluate(verification)
    assert report.status == "BLOCKED"
    assert "OUTPUT_TIMING_CONTRADICTION" in report.reason_codes


def test_qc_blocks_missing_output_timing_observation(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    verification = verify_preview(_artifact(source, output, attempt="producer-attempt"), source_path=source, attempt_id="attempt-1")
    verification = replace(verification, measured_output_streams=1)
    report = TechnicalQC.evaluate(verification)
    assert report.status == "BLOCKED"
    assert "OUTPUT_TIMING_NOT_OBSERVED" in report.reason_codes


def test_verifier_rejects_bound_digest_and_pts_mismatches(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    artifact = _artifact(source, output, attempt="producer-attempt")
    with pytest.raises(ValueError, match="PLAN_DIGEST_MISMATCH"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1", expected_plan_digest="x" * 64)
    with pytest.raises(ValueError, match="PTS_NOT_MEASURED"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1", measured_source_pts=[0, 1])


def test_verifier_fails_closed_on_independently_measured_multi_stream_output(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    artifact = _artifact(source, output, attempt="producer-attempt")

    class Result:
        returncode = 0
        stdout = b'{"streams":[{"codec_type":"video","time_base":"1/1000"},{"codec_type":"video","time_base":"1/1000"}]}'

    with pytest.raises(ValueError, match="OUTPUT_STREAM_AMBIGUOUS"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1", probe_runner=lambda *a, **k: Result())


def _authority(tmp_path: Path, source: Path, *, pts=(100, 137, 191), revision="rev-sealed",
               stream=2, timebase=(1, 1000)):
    evidence = {
        "source_bytes_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "stream_index": stream, "media_timescale": timebase[1], "pts_ticks": list(pts),
        "nb_frames": len(pts), "duration_ts": 191, "duration_consistency": "MATCH",
    }
    evidence_path = tmp_path / "source-probe.json"
    evidence_path.write_text(json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n")
    refinement = {
        "source_revision_id": revision, "selected_stream_index": stream,
        "timebase": {"num": timebase[0], "den": timebase[1]},
        "source_pts_interval": {"start": pts[0], "end": pts[1], "time_domain": "source_pts", "endpoint_semantics": "half_open"},
        "evidence_artifact_ref": str(evidence_path),
        "evidence_digest": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
    }
    placement = SimpleNamespace(to_record=lambda: {"placement": "fixture"})
    placement_digest = hashlib.sha256(json.dumps(placement.to_record(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    mapping = SimpleNamespace(source_refinement_id="ref-1", source_start_pts=pts[0], source_end_pts=pts[1],
                              to_record=lambda: {"record_digest": "m" * 64})
    plan = SimpleNamespace(
        plan_digest="p" * 64, placement_digest=placement_digest, mapping_digest="m" * 64,
        placement=placement, mapping=mapping,
        plan=SimpleNamespace(digest="p" * 64, pinned_refinements={"ref-1": refinement}),
    )
    auth = SimpleNamespace(
        record_digest="a" * 64, plan_digest=plan.plan_digest,
        source_revision_id=revision, source_sha256=evidence["source_bytes_sha256"],
        placement_digest=plan.placement_digest, mapping_digest=plan.mapping_digest,
    )
    auth.compute_digest = lambda: auth.record_digest
    return plan, auth, evidence_path


def _sealed_artifact(source: Path, output: Path, plan, auth, *, attempt="producer-attempt", **changes):
    """Build a producer artifact whose untouched authority fields are sealed-valid."""
    return replace(_artifact(source, output, attempt=attempt),
                   plan_digest=plan.plan_digest,
                   placement_digest=plan.placement_digest,
                   mapping_digest=plan.mapping_digest,
                   authorization_digest=auth.record_digest,
                   **changes)


def test_verifier_rederives_source_authority_from_sealed_plan_and_evidence(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    artifact = _sealed_artifact(source, output, plan, auth, attempt="producer-attempt")
    with pytest.raises(ValueError, match="SOURCE_REVISION_MISMATCH"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1",
                       plan_artifacts=plan, authorization=auth,
                       source_evidence_path=evidence_path,
                       source_probe_runner=lambda *a, **k: SimpleNamespace(
                           returncode=0, stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}'))


@pytest.mark.parametrize(
    ("field", "reason"),
    (("plan_digest", "PLAN_DIGEST_MISMATCH"),
     ("placement_digest", "PLACEMENT_DIGEST_MISMATCH"),
     ("mapping_digest", "MAPPING_DIGEST_MISMATCH"),
     ("authorization_digest", "AUTHORIZATION_DIGEST_MISMATCH")),
)
def test_verifier_binds_artifact_digests_to_sealed_authority(
    tmp_path: Path, field: str, reason: str,
):
    """A forged artifact cannot pass when caller supplies sealed plan/auth data."""
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    artifact = replace(
        _sealed_artifact(source, output, plan, auth, attempt="producer-attempt"),
        source_revision_id="rev-sealed", selected_stream_index=2,
        source_timebase_num=1, source_timebase_den=1000,
        source_start_pts=100, source_end_pts=137,
        **{field: "f" * 64},
    )
    with pytest.raises(ValueError, match=reason):
        verify_preview(
            artifact, source_path=source, attempt_id="attempt-1",
            plan_artifacts=plan, authorization=auth,
            source_evidence_path=evidence_path,
            source_probe_runner=lambda *a, **k: SimpleNamespace(
                returncode=0,
                stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}',
            ),
        )


@pytest.mark.parametrize("bad_value", [None, "", "short"])
def test_verifier_rejects_malformed_authority_digests(tmp_path: Path, bad_value):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    artifact = replace(_sealed_artifact(source, output, plan, auth, attempt="producer-attempt"),
                       source_revision_id="rev-sealed", selected_stream_index=2,
                       source_timebase_num=1, source_timebase_den=1000,
                       source_start_pts=100, source_end_pts=137,
                       plan_digest=bad_value)
    with pytest.raises(ValueError, match="PLAN_DIGEST_MISMATCH"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1",
                       plan_artifacts=plan, authorization=auth,
                       source_evidence_path=evidence_path,
                       strict_artifact_digests=True,
                       source_probe_runner=lambda *a, **k: SimpleNamespace(
                           returncode=0, stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}'))


@pytest.mark.parametrize("field", ["plan_digest", "placement_digest", "mapping_digest", "authorization_digest"])
def test_verifier_requires_sealed_authority_digests_by_default(tmp_path: Path, field: str):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    artifact = replace(
        _sealed_artifact(source, output, plan, auth, attempt="producer-attempt"),
        source_revision_id="rev-sealed", selected_stream_index=2,
        source_timebase_num=1, source_timebase_den=1000,
        source_start_pts=100, source_end_pts=137,
        **{field: ""},
    )
    with pytest.raises(ValueError, match=field.upper().replace("_", "_") + "_MISMATCH"):
        verify_preview(
            artifact, source_path=source, attempt_id="attempt-1",
            plan_artifacts=plan, authorization=auth,
            source_evidence_path=evidence_path,
            source_probe_runner=lambda *a, **k: SimpleNamespace(
                returncode=0,
                stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}',
            ),
        )


def test_verifier_rejects_malformed_sealed_timebase(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    plan.plan.pinned_refinements["ref-1"]["timebase"] = {"num": 1, "den": "1000"}
    artifact = replace(_sealed_artifact(source, output, plan, auth, attempt="producer-attempt"),
                       source_revision_id="rev-sealed", selected_stream_index=2,
                       source_timebase_num=1, source_timebase_den=1000,
                       source_start_pts=100, source_end_pts=137)
    with pytest.raises(ValueError, match="TIMEBASE_INVALID"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1",
                       plan_artifacts=plan, authorization=auth,
                       source_evidence_path=evidence_path,
                       source_probe_runner=lambda *a, **k: SimpleNamespace(
                           returncode=0, stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}'))


def test_verifier_rejects_pts_rows_without_stream_scope(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    evidence_path.write_text(json.dumps({
        "source_bytes_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "stream_index": 2, "media_timescale": 1000,
        "frames": [{"best_effort_timestamp": 100}, {"best_effort_timestamp": 137}],
    }, sort_keys=True, separators=(",", ":")) + "\n")
    plan.plan.pinned_refinements["ref-1"]["evidence_digest"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    artifact = replace(_sealed_artifact(source, output, plan, auth, attempt="producer-attempt"),
                       source_revision_id="rev-sealed", selected_stream_index=2,
                       source_timebase_num=1, source_timebase_den=1000,
                       source_start_pts=100, source_end_pts=137)
    with pytest.raises(ValueError, match="SOURCE_PTS_EVIDENCE_INVALID"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1",
                       plan_artifacts=plan, authorization=auth,
                       source_evidence_path=evidence_path,
                       source_probe_runner=lambda *a, **k: SimpleNamespace(
                           returncode=0, stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}'))


def test_verifier_rejects_producer_pts_when_pinned_sparse_evidence_disagrees(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    artifact = _artifact(source, output, attempt="producer-attempt")
    plan, auth, evidence_path = _authority(tmp_path, source)
    artifact = replace(_sealed_artifact(source, output, plan, auth, attempt="producer-attempt"), source_revision_id="rev-sealed", selected_stream_index=2, source_start_pts=100, source_end_pts=137,
                       measured_source_pts=(100, 101, 102))
    with pytest.raises(ValueError, match="PTS_NOT_MEASURED"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1",
                       plan_artifacts=plan, authorization=auth, source_evidence_path=evidence_path,
                       source_probe_runner=lambda *a, **k: SimpleNamespace(
                           returncode=0, stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}'))


def test_verifier_accepts_sparse_vfr_next_pts_without_integer_adjacency(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    probe = tmp_path / "ffprobe"; ffmpeg = tmp_path / "ffmpeg"
    probe.write_bytes(b"probe"); ffmpeg.write_bytes(b"ffmpeg")
    probe_digest = hashlib.sha256(probe.read_bytes()).hexdigest()
    ffmpeg_digest = hashlib.sha256(ffmpeg.read_bytes()).hexdigest()
    auth.ffprobe_tool_digest = probe_digest; auth.ffmpeg_tool_digest = ffmpeg_digest
    artifact = replace(_sealed_artifact(source, output, plan, auth, attempt="producer-attempt"), source_revision_id="rev-sealed",
                       selected_stream_index=2, source_timebase_num=1, source_timebase_den=1000,
                       source_start_pts=100, source_end_pts=137,
                       ffprobe_tool={"path": str(probe), "sha256": probe_digest},
                       ffmpeg_tool={"path": str(ffmpeg), "sha256": ffmpeg_digest})
    verified = verify_preview(artifact, source_path=source, attempt_id="attempt-1",
                              plan_artifacts=plan, authorization=auth, source_evidence_path=evidence_path,
                              source_probe_runner=lambda *a, **k: SimpleNamespace(
                                  returncode=0, stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}'))
    assert verified.status == "PASS"


def test_verifier_refuses_stream_tail_without_explicit_tail_support(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    refinement = plan.plan.pinned_refinements["ref-1"]
    refinement["source_pts_interval"]["start"] = 191
    refinement["source_pts_interval"]["end"] = 200
    plan.mapping.source_start_pts = 191; plan.mapping.source_end_pts = 200
    probe = tmp_path / "ffprobe"; ffmpeg = tmp_path / "ffmpeg"
    probe.write_bytes(b"probe"); ffmpeg.write_bytes(b"ffmpeg")
    probe_digest = hashlib.sha256(probe.read_bytes()).hexdigest(); ffmpeg_digest = hashlib.sha256(ffmpeg.read_bytes()).hexdigest()
    auth.ffprobe_tool_digest = probe_digest; auth.ffmpeg_tool_digest = ffmpeg_digest
    artifact = replace(_sealed_artifact(source, output, plan, auth, attempt="producer-attempt"), source_revision_id="rev-sealed",
                       selected_stream_index=2, source_start_pts=191, source_end_pts=200,
                       ffprobe_tool={"path": str(probe), "sha256": probe_digest},
                       ffmpeg_tool={"path": str(ffmpeg), "sha256": ffmpeg_digest})
    with pytest.raises(ValueError, match="STREAM_TAIL_NOT_SUPPORTED"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1", plan_artifacts=plan,
                       authorization=auth, source_evidence_path=evidence_path,
                       source_probe_runner=lambda *a, **k: SimpleNamespace(
                           returncode=0, stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}'))


def test_verifier_rejects_tampered_pinned_evidence_digest(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    artifact = replace(_sealed_artifact(source, output, plan, auth, attempt="producer-attempt"), source_revision_id="rev-sealed",
                       selected_stream_index=2, source_start_pts=100, source_end_pts=137)
    evidence_path.write_text(evidence_path.read_text().replace("137", "138"))
    with pytest.raises(ValueError, match="EVIDENCE_DIGEST_MISMATCH"):
        verify_preview(artifact, source_path=source, attempt_id="attempt-1",
                       plan_artifacts=plan, authorization=auth, source_evidence_path=evidence_path,
                       source_probe_runner=lambda *a, **k: SimpleNamespace(
                           returncode=0, stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}'))


# --- IT-7: multiplicity preservation and one-admission-rule (Root G §3.2) ---


def _sealed_verify(artifact, source: Path, plan, auth, evidence_path: Path):
    return verify_preview(
        artifact, source_path=source, attempt_id="attempt-1",
        plan_artifacts=plan, authorization=auth, source_evidence_path=evidence_path,
        source_probe_runner=lambda *a, **k: SimpleNamespace(
            returncode=0,
            stdout=b'{"streams":[{"index":2,"codec_type":"video","time_base":"1/1000"}]}',
        ),
    )


def _rewrite_evidence(plan, evidence_path: Path, payload) -> None:
    evidence_path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    plan.plan.pinned_refinements["ref-1"]["evidence_digest"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()


def _probe_tools(tmp_path: Path, auth):
    probe, ffmpeg = tmp_path / "ffprobe", tmp_path / "ffmpeg"
    probe.write_bytes(b"probe"); ffmpeg.write_bytes(b"ffmpeg")
    probe_digest = hashlib.sha256(probe.read_bytes()).hexdigest()
    ffmpeg_digest = hashlib.sha256(ffmpeg.read_bytes()).hexdigest()
    auth.ffprobe_tool_digest = probe_digest
    auth.ffmpeg_tool_digest = ffmpeg_digest
    return ({"path": str(probe), "sha256": probe_digest},
            {"path": str(ffmpeg), "sha256": ffmpeg_digest})


def _sealed_artifact_for_interval(source: Path, output: Path, plan, auth, **changes):
    probe_tool, ffmpeg_tool = _probe_tools(source.parent, auth)
    return replace(
        _sealed_artifact(source, output, plan, auth, attempt="producer-attempt"),
        source_revision_id="rev-sealed", selected_stream_index=2,
        source_timebase_num=1, source_timebase_den=1000,
        source_start_pts=100, source_end_pts=137,
        ffprobe_tool=probe_tool, ffmpeg_tool=ffmpeg_tool, **changes,
    )


def test_verifier_preserves_duplicate_presentation_tick_multiplicity(tmp_path: Path):
    """A producer that collapses duplicate presentation ticks must be refused.

    Before IT-7 both sides collapsed to ``sorted(set(...))``, so a duplicated
    observed tick silently compared equal to a collapsed producer projection.
    """
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    _rewrite_evidence(plan, evidence_path, {
        "source_bytes_sha256": auth.source_sha256,
        "stream_index": 2, "media_timescale": 1000,
        "frames": [
            {"stream_index": 2, "best_effort_timestamp": 100},
            {"stream_index": 2, "best_effort_timestamp": 100},
            {"stream_index": 2, "best_effort_timestamp": 137},
        ],
    })
    artifact = _sealed_artifact_for_interval(source, output, plan, auth, measured_source_pts=(100, 137))
    with pytest.raises(ValueError, match="PTS_NOT_MEASURED"):
        _sealed_verify(artifact, source, plan, auth, evidence_path)


def test_verifier_accepts_multiplicity_preserving_producer_projection(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    _rewrite_evidence(plan, evidence_path, {
        "source_bytes_sha256": auth.source_sha256,
        "stream_index": 2, "media_timescale": 1000,
        "frames": [
            {"stream_index": 2, "best_effort_timestamp": 100},
            {"stream_index": 2, "best_effort_timestamp": 100},
            {"stream_index": 2, "best_effort_timestamp": 137},
        ],
    })
    artifact = _sealed_artifact_for_interval(source, output, plan, auth, measured_source_pts=(100, 100, 137))
    assert _sealed_verify(artifact, source, plan, auth, evidence_path).status == "PASS"


def test_verifier_counts_one_presentation_tick_per_frame_row(tmp_path: Path):
    """``best_effort_timestamp`` and ``pts`` are aliases of one observation.

    A row carrying both must contribute one tick (Root G §3.2(3)); a naive
    multiset over every alias would double-count and refuse this evidence.
    """
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    _rewrite_evidence(plan, evidence_path, {
        "source_bytes_sha256": auth.source_sha256,
        "stream_index": 2, "media_timescale": 1000,
        "frames": [
            {"stream_index": 2, "best_effort_timestamp": 100, "pts": 100},
            {"stream_index": 2, "best_effort_timestamp": 137, "pts": 137},
            {"stream_index": 2, "best_effort_timestamp": 191, "pts": 191},
        ],
    })
    artifact = _sealed_artifact_for_interval(source, output, plan, auth, measured_source_pts=(100, 137, 191))
    assert _sealed_verify(artifact, source, plan, auth, evidence_path).status == "PASS"


def test_verifier_excludes_rows_without_stream_scope_like_preview(tmp_path: Path):
    """Root G §3.2(1): absent stream identity is excluded, never guessed.

    The preview projection already skipped such rows; the verifier used to
    raise, so render-admitted evidence was verify-refused (Dv-11).
    """
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source"); output.write_bytes(b"preview")
    plan, auth, evidence_path = _authority(tmp_path, source)
    _rewrite_evidence(plan, evidence_path, {
        "source_bytes_sha256": auth.source_sha256,
        "stream_index": 2, "media_timescale": 1000,
        "frames": [
            {"best_effort_timestamp": 191},
            {"stream_index": 2, "best_effort_timestamp": 100},
            {"stream_index": 2, "best_effort_timestamp": 137},
        ],
    })
    artifact = _sealed_artifact_for_interval(source, output, plan, auth, measured_source_pts=(100, 137))
    assert _sealed_verify(artifact, source, plan, auth, evidence_path).status == "PASS"
