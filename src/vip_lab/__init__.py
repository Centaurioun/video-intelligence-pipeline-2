"""Synthetic Lab preflight and cross-gate integration package for VIP.

All modules in ``vip_lab`` are bounded synthetic/offline readiness and preflight
evaluators. They never grant owner authority, execute authentic models, invoke
native media tools (FFmpeg/FFprobe), or approve production gates.
"""

from __future__ import annotations

from .common import (
    LAB_PROGRAM_VERSION,
    MAX_LAB_JSON_BYTES,
    SYNTHETIC_CONTEXT_TOKEN,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    SyntheticContextMarker,
    VipLabError,
    canonical_json_bytes,
    canonical_json_dumps,
    canonical_sha256,
    load_bounded_json_file,
    parse_strict_json_bytes,
    parse_strict_json_text,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)
# Do not eagerly import integration: every lab wave must collect independently.

__all__ = [
    "LAB_PROGRAM_VERSION",
    "MAX_LAB_JSON_BYTES",
    "SYNTHETIC_CONTEXT_TOKEN",
    "ReadinessFinding",
    "ReadinessPacket",
    "ReadinessStatus",
    "SyntheticContextMarker",
    "VipLabError",
    "canonical_json_bytes",
    "canonical_json_dumps",
    "canonical_sha256",
    "load_bounded_json_file",
    "parse_strict_json_bytes",
    "parse_strict_json_text",
    "sanitize_untrusted_authority_claims",
    "validate_hex_digest",
]
