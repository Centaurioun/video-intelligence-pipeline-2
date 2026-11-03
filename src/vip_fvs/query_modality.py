"""Typed, provider-neutral query modality envelope.

Reference modalities are declared extension seams only. This module carries
opaque provenance references; it never loads, decodes, uploads, or embeds media.
"""
from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


class QueryModality(str, Enum):
    TEXT = "TEXT"
    IMAGE_REFERENCE = "IMAGE_REFERENCE"
    VIDEO_REFERENCE = "VIDEO_REFERENCE"


class CapabilityLevel(str, Enum):
    DECLARED = "DECLARED"
    EXECUTABLE = "EXECUTABLE"


class ModalityAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    NOT_OBSERVED = "NOT_OBSERVED"


@dataclass(frozen=True)
class CoarseReferenceInterval:
    """Non-binding interval on a referenced query asset, never source PTS."""

    start_seconds: float
    end_seconds: float
    timebase: str = "seconds"

    def __post_init__(self) -> None:
        if (isinstance(self.start_seconds, bool) or isinstance(self.end_seconds, bool)
                or not isinstance(self.start_seconds, (int, float))
                or not isinstance(self.end_seconds, (int, float))
                or not math.isfinite(self.start_seconds) or not math.isfinite(self.end_seconds)
                or self.start_seconds < 0 or self.end_seconds <= self.start_seconds):
            raise ValueError("INVALID_COARSE_REFERENCE_INTERVAL")
        if self.timebase != "seconds":
            raise ValueError("UNSUPPORTED_REFERENCE_INTERVAL_TIMEBASE")
        object.__setattr__(self, "start_seconds", float(self.start_seconds))
        object.__setattr__(self, "end_seconds", float(self.end_seconds))


@dataclass(frozen=True)
class ReferenceQuery:
    """Opaque reference plus required provenance; contains no media payload."""

    reference_id: str
    provenance_ref: str
    source_revision_ref: str
    interval: CoarseReferenceInterval | None = None

    def __post_init__(self) -> None:
        _require_identifier(self.reference_id, "REFERENCE_ID_REQUIRED")
        if _looks_like_path(self.reference_id):
            raise ValueError("REFERENCE_ID_MUST_NOT_BE_PATH")
        _require_identifier(self.provenance_ref, "PROVENANCE_REF_REQUIRED")
        _require_identifier(self.source_revision_ref, "SOURCE_REVISION_REF_REQUIRED")
        if self.interval is not None and not isinstance(self.interval, CoarseReferenceInterval):
            raise TypeError("interval must be CoarseReferenceInterval")


