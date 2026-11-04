"""Deterministic report builder and self-contained verifier for synthetic batches.

Authority: VIP-LAB-MEGA-02 Workstream W5.

Produces and verifies canonical JSON report payloads for single-arm and
three-arm synthetic batch runs. Never writes media, never mutates an index,
never opens or resolves source paths, and enforces closed non-production claim
banners (`status="SYNTHETIC_ONLY"`, `benchmark_status="NOT_RUN"`,
`model_evidence="NOT_OBSERVED"`, `gate_decision="NOT_AUTHORIZED"`).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any, Mapping, Sequence

from .batch_retrieval import BatchQueryResult, SingleArmBatchResult
from .query_batch import (
    MAX_QUERY_COUNT,
    MIN_QUERY_COUNT,
    validate_lab_top_k,
)
from .three_arm_batch import (
    ARM_TO_PROFILE_ID,
    DECLARED_ARM_ORDER,
    PROFILE_ID_TO_ARM,
    ThreeArmBatchArmResult,
    ThreeArmBatchResult,
)

BATCH_REPORT_SCHEMA_VERSION = "vip-lab-batch-report-v1"
KIND_SINGLE_ARM = "SINGLE_ARM_SYNTHETIC_BATCH"
KIND_THREE_ARM = "THREE_ARM_SYNTHETIC_BATCH"

REPORT_STATUS_SYNTHETIC_ONLY = "SYNTHETIC_ONLY"
BENCHMARK_STATUS_NOT_RUN = "NOT_RUN"
MODEL_EVIDENCE_NOT_OBSERVED = "NOT_OBSERVED"
GATE_DECISION_NOT_AUTHORIZED = "NOT_AUTHORIZED"

REPORT_LIMITATIONS: tuple[str, ...] = (
    "NO_AUTHENTIC_MODEL_INFERENCE",
    "NO_REAL_SOURCE_MEDIA",
    "NO_HUMAN_LABELS",
    "NO_CROSS_ARM_WINNER",
    "NO_GATE_PROMOTION",
)

_LOWER_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_HEX64_ANY_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

_REPORT_TOP_FIELDS = frozenset({
    "schema_version",
    "kind",
    "status",
    "benchmark_status",
    "model_evidence",
    "gate_decision",
    "synthetic_only",
    "authentic_model_evidence",
    "cross_arm_winner",
    "catalog_id",
    "catalog_digest",
    "query_ids",
    "top_k",
    "limitations",
    "arms",
    "report_digest",
})

_ARM_RECORD_FIELDS = frozenset({
    "arm_id",
    "profile_id",
    "model_identity",
    "space_id",
    "generation_id",
    "embedding_dim",
    "row_width_bytes",
    "manifest_digest",
    "catalog_digest",
    "query_count",
    "candidate_count",
    "fake_runtime_used",
    "synthetic_only",
    "authentic_model_evidence",
    "queries",
})

_QUERY_RECORD_FIELDS = frozenset({
    "query_id",
    "query_text",
    "candidate_count",
    "candidates",
})

_CANDIDATE_RECORD_FIELDS = frozenset({
    "arm_id",
    "query_id",
    "query",
    "rank",
    "score",
    "revision_id",
    "content_id",
    "source_path",
    "source_sha256",
    "generation_id",
    "space_id",
    "source_sample_pts",
    "source_timebase_num",
    "source_timebase_den",
    "timestamp_human",
    "thumbnail_path",
    "thumbnail_status",
    "evidence_class",
    "binding_eligible",
})

_FORBIDDEN_EDIT_BOUNDARY_FIELDS = frozenset({
    "source_pts_interval",
    "frame_accurate_boundary",
    "editorial_decision",
    "edit_boundary",
    "start_frame",
    "end_frame",
    "start_pts",
    "end_pts",
    "cut_in",
    "cut_out",
})

_EXPECTED_PROFILE_GEOMETRY: Mapping[str, tuple[str, int, int]] = {
    "vip-v1-siglip-base-224": ("google/siglip-base-patch16-224", 768, 3072),
    "vip-v2-siglip2-base-224": ("google/siglip2-base-patch16-224", 768, 3072),
    "vip-v2-siglip2-so400m-384": ("google/siglip2-so400m-patch14-384", 1152, 4608),
}


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    try:
        text = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("BATCH_REPORT_CANONICALIZATION_FAILED") from exc
    return text.encode("utf-8")


def compute_batch_report_digest(report_without_digest: Mapping[str, Any]) -> str:
    """Compute the deterministic SHA-256 digest of a report body excluding ``report_digest``."""
    body = {k: v for k, v in report_without_digest.items() if k != "report_digest"}
    return hashlib.sha256(_canonical_json_bytes(body)).hexdigest()


def serialize_batch_report(report: Mapping[str, Any]) -> str:
    """Verify and serialize a batch report to canonical compact JSON text."""
    verified = verify_batch_report(report)
    return _canonical_json_bytes(verified).decode("utf-8")


def _serialize_query_results(
    arm_id: str,
    query_results: Sequence[BatchQueryResult],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for qr in query_results:
        rows.append({
            "query_id": qr.query_id,
            "query_text": qr.query_text,
            "candidate_count": qr.candidate_count,
            "candidates": [cand.to_dict(arm_id=arm_id) for cand in qr.candidates],
        })
    return rows


def _build_arm_dict_from_single(
    arm_id: str,
    batch_result: SingleArmBatchResult,
) -> dict[str, Any]:
    return {
        "arm_id": arm_id,
        "profile_id": batch_result.profile_id,
        "model_identity": batch_result.model_identity,
        "space_id": batch_result.space_id,
        "generation_id": batch_result.generation_id,
        "embedding_dim": batch_result.embedding_dim,
        "row_width_bytes": batch_result.row_width_bytes,
        "manifest_digest": batch_result.manifest_digest,
        "catalog_digest": batch_result.catalog_digest,
        "query_count": len(batch_result.query_ids),
        "candidate_count": batch_result.total_candidate_count,
        "fake_runtime_used": True,
        "synthetic_only": True,
        "authentic_model_evidence": False,
        "queries": _serialize_query_results(arm_id, batch_result.query_results),
    }


def _build_arm_dict_from_three_arm(arm: ThreeArmBatchArmResult) -> dict[str, Any]:
    return {
        "arm_id": arm.arm_id,
        "profile_id": arm.profile_id,
        "model_identity": arm.model_identity,
        "space_id": arm.space_id,
        "generation_id": arm.generation_id,
        "embedding_dim": arm.embedding_dim,
        "row_width_bytes": arm.row_width_bytes,
        "manifest_digest": arm.manifest_digest,
        "catalog_digest": arm.catalog_digest,
        "query_count": arm.query_count,
        "candidate_count": arm.candidate_count,
        "fake_runtime_used": True,
        "synthetic_only": True,
        "authentic_model_evidence": False,
        "queries": _serialize_query_results(arm.arm_id, arm.batch_result.query_results),
    }


def build_single_arm_batch_report(
    result: SingleArmBatchResult,
    *,
    arm_id: str | None = None,
) -> dict[str, Any]:
    """Construct and self-verify a canonical single-arm synthetic batch report."""
    if not isinstance(result, SingleArmBatchResult):
        raise TypeError("SINGLE_ARM_BATCH_RESULT_REQUIRED")
    resolved_arm_id = arm_id if arm_id is not None else PROFILE_ID_TO_ARM.get(result.profile_id)
    if resolved_arm_id is None or ARM_TO_PROFILE_ID.get(resolved_arm_id) != result.profile_id:
        raise ValueError(f"BATCH_REPORT_ARM_PROFILE_MISMATCH:{resolved_arm_id}:{result.profile_id}")

    body: dict[str, Any] = {
        "schema_version": BATCH_REPORT_SCHEMA_VERSION,
        "kind": KIND_SINGLE_ARM,
        "status": REPORT_STATUS_SYNTHETIC_ONLY,
        "benchmark_status": BENCHMARK_STATUS_NOT_RUN,
        "model_evidence": MODEL_EVIDENCE_NOT_OBSERVED,
        "gate_decision": GATE_DECISION_NOT_AUTHORIZED,
        "synthetic_only": True,
        "authentic_model_evidence": False,
        "cross_arm_winner": None,
        "catalog_id": result.catalog_id,
        "catalog_digest": result.catalog_digest,
        "query_ids": list(result.query_ids),
        "top_k": result.top_k,
        "limitations": list(REPORT_LIMITATIONS),
        "arms": [_build_arm_dict_from_single(resolved_arm_id, result)],
    }
    body["report_digest"] = compute_batch_report_digest(body)
    return verify_batch_report(body)


def build_three_arm_batch_report(result: ThreeArmBatchResult) -> dict[str, Any]:
    """Construct and self-verify a canonical three-arm synthetic batch report."""
    if not isinstance(result, ThreeArmBatchResult):
        raise TypeError("THREE_ARM_BATCH_RESULT_REQUIRED")

    body: dict[str, Any] = {
        "schema_version": BATCH_REPORT_SCHEMA_VERSION,
        "kind": KIND_THREE_ARM,
        "status": REPORT_STATUS_SYNTHETIC_ONLY,
        "benchmark_status": BENCHMARK_STATUS_NOT_RUN,
        "model_evidence": MODEL_EVIDENCE_NOT_OBSERVED,
        "gate_decision": GATE_DECISION_NOT_AUTHORIZED,
        "synthetic_only": True,
        "authentic_model_evidence": False,
        "cross_arm_winner": None,
        "catalog_id": result.catalog_id,
        "catalog_digest": result.catalog_digest,
        "query_ids": list(result.query_ids),
        "top_k": result.top_k,
        "limitations": list(REPORT_LIMITATIONS),
        "arms": [_build_arm_dict_from_three_arm(arm) for arm in result.arms],
    }
    body["report_digest"] = compute_batch_report_digest(body)
    return verify_batch_report(body)


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"BATCH_REPORT_DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def _reject_non_finite_json_constant(token: str) -> Any:
    raise ValueError(f"BATCH_REPORT_NON_FINITE_NUMBER:{token}")


def _validate_identifier(value: object, error_code: str) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or "/" in value
        or "\\" in value
        or ":" in value
        or ".." in value
        or _IDENTIFIER_RE.fullmatch(value) is None
        or _HEX64_ANY_RE.fullmatch(value) is not None
    ):
        raise ValueError(error_code)
    return value


def _validate_candidate_dict(
    cand: Any,
    *,
    expected_arm_id: str,
    expected_query_id: str,
    expected_query_text: str,
    expected_generation_id: str,
    expected_space_id: str,
) -> dict[str, Any]:
    if not isinstance(cand, Mapping):
        raise ValueError("BATCH_REPORT_CANDIDATE_NOT_OBJECT")
    actual_keys = set(cand.keys())
    if actual_keys & _FORBIDDEN_EDIT_BOUNDARY_FIELDS:
        raise ValueError("BATCH_REPORT_CANDIDATE_EDIT_BOUNDARY_FORBIDDEN")
    if actual_keys != _CANDIDATE_RECORD_FIELDS:
        raise ValueError("BATCH_REPORT_CANDIDATE_FIELDS_INVALID")

    if cand["arm_id"] != expected_arm_id:
        raise ValueError("BATCH_REPORT_CANDIDATE_ARM_MISMATCH")
    if cand["query_id"] != expected_query_id or cand["query"] != expected_query_text:
        raise ValueError("BATCH_REPORT_CANDIDATE_QUERY_MISMATCH")
    if (
        cand["generation_id"] != expected_generation_id
        or cand["space_id"] != expected_space_id
    ):
        raise ValueError("BATCH_REPORT_CANDIDATE_GENERATION_SPACE_MISMATCH")

    rank = cand["rank"]
    if type(rank) is not int or rank < 1:
        raise ValueError("BATCH_REPORT_CANDIDATE_RANK_INVALID")
    score = cand["score"]
    if type(score) is bool or not isinstance(score, (int, float)) or not math.isfinite(score):
        raise ValueError("BATCH_REPORT_CANDIDATE_SCORE_INVALID")

    for str_field in ("revision_id", "content_id", "source_path", "timestamp_human", "thumbnail_status"):
        val = cand[str_field]
        if type(val) is not str or not val or "\x00" in val:
            raise ValueError(f"BATCH_REPORT_CANDIDATE_FIELD_INVALID:{str_field}")
    if _HEX64_ANY_RE.fullmatch(cand["revision_id"]) is not None:
        raise ValueError("BATCH_REPORT_CANDIDATE_REVISION_ID_INVALID")

    sha = cand["source_sha256"]
    if type(sha) is not str or _LOWER_SHA256_RE.fullmatch(sha) is None:
        raise ValueError("BATCH_REPORT_CANDIDATE_SHA256_INVALID")

    thumb_path = cand["thumbnail_path"]
    if thumb_path is not None and (type(thumb_path) is not str or not thumb_path):
        raise ValueError("BATCH_REPORT_CANDIDATE_THUMBNAIL_INVALID")

    pts = cand["source_sample_pts"]
    tb_num = cand["source_timebase_num"]
    tb_den = cand["source_timebase_den"]
    if (
        type(pts) is not int
        or type(tb_num) is not int
        or type(tb_den) is not int
        or tb_num <= 0
        or tb_den <= 0
    ):
        raise ValueError("BATCH_REPORT_CANDIDATE_LOCATOR_INVALID")

    if cand["evidence_class"] != "MATCHED":
        raise ValueError(f"BATCH_REPORT_CANDIDATE_EVIDENCE_CLASS_INVALID:{cand['evidence_class']!r}")
    if cand["binding_eligible"] is not False:
        raise ValueError("BATCH_REPORT_CANDIDATE_BINDING_ELIGIBLE_FORBIDDEN")

    return dict(cand, score=float(score))


def verify_batch_report(report: Mapping[str, Any] | bytes | str) -> dict[str, Any]:
    """Verify exact report shape, claim limits, candidate invariants, and digest.

    Never opens or resolves any ``source_path`` on the filesystem.
    """
    if isinstance(report, (bytes, bytearray)):
        if b"\x00" in report:
            raise ValueError("BATCH_REPORT_NUL_BYTE_FORBIDDEN")
        try:
            text = bytes(report).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("BATCH_REPORT_UTF8_INVALID") from exc
        parsed = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_non_finite_json_constant,
        )
    elif type(report) is str:
        if "\x00" in report:
            raise ValueError("BATCH_REPORT_NUL_BYTE_FORBIDDEN")
        parsed = json.loads(
            report,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_non_finite_json_constant,
        )
    elif isinstance(report, Mapping):
        parsed = dict(report)
    else:
        raise TypeError("BATCH_REPORT_MAPPING_OR_JSON_REQUIRED")

    if not isinstance(parsed, Mapping):
        raise ValueError("BATCH_REPORT_NOT_OBJECT")
    if set(parsed.keys()) != _REPORT_TOP_FIELDS:
        raise ValueError("BATCH_REPORT_FIELDS_INVALID")

    if parsed["schema_version"] != BATCH_REPORT_SCHEMA_VERSION:
        raise ValueError(f"BATCH_REPORT_SCHEMA_INVALID:{parsed['schema_version']!r}")
    kind = parsed["kind"]
    if kind not in {KIND_SINGLE_ARM, KIND_THREE_ARM}:
        raise ValueError(f"BATCH_REPORT_KIND_INVALID:{kind!r}")
    if parsed["status"] != REPORT_STATUS_SYNTHETIC_ONLY:
        raise ValueError(f"BATCH_REPORT_STATUS_INVALID:{parsed['status']!r}")
    if parsed["benchmark_status"] != BENCHMARK_STATUS_NOT_RUN:
        raise ValueError(f"BATCH_REPORT_BENCHMARK_STATUS_INVALID:{parsed['benchmark_status']!r}")
    if parsed["model_evidence"] != MODEL_EVIDENCE_NOT_OBSERVED:
        raise ValueError(f"BATCH_REPORT_MODEL_EVIDENCE_INVALID:{parsed['model_evidence']!r}")
    if parsed["gate_decision"] != GATE_DECISION_NOT_AUTHORIZED:
        raise ValueError(f"BATCH_REPORT_GATE_DECISION_INVALID:{parsed['gate_decision']!r}")
    if parsed["synthetic_only"] is not True or parsed["authentic_model_evidence"] is not False:
        raise ValueError("BATCH_REPORT_SYNTHETIC_FLAGS_INVALID")
    if parsed["cross_arm_winner"] is not None:
        raise ValueError("BATCH_REPORT_WINNER_FORBIDDEN")

    limitations = parsed["limitations"]
    if type(limitations) is not list or tuple(limitations) != REPORT_LIMITATIONS:
        raise ValueError("BATCH_REPORT_LIMITATIONS_INVALID")

    _validate_identifier(parsed["catalog_id"], "BATCH_REPORT_CATALOG_ID_INVALID")
    catalog_digest = parsed["catalog_digest"]
    if type(catalog_digest) is not str or _LOWER_SHA256_RE.fullmatch(catalog_digest) is None:
        raise ValueError("BATCH_REPORT_CATALOG_DIGEST_INVALID")

    top_k = validate_lab_top_k(parsed["top_k"])

    query_ids = parsed["query_ids"]
    if (
        type(query_ids) is not list
        or not (MIN_QUERY_COUNT <= len(query_ids) <= MAX_QUERY_COUNT)
    ):
        raise ValueError("BATCH_REPORT_QUERY_IDS_INVALID")
    seen_qids: set[str] = set()
    for qid in query_ids:
        _validate_identifier(qid, "BATCH_REPORT_QUERY_ID_INVALID")
        if qid in seen_qids:
            raise ValueError(f"BATCH_REPORT_DUPLICATE_QUERY_ID:{qid}")
        seen_qids.add(qid)

    arms = parsed["arms"]
    if type(arms) is not list:
        raise ValueError("BATCH_REPORT_ARMS_INVALID")
    if kind == KIND_SINGLE_ARM and len(arms) != 1:
        raise ValueError("BATCH_REPORT_SINGLE_ARM_COUNT_INVALID")
    if kind == KIND_THREE_ARM and len(arms) != len(DECLARED_ARM_ORDER):
        raise ValueError("BATCH_REPORT_THREE_ARM_COUNT_INVALID")

    seen_arm_ids: list[str] = []
    seen_space_ids: set[str] = set()
    seen_generation_ids: set[str] = set()
    validated_arms: list[dict[str, Any]] = []

    for arm in arms:
        if not isinstance(arm, Mapping) or set(arm.keys()) != _ARM_RECORD_FIELDS:
            raise ValueError("BATCH_REPORT_ARM_FIELDS_INVALID")
        arm_id = arm["arm_id"]
        profile_id = arm["profile_id"]
        if type(arm_id) is not str or arm_id not in ARM_TO_PROFILE_ID:
            raise ValueError(f"BATCH_REPORT_ARM_ID_INVALID:{arm_id!r}")
        if ARM_TO_PROFILE_ID[arm_id] != profile_id:
            raise ValueError(f"BATCH_REPORT_ARM_PROFILE_MISMATCH:{arm_id}:{profile_id}")
        if arm_id in seen_arm_ids:
            raise ValueError(f"BATCH_REPORT_DUPLICATE_ARM_ID:{arm_id}")
        seen_arm_ids.append(arm_id)

        expected_model_id, expected_dim, expected_row_bytes = _EXPECTED_PROFILE_GEOMETRY[profile_id]
        if arm["model_identity"] != expected_model_id:
            raise ValueError("BATCH_REPORT_ARM_MODEL_IDENTITY_INVALID")
        if type(arm["embedding_dim"]) is not int or arm["embedding_dim"] != expected_dim:
            raise ValueError("BATCH_REPORT_ARM_DIM_INVALID")
        if type(arm["row_width_bytes"]) is not int or arm["row_width_bytes"] != expected_row_bytes:
            raise ValueError("BATCH_REPORT_ARM_ROW_WIDTH_INVALID")

        space_id = arm["space_id"]
        manifest_digest = arm["manifest_digest"]
        generation_id = arm["generation_id"]
        if type(space_id) is not str or _LOWER_SHA256_RE.fullmatch(space_id) is None:
            raise ValueError("BATCH_REPORT_ARM_SPACE_ID_INVALID")
        if type(manifest_digest) is not str or _LOWER_SHA256_RE.fullmatch(manifest_digest) is None:
            raise ValueError("BATCH_REPORT_ARM_MANIFEST_DIGEST_INVALID")
        if type(generation_id) is not str or not generation_id:
            raise ValueError("BATCH_REPORT_ARM_GENERATION_ID_INVALID")
        if space_id in seen_space_ids or generation_id in seen_generation_ids:
            raise ValueError("BATCH_REPORT_CROSS_ARM_SPACE_COLLISION")
        seen_space_ids.add(space_id)
        seen_generation_ids.add(generation_id)

        if arm["catalog_digest"] != catalog_digest:
            raise ValueError("BATCH_REPORT_ARM_CATALOG_DIGEST_MISMATCH")
        if (
            arm["fake_runtime_used"] is not True
            or arm["synthetic_only"] is not True
            or arm["authentic_model_evidence"] is not False
        ):
            raise ValueError("BATCH_REPORT_ARM_SYNTHETIC_FLAGS_INVALID")

        queries = arm["queries"]
        if type(queries) is not list or len(queries) != len(query_ids):
            raise ValueError("BATCH_REPORT_ARM_QUERIES_COUNT_MISMATCH")
        if type(arm["query_count"]) is not int or arm["query_count"] != len(query_ids):
            raise ValueError("BATCH_REPORT_ARM_QUERY_COUNT_MISMATCH")

        validated_queries: list[dict[str, Any]] = []
        total_arm_candidates = 0
        for expected_qid, q_row in zip(query_ids, queries):
            if not isinstance(q_row, Mapping) or set(q_row.keys()) != _QUERY_RECORD_FIELDS:
                raise ValueError("BATCH_REPORT_QUERY_ROW_FIELDS_INVALID")
            if q_row["query_id"] != expected_qid:
                raise ValueError("BATCH_REPORT_QUERY_ORDER_MISMATCH")
            q_text = q_row["query_text"]
            if type(q_text) is not str or not q_text or not q_text.strip() or "\x00" in q_text:
                raise ValueError("BATCH_REPORT_QUERY_TEXT_INVALID")
            raw_candidates = q_row["candidates"]
            if type(raw_candidates) is not list or len(raw_candidates) > top_k:
                raise ValueError("BATCH_REPORT_QUERY_CANDIDATES_INVALID")
            if (
                type(q_row["candidate_count"]) is not int
                or q_row["candidate_count"] != len(raw_candidates)
            ):
                raise ValueError("BATCH_REPORT_QUERY_CANDIDATE_COUNT_MISMATCH")

            validated_cands: list[dict[str, Any]] = []
            prev_rank = 0
            for cand in raw_candidates:
                vc = _validate_candidate_dict(
                    cand,
                    expected_arm_id=arm_id,
                    expected_query_id=expected_qid,
                    expected_query_text=q_text,
                    expected_generation_id=generation_id,
                    expected_space_id=space_id,
                )
                if vc["rank"] < prev_rank:
                    raise ValueError("BATCH_REPORT_CANDIDATE_RANK_ORDER_INVALID")
                prev_rank = vc["rank"]
                validated_cands.append(vc)

            total_arm_candidates += len(validated_cands)
            validated_queries.append({
                "query_id": expected_qid,
                "query_text": q_text,
                "candidate_count": len(validated_cands),
                "candidates": validated_cands,
            })

        if type(arm["candidate_count"]) is not int or arm["candidate_count"] != total_arm_candidates:
            raise ValueError("BATCH_REPORT_ARM_CANDIDATE_COUNT_MISMATCH")

        validated_arms.append({
            "arm_id": arm_id,
            "profile_id": profile_id,
            "model_identity": arm["model_identity"],
            "space_id": space_id,
            "generation_id": generation_id,
            "embedding_dim": arm["embedding_dim"],
            "row_width_bytes": arm["row_width_bytes"],
            "manifest_digest": manifest_digest,
            "catalog_digest": catalog_digest,
            "query_count": len(query_ids),
            "candidate_count": total_arm_candidates,
            "fake_runtime_used": True,
            "synthetic_only": True,
            "authentic_model_evidence": False,
            "queries": validated_queries,
        })

    if kind == KIND_THREE_ARM and tuple(seen_arm_ids) != DECLARED_ARM_ORDER:
        raise ValueError("BATCH_REPORT_THREE_ARM_ORDER_INVALID")

    report_digest = parsed["report_digest"]
    if type(report_digest) is not str or _LOWER_SHA256_RE.fullmatch(report_digest) is None:
        raise ValueError("BATCH_REPORT_DIGEST_INVALID")

    normalized_report: dict[str, Any] = {
        "schema_version": BATCH_REPORT_SCHEMA_VERSION,
        "kind": kind,
        "status": REPORT_STATUS_SYNTHETIC_ONLY,
        "benchmark_status": BENCHMARK_STATUS_NOT_RUN,
        "model_evidence": MODEL_EVIDENCE_NOT_OBSERVED,
        "gate_decision": GATE_DECISION_NOT_AUTHORIZED,
        "synthetic_only": True,
        "authentic_model_evidence": False,
        "cross_arm_winner": None,
        "catalog_id": parsed["catalog_id"],
        "catalog_digest": catalog_digest,
        "query_ids": list(query_ids),
        "top_k": top_k,
        "limitations": list(REPORT_LIMITATIONS),
        "arms": validated_arms,
        "report_digest": report_digest,
    }
    expected_digest = compute_batch_report_digest(normalized_report)
    if report_digest != expected_digest:
        raise ValueError(f"BATCH_REPORT_DIGEST_MISMATCH:{report_digest}!={expected_digest}")

    return normalized_report


__all__ = [
    "BATCH_REPORT_SCHEMA_VERSION",
    "BENCHMARK_STATUS_NOT_RUN",
    "GATE_DECISION_NOT_AUTHORIZED",
    "KIND_SINGLE_ARM",
    "KIND_THREE_ARM",
    "MODEL_EVIDENCE_NOT_OBSERVED",
    "REPORT_LIMITATIONS",
    "REPORT_STATUS_SYNTHETIC_ONLY",
    "build_single_arm_batch_report",
    "build_three_arm_batch_report",
    "compute_batch_report_digest",
    "serialize_batch_report",
    "verify_batch_report",
]
