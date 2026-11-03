import json
from pathlib import Path

import pytest
from types import SimpleNamespace

from vip_fvs.real_preview_receipt import (RealPreviewReceipt, build_real_preview_receipt,
                                          load_real_preview_receipt, save_real_preview_receipt)


def valid_record():
    d = "a" * 64
    return {
        "schema": "vip_fvs.real_preview_receipt.v1", "receipt_id": "preview-receipt:a", "run_id": "run:a", "attempt_id": "attempt:a",
        "status": "FAILED", "scope": "LOCAL_REAL_NON_PRODUCTION_PREVIEW",
        "source": {"source_revision_id": "revision:a", "source_sha256": d, "source_byte_count": 10, "selected_stream_index": 0, "timebase": {"num": 1, "den": 1000}},
        "lifecycle": {"review_bundle_ref": "bundle:a", "review_bundle_digest": d, "review_bundle_dependency_digest": d, "decision_ref": "decision:a", "decision_digest": d, "plan_ref": "plan:a", "plan_digest": d, "placement_digest": d, "mapping_digest": d},
        "authorization": {"authorization_id": "auth:a", "authorization_digest": d, "policy_identity": "policy:preview", "scope": "NON_PRODUCTION_PREVIEW"},
        "preview": {"output_ref": "preview.mp4", "output_sha256": d, "output_byte_count": 12, "source_sha256_before": d, "source_sha256_after": d, "source_byte_count_before": 10, "source_byte_count_after": 10, "source_start_pts": 0, "source_end_pts": 1000, "preview_digest": d},
        "verifier": {"status": "PASS", "attempt_id": "attempt:a", "digest": d, "artifact_ref": "verifier.json", "evidence_class": "MEASURED"}, "technical_qc": {"status": "PASS", "attempt_id": "attempt:a", "digest": d, "artifact_ref": "technical-qc.json", "evidence_class": "MEASURED"},
        "tooling": {"ffprobe_digest": d, "ffmpeg_digest": d, "configuration_digest": d},
        "production_eligible": False, "export_eligible": False, "NOT_OBSERVED": ["visual inspection", "audio inspection", "production export"],
    }


def test_preview_receipt_is_distinct_digest_sealed_and_idempotent(tmp_path: Path):
    receipt = RealPreviewReceipt.create(valid_record())
    path = save_real_preview_receipt(receipt, tmp_path / "preview-receipt.json")
    assert load_real_preview_receipt(path).record_digest == receipt.record_digest
    assert save_real_preview_receipt(receipt, path) == path
    assert json.loads(path.read_text())["scope"] == "LOCAL_REAL_NON_PRODUCTION_PREVIEW"


def test_preview_receipt_rejects_mutation_and_non_preview_claims(tmp_path: Path):
    receipt = RealPreviewReceipt.create(valid_record())
    path = save_real_preview_receipt(receipt, tmp_path / "preview.json")
    path.write_text(path.read_text().replace("FAILED", "SUCCEEDED"))
    with pytest.raises(ValueError):
        load_real_preview_receipt(path)
    for field in ("gate3_receipt", "M3", "synthetic", "synthetic_suite", "visual_claim", "audio_claim"):
        bad = valid_record(); bad["preview"][field] = "PASS"
        with pytest.raises(ValueError):
            RealPreviewReceipt.create(bad)


def test_preview_receipt_is_closed_and_non_production():
    bad = valid_record(); bad["authorization"]["production_eligible"] = True
    with pytest.raises(ValueError):
        RealPreviewReceipt.create(bad)
    bad = valid_record(); bad["visual_observation"] = "PASS"
    with pytest.raises(ValueError):
        RealPreviewReceipt.create(bad)


def test_preview_schema_validates_sealed_record():
    from gate3.schema_subset import validate
    schema = json.loads(Path("schemas/vip_fvs/real_preview_receipt.v1.json").read_text())
    assert validate(RealPreviewReceipt.create(valid_record()).to_record(), schema) == []


def test_builder_rejects_unresolved_upstream_lifecycle(tmp_path: Path):
    d = "a" * 64
    preview = SimpleNamespace(
        source_revision_id="revision:a", source_sha256_before=d, source_sha256_after=d,
        source_byte_count_before=10, source_byte_count_after=10, selected_stream_index=0,
        source_timebase_num=1, source_timebase_den=1000, output_path=tmp_path / "preview.mp4",
        output_sha256=d, output_bytes=12, source_start_pts=0, source_end_pts=1000,
        ffprobe_tool={"sha256": d}, ffmpeg_tool={"sha256": d}, ffprobe_argv=("probe",),
        ffmpeg_argv=("ffmpeg",),
    )
    authorization = SimpleNamespace(
        authorization_id="auth:a", record_digest=d, policy_identity="policy:preview",
        scope="NON_PRODUCTION_PREVIEW", review_bundle_record_digest=d,
        review_bundle_dependency_digest=d, human_decision_digest=d,
        review_bundle_ref="bundle.json", decision_ref="decision.json",
    )
    artifacts = SimpleNamespace(plan_digest=d, placement_digest=d, mapping_digest=d)
    with pytest.raises(ValueError, match="UPSTREAM_LIFECYCLE_UNRESOLVED"):
        build_real_preview_receipt(plan_artifacts=artifacts, authorization=authorization,
            preview=preview, verifier={"status": "PASS"}, technical_qc={"status": "PASS"},
            run_id="run:a", attempt_id="attempt:a", plan_ref="plan.json")


