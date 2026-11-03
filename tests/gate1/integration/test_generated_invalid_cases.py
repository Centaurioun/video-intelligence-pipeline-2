"""Fail-closed end-to-end tests for generated invalid protocol cases."""
from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path

import pytest

from gate1.artifacts import load_artifact_root
from gate1.verify import VerificationError, verify_artifact_set
from gate1.harness import get_case


INVALID_CASES = (
    "invalid_multi_axis",
    "invalid_pinned_control",
    "source_overlap",
    "label_leakage_declaration",
    "incompatible_space",
    "policy_ineligible",
    "fabricated_backend",
)


def _run_generated_case(case_id: str, output_root: Path) -> Path:
    # Keep the pre-implementation failure behavioral and readable: missing
    # harness is the exact capability this integration contract requires.
    assert find_spec("gate1.harness") is not None, (
        "generated-case harness is not implemented yet"
    )
    from gate1.harness import run_generated_case

    artifact_root = run_generated_case(case_id, output_root)
    assert isinstance(artifact_root, Path)
    return artifact_root


@pytest.mark.parametrize("case_id", INVALID_CASES)
def test_invalid_protocol_case_fails_before_creating_output(case_id: str, tmp_path: Path):
    case = get_case(case_id)
    assert case["expected"]["protocol_validity"] == "INVALID_PROTOCOL"
    assert case["expected"]["benchmark_status"] == "INVALID_PROTOCOL"

    output_root = tmp_path / case_id
    with pytest.raises(ValueError):
        _run_generated_case(case_id, output_root)
    assert not output_root.exists()


def test_frozen_protocol_mutation_is_rejected_by_artifact_verifier(tmp_path: Path):
    case = get_case("frozen_protocol_mutation")
    assert case["expected"]["mutation_rejected"] is True

    artifact_root = _run_generated_case("positive_one_axis", tmp_path / "positive")
    artifacts = load_artifact_root(artifact_root)
    verify_artifact_set(artifacts)

    mutated = {name: value for name, value in artifacts.items()}
    mutated["comparison_contract.json"] = {
        **artifacts["comparison_contract.json"],
        "changed_axis": "provider_family",
    }
    with pytest.raises(VerificationError, match="digest|frozen|mutat|comparison"):
        verify_artifact_set(mutated)
