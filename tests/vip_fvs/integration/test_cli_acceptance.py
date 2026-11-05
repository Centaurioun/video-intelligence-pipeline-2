"""Subprocess acceptance checks for the developer-facing FVS CLI."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.vip_fvs.fixtures.materialize import materialize_fixture


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("recipe", ["cfr_4s_shape", "vfr_nonuniform"])
def test_cli_run_emits_success_summary_and_artifacts(recipe: str, tmp_path: Path) -> None:
    """The installed-in-place CLI completes each bounded synthetic recipe.

    Running a fresh Python process is important here: it verifies that the
    package's normal module entry point wires the coordinator, rather than
    relying on test-process imports or an already configured service seam.
    """

    source = materialize_fixture(recipe, tmp_path)
    index_root = tmp_path / "index"
    run_dir = tmp_path / "run"
    before_source = source.read_bytes()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        ["src", "experiments", "."]
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "vip_fvs.cli",
            "run",
            "--source",
            str(source),
            "--query",
            "target phrase",
            "--index-root",
            str(index_root),
            "--fake-embedder",
            "--scenario",
            recipe,
            "--run-dir",
            str(run_dir),
        ],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert completed.stderr == ""
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert len(lines) == 1
    summary = json.loads(lines[0])
    assert summary["all_checks_passed"] is True
    assert summary["export_eligible"] is False

    artifact_paths = summary["artifact_paths"]
    assert isinstance(artifact_paths, (list, dict))
    paths = artifact_paths.values() if isinstance(artifact_paths, dict) else artifact_paths
    for artifact in paths:
        artifact_path = Path(artifact)
        if not artifact_path.is_absolute():
            artifact_path = REPOSITORY_ROOT / artifact_path
        assert artifact_path.is_file(), artifact_path

    assert source.read_bytes() == before_source


def test_index_local_cli_rejects_snapshot_digest_drift_before_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A source change after scope authorization must fail before runtime open."""
    from types import SimpleNamespace

    from vip_fvs import cli, coordinator

    source = tmp_path / "generated-source.bin"
    original = b"authorized synthetic source"
    source.write_bytes(original)
    authorization = SimpleNamespace(
        source_sha256=hashlib.sha256(original).hexdigest(),
        authorization_id="synthetic-auth-1",
        source_revision_id="synthetic-revision-1",
    )

    def authorize_scope_then_mutate(*args, **kwargs) -> None:
        # Models a source changing after the no-content preliminary check.
        source.write_bytes(b"changed after authorization")

    monkeypatch.setattr(coordinator, "load_index_local_authorization", lambda _path: authorization)
    monkeypatch.setattr(coordinator, "require_index_local_authorization", authorize_scope_then_mutate)
    monkeypatch.setattr(cli, "_real_runtime", lambda _args: pytest.fail("runtime opened before snapshot verification"))
    args = SimpleNamespace(
        fake_embedder=False, model_profile_json=None,
        model_root=str(tmp_path / "model"), model_identity="synthetic-model",
        model_revision="synthetic-revision", weights_sha256="a" * 64,
        pilot_authorization=str(tmp_path / "authorization.json"),
        output_root=str(tmp_path / "output"), source=str(source),
        index_root=str(tmp_path / "index"), device="cpu",
        source_snapshot_root=str(tmp_path / "snapshot-store"),
        max_source_bytes=1024, max_store_bytes=8192,
    )

    with pytest.raises(ValueError, match="SOURCE_DIGEST_MISMATCH"):
        cli._product_runtime(args, index_operation=True)


def test_index_local_cli_rejects_invalid_synthetic_preflight_before_runtime_or_source_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    from vip_fvs import cli

    source = tmp_path / "controlled-source.bin"
    source.write_bytes(b"controlled bytes")
    attestation = tmp_path / "attestation.json"
    attestation.write_text("{}", encoding="utf-8")
    binding = tmp_path / "binding.json"
    binding.write_text(json.dumps({"revision_id": "candidate", "source_sha256": "a" * 64,
                                   "authorization": {}, "locator": str(source.resolve())}), encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def guarded_read_bytes(path: Path) -> bytes:
        if path == source:
            pytest.fail("controlled source was read before P1 metadata validation")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)
    monkeypatch.setattr(cli, "_product_runtime", lambda *a, **k: pytest.fail("runtime opened before P1 validation"))
    result = cli.main(["index-local", "--source", str(source), "--index-root", str(tmp_path / "index"),
                       "--fake-embedder", "--synthetic-attestation", str(attestation),
                       "--synthetic-binding", str(binding)])
    assert result == 1
    assert "CORPUS_SEPARATION_" in capsys.readouterr().out
    assert not (tmp_path / "index").exists()


