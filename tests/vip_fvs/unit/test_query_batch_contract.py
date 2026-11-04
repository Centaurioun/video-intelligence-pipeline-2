"""Unit contract tests for Workstream W1 (query_batch) and Workstream W2 (synthetic_profiles)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from vip_fvs.query_batch import (
    MAX_CATALOG_BYTES,
    MAX_QUERY_COUNT,
    MAX_QUERY_TEXT_LENGTH,
    MAX_TOP_K,
    MIN_QUERY_COUNT,
    MIN_TOP_K,
    QUERY_CATALOG_SCHEMA_VERSION,
    QueryCatalog,
    QueryCatalogItem,
    load_query_catalog,
    parse_query_catalog_bytes,
    parse_query_catalog_mapping,
    validate_lab_top_k,
)
from vip_fvs.synthetic_profiles import (
    CLOSED_SYNTHETIC_PROFILE_IDS,
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
    build_synthetic_profile_runtime,
    load_model_profile_json,
    load_synthetic_profile_bundle,
    make_synthetic_profile,
    make_synthetic_profile_payload,
    parse_model_profile_mapping,
)


def _valid_catalog_payload() -> dict[str, Any]:
    return {
        "schema_version": QUERY_CATALOG_SCHEMA_VERSION,
        "catalog_id": "synthetic-catalog-01",
        "queries": [
            {"query_id": "q-001", "text": "a dancer landing from a grand jeté"},
            {"query_id": "q-002", "text": "a close-up of an orchestra conductor — kuğu gölü"},
        ],
    }


# ---------------------------------------------------------------------------
# Workstream W1 — Query catalog contract & deterministic identity
# ---------------------------------------------------------------------------


def test_valid_query_catalog_preserves_order_utf8_and_deterministic_digest(
    tmp_path: Path,
) -> None:
    payload = _valid_catalog_payload()
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    catalog_a = load_query_catalog(catalog_path)
    catalog_b = parse_query_catalog_mapping(payload)

    assert catalog_a == catalog_b
    assert catalog_a.schema_version == QUERY_CATALOG_SCHEMA_VERSION
    assert catalog_a.catalog_id == "synthetic-catalog-01"
    assert catalog_a.query_ids == ("q-001", "q-002")
    assert catalog_a.queries[0].text == "a dancer landing from a grand jeté"
    assert catalog_a.queries[1].text == "a close-up of an orchestra conductor — kuğu gölü"
    assert len(catalog_a.catalog_digest) == 64
    assert catalog_a.catalog_id != catalog_a.catalog_digest
    assert catalog_a.to_dict() == payload


@pytest.mark.parametrize("count", [MIN_QUERY_COUNT, 2, MAX_QUERY_COUNT])
def test_query_catalog_accepts_bounded_query_counts(count: int) -> None:
    payload = {
        "schema_version": QUERY_CATALOG_SCHEMA_VERSION,
        "catalog_id": f"catalog-count-{count}",
        "queries": [
            {"query_id": f"q-{idx:03d}", "text": f"synthetic query text {idx}"}
            for idx in range(1, count + 1)
        ],
    }
    catalog = parse_query_catalog_mapping(payload)
    assert len(catalog.queries) == count
    assert len(catalog.query_ids) == count


def test_duplicate_query_text_under_distinct_query_ids_preserves_both_ids() -> None:
    payload = {
        "schema_version": QUERY_CATALOG_SCHEMA_VERSION,
        "catalog_id": "dup-text-catalog",
        "queries": [
            {"query_id": "q-alpha", "text": "identical ballet phrase"},
            {"query_id": "q-beta", "text": "distinct intermezzo"},
            {"query_id": "q-gamma", "text": "identical ballet phrase"},
        ],
    }
    catalog = parse_query_catalog_mapping(payload)
    assert catalog.query_ids == ("q-alpha", "q-beta", "q-gamma")
    assert [q.text for q in catalog.queries] == [
        "identical ballet phrase",
        "distinct intermezzo",
        "identical ballet phrase",
    ]
    assert catalog.distinct_texts() == ("identical ballet phrase", "distinct intermezzo")


@pytest.mark.parametrize(
    ("mutator", "expected_match"),
    [
        (lambda d: d.pop("schema_version"), "QUERY_CATALOG_FIELDS_INVALID"),
        (lambda d: d.update(extra="forbidden"), "QUERY_CATALOG_FIELDS_INVALID"),
        (lambda d: d.update(schema_version="vip-lab-query-catalog-v0"), "QUERY_CATALOG_SCHEMA_INVALID"),
        (lambda d: d.update(catalog_id=""), "QUERY_CATALOG_ID_INVALID"),
        (lambda d: d.update(catalog_id="../traversal"), "QUERY_CATALOG_ID_INVALID"),
        (lambda d: d.update(catalog_id="a/b"), "QUERY_CATALOG_ID_INVALID"),
        (lambda d: d.update(catalog_id="a" * 64), "QUERY_CATALOG_ID_INVALID"),
        (lambda d: d.update(queries=[]), "QUERY_CATALOG_COUNT_OUT_OF_BOUNDS"),
        (
            lambda d: d.update(
                queries=[
                    {"query_id": f"q-{i:03d}", "text": "x"}
                    for i in range(MAX_QUERY_COUNT + 1)
                ]
            ),
            "QUERY_CATALOG_COUNT_OUT_OF_BOUNDS",
        ),
        (
            lambda d: d.update(
                queries=[
                    {"query_id": "q-001", "text": "first"},
                    {"query_id": "q-001", "text": "second"},
                ]
            ),
            "QUERY_CATALOG_DUPLICATE_QUERY_ID",
        ),
        (
            lambda d: d["queries"][0].update(extra_item_field="no"),
            "QUERY_CATALOG_ITEM_FIELDS_INVALID",
        ),
        (
            lambda d: d["queries"][0].pop("text"),
            "QUERY_CATALOG_ITEM_FIELDS_INVALID",
        ),
    ],
)
def test_query_catalog_mapping_rejects_invalid_shapes(
    mutator: Any, expected_match: str
) -> None:
    payload = _valid_catalog_payload()
    mutator(payload)
    with pytest.raises(ValueError, match=expected_match):
        parse_query_catalog_mapping(payload)


@pytest.mark.parametrize(
    "bad_query_id",
    [
        "",
        "   ",
        " q-001",
        "q-001 ",
        "../q-001",
        "/abs/q-001",
        "dir/q-001",
        "dir\\q-001",
        "C:q-001",
        ".",
        "..",
        "q..001",
        "q\x00001",
        "f" * 64,
        "q-" + ("x" * 130),
    ],
)
def test_query_catalog_item_rejects_invalid_or_pathlike_query_ids(
    bad_query_id: str,
) -> None:
    with pytest.raises(ValueError, match="QUERY_CATALOG_QUERY_ID_INVALID"):
        QueryCatalogItem(query_id=bad_query_id, text="valid text")


@pytest.mark.parametrize(
    "bad_text",
    [
        "",
        "   \t\n  ",
        "embedded\x00nul",
        "x" * (MAX_QUERY_TEXT_LENGTH + 1),
        None,
        123,
    ],
)
def test_query_catalog_item_rejects_invalid_text(bad_text: Any) -> None:
    with pytest.raises(ValueError, match="QUERY_CATALOG_QUERY_TEXT_INVALID"):
        QueryCatalogItem(query_id="q-001", text=bad_text)


def test_query_catalog_bytes_rejects_duplicate_keys_invalid_utf8_nonfinite_and_oversize(
    tmp_path: Path,
) -> None:
    dup_key_raw = (
        b'{"schema_version":"vip-lab-query-catalog-v1",'
        b'"catalog_id":"cat-1","catalog_id":"cat-2",'
        b'"queries":[{"query_id":"q-1","text":"ok"}]}'
    )
    with pytest.raises(ValueError, match="QUERY_CATALOG_DUPLICATE_JSON_KEY"):
        parse_query_catalog_bytes(dup_key_raw)

    with pytest.raises(ValueError, match="QUERY_CATALOG_UTF8_INVALID"):
        parse_query_catalog_bytes(b"\xff\xfe\xfd")

    with pytest.raises(ValueError, match="QUERY_CATALOG_NUL_BYTE_FORBIDDEN"):
        parse_query_catalog_bytes(b'{"schema_version":"vip-lab-query-catalog-v1\x00"}')

    with pytest.raises(ValueError, match="QUERY_CATALOG_NON_FINITE_NUMBER"):
        parse_query_catalog_bytes(b'{"schema_version":NaN}')

    oversize_path = tmp_path / "oversize-catalog.json"
    oversize_path.write_bytes(b" " * (MAX_CATALOG_BYTES + 1))
    with pytest.raises(ValueError, match="QUERY_CATALOG_SIZE_EXCEEDED"):
        load_query_catalog(oversize_path)


@pytest.mark.parametrize(
    "bad_top_k",
    [True, False, 0, -1, -100, MAX_TOP_K + 1, 1.5, "5", None],
)
def test_validate_lab_top_k_guards_bounds_and_boolean_ints(bad_top_k: Any) -> None:
    with pytest.raises(ValueError, match="QUERY_BATCH_TOP_K_INVALID"):
        validate_lab_top_k(bad_top_k)
    assert validate_lab_top_k(MIN_TOP_K) == MIN_TOP_K
    assert validate_lab_top_k(MAX_TOP_K) == MAX_TOP_K


# ---------------------------------------------------------------------------
# Workstream W2 — Synthetic three-profile runtime factory
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("profile_id", "expected_dim", "expected_row_bytes", "expected_device", "expected_policy"),
    [
        (V1_PROFILE_ID, 768, 3072, "cpu", "v1-float32"),
        (V2_BASE_PROFILE_ID, 768, 3072, "pytorch-cpu", "siglip2-fp16-compute-fp32-output"),
        (V2_SO400M_PROFILE_ID, 1152, 4608, "pytorch-cpu", "siglip2-fp16-compute-fp32-output"),
    ],
)
def test_synthetic_profile_factory_builds_checked_fake_bundles_for_all_three_profiles(
    tmp_path: Path,
    profile_id: str,
    expected_dim: int,
    expected_row_bytes: int,
    expected_device: str,
    expected_policy: str,
) -> None:
    assert CLOSED_SYNTHETIC_PROFILE_IDS == (
        V1_PROFILE_ID,
        V2_BASE_PROFILE_ID,
        V2_SO400M_PROFILE_ID,
    )
    payload = make_synthetic_profile_payload(profile_id)
    profile_path = tmp_path / f"{profile_id}.json"
    profile_path.write_text(json.dumps(payload), encoding="utf-8")

    bundle = load_synthetic_profile_bundle(profile_path)
    assert bundle.profile.profile_id == profile_id
    assert bundle.profile.device_backend == expected_device
    assert bundle.profile.precision_policy_id == expected_policy
    assert bundle.profile.embedding_dim == expected_dim
    assert bundle.row_width_bytes == expected_row_bytes
    assert bundle.runtime.fake is True
    assert bundle.synthetic_only is True
    assert bundle.authentic_model_evidence is False

    vec = bundle.runtime.text_embedder(["synthetic ballet query"])
    assert vec.shape == (1, expected_dim)
    assert vec.dtype == np.float32
    assert np.isfinite(vec).all()
    assert np.allclose(np.linalg.norm(vec, axis=1), 1.0, atol=1e-5)


def test_v1_and_v2_base_768d_and_so400m_1152d_have_distinct_space_ids() -> None:
    b_v1 = build_synthetic_profile_runtime(make_synthetic_profile(V1_PROFILE_ID))
    b_v2_base = build_synthetic_profile_runtime(make_synthetic_profile(V2_BASE_PROFILE_ID))
    b_so400m = build_synthetic_profile_runtime(make_synthetic_profile(V2_SO400M_PROFILE_ID))

    assert b_v1.semantic_space.embedding_dim == b_v2_base.semantic_space.embedding_dim == 768
    assert b_so400m.semantic_space.embedding_dim == 1152
    assert len({b_v1.space_id, b_v2_base.space_id, b_so400m.space_id}) == 3


def test_v1_rejects_v2_representation_policy_and_v2_rejects_unlisted_text_contract(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="MODEL_PROFILE_V1_REPRESENTATION_POLICY_UNSUPPORTED"):
        make_synthetic_profile(V1_PROFILE_ID, device_backend="pytorch-cpu")

    with pytest.raises(ValueError, match="MODEL_PROFILE_V1_REPRESENTATION_POLICY_UNSUPPORTED"):
        make_synthetic_profile(
            V1_PROFILE_ID,
            precision_policy_id="siglip2-fp16-compute-fp32-output",
        )

    with pytest.raises(ValueError, match="MODEL_PROFILE_TEXT_CONTRACT_INVALID"):
        make_synthetic_profile(
            V2_SO400M_PROFILE_ID,
            text_preprocessing_contract=f"{V2_SO400M_PROFILE_ID}:text-contract:sha256:{'a' * 64}",
        )

    bool_dim_payload = make_synthetic_profile_payload(V2_BASE_PROFILE_ID)
    bool_dim_payload["embedding_dim"] = True
    with pytest.raises(ValueError, match="MODEL_PROFILE_JSON_INVALID:embedding_dim"):
        parse_model_profile_mapping(bool_dim_payload)

    missing_path = tmp_path / "does-not-exist.json"
    with pytest.raises(ValueError, match="MODEL_PROFILE_JSON_UNREADABLE"):
        load_model_profile_json(missing_path)