def test_succeeded_receipt_requires_pass_attempt_agreement_and_artifact_digests(tmp_path: Path):
    verifier = tmp_path / "verifier.json"
    qc = tmp_path / "technical-qc.json"
    output = tmp_path / "preview.mp4"
    verifier.write_bytes(b'{"status":"PASS","attempt_id":"attempt:a"}\n')
    qc.write_bytes(b'{"status":"PASS","attempt_id":"attempt:a"}\n')
    output.write_bytes(b"preview")
    record = valid_record()
    record["status"] = "SUCCEEDED"
    import hashlib
    record["preview"].update({"output_ref": str(output), "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "output_byte_count": output.stat().st_size})
    record["verifier"].update({"attempt_id": record["attempt_id"], "artifact_ref": str(verifier),
                                "digest": __import__("hashlib").sha256(verifier.read_bytes()).hexdigest()})
    record["technical_qc"].update({"attempt_id": record["attempt_id"], "artifact_ref": str(qc),
                                    "digest": __import__("hashlib").sha256(qc.read_bytes()).hexdigest()})
    with pytest.raises(ValueError, match="authorized_output_root"):
        RealPreviewReceipt.create(record)
    assert RealPreviewReceipt.create(record, authorized_output_root=tmp_path).record["status"] == "SUCCEEDED"
    bad = dict(record); bad["verifier"] = {**record["verifier"], "attempt_id": "other"}
    with pytest.raises(ValueError, match="attempt identity"):
        RealPreviewReceipt.create(bad, authorized_output_root=tmp_path)
    bad = dict(record); bad["technical_qc"] = {**record["technical_qc"], "digest": "a" * 64}
    with pytest.raises(ValueError, match="artifact digest"):
        RealPreviewReceipt.create(bad, authorized_output_root=tmp_path)


def test_succeeded_receipt_revalidates_output_and_root(tmp_path: Path):
    verifier = tmp_path / "verifier.json"; qc = tmp_path / "technical-qc.json"; output = tmp_path / "preview.mp4"
    verifier.write_bytes(b'{"status":"PASS","attempt_id":"attempt:a"}\n'); qc.write_bytes(b'{"status":"PASS","attempt_id":"attempt:a"}\n'); output.write_bytes(b"preview")
    import hashlib
    record = valid_record(); record["status"] = "SUCCEEDED"
    record["preview"].update({"output_ref": str(output), "output_sha256": hashlib.sha256(b"preview").hexdigest(), "output_byte_count": 7})
    record["verifier"].update({"attempt_id": record["attempt_id"], "artifact_ref": str(verifier), "digest": hashlib.sha256(verifier.read_bytes()).hexdigest()})
    record["technical_qc"].update({"attempt_id": record["attempt_id"], "artifact_ref": str(qc), "digest": hashlib.sha256(qc.read_bytes()).hexdigest()})
    receipt = RealPreviewReceipt.create(record, authorized_output_root=tmp_path)
    assert receipt.record["status"] == "SUCCEEDED"
    output.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="output digest"):
        RealPreviewReceipt.create(record, authorized_output_root=tmp_path)


def test_succeeded_receipt_rejects_relative_output_ref(tmp_path: Path):
    verifier = tmp_path / "verifier.json"; qc = tmp_path / "technical-qc.json"
    verifier.write_bytes(b'{"status":"PASS"}\n'); qc.write_bytes(b'{"status":"PASS"}\n')
    record = valid_record(); record["status"] = "SUCCEEDED"
    digest = __import__("hashlib").sha256
    record["verifier"].update({"attempt_id": record["attempt_id"], "artifact_ref": str(verifier), "digest": digest(verifier.read_bytes()).hexdigest()})
    record["technical_qc"].update({"attempt_id": record["attempt_id"], "artifact_ref": str(qc), "digest": digest(qc.read_bytes()).hexdigest()})
    with pytest.raises(ValueError, match="output_ref"):
        RealPreviewReceipt.create(record)


def test_succeeded_receipt_requires_owner_authorized_output_root(tmp_path: Path):
    owner_root = tmp_path / "owner-output"; attacker_root = tmp_path / "attacker-output"
    owner_root.mkdir(); attacker_root.mkdir()
    verifier = owner_root / "verifier.json"; qc = owner_root / "technical-qc.json"; output = attacker_root / "preview.mp4"
    verifier.write_bytes(b'{"status":"PASS"}\n'); qc.write_bytes(b'{"status":"PASS"}\n'); output.write_bytes(b"preview")
    import hashlib
    record = valid_record(); record["status"] = "SUCCEEDED"
    record["preview"].update({"output_ref": str(output), "output_sha256": hashlib.sha256(b"preview").hexdigest(), "output_byte_count": 7})
    record["verifier"].update({"attempt_id": record["attempt_id"], "artifact_ref": str(verifier), "digest": hashlib.sha256(verifier.read_bytes()).hexdigest()})
    record["technical_qc"].update({"attempt_id": record["attempt_id"], "artifact_ref": str(qc), "digest": hashlib.sha256(qc.read_bytes()).hexdigest()})
    with pytest.raises(ValueError, match="authorized output root"):
        RealPreviewReceipt.create(record, authorized_output_root=owner_root)


@pytest.mark.parametrize("timebase", [{"num": 0, "den": 1000}, {"num": 1, "den": "1000"}, {"num": True, "den": 1000}])
def test_preview_receipt_rejects_malformed_timebase(timebase):
    record = valid_record()
    record["source"]["timebase"] = timebase
    with pytest.raises(ValueError, match="timebase"):
        RealPreviewReceipt.create(record)


@pytest.mark.parametrize("status", ["FAILED", "REFUSED"])
def test_failed_and_refused_receipts_remain_loadable_without_success_artifacts(tmp_path: Path, status: str):
    record = valid_record()
    record["status"] = status
    receipt = RealPreviewReceipt.create(record)
    path = save_real_preview_receipt(receipt, tmp_path / f"{status.lower()}.json")
    assert load_real_preview_receipt(path).record["status"] == status
