"""Adversarial RED tests for the real-plan authority boundary."""
from __future__ import annotations

import pytest

from tests.vip_fvs.unit.test_real_plan import _accept, _binding_fixture, _bundle
from vip_fvs.review_bundle import ReviewBundle


@pytest.mark.parametrize("decision_class, kwargs", [
    ("REJECT", {}),
    ("MODIFY", {"requested_modification": "Recheck endpoint."}),
])
def test_reject_and_modify_never_construct_real_plan(monkeypatch, decision_class, kwargs):
    _binding_fixture(monkeypatch)
    from vip_fvs.real_plan import build_real_edit_plan

    bundle = _bundle()
    decision = _accept(bundle, decision_class=decision_class, **kwargs)
    with pytest.raises((ValueError, TypeError)):
        build_real_edit_plan(bundle, decision, plan_id="plan-1", plan_revision=1)


def test_mismatched_bundle_decision_pins_are_not_authority(monkeypatch):
    _binding_fixture(monkeypatch)
    from vip_fvs.real_plan import build_real_edit_plan

    first = _bundle()
    # A distinct bundle identity is required for this boundary test.  The
    # fixture payload is otherwise intentionally identical, so using the
    # helper defaults would create the same sealed record and cannot represent
    # a mismatch.
    second = ReviewBundle.create(
        _bundle().payload, run_id="run-1", bundle_id="bundle-2",
        created_at="2026-09-21T12:00:00Z",
    )
    decision = _accept(first)
    with pytest.raises((ValueError, TypeError)):
        build_real_edit_plan(second, decision, plan_id="plan-1", plan_revision=1)


def test_digest_valid_decision_with_unreviewed_subinterval_is_not_authority(monkeypatch):
    """A digest-valid envelope must still be rebound to the sealed refinement."""
    _binding_fixture(monkeypatch)
    from hashlib import sha256
    import json
    from vip_fvs.human_decision import HumanDecisionArtifact
    from vip_fvs.real_plan import build_real_edit_plan

    bundle = _bundle()
    record = _accept(bundle).to_record()
    record["payload"]["accepted_sub_interval_ref"] = "semantic:0.1-0.2"
    preimage = {key: record[key] for key in ("record_id", "record_type", "record_schema_version", "payload")}
    record["record_digest"] = sha256(json.dumps(preimage, ensure_ascii=False, sort_keys=True,
                                                  separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    decision = HumanDecisionArtifact.from_record(record)
    with pytest.raises(ValueError, match="accepted_sub_interval_ref"):
        build_real_edit_plan(bundle, decision, plan_id="plan-1", plan_revision=1)


def test_fabricated_human_principal_authority_does_not_make_plan_exportable(monkeypatch):
    _binding_fixture(monkeypatch)
    from vip_fvs.real_plan import build_real_edit_plan

    bundle = _bundle()
    artifacts = build_real_edit_plan(bundle, _accept(bundle, principal_ref="human:invented-registry"), plan_id="plan-1", plan_revision=1)
    assert artifacts.plan.real_authority_eligible is True
    assert artifacts.plan.export_eligible is False
    assert artifacts.projected_decision.principal_authority_evidence is None


@pytest.mark.parametrize("field", ["refinement_id", "source_revision_id", "source_sha256", "refinement_evidence_digest"])
def test_exact_decision_pins_cannot_be_substituted(monkeypatch, field):
    _binding_fixture(monkeypatch)
    from vip_fvs.real_plan import build_real_edit_plan

    bundle = _bundle()
    decision = _accept(bundle)
    record = decision.to_record()
    record["payload"][field] = "1" * 64 if field.endswith(("digest", "sha256")) else "substituted"
    from vip_fvs.human_decision import HumanDecisionArtifact
    # The tamper is rejected at the sealed decision envelope boundary before a
    # plan can be built.  Do not weaken that digest check merely to exercise a
    # later plan-level check.
    with pytest.raises(ValueError, match="record digest mismatch"):
        HumanDecisionArtifact.from_record(record)
