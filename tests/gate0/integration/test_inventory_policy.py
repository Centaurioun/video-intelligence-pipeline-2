from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

import pytest

from gate0.inventory import ProbeEvidence, SourceOccurrence, build_inventory
from gate0.policy import PolicyDecision, PolicyUseContext, PolicyDenied, require_allow
from gate0.stages.prepare import prepare


NOW = "2026-09-12T12:00:00Z"
EGRESS = "a" * 64


def decision(scope, *, decision="ALLOW", purpose="DISCOVER", expires="2026-09-13T00:00:00Z"):
    return PolicyDecision(
        policy_decision_id="policy_inventory",
        revision_scope=tuple(scope), purpose=purpose,
        sensitivity_consent="PUBLIC",
        allowed_artifact_types=("source_manifest", "discovery_authorization"),
        provider_model_boundary="local_only", retention_class="SOURCE_REFERENCE",
        expires_at=expires, revocation_ref=None, egress_manifest_digest=EGRESS,
        decision=decision, effective_at_use=True,
    )


def test_prepare_initializes_without_publishing_artifacts(tmp_path):
    result = prepare(run_id="run_demo", attempt_id="attempt_prepare", output_root=tmp_path, now=NOW)
    assert result.payload.initialized is True
    assert result.output_artifact_refs == ()
    assert list(tmp_path.iterdir()) == []


def test_inventory_is_deterministic_and_resolves_configured_stream_without_mutating_source(tmp_path):
    source = tmp_path / "clip.bin"
    source.write_bytes(b"synthetic media")
    before = source.read_bytes()
    occurrence = SourceOccurrence("occ_1", "rev_1", "content_1", source)
    probe = ProbeEvidence(
        ffprobe_json={"streams": [{"index": 0, "codec_type": "video"}, {"index": 1, "codec_type": "audio"}], "format": {"size": "15"}},
        time_base=(1, 25),
    )
    first = build_inventory((occurrence,), probe_by_revision={"rev_1": probe}, authorization=decision(("rev_1",)), selected_stream_index=0, now=NOW)
    second = build_inventory((occurrence,), probe_by_revision={"rev_1": probe}, authorization=decision(("rev_1",)), selected_stream_index=0, now=NOW)
    assert first.inventory_digest == second.inventory_digest
    assert first.revision_refs[0].selected_stream_index == 0
    assert first.revision_refs[0].selection_source == "config"
    assert first.source_records[0]["payload"]["stream_refs"] == [{"stream_index": 0, "stream_type": "video"}, {"stream_index": 1, "stream_type": "audio"}]
    assert first.source_records[0]["payload"]["source_status"] == "INCLUDED"
    assert first.source_records[0]["payload"]["custody"]["state"] == "PRESERVED"
    assert source.read_bytes() == before


@pytest.mark.parametrize("bad", [
    {"decision": "EXPIRED"},
    {"expires": "2026-09-11T00:00:00Z"},
    {"purpose": "PROCESS"},
])
def test_inventory_denies_invalid_discovery_authorization(tmp_path, bad):
    source = tmp_path / "clip.bin"
    source.write_bytes(b"x")
    auth = decision(("rev_1",), **bad)
    with pytest.raises(PolicyDenied):
        build_inventory((SourceOccurrence("occ_1", "rev_1", "content_1", source),), {"rev_1": ProbeEvidence({"streams": [{"index": 0, "codec_type": "video"}]}, (1, 25))}, auth, selected_stream_index=0, now=NOW)


def test_selected_stream_requires_unique_or_configured(tmp_path):
    source = tmp_path / "clip.bin"
    source.write_bytes(b"x")
    occurrence = SourceOccurrence("occ_1", "rev_1", "content_1", source)
    probe = ProbeEvidence({"streams": [{"index": 0, "codec_type": "video"}, {"index": 2, "codec_type": "video"}]}, (1, 25))
    with pytest.raises(ValueError, match="AMBIGUOUS_STREAM"):
        build_inventory((occurrence,), {"rev_1": probe}, decision(("rev_1",)), selected_stream_index=None, now=NOW)


def test_publication_is_all_or_nothing_and_rejects_non_discovery_policy(tmp_path):
    source = tmp_path / "clip.bin"
    source.write_bytes(b"x")
    occurrence = SourceOccurrence("occ_1", "rev_1", "content_1", source)
    probe = ProbeEvidence({"streams": [{"index": 0, "codec_type": "video"}]}, (1, 25))
    output = tmp_path / "run"
    with pytest.raises(PolicyDenied, match="discovery policy purpose"):
        from gate0.stages.inventory import inventory
        inventory(occurrences=(occurrence,), probe_by_revision={"rev_1": probe}, authorization=decision(("rev_1",), purpose="PROCESS"), output_root=output, selected_stream_index=0, now=NOW)
    assert not output.exists()


def test_publication_rolls_back_if_second_replace_fails(tmp_path, monkeypatch):
    source = tmp_path / "clip.bin"
    source.write_bytes(b"x")
    occurrence = SourceOccurrence("occ_1", "rev_1", "content_1", source)
    probe = ProbeEvidence({"streams": [{"index": 0, "codec_type": "video"}]}, (1, 25))
    output = tmp_path / "run"
    from gate0.stages import inventory as stage
    original = stage._replace
    calls = {"n": 0}

    def fail_second(source_path, target_path):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("injected replace failure")
        return original(source_path, target_path)

    monkeypatch.setattr(stage, "_replace", fail_second)
    with pytest.raises(OSError, match="injected replace failure"):
        stage.inventory(occurrences=(occurrence,), probe_by_revision={"rev_1": probe}, authorization=decision(("rev_1",)), output_root=output, selected_stream_index=0, now=NOW)
    assert not output.exists()


def test_require_allow_maps_hash_and_probe_to_discover_and_rejects_discover_for_process():
    discover = decision(("rev_1",))
    context = PolicyUseContext("rev_1", "HASH", "DISCOVER", "source_manifest", "local_only", "SOURCE_REFERENCE", NOW, EGRESS, discover, None)
    assert require_allow(context) is None
    process = PolicyUseContext("rev_1", "PROCESS", "PROCESS", "window_sample_manifest", "local_only", "DERIVED_REPLAYABLE", NOW, EGRESS, discover, None)
    with pytest.raises(PolicyDenied):
        require_allow(process)
