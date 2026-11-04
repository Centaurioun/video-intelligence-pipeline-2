"""MEGA-15.1 — Deterministic Temporal Refinement Preflight & Gate-3 Request Construction.

Bridges MEGA-10 (`TemporalRefinementRequest` + `PtsFixtureDiagnostic`) to canonical
Gate-3 (`gate3.pts`, `gate3.temporal`, `gate3.refinement_request`, `gate3.refinement`)
solely on synthetic PTS fixtures.

Strict Non-Negotiable Invariants:
- No real video files, FFmpeg, FFprobe, or container media probes are invoked.
- Semantic retrieval candidates (`MATCHED`) are never treated as exact frame-accurate cuts.
- `seconds * nominal_fps` derivation is strictly refused.
- Duplicate PTS values without an explicit 0-based `occurrence` selector are refused.
- Unresolved PTS discontinuities (> 3x median positive delta) are refused unless
  explicitly subdivided via `gate3.temporal.subdivide_on_discontinuity`.
- Stream identity is fixed to canonical `video:<index>` namespace; audio or ambiguous
  stream namespaces are refused.
- Output `TemporalPreparationRecord` remains `source_pts_evidence_state = "NOT_OBSERVED"`,
  `binding_eligible = False`, and `authoritative_source_measurement = False`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from gate3.pts import PtsTable
from gate3.rational import Rational, TimeBase
from gate3.refinement_request import RefinementRequest
from gate3.temporal import (
    SnapResult,
    classify_vfr,
    detect_discontinuity,
    resolve_end,
    resolve_start,
    subdivide_on_discontinuity,
    tail_end,
)
from vip_lab.common import (
    FORBIDDEN_EXTERNAL_AUTHORITY_KEYS,
    SYNTHETIC_CONTEXT_TOKEN,
    SyntheticContextMarker,
    VipLabError,
    canonical_sha256,
)
from vip_lab.mega10 import (
    PtsFixtureDiagnostic,
    TemporalRefinementRequest,
    verify_temporal_refinement_request,
)

TEMPORAL_PREFLIGHT_SCHEMA_VERSION = "1.0.0"
TEMPORAL_PREFLIGHT_KIND = "vip_lab.mega15.temporal_preparation_record"

# Explicit refusal codes for MEGA-15.1
REFUSAL_NOMINAL_FPS_DERIVATION = "REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN"
REFUSAL_CANDIDATE_AS_EXACT_CUT = "REFUSAL_SEMANTIC_CANDIDATE_AS_EXACT_CUT_FORBIDDEN"
REFUSAL_DUPLICATE_PTS_AMBIGUOUS = "REFUSAL_DUPLICATE_PTS_REQUIRES_OCCURRENCE"
REFUSAL_PTS_DISCONTINUITY_UNRESOLVED = "REFUSAL_PTS_DISCONTINUITY_UNRESOLVED"
REFUSAL_TERMINAL_TAIL_UNRESOLVED = "REFUSAL_TERMINAL_TAIL_UNRESOLVED"
REFUSAL_STREAM_NAMESPACE_MISMATCH = "REFUSAL_STREAM_NAMESPACE_MISMATCH"
REFUSAL_TIMEBASE_MISMATCH = "REFUSAL_TIMEBASE_MISMATCH"
REFUSAL_FORGED_SOURCE_MEASUREMENT = "REFUSAL_FORGED_SOURCE_MEASUREMENT_FORBIDDEN"
REFUSAL_BINDING_ELIGIBILITY_ESCALATION = "REFUSAL_BINDING_ELIGIBILITY_ESCALATION_FORBIDDEN"
REFUSAL_PTS_NON_MONOTONIC = "REFUSAL_PTS_TABLE_NON_MONOTONIC_OR_INVALID"
REFUSAL_SYNTHETIC_TO_REAL_ESCALATION = "REFUSAL_SYNTHETIC_TO_REAL_ESCALATION_FORBIDDEN"

_EXTRA_UNTRUSTED_AUTHORITY_KEYS: frozenset[str] = frozenset(
    {
        "human_approved",
        "owner_approved",
        "production_export_authorized",
        "gate_promoted",
        "real_human_approved",
        "authoritative_source_measurement",
    }
)


def ensure_non_empty_str(value: object, field_name: str) -> str:
    """Validate that ``value`` is a non-empty, non-whitespace string."""
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise_mega15_error(
            "MEGA15_INVALID_NON_EMPTY_STRING",
            f"Field {field_name!r} must be a non-empty string",
            field_path=field_name,
        )
    return value


def raise_mega15_error(
    code: str,
    detail: str,
    *,
    field_path: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> None:
    """Raise a canonical two-argument VipLabError whose message begins with ``code``."""
    msg = detail if detail.startswith(code) else f"{code}: {detail}"
    raise VipLabError(code, msg, field_path=field_path, details=details)


def make_synthetic_context() -> SyntheticContextMarker:
    """Create a canonical SyntheticContextMarker instance."""
    return SyntheticContextMarker.create()


def validate_synthetic_context(ctx: Any) -> SyntheticContextMarker:
    """Verify that ``ctx`` is an unescalated ``SyntheticContextMarker``."""
    if not isinstance(ctx, SyntheticContextMarker):
        raise_mega15_error(
            REFUSAL_SYNTHETIC_TO_REAL_ESCALATION,
            "synthetic_context must be a SyntheticContextMarker instance",
        )
    if (
        ctx.token != SYNTHETIC_CONTEXT_TOKEN
        or ctx.synthetic_only is not True
        or ctx.authentic_authority_granted is not False
    ):
        raise_mega15_error(
            REFUSAL_SYNTHETIC_TO_REAL_ESCALATION,
            f"Invalid or escalated SyntheticContextMarker: {ctx!r}",
        )
    return ctx


def serialize_synthetic_context(ctx: SyntheticContextMarker) -> dict[str, Any]:
    """Serialize ``SyntheticContextMarker`` to a deterministic JSON dictionary."""
    validate_synthetic_context(ctx)
    return {
        "token": ctx.token,
        "synthetic_only": ctx.synthetic_only,
        "authentic_authority_granted": ctx.authentic_authority_granted,
    }


def parse_synthetic_context_dict(payload: Mapping[str, Any]) -> SyntheticContextMarker:
    """Validate an untrusted dictionary representation of ``SyntheticContextMarker``."""
    if not isinstance(payload, Mapping):
        raise_mega15_error(
            REFUSAL_SYNTHETIC_TO_REAL_ESCALATION,
            "synthetic_context payload must be a mapping",
        )
    forbidden_keys = (set(payload.keys()) & FORBIDDEN_EXTERNAL_AUTHORITY_KEYS) | (
        set(payload.keys()) & _EXTRA_UNTRUSTED_AUTHORITY_KEYS
    )
    if forbidden_keys:
        raise_mega15_error(
            REFUSAL_SYNTHETIC_TO_REAL_ESCALATION,
            f"Forbidden authority keys in synthetic_context: {sorted(forbidden_keys)}",
        )
    if (
        payload.get("token") != SYNTHETIC_CONTEXT_TOKEN
        or payload.get("synthetic_only") is not True
        or payload.get("authentic_authority_granted") is not False
    ):
        raise_mega15_error(
            REFUSAL_SYNTHETIC_TO_REAL_ESCALATION,
            "Untrusted synthetic_context failed synthetic-only verification",
        )
    return SyntheticContextMarker.create()


def refuse_nominal_fps_derivation(
    *,
    seconds: float | int | None = None,
    nominal_fps: float | int | None = None,
    derivation_mode: str | None = None,
) -> None:
    """Fail closed whenever a caller attempts to derive frame/PTS boundaries via seconds * nominal_fps."""
    if seconds is not None or nominal_fps is not None or derivation_mode is not None:
        raise_mega15_error(
            REFUSAL_NOMINAL_FPS_DERIVATION,
            "Deriving VFR/CFR frame or PTS positions via seconds * nominal_fps is strictly forbidden; "
            f"received seconds={seconds!r}, nominal_fps={nominal_fps!r}, derivation_mode={derivation_mode!r}.",
        )


def refuse_semantic_candidate_as_cut(
    *,
    evidence_class: str,
    treat_as_exact_cut: bool = False,
) -> None:
    """Fail closed if a semantic candidate is used directly as an exact cut boundary."""
    if treat_as_exact_cut or evidence_class != "MATCHED":
        raise_mega15_error(
            REFUSAL_CANDIDATE_AS_EXACT_CUT,
            "Semantic retrieval candidate timestamps cannot be used as exact frame-accurate edit boundaries "
            f"(evidence_class={evidence_class!r}, treat_as_exact_cut={treat_as_exact_cut!r}).",
        )


def validate_video_stream_namespace(stream_id: str) -> int:
    """Validate canonical `video:<non_negative_int>` stream identity and return stream index."""
    ensure_non_empty_str(stream_id, "stream_id")
    if not stream_id.startswith("video:"):
        raise_mega15_error(
            REFUSAL_STREAM_NAMESPACE_MISMATCH,
            f"Stream namespace must be 'video:<index>', got {stream_id!r}",
        )
    suffix = stream_id[len("video:") :]
    if not suffix.isdigit():
        raise_mega15_error(
            REFUSAL_STREAM_NAMESPACE_MISMATCH,
            f"Video stream index must be non-negative decimal integer, got {stream_id!r}",
        )
    return int(suffix)


@dataclass(frozen=True)
class TemporalPreparationRecord:
    """Synthetic Gate-3 temporal preflight record derived from MEGA-10 + Gate-3 temporal utilities."""

    schema_version: str
    kind: str
    record_id: str
    upstream_request_id: str
    upstream_request_digest: str
    queue_item_id: str
    arm_id: str
    profile_id: str
    query_id: str
    revision_id: str
    content_id: str
    source_path: str
    source_sha256: str
    selected_stream_index: int
    stream_id: str
    timebase_num: int
    timebase_den: int
    pts_ticks: tuple[int, ...]
    candidate_sample_pts: int
    requested_start_pts: int
    requested_end_pts: int
    start_occurrence: int | None
    end_occurrence: int | None
    resolved_start_pts: int
    resolved_end_pts: int
    start_snap_policy: str
    end_snap_policy: str
    endpoint_semantics: str
    is_vfr: bool
    vfr_classification: str
    has_discontinuity: bool
    discontinuity_subdivided: bool
    subdivided_segments: tuple[tuple[int, int], ...]
    gate3_refinement_request: dict[str, Any]
    candidate_evidence_class: str
    source_pts_evidence_state: str
    authoritative_source_measurement: bool
    binding_eligible: bool
    synthetic_context: SyntheticContextMarker
    record_digest: str

    @property
    def candidate_item_id(self) -> str:
        """Compatibility alias for ``queue_item_id``."""
        return self.queue_item_id

    @property
    def source_revision_id(self) -> str:
        """Compatibility alias for ``revision_id``."""
        return self.revision_id

    @property
    def source_timebase_num(self) -> int:
        """Compatibility alias for ``timebase_num``."""
        return self.timebase_num

    @property
    def source_timebase_den(self) -> int:
        """Compatibility alias for ``timebase_den``."""
        return self.timebase_den

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "record_id": self.record_id,
            "upstream_request_id": self.upstream_request_id,
            "upstream_request_digest": self.upstream_request_digest,
            "queue_item_id": self.queue_item_id,
            "arm_id": self.arm_id,
            "profile_id": self.profile_id,
            "query_id": self.query_id,
            "revision_id": self.revision_id,
            "content_id": self.content_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "selected_stream_index": self.selected_stream_index,
            "stream_id": self.stream_id,
            "timebase_num": self.timebase_num,
            "timebase_den": self.timebase_den,
            "pts_ticks": list(self.pts_ticks),
            "candidate_sample_pts": self.candidate_sample_pts,
            "requested_start_pts": self.requested_start_pts,
            "requested_end_pts": self.requested_end_pts,
            "start_occurrence": self.start_occurrence,
            "end_occurrence": self.end_occurrence,
            "resolved_start_pts": self.resolved_start_pts,
            "resolved_end_pts": self.resolved_end_pts,
            "start_snap_policy": self.start_snap_policy,
            "end_snap_policy": self.end_snap_policy,
            "endpoint_semantics": self.endpoint_semantics,
            "is_vfr": self.is_vfr,
            "vfr_classification": self.vfr_classification,
            "has_discontinuity": self.has_discontinuity,
            "discontinuity_subdivided": self.discontinuity_subdivided,
            "subdivided_segments": [[s, e] for s, e in self.subdivided_segments],
            "gate3_refinement_request": self.gate3_refinement_request,
            "candidate_evidence_class": self.candidate_evidence_class,
            "source_pts_evidence_state": self.source_pts_evidence_state,
            "authoritative_source_measurement": self.authoritative_source_measurement,
            "binding_eligible": self.binding_eligible,
            "synthetic_context": serialize_synthetic_context(self.synthetic_context),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._digest_payload()
        payload["record_digest"] = self.record_digest
        return payload

    def validate(self) -> None:
        if self.schema_version != TEMPORAL_PREFLIGHT_SCHEMA_VERSION:
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_SCHEMA_MISMATCH",
                f"Unsupported schema_version: {self.schema_version!r}",
            )
        if self.kind != TEMPORAL_PREFLIGHT_KIND:
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_KIND_MISMATCH",
                f"Unsupported kind: {self.kind!r}",
            )
        ensure_non_empty_str(self.record_id, "record_id")
        ensure_non_empty_str(self.upstream_request_id, "upstream_request_id")
        ensure_non_empty_str(self.upstream_request_digest, "upstream_request_digest")
        ensure_non_empty_str(self.queue_item_id, "queue_item_id")
        ensure_non_empty_str(self.arm_id, "arm_id")
        ensure_non_empty_str(self.profile_id, "profile_id")
        ensure_non_empty_str(self.query_id, "query_id")
        ensure_non_empty_str(self.revision_id, "revision_id")
        ensure_non_empty_str(self.content_id, "content_id")
        ensure_non_empty_str(self.source_path, "source_path")
        ensure_non_empty_str(self.source_sha256, "source_sha256")
        idx = validate_video_stream_namespace(self.stream_id)
        if idx != self.selected_stream_index:
            raise_mega15_error(
                REFUSAL_STREAM_NAMESPACE_MISMATCH,
                f"stream_id index {idx} != selected_stream_index {self.selected_stream_index}",
            )

        validate_synthetic_context(self.synthetic_context)

        if self.candidate_evidence_class != "MATCHED":
            raise_mega15_error(
                REFUSAL_CANDIDATE_AS_EXACT_CUT,
                f"candidate_evidence_class must be 'MATCHED', got {self.candidate_evidence_class!r}",
            )
        if self.source_pts_evidence_state != "NOT_OBSERVED":
            raise_mega15_error(
                REFUSAL_FORGED_SOURCE_MEASUREMENT,
                f"source_pts_evidence_state must remain 'NOT_OBSERVED', got {self.source_pts_evidence_state!r}",
            )
        if self.authoritative_source_measurement is not False:
            raise_mega15_error(
                REFUSAL_FORGED_SOURCE_MEASUREMENT,
                "authoritative_source_measurement must remain False in synthetic preflight",
            )
        if self.binding_eligible is not False:
            raise_mega15_error(
                REFUSAL_BINDING_ELIGIBILITY_ESCALATION,
                "binding_eligible must remain False in synthetic preflight",
            )
        if self.endpoint_semantics != "HALF_OPEN_START_INCLUSIVE_END_EXCLUSIVE":
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_INVALID_ENDPOINT_SEMANTICS",
                f"Invalid endpoint_semantics: {self.endpoint_semantics!r}",
            )
        if self.resolved_end_pts <= self.resolved_start_pts:
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_INVALID_INTERVAL",
                f"Resolved interval must be positive: [{self.resolved_start_pts}, {self.resolved_end_pts})",
            )
        if self.has_discontinuity and not self.discontinuity_subdivided:
            raise_mega15_error(
                REFUSAL_PTS_DISCONTINUITY_UNRESOLVED,
                "TemporalPreparationRecord cannot persist an unresolved PTS discontinuity",
            )
        if not self.subdivided_segments:
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_EMPTY_SEGMENTS",
                "subdivided_segments must contain at least one half-open segment",
            )
        for seg_start, seg_end in self.subdivided_segments:
            if seg_end <= seg_start:
                raise_mega15_error(
                    "TEMPORAL_PREFLIGHT_INVALID_SEGMENT",
                    f"Segment [{seg_start}, {seg_end}) must satisfy seg_end > seg_start",
                )

        expected_digest = canonical_sha256(self._digest_payload())
        if self.record_digest != expected_digest:
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_DIGEST_MISMATCH",
                f"record_digest mismatch: expected {expected_digest}, got {self.record_digest}",
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "TemporalPreparationRecord":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_INVALID_PAYLOAD",
                "Payload must be a mapping",
            )
        raw_ctx = payload.get("synthetic_context")
        if not isinstance(raw_ctx, Mapping):
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_INVALID_SYNTHETIC_CONTEXT",
                "synthetic_context must be a mapping",
            )
        raw_segments = payload.get("subdivided_segments")
        if not isinstance(raw_segments, Sequence) or isinstance(raw_segments, (str, bytes)):
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_INVALID_SEGMENTS",
                "subdivided_segments must be a sequence",
            )
        segments: list[tuple[int, int]] = []
        for pair in raw_segments:
            if (
                not isinstance(pair, Sequence)
                or isinstance(pair, (str, bytes))
                or len(pair) != 2
            ):
                raise_mega15_error(
                    "TEMPORAL_PREFLIGHT_INVALID_SEGMENT_PAIR",
                    "Each segment must be a [start, end] pair",
                )
            segments.append((int(pair[0]), int(pair[1])))

        raw_ticks = payload.get("pts_ticks")
        if not isinstance(raw_ticks, Sequence) or isinstance(raw_ticks, (str, bytes)):
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_INVALID_PTS_TICKS",
                "pts_ticks must be a sequence of ints",
            )

        gate3_req = payload.get("gate3_refinement_request")
        if not isinstance(gate3_req, Mapping):
            raise_mega15_error(
                "TEMPORAL_PREFLIGHT_INVALID_GATE3_REQUEST",
                "gate3_refinement_request must be a mapping",
            )

        record = cls(
            schema_version=str(payload.get("schema_version", "")),
            kind=str(payload.get("kind", "")),
            record_id=str(payload.get("record_id", "")),
            upstream_request_id=str(payload.get("upstream_request_id", "")),
            upstream_request_digest=str(payload.get("upstream_request_digest", "")),
            queue_item_id=str(
                payload.get("queue_item_id", payload.get("candidate_item_id", ""))
            ),
            arm_id=str(payload.get("arm_id", "")),
            profile_id=str(payload.get("profile_id", "")),
            query_id=str(payload.get("query_id", "")),
            revision_id=str(
                payload.get("revision_id", payload.get("source_revision_id", ""))
            ),
            content_id=str(payload.get("content_id", "")),
            source_path=str(payload.get("source_path", "")),
            source_sha256=str(payload.get("source_sha256", "")),
            selected_stream_index=int(payload.get("selected_stream_index", 0)),
            stream_id=str(payload.get("stream_id", "")),
            timebase_num=int(
                payload.get("timebase_num", payload.get("source_timebase_num", 0))
            ),
            timebase_den=int(
                payload.get("timebase_den", payload.get("source_timebase_den", 0))
            ),
            pts_ticks=tuple(int(t) for t in raw_ticks),
            candidate_sample_pts=int(payload.get("candidate_sample_pts", 0)),
            requested_start_pts=int(payload.get("requested_start_pts", 0)),
            requested_end_pts=int(payload.get("requested_end_pts", 0)),
            start_occurrence=(
                None
                if payload.get("start_occurrence") is None
                else int(payload["start_occurrence"])
            ),
            end_occurrence=(
                None
                if payload.get("end_occurrence") is None
                else int(payload["end_occurrence"])
            ),
            resolved_start_pts=int(payload.get("resolved_start_pts", 0)),
            resolved_end_pts=int(payload.get("resolved_end_pts", 0)),
            start_snap_policy=str(payload.get("start_snap_policy", "")),
            end_snap_policy=str(payload.get("end_snap_policy", "")),
            endpoint_semantics=str(payload.get("endpoint_semantics", "")),
            is_vfr=bool(payload.get("is_vfr", False)),
            vfr_classification=str(payload.get("vfr_classification", "")),
            has_discontinuity=bool(payload.get("has_discontinuity", False)),
            discontinuity_subdivided=bool(payload.get("discontinuity_subdivided", False)),
            subdivided_segments=tuple(segments),
            gate3_refinement_request=dict(gate3_req),
            candidate_evidence_class=str(payload.get("candidate_evidence_class", "")),
            source_pts_evidence_state=str(payload.get("source_pts_evidence_state", "")),
            authoritative_source_measurement=bool(
                payload.get("authoritative_source_measurement", True)
            ),
            binding_eligible=bool(payload.get("binding_eligible", True)),
            synthetic_context=parse_synthetic_context_dict(raw_ctx),
            record_digest=str(payload.get("record_digest", "")),
        )
        record.validate()
        return record


def build_temporal_preparation_record(
    *,
    refinement_request: TemporalRefinementRequest,
    pts_diagnostic: PtsFixtureDiagnostic,
    start_occurrence: int | None = None,
    end_occurrence: int | None = None,
    allow_discontinuity_subdivision: bool = False,
    allow_terminal_tail_fallback: bool = False,
    declared_rate_num: int | None = None,
    declared_rate_den: int | None = None,
    seconds: float | int | None = None,
    nominal_fps: float | int | None = None,
    treat_candidate_as_exact_cut: bool = False,
    stream_id: str | None = None,
) -> TemporalPreparationRecord:
    """Build a verified synthetic Gate-3 temporal preflight record from MEGA-10 inputs."""
    refuse_nominal_fps_derivation(seconds=seconds, nominal_fps=nominal_fps)

    if not isinstance(refinement_request, TemporalRefinementRequest):
        raise_mega15_error(
            "TEMPORAL_PREFLIGHT_INVALID_REQUEST_TYPE",
            "refinement_request must be a TemporalRefinementRequest instance",
        )
    if not isinstance(pts_diagnostic, PtsFixtureDiagnostic):
        raise_mega15_error(
            "TEMPORAL_PREFLIGHT_INVALID_DIAGNOSTIC_TYPE",
            "pts_diagnostic must be a PtsFixtureDiagnostic instance",
        )

    # Enforce MEGA-15 authority & evidence refusal guards before generic schema verification
    if refinement_request.synthetic_only is not True:
        raise_mega15_error(
            REFUSAL_SYNTHETIC_TO_REAL_ESCALATION,
            "TemporalRefinementRequest.synthetic_only must be True",
        )
    refuse_semantic_candidate_as_cut(
        evidence_class=refinement_request.candidate_evidence_class,
        treat_as_exact_cut=treat_candidate_as_exact_cut,
    )
    if (
        refinement_request.source_pts_evidence_state != "NOT_OBSERVED"
        or refinement_request.measurement_needed is not True
    ):
        raise_mega15_error(
            REFUSAL_FORGED_SOURCE_MEASUREMENT,
            "TemporalRefinementRequest cannot claim measured source PTS evidence in offline preflight",
        )
    if refinement_request.binding_eligible is not False:
        raise_mega15_error(
            REFUSAL_BINDING_ELIGIBILITY_ESCALATION,
            "TemporalRefinementRequest cannot be binding_eligible in offline preflight",
        )
    if (
        pts_diagnostic.diagnostic_only is not True
        or pts_diagnostic.authoritative_source_measurement is not False
    ):
        raise_mega15_error(
            REFUSAL_FORGED_SOURCE_MEASUREMENT,
            "PtsFixtureDiagnostic must remain diagnostic_only=True and authoritative_source_measurement=False",
        )

    # Validate stream identity namespace
    if (
        not isinstance(refinement_request.selected_stream_index, int)
        or isinstance(refinement_request.selected_stream_index, bool)
        or refinement_request.selected_stream_index < 0
    ):
        raise_mega15_error(
            REFUSAL_STREAM_NAMESPACE_MISMATCH,
            f"selected_stream_index must be a non-negative integer, got {refinement_request.selected_stream_index!r}",
        )
    effective_stream_id = (
        stream_id
        if stream_id is not None
        else getattr(
            refinement_request,
            "stream_id",
            f"video:{refinement_request.selected_stream_index}",
        )
    )
    req_stream_idx = validate_video_stream_namespace(str(effective_stream_id))
    if req_stream_idx != refinement_request.selected_stream_index:
        raise_mega15_error(
            REFUSAL_STREAM_NAMESPACE_MISMATCH,
            f"Stream namespace index {req_stream_idx} != selected_stream_index {refinement_request.selected_stream_index}",
        )
    diag_stream_id = getattr(pts_diagnostic, "stream_id", None)
    if diag_stream_id is not None:
        diag_idx = validate_video_stream_namespace(str(diag_stream_id))
        if diag_idx != req_stream_idx:
            raise_mega15_error(
                REFUSAL_STREAM_NAMESPACE_MISMATCH,
                f"Diagnostic stream_id {diag_stream_id!r} != request stream_id {effective_stream_id!r}",
            )

    # Validate timebase consistency before generic schema check so timebase mismatches get specific code
    if (
        refinement_request.timebase_num != pts_diagnostic.timebase_num
        or refinement_request.timebase_den != pts_diagnostic.timebase_den
    ):
        raise_mega15_error(
            REFUSAL_TIMEBASE_MISMATCH,
            f"Timebase mismatch between request ({refinement_request.timebase_num}/{refinement_request.timebase_den}) "
            f"and diagnostic ({pts_diagnostic.timebase_num}/{pts_diagnostic.timebase_den})",
        )

    # Verify upstream MEGA-10 request payload & digest
    verify_temporal_refinement_request(refinement_request.to_dict())

    try:
        tb = TimeBase(
            num=int(refinement_request.timebase_num),
            den=int(refinement_request.timebase_den),
        )
    except Exception as exc:
        raise_mega15_error(
            REFUSAL_TIMEBASE_MISMATCH,
            f"Invalid rational timebase: {exc}",
        )

    pts_ticks = tuple(int(t) for t in pts_diagnostic.pts_ticks)
    try:
        table = PtsTable(time_base=tb, ticks=pts_ticks)
    except ValueError as exc:
        raise_mega15_error(
            REFUSAL_PTS_NON_MONOTONIC,
            f"Invalid PtsTable: {exc}",
        )

    req_start = int(refinement_request.requested_start_pts)
    req_end = int(refinement_request.requested_end_pts)

    start_snap: SnapResult = resolve_start(table, req_start)
    if start_snap.resolved_ticks is None:
        raise_mega15_error(
            REFUSAL_TERMINAL_TAIL_UNRESOLVED,
            f"Start tick {req_start} could not be resolved on PtsTable (policy={start_snap.policy})",
        )

    try:
        start_ord = table.ordinal_of(int(start_snap.resolved_ticks), occurrence=start_occurrence)
    except ValueError as exc:
        raise_mega15_error(
            REFUSAL_DUPLICATE_PTS_AMBIGUOUS,
            f"Start PTS resolution failed: {exc}",
        )
    if start_ord is None:
        raise_mega15_error(
            REFUSAL_DUPLICATE_PTS_AMBIGUOUS,
            f"Start PTS occurrence {start_occurrence!r} out of range for tick {start_snap.resolved_ticks}",
        )

    end_snap: SnapResult = resolve_end(table, req_end)
    if end_snap.resolved_ticks is None:
        if not allow_terminal_tail_fallback:
            raise_mega15_error(
                REFUSAL_TERMINAL_TAIL_UNRESOLVED,
                f"End tick {req_end} exceeds final PTS tick; explicit tail_end policy required",
            )
        last_delta = (pts_ticks[-1] - pts_ticks[-2]) if len(pts_ticks) >= 2 and pts_ticks[-1] > pts_ticks[-2] else 1
        te = tail_end(table, last_delta_ticks=last_delta, rate_regime="uniform")
        resolved_end = int(te.end_ticks) if te.end_ticks is not None else int(pts_ticks[-1] + last_delta)
        end_policy = "EXPLICIT_TAIL_END_FALLBACK"
    else:
        try:
            end_ord = table.ordinal_of(int(end_snap.resolved_ticks), occurrence=end_occurrence)
        except ValueError as exc:
            raise_mega15_error(
                REFUSAL_DUPLICATE_PTS_AMBIGUOUS,
                f"End PTS resolution failed: {exc}",
            )
        if end_ord is None:
            raise_mega15_error(
                REFUSAL_DUPLICATE_PTS_AMBIGUOUS,
                f"End PTS occurrence {end_occurrence!r} out of range for tick {end_snap.resolved_ticks}",
            )
        resolved_end = int(end_snap.resolved_ticks)
        end_policy = str(end_snap.policy)

    resolved_start = int(start_snap.resolved_ticks)
    start_policy = str(start_snap.policy)

    if resolved_end <= resolved_start:
        raise_mega15_error(
            "TEMPORAL_PREFLIGHT_EMPTY_RESOLVED_WINDOW",
            f"Resolved half-open window [{resolved_start}, {resolved_end}) is empty or inverted",
        )

    declared_rate = (
        Rational(int(declared_rate_num), int(declared_rate_den))
        if declared_rate_num is not None and declared_rate_den is not None
        else None
    )
    is_vfr_flag, _period_rat, _basis, _deviation = classify_vfr(table, declared_rate=declared_rate)
    is_vfr = str(is_vfr_flag) == "true"
    vfr_classification = "VFR" if is_vfr else "CFR"

    gaps = detect_discontinuity(table, resolved_start, resolved_end)
    has_discontinuity = len(gaps) > 0
    if has_discontinuity:
        if not allow_discontinuity_subdivision:
            raise_mega15_error(
                REFUSAL_PTS_DISCONTINUITY_UNRESOLVED,
                f"Unresolved PTS discontinuity detected in interval [{resolved_start}, {resolved_end}) "
                f"for request_id={refinement_request.request_id!r}",
            )
        parts_raw, _sub_gaps = subdivide_on_discontinuity(
            table, resolved_start, resolved_end
        )
        subdivided_segments = tuple((int(seg_s), int(seg_e)) for seg_s, seg_e in parts_raw)
        discontinuity_subdivided = True
    else:
        subdivided_segments = ((resolved_start, resolved_end),)
        discontinuity_subdivided = False

    # Construct canonical Gate-3 RefinementRequest contract (offline synthetic preflight only)
    gate3_req_obj = RefinementRequest(
        request_id=f"g3req_{refinement_request.request_id}",
        candidate_assertion_ref=refinement_request.queue_item_id,
        source_revision_id=refinement_request.revision_id,
        source_locator=refinement_request.source_path,
        expected_source_sha256=refinement_request.source_sha256,
        selected_stream_index=refinement_request.selected_stream_index,
        requested_start_pts=resolved_start,
        requested_end_pts=resolved_end,
        producer_attempt_id=f"attempt_{refinement_request.request_id}",
        idempotency_key=f"idem_{refinement_request.request_digest[:16]}",
        expected_timebase=(tb.num, tb.den),
    )
    gate3_req_dict = {
        "request_id": gate3_req_obj.request_id,
        "candidate_assertion_ref": gate3_req_obj.candidate_assertion_ref,
        "source_revision_id": gate3_req_obj.source_revision_id,
        "source_locator": gate3_req_obj.source_locator,
        "expected_source_sha256": gate3_req_obj.expected_source_sha256,
        "selected_stream_index": gate3_req_obj.selected_stream_index,
        "requested_start_pts": gate3_req_obj.requested_start_pts,
        "requested_end_pts": gate3_req_obj.requested_end_pts,
        "producer_attempt_id": gate3_req_obj.producer_attempt_id,
        "idempotency_key": gate3_req_obj.idempotency_key,
        "expected_timebase": (
            list(gate3_req_obj.expected_timebase)
            if gate3_req_obj.expected_timebase is not None
            else [tb.num, tb.den]
        ),
    }

    syn_ctx = make_synthetic_context()
    record_id = f"tprep_{refinement_request.request_id}"

    provisional = TemporalPreparationRecord(
        schema_version=TEMPORAL_PREFLIGHT_SCHEMA_VERSION,
        kind=TEMPORAL_PREFLIGHT_KIND,
        record_id=record_id,
        upstream_request_id=refinement_request.request_id,
        upstream_request_digest=refinement_request.request_digest,
        queue_item_id=refinement_request.queue_item_id,
        arm_id=refinement_request.arm_id,
        profile_id=refinement_request.profile_id,
        query_id=refinement_request.query_id,
        revision_id=refinement_request.revision_id,
        content_id=refinement_request.content_id,
        source_path=refinement_request.source_path,
        source_sha256=refinement_request.source_sha256,
        selected_stream_index=refinement_request.selected_stream_index,
        stream_id=str(effective_stream_id),
        timebase_num=tb.num,
        timebase_den=tb.den,
        pts_ticks=pts_ticks,
        candidate_sample_pts=int(refinement_request.candidate_sample_pts),
        requested_start_pts=req_start,
        requested_end_pts=req_end,
        start_occurrence=start_occurrence,
        end_occurrence=end_occurrence,
        resolved_start_pts=resolved_start,
        resolved_end_pts=resolved_end,
        start_snap_policy=start_policy,
        end_snap_policy=end_policy,
        endpoint_semantics="HALF_OPEN_START_INCLUSIVE_END_EXCLUSIVE",
        is_vfr=is_vfr,
        vfr_classification=vfr_classification,
        has_discontinuity=has_discontinuity,
        discontinuity_subdivided=discontinuity_subdivided,
        subdivided_segments=subdivided_segments,
        gate3_refinement_request=gate3_req_dict,
        candidate_evidence_class="MATCHED",
        source_pts_evidence_state="NOT_OBSERVED",
        authoritative_source_measurement=False,
        binding_eligible=False,
        synthetic_context=syn_ctx,
        record_digest="",
    )
    digest = canonical_sha256(provisional._digest_payload())
    final_record = TemporalPreparationRecord(
        **{**provisional.__dict__, "record_digest": digest}
    )
    final_record.validate()
    return final_record


def verify_temporal_preparation_record(
    record: TemporalPreparationRecord | Mapping[str, Any],
) -> TemporalPreparationRecord:
    """Verify and return a `TemporalPreparationRecord`."""
    if isinstance(record, TemporalPreparationRecord):
        record.validate()
        return record
    return TemporalPreparationRecord.from_dict(record)
