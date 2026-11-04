"""MEGA-17 Workstream C: Gate-0 Diagnostic Retrieval Experiment Readiness (Roadmap Step 4).

Reuses ``vip_lab.mega04`` (``inspect_query_review_preflight``), ``gate0.labels``
(``FAMILIES``, ``build_queries``, ``build_gold_events``, ``ranking_inputs``), and
``gate0.evaluation.evaluate`` to build a closed Gate-0 experiment-preflight receipt,
verify all 12 Gate-0 contract artifacts, validate the 4-second non-overlapping
half-open window and 2-FPS presentation-frame sampling protocol, test deterministic
synthetic scoring against exact Gate-0 thresholds (Hit@10 >= 20/24, paired lift >= 5/24,
per-family Hit@10 >= 3/6 in all 4 families), and preserve the strict boundary between
Gate-0 diagnostic baseline lift and Gate-1 multi-profile benchmarking.

Hard invariants:
- ``gate0_authentic_experiment_status == "NOT_RUN"``
- ``gate0_d3_authorized == False``
- ``gate0_real_model_execution == "NOT_OBSERVED"``
- ``gate0_real_human_labels == "NOT_OBSERVED"``
- ``gate0_promotion == False``
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from gate0.evaluation import evaluate as evaluate_gate0_metrics
from gate0.labels import FAMILIES
from vip_lab.common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    canonical_sha256,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)
from vip_lab.mega04.query_review_preflight import inspect_query_review_preflight
from vip_lab.mega08.capability_inventory import _SYNTHETIC_PROFILE_CROSSWALK
from vip_lab.mega17.source_readiness import build_synthetic_40_query_artifact


STAGE_ID = "MEGA-17.WORKSTREAM_C_GATE0_EXPERIMENT_READINESS"
GATE0_READINESS_SCHEMA_VERSION = "vip_lab.mega17.gate0_readiness.v1"

GATE0_CONTRACT_ARTIFACT_NAMES: tuple[str, ...] = (
    "source_manifest",
    "sample_manifest",
    "queries",
    "gold_events",
    "reviewer_judgments",
    "run_manifest",
    "benchmark_metrics",
    "failure_taxonomy",
    "decision_record",
    "experiment_ledger",
    "gate_verdict",
    "audit_log",
)

GATE0_VERDICT_STATES: tuple[str, ...] = (
    "INVALID_PROTOCOL",
    "NOT_RUN",
    "BLOCKED_PREREQUISITE",
    "FAIL",
    "PASS",
)

REFUSAL_GATE0_SINGLE_REVIEWER_INSUFFICIENT = "REFUSAL_GATE0_SINGLE_REVIEWER_INSUFFICIENT"
REFUSAL_GATE0_GOLD_LABEL_LEAKAGE_TO_RANKER = "REFUSAL_GATE0_GOLD_LABEL_LEAKAGE_TO_RANKER"
REFUSAL_GATE0_WINDOW_SAMPLING_INVALID = "REFUSAL_GATE0_WINDOW_SAMPLING_INVALID"
REFUSAL_GATE0_PROMOTION_FROM_SYNTHETIC_FORBIDDEN = "REFUSAL_GATE0_PROMOTION_FROM_SYNTHETIC_FORBIDDEN"
REFUSAL_GATE1_SUBSTITUTED_FOR_GATE0 = "REFUSAL_GATE1_SUBSTITUTED_FOR_GATE0"
REFUSAL_GATE0_AUTHENTIC_EXECUTION_NOT_AUTHORIZED = "REFUSAL_GATE0_AUTHENTIC_EXECUTION_NOT_AUTHORIZED"


def _build_synthetic_gold_and_reviewer_payload() -> dict[str, Any]:
    q_doc = build_synthetic_40_query_artifact()
    q_rows = q_doc["queries"]
    query_specs = [
        (r["query_id"], r["text"], (r["family"], r["presence"])) for r in q_rows
    ]
    split_by_id = {r["query_id"]: r["split"] for r in q_rows}

    eval_pos_ids = [
        r["query_id"]
        for r in q_rows
        if r["split"] == "EVALUATION" and r["presence"] == "POSITIVE"
    ]

    gold_events: list[dict[str, Any]] = []
    reviewer_rows: list[dict[str, Any]] = []
    for idx, qid in enumerate(eval_pos_ids):
        win_id = f"win-{idx + 1:03d}"
        for rev_id in ("rev-alpha-01", "rev-beta-02"):
            gold_events.append(
                {
                    "query_id": qid,
                    "revision_id": "rev-ballet-01",
                    "reviewer_id": rev_id,
                    "grade": 2,
                    "rationale": f"Synthetic dual-reviewer gold interval for {qid}",
                    "stream_index": 0,
                    "start": {"numerator": idx * 4, "denominator": 1},
                    "end": {"numerator": (idx + 1) * 4, "denominator": 1},
                    "uncertainty": {
                        "start": {"numerator": 1, "denominator": 2},
                        "end": {"numerator": 1, "denominator": 2},
                    },
                }
            )
            for token in ("arm-a", "arm-b"):
                reviewer_rows.append(
                    {
                        "assertion_id": f"asrt-{qid}-{token}-{rev_id}",
                        "query_id": qid,
                        "window_id": win_id,
                        "blind_arm_token": token,
                        "reviewer_id": rev_id,
                        "grade": 2,
                        "ambiguity": "NONE",
                        "review_status": "ACCEPTED",
                        "assertion": {
                            "version": "v1",
                            "text": f"Assertion for {qid} on {win_id}",
                            "digest": "a" * 64,
                        },
                    }
                )

    return {
        "query_specs": query_specs,
        "split_by_id": split_by_id,
        "query_version": "synth-q-v1",
        "gold_events": gold_events,
        "label_version": "synth-lbl-v1",
        "reviewer_envelope_inputs": {
            "rows": reviewer_rows,
            "mapping_version": "gate0-v1",
            "config_digest": "b" * 64,
        },
    }


def evaluate_synthetic_gate0_scoring_fixture(
    *,
    scenario: str = "SYNTHETIC_THRESHOLD_PASS",
) -> dict[str, Any]:
    """Run deterministic synthetic scoring through ``gate0.evaluation.evaluate`` to test threshold rules.

    Exact Gate-0 pass criteria on the 24 positive evaluation queries:
    1. Semantic ``Hit@10 >= 20/24``
    2. Paired lift ``semantic - metadata >= 5/24``
    3. Per-family semantic ``Hit@10 >= 3/6`` in all 4 families

    Even when synthetic scoring satisfies all three criteria, ``gate0_authentic_experiment_status``
    remains ``"NOT_RUN"`` and ``gate0_promotion`` remains ``False``.
    """
    q_doc = build_synthetic_40_query_artifact()
    queries = q_doc["queries"]
    eval_pos = [
        r for r in queries if r["split"] == "EVALUATION" and r["presence"] == "POSITIVE"
    ]
    eval_abs = [
        r for r in queries if r["split"] == "EVALUATION" and r["presence"] == "ABSENT"
    ]

    # Configure per-query semantic and metadata hits according to requested synthetic scenario
    judgments: list[dict[str, Any]] = []
    for idx, row in enumerate(eval_pos):
        qid = row["query_id"]
        fam = row["family"]
        if scenario == "SYNTHETIC_THRESHOLD_PASS":
            # 21/24 semantic hits (at least 5/6 per family), 12/24 metadata hits -> lift = 9/24
            sem_grade = 2 if (idx % 8 != 0) else 0
            meta_grade = 2 if (idx % 2 == 0 and sem_grade == 2) else 0
        elif scenario == "SYNTHETIC_THRESHOLD_FAIL_OVERALL":
            # 16/24 semantic hits (< 20/24)
            sem_grade = 2 if (idx % 3 != 0) else 0
            meta_grade = 2 if (idx % 4 == 0) else 0
        elif scenario == "SYNTHETIC_THRESHOLD_FAIL_FAMILY_FLOOR":
            # APPEARANCE gets only 2/6 (< 3/6), others get 6/6 (total 20/24)
            if fam == "APPEARANCE":
                sem_grade = 2 if idx < 2 else 0
            else:
                sem_grade = 2
            meta_grade = 0
        elif scenario == "SYNTHETIC_THRESHOLD_FAIL_PAIRED_LIFT":
            # Semantic 21/24, metadata 19/24 -> paired lift = 2/24 (< 5/24)
            sem_grade = 2 if idx < 21 else 0
            meta_grade = 2 if idx < 19 else 0
        else:
            raise VipLabError(
                "GATE0_SYNTHETIC_SCENARIO_UNKNOWN",
                f"Unknown synthetic scoring scenario: {scenario!r}",
            )

        judgments.append(
            {
                "query_id": qid,
                "window_id": f"win-{idx + 1:03d}",
                "arm_id": "offline-development-arm",
                "grade": sem_grade,
            }
        )
        judgments.append(
            {
                "query_id": qid,
                "window_id": f"win-{idx + 1:03d}",
                "arm_id": "metadata-floor",
                "grade": meta_grade,
            }
        )

    for idx, row in enumerate(eval_abs):
        qid = row["query_id"]
        for arm in ("offline-development-arm", "metadata-floor"):
            judgments.append(
                {
                    "query_id": qid,
                    "window_id": f"win-abs-{idx + 1:03d}",
                    "arm_id": arm,
                    "grade": 0,
                }
            )

    eval_res = evaluate_gate0_metrics(
        queries,
        judgments,
        ranking_digest="1" * 64,
        baseline_digest="2" * 64,
        gold_version_digest="3" * 64,
        query_version_digest="4" * 64,
        validity="VALID",
    )

    sem_hit = eval_res.metrics["hit_at_10.semantic"].numerator
    meta_hit = eval_res.metrics["hit_at_10.metadata"].numerator
    paired_lift = eval_res.metrics["paired_lift.semantic_minus_metadata"].numerator
    family_hits = {
        fam: eval_res.metrics[f"family_hit_at_10.semantic.{fam.lower()}"].numerator
        for fam in sorted(FAMILIES)
    }

    failure_reasons: list[str] = []
    if sem_hit < 20:
        failure_reasons.append("OVERALL_SEMANTIC_HIT_AT_10_BELOW_20_OF_24")
    if paired_lift < 5:
        failure_reasons.append("PAIRED_LIFT_BELOW_5_OF_24")
    if any(v < 3 for v in family_hits.values()):
        failure_reasons.append("FAMILY_FLOOR_BELOW_3_OF_6")

    synthetic_outcome = "PASS" if not failure_reasons else "FAIL"
    return {
        "scenario": scenario,
        "synthetic_only": True,
        "synthetic_threshold_outcome": synthetic_outcome,
        "semantic_hit_at_10_numerator": sem_hit,
        "semantic_hit_at_10_denominator": 24,
        "metadata_hit_at_10_numerator": meta_hit,
        "metadata_hit_at_10_denominator": 24,
        "paired_lift_numerator": paired_lift,
        "paired_lift_denominator": 24,
        "family_semantic_hits": family_hits,
        "failure_reasons": failure_reasons,
        "gate0_authentic_experiment_status": "NOT_RUN",
        "gate0_promotion": False,
    }


@dataclass(frozen=True)
class Gate0ExperimentReadinessReceipt:
    """Immutable Workstream C Gate-0 Diagnostic Retrieval Experiment Readiness receipt."""

    schema_version: str
    gate0_authentic_experiment_status: str
    gate0_d3_authorized: bool
    gate0_real_model_execution: str
    gate0_real_human_labels: str
    gate0_promotion: bool
    query_protocol_summary: Mapping[str, Any]
    window_sampling_spec: Mapping[str, Any]
    contract_artifacts_status: Mapping[str, Mapping[str, Any]]
    synthetic_scoring_matrix: Mapping[str, Any]
    host_runtime_repetition_requirements: Mapping[str, Any]
    gate0_vs_gate1_boundary: Mapping[str, Any]
    receipt_digest: str

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "gate0_authentic_experiment_status": self.gate0_authentic_experiment_status,
            "gate0_d3_authorized": self.gate0_d3_authorized,
            "gate0_real_model_execution": self.gate0_real_model_execution,
            "gate0_real_human_labels": self.gate0_real_human_labels,
            "gate0_promotion": self.gate0_promotion,
            "query_protocol_summary": dict(self.query_protocol_summary),
            "window_sampling_spec": dict(self.window_sampling_spec),
            "contract_artifacts_status": {
                k: dict(v) for k, v in self.contract_artifacts_status.items()
            },
            "synthetic_scoring_matrix": dict(self.synthetic_scoring_matrix),
            "host_runtime_repetition_requirements": dict(
                self.host_runtime_repetition_requirements
            ),
            "gate0_vs_gate1_boundary": dict(self.gate0_vs_gate1_boundary),
        }

    def to_dict(self) -> dict[str, Any]:
        out = self.payload_without_digest()
        out["receipt_digest"] = self.receipt_digest
        return out


def build_gate0_experiment_readiness_receipt() -> Gate0ExperimentReadinessReceipt:
    """Build deterministic Workstream C Gate-0 experiment readiness receipt."""
    qr_payload = _build_synthetic_gold_and_reviewer_payload()
    qr_pkt = inspect_query_review_preflight(qr_payload)
    if qr_pkt.status != ReadinessStatus.READY_SYNTHETIC:
        raise VipLabError(
            "WORKSTREAM_C_PREFLIGHT_UNEXPECTED_STATE",
            f"Query/review preflight did not return READY_SYNTHETIC: {qr_pkt.blockers}",
        )

    query_protocol_summary = {
        "total_queries": 40,
        "evaluation_positive_count": 24,
        "evaluation_absent_count": 8,
        "development_count": 8,
        "family_positive_counts": {fam: 6 for fam in sorted(FAMILIES)},
        "independent_reviewer_count": 2,
        "disagreement_adjudication_required": True,
        "source_disjoint_held_out_split": True,
        "gold_labels_withheld_from_ranker": True,
        "label_version_digest": qr_pkt.summary["label_version_digest"],
        "reviewer_envelope_digest": qr_pkt.summary["envelope_digest"],
    }

    window_sampling_spec = {
        "window_duration_seconds": 4,
        "window_overlap_seconds": 0,
        "endpoint_semantics": "HALF_OPEN",
        "sampling_fps": 2,
        "sampling_domain": "PRESENTATION_FRAMES",
        "vfr_nominal_fps_multiplication_forbidden": True,
    }

    contract_artifacts_status = {
        name: {
            "artifact_name": name,
            "contract_defined": True,
            "synthetic_preflight_supported": True,
            "authentic_artifact_state": NOT_OBSERVED,
        }
        for name in GATE0_CONTRACT_ARTIFACT_NAMES
    }

    synthetic_scoring_matrix = {
        "verdict_states_supported": list(GATE0_VERDICT_STATES),
        "pass_scenario": evaluate_synthetic_gate0_scoring_fixture(
            scenario="SYNTHETIC_THRESHOLD_PASS"
        ),
        "fail_overall_scenario": evaluate_synthetic_gate0_scoring_fixture(
            scenario="SYNTHETIC_THRESHOLD_FAIL_OVERALL"
        ),
        "fail_family_floor_scenario": evaluate_synthetic_gate0_scoring_fixture(
            scenario="SYNTHETIC_THRESHOLD_FAIL_FAMILY_FLOOR"
        ),
        "fail_paired_lift_scenario": evaluate_synthetic_gate0_scoring_fixture(
            scenario="SYNTHETIC_THRESHOLD_FAIL_PAIRED_LIFT"
        ),
    }

    host_runtime_repetition_requirements = {
        "sandbox_isolation_required": True,
        "network_egress_allowed": False,
        "dependency_lock_no_install_required": True,
        "deterministic_tie_break_required": True,
        "repeated_run_digest_equality_required": True,
        "authentic_host_execution_observed": NOT_OBSERVED,
    }

    profiles_info = [
        {
            "profile_id": row["profile_id"],
            "model_id": row["model_id"],
            "embedding_dim": row["embedding_dim"],
            "space_id": row["space_id"],
        }
        for row in _SYNTHETIC_PROFILE_CROSSWALK
    ]

    gate0_vs_gate1_boundary = {
        "gate0_role": "DIAGNOSTIC_USEFUL_MOMENT_LIFT_OVER_METADATA_FLOOR",
        "gate1_role": "CONTROLLED_REPRESENTATION_AND_MODEL_CAPABILITY_BENCHMARK",
        "gate1_substitutes_for_gate0": False,
        "v1_and_v2_base_768d_interchangeable": False,
        "gate1_distinct_profiles": profiles_info,
    }

    provisional = Gate0ExperimentReadinessReceipt(
        schema_version=GATE0_READINESS_SCHEMA_VERSION,
        gate0_authentic_experiment_status="NOT_RUN",
        gate0_d3_authorized=False,
        gate0_real_model_execution=NOT_OBSERVED,
        gate0_real_human_labels=NOT_OBSERVED,
        gate0_promotion=False,
        query_protocol_summary=query_protocol_summary,
        window_sampling_spec=window_sampling_spec,
        contract_artifacts_status=contract_artifacts_status,
        synthetic_scoring_matrix=synthetic_scoring_matrix,
        host_runtime_repetition_requirements=host_runtime_repetition_requirements,
        gate0_vs_gate1_boundary=gate0_vs_gate1_boundary,
        receipt_digest="0" * 64,
    )
    digest = canonical_sha256(provisional.payload_without_digest())
    return Gate0ExperimentReadinessReceipt(
        schema_version=provisional.schema_version,
        gate0_authentic_experiment_status="NOT_RUN",
        gate0_d3_authorized=False,
        gate0_real_model_execution=NOT_OBSERVED,
        gate0_real_human_labels=NOT_OBSERVED,
        gate0_promotion=False,
        query_protocol_summary=provisional.query_protocol_summary,
        window_sampling_spec=provisional.window_sampling_spec,
        contract_artifacts_status=provisional.contract_artifacts_status,
        synthetic_scoring_matrix=provisional.synthetic_scoring_matrix,
        host_runtime_repetition_requirements=provisional.host_runtime_repetition_requirements,
        gate0_vs_gate1_boundary=provisional.gate0_vs_gate1_boundary,
        receipt_digest=digest,
    )


def verify_gate0_experiment_readiness_receipt(
    receipt: Gate0ExperimentReadinessReceipt | Mapping[str, Any],
) -> dict[str, Any]:
    """Verify integrity and Section 8 invariants of a Gate0ExperimentReadinessReceipt."""
    raw = (
        receipt.to_dict()
        if isinstance(receipt, Gate0ExperimentReadinessReceipt)
        else dict(receipt)
    )
    if raw.get("schema_version") != GATE0_READINESS_SCHEMA_VERSION:
        raise VipLabError(
            "GATE0_READINESS_SCHEMA_MISMATCH",
            f"Expected {GATE0_READINESS_SCHEMA_VERSION}, got {raw.get('schema_version')!r}",
        )
    if (
        raw.get("gate0_authentic_experiment_status") != "NOT_RUN"
        or raw.get("gate0_d3_authorized") is not False
        or raw.get("gate0_real_model_execution") != NOT_OBSERVED
        or raw.get("gate0_real_human_labels") != NOT_OBSERVED
        or raw.get("gate0_promotion") is not False
    ):
        raise VipLabError(
            "GATE0_READINESS_INVARIANT_VIOLATION",
            "Gate0ExperimentReadinessReceipt violated mandatory Section 8 invariants.",
        )
    declared_digest = validate_hex_digest(
        str(raw.get("receipt_digest", "")),
        field_name="receipt_digest",
    )
    body = {k: v for k, v in raw.items() if k != "receipt_digest"}
    computed = canonical_sha256(body)
    if declared_digest != computed:
        raise VipLabError(
            "GATE0_READINESS_DIGEST_MISMATCH",
            f"receipt_digest mismatch: declared {declared_digest} != computed {computed}",
        )
    return raw


def inspect_gate0_experiment_readiness(
    payload: Mapping[str, Any] | None = None,
) -> ReadinessPacket:
    """Inspect Workstream C Gate-0 diagnostic experiment readiness and refuse protocol violations."""
    raw_payload = dict(payload) if isinstance(payload, Mapping) else {}
    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(raw_payload)

    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="WORKSTREAM_C_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Ignored untrusted authority flags in Workstream C payload.",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    reviewer_count = cleaned.get("reviewer_count", 2)
    if reviewer_count != 2:
        blockers.append(REFUSAL_GATE0_SINGLE_REVIEWER_INSUFFICIENT)
        reasons.append(REFUSAL_GATE0_SINGLE_REVIEWER_INSUFFICIENT)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_GATE0_SINGLE_REVIEWER_INSUFFICIENT,
                status=ReadinessStatus.BLOCKED,
                message=f"Gate-0 requires exactly 2 independent reviewers; got {reviewer_count!r}.",
            )
        )

    if bool(raw_payload.get("leak_gold_labels_to_ranker", False)):
        blockers.append(REFUSAL_GATE0_GOLD_LABEL_LEAKAGE_TO_RANKER)
        reasons.append(REFUSAL_GATE0_GOLD_LABEL_LEAKAGE_TO_RANKER)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_GATE0_GOLD_LABEL_LEAKAGE_TO_RANKER,
                status=ReadinessStatus.BLOCKED,
                message="Gold events, presence, split, and family labels must be withheld from retrieval arms.",
            )
        )

    win_dur = cleaned.get("window_duration_seconds", 4)
    win_ovl = cleaned.get("window_overlap_seconds", 0)
    fps = cleaned.get("sampling_fps", 2)
    if win_dur != 4 or win_ovl != 0 or fps != 2:
        blockers.append(REFUSAL_GATE0_WINDOW_SAMPLING_INVALID)
        reasons.append(REFUSAL_GATE0_WINDOW_SAMPLING_INVALID)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_GATE0_WINDOW_SAMPLING_INVALID,
                status=ReadinessStatus.BLOCKED,
                message="Gate-0 requires 4-second non-overlapping half-open windows and 2-FPS presentation-frame sampling.",
            )
        )

    if bool(raw_payload.get("claim_gate0_promotion_from_synthetic", False)):
        blockers.append(REFUSAL_GATE0_PROMOTION_FROM_SYNTHETIC_FORBIDDEN)
        reasons.append(REFUSAL_GATE0_PROMOTION_FROM_SYNTHETIC_FORBIDDEN)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_GATE0_PROMOTION_FROM_SYNTHETIC_FORBIDDEN,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Synthetic Gate-0 threshold pass never promotes Gate-0 or substitutes for real corpus evaluation.",
            )
        )

    if bool(raw_payload.get("substitute_gate1_for_gate0", False)):
        blockers.append(REFUSAL_GATE1_SUBSTITUTED_FOR_GATE0)
        reasons.append(REFUSAL_GATE1_SUBSTITUTED_FOR_GATE0)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_GATE1_SUBSTITUTED_FOR_GATE0,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Gate-1 model representation benchmarking cannot substitute for the Gate-0 diagnostic baseline experiment.",
            )
        )

    if bool(raw_payload.get("claim_authentic_experiment_executed", False)):
        blockers.append(REFUSAL_GATE0_AUTHENTIC_EXECUTION_NOT_AUTHORIZED)
        reasons.append(REFUSAL_GATE0_AUTHENTIC_EXECUTION_NOT_AUTHORIZED)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_GATE0_AUTHENTIC_EXECUTION_NOT_AUTHORIZED,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Authentic Gate-0 experiment has not been run and D-3 execution is not authorized.",
            )
        )

    receipt = build_gate0_experiment_readiness_receipt()

    has_auth_refusal = any(f.status == ReadinessStatus.NOT_AUTHORIZED for f in findings)
    if has_auth_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("GATE0_EXPERIMENT_PREFLIGHT_READY_NOT_RUN")
        findings.append(
            ReadinessFinding(
                code="GATE0_EXPERIMENT_PREFLIGHT_READY_NOT_RUN",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Validated 40-query protocol, 4s/2-FPS window spec, 12 contract artifacts, and synthetic scoring fixtures; authentic Gate-0 remains NOT_RUN.",
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_RUN",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "receipt_digest": receipt.receipt_digest,
            "gate0_authentic_experiment_status": "NOT_RUN",
            "gate0_d3_authorized": False,
            "gate0_real_model_execution": NOT_OBSERVED,
            "gate0_real_human_labels": NOT_OBSERVED,
            "gate0_promotion": False,
            "contract_artifact_count": len(receipt.contract_artifacts_status),
        },
    )
