"""Candidate ingress and byte-bound Gate-3 refinement for the FVS.

Retrieval metadata remains a non-binding MATCHED candidate. Only the named
source bytes' freshly measured PTS table can support a source-native refinement.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Any, Mapping

from gate3.refinement_request import RefinementRequest


@dataclass(frozen=True)
class RefinementResult:
    candidate: Mapping[str, Any]
    measured_refinement: Mapping[str, Any]
    binding_eligible: bool
    source_digest_before: str
    source_digest_after: str


class RefinementRefusal(ValueError):
    """Fail-closed refusal before a source can produce a binding refinement."""


def _get(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _sha256_regular_file(path: Path) -> str:
    """Hash a named regular file without following a final-component symlink."""
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise RefinementRefusal(f"named source is unavailable or a symlink: {path}") from exc
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise RefinementRefusal(f"named source is not a regular file: {path}")
        digest = hashlib.sha256()
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    finally:
        os.close(descriptor)


# Preserve the historical helper seam used by existing adapter regression tests.
_sha256 = _sha256_regular_file


def _candidate_record(
    hit: Any,
    request: RefinementRequest,
    source_digest: str,
) -> Mapping[str, Any]:
    """Retain candidate provenance while pinning its evidence as non-binding MATCHED."""
    incoming_revision = _get(hit, "source_revision_id")
    if incoming_revision is not None and incoming_revision != request.source_revision_id:
        raise RefinementRefusal("candidate source revision does not match refinement request")
    incoming_digest = _get(hit, "source_sha256", _get(hit, "source_content_digest"))
    if incoming_digest is not None and incoming_digest != request.expected_source_sha256:
        raise RefinementRefusal("candidate source digest does not match refinement request")
    incoming_path = _get(hit, "source_path")
    if incoming_path:
        try:
            if Path(incoming_path).resolve(strict=True) != Path(request.source_locator).resolve(strict=True):
                raise RefinementRefusal("candidate source locator does not match refinement request")
        except OSError as exc:
            raise RefinementRefusal("candidate source locator is unavailable") from exc

    timebase_num = _get(hit, "timebase_num", _get(hit, "time_base_num", 1))
    timebase_den = _get(hit, "timebase_den", _get(hit, "time_base_den", 1))
    raw = {
        "assertion_id": request.candidate_assertion_ref,
        "source_revision_id": request.source_revision_id,
        "interval_id": f"interval:{request.request_id}",
        "stream_index": request.selected_stream_index,
        "time_domain": "semantic_seconds",
        "origin_description": "semantic retrieval candidate; timing is non-binding",
        # Gate-3 A.1 requires integer endpoints even for a semantic candidate. These are
        # envelope placeholders only; the untouched retrieval claim is retained below.
        "start": 0,
        "end": 1,
        "endpoint_semantics": "half_open",
        "evidence_assertion_refs": [],
        "producer_attempt_id": request.producer_attempt_id,
        "evidence_class": "MATCHED",
        "producer_kind": "model",
        "invocation_ref": str(_get(hit, "invocation_ref", request.producer_attempt_id)),
        "precision": "semantic-window",
        "uncertainty": "unknown",
        "assertion_status": "ACTIVE",
        "refinement_eligibility": "NOT_ELIGIBLE",
        "binding_eligible": False,
        "time_base_or_rate": {"num": timebase_num, "den": timebase_den},
        "config_digest": str(_get(hit, "config_digest", "fvs-retrieval")),
        "source_content_digest": source_digest,
        "source_path": request.source_locator,
        "input_coverage": [],
        "method": {
            "method_kind": "model_scored",
            "tool": "persistent_local_index",
            "derivation": "semantic retrieval locator",
            "config_digest": str(_get(hit, "config_digest", "fvs-retrieval")),
        },
        "rank": _get(hit, "rank"),
        "score": _get(hit, "score"),
        "original_claim": dict(hit) if isinstance(hit, Mapping) else {
            key: getattr(hit, key)
            for key in ("pts", "timestamp_human", "rank", "score", "source_path")
            if hasattr(hit, key)
        },
    }
    for key in ("rank", "score"):
        if raw[key] is None:
            raw.pop(key)
    return raw


def _request_identity(request: RefinementRequest) -> dict[str, str]:
    payload = json.dumps(asdict(request), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {
        "request_id": request.request_id,
        "candidate_assertion_ref": request.candidate_assertion_ref,
        "producer_attempt_id": request.producer_attempt_id,
        "idempotency_key": request.idempotency_key,
        "request_digest": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "request": asdict(request),
    }


def refine_requested_candidate(
    request: RefinementRequest,
    candidate_provenance: Any,
    *,
    tool_identity: Mapping[str, Any] | None = None,
    declared_rate: Any = None,
    snapshot_evidence: Mapping[str, Any] | None = None,
    probe_artifact_path: str | Path | None = None,
    probe_digest: str | None = None,
) -> RefinementResult:
    """Measure and bind a request against the exact named source bytes."""
    if not isinstance(request, RefinementRequest):
        raise TypeError("request must be a RefinementRequest")

    from gate3 import container as container_module
    from gate3.container import parse_iso_bmff_timing
    from gate3.ingress import validate_candidate
    from gate3.pts import PtsTable
    from gate3.rational import TimeBase
    from gate3.refinement import refine, is_binding_eligible
    from gate3.stream_identity import StreamIdentityUnproven
    from vip_fvs.stream_identity_gate import require_bound_stream_identity

    path = Path(request.source_locator)
    source_digest_before = _sha256(path)
    if source_digest_before != request.expected_source_sha256:
        raise RefinementRefusal("named source digest does not match refinement request")

    candidate = _candidate_record(candidate_provenance, request, source_digest_before)
    validation = validate_candidate(candidate, stage_idempotency_key=request.idempotency_key)
    if validation.get("disposition") == "REJECTED":
        raise RefinementRefusal(
            "Gate-3 ingress rejected candidate: " + ",".join(validation.get("reason_codes", ()))
        )
    admitted = validation.get("record")
    if (
        not isinstance(admitted, Mapping)
        or admitted.get("evidence_class") != "MATCHED"
        or admitted.get("binding_eligible") is not False
    ):
        raise RefinementRefusal("semantic candidate must remain MATCHED and non-binding")

    try:
        measured = parse_iso_bmff_timing(path, selected_stream_index=request.selected_stream_index)
    except (OSError, ValueError) as exc:
        raise RefinementRefusal("named source timing could not be measured") from exc
    measured_digest = measured.get("source_bytes_sha256")
    if measured_digest is not None:
        if not isinstance(measured_digest, str) or measured_digest != request.expected_source_sha256:
            raise RefinementRefusal("measured source digest does not match refinement request")
    elif _sha256(path) != source_digest_before:
        # Older test seams omit the parser's byte digest. Require a stable named
        # file across that measurement boundary; production parsing supplies it.
        raise RefinementRefusal("source changed during refinement")
    # Explicit container ordinals require the integrated S2/S3 identity proof
    # before they can bind to the FFprobe stream namespace.
    explicit_ordinal = getattr(
        container_module,
        "EXPLICIT_SELECTION_DERIVATION",
        "explicitly_selected_trak_ordinal",
    )
    measured_stream_count = measured.get("stream_count")
    if (
        measured.get("stream_identity_derivation") == explicit_ordinal
        and isinstance(measured_stream_count, int)
        and not isinstance(measured_stream_count, bool)
        and measured_stream_count > 1
    ):
        try:
            identity = require_bound_stream_identity(
                container_path=request.source_locator,
                container_sha256=request.expected_source_sha256,
                probe_artifact_path=probe_artifact_path,
                probe_digest=probe_digest,
                selected_stream_index=request.selected_stream_index,
            )
        except StreamIdentityUnproven as exc:
            raise RefinementRefusal(
                f"stream identity is unproven: {exc.reason}"
            ) from exc
        if identity.state != "PROVEN":
            reason = identity.reason or "BOUND-EVIDENCE-UNAVAILABLE"
            raise RefinementRefusal(f"stream identity is unproven: {reason}")
    measured_stream = measured.get("stream_index")
    if (
        not isinstance(measured_stream, int)
        or isinstance(measured_stream, bool)
        or measured_stream != request.selected_stream_index
    ):
        raise RefinementRefusal("measured stream does not match requested stream")

    media_timescale = measured.get("media_timescale")
    if (
        not isinstance(media_timescale, int)
        or isinstance(media_timescale, bool)
        or media_timescale <= 0
    ):
        raise RefinementRefusal("measured media timebase is invalid")
    if request.expected_timebase is not None:
        expected_num, expected_den = request.expected_timebase
        if expected_num * media_timescale != expected_den:
            raise RefinementRefusal("declared expected timebase contradicts measured source timebase")

    measured_ticks = measured.get("pts_ticks")
    if not isinstance(measured_ticks, (tuple, list)) or any(
        not isinstance(tick, int) or isinstance(tick, bool) for tick in measured_ticks
    ):
        raise RefinementRefusal("measured source PTS table must contain exact integers")
    try:
        table = PtsTable(TimeBase(1, media_timescale), tuple(measured_ticks))
    except ValueError as exc:
        raise RefinementRefusal("measured source PTS table is invalid") from exc
    requested_pts = (request.requested_start_pts, request.requested_end_pts)
    if not table.is_boundary_member(request.requested_start_pts):
        raise RefinementRefusal("requested start endpoint is not a measured source PTS")

    refinement = refine(
        table,
        requested_pts,
        attempt_id=request.producer_attempt_id,
        tool_identity=dict(tool_identity or {"name": "gate3.refinement", "version": "pinned"}),
        time_domain="source_pts",
        precision="source-pts",
        retain_enumeration=True,
        source_revision_id=request.source_revision_id,
        source_content_digest=source_digest_before,
        stream_index=request.selected_stream_index,
        declared_rate=declared_rate,
        container_path=str(path),
        selected_stream_index=request.selected_stream_index,
        request_identity=_request_identity(request),
        snapshot_evidence=snapshot_evidence,
    )
    source_digest_after = _sha256(path)
    if source_digest_after != source_digest_before:
        raise RefinementRefusal("source changed during refinement")
    if not is_binding_eligible(refinement):
        raise RefinementRefusal(
            "Gate-3 refinement is not binding-eligible: "
            + str(refinement.get("blocked", "authority predicate refused"))
        )
    if refinement.get("evidence_class") != "MEASURED":
        raise RefinementRefusal("binding-eligible refinement lacks MEASURED evidence class")
    return RefinementResult(admitted, refinement, True, source_digest_before, source_digest_after)


def refine_retrieval_candidate(
    hit: Any,
    *,
    source_path: str | Path | None = None,
    source_revision_id: str,
    requested_pts: tuple[int, int],
    stream_index: int = 0,
    attempt_id: str = "fvs-refinement-attempt",
    stage_idempotency_key: str | None = None,
    tool_identity: Mapping[str, Any] | None = None,
    selected_stream_index: int | None = None,
    declared_rate: Any = None,
    snapshot_evidence: Mapping[str, Any] | None = None,
    probe_artifact_path: str | Path | None = None,
    probe_digest: str | None = None,
) -> RefinementResult:
    """Compatibility wrapper; all authority work goes through RefinementRequest."""
    path_value = source_path if source_path is not None else _get(hit, "source_path")
    if not path_value:
        raise RefinementRefusal("retrieval hit has no named source path")
    expected_digest = _get(hit, "source_sha256", _get(hit, "source_content_digest"))
    if not isinstance(expected_digest, str):
        raise RefinementRefusal("retrieval hit must carry an expected source digest")
    if selected_stream_index is not None and stream_index != selected_stream_index:
        raise RefinementRefusal("candidate stream does not match selected refinement stream")
    expected_timebase = None
    timebase_num = _get(hit, "timebase_num", _get(hit, "time_base_num"))
    timebase_den = _get(hit, "timebase_den", _get(hit, "time_base_den"))
    if timebase_num is not None or timebase_den is not None:
        if timebase_num is None or timebase_den is None:
            raise RefinementRefusal("candidate timebase declaration is incomplete")
        expected_timebase = (timebase_num, timebase_den)
    try:
        request = RefinementRequest(
            request_id=str(_get(hit, "request_id", f"request:{attempt_id}")),
            candidate_assertion_ref=str(_get(hit, "assertion_id", f"candidate:{attempt_id}")),
            source_revision_id=source_revision_id,
            source_locator=str(path_value),
            expected_source_sha256=expected_digest,
            selected_stream_index=stream_index,
            requested_start_pts=requested_pts[0],
            requested_end_pts=requested_pts[1],
            producer_attempt_id=attempt_id,
            idempotency_key=stage_idempotency_key or f"refinement:{attempt_id}",
            expected_timebase=expected_timebase,
        )
    except (TypeError, ValueError) as exc:
        raise RefinementRefusal(str(exc)) from exc
    return refine_requested_candidate(
        request, hit, tool_identity=tool_identity, declared_rate=declared_rate,
        snapshot_evidence=snapshot_evidence, probe_artifact_path=probe_artifact_path,
        probe_digest=probe_digest,
    )


# Short boundary name retained as a thin compatibility alias.
refine_candidate = refine_retrieval_candidate
