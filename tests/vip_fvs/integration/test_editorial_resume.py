"""RED pause/resume contract at the editorial decision boundary."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.vip_fvs.unit.test_human_decision import bundle, decision_args
from vip_fvs.human_decision import create_human_decision, load_human_decision, save_human_decision


def test_resume_accept_creates_only_decision_and_preserves_awaiting_bundle(tmp_path: Path):
    sealed = bundle(tmp_path)
    decision = create_human_decision(bundle=sealed, **decision_args(sealed))
    decision_path = save_human_decision(decision, tmp_path / "decision.json")
    loaded = load_human_decision(decision_path, bundle_path=tmp_path / "bundle.json")
    assert loaded.to_record()["payload"]["plan_action"] == "BUILD_REAL_PLAN"
    assert sealed.to_record()["payload"]["review_status"] == "AWAITING_EDITORIAL_DECISION"


def test_resume_reject_and_modify_are_planless(tmp_path: Path):
    sealed = bundle(tmp_path)
    reject = create_human_decision(bundle=sealed, **decision_args(sealed, decision_class="REJECT"))
    modify = create_human_decision(bundle=sealed, **decision_args(sealed, decision_class="MODIFY", requested_modification="Use a different reviewed interval."))
    assert reject.to_record()["payload"]["plan_action"] == "NONE"
    assert modify.to_record()["payload"]["plan_action"] == "NONE"
    assert sealed.to_record()["payload"]["decision"] is None


def test_editorial_resume_follows_append_only_supersession_head(tmp_path: Path):
    from vip_fvs.human_decision import resolve_human_decision_resume

    sealed = bundle(tmp_path)
    bundle_path = tmp_path / "bundle.json"
    before = bundle_path.read_bytes()
    first = create_human_decision(bundle=sealed, **decision_args(sealed))
    first_path = save_human_decision(first, tmp_path / "decision-v1.json")
    assert resolve_human_decision_resume(bundle_path, [first_path]).record_digest == first.record_digest

    second = create_human_decision(bundle=sealed, **decision_args(
        sealed, decision_id="decision-2", rationale="The prior decision is explicitly superseded.",
        supersedes=first.record_digest))
    second_path = save_human_decision(second, tmp_path / "decision-v2.json")
    assert resolve_human_decision_resume(bundle_path, [first_path, second_path]).record_digest == second.record_digest
    assert bundle_path.read_bytes() == before


def test_historical_v1_can_resume_only_after_current_e01_revalidation(tmp_path: Path):
    from vip_fvs.review_bundle import ReviewBundle, dependency_digest, record_digest

    current = bundle(tmp_path)
    record = current.to_record()
    record["record_schema_version"] = "vip_fvs.review_bundle.v1"
    record["payload"]["refinement"].pop("request_identity")
    record["payload"]["dependency_digest"] = dependency_digest(record["payload"])
    record["record_digest"] = record_digest(record)

    historical = ReviewBundle.from_record(record)
    assert historical.to_record()["record_schema_version"] == "vip_fvs.review_bundle.v1"
    assert "request_identity" not in historical.payload["refinement"]
    assert historical.current_e01_validated is True
    with pytest.raises(ValueError, match="cannot be republished"):
        from vip_fvs.review_bundle import save_review_bundle
        save_review_bundle(historical, tmp_path / "v1-copy.json")
    decision = create_human_decision(bundle=historical, **decision_args(historical))
    assert decision.to_record()["payload"]["plan_action"] == "BUILD_REAL_PLAN"
