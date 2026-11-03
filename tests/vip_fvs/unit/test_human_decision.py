"""RED contracts for immutable human editorial decisions."""
from __future__ import annotations

import copy
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from tests.vip_fvs.unit.test_review_bundle import payload
from vip_fvs.review_bundle import ReviewBundle, save_review_bundle
from vip_fvs.human_decision import (
    create_human_decision,
    load_human_decision,
    save_human_decision,
)

ZERO = "0" * 64


def bundle(tmp_path: Path) -> ReviewBundle:
    import hashlib

    from tests.vip_fvs.unit.test_real_source_temporal_authority import _refine_named_source, _valid_refinement_request_identity

    refinement, source = _refine_named_source(tmp_path / "source", _valid_refinement_request_identity())
    artifact_path = tmp_path / "refinement.json"
    artifact_path.write_text(json.dumps(refinement, sort_keys=True, separators=(",", ":")) + "\n")
    value = payload()
    value["source"].update({"source_revision_id": refinement["source_revision_id"],
                            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                            "source_byte_count": source.stat().st_size,
                            "selected_stream_index": refinement["stream_index"], "timebase": refinement["time_base"]})
    value["generation"]["attempt_id"] = refinement["attempt_id"]
    value["refinement"].update({"refinement_id": refinement["refinement_id"],
                                "source_revision_id": refinement["source_revision_id"],
                                "selected_stream_index": refinement["stream_index"],
                                "source_pts_interval": {"start": refinement["start_ticks"], "end": refinement["end_ticks"], "time_domain": "source_pts", "endpoint_semantics": "half_open"},
                                "timebase": refinement["time_base"], "attempt_id": refinement["attempt_id"],
                                "evidence_artifact_ref": str(artifact_path), "evidence_digest": refinement["evidence_digest"]})
    value = ReviewBundle.create(value, run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    save_review_bundle(value, tmp_path / "bundle.json")
    return value


def decision_args(value: ReviewBundle, **overrides):
    result = {
        "decision_id": "decision-1", "principal_kind": "human", "principal_ref": "human:editor-1",
        "decision_class": "ACCEPT", "rationale": "The reviewed refinement is suitable for planning.",
        "target_plan_revision": 1, "requested_modification": None, "accepted_sub_interval_ref": None,
    }
    result.update(overrides)
    return result


def test_exact_classes_principal_rationale_and_pins(tmp_path: Path):
    b = bundle(tmp_path)
    d = create_human_decision(bundle=b, **decision_args(b))
    record = d.to_record()
    assert set(record) == {"record_id", "record_type", "record_schema_version", "record_digest", "payload"}
    p = record["payload"]
    assert p["decision_class"] == "ACCEPT"
    assert p["principal_kind"] == "human" and p["principal_ref"] == "human:editor-1"
    assert p["rationale"]
    assert p["bundle_record_digest"] == b.record_digest
    assert p["bundle_dependency_digest"] == b.dependency_digest
    assert p["refinement_id"] == b.payload["refinement"]["refinement_id"]
    assert p["refinement_evidence_digest"] == b.payload["refinement"]["evidence_digest"]
    assert p["source_revision_id"] == b.payload["source"]["source_revision_id"]
    assert p["source_sha256"] == b.payload["source"]["source_sha256"]
    assert p["evidence_class"] == "EDITORIAL_INFERENCE"


@pytest.mark.parametrize("decision_class", ["DEFER", "", "MODEL_ACCEPT"])
def test_only_accept_reject_modify_are_admitted(tmp_path: Path, decision_class: str):
    with pytest.raises((ValueError, TypeError)):
        create_human_decision(bundle=bundle(tmp_path), **decision_args(bundle(tmp_path), decision_class=decision_class))


@pytest.mark.parametrize("principal_kind", ["model", "tool", "SYNTHETIC_HUMAN"])
def test_model_or_synthetic_principal_is_rejected(tmp_path: Path, principal_kind: str):
    b = bundle(tmp_path)
    with pytest.raises((ValueError, TypeError)):
        create_human_decision(bundle=b, **decision_args(b, principal_kind=principal_kind))
    with pytest.raises((ValueError, TypeError)):
        create_human_decision(bundle=b, **decision_args(b, principal_ref="fixture:editor"))


@pytest.mark.parametrize("rationale", ["", "   ", "\t\n"])
def test_empty_rationale_is_rejected(tmp_path: Path, rationale: str):
    b = bundle(tmp_path)
    with pytest.raises((ValueError, TypeError)):
        create_human_decision(bundle=b, **decision_args(b, rationale=rationale))


def test_modify_requires_request_and_reject_is_planless(tmp_path: Path):
    b = bundle(tmp_path)
    with pytest.raises((ValueError, TypeError)):
        create_human_decision(bundle=b, **decision_args(b, decision_class="MODIFY"))
    modify = create_human_decision(bundle=b, **decision_args(b, decision_class="MODIFY", requested_modification="Review the endpoint.") )
    reject = create_human_decision(bundle=b, **decision_args(b, decision_class="REJECT"))
    assert modify.to_record()["payload"]["plan_action"] == "NONE"
    assert modify.to_record()["payload"]["disposition"] == "MODIFICATION_REQUESTED"
    assert reject.to_record()["payload"]["plan_action"] == "NONE"
    assert reject.to_record()["payload"]["disposition"] == "REJECTED"


def test_accept_is_plan_action_only_and_bundle_stays_awaiting(tmp_path: Path):
    b = bundle(tmp_path)
    d = create_human_decision(bundle=b, **decision_args(b))
    assert d.to_record()["payload"]["plan_action"] == "BUILD_REAL_PLAN"
    assert b.to_record()["payload"]["review_status"] == "AWAITING_EDITORIAL_DECISION"
    assert b.to_record()["payload"]["decision"] is None


@pytest.mark.parametrize("field", ["refinement_id", "refinement_evidence_digest", "source_revision_id", "source_sha256"])
def test_dependency_pin_substitution_is_rejected(tmp_path: Path, field: str):
    b = bundle(tmp_path)
    value = decision_args(b)
    value[field] = "different" if field in {"refinement_id", "source_revision_id"} else "1" * 64
    with pytest.raises((ValueError, TypeError)):
        create_human_decision(bundle=b, **value)


@pytest.mark.parametrize("revision", [0, -1, True, False, "1"])
def test_target_plan_revision_must_be_positive_integer(tmp_path: Path, revision):
    b = bundle(tmp_path)
    with pytest.raises((ValueError, TypeError)):
        create_human_decision(bundle=b, **decision_args(b, target_plan_revision=revision))


def test_persistence_is_immutable_and_readback_validates_pins(tmp_path: Path):
    b = bundle(tmp_path)
    d = create_human_decision(bundle=b, **decision_args(b))
    path = save_human_decision(d, tmp_path / "decision.json")
    loaded = load_human_decision(path, bundle_path=tmp_path / "bundle.json")
    assert loaded.record_digest == d.record_digest
    assert loaded.to_record() == d.to_record()
    with pytest.raises(ValueError):
        save_human_decision(create_human_decision(bundle=b, **decision_args(b, rationale="changed")), path)


def test_accepted_sub_interval_must_be_the_reviewed_refinement(tmp_path: Path):
    b = bundle(tmp_path)
    reviewed = b.payload["refinement"]["refinement_id"]
    accepted = create_human_decision(
        bundle=b, **decision_args(b, accepted_sub_interval_ref=reviewed)
    )
    assert accepted.payload["accepted_sub_interval_ref"] == reviewed
    for unreviewed in ("source_pts:40-80", "semantic_seconds:1.0-2.0", "refinement:other"):
        with pytest.raises(ValueError, match="reviewed refinement"):
            create_human_decision(
                bundle=b, **decision_args(b, accepted_sub_interval_ref=unreviewed)
            )


def test_changed_decision_is_new_artifact_with_explicit_supersession(tmp_path: Path):
    b = bundle(tmp_path)
    original = create_human_decision(bundle=b, **decision_args(b))
    original_path = save_human_decision(original, tmp_path / "decision-v1.json")
    changed = create_human_decision(
        bundle=b,
        **decision_args(
            b,
            decision_id="decision-2",
            rationale="A revised human disposition is required.",
            supersedes=original.record_digest,
        ),
    )
    changed_path = save_human_decision(changed, tmp_path / "decision-v2.json")
    assert changed.record_digest != original.record_digest
    assert changed.payload["supersedes"] == original.record_digest
    assert load_human_decision(original_path).to_record() == original.to_record()
    assert load_human_decision(changed_path).to_record() == changed.to_record()


def test_new_path_supersession_must_resolve_same_lineage_prior(tmp_path: Path):
    b = bundle(tmp_path)
    original = create_human_decision(bundle=b, **decision_args(b))
    save_human_decision(original, tmp_path / "decision-v1.json")

    missing = create_human_decision(
        bundle=b,
        **decision_args(b, decision_id="decision-missing", supersedes="0" * 64),
    )
    with pytest.raises(ValueError, match="superseded decision"):
        save_human_decision(missing, tmp_path / "decision-v2.json")

    other_bundle = ReviewBundle.create(
        b.payload, run_id="run-2", bundle_id="bundle-2", created_at="2026-09-21T12:01:00Z"
    )
    other = create_human_decision(
        bundle=other_bundle,
        **decision_args(other_bundle, decision_id="decision-other", supersedes=original.record_digest),
    )
    with pytest.raises(ValueError, match="superseded decision"):
        save_human_decision(other, tmp_path / "decision-v3.json")


def test_concurrent_publishers_cannot_clobber_sealed_decision(tmp_path: Path, monkeypatch):
    b = bundle(tmp_path)
    path = tmp_path / "decision.json"
    decisions = [
        create_human_decision(bundle=b, **decision_args(b, decision_id=f"decision-{i}", rationale=f"Rationale {i}."))
        for i in range(2)
    ]

    import vip_fvs.human_decision as module
    original_link = module.os.link
    entered = []
    import threading
    rendezvous = threading.Barrier(2)

    def synchronized_link(*args, **kwargs):
        entered.append(True)
        rendezvous.wait(timeout=5)
        return original_link(*args, **kwargs)

    monkeypatch.setattr(module.os, "link", synchronized_link)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda value: _save_capturing(value, path), decisions))

    assert len(entered) == 2
    assert sorted(outcomes) == ["error", "ok"]
    assert load_human_decision(path).record_digest in {d.record_digest for d in decisions}


