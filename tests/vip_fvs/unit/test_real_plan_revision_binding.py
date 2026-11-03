"""D-REALPLAN-1 revision-binding closure tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from vip_fvs.human_decision import create_human_decision
from vip_fvs.real_plan import (
    build_real_edit_plan,
    load_real_plan,
    save_real_plan,
)
from tests.vip_fvs.unit.test_real_plan import _bundle, _binding_fixture   # existing fixture builders


def _accept(bundle, revision: int):
    return create_human_decision(
        bundle=bundle, decision_id=f"decision-{revision}", principal_kind="human",
        principal_ref="human:editor-1", decision_class="ACCEPT",
        rationale="Reviewed measured source interval.", target_plan_revision=revision,
    )


def test_revision_1_with_no_prior_succeeds(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    artifacts = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    assert artifacts.plan.supersedes is None
    assert list(artifacts.plan.derived_from_refs) == []
    assert artifacts.plan.prior_revision is None


def test_revision_1_with_prior_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    with pytest.raises(ValueError, match="PLAN_REVISION_1_CANNOT_HAVE_PRIOR_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1,
                             prior_revision=first.plan)


def test_mismatched_decision_revision_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    with pytest.raises(ValueError, match="PLAN_REVISION_MUST_MATCH_DECISION_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 3), plan_id="plan-1", plan_revision=1)


def test_revision_2_without_prior_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    with pytest.raises(ValueError, match="PLAN_REVISION_AFTER_1_REQUIRES_IMMEDIATE_PRIOR_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2)


def test_revision_2_with_immediate_prior_succeeds_with_lineage(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    assert second.plan.plan_revision == 2
    assert second.plan.supersedes == first.plan.digest
    assert list(second.plan.derived_from_refs) == [first.plan.digest]
    assert second.plan.prior_revision is first.plan


def test_revision_2_with_target_1_decision_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    with pytest.raises(ValueError, match="PLAN_REVISION_MUST_MATCH_DECISION_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=2,
                             prior_revision=first.plan)


def test_skipped_revision_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    with pytest.raises(ValueError, match="PRIOR_REVISION_MUST_IMMEDIATELY_PRECEDE_THIS_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 3), plan_id="plan-1", plan_revision=3,
                             prior_revision=first.plan)


def test_different_plan_id_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    with pytest.raises(ValueError, match="PRIOR_REVISION_MUST_SHARE_PLAN_ID"):
        build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-2", plan_revision=2,
                             prior_revision=first.plan)


def test_save_load_preserves_lineage(monkeypatch, tmp_path: Path):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    path = save_real_plan(second, tmp_path / "real-plan.json")
    loaded = load_real_plan(path)
    assert loaded.plan.plan_revision == 2
    assert loaded.plan.supersedes == first.plan.digest
    assert list(loaded.plan.derived_from_refs) == [first.plan.digest]


def test_load_then_extend_to_next_revision(monkeypatch, tmp_path: Path):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    loaded = load_real_plan(save_real_plan(second, tmp_path / "real-plan.json"))
    third = build_real_edit_plan(bundle, _accept(bundle, 3), plan_id="plan-1", plan_revision=3,
                                 prior_revision=loaded.plan)
    assert third.plan.plan_revision == 3
    assert third.plan.supersedes == loaded.plan.digest


def test_export_eligibility_is_never_granted(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    assert second.plan.export_eligible is False


# --------------------------------------------------------------------------
# Adversarial lineage cases required by spec §9.4.
# Both use real EditPlanRevision values (never duck-typed stand-ins), because
# the accepted prior_revision type is frozen to EditPlanRevision.
# --------------------------------------------------------------------------

def test_incompatible_prior_plan_scope_refuses(monkeypatch):
    """A structurally valid immediate predecessor with a non-REAL scope refuses.

    Derived from a genuinely built revision 1 so the predecessor is a real,
    already-valid ``EditPlanRevision`` (pinned refinements remain the real
    binding-eligible ones); only the scope and its matching synthetic principal
    are substituted, so the ONLY failing predicate is scope compatibility.
    """
    from dataclasses import replace

    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    rid = next(iter(first.plan.pinned_decisions))
    fixture_decision = replace(
        first.plan.pinned_decisions[rid],
        principal_kind="SYNTHETIC_HUMAN",
        fixture_scope="SYNTHETIC_FIXTURE",
    )
    synthetic_prior = replace(
        first.plan,
        plan_scope="SYNTHETIC_FIXTURE",
        pinned_decisions={rid: fixture_decision},
    )
    assert synthetic_prior.plan_scope == "SYNTHETIC_FIXTURE"
    assert synthetic_prior.plan_revision == 1 and synthetic_prior.plan_id == "plan-1"
    with pytest.raises(ValueError, match="PRIOR_REVISION_MUST_HAVE_COMPATIBLE_PLAN_SCOPE"):
        build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                             prior_revision=synthetic_prior)


def test_forged_lineage_with_extra_derived_ref_refuses(tmp_path: Path, monkeypatch):
    def mutate(plan):
        plan["derived_from_refs"] = list(plan["derived_from_refs"]) + ["e" * 64]

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2(tmp_path, monkeypatch, mutate=mutate))


def test_forged_lineage_missing_supersedes_link_refuses(tmp_path: Path, monkeypatch):
    def mutate(plan):
        plan["derived_from_refs"] = []

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2(tmp_path, monkeypatch, mutate=mutate))


def test_revision1_with_forged_lineage_refuses(tmp_path: Path, monkeypatch):
    """Revision 1 must carry no lineage at all."""
    import json

    from vip_fvs.real_plan import _canonical, _digest

    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    path = save_real_plan(first, tmp_path / "sealed.json")
    record = json.loads(path.read_bytes()[:-1].decode("utf-8"))
    record["plan"]["derived_from_refs"] = ["f" * 64]
    record.pop("record_digest", None)
    record["record_digest"] = _digest(record)
    forged = tmp_path / "forged.json"
    forged.write_bytes(_canonical(record) + b"\n")
    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(forged)


def _forge_revision2(tmp_path: Path, monkeypatch, *, mutate) -> Path:
    """Seal a valid revision 2, then rewrite raw plan lineage and re-seal the envelope.

    Only the outer ``record_digest`` is recomputed. ``plan_digest`` is deliberately
    NOT recomputed, so these records prove that raw lineage classification happens
    before the plan-digest comparison AND before Gate-3 construction.
    """
    import json

    from vip_fvs.real_plan import _canonical, _digest

    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    path = save_real_plan(second, tmp_path / "sealed.json")
    record = json.loads(path.read_bytes()[:-1].decode("utf-8"))
    mutate(record["plan"])
    record.pop("record_digest", None)
    record["record_digest"] = _digest(record)
    forged = tmp_path / "forged.json"
    forged.write_bytes(_canonical(record) + b"\n")
    return forged


def test_forged_lineage_missing_supersedes_key_refuses(tmp_path: Path, monkeypatch):
    """Revision >1 with no supersedes at all: raw-lineage classification, not Gate-3."""
    def mutate(plan):
        plan.pop("supersedes", None)

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2(tmp_path, monkeypatch, mutate=mutate))


def test_forged_lineage_malformed_supersedes_refuses(tmp_path: Path, monkeypatch):
    """Revision >1 with a non-lowercase-hex supersedes.

    ``derived_from_refs`` is kept consistent with the malformed value so the ONLY
    failing predicate is digest-shape validity — not list equality. Without the
    raw pre-construction check, Gate-3 would raise its own
    'supersedes must name a prior revision digest' and mask this code.
    """
    def mutate(plan):
        plan["supersedes"] = "NOT-LOWERCASE-HEX"
        plan["derived_from_refs"] = ["NOT-LOWERCASE-HEX"]

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2(tmp_path, monkeypatch, mutate=mutate))


def test_invalid_prior_revision_type_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    with pytest.raises(ValueError, match="PRIOR_REVISION_MUST_BE_AN_EDIT_PLAN_REVISION"):
        build_real_edit_plan(
            bundle,
            _accept(bundle, 2),
            plan_id="plan-1",
            plan_revision=2,
            prior_revision=object(),
        )


# --------------------------------------------------------------------------
# Independent-review hardening: raw lineage must be classified before ANY
# Gate-3 object is constructed, and non-exact plan_revision types or a
# non-list derived_from_refs must not escape as unrelated exceptions.
# --------------------------------------------------------------------------

def _forge_revision2_raw(tmp_path: Path, monkeypatch, *, mutate) -> Path:
    """Forge a revision-2 sealed record without building a plan from it first."""
    import json

    from vip_fvs.real_plan import _canonical, _digest

    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    path = save_real_plan(second, tmp_path / "sealed.json")
    record = json.loads(path.read_bytes()[:-1].decode("utf-8"))
    mutate(record)
    record.pop("record_digest", None)
    record["record_digest"] = _digest(record)
    forged = tmp_path / "forged.json"
    forged.write_bytes(_canonical(record) + b"\n")
    return forged


def test_raw_lineage_check_precedes_mapping_construction(tmp_path: Path, monkeypatch):
    """Malformed supersedes must win over an independently malformed mapping.

    Without raw-lineage-first ordering, SourceTimelineMapping raises its own
    'source interval must be non-empty half-open' and masks the Root-G code.
    """
    def mutate(record):
        record["plan"]["supersedes"] = "NOT-LOWERCASE-HEX"
        record["plan"]["derived_from_refs"] = ["NOT-LOWERCASE-HEX"]
        record["mapping"]["source_end_pts"] = record["mapping"]["source_start_pts"]

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2_raw(tmp_path, monkeypatch, mutate=mutate))


def test_raw_lineage_check_precedes_placement_construction(tmp_path: Path, monkeypatch):
    """Malformed supersedes must win over an independently malformed placement."""
    def mutate(record):
        record["plan"].pop("supersedes", None)
        record["placement"]["timeline_end_ticks"] = 0

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2_raw(tmp_path, monkeypatch, mutate=mutate))


@pytest.mark.parametrize("bad_revision", [True, False, 1.0, "1", None])
def test_non_exact_plan_revision_type_refuses(tmp_path: Path, monkeypatch, bad_revision):
    """plan_revision must be an exact non-boolean int, matching construction."""
    def mutate(record):
        record["plan"]["plan_revision"] = bad_revision

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2_raw(tmp_path, monkeypatch, mutate=mutate))


@pytest.mark.parametrize("bad_derived", [None, 1, "deadbeef", {"a": 1}])
def test_non_list_derived_from_refs_refuses(tmp_path: Path, monkeypatch, bad_derived):
    """A non-list derived_from_refs must refuse with the lineage code, not TypeError."""
    def mutate(record):
        record["plan"]["derived_from_refs"] = bad_derived

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2_raw(tmp_path, monkeypatch, mutate=mutate))
