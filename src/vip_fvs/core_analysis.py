"""Single-video query-driven semantic analysis orchestration for QUERY_DRIVEN_SEMANTIC_REPORT_V1."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import inspect
import json
import math
from pathlib import Path
import sqlite3
from typing import Any, Callable

from .core_report import (
    ANALYSIS_KIND_SEMANTIC_RETRIEVAL,
    CORE_REPORT_KIND,
    CORE_REPORT_SCHEMA_VERSION,
    NOT_OBSERVED,
    CoreReportError,
    CoreReportPublicationError,
    build_core_semantic_report,
    build_point_semantic_location,
    format_rational_seconds,
    publish_core_semantic_report,
    validate_output_target_path,
)
from .corpus_admission import (
    AdmissionBinding,
    CorpusAdmissionError,
    check_synthetic_preflight,
)
from .pilot_authorization import (
    PilotAuthorization,
    PilotAuthorizationError,
    load_pilot_authorization,
)
from .query_modality import QueryEnvelope
from .real_source_probe import (
    DEFAULT_PROBE_TIMEOUT_SECONDS,
    MeasuredProbeRefusal,
    ProbeFailure,
    RealSourceProbeBinding,
    probe_real_source,
)
from .source_snapshot import (
    SourceSnapshotError,
    SourceSnapshotStore,
    VerifiedSourceSnapshot,
)


class CoreAnalysisRefusal(RuntimeError):
    """Fail-closed refusal raised during single-video semantic analysis."""

    def __init__(
        self,
        code: str,
        detail: str | None = None,
        *,
        stage_status: str = "FAILED",
        result_kind: str = "REFUSED",
    ) -> None:
        self.code = str(code)
        self.detail = detail or str(code)
        self.stage_status = stage_status
        self.result_kind = result_kind
        super().__init__(f"{self.code}: {self.detail}" if detail else self.code)


@dataclass(frozen=True)
class CoreAnalysisRequest:
    """Input contract for vip-fvs analyze-local."""

    source_path: str | Path
    query: str
    index_root: str | Path
    output_root: str | Path
    report_path: str | Path | None = None
    attempt_id: str | None = None
    source_revision_id: str | None = None
    top_k: int = 5
    fake_embedder: bool = False
    pilot_authorization_path: str | Path | None = None
    model_root: str | Path | None = None
    model_identity: str | None = None
    model_revision: str | None = None
    weights_sha256: str | None = None
    device: str = "cpu"
    model_profile_json: str | Path | None = None
    source_snapshot_root: str | Path | None = None
    max_source_bytes: int | None = None
    max_store_bytes: int | None = None
    preverified_snapshot_id: str | None = None
    selected_stream_index: int | None = None
    probe_executable: str = "/usr/bin/ffprobe"
    refinement_artifact_path: str | Path | None = None
    synthetic_attestation_paths: Sequence[str | Path] | None = None
    synthetic_binding_paths: Sequence[str | Path] | None = None
    runtime: Any | None = None
    engine: Any | None = None
    probe_fn: Callable[..., RealSourceProbeBinding] | None = None
    snapshot_store_factory: Callable[..., SourceSnapshotStore] | None = None


@dataclass(frozen=True)
class CoreAnalysisOutcome:
    """Validated result of a single-video semantic analysis invocation."""

    report: dict[str, Any]
    report_path: Path
    summary: dict[str, Any]


def _is_non_bool_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _resolve_space_attr(space: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if hasattr(space, name):
            val = getattr(space, name)
            if val is not None:
                return val
    return default


def _compute_space_id(space: Any) -> str:
    explicit = _resolve_space_attr(space, "space_id", "semantic_space_id")
    if isinstance(explicit, str) and len(explicit) == 64:
        return explicit
    try:
        from persistent_local_index.model_space import semantic_space_id

        return semantic_space_id(space)
    except Exception:
        payload = asdict(space) if hasattr(space, "__dataclass_fields__") else dict(vars(space))
        return _canonical_sha256(payload)


def _derive_model_family(space: Any) -> str:
    explicit = _resolve_space_attr(space, "model_family", "family")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    model_id = str(_resolve_space_attr(space, "model_identity", "model_id", default="")).lower()
    if "siglip2" in model_id:
        return "siglip2"
    if "siglip" in model_id:
        return "siglip"
    if "fake" in model_id or "synthetic" in model_id:
        return "synthetic_fake"
    return model_id or "unknown"


def _hash_regular_file(path: Path) -> tuple[str, int]:
    if path.is_symlink():
        raise CoreAnalysisRefusal(
            "SOURCE_SYMLINK_FORBIDDEN", f"Source path must not be a symlink: {path}"
        )
    try:
        st = path.lstat()
    except OSError as exc:
        raise CoreAnalysisRefusal(
            "SOURCE_NOT_FOUND", f"Source file does not exist: {path}"
        ) from exc
    if not path.is_file():
        raise CoreAnalysisRefusal(
            "SOURCE_NOT_A_REGULAR_FILE", f"Source path is not a regular file: {path}"
        )
    if st.st_size <= 0:
        raise CoreAnalysisRefusal(
            "SOURCE_EMPTY_FILE", f"Source file is empty: {path}"
        )
    digest = hashlib.sha256()
    total = 0
    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                total += len(chunk)
    except OSError as exc:
        raise CoreAnalysisRefusal(
            "SOURCE_READ_FAILED", f"Failed to read source file: {path}"
        ) from exc
    if total <= 0:
        raise CoreAnalysisRefusal(
            "SOURCE_EMPTY_FILE", f"Source file read 0 bytes: {path}"
        )
    return digest.hexdigest(), total


def _validate_synthetic_preflight_args(
    request: CoreAnalysisRequest,
    *,
    resolved_output_root: Path,
) -> None:
    att_paths = list(request.synthetic_attestation_paths or ())
    bind_paths = list(request.synthetic_binding_paths or ())
    if not att_paths and not bind_paths:
        return
    if not request.fake_embedder:
        raise CoreAnalysisRefusal(
            "CORPUS_SEPARATION_REAL_ADMISSION_FORBIDDEN",
            "Synthetic admission attestations/bindings are forbidden in real-mode analyze-local",
        )
    if not att_paths or not bind_paths or len(att_paths) != len(bind_paths):
        raise CoreAnalysisRefusal(
            "CORPUS_SEPARATION_DECLARATION_INVALID",
            "Synthetic attestation and binding counts must match",
        )
    try:
        attestations = tuple(
            json.loads(Path(p).read_text(encoding="utf-8")) for p in att_paths
        )
        bindings = tuple(
            AdmissionBinding(**json.loads(Path(p).read_text(encoding="utf-8")))
            for p in bind_paths
        )
        check_synthetic_preflight(
            attestations,
            bindings=bindings,
            operation="analyze-local",
            output_root=resolved_output_root,
        )
    except (OSError, TypeError, ValueError, CorpusAdmissionError) as exc:
        code = str(exc) if isinstance(exc, CorpusAdmissionError) else "CORPUS_SEPARATION_DECLARATION_INVALID"
        raise CoreAnalysisRefusal(code, f"Synthetic preflight invalid: {exc}") from exc


def _validate_and_load_real_authorization(
    request: CoreAnalysisRequest,
    *,
    raw_query_text: str,
    normalized_query_text: str,
    query_digest: str,
    resolved_output_root: Path,
) -> tuple[PilotAuthorization, dict[str, Any], str, int | None]:
    """Validate owner pilot authorization before any source, model, or index access."""
    if not request.pilot_authorization_path:
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_REQUIRED_BEFORE_REAL_SOURCE_ACCESS",
            "Real-mode analyze-local requires --pilot-authorization before source access",
        )
    auth_path = Path(request.pilot_authorization_path).expanduser()
    if auth_path.is_symlink() or not auth_path.is_file():
        raise CoreAnalysisRefusal(
            "REAL_MEDIA_AUTHORIZATION_REQUIRED",
            f"Pilot authorization file is missing or invalid: {auth_path}",
        )
    try:
        raw_payload = json.loads(auth_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CoreAnalysisRefusal(
            "PILOT_AUTHORIZATION_UNREADABLE",
            f"Pilot authorization is not valid JSON: {auth_path}",
        ) from exc
    if not isinstance(raw_payload, dict):
        raise CoreAnalysisRefusal(
            "PILOT_AUTHORIZATION_SCHEMA_INVALID",
            "Pilot authorization JSON must be an object",
        )

    # Check revocation, local_only, and expiry on raw_payload before load_pilot_authorization
    # touches source_path.is_file() so revoked/expired authorizations fail closed first.
    if type(raw_payload.get("revoked", False)) is not bool:
        raise CoreAnalysisRefusal(
            "PILOT_AUTHORIZATION_REVOCATION_FLAG_INVALID",
            "revoked must be a boolean",
        )
    if raw_payload.get("revoked") is True:
        raise CoreAnalysisRefusal(
            "PILOT_AUTHORIZATION_REVOKED",
            "Pilot authorization is revoked",
        )
    if "local_only" in raw_payload and raw_payload.get("local_only") is not True:
        raise CoreAnalysisRefusal(
            "PILOT_AUTHORIZATION_LOCAL_ONLY_REQUIRED",
            "Pilot authorization must have local_only=True",
        )
    raw_expiry = raw_payload.get("expires_at")
    if raw_expiry is not None:
        if not isinstance(raw_expiry, str) or not raw_expiry.strip():
            raise CoreAnalysisRefusal(
                "PILOT_AUTHORIZATION_EXPIRY_INVALID",
                "expires_at must be a timezone-aware RFC3339 timestamp",
            )
        try:
            expiry_dt = datetime.fromisoformat(raw_expiry.replace("Z", "+00:00"))
        except ValueError as exc:
            raise CoreAnalysisRefusal(
                "PILOT_AUTHORIZATION_EXPIRY_INVALID",
                f"Invalid expires_at: {raw_expiry}",
            ) from exc
        if expiry_dt.tzinfo is None or expiry_dt.utcoffset() is None:
            raise CoreAnalysisRefusal(
                "PILOT_AUTHORIZATION_EXPIRY_INVALID",
                "expires_at must include timezone offset",
            )
        if expiry_dt <= datetime.now(timezone.utc):
            raise CoreAnalysisRefusal(
                "PILOT_AUTHORIZATION_EXPIRED",
                "Pilot authorization has expired",
            )

    try:
        record = load_pilot_authorization(auth_path)
    except PilotAuthorizationError as exc:
        raise CoreAnalysisRefusal(str(exc), f"Pilot authorization invalid: {exc}") from exc

    if record.revoked:
        raise CoreAnalysisRefusal(
            "PILOT_AUTHORIZATION_REVOKED", "Pilot authorization is revoked"
        )
    if record.local_only is False:
        raise CoreAnalysisRefusal(
            "PILOT_AUTHORIZATION_LOCAL_ONLY_REQUIRED",
            "Pilot authorization requires local_only=True",
        )

    stages = set(record.allowed_stages)
    has_query_stage = "query" in stages or "retrieve" in stages
    has_index_stage = {"decode", "embed", "index"}.issubset(stages)
    if not (has_query_stage and has_index_stage):
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_STAGE_NOT_ALLOWED",
            "Pilot authorization must allow decode, embed, index, and query/retrieve stages",
        )

    raw_source = str(request.source_path).strip() if request.source_path is not None else ""
    if not raw_source:
        raise CoreAnalysisRefusal("SOURCE_PATH_REQUIRED", "--source is required")
    req_source_resolved = Path(raw_source).expanduser().resolve(strict=False)
    auth_source_resolved = record.source_path.resolve(strict=False)
    if req_source_resolved != auth_source_resolved:
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_SOURCE_PATH_MISMATCH",
            "Requested --source does not match authorized source_path",
        )

    if (
        not request.model_root
        or not request.model_identity
        or not request.model_revision
        or not request.weights_sha256
    ):
        raise CoreAnalysisRefusal(
            "REAL_MODE_REQUIRES_EXPLICIT_MODEL_PROVENANCE",
            "Real mode requires --model-root, --model-identity, --model-revision, and --weights-sha256",
        )

    if (
        Path(request.model_root).expanduser().resolve(strict=False)
        != record.model_root.resolve(strict=False)
    ):
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_MODEL_ROOT_MISMATCH",
            "Requested --model-root does not match authorized model_root",
        )
    if (
        record.model_identity is not None
        and str(request.model_identity) != record.model_identity
    ):
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_MODEL_IDENTITY_MISMATCH",
            "Requested --model-identity does not match authorized model_identity",
        )
    if str(request.model_revision) != record.model_revision:
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_MODEL_REVISION_MISMATCH",
            "Requested --model-revision does not match authorized model_revision",
        )
    if str(request.weights_sha256) != record.weights_sha256:
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_WEIGHTS_MISMATCH",
            "Requested --weights-sha256 does not match authorized weights_sha256",
        )
    if (
        Path(request.index_root).expanduser().resolve(strict=False)
        != record.index_root.resolve(strict=False)
    ):
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_INDEX_ROOT_MISMATCH",
            "Requested --index-root does not match authorized index_root",
        )

    auth_output_root = record.output_root.resolve(strict=False)
    if resolved_output_root != auth_output_root:
        try:
            resolved_output_root.relative_to(auth_output_root)
        except ValueError as exc:
            raise CoreAnalysisRefusal(
                "AUTHORIZATION_OUTPUT_ROOT_MISMATCH",
                "Requested --output-root is outside authorized output_root",
            ) from exc

    auth_revision = record.source_revision_id
    req_revision = (
        str(request.source_revision_id).strip()
        if request.source_revision_id is not None
        else ""
    )
    if auth_revision is not None:
        if req_revision and req_revision != auth_revision:
            raise CoreAnalysisRefusal(
                "AUTHORIZATION_SOURCE_REVISION_MISMATCH",
                "Requested --source-revision-id does not match authorized source_revision_id",
            )
        resolved_revision = auth_revision
    elif req_revision:
        resolved_revision = req_revision
    else:
        raise CoreAnalysisRefusal(
            "SOURCE_REVISION_ID_REQUIRED",
            "source_revision_id must be supplied via --source-revision-id or pilot authorization",
        )

    effective_stream_index = request.selected_stream_index
    if record.selected_stream_index is not None:
        if (
            effective_stream_index is not None
            and effective_stream_index != record.selected_stream_index
        ):
            raise CoreAnalysisRefusal(
                "AUTHORIZATION_STREAM_INDEX_MISMATCH",
                "Requested --selected-stream-index does not match authorized selected_stream_index",
            )
        effective_stream_index = int(record.selected_stream_index)

    if record.query_digest is not None:
        json_raw_digest = _canonical_sha256(raw_query_text)
        json_norm_digest = _canonical_sha256(normalized_query_text)
        if record.query_digest not in {query_digest, json_raw_digest, json_norm_digest}:
            raise CoreAnalysisRefusal(
                "AUTHORIZATION_QUERY_DIGEST_MISMATCH",
                "Query digest does not match authorized query_digest",
            )

    return record, raw_payload, resolved_revision, effective_stream_index


def _build_default_runtime(request: CoreAnalysisRequest) -> Any:
    if request.fake_embedder:
        if request.model_profile_json is not None:
            from persistent_local_index.embedding import build_fake_profile_runtime
            from persistent_local_index.model_profile import ModelProfile

            profile_path = Path(request.model_profile_json).expanduser()
            try:
                payload = json.loads(profile_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise CoreAnalysisRefusal(
                    "MODEL_PROFILE_JSON_UNREADABLE",
                    f"Unable to read model profile JSON: {profile_path}",
                ) from exc
            if not isinstance(payload, dict):
                raise CoreAnalysisRefusal(
                    "MODEL_PROFILE_JSON_NOT_OBJECT",
                    "Model profile JSON must be an object",
                )
            assets = payload.get("processor_asset_digests")
            if not isinstance(assets, list):
                raise CoreAnalysisRefusal(
                    "MODEL_PROFILE_ASSETS_INVALID",
                    "processor_asset_digests must be a list",
                )
            try:
                profile = ModelProfile(
                    **{
                        **payload,
                        "processor_asset_digests": tuple(
                            tuple(item) for item in assets
                        ),
                    }
                )
                return build_fake_profile_runtime(profile)
            except (TypeError, ValueError) as exc:
                raise CoreAnalysisRefusal(
                    "MODEL_PROFILE_JSON_INVALID", f"Invalid model profile: {exc}"
                ) from exc
        from .local_semantic import fake_runtime

        return fake_runtime()

    from persistent_local_index.embedding import embed_images, embed_texts, load_session
    from persistent_local_index.local_model import LocalModelSpec, open_local_model
    from persistent_local_index.model_space import (
        EMBEDDING_DIM,
        EMBEDDING_DTYPE,
        TEXT_PREPROCESSING_CONTRACT,
        SemanticSpace,
        digest_image_preprocessing_assets,
        digest_processor_assets,
    )
    from .local_semantic import checked_runtime

    try:
        root = Path(request.model_root).expanduser().resolve()
        processor_digest = digest_processor_assets(root)
        spec = LocalModelSpec(
            root,
            str(request.weights_sha256),
            processor_digest,
            str(request.model_revision),
            device=request.device,
        )
        handle = open_local_model(
            spec,
            loader=lambda checked_root, checked_device: load_session(
                checked_root, str(request.weights_sha256), device=checked_device
            ),
        )
        space = SemanticSpace(
            str(request.model_identity),
            str(request.model_revision),
            str(request.weights_sha256),
            processor_digest,
            digest_image_preprocessing_assets(root),
            TEXT_PREPROCESSING_CONTRACT,
            EMBEDDING_DIM,
            EMBEDDING_DTYPE,
            "l2",
        )
        return checked_runtime(
            image_embedder=lambda paths: embed_images(handle.runtime, paths),
            text_embedder=lambda texts: embed_texts(handle.runtime, texts),
            semantic_space=space,
            runtime_identity=str(request.model_identity),
        )
    except Exception as exc:
        raise CoreAnalysisRefusal(
            "REAL_RUNTIME_INIT_FAILED", f"Failed to initialize local model runtime: {exc}"
        ) from exc


def _build_default_engine() -> Any:
    from .semantic_index import PersistentLocalSemanticIndexEngine

    return PersistentLocalSemanticIndexEngine()


def _invoke_engine_index_source(
    engine: Any,
    *,
    source_path: Path,
    index_root: Path,
    spec: Any,
    runtime: Any,
) -> dict[str, int]:
    """Call engine.index_source using either the 4-arg SemanticIndexEngine protocol or keyword form."""
    image_embedder = getattr(runtime, "image_embedder", None)
    method = engine.index_source
    positional = (source_path, index_root, spec, image_embedder)
    keyword = {"source_path": source_path, "index_root": index_root, "runtime": runtime}
    try:
        signature = inspect.signature(method)
    except (TypeError, ValueError):
        signature = None
    if signature is not None and not _signature_accepts(signature, positional, {}):
        if _signature_accepts(signature, (), keyword):
            raw_summary = method(**keyword)
        else:
            raw_summary = method(*positional)
    else:
        raw_summary = method(*positional)
    values = (
        {key: raw_summary.get(key) for key in ("indexed", "skipped", "reused", "failed")}
        if isinstance(raw_summary, Mapping)
        else {key: getattr(raw_summary, key, None) for key in ("indexed", "skipped", "reused", "failed")}
    )
    if any(not _is_non_bool_int(value) or value < 0 for value in values.values()):
        raise CoreAnalysisRefusal("INDEX_SUMMARY_INVALID", "Index engine returned missing or invalid disposition counts")
    if not any(values[key] > 0 for key in ("indexed", "skipped", "reused", "failed")):
        raise CoreAnalysisRefusal("INDEX_SUMMARY_INVALID", "Index engine returned no source disposition")
    return values  # type: ignore[return-value]


def _signature_accepts(signature: inspect.Signature, args: tuple[Any, ...], kwargs: dict[str, Any]) -> bool:
    try:
        signature.bind(*args, **kwargs)
    except TypeError:
        return False
    return True


def _invoke_engine_query(
    engine: Any,
    *,
    index_root: Path,
    spec: Any,
    query_text: str,
    runtime: Any,
    top_k: int,
) -> list[Any]:
    """Call engine.query using either the SemanticIndexEngine protocol or keyword form."""
    text_embedder = getattr(runtime, "text_embedder", None)
    method = engine.query
    positional = (index_root, spec, [query_text], text_embedder)
    positional_kwargs = {"top_k": top_k}
    keyword = {"index_root": index_root, "generation_id": str(spec.generation_id), "runtime": runtime, "query_text": query_text, "top_k": top_k}
    try:
        signature = inspect.signature(method)
    except (TypeError, ValueError):
        signature = None
    if signature is not None and not _signature_accepts(signature, positional, positional_kwargs):
        if _signature_accepts(signature, (), keyword):
            raw_result = method(**keyword)
        else:
            raw_result = method(*positional, **positional_kwargs)
    else:
        raw_result = method(*positional, **positional_kwargs)
    if isinstance(raw_result, Mapping):
        hits = raw_result.get(query_text)
        if hits is None and len(raw_result) == 1:
            hits = next(iter(raw_result.values()))
        return list(hits or ())
    return list(raw_result or ())


def _inspect_generation_pre_index(
    db_path: Path,
    *,
    expected_space_id: str,
    expected_source_sha256: str,
    expected_source_revision_id: str,
    expected_stream_index: int,
    expected_timebase: tuple[int, int],
    expected_byte_count: int,
    allowed_paths: set[str],
) -> bool:
    """Verify existing generation DB has no foreign sources or mismatched occurrence metadata."""
    if not db_path.exists():
        return False

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        raise CoreAnalysisRefusal(
            "INDEX_SQLITE_OPEN_FAILED", f"Failed to inspect index SQLite: {exc}"
        ) from exc

    try:
        gen_row = conn.execute(
            "SELECT space_id FROM generation_state LIMIT 1"
        ).fetchone()
        if gen_row is not None and str(gen_row["space_id"]) != expected_space_id:
            raise CoreAnalysisRefusal(
                "INDEX_SEMANTIC_SPACE_MISMATCH",
                f"Existing generation space_id {gen_row['space_id']} != {expected_space_id}",
            )

        foreign_obj = conn.execute(
            "SELECT source_sha256 FROM source_objects WHERE source_sha256 != ? LIMIT 1",
            (expected_source_sha256,),
        ).fetchone()
        if foreign_obj is not None:
            raise CoreAnalysisRefusal(
                "MULTI_SOURCE_INDEX_UNSUPPORTED",
                "Existing index generation contains another source_sha256; single-video scope refuses multi-source generations",
            )

        foreign_sample = conn.execute(
            "SELECT source_sha256 FROM samples WHERE source_sha256 != ? LIMIT 1",
            (expected_source_sha256,),
        ).fetchone()
        if foreign_sample is not None:
            raise CoreAnalysisRefusal(
                "MULTI_SOURCE_INDEX_UNSUPPORTED",
                "Existing index samples contain another source_sha256",
            )

        foreign_loc = conn.execute(
            "SELECT path, source_sha256 FROM source_locations WHERE source_sha256 != ? LIMIT 1",
            (expected_source_sha256,),
        ).fetchone()
        if foreign_loc is not None:
            raise CoreAnalysisRefusal(
                "MULTI_SOURCE_INDEX_UNSUPPORTED",
                "Existing index locations contain another source_sha256",
            )

        loc_rows = conn.execute(
            "SELECT path FROM source_locations WHERE source_sha256 = ?",
            (expected_source_sha256,),
        ).fetchall()
        for loc_row in loc_rows:
            loc_path = str(loc_row["path"])
            resolved_loc = str(Path(loc_path).expanduser().resolve(strict=False))
            if loc_path not in allowed_paths and resolved_loc not in allowed_paths:
                raise CoreAnalysisRefusal(
                    "SOURCE_OCCURRENCE_MISMATCH",
                    f"Same SHA-256 was indexed from a different source occurrence path: {loc_path}",
                )

        obj_row = conn.execute(
            "SELECT * FROM source_objects WHERE source_sha256 = ?",
            (expected_source_sha256,),
        ).fetchone()
        if obj_row is None:
            return False

        if str(obj_row["state"]) != "COMPLETE" or int(obj_row["active"]) != 1:
            raise CoreAnalysisRefusal(
                "INDEX_SOURCE_STATE_INVALID",
                f"Existing index source state is not active COMPLETE: {obj_row['state']}",
            )
        if int(obj_row["stream_index"]) != expected_stream_index:
            raise CoreAnalysisRefusal(
                "INDEX_STREAM_IDENTITY_MISMATCH",
                f"Existing indexed stream_index {obj_row['stream_index']} != probed stream_index {expected_stream_index}",
            )
        if (
            int(obj_row["timebase_num"]) != expected_timebase[0]
            or int(obj_row["timebase_den"]) != expected_timebase[1]
        ):
            raise CoreAnalysisRefusal(
                "INDEX_TIMEBASE_MISMATCH",
                "Existing indexed timebase does not match probed timebase",
            )
        if int(obj_row["size_bytes"]) != expected_byte_count:
            raise CoreAnalysisRefusal(
                "INDEX_SOURCE_SIZE_MISMATCH",
                "Existing indexed size_bytes does not match probed source_byte_count",
            )

        existing_rev = obj_row["source_revision"]
        if existing_rev is None or not str(existing_rev).strip():
            raise CoreAnalysisRefusal(
                "SOURCE_REVISION_UNBOUND_IN_EXISTING_INDEX",
                "Existing index entry has no bound source_revision; refusing silent source identity promotion",
            )
        if str(existing_rev) != expected_source_revision_id:
            raise CoreAnalysisRefusal(
                "SOURCE_REVISION_MISMATCH",
                f"Existing index source_revision {existing_rev!r} != {expected_source_revision_id!r}",
            )
        return True
    finally:
        conn.close()


def _verify_and_bind_generation_post_index(
    db_path: Path,
    *,
    expected_space_id: str,
    expected_source_sha256: str,
    expected_source_revision_id: str,
    expected_stream_index: int,
    expected_timebase: tuple[int, int],
    expected_byte_count: int,
    allowed_paths: set[str],
) -> tuple[dict[int, dict[str, Any]], int, int]:
    """Verify post-index SQLite state, bind source_revision, and return verified sample metadata."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        raise CoreAnalysisRefusal(
            "INDEX_SQLITE_OPEN_FAILED", f"Failed to open post-index SQLite: {exc}"
        ) from exc

    try:
        gen_row = conn.execute(
            "SELECT space_id, committed_row_count FROM generation_state LIMIT 1"
        ).fetchone()
        if gen_row is None:
            raise CoreAnalysisRefusal(
                "INDEX_GENERATION_STATE_MISSING",
                "generation_state row is missing after indexing",
            )
        if str(gen_row["space_id"]) != expected_space_id:
            raise CoreAnalysisRefusal(
                "INDEX_SEMANTIC_SPACE_MISMATCH",
                "Post-index generation space_id mismatches runtime semantic_space_id",
            )
        committed_row_count = int(gen_row["committed_row_count"])

        obj_rows = conn.execute("SELECT * FROM source_objects").fetchall()
        if len(obj_rows) != 1:
            raise CoreAnalysisRefusal(
                "MULTI_SOURCE_INDEX_UNSUPPORTED",
                f"Expected exactly 1 source_object in generation, found {len(obj_rows)}",
            )
        obj_row = obj_rows[0]
        if str(obj_row["source_sha256"]) != expected_source_sha256:
            raise CoreAnalysisRefusal(
                "MULTI_SOURCE_INDEX_UNSUPPORTED",
                "Indexed source_object SHA-256 does not match probed source_sha256",
            )
        if str(obj_row["state"]) != "COMPLETE" or int(obj_row["active"]) != 1:
            raise CoreAnalysisRefusal(
                "INDEX_SOURCE_STATE_INVALID",
                "Indexed source_object is not in active COMPLETE state",
            )
        if int(obj_row["stream_index"]) != expected_stream_index:
            raise CoreAnalysisRefusal(
                "INDEX_STREAM_IDENTITY_MISMATCH",
                f"Indexed stream_index {obj_row['stream_index']} != probed selected_stream_index {expected_stream_index}",
            )
        if (
            int(obj_row["timebase_num"]) != expected_timebase[0]
            or int(obj_row["timebase_den"]) != expected_timebase[1]
        ):
            raise CoreAnalysisRefusal(
                "INDEX_TIMEBASE_MISMATCH",
                "Indexed source_object timebase does not match probed timebase",
            )
        if int(obj_row["size_bytes"]) != expected_byte_count:
            raise CoreAnalysisRefusal(
                "INDEX_SOURCE_SIZE_MISMATCH",
                "Indexed source_object size_bytes does not match probed byte count",
            )

        existing_rev = obj_row["source_revision"]
        if existing_rev is not None and str(existing_rev) != expected_source_revision_id:
            raise CoreAnalysisRefusal(
                "SOURCE_REVISION_MISMATCH",
                f"Indexed source_revision {existing_rev!r} != {expected_source_revision_id!r}",
            )
        if existing_rev is None:
            with conn:
                conn.execute(
                    "UPDATE source_objects SET source_revision = ? WHERE source_sha256 = ?",
                    (expected_source_revision_id, expected_source_sha256),
                )

        loc_rows = conn.execute("SELECT path, source_sha256 FROM source_locations").fetchall()
        for loc_row in loc_rows:
            if str(loc_row["source_sha256"]) != expected_source_sha256:
                raise CoreAnalysisRefusal(
                    "MULTI_SOURCE_INDEX_UNSUPPORTED",
                    "source_locations contains foreign source_sha256",
                )
            loc_path = str(loc_row["path"])
            resolved_loc = str(Path(loc_path).expanduser().resolve(strict=False))
            if loc_path not in allowed_paths and resolved_loc not in allowed_paths:
                raise CoreAnalysisRefusal(
                    "SOURCE_OCCURRENCE_MISMATCH",
                    f"source_locations contains foreign occurrence path: {loc_path}",
                )

        sample_rows = conn.execute(
            "SELECT row_id, source_sha256, stream_index, pts, timebase_num, timebase_den, timestamp_human, thumbnail_relpath, active FROM samples WHERE active = 1 ORDER BY row_id"
        ).fetchall()
        verified_samples: dict[int, dict[str, Any]] = {}
        for s_row in sample_rows:
            if str(s_row["source_sha256"]) != expected_source_sha256:
                raise CoreAnalysisRefusal(
                    "MULTI_SOURCE_INDEX_UNSUPPORTED",
                    "Active sample belongs to a foreign source_sha256",
                )
            s_stream = s_row["stream_index"]
            if not _is_non_bool_int(s_stream) or int(s_stream) != expected_stream_index:
                raise CoreAnalysisRefusal(
                    "SAMPLE_STREAM_IDENTITY_MISMATCH",
                    f"Sample row {s_row['row_id']} stream_index {s_stream} != probed stream {expected_stream_index}",
                )
            if (
                int(s_row["timebase_num"]) != expected_timebase[0]
                or int(s_row["timebase_den"]) != expected_timebase[1]
            ):
                raise CoreAnalysisRefusal(
                    "SAMPLE_TIMEBASE_MISMATCH",
                    f"Sample row {s_row['row_id']} timebase mismatches probed timebase",
                )
            s_pts = int(s_row["pts"])
            if s_pts < 0:
                raise CoreAnalysisRefusal(
                    "SAMPLE_PTS_INVALID",
                    f"Sample row {s_row['row_id']} has negative PTS {s_pts}",
                )
            verified_samples[int(s_row["row_id"])] = {
                "row_id": int(s_row["row_id"]),
                "source_sha256": str(s_row["source_sha256"]),
                "stream_index": int(s_stream),
                "pts": s_pts,
                "timebase_num": int(s_row["timebase_num"]),
                "timebase_den": int(s_row["timebase_den"]),
                "timestamp_human": str(s_row["timestamp_human"]),
                "thumbnail_relpath": str(s_row["thumbnail_relpath"]),
            }

        return verified_samples, committed_row_count, len(verified_samples)
    finally:
        conn.close()


