"""V4 RED contract: owner authorization is checked before model acquisition.

These tests intentionally patch ``_real_runtime`` with a trap. A failing
authorization must be rejected before the trap is entered; a valid owner
authorization must enter it. The production CLI does not yet implement this
ordering, so the negative cases are expected to remain RED until V4 lands.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from vip_fvs import cli


class RuntimeReached(RuntimeError):
    """Sentinel proving that authorization was not evaluated first."""


def _owner(tmp_path: Path, source: Path, **overrides: object) -> SimpleNamespace:
    index = tmp_path / "index"
    output = tmp_path / "out"
    model = tmp_path / "model"
    runtime_root = tmp_path / "runtime"
    query = "target phrase"
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    values: dict[str, object] = {
        "authorization_id": "owner-v4", "source_path": source.resolve(), "source_sha256": source_digest,
        "source_revision_id": "revision-v4", "purpose": "REAL_SOURCE_PREPARATION",
        "model_root": model.resolve(), "model_identity": "model-v4", "model_revision": "weights-v4",
        "weights_sha256": "a" * 64, "runtime_root": runtime_root.resolve(), "index_root": index.resolve(),
        "index_digest": hashlib.sha256(json.dumps(str(index.resolve()), separators=(",", ":")).encode()).hexdigest(),
        "output_root": output.resolve(), "allowed_stages": ("decode", "embed", "index", "probe", "retrieve", "refine"),
        "query_digest": hashlib.sha256(json.dumps(query, separators=(",", ":")).encode()).hexdigest(),
        "semantic_space_id": "space-v4", "local_only": True, "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": False, "selected_stream_index": 0, "policy_digest": "b" * 64,
        "scope_digest": "c" * 64, "record_digest": "d" * 64,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _args(tmp_path: Path, source: Path) -> SimpleNamespace:
    return SimpleNamespace(
        source=str(source), query="target phrase", index_root=str(tmp_path / "index"),
        output_root=str(tmp_path / "out"), run_dir=str(tmp_path / "run"), source_revision_id="revision-v4",
        attempt_id="attempt-v4", pilot_authorization=str(tmp_path / "owner.json"),
        model_root=str(tmp_path / "model"), model_identity="model-v4", model_revision="weights-v4",
        weights_sha256="a" * 64, selected_stream_index=0, probe_executable="/usr/bin/ffprobe", device="cpu",
        source_snapshot_root=str(tmp_path / "private-snapshots"),
        max_source_bytes=1024, max_store_bytes=8192,
    )


@pytest.fixture
def auth_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"generated V4 source")
    args = _args(tmp_path, source)
    owner = _owner(tmp_path, source)
    monkeypatch.setattr("vip_fvs.pilot_authorization.load_pilot_authorization", lambda _path: owner)
    return args, owner


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("source_path", Path("/other/source.mp4"), "SOURCE_PATH_MISMATCH"),
        ("source_revision_id", "revision-other", "SOURCE_REVISION_ID_MISMATCH"),
        ("query_digest", "0" * 64, "QUERY_DIGEST_MISMATCH"),
        ("model_identity", "other-model", "MODEL_IDENTITY_MISMATCH"),
        ("model_root", Path("/other/model"), "MODEL_ROOT_MISMATCH"),
        ("model_revision", "revision-other", "MODEL_REVISION_MISMATCH"),
        ("weights_sha256", "e" * 64, "WEIGHTS_DIGEST_MISMATCH"),
        ("index_root", Path("/other/index"), "INDEX_ROOT_MISMATCH"),
        ("output_root", Path("/other/output"), "OUTPUT_ROOT_MISMATCH"),
    ],
)
def test_scope_mismatch_is_rejected_before_real_runtime(
    auth_boundary, monkeypatch: pytest.MonkeyPatch, field: str, value: object, reason: str
) -> None:
    args, owner = auth_boundary
    setattr(owner, field, value)
    monkeypatch.setattr(cli, "_real_runtime", lambda _args: pytest.fail("_real_runtime reached"))
    with pytest.raises(SystemExit, match=reason):
        cli._prepare_real(args)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("expires_at", "2000-01-01T00:00:00+00:00", "EXPIRED"),
        ("revoked", True, "REVOKED"),
        ("allowed_stages", ("probe",), "OPERATION_SCOPE"),
    ],
)
def test_expiry_revocation_and_operation_scope_fail_before_real_runtime(
    auth_boundary, monkeypatch: pytest.MonkeyPatch, field: str, value: object, reason: str
) -> None:
    args, owner = auth_boundary
    setattr(owner, field, value)
    monkeypatch.setattr(cli, "_real_runtime", lambda _args: pytest.fail("_real_runtime reached"))
    with pytest.raises(SystemExit, match=reason):
        cli._prepare_real(args)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [("expires_at", "not-a-timestamp", "EXPIRY_INVALID"), ("local_only", False, "LOCAL_ONLY_REQUIRED"),
     ("selected_stream_index", 2, "STREAM_SCOPE")],
)
def test_malformed_locality_and_stream_scope_fail_before_real_runtime(
    auth_boundary, monkeypatch: pytest.MonkeyPatch, field: str, value: object, reason: str
) -> None:
    args, owner = auth_boundary
    setattr(owner, field, value)
    monkeypatch.setattr(cli, "_real_runtime", lambda _args: pytest.fail("_real_runtime reached"))
    with pytest.raises(SystemExit, match=reason):
        cli._prepare_real(args)


def test_valid_owner_authorization_reaches_real_runtime(auth_boundary, monkeypatch: pytest.MonkeyPatch) -> None:
    args, _owner_record = auth_boundary
    monkeypatch.setattr(cli, "_real_runtime", lambda _args: (_ for _ in ()).throw(RuntimeReached()))
    with pytest.raises(RuntimeReached):
        cli._prepare_real(args)
