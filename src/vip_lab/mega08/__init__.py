"""MEGA-08: Deterministic Repository Capability, Contract & Gap Inventory (Packet P08)."""

from __future__ import annotations

from .capability_inventory import (
    ALLOWED_INVENTORY_PREFIXES,
    CANONICAL_CAPABILITY_CLASSES,
    CANONICAL_VIP_REFERENCE_SHA,
    DECLARED_BASELINE_REVISION,
    DEFAULT_MODULE_EXPECTATIONS,
    MEGA_08_14_SPEC_VERSION,
    CapabilityEntry,
    CapabilityInventoryReport,
    ModuleSymbolRecord,
    build_capability_inventory,
    inspect_module_symbols_ast,
    validate_allowlisted_relative_path,
)
from .contract_gate import STAGE_ID, inspect_capability_gate
from .gap_digest import compute_gap_digest, verify_gap_digest

__all__ = [
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
    "verify_gap_digest",
]
