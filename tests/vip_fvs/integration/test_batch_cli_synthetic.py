"""CLI integration and refusal tests for Workstreams W6 and W7 (`query-batch-synthetic`, `query-three-arm-synthetic`)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import pytest

from persistent_local_index import storage
from persistent_local_index.model_space import GenerationSpec, build_generation_spec
from vip_fvs import cli, coordinator
from vip_fvs.batch_report import (
    BENCHMARK_STATUS_NOT_RUN,
    GATE_DECISION_NOT_AUTHORIZED,
    KIND_SINGLE_ARM,
    KIND_THREE_ARM,
    MODEL_EVIDENCE_NOT_OBSERVED,
    REPORT_STATUS_SYNTHETIC_ONLY,
    verify_batch_report,
)
from vip_fvs.local_semantic import CheckedLocalSemanticRuntime
from vip_fvs.query_batch import MAX_TOP_K, QUERY_CATALOG_SCHEMA_VERSION
from vip_fvs.source_adapter import (
    MultiSourceManifest,
    SourceManifestEntry,
    save_multi_source_manifest,
)
from vip_fvs.synthetic_profiles import (
    CLOSED_SYNTHETIC_PROFILE_IDS,
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
    build_synthetic_profile_runtime,
    make_synthetic_profile,
    make_synthetic_profile_payload,
)
from vip_fvs.three_arm_batch import (
    ARM_VIP_V1_BASE,
    ARM_VIP_V2_BASE,
    ARM_VIP_V2_SO400M,
    DECLARED_ARM_ORDER,
    THREE_ARM_MAP_SCHEMA_VERSION,
)


def _write_catalog(tmp_path: Path, queries: Sequence[tuple[str, str]] | None = None) -> Path:
    rows = queries or (
        ("q-001", "a dancer landing from a grand jeté"),
        ("q-002", "a close-up of an orchestra conductor"),
    )
    payload = {
        "schema_version": QUERY_CATALOG_SCHEMA_VERSION,
        "catalog_id": "cli-synthetic-catalog-01",
        "queries": [{"query_id": qid, "text": text} for qid, text in rows],
    }
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _build_manifest(path: Path, *, revision: str, content: str, digest: str) -> MultiSourceManifest:
    entry = SourceManifestEntry(
        revision_id=revision,
        content_id=content,
        source_path=path,
        source_sha256=digest,
        selected_stream_index=0,
        selection_source="explicit",
        inventory_digest="b" * 64,
        policy_decision_ref="policy-cli-synthetic",
        custody_state="synthetic",
    )
    body = {
        "entries": [
            {
                "revision_id": entry.revision_id,
                "content_id": entry.content_id,
                "source_path": str(entry.source_path),
                "source_sha256": entry.source_sha256,
                "selected_stream_index": entry.selected_stream_index,
                "selection_source": entry.selection_source,
                "inventory_digest": entry.inventory_digest,
                "policy_decision_ref": entry.policy_decision_ref,
                "custody_state": entry.custody_state,
                "inventory_artifact_id": None,
                "inventory_payload_digest": None,
            }
        ],
        "schema_version": "vip_fvs.multi_source_manifest.v1",
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest_digest = hashlib.sha256(raw).hexdigest()
    return MultiSourceManifest((entry,), manifest_digest)


def _seed_arm_artifacts(
    tmp_path: Path,
    arm_label: str,
    profile_id: str,
    *,
    sha_hex: str,
    pts: int,
) -> dict[str, Path]:
    profile_path = tmp_path / f"{arm_label}-profile.json"
    profile_path.write_text(
        json.dumps(make_synthetic_profile_payload(profile_id), sort_keys=True),
        encoding="utf-8",
    )
    bundle = build_synthetic_profile_runtime(make_synthetic_profile(profile_id))
    source_locator = tmp_path / f"{arm_label}-opaque-source.mp4"
    index_root = tmp_path / f"{arm_label}-index"

    spec: GenerationSpec = build_generation_spec(bundle.semantic_space)
    paths = storage.open_or_create_generation(index_root, spec)
    samples = [
        storage.PersistedSample(
            pts=pts,
            timebase_num=1001,
            timebase_den=30000,
            pts_time=(pts * 1001) / 30000,
            timestamp_human="00:00:03.003",
            thumbnail_stage_path=paths.staging / "stage-0.jpg",
        )
    ]
    vectors = bundle.runtime.image_embedder([index_root / "synthetic-frame-0.jpg"])
    conn = storage.connect_db(paths)
    try:
        storage.append_source_segment(
            paths,
            conn,
            source_sha256=sha_hex,
            source_metadata={
                "source_revision": f"rev-{arm_label}",
                "size_bytes": 1024,
                "stream_index": 0,
                "codec": "h264",
                "width": 1920,
                "height": 1080,
                "timebase_num": 1001,
                "timebase_den": 30000,
                "duration_seconds": 8.0,
            },
            samples=samples,
            normalized_vectors=vectors,
            expected_dim=spec.space.embedding_dim,
            stream_index=0,
        )
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO source_locations ("
                "path, source_sha256, last_observed_size, last_observed_mtime_ns, last_observed_at"
                ") VALUES (?,?,?,?,?)",
                (str(source_locator), sha_hex, 1024, 1, "2026-11-04T00:00:00+00:00"),
            )
    finally:
        conn.close()

    manifest = _build_manifest(
        source_locator,
        revision=f"rev-{arm_label}",
        content=f"content-{arm_label}",
        digest=sha_hex,
    )
    manifest_path = tmp_path / f"{arm_label}-manifest.json"
    save_multi_source_manifest(manifest, manifest_path)
    return {
        "profile_json": profile_path,
        "index_root": index_root,
        "manifest": manifest_path,
    }


def test_existing_and_new_cli_commands_parse_without_regression() -> None:
    parser = cli._parser()

    batch_args = parser.parse_args([
        "query-batch-synthetic",
        "--catalog",
        "catalog.json",
        "--manifest",
        "manifest.json",
        "--index-root",
        "index",
        "--model-profile-json",
        "profile.json",
        "--fake-embedder",
        "--top-k",
        "5",
    ])
    assert batch_args.command == "query-batch-synthetic"
    assert batch_args.fake_embedder is True
    assert not hasattr(batch_args, "source")

    three_arm_args = parser.parse_args([
        "query-three-arm-synthetic",
        "--catalog",
        "catalog.json",
        "--arm-map",
        "arms.json",
        "--fake-embedder",
        "--top-k",
        "10",
    ])
    assert three_arm_args.command == "query-three-arm-synthetic"
    assert three_arm_args.fake_embedder is True
    assert not hasattr(three_arm_args, "source")

    # Verify legacy commands remain intact.
    assert parser.parse_args([
        "query-multi", "--manifest", "m.json", "--query", "q", "--index-root", "i", "--fake-embedder"
    ]).command == "query-multi"
    assert parser.parse_args([
        "query-local", "--query", "q", "--index-root", "i", "--fake-embedder"
    ]).command == "query-local"
    assert parser.parse_args([
        "index-local", "--source", "s.mp4", "--index-root", "i", "--fake-embedder"
    ]).command == "index-local"


@pytest.mark.parametrize(
    ("profile_id", "expected_dim", "expected_row_bytes"),
    [
        (V1_PROFILE_ID, 768, 3072),
        (V2_BASE_PROFILE_ID, 768, 3072),
        (V2_SO400M_PROFILE_ID, 1152, 4608),
    ],
)
def test_cli_query_batch_synthetic_emits_verified_deterministic_report_for_each_profile(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    profile_id: str,
    expected_dim: int,
    expected_row_bytes: int,
) -> None:
    catalog_path = _write_catalog(tmp_path)
    artifacts = _seed_arm_artifacts(
        tmp_path,
        profile_id,
        profile_id,
        sha_hex="aa" * 32,
        pts=90090,
    )
    argv = [
        "query-batch-synthetic",
        "--catalog",
        str(catalog_path),
        "--manifest",
        str(artifacts["manifest"]),
        "--index-root",
        str(artifacts["index_root"]),
        "--model-profile-json",
        str(artifacts["profile_json"]),
        "--fake-embedder",
        "--top-k",
        "3",
    ]

    assert cli.main(argv) == 0
    out_1 = capsys.readouterr().out.strip()
    assert cli.main(argv) == 0
    out_2 = capsys.readouterr().out.strip()
    assert out_1 == out_2

    report = verify_batch_report(out_1)
    assert report["kind"] == KIND_SINGLE_ARM
    assert report["status"] == REPORT_STATUS_SYNTHETIC_ONLY
    assert report["benchmark_status"] == BENCHMARK_STATUS_NOT_RUN
    assert report["model_evidence"] == MODEL_EVIDENCE_NOT_OBSERVED
    assert report["gate_decision"] == GATE_DECISION_NOT_AUTHORIZED
    assert report["arms"][0]["profile_id"] == profile_id
    assert report["arms"][0]["embedding_dim"] == expected_dim
    assert report["arms"][0]["row_width_bytes"] == expected_row_bytes
    cand = report["arms"][0]["queries"][0]["candidates"][0]
    assert cand["evidence_class"] == "MATCHED"
    assert cand["binding_eligible"] is False
    assert cand["source_sample_pts"] == 90090
    assert cand["source_timebase_num"] == 1001
    assert cand["source_timebase_den"] == 30000


def test_cli_query_three_arm_synthetic_emits_verified_deterministic_three_arm_report(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    catalog_path = _write_catalog(tmp_path)
    v1_art = _seed_arm_artifacts(tmp_path, "v1", V1_PROFILE_ID, sha_hex="11" * 32, pts=45045)
    v2_base_art = _seed_arm_artifacts(tmp_path, "v2base", V2_BASE_PROFILE_ID, sha_hex="22" * 32, pts=90090)
    so400m_art = _seed_arm_artifacts(tmp_path, "so400m", V2_SO400M_PROFILE_ID, sha_hex="33" * 32, pts=135135)

    arm_map_path = tmp_path / "arm-map.json"
    arm_map_payload = {
        "schema_version": THREE_ARM_MAP_SCHEMA_VERSION,
        "arms": [
            {
                "arm_id": ARM_VIP_V2_SO400M,
                "model_profile_json": str(so400m_art["profile_json"]),
                "index_root": str(so400m_art["index_root"]),
                "manifest": str(so400m_art["manifest"]),
            },
            {
                "arm_id": ARM_VIP_V1_BASE,
                "model_profile_json": str(v1_art["profile_json"]),
                "index_root": str(v1_art["index_root"]),
                "manifest": str(v1_art["manifest"]),
            },
            {
                "arm_id": ARM_VIP_V2_BASE,
                "model_profile_json": str(v2_base_art["profile_json"]),
                "index_root": str(v2_base_art["index_root"]),
                "manifest": str(v2_base_art["manifest"]),
            },
        ],
    }
    arm_map_path.write_text(json.dumps(arm_map_payload, sort_keys=True), encoding="utf-8")

    argv = [
        "query-three-arm-synthetic",
        "--catalog",
        str(catalog_path),
        "--arm-map",
        str(arm_map_path),
        "--fake-embedder",
        "--top-k",
        "2",
    ]
    assert cli.main(argv) == 0
    out_1 = capsys.readouterr().out.strip()
    assert cli.main(argv) == 0
    out_2 = capsys.readouterr().out.strip()
    assert out_1 == out_2

    report = verify_batch_report(out_1)
    assert report["kind"] == KIND_THREE_ARM
    assert [a["arm_id"] for a in report["arms"]] == list(DECLARED_ARM_ORDER)
    assert [a["embedding_dim"] for a in report["arms"]] == [768, 768, 1152]
    assert [
        a["queries"][0]["candidates"][0]["source_sample_pts"] for a in report["arms"]
    ] == [45045, 90090, 135135]


def test_cli_synthetic_batch_commands_refuse_invalid_inputs_without_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    side_effects: list[str] = []
    monkeypatch.setattr(
        cli,
        "_real_runtime",
        lambda _args: side_effects.append("real_runtime") or pytest.fail("_real_runtime must not run"),
    )
    monkeypatch.setattr(
        coordinator,
        "index_local_source",
        lambda *a, **k: side_effects.append("index_local_source") or pytest.fail("index_local_source must not run"),
    )

    catalog_path = _write_catalog(tmp_path)
    v1_art = _seed_arm_artifacts(tmp_path, "refusal-v1", V1_PROFILE_ID, sha_hex="44" * 32, pts=90090)
    v2_art = _seed_arm_artifacts(tmp_path, "refusal-v2", V2_BASE_PROFILE_ID, sha_hex="55" * 32, pts=90090)
    so400m_art = _seed_arm_artifacts(tmp_path, "refusal-so400m", V2_SO400M_PROFILE_ID, sha_hex="66" * 32, pts=90090)

    # Construct an arm map with a generation mismatch on VIP_V1_BASE (pointing to V2 Base index).
    mismatched_arm_map_path = tmp_path / "mismatched-arm-map.json"
    mismatched_arm_map_path.write_text(
        json.dumps({
            "schema_version": THREE_ARM_MAP_SCHEMA_VERSION,
            "arms": [
                {
                    "arm_id": ARM_VIP_V1_BASE,
                    "model_profile_json": str(v1_art["profile_json"]),
                    "index_root": str(v2_art["index_root"]),
                    "manifest": str(v1_art["manifest"]),
                },
                {
                    "arm_id": ARM_VIP_V2_BASE,
                    "model_profile_json": str(v2_art["profile_json"]),
                    "index_root": str(v1_art["index_root"]),
                    "manifest": str(v2_art["manifest"]),
                },
                {
                    "arm_id": ARM_VIP_V2_SO400M,
                    "model_profile_json": str(so400m_art["profile_json"]),
                    "index_root": str(so400m_art["index_root"]),
                    "manifest": str(so400m_art["manifest"]),
                },
            ],
        }),
        encoding="utf-8",
    )

    refusal_cases: list[tuple[list[str], str]] = [
        # 1. Missing --fake-embedder on query-batch-synthetic
        (
            [
                "query-batch-synthetic",
                "--catalog",
                str(catalog_path),
                "--manifest",
                str(v2_art["manifest"]),
                "--index-root",
                str(v2_art["index_root"]),
                "--model-profile-json",
                str(v2_art["profile_json"]),
            ],
            "SYNTHETIC_BATCH_REQUIRES_EXPLICIT_FAKE_MODE",
        ),
        # 2. Missing --fake-embedder on query-three-arm-synthetic
        (
            [
                "query-three-arm-synthetic",
                "--catalog",
                str(catalog_path),
                "--arm-map",
                str(mismatched_arm_map_path),
            ],
            "SYNTHETIC_BATCH_REQUIRES_EXPLICIT_FAKE_MODE",
        ),
        # 3. Missing --model-profile-json on query-batch-synthetic
        (
            [
                "query-batch-synthetic",
                "--catalog",
                str(catalog_path),
                "--manifest",
                str(v2_art["manifest"]),
                "--index-root",
                str(v2_art["index_root"]),
                "--fake-embedder",
            ],
            "MODEL_PROFILE_JSON_REQUIRED",
        ),
        # 4. Real-mode flag passed alongside --fake-embedder
        (
            [
                "query-batch-synthetic",
                "--catalog",
                str(catalog_path),
                "--manifest",
                str(v2_art["manifest"]),
                "--index-root",
                str(v2_art["index_root"]),
                "--model-profile-json",
                str(v2_art["profile_json"]),
                "--fake-embedder",
                "--model-root",
                str(tmp_path / "model"),
            ],
            "FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS",
        ),
        # 5. Unsupported modality (image-reference)
        (
            [
                "query-batch-synthetic",
                "--catalog",
                str(catalog_path),
                "--manifest",
                str(v2_art["manifest"]),
                "--index-root",
                str(v2_art["index_root"]),
                "--model-profile-json",
                str(v2_art["profile_json"]),
                "--fake-embedder",
                "--modality",
                "image-reference",
            ],
            "QUERY_MODALITY_NOT_EXECUTABLE:IMAGE_REFERENCE",
        ),
        # 6. Out-of-bounds top-k
        (
            [
                "query-batch-synthetic",
                "--catalog",
                str(catalog_path),
                "--manifest",
                str(v2_art["manifest"]),
                "--index-root",
                str(v2_art["index_root"]),
                "--model-profile-json",
                str(v2_art["profile_json"]),
                "--fake-embedder",
                "--top-k",
                str(MAX_TOP_K + 1),
            ],
            "QUERY_BATCH_TOP_K_INVALID",
        ),
        # 7. Missing profile JSON file
        (
            [
                "query-batch-synthetic",
                "--catalog",
                str(catalog_path),
                "--manifest",
                str(v2_art["manifest"]),
                "--index-root",
                str(v2_art["index_root"]),
                "--model-profile-json",
                str(tmp_path / "nonexistent-profile.json"),
                "--fake-embedder",
            ],
            "MODEL_PROFILE_JSON_UNREADABLE",
        ),
        # 8. One arm generation mismatch in query-three-arm-synthetic
        (
            [
                "query-three-arm-synthetic",
                "--catalog",
                str(catalog_path),
                "--arm-map",
                str(mismatched_arm_map_path),
                "--fake-embedder",
            ],
            "SEMANTIC_SPACE_MISMATCH:model_identity:",
        ),
    ]

    for argv, expected_error in refusal_cases:
        assert cli.main(argv) == 1
        raw_out = capsys.readouterr().out.strip()
        err_obj = json.loads(raw_out)
        assert err_obj["all_checks_passed"] is False
        assert expected_error in err_obj["error"]
        assert err_obj.get("status") != REPORT_STATUS_SYNTHETIC_ONLY

    assert side_effects == []
