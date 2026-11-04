from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from gate3.pts import PtsTable, resolve_end, resolve_start
from gate3.rational import TimeBase
from gate3.refinement import is_binding_eligible
from gate3.refinement_request import RefinementRequest
from gate3.stream_identity import (
    REASON_BOUND_EVIDENCE_UNAVAILABLE,
    REASON_POSITIONAL_MISMATCH,
)
from gate3.temporal import (
    classify_vfr,
    detect_discontinuity,
    subdivide_on_discontinuity,
    tail_end,
)
from vip_lab.common import (
    NOT_OBSERVED,
    VipLabError,
    canonical_sha256,
    validate_hex_digest,
)
from vip_lab.mega10 import (
    PtsFixtureDiagnostic,
    TemporalRefinementRequest,
    verify_temporal_refinement_request,
)

REFUSAL_SOURCE_PTS_NOT_OBSERVED = "REFUSAL_SOURCE_PTS_NOT_OBSERVED"
REFUSAL_STREAM_NAMESPACE_UNPROVEN = "REFUSAL_STREAM_NAMESPACE_UNPROVEN"
REFUSAL_TERMINAL_TAIL_UNCERTAIN = "REFUSAL_TERMINAL_TAIL_UNCERTAIN"
REFUSAL_AMBIGUOUS_DUPLICATE_PTS = "REFUSAL_AMBIGUOUS_DUPLICATE_PTS"
REFUSAL_PTS_DISCONTINUITY = "REFUSAL_PTS_DISCONTINUITY"
REFUSAL_NOMINAL_FPS_FORBIDDEN = "REFUSAL_NOMINAL_FPS_FORBIDDEN"
REFUSAL_FORGED_MEASURED_PTS = "REFUSAL_FORGED_MEASURED_PTS"


def _parse_time_base_str(tb_str: str) -> TimeBase:
    if not isinstance(tb_str, str) or "/" not in tb_str:
        raise VipLabError(f"Invalid rational time_base string: {tb_str!r}")
    parts = tb_str.split("/")
    if len(parts) != 2:
        raise VipLabError(f"Invalid rational time_base string: {tb_str!r}")
    try:
        num = int(parts[0])
        den = int(parts[1])
    except ValueError as exc:
        raise VipLabError(f"Non-integer time_base components: {tb_str!r}") from exc
    if num <= 0 or den <= 0:
        raise VipLabError(f"time_base components must be positive: {tb_str!r}")
    return TimeBase(num, den)


def assert_no_nominal_fps_derivation(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, Mapping):
        raise VipLabError("Nominal FPS check requires a mapping payload.")
    forbidden_keys = {"nominal_fps", "fps_derivation", "seconds_times_fps", "frame_rate_float"}
    present = sorted(k for k in forbidden_keys if k in payload)
    if present:
        raise VipLabError(
            f"{REFUSAL_NOMINAL_FPS_FORBIDDEN}: forbidden nominal-FPS keys present: {present}"
        )
    derivation = str(payload.get("derivation", "")).lower()
    if "nominal_fps" in derivation or "seconds * fps" in derivation or "seconds*fps" in derivation:
        raise VipLabError(
            f"{REFUSAL_NOMINAL_FPS_FORBIDDEN}: seconds * nominal_fps derivation is prohibited."
        )


