"""Stage-A feasibility harness exports.

These names are re-exported **lazily** (PEP 562).  Importing any
``gate0.feasibility.*`` submodule executes this package's ``__init__``, so an
eager Stage-A import here would drag the entire Stage-A closure
(``gate0.adapters``, ``gate0.inventory``, ``gate0.policy``) into a
network-only execution path.  Deferring the import keeps
``from gate0.feasibility import run_stage_a`` working while leaving the
network-only path free of every Stage-A dependency.
"""
from typing import Any

__all__ = ["compare_stage_a_receipts", "run_stage_a"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from .macos_stage_a import compare_stage_a_receipts, run_stage_a
        return {"compare_stage_a_receipts": compare_stage_a_receipts,
                "run_stage_a": run_stage_a}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
