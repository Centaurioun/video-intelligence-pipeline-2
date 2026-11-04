"""MEGA-17 Workstream A: LAB-to-Canonical Integration Readiness (Roadmap Step 2).

Provides a source-backed inventory of MEGA-03 through MEGA-16 modules and tests,
classifies each module for canonical integration safety, detects transplant conflicts
(duplicate paths, symbol collisions, PR #258 / PR #259 overlap, `.gitignore` `media/`
hazard, forbidden canonical core overwrites), proposes a non-destructive integration
sequence, and refuses any premature claim that canonical integration has been executed.

Hard invariants:
- ``canonical_integration_executed == False``
- ``canonical_main_modified == False``
- ``canonical_adoption_authorized == False``
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from vip_lab.common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    canonical_sha256,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)
from vip_lab.mega08.capability_inventory import (
    CANONICAL_VIP_REFERENCE_SHA,
    ModuleSymbolRecord,
    inspect_module_symbols_ast,
    validate_allowlisted_relative_path,
)


STAGE_ID = "MEGA-17.WORKSTREAM_A_CANONICAL_INTEGRATION_READINESS"
CANONICAL_INTEGRATION_SCHEMA_VERSION = "vip_lab.mega17.canonical_integration_readiness.v1"
CANONICAL_MAIN_REFERENCE_SHA = CANONICAL_VIP_REFERENCE_SHA
DECLARED_LAB_PR1_REPAIR_SHA = "85a4190925fbb2c6ca11c4b354ad9f1296daf82f"

CATEGORY_ADDITIVE_SAFE = "ADDITIVE_SAFE"
CATEGORY_OVERLAPPING_RECONCILIATION = "OVERLAPPING_REQUIRES_RECONCILIATION"
CATEGORY_INCOMPATIBLE = "INCOMPATIBLE_WITHOUT_AMENDMENT"
CATEGORY_SYNTHETIC_ONLY_HARNESS = "SYNTHETIC_ONLY_LAB_HARNESS"
CATEGORY_OWNER_GATED_DECISION = "OWNER_GATED_CANONICAL_DECISION"

INTEGRATION_CATEGORIES: frozenset[str] = frozenset(
    {
        CATEGORY_ADDITIVE_SAFE,
        CATEGORY_OVERLAPPING_RECONCILIATION,
        CATEGORY_INCOMPATIBLE,
        CATEGORY_SYNTHETIC_ONLY_HARNESS,
        CATEGORY_OWNER_GATED_DECISION,
    }
)

REFUSAL_CANONICAL_INTEGRATION_NOT_EXECUTED = "REFUSAL_CANONICAL_INTEGRATION_NOT_EXECUTED"
REFUSAL_CANONICAL_MAIN_MUTATION_FORBIDDEN = "REFUSAL_CANONICAL_MAIN_MUTATION_FORBIDDEN"
REFUSAL_CANONICAL_ADOPTION_NOT_AUTHORIZED = "REFUSAL_CANONICAL_ADOPTION_NOT_AUTHORIZED"
REFUSAL_TRANSPLANT_CONFLICT_DETECTED = "REFUSAL_TRANSPLANT_CONFLICT_DETECTED"
REFUSAL_GATE0_MEDIA_MODULES_MISSING = "REFUSAL_GATE0_MEDIA_MODULES_MISSING"

REQUIRED_GATE0_MEDIA_MODULES: tuple[str, ...] = (
    "src/gate0/media/__init__.py",
    "src/gate0/media/decode.py",
    "src/gate0/media/probe.py",
    "src/gate0/media/proc.py",
    "src/gate0/media/source_guard.py",
    "src/gate0/media/tool_identity.py",
)

FORBIDDEN_CANONICAL_OVERWRITE_PREFIXES: tuple[str, ...] = (
    "src/gate0/",
    "src/gate1/",
    "src/gate2/",
    "src/gate3/",
    "src/vip_fvs/",
    "src/persistent_local_index/",
)

UNOBSERVED_EXTERNAL_PRS: frozenset[str] = frozenset(
    {"PR#258", "PR #258", "258", "PR#259", "PR #259", "259"}
)

# Complete source-backed catalog of MEGA-03 through MEGA-16 modules and tests
MEGA03_TO_16_MODULE_CATALOG: tuple[tuple[str, str, str], ...] = (
    ("src/vip_lab/common.py", "MEGA-03..16", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/integration.py", "MEGA-03..07", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/cli.py", "MEGA-03..07", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega03/__init__.py", "MEGA-03", CATEGORY_OWNER_GATED_DECISION),
    ("src/vip_lab/mega03/s5_preflight.py", "MEGA-03", CATEGORY_OWNER_GATED_DECISION),
    ("src/vip_lab/mega03/stream_identity_preflight.py", "MEGA-03", CATEGORY_OWNER_GATED_DECISION),
    ("src/vip_lab/mega03/review_bundle_check.py", "MEGA-03", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega04/__init__.py", "MEGA-04", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega04/d2_readiness.py", "MEGA-04", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega04/query_review_preflight.py", "MEGA-04", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega04/experiment_readiness.py", "MEGA-04", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega05/__init__.py", "MEGA-05", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega05/model_assets.py", "MEGA-05", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega05/runtime_authority.py", "MEGA-05", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega05/benchmark_entry.py", "MEGA-05", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega06/__init__.py", "MEGA-06", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega06/workload_plan.py", "MEGA-06", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega06/recovery_matrix.py", "MEGA-06", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega06/measurement_review.py", "MEGA-06", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega07/__init__.py", "MEGA-07", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega07/candidate_temporal_gate.py", "MEGA-07", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega07/editorial_lineage.py", "MEGA-07", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega07/qc_export_readiness.py", "MEGA-07", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega08/__init__.py", "MEGA-08", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega08/capability_inventory.py", "MEGA-08", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega08/gap_digest.py", "MEGA-08", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega08/contract_gate.py", "MEGA-08", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega09/__init__.py", "MEGA-09", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega09/candidate_queue.py", "MEGA-09", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega09/queue_validation.py", "MEGA-09", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega09/review_intake.py", "MEGA-09", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega10/__init__.py", "MEGA-10", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega10/temporal_request.py", "MEGA-10", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega10/pts_fixture_diagnostics.py", "MEGA-10", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega10/measurement_boundary.py", "MEGA-10", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega11/__init__.py", "MEGA-11", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega11/editorial_proposal.py", "MEGA-11", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega11/proposal_revisions.py", "MEGA-11", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega11/decision_boundary.py", "MEGA-11", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega12/__init__.py", "MEGA-12", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega12/replay_graph.py", "MEGA-12", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega12/fault_scenarios.py", "MEGA-12", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega12/consistency_review.py", "MEGA-12", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega13/__init__.py", "MEGA-13", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega13/lineage_audit.py", "MEGA-13", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega13/qc_readiness.py", "MEGA-13", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega13/release_blockers.py", "MEGA-13", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega14/__init__.py", "MEGA-14", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("src/vip_lab/mega14/scenario.py", "MEGA-14", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("src/vip_lab/mega14/report.py", "MEGA-14", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("src/vip_lab/mega14/orchestrator.py", "MEGA-14", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("src/vip_lab/mega14/cli.py", "MEGA-14", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("src/vip_lab/mega15/__init__.py", "MEGA-15", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega15/temporal_preflight.py", "MEGA-15", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega15/editorial_handoff.py", "MEGA-15", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega15/lineage.py", "MEGA-15", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega16/__init__.py", "MEGA-16", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega16/render_preflight.py", "MEGA-16", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega16/qc_requirements.py", "MEGA-16", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega16/release_refusal.py", "MEGA-16", CATEGORY_ADDITIVE_SAFE),
    ("src/vip_lab/mega16/cli.py", "MEGA-16", CATEGORY_ADDITIVE_SAFE),
    ("tests/vip_lab/test_mega03.py", "MEGA-03", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega04.py", "MEGA-04", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega05.py", "MEGA-05", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega06.py", "MEGA-06", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega07.py", "MEGA-07", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega08.py", "MEGA-08", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega09.py", "MEGA-09", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega10.py", "MEGA-10", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega11.py", "MEGA-11", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega12.py", "MEGA-12", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega13.py", "MEGA-13", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega14.py", "MEGA-14", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega08_14_end_to_end.py", "MEGA-08..14", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega15.py", "MEGA-15", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega16.py", "MEGA-16", CATEGORY_SYNTHETIC_ONLY_HARNESS),
    ("tests/vip_lab/test_mega15_16_end_to_end.py", "MEGA-15..16", CATEGORY_SYNTHETIC_ONLY_HARNESS),
)


@dataclass(frozen=True)
class ModuleIntegrationClassification:
    """Classification of one LAB module/test for future canonical integration."""

    relative_path: str
    wave_origin: str
    category: str
    exists: bool
    file_sha256: str
    symbol_count: int
    exported_symbols: tuple[str, ...]
    canonical_conflict_risk: str
    notes: str

    def __post_init__(self) -> None:
        if self.category not in INTEGRATION_CATEGORIES:
            raise VipLabError(
                "CANONICAL_INTEGRATION_CATEGORY_INVALID",
                f"Invalid integration category: {self.category!r}",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "relative_path": self.relative_path,
            "wave_origin": self.wave_origin,
            "category": self.category,
            "exists": self.exists,
            "file_sha256": self.file_sha256,
            "symbol_count": self.symbol_count,
            "exported_symbols": list(self.exported_symbols),
            "canonical_conflict_risk": self.canonical_conflict_risk,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class TransplantConflictRecord:
    """One detected transplant conflict or governance hazard."""

    conflict_code: str
    severity: str
    affected_paths: tuple[str, ...]
    remediation_required: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_code": self.conflict_code,
            "severity": self.severity,
            "affected_paths": list(self.affected_paths),
            "remediation_required": self.remediation_required,
        }


@dataclass(frozen=True)
class IntegrationWaveProposal:
    """One non-destructive step in the proposed LAB-to-canonical integration order."""

    wave_order: int
    wave_id: str
    title: str
    included_prefixes: tuple[str, ...]
    prerequisites: tuple[str, ...]
    requires_separate_owner_grant: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "wave_order": self.wave_order,
            "wave_id": self.wave_id,
            "title": self.title,
            "included_prefixes": list(self.included_prefixes),
            "prerequisites": list(self.prerequisites),
            "requires_separate_owner_grant": self.requires_separate_owner_grant,
        }


@dataclass(frozen=True)
class CanonicalIntegrationReadinessPacket:
    """Immutable Workstream A readiness packet."""

    schema_version: str
    workspace_git_sha: str
    declared_lab_baseline_sha: str
    canonical_reference_sha: str
    canonical_integration_executed: bool
    canonical_main_modified: bool
    canonical_adoption_authorized: bool
    gate0_media_modules_intact: bool
    gate0_media_inventory: tuple[ModuleSymbolRecord, ...]
    module_classifications: tuple[ModuleIntegrationClassification, ...]
    transplant_conflicts: tuple[TransplantConflictRecord, ...]
    integration_sequence: tuple[IntegrationWaveProposal, ...]
    packet_digest: str

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "workspace_git_sha": self.workspace_git_sha,
            "declared_lab_baseline_sha": self.declared_lab_baseline_sha,
            "canonical_reference_sha": self.canonical_reference_sha,
            "canonical_integration_executed": self.canonical_integration_executed,
            "canonical_main_modified": self.canonical_main_modified,
            "canonical_adoption_authorized": self.canonical_adoption_authorized,
            "gate0_media_modules_intact": self.gate0_media_modules_intact,
            "gate0_media_inventory": [m.to_dict() for m in self.gate0_media_inventory],
            "module_classifications": [m.to_dict() for m in self.module_classifications],
            "transplant_conflicts": [c.to_dict() for c in self.transplant_conflicts],
            "integration_sequence": [w.to_dict() for w in self.integration_sequence],
        }

    def to_dict(self) -> dict[str, Any]:
        out = self.payload_without_digest()
        out["packet_digest"] = self.packet_digest
        return out


def detect_transplant_conflicts(
    *,
    candidate_paths: Sequence[str] = (),
    claimed_pr_transplants: Sequence[str] = (),
    workspace_root: str | Path | None = None,
) -> tuple[TransplantConflictRecord, ...]:
    """Detect path collisions, canonical core overwrites, PR #258/#259 overlaps, and `.gitignore` hazards."""
    root = (
        Path(workspace_root).resolve()
        if workspace_root is not None
        else Path(__file__).resolve().parents[3]
    )
    conflicts: list[TransplantConflictRecord] = []

    seen: set[str] = set()
    duplicates: set[str] = set()
    for raw_p in candidate_paths:
        clean_p = str(raw_p).strip().replace("\\", "/")
        if clean_p in seen:
            duplicates.add(clean_p)
        seen.add(clean_p)

        if clean_p in REQUIRED_GATE0_MEDIA_MODULES:
            conflicts.append(
                TransplantConflictRecord(
                    conflict_code="GATE0_MEDIA_SAFEGUARD_MODIFICATION_FORBIDDEN",
                    severity="CRITICAL",
                    affected_paths=(clean_p,),
                    remediation_required="Preserve all six src/gate0/media modules verbatim without modification or omission.",
                )
            )
        elif any(clean_p.startswith(pfx) for pfx in FORBIDDEN_CANONICAL_OVERWRITE_PREFIXES):
            conflicts.append(
                TransplantConflictRecord(
                    conflict_code="CANONICAL_CORE_OVERWRITE_FORBIDDEN",
                    severity="HIGH",
                    affected_paths=(clean_p,),
                    remediation_required="Keep LAB changes additive under src/vip_lab/ and tests/vip_lab/ unless a separate canonical amendment authorizes core changes.",
                )
            )

    if duplicates:
        conflicts.append(
            TransplantConflictRecord(
                conflict_code="DUPLICATE_CANDIDATE_PATH",
                severity="HIGH",
                affected_paths=tuple(sorted(duplicates)),
                remediation_required="Deduplicate candidate transplant file list so every path has a single authoritative owner.",
            )
        )

    for pr_claim in claimed_pr_transplants:
        norm = str(pr_claim).strip().upper()
        if norm in UNOBSERVED_EXTERNAL_PRS or "258" in norm or "259" in norm:
            conflicts.append(
                TransplantConflictRecord(
                    conflict_code="UNOBSERVED_EXTERNAL_PR_OVERLAP",
                    severity="CRITICAL",
                    affected_paths=(str(pr_claim),),
                    remediation_required="Do not transplant or overwrite PR #258 (A-7 S5-T1 admission) or PR #259 (continuity handoff) without explicit source-level reconciliation.",
                )
            )

    # Check if any of the 6 gate0/media modules are missing on disk
    missing_media = [
        rel for rel in REQUIRED_GATE0_MEDIA_MODULES if not (root / rel).is_file()
    ]
    if missing_media:
        conflicts.append(
            TransplantConflictRecord(
                conflict_code="MISSING_GATE0_MEDIA_MODULES",
                severity="CRITICAL",
                affected_paths=tuple(missing_media),
                remediation_required="Restore all 6 src/gate0/media modules before any integration or CI run.",
            )
        )

    # Inspect .gitignore for unanchored 'media/' line hazard
    gitignore_path = root / ".gitignore"
    if gitignore_path.is_file():
        lines = [ln.strip() for ln in gitignore_path.read_text(encoding="utf-8").splitlines()]
        if "media/" in lines:
            conflicts.append(
                TransplantConflictRecord(
                    conflict_code="UNANCHORED_GITIGNORE_MEDIA_PATTERN_IN_CONTAINER",
                    severity="ADVISORY_GUARDRAIL",
                    affected_paths=(".gitignore", "src/gate0/media/"),
                    remediation_required="Ensure GitHub branch retains anchored '/media/' from PR #1 and never overwrite .gitignore from an unanchored ZIP snapshot.",
                )
            )

    return tuple(conflicts)


