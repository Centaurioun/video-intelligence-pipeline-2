"""Independent, fail-closed verification for one local REAL preview.

This module intentionally does not import Gate-3 verifier/QC or execute tools.
It re-reads the bytes and reconciles the typed ``PreviewArtifact`` produced by
``LocalPreviewAdapter``.  The caller supplies the attempt identity because the
adapter is deliberately a media-only seam; orchestration binds this result to
its sealed authorization/receipt envelope.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ffprobe_frame_rows import (
    FfprobePayloadShapeError,
    normalized_frame_rows,
    normalized_packet_rows,
)
from .local_preview import PreviewArtifact


def _sha256(path: Path) -> tuple[int, str]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"LOCAL_ARTIFACT_UNREADABLE: {path}") from exc
    return len(payload), hashlib.sha256(payload).hexdigest()


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _timebase(value: Any) -> tuple[int, int]:
    if not isinstance(value, Mapping) or set(value) != {"num", "den"}:
        raise ValueError("TIMEBASE_INVALID")
    num, den = value["num"], value["den"]
    if (isinstance(num, bool) or not isinstance(num, int) or num <= 0
            or isinstance(den, bool) or not isinstance(den, int) or den <= 0):
        raise ValueError("TIMEBASE_INVALID")
    return num, den


def _authority_from_plan(plan_artifacts: Any, authorization: Any) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Return the pinned refinement and authorization preimage without producer observations."""
    if plan_artifacts is None or authorization is None:
        raise ValueError("SOURCE_AUTHORITY_REQUIRED")
    mapping = getattr(plan_artifacts, "mapping", None)
    plan = getattr(plan_artifacts, "plan", None)
    refinement_id = getattr(mapping, "source_refinement_id", None)
    refinements = getattr(plan, "pinned_refinements", None)
    refinement = refinements.get(refinement_id) if isinstance(refinements, Mapping) else None
    if not isinstance(refinement, Mapping):
        raise ValueError("REFINEMENT_AUTHORITY_MISSING")
    expected_revision = refinement.get("source_revision_id")
    if expected_revision != getattr(authorization, "source_revision_id", None):
        raise ValueError("SOURCE_REVISION_MISMATCH")
    if getattr(plan_artifacts, "plan_digest", None) != getattr(plan, "digest", None):
        raise ValueError("PLAN_DIGEST_MISMATCH")
    placement = getattr(plan_artifacts, "placement", None)
    if placement is None or _canonical_digest(placement.to_record()) != getattr(plan_artifacts, "placement_digest", None):
        raise ValueError("PLACEMENT_DIGEST_MISMATCH")
    mapping_record = mapping.to_record() if hasattr(mapping, "to_record") else None
    if mapping_record is None or mapping_record.get("record_digest") != getattr(plan_artifacts, "mapping_digest", None):
        raise ValueError("MAPPING_DIGEST_MISMATCH")
    if getattr(authorization, "plan_digest", None) != getattr(plan_artifacts, "plan_digest", None):
        raise ValueError("AUTHORIZATION_PLAN_MISMATCH")
    if getattr(authorization, "placement_digest", None) != getattr(plan_artifacts, "placement_digest", None):
        raise ValueError("AUTHORIZATION_PLACEMENT_MISMATCH")
    if getattr(authorization, "mapping_digest", None) != getattr(plan_artifacts, "mapping_digest", None):
        raise ValueError("AUTHORIZATION_MAPPING_MISMATCH")
    interval = refinement.get("source_pts_interval", {})
    if (getattr(mapping, "source_start_pts", None), getattr(mapping, "source_end_pts", None)) != (interval.get("start"), interval.get("end")):
        raise ValueError("MAPPING_INTERVAL_MISMATCH")
    compute = getattr(authorization, "compute_digest", None)
    if not callable(compute) or getattr(authorization, "record_digest", "") != compute():
        raise ValueError("AUTHORIZATION_DIGEST_MISMATCH")
    return refinement, {"source_revision_id": expected_revision,
                        "source_sha256": getattr(authorization, "source_sha256", None),
                        "plan_digest": getattr(plan_artifacts, "plan_digest", None),
                        "placement_digest": getattr(plan_artifacts, "placement_digest", None),
                        "mapping_digest": getattr(plan_artifacts, "mapping_digest", None),
                        "authorization_digest": getattr(authorization, "record_digest", None)}


