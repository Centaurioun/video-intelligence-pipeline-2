"""Unit tests for the sealed fixture preview receipt profile.

No ffmpeg, model, provider or network is used: artifacts are tiny sealed files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import vip_fvs.real_preview_receipt as receipts

FIXTURE_SCHEMA = "vip_fvs.fixture_preview_receipt.v1"
FIXTURE_SCOPE = "LOCAL_FIXTURE_NON_PRODUCTION_PREVIEW"
REAL_SCHEMA = "vip_fvs.real_preview_receipt.v1"
REAL_SCOPE = "LOCAL_REAL_NON_PRODUCTION_PREVIEW"
ATTEMPT = "attempt-fixture-1"
FIXTURE_NOT_OBSERVED = [
    "human editorial authority",
    "visual editorial suitability",
    "audio observation",
    "production render capability",
    "provider/cloud inference",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _artifacts(root: Path):
    output = root / "fixture-plan-1.preview.mp4"
    output.write_bytes(b"measured-preview-bytes")
    verifier = root / "verifier.json"
    verifier.write_bytes(json.dumps({"status": "PASS", "attempt_id": ATTEMPT}).encode())
    qc = root / "technical-qc.json"
    qc.write_bytes(json.dumps({"status": "PASS", "attempt_id": ATTEMPT}).encode())
    return output, verifier, qc


def _common(root: Path):
    output, verifier, qc = _artifacts(root)
    source_sha = "a" * 64
    return {
        "source": {
            "source_revision_id": "fixture-source-1",
            "source_sha256": source_sha,
            "source_byte_count": 4096,
            "selected_stream_index": 0,
            "timebase": {"num": 1, "den": 1000},
        },
        "preview": {
            "output_ref": str(output),
            "output_sha256": _sha(output.read_bytes()),
            "output_byte_count": output.stat().st_size,
            "source_sha256_before": source_sha,
            "source_sha256_after": source_sha,
            "source_byte_count_before": 4096,
            "source_byte_count_after": 4096,
            "source_start_pts": 0,
            "source_end_pts": 40,
            "preview_digest": "c" * 64,
        },
        "authorization": {
            "authorization_id": "fixture-authorization-1",
            "authorization_digest": "d" * 64,
            "policy_identity": "local-fixture-preview",
            "scope": "NON_PRODUCTION_PREVIEW",
        },
        "verifier": {
            "status": "PASS",
            "attempt_id": ATTEMPT,
            "digest": _sha(verifier.read_bytes()),
            "artifact_ref": str(verifier),
            "evidence_class": "MEASURED",
        },
        "technical_qc": {
            "status": "PASS",
            "attempt_id": ATTEMPT,
            "digest": _sha(qc.read_bytes()),
            "artifact_ref": str(qc),
            "evidence_class": "MEASURED",
        },
        "tooling": {"ffprobe_digest": "e" * 64, "ffmpeg_digest": "f" * 64, "configuration_digest": "0" * 64},
        "production_eligible": False,
        "export_eligible": False,
    }


def _fixture_record(root: Path) -> dict:
    record = {
        "schema": FIXTURE_SCHEMA,
        "receipt_id": "fixture-preview-receipt:attempt-fixture-1",
        "run_id": "fixture-run-1",
        "attempt_id": ATTEMPT,
        "status": "SUCCEEDED",
        "scope": FIXTURE_SCOPE,
        **_common(root),
        "lifecycle": {
            "decision_digest": "1" * 64,
            "decision_id": "fixture-decision-1",
            "principal_kind": "SYNTHETIC_HUMAN",
            "fixture_scope": "SYNTHETIC_FIXTURE",
            "refinement_id": "ref_fixture00000001",
            "refinement_evidence_digest": "b" * 64,
            "plan_ref": str(root / "plan.json"),
            "plan_digest": "2" * 64,
            "placement_digest": "3" * 64,
            "mapping_digest": "4" * 64,
            "plan_scope": "SYNTHETIC_FIXTURE",
        },
        "NOT_OBSERVED": list(FIXTURE_NOT_OBSERVED),
    }
    return record


def _real_record(root: Path) -> dict:
    return {
        "schema": REAL_SCHEMA,
        "receipt_id": "preview-receipt:attempt-fixture-1",
        "run_id": "real-run-1",
        "attempt_id": ATTEMPT,
        "status": "SUCCEEDED",
        "scope": REAL_SCOPE,
        **_common(root),
        "lifecycle": {
            "review_bundle_ref": str(root / "review-bundle.json"),
            "review_bundle_digest": "1" * 64,
            "review_bundle_dependency_digest": "2" * 64,
            "decision_ref": str(root / "human-decision.json"),
            "decision_digest": "3" * 64,
            "plan_ref": str(root / "plan.json"),
            "plan_digest": "4" * 64,
            "placement_digest": "5" * 64,
            "mapping_digest": "6" * 64,
        },
        "NOT_OBSERVED": ["VISUALLY_OBSERVED", "AUDIO_OBSERVED"],
    }


def test_fixture_receipt_create_is_sealed_and_nonproduction(tmp_path):
    receipt = receipts.FixturePreviewReceipt.create(
        _fixture_record(tmp_path), authorized_output_root=tmp_path)
    record = receipt.to_record()

    assert record["schema"] == FIXTURE_SCHEMA
    assert record["scope"] == FIXTURE_SCOPE
    assert record["status"] == "SUCCEEDED"
    assert record["production_eligible"] is False
    assert record["export_eligible"] is False
    assert record["lifecycle"]["principal_kind"] == "SYNTHETIC_HUMAN"
    assert record["lifecycle"]["fixture_scope"] == "SYNTHETIC_FIXTURE"
    assert record["record_digest"] == receipts.fixture_receipt_digest(record)
    for entry in FIXTURE_NOT_OBSERVED:
        assert entry in record["NOT_OBSERVED"]


def test_fixture_receipt_round_trips_through_save_and_load(tmp_path):
    receipt = receipts.FixturePreviewReceipt.create(
        _fixture_record(tmp_path), authorized_output_root=tmp_path)
    path = receipts.save_fixture_preview_receipt(
        receipt, tmp_path / "preview-receipt.json", authorized_output_root=tmp_path)
    loaded = receipts.load_fixture_preview_receipt(path, authorized_output_root=tmp_path)

    assert loaded.record_digest == receipt.record_digest
    assert loaded.record == receipt.record


def test_fixture_receipt_refuses_create_on_attempt_mismatch(tmp_path):
    record = _fixture_record(tmp_path)
    record["verifier"] = {**record["verifier"], "attempt_id": "attempt-other"}
    with pytest.raises(ValueError, match="FIXTURE_VERIFIER_ATTEMPT_MISMATCH"):
        receipts.FixturePreviewReceipt.create(record, authorized_output_root=tmp_path)


def test_fixture_receipt_refuses_missing_human_authority_disclaimer(tmp_path):
    record = _fixture_record(tmp_path)
    record["NOT_OBSERVED"] = ["audio observation", "provider/cloud inference"]
    with pytest.raises(ValueError, match="FIXTURE_NOT_OBSERVED_INCOMPLETE"):
        receipts.FixturePreviewReceipt.create(record, authorized_output_root=tmp_path)


def test_fixture_receipt_refuses_nonproduction_flag(tmp_path):
    record = _fixture_record(tmp_path)
    record["production_eligible"] = True
    with pytest.raises(ValueError, match="production/export authority"):
        receipts.FixturePreviewReceipt.create(record, authorized_output_root=tmp_path)


def test_fixture_receipt_refuses_human_principal_lifecycle(tmp_path):
    record = _fixture_record(tmp_path)
    record["lifecycle"] = {**record["lifecycle"], "principal_kind": "human"}
    with pytest.raises(ValueError, match="FIXTURE_PRINCIPAL_REQUIRED"):
        receipts.FixturePreviewReceipt.create(record, authorized_output_root=tmp_path)


def test_fixture_receipt_refuses_real_scope_lifecycle(tmp_path):
    record = _fixture_record(tmp_path)
    record["lifecycle"] = {**record["lifecycle"], "plan_scope": "REAL"}
    with pytest.raises(ValueError, match="FIXTURE_PLAN_SCOPE_REQUIRED"):
        receipts.FixturePreviewReceipt.create(record, authorized_output_root=tmp_path)


def test_load_real_preview_receipt_refuses_fixture_receipt(tmp_path):
    receipt = receipts.FixturePreviewReceipt.create(
        _fixture_record(tmp_path), authorized_output_root=tmp_path)
    path = receipts.save_fixture_preview_receipt(
        receipt, tmp_path / "fixture-receipt.json", authorized_output_root=tmp_path)
    with pytest.raises(ValueError):
        receipts.load_real_preview_receipt(path, authorized_output_root=tmp_path)


def test_load_fixture_preview_receipt_refuses_real_receipt(tmp_path):
    real = receipts.RealPreviewReceipt.create(
        _real_record(tmp_path), authorized_output_root=tmp_path)
    path = receipts.save_real_preview_receipt(
        real, tmp_path / "real-receipt.json", authorized_output_root=tmp_path)
    with pytest.raises(ValueError):
        receipts.load_fixture_preview_receipt(path, authorized_output_root=tmp_path)


def test_save_fixture_receipt_refuses_overwrite_of_different_receipt(tmp_path):
    receipt = receipts.FixturePreviewReceipt.create(
        _fixture_record(tmp_path), authorized_output_root=tmp_path)
    path = receipts.save_fixture_preview_receipt(
        receipt, tmp_path / "preview-receipt.json", authorized_output_root=tmp_path)
    other_record = _fixture_record(tmp_path)
    other_record["run_id"] = "fixture-run-2"
    other = receipts.FixturePreviewReceipt.create(other_record, authorized_output_root=tmp_path)
    with pytest.raises(ValueError, match="sealed fixture preview receipt differs"):
        receipts.save_fixture_preview_receipt(
            other, path, authorized_output_root=tmp_path)
