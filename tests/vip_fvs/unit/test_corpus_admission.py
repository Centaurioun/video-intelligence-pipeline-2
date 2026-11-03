"""Behavioral contracts for the opt-in synthetic preflight seam."""

from pathlib import Path
import hashlib

import pytest

from vip_fvs import corpus_separation as cs
from vip_fvs.corpus_admission import (
    AdmissionBinding,
    CorpusAdmissionError,
    SyntheticPreflightContext,
    check_synthetic_preflight,
    require_synthetic_preflight,
)


def _valid_synthetic_attestation(*, source_sha256: str = "d" * 64):
    # Reuse only the frozen P1 synthetic fixture builder; all admission assertions
    # below target the P2 contract, not P1 implementation internals.
    import test_corpus_separation as p1

    evidence = p1._fixture()
    evidence["candidate"]["source_sha256"] = source_sha256
    reference = p1._ref()
    authorization = {
        "schema_version": "vip_fvs.pilot_authorization.v2",
        "source_revision_id": "candidate-c",
        "source_sha256": source_sha256,
        "corpus_separation_ref": reference,
    }
    for key, expected in (
        ("authorization_scope_digest", cs.authorization_scope_digest(authorization)),
        ("inventory_digest", evidence["inventory"]["digest"]),
        ("split_digest", hashlib.sha256(cs.canonical_bytes(evidence["split"])).hexdigest()),
        ("gate0_relation_digest", evidence["relation_inventory"]["digest"]),
    ):
        if evidence["candidate_relation"][key] == "0" * 64:
            evidence["candidate_relation"][key] = expected
    reference["canonical_content_sha256"] = hashlib.sha256(cs.canonical_bytes(evidence)).hexdigest()
    reference["issuer_policy_ref"] = evidence["issuer_policy_ref"]
    authorization["corpus_separation_ref"] = reference
    attestation = cs.verify_synthetic(
        evidence, reference, authorization=authorization,
        checked_at="2026-01-01T00:00:00Z", trust_policy=p1._synthetic_trust_policy,
    )
    return attestation, authorization


def test_missing_opt_in_evidence_refuses_with_stable_error_before_any_work(tmp_path: Path) -> None:
    effects: list[str] = []
    binding = AdmissionBinding("synthetic:revision", "a" * 64, {})
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_ATTESTATION_REQUIRED"):
        context = check_synthetic_preflight(
            (), bindings=(binding,), operation="index-local", output_root=tmp_path / "out"
        )
        effects.append("source-read")
        require_synthetic_preflight(
            context, bindings=(binding,), operation="index-local", output_root=tmp_path / "out"
        )
    assert effects == []
    assert not (tmp_path / "out").exists()
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        check_synthetic_preflight(
            None, bindings=(binding,), operation="index-local", output_root=tmp_path / "out"
        )


def test_caller_constructed_context_cannot_bypass_checked_preflight(tmp_path: Path) -> None:
    binding = AdmissionBinding("synthetic:revision", "a" * 64, {})
    forged = SyntheticPreflightContext(
        operation="index-local", bindings=(), output_root=str(tmp_path / "out"),
        plan_digest=None, manifest_digest=None, attestation_digests=(),
    )
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        require_synthetic_preflight(
            forged, bindings=(binding,), operation="index-local", output_root=tmp_path / "out"
        )


def test_checked_attestation_is_bound_to_exact_operation_authorization_and_output(tmp_path: Path) -> None:
    attestation, authorization = _valid_synthetic_attestation()
    binding = AdmissionBinding("candidate-c", "d" * 64, authorization, "fixture://one")
    output = tmp_path / "out"
    context = check_synthetic_preflight(
        (attestation,), bindings=(binding,), operation="index-local", output_root=output,
        manifest_digest="b" * 64,
    )
    require_synthetic_preflight(
        context, bindings=(binding,), operation="index-local", output_root=output,
        manifest_digest="b" * 64,
    )
    assert context.evidence_state == "SYNTHETIC_ONLY"
    assert context.authenticity_status == "SYNTHETIC_TRUST_DOUBLE_ONLY"
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        require_synthetic_preflight(
            context, bindings=(binding,), operation="prepare-real", output_root=output,
            manifest_digest="b" * 64,
        )
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        require_synthetic_preflight(
            context, bindings=(binding,), operation="index-local", output_root=tmp_path / "other",
            manifest_digest="b" * 64,
        )
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        require_synthetic_preflight(
            context, bindings=(binding,), operation="index-local", output_root=output,
            manifest_digest="c" * 64,
        )


def test_preview_authorization_digest_is_part_of_the_ephemeral_binding(tmp_path: Path) -> None:
    attestation, authorization = _valid_synthetic_attestation()
    binding = AdmissionBinding("candidate-c", "d" * 64, authorization, "fixture://one")
    context = check_synthetic_preflight(
        (attestation,), bindings=(binding,), operation="local_preview.render_preview",
        output_root=tmp_path / "out", plan_digest="c" * 64,
        preview_authorization_digest="e" * 64,
    )
    require_synthetic_preflight(
        context, bindings=(binding,), operation="local_preview.render_preview",
        output_root=tmp_path / "out", plan_digest="c" * 64,
        preview_authorization_digest="e" * 64,
    )
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        require_synthetic_preflight(
            context, bindings=(binding,), operation="local_preview.render_preview",
            output_root=tmp_path / "out", plan_digest="c" * 64,
            preview_authorization_digest="f" * 64,
        )
