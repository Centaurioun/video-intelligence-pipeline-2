"""Candidate temporal refinement request builder and verifier for MEGA-10.

Packet P10 — Candidate Temporal Request & Source-Native Diagnostic (`LAB-MEGA-08-14-v1.0.0`).

Invariants enforced:
- Consumes a MEGA-09 ``CandidateQueueItem`` and upstream ``queue_digest``.
- Keeps ``measurement_needed=True``, ``source_pts_evidence_state="NOT_OBSERVED"``,
  ``candidate_evidence_class="MATCHED"``, ``binding_eligible=False``, and
  ``refinement_status="SYNTHETIC_DIAGNOSTIC_ONLY"``.
- Never promotes a semantic candidate timestamp into a ``MEASURED`` frame-accurate cut.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..common import (
    NOT_OBSERVED,
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)
from ..mega09.candidate_queue import CandidateQueueItem
from .pts_fixture_diagnostics import (
    PtsFixtureDiagnostic,
    evaluate_pts_fixture_diagnostic,
)


TEMPORAL_REQUEST_SCHEMA_VERSION = "vip-lab-temporal-refinement-request-v1"


@dataclass(frozen=True)
class TemporalRefinementRequest:
    """Immutable nonbinding request for source-native temporal measurement."""

    schema_version: str
    request_id: str
    upstream_queue_digest: str
    queue_item_id: str
    arm_id: str
    profile_id: str
    query_id: str
    revision_id: str
    content_id: str
    source_path: str
    source_sha256: str
    selected_stream_index: int
    candidate_sample_pts: int
    timebase_num: int
    timebase_den: int
    requested_start_pts: int
    requested_end_pts: int
    measurement_needed: bool
    source_pts_evidence_state: str
    candidate_evidence_class: str
    binding_eligible: bool
    refinement_status: str
    synthetic_pts_diagnostic: PtsFixtureDiagnostic | None
    request_digest: str
    synthetic_only: bool = True

    def __post_init__(self) -> None:
        if self.schema_version != TEMPORAL_REQUEST_SCHEMA_VERSION:
            raise VipLabError(
                "TEMPORAL_REQUEST_SCHEMA_INVALID",
                f"Expected schema_version {TEMPORAL_REQUEST_SCHEMA_VERSION!r}",
            )
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise VipLabError("TEMPORAL_REQUEST_ID_INVALID", "request_id must be non-empty")
        validate_hex_digest(
            self.upstream_queue_digest,
            field_name="upstream_queue_digest",
            error_code="TEMPORAL_REQUEST_QUEUE_DIGEST_INVALID",
        )
        validate_hex_digest(
            self.source_sha256,
            field_name="source_sha256",
            error_code="TEMPORAL_REQUEST_SOURCE_SHA256_INVALID",
        )
        validate_hex_digest(
            self.request_digest,
            field_name="request_digest",
            error_code="TEMPORAL_REQUEST_DIGEST_INVALID",
        )
        if type(self.selected_stream_index) is not int or self.selected_stream_index < 0:
            raise VipLabError(
                "TEMPORAL_REQUEST_STREAM_INDEX_INVALID",
                "selected_stream_index must be int >= 0",
            )
        if (
            type(self.candidate_sample_pts) is not int
            or type(self.timebase_num) is not int
            or type(self.timebase_den) is not int
            or self.timebase_num <= 0
            or self.timebase_den <= 0
        ):
            raise VipLabError(
                "TEMPORAL_REQUEST_TIMEBASE_INVALID",
                "candidate_sample_pts and rational timebase must be valid integers",
            )
        if (
            type(self.requested_start_pts) is not int
            or type(self.requested_end_pts) is not int
            or self.requested_end_pts <= self.requested_start_pts
        ):
            raise VipLabError(
                "TEMPORAL_REQUEST_INTERVAL_INVALID",
                "requested_start_pts and requested_end_pts must form a non-degenerate interval",
            )
        if self.measurement_needed is not True:
            raise VipLabError(
                "TEMPORAL_REQUEST_MEASUREMENT_NEEDED_REQUIRED",
                "measurement_needed must be True in synthetic laboratory requests",
            )
        if self.source_pts_evidence_state != NOT_OBSERVED:
            raise VipLabError(
                "SYNTHETIC_TEMPORAL_CANNOT_CLAIM_MEASURED",
                f"source_pts_evidence_state must remain 'NOT_OBSERVED', got {self.source_pts_evidence_state!r}",
            )
        if self.candidate_evidence_class != "MATCHED":
            raise VipLabError(
                "TEMPORAL_REQUEST_CANDIDATE_CLASS_INVALID",
                "candidate_evidence_class must be 'MATCHED'",
            )
        if self.binding_eligible is not False:
            raise VipLabError(
                "TEMPORAL_REQUEST_BINDING_FORBIDDEN",
                "binding_eligible must be False",
            )
        if self.refinement_status != "SYNTHETIC_DIAGNOSTIC_ONLY":
            raise VipLabError(
                "TEMPORAL_REQUEST_STATUS_INVALID",
                "refinement_status must be 'SYNTHETIC_DIAGNOSTIC_ONLY'",
            )
        if self.synthetic_only is not True:
            raise VipLabError(
                "TEMPORAL_REQUEST_SYNTHETIC_ONLY_REQUIRED",
                "synthetic_only must be True",
            )

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "upstream_queue_digest": self.upstream_queue_digest,
            "queue_item_id": self.queue_item_id,
            "arm_id": self.arm_id,
            "profile_id": self.profile_id,
            "query_id": self.query_id,
            "revision_id": self.revision_id,
            "content_id": self.content_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "selected_stream_index": self.selected_stream_index,
            "candidate_sample_pts": self.candidate_sample_pts,
            "timebase_num": self.timebase_num,
            "timebase_den": self.timebase_den,
            "requested_start_pts": self.requested_start_pts,
            "requested_end_pts": self.requested_end_pts,
            "measurement_needed": self.measurement_needed,
            "source_pts_evidence_state": self.source_pts_evidence_state,
            "candidate_evidence_class": self.candidate_evidence_class,
            "binding_eligible": self.binding_eligible,
            "refinement_status": self.refinement_status,
            "synthetic_only": self.synthetic_only,
            "synthetic_pts_diagnostic": (
                self.synthetic_pts_diagnostic.to_dict()
                if self.synthetic_pts_diagnostic is not None
                else None
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload_without_digest()
        body["request_digest"] = self.request_digest
        return body


def compute_temporal_request_digest(payload_without_digest: Mapping[str, Any]) -> str:
    """Compute canonical SHA-256 digest of a TemporalRefinementRequest payload."""
    body = {k: v for k, v in payload_without_digest.items() if k != "request_digest"}
    return canonical_sha256(body)


def build_temporal_refinement_request(
    item: CandidateQueueItem,
    *,
    upstream_queue_digest: str,
    selected_stream_index: int = 0,
    requested_start_pts: int | None = None,
    requested_end_pts: int | None = None,
    pts_ticks: Sequence[int] | None = None,
    start_occurrence: int | None = None,
    end_occurrence: int | None = None,
    declared_rate_num: int | None = None,
    declared_rate_den: int | None = None,
) -> TemporalRefinementRequest:
    """Construct a deterministic TemporalRefinementRequest from a CandidateQueueItem."""
    if not isinstance(item, CandidateQueueItem):
        raise VipLabError(
            "TEMPORAL_REQUEST_ITEM_REQUIRED",
            "Expected CandidateQueueItem instance",
        )
    validate_hex_digest(
        upstream_queue_digest,
        field_name="upstream_queue_digest",
        error_code="TEMPORAL_REQUEST_QUEUE_DIGEST_INVALID",
    )

    start_pts = (
        requested_start_pts
        if requested_start_pts is not None
        else item.source_sample_pts
    )
    end_pts = (
        requested_end_pts
        if requested_end_pts is not None
        else item.source_sample_pts + item.source_timebase_num
    )

    diag: PtsFixtureDiagnostic | None = None
    if pts_ticks is not None:
        diag = evaluate_pts_fixture_diagnostic(
            timebase_num=item.source_timebase_num,
            timebase_den=item.source_timebase_den,
            pts_ticks=pts_ticks,
            requested_start_pts=start_pts,
            requested_end_pts=end_pts,
            start_occurrence=start_occurrence,
            end_occurrence=end_occurrence,
            declared_rate_num=declared_rate_num,
            declared_rate_den=declared_rate_den,
        )

    seed = {
        "upstream_queue_digest": upstream_queue_digest,
        "queue_item_id": item.queue_item_id,
        "revision_id": item.revision_id,
        "selected_stream_index": selected_stream_index,
        "requested_start_pts": start_pts,
        "requested_end_pts": end_pts,
    }
    request_id = f"trr-{item.query_id}-{canonical_sha256(seed)[:16]}"

    provisional = TemporalRefinementRequest(
        schema_version=TEMPORAL_REQUEST_SCHEMA_VERSION,
        request_id=request_id,
        upstream_queue_digest=upstream_queue_digest,
        queue_item_id=item.queue_item_id,
        arm_id=item.arm_id,
        profile_id=item.profile_id,
        query_id=item.query_id,
        revision_id=item.revision_id,
        content_id=item.content_id,
        source_path=item.source_path,
        source_sha256=item.source_sha256,
        selected_stream_index=selected_stream_index,
        candidate_sample_pts=item.source_sample_pts,
        timebase_num=item.source_timebase_num,
        timebase_den=item.source_timebase_den,
        requested_start_pts=start_pts,
        requested_end_pts=end_pts,
        measurement_needed=True,
        source_pts_evidence_state=NOT_OBSERVED,
        candidate_evidence_class="MATCHED",
        binding_eligible=False,
        refinement_status="SYNTHETIC_DIAGNOSTIC_ONLY",
        synthetic_pts_diagnostic=diag,
        request_digest="0" * 64,
        synthetic_only=True,
    )
    digest = compute_temporal_request_digest(provisional.payload_without_digest())
    return TemporalRefinementRequest(
        schema_version=provisional.schema_version,
        request_id=provisional.request_id,
        upstream_queue_digest=provisional.upstream_queue_digest,
        queue_item_id=provisional.queue_item_id,
        arm_id=provisional.arm_id,
        profile_id=provisional.profile_id,
        query_id=provisional.query_id,
        revision_id=provisional.revision_id,
        content_id=provisional.content_id,
        source_path=provisional.source_path,
        source_sha256=provisional.source_sha256,
        selected_stream_index=provisional.selected_stream_index,
        candidate_sample_pts=provisional.candidate_sample_pts,
        timebase_num=provisional.timebase_num,
        timebase_den=provisional.timebase_den,
        requested_start_pts=provisional.requested_start_pts,
        requested_end_pts=provisional.requested_end_pts,
        measurement_needed=True,
        source_pts_evidence_state=NOT_OBSERVED,
        candidate_evidence_class="MATCHED",
        binding_eligible=False,
        refinement_status="SYNTHETIC_DIAGNOSTIC_ONLY",
        synthetic_pts_diagnostic=diag,
        request_digest=digest,
        synthetic_only=True,
    )


def verify_temporal_refinement_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Verify a TemporalRefinementRequest dictionary and its canonical SHA-256 digest."""
    if not isinstance(payload, Mapping):
        raise VipLabError("TEMPORAL_REQUEST_NOT_MAPPING", "payload must be a mapping")
    if payload.get("schema_version") != TEMPORAL_REQUEST_SCHEMA_VERSION:
        raise VipLabError(
            "TEMPORAL_REQUEST_SCHEMA_INVALID",
            f"Invalid schema_version {payload.get('schema_version')!r}",
        )
    if payload.get("measurement_needed") is not True:
        raise VipLabError(
            "TEMPORAL_REQUEST_MEASUREMENT_NEEDED_REQUIRED",
            "measurement_needed must be True",
        )
    if payload.get("source_pts_evidence_state") != NOT_OBSERVED:
        raise VipLabError(
            "SYNTHETIC_TEMPORAL_CANNOT_CLAIM_MEASURED",
            "source_pts_evidence_state must be 'NOT_OBSERVED'",
        )
    if payload.get("candidate_evidence_class") != "MATCHED":
        raise VipLabError(
            "TEMPORAL_REQUEST_CANDIDATE_CLASS_INVALID",
            "candidate_evidence_class must be 'MATCHED'",
        )
    if payload.get("binding_eligible") is not False:
        raise VipLabError(
            "TEMPORAL_REQUEST_BINDING_FORBIDDEN",
            "binding_eligible must be False",
        )
    if payload.get("refinement_status") != "SYNTHETIC_DIAGNOSTIC_ONLY":
        raise VipLabError(
            "TEMPORAL_REQUEST_STATUS_INVALID",
            "refinement_status must be 'SYNTHETIC_DIAGNOSTIC_ONLY'",
        )
    declared_digest = validate_hex_digest(
        payload.get("request_digest"),
        field_name="request_digest",
        error_code="TEMPORAL_REQUEST_DIGEST_INVALID",
    )
    expected_digest = compute_temporal_request_digest(payload)
    if declared_digest != expected_digest:
        raise VipLabError(
            "TEMPORAL_REQUEST_DIGEST_MISMATCH",
            f"TemporalRefinementRequest digest mismatch: {declared_digest} != {expected_digest}",
        )
    return dict(payload)
