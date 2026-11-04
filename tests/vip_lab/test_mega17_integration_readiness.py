"""Tests for MEGA-17 Workstream A: LAB-to-Canonical Integration Readiness."""

from __future__ import annotations

from pathlib import Path
import pytest

from vip_lab.common import ReadinessStatus, VipLabError
from vip_lab.mega17.canonical_integration import (
    CANONICAL_INTEGRATION_SCHEMA_VERSION,
    CANONICAL_MAIN_REFERENCE_SHA,
    DECLARED_LAB_PR1_REPAIR_SHA,
    INTEGRATION_CATEGORIES,
    REQUIRED_GATE0_MEDIA_MODULES,
    REFUSAL_CANONICAL_ADOPTION_NOT_AUTHORIZED,
    REFUSAL_CANONICAL_INTEGRATION_NOT_EXECUTED,
    REFUSAL_CANONICAL_MAIN_MUTATION_FORBIDDEN,
    REFUSAL_TRANSPLANT_CONFLICT_DETECTED,
    CanonicalIntegrationReadinessPacket,
    build_canonical_integration_readiness,
    detect_transplant_conflicts,
    inspect_canonical_integration_gate,
    verify_canonical_integration_readiness,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


def test_workstream_a_inventory_covers_mega03_through_mega16_and_gate0_media() -> None:
    packet = build_canonical_integration_readiness(WORKSPACE_ROOT)
    assert isinstance(packet, CanonicalIntegrationReadinessPacket)
    assert packet.schema_version == CANONICAL_INTEGRATION_SCHEMA_VERSION
    assert packet.canonical_reference_sha == CANONICAL_MAIN_REFERENCE_SHA
    assert packet.declared_lab_baseline_sha == DECLARED_LAB_PR1_REPAIR_SHA
    assert packet.workspace_git_sha == "NOT_OBSERVED"

    # Hard required flags from Section 6
    assert packet.canonical_integration_executed is False
    assert packet.canonical_main_modified is False
    assert packet.canonical_adoption_authorized is False
    assert packet.gate0_media_modules_intact is True

    # Verify all 6 src/gate0/media modules are inventoried and present
    media_paths = {m.relative_path for m in packet.gate0_media_inventory if m.exists}
    assert media_paths == set(REQUIRED_GATE0_MEDIA_MODULES)

    # Verify MEGA-03 through MEGA-16 packages are all inventoried
    inventoried_paths = {item.relative_path for item in packet.module_classifications}
    for wave_num in range(3, 17):
        prefix = f"src/vip_lab/mega{wave_num:02d}/"
        assert any(p.startswith(prefix) for p in inventoried_paths), f"Missing {prefix}"
        test_path = f"tests/vip_lab/test_mega{wave_num:02d}.py"
        assert test_path in inventoried_paths, f"Missing {test_path}"

    # Every classification must belong to the closed category set
    for item in packet.module_classifications:
        assert item.category in INTEGRATION_CATEGORIES
        assert item.exists is True
        assert len(item.file_sha256) == 64

    # Integration wave sequence must be non-empty and ordered
    assert len(packet.integration_sequence) >= 4
    wave_orders = [w.wave_order for w in packet.integration_sequence]
    assert wave_orders == sorted(wave_orders)

    verified = verify_canonical_integration_readiness(packet)
    assert verified["packet_digest"] == packet.packet_digest


def test_workstream_a_transplant_conflict_detector_catches_collisions_and_pr_overlaps() -> None:
    # 1. Duplicate path collision
    conflicts_dup = detect_transplant_conflicts(
        candidate_paths=(
            "src/vip_lab/mega17/canonical_integration.py",
            "src/vip_lab/mega17/canonical_integration.py",
        ),
        workspace_root=WORKSPACE_ROOT,
    )
    assert any(c.conflict_code == "DUPLICATE_CANDIDATE_PATH" for c in conflicts_dup)

    # 2. Forbidden canonical overwrite (e.g., mutating src/gate3/refinement.py or src/gate0/media/probe.py)
    conflicts_canonical = detect_transplant_conflicts(
        candidate_paths=("src/gate3/refinement.py", "src/gate0/media/probe.py"),
        workspace_root=WORKSPACE_ROOT,
    )
    codes = {c.conflict_code for c in conflicts_canonical}
    assert "CANONICAL_CORE_OVERWRITE_FORBIDDEN" in codes
    assert "GATE0_MEDIA_SAFEGUARD_MODIFICATION_FORBIDDEN" in codes

    # 3. PR #258 / PR #259 overlap detection
    conflicts_pr = detect_transplant_conflicts(
        candidate_paths=("src/vip_lab/mega17/canonical_integration.py",),
        claimed_pr_transplants=("PR#258", "PR#259"),
        workspace_root=WORKSPACE_ROOT,
    )
    assert any(c.conflict_code == "UNOBSERVED_EXTERNAL_PR_OVERLAP" for c in conflicts_pr)


def test_workstream_a_refuses_canonical_completion_or_main_mutation_claims() -> None:
    pkt = inspect_canonical_integration_gate(
        {
            "workspace_root": str(WORKSPACE_ROOT),
            "claim_canonical_integration_executed": True,
            "claim_canonical_main_modified": True,
            "claim_canonical_adoption_authorized": True,
        }
    )
    assert pkt.status == ReadinessStatus.NOT_AUTHORIZED
    assert REFUSAL_CANONICAL_INTEGRATION_NOT_EXECUTED in pkt.blockers
    assert REFUSAL_CANONICAL_MAIN_MUTATION_FORBIDDEN in pkt.blockers
    assert REFUSAL_CANONICAL_ADOPTION_NOT_AUTHORIZED in pkt.blockers
    assert pkt.summary["canonical_integration_executed"] is False
    assert pkt.summary["canonical_main_modified"] is False
    assert pkt.summary["canonical_adoption_authorized"] is False


def test_workstream_a_refuses_candidate_with_transplant_conflicts() -> None:
    pkt = inspect_canonical_integration_gate(
        {
            "workspace_root": str(WORKSPACE_ROOT),
            "candidate_paths": ["src/gate0/d2_intake.py"],
        }
    )
    assert pkt.status == ReadinessStatus.BLOCKED
    assert REFUSAL_TRANSPLANT_CONFLICT_DETECTED in pkt.blockers


def test_workstream_a_tampered_digest_is_refused() -> None:
    packet = build_canonical_integration_readiness(WORKSPACE_ROOT)
    d = packet.to_dict()
    d["canonical_integration_executed"] = True
    with pytest.raises(VipLabError) as exc_info:
        verify_canonical_integration_readiness(d)
    assert exc_info.value.code in (
        "CANONICAL_INTEGRATION_INVARIANT_VIOLATION",
        "CANONICAL_INTEGRATION_DIGEST_MISMATCH",
    )