def _default_integration_sequence() -> tuple[IntegrationWaveProposal, ...]:
    return (
        IntegrationWaveProposal(
            wave_order=1,
            wave_id="WAVE_1_PURE_LAB_PACKAGE",
            title="Additive import of src/vip_lab/ (common, integration, mega03..mega17)",
            included_prefixes=("src/vip_lab/",),
            prerequisites=(
                "Verify all 6 src/gate0/media/*.py modules remain tracked",
                "Verify .gitignore uses anchored '/media/'",
            ),
            requires_separate_owner_grant=True,
        ),
        IntegrationWaveProposal(
            wave_order=2,
            wave_id="WAVE_2_LAB_SYNTHETIC_TEST_SUITE",
            title="Additive import of tests/vip_lab/test_mega03..17*.py",
            included_prefixes=("tests/vip_lab/",),
            prerequisites=("WAVE_1_PURE_LAB_PACKAGE", "Hosted pytest green across full suite"),
            requires_separate_owner_grant=True,
        ),
        IntegrationWaveProposal(
            wave_order=3,
            wave_id="WAVE_3_CI_AND_DOC_LEDGER_REVIEW",
            title="Selective adoption of docs/ai-studio-tasks/MEGA_* ledgers and synthetic CI workflow",
            included_prefixes=("docs/ai-studio-tasks/", ".github/workflows/vip-ai-studio-synthetic-ci.yml"),
            prerequisites=("WAVE_2_LAB_SYNTHETIC_TEST_SUITE",),
            requires_separate_owner_grant=True,
        ),
        IntegrationWaveProposal(
            wave_order=4,
            wave_id="WAVE_4_OWNER_GATED_CANONICAL_RECONCILIATION",
            title="Reconcile PR #258 (A-7 S5-T1), PR #259, H3-A04, and H3-C05 on canonical main",
            included_prefixes=("src/gate3/", "src/vip_fvs/"),
            prerequisites=(
                "WAVE_3_CI_AND_DOC_LEDGER_REVIEW",
                "Live Git history inspection of PR #258 and PR #259",
                "Explicit Owner canonical-main merge authorization",
            ),
            requires_separate_owner_grant=True,
        ),
    )


