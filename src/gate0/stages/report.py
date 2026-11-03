"""Sole Gate-0 gate-decision publisher."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence
from gate0.identity import digest_bytes
from gate0.canonical_json import canonical_bytes
from gate0.evaluation import EvaluationResult

@dataclass(frozen=True)
class ReportResult:
    gate_decision: str
    benchmark_status: str
    stop_reason: str
    run_id: str
    authority: str
    reviewers: tuple[str, ...]
    metrics_digest: str

REQUIRED_METRICS = {"hit_at_10.metadata", "hit_at_10.semantic", "paired_lift.semantic_minus_metadata"}
REQUIRED_FAMILY_METRICS = {f"family_hit_at_10.semantic.{family.lower()}" for family in ("APPEARANCE", "VISIBLE_ACTION", "INTERACTION", "SCENE_COMPOSITION_CAMERA_MOVEMENT")}

def decide_gate(result: EvaluationResult, *, validity: str, policy_status: str, repeat_status: str, thresholds: Mapping[str, int] | None = None) -> str:
    if not REQUIRED_METRICS.issubset(result.metrics) or not REQUIRED_FAMILY_METRICS.issubset(result.metrics): return "INVALID_PROTOCOL"
    if validity == "INVALID_PROTOCOL": return "INVALID_PROTOCOL"
    if validity == "NOT_RUN" or policy_status in {"BLOCKED", "BLOCKED_PREREQUISITE"}: return "NOT_RUN"
    if repeat_status == "NOT_RUN": return "NOT_RUN"
    if repeat_status not in {"EQUAL", "VALID"}: return "INVALID_PROTOCOL"
    t = thresholds or {"semantic_num": 20, "paired_num": 5, "family_num": 3}
    semantic = result.metrics["hit_at_10.semantic"].numerator >= t["semantic_num"]
    paired = result.metrics["paired_lift.semantic_minus_metadata"].numerator >= t["paired_num"]
    families = all(result.metrics[key].numerator >= t["family_num"] for key in REQUIRED_FAMILY_METRICS)
    return "PASS" if semantic and paired and families else "FAIL"

def report(result: EvaluationResult, *, run_id: str, authority: str, reviewers: Sequence[str], validity: str, policy_status: str, repeat_status: str, gate_owner_id: str | None = None, run_manifest: Mapping[str, Any] | None = None, policy_decision_id: str | None = None, expected_policy_decision_id: str | None = None, required_metric_ids: Sequence[str] = tuple(REQUIRED_METRICS)) -> ReportResult:
    if gate_owner_id is not None and gate_owner_id != authority: raise ValueError("gate owner mismatch")
    if run_manifest is not None and (run_manifest.get("run_id") != run_id or run_manifest.get("gate_owner_id") != authority): raise ValueError("run manifest binding mismatch")
    if policy_status != "ALLOW":
        # A blocked prerequisite is projected by precedence; any other policy
        # state is an invalid protocol rather than a quality miss.
        if policy_status not in {"BLOCKED", "BLOCKED_PREREQUISITE"}: raise ValueError("policy binding mismatch")
    if expected_policy_decision_id is not None and policy_decision_id != expected_policy_decision_id: raise ValueError("policy decision binding mismatch")
    if not set(required_metric_ids).issubset(result.metrics): raise ValueError("required metric missing")
    decision = decide_gate(result, validity=validity, policy_status=policy_status, repeat_status=repeat_status)
    benchmark = "VALID" if decision in {"PASS", "FAIL"} else ("INVALID_PROTOCOL" if decision == "INVALID_PROTOCOL" else "NOT_RUN")
    metrics_digest = digest_bytes(canonical_bytes({key: value.to_dict() for key, value in sorted(result.metrics.items())}))
    if run_manifest is not None and run_manifest.get("metrics_digest") not in (None, metrics_digest):
        raise ValueError("metrics digest binding mismatch")
    return ReportResult(decision, benchmark, "NONE" if decision in {"PASS", "FAIL"} else decision, run_id, authority, tuple(reviewers), metrics_digest)

def render_gate_decision(result: EvaluationResult, *, run_id: str, authority: str,
                         reviewers: Sequence[str], validity: str, policy_status: str,
                         repeat_status: str, threshold_digest: str,
                         gate_owner_id: str | None = None,
                         decided_at: str | None = None) -> tuple[ReportResult, bytes, str]:
    """Return the closed markdown payload, its digest, and report projection."""
    projection = report(result, run_id=run_id, authority=authority, reviewers=reviewers,
                        validity=validity, policy_status=policy_status,
                        repeat_status=repeat_status, gate_owner_id=gate_owner_id)
    when = decided_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines = [f"run_id: {run_id}", f"benchmark_status: {projection.benchmark_status}",
             f"gate_decision: {projection.gate_decision}", f"stop_reason: {projection.stop_reason}",
             f"metrics_digest: {projection.metrics_digest}", f"threshold_digest: {threshold_digest}",
             f"authority: {authority}", f"reviewers: {','.join(reviewers)}", f"decided_at: {when}"]
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    return projection, payload, digest_bytes(payload)
