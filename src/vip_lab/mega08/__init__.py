"""MEGA-08: Deterministic Repository Capability, Contract & Gap Inventory (Packet P08)."""

from __future__ import annotations

from .capability_inventory import (
    ALLOWED_GOVERNANCE_DOC_PATHS,
    ALLOWED_INVENTORY_PREFIXES,
    CANONICAL_CAPABILITY_CLASSES,
    CANONICAL_VIP_REFERENCE_SHA,
    DECLARED_BASELINE_REVISION,
    DEFAULT_MODULE_EXPECTATIONS,
    CapabilityEntry,
    CapabilityInventoryReport,
    ModuleSymbolRecord,
    build_capability_inventory,
    inspect_module_symbols_ast,
    validate_allowlisted_relative_path,
    validate_capability_source_reference_path,
)
from .contract_gate import STAGE_ID, inspect_capability_gate
from .gap_digest import MEGA_08_14_SPEC_VERSION, compute_gap_digest, verify_gap_digest

__all__ = [
    "ALLOWED_GOVERNANCE_DOC_PATHS",
    "ALLOWED_INVENTORY_PREFIXES",
    "CANONICAL_CAPABILITY_CLASSES",
    "CANONICAL_VIP_REFERENCE_SHA",
    "DECLARED_BASELINE_REVISION",
    "DEFAULT_MODULE_EXPECTATIONS",
    "MEGA_08_14_SPEC_VERSION",
    "STAGE_ID",
    "CapabilityEntry",
    "CapabilityInventoryReport",
    "ModuleSymbolRecord",
    "build_capability_inventory",
    "compute_gap_digest",
    "inspect_capability_gate",
    "inspect_module_symbols_ast",
    "validate_allowlisted_relative_path",
    "validate_capability_source_reference_path",
    "verify_gap_digest",
]
