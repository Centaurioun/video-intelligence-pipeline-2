"""S-06 / S-07 / S-12 / S-13 / S-14 compatibility report contract tests."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import hashlib

from gate1.canonical_json import canonical_bytes, sha256_digest
from gate1.harness import (
    ARM_DERIVATIONS,
    CHARTER_ARMS,
    CHARTER_PAIRS,
    LIMITATIONS,
    B07_NOT_COMPUTABLE,
    CompatibilityError,
    build_three_arm_compat_report,
    gate1_code_sha,
)
from tests.gate1.compat.test_three_arm_compat import _case


REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = REPO_ROOT / "schemas" / "gate1_compat_v2"
SHA256 = re.compile(r"^[0-9a-f]{64}$")

UNITS = {
    "SYNTHETIC_DELTA_MEETS_CONFIGURED_THRESHOLD",
    "SYNTHETIC_DELTA_BELOW_CONFIGURED_THRESHOLD",
    "SYNTHETIC_VALID_NEGATIVE_EVIDENCE",
    "COMPARISON_INVALID_NO_OUTCOME_CLAIM",
}


PRODUCING_MODULE_PATHS = (
    "__init__.py",
    "artifacts.py",
    "canonical_json.py",
    "contracts/__init__.py",
    "contracts/types.py",
    "contracts/validator.py",
    "evaluation.py",
    "harness.py",
    "ranking.py",
    "verify.py",
)


def _independent_code_sha(package_root: Path, relative_paths=PRODUCING_MODULE_PATHS) -> str:
    """Recompute the code identity locally; never call the production helper."""
    entries = [
        [relative_path, hashlib.sha256((package_root / relative_path).read_bytes()).hexdigest()]
        for relative_path in relative_paths
    ]
    entries.sort(key=lambda item: item[0])
    canonical = json.dumps(entries, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _schema(name: str) -> dict:
    return json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))


def _args(**overrides):
    contract, descriptors, policies, manifest, rankings, judgments = _case()
    kwargs = dict(
        contract=contract,
        descriptors=descriptors,
        policies=policies,
        run_manifest=manifest,
        rankings_by_arm=rankings,
        judgments=judgments,
        failures=(),
        query_ids=("query-1",),
        fixture_id="positive_one_axis",
        code_sha=gate1_code_sha(),
        arm_derivations=ARM_DERIVATIONS,
    )
    kwargs.update(overrides)
    return kwargs


def _report(**overrides):
    return build_three_arm_compat_report(**_args(**overrides))


def test_report_carries_deterministic_identity_and_anti_promotion_scope():
    report = _report()

    assert report["fixture_id"] == "positive_one_axis"
    assert SHA256.match(report["code_sha"])
    assert report["code_sha"] == _independent_code_sha(REPO_ROOT / "src" / "gate1")
    assert report["evidence_status"] == "SYNTHETIC_NOT_MODEL_EVIDENCE"
    assert report["judgment_evidence_class"] == "NOT_APPLICABLE_SYNTHETIC"
    contract = _args()["contract"]
    assert report["contract_digest"] == sha256_digest(contract)
    assert report["execution_mode"] == "SYNTHETIC"
    assert report["evaluation_scope"] == "SYNTHETIC_PROTOCOL_COMPATIBILITY_ONLY"
    assert report["operational_evaluation_status"] == "NOT_IMPLEMENTED"
    assert report["benchmark_readiness"] == "NOT_BENCHMARK_READY"
    assert report["winner_status"] == "NOT_EVALUATED"
    assert report["limitations"] == list(LIMITATIONS)
    assert "NOT_OPERATIONAL_THREE_ARM_B00_B18_EVALUATION" in report["limitations"]


def test_each_arm_declares_its_synthetic_derivation_including_the_cloned_third_arm():
    report = _report()

    assert report["arm_derivations"] == list(ARM_DERIVATIONS)
    assert [row["arm_id"] for row in report["arm_derivations"]] == list(CHARTER_ARMS)
    assert [row["synthetic_projection"] for row in report["arm_derivations"]] == [False, False, True]
    assert report["arm_derivations"][2]["arm_id"] == "VIP_V2_SO400M"
    assert report["arm_derivations"][2]["derived_from_arm_id"] == "arm_b"
    assert report["arm_derivations"][0]["derived_from_arm_id"] == "arm_a"


def test_arm_derivation_records_are_validated():
    bad_cases = (
        [],
        ARM_DERIVATIONS[:2],
        ARM_DERIVATIONS + (dict(ARM_DERIVATIONS[0]),),
        (dict(ARM_DERIVATIONS[0], arm_id="OTHER"), *ARM_DERIVATIONS[1:]),
        tuple(dict(row, synthetic_projection=False) for row in ARM_DERIVATIONS),
        (dict(ARM_DERIVATIONS[0], synthetic_projection=True), *ARM_DERIVATIONS[1:]),
        (dict(ARM_DERIVATIONS[0], derived_from_arm_id=""), *ARM_DERIVATIONS[1:]),
        (dict(ARM_DERIVATIONS[0], extra="x"), *ARM_DERIVATIONS[1:]),
    )
    for bad in bad_cases:
        with pytest.raises(CompatibilityError):
            _report(arm_derivations=bad)


def test_report_identity_inputs_are_validated():
    for kwargs in (
        {"fixture_id": ""},
        {"fixture_id": None},
        {"code_sha": "abc"},
        {"code_sha": "G" * 64},
        {"code_sha": ""},
    ):
        with pytest.raises(CompatibilityError):
            _report(**kwargs)


def test_b07_markers_use_metric_not_implemented_and_are_required():
    assert [state["reason"] for state in B07_NOT_COMPUTABLE] == [
        "POOLED_GROUND_TRUTH",
        "METRIC_NOT_IMPLEMENTED",
    ]
    for metric_id, reason in (
        ("recall_at_5", "POOLED_GROUND_TRUTH"),
        ("ndcg_at_10", "METRIC_NOT_IMPLEMENTED"),
    ):
        assert {"metric_id": metric_id, "status": "NOT_COMPUTABLE", "reason": reason} in [
            dict(state) for state in B07_NOT_COMPUTABLE
        ]

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    for bad_states in (
        [],
        [{"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE", "reason": "POOLED_GROUND_TRUTH"}],
        [{"metric_id": "ndcg_at_10", "status": "NOT_COMPUTABLE", "reason": "ZERO_IDCG"}],
        [{"metric_id": "unknown", "status": "NOT_COMPUTABLE", "reason": "METRIC_NOT_IMPLEMENTED"}],
        [{"metric_id": "recall_at_5", "status": "COMPUTABLE", "reason": "POOLED_GROUND_TRUTH"}],
    ):
        biased = json.loads(json.dumps(contract))
        biased["b07_metric_states"] = bad_states
        with pytest.raises(CompatibilityError):
            _report(contract=biased)


def test_validity_is_separate_from_outcome():
    report = _report()
    assert [(pair["validity"], pair["outcome"]) for pair in report["pairwise_evaluations"]] == [
        ("VALID", "PASS"), ("VALID", "PASS"), ("VALID", "FAIL"),
    ]
    assert {pair["conclusion"] for pair in report["pairwise_evaluations"]} <= UNITS

    invalid = _report(protocol_validity="INVALID_PROTOCOL")
    for pair in invalid["pairwise_evaluations"]:
        assert pair["validity"] == "INVALID_PROTOCOL"
        assert pair["outcome"] == "NOT_EVALUATED"
        assert pair["benchmark_status"] == "INVALID_PROTOCOL"
        assert pair["primary_value"] is None
        assert pair["arm_values"] == {}
        assert pair["conclusion"] == "COMPARISON_INVALID_NO_OUTCOME_CLAIM"
        assert "FAIL" not in (pair["outcome"], pair["benchmark_status"])
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(invalid, _schema("three_arm_compat_report.json"))


def test_synthetic_judgments_reject_real_editorial_evidence_classes():
    from dataclasses import replace

    contract, descriptors, policies, manifest, rankings, judgments = _case()
    real = (replace(judgments[0], evidence_class="EDITORIAL_INFERENCE"),)
    with pytest.raises(CompatibilityError, match="synthetic"):
        _report(judgments=real)
    not_synthetic = (replace(judgments[0], synthetic=False),)
    with pytest.raises(CompatibilityError, match="synthetic"):
        _report(judgments=not_synthetic)


def test_built_report_is_schema_valid_and_deterministic():
    jsonschema = pytest.importorskip("jsonschema")
    report = _report()
    jsonschema.validate(report, _schema("three_arm_compat_report.json"))

    first = canonical_bytes(report)
    second = canonical_bytes(_report())
    assert first == second
    assert sha256_digest(report) == sha256_digest(_report())


def test_report_schema_rejects_invalid_evidence_promotion_and_vocabularies():
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema("three_arm_compat_report.json")
    report = _report()

    def mutated(**changes):
        candidate = json.loads(json.dumps(report))
        candidate.update(changes)
        return candidate

    for bad in (
        mutated(evidence_status="MODEL_EVIDENCE"),
        mutated(evaluation_scope="OPERATIONAL_B00_B18"),
        mutated(benchmark_readiness="BENCHMARK_READY"),
        mutated(winner_status="VIP_V2_BASE"),
        mutated(limitations=[]),
        mutated(arm_derivations=[]),
        mutated(judgment_evidence_class="EDITORIAL_INFERENCE"),
        mutated(b07_metric_states=[]),
        mutated(b07_metric_states=[{"metric_id": "ndcg_at_10", "status": "NOT_COMPUTABLE",
                                    "reason": "ZERO_IDCG"}]),
        mutated(fixture_id=""),
        mutated(contract_digest="not-a-digest"),
        mutated(code_sha="abc"),
    ):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)


def test_report_schema_rejects_cross_field_outcome_violations():
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema("three_arm_compat_report.json")
    report = _report()
    pair = report["pairwise_evaluations"][0]

    def mutated_pair(**changes):
        candidate = json.loads(json.dumps(report))
        candidate["pairwise_evaluations"][0] = {**pair, **changes}
        return candidate

    for bad in (
        mutated_pair(validity="INVALID_PROTOCOL"),
        mutated_pair(outcome="NOT_EVALUATED"),
        mutated_pair(benchmark_status="INVALID_PROTOCOL"),
        mutated_pair(outcome="PASS", validity="INVALID_PROTOCOL",
                     benchmark_status="INVALID_PROTOCOL", primary_value=None, arm_values={}),
        mutated_pair(primary_metric_id="ndcg_at_10"),
        mutated_pair(failure_class="FROZEN_PROTOCOL_MUTATION_REJECTED"),
        mutated_pair(conclusion="SOMETHING_ELSE"),
        mutated_pair(arm_values={"arm_a": 0.0, "not_an_arm": 1.0}),
        mutated_pair(arm_values={"arm_a": 0.0}),
        mutated_pair(coverage={"arm_a::SELECTED": -1}),
        mutated_pair(coverage={"arm_a::UNKNOWN": 1}),
        mutated_pair(validity="INVALID_PROTOCOL", outcome="NOT_EVALUATED",
                     benchmark_status="INVALID_PROTOCOL", primary_value=1.0,
                     arm_values={}),
    ):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)


def test_report_schema_pins_arm_values_to_the_pair_arm_ids():
    """C-2: a pair may only score exactly the two arms it compares."""
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema("three_arm_compat_report.json")
    report = _report()

    forged = json.loads(json.dumps(report))
    forged["pairwise_evaluations"][0]["arm_values"] = {
        "VIP_V2_BASE": 1.0, "VIP_V2_SO400M": 0.0,
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(forged, schema)

    forged = json.loads(json.dumps(report))
    forged["pairwise_evaluations"][2]["arm_values"] = {
        "VIP_V1_BASE": 1.0, "VIP_V2_BASE": 0.0,
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(forged, schema)


def test_report_schema_requires_exactly_the_frozen_charter_pairs():
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema("three_arm_compat_report.json")
    report = _report()
    assert [tuple(pair["arm_ids"]) for pair in report["pairwise_evaluations"]] == list(CHARTER_PAIRS)

    duplicated = json.loads(json.dumps(report))
    duplicated["pairwise_evaluations"][2] = duplicated["pairwise_evaluations"][0]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(duplicated, schema)

    missing = json.loads(json.dumps(report))
    missing["pairwise_evaluations"] = missing["pairwise_evaluations"][:2]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(missing, schema)


def test_code_sha_is_recomputed_from_module_bytes_and_changes_on_mutation(tmp_path, monkeypatch):
    """C-4: prove the digest is genuinely derived from bytes, not a constant."""
    import gate1.harness as harness

    fake_package = tmp_path / "gate1"
    fake_package.mkdir()
    (fake_package / "a.py").write_bytes(b"# module a\n")
    (fake_package / "b.py").write_bytes(b"# module b\n")
    paths = ("a.py", "b.py")
    monkeypatch.setattr(harness, "_PRODUCING_MODULE_PATHS", paths)
    monkeypatch.setattr(harness, "__file__", str(fake_package / "harness.py"))

    first = harness.gate1_code_sha()
    assert first == _independent_code_sha(fake_package, paths)

    (fake_package / "b.py").write_bytes(b"# module b changed\n")
    second = harness.gate1_code_sha()
    assert second != first
    assert second == _independent_code_sha(fake_package, paths)
    assert harness.gate1_code_sha() == second == _independent_code_sha(fake_package, paths)
