"""D-1 Lane A / S1: authorized_local admission is refused before any I/O.

These tests pin the fail-closed ordering the D-1 decision requires:

* an ``authorized-corpus.json`` declaration is admitted as a *distinct* mode;
* the CLI refuses it with ``BLOCKED_PREREQUISITE`` / exit 20 **before** reading
  ``run_manifest.json``, the config, or dispatching a stage;
* the pre-existing synthetic/media paths are never used as a fallback, even when
  the declaration is malformed;
* ``execute_stage`` refuses again (defence in depth) before loading inputs;
* a generated-fixture manifest relabelled as ``authorized_local`` cannot become
  real evidence.

Every path that could touch a declared source, run a probe/decoder, load the
model adapter or open a socket is armed to raise.  No real media, model weight,
network call or Gate decision exists in this file.
"""
from __future__ import annotations

import io
import json
import os
import socket
import sys
from pathlib import Path

import pytest

from gate0 import execution
from gate0 import media_experiment
from gate0.cli import main

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "config/gate0/default.json"
RUN_ID = "run_d1_authorized_refusal"

AUTHORIZED_REASON = "AUTHORIZED_LOCAL_EXECUTION_NOT_AUTHORIZED"


def _valid_declaration() -> dict:
    """A complete, non-forged declaration shape (D-2/D-3 still unattested)."""
    return {
        "schema_version": media_experiment.AUTHORIZED_CORPUS_SCHEMA_VERSION,
        "corpus_kind": media_experiment.AUTHORIZED_CORPUS_KIND,
        "revisions": [
            {
                "revision_id": "rev_eval_alpha",
                "occurrence_id": "occ_eval_alpha",
                "content_id": "content_eval_alpha",
                "locator": "media/alpha.mp4",
                "relation_ids": [],
                "split": "EVALUATION",
                "window_count": 2,
                "selected_stream_index": 0,
                "declared_byte_count": None,
                "declared_content_sha256": None,
            },
            {
                "revision_id": "rev_eval_beta",
                "occurrence_id": "occ_eval_beta",
                "content_id": "content_eval_beta",
                "locator": "media/beta.mp4",
                "relation_ids": [],
                "split": "EVALUATION",
                "window_count": 2,
                "selected_stream_index": 0,
                "declared_byte_count": None,
                "declared_content_sha256": None,
            },
            {
                "revision_id": "rev_dev_probe",
                "occurrence_id": "occ_dev_probe",
                "content_id": "content_dev_probe",
                "locator": "media/probe.mp4",
                "relation_ids": [],
                "split": "DEVELOPMENT",
                "window_count": 1,
                "selected_stream_index": 0,
                "declared_byte_count": None,
                "declared_content_sha256": None,
            },
        ],
        "relations": [],
        "evaluation_revision_ids": ["rev_eval_alpha", "rev_eval_beta"],
        "development_revision_id": "rev_dev_probe",
        "provenance": {"declaration_authority": "gate0-owner"},
        "policy": {"local_only": True},
    }


def _make_input_root(tmp_path: Path, *, declaration: object = None, raw: bytes | None = None):
    """Build a disposable input root plus the sentinel "declared source" tree."""
    input_root = tmp_path / "inputs"
    sentinel = input_root / "media"
    sentinel.mkdir(parents=True)
    for name in ("alpha.mp4", "beta.mp4", "probe.mp4"):
        # Synthetic placeholder bytes, never real/protected media.
        (sentinel / name).write_bytes(b"synthetic-placeholder-not-real-media")
    if raw is not None:
        (input_root / media_experiment.AUTHORIZED_CORPUS_FILE).write_bytes(raw)
    elif declaration is not None:
        (input_root / media_experiment.AUTHORIZED_CORPUS_FILE).write_text(
            json.dumps(declaration), encoding="utf-8"
        )
    return input_root, sentinel


def _boom(label: str):
    def _raise(*_args, **_kwargs):
        raise AssertionError(f"forbidden call during authorized_local refusal: {label}")

    return _raise


def _install_source_guard(monkeypatch, sentinel: Path) -> None:
    """Raise if any declared-source path is opened/stat'ed/created by name."""
    prefix = str(sentinel) + os.sep
    replacements = {
        "stat": os.stat,
        "lstat": os.lstat,
        "open": os.open,
    }
    for name, real in replacements.items():
        def guarded(path, *args, __real=real, __prefix=prefix, __name=name, **kwargs):
            if str(path).startswith(__prefix):
                raise AssertionError(f"forbidden source {__name}: {path}")
            return __real(path, *args, **kwargs)

        monkeypatch.setattr(os, name, guarded)

    real_io_open = io.open

    def guarded_io_open(file, *args, **kwargs):
        if str(file).startswith(prefix):
            raise AssertionError(f"forbidden source open: {file}")
        return real_io_open(file, *args, **kwargs)

    monkeypatch.setattr(io, "open", guarded_io_open)