def test_run_cli_rejects_invalid_synthetic_preflight_before_service_or_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    from vip_fvs import coordinator, cli

    source = tmp_path / "controlled-source.bin"
    source.write_bytes(b"controlled bytes")
    attestation = tmp_path / "attestation.json"
    attestation.write_text("{}", encoding="utf-8")
    binding = tmp_path / "binding.json"
    binding.write_text(json.dumps({"revision_id": "candidate", "source_sha256": "a" * 64,
                                   "authorization": {}, "locator": str(source.resolve())}), encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def guarded_read_bytes(path: Path) -> bytes:
        if path == source:
            pytest.fail("controlled source was read before P1 metadata validation")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)
    monkeypatch.setattr(coordinator, "run_vertical_slice", lambda *a, **k: pytest.fail("service reached before P1 validation"))
    run_dir = tmp_path / "run"
    result = cli.main(["run", "--source", str(source), "--query", "target", "--index-root", str(tmp_path / "index"),
                       "--fake-embedder", "--run-dir", str(run_dir),
                       "--synthetic-attestation", str(attestation), "--synthetic-binding", str(binding)])
    assert result == 1
    assert "CORPUS_SEPARATION_" in capsys.readouterr().out
    assert not run_dir.exists()


def test_prepare_real_cli_rejects_invalid_synthetic_preflight_before_real_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    from vip_fvs import cli

    source = tmp_path / "controlled-source.bin"
    source.write_bytes(b"controlled bytes")
    attestation = tmp_path / "attestation.json"
    attestation.write_text("{}", encoding="utf-8")
    binding = tmp_path / "binding.json"
    binding.write_text(json.dumps({"revision_id": "candidate", "source_sha256": "a" * 64,
                                   "authorization": {}, "locator": str(source.resolve())}), encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def guarded_read_bytes(path: Path) -> bytes:
        if path == source:
            pytest.fail("controlled source was read before P1 metadata validation")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)
    monkeypatch.setattr(cli, "_prepare_real", lambda *a, **k: pytest.fail("real dispatch reached before P1 validation"))
    output_root = tmp_path / "out"
    argv = ["prepare-real", "--source", str(source), "--query", "target", "--index-root", str(tmp_path / "index"),
            "--output-root", str(output_root), "--run-dir", str(tmp_path / "run"),
            "--source-revision-id", "candidate", "--attempt-id", "attempt", "--pilot-authorization", "auth",
            "--model-root", "model", "--model-identity", "model", "--model-revision", "revision",
            "--weights-sha256", "a" * 64, "--probe-executable", "ffprobe",
            "--source-snapshot-root", str(tmp_path / "snapshots"), "--max-source-bytes", "1000",
            "--max-store-bytes", "10000", "--synthetic-attestation", str(attestation),
            "--synthetic-binding", str(binding)]
    result = cli.main(argv)
    assert result == 1
    assert "CORPUS_SEPARATION_" in capsys.readouterr().out
    assert not output_root.exists()


