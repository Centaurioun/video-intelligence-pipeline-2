"""MEGA-17 Workstream B: Source Identity, Custody, Rights, and D-2 Readiness (Roadmap Step 3).

Reuses ``gate0.d2_intake`` (``D2_FIELDS``, ``D2_FIELD_IDS``, ``D2_BASELINE_STATES``)
and ``vip_lab.mega04.d2_readiness.inspect_d2_readiness`` to provide a closed synthetic
D-2 readiness fixture, an 8-layer source/custody identity matrix that preserves
duplicate-content occurrences without collapsing ``occurrence_id`` or ``revision_id``,
a 7-permission boundary matrix, source-disjoint DEVELOPMENT/EVALUATION partition
validation, and a structured Owner-input requirements packet.

Hard invariants:
- ``real_source_inventory_executed == False``
- ``real_source_bytes_observed == False``
- ``real_source_rights_verified == False``
- ``d3_authorized_local_execution == False``
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping, Sequence

from gate0.canonical_json import canonical_bytes
from gate0.d2_intake import (
    D2_BASELINE_STATES,
    D2_FIELDS,
    D2_FIELD_IDS,
    D2_PACKAGE_SCHEMA_VERSION,
    RULE_EVIDENCE,
    RULE_OBSERVATION,
    RULE_RULING,
)
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
from vip_lab.mega04.d2_readiness import inspect_d2_readiness


STAGE_ID = "MEGA-17.WORKSTREAM_B_SOURCE_AND_D2_READINESS"
SOURCE_READINESS_SCHEMA_VERSION = "vip_lab.mega17.source_readiness.v1"

PERMISSION_DISCOVER_SOURCES = "PERMISSION_DISCOVER_SOURCES"
PERMISSION_INSPECT_LOCAL_BYTES = "PERMISSION_INSPECT_LOCAL_BYTES"
PERMISSION_CREATE_DERIVED_ARTIFACTS = "PERMISSION_CREATE_DERIVED_ARTIFACTS"
PERMISSION_RUN_AUTHENTIC_MODELS = "PERMISSION_RUN_AUTHENTIC_MODELS"
PERMISSION_PROVIDER_OR_CLOUD_EGRESS = "PERMISSION_PROVIDER_OR_CLOUD_EGRESS"
PERMISSION_RETAIN_OUTPUTS = "PERMISSION_RETAIN_OUTPUTS"
PERMISSION_EXPORT_OUTPUTS = "PERMISSION_EXPORT_OUTPUTS"

SEVEN_PERMISSION_BOUNDARIES: tuple[str, ...] = (
    PERMISSION_DISCOVER_SOURCES,
    PERMISSION_INSPECT_LOCAL_BYTES,
    PERMISSION_CREATE_DERIVED_ARTIFACTS,
    PERMISSION_RUN_AUTHENTIC_MODELS,
    PERMISSION_PROVIDER_OR_CLOUD_EGRESS,
    PERMISSION_RETAIN_OUTPUTS,
    PERMISSION_EXPORT_OUTPUTS,
)

REFUSAL_FILENAME_EQUALITY_NOT_BYTE_IDENTITY = "REFUSAL_FILENAME_EQUALITY_NOT_BYTE_IDENTITY"
REFUSAL_DUPLICATE_OCCURRENCE_COLLAPSE_FORBIDDEN = "REFUSAL_DUPLICATE_OCCURRENCE_COLLAPSE_FORBIDDEN"
REFUSAL_FORGED_OWNER_ATTESTATION = "REFUSAL_FORGED_OWNER_ATTESTATION"
REFUSAL_D3_EXECUTION_NOT_AUTHORIZED = "REFUSAL_D3_EXECUTION_NOT_AUTHORIZED"
REFUSAL_DISCOVERY_DOES_NOT_GRANT_PROCESSING = "REFUSAL_DISCOVERY_DOES_NOT_GRANT_PROCESSING"
REFUSAL_DEV_EVAL_PARTITION_LEAKAGE = "REFUSAL_DEV_EVAL_PARTITION_LEAKAGE"


def _doc_digest(doc: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(dict(doc))).hexdigest()


def build_synthetic_40_query_artifact() -> dict[str, Any]:
    """Build a canonical 40-query synthetic editor-queries artifact (24 pos, 8 absent, 8 dev)."""
    families_ordered = sorted(FAMILIES)
    queries: list[dict[str, Any]] = []
    # 24 EVALUATION POSITIVE queries (6 per family)
    idx = 1
    for fam in families_ordered:
        for k in range(1, 7):
            queries.append(
                {
                    "query_id": f"q-eval-pos-{idx:02d}",
                    "text": f"synthetic {fam.lower().replace('_', ' ')} ensemble rehearsal moment {k}",
                    "family": fam,
                    "presence": "POSITIVE",
                    "split": "EVALUATION",
                }
            )
            idx += 1
    # 8 EVALUATION ABSENT queries (2 per family)
    for k in range(1, 9):
        fam = families_ordered[(k - 1) % len(families_ordered)]
        queries.append(
            {
                "query_id": f"q-eval-abs-{k:02d}",
                "text": f"synthetic absent stage pattern {fam.lower().replace('_', ' ')} {k}",
                "family": fam,
                "presence": "ABSENT",
                "split": "EVALUATION",
            }
        )
    # 8 DEVELOPMENT queries (disjoint IDs and texts)
    for k in range(1, 9):
        fam = families_ordered[(k - 1) % len(families_ordered)]
        queries.append(
            {
                "query_id": f"q-dev-{k:02d}",
                "text": f"synthetic development calibration query {fam.lower().replace('_', ' ')} {k}",
                "family": fam,
                "presence": "POSITIVE" if k <= 6 else "ABSENT",
                "split": "DEVELOPMENT",
            }
        )
    return {
        "schema_version": "gate0.editor-queries.v1",
        "query_version": "synth-q-v1",
        "queries": queries,
    }


def build_closed_synthetic_d2_fixture_payload() -> dict[str, Any]:
    """Build a deterministic in-memory D-2 package payload exercising all 7 EVIDENCE validators.

    Resulting D-2 state distribution:
    - 0 VERIFIED (no cryptographic Owner attestation exists in source-only mode)
    - 7 PENDING (all 7 EVIDENCE rows pass deterministic schema validation under SYNTHETIC_FIXTURE)
    - 21 BLOCKED (all 21 RULING rows remain declared ABSENT)
    - 2 NOT_OBSERVED (both OBSERVATION rows remain declared ABSENT)
    """
    families_sorted = sorted(FAMILIES)
    corpus_designation = {
        "sessions": [
            {"session_id": "sess-ballet-01", "duration_minutes": 30},
            {"session_id": "sess-dance-02", "duration_minutes": 30},
            {"session_id": "sess-theatre-03", "duration_minutes": 25},
        ],
        "revisions": [
            {
                "revision_id": "rev-ballet-01",
                "session_id": "sess-ballet-01",
                "duration_minutes": 15,
                "split": "EVALUATION",
                "families": [families_sorted[0], families_sorted[1]],
            },
            {
                "revision_id": "rev-ballet-02",
                "session_id": "sess-ballet-01",
                "duration_minutes": 15,
                "split": "EVALUATION",
                "families": [families_sorted[2], families_sorted[3]],
            },
            {
                "revision_id": "rev-dance-03",
                "session_id": "sess-dance-02",
                "duration_minutes": 15,
                "split": "EVALUATION",
                "families": [families_sorted[0], families_sorted[2]],
            },
            {
                "revision_id": "rev-dance-04",
                "session_id": "sess-dance-02",
                "duration_minutes": 15,
                "split": "EVALUATION",
                "families": [families_sorted[1], families_sorted[3]],
            },
            {
                "revision_id": "rev-theatre-05",
                "session_id": "sess-theatre-03",
                "duration_minutes": 13,
                "split": "EVALUATION",
                "families": families_sorted,
            },
            {
                "revision_id": "rev-dev-06",
                "session_id": "sess-theatre-03",
                "duration_minutes": 12,
                "split": "DEVELOPMENT",
                "families": families_sorted,
            },
        ],
        "family_coverage": families_sorted,
    }
    editor_queries = build_synthetic_40_query_artifact()
    reviewers_doc = {
        "reviewer_ids": ["rev-alpha-01", "rev-beta-02"],
        "appointment_authority": "synthetic-editorial-committee-v1",
    }
    blinding_doc = {
        "token_map": [
            {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
            {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"},
        ],
        "reviewer_visible_fields": ["blind_arm_token"],
        "reviewer_hidden_fields": ["arm_id", "model_identity", "score"],
    }
    owner_binding_doc = {
        "config_gate_owner_id": "owner-principal-synth-01",
        "manifest_gate_owner_id": "owner-principal-synth-01",
    }

    artifacts = {
        "corpus-designation.json": corpus_designation,
        "editor-queries.json": editor_queries,
        "reviewers.json": reviewers_doc,
        "blinding.json": blinding_doc,
        "owner-binding.json": owner_binding_doc,
    }
    artifact_digests = {name: _doc_digest(doc) for name, doc in artifacts.items()}

    evidence_field_map = {
        "G0-D2-01": "corpus-designation.json",
        "G0-D2-10": "editor-queries.json",
        "G0-D2-11": "editor-queries.json",
        "G0-D2-12": "editor-queries.json",
        "G0-D2-14": "reviewers.json",
        "G0-D2-17": "blinding.json",
        "G0-D2-26": "owner-binding.json",
    }

    fields: dict[str, Any] = {}
    for spec in D2_FIELDS:
        if spec.field_id in evidence_field_map:
            art_name = evidence_field_map[spec.field_id]
            fields[spec.field_id] = {
                "declared_status": "COMPLETE",
                "evidence": [
                    {
                        "artifact": art_name,
                        "digest": artifact_digests[art_name],
                    }
                ],
                "notes": f"Synthetic structural evidence for {spec.field_id}",
            }
        else:
            fields[spec.field_id] = {
                "declared_status": "ABSENT",
                "evidence": [],
                "notes": f"Unresolved {spec.state_rule.lower()} field in synthetic mode",
            }

    return {
        "schema_version": D2_PACKAGE_SCHEMA_VERSION,
        "package_id": "d2p-mega17-synth-01",
        "fixture": True,
        "attestation": {
            "attester_id": "synth-attester-01",
            "attester_kind": "SYNTHETIC_FIXTURE",
        },
        "fields": fields,
        "artifacts": artifacts,
    }


@dataclass(frozen=True)
class SourceIdentityCustodyEntry:
    """Eight-layer identity record preserving occurrence vs revision vs content vs locator."""

    source_occurrence_id: str
    source_revision_id: str
    source_content_id: str
    source_sha256: str
    source_locator: str
    selected_stream_index: int
    derived_artifact_id: str
    policy_decision_ref: str
    run_attempt_id: str
    partition_split: str
    relation_kind: str
    custody_state: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_occurrence_id": self.source_occurrence_id,
            "source_revision_id": self.source_revision_id,
            "source_content_id": self.source_content_id,
            "source_sha256": self.source_sha256,
            "source_locator": self.source_locator,
            "selected_stream_index": self.selected_stream_index,
            "derived_artifact_id": self.derived_artifact_id,
            "policy_decision_ref": self.policy_decision_ref,
            "run_attempt_id": self.run_attempt_id,
            "partition_split": self.partition_split,
            "relation_kind": self.relation_kind,
            "custody_state": self.custody_state,
        }


@dataclass(frozen=True)
class SourceReadinessPacket:
    """Immutable Workstream B Source Identity, Custody, Rights, and D-2 Readiness packet."""

    schema_version: str
    real_source_inventory_executed: bool
    real_source_bytes_observed: bool
    real_source_rights_verified: bool
    d3_authorized_local_execution: bool
    duplicate_occurrences_preserved: bool
    auto_deduplication_applied: bool
    dev_eval_partition_disjoint: bool
    d2_readiness_summary: Mapping[str, Any]
    identity_custody_entries: tuple[SourceIdentityCustodyEntry, ...]
    permission_matrix: Mapping[str, str]
    owner_input_requirements: Mapping[str, Any]
    packet_digest: str

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "real_source_inventory_executed": self.real_source_inventory_executed,
            "real_source_bytes_observed": self.real_source_bytes_observed,
            "real_source_rights_verified": self.real_source_rights_verified,
            "d3_authorized_local_execution": self.d3_authorized_local_execution,
            "duplicate_occurrences_preserved": self.duplicate_occurrences_preserved,
            "auto_deduplication_applied": self.auto_deduplication_applied,
            "dev_eval_partition_disjoint": self.dev_eval_partition_disjoint,
            "d2_readiness_summary": dict(self.d2_readiness_summary),
            "identity_custody_entries": [e.to_dict() for e in self.identity_custody_entries],
            "permission_matrix": dict(self.permission_matrix),
            "owner_input_requirements": dict(self.owner_input_requirements),
        }

    def to_dict(self) -> dict[str, Any]:
        out = self.payload_without_digest()
        out["packet_digest"] = self.packet_digest
        return out


def _default_identity_custody_entries() -> tuple[SourceIdentityCustodyEntry, ...]:
    sha_shared = "11" * 32
    sha_second = "22" * 32
    sha_dev = "33" * 32
    return (
        SourceIdentityCustodyEntry(
            source_occurrence_id="occ-synth-001",
            source_revision_id="rev-ballet-01",
            source_content_id="cnt-ballet-01",
            source_sha256=sha_shared,
            source_locator="synthetic://archive/session01/cam_a_take1.mov",
            selected_stream_index=0,
            derived_artifact_id="drv-manifest-row-001",
            policy_decision_ref="pol-synth-discover-only-01",
            run_attempt_id="att-synth-mega17-01",
            partition_split="EVALUATION",
            relation_kind="PRIMARY_OCCURRENCE",
            custody_state="SYNTHETIC_DECLARED_NOT_OBSERVED",
        ),
        # Second occurrence with identical content SHA-256 but distinct occurrence_id, revision_id, and locator
        SourceIdentityCustodyEntry(
            source_occurrence_id="occ-synth-002",
            source_revision_id="rev-ballet-01-mirror",
            source_content_id="cnt-ballet-01",
            source_sha256=sha_shared,
            source_locator="synthetic://archive/backup_mirror/cam_a_take1_copy.mov",
            selected_stream_index=0,
            derived_artifact_id="drv-manifest-row-002",
            policy_decision_ref="pol-synth-discover-only-01",
            run_attempt_id="att-synth-mega17-01",
            partition_split="EVALUATION",
            relation_kind="EXACT_BYTE_DUPLICATE_PRESERVED",
            custody_state="SYNTHETIC_DECLARED_NOT_OBSERVED",
        ),
        SourceIdentityCustodyEntry(
            source_occurrence_id="occ-synth-003",
            source_revision_id="rev-dance-03",
            source_content_id="cnt-dance-03",
            source_sha256=sha_second,
            source_locator="synthetic://archive/session02/rehearsal_wide.mov",
            selected_stream_index=0,
            derived_artifact_id="drv-manifest-row-003",
            policy_decision_ref="pol-synth-discover-only-01",
            run_attempt_id="att-synth-mega17-01",
            partition_split="EVALUATION",
            relation_kind="PRIMARY_OCCURRENCE",
            custody_state="SYNTHETIC_DECLARED_NOT_OBSERVED",
        ),
        SourceIdentityCustodyEntry(
            source_occurrence_id="occ-synth-004",
            source_revision_id="rev-dev-06",
            source_content_id="cnt-dev-06",
            source_sha256=sha_dev,
            source_locator="synthetic://archive/session03/dev_calibration.mov",
            selected_stream_index=0,
            derived_artifact_id="drv-manifest-row-004",
            policy_decision_ref="pol-synth-discover-only-01",
            run_attempt_id="att-synth-mega17-01",
            partition_split="DEVELOPMENT",
            relation_kind="PRIMARY_OCCURRENCE",
            custody_state="SYNTHETIC_DECLARED_NOT_OBSERVED",
        ),
    )


def _build_owner_input_requirements() -> dict[str, Any]:
    pending_evidence = [
        {"field_id": f.field_id, "title": f.title, "validator": f.validator}
        for f in D2_FIELDS
        if f.state_rule == RULE_EVIDENCE
    ]
    blocked_rulings = [
        {"field_id": f.field_id, "title": f.title, "unresolved_ruling": f.unresolved_ruling}
        for f in D2_FIELDS
        if f.state_rule == RULE_RULING
    ]
    observation_fields = [
        {"field_id": f.field_id, "title": f.title, "unresolved_ruling": f.unresolved_ruling}
        for f in D2_FIELDS
        if f.state_rule == RULE_OBSERVATION
    ]
    return {
        "total_d2_fields": len(D2_FIELD_IDS),
        "baseline_states": dict(D2_BASELINE_STATES),
        "pending_evidence_fields": pending_evidence,
        "blocked_ruling_fields": blocked_rulings,
        "observation_only_fields": observation_fields,
        "required_d3_grants": [
            "D-3-AUTH-1: Authorized local source discovery and inventory grant",
            "D-3-AUTH-2: Authorized reviewer media observation and review_input root grant",
            "D-3-AUTH-3: Authorized Gate-0 diagnostic experiment execution & retention grant",
        ],
    }


def build_source_readiness_packet() -> SourceReadinessPacket:
    """Build deterministic Workstream B Source Identity, Custody, Rights, and D-2 Readiness packet."""
    d2_payload = build_closed_synthetic_d2_fixture_payload()
    d2_pkt = inspect_d2_readiness(d2_payload)
    if d2_pkt.status != ReadinessStatus.READY_SYNTHETIC:
        raise VipLabError(
            "WORKSTREAM_B_D2_FIXTURE_UNEXPECTED_STATE",
            f"Expected READY_SYNTHETIC from closed D-2 fixture, got {d2_pkt.status.value}: {d2_pkt.blockers}",
        )

    entries = _default_identity_custody_entries()
    eval_shas = {e.source_sha256 for e in entries if e.partition_split == "EVALUATION"}
    dev_shas = {e.source_sha256 for e in entries if e.partition_split == "DEVELOPMENT"}
    disjoint = eval_shas.isdisjoint(dev_shas)

    permission_matrix = {
        PERMISSION_DISCOVER_SOURCES: "SYNTHETIC_FIXTURE_ONLY",
        PERMISSION_INSPECT_LOCAL_BYTES: "NOT_AUTHORIZED",
        PERMISSION_CREATE_DERIVED_ARTIFACTS: "SYNTHETIC_FIXTURE_ONLY",
        PERMISSION_RUN_AUTHENTIC_MODELS: "NOT_AUTHORIZED",
        PERMISSION_PROVIDER_OR_CLOUD_EGRESS: "FORBIDDEN_NO_EGRESS",
        PERMISSION_RETAIN_OUTPUTS: "NOT_AUTHORIZED",
        PERMISSION_EXPORT_OUTPUTS: "NOT_AUTHORIZED",
    }

    summary_slim = {
        "package_id": d2_pkt.summary["package_id"],
        "package_digest": d2_pkt.summary["package_digest"],
        "attestation_state": d2_pkt.summary["attestation_state"],
        "authenticity": d2_pkt.summary["authenticity"],
        "verified_count": d2_pkt.summary["verified_count"],
        "pending_count": d2_pkt.summary["pending_count"],
        "blocked_count": d2_pkt.summary["blocked_count"],
        "not_observed_count": d2_pkt.summary["not_observed_count"],
        "owner_approval_claimed": d2_pkt.summary["owner_approval_claimed"],
        "execution_authorized": d2_pkt.summary["execution_authorized"],
        "d3_status": d2_pkt.summary["d3_status"],
        "field_states": dict(d2_pkt.summary["field_states"]),
    }

    provisional = SourceReadinessPacket(
        schema_version=SOURCE_READINESS_SCHEMA_VERSION,
        real_source_inventory_executed=False,
        real_source_bytes_observed=False,
        real_source_rights_verified=False,
        d3_authorized_local_execution=False,
        duplicate_occurrences_preserved=True,
        auto_deduplication_applied=False,
        dev_eval_partition_disjoint=disjoint,
        d2_readiness_summary=summary_slim,
        identity_custody_entries=entries,
        permission_matrix=permission_matrix,
        owner_input_requirements=_build_owner_input_requirements(),
        packet_digest="0" * 64,
    )
    digest = canonical_sha256(provisional.payload_without_digest())
    return SourceReadinessPacket(
        schema_version=provisional.schema_version,
        real_source_inventory_executed=False,
        real_source_bytes_observed=False,
        real_source_rights_verified=False,
        d3_authorized_local_execution=False,
        duplicate_occurrences_preserved=True,
        auto_deduplication_applied=False,
        dev_eval_partition_disjoint=provisional.dev_eval_partition_disjoint,
        d2_readiness_summary=provisional.d2_readiness_summary,
        identity_custody_entries=provisional.identity_custody_entries,
        permission_matrix=provisional.permission_matrix,
        owner_input_requirements=provisional.owner_input_requirements,
        packet_digest=digest,
    )


def verify_source_readiness_packet(
    packet: SourceReadinessPacket | Mapping[str, Any],
) -> dict[str, Any]:
    """Verify integrity and Section 7 non-execution invariants of a SourceReadinessPacket."""
    raw = packet.to_dict() if isinstance(packet, SourceReadinessPacket) else dict(packet)
    if raw.get("schema_version") != SOURCE_READINESS_SCHEMA_VERSION:
        raise VipLabError(
            "SOURCE_READINESS_SCHEMA_MISMATCH",
            f"Expected {SOURCE_READINESS_SCHEMA_VERSION}, got {raw.get('schema_version')!r}",
        )
    if (
        raw.get("real_source_inventory_executed") is not False
        or raw.get("real_source_bytes_observed") is not False
        or raw.get("real_source_rights_verified") is not False
        or raw.get("d3_authorized_local_execution") is not False
        or raw.get("duplicate_occurrences_preserved") is not True
        or raw.get("auto_deduplication_applied") is not False
    ):
        raise VipLabError(
            "SOURCE_READINESS_INVARIANT_VIOLATION",
            "SourceReadinessPacket violated mandatory Section 7 invariants.",
        )
    declared_digest = validate_hex_digest(
        str(raw.get("packet_digest", "")),
        field_name="packet_digest",
    )
    body = {k: v for k, v in raw.items() if k != "packet_digest"}
    computed = canonical_sha256(body)
    if declared_digest != computed:
        raise VipLabError(
            "SOURCE_READINESS_DIGEST_MISMATCH",
            f"packet_digest mismatch: declared {declared_digest} != computed {computed}",
        )
    return raw


def inspect_source_and_d2_readiness(
    payload: Mapping[str, Any] | None = None,
) -> ReadinessPacket:
    """Inspect Workstream B source identity, custody, permission separation, and D-2 readiness."""
    raw_payload = dict(payload) if isinstance(payload, Mapping) else {}
    cleaned, untrusted_flags = sanitize_untrusted_authority_claims(raw_payload)

    findings: list[ReadinessFinding] = []
    reasons: list[str] = []
    blockers: list[str] = []

    if untrusted_flags:
        reasons.append("UNTRUSTED_AUTHORITY_FLAGS_IGNORED")
        findings.append(
            ReadinessFinding(
                code="WORKSTREAM_B_UNTRUSTED_AUTHORITY_STRIPPED",
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Ignored untrusted authority flags in Workstream B payload.",
                details={"ignored_keys": list(untrusted_flags)},
            )
        )

    if bool(raw_payload.get("infer_byte_identity_from_filename", False)):
        blockers.append(REFUSAL_FILENAME_EQUALITY_NOT_BYTE_IDENTITY)
        reasons.append(REFUSAL_FILENAME_EQUALITY_NOT_BYTE_IDENTITY)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_FILENAME_EQUALITY_NOT_BYTE_IDENTITY,
                status=ReadinessStatus.BLOCKED,
                message="Identical filename or locator never establishes content byte identity without SHA-256 verification.",
            )
        )

    if bool(raw_payload.get("collapse_duplicate_sha256_occurrences", False)):
        blockers.append(REFUSAL_DUPLICATE_OCCURRENCE_COLLAPSE_FORBIDDEN)
        reasons.append(REFUSAL_DUPLICATE_OCCURRENCE_COLLAPSE_FORBIDDEN)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_DUPLICATE_OCCURRENCE_COLLAPSE_FORBIDDEN,
                status=ReadinessStatus.BLOCKED,
                message="Duplicate SHA-256 occurrences must retain distinct occurrence_id and revision_id and must never be auto-deleted or skipped.",
            )
        )

    if bool(raw_payload.get("claim_forged_owner_attestation", False)):
        blockers.append(REFUSAL_FORGED_OWNER_ATTESTATION)
        reasons.append(REFUSAL_FORGED_OWNER_ATTESTATION)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_FORGED_OWNER_ATTESTATION,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Forged or unauthenticated Owner attestation cannot promote D-2 fields to VERIFIED.",
            )
        )

    if bool(raw_payload.get("claim_d3_execution_authorized", False)):
        blockers.append(REFUSAL_D3_EXECUTION_NOT_AUTHORIZED)
        reasons.append(REFUSAL_D3_EXECUTION_NOT_AUTHORIZED)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_D3_EXECUTION_NOT_AUTHORIZED,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="D-3 real archive execution is not authorized.",
            )
        )

    if bool(raw_payload.get("treat_discovery_as_processing_grant", False)):
        blockers.append(REFUSAL_DISCOVERY_DOES_NOT_GRANT_PROCESSING)
        reasons.append(REFUSAL_DISCOVERY_DOES_NOT_GRANT_PROCESSING)
        findings.append(
            ReadinessFinding(
                code=REFUSAL_DISCOVERY_DOES_NOT_GRANT_PROCESSING,
                status=ReadinessStatus.NOT_AUTHORIZED,
                message="Permission to discover paths never grants permission to read bytes, create derived artifacts, run authentic models, egress, retain, or export.",
            )
        )

    partition_check = cleaned.get("partition_check")
    if isinstance(partition_check, Mapping):
        dev_revs = {str(x) for x in partition_check.get("development_revision_ids", ())}
        eval_revs = {str(x) for x in partition_check.get("evaluation_revision_ids", ())}
        overlap = sorted(dev_revs & eval_revs)
        if overlap:
            blockers.append(REFUSAL_DEV_EVAL_PARTITION_LEAKAGE)
            reasons.append(REFUSAL_DEV_EVAL_PARTITION_LEAKAGE)
            findings.append(
                ReadinessFinding(
                    code=REFUSAL_DEV_EVAL_PARTITION_LEAKAGE,
                    status=ReadinessStatus.BLOCKED,
                    message=f"DEVELOPMENT and EVALUATION partitions share revision IDs: {overlap}",
                    details={"overlapping_revisions": overlap},
                )
            )

    pkt = build_source_readiness_packet()

    has_auth_refusal = any(f.status == ReadinessStatus.NOT_AUTHORIZED for f in findings)
    if has_auth_refusal:
        status = ReadinessStatus.NOT_AUTHORIZED
    elif blockers:
        status = ReadinessStatus.BLOCKED
    else:
        status = ReadinessStatus.READY_SYNTHETIC
        reasons.append("SOURCE_AND_D2_SYNTHETIC_READINESS_VERIFIED")
        findings.append(
            ReadinessFinding(
                code="SOURCE_AND_D2_SYNTHETIC_READINESS_VERIFIED",
                status=ReadinessStatus.READY_SYNTHETIC,
                message="Validated 30-field D-2 intake, 8-layer source identity separation, and 7-permission boundaries.",
            )
        )

    return ReadinessPacket(
        stage_id=STAGE_ID,
        status=status,
        owner_approval_status="NOT_GRANTED",
        gate_verdict="NOT_AUTHORIZED",
        evidence_state=NOT_OBSERVED,
        reasons=tuple(reasons),
        blockers=tuple(blockers),
        findings=tuple(findings),
        summary={
            "packet_digest": pkt.packet_digest,
            "real_source_inventory_executed": False,
            "real_source_bytes_observed": False,
            "real_source_rights_verified": False,
            "d3_authorized_local_execution": False,
            "duplicate_occurrences_preserved": pkt.duplicate_occurrences_preserved,
            "d2_verified_count": pkt.d2_readiness_summary["verified_count"],
            "d2_pending_count": pkt.d2_readiness_summary["pending_count"],
            "d2_blocked_count": pkt.d2_readiness_summary["blocked_count"],
            "d2_not_observed_count": pkt.d2_readiness_summary["not_observed_count"],
        },
    )
