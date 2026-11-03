"""Adversarial temporal-authority checks for the FVS refinement boundary.

These tests deliberately feed locator metadata that disagrees with measured
source timing.  A semantic hit, nominal frame rate, or caller-selected stream
must never become a source-native cut authority by arithmetic or implication.
"""
from __future__ import annotations

import hashlib
import sys
import types

import pytest

from vip_fvs.refinement_adapter import RefinementRefusal, refine_retrieval_candidate


def _install_gate3(monkeypatch, *, measured, binding=True, parser_digest=None):
    """Install a small seam that records the adapter's authority inputs."""
    calls = {}
    container = types.ModuleType("gate3.container")

    def parse(path, selected_stream_index=None):
        calls["selected_stream_index"] = selected_stream_index
        result = dict(measured)
        result.setdefault(
            "source_bytes_sha256",
            hashlib.sha256(path.read_bytes()).hexdigest() if parser_digest is None else parser_digest,
        )
        return result

    container.parse_iso_bmff_timing = parse
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
        def __init__(self, num, den):
            self.num, self.den = num, den

    rational.TimeBase = TimeBase
    refinement = types.ModuleType("gate3.refinement")

    def refine(table, requested, **kwargs):
        calls["table"] = table
        calls["requested"] = requested
        calls["kwargs"] = kwargs
        # Model the production authority result: a stream mismatch cannot bind.
        eligible = binding and kwargs.get("stream_index") == measured.get("stream_index")
        return {
            "evidence_class": "MEASURED", "time_domain": "source_pts",
            "start_ticks": requested[0], "end_ticks": requested[1],
            "binding_eligible": eligible,
        }

    refinement.refine = refine
    refinement.is_binding_eligible = lambda record: bool(record["binding_eligible"])
    gate3 = types.ModuleType("gate3")
    for name, module in (("container", container), ("ingress", ingress),
                         ("pts", pts), ("rational", rational),
                         ("refinement", refinement)):
        setattr(gate3, name, module)
        monkeypatch.setitem(sys.modules, "gate3." + name, module)
    monkeypatch.setitem(sys.modules, "gate3", gate3)
    return calls


def _hit(path, digest, *, pts=40, timebase=(1, 1000)):
    return {
        "source_path": str(path), "source_sha256": digest, "pts": pts,
        "timebase_num": timebase[0], "timebase_den": timebase[1],
        "rank": 1, "score": 0.9,
    }


def _source(tmp_path):
    source = tmp_path / "source.synthetic"
    source.write_bytes(b"synthetic-source")
    return source, hashlib.sha256(source.read_bytes()).hexdigest()


def test_candidate_revision_mismatch_cannot_be_relabelled(tmp_path, monkeypatch):
    source, digest = _source(tmp_path)
    calls = _install_gate3(
        monkeypatch,
        measured={"media_timescale": 1000, "pts_ticks": (0, 40, 80), "stream_index": 0},
    )
    hit = {**_hit(source, digest), "source_revision_id": "rev-other"}

    with pytest.raises(RefinementRefusal, match="revision"):
        refine_retrieval_candidate(
            hit, source_revision_id="rev-request", requested_pts=(40, 80),
        )
    assert "requested" not in calls


def test_parser_measured_byte_digest_must_match_request(tmp_path, monkeypatch):
    source, digest = _source(tmp_path)
    calls = _install_gate3(
        monkeypatch,
        measured={"media_timescale": 1000, "pts_ticks": (0, 40, 80), "stream_index": 0},
        parser_digest="0" * 64,
    )

    with pytest.raises(RefinementRefusal, match="measured source digest"):
        refine_retrieval_candidate(
            _hit(source, digest), source_revision_id="rev-digest", requested_pts=(40, 80),
        )
    assert "requested" not in calls


def test_nominal_fps_cannot_rewrite_nonuniform_source_pts(tmp_path, monkeypatch):
    source, digest = _source(tmp_path)
    calls = _install_gate3(
        monkeypatch,
        measured={"media_timescale": 1000, "pts_ticks": (0, 40, 80, 160, 280),
                  "stream_index": 0},
    )

    refine_retrieval_candidate(
        _hit(source, digest, pts=160, timebase=(1, 1000)),
        source_revision_id="rev-vfr", requested_pts=(80, 280), declared_rate=25,
    )

    assert calls["table"].ticks == (0, 40, 80, 160, 280)
    assert calls["requested"] == (80, 280)
    assert calls["requested"] != (3_200, 11_200)  # 25-fps arithmetic in source ticks


def test_declared_locator_timebase_mismatch_refuses(tmp_path, monkeypatch):
    source, digest = _source(tmp_path)
    calls = _install_gate3(
        monkeypatch,
        measured={"media_timescale": 90_000, "pts_ticks": (0, 3_600, 9_000),
                  "stream_index": 0},
    )

    with pytest.raises(RefinementRefusal, match="timebase"):
        refine_retrieval_candidate(
            _hit(source, digest, pts=1, timebase=(1, 25)),
            source_revision_id="rev-timebase", requested_pts=(3_600, 9_000),
        )
    assert "requested" not in calls


def test_selected_stream_is_forwarded_and_cross_stream_binding_fails_closed(
    tmp_path, monkeypatch,
):
    source, digest = _source(tmp_path)
    calls = _install_gate3(
        monkeypatch,
        measured={"media_timescale": 48_000, "pts_ticks": (0, 1_920, 4_800),
                  "stream_index": 0},
    )

    with pytest.raises(RefinementRefusal, match="stream"):
        refine_retrieval_candidate(
            _hit(source, digest, pts=1, timebase=(1, 1000)),
            source_revision_id="rev-stream", requested_pts=(1_920, 4_800),
            stream_index=1, selected_stream_index=1,
        )
    assert calls["selected_stream_index"] == 1
    assert calls.get("requested") is None


def test_semantic_locator_cannot_be_promoted_by_synthetic_exact_endpoints(
    tmp_path, monkeypatch,
):
    source, digest = _source(tmp_path)
    _install_gate3(
        monkeypatch,
        measured={"media_timescale": 1000, "pts_ticks": (0, 40, 80),
                  "stream_index": 0},
    )

    # The locator's semantic window is intentionally made to numerically match
    # source ticks.  Its ingress record must remain non-binding regardless.
    result = refine_retrieval_candidate(
        _hit(source, digest, pts=40), source_revision_id="rev-semantic",
        requested_pts=(40, 80),
    )
    assert result.candidate["time_domain"] == "semantic_seconds"
    assert result.candidate["precision"] == "semantic-window"
    assert result.candidate["binding_eligible"] is False


def test_non_integer_requested_timestamp_is_refused_before_refinement(
    tmp_path, monkeypatch,
):
    source, digest = _source(tmp_path)
    calls = _install_gate3(
        monkeypatch,
        measured={"media_timescale": 1000, "pts_ticks": (0, 40, 80),
                  "stream_index": 0},
    )

    with pytest.raises(RefinementRefusal, match="integer"):
        refine_retrieval_candidate(
            _hit(source, digest), source_revision_id="rev-type",
            requested_pts=(40, 80.0),
        )
    assert "requested" not in calls
