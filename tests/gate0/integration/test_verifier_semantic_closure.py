import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests/gate0/fixtures/semantic-closure"


def run(root, *flags):
    return subprocess.run([sys.executable, "scripts/verify-gate0.py", *flags, "--candidate-root", str(root)], cwd=ROOT, text=True, capture_output=True)


def clone(tmp_path):
    dst = tmp_path / "candidate"
    shutil.copytree(FIXTURE, dst)
    return dst


def test_complete_candidate_is_semantically_closed(tmp_path):
    result = run(clone(tmp_path), "--foreign-keys", "--manifest-closure", "--synthetic-only")
    assert result.returncode == 0, result.stderr
    assert "foreign_keys=PASS" in result.stdout
    assert "manifest_closure=PASS" in result.stdout
    assert "structural gate" not in result.stdout


def test_foreign_keys_without_candidate_root_fails_closed():
    result = subprocess.run([sys.executable, "scripts/verify-gate0.py", "--foreign-keys"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 30
    assert "candidate-root" in result.stderr


def test_wrong_dependency_digest_fails(tmp_path):
    root = clone(tmp_path)
    path = root / "run_manifest.json"
    data = json.loads(path.read_text())
    data["artifact_envelopes"][9]["input_artifact_refs"][0]["payload_digest"] = "0" * 64
    path.write_text(json.dumps(data))
    result = run(root, "--foreign-keys")
    assert result.returncode == 30
    assert "digest" in result.stderr


def test_missing_sentinel_protocol_fails(tmp_path):
    root = clone(tmp_path)
    path = root / "runtime_and_failure_ledger.json"
    data = json.loads(path.read_text())
    data["events"] = [e for e in data["events"] if e.get("protocol") != "PROVIDER"]
    path.write_text(json.dumps(data))
    result = run(root, "--foreign-keys")
    assert result.returncode == 30
    assert "sentinel" in result.stderr


def test_sentinel_attempt_must_be_preflight(tmp_path):
    root = clone(tmp_path)
    path = root / "run_manifest.json"
    data = json.loads(path.read_text())
    data["attempts"][0]["stage"] = "inventory"
    path.write_text(json.dumps(data))
    result = run(root, "--foreign-keys")
    assert result.returncode == 30
    assert "preflight" in result.stderr


def test_incomplete_sandbox_attestation_fails_closed(tmp_path):
    root = clone(tmp_path)
    path = root / "run_manifest.json"
    data = json.loads(path.read_text())
    del data["sandbox"]["bwrap_digest"]
    path.write_text(json.dumps(data))
    result = run(root, "--foreign-keys")
    assert result.returncode == 30
    assert "sandbox attestation" in result.stderr


def test_extra_result_file_is_rejected(tmp_path):
    root = clone(tmp_path)
    (root / "unexpected.json").write_text("{}")
    result = run(root, "--foreign-keys")
    assert result.returncode == 30
