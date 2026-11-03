"""Adversarial checks for the FVS editorial/export authority boundary.

These tests intentionally exercise the narrow synthetic plan seam.  A fixture decision can
make a plan structurally useful for the vertical slice, but it must never become production
export authority merely because fields look complete.
"""

import pytest

from gate3.editorial import EditorialDecision
from gate3.plan import EditPlanRevision
from gate3.placement import TimelinePlacement
from gate3.rational import TimeBase
from gate3.timeline import TimelineDomain
from vip_fvs.editorial_plan import build_edit_plan, editorial_decision


def _refinement():
    return {
        "refinement_id": "ref-1",
        "evidence_digest": "evidence-1",
        "source_revision_id": "source-rev-1",
        "source_content_digest": "source-bytes-1",
    }


def _fixture_decision():
    return editorial_decision(
        decision_id="decision-1",
        principal_kind="SYNTHETIC_HUMAN",
        principal_ref="fixture:editor",
        refinement_id="ref-1",
        plan_revision=1,
        rationale="retain the synthetic fixture interval",
        fixture_scope="SYNTHETIC_FIXTURE",
    )


def _placement(*, start=0, end=10, placement_id="placement-1"):
    domain = TimelineDomain("timeline-1", TimeBase(1, 1000))
    return TimelinePlacement(
        placement_id,
        "plan-1",
        1,
        "ref-1",
        "decision-1",
        "V1",
        0,
        start,
        end,
        "mapping-1",
        domain,
    )


def test_missing_decision_cannot_create_an_editorial_plan():
    with pytest.raises(ValueError, match="explicit editorial decision"):
        build_edit_plan(
            plan_id="plan-1",
            plan_revision=1,
            refinement=_refinement(),
            decision=None,
            placements=[],
            source_revision_ids=["source-rev-1"],
        )


def test_synthetic_human_decision_cannot_leak_into_real_plan(monkeypatch):
    # Isolate this authority test from the byte-measurement fixture: the question here is
    # whether principal/scope checks remain fail-closed after a candidate is otherwise valid.
    monkeypatch.setattr("gate3.plan.is_binding_eligible", lambda record: True)
    with pytest.raises(ValueError, match="real human"):
        build_edit_plan(
            plan_id="plan-1",
            plan_revision=1,
            refinement=_refinement(),
            decision=_fixture_decision(),
            placements=[],
            source_revision_ids=["source-rev-1"],
            plan_scope="REAL",
        )


def test_same_track_overlapping_placements_are_rejected_before_export_projection(monkeypatch):
    monkeypatch.setattr("gate3.plan.is_binding_eligible", lambda record: True)
    first = _placement()
    second = _placement(start=9, end=20, placement_id="placement-2")
    with pytest.raises(ValueError, match="overlap"):
        EditPlanRevision(
            "plan-1",
            1,
            [first, second],
            {"ref-1": _refinement()},
            {"ref-1": _fixture_decision()},
            ["source-rev-1"],
            plan_scope="SYNTHETIC_FIXTURE",
            policy_decision_ref="ref-1",
            pinned_evidence_digests={"ref-1": "evidence-1"},
        )


def test_synthetic_plan_may_be_structural_but_never_export_eligible(monkeypatch):
    monkeypatch.setattr("gate3.plan.is_binding_eligible", lambda record: True)
    plan = build_edit_plan(
        plan_id="plan-1",
        plan_revision=1,
        refinement=_refinement(),
        decision=_fixture_decision(),
        placements=[_placement()],
        source_revision_ids=["source-rev-1"],
        policy_decision_ref="ref-1",
    )

    assert plan.plan_scope == "SYNTHETIC_FIXTURE"
    assert plan.export_plan_structurally_valid is True
    assert plan.real_authority_eligible is False
    assert plan.export_eligible is False
    assert plan.to_record()["export_eligible"] is False


def test_fixture_addressed_human_is_not_evidence_backed_export_authority(monkeypatch):
    monkeypatch.setattr("gate3.plan.is_binding_eligible", lambda record: True)
    decision = EditorialDecision(
        "decision-1",
        "human",
        "fixture:human-shaped",
        "ref-1",
        1,
        "ACCEPT",
        "looks like a human decision but is fixture-addressed",
    )
    plan = build_edit_plan(
        plan_id="plan-1",
        plan_revision=1,
        refinement=_refinement(),
        decision=decision,
        placements=[_placement()],
        source_revision_ids=["source-rev-1"],
        policy_decision_ref="ref-1",
        plan_scope="REAL",
    )
    assert decision.real_authority_eligible is False
    assert decision.principal_authority_evidence is None
    assert plan.export_eligible is False
