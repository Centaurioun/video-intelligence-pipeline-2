"""Unit tests for the fixture-scoped Gate-3 plan bridge.

The byte-bound refinement predicate is stubbed in these tests because the
authoritative byte re-measurement is covered by the real-FFmpeg integration
test; here we isolate the fixture authority/scope rules and the sealed
save/load round-trip.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import gate3.plan
import vip_fvs.real_plan as real_plan
from gate3.editorial import EditorialDecision
from vip_fvs.editorial_plan import editorial_decision


def _refinement(**overrides):
    record = {
        "refinement_id": "ref_fixture00000001",
        "attempt_id": "attempt-fixture-1:refinement",
        "source_revision_id": "fixture-source-1",
        "source_content_digest": "a" * 64,
        "stream_index": 0,
        "selected_stream_index": 0,
        "evidence_class": "MEASURED",
        "time_domain": "source_pts",
        "precision": "source-pts",
        "start_ticks": 0,
        "end_ticks": 40,
        "endpoint_semantics": "half_open",
        "time_base": {"num": 1, "den": 1000},
        "timebase": {"num": 1, "den": 1000},
        "source_pts_interval": {
            "start": 0,
            "end": 40,
            "time_domain": "source_pts",
            "endpoint_semantics": "half_open",
        },
        "evidence_digest": "b" * 64,
    }
    record.update(overrides)
    return record


def _fixture_decision(**overrides):
    kwargs = {
        "decision_id": "fixture-decision-1",
        "principal_kind": "SYNTHETIC_HUMAN",
        "principal_ref": "fixture:synthetic-human:attempt-fixture-1",
        "refinement_id": "ref_fixture00000001",
        "plan_revision": 1,
        "decision_class": "ACCEPT",
        "rationale": "Generated synthetic fixture preview acceptance; no human editorial authority is claimed.",
        "fixture_scope": "SYNTHETIC_FIXTURE",
    }
    kwargs.update(overrides)
    return editorial_decision(**kwargs)


@pytest.fixture
def binding(monkeypatch):
    monkeypatch.setattr(gate3.plan, "is_binding_eligible", lambda record: True)
    monkeypatch.setattr(real_plan._gate3_refinement, "is_binding_eligible", lambda record: True)


def test_fixture_plan_builds_nonproduction_synthetic_scope(binding):
    artifacts = real_plan.build_fixture_plan_artifacts(
        plan_id="fixture-plan-1", plan_revision=1,
        decision=_fixture_decision(), refinement=_refinement(),
    )

    assert artifacts.plan.plan_scope == "SYNTHETIC_FIXTURE"
    assert artifacts.plan.real_authority_eligible is False
    assert artifacts.plan.export_eligible is False
    assert artifacts.plan_digest == artifacts.plan.digest
    assert artifacts.projected_decision.principal_kind == "SYNTHETIC_HUMAN"
    assert artifacts.projected_decision.fixture_scope == "SYNTHETIC_FIXTURE"
    assert artifacts.projected_decision.decided_on_revision == 1
    assert artifacts.mapping.source_refinement_id == "ref_fixture00000001"
    assert (artifacts.mapping.source_timebase_num, artifacts.mapping.source_timebase_den) == (1, 1000)
    assert artifacts.mapping.source_start_pts == 0
    assert artifacts.mapping.source_end_pts == 40
    assert artifacts.mapping.offset_ticks == 0
    assert artifacts.placement.timeline_start_ticks == 0
    assert artifacts.placement.timeline_end_ticks == 40
    assert artifacts.placement.plan_id == "fixture-plan-1"
    assert artifacts.placement_digest == real_plan._digest(artifacts.placement.to_record())


def test_fixture_plan_rejects_human_shaped_principal(binding):
    human = EditorialDecision(
        decision_id="human-decision-1",
        principal_kind="human",
        principal_ref="human:editor-1",
        decided_on_refinement="ref_fixture00000001",
        decided_on_revision=1,
        decision_class="ACCEPT",
        rationale="A real human decision must never authorize a fixture plan.",
    )
    with pytest.raises(ValueError, match="FIXTURE_DECISION_REQUIRED"):
        real_plan.build_fixture_plan_artifacts(
            plan_id="fixture-plan-1", plan_revision=1,
            decision=human, refinement=_refinement(),
        )


def test_fixture_plan_rejects_human_labeled_as_fixture(binding):
    mislabeled = EditorialDecision(
        decision_id="human-labeled-fixture",
        principal_kind="human",
        principal_ref="fixture:synthetic-human:forged",
        decided_on_refinement="ref_fixture00000001",
        decided_on_revision=1,
        decision_class="ACCEPT",
        rationale="Forged fixture labeling must not be accepted.",
        fixture_scope="SYNTHETIC_FIXTURE",
    )
    with pytest.raises(ValueError, match="FIXTURE_DECISION_REQUIRED"):
        real_plan.build_fixture_plan_artifacts(
            plan_id="fixture-plan-1", plan_revision=1,
            decision=mislabeled, refinement=_refinement(),
        )


def test_fixture_plan_refuses_decision_on_another_refinement(binding):
    with pytest.raises(ValueError, match="FIXTURE_DECISION_REFINEMENT_MISMATCH"):
        real_plan.build_fixture_plan_artifacts(
            plan_id="fixture-plan-1", plan_revision=1,
            decision=_fixture_decision(refinement_id="ref_other000000000"),
            refinement=_refinement(),
        )


def test_fixture_plan_refuses_decision_on_another_revision(binding):
    with pytest.raises(ValueError, match="FIXTURE_DECISION_REVISION_MISMATCH"):
        real_plan.build_fixture_plan_artifacts(
            plan_id="fixture-plan-1", plan_revision=1,
            decision=_fixture_decision(plan_revision=2),
            refinement=_refinement(),
        )


def test_fixture_plan_refuses_non_measured_refinement(binding):
    with pytest.raises(ValueError, match="FIXTURE_REFINEMENT_NOT_MEASURED"):
        real_plan.build_fixture_plan_artifacts(
            plan_id="fixture-plan-1", plan_revision=1,
            decision=_fixture_decision(),
            refinement=_refinement(evidence_class="MATCHED"),
        )


def test_fixture_plan_refuses_non_binding_refinement(monkeypatch):
    monkeypatch.setattr(gate3.plan, "is_binding_eligible", lambda record: False)
    monkeypatch.setattr(real_plan._gate3_refinement, "is_binding_eligible", lambda record: False)
    with pytest.raises(ValueError, match="FIXTURE_REFINEMENT_NOT_BINDING"):
        real_plan.build_fixture_plan_artifacts(
            plan_id="fixture-plan-1", plan_revision=1,
            decision=_fixture_decision(), refinement=_refinement(),
        )


def test_fixture_plan_refuses_non_integer_interval(binding):
    with pytest.raises(ValueError, match="FIXTURE_REFINEMENT_INTERVAL_INVALID"):
        real_plan.build_fixture_plan_artifacts(
            plan_id="fixture-plan-1", plan_revision=1,
            decision=_fixture_decision(),
            refinement=_refinement(source_pts_interval={
                "start": 0, "end": 40.0, "time_domain": "source_pts", "endpoint_semantics": "half_open"}),
        )


def test_fixture_plan_round_trips_through_sealed_record(binding, tmp_path):
    artifacts = real_plan.build_fixture_plan_artifacts(
        plan_id="fixture-plan-roundtrip", plan_revision=1,
        decision=_fixture_decision(), refinement=_refinement(),
    )
    target = real_plan.save_real_plan(artifacts, tmp_path / "plan.json")
    loaded = real_plan.load_real_plan(target)

    assert loaded.plan.plan_scope == "SYNTHETIC_FIXTURE"
    assert loaded.plan_digest == artifacts.plan_digest
    assert loaded.placement_digest == artifacts.placement_digest
    assert loaded.mapping_digest == artifacts.mapping_digest
    assert loaded.projected_decision is not None
    assert loaded.projected_decision.principal_kind == "SYNTHETIC_HUMAN"
    assert loaded.projected_decision.fixture_scope == "SYNTHETIC_FIXTURE"
    assert loaded.projected_decision.decision_id == "fixture-decision-1"
    assert loaded.plan.pinned_evidence_digests == {"ref_fixture00000001": "b" * 64}
    assert loaded.plan.real_authority_eligible is False
    assert loaded.plan.export_eligible is False


def test_fixture_plan_is_never_readable_as_real(binding, tmp_path):
    artifacts = real_plan.build_fixture_plan_artifacts(
        plan_id="fixture-plan-scope", plan_revision=1,
        decision=_fixture_decision(), refinement=_refinement(),
    )
    target = real_plan.save_real_plan(artifacts, tmp_path / "plan.json")
    loaded = real_plan.load_real_plan(target)

    assert loaded.plan.plan_scope != "REAL"
    assert loaded.projected_decision.real_authority_eligible is False
    payload = json.loads(Path(target).read_text(encoding="utf-8"))
    assert payload["plan"]["plan_scope"] == "SYNTHETIC_FIXTURE"
    assert payload["plan"]["real_authority_eligible"] is False
    assert payload["plan"]["export_eligible"] is False
    assert payload["projected_decision"]["principal_kind"] == "SYNTHETIC_HUMAN"
    assert payload["projected_decision"]["fixture_scope"] == "SYNTHETIC_FIXTURE"


def test_fixture_plan_revision_continuity_keeps_fixture_scope(binding):
    first = real_plan.build_fixture_plan_artifacts(
        plan_id="fixture-plan-revisions", plan_revision=1,
        decision=_fixture_decision(), refinement=_refinement(),
    )
    second = real_plan.build_fixture_plan_artifacts(
        plan_id="fixture-plan-revisions", plan_revision=2,
        decision=_fixture_decision(decision_id="fixture-decision-2", plan_revision=2),
        refinement=_refinement(), prior_revision=first.plan,
    )
    assert second.plan.plan_revision == 2
    assert second.plan.plan_scope == "SYNTHETIC_FIXTURE"
    assert second.plan.supersedes == first.plan.digest
