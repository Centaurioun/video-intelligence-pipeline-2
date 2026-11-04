"""End-to-end deterministic integration and tamper-resistance tests for MEGA-15 + MEGA-16."""

from __future__ import annotations

import copy
import pytest

from vip_lab.common import VipLabError, canonical_json_bytes
from vip_lab.mega13 import CANONICAL_RELEASE_BLOCKER_CODES
from vip_lab.mega16 import (
    run_mega15_16_offline_pipeline,
    verify_mega15_16_offline_report,
)


def test_mega15_16_end_to_end_deterministic_replay_and_invariants() -> None:
    report_a = run_mega15_16_offline_pipeline(seed=20261102)
    report_b = run_mega15_16_offline_pipeline(seed=20261102)

    assert report_a.report_digest == report_b.report_digest
    assert canonical_json_bytes(report_a.to_dict()) == canonical_json_bytes(
        report_b.to_dict()
    )

    # Verify all non-negotiable NOT_OBSERVED / False authority boundaries
    cert = report_a.release_refusal_certificate
    assert cert.real_source_media_state == "NOT_OBSERVED"
    assert cert.authentic_model_inference_state == "NOT_OBSERVED"
    assert cert.source_pts_measurement_state == "NOT_OBSERVED"
    assert cert.real_human_editorial_decision_state == "NOT_OBSERVED"
    assert cert.technical_qc_state == "NOT_OBSERVED"
    assert cert.visual_editorial_qc_state == "NOT_OBSERVED"
    assert cert.audio_editorial_qc_state == "NOT_OBSERVED"
    assert cert.preview_eligible is False
    assert cert.production_export_authorized is False
    assert cert.gate_promotion_authorized is False
    assert cert.export_status == "REFUSED_NOT_AUTHORIZED"
    assert set(CANONICAL_RELEASE_BLOCKER_CODES).issubset(
        set(cert.active_release_blocker_codes)
    )

    # Verify genuine duplicate occurrence and query-text preservation across the E2E fixture
    assert report_a.mega15_lineage_receipt.lineage_valid is True
    assert report_a.mega15_lineage_receipt.duplicate_occurrence_paths_preserved is True
    assert report_a.mega15_lineage_receipt.duplicate_query_texts_preserved is True

    sha_to_paths: dict[str, set[str]] = {}
    for occ in report_a.preparation_packet.occurrence_identities:
        sha_to_paths.setdefault(occ["source_sha256"], set()).add(occ["source_path"])
    assert any(len(paths) >= 2 for paths in sha_to_paths.values())

    qtext_to_qids: dict[str, set[str]] = {}
    for q in report_a.preparation_packet.query_identities:
        qtext_to_qids.setdefault(q["query_text"], set()).add(q["query_id"])
    assert any(len(qids) >= 2 for qids in qtext_to_qids.values())

    # Full JSON round-trip verification
    verified = verify_mega15_16_offline_report(report_a.to_dict())
    assert verified == report_a


def test_mega15_16_end_to_end_rejects_cross_stage_digest_tampering() -> None:
    report = run_mega15_16_offline_pipeline(seed=20261102)
    raw = report.to_dict()

    # Tamper 1: mutate preparation_packet_digest inside render_specification
    tampered_1 = copy.deepcopy(raw)
    tampered_1["render_specification"]["preparation_packet_digest"] = "0" * 64
    with pytest.raises(VipLabError):
        verify_mega15_16_offline_report(tampered_1)

    # Tamper 2: mutate source_pts_evidence_state inside temporal_records[0]
    tampered_2 = copy.deepcopy(raw)
    tampered_2["preparation_packet"]["temporal_records"][0][
        "source_pts_evidence_state"
    ] = "MEASURED"
    with pytest.raises(VipLabError):
        verify_mega15_16_offline_report(tampered_2)

    # Tamper 3: mutate real_human_decision_state inside handoff_envelopes[0]
    tampered_3 = copy.deepcopy(raw)
    tampered_3["preparation_packet"]["handoff_envelopes"][0][
        "real_human_decision_state"
    ] = "OBSERVED"
    with pytest.raises(VipLabError):
        verify_mega15_16_offline_report(tampered_3)

    # Tamper 4: mutate technical_qc_state inside qc_requirements_bundle
    tampered_4 = copy.deepcopy(raw)
    tampered_4["qc_requirements_bundle"]["technical_qc_state"] = "MEASURED"
    with pytest.raises(VipLabError):
        verify_mega15_16_offline_report(tampered_4)
