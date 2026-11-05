"""Bounded local preparation service for an explicitly authorized source.

This module stops at the editorial hand-off.  A semantic hit is a ``MATCHED``
locator only; source-native timing is retained as a measured/refined record and
the returned bundle contains no editorial decision or edit plan.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import gate3.authority as _gate3_authority

from .ffprobe_frame_rows import (
    FfprobePayloadShapeError,
    normalized_frame_rows,
    normalized_packet_rows,
)
from .corpus_admission import (AdmissionBinding, CorpusAdmissionError,
                               SyntheticPreflightContext, require_synthetic_preflight)
from .local_semantic import CheckedLocalSemanticRuntime, retrieve_local_semantic
from persistent_local_index.model_space import semantic_space_id
from .real_source_probe import (DEFAULT_PROBE_TIMEOUT_SECONDS, RealSourceProbeBinding,
                                assert_source_unchanged, probe_real_source)
from .refinement_adapter import refine_retrieval_candidate
from .review_bundle import ReviewBundle, save_review_bundle
from .source_snapshot import SourceSnapshotStore, VerifiedSourceSnapshot


class RealSourcePreparationRefusal(RuntimeError):
    """Fail-closed refusal before a real-source bundle is published."""


@dataclass(frozen=True)
class RealSourceRequest:
    source_path: Path
    query: str
    authorization: Any
    runtime: CheckedLocalSemanticRuntime
    index_root: Path
    output_root: Path
    run_dir: Path
    source_revision_id: str
    attempt_id: str
    model_root: Path | None = None
    source_snapshot_root: Path | None = None
    max_source_bytes: int | None = None
    max_store_bytes: int | None = None
    preverified_snapshot: VerifiedSourceSnapshot | None = None
    selected_stream_index: int | None = None
    top_k: int = 1
    policy_identity: str = "real-source-local-only"
    # The measured probe boundary deliberately does not resolve PATH.  Callers
    # must provide the executable identity (and may inject a runner in tests).
    probe_executable: Path = Path("/usr/bin/ffprobe")
    # `None` is reserved for the explicit local-pilot CLI opt-in. Ordinary
    # service callers retain the finite FFprobe deadline.
    probe_timeout_seconds: float | None = DEFAULT_PROBE_TIMEOUT_SECONDS
    probe_runner: Any = None
    # Optional explicit adapter seam for deterministic generated-fixture tests.
    refinement_adapter: Any = None
    # Synthetic P1 evidence is an opt-in refusal signal at this REAL boundary;
    # it is never authority to read or prepare real media.
    synthetic_preflight: SyntheticPreflightContext | None = None
    admission_bindings: tuple[AdmissionBinding, ...] | None = None


@dataclass(frozen=True)
class RealSourcePreparationResult:
    bundle: ReviewBundle
    bundle_path: Path
    probe: RealSourceProbeBinding
    snapshot: VerifiedSourceSnapshot


def resume_multi_source_reconciliation(
    journal_path: str | Path,
    previous_manifest: Any,
    current_manifest: Any,
    *,
    index_root: Path,
    engine: Any,
    semantic_space: Any,
    image_embedder: Any,
    authorize_source: Any,
) -> Any:
    """Resume a manifest pair through the existing SQLite-authoritative writer APIs.

    The journal validates its manifest/generation/space binding before this
    function invokes the established multi-source index and exact-removal path.
    Those writers retain responsibility for reconciling uncommitted vector tails.
    """
    from .multi_source_recovery import start_or_resume
    spec = engine.build_generation_spec(semantic_space)
    journal = start_or_resume(
        journal_path, previous_manifest, current_manifest,
        generation_id=spec.generation_id, space_id=spec.space_id,
    )
    # Delegate each indexed entry through the same accepted one-entry manifest
    # operation used by C03. It performs writer-tail reconciliation itself.
    from .multi_source_index import index_multi_source_manifest
    from .source_adapter import MultiSourceManifest
    import hashlib
    import json

    def index_entry(entry: Any) -> Any:
        body = {"locator": str(entry.source_path), "revision_id": entry.revision_id, "source_sha256": entry.source_sha256}
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        one = MultiSourceManifest((entry,), digest)
        result = index_multi_source_manifest(
            one, index_root=Path(index_root), engine=engine,
            semantic_space=semantic_space, image_embedder=image_embedder,
            authorize_source=authorize_source,
        )
        if len(result.results) != 1:
            raise ValueError("ENGINE_RESULT_CARDINALITY_MISMATCH")
        return result.results[0]

    from persistent_local_index.indexer import remove_source_location
    journal.run(
        index_entry,
        lambda locator: remove_source_location(Path(index_root), spec, Path(locator)),
    )
    return journal


def _sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def _source_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _value(value: Any, name: str, default: Any = None) -> Any:
    return value.get(name, default) if isinstance(value, Mapping) else getattr(value, name, default)


def _refuse(reason: str) -> RealSourcePreparationRefusal:
    return RealSourcePreparationRefusal(reason)


def _validate_prepare_authorization(request: RealSourceRequest, source: Path) -> None:
    auth = request.authorization
    from .pilot_authorization import (
        PilotAuthorization,
        PilotAuthorizationError,
        require_prepare_authorization,
    )

    if isinstance(auth, Mapping):
        from .pilot_authorization import _FIELDS, _PREPARE_FIELDS
        if set(auth) != (_FIELDS | _PREPARE_FIELDS):
            raise _refuse("PREPARE_AUTHORIZATION_EXACT_ENVELOPE_REQUIRED")
        supplied = auth.get("record_digest")
        body = dict(auth)
        body.pop("record_digest", None)
        calculated = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        if supplied != calculated:
            raise _refuse("PREPARE_AUTHORIZATION_RECORD_DIGEST_MISMATCH")
        try:
            auth = PilotAuthorization(
                **{key: Path(auth[key]) if key in {"source_path", "model_root", "runtime_root", "index_root", "output_root"} else tuple(auth[key]) if key == "allowed_stages" else auth[key]
                   for key in (_FIELDS | _PREPARE_FIELDS) if key != "record_digest"},
                record_digest=supplied,
            )
        except (TypeError, ValueError, KeyError) as exc:
            raise _refuse("PREPARE_AUTHORIZATION_EXACT_ENVELOPE_INVALID") from exc
    if not isinstance(auth, PilotAuthorization):
        raise _refuse("PREPARE_AUTHORIZATION_EXACT_ENVELOPE_REQUIRED")
    if request.model_root is None:
        raise _refuse("PREPARE_AUTHORIZATION_MODEL_ROOT_REQUIRED")
    try:
        require_prepare_authorization(
            auth,
            source_path=source,
            source_revision_id=request.source_revision_id,
            query=request.query,
            model_root=request.model_root,
            model_identity=str(getattr(request.runtime.semantic_space, "model_identity", "unknown")),
            model_revision=str(getattr(request.runtime.semantic_space, "frozen_revision", "")),
            weights_sha256=str(getattr(request.runtime.semantic_space, "weights_sha256", "")),
            semantic_space_id=semantic_space_id(request.runtime.semantic_space),
            index_root=request.index_root,
            output_root=request.output_root,
            selected_stream_index=request.selected_stream_index,
            verify_source_digest=False,
        )
    except PilotAuthorizationError as exc:
        raise _refuse(str(exc)) from exc
    expected = {
        "source_path": str(source.resolve()),
        "source_revision_id": request.source_revision_id,
        "source_sha256": _value(auth, "source_sha256", None),
        "query_digest": _sha(request.query),
        "index_root": str(request.index_root.resolve()),
        "index_digest": _sha(str(request.index_root)),
        "output_root": str(request.output_root.resolve()),
        "local_only": True,
    }
    for key, value in expected.items():
        actual = _value(auth, key, None)
        if key in {"index_root", "source_path", "output_root"}:
            actual = str(Path(str(actual)).resolve()) if actual is not None else None
        if actual != value:
            raise _refuse(f"PREPARE_AUTHORIZATION_{key.upper()}_MISMATCH")
    source_digest = _value(auth, "source_sha256", None)
    if (not isinstance(source_digest, str) or len(source_digest) != 64
            or any(ch not in "0123456789abcdef" for ch in source_digest)):
        raise _refuse("PREPARE_AUTHORIZATION_SOURCE_DIGEST_INVALID")
    authorized_stream = _value(auth, "selected_stream_index", None)
    if authorized_stream is not None and request.selected_stream_index is not None and authorized_stream != request.selected_stream_index:
        raise _refuse("PREPARE_AUTHORIZATION_STREAM_SCOPE_MISMATCH")
    semantic_space = request.runtime.semantic_space
    canonical_space_id = semantic_space_id(semantic_space)
    runtime_values = {
        "model_identity": str(getattr(semantic_space, "model_identity", "unknown")),
        "model_revision": str(getattr(semantic_space, "frozen_revision", "")),
        "weights_sha256": str(getattr(semantic_space, "weights_sha256", "")),
        "semantic_space_id": canonical_space_id,
    }
    for key, value in runtime_values.items():
        if _value(auth, key, None) != value:
            raise _refuse(f"PREPARE_AUTHORIZATION_{key.upper()}_MISMATCH")
    stages = _value(auth, "allowed_stages", ())
    if not isinstance(stages, (tuple, list, set)) or not {"decode", "embed", "index", "probe", "retrieve", "refine"}.issubset(stages):
        raise _refuse("PREPARE_AUTHORIZATION_OPERATION_SCOPE_MISMATCH")
    expiry = _value(auth, "expires_at", None)
    if expiry is not None:
        try:
            expires = datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
            if expires.tzinfo is None or expires <= datetime.now(timezone.utc):
                raise _refuse("PREPARE_AUTHORIZATION_EXPIRED")
        except ValueError as exc:
            raise _refuse("PREPARE_AUTHORIZATION_EXPIRY_INVALID") from exc
    if _value(auth, "revoked", False) is True:
        raise _refuse("PREPARE_AUTHORIZATION_REVOKED")


def _candidate_from_hit(hit: Any, probe: RealSourceProbeBinding, attempt_id: str) -> dict[str, Any]:
    source_sha = _value(hit, "source_sha256", probe.source_sha256)
    source_path = _value(hit, "source_path", str(probe.source_path))
    if (
        type(source_sha) is not str
        or source_sha != probe.source_sha256
        or not isinstance(source_path, (str, Path))
        or Path(source_path).resolve() != probe.source_path.resolve()
    ):
        raise _refuse("RETRIEVAL_SOURCE_IDENTITY_MISMATCH")
    hit_stream_index = _value(
        hit, "stream_index", _value(hit, "selected_stream_index", None)
    )
    if hit_stream_index is not None:
        if (
            isinstance(hit_stream_index, bool)
            or not isinstance(hit_stream_index, int)
            or hit_stream_index != probe.selected_stream_index
        ):
            raise _refuse("RETRIEVAL_SOURCE_IDENTITY_MISMATCH")
    _locator_timebase(hit, probe)
    locator_num = _value(hit, "timebase_num", None)
    locator_den = _value(hit, "timebase_den", None)
    pts = _value(hit, "pts", None)
    if not isinstance(pts, int) or isinstance(pts, bool) or pts < 0:
        raise _refuse("SOURCE_PTS_NOT_OBSERVED")
    rank = _value(hit, "rank", 1)
    if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
        raise _refuse("CANDIDATE_RANK_INVALID")
    score = _value(hit, "score", 0.0)
    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(score)
    ):
        raise _refuse("CANDIDATE_SCORE_INVALID")
    # A semantic interval is deliberately coarse and never source-cut authority.
    start = (pts * locator_num) / locator_den
    coarse_window = _value(
        hit,
        "coarse_window_seconds",
        _value(hit, "sampling_interval_seconds", None),
    )
    if coarse_window is not None:
        if (
            isinstance(coarse_window, bool)
            or not isinstance(coarse_window, (int, float))
            or not math.isfinite(coarse_window)
            or coarse_window < 0
        ):
            raise _refuse("CANDIDATE_SEMANTIC_WINDOW_INVALID")
        end = start + float(coarse_window)
    else:
        end = start
    interval = {
        "start": start,
        "end": end,
        "time_domain": "semantic_seconds",
        "endpoint_semantics": "half_open",
    }
    return {
        "candidate_id": f"candidate:{attempt_id}",
        "rank": int(rank),
        "score": float(score),
        "evidence_class": "MATCHED",
        "binding_eligible": False,
        "assertion_digest": _sha({"source": source_sha, "rank": rank, "score": score, "pts": pts}),
        "semantic_interval": interval,
    }


def _observed_pts(probe: RealSourceProbeBinding) -> tuple[int, ...]:
    """Return a broad observed-timestamp inventory for diagnostics only.

    This helper deliberately unions every explicit presentation alias with packet
    ``pts`` so callers can report what the probe saw.  It is **not** endpoint
    authority: exact source-PTS endpoints come only from
    :func:`_frame_presentation_pts`, which reads measured frame presentation
    evidence of the selected stream.  A tick that appears here only because a
    packet carried it must never become an exact edit boundary.
    """
    payload = probe.ffprobe_json
    values: list[Any] = []

    def as_tick(value: Any) -> int | None:
        # ffprobe emits timestamp fields as JSON strings in some output modes;
        # accept only lossless integer forms and never coerce floats/DTS.
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return int(value.strip())
        return None

    if isinstance(payload, Mapping):
        pts_ticks = payload.get("pts_ticks")
        if isinstance(pts_ticks, (list, tuple)) and payload.get("stream_index") == probe.selected_stream_index:
            values.extend(pts_ticks)
    # The payload layout (legacy arrays or ffprobe-9 ``packets_and_frames``) is
    # resolved in one place; a malformed/ambiguous layout is a fail-closed
    # error, never an empty inventory.
    for rows, fields in (
        (normalized_frame_rows(payload), ("best_effort_timestamp", "pts", "pkt_pts")),
        (normalized_packet_rows(payload), ("pts",)),
    ):
        for item in rows:
            stream_index = item.get("stream_index")
            if stream_index is None:
                continue
            try:
                if int(stream_index) != probe.selected_stream_index:
                    continue
            except (TypeError, ValueError):
                continue
            # Frames prefer best_effort_timestamp, which is ffprobe's
            # presentation-order timestamp; packets use pts.  The other
            # explicit presentation aliases are retained for injected probe
            # contracts and older ffprobe versions.
            values.extend(item.get(field) for field in fields)
    ticks = sorted({tick for value in values if (tick := as_tick(value)) is not None})
    return tuple(ticks)


def _frame_presentation_pts(probe: RealSourceProbeBinding) -> tuple[int, ...]:
    """Return the authoritative frame-presentation ticks for the selected stream.

    Exact source-PTS endpoint authority comes only from measured frame records
    of the selected stream.  Per frame the presentation aliases are inspected in
    this order: ``best_effort_timestamp`` -> ``pts`` -> ``pkt_pts``; the first
    alias holding a valid lossless presentation tick is used and exactly one tick
    is contributed per qualifying frame.  A malformed earlier alias is skipped
    rather than masking a later valid one, and no float/DTS value is ever coerced.

    Order and duplicate multiplicity are preserved deliberately: repeated
    presentation observations are evidence and must survive the projection.
    Packets and a top-level ``pts_ticks`` key are never consulted here.
    """
    payload = probe.ffprobe_json
    try:
        frames = normalized_frame_rows(payload)
    except FfprobePayloadShapeError as exc:
        # An unreadable payload and an absent one are the same missing endpoint
        # evidence at this boundary; neither may fall through as "measured".
        raise _refuse("SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED") from exc

    def as_tick(value: Any) -> int | None:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return int(value.strip())
        return None

    ticks: list[int] = []
    for item in frames:
        stream_index = item.get("stream_index")
        if stream_index is None:
            continue
        try:
            if int(stream_index) != probe.selected_stream_index:
                continue
        except (TypeError, ValueError):
            continue
        for field in ("best_effort_timestamp", "pts", "pkt_pts"):
            tick = as_tick(item.get(field))
            if tick is not None:
                ticks.append(tick)
                break
    return tuple(ticks)


def _locator_timebase(hit: Any, probe: RealSourceProbeBinding) -> None:
    """Refuse unless the locator timebase is exact-rationally equivalent to the probe.

    A locator ``pts`` may only be interpreted as a source tick when the locator
    declares the same tick unit as the measured probe.  Comparison is exact
    integer cross-multiplication; no float, nominal FPS, or seconds conversion is
    used, and no rescaling of the locator tick is performed.
    """
    locator_num = _value(hit, "timebase_num", None)
    locator_den = _value(hit, "timebase_den", None)
    for value in (locator_num, locator_den):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise _refuse("SOURCE_LOCATOR_TIMEBASE_INVALID")
    if locator_num * probe.timebase_den != probe.timebase_num * locator_den:
        raise _refuse("SOURCE_LOCATOR_TIMEBASE_MISMATCH")


def _source_pts_interval(hit: Any, probe: RealSourceProbeBinding) -> dict[str, Any]:
    _locator_timebase(hit, probe)
    observed = _frame_presentation_pts(probe)
    if not observed:
        raise _refuse("SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED")
    pts = _value(hit, "pts", None)
    if not isinstance(pts, int) or isinstance(pts, bool) or pts not in observed:
        raise _refuse("SOURCE_PTS_NOT_OBSERVED")
    following = tuple(tick for tick in observed if tick > pts)
    if not following:
        raise _refuse("SOURCE_PTS_INTERVAL_NOT_OBSERVED")
    return {"start": pts, "end": following[0], "time_domain": "source_pts", "endpoint_semantics": "half_open"}


def _measured_timebase(authoritative: Mapping[str, Any]) -> dict[str, int]:
    """Return the validated measured timebase from the authoritative refinement.

    A missing or structurally invalid measured timebase refuses rather than
    degrading silently to the probe's declaration.  The accepted shape is exact:
    a mapping whose key set is exactly ``{"num", "den"}`` with both values exact
    positive non-boolean integers.  An extra key is refused rather than
    normalized away, because publishing a reduced num/den would satisfy the
    downstream exact-mapping comparison while the persisted record still carried
    the extension -- a publishable-but-unplannable bundle.  A future schema
    extension is therefore an explicit compatibility decision, not silent.
    """
    measured = authoritative.get("time_base")
    if not isinstance(measured, Mapping):
        raise _refuse("AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED")
    # Normalize the declaration into a plain dict FIRST and validate that copy.
    # A Mapping may lie through keys(), __iter__, items() or get(); validating one
    # view while later serializing another could publish a bundle whose timebase
    # disagrees with the persisted artifact.  The validated plain dict is what the
    # caller persists, so the two can never diverge.  A declaration that cannot be
    # normalized is refused rather than propagated as a raw exception.
    try:
        normalized = dict(measured)
    except Exception as exc:
        raise _refuse(f"AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED:{type(exc).__name__}") from exc
    if set(normalized) != {"num", "den"}:
        raise _refuse("AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED")
    num, den = normalized["num"], normalized["den"]
    for value in (num, den):
        if type(value) is not int or value <= 0:
            raise _refuse("AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED")
    return {"num": num, "den": den}


def _refinement_id_filename(value: Any) -> str:
    """Return ``value`` only when it is safe as a single artifact filename.

    ``refinement_id`` becomes a path component when the authoritative record is
    persisted, so an unvalidated value could write outside ``output_root`` before
    the bundle is ever validated.  Accepted form is one bare filename segment of
    ASCII letters, digits, dot, underscore and hyphen, which excludes separators,
    traversal, leading dots and empty names.  No sanitization is performed: an
    unsafe identifier refuses rather than being rewritten.
    """
    if type(value) is not str or not value:
        raise _refuse("AUTHORITATIVE_REFINEMENT_ID_UNSAFE")
    if len(value) > 128 or value.startswith(".") or ".." in value:
        raise _refuse("AUTHORITATIVE_REFINEMENT_ID_UNSAFE")
    if re.fullmatch(r"[A-Za-z0-9._-]+", value) is None:
        raise _refuse("AUTHORITATIVE_REFINEMENT_ID_UNSAFE")
    return value


def _canonical_refinement_bytes(record: Mapping[str, Any]) -> bytes:
    """Serialize the authoritative record before anything is written.

    Uses Gate-3's canonical JSON so the persisted bytes keep exactly the
    serialization the evidence digest is computed over.  A record carrying a
    value that cannot be serialized refuses with a named Root G code instead of
    escaping as a raw ``TypeError``/``ValueError`` from the JSON encoder.
    """
    try:
        return (_gate3_authority.canonical_json(record) + "\n").encode("utf-8")
    except Exception as exc:
        raise _refuse(f"AUTHORITATIVE_REFINEMENT_NOT_SERIALIZABLE:{type(exc).__name__}") from exc


def prepare_real_source(request: RealSourceRequest) -> RealSourcePreparationResult:
    """Probe, retrieve, and prepare one sealed editorial-review bundle."""
    if request.synthetic_preflight is not None or request.admission_bindings is not None:
        if request.synthetic_preflight is None or not request.admission_bindings:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        require_synthetic_preflight(
            request.synthetic_preflight, bindings=request.admission_bindings,
            operation="prepare-real", output_root=request.output_root,
        )
        binding = request.admission_bindings[0]
        authorization = request.authorization
        authorized_digest = (authorization.get("source_sha256") if isinstance(authorization, Mapping)
                             else getattr(authorization, "source_sha256", None))
        if (len(request.admission_bindings) != 1
                or not isinstance(binding.authorization, Mapping)
                or binding.locator != str(Path(request.source_path).expanduser().absolute())
                or binding.revision_id != request.source_revision_id
                or binding.source_sha256 != authorized_digest
                or binding.authorization.get("source_revision_id") != request.source_revision_id
                or binding.authorization.get("source_sha256") != binding.source_sha256):
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        raise CorpusAdmissionError("CORPUS_SEPARATION_REAL_ADMISSION_FORBIDDEN")
    if request.authorization is None or isinstance(request.authorization, (str, bytes, Path)):
        raise _refuse("AUTHORIZATION_REQUIRED")
    if not isinstance(request.query, str) or not request.query.strip():
        raise _refuse("QUERY_REQUIRED")
    if not isinstance(request.runtime, CheckedLocalSemanticRuntime) or request.runtime.fake:
        raise _refuse("REAL_CHECKED_RUNTIME_REQUIRED")
    source = Path(request.source_path)
    if not source.is_file():
        raise _refuse("LOCAL_SOURCE_REQUIRED")
    _validate_prepare_authorization(request, source)
    if request.top_k < 1:
        raise _refuse("INVALID_TOP_K")
    if request.source_snapshot_root is None or request.max_source_bytes is None or request.max_store_bytes is None:
        raise _refuse("SOURCE_SNAPSHOT_QUOTAS_REQUIRED")
    try:
        snapshot_store = SourceSnapshotStore(
            request.source_snapshot_root,
            max_source_bytes=request.max_source_bytes,
            max_store_bytes=request.max_store_bytes,
        )
        if request.preverified_snapshot is None:
            snapshot = snapshot_store.capture(
                source,
                expected_sha256=str(_value(request.authorization, "source_sha256", "")),
                authorization_id=str(_value(request.authorization, "authorization_id", "")),
                source_revision_id=request.source_revision_id,
            )
        else:
            snapshot = request.preverified_snapshot
            snapshot_store.verify(snapshot)
            if (snapshot.source_locator != str(source)
                    or snapshot.sha256 != str(_value(request.authorization, "source_sha256", ""))
                    or snapshot.authorization_id != str(_value(request.authorization, "authorization_id", ""))
                    or snapshot.source_revision_id != request.source_revision_id):
                raise _refuse("PREVERIFIED_SNAPSHOT_AUTHORIZATION_BINDING_MISMATCH")
    except (OSError, TypeError, ValueError) as exc:
        raise _refuse(f"SOURCE_SNAPSHOT_REFUSED:{exc}") from exc
    try:
        probe = probe_real_source(
            snapshot.snapshot_path, source_locator=str(source), snapshot_evidence=snapshot.as_evidence(),
            selected_stream_index=request.selected_stream_index,
            source_revision_id=request.source_revision_id, policy_identity=request.policy_identity,
            run_dir=request.run_dir,
            executable=request.probe_executable, runner=request.probe_runner,
            timeout_seconds=request.probe_timeout_seconds,
        )
        if (probe.source_path != snapshot.snapshot_path
                or probe.source_sha256 != snapshot.sha256
                or probe.source_byte_count != snapshot.byte_count
                or probe.source_locator != str(source)
                or dict(probe.snapshot_evidence or {}) != snapshot.as_evidence()):
            raise _refuse("SOURCE_PROBE_SNAPSHOT_BINDING_MISMATCH")
        assert_source_unchanged(probe)
        request.index_root.mkdir(parents=True, exist_ok=True)
        request.output_root.mkdir(parents=True, exist_ok=True)
        try:
            retrieved = retrieve_local_semantic(
                probe, request.query, request.index_root, runtime=request.runtime,
                top_k=request.top_k, invocation_ref=f"fvs:real:{request.attempt_id}",
            )
            retrieved_space_id = _value(retrieved, "space_id", None)
            if retrieved_space_id != semantic_space_id(request.runtime.semantic_space):
                raise _refuse("RETRIEVAL_SEMANTIC_SPACE_ID_MISMATCH")
            retrieved_generation_id = _value(retrieved, "generation_id", None)
            if not isinstance(retrieved_generation_id, str) or not retrieved_generation_id.strip():
                raise _refuse("RETRIEVAL_GENERATION_ID_INVALID")
            hits = tuple(retrieved.hits)
        except RealSourcePreparationRefusal:
            raise
        except (OSError, ValueError, RuntimeError) as exc:
            raise _refuse(f"SEMANTIC_RETRIEVAL_FAILED:{type(exc).__name__}:{exc}") from exc
        assert_source_unchanged(probe)
    except RealSourcePreparationRefusal:
        raise
    except Exception as exc:
        if isinstance(exc, AssertionError):
            raise
        raise _refuse(f"REAL_SOURCE_PREPARATION_FAILED:{type(exc).__name__}:{exc}") from exc

    if not hits:
        raise _refuse("NO_SEMANTIC_MATCH")
    candidate = _candidate_from_hit(hits[0], probe, request.attempt_id)
    # Publish only endpoints observed in the measured frame-presentation table,
    # then cross the approved Gate-3 refinement adapter.  The compact ReviewBundle
    # summary below is never itself the binding authority.
    source_pts = _source_pts_interval(hits[0], probe)
    adapter = request.refinement_adapter or refine_retrieval_candidate
    try:
        refined = adapter(
            hits[0], source_path=probe.source_path,
            source_revision_id=probe.source_revision_id,
            requested_pts=(source_pts["start"], source_pts["end"]),
            stream_index=probe.selected_stream_index,
            selected_stream_index=probe.selected_stream_index,
            attempt_id=request.attempt_id,
            stage_idempotency_key=f"real-source:{request.attempt_id}",
            tool_identity={"name": "vip_fvs.real_source_service", "version": "v3"},
            snapshot_evidence=snapshot.as_evidence(),
            probe_artifact_path=probe.canonical_probe_artifact_ref,
            probe_digest=probe.probe_digest,
        )
    except Exception as exc:
        raise _refuse(f"AUTHORITATIVE_REFINEMENT_FAILED:{type(exc).__name__}:{exc}") from exc
    authoritative = dict(getattr(refined, "measured_refinement", {}) or {})
    if not authoritative or not bool(getattr(refined, "binding_eligible", False)):
        raise _refuse("AUTHORITATIVE_REFINEMENT_NOT_BINDING_ELIGIBLE")
    # D6: never upgrade an authoritative evidence class.  The adapter's
    # `binding_eligible` flag is a caller-supplied wrapper claim and must not be
    # trusted to promote a weaker class, so the authoritative class itself is
    # required to be exactly MEASURED before any artifact or bundle is published.
    # The check is exact-type rather than `!=`: a str subclass can lie about
    # equality and would otherwise satisfy both this gate and the bundle's own
    # re-validation while carrying a weaker class string.
    authoritative_evidence_class = authoritative.get("evidence_class")
    if type(authoritative_evidence_class) is not str or authoritative_evidence_class != "MEASURED":
        raise _refuse("AUTHORITATIVE_REFINEMENT_EVIDENCE_CLASS_MISMATCH")
    # Scope/digest/interval predicates are exact-typed for the same reason: a
    # subclass overriding __eq__ would otherwise satisfy a `!=` comparison while
    # carrying a foreign value that gets persisted into the evidence artifact.
    authoritative_source_revision_id = authoritative.get("source_revision_id")
    authoritative_stream_index = authoritative.get("stream_index")
    authoritative_source_content_digest = authoritative.get("source_content_digest")
    authoritative_start_ticks = authoritative.get("start_ticks")
    authoritative_end_ticks = authoritative.get("end_ticks")
    if (type(authoritative_source_revision_id) is not str
            or authoritative_source_revision_id != probe.source_revision_id
            or type(authoritative_stream_index) is not int
            or authoritative_stream_index != probe.selected_stream_index):
        raise _refuse("AUTHORITATIVE_REFINEMENT_SOURCE_SCOPE_MISMATCH")
    if (type(authoritative_source_content_digest) is not str
            or authoritative_source_content_digest != probe.source_sha256):
        raise _refuse("AUTHORITATIVE_REFINEMENT_SOURCE_DIGEST_MISMATCH")
    if (type(authoritative_start_ticks) is not int or type(authoritative_end_ticks) is not int
            or (authoritative_start_ticks, authoritative_end_ticks) != (source_pts["start"], source_pts["end"])):
        raise _refuse("AUTHORITATIVE_REFINEMENT_INTERVAL_MISMATCH")
    # D-PROV-1.C: the authoritative measured timebase must be present, valid and
    # exactly equal to the probe timebase before anything is published.  A
    # mismatch means two measurements of the same bytes disagree about the tick
    # unit, so publishing either one would be a silent equivalence.  The measured
    # value is the published authority; the probe declaration is not re-asserted.
    measured_tb = _measured_timebase(authoritative)
    if (measured_tb["num"], measured_tb["den"]) != (probe.timebase_num, probe.timebase_den):
        raise _refuse("AUTHORITATIVE_REFINEMENT_TIMEBASE_MISMATCH")
    tb = {"num": measured_tb["num"], "den": measured_tb["den"]}
    # Complete every read, normalization and serialization this publication needs
    # BEFORE the first byte is written.  A field only dereferenced after the write
    # would leave a partial artifact on disk and escape as a raw KeyError, and a
    # value only rejected by ReviewBundle would leave a partial artifact and
    # escape as a raw ValueError.
    refinement_id = _refinement_id_filename(authoritative.get("refinement_id"))
    evidence_digest = authoritative.get("evidence_digest")
    if type(evidence_digest) is not str or not evidence_digest:
        raise _refuse("AUTHORITATIVE_REFINEMENT_EVIDENCE_DIGEST_MISSING")
    refinement_record = dict(authoritative)
    # Persist the validated plain timebase so the artifact can never carry a
    # declaration that differs from the validated/bundled one.
    refinement_record["time_base"] = dict(tb)
    refinement_record["source_probe_artifact_ref"] = probe.canonical_probe_artifact_ref
    refinement_record["source_probe_digest"] = probe.probe_digest
    # Final evidence rebinding.  `time_base` is evidence-bearing and was just
    # normalized, so the record that will actually be persisted must still satisfy
    # Gate-3's own evidence projection.  The producer's digest is verified, never
    # recomputed or replaced: a mismatch is a refusal.  This runs after all
    # evidence-bearing normalization and before any serialization or write, so a
    # record whose persisted projection disagrees with its declared digest can
    # never produce a publishable-but-unplannable artifact.  The source-probe
    # fields above are not part of the projection and do not affect this check.
    # The verifier canonicalizes the projection, so an unserializable projected
    # value must surface as this module's named refusal rather than escaping as a
    # raw encoder error.
    try:
        digest_check = _gate3_authority.assert_evidence_digest(
            _gate3_authority.RECORD_KIND_REFINEMENT, refinement_record,
        )
    except Exception as exc:
        raise _refuse(f"AUTHORITATIVE_REFINEMENT_NOT_SERIALIZABLE:{type(exc).__name__}") from exc
    if not isinstance(digest_check, str) or digest_check != evidence_digest:
        raise _refuse("AUTHORITATIVE_REFINEMENT_EVIDENCE_DIGEST_MISMATCH")
    refinement_bytes = _canonical_refinement_bytes(refinement_record)
    compact_refinement = {
        "refinement_id": refinement_id, "status": "MEASURED",
        "source_revision_id": probe.source_revision_id, "selected_stream_index": probe.selected_stream_index,
        "source_pts_interval": source_pts, "timebase": tb, "attempt_id": request.attempt_id,
        "evidence_class": authoritative_evidence_class,
    }
    # Re-check the owner-scoped authorization immediately before publication;
    # source/query/runtime/index scope must still be current after retrieval and
    # refinement work has completed.
    _validate_prepare_authorization(request, source)
    refinement_path = request.output_root / "refinement" / f"{refinement_id}.json"
    artifact_ref_length = len(str(refinement_path))
    if artifact_ref_length == 0 or artifact_ref_length > 256:
        raise _refuse("AUTHORITATIVE_REFINEMENT_ARTIFACT_REF_TOO_LONG")
    refinement_path.parent.mkdir(parents=True, exist_ok=True)
    if refinement_path.exists() and refinement_path.read_bytes() != refinement_bytes:
        raise _refuse("AUTHORITATIVE_REFINEMENT_ARTIFACT_CONFLICT")
    refinement_path.write_bytes(refinement_bytes)
    refinement = {
        **compact_refinement,
        "evidence_artifact_ref": str(refinement_path),
        "evidence_digest": evidence_digest,
    }
    semantic_space = request.runtime.semantic_space
    model_identity = str(getattr(semantic_space, "model_identity", "unknown"))
    retrieved_space_id = str(_value(retrieved, "space_id", ""))
    retrieved_generation_id = str(_value(retrieved, "generation_id", ""))
    payload = {
        "bundle_id": f"bundle:{request.attempt_id}", "run_id": request.attempt_id,
        "created_at": "1970-01-01T00:00:00Z", "review_status": "AWAITING_EDITORIAL_DECISION",
        "source": {"source_revision_id": probe.source_revision_id, "source_sha256": probe.source_sha256,
                   "source_byte_count": probe.source_byte_count, "selected_stream_index": probe.selected_stream_index,
                   "timebase": tb, "probe_artifact_ref": probe.probe_artifact_ref, "probe_digest": probe.probe_digest,
                   "source_locator": snapshot.source_locator, "snapshot": snapshot.as_evidence()},
        "authorization": {"discovery_policy_ref": str(_value(request.authorization, "discovery_policy_ref", request.policy_identity)),
                           "refinement_policy_ref": str(_value(request.authorization, "refinement_policy_ref", request.policy_identity)),
                           "policy_digest": str(_value(request.authorization, "policy_digest", _sha({"policy": request.policy_identity}))),
                           "scope_digest": str(_value(request.authorization, "scope_digest", _sha({"source": probe.source_sha256})))},
        "query": {"query_id": f"query:{request.attempt_id}", "text": request.query, "digest": _sha(request.query)},
        "generation": {"attempt_id": request.attempt_id, "generation_id": retrieved_generation_id,
                        "semantic_space_id": retrieved_space_id,
                        "model_identity": model_identity, "model_revision": str(getattr(semantic_space, "frozen_revision", retrieved_generation_id)),
                        "weights_digest": str(getattr(semantic_space, "weights_sha256", "0" * 64)),
                        "processor_digest": str(getattr(semantic_space, "processor_digest", "0" * 64)),
                        "index_ref": str(request.index_root), "index_digest": _sha(str(request.index_root)),
                        "input_digest": probe.source_sha256},
        "candidate": candidate, "refinement": refinement,
        "presentation": {"display_only": True, "start_seconds": 0.0, "end_seconds": 1.0},
        "dependency_digest": "0" * 64, "decision": None,
    }
    bundle = ReviewBundle.create(payload, run_id=request.attempt_id, bundle_id=payload["bundle_id"], created_at=payload["created_at"])
    path = save_review_bundle(bundle, request.output_root / "review-bundle.json")
    return RealSourcePreparationResult(bundle=bundle, bundle_path=path, probe=probe, snapshot=snapshot)


__all__ = ["RealSourcePreparationRefusal", "RealSourceRequest", "RealSourcePreparationResult", "prepare_real_source"]
