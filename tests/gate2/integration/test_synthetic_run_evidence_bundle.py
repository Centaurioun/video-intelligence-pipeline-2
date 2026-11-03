"""Verify the committed executed-workload evidence bundle (Gate-2 G2.2.1).

The bundle records a real execution of the frozen synthetic workload at a
specific commit.  Artifact payload bytes were verified in-run and then
discarded to keep the repository compact, so this test verifies everything
that remains independently checkable:

* both runs self-verified their own evidence at execution time;
* every reregistered metric has a committed carrier whose hash and value match
  the observation rows, with the declared repetition coverage;
* the two independent invocations agree on all identity digests (fixture,
  workload, configuration, fault schedule, preregistration, artifact manifest,
  decision disposition) while measurements remain observations;
* the durable journals parse under the real fail-closed journal loader with
  full stage completion, and no completion record precedes its artifact;
* the derived disposition is BR-1 (the simpler design met every preregistered
  bound) and no mechanism was adopted;
* archive, model, provider, and production behaviour is declared NOT_OBSERVED.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gate2 import runner


REPO_ROOT = Path(__file__).parents[3]
BUNDLE_ROOT = (
    REPO_ROOT
    / "docs"
    / "agent-runs"
    / "2026-10-25-gate2-reliability-execution"
    / "evidence"
)
RUN_NAMES = ("run-v2", "run-v2-confirmation")


def _receipt(name: str) -> dict:
    return json.loads((BUNDLE_ROOT / name / "receipt.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def receipts() -> dict[str, dict]:
    return {name: _receipt(name) for name in RUN_NAMES}


def test_both_runs_self_verified_at_execution_time(receipts):
    for name, receipt in receipts.items():
        assert receipt["schema"] == runner.RUN_SCHEMA, name
        assert receipt["scope"] == "synthetic_generated_only", name
        assert receipt["security_verification"]["verified"] is True, name
        assert receipt["security_verification"]["errors"] == [], name
        assert receipt["preregistration"]["recorded_before_observations"] is True, name
        assert receipt["safety"] == {
            "production_eligible": False,
            "gate_promotion": False,
            "mechanism_adopted": False,
        }, name
        # The evidence is bound to a real commit and the recorded source digest.
        assert len(receipt["source_binding"]["head_sha"]) == 40, name
        assert len(receipt["source_binding"]["source_digest"]) == 64, name


def test_fault_injection_evidence_was_derived_from_executed_observations(receipts):
    for name, receipt in receipts.items():
        injections = {item["fault_class"]: item for item in receipt["fault_injection"]}
        assert set(injections) == {"H_INTERRUPTED_RECOVERY",
                                   "E_REPEATED_IDEMPOTENCY_KEY"}, name
        for item in injections.values():
            assert item["capability"] == "HARNESSED", name
            assert item["detected"] is True, name
            assert item["disposition"] == "PASS", name
            assert len(item["payload_digest"]) == 64, name
            assert item["evidence_basis"], name


def test_every_preregistered_metric_has_a_matching_committed_carrier(receipts):
    for name, receipt in receipts.items():
        bundle = BUNDLE_ROOT / name
        assert set(receipt["measurement_rows_by_metric"]) == set(runner.METRIC_DEFINITIONS)
        for metric, rows in receipt["measurement_rows_by_metric"].items():
            definition = runner.METRIC_DEFINITIONS[metric]
            assert {row["repetition"] for row in rows} == set(
                range(1, definition["repetitions"] + 1)
            ), f"{name}:{metric} repetition coverage"
            for row in rows:
                assert row["status"] == "MEASURED"
                assert row["evidence_class"] == "MEASURED"
                assert isinstance(row["value"], float) and row["value"] >= 0
                assert row["unit"] == definition["unit"]
                payload = (bundle / row["carrier_path"]).read_bytes()
                assert hashlib.sha256(payload).hexdigest() == row["carrier_sha256"]
                records = json.loads(payload)
                assert any(
                    record["metric_id"] == metric
                    and record["repetition"] == row["repetition"]
                    and record["value"] == row["value"]
                    for record in records
                ), f"{name}:{metric} carrier does not carry the observed value"


def test_identity_is_reproducible_across_independent_invocations(receipts):
    left, right = receipts["run-v2"], receipts["run-v2-confirmation"]
    for key in ("fixture_digest", "generation_id", "workload_digest",
                "config_digest", "fault_schedule_digest", "fault_schedule", "dimensions"):
        assert left["workload_identity"][key] == right["workload_identity"][key], key
    assert left["preregistration"]["digest"] == right["preregistration"]["digest"]
    assert left["integrity"]["artifact_manifest"] == right["integrity"]["artifact_manifest"]
    assert left["decision"]["disposition_digest"] == right["decision"]["disposition_digest"]
    # Measurements are local observations, so whole receipts legitimately differ.
    assert left["receipt_digest"] != right["receipt_digest"]


def test_durable_journals_are_complete_and_ordered(receipts):
    for name in RUN_NAMES:
        bundle = BUNDLE_ROOT / name
        repetitions = receipts[name]["workload_identity"]["dimensions"]["repetitions"]
        stages = (receipts[name]["workload_identity"]["dimensions"]["jobs"]
                  * receipts[name]["workload_identity"]["dimensions"]["stages"])
        for repetition in range(1, repetitions + 1):
            journal_path = bundle / "repetitions" / f"rep-{repetition}" / "journal.jsonl"
            journal = runner.StageJournal.load(journal_path)
            assert journal.completed_stages() == stages
            assert len(journal.entries) == stages
            assert all(state["digest"] for state in journal.entries.values())
            lines = journal_path.read_text(encoding="utf-8").splitlines()
            assert len(lines) == stages * 2


def test_disposition_justifies_no_additional_mechanism(receipts):
    for name, receipt in receipts.items():
        decision = receipt["decision"]
        assert decision["disposition"] == "BR-1", name
        assert decision["notes"] == ["the simpler design met every preregistered bound"]
        assert decision["mechanism_adopted"] is False
        assert decision["production_eligible"] is False
        assert decision["gate_promotion"] is False
        assert "same-run self-verified observations" in decision["decision_scope"]


def test_real_scale_evidence_remains_not_observed(receipts):
    for name, receipt in receipts.items():
        for scope in ("archive reliability", "archive scale", "protected media",
                      "provider/model behavior", "production performance",
                      "storage hardware flush beyond fsync"):
            assert scope in receipt["not_observed"], f"{name}:{scope}"