@pytest.mark.parametrize("unbounded", [False, True])
def test_prepare_real_cli_scopes_unbounded_probe_to_explicit_local_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unbounded: bool,
) -> None:
    from types import SimpleNamespace
    from vip_fvs import cli
    from vip_fvs.real_source_probe import DEFAULT_PROBE_TIMEOUT_SECONDS

    authorization = SimpleNamespace(
        source_sha256="a" * 64, authorization_id="authorization-test",
        source_revision_id="revision-test", selected_stream_index=0,
    )
    snapshot = SimpleNamespace(
        snapshot_path=tmp_path / "snapshot.mp4", sha256="a" * 64,
        source_locator=str((tmp_path / "source.mp4").absolute()),
        authorization_id="authorization-test", source_revision_id="revision-test",
    )
    runtime = SimpleNamespace(semantic_space=SimpleNamespace(
        model_identity="model", frozen_revision="revision", weights_sha256="b" * 64,
    ))
    monkeypatch.setattr("vip_fvs.pilot_authorization.load_pilot_authorization", lambda _path: authorization)
    monkeypatch.setattr("vip_fvs.pilot_authorization.require_prepare_authorization", lambda *a, **k: None)
    store_calls = []
    monkeypatch.setattr("vip_fvs.source_snapshot.SourceSnapshotStore", lambda *a, **kwargs: SimpleNamespace(
        capture=lambda *a, **k: store_calls.append("capture"),
        load_verified_snapshot=lambda snapshot_id: store_calls.append(("load", snapshot_id)) or snapshot,
    ))
    monkeypatch.setattr(cli, "_real_runtime", lambda _args: runtime)
    monkeypatch.setattr("persistent_local_index.model_space.semantic_space_id", lambda _space: "space-test")

    class CapturedRequest(Exception):
        pass

    observed = {}

    def capture_request(request):
        observed["request"] = request
        raise CapturedRequest

    monkeypatch.setattr(cli, "prepare_real_source", capture_request)
    args = cli._parser().parse_args([
        "prepare-real", "--source", str(tmp_path / "source.mp4"), "--query", "query",
        "--index-root", str(tmp_path / "index"), "--output-root", str(tmp_path / "out"),
        "--run-dir", str(tmp_path / "run"), "--source-revision-id", "revision-test",
        "--attempt-id", "attempt-test", "--pilot-authorization", str(tmp_path / "auth.json"),
        "--model-root", str(tmp_path / "model"), "--model-identity", "model",
        "--model-revision", "revision", "--weights-sha256", "b" * 64,
        "--probe-executable", "/usr/bin/ffprobe", "--source-snapshot-root", str(tmp_path / "snapshots"),
        "--preverified-snapshot-id", "1" * 32,
        "--max-source-bytes", "1000000", "--max-store-bytes", "2000000",
        *( ["--allow-unbounded-local-pilot"] if unbounded else [] ),
    ])
    with pytest.raises(CapturedRequest):
        cli._prepare_real(args)
    assert observed["request"].probe_timeout_seconds == (
        None if unbounded else DEFAULT_PROBE_TIMEOUT_SECONDS
    )
    assert observed["request"].preverified_snapshot is snapshot
    assert store_calls == [("load", "1" * 32)]


def test_unbounded_local_pilot_requires_reused_snapshot_id(tmp_path: Path) -> None:
    from vip_fvs import cli

    args = cli._parser().parse_args([
        "prepare-real", "--source", str(tmp_path / "source.mp4"), "--query", "query",
        "--index-root", str(tmp_path / "index"), "--output-root", str(tmp_path / "out"),
        "--run-dir", str(tmp_path / "run"), "--source-revision-id", "revision-test",
        "--attempt-id", "attempt-test", "--pilot-authorization", str(tmp_path / "auth.json"),
        "--model-root", str(tmp_path / "model"), "--model-identity", "model",
        "--model-revision", "revision", "--weights-sha256", "b" * 64,
        "--probe-executable", "/usr/bin/ffprobe", "--source-snapshot-root", str(tmp_path / "snapshots"),
        "--max-source-bytes", "1000000", "--max-store-bytes", "2000000",
        "--allow-unbounded-local-pilot",
    ])
    with pytest.raises(SystemExit, match="UNBOUNDED_LOCAL_PILOT_REQUIRES_PREVERIFIED_SNAPSHOT_ID"):
        cli._prepare_real(args)


def test_unbounded_local_pilot_help_requires_manual_cancellation_without_outer_timeout() -> None:
    import argparse
    from vip_fvs import cli

    parser = cli._parser()
    subparsers = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    help_text = " ".join(subparsers.choices["prepare-real"].format_help().split())
    assert "interactive foreground terminal" in help_text
    assert "without an enclosing timeout" in help_text
    assert "Ctrl-C" in help_text


