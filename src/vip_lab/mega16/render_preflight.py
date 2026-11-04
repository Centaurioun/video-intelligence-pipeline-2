"""MEGA-16.1 — Offline Render Preflight Specification (Non-Executing).

Builds a deterministic, non-executing `RenderPreflightSpecification` from MEGA-15's
`Gate3OfflinePreparationPacket` and `Mega15LineageReceipt`, documenting the exact
canonical `vip_fvs.real_preview_receipt` schema requirements (`_REQUIRED_FIELDS`)
without executing FFmpeg, creating media files, or authorizing preview/production render.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vip_fvs.real_preview_receipt import (
    _FIELDS as REAL_PREVIEW_RECEIPT_REQUIRED_FIELDS,
    SCHEMA as RECEIPT_SCHEMA_VERSION,
    SCOPE as PREVIEW_NON_PRODUCTION_MARKER,
)
from vip_lab.common import (
    SyntheticContextMarker,
    canonical_sha256,
)
from vip_lab.mega15.editorial_handoff import (
    Gate3OfflinePreparationPacket,
    verify_gate3_offline_preparation_packet,
)
from vip_lab.mega15.lineage import (
    Mega15LineageReceipt,
    REFUSAL_MEGA15_LINEAGE_BROKEN,
    verify_mega15_lineage_receipt,
)
from vip_lab.mega15.temporal_preflight import (
    ensure_non_empty_str,
    make_synthetic_context,
    parse_synthetic_context_dict,
    raise_mega15_error,
    serialize_synthetic_context,
    validate_synthetic_context,
    validate_video_stream_namespace,
)

RENDER_PREFLIGHT_SCHEMA_VERSION = "1.0.0"
RENDER_PREFLIGHT_KIND = "vip_lab.mega16.render_preflight_specification"

REFUSAL_RENDER_EXECUTION_FORBIDDEN = "REFUSAL_OFFLINE_RENDER_EXECUTION_FORBIDDEN"
REFUSAL_PREVIEW_AS_PRODUCTION_FORBIDDEN = "REFUSAL_PREVIEW_AS_PRODUCTION_EXPORT_FORBIDDEN"
REFUSAL_RENDER_OUTPUT_PATH_FORBIDDEN = "REFUSAL_RENDER_MEDIA_OUTPUT_PATH_FORBIDDEN"
REFUSAL_FFMPEG_INVOCATION_FORBIDDEN = "REFUSAL_FFMPEG_INVOCATION_FORBIDDEN"


def refuse_render_or_ffmpeg_execution(
    *,
    execute_render: bool = False,
    ffmpeg_argv: Sequence[str] | None = None,
    media_output_path: str | None = None,
    treat_preview_as_production: bool = False,
) -> None:
    """Fail closed if a caller attempts to invoke FFmpeg, write media outputs, or escalate preview."""
    if execute_render:
        raise_mega15_error(
            REFUSAL_RENDER_EXECUTION_FORBIDDEN,
            "Executing real or preview media rendering is forbidden in MEGA-16 offline preflight.",
        )
    if ffmpeg_argv is not None:
        raise_mega15_error(
            REFUSAL_FFMPEG_INVOCATION_FORBIDDEN,
            f"FFmpeg command invocation is forbidden in offline preflight: {list(ffmpeg_argv)!r}",
        )
    if media_output_path is not None:
        raise_mega15_error(
            REFUSAL_RENDER_OUTPUT_PATH_FORBIDDEN,
            f"Media output path specification is forbidden in offline preflight: {media_output_path!r}",
        )
    if treat_preview_as_production:
        raise_mega15_error(
            REFUSAL_PREVIEW_AS_PRODUCTION_FORBIDDEN,
            "Non-production preview eligibility or receipts never authorize production export.",
        )


@dataclass(frozen=True)
class RenderWindowSpecification:
    """Per-occurrence non-executing render preflight window specification."""

    window_id: str
    queue_item_id: str
    revision_id: str
    content_id: str
    source_path: str
    source_sha256: str
    stream_id: str
    timebase_num: int
    timebase_den: int
    resolved_start_pts: int
    resolved_end_pts: int
    subdivided_segments: tuple[tuple[int, int], ...]
    temporal_record_id: str
    temporal_record_digest: str
    handoff_envelope_id: str
    handoff_envelope_digest: str
    render_execution_state: str
    media_output_path: None

    @property
    def candidate_item_id(self) -> str:
        return self.queue_item_id

    @property
    def source_revision_id(self) -> str:
        return self.revision_id

    @property
    def source_timebase_num(self) -> int:
        return self.timebase_num

    @property
    def source_timebase_den(self) -> int:
        return self.timebase_den

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_id": self.window_id,
            "queue_item_id": self.queue_item_id,
            "revision_id": self.revision_id,
            "content_id": self.content_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "stream_id": self.stream_id,
            "timebase_num": self.timebase_num,
            "timebase_den": self.timebase_den,
            "resolved_start_pts": self.resolved_start_pts,
            "resolved_end_pts": self.resolved_end_pts,
            "subdivided_segments": [[s, e] for s, e in self.subdivided_segments],
            "temporal_record_id": self.temporal_record_id,
            "temporal_record_digest": self.temporal_record_digest,
            "handoff_envelope_id": self.handoff_envelope_id,
            "handoff_envelope_digest": self.handoff_envelope_digest,
            "render_execution_state": self.render_execution_state,
            "media_output_path": self.media_output_path,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "RenderWindowSpecification":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                "RENDER_PREFLIGHT_INVALID_WINDOW",
                "Window specification must be a mapping",
            )
        if payload.get("media_output_path") is not None:
            raise_mega15_error(
                REFUSAL_RENDER_OUTPUT_PATH_FORBIDDEN,
                "media_output_path must be None in offline render preflight",
            )
        raw_segs = payload.get("subdivided_segments")
        if not isinstance(raw_segs, Sequence) or isinstance(raw_segs, (str, bytes)):
            raise_mega15_error(
                "RENDER_PREFLIGHT_INVALID_SEGMENTS",
                "subdivided_segments must be a sequence",
            )
        segs = tuple((int(pair[0]), int(pair[1])) for pair in raw_segs)
        return cls(
            window_id=str(payload.get("window_id", "")),
            queue_item_id=str(
                payload.get("queue_item_id", payload.get("candidate_item_id", ""))
            ),
            revision_id=str(
                payload.get("revision_id", payload.get("source_revision_id", ""))
            ),
            content_id=str(payload.get("content_id", "")),
            source_path=str(payload.get("source_path", "")),
            source_sha256=str(payload.get("source_sha256", "")),
            stream_id=str(payload.get("stream_id", "")),
            timebase_num=int(
                payload.get("timebase_num", payload.get("source_timebase_num", 0))
            ),
            timebase_den=int(
                payload.get("timebase_den", payload.get("source_timebase_den", 0))
            ),
            resolved_start_pts=int(payload.get("resolved_start_pts", 0)),
            resolved_end_pts=int(payload.get("resolved_end_pts", 0)),
            subdivided_segments=segs,
            temporal_record_id=str(payload.get("temporal_record_id", "")),
            temporal_record_digest=str(payload.get("temporal_record_digest", "")),
            handoff_envelope_id=str(payload.get("handoff_envelope_id", "")),
            handoff_envelope_digest=str(payload.get("handoff_envelope_digest", "")),
            render_execution_state=str(payload.get("render_execution_state", "")),
            media_output_path=None,
        )


@dataclass(frozen=True)
class RenderPreflightSpecification:
    """Offline non-executing Gate-3 render preflight specification."""

    schema_version: str
    kind: str
    specification_id: str
    catalog_id: str
    queue_digest: str
    preparation_packet_id: str
    preparation_packet_digest: str
    mega15_lineage_receipt_id: str
    mega15_lineage_receipt_digest: str
    windows: tuple[RenderWindowSpecification, ...]
    gate3_render_receipt_required_fields: tuple[str, ...]
    gate3_render_receipt_schema_version: str
    expected_non_production_marker: str
    render_execution_state: str
    preview_eligible: bool
    production_export_authorized: bool
    ffmpeg_invocation_permitted: bool
    media_write_permitted: bool
    synthetic_context: SyntheticContextMarker
    specification_digest: str

    @property
    def queue_id(self) -> str:
        return self.catalog_id

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "specification_id": self.specification_id,
            "catalog_id": self.catalog_id,
            "queue_digest": self.queue_digest,
            "preparation_packet_id": self.preparation_packet_id,
            "preparation_packet_digest": self.preparation_packet_digest,
            "mega15_lineage_receipt_id": self.mega15_lineage_receipt_id,
            "mega15_lineage_receipt_digest": self.mega15_lineage_receipt_digest,
            "windows": [w.to_dict() for w in self.windows],
            "gate3_render_receipt_required_fields": list(
                self.gate3_render_receipt_required_fields
            ),
            "gate3_render_receipt_schema_version": self.gate3_render_receipt_schema_version,
            "expected_non_production_marker": self.expected_non_production_marker,
            "render_execution_state": self.render_execution_state,
            "preview_eligible": self.preview_eligible,
            "production_export_authorized": self.production_export_authorized,
            "ffmpeg_invocation_permitted": self.ffmpeg_invocation_permitted,
            "media_write_permitted": self.media_write_permitted,
            "synthetic_context": serialize_synthetic_context(self.synthetic_context),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._digest_payload()
        payload["specification_digest"] = self.specification_digest
        return payload

    def validate(self) -> None:
        if self.schema_version != RENDER_PREFLIGHT_SCHEMA_VERSION:
            raise_mega15_error(
                "RENDER_PREFLIGHT_SCHEMA_MISMATCH",
                f"Unsupported schema_version: {self.schema_version!r}",
            )
        if self.kind != RENDER_PREFLIGHT_KIND:
            raise_mega15_error(
                "RENDER_PREFLIGHT_KIND_MISMATCH",
                f"Unsupported kind: {self.kind!r}",
            )
        ensure_non_empty_str(self.specification_id, "specification_id")
        ensure_non_empty_str(self.catalog_id, "catalog_id")
        ensure_non_empty_str(self.queue_digest, "queue_digest")
        ensure_non_empty_str(self.preparation_packet_id, "preparation_packet_id")
        ensure_non_empty_str(self.preparation_packet_digest, "preparation_packet_digest")
        ensure_non_empty_str(
            self.mega15_lineage_receipt_id, "mega15_lineage_receipt_id"
        )
        ensure_non_empty_str(
            self.mega15_lineage_receipt_digest, "mega15_lineage_receipt_digest"
        )
        validate_synthetic_context(self.synthetic_context)

        if self.render_execution_state != "PREFLIGHT_ONLY_NOT_EXECUTED":
            raise_mega15_error(
                REFUSAL_RENDER_EXECUTION_FORBIDDEN,
                f"render_execution_state must be 'PREFLIGHT_ONLY_NOT_EXECUTED', got {self.render_execution_state!r}",
            )
        if self.preview_eligible is not False:
            raise_mega15_error(
                REFUSAL_RENDER_EXECUTION_FORBIDDEN,
                "preview_eligible must remain False in offline synthetic preflight",
            )
        if self.production_export_authorized is not False:
            raise_mega15_error(
                REFUSAL_PREVIEW_AS_PRODUCTION_FORBIDDEN,
                "production_export_authorized must remain False",
            )
        if (
            self.ffmpeg_invocation_permitted is not False
            or self.media_write_permitted is not False
        ):
            raise_mega15_error(
                REFUSAL_FFMPEG_INVOCATION_FORBIDDEN,
                "ffmpeg_invocation_permitted and media_write_permitted must remain False",
            )
        if self.expected_non_production_marker != PREVIEW_NON_PRODUCTION_MARKER:
            raise_mega15_error(
                REFUSAL_PREVIEW_AS_PRODUCTION_FORBIDDEN,
                f"expected_non_production_marker must be {PREVIEW_NON_PRODUCTION_MARKER!r}",
            )
        expected_req_fields = tuple(sorted(REAL_PREVIEW_RECEIPT_REQUIRED_FIELDS))
        if self.gate3_render_receipt_required_fields != expected_req_fields:
            raise_mega15_error(
                "RENDER_PREFLIGHT_RECEIPT_FIELDS_MISMATCH",
                "gate3_render_receipt_required_fields does not match vip_fvs.real_preview_receipt._REQUIRED_FIELDS",
            )
        if not self.windows:
            raise_mega15_error(
                "RENDER_PREFLIGHT_EMPTY_WINDOWS",
                "windows must be non-empty",
            )
        for win in self.windows:
            validate_video_stream_namespace(win.stream_id)
            if win.render_execution_state != "PREFLIGHT_ONLY_NOT_EXECUTED":
                raise_mega15_error(
                    REFUSAL_RENDER_EXECUTION_FORBIDDEN,
                    f"Window {win.window_id} invalid state: {win.render_execution_state!r}",
                )
            if win.media_output_path is not None:
                raise_mega15_error(
                    REFUSAL_RENDER_OUTPUT_PATH_FORBIDDEN,
                    "Window media_output_path must be None",
                )
            if win.resolved_end_pts <= win.resolved_start_pts:
                raise_mega15_error(
                    "RENDER_PREFLIGHT_INVALID_WINDOW_INTERVAL",
                    f"Window {win.window_id} interval must be positive",
                )

        expected_digest = canonical_sha256(self._digest_payload())
        if self.specification_digest != expected_digest:
            raise_mega15_error(
                "RENDER_PREFLIGHT_DIGEST_MISMATCH",
                f"specification_digest mismatch: expected {expected_digest}, got {self.specification_digest}",
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "RenderPreflightSpecification":
        if not isinstance(payload, Mapping):
            raise_mega15_error(
                "RENDER_PREFLIGHT_INVALID_PAYLOAD",
                "Payload must be a mapping",
            )
        raw_ctx = payload.get("synthetic_context")
        if not isinstance(raw_ctx, Mapping):
            raise_mega15_error(
                "RENDER_PREFLIGHT_INVALID_SYNTHETIC_CONTEXT",
                "synthetic_context must be a mapping",
            )
        raw_windows = payload.get("windows")
        raw_fields = payload.get("gate3_render_receipt_required_fields")
        if not isinstance(raw_windows, Sequence) or not isinstance(
            raw_fields, Sequence
        ):
            raise_mega15_error(
                "RENDER_PREFLIGHT_INVALID_LISTS",
                "windows and required_fields must be sequences",
            )
        spec = cls(
            schema_version=str(payload.get("schema_version", "")),
            kind=str(payload.get("kind", "")),
            specification_id=str(payload.get("specification_id", "")),
            catalog_id=str(payload.get("catalog_id", payload.get("queue_id", ""))),
            queue_digest=str(payload.get("queue_digest", "")),
            preparation_packet_id=str(payload.get("preparation_packet_id", "")),
            preparation_packet_digest=str(payload.get("preparation_packet_digest", "")),
            mega15_lineage_receipt_id=str(
                payload.get("mega15_lineage_receipt_id", "")
            ),
            mega15_lineage_receipt_digest=str(
                payload.get("mega15_lineage_receipt_digest", "")
            ),
            windows=tuple(
                RenderWindowSpecification.from_dict(item) for item in raw_windows
            ),
            gate3_render_receipt_required_fields=tuple(str(f) for f in raw_fields),
            gate3_render_receipt_schema_version=str(
                payload.get("gate3_render_receipt_schema_version", "")
            ),
            expected_non_production_marker=str(
                payload.get("expected_non_production_marker", "")
            ),
            render_execution_state=str(payload.get("render_execution_state", "")),
            preview_eligible=bool(payload.get("preview_eligible", True)),
            production_export_authorized=bool(
                payload.get("production_export_authorized", True)
            ),
            ffmpeg_invocation_permitted=bool(
                payload.get("ffmpeg_invocation_permitted", True)
            ),
            media_write_permitted=bool(payload.get("media_write_permitted", True)),
            synthetic_context=parse_synthetic_context_dict(raw_ctx),
            specification_digest=str(payload.get("specification_digest", "")),
        )
        spec.validate()
        return spec


def build_render_preflight_specification(
    *,
    preparation_packet: Gate3OfflinePreparationPacket,
    lineage_receipt: Mega15LineageReceipt,
    specification_id: str = "rpreflight_default",
    execute_render: bool = False,
    ffmpeg_argv: Sequence[str] | None = None,
    media_output_path: str | None = None,
    treat_preview_as_production: bool = False,
) -> RenderPreflightSpecification:
    """Build a verified offline `RenderPreflightSpecification` from MEGA-15 artifacts."""
    refuse_render_or_ffmpeg_execution(
        execute_render=execute_render,
        ffmpeg_argv=ffmpeg_argv,
        media_output_path=media_output_path,
        treat_preview_as_production=treat_preview_as_production,
    )
    verify_gate3_offline_preparation_packet(preparation_packet)
    verify_mega15_lineage_receipt(lineage_receipt)

    if (
        lineage_receipt.preparation_packet_id != preparation_packet.packet_id
        or lineage_receipt.preparation_packet_digest != preparation_packet.packet_digest
        or lineage_receipt.catalog_id != preparation_packet.catalog_id
        or lineage_receipt.queue_digest != preparation_packet.queue_digest
    ):
        raise_mega15_error(
            REFUSAL_MEGA15_LINEAGE_BROKEN,
            "Mega15LineageReceipt does not match Gate3OfflinePreparationPacket identity/digest",
        )

    windows: list[RenderWindowSpecification] = []
    for rec, env in zip(
        preparation_packet.temporal_records, preparation_packet.handoff_envelopes
    ):
        windows.append(
            RenderWindowSpecification(
                window_id=f"rwin_{rec.queue_item_id}",
                queue_item_id=rec.queue_item_id,
                revision_id=rec.revision_id,
                content_id=rec.content_id,
                source_path=rec.source_path,
                source_sha256=rec.source_sha256,
                stream_id=rec.stream_id,
                timebase_num=rec.timebase_num,
                timebase_den=rec.timebase_den,
                resolved_start_pts=rec.resolved_start_pts,
                resolved_end_pts=rec.resolved_end_pts,
                subdivided_segments=rec.subdivided_segments,
                temporal_record_id=rec.record_id,
                temporal_record_digest=rec.record_digest,
                handoff_envelope_id=env.envelope_id,
                handoff_envelope_digest=env.envelope_digest,
                render_execution_state="PREFLIGHT_ONLY_NOT_EXECUTED",
                media_output_path=None,
            )
        )

    syn_ctx = make_synthetic_context()
    provisional = RenderPreflightSpecification(
        schema_version=RENDER_PREFLIGHT_SCHEMA_VERSION,
        kind=RENDER_PREFLIGHT_KIND,
        specification_id=specification_id,
        catalog_id=preparation_packet.catalog_id,
        queue_digest=preparation_packet.queue_digest,
        preparation_packet_id=preparation_packet.packet_id,
        preparation_packet_digest=preparation_packet.packet_digest,
        mega15_lineage_receipt_id=lineage_receipt.receipt_id,
        mega15_lineage_receipt_digest=lineage_receipt.receipt_digest,
        windows=tuple(windows),
        gate3_render_receipt_required_fields=tuple(
            sorted(REAL_PREVIEW_RECEIPT_REQUIRED_FIELDS)
        ),
        gate3_render_receipt_schema_version=RECEIPT_SCHEMA_VERSION,
        expected_non_production_marker=PREVIEW_NON_PRODUCTION_MARKER,
        render_execution_state="PREFLIGHT_ONLY_NOT_EXECUTED",
        preview_eligible=False,
        production_export_authorized=False,
        ffmpeg_invocation_permitted=False,
        media_write_permitted=False,
        synthetic_context=syn_ctx,
        specification_digest="",
    )
    digest = canonical_sha256(provisional._digest_payload())
    final_spec = RenderPreflightSpecification(
        **{**provisional.__dict__, "specification_digest": digest}
    )
    final_spec.validate()
    return final_spec


def verify_render_preflight_specification(
    spec: RenderPreflightSpecification | Mapping[str, Any],
) -> RenderPreflightSpecification:
    """Verify and return a `RenderPreflightSpecification`."""
    if isinstance(spec, RenderPreflightSpecification):
        spec.validate()
        return spec
    return RenderPreflightSpecification.from_dict(spec)
