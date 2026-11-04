"""Regression tests for Packet P00 and Wave MEGA-03 (P03a, P03b, P03c)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
import pytest

from vip_fvs.review_bundle import (
    RECORD_TYPE as RB_RECORD_TYPE,
    V1_SCHEMA_VERSION,
    V2_SCHEMA_VERSION,
    V3_SCHEMA_VERSION,
    dependency_digest,
    record_digest,
)
from vip_fvs.source_snapshot import SourceSnapshotStore
from vip_lab.common import (
    ReadinessStatus,
    SyntheticContextMarker,
    VipLabError,
    canonical_json_dumps,
    load_bounded_json_file,
    parse_strict_json_text,
)
from vip_lab.mega03 import (
    inspect_review_bundle_record,
    inspect_s5_declaration,
    inspect_stream_namespace,
)


def _capture_sample_snapshot(
    tmp_path: Path,
    source_bytes: bytes = b"synthetic-iso-bmff-placeholder",
    source_revision: str = "rev_001",
) -> tuple[Path, str, dict[str, Any]]:
    src_dir = tmp_path / "source_input"
    src_dir.mkdir(parents=True, exist_ok=True)
    src_file = src_dir / "swan_lake.mp4"
    src_file.write_bytes(source_bytes)
    sha = hashlib.sha256(source_bytes).hexdigest()

    store_dir = tmp_path / "snap_store"
    store = SourceSnapshotStore(
        store_dir,
        max_source_bytes=1024 * 1024,
        max_store_bytes=4 * 1024 * 1024,
    )
    snap = store.capture(
        src_file,
        expected_sha256=sha,
        authorization_id="auth_synth_01",
        source_revision_id=source_revision,
    )
    return src_dir, sha, snap.as_evidence()


def _make_review_bundle_record(
    schema_version: str,
    *,
    snapshot_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    src_sha = (
        snapshot_evidence["snapshot_sha256"]
        if snapshot_evidence is not None
        else "a" * 64
    )
    src_bytes = (
        snapshot_evidence["source_byte_count"]
        if snapshot_evidence is not None
        else 128
    )
    src_locator = (
        snapshot_evidence["source_locator"]
        if snapshot_evidence is not None
        else "/tmp/synthetic/swan_lake.mp4"
    )
    req_locator = (
        snapshot_evidence["snapshot_path"]
        if snapshot_evidence is not None
        else src_locator
    )

    source_block: dict[str, Any] = {
        "source_revision_id": "rev_001",
        "source_sha256": src_sha,
        "source_byte_count": src_bytes,
        "selected_stream_index": 0,
        "timebase": {"num": 1, "den": 90000},
        "probe_artifact_ref": "/nonexistent/probe.json",
        "probe_digest": "1" * 64,
    }
    if schema_version == V3_SCHEMA_VERSION and snapshot_evidence is not None:
        source_block["source_locator"] = src_locator
        source_block["snapshot"] = snapshot_evidence

    refinement_block: dict[str, Any] = {
        "refinement_id": "ref_001",
        "status": "MEASURED",
        "source_revision_id": "rev_001",
        "selected_stream_index": 0,
        "source_pts_interval": {
            "start": 90000,
            "end": 270000,
            "time_domain": "source_pts",
            "endpoint_semantics": "half_open",
        },
        "timebase": {"num": 1, "den": 90000},
        "attempt_id": "att_001",
        "evidence_artifact_ref": "/nonexistent/e01_refinement.json",
        "evidence_digest": "2" * 64,
        "evidence_class": "MEASURED",
    }

    if schema_version in (V2_SCHEMA_VERSION, V3_SCHEMA_VERSION):
        req_dict = {
            "request_id": "req_001",
            "candidate_assertion_ref": "cand_001",
            "source_revision_id": "rev_001",
            "source_locator": req_locator,
            "expected_source_sha256": src_sha,
            "selected_stream_index": 0,
            "requested_start_pts": 90000,
            "requested_end_pts": 270000,
            "producer_attempt_id": "att_001",
            "idempotency_key": "idem_001",
            "expected_timebase": [1, 90000],
        }
        req_digest = hashlib.sha256(
            canonical_json_dumps(req_dict).encode("utf-8")
        ).hexdigest()
        refinement_block["request_identity"] = {
            "request_id": "req_001",
            "candidate_assertion_ref": "cand_001",
            "producer_attempt_id": "att_001",
            "idempotency_key": "idem_001",
            "request_digest": req_digest,
            "request": req_dict,
        }

    payload: dict[str, Any] = {
        "bundle_id": "bundle_001",
        "run_id": "run_001",
        "created_at": "2026-10-30T12:00:00Z",
        "review_status": "AWAITING_EDITORIAL_DECISION",
        "source": source_block,
        "authorization": {
            "discovery_policy_ref": "pol_disc_01",
            "refinement_policy_ref": "pol_ref_01",
            "policy_digest": "3" * 64,
            "scope_digest": "4" * 64,
        },
        "query": {
            "query_id": "q_01",
            "text": "grand jete",
            "digest": "5" * 64,
        },
        "generation": {
            "attempt_id": "att_001",
            "generation_id": "gen_001",
            "semantic_space_id": "vip-v1-siglip-base-224:768",
            "model_identity": "siglip-base-patch16-224",
            "model_revision": "rev1",
            "weights_digest": "6" * 64,
            "processor_digest": "7" * 64,
            "index_ref": "idx_001",
            "index_digest": "8" * 64,
            "input_digest": "9" * 64,
        },
        "candidate": {
            "candidate_id": "cand_001",
            "rank": 1,
            "score": 0.9125,
            "evidence_class": "MATCHED",
            "binding_eligible": False,
            "assertion_digest": "b" * 64,
            "semantic_interval": {
                "start": 1.0,
                "end": 3.0,
                "time_domain": "semantic_seconds",
                "endpoint_semantics": "half_open",
            },
        },
        "refinement": refinement_block,
        "presentation": {
            "display_only": True,
            "start_seconds": 1.0,
            "end_seconds": 3.0,
        },
        "dependency_digest": "0" * 64,
        "decision": None,
    }
    payload["dependency_digest"] = dependency_digest(payload)
    record = {
        "record_id": "bundle_001",
        "record_type": RB_RECORD_TYPE,
        "record_schema_version": schema_version,
        "record_digest": "0" * 64,
        "payload": payload,
    }
    record["record_digest"] = record_digest(record)
    return record


class TestPacketP00Common:
    def test_canonical_json_rejects_nan_and_nonstring_keys(self) -> None:
        with pytest.raises(VipLabError) as exc_info:
            canonical_json_dumps({"bad": float("nan")})
        assert exc_info.value.code == "LAB_NONFINITE_NUMBER"

        with pytest.raises(VipLabError) as exc_info2:
            canonical_json_dumps({123: "value"})  # type: ignore[dict-item]
        assert exc_info2.value.code == "LAB_NONSTRING_JSON_KEY"

    def test_strict_json_rejects_duplicate_keys_and_oversized_bytes(self) -> None:
        with pytest.raises(VipLabError) as exc_info:
            parse_strict_json_text('{"a": 1, "a": 2}')
        assert exc_info.value.code == "LAB_DUPLICATE_JSON_KEY"

        with pytest.raises(VipLabError) as exc_info2:
            parse_strict_json_text('{"a": 1}', max_bytes=4)
        assert exc_info2.value.code == "LAB_JSON_SIZE_EXCEEDED"

    def test_forged_context_marker_rejected(self) -> None:
        with pytest.raises(VipLabError) as exc_info:
            SyntheticContextMarker(
                token="VIP_LAB_SYNTHETIC_ONLY_V1",
                synthetic_only=True,
                authentic_authority_granted=False,
                _seal=object(),
            )
        assert exc_info.value.code == "LAB_FORGED_CONTEXT_MARKER"

    def test_load_bounded_json_refuses_symlink(self, tmp_path: Path) -> None:
        real_file = tmp_path / "real.json"
        real_file.write_text('{"ok": true}', encoding="utf-8")
        link_file = tmp_path / "link.json"
        link_file.symlink_to(real_file)

        loaded = load_bounded_json_file(real_file)
        assert loaded == {"ok": True}

        with pytest.raises(VipLabError) as exc_info:
            load_bounded_json_file(link_file)
        assert exc_info.value.code in ("LAB_FILE_OPEN_REFUSED", "LAB_NON_REGULAR_FILE")


class TestMega03S5Preflight:
    def test_valid_metadata_never_admits_or_measures_source(self) -> None:
        source_bytes = b"synthetic-only-not-opened"
        declared_sha = hashlib.sha256(source_bytes).hexdigest()
        body = {
            "schema_version": 1,
            "source_revision_id": "rev_001",
            "source_sha256": declared_sha,
            "source_byte_count": len(source_bytes),
        }
        temporal = {
            **body,
            "evidence_sha256": hashlib.sha256(
                canonical_json_dumps(body).encode("utf-8")
            ).hexdigest(),
        }
        pkt = inspect_s5_declaration({
            "source_id": "src_swan_01",
            "source_revision": "rev_001",
            "declared_sha256": declared_sha,
            "declared_size": len(source_bytes),
            "relative_path": "swan_lake.mp4",
            "snapshot": {
                "source_revision_id": "rev_001",
                "snapshot_sha256": declared_sha,
                "source_byte_count": len(source_bytes),
            },
            "temporal_binding": temporal,
            "trusted": True,
        })
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.synthetic_only is True
        assert pkt.execution_authorized is False
        assert pkt.evidence_state == "NOT_OBSERVED"
        assert pkt.summary["admitted"] is False
        assert pkt.summary["bytes_verified"] is False
        assert pkt.summary["snapshot_verified"] is False
        assert pkt.summary["snapshot_record_declared_consistent"] is True
        assert pkt.summary["temporal_binding_version"] == 1
        assert "UNTRUSTED_AUTHORITY_FLAGS_IGNORED" in pkt.reasons
        assert all(f.evidence_state == "NOT_OBSERVED" for f in pkt.findings)

    def test_s5_refuses_path_traversal_and_absolute_paths(self) -> None:
        for bad_path in ("../outside.mp4", "/etc/passwd", "a/../../b.mp4", "a\\b.mp4"):
            pkt = inspect_s5_declaration(
                {
                    "source_id": "src_01",
                    "source_revision": "rev_1",
                    "declared_sha256": "a" * 64,
                    "declared_size": 32,
                    "relative_path": bad_path,
                }
            )
            assert pkt.status == ReadinessStatus.INVALID
            assert pkt.summary["admitted"] is False

    def test_s5_refuses_even_synthetic_source_root_without_opening(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import os

        # Refuse before any filesystem API call, even when bytes and hash match.
        def forbidden_open(*args: Any, **kwargs: Any) -> None:
            raise AssertionError("S5 metadata-only inspector must not open source bytes")

        monkeypatch.setattr(os, "open", forbidden_open)
        pkt = inspect_s5_declaration({
            "source_id": "src_01",
            "source_revision": "rev_1",
            "declared_sha256": "f" * 64,
            "declared_size": 16,
            "relative_path": "clip.mp4",
        }, snapshot_root=tmp_path)
        assert pkt.status == ReadinessStatus.BLOCKED
        assert "S5_SOURCE_BYTE_ADMISSION_NOT_AUTHORIZED" in pkt.blockers
        assert pkt.summary["admitted"] is False
        assert pkt.summary["bytes_verified"] is False

    def test_s5_declared_snapshot_mismatch_is_invalid_without_read(self) -> None:
        pkt = inspect_s5_declaration({
            "source_id": "src_01",
            "source_revision": "rev_1",
            "declared_sha256": "f" * 64,
            "declared_size": 16,
            "relative_path": "clip.mp4",
            "snapshot": {
                "source_revision_id": "rev_1",
                "snapshot_sha256": "a" * 64,
                "source_byte_count": 16,
            },
        })
        assert pkt.status == ReadinessStatus.INVALID
        assert "S5_SNAPSHOT_DECLARATION_MISMATCH" in pkt.blockers

class TestMega03StreamIdentityPreflight:
    def test_negative_preflight_refuses_numeric_coincidence_and_multi_trak(self) -> None:
        pkt = inspect_stream_namespace(
            {
                "ffprobe_stream_index": 0,
                "mp4_track_index": 0,
                "mp4_track_id": 1,
                "mp4_trak_count": 1,
            }
        )
        assert pkt.status == ReadinessStatus.BLOCKED
        assert "STREAM_IDENTITY_METADATA_ONLY_UNPROVEN" in pkt.blockers
        assert pkt.summary["stream_identity_verified"] is False

        multi_pkt = inspect_stream_namespace(
            {
                "ffprobe_stream_index": 0,
                "mp4_track_index": 0,
                "mp4_trak_count": 2,
                "identity_derivation": "POSITIONAL_INDEX_EQUALITY",
                "claim_positive_track_id_mapping": True,
            }
        )
        assert multi_pkt.status == ReadinessStatus.BLOCKED
        assert "STREAM_IDENTITY_MULTI_TRAK_AMBIGUOUS" in multi_pkt.blockers
        assert "POSITIONAL_STREAM_IDENTITY_FORBIDDEN" in multi_pkt.blockers
        assert "STREAM_NAMESPACE_POSITIVE_MAPPING_DEFERRED" in multi_pkt.blockers


class TestMega03ReviewBundleCheck:
    @pytest.mark.parametrize(
        "schema_ver",
        [V1_SCHEMA_VERSION, V2_SCHEMA_VERSION, V3_SCHEMA_VERSION],
    )
    def test_review_bundle_v1_v2_v3_envelope_valid_but_e01_unvalidated(
        self, tmp_path: Path, schema_ver: str
    ) -> None:
        snap_ev = None
        if schema_ver == V3_SCHEMA_VERSION:
            _, _, snap_ev = _capture_sample_snapshot(tmp_path)
        rec = _make_review_bundle_record(schema_ver, snapshot_evidence=snap_ev)
        pkt = inspect_review_bundle_record(rec, require_e01_binding=False)
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.summary["envelope_valid"] is True
        assert pkt.summary["current_e01_validated"] is False
        assert pkt.summary["binding_eligible"] is False
        assert "REVIEW_BUNDLE_ENVELOPE_VALID_BUT_E01_UNVALIDATED" in pkt.reasons

        strict_pkt = inspect_review_bundle_record(rec, require_e01_binding=True)
        assert strict_pkt.status == ReadinessStatus.BLOCKED
        assert "REVIEW_BUNDLE_E01_UNVALIDATED" in strict_pkt.blockers

    def test_review_bundle_tampered_digest_rejected(self, tmp_path: Path) -> None:
        _, _, snap_ev = _capture_sample_snapshot(tmp_path)
        rec = _make_review_bundle_record(V3_SCHEMA_VERSION, snapshot_evidence=snap_ev)
        rec["record_digest"] = "0" * 64
        pkt = inspect_review_bundle_record(rec)
        assert pkt.status == ReadinessStatus.INVALID
        assert "REVIEW_BUNDLE_VALIDATION_FAILED" in pkt.blockers