def build_canonical_integration_readiness(
    workspace_root: str | Path | None = None,
) -> CanonicalIntegrationReadinessPacket:
    """Build deterministic Workstream A LAB-to-Canonical integration readiness packet."""
    root = (
        Path(workspace_root).resolve()
        if workspace_root is not None
        else Path(__file__).resolve().parents[3]
    )

    media_records: list[ModuleSymbolRecord] = []
    for rel in REQUIRED_GATE0_MEDIA_MODULES:
        rec = inspect_module_symbols_ast(root, rel)
        media_records.append(rec)

    media_intact = all(r.exists and len(r.file_sha256) == 64 for r in media_records)
    if not media_intact:
        raise VipLabError(
            "BLOCKED_STALE_OR_INCOMPLETE_LAB_BASELINE",
            "One or more required src/gate0/media modules are missing from the workspace baseline.",
        )

    classifications: list[ModuleIntegrationClassification] = []
    for rel_path, wave_origin, category in MEGA03_TO_16_MODULE_CATALOG:
        clean_rel = validate_allowlisted_relative_path(rel_path)
        rec = inspect_module_symbols_ast(root, clean_rel)
        if not rec.exists:
            raise VipLabError(
                "BLOCKED_STALE_OR_INCOMPLETE_LAB_BASELINE",
                f"Required LAB baseline file {clean_rel!r} is missing.",
            )
        risk = (
            "NONE_ISOLATED_VIP_LAB_NAMESPACE"
            if category in (CATEGORY_ADDITIVE_SAFE, CATEGORY_SYNTHETIC_ONLY_HARNESS)
            else "REQUIRES_PR258_AND_A7_S5_RECONCILIATION"
        )
        note = (
            "Pure additive module under vip_lab namespace; zero path overlap with canonical main."
            if category == CATEGORY_ADDITIVE_SAFE
            else (
                "Synthetic-only test or orchestrator harness; safe to add under vip_lab/tests."
                if category == CATEGORY_SYNTHETIC_ONLY_HARNESS
                else "References A-7 S5 / E01 governance boundaries; requires reconciliation with PR #258 before canonical core adoption."
            )
        )
        classifications.append(
            ModuleIntegrationClassification(
                relative_path=clean_rel,
                wave_origin=wave_origin,
                category=category,
                exists=rec.exists,
                file_sha256=rec.file_sha256,
                symbol_count=len(rec.exported_symbols),
                exported_symbols=rec.exported_symbols,
                canonical_conflict_risk=risk,
                notes=note,
            )
        )

    conflicts = detect_transplant_conflicts(workspace_root=root)
    sequence = _default_integration_sequence()

    provisional = CanonicalIntegrationReadinessPacket(
        schema_version=CANONICAL_INTEGRATION_SCHEMA_VERSION,
        workspace_git_sha=NOT_OBSERVED,
        declared_lab_baseline_sha=DECLARED_LAB_PR1_REPAIR_SHA,
        canonical_reference_sha=CANONICAL_MAIN_REFERENCE_SHA,
        canonical_integration_executed=False,
        canonical_main_modified=False,
        canonical_adoption_authorized=False,
        gate0_media_modules_intact=media_intact,
        gate0_media_inventory=tuple(media_records),
        module_classifications=tuple(classifications),
        transplant_conflicts=conflicts,
        integration_sequence=sequence,
        packet_digest="0" * 64,
    )
    digest = canonical_sha256(provisional.payload_without_digest())
    return CanonicalIntegrationReadinessPacket(
        schema_version=provisional.schema_version,
        workspace_git_sha=provisional.workspace_git_sha,
        declared_lab_baseline_sha=provisional.declared_lab_baseline_sha,
        canonical_reference_sha=provisional.canonical_reference_sha,
        canonical_integration_executed=False,
        canonical_main_modified=False,
        canonical_adoption_authorized=False,
        gate0_media_modules_intact=provisional.gate0_media_modules_intact,
        gate0_media_inventory=provisional.gate0_media_inventory,
        module_classifications=provisional.module_classifications,
        transplant_conflicts=provisional.transplant_conflicts,
        integration_sequence=provisional.integration_sequence,
        packet_digest=digest,
    )


