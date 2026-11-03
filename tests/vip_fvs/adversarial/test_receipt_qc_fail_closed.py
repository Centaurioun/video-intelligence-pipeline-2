from __future__ import annotations

import hashlib
import pathlib
import sys
import types

import pytest

from gate3.qc import QCReport
from gate3.receipt import manifest_inventory_errors, verify_verifier_report
from gate3.verify import VERIFIER_ID
from vip_fvs.local_preview import PreviewArtifact
from vip_fvs.real_preview_receipt import RealPreviewReceipt
from vip_fvs.real_preview_qc import TechnicalQC
from vip_fvs.real_preview_verifier import verify_preview


def _attestation(path: pathlib.Path, *, agreement="AGREE"):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    observation = {
        "refinement_id": "ref-1",
        "source_bytes_match": True,
        "declared_source_digest": digest,
        "measured_source_digest": digest,
        "stream_identity_matches": True,
        "claimed_stream_index": 0,
        "measured_stream_index": 0,
        "endpoints_are_pts_members": True,
        "tail_matches_measured_tail": True,
    }
    return {
        "attestation_id": "att-1",
        "verifier_attempt_id": "attempt-1",
        "verifier_entry_point_id": VERIFIER_ID,
        "producing_entry_point_ids": ["producer.entry"],
        "named_inputs": [str(path)],
        "named_input_digest": digest,
        "method": "synthetic-adversarial-test",
        "configuration_digest": "cfg-1",
        "observations": [observation],
        "observed_result": observation,
        "subject_assertion_refs": ["ref-1"],
        "agreement": agreement,
        "independent_of_producer": True,
        "tool_and_runtime_identity": {"verifier": VERIFIER_ID},
        "residual": 0,
        "NOT_OBSERVED": ["real-media execution"],
    }


def _report(attestation):
    return {
        "verifier_entry_point_id": VERIFIER_ID,
        "checks": [
            {"check": name, "result": "PASS"}
            for name in (
                "gate3_does_not_import_other_gates",
                "independent_re_derivation",
                "source_stream_and_tail_identity",
                "canonical_contract_blob_unchanged",
            )
        ],
        "attestation": attestation,
    }


@pytest.mark.parametrize("missing_artifact", ["verifier", "technical_qc"])
def test_succeeded_receipt_rejects_missing_artifact_attempt_id(tmp_path, missing_artifact):
    import hashlib

    output = tmp_path / "preview.mp4"
    verifier = tmp_path / "verifier.json"
    technical_qc = tmp_path / "technical-qc.json"
    output.write_bytes(b"preview")
    verifier.write_text('{"status":"PASS","attempt_id":"attempt-1"}\n')
    technical_qc.write_text('{"status":"PASS","attempt_id":"attempt-1"}\n')
    target = verifier if missing_artifact == "verifier" else technical_qc
    target.write_text('{"status":"PASS"}\n')

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    record = {
        "schema": "vip_fvs.real_preview_receipt.v1", "receipt_id": "preview-receipt:1",
        "run_id": "run-1", "attempt_id": "attempt-1", "status": "SUCCEEDED",
        "scope": "LOCAL_REAL_NON_PRODUCTION_PREVIEW",
        "source": {"source_revision_id": "revision-1", "source_sha256": "a" * 64,
                   "source_byte_count": 10, "selected_stream_index": 0,
                   "timebase": {"num": 1, "den": 1000}},
        "lifecycle": {"review_bundle_ref": "bundle", "review_bundle_digest": "a" * 64,
                      "review_bundle_dependency_digest": "a" * 64, "decision_ref": "decision",
                      "decision_digest": "a" * 64, "plan_ref": "plan", "plan_digest": "a" * 64,
                      "placement_digest": "a" * 64, "mapping_digest": "a" * 64},
        "authorization": {"authorization_id": "auth-1", "authorization_digest": "a" * 64,
                          "policy_identity": "policy:preview", "scope": "NON_PRODUCTION_PREVIEW"},
        "preview": {"output_ref": str(output), "output_sha256": digest(output),
                    "output_byte_count": output.stat().st_size, "source_sha256_before": "a" * 64,
                    "source_sha256_after": "a" * 64, "source_byte_count_before": 10,
                    "source_byte_count_after": 10, "source_start_pts": 0, "source_end_pts": 1000,
                    "preview_digest": "a" * 64},
        "verifier": {"status": "PASS", "attempt_id": "attempt-1", "digest": digest(verifier),
                     "artifact_ref": str(verifier), "evidence_class": "MEASURED"},
        "technical_qc": {"status": "PASS", "attempt_id": "attempt-1", "digest": digest(technical_qc),
                         "artifact_ref": str(technical_qc), "evidence_class": "MEASURED"},
        "tooling": {"ffprobe_digest": "a" * 64, "ffmpeg_digest": "a" * 64,
                    "configuration_digest": "a" * 64},
        "production_eligible": False, "export_eligible": False,
        "NOT_OBSERVED": ["visual inspection", "audio inspection"],
    }
    with pytest.raises(ValueError, match="attempt/status mismatch"):
        RealPreviewReceipt.create(record, authorized_output_root=tmp_path)


