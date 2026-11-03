import math
import struct

import pytest

from gate0.adapters.embedding import FakeEmbeddingAdapter, EmbeddingResult, normalize_vector
from gate0.arms.metadata import metadata_tokens, token_set_jaccard
from gate0.arms.semantic import RepresentationRecord, embed_windows
from gate0.temporal import Rational, SampleTarget


def test_metadata_tokenization_is_casefolded_and_unicode_aware():
    assert metadata_tokens("Ä CAT-01", "Clip.MP4", "Parent Dir") == {
        "ä", "cat", "01", "clip", "mp4", "parent", "dir"
    }
    assert token_set_jaccard({"cat", "dog"}, {"cat", "bird"}) == pytest.approx(1 / 3)
    assert metadata_tokens("", "clip_name", "parent_dir") == {"clip", "name", "parent", "dir"}


def test_normalize_vector_rejects_zero_and_nonfinite_vectors():
    with pytest.raises(ValueError, match="ZERO_VECTOR"):
        normalize_vector((0.0, 0.0))
    with pytest.raises(ValueError, match="NON_FINITE"):
        normalize_vector((1.0, math.nan))


def test_fake_embedding_is_local_and_never_falls_back_to_provider():
    adapter = FakeEmbeddingAdapter({"pixels": (3.0, 4.0), "text": (1.0, 0.0)})
    assert adapter.embed("pixels", b"frame").vector == (3.0, 4.0)
    assert adapter.embed("text", "query").vector == (1.0, 0.0)
    assert adapter.provider_calls == 0


def test_semantic_pooling_is_target_tick_ordered_and_digest_is_float64_le():
    rows = (
        SampleTarget("t1", "w", "i", 1, Rational(1, 2), None, None, "VALID", "SUCCEEDED", "f1"),
        SampleTarget("t0", "w", "i", 0, Rational(0, 1), None, None, "VALID", "SUCCEEDED", "f0"),
    )
    adapter = FakeEmbeddingAdapter({b"f0": (1.0, 0.0), b"f1": (0.0, 1.0)})
    records = embed_windows(rows, adapter, pixels_by_frame={"f0": b"f0", "f1": b"f1"},
                            revision_id="rev", sampling_manifest_digest="a" * 64,
                            generation_attempt_id="attempt_1")
    record = records[0]
    assert record.representation_status == "SUCCEEDED"
    assert record.vector_length == 2
    assert record.vector_encoding == "float64_le_row_major"
    expected = __import__("hashlib").sha256(struct.pack("<2d", 1 / math.sqrt(2), 1 / math.sqrt(2))).hexdigest()
    assert record.vector_digest == expected


def test_semantic_normalizes_each_frame_before_pooling():
    rows = (
        SampleTarget("t0", "w", "i", 0, Rational(0, 1), None, None, "VALID", "SUCCEEDED", "f0"),
        SampleTarget("t1", "w", "i", 1, Rational(1, 2), None, None, "VALID", "SUCCEEDED", "f1"),
    )
    adapter = FakeEmbeddingAdapter({b"f0": (10.0, 0.0), b"f1": (0.0, 1.0)})
    record = embed_windows(rows, adapter, pixels_by_frame={"f0": b"f0", "f1": b"f1"},
                           revision_id="rev", sampling_manifest_digest="a" * 64,
                           generation_attempt_id="attempt_1")[0]
    expected = __import__("hashlib").sha256(struct.pack("<2d", 1 / math.sqrt(2), 1 / math.sqrt(2))).hexdigest()
    assert record.vector_digest == expected


def test_missing_pixels_are_explicit_status_rows_without_fake_fallback():
    rows = (SampleTarget("t0", "w", "i", 0, Rational(0, 1), None, None, "VALID", "SUCCEEDED", "f0"),)
    adapter = FakeEmbeddingAdapter({"pixels": (1.0, 0.0)})
    record = embed_windows(rows, adapter, pixels_by_frame={}, revision_id="rev",
                           sampling_manifest_digest="a" * 64, generation_attempt_id="attempt_1")[0]
    assert record.representation_status == "FAILED"
    assert record.failure_reason == "MISSING_PIXELS"
    assert record.vector_digest is None


def test_failed_embedding_is_status_only_without_vector_digest():
    rows = (SampleTarget("t0", "w", "i", 0, Rational(0, 1), None, None, "VALID", "SUCCEEDED", "f0"),)
    adapter = FakeEmbeddingAdapter({"pixels": (0.0, 0.0)})
    record = embed_windows(rows, adapter, pixels_by_frame={"f0": b"f0"}, revision_id="rev",
                           sampling_manifest_digest="a" * 64, generation_attempt_id="attempt_1")[0]
    assert record.representation_status == "FAILED"
    assert record.vector_digest is None
    assert record.failure_reason == "ZERO_VECTOR"
