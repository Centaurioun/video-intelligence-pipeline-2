"""RED contracts for the real-source plan bridge.

The fixture is synthetic bytes and a sealed ReviewBundle; it never opens archive
media or invokes a model/provider.  These tests specify the narrow source-PTS to
timeline bridge that Task 5 is allowed to construct.
"""
from __future__ import annotations

from pathlib import Path
import copy
import hashlib
import json
import tempfile

import pytest

from gate3.rational import TimeBase
from gate3.timeline import TimelineDomain
from tests.vip_fvs.unit.test_review_bundle import payload
from vip_fvs.human_decision import create_human_decision
from vip_fvs.review_bundle import ReviewBundle


def _bundle(suffix: str = "", revision_id: str = "rev-1") -> ReviewBundle:
    from gate3.fixturegen import build_mp4
    from vip_fvs.refinement_adapter import refine_retrieval_candidate
    source = Path(tempfile.gettempdir()) / f"vip-fvs-v3-plan-fixture{suffix}.mp4"
    source.write_bytes(build_mp4(media_timescale=1000, sample_deltas=(40, 40, 40)))
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    measured = dict(refine_retrieval_candidate(
        {"source_path": str(source), "source_sha256": source_sha, "pts": 40, "rank": 1, "score": .9},
        source_path=source, source_revision_id=revision_id, requested_pts=(40, 80),
        stream_index=0, selected_stream_index=0, attempt_id="attempt-1",
    ).measured_refinement)
    refinement_id = "refinement-1" if revision_id == "rev-1" else f"refinement-{revision_id}"
    measured["refinement_id"] = refinement_id
    probe = source.with_name(f"vip-fvs-v3-plan-probe{suffix}.json")
    probe.write_text(json.dumps({"source_bytes_sha256": source_sha, "stream_index": 0,
                                 "media_timescale": 1000, "pts_ticks": [0, 40, 80],
                                 "frames": [{"stream_index": 0, "best_effort_timestamp": "0"},
                                            {"stream_index": 0, "best_effort_timestamp": "40"},
                                            {"stream_index": 0, "best_effort_timestamp": "80"}]},
                                sort_keys=True, separators=(",", ":")) + "\n")
    measured["source_probe_artifact_ref"] = str(probe)
    measured["source_probe_digest"] = hashlib.sha256(probe.read_bytes()).hexdigest()
    artifact = source.with_name(f"vip-fvs-v3-plan-refinement{suffix}.json")
    artifact.write_text(json.dumps(measured, sort_keys=True, separators=(",", ":")) + "\n")
    raw = copy.deepcopy(payload())
    raw["source"]["source_revision_id"] = revision_id
    raw["refinement"]["refinement_id"] = refinement_id
    raw["refinement"]["source_revision_id"] = revision_id
    raw["source"]["source_sha256"] = source_sha
    raw["source"]["source_byte_count"] = source.stat().st_size
    raw["source"]["timebase"] = {"num": 1, "den": 1000}
    raw["source"]["probe_artifact_ref"] = str(probe)
    raw["source"]["probe_digest"] = measured["source_probe_digest"]
    raw["refinement"].update({"evidence_artifact_ref": str(artifact), "evidence_digest": measured["evidence_digest"], "timebase": {"num": 1, "den": 1000}})
    return ReviewBundle.create(raw, run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")


def _accept(bundle: ReviewBundle, **overrides):
    args = {
        "decision_id": "decision-1", "principal_kind": "human", "principal_ref": "human:editor-1",
        "decision_class": "ACCEPT", "rationale": "Reviewed measured source interval.",
        "target_plan_revision": 1,
    }
    args.update(overrides)
    return create_human_decision(bundle=bundle, **args)


def _binding_fixture(monkeypatch):
    """The ReviewBundle fixture is validated at its own boundary.

    Gate-3's byte-bound predicate is a separate measured-media concern; this
    seam lets the plan tests focus on exact identity and coordinate contracts.
    """
    # V3 uses the real byte-bound predicate; retained for call-site compatibility.
    return None


def test_source_timeline_mapping_is_exact_same_timebase_and_half_open():
    from vip_fvs.real_plan import SourceTimelineMapping

    mapping = SourceTimelineMapping(
        mapping_id="mapping-1", source_refinement_id="refinement-1",
        source_timebase_num=1, source_timebase_den=1000,
        source_start_pts=40, source_end_pts=80,
        timeline_domain=TimelineDomain("plan-1-timeline", TimeBase(1, 1000)),
        offset_ticks=-40, scale_num=1, scale_den=1,
    )
    assert mapping.timeline_tick(40) == 0
    assert mapping.timeline_tick(79) == 39
    assert mapping.record_digest == mapping.compute_digest()
    with pytest.raises(ValueError):
        SourceTimelineMapping(
            mapping_id="bad", source_refinement_id="refinement-1",
            source_timebase_num=1, source_timebase_den=1000,
            source_start_pts=40, source_end_pts=80,
            timeline_domain=TimelineDomain("other", TimeBase(1, 2000)),
            offset_ticks=-40, scale_num=1, scale_den=1,
        )
    with pytest.raises(ValueError):
        SourceTimelineMapping(
            mapping_id="bad-scale", source_refinement_id="refinement-1",
            source_timebase_num=1, source_timebase_den=1000,
            source_start_pts=40, source_end_pts=80,
            timeline_domain=TimelineDomain("plan-1-timeline", TimeBase(1, 1000)),
            offset_ticks=-40, scale_num=2, scale_den=1,
        )


def test_accept_builds_one_v1_order_zero_half_open_real_plan_and_exact_pins(monkeypatch):
    _binding_fixture(monkeypatch)
    from vip_fvs.real_plan import build_real_edit_plan

    bundle = _bundle()
    decision = _accept(bundle)
    artifacts = build_real_edit_plan(bundle, decision, plan_id="plan-1", plan_revision=1)
    assert artifacts.plan.plan_scope == "REAL"
    assert artifacts.plan.export_plan_structurally_valid is True
    assert artifacts.plan.export_eligible is False
    assert artifacts.mapping.source_refinement_id == bundle.payload["refinement"]["refinement_id"]
    assert artifacts.mapping.offset_ticks == -40
    assert artifacts.mapping.scale_num == artifacts.mapping.scale_den == 1
    assert artifacts.placement.track == "V1"
    assert artifacts.placement.order_index == 0
    assert (artifacts.placement.timeline_start_ticks, artifacts.placement.timeline_end_ticks) == (0, 40)
    assert artifacts.placement.endpoint_semantics == "half_open"
    assert artifacts.plan.pinned_evidence_digests["refinement-1"] == bundle.payload["refinement"]["evidence_digest"]
    assert artifacts.plan.pinned_decisions["refinement-1"].decision_id == decision.payload["decision_id"]


def test_real_plan_retains_digests_and_canonical_readback(monkeypatch, tmp_path: Path):
    _binding_fixture(monkeypatch)
    from vip_fvs.real_plan import build_real_edit_plan, load_real_plan, save_real_plan

    bundle = _bundle()
    artifacts = build_real_edit_plan(bundle, _accept(bundle), plan_id="plan-1", plan_revision=1)
    assert artifacts.plan_digest == artifacts.plan.digest
    assert artifacts.placement_digest
    assert artifacts.mapping_digest == artifacts.mapping.record_digest
    path = save_real_plan(artifacts, tmp_path / "real-plan.json")
    loaded = load_real_plan(path)
    assert loaded.plan_digest == artifacts.plan_digest
    assert loaded.placement_digest == artifacts.placement_digest
    assert loaded.mapping_digest == artifacts.mapping_digest
    assert loaded.plan.to_record() == artifacts.plan.to_record()


def test_real_plan_readback_recomputes_retained_digests_and_links(monkeypatch, tmp_path: Path):
    _binding_fixture(monkeypatch)
    from hashlib import sha256
    import json
    from vip_fvs.real_plan import build_real_edit_plan, load_real_plan, save_real_plan

    bundle = _bundle()
    artifacts = build_real_edit_plan(bundle, _accept(bundle), plan_id="plan-1", plan_revision=1)
    path = save_real_plan(artifacts, tmp_path / "real-plan.json")
    record = json.loads(path.read_text())
    record["placement_digest"] = "0" * 64
    preimage = {key: record[key] for key in record if key != "record_digest"}
    record["record_digest"] = sha256(json.dumps(preimage, ensure_ascii=False, sort_keys=True,
                                                  separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    path.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    with pytest.raises(ValueError, match="placement digest"):
        load_real_plan(path)


def test_real_plan_readback_rejects_unknown_or_noncanonical_envelope(monkeypatch, tmp_path: Path):
    _binding_fixture(monkeypatch)
    import json
    from vip_fvs.real_plan import build_real_edit_plan, load_real_plan, save_real_plan

    bundle = _bundle()
    artifacts = build_real_edit_plan(bundle, _accept(bundle), plan_id="plan-1", plan_revision=1)
    path = save_real_plan(artifacts, tmp_path / "real-plan.json")
    record = json.loads(path.read_text())
    record["unknown"] = True
    path.write_text(json.dumps(record, indent=2) + "\n")
    with pytest.raises(ValueError):
        load_real_plan(path)


def test_plan_rejects_semantic_interval_as_source_authority(monkeypatch):
    _binding_fixture(monkeypatch)
    raw = payload()
    raw["refinement"]["source_pts_interval"]["time_domain"] = "semantic_seconds"
    with pytest.raises((ValueError, TypeError)):
        ReviewBundle.create(raw, run_id="run-1", bundle_id="bundle-mutated", created_at="2026-09-21T12:00:00Z")


def test_missing_evidence_pin_and_fabricated_policy_authority_fail_closed(monkeypatch):
    _binding_fixture(monkeypatch)
    from vip_fvs.real_plan import build_real_edit_plan

    bundle = _bundle()
    decision = _accept(bundle)
    with pytest.raises((ValueError, TypeError)):
        build_real_edit_plan(bundle, decision, plan_id="plan-1", plan_revision=1, pinned_evidence_digests={})
    with pytest.raises((ValueError, TypeError)):
        build_real_edit_plan(bundle, decision, plan_id="plan-1", plan_revision=1, policy_decision_ref="fabricated-policy")


def test_multi_selection_plan_pins_each_source_and_is_deterministic(monkeypatch):
    from vip_fvs.real_plan import RealPlanSelection, build_real_edit_plan_from_selections

    first = _bundle()
    second = _bundle("-second", "rev-2")
    selections = [
        RealPlanSelection(first, _accept(first, decision_id="decision-1"), timeline_start_ticks=0),
        RealPlanSelection(second, _accept(second, decision_id="decision-2"), timeline_start_ticks=40),
    ]
    built = build_real_edit_plan_from_selections(selections, plan_id="plan-multi", plan_revision=1)
    rebuilt = build_real_edit_plan_from_selections(selections, plan_id="plan-multi", plan_revision=1)
    assert built.plan.source_revision_ids == ("rev-1", "rev-2")
    assert len(built.placements) == len(built.mappings) == 2
    assert [p.timeline_start_ticks for p in built.placements] == [0, 40]
    assert [p.order_index for p in built.placements] == [0, 1]
    assert built.plan.digest == rebuilt.plan.digest
    assert built.plan.export_eligible is False


def test_lineage_successor_rejects_nonsequential_explicit_order_before_build(monkeypatch):
    from vip_fvs.real_plan import RealPlanSelection, build_real_edit_plan_from_selections

    first = _bundle("-order-first", "rev-order-first")
    second = _bundle("-order-second", "rev-order-second")
    selections = [
        RealPlanSelection(first, _accept(first, decision_id="decision-order-first"), order_index=1),
        RealPlanSelection(second, _accept(second, decision_id="decision-order-second"), order_index=0),
    ]
    with pytest.raises(ValueError, match="order_index"):
        build_real_edit_plan_from_selections(selections, plan_id="plan-order", plan_revision=1)


def test_v3_lineage_build_roundtrip_and_rebind_preserve_order(monkeypatch, tmp_path: Path):
    from vip_fvs.real_plan import (RealPlanSelection, build_real_edit_plan_from_selections,
                                   build_real_edit_plan_from_selections_with_lineage,
                                   load_real_plan, rebind_real_plan_selections, save_real_plan)

    first = _bundle("-v3-first", "rev-v3-first")
    second = _bundle("-v3-second", "rev-v3-second")
    selections = (
        RealPlanSelection(first, _accept(first, decision_id="decision-v3-first"), timeline_start_ticks=0),
        RealPlanSelection(second, _accept(second, decision_id="decision-v3-second"), timeline_start_ticks=40),
    )
    artifacts = build_real_edit_plan_from_selections_with_lineage(selections, plan_id="plan-v3", plan_revision=1)
    legacy_multi = build_real_edit_plan_from_selections(selections, plan_id="plan-v3", plan_revision=1)
    assert [item.order_index for item in artifacts.lineage] == [0, 1]
    assert [item.review_bundle_record_digest for item in artifacts.lineage] == [first.record_digest, second.record_digest]
    assert artifacts.plan_digest == legacy_multi.plan_digest
    explicit = (RealPlanSelection(first, selections[0].decision, timeline_start_ticks=0, order_index=0),
                RealPlanSelection(second, selections[1].decision, timeline_start_ticks=40, order_index=1))
    assert build_real_edit_plan_from_selections(explicit, plan_id="plan-v3", plan_revision=1).plan_digest == artifacts.plan_digest
    path = save_real_plan(artifacts, tmp_path / "v3.json")
    assert json.loads(path.read_text())["schema_version"] == "vip_fvs.real_plan.v3"
    loaded = load_real_plan(path)
    assert loaded.lineage == artifacts.lineage
    assert loaded.plan_digest == artifacts.plan_digest
    record = json.loads(path.read_text())
    digest_before = record["record_digest"]
    record["lineage"][0]["review_bundle_record_digest"] = "f" * 64
    preimage = {key: value for key, value in record.items() if key != "record_digest"}
    assert hashlib.sha256(json.dumps(preimage, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest() != digest_before
    assert rebind_real_plan_selections(loaded, selections) == selections


def test_v3_single_selection_builder_is_opt_in(monkeypatch, tmp_path: Path):
    from vip_fvs.real_plan import (build_real_edit_plan_with_lineage, load_real_plan,
                                   save_real_plan)

    bundle = _bundle("-v3-single", "rev-v3-single")
    artifacts = build_real_edit_plan_with_lineage(bundle, _accept(bundle, decision_id="decision-v3-single"),
        plan_id="plan-v3-single", plan_revision=1)
    assert len(artifacts.lineage) == 1
    path = save_real_plan(artifacts, tmp_path / "single-v3.json")
    assert json.loads(path.read_text())["schema_version"] == "vip_fvs.real_plan.v3"
    assert load_real_plan(path).lineage == artifacts.lineage


def test_v3_rebind_rejects_explicit_order_and_alternate_sealed_source(monkeypatch, tmp_path: Path):
    from vip_fvs.real_plan import (RealPlanSelection, build_real_edit_plan_from_selections_with_lineage,
                                   rebind_real_plan_selections, save_real_plan, load_real_plan)

    first = _bundle("-v3-rebind-first", "rev-v3-rebind-first")
    second = _bundle("-v3-rebind-second", "rev-v3-rebind-second")
    selections = [RealPlanSelection(first, _accept(first, decision_id="decision-v3-r1"), timeline_start_ticks=0),
                  RealPlanSelection(second, _accept(second, decision_id="decision-v3-r2"), timeline_start_ticks=40)]
    artifacts = build_real_edit_plan_from_selections_with_lineage(selections, plan_id="plan-v3-r", plan_revision=1)
    artifacts = load_real_plan(save_real_plan(artifacts, tmp_path / "v3-r.json"))
    with pytest.raises(ValueError, match="cardinality"):
        rebind_real_plan_selections(artifacts, selections[:1])
    with pytest.raises(ValueError, match="invalid"):
        rebind_real_plan_selections(artifacts, [object(), selections[1]])
    reordered = [RealPlanSelection(first, selections[0].decision, timeline_start_ticks=0, order_index=1), selections[1]]
    with pytest.raises(ValueError, match="order_index"):
        rebind_real_plan_selections(artifacts, reordered)
    alternate = _bundle("-v3-rebind-first-alternate", "rev-v3-rebind-first")
    substituted = [RealPlanSelection(alternate, _accept(alternate, decision_id="decision-v3-r1"), timeline_start_ticks=0), selections[1]]
    with pytest.raises(ValueError, match="source lineage"):
        rebind_real_plan_selections(artifacts, substituted)


def test_legacy_real_plan_has_no_lineage_and_cannot_rebind(monkeypatch, tmp_path: Path):
    from vip_fvs.real_plan import (RealPlanSelection, build_real_edit_plan_from_selections,
                                   load_real_plan, rebind_real_plan_selections, save_real_plan)

    bundle = _bundle("-legacy-no-lineage", "rev-legacy-no-lineage")
    selection = RealPlanSelection(bundle, _accept(bundle, decision_id="decision-legacy-no-lineage"))
    legacy = build_real_edit_plan_from_selections([selection], plan_id="plan-legacy", plan_revision=1)
    loaded = load_real_plan(save_real_plan(legacy, tmp_path / "legacy.json"))
    assert loaded.lineage == ()
    with pytest.raises(ValueError, match="verified v3"):
        rebind_real_plan_selections(loaded, [selection])


@pytest.mark.parametrize("field", [
    "placement_id", "order_index", "refinement_id", "decision_id",
    "review_bundle_record_digest", "review_bundle_dependency_digest", "human_decision_record_digest",
])
def test_v3_lineage_mutation_fails_rebind(monkeypatch, tmp_path: Path, field):
    from hashlib import sha256
    from vip_fvs.real_plan import (RealPlanSelection, build_real_edit_plan_from_selections_with_lineage,
                                   load_real_plan, rebind_real_plan_selections, save_real_plan)

    bundle = _bundle(f"-v3-mutate-{field}", f"rev-v3-mutate-{field}")
    selection = RealPlanSelection(bundle, _accept(bundle, decision_id=f"decision-v3-mutate-{field}"))
    artifacts = build_real_edit_plan_from_selections_with_lineage([selection], plan_id="plan-v3-mutate", plan_revision=1)
    path = save_real_plan(artifacts, tmp_path / f"{field}.json")
    record = json.loads(path.read_text())
    record["lineage"][0][field] = (1 if field == "order_index" else
        ("f" * 64 if field.endswith("digest") else "mutated-identity"))
    preimage = {key: value for key, value in record.items() if key != "record_digest"}
    record["record_digest"] = sha256(json.dumps(preimage, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    path.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    if field.endswith("digest"):
        loaded = load_real_plan(path)
        with pytest.raises(ValueError):
            rebind_real_plan_selections(loaded, [selection])
    else:
        with pytest.raises(ValueError):
            load_real_plan(path)


@pytest.mark.parametrize("mutation", ["unknown_lineage_key", "bad_digest", "duplicate", "omitted", "extra",
                                       "reordered", "unknown_version", "bad_record_digest",
                                       "unknown_envelope_key",
                                       "placement_omitted", "mapping_omitted", "decision_omitted",
                                       "placement_digest_omitted", "mapping_digest_omitted"])
def test_v3_loader_rejects_malformed_lineage_envelope(monkeypatch, tmp_path: Path, mutation):
    from hashlib import sha256
    from vip_fvs.real_plan import (RealPlanSelection, build_real_edit_plan_from_selections_with_lineage,
                                   load_real_plan, save_real_plan)

    first = _bundle(f"-v3-load-{mutation}-1", f"rev-v3-load-{mutation}-1")
    second = _bundle(f"-v3-load-{mutation}-2", f"rev-v3-load-{mutation}-2")
    selections = [RealPlanSelection(first, _accept(first, decision_id=f"decision-v3-load-{mutation}-1"), timeline_start_ticks=0),
                  RealPlanSelection(second, _accept(second, decision_id=f"decision-v3-load-{mutation}-2"), timeline_start_ticks=40)]
    artifacts = build_real_edit_plan_from_selections_with_lineage(selections, plan_id=f"plan-v3-load-{mutation}", plan_revision=1)
    path = save_real_plan(artifacts, tmp_path / f"{mutation}.json")
    record = json.loads(path.read_text())
    if mutation == "unknown_lineage_key":
        record["lineage"][0]["unknown"] = True
    elif mutation == "bad_digest":
        record["lineage"][0]["review_bundle_record_digest"] = "A" * 64
    elif mutation == "duplicate":
        record["lineage"][1] = dict(record["lineage"][0])
    elif mutation == "omitted":
        record["lineage"].pop()
    elif mutation == "extra":
        record["lineage"].append(dict(record["lineage"][-1]))
    elif mutation == "reordered":
        record["lineage"].reverse()
    elif mutation == "unknown_version":
        record["schema_version"] = "vip_fvs.real_plan.v4"
    elif mutation == "unknown_envelope_key":
        record["extra"] = True
    elif mutation == "placement_omitted":
        record["placements"].pop()
    elif mutation == "mapping_omitted":
        record["mappings"].pop()
    elif mutation == "decision_omitted":
        record["projected_decisions"].pop()
    elif mutation == "placement_digest_omitted":
        record["placement_digests"].pop()
    elif mutation == "mapping_digest_omitted":
        record["mapping_digests"].pop()
    if mutation == "bad_record_digest":
        record["record_digest"] = "f" * 64
    else:
        preimage = {key: value for key, value in record.items() if key != "record_digest"}
        record["record_digest"] = sha256(json.dumps(preimage, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    path.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    with pytest.raises(ValueError):
        load_real_plan(path)


def test_multi_selection_refuses_same_track_overlap(monkeypatch):
    from vip_fvs.real_plan import RealPlanSelection, build_real_edit_plan_from_selections

    first = _bundle()
    second = _bundle("-overlap", "rev-overlap")
    with pytest.raises(ValueError, match="overlap"):
        build_real_edit_plan_from_selections([
            RealPlanSelection(first, _accept(first), timeline_start_ticks=0),
            RealPlanSelection(second, _accept(second, decision_id="decision-2"), timeline_start_ticks=20),
        ], plan_id="plan-overlap", plan_revision=1)


def test_multi_selection_sealed_readback_and_successor_use_fresh_decisions(monkeypatch, tmp_path):
    from vip_fvs.real_plan import (RealPlanSelection, build_real_edit_plan_from_selections,
                                   load_real_plan, save_real_plan)

    first = _bundle("-lineage-1", "rev-lineage-1")
    second = _bundle("-lineage-2", "rev-lineage-2")
    prior = build_real_edit_plan_from_selections([
        RealPlanSelection(first, _accept(first, decision_id="decision-lineage-1")),
    ], plan_id="plan-lineage", plan_revision=1)
    prior_path = save_real_plan(prior, tmp_path / "prior.json")
    assert load_real_plan(prior_path).plan_digest == prior.plan_digest

    successor = build_real_edit_plan_from_selections([
        RealPlanSelection(second, _accept(second, decision_id="decision-lineage-2", target_plan_revision=2)),
    ], plan_id="plan-lineage", plan_revision=2, prior_revision=prior.plan)
    assert successor.plan.supersedes == prior.plan.digest
    assert successor.plan.derived_from_refs == (prior.plan.digest,)
    assert successor.plan.source_revision_ids == ("rev-lineage-2",)
    assert set(successor.plan.pinned_decisions) == {"refinement-rev-lineage-2"}
    successor_path = save_real_plan(successor, tmp_path / "successor.json")
    assert load_real_plan(successor_path).plan_digest == successor.plan_digest
