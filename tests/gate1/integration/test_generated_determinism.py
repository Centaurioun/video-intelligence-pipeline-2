"""Deterministic protocol readiness and side-effect boundary for D05 runs."""
from __future__ import annotations

import hashlib
import json
import socket
import subprocess
from pathlib import Path

import pytest


def _artifact_identity(root: Path) -> tuple[tuple[str, str], ...]:
    """Hash every emitted file; no volatile-field normalization is permitted."""
    return tuple(
        (path.relative_to(root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    )


def _scientific_outcome(root: Path) -> dict:
    report = json.loads((root / "benchmark_report.json").read_text())
    receipt = json.loads((root / "synthetic_receipt.json").read_text())
    return {
        "benchmark_status": report["benchmark_status"],
        "conclusion": report["conclusion"],
        "real_benchmark_executed": receipt["real_benchmark_executed"],
        "winner_observed": receipt["winner_observed"],
        "gate_promotion": receipt["gate_promotion"],
    }


def test_repeated_generated_positive_case_has_identical_identity_and_outcome(tmp_path):
    from gate1.harness import run_generated_case

    first = run_generated_case("positive_one_axis", tmp_path / "run-a")
    second = run_generated_case("positive_one_axis", tmp_path / "run-b")
    first, second = Path(first), Path(second)

    assert first.is_dir() and second.is_dir()
    assert _artifact_identity(first) == _artifact_identity(second)
    assert _scientific_outcome(first) == _scientific_outcome(second)
    outcome = _scientific_outcome(first)
    assert outcome["benchmark_status"] == "PASS"
    assert outcome["conclusion"] == "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"
    assert outcome["real_benchmark_executed"] is False
    assert outcome["winner_observed"] is False
    assert outcome["gate_promotion"] is False


def test_generated_run_fails_if_network_or_process_execution_is_attempted(tmp_path, monkeypatch):
    from gate1.harness import run_generated_case

    def forbidden(*args, **kwargs):
        pytest.fail(f"generated harness attempted external side effect: {args!r}")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "check_call", forbidden)
    monkeypatch.setattr(subprocess, "check_output", forbidden)

    result = Path(run_generated_case("positive_one_axis", tmp_path / "generated"))
    assert result.is_dir()
