"""Deterministic orchestration for an explicit multi-source manifest.

This module checks each manifest entry's use authorization and current bytes,
then delegates indexing to the stable semantic engine. It never discovers
sources or performs query, refinement, editorial, or render work.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Callable, Mapping, Sequence, Any

from .semantic_index import ImageEmbedder, SemanticIndexEngine, SemanticSpace
from .source_adapter import MultiSourceManifest, SourceManifestEntry
from .source_adapter import _canonical_manifest_bytes, _manifest_body
from .corpus_admission import (
    AdmissionBinding, SyntheticPreflightContext, check_synthetic_preflight,
    require_synthetic_preflight,
)


@dataclass(frozen=True)
class MultiSourceEntryResult:
    """Observed indexing outcome for one manifest entry."""

    revision_id: str
    source_path: Path
    source_sha256: str
    disposition: str
    row_start: int | None
    row_end: int | None
    error: str | None


@dataclass(frozen=True)
class MultiSourceIndexResult:
    """Deterministic generation identity and ordered per-entry outcomes."""

    manifest_digest: str
    generation_id: str
    space_id: str
    results: tuple[MultiSourceEntryResult, ...]


SourceUseAuthorizer = Callable[[SourceManifestEntry], bool]


def _preflight_batch(
    entries: Sequence[SourceManifestEntry], *, attestations: Sequence[Mapping[str, Any]] | None,
    authorizations: Sequence[Mapping[str, Any]] | None, operation: str,
    output_root: Path, manifest_digest: str, plan_digest: str | None = None,
) -> SyntheticPreflightContext | None:
    """Check an optional synthetic-only admission envelope before source I/O."""
    if attestations is None and authorizations is None:
        return None
    if attestations is None or authorizations is None or len(entries) != len(authorizations):
        from .corpus_admission import CorpusAdmissionError
        raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
    if not entries or any(not isinstance(entry, SourceManifestEntry) for entry in entries):
        from .corpus_admission import CorpusAdmissionError
        raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
    try:
        expected_manifest_digest = hashlib.sha256(
            _canonical_manifest_bytes(_manifest_body(tuple(entries)))
        ).hexdigest()
    except (TypeError, ValueError, AttributeError) as exc:
        from .corpus_admission import CorpusAdmissionError
        raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID") from exc
    if manifest_digest != expected_manifest_digest:
        from .corpus_admission import CorpusAdmissionError
        raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
    bindings = tuple(AdmissionBinding(
        revision_id=entry.revision_id, source_sha256=entry.source_sha256,
        authorization=authorization, locator=str(entry.source_path),
    ) for entry, authorization in zip(entries, authorizations))
    context = check_synthetic_preflight(
        attestations, bindings=bindings, operation=operation, output_root=output_root,
        plan_digest=plan_digest, manifest_digest=expected_manifest_digest,
    )
    require_synthetic_preflight(
        context, bindings=bindings, operation=operation, output_root=output_root,
        plan_digest=plan_digest, manifest_digest=expected_manifest_digest,
    )
    return context


def _preflight_source_bytes(
    entries: Sequence[SourceManifestEntry], authorize_source: SourceUseAuthorizer,
) -> None:
    """Validate every source in an opted-in batch before any engine write."""
    from .corpus_admission import CorpusAdmissionError
    for entry in entries:
        try:
            if authorize_source(entry) is not True:
                raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        except CorpusAdmissionError:
            raise
        except Exception as exc:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID") from exc
        path = entry.source_path
        try:
            if path.is_symlink() or not path.is_file() or _digest_file(path) != entry.source_sha256:
                raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        except CorpusAdmissionError:
            raise
        except OSError as exc:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID") from exc


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _entry_result(
    entry: SourceManifestEntry,
    disposition: str,
    *,
    row_start: int | None = None,
    row_end: int | None = None,
    error: str | None = None,
) -> MultiSourceEntryResult:
    return MultiSourceEntryResult(
        revision_id=entry.revision_id,
        source_path=entry.source_path,
        source_sha256=entry.source_sha256,
        disposition=disposition,
        row_start=row_start,
        row_end=row_end,
        error=error,
    )


def _summary_entry(summary):
    """Accept the stable engine's one-source summary and small test seams."""
    results = getattr(summary, "results", None)
    if results is not None:
        if len(results) != 1:
            raise ValueError("ENGINE_RESULT_CARDINALITY_MISMATCH")
        return results[0]
    return summary


