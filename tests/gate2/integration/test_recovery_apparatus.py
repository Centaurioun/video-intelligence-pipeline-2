"""Contract-level falsification tests for the synthetic recovery apparatus.

The public recovery seam is deliberately loaded through an assertion so this
file collects cleanly while the implementation lane is still working.
"""
from __future__ import annotations

import importlib
import importlib.util
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest


def recovery_api():
    spec = importlib.util.find_spec("gate2.recovery")
    assert spec is not None, "missing public gate2.recovery module/API"
    module = importlib.import_module("gate2.recovery")
    required = ("RecoveryBinding", "RecoveryHarness", "RecoveryRefusal")
    missing = [name for name in required if not hasattr(module, name)]
    assert not missing, f"recovery API missing: {missing}"
    return module


def binding(api, **updates):
    fields = dict(
        f01_sha="345f9526d54f4fbd582c15f4f0b613bc8ab3996e",
        c04_sha="5d482a1016b97d663c57ad31d8bac21c19c8c799",
        e05_sha="e52b91d38a9f9c6651a4203eccbe59b03d908905",
        workload_digest="1" * 64,
        configuration_digest="2" * 64,
        previous_manifest_digest="3" * 64,
        current_manifest_digest="4" * 64,
        generation_id="generation:fixture-1",
        semantic_space_id="space:fixture-1",
        receipt_identity="receipt:fixture-1",
    )
    fields.update(updates)
    return api.RecoveryBinding(**fields)


def test_binding_accepts_real_accepted_f01_digest_and_rejects_non_digest():
    from gate2.verify import _ACCEPTED_DEPENDENCY_HEADS

    accepted = _ACCEPTED_DEPENDENCY_HEADS["F01"]["sha"]
    api = recovery_api()
    assert binding(api, f01_sha=accepted).f01_sha == accepted
    # A SHA-1 accepted generation is a 40-hex digest; an uppercase or truncated
    # value must not be silently accepted as the same identity.
    with pytest.raises(ValueError):
        binding(api, f01_sha=accepted.upper())
    with pytest.raises(ValueError):
        binding(api, f01_sha=accepted[:-1])


class FakeC04Adapter:
    """A small C04-journal stand-in; all operation truth stays here."""

    def __init__(self, operations=("op:add", "op:update")):
        self.events = []
        self.operations = tuple(operations)
        self.completed = set()
        self.side_effects = []
        self._state = {"canonical_rows": []}

    def validate_receipt(self, receipt_identity):
        self.events.append(("validate_receipt", receipt_identity))
        return receipt_identity == "receipt:fixture-1"

    def reconcile_sqlite_tail(self):
        self.events.append("sqlite_tail")

    def start_or_resume(self, bound):
        self.events.append("c04_start_or_resume")
        self.bound = bound
        return self.operations

    def is_complete(self, operation_id):
        return operation_id in self.completed

    def apply_idempotent(self, operation_id):
        self.events.append(("apply", operation_id))
        if operation_id not in self.side_effects:
            self.side_effects.append(operation_id)
            self._state["canonical_rows"].append(operation_id)

    def mark_complete(self, operation_id):
        self.events.append(("mark_complete", operation_id))
        self.completed.add(operation_id)

    def state_digest(self):
        import hashlib

        return hashlib.sha256(json.dumps(self._state, sort_keys=True).encode()).hexdigest()


def report_value(report, key):
    return report[key] if isinstance(report, dict) else getattr(report, key)


def test_public_recovery_api_is_present_without_collection_import_failure():
    recovery_api()


def test_sqlite_tail_reconciles_before_c04_journal_and_adapter_owns_completion(tmp_path):
    api = recovery_api()
    adapter = FakeC04Adapter()
    bound = binding(api)
    harness = api.RecoveryHarness.open(tmp_path / "apparatus.json", bound, adapter)
    report = harness.run()
    assert adapter.events[:3] == [
        ("validate_receipt", bound.receipt_identity), "sqlite_tail", "c04_start_or_resume"
    ]
    assert adapter.events.index("sqlite_tail") < adapter.events.index("c04_start_or_resume")
    assert {event[1] for event in adapter.events if isinstance(event, tuple) and event[0] == "mark_complete"} == set(adapter.operations)
    assert all(adapter.is_complete(op) for op in adapter.operations)
    assert report_value(report, "operation_count") == len(adapter.operations)


