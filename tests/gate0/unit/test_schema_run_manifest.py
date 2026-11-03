"""Closed-schema contract tests for ``schemas/gate0/run_manifest.json`` (D5).

Authority: ``docs/implementation-spec-v1.1.md`` §3:83 (run manifest names frozen
inputs/config/policies, thresholds, attempts, invocation summaries, stage
transitions, artifact digests, status projection, stop reason), §6:38
(CANONICAL_CONTRACTS: a run manifest names exact input revisions, query/gold
versions, policy decisions, profiles/configuration digests, tool/runtime
observations, attempts and output artifact digests), §9.1 envelope identity;
``contract-owner-proposal.md`` D5.  Extension projections are enumerated
explicitly and stay optional; unknown keys are refused (no blanket
``additionalProperties`` escape).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from gate0.contracts.types import ARTIFACT_TYPES

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "schemas/gate0/run_manifest.json").read_text(encoding="utf-8"))

D = "0" * 64


def _validator(subschema: dict) -> Draft202012Validator:
    root = {"$defs": SCHEMA["$defs"]}
    root.update(subschema)
    return Draft202012Validator(root)


def _sub(pointer: str) -> Draft202012Validator:
    return _validator({"$ref": pointer})


TOOL = {
    "role": "ffprobe",
    "executable": "ffprobe",
    "version": "9.0.2",
    "configuration": "-show_frames",
    "version_stdout_digest": "1" * 64,
    "identity_digest": "2" * 64,
}

MEASUREMENT = {
    "revision_id": "rev_dev_probe",
    "source_kind": "LOCAL_GENERATED_MEDIA",
    "evidence_class": "MEASURED",
    "locator": "media/dev_cfr_25.mp4",
    "source_byte_count": 1024,
    "source_digest": "3" * 64,
    "probe_ref": "probe_rev_dev_probe",
    "probe_raw_output_digest": "4" * 64,
    "selected_stream_index": 0,
    "selection_source": "declared",
    "time_base": {"numerator": 1, "denominator": 12800},
    "origin_pts_ticks": 0,
    "presentation_pts_ticks_first": None,
    "presentation_pts_ticks_last": None,
    "frame_count": 4,
    "decoded_frame_count": 4,
    "window_count": 1,
    "measured_duration": {"numerator": 4, "denominator": 1},
    "probe_tool": TOOL,
    "frame_evidence_tool": TOOL,
}

MEDIA_TOOLS = {
    "ffmpeg": TOOL,
    "ffmpeg_used_for_sampling": False,
    "ffprobe": TOOL,
    "frame_evidence": TOOL,
}

METRIC_IDS = (
    "absent_query_diagnostic.metadata",
    "absent_query_diagnostic.semantic",
    "family_hit_at_10.metadata.appearance",
    "family_hit_at_10.metadata.interaction",
    "family_hit_at_10.metadata.scene_composition_camera_movement",
    "family_hit_at_10.metadata.visible_action",
    "family_hit_at_10.semantic.appearance",
    "family_hit_at_10.semantic.interaction",
    "family_hit_at_10.semantic.scene_composition_camera_movement",
    "family_hit_at_10.semantic.visible_action",
    "hit_at_10.metadata",
    "hit_at_10.semantic",
    "paired_lift.semantic_minus_metadata",
)

ENVELOPE = {
    "artifact_id": "artifact_source",
    "artifact_type": "source_manifest.json",
    "schema_version": "gate0.v1",
    "digest_algorithm": "SHA-256",
    "payload_digest": D,
    "producer_attempt_id": "attempt_report",
    "input_artifact_refs": [{
        "artifact_id": "artifact_sample",
        "payload_digest": D,
        "artifact_type": "window_sample_manifest.jsonl",
    }],
    "policy_decision_id": "policy_a",
    "retention_class": "SOURCE_REFERENCE",
    "availability_status": "AVAILABLE",
    "created_at": "2026-01-01T00:00:00Z",
}

REPRESENTATION = {
    "space_id": "semantic_visual",
    "representation_id": "representation_abc",
    "revision_id": "rev_dev_probe",
    "window_id": "rev_dev_probe_window_0",
    "sampling_manifest_digest": D,
    "model_identity": "SYNTHETIC_FAKE_EMBEDDER_V1",
    "processor_digest": D,
    "preprocessing_digest": D,
    "pooling": "MEAN_TARGET_SLOTS",
    "dimension": 8,
    "dtype": "float64",
    "normalization": "L2",
    "metric": "COSINE",
    "generation_attempt_id": "attempt_embed",
    "representation_status": "SUCCEEDED",
    "vector_digest": D,
    "vector_digest_algorithm": "SHA-256",
    "vector_encoding": "float64_le_row_major",
    "vector_length": 8,
    "accumulation_order": "target_tick_ascending_serial",
}

BLINDING = {
    "mapping_version": "gate0-blind-v1",
    "blind_mapping_digest": D,
    "token_map": [
        {"blind_arm_token": "arm_a", "arm_id": "metadata-floor"},
        {"blind_arm_token": "arm_b", "arm_id": "offline-development-arm"},
    ],
    "reviewer_count": 2,
    "reviewer_visible_fields": ["blind_arm_token"],
    "reviewer_hidden_fields": ["arm_id"],
    "access_scope": "T08_only",
}

ARMS = [
    {"arm_id": "metadata-floor", "representation_kind": "metadata_floor"},
    {"arm_id": "offline-development-arm", "representation_kind": "embedding"},
]

#: Every extension key the executable producer actually projects onto the
#: frozen manifest document.  These are modelled explicitly and stay optional.
EXTENSIONS = {
    "spec_digest": "1" * 64,
    "evidence_class": "MEASURED",
    "corpus_kind": "generated_synthetic_media_not_experiment_evidence",
    "evidence_class_boundary": {
        "media_sampling": "MEASURED",
        "embedding": "SYNTHETIC_FIXTURE",
        "ground_truth": "SYNTHETIC_FIXTURE",
        "experiment_result": "NOT_OBSERVED",
    },
    "synthetic_input": {
        "corpus": "media-corpus.json",
        "labels": "labels.json",
        "query_vectors": "query-vectors.json",
    },
    "selected_streams": [
        {"revision_id": "rev_dev_probe", "stream_index": 0, "selection_source": "declared"},
    ],
    "stage_inputs": {
        "prepare": ["media-corpus.json", "labels.json", "query-vectors.json"],
        "rank": ["media-corpus.json", "query-vectors.json"],
        "evaluate": ["labels.json"],
    },
    "label_isolation": {
        "ranker_inputs": ["media-corpus.json", "query-vectors.json", "queries.jsonl"],
        "ranker_excludes": ["labels.json", "gold_events.jsonl", "window_judgments.jsonl"],
    },
    "host_sandbox_observation": "NOT_OBSERVED",
    "sandbox_observation_source": "config_bound_synthetic_fixture",
    "inventory_digest": "2" * 64,
    "media_measurements": [MEASUREMENT],
    "media_tools": MEDIA_TOOLS,
    "media_measurement_origin": "LOCAL_GENERATED_MEDIA_NOT_AUTHORIZED_CORPUS",
    "split_version": "split-v1",
    "split_digest": "3" * 64,
    "query_version": "queries-synthetic-v1",
    "label_version": "4" * 64,
    "query_version_digest": "5" * 64,
    "gold_version_digest": "6" * 64,
    "sample_manifest_digest": "7" * 64,
    "target_counts": {"failed": 0, "omitted": 0, "planned": 4, "quarantined": 0, "succeeded": 4},
    "windows": [{
        "end": {"numerator": 4, "denominator": 1},
        "mapping_ref": "rev_dev_probe_map_0_0_000000",
        "origin": {"numerator": 0, "denominator": 1},
        "revision_id": "rev_dev_probe",
        "start": {"numerator": 0, "denominator": 1},
        "time_base": {"numerator": 1, "denominator": 12800},
        "window_id": "rev_dev_probe_window_0",
        "window_index": 0,
    }],
    "representation_digests": ["8" * 64],
    "ranking_digest": "9" * 64,
    "baseline_digest": "a" * 64,
    "metrics_digest": "b" * 64,
    "judgments_digest": "c" * 64,
    "replay_comparison": {
        "status": "EQUAL",
        "first_difference": None,
        "differences": [],
        "full_pipeline": {
            "sample_manifest_digest": "7" * 64,
            "representation_digests": ["8" * 64],
            "ranking_digest": "9" * 64,
            "baseline_digest": "a" * 64,
        },
        "frozen_index_equal": True,
    },
    "review_input": {"path": "/authorized/review-input/review.json", "digest": "d" * 64},
    "metric_snapshot": {key: {"numerator": 0, "denominator": 1} for key in METRIC_IDS},
    "threshold_digest": "e" * 64,
    "run_decision": {
        "benchmark_status": "NOT_RUN",
        "gate_decision": "NOT_RUN",
        "stop_reason": "NOT_RUN",
        "stop_reason_detail": "GENERATED_MEDIA_NOT_AUTHORIZED_CORPUS",
    },
    "frozen_input": {
        "source_revision_ids": ["rev_dev_probe"],
        "sample_manifest_digest": "7" * 64,
        "representation_digests": ["8" * 64],
        "ranking_digest": "9" * 64,
        "metrics_digest": "b" * 64,
        "config_digest": D,
    },
    "frozen_input_digests": {"frozen-index": "f" * 64, "full-pipeline": "1" * 64},
    "model_processor_digest": D,
    "arms": ARMS,
}

BASE = {
    "schema_version": "gate0.run_manifest.v1",
    "run_id": "run_media_e2e",
    "gate_owner_id": "gate_owner_local",
    "source_revision_ids": ["rev_dev_probe"],
    "config_digest": D,
    "dependency_lock_digest": D,
    "policy_decision_ids": ["policy_a", "policy_b"],
    "thresholds": {
        "semantic_hit_at_10_num": 20,
        "semantic_hit_at_10_den": 24,
        "paired_lift_num": 5,
        "paired_lift_den": 24,
        "family_hit_at_10_num": 3,
        "family_hit_at_10_den": 6,
    },
    "runtime": {
        "python_version": "3.11.9",
        "os_release_digest": D,
        "runtime_executable_digest": D,
        "dependency_lock_digest": D,
        "config_digest": D,
        "blas_thread_control_digest": D,
        "tool_environment_digest": D,
    },
    "sandbox": {
        "bwrap_path": "/usr/bin/bwrap",
        "bwrap_version": "0.8.0",
        "bwrap_digest": D,
        "interpreter_path": "/usr/bin/python3",
        "interpreter_version": "3.11.9",
        "interpreter_digest": D,
        "read_only_mounts": [],
        "writable_mounts": [],
        "clearenv": True,
        "net_unshared": True,
        "argv_digest": D,
        "mount_policy_digest": D,
        "child_network_sentinel": True,
    },
    "invocations": [],
    "blinding": BLINDING,
    "stage_transitions": [],
    "attempts": [],
    "artifact_envelopes": [ENVELOPE],
    "representations": [REPRESENTATION],
    "repeat_comparisons": [],
    "status": "REPORTED",
}


def _manifest(**overrides: object) -> dict:
    manifest = {**BASE, **EXTENSIONS, **{key: value for key, value in overrides.items()}}
    return manifest


def _assert_valid(value: dict) -> None:
    Draft202012Validator(SCHEMA).validate(value)


def _assert_invalid(value: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(SCHEMA).validate(value)


def test_top_level_required_surface_is_pinned_and_extensions_are_optional() -> None:
    assert set(SCHEMA["required"]) == {
        "schema_version", "run_id", "gate_owner_id", "source_revision_ids",
        "config_digest", "dependency_lock_digest", "policy_decision_ids",
        "thresholds", "runtime", "sandbox", "invocations", "blinding",
        "stage_transitions", "attempts", "artifact_envelopes",
        "representations", "repeat_comparisons", "status",
    }
    assert SCHEMA["additionalProperties"] is False
    assert len(EXTENSIONS) == 37, "every produced extension projection must be documented"
    assert set(EXTENSIONS) == set(SCHEMA["properties"]) - set(SCHEMA["required"]) - {"stop_reason"}
    assert not (set(EXTENSIONS) & set(SCHEMA["required"]))


def test_observed_manifest_with_documented_extension_keys_validates() -> None:
    _assert_valid(_manifest())


def test_unknown_extension_key_is_refused() -> None:
    _assert_invalid(_manifest(undocumented_projection={"anything": True}))
    _assert_invalid(_manifest(custom_note="x"))


def test_artifact_type_vocabulary_is_exactly_thirteen_registered_filenames() -> None:
    for pointer in ("#/$defs/envelope/properties/artifact_type", "#/$defs/ref/properties/artifact_type"):
        node: object = SCHEMA
        for part in pointer[2:].split("/"):
            node = node[part]  # type: ignore[index]
        assert tuple(node["enum"]) == ARTIFACT_TYPES
        assert len(node["enum"]) == 13
    for name in ARTIFACT_TYPES:
        _assert_valid(_manifest(artifact_envelopes=[{**ENVELOPE, "artifact_type": name}]))
    _assert_invalid(_manifest(artifact_envelopes=[{**ENVELOPE, "artifact_type": "run_manifest"}]))
    _assert_invalid(_manifest(artifact_envelopes=[{
        **ENVELOPE,
        "input_artifact_refs": [{**ENVELOPE["input_artifact_refs"][0], "artifact_type": "summary.md"}],
    }]))


def test_arms_registry_is_an_optional_closed_two_field_shape() -> None:
    """D8: closed per-run arm registry; the 18-key required set is unchanged."""
    assert "arms" not in SCHEMA["required"]
    validator = _sub("#/$defs/arm")
    validator.validate(ARMS[0])
    validator.validate(ARMS[1])
    with pytest.raises(ValidationError):
        validator.validate({"arm_id": "metadata-floor", "representation_kind": "METADATA"})
    with pytest.raises(ValidationError):
        validator.validate({"arm_id": "metadata-floor"})
    with pytest.raises(ValidationError):
        validator.validate({"arm_id": "metadata-floor", "representation_kind": "embedding", "note": "x"})
    with pytest.raises(ValidationError):
        validator.validate({"arm_id": "METADATA-FLOOR", "representation_kind": "metadata_floor"})
    array_validator = _validator({**SCHEMA["properties"]["arms"], "$defs": SCHEMA["$defs"]})
    array_validator.validate(ARMS)
    with pytest.raises(ValidationError):
        array_validator.validate([])
    with pytest.raises(ValidationError):
        array_validator.validate([ARMS[0], ARMS[0]])
    with pytest.raises(ValidationError):
        array_validator.validate([{"arm_id": "a", "representation_kind": "unknown"}])
    _assert_valid(_manifest())
    without_arms = _manifest()
    without_arms.pop("arms")
    _assert_valid(without_arms)
    _assert_invalid(_manifest(arms=[ARMS[0], ARMS[0]]))


def test_blinding_reviewer_ids_is_an_optional_unique_id_array() -> None:
    validator = _sub("#/$defs/blinding")
    validator.validate(BLINDING)
    validator.validate({**BLINDING, "reviewer_ids": ["reviewer_a", "reviewer_b"]})
    with pytest.raises(ValidationError):
        validator.validate({**BLINDING, "reviewer_ids": ["reviewer_a", "reviewer_a"]})
    with pytest.raises(ValidationError):
        validator.validate({**BLINDING, "reviewer_ids": ["REVIEWER_A"]})
    with pytest.raises(ValidationError):
        validator.validate({**BLINDING, "access_scope": "T09_only"})


def test_representation_vocabulary_matches_the_frozen_authority() -> None:
    properties = SCHEMA["$defs"]["representation"]["properties"]
    assert properties["pooling"]["enum"] == ["MEAN_TARGET_SLOTS"]
    assert properties["normalization"]["enum"] == ["L2"]
    assert properties["metric"]["enum"] == ["COSINE"]
    assert properties["representation_status"]["enum"] == [
        "SUCCEEDED", "FAILED", "ZERO_VECTOR", "NON_FINITE",
    ]
    _sub("#/$defs/representation").validate(REPRESENTATION)
    failed = {key: value for key, value in REPRESENTATION.items()
              if key not in {"vector_digest", "vector_digest_algorithm", "vector_encoding",
                             "vector_length", "accumulation_order"}}
    failed.update(representation_status="ZERO_VECTOR", failure_reason="ZERO_VECTOR")
    _sub("#/$defs/representation").validate(failed)
    with pytest.raises(ValidationError):
        _sub("#/$defs/representation").validate({**REPRESENTATION, "pooling": "mean"})


def test_media_measurement_shape_is_closed_and_allows_missing_pts() -> None:
    validator = _sub("#/$defs/media_measurement")
    validator.validate(MEASUREMENT)
    validator.validate({**MEASUREMENT, "presentation_pts_ticks_first": 0, "presentation_pts_ticks_last": 3})
    with pytest.raises(ValidationError):
        validator.validate({**MEASUREMENT, "unexpected_probe": True})
    with pytest.raises(ValidationError):
        validator.validate({**MEASUREMENT, "evidence_class": "SYNTHETIC_FIXTURE"})


def test_media_tools_require_observed_probe_identity() -> None:
    validator = _sub("#/$defs/media_tools")
    validator.validate(MEDIA_TOOLS)
    validator.validate({**MEDIA_TOOLS, "ffprobe": None, "frame_evidence": None})
    validator.validate({
        **MEDIA_TOOLS,
        "ffmpeg": {"role": "ffmpeg", "executable": "ffmpeg", "status": "NOT_OBSERVED", "detail": "missing"},
    })
    with pytest.raises(ValidationError):
        validator.validate({key: value for key, value in MEDIA_TOOLS.items() if key != "ffprobe"})
    with pytest.raises(ValidationError):
        validator.validate({**MEDIA_TOOLS, "ffmpeg": {"role": "ffmpeg", "executable": "ffmpeg", "status": "MAYBE"}})
    with pytest.raises(ValidationError):
        validator.validate({**MEDIA_TOOLS, "ffmpeg_used_for_sampling": True})


def test_frozen_input_digests_is_a_closed_two_mode_map() -> None:
    validator = _sub("#/$defs/frozen_input_digests")
    validator.validate(EXTENSIONS["frozen_input_digests"])
    with pytest.raises(ValidationError):
        validator.validate({**EXTENSIONS["frozen_input_digests"], "third-mode": D})
    with pytest.raises(ValidationError):
        validator.validate({"frozen-index": D})


def test_metric_snapshot_is_a_closed_metric_rational_map() -> None:
    validator = _sub("#/$defs/metric_snapshot")
    validator.validate(EXTENSIONS["metric_snapshot"])
    with pytest.raises(ValidationError):
        validator.validate({**EXTENSIONS["metric_snapshot"], "invented.metric": {"numerator": 0, "denominator": 1}})
    with pytest.raises(ValidationError):
        validator.validate({key: value for key, value in EXTENSIONS["metric_snapshot"].items() if key != "hit_at_10.semantic"})
