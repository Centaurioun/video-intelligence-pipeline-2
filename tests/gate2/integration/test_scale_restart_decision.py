"""Contract checks for the bounded H3-F03 synthetic measurement receipts."""
import hashlib
import json
from pathlib import Path

from gate2.cli import main as gate2_main
from gate2.verify import (
    _ACCEPTED_DEPENDENCY_HEADS,
    resolve_accepted_heads,
    resolve_contract_fingerprints,
    verify_evidence,
)


REPO_ROOT = Path(__file__).parents[3]
BUNDLE_ROOT = REPO_ROOT / ".orchestration/remaining-work/runs/H3-F03/measurement"
RECEIPT = BUNDLE_ROOT / "metrics-001/measurement.json"
CURRENT_RECEIPT = BUNDLE_ROOT / "metrics-003/measurement.json"
CURRENT_BUNDLE = CURRENT_RECEIPT.parent


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def _preregistration():
    preregistration_bytes = (CURRENT_BUNDLE / "preregistration.json").read_bytes()
    preregistration = json.loads(preregistration_bytes)
    freeze_digest = preregistration.pop("freeze_digest")
    return preregistration, preregistration_bytes, freeze_digest


def test_receipt_binds_exact_dependencies_and_synthetic_scope():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["scope"] == "synthetic_generated_only"
    assert receipt["dependencies"] == {
        "F01": {"sha": "cf8567cbbba321e79059b5e029e58c326dee9d01", "tree": "9d9b34accb355024b1936ebee08af5d7e158c36f"},
        "F02": {"sha": "83bfb1732e18d58688a008fae27785c9f6c6e4ee", "tree": "a4bcb06e8b7885da045d525ff25c14529007c7d0"},
    }
    assert receipt["corrections"] == ["Parent corrected F01 expected tree transcription; exact checkout tree verified against overlay."]


def test_only_carried_metrics_are_measured_and_unavailable_metrics_are_explicit():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    observations = receipt["measurements"]
    measured = [m for m in observations if m["status"] == "MEASURED"]
    absent = [m for m in observations if m["status"] == "NOT_OBSERVED"]
    assert {m["metric_id"] for m in measured} == {
        "fixture_generation_wall_time", "restart_recovery_wall_time", "idempotent_duplicate_applications"
    }
    assert {m["metric_id"] for m in absent} == {"peak_memory", "materialization_latency"}
    assert all(m["unit"] == "milliseconds" for m in measured if m["metric_id"].endswith("wall_time"))
    assert all(m["carrier_path"] and m["carrier_sha256"] for m in measured)
    for m in measured:
        carrier = RECEIPT.parent / m["carrier_path"]
        assert hashlib.sha256(carrier.read_bytes()).hexdigest() == m["carrier_sha256"]
    assert all(m["repetition"] in (1, 2) for m in observations)


def test_workload_bounds_and_freeze_are_recorded_before_measurements():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["preregistration"]["freeze_digest"]
    assert hashlib.sha256((RECEIPT.parent / "preregistration.json").read_bytes().rstrip(b"\n")).hexdigest() == receipt["preregistration"]["freeze_digest"]
    assert receipt["workload"] == {
        "jobs": 4,
        "stages": 3,
        "artifact_bytes_per_stage": 64,
        "cost_units_per_first_stage": 5,
        "concurrency": 1,
        "repetitions": 2,
        "seed": 20261007,
        "fault": "after_side_effect_before_completion",
    }
    assert receipt["bounds"]["max_generated_artifact_bytes"] == 8000000
    assert receipt["bounds"]["max_wall_time_ms"] == 30000