def verify_canonical_integration_readiness(
    packet: CanonicalIntegrationReadinessPacket | Mapping[str, Any],
) -> dict[str, Any]:
    """Verify integrity and non-execution invariants of a Workstream A packet."""
    raw = packet.to_dict() if isinstance(packet, CanonicalIntegrationReadinessPacket) else dict(packet)
    if raw.get("schema_version") != CANONICAL_INTEGRATION_SCHEMA_VERSION:
        raise VipLabError(
            "CANONICAL_INTEGRATION_SCHEMA_MISMATCH",
            f"Expected {CANONICAL_INTEGRATION_SCHEMA_VERSION}, got {raw.get('schema_version')!r}",
        )
    if (
        raw.get("canonical_integration_executed") is not False
        or raw.get("canonical_main_modified") is not False
        or raw.get("canonical_adoption_authorized") is not False
        or raw.get("gate0_media_modules_intact") is not True
    ):
        raise VipLabError(
            "CANONICAL_INTEGRATION_INVARIANT_VIOLATION",
            "Workstream A packet violated canonical non-execution or gate0/media preservation invariants.",
        )
    declared_digest = validate_hex_digest(
        str(raw.get("packet_digest", "")),
        field_name="packet_digest",
    )
    body = {k: v for k, v in raw.items() if k != "packet_digest"}
    computed = canonical_sha256(body)
    if declared_digest != computed:
        raise VipLabError(
            "CANONICAL_INTEGRATION_DIGEST_MISMATCH",
            f"packet_digest mismatch: declared {declared_digest} != computed {computed}",
        )
    return raw