def _install_dispatch_guards(monkeypatch, *, forbid_execute_stage: bool = True) -> None:
    """No stage dispatch, probe, decode, model load or network may occur."""
    if forbid_execute_stage:
        monkeypatch.setattr(execution, "execute_stage", _boom("execution.execute_stage"))
    monkeypatch.setattr(execution, "has_synthetic_input", _boom("execution.has_synthetic_input"))
    monkeypatch.setattr(execution, "has_media_input", _boom("execution.has_media_input"))
    monkeypatch.setattr(execution, "_load_inputs", _boom("execution._load_inputs"))
    monkeypatch.setattr(media_experiment, "measure_revision", _boom("media_experiment.measure_revision"))
    monkeypatch.setattr(media_experiment, "measure_corpus", _boom("media_experiment.measure_corpus"))
    monkeypatch.setattr(media_experiment, "snapshot_source", _boom("media_experiment.snapshot_source"))

    from gate0.media import decode as media_decode
    from gate0.media.probe import FfprobeAdapter

    monkeypatch.setattr(media_decode, "decode_frames", _boom("media.decode.decode_frames"))
    monkeypatch.setattr(FfprobeAdapter, "probe", _boom("FfprobeAdapter.probe"))

    from gate0.adapters.siglip_local import LocalSiglipEmbeddingAdapter

    monkeypatch.setattr(
        LocalSiglipEmbeddingAdapter, "load_cpu", classmethod(_boom("LocalSiglipEmbeddingAdapter.load_cpu"))
    )
    monkeypatch.setattr(socket, "socket", _boom("socket.socket"))
    monkeypatch.setattr(socket, "create_connection", _boom("socket.create_connection"))


def _cli(argv_input_root: Path, output_root: Path, stage: str = "inventory") -> int:
    return main(
        [
            stage,
            "--run",
            str(output_root / RUN_ID),
            "--config",
            str(CONFIG),
            "--input-root",
            str(argv_input_root),
            "--output-root",
            str(output_root),
            "--run-id",
            RUN_ID,
        ]
    )


# ---------------------------------------------------------------------------
# S1-1: refusal happens before manifest/config/dispatch/source access
# ---------------------------------------------------------------------------

def test_cli_refuses_authorized_local_before_manifest_config_or_dispatch(
    tmp_path, monkeypatch, capsys
):
    declaration = _valid_declaration()
    input_root, sentinel = _make_input_root(tmp_path, declaration=declaration)
    output_root = tmp_path / "outputs"
    output_root.mkdir()

    _install_dispatch_guards(monkeypatch)
    _install_source_guard(monkeypatch, sentinel)
    # The manifest/config readers are the ordering proof: they must not run.
    monkeypatch.setattr("gate0.cli._load_json", _boom("cli._load_json (run_manifest/config)"))
    import gate0.config as config_module

    monkeypatch.setattr(config_module, "load_config", _boom("config.load_config"))

    modules_before = set(sys.modules)
    code = _cli(input_root, output_root)
    captured = capsys.readouterr()

    assert code == 20
    projection = json.loads(captured.out)
    assert projection["command"] == "inventory"
    assert projection["status"] == "BLOCKED_PREREQUISITE"
    assert projection["reason"] == AUTHORIZED_REASON
    assert projection["evidence_state"] == "NOT_OBSERVED"
    assert projection["source_access_attempted"] is False
    assert projection["declaration_error"] is None
    assert isinstance(projection["declaration_digest"], str)
    assert len(projection["declaration_digest"]) == 64
    for blocker in media_experiment.AUTHORIZED_EXECUTION_BLOCKERS:
        assert blocker in projection["blockers"]

    # No artifacts, no Gate decision, no late imports of torch/transformers.
    assert not (output_root / RUN_ID).exists()
    assert "gate_decision" not in captured.out
    late = set(sys.modules) - modules_before
    assert not ({"torch", "transformers", "sentence_transformers"} & late)

    # The digest really is the declaration digest, not a fabricated one.
    loaded = media_experiment.load_authorized_local_declaration(
        input_root / media_experiment.AUTHORIZED_CORPUS_FILE
    )
    assert projection["declaration_digest"] == loaded.declaration_digest


# ---------------------------------------------------------------------------
# S1-2: malformed declaration still refuses and never falls back
# ---------------------------------------------------------------------------

def test_malformed_authorized_declaration_refuses_without_synthetic_fallback(
    tmp_path, monkeypatch, capsys
):
    input_root, sentinel = _make_input_root(tmp_path, raw=b"{ this is not json")
    # Pre-existing synthetic/media inputs are present and must stay untouched.
    synthetic = input_root / "synthetic-corpus.json"
    synthetic.write_text("{}", encoding="utf-8")
    media = input_root / "media-corpus.json"
    media.write_text(json.dumps({"schema_version": "gate0.media-corpus.v1"}), encoding="utf-8")
    media_before = media.read_bytes()
    output_root = tmp_path / "outputs"
    output_root.mkdir()

    _install_dispatch_guards(monkeypatch)
    _install_source_guard(monkeypatch, sentinel)

    code = _cli(input_root, output_root)
    captured = capsys.readouterr()

    assert code == 20
    projection = json.loads(captured.out)
    assert projection["status"] == "BLOCKED_PREREQUISITE"
    assert projection["reason"] == AUTHORIZED_REASON
    assert projection["source_access_attempted"] is False
    assert projection["declaration_digest"] is None
    assert isinstance(projection["declaration_error"], str)
    assert projection["declaration_error"]
    for blocker in media_experiment.AUTHORIZED_EXECUTION_BLOCKERS:
        assert blocker in projection["blockers"]
    assert not (output_root / RUN_ID).exists()
    assert media.read_bytes() == media_before
    assert synthetic.read_text(encoding="utf-8") == "{}"


