"""Fail-closed contract gate evaluator for MEGA-08 capability & gap inventory.

Packet P08 — Capability & Gap Inventory (`LAB-MEGA-08-14-v1.0.0`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)
from .capability_inventory import (
    CapabilityEntry,
    build_capability_inventory,
)


STAGE_ID = "MEGA-08.CAPABILITY_INVENTORY"

_FORGED_GATE_KEYS = (
    "gate0_passed",
    "gate1_passed",
    "gate2_passed",
    "gate3_passed",
    "d3_authorized",
    "production_export_authorized",
    "authentic_model_loaded",
)


def inspect_capability_gate(payload: Mapping[str, Any]) -> ReadinessPacket:
    """Validate capability inventory inputs and emit a fail-closed ReadinessPacket."""
    if not isinstance(payload, Mapping):
        raise VipLabError("CAPABILITY_GATE_NOT_MAPPING", "payload must be a mapping")

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = ["GIT_SNAPSHOT_NOT_OBSERVED_ZIP_IMPORT"]
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="CAPABILITY_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted authority flags were stripped by MEGA-08 contract gate",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(cleaned.get("pr258_present", False)):
        code = "PR258_FORGED_PRESENCE_REFUSED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message="PR #258 is not merged in the imported ZIP snapshot and cannot be asserted as present",
                field_path="pr258_present",
            )
        )

    forged_gates = [k for k in _FORGED_GATE_KEYS if bool(cleaned.get(k, False))]
    if forged_gates:
        code = "FORGED_GATE_PROMOTION_REFUSED"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message=f"Forged gate promotion or execution claims refused: {forged_gates}",
                details={"forged_keys": forged_gates},
            )
        )

    raw_root = cleaned.get("workspace_root")
    if not isinstance(raw_root, (str, Path)) or not str(raw_root).strip():
        code = "CAPABILITY_WORKSPACE_ROOT_MISSING"
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=(code,),
            blockers=(code,),
            findings=(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message="workspace_root must be a non-empty path string",
                    field_path="workspace_root",
                ),
            ),
        )

    custom_caps_raw = cleaned.get("custom_capabilities")
    custom_caps: list[CapabilityEntry] | None = None
    if custom_caps_raw is not None:
        if not isinstance(custom_caps_raw, (list, tuple)):
            code = "CAPABILITY_CUSTOM_LIST_INVALID"
            return ReadinessPacket(
                stage_id=STAGE_ID,
                status=ReadinessStatus.INVALID,
                reasons=(code,),
                blockers=(code,),
            )
        custom_caps = []
        try:
            for idx, item in enumerate(custom_caps_raw):
                if not isinstance(item, Mapping):
                    raise VipLabError(
                        "CAPABILITY_ITEM_NOT_MAPPING",
                        f"custom_capabilities[{idx}] must be a mapping",
                    )
                custom_caps.append(
                    CapabilityEntry(
                        capability_id=str(item.get("capability_id", "")),
                        title=str(item.get("title", "")),
                        gate=str(item.get("gate", "")),
                        classification=str(item.get("classification", "")),
                        evidence_state=str(item.get("evidence_state", NOT_OBSERVED)),
                        source_paths=tuple(str(p) for p in item.get("source_paths", ())),
                        authority_blocker=(
                            str(item["authority_blocker"])
                            if item.get("authority_blocker") is not None
                            else None
                        ),
                    )
                )
        except VipLabError as exc:
            reasons.append(exc.code)
            blockers.append(exc.code)
            findings.append(
                ReadinessFinding(
                    code=exc.code,
                    status=ReadinessStatus.INVALID,
                    message=exc.message,
                    field_path=exc.field_path or "custom_capabilities",
                )
            )
            return ReadinessPacket(
                stage_id=STAGE_ID,
                status=ReadinessStatus.INVALID,
                reasons=tuple(reasons),
                blockers=tuple(blockers),
                findings=tuple(findings),
            )

    raw_expectations = cleaned.get("module_expectations")
    parsed_expectations: list[tuple[str, tuple[str, ...]]] | None = None
    if raw_expectations is not None:
        if not isinstance(raw_expectations, (list, tuple)):
            code = "CAPABILITY_MODULE_EXPECTATIONS_INVALID"
            return ReadinessPacket(
                stage_id=STAGE_ID,
                status=ReadinessStatus.INVALID,
                reasons=(code,),
                blockers=(code,),
            )
        parsed_expectations = []
        for item in raw_expectations:
            if (
                not isinstance(item, (list, tuple))
                or len(item) != 2
                or not isinstance(item[0], str)
                or not isinstance(item[1], (list, tuple))
            ):
                code = "CAPABILITY_MODULE_EXPECTATIONS_INVALID"
                return ReadinessPacket(
                    stage_id=STAGE_ID,
                    status=ReadinessStatus.INVALID,
                    reasons=(code,),
                    blockers=(code,),
                )
            parsed_expectations.append((item[0], tuple(str(s) for s in item[1])))

    try:
        report = build_capability_inventory(
            raw_root,
            module_expectations=parsed_expectations,
            capability_entries=custom_caps,
        )
    except VipLabError as exc:
        reasons.append(exc.code)
        blockers.append(exc.code)
        findings.append(
            ReadinessFinding(
                code=exc.code,
                status=ReadinessStatus.INVALID,
                message=exc.message,
                field_path=exc.field_path,
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
        )

    for mod_rec in report.module_inventory:
        if not mod_rec.exists:
            code = "INVENTORY_REQUIRED_MODULE_MISSING"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=f"Required module does not exist: {mod_rec.relative_path}",
                    field_path=mod_rec.relative_path,
                )
            )
        elif mod_rec.missing_symbols:
            code = "INVENTORY_REQUIRED_SYMBOL_MISSING"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=(
                        f"Module {mod_rec.relative_path} is missing symbols: "
                        f"{list(mod_rec.missing_symbols)}"
                    ),
                    field_path=mod_rec.relative_path,
                    details={"missing_symbols": list(mod_rec.missing_symbols)},
                )
            )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("CAPABILITY_INVENTORY_SYNTHETIC_READY")

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "inventory_digest": report.inventory_digest,
            "workspace_git_sha": report.workspace_git_sha,
            "declared_baseline_revision": report.declared_baseline_revision,
            "canonical_reference_sha": report.canonical_reference_sha,
            "module_count": len(report.module_inventory),
            "capability_count": len(report.capability_matrix),
            "report": report.to_dict(),
        },
    )
