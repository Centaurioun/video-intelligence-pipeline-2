"""Adversarial identity checks for the local semantic representation arm.

These tests exercise the seams where a replay can look numerically valid while
actually belonging to a different model generation.  A representation must
never be reused merely because its vector dimension (or its source/window) is
unchanged; the semantic coordinate domain must also remain distinct from
source-native timing.
"""
from __future__ import annotations

import pytest

from gate0.adapters.embedding import FakeEmbeddingAdapter
from gate0.arms.semantic import embed_windows
from gate0.temporal import Rational, SampleTarget
from gate3.ingress import validate_candidate


def _rows() -> tuple[SampleTarget, ...]:
    return (
        SampleTarget("target_0", "window_0", "interval_0", 0, Rational(0, 1),
                     None, None, "VALID", "SUCCEEDED", "frame_0"),
    )


def _record(*, model: str = "weights-a", processor: str = "a" * 64,
            preprocessing: str = "b" * 64, sampling: str = "c" * 64,
            attempt: str = "attempt-1"):
    return embed_windows(
        _rows(), FakeEmbeddingAdapter({b"pixels": (1.0, 0.0)}),
        pixels_by_frame={"frame_0": b"pixels"}, revision_id="revision-1",
        sampling_manifest_digest=sampling, generation_attempt_id=attempt,
        model_identity=model, processor_digest=processor,
        preprocessing_digest=preprocessing,
    )[0]


@pytest.mark.parametrize(
    ("field", "left", "right"),
    [
        ("model", "weights-a", "weights-b"),
        ("processor", "a" * 64, "d" * 64),
        ("preprocessing", "b" * 64, "e" * 64),
        ("sampling", "c" * 64, "f" * 64),
    ],
)
def test_identity_changes_for_every_semantic_generation_input(field, left, right):
    kwargs = {"model": "weights-a", "processor": "a" * 64,
              "preprocessing": "b" * 64, "sampling": "c" * 64}
    kwargs[field] = left
    first = _record(**kwargs)
    kwargs[field] = right
    second = _record(**kwargs)

    assert first.representation_status == second.representation_status == "SUCCEEDED"
    assert first.representation_id != second.representation_id, (
        f"changing {field} must not alias the same representation identity"
    )


def test_incompatible_generation_cannot_alias_even_when_vectors_match():
    first = _record(attempt="generation-1", model="weights-a")
    second = _record(attempt="generation-2", model="weights-a")
    assert first.vector_digest == second.vector_digest
    assert first.representation_id != second.representation_id
    assert first.generation_attempt_id != second.generation_attempt_id


def _semantic_candidate(**overrides):
    candidate = {
        "assertion_id": "assertion-1", "source_revision_id": "revision-1",
        "interval_id": "interval-1", "stream_index": 0,
        "time_domain": "semantic_seconds", "origin_description": "semantic locator",
        "start": 40, "end": 80, "endpoint_semantics": "half_open",
        "evidence_assertion_refs": [], "producer_attempt_id": "attempt-1",
        "evidence_class": "MATCHED", "producer_kind": "model",
        "invocation_ref": "invocation-1", "precision": "semantic-window",
        "uncertainty": "unknown", "assertion_status": "ACTIVE",
        "refinement_eligibility": "NOT_ELIGIBLE", "binding_eligible": False,
    }
    candidate.update(overrides)
    return candidate


def test_semantic_seconds_remains_typed_when_numbers_resemble_source_ticks():
    result = validate_candidate(_semantic_candidate())
    assert result["disposition"] == "ADMITTED"
    assert result["record"]["time_domain"] == "semantic_seconds"
    assert result["record"]["binding_eligible"] is False
    assert result["record"]["refinement_eligibility"] == "NOT_ELIGIBLE"


def test_semantic_timestamp_cannot_be_smuggled_as_fractional_source_coordinate():
    result = validate_candidate(_semantic_candidate(start=40.0, end=80.0))
    assert result["disposition"] == "REJECTED"
    assert "INTERVAL_ENDPOINTS_NOT_INTEGERS" in result["reason_codes"]


def test_source_pts_claim_requires_typed_deterministic_provenance():
    result = validate_candidate(_semantic_candidate(
        time_domain="source_pts", precision="source-pts",
        refinement_eligibility="ELIGIBLE", binding_eligible=False,
    ))
    assert result["disposition"] == "DOWNGRADED"
    assert result["record"]["time_domain"] == "semantic_seconds"
    assert result["record"]["precision"] == "semantic-window"
