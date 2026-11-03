"""Deterministic, fail-closed validation for F03 evidence envelopes."""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from .preregistration import Preregistration

# Evidence classes are the five approved assertion-level classes. NOT_OBSERVED
# is an availability/status condition and never a class.
_EVIDENCE_CLASSES = {
    "MEASURED", "MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED",
    "EDITORIAL_INFERENCE",
}
# Only the current provenance-bearing envelope is admitted. The historical
# f03-evidence.v1 envelope has no reason provenance, so admitting it would
# silently downgrade current provenance to a declaration-only claim.
_EVIDENCE_VERSIONS = frozenset({"f03-evidence.v2"})
_ATTEMPT_4 = re.compile(r"attempt0*4(?!\d)")
_NOT_OBSERVED_PROVENANCE_STATES = frozenset({"UNAVAILABLE", "INFERRED"})
_CONTRACT_FIELDS = {"dependency_heads", "preregistration_path", "preregistration_digest", "freeze_digest", "workload_digest", "config_digest",
                    "fault_schedule_digest", "metric_definitions", "decision_digest", "candidate"}
_EVIDENCE_FIELDS = _CONTRACT_FIELDS | {"version", "observations"}
_OBSERVATION_FIELDS = frozenset({
    "metric_id", "status", "value", "unit", "evidence_class", "carrier_path",
    "carrier_sha256", "dependency_id", "dependency_heads", "candidate",
    "preregistration_digest", "freeze_digest", "workload_digest", "config_digest",
    "fault_schedule_digest", "repetition", "reason_provenance",
})
_REASON_PROVENANCE_FIELDS = frozenset({
    "schema_version", "state", "reason_code", "evidence_identity",
})
_REASON_CODES = {
    "MEASURED": "OBSERVED",
    "UNAVAILABLE": "SOURCE_UNAVAILABLE",
    "INFERRED": "CONTEXT_INFERENCE",
}
_F01_CONSUMED_CONTRACT_IDS = frozenset({
    "gate2_synthetic_candidate", "gate2_reconciliation", "canonical_contracts",
    "resource_policy_v5", "gate2_protocol_candidate", "gate2_measure_candidate",
    "gate2_preregistration_schema_candidate", "gate2_measurement_schema_candidate",
})
# Every consumed contract fingerprint is resolved from committed git objects,
# never from worktree bytes. Fingerprint declarations alone never authorize the
# freeze.
_F01_CONSUMED_CONTRACT_PATHS = {
    "gate2_reconciliation": "docs/audits/2026-09-13-portfolio-state-reconciliation-after-gate2-m3.md",
    "canonical_contracts": "docs/architecture/CANONICAL_CONTRACTS.md",
    "resource_policy_v5": "docs/portfolio/portfolio-v1/resource-policy-v5.yaml",
    "gate2_measure_candidate": "src/gate2/measure.py",
    "gate2_preregistration_schema_candidate": "schemas/gate2/preregistration.json",
    "gate2_measurement_schema_candidate": "schemas/gate2/measurement.json",
}
_F01_CONSUMED_OBJECT_CONTRACTS = {
    "gate2_synthetic_candidate": {
        "kind": "commit",
        "commit": "88bff2e1be00bf3717a48c00a3529cabce3d16b5",
    },
    "gate2_protocol_candidate": {
        "kind": "blob",
        "commit": "88bff2e1be00bf3717a48c00a3529cabce3d16b5",
        "path": "src/gate2/protocol.py",
    },
}
_F01_RESOURCE_POLICY = {
    "schema_version": 5,
    "resource_leases": {
        "HEAVY_CPU": {
            "policy": "ADAPTIVE_MEASURED_LEASE",
            "initial_max_concurrent": 2,
            "calibration_target_max_concurrent": 3,
            "fallback_max_concurrent": 1,
        },
    },
}
_ACCEPTED_DEPENDENCY_HEADS = {
    "F01": {"sha": "345f9526d54f4fbd582c15f4b0f613bc8ab3996e", "tree": "daea7e43cfae051a56927daaf51da5e2a221759d"},
    "F02": {"sha": "d8c42ba7c276e8df86991904efaf0dc09ed5fd01", "tree": "720459d545f387688bd1eae1c9a5656d39b75aee"},
}
_GIT_TIMEOUT_SECONDS = 10


