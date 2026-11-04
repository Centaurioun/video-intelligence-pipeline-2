"""Static AST-based repository capability and gap inventory for MEGA-08.

Packet P08 — Capability & Gap Inventory (`LAB-MEGA-08-14-v1.0.0`).

Invariants enforced:
- Uses Python ``ast.parse`` over bounded UTF-8 file reads; never imports or executes
  inspected target files during static inventory.
- Enforces a closed repository path allowlist (`src/vip_fvs/`, `src/vip_lab/`,
  `src/gate0/`, `src/gate1/`, `src/gate2/`, `src/gate3/`, `src/persistent_local_index/`,
  `tests/vip_lab/`, `docs/ai-studio-tasks/`).
- Reports ``workspace_git_sha = "NOT_OBSERVED"``,
  ``declared_baseline_revision = "22f1ffa7064f697d4049e39587945b1decabec4e"``, and
  ``canonical_reference_sha = "592952daf475b1bbae2eebdee64d992c1a744f08"``.
- Provides read-only WBS/H3 advisory mappings and Stretch S1/S4/S5 crosswalks with
  ``scheduler_state_mutated = False``.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any, Mapping, Sequence

from ..common import (
    CANONICAL_EVIDENCE_CLASSES,
    NOT_OBSERVED,
    VipLabError,
)
from .gap_digest import compute_gap_digest


MEGA_08_14_SPEC_VERSION = "LAB-MEGA-08-14-v1.0.0"
DECLARED_BASELINE_REVISION = "22f1ffa7064f697d4049e39587945b1decabec4e"
CANONICAL_VIP_REFERENCE_SHA = "592952daf475b1bbae2eebdee64d992c1a744f08"
MAX_INVENTORY_SOURCE_BYTES = 1024 * 1024  # 1 MiB per inspected source file

ALLOWED_INVENTORY_PREFIXES: tuple[str, ...] = (
    "src/vip_fvs/",
    "src/vip_lab/",
    "src/gate0/",
    "src/gate1/",
    "src/gate2/",
    "src/gate3/",
    "src/persistent_local_index/",
    "tests/vip_lab/",
    "docs/ai-studio-tasks/",
)

CANONICAL_CAPABILITY_CLASSES = frozenset(
    {
        "IMPLEMENTED_IN_SOURCE",
        "COVERED_SYNTHETIC",
        "GAP_CODE_CAPABLE",
        "BLOCKED_BY_AUTHORITY",
        "NOT_OBSERVED",
    }
)

# Deterministic precomputed semantic space IDs for the 3 closed synthetic profiles
# (derived from persistent_local_index.model_space.semantic_space_id over make_synthetic_profile)
_SYNTHETIC_PROFILE_CROSSWALK: tuple[dict[str, Any], ...] = (
    {
        "arm_id": "VIP_V1_BASE",
        "profile_id": "vip-v1-siglip-base-224",
        "model_id": "google/siglip-base-patch16-224",
        "family": "siglip",
        "embedding_dim": 768,
        "row_width_bytes": 3072,
        "space_id": "vip-v1-siglip-base-224:768:float32:l2",
        "tokenizer_contract_state": "SYNTHETIC_TEXT_CONTRACT_ONLY",
    },
    {
        "arm_id": "VIP_V2_BASE",
        "profile_id": "vip-v2-siglip2-base-224",
        "model_id": "google/siglip2-base-patch16-224",
        "family": "siglip2",
        "embedding_dim": 768,
        "row_width_bytes": 3072,
        "space_id": "vip-v2-siglip2-base-224:768:float32:l2",
        "tokenizer_contract_state": "PROVISIONAL_CONTRADICTORY_32000_VS_256000",
    },
    {
        "arm_id": "VIP_V2_SO400M",
        "profile_id": "vip-v2-siglip2-so400m-384",
        "model_id": "google/siglip2-so400m-patch14-384",
        "family": "siglip2",
        "embedding_dim": 1152,
        "row_width_bytes": 4608,
        "space_id": "vip-v2-siglip2-so400m-384:1152:float32:l2",
        "tokenizer_contract_state": "PROVISIONAL_CONTRADICTORY_32000_VS_256000",
    },
)

DEFAULT_MODULE_EXPECTATIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "src/vip_fvs/query_batch.py",
        (
            "QUERY_CATALOG_SCHEMA_VERSION",
            "QueryCatalog",
            "QueryCatalogItem",
            "parse_query_catalog_mapping",
            "validate_lab_top_k",
        ),
    ),
    (
        "src/vip_fvs/synthetic_profiles.py",
        (
            "CLOSED_SYNTHETIC_PROFILE_IDS",
            "V1_PROFILE_ID",
            "V2_BASE_PROFILE_ID",
            "V2_SO400M_PROFILE_ID",
            "SyntheticProfileBundle",
            "build_synthetic_profile_runtime",
            "make_synthetic_profile",
        ),
    ),
    (
        "src/vip_fvs/batch_retrieval.py",
        (
            "BatchCandidateRecord",
            "BatchQueryResult",
            "SingleArmBatchResult",
            "run_batch_retrieval",
        ),
    ),
    (
        "src/vip_fvs/three_arm_batch.py",
        (
            "DECLARED_ARM_ORDER",
            "ARM_TO_PROFILE_ID",
            "ThreeArmConfigMap",
            "ThreeArmBatchResult",
            "run_three_arm_batch",
        ),
    ),
    (
        "src/vip_fvs/batch_report.py",
        (
            "BATCH_REPORT_SCHEMA_VERSION",
            "build_single_arm_batch_report",
            "build_three_arm_batch_report",
            "verify_batch_report",
        ),
    ),
    (
        "src/vip_fvs/review_bundle.py",
        ("ReviewBundle", "V1_SCHEMA_VERSION", "V2_SCHEMA_VERSION", "V3_SCHEMA_VERSION"),
    ),
    (
        "src/vip_fvs/human_decision.py",
        ("HumanDecisionArtifact", "create_human_decision"),
    ),
    (
        "src/vip_fvs/real_plan.py",
        ("SourceTimelineMapping", "RealPlanArtifacts", "build_real_edit_plan"),
    ),
    (
        "src/gate2/workload.py",
        ("WorkloadSpec", "WorkloadError", "SyntheticFixture", "generate"),
    ),
    (
        "src/gate2/recovery.py",
        ("RecoveryBinding", "RecoveryHarness", "RecoveryRefusal"),
    ),
    (
        "src/gate2/faults.py",
        ("FaultClass", "Capability", "capability", "inject"),
    ),
    (
        "src/gate3/pts.py",
        ("PtsTable",),
    ),
    (
        "src/gate3/temporal.py",
        (
            "SnapResult",
            "resolve_start",
            "resolve_end",
            "classify_vfr",
            "detect_discontinuity",
        ),
    ),
    (
        "src/gate3/qc.py",
        ("QCReport", "bare_pass_is_insufficient", "may_consume_for_binding_origin"),
    ),
    (
        "src/vip_lab/common.py",
        (
            "ReadinessPacket",
            "ReadinessStatus",
            "SyntheticContextMarker",
            "canonical_json_dumps",
            "canonical_sha256",
        ),
    ),
)


def validate_allowlisted_relative_path(rel_path: str) -> str:
    """Validate that ``rel_path`` is a clean relative POSIX path under an allowlisted prefix."""
    if not isinstance(rel_path, str) or not rel_path.strip() or "\x00" in rel_path:
        raise VipLabError(
            "INVENTORY_PATH_INVALID",
            "Relative path must be a non-empty string without NUL bytes",
            field_path="relative_path",
        )
    if rel_path.startswith("/") or rel_path.startswith("\\") or ":" in rel_path:
        raise VipLabError(
            "INVENTORY_ABSOLUTE_PATH_REFUSED",
            f"Absolute or drive-prefixed path is forbidden: {rel_path!r}",
            field_path="relative_path",
        )
    normalized = rel_path.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise VipLabError(
            "INVENTORY_PATH_TRAVERSAL_REFUSED",
            f"Path traversal or dot segment is forbidden: {rel_path!r}",
            field_path="relative_path",
        )
    clean_posix = "/".join(parts)
    if not any(clean_posix.startswith(prefix) for prefix in ALLOWED_INVENTORY_PREFIXES):
        raise VipLabError(
            "INVENTORY_PATH_NOT_ALLOWLISTED",
            f"Path {clean_posix!r} is outside allowlisted repository prefixes",
            field_path="relative_path",
        )
    return clean_posix


def _read_bounded_regular_bytes(path: Path, *, max_bytes: int = MAX_INVENTORY_SOURCE_BYTES) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    fd = os.open(str(path), flags)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise VipLabError(
                "INVENTORY_NON_REGULAR_FILE",
                f"Refused non-regular file during inventory: {path}",
            )
        if st.st_size > max_bytes:
            raise VipLabError(
                "INVENTORY_FILE_SIZE_EXCEEDED",
                f"File {path} size {st.st_size} exceeds {max_bytes} bytes",
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, max_bytes - total + 1))
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise VipLabError(
                    "INVENTORY_FILE_SIZE_EXCEEDED",
                    f"File {path} grew past {max_bytes} bytes during read",
                )
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _extract_top_level_ast_symbols(source_text: str, *, rel_path: str) -> tuple[str, ...]:
    try:
        tree = ast.parse(source_text, filename=rel_path)
    except SyntaxError as exc:
        raise VipLabError(
            "INVENTORY_AST_SYNTAX_ERROR",
            f"SyntaxError while parsing {rel_path}: {exc}",
            field_path=rel_path,
        ) from exc

    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
                    if target.id == "__all__" and isinstance(
                        node.value, (ast.List, ast.Tuple, ast.Set)
                    ):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                names.add(elt.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return tuple(sorted(names))


@dataclass(frozen=True)
class ModuleSymbolRecord:
    """Static AST symbol inspection record for one allowlisted Python file."""

    relative_path: str
    exists: bool
    file_sha256: str
    exported_symbols: tuple[str, ...]
    expected_symbols: tuple[str, ...]
    missing_symbols: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "relative_path": self.relative_path,
            "exists": self.exists,
            "file_sha256": self.file_sha256,
            "exported_symbols": list(self.exported_symbols),
            "expected_symbols": list(self.expected_symbols),
            "missing_symbols": list(self.missing_symbols),
        }


def inspect_module_symbols_ast(
    workspace_root: str | Path,
    relative_path: str,
    *,
    expected_symbols: Sequence[str] = (),
) -> ModuleSymbolRecord:
    """Inspect a Python module statically via ``ast.parse`` without importing it."""
    clean_rel = validate_allowlisted_relative_path(relative_path)
    root = Path(workspace_root)
    target = root / clean_rel
    expected_tuple = tuple(sorted({str(s) for s in expected_symbols if str(s).strip()}))

    if not target.exists():
        return ModuleSymbolRecord(
            relative_path=clean_rel,
            exists=False,
            file_sha256=NOT_OBSERVED,
            exported_symbols=(),
            expected_symbols=expected_tuple,
            missing_symbols=expected_tuple,
        )

    raw_bytes = _read_bounded_regular_bytes(target)
    digest = hashlib.sha256(raw_bytes).hexdigest()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VipLabError(
            "INVENTORY_UTF8_DECODE_ERROR",
            f"Non-UTF-8 source file {clean_rel}: {exc}",
            field_path=clean_rel,
        ) from exc

    exported = _extract_top_level_ast_symbols(text, rel_path=clean_rel)
    exported_set = set(exported)
    missing = tuple(sym for sym in expected_tuple if sym not in exported_set)
    return ModuleSymbolRecord(
        relative_path=clean_rel,
        exists=True,
        file_sha256=digest,
        exported_symbols=exported,
        expected_symbols=expected_tuple,
        missing_symbols=missing,
    )


@dataclass(frozen=True)
class CapabilityEntry:
    """One classified repository or laboratory capability row."""

    capability_id: str
    title: str
    gate: str
    classification: str
    evidence_state: str
    source_paths: tuple[str, ...]
    authority_blocker: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not self.capability_id.strip():
            raise VipLabError("CAPABILITY_ID_INVALID", "capability_id must be non-empty")
        if self.classification not in CANONICAL_CAPABILITY_CLASSES:
            raise VipLabError(
                "CAPABILITY_CLASSIFICATION_INVALID",
                f"Unsupported capability classification: {self.classification!r}",
            )
        if (
            self.evidence_state != NOT_OBSERVED
            and self.evidence_state not in CANONICAL_EVIDENCE_CLASSES
        ):
            raise VipLabError(
                "CAPABILITY_EVIDENCE_STATE_INVALID",
                f"Unsupported evidence_state: {self.evidence_state!r}",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "title": self.title,
            "gate": self.gate,
            "classification": self.classification,
            "evidence_state": self.evidence_state,
            "source_paths": list(self.source_paths),
            "authority_blocker": self.authority_blocker,
        }


@dataclass(frozen=True)
class CapabilityInventoryReport:
    """Immutable deterministic MEGA-08 capability and gap inventory report."""

    spec_version: str
    workspace_git_sha: str
    declared_baseline_revision: str
    canonical_reference_sha: str
    synthetic_only: bool
    execution_authorized: bool
    module_inventory: tuple[ModuleSymbolRecord, ...]
    capability_matrix: tuple[CapabilityEntry, ...]
    wbs_h3_advisory_map: Mapping[str, Any]
    stretch_advisory_crosswalks: Mapping[str, Any]
    inventory_digest: str

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "spec_version": self.spec_version,
            "workspace_git_sha": self.workspace_git_sha,
            "declared_baseline_revision": self.declared_baseline_revision,
            "canonical_reference_sha": self.canonical_reference_sha,
            "synthetic_only": self.synthetic_only,
            "execution_authorized": self.execution_authorized,
            "module_inventory": [m.to_dict() for m in self.module_inventory],
            "capability_matrix": [c.to_dict() for c in self.capability_matrix],
            "wbs_h3_advisory_map": dict(self.wbs_h3_advisory_map),
            "stretch_advisory_crosswalks": dict(self.stretch_advisory_crosswalks),
        }

    def to_dict(self) -> dict[str, Any]:
        out = self.payload_without_digest()
        out["inventory_digest"] = self.inventory_digest
        return out


def _build_wbs_h3_advisory_map() -> dict[str, Any]:
    return {
        "advisory_status": "ADVISORY_ONLY",
        "scheduler_state_mutated": False,
        "wbs_checkboxes_mutated": False,
        "mappings": [
            {
                "target_id": "G0.1.4",
                "domain": "WBS_GATE0",
                "lab_packets": ["MEGA-04", "MEGA-08", "S1"],
                "canonical_status": "OPEN_PARTIAL_SYNTHETIC_ONLY",
                "advisory_note": "30-field D-2 readiness remains 0 VERIFIED / 7 PENDING / 21 BLOCKED / 2 NOT_OBSERVED.",
            },
            {
                "target_id": "G0.2.2",
                "domain": "WBS_GATE0",
                "lab_packets": ["MEGA-04", "MEGA-08"],
                "canonical_status": "OPEN_PARTIAL_SYNTHETIC_ONLY",
                "advisory_note": "24+8+8 synthetic query/gold conformance only; genuine editor queries NOT_OBSERVED.",
            },
            {
                "target_id": "G0.2.3",
                "domain": "WBS_GATE0",
                "lab_packets": ["MEGA-04"],
                "canonical_status": "OPEN_PARTIAL_SYNTHETIC_ONLY",
                "advisory_note": "Reviewer query/window membership checked; genuine human blind review NOT_OBSERVED.",
            },
            {
                "target_id": "G1.1.4",
                "domain": "WBS_GATE1",
                "lab_packets": ["MEGA-05", "MEGA-08", "S4"],
                "canonical_status": "SOURCE_ONLY_RECONCILED_GATE_B_BLOCKED",
                "advisory_note": "Three synthetic profiles isolated; authentic V2 runtime NOT_OBSERVED, Gate B NO_GO_BLOCKED.",
            },
            {
                "target_id": "G2.1.3",
                "domain": "WBS_GATE2",
                "lab_packets": ["MEGA-06", "MEGA-12", "S3"],
                "canonical_status": "SYNTHETIC_WORKLOAD_ONLY",
                "advisory_note": "Generated workload and replay consistency tested; real archive workload NOT_OBSERVED.",
            },
            {
                "target_id": "G3.1.5",
                "domain": "WBS_GATE3",
                "lab_packets": ["MEGA-07", "MEGA-09", "MEGA-10", "MEGA-11", "MEGA-13", "MEGA-14"],
                "canonical_status": "SYNTHETIC_RECONCILIATION_COVERED",
                "advisory_note": "End-to-end synthetic candidate -> temporal request -> proposal -> QC refusal covered.",
            },
            {
                "target_id": "G3.1.6",
                "domain": "WBS_GATE3",
                "lab_packets": ["MEGA-07", "MEGA-10", "MEGA-13"],
                "canonical_status": "SYNTHETIC_GUARDS_COVERED",
                "advisory_note": "Fail-closed PTS/stream/export refusal boundaries preserved.",
            },
            {
                "target_id": "H3-C05",
                "domain": "ATLAS_H3",
                "lab_packets": ["MEGA-02", "MEGA-09"],
                "canonical_status": "PLANNED_CONTRACT_V1_0_2_ADOPTED",
                "advisory_note": "Read-only existing-generation query-multi contract adopted; canonical H3 state remains PLANNED.",
            },
            {
                "target_id": "H3-A04",
                "domain": "ATLAS_H3",
                "lab_packets": ["MEGA-08"],
                "canonical_status": "PLANNED_CONTRACT_V1_0_1_OPTION_B_ADOPTED",
                "advisory_note": "Contract-only Option B adopted; Task-6 source implementation requires separate grant.",
            },
            {
                "target_id": "A-7-S5",
                "domain": "GATE3_DECISION",
                "lab_packets": ["MEGA-03", "MEGA-08", "S5"],
                "canonical_status": "PLAN_ADOPTED_IMPLEMENTATION_AUTHORIZED_FALSE",
                "advisory_note": "D1-D7 and T1-T8 conditional TDD plan adopted; PR #258 absent from ZIP snapshot.",
            },
        ],
    }


def _build_stretch_advisory_crosswalks() -> dict[str, Any]:
    return {
        "S1_d2_readiness_crosswalk": {
            "advisory_only": True,
            "total_fields": 30,
            "verified_count": 0,
            "pending_count": 7,
            "blocked_count": 21,
            "not_observed_count": 2,
            "authenticity": "DECLARED_NOT_AUTHENTICATED",
            "owner_approval_claimed": False,
            "execution_authorized": False,
            "authorized_local_execution_gate_open": False,
        },
        "S4_siglip2_contract_crosswalk": {
            "advisory_only": True,
            "gate_b_status": "NO_GO_BLOCKED",
            "native_task_4_5_exception": "PROPOSED_NOT_ADOPTED",
            "authentic_weights_loaded": False,
            "historical_vocab_contradiction": "0..31999_VS_256000_UNRESOLVED_IN_PROVISIONAL_DOC",
            "profiles": [dict(row) for row in _SYNTHETIC_PROFILE_CROSSWALK],
        },
        "S5_a7_s5_test_resource_crosswalk": {
            "advisory_only": True,
            "reader_unit_source_cap_bytes": 4096,
            "integrated_synthetic_source_cap_bytes": 8 * 1024 * 1024,
            "timing_sample_cap": 20000,
            "refuse_at_sample_count": 20001,
            "probe_json_cap_bytes": 1024 * 1024,
            "refinement_json_cap_bytes": 1024 * 1024,
            "review_bundle_json_cap_bytes": 512 * 1024,
            "snapshot_manifest_json_cap_bytes": 64 * 1024,
            "probe_rows_cap": 64,
            "json_nesting_depth_cap": 64,
            "read_chunk_bytes": 64 * 1024,
            "child_process_rss_guard_bytes": 256 * 1024 * 1024,
            "production_resource_budget": "PENDING_EVIDENCE",
            "implementation_authorized": False,
            "production_ready": False,
            "pr258_merged_in_snapshot": False,
        },
    }


def _default_capability_matrix(workspace_root: Path) -> tuple[CapabilityEntry, ...]:
    def _wave_status(rel_dir: str) -> str:
        return (
            "COVERED_SYNTHETIC"
            if (workspace_root / rel_dir / "__init__.py").is_file()
            else "GAP_CODE_CAPABLE"
        )

    entries = (
        CapabilityEntry(
            capability_id="VIP_FVS_QUERY_BATCH_W1",
            title="Closed Bounded Query Catalog & Digest Identity",
            gate="G0_G1_LAB",
            classification="IMPLEMENTED_IN_SOURCE",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_fvs/query_batch.py",),
        ),
        CapabilityEntry(
            capability_id="VIP_FVS_SYNTHETIC_PROFILES_W2",
            title="Three Closed Synthetic Model Profiles & Fake Checked Runtimes",
            gate="G1_LAB",
            classification="IMPLEMENTED_IN_SOURCE",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_fvs/synthetic_profiles.py",),
        ),
        CapabilityEntry(
            capability_id="VIP_FVS_BATCH_RETRIEVAL_W3",
            title="Read-Only Multi-Source Batch Retrieval Consumer",
            gate="G0_G1_LAB",
            classification="IMPLEMENTED_IN_SOURCE",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_fvs/batch_retrieval.py", "src/vip_fvs/multi_source_retrieval.py"),
        ),
        CapabilityEntry(
            capability_id="VIP_FVS_THREE_ARM_BATCH_W4",
            title="Three-Arm Isolated Synthetic Batch Retrieval Orchestrator",
            gate="G1_LAB",
            classification="IMPLEMENTED_IN_SOURCE",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_fvs/three_arm_batch.py",),
        ),
        CapabilityEntry(
            capability_id="VIP_FVS_BATCH_REPORT_W5",
            title="Canonical Single-Arm & Three-Arm Synthetic Batch Report Verifier",
            gate="G1_LAB",
            classification="IMPLEMENTED_IN_SOURCE",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_fvs/batch_report.py",),
        ),
        CapabilityEntry(
            capability_id="VIP_LAB_MEGA03_TO_07_PREFLIGHT",
            title="MEGA-03 through MEGA-07 Multi-Gate Synthetic Readiness Preflight",
            gate="ALL_GATES_LAB",
            classification="COVERED_SYNTHETIC",
            evidence_state=NOT_OBSERVED,
            source_paths=(
                "src/vip_lab/common.py",
                "src/vip_lab/integration.py",
                "src/vip_lab/cli.py",
            ),
        ),
        CapabilityEntry(
            capability_id="LAB_MEGA08_CAPABILITY_INVENTORY",
            title="MEGA-08 Static AST Capability & Gap Inventory",
            gate="ALL_GATES_LAB",
            classification=_wave_status("src/vip_lab/mega08"),
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_lab/mega08/capability_inventory.py",),
        ),
        CapabilityEntry(
            capability_id="LAB_MEGA09_CANDIDATE_REVIEW_QUEUE",
            title="MEGA-09 Batch Retrieval to Nonbinding Review Queue",
            gate="G1_G3_LAB",
            classification=_wave_status("src/vip_lab/mega09"),
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_lab/mega09/candidate_queue.py",),
        ),
        CapabilityEntry(
            capability_id="LAB_MEGA10_TEMPORAL_REFINEMENT_REQUEST",
            title="MEGA-10 Candidate Temporal Request & Source-Native PTS Diagnostic",
            gate="G3_LAB",
            classification=_wave_status("src/vip_lab/mega10"),
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_lab/mega10/temporal_request.py",),
        ),
        CapabilityEntry(
            capability_id="LAB_MEGA11_VERSIONED_EDITORIAL_PROPOSAL",
            title="MEGA-11 Versioned Non-Authoritative Editorial Proposal",
            gate="G3_LAB",
            classification=_wave_status("src/vip_lab/mega11"),
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_lab/mega11/editorial_proposal.py",),
        ),
        CapabilityEntry(
            capability_id="LAB_MEGA12_REPLAY_CONSISTENCY_LEDGER",
            title="MEGA-12 Generated-Only Recovery & Replay Consistency Ledger",
            gate="G2_LAB",
            classification=_wave_status("src/vip_lab/mega12"),
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_lab/mega12/replay_graph.py",),
        ),
        CapabilityEntry(
            capability_id="LAB_MEGA13_QC_EXPORT_REFUSAL_AUDIT",
            title="MEGA-13 QC Evidence Completeness & Production Export Refusal",
            gate="G3_LAB",
            classification=_wave_status("src/vip_lab/mega13"),
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_lab/mega13/qc_readiness.py",),
        ),
        CapabilityEntry(
            capability_id="LAB_MEGA14_END_TO_END_SYNTHETIC_RUNNER",
            title="MEGA-14 End-to-End Synthetic Lab Runner, Verifier & CLI",
            gate="ALL_GATES_LAB",
            classification=_wave_status("src/vip_lab/mega14"),
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_lab/mega14/orchestrator.py",),
        ),
        CapabilityEntry(
            capability_id="GATE3_A7_S5_T1_BOUNDED_ADMISSION_PR258",
            title="Gate-3 A-7 S5-T1 Bounded Descriptor Admission (PR #258)",
            gate="G3",
            classification="BLOCKED_BY_AUTHORITY",
            evidence_state=NOT_OBSERVED,
            source_paths=("docs/decisions/2026-10-29-a7-s5-scoped-synthetic-tdd-plan-owner-adoption.md",),
            authority_blocker="PR_258_ABSENT_IN_SNAPSHOT_AND_SEPARATE_T1_GRANT_REQUIRED",
        ),
        CapabilityEntry(
            capability_id="GATE3_A7_POSITIVE_STREAM_MAPPING",
            title="Gate-3 A-7 Positive FFprobe-Global to ISO-BMFF Track Mapping",
            gate="G3",
            classification="BLOCKED_BY_AUTHORITY",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/gate3/pts.py",),
            authority_blocker="A7_POSITIVE_MAPPING_OWNER_ADOPTION_PENDING",
        ),
        CapabilityEntry(
            capability_id="GATE0_D3_REAL_CORPUS_EXPERIMENT",
            title="Gate-0 D-3 Authorized Real Corpus Diagnostic Experiment",
            gate="G0",
            classification="BLOCKED_BY_AUTHORITY",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/gate0/media/source_guard.py",),
            authority_blocker="D2_OWNER_INPUTS_PENDING_AND_D3_NOT_AUTHORIZED",
        ),
        CapabilityEntry(
            capability_id="GATE1_AUTHENTIC_MODEL_WEIGHTS_BENCHMARK",
            title="Gate-1 Authentic SigLIP / SigLIP2 Weights & Held-Out Benchmark",
            gate="G1",
            classification="BLOCKED_BY_AUTHORITY",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/vip_fvs/synthetic_profiles.py",),
            authority_blocker="GATE_B_NO_GO_BLOCKED_AND_MODEL_LOAD_NOT_AUTHORIZED",
        ),
        CapabilityEntry(
            capability_id="GATE2_REAL_ARCHIVE_WORKLOAD_SCALE",
            title="Gate-2 Representative Archive-Scale Workload & Mechanism Justification",
            gate="G2",
            classification="BLOCKED_BY_AUTHORITY",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/gate2/workload.py",),
            authority_blocker="REAL_ARCHIVE_WORKLOAD_NOT_OBSERVED",
        ),
        CapabilityEntry(
            capability_id="GATE3_PRODUCTION_RENDER_EXPORT",
            title="Gate-3 Production Video Render & Export",
            gate="G3",
            classification="BLOCKED_BY_AUTHORITY",
            evidence_state=NOT_OBSERVED,
            source_paths=("src/gate3/qc.py",),
            authority_blocker="PRODUCTION_EXPORT_NOT_AUTHORIZED",
        ),
    )
    return entries


def build_capability_inventory(
    workspace_root: str | Path,
    *,
    module_expectations: Sequence[tuple[str, Sequence[str]]] | None = None,
    capability_entries: Sequence[CapabilityEntry] | None = None,
) -> CapabilityInventoryReport:
    """Build a deterministic, digest-verified MEGA-08 capability & gap inventory."""
    root = Path(workspace_root)
    expectations = (
        tuple((rel, tuple(syms)) for rel, syms in module_expectations)
        if module_expectations is not None
        else DEFAULT_MODULE_EXPECTATIONS
    )

    seen_rel_paths: set[str] = set()
    module_records: list[ModuleSymbolRecord] = []
    for rel_path, expected_syms in expectations:
        clean_rel = validate_allowlisted_relative_path(rel_path)
        if clean_rel in seen_rel_paths:
            raise VipLabError(
                "INVENTORY_DUPLICATE_MODULE_PATH",
                f"Duplicate module path in inventory request: {clean_rel!r}",
                field_path="module_expectations",
            )
        seen_rel_paths.add(clean_rel)
        module_records.append(
            inspect_module_symbols_ast(root, clean_rel, expected_symbols=expected_syms)
        )

    matrix = (
        tuple(capability_entries)
        if capability_entries is not None
        else _default_capability_matrix(root)
    )
    seen_cap_ids: set[str] = set()
    for cap in matrix:
        if cap.capability_id in seen_cap_ids:
            raise VipLabError(
                "CAPABILITY_INVENTORY_DUPLICATE_ID",
                f"Duplicate capability_id {cap.capability_id!r}",
                field_path="capability_matrix",
            )
        seen_cap_ids.add(cap.capability_id)
        for src_p in cap.source_paths:
            validate_allowlisted_relative_path(src_p)

    wbs_map = _build_wbs_h3_advisory_map()
    stretch_map = _build_stretch_advisory_crosswalks()

    provisional = CapabilityInventoryReport(
        spec_version=MEGA_08_14_SPEC_VERSION,
        workspace_git_sha=NOT_OBSERVED,
        declared_baseline_revision=DECLARED_BASELINE_REVISION,
        canonical_reference_sha=CANONICAL_VIP_REFERENCE_SHA,
        synthetic_only=True,
        execution_authorized=False,
        module_inventory=tuple(module_records),
        capability_matrix=matrix,
        wbs_h3_advisory_map=wbs_map,
        stretch_advisory_crosswalks=stretch_map,
        inventory_digest="0" * 64,
    )
    digest = compute_gap_digest(provisional.payload_without_digest())
    return CapabilityInventoryReport(
        spec_version=provisional.spec_version,
        workspace_git_sha=provisional.workspace_git_sha,
        declared_baseline_revision=provisional.declared_baseline_revision,
        canonical_reference_sha=provisional.canonical_reference_sha,
        synthetic_only=True,
        execution_authorized=False,
        module_inventory=provisional.module_inventory,
        capability_matrix=provisional.capability_matrix,
        wbs_h3_advisory_map=provisional.wbs_h3_advisory_map,
        stretch_advisory_crosswalks=provisional.stretch_advisory_crosswalks,
        inventory_digest=digest,
    )
