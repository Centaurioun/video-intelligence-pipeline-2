"""Behavioral coverage for the synthetic D05 generated-case harness."""

from __future__ import annotations

from pathlib import Path

import pytest

from gate1.artifacts import load_artifact_root
from gate1.verify import verify_artifact_set
from gate1.harness import get_case


VALID_CASES = (
    "positive_one_axis",
    "tie_no_superiority",
    "partial_coverage",
    "quality_failure",
    "resource_failure",
)


def _run(case_id: str, tmp_path: Path) -> tuple[Path, dict[str, object]]:
    # Import inside the test so the pre-implementation run reaches the intended
    # behavioral RED: the D05 harness is not present on the frozen base.
    from gate1.harness import run_generated_case

    artifact_root = run_generated_case(case_id, tmp_path / case_id)
    assert isinstance(artifact_root, Path)
    assert artifact_root.is_dir()
    candidate = load_artifact_root(artifact_root)
    verify_artifact_set(candidate, mode="SYNTHETIC")
    return artifact_root, candidate


@pytest.mark.parametrize("case_id", VALID_CASES)
def test_generated_valid_cases_emit_closed_verifiable_synthetic_artifacts(case_id, tmp_path):
    _, candidate = _run(case_id, tmp_path)
    expected = get_case(case_id)["expected"]

    assert candidate["benchmark_report.json"] == expected["benchmark_report"]

    ranked_by_arm_candidate = {}
    for row in candidate["ranked_candidates.jsonl"]:
        ranked_by_arm_candidate.setdefault(row["arm_id"], {})[row["candidate_id"]] = {
            "score": row["score"],
            "rank": row["rank"],
            "tie_key": row["tie_key"],
            "coverage_status": row["coverage_status"],
        }
    assert ranked_by_arm_candidate == expected["ranked_candidates"]

    assert candidate["run_manifest.json"]["execution_mode"] == "SYNTHETIC"
    assert candidate["synthetic_receipt.json"]["real_benchmark_executed"] is False
    assert candidate["synthetic_receipt.json"]["provider_calls"] == 0
    assert candidate["synthetic_receipt.json"]["network_egress_bytes"] == 0
    assert candidate["synthetic_receipt.json"]["protected_media_used"] is False
    assert candidate["synthetic_receipt.json"]["model_download_or_change"] is False
    assert candidate["synthetic_receipt.json"]["gate_promotion"] is False


def test_positive_one_axis_case_reports_synthetic_success_without_real_claim(tmp_path):
    _, candidate = _run("positive_one_axis", tmp_path)

    contract = candidate["comparison_contract.json"]
    report = candidate["benchmark_report.json"]
    assert len(contract["arm_ids"]) == 2
    assert contract["changed_axis"] in {"space_id", "representation_id"}
    assert report["validity"] == "VALID"
    assert report["benchmark_status"] == "PASS"
    assert report["failure_class"] is None
    assert report["conclusion"] == "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"
    assert candidate["synthetic_receipt.json"]["winner_observed"] is False


def test_tie_case_keeps_equal_outcomes_and_makes_no_winner_claim(tmp_path):
    _, candidate = _run("tie_no_superiority", tmp_path)

    report = candidate["benchmark_report.json"]
    values = report["arm_values"]
    assert len(values) == 2
    assert len(set(values.values())) == 1
    assert report["primary_value"] == 0
    assert report["validity"] == "VALID"
    assert report["failure_class"] == "QUALITY"
    assert not any("winner" in key.lower() for key in report)
    assert candidate["synthetic_receipt.json"]["winner_observed"] is False


def test_partial_coverage_preserves_d04_omitted_null_rankings(tmp_path):
    _, candidate = _run("partial_coverage", tmp_path)

    omitted = [row for row in candidate["ranked_candidates.jsonl"]
               if row["coverage_status"] == "OMITTED"]
    assert omitted, "partial-coverage fixture must contain an explicit D04 OMITTED row"
    assert all(row["score"] is None and row["rank"] is None and row["tie_key"] is None
               for row in omitted)
    assert candidate["benchmark_report.json"]["validity"] == "VALID"
    assert candidate["benchmark_report.json"]["benchmark_status"] == "FAIL"
    assert candidate["benchmark_report.json"]["failure_class"] == "COVERAGE_INCOMPLETE"


def test_quality_failure_is_valid_negative_synthetic_evidence(tmp_path):
    _, candidate = _run("quality_failure", tmp_path)

    report = candidate["benchmark_report.json"]
    assert report["validity"] == "VALID"
    assert report["benchmark_status"] == "FAIL"
    assert report["failure_class"] == "QUALITY"
    assert report["conclusion"] == "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"


def test_resource_failure_is_valid_and_classified_as_operability(tmp_path):
    _, candidate = _run("resource_failure", tmp_path)

    report = candidate["benchmark_report.json"]
    assert candidate["failure_ledger.json"]["event_type"] == "RESOURCE_OPERABILITY"
    assert report["validity"] == "VALID"
    assert report["benchmark_status"] == "FAIL"
    assert report["failure_class"] == "RESOURCE_OPERABILITY"
    assert report["conclusion"] == "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"