class ProvenanceError(ValueError):
    """A consumed contract or accepted generation could not be proven."""


def _git(git_root: str | Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(git_root), *args],
            capture_output=True, text=True, timeout=_GIT_TIMEOUT_SECONDS, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProvenanceError(f"git object resolution unavailable: {exc}") from exc


def discover_git_root(start: str | Path) -> Path | None:
    """Resolve the repository that owns an evidence root; None when absent."""
    try:
        resolved = Path(start).resolve()
    except OSError:
        return None
    probe = resolved if resolved.is_dir() else resolved.parent
    try:
        completed = subprocess.run(
            ["git", "-C", str(probe), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=_GIT_TIMEOUT_SECONDS, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    root = completed.stdout.strip()
    return Path(root) if root else None


def git_blob_sha(data: bytes) -> str:
    """Git object identity of blob content (sha1 over the canonical header)."""
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _blob_at(git_root: Path, commit: str, relative: Path) -> str:
    probe = _git(git_root, "rev-parse", "--verify", f"{commit}:{relative.as_posix()}")
    if probe.returncode != 0:
        raise ProvenanceError(
            f"consumed contract source is absent from the accepted generation: {relative.as_posix()}"
        )
    blob = probe.stdout.strip()
    kind = _git(git_root, "cat-file", "-t", blob)
    if kind.returncode != 0 or kind.stdout.strip() != "blob":
        raise ProvenanceError(f"consumed contract is not a blob: {relative.as_posix()}")
    return blob


def _blob_text(git_root: Path, blob: str) -> str:
    """Read a blob's committed content without touching the worktree."""
    completed = _git(git_root, "cat-file", "blob", blob)
    if completed.returncode != 0:
        raise ProvenanceError(f"consumed contract blob cannot be read: {blob}")
    return completed.stdout


def resolve_accepted_heads(git_root: str | Path) -> dict[str, dict[str, str]]:
    """Require the accepted F01/F02 commits and their declared trees to exist."""
    root = Path(git_root)
    resolved: dict[str, dict[str, str]] = {}
    for generation, head in _ACCEPTED_DEPENDENCY_HEADS.items():
        kind = _git(root, "cat-file", "-t", head["sha"])
        if kind.returncode != 0 or kind.stdout.strip() != "commit":
            raise ProvenanceError(f"accepted {generation} commit cannot be resolved")
        tree = _git(root, "rev-parse", "--verify", f"{head['sha']}^{{tree}}")
        if tree.returncode != 0 or tree.stdout.strip() != head["tree"]:
            raise ProvenanceError(f"accepted {generation} tree does not match its declared identity")
        resolved[generation] = {"sha": head["sha"], "tree": head["tree"]}
    return resolved


def resolve_contract_fingerprints(git_root: str | Path) -> dict[str, str]:
    """Derive the current F01 consumed-contract fingerprints from real objects."""
    root = Path(git_root)
    fingerprints: dict[str, str] = {}
    accepted_f01 = _ACCEPTED_DEPENDENCY_HEADS["F01"]["sha"]
    for contract_id, relative_text in _F01_CONSUMED_CONTRACT_PATHS.items():
        # Every consumed contract is bound to the accepted F01 generation, never
        # to whatever bytes happen to be in the current worktree.
        fingerprints[contract_id] = _blob_at(root, accepted_f01, Path(relative_text))
    for contract_id, spec in _F01_CONSUMED_OBJECT_CONTRACTS.items():
        kind = _git(root, "cat-file", "-t", spec["commit"])
        if kind.returncode != 0 or kind.stdout.strip() != "commit":
            raise ProvenanceError(f"certified contract generation cannot be resolved: {contract_id}")
        if spec["kind"] == "commit":
            fingerprints[contract_id] = spec["commit"]
        else:
            fingerprints[contract_id] = _blob_at(root, spec["commit"], Path(spec["path"]))
    if set(fingerprints) != set(_F01_CONSUMED_CONTRACT_IDS):
        raise ProvenanceError("consumed-contract fingerprint set is incomplete")
    return fingerprints


def _resource_policy_lease(policy_text: str) -> dict[str, Any]:
    """Extract the HEAVY_CPU lease declaration from resource-policy-v5 YAML.

    A deliberately narrow indentation parse keeps the verifier dependency-free
    while still binding the lease semantics to the real consumed policy file.
    """
    schema_version: int | None = None
    in_leases = False
    lease: dict[str, Any] = {}
    in_heavy = False
    for raw_line in policy_text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not raw_line.startswith(" "):
            in_leases = stripped == "resource_leases:"
            in_heavy = False
            if stripped.startswith("schema_version:"):
                value = stripped.split(":", 1)[1].strip()
                if value.isdigit():
                    schema_version = int(value)
            continue
        if in_leases:
            if raw_line.startswith("  ") and not raw_line.startswith("    ") and stripped.endswith(":"):
                in_heavy = stripped == "HEAVY_CPU:"
                continue
            if in_heavy and raw_line.startswith("    "):
                if ":" not in stripped:
                    raise ProvenanceError("HEAVY_CPU lease declaration is malformed")
                key, value = (part.strip() for part in stripped.split(":", 1))
                lease[key] = int(value) if value.isdigit() else value
    if schema_version is None:
        raise ProvenanceError("resource policy schema version is unavailable")
    if not lease:
        raise ProvenanceError("HEAVY_CPU lease declaration is absent from resource policy v5")
    return {"schema_version": schema_version, "HEAVY_CPU": lease}


def resolve_gate2_provenance(git_root_text: str) -> dict[str, Any]:
    """Resolve accepted generations, consumed fingerprints and policy semantics.

    Deliberately uncached: a long-lived process must never verify against stale
    provenance after the repository moves.
    """
    root = Path(git_root_text)
    heads = resolve_accepted_heads(root)
    consumed = resolve_contract_fingerprints(root)
    policy_path = Path(_F01_CONSUMED_CONTRACT_PATHS["resource_policy_v5"])
    policy_blob = consumed["resource_policy_v5"]
    policy_text = _blob_text(root, policy_blob)
    lease = _resource_policy_lease(policy_text)
    expected_lease = _F01_RESOURCE_POLICY["resource_leases"]["HEAVY_CPU"]
    if lease["schema_version"] != _F01_RESOURCE_POLICY["schema_version"] or lease["HEAVY_CPU"] != expected_lease:
        raise ProvenanceError("resource policy v5 lease semantics do not match the frozen projection")
    return {"heads": heads, "consumed": consumed, "resource_policy": _F01_RESOURCE_POLICY}


def _normalize_attempt_token(value: str) -> str:
    """Strip every separator so Attempt-4 cannot hide behind punctuation."""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def canonical_digest(value: Any) -> str:
    """SHA-256 of canonical UTF-8 JSON (sorted keys, compact separators)."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                         allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_evidence(evidence: Mapping[str, Any], expected_contract: Mapping[str, Any], *, carrier_root: str | Path | None = None,
                    git_root: str | Path | None = None) -> dict[str, Any]:
    """Validate identity, carriers and decision binding; any defect rejects the envelope."""
    errors: list[str] = []
    if not isinstance(evidence, Mapping) or not isinstance(expected_contract, Mapping):
        errors.append("evidence and expected_contract must be objects")
        return _result(errors)
    provenance: dict[str, Any] | None = None
    provenance_source = git_root if git_root is not None else carrier_root
    if provenance_source is None:
        errors.append("git-object provenance unavailable: a repository root is required")
    else:
        discovered = discover_git_root(provenance_source)
        if discovered is None:
            errors.append("git-object provenance unavailable: evidence root is not inside a Git repository")
        else:
            try:
                provenance = resolve_gate2_provenance(str(discovered))
            except ProvenanceError as exc:
                errors.append(f"git-object provenance unavailable: {exc}")
    accepted_heads = provenance["heads"] if provenance is not None else _ACCEPTED_DEPENDENCY_HEADS
    consumed_contracts = provenance["consumed"] if provenance is not None else None
    resource_policy = provenance["resource_policy"] if provenance is not None else _F01_RESOURCE_POLICY
    if set(expected_contract) != _CONTRACT_FIELDS:
        errors.append("expected contract is incomplete or has unknown fields")
    for key in ("preregistration_digest", "freeze_digest", "workload_digest", "config_digest", "fault_schedule_digest"):
        value = expected_contract.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            errors.append(f"invalid {key}")
    deps = expected_contract.get("dependency_heads")
    if not isinstance(deps, Mapping) or set(deps) != {"F01", "F02"} or any(
        not isinstance(v, Mapping) or len(v.get("sha", "")) != 40 or len(v.get("tree", "")) != 40
        for v in deps.values()
    ):
        errors.append("invalid dependency heads")
    elif deps != accepted_heads:
        errors.append("dependency heads do not match the accepted F01/F02 candidates")
    candidate = expected_contract.get("candidate")
    if not isinstance(candidate, Mapping) or any(
        not isinstance(candidate.get(k), str) or len(candidate[k]) != 40 or any(c not in "0123456789abcdef" for c in candidate[k])
        for k in ("sha", "tree")
    ):
        errors.append("invalid candidate identity")
    elif isinstance(deps, Mapping) and candidate != deps.get("F02"):
        errors.append("candidate must match the pinned F02 head")
    digest = expected_contract.get("decision_digest")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        errors.append("invalid expected decision digest")
    metrics = expected_contract.get("metric_definitions")
    if not isinstance(metrics, Mapping) or not metrics:
        errors.append("invalid metric definitions")
    else:
        for name, definition in metrics.items():
            if not isinstance(definition, Mapping):
                errors.append(f"invalid definition for {name}")
                continue
            unit = definition.get("unit")
            if not isinstance(unit, str) or not unit:
                errors.append(f"invalid unit for {name}")
            reps = definition.get("repetitions")
            if isinstance(reps, bool) or not isinstance(reps, int) or reps < 1:
                errors.append(f"invalid repetitions for {name}")
            limits = [definition.get(k) for k in ("min", "max") if k in definition]
            if not limits or any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in limits):
                errors.append(f"invalid numeric bounds for {name}")
    root = Path(carrier_root).resolve() if carrier_root is not None else None
    payload: Mapping[str, Any] | None = None
    prereg_path_value = expected_contract.get("preregistration_path")
    if not isinstance(prereg_path_value, str) or not prereg_path_value:
        errors.append("invalid preregistration path")
    elif root is None:
        errors.append("carrier root required to verify preregistration")
    else:
        relative_prereg = Path(prereg_path_value)
        resolved_prereg = (root / relative_prereg).resolve()
        if relative_prereg.is_absolute() or not resolved_prereg.is_relative_to(root):
            errors.append("preregistration path escapes evidence root")
        else:
            try:
                prereg_bytes = resolved_prereg.read_bytes()
                if hashlib.sha256(prereg_bytes).hexdigest() != expected_contract.get("preregistration_digest"):
                    errors.append("preregistration digest does not match carrier")
                preregistration = json.loads(prereg_bytes)
                if not isinstance(preregistration, Mapping):
                    errors.append("preregistration must be an object")
                else:
                    freeze_digest = preregistration.get("freeze_digest")
                    payload = {key: value for key, value in preregistration.items() if key != "freeze_digest"}
                    if consumed_contracts is None:
                        errors.append("preregistration admission requires resolved git provenance")
                        frozen = None
                    else:
                        frozen = Preregistration.from_payload(
                            payload,
                            consumed_contracts=consumed_contracts,
                            resource_policy=resource_policy,
                        ).seal()
                    if frozen is not None and (not isinstance(freeze_digest, str) or freeze_digest != frozen.freeze_digest):
                        errors.append("preregistration freeze digest does not match canonical F01 payload")
                    if frozen is not None and frozen.canonical_bytes() != prereg_bytes:
                        errors.append("preregistration bytes are not canonical F01 schema-v1 bytes")
                    if frozen is not None and expected_contract.get("freeze_digest") != frozen.freeze_digest:
                        errors.append("expected freeze digest does not match F01 preregistration")
                    if expected_contract.get("workload_digest") != payload["workload_identity"]["digest"]:
                        errors.append("expected workload digest does not match F01 preregistration")
                    if expected_contract.get("config_digest") != payload["configuration_identity"]["digest"]:
                        errors.append("expected configuration digest does not match F01 preregistration")
                    if expected_contract.get("fault_schedule_digest") != canonical_digest(payload["fault_schedule"]):
                        errors.append("expected fault schedule digest does not match F01 preregistration")
                    if deps != accepted_heads:
                        errors.append("expected dependency heads do not match accepted F01/F02 candidates")
                    if payload.get("dependency_generations") != {
                        "F01": accepted_heads["F01"]["sha"],
                        "F02": accepted_heads["F02"]["sha"],
                    }:
                        errors.append("preregistration generations do not bind accepted F01/F02 heads")
                    derived: dict[str, dict[str, Any]] = {}
                    for item in payload["metrics"]:
                        metric_id = item["name"]
                        if metric_id not in payload["numeric_bounds"]:
                            errors.append(f"preregistration has no numeric bound for {metric_id}")
                            continue
                        if metric_id in derived:
                            errors.append(f"duplicate preregistration metric {metric_id}")
                        derived[metric_id] = {
                            "unit": item["unit"],
                            "min": 0,
                            "max": payload["numeric_bounds"][metric_id],
                            "repetitions": payload["fault_schedule"]["repetitions"],
                        }
                    if derived != metrics:
                        errors.append("metric definitions are not preregistration-derived")
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError, KeyError, TypeError, ValueError):
                errors.append("preregistration unavailable or invalid JSON")
    if set(evidence) != _EVIDENCE_FIELDS:
        errors.append("evidence envelope is incomplete or has unknown fields")
    envelope_version = evidence.get("version")
    if envelope_version not in _EVIDENCE_VERSIONS:
        errors.append(
            "unsupported evidence envelope version; only f03-evidence.v2 with reason provenance is admitted"
        )
    declarations: Mapping[str, Any] | None = None
    if isinstance(payload, Mapping):
        declared = payload.get("evidence_declarations")
        if not isinstance(declared, Mapping) or not declared:
            errors.append("preregistration evidence declarations are required")
        else:
            declarations = declared
            preregistered_metrics = {
                item["name"] for item in payload.get("metrics", ()) if isinstance(item, Mapping) and "name" in item
            }
            if set(declared) != preregistered_metrics:
                missing = sorted(preregistered_metrics - set(declared))
                extra = sorted(set(declared) - preregistered_metrics)
                errors.append(
                    "evidence declarations must cover exactly the preregistered metrics"
                    + (f"; missing {missing}" if missing else "")
                    + (f"; undeclared metrics {extra}" if extra else "")
                )
    if not isinstance(payload, Mapping) and not errors:
        errors.append("preregistration payload is required for evidence declarations")
    for key in ("dependency_heads", "preregistration_path", "preregistration_digest", "freeze_digest", "workload_digest", "config_digest", "fault_schedule_digest", "metric_definitions"):
        if evidence.get(key) != expected_contract.get(key):
            errors.append(f"{key} identity mismatch")
    if evidence.get("candidate") != expected_contract.get("candidate"):
        errors.append("candidate identity mismatch")
    observations = evidence.get("observations")
    if not isinstance(observations, list):
        errors.append("observations must be an array")
        observations = []
    counts: Counter[str] = Counter()
    measured_counts: Counter[str] = Counter()
    repetitions_seen: dict[str, set[int]] = {}
    for item in observations:
        if not isinstance(item, Mapping):
            errors.append("observation must be an object")
            continue
        unknown_fields = set(item) - _OBSERVATION_FIELDS
        if unknown_fields:
            errors.append(f"unknown observation fields: {sorted(unknown_fields)}")
            continue
        if envelope_version in _EVIDENCE_VERSIONS:
            reason_provenance = item.get("reason_provenance")
            if not isinstance(reason_provenance, Mapping):
                errors.append("v2 reason provenance is required")
            elif set(reason_provenance) != _REASON_PROVENANCE_FIELDS:
                errors.append("reason provenance has missing or unknown fields")
            else:
                state = reason_provenance.get("state")
                if reason_provenance.get("schema_version") != "gate2.reason-provenance.v1":
                    errors.append("unsupported reason provenance schema version")
                if not isinstance(state, str) or state not in _REASON_CODES or reason_provenance.get("reason_code") != _REASON_CODES.get(state):
                    errors.append("reason provenance state and reason code conflict")
                expected_identity = {
                    key: item.get(key)
                    for key in ("metric_id", "repetition", "status", "value", "unit", "dependency_id",
                                "evidence_class", "carrier_path", "carrier_sha256",
                                "dependency_heads", "candidate",
                                "preregistration_digest", "freeze_digest", "workload_digest",
                                "config_digest", "fault_schedule_digest")
                }
                if reason_provenance.get("evidence_identity") != expected_identity:
                    errors.append("reason provenance evidence identity is stale or conflicting")
                if item.get("status") == "NOT_OBSERVED" and state not in _NOT_OBSERVED_PROVENANCE_STATES:
                    errors.append(
                        "NOT_OBSERVED reason provenance must be UNAVAILABLE or CONTEXT_INFERENCE-derived"
                    )
                if item.get("status") == "MEASURED" and state != "MEASURED":
                    errors.append("MEASURED evidence requires MEASURED reason provenance")
        metric = item.get("metric_id")
        if not isinstance(metric, str):
            errors.append("invalid observation metric identity")
            continue
        definition = metrics.get(metric) if isinstance(metrics, Mapping) else None
        if not isinstance(definition, Mapping):
            errors.append("unknown metric carrier")
            continue
        counts[metric] += 1
        if item.get("status") == "MEASURED":
            measured_counts[metric] += 1
        if item.get("unit") != definition.get("unit"):
            errors.append(f"carrier unit mismatch for {metric}")
        if item.get("status") not in {"MEASURED", "NOT_OBSERVED"}:
            errors.append(f"invalid evidence status for {metric}")
        reported_class = item.get("evidence_class")
        if reported_class is not None and (
            not isinstance(reported_class, str) or reported_class not in _EVIDENCE_CLASSES
        ):
            errors.append(f"invalid evidence class for {metric}")
        if item.get("status") == "MEASURED" and item.get("evidence_class") != "MEASURED":
            errors.append(f"non-measured evidence class for measured carrier {metric}")
        if isinstance(declarations, Mapping) and item.get("status") == "MEASURED":
            declared_class = declarations.get(metric)
            if declared_class is None:
                errors.append(f"measured carrier has no preregistered evidence declaration for {metric}")
            elif declared_class != item.get("evidence_class"):
                errors.append(
                    f"measured evidence class does not match the preregistered declaration for {metric}"
                )
        if item.get("status") == "NOT_OBSERVED" and item.get("evidence_class") is not None:
            errors.append(f"NOT_OBSERVED must not claim an evidence class for {metric}")
        for key in ("preregistration_digest", "freeze_digest", "workload_digest", "config_digest", "fault_schedule_digest"):
            if item.get(key) != expected_contract.get(key):
                errors.append(f"carrier {key} mismatch for {metric}")
        if item.get("dependency_heads") != expected_contract.get("dependency_heads"):
            errors.append(f"carrier dependency heads mismatch for {metric}")
        if item.get("candidate") != expected_contract.get("candidate"):
            errors.append(f"candidate identity mismatch for {metric}")
        dependency_id = item.get("dependency_id")
        dependency_heads = expected_contract.get("dependency_heads", {})
        if dependency_id not in {"F01", "F02", "F01+F02"}:
            errors.append(f"unknown dependency source for {metric}")
        elif ("F01" in dependency_id and "F01" not in dependency_heads) or (
                "F02" in dependency_id and "F02" not in dependency_heads):
            errors.append(f"dependency source is not pinned for {metric}")
        if item.get("candidate") != expected_contract.get("candidate"):
            errors.append(f"dependency source/candidate mismatch for {metric}")
        carrier_path = item.get("carrier_path")
        if isinstance(dependency_id, str) and _ATTEMPT_4.search(_normalize_attempt_token(dependency_id)):
            errors.append(f"historical Attempt-4 cannot provide a current carrier for {metric}")
        if isinstance(carrier_path, str) and _ATTEMPT_4.search(_normalize_attempt_token(carrier_path)):
            errors.append(f"historical Attempt-4 path cannot provide a current carrier for {metric}")
        if item.get("status") == "MEASURED":
            carrier_hash = item.get("carrier_sha256")
            if not isinstance(item.get("carrier_path"), str) or not isinstance(carrier_hash, str) or len(carrier_hash) != 64 or any(c not in "0123456789abcdef" for c in carrier_hash):
                errors.append(f"measured carrier provenance missing for {metric}")
            elif root is None:
                errors.append(f"carrier root required for measured carrier {metric}")
            else:
                rel = Path(item["carrier_path"])
                candidate_path = (root / rel).resolve()
                if rel.is_absolute() or not candidate_path.is_relative_to(root):
                    errors.append(f"carrier path escapes evidence root for {metric}")
                else:
                    try:
                        raw = candidate_path.read_bytes()
                        if hashlib.sha256(raw).hexdigest() != carrier_hash:
                            errors.append(f"carrier content hash mismatch for {metric}")
                        else:
                            carrier = json.loads(raw)
                            records = carrier if isinstance(carrier, list) else carrier.get("observations") if isinstance(carrier, Mapping) else None
                            if not isinstance(records, list):
                                errors.append(f"carrier has no observation records for {metric}")
                            else:
                                rep = item.get("repetition")
                                matches = [row for row in records if isinstance(row, Mapping) and row.get("repetition") == rep]
                                if len(matches) != 1:
                                    errors.append(f"carrier repetition missing or ambiguous for {metric}")
                                else:
                                    row = matches[0]
                                    if row.get("metric_id") != metric:
                                        errors.append(
                                            f"carrier observation metric identity mismatch for {metric}"
                                        )
                                    if row.get("unit") != item.get("unit") or row.get("value") != item.get("value"):
                                        errors.append(f"carrier observation mismatch for {metric}")
                            if isinstance(carrier, Mapping) and carrier.get("metric_id", metric) != metric:
                                errors.append(f"carrier metric identity mismatch for {metric}")
                    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
                        errors.append(f"carrier unavailable or invalid JSON for {metric}")
        elif item.get("value") is not None or item.get("carrier_path") is not None or item.get("carrier_sha256") is not None:
            errors.append(f"NOT_OBSERVED carrier contains measured value/provenance for {metric}")
        value = item.get("value")
        if item.get("status") == "MEASURED" and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)):
            errors.append(f"missing numeric carrier for {metric}")
        if isinstance(item.get("repetition"), bool) or not isinstance(item.get("repetition"), int):
            errors.append(f"invalid repetition index for {metric}")
        elif not isinstance(definition.get("repetitions"), int) or item["repetition"] < 1 or item["repetition"] > definition["repetitions"]:
            errors.append(f"repetition index outside contract for {metric}")
        else:
            seen = repetitions_seen.setdefault(metric, set())
            if item["repetition"] in seen:
                errors.append(f"duplicate repetition index for {metric}")
            seen.add(item["repetition"])
    if isinstance(metrics, Mapping):
        for metric in metrics:
            reps = metrics[metric].get("repetitions", 0)
            if counts[metric] != reps:
                errors.append(f"carrier repetition count mismatch for {metric}")
    if evidence.get("decision_digest") != expected_contract.get("decision_digest"):
        errors.append("decision digest mismatch")
    declared_without_observation = sorted(
        metric for metric, declared_class in (declarations or {}).items()
        if declared_class == "MEASURED" and not measured_counts.get(metric, 0)
    )
    return _result(errors, declared_without_observation=declared_without_observation)


def _result(errors: list[str], *, declared_without_observation: list[str] | None = None) -> dict[str, Any]:
    return {
        "verified": not errors,
        "errors": errors,
        "production_eligible": False,
        "gate_promotion": False,
        "mechanism_adopted": False,
        # A declared-MEASURED metric with no measured row is disclosed rather
        # than silently counted as covered evidence.
        "declared_measured_without_observation": list(declared_without_observation or ()),
    }
