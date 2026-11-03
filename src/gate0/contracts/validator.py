"""Cross-artifact validation which cannot be expressed by JSON Schema.

The validator deliberately consumes the candidate artifact set.  In
particular, policy ids are resolved from the serialized policy and
authorization records; a caller supplied list of ids is not evidence of a
foreign-key relationship.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

from gate0.failure import membership_digest


ARTIFACT_FILENAMES = (
    "source_manifest.json", "discovery_authorizations.jsonl",
    "policy_decisions.jsonl", "split_manifest.json", "queries.jsonl",
    "gold_events.jsonl", "window_judgments.jsonl",
    "window_sample_manifest.jsonl", "run_manifest.json",
    "ranked_candidates.jsonl", "runtime_and_failure_ledger.json",
    "metrics.json", "gate_decision.md",
)

DISCOVERY_TYPES = ("source_manifest", "discovery_authorization")
DISCOVERY_OPERATIONS = {"DISCOVER", "HASH", "PROBE"}
PURPOSE_BY_OPERATION = {
    "DISCOVER": "DISCOVER", "HASH": "DISCOVER", "PROBE": "DISCOVER",
    "PROCESS": "PROCESS", "CACHE_READ": "CACHE_READ",
    "PROJECTION_READ": "PROJECTION_READ",
}
_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,127}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Raised when a candidate artifact set is not contract-valid."""


def _fail(message: str) -> None:
    raise ContractError(message)


def _record_payload(value: Any) -> Mapping[str, Any]:
    """Return a payload while retaining support for record/envelope fixtures."""
    if not isinstance(value, Mapping):
        _fail("artifact must be an object")
    payload = value.get("payload", value)
    if not isinstance(payload, Mapping):
        _fail("artifact payload must be an object")
    return payload


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping) and "records" in value:
        value = value["records"]
    if isinstance(value, Mapping):
        return [_record_payload(value)]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_record_payload(item) for item in value]
    _fail("JSONL artifact must contain records")


def _artifact_payloads(candidate: Any) -> Mapping[str, Any]:
    if isinstance(candidate, Mapping) and "artifacts" in candidate:
        candidate = candidate["artifacts"]
    if not isinstance(candidate, Mapping):
        _fail("candidate artifact set must be a mapping")
    names = tuple(candidate)
    if len(names) != len(ARTIFACT_FILENAMES) or set(names) != set(ARTIFACT_FILENAMES):
        _fail("artifact set must contain exactly 13 named files")
    return candidate


def _get(payload: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    return default


def _id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        _fail(f"invalid {label}")
    return value


def _digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        _fail(f"invalid {label}")
    return value


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _parse_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        _fail(f"invalid {label}")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"invalid {label}") from exc
    if result.tzinfo is None:
        _fail(f"invalid {label}")
    return result.astimezone(timezone.utc)


def _envelopes(candidate: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    """Collect envelopes from top-level wrappers or run_manifest payload."""
    result: dict[str, Mapping[str, Any]] = {}
    run = _record_payload(candidate["run_manifest.json"])
    envs = _get(run, "artifact_envelopes", "envelopes", default=[])
    if isinstance(envs, Mapping):
        envs = list(envs.values())
    if isinstance(envs, Sequence) and not isinstance(envs, (str, bytes, bytearray)):
        for item in envs:
            if isinstance(item, Mapping):
                typ = item.get("artifact_type")
                if isinstance(typ, str):
                    result[_artifact_filename(typ)] = item
    for name in ("source_manifest.json", "discovery_authorizations.jsonl"):
        wrapper = candidate[name]
        if isinstance(wrapper, Mapping):
            env = wrapper.get("envelope")
            if isinstance(env, Mapping):
                result[name] = env
    return result


def _artifact_filename(value: str) -> str:
    if value in ARTIFACT_FILENAMES:
        return value
    return {
        "source_manifest": "source_manifest.json",
        "discovery_authorization": "discovery_authorizations.jsonl",
        "policy_decision": "policy_decisions.jsonl",
    }.get(value, value)


def _validate_envelope_refs(candidate: Mapping[str, Any], envs: Mapping[str, Mapping[str, Any]]) -> None:
    """Resolve typed refs against envelope IDs and digests when envelopes exist."""
    by_id: dict[str, tuple[str, str]] = {}
    for filename, env in envs.items():
        if _artifact_filename(str(env.get("artifact_type", filename))) != filename:
            _fail("artifact envelope owner/type mismatch")
        artifact_id = _id(env.get("artifact_id"), f"{filename} artifact_id")
        digest = _digest(env.get("payload_digest"), f"{filename} payload_digest")
        if artifact_id in by_id:
            _fail("duplicate artifact envelope id")
        by_id[artifact_id] = (filename, digest)
    for env in envs.values():
        refs = env.get("input_artifact_refs", ())
        if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes, bytearray)):
            _fail("input_artifact_refs must be an array")
        for ref in refs:
            if not isinstance(ref, Mapping) or set(ref) != {"artifact_id", "payload_digest", "artifact_type"}:
                _fail("typed artifact reference required")
            aid = _id(ref.get("artifact_id"), "artifact reference artifact_id")
            digest = _digest(ref.get("payload_digest"), "artifact reference payload_digest")
            typ = _artifact_filename(ref.get("artifact_type"))
            target = by_id.get(aid)
            if target is None or target[0] != typ or target[1] != digest:
                _fail("unresolved or wrong-digest artifact reference")