def _evidence_facts(path: Path, expected_digest: str, selected_stream: int | None = None) -> tuple[Mapping[str, Any], tuple[int, ...]]:
    try:
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise ValueError("SOURCE_PTS_EVIDENCE_INVALID") from exc
    if hashlib.sha256(raw).hexdigest() != expected_digest:
        raise ValueError("EVIDENCE_DIGEST_MISMATCH")
    if not isinstance(payload, Mapping):
        raise ValueError("SOURCE_PTS_EVIDENCE_INVALID")
    values: list[int] = []
    def as_tick(value: Any) -> int | None:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return int(value.strip())
        return None
    if isinstance(payload.get("pts_ticks"), list):
        if selected_stream is not None and payload.get("stream_index") != selected_stream:
            raise ValueError("SOURCE_PTS_EVIDENCE_INVALID")
        values.extend(v for v in (as_tick(item) for item in payload["pts_ticks"]) if v is not None)
    try:
        row_groups = (
            (("best_effort_timestamp", "pts", "pkt_pts"), normalized_frame_rows(payload)),
            (("pts",), normalized_packet_rows(payload)),
        )
    except FfprobePayloadShapeError as exc:
        raise ValueError("SOURCE_PTS_EVIDENCE_INVALID") from exc
    for fields, rows in row_groups:
        for item in rows:
            # Root G §3.2(1): entries whose stream identity is absent are
            # excluded, never guessed.  The preview projection applies the same
            # rule, so render-admitted evidence stays verify-admissible.
            stream_index = item.get("stream_index")
            if stream_index is None:
                continue
            if selected_stream is not None and stream_index != selected_stream:
                continue
            # Root G §3.2(2)(3): the first valid presentation alias contributes
            # exactly one tick per row; aliases are not additive evidence.
            tick = next((value for value in (as_tick(item.get(field)) for field in fields)
                         if value is not None), None)
            if tick is not None:
                values.append(tick)
    # Root G §3.2(7): duplicate presentation ticks are preserved with their
    # multiplicity; a value set alone would destroy evidence.
    pts = tuple(sorted(values))
    if not pts:
        raise ValueError("SOURCE_PTS_EVIDENCE_INVALID")
    return payload, pts


