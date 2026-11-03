"""End-to-end `preview-fixture` lifecycle over generated synthetic media.

The source is produced by the real local FFmpeg from a lavfi testsrc; a
provenance sidecar declares it synthetic. No model, provider, network, archive
media, production render or export is involved.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from vip_fvs.cli import main
import vip_fvs.real_preview_receipt as receipts

FFMPEG = Path("/opt/homebrew/bin/ffmpeg")
FFPROBE = Path("/opt/homebrew/bin/ffprobe")
pytestmark = pytest.mark.skipif(
    not (FFMPEG.is_file() and FFPROBE.is_file()),
    reason="real ffmpeg/ffprobe binaries are required",
)

SOURCE_SHA = ""
SOURCE_PTS = (0, 40, 80, 120, 160)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _generate_source(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(FFMPEG), "-v", "error", "-y",
            "-f", "lavfi", "-i", "testsrc=size=160x90:rate=25",
            "-frames:v", "5", "-c:v", "mpeg4", "-g", "5", "-pix_fmt", "yuv420p",
            "-video_track_timescale", "1000", str(path),
        ],
        check=True, capture_output=True,
    )
    return path


def _provenance(source: Path, *, source_kind: str = "synthetic", sha: str | None = None,
                generator: str = "local-lavfi-testsrc", raw: bytes | None = None) -> Path:
    sidecar = source.parent / "provenance.json"
    if raw is not None:
        sidecar.write_bytes(raw)
        return sidecar
    sidecar.write_bytes(_canonical({
        "source_kind": source_kind,
        "sha256": sha if sha is not None else _sha(source),
        "generator": generator,
    }) + b"\n")
    return sidecar


def _args(source: Path, provenance: Path, output_root: Path, *extra: str) -> list[str]:
    return [
        "preview-fixture", "--source", str(source), "--provenance", str(provenance),
        "--output-root", str(output_root),
        "--ffprobe-executable", str(FFPROBE), "--ffmpeg-executable", str(FFMPEG),
        "--run-id", "fixture-run-1", "--attempt-id", "attempt-fixture-1",
        *extra,
    ]


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    root = tmp_path_factory.mktemp("fixture-media")
    source = _generate_source(root / "source.mp4")
    global SOURCE_SHA
    SOURCE_SHA = _sha(source)
    return source


def test_preview_fixture_end_to_end_pass(generated, tmp_path, capsys):
    source = generated
    provenance = _provenance(source)
    out = tmp_path / "out"
    code = main(_args(source, provenance, out))
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    assert code == 0, summary
    assert summary["status"] == "PASS"
    assert summary["plan_scope"] == "SYNTHETIC_FIXTURE"
    assert summary["principal_kind"] == "SYNTHETIC_HUMAN"
    assert summary["fixture_scope"] == "SYNTHETIC_FIXTURE"
    assert summary["production_eligible"] is False
    assert summary["export_eligible"] is False
    assert summary["verifier_status"] == "PASS"
    assert summary["technical_qc_status"] == "PASS"

    plan_path = out / "plan.json"
    authorization_path = out / "authorization.json"
    verifier_path = out / "verifier.json"
    qc_path = out / "technical-qc.json"
    receipt_path = out / "preview-receipt.json"
    for path in (plan_path, authorization_path, verifier_path, qc_path, receipt_path):
        assert path.is_file(), path
    previews = list(out.glob("*.preview.mp4"))
    assert len(previews) == 1, previews

    plan_record = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan_record["plan"]["plan_scope"] == "SYNTHETIC_FIXTURE"
    assert plan_record["plan"]["real_authority_eligible"] is False
    assert plan_record["plan"]["export_eligible"] is False
    assert plan_record["plan"]["pinned_decisions"][next(iter(plan_record["plan"]["pinned_decisions"]))]["principal_kind"] == "SYNTHETIC_HUMAN"

    authorization = json.loads(authorization_path.read_text(encoding="utf-8"))["authorization"]
    assert authorization["scope"] == "NON_PRODUCTION_PREVIEW"
    assert authorization["production_eligible"] is False
    assert authorization["export_eligible"] is False
    assert authorization["review_bundle_record_digest"] == ""
    assert authorization["human_decision_digest"] == ""

    preview = previews[0]
    probe = subprocess.run(
        [str(FFPROBE), "-v", "error", "-of", "json", "-show_streams", "-show_format", str(preview)],
        check=True, capture_output=True,
    )
    measured = json.loads(probe.stdout)
    streams = [s for s in measured["streams"] if s.get("codec_type") == "video"]
    assert len(streams) == 1
    assert streams[0]["time_base"] == "1/1000"
    assert int(streams[0]["duration_ts"]) == 40

    verifier = json.loads(verifier_path.read_text(encoding="utf-8"))
    qc = json.loads(qc_path.read_text(encoding="utf-8"))
    assert verifier["status"] == "PASS"
    assert verifier["attempt_id"] == "attempt-fixture-1"
    assert verifier["independent_of_producer"] is True
    assert verifier["checks"]
    assert qc["status"] == "PASS"
    assert qc["attempt_id"] == "attempt-fixture-1"
    assert qc["evidence_class"] == "MEASURED"
    assert qc["production_eligible"] is False
    assert qc["export_eligible"] is False

    receipt = receipts.load_fixture_preview_receipt(receipt_path, authorized_output_root=out)
    assert receipt.record["scope"] == receipts.FIXTURE_SCOPE
    assert receipt.record["status"] == "SUCCEEDED"
    assert receipt.record["production_eligible"] is False
    assert receipt.record["export_eligible"] is False
    assert receipt.record["source"]["source_sha256"] == SOURCE_SHA
    assert receipt.record["verifier"]["status"] == "PASS"
    assert receipt.record["technical_qc"]["status"] == "PASS"
    required = {"human editorial authority", "visual editorial suitability", "audio observation",
                "production render capability", "provider/cloud inference"}
    assert required.issubset(set(receipt.record["NOT_OBSERVED"]))
    assert receipt.record["lifecycle"]["principal_kind"] == "SYNTHETIC_HUMAN"
    assert receipt.record["lifecycle"]["plan_scope"] == "SYNTHETIC_FIXTURE"

    with pytest.raises(ValueError):
        receipts.load_real_preview_receipt(receipt_path, authorized_output_root=out)

    assert _sha(source) == SOURCE_SHA
    assert source.resolve() not in previews


def test_preview_fixture_refuses_second_run_output_overwrite(generated, tmp_path, capsys):
    source = generated
    provenance = _provenance(source)
    out = tmp_path / "out"
    assert main(_args(source, provenance, out)) == 0
    capsys.readouterr()

    code = main(_args(source, provenance, out))
    output = capsys.readouterr().out
    assert code == 1
    assert "OUTPUT_EXISTS" in output


def test_preview_fixture_refuses_missing_provenance(generated, tmp_path, capsys):
    source = generated
    provenance = source.parent / "no-such-provenance.json"
    code = main(_args(source, provenance, tmp_path / "out"))
    assert code == 1
    assert "FIXTURE_PROVENANCE_REQUIRED" in capsys.readouterr().out


def test_preview_fixture_refuses_malformed_provenance(generated, tmp_path, capsys):
    source = generated
    provenance = _provenance(source, raw=b"{not-json")
    code = main(_args(source, provenance, tmp_path / "out"))
    assert code == 1
    assert "FIXTURE_PROVENANCE_REQUIRED" in capsys.readouterr().out


def test_preview_fixture_refuses_sha_mismatch(generated, tmp_path, capsys):
    source = generated
    provenance = _provenance(source, sha="0" * 64)
    code = main(_args(source, provenance, tmp_path / "out"))
    assert code == 1
    assert "FIXTURE_PROVENANCE_MISMATCH" in capsys.readouterr().out


def test_preview_fixture_refuses_non_synthetic_provenance(generated, tmp_path, capsys):
    source = generated
    provenance = _provenance(source, source_kind="authentic")
    code = main(_args(source, provenance, tmp_path / "out"))
    assert code == 1
    assert "FIXTURE_PROVENANCE_MISMATCH" in capsys.readouterr().out


def test_preview_fixture_refuses_real_mode_inputs(generated, tmp_path, capsys):
    source = generated
    provenance = _provenance(source)
    code = main(_args(source, provenance, tmp_path / "out", "--model-root", str(tmp_path / "model")))
    assert code == 1
    assert "FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS" in capsys.readouterr().out


def test_preview_fixture_refuses_non_video_source(generated, tmp_path, capsys):
    source = generated.parent / "garbage.mp4"
    source.write_bytes(b"this is not a video container")
    provenance = _provenance(source)
    code = main(_args(source, provenance, tmp_path / "out"))
    assert code == 1
    output = capsys.readouterr().out
    assert "all_checks_passed" in output
    # The generated bytes must never reach a render; the probe refuses first.
    assert not list((tmp_path / "out").glob("*.preview.mp4")) if (tmp_path / "out").is_dir() else True
