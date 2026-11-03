"""Authorization-gated local preview materialization for the REAL FVS path.

This is deliberately a small, non-production adapter.  It consumes a sealed
``RealPlanArtifacts`` value, invokes explicitly configured local tools through
an injected subprocess seam, and publishes a new preview file only after all
measurements and source-integrity checks have succeeded.  It never uses the
synthetic renderer and never grants export or production authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from .corpus_admission import (
    AdmissionBinding,
    CorpusAdmissionError,
    SyntheticPreflightContext,
    require_synthetic_preflight,
)
from .ffprobe_frame_rows import normalized_frame_rows, normalized_packet_rows
from .real_plan import (RealPlanArtifacts, RealPlanSelection,
                        rebind_real_plan_selections)
from .review_bundle import ReviewBundle
from .human_decision import HumanDecisionArtifact


class PreviewRefusal(RuntimeError):
    """Fail-closed refusal; the stable prefix is suitable for CLI/QC use."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _digest(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8"))


def canonical_digest(value: Any) -> str:
    """Return the canonical UTF-8 JSON SHA-256 used by aggregate v1 domains."""
    return _digest(value)


_DIGEST_RE = re.compile(r"[0-9a-f]{64}\Z")


def _require_digest(value: str, name: str) -> None:
    if not isinstance(value, str) or not _DIGEST_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")


@dataclass(frozen=True)
class PreviewSourcePin:
    source_revision_id: str
    source_sha256: str
    byte_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.source_revision_id, str) or not self.source_revision_id.strip():
            raise ValueError("source_revision_id is required")
        _require_digest(self.source_sha256, "source_sha256")
        if isinstance(self.byte_count, bool) or not isinstance(self.byte_count, int) or self.byte_count <= 0:
            raise ValueError("byte_count must be a positive integer")

    def to_record(self) -> dict[str, Any]:
        return {"source_revision_id": self.source_revision_id, "source_sha256": self.source_sha256,
                "byte_count": self.byte_count}


def placement_set_digest(plan_digest: str, placements: Any) -> str:
    _require_digest(plan_digest, "plan_digest")
    records = [dict(p) for p in placements]
    indexes = [p.get("order_index") for p in records]
    if any(isinstance(i, bool) or not isinstance(i, int) for i in indexes):
        raise ValueError("placement order_index must be an integer")
    if indexes != list(range(len(indexes))):
        raise ValueError("placement order indexes must be unique and contiguous")
    for item in records:
        _require_digest(item.get("placement_digest"), "placement_digest")
        _require_digest(item.get("mapping_digest"), "mapping_digest")
        if set(item) != {"order_index", "placement_digest", "mapping_digest"}:
            raise ValueError("placement set entry has unexpected fields")
    return _digest({"domain": "vip_fvs.preview-placement-set.v1", "plan_digest": plan_digest,
                    "placements": records})


def source_set_digest(sources: Any) -> str:
    records = [s.to_record() if isinstance(s, PreviewSourcePin) else dict(s) for s in sources]
    seen: set[str] = set()
    for item in records:
        pin = PreviewSourcePin(item.get("source_revision_id"), item.get("source_sha256"), item.get("byte_count"))
        if pin.source_revision_id in seen:
            raise ValueError("source revision ids must be unique")
        seen.add(pin.source_revision_id)
        if set(item) != {"source_revision_id", "source_sha256", "byte_count"}:
            raise ValueError("source set entry has unexpected fields")
    return _digest({"domain": "vip_fvs.preview-source-set.v1", "sources": records})


def composition_digest(plan_digest: str, timeline_domain: Mapping[str, Any], placements: Any,
                       audio_policy: str = "VIDEO_ONLY_DROP_AUDIO_V1") -> str:
    _require_digest(plan_digest, "plan_digest")
    if audio_policy != "VIDEO_ONLY_DROP_AUDIO_V1":
        raise ValueError("unsupported audio_policy")
    records = [dict(p) for p in placements]
    indexes = [p.get("order_index") for p in records]
    if any(isinstance(i, bool) or not isinstance(i, int) for i in indexes) or indexes != list(range(len(indexes))):
        raise ValueError("composition order indexes must be unique and contiguous")
    if not isinstance(timeline_domain, Mapping) or not timeline_domain.get("domain_id"):
        raise ValueError("timeline domain is required")
    time_base = timeline_domain.get("time_base")
    if not isinstance(time_base, Mapping) or any(isinstance(time_base.get(k), bool) or
            not isinstance(time_base.get(k), int) or time_base[k] <= 0 for k in ("num", "den")):
        raise ValueError("timeline time_base must contain positive integers")
    expected_fields = {"order_index", "placement_id", "placement_digest", "mapping_digest",
                       "source_revision_id", "source_sha256", "stream_index", "source_timebase",
                       "source_pts_start", "source_pts_end_exclusive", "timeline_start_ticks", "timeline_end_ticks"}
    prior_end = 0
    for item in records:
        if set(item) != expected_fields:
            raise ValueError("composition placement fields do not match v1 contract")
        if not isinstance(item["placement_id"], str) or not item["placement_id"].strip():
            raise ValueError("placement_id is required")
        _require_digest(item["placement_digest"], "placement_digest")
        _require_digest(item["mapping_digest"], "mapping_digest")
        _require_digest(item["source_sha256"], "source_sha256")
        if not isinstance(item["source_revision_id"], str) or not item["source_revision_id"].strip():
            raise ValueError("source_revision_id is required")
        tb = item["source_timebase"]
        if not isinstance(tb, Mapping) or any(isinstance(tb.get(k), bool) or not isinstance(tb.get(k), int)
                or tb[k] <= 0 for k in ("num", "den")):
            raise ValueError("source_timebase must contain positive integers")
        if isinstance(item["stream_index"], bool) or not isinstance(item["stream_index"], int) or item["stream_index"] < 0:
            raise ValueError("stream_index must be a nonnegative integer")
        ticks = (item["source_pts_start"], item["source_pts_end_exclusive"],
                 item["timeline_start_ticks"], item["timeline_end_ticks"])
        if any(isinstance(t, bool) or not isinstance(t, int) for t in ticks):
            raise ValueError("PTS and timeline ticks must be integers")
        source_start, source_end, timeline_start, timeline_end = ticks
        if source_end <= source_start or timeline_end - timeline_start != source_end - source_start:
            raise ValueError("composition interval lengths must match")
        if timeline_start != prior_end:
            raise ValueError("composition timeline must be contiguous")
        prior_end = timeline_end
    return _digest({"domain": "vip_fvs.preview-composition.v1", "plan_digest": plan_digest,
                    "timeline_domain": dict(timeline_domain), "audio_policy": audio_policy,
                    "placements": records})


def _refuse(reason: str, detail: str = "") -> PreviewRefusal:
    return PreviewRefusal(reason + ((": " + detail) if detail else ""))


