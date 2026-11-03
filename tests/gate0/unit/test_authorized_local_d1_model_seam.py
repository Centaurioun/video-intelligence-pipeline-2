"""D-1 Lane A / S4: model preconditions, deferred SigLIP seam, decoder capability.

D-1 authorizes *source-only* preparation: no model download, no weight load, no
inference, no torch/transformers, no filesystem/env probing.  These tests pin
that the model story is declarative and deterministic from the config mapping
alone, that the real model load seam exists but is deferred/closed, and that
pixel decoding stays blocked behind the closed D-3 gate.

Guard rails:
* ``sys.modules`` must stay free of torch/transformers, including during calls;
* no config-derived path may be stat'ed/opened;
* no environment variable or ``importlib.util.find_spec`` may be consulted;
* behaviour must be identical whether or not torch/transformers are installed.
"""
from __future__ import annotations

import dataclasses
import importlib.util
import io
import json
import os
import sys
from pathlib import Path

import pytest

from gate0 import execution
from gate0.media_experiment import AuthorizedLocalError

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "gate0" / "default.json"
FORBIDDEN_IMPORTS = ("torch", "transformers", "hf_hub", "sentence_transformers")


def _default_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _complete_model_config() -> dict:
    config = _default_config()
    config["model"].update({
        "model_identity": "siglip-base-patch16-384",
        "weights_digest": "a" * 64,
        "processor_digest": "b" * 64,
        "preprocessing_digest": "c" * 64,
        "dimension": 768,
        "runtime_precision": "float32",
        "licence": "apache-2.0",
        "model_root": "models/siglip-base-patch16-384",
        "revision": "main",
    })
    config["sandbox"].update({
        "sandbox_id": "sandbox-1",
        "bwrap_version": "0.9.0",
        "bwrap_digest": "d" * 64,
        "interpreter_digest": "e" * 64,
    })
    return config


@pytest.fixture()
def hostile_environment(monkeypatch):
    """Forbid torch/transformers imports, filesystem probes and find_spec."""
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def guarded_import(name, *args, **kwargs):
        root = name.split(".")[0]
        if root in FORBIDDEN_IMPORTS:
            raise AssertionError(f"forbidden model import: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded_import)

    real_find_spec = importlib.util.find_spec

    def guarded_find_spec(name, *args, **kwargs):
        raise AssertionError(f"forbidden import probing: {name}")

    monkeypatch.setattr(importlib.util, "find_spec", guarded_find_spec)

    real_stat = os.stat

    def guarded_stat(path, *args, **kwargs):
        text = str(path)
        if "/models/" in text or "models/siglip" in text:
            raise AssertionError(f"forbidden model path probe: {path}")
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(os, "stat", guarded_stat)
    real_io_open = io.open

    def guarded_io_open(file, *args, **kwargs):
        text = str(file)
        if "/models/" in text or "models/siglip" in text:
            raise AssertionError(f"forbidden model path open: {file}")
        return real_io_open(file, *args, **kwargs)

    monkeypatch.setattr(io, "open", guarded_io_open)
    yield
    monkeypatch.setattr(importlib.util, "find_spec", real_find_spec)


def test_no_model_libraries_are_imported():
    assert "torch" not in sys.modules
    assert "transformers" not in sys.modules


def test_model_preconditions_report_placeholders_as_blockers(hostile_environment):
    result = execution.model_preconditions(_default_config())
    assert result["config_complete"] is False
    assert result["gate_open"] is False
    assert result["model_identity"] == "NOT_OBSERVED"
    assert result["weights_digest"] is None
    assert result["processor_digest"] == "0" * 64
    assert result["dimension"] == 0
    assert result["decode_pixels"] is False
    for blocker in (
        "MODEL_IDENTITY_NOT_OBSERVED",
        "MODEL_WEIGHTS_DIGEST_MISSING",
        "MODEL_PROCESSOR_DIGEST_PLACEHOLDER",
        "MODEL_LICENCE_MISSING",
        "MODEL_RUNTIME_PRECISION_MISSING",
        "MODEL_SANDBOX_BINDING_MISSING",
    ):
        assert blocker in result["blockers"]
    assert "torch" not in sys.modules and "transformers" not in sys.modules


def test_model_preconditions_are_deterministic_and_do_not_mutate_config(hostile_environment):
    config = _complete_model_config()
    before = json.dumps(config, sort_keys=True)
    first = execution.model_preconditions(config)
    second = execution.model_preconditions(config)
    assert first == second
    assert json.dumps(config, sort_keys=True) == before
    assert first["config_complete"] is True
    assert first["gate_open"] is False
    assert first["blockers"] == ()
    assert first["model_identity"] == "siglip-base-patch16-384"
    assert first["weights_digest"] == "a" * 64
    assert first["dimension"] == 768
    assert first["runtime_precision"] == "float32"


@pytest.mark.parametrize("field, blocker", [
    ("weights_digest", "MODEL_WEIGHTS_DIGEST_MISSING"),
    ("processor_digest", "MODEL_PROCESSOR_DIGEST_PLACEHOLDER"),
    ("dimension", "MODEL_IDENTITY_NOT_OBSERVED"),
    ("runtime_precision", "MODEL_RUNTIME_PRECISION_MISSING"),
    ("licence", "MODEL_LICENCE_MISSING"),
])
def test_model_preconditions_isolated_blockers(field, blocker, hostile_environment):
    config = _complete_model_config()
    config["model"][field] = None if field != "dimension" else 0
    result = execution.model_preconditions(config)
    assert result["config_complete"] is False
    assert result["gate_open"] is False
    assert blocker in result["blockers"]


def test_model_preconditions_identical_without_model_libraries(monkeypatch):
    """Even if imports are unavailable, the answer is config-derived and equal."""
    config = _complete_model_config()
    baseline = execution.model_preconditions(config)
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".")[0] in FORBIDDEN_IMPORTS:
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded_import)
    assert execution.model_preconditions(config) == baseline
    assert execution.decoder_capability(config=config) == execution.decoder_capability(config=config)


