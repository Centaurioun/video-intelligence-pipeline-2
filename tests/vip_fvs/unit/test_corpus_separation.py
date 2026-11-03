"""Synthetic-only tests for the P1 corpus-separation verifier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from vip_fvs import corpus_separation as cs
from gate0.identity import opaque_id


P1_CASE_TO_TESTS = {
    1: ("test_synthetic_complete_evidence_emits_exact_deterministic_attestation",),
    2: ("test_exact_candidate_digest_collision_refuses",),
    3: ("test_exact_candidate_digest_collision_refuses",),
    4: ("test_matching_locator_alone_does_not_create_candidate_collision",),
    5: ("test_case_5_expanded_inventory_membership_digest_collision_refuses",),
    6: ("test_relation_transitive_candidate_collision_refuses",),
    7: ("test_relation_transitive_candidate_collision_refuses",),
    8: ("test_candidate_self_cycle_is_finite_and_cannot_hide_unknown_edge",),
    9: ("test_duplicate_and_reordered_relation_rows_have_stable_graph_results",),
    10: ("test_malformed_candidate_digest_duplicate_inventory_and_empty_membership_refuse",),
    11: ("test_candidate_identity_labels_split_and_relation_coverage_refuse",),
    12: ("test_malformed_candidate_digest_duplicate_inventory_and_empty_membership_refuse",),
    13: ("test_missing_gate0_membership_refuses", "test_malformed_candidate_digest_duplicate_inventory_and_empty_membership_refuse"),
    14: ("test_missing_gate0_membership_refuses",),
    15: ("test_missing_gate0_membership_refuses",),
    16: ("test_option_r_reference_is_closed_and_duplicate_json_keys_refuse", "test_configured_root_resolver_checks_canonical_metadata_digest"),
    17: ("test_frozen_membership_and_trust_chain_fail_closed",),
    18: ("test_candidate_identity_labels_split_and_relation_coverage_refuse",),
    19: ("test_producer_rights_and_stale_parent_references_refuse", "test_candidate_identity_labels_split_and_relation_coverage_refuse"),
    20: ("test_option_r_reference_is_closed_and_duplicate_json_keys_refuse", "test_candidate_identity_labels_split_and_relation_coverage_refuse"),
    21: ("test_candidate_identity_labels_split_and_relation_coverage_refuse",),
    22: ("test_synthetic_complete_evidence_emits_exact_deterministic_attestation",),
    23: ("test_attestation_tampering_and_changed_time_are_distinguished",),
    25: ("test_resolver_rejects_escape_and_symlink", "test_configured_root_resolver_checks_canonical_metadata_digest", "test_fifo_replacement_is_refused_without_blocking"),
    29: ("test_synthetic_complete_evidence_emits_exact_deterministic_attestation",),
    30: ("test_case_30_cross_artifact_child_run_mismatch_is_refused", "test_producer_rights_and_stale_parent_references_refuse"),
    31: ("test_candidate_identity_labels_split_and_relation_coverage_refuse", "test_producer_rights_and_stale_parent_references_refuse"),
    32: ("test_valid_self_digest_does_not_establish_authenticity", "test_missing_or_unknown_issuer_and_policy_binding_refuse"),
    33: ("test_candidate_identity_labels_split_and_relation_coverage_refuse", "test_candidate_self_cycle_is_finite_and_cannot_hide_unknown_edge"),
    34: ("test_relation_transitive_candidate_collision_refuses", "test_cross_split_candidate_relation_graph_refuses"),
    35: ("test_producer_rights_and_stale_parent_references_refuse",),
    36: ("test_attestation_tampering_and_changed_time_are_distinguished",),
}
P1_OUT_OF_SCOPE_CASES = (24, 26, 27, 28)
P1_REFUSAL_TO_TESTS = {
    "CORPUS_SEPARATION_ATTESTATION_REQUIRED": ("test_missing_gate0_membership_refuses",),
    "CORPUS_SEPARATION_EVIDENCE_INCOMPLETE": ("test_case_30_cross_artifact_child_run_mismatch_is_refused", "test_frozen_membership_and_trust_chain_fail_closed"),
    "CORPUS_SEPARATION_CANDIDATE_IDENTITY_REQUIRED": ("test_candidate_identity_labels_split_and_relation_coverage_refuse",),
    "CORPUS_SEPARATION_RELATION_COVERAGE_UNVERIFIED": ("test_candidate_identity_labels_split_and_relation_coverage_refuse", "test_producer_rights_and_stale_parent_references_refuse"),
    "CORPUS_SEPARATION_OUTPUT_PATH_INVALID": ("test_resolver_rejects_escape_and_symlink", "test_configured_root_resolver_checks_canonical_metadata_digest"),
    "CORPUS_SEPARATION_DECLARATION_INVALID": ("test_option_r_reference_is_closed_and_duplicate_json_keys_refuse", "test_candidate_identity_labels_split_and_relation_coverage_refuse"),
    "CORPUS_SEPARATION_LABEL_VERSION_UNBOUND": ("test_candidate_identity_labels_split_and_relation_coverage_refuse",),
    "CORPUS_SEPARATION_DIGEST_COLLISION": ("test_exact_candidate_digest_collision_refuses", "test_case_5_expanded_inventory_membership_digest_collision_refuses"),
    "CORPUS_SEPARATION_GROUP_COLLISION": ("test_relation_transitive_candidate_collision_refuses", "test_cross_split_candidate_relation_graph_refuses"),
    "CORPUS_SEPARATION_ATTESTATION_DIGEST_MISMATCH": ("test_attestation_tampering_and_changed_time_are_distinguished",),
}


def test_p1_case_and_refusal_maps_resolve_to_executable_tests() -> None:
    expected_cases = set(range(1, 24)) | {25} | set(range(29, 37))
    assert set(P1_CASE_TO_TESTS) == expected_cases
    assert P1_OUT_OF_SCOPE_CASES == (24, 26, 27, 28)
    assert all(name in globals() and callable(globals()[name]) for names in P1_CASE_TO_TESTS.values() for name in names)
    assert all(name in globals() and callable(globals()[name]) for names in P1_REFUSAL_TO_TESTS.values() for name in names)


def _digest(value: object) -> str:
    return hashlib.sha256(cs.canonical_bytes(value)).hexdigest()


def _ref() -> dict:
    return {
        "schema_version": "vip_fvs.corpus_separation_ref.v1",
        "artifact_id": "synthetic:evidence-1",
        "artifact_schema_version": "vip_fvs.corpus_separation_evidence.v1",
        "canonical_content_sha256": "0" * 64,
        "authorized_root_id": "synthetic-root",
        "issuer_policy_ref": "synthetic-policy:v1",
    }


def _fixture() -> dict:
    inventory = [
        {"revision_id": "eval-a", "source_sha256": "a" * 64, "status": "INCLUDED"},
        {"revision_id": "dev-b", "source_sha256": "b" * 64, "status": "INCLUDED"},
    ]
    nodes = ["eval-a", "dev-b"]
    edges: list[list[str]] = []
    return {
        "schema_version": "vip_fvs.corpus_separation_evidence.v1",
        "artifact_id": "synthetic:evidence-1",
        "evidence_state": "SYNTHETIC_ONLY",
        "issuer_policy_ref": "synthetic-policy:v1",
        "run_id": "synthetic:run-1",
        "corpus_id": "synthetic:candidate-corpus",
        "inventory": {"records": inventory, "digest": _digest(inventory), "run_id": "synthetic:run-1", "producer_id": "synthetic:gate0"},
        "relation_inventory": {"nodes": nodes, "edges": edges, "digest": _digest({"nodes": nodes, "edges": edges}), "run_id": "synthetic:run-1", "producer_id": "synthetic:gate0"},
        "split": {"allocations": {opaque_id("component", ("eval-a",)): "EVALUATION",
                                   opaque_id("component", ("dev-b",)): "DEVELOPMENT"},
                  "relation_inventory_digest": _digest({"nodes": nodes, "edges": edges}), "run_id": "synthetic:run-1", "producer_id": "synthetic:gate0"},
        "evaluation_membership": {"revision_ids": ["eval-a"], "count": 1, "run_id": "synthetic:run-1", "producer_id": "synthetic:gate0"},
        "development_membership": {"revision_ids": ["dev-b"], "count": 1, "run_id": "synthetic:run-1", "producer_id": "synthetic:gate0"},
        "label_version_refs": [{"artifact_id": "synthetic:labels", "digest": "c" * 64, "run_id": "synthetic:run-1", "producer_id": "synthetic:gate0"}],
        "policy_rights_refs": [{"artifact_id": "synthetic:rights", "status": "ALLOW", "run_id": "synthetic:run-1", "producer_id": "synthetic:gate0"}],
        "candidate": {"revision_id": "candidate-c", "source_sha256": "d" * 64},
        "candidate_relation": {"nodes": ["eval-a", "dev-b", "candidate-c"], "edges": [], "claimed_complete": True,
                               "method_ref": "synthetic:method:v1", "authorization_scope_digest": "0" * 64,
                               "run_id": "synthetic:run-1", "producer_id": "synthetic:relations",
                               "inventory_digest": "0" * 64, "split_digest": "0" * 64, "gate0_relation_digest": "0" * 64},
        "trust": {"issuer_ref": "synthetic:issuer", "acceptance_ref": "synthetic:acceptance:v1", "revocation_ref": "synthetic:revocation:v1", "accepted": True, "revoked": False,
                  "accepted_producer_ids": ["synthetic:gate0", "synthetic:relations"]},
    }


def _synthetic_trust_policy(evidence: dict, reference: dict) -> dict | None:
    """Explicit test-only allowlist bound to exact evidence bytes and provenance."""
    trust = evidence.get("trust", {})
    accepted = (
        trust.get("issuer_ref") == "synthetic:issuer"
        and trust.get("acceptance_ref") == "synthetic:acceptance:v1"
        and reference.get("issuer_policy_ref") == "synthetic-policy:v1"
        and reference.get("artifact_id") == "synthetic:evidence-1"
        and reference.get("canonical_content_sha256") == _digest(evidence)
        and evidence.get("run_id") == "synthetic:run-1"
        and trust.get("accepted_producer_ids") == ["synthetic:gate0", "synthetic:relations"]
        and trust.get("accepted") is True
        and trust.get("revoked") is False
    )
    if not accepted:
        return None
    return {"issuer_ref": "synthetic:issuer", "issuer_policy_ref": "synthetic-policy:v1",
            "artifact_id": "synthetic:evidence-1", "canonical_content_sha256": _digest(evidence),
            "run_id": "synthetic:run-1", "accepted_producer_ids": ["synthetic:gate0", "synthetic:relations"],
            "acceptance_ref": "synthetic:acceptance:v1", "revocation_ref": "synthetic:revocation:v1",
            "accepted": True, "revoked": False, "evidence_state": "SYNTHETIC_ONLY"}


def _verify(evidence: dict, authorization: dict, checked_at: str = "2026-01-01T00:00:00Z", trust_policy=None) -> dict:
    ref = _ref()
    authorization = dict(authorization)
    if "schema_version" not in authorization:
        authorization["schema_version"] = "vip_fvs.pilot_authorization.v2"
        authorization["corpus_separation_ref"] = ref
    for key, expected in (("authorization_scope_digest", cs.authorization_scope_digest(authorization)),
                          ("inventory_digest", evidence["inventory"]["digest"]),
                          ("split_digest", _digest(evidence["split"])),
                          ("gate0_relation_digest", evidence["relation_inventory"]["digest"])):
        if evidence["candidate_relation"][key] == "0" * 64:
            evidence["candidate_relation"][key] = expected
    ref["canonical_content_sha256"] = _digest(evidence)
    ref["issuer_policy_ref"] = evidence.get("issuer_policy_ref", ref["issuer_policy_ref"])
    if authorization.get("corpus_separation_ref") == _ref():
        authorization["corpus_separation_ref"] = ref
    return cs.verify_synthetic(evidence, ref, authorization=authorization, checked_at=checked_at,
                               trust_policy=trust_policy or _synthetic_trust_policy)


def test_option_r_reference_is_closed_and_duplicate_json_keys_refuse() -> None:
    ref = _ref()
    assert cs.parse_reference(ref) == ref
    with pytest.raises(cs.CorpusSeparationError, match="DECLARATION_INVALID"):
        cs.parse_reference({**ref, "unexpected": True})
    with pytest.raises(cs.CorpusSeparationError, match="DECLARATION_INVALID"):
        cs.parse_json(b'{"a":1,"a":2}')
    with pytest.raises(cs.CorpusSeparationError, match="DECLARATION_INVALID"):
        cs.parse_json(b'{ "a":1}')


def test_reference_and_evidence_schema_instances_match_parser_shape() -> None:
    schema_dir = Path(__file__).resolve().parents[3] / "schemas" / "vip_fvs"
    ref_schema = json.loads((schema_dir / "corpus_separation_ref.v1.json").read_text())
    evidence_schema = json.loads((schema_dir / "corpus_separation_evidence.v1.json").read_text())
    Draft202012Validator.check_schema(ref_schema)
    Draft202012Validator.check_schema(evidence_schema)
    reference = _ref()
    evidence = _fixture()
    assert not list(Draft202012Validator(ref_schema).iter_errors(reference))
    assert not list(Draft202012Validator(evidence_schema).iter_errors(evidence))
    assert cs.parse_reference(reference) == reference
    assert _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})
    malformed_ref = {**reference, "artifact_id": " "}
    assert list(Draft202012Validator(ref_schema).iter_errors(malformed_ref))
    with pytest.raises(cs.CorpusSeparationError, match="DECLARATION_INVALID"):
        cs.parse_reference(malformed_ref)
    malformed_evidence = _fixture()
    malformed_evidence["relation_inventory"]["nodes"] = [["nested"]]
    assert list(Draft202012Validator(evidence_schema).iter_errors(malformed_evidence))


def test_v2_authorization_must_bind_exact_option_r_reference() -> None:
    evidence = _fixture()
    authorization = {"schema_version": "vip_fvs.pilot_authorization.v2",
                     "source_revision_id": "candidate-c", "source_sha256": "d" * 64}
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, authorization)

    evidence = _fixture()
    authorization["corpus_separation_ref"] = {**_ref(), "artifact_id": "synthetic:other-evidence"}
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, authorization)


def test_authorization_scope_projection_excludes_cycle_fields() -> None:
    before = {"authorization_id": "auth-1", "source_revision_id": "candidate-c", "source_sha256": "d" * 64,
              "policy_digest": "e" * 64, "scope_digest": "f" * 64, "record_digest": "1" * 64}
    after = {**before, "record_digest": "2" * 64, "corpus_separation_ref": _ref()}
    assert cs.authorization_scope_digest(before) == cs.authorization_scope_digest(after)
    assert cs.authorization_scope_digest({**after, "scope_digest": "0" * 64}) != cs.authorization_scope_digest(before)


def test_synthetic_complete_evidence_emits_exact_deterministic_attestation() -> None:
    evidence = _fixture()
    ref = _ref()
    ref["canonical_content_sha256"] = _digest(evidence)
    auth = {"source_revision_id": "candidate-c", "source_sha256": "d" * 64, "authorization_id": "auth-1", "policy_digest": "e" * 64, "scope_digest": "f" * 64}
    first = _verify(evidence, auth)
    second = _verify(json.loads(cs.canonical_bytes(evidence)), auth)
    assert list(first) == list(second)
    assert len(first) == 28
    assert first["authenticity_status"] == "SYNTHETIC_TRUST_DOUBLE_ONLY"
    assert first["transform_equivalence_status"] == "NOT_OBSERVED"
    assert first["judgment_separation_status"] == "NOT_OBSERVED"
    assert cs.canonical_bytes(first) == cs.canonical_bytes(second)
    cs.validate_attestation(cs.parse_json(cs.canonical_bytes(first)))


@pytest.mark.parametrize("role", ["EVALUATION", "DEVELOPMENT"])
def test_exact_candidate_digest_collision_refuses(role: str) -> None:
    evidence = _fixture()
    evidence["candidate"]["source_sha256"] = "a" * 64 if role == "EVALUATION" else "b" * 64
    with pytest.raises(cs.CorpusSeparationError, match="DIGEST_COLLISION"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": evidence["candidate"]["source_sha256"]})


def test_case_5_expanded_inventory_membership_digest_collision_refuses() -> None:
    evidence = _fixture()
    evidence["inventory"]["records"].append({"revision_id": "eval-c", "source_sha256": "e" * 64, "status": "INCLUDED"})
    evidence["inventory"]["digest"] = _digest(evidence["inventory"]["records"])
    rel = evidence["relation_inventory"]
    rel["nodes"].append("eval-c"); rel["edges"].append(["eval-a", "eval-c"])
    rel["digest"] = _digest({"nodes": rel["nodes"], "edges": rel["edges"]})
    split = evidence["split"]
    split["allocations"].pop(opaque_id("component", ("eval-a",)))
    split["allocations"][opaque_id("component", ("eval-a", "eval-c"))] = "EVALUATION"
    split["relation_inventory_digest"] = rel["digest"]
    evidence["evaluation_membership"] = {**evidence["evaluation_membership"], "revision_ids": ["eval-a", "eval-c"], "count": 2}
    evidence["candidate_relation"]["nodes"].append("eval-c")
    evidence["candidate"]["source_sha256"] = "e" * 64
    with pytest.raises(cs.CorpusSeparationError, match="DIGEST_COLLISION"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "e" * 64})


def test_matching_locator_alone_does_not_create_candidate_collision() -> None:
    evidence = _fixture()
    evidence["candidate"]["locator"] = "synthetic/path/same-name.mp4"
    result = _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})
    assert result["digest_intersection"] == []


def test_relation_transitive_candidate_collision_refuses() -> None:
    evidence = _fixture()
    evidence["candidate_relation"]["nodes"] = ["eval-a", "dev-b", "middle", "candidate-c"]
    evidence["candidate_relation"]["edges"] = [["eval-a", "middle"], ["middle", "candidate-c"]]
    with pytest.raises(cs.CorpusSeparationError, match="GROUP_COLLISION"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_attestation_tampering_and_changed_time_are_distinguished() -> None:
    evidence = _fixture()
    auth = {"source_revision_id": "candidate-c", "source_sha256": "d" * 64}
    first = _verify(evidence, auth)
    later = _verify(evidence, auth, checked_at="2026-01-02T00:00:00Z")
    assert first["deterministic_input_digest"] == later["deterministic_input_digest"]
    assert first["attestation_digest"] != later["attestation_digest"]
    first["corpus_id"] = "tampered"
    with pytest.raises(cs.CorpusSeparationError, match="ATTESTATION_DIGEST_MISMATCH"):
        cs.validate_attestation(first)


@pytest.mark.parametrize("missing", [
    "declared_universe_digest", "declared_node_count", "claimed_coverage_status", "method_ref",
])
def test_attestation_missing_coverage_projection_key_is_stable_refusal(missing: str) -> None:
    attestation = _verify(_fixture(), {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})
    attestation["candidate_relation_coverage"].pop(missing)
    body = dict(attestation)
    body.pop("attestation_digest")
    attestation["attestation_digest"] = _digest(body)
    with pytest.raises(cs.CorpusSeparationError, match="ATTESTATION_DIGEST_MISMATCH"):
        cs.validate_attestation(attestation)


@pytest.mark.parametrize(("field", "value"), [
    ("declared_universe_digest", ["nested"]),
    ("declared_node_count", True),
    ("claimed_coverage_status", {"nested": True}),
    ("method_ref", ["nested"]),
])
def test_attestation_wrong_coverage_types_are_stable_refusals(field: str, value: object) -> None:
    attestation = _verify(_fixture(), {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})
    attestation["candidate_relation_coverage"][field] = value
    body = dict(attestation)
    body.pop("attestation_digest")
    attestation["attestation_digest"] = _digest(body)
    with pytest.raises(cs.CorpusSeparationError, match="ATTESTATION_DIGEST_MISMATCH"):
        cs.validate_attestation(attestation)


@pytest.mark.parametrize(
    ("path", "replacement", "refusal"),
    [
        (("relation_inventory", "nodes"), [["nested"]], "EVIDENCE_INCOMPLETE"),
        (("relation_inventory", "edges"), [[{"nested": "node"}, "eval-a"]], "EVIDENCE_INCOMPLETE"),
        (("candidate_relation", "nodes"), [["nested"]], "RELATION_COVERAGE_UNVERIFIED"),
        (("candidate_relation", "edges"), [[{"nested": "node"}, "candidate-c"]], "RELATION_COVERAGE_UNVERIFIED"),
    ],
)
def test_nested_json_graph_values_refuse_without_leaking_typeerror(
    path: tuple[str, str], replacement: list[object], refusal: str,
) -> None:
    evidence = _fixture()
    evidence[path[0]][path[1]] = replacement
    if path == ("relation_inventory", "edges"):
        rel = evidence["relation_inventory"]
        rel["digest"] = _digest({"nodes": rel["nodes"], "edges": rel["edges"]})
    with pytest.raises(cs.CorpusSeparationError, match=refusal):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_nested_membership_values_and_boolean_counts_refuse() -> None:
    evidence = _fixture()
    evidence["evaluation_membership"]["revision_ids"] = [["eval-a"]]
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture()
    component_id = opaque_id("component", ("eval-a",))
    evidence["split"]["allocations"][component_id] = ["EVALUATION"]
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture()
    evidence["evaluation_membership"]["count"] = True
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_resolver_rejects_escape_and_symlink(tmp_path: Path) -> None:
    root = tmp_path / "root"; root.mkdir()
    outside = tmp_path / "outside.json"; outside.write_text("{}", encoding="utf-8")
    with pytest.raises(cs.CorpusSeparationError, match="OUTPUT_PATH_INVALID"):
        cs.resolve_artifact(root, "../outside.json")
    link = root / "link.json"; link.symlink_to(outside)
    with pytest.raises(cs.CorpusSeparationError, match="OUTPUT_PATH_INVALID"):
        cs.resolve_artifact(root, "link.json")


def test_configured_root_resolver_checks_canonical_metadata_digest(tmp_path: Path) -> None:
    root = tmp_path / "root"; root.mkdir()
    evidence = _fixture()
    metadata = root / "evidence.json"
    metadata.write_bytes(cs.canonical_bytes(evidence))
    ref = _ref(); ref["canonical_content_sha256"] = hashlib.sha256(metadata.read_bytes()).hexdigest()
    protected = tmp_path / "protected"; protected.mkdir()
    path, loaded = cs.load_referenced_metadata(ref, {"synthetic-root": root}, "evidence.json", protected_roots=(protected,))
    assert path == metadata and loaded == evidence
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        cs.load_referenced_metadata(ref, {"other-root": root}, "evidence.json", protected_roots=(protected,))
    ref["canonical_content_sha256"] = "0" * 64
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        cs.load_referenced_metadata(ref, {"synthetic-root": root}, "evidence.json", protected_roots=(protected,))
    with pytest.raises(cs.CorpusSeparationError, match="OUTPUT_PATH_INVALID"):
        cs.resolve_artifact(root, "evidence.json", protected_roots=(root,))
    with pytest.raises(cs.CorpusSeparationError, match="OUTPUT_PATH_INVALID"):
        cs.resolve_artifact(root, "evidence.json", protected_roots=(tmp_path,))

    noncanonical = root / "noncanonical.json"
    noncanonical_bytes = b'{ "schema_version":"vip_fvs.corpus_separation_evidence.v1"}'
    noncanonical.write_bytes(noncanonical_bytes)
    ref["canonical_content_sha256"] = hashlib.sha256(noncanonical_bytes).hexdigest()
    with pytest.raises(cs.CorpusSeparationError, match="DECLARATION_INVALID"):
        cs.load_referenced_metadata(ref, {"synthetic-root": root}, "noncanonical.json", protected_roots=(protected,))


def test_metadata_root_failures_size_bound_and_in_root_hardlink(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    protected = tmp_path / "protected"
    protected.mkdir()
    evidence = _fixture()
    metadata = root / "evidence.json"
    raw = cs.canonical_bytes(evidence)
    metadata.write_bytes(raw)
    ref = _ref()
    ref["canonical_content_sha256"] = hashlib.sha256(raw).hexdigest()
    alias = root / "alias.json"
    alias.hardlink_to(metadata)
    _, loaded = cs.load_referenced_metadata(ref, {"synthetic-root": root}, "alias.json", protected_roots=(protected,))
    assert loaded == evidence

    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        cs.load_referenced_metadata(ref, {"synthetic-root": root}, "evidence.json", protected_roots=())

    regular_file = tmp_path / "not-a-directory"
    regular_file.write_bytes(b"synthetic")
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        cs.load_referenced_metadata(ref, {"synthetic-root": regular_file}, "evidence.json", protected_roots=(protected,))

    oversized = root / "oversized.json"
    oversized.write_bytes(b" " * (4 * 1024 * 1024 + 1))
    ref["canonical_content_sha256"] = hashlib.sha256(oversized.read_bytes()).hexdigest()
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        cs.load_referenced_metadata(ref, {"synthetic-root": root}, "oversized.json", protected_roots=(protected,))


def test_path_replacement_after_resolution_cannot_swap_the_opened_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "authorized"; root.mkdir()
    protected = tmp_path / "protected"; protected.mkdir()
    displaced = tmp_path / "authorized-displaced"
    allowed = _fixture(); allowed["corpus_id"] = "synthetic:allowed"
    protected_evidence = _fixture(); protected_evidence["corpus_id"] = "synthetic:protected"
    (root / "evidence.json").write_bytes(cs.canonical_bytes(allowed))
    (protected / "evidence.json").write_bytes(cs.canonical_bytes(protected_evidence))
    ref = _ref(); ref["canonical_content_sha256"] = hashlib.sha256((protected / "evidence.json").read_bytes()).hexdigest()
    real_resolve = cs.resolve_artifact
    swapped: list[bool] = []

    def replace_after_check(base: Path, relative: str, *, protected_roots: tuple[Path, ...] = ()) -> Path:
        result = real_resolve(base, relative, protected_roots=protected_roots)
        root.rename(displaced)
        protected.rename(root)
        swapped.append(True)
        return result

    monkeypatch.setattr(cs, "resolve_artifact", replace_after_check)
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        cs.load_referenced_metadata(ref, {"synthetic-root": root}, "evidence.json", protected_roots=(protected,))
    assert swapped == [True]


def test_fifo_replacement_is_refused_without_blocking(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "authorized"; root.mkdir()
    protected = tmp_path / "protected"; protected.mkdir()
    metadata = root / "evidence.json"
    metadata.write_bytes(cs.canonical_bytes(_fixture()))
    ref = _ref(); ref["canonical_content_sha256"] = hashlib.sha256(metadata.read_bytes()).hexdigest()
    real_resolve = cs.resolve_artifact

    def replace_with_fifo(base: Path, relative: str, *, protected_roots: tuple[Path, ...] = ()) -> Path:
        result = real_resolve(base, relative, protected_roots=protected_roots)
        metadata.unlink()
        import os
        os.mkfifo(metadata)
        return result

    monkeypatch.setattr(cs, "resolve_artifact", replace_with_fifo)
    with pytest.raises(cs.CorpusSeparationError, match="OUTPUT_PATH_INVALID"):
        cs.load_referenced_metadata(ref, {"synthetic-root": root}, "evidence.json", protected_roots=(protected,))


def test_valid_self_digest_does_not_establish_authenticity(tmp_path: Path) -> None:
    root = tmp_path / "root"; root.mkdir()
    evidence = _fixture()
    artifact = root / "evidence.json"; artifact.write_bytes(cs.canonical_bytes(evidence))
    ref = _ref(); ref["canonical_content_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    protected = tmp_path / "protected"; protected.mkdir()
    _, loaded = cs.load_referenced_metadata(ref, {"synthetic-root": root}, "evidence.json", protected_roots=(protected,))
    assert loaded == evidence  # Exact bytes and self-digest establish integrity only.
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        cs.verify_synthetic(loaded, ref, authorization={"source_revision_id": "candidate-c", "source_sha256": "d" * 64},
                            checked_at="2026-01-01T00:00:00Z")


def test_boolean_trust_policy_answer_cannot_authenticate_evidence() -> None:
    evidence = _fixture()
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64},
                trust_policy=lambda *_: True)


def test_trust_policy_exception_becomes_stable_refusal() -> None:
    evidence = _fixture()

    def broken_trust_policy(*_args):
        raise RuntimeError("synthetic trust lookup failed")

    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64},
                trust_policy=broken_trust_policy)


def test_missing_or_unknown_issuer_and_policy_binding_refuse() -> None:
    evidence = _fixture(); evidence["trust"].pop("issuer_ref")
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["trust"]["issuer_ref"] = "synthetic:unknown-issuer"
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["issuer_policy_ref"] = "synthetic:unknown-policy:v99"
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["trust"].pop("acceptance_ref")
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_frozen_membership_and_trust_chain_fail_closed() -> None:
    evidence = _fixture()
    evidence["evaluation_membership"]["revision_ids"] = ["eval-a", "dev-b"]
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["trust"]["revoked"] = True
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture()
    ref = _ref(); ref["canonical_content_sha256"] = _digest(evidence)
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        cs.verify_synthetic(evidence, ref, authorization={"source_revision_id": "candidate-c", "source_sha256": "d" * 64},
                            checked_at="2026-01-01T00:00:00Z", trust_policy=lambda *_: False)


@pytest.mark.parametrize("missing", ["evaluation_membership", "development_membership"])
def test_missing_gate0_membership_refuses(missing: str) -> None:
    evidence = _fixture(); evidence.pop(missing)
    with pytest.raises(cs.CorpusSeparationError, match="ATTESTATION_REQUIRED"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_case_30_cross_artifact_child_run_mismatch_is_refused() -> None:
    evidence = _fixture()
    evidence["split"]["run_id"] = "synthetic:other-run"
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_candidate_identity_labels_split_and_relation_coverage_refuse() -> None:
    evidence = _fixture(); evidence.pop("candidate")
    with pytest.raises(cs.CorpusSeparationError, match="CANDIDATE_IDENTITY_REQUIRED"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["candidate"]["revision_id"] = ""
    with pytest.raises(cs.CorpusSeparationError, match="CANDIDATE_IDENTITY_REQUIRED"):
        _verify(evidence, {"source_revision_id": "", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["candidate"]["revision_id"] = 42
    with pytest.raises(cs.CorpusSeparationError, match="DECLARATION_INVALID"):
        _verify(evidence, {"source_revision_id": 42, "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["candidate"]["corpus_role"] = "GATE0_EVALUATION"
    with pytest.raises(cs.CorpusSeparationError, match="DECLARATION_INVALID"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["split"]["allocations"].pop(opaque_id("component", ("dev-b",)))
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["label_version_refs"] = []
    with pytest.raises(cs.CorpusSeparationError, match="LABEL_VERSION_UNBOUND"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["split"]["relation_inventory_digest"] = "f" * 64
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["candidate_relation"]["nodes"].remove("dev-b")
    with pytest.raises(cs.CorpusSeparationError, match="RELATION_COVERAGE_UNVERIFIED"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_cross_split_candidate_relation_graph_refuses() -> None:
    evidence = _fixture()
    evidence["candidate_relation"]["edges"] = [["eval-a", "dev-b"]]
    with pytest.raises(cs.CorpusSeparationError, match="GROUP_COLLISION"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_candidate_self_cycle_is_finite_and_cannot_hide_unknown_edge() -> None:
    evidence = _fixture()
    evidence["candidate_relation"]["nodes"] = ["eval-a", "dev-b", "candidate-c", "x", "y"]
    evidence["candidate_relation"]["edges"] = [["candidate-c", "x"], ["x", "y"], ["y", "candidate-c"]]
    result = _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})
    assert result["relation_component_intersection"] == []

    evidence["candidate_relation"]["edges"].append(["x", "unknown"])
    with pytest.raises(cs.CorpusSeparationError, match="RELATION_COVERAGE_UNVERIFIED"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_producer_rights_and_stale_parent_references_refuse() -> None:
    evidence = _fixture(); evidence["policy_rights_refs"][0]["producer_id"] = "synthetic:untrusted"
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["policy_rights_refs"][0]["status"] = "REVOKED"
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["candidate_relation"]["split_digest"] = "f" * 64
    with pytest.raises(cs.CorpusSeparationError, match="RELATION_COVERAGE_UNVERIFIED"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["candidate_relation"]["producer_id"] = "synthetic:untrusted-relations"
    with pytest.raises(cs.CorpusSeparationError, match="RELATION_COVERAGE_UNVERIFIED"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["candidate_relation"]["claimed_complete"] = False
    with pytest.raises(cs.CorpusSeparationError, match="RELATION_COVERAGE_UNVERIFIED"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_malformed_candidate_digest_duplicate_inventory_and_empty_membership_refuse() -> None:
    evidence = _fixture(); evidence["candidate"]["source_sha256"] = "D" * 64
    with pytest.raises(cs.CorpusSeparationError, match="DECLARATION_INVALID"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "D" * 64})

    evidence = _fixture(); evidence["inventory"]["records"].append(dict(evidence["inventory"]["records"][0]))
    evidence["inventory"]["digest"] = _digest(evidence["inventory"]["records"])
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})

    evidence = _fixture(); evidence["evaluation_membership"] = {"revision_ids": [], "count": 0}
    with pytest.raises(cs.CorpusSeparationError, match="EVIDENCE_INCOMPLETE"):
        _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})


def test_duplicate_and_reordered_relation_rows_have_stable_graph_results() -> None:
    evidence = _fixture()
    relation = evidence["candidate_relation"]
    relation["nodes"] = ["eval-a", "dev-b", "candidate-c", "x", "y"]
    relation["edges"] = [["candidate-c", "x"], ["x", "y"], ["y", "candidate-c"], ["candidate-c", "x"]]
    first = _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})
    relation["edges"] = list(reversed(relation["edges"]))
    second = _verify(evidence, {"source_revision_id": "candidate-c", "source_sha256": "d" * 64})
    assert first["relation_component_intersection"] == second["relation_component_intersection"] == []
