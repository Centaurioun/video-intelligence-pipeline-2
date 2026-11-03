"""S-10: three-arm artifact closure verification, receipt binding, and tamper tests."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from gate1.harness import run_generated_three_arm_case
from gate1.verify import VerificationError, verify_path, verify_synthetic_only


REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT = "three_arm_compat_report.json"
RECEIPT = "three_arm_compat_receipt.json"


def _canonical_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _resync_receipt(output: Path) -> None:
    report_bytes = (output / REPORT).read_bytes()
    receipt = json.loads((output / RECEIPT).read_text())
    receipt["report_sha256"] = hashlib.sha256(report_bytes).hexdigest()
    (output / RECEIPT).write_bytes(_canonical_bytes(receipt))


def _artifact(tmp_path: Path) -> Path:
    output = tmp_path / "three-arm"
    run_generated_three_arm_case("positive_one_axis", output)
    return output


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(REPO_ROOT / "src"), str(REPO_ROOT)))
    return subprocess.run(
        [sys.executable, "-m", "gate1.cli", *args],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True,
    )


def test_fresh_three_arm_artifact_closure_verifies(tmp_path):
    output = _artifact(tmp_path)
    assert {path.name for path in output.iterdir()} == {REPORT, RECEIPT}
    verify_path(output)


def test_cli_verify_generated_accepts_three_arm_artifact(tmp_path):
    output = _artifact(tmp_path)
    result = _run_cli("verify-generated", "--artifact-dir", str(output))
    assert result.returncode == 0
    assert "verified" in result.stdout


def test_cli_verify_generated_rejects_tampered_three_arm_artifact(tmp_path):
    output = _artifact(tmp_path)
    report_path = output / REPORT
    report = json.loads(report_path.read_text())
    report["evidence_status"] = "MODEL_EVIDENCE"
    report_path.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n")
    result = _run_cli("verify-generated", "--artifact-dir", str(output))
    assert result.returncode != 0
    assert "error:" in result.stderr


def _mutate_report(path: Path, mutate) -> None:
    report = json.loads(path.read_text())
    mutate(report)
    path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def _mutate_receipt(path: Path, mutate) -> None:
    receipt = json.loads(path.read_text())
    mutate(receipt)
    path.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


TAMPERS = {
    "evidence_promotion": lambda report_path, receipt_path: _mutate_report(
        report_path, lambda r: r.update(evidence_status="MODEL_EVIDENCE")),
    "winner_claim": lambda report_path, receipt_path: _mutate_report(
        report_path, lambda r: r.update(winner_status="VIP_V2_BASE")),
    "dropped_pair": lambda report_path, receipt_path: _mutate_report(
        report_path, lambda r: r["pairwise_evaluations"].pop()),
    "outcome_inversion": lambda report_path, receipt_path: _mutate_report(
        report_path, lambda r: r["pairwise_evaluations"][0].update(outcome="NOT_EVALUATED")),
    "b07_false_reason": lambda report_path, receipt_path: _mutate_report(
        report_path, lambda r: r["b07_metric_states"][1].update(reason="ZERO_IDCG")),
    "code_sha_scrambled": lambda report_path, receipt_path: _mutate_report(
        report_path, lambda r: r.update(code_sha="0" * 64)),
    "limitation_dropped": lambda report_path, receipt_path: _mutate_report(
        report_path, lambda r: r.update(limitations=["SYNTHETIC_PROTOCOL_COMPATIBILITY_ONLY"])),
    "receipt_sha_mismatch": lambda report_path, receipt_path: _mutate_receipt(
        receipt_path, lambda r: r.update(report_sha256="0" * 64)),
    "receipt_evidence_promotion": lambda report_path, receipt_path: _mutate_receipt(
        receipt_path, lambda r: r.update(evidence_status="MODEL_EVIDENCE")),
    "receipt_real_execution_claim": lambda report_path, receipt_path: _mutate_receipt(
        receipt_path, lambda r: r.update(real_benchmark_executed=True)),
    "receipt_gate_promotion": lambda report_path, receipt_path: _mutate_receipt(
        receipt_path, lambda r: r.update(gate_promotion=True)),
    "report_whitespace": lambda report_path, receipt_path: report_path.write_text(
        report_path.read_text().replace(",", ", ", 1)),
}


@pytest.mark.parametrize("tamper", sorted(TAMPERS))
def test_tampered_three_arm_artifact_fails_verification(tmp_path, tamper):
    output = _artifact(tmp_path)
    TAMPERS[tamper](output / REPORT, output / RECEIPT)
    with pytest.raises(VerificationError):
        verify_path(output)


def test_missing_or_extra_closure_entries_fail_verification(tmp_path):
    output = _artifact(tmp_path)
    receipt = json.loads((output / RECEIPT).read_text())
    (output / RECEIPT).unlink()
    with pytest.raises(VerificationError, match="closure mismatch"):
        verify_path(output)

    (output / RECEIPT).write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n")
    (output / "extra.json").write_text("{}\n")
    with pytest.raises(VerificationError, match="closure mismatch"):
        verify_path(output)


def test_verify_path_refuses_real_mode_for_three_arm_artifacts(tmp_path):
    output = _artifact(tmp_path)
    with pytest.raises(VerificationError):
        verify_path(output, mode="REAL")


def test_verify_synthetic_only_is_wired_and_detects_test_imports(tmp_path):
    verify_synthetic_only(REPO_ROOT)

    fake = tmp_path / "fake-repo"
    shutil.copytree(REPO_ROOT / "src" / "gate1", fake / "src" / "gate1")
    (fake / "src" / "gate1" / "leaky.py").write_text("import tests.gate1\n", encoding="utf-8")
    with pytest.raises(VerificationError, match="test package"):
        verify_synthetic_only(fake)


def test_verify_generated_cli_has_no_verifier_exempt_escape_option():
    from gate1.cli import _parser

    parser = _parser()
    verify_parser = next(
        action for action in parser._actions
        if action.dest == "command" and hasattr(action, "choices")
    ).choices["verify-generated"]
    option_strings = {option for action in verify_parser._actions for option in action.option_strings}
    assert not any("exempt" in option for option in option_strings)
    assert "--artifact-dir" in option_strings


def _forge(output: Path, forge: str) -> None:
    report = json.loads((output / REPORT).read_text())
    if forge == "duplicate_b07_metric":
        report["b07_metric_states"] = [
            report["b07_metric_states"][0], dict(report["b07_metric_states"][0]),
        ]
    elif forge == "synthetic_arm_wrong_source":
        report["arm_derivations"][2]["derived_from_arm_id"] = "arm_a"
    else:  # pragma: no cover - defensive
        raise AssertionError(forge)
    (output / REPORT).write_bytes(_canonical_bytes(report))
    _resync_receipt(output)


@pytest.mark.parametrize("forge", ["duplicate_b07_metric", "synthetic_arm_wrong_source"])
def test_forged_report_is_rejected_even_after_receipt_digest_resync(tmp_path, forge):
    """C-1: verifier must reject reports the schemas reject, even if digests are resynced."""
    output = _artifact(tmp_path)
    _forge(output, forge)
    with pytest.raises(VerificationError):
        verify_path(output)
    result = _run_cli("verify-generated", "--artifact-dir", str(output))
    assert result.returncode != 0
    assert "error:" in result.stderr


@pytest.mark.parametrize("forge", ["duplicate_b07_metric", "synthetic_arm_wrong_source"])
def test_forged_report_is_also_schema_invalid(tmp_path, forge):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((REPO_ROOT / "schemas" / "gate1_compat_v2" /
                         "three_arm_compat_report.json").read_text(encoding="utf-8"))
    output = _artifact(tmp_path)
    _forge(output, forge)
    report = json.loads((output / REPORT).read_text())
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(report, schema)
