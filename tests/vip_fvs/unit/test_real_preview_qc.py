from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

from vip_fvs.local_preview import PreviewArtifact
from vip_fvs.real_preview_qc import TechnicalQC
from vip_fvs.real_preview_verifier import verify_preview


def _artifact(source: Path, output: Path) -> PreviewArtifact:
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    output_digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return PreviewArtifact(
        output, output.stat().st_size, output_digest, source_digest, source_digest,
        source.stat().st_size, source.stat().st_size, "rev-1", 0, 1, 1000, 10, 40,
        "p" * 64, "l" * 64, "m" * 64, "a" * 64, ("ffprobe",), ("ffmpeg",),
        {"sha256": "b" * 64}, {"sha256": "c" * 64}, False, False, "MEASURED", "producer-attempt",
    )


def _verification(tmp_path: Path):
    source, output = tmp_path / "source.mp4", tmp_path / "preview.mp4"
    source.write_bytes(b"source")
    output.write_bytes(b"preview")
    verified = verify_preview(
        _artifact(source, output),
        source_path=source,
        attempt_id="qc-attempt",
    )
    return replace(
        verified,
        measured_output_streams=1,
        measured_output_timebase="1/1000",
        measured_output_duration_ticks=30,
        expected_output_duration_ticks=30,
    )


def test_technical_qc_pass_is_measured_and_keeps_editorial_observations_absent(tmp_path: Path):
    report = TechnicalQC.evaluate(_verification(tmp_path))

    record = report.to_record()
    assert report.status == "PASS"
    assert record["evidence_class"] == "MEASURED"
    assert "EDITORIAL_INFERENCE" not in record["evidence_class"]
    assert "visual editorial suitability" in record["NOT_OBSERVED"]
    assert "audio observation" in record["NOT_OBSERVED"]
    assert all(check["evidence_class"] == "MEASURED" for check in record["checks"])


def test_technical_qc_blocks_unbound_expected_duration(tmp_path: Path):
    verification = replace(_verification(tmp_path), expected_output_duration_ticks=None)

    report = TechnicalQC.evaluate(verification)

    assert report.status == "BLOCKED"
    assert "EXPECTED_DURATION_NOT_BOUND" in report.reason_codes


def test_technical_qc_rejects_boolean_stream_count(tmp_path: Path):
    verification = replace(_verification(tmp_path), measured_output_streams=True)

    report = TechnicalQC.evaluate(verification)

    assert report.status == "BLOCKED"
    assert "OUTPUT_STREAM_NOT_OBSERVED" in report.reason_codes
