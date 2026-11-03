"""Deny-by-default, append-only egress decision seam for Gate-0."""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from gate0.identity import opaque_id, validate_digest, validate_opaque_id


@dataclass(frozen=True)
class EgressRequestContext:
    run_id: str
    attempt_id: str
    policy_decision_id: str
    egress_manifest_digest: str
    tool_identity: str
    destination: str
    protocol: str
    attempted_bytes: int
    now: str

    def __post_init__(self) -> None:
        for value in (self.run_id, self.attempt_id, self.policy_decision_id):
            validate_opaque_id(value)
        validate_digest(self.egress_manifest_digest)
        if self.attempted_bytes < 0:
            raise ValueError("attempted_bytes must be non-negative")


@dataclass(frozen=True)
class EgressDecision:
    event_id: str
    attempt_id: str
    policy_decision_id: str
    tool_identity: str
    timestamp: str
    decision: str
    outcome: str
    destination: str
    protocol: str
    attempted_bytes: int
    transmitted_bytes: int
    payload: None = None

    def __post_init__(self) -> None:
        validate_opaque_id(self.event_id)
        validate_opaque_id(self.attempt_id)
        validate_opaque_id(self.policy_decision_id)
        if self.decision not in {"DENY", "ALLOW"}:
            raise ValueError("invalid egress decision")
        if self.outcome not in {"BLOCKED", "TRANSMITTED"}:
            raise ValueError("invalid egress outcome")
        if self.attempted_bytes < 0 or self.transmitted_bytes < 0:
            raise ValueError("byte counts must be non-negative")
        if self.decision == "DENY" and self.transmitted_bytes != 0:
            raise ValueError("denied egress must transmit zero bytes")
        if self.payload is not None:
            raise ValueError("egress payloads are never persisted")

    def to_dict(self) -> dict[str, object]:
        return {"event_id": self.event_id, "attempt_id": self.attempt_id,
                "policy_decision_id": self.policy_decision_id,
                "tool_identity": self.tool_identity, "timestamp": self.timestamp,
                "decision": self.decision, "outcome": self.outcome,
                "destination": self.destination, "protocol": self.protocol,
                "attempted_bytes": self.attempted_bytes,
                "transmitted_bytes": self.transmitted_bytes, "payload": None}


def _redact_destination(destination: str) -> str:
    try:
        parsed = urlsplit(destination)
        if parsed.username is not None or parsed.password is not None:
            host = parsed.hostname or "redacted"
            if parsed.port:
                host += f":{parsed.port}"
            return urlunsplit((parsed.scheme, host, parsed.path, parsed.query, parsed.fragment))
    except ValueError:
        return "[REDACTED_DESTINATION]"
    return destination


class EgressGuard:
    """A process/child boundary seam; no request is permitted by default."""

    def __init__(self) -> None:
        self._events: list[EgressDecision] = []

    @property
    def events(self) -> tuple[EgressDecision, ...]:
        return tuple(self._events)

    def request(self, context: EgressRequestContext) -> EgressDecision:
        event = EgressDecision(
            event_id=opaque_id("egress", {"attempt": context.attempt_id,
                                           "tool": context.tool_identity,
                                           "destination": _redact_destination(context.destination),
                                           "timestamp": context.now}),
            attempt_id=context.attempt_id,
            policy_decision_id=context.policy_decision_id,
            tool_identity=context.tool_identity,
            timestamp=context.now,
            decision="DENY",
            outcome="BLOCKED",
            destination=_redact_destination(context.destination),
            protocol=context.protocol,
            attempted_bytes=context.attempted_bytes,
            transmitted_bytes=0,
            payload=None,
        )
        self._events.append(event)
        return event

    def child_network_sentinel(self, run_id: str, attempt_id: str, policy_decision_id: str,
                               egress_manifest_digest: str, now: str) -> tuple[EgressDecision, ...]:
        """Exercise all forbidden child routes through the same typed seam."""
        probes = (("DNS", "dns://sentinel.invalid", 1),
                  ("HTTP_PROXY", "http://proxy.invalid", 1),
                  ("PROVIDER", "https://provider.invalid", 1),
                  ("LOOPBACK", "http://127.0.0.1", 1))
        return tuple(self.request(EgressRequestContext(run_id, attempt_id, policy_decision_id,
                         egress_manifest_digest, "child-network-sentinel", destination,
                         protocol, attempted, now)) for protocol, destination, attempted in probes)
