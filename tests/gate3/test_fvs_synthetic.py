"""Deterministic local Gate-3 module executed by the FVS receipt path.

This is intentionally a small synthetic contract test.  It gives the persisted
receipt a real in-repository module inventory and a subprocess-derived execution
record without claiming a provider, model, or real-media run.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from gate3.container import parse_iso_bmff_timing
from gate3.fixturegen import build_mp4


def run_deterministic_probe() -> None:
    """Run the same deterministic probe without requiring pytest at runtime."""
    with tempfile.TemporaryDirectory(prefix="gate3-fvs-") as directory:
        path = Path(directory) / "fixture.mp4"
        path.write_bytes(build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12)))
        first = parse_iso_bmff_timing(path)
        second = parse_iso_bmff_timing(path)
        assert first == second
        assert tuple(first["pts_ticks"]) == (0, 13, 25, 38)
        assert first["duration_consistency"] == "MATCH"


def test_synthetic_container_timing_is_deterministic(tmp_path):
    path = tmp_path / "fixture.mp4"
    path.write_bytes(build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12)))
    first = parse_iso_bmff_timing(path)
    second = parse_iso_bmff_timing(path)
    assert first == second
    assert tuple(first["pts_ticks"]) == (0, 13, 25, 38)
    assert first["duration_consistency"] == "MATCH"


if __name__ == "__main__":
    run_deterministic_probe()
