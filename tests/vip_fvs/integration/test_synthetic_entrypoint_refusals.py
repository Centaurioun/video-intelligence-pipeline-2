"""Refusal behaviour of the supported synthetic product entrypoint.

The developer CLI must refuse ambiguous or incomplete fixture evidence and
incorrect fixture identity before any synthetic PTS is treated as a measured
source-native interval.  A refusal is a single JSON summary with
``all_checks_passed`` false and a stable reason token, never a PASS built on
defaulted or truncated timestamps.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from tests.vip_fvs.fixtures.materialize import load_recipe

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _run_cli(source: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(["src", "experiments", "."])
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "vip_fvs.cli",
            "run",
            "--source",
            str(source),
            "--query",
            "target phrase",
            "--index-root",
            str(source.parent / "index"),
            "--run-dir",
            str(source.parent / "run"),
            *extra,
        ],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def _summary(completed: subprocess.CompletedProcess[str]) -> dict:
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert len(lines) == 1, completed.stderr or completed.stdout
    return json.loads(lines[0])


def _digest_payload(recipe: dict, *, declared_digest: str | None = None) -> bytes:
    canonical = json.dumps(recipe, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = declared_digest or hashlib.sha256(canonical.encode()).hexdigest()
    return json.dumps({"recipe": recipe, "content_sha256": digest}, sort_keys=True, indent=2).encode()


def test_cli_refuses_descriptor_without_recipe(tmp_path: Path) -> None:
    source = tmp_path / "incomplete.source.json"
    source.write_bytes(b'{"content_sha256":"abc"}')
    completed = _run_cli(source, "--fake-embedder", "--scenario", "cfr_4s_shape")
    assert completed.returncode == 1
    summary = _summary(completed)
    assert summary["all_checks_passed"] is False
    assert "SYNTHETIC_RECIPE_ENVELOPE_INVALID" in summary["error"]
    assert not (tmp_path / "run").exists()


def test_cli_refuses_non_json_descriptor(tmp_path: Path) -> None:
    source = tmp_path / "garbage.source.json"
    source.write_bytes(b"not json")
    completed = _run_cli(source, "--fake-embedder", "--scenario", "cfr_4s_shape")
    assert completed.returncode == 1
    summary = _summary(completed)
    assert "SYNTHETIC_RECIPE_SOURCE_NOT_JSON" in summary["error"]


def test_cli_refuses_non_integer_pts(tmp_path: Path) -> None:
    recipe = load_recipe("cfr_4s_shape")
    recipe["pts_ticks"] = [0, 13.5, 25]
    recipe["frames"] = []
    source = tmp_path / "float-pts.source.json"
    source.write_bytes(_digest_payload(recipe))
    completed = _run_cli(source, "--fake-embedder", "--scenario", "cfr_4s_shape")
    assert completed.returncode == 1
    summary = _summary(completed)
    assert "SYNTHETIC_RECIPE_PTS_INVALID" in summary["error"]


def test_cli_refuses_scenario_identity_mismatch(tmp_path: Path) -> None:
    recipe = load_recipe("cfr_4s_shape")
    source = tmp_path / "cfr.source.json"
    source.write_bytes(_digest_payload(recipe))
    completed = _run_cli(source, "--fake-embedder", "--scenario", "vfr_nonuniform")
    assert completed.returncode == 1
    summary = _summary(completed)
    assert "SYNTHETIC_RECIPE_IDENTITY_MISMATCH" in summary["error"]
    assert not (tmp_path / "run").exists()


def test_cli_refuses_fake_and_real_mode_ambiguity(tmp_path: Path) -> None:
    from tests.vip_fvs.fixtures.materialize import materialize_fixture

    source = materialize_fixture("cfr_4s_shape", tmp_path)
    completed = _run_cli(
        source,
        "--fake-embedder",
        "--scenario",
        "cfr_4s_shape",
        "--pilot-authorization",
        str(tmp_path / "nonexistent-authorization.json"),
    )
    assert completed.returncode == 1
    summary = _summary(completed)
    assert summary["all_checks_passed"] is False
    assert "FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS" in summary["error"]
    assert not (tmp_path / "run").exists()


def test_cli_refuses_real_mode_inputs_without_real_mode(tmp_path: Path) -> None:
    from tests.vip_fvs.fixtures.materialize import materialize_fixture

    source = materialize_fixture("cfr_4s_shape", tmp_path)
    completed = _run_cli(
        source,
        "--fake-embedder",
        "--scenario",
        "cfr_4s_shape",
        "--model-identity",
        "synthetic-model",
    )
    assert completed.returncode == 1
    summary = _summary(completed)
    assert "FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS" in summary["error"]
