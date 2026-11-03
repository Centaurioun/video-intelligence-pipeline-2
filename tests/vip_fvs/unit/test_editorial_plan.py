import sys
import types

import pytest

from vip_fvs.editorial_plan import build_edit_plan, editorial_decision


class FakeDecision:
    def __init__(self, *args, **kwargs):
        self.decision_id, self.principal_kind, self.principal_ref = args[:3]
        self.decided_on_refinement = args[3]
        self.decided_on_revision = args[4]
        self.decision_class = args[5]
        self.rationale = args[6]
        self.fixture_scope = kwargs.get("fixture_scope")


def install_gate3_editorial(monkeypatch):
    pkg = types.ModuleType("gate3")
    mod = types.ModuleType("gate3.editorial")
    mod.EditorialDecision = FakeDecision
    monkeypatch.setitem(sys.modules, "gate3", pkg)
    monkeypatch.setitem(sys.modules, "gate3.editorial", mod)


def test_decision_requires_rationale_and_fixture_scope(monkeypatch):
    install_gate3_editorial(monkeypatch)
    with pytest.raises(ValueError, match="rationale"):
        editorial_decision(
            decision_id="d", principal_kind="SYNTHETIC_HUMAN", principal_ref="fixture:x",
            refinement_id="r", plan_revision=1, rationale="",
            fixture_scope="SYNTHETIC_FIXTURE",
        )
    with pytest.raises(ValueError, match="fixture"):
        editorial_decision(
            decision_id="d", principal_kind="SYNTHETIC_HUMAN", principal_ref="fixture:x",
            refinement_id="r", plan_revision=1, rationale="keep the action",
        )


def test_plan_requires_decision_and_pins_evidence(monkeypatch):
    install_gate3_editorial(monkeypatch)
    decision = editorial_decision(
        decision_id="d", principal_kind="SYNTHETIC_HUMAN", principal_ref="fixture:x",
        refinement_id="r", plan_revision=1, rationale="keep the action",
        fixture_scope="SYNTHETIC_FIXTURE",
    )
    with pytest.raises(ValueError, match="explicit editorial decision"):
        build_edit_plan(
            plan_id="p", plan_revision=1,
            refinement={"refinement_id": "r", "evidence_digest": "e"},
            decision=None, placements=[], source_revision_ids=["src"],
        )

    captured = {}
    plan_mod = types.ModuleType("gate3.plan")

    class FakePlan:
        def __init__(self, *args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs

    plan_mod.EditPlanRevision = FakePlan
    monkeypatch.setitem(sys.modules, "gate3.plan", plan_mod)
    plan = build_edit_plan(
        plan_id="p", plan_revision=1,
        refinement={"refinement_id": "r", "evidence_digest": "e", "source_content_digest": "s"},
        decision=decision, placements=["placement-1"], source_revision_ids=["src"],
        policy_decision_ref="policy", pinned_source_digest="s",
    )
    assert isinstance(plan, FakePlan)
    assert captured["kwargs"]["pinned_evidence_digests"] == {"r": "e"}
    assert captured["kwargs"]["policy_decision_ref"] == "policy"


def test_source_digest_pin_rejects_substitution(monkeypatch):
    install_gate3_editorial(monkeypatch)
    decision = editorial_decision(
        decision_id="d", principal_kind="SYNTHETIC_HUMAN", principal_ref="fixture:x",
        refinement_id="r", plan_revision=1, rationale="keep", fixture_scope="SYNTHETIC_FIXTURE",
    )
    with pytest.raises(ValueError, match="source digest"):
        build_edit_plan(
            plan_id="p", plan_revision=1,
            refinement={"refinement_id": "r", "evidence_digest": "e", "source_content_digest": "actual"},
            decision=decision, placements=[], source_revision_ids=["src"], pinned_source_digest="other",
        )
