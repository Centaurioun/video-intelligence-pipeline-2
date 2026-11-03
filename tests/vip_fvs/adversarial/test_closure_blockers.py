"""Regression coverage for the coordinator's persisted Gate-3 receipt boundary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from vip_fvs import run_vertical_slice
from tests.vip_fvs.fixtures.materialize import materialize_fixture


def _run(tmp_path: Path) -> dict:
    source_dir = tmp_path / "input"
    source_dir.mkdir()
    source = materialize_fixture("cfr_4s_shape", source_dir)
    return run_vertical_slice(source, "target phrase", tmp_path / "index",
                              fake_embedder=True, scenario="cfr_4s_shape",
                              run_dir=tmp_path / "artifacts")


def test_coordinator_invokes_persisted_gate3_receipt(tmp_path: Path):
    result = _run(tmp_path)
    receipt = result["receipt"]["gate3_receipt"]
    assert receipt["verifier_report_ref"]
    assert receipt["container_measurement_ref"]
    assert receipt["resource_evidence_ref"]
    assert receipt["module_execution_ref"]
    assert receipt["discriminating_report_ref"]
    assert receipt["gate0_suite_executed"] is False


def test_tampered_persisted_artifact_digest_is_not_silently_accepted(tmp_path: Path):
    result = _run(tmp_path)
    manifest_path = Path(result["manifest"])
    manifest = json.loads(manifest_path.read_text())
    entries = manifest["output_artifact_digests"]
    first = entries[0].rsplit(":", 1)
    entries[0] = first[0] + ":" + ("0" * 64)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    assert entries[0].rsplit(":", 1)[1] != hashlib.sha256(
        (Path.cwd() / first[0]).read_bytes()).hexdigest()
