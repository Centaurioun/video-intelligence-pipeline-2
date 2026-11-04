"""Explicit three-arm isolated synthetic batch retrieval orchestrator.

Authority: VIP-LAB-MEGA-02 Workstream W4.

Executes read-only multi-source batch retrieval independently across the three
closed charter arms:
- ``VIP_V1_BASE`` -> ``vip-v1-siglip-base-224`` (768D)
- ``VIP_V2_BASE`` -> ``vip-v2-siglip2-base-224`` (768D)
- ``VIP_V2_SO400M`` -> ``vip-v2-siglip2-so400m-384`` (1152D)

No cross-arm score normalization, winner selection, or benchmark verdict is
computed. If any arm fails validation or retrieval, the entire three-arm batch
fails closed without emitting a partial result.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from .batch_retrieval import SingleArmBatchResult, run_batch_retrieval
from .query_batch import QueryCatalog, validate_lab_top_k
from .semantic_index import PersistentLocalSemanticIndexEngine, SemanticIndexEngine
from .source_adapter import MultiSourceManifest, load_multi_source_manifest
from .synthetic_profiles import (
    SyntheticProfileBundle,
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
    load_synthetic_profile_bundle,
)

THREE_ARM_MAP_SCHEMA_VERSION = "vip-lab-three-arm-v1"
MAX_ARM_MAP_BYTES = 256 * 1024

ARM_VIP_V1_BASE = "VIP_V1_BASE"
ARM_VIP_V2_BASE = "VIP_V2_BASE"
ARM_VIP_V2_SO400M = "VIP_V2_SO400M"

DECLARED_ARM_ORDER: tuple[str, str, str] = (
    ARM_VIP_V1_BASE,
    ARM_VIP_V2_BASE,
    ARM_VIP_V2_SO400M,
)

ARM_TO_PROFILE_ID: Mapping[str, str] = {
    ARM_VIP_V1_BASE: V1_PROFILE_ID,
    ARM_VIP_V2_BASE: V2_BASE_PROFILE_ID,
    ARM_VIP_V2_SO400M: V2_SO400M_PROFILE_ID,
}

PROFILE_ID_TO_ARM: Mapping[str, str] = {
    V1_PROFILE_ID: ARM_VIP_V1_BASE,
    V2_BASE_PROFILE_ID: ARM_VIP_V2_BASE,
    V2_SO400M_PROFILE_ID: ARM_VIP_V2_SO400M,
}

_TOP_LEVEL_FIELDS = frozenset({"schema_version", "arms"})
_ARM_ENTRY_FIELDS = frozenset({"arm_id", "model_profile_json", "index_root", "manifest"})


def _validate_non_empty_path_str(value: object, field_name: str) -> str:
    if type(value) is not str or not value or not value.strip() or "\x00" in value:
        raise ValueError(f"THREE_ARM_MAP_PATH_INVALID:{field_name}")
    return value


@dataclass(frozen=True)
class ThreeArmConfigEntry:
    """Configuration binding one declared arm to its profile, index root, and manifest."""

    arm_id: str
    model_profile_json: Path
    index_root: Path
    manifest: Path

    def __post_init__(self) -> None:
        if type(self.arm_id) is not str or self.arm_id not in ARM_TO_PROFILE_ID:
            raise ValueError(f"THREE_ARM_MAP_UNKNOWN_ARM_ID:{self.arm_id!r}")
        for attr in ("model_profile_json", "index_root", "manifest"):
            val = getattr(self, attr)
            if not isinstance(val, Path) or not str(val) or "\x00" in str(val):
                raise ValueError(f"THREE_ARM_MAP_PATH_INVALID:{attr}")

    def to_dict(self) -> dict[str, str]:
        return {
            "arm_id": self.arm_id,
            "model_profile_json": str(self.model_profile_json),
            "index_root": str(self.index_root),
            "manifest": str(self.manifest),
        }


def _compute_arm_map_digest(
    schema_version: str, arms: tuple[ThreeArmConfigEntry, ...]
) -> str:
    payload = {
        "schema_version": schema_version,
        "arms": [entry.to_dict() for entry in arms],
    }
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class ThreeArmConfigMap:
    """Canonicalized three-arm configuration map in fixed charter arm order."""

    schema_version: str
    arms: tuple[ThreeArmConfigEntry, ...]
    arm_map_digest: str

    def __post_init__(self) -> None:
        if (
            type(self.schema_version) is not str
            or self.schema_version != THREE_ARM_MAP_SCHEMA_VERSION
        ):
            raise ValueError(f"THREE_ARM_MAP_SCHEMA_INVALID:{self.schema_version!r}")
        if type(self.arms) is not tuple or len(self.arms) != len(DECLARED_ARM_ORDER):
            raise ValueError("THREE_ARM_MAP_INCOMPLETE_ARMS")
        if any(type(entry) is not ThreeArmConfigEntry for entry in self.arms):
            raise ValueError("THREE_ARM_MAP_ENTRY_INVALID")
        if tuple(entry.arm_id for entry in self.arms) != DECLARED_ARM_ORDER:
            raise ValueError("THREE_ARM_MAP_ORDER_INVALID")
        index_roots = [str(entry.index_root) for entry in self.arms]
        if len(set(index_roots)) != len(DECLARED_ARM_ORDER):
            raise ValueError("THREE_ARM_SHARED_INDEX_ROOT_FORBIDDEN")
        expected_digest = _compute_arm_map_digest(self.schema_version, self.arms)
        if self.arm_map_digest != expected_digest:
            raise ValueError("THREE_ARM_MAP_DIGEST_MISMATCH")


def parse_three_arm_map_mapping(payload: Mapping[str, Any]) -> ThreeArmConfigMap:
    """Validate an in-memory mapping and return a canonical :class:`ThreeArmConfigMap`."""
    if not isinstance(payload, Mapping):
        raise ValueError("THREE_ARM_MAP_NOT_OBJECT")
    if set(payload.keys()) != _TOP_LEVEL_FIELDS:
        raise ValueError("THREE_ARM_MAP_FIELDS_INVALID")
    schema_version = payload["schema_version"]
    if type(schema_version) is not str or schema_version != THREE_ARM_MAP_SCHEMA_VERSION:
        raise ValueError(f"THREE_ARM_MAP_SCHEMA_INVALID:{schema_version!r}")

    raw_arms = payload["arms"]
    if type(raw_arms) is not list or not raw_arms:
        raise ValueError("THREE_ARM_MAP_ARMS_INVALID")

    by_arm_id: dict[str, ThreeArmConfigEntry] = {}
    for raw_entry in raw_arms:
        if type(raw_entry) is not dict:
            raise ValueError("THREE_ARM_MAP_ENTRY_NOT_OBJECT")
        if set(raw_entry.keys()) != _ARM_ENTRY_FIELDS:
            raise ValueError("THREE_ARM_MAP_ENTRY_FIELDS_INVALID")
        arm_id = raw_entry["arm_id"]
        if type(arm_id) is not str or arm_id not in ARM_TO_PROFILE_ID:
            raise ValueError(f"THREE_ARM_MAP_UNKNOWN_ARM_ID:{arm_id!r}")
        if arm_id in by_arm_id:
            raise ValueError(f"THREE_ARM_MAP_DUPLICATE_ARM_ID:{arm_id}")
        profile_str = _validate_non_empty_path_str(
            raw_entry["model_profile_json"], "model_profile_json"
        )
        index_str = _validate_non_empty_path_str(
            raw_entry["index_root"], "index_root"
        )
        manifest_str = _validate_non_empty_path_str(
            raw_entry["manifest"], "manifest"
        )
        by_arm_id[arm_id] = ThreeArmConfigEntry(
            arm_id=arm_id,
            model_profile_json=Path(profile_str),
            index_root=Path(index_str),
            manifest=Path(manifest_str),
        )

    if set(by_arm_id.keys()) != set(DECLARED_ARM_ORDER):
        raise ValueError("THREE_ARM_MAP_INCOMPLETE_ARMS")

    ordered_entries = tuple(by_arm_id[arm_id] for arm_id in DECLARED_ARM_ORDER)
    if len({str(entry.index_root) for entry in ordered_entries}) != len(DECLARED_ARM_ORDER):
        raise ValueError("THREE_ARM_SHARED_INDEX_ROOT_FORBIDDEN")

    digest = _compute_arm_map_digest(schema_version, ordered_entries)
    return ThreeArmConfigMap(
        schema_version=schema_version,
        arms=ordered_entries,
        arm_map_digest=digest,
    )


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"THREE_ARM_MAP_DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def _reject_non_finite_json_constant(token: str) -> Any:
    raise ValueError(f"THREE_ARM_MAP_NON_FINITE_NUMBER:{token}")


def parse_three_arm_map_bytes(raw: bytes) -> ThreeArmConfigMap:
    """Parse and validate UTF-8 JSON bytes into a :class:`ThreeArmConfigMap`."""
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("THREE_ARM_MAP_BYTES_REQUIRED")
    if not raw or len(raw) > MAX_ARM_MAP_BYTES or b"\x00" in raw:
        raise ValueError("THREE_ARM_MAP_UNREADABLE")
    try:
        text = bytes(raw).decode("utf-8")
        parsed = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_non_finite_json_constant,
        )
    except ValueError as exc:
        msg = str(exc)
        if msg.startswith("THREE_ARM_"):
            raise
        raise ValueError("THREE_ARM_MAP_JSON_INVALID") from exc
    if type(parsed) is not dict:
        raise ValueError("THREE_ARM_MAP_NOT_OBJECT")
    return parse_three_arm_map_mapping(parsed)


def load_three_arm_map(path: str | Path) -> ThreeArmConfigMap:
    """Load and validate a three-arm configuration map JSON file."""
    if not isinstance(path, (str, Path)):
        raise TypeError("THREE_ARM_MAP_PATH_INVALID")
    target = Path(path)
    try:
        with target.open("rb") as handle:
            raw = handle.read(MAX_ARM_MAP_BYTES + 1)
    except OSError as exc:
        raise ValueError("THREE_ARM_MAP_UNREADABLE") from exc
    if len(raw) > MAX_ARM_MAP_BYTES:
        raise ValueError("THREE_ARM_MAP_SIZE_EXCEEDED")
    return parse_three_arm_map_bytes(raw)


@dataclass(frozen=True)
class ThreeArmBatchArmResult:
    """Per-arm isolated synthetic batch retrieval record."""

    arm_id: str
    profile_id: str
    model_identity: str
    space_id: str
    generation_id: str
    embedding_dim: int
    row_width_bytes: int
    manifest_digest: str
    catalog_digest: str
    query_count: int
    candidate_count: int
    batch_result: SingleArmBatchResult
    fake_runtime_used: bool = True
    synthetic_only: bool = True
    authentic_model_evidence: bool = False

    def __post_init__(self) -> None:
        expected_profile = ARM_TO_PROFILE_ID.get(self.arm_id)
        if expected_profile is None or self.profile_id != expected_profile:
            raise ValueError(
                f"THREE_ARM_PROFILE_ID_MISMATCH:{self.arm_id}:{self.profile_id}!={expected_profile}"
            )
        if (
            self.batch_result.profile_id != self.profile_id
            or self.batch_result.space_id != self.space_id
            or self.batch_result.generation_id != self.generation_id
            or self.batch_result.catalog_digest != self.catalog_digest
            or self.batch_result.manifest_digest != self.manifest_digest
        ):
            raise ValueError("THREE_ARM_BATCH_RESULT_PROVENANCE_MISMATCH")
        if (
            self.fake_runtime_used is not True
            or self.synthetic_only is not True
            or self.authentic_model_evidence is not False
        ):
            raise ValueError("THREE_ARM_SYNTHETIC_CLAIM_VIOLATION")


@dataclass(frozen=True)
class ThreeArmBatchResult:
    """Complete three-arm synthetic batch result across all three charter arms."""

    catalog_id: str
    catalog_digest: str
    query_ids: tuple[str, ...]
    top_k: int
    arm_map_digest: str
    arms: tuple[ThreeArmBatchArmResult, ...]
    synthetic_only: bool = True
    authentic_model_evidence: bool = False

    def __post_init__(self) -> None:
        validate_lab_top_k(self.top_k)
        if type(self.arms) is not tuple or len(self.arms) != len(DECLARED_ARM_ORDER):
            raise ValueError("THREE_ARM_RESULT_INCOMPLETE_ARMS")
        if tuple(arm.arm_id for arm in self.arms) != DECLARED_ARM_ORDER:
            raise ValueError("THREE_ARM_RESULT_ORDER_INVALID")
        if len({arm.space_id for arm in self.arms}) != len(DECLARED_ARM_ORDER):
            raise ValueError("THREE_ARM_SEMANTIC_SPACE_COLLISION")
        if len({arm.generation_id for arm in self.arms}) != len(DECLARED_ARM_ORDER):
            raise ValueError("THREE_ARM_GENERATION_COLLISION")
        for arm in self.arms:
            if (
                arm.catalog_digest != self.catalog_digest
                or arm.batch_result.query_ids != self.query_ids
                or arm.query_count != len(self.query_ids)
            ):
                raise ValueError("THREE_ARM_CATALOG_ALIGNMENT_MISMATCH")
        if self.synthetic_only is not True or self.authentic_model_evidence is not False:
            raise ValueError("THREE_ARM_SYNTHETIC_CLAIM_VIOLATION")


def run_three_arm_batch(
    catalog: QueryCatalog,
    arm_map: ThreeArmConfigMap,
    *,
    top_k: int = 5,
    engine_by_arm: Mapping[str, SemanticIndexEngine] | None = None,
    engine_factory: Callable[[str], SemanticIndexEngine] | None = None,
) -> ThreeArmBatchResult:
    """Execute isolated read-only batch retrieval for all three charter arms.

    Preflights all three profile bundles, manifests, and distinct semantic
    spaces before executing any query. Any failure aborts the entire comparison.
    """
    if not isinstance(catalog, QueryCatalog):
        raise TypeError("QUERY_CATALOG_REQUIRED")
    if not isinstance(arm_map, ThreeArmConfigMap):
        raise TypeError("THREE_ARM_MAP_REQUIRED")
    validated_top_k = validate_lab_top_k(top_k)

    prepared_arms: list[
        tuple[
            ThreeArmConfigEntry,
            SyntheticProfileBundle,
            MultiSourceManifest,
            SemanticIndexEngine,
        ]
    ] = []
    seen_space_ids: set[str] = set()
    seen_generation_ids: set[str] = set()

    for entry in arm_map.arms:
        bundle = load_synthetic_profile_bundle(entry.model_profile_json)
        expected_profile_id = ARM_TO_PROFILE_ID[entry.arm_id]
        if bundle.profile.profile_id != expected_profile_id:
            raise ValueError(
                f"THREE_ARM_PROFILE_ID_MISMATCH:{entry.arm_id}:"
                f"{bundle.profile.profile_id}!={expected_profile_id}"
            )
        manifest = load_multi_source_manifest(entry.manifest)

        if engine_by_arm is not None:
            if entry.arm_id not in engine_by_arm:
                raise ValueError(f"THREE_ARM_ENGINE_MISSING:{entry.arm_id}")
            engine = engine_by_arm[entry.arm_id]
        elif engine_factory is not None:
            engine = engine_factory(entry.arm_id)
        else:
            engine = PersistentLocalSemanticIndexEngine()

        if not callable(getattr(engine, "build_generation_spec", None)) or not callable(
            getattr(engine, "query", None)
        ):
            raise ValueError(f"ENGINE_QUERY_REQUIRED:{entry.arm_id}")

        spec = engine.build_generation_spec(bundle.semantic_space)
        if getattr(spec, "space", None) != bundle.semantic_space:
            raise ValueError(f"GENERATION_SEMANTIC_SPACE_MISMATCH:{entry.arm_id}")
        if bundle.space_id in seen_space_ids or spec.space_id in seen_space_ids:
            raise ValueError("THREE_ARM_SEMANTIC_SPACE_COLLISION")
        if spec.generation_id in seen_generation_ids:
            raise ValueError("THREE_ARM_GENERATION_COLLISION")
        seen_space_ids.add(bundle.space_id)
        seen_generation_ids.add(spec.generation_id)
        prepared_arms.append((entry, bundle, manifest, engine))

    arm_results: list[ThreeArmBatchArmResult] = []
    for entry, bundle, manifest, engine in prepared_arms:
        single_result = run_batch_retrieval(
            catalog,
            manifest,
            entry.index_root,
            runtime=bundle.runtime,
            semantic_space=bundle.semantic_space,
            engine=engine,
            top_k=validated_top_k,
            profile_id=bundle.profile.profile_id,
        )
        arm_results.append(
            ThreeArmBatchArmResult(
                arm_id=entry.arm_id,
                profile_id=bundle.profile.profile_id,
                model_identity=bundle.semantic_space.model_identity,
                space_id=single_result.space_id,
                generation_id=single_result.generation_id,
                embedding_dim=bundle.profile.embedding_dim,
                row_width_bytes=bundle.row_width_bytes,
                manifest_digest=manifest.manifest_digest,
                catalog_digest=catalog.catalog_digest,
                query_count=len(catalog.query_ids),
                candidate_count=single_result.total_candidate_count,
                batch_result=single_result,
                fake_runtime_used=True,
                synthetic_only=True,
                authentic_model_evidence=False,
            )
        )

    return ThreeArmBatchResult(
        catalog_id=catalog.catalog_id,
        catalog_digest=catalog.catalog_digest,
        query_ids=catalog.query_ids,
        top_k=validated_top_k,
        arm_map_digest=arm_map.arm_map_digest,
        arms=tuple(arm_results),
        synthetic_only=True,
        authentic_model_evidence=False,
    )


__all__ = [
    "ARM_TO_PROFILE_ID",
    "ARM_VIP_V1_BASE",
    "ARM_VIP_V2_BASE",
    "ARM_VIP_V2_SO400M",
    "DECLARED_ARM_ORDER",
    "MAX_ARM_MAP_BYTES",
    "PROFILE_ID_TO_ARM",
    "THREE_ARM_MAP_SCHEMA_VERSION",
    "ThreeArmBatchArmResult",
    "ThreeArmBatchResult",
    "ThreeArmConfigEntry",
    "ThreeArmConfigMap",
    "load_three_arm_map",
    "parse_three_arm_map_bytes",
    "parse_three_arm_map_mapping",
    "run_three_arm_batch",
]
