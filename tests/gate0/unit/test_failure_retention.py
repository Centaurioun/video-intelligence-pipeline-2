from __future__ import annotations

import pytest

from gate0.failure import (
    RETENTION_CLASSES,
    AttemptRecord,
    FailureEvent,
    Tombstone,
    invalidation_event,
    membership_digest,
    retention_transition,
)
from gate0.repeat import idempotency_key, can_retry


def test_unchanged_transient_retry_is_allowed_once_and_changed_digest_denied():
    first = AttemptRecord.create("run_1", "extract", "in_digest", "cfg", "tool", "targets", error_class="TRANSIENT_IO")
    retry = AttemptRecord.create("run_1", "extract", "in_digest", "cfg", "tool", "targets", retry_of=first.attempt_id, error_class="TRANSIENT_IO")
    assert can_retry(first, retry) is True
    assert can_retry(retry, AttemptRecord.create("run_1", "extract", "in_digest", "cfg", "tool", "targets", retry_of=retry.attempt_id, error_class="TRANSIENT_IO")) is False
    changed = AttemptRecord.create("run_1", "extract", "changed", "cfg", "tool", "targets", retry_of=first.attempt_id, error_class="TRANSIENT_IO")
    assert can_retry(first, changed) is False
    assert retry.attempt_id != first.attempt_id


def test_invalidation_membership_digest_is_closed_sorted_and_tombstone_is_private():
    event = invalidation_event("attempt_1", ["artifact_b", "artifact_a"], reason="POLICY_REVOKED", authority="owner", now="2026-01-01T00:00:00Z", trigger="revocation", quarantine_destination="quarantine/run_1")
    assert event.membership_digest == membership_digest(("artifact_a", "artifact_b"))
    assert event.trigger == "revocation"
    assert event.quarantine_destination == "quarantine/run_1"
    assert event.actor == "owner"
    assert event.idempotency_key
    tomb = Tombstone.create("artifact_a", "revision_1", ("parent_1",), digest="a" * 64, byte_count=12, reason="EXPIRED", policy_ref="policy_1", run_id="run_1", attempt_id="attempt_1", deleted_at="2026-01-01T00:00:00Z", rebuildability="rebuildable")
    assert tomb.searchable is False
    assert "locator" not in tomb.to_dict()
    with pytest.raises(ValueError):
            Tombstone.create("artifact_a", "revision_1", (), digest="a" * 64, byte_count=0, reason="x", policy_ref="policy_1", run_id="run_1", attempt_id="attempt_1", deleted_at="2026-01-01T00:00:00Z", rebuildability="rebuildable", raw_media=b"pixels")
    with pytest.raises(ValueError):
        Tombstone.create("artifact_a", "revision_1", (), digest="a" * 64, byte_count=0, reason="x", policy_ref="policy_1", run_id="run_1", attempt_id="attempt_1", deleted_at="2026-01-01T00:00:00Z", rebuildability="rebuildable", locator="/private/source.mp4")
    with pytest.raises(ValueError):
        Tombstone.create("artifact_a", "revision_1", (), digest="a" * 64, byte_count=0, reason="x", policy_ref="policy_1", run_id="run_1", attempt_id="attempt_1", deleted_at="2026-01-01T00:00:00Z", rebuildability="rebuildable", provenance_ref="/private/source.mp4")
    with pytest.raises(ValueError):
        Tombstone.create("artifact_a", "revision_1", (), digest="a" * 64, byte_count=0, reason="x", policy_ref="policy_1", run_id="run_1", attempt_id="attempt_1", deleted_at="2026-01-01T00:00:00Z", rebuildability="rebuildable", provenance_fields={"query_text": "secret question"})


def test_retention_has_exact_five_classes_and_expiry_preserves_audit_fields():
    assert RETENTION_CLASSES == ("SOURCE_REFERENCE", "DERIVED_REPLAYABLE", "DERIVED_RESTRICTED", "AUDIT_MINIMUM", "TOMBSTONE")
    assert retention_transition("AVAILABLE", "QUARANTINED") == "QUARANTINED"
    assert retention_transition("QUARANTINED", "CLEANUP_PENDING") == "CLEANUP_PENDING"
    with pytest.raises(ValueError):
        retention_transition("CLEANUP_PENDING", "AVAILABLE")
