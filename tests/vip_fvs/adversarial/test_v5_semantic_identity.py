"""V5 RED contracts for semantic-space and retrieval-generation identity binding."""
from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
from types import SimpleNamespace

from persistent_local_index.model_space import semantic_space_id
from persistent_local_index.model_space import build_generation_spec
from vip_fvs.pilot_authorization import PilotAuthorizationError, require_prepare_authorization
from vip_fvs.review_bundle import ReviewBundle
from vip_fvs.real_source_service import RealSourceRequest, _validate_prepare_authorization


def _source(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "generated-v5-source.mp4"
    path.write_bytes(b"generated V5 fixture; never archive media")
    return path


def _runtime_space():
    from vip_fvs.retrieval_adapter import fake_semantic_space

    return fake_semantic_space()


def _request(tmp_path: Path, space, *, semantic_id: str | None = None) -> RealSourceRequest:
    source = _source(tmp_path)
    index_root = tmp_path / "index"
    output_root = tmp_path / "out"
    query = "target phrase"
    auth = {
        "authorization_id": "auth:generated-v5",
        "source_path": str(source.resolve()),
        "source_revision_id": "generated-v5-rev",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "purpose": "generated synthetic authorization-order fixture",
        "model_root": str((tmp_path / "model").resolve()),
        "model_revision": space.frozen_revision,
        "weights_sha256": space.weights_sha256,
        "runtime_root": str((tmp_path / "runtime").resolve()),
        "query_digest": hashlib.sha256(json.dumps(query, separators=(",", ":")).encode()).hexdigest(),
        "index_root": str(index_root.resolve()),
        "index_digest": hashlib.sha256(json.dumps(str(index_root.resolve()), separators=(",", ":")).encode()).hexdigest(),
        "output_root": str(output_root.resolve()),
        "local_only": True,
        "model_identity": space.model_identity,
        "model_revision": space.frozen_revision,
        "weights_sha256": space.weights_sha256,
        "semantic_space_id": semantic_id if semantic_id is not None else semantic_space_id(space),
        "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
        "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": False,
        "selected_stream_index": 0,
        "policy_digest": "4" * 64,
        "scope_digest": "5" * 64,
    }
    auth["record_digest"] = hashlib.sha256(
        json.dumps(auth, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return RealSourceRequest(
        source_path=source,
        query=query,
        authorization=auth,
        runtime=type("Runtime", (), {"semantic_space": space})(),
        index_root=index_root,
        output_root=output_root,
        run_dir=tmp_path / "run",
        source_revision_id="generated-v5-rev",
        attempt_id="attempt-v5",
        model_root=tmp_path / "model",
    )


def test_semantic_space_id_changes_when_processor_identity_changes():
    original = _runtime_space()
    changed = replace(original, processor_digest="1" * 64)
    assert semantic_space_id(original) != semantic_space_id(changed)


def test_service_rejects_same_model_with_different_semantic_space(tmp_path: Path):
    space_a = _runtime_space()
    space_b = replace(space_a, processor_digest="1" * 64)
    request = _request(tmp_path, space_b, semantic_id=semantic_space_id(space_a))
    with pytest.raises(Exception, match="SEMANTIC_SPACE_ID_MISMATCH"):
        _validate_prepare_authorization(request, request.source_path)


def test_service_rejects_revision_alias_and_accepts_canonical_id(tmp_path: Path):
    space = _runtime_space()
    revision_alias = _request(tmp_path / "alias", space, semantic_id=space.frozen_revision)
    with pytest.raises(Exception, match="SEMANTIC_SPACE_ID_MISMATCH"):
        _validate_prepare_authorization(revision_alias, revision_alias.source_path)

    canonical = _request(tmp_path / "canonical", space, semantic_id=semantic_space_id(space))
    _validate_prepare_authorization(canonical, canonical.source_path)


def test_post_runtime_owner_check_requires_canonical_semantic_space_id(tmp_path: Path):
    space = _runtime_space()
    request = _request(tmp_path, space)
    values = dict(request.authorization)
    values["source_path"] = request.source_path
    values["model_root"] = tmp_path / "model"
    values["runtime_root"] = tmp_path / "runtime"
    values["index_root"] = request.index_root
    values["output_root"] = request.output_root
    values.update(
        authorization_id="auth-v5", record_digest="record", policy_digest="1" * 64,
        scope_digest="2" * 64, index_digest=values["index_digest"],
    )
    auth = SimpleNamespace(**values)
    common = dict(
        authorization=auth, source_path=request.source_path, source_revision_id=request.source_revision_id,
        query=request.query, model_root=tmp_path / "model", model_identity=space.model_identity,
        model_revision=space.frozen_revision, weights_sha256=space.weights_sha256,
        index_root=request.index_root, output_root=request.output_root,
    )
    with pytest.raises(PilotAuthorizationError, match="SEMANTIC_SPACE_ID_MISMATCH"):
        require_prepare_authorization(**common, semantic_space_id=space.frozen_revision)
    require_prepare_authorization(**common, semantic_space_id=semantic_space_id(space))


def test_preprocessing_identity_changes_review_bundle_dependency_identity(tmp_path: Path):
    from tests.vip_fvs.unit.test_review_bundle import payload_with_e01_artifact

    space_a = _runtime_space()
    space_b = replace(space_a, processor_digest="1" * 64)
    generation_a = build_generation_spec(space_a)
    generation_b = build_generation_spec(space_b)

    payload_a = payload_with_e01_artifact(tmp_path / "space-a")
    payload_a["generation"].update(
        semantic_space_id=generation_a.space_id,
        generation_id=generation_a.generation_id,
    )
    payload_b = payload_with_e01_artifact(tmp_path / "space-b")
    payload_b["generation"].update(
        semantic_space_id=generation_b.space_id,
        generation_id=generation_b.generation_id,
    )
    bundle_a = ReviewBundle.create(payload_a, run_id="run-a", bundle_id="bundle-a", created_at="2026-09-21T12:00:00Z")
    bundle_b = ReviewBundle.create(payload_b, run_id="run-b", bundle_id="bundle-b", created_at="2026-09-21T12:00:00Z")

    assert generation_a.space_id != generation_b.space_id
    assert bundle_a.dependency_digest != bundle_b.dependency_digest
