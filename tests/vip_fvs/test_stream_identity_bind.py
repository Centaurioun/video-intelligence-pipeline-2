"""S4 bind-time enforcement tests using only deterministic synthetic bytes."""
from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from gate3.container import parse_iso_bmff_timing
from gate3.fixturegen import build_mp4, build_multi_trak_mp4
from vip_fvs.refinement_adapter import RefinementRefusal, refine_retrieval_candidate


def _source_bytes(*, duplicate_ids: bool = False) -> bytes:
    if duplicate_ids:
        return build_multi_trak_mp4(
            media_timescale=1000,
            traks=[
                {"media_timescale": 1000, "sample_deltas": (40, 40), "track_id": 1, "handler": b"vide"},
                {"media_timescale": 48000, "sample_deltas": (1024, 1024), "track_id": 1, "handler": b"soun"},
            ],
        )
    return build_multi_trak_mp4(
        media_timescale=1000,
        traks=[
            {"media_timescale": 48000, "sample_deltas": (1024, 1024), "track_id": 1, "handler": b"soun"},
            {"media_timescale": 1000, "sample_deltas": (40, 40), "track_id": 2, "handler": b"vide"},
        ],
    )


def _persist_probe(tmp_path: Path, stream_ids: tuple[str, str]):
    payload = {
        "streams": [
            {"index": index, "codec_type": codec_type, "id": stream_id}
            for index, (codec_type, stream_id) in enumerate(
                zip(("audio", "video"), stream_ids, strict=True)
            )
        ]
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path = tmp_path / "probe-canonical.json"
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()


def _refine(path: Path, *, probe=None, selected_stream_index: int = 1):
    measured = parse_iso_bmff_timing(path, selected_stream_index=selected_stream_index)
    hit = {
        "source_path": str(path),
        "source_sha256": measured["source_bytes_sha256"],
        "pts": int(measured["pts_ticks"][-1]),
        "timebase_num": 1,
        "timebase_den": int(measured["media_timescale"]),
        "rank": 1,
        "score": 0.9,
    }
    probe_path, probe_digest = probe if probe is not None else (None, None)
    kwargs = {
        "source_revision_id": "revision:synthetic-s4",
        "requested_pts": (int(measured["pts_ticks"][0]), int(measured["pts_ticks"][-1])),
        "stream_index": selected_stream_index,
        "selected_stream_index": selected_stream_index,
        "attempt_id": "attempt:synthetic-s4",
        "stage_idempotency_key": "real-source:synthetic-s4",
        "tool_identity": {"name": "vip_fvs.real_source_service", "version": "v3"},
    }
    if probe is not None:
        kwargs["probe_artifact_path"] = probe_path
        kwargs["probe_digest"] = probe_digest
    return refine_retrieval_candidate(hit, **kwargs)


def _missing_probe_refusal(path: Path, *, selected_stream_index: int = 1) -> str:
    with pytest.raises(RefinementRefusal) as exc:
        _refine(path, selected_stream_index=selected_stream_index)
    return str(exc.value)


def test_r_b1_valid_two_track_probe_binds_selected_video(tmp_path: Path) -> None:
    source = tmp_path / "audio-first-video-second.mp4"
    source.write_bytes(_source_bytes())
    probe = _persist_probe(tmp_path, ("0x1", "0x2"))

    result = _refine(source, probe=probe)

    assert result.binding_eligible is True
    assert result.source_digest_before == hashlib.sha256(source.read_bytes()).hexdigest()
    assert result.source_digest_after == result.source_digest_before
    assert result.measured_refinement["stream_index"] == 1
    assert result.measured_refinement["evidence_class"] == "MEASURED"


def test_r_b2_swapped_probe_positions_keep_a_distinct_typed_refusal(tmp_path: Path) -> None:
    source = tmp_path / "audio-first-video-second.mp4"
    source.write_bytes(_source_bytes())
    probe = _persist_probe(tmp_path, ("0x2", "0x1"))

    with pytest.raises(RefinementRefusal) as exc:
        _refine(source, probe=probe)

    assert str(exc.value).startswith("stream identity is unproven: ")
    assert str(exc.value) != _missing_probe_refusal(source)


def test_r_b3_missing_probe_keeps_legacy_refusal_prefix(tmp_path: Path) -> None:
    source = tmp_path / "audio-first-video-second.mp4"
    source.write_bytes(_source_bytes())

    with pytest.raises(RefinementRefusal) as exc:
        _refine(source)

    assert str(exc.value).startswith("stream identity is unproven: ")


def test_r_b4_duplicate_track_identity_keeps_a_distinct_refusal(tmp_path: Path) -> None:
    source = tmp_path / "duplicate-track-id.mp4"
    source.write_bytes(_source_bytes(duplicate_ids=True))
    probe = _persist_probe(tmp_path, ("0x1", "0x1"))

    with pytest.raises(RefinementRefusal) as exc:
        _refine(source, probe=probe, selected_stream_index=0)

    assert str(exc.value).startswith("stream identity is unproven: ")
    assert str(exc.value) != _missing_probe_refusal(source, selected_stream_index=0)


def _service_runtime():
    from vip_fvs.local_semantic import checked_runtime
    from vip_fvs.retrieval_adapter import fake_semantic_space

    return checked_runtime(
        image_embedder=lambda paths: np.ones((len(paths), 768), dtype=np.float32),
        text_embedder=lambda texts: np.ones((len(texts), 768), dtype=np.float32),
        semantic_space=fake_semantic_space(),
        fake=False,
        runtime_identity="test-injected-semantic-runtime/v1",
    )


def _service_probe_binding(source: Path, source_digest: str, run_dir: Path):
    from vip_fvs.real_source_probe import RealSourceProbeBinding

    canonical_ref = str(run_dir / "probe-canonical.json")
    return RealSourceProbeBinding(
        source_path=source,
        source_revision_id="revision:synthetic-s4",
        source_sha256=source_digest,
        source_byte_count=source.stat().st_size,
        selected_stream_index=0,
        timebase_num=1,
        timebase_den=1000,
        ffprobe_json={
            "streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}],
            "stream_index": 0,
            "frames": [
                {"stream_index": 0, "best_effort_timestamp": "40"},
                {"stream_index": 0, "best_effort_timestamp": "80"},
            ],
        },
        probe_digest="a" * 64,
        probe_artifact_ref=canonical_ref,
        raw_probe_artifact_ref=str(run_dir / "probe-raw.json"),
        canonical_probe_artifact_ref=canonical_ref,
        policy_identity="synthetic-s4-policy",
    )


def _service_authorization(case):
    from persistent_local_index.model_space import semantic_space_id

    space = case.runtime.semantic_space
    authorization = {
        "source_path": str(case.source.resolve()),
        "source_sha256": case.source_digest,
        "purpose": "generated-test-only",
        "model_root": str(case.model_root.resolve()),
        "model_revision": space.frozen_revision,
        "weights_sha256": space.weights_sha256,
        "runtime_root": str((case.source.parent / "runtime").resolve()),
        "index_root": str(case.index_root.resolve()),
        "output_root": str(case.output_root.resolve()),
        "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
        "authorization_id": "auth-synthetic-s4",
        "source_revision_id": "revision:synthetic-s4",
        "query_digest": hashlib.sha256(
            json.dumps(case.query, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "model_identity": space.model_identity,
        "semantic_space_id": semantic_space_id(space),
        "index_digest": hashlib.sha256(
            json.dumps(str(case.index_root.resolve()), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "local_only": True,
        "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": False,
        "selected_stream_index": 0,
        "policy_digest": "1" * 64,
        "scope_digest": "2" * 64,
    }
    authorization["record_digest"] = hashlib.sha256(
        json.dumps(authorization, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return authorization


def _patch_service_producers(monkeypatch, case):
    from persistent_local_index.model_space import semantic_space_id

    monkeypatch.setattr(
        "vip_fvs.real_source_service.probe_real_source",
        lambda path, **kwargs: replace(
            case.probe,
            source_path=Path(path),
            source_locator=kwargs["source_locator"],
            snapshot_evidence=kwargs["snapshot_evidence"],
        ),
    )
    monkeypatch.setattr(
        "vip_fvs.real_source_service.retrieve_local_semantic",
        lambda measured, *args, **kwargs: SimpleNamespace(
            space_id=semantic_space_id(case.runtime.semantic_space),
            generation_id="synthetic-generation-s4",
            hits=(SimpleNamespace(source_sha256=case.source_digest,
                                  source_path=str(measured.source_path), rank=1,
                                  score=0.9, pts=40, timebase_num=1,
                                  timebase_den=1000),),
        ),
    )



def _service_request(case, adapter):
    from vip_fvs.real_source_service import RealSourceRequest

    return RealSourceRequest(
        source_path=case.source,
        query=case.query,
        authorization=_service_authorization(case),
        runtime=case.runtime,
        index_root=case.index_root,
        output_root=case.output_root,
        run_dir=case.run_dir,
        source_revision_id="revision:synthetic-s4",
        attempt_id="attempt:synthetic-s4-service",
        model_root=case.model_root,
        source_snapshot_root=case.root / "snapshot-store",
        max_source_bytes=1_000_000,
        max_store_bytes=2_000_000,
        refinement_adapter=adapter,
    )


def test_service_forwards_probe_binding_reference_and_digest(monkeypatch, tmp_path: Path) -> None:
    from vip_fvs.real_source_service import prepare_real_source
    from vip_fvs.refinement_adapter import refine_retrieval_candidate as refine

    source = tmp_path / "service-source.mp4"
    source.write_bytes(build_mp4(media_timescale=1000, sample_deltas=(40, 40, 40)))
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    run_dir = tmp_path / "run"
    case = SimpleNamespace(
        root=tmp_path,
        source=source,
        source_digest=source_digest,
        run_dir=run_dir,
        runtime=_service_runtime(),
        model_root=tmp_path / "model",
        index_root=tmp_path / "index",
        output_root=tmp_path / "output",
        query="synthetic identity query",
    )
    case.probe = _service_probe_binding(source, source_digest, run_dir)
    _patch_service_producers(monkeypatch, case)

    calls = []

    def adapter(*args, **kwargs):
        calls.append(kwargs)
        return refine(*args, **kwargs)

    prepare_real_source(_service_request(case, adapter))

    assert calls
    assert calls[0]["probe_artifact_path"] == case.probe.canonical_probe_artifact_ref
    assert calls[0]["probe_digest"] == case.probe.probe_digest


def test_refinement_wrapper_forwards_probe_artifact_and_digest(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "single-track.mp4"
    source.write_bytes(b"synthetic single-track source")
    marker_path = tmp_path / "producer-probe.json"
    marker_digest = "a" * 64
    seen = {}

    def capture(request, candidate, **kwargs):
        seen["request"] = request
        seen.update(kwargs)
        return object()

    monkeypatch.setattr("vip_fvs.refinement_adapter.refine_requested_candidate", capture)
    result = refine_retrieval_candidate(
        {"source_path": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        source_revision_id="revision:synthetic-s4",
        requested_pts=(0, 1),
        probe_artifact_path=marker_path,
        probe_digest=marker_digest,
    )

    assert result is not None
    assert seen["probe_artifact_path"] == marker_path
    assert seen["probe_digest"] == marker_digest
