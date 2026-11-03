"""V4 RED contracts for authoritative refinement/probe cross-binding.

These tests deliberately mutate the byte-addressed refinement artifact after a
sealed review bundle has been created.  ``build_real_edit_plan`` must re-derive
the evidence projection and bind the source-probe declaration to the reviewed
probe; accepting either mutation would let a caller substitute evidence after
editorial review.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.vip_fvs.unit.test_real_plan import _accept, _bundle


def _rewrite_refinement_artifact(bundle, mutate) -> Path:
    artifact = Path(bundle.payload["refinement"]["evidence_artifact_ref"])
    record = json.loads(artifact.read_text(encoding="utf-8"))
    mutate(record)
    artifact.write_text(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return artifact


def test_build_rejects_forged_refinement_evidence_projection(monkeypatch):
    """A changed evidence-bearing field cannot retain the old evidence digest."""
    from vip_fvs.real_plan import build_real_edit_plan

    bundle = _bundle()
    _rewrite_refinement_artifact(bundle, lambda record: record["method"].update(
        {"derivation": "forged-post-review-derivation"}
    ))

    with pytest.raises(ValueError, match="evidence"):
        build_real_edit_plan(bundle, _accept(bundle), plan_id="v4-forged-evidence", plan_revision=1)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_probe_digest", "f" * 64),
        ("source_probe_artifact_ref", "/tmp/forged-source-probe.json"),
    ],
)
def test_build_rejects_mutated_source_probe_binding_fields(monkeypatch, field, value):
    """Probe identity must remain bound to the probe reviewed by the bundle."""
    from vip_fvs.real_plan import build_real_edit_plan

    bundle = _bundle()
    _rewrite_refinement_artifact(bundle, lambda record: record.__setitem__(field, value))

    with pytest.raises(ValueError, match="probe|evidence"):
        build_real_edit_plan(bundle, _accept(bundle), plan_id="v4-mutated-probe", plan_revision=1)