def _local_path(value: str | os.PathLike[str], name: str) -> Path:
    raw = str(value)
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", raw) or "://" in raw:
        raise _refuse("LOCAL_SOURCE_REQUIRED", name)
    path = Path(value)
    if not path.is_absolute():
        raise _refuse("ABSOLUTE_PATH_REQUIRED", name)
    return path


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _tool_identity(path: Path, label: str) -> dict[str, Any]:
    if not path.is_absolute() or not path.is_file():
        raise _refuse("MISSING_TOOL_IDENTITY", label)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise _refuse("MISSING_TOOL_IDENTITY", str(exc)) from exc
    return {"path": str(path), "sha256": _sha(data), "version": "INJECTED_OR_NOT_OBSERVED"}


def tool_configuration_digest(probe_id: Mapping[str, Any], ffmpeg_id: Mapping[str, Any], *,
                              multi_placement: bool = False) -> str:
    """Digest the closed argv/configuration surface used by this adapter.

    Source, temporary-output, and measured PTS values are deliberately not
    included: those are request data, not authorization configuration.  Tool
    identity is included so an authorization cannot be replayed with the same
    options but a different executable.
    """
    value = {
        "network_allowed": False,
        "shell": False,
        "ffprobe": {
            "identity_sha256": probe_id["sha256"],
            "argv_options": ["-v", "error", "-of", "json", "-show_streams", "-show_format"],
        },
        "ffmpeg": {
            "temporary_output_policy": "private_nonexistent_child_v1",
            "identity_sha256": ffmpeg_id["sha256"],
            "argv_options": ["-v", "error", "-nostdin", "-i", "<source>", "-map", "0:<stream>",
                             "-copyts", "-vf", "trim=start_pts=<start_pts>:end_pts=<end_pts>,setpts=PTS-STARTPTS",
                             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                             "-pix_fmt", "yuv420p", "-fps_mode", "passthrough",
                             "-video_track_timescale", "<source_timebase_den>", "-an", "-f", "mp4",
                             "<temporary_output>"],
        },
    }
    if multi_placement:
        value["ffmpeg"]["multi_placement"] = {
            "segment_argv_options": ["-copyts", "-i", "<source>", "-map", "0:<stream>",
                                     "-vf", "trim=start_pts=<start_pts>:end_pts=<end_pts>,setpts=PTS-STARTPTS",
                                     "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                                     "-pix_fmt", "yuv420p", "-fps_mode", "passthrough",
                                     "-video_track_timescale", "<timeline_timebase_den>", "-an", "-f", "mp4"],
            "concat_argv_options": ["-f", "concat", "-safe", "0", "-i", "<private_manifest>",
                                    "-c", "copy", "-video_track_timescale", "<timeline_timebase_den>",
                                    "-an", "-f", "mp4"],
            "concatenation": "private_manifest_concat_demuxer_stream_copy_v1",
            "network_allowed": False, "shell": False,
        }
    return _digest(value)


@dataclass(frozen=True)
class PreviewAuthorization:
    """Closed, digest-bound authorization for one non-production preview."""

    authorization_id: str
    policy_identity: str
    scope: str
    plan_digest: str
    source_revision_id: str
    source_sha256: str
    placement_digest: str
    mapping_digest: str
    output_root: Path
    issued_at: str = ""
    expires_at: str | None = None
    revoked: bool = False
    production_eligible: bool = False
    export_eligible: bool = False
    timeout_seconds: float = 60.0
    max_output_bytes: int = 100_000_000
    ffprobe_tool_digest: str = ""
    ffmpeg_tool_digest: str = ""
    tool_config_digest: str = ""
    review_bundle_record_digest: str = ""
    review_bundle_dependency_digest: str = ""
    human_decision_digest: str = ""
    review_bundle_ref: str = ""
    decision_ref: str = ""
    record_digest: str = field(default="")
    schema_version: str = "v1"
    placement_set_digest: str = ""
    source_set_digest: str = ""
    composition_digest: str = ""
    ordered_source_pins: tuple[PreviewSourcePin, ...] = ()
    review_bundle_record_digests: tuple[str, ...] = ()
    review_bundle_dependency_digests: tuple[str, ...] = ()
    human_decision_digests: tuple[str, ...] = ()
    audio_policy: str = "VIDEO_ONLY_DROP_AUDIO_V1"

    def __post_init__(self) -> None:
        if not self.authorization_id.strip() or not self.policy_identity.strip():
            raise ValueError("authorization identity is required")
        if self.scope != "NON_PRODUCTION_PREVIEW":
            raise ValueError("authorization scope must be NON_PRODUCTION_PREVIEW")
        if self.schema_version not in {"v1", "v2"}:
            raise ValueError("unsupported authorization schema_version")
        legacy_names = ("plan_digest", "source_sha256", "placement_digest", "mapping_digest")
        for name in (legacy_names if self.schema_version == "v1" else ("plan_digest",)):
            value = getattr(self, name)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError(f"{name} must be a SHA-256 digest")
        for name in ("ffprobe_tool_digest", "ffmpeg_tool_digest", "tool_config_digest"):
            value = getattr(self, name)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError(f"{name} must be a SHA-256 digest")
        for name in ("review_bundle_record_digest", "review_bundle_dependency_digest", "human_decision_digest"):
            value = getattr(self, name)
            if value and (not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)):
                raise ValueError(f"{name} must be a SHA-256 digest when provided")
        if self.production_eligible or self.export_eligible:
            raise ValueError("preview authorization cannot grant production/export authority")
        if not isinstance(self.output_root, Path) or not self.output_root.is_absolute():
            raise ValueError("output_root must be an absolute Path")
        if (not isinstance(self.max_output_bytes, int) or isinstance(self.max_output_bytes, bool)
                or self.timeout_seconds <= 0 or self.max_output_bytes <= 0):
            raise ValueError("preview limits must be positive")
        if not math.isfinite(self.timeout_seconds):
            raise ValueError("preview timeout must be finite")
        if self.schema_version == "v2":
            for name in ("placement_set_digest", "source_set_digest", "composition_digest"):
                _require_digest(getattr(self, name), name)
            if self.audio_policy != "VIDEO_ONLY_DROP_AUDIO_V1":
                raise ValueError("unsupported audio_policy")
            if not self.ordered_source_pins:
                raise ValueError("v2 authorization requires ordered_source_pins")
            if source_set_digest(self.ordered_source_pins) != self.source_set_digest:
                raise ValueError("source_set_digest does not match ordered_source_pins")
            for name, pins in (("review_bundle_record_digests", self.review_bundle_record_digests),
                               ("review_bundle_dependency_digests", self.review_bundle_dependency_digests),
                               ("human_decision_digests", self.human_decision_digests)):
                if not pins:
                    raise ValueError(f"{name} must not be empty")
                for value in pins:
                    _require_digest(value, name)
            if not (len(self.review_bundle_record_digests) == len(self.review_bundle_dependency_digests) ==
                    len(self.human_decision_digests)):
                raise ValueError("ordered per-placement authorization pin cardinality mismatch")
            if str(self.output_root) != os.path.realpath(self.output_root):
                raise ValueError("v2 output_root must be canonical absolute path")
        expected = self.compute_digest()
        if self.record_digest and self.record_digest != expected:
            raise ValueError("authorization digest mismatch")
        object.__setattr__(self, "record_digest", expected)

    def _preimage(self) -> dict[str, Any]:
        return {"authorization_id": self.authorization_id, "policy_identity": self.policy_identity,
                "scope": self.scope, "plan_digest": self.plan_digest,
                "source_revision_id": self.source_revision_id, "source_sha256": self.source_sha256,
                "placement_digest": self.placement_digest, "mapping_digest": self.mapping_digest,
                "output_root": str(self.output_root), "issued_at": self.issued_at,
                "expires_at": self.expires_at, "revoked": self.revoked,
                "production_eligible": self.production_eligible, "export_eligible": self.export_eligible,
                "timeout_seconds": self.timeout_seconds, "max_output_bytes": self.max_output_bytes,
                "ffprobe_tool_digest": self.ffprobe_tool_digest,
                "ffmpeg_tool_digest": self.ffmpeg_tool_digest,
                "tool_config_digest": self.tool_config_digest,
                "review_bundle_record_digest": self.review_bundle_record_digest,
                "review_bundle_dependency_digest": self.review_bundle_dependency_digest,
                "human_decision_digest": self.human_decision_digest,
                "review_bundle_ref": self.review_bundle_ref,
                "decision_ref": self.decision_ref}

    def compute_digest(self) -> str:
        legacy = self._preimage()
        if self.schema_version == "v1":
            # Deliberately retain the historical v1 preimage with no schema tag.
            return _digest(legacy)
        extension = {
            "domain": "vip_fvs.preview-authorization.v2",
            "legacy_authorization_preimage": legacy,
            "placement_set_digest": self.placement_set_digest,
            "source_set_digest": self.source_set_digest,
            "composition_digest": self.composition_digest,
            "ffprobe_tool_digest": self.ffprobe_tool_digest,
            "ffmpeg_tool_digest": self.ffmpeg_tool_digest,
            "tool_config_digest": self.tool_config_digest,
            "review_bundle_record_digests": list(self.review_bundle_record_digests),
            "review_bundle_dependency_digests": list(self.review_bundle_dependency_digests),
            "human_decision_digests": list(self.human_decision_digests),
            "timeout_seconds": self.timeout_seconds, "max_output_bytes": self.max_output_bytes,
            "output_root": str(self.output_root), "scope": self.scope,
            "production_eligible": self.production_eligible, "export_eligible": self.export_eligible,
            "source_pins": [p.to_record() for p in self.ordered_source_pins],
            "audio_policy": self.audio_policy,
        }
        return _digest(extension)


