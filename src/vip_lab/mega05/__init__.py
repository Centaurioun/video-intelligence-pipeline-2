"""MEGA-05: Gate-1 Model Asset Preflight, Side-Effect-Free Runtime Authority
State Machine, and Three-Arm Benchmark Entry Guard.
"""

from __future__ import annotations

from .benchmark_entry import inspect_benchmark_entry
from .model_assets import inspect_model_asset_claims
from .runtime_authority import (
     RUNTIME_AUTHORITY_STAGES,
    RuntimeAuthorityStage,
    inspect_runtime_authority,
)

__all__ = [
    "RUNTIME_AUTHORITY_STAGES",
    "RuntimeAuthorityStage",
    "inspect_benchmark_entry",
    "inspect_model_asset_claims",
    "inspect_runtime_authority",
]
