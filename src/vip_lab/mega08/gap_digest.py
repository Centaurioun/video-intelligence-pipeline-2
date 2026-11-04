"""Deterministic SHA-256 gap-digest calculation and verification for MEGA-08.

Packet P08 — Capability & Gap Inventory (`LAB-MEGA-08-14-v1.0.0`).
"""

from __future__ import annotations

from typing import Any, Mapping

from ..common import VipLabError, canonical_sha256, validate_hex_digest

MEGA_08_14_SPEC_VERSION = "LAB-MEGA-08-14-v1.0.0"


def compute_gap_digest(report_without_digest: Mapping[str, Any]) -> str:
    """Compute canonical SHA-256 digest over a MEGA-08 inventory report body."""
    if not isinstance(report_without_digest, Mapping):
        raise VipLabError("GAP_DIGEST_NOT_MAPPING", "Inventory report must be a mapping")
    body = {k: v for k, v in report_without_digest.items() if k != "inventory_digest"}
    return canonical_sha256(body)


def verify_gap_digest(report_payload: Mapping[str, Any]) -> bool:
    """Verify that ``report_payload["inventory_digest"]`` matches the canonical body."""
    if not isinstance(report_payload, Mapping):
        raise VipLabError("GAP_DIGEST_NOT_MAPPING", "Inventory report must be a mapping")
    declared = validate_hex_digest(
        report_payload.get("inventory_digest"),
        field_name="inventory_digest",
        error_code="GAP_DIGEST_INVALID",
    )
    expected = compute_gap_digest(report_payload)
    if declared != expected:
        raise VipLabError(
            "GAP_DIGEST_MISMATCH",
            f"inventory_digest mismatch: declared {declared} != expected {expected}",
            field_path="inventory_digest",
        )
    return True


__all__ = [
    "MEGA_08_14_SPEC_VERSION",
    "compute_gap_digest",
    "verify_gap_digest",
]
