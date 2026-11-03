"""T11 synthetic-only acceptance projections.

These checks inspect checked-in contracts and test inputs only.  They do not
run media, models, providers, or the Gate-0 pipeline against a real archive.
"""

import json
from pathlib import Path

import pytest

from gate0.contracts.validator import ARTIFACT_FILENAMES


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "gate0" / "fixtures"


def _assert_no_forbidden_policy_paths(root: Path) -> None:
    forbidden = sorted(path for path in root.rglob("policy.json") if path.is_file())
    assert not forbidden, f"policy.json is forbidden under acceptance root: {forbidden}"


def test_fixture_catalog_is_exact_and_covers_six_v11_roles():
    catalog = json.loads((FIXTURES / "catalog.json").read_text(encoding="utf-8"))
    fixtures = catalog["fixtures"]
    assert [fixture["id"] for fixture in fixtures] == [
        "cfr_4s",
        "vfr_nonunit",
        "vfr_negative",
        "duplicate_pts",
        "missing_pts",
        "tie_oracle",
        "boundary_end",
    ]
    assert len(fixtures) == 7

    roles = {
        "cfr": any(item["id"] == "cfr_4s" for item in fixtures),
        "vfr": any(item["id"].startswith("vfr_") for item in fixtures),
        "nonunit_timebase": any(
            item["time_base"] != {"num": 1, "den": 1} for item in fixtures
        ),
        "nonzero_origin": any(item["id"] == "vfr_negative" for item in fixtures),
        "duplicate_or_equal_pts": any(
            item["id"] in {"duplicate_pts", "tie_oracle"} for item in fixtures
        ),
        "missing_pts_failure": any(item["id"] == "missing_pts" for item in fixtures),
    }
    assert all(roles.values()), roles


def test_fixture_catalog_entries_have_required_oracle_fields():
    catalog = json.loads((FIXTURES / "catalog.json").read_text(encoding="utf-8"))
    for fixture in catalog["fixtures"]:
        assert {
            "id",
            "generation_method",
            "check_in_method",
            "codec_container",
            "source",
            "time_base",
            "pts",
            "duration_seconds",
            "duplicate_state",
            "expected_target_schedule",
            "expected_outcome",
            "checksum",
        } <= fixture.keys()


def test_run_result_contract_is_exactly_thirteen_and_policy_json_is_not_an_artifact():
    assert len(ARTIFACT_FILENAMES) == 13
    assert "policy.json" not in ARTIFACT_FILENAMES
    assert "config/gate0/default.json" not in ARTIFACT_FILENAMES

    # A runtime output root may contain only the closed result inventory.  The
    # repository has no committed runtime output roots; this guard also catches
    # accidental policy-control duplication if one is introduced later.
    for root in (ROOT / "output", ROOT / "outputs", ROOT / "runtime_artifacts"):
        if root.exists():
            assert not any(path.name == "policy.json" for path in root.rglob("*"))


def test_acceptance_receipt_preserves_unobserved_runtime_boundaries():
    receipt = ROOT / "docs" / "gate0" / "implementation-receipt.md"
    text = receipt.read_text(encoding="utf-8")
    assert "NOT_OBSERVED" in text
    assert "real" in text.lower() and "model" in text.lower()
    assert "13" in text


def test_policy_json_is_rejected_under_a_synthetic_run_output_root(tmp_path):
    run_root = tmp_path / "outputs" / "synthetic-run"
    run_root.mkdir(parents=True)
    (run_root / "policy.json").write_text("{}", encoding="utf-8")
    with pytest.raises(AssertionError, match="policy.json"):
        _assert_no_forbidden_policy_paths(run_root)


def test_second_policy_control_file_is_rejected(tmp_path):
    control_root = tmp_path / "config" / "gate0"
    control_root.mkdir(parents=True)
    (control_root / "default.json").write_text("{}", encoding="utf-8")
    (control_root / "policy.json").write_text("{}", encoding="utf-8")
    with pytest.raises(AssertionError, match="policy.json"):
        _assert_no_forbidden_policy_paths(tmp_path)
