"""Closed-schema contract tests for ``schemas/gate0/runtime_and_failure_ledger.json`` (D5).

Authority: ``docs/implementation-spec-v1.1.md`` §5:242-244 ("An attempted call
records destination, protocol, attempted bytes, decision, tool/attempt,
timestamp, and outcome as EGRESS_BLOCKED, with no payload and zero bytes"),
§9.2 event matrix, §6:38; ``contract-owner-proposal.md`` D5.  A vacuous
EGRESS_BLOCKED event and unknown failure/egress vocabulary must refuse.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from gate0.contracts.types import ARTIFACT_TYPES

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "schemas/gate0/runtime_and_failure_ledger.json").read_text(encoding="utf-8"))
D = "0" * 64


def _validator(subschema: dict) -> Draft202012Validator:
    root = {"$defs": SCHEMA["$defs"]}
    root.update(subschema)
    return Draft202012Validator(root)


def _event(**overrides: object) -> dict:
    event = {
        "event_id": "egress_sentinel_dns",
        "event_type": "EGRESS_BLOCKED",
        "attempt_id": "attempt_preflight",
        "affected_refs": [],
        "reason": "child network denied",
        "occurred_at": "2026-01-01T00:00:00Z",
        "policy_decision_id": "policy_a",
        "tool_identity": "child-network-sentinel",
        "destination": "dns://sentinel.invalid",
        "protocol": "DNS",
        "attempted_bytes": 1,
        "transmitted_bytes": 0,
        "payload": None,
        "decision": "DENY",
        "outcome": "BLOCKED",
    }
    event.update(overrides)
    return event


def _failure_event(**overrides: object) -> dict:
    event = {
        "event_id": "failure_stage",
        "event_type": "FAILURE",
        "attempt_id": "attempt_rank",
        "affected_refs": ["artifact_ranked"],
        "reason": "REPRESENTATION_VECTOR_MISSING",
        "occurred_at": "2026-01-01T00:00:00Z",
    }
    event.update(overrides)
    return event


def _assert_invalid(value: dict) -> None:
    with pytest.raises(ValidationError):
        _validator({"$ref": "#/$defs/event"}).validate(value)


def test_egress_blocked_requires_decision_and_outcome() -> None:
    properties = SCHEMA["$defs"]["event"]["properties"]
    assert properties["decision"]["enum"] == ["ALLOW", "DENY"]
    assert properties["outcome"]["enum"] == ["BLOCKED", "TRANSMITTED", "FAILED"]
    conditional = next(item for item in SCHEMA["$defs"]["event"]["allOf"] if "if" in item)
    assert conditional["if"]["properties"]["event_type"]["const"] == "EGRESS_BLOCKED"
    assert {"decision", "outcome"} <= set(conditional["then"]["required"])
    _validator({"$ref": "#/$defs/event"}).validate(_event())
    for key in ("decision", "outcome"):
        missing = _event()
        missing.pop(key)
        _assert_invalid(missing)
    _assert_invalid(_event(decision="MAYBE"))
    _assert_invalid(_event(outcome="SENT"))


def test_egress_blocked_keeps_zero_byte_sentinel_evidence() -> None:
    _assert_invalid(_event(transmitted_bytes=1))
    _assert_invalid(_event(payload={"bytes": 0}))
    for key in ("policy_decision_id", "tool_identity", "destination", "protocol", "attempted_bytes"):
        missing = _event()
        missing.pop(key)
        _assert_invalid(missing)
    _assert_invalid(_event(protocol="SMTP"))


def test_non_egress_events_do_not_require_egress_fields() -> None:
    _validator({"$ref": "#/$defs/event"}).validate(_failure_event())
    _validator({"$ref": "#/$defs/event"}).validate(_failure_event(decision="ALLOW"))
    _assert_invalid(_failure_event(event_type="EGRESS_ALLOWED"))
    _assert_invalid(_failure_event(event_type="FAILURE", decision="MAYBE"))


def test_artifact_type_ref_uses_the_registered_artifact_enum() -> None:
    ref = SCHEMA["$defs"]["ref"]
    assert tuple(ref["properties"]["artifact_type"]["enum"]) == ARTIFACT_TYPES
    for name in ARTIFACT_TYPES:
        _validator({"$ref": "#/$defs/ref"}).validate({
            "artifact_id": "artifact_a", "payload_digest": D, "artifact_type": name,
        })
    with pytest.raises(ValidationError):
        _validator({"$ref": "#/$defs/ref"}).validate({
            "artifact_id": "artifact_a", "payload_digest": D, "artifact_type": "summary.md",
        })


def test_egress_event_can_carry_a_registered_payload_ref() -> None:
    _validator({"$ref": "#/$defs/event"}).validate(_event(
        payload_ref={"artifact_id": "artifact_ledger", "payload_digest": D,
                     "artifact_type": "runtime_and_failure_ledger.json"},
    ))
    _assert_invalid(_event(payload_ref={"artifact_id": "artifact_ledger", "payload_digest": D,
                                        "artifact_type": "ledger"}))
