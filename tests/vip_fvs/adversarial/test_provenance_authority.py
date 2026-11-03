"""Adversarial checks for source identity and byte authority at the FVS boundary.

These tests deliberately exercise the trust boundary with stale locators,
forged digests, and source changes during measurement.  A logical revision ID
is an opaque handle; it must never be accepted as a substitute for the bytes'
SHA-256 digest.
"""
from __future__ import annotations

import hashlib
import sys
import types

import pytest

from gate0.policy import PolicyDecision
from vip_fvs.refinement_adapter import RefinementRefusal, refine_retrieval_candidate
from vip_fvs.source_adapter import inventory_source


def _policy(revision: str = "rev-synthetic") -> PolicyDecision:
    return PolicyDecision(
        policy_decision_id="policy-fvs-adversarial",
        revision_scope=(revision,),
        purpose="DISCOVER",
        sensitivity_consent="SYNTHETIC",
        allowed_artifact_types=("source_manifest", "discovery_authorization"),
        provider_model_boundary="local_only",
        retention_class="SOURCE_REFERENCE",
        expires_at="2099-01-01T00:00:00Z",
        revocation_ref=None,
        egress_manifest_digest="a" * 64,
        decision="ALLOW",
        effective_at_use=True,
    )


def _fake_gate3(monkeypatch, source, *, mutate_during_measurement=False):
    container = types.ModuleType("gate3.container")

    def parse(path, selected_stream_index=None):
        if mutate_during_measurement:
            source.write_bytes(b"mutated while being measured")
        return {"media_timescale": 1000, "pts_ticks": (0, 779, 2048)}

    container.parse_iso_bmff_timing = parse
    ingress = types.ModuleType("gate3.ingress")
    ingress.validate_candidate = lambda raw, **kwargs: {
        "disposition": "ADMITTED", "reason_codes": [], "record": {**raw, "binding_eligible": False}
    }
    pts = types.ModuleType("gate3.pts")
    pts.PtsTable = type("PtsTable", (), {"__init__": lambda self, time_base, ticks: setattr(self, "ticks", ticks)})
    rational = types.ModuleType("gate3.rational")
    rational.TimeBase = type("TimeBase", (), {"__init__": lambda self, num, den: None})
    refinement = types.ModuleType("gate3.refinement")
    refinement.refine = lambda table, requested, **kwargs: {"evidence_class": "MEASURED", "time_domain": "source_pts"}
    refinement.is_binding_eligible = lambda record: True
    gate3 = types.ModuleType("gate3")
    for name, module in (("container", container), ("ingress", ingress), ("pts", pts), ("rational", rational), ("refinement", refinement)):
        setattr(gate3, name, module)
        monkeypatch.setitem(sys.modules, "gate3." + name, module)
    monkeypatch.setitem(sys.modules, "gate3", gate3)


def _hit(path, digest):
    return {"source_path": str(path), "source_sha256": digest, "pts": 779}


def test_replaced_path_cannot_reuse_an_old_inventory_digest(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original revision")
    binding = inventory_source(source, tmp_path / "run", _policy())
    source.write_bytes(b"replacement revision")
    _fake_gate3(monkeypatch, source)

    with pytest.raises(RefinementRefusal, match="digest"):
        refine_retrieval_candidate(
            _hit(source, binding.source_sha256),
            source_revision_id=binding.revision_id,
            requested_pts=(779, 2048),
        )


def test_forged_digest_is_not_authority_for_a_source_path(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"actual bytes")
    _fake_gate3(monkeypatch, source)

    with pytest.raises(RefinementRefusal, match="digest"):
        refine_retrieval_candidate(
            _hit(source, "0" * 64), source_revision_id="rev-synthetic", requested_pts=(779, 2048)
        )


def test_source_mutation_during_measurement_is_refused(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"stable until parser starts")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    _fake_gate3(monkeypatch, source, mutate_during_measurement=True)

    with pytest.raises(RefinementRefusal, match="changed during refinement"):
        refine_retrieval_candidate(
            _hit(source, digest), source_revision_id="rev-synthetic", requested_pts=(779, 2048)
        )


def test_logical_revision_and_content_digest_are_distinct_authority_fields(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"same bytes")
    binding = inventory_source(source, tmp_path / "run", _policy())
    record = binding.inventory.source_records[0]["payload"]

    assert binding.revision_id != binding.source_sha256
    assert record["revision_id"] == binding.revision_id
    assert record["content_digest"] == binding.source_sha256
    assert len(binding.source_sha256) == 64
    assert binding.revision_id not in {binding.source_sha256, record["content_digest"]}


def test_digest_shaped_revision_id_is_rejected_instead_of_becoming_logical_identity(tmp_path):
    """A byte digest must not be silently accepted as a logical revision handle."""
    source = tmp_path / "source.mp4"
    source.write_bytes(b"revision identity probe")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()

    with pytest.raises(ValueError, match="revision"):
        inventory_source(source, tmp_path / "run", _policy(digest), revision_id=digest)
