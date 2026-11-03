"""V3 authority-boundary regressions; all inputs are generated local fixtures."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from persistent_local_index.model_space import semantic_space_id

from vip_fvs.real_source_probe import RealSourceProbeBinding
from vip_fvs.real_source_service import RealSourcePreparationRefusal, RealSourceRequest, prepare_real_source


def _runtime():
    from vip_fvs.local_semantic import checked_runtime
    from vip_fvs.retrieval_adapter import fake_semantic_space
    return checked_runtime(
        image_embedder=lambda paths: np.ones((len(paths), 768), dtype=np.float32),
        text_embedder=lambda texts: np.ones((len(texts), 768), dtype=np.float32),
        semantic_space=fake_semantic_space(), fake=False, runtime_identity="generated-v3-runtime",
    )


def _auth(source: Path, index: Path, query: str, revision: str, runtime, model_root: Path) -> dict:
    space = runtime.semantic_space
    body = {
        "source_path": str(source.resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "purpose": "generated-v3-test-only",
        "model_root": str(model_root.resolve()),
        "model_revision": space.frozen_revision,
        "weights_sha256": space.weights_sha256,
        "runtime_root": str((model_root.parent / "runtime").resolve()),
        "index_root": str(index.resolve()),
        "output_root": str((index.parent / "out").resolve()),
        "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
        "authorization_id": "auth-v3", "source_revision_id": revision,
        "query_digest": hashlib.sha256(json.dumps(query, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "model_identity": space.model_identity, "semantic_space_id": semantic_space_id(space),
        "index_digest": hashlib.sha256(json.dumps(str(index.resolve()), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "local_only": True, "expires_at": "2099-01-01T00:00:00+00:00", "revoked": False,
        "selected_stream_index": 0,
        "policy_digest": "1" * 64, "scope_digest": "2" * 64,
    }
    body["record_digest"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return body


def test_prepare_rejects_opaque_authorization_before_probe(tmp_path: Path, monkeypatch):
    source = tmp_path / "generated.mp4"; source.write_bytes(b"fixture")
    monkeypatch.setattr("vip_fvs.real_source_service.probe_real_source", lambda *a, **k: pytest.fail("probe must not run"))
    request = RealSourceRequest(source, "target", "opaque-path", _runtime(), tmp_path / "index", tmp_path / "out", tmp_path / "run", "rev", "attempt")
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORIZATION_REQUIRED"):
        prepare_real_source(request)


def test_prepare_calls_refinement_adapter_and_persists_full_record(tmp_path: Path, monkeypatch):
    from gate3.fixturegen import build_mp4
    from vip_fvs.refinement_adapter import refine_retrieval_candidate

    source = tmp_path / "generated.mp4"
    source.write_bytes(build_mp4(media_timescale=1000, sample_deltas=(40, 40, 40)))
    runtime = _runtime(); index = tmp_path / "index"; run = tmp_path / "run"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    probe = RealSourceProbeBinding(source, "rev", digest, source.stat().st_size, 0, 1, 1000,
        {"streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}], "stream_index": 0,
         "frames": [{"stream_index": 0, "best_effort_timestamp": "40"},
                    {"stream_index": 0, "best_effort_timestamp": "80"}]},
        "a" * 64, str(run / "probe.json"), str(run / "raw.json"), str(run / "probe.json"), "policy")
    monkeypatch.setattr("vip_fvs.real_source_service.probe_real_source",
        lambda path, **kwargs: __import__("dataclasses").replace(
            probe, source_path=Path(path), source_locator=kwargs["source_locator"],
            snapshot_evidence=kwargs["snapshot_evidence"]))
    monkeypatch.setattr("vip_fvs.real_source_service.retrieve_local_semantic",
        lambda measured, *a, **k: SimpleNamespace(space_id=semantic_space_id(runtime.semantic_space), generation_id="generation-v3", hits=(SimpleNamespace(source_sha256=digest, source_path=str(measured.source_path), rank=1, score=.9, pts=40, timebase_num=1, timebase_den=1000),)))
    calls = []
    def adapter(*args, **kwargs):
        calls.append(kwargs)
        return refine_retrieval_candidate(*args, **kwargs)
    model_root = tmp_path / "model"
    request = RealSourceRequest(source, "target", _auth(source, index, "target", "rev", runtime, model_root),
        runtime, index, tmp_path / "out", run, "rev", "attempt", model_root=model_root,
        source_snapshot_root=tmp_path / "snapshot-store", max_source_bytes=1_000_000,
        max_store_bytes=2_000_000, selected_stream_index=0, refinement_adapter=adapter)
    result = prepare_real_source(request)
    assert calls and calls[0]["requested_pts"] == (40, 80)
    artifact = Path(result.bundle.payload["refinement"]["evidence_artifact_ref"])
    assert artifact.is_file()
    import json
    from gate3.refinement import is_binding_eligible

    persisted = json.loads(artifact.read_text())
    assert is_binding_eligible(persisted)