def test_rebuilt_metrics_003_binds_git_objects_frozen_preregistration_and_exact_carriers(capsys):
    receipt = json.loads(CURRENT_RECEIPT.read_text(encoding="utf-8"))
    assert receipt["schema"] == "h3-f03.measurement-receipt.v3"
    assert receipt["scope"] == "synthetic_generated_only"

    # Accepted dependency heads are resolved from real git objects and must
    # agree with the pinned accepted heads.
    accepted_heads = resolve_accepted_heads(REPO_ROOT)
    assert accepted_heads == _ACCEPTED_DEPENDENCY_HEADS
    assert receipt["dependencies"] == accepted_heads
    assert receipt["candidate"] == accepted_heads["F02"]
    assert receipt["safety"] == {
        "production_eligible": False,
        "gate_promotion": False,
        "mechanism_adopted": False,
    }

    # The frozen preregistration is the current generation, not a stale literal.
    preregistration, preregistration_bytes, freeze_digest = _preregistration()
    assert hashlib.sha256(_canonical(preregistration)).hexdigest() == freeze_digest
    assert hashlib.sha256(preregistration_bytes).hexdigest() == receipt["preregistration"]["canonical_bytes_sha256"]
    assert receipt["preregistration"]["freeze_digest"] == freeze_digest
    assert receipt["preregistration"]["recorded_before_observations"] is True

    expected_fingerprints = resolve_contract_fingerprints(REPO_ROOT)
    assert preregistration["contract_fingerprints"] == expected_fingerprints
    assert receipt["preregistration"]["consumed_contracts"] == expected_fingerprints
    # The stale F01 generation fingerprints must never be re-declared.
    assert "07588fc7c721068b678f41023f7358b53c275c0b" not in expected_fingerprints.values()
    assert "3530190eabd6efccfae0cb090423c310c6e12c02" not in expected_fingerprints.values()
    assert "0bf2b12cd75a0d72e815e82089f180a7d5e04070" not in expected_fingerprints.values()
    assert expected_fingerprints["gate2_measure_candidate"] == hashlib.sha1(
        b"blob %d\x00" % len((REPO_ROOT / "src/gate2/measure.py").read_bytes())
        + (REPO_ROOT / "src/gate2/measure.py").read_bytes()
    ).hexdigest()

    assert preregistration["dependency_generations"] == {
        "F01": accepted_heads["F01"]["sha"],
        "F02": accepted_heads["F02"]["sha"],
    }
    assert receipt["dependencies"] == accepted_heads
    assert hashlib.sha256(_canonical(receipt["configuration"])).hexdigest() == preregistration["configuration_identity"]["digest"]
    assert hashlib.sha256(_canonical(receipt["workload_identity"])).hexdigest() == preregistration["workload_identity"]["digest"]
    assert receipt["workload_digest"] == preregistration["workload_identity"]["digest"]
    assert receipt["config_digest"] == preregistration["configuration_identity"]["digest"]
    assert receipt["bounds"] == preregistration["numeric_bounds"]

    # Evidence declarations are honest and enforced: the absent metric is
    # declared before observation and is reported as NOT_OBSERVED.
    assert set(preregistration["evidence_declarations"]) == {
        metric["name"] for metric in preregistration["metrics"]
    }
    assert preregistration["evidence_declarations"]["peak_memory"] == "MEASURED"

    contract = json.loads((CURRENT_BUNDLE / "expected-contract.json").read_text(encoding="utf-8"))
    evidence = json.loads((CURRENT_BUNDLE / "evidence.json").read_text(encoding="utf-8"))
    assert evidence["version"] == "f03-evidence.v2"
    verification = verify_evidence(
        evidence, contract, carrier_root=CURRENT_BUNDLE, git_root=REPO_ROOT
    )
    assert verification["verified"] is True
    assert verification["errors"] == []
    assert gate2_main([
        "decide", "--input", str(CURRENT_BUNDLE / "evidence.json"),
        "--contract", str(CURRENT_BUNDLE / "expected-contract.json"),
        "--git-root", str(REPO_ROOT),
    ]) == 0
    assert json.loads(capsys.readouterr().out) == receipt["decision"]
    assert receipt["decision_disposition"] == "BR-7"
    assert receipt["decision_notes"] == ["one or more preregistered metric carriers are absent"]
    assert receipt["security_verification"]["verified"] is True

    # Every observation carries closed v2 reason provenance bound to its own
    # identity, and the reconstructed dependency heads prove git resolution.
    for observation in evidence["observations"]:
        provenance = observation["reason_provenance"]
        assert provenance["schema_version"] == "gate2.reason-provenance.v1"
        assert provenance["evidence_identity"] == {
            key: observation[key] for key in provenance["evidence_identity"]
        }
        if observation["status"] == "MEASURED":
            assert provenance["state"] == "MEASURED"
            assert provenance["reason_code"] == "OBSERVED"
            assert observation["evidence_class"] == "MEASURED"
        else:
            assert observation["status"] == "NOT_OBSERVED"
            assert provenance["state"] == "UNAVAILABLE"
            assert provenance["reason_code"] == "SOURCE_UNAVAILABLE"
            assert observation["evidence_class"] is None

    measurements = receipt["measurements"]
    expected_repetitions = preregistration["fault_schedule"]["repetitions"]
    assert expected_repetitions == 2
    assert len(measurements) == len(preregistration["metrics"]) * expected_repetitions
    for observation in measurements:
        assert observation["repetition"] in range(1, expected_repetitions + 1)
        assert observation["freeze_digest"] == freeze_digest
        assert observation["dependencies"] == receipt["dependencies"]
        assert observation["preregistration_digest"] == receipt["preregistration"]["canonical_bytes_sha256"]
        if observation["status"] == "MEASURED":
            carrier = CURRENT_BUNDLE / observation["carrier_path"]
            assert hashlib.sha256(carrier.read_bytes()).hexdigest() == observation["carrier_sha256"]
            assert observation["evidence_class"] == "MEASURED"
            assert observation["value"] <= preregistration["numeric_bounds"][observation["metric_id"]]
        else:
            assert observation["status"] == "NOT_OBSERVED"
            assert observation["value"] is None
            assert observation["carrier_path"] is None
            assert observation["carrier_sha256"] is None

    # Rebuilt fault/refusal evidence comes from real injectors and real refusals,
    # and the receipt binds it by content hash.
    fault_bytes = (CURRENT_BUNDLE / "fault-refusal.json").read_bytes()
    fault_evidence = json.loads(fault_bytes)
    assert receipt["fault_refusal_evidence"]["sha256"] == hashlib.sha256(fault_bytes).hexdigest()
    assert receipt["fault_refusal_evidence"]["case_count"] == len(fault_evidence["cases"])
    assert fault_evidence["all_passed"] is True
    cases = {case["case"]: case for case in fault_evidence["cases"]}
    assert cases["blocked-prerequisite-before-stage"]["observed"]["disposition"] == "PASS"
    assert cases["false-success-swallowed-recovery"]["observed"]["details"]["false_success"] is True
    assert cases["unreachable-class-never-detects"]["observed"]["capability"] == "UNREACHABLE"
    assert cases["e05-receipt-identity-refused"]["observed"]["refused"] is True
    assert cases["tampered-checkpoint-refused"]["observed"]["refused"] is True
    assert cases["unsupported-crash-point-refused"]["observed"]["refused"] is True
