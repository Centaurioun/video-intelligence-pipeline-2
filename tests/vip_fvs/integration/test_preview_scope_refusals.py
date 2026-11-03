"""Scope-boundary refusals across the REAL and fixture preview entrypoints.

A sealed SYNTHETIC_FIXTURE plan must never be accepted by the REAL preview
entrypoint: doing so would run the real renderer, verifier and technical QC and
write MEASURED-looking REAL evidence for fixture-scoped editorial authority
before failing late on provenance. The refusal must happen before any render,
verifier, QC or authorization side effect.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import gate3.plan
import vip_fvs.cli as cli
import vip_fvs.real_plan as real_plan
from gate3.editorial import EditorialDecision
from vip_fvs.editorial_plan import editorial_decision

from tests.vip_fvs.unit.test_fixture_preview_plan import (  # noqa: F401  (helpers reused deliberately)
    _fixture_decision,
    _refinement,
)


@pytest.fixture
def binding(monkeypatch):
    monkeypatch.setattr(gate3.plan, "is_binding_eligible", lambda record: True)
    monkeypatch.setattr(real_plan._gate3_refinement, "is_binding_eligible", lambda record: True)


def _sealed_fixture_plan(binding, plan_path: Path) -> None:
    decision = _fixture_decision()
    assert isinstance(decision, EditorialDecision)
    artifacts = real_plan.build_fixture_plan_artifacts(
        plan_id="fixture-plan-scope-1", plan_revision=1,
        decision=decision, refinement=_refinement(),
    )
    real_plan.save_real_plan(artifacts, plan_path)


def _preview_real_args(**overrides):
    values = {
        "plan": "plan.json",
        "source": "source.mp4",
        "output_root": "out",
        "authorization": "authorization.json",
        "ffprobe_executable": "/opt/homebrew/bin/ffprobe",
        "ffmpeg_executable": "/opt/homebrew/bin/ffmpeg",
        "attempt_id": "attempt-real-1",
        "run_id": "run-real-1",
        "receipt_path": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_preview_real_refuses_fixture_plan_before_any_render(binding, tmp_path, monkeypatch):
    plan_path = tmp_path / "plan.json"
    _sealed_fixture_plan(binding, plan_path)
    output_root = tmp_path / "out"
    source = tmp_path / "source.mp4"
    source.write_bytes(b"generated-source-placeholder")

    rendered: list[str] = []

    def fail_if_rendered(*_args, **_kwargs):
        rendered.append("render_preview")
        raise AssertionError("REAL preview rendered a SYNTHETIC_FIXTURE plan")

    import vip_fvs.local_preview as local_preview

    monkeypatch.setattr(local_preview.LocalPreviewAdapter, "render_preview", fail_if_rendered)

    args = _preview_real_args(plan=str(plan_path), source=str(source),
                             output_root=str(output_root),
                             authorization=str(tmp_path / "absent-authorization.json"))

    with pytest.raises(ValueError, match="PLAN_SCOPE_MISMATCH"):
        cli._preview_real(args)

    assert rendered == []
    assert not output_root.exists() or not any(output_root.iterdir())
    assert not (output_root / "verifier.json").exists()
    assert not (output_root / "technical-qc.json").exists()
    assert not (output_root / "preview-receipt.json").exists()


def test_fixture_plan_reports_non_real_scope_after_readback(binding, tmp_path):
    plan_path = tmp_path / "plan.json"
    _sealed_fixture_plan(binding, plan_path)

    artifacts = real_plan.load_real_plan(plan_path)

    assert artifacts.plan.plan_scope == "SYNTHETIC_FIXTURE"
    assert artifacts.projected_decision.principal_kind == "SYNTHETIC_HUMAN"
    assert artifacts.projected_decision.fixture_scope == "SYNTHETIC_FIXTURE"
    assert artifacts.plan.real_authority_eligible is False