def _probe_source(*, source: Path, executable: Path, runner: Any, selected_stream: int | None = None) -> tuple[int, str]:
    argv = [str(executable), "-v", "error", "-of", "json", "-show_streams", "-show_format", str(source)]
    try:
        result = runner(argv, shell=False, capture_output=True, check=False, timeout=60)
        if getattr(result, "returncode", 1) != 0:
            raise ValueError("SOURCE_PROBE_FAILED")
        payload = json.loads(getattr(result, "stdout", b"{}").decode("utf-8"))
        streams = [s for s in payload.get("streams", []) if s.get("codec_type") == "video"]
        if selected_stream is not None:
            streams = [s for s in streams if s.get("index") == selected_stream]
        if len(streams) != 1:
            raise ValueError("SOURCE_STREAM_AMBIGUOUS")
        return int(streams[0]["index"]), str(streams[0]["time_base"])
    except (OSError, subprocess.SubprocessError, TimeoutError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        if isinstance(exc, ValueError) and str(exc) in {"SOURCE_PROBE_FAILED", "SOURCE_STREAM_AMBIGUOUS"}:
            raise
        raise ValueError("SOURCE_PROBE_FAILED") from exc


@dataclass(frozen=True)
class PreviewVerification:
    status: str
    attempt_id: str
    source_sha256: str
    output_sha256: str
    source_byte_count: int
    output_byte_count: int
    artifact_id: str
    checks: tuple[dict[str, Any], ...]
    reason_codes: tuple[str, ...] = ()
    independent_of_producer: bool = True
    production_eligible: bool = False
    export_eligible: bool = False
    measured_output_streams: int | None = None
    measured_output_timebase: str | None = None
    measured_output_duration_ticks: int | None = None
    expected_output_duration_ticks: int | None = None

    def to_record(self) -> dict[str, Any]:
        return {
            "status": self.status, "attempt_id": self.attempt_id,
            "source_sha256": self.source_sha256, "output_sha256": self.output_sha256,
            "source_byte_count": self.source_byte_count, "output_byte_count": self.output_byte_count,
            "artifact_id": self.artifact_id, "checks": list(self.checks),
            "reason_codes": list(self.reason_codes), "independent_of_producer": self.independent_of_producer,
            "production_eligible": self.production_eligible, "export_eligible": self.export_eligible,
            "measured_output_streams": self.measured_output_streams,
            "measured_output_timebase": self.measured_output_timebase,
            "measured_output_duration_ticks": self.measured_output_duration_ticks,
            "expected_output_duration_ticks": self.expected_output_duration_ticks,
        }


def verify_preview(artifact: PreviewArtifact, *, source_path: str | Path,
                   attempt_id: str, expected_plan_digest: str | None = None,
                   expected_placement_digest: str | None = None,
                   expected_mapping_digest: str | None = None,
                   expected_authorization_digest: str | None = None,
                   expected_stream_index: int | None = None,
                   expected_timebase: tuple[int, int] | None = None,
                   measured_source_pts: Sequence[int] | None = None,
                   probe_runner: Any | None = None,
                   plan_artifacts: Any | None = None,
                   authorization: Any | None = None,
                   source_evidence_path: str | Path | None = None,
                   source_probe_runner: Any | None = None,
                   source_paths: Mapping[str, str | Path] | None = None,
                   strict_artifact_digests: bool = True) -> PreviewVerification:
    """Re-read and verify one preview; raise a stable refusal on any mismatch."""
    if not isinstance(artifact, PreviewArtifact):
        raise ValueError("ARTIFACT_TYPE_INVALID")
    if not isinstance(attempt_id, str) or not attempt_id.strip():
        raise ValueError("ATTEMPT_REQUIRED")
    if artifact.producer_attempt_id and artifact.producer_attempt_id == attempt_id:
        raise ValueError("ATTEMPT_MISMATCH")
    if artifact.schema_version == "v2":
        # V2 is a sealed multi-placement manifest. Re-derive its seal and
        # re-read every named source and the output before accepting it.
        if artifact.compute_digest() != artifact.record_digest:
            raise ValueError("ARTIFACT_DIGEST_MISMATCH")
        if plan_artifacts is None or authorization is None:
            raise ValueError("SEALED_V2_AUTHORITY_REQUIRED")
        if (getattr(plan_artifacts, "plan_digest", None) != getattr(plan_artifacts.plan, "digest", None)
                or artifact.plan_digest != plan_artifacts.plan_digest
                or authorization.plan_digest != plan_artifacts.plan_digest
                or authorization.compute_digest() != authorization.record_digest
                or artifact.authorization_digest != authorization.record_digest):
            raise ValueError("V2_AUTHORITY_DIGEST_MISMATCH")
        from .local_preview import (PreviewSourcePin, composition_digest,
                                    placement_set_digest, source_set_digest)
        placements = tuple(plan_artifacts.placements)
        mappings = tuple(plan_artifacts.mappings)
        if (not placements or len(placements) != len(mappings)
                or len(placements) != len(artifact.ordered_inputs)
                or tuple(item.get("order_index") for item in artifact.ordered_inputs) != tuple(range(len(placements)))):
            raise ValueError("ORDERED_LINEAGE_INVALID")
        placement_records = tuple({"order_index": i, "placement_digest": _canonical_digest(p.to_record()),
                                   "mapping_digest": m.record_digest}
                                  for i, (p, m) in enumerate(zip(placements, mappings)))
        if (placement_set_digest(plan_artifacts.plan_digest, placement_records) != artifact.placement_set_digest
                or artifact.placement_set_digest != authorization.placement_set_digest):
            raise ValueError("PLACEMENT_SET_DIGEST_MISMATCH")
        source_pins = tuple(PreviewSourcePin(item.get("source_revision_id"), item.get("source_sha256"),
                                             item.get("byte_count")) for item in artifact.ordered_inputs)
        if (source_set_digest(source_pins) != artifact.source_set_digest
                or artifact.source_set_digest != authorization.source_set_digest
                or tuple(source_pins) != tuple(authorization.ordered_source_pins)):
            raise ValueError("SOURCE_SET_DIGEST_MISMATCH")
        lineage = tuple(plan_artifacts.lineage)
        if (len(lineage) != len(placements)
                or tuple(x.order_index for x in lineage) != tuple(range(len(lineage)))
                or tuple(x.review_bundle_record_digest for x in lineage) != tuple(authorization.review_bundle_record_digests)
                or tuple(x.review_bundle_dependency_digest for x in lineage) != tuple(authorization.review_bundle_dependency_digests)
                or tuple(x.human_decision_record_digest for x in lineage) != tuple(authorization.human_decision_digests)):
            raise ValueError("ORDERED_REVIEW_DECISION_LINEAGE_MISMATCH")
        composition = []
        for i, (item, placement, mapping, pin) in enumerate(zip(artifact.ordered_inputs, placements, mappings, source_pins)):
            refinement_id = mapping.source_refinement_id
            refinement = plan_artifacts.plan.pinned_refinements.get(refinement_id)
            if (refinement is None or item.get("source_revision_id") != pin.source_revision_id
                    or item.get("source_pts_start") != refinement.get("source_pts_interval", {}).get("start")
                    or item.get("source_pts_end_exclusive") != refinement.get("source_pts_interval", {}).get("end")):
                raise ValueError("ORDERED_SOURCE_REFINEMENT_MISMATCH")
            tb = _timebase(refinement.get("timebase"))
            selected_stream = refinement.get("selected_stream_index")
            composition.append({"order_index": i, "placement_id": placement.placement_id,
                                "placement_digest": _canonical_digest(placement.to_record()),
                                "mapping_digest": mapping.record_digest,
                                "source_revision_id": pin.source_revision_id, "source_sha256": pin.source_sha256,
                                "stream_index": selected_stream, "source_timebase": {"num": tb[0], "den": tb[1]},
                                "source_pts_start": item["source_pts_start"],
                                "source_pts_end_exclusive": item["source_pts_end_exclusive"],
                                "timeline_start_ticks": placement.timeline_start_ticks,
                                "timeline_end_ticks": placement.timeline_end_ticks})
            evidence_ref = refinement.get("source_probe_artifact_ref") or refinement.get("evidence_artifact_ref")
            evidence_digest = refinement.get("source_probe_digest", refinement.get("evidence_digest", ""))
            if not evidence_ref:
                raise ValueError("SOURCE_PTS_EVIDENCE_REQUIRED")
            evidence, pts = _evidence_facts(Path(evidence_ref), evidence_digest, selected_stream)
            start, end = item["source_pts_start"], item["source_pts_end_exclusive"]
            following = [tick for tick in pts if tick > start]
            if start not in pts or not following or following[0] != end:
                raise ValueError("PTS_NOT_MEASURED")
            source_path_for_item = dict(source_paths or {}).get(pin.source_revision_id)
            if source_path_for_item is None and len(source_pins) == 1:
                source_path_for_item = source_path
            if source_path_for_item is None:
                raise ValueError("SOURCE_LINEAGE_UNRESOLVED")
            measured_stream, measured_tb = _probe_source(source=Path(source_path_for_item),
                executable=Path(artifact.ffprobe_tool.get("path", "ffprobe")),
                runner=source_probe_runner or probe_runner, selected_stream=selected_stream)
            if measured_stream != selected_stream or measured_tb != f"{tb[0]}/{tb[1]}":
                raise ValueError("SOURCE_STREAM_OR_TIMEBASE_MISMATCH")
        domain = placements[0].timeline_domain
        expected_composition = composition_digest(plan_artifacts.plan_digest,
            {"domain_id": domain.domain_id, "time_base": {"num": domain.time_base.num, "den": domain.time_base.den}},
            composition, authorization.audio_policy)
        if expected_composition != artifact.composition_digest or expected_composition != authorization.composition_digest:
            raise ValueError("COMPOSITION_DIGEST_MISMATCH")
        supplied_sources = dict(source_paths or {})
        if not supplied_sources and len(artifact.ordered_inputs) == 1:
            supplied_sources[artifact.ordered_inputs[0].get("source_revision_id", "")] = source_path
        if len(artifact.ordered_inputs) == 0:
            raise ValueError("ORDERED_LINEAGE_REQUIRED")
        indexes = [item.get("order_index") for item in artifact.ordered_inputs]
        if indexes != list(range(len(indexes))):
            raise ValueError("ORDERED_LINEAGE_INVALID")
        for item in artifact.ordered_inputs:
            revision = item.get("source_revision_id")
            path = supplied_sources.get(revision)
            if not revision or path is None:
                raise ValueError("SOURCE_LINEAGE_UNRESOLVED")
            nbytes, digest = _sha256(Path(path))
            if digest != item.get("source_sha256") or nbytes != item.get("byte_count"):
                raise ValueError("SOURCE_DIGEST_MISMATCH")
        expected_duration = sum(item.get("source_pts_end_exclusive", 0) - item.get("source_pts_start", 0)
                                for item in artifact.ordered_inputs)
        if (artifact.output_video_stream_count != 1
                or artifact.output_timebase_num <= 0 or artifact.output_timebase_den <= 0
                or artifact.output_duration_ticks != expected_duration):
            raise ValueError("OUTPUT_TIMING_MISMATCH")
        if strict_artifact_digests:
            for label, tool in (("FFPROBE", artifact.ffprobe_tool), ("FFMPEG", artifact.ffmpeg_tool)):
                if _sha256(Path(str(tool.get("path", ""))))[1] != tool.get("sha256"):
                    raise ValueError(f"{label}_TOOL_DIGEST_MISMATCH")
    for name, expected, actual in (
        ("PLAN_DIGEST_MISMATCH", expected_plan_digest, artifact.plan_digest),
        ("PLACEMENT_DIGEST_MISMATCH", expected_placement_digest, artifact.placement_digest),
        ("MAPPING_DIGEST_MISMATCH", expected_mapping_digest, artifact.mapping_digest),
        ("AUTHORIZATION_DIGEST_MISMATCH", expected_authorization_digest, artifact.authorization_digest),
    ):
        if expected is not None and expected != actual:
            raise ValueError(name)
    independent_pts: tuple[int, ...] | None = None
    if plan_artifacts is not None or authorization is not None:
        refinement, auth_values = _authority_from_plan(plan_artifacts, authorization)
        # The producer-returned artifact is untrusted.  Once sealed authority is
        # supplied, every digest in that artifact must be bound to the exact
        # plan/placement/mapping/authorization preimages re-derived above.
        for name, reason in (
            ("plan_digest", "PLAN_DIGEST_MISMATCH"),
            ("placement_digest", "PLACEMENT_DIGEST_MISMATCH"),
            ("mapping_digest", "MAPPING_DIGEST_MISMATCH"),
            ("authorization_digest", "AUTHORIZATION_DIGEST_MISMATCH"),
        ):
            actual = getattr(artifact, name, None)
            # The producer artifact is untrusted: once sealed authority is
            # available, malformed, missing, and substituted digests all fail
            # closed rather than being treated as legacy placeholders.
            if actual != auth_values[name]:
                raise ValueError(reason)
        if artifact.source_revision_id != refinement.get("source_revision_id"):
            raise ValueError("SOURCE_REVISION_MISMATCH")
        interval = refinement.get("source_pts_interval", {})
        tb = refinement.get("timebase", {})
        tb_num, tb_den = _timebase(tb)
        stream = refinement.get("selected_stream_index")
        if (artifact.source_start_pts, artifact.source_end_pts) != (interval.get("start"), interval.get("end")):
            raise ValueError("PTS_INTERVAL_MISMATCH")
        if (artifact.source_timebase_num, artifact.source_timebase_den) != (tb_num, tb_den):
            raise ValueError("TIMEBASE_MISMATCH")
        if not isinstance(source_evidence_path, (str, Path)):
            source_evidence_path = refinement.get("source_probe_artifact_ref") or refinement.get("evidence_artifact_ref")
        if not source_evidence_path:
            raise ValueError("SOURCE_PTS_EVIDENCE_REQUIRED")
        evidence, independent_pts = _evidence_facts(Path(source_evidence_path), refinement.get("source_probe_digest", refinement.get("evidence_digest", "")), stream)
        if evidence.get("source_bytes_sha256") and evidence.get("source_bytes_sha256") != auth_values["source_sha256"]:
            raise ValueError("SOURCE_DIGEST_MISMATCH")
        if evidence.get("stream_index") is not None and evidence.get("stream_index") != stream:
            raise ValueError("STREAM_MISMATCH")
        if evidence.get("media_timescale") is not None and evidence.get("media_timescale") != tb_den:
            raise ValueError("TIMEBASE_MISMATCH")
        source_probe_runner = source_probe_runner or probe_runner
        if source_probe_runner is None:
            raise ValueError("SOURCE_PROBE_REQUIRED")
        measured_stream, measured_timebase = _probe_source(source=Path(source_path), executable=Path(artifact.ffprobe_tool.get("path", "ffprobe")), runner=source_probe_runner, selected_stream=stream)
        if measured_stream != stream:
            raise ValueError("STREAM_MISMATCH")
        if artifact.selected_stream_index != measured_stream:
            raise ValueError("PRODUCER_STREAM_MISMATCH")
        if measured_timebase != f"{tb_num}/{tb_den}" :
            raise ValueError("TIMEBASE_MISMATCH")
        start, end = interval.get("start"), interval.get("end")
        if start not in independent_pts:
            raise ValueError("PTS_NOT_MEASURED")
        following = [value for value in independent_pts if value > start]
        if following:
            if end != following[0]:
                raise ValueError("PTS_NOT_MEASURED")
        else:
            # This FVS version admits only intervals with a strictly following
            # measured presentation PTS.  A terminal interval requires the
            # full Gate-3 duration_ts tail contract and is not accepted here.
            raise ValueError("STREAM_TAIL_NOT_SUPPORTED")
        if artifact.measured_source_pts and tuple(sorted(artifact.measured_source_pts)) != independent_pts:
            raise ValueError("PTS_NOT_MEASURED")
    elif expected_stream_index is not None and artifact.selected_stream_index != expected_stream_index:
        raise ValueError("STREAM_MISMATCH")
    elif expected_timebase is not None and (artifact.source_timebase_num, artifact.source_timebase_den) != expected_timebase:
        raise ValueError("TIMEBASE_MISMATCH")
    elif measured_source_pts is not None:
        pts = set(measured_source_pts)
        if artifact.source_start_pts not in pts or not any(value > artifact.source_start_pts for value in pts):
            raise ValueError("PTS_NOT_MEASURED")
    source = Path(source_path)
    output = artifact.output_path
    if source.resolve() == output.resolve():
        raise ValueError("SOURCE_OUTPUT_COLLISION")
    source_size, source_digest = _sha256(source)
    output_size, output_digest = _sha256(output)
    if artifact.schema_version == "v2" and (output_digest != artifact.output_sha256 or output_size != artifact.output_bytes):
        raise ValueError("OUTPUT_DIGEST_MISMATCH")
    if plan_artifacts is not None:
        for label, tool in (("ffprobe", artifact.ffprobe_tool), ("ffmpeg", artifact.ffmpeg_tool)):
            tool_path = Path(str(tool.get("path", "")))
            _, tool_digest = _sha256(tool_path)
            if tool_digest != tool.get("sha256"):
                raise ValueError(f"{label.upper()}_TOOL_DIGEST_MISMATCH")
        if auth_values.get("authorization_digest") and getattr(authorization, "ffprobe_tool_digest", "") != artifact.ffprobe_tool.get("sha256"):
            raise ValueError("FFPROBE_TOOL_BINDING_MISMATCH")
        if getattr(authorization, "ffmpeg_tool_digest", "") != artifact.ffmpeg_tool.get("sha256"):
            raise ValueError("FFMPEG_TOOL_BINDING_MISMATCH")
    if source_digest != artifact.source_sha256_before or source_digest != artifact.source_sha256_after:
        raise ValueError("SOURCE_DIGEST_MISMATCH")
    if plan_artifacts is not None and source_digest != auth_values["source_sha256"]:
        raise ValueError("SOURCE_DIGEST_MISMATCH")
    if source_size != artifact.source_byte_count_before or source_size != artifact.source_byte_count_after:
        raise ValueError("SOURCE_BYTE_COUNT_MISMATCH")
    if output_digest != artifact.output_sha256:
        raise ValueError("OUTPUT_DIGEST_MISMATCH")
    if output_size != artifact.output_bytes or output_size <= 0:
        raise ValueError("OUTPUT_BYTE_COUNT_MISMATCH")
    if artifact.production_eligible or artifact.export_eligible:
        raise ValueError("INVALID_SCOPE")
    if artifact.source_end_pts <= artifact.source_start_pts:
        raise ValueError("INVALID_TIMING_DOMAIN")
    if artifact.mapping_state not in {"MEASURED", "NOT_OBSERVED"}:
        raise ValueError("MAPPING_STATE_INVALID")
    measured_streams = None
    measured_timebase = None
    measured_duration_ticks = None
    expected_duration_ticks = (sum(item["source_pts_end_exclusive"] - item["source_pts_start"]
                                   for item in artifact.ordered_inputs)
                               if artifact.schema_version == "v2"
                               else artifact.source_end_pts - artifact.source_start_pts)
    if probe_runner is not None:
        probe = Path(artifact.ffprobe_tool.get("path", "ffprobe"))
        argv = [str(probe), "-v", "error", "-of", "json", "-show_streams", "-show_format", str(output)]
        try:
            result = probe_runner(argv, shell=False, capture_output=True, check=False, timeout=60)
            if getattr(result, "returncode", 1) != 0:
                raise ValueError("OUTPUT_PROBE_FAILED")
            payload = json.loads(getattr(result, "stdout", b"{}").decode("utf-8"))
            streams = [s for s in payload.get("streams", []) if s.get("codec_type") == "video"]
            measured_streams = len(streams)
            if measured_streams != 1:
                raise ValueError("OUTPUT_STREAM_AMBIGUOUS")
            measured_timebase = str(streams[0].get("time_base", ""))
            if measured_timebase != f"{artifact.source_timebase_num}/{artifact.source_timebase_den}":
                raise ValueError("OUTPUT_TIMEBASE_MISMATCH")
            duration_value = streams[0].get("duration_ts")
            if duration_value is None:
                raise ValueError("OUTPUT_TIMING_INVALID")
            try:
                measured_duration_ticks = int(duration_value)
            except (TypeError, ValueError) as exc:
                raise ValueError("OUTPUT_TIMING_INVALID") from exc
        except (OSError, subprocess.SubprocessError, TimeoutError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            if isinstance(exc, ValueError) and str(exc) in {"OUTPUT_STREAM_AMBIGUOUS", "OUTPUT_TIMEBASE_MISMATCH", "OUTPUT_TIMING_INVALID", "OUTPUT_PROBE_FAILED"}:
                raise
            raise ValueError("OUTPUT_PROBE_FAILED") from exc
    identity = hashlib.sha256(json.dumps({"attempt_id": attempt_id, "output": output_digest,
                                          "source": source_digest, "plan": artifact.plan_digest},
                                         sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    checks = ({"check": "source_digest", "result": "PASS"},
              {"check": "output_digest", "result": "PASS"},
              {"check": "source_output_distinct", "result": "PASS"},
              {"check": "nonproduction_scope", "result": "PASS"})
    return PreviewVerification("PASS", attempt_id, source_digest, output_digest, source_size,
                               output_size, identity, checks, measured_output_streams=measured_streams,
                               measured_output_timebase=measured_timebase,
                               measured_output_duration_ticks=measured_duration_ticks,
                               expected_output_duration_ticks=expected_duration_ticks)


verify_real_preview = verify_preview

__all__ = ["PreviewVerification", "verify_preview", "verify_real_preview"]