def _source_revision_ids(source: Mapping[str, Any]) -> tuple[str, ...]:
    """Resolve the canonical source revision inventory (source_manifest owner)."""
    revisions = _get(source, "revision_ids")
    if revisions is None and isinstance(source.get("source_records"), Sequence):
        revisions = [_get(_record_payload(row), "revision_id") for row in source["source_records"]]
    if revisions is None:
        revisions = [r.get("revision_id") for r in _rows(source.get("records", source))] if "records" in source else [source.get("revision_id")]
    if not isinstance(revisions, Sequence) or isinstance(revisions, (str, bytes, bytearray)) or not revisions:
        _fail("source manifest revision inventory is empty")
    return tuple(_id(v, "revision_id") for v in revisions)


def _validate_discovery(candidate: Mapping[str, Any]) -> None:
    source = _record_payload(candidate["source_manifest.json"])
    policies = _rows(candidate["policy_decisions.jsonl"])
    auths = _rows(candidate["discovery_authorizations.jsonl"])
    if not auths:
        _fail("discovery authorization rows are required")

    # A discovery authorization owns only the scalar FK.  This catches both
    # per-row decisions and the old duplicated/embedded decision defect.
    auth_ids: list[str] = []
    for row in auths:
        if "discovery_policy_decision" in row or "policy_decision" in row or isinstance(row.get("decision"), Mapping):
            _fail("embedded policy decision in discovery authorization")
        auth_ids.append(_id(row.get("policy_decision_id"), "policy_decision_id"))
    if len(set(auth_ids)) != 1:
        _fail("all discovery authorization rows must reference one policy decision")
    decision_id = auth_ids[0]
    matches = [p for p in policies if p.get("policy_decision_id") == decision_id]
    if len(matches) != 1:
        _fail("discovery policy foreign key must resolve exactly once")
    decision = matches[0]
    if _get(decision, "purpose") != "DISCOVER" or _get(decision, "decision") != "ALLOW":
        _fail("discovery policy must be DISCOVER/ALLOW")
    allowed = _get(decision, "allowed_artifact_types")
    if tuple(allowed or ()) != DISCOVERY_TYPES:
        _fail("discovery policy allowed artifact types mismatch")

    revision_tuple = _source_revision_ids(source)
    scope = _get(decision, "revision_scope")
    if tuple(scope or ()) != revision_tuple:
        _fail("discovery policy revision scope mismatch")
    expires = _get(decision, "expires_at")
    if expires is not None and _parse_time(expires, "policy expiry") <= datetime.now(timezone.utc):
        _fail("discovery policy is expired")
    if _get(decision, "revoked", "revocation_ref") not in (None, False, ""):
        _fail("discovery policy is revoked")

    envs = _envelopes(candidate)
    _validate_envelope_refs(candidate, envs)
    ids = []
    for name in ("source_manifest.json", "discovery_authorizations.jsonl"):
        env = envs.get(name)
        if env is not None:
            ids.append(_id(env.get("policy_decision_id"), f"{name} policy_decision_id"))
    if ids and (len(ids) != 2 or any(item != decision_id for item in ids)):
                _fail("discovery envelopes must reference the same policy decision")


ARM_REPRESENTATION_KINDS = ("metadata_floor", "embedding")


