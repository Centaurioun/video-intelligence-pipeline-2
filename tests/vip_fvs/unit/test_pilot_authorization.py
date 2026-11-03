"""RED-first tests for the exact developer-local pilot authorization boundary.

These tests deliberately exercise the contract before its implementation is
present.  Real mode must validate the owner-supplied authorization envelope
before opening a model, decoding media, or mutating a persistent index.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from vip_fvs import coordinator, local_semantic, pilot_authorization


def test_authorization_schema_rejects_partial_v2_extension(tmp_path: Path) -> None:
    schema_path = Path(__file__).resolve().parents[3] / "schemas" / "vip_fvs" / "pilot_authorization.v2.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    path, legacy = _write_authorization(tmp_path)
    assert validator.is_valid(legacy)
    assert pilot_authorization.load_pilot_authorization(path)

    partial_v2 = {**legacy, "schema_version": "vip_fvs.pilot_authorization.v2"}
    path.write_text(json.dumps(partial_v2), encoding="utf-8")
    assert not validator.is_valid(partial_v2)
    with pytest.raises(pilot_authorization.PilotAuthorizationError, match="SCHEMA_INVALID"):
        pilot_authorization.load_pilot_authorization(path)


@pytest.mark.parametrize(("field", "value", "reason"), [
    ("authorization_id", 7, "AUTHORIZATION_ID_INVALID"),
    ("source_revision_id", [], "SOURCE_REVISION_ID_INVALID"),
    ("model_identity", {"nested": True}, "MODEL_IDENTITY_INVALID"),
    ("semantic_space_id", False, "SEMANTIC_SPACE_ID_INVALID"),
    ("selected_stream_index", 1.5, "STREAM_INVALID"),
    ("source_revision_id", " ", "SOURCE_REVISION_ID_INVALID"),
    ("expires_at", "not-a-date", "EXPIRY_INVALID"),
    ("expires_at", "2099-01-01T00:00+00:00", "EXPIRY_INVALID"),
])
def test_prepare_authorization_parser_rejects_schema_invalid_field_types(
    tmp_path: Path, field: str, value: object, reason: str,
) -> None:
    payload = _authorization_payload(tmp_path)
    payload.update({
        "authorization_id": "auth:type-check", "source_revision_id": "revision:type-check",
        "query_digest": "1" * 64, "semantic_space_id": "2" * 64,
        "model_identity": "model:type-check", "index_digest": "3" * 64,
        "local_only": True, "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": False, "selected_stream_index": 0,
        "policy_digest": "4" * 64, "scope_digest": "5" * 64,
    })
    payload[field] = value
    payload["record_digest"] = hashlib.sha256(
        json.dumps({key: item for key, item in payload.items() if key != "record_digest"},
                   sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    schema_path = Path(__file__).resolve().parents[3] / "schemas" / "vip_fvs" / "pilot_authorization.v2.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert not Draft202012Validator(schema, format_checker=FormatChecker()).is_valid(payload)
    path = tmp_path / "typed-authorization.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(pilot_authorization.PilotAuthorizationError, match=reason):
        pilot_authorization.load_pilot_authorization(path)


def _authorization_payload(tmp_path: Path, *, source: Path | None = None) -> dict[str, object]:
    source = source or (tmp_path / "developer.mp4")
    source.write_bytes(b"synthetic developer-local source")
    model_root = tmp_path / "model"
    index_root = tmp_path / "index"
    output_root = tmp_path / "output"
    return {
        "source_path": str(source.resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "purpose": "bounded developer-local semantic retrieval pilot",
        "model_root": str(model_root.resolve()),
        "model_revision": "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
        "weights_sha256": "2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8",
        "runtime_root": str((tmp_path / "runtime").resolve()),
        "index_root": str(index_root.resolve()),
        "output_root": str(output_root.resolve()),
        "allowed_stages": ["decode", "thumbnail", "embed", "index", "query"],
    }


def _write_authorization(tmp_path: Path, **changes: object) -> tuple[Path, dict[str, object]]:
    payload = _authorization_payload(tmp_path)
    payload.update(changes)
    path = tmp_path / "pilot-authorization.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path, payload


def _model_contract(payload: dict[str, object]) -> SimpleNamespace:
    return SimpleNamespace(
        model_root=Path(str(payload["model_root"])),
        model_revision=str(payload["model_revision"]),
        weights_sha256=str(payload["weights_sha256"]),
    )


def _processing_spies(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []
    monkeypatch.setattr(
        local_semantic,
        "build_local_semantic_runtime",
        lambda *args, **kwargs: calls.append("model")
        or SimpleNamespace(),
    )
    monkeypatch.setattr(
        coordinator,
        "decode_source",
        lambda *args, **kwargs: calls.append("decode"),
        raising=False,
    )
    monkeypatch.setattr(
        coordinator,
        "index_inputs",
        lambda *args, **kwargs: calls.append("index"),
        raising=False,
    )
    return calls


def test_missing_authorization_stops_before_processing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls = _processing_spies(monkeypatch)

    with pytest.raises(ValueError, match="REAL_MEDIA_AUTHORIZATION_REQUIRED"):
        coordinator.run_vertical_slice(
            tmp_path / "developer.mp4",
            "query",
            tmp_path / "index",
            fake_embedder=False,
            local_semantic_config=SimpleNamespace(),
            pilot_authorization=None,
        )

    assert calls == []


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("source_sha256", "0" * 64),
        ("model_root", "/different/absolute/model-root"),
        ("model_revision", "different-frozen-revision"),
        ("weights_sha256", "1" * 64),
        ("index_root", "/different/absolute/index-root"),
        ("output_root", "/different/absolute/output-root"),
    ],
)
def test_mismatched_exact_authorization_field_stops_before_processing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    field: str,
    replacement: object,
) -> None:
    expected = _authorization_payload(tmp_path)
    authorization_path, payload = _write_authorization(tmp_path, **{field: replacement})
    authorization = pilot_authorization.load_pilot_authorization(authorization_path)
    calls = _processing_spies(monkeypatch)

    with pytest.raises(ValueError):
        pilot_authorization.require_pilot_authorization(
            authorization,
            source_path=Path(str(expected["source_path"])),
            model_contract=_model_contract(expected),
            index_root=Path(str(expected["index_root"])),
            output_root=Path(str(expected["output_root"])),
        )

    assert calls == []


def test_valid_but_mismatched_source_path_reaches_requirement_check(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    expected = _authorization_payload(tmp_path)
    alternate_source = tmp_path / "other-developer-file.mp4"
    alternate_source.write_bytes(b"another synthetic developer-local source")
    authorization_path, _ = _write_authorization(
        tmp_path, source_path=str(alternate_source.resolve())
    )
    calls = _processing_spies(monkeypatch)

    authorization = pilot_authorization.load_pilot_authorization(authorization_path)
    with pytest.raises(ValueError, match="SOURCE_PATH_MISMATCH"):
        pilot_authorization.require_pilot_authorization(
            authorization,
            source_path=Path(str(expected["source_path"])),
            model_contract=_model_contract(expected),
            index_root=Path(str(expected["index_root"])),
            output_root=Path(str(expected["output_root"])),
        )

    assert calls == []


def test_non_source_scope_failure_happens_before_source_content_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = _authorization_payload(tmp_path)
    authorization_path, _ = _write_authorization(tmp_path)
    authorization = pilot_authorization.load_pilot_authorization(authorization_path)
    hash_calls: list[Path] = []

    def source_hash(path: Path) -> str:
        hash_calls.append(path)
        raise AssertionError("source content opened before scope validation")

    monkeypatch.setattr(pilot_authorization, "_sha256", source_hash)
    wrong_contract = _model_contract(payload)
    wrong_contract.weights_sha256 = "0" * 64

    with pytest.raises(ValueError, match="WEIGHTS_DIGEST_MISMATCH"):
        pilot_authorization.require_pilot_authorization(
            authorization,
            source_path=Path(str(payload["source_path"])),
            model_contract=wrong_contract,
            index_root=Path(str(payload["index_root"])),
            output_root=Path(str(payload["output_root"])),
        )

    assert hash_calls == []


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"revoked": True}, "PILOT_AUTHORIZATION_REVOKED"),
        ({"expires_at": "2000-01-01T00:00:00+00:00"}, "PILOT_AUTHORIZATION_EXPIRED"),
    ],
)
def test_revoked_or_expired_authorization_fails_before_source_content_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, changes: dict[str, object], reason: str
) -> None:
    payload = _authorization_payload(tmp_path)
    payload.update({
        "schema_version": "vip_fvs.pilot_authorization.v2",
        "authorization_id": "auth:lifecycle-test", "source_revision_id": "revision:lifecycle-test",
        "query_digest": "1" * 64, "semantic_space_id": "2" * 64,
        "model_identity": "model:lifecycle-test", "index_digest": "3" * 64,
        "local_only": True, "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": False, "selected_stream_index": 0,
        "policy_digest": "4" * 64, "scope_digest": "5" * 64,
        "corpus_separation_ref": {
            "schema_version": "vip_fvs.corpus_separation_ref.v1",
            "artifact_id": "synthetic:untrusted-evidence",
            "artifact_schema_version": "vip_fvs.corpus_separation_evidence.v1",
            "canonical_content_sha256": "6" * 64,
            "authorized_root_id": "synthetic-root",
            "issuer_policy_ref": "synthetic-policy:v1",
        },
        "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
    })
    payload.update(changes)
    payload["record_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    path = tmp_path / "auth.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    authorization = pilot_authorization.load_pilot_authorization(path)
    monkeypatch.setattr(
        pilot_authorization, "_sha256",
        lambda _path: pytest.fail("source content opened before lifecycle rejection"),
    )
    with pytest.raises(ValueError, match=reason):
        pilot_authorization.require_pilot_authorization(
            authorization, source_path=Path(str(payload["source_path"])),
            model_contract=_model_contract(payload), index_root=Path(str(payload["index_root"])),
            output_root=Path(str(payload["output_root"])),
        )


def test_index_local_snapshot_binding_is_checked_before_source_content_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = _authorization_payload(tmp_path)
    path, _ = _write_authorization(tmp_path)
    authorization = pilot_authorization.load_pilot_authorization(path)
    monkeypatch.setattr(
        pilot_authorization, "_sha256",
        lambda _path: pytest.fail("source content opened before snapshot binding validation"),
    )

    with pytest.raises(ValueError, match="SNAPSHOT_BINDING_REQUIRED"):
        coordinator.require_index_local_authorization(
            authorization,
            source_path=Path(str(payload["source_path"])),
            model_contract=_model_contract(payload),
            index_root=Path(str(payload["index_root"])),
            output_root=Path(str(payload["output_root"])),
        )


def test_extended_authorization_rejects_coerced_revocation_flag_at_load(tmp_path: Path) -> None:
    payload = _authorization_payload(tmp_path)
    payload.update({
        "authorization_id": "auth:strict-revocation",
        "source_revision_id": "revision:strict-revocation",
        "query_digest": "1" * 64,
        "semantic_space_id": "2" * 64,
        "model_identity": "model:strict-revocation",
        "index_digest": "3" * 64,
        "local_only": True,
        "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": 0,
        "selected_stream_index": 0,
        "policy_digest": "4" * 64,
        "scope_digest": "5" * 64,
        "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
    })
    payload["record_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    path = tmp_path / "invalid-revocation.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="REVOCATION_FLAG_INVALID"):
        pilot_authorization.load_pilot_authorization(path)


@pytest.mark.parametrize("missing", [
    "source_path",
    "source_sha256",
    "purpose",
    "model_root",
    "model_revision",
    "weights_sha256",
    "runtime_root",
    "index_root",
    "output_root",
    "allowed_stages",
])
def test_missing_exact_authorization_field_is_rejected(tmp_path: Path, missing: str) -> None:
    payload = _authorization_payload(tmp_path)
    payload.pop(missing)
    path = tmp_path / "missing-field.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="AUTHORIZATION"):
        pilot_authorization.load_pilot_authorization(path)


def test_relative_source_path_is_rejected_at_load_before_processing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = _processing_spies(monkeypatch)
    authorization_path, _ = _write_authorization(tmp_path, source_path="developer.mp4")

    with pytest.raises(ValueError, match="SOURCE_PATH_MUST_BE_ABSOLUTE"):
        pilot_authorization.load_pilot_authorization(authorization_path)

    assert calls == []


def test_missing_required_stage_is_rejected_at_load_before_processing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = _processing_spies(monkeypatch)
    authorization_path, _ = _write_authorization(
        tmp_path, allowed_stages=["decode", "thumbnail", "query"]
    )

    with pytest.raises(ValueError, match="REQUIRED_STAGE_ABSENT"):
        pilot_authorization.load_pilot_authorization(authorization_path)

    assert calls == []


def test_directory_source_artifact_is_rejected_at_load_before_processing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source_dir = tmp_path / "developer-media"
    source_dir.mkdir()
    authorization_path, _ = _write_authorization(tmp_path, source_path=str(source_dir.resolve()))
    calls = _processing_spies(monkeypatch)

    with pytest.raises(ValueError, match="SOURCE_NOT_REGULAR_FILE"):
        pilot_authorization.load_pilot_authorization(authorization_path)

    assert calls == []


def test_opt_in_corpus_separation_reference_is_validated_and_legacy_omission_remains_valid(tmp_path: Path) -> None:
    legacy_path, _ = _write_authorization(tmp_path)
    assert pilot_authorization.load_pilot_authorization(legacy_path).corpus_separation_ref is None

    payload = _authorization_payload(tmp_path)
    payload.update({
        "schema_version": "vip_fvs.pilot_authorization.v2",
        "authorization_id": "auth:corpus-test", "source_revision_id": "synthetic:candidate",
        "query_digest": "1" * 64, "semantic_space_id": "2" * 64,
        "model_identity": "model:synthetic", "index_digest": "3" * 64,
        "local_only": True, "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": False, "selected_stream_index": 0,
        "policy_digest": "4" * 64, "scope_digest": "5" * 64,
        "allowed_stages": ["decode", "embed", "index"],
        "corpus_separation_ref": {
            "schema_version": "vip_fvs.corpus_separation_ref.v1", "artifact_id": "synthetic:evidence",
            "artifact_schema_version": "vip_fvs.corpus_separation_evidence.v1",
            "canonical_content_sha256": "a" * 64, "authorized_root_id": "synthetic-root",
            "issuer_policy_ref": "synthetic-policy:v1",
        },
    })
    payload["record_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    path = tmp_path / "auth-with-corpus-ref.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    authorization = pilot_authorization.load_pilot_authorization(path)
    assert authorization.corpus_separation_ref == payload["corpus_separation_ref"]

    payload["corpus_separation_ref"] = {**payload["corpus_separation_ref"], "unexpected": True}
    payload["record_digest"] = hashlib.sha256(
        json.dumps({k: v for k, v in payload.items() if k != "record_digest"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="DECLARATION_INVALID"):
        pilot_authorization.load_pilot_authorization(path)


def test_pilot_authorization_duplicate_json_key_refuses(tmp_path: Path) -> None:
    payload = _authorization_payload(tmp_path)
    encoded = json.dumps(payload)
    encoded = encoded.replace('"source_sha256":', '"source_sha256":"' + "0" * 64 + '","source_sha256":', 1)
    path = tmp_path / "duplicate-key.json"
    path.write_text(encoded, encoding="utf-8")
    with pytest.raises(ValueError, match="PILOT_AUTHORIZATION_SCHEMA_INVALID"):
        pilot_authorization.load_pilot_authorization(path)
