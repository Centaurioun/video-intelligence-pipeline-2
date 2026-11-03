"""Closed, immutable Gate-0 control-input loader."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


class ConfigError(ValueError):
    """Raised when the Gate-0 control input or dependency lock is invalid."""


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


_TOP = ("corpus", "windows", "sampling", "thresholds", "model", "runtime", "policy", "retention", "tie_rules", "sandbox", "blinding")
_RETENTION = ("SOURCE_REFERENCE", "DERIVED_REPLAYABLE", "DERIVED_RESTRICTED", "AUDIT_MINIMUM", "TOMBSTONE")
_ENUMS = {
    "relation_policy": "component_frozen", "half_open": True, "final_window_policy": "omit_incomplete",
    "selected_stream_policy": "configured_single_video_stream", "origin_policy": "selected_stream_origin",
    "dtype": "float64", "offline_only": True, "provider_model_boundary": "local_only",
    "cache_policy": "cleared_between_replays", "local_only": True,
    "revalidation": "every_stage_boundary_and_cache_read", "score_order": "descending",
    "window_start_key": "reduced_rational", "numeric_identity": "float64_row_major",
    "clearenv": True, "net_unshared": True, "child_network_sentinel": True,
}
_REQUIRED = {
    "corpus": ("source_root", "source_manifest_digest", "relation_policy", "evaluation_query_count", "development_query_count"),
    "windows": ("duration_seconds", "half_open", "final_window_policy", "selected_stream_policy", "selected_stream_index"),
    "sampling": ("target_fps_num", "target_fps_den", "target_ticks", "origin_policy"),
    "thresholds": ("semantic_hit_at_10_num", "semantic_hit_at_10_den", "paired_lift_num", "paired_lift_den", "family_hit_at_10_num", "family_hit_at_10_den"),
    "model": ("semantic_arm_id", "model_identity", "weights_digest", "processor_digest", "space_id", "dimension", "dtype", "offline_only", "provider_model_boundary"),
    "runtime": ("python_path", "python_version", "dependency_lock_path", "ffmpeg_path", "ffprobe_path", "blas_thread_count", "cache_policy"),
    "policy": ("reviewer_ids", "policy_authority", "gate_owner_id", "local_only", "egress_manifest_digest", "permitted_artifact_types", "provider_model_boundary", "revalidation", "review_input"),
    "tie_rules": ("score_order", "candidate_key", "window_start_key", "numeric_identity"),
    "sandbox": ("bwrap_path", "bwrap_version", "bwrap_digest", "interpreter_path", "interpreter_version", "interpreter_digest", "read_only_mounts", "writable_mounts", "clearenv", "net_unshared", "argv_digest", "mount_policy_digest", "child_network_sentinel"),
    "blinding": ("mapping_version", "blind_mapping_digest", "reviewer_count", "reviewer_visible_fields", "reviewer_hidden_fields", "token_map"),
}


def _validate_schema(value: Any, schema: dict[str, Any], path: str = "$",) -> None:
    expected = schema.get("type")
    valid = {"object": isinstance(value, dict), "array": isinstance(value, list), "string": isinstance(value, str), "integer": isinstance(value, int) and not isinstance(value, bool), "boolean": isinstance(value, bool), "null": value is None}
    if expected and not any(valid.get(item, False) for item in (expected if isinstance(expected, list) else [expected])):
        raise ConfigError(f"schema type at {path}: expected {expected}")
    if "enum" in schema and value not in schema["enum"]:
        raise ConfigError(f"schema enum at {path}")
    if "const" in schema and value != schema["const"]:
        raise ConfigError(f"schema invariant at {path}")
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ConfigError(f"required field: {path}.{key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = [key for key in value if key not in properties]
            if unknown:
                raise ConfigError(f"unknown field: {path}.{unknown[0]}")
        for key, item in value.items():
            if key in properties:
                _validate_schema(item, properties[key], f"{path}.{key}")
            elif isinstance(schema.get("additionalProperties"), dict):
                _validate_schema(item, schema["additionalProperties"], f"{path}.{key}")
        names = schema.get("propertyNames", {}).get("enum")
        if names is not None and any(key not in names for key in value):
            raise ConfigError(f"schema property name at {path}")
        if names is not None and set(value) != set(names):
            raise ConfigError(f"schema property cardinality at {path}")
    elif isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise ConfigError(f"schema minItems at {path}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise ConfigError(f"schema maxItems at {path}")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate_schema(item, schema["items"], f"{path}[{index}]")


def _validate(data: dict[str, Any]) -> None:
    if tuple(data) != _TOP:
        unknown = [key for key in data if key not in _TOP]
        if unknown:
            raise ConfigError(f"unknown field: {unknown[0]}")
    for section, fields in _REQUIRED.items():
        value = data.get(section)
        if not isinstance(value, dict):
            raise ConfigError(f"required field section: {section}")
        unknown = [key for key in value if key not in fields and not (section == "retention" and key in _RETENTION)]
        if unknown:
            raise ConfigError(f"unknown field: {section}.{unknown[0]}")
        for field in fields:
            if field not in value:
                raise ConfigError(f"required field: {section}.{field}")
    retention = data.get("retention")
    if not isinstance(retention, dict) or set(retention) != set(_RETENTION):
        raise ConfigError("retention must contain exactly five classes")
    for name in _RETENTION:
        entry = retention[name]
        if not isinstance(entry, dict):
            raise ConfigError(f"retention.{name} must be an object")
        required = ("owner", "authority", "start_event", "expiry_event", "time_zone", "permitted_readers", "post_expiry_fields", "cleanup_action", "rebuildability")
        if set(entry) != set(required):
            raise ConfigError(f"retention.{name} fields mismatch")
    for section in data.values():
        if isinstance(section, dict):
            for field, expected in _ENUMS.items():
                if field in section and section[field] != expected:
                    raise ConfigError(f"invalid value for {field}")
    if data["corpus"]["evaluation_query_count"] != 24 or data["corpus"]["development_query_count"] != 8:
        raise ConfigError("query counts are frozen")
    if data["windows"]["duration_seconds"] != 4 or len(data["sampling"]["target_ticks"]) != 8:
        raise ConfigError("window/sampling invariant failed")
    if data["sampling"]["target_fps_num"] != 2 or data["sampling"]["target_fps_den"] != 1:
        raise ConfigError("target FPS invariant failed")
    if data["blinding"]["reviewer_count"] != 2 or len(data["blinding"]["token_map"]) != 2:
        raise ConfigError("blinding invariant failed")
    if len(data["model"]["processor_digest"]) != 64 or len(data["policy"]["egress_manifest_digest"]) != 64:
        raise ConfigError("digest field must be SHA-256")


@dataclass(frozen=True)
class ConfigDigest:
    config: Mapping[str, Any]
    config_digest: str
    dependency_lock_digest: str
    python_version: str


def load_config(path: Path, lock_path: Path | None = None) -> ConfigDigest:
    path = Path(path)
    lock_path = Path(lock_path or "requirements/gate0.lock")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"invalid config: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("config must be an object")
    schema_path = Path(__file__).resolve().parents[2] / "schemas/gate0/config.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"config schema missing: {schema_path}") from exc
    _validate_schema(data, schema)
    _validate(data)
    try:
        lock_bytes = lock_path.read_bytes()
    except OSError as exc:
        raise ConfigError(f"dependency lock missing: {lock_path}") from exc
    if not lock_bytes.endswith(b"\n"):
        raise ConfigError("dependency lock must be UTF-8 LF text")
    return ConfigDigest(_freeze(data), hashlib.sha256(canonical_json_bytes(data)).hexdigest(), hashlib.sha256(lock_bytes).hexdigest(), data["runtime"]["python_version"])