def _load_and_verify_manifest_digest(
    gen_dir: Path,
    *,
    expected_generation_id: str,
    expected_space_id: str,
) -> str:
    manifest_path = gen_dir / "manifest.json"
    if not manifest_path.is_file():
        return NOT_OBSERVED
    try:
        raw_bytes = manifest_path.read_bytes()
        payload = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CoreAnalysisRefusal(
            "INDEX_MANIFEST_CORRUPT", f"Index manifest.json is corrupt: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise CoreAnalysisRefusal(
            "INDEX_MANIFEST_INVALID", "Index manifest.json must be a JSON object"
        )
    if payload.get("generation_id") != expected_generation_id:
        raise CoreAnalysisRefusal(
            "INDEX_MANIFEST_GENERATION_MISMATCH",
            "Index manifest generation_id does not match expected generation_id",
        )
    if payload.get("space_id") != expected_space_id:
        raise CoreAnalysisRefusal(
            "INDEX_MANIFEST_SPACE_MISMATCH",
            "Index manifest space_id does not match runtime semantic_space_id",
        )
    return hashlib.sha256(raw_bytes).hexdigest()


def _load_optional_refinement_intervals(
    refinement_path: str | Path | None,
    *,
    expected_source_sha256: str,
    expected_source_revision_id: str,
    expected_stream_index: int,
    expected_timebase: tuple[int, int],
) -> dict[int, dict[str, Any]]:
    if refinement_path is None:
        return {}
    path = Path(refinement_path).expanduser()
    if path.is_symlink() or not path.is_file():
        raise CoreAnalysisRefusal(
            "REFINEMENT_ARTIFACT_MISSING",
            f"Refinement artifact does not exist or is a symlink: {path}",
        )
    try:
        raw_bytes = path.read_bytes()
        payload = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CoreAnalysisRefusal(
            "REFINEMENT_ARTIFACT_INVALID_JSON",
            f"Refinement artifact is not valid JSON: {path}",
        ) from exc
    if not isinstance(payload, dict):
        raise CoreAnalysisRefusal(
            "REFINEMENT_ARTIFACT_INVALID", "Refinement artifact must be a JSON object"
        )
    if payload.get("source_sha256") != expected_source_sha256:
        raise CoreAnalysisRefusal(
            "REFINEMENT_SOURCE_SHA256_MISMATCH",
            "Refinement artifact source_sha256 does not match probed source_sha256",
        )
    if payload.get("source_revision_id") != expected_source_revision_id:
        raise CoreAnalysisRefusal(
            "REFINEMENT_SOURCE_REVISION_MISMATCH",
            "Refinement artifact source_revision_id does not match source_revision_id",
        )
    if payload.get("selected_stream_index") != expected_stream_index:
        raise CoreAnalysisRefusal(
            "REFINEMENT_STREAM_INDEX_MISMATCH",
            "Refinement artifact selected_stream_index does not match probed stream",
        )
    tb = payload.get("timebase")
    if tb != {"num": expected_timebase[0], "den": expected_timebase[1]}:
        raise CoreAnalysisRefusal(
            "REFINEMENT_TIMEBASE_MISMATCH",
            "Refinement artifact timebase does not match probed timebase",
        )

    artifact_digest = hashlib.sha256(raw_bytes).hexdigest()
    intervals_by_row: dict[int, dict[str, Any]] = {}
    raw_intervals = payload.get("intervals_by_row_id", {})
    if not isinstance(raw_intervals, dict):
        raise CoreAnalysisRefusal(
            "REFINEMENT_INTERVALS_INVALID",
            "Refinement artifact intervals_by_row_id must be an object",
        )
    for row_key, item in raw_intervals.items():
        try:
            row_id = int(row_key)
        except (TypeError, ValueError) as exc:
            raise CoreAnalysisRefusal(
                "REFINEMENT_ROW_ID_INVALID", f"Invalid refinement row_id: {row_key}"
            ) from exc
        if not isinstance(item, dict):
            raise CoreAnalysisRefusal(
                "REFINEMENT_INTERVAL_ITEM_INVALID",
                f"Refinement entry for row {row_id} must be an object",
            )
        start_pts = item.get("start_pts")
        end_pts = item.get("end_pts")
        if (
            not _is_non_bool_int(start_pts)
            or not _is_non_bool_int(end_pts)
            or start_pts < 0
            or end_pts <= start_pts
        ):
            raise CoreAnalysisRefusal(
                "REFINEMENT_INTERVAL_PTS_INVALID",
                f"Refinement interval for row {row_id} requires 0 <= start_pts < end_pts",
            )
        intervals_by_row[row_id] = {
            "evidence_class": "MEASURED",
            "time_domain": "source_pts",
            "start_pts": int(start_pts),
            "end_pts": int(end_pts),
            "timebase": {"num": expected_timebase[0], "den": expected_timebase[1]},
            "refinement_artifact_ref": str(path),
            "refinement_digest": artifact_digest,
        }
    return intervals_by_row


