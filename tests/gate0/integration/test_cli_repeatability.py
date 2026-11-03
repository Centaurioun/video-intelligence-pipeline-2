import json
import subprocess
import sys

from gate0.repeat import compare_replays, frozen_input_digest, repeat_projection
from gate0.launcher_attestation import encode_attestation
from gate0.stages.preflight import SandboxAttestation


def _run(tmp_path, **changes):
    run = tmp_path / "run-1"
    run.mkdir()
    manifest = {
        "run_id": "run-1",
        "status": "REPORTED",
        "source_revision_ids": ["rev-1"],
        "sample_manifest_digest": "b" * 64,
        "representation_digests": ["c" * 64],
        "ranking_digest": "d" * 64,
        "metrics_digest": "e" * 64,
        "config_digest": "f" * 64,
        "ranked_candidates": [{"candidate_id": "cand-1", "score": 1.0}],
        "runtime": {"python_version": "3.11.9", "timing_ms": 1},
    }
    manifest["frozen_input"] = {key: manifest[key] for key in
                                 ("source_revision_ids", "sample_manifest_digest",
                                  "representation_digests", "ranking_digest",
                                  "metrics_digest", "config_digest")}
    manifest["frozen_input_digests"] = {
        mode: frozen_input_digest(mode, manifest) for mode in ("frozen-index", "full-pipeline")
    }
    manifest["frozen_input_digest"] = manifest["frozen_input_digests"]["frozen-index"]
    manifest.update(changes)
    (run / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return run


def test_repeat_projection_ignores_runtime_observations_but_keeps_identity():
    left = {"candidate_id": "c", "score": 0.5, "runtime": {"timing_ms": 1}}
    right = {"candidate_id": "c", "score": 0.5, "runtime": {"timing_ms": 99}}
    assert repeat_projection(left) == repeat_projection(right)
    assert compare_replays(left, {**right, "candidate_id": "different"}).equal is False


def test_frozen_input_digest_is_ordered_and_mode_bound():
    base = {"source_revision_ids": ["rev"], "sample_manifest_digest": "a" * 64,
            "representation_digests": ["b" * 64], "ranking_digest": "c" * 64,
            "metrics_digest": "d" * 64, "config_digest": "e" * 64}
    assert frozen_input_digest("frozen-index", base) != frozen_input_digest("full-pipeline", base)


def test_repeat_cli_rejects_digest_binding_and_wrong_reported_run(tmp_path):
    run = _run(tmp_path)
    output_root = tmp_path
    command = [sys.executable, "-m", "gate0.cli", "repeat", "--run", str(run),
               "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
               "--output-root", str(output_root), "--run-id", "run-1", "--mode", "frozen-index",
               "--predecessor-run-id", "run-1", "--frozen-input-digest", "0" * 64]
    result = subprocess.run(command, cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 20


def test_repeat_cli_accepts_fresh_process_replay(tmp_path):
    run = _run(tmp_path)
    digest = frozen_input_digest("frozen-index", json.loads((run / "run_manifest.json").read_text()))
    manifest = json.loads((run / "run_manifest.json").read_text())
    manifest["frozen_input_digest"] = digest
    (run / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    command = [sys.executable, "-m", "gate0.cli", "repeat", "--run", str(run),
               "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
               "--output-root", str(tmp_path), "--run-id", "run-1", "--mode", "frozen-index",
               "--predecessor-run-id", "run-1", "--frozen-input-digest", digest]
    result = subprocess.run(command, cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    updated = json.loads((run / "run_manifest.json").read_text())
    assert len(updated["repeat_comparisons"]) == 1
    assert len(updated["attempts"]) == 1
    assert len(updated["stage_transitions"]) == 2


def test_repeat_cli_rejects_unreported_status(tmp_path):
    run = _run(tmp_path, status="SUCCEEDED")
    digest = frozen_input_digest("frozen-index", json.loads((run / "run_manifest.json").read_text()))
    command = [sys.executable, "-m", "gate0.cli", "repeat", "--run", str(run),
               "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
               "--output-root", str(tmp_path), "--run-id", "run-1", "--mode", "frozen-index",
               "--predecessor-run-id", "run-1", "--frozen-input-digest", digest]
    result = subprocess.run(command, cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 20


def test_repeat_cli_rejects_top_level_identity_tampering(tmp_path):
    run = _run(tmp_path)
    manifest = json.loads((run / "run_manifest.json").read_text())
    manifest["source_revision_ids"] = ["tampered"]
    (run / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    command = [sys.executable, "-m", "gate0.cli", "repeat", "--run", str(run),
               "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
               "--output-root", str(tmp_path), "--run-id", "run-1", "--mode", "frozen-index",
               "--predecessor-run-id", "run-1", "--frozen-input-digest", manifest["frozen_input_digest"]]
    result = subprocess.run(command, cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 20


def test_repeat_cli_supports_full_pipeline_against_same_reported_manifest(tmp_path):
    run = _run(tmp_path)
    manifest = json.loads((run / "run_manifest.json").read_text())
    digest = manifest["frozen_input_digests"]["full-pipeline"]
    command = [sys.executable, "-m", "gate0.cli", "repeat", "--run", str(run),
               "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
               "--output-root", str(tmp_path), "--run-id", "run-1", "--mode", "full-pipeline",
               "--predecessor-run-id", "run-1", "--frozen-input-digest", digest]
    result = subprocess.run(command, cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    updated = json.loads((run / "run_manifest.json").read_text())
    assert updated["repeat_comparisons"][-1]["mode"] == "full-pipeline"
    assert len(updated["stage_transitions"]) == 2


def test_repeat_cli_rejects_malformed_comparison_records(tmp_path):
    run = _run(tmp_path, repeat_comparisons=["not-a-record"])
    manifest = json.loads((run / "run_manifest.json").read_text())
    command = [sys.executable, "-m", "gate0.cli", "repeat", "--run", str(run),
               "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
               "--output-root", str(tmp_path), "--run-id", "run-1", "--mode", "frozen-index",
               "--predecessor-run-id", "run-1", "--frozen-input-digest", manifest["frozen_input_digest"]]
    result = subprocess.run(command, cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 20


def test_repeat_cli_rejects_partial_mode_comparison_map(tmp_path):
    run = _run(tmp_path)
    manifest = json.loads((run / "run_manifest.json").read_text())
    manifest["repeat_comparisons"] = [{"mode": "frozen-index", "equal": True}]
    (run / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    digest = manifest["frozen_input_digests"]["full-pipeline"]
    command = [sys.executable, "-m", "gate0.cli", "repeat", "--run", str(run),
               "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
               "--output-root", str(tmp_path), "--run-id", "run-1", "--mode", "full-pipeline",
               "--predecessor-run-id", "run-1", "--frozen-input-digest", digest]
    result = subprocess.run(command, cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 20


def test_cli_rejects_unknown_or_out_of_order_stage():
    result = subprocess.run([sys.executable, "-m", "gate0.cli", "bogus"],
                            cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 40


def test_cli_blocks_nonrepeat_stage_until_durable_predecessor(tmp_path):
    run = tmp_path / "run-1"; run.mkdir()
    (run / "run_manifest.json").write_text(json.dumps({"run_id": "run-1", "stage_transitions": []}), encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "gate0.cli", "inventory", "--run", str(run),
                             "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
                             "--output-root", str(tmp_path), "--run-id", "run-1"],
                            cwd=__file__.split("/tests/")[0], text=True, capture_output=True)
    assert result.returncode == 20
    assert json.loads(result.stdout)["reason"] == "STAGE_PREDECESSOR"


def test_cli_preflight_binds_attestation_and_four_child_sentinels(tmp_path):
    run = tmp_path / "run-1"; run.mkdir()
    transition = {"transition_id": "transition-label", "run_id": "run-1", "attempt_id": "attempt-label",
                  "stage": "label", "from_status": "RUNNING", "to_status": "SUCCEEDED"}
    manifest = {"run_id": "run-1", "stage_transitions": [transition], "policy_decision_ids": ["policy_process"]}
    (run / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run / "runtime_and_failure_ledger.json").write_text(json.dumps({"schema_version": "gate0.runtime_and_failure_ledger.v1", "events": []}), encoding="utf-8")
    attestation = encode_attestation(SandboxAttestation.synthetic("0" * 64))
    env = {**__import__("os").environ, "GATE0_SANDBOX_ATTESTATION_JSON": attestation, "GATE0_CHILD_NETWORK_SENTINEL": "1"}
    result = subprocess.run([sys.executable, "-m", "gate0.cli", "preflight", "--run", str(run),
                             "--config", "config/gate0/default.json", "--input-root", str(tmp_path),
                             "--output-root", str(tmp_path), "--run-id", "run-1"],
                            cwd=__file__.split("/tests/")[0], text=True, capture_output=True, env=env)
    assert result.returncode == 20
    assert json.loads(result.stdout)["status"] == "NOT_OBSERVED"
    bound = json.loads((run / "run_manifest.json").read_text())
    ledger = json.loads((run / "runtime_and_failure_ledger.json").read_text())
    assert bound["sandbox"]["argv_digest"] == "5034e67ec47676b9dcb85dfa9595cc91a2687a1bdea0f8a4d776f77a80e0fa8e"
    assert len(ledger["events"]) == 4
    assert {event["protocol"] for event in ledger["events"]} == {"DNS", "HTTP_PROXY", "PROVIDER", "LOOPBACK"}
