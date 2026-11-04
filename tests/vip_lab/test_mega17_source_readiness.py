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


def test_workstream_b_synthetic_dev_eval_partitions_are_disjoint_on_all_identity_axes() -> None:
    fixture = build_closed_synthetic_d2_fixture_payload()
    corpus = fixture["artifacts"]["corpus-designation.json"]
    query_doc = fixture["artifacts"]["editor-queries.json"]
    revisions = corpus["revisions"]
    development_revisions = [row for row in revisions if row["split"] == "DEVELOPMENT"]
    evaluation_revisions = [row for row in revisions if row["split"] == "EVALUATION"]
    development_sessions = {row["session_id"] for row in development_revisions}
    evaluation_sessions = {row["session_id"] for row in evaluation_revisions}
    development_queries = [
        row for row in query_doc["queries"] if row["split"] == "DEVELOPMENT"
    ]
    evaluation_queries = [
        row for row in query_doc["queries"] if row["split"] == "EVALUATION"
    ]

    assert development_sessions.isdisjoint(evaluation_sessions)
    assert {row["revision_id"] for row in development_revisions}.isdisjoint(
        row["revision_id"] for row in evaluation_revisions
    )
    packet = build_source_readiness_packet()
    development_content = {
        row.source_content_id
        for row in packet.identity_custody_entries
        if row.partition_split == "DEVELOPMENT"
    }
    evaluation_content = {
        row.source_content_id
        for row in packet.identity_custody_entries
        if row.partition_split == "EVALUATION"
    }
    assert development_content.isdisjoint(evaluation_content)
    assert {row["query_id"] for row in development_queries}.isdisjoint(
        row["query_id"] for row in evaluation_queries
    )
    assert {row["text"] for row in development_queries}.isdisjoint(
        row["text"] for row in evaluation_queries
    )
    assert packet.dev_eval_partition_disjoint is True


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


@pytest.mark.parametrize(
    ("development_key", "evaluation_key"),
    [
        ("development_session_ids", "evaluation_session_ids"),
        ("development_content_ids", "evaluation_content_ids"),
        ("development_query_ids", "evaluation_query_ids"),
        ("development_query_text_ids", "evaluation_query_text_ids"),
    ],
)
def test_workstream_b_refuses_cross_partition_identity_overlap(
    development_key: str, evaluation_key: str
) -> None:
    pkt = inspect_source_and_d2_readiness(
        {
            "partition_check": {
                "development_revision_ids": ["rev-development"],
                "evaluation_revision_ids": ["rev-evaluation"],
                development_key: ["shared-identity"],
                evaluation_key: ["shared-identity"],
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
