"""Executed, measured synthetic workload evidence (Gate-2 G2.2.1).

These tests run the bounded frozen synthetic workload through the real
``gate2.runner`` execution path: durable per-stage materialization, the
fixture's preregistered interruption, resume from the persisted journal in a
fresh executor instance, local environment measurement, and a same-run
``gate2.decision.decide`` disposition preview.

Every number observed here is a local synthetic observation of this test host.
It is never production performance and never archive scale evidence.
"""
import hashlib
import json
import math
import subprocess
from pathlib import Path

import pytest

from gate2 import runner


REPO_ROOT = Path(__file__).parents[3]


def _git(*args):
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _head():
    return _git("rev-parse", "HEAD")


def _run(tmp_path, name="run", **kwargs):
    return runner.execute_and_emit(tmp_path / name, expect_head=_head(), **kwargs)


def test_bounded_run_measures_every_preregistered_metric(tmp_path):
    receipt = _run(tmp_path, discard_artifacts=True)

    assert receipt["schema"] == runner.RUN_SCHEMA
    assert receipt["scope"] == "synthetic_generated_only"
    assert receipt["safety"] == {
        "production_eligible": False,
        "gate_promotion": False,
        "mechanism_adopted": False,
    }
    assert receipt["source_binding"]["head_sha"] == _head()
    assert receipt["preregistration"]["recorded_before_observations"] is True

    rows = receipt["measurements"]
    assert {row["metric_id"] for row in rows} == set(runner.METRIC_DEFINITIONS)
    for row in rows:
        assert row["status"] == "MEASURED"
        assert row["evidence_class"] == "MEASURED"
        assert isinstance(row["value"], (int, float)) and not isinstance(row["value"], bool)
        assert math.isfinite(row["value"]) and row["value"] >= 0
        assert row["unit"] and row["unit"] != "n/a"
        assert 1 <= row["repetition"] <= runner.FROZEN_DIMENSIONS["repetitions"]
        carrier = (tmp_path / "run" / row["carrier_path"]).read_bytes()
        assert hashlib.sha256(carrier).hexdigest() == row["carrier_sha256"]
        assert json.loads(carrier)  # carriers are real non-empty observations

    # The produced evidence is self-verified before any disposition is derived.
    assert receipt["security_verification"]["verified"] is True
    assert receipt["security_verification"]["errors"] == []

    # Every preregistered bound is met by the simpler design; nothing here
    # justifies adding a mechanism.
    assert receipt["decision"]["disposition"] == "BR-1"
    assert receipt["decision"]["notes"] == ["the simpler design met every preregistered bound"]
    assert receipt["decision"]["mechanism_adopted"] is False
    assert receipt["decision"]["production_eligible"] is False
    assert receipt["decision"]["gate_promotion"] is False

    # Throughput and job outcomes are reported as descriptive run observations.
    derived = receipt["derived_observations"]
    assert derived["job_completion"] == {
        "jobs_total": runner.FROZEN_DIMENSIONS["jobs"],
        "jobs_completed": runner.FROZEN_DIMENSIONS["jobs"],
        "failure_outcomes": [],
    }
    assert len(derived["stage_throughput_stages_per_second"]) == 3
    assert all(value > 0 for value in derived["stage_throughput_stages_per_second"])

    # Existing fault-class API evaluated from this run's executed observations.
    injections = {item["fault_class"]: item for item in receipt["fault_injection"]}
    assert set(injections) == {"H_INTERRUPTED_RECOVERY", "E_REPEATED_IDEMPOTENCY_KEY"}
    for item in injections.values():
        assert item["capability"] == "HARNESSED"
        assert item["detected"] is True
        assert item["disposition"] == "PASS"
        assert len(item["payload_digest"]) == 64
    assert injections["H_INTERRUPTED_RECOVERY"]["details"]["false_success"] is False

    # Real archives, models, providers, and production remain unobserved.
    assert "archive scale" in receipt["not_observed"]
    assert "provider/model behavior" in receipt["not_observed"]


def test_interruption_resumes_from_journal_without_duplicate_writes(tmp_path):
    receipt = _run(tmp_path, discard_artifacts=True)
    stages_total = runner.FROZEN_DIMENSIONS["jobs"] * runner.FROZEN_DIMENSIONS["stages"]

    for repetition in receipt["repetitions"]:
        assert repetition["interruption"]["observed"] is True
        assert repetition["interruption"]["crash_point"] == "after_side_effect_before_completion"
        assert repetition["resume"]["recovered_stages"] == 1
        assert repetition["resume"]["idempotent_replays"] == 1
        assert repetition["resume"]["duplicate_writes"] == 0
        assert repetition["stages_completed"] == stages_total
        assert repetition["integrity"]["mismatches"] == 0
    assert receipt["integrity"]["duplicate_writes_total"] == 0


def test_integrity_verification_detects_tampered_artifacts(tmp_path):
    receipt = _run(tmp_path, discard_artifacts=False)
    assert receipt["integrity"]["artifacts_verified"] > 0

    rep_dir = tmp_path / "run" / "repetitions" / "rep-1"
    artifacts = sorted(rep_dir.glob("artifacts/**/*.bin"))
    assert artifacts
    tampered = artifacts[0]
    payload = bytearray(tampered.read_bytes())
    payload[0] ^= 0xFF
    tampered.write_bytes(bytes(payload))

    verification = runner.verify_persisted_artifacts(rep_dir)
    assert verification["mismatches"] == 1
    assert verification["verified"] is False


def test_stale_base_is_refused_before_any_measurement(tmp_path):
    with pytest.raises(runner.RunRefusal):
        runner.execute_and_emit(tmp_path / "run", expect_head="0" * 40)
    assert not (tmp_path / "run").exists()


def test_repeated_runs_reproduce_identity_but_not_wall_clock(tmp_path):
    first = _run(tmp_path, "first", discard_artifacts=True)
    second = _run(tmp_path, "second", discard_artifacts=True)

    assert first["workload_identity"]["fixture_digest"] == second["workload_identity"]["fixture_digest"]
    assert first["integrity"]["artifact_manifest"] == second["integrity"]["artifact_manifest"]
    assert first["preregistration"]["digest"] == second["preregistration"]["digest"]
    assert first["decision"]["disposition_digest"] == second["decision"]["disposition_digest"]
    # Wall clock is an observation, not reproducible identity.
    assert "wall_time" not in json.dumps(first["workload_identity"])
    assert first["repeatability"]["artifact_manifests_identical"] is True
    assert first["repeatability"]["fixture_digest_identical"] is True


def test_cli_run_executes_and_reports_disposition(tmp_path, capsys):
    from gate2.cli import main

    out = tmp_path / "cli-run"
    assert main(["run", "--out", str(out), "--expect-head", _head(),
                 "--discard-artifacts"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["schema"] == runner.RUN_SCHEMA
    assert printed["decision"]["disposition"] == "BR-1"
    assert printed["security_verification"]["verified"] is True


def test_cli_run_refuses_stale_base(tmp_path, capsys):
    from gate2.cli import main

    assert main(["run", "--out", str(tmp_path / "cli-stale"), "--expect-head", "0" * 40]) == 2
    assert "gate2: " in capsys.readouterr().err
    assert not (tmp_path / "cli-stale").exists()
