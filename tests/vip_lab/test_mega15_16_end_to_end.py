from __future__ import annotations

import pytest

from vip_lab.common import NOT_OBSERVED, VipLabError, canonical_json_dumps
from vip_lab.mega16 import (
    MEGA15_16_PROGRAM_VERSION,
    Mega1516OfflineBundle,
    run_mega15_16_offline_pipeline,
    verify_mega15_16_offline_bundle,
)


def test_mega15_16_end_to_end_three_arm_and_single_arm_determinism() -> None:
    bundle_3a_first = run_mega15_16_offline_pipeline(scenario_mode="three_arm")
    bundle_3a_second = run_mega15_16_offline_pipeline(scenario_mode="three_arm")

    verify_mega15_16_offline_bundle(bundle_3a_first)
    verify_mega15_16_offline_bundle(bundle_3a_second)

    assert bundle_3a_first.bundle_digest == bundle_3a_second.bundle_digest
    assert canonical_json_dumps(bundle_3a_first.to_dict()) == canonical_json_dumps(
        bundle_3a_second.to_dict()
    )
    assert bundle_3a_first.lab_program_version == MEGA15_16_PROGRAM_VERSION
    assert bundle_3a_first.scenario_mode == "three_arm"
    assert bundle_3a_first.lineage_certificate.duplicate_occurrence_paths_preserved is True
    assert bundle_3a_first.lineage_certificate.duplicate_query_texts_preserved is True
    assert bundle_3a_first.export_readiness_packet.export_status == "REFUSED_NOT_AUTHORIZED"
    assert bundle_3a_first.export_readiness_packet.real_human_decision_state == NOT_OBSERVED
    assert bundle_3a_first.export_readiness_packet.source_pts_evidence_state == NOT_OBSERVED
    assert bundle_3a_first.export_readiness_packet.render_executed is False
    assert bundle_3a_first.export_readiness_packet.production_export_authorized is False

    # Round-trip serialization
    reloaded_3a = Mega1516OfflineBundle.from_dict(bundle_3a_first.to_dict())
    assert reloaded_3a.bundle_digest == bundle_3a_first.bundle_digest

    # Single-arm mode
    bundle_1a = run_mega15_16_offline_pipeline(scenario_mode="single_arm")
    verify_mega15_16_offline_bundle(bundle_1a)
    assert bundle_1a.scenario_mode == "single_arm"
    assert bundle_1a.export_readiness_packet.export_status == "REFUSED_NOT_AUTHORIZED"


def test_mega15_16_end_to_end_adversarial_tampering_matrix() -> None:
    bundle = run_mega15_16_offline_pipeline(scenario_mode="three_arm")
    base_dict = bundle.to_dict()

    # 1. Tamper top-level bundle_digest
    tampered_bundle_digest = dict(base_dict)
    tampered_bundle_digest["bundle_digest"] = "f" * 64
    with pytest.raises(VipLabError, match="digest mismatch"):
        Mega1516OfflineBundle.from_dict(tampered_bundle_digest)

    # 2. Tamper stage link between preparation_packet and lineage_certificate
    tampered_lineage_link = bundle.to_dict()
    tampered_lineage_link["lineage_certificate"]["preparation_packet_digest"] = "1" * 64
    with pytest.raises(VipLabError):
        Mega1516OfflineBundle.from_dict(tampered_lineage_link)

    # 3. Forged measured PTS inside preparation_packet
    forged_pts = bundle.to_dict()
    forged_pts["preparation_packet"]["temporal_records"][0]["source_pts_evidence_state"] = "MEASURED"
    with pytest.raises(VipLabError):
        Mega1516OfflineBundle.from_dict(forged_pts)

    # 4. Bogus real human approval inside handoff_envelopes
    forged_human = bundle.to_dict()
    forged_human["preparation_packet"]["handoff_envelopes"][0]["real_human_decision_state"] = "ACCEPTED"
    with pytest.raises(VipLabError):
        Mega1516OfflineBundle.from_dict(forged_human)

    # 5. Spoofed QC PASS inside qc_requirement_manifest
    spoofed_qc = bundle.to_dict()
    spoofed_qc["qc_requirement_manifest"]["overall_qc_status"] = "PASS"
    with pytest.raises(VipLabError):
        Mega1516OfflineBundle.from_dict(spoofed_qc)

    # 6. Forged visual sensory QC inside qc_requirement_manifest
    forged_visual = bundle.to_dict()
    forged_visual["qc_requirement_manifest"]["visual_editorial_qc_observed"] = "VISUALLY_OBSERVED"
    with pytest.raises(VipLabError):
        Mega1516OfflineBundle.from_dict(forged_visual)

    # 7. False stream namespace equivalence proof
    forged_stream = bundle.to_dict()
    forged_stream["preparation_packet"]["temporal_records"][0]["stream_namespace_preflight"][
        "namespace_equivalence_proven"
    ] = True
    with pytest.raises(VipLabError):
        Mega1516OfflineBundle.from_dict(forged_stream)

    # 8. Forged terminal-tail binding eligibility
    forged_tail = bundle.to_dict()
    forged_tail["preparation_packet"]["temporal_records"][0]["terminal_tail_preflight"][
        "tail_binding_eligible"
    ] = True
    with pytest.raises(VipLabError):
        Mega1516OfflineBundle.from_dict(forged_tail)

    # 9. Unapproved production export flip
    forged_export = bundle.to_dict()
    forged_export["export_readiness_packet"]["export_status"] = "EXPORT_READY"
    with pytest.raises(VipLabError):
        Mega1516OfflineBundle.from_dict(forged_export)
