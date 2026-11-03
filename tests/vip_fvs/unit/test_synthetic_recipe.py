"""Strict validation of digest-bound synthetic source descriptors.

These tests cover the measurement seam of the synthetic product entrypoint.
A fixture descriptor that is incomplete, ambiguous, non-integer, mislabelled,
or digest-inconsistent must be refused *before* any PTS is treated as a
measured source-native interval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tests.vip_fvs.fixtures.materialize import load_recipe, materialize_fixture
from vip_fvs.synthetic_recipe import SyntheticRecipeRefusal, load_synthetic_recipe


def _payload(recipe: dict) -> bytes:
    canonical = json.dumps(recipe, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return json.dumps(
        {"recipe": recipe, "content_sha256": hashlib.sha256(canonical.encode()).hexdigest()},
        ensure_ascii=False, sort_keys=True, indent=2,
    ).encode("utf-8")


def _recipe() -> dict:
    return load_recipe("cfr_4s_shape")


def test_materialized_fixture_is_accepted(tmp_path: Path) -> None:
    source = materialize_fixture("cfr_4s_shape", tmp_path)
    recipe = load_synthetic_recipe(source.read_bytes(), scenario="cfr_4s_shape")
    assert recipe["fixture_id"] == "cfr_4s_shape"
    assert recipe["pts_ticks"] == [0, 13, 25, 38, 50, 63, 75, 88]


def test_missing_recipe_is_refused() -> None:
    payload = json.dumps({"content_sha256": "abc"}).encode()
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_ENVELOPE_INVALID"):
        load_synthetic_recipe(payload, scenario="cfr_4s_shape")


def test_non_json_source_is_refused() -> None:
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_SOURCE_NOT_JSON"):
        load_synthetic_recipe(b"not json", scenario="cfr_4s_shape")


def test_digest_mismatch_is_refused() -> None:
    recipe = _recipe()
    payload = json.dumps({"recipe": recipe, "content_sha256": "0" * 64}).encode()
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_DIGEST_MISMATCH"):
        load_synthetic_recipe(payload, scenario="cfr_4s_shape")


def test_envelope_with_extra_fields_is_refused() -> None:
    recipe = _recipe()
    canonical = json.dumps(recipe, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload = json.dumps(
        {"recipe": recipe, "content_sha256": hashlib.sha256(canonical.encode()).hexdigest(), "extra": 1}
    ).encode()
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_ENVELOPE_INVALID"):
        load_synthetic_recipe(payload, scenario="cfr_4s_shape")


def test_scenario_identity_mismatch_is_refused() -> None:
    payload = _payload(_recipe())
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_IDENTITY_MISMATCH"):
        load_synthetic_recipe(payload, scenario="vfr_nonuniform")


def test_unsupported_schema_is_refused() -> None:
    recipe = _recipe()
    recipe["schema_version"] = "vip_fvs.fixture.v0"
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_SCHEMA_UNSUPPORTED"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")


def test_float_pts_are_refused() -> None:
    recipe = _recipe()
    recipe["pts_ticks"] = [0, 13.5, 25]
    recipe["frames"] = []
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_PTS_INVALID"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")


def test_duplicate_pts_are_refused() -> None:
    recipe = _recipe()
    recipe["pts_ticks"] = [0, 40, 40, 80]
    recipe["frames"] = []
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_PTS_INVALID"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")


def test_empty_pts_are_refused() -> None:
    recipe = _recipe()
    recipe["pts_ticks"] = []
    recipe["frames"] = []
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_PTS_INVALID"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")


def test_origin_pts_mismatch_is_refused() -> None:
    recipe = _recipe()
    recipe["stream"]["origin_pts_ticks"] = 5
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_PTS_INVALID"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")


def test_timescale_timebase_mismatch_is_refused() -> None:
    recipe = _recipe()
    recipe["stream"]["media_timescale"] = 1000
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_TIME_BASE_INVALID"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")


def test_duration_inconsistency_is_refused() -> None:
    recipe = _recipe()
    recipe["duration_ticks"] = 101
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_DURATION_INCONSISTENT"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")


def test_frame_presentation_order_inconsistency_is_refused() -> None:
    recipe = _recipe()
    recipe["frames"] = list(reversed(recipe["frames"]))
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_FRAME_ORDER_INCONSISTENT"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")


def test_non_synthetic_source_kind_is_refused() -> None:
    recipe = _recipe()
    recipe["source_kind"] = "real"
    with pytest.raises(SyntheticRecipeRefusal, match="SYNTHETIC_RECIPE_IDENTITY_MISMATCH"):
        load_synthetic_recipe(_payload(recipe), scenario="cfr_4s_shape")