def _validate_arm_registry(run: Mapping[str, Any]) -> dict[str, str]:
    """Resolve the closed per-run arm registry (D8/Q1=A).

    The run manifest declares every scored arm with an explicit representation
    kind.  Duplicate arm ids, unknown kinds or a malformed entry are contract
    violations; an absent registry is reported separately because it is only
    required once an arm-scoped artifact exists.
    """
    raw = run.get("arms", [])
    if raw is None:
        raw = []
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        _fail("arm registry must be an array")
    arms: dict[str, str] = {}
    for entry in raw:
        if not isinstance(entry, Mapping):
            _fail("arm registry entry must be an object")
        arm_id = _id(entry.get("arm_id"), "arm_id")
        kind = entry.get("representation_kind")
        if kind not in ARM_REPRESENTATION_KINDS:
            _fail("unknown arm representation kind")
        if arm_id in arms:
            _fail("duplicate arm id")
        arms[arm_id] = kind
    return arms


def _validate_semantic_closure(candidate: Mapping[str, Any], envs: Mapping[str, Mapping[str, Any]]) -> None:
    """Validate the closed candidate graph beyond JSON Schema structure."""
    if len(envs) != len(ARTIFACT_FILENAMES) or set(envs) != set(ARTIFACT_FILENAMES):
        _fail("candidate must provide one envelope for each of 13 artifact owners")
    ids: dict[str, tuple[str, str]] = {}
    for name, env in envs.items():
        aid = _id(env.get("artifact_id"), f"{name} artifact_id")
        if aid in ids:
            _fail("duplicate artifact envelope id")
        ids[aid] = (name, _digest(env.get("payload_digest"), f"{name} payload_digest"))

    # Every serialized dependency reference must resolve exactly by id, type and digest.
    for env in envs.values():
        for ref in env.get("input_artifact_refs", ()):
            if not isinstance(ref, Mapping):
                _fail("typed artifact reference required")
            target = ids.get(ref.get("artifact_id"))
            if target is None or target[0] != _artifact_filename(str(ref.get("artifact_type"))) or target[1] != ref.get("payload_digest"):
                _fail("unresolved or wrong-digest artifact reference")

    ledger = _record_payload(candidate["runtime_and_failure_ledger.json"])
    events = ledger.get("events", [])
    if isinstance(events, Mapping):
        events = [events]
    tombstoned: set[str] = set()
    for event in events:
        if not isinstance(event, Mapping):
            _fail("runtime ledger event must be an object")
        et = event.get("event_type")
        affected = event.get("affected_refs", [])
        if et in {"INVALIDATION", "ROLLBACK"}:
            if not isinstance(affected, list) or len(set(affected)) != len(affected) or affected != sorted(affected):
                _fail("affected_refs must be unique and bytewise sorted")
            if any(ref not in ids for ref in affected):
                _fail("unknown affected artifact")
            if event.get("membership_digest") != membership_digest(affected):
                _fail("invalid membership digest")
        if et == "TOMBSTONE":
            tombstoned.update(affected)
            aid = event.get("artifact_id")
            if aid:
                tombstoned.add(aid)
    for aid in tombstoned:
        name, _ = ids.get(aid, (None, None))
        env = envs.get(name) if name else None
        if env and env.get("availability_status") == "AVAILABLE":
            _fail("tombstoned artifact remains AVAILABLE")

    sampling = _rows(candidate["window_sample_manifest.jsonl"])
    slots: set[str] = set(); ticks: set[tuple[Any, Any]] = set()
    sampling_windows: set[str] = set()
    for row in sampling:
        target = _id(row.get("target_id"), "target_id")
        key = (row.get("window_id"), row.get("tick"))
        if target in slots or key in ticks:
            _fail("duplicate target slot")
        slots.add(target); ticks.add(key)
        if row.get("window_id") is not None:
            sampling_windows.add(_id(row.get("window_id"), "sample_target window_id"))
    run = _record_payload(candidate["run_manifest.json"])
    source_revisions = set(_source_revision_ids(_record_payload(candidate["source_manifest.json"])))
    reps = run.get("representations", [])
    ranked = _rows(candidate["ranked_candidates.jsonl"])
    judgments = _rows(candidate["window_judgments.jsonl"])

    # The closed per-run arm registry is the arm/representation identity surface.
    arms = _validate_arm_registry(run)
    if ranked or judgments:
        if not arms:
            _fail("arm registry is required when ranked candidates or window judgments exist")
        # ADR/D03 freezes exactly one local semantic (embedding) arm and one
        # transparent metadata baseline.  The rank stage always scores both, so
        # a closed registry carries exactly that multiset of representation
        # kinds.  Kinds/counts are enforced, not hardcoded arm ids.
        if sorted(arms.values()) != sorted(ARM_REPRESENTATION_KINDS):
            _fail("arm registry must declare exactly the frozen two-arm set")

    # Provenance for ranked candidates lives on the artifact envelope, not in
    # duplicated row coordinates; a tombstoned dependency is still fatal.
    ranked_consumed = {
        ref.get("artifact_id")
        for ref in envs["ranked_candidates.jsonl"].get("input_artifact_refs", ())
        if isinstance(ref, Mapping)
    }
    if ranked_consumed & tombstoned:
        _fail("ranked candidate consumes tombstoned artifact")

    sampling_digest = _digest(envs["window_sample_manifest.jsonl"].get("payload_digest"), "sampling payload_digest")
    rep_by_id: dict[str, Mapping[str, Any]] = {}
    for rep in reps:
        if not isinstance(rep, Mapping):
            _fail("representation record must be an object")
        representation_id = _id(rep.get("representation_id"), "representation_id")
        if representation_id in rep_by_id:
            _fail("duplicate representation id")
        rep_by_id[representation_id] = rep
        # A representation joins a source revision, a technical window and the
        # sampling manifest.  The revision identity is owned by source_manifest.
        if _id(rep.get("revision_id"), "representation revision_id") not in source_revisions:
            _fail("representation revision_id does not resolve to source_manifest")
        if rep.get("pooling") != "MEAN_TARGET_SLOTS" or rep.get("accumulation_order") != "target_tick_ascending_serial":
            _fail("representation target-slot declaration mismatch")
        if rep.get("sampling_manifest_digest") != sampling_digest:
            _fail("representation sampling manifest digest mismatch")

    candidate_ids: set[str] = set()
    for row in ranked:
        candidate_id = _id(row.get("candidate_id"), "candidate_id")
        if candidate_id in candidate_ids:
            _fail("duplicate ranked candidate id")
        candidate_ids.add(candidate_id)
    ranked_arms: set[str] = set()
    for row in ranked:
        arm_id = _id(row.get("arm_id"), "arm_id")
        kind = arms.get(arm_id)
        if kind is None:
            _fail("unknown arm id")
        ranked_arms.add(arm_id)
        # F2/D8-3: window_id is the sole technical-coordinate join.  The
        # canonical owner is window_sample_manifest.jsonl, not run_manifest.windows
        # (an optional projection of SUCCEEDED rows only).  Any coverage_status
        # makes a window valid, so failed/omitted sampling still resolves here.
        window_id = _id(row.get("window_id"), "ranked candidate window_id")
        if window_id not in sampling_windows:
            _fail("ranked candidate window_id does not resolve to window_sample_manifest")
        if kind == "embedding":
            representation_id = _id(row.get("representation_id"), "ranked candidate representation_id")
            rep = rep_by_id.get(representation_id)
            if rep is None:
                _fail("unknown representation id")
            if rep.get("window_id") != row.get("window_id"):
                _fail("representation window mismatch")
            # Spec §5: failed/non-finite/zero vectors remain status rows.  Only
            # a primary FINITE ranking asserts that the space it ranks in is
            # well-formed, so only FINITE rows require a SUCCEEDED encoding.
            if (row.get("score_status") == "FINITE"
                    and rep.get("representation_status") != "SUCCEEDED"):
                _fail("ranked candidate representation is not SUCCEEDED")
        elif "representation_id" in row or row.get("representation_id") is not None:
            _fail("metadata-floor candidate must not declare representation_id")
    # F3/D8-1: the producer emits both configured D03 arms at prepare time and
    # the rank stage always scores both, so a non-empty ranked artifact must
    # carry at least one row per declared arm.  Pre-ranking runs (empty
    # ranked_candidates and window_judgments) are exempt.
    if ranked:
        missing_arms = sorted(set(arms) - ranked_arms)
        if missing_arms:
            _fail("ranked candidates must include every declared arm; missing: " + ", ".join(missing_arms))

    for judgment in judgments:
        arm_id = _id(judgment.get("arm_id"), "window_judgment arm_id")
        if arm_id not in arms:
            _fail("window judgment arm is not declared")
        window_id = _id(judgment.get("window_id"), "window_judgment window_id")
        if window_id not in sampling_windows:
            _fail("window judgment window_id does not resolve to window_sample_manifest")
    sandbox = run.get("sandbox")
    sandbox_fields = {"bwrap_path", "bwrap_version", "bwrap_digest", "interpreter_path",
                      "interpreter_version", "interpreter_digest", "read_only_mounts",
                      "writable_mounts", "clearenv", "net_unshared", "argv_digest",
                      "mount_policy_digest", "child_network_sentinel"}
    if not isinstance(sandbox, Mapping) or set(sandbox) != sandbox_fields:
        _fail("complete sandbox attestation is required")
    for field in ("bwrap_path", "bwrap_version", "bwrap_digest", "interpreter_path",
                  "interpreter_version", "interpreter_digest", "argv_digest", "mount_policy_digest"):
        if not isinstance(sandbox.get(field), str) or not sandbox[field]:
            _fail("complete sandbox attestation is required")
    if (not isinstance(sandbox.get("read_only_mounts"), list)
            or not isinstance(sandbox.get("writable_mounts"), list)
            or sandbox.get("clearenv") is not True
            or sandbox.get("net_unshared") is not True
            or sandbox.get("child_network_sentinel") is not True):
        _fail("complete sandbox attestation is required")
    attempts = {a.get("attempt_id") for a in run.get("attempts", []) if isinstance(a, Mapping)}
    sentinels = [e for e in events if e.get("event_type") == "EGRESS_BLOCKED"]
    protocols = {e.get("protocol") for e in sentinels}
    if protocols != {"DNS", "HTTP_PROXY", "PROVIDER", "LOOPBACK"}:
        _fail("incomplete child network sentinel protocol group")
    sentinel_attempt_ids = {e.get("attempt_id") for e in sentinels}
    if not sentinels or len(sentinel_attempt_ids) != 1 or next(iter(sentinel_attempt_ids)) not in attempts:
        _fail("sentinel attempt is not joined to preflight attempt")
    sentinel_attempt = next(a for a in run.get("attempts", []) if isinstance(a, Mapping) and a.get("attempt_id") in sentinel_attempt_ids)
    if sentinel_attempt.get("stage") != "preflight":
        _fail("sentinel attempt is not joined to preflight attempt")
    if len({e.get("policy_decision_id") for e in sentinels}) != 1:
        _fail("sentinel policy decision mismatch")
    for e in sentinels:
        if e.get("decision") not in {"DENY", "BLOCKED"} or e.get("outcome") not in {"DENY", "BLOCKED"} or not isinstance(e.get("attempted_bytes"), int) or e["attempted_bytes"] <= 0 or e.get("transmitted_bytes") != 0 or e.get("payload") is not None:
            _fail("invalid child network sentinel evidence")


