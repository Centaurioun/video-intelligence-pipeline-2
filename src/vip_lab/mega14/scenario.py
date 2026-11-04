"""Closed SyntheticLabScenario schema and default scenarios for MEGA-14."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from vip_fvs.synthetic_profiles import CLOSED_SYNTHETIC_PROFILE_IDS, V1_PROFILE_ID
from vip_lab.common import (
    VipLabError,
    load_bounded_json_file,
    sanitize_untrusted_authority_claims,
    validate_hex_digest,
)

E2E_SCENARIO_SCHEMA_VERSION = "vip-lab-e2e-scenario-v1"
ALLOWED_SCENARIO_MODES: tuple[str, ...] = ("SINGLE_ARM", "THREE_ARM")

_FORBIDDEN_EXECUTION_FLAGS = frozenset(
    {
        "real_media",
        "authentic_weights",
        "run_ffmpeg",
        "production_export",
        "network_access",
        "provider_api",
    }
)

_ALLOWED_SCENARIO_KEYS = frozenset(
    {
        "schema_version",
        "scenario_id",
        "mode",
        "single_arm_profile_id",
        "catalog_id",
        "top_k",
        "queries",
        "sources",
        "timebase_num",
        "timebase_den",
        "pts_ticks",
        "requested_start_pts",
        "requested_end_pts",
        "workload",
    }
)


@dataclass(frozen=True)
class SyntheticLabScenario:
    schema_version: str
    scenario_id: str
    mode: str
    single_arm_profile_id: str
    catalog_id: str
    top_k: int
    queries: tuple[dict[str, str], ...]
    sources: tuple[dict[str, Any], ...]
    timebase_num: int
    timebase_den: int
    pts_ticks: tuple[int, ...]
    requested_start_pts: int
    requested_end_pts: int
    workload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scenario_id": self.scenario_id,
            "mode": self.mode,
            "single_arm_profile_id": self.single_arm_profile_id,
            "catalog_id": self.catalog_id,
            "top_k": self.top_k,
            "queries": [dict(q) for q in self.queries],
            "sources": [dict(s) for s in self.sources],
            "timebase_num": self.timebase_num,
            "timebase_den": self.timebase_den,
            "pts_ticks": list(self.pts_ticks),
            "requested_start_pts": self.requested_start_pts,
            "requested_end_pts": self.requested_end_pts,
            "workload": dict(self.workload),
        }


def default_three_arm_scenario() -> SyntheticLabScenario:
    shared_sha = "c" * 64
    return SyntheticLabScenario(
        schema_version=E2E_SCENARIO_SCHEMA_VERSION,
        scenario_id="scen-mega14-three-arm-default",
        mode="THREE_ARM",
        single_arm_profile_id=V1_PROFILE_ID,
        catalog_id="cat-mega14-01",
        top_k=5,
        queries=(
            {"query_id": "q-01", "text": "ballet grand jete"},
            {"query_id": "q-02", "text": "ballet grand jete"},
            {"query_id": "q-03", "text": "orchestra downbeat"},
        ),
        sources=(
            {
                "revision_id": "rev-cam-a",
                "content_id": "content-shared",
                "source_path": "/synthetic/archive/cam_a.mp4",
                "source_sha256": shared_sha,
                "sample_pts": 3003,
                "timestamp_human": "00:00:00.100",
                "score": 0.93,
            },
            {
                "revision_id": "rev-cam-b",
                "content_id": "content-shared",
                "source_path": "/synthetic/archive/cam_b_copy.mp4",
                "source_sha256": shared_sha,
                "sample_pts": 5005,
                "timestamp_human": "00:00:00.167",
                "score": 0.87,
            },
        ),
        timebase_num=1001,
        timebase_den=30000,
        pts_ticks=(0, 1001, 2002, 3003, 4004, 5005, 6006, 7007),
        requested_start_pts=3003,
        requested_end_pts=6006,
        workload={
            "workload_id": "wl-mega14-e2e",
            "seed": 20261104,
            "job_count": 3,
            "stages_per_job": 2,
            "payload_bytes": 48,
        },
    )


def default_single_arm_scenario() -> SyntheticLabScenario:
    base = default_three_arm_scenario()
    return SyntheticLabScenario(
        schema_version=base.schema_version,
        scenario_id="scen-mega14-single-arm-default",
        mode="SINGLE_ARM",
        single_arm_profile_id=V1_PROFILE_ID,
        catalog_id=base.catalog_id,
        top_k=base.top_k,
        queries=base.queries,
        sources=base.sources,
        timebase_num=base.timebase_num,
        timebase_den=base.timebase_den,
        pts_ticks=base.pts_ticks,
        requested_start_pts=base.requested_start_pts,
        requested_end_pts=base.requested_end_pts,
        workload=dict(base.workload),
    )


def parse_e2e_scenario_mapping(raw: Mapping[str, Any]) -> SyntheticLabScenario:
    if not isinstance(raw, Mapping):
        raise VipLabError("SCENARIO_NOT_MAPPING", "Scenario payload must be a mapping.")

    _, untrusted = sanitize_untrusted_authority_claims(raw)
    if untrusted:
        raise VipLabError(
            "SCENARIO_FORBIDDEN_AUTHORITY_FLAG",
            f"Scenario contains forbidden authority keys: {list(untrusted)}",
        )

    forbidden_present = sorted(k for k in raw.keys() if k in _FORBIDDEN_EXECUTION_FLAGS)
    if forbidden_present:
        raise VipLabError(
            "SCENARIO_FORBIDDEN_EXECUTION_FLAG",
            f"Scenario contains forbidden execution flags: {forbidden_present}",
        )

    unknown = sorted(set(raw.keys()) - _ALLOWED_SCENARIO_KEYS)
    if unknown:
        raise VipLabError(
            "SCENARIO_UNKNOWN_FIELD",
            f"Unknown scenario fields: {unknown}",
        )

    if raw.get("schema_version") != E2E_SCENARIO_SCHEMA_VERSION:
        raise VipLabError(
            "SCENARIO_SCHEMA_INVALID",
            f"Expected schema_version {E2E_SCENARIO_SCHEMA_VERSION!r}.",
        )
    mode = str(raw.get("mode", ""))
    if mode not in ALLOWED_SCENARIO_MODES:
        raise VipLabError(
            "SCENARIO_MODE_INVALID",
            f"Scenario mode must be one of {ALLOWED_SCENARIO_MODES}, got {mode!r}.",
        )
    prof_id = str(raw.get("single_arm_profile_id", V1_PROFILE_ID))
    if prof_id not in CLOSED_SYNTHETIC_PROFILE_IDS:
        raise VipLabError(
            "SCENARIO_PROFILE_INVALID",
            f"Unsupported single_arm_profile_id {prof_id!r}.",
        )

    queries_raw = raw.get("queries")
    if not isinstance(queries_raw, (list, tuple)) or len(queries_raw) == 0:
        raise VipLabError("SCENARIO_QUERIES_INVALID", "queries must be a non-empty list.")
    queries: list[dict[str, str]] = []
    for q in queries_raw:
        if not isinstance(q, Mapping) or not q.get("query_id") or not q.get("text"):
            raise VipLabError(
                "SCENARIO_QUERIES_INVALID",
                "Each query must contain non-empty query_id and text.",
            )
        queries.append({"query_id": str(q["query_id"]), "text": str(q["text"])})

    sources_raw = raw.get("sources")
    if not isinstance(sources_raw, (list, tuple)) or len(sources_raw) == 0:
        raise VipLabError("SCENARIO_SOURCES_INVALID", "sources must be a non-empty list.")
    sources: list[dict[str, Any]] = []
    for s in sources_raw:
        if not isinstance(s, Mapping):
            raise VipLabError("SCENARIO_SOURCES_INVALID", "Each source entry must be a mapping.")
        sha = validate_hex_digest(
            s.get("source_sha256"),
            field_name="source_sha256",
            error_code="SCENARIO_SOURCE_SHA256_INVALID",
        )
        sources.append(
            {
                "revision_id": str(s["revision_id"]),
                "content_id": str(s["content_id"]),
                "source_path": str(s["source_path"]),
                "source_sha256": sha,
                "sample_pts": int(s.get("sample_pts", 3003)),
                "timestamp_human": str(s.get("timestamp_human", "00:00:00.100")),
                "score": float(s.get("score", 0.90)),
            }
        )

    ticks_raw = raw.get("pts_ticks")
    if not isinstance(ticks_raw, (list, tuple)) or len(ticks_raw) < 2:
        raise VipLabError("SCENARIO_PTS_TICKS_INVALID", "pts_ticks must contain >= 2 integers.")
    pts_ticks = tuple(int(t) for t in ticks_raw)

    workload_raw = raw.get("workload")
    if not isinstance(workload_raw, Mapping):
        raise VipLabError("SCENARIO_WORKLOAD_INVALID", "workload must be a mapping.")

    return SyntheticLabScenario(
        schema_version=E2E_SCENARIO_SCHEMA_VERSION,
        scenario_id=str(raw.get("scenario_id", "scen-custom")),
        mode=mode,
        single_arm_profile_id=prof_id,
        catalog_id=str(raw.get("catalog_id", "cat-custom")),
        top_k=int(raw.get("top_k", 5)),
        queries=tuple(queries),
        sources=tuple(sources),
        timebase_num=int(raw.get("timebase_num", 1001)),
        timebase_den=int(raw.get("timebase_den", 30000)),
        pts_ticks=pts_ticks,
        requested_start_pts=int(raw.get("requested_start_pts", pts_ticks[0])),
        requested_end_pts=int(raw.get("requested_end_pts", pts_ticks[-1])),
        workload={
            "workload_id": str(workload_raw.get("workload_id", "wl-custom")),
            "seed": int(workload_raw.get("seed", 20261104)),
            "job_count": int(workload_raw.get("job_count", 3)),
            "stages_per_job": int(workload_raw.get("stages_per_job", 2)),
            "payload_bytes": int(workload_raw.get("payload_bytes", 48)),
        },
    )


def load_e2e_scenario_file(path: str | Path) -> SyntheticLabScenario:
    raw = load_bounded_json_file(path, require_mapping=True)
    return parse_e2e_scenario_mapping(raw)