@dataclass(frozen=True)
class PreviewArtifact:
    output_path: Path
    output_bytes: int
    output_sha256: str
    source_sha256_before: str
    source_sha256_after: str
    source_byte_count_before: int
    source_byte_count_after: int
    source_revision_id: str
    selected_stream_index: int
    source_timebase_num: int
    source_timebase_den: int
    source_start_pts: int
    source_end_pts: int
    plan_digest: str
    placement_digest: str
    mapping_digest: str
    authorization_digest: str
    ffprobe_argv: tuple[str, ...]
    ffmpeg_argv: tuple[str, ...]
    ffprobe_tool: Mapping[str, Any]
    ffmpeg_tool: Mapping[str, Any]
    production_eligible: bool = False
    export_eligible: bool = False
    mapping_state: str = "NOT_OBSERVED"
    producer_attempt_id: str = ""
    measured_source_pts: tuple[int, ...] = ()
    schema_version: str = "v1"
    ordered_inputs: tuple[Mapping[str, Any], ...] = ()
    placement_set_digest: str = ""
    source_set_digest: str = ""
    composition_digest: str = ""
    tool_config_digest: str = ""
    ffprobe_argv_digest: str = ""
    ffmpeg_argv_digest: str = ""
    output_video_stream_count: int | None = None
    output_timebase_num: int | None = None
    output_timebase_den: int | None = None
    output_duration_ticks: int | None = None
    record_digest: str = ""

    def __post_init__(self) -> None:
        if self.schema_version not in {"v1", "v2"}:
            raise ValueError("unsupported artifact schema_version")
        if self.schema_version == "v2":
            for name in ("authorization_digest", "plan_digest", "placement_set_digest", "source_set_digest",
                         "composition_digest", "tool_config_digest", "ffprobe_argv_digest", "ffmpeg_argv_digest",
                         "output_sha256"):
                _require_digest(getattr(self, name), name)
            if not self.ordered_inputs:
                raise ValueError("v2 artifact requires ordered_inputs")
            if self.production_eligible or self.export_eligible:
                raise ValueError("preview artifact cannot grant production/export authority")
            _require_digest(self.ffprobe_tool.get("sha256"), "ffprobe_tool_digest")
            _require_digest(self.ffmpeg_tool.get("sha256"), "ffmpeg_tool_digest")
            if self.output_bytes <= 0 or self.output_video_stream_count is None or self.output_timebase_num is None or self.output_timebase_den is None or self.output_duration_ticks is None:
                raise ValueError("v2 artifact requires measured output type fields")
            for name in ("output_bytes", "output_video_stream_count", "output_timebase_num",
                         "output_timebase_den", "output_duration_ticks"):
                if type(getattr(self, name)) is not int:
                    raise ValueError(f"{name} must be an integer")
            if self.output_video_stream_count != 1 or min(self.output_timebase_num, self.output_timebase_den,
                                                          self.output_duration_ticks) <= 0:
                raise ValueError("invalid v2 measured output fields")
            expected = self.compute_digest()
            if self.record_digest and self.record_digest != expected:
                raise ValueError("artifact digest mismatch")
            object.__setattr__(self, "record_digest", expected)

    def _manifest_preimage(self) -> dict[str, Any]:
        if self.schema_version != "v2":
            raise ValueError("manifest digest is available only for v2 artifacts")
        return {
            "domain": "vip_fvs.preview-artifact.v2",
            "authorization_digest": self.authorization_digest,
            "plan_digest": self.plan_digest,
            "placement_set_digest": self.placement_set_digest,
            "source_set_digest": self.source_set_digest,
            "composition_digest": self.composition_digest,
            "ordered_inputs": [dict(item) for item in self.ordered_inputs],
            "ffprobe_tool_digest": self.ffprobe_tool["sha256"],
            "ffmpeg_tool_digest": self.ffmpeg_tool["sha256"],
            "tool_config_digest": self.tool_config_digest,
            "ffprobe_argv_digest": self.ffprobe_argv_digest,
            "ffmpeg_argv_digest": self.ffmpeg_argv_digest,
            "output": {"sha256": self.output_sha256, "byte_count": self.output_bytes,
                       "video_stream_count": self.output_video_stream_count,
                       "time_base": {"num": self.output_timebase_num, "den": self.output_timebase_den},
                       "duration_ticks": self.output_duration_ticks},
            "production_eligible": self.production_eligible,
            "export_eligible": self.export_eligible,
        }

    def compute_digest(self) -> str:
        return _digest(self._manifest_preimage())