def test_checked_synthetic_attestation_cannot_admit_real_index_cli_before_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    import sys
    unit_dir = str(Path(__file__).resolve().parents[1] / "unit")
    sys.path.insert(0, unit_dir)
    try:
        from test_corpus_admission import _valid_synthetic_attestation
        attestation_record, authorization = _valid_synthetic_attestation()
    finally:
        sys.path.remove(unit_dir)
    from vip_fvs import cli

    source = tmp_path / "controlled-source.bin"
    source.write_bytes(b"controlled bytes")
    attestation = tmp_path / "attestation.json"
    attestation.write_text(json.dumps(attestation_record), encoding="utf-8")
    binding = tmp_path / "binding.json"
    binding.write_text(json.dumps({"revision_id": "candidate-c", "source_sha256": "d" * 64,
                                   "authorization": authorization, "locator": str(source.resolve())}),
                      encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def guarded_read_bytes(path: Path) -> bytes:
        if path == source:
            pytest.fail("real branch read source despite synthetic-only preflight")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)
    monkeypatch.setattr(cli, "_product_runtime", lambda *a, **k: pytest.fail("real runtime opened"))
    result = cli.main(["index-local", "--source", str(source), "--index-root", str(tmp_path / "index"),
                       "--model-root", "model", "--model-identity", "model", "--model-revision", "r1",
                       "--weights-sha256", "a" * 64, "--pilot-authorization", "authorization",
                       "--output-root", str(tmp_path / "out"), "--source-snapshot-root", str(tmp_path / "snapshots"),
                       "--max-source-bytes", "1000", "--max-store-bytes", "10000",
                       "--synthetic-attestation", str(attestation), "--synthetic-binding", str(binding)])
    assert result == 1
    assert "CORPUS_SEPARATION_REAL_ADMISSION_FORBIDDEN" in capsys.readouterr().out
    assert not (tmp_path / "out").exists()


def test_preview_real_cli_forwards_plan_bound_synthetic_context_before_adapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import sys
    from types import SimpleNamespace
    unit_dir = str(Path(__file__).resolve().parents[1] / "unit")
    sys.path.insert(0, unit_dir)
    try:
        from test_corpus_admission import _valid_synthetic_attestation
        attestation_record, authorization_record = _valid_synthetic_attestation()
    finally:
        sys.path.remove(unit_dir)
    from vip_fvs import cli, real_plan

    source = tmp_path / "source.mp4"
    plan_path = tmp_path / "plan.json"
    auth_path = tmp_path / "preview-auth.json"
    output_root = tmp_path / "preview-out"
    attestation_path = tmp_path / "attestation.json"
    binding_path = tmp_path / "binding.json"
    attestation_path.write_text(json.dumps(attestation_record), encoding="utf-8")
    binding_path.write_text(json.dumps({"revision_id": "candidate-c", "source_sha256": "d" * 64,
                                        "authorization": authorization_record, "locator": str(source.resolve())}),
                            encoding="utf-8")
    args = cli._parser().parse_args(["preview-real", "--plan", str(plan_path), "--authorization", str(auth_path),
        "--source", str(source), "--output-root", str(output_root), "--ffprobe", "ffprobe", "--ffmpeg", "ffmpeg",
        "--run-id", "run", "--attempt-id", "attempt", "--synthetic-attestation", str(attestation_path),
        "--synthetic-binding", str(binding_path)])
    plan = SimpleNamespace(plan_scope="REAL", digest="c" * 64)
    artifacts = SimpleNamespace(plan=plan)
    preview_authorization = SimpleNamespace(source_revision_id="candidate-c", source_sha256="d" * 64,
                                            output_root=output_root.resolve(), record_digest="e" * 64,
                                            compute_digest=lambda: "e" * 64)
    monkeypatch.setattr(real_plan, "load_real_plan", lambda _path: artifacts)
    monkeypatch.setattr(cli, "_load_preview_authorization", lambda _path, output_root: preview_authorization)
    context, bindings = cli._load_cli_synthetic_preflight(args)
    assert context is not None
    assert context.operation == "local_preview.render_preview"
    assert context.plan_digest == plan.digest

    seen: dict[str, object] = {}

    class Adapter:
        def render_preview(self, _artifacts, **kwargs):
            seen.update(kwargs)
            raise RuntimeError("adapter dispatch observed")

    monkeypatch.setattr("vip_fvs.local_preview.LocalPreviewAdapter", Adapter)
    from vip_fvs.corpus_admission import CorpusAdmissionError
    preview_authorization.record_digest = "f" * 64
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        cli._preview_real(args, synthetic_preflight=context, admission_bindings=bindings)
    assert seen == {}
    preview_authorization.record_digest = "e" * 64
    with pytest.raises(RuntimeError, match="adapter dispatch observed"):
        cli._preview_real(args, synthetic_preflight=context, admission_bindings=bindings)
    assert seen["synthetic_opt_in"] is True
    assert seen["synthetic_preflight"] is context
    assert seen["synthetic_binding"] == bindings[0]


