"""Deterministic semantic-space and generation identity for the persistent index.

Authority: `docs/superpowers/specs/2026-09-15-persistent-local-semantic-index-design.md`
(approved design), sections 6 and 19.  A generation is immutable with respect to
its semantic embedding space and sampling policy; any change to either requires a
new generation.  Identity is derived, never wall-clock based, so two independent
builds of the same frozen assets agree.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

# --------------------------------------------------------------------------
# v1 fixed policy values (approved design section 19 / plan Task 1)
# --------------------------------------------------------------------------

SCHEMA_VERSION = 1
SAMPLING_POLICY_ID = "coarse-pts-4.5s"
SAMPLING_POLICY_VERSION = 1
SAMPLING_INTERVAL_SECONDS = 4.5
SELECTED_STREAM_POLICY = "first-video-stream"

#: Exact SigLIP text-preprocessing contract proven by the preserved spike.
#: `padding="max_length"` is the trained contract; omitting it caused 7/7 MISS.
TEXT_PREPROCESSING_CONTRACT = "padding=max_length"

EMBEDDING_DIM = 768
EMBEDDING_DTYPE = "float32"
VECTOR_NORMALIZATION = "l2"

#: Required local processor/config assets whose identity participates in the
#: processor digest.  Hashed in lexical filename order, name plus content.
PROCESSOR_ASSETS: tuple[str, ...] = (
    "config.json",
    "preprocessor_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "spiece.model",
)

MANIFEST_SCHEMA_PATH = "manifest.json"


@dataclass(frozen=True)
class SemanticSpace:
    """Immutable identity of the embedding space a generation was built in."""

    model_identity: str
    frozen_revision: str
    weights_sha256: str
    processor_digest: str
    image_preprocessing_digest: str
    text_preprocessing_contract: str
    embedding_dim: int
    dtype: str
    normalization: str


@dataclass(frozen=True)
class GenerationSpec:
    """Immutable generation identity: semantic space plus sampling policy."""

    schema_version: int
    generation_id: str
    space: SemanticSpace
    space_id: str
    sampling_policy_id: str
    sampling_policy_version: int
    sampling_interval_seconds: float
    selected_stream_policy: str


# --------------------------------------------------------------------------
# digests
# --------------------------------------------------------------------------


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json(payload: object) -> str:
    """Canonical JSON: sorted keys, no insignificant whitespace, UTF-8 safe."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_file(path: Path) -> str:
    """SHA-256 of the exact bytes of ``path``."""
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"FILE_NOT_FOUND:{path.name}")
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def digest_processor_assets(model_root: Path) -> str:
    """Digest of the required local processor assets, name- and content-bound.

    Missing required assets fail closed with ``PROCESSOR_ASSET_MISSING:<name>``
    rather than silently producing a weaker identity.
    """
    root = Path(model_root)
    hasher = hashlib.sha256()
    for name in sorted(PROCESSOR_ASSETS):
        asset = root / name
        if not asset.is_file():
            raise ValueError(f"PROCESSOR_ASSET_MISSING:{name}")
        hasher.update(name.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(digest_file(asset).encode("ascii"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def digest_image_preprocessing_assets(model_root: Path) -> str:
    """``image_preprocessing_digest`` is the digest of ``preprocessor_config.json``."""
    asset = Path(model_root) / "preprocessor_config.json"
    if not asset.is_file():
        raise ValueError("PROCESSOR_ASSET_MISSING:preprocessor_config.json")
    return digest_file(asset)


# --------------------------------------------------------------------------
# identity derivation
# --------------------------------------------------------------------------


def semantic_space_id(space: SemanticSpace) -> str:
    """Deterministic 64-hex identity of a semantic space."""
    return _sha256_bytes(canonical_json(asdict(space)).encode("utf-8"))


def generation_id_for(
    *,
    space_id: str,
    schema_version: int,
    sampling_policy_id: str,
    sampling_policy_version: int,
    sampling_interval_seconds: float,
    selected_stream_policy: str,
) -> str:
    """Deterministic generation identity from semantic space + sampling policy."""
    return _sha256_bytes(
        canonical_json(
            {
                "space_id": space_id,
                "schema_version": schema_version,
                "sampling_policy_id": sampling_policy_id,
                "sampling_policy_version": sampling_policy_version,
                "sampling_interval_seconds": sampling_interval_seconds,
                "selected_stream_policy": selected_stream_policy,
            }
        ).encode("utf-8")
    )


def build_generation_spec(
    space: SemanticSpace, *, sampling_interval_seconds: float = SAMPLING_INTERVAL_SECONDS
) -> GenerationSpec:
    """Build the v1 generation spec for ``space`` (fixed sampling policy)."""
    space_id = semantic_space_id(space)
    return GenerationSpec(
        schema_version=SCHEMA_VERSION,
        generation_id=generation_id_for(
            space_id=space_id,
            schema_version=SCHEMA_VERSION,
            sampling_policy_id=SAMPLING_POLICY_ID,
            sampling_policy_version=SAMPLING_POLICY_VERSION,
            sampling_interval_seconds=sampling_interval_seconds,
            selected_stream_policy=SELECTED_STREAM_POLICY,
        ),
        space=space,
        space_id=space_id,
        sampling_policy_id=SAMPLING_POLICY_ID,
        sampling_policy_version=SAMPLING_POLICY_VERSION,
        sampling_interval_seconds=sampling_interval_seconds,
        selected_stream_policy=SELECTED_STREAM_POLICY,
    )


# --------------------------------------------------------------------------
# fail-closed compatibility
# --------------------------------------------------------------------------

_SPACE_FIELDS: tuple[str, ...] = (
    "model_identity",
    "frozen_revision",
    "weights_sha256",
    "processor_digest",
    "image_preprocessing_digest",
    "text_preprocessing_contract",
    "embedding_dim",
    "dtype",
    "normalization",
)


def assert_same_space(expected: SemanticSpace, live: SemanticSpace) -> None:
    """Fail closed naming the *first* mismatched semantic-space field."""
    for field in _SPACE_FIELDS:
        left = getattr(expected, field)
        right = getattr(live, field)
        if left != right:
            raise ValueError(
                f"SEMANTIC_SPACE_MISMATCH:{field}:expected={left!r}:live={right!r}"
            )


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------


def _manifest_payload(spec: GenerationSpec, committed_rows: int) -> dict[str, object]:
    return {
        "schema_version": spec.schema_version,
        "generation_id": spec.generation_id,
        "space_id": spec.space_id,
        "space": asdict(spec.space),
        "sampling_policy_id": spec.sampling_policy_id,
        "sampling_policy_version": spec.sampling_policy_version,
        "sampling_interval_seconds": spec.sampling_interval_seconds,
        "selected_stream_policy": spec.selected_stream_policy,
        "embedding_dim": spec.space.embedding_dim,
        "dtype": spec.space.dtype,
        "normalization": spec.space.normalization,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "committed_rows": int(committed_rows),
    }


def write_manifest(path: Path, spec: GenerationSpec, committed_rows: int) -> None:
    """Atomically write the generation manifest.

    Atomicity is via write-to-temp + ``os.replace`` in the same directory, so a
    crash mid-write cannot leave a truncated manifest.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _manifest_payload(spec, committed_rows)
    if path.is_file():
        # Preserve the original created_at across refreshes; this field is
        # informational and must not appear to move on every commit.
        try:
            prior = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(prior, dict) and prior.get("created_at"):
                payload["created_at"] = prior["created_at"]
        except (OSError, ValueError):
            pass
    encoded = (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    handle, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".manifest-", suffix=".tmp")
    try:
        with os.fdopen(handle, "wb") as fh:
            fh.write(encoded)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def read_manifest_committed_rows(manifest: Mapping[str, object]) -> int:
    """Read the informational committed-row mirror from a loaded manifest."""
    value = manifest.get("committed_rows")
    if not isinstance(value, int):
        raise ValueError("MANIFEST_COMMITTED_ROWS_NOT_INTEGER")
    return value


def load_manifest(path: Path) -> dict[str, object]:
    """Load and structurally validate a generation manifest."""
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"MANIFEST_MISSING:{path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"MANIFEST_UNREADABLE:{path.name}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"MANIFEST_NOT_OBJECT:{path.name}")
    if not isinstance(payload.get("space"), dict):
        raise ValueError("MANIFEST_SPACE_NOT_OBJECT")
    return payload


def validate_manifest_compatibility(
    manifest: Mapping[str, object], live: GenerationSpec
) -> None:
    """Fail closed naming the first mismatched generation field.

    The manifest is immutable semantic/sampling identity; it is deliberately not
    an authority for crash recovery or the current append boundary.
    """
    scalars: tuple[tuple[str, object], ...] = (
        ("schema_version", live.schema_version),
        ("generation_id", live.generation_id),
        ("space_id", live.space_id),
        ("sampling_policy_id", live.sampling_policy_id),
        ("sampling_policy_version", live.sampling_policy_version),
        ("sampling_interval_seconds", live.sampling_interval_seconds),
        ("selected_stream_policy", live.selected_stream_policy),
    )
    for field, expected in scalars:
        if field not in manifest:
            raise ValueError(f"MANIFEST_FIELD_MISSING:{field}")
        if manifest[field] != expected:
            raise ValueError(
                f"MANIFEST_MISMATCH:{field}:expected={expected!r}:found={manifest[field]!r}"
            )

    space = manifest.get("space")
    if not isinstance(space, Mapping):
        raise ValueError("MANIFEST_SPACE_NOT_OBJECT")
    for field in _SPACE_FIELDS:
        if field not in space:
            raise ValueError(f"MANIFEST_FIELD_MISSING:space.{field}")
        expected_value = getattr(live.space, field)
        if space[field] != expected_value:
            raise ValueError(
                f"MANIFEST_MISMATCH:{field}:"
                f"expected={expected_value!r}:found={space[field]!r}"
            )


def generation_spec_from_manifest(manifest: Mapping[str, object]) -> GenerationSpec:
    """Reconstruct the immutable spec pinned by a manifest.

    Used by the writer's mirror refresh so that refreshing ``committed_rows``
    reuses the manifest's exact recorded identity instead of re-deriving it; a
    mirror refresh must never be able to rewrite generation identity.
    """
    space_payload = manifest.get("space")
    if not isinstance(space_payload, Mapping):
        raise ValueError("MANIFEST_SPACE_NOT_OBJECT")
    missing = [field for field in _SPACE_FIELDS if field not in space_payload]
    if missing:
        raise ValueError(f"MANIFEST_FIELD_MISSING:space.{missing[0]}")
    return GenerationSpec(
        schema_version=int(manifest["schema_version"]),
        generation_id=str(manifest["generation_id"]),
        space=SemanticSpace(**{field: space_payload[field] for field in _SPACE_FIELDS}),
        space_id=str(manifest["space_id"]),
        sampling_policy_id=str(manifest["sampling_policy_id"]),
        sampling_policy_version=int(manifest["sampling_policy_version"]),
        sampling_interval_seconds=float(manifest["sampling_interval_seconds"]),
        selected_stream_policy=str(manifest["selected_stream_policy"]),
    )
