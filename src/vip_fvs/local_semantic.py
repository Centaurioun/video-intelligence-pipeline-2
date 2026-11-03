"""Checked local-semantic runtime seam for the FVS.

This module is intentionally *not* a model loader.  A caller supplies an
already checked local runtime: ordered image/text embedding callables and the
immutable :class:`SemanticSpace` identity they implement.  The adapter only
connects that runtime to :mod:`vip_fvs.retrieval_adapter`; model acquisition,
device selection, digest checking, and offline enforcement belong to the
``persistent_local_index`` runtime layer.

Fake execution is available only when explicitly requested.  A real-mode
invocation with a missing callable or semantic-space identity fails closed and
never substitutes the fake runtime or a remote/provider fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

from .retrieval_adapter import (
    RetrievalResult,
    fake_image_embedder,
    fake_semantic_space,
    fake_text_embedder,
    retrieve,
)
from .semantic_index import SemanticSpace


EmbedImages = Callable[[Sequence[Path]], np.ndarray]
EmbedTexts = Callable[[Sequence[str]], np.ndarray]


class LocalSemanticRuntimeError(ValueError):
    """Fail-closed configuration or invocation of the local semantic seam."""


@dataclass(frozen=True)
class CheckedLocalSemanticRuntime:
    """An embedding runtime checked before it crosses the FVS boundary.

    ``fake`` is a provenance flag, not an implicit fallback switch.  For a
    real runtime it must be false and all three real components must be
    supplied.  ``runtime_identity`` is caller-owned metadata (for example a
    runtime/version digest) and is retained without interpreting it as a model
    identity; the semantic-space object remains the identity authority.
    """

    image_embedder: EmbedImages
    text_embedder: EmbedTexts
    semantic_space: SemanticSpace
    fake: bool = False
    runtime_identity: str | None = None

    @property
    def fake_embedder(self) -> bool:
        """Compatibility spelling used by the existing retrieval seam."""
        return self.fake

    def __post_init__(self) -> None:
        if not callable(self.image_embedder):
            raise LocalSemanticRuntimeError("IMAGE_EMBEDDER_REQUIRED")
        if not callable(self.text_embedder):
            raise LocalSemanticRuntimeError("TEXT_EMBEDDER_REQUIRED")
        if not isinstance(self.semantic_space, SemanticSpace):
            raise LocalSemanticRuntimeError("SEMANTIC_SPACE_REQUIRED")
        if not isinstance(self.fake, bool):
            raise LocalSemanticRuntimeError("INVALID_FAKE_MODE")


def checked_runtime(
    *,
    image_embedder: EmbedImages | None,
    text_embedder: EmbedTexts | None,
    semantic_space: SemanticSpace | None,
    fake: bool = False,
    runtime_identity: str | None = None,
) -> CheckedLocalSemanticRuntime:
    """Validate and construct the explicit runtime seam.

    The function deliberately does not discover, import, instantiate, or
    download a model.  ``fake=True`` still requires an explicit caller choice;
    use :func:`fake_runtime` for the deterministic synthetic implementation.
    """
    if image_embedder is None:
        raise LocalSemanticRuntimeError("IMAGE_EMBEDDER_REQUIRED")
    if text_embedder is None:
        raise LocalSemanticRuntimeError("TEXT_EMBEDDER_REQUIRED")
    if semantic_space is None:
        raise LocalSemanticRuntimeError("SEMANTIC_SPACE_REQUIRED")
    return CheckedLocalSemanticRuntime(
        image_embedder=image_embedder,
        text_embedder=text_embedder,
        semantic_space=semantic_space,
        fake=fake,
        runtime_identity=runtime_identity,
    )


def build_local_semantic_runtime(config: Any) -> CheckedLocalSemanticRuntime:
    """Build a checked runtime from an explicit, already-local configuration.

    This is a compatibility seam for coordinators and tests.  It deliberately
    accepts callables supplied by the caller; it does not import Transformers,
    download weights, select a device, or manufacture a fake runtime.  A
    configuration may provide ``runtime_factory`` (returning a checked
    runtime), or the three explicit ``image_embedder``, ``text_embedder`` and
    ``semantic_space`` fields consumed by :func:`checked_runtime`.
    """
    if config is None:
        raise LocalSemanticRuntimeError("LOCAL_SEMANTIC_CONFIG_REQUIRED")
    factory = config.get("runtime_factory") if isinstance(config, dict) else getattr(config, "runtime_factory", None)
    if factory is not None:
        if not callable(factory):
            raise LocalSemanticRuntimeError("RUNTIME_FACTORY_REQUIRED")
        runtime = factory()
        if not isinstance(runtime, CheckedLocalSemanticRuntime):
            raise LocalSemanticRuntimeError("CHECKED_RUNTIME_REQUIRED")
        if runtime.fake:
            raise LocalSemanticRuntimeError("REAL_RUNTIME_MUST_NOT_BE_FAKE")
        return runtime
    def value(name: str) -> Any:
        return config.get(name) if isinstance(config, dict) else getattr(config, name, None)
    runtime = checked_runtime(
        image_embedder=value("image_embedder"), text_embedder=value("text_embedder"),
        semantic_space=value("semantic_space"), fake=False,
        runtime_identity=value("runtime_identity"),
    )
    return runtime


def fake_runtime() -> CheckedLocalSemanticRuntime:
    """Return the visibly synthetic runtime used by local FVS tests."""
    return CheckedLocalSemanticRuntime(
        image_embedder=fake_image_embedder,
        text_embedder=fake_text_embedder,
        semantic_space=fake_semantic_space(),
        fake=True,
        runtime_identity="vip-fvs-fake-runtime/v1",
    )


@dataclass(frozen=True)
class LocalSemanticResult:
    """Retrieval output plus the checked runtime boundary provenance."""

    retrieval: RetrievalResult
    runtime_identity: str | None
    fake: bool

    @property
    def generation_id(self) -> str:
        return self.retrieval.generation_id

    @property
    def space_id(self) -> str:
        return self.retrieval.space_id

    @property
    def hits(self) -> tuple[Any, ...]:
        return self.retrieval.hits

    @property
    def invocation_ref(self) -> str:
        return self.retrieval.invocation_ref

    @property
    def fake_embedder_used(self) -> bool:
        return self.retrieval.fake_embedder_used


def retrieve_local_semantic(
    source_binding: Any,
    query: str | Sequence[str],
    index_root: Path,
    *,
    runtime: CheckedLocalSemanticRuntime,
    top_k: int = 5,
    invocation_ref: str = "fvs:local-semantic",
) -> LocalSemanticResult:
    """Run FVS retrieval through an already checked local runtime.

    There is no model fallback: a real runtime is passed to the existing
    persistent-index adapter exactly as supplied.  The source binding and
    invocation reference remain owned by the existing retrieval contract.
    """
    if not isinstance(runtime, CheckedLocalSemanticRuntime):
        raise LocalSemanticRuntimeError("CHECKED_RUNTIME_REQUIRED")
    result = retrieve(
        source_binding,
        query,
        Path(index_root),
        top_k=top_k,
        fake_embedder=runtime.fake,
        image_embedder=runtime.image_embedder,
        text_embedder=runtime.text_embedder,
        semantic_space=runtime.semantic_space,
        invocation_ref=invocation_ref,
    )
    return LocalSemanticResult(result, runtime.runtime_identity, runtime.fake)


@dataclass(frozen=True)
class LocalSemanticRuntimeAdapter:
    """Small stateful façade for coordinators that retain a checked runtime."""

    runtime: CheckedLocalSemanticRuntime

    def retrieve(
        self,
        source_binding: Any,
        query: str | Sequence[str],
        index_root: Path,
        *,
        top_k: int = 5,
        invocation_ref: str = "fvs:local-semantic",
    ) -> LocalSemanticResult:
        return retrieve_local_semantic(
            source_binding,
            query,
            index_root,
            runtime=self.runtime,
            top_k=top_k,
            invocation_ref=invocation_ref,
        )


# Coordinator-friendly short names.  These aliases do not create another
# implementation or another model-loading path.
LocalSemanticRuntime = CheckedLocalSemanticRuntime
run_local_semantic = retrieve_local_semantic


__all__ = [
    "CheckedLocalSemanticRuntime",
    "LocalSemanticResult",
    "LocalSemanticRuntime",
    "LocalSemanticRuntimeError",
    "LocalSemanticRuntimeAdapter",
    "checked_runtime",
    "build_local_semantic_runtime",
    "fake_runtime",
    "retrieve_local_semantic",
    "run_local_semantic",
]
