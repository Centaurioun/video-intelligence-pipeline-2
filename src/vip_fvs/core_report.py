"""Versioned JSON report contract and atomic publisher for QUERY_DRIVEN_SEMANTIC_REPORT_V1."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping

CORE_REPORT_SCHEMA_VERSION = 1
CORE_REPORT_KIND = "vip_fvs.query_driven_semantic_report.v1"
ANALYSIS_KIND_SEMANTIC_RETRIEVAL = "semantic_retrieval"

APPROVED_EVIDENCE_CLASSES = frozenset(
    {
        "MEASURED",
        "MATCHED",
        "VISUALLY_OBSERVED",
        "AUDIO_OBSERVED",
        "EDITORIAL_INFERENCE",
    }
)
NOT_OBSERVED = "NOT_OBSERVED"
OBSERVED = "OBSERVED"

VALID_STAGE_STATUSES = frozenset({"SUCCEEDED", "FAILED", "PARTIAL", "BLOCKED"})
VALID_RESULT_KINDS = frozenset({"MATCHES_FOUND", "ZERO_MATCH", "REFUSED", "FAILED"})
VALID_RUNTIME_MODES = frozenset({"REAL", "SYNTHETIC"})
VALID_CUSTODY_STATES = frozenset({"SNAPSHOT_VERIFIED", "PRESERVED_IMMUTABLE"})
VALID_AUTHORIZATION_MODES = frozenset({"OWNER_PILOT_AUTHORIZATION", "SYNTHETIC_TEST_ONLY"})
VALID_INDEX_DISPOSITIONS = frozenset(
    {"INDEXED", "SKIPPED_UNCHANGED", "REUSED_SAME_OCCURRENCE"}
)
VALID_THUMBNAIL_STATUSES = frozenset({"PRESENT", "MISSING", "NOT_OBSERVED"})

DEFAULT_LIMITATIONS: tuple[str, ...] = (
    "QUERY_DRIVEN_RETRIEVAL_NOT_EXHAUSTIVE_CAPTIONING",
    "SIMILARITY_SCORE_NOT_PROBABILITY",
    "SAMPLE_PTS_NOT_EVENT_BOUNDARY_OR_EDIT_CUT",
    "NO_CALIBRATED_RELEVANCE_THRESHOLD",
)

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"sk-[0-9A-Za-z]{20,}"),
    re.compile(r"ghp_[0-9A-Za-z]{20,}"),
    re.compile(r"github_pat_[0-9A-Za-z_]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


class CoreReportError(ValueError):
    """Raised when a CORE-02 semantic report violates schema or contract invariants."""

    def __init__(self, code: str, detail: str | None = None) -> None:
        self.code = str(code)
        self.detail = detail or str(code)
        super().__init__(f"{self.code}: {self.detail}" if detail else self.code)


class CoreReportPublicationError(CoreReportError):
    """Raised when report publication fails path confinement or atomic no-clobber rules."""


def _is_non_bool_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_non_empty_str(value: Any, code: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoreReportError(code, f"{field_name} must be a non-empty string")
    return value


def _require_hex64(value: Any, code: str, field_name: str) -> str:
    if not isinstance(value, str) or not _HEX64_RE.fullmatch(value):
        raise CoreReportError(
            code, f"{field_name} must be a 64-character lowercase hex digest"
        )
    return value


def _canonical_json_without_self_digest(report: Mapping[str, Any]) -> str:
    payload = json.loads(json.dumps(dict(report), sort_keys=True))
    artifact = payload.get("artifact")
    if isinstance(artifact, dict):
        artifact.pop("report_digest", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_core_report_digest(report: Mapping[str, Any]) -> str:
    """Compute the SHA-256 digest of the report excluding artifact.report_digest."""
    canonical = _canonical_json_without_self_digest(report)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def format_rational_seconds(pts: int, timebase_num: int, timebase_den: int) -> dict[str, Any]:
    """Return exact gcd-normalized rational seconds for a source PTS and rational timebase."""
    if not _is_non_bool_int(pts) or pts < 0:
        raise CoreReportError("REPORT_INVALID_PTS", "pts must be a non-negative integer")
    if not _is_non_bool_int(timebase_num) or timebase_num <= 0:
        raise CoreReportError(
            "REPORT_INVALID_TIMEBASE", "timebase.num must be a positive integer"
        )
    if not _is_non_bool_int(timebase_den) or timebase_den <= 0:
        raise CoreReportError(
            "REPORT_INVALID_TIMEBASE", "timebase.den must be a positive integer"
        )
    exact = Fraction(pts * timebase_num, timebase_den)
    return {
        "num": int(exact.numerator),
        "den": int(exact.denominator),
        "canonical": f"{exact.numerator}/{exact.denominator}",
    }


def build_point_semantic_location(
    pts: int, timebase_num: int, timebase_den: int
) -> dict[str, Any]:
    """Build a truthful POINT approximate semantic location without fabricated window width."""
    rational = format_rational_seconds(pts, timebase_num, timebase_den)
    exact = Fraction(rational["num"], rational["den"])
    return {
        "location_kind": "POINT",
        "time_domain": "semantic_seconds",
        "position_seconds": round(float(exact), 6),
        "rational_seconds": rational,
        "window_width_seconds": NOT_OBSERVED,
    }


def validate_output_target_path(
    report_path: str | Path,
    *,
    output_root: str | Path,
    require_nonexistent: bool = False,
) -> tuple[Path, Path]:
    """Validate that report_path is confined under output_root without symlink traversal."""
    raw_root_str = str(output_root).strip() if output_root is not None else ""
    raw_report_str = str(report_path).strip() if report_path is not None else ""
    if not raw_root_str:
        raise CoreReportPublicationError(
            "OUTPUT_ROOT_REQUIRED", "output_root must be a non-empty path"
        )
    if not raw_report_str:
        raise CoreReportPublicationError(
            "REPORT_PATH_REQUIRED", "report_path must be a non-empty path"
        )

    raw_root = Path(raw_root_str).expanduser()
    raw_report = Path(raw_report_str).expanduser()
    if ".." in raw_root.parts or ".." in raw_report.parts:
        raise CoreReportPublicationError(
            "OUTPUT_PATH_TRAVERSAL_FORBIDDEN",
            "Parent traversal ('..') is forbidden in output_root or report_path",
        )

    abs_root = raw_root if raw_root.is_absolute() else (Path.cwd() / raw_root)
    abs_report = raw_report if raw_report.is_absolute() else (Path.cwd() / raw_report)

    def _reject_symlink_chain(target: Path) -> None:
        current = Path(target.anchor) if target.anchor else Path("/")
        for part in target.parts[1:] if target.anchor else target.parts:
            current = current / part
            if current.is_symlink():
                raise CoreReportPublicationError(
                    "OUTPUT_SYMLINK_FORBIDDEN",
                    f"Symlink component is forbidden in output path: {current}",
                )

    _reject_symlink_chain(abs_root)
    _reject_symlink_chain(abs_report)

    resolved_root = abs_root.resolve(strict=False)
    resolved_report = abs_report.resolve(strict=False)

    if resolved_report == resolved_root:
        raise CoreReportPublicationError(
            "OUTPUT_PATH_IS_DIRECTORY",
            "report_path must designate a file inside output_root, not output_root itself",
        )
    try:
        resolved_report.relative_to(resolved_root)
    except ValueError as exc:
        raise CoreReportPublicationError(
            "OUTPUT_PATH_OUTSIDE_ROOT",
            f"report_path {resolved_report} is outside output_root {resolved_root}",
        ) from exc

    if abs_report.is_symlink() or (abs_report.exists() and abs_report.is_dir()):
        if abs_report.is_symlink():
            raise CoreReportPublicationError(
                "OUTPUT_SYMLINK_FORBIDDEN",
                f"report_path must not be a symlink: {abs_report}",
            )
        raise CoreReportPublicationError(
            "OUTPUT_PATH_IS_DIRECTORY",
            f"report_path points to an existing directory: {abs_report}",
        )

    if require_nonexistent and (abs_report.exists() or abs_report.is_symlink()):
        raise CoreReportPublicationError(
            "OUTPUT_ALREADY_EXISTS",
            f"Refusing to overwrite existing report path: {abs_report}",
        )

    return resolved_root, resolved_report


def build_core_semantic_report(
    *,
    attempt_id: str,
    run_id: str,
    runtime_mode: str,
    top_k: int,
    total_eligible_matches: int | str,
    source: Mapping[str, Any],
    authority: Mapping[str, Any],
    model: Mapping[str, Any],
    index: Mapping[str, Any],
    query: Mapping[str, Any],
    matches: list[Mapping[str, Any]],
    report_path: str,
    output_root: str,
    warnings: list[str] | None = None,
    limitations: list[str] | None = None,
    refinement_observed: bool = False,
) -> dict[str, Any]:
    """Assemble, digest, and validate a canonical QUERY_DRIVEN_SEMANTIC_REPORT_V1 dictionary."""
    normalized_matches = [dict(item) for item in matches]
    returned_count = len(normalized_matches)
    result_kind = "MATCHES_FOUND" if returned_count > 0 else "ZERO_MATCH"

    merged_limitations = list(DEFAULT_LIMITATIONS)
    if runtime_mode == "SYNTHETIC":
        merged_limitations.append("SYNTHETIC_FAKE_EMBEDDER_NO_MODEL_INFERENCE")
    if not refinement_observed:
        merged_limitations.append("NO_SOURCE_NATIVE_REFINEMENT_OBSERVED")
    if limitations:
        for item in limitations:
            if item not in merged_limitations:
                merged_limitations.append(item)

    evidence_availability = {
        "authentic_model_inference": (
            OBSERVED if model.get("authentic_inference_observed") is True else NOT_OBSERVED
        ),
        "source_native_interval_refinement": (
            OBSERVED if refinement_observed else NOT_OBSERVED
        ),
        "human_editorial_decision": NOT_OBSERVED,
        "visual_scene_captioning": NOT_OBSERVED,
        "audio_observation": NOT_OBSERVED,
    }

    non_claims = {
        "captioning_performed": False,
        "exhaustive_scene_description": False,
        "editorial_decision_present": False,
        "edit_boundary_established": False,
        "export_eligible": False,
        "production_eligible": False,
        "gate_promotion_claimed": False,
        "model_winner_claimed": False,
    }

    report: dict[str, Any] = {
        "schema_version": CORE_REPORT_SCHEMA_VERSION,
        "report_kind": CORE_REPORT_KIND,
        "analysis_kind": ANALYSIS_KIND_SEMANTIC_RETRIEVAL,
        "attempt_id": attempt_id,
        "run_id": run_id,
        "runtime_mode": runtime_mode,
        "stage_status": "SUCCEEDED",
        "result_kind": result_kind,
        "top_k": top_k,
        "total_eligible_matches": total_eligible_matches,
        "returned_candidate_count": returned_count,
        "errors": [],
        "warnings": list(warnings or []),
        "limitations": merged_limitations,
        "evidence_availability": evidence_availability,
        "non_claims": non_claims,
        "source": dict(source),
        "authority": dict(authority),
        "model": dict(model),
        "index": dict(index),
        "query": dict(query),
        "matches": normalized_matches,
        "artifact": {
            "report_path": str(report_path),
            "output_root": str(output_root),
            "schema_valid": True,
        },
    }
    report["artifact"]["report_digest"] = compute_core_report_digest(report)
    validate_core_semantic_report(report)
    return report


def validate_core_semantic_report(report: Mapping[str, Any]) -> None:
    """Validate all structural, temporal, evidence, and provenance invariants on Report V1."""
    if not isinstance(report, Mapping):
        raise CoreReportError("REPORT_INVALID_TYPE", "Report must be a JSON object")

    if (
        not _is_non_bool_int(report.get("schema_version"))
        or report.get("schema_version") != CORE_REPORT_SCHEMA_VERSION
    ):
        raise CoreReportError(
            "REPORT_INVALID_SCHEMA_VERSION",
            f"schema_version must be {CORE_REPORT_SCHEMA_VERSION}",
        )
    if report.get("report_kind") != CORE_REPORT_KIND:
        raise CoreReportError(
            "REPORT_INVALID_KIND", f"report_kind must be {CORE_REPORT_KIND!r}"
        )
    if report.get("analysis_kind") != ANALYSIS_KIND_SEMANTIC_RETRIEVAL:
        raise CoreReportError(
            "REPORT_INVALID_ANALYSIS_KIND",
            f"analysis_kind must be {ANALYSIS_KIND_SEMANTIC_RETRIEVAL!r}",
        )

    _require_non_empty_str(report.get("attempt_id"), "REPORT_INVALID_ATTEMPT_ID", "attempt_id")
    _require_non_empty_str(report.get("run_id"), "REPORT_INVALID_RUN_ID", "run_id")

    runtime_mode = report.get("runtime_mode")
    if runtime_mode not in VALID_RUNTIME_MODES:
        raise CoreReportError(
            "REPORT_INVALID_RUNTIME_MODE",
            f"runtime_mode must be one of {sorted(VALID_RUNTIME_MODES)}",
        )

    stage_status = report.get("stage_status")
    if stage_status not in VALID_STAGE_STATUSES:
        raise CoreReportError(
            "REPORT_INVALID_STAGE_STATUS",
            f"stage_status must be one of {sorted(VALID_STAGE_STATUSES)}",
        )

    result_kind = report.get("result_kind")
    if result_kind not in VALID_RESULT_KINDS:
        raise CoreReportError(
            "REPORT_INVALID_RESULT_KIND",
            f"result_kind must be one of {sorted(VALID_RESULT_KINDS)}",
        )

    top_k = report.get("top_k")
    if not _is_non_bool_int(top_k) or top_k < 1 or top_k > 1000:
        raise CoreReportError("REPORT_INVALID_TOP_K", "top_k must be an integer in [1, 1000]")

    total_eligible = report.get("total_eligible_matches")
    if total_eligible != NOT_OBSERVED and (
        not _is_non_bool_int(total_eligible) or total_eligible < 0
    ):
        raise CoreReportError(
            "REPORT_INVALID_TOTAL_ELIGIBLE_MATCHES",
            "total_eligible_matches must be a non-negative integer or NOT_OBSERVED",
        )

    returned_count = report.get("returned_candidate_count")
    if not _is_non_bool_int(returned_count) or returned_count < 0 or returned_count > top_k:
        raise CoreReportError(
            "REPORT_INVALID_RETURNED_COUNT",
            "returned_candidate_count must be an integer in [0, top_k]",
        )
    if total_eligible != NOT_OBSERVED and total_eligible < returned_count:
        raise CoreReportError(
            "REPORT_INVALID_MATCH_COUNTS",
            "total_eligible_matches cannot be less than returned_candidate_count",
        )

    errors = report.get("errors")
    if not isinstance(errors, list) or not all(
        isinstance(e, str) and e.strip() for e in errors
    ):
        raise CoreReportError("REPORT_INVALID_ERRORS", "errors must be a list of non-empty strings")

    warnings = report.get("warnings")
    if not isinstance(warnings, list) or not all(
        isinstance(w, str) and w.strip() for w in warnings
    ):
        raise CoreReportError(
            "REPORT_INVALID_WARNINGS", "warnings must be a list of non-empty strings"
        )

    limitations = report.get("limitations")
    if (
        not isinstance(limitations, list)
        or not limitations
        or not all(isinstance(item, str) and item.strip() for item in limitations)
    ):
        raise CoreReportError(
            "REPORT_INVALID_LIMITATIONS",
            "limitations must be a non-empty list of strings",
        )

    evidence_availability = report.get("evidence_availability")
    if not isinstance(evidence_availability, Mapping):
        raise CoreReportError(
            "REPORT_INVALID_EVIDENCE_AVAILABILITY",
            "evidence_availability must be an object",
        )
    for key in (
        "authentic_model_inference",
        "source_native_interval_refinement",
        "human_editorial_decision",
        "visual_scene_captioning",
        "audio_observation",
    ):
        val = evidence_availability.get(key)
        if val not in {OBSERVED, NOT_OBSERVED}:
            raise CoreReportError(
                "REPORT_INVALID_EVIDENCE_AVAILABILITY",
                f"evidence_availability.{key} must be OBSERVED or NOT_OBSERVED",
            )
    if runtime_mode == "SYNTHETIC" and (
        evidence_availability.get("authentic_model_inference") != NOT_OBSERVED
    ):
        raise CoreReportError(
            "REPORT_SYNTHETIC_INFERENCE_MISLABELED",
            "SYNTHETIC runtime_mode must report authentic_model_inference as NOT_OBSERVED",
        )
    if evidence_availability.get("human_editorial_decision") != NOT_OBSERVED:
        raise CoreReportError(
            "REPORT_EDITORIAL_DECISION_MISLABELED",
            "Automatic semantic analysis must report human_editorial_decision as NOT_OBSERVED",
        )
    if evidence_availability.get("visual_scene_captioning") != NOT_OBSERVED:
        raise CoreReportError(
            "REPORT_CAPTIONING_MISLABELED",
            "Semantic retrieval report must report visual_scene_captioning as NOT_OBSERVED",
        )

    non_claims = report.get("non_claims")
    if not isinstance(non_claims, Mapping):
        raise CoreReportError("REPORT_INVALID_NON_CLAIMS", "non_claims must be an object")
    for required_false_key in (
        "captioning_performed",
        "exhaustive_scene_description",
        "editorial_decision_present",
        "edit_boundary_established",
        "export_eligible",
        "production_eligible",
        "gate_promotion_claimed",
        "model_winner_claimed",
    ):
        if non_claims.get(required_false_key) is not False:
            raise CoreReportError(
                "REPORT_INVALID_NON_CLAIMS",
                f"non_claims.{required_false_key} must be explicitly False",
            )

    # Validate source section
    source = report.get("source")
    if not isinstance(source, Mapping):
        raise CoreReportError("REPORT_MISSING_SOURCE", "source section must be an object")
    source_locator = _require_non_empty_str(
        source.get("source_locator"), "REPORT_INVALID_SOURCE_LOCATOR", "source.source_locator"
    )
    source_revision_id = _require_non_empty_str(
        source.get("source_revision_id"),
        "REPORT_INVALID_SOURCE_REVISION",
        "source.source_revision_id",
    )
    source_sha256 = _require_hex64(
        source.get("source_sha256"), "REPORT_INVALID_SOURCE_SHA256", "source.source_sha256"
    )
    source_byte_count = source.get("source_byte_count")
    if not _is_non_bool_int(source_byte_count) or source_byte_count <= 0:
        raise CoreReportError(
            "REPORT_INVALID_SOURCE_BYTES",
            "source.source_byte_count must be a positive integer",
        )
    if source.get("custody_state") not in VALID_CUSTODY_STATES:
        raise CoreReportError(
            "REPORT_INVALID_CUSTODY_STATE",
            f"source.custody_state must be one of {sorted(VALID_CUSTODY_STATES)}",
        )

    immutability = source.get("immutability_verified")
    if not isinstance(immutability, Mapping):
        raise CoreReportError(
            "REPORT_INVALID_IMMUTABILITY",
            "source.immutability_verified must be an object",
        )
    if (
        immutability.get("before_analysis") is not True
        or immutability.get("after_analysis") is not True
        or immutability.get("source_sha256_before") != source_sha256
        or immutability.get("source_sha256_after") != source_sha256
        or immutability.get("source_byte_count_before") != source_byte_count
        or immutability.get("source_byte_count_after") != source_byte_count
    ):
        raise CoreReportError(
            "REPORT_SOURCE_MUTATION_OR_UNVERIFIED",
            "source.immutability_verified must confirm identical sha256 and byte count before and after analysis",
        )

    snapshot = source.get("snapshot")
    if snapshot == NOT_OBSERVED:
        if runtime_mode == "REAL":
            raise CoreReportError(
                "REPORT_REAL_SNAPSHOT_REQUIRED",
                "source.snapshot cannot be NOT_OBSERVED when runtime_mode is REAL",
            )
    elif isinstance(snapshot, Mapping):
        _require_non_empty_str(
            snapshot.get("snapshot_id"), "REPORT_INVALID_SNAPSHOT", "source.snapshot.snapshot_id"
        )
        _require_non_empty_str(
            snapshot.get("snapshot_path"),
            "REPORT_INVALID_SNAPSHOT",
            "source.snapshot.snapshot_path",
        )
        snap_sha = snapshot.get("snapshot_sha256", snapshot.get("sha256"))
        if snap_sha != source_sha256:
            raise CoreReportError(
                "REPORT_SNAPSHOT_DIGEST_MISMATCH",
                "source.snapshot digest must match source.source_sha256",
            )
        snap_bytes = snapshot.get("source_byte_count", snapshot.get("byte_count"))
        if snap_bytes != source_byte_count:
            raise CoreReportError(
                "REPORT_SNAPSHOT_BYTE_COUNT_MISMATCH",
                "source.snapshot byte count must match source.source_byte_count",
            )
        if snapshot.get("source_revision_id") != source_revision_id:
            raise CoreReportError(
                "REPORT_SNAPSHOT_REVISION_MISMATCH",
                "source.snapshot.source_revision_id must match source.source_revision_id",
            )
    else:
        raise CoreReportError(
            "REPORT_INVALID_SNAPSHOT",
            "source.snapshot must be an object or NOT_OBSERVED in SYNTHETIC mode",
        )

    probe = source.get("probe")
    if not isinstance(probe, Mapping):
        raise CoreReportError("REPORT_MISSING_PROBE", "source.probe must be an object")
    _require_non_empty_str(
        probe.get("probe_artifact_ref"),
        "REPORT_INVALID_PROBE_REF",
        "source.probe.probe_artifact_ref",
    )
    _require_hex64(
        probe.get("probe_digest"), "REPORT_INVALID_PROBE_DIGEST", "source.probe.probe_digest"
    )
    selected_stream_index = probe.get("selected_stream_index")
    if not _is_non_bool_int(selected_stream_index) or selected_stream_index < 0:
        raise CoreReportError(
            "REPORT_INVALID_STREAM_INDEX",
            "source.probe.selected_stream_index must be a non-negative integer",
        )
    probe_tb = probe.get("timebase")
    if not isinstance(probe_tb, Mapping):
        raise CoreReportError(
            "REPORT_INVALID_TIMEBASE", "source.probe.timebase must be an object"
        )
    tb_num = probe_tb.get("num")
    tb_den = probe_tb.get("den")
    if not _is_non_bool_int(tb_num) or tb_num <= 0 or not _is_non_bool_int(tb_den) or tb_den <= 0:
        raise CoreReportError(
            "REPORT_INVALID_TIMEBASE",
            "source.probe.timebase.num and den must be positive integers",
        )
    if probe.get("time_domain") != "source_pts":
        raise CoreReportError(
            "REPORT_INVALID_PROBE_TIME_DOMAIN",
            "source.probe.time_domain must be 'source_pts'",
        )
    if probe.get("evidence_class") != "MEASURED":
        raise CoreReportError(
            "REPORT_INVALID_PROBE_EVIDENCE_CLASS",
            "source.probe.evidence_class must be 'MEASURED'",
        )
    _require_non_empty_str(
        probe.get("measurement_provenance"),
        "REPORT_INVALID_PROBE_PROVENANCE",
        "source.probe.measurement_provenance",
    )

    # Validate authority section
    authority = report.get("authority")
    if not isinstance(authority, Mapping):
        raise CoreReportError("REPORT_MISSING_AUTHORITY", "authority must be an object")
    auth_mode = authority.get("authorization_mode")
    if auth_mode not in VALID_AUTHORIZATION_MODES:
        raise CoreReportError(
            "REPORT_INVALID_AUTHORIZATION_MODE",
            f"authority.authorization_mode must be one of {sorted(VALID_AUTHORIZATION_MODES)}",
        )
    if authority.get("local_only") is not True:
        raise CoreReportError(
            "REPORT_INVALID_LOCAL_ONLY", "authority.local_only must be True"
        )
    if authority.get("development_source_auth_enforcement") != "DISABLED_BY_OWNER":
        raise CoreReportError(
            "REPORT_INVALID_DEV_SOURCE_AUTH_STATE",
            "authority.development_source_auth_enforcement must be 'DISABLED_BY_OWNER'",
        )
    if runtime_mode == "REAL":
        if auth_mode != "OWNER_PILOT_AUTHORIZATION":
            raise CoreReportError(
                "REPORT_REAL_AUTHORIZATION_REQUIRED",
                "REAL runtime_mode requires OWNER_PILOT_AUTHORIZATION",
            )
        auth_id = _require_non_empty_str(
            authority.get("authorization_id"),
            "REPORT_INVALID_AUTHORIZATION_ID",
            "authority.authorization_id",
        )
        if auth_id == NOT_OBSERVED:
            raise CoreReportError(
                "REPORT_REAL_AUTHORIZATION_REQUIRED",
                "authority.authorization_id cannot be NOT_OBSERVED in REAL mode",
            )
        _require_hex64(
            authority.get("authorization_record_digest"),
            "REPORT_INVALID_AUTH_RECORD_DIGEST",
            "authority.authorization_record_digest",
        )
        _require_hex64(
            authority.get("policy_digest"),
            "REPORT_INVALID_POLICY_DIGEST",
            "authority.policy_digest",
        )
        _require_hex64(
            authority.get("scope_digest"),
            "REPORT_INVALID_SCOPE_DIGEST",
            "authority.scope_digest",
        )
    else:
        _require_non_empty_str(
            authority.get("authorization_id"),
            "REPORT_INVALID_AUTHORIZATION_ID",
            "authority.authorization_id",
        )
        for digest_key in ("authorization_record_digest", "policy_digest", "scope_digest"):
            digest_val = authority.get(digest_key)
            if digest_val != NOT_OBSERVED:
                _require_hex64(
                    digest_val,
                    "REPORT_INVALID_AUTHORITY_DIGEST",
                    f"authority.{digest_key}",
                )

    # Validate model section
    model = report.get("model")
    if not isinstance(model, Mapping):
        raise CoreReportError("REPORT_MISSING_MODEL", "model section must be an object")
    model_family = _require_non_empty_str(
        model.get("model_family"), "REPORT_INVALID_MODEL_FAMILY", "model.model_family"
    )
    model_identity = _require_non_empty_str(
        model.get("model_identity"), "REPORT_INVALID_MODEL_IDENTITY", "model.model_identity"
    )
    _require_non_empty_str(
        model.get("frozen_revision"), "REPORT_INVALID_MODEL_REVISION", "model.frozen_revision"
    )
    _require_hex64(
        model.get("weights_sha256"), "REPORT_INVALID_WEIGHTS_SHA256", "model.weights_sha256"
    )
    _require_hex64(
        model.get("processor_digest"), "REPORT_INVALID_PROCESSOR_DIGEST", "model.processor_digest"
    )
    _require_hex64(
        model.get("image_preprocessing_digest"),
        "REPORT_INVALID_IMAGE_PREPROC_DIGEST",
        "model.image_preprocessing_digest",
    )
    _require_non_empty_str(
        model.get("text_preprocessing_contract"),
        "REPORT_INVALID_TEXT_CONTRACT",
        "model.text_preprocessing_contract",
    )
    embedding_dim = model.get("embedding_dim")
    if not _is_non_bool_int(embedding_dim) or embedding_dim <= 0:
        raise CoreReportError(
            "REPORT_INVALID_EMBEDDING_DIM",
            "model.embedding_dim must be a positive integer",
        )
    if model.get("dtype") != "float32":
        raise CoreReportError("REPORT_INVALID_DTYPE", "model.dtype must be 'float32'")
    if model.get("normalization") != "l2":
        raise CoreReportError(
            "REPORT_INVALID_NORMALIZATION", "model.normalization must be 'l2'"
        )
    model_space_id = _require_hex64(
        model.get("semantic_space_id"),
        "REPORT_INVALID_SEMANTIC_SPACE_ID",
        "model.semantic_space_id",
    )
    runtime_identity = _require_non_empty_str(
        model.get("runtime_identity"),
        "REPORT_INVALID_RUNTIME_IDENTITY",
        "model.runtime_identity",
    )
    if model.get("runtime_mode") != runtime_mode:
        raise CoreReportError(
            "REPORT_MODEL_RUNTIME_MODE_MISMATCH",
            "model.runtime_mode must match top-level runtime_mode",
        )
    is_fake_marker = any(
        "fake" in token.lower() or "synthetic" in token.lower()
        for token in (runtime_identity, model_family, model_identity)
    )
    if is_fake_marker and runtime_mode == "REAL":
        raise CoreReportError(
            "REPORT_FAKE_EMBEDDER_MISLABELED_AS_REAL",
            "Fake/synthetic embedder evidence must never be labeled as REAL runtime_mode",
        )
    authentic_observed = model.get("authentic_inference_observed")
    if not isinstance(authentic_observed, bool):
        raise CoreReportError(
            "REPORT_AUTHENTIC_INFERENCE_FLAG_MISMATCH",
            "model.authentic_inference_observed must be a boolean backed by runtime evidence",
        )
    if authentic_observed and runtime_mode != "REAL":
        raise CoreReportError(
            "REPORT_AUTHENTIC_INFERENCE_FLAG_MISMATCH",
            "Synthetic runtime cannot report authentic model inference",
        )
    evidence_availability = report.get("evidence_availability")
    if isinstance(evidence_availability, Mapping):
        expected_inference_availability = OBSERVED if authentic_observed else NOT_OBSERVED
        if evidence_availability.get("authentic_model_inference") != expected_inference_availability:
            raise CoreReportError(
                "REPORT_AUTHENTIC_INFERENCE_EVIDENCE_MISMATCH",
                "Authentic model inference availability must match observed runtime evidence",
            )

    # Validate index section
    index = report.get("index")
    if not isinstance(index, Mapping):
        raise CoreReportError("REPORT_MISSING_INDEX", "index section must be an object")
    _require_non_empty_str(
        index.get("generation_id"), "REPORT_INVALID_GENERATION_ID", "index.generation_id"
    )
    index_space_id = _require_hex64(
        index.get("semantic_space_id"),
        "REPORT_INVALID_INDEX_SPACE_ID",
        "index.semantic_space_id",
    )
    if index_space_id != model_space_id:
        raise CoreReportError(
            "REPORT_SEMANTIC_SPACE_MISMATCH",
            "index.semantic_space_id must equal model.semantic_space_id",
        )
    if index.get("index_disposition") not in VALID_INDEX_DISPOSITIONS:
        raise CoreReportError(
            "REPORT_INVALID_INDEX_DISPOSITION",
            f"index.index_disposition must be one of {sorted(VALID_INDEX_DISPOSITIONS)}",
        )
    manifest_digest = index.get("manifest_digest")
    if manifest_digest != NOT_OBSERVED:
        _require_hex64(
            manifest_digest, "REPORT_INVALID_MANIFEST_DIGEST", "index.manifest_digest"
        )
    committed_rows = index.get("committed_row_count")
    source_samples = index.get("source_sample_count")
    if not _is_non_bool_int(committed_rows) or committed_rows < 0:
        raise CoreReportError(
            "REPORT_INVALID_COMMITTED_ROWS",
            "index.committed_row_count must be a non-negative integer",
        )
    if not _is_non_bool_int(source_samples) or source_samples < 0:
        raise CoreReportError(
            "REPORT_INVALID_SOURCE_SAMPLES",
            "index.source_sample_count must be a non-negative integer",
        )
    if index.get("single_source_scope_verified") is not True:
        raise CoreReportError(
            "REPORT_SINGLE_SOURCE_SCOPE_UNVERIFIED",
            "index.single_source_scope_verified must be True",
        )
    sampling_policy = index.get("sampling_policy")
    if not isinstance(sampling_policy, Mapping):
        raise CoreReportError(
            "REPORT_INVALID_SAMPLING_POLICY", "index.sampling_policy must be an object"
        )
    _require_non_empty_str(
        sampling_policy.get("sampling_policy_id"),
        "REPORT_INVALID_SAMPLING_POLICY",
        "index.sampling_policy.sampling_policy_id",
    )
    sp_ver = sampling_policy.get("sampling_policy_version")
    if not _is_non_bool_int(sp_ver) or sp_ver < 1:
        raise CoreReportError(
            "REPORT_INVALID_SAMPLING_POLICY",
            "index.sampling_policy.sampling_policy_version must be a positive integer",
        )
    sp_interval = sampling_policy.get("sampling_interval_seconds")
    if (
        not isinstance(sp_interval, (int, float))
        or isinstance(sp_interval, bool)
        or not math.isfinite(float(sp_interval))
        or float(sp_interval) <= 0.0
    ):
        raise CoreReportError(
            "REPORT_INVALID_SAMPLING_INTERVAL",
            "index.sampling_policy.sampling_interval_seconds must be a positive finite number",
        )
    _require_non_empty_str(
        sampling_policy.get("selected_stream_policy"),
        "REPORT_INVALID_STREAM_POLICY",
        "index.sampling_policy.selected_stream_policy",
    )
    if sampling_policy.get("selected_stream_index") != selected_stream_index:
        raise CoreReportError(
            "REPORT_INDEX_STREAM_MISMATCH",
            "index.sampling_policy.selected_stream_index must match source.probe.selected_stream_index",
        )

    # Validate query section
    query = report.get("query")
    if not isinstance(query, Mapping):
        raise CoreReportError("REPORT_MISSING_QUERY", "query section must be an object")
    _require_non_empty_str(query.get("query_id"), "REPORT_INVALID_QUERY_ID", "query.query_id")
    _require_non_empty_str(query.get("raw_text"), "REPORT_INVALID_QUERY_TEXT", "query.raw_text")
    normalized_text = _require_non_empty_str(
        query.get("normalized_text"), "REPORT_INVALID_QUERY_TEXT", "query.normalized_text"
    )
    query_digest = _require_hex64(
        query.get("query_digest"), "REPORT_INVALID_QUERY_DIGEST", "query.query_digest"
    )
    expected_query_digest = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
    if query_digest != expected_query_digest:
        raise CoreReportError(
            "REPORT_QUERY_DIGEST_MISMATCH",
            "query.query_digest does not match SHA-256 of query.normalized_text",
        )
    if query.get("modality") != "text":
        raise CoreReportError("REPORT_INVALID_QUERY_MODALITY", "query.modality must be 'text'")
    if (
        query.get("score_interpretation")
        != "uncalibrated_cosine_similarity_not_probability"
    ):
        raise CoreReportError(
            "REPORT_INVALID_SCORE_INTERPRETATION",
            "query.score_interpretation must be 'uncalibrated_cosine_similarity_not_probability'",
        )

    # Validate matches section
    matches = report.get("matches")
    if not isinstance(matches, list):
        raise CoreReportError("REPORT_INVALID_MATCHES", "matches must be a list")
    if len(matches) != returned_count:
        raise CoreReportError(
            "REPORT_MATCH_COUNT_MISMATCH",
            "len(matches) must equal returned_candidate_count",
        )

    if stage_status == "SUCCEEDED":
        if errors:
            raise CoreReportError(
                "REPORT_SUCCEEDED_WITH_ERRORS",
                "SUCCEEDED report cannot contain error codes",
            )
        if returned_count == 0 and result_kind != "ZERO_MATCH":
            raise CoreReportError(
                "REPORT_ZERO_MATCH_RESULT_KIND_MISMATCH",
                "Zero returned matches on SUCCEEDED report must have result_kind == 'ZERO_MATCH'",
            )
        if returned_count == 0 and total_eligible != 0:
            raise CoreReportError(
                "REPORT_ZERO_MATCH_ELIGIBLE_MISMATCH",
                "ZERO_MATCH report must have total_eligible_matches == 0",
            )
        if returned_count > 0 and result_kind != "MATCHES_FOUND":
            raise CoreReportError(
                "REPORT_MATCHES_FOUND_RESULT_KIND_MISMATCH",
                "Positive returned matches on SUCCEEDED report must have result_kind == 'MATCHES_FOUND'",
            )

    prev_score: float | None = None
    prev_tie_key: tuple[int, int] | None = None
    seen_row_ids: set[int] = set()

    for idx, match in enumerate(matches, start=1):
        if not isinstance(match, Mapping):
            raise CoreReportError("REPORT_INVALID_MATCH_ITEM", f"matches[{idx - 1}] must be an object")
        _require_non_empty_str(
            match.get("candidate_id"),
            "REPORT_INVALID_CANDIDATE_ID",
            f"matches[{idx - 1}].candidate_id",
        )
        row_id = match.get("row_id")
        if not _is_non_bool_int(row_id) or row_id < 0:
            raise CoreReportError(
                "REPORT_INVALID_ROW_ID",
                f"matches[{idx - 1}].row_id must be a non-negative integer",
            )
        if row_id in seen_row_ids:
            raise CoreReportError(
                "REPORT_DUPLICATE_MATCH_ROW_ID",
                f"Duplicate row_id {row_id} in matches",
            )
        seen_row_ids.add(row_id)

        rank = match.get("rank")
        if not _is_non_bool_int(rank) or rank != idx:
            raise CoreReportError(
                "REPORT_INVALID_MATCH_RANK",
                f"matches[{idx - 1}].rank must be {idx}",
            )

        score = match.get("score")
        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not math.isfinite(float(score))
        ):
            raise CoreReportError(
                "REPORT_INVALID_MATCH_SCORE",
                f"matches[{idx - 1}].score must be a finite number",
            )
        score_f = float(score)
        if match.get("score_is_probability") is not False:
            raise CoreReportError(
                "REPORT_SCORE_PROBABILITY_CLAIM_FORBIDDEN",
                f"matches[{idx - 1}].score_is_probability must be False",
            )

        if match.get("source_sha256") != source_sha256:
            raise CoreReportError(
                "REPORT_MATCH_SOURCE_SHA256_MISMATCH",
                f"matches[{idx - 1}].source_sha256 must match source.source_sha256",
            )
        if match.get("source_revision_id") != source_revision_id:
            raise CoreReportError(
                "REPORT_MATCH_SOURCE_REVISION_MISMATCH",
                f"matches[{idx - 1}].source_revision_id must match source.source_revision_id",
            )
        if match.get("source_locator") != source_locator:
            raise CoreReportError(
                "REPORT_MATCH_SOURCE_LOCATOR_MISMATCH",
                f"matches[{idx - 1}].source_locator must match source.source_locator",
            )
        if match.get("selected_stream_index") != selected_stream_index:
            raise CoreReportError(
                "REPORT_MATCH_STREAM_INDEX_MISMATCH",
                f"matches[{idx - 1}].selected_stream_index must match source.probe.selected_stream_index",
            )

        # Sampled timing validation
        timing = match.get("sampled_timing")
        if not isinstance(timing, Mapping):
            raise CoreReportError(
                "REPORT_INVALID_SAMPLED_TIMING",
                f"matches[{idx - 1}].sampled_timing must be an object",
            )
        pts = timing.get("pts")
        if not _is_non_bool_int(pts) or pts < 0:
            raise CoreReportError(
                "REPORT_INVALID_PTS",
                f"matches[{idx - 1}].sampled_timing.pts must be a non-negative integer",
            )
        timing_tb = timing.get("timebase")
        if (
            not isinstance(timing_tb, Mapping)
            or timing_tb.get("num") != tb_num
            or timing_tb.get("den") != tb_den
        ):
            raise CoreReportError(
                "REPORT_MATCH_TIMEBASE_MISMATCH",
                f"matches[{idx - 1}].sampled_timing.timebase must match source.probe.timebase",
            )
        if timing.get("time_domain") != "source_pts":
            raise CoreReportError(
                "REPORT_INVALID_TIMING_DOMAIN",
                f"matches[{idx - 1}].sampled_timing.time_domain must be 'source_pts'",
            )
        expected_rational = format_rational_seconds(pts, tb_num, tb_den)
        if timing.get("rational_seconds") != expected_rational:
            raise CoreReportError(
                "REPORT_INVALID_RATIONAL_SECONDS",
                f"matches[{idx - 1}].sampled_timing.rational_seconds does not match exact PTS * timebase",
            )
        _require_non_empty_str(
            timing.get("display_timestamp"),
            "REPORT_INVALID_DISPLAY_TIMESTAMP",
            f"matches[{idx - 1}].sampled_timing.display_timestamp",
        )
        if timing.get("display_only_not_frame_authority") is not True:
            raise CoreReportError(
                "REPORT_DISPLAY_TIMESTAMP_AUTHORITY_FORBIDDEN",
                f"matches[{idx - 1}].sampled_timing.display_only_not_frame_authority must be True",
            )
        if timing.get("evidence_class") != "MEASURED":
            raise CoreReportError(
                "REPORT_INVALID_TIMING_EVIDENCE_CLASS",
                f"matches[{idx - 1}].sampled_timing.evidence_class must be 'MEASURED'",
            )
        _require_non_empty_str(
            timing.get("measurement_provenance"),
            "REPORT_INVALID_TIMING_PROVENANCE",
            f"matches[{idx - 1}].sampled_timing.measurement_provenance",
        )
        if timing.get("is_event_boundary") is not False or timing.get("is_edit_boundary") is not False:
            raise CoreReportError(
                "REPORT_SAMPLE_BOUNDARY_CLAIM_FORBIDDEN",
                f"matches[{idx - 1}].sampled_timing cannot claim event or edit boundary authority",
            )

        # Ordering check
        if prev_score is not None:
            if score_f > prev_score:
                raise CoreReportError(
                    "REPORT_MATCHES_NOT_SORTED",
                    "matches must be ordered by non-increasing score",
                )
            if score_f == prev_score and prev_tie_key is not None:
                if (pts, row_id) < prev_tie_key:
                    raise CoreReportError(
                        "REPORT_MATCHES_TIE_BREAK_INVALID",
                        "Tied scores must be deterministically ordered by (pts, row_id)",
                    )
        prev_score = score_f
        prev_tie_key = (pts, row_id)

        # Approximate semantic location validation
        loc = match.get("approx_semantic_location")
        if not isinstance(loc, Mapping):
            raise CoreReportError(
                "REPORT_INVALID_SEMANTIC_LOCATION",
                f"matches[{idx - 1}].approx_semantic_location must be an object",
            )
        if loc.get("time_domain") != "semantic_seconds":
            raise CoreReportError(
                "REPORT_INVALID_SEMANTIC_LOCATION_DOMAIN",
                f"matches[{idx - 1}].approx_semantic_location.time_domain must be 'semantic_seconds'",
            )
        loc_kind = loc.get("location_kind")
        if loc_kind == "POINT":
            for forbidden_interval_key in ("start_seconds", "end_seconds", "start", "end"):
                if forbidden_interval_key in loc:
                    raise CoreReportError(
                        "REPORT_POINT_LOCATION_HAS_INTERVAL_BOUNDS",
                        f"POINT semantic location must not encode interval field {forbidden_interval_key!r}",
                    )
            if loc.get("window_width_seconds") != NOT_OBSERVED:
                raise CoreReportError(
                    "REPORT_POINT_WINDOW_WIDTH_MUST_BE_NOT_OBSERVED",
                    "POINT semantic location must set window_width_seconds to NOT_OBSERVED",
                )
            if loc.get("rational_seconds") != expected_rational:
                raise CoreReportError(
                    "REPORT_POINT_RATIONAL_SECONDS_MISMATCH",
                    "POINT semantic location rational_seconds must match sampled_timing.rational_seconds",
                )
            pos_sec = loc.get("position_seconds")
            if (
                not isinstance(pos_sec, (int, float))
                or isinstance(pos_sec, bool)
                or not math.isfinite(float(pos_sec))
                or float(pos_sec) < 0.0
            ):
                raise CoreReportError(
                    "REPORT_INVALID_POINT_POSITION",
                    "POINT position_seconds must be a non-negative finite number",
                )
        elif loc_kind == "COARSE_WINDOW":
            start_s = loc.get("start_seconds")
            end_s = loc.get("end_seconds")
            width_s = loc.get("window_width_seconds")
            if (
                not isinstance(start_s, (int, float))
                or not isinstance(end_s, (int, float))
                or not isinstance(width_s, (int, float))
                or isinstance(start_s, bool)
                or isinstance(end_s, bool)
                or isinstance(width_s, bool)
                or float(end_s) <= float(start_s)
                or float(width_s) <= 0.0
            ):
                raise CoreReportError(
                    "REPORT_INVALID_COARSE_WINDOW",
                    "COARSE_WINDOW requires start_seconds < end_seconds and positive window_width_seconds",
                )
            _require_non_empty_str(
                loc.get("window_provenance"),
                "REPORT_MISSING_WINDOW_PROVENANCE",
                f"matches[{idx - 1}].approx_semantic_location.window_provenance",
            )
        else:
            raise CoreReportError(
                "REPORT_INVALID_SEMANTIC_LOCATION_KIND",
                f"matches[{idx - 1}].approx_semantic_location.location_kind must be POINT or COARSE_WINDOW",
            )

        # Semantic assertion validation
        assertion = match.get("semantic_assertion")
        if not isinstance(assertion, Mapping):
            raise CoreReportError(
                "REPORT_INVALID_SEMANTIC_ASSERTION",
                f"matches[{idx - 1}].semantic_assertion must be an object",
            )
        ev_class = assertion.get("evidence_class")
        if ev_class not in APPROVED_EVIDENCE_CLASSES:
            raise CoreReportError(
                "REPORT_INVALID_EVIDENCE_CLASS",
                f"Invalid evidence_class {ev_class!r}; NOT_OBSERVED is not an evidence class",
            )
        if ev_class != "MATCHED":
            raise CoreReportError(
                "REPORT_SEMANTIC_ASSERTION_MUST_BE_MATCHED",
                "semantic_assertion.evidence_class must be 'MATCHED'",
            )
        if assertion.get("binding_eligible") is not False:
            raise CoreReportError(
                "REPORT_SEMANTIC_BINDING_ELIGIBLE_FORBIDDEN",
                "semantic_assertion.binding_eligible must be False",
            )
        if assertion.get("assertion_kind") != "query_visual_similarity_candidate":
            raise CoreReportError(
                "REPORT_INVALID_ASSERTION_KIND",
                "semantic_assertion.assertion_kind must be 'query_visual_similarity_candidate'",
            )
        if assertion.get("caption_claim") != NOT_OBSERVED:
            raise CoreReportError(
                "REPORT_CAPTION_CLAIM_FORBIDDEN",
                "semantic_assertion.caption_claim must be NOT_OBSERVED",
            )

        # Measured frame interval validation
        interval = match.get("measured_frame_interval")
        if interval != NOT_OBSERVED:
            if not isinstance(interval, Mapping):
                raise CoreReportError(
                    "REPORT_INVALID_MEASURED_INTERVAL",
                    "measured_frame_interval must be NOT_OBSERVED or a validated interval object",
                )
            if interval.get("evidence_class") != "MEASURED":
                raise CoreReportError(
                    "REPORT_INTERVAL_EVIDENCE_MUST_BE_MEASURED",
                    "measured_frame_interval.evidence_class must be 'MEASURED'",
                )
            if interval.get("time_domain") != "source_pts":
                raise CoreReportError(
                    "REPORT_INTERVAL_DOMAIN_MUST_BE_SOURCE_PTS",
                    "measured_frame_interval.time_domain must be 'source_pts'",
                )
            start_pts = interval.get("start_pts")
            end_pts = interval.get("end_pts")
            if (
                not _is_non_bool_int(start_pts)
                or not _is_non_bool_int(end_pts)
                or start_pts < 0
                or end_pts <= start_pts
            ):
                raise CoreReportError(
                    "REPORT_INVALID_INTERVAL_PTS",
                    "measured_frame_interval requires 0 <= start_pts < end_pts",
                )
            if interval.get("timebase") != {"num": tb_num, "den": tb_den}:
                raise CoreReportError(
                    "REPORT_INTERVAL_TIMEBASE_MISMATCH",
                    "measured_frame_interval.timebase must match source.probe.timebase",
                )
            _require_non_empty_str(
                interval.get("refinement_artifact_ref"),
                "REPORT_MISSING_REFINEMENT_REF",
                "measured_frame_interval.refinement_artifact_ref",
            )
            _require_hex64(
                interval.get("refinement_digest"),
                "REPORT_INVALID_REFINEMENT_DIGEST",
                "measured_frame_interval.refinement_digest",
            )

        # Thumbnail validation
        thumb = match.get("thumbnail")
        if not isinstance(thumb, Mapping):
            raise CoreReportError(
                "REPORT_INVALID_THUMBNAIL",
                f"matches[{idx - 1}].thumbnail must be an object",
            )
        thumb_status = thumb.get("status")
        if thumb_status not in VALID_THUMBNAIL_STATUSES:
            raise CoreReportError(
                "REPORT_INVALID_THUMBNAIL_STATUS",
                f"thumbnail.status must be one of {sorted(VALID_THUMBNAIL_STATUSES)}",
            )
        thumb_path = thumb.get("path")
        if thumb_status == "PRESENT":
            _require_non_empty_str(
                thumb_path,
                "REPORT_MISSING_THUMBNAIL_PATH",
                f"matches[{idx - 1}].thumbnail.path",
            )
        elif thumb_path is not None and not isinstance(thumb_path, str):
            raise CoreReportError(
                "REPORT_INVALID_THUMBNAIL_PATH",
                f"matches[{idx - 1}].thumbnail.path must be string or None",
            )

    # Validate artifact section and self-digest
    artifact = report.get("artifact")
    if not isinstance(artifact, Mapping):
        raise CoreReportError("REPORT_MISSING_ARTIFACT", "artifact section must be an object")
    _require_non_empty_str(
        artifact.get("report_path"), "REPORT_INVALID_ARTIFACT_PATH", "artifact.report_path"
    )
    _require_non_empty_str(
        artifact.get("output_root"), "REPORT_INVALID_OUTPUT_ROOT", "artifact.output_root"
    )
    if artifact.get("schema_valid") is not True:
        raise CoreReportError(
            "REPORT_SCHEMA_VALID_MUST_BE_TRUE", "artifact.schema_valid must be True"
        )
    recorded_digest = _require_hex64(
        artifact.get("report_digest"),
        "REPORT_INVALID_REPORT_DIGEST",
        "artifact.report_digest",
    )
    expected_digest = compute_core_report_digest(report)
    if recorded_digest != expected_digest:
        raise CoreReportError(
            "REPORT_DIGEST_MISMATCH",
            f"artifact.report_digest {recorded_digest} does not match computed digest {expected_digest}",
        )

    # Secret scan over serialized form
    serialized = json.dumps(dict(report), sort_keys=True, ensure_ascii=False)
    for pattern in _SECRET_PATTERNS:
        if pattern.search(serialized):
            raise CoreReportError(
                "REPORT_SECRET_MATERIAL_FORBIDDEN",
                "Report contains forbidden secret/token pattern",
            )


def serialize_core_semantic_report(report: Mapping[str, Any]) -> str:
    """Validate and serialize Report V1 as canonical pretty JSON with trailing newline."""
    validate_core_semantic_report(report)
    return json.dumps(dict(report), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def publish_core_semantic_report(
    report: Mapping[str, Any],
    report_path: str | Path,
    *,
    output_root: str | Path,
) -> Path:
    """Atomically publish a validated Report V1 inside output_root without clobbering."""
    validate_core_semantic_report(report)
    resolved_root, resolved_report = validate_output_target_path(
        report_path, output_root=output_root, require_nonexistent=True
    )

    serialized_bytes = serialize_core_semantic_report(report).encode("utf-8")
    parent_dir = resolved_report.parent
    parent_dir.mkdir(parents=True, exist_ok=True)

    # Re-verify no symlink was introduced in the created hierarchy
    validate_output_target_path(
        resolved_report, output_root=resolved_root, require_nonexistent=True
    )

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{resolved_report.name}.tmp.",
        dir=str(parent_dir),
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(serialized_bytes)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp_path, resolved_report)
        except FileExistsError as exc:
            raise CoreReportPublicationError(
                "OUTPUT_ALREADY_EXISTS",
                f"Refusing to overwrite existing report path: {resolved_report}",
            ) from exc
    finally:
        try:
            if temp_path.exists() or temp_path.is_symlink():
                temp_path.unlink()
        except OSError:
            pass

    try:
        dir_fd = os.open(str(parent_dir), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        pass

    return resolved_report
