"""Fail-closed boundary for an already-local semantic model.

This module is deliberately a loader *boundary*, not a model implementation.  It
validates the complete local identity before opening a runtime and validates it
again immediately after the open.  Tests can provide a loader stub; no
Transformers/Torch import or model acquisition is performed here.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .model_space import PROCESSOR_ASSETS, digest_processor_assets

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVISION = re.compile(r"^[0-9a-f]{40}$")
_SUPPORTED_DEVICES = frozenset({"cpu", "mps"})


@dataclass(frozen=True)
class LocalModelSpec:
    """The immutable identity required to open a local model."""

    model_root: Path
    weights_sha256: str
    processor_digest: str
    frozen_revision: str
    device: str = "cpu"
    offline_only: bool = True
    weights_name: str = "model.safetensors"


@dataclass(frozen=True)
class LocalModelHandle:
    """Opened runtime plus the identity that was checked around the open."""

    runtime: Any
    spec: LocalModelSpec
    identity: tuple[str, str, str]

    # Compatibility-facing identity fields.  Keeping these as properties means
    # callers can use the small ``load_local_model`` contract without losing
    # the richer immutable ``LocalModelSpec`` used by ``open_local_model``.
    @property
    def model_root(self) -> Path:
        return self.spec.model_root

    @property
    def frozen_revision(self) -> str:
        return self.spec.frozen_revision

    @property
    def weights_sha256(self) -> str:
        return self.spec.weights_sha256

    @property
    def processor_digest(self) -> str:
        return self.spec.processor_digest


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _revision_on_disk(root: Path) -> str | None:
    """Read a revision from the small, local manifest forms used by fixtures."""
    for name in ("revision.txt", "revision", "model_revision"):
        candidate = root / name
        if candidate.is_file():
            value = candidate.read_text(encoding="utf-8").strip()
            if value:
                return value
    manifest = root / "manifest.json"
    if manifest.is_file():
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError("MODEL_MANIFEST_INVALID") from exc
        if isinstance(payload, Mapping):
            for key in ("revision", "frozen_revision", "commit", "model_revision"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    return value
    return None


def _validate_hex(value: str, field: str) -> None:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{field}_MUST_BE_LOWERCASE_SHA256")


def validate_local_model(spec: LocalModelSpec) -> tuple[str, str, str]:
    """Validate root, exact weights/processor/revision, device, and offline mode.

    The returned tuple is the observed ``(weights, processor, revision)``
    identity and is suitable for an immediately-before/after comparison.
    """
    root = Path(spec.model_root)
    if not root.is_absolute():
        raise ValueError("MODEL_ROOT_MUST_BE_ABSOLUTE")
    if root != root.resolve(strict=False):
        raise ValueError("MODEL_ROOT_MUST_BE_CANONICAL")
    if not root.is_dir():
        raise ValueError("MODEL_ROOT_NOT_FOUND")
    if spec.device not in _SUPPORTED_DEVICES:
        raise ValueError(f"UNSUPPORTED_DEVICE:{spec.device!r}")
    if spec.offline_only is not True:
        raise ValueError("MODEL_MUST_BE_OFFLINE_ONLY")
    _validate_hex(spec.weights_sha256, "WEIGHTS_DIGEST")
    _validate_hex(spec.processor_digest, "PROCESSOR_DIGEST")
    if not isinstance(spec.frozen_revision, str) or not _REVISION.fullmatch(spec.frozen_revision):
        raise ValueError("MODEL_REVISION_MUST_BE_40_HEX")
    if not isinstance(spec.weights_name, str) or Path(spec.weights_name).name != spec.weights_name:
        raise ValueError("WEIGHTS_NAME_MUST_BE_BASENAME")

    weights = root / spec.weights_name
    if not weights.is_file():
        raise ValueError("MODEL_WEIGHTS_NOT_FOUND")
    observed_weights = _sha256(weights)
    if observed_weights != spec.weights_sha256:
        raise ValueError("MODEL_WEIGHTS_DIGEST_MISMATCH")
    try:
        observed_processor = digest_processor_assets(root)
    except ValueError as exc:
        raise ValueError(str(exc).replace("PROCESSOR_ASSET_MISSING", "MODEL_PROCESSOR_ASSET_MISSING", 1)) from exc
    if observed_processor != spec.processor_digest:
        raise ValueError("MODEL_PROCESSOR_DIGEST_MISMATCH")
    observed_revision = _revision_on_disk(root)
    # Some approved immutable acquisition roots carry the revision in their
    # canonical directory name rather than a mutable sidecar file.  Accept
    # that form only when it exactly equals the explicit frozen revision;
    # arbitrary roots without revision metadata remain fail-closed.
    if observed_revision is None and root.name == spec.frozen_revision:
        observed_revision = spec.frozen_revision
    if observed_revision is None:
        raise ValueError("MODEL_REVISION_NOT_FOUND")
    if observed_revision != spec.frozen_revision:
        raise ValueError("MODEL_REVISION_MISMATCH")
    return observed_weights, observed_processor, observed_revision


def open_local_model(
    spec: LocalModelSpec,
    loader: Callable[[Path, str], Any] | None = None,
) -> LocalModelHandle:
    """Open through an injected loader, with runtime-open identity revalidation.

    ``loader`` is intentionally required for a real open; omitting it returns a
    handle with a ``None`` runtime for dry-run/contract tests and never loads a
    model.  A mutation during the injected open fails closed.
    """
    before = validate_local_model(spec)
    runtime = loader(spec.model_root, spec.device) if loader is not None else None
    after = validate_local_model(spec)
    if before != after:
        raise ValueError("MODEL_IDENTITY_CHANGED_DURING_OPEN")
    return LocalModelHandle(runtime=runtime, spec=spec, identity=after)


def _mps_available() -> bool:
    """Return MPS availability without making runtime loading mandatory."""
    try:
        import torch  # type: ignore[import-not-found]
    except ImportError:
        return False
    return bool(torch.backends.mps.is_available())


def _load_runtime(
    model_root: Path,
    *,
    device: str,
    local_files_only: bool,
    revision: str,
) -> Any:
    """Runtime seam; the production runtime is intentionally not bundled here."""
    raise RuntimeError("LOCAL_MODEL_RUNTIME_UNAVAILABLE")


def _validate_compat_identity(
    model_root: Path,
    *,
    expected_weights_sha256: str,
    expected_revision: str,
) -> tuple[str, str, str]:
    """Validate the RED-test compatibility API, including non-hex fixture revisions."""
    root = Path(model_root)
    if not root.is_absolute():
        raise ValueError("MODEL_ROOT_MUST_BE_ABSOLUTE")
    if root != root.resolve(strict=False):
        raise ValueError("MODEL_ROOT_MUST_BE_CANONICAL")
    if not root.is_dir():
        raise ValueError("MODEL_ROOT_NOT_FOUND")
    _validate_hex(expected_weights_sha256, "WEIGHTS_DIGEST")
    if not isinstance(expected_revision, str) or not expected_revision:
        raise ValueError("MODEL_REVISION_REQUIRED")
    weights = root / "model.safetensors"
    if not weights.is_file():
        raise ValueError("MODEL_WEIGHTS_NOT_FOUND")
    observed_weights = _sha256(weights)
    if observed_weights != expected_weights_sha256:
        raise ValueError("MODEL_WEIGHTS_DIGEST_MISMATCH")
    # Keep the exact processor error for this public compatibility seam.
    observed_processor = digest_processor_assets(root)
    observed_revision = _revision_on_disk(root)
    if observed_revision is None and root.name == expected_revision:
        observed_revision = expected_revision
    if observed_revision is None:
        raise ValueError("MODEL_REVISION_NOT_FOUND")
    if observed_revision != expected_revision:
        raise ValueError("MODEL_REVISION_MISMATCH")
    return observed_weights, observed_processor, observed_revision


def load_local_model(
    model_root: Path,
    *,
    expected_weights_sha256: str,
    expected_revision: str,
    device: str = "cpu",
    offline: bool = True,
) -> LocalModelHandle:
    """Load a frozen local bundle through an injectable, offline-only runtime seam.

    All byte/processor/revision checks and device availability checks happen
    before ``_load_runtime``.  Requested MPS is never silently changed to CPU.
    """
    if offline is not True:
        raise ValueError("OFFLINE_REQUIRED")
    if device not in _SUPPORTED_DEVICES:
        raise ValueError(f"UNSUPPORTED_DEVICE:{device!r}")
    if device == "mps" and not _mps_available():
        raise RuntimeError("MPS_REQUESTED_BUT_UNAVAILABLE")
    identity = _validate_compat_identity(
        model_root,
        expected_weights_sha256=expected_weights_sha256,
        expected_revision=expected_revision,
    )
    spec = LocalModelSpec(
        model_root=Path(model_root).resolve(),
        weights_sha256=identity[0],
        processor_digest=identity[1],
        frozen_revision=identity[2],
        device=device,
        offline_only=True,
    )
    runtime = _load_runtime(
        spec.model_root,
        device=device,
        local_files_only=True,
        revision=expected_revision,
    )
    try:
        after = _validate_compat_identity(
            spec.model_root,
            expected_weights_sha256=spec.weights_sha256,
            expected_revision=spec.frozen_revision,
        )
    except (OSError, ValueError) as exc:
        raise ValueError("MODEL_REVALIDATION_FAILED") from exc
    if after != identity:
        raise ValueError("MODEL_REVALIDATION_FAILED")
    return LocalModelHandle(runtime=runtime, spec=spec, identity=after)


def revalidate_local_model(handle: LocalModelHandle) -> LocalModelHandle:
    """Recheck a previously opened compatibility handle and return it."""
    try:
        observed = _validate_compat_identity(
            handle.spec.model_root,
            expected_weights_sha256=handle.spec.weights_sha256,
            expected_revision=handle.spec.frozen_revision,
        )
    except (OSError, ValueError) as exc:
        raise ValueError("MODEL_REVALIDATION_FAILED") from exc
    if observed != handle.identity:
        raise ValueError("MODEL_REVALIDATION_FAILED")
    return handle


# Short aliases make the boundary convenient without hiding the explicit checks.
validate_model = validate_local_model
open_model = open_local_model

__all__ = [
    "LocalModelHandle",
    "LocalModelSpec",
    "open_local_model",
    "open_model",
    "load_local_model",
    "revalidate_local_model",
    "validate_local_model",
    "validate_model",
]