@pytest.mark.parametrize(
    ("stub_summary", "expected_rc"),
    [
        (
            {
                "operation": "index-local",
                "generation_id": "gen-1",
                "space_id": "space-1",
                "indexed": 1,
                "skipped": 0,
                "reused": 0,
                "failed": 0,
            },
            0,
        ),
        (
            {
                "operation": "index-local",
                "generation_id": "gen-1",
                "space_id": "space-1",
                "indexed": 0,
                "skipped": 1,
                "reused": 0,
                "failed": 0,
            },
            0,
        ),
        (
            {
                "operation": "index-local",
                "generation_id": "gen-1",
                "space_id": "space-1",
                "indexed": 0,
                "skipped": 0,
                "reused": 1,
                "failed": 0,
            },
            0,
        ),
        (
            {
                "operation": "index-local",
                "generation_id": "gen-1",
                "space_id": "space-1",
                "indexed": 0,
                "skipped": 0,
                "reused": 0,
                "failed": 1,
            },
            1,
        ),
        (
            {
                "operation": "index-local",
                "generation_id": "gen-1",
                "space_id": "space-1",
                "indexed": 2,
                "skipped": 1,
                "reused": 1,
                "failed": 1,
            },
            1,
        ),
        (
            {
                "operation": "index-local",
                "generation_id": "gen-1",
                "space_id": "space-1",
                "indexed": 0,
                "skipped": 0,
                "reused": 0,
                "failed": 0,
            },
            1,
        ),
        (
            {
                "operation": "index-local",
                "generation_id": "gen-1",
                "space_id": "space-1",
                "indexed": 1,
            },
            1,
        ),
    ],
)
def test_index_local_cli_exit_code_reflects_disposition_and_failure_counts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stub_summary: dict[str, object],
    expected_rc: int,
) -> None:
    from vip_fvs import cli, coordinator

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic source")
    monkeypatch.setattr(
        coordinator,
        "index_local_source",
        lambda *args, **kwargs: dict(stub_summary),
    )

    rc = cli.main(
        [
            "index-local",
            "--source",
            str(source),
            "--index-root",
            str(tmp_path / "index"),
            "--fake-embedder",
        ]
    )
    assert rc == expected_rc
    out_lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(out_lines) == 1
    parsed = json.loads(out_lines[0])
    assert parsed["runtime_mode"] == "fake"
    assert parsed["generation_id"] == "gen-1"


def test_index_local_cli_upstream_exception_refusal_returns_nonzero_with_single_json_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from vip_fvs import cli, coordinator

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic source")

    def fail_upstream(*args, **kwargs):
        raise ValueError("MISSING_STREAM_INDEX")

    monkeypatch.setattr(coordinator, "index_local_source", fail_upstream)
    rc = cli.main(
        [
            "index-local",
            "--source",
            str(source),
            "--index-root",
            str(tmp_path / "index"),
            "--fake-embedder",
        ]
    )
    assert rc != 0
    out_lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(out_lines) == 1
    parsed = json.loads(out_lines[0])
    assert parsed["all_checks_passed"] is False
    assert "MISSING_STREAM_INDEX" in parsed["error"]