def inspect_canonical_integration_gate(
    payload: Mapping[str, Any] | None = None,
) -> ReadinessPacket:
    """Evaluate Workstream A readiness and enforce refusal on premature canonical claims."""
    raw_payload = dict(payload) if isinstance(payload, Mapping) else {}
    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(raw_payload)

    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="WORKSTREAM_A_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Ignored untrusted authority flags in Workstream A payload.",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(raw_payload.get("claim_canonical_integration_executed", False)):
        blockers.append(REFUSAL_CANONICAL_INTEGRATION_NOT_EXECUTED)
        reasons.append(REFUSAL_CANONICAL_INTEGRATION_NOT_EXECUTED)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_CANONICAL_INTEGRATION_NOT_EXECUTED,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Canonical integration cannot be marked executed inside the LAB workspace.",
            )
        )

    if bool(raw_payload.get("claim_canonical_main_modified", False)):
        blockers.append(REFUSAL_CANONICAL_MAIN_MUTATION_FORBIDDEN)
        reasons.append(REFUSAL_CANONICAL_MAIN_MUTATION_FORBIDDEN)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_CANONICAL_MAIN_MUTATION_FORBIDDEN,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Canonical repository Centaurioun/video-intelligence-pipeline is strictly READ-ONLY.",
            )
        )

    if bool(raw_payload.get("claim_canonical_adoption_authorized", False)):
        blockers.append(REFUSAL_CANONICAL_ADOPTION_NOT_AUTHORIZED)
        reasons.append(REFUSAL_CANONICAL_ADOPTION_NOT_AUTHORIZED)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_CANONICAL_ADOPTION_NOT_AUTHORIZED,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Canonical adoption requires a separate Owner decision and canonical PR review.",
            )
        )

    ws_root = cleaned.get("workspace_root")
    pkt = build_canonical_integration_readiness(ws_root)

    cand_paths = tuple(str(x) for x in cleaned.get("candidate_paths", ()))
    pr_claims = tuple(str(x) for x in cleaned.get("claimed_pr_transplants", ()))
    extra_conflicts = detect_transplant_conflicts(
        candidate_paths=cand_paths,
        claimed_pr_transplants=pr_claims,
        workspace_root=ws_root,
    )
    blocking_conflicts = [
        c for c in extra_conflicts if c.severity in ("CRITICAL", "HIGH")
    ]
    if blocking_conflicts:
        blockers.append(REFUSAL_TRANSPLANT_CONFLICT_DETECTED)
        reasons.append(REFUSAL_TRANSPLANT_CONFLICT_DETECTED)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_TRANSPLANT_CONFLICT_DETECTED,
                status=ReadinessStatus.BLOCKED,
                message="Detected transplant conflicts in candidate canonical integration set.",
                details={"conflicts": [c.to_dict() for c in blocking_conflicts]},
            )
        )

    has_auth_refusal = any(f.status == ReadinessStatus.NOT_AUTHORIZED for f in findings)
    if has_auth_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("CANONICAL_INTEGRATION_PLAN_READY_NOT_EXECUTED")
        findings.append(
            ReadinessFinding(
                code="CANONICAL_INTEGRATION_PLAN_READY_NOT_EXECUTED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Inventoried MEGA-03..16 modules and verified 6 gate0/media modules; canonical integration remains unexecuted.",
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_AUTHORIZED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "packet_digest": pkt.packet_digest,
            "canonical_integration_executed": False,
            "canonical_main_modified": False,
            "canonical_adoption_authorized": False,
            "gate0_media_modules_intact": pkt.gate0_media_modules_intact,
            "inventoried_module_count": len(pkt.module_classifications),
            "wave_count": len(pkt.integration_sequence),
            "blocking_conflict_count": len(blocking_conflicts),
        },
    )