def test_invalid_e05_receipt_refuses_before_sqlite_recovery_journal_or_writes(tmp_path):
    api = recovery_api()
    adapter = FakeC04Adapter()
    harness = api.RecoveryHarness.open(
        tmp_path / "apparatus.json", binding(api, receipt_identity="receipt:stale"), adapter
    )
    with pytest.raises(api.RecoveryRefusal):
        harness.run()
    assert adapter.events == [("validate_receipt", "receipt:stale")]
    assert adapter.side_effects == []


def test_e05_verifier_and_refused_receipt_block_recovery_before_tail_or_c04(tmp_path):
    """Current FVS refusal evidence is consumed before any recovery side effect."""
    from vip_fvs.local_preview import PreviewArtifact
    from vip_fvs.real_preview_receipt import RealPreviewReceipt, load_real_preview_receipt, save_real_preview_receipt
    from vip_fvs.real_preview_verifier import verify_preview

    source, output = tmp_path / "source.fixture", tmp_path / "preview.fixture"
    source.write_bytes(b"generated source fixture")
    output.write_bytes(b"generated preview fixture")
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    output_digest = hashlib.sha256(output.read_bytes()).hexdigest()
    artifact = PreviewArtifact(
        output, output.stat().st_size, output_digest, source_digest, source_digest,
        source.stat().st_size, source.stat().st_size, "fixture-revision", 0, 1, 1000,
        0, 30, "p" * 64, "l" * 64, "m" * 64, "a" * 64, ("ffprobe",), ("ffmpeg",),
        {"sha256": "b" * 64}, {"sha256": "c" * 64}, producer_attempt_id="attempt-1",
    )
    with pytest.raises(ValueError, match="ATTEMPT_MISMATCH") as verifier_failure:
        verify_preview(artifact, source_path=source, attempt_id="attempt-1")

    verifier_evidence = {
        "schema": "vip_fvs.preview_verifier_refusal.v1",
        "error_type": type(verifier_failure.value).__name__,
        "error": str(verifier_failure.value),
        "attempt_id": "attempt-1",
        "producer_attempt_id": artifact.producer_attempt_id,
        "artifact_identity": {
            "output_sha256": artifact.output_sha256,
            "source_sha256_before": artifact.source_sha256_before,
            "source_sha256_after": artifact.source_sha256_after,
            "producer_attempt_id": artifact.producer_attempt_id,
        },
        "source_sha256": source_digest,
        "output_sha256": output_digest,
    }
    verifier_evidence_bytes = json.dumps(
        verifier_evidence, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    verifier_evidence_digest = hashlib.sha256(verifier_evidence_bytes).hexdigest()
    verifier_evidence_path = tmp_path / "verifier-refusal.json"
    verifier_evidence_path.write_bytes(verifier_evidence_bytes)

    digest = "a" * 64
    record = {
        "schema": "vip_fvs.real_preview_receipt.v1", "receipt_id": "preview-receipt:attempt-1",
        "run_id": "run:fixture", "attempt_id": "attempt-1", "status": "REFUSED",
        "scope": "LOCAL_REAL_NON_PRODUCTION_PREVIEW",
        "source": {"source_revision_id": "fixture-revision", "source_sha256": source_digest,
                   "source_byte_count": source.stat().st_size, "selected_stream_index": 0,
                   "timebase": {"num": 1, "den": 1000}},
        "lifecycle": {"review_bundle_ref": "bundle:fixture", "review_bundle_digest": digest,
                      "review_bundle_dependency_digest": digest, "decision_ref": "decision:fixture",
                      "decision_digest": digest, "plan_ref": "plan:fixture", "plan_digest": digest,
                      "placement_digest": digest, "mapping_digest": digest},
        "authorization": {"authorization_id": "auth:fixture", "authorization_digest": digest,
                          "policy_identity": "policy:preview", "scope": "NON_PRODUCTION_PREVIEW"},
        "preview": {"output_ref": str(output), "output_sha256": output_digest,
                    "output_byte_count": output.stat().st_size, "source_sha256_before": source_digest,
                    "source_sha256_after": source_digest, "source_byte_count_before": source.stat().st_size,
                    "source_byte_count_after": source.stat().st_size, "source_start_pts": 0,
                    "source_end_pts": 30, "preview_digest": digest},
        "verifier": {"status": "FAIL", "attempt_id": "attempt-1", "digest": verifier_evidence_digest,
                     "artifact_ref": str(verifier_evidence_path), "evidence_class": "MEASURED"},
        "technical_qc": {"status": "NOT_OBSERVED", "attempt_id": "attempt-1", "digest": digest,
                         "artifact_ref": "qc:not-observed", "evidence_class": "MEASURED"},
        "tooling": {"ffprobe_digest": digest, "ffmpeg_digest": digest,
                    "configuration_digest": digest},
        "production_eligible": False, "export_eligible": False,
        "NOT_OBSERVED": ["visual inspection", "audio inspection"],
    }
    receipt = RealPreviewReceipt.create(record)
    assert receipt.record["verifier"]["digest"] == verifier_evidence_digest
    assert hashlib.sha256(verifier_evidence_path.read_bytes()).hexdigest() == receipt.record["verifier"]["digest"]
    receipt_path = save_real_preview_receipt(receipt, tmp_path / "refused-receipt.json")
    loaded_receipt = load_real_preview_receipt(receipt_path)

    class ReceiptBoundAdapter(FakeC04Adapter):
        def validate_receipt(self, receipt_identity):
            self.events.append(("validate_receipt", receipt_identity))
            verifier_record = json.loads(Path(loaded_receipt.record["verifier"]["artifact_ref"]).read_text())
            self.refusal_matches_failure = (
                receipt_identity == loaded_receipt.record_digest
                and loaded_receipt.record["status"] == "REFUSED"
                and loaded_receipt.record["verifier"]["status"] == "FAIL"
                and hashlib.sha256(Path(loaded_receipt.record["verifier"]["artifact_ref"]).read_bytes()).hexdigest()
                == loaded_receipt.record["verifier"]["digest"]
                and verifier_record["error"] == "ATTEMPT_MISMATCH"
                and verifier_record["error_type"] == "ValueError"
                and verifier_record["attempt_id"] == loaded_receipt.record["attempt_id"] == "attempt-1"
                and verifier_record["producer_attempt_id"] == artifact.producer_attempt_id
                and verifier_record["artifact_identity"]["producer_attempt_id"] == artifact.producer_attempt_id
                and verifier_record["artifact_identity"]["source_sha256_before"] == artifact.source_sha256_before
                and verifier_record["artifact_identity"]["source_sha256_after"] == artifact.source_sha256_after
                and verifier_record["artifact_identity"]["output_sha256"] == output_digest
                and verifier_record["source_sha256"] == loaded_receipt.record["source"]["source_sha256"]
                and verifier_record["source_sha256"] == loaded_receipt.record["preview"]["source_sha256_before"]
                and verifier_record["source_sha256"] == loaded_receipt.record["preview"]["source_sha256_after"]
                and verifier_record["output_sha256"] == loaded_receipt.record["preview"]["output_sha256"]
            )
            return not self.refusal_matches_failure

    api = recovery_api()
    adapter = ReceiptBoundAdapter()
    harness = api.RecoveryHarness.open(
        tmp_path / "apparatus.json", binding(api, receipt_identity=loaded_receipt.record_digest), adapter
    )
    with pytest.raises(api.RecoveryRefusal, match="E05 receipt identity was refused"):
        harness.run()
    assert adapter.events == [("validate_receipt", loaded_receipt.record_digest)]
    assert adapter.refusal_matches_failure is True
    assert adapter.side_effects == []


def test_accepted_e05_receipt_validation_precedes_tail_recovery_and_all_writes(tmp_path):
    api = recovery_api()
    adapter = FakeC04Adapter()
    harness = api.RecoveryHarness.open(tmp_path / "apparatus.json", binding(api), adapter)
    harness.run()
    labels = [event if isinstance(event, str) else event[0] for event in adapter.events]
    assert adapter.events[:3] == [
        ("validate_receipt", "receipt:fixture-1"), "sqlite_tail", "c04_start_or_resume"
    ]
    assert labels.index("validate_receipt") < labels.index("sqlite_tail")
    assert labels.index("validate_receipt") < labels.index("c04_start_or_resume")
    assert labels.index("validate_receipt") < labels.index("apply")


@pytest.mark.parametrize("field", ["f01_sha", "c04_sha", "e05_sha", "workload_digest", "configuration_digest"])
def test_exact_dependency_and_workload_binding_refuses_stale_identity(tmp_path, field):
    api = recovery_api()
    path = tmp_path / "apparatus.json"
    first = binding(api)
    api.RecoveryHarness.open(path, first, FakeC04Adapter())
    stale = replace(first, **{field: "f" * 64})
    with pytest.raises(api.RecoveryRefusal):
        api.RecoveryHarness.open(path, stale, FakeC04Adapter())


@pytest.mark.parametrize("field", ["previous_manifest_digest", "current_manifest_digest", "generation_id", "semantic_space_id", "receipt_identity"])
def test_stale_manifest_generation_space_or_receipt_refuses_resume(tmp_path, field):
    api = recovery_api()
    path = tmp_path / "apparatus.json"
    first = binding(api)
    api.RecoveryHarness.open(path, first, FakeC04Adapter())
    stale_value = "stale:" + field if field.endswith("_id") or field == "receipt_identity" else "f" * 64
    with pytest.raises(api.RecoveryRefusal):
        api.RecoveryHarness.open(path, replace(first, **{field: stale_value}), FakeC04Adapter())


@pytest.mark.parametrize("payload", [b"{", b"{}\ntrailing", b'{"schema":"partial"}'])
def test_corrupt_or_partial_checkpoint_fails_closed(tmp_path, payload):
    api = recovery_api()
    path = tmp_path / "apparatus.json"
    path.write_bytes(payload)
    with pytest.raises(api.RecoveryRefusal):
        api.RecoveryHarness.open(path, binding(api), FakeC04Adapter())


@pytest.mark.parametrize("crash_point", ["before_action", "after_side_effect_before_completion"])
def test_restart_replay_converges_without_duplicate_canonical_writes(tmp_path, crash_point):
    api = recovery_api()
    path = tmp_path / "apparatus.json"
    adapter = FakeC04Adapter(("op:only",))
    harness = api.RecoveryHarness.open(path, binding(api), adapter)
    with pytest.raises((RuntimeError, SystemExit)):
        harness.run(crash_point=crash_point)
    resumed = api.RecoveryHarness.open(path, binding(api), adapter)
    resumed.run()
    assert adapter._state["canonical_rows"] == ["op:only"]
    assert adapter.side_effects == ["op:only"]
    assert adapter.is_complete("op:only")


def test_checkpoint_contains_measurements_not_second_journal_or_provenance(tmp_path):
    api = recovery_api()
    path = tmp_path / "apparatus.json"
    harness = api.RecoveryHarness.open(path, binding(api), FakeC04Adapter())
    harness.run()
    record = json.loads(path.read_text())
    encoded = json.dumps(record, sort_keys=True).lower()
    assert "operations" not in record
    assert "provenance" not in encoded and "source_revision" not in encoded
    assert "pre_state_digest" in encoded and "post_state_digest" in encoded
    assert "attempt" in encoded and "checkpoint" in encoded


def test_report_carries_explicit_not_observed_scopes_and_deterministic_digests(tmp_path):
    api = recovery_api()
    binding_value = binding(api)
    adapter_a, adapter_b = FakeC04Adapter(), FakeC04Adapter()
    report_a = api.RecoveryHarness.open(tmp_path / "a.json", binding_value, adapter_a).run()
    report_b = api.RecoveryHarness.open(tmp_path / "b.json", binding_value, adapter_b).run()
    for key in ("attempts", "checkpoints", "pre_state_digest", "post_state_digest", "NOT_OBSERVED"):
        assert report_value(report_a, key) == report_value(report_b, key)
    not_observed = report_value(report_a, "NOT_OBSERVED")
    assert {"archive reliability", "archive scale", "wall clock", "protected media", "provider/model behavior"} <= set(not_observed)
    assert all(not_observed[scope] == "NOT_OBSERVED" for scope in (
        "archive reliability", "archive scale", "wall clock", "protected media", "provider/model behavior"
    ))


def test_not_yet_harnessed_and_unreachable_faults_never_report_pass():
    from gate2.faults import Capability, FaultClass, capability, inject

    unavailable = [
        fault for fault in FaultClass
        if capability(fault) in {Capability.NOT_YET_HARNESSED, Capability.UNREACHABLE}
    ]
    assert unavailable
    for fault in unavailable:
        result = inject(fault, {"synthetic": True})
        assert result.disposition == capability(fault).value
        assert result.disposition != "PASS"


def test_recovery_run_does_not_touch_protected_media_network_or_model_runtime(tmp_path, monkeypatch):
    api = recovery_api()
    def forbidden(*_args, **_kwargs):
        raise AssertionError("external or protected activity is forbidden in synthetic recovery")

    import socket

    monkeypatch.setattr(socket, "create_connection", forbidden)
    adapter = FakeC04Adapter()
    harness = api.RecoveryHarness.open(tmp_path / "apparatus.json", binding(api), adapter)
    harness.run()
    assert adapter.events[:2] == [
        ("validate_receipt", "receipt:fixture-1"), "sqlite_tail"
    ]
