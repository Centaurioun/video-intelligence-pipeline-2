"""The explicit REAL CLI branches must remain disjoint from the synthetic FVS."""
from __future__ import annotations

from vip_fvs import cli


def test_real_cli_dispatch_does_not_enter_synthetic_or_gate3(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("REAL CLI crossed a synthetic/Gate-3 boundary")

    monkeypatch.setattr(cli, "_prepare_real", lambda args: {"status": "AWAITING_EDITORIAL_DECISION"})
    monkeypatch.setattr(cli, "_resume_real", lambda args: {"status": "REJECTED"})
    monkeypatch.setattr("vip_fvs.coordinator.SyntheticVerticalSliceServices", forbidden)
    monkeypatch.setattr("gate3.receipt.build_receipt", forbidden)
    monkeypatch.setattr("gate3.render_adapter.SyntheticRenderAdapter", forbidden)

    assert cli.main(["prepare-real", "--source", "s", "--query", "q", "--index-root", "i",
                     "--output-root", str(tmp_path), "--run-dir", "r", "--source-revision-id", "rev",
                     "--attempt-id", "a", "--pilot-authorization", "auth", "--model-root", "m",
                     "--model-identity", "model", "--model-revision", "v1", "--weights-sha256", "a" * 64,
                     "--probe-executable", "ffprobe",
                     "--source-snapshot-root", str(tmp_path / "snapshot-store"),
                     "--max-source-bytes", "1000000", "--max-store-bytes", "2000000"]) == 0
    assert cli.main(["resume-real", "--bundle", "b", "--decision", "d", "--output-root", str(tmp_path),
                     "--run-id", "r", "--attempt-id", "a"]) == 0
