from pathlib import Path

import pytest

from tests.vip_fvs.unit.test_human_decision import bundle, decision_args
from vip_fvs.human_decision import create_human_decision, save_human_decision
from vip_fvs.real_receipt import RealReceipt, build_decision_receipt, load_real_receipt, save_real_receipt
from vip_fvs.review_bundle import load_review_bundle


def _valid_artifacts():
    return {"review_bundle_ref": "bundle:a", "review_bundle_digest": "e" * 64,
            "review_bundle_dependency_digest": "f" * 64, "probe_ref": "probe:a",
            "probe_digest": "b" * 64}


def test_real_receipt_is_sealed_and_explicitly_non_production(tmp_path: Path):
    source = {
        "source_revision_id": "revision:a", "source_sha256": "a" * 64,
        "source_byte_count": 1, "selected_stream_index": 0,
        "timebase": {"num": 1, "den": 1000},
        "probe_artifact_ref": "probe:a", "probe_digest": "b" * 64,
    }
    record = {
        "schema": "vip_fvs.real_receipt.v1", "receipt_id": "receipt:a", "run_id": "a",
        "attempt_id": "a", "status": "AWAITING_EDITORIAL_DECISION", "scope": "REAL_LOCAL_ONLY",
        "source": source, "authorization": {"discovery_policy_ref": "policy:discover",
        "refinement_policy_ref": "policy:refine", "policy_digest": "c" * 64, "scope_digest": "d" * 64},
        "artifacts": _valid_artifacts(), "decision": None, "plan": None, "export_eligible": False,
        "network_allowed": False, "model_download_allowed": False,
        "NOT_OBSERVED": ["rendering or export"], "refusal": None,
    }
    receipt = RealReceipt.create(record)
    path = save_real_receipt(receipt, tmp_path / "receipt.json")
    assert load_real_receipt(path).record_digest == receipt.record_digest
    tampered = path.read_text().replace("REAL_LOCAL_ONLY", "SYNTHETIC")
    path.write_text(tampered)
    with pytest.raises(ValueError):
        load_real_receipt(path)


def test_resume_receipt_records_accept_without_gate3_fields(tmp_path: Path):
    sealed = bundle(tmp_path)
    bundle_path = tmp_path / "bundle.json"
    from vip_fvs.review_bundle import save_review_bundle
    save_review_bundle(sealed, bundle_path)
    decision = create_human_decision(bundle=sealed, **decision_args(sealed))
    decision_path = tmp_path / "decision.json"
    save_human_decision(decision, decision_path)
    receipt = build_decision_receipt(bundle=sealed, decision=decision, run_id="r", attempt_id="a",
                                     bundle_path=bundle_path, decision_path=decision_path)
    assert receipt.record["status"] == "PLAN_BUILT"
    assert "gate3_receipt" not in receipt.record
    assert receipt.record["export_eligible"] is False


@pytest.mark.parametrize("field", ["gate3_receipt", "synthetic", "render", "technical_qc"])
def test_real_receipt_rejects_non_real_claims(field):
    source = {
        "source_revision_id": "revision:a", "source_sha256": "a" * 64,
        "source_byte_count": 1, "selected_stream_index": 0,
        "timebase": {"num": 1, "den": 1000},
        "probe_artifact_ref": "probe:a", "probe_digest": "b" * 64,
    }
    record = {
        "schema": "vip_fvs.real_receipt.v1", "receipt_id": "receipt:a", "run_id": "a",
        "attempt_id": "a", "status": "AWAITING_EDITORIAL_DECISION", "scope": "REAL_LOCAL_ONLY",
        "source": source, "authorization": {"discovery_policy_ref": "policy:discover",
        "refinement_policy_ref": "policy:refine", "policy_digest": "c" * 64, "scope_digest": "d" * 64},
        "artifacts": {**_valid_artifacts(), field: {"status": "PASS"}}, "decision": None, "plan": None,
        "export_eligible": False, "network_allowed": False, "model_download_allowed": False,
        "NOT_OBSERVED": ["rendering or export"], "refusal": None,
    }
    with pytest.raises(ValueError, match="non-REAL|unknown"):
        RealReceipt.create(record)


def test_real_receipt_schema_closes_nested_envelopes_and_requires_authority():
    import json
    from gate3.schema_subset import validate

    schema = json.loads(Path("schemas/vip_fvs/real_receipt.v1.json").read_text())
    source = {"source_revision_id": "revision:a", "source_sha256": "a" * 64,
              "source_byte_count": 1, "selected_stream_index": 0,
              "timebase": {"num": 1, "den": 1000}, "probe_artifact_ref": "probe:a",
              "probe_digest": "b" * 64}
    record = {"schema": "vip_fvs.real_receipt.v1", "receipt_id": "receipt:a", "run_id": "a",
              "attempt_id": "a", "status": "AWAITING_EDITORIAL_DECISION", "scope": "REAL_LOCAL_ONLY",
              "source": source, "authorization": {"discovery_policy_ref": "policy:discover",
              "refinement_policy_ref": "policy:refine", "policy_digest": "c" * 64, "scope_digest": "d" * 64},
              "artifacts": _valid_artifacts(), "decision": None, "plan": None,
              "export_eligible": False, "network_allowed": False, "model_download_allowed": False,
              "NOT_OBSERVED": ["rendering"], "refusal": None}
    record = RealReceipt.create(record).to_record()
    assert validate(record, schema) == []
    bad = json.loads(json.dumps(record)); bad["authorization"].pop("scope_digest")
    assert validate(bad, schema)
    bad = json.loads(json.dumps(record)); bad["artifacts"]["nested_unknown"] = {"status": "PASS"}
    assert validate(bad, schema)


def test_sealed_real_receipt_record_validates_against_checked_in_schema():
    import json
    from gate3.schema_subset import validate

    source = {"source_revision_id": "revision:a", "source_sha256": "a" * 64,
              "source_byte_count": 1, "selected_stream_index": 0,
              "timebase": {"num": 1, "den": 1000}, "probe_artifact_ref": "probe:a",
              "probe_digest": "b" * 64}
    receipt = RealReceipt.create({
        "schema": "vip_fvs.real_receipt.v1", "receipt_id": "receipt:a", "run_id": "a",
        "attempt_id": "a", "status": "AWAITING_EDITORIAL_DECISION", "scope": "REAL_LOCAL_ONLY",
        "source": source, "authorization": {"discovery_policy_ref": "policy:discover",
        "refinement_policy_ref": "policy:refine", "policy_digest": "c" * 64, "scope_digest": "d" * 64},
        "artifacts": _valid_artifacts(), "decision": None, "plan": None,
        "export_eligible": False, "network_allowed": False, "model_download_allowed": False,
        "NOT_OBSERVED": ["rendering"], "refusal": None,
    })
    schema = json.loads(Path("schemas/vip_fvs/real_receipt.v1.json").read_text())
    assert validate(receipt.to_record(), schema) == []