def test_verifier_disagreement_cannot_be_consumed_as_receipt_evidence(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    attestation = _attestation(source, agreement="DISAGREE")

    accepted, errors = verify_verifier_report(
        _report(attestation),
        subject_ref="ref-1",
        source_content_digest=hashlib.sha256(source.read_bytes()).hexdigest(),
        stream_index=0,
        expected_verifier_attempt_id="attempt-1",
    )

    assert accepted is None
    assert "VERIFIER_DID_NOT_AGREE" in errors
    assert any(error.startswith("MANDATORY_CHECK_NOT_PASS:attestation.agreement") for error in errors)


def test_technical_qc_requires_same_explicit_attempt_as_verification(tmp_path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    output_digest = hashlib.sha256(output.read_bytes()).hexdigest()
    artifact = PreviewArtifact(
        output, output.stat().st_size, output_digest, source_digest, source_digest,
        source.stat().st_size, source.stat().st_size, "rev-1", 0, 1, 1000, 10, 40,
        "a" * 64, "b" * 64, "c" * 64, "d" * 64, ("ffprobe",), ("ffmpeg",),
        {"sha256": "b" * 64}, {"sha256": "c" * 64}, False, False, "MEASURED", "producer-attempt",
    )
    verification = verify_preview(artifact, source_path=source, attempt_id="verifier-attempt")
    from dataclasses import replace
    verification = replace(
        verification, measured_output_streams=1, measured_output_timebase="1/1000",
        measured_output_duration_ticks=30, expected_output_duration_ticks=30,
    )

    report = TechnicalQC.evaluate(verification, attempt_id="different-attempt")

    assert report.status == "BLOCKED"
    assert "ATTEMPT_MISMATCH" in report.reason_codes


def test_v2_verifier_rejects_producer_manifest_without_sealed_authority(tmp_path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    output_digest = hashlib.sha256(output.read_bytes()).hexdigest()
    artifact = PreviewArtifact(
        output, output.stat().st_size, output_digest, source_digest, source_digest,
        source.stat().st_size, source.stat().st_size, "rev-1", 0, 1, 1000, 0, 30,
        "a" * 64, "b" * 64, "c" * 64, "d" * 64, ("ffprobe",), ("ffmpeg",),
        {"sha256": "b" * 64}, {"sha256": "c" * 64}, schema_version="v2",
        ordered_inputs=({"order_index": 0, "source_revision_id": "rev-1",
                         "source_sha256": source_digest, "byte_count": source.stat().st_size,
                         "source_pts_start": 0, "source_pts_end_exclusive": 30},),
        placement_set_digest="d" * 64, source_set_digest="e" * 64,
        composition_digest="f" * 64, tool_config_digest="1" * 64,
        ffprobe_argv_digest="2" * 64, ffmpeg_argv_digest="3" * 64,
        output_video_stream_count=1, output_timebase_num=1,
        output_timebase_den=1000, output_duration_ticks=30,
    )
    with pytest.raises(ValueError, match="SEALED_V2_AUTHORITY_REQUIRED"):
        verify_preview(artifact, source_path=source, attempt_id="verifier-attempt",
                       strict_artifact_digests=False)


def test_qc_non_pass_is_not_promoted_by_a_valid_verifier(tmp_path, monkeypatch):
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    attestation = _attestation(source)
    monkeypatch.setattr("gate3.qc._named_bytes_stream_index", lambda _att: (0, None))
    report = QCReport(
        report_id="qc-1",
        artifact_id="render-1",
        qc_scope="technical",
        checks=[{"name": "artifact-readable", "result": "FAIL", "evidence_class": "MEASURED"}],
        supporting_evidence_refs=["ref-1"],
        verifier_attestation=attestation,
        support_records={},
        source_content_digest=hashlib.sha256(source.read_bytes()).hexdigest(),
    )

    assert report.status == "REVISE"
    assert report.to_record()["edit_qc_status"] == "REVISE"


def test_manifest_artifact_digest_mismatch_fails_closed(tmp_path):
    artifact = tmp_path / "artifact.json"
    artifact.write_text("{}")
    errors = manifest_inventory_errors(
        {"output_artifact_digests": [f"{artifact.name}:{'0' * 64}"]}, root=tmp_path
    )

    assert any(error.startswith("RUN_MANIFEST_INVENTORY_INCONSISTENT:DIGEST_MISMATCH") for error in errors)


def test_missing_not_observed_invalidates_verifier_attestation(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    attestation = _attestation(source)
    del attestation["NOT_OBSERVED"]

    accepted, errors = verify_verifier_report(
        _report(attestation),
        subject_ref="ref-1",
        source_content_digest=hashlib.sha256(source.read_bytes()).hexdigest(),
        stream_index=0,
        expected_verifier_attempt_id="attempt-1",
    )

    assert accepted is None
    assert "ATTESTATION_INVALID" in errors


def test_refinement_rejects_source_digest_change_after_refinement(tmp_path, monkeypatch):
    import vip_fvs.refinement_adapter as adapter

    source = tmp_path / "source.mp4"
    source.write_bytes(b"original")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    changed = hashlib.sha256(b"changed").hexdigest()
    calls = {"count": 0}

    monkeypatch.setattr(adapter, "_sha256", lambda _path: calls.update(count=calls["count"] + 1) or (digest if calls["count"] == 1 else changed))
    monkeypatch.setattr(adapter, "_load_gate3", lambda: None, raising=False)
    gate3 = types.ModuleType("gate3")
    container = types.ModuleType("gate3.container")
    container.parse_iso_bmff_timing = lambda *_args, **_kwargs: {"media_timescale": 1000, "pts_ticks": (0, 10, 20)}
    refinement = types.ModuleType("gate3.refinement")
    refinement.is_binding_eligible = lambda _record: True
    refinement.refine = lambda _table, requested, **_kwargs: {"evidence_class": "MEASURED", "time_domain": "source_pts", "start_ticks": requested[0], "end_ticks": requested[1]}
    ingress = types.ModuleType("gate3.ingress")
    ingress.validate_candidate = lambda raw, **_kwargs: {"disposition": "ADMITTED", "reason_codes": [], "record": {**raw, "binding_eligible": False}}
    pts = types.ModuleType("gate3.pts")
    pts.PtsTable = lambda time_base, ticks: types.SimpleNamespace(time_base=time_base, ticks=ticks)
    rational = types.ModuleType("gate3.rational")
    rational.TimeBase = lambda num, den: (num, den)
    for name, module in (("container", container), ("refinement", refinement), ("ingress", ingress), ("pts", pts), ("rational", rational)):
        setattr(gate3, name, module)
        monkeypatch.setitem(sys.modules, "gate3." + name, module)
    monkeypatch.setitem(sys.modules, "gate3", gate3)

    with pytest.raises(adapter.RefinementRefusal, match="changed during refinement"):
        adapter.refine_retrieval_candidate(
            {"source_path": str(source), "source_sha256": digest, "pts": 10, "rank": 1, "score": 1.0},
            source_revision_id="rev-1",
            requested_pts=(10, 20),
        )