def validate_artifact_set(candidate: Any, refs: Mapping[str, Any] | None = None) -> bool:
    """Validate the closed artifact set and its discovery FK/cardinality graph.

    ``refs`` is accepted only as a compatibility-shaped second argument when
    it is itself the complete candidate mapping.  An id-list context (the old
    vacuous API) is rejected explicitly.
    """
    # Preserve the artifact-closure gate as the first diagnostic.  This is
    # important for callers still passing the legacy `(filenames, refs)`
    # shape: a missing/14th/unknown artifact must not be masked by the later
    # typed-graph API error.
    if not isinstance(candidate, Mapping):
        names = tuple(candidate) if isinstance(candidate, Sequence) and not isinstance(candidate, (str, bytes, bytearray)) else ()
        if len(names) != len(ARTIFACT_FILENAMES) or set(names) != set(ARTIFACT_FILENAMES):
            _fail("artifact set must contain exactly 13 named files")
    if refs is not None:
        if not isinstance(refs, Mapping) or "artifacts" not in refs:
            _fail("foreign-key validation requires typed candidate artifacts")
        candidate = refs
    artifacts = _artifact_payloads(candidate)
    _validate_discovery(artifacts)
    envs = _envelopes(artifacts)
    _validate_semantic_closure(artifacts, envs)
    return True


def validate_operation_purpose(operation: str, purpose: str) -> bool:
    """Enforce the closed discovery/process purpose mapping."""
    if operation not in PURPOSE_BY_OPERATION or purpose != PURPOSE_BY_OPERATION[operation]:
        _fail("operation/purpose mismatch")
    return True