def _save_capturing(decision, path):
    try:
        save_human_decision(decision, path)
    except ValueError:
        return "error"
    return "ok"


def test_replacing_existing_path_requires_supersession_link(tmp_path: Path):
    b = bundle(tmp_path)
    path = tmp_path / "decision.json"
    original = create_human_decision(bundle=b, **decision_args(b))
    save_human_decision(original, path)
    changed = create_human_decision(bundle=b, **decision_args(b, rationale="changed"))
    with pytest.raises(ValueError, match="explicitly supersede"):
        save_human_decision(changed, path)


def test_supersession_lineage_cannot_fork_from_one_decision(tmp_path: Path):
    b = bundle(tmp_path)
    original = create_human_decision(bundle=b, **decision_args(b))
    save_human_decision(original, tmp_path / "decision-v1.json")
    first = create_human_decision(bundle=b, **decision_args(
        b, decision_id="decision-2a", rationale="First superseding decision.", supersedes=original.record_digest))
    save_human_decision(first, tmp_path / "decision-v2a.json")
    second = create_human_decision(bundle=b, **decision_args(
        b, decision_id="decision-2b", rationale="Conflicting second branch.", supersedes=original.record_digest))

    with pytest.raises(ValueError, match="fork"):
        save_human_decision(second, tmp_path / "decision-v2b.json")


def test_decision_lineage_cannot_start_a_second_root(tmp_path: Path):
    b = bundle(tmp_path)
    first = create_human_decision(bundle=b, **decision_args(b))
    save_human_decision(first, tmp_path / "decision-v1.json")
    second = create_human_decision(bundle=b, **decision_args(
        b, decision_id="decision-2", rationale="A second unlinked root is not valid."))

    with pytest.raises(ValueError, match="second root"):
        save_human_decision(second, tmp_path / "decision-v2.json")


@pytest.mark.parametrize("decision_class,modification", [("REJECT", None), ("MODIFY", "Review another interval.")])
def test_reject_and_modify_cannot_resume_same_review_lineage(tmp_path: Path, decision_class, modification):
    b = bundle(tmp_path)
    prior = create_human_decision(bundle=b, **decision_args(
        b, decision_class=decision_class, requested_modification=modification))
    save_human_decision(prior, tmp_path / "decision-v1.json")
    accept = create_human_decision(bundle=b, **decision_args(
        b, decision_id="decision-2", rationale="Attempt to continue this reviewed refinement.",
        supersedes=prior.record_digest))

    with pytest.raises(ValueError, match="new review"):
        save_human_decision(accept, tmp_path / "decision-v2.json")
