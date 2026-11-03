"""Product orchestration contract for the separate local index/query operations.

The fake engine is deliberately injected: these checks exercise coordinator
composition and provenance without media decoding, model execution, or I/O from
the persistent index implementation.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
from typing import Sequence

import numpy as np
import pytest
from vip_fvs.semantic_index import GenerationSpec, IndexSummary, SearchHit, SemanticSpace


def _space() -> SemanticSpace:
    return SemanticSpace(
        model_identity="fixture-model", frozen_revision="fixture-r1",
        weights_sha256="1" * 64, processor_digest="2" * 64,
        image_preprocessing_digest="3" * 64,
        text_preprocessing_contract="padding=max_length", embedding_dim=2,
        dtype="float32", normalization="l2",
    )


class CountingEngine:
    """Small deterministic engine that records which product operation ran."""

    def __init__(self) -> None:
        from persistent_local_index.model_space import build_generation_spec

        self.spec = build_generation_spec(_space())
        self.index_calls: list[tuple[Path, Path, object, object]] = []
        self.query_calls: list[tuple[Path, object, tuple[str, ...], object, int]] = []
        self.hit = SearchHit(
            query="harbor", rank=1, score=0.875, row_id=7,
            source_path="fixture://source-a", source_sha256="a" * 64,
            pts=9000, timebase_num=1, timebase_den=90000,
            timestamp_human="00:00:00.100", thumbnail_path=None,
            thumbnail_status="MISSING",
        )

    def build_generation_spec(self, space: SemanticSpace) -> GenerationSpec:
        assert space == _space()
        return self.spec

    def index_source(self, input_path: Path, index_root: Path, spec: GenerationSpec, image_embedder):
        self.index_calls.append((Path(input_path), Path(index_root), spec, image_embedder))
        return IndexSummary(self.spec.generation_id, indexed=1, skipped=0, reused=0, failed=0, results=())

    def query(self, index_root: Path, spec: GenerationSpec, texts: Sequence[str], text_embedder,
              *, top_k: int):
        self.query_calls.append((Path(index_root), spec, tuple(texts), text_embedder, top_k))
        return {text: (dataclasses.replace(self.hit, query=text),) for text in texts}


def _runtime():
    from vip_fvs.local_semantic import checked_runtime

    def image_embedder(paths: Sequence[Path]) -> np.ndarray:
        return np.ones((len(paths), 2), dtype=np.float32)

    def text_embedder(texts: Sequence[str]) -> np.ndarray:
        return np.ones((len(texts), 2), dtype=np.float32)

    return checked_runtime(image_embedder=image_embedder, text_embedder=text_embedder,
                           semantic_space=_space(), fake=True, runtime_identity="fixture-runtime")


def _v2_base_profile_payload() -> dict[str, object]:
    """Closed synthetic profile identity for CLI selection tests only."""
    assets = (("tokenizer.json", "a" * 64),)
    processor_payload = json.dumps(
        {"identity_mapping": "vip-processor-assets-v1",
         "assets": [{"name": name, "sha256": digest} for name, digest in sorted(assets)]},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    return {
        "profile_id": "vip-v2-siglip2-base-224",
        "model_id": "google/siglip2-base-patch16-224",
        "family": "siglip2",
        "frozen_revision": "1" * 40,
        "weights_sha256": "c" * 64,
        "processor_asset_digests": [list(item) for item in assets],
        "processor_digest": hashlib.sha256(processor_payload.encode("utf-8")).hexdigest(),
        "image_preprocessing_digest": "b" * 64,
        "text_preprocessing_contract": "vip-v2-siglip2-base-224:text-synthetic:v1",
        "image_size": 224,
        "patch_size": 16,
        "embedding_dim": 768,
        "output_dtype": "float32",
        "normalization": "l2",
        "loader_kind": "siglip2-auto",
        "device_backend": "pytorch-mps",
        "precision_policy_id": "siglip2-fp16-compute-fp32-output",
        "precision_policy_version": 1,
    }


def test_cli_fake_v2_profile_selects_its_own_semantic_space_and_vector_width(tmp_path: Path) -> None:
    from types import SimpleNamespace
    from persistent_local_index.model_profile import ModelProfile, profile_semantic_space
    from vip_fvs import cli

    payload = _v2_base_profile_payload()
    profile_path = tmp_path / "synthetic-model-profile.json"
    profile_path.write_text(json.dumps(payload), encoding="utf-8")
    profile = ModelProfile(**{**payload, "processor_asset_digests": tuple(map(tuple, payload["processor_asset_digests"]))})
    args = SimpleNamespace(
        fake_embedder=True,
        model_profile_json=str(profile_path),
        model_root=None,
        model_identity=None,
        model_revision=None,
        weights_sha256=None,
        pilot_authorization=None,
        output_root=None,
    )

    runtime, authorization = cli._product_runtime(args, index_operation=False)

    assert authorization is None
    assert runtime.fake is True
    assert runtime.semantic_space == profile_semantic_space(profile)
    assert runtime.semantic_space.embedding_dim == 768
    assert runtime.semantic_space != _runtime().semantic_space
    assert runtime.text_embedder(["synthetic query"]).shape == (1, 768)
    assert runtime.image_embedder([tmp_path / "does-not-open-this-path"]).shape == (1, 768)


def test_fake_profile_json_is_rejected_without_explicit_fake_selection(tmp_path: Path) -> None:
    from types import SimpleNamespace
    from vip_fvs import cli

    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(_v2_base_profile_payload()), encoding="utf-8")
    args = SimpleNamespace(
        fake_embedder=False,
        model_profile_json=str(profile_path),
        model_root=None,
        model_identity=None,
        model_revision=None,
        weights_sha256=None,
        pilot_authorization=None,
        output_root=None,
    )

    with pytest.raises(ValueError, match="MODEL_PROFILE_JSON_REQUIRES_EXPLICIT_FAKE_MODE"):
        cli._product_runtime(args, index_operation=False)


def test_query_cli_binds_fake_runtime_to_selected_index_profile(monkeypatch, capsys, tmp_path: Path) -> None:
    import vip_fvs.cli as cli
    import vip_fvs.coordinator as coordinator

    profile_path = tmp_path / "synthetic-profile.json"
    profile_path.write_text(json.dumps(_v2_base_profile_payload()), encoding="utf-8")
    observed = {}

    def query_stub(index_root, query, *, runtime, semantic_space, engine, top_k):
        observed.update(root=Path(index_root), query=query, runtime=runtime,
                        semantic_space=semantic_space, top_k=top_k)
        return {"generation_id": "g", "space_id": "s", "query_count": 1, "hits": []}

    monkeypatch.setattr(coordinator, "query_local_index", query_stub, raising=False)
    assert cli.main([
        "query-local", "--query", "synthetic query", "--index-root", str(tmp_path / "index"),
        "--fake-embedder", "--model-profile-json", str(profile_path),
    ]) == 0
    assert json.loads(capsys.readouterr().out)["space_id"] == "s"
    assert observed["runtime"].fake is True
    assert observed["semantic_space"].text_preprocessing_contract == (
        "vip-v2-siglip2-base-224:text-synthetic:v1"
    )
    assert observed["semantic_space"].embedding_dim == 768


def test_index_and_query_are_separate_and_queries_reuse_generation(tmp_path: Path) -> None:
    import vip_fvs.coordinator as coordinator

    index = getattr(coordinator, "index_local_source", None)
    query = getattr(coordinator, "query_local_index", None)
    assert callable(index), "coordinator must expose index_local_source"
    assert callable(query), "coordinator must expose query_local_index"

    source = tmp_path / "source.mp4"
    source.write_bytes(b"opaque synthetic fixture; fake engine never decodes it")
    root = tmp_path / "index"
    engine = CountingEngine()
    runtime = _runtime()

    indexed = index(source, root, runtime=runtime, semantic_space=runtime.semantic_space,
                    engine=engine)
    assert indexed["generation_id"] == engine.spec.generation_id
    assert indexed["space_id"] == engine.spec.space_id
    assert indexed["indexed"] == 1
    assert len(engine.index_calls) == 1
    assert engine.query_calls == [], "index-local must not query or enter downstream stages"
    assert engine.index_calls[0][0] == source
    assert engine.index_calls[0][3] is runtime.image_embedder

    # Query calls intentionally receive no source path. Repetition is read-only:
    # it must not decode, image-embed, or re-index the source.
    first = query(root, "harbor", runtime=runtime, semantic_space=runtime.semantic_space,
                  engine=engine, top_k=1)
    second = query(root, "harbor", runtime=runtime, semantic_space=runtime.semantic_space,
                   engine=engine, top_k=1)
    assert len(engine.index_calls) == 1
    assert len(engine.query_calls) == 2
    assert all(call[3] is runtime.text_embedder for call in engine.query_calls)
    assert first == second
    for result in (first, second):
        assert result["generation_id"] == engine.spec.generation_id
        assert result["space_id"] == engine.spec.space_id
        assert result["query_count"] == 1
        assert result["hits"][0]["source_sha256"] == "a" * 64
        assert result["hits"][0]["row_id"] == 7
        assert result["hits"][0]["score"] == 0.875
        assert result["hits"][0]["pts"] == 9000


def test_product_summaries_are_compact_deterministic_json(tmp_path: Path) -> None:
    import vip_fvs.coordinator as coordinator

    index = getattr(coordinator, "index_local_source", None)
    query = getattr(coordinator, "query_local_index", None)
    assert callable(index) and callable(query), "separate local index/query API is required"
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic")
    engine = CountingEngine()
    runtime = _runtime()
    indexed = index(source, tmp_path / "index", runtime=runtime,
                    semantic_space=runtime.semantic_space, engine=engine)
    result = query(tmp_path / "index", "harbor", runtime=runtime,
                   semantic_space=runtime.semantic_space, engine=engine, top_k=1)
    # Summaries must be plain JSON-compatible values and stable for equal inputs.
    assert json.dumps(indexed, sort_keys=True, separators=(",", ":"))
    assert json.dumps(result, sort_keys=True, separators=(",", ":"))
    again = query(tmp_path / "index", "harbor", runtime=runtime,
                  semantic_space=runtime.semantic_space, engine=engine, top_k=1)
    assert json.dumps(result, sort_keys=True, separators=(",", ":")) == json.dumps(
        again, sort_keys=True, separators=(",", ":")
    )


def test_coordinator_rejects_semantic_space_mismatch_before_engine_use(tmp_path: Path) -> None:
    import vip_fvs.coordinator as coordinator

    index = getattr(coordinator, "index_local_source", None)
    query = getattr(coordinator, "query_local_index", None)
    assert callable(index), "coordinator must expose index_local_source"
    assert callable(query), "coordinator must expose query_local_index"
    engine = CountingEngine()
    runtime = _runtime()
    other_space = dataclasses.replace(runtime.semantic_space, frozen_revision="other-revision")
    source = tmp_path / "synthetic-source"
    source.write_bytes(b"opaque synthetic bytes")

    with pytest.raises((ValueError, RuntimeError)):
        index(source, tmp_path / "index", runtime=runtime, semantic_space=other_space,
              engine=engine)
    with pytest.raises((ValueError, RuntimeError)):
        query(tmp_path / "index", "harbor", runtime=runtime, semantic_space=other_space,
              engine=engine, top_k=1)
    assert engine.index_calls == []
    assert engine.query_calls == []


def test_index_local_and_query_local_cli_parser_contract() -> None:
    from vip_fvs.cli import _parser

    parser = _parser()
    index_args = parser.parse_args([
        "index-local", "--source", "synthetic.mp4", "--index-root", "index",
        "--fake-embedder",
    ])
    assert index_args.command == "index-local"
    assert index_args.source == "synthetic.mp4"
    assert index_args.fake_embedder is True

    query_args = parser.parse_args([
        "query-local", "--query", "harbor", "--index-root", "index", "--fake-embedder",
    ])
    assert query_args.command == "query-local"
    assert query_args.query == "harbor"
    assert not hasattr(query_args, "source"), "query-local must not require a source path"

    query_multi_args = parser.parse_args([
        "query-multi", "--manifest", "manifest.json", "--index-root", "index",
        "--fake-embedder", "--model-profile-json", "profile.json",
    ])
    assert query_multi_args.model_profile_json == "profile.json"

    with pytest.raises(SystemExit):
        parser.parse_args(["index-local", "--index-root", "index", "--fake-embedder"])


def test_product_cli_fake_dispatch_and_fail_closed_real_mode(monkeypatch, capsys, tmp_path: Path) -> None:
    import vip_fvs.cli as cli
    import vip_fvs.coordinator as coordinator

    runtime = _runtime()
    calls: list[tuple[str, tuple, dict]] = []

    def index_stub(*args, **kwargs):
        calls.append(("index", args, kwargs))
        return {"generation_id": "g", "space_id": "s", "indexed": 1}

    def query_stub(*args, **kwargs):
        calls.append(("query", args, kwargs))
        return {"generation_id": "g", "space_id": "s", "query_count": 1, "hits": []}

    monkeypatch.setattr(coordinator, "index_local_source", index_stub, raising=False)
    monkeypatch.setattr(coordinator, "query_local_index", query_stub, raising=False)
    monkeypatch.setattr(cli, "_fake_runtime", lambda: runtime, raising=False)

    assert cli.main(["index-local", "--source", str(tmp_path / "source"),
                     "--index-root", str(tmp_path / "index"), "--fake-embedder"]) == 0
    first_output = json.loads(capsys.readouterr().out)
    assert first_output["generation_id"] == "g"
    assert calls[-1][0] == "index"
    assert calls[-1][2]["semantic_space"] == runtime.semantic_space

    assert cli.main(["query-local", "--query", "harbor", "--index-root",
                     str(tmp_path / "index"), "--fake-embedder"]) == 0
    second_output = json.loads(capsys.readouterr().out)
    assert second_output["generation_id"] == "g"
    assert calls[-1][0] == "query"
    assert "source" not in calls[-1][2]

    calls.clear()
    assert cli.main(["index-local", "--source", str(tmp_path / "source"),
                     "--index-root", str(tmp_path / "index")]) != 0
    error_output = json.loads(capsys.readouterr().out)
    assert error_output.get("error")
    assert calls == [], "missing real-mode authorization/runtime inputs must fail before dispatch"


def test_existing_cli_commands_remain_parseable() -> None:
    from vip_fvs.cli import _parser

    parser = _parser()
    assert parser.parse_args(["run", "--source", "s", "--query", "q", "--index-root", "i",
                              "--fake-embedder"]).command == "run"
    assert parser.parse_args(["prepare-real", "--source", "s", "--query", "q", "--index-root", "i",
                              "--output-root", "o", "--run-dir", "r", "--source-revision-id", "rev",
                              "--attempt-id", "a", "--pilot-authorization", "auth", "--model-root", "m",
                              "--model-identity", "id", "--model-revision", "r1", "--weights-sha256", "0" * 64,
                              "--probe-executable", "probe", "--source-snapshot-root", "snapshots",
                              "--max-source-bytes", "1024", "--max-store-bytes", "8192"]).command == "prepare-real"
    pilot_args = parser.parse_args(["prepare-real", "--source", "s", "--query", "q", "--index-root", "i",
                                    "--output-root", "o", "--run-dir", "r", "--source-revision-id", "rev",
                                    "--attempt-id", "a", "--pilot-authorization", "auth", "--model-root", "m",
                                    "--model-identity", "id", "--model-revision", "r1", "--weights-sha256", "0" * 64,
                                    "--probe-executable", "probe", "--source-snapshot-root", "snapshots",
                                    "--max-source-bytes", "1024", "--max-store-bytes", "8192",
                                    "--allow-unbounded-local-pilot"])
    assert pilot_args.allow_unbounded_local_pilot is True
    assert parser.parse_args(["prepare-real", "--source", "s", "--query", "q", "--index-root", "i",
                              "--output-root", "o", "--run-dir", "r", "--source-revision-id", "rev",
                              "--attempt-id", "a", "--pilot-authorization", "auth", "--model-root", "m",
                              "--model-identity", "id", "--model-revision", "r1", "--weights-sha256", "0" * 64,
                              "--probe-executable", "probe", "--source-snapshot-root", "snapshots",
                              "--max-source-bytes", "1024", "--max-store-bytes", "8192"]).allow_unbounded_local_pilot is False
    with pytest.raises(SystemExit):
        parser.parse_args(["query-local", "--index-root", "i", "--allow-unbounded-local-pilot"])
    assert parser.parse_args(["resume-real", "--bundle", "b", "--decision", "d", "--output-root", "o",
                              "--run-id", "r", "--attempt-id", "a"]).command == "resume-real"
    assert parser.parse_args(["preview-real", "--plan", "p", "--authorization", "a", "--source", "s",
                              "--output-root", "o", "--ffprobe", "probe", "--ffmpeg", "ffmpeg",
                              "--run-id", "r", "--attempt-id", "a"]).command == "preview-real"

@pytest.mark.parametrize("changes", [
    {"revoked": True},
    {"revoked": 1},
    {"revoked": "false"},
    {"revoked": None},
    {"expires_at": "2000-01-01T00:00:00+00:00"},
    {"expires_at": "not-a-time"},
    {"expires_at": "2999-01-01T00:00:00"},
])
def test_index_local_rejects_revoked_or_invalid_expiry_before_engine_use(tmp_path: Path, changes) -> None:
    from types import SimpleNamespace
    from vip_fvs.local_semantic import checked_runtime
    from vip_fvs.pilot_authorization import PilotAuthorization, PilotAuthorizationError
    import hashlib
    import vip_fvs.coordinator as coordinator

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic authorization fixture")
    index_root, output_root, model_root, runtime_root = (
        tmp_path / name for name in ("index", "output", "model", "runtime")
    )
    contract = SimpleNamespace(model_root=model_root, model_revision="r1", weights_sha256="4" * 64)
    fields = dict(source_path=source, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  purpose="synthetic test", model_root=model_root, model_revision="r1",
                  weights_sha256="4" * 64, runtime_root=runtime_root, index_root=index_root,
                  output_root=output_root, allowed_stages=("decode", "embed", "index"),
                  authorization_id="synthetic-index-auth",
                  source_revision_id="synthetic-source-revision", local_only=True,
                  expires_at="2999-01-01T00:00:00+00:00", revoked=False)
    fields.update(changes)
    if type(fields["revoked"]) is not bool:
        with pytest.raises(PilotAuthorizationError, match="PILOT_AUTHORIZATION_REVOCATION_FLAG_INVALID"):
            PilotAuthorization(**fields)
        return
    if fields["expires_at"] in {"not-a-time", "2999-01-01T00:00:00"}:
        with pytest.raises(PilotAuthorizationError, match="PILOT_AUTHORIZATION_EXPIRY_INVALID"):
            PilotAuthorization(**fields)
        return
    authorization = PilotAuthorization(**fields)
    runtime = checked_runtime(image_embedder=lambda paths: np.ones((len(paths), 2), dtype=np.float32),
                              text_embedder=lambda texts: np.ones((len(texts), 2), dtype=np.float32),
                              semantic_space=_space(), fake=False)
    engine = CountingEngine()
    with pytest.raises(ValueError, match="PILOT_AUTHORIZATION_(REVOKED|EXPIRED|EXPIRY_INVALID)"):
        coordinator.index_local_source(source, index_root, runtime=runtime,
                                       semantic_space=runtime.semantic_space, engine=engine,
                                       pilot_authorization=authorization, model_contract=contract,
                                       output_root=output_root,
                                       source_snapshot_root=tmp_path / "snapshot-store",
                                       max_source_bytes=1024, max_store_bytes=8192)
    assert engine.index_calls == []


@pytest.mark.parametrize("extended", [False, True])
def test_index_local_accepts_valid_extended_and_legacy_authorization(tmp_path: Path, extended: bool) -> None:
    from types import SimpleNamespace
    from datetime import datetime, timedelta, timezone
    from vip_fvs.local_semantic import checked_runtime
    from vip_fvs.pilot_authorization import PilotAuthorization
    import hashlib
    import vip_fvs.coordinator as coordinator

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic authorization fixture")
    index_root, output_root, model_root, runtime_root = (
        tmp_path / name for name in ("index", "output", "model", "runtime")
    )
    runtime = checked_runtime(image_embedder=lambda paths: np.ones((len(paths), 2), dtype=np.float32),
                              text_embedder=lambda texts: np.ones((len(texts), 2), dtype=np.float32),
                              semantic_space=_space(), fake=False)
    contract = SimpleNamespace(model_root=model_root, model_revision="r1", weights_sha256="4" * 64)
    fields = dict(source_path=source, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  purpose="synthetic test", model_root=model_root, model_revision="r1",
                  weights_sha256="4" * 64, runtime_root=runtime_root, index_root=index_root,
                  output_root=output_root, allowed_stages=("decode", "embed", "index"))
    fields.update(
        authorization_id="synthetic-index-auth",
        source_revision_id="synthetic-source-revision",
        local_only=True,
        expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        revoked=False,
    )
    if extended:
        fields.update(
            query_digest="5" * 64,
            semantic_space_id="6" * 64,
            model_identity="synthetic-model",
            index_digest="7" * 64,
            policy_digest="8" * 64,
            scope_digest="9" * 64,
        )
    engine = CountingEngine()
    result = coordinator.index_local_source(
        source, index_root, runtime=runtime, semantic_space=runtime.semantic_space, engine=engine,
        pilot_authorization=PilotAuthorization(**fields), model_contract=contract, output_root=output_root,
        source_snapshot_root=tmp_path / "snapshot-store", max_source_bytes=1024, max_store_bytes=8192,
    )
    assert result["indexed"] == 1
    assert len(engine.index_calls) == 1


@pytest.mark.parametrize("changes", [
    {"revoked": True},
    {"revoked": 1},
    {"revoked": "false"},
    {"revoked": None},
    {"expires_at": "2000-01-01T00:00:00+00:00"},
])
def test_index_local_cli_rejects_revoked_or_expired_before_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, changes,
) -> None:
    import hashlib
    from types import SimpleNamespace
    from vip_fvs import cli
    from vip_fvs.pilot_authorization import PilotAuthorization

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic authorization fixture")
    index_root, output_root, model_root, runtime_root = (
        tmp_path / name for name in ("index", "output", "model", "runtime")
    )
    authorization_fields = dict(
        source_path=source.resolve(),
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        purpose="synthetic test", model_root=model_root.resolve(),
        model_revision="r1", weights_sha256="4" * 64,
        runtime_root=runtime_root.resolve(), index_root=index_root.resolve(),
        output_root=output_root.resolve(), allowed_stages=("decode", "embed", "index"),
        authorization_id="synthetic-index-auth",
        source_revision_id="synthetic-source-revision", local_only=True,
        expires_at="2999-01-01T00:00:00+00:00", revoked=False,
    )
    authorization_fields.update(changes)
    if type(authorization_fields["revoked"]) is not bool:
        with pytest.raises(ValueError, match="PILOT_AUTHORIZATION_REVOCATION_FLAG_INVALID"):
            PilotAuthorization(**authorization_fields)
        return
    authorization = PilotAuthorization(**authorization_fields)
    monkeypatch.setattr(
        "vip_fvs.coordinator.load_index_local_authorization",
        lambda _path: authorization,
    )
    monkeypatch.setattr(cli, "_real_runtime", lambda _args: pytest.fail("runtime opened before lifecycle validation"))
    args = SimpleNamespace(
        source=str(source), index_root=str(index_root), output_root=str(output_root),
        pilot_authorization=str(tmp_path / "owner.json"), model_root=str(model_root),
        model_identity="fixture-model", model_revision="r1", weights_sha256="4" * 64,
        device="cpu", fake_embedder=False,
        source_snapshot_root=str(tmp_path / "snapshot-store"),
        max_source_bytes=1024, max_store_bytes=8192,
    )
    with pytest.raises(ValueError, match="INDEX_LOCAL_AUTHORIZATION_INVALID:PILOT_AUTHORIZATION_(REVOKED|EXPIRED|REVOCATION_FLAG_INVALID)"):
        cli._product_runtime(args, index_operation=True)


def _write_extended_authorization(path: Path, source: Path, *, revoked) -> None:
    """Write a digest-correct envelope so tests exercise the production JSON loader."""
    import hashlib
    from vip_fvs.pilot_authorization import _FIELDS, _PREPARE_FIELDS

    record = {
        "source_path": str(source.resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "purpose": "synthetic test", "model_root": str((path.parent / "model").resolve()),
        "model_revision": "r1", "weights_sha256": "4" * 64,
        "runtime_root": str((path.parent / "runtime").resolve()),
        "index_root": str((path.parent / "index").resolve()),
        "output_root": str((path.parent / "output").resolve()),
        "allowed_stages": ["decode", "embed", "index"],
        "authorization_id": "fixture-auth", "source_revision_id": "fixture-revision",
        "query_digest": "1" * 64, "semantic_space_id": "fixture-space", "model_identity": "fixture-model",
        "index_digest": "2" * 64, "local_only": True,
        "expires_at": "2999-01-01T00:00:00+00:00", "revoked": revoked,
        "selected_stream_index": 0, "policy_digest": "3" * 64, "scope_digest": "5" * 64,
    }
    assert set(record) | {"record_digest"} == _FIELDS | _PREPARE_FIELDS
    body = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    record["record_digest"] = hashlib.sha256(body.encode()).hexdigest()
    path.write_text(json.dumps(record), encoding="utf-8")


@pytest.mark.parametrize("revoked", [None, 0])
def test_json_loader_rejects_falsey_non_boolean_revocation_before_cli_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, revoked,
) -> None:
    from types import SimpleNamespace
    from vip_fvs import cli

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic authorization fixture")
    auth_path = tmp_path / "owner.json"
    _write_extended_authorization(auth_path, source, revoked=revoked)
    monkeypatch.setattr(cli, "_real_runtime", lambda _args: pytest.fail("runtime opened before loader validation"))
    args = SimpleNamespace(
        source=str(source), index_root=str(tmp_path / "index"), output_root=str(tmp_path / "output"),
        pilot_authorization=str(auth_path), model_root=str(tmp_path / "model"),
        model_identity="fixture-model", model_revision="r1", weights_sha256="4" * 64,
        device="cpu", fake_embedder=False,
    )
    with pytest.raises(ValueError, match="INDEX_LOCAL_AUTHORIZATION_INVALID:PILOT_AUTHORIZATION_REVOKED_FLAG_INVALID"):
        cli._product_runtime(args, index_operation=True)


@pytest.mark.parametrize("revoked", [None, 0])
def test_json_loader_rejects_falsey_non_boolean_revocation_before_coordinator_engine(
    tmp_path: Path, revoked,
) -> None:
    from types import SimpleNamespace
    from vip_fvs.local_semantic import checked_runtime
    import vip_fvs.coordinator as coordinator

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic authorization fixture")
    auth_path = tmp_path / "owner.json"
    _write_extended_authorization(auth_path, source, revoked=revoked)
    runtime = checked_runtime(
        image_embedder=lambda paths: np.ones((len(paths), 2), dtype=np.float32),
        text_embedder=lambda texts: np.ones((len(texts), 2), dtype=np.float32),
        semantic_space=_space(), fake=False,
    )
    engine = CountingEngine()
    with pytest.raises(ValueError, match="PILOT_AUTHORIZATION_REVOKED_FLAG_INVALID"):
        coordinator.index_local_source(
            source, tmp_path / "index", runtime=runtime, semantic_space=runtime.semantic_space,
            engine=engine, pilot_authorization=auth_path,
            model_contract=SimpleNamespace(model_root=tmp_path / "model", model_revision="r1",
                                           weights_sha256="4" * 64),
            output_root=tmp_path / "output",
        )
    assert engine.index_calls == []


def test_index_local_loader_uses_pinned_authorization_when_path_is_replaced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from vip_fvs import coordinator
    from vip_fvs.pilot_authorization import load_pilot_authorization as shared_loader

    source_a = tmp_path / "source-a.mp4"
    source_b = tmp_path / "source-b.mp4"
    source_a.write_bytes(b"authorization A")
    source_b.write_bytes(b"authorization B")
    auth_path = tmp_path / "owner.json"
    replacement = tmp_path / "replacement.json"
    _write_extended_authorization(auth_path, source_a, revoked=False)
    _write_extended_authorization(replacement, source_b, revoked=False)
    received_paths = []

    def replace_then_load(pinned_path):
        received_paths.append(Path(pinned_path))
        auth_path.unlink()
        replacement.rename(auth_path)
        return shared_loader(pinned_path)

    monkeypatch.setattr(coordinator, "load_pilot_authorization", replace_then_load)
    loaded = coordinator.load_index_local_authorization(auth_path)

    assert loaded.source_path == source_a.resolve()
    assert len(received_paths) == 1
    assert str(received_paths[0]).startswith("/dev/fd/")