def test_decoder_capability_stays_closed_under_closed_gate(hostile_environment):
    assert execution.authorized_local_execution_gate_open(_default_config()) is False
    assert execution.authorized_local_execution_gate_open(_complete_model_config()) is False

    closed = execution.decoder_capability(config=_complete_model_config())
    assert closed["status"] == "BLOCKED_PREREQUISITE"
    assert closed["decode_pixels"] is False
    assert "DECODE_PIXELS_NOT_AUTHORIZED" not in closed["blockers"]

    pixel = execution.decoder_capability(config=_complete_model_config(), decode_pixels=True)
    assert pixel["status"] == "BLOCKED_PREREQUISITE"
    assert pixel["decode_pixels"] is True
    assert "DECODE_PIXELS_NOT_AUTHORIZED" in pixel["blockers"]

    default_pixel = execution.decoder_capability(config=_default_config(), decode_pixels=True)
    for blocker in pixel["blockers"]:
        assert blocker in default_pixel["blockers"] or blocker.startswith("MODEL_")


def test_decoder_capability_never_constructs_a_decoder(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("decoder construction attempted")

    monkeypatch.setattr("gate0.media.decode.FfprobeFrameDecoder", forbidden)
    monkeypatch.setattr("gate0.adapters.decoder.SyntheticDecoder", forbidden)
    result = execution.decoder_capability(config=_complete_model_config(), decode_pixels=True)
    assert result["status"] == "BLOCKED_PREREQUISITE"


def test_deferred_siglip_seam_is_deferred_and_closed(hostile_environment):
    seam = execution.build_deferred_siglip_seam(_complete_model_config())
    assert dataclasses.is_dataclass(seam)
    assert seam.is_loaded is False
    assert seam.model_root == "models/siglip-base-patch16-384"
    assert seam.revision == "main"
    assert seam.weights_sha256 == "a" * 64
    assert seam.processor_digest == "b" * 64
    assert seam.preprocessing_digest == "c" * 64
    assert seam.dimension == 768
    assert seam.runtime_precision == "float32"
    assert seam.licence == "apache-2.0"
    with pytest.raises(RuntimeError) as excinfo:
        seam.load()
    assert str(excinfo.value) == "AUTHORIZED_LOCAL_MODEL_LOAD_NOT_AUTHORIZED"
    assert seam.is_loaded is False


def test_deferred_siglip_seam_is_frozen(hostile_environment):
    seam = execution.build_deferred_siglip_seam(_complete_model_config())
    with pytest.raises(dataclasses.FrozenInstanceError):
        seam.dimension = 384
    with pytest.raises(dataclasses.FrozenInstanceError):
        seam.is_loaded = True


def test_deferred_siglip_seam_rejects_incomplete_identity(hostile_environment):
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.build_deferred_siglip_seam(_default_config())
    assert excinfo.value.reason == "AUTHORIZED_LOCAL_MODEL_NOT_DECLARED"

    partial = _complete_model_config()
    partial["model"]["licence"] = None
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.build_deferred_siglip_seam(partial)
    assert excinfo.value.reason == "AUTHORIZED_LOCAL_MODEL_NOT_DECLARED"


def test_deferred_siglip_seam_never_calls_local_adapter_load_cpu(hostile_environment, monkeypatch):
    calls = []
    monkeypatch.setattr("gate0.adapters.siglip_local.LocalSiglipEmbeddingAdapter.load_cpu",
                        lambda self, *args, **kwargs: calls.append(args) or (_ for _ in ()).throw(
                            AssertionError("load_cpu must stay deferred")))
    seam = execution.build_deferred_siglip_seam(_complete_model_config())
    with pytest.raises(RuntimeError):
        seam.load()
    assert calls == []
    assert "transformers" not in sys.modules


# ---------------------------------------------------------------------------
# S7: config completeness is not authorization
# ---------------------------------------------------------------------------

def test_model_preconditions_never_report_authorized(hostile_environment):
    for config in (_default_config(), _complete_model_config()):
        result = execution.model_preconditions(config)
        assert "ready" not in result
        assert result["gate_open"] is False
        assert execution.authorized_local_execution_gate_open(config) is False
        capability = execution.decoder_capability(config=config)
        assert capability["status"] == "BLOCKED_PREREQUISITE"
