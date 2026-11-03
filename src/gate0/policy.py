"""Fail-closed policy decisions for the local Gate-0 discovery boundary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Mapping

from gate0.identity import validate_digest, validate_opaque_id

Purpose = Literal["DISCOVER", "HASH", "PROBE", "PROCESS", "CACHE_READ", "PROJECTION_READ"]
_PURPOSE = {"DISCOVER": "DISCOVER", "HASH": "DISCOVER", "PROBE": "DISCOVER", "PROCESS": "PROCESS", "CACHE_READ": "CACHE_READ", "PROJECTION_READ": "PROJECTION_READ"}


class PolicyDenied(PermissionError):
    """Raised whenever a policy use cannot be proven allowed."""


@dataclass(frozen=True)
class PolicyDecision:
    policy_decision_id: str
    revision_scope: tuple[str, ...]
    purpose: str
    sensitivity_consent: str
    allowed_artifact_types: tuple[str, ...]
    provider_model_boundary: str
    retention_class: str
    expires_at: str
    revocation_ref: str | None
    egress_manifest_digest: str
    decision: str
    effective_at_use: bool

    def __post_init__(self) -> None:
        validate_opaque_id(self.policy_decision_id)
        if not self.revision_scope or len(set(self.revision_scope)) != len(self.revision_scope):
            raise ValueError("revision scope must be non-empty and unique")
        if self.purpose not in {"DISCOVER", "PROCESS", "CACHE_READ", "PROJECTION_READ"}:
            raise ValueError("invalid policy purpose")
        validate_digest(self.egress_manifest_digest)
        if self.decision not in {"ALLOW", "DENY", "EXPIRED", "REVOKED"}:
            raise ValueError("invalid policy decision")
        datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))

    def to_dict(self) -> dict[str, object]:
        return {"policy_decision_id": self.policy_decision_id, "revision_scope": list(self.revision_scope), "purpose": self.purpose, "sensitivity_consent": self.sensitivity_consent, "allowed_artifact_types": list(self.allowed_artifact_types), "provider_model_boundary": self.provider_model_boundary, "retention_class": self.retention_class, "expires_at": self.expires_at, "revocation_ref": self.revocation_ref, "egress_manifest_digest": self.egress_manifest_digest, "decision": self.decision, "effective_at_use": self.effective_at_use}


@dataclass(frozen=True)
class PolicyUseContext:
    revision_id: str
    operation: Purpose
    purpose: Purpose
    artifact_type: str
    provider_model_boundary: str
    retention_class: str
    now: str
    expected_egress_manifest_digest: str
    discovery_decision: PolicyDecision | None
    processing_decision: PolicyDecision | None


def _expired(expires_at: str, now: str) -> bool:
    return datetime.fromisoformat(expires_at.replace("Z", "+00:00")) <= datetime.fromisoformat(now.replace("Z", "+00:00"))


def require_allow(context: PolicyUseContext | Mapping[str, object]) -> None:
    """Prove one use is authorized; every missing or mismatched fact denies."""
    if isinstance(context, Mapping):
        context = PolicyUseContext(**context)  # type: ignore[arg-type]
    if context.operation not in _PURPOSE or context.purpose not in _PURPOSE:
        raise PolicyDenied("invalid policy operation/purpose")
    expected = _PURPOSE[context.operation]
    if context.purpose != expected:
        raise PolicyDenied("operation purpose mismatch")
    decision = context.discovery_decision if expected == "DISCOVER" else context.processing_decision
    if decision is None:
        raise PolicyDenied("missing effective policy decision")
    if decision.purpose != expected or decision.decision != "ALLOW" or not decision.effective_at_use:
        raise PolicyDenied("policy is not effective ALLOW")
    if context.revision_id not in decision.revision_scope:
        raise PolicyDenied("revision outside policy scope")
    if context.artifact_type not in decision.allowed_artifact_types:
        raise PolicyDenied("artifact not allowed")
    if decision.provider_model_boundary != context.provider_model_boundary:
        raise PolicyDenied("provider boundary mismatch")
    if decision.retention_class != context.retention_class:
        raise PolicyDenied("retention class mismatch")
    if decision.egress_manifest_digest != context.expected_egress_manifest_digest:
        raise PolicyDenied("egress manifest mismatch")
    if decision.revocation_ref is not None:
        raise PolicyDenied("policy is revoked")
    if _expired(decision.expires_at, context.now):
        raise PolicyDenied("policy is expired")
