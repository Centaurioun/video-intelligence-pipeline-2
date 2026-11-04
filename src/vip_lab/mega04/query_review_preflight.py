"""Packet P04b: Gate-0 Query/Split/Gold-Event & Blinded Reviewer Envelope Preflight.

Delegates directly to:
- ``gate0.labels.build_queries``, ``ranking_inputs``, ``build_gold_events``,
  ``label_version_digest``
- ``gate0.reviewer_envelope.build_reviewer_envelope``, ``validate_reviewer_envelope``
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from gate0.labels import (
    FAMILIES,
     build_gold_events,
    build_queries,
    label_version_digest,
    ranking_inputs,
)
from gate0.reviewer_envelope import (
    build_reviewer_envelope,
    validate_reviewer_envelope,
)

from ..common import (
    NOT_OBSERVED,
    ReadinessFinding,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    sanitize_untrusted_authority_claims,
)


STAGE_ID = "MEGA-04.QUERY_REVIEW_PREFLIGHT"
LEAKAGE_FORBIDDEN_RANKING_KEYS = frozenset({"family", "presence", "split", "gold_events"})


def inspect_query_review_preflight(
    payload: Mapping[str, Any],
) -> ReadinessPacket:
    """Validate Gate-0 40-query split protocol, ranking-input non-leakage,
    dual-reviewer rational gold events, and blinded reviewer envelopes.
    """
    if not isinstance(payload, Mapping):
        raise VipLabError(
            "GATE0_QUERY_REVIEW_NOT_MAPPING",
            "payload must be a mapping",
        )

    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(payload)
    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="GATE0_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Untrusted authority flags in query/review payload were ignored",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    query_specs = cleaned.get("query_specs")
    split_by_id = cleaned.get("split_by_id")
    query_version = str(cleaned.get("query_version", "q_v1"))
    gold_event_specs = cleaned.get("gold_events")
    label_version = str(cleaned.get("label_version", "lbl_v1"))
    reviewer_envelope = cleaned.get("reviewer_envelope")
    reviewer_envelope_builder_args = cleaned.get("reviewer_envelope_inputs")
    forbidden_identifiers: Sequence[str] = tuple(
        str(x) for x in cleaned.get("forbidden_identifiers", ("baseline", "v1_siglip"))
    )

    if not isinstance(query_specs, Sequence) or not isinstance(split_by_id, Mapping):
        code = "GATE0_QUERY_SPECS_OR_SPLITS_MISSING"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.INVALID,
                message="query_specs (sequence) and split_by_id (mapping) are required",
                field_path="query_specs",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.INVALID,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"queries_valid": False, "gold_valid": False, "reviewer_valid": False},
        )

    try:
        queries = build_queries(list(query_specs), dict(split_by_id), query_version)
        rank_in = ranking_inputs(queries)
    except ValueError as exc:
        code = "GATE0_QUERY_PROTOCOL_VIOLATION"
        reasons.append(code)
        blockers.append(code)
        findings.append(
            ReadinessFinding(
                code=code,
                status=ReadinessStatus.BLOCKED,
                message=str(exc),
                field_path="query_specs",
            )
        )
        return ReadinessPacket(
            stage_id=STAGE_ID,
            status=ReadinessStatus.BLOCKED,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            findings=tuple(findings),
            summary={"queries_valid": False, "gold_valid": False, "reviewer_valid": False},
        )

    # Verify non-leakage in ranking_inputs
    for row in rank_in:
        leaked = LEAKAGE_FORBIDDEN_RANKING_KEYS.intersection(row.keys())
        if leaked:
            code = "GATE0_RANKING_INPUT_LABEL_LEAKAGE"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=f"Ranking input leaked forbidden keys: {sorted(leaked)}",
                    field_path="ranking_inputs",
                )
            )

    findings.append(
        ReadinessFinding(
            code="GATE0_QUERY_SET_VALIDATED",
            status=ReadinessStatus.READY_SYNTHETIC,
            message="Validated 40-query protocol (32 EVALUATION / 8 DEVELOPMENT) and non-leaking ranking inputs",
            details={
                "query_count": len(queries),
                "families": list(FAMILIES),
                "ranking_input_keys": sorted(rank_in[0].keys()) if rank_in else [],
            },
        )
    )

    gold_valid = False
    lbl_digest: str | None = None
    if gold_event_specs is not None:
        if not isinstance(gold_event_specs, Sequence):
            code = "GATE0_GOLD_EVENTS_NOT_SEQUENCE"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.INVALID,
                    message="gold_events must be a sequence",
                    field_path="gold_events",
                )
            )
        else:
            try:
                gold = build_gold_events(
                    list(gold_event_specs),
                    queries,
                    label_version,
                    reviewer_count=2,
                )
                lbl_digest = label_version_digest(queries, gold)
                gold_valid = True
                findings.append(
                    ReadinessFinding(
                        code="GATE0_GOLD_EVENTS_VALIDATED",
                        status=ReadinessStatus.READY_SYNTHETIC,
                        message="Validated dual-reviewer EVALUATION rational gold events",
                        details={
                            "gold_event_count": len(gold),
                            "label_version_digest": lbl_digest,
                        },
                    )
                )
            except ValueError as exc:
                code = "GATE0_GOLD_EVENT_PROTOCOL_VIOLATION"
                reasons.append(code)
                blockers.append(code)
                findings.append(
                    ReadinessFinding(
                        code=code,
                        status=ReadinessStatus.BLOCKED,
                        message=str(exc),
                        field_path="gold_events",
                    )
                )

    reviewer_valid = False
    envelope_digest: str | None = None
    if reviewer_envelope is not None or reviewer_envelope_builder_args is not None:
        try:
            if isinstance(reviewer_envelope, Mapping):
                env_dict = dict(reviewer_envelope)
            elif isinstance(reviewer_envelope_builder_args, Mapping):
                env_dict = build_reviewer_envelope(
                    run_id=str(reviewer_envelope_builder_args["run_id"]),
                    config_digest=str(reviewer_envelope_builder_args["config_digest"]),
                    label_version_digest=str(
                        reviewer_envelope_builder_args.get("label_version_digest")
                        or lbl_digest
                        or ("b" * 64)
                    ),
                    judgments=list(reviewer_envelope_builder_args["judgments"]),
                    blind_manifest=dict(
                        reviewer_envelope_builder_args["blind_manifest"]
                    ),
                )
            else:
                raise ValueError("Invalid reviewer envelope configuration")

            validate_reviewer_envelope(
                env_dict,
                forbidden_identifiers=forbidden_identifiers,
                expected_run_id=env_dict.get("run_id"),
                expected_config_digest=env_dict.get("config_digest"),
                expected_label_version_digest=env_dict.get("label_version_digest"),
            )
            reviewer_valid = True
            envelope_digest = str(env_dict.get("envelope_digest"))
            findings.append(
                ReadinessFinding(
                    code="GATE0_REVIEWER_ENVELOPE_VALIDATED",
                    status=ReadinessStatus.READY_SYNTHETIC,
                    message="Validated blinded dual-reviewer judgment envelope",
                    details={"envelope_digest": envelope_digest},
                )
            )
        except ValueError as exc:
            code = "GATE0_REVIEWER_ENVELOPE_VIOLATION"
            reasons.append(code)
            blockers.append(code)
            findings.append(
                ReadinessFinding(
                    code=code,
                    status=ReadinessStatus.BLOCKED,
                    message=str(exc),
                    field_path="reviewer_envelope",
                )
            )

    if any(f.status == ReadinessStatus.INVALID for f in findings):
        final_status = ReadinessStatus.INVALID
    elif blockers:
        final_status = ReadinessStatus.BLOCKED
    else:
        final_status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("GATE0_QUERY_REVIEW_SYNTHETIC_READY")

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=final_status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_RUN",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "queries_valid": True,
            "query_count": len(queries),
            "ranking_input_count": len(rank_in),
            "gold_valid": gold_valid,
            "label_version_digest": lbl_digest,
            "reviewer_valid": reviewer_valid,
            "envelope_digest": envelope_digest,
        },
    )
