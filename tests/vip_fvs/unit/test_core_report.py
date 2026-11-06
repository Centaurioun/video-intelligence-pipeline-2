"""Unit tests for QUERY_DRIVEN_SEMANTIC_REPORT_V1 schema, validation, and atomic publication."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

try:
    import pytest
except ImportError:  # pragma: no cover

    class _RaisesContext:
        def __init__(self, exc_type):
            self.exc_type = exc_type
            self.value = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, _tb):
            if exc_type is None:
                raise AssertionError(
                    f"Expected {self.exc_type}, but no exception was raised"
                )
            if not issubclass(exc_type, self.exc_type):
                return False
            self.value = exc_val
            return True

    class _PytestShim:
        @staticmethod
        def raises(exc_type):
            return _RaisesContext(exc_type)

    pytest = _PytestShim()  # type: ignore[assignment]

try:
    import numpy as _np  # noqa: F401
    from PIL import Image as _pil_img  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    import sys
    import types

    if "numpy" not in sys.modules:
        _stub_np = types.ModuleType("numpy")
        _stub_np.ndarray = object  # type: ignore[attr-defined]
        _stub_np.float32 = float  # type: ignore[attr-defined]
        _stub_np.float64 = float  # type: ignore[attr-defined]
        _stub_np.dtype = lambda *_a, **_kw: types.SimpleNamespace(itemsize=4)  # type: ignore[attr-defined]
        sys.modules["numpy"] = _stub_np
    if "PIL" not in sys.modules:
        _stub_pil = types.ModuleType("PIL")
        _stub_pil.Image = types.SimpleNamespace(Image=object, open=lambda *_a, **_kw: None)  # type: ignore[attr-defined]
        sys.modules["PIL"] = _stub_pil
        sys.modules["PIL.Image"] = _stub_pil.Image  # type: ignore[assignment]

from vip_fvs.core_report import (
    ANALYSIS_KIND_SEMANTIC_RETRIEVAL,
    CORE_REPORT_KIND,
    CORE_REPORT_SCHEMA_VERSION,
    NOT_OBSERVED,
    CoreReportError,
    CoreReportPublicationError,
    build_core_semantic_report,
    build_point_semantic_location,
    compute_core_report_digest,
    format_rational_seconds,
    publish_core_semantic_report,
    serialize_core_semantic_report,
    validate_core_semantic_report,
)


def _sample_report_Fixtures(output_root: Path, *, with_matches: bool = True) -> dict:
    source_sha = "a" * 64
    space_id = "b" * 64
    gen_id = "c" * 64
    probe_digest = "d" * 64
    norm_query = "ballet grand jete"
    query_digest = hashlib.sha256(norm_query.encode("utf-8")).hexdigest()
    report_path = output_root / "semantic-report.json"

    matches = []
    if with_matches:
        for rank_idx, (row_id, pts, score) in enumerate(
            ((1, 4004, 0.812345), (0, 1001, 0.654321)), start=1
        ):
            matches.append(
                {
                    "candidate_id": f"candidate:att-001:rank:{rank_idx}:row:{row_id}",
                    "row_id": row_id,
                    "rank": rank_idx,
                    "score": score,
                    "score_is_probability": False,
                    "source_sha256": source_sha,
                    "source_revision_id": "rev-001",
                    "source_locator": "/tmp/source.mp4",
                    "selected_stream_index": 1,
                    "sampled_timing": {
                        "pts": pts,
                        "timebase": {"num": 1001, "den": 30000},
                        "time_domain": "source_pts",
                        "rational_seconds": format_rational_seconds(pts, 1001, 30000),
                        "display_timestamp": "00:00:00.133",
                        "display_only_not_frame_authority": True,
                        "evidence_class": "MEASURED",
                        "measurement_provenance": "ffmpeg_showinfo_one_pass_sample_pts",
                        "is_event_boundary": False,
                        "is_edit_boundary": False,
                    },
                    "approx_semantic_location": build_point_semantic_location(
                        pts, 1001, 30000
                    ),
                    "semantic_assertion": {
                        "evidence_class": "MATCHED",
                        "binding_eligible": False,
                        "assertion_kind": "query_visual_similarity_candidate",
                        "caption_claim": NOT_OBSERVED,
                    },
                    "measured_frame_interval": NOT_OBSERVED,
                    "thumbnail": {
                        "status": "PRESENT",
                        "path": f"thumbnails/{source_sha}/{pts}.jpg",
                    },
                }
            )

    return build_core_semantic_report(
        attempt_id="att-001",
        run_id="core-analyze:att-001",
        runtime_mode="SYNTHETIC",
        top_k=5,
        total_eligible_matches=len(matches),
        source={
            "source_locator": "/tmp/source.mp4",
            "source_revision_id": "rev-001",
            "source_sha256": source_sha,
            "source_byte_count": 4096,
            "custody_state": "PRESERVED_IMMUTABLE",
            "immutability_verified": {
                "before_analysis": True,
                "after_analysis": True,
                "source_sha256_before": source_sha,
                "source_sha256_after": source_sha,
                "source_byte_count_before": 4096,
                "source_byte_count_after": 4096,
            },
            "snapshot": NOT_OBSERVED,
            "probe": {
                "probe_artifact_ref": "probe:att-001",
                "probe_digest": probe_digest,
                "selected_stream_index": 1,
                "timebase": {"num": 1001, "den": 30000},
                "time_domain": "source_pts",
                "evidence_class": "MEASURED",
                "measurement_provenance": "ffprobe_stream_probe",
            },
        },
        authority={
            "authorization_mode": "SYNTHETIC_TEST_ONLY",
            "authorization_id": "synthetic-auth:att-001",
            "authorization_record_digest": NOT_OBSERVED,
            "policy_digest": NOT_OBSERVED,
            "scope_digest": NOT_OBSERVED,
            "local_only": True,
            "development_source_auth_enforcement": "DISABLED_BY_OWNER",
        },
        model={
            "model_family": "synthetic_fake",
            "model_identity": "vip-fvs-fake-embedder",
            "frozen_revision": "synthetic-v1",
            "weights_sha256": "0" * 64,
            "processor_digest": "0" * 64,
            "image_preprocessing_digest": "0" * 64,
            "text_preprocessing_contract": "padding=max_length",
            "embedding_dim": 768,
            "dtype": "float32",
            "normalization": "l2",
            "semantic_space_id": space_id,
            "runtime_identity": "vip-fvs-fake-runtime/v1",
            "runtime_mode": "SYNTHETIC",
            "authentic_inference_observed": False,
        },
        index={
            "generation_id": gen_id,
            "semantic_space_id": space_id,
            "index_disposition": "INDEXED",
            "manifest_digest": "e" * 64,
            "committed_row_count": len(matches),
            "source_sample_count": len(matches),
            "single_source_scope_verified": True,
            "sampling_policy": {
                "sampling_policy_id": "coarse-pts-4.5s",
                "sampling_policy_version": 1,
                "sampling_interval_seconds": 4.5,
                "selected_stream_policy": "first-video-stream",
                "selected_stream_index": 1,
            },
        },
        query={
            "query_id": "query:att-001",
            "raw_text": "  ballet   grand jete ",
            "normalized_text": norm_query,
            "query_digest": query_digest,
            "modality": "text",
            "score_interpretation": "uncalibrated_cosine_similarity_not_probability",
        },
        matches=matches,
        report_path=str(report_path),
        output_root=str(output_root),
    )


def test_report_v1_valid_positive_and_zero_match(tmp_path: Path) -> None:
    report = _sample_report_Fixtures(tmp_path, with_matches=True)
    assert report["schema_version"] == CORE_REPORT_SCHEMA_VERSION
    assert report["report_kind"] == CORE_REPORT_KIND
    assert report["analysis_kind"] == ANALYSIS_KIND_SEMANTIC_RETRIEVAL
    assert report["stage_status"] == "SUCCEEDED"
    assert report["result_kind"] == "MATCHES_FOUND"
    assert report["returned_candidate_count"] == 2
    assert report["artifact"]["report_digest"] == compute_core_report_digest(report)

    zero_report = _sample_report_Fixtures(tmp_path, with_matches=False)
    assert zero_report["stage_status"] == "SUCCEEDED"
    assert zero_report["result_kind"] == "ZERO_MATCH"
    assert zero_report["returned_candidate_count"] == 0
    assert zero_report["total_eligible_matches"] == 0
    assert zero_report["matches"] == []


def test_report_digest_self_verification_and_tamper_rejection(tmp_path: Path) -> None:
    report = _sample_report_Fixtures(tmp_path, with_matches=True)
    tampered = copy.deepcopy(report)
    tampered["matches"][0]["score"] = 0.999999
    with pytest.raises(CoreReportError) as exc_info:
        validate_core_semantic_report(tampered)
    assert exc_info.value.code == "REPORT_DIGEST_MISMATCH"


def test_point_semantic_location_rejects_degenerate_or_fabricated_intervals(
    tmp_path: Path,
) -> None:
    report = _sample_report_Fixtures(tmp_path, with_matches=True)
    loc = report["matches"][0]["approx_semantic_location"]
    assert loc["location_kind"] == "POINT"
    assert loc["window_width_seconds"] == NOT_OBSERVED
    assert "start_seconds" not in loc
    assert "end_seconds" not in loc

    bad_point = copy.deepcopy(report)
    bad_point["matches"][0]["approx_semantic_location"]["start_seconds"] = 0.133467
    bad_point["matches"][0]["approx_semantic_location"]["end_seconds"] = 0.133467
    bad_point["artifact"]["report_digest"] = compute_core_report_digest(bad_point)
    with pytest.raises(CoreReportError) as exc_info:
        validate_core_semantic_report(bad_point)
    assert exc_info.value.code == "REPORT_POINT_LOCATION_HAS_INTERVAL_BOUNDS"

    bad_window = copy.deepcopy(report)
    bad_window["matches"][0]["approx_semantic_location"] = {
        "location_kind": "COARSE_WINDOW",
        "time_domain": "semantic_seconds",
        "start_seconds": 1.0,
        "end_seconds": 1.0,
        "window_width_seconds": 0.0,
    }
    bad_window["artifact"]["report_digest"] = compute_core_report_digest(bad_window)
    with pytest.raises(CoreReportError) as exc_info2:
        validate_core_semantic_report(bad_window)
    assert exc_info2.value.code == "REPORT_INVALID_COARSE_WINDOW"


def test_not_observed_rejected_as_sixth_evidence_class(tmp_path: Path) -> None:
    report = _sample_report_Fixtures(tmp_path, with_matches=True)
    bad = copy.deepcopy(report)
    bad["matches"][0]["semantic_assertion"]["evidence_class"] = "NOT_OBSERVED"
    bad["artifact"]["report_digest"] = compute_core_report_digest(bad)
    with pytest.raises(CoreReportError) as exc_info:
        validate_core_semantic_report(bad)
    assert exc_info.value.code == "REPORT_INVALID_EVIDENCE_CLASS"


def test_fake_embedder_cannot_be_labeled_as_real(tmp_path: Path) -> None:
    report = _sample_report_Fixtures(tmp_path, with_matches=True)
    bad = copy.deepcopy(report)
    bad["runtime_mode"] = "REAL"
    bad["model"]["runtime_mode"] = "REAL"
    bad["model"]["authentic_inference_observed"] = True
    bad["evidence_availability"]["authentic_model_inference"] = "OBSERVED"
    bad["source"]["snapshot"] = {
        "snapshot_id": "f" * 32,
        "snapshot_path": "/tmp/snap/source.mp4",
        "snapshot_sha256": "a" * 64,
        "source_byte_count": 4096,
        "source_revision_id": "rev-001",
    }
    bad["authority"] = {
        "authorization_mode": "OWNER_PILOT_AUTHORIZATION",
        "authorization_id": "auth-001",
        "authorization_record_digest": "1" * 64,
        "policy_digest": "2" * 64,
        "scope_digest": "3" * 64,
        "local_only": True,
        "development_source_auth_enforcement": "DISABLED_BY_OWNER",
    }
    bad["artifact"]["report_digest"] = compute_core_report_digest(bad)
    with pytest.raises(CoreReportError) as exc_info:
        validate_core_semantic_report(bad)
    assert exc_info.value.code == "REPORT_FAKE_EMBEDDER_MISLABELED_AS_REAL"


def test_atomic_publication_no_clobber_and_path_confinement(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    report_path = output_root / "nested" / "semantic-report.json"
    report = _sample_report_Fixtures(output_root, with_matches=True)

    published = publish_core_semantic_report(
        report, report_path, output_root=output_root
    )
    assert published == report_path.resolve()
    original_bytes = published.read_bytes()
    assert json.loads(original_bytes.decode("utf-8"))["artifact"]["report_digest"] == (
        report["artifact"]["report_digest"]
    )

    # Repeated publication to same path must refuse with OUTPUT_ALREADY_EXISTS even when bytes match
    with pytest.raises(CoreReportPublicationError) as exc_info:
        publish_core_semantic_report(report, report_path, output_root=output_root)
    assert exc_info.value.code == "OUTPUT_ALREADY_EXISTS"
    assert published.read_bytes() == original_bytes

    # Path outside output_root refused
    outside_path = tmp_path / "outside-report.json"
    with pytest.raises(CoreReportPublicationError) as exc_outside:
        publish_core_semantic_report(report, outside_path, output_root=output_root)
    assert exc_outside.value.code == "OUTPUT_PATH_OUTSIDE_ROOT"
    assert not outside_path.exists()

    # '..' traversal refused
    traversal_path = output_root / ".." / "escaped.json"
    with pytest.raises(CoreReportPublicationError) as exc_trav:
        publish_core_semantic_report(report, traversal_path, output_root=output_root)
    assert exc_trav.value.code == "OUTPUT_PATH_TRAVERSAL_FORBIDDEN"

    # Symlink target or directory refused
    symlink_target = output_root / "symlink-report.json"
    symlink_target.symlink_to(tmp_path / "real-target.json")
    with pytest.raises(CoreReportPublicationError) as exc_sym:
        publish_core_semantic_report(report, symlink_target, output_root=output_root)
    assert exc_sym.value.code == "OUTPUT_SYMLINK_FORBIDDEN"


class CoreReportStdlibTestCase(unittest.TestCase):
    """Stdlib unittest wrapper so core_report tests also execute directly under python3 -m unittest."""

    def test_all_core_report_invariants(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_report_v1_valid_positive_and_zero_match(root / "t1")
            test_report_digest_self_verification_and_tamper_rejection(root / "t2")
            test_point_semantic_location_rejects_degenerate_or_fabricated_intervals(
                root / "t3"
            )
            test_not_observed_rejected_as_sixth_evidence_class(root / "t4")
            test_fake_embedder_cannot_be_labeled_as_real(root / "t5")
            test_atomic_publication_no_clobber_and_path_confinement(root / "t6")


if __name__ == "__main__":
    unittest.main()
