"""MEGA-08 Regression Tests: Deterministic Capability & Gap Inventory (Packet P08).

Covers:
1. Static AST-based module inventory over allowlisted repository paths without importing
   inspected modules at inventory time.
2. Exact classification of capabilities into IMPLEMENTED_IN_SOURCE, COVERED_SYNTHETIC,
   GAP_CODE_CAPABLE, BLOCKED_BY_AUTHORITY, and NOT_OBSERVED.
3. Read-only WBS / H3 advisory mapping with ``advisory_status="ADVISORY_ONLY"`` and
   ``scheduler_state_mutated=False``.
4. Stretch S1 (D-2 30-field readiness crosswalk), S4 (SigLIP2 3-profile & provisional
   tokenizer crosswalk), and S5 (A-7 S5 test-only resource profile crosswalk).
5. Fail-closed refusal of path traversal, non-allowlisted directories, duplicate
   capability IDs, missing expected symbols, forged PR #258 presence, and forged
   Gate/Owner authority claims.
6. Canonical JSON digest stability across repeated runs.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from vip_lab.common import (
    NOT_OBSERVED,
    ReadinessStatus,
    VipLabError,
    canonical_json_dumps,
)
from vip_lab.mega08 import (
    ALLOWED_INVENTORY_PREFIXES,
    CANONICAL_CAPABILITY_CLASSES,
    DECLARED_BASELINE_REVISION,
    CANONICAL_VIP_REFERENCE_SHA,
    CapabilityEntry,
    CapabilityInventoryReport,
    ModuleSymbolRecord,
    build_capability_inventory,
    compute_gap_digest,
    inspect_capability_gate,
    inspect_module_symbols_ast,
    verify_gap_digest,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_allowed_prefixes_and_capability_classes_are_closed() -> None:
    assert CANONICAL_CAPABILITY_CLASSES == frozenset(
        {
            "IMPLEMENTED_IN_SOURCE",
            "COVERED_SYNTHETIC",
            "GAP_CODE_CAPABLE",
            "BLOCKED_BY_AUTHORITY",
            "NOT_OBSERVED",
        }
    )
    assert "src/vip_fvs/" in ALLOWED_INVENTORY_PREFIXES
    assert "src/vip_lab/" in ALLOWED_INVENTORY_PREFIXES
    assert "src/gate0/" in ALLOWED_INVENTORY_PREFIXES
    assert "src/gate2/" in ALLOWED_INVENTORY_PREFIXES
    assert "src/gate3/" in ALLOWED_INVENTORY_PREFIXES
    assert "external/" not in ALLOWED_INVENTORY_PREFIXES


def test_ast_symbol_inspection_extracts_classes_functions_and_constants_without_exec() -> None:
    rec = inspect_module_symbols_ast(
        REPO_ROOT,
        "src/vip_fvs/synthetic_profiles.py",
        expected_symbols=(
            "CLOSED_SYNTHETIC_PROFILE_IDS",
            "V1_PROFILE_ID",
            "V2_BASE_PROFILE_ID",
            "V2_SO400M_PROFILE_ID",
            "SyntheticProfileBundle",
            "build_synthetic_profile_runtime",
            "make_synthetic_profile",
        ),
    )
    assert isinstance(rec, ModuleSymbolRecord)
    assert rec.relative_path == "src/vip_fvs/synthetic_profiles.py"
    assert rec.exists is True
    assert len(rec.file_sha256) == 64
    assert rec.missing_symbols == ()
    assert "CLOSED_SYNTHETIC_PROFILE_IDS" in rec.exported_symbols
    assert "SyntheticProfileBundle" in rec.exported_symbols
    assert "build_synthetic_profile_runtime" in rec.exported_symbols


def test_ast_symbol_inspection_detects_missing_expected_symbol() -> None:
    rec = inspect_module_symbols_ast(
        REPO_ROOT,
        "src/vip_fvs/synthetic_profiles.py",
        expected_symbols=("CLOSED_SYNTHETIC_PROFILE_IDS", "CLOSED_PROFILE_IDS_NONEXISTENT"),
    )
    assert rec.exists is True
    assert rec.missing_symbols == ("CLOSED_PROFILE_IDS_NONEXISTENT",)


def test_build_capability_inventory_is_deterministic_and_digest_verified() -> None:
    report_a = build_capability_inventory(REPO_ROOT)
    report_b = build_capability_inventory(REPO_ROOT)

    assert isinstance(report_a, CapabilityInventoryReport)
    assert report_a.workspace_git_sha == NOT_OBSERVED
    assert report_a.declared_baseline_revision == DECLARED_BASELINE_REVISION
    assert report_a.canonical_reference_sha == CANONICAL_VIP_REFERENCE_SHA
    assert report_a.synthetic_only is True
    assert report_a.execution_authorized is False
    assert report_a.inventory_digest == report_b.inventory_digest
    assert canonical_json_dumps(report_a.to_dict()) == canonical_json_dumps(report_b.to_dict())
    assert verify_gap_digest(report_a.to_dict()) is True


def test_capability_matrix_classifies_implemented_code_capable_and_authority_blocked() -> None:
    report = build_capability_inventory(REPO_ROOT)
    by_id = {entry.capability_id: entry for entry in report.capability_matrix}

    assert by_id["VIP_FVS_QUERY_BATCH_W1"].classification == "IMPLEMENTED_IN_SOURCE"
    assert by_id["VIP_FVS_SYNTHETIC_PROFILES_W2"].classification == "IMPLEMENTED_IN_SOURCE"
    assert by_id["VIP_FVS_BATCH_RETRIEVAL_W3"].classification == "IMPLEMENTED_IN_SOURCE"
    assert by_id["VIP_FVS_THREE_ARM_BATCH_W4"].classification == "IMPLEMENTED_IN_SOURCE"
    assert by_id["VIP_FVS_BATCH_REPORT_W5"].classification == "IMPLEMENTED_IN_SOURCE"
    assert by_id["VIP_LAB_MEGA03_TO_07_PREFLIGHT"].classification == "COVERED_SYNTHETIC"

    # Lab code-capable waves P08..P14
    assert by_id["LAB_MEGA09_CANDIDATE_REVIEW_QUEUE"].classification in {
        "GAP_CODE_CAPABLE",
        "IMPLEMENTED_IN_SOURCE",
        "COVERED_SYNTHETIC",
    }

    # Authority-blocked boundaries must always remain BLOCKED_BY_AUTHORITY
    assert by_id["GATE3_A7_S5_T1_BOUNDED_ADMISSION_PR258"].classification == "BLOCKED_BY_AUTHORITY"
    assert by_id["GATE3_A7_POSITIVE_STREAM_MAPPING"].classification == "BLOCKED_BY_AUTHORITY"
    assert by_id["GATE0_D3_REAL_CORPUS_EXPERIMENT"].classification == "BLOCKED_BY_AUTHORITY"
    assert by_id["GATE1_AUTHENTIC_MODEL_WEIGHTS_BENCHMARK"].classification == "BLOCKED_BY_AUTHORITY"
    assert by_id["GATE2_REAL_ARCHIVE_WORKLOAD_SCALE"].classification == "BLOCKED_BY_AUTHORITY"
    assert by_id["GATE3_PRODUCTION_RENDER_EXPORT"].classification == "BLOCKED_BY_AUTHORITY"


def test_wbs_h3_advisory_map_and_stretch_crosswalks_are_read_only() -> None:
    report = build_capability_inventory(REPO_ROOT)
    wbs_map = report.wbs_h3_advisory_map
    assert wbs_map["advisory_status"] == "ADVISORY_ONLY"
    assert wbs_map["scheduler_state_mutated"] is False
    assert wbs_map["wbs_checkboxes_mutated"] is False
    entries = {row["target_id"]: row for row in wbs_map["mappings"]}
    assert "G0.1.4" in entries
    assert "G1.1.4" in entries
    assert "G2.1.3" in entries
    assert "G3.1.5" in entries
    assert "H3-C05" in entries
    assert "H3-A04" in entries
    assert "A-7-S5" in entries

    stretch = report.stretch_advisory_crosswalks
    s1 = stretch["S1_d2_readiness_crosswalk"]
    assert s1["total_fields"] == 30
    assert s1["verified_count"] == 0
    assert s1["pending_count"] == 7
    assert s1["blocked_count"] == 21
    assert s1["not_observed_count"] == 2
    assert s1["authenticity"] == "DECLARED_NOT_AUTHENTICATED"
    assert s1["execution_authorized"] is False

    s4 = stretch["S4_siglip2_contract_crosswalk"]
    assert len(s4["profiles"]) == 3
    assert len({p["space_id"] for p in s4["profiles"]}) == 3
    assert s4["gate_b_status"] == "NO_GO_BLOCKED"
    assert s4["authentic_weights_loaded"] is False

    s5 = stretch["S5_a7_s5_test_resource_crosswalk"]
    assert s5["reader_unit_source_cap_bytes"] == 4096
    assert s5["integrated_synthetic_source_cap_bytes"] == 8 * 1024 * 1024
    assert s5["timing_sample_cap"] == 20000
    assert s5["refuse_at_sample_count"] == 20001
    assert s5["production_resource_budget"] == "PENDING_EVIDENCE"
    assert s5["implementation_authorized"] is False
    assert s5["pr258_merged_in_snapshot"] is False


def test_contract_gate_rejects_path_traversal_and_non_allowlisted_paths() -> None:
    with pytest.raises(VipLabError) as exc_info:
        inspect_module_symbols_ast(REPO_ROOT, "../outside.py")
    assert exc_info.value.code == "INVENTORY_PATH_TRAVERSAL_REFUSED"

    with pytest.raises(VipLabError) as exc_info2:
        inspect_module_symbols_ast(REPO_ROOT, "external/some_vendor_file.py")
    assert exc_info2.value.code == "INVENTORY_PATH_NOT_ALLOWLISTED"

    with pytest.raises(VipLabError) as exc_info3:
        inspect_module_symbols_ast(REPO_ROOT, "/etc/passwd")
    assert exc_info3.value.code == "INVENTORY_ABSOLUTE_PATH_REFUSED"

    # Governance decision docs are never permitted as Python AST module targets
    with pytest.raises(VipLabError) as exc_info4:
        inspect_module_symbols_ast(
            REPO_ROOT,
            "docs/decisions/2026-10-29-a7-s5-scoped-synthetic-tdd-plan-owner-adoption.md",
        )
    assert exc_info4.value.code == "INVENTORY_PATH_NOT_ALLOWLISTED"

    # Unlisted docs or external files in custom_capabilities are refused
    bad_cap_pkt = inspect_capability_gate(
        {
            "workspace_root": str(REPO_ROOT),
            "custom_capabilities": [
                {
                    "capability_id": "UNLISTED_DOC_CAP",
                    "title": "Unlisted Doc Reference",
                    "gate": "G3",
                    "classification": "BLOCKED_BY_AUTHORITY",
                    "evidence_state": NOT_OBSERVED,
                    "source_paths": ["docs/decisions/unlisted-arbitrary-doc.md"],
                    "authority_blocker": "TEST_BLOCKER",
                }
            ],
        }
    )
    assert bad_cap_pkt.status == ReadinessStatus.INVALID
    assert "INVENTORY_PATH_NOT_ALLOWLISTED" in bad_cap_pkt.blockers


def test_contract_gate_rejects_duplicate_capability_ids() -> None:
    dup_entry = CapabilityEntry(
        capability_id="DUP_CAP_01",
        title="Duplicate Capability",
        gate="G3",
        classification="COVERED_SYNTHETIC",
        evidence_state=NOT_OBSERVED,
        source_paths=("src/vip_fvs/query_batch.py",),
        authority_blocker=None,
    )
    pkt = inspect_capability_gate(
        {
            "workspace_root": str(REPO_ROOT),
            "custom_capabilities": [dup_entry.to_dict(), dup_entry.to_dict()],
        }
    )
    assert pkt.status == ReadinessStatus.INVALID
    assert "CAPABILITY_INVENTORY_DUPLICATE_ID" in pkt.blockers


def test_contract_gate_refuses_forged_pr258_or_gate_promotion_claims() -> None:
    pkt = inspect_capability_gate(
        {
            "workspace_root": str(REPO_ROOT),
            "pr258_present": True,
            "gate0_passed": True,
            "approved": True,
        }
    )
    assert pkt.status in (ReadinessStatus.BLOCKED, ReadinessStatus.NOT_AUTHORIZED)
    assert "PR258_FORGED_PRESENCE_REFUSED" in pkt.blockers
    assert "FORGED_GATE_PROMOTION_REFUSED" in pkt.blockers
    assert "UNTRUSTED_AUTHORITY_FLAGS_IGNORED" in pkt.reasons


def test_gap_digest_tampering_is_detected() -> None:
    report = build_capability_inventory(REPO_ROOT)
    payload = report.to_dict()
    assert compute_gap_digest(payload) == report.inventory_digest

    tampered = dict(payload)
    tampered["workspace_git_sha"] = "592952daf475b1bbae2eebdee64d992c1a744f08"
    with pytest.raises(VipLabError) as exc_info:
        verify_gap_digest(tampered)
    assert exc_info.value.code == "GAP_DIGEST_MISMATCH"
