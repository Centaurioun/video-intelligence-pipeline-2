"""RED integration contract for generated-fixture real-source preparation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from vip_fvs.local_semantic import checked_runtime
from persistent_local_index.model_space import semantic_space_id
from vip_fvs.real_source_probe import RealSourceProbeBinding
from vip_fvs.real_source_service import RealSourcePreparationRefusal, RealSourceRequest, prepare_real_source
from vip_fvs.review_bundle import ReviewBundle


def _runtime():
    from vip_fvs.retrieval_adapter import fake_semantic_space

    return checked_runtime(
        image_embedder=lambda paths: np.ones((len(paths), 768), dtype=np.float32),
        text_embedder=lambda texts: np.ones((len(texts), 768), dtype=np.float32),
        semantic_space=fake_semantic_space(),
        fake=False,
        runtime_identity="test-injected-semantic-runtime/v1",
    )


def _auth(source: Path, index: Path, output: Path, runtime, query: str = "target phrase") -> dict:
    space = runtime.semantic_space
    body = {"source_path": str(source.resolve()), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "purpose": "generated-test-only", "model_root": str((output.parent / "model").resolve()),
            "model_revision": space.frozen_revision, "weights_sha256": space.weights_sha256,
            "runtime_root": str((output.parent / "runtime").resolve()), "index_root": str(index.resolve()),
            "output_root": str(output.resolve()),
            "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
            "authorization_id": "auth-test", "source_revision_id": "rev-generated-1",
            "query_digest": hashlib.sha256(json.dumps(query, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "model_identity": space.model_identity, "semantic_space_id": semantic_space_id(space),
            "index_digest": hashlib.sha256(json.dumps(str(index.resolve()), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "local_only": True, "expires_at": "2099-01-01T00:00:00+00:00", "revoked": False,
            "selected_stream_index": 0, "policy_digest": "1" * 64, "scope_digest": "2" * 64}
    body["record_digest"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return body


def test_prepare_real_source_seals_awaiting_editorial_bundle_without_synthetic_probe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from gate3.fixturegen import build_mp4

    source = tmp_path / "generated-real-source.mp4"
    source.write_bytes(build_mp4(media_timescale=1000, sample_deltas=(40, 40, 40)))
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    run_dir = tmp_path / "run"
    probe = RealSourceProbeBinding(
        source_path=source,
        source_revision_id="rev-generated-1",
        source_sha256=source_digest,
        source_byte_count=source.stat().st_size,
        selected_stream_index=0,
        timebase_num=1,
        timebase_den=1000,
            ffprobe_json={"streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}], "stream_index": 0,
                          "frames": [{"stream_index": 0, "best_effort_timestamp": "40"},
                                     {"stream_index": 0, "best_effort_timestamp": "80"}]},
        probe_digest="b" * 64,
        probe_artifact_ref=str(run_dir / "probe-canonical.json"),
        raw_probe_artifact_ref=str(run_dir / "probe-raw.json"),
        canonical_probe_artifact_ref=str(run_dir / "probe-canonical.json"),
        policy_identity="policy-real-source-test",
    )
    monkeypatch.setattr("vip_fvs.real_source_service.probe_real_source", lambda path, **kw: __import__("dataclasses").replace(probe, source_path=Path(path), source_locator=kw["source_locator"], snapshot_evidence=kw["snapshot_evidence"]))
    monkeypatch.setattr(
        "vip_fvs.source_adapter._synthetic_probe",
        lambda *a, **k: pytest.fail("real preparation used synthetic probe"),
    )
    request_runtime = _runtime()
    monkeypatch.setattr(
        "vip_fvs.real_source_service.retrieve_local_semantic",
        lambda measured, *a, **k: SimpleNamespace(space_id=semantic_space_id(request_runtime.semantic_space), generation_id="generated-generation-v5", hits=(SimpleNamespace(
            source_sha256=source_digest, source_path=str(measured.source_path), rank=1, score=0.9, pts=40,
            timebase_num=1, timebase_den=1000,
            timestamp_human="00:00:00.040",
        ),)),
    )

    request = RealSourceRequest(
        source_path=source,
        query="target phrase",
        authorization=_auth(source, tmp_path / "index", tmp_path / "out", request_runtime),
        runtime=request_runtime,
        index_root=tmp_path / "index",
        output_root=tmp_path / "out",
        run_dir=run_dir,
        source_revision_id="rev-generated-1",
        attempt_id="attempt-generated-1",
        selected_stream_index=0,
        model_root=tmp_path / "model", source_snapshot_root=tmp_path / "snapshot-store",
        max_source_bytes=1_000_000, max_store_bytes=2_000_000,
    )
    result = prepare_real_source(request)
    bundle = result.bundle if hasattr(result, "bundle") else result
    assert isinstance(bundle, ReviewBundle)
    payload = bundle.payload
    assert payload["review_status"] == "AWAITING_EDITORIAL_DECISION"
    assert payload["decision"] is None
    assert payload["source"]["source_sha256"] == source_digest
    assert payload["source"]["selected_stream_index"] == 0
    assert payload["candidate"]["evidence_class"] == "MATCHED"
    assert payload["candidate"]["binding_eligible"] is False
    assert payload["refinement"]["status"] == "MEASURED"
    assert payload["refinement"]["evidence_class"] == "MEASURED"
    assert payload["refinement"]["source_pts_interval"]["time_domain"] == "source_pts"
    assert payload["refinement"]["timebase"] == {"num": 1, "den": 1000}
    assert payload["refinement"]["source_pts_interval"]["start"] == 40
    assert payload["refinement"]["source_pts_interval"]["end"] == 80
    assert payload["presentation"]["display_only"] is True
    assert payload["generation"]["semantic_space_id"] == semantic_space_id(request_runtime.semantic_space)
    assert payload["generation"]["generation_id"] == "generated-generation-v5"


def test_prepare_real_source_fails_closed_on_retrieval_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "generated-real-source.mp4"
    source.write_bytes(b"generated fixture bytes for retrieval failure")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    run_dir = tmp_path / "run"
    probe = RealSourceProbeBinding(
        source_path=source, source_revision_id="rev-generated-1", source_sha256=digest,
        source_byte_count=source.stat().st_size, selected_stream_index=0, timebase_num=1,
        timebase_den=1000, ffprobe_json={"streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}], "stream_index": 0, "pts_ticks": [40, 80]},
        probe_digest="c" * 64, probe_artifact_ref=str(run_dir / "probe-canonical.json"),
        raw_probe_artifact_ref=str(run_dir / "probe-raw.json"), canonical_probe_artifact_ref=str(run_dir / "probe-canonical.json"),
        policy_identity="policy-real-source-test",
    )
    monkeypatch.setattr("vip_fvs.real_source_service.probe_real_source", lambda path, **kw: __import__("dataclasses").replace(probe, source_path=Path(path), source_locator=kw["source_locator"], snapshot_evidence=kw["snapshot_evidence"]))
    monkeypatch.setattr("vip_fvs.real_source_service.retrieve_local_semantic", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("index failed")))
    request = RealSourceRequest(
        source_path=source, query="target phrase", authorization=_auth(source, tmp_path / "index", tmp_path / "out", _runtime()), runtime=_runtime(),
        index_root=tmp_path / "index", output_root=tmp_path / "out", run_dir=run_dir,
        source_revision_id="rev-generated-1", attempt_id="attempt-generated-1", selected_stream_index=0,
            model_root=tmp_path / "model", source_snapshot_root=tmp_path / "snapshot-store",
            max_source_bytes=1_000_000, max_store_bytes=2_000_000,
    )
    with pytest.raises(RealSourcePreparationRefusal, match="SEMANTIC_RETRIEVAL_FAILED"):
        prepare_real_source(request)