def _completed(result: Any) -> tuple[int, bytes, bytes]:
    code = getattr(result, "returncode", 1)
    stdout = getattr(result, "stdout", b"")
    stderr = getattr(result, "stderr", b"")
    if isinstance(stdout, str):
        stdout = stdout.encode()
    if isinstance(stderr, str):
        stderr = stderr.encode()
    return (int(code), stdout if isinstance(stdout, bytes) else b"",
            stderr if isinstance(stderr, bytes) else b"")


def _failure_detail(code: int, stderr: bytes, *, limit: int = 512) -> str:
    """Return bounded, stable subprocess detail without publishing raw output."""
    excerpt = stderr.decode("utf-8", errors="replace")[:limit].replace("\n", "\\n")
    digest = _sha(stderr)
    return f"returncode={code}; stderr_sha256={digest}; stderr_excerpt={excerpt}"


def _exception_detail(exc: BaseException, *, limit: int = 256) -> str:
    """Bound exception text so injected/runtime failures cannot leak unbounded data."""
    return f"exception={type(exc).__name__}; detail={str(exc)[:limit]}"


def _render_failure_detail(code: int, stderr: bytes, temp: Path,
                           ffmpeg_argv: tuple[str, ...]) -> str:
    """Capture bounded subprocess and staging state before cleanup."""
    try:
        exists = temp.is_file()
        size = temp.stat().st_size if exists else 0
    except OSError:
        exists, size = False, 0
    return (f"{_failure_detail(code, stderr)}; temp_exists={exists}; temp_bytes={size}; "
            f"ffmpeg_argv_sha256={_digest(list(ffmpeg_argv))}")