def index_multi_source_manifest(
    manifest: MultiSourceManifest,
    *,
    index_root: Path,
    engine: SemanticIndexEngine,
    semantic_space: SemanticSpace,
    image_embedder: ImageEmbedder,
    authorize_source: SourceUseAuthorizer,
    synthetic_attestations: Sequence[Mapping[str, Any]] | None = None,
    synthetic_authorizations: Sequence[Mapping[str, Any]] | None = None,
) -> MultiSourceIndexResult:
    """Index exactly the authorized, digest-current files in ``manifest``.

    ``authorize_source`` is mandatory and is called before inspecting or reading
    each source path. A false decision records a refusal row and proceeds to the
    next independent manifest entry. Manifest membership never grants source-use
    authorization.
    """
    if not isinstance(manifest, MultiSourceManifest):
        raise TypeError("manifest must be MultiSourceManifest")
    if not callable(authorize_source):
        raise ValueError("explicit source-use authorization is required")
    if not callable(getattr(engine, "build_generation_spec", None)) or not callable(
        getattr(engine, "index_source", None)
    ):
        raise ValueError("engine must provide generation and single-source indexing")

    opted_in = synthetic_attestations is not None or synthetic_authorizations is not None
    if opted_in:
        _preflight_batch(
            manifest.entries, attestations=synthetic_attestations,
            authorizations=synthetic_authorizations, operation="multi-source-index",
            output_root=Path(index_root), manifest_digest=manifest.manifest_digest,
        )
        _preflight_source_bytes(manifest.entries, authorize_source)

    spec = engine.build_generation_spec(semantic_space)
    if opted_in:
        # Generation setup is caller controlled. Recheck the complete batch
        # after it returns so a source change during setup cannot reach the
        # first index write or leave a partially indexed generation.
        _preflight_source_bytes(manifest.entries, authorize_source)
    generation_id = getattr(spec, "generation_id", None)
    space_id = getattr(spec, "space_id", None)
    if not isinstance(generation_id, str) or not generation_id:
        raise ValueError("ENGINE_GENERATION_ID_MISSING")
    if not isinstance(space_id, str) or not space_id:
        raise ValueError("ENGINE_SPACE_ID_MISSING")

    results: list[MultiSourceEntryResult] = []
    for entry in manifest.entries:
        if opted_in:
            # Authorization and digest checks were completed for the whole batch.
            try:
                summary = engine.index_source(Path(entry.source_path), Path(index_root), spec, image_embedder)
                indexed = _summary_entry(summary)
                disposition = getattr(indexed, "disposition", None)
                if not isinstance(disposition, str) or not disposition:
                    raise ValueError("ENGINE_DISPOSITION_MISSING")
                observed_digest = getattr(indexed, "source_sha256", None)
                if observed_digest != entry.source_sha256:
                    raise ValueError("SOURCE_DIGEST_MISMATCH_AFTER_INDEX")
                source_path = getattr(indexed, "path", str(entry.source_path))
                if str(source_path) != str(entry.source_path):
                    raise ValueError("ENGINE_SOURCE_PATH_MISMATCH")
                results.append(_entry_result(entry, disposition,
                    row_start=getattr(indexed, "row_start", None),
                    row_end=getattr(indexed, "row_end", None),
                    error=getattr(indexed, "error", None)))
            except Exception as exc:  # noqa: BLE001 - preserve ordered batch result
                results.append(_entry_result(entry, "FAILED", error=f"INDEX_FAILED:{type(exc).__name__}:{exc}"))
            continue
        try:
            authorized = authorize_source(entry)
        except Exception as exc:  # noqa: BLE001 - this source must fail closed
            results.append(_entry_result(
                entry, "FAILED", error=f"AUTHORIZATION_CHECK_FAILED:{type(exc).__name__}"
            ))
            continue
        if authorized is not True:
            results.append(_entry_result(entry, "REFUSED", error="SOURCE_USE_NOT_AUTHORIZED"))
            continue

        path = entry.source_path
        if path.is_symlink() or not path.is_file():
            results.append(_entry_result(entry, "FAILED", error="SOURCE_NOT_REGULAR_FILE"))
            continue
        try:
            actual_digest = _digest_file(path)
        except OSError as exc:
            results.append(_entry_result(
                entry, "FAILED", error=f"SOURCE_UNREADABLE:{type(exc).__name__}"
            ))
            continue
        if actual_digest != entry.source_sha256:
            results.append(_entry_result(entry, "REFUSED", error="SOURCE_DIGEST_MISMATCH"))
            continue

        try:
            summary = engine.index_source(
                path, Path(index_root), spec, image_embedder
            )
            indexed = _summary_entry(summary)
            disposition = getattr(indexed, "disposition", None)
            if not isinstance(disposition, str) or not disposition:
                raise ValueError("ENGINE_DISPOSITION_MISSING")
            observed_digest = getattr(indexed, "source_sha256", None)
            if observed_digest != entry.source_sha256:
                results.append(_entry_result(
                    entry,
                    "REFUSED",
                    error="SOURCE_DIGEST_MISMATCH_AFTER_INDEX",
                ))
                continue
            row_start = getattr(indexed, "row_start", None)
            row_end = getattr(indexed, "row_end", None)
            source_path = getattr(indexed, "path", str(path))
            if str(source_path) != str(path):
                raise ValueError("ENGINE_SOURCE_PATH_MISMATCH")
            results.append(_entry_result(
                entry,
                disposition,
                row_start=row_start,
                row_end=row_end,
                error=getattr(indexed, "error", None),
            ))
        except Exception as exc:  # noqa: BLE001 - isolate independent source errors
            results.append(_entry_result(
                entry, "FAILED", error=f"INDEX_FAILED:{type(exc).__name__}:{exc}"
            ))

    return MultiSourceIndexResult(
        manifest_digest=manifest.manifest_digest,
        generation_id=generation_id,
        space_id=space_id,
        results=tuple(results),
    )


__all__ = [
    "MultiSourceEntryResult",
    "MultiSourceIndexResult",
    "SourceUseAuthorizer",
    "index_multi_source_manifest",
]