@dataclass(frozen=True)
class QueryEnvelope:
    """Closed query shape with modality capability separated from availability."""

    modality: QueryModality
    text: str | None = None
    reference: ReferenceQuery | None = None
    capability: CapabilityLevel | None = None
    availability: ModalityAvailability | None = None

    def __post_init__(self) -> None:
        try:
            modality = self.modality if isinstance(self.modality, QueryModality) else QueryModality(self.modality)
        except (ValueError, TypeError) as exc:
            raise ValueError("UNSUPPORTED_QUERY_MODALITY") from exc
        object.__setattr__(self, "modality", modality)
        if self.capability is not None and not isinstance(self.capability, CapabilityLevel):
            try:
                object.__setattr__(self, "capability", CapabilityLevel(self.capability))
            except (ValueError, TypeError) as exc:
                raise ValueError("INVALID_CAPABILITY_LEVEL") from exc
        if self.availability is not None and not isinstance(self.availability, ModalityAvailability):
            try:
                object.__setattr__(self, "availability", ModalityAvailability(self.availability))
            except (ValueError, TypeError) as exc:
                raise ValueError("INVALID_MODALITY_AVAILABILITY") from exc
        if self.capability is None:
            object.__setattr__(self, "capability", CapabilityLevel.EXECUTABLE if modality is QueryModality.TEXT else CapabilityLevel.DECLARED)
        if self.availability is None:
            object.__setattr__(self, "availability", ModalityAvailability.AVAILABLE if modality is QueryModality.TEXT else ModalityAvailability.NOT_AVAILABLE)

        if modality is QueryModality.TEXT:
            if self.reference is not None or not isinstance(self.text, str) or not self.text.strip():
                raise ValueError("TEXT_QUERY_REQUIRED")
            normalized = " ".join(self.text.split())
            object.__setattr__(self, "text", normalized)
            if self.capability is not CapabilityLevel.EXECUTABLE or self.availability is not ModalityAvailability.AVAILABLE:
                raise ValueError("TEXT_QUERY_NOT_EXECUTABLE")
        else:
            if self.text is not None or not isinstance(self.reference, ReferenceQuery):
                raise ValueError("REFERENCE_QUERY_REQUIRED")
            if self.capability is not CapabilityLevel.DECLARED or self.availability is not ModalityAvailability.NOT_AVAILABLE:
                raise ValueError("REFERENCE_MODALITY_NOT_EXECUTABLE")

    @classmethod
    def from_text(cls, text: str) -> "QueryEnvelope":
        return cls(modality=QueryModality.TEXT, text=text)

    @classmethod
    def from_reference(
        cls, modality: QueryModality, reference: ReferenceQuery
    ) -> "QueryEnvelope":
        return cls(modality=modality, reference=reference)

    @property
    def executable(self) -> bool:
        return self.capability is CapabilityLevel.EXECUTABLE and self.availability is ModalityAvailability.AVAILABLE

    def to_dict(self) -> dict[str, Any]:
        reference = None
        if self.reference is not None:
            reference = {
                "reference_id": self.reference.reference_id,
                "provenance_ref": self.reference.provenance_ref,
                "source_revision_ref": self.reference.source_revision_ref,
                "interval": None if self.reference.interval is None else {
                    "start_seconds": self.reference.interval.start_seconds,
                    "end_seconds": self.reference.interval.end_seconds,
                    "timebase": self.reference.interval.timebase,
                },
            }
        return {
            "modality": self.modality.value,
            "text": self.text,
            "reference": reference,
            "capability": self.capability.value,
            "availability": self.availability.value,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "QueryEnvelope":
        if not isinstance(value, Mapping):
            raise TypeError("query envelope must be a mapping")
        allowed = {"modality", "text", "reference", "capability", "availability"}
        if set(value) - allowed:
            raise ValueError("UNKNOWN_QUERY_ENVELOPE_FIELDS")
        ref_value = value.get("reference")
        reference = None
        if ref_value is not None:
            if not isinstance(ref_value, Mapping):
                raise TypeError("reference must be a mapping")
            allowed_ref = {"reference_id", "provenance_ref", "source_revision_ref", "interval"}
            if set(ref_value) - allowed_ref:
                raise ValueError("UNKNOWN_REFERENCE_QUERY_FIELDS")
            interval_value = ref_value.get("interval")
            interval = None
            if interval_value is not None:
                if not isinstance(interval_value, Mapping) or set(interval_value) - {"start_seconds", "end_seconds", "timebase"}:
                    raise ValueError("INVALID_COARSE_REFERENCE_INTERVAL")
                interval = CoarseReferenceInterval(**interval_value)
            reference = ReferenceQuery(
                reference_id=ref_value.get("reference_id"),
                provenance_ref=ref_value.get("provenance_ref"),
                source_revision_ref=ref_value.get("source_revision_ref"),
                interval=interval,
            )
        return cls(
            modality=value.get("modality"),
            text=value.get("text"),
            reference=reference,
            capability=value.get("capability"),
            availability=value.get("availability"),
        )


def _require_identifier(value: object, error: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(error)


def _looks_like_path(value: str) -> bool:
    # Identifiers are opaque tokens; path/URI locators and OS path objects are
    # deliberately not accepted as identity shortcuts.
    return (isinstance(value, os.PathLike) or value.startswith(("/", "\\", "file:"))
            or re.match(r"^[A-Za-z]:", value) is not None
            or "/" in value or "\\" in value or bool(Path(value).drive))


__all__ = [
    "CapabilityLevel",
    "CoarseReferenceInterval",
    "ModalityAvailability",
    "QueryEnvelope",
    "QueryModality",
    "ReferenceQuery",
]
