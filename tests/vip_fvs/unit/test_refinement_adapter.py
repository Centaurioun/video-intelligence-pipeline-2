from __future__ import annotations

import hashlib
import sys
import types

import pytest

from vip_fvs.refinement_adapter import RefinementRefusal, refine_retrieval_candidate


def _fake_gate3(monkeypatch, *, binding=True):
    container = types.ModuleType("gate3.container")
    container.parse_iso_bmff_timing = lambda path, selected_stream_index=None: {
        "media_timescale": 1000, "pts_ticks": (0, 779, 2048, 3072),
        "stream_index": selected_stream_index,
    }
    ingress = types.ModuleType("gate3.ingress")
    ingress.validate_candidate = lambda raw, **kwargs: {
        "disposition": "ADMITTED", "reason_codes": [], "downgrades": [],
        "record": {**raw, "binding_eligible": False},
    }
    pts = types.ModuleType("gate3.pts")
    class PtsTable:
        def __init__(self, time_base, ticks):
            self.time_base, self.ticks = time_base, ticks
        def is_boundary_member(self, tick):
            return tick in self.ticks
    pts.PtsTable = PtsTable
    rational = types.ModuleType("gate3.rational")
    class TimeBase:
        def __init__(self, num, den): self.num, self.den = num, den
    rational.TimeBase = TimeBase
    refinement = types.ModuleType("gate3.refinement")
    calls = {}
    def refine(table, requested, **kwargs):
        calls["table"], calls["requested"], calls["kwargs"] = table, requested, kwargs
        return {"evidence_class": "MEASURED", "time_domain": "source_pts",
                "start_ticks": requested[0], "end_ticks": requested[1]}
    refinement.refine = refine
    refinement.is_binding_eligible = lambda record: binding
    gate3 = types.ModuleType("gate3")
    for name, module in (("container", container), ("ingress", ingress),
                         ("pts", pts), ("rational", rational), ("refinement", refinement)):
        setattr(gate3, name, module)
        monkeypatch.setitem(sys.modules, "gate3." + name, module)
    monkeypatch.setitem(sys.modules, "gate3", gate3)
    return calls


def _hit(path, digest):
    return {"source_path": str(path), "source_sha256": digest, "pts": 779,
            "timebase_num": 1, "timebase_den": 1000, "rank": 1, "score": .9}


def test_semantic_hit_stays_non_binding_and_preserves_integer_pts(tmp_path, monkeypatch):
    calls = _fake_gate3(monkeypatch)
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic-source")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    result = refine_retrieval_candidate(
        _hit(source, digest), source_revision_id="rev-local-1",
        requested_pts=(779, 2048), stream_index=0, attempt_id="a-1",
    )
    assert result.candidate["binding_eligible"] is False
    assert result.measured_refinement["evidence_class"] == "MEASURED"
    assert result.binding_eligible is True
    assert result.source_digest_before == result.source_digest_after == digest
    assert calls["requested"] == (779, 2048)
    assert calls["kwargs"]["time_domain"] == "source_pts"
    assert calls["kwargs"]["precision"] == "source-pts"


def test_replaced_or_mutated_source_is_refused(tmp_path, monkeypatch):
    _fake_gate3(monkeypatch)
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original")
    with pytest.raises(RefinementRefusal, match="digest"):
        refine_retrieval_candidate(
            _hit(source, "0" * 64), source_revision_id="rev-local-1",
            requested_pts=(779, 2048),
        )


def test_nonuniform_pts_are_used_verbatim_never_nominal_fps(tmp_path, monkeypatch):
    calls = _fake_gate3(monkeypatch)
    source = tmp_path / "source.mp4"
    source.write_bytes(b"vfr")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    refine_retrieval_candidate(
        _hit(source, digest), source_revision_id="rev-vfr",
        requested_pts=(779, 2048), declared_rate=25,
    )
    assert calls["table"].ticks == (0, 779, 2048, 3072)
    assert calls["requested"] != (19, 51)
