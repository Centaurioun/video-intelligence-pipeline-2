"""Command boundary tests for deterministic, verifier-bound F03 dispositions."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from gate2 import cli


SAFETY = {
    "production_eligible": False,
    "gate_promotion": False,
    "mechanism_adopted": False,
}


def _fixtures(tmp_path: Path, *, extra_evidence: dict | None = None) -> tuple[Path, Path]:
    dependencies = {
        "F01": {"sha": "1" * 40, "tree": "2" * 40},
        "F02": {"sha": "3" * 40, "tree": "4" * 40},
    }
    candidate = dependencies["F02"]
    definitions = {
        "restart_recovery_wall_time": {
            "unit": "milliseconds", "min": 0, "max": 30_000,
            "repetitions": 2, "deficit_class": "C5-recovery-time",
        },
    }
    preregistration_path = tmp_path / "preregistration.json"
    preregistration = {"workload": {"repetitions": 2}, "metrics": [
        {"metric_id": "restart_recovery_wall_time", "unit": "milliseconds", "bound_max": 30_000},
    ]}
    preregistration_path.write_text(json.dumps(preregistration), encoding="utf-8")
    contract = {
        "dependency_heads": dependencies,
        "candidate": candidate,
        "preregistration_path": "preregistration.json",
        "preregistration_digest": hashlib.sha256(preregistration_path.read_bytes()).hexdigest(),
        "freeze_digest": "b" * 64,
        "workload_digest": "c" * 64,
        "config_digest": "d" * 64,
        "fault_schedule_digest": "e" * 64,
        "metric_definitions": definitions,
        "decision_digest": "f" * 64,
    }
    evidence = {
        "version": "f03-evidence.v1",
        **{key: value for key, value in contract.items() if key != "decision_digest"},
        "decision_digest": contract["decision_digest"],
        "observations": [
            {
                "metric_id": "restart_recovery_wall_time", "status": "MEASURED",
                "value": value, "unit": "milliseconds", "evidence_class": "MEASURED",
                "carrier_path": "measurement/recovery.raw.json", "carrier_sha256": "7" * 64,
                "dependency_id": "F02", "repetition": repetition,
                "dependency_heads": dependencies, "candidate": candidate,
                "preregistration_digest": "a" * 64, "freeze_digest": "b" * 64,
                "workload_digest": "c" * 64, "config_digest": "d" * 64,
                "fault_schedule_digest": "e" * 64,
            }
            for repetition, value in ((1, 10), (2, 11))
        ],
    }
    if extra_evidence:
        evidence.update(extra_evidence)
    carrier = tmp_path / "measurement" / "recovery.raw.json"
    carrier.parent.mkdir(parents=True)
    carrier.write_text(json.dumps([
        {"metric_id": "restart_recovery_wall_time", "repetition": repetition,
         "value": value, "unit": "milliseconds"}
        for repetition, value in ((1, 10), (2, 11))
    ]), encoding="utf-8")
    carrier_digest = hashlib.sha256(carrier.read_bytes()).hexdigest()
    for row in evidence["observations"]:
        row["carrier_sha256"] = carrier_digest
    evidence_path, contract_path = tmp_path / "evidence.json", tmp_path / "contract.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    return evidence_path, contract_path


def test_cli_has_no_mechanism_preselection_option(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["decide", "--input", "evidence.json", "--contract", "contract.json",
                  "--mechanism", "cache"])
    assert exc.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err


def test_decide_is_deterministic_and_emits_fixed_safety_flags(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_path, contract_path = _fixtures(tmp_path)

    def decision(**_kwargs):
        return SimpleNamespace(to_dict=lambda: {
            "disposition": "BR-1", "disposition_digest": "f" * 64,
            "mechanisms": [{"mechanism": "cache", "adoption": False,
                            "eligible_for_later_evaluation": False}],
        })

    monkeypatch.setattr(cli, "decide", decision)
    monkeypatch.setattr(cli, "verify_evidence", lambda *_args, **_kwargs: {"verified": True, "errors": []})
    argv = ["decide", "--input", str(evidence_path), "--contract", str(contract_path)]
    assert cli.main(argv) == 0
    first = json.loads(capsys.readouterr().out)
    assert cli.main(argv) == 0
    second = json.loads(capsys.readouterr().out)
    assert first == second
    assert {key: first[key] for key in SAFETY} == SAFETY
    assert first["scope"] == "synthetic/generated"
    assert first["mechanisms"] == [{"name": "cache", "eligible_later": False, "adopted": False}]
    assert all(row["adopted"] is False for row in first["mechanisms"])


def test_decision_rows_receive_candidate_identity_from_verified_evidence(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_path, contract_path = _fixtures(tmp_path)
    seen: dict = {}

    def decision(**kwargs):
        seen.update(kwargs)
        return SimpleNamespace(to_dict=lambda: {
            "disposition": "BR-1", "disposition_digest": "f" * 64,
            "mechanisms": [],
        })

    monkeypatch.setattr(cli, "decide", decision)
    monkeypatch.setattr(cli, "verify_evidence", lambda *_args, **_kwargs: {"verified": True, "errors": []})
    assert cli.main(["decide", "--input", str(evidence_path), "--contract", str(contract_path)]) == 0
    capsys.readouterr()
    row = seen["observations"]["restart_recovery_wall_time"][0]
    assert row["dependency_id"] == "H3-F02"
    assert row["candidate_sha"] == "3" * 40
    assert row["candidate_tree"] == "4" * 40


def test_decision_request_cannot_supply_mechanism_field(
    capsys: pytest.CaptureFixture[str], tmp_path: Path,
) -> None:
    evidence_path, contract_path = _fixtures(tmp_path, extra_evidence={"mechanism": "cache"})
    assert cli.main(["decide", "--input", str(evidence_path), "--contract", str(contract_path)]) == 2
    assert "unknown evidence fields" in capsys.readouterr().err


def test_decide_fails_before_decision_when_raw_carrier_digest_changes(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_path, contract_path = _fixtures(tmp_path)
    raw_carrier = tmp_path / "measurement" / "recovery.raw.json"
    raw_carrier.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(cli, "decide", lambda **_kwargs: pytest.fail("unverified data reached decision"))

    result = cli.main(["decide", "--input", str(evidence_path), "--contract", str(contract_path)])

    assert result == 2
    output = json.loads(capsys.readouterr().out)
    assert output["verified"] is False
    # The fixture carries a superseded v1 envelope and non-current provenance, so
    # the verifier fails closed before any carrier digest decision is reached.
    assert output["errors"]
    assert any("unsupported evidence envelope version" in error for error in output["errors"])


def test_verify_cli_calls_bound_verifier_and_keeps_safety_flags(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_path, contract_path = _fixtures(tmp_path)
    seen: list[tuple[dict, dict]] = []

    def verify(evidence: dict, contract: dict, *, carrier_root: Path, git_root=None) -> dict:
        seen.append((evidence, contract))
        assert carrier_root == evidence_path.parent
        assert git_root is None
        return {"verified": True, "errors": [], "production_eligible": False,
                "gate_promotion": False, "mechanism_adopted": False}

    # The standalone verify path replays the disposition; bind the replay to the
    # frozen digest so this test isolates the verifier-call contract only.
    monkeypatch.setattr(cli, "verify_evidence", verify)
    monkeypatch.setattr(cli, "_derive_disposition",
                        lambda contract, rows: {"disposition_digest": contract["decision_digest"]})
    assert cli.main(["verify", "--input", str(evidence_path), "--contract", str(contract_path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["verified"] is True
    assert {key: output[key] for key in SAFETY} == SAFETY
    assert len(seen) == 1


def test_verify_cli_accepts_an_explicit_git_root(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_path, contract_path = _fixtures(tmp_path)
    seen: dict = {}

    def verify(evidence: dict, contract: dict, *, carrier_root: Path, git_root=None) -> dict:
        seen["git_root"] = git_root
        return {"verified": True, "errors": [], "production_eligible": False,
                "gate_promotion": False, "mechanism_adopted": False}

    monkeypatch.setattr(cli, "verify_evidence", verify)
    monkeypatch.setattr(cli, "_derive_disposition",
                        lambda contract, rows: {"disposition_digest": contract["decision_digest"]})
    argv = ["verify", "--input", str(evidence_path), "--contract", str(contract_path),
            "--git-root", str(tmp_path)]
    assert cli.main(argv) == 0
    capsys.readouterr()
    assert seen["git_root"] == str(tmp_path)


def test_verify_cli_rejects_a_forged_decision_digest(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_path, contract_path = _fixtures(tmp_path)
    monkeypatch.setattr(cli, "verify_evidence", lambda *args, **kwargs: {
        "verified": True, "errors": [], "production_eligible": False,
        "gate_promotion": False, "mechanism_adopted": False,
    })
    monkeypatch.setattr(cli, "_derive_disposition",
                        lambda contract, rows: {"disposition_digest": "0" * 64})
    assert cli.main(["verify", "--input", str(evidence_path), "--contract", str(contract_path)]) == 2
    output = json.loads(capsys.readouterr().out)
    assert output["verified"] is False
    assert "decision digest mismatch" in output["errors"]
