"""Tests for MEGA-17 Workstream B: Source Identity, Custody, Rights, and D-2 Readiness."""

from __future__ import annotations

import pytest

from vip_lab.common import ReadinessStatus, VipLabError
from vip_lab.mega17.source_readiness import (
    PERMISSION_CREATE_DERIVED_ARTIFACTS,
    PERMISSION_DISCOVER_SOURCES,
    PERMISSION_EXPORT_OUTPUTS,
    PERMISSION_INSPECT_LOCAL_BYTES,
    PERMISSION_PROVIDER_OR_CLOUD_EGRESS,
    PERMISSION_RETAIN_OUTPUTS,
    PERMISSION_RUN_AUTHENTIC_MODELS,
    REFUSAL_D3_EXECUTION_NOT_AUTHORIZED,
    REFUSAL_DEV_EVAL_PARTITION_LEAKAGE,
    REFUSAL_DISCOVERY_DOES_NOT_GRANT_PROCESSING,
    REFUSAL_DUPLICATE_OCCURRENCE_COLLAPSE_FORBIDDEN,
    REFUSAL_FILENAME_EQUALITY_NOT_BYTE_IDENTITY,
    REFUSAL_FORGED_OWNER_ATTESTATION,
    SEVEN_PERMISSION_BOUNDARIES,
    SourceIdentityCustodyEntry,
    SourceReadinessPacket,
    build_closed_synthetic_d2_fixture_payload,
    build_source_readiness_packet,
    inspect_source_and_d2_readiness,
    verify_source_readiness_packet,
)


def test_workstream_b_closed_synthetic_d2_fixture_and_invariants() -> None:
    packet = build_source_readiness_packet()
    assert isinstance(packet, SourceReadinessPacket)

    # Mandatory Section 7 flags
    assert packet.real_source_inventory_executed is False
    assert packet.real_source_bytes_observed is False
    assert packet.real_source_rights_verified is False
    assert packet.d3_authorized_local_execution is False

    # D-2 30-field accounting: 0 VERIFIED, 7 PENDING, 21 BLOCKED, 2 NOT_OBSERVED
    d2_summary = packet.d2_readiness_summary
    assert d2_summary["verified_count"] == 0
    assert d2_summary["pending_count"] == 7
    assert d2_summary["blocked_count"] == 21
    assert d2_summary["not_observed_count"] == 2
    assert d2_summary["execution_authorized"] is False
    assert d2_summary["owner_approval_claimed"] is False

    # Duplicate content occurrences preserved without collapsing occurrence_id or revision_id
    assert packet.duplicate_occurrences_preserved is True
    assert packet.auto_deduplication_applied is False
    occ_ids = [e.source_occurrence_id for e in packet.identity_custody_entries]
    rev_ids = [e.source_revision_id for e in packet.identity_custody_entries]
    sha_vals = [e.source_sha256 for e in packet.identity_custody_entries]
    assert len(set(occ_ids)) == len(occ_ids)
    assert len(set(rev_ids)) == len(rev_ids)
    # At least two entries share an identical content SHA-256 while keeping distinct occurrence & revision IDs
    assert len(set(sha_vals)) < len(sha_vals)

    # All 7 permissions explicitly tracked and false for real archive operations
    assert set(packet.permission_matrix.keys()) == set(SEVEN_PERMISSION_BOUNDARIES)
    assert packet.permission_matrix[PERMISSION_DISCOVER_SOURCES] == "SYNTHETIC_FIXTURE_ONLY"
    assert packet.permission_matrix[PERMISSION_INSPECT_LOCAL_BYTES] == "NOT_AUTHORIZED"
    assert packet.permission_matrix[PERMISSION_CREATE_DERIVED_ARTIFACTS] == "SYNTHETIC_FIXTURE_ONLY"
    assert packet.permission_matrix[PERMISSION_RUN_AUTHENTIC_MODELS] == "NOT_AUTHORIZED"
    assert packet.permission_matrix[PERMISSION_PROVIDER_OR_CLOUD_EGRESS] == "FORBIDDEN_NO_EGRESS"
    assert packet.permission_matrix[PERMISSION_RETAIN_OUTPUTS] == "NOT_AUTHORIZED"
    assert packet.permission_matrix[PERMISSION_EXPORT_OUTPUTS] == "NOT_AUTHORIZED"

    # Owner input requirements packet is populated
    assert len(packet.owner_input_requirements["pending_evidence_fields"]) == 7
    assert len(packet.owner_input_requirements["blocked_ruling_fields"]) == 21
    assert len(packet.owner_input_requirements["observation_only_fields"]) == 2

    verified = verify_source_readiness_packet(packet)
    assert verified["packet_digest"] == packet.packet_digest


def test_workstream_b_refuses_identical_filename_as_byte_identity() -> None:
    pkt = inspect_source_and_d2_readiness(
        {
            "infer_byte_identity_from_filename": True,
            "filename_pair": ("rehearsal_act1.mov", "rehearsal_act1.mov"),
        }
    )
    assert pkt.status == ReadinessStatus.BLOCKED
    assert REFUSAL_FILENAME_EQUALITY_NOT_BYTE_IDENTITY in pkt.blockers


def test_workstream_b_refuses_duplicate_occurrence_collapse_or_auto_skip() -> None:
    pkt = inspect_source_and_d2_readiness(
        {
            "collapse_duplicate_sha256_occurrences": True,
        }
    )
    assert pkt.status == ReadinessStatus.BLOCKED
    assert REFUSAL_DUPLICATE_OCCURRENCE_COLLAPSE_FORBIDDEN in pkt.blockers


def test_workstream_b_refuses_forged_owner_attestation_and_d3_claims() -> None:
    pkt = inspect_source_and_d2_readiness(
        {
            "claim_forged_owner_attestation": True,
            "claim_d3_execution_authorized": True,
        }
    )
    assert pkt.status == ReadinessStatus.NOT_AUTHORIZED
    assert REFUSAL_FORGED_OWNER_ATTESTATION in pkt.blockers
    assert REFUSAL_D3_EXECUTION_NOT_AUTHORIZED in pkt.blockers
    assert pkt.summary["real_source_inventory_executed"] is False
    assert pkt.summary["real_source_bytes_observed"] is False
    assert pkt.summary["real_source_rights_verified"] is False
    assert pkt.summary["d3_authorized_local_execution"] is False


def test_workstream_b_refuses_discovery_granting_processing_or_model_or_export() -> None:
    pkt = inspect_source_and_d2_readiness(
        {
            "treat_discovery_as_processing_grant": True,
        }
    )
    assert pkt.status == ReadinessStatus.NOT_AUTHORIZED
    assert REFUSAL_DISCOVERY_DOES_NOT_GRANT_PROCESSING in pkt.blockers


def test_workstream_b_refuses_dev_eval_partition_leakage() -> None:
    d2_fixture = build_closed_synthetic_d2_fixture_payload()
    pkt = inspect_source_and_d2_readiness(
        {
            "d2_package": d2_fixture,
            "partition_check": {
                "development_revision_ids": ["rev-ballet-01", "rev-dev-01"],
                "evaluation_revision_ids": ["rev-ballet-01", "rev-eval-02"],
            },
        }
    )
    assert pkt.status == ReadinessStatus.BLOCKED
    assert REFUSAL_DEV_EVAL_PARTITION_LEAKAGE in pkt.blockers


def test_workstream_b_tampered_packet_is_rejected() -> None:
    packet = build_source_readiness_packet()
    raw = packet.to_dict()
    raw["real_source_bytes_observed"] = True
    with pytest.raises(VipLabError):
        verify_source_readiness_packet(raw)
