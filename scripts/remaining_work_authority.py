from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

SHA256 = re.compile(r"^[0-9a-f]{64}$")
AUTHORITY_PATHS = {
    "task4_amendment": "docs/superpowers/specs/2026-10-02-g0-task4-post-task3-successor-amendment.md",
    "successor_spec": "docs/superpowers/specs/2026-09-27-g0-v7-task9-projection-dataflow-successor-spec.md",
    "successor_implementation_plan": "docs/superpowers/plans/2026-09-27-g0-v7-task9-projection-dataflow-successor-implementation-plan.md",
}


def validate_implementation_authority(
    root: Path,
    node: dict,
    prompt_core: dict,
    core_digest: str,
    operation_class: str,
) -> tuple[str | None, str | None]:
    """Return (problem, authorization_digest) for an explicitly required authority."""
    if node.get("implementation_authorization_required") is not True:
        return None, None

    ref = node.get("implementation_authorization_ref")
    if not isinstance(ref, dict):
        return "implementation_authorization_ref_missing", None
    rel = ref.get("path")
    declared_digest = ref.get("sha256")
    if (
        not isinstance(rel, str)
        or not rel
        or not isinstance(declared_digest, str)
        or SHA256.fullmatch(declared_digest) is None
    ):
        return "implementation_authorization_ref_invalid", None
    path = (root / rel).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return "implementation_authorization_ref_escapes_repository", None
    if not path.is_file():
        return "implementation_authorization_record_missing", None
    raw = path.read_bytes()
    actual_digest = hashlib.sha256(raw).hexdigest()
    if actual_digest != declared_digest:
        return "implementation_authorization_record_hash_mismatch", actual_digest
    try:
        record = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "implementation_authorization_record_invalid", actual_digest
    if not isinstance(record, dict):
        return "implementation_authorization_record_invalid", actual_digest

    supersession = record.get("supersession")
    if not isinstance(supersession, dict):
        return "implementation_authorization_record_invalid", actual_digest
    if (
        record.get("schema_version") != "owner-implementation-authorization.v1"
        or record.get("status") != "AUTHORIZED_FOR_IMPLEMENTATION_AND_TEST_EXECUTION"
        or not str(record.get("historical_state", "")).startswith("Tasks 4–12 were PARKED / NOT AUTHORIZED")
        or supersession.get("forward_only") is not True
        or supersession.get("non_retroactive") is not True
        or supersession.get("does_not_rewrite_historical_records") is not True
    ):
        return "implementation_authorization_record_not_current", actual_digest

    scope = record.get("scope")
    if not isinstance(scope, dict):
        return "implementation_authorization_record_invalid", actual_digest
    frozen_cores = scope.get("frozen_cores")
    if not isinstance(frozen_cores, dict):
        return "implementation_authorization_record_invalid", actual_digest
    task = frozen_cores.get(node.get("id"))
    if not isinstance(task, dict):
        return "implementation_authorization_task_not_covered", actual_digest
    if task.get("version") != prompt_core.get("version") or task.get(
        "core_md_sha256"
    ) != core_digest:
        return "implementation_authorization_core_mismatch", actual_digest
    core_meta_path = (root / node["prompt_core_ref"]).with_name("core.json")
    expected_json_digest = task.get("core_json_sha256")
    if (
        not isinstance(expected_json_digest, str)
        or SHA256.fullmatch(expected_json_digest) is None
        or not core_meta_path.is_file()
        or hashlib.sha256(core_meta_path.read_bytes()).hexdigest() != expected_json_digest
    ):
        return "implementation_authorization_core_mismatch", actual_digest

    authority_refs = record.get("authority_inputs")
    if not isinstance(authority_refs, dict):
        return "implementation_authorization_record_invalid", actual_digest
    if any(not isinstance(authority_refs.get(key), dict) for key in AUTHORITY_PATHS):
        return "implementation_authorization_record_invalid", actual_digest
    for key, expected_path in AUTHORITY_PATHS.items():
        ref_key = "successor_implementation_plan" if key == "successor_implementation_plan" else key
        ref = authority_refs.get(ref_key)
        blob = ref.get("blob") if isinstance(ref, dict) else None
        verified_at = ref.get("verified_at_commit") if isinstance(ref, dict) else None
        if (
            not isinstance(ref, dict)
            or ref.get("path") != expected_path
            or not isinstance(blob, str)
            or not re.fullmatch(r"[0-9a-f]{40}", blob)
            or not isinstance(verified_at, str)
            or not re.fullmatch(r"[0-9a-f]{40}", verified_at)
        ):
            return "implementation_authorization_governing_contract_mismatch", actual_digest
        verified_blob = subprocess.run(
            ["git", "-C", str(root), "rev-parse", f"{verified_at}:{expected_path}"],
            text=True,
            capture_output=True,
            check=False,
        )
        if verified_blob.returncode != 0 or verified_blob.stdout.strip() != blob:
            return "implementation_authorization_governing_blob_missing", actual_digest
    expected_contracts = {
        "gate0_task4_successor_amendment": authority_refs.get("task4_amendment", {}).get("blob"),
        "gate0_projection_successor_spec": authority_refs.get("successor_spec", {}).get("blob"),
        "gate0_projection_successor_plan": authority_refs.get("successor_implementation_plan", {}).get("blob"),
    }
    consumed_contracts = node.get("consumed_contracts")
    if not isinstance(consumed_contracts, list):
        return "implementation_authorization_governing_contract_mismatch", actual_digest
    consumed = {
        item.get("id"): item.get("fingerprint")
        for item in consumed_contracts
        if isinstance(item, dict)
    }
    if any(
        not isinstance(value, str)
        or consumed.get(contract_id) != value
        for contract_id, value in expected_contracts.items()
    ):
        return "implementation_authorization_governing_contract_mismatch", actual_digest

    operations = scope.get("operation_classes")
    if not isinstance(operations, list) or operation_class not in operations:
        return "implementation_authorization_operation_not_covered", actual_digest
    return None, actual_digest