class LocalPreviewAdapter:
    """Materialize one bounded, local-only preview with injected tools."""

    def __init__(self, *, runner: Callable[..., Any] | None = None):
        self.runner = runner or subprocess.run

    def render_plan_preview(self, artifacts: RealPlanArtifacts, *, authorization: PreviewAuthorization,
                            source_paths: Mapping[str, str | os.PathLike[str]],
                            selections: tuple[RealPlanSelection, ...] | list[RealPlanSelection] | None = None,
                            output_root: str | os.PathLike[str],
                            ffprobe_executable: str | os.PathLike[str],
                            ffmpeg_executable: str | os.PathLike[str],
                            timeout_seconds: float | None = None,
                            producer_attempt_id: str = "") -> PreviewArtifact:
        """Preview an accepted successor plan through the existing bounded renderer.

        This entry point deliberately admits a one-placement successor only.  Its
        source is selected by the exact pinned revision id, then all existing
        authorization, byte-integrity, tool, staging, and output-measurement
        checks remain in force.
        """
        if not isinstance(artifacts, RealPlanArtifacts):
            raise _refuse("MISSING_AUTHORIZATION")
        if not isinstance(authorization, PreviewAuthorization):
            raise _refuse("MISSING_AUTHORIZATION")
        if artifacts.plan.plan_revision < 2:
            raise _refuse("PLAN_REVISION_REQUIRED")
        placements = artifacts.placements or (artifacts.placement,)
        mappings = artifacts.mappings or (artifacts.mapping,)
        if len(placements) != 1 or len(mappings) != 1:
            if authorization.schema_version != "v2" or selections is None:
                raise _refuse("UNSUPPORTED_PLAN_LAYOUT", "multi-placement requires v2 authorization and sealed selections")
            return self._render_multi_plan_preview(
                artifacts, authorization=authorization, source_paths=source_paths, selections=selections,
                output_root=output_root, ffprobe_executable=ffprobe_executable,
                ffmpeg_executable=ffmpeg_executable, timeout_seconds=timeout_seconds,
                producer_attempt_id=producer_attempt_id)
        revision_id = artifacts.plan.pinned_refinements[mappings[0].source_refinement_id]["source_revision_id"]
        source = source_paths.get(revision_id)
        if source is None:
            raise _refuse("SOURCE_REVISION_REQUIRED", revision_id)
        return self.render_preview(
            artifacts, authorization=authorization, source_path=source,
            output_root=output_root, ffprobe_executable=ffprobe_executable,
            ffmpeg_executable=ffmpeg_executable, timeout_seconds=timeout_seconds,
            producer_attempt_id=producer_attempt_id,
        )

    def _render_multi_plan_preview(self, artifacts: RealPlanArtifacts, *, authorization: PreviewAuthorization,
                                   source_paths: Mapping[str, str | os.PathLike[str]],
                                   selections: tuple[RealPlanSelection, ...] | list[RealPlanSelection],
                                   output_root: str | os.PathLike[str],
                                   ffprobe_executable: str | os.PathLike[str],
                                   ffmpeg_executable: str | os.PathLike[str],
                                   timeout_seconds: float | None, producer_attempt_id: str) -> PreviewArtifact:
        """Render ordered, lineage-revalidated placements into a local preview."""
        if not artifacts.lineage or len(artifacts.placements) < 2:
            raise _refuse("REAL_PLAN_LINEAGE_REQUIRED")
        try:
            checked: list[RealPlanSelection] = []
            for selection in selections:
                if not isinstance(selection, RealPlanSelection):
                    raise ValueError("invalid selection type")
                bundle = ReviewBundle.from_record(selection.bundle.to_record())
                decision = HumanDecisionArtifact.from_record(selection.decision.to_record())
                if not bundle.current_e01_validated:
                    raise ValueError("sealed review bundle E01 authority was not revalidated")
                checked.append(RealPlanSelection(bundle, decision, selection.track,
                                                 selection.timeline_start_ticks, selection.order_index))
            verified = tuple(rebind_real_plan_selections(artifacts, tuple(checked)))
        except (TypeError, ValueError, KeyError) as exc:
            raise _refuse("REAL_PLAN_LINEAGE_MISMATCH", str(exc)) from exc
        if len(verified) != len(artifacts.placements) or len(source_paths) != len(verified):
            raise _refuse("SOURCE_REVISION_SET_MISMATCH")
        if authorization.schema_version != "v2" or authorization.plan_digest != artifacts.plan.digest:
            raise _refuse("V2_AUTHORIZATION_REQUIRED")
        placements, mappings = artifacts.placements, artifacts.mappings
        if (len(mappings) != len(placements) or tuple(artifacts.plan.placements) != placements or
                tuple(p.order_index for p in placements) != tuple(range(len(placements)))):
            raise _refuse("REAL_PLAN_LINEAGE_MISMATCH", "placement order or cardinality")
        probe = _local_path(ffprobe_executable, "ffprobe")
        ffmpeg = _local_path(ffmpeg_executable, "ffmpeg")
        probe_id, ffmpeg_id = _tool_identity(probe, "ffprobe"), _tool_identity(ffmpeg, "ffmpeg")
        if probe_id["sha256"] != authorization.ffprobe_tool_digest or ffmpeg_id["sha256"] != authorization.ffmpeg_tool_digest:
            raise _refuse("TOOL_IDENTITY_MISMATCH")
        if tool_configuration_digest(probe_id, ffmpeg_id, multi_placement=True) != authorization.tool_config_digest:
            raise _refuse("TOOL_CONFIG_MISMATCH")
        timeout = authorization.timeout_seconds if timeout_seconds is None else timeout_seconds
        if timeout <= 0 or timeout > authorization.timeout_seconds:
            raise _refuse("UNSUPPORTED_OPTIONS", "timeout")
        expected_bundle = tuple(s.bundle.record_digest for s in verified)
        expected_dependencies = tuple(s.bundle.dependency_digest for s in verified)
        expected_decisions = tuple(s.decision.record_digest for s in verified)
        if (authorization.review_bundle_record_digests != expected_bundle or
                authorization.review_bundle_dependency_digests != expected_dependencies or
                authorization.human_decision_digests != expected_decisions):
            raise _refuse("SEALED_RECORD_PIN_MISMATCH")
        placement_records = tuple({"order_index": i, "placement_digest": _digest(p.to_record()),
                                    "mapping_digest": m.record_digest}
                                   for i, (p, m) in enumerate(zip(placements, mappings)))
        expected_placement_set = placement_set_digest(artifacts.plan.digest, placement_records)
        if authorization.placement_set_digest != expected_placement_set:
            raise _refuse("STALE", "placement set digest")
        root = _local_path(output_root, "output_root")
        if root != authorization.output_root or str(root) != os.path.realpath(root):
            raise _refuse("PATH_ESCAPE", "output root is not authorized")
        pins: list[PreviewSourcePin] = []
        source_items: list[dict[str, Any]] = []
        source_hashes: list[tuple[Path, bytes, str]] = []
        input_paths: list[Path] = []
        timebase = None
        composition: list[dict[str, Any]] = []
        total_duration = 0
        for i, (selection, placement, mapping) in enumerate(zip(verified, placements, mappings)):
            payload = selection.bundle.payload
            revision_id = payload["source"]["source_revision_id"]
            source_value = source_paths.get(revision_id)
            if source_value is None:
                raise _refuse("SOURCE_REVISION_REQUIRED", revision_id)
            source = _local_path(source_value, "source")
            refinement = artifacts.plan.pinned_refinements.get(mapping.source_refinement_id)
            if not isinstance(refinement, Mapping) or revision_id != payload["source"]["source_revision_id"]:
                raise _refuse("INVALID_TIMING_DOMAIN")
            interval, tb = refinement.get("source_pts_interval", {}), refinement.get("timebase", {})
            if (interval.get("time_domain") != "source_pts" or interval.get("endpoint_semantics") != "half_open" or
                    type(interval.get("start")) is not int or type(interval.get("end")) is not int or
                    interval["end"] <= interval["start"]):
                raise _refuse("INVALID_TIMING_DOMAIN")
            identity = (tb.get("num"), tb.get("den"))
            if any(type(v) is not int or v <= 0 for v in identity) or identity != (
                    placement.timeline_domain.time_base.num, placement.timeline_domain.time_base.den):
                raise _refuse("INVALID_TIMING_DOMAIN", "timeline/source timebase mismatch")
            if timebase is None:
                timebase = identity
            elif timebase != identity:
                raise _refuse("INVALID_TIMING_DOMAIN", "incompatible source timebases")
            if (mapping.scale_num != 1 or mapping.scale_den != 1 or
                    mapping.timeline_domain != placement.timeline_domain or
                    mapping.source_start_pts != interval["start"] or mapping.source_end_pts != interval["end"]):
                raise _refuse("INVALID_TIMING_DOMAIN", "unsupported mapping")
            evidence_ref = refinement.get("source_probe_artifact_ref") or refinement.get("evidence_artifact_ref")
            evidence_digest = refinement.get("source_probe_digest") if refinement.get("source_probe_artifact_ref") else refinement.get("evidence_digest")
            try:
                evidence_bytes = Path(evidence_ref).read_bytes()
                if _sha(evidence_bytes) != evidence_digest:
                    raise ValueError("evidence digest mismatch")
                evidence = json.loads(evidence_bytes.decode("utf-8"))
                # Root G §3.2(7): keep duplicate presentation ticks; membership
                # checks are defined over the multiset, not a collapsed set.
                pts: list[int] = []
                for rows, fields in (
                        (normalized_frame_rows(evidence), ("best_effort_timestamp", "pts", "pkt_pts")),
                        (normalized_packet_rows(evidence), ("pts",))):
                    for frame in rows:
                        if frame.get("stream_index") is not None and int(frame["stream_index"]) == refinement["selected_stream_index"]:
                            for field_name in fields:
                                value = frame.get(field_name)
                                if type(value) is int: pts.append(value)
                                elif isinstance(value, str) and value.strip().lstrip("-").isdigit(): pts.append(int(value))
                if interval["start"] not in pts or interval["end"] not in pts:
                    raise ValueError("source PTS endpoints were not observed")
            except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
                raise _refuse("SOURCE_PTS_EVIDENCE_INVALID", str(exc)) from exc
            try:
                before_bytes = source.read_bytes()
            except OSError as exc:
                raise _refuse("LOCAL_SOURCE_REQUIRED", str(exc)) from exc
            source_sha = _sha(before_bytes)
            if (source_sha != payload["source"]["source_sha256"] or
                    len(before_bytes) != payload["source"].get("source_byte_count")):
                raise _refuse("SOURCE_DIGEST_MISMATCH", revision_id)
            source_probe_argv = (str(probe), "-v", "error", "-of", "json", "-show_streams", "-show_format", str(source))
            try:
                source_probe_result = self.runner(list(source_probe_argv), shell=False, capture_output=True,
                                                  check=False, timeout=timeout)
            except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
                raise _refuse("PROBE_FAILED", _exception_detail(exc)) from exc
            source_probe_code, source_probe_stdout, source_probe_stderr = _completed(source_probe_result)
            if source_probe_code != 0:
                raise _refuse("PROBE_FAILED", _failure_detail(source_probe_code, source_probe_stderr))
            try:
                source_probe = json.loads(source_probe_stdout.decode("utf-8"))
                selected_streams = [s for s in source_probe["streams"] if s.get("codec_type") == "video"
                                    and int(s["index"]) == refinement["selected_stream_index"]]
                if len(selected_streams) != 1 or selected_streams[0].get("time_base") != f"{identity[0]}/{identity[1]}":
                    raise ValueError("selected source stream/timebase mismatch")
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise _refuse("PROBE_MISMATCH", str(exc)) from exc
            if revision_id in {p.source_revision_id for p in pins}:
                raise _refuse("SOURCE_REVISION_SET_MISMATCH", "duplicate source revision")
            pins.append(PreviewSourcePin(revision_id, source_sha, len(before_bytes)))
            source_hashes.append((source, before_bytes, source_sha)); input_paths.append(source)
            stream_index = refinement["selected_stream_index"]
            source_items.append({"order_index": i, "placement_id": placement.placement_id,
                                 "source_revision_id": revision_id, "source_sha256": source_sha,
                                 "byte_count": len(before_bytes), "stream_index": stream_index,
                                 "source_pts_start": interval["start"], "source_pts_end_exclusive": interval["end"]})
            duration = interval["end"] - interval["start"]
            if placement.timeline_end_ticks - placement.timeline_start_ticks != duration or placement.timeline_start_ticks != total_duration:
                raise _refuse("UNSUPPORTED_PLAN_LAYOUT", "placements must be contiguous and preserve measured PTS duration")
            total_duration += duration
            composition.append({"order_index": i, "placement_id": placement.placement_id,
                                "placement_digest": _digest(placement.to_record()), "mapping_digest": mapping.record_digest,
                                "source_revision_id": revision_id, "source_sha256": source_sha,
                                "stream_index": stream_index, "source_timebase": {"num": identity[0], "den": identity[1]},
                                "source_pts_start": interval["start"], "source_pts_end_exclusive": interval["end"],
                                "timeline_start_ticks": placement.timeline_start_ticks,
                                "timeline_end_ticks": placement.timeline_end_ticks})
        expected_source_set = source_set_digest(pins)
        if authorization.ordered_source_pins != tuple(pins) or authorization.source_set_digest != expected_source_set:
            raise _refuse("STALE", "source set digest")
        composition_value = composition_digest(artifacts.plan.digest,
                                               {"domain_id": placements[0].timeline_domain.domain_id,
                                                "time_base": {"num": timebase[0], "den": timebase[1]}}, composition)
        if authorization.composition_digest != composition_value:
            raise _refuse("STALE", "composition digest")
        if authorization.record_digest != authorization.compute_digest() or authorization.revoked:
            raise _refuse("STALE", "authorization digest")
        if authorization.expires_at is not None:
            try:
                expiry = datetime.fromisoformat(authorization.expires_at.replace("Z", "+00:00"))
                if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc): raise _refuse("STALE")
            except ValueError as exc: raise _refuse("STALE", "invalid expiry") from exc
        if artifacts.plan.export_eligible or authorization.production_eligible or authorization.export_eligible:
            raise _refuse("INVALID_SCOPE")
        root.mkdir(parents=True, exist_ok=True)
        if any(not source.is_file() or _inside(source, root) for source in input_paths):
            raise _refuse("PATH_ESCAPE", "source/output roles overlap")
        plan_id = artifacts.plan.plan_id
        if not isinstance(plan_id, str) or not plan_id or Path(plan_id).name != plan_id or plan_id in {".", ".."}:
            raise _refuse("PATH_ESCAPE", "unsafe plan id")
        final = root / f"{plan_id}.preview.mp4"
        temp_dir = Path(tempfile.mkdtemp(prefix=f".{final.name}.", dir=str(root)))
        temp = temp_dir / "render.mp4"
        segment_paths = [temp_dir / f"placement-{i}.mp4" for i in range(len(input_paths))]
        ffmpeg_commands: list[list[str]] = []
        for i, (source, segment, record) in enumerate(zip(input_paths, segment_paths, composition)):
            stream_index = record["stream_index"]
            filter_expr = (f"trim=start_pts={record['source_pts_start']}:end_pts="
                           f"{record['source_pts_end_exclusive']},setpts=PTS-STARTPTS")
            ffmpeg_commands.append([str(ffmpeg), "-v", "error", "-nostdin", "-copyts", "-i", str(source),
                "-map", f"0:{stream_index}", "-vf", filter_expr, "-c:v", "libx264", "-preset", "ultrafast",
                "-crf", "18", "-pix_fmt", "yuv420p", "-fps_mode", "passthrough", "-video_track_timescale",
                str(timebase[1]), "-an", "-f", "mp4", str(segment)])
        manifest = temp_dir / "concat-list.txt"
        def concat_quote(path: Path) -> str:
            return "'" + str(path).replace("'", "'\\''") + "'"
        manifest.write_text("".join(f"file {concat_quote(segment)}\n" for segment in segment_paths), encoding="utf-8")
        concat_argv = [str(ffmpeg), "-v", "error", "-nostdin", "-f", "concat", "-safe", "0", "-i", str(manifest),
                       "-c", "copy", "-video_track_timescale", str(timebase[1]), "-an", "-f", "mp4", str(temp)]
        ffmpeg_commands.append(concat_argv)
        flattened_argv = [arg for command in ffmpeg_commands for arg in ("--COMMAND--", *command)]
        try:
            for command, destination in zip(ffmpeg_commands, [*segment_paths, temp]):
                try: result = self.runner(command, shell=False, capture_output=True, check=False, timeout=timeout)
                except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
                    raise _refuse("RENDER_FAILED", _exception_detail(exc)) from exc
                code, _, stderr = _completed(result)
                if code != 0 or not destination.is_file() or destination.stat().st_size <= 0 or destination.stat().st_size > authorization.max_output_bytes:
                    raise _refuse("RENDER_FAILED", _render_failure_detail(code, stderr, destination, tuple(command)))
            if temp.stat().st_size > authorization.max_output_bytes:
                raise _refuse("RENDER_FAILED", "output byte limit exceeded")
            output_probe_argv = [str(probe), "-v", "error", "-of", "json", "-show_streams", "-show_format", str(temp)]
            try: output_result = self.runner(output_probe_argv, shell=False, capture_output=True, check=False, timeout=timeout)
            except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
                raise _refuse("OUTPUT_PROBE_FAILED", _exception_detail(exc)) from exc
            output_code, output_stdout, output_stderr = _completed(output_result)
            if output_code != 0: raise _refuse("OUTPUT_PROBE_FAILED", _failure_detail(output_code, output_stderr))
            try:
                measured = json.loads(output_stdout.decode("utf-8")); videos = [s for s in measured["streams"] if s.get("codec_type") == "video"]
                if len(videos) != 1 or videos[0].get("time_base") != f"{timebase[0]}/{timebase[1]}" or int(videos[0]["duration_ts"]) != total_duration:
                    raise ValueError(f"output stream, timebase, or duration mismatch: {videos}")
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise _refuse("OUTPUT_PROBE_FAILED", str(exc)) from exc
            for source, before_bytes, before_sha in source_hashes:
                after_bytes = source.read_bytes()
                if _sha(after_bytes) != before_sha or len(after_bytes) != len(before_bytes):
                    raise _refuse("SOURCE_DIGEST_MISMATCH")
            output_bytes = temp.read_bytes(); output_sha = _sha(output_bytes)
            try: os.link(temp, final)
            except FileExistsError as exc: raise _refuse("OUTPUT_EXISTS") from exc
            ordered_inputs = tuple(source_items)
            return PreviewArtifact(final, len(output_bytes), output_sha, source_hashes[0][2], source_hashes[0][2],
                len(source_hashes[0][1]), len(source_hashes[0][1]), pins[0].source_revision_id,
                composition[0]["stream_index"], timebase[0], timebase[1], composition[0]["source_pts_start"],
                composition[0]["source_pts_end_exclusive"], artifacts.plan.digest,
                _digest(placements[0].to_record()), mappings[0].record_digest, authorization.record_digest,
                tuple(output_probe_argv), tuple(flattened_argv), probe_id, ffmpeg_id, schema_version="v2",
                ordered_inputs=ordered_inputs, placement_set_digest=expected_placement_set,
                source_set_digest=expected_source_set, composition_digest=composition_value,
                tool_config_digest=authorization.tool_config_digest,
                ffprobe_argv_digest=_digest(output_probe_argv), ffmpeg_argv_digest=_digest(ffmpeg_commands),
                output_video_stream_count=1, output_timebase_num=timebase[0], output_timebase_den=timebase[1],
                output_duration_ticks=total_duration)
        finally:
            temp.unlink(missing_ok=True); shutil.rmtree(temp_dir, ignore_errors=True)

    def render_preview(self, artifacts: RealPlanArtifacts, *, authorization: PreviewAuthorization,
                       source_path: str | os.PathLike[str], output_root: str | os.PathLike[str],
                       ffprobe_executable: str | os.PathLike[str],
                       ffmpeg_executable: str | os.PathLike[str],
                       timeout_seconds: float | None = None,
                       producer_attempt_id: str = "",
                       synthetic_opt_in: bool = False,
                       synthetic_preflight: SyntheticPreflightContext | None = None,
                       synthetic_binding: AdmissionBinding | None = None) -> PreviewArtifact:
        if not isinstance(synthetic_opt_in, bool):
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        if synthetic_opt_in:
            if not isinstance(artifacts, RealPlanArtifacts) and not hasattr(getattr(artifacts, "plan", None), "digest"):
                raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
            if not isinstance(authorization, PreviewAuthorization) and not all(
                    hasattr(authorization, name) for name in ("source_revision_id", "source_sha256")):
                raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
            if synthetic_preflight is None or synthetic_binding is None:
                raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
            try:
                preview_authorization_digest = authorization.compute_digest()
                if authorization.record_digest != preview_authorization_digest:
                    raise CorpusAdmissionError("CORPUS_SEPARATION_ATTESTATION_DIGEST_MISMATCH")
                require_synthetic_preflight(
                    synthetic_preflight, bindings=(synthetic_binding,),
                    operation="local_preview.render_preview", output_root=output_root,
                    plan_digest=artifacts.plan.digest,
                    preview_authorization_digest=preview_authorization_digest,
                )
            except CorpusAdmissionError:
                raise
            except (AttributeError, TypeError, ValueError) as exc:
                raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID") from exc
            if (synthetic_binding.revision_id != authorization.source_revision_id
                    or synthetic_binding.source_sha256 != authorization.source_sha256):
                raise CorpusAdmissionError("CORPUS_SEPARATION_BINDING_MISMATCH")
            # P1's verifier is synthetic-only.  A valid result can check that a
            # requested boundary is consistently bound, but it cannot authorize
            # REAL media rendering or produce REAL preview/QC evidence.
            raise CorpusAdmissionError("CORPUS_SEPARATION_SYNTHETIC_PREFLIGHT_ONLY")
        if synthetic_preflight is not None or synthetic_binding is not None:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        if not isinstance(artifacts, RealPlanArtifacts) or not isinstance(authorization, PreviewAuthorization):
            raise _refuse("MISSING_AUTHORIZATION")
        if authorization.record_digest != authorization.compute_digest():
            raise _refuse("STALE", "authorization digest")
        if authorization.revoked:
            raise _refuse("STALE")
        if authorization.expires_at is not None:
            try:
                expiry = datetime.fromisoformat(authorization.expires_at.replace("Z", "+00:00"))
                if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
                    raise _refuse("STALE")
            except ValueError as exc:
                raise _refuse("STALE", "invalid expiry") from exc
        if artifacts.plan.export_eligible or authorization.production_eligible or authorization.export_eligible:
            raise _refuse("INVALID_SCOPE")
        if authorization.plan_digest != artifacts.plan.digest:
            raise _refuse("STALE", "plan digest")
        if authorization.placement_digest != _digest(artifacts.placement.to_record()):
            raise _refuse("STALE", "placement digest")
        if authorization.mapping_digest != artifacts.mapping.record_digest:
            raise _refuse("STALE", "mapping digest")
        source = _local_path(source_path, "source")
        root = _local_path(output_root, "output_root")
        if root != authorization.output_root:
            raise _refuse("PATH_ESCAPE", "output root is not authorized")
        root.mkdir(parents=True, exist_ok=True)
        if not source.is_file() or _inside(source, root):
            raise _refuse("PATH_ESCAPE", "source/output roles overlap")
        probe = _local_path(ffprobe_executable, "ffprobe")
        ffmpeg = _local_path(ffmpeg_executable, "ffmpeg")
        probe_id, ffmpeg_id = _tool_identity(probe, "ffprobe"), _tool_identity(ffmpeg, "ffmpeg")
        if probe_id["sha256"] != authorization.ffprobe_tool_digest:
            raise _refuse("TOOL_IDENTITY_MISMATCH", "ffprobe")
        if ffmpeg_id["sha256"] != authorization.ffmpeg_tool_digest:
            raise _refuse("TOOL_IDENTITY_MISMATCH", "ffmpeg")
        if tool_configuration_digest(probe_id, ffmpeg_id) != authorization.tool_config_digest:
            raise _refuse("TOOL_CONFIG_MISMATCH")
        timeout = authorization.timeout_seconds if timeout_seconds is None else timeout_seconds
        if timeout <= 0 or timeout > authorization.timeout_seconds:
            raise _refuse("UNSUPPORTED_OPTIONS", "timeout")

        refinement = artifacts.plan.pinned_refinements.get(artifacts.mapping.source_refinement_id)
        if not isinstance(refinement, Mapping):
            raise _refuse("INVALID_TIMING_DOMAIN")
        if refinement.get("source_revision_id") != authorization.source_revision_id:
            raise _refuse("STALE", "source revision")
        interval = refinement.get("source_pts_interval", {})
        if (interval.get("time_domain") != "source_pts" or interval.get("endpoint_semantics") != "half_open"
                or any(isinstance(interval.get(k), bool) or not isinstance(interval.get(k), int) for k in ("start", "end"))):
            raise _refuse("INVALID_TIMING_DOMAIN")
        start, end = interval["start"], interval["end"]
        if end <= start:
            raise _refuse("INVALID_TIMING_DOMAIN")
        tb = refinement.get("timebase", {})
        if (tb.get("num"), tb.get("den")) != (artifacts.mapping.source_timebase_num, artifacts.mapping.source_timebase_den):
            raise _refuse("INVALID_TIMING_DOMAIN")
        measured_pts: tuple[int, ...] = ()
        evidence_ref = refinement.get("source_probe_artifact_ref") or refinement.get("evidence_artifact_ref")
        expected_evidence_digest = refinement.get("source_probe_digest") if refinement.get("source_probe_artifact_ref") else refinement.get("evidence_digest")
        if not evidence_ref or not expected_evidence_digest or not Path(evidence_ref).is_file():
            raise _refuse("SOURCE_PTS_EVIDENCE_REQUIRED")
        if evidence_ref:
            try:
                evidence_path = Path(evidence_ref)
                evidence_bytes = evidence_path.read_bytes()
                if _sha(evidence_bytes) != expected_evidence_digest:
                    raise _refuse("SOURCE_PTS_EVIDENCE_INVALID", "digest mismatch")
                evidence = json.loads(evidence_bytes.decode("utf-8"))
                values: list[int] = []
                def as_tick(value):
                    if isinstance(value, int) and not isinstance(value, bool):
                        return value
                    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
                        return int(value.strip())
                    return None
                for rows, fields in (
                        (normalized_frame_rows(evidence), ("best_effort_timestamp", "pts", "pkt_pts")),
                        (normalized_packet_rows(evidence), ("pts",))):
                    for item in rows:
                        if item.get("stream_index") is None:
                            continue
                        if int(item["stream_index"]) != int(refinement["selected_stream_index"]):
                            continue
                        for field in fields:
                            value = item.get(field)
                            tick = as_tick(value)
                            if tick is not None:
                                values.append(tick)
                                break
                measured_pts = tuple(sorted(values))
                if start not in measured_pts or end not in measured_pts:
                    raise _refuse("SOURCE_PTS_NOT_OBSERVED")
            except PreviewRefusal:
                raise
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise _refuse("SOURCE_PTS_EVIDENCE_INVALID", str(exc)) from exc
        try:
            before_bytes = source.read_bytes()
        except OSError as exc:
            raise _refuse("LOCAL_SOURCE_REQUIRED", str(exc)) from exc
        before = _sha(before_bytes)
        if before != authorization.source_sha256:
            raise _refuse("SOURCE_DIGEST_MISMATCH")
        stream_index = int(refinement["selected_stream_index"])
        ffprobe_argv = (str(probe), "-v", "error", "-of", "json", "-show_streams", "-show_format", str(source))
        try:
            result = self.runner(list(ffprobe_argv), shell=False, capture_output=True, check=False, timeout=timeout)
        except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
            raise _refuse("PROBE_FAILED", _exception_detail(exc)) from exc
        code, stdout, stderr = _completed(result)
        if code != 0:
            raise _refuse("PROBE_FAILED", _failure_detail(code, stderr))
        try:
            payload = json.loads(stdout.decode("utf-8"))
            streams = [s for s in payload["streams"] if s.get("codec_type") == "video"]
            matches = [s for s in streams if int(s["index"]) == stream_index]
            if len(matches) != 1:
                raise ValueError("selected stream is absent or duplicated")
            selected = matches[0]
            if str(selected.get("time_base")) != f"{tb['num']}/{tb['den']}":
                raise ValueError("timebase mismatch")
        except (KeyError, StopIteration, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise _refuse("PROBE_MISMATCH", str(exc)) from exc
        plan_id = artifacts.plan.plan_id
        if (not isinstance(plan_id, str) or not plan_id or Path(plan_id).name != plan_id
                or plan_id in {".", ".."} or any(ch in plan_id for ch in ("/", "\\"))):
            raise _refuse("PATH_ESCAPE", "unsafe plan id")
        final = root / f"{plan_id}.preview.mp4"
        if not _inside(final, root):
            raise _refuse("PATH_ESCAPE", "final output")
        # FFmpeg refuses an existing output pathname when -y is absent. Keep
        # the private staging directory, but pass a genuinely non-existent
        # child pathname so the tool owns creation and publication remains
        # hard-link based and non-overwriting.
        temp_dir = Path(tempfile.mkdtemp(prefix=f".{final.name}.", dir=str(root)))
        temp = temp_dir / "render.mp4"
        filter_expr = f"trim=start_pts={start}:end_pts={end},setpts=PTS-STARTPTS"
        ffmpeg_argv = (str(ffmpeg), "-v", "error", "-nostdin", "-copyts", "-i", str(source),
                       "-map", f"0:{stream_index}", "-vf", filter_expr, "-c:v", "libx264",
                       "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
                       "-fps_mode", "passthrough", "-video_track_timescale", str(tb["den"]),
                       "-an", "-f", "mp4", str(temp))
        try:
            try:
                result = self.runner(list(ffmpeg_argv), shell=False, capture_output=True, check=False, timeout=timeout)
            except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
                raise _refuse("RENDER_FAILED", _exception_detail(exc)) from exc
            code, _, stderr = _completed(result)
            if code != 0 or not temp.is_file() or temp.stat().st_size <= 0 or temp.stat().st_size > authorization.max_output_bytes:
                detail = _render_failure_detail(code, stderr, temp, ffmpeg_argv)
                raise _refuse("RENDER_FAILED", detail)
            output_probe_argv = (str(probe), "-v", "error", "-of", "json", "-show_streams", "-show_format", str(temp))
            try:
                output_probe = self.runner(list(output_probe_argv), shell=False, capture_output=True, check=False, timeout=timeout)
            except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
                raise _refuse("OUTPUT_PROBE_FAILED", _exception_detail(exc)) from exc
            output_code, output_stdout, output_stderr = _completed(output_probe)
            if output_code != 0:
                raise _refuse("OUTPUT_PROBE_FAILED", _failure_detail(output_code, output_stderr))
            try:
                output_payload = json.loads(output_stdout.decode("utf-8"))
                videos = [s for s in output_payload["streams"] if s.get("codec_type") == "video"]
                if len(videos) != 1:
                    raise ValueError("output must contain exactly one video stream")
                if str(videos[0].get("time_base")) != f"{tb['num']}/{tb['den']}":
                    raise ValueError("output timebase mismatch")
                duration_ts = videos[0].get("duration_ts")
                if isinstance(duration_ts, bool) or not isinstance(duration_ts, (int, str)):
                    raise ValueError("output duration is missing")
                if int(duration_ts) != end - start:
                    raise ValueError("output duration mismatch")
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise _refuse("OUTPUT_PROBE_FAILED", str(exc)) from exc
            after_bytes = source.read_bytes(); after = _sha(after_bytes)
            if after != before or len(after_bytes) != len(before_bytes):
                raise _refuse("SOURCE_DIGEST_MISMATCH")
            output_bytes = temp.read_bytes(); output_hash = _sha(output_bytes)
            # Hard-link publication never overwrites an existing authoritative preview.
            try:
                os.link(temp, final)
            except FileExistsError as exc:
                raise _refuse("OUTPUT_EXISTS") from exc
            temp.unlink(missing_ok=True)
            return PreviewArtifact(final, len(output_bytes), output_hash, before, after,
                                   len(before_bytes), len(after_bytes),
                                   authorization.source_revision_id, stream_index, tb["num"], tb["den"],
                                   start, end, artifacts.plan.digest,
                                   authorization.placement_digest, artifacts.mapping.record_digest,
                                   authorization.record_digest, ffprobe_argv, ffmpeg_argv,
                                   probe_id, ffmpeg_id, False, False, "NOT_OBSERVED", producer_attempt_id, measured_pts)
        finally:
            temp.unlink(missing_ok=True)
            shutil.rmtree(temp_dir, ignore_errors=True)


__all__ = ["LocalPreviewAdapter", "PreviewAuthorization", "PreviewArtifact", "PreviewRefusal",
           "PreviewSourcePin", "canonical_digest", "placement_set_digest", "source_set_digest",
           "composition_digest", "tool_configuration_digest"]