def assert_stream_namespace_separation(
    *,
    ffprobe_stream_index: int,
    iso_bmff_trak_ordinal: int | None = None,
    tkhd_track_id: int | None = None,
    probe_stream_id_hex: str | None = None,
    claim_equivalence_without_proof: bool = False,
) -> None:
    if isinstance(ffprobe_stream_index, bool) or not isinstance(ffprobe_stream_index, int) or ffprobe_stream_index < 0:
        raise VipLabError(
            f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: ffprobe_stream_index must be a non-negative int."
        )
    if claim_equivalence_without_proof:
        raise VipLabError(
            f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: cannot claim FFprobe stream index == ISO-BMFF trak ordinal without byte-bound P2 proof ({REASON_BOUND_EVIDENCE_UNAVAILABLE})."
        )
    if tkhd_track_id is not None:
        if isinstance(tkhd_track_id, bool) or not isinstance(tkhd_track_id, int):
            raise VipLabError(
                f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: tkhd_track_id must be an integer when provided."
            )
        if tkhd_track_id <= 0 or tkhd_track_id >= 0xFFFFFFFF:
            raise VipLabError(
                f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: unusable tkhd.track_ID={tkhd_track_id:#x}; 0 and 0xFFFFFFFF are refused per Gate-3 A-7."
            )
    if probe_stream_id_hex is not None:
        if not isinstance(probe_stream_id_hex, str) or not probe_stream_id_hex.startswith("0x"):
            raise VipLabError(
                f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: probe_stream_id_hex must be canonical 0x-prefixed hex."
            )
        try:
            parsed_probe_id = int(probe_stream_id_hex, 16)
        except ValueError as exc:
            raise VipLabError(
                f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: invalid hex in probe_stream_id_hex={probe_stream_id_hex!r}"
            ) from exc
        if parsed_probe_id <= 0 or parsed_probe_id >= 0xFFFFFFFF:
            raise VipLabError(
                f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: unusable probe stream id {probe_stream_id_hex!r}."
            )
        if tkhd_track_id is not None and parsed_probe_id != tkhd_track_id:
            raise VipLabError(
                f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: positional track_ID mismatch ({REASON_POSITIONAL_MISMATCH}): probe={probe_stream_id_hex} vs tkhd={tkhd_track_id:#x}."
            )
    if iso_bmff_trak_ordinal is not None and iso_bmff_trak_ordinal != ffprobe_stream_index:
        raise VipLabError(
            f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: ordinal displacement between ffprobe_stream_index={ffprobe_stream_index} and iso_bmff_trak_ordinal={iso_bmff_trak_ordinal} is unrepresentable in V1."
        )


@dataclass(frozen=True)
class StreamNamespacePreflight:
    preflight_id: str
    source_revision_id: str
    source_sha256: str
    ffprobe_stream_index: int
    iso_bmff_trak_ordinal: int | None
    tkhd_track_id: int | None
    probe_stream_id_hex: str | None
    stream_count: int
    namespace_equivalence_proven: bool
    status: str
    refusal_code: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "preflight_id": self.preflight_id,
            "source_revision_id": self.source_revision_id,
            "source_sha256": self.source_sha256,
            "ffprobe_stream_index": self.ffprobe_stream_index,
            "iso_bmff_trak_ordinal": self.iso_bmff_trak_ordinal,
            "tkhd_track_id": self.tkhd_track_id,
            "probe_stream_id_hex": self.probe_stream_id_hex,
            "stream_count": self.stream_count,
            "namespace_equivalence_proven": self.namespace_equivalence_proven,
            "status": self.status,
            "refusal_code": self.refusal_code,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> StreamNamespacePreflight:
        if not isinstance(payload, Mapping):
            raise VipLabError("StreamNamespacePreflight payload must be a mapping.")
        if payload.get("namespace_equivalence_proven") is not False:
            raise VipLabError(
                f"{REFUSAL_STREAM_NAMESPACE_UNPROVEN}: synthetic preflight cannot claim namespace_equivalence_proven=True."
            )
        return cls(
            preflight_id=str(payload["preflight_id"]),
            source_revision_id=str(payload["source_revision_id"]),
            source_sha256=validate_hex_digest(str(payload["source_sha256"]), field_name="source_sha256"),
            ffprobe_stream_index=int(payload["ffprobe_stream_index"]),
            iso_bmff_trak_ordinal=(
                int(payload["iso_bmff_trak_ordinal"])
                if payload.get("iso_bmff_trak_ordinal") is not None
                else None
            ),
            tkhd_track_id=(
                int(payload["tkhd_track_id"])
                if payload.get("tkhd_track_id") is not None
                else None
            ),
            probe_stream_id_hex=(
                str(payload["probe_stream_id_hex"])
                if payload.get("probe_stream_id_hex") is not None
                else None
            ),
            stream_count=int(payload["stream_count"]),
            namespace_equivalence_proven=False,
            status=str(payload["status"]),
            refusal_code=str(payload["refusal_code"]),
            reason=str(payload["reason"]),
        )


def evaluate_stream_namespace_preflight(
    *,
    source_revision_id: str,
    source_sha256: str,
    ffprobe_stream_index: int,
    iso_bmff_trak_ordinal: int | None = None,
    tkhd_track_id: int | None = None,
    probe_stream_id_hex: str | None = None,
    stream_count: int = 1,
    claim_equivalence_without_proof: bool = False,
) -> StreamNamespacePreflight:
    validate_hex_digest(source_sha256, field_name="source_sha256")
    if isinstance(stream_count, bool) or not isinstance(stream_count, int) or stream_count < 1:
        raise VipLabError("stream_count must be a positive integer.")

    assert_stream_namespace_separation(
        ffprobe_stream_index=ffprobe_stream_index,
        iso_bmff_trak_ordinal=iso_bmff_trak_ordinal,
        tkhd_track_id=tkhd_track_id,
        probe_stream_id_hex=probe_stream_id_hex,
        claim_equivalence_without_proof=claim_equivalence_without_proof,
    )

    status = (
        "REFUSED_MULTI_STREAM_NAMESPACE_UNPROVEN"
        if stream_count > 1
        else "DIAGNOSTIC_SINGLE_STREAM_SYNTHETIC_ONLY"
    )
    return StreamNamespacePreflight(
        preflight_id=f"ns_preflight_{source_revision_id}_{ffprobe_stream_index}",
        source_revision_id=source_revision_id,
        source_sha256=source_sha256,
        ffprobe_stream_index=ffprobe_stream_index,
        iso_bmff_trak_ordinal=iso_bmff_trak_ordinal,
        tkhd_track_id=tkhd_track_id,
        probe_stream_id_hex=probe_stream_id_hex,
        stream_count=stream_count,
        namespace_equivalence_proven=False,
        status=status,
        refusal_code=REFUSAL_STREAM_NAMESPACE_UNPROVEN,
        reason=REASON_BOUND_EVIDENCE_UNAVAILABLE,
    )


@dataclass(frozen=True)
class TerminalTailPreflight:
    requested_end_ticks: int
    last_observed_pts_ticks: int
    end_is_stream_tail: bool
    extent_state: str
    last_frame_extent: str
    tail_binding_eligible: bool
    it6_disposition_state: str
    refusal_code: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_end_ticks": self.requested_end_ticks,
            "last_observed_pts_ticks": self.last_observed_pts_ticks,
            "end_is_stream_tail": self.end_is_stream_tail,
            "extent_state": self.extent_state,
            "last_frame_extent": self.last_frame_extent,
            "tail_binding_eligible": self.tail_binding_eligible,
            "it6_disposition_state": self.it6_disposition_state,
            "refusal_code": self.refusal_code,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TerminalTailPreflight:
        if not isinstance(payload, Mapping):
            raise VipLabError("TerminalTailPreflight payload must be a mapping.")
        end_is_tail = bool(payload["end_is_stream_tail"])
        tail_eligible = bool(payload["tail_binding_eligible"])
        if tail_eligible:
            raise VipLabError(
                f"{REFUSAL_TERMINAL_TAIL_UNCERTAIN}: synthetic preflight cannot set tail_binding_eligible=True under IT-6 P3."
            )
        return cls(
            requested_end_ticks=int(payload["requested_end_ticks"]),
            last_observed_pts_ticks=int(payload["last_observed_pts_ticks"]),
            end_is_stream_tail=end_is_tail,
            extent_state=str(payload["extent_state"]),
            last_frame_extent=str(payload["last_frame_extent"]),
            tail_binding_eligible=False,
            it6_disposition_state=str(payload["it6_disposition_state"]),
            refusal_code=(
                str(payload["refusal_code"])
                if payload.get("refusal_code") is not None
                else None
            ),
        )


def evaluate_terminal_tail_preflight(
    *,
    pts_table: PtsTable,
    requested_end_ticks: int,
    container_facts: Mapping[str, Any] | None = None,
) -> TerminalTailPreflight:
    end_snap = resolve_end(pts_table, requested_end_ticks)
    last_pts = pts_table.ticks[-1]
    if end_snap.snapped_ticks is not None:
        return TerminalTailPreflight(
            requested_end_ticks=requested_end_ticks,
            last_observed_pts_ticks=last_pts,
            end_is_stream_tail=False,
            extent_state="OBSERVED_NEXT_TICK",
            last_frame_extent="OBSERVED",
            tail_binding_eligible=False,
            it6_disposition_state="PENDING_OWNER_DISPOSITION_P3_IN_FORCE",
            refusal_code=None,
        )

    tail_info = tail_end(
        pts_table,
        container_facts=dict(container_facts) if container_facts is not None else None,
    )
    return TerminalTailPreflight(
        requested_end_ticks=requested_end_ticks,
        last_observed_pts_ticks=last_pts,
        end_is_stream_tail=True,
        extent_state=tail_info.extent_state,
        last_frame_extent="UNCERTAIN",
        tail_binding_eligible=False,
        it6_disposition_state="PENDING_OWNER_DISPOSITION_P3_IN_FORCE",
        refusal_code=REFUSAL_TERMINAL_TAIL_UNCERTAIN,
    )


@dataclass(frozen=True)
class TemporalPreparationRecord:
    preparation_id: str
    refinement_request_id: str
    queue_item_id: str
    candidate_id: str
    query_id: str
    query_text: str
    arm_id: str
    source_id: str
    source_revision_id: str
    source_sha256: str
    source_path: str
    selected_stream_index: int
    time_base: str
    candidate_interval_ticks: tuple[int, int]
    resolved_start_ticks: int
    resolved_end_ticks: int
    vfr_classification: str
    discontinuity_detected: bool
    subdivided_segments: tuple[tuple[int, int], ...]
    stream_namespace_preflight: StreamNamespacePreflight
    terminal_tail_preflight: TerminalTailPreflight
    gate3_structurally_eligible: bool
    gate3_binding_eligible: bool
    source_pts_evidence_state: str
    candidate_evidence_class: str
    exact_cut_eligible: bool
    refusal_codes: tuple[str, ...]
    record_digest: str

    def _Body_without_digest(self) -> dict[str, Any]:
        return {
            "preparation_id": self.preparation_id,
            "refinement_request_id": self.refinement_request_id,
            "queue_item_id": self.queue_item_id,
            "candidate_id": self.candidate_id,
            "query_id": self.query_id,
            "query_text": self.query_text,
            "arm_id": self.arm_id,
            "source_id": self.source_id,
            "source_revision_id": self.source_revision_id,
            "source_sha256": self.source_sha256,
            "source_path": self.source_path,
            "selected_stream_index": self.selected_stream_index,
            "time_base": self.time_base,
            "candidate_interval_ticks": list(self.candidate_interval_ticks),
            "resolved_start_ticks": self.resolved_start_ticks,
            "resolved_end_ticks": self.resolved_end_ticks,
            "vfr_classification": self.vfr_classification,
            "discontinuity_detected": self.discontinuity_detected,
            "subdivided_segments": [list(seg) for seg in self.subdivided_segments],
            "stream_namespace_preflight": self.stream_namespace_preflight.to_dict(),
            "terminal_tail_preflight": self.terminal_tail_preflight.to_dict(),
            "gate3_structurally_eligible": self.gate3_structurally_eligible,
            "gate3_binding_eligible": self.gate3_binding_eligible,
            "source_pts_evidence_state": self.source_pts_evidence_state,
            "candidate_evidence_class": self.candidate_evidence_class,
            "exact_cut_eligible": self.exact_cut_eligible,
            "refusal_codes": list(self.refusal_codes),
        }

    def to_dict(self) -> dict[str, Any]:
        body = self._Body_without_digest()
        body["record_digest"] = self.record_digest
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TemporalPreparationRecord:
        if not isinstance(payload, Mapping):
            raise VipLabError("TemporalPreparationRecord payload must be a mapping.")
        assert_no_nominal_fps_derivation(payload)
        if payload.get("source_pts_evidence_state") != NOT_OBSERVED:
            raise VipLabError(
                f"{REFUSAL_FORGED_MEASURED_PTS}: source_pts_evidence_state must be {NOT_OBSERVED!r} in synthetic preparation, got {payload.get('source_pts_evidence_state')!r}."
            )
        if payload.get("gate3_binding_eligible") is not False:
            raise VipLabError(
                f"{REFUSAL_FORGED_MEASURED_PTS}: gate3_binding_eligible must be False in synthetic preparation."
            )
        if payload.get("exact_cut_eligible") is not False:
            raise VipLabError(
                f"{REFUSAL_FORGED_MEASURED_PTS}: exact_cut_eligible must be False in synthetic preparation."
            )
        cand_interval = payload["candidate_interval_ticks"]
        sub_segs = payload.get("subdivided_segments", [])
        record = cls(
            preparation_id=str(payload["preparation_id"]),
            refinement_request_id=str(payload["refinement_request_id"]),
            queue_item_id=str(payload["queue_item_id"]),
            candidate_id=str(payload["candidate_id"]),
            query_id=str(payload["query_id"]),
            query_text=str(payload["query_text"]),
            arm_id=str(payload["arm_id"]),
            source_id=str(payload["source_id"]),
            source_revision_id=str(payload["source_revision_id"]),
            source_sha256=validate_hex_digest(str(payload["source_sha256"]), field_name="source_sha256"),
            source_path=str(payload["source_path"]),
            selected_stream_index=int(payload["selected_stream_index"]),
            time_base=str(payload["time_base"]),
            candidate_interval_ticks=(int(cand_interval[0]), int(cand_interval[1])),
            resolved_start_ticks=int(payload["resolved_start_ticks"]),
            resolved_end_ticks=int(payload["resolved_end_ticks"]),
            vfr_classification=str(payload["vfr_classification"]),
            discontinuity_detected=bool(payload["discontinuity_detected"]),
            subdivided_segments=tuple((int(s[0]), int(s[1])) for s in sub_segs),
            stream_namespace_preflight=StreamNamespacePreflight.from_dict(
                payload["stream_namespace_preflight"]
            ),
            terminal_tail_preflight=TerminalTailPreflight.from_dict(
                payload["terminal_tail_preflight"]
            ),
            gate3_structurally_eligible=bool(payload["gate3_structurally_eligible"]),
            gate3_binding_eligible=False,
            source_pts_evidence_state=NOT_OBSERVED,
            candidate_evidence_class=str(payload["candidate_evidence_class"]),
            exact_cut_eligible=False,
            refusal_codes=tuple(str(c) for c in payload.get("refusal_codes", ())),
            record_digest=validate_hex_digest(str(payload["record_digest"]), field_name="record_digest"),
        )
        verify_temporal_preparation_record(record)
        return record


def build_temporal_preparation_record(
    *,
    refinement_request: TemporalRefinementRequest,
    pts_diagnostic: PtsFixtureDiagnostic,
    stream_count: int = 1,
    tkhd_track_id: int | None = None,
    probe_stream_id_hex: str | None = None,
    occurrence_index: int | None = None,
    allow_discontinuity_subdivision: bool = False,
) -> TemporalPreparationRecord:
    verify_temporal_refinement_request(refinement_request)

    if pts_diagnostic.request_id != refinement_request.request_id:
        raise VipLabError(
            f"pts_diagnostic.request_id ({pts_diagnostic.request_id!r}) != refinement_request.request_id ({refinement_request.request_id!r})"
        )
    if pts_diagnostic.source_revision_id != refinement_request.source_revision_id:
        raise VipLabError("source_revision_id mismatch between request and diagnostic.")
    if pts_diagnostic.selected_stream_index != refinement_request.selected_stream_index:
        raise VipLabError("selected_stream_index mismatch between request and diagnostic.")
    if pts_diagnostic.time_base != refinement_request.expected_timebase:
        raise VipLabError("time_base mismatch between request and diagnostic.")

    tb = _parse_time_base_str(refinement_request.expected_timebase)
    table = PtsTable(tb, pts_diagnostic.pts_ticks)

    req_start = refinement_request.requested_start_pts
    req_end = refinement_request.requested_end_pts

    start_snap = resolve_start(table, req_start)
    if start_snap.snapped_ticks is None:
        raise VipLabError(
            f"{REFUSAL_SOURCE_PTS_NOT_OBSERVED}: start tick {req_start} could not be snapped in PtsTable."
        )
    resolved_start = start_snap.snapped_ticks

    # Check duplicate PTS ambiguity on the resolved start tick
    if table.is_ambiguous(resolved_start):
        if occurrence_index is None:
            raise VipLabError(
                f"{REFUSAL_AMBIGUOUS_DUPLICATE_PTS}: duplicate PTS tick {resolved_start} is ambiguous without occurrence_index."
            )
        _ = table.ordinal_of(resolved_start, occurrence=occurrence_index)

    end_snap = resolve_end(table, req_end)
    tail_preflight = evaluate_terminal_tail_preflight(
        pts_table=table,
        requested_end_ticks=req_end,
        container_facts=None,
    )
    resolved_end = end_snap.snapped_ticks if end_snap.snapped_ticks is not None else req_end
    if resolved_end <= resolved_start:
        raise VipLabError(
            f"Resolved interval [{resolved_start}, {resolved_end}) is empty or inverted."
        )

    # Check VFR and discontinuity via gate3.temporal
    vfr_label, _, _, _ = classify_vfr(table)
    disc_list = detect_discontinuity(table, resolved_start, resolved_end)
    discontinuity_detected = len(disc_list) > 0
    if discontinuity_detected and not allow_discontinuity_subdivision:
        raise VipLabError(
            f"{REFUSAL_PTS_DISCONTINUITY}: PTS discontinuity detected in [{resolved_start}, {resolved_end}): {disc_list}"
        )
    subdivided = tuple(subdivide_on_discontinuity(table, resolved_start, resolved_end))

    # Validate structural RefinementRequest contract from gate3.refinement_request
    gate3_req = RefinementRequest(
        request_id=refinement_request.request_id,
        candidate_assertion_ref=refinement_request.candidate_id,
        source_revision_id=refinement_request.source_revision_id,
        source_locator=refinement_request.source_path,
        expected_source_sha256=refinement_request.expected_source_sha256,
        selected_stream_index=refinement_request.selected_stream_index,
        requested_start_pts=req_start,
        requested_end_pts=req_end,
        producer_attempt_id=refinement_request.producer_attempt_id,
        idempotency_key=refinement_request.idempotency_key,
        expected_timebase=(tb.num, tb.den),
    )
    structurally_eligible = bool(gate3_req.request_id) and (resolved_start < resolved_end)

    # Evaluate authoritative gate3.refinement.is_binding_eligible on synthetic preflight dict
    synthetic_refinement_probe = {
        "refinement_id": f"syn_ref_{refinement_request.request_id}",
        "source_revision_id": refinement_request.source_revision_id,
        "source_content_digest": refinement_request.expected_source_sha256,
        "stream_index": refinement_request.selected_stream_index,
        "time_base": [tb.num, tb.den],
        "time_domain": "source_pts",
        "start_ticks": resolved_start,
        "end_ticks": resolved_end,
        "evidence_state": NOT_OBSERVED,
        "blocked": REFUSAL_SOURCE_PTS_NOT_OBSERVED,
    }
    binding_eligible = bool(is_binding_eligible(synthetic_refinement_probe))
    if binding_eligible:
        raise VipLabError("Synthetic preflight record unexpectedly reported gate3_binding_eligible=True.")

    ns_preflight = evaluate_stream_namespace_preflight(
        source_revision_id=refinement_request.source_revision_id,
        source_sha256=refinement_request.expected_source_sha256,
        ffprobe_stream_index=refinement_request.selected_stream_index,
        iso_bmff_trak_ordinal=refinement_request.selected_stream_index,
        tkhd_track_id=tkhd_track_id,
        probe_stream_id_hex=probe_stream_id_hex,
        stream_count=stream_count,
    )

    refusal_codes: list[str] = [
        REFUSAL_SOURCE_PTS_NOT_OBSERVED,
        ns_preflight.refusal_code,
    ]
    if tail_preflight.refusal_code is not None:
        refusal_codes.append(tail_preflight.refusal_code)
    if discontinuity_detected:
        refusal_codes.append(REFUSAL_PTS_DISCONTINUITY)

    temp = TemporalPreparationRecord(
        preparation_id=f"tprep_{refinement_request.request_id}",
        refinement_request_id=refinement_request.request_id,
        queue_item_id=refinement_request.queue_item_id,
        candidate_id=refinement_request.candidate_id,
        query_id=refinement_request.query_id,
        query_text=refinement_request.query_text,
        arm_id=refinement_request.arm_id,
        source_id=refinement_request.source_id,
        source_revision_id=refinement_request.source_revision_id,
        source_sha256=refinement_request.expected_source_sha256,
        source_path=refinement_request.source_path,
        selected_stream_index=refinement_request.selected_stream_index,
        time_base=refinement_request.expected_timebase,
        candidate_interval_ticks=(req_start, req_end),
        resolved_start_ticks=resolved_start,
        resolved_end_ticks=resolved_end,
        vfr_classification=vfr_label,
        discontinuity_detected=discontinuity_detected,
        subdivided_segments=subdivided,
        stream_namespace_preflight=ns_preflight,
        terminal_tail_preflight=tail_preflight,
        gate3_structurally_eligible=structurally_eligible,
        gate3_binding_eligible=False,
        source_pts_evidence_state=NOT_OBSERVED,
        candidate_evidence_class="MATCHED",
        exact_cut_eligible=False,
        refusal_codes=tuple(refusal_codes),
        record_digest="0" * 64,
    )
    digest = canonical_sha256(temp._Body_without_digest())
    record = TemporalPreparationRecord(
        **{**temp.__dict__, "record_digest": digest}
    )
    verify_temporal_preparation_record(record)
    return record


def verify_temporal_preparation_record(record: TemporalPreparationRecord) -> None:
    if not isinstance(record, TemporalPreparationRecord):
        raise VipLabError("Expected TemporalPreparationRecord instance.")
    validate_hex_digest(record.source_sha256, field_name="source_sha256")
    validate_hex_digest(record.record_digest, field_name="record_digest")
    if record.source_pts_evidence_state != NOT_OBSERVED:
        raise VipLabError(
            f"{REFUSAL_FORGED_MEASURED_PTS}: source_pts_evidence_state must be {NOT_OBSERVED!r}."
        )
    if record.gate3_binding_eligible is not False:
        raise VipLabError(
            f"{REFUSAL_FORGED_MEASURED_PTS}: gate3_binding_eligible must be False."
        )
    if record.exact_cut_eligible is not False:
        raise VipLabError(
            f"{REFUSAL_FORGED_MEASURED_PTS}: exact_cut_eligible must be False."
        )
    if is_binding_eligible(record.to_dict()) is not False:
        raise VipLabError(
            f"{REFUSAL_FORGED_MEASURED_PTS}: gate3.refinement.is_binding_eligible must be False."
        )
    if record.candidate_evidence_class != "MATCHED":
        raise VipLabError("candidate_evidence_class must be 'MATCHED'.")
    if record.resolved_end_ticks <= record.resolved_start_ticks:
        raise VipLabError("resolved_end_ticks must be > resolved_start_ticks.")
    if REFUSAL_SOURCE_PTS_NOT_OBSERVED not in record.refusal_codes:
        raise VipLabError("TemporalPreparationRecord must include REFUSAL_SOURCE_PTS_NOT_OBSERVED.")
    expected_digest = canonical_sha256(record._Body_without_digest())
    if record.record_digest != expected_digest:
        raise VipLabError(
            f"TemporalPreparationRecord digest mismatch: expected {expected_digest}, got {record.record_digest}"
        )