# ---------------------------------------------------------------------------
# S1-3: a generated fixture relabelled authorized_local cannot be promoted
# ---------------------------------------------------------------------------

def test_generated_fixture_relabel_cannot_become_authorized_local(
    tmp_path, monkeypatch, capsys
):
    relabelled = _valid_declaration()
    relabelled["corpus_kind"] = "generated_synthetic_media_not_experiment_evidence"
    input_root, sentinel = _make_input_root(tmp_path, declaration=relabelled)
    output_root = tmp_path / "outputs"
    output_root.mkdir()

    _install_dispatch_guards(monkeypatch)
    _install_source_guard(monkeypatch, sentinel)

    code = _cli(input_root, output_root)
    projection = json.loads(capsys.readouterr().out)

    assert code == 20
    assert projection["status"] == "BLOCKED_PREREQUISITE"
    assert projection["reason"] == AUTHORIZED_REASON
    assert "AUTHORIZED_CORPUS_KIND_MISMATCH" in projection["declaration_error"]
    assert not (output_root / RUN_ID).exists()


def test_generated_fixture_provenance_markers_are_refused(tmp_path, monkeypatch, capsys):
    forged = _valid_declaration()
    forged["provenance"]["generator"] = "LOCAL_GENERATED_MEDIA"
    input_root, sentinel = _make_input_root(tmp_path, declaration=forged)
    output_root = tmp_path / "outputs"
    output_root.mkdir()

    _install_dispatch_guards(monkeypatch)
    _install_source_guard(monkeypatch, sentinel)

    code = _cli(input_root, output_root)
    projection = json.loads(capsys.readouterr().out)

    assert code == 20
    assert projection["reason"] == AUTHORIZED_REASON
    assert "AUTHORIZED_CORPUS_FORGED_GENERATED_FIXTURE" in projection["declaration_error"]


# ---------------------------------------------------------------------------
# S1-4: execute_stage is a second fail-closed barrier
# ---------------------------------------------------------------------------

def test_execute_stage_refuses_authorized_local_before_loading_inputs(
    tmp_path, monkeypatch
):
    input_root, sentinel = _make_input_root(tmp_path, declaration=_valid_declaration())
    output_root = tmp_path / "outputs"
    output_root.mkdir()
    run = output_root / RUN_ID

    _install_dispatch_guards(monkeypatch, forbid_execute_stage=False)
    _install_source_guard(monkeypatch, sentinel)
    import gate0.config as config_module

    monkeypatch.setattr(config_module, "load_config", _boom("config.load_config"))

    with pytest.raises(media_experiment.AuthorizedLocalError) as excinfo:
        execution.execute_stage(
            "inventory",
            run=run,
            config_path=CONFIG,
            input_root=input_root,
            output_root=output_root,
            run_id=RUN_ID,
        )
    assert excinfo.value.reason == AUTHORIZED_REASON
    assert not run.exists()


# ---------------------------------------------------------------------------
# S1-5: admission is a filename-only check and refusal never raises
# ---------------------------------------------------------------------------

def test_has_authorized_local_input_is_filename_existence_only(tmp_path, monkeypatch):
    input_root = tmp_path / "inputs"
    input_root.mkdir()
    assert execution.has_authorized_local_input(input_root) is False

    (input_root / media_experiment.AUTHORIZED_CORPUS_FILE).write_bytes(b"\x00not json at all")
    monkeypatch.setattr(json, "loads", _boom("json.loads during admission check"))
    assert execution.has_authorized_local_input(input_root) is True

    # A directory with the declaration name is not an admissible file.
    other = tmp_path / "other"
    (other / media_experiment.AUTHORIZED_CORPUS_FILE).mkdir(parents=True)
    assert execution.has_authorized_local_input(other) is False


@pytest.mark.parametrize("raw", [b"", b"{", b"[]", b"null", b'{"schema_version": 5}'])
def test_authorized_local_refusal_never_raises_for_malformed_declaration(raw, tmp_path):
    input_root, _sentinel = _make_input_root(tmp_path, raw=raw)
    projection = execution.authorized_local_refusal(stage="prepare", input_root=input_root)
    assert projection["command"] == "prepare"
    assert projection["status"] == "BLOCKED_PREREQUISITE"
    assert projection["reason"] == AUTHORIZED_REASON
    assert projection["source_access_attempted"] is False
    assert projection["declaration_error"]
    for blocker in media_experiment.AUTHORIZED_EXECUTION_BLOCKERS:
        assert blocker in projection["blockers"]
