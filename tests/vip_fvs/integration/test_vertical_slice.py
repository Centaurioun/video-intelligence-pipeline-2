"""Contract-level acceptance tests for the local/synthetic FVS.

These tests deliberately call the public coordinator boundary.  The concrete
service is installed by the coordinator integration lane; this file owns the
observable chain and does not reach into implementation internals.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from vip_fvs import run_vertical_slice
from tests.vip_fvs.fixtures.materialize import materialize_fixture


def _stage(result: dict, name: str) -> dict:
    value = result.get(name)
    assert isinstance(value, dict), f"missing {name} stage record"
    return value


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def run_root(tmp_path: Path) -> Path:
    path = tmp_path / "run"
    path.mkdir()
    return path


def _run(recipe: str, run_root: Path) -> tuple[dict, Path, str]:
    input_root = run_root / "input"
    input_root.mkdir(parents=True, exist_ok=True)
    source = materialize_fixture(recipe, input_root)
    before = _digest(source)
    result = run_vertical_slice(
        source,
        "target phrase",
        run_root / "index",
        fake_embedder=True,
        scenario=recipe,
        run_dir=run_root / "artifacts",
    )
    assert _digest(source) == before, "the source descriptor must remain immutable"
    assert result.get("all_checks_passed") is True
    return result, source, before


def test_cfr_vertical_slice_preserves_provenance_and_digest_stability(run_root: Path):
    first, source, source_digest = _run("cfr_4s_shape", run_root)

    source_stage = _stage(first, "source")
    assert source_stage["source_sha256"] == source_digest
    assert source_stage["source_sha256_before"] == source_digest
    assert source_stage["source_sha256_after"] == source_digest
    assert source_stage["custody_state"] == "PRESERVED"

    retrieval = _stage(first, "retrieval")
    candidate = _stage(first, "candidate")
    assert retrieval["fake_embedder_used"] is True
    assert candidate["evidence_class"] == "MATCHED"
    assert candidate["time_domain"] == "semantic_seconds"
    assert candidate["binding_eligible"] is False
    assert candidate["refinement_eligibility"] == "NOT_ELIGIBLE"

    refinement = _stage(first, "refinement")
    assert refinement["time_domain"] == "source_pts"
    assert refinement["precision"] == "source-pts"
    assert isinstance(refinement["pts_ticks"], list)
    assert all(isinstance(tick, int) for tick in refinement["pts_ticks"])
    assert refinement["time_base"] == {"num": 1, "den": 25}
    assert refinement["source_content_digest"] == source_digest
    assert refinement["binding_eligible"] is True

    decision = _stage(first, "editorial_decision")
    assert decision["principal_kind"] == "SYNTHETIC_HUMAN"
    assert decision["fixture_scope"] == "SYNTHETIC_FIXTURE"
    assert decision["rationale"]

    plan = _stage(first, "edit_plan")
    assert plan["plan_scope"] == "SYNTHETIC_FIXTURE"
    assert plan["export_eligible"] is False
    assert plan["source_revision_ids"]

    render = _stage(first, "render")
    assert render["production_eligible"] is False
    assert render["production_renderer_selected"] is False
    assert render["attribution_verified"] is True
    render_path = Path(render["path"])
    assert render_path.is_file()
    assert render["digest"] == _digest(render_path)

    verifier = _stage(first, "verifier")
    assert verifier["agreement"] == "AGREE"
    assert verifier["source_content_digest"] == source_digest
    qc = _stage(first, "technical_qc")
    assert qc["status"] == "PASS"

    receipt = _stage(first, "receipt")
    assert receipt["receipt_status"] == "PASS"
    assert receipt["source_content_digest"] == source_digest
    assert receipt["render_digest"] == render["digest"]
    assert first["fresh_process_readback_ok"] is True
    assert not (run_root / "artifacts" / "measured.synthetic.mp4").exists()
    assert _stage(first, "refinement")["source_native_path"]
    assert receipt["authoritative_rederivation"]["verifier_report_status"] == "PASS"
    assert receipt["authoritative_rederivation"]["qc_status"] == "PASS"
    assert receipt["authoritative_rederivation"]["manifest_status"] == "PASS"

    # A second invocation in a fresh artifact root must preserve content-bound
    # identities even though run-local paths and attempt ids may differ.
    second_root = run_root / "second"
    second_root.mkdir()
    second, _, second_source_digest = _run("cfr_4s_shape", second_root)
    assert second_source_digest == source_digest
    assert _stage(second, "source")["source_sha256"] == source_digest
    assert _stage(second, "render")["digest"] == render["digest"]
    assert _stage(second, "receipt")["render_digest"] == receipt["render_digest"]


def test_vfr_vertical_slice_uses_measured_nonuniform_pts_and_never_nominal_fps(run_root: Path):
    result, _, source_digest = _run("vfr_nonuniform", run_root)

    candidate = _stage(result, "candidate")
    assert candidate["time_domain"] == "semantic_seconds"
    assert candidate["binding_eligible"] is False

    refinement = _stage(result, "refinement")
    assert refinement["time_domain"] == "source_pts"
    assert refinement["time_base"] == {"num": 1, "den": 1000}
    assert refinement["pts_ticks"] == [0, 40, 80, 160, 280]
    assert refinement["pts_deltas_ticks"] == [40, 40, 80, 120]
    assert refinement["nonuniform"] is True
    assert refinement["nominal_fps_shortcut_used"] is False
    assert refinement["source_content_digest"] == source_digest

    plan = _stage(result, "edit_plan")
    assert plan["export_eligible"] is False
    assert _stage(result, "render")["attribution_verified"] is True
    assert _stage(result, "technical_qc")["status"] == "PASS"
    assert result["fresh_process_readback_ok"] is True


def test_receipt_readback_is_independent_of_in_process_coordinator(run_root: Path):
    result, source, source_digest = _run("cfr_4s_shape", run_root)
    receipt = _stage(result, "receipt")
    receipt_path = Path(receipt["path"])
    assert receipt_path.is_file()

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, ["src", ".", env.get("PYTHONPATH", "")]))
    code = (
        "import json,sys; "
        "r=json.load(open(sys.argv[1])); "
        "assert r['receipt_status']=='PASS'; "
        "assert r['source_content_digest']==sys.argv[2]; "
        "print('READBACK_PASS')"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code, str(receipt_path), source_digest],
        cwd=Path(__file__).parents[3],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == "READBACK_PASS"
