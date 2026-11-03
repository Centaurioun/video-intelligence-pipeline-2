"""RED contract tests for the immutable real-source ReviewBundle."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from vip_fvs.review_bundle import ReviewBundle


ZERO = "0" * 64


def payload(**overrides):
    value = {
        "bundle_id": "bundle-1", "run_id": "run-1", "created_at": "2026-09-21T12:00:00Z",
        "review_status": "AWAITING_EDITORIAL_DECISION",
        "source": {"source_revision_id": "rev-1", "source_sha256": ZERO, "source_byte_count": 10,
                    "selected_stream_index": 0, "timebase": {"num": 1, "den": 1000},
                    "probe_artifact_ref": "probe-1", "probe_digest": ZERO},
        "authorization": {"discovery_policy_ref": "discover-1", "refinement_policy_ref": "refine-1",
                           "policy_digest": ZERO, "scope_digest": ZERO},
        "query": {"query_id": "query-1", "text": "target", "digest": ZERO},
        "generation": {"attempt_id": "attempt-1", "generation_id": "generation-1", "semantic_space_id": "space-1",
                        "model_identity": "model-1", "model_revision": "rev-a", "weights_digest": ZERO,
                        "processor_digest": ZERO, "index_ref": "index-1", "index_digest": ZERO, "input_digest": ZERO},
        "candidate": {"candidate_id": "candidate-1", "rank": 1, "score": 0.9, "evidence_class": "MATCHED",
                       "binding_eligible": False, "assertion_digest": ZERO,
                       "semantic_interval": {"start": 1.0, "end": 2.0, "time_domain": "semantic_seconds", "endpoint_semantics": "half_open"}},
        "refinement": {"refinement_id": "refinement-1", "status": "MEASURED", "source_revision_id": "rev-1",
                        "selected_stream_index": 0, "source_pts_interval": {"start": 40, "end": 80, "time_domain": "source_pts", "endpoint_semantics": "half_open"},
                        "timebase": {"num": 1, "den": 1000}, "attempt_id": "attempt-1", "evidence_artifact_ref": "evidence-1",
                        "evidence_digest": ZERO, "evidence_class": "MEASURED"},
        "presentation": {"display_only": True, "start_seconds": 0.04, "end_seconds": 0.08},
        "dependency_digest": ZERO, "decision": None,
    }
    value.update(overrides)
    return value


def payload_with_e01_artifact(tmp_path: Path):
    import hashlib

    from tests.vip_fvs.unit.test_real_source_temporal_authority import _refine_named_source, _valid_refinement_request_identity

    refinement, source = _refine_named_source(tmp_path / "e01-source", _valid_refinement_request_identity())
    artifact = tmp_path / "refinement.json"
    artifact.write_text(json.dumps(refinement, sort_keys=True, separators=(",", ":")) + "\n")
    value = payload()
    value["source"].update({"source_revision_id": refinement["source_revision_id"],
                            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                            "source_byte_count": source.stat().st_size,
                            "selected_stream_index": refinement["stream_index"],
                            "timebase": refinement["time_base"]})
    value["generation"]["attempt_id"] = refinement["attempt_id"]
    value["refinement"].update({"refinement_id": refinement["refinement_id"],
                                "source_revision_id": refinement["source_revision_id"],
                                "selected_stream_index": refinement["stream_index"],
                                "source_pts_interval": {"start": refinement["start_ticks"], "end": refinement["end_ticks"],
                                                        "time_domain": "source_pts", "endpoint_semantics": "half_open"},
                                "timebase": refinement["time_base"], "attempt_id": refinement["attempt_id"],
                                "evidence_artifact_ref": str(artifact), "evidence_digest": refinement["evidence_digest"]})
    return value


def test_create_emits_closed_five_field_record_and_awaits_editorial_decision(tmp_path: Path):
    bundle = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    record = bundle.to_record()
    assert set(record) == {"record_id", "record_type", "record_schema_version", "record_digest", "payload"}
    assert record["payload"]["review_status"] == "AWAITING_EDITORIAL_DECISION"
    assert record["payload"]["decision"] is None
    assert bundle.record_digest == record["record_digest"]


def test_new_records_use_v2_and_round_trip_without_losing_request_identity(tmp_path: Path):
    bundle = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    assert bundle.to_record()["record_schema_version"] == "vip_fvs.review_bundle.v2"
    assert ReviewBundle.from_record(bundle.to_record()).to_record() == bundle.to_record()
    import jsonschema
    schema = json.loads(Path("schemas/vip_fvs/review_bundle.v2.json").read_text())
    jsonschema.validate(bundle.to_record(), schema)


def test_new_bundle_refuses_missing_or_unresolved_request_provenance():
    with pytest.raises(ValueError, match="persisted E01 refinement artifact"):
        ReviewBundle.create(payload(), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")


@pytest.mark.parametrize("timebase", [{"num": 2, "den": 50}, {"num": 1, "den": 50}, {"num": True, "den": 25}])
def test_v2_rejects_noncanonical_or_unmeasured_timebase(tmp_path: Path, timebase):
    value = payload_with_e01_artifact(tmp_path)
    value["source"]["timebase"] = timebase
    with pytest.raises(ValueError):
        ReviewBundle.create(value, run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")


def test_historical_v1_envelope_digest_and_dependency_digest_remain_unchanged():
    from vip_fvs.review_bundle import record_digest

    legacy_payload = payload()
    legacy_payload["dependency_digest"] = "ad8bf3120b24de0488f2ee977650b5a71d1aed6560499655ae12dbaf646d3041"
    legacy = {"record_id": "bundle-1", "record_type": "vip_fvs.review_bundle",
              "record_schema_version": "vip_fvs.review_bundle.v1", "record_digest": "",
              "payload": legacy_payload}
    legacy["record_digest"] = record_digest(legacy)
    assert legacy["record_digest"] == "ab35db6e57bbaf44ce85609d91e6061cc6d4a3609bcd89c23c359cc1a812b4da"
    assert ReviewBundle.from_record(legacy).to_record() == legacy


def test_record_digest_changes_for_any_retained_payload_field(tmp_path: Path):
    original = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    changed = original.payload; changed["presentation"]["start_seconds"] = 9.0
    replacement = ReviewBundle.create(changed, run_id="run-1", bundle_id="bundle-2", created_at="2026-09-21T12:00:00Z")
    assert replacement.record_digest != original.record_digest


@pytest.mark.parametrize("path", [
    ("source", "source_sha256"), ("source", "probe_digest"), ("authorization", "policy_digest"),
    ("query", "digest"), ("generation", "model_identity"), ("generation", "processor_digest"),
    ("generation", "index_digest"), ("candidate", "assertion_digest"), ("refinement", "evidence_digest"),
])
def test_dependency_digest_changes_for_each_load_bearing_dependency(path, tmp_path: Path):
    from vip_fvs.review_bundle import dependency_digest
    original = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    changed = original.payload
    changed[path[0]][path[1]] = "1" * 64 if "digest" in path[1] or path[1].endswith("sha256") else "changed"
    if path == ("source", "source_sha256"):
        identity = changed["refinement"]["request_identity"]
        identity["request"]["expected_source_sha256"] = "1" * 64
        identity["request_digest"] = __import__("hashlib").sha256(json.dumps(identity["request"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    assert dependency_digest(changed) != original.dependency_digest


def test_dependency_digest_excludes_locator_display_creation_and_host_metadata(tmp_path: Path):
    original = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    changed = original.payload; changed["presentation"]["start_seconds"] = 8.0; changed["created_at"] = "different"; changed["source"]["probe_artifact_ref"] = "other"
    replacement = ReviewBundle.create(changed, run_id="run-2", bundle_id="bundle-2", created_at="different")
    assert replacement.dependency_digest == original.dependency_digest


def test_dependency_change_never_reuses_sealed_bundle(tmp_path: Path):
    bundle = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    path = tmp_path / "review-bundle.json"
    from vip_fvs.review_bundle import find_sealed_bundle, save_review_bundle
    save_review_bundle(bundle, path)
    assert find_sealed_bundle(tmp_path, bundle.dependency_digest).record_digest == bundle.record_digest
    assert find_sealed_bundle(tmp_path, "1" * 64) is None


def test_persisted_refinement_artifact_mints_v2_identity_and_byte_authority(tmp_path: Path):
    """The bundle layer must derive request identity from its persisted E01 artifact."""
    import hashlib
    import json

    from gate3.refinement import is_binding_eligible
    from tests.vip_fvs.unit.test_real_source_temporal_authority import _refine_named_source, _valid_refinement_request_identity

    refinement, source_path = _refine_named_source(tmp_path / "source", _valid_refinement_request_identity())
    artifact_path = tmp_path / "refinement.json"
    artifact_path.write_text(json.dumps(refinement, sort_keys=True, separators=(",", ":")) + "\n")
    value = payload()
    value["source"].update({
        "source_revision_id": refinement["source_revision_id"],
        "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "source_byte_count": source_path.stat().st_size,
        "selected_stream_index": refinement["stream_index"],
        "timebase": refinement["time_base"],
    })
    value["generation"]["attempt_id"] = refinement["attempt_id"]
    value["refinement"].update({
        "refinement_id": refinement["refinement_id"],
        "source_revision_id": refinement["source_revision_id"],
        "selected_stream_index": refinement["stream_index"],
        "source_pts_interval": {"start": refinement["start_ticks"], "end": refinement["end_ticks"],
                                "time_domain": "source_pts", "endpoint_semantics": "half_open"},
        "timebase": refinement["time_base"],
        "attempt_id": refinement["attempt_id"],
        "evidence_artifact_ref": str(artifact_path),
        "evidence_digest": refinement["evidence_digest"],
    })

    bundle = ReviewBundle.create(value, run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")

    assert bundle.to_record()["record_schema_version"] == "vip_fvs.review_bundle.v2"
    assert bundle.payload["refinement"]["request_identity"] == refinement["validation_results"][-1].get("request_identity") or bundle.payload["refinement"]["request_identity"] == next(item["request_identity"] for item in refinement["validation_results"] if item.get("check") == "C2_named_byte_binding")
    assert is_binding_eligible(refinement)


def test_v2_dependency_digest_changes_when_request_identity_changes(tmp_path: Path):
    import hashlib

    from tests.vip_fvs.unit.test_real_source_temporal_authority import _refine_named_source, _valid_refinement_request_identity
    from vip_fvs.review_bundle import dependency_digest

    refinement, source_path = _refine_named_source(tmp_path / "source", _valid_refinement_request_identity())
    artifact_path = tmp_path / "refinement.json"
    artifact_path.write_text(json.dumps(refinement, sort_keys=True, separators=(",", ":")) + "\n")
    value = payload()
    value["source"].update({"source_revision_id": refinement["source_revision_id"],
                            "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                            "source_byte_count": source_path.stat().st_size,
                            "selected_stream_index": refinement["stream_index"], "timebase": refinement["time_base"]})
    value["generation"]["attempt_id"] = refinement["attempt_id"]
    value["refinement"].update({"refinement_id": refinement["refinement_id"],
                                "source_revision_id": refinement["source_revision_id"],
                                "selected_stream_index": refinement["stream_index"],
                                "source_pts_interval": {"start": refinement["start_ticks"], "end": refinement["end_ticks"], "time_domain": "source_pts", "endpoint_semantics": "half_open"},
                                "timebase": refinement["time_base"], "attempt_id": refinement["attempt_id"],
                                "evidence_artifact_ref": str(artifact_path), "evidence_digest": refinement["evidence_digest"]})
    original = ReviewBundle.create(value, run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z").payload
    changed = copy.deepcopy(original)
    identity = changed["refinement"]["request_identity"]
    identity["request_id"] = identity["request"]["request_id"] = "different-request"
    identity["request_digest"] = hashlib.sha256(json.dumps(identity["request"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

    assert dependency_digest(changed) != dependency_digest(original)