def analyze_local_video(request: CoreAnalysisRequest) -> CoreAnalysisOutcome:
    """Execute bounded single-video semantic retrieval and atomically publish Report V1."""
    # 1. Validate output root & target report path first (fail fast on no-clobber or path escape)
    raw_output_root = (
        str(request.output_root).strip() if request.output_root is not None else ""
    )
    if not raw_output_root:
        raise CoreAnalysisRefusal("OUTPUT_ROOT_REQUIRED", "--output-root is required")
    target_report = (
        request.report_path
        if request.report_path is not None
        else (Path(raw_output_root) / "semantic-report.json")
    )
    try:
        resolved_output_root, resolved_report_path = validate_output_target_path(
            target_report,
            output_root=raw_output_root,
            require_nonexistent=True,
        )
    except CoreReportPublicationError as exc:
        raise CoreAnalysisRefusal(exc.code, exc.detail) from exc

    # 2. Validate attempt_id, query, top_k, and selected_stream_index
    attempt_id = (
        str(request.attempt_id).strip() if request.attempt_id is not None else ""
    )
    if not attempt_id:
        raise CoreAnalysisRefusal(
            "ATTEMPT_ID_REQUIRED",
            "--attempt-id is required and must not be invented",
        )

    if not _is_non_bool_int(request.top_k) or request.top_k < 1 or request.top_k > 1000:
        raise CoreAnalysisRefusal(
            "INVALID_TOP_K", "--top-k must be an integer between 1 and 1000"
        )

    if request.selected_stream_index is not None and (
        not _is_non_bool_int(request.selected_stream_index)
        or request.selected_stream_index < 0
    ):
        raise CoreAnalysisRefusal(
            "INVALID_SELECTED_STREAM_INDEX",
            "--selected-stream-index must be a non-negative integer",
        )

    try:
        query_env = QueryEnvelope.from_text(request.query)
    except ValueError as exc:
        raise CoreAnalysisRefusal(str(exc), f"Invalid query: {exc}") from exc

    normalized_query_text = str(query_env.text)
    query_digest = hashlib.sha256(normalized_query_text.encode("utf-8")).hexdigest()

    raw_index_root = (
        str(request.index_root).strip() if request.index_root is not None else ""
    )
    if not raw_index_root:
        raise CoreAnalysisRefusal("INDEX_ROOT_REQUIRED", "--index-root is required")
    resolved_index_root = Path(raw_index_root).expanduser().resolve(strict=False)

    # 3. Mode separation, synthetic preflight, and pre-read authority validation
    _validate_synthetic_preflight_args(request, resolved_output_root=resolved_output_root)

    has_real_only_inputs = any(
        (
            request.pilot_authorization_path is not None,
            request.model_root is not None,
            request.model_identity is not None,
            request.model_revision is not None,
            request.weights_sha256 is not None,
            request.device != "cpu",
        )
    )
    if request.fake_embedder:
        if has_real_only_inputs:
            raise CoreAnalysisRefusal(
                "FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS",
                "Cannot combine --fake-embedder with real-mode model or pilot authorization flags",
            )
        resolved_source_revision_id = (
            str(request.source_revision_id).strip()
            if request.source_revision_id is not None
            else ""
        )
        if not resolved_source_revision_id:
            raise CoreAnalysisRefusal(
                "SOURCE_REVISION_ID_REQUIRED",
                "--source-revision-id is required in synthetic mode",
            )
        effective_stream_index = request.selected_stream_index
        auth_record: PilotAuthorization | None = None
        auth_raw_payload: dict[str, Any] = {}
    else:
        if request.model_profile_json is not None:
            raise CoreAnalysisRefusal(
                "FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS",
                "--model-profile-json is only valid with --fake-embedder",
            )
        auth_record, auth_raw_payload, resolved_source_revision_id, effective_stream_index = (
            _validate_and_load_real_authorization(
                request,
                raw_query_text=str(request.query),
                normalized_query_text=normalized_query_text,
                query_digest=query_digest,
                resolved_output_root=resolved_output_root,
            )
        )

    # 4. Snapshot configuration validation and source capture / immutability baseline
    has_any_snapshot_arg = any(
        v is not None
        for v in (
            request.source_snapshot_root,
            request.max_source_bytes,
            request.max_store_bytes,
            request.preverified_snapshot_id,
        )
    )
    if not request.fake_embedder and not has_any_snapshot_arg:
        raise CoreAnalysisRefusal(
            "SOURCE_SNAPSHOT_REQUIRED",
            "Real-mode analyze-local requires --source-snapshot-root, --max-source-bytes, and --max-store-bytes",
        )

    raw_source_str = (
        str(request.source_path).strip() if request.source_path is not None else ""
    )
    if not raw_source_str:
        raise CoreAnalysisRefusal("SOURCE_PATH_REQUIRED", "--source is required")
    source_path = Path(raw_source_str).expanduser()

    snapshot_store: SourceSnapshotStore | None = None
    snapshot_record: VerifiedSourceSnapshot | None = None

    if has_any_snapshot_arg:
        if (
            request.source_snapshot_root is None
            or not _is_non_bool_int(request.max_source_bytes)
            or request.max_source_bytes <= 0
            or not _is_non_bool_int(request.max_store_bytes)
            or request.max_store_bytes <= 0
        ):
            raise CoreAnalysisRefusal(
                "SNAPSHOT_QUOTA_REQUIRED",
                "Snapshot mode requires --source-snapshot-root and positive --max-source-bytes and --max-store-bytes",
            )
        store_factory = request.snapshot_store_factory or SourceSnapshotStore
        try:
            snapshot_store = store_factory(
                Path(request.source_snapshot_root).expanduser(),
                max_source_bytes=int(request.max_source_bytes),
                max_store_bytes=int(request.max_store_bytes),
            )
            auth_id = (
                str(auth_record.authorization_id or "pilot-auth")
                if auth_record is not None
                else f"synthetic-auth:{attempt_id}"
            )
            abs_source_path = source_path.absolute()
            if request.preverified_snapshot_id is not None:
                snapshot_record = snapshot_store.load_verified_snapshot(
                    str(request.preverified_snapshot_id)
                )
                if (
                    snapshot_record.source_locator != str(abs_source_path)
                    or snapshot_record.source_revision_id != resolved_source_revision_id
                    or snapshot_record.authorization_id != auth_id
                    or (
                        auth_record is not None
                        and snapshot_record.sha256 != auth_record.source_sha256
                    )
                ):
                    raise CoreAnalysisRefusal(
                        "PREVERIFIED_SNAPSHOT_AUTHORIZATION_BINDING_MISMATCH",
                        "Preverified snapshot metadata does not match current source/authority binding",
                    )
                live_sha, live_bytes = _hash_regular_file(source_path)
                if (
                    live_sha != snapshot_record.sha256
                    or live_bytes != snapshot_record.byte_count
                ):
                    raise CoreAnalysisRefusal(
                        "SOURCE_SNAPSHOT_LIVE_SOURCE_DIVERGED",
                        "Live source file bytes or digest diverged from preverified snapshot",
                    )
            else:
                expected_sha = (
                    auth_record.source_sha256
                    if auth_record is not None
                    else _hash_regular_file(source_path)[0]
                )
                snapshot_record = snapshot_store.capture(
                    abs_source_path,
                    expected_sha256=expected_sha,
                    authorization_id=auth_id,
                    source_revision_id=resolved_source_revision_id,
                )
        except SourceSnapshotError as exc:
            raise CoreAnalysisRefusal(str(exc), f"Source snapshot error: {exc}") from exc

        before_sha256 = snapshot_record.sha256
        before_byte_count = snapshot_record.byte_count
        execution_source_path = Path(snapshot_record.snapshot_path)
        custody_state = "SNAPSHOT_VERIFIED"
        source_locator_str = snapshot_record.source_locator
    else:
        before_sha256, before_byte_count = _hash_regular_file(source_path)
        execution_source_path = source_path.resolve(strict=False)
        custody_state = "PRESERVED_IMMUTABLE"
        source_locator_str = str(source_path)

    # 5. Measured source probe (ffprobe)
    probe_runner = request.probe_fn or probe_real_source
    try:
        canonical_kwargs = {
            "executable": request.probe_executable,
            "timeout_seconds": DEFAULT_PROBE_TIMEOUT_SECONDS,
            "selected_stream_index": effective_stream_index,
            "source_revision_id": resolved_source_revision_id,
            "policy_identity": "vip_fvs.core_analyze_local.v1",
            "source_locator": source_locator_str,
            "snapshot_evidence": snapshot_record.as_evidence() if snapshot_record is not None else None,
        }
        legacy_kwargs = {
            "source_path": execution_source_path,
            "source_revision_id": resolved_source_revision_id,
            "probe_executable": request.probe_executable,
            "selected_stream_index": effective_stream_index,
            "source_locator": source_locator_str,
            "snapshot_evidence": snapshot_record.as_evidence() if snapshot_record is not None else None,
        }
        try:
            probe_signature = inspect.signature(probe_runner)
        except (TypeError, ValueError):
            probe_signature = None
        if probe_signature is not None and not _signature_accepts(probe_signature, (execution_source_path,), canonical_kwargs):
            if _signature_accepts(probe_signature, (), legacy_kwargs):
                probe = probe_runner(**legacy_kwargs)
            else:
                probe = probe_runner(execution_source_path, **canonical_kwargs)
        else:
            probe = probe_runner(execution_source_path, **canonical_kwargs)
    except (ProbeFailure, MeasuredProbeRefusal) as exc:
        raise CoreAnalysisRefusal(str(exc), f"Source probe failed: {exc}") from exc

    if (
        probe.source_sha256 != before_sha256
        or probe.source_byte_count != before_byte_count
    ):
        raise CoreAnalysisRefusal(
            "PROBE_SOURCE_DIGEST_MISMATCH",
            "Probed source digest or byte count does not match verified source baseline",
        )
    if auth_record is not None and probe.source_sha256 != auth_record.source_sha256:
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_SOURCE_SHA256_MISMATCH",
            "Probed source SHA-256 does not match authorized source_sha256",
        )
    if (
        effective_stream_index is not None
        and probe.selected_stream_index != effective_stream_index
    ):
        raise CoreAnalysisRefusal(
            "PROBE_STREAM_SELECTION_MISMATCH",
            f"Probed stream index {probe.selected_stream_index} != requested stream index {effective_stream_index}",
        )
    if (
        not _is_non_bool_int(probe.selected_stream_index)
        or probe.selected_stream_index < 0
        or not _is_non_bool_int(probe.timebase_num)
        or probe.timebase_num <= 0
        or not _is_non_bool_int(probe.timebase_den)
        or probe.timebase_den <= 0
    ):
        raise CoreAnalysisRefusal(
            "PROBE_TIMING_EVIDENCE_INVALID",
            "Probe result lacks valid non-negative stream index or positive rational timebase",
        )

    # 6. Optional refinement artifact verification
    refinement_intervals = _load_optional_refinement_intervals(
        request.refinement_artifact_path,
        expected_source_sha256=probe.source_sha256,
        expected_source_revision_id=resolved_source_revision_id,
        expected_stream_index=probe.selected_stream_index,
        expected_timebase=(probe.timebase_num, probe.timebase_den),
    )

    # 7. Runtime & semantic space initialization and validation
    runtime = (
        request.runtime
        if request.runtime is not None
        else _build_default_runtime(request)
    )
    default_runtime_used = request.runtime is None
    embedder_calls = {"image": 0, "text": 0}
    engine_runtime = runtime
    if default_runtime_used:
        from types import SimpleNamespace

        image_embedder = getattr(runtime, "image_embedder", None)
        text_embedder = getattr(runtime, "text_embedder", None)

        def tracked_image_embedder(paths: Any) -> Any:
            embedder_calls["image"] += 1
            return image_embedder(paths)

        def tracked_text_embedder(texts: Any) -> Any:
            embedder_calls["text"] += 1
            return text_embedder(texts)

        engine_runtime = SimpleNamespace(
            semantic_space=getattr(runtime, "semantic_space", None),
            runtime_identity=getattr(runtime, "runtime_identity", None),
            fake=getattr(runtime, "fake", False),
            fake_embedder=getattr(runtime, "fake_embedder", False),
            image_embedder=tracked_image_embedder,
            text_embedder=tracked_text_embedder,
        )
    space = getattr(runtime, "semantic_space", None)
    if space is None:
        raise CoreAnalysisRefusal(
            "RUNTIME_SEMANTIC_SPACE_MISSING",
            "Runtime is missing semantic_space contract",
        )
    runtime_identity = str(getattr(runtime, "runtime_identity", "") or "").strip()
    if not runtime_identity:
        raise CoreAnalysisRefusal(
            "RUNTIME_IDENTITY_MISSING", "Runtime is missing runtime_identity"
        )

    model_identity_str = str(
        _resolve_space_attr(space, "model_identity", "model_id", default="")
    )
    model_family_str = _derive_model_family(space)
    frozen_revision_str = str(
        _resolve_space_attr(space, "frozen_revision", "model_revision", default="")
    )
    weights_sha256_str = str(_resolve_space_attr(space, "weights_sha256", default=""))
    processor_digest_str = str(
        _resolve_space_attr(space, "processor_digest", default="")
    )
    image_preproc_digest_str = str(
        _resolve_space_attr(space, "image_preprocessing_digest", default="")
    )
    text_contract_str = str(
        _resolve_space_attr(
            space, "text_preprocessing_contract", "text_preprocessing_id", default=""
        )
    )
    space_id_str = _compute_space_id(space)

    is_synthetic_runtime = bool(
        request.fake_embedder
        or getattr(runtime, "fake", False)
        or getattr(runtime, "fake_embedder", False)
        or any(
            marker in token.lower()
            for token in (runtime_identity, model_family_str, model_identity_str)
            for marker in ("fake", "synthetic")
        )
    )
    if not request.fake_embedder and is_synthetic_runtime:
        raise CoreAnalysisRefusal(
            "FAKE_RUNTIME_FORBIDDEN_IN_REAL_MODE",
            "Synthetic/fake embedder runtime cannot execute in REAL mode",
        )
    runtime_mode = "SYNTHETIC" if is_synthetic_runtime else "REAL"

    if (
        auth_record is not None
        and auth_record.semantic_space_id is not None
        and str(auth_record.semantic_space_id) != space_id_str
    ):
        raise CoreAnalysisRefusal(
            "AUTHORIZATION_SEMANTIC_SPACE_MISMATCH",
            "Runtime semantic_space_id does not match authorized semantic_space_id",
        )

    # 8. Index generation inspection, single-source scope guard, and indexing
    engine = request.engine if request.engine is not None else _build_default_engine()
    spec = engine.build_generation_spec(space)
    spec_space_id = str(_resolve_space_attr(spec, "space_id", "semantic_space_id", default=""))
    if spec_space_id != space_id_str:
        raise CoreAnalysisRefusal(
            "INDEX_SPEC_SEMANTIC_SPACE_MISMATCH",
            "Generation spec space_id does not match runtime semantic_space_id",
        )

    gen_dir = resolved_index_root / "generations" / str(spec.generation_id)
    db_path = gen_dir / "index.sqlite"
    allowed_paths = {
        str(execution_source_path),
        str(execution_source_path.resolve(strict=False)),
        str(source_path),
        str(source_path.resolve(strict=False)),
        source_locator_str,
    }

    was_already_indexed = _inspect_generation_pre_index(
        db_path,
        expected_space_id=space_id_str,
        expected_source_sha256=probe.source_sha256,
        expected_source_revision_id=resolved_source_revision_id,
        expected_stream_index=probe.selected_stream_index,
        expected_timebase=(probe.timebase_num, probe.timebase_den),
        expected_byte_count=probe.source_byte_count,
        allowed_paths=allowed_paths,
    )

    try:
        index_summary = _invoke_engine_index_source(
            engine,
            source_path=execution_source_path,
            index_root=resolved_index_root,
            spec=spec,
            runtime=engine_runtime,
        )
    except CoreAnalysisRefusal:
        raise
    except Exception as exc:
        raise CoreAnalysisRefusal(
            "INDEX_EXECUTION_FAILED", f"Indexing failed: {exc}"
        ) from exc

    if int(index_summary.get("failed", 0)) > 0:
        raise CoreAnalysisRefusal(
            "INDEX_SOURCE_FAILED", "Indexing reported failed source state"
        )
    if int(index_summary.get("reused", 0)) > 0 and not was_already_indexed:
        raise CoreAnalysisRefusal(
            "SOURCE_OCCURRENCE_MISMATCH",
            "Refusing silent duplicate SHA reuse across distinct source occurrences",
        )

    if int(index_summary.get("indexed", 0)) > 0:
        index_disposition = "INDEXED"
    elif int(index_summary.get("skipped", 0)) > 0:
        index_disposition = "SKIPPED_UNCHANGED"
    elif was_already_indexed and int(index_summary.get("reused", 0)) > 0:
        index_disposition = "REUSED_SAME_OCCURRENCE"
    else:
        index_disposition = "INDEXED"

    # 9. Post-index SQLite or custom engine verification
    if db_path.exists():
        verified_samples, committed_row_count, source_sample_count = (
            _verify_and_bind_generation_post_index(
                db_path,
                expected_space_id=space_id_str,
                expected_source_sha256=probe.source_sha256,
                expected_source_revision_id=resolved_source_revision_id,
                expected_stream_index=probe.selected_stream_index,
                expected_timebase=(probe.timebase_num, probe.timebase_den),
                expected_byte_count=probe.source_byte_count,
                allowed_paths=allowed_paths,
            )
        )
        manifest_digest = _load_and_verify_manifest_digest(
            gen_dir,
            expected_generation_id=str(spec.generation_id),
            expected_space_id=space_id_str,
        )
    else:
        engine_sources = getattr(engine, "source_sha256_set", None)
        if engine_sources is not None:
            source_set = {str(s) for s in engine_sources}
            if source_set and source_set != {probe.source_sha256}:
                raise CoreAnalysisRefusal(
                    "MULTI_SOURCE_INDEX_UNSUPPORTED",
                    "Injected engine contains multiple or foreign source_sha256 entries",
                )
        elif not bool(getattr(engine, "single_source_verified", True)):
            raise CoreAnalysisRefusal(
                "SOURCE_SCOPE_UNPROVABLE",
                "Injected engine cannot prove single-source index scope",
            )

        raw_verified_samples = getattr(engine, "verified_sample_records", None)
        if callable(raw_verified_samples):
            raw_verified_samples = raw_verified_samples(str(spec.generation_id))
        if raw_verified_samples is not None and not isinstance(
            raw_verified_samples, Mapping
        ):
            raise CoreAnalysisRefusal(
                "HIT_STREAM_METADATA_UNVERIFIED",
                "verified_sample_records on injected engine must be a mapping",
            )
        verified_samples = (
            {int(k): dict(v) for k, v in raw_verified_samples.items()}
            if isinstance(raw_verified_samples, Mapping)
            else {}
        )
        committed_row_count = int(
            getattr(engine, "committed_row_count", len(verified_samples))
        )
        source_sample_count = len(verified_samples)
        manifest_digest = str(getattr(engine, "manifest_digest", NOT_OBSERVED))

    # 10. Query execution & candidate verification
    if db_path.exists() and source_sample_count == 0:
        raw_hits: list[Any] = []
    else:
        try:
            raw_hits = _invoke_engine_query(
                engine,
                index_root=resolved_index_root,
                spec=spec,
                query_text=normalized_query_text,
                runtime=engine_runtime,
                top_k=request.top_k,
            )
        except CoreAnalysisRefusal:
            raise
        except Exception as exc:
            raise CoreAnalysisRefusal(
                "QUERY_EXECUTION_FAILED", f"Query execution failed: {exc}"
            ) from exc

    validated_candidates: list[dict[str, Any]] = []
    seen_row_ids: set[int] = set()

    for hit in raw_hits:
        hit_sha = str(getattr(hit, "source_sha256", "")).strip()
        if hit_sha != probe.source_sha256:
            raise CoreAnalysisRefusal(
                "MULTI_SOURCE_INDEX_UNSUPPORTED",
                f"Query returned candidate from foreign source_sha256 {hit_sha!r}",
            )
        hit_row_id = getattr(hit, "row_id", None)
        if not _is_non_bool_int(hit_row_id) or hit_row_id < 0:
            raise CoreAnalysisRefusal(
                "CANDIDATE_ROW_ID_INVALID",
                f"Query hit has invalid row_id: {hit_row_id!r}",
            )
        if hit_row_id in seen_row_ids:
            raise CoreAnalysisRefusal(
                "CANDIDATE_DUPLICATE_ROW_ID",
                f"Query returned duplicate row_id {hit_row_id}",
            )
        seen_row_ids.add(hit_row_id)

        # Stream authority must come from verified sample/source_objects record, never invented from SearchHit
        sample_meta = verified_samples.get(hit_row_id)
        if sample_meta is None:
            raise CoreAnalysisRefusal(
                "HIT_STREAM_METADATA_UNVERIFIED",
                f"SearchHit row_id={hit_row_id} lacks independently verified sample/stream metadata",
            )
        sample_stream = sample_meta.get("stream_index")
        if (
            not _is_non_bool_int(sample_stream)
            or sample_stream != probe.selected_stream_index
        ):
            raise CoreAnalysisRefusal(
                "RETRIEVAL_STREAM_IDENTITY_MISMATCH",
                f"Verified sample stream_index {sample_stream!r} != probed stream {probe.selected_stream_index}",
            )
        if str(sample_meta.get("source_sha256", "")) != probe.source_sha256:
            raise CoreAnalysisRefusal(
                "CANDIDATE_SOURCE_SHA256_MISMATCH",
                f"Sample row {hit_row_id} source_sha256 mismatches probed source_sha256",
            )

        for attr_name in ("stream_index", "selected_stream_index"):
            if hasattr(hit, attr_name):
                explicit_val = getattr(hit, attr_name)
                if explicit_val is not None and (
                    not _is_non_bool_int(explicit_val)
                    or explicit_val != probe.selected_stream_index
                ):
                    raise CoreAnalysisRefusal(
                        "RETRIEVAL_STREAM_IDENTITY_MISMATCH",
                        f"Hit {attr_name}={explicit_val!r} != probed stream {probe.selected_stream_index}",
                    )

        hit_pts = getattr(hit, "pts", None)
        if not _is_non_bool_int(hit_pts) or hit_pts < 0:
            raise CoreAnalysisRefusal(
                "CANDIDATE_PTS_INVALID",
                f"Hit row {hit_row_id} has invalid PTS {hit_pts!r}",
            )
        if "pts" in sample_meta and int(sample_meta["pts"]) != hit_pts:
            raise CoreAnalysisRefusal(
                "CANDIDATE_PTS_MISMATCH",
                f"Hit row {hit_row_id} PTS {hit_pts} != sample record PTS {sample_meta['pts']}",
            )

        hit_tb_num = getattr(hit, "timebase_num", None)
        hit_tb_den = getattr(hit, "timebase_den", None)
        if (
            not _is_non_bool_int(hit_tb_num)
            or not _is_non_bool_int(hit_tb_den)
            or (hit_tb_num, hit_tb_den) != (probe.timebase_num, probe.timebase_den)
        ):
            raise CoreAnalysisRefusal(
                "CANDIDATE_TIMEBASE_MISMATCH",
                f"Hit row {hit_row_id} timebase {(hit_tb_num, hit_tb_den)} != probed timebase {(probe.timebase_num, probe.timebase_den)}",
            )

        hit_score = getattr(hit, "score", None)
        if (
            not isinstance(hit_score, (int, float))
            or isinstance(hit_score, bool)
            or not math.isfinite(float(hit_score))
        ):
            raise CoreAnalysisRefusal(
                "CANDIDATE_SCORE_INVALID",
                f"Hit row {hit_row_id} has non-finite score {hit_score!r}",
            )

        thumb_status = str(getattr(hit, "thumbnail_status", "NOT_OBSERVED"))
        thumb_path = getattr(hit, "thumbnail_path", None)
        if thumb_status == "PRESENT" and (
            not isinstance(thumb_path, str) or not thumb_path.strip()
        ):
            thumb_status = "MISSING"
            thumb_path = None
        elif thumb_status not in {"PRESENT", "MISSING", "NOT_OBSERVED"}:
            thumb_status = "NOT_OBSERVED"
            thumb_path = None

        display_ts = str(
            getattr(
                hit,
                "timestamp_human",
                sample_meta.get("timestamp_human", "00:00:00.000"),
            )
        ).strip()
        if not display_ts:
            display_ts = "00:00:00.000"

        validated_candidates.append(
            {
                "row_id": int(hit_row_id),
                "score": float(hit_score),
                "_raw_score": float(hit_score),
                "pts": int(hit_pts),
                "display_timestamp": display_ts,
                "thumbnail_status": thumb_status,
                "thumbnail_path": str(thumb_path) if thumb_path else None,
            }
        )

    validated_candidates.sort(
        key=lambda item: (-item["_raw_score"], item["pts"], item["row_id"])
    )
    selected_candidates = validated_candidates[: request.top_k]

    if not selected_candidates:
        total_eligible_matches = 0
    elif len(validated_candidates) < request.top_k:
        total_eligible_matches = len(validated_candidates)
    else:
        total_eligible_matches = NOT_OBSERVED

    matches_payload: list[dict[str, Any]] = []
    refinement_observed = False
    for rank_idx, cand in enumerate(selected_candidates, start=1):
        row_id = cand["row_id"]
        pts = cand["pts"]
        row_interval = refinement_intervals.get(row_id, NOT_OBSERVED)
        if row_interval != NOT_OBSERVED:
            refinement_observed = True
        matches_payload.append(
            {
                "candidate_id": f"candidate:{attempt_id}:rank:{rank_idx}:row:{row_id}",
                "row_id": row_id,
                "rank": rank_idx,
                "score": cand["score"],
                "score_is_probability": False,
                "source_sha256": probe.source_sha256,
                "source_revision_id": resolved_source_revision_id,
                "source_locator": source_locator_str,
                "selected_stream_index": probe.selected_stream_index,
                "sampled_timing": {
                    "pts": pts,
                    "timebase": {
                        "num": probe.timebase_num,
                        "den": probe.timebase_den,
                    },
                    "time_domain": "source_pts",
                    "rational_seconds": format_rational_seconds(
                        pts, probe.timebase_num, probe.timebase_den
                    ),
                    "display_timestamp": cand["display_timestamp"],
                    "display_only_not_frame_authority": True,
                    "evidence_class": "MEASURED",
                    "measurement_provenance": "ffmpeg_showinfo_one_pass_sample_pts",
                    "is_event_boundary": False,
                    "is_edit_boundary": False,
                },
                "approx_semantic_location": build_point_semantic_location(
                    pts, probe.timebase_num, probe.timebase_den
                ),
                "semantic_assertion": {
                    "evidence_class": "MATCHED",
                    "binding_eligible": False,
                    "assertion_kind": "query_visual_similarity_candidate",
                    "caption_claim": NOT_OBSERVED,
                },
                "measured_frame_interval": row_interval,
                "thumbnail": {
                    "status": cand["thumbnail_status"],
                    "path": cand["thumbnail_path"],
                },
            }
        )

    # 11. Re-verify source and snapshot immutability after analysis before publishing
    if snapshot_store is not None and snapshot_record is not None:
        try:
            snapshot_store.verify(snapshot_record)
        except SourceSnapshotError as exc:
            raise CoreAnalysisRefusal(
                "SOURCE_MUTATED_DURING_ANALYSIS",
                f"Snapshot immutability check failed after analysis: {exc}",
            ) from exc
    after_sha256, after_byte_count = _hash_regular_file(source_path)
    if after_sha256 != before_sha256 or after_byte_count != before_byte_count:
        raise CoreAnalysisRefusal(
            "SOURCE_MUTATED_DURING_ANALYSIS",
            "Live source file digest or byte count changed during analysis",
        )

    # 12. Assemble and publish Report V1
    source_section: dict[str, Any] = {
        "source_locator": source_locator_str,
        "source_revision_id": resolved_source_revision_id,
        "source_sha256": probe.source_sha256,
        "source_byte_count": probe.source_byte_count,
        "custody_state": custody_state,
        "immutability_verified": {
            "before_analysis": True,
            "after_analysis": True,
            "source_sha256_before": before_sha256,
            "source_sha256_after": after_sha256,
            "source_byte_count_before": before_byte_count,
            "source_byte_count_after": after_byte_count,
        },
        "snapshot": (
            snapshot_record.as_evidence()
            if snapshot_record is not None
            else NOT_OBSERVED
        ),
        "probe": {
            "probe_artifact_ref": (
                str(probe.probe_artifact_ref)
                if getattr(probe, "probe_artifact_ref", None)
                else f"probe:{attempt_id}:{probe.source_sha256[:12]}"
            ),
            "probe_digest": probe.probe_digest,
            "selected_stream_index": probe.selected_stream_index,
            "timebase": {
                "num": probe.timebase_num,
                "den": probe.timebase_den,
            },
            "time_domain": "source_pts",
            "evidence_class": "MEASURED",
            "measurement_provenance": "ffprobe_stream_probe",
        },
    }

    if auth_record is not None:
        auth_rec_digest = str(
            auth_record.record_digest or _canonical_sha256(auth_raw_payload)
        )
        policy_digest = str(
            auth_record.policy_digest
            or _canonical_sha256(
                {
                    "authorization_id": auth_record.authorization_id or "pilot-auth",
                    "purpose": auth_record.purpose,
                    "local_only": True,
                    "allowed_stages": list(auth_record.allowed_stages),
                }
            )
        )
        scope_digest = str(
            auth_record.scope_digest
            or _canonical_sha256(
                {
                    "source_path": str(auth_record.source_path),
                    "source_sha256": auth_record.source_sha256,
                    "model_identity": str(request.model_identity),
                    "model_revision": auth_record.model_revision,
                    "weights_sha256": auth_record.weights_sha256,
                    "index_root": str(auth_record.index_root),
                }
            )
        )
        authority_section: dict[str, Any] = {
            "authorization_mode": "OWNER_PILOT_AUTHORIZATION",
            "authorization_id": str(auth_record.authorization_id or "pilot-auth"),
            "authorization_record_digest": auth_rec_digest,
            "policy_digest": policy_digest,
            "scope_digest": scope_digest,
            "local_only": True,
            "development_source_auth_enforcement": "DISABLED_BY_OWNER",
        }
    else:
        authority_section = {
            "authorization_mode": "SYNTHETIC_TEST_ONLY",
            "authorization_id": f"synthetic-auth:{attempt_id}",
            "authorization_record_digest": NOT_OBSERVED,
            "policy_digest": NOT_OBSERVED,
            "scope_digest": NOT_OBSERVED,
            "local_only": True,
            "development_source_auth_enforcement": "DISABLED_BY_OWNER",
        }

    model_section: dict[str, Any] = {
        "model_family": model_family_str,
        "model_identity": model_identity_str,
        "frozen_revision": frozen_revision_str,
        "weights_sha256": weights_sha256_str,
        "processor_digest": processor_digest_str,
        "image_preprocessing_digest": image_preproc_digest_str,
        "text_preprocessing_contract": text_contract_str,
        "embedding_dim": int(space.embedding_dim),
        "dtype": str(space.dtype),
        "normalization": str(space.normalization),
        "semantic_space_id": space_id_str,
        "runtime_identity": runtime_identity,
        "runtime_mode": runtime_mode,
        "authentic_inference_observed": bool(
            runtime_mode == "REAL"
            and default_runtime_used
            and request.engine is None
            and embedder_calls["text"] > 0
        ),
    }

    index_section: dict[str, Any] = {
        "generation_id": str(spec.generation_id),
        "semantic_space_id": space_id_str,
        "index_disposition": index_disposition,
        "manifest_digest": manifest_digest,
        "committed_row_count": committed_row_count,
        "source_sample_count": source_sample_count,
        "single_source_scope_verified": True,
        "sampling_policy": {
            "sampling_policy_id": str(spec.sampling_policy_id),
            "sampling_policy_version": int(spec.sampling_policy_version),
            "sampling_interval_seconds": float(spec.sampling_interval_seconds),
            "selected_stream_policy": str(
                getattr(
                    spec,
                    "selected_stream_policy",
                    "ffprobe_explicit_or_first_video_stream",
                )
            ),
            "selected_stream_index": probe.selected_stream_index,
        },
    }

    query_section: dict[str, Any] = {
        "query_id": f"query:{attempt_id}:{query_digest[:12]}",
        "raw_text": str(request.query),
        "normalized_text": normalized_query_text,
        "query_digest": query_digest,
        "modality": "text",
        "score_interpretation": "uncalibrated_cosine_similarity_not_probability",
    }

    run_id = f"core-analyze:{attempt_id}"
    try:
        report = build_core_semantic_report(
            attempt_id=attempt_id,
            run_id=run_id,
            runtime_mode=runtime_mode,
            top_k=request.top_k,
            total_eligible_matches=total_eligible_matches,
            source=source_section,
            authority=authority_section,
            model=model_section,
            index=index_section,
            query=query_section,
            matches=matches_payload,
            report_path=str(resolved_report_path),
            output_root=str(resolved_output_root),
            refinement_observed=refinement_observed,
        )
        published_path = publish_core_semantic_report(
            report,
            resolved_report_path,
            output_root=resolved_output_root,
        )
    except (CoreReportError, CoreReportPublicationError) as exc:
        raise CoreAnalysisRefusal(exc.code, exc.detail) from exc

    summary = {
        "command": "analyze-local",
        "schema_version": CORE_REPORT_SCHEMA_VERSION,
        "report_kind": CORE_REPORT_KIND,
        "analysis_kind": ANALYSIS_KIND_SEMANTIC_RETRIEVAL,
        "attempt_id": attempt_id,
        "run_id": run_id,
        "runtime_mode": runtime_mode,
        "stage_status": report["stage_status"],
        "result_kind": report["result_kind"],
        "source_sha256": probe.source_sha256,
        "source_revision_id": resolved_source_revision_id,
        "selected_stream_index": probe.selected_stream_index,
        "semantic_space_id": space_id_str,
        "generation_id": str(spec.generation_id),
        "query_digest": query_digest,
        "top_k": request.top_k,
        "total_eligible_matches": total_eligible_matches,
        "returned_candidate_count": report["returned_candidate_count"],
        "report_path": str(published_path),
        "report_digest": report["artifact"]["report_digest"],
        "errors": [],
    }
    return CoreAnalysisOutcome(
        report=report,
        report_path=published_path,
        summary=summary,
    )
