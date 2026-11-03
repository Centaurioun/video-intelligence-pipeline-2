"""Public REAL preview CLI boundary tests (synthetic/injected only)."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
import hashlib
import os
import stat
import pytest

from vip_fvs import cli
from vip_fvs.corpus_admission import (
    AdmissionBinding,
    CorpusAdmissionError,
    check_synthetic_preflight,
)
from vip_fvs.corpus_separation import authorization_scope_digest
from vip_fvs.local_preview import LocalPreviewAdapter, PreviewRefusal
from persistent_local_index.model_space import semantic_space_id


def _synthetic_preview_preflight(monkeypatch, tmp_path: Path, *, authorization=None):
    """Build sealed plumbing context without asserting a P1 trust decision."""
    import vip_fvs.corpus_admission as admission

    monkeypatch.setattr(admission.cs, "validate_attestation", lambda _value: None)
    p1_authorization = authorization or {"authorization_id": "synthetic-test-authorization"}
    binding = AdmissionBinding("synthetic-revision", "a" * 64, p1_authorization, "candidate.json")
    attestation = {
        "attestation_digest": "b" * 64,
        "authenticity_status": "SYNTHETIC_TRUST_DOUBLE_ONLY",
        "candidate_revision_id": binding.revision_id,
        "candidate_source_sha256": binding.source_sha256,
        "candidate_authorization_digest": authorization_scope_digest(p1_authorization),
        "byte_disjoint_status": "VERIFIED_DISJOINT_SYNTHETIC",
        "declared_relations_status": "VERIFIED_DISJOINT_SYNTHETIC",
    }
    plan_digest = "c" * 64
    preview_authorization_digest = "e" * 64
    output_root = tmp_path / "preview-output"
    context = check_synthetic_preflight(
        [attestation], bindings=[binding], operation="local_preview.render_preview",
        output_root=output_root, plan_digest=plan_digest,
        preview_authorization_digest=preview_authorization_digest,
    )
    return context, binding, plan_digest, output_root, preview_authorization_digest


def _synthetic_preview_request(adapter, *, context, binding, plan_digest, output_root,
                               preview_authorization_digest="e" * 64,
                               authorization=None):
    from types import SimpleNamespace

    artifacts = SimpleNamespace(plan=SimpleNamespace(digest=plan_digest))
    source_revision_id = "synthetic-revision" if binding is None else binding.revision_id
    source_sha256 = "a" * 64 if binding is None else binding.source_sha256
    preview_authorization = authorization or SimpleNamespace(
        source_revision_id=source_revision_id,
        source_sha256=source_sha256,
        record_digest=preview_authorization_digest,
        compute_digest=lambda: preview_authorization_digest,
    )
    return adapter.render_preview(
        artifacts, authorization=preview_authorization,
        source_path=output_root.parent / "must-not-read.mp4", output_root=output_root,
        ffprobe_executable=output_root.parent / "must-not-probe",
        ffmpeg_executable=output_root.parent / "must-not-render",
        synthetic_opt_in=True, synthetic_preflight=context, synthetic_binding=binding,
    )


def test_synthetic_preview_preflight_validates_then_refuses_before_any_effect(monkeypatch, tmp_path: Path):
    context, binding, plan_digest, output_root, preview_authorization_digest = _synthetic_preview_preflight(monkeypatch, tmp_path)
    calls = []
    adapter = LocalPreviewAdapter(runner=lambda *a, **k: calls.append((a, k)))

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_SYNTHETIC_PREFLIGHT_ONLY"):
        _synthetic_preview_request(adapter, context=context, binding=binding,
                                   plan_digest=plan_digest, output_root=output_root)

    assert calls == []
    assert not output_root.exists()


@pytest.mark.parametrize("missing", ["context", "binding"])
def test_synthetic_preview_opt_in_requires_both_ephemeral_inputs(monkeypatch, tmp_path: Path, missing):
    context, binding, plan_digest, output_root, preview_authorization_digest = _synthetic_preview_preflight(monkeypatch, tmp_path)
    if missing == "context":
        context = None
    else:
        binding = None
    adapter = LocalPreviewAdapter(runner=lambda *a, **k: pytest.fail("tool must not run"))

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION"):
        _synthetic_preview_request(adapter, context=context, binding=binding,
                                   plan_digest=plan_digest, output_root=output_root)

    assert not output_root.exists()


def test_synthetic_preview_preflight_rejects_mismatched_preview_authorization_before_effect(monkeypatch, tmp_path: Path):
    context, binding, plan_digest, output_root, preview_authorization_digest = _synthetic_preview_preflight(monkeypatch, tmp_path)
    from types import SimpleNamespace

    wrong_authorization = SimpleNamespace(source_revision_id="other-revision", source_sha256="d" * 64,
                                          record_digest=preview_authorization_digest,
                                          compute_digest=lambda: preview_authorization_digest)
    adapter = LocalPreviewAdapter(runner=lambda *a, **k: pytest.fail("tool must not run"))

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION"):
        _synthetic_preview_request(adapter, context=context, binding=binding,
                                   plan_digest=plan_digest, output_root=output_root,
                                   authorization=wrong_authorization)

    assert not output_root.exists()


def test_synthetic_preview_preflight_rejects_changed_preview_authorization_digest(monkeypatch, tmp_path: Path):
    context, binding, plan_digest, output_root, _ = _synthetic_preview_preflight(monkeypatch, tmp_path)
    from types import SimpleNamespace

    changed_authorization = SimpleNamespace(
        source_revision_id=binding.revision_id,
        source_sha256=binding.source_sha256,
        record_digest="f" * 64,
        compute_digest=lambda: "f" * 64,
    )
    adapter = LocalPreviewAdapter(runner=lambda *a, **k: pytest.fail("tool must not run"))

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION"):
        _synthetic_preview_request(adapter, context=context, binding=binding,
                                   plan_digest=plan_digest, output_root=output_root,
                                   authorization=changed_authorization)

    assert not output_root.exists()


@pytest.mark.parametrize("mismatch", ["plan", "output", "binding", "forged-context"])
def test_synthetic_preview_preflight_rejects_stale_or_forged_binding_before_effect(
        monkeypatch, tmp_path: Path, mismatch):
    context, binding, plan_digest, output_root, preview_authorization_digest = _synthetic_preview_preflight(monkeypatch, tmp_path)
    if mismatch == "plan":
        plan_digest = "e" * 64
    elif mismatch == "output":
        output_root = tmp_path / "different-output"
    elif mismatch == "binding":
        binding = AdmissionBinding("other-revision", "f" * 64, binding.authorization, "candidate.json")
    else:
        context = replace(context, _seal=None)
    adapter = LocalPreviewAdapter(runner=lambda *a, **k: pytest.fail("tool must not run"))

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION"):
        _synthetic_preview_request(adapter, context=context, binding=binding,
                                   plan_digest=plan_digest, output_root=output_root)

    assert not (tmp_path / "preview-output").exists()
    assert not (tmp_path / "different-output").exists()


def test_preflight_data_cannot_be_silently_ignored_without_opt_in(monkeypatch, tmp_path: Path):
    context, binding, plan_digest, output_root, preview_authorization_digest = _synthetic_preview_preflight(monkeypatch, tmp_path)
    adapter = LocalPreviewAdapter(runner=lambda *a, **k: pytest.fail("tool must not run"))

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION"):
        adapter.render_preview(
            None, authorization=None, source_path=tmp_path / "source.mp4", output_root=output_root,
            ffprobe_executable=tmp_path / "ffprobe", ffmpeg_executable=tmp_path / "ffmpeg",
            synthetic_preflight=context, synthetic_binding=binding,
        )

    assert not output_root.exists()


def test_legacy_preview_adapter_opt_out_keeps_missing_authorization_refusal(tmp_path: Path):
    output_root = tmp_path / "legacy-output"
    adapter = LocalPreviewAdapter(runner=lambda *a, **k: pytest.fail("tool must not run"))

    with pytest.raises(PreviewRefusal, match="MISSING_AUTHORIZATION"):
        adapter.render_preview(
            None, authorization=None, source_path=tmp_path / "source.mp4", output_root=output_root,
            ffprobe_executable=tmp_path / "ffprobe", ffmpeg_executable=tmp_path / "ffmpeg",
        )

    assert not output_root.exists()


def test_preview_real_dispatches_to_sealed_preview_chain(monkeypatch, tmp_path: Path, capsys):
    seen = {}

    def fake_preview(args):
        seen.update(vars(args))
        return {"scope": "LOCAL_REAL_NON_PRODUCTION_PREVIEW", "status": "PASS",
                "receipt_path": str(tmp_path / "preview-receipt.json")}

    monkeypatch.setattr(cli, "_preview_real", fake_preview)
    assert cli.main([
        "preview-real", "--plan", "plan.json", "--authorization", "auth.json",
        "--source", "source.mp4", "--output-root", str(tmp_path),
        "--ffprobe-executable", "ffprobe", "--ffmpeg-executable", "ffmpeg",
        "--run-id", "run-1", "--attempt-id", "attempt-1",
    ]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["scope"] == "LOCAL_REAL_NON_PRODUCTION_PREVIEW"
    assert seen["plan"] == "plan.json" and seen["authorization"] == "auth.json"


def test_preview_real_is_not_synthetic_run(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(cli, "_preview_real", lambda args: {"status": "PASS"})
    monkeypatch.setattr("vip_fvs.coordinator.run_vertical_slice",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("synthetic path")))
    assert cli.main([
        "preview-real", "--plan", "p", "--authorization", "a", "--source", "s",
        "--output-root", str(tmp_path), "--ffprobe-executable", "probe",
        "--ffmpeg-executable", "ffmpeg", "--run-id", "r", "--attempt-id", "a1",
    ]) == 0


def test_preview_real_implementation_uses_distinct_receipt_without_synthetic_opt_in(
        monkeypatch, tmp_path: Path):
    from types import SimpleNamespace
    import vip_fvs.local_preview as local_preview
    import vip_fvs.real_plan as real_plan
    import vip_fvs.real_preview_qc as real_preview_qc
    import vip_fvs.real_preview_receipt as real_preview_receipt
    import vip_fvs.real_preview_verifier as real_preview_verifier

    output_root = tmp_path / "real-output"
    output_root.mkdir()
    artifacts = SimpleNamespace(plan=SimpleNamespace(plan_scope="REAL", digest="plan-digest"))
    authorization = SimpleNamespace(output_root=output_root)
    preview_artifact = SimpleNamespace(output_path=tmp_path / "preview.mp4")
    verification = SimpleNamespace(status="PASS", to_record=lambda: {"status": "PASS"})
    qc_report = SimpleNamespace(status="PASS", to_record=lambda: {"status": "PASS"})
    receipt = SimpleNamespace(
        record={"scope": "LOCAL_REAL_NON_PRODUCTION_PREVIEW", "status": "SUCCEEDED"},
        record_digest="d" * 64,
    )
    calls = {"render": [], "receipt": [], "saved": []}

    class PreviewAdapterDouble:
        def render_preview(self, rendered_artifacts, **kwargs):
            calls["render"].append((rendered_artifacts, kwargs))
            return preview_artifact

    class TechnicalQCDouble:
        @staticmethod
        def evaluate(result):
            assert result is verification
            return qc_report

    monkeypatch.setattr(real_plan, "load_real_plan", lambda _path: artifacts)
    monkeypatch.setattr(cli, "_load_preview_authorization", lambda _path, *, output_root: authorization)
    monkeypatch.setattr(local_preview, "LocalPreviewAdapter", PreviewAdapterDouble)
    monkeypatch.setattr(real_preview_verifier, "verify_preview", lambda *_a, **_k: verification)
    monkeypatch.setattr(real_preview_qc, "TechnicalQC", TechnicalQCDouble)
    monkeypatch.setattr(real_preview_receipt, "build_real_preview_receipt",
                        lambda **_kwargs: calls["receipt"].append(_kwargs) or receipt)
    monkeypatch.setattr(real_preview_receipt, "save_real_preview_receipt",
                        lambda saved, path, *, authorized_output_root:
                        calls["saved"].append((saved, path, authorized_output_root)) or path)

    args = SimpleNamespace(
        plan=str(tmp_path / "plan.json"), source=str(tmp_path / "source.mp4"),
        output_root=str(output_root), authorization=str(tmp_path / "authorization.json"),
        ffprobe_executable="ffprobe", ffmpeg_executable="ffmpeg", attempt_id="attempt-1",
        run_id="run-1", receipt_path=None,
    )
    result = cli._preview_real(args)

    assert result["scope"] == "LOCAL_REAL_NON_PRODUCTION_PREVIEW"
    assert result["status"] == "PASS"
    assert result["receipt_path"] == str(output_root / "preview-receipt.json")
    assert len(calls["receipt"]) == 1 and calls["saved"][0][0] is receipt
    assert calls["saved"][0][2] == output_root
    assert len(calls["render"]) == 1
    render_kwargs = calls["render"][0][1]
    assert not {"synthetic_opt_in", "synthetic_preflight", "synthetic_binding"} & render_kwargs.keys()


def test_preview_real_rejects_missing_or_mismatched_synthetic_bindings_before_render(
        monkeypatch, tmp_path: Path):
    from types import SimpleNamespace
    import vip_fvs.corpus_admission as admission
    import vip_fvs.local_preview as local_preview
    import vip_fvs.real_plan as real_plan

    output_root = tmp_path / "preview-output"
    output_root.mkdir()
    source = tmp_path / "source.mp4"
    artifacts = SimpleNamespace(plan=SimpleNamespace(plan_scope="REAL", digest="c" * 64))
    authorization_record = {
        "authorization_id": "synthetic-test-authorization",
        "source_revision_id": "revision-1",
        "source_sha256": "a" * 64,
        "output_root": str(output_root),
    }
    authorization_digest = "e" * 64
    authorization = SimpleNamespace(
        output_root=output_root, source_revision_id="revision-1", source_sha256="a" * 64,
        record_digest=authorization_digest, compute_digest=lambda: authorization_digest,
    )
    binding = AdmissionBinding("revision-1", "a" * 64, authorization_record, str(source.resolve()))
    monkeypatch.setattr(admission.cs, "validate_attestation", lambda _attestation: None)
    attestation = {
        "attestation_digest": "b" * 64,
        "authenticity_status": "SYNTHETIC_TRUST_DOUBLE_ONLY",
        "candidate_revision_id": binding.revision_id,
        "candidate_source_sha256": binding.source_sha256,
        "candidate_authorization_digest": authorization_scope_digest(authorization_record),
        "byte_disjoint_status": "VERIFIED_DISJOINT_SYNTHETIC",
        "declared_relations_status": "VERIFIED_DISJOINT_SYNTHETIC",
    }
    context = check_synthetic_preflight(
        [attestation], bindings=[binding], operation="local_preview.render_preview",
        output_root=output_root, plan_digest=artifacts.plan.digest,
        preview_authorization_digest=authorization_digest,
    )
    calls = []

    class PreviewAdapterDouble(local_preview.LocalPreviewAdapter):
        def __init__(self):
            super().__init__(runner=lambda *_args, **_kwargs:
                             pytest.fail("preview tools must not run for synthetic preflight"))

    monkeypatch.setattr(real_plan, "load_real_plan", lambda _path: artifacts)
    monkeypatch.setattr(cli, "_load_preview_authorization", lambda _path, *, output_root: authorization)
    monkeypatch.setattr(local_preview, "LocalPreviewAdapter", PreviewAdapterDouble)
    args = SimpleNamespace(
        plan=str(tmp_path / "plan.json"), source=str(source), output_root=str(output_root),
        authorization=str(tmp_path / "authorization.json"), ffprobe_executable="ffprobe",
        ffmpeg_executable="ffmpeg", attempt_id="attempt-1", run_id="run-1", receipt_path=None,
    )

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_DECLARATION_INVALID"):
        cli._preview_real(args, synthetic_preflight=context, admission_bindings=None)
    mismatched = AdmissionBinding("other-revision", "f" * 64, authorization_record, str(source.resolve()))
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_DECLARATION_INVALID"):
        cli._preview_real(args, synthetic_preflight=context, admission_bindings=[mismatched])
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_SYNTHETIC_PREFLIGHT_ONLY"):
        cli._preview_real(args, synthetic_preflight=context, admission_bindings=[binding])
    assert calls == []
    assert list(output_root.iterdir()) == []


def test_public_preview_real_executes_full_generated_fixture_chain(monkeypatch, tmp_path: Path, capsys):
    return test_generated_prepare_to_preview_chain_has_no_authority_monkeypatch(monkeypatch, tmp_path, capsys)


def test_generated_prepare_to_preview_chain_has_no_authority_monkeypatch(monkeypatch, tmp_path: Path, capsys):
    """Exercise the approved prepare -> ACCEPT -> REAL plan -> preview chain."""
    import hashlib
    from types import SimpleNamespace
    import numpy as np
    from gate3.fixturegen import build_mp4
    from vip_fvs.local_semantic import checked_runtime
    from vip_fvs.retrieval_adapter import fake_semantic_space
    from vip_fvs.real_source_service import RealSourceRequest, prepare_real_source
    from vip_fvs.human_decision import create_human_decision, save_human_decision
    from vip_fvs.local_preview import PreviewAuthorization, tool_configuration_digest
    from vip_fvs.real_plan import build_real_edit_plan, save_real_plan
    from vip_fvs.review_bundle import save_review_bundle

    source = tmp_path / "generated-valid.mp4"
    source.write_bytes(build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12)))
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    run_dir, index_root, output_root = tmp_path / "run", tmp_path / "index", tmp_path / "out"
    runtime = checked_runtime(
        image_embedder=lambda paths: np.ones((len(paths), 768), dtype=np.float32),
        text_embedder=lambda texts: np.ones((len(texts), 768), dtype=np.float32),
        semantic_space=fake_semantic_space(), fake=False, runtime_identity="generated-chain-runtime",
    )
    probe_payload = {"streams": [{"index": 0, "codec_type": "video", "time_base": "1/25"}],
                     "frames": [{"stream_index": 0, "best_effort_timestamp": str(v)} for v in (0, 13, 25, 38)]}
    def probe_runner(argv, **kwargs):
        return SimpleNamespace(returncode=0, stdout=json.dumps(probe_payload).encode(), stderr=b"")
    monkeypatch.setattr(
        "vip_fvs.real_source_service.retrieve_local_semantic",
        lambda measured, *a, **k: SimpleNamespace(space_id=semantic_space_id(runtime.semantic_space), generation_id="generated-generation", hits=(SimpleNamespace(source_sha256=source_sha, source_path=str(measured.source_path), rank=1, score=.9, pts=0, timebase_num=1, timebase_den=25),)),
    )
    model_root = tmp_path / "model"
    auth_body = {
        "source_path": str(source.resolve()), "source_sha256": source_sha,
        "purpose": "generated-preview-chain-test-only", "model_root": str(model_root.resolve()),
        "model_revision": runtime.semantic_space.frozen_revision,
        "weights_sha256": runtime.semantic_space.weights_sha256,
        "runtime_root": str((tmp_path / "runtime").resolve()),
        "index_root": str(index_root.resolve()), "output_root": str(output_root.resolve()),
        "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
        "authorization_id": "prepare-auth-v3", "source_revision_id": "generated-rev",
        "query_digest": hashlib.sha256(json.dumps("target", sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "model_identity": runtime.semantic_space.model_identity,
        "semantic_space_id": semantic_space_id(runtime.semantic_space),
        "index_digest": hashlib.sha256(json.dumps(str(index_root.resolve()), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "local_only": True, "expires_at": "2099-01-01T00:00:00+00:00", "revoked": False,
        "selected_stream_index": 0, "policy_digest": "1" * 64, "scope_digest": "2" * 64,
    }
    auth_body["record_digest"] = hashlib.sha256(
        json.dumps(auth_body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    auth = auth_body
    result = prepare_real_source(RealSourceRequest(
        source_path=source, query="target", authorization=auth, runtime=runtime,
        index_root=index_root, output_root=output_root, run_dir=run_dir,
        source_revision_id="generated-rev", attempt_id="generated-attempt",
        selected_stream_index=0, probe_runner=probe_runner, model_root=model_root,
        source_snapshot_root=tmp_path / "snapshot-store",
        max_source_bytes=1_000_000, max_store_bytes=2_000_000,
    ))
    bundle_path = output_root / "review-bundle.json"
    assert bundle_path == result.bundle_path
    decision = create_human_decision(bundle=result.bundle, decision_id="generated-decision",
                                     principal_kind="human", principal_ref="human:test",
                                     decision_class="ACCEPT", rationale="Measured generated fixture.", target_plan_revision=1)
    decision_path = tmp_path / "decision.json"
    save_human_decision(decision, decision_path)
    artifacts = build_real_edit_plan(result.bundle, decision, plan_id="generated-plan", plan_revision=1)
    plan_path = tmp_path / "plan.json"
    save_real_plan(artifacts, plan_path)

    ffprobe = tmp_path / "ffprobe.py"
    ffprobe.write_text("#!/usr/bin/env python3\nimport json\nprint(json.dumps({'streams':[{'index':0,'codec_type':'video','time_base':'1/25','duration_ts':13}], 'format':{}}))\n")
    ffmpeg = tmp_path / "ffmpeg.py"
    ffmpeg.write_text("#!/usr/bin/env python3\nfrom pathlib import Path\nimport sys\nPath(sys.argv[-1]).write_bytes(b'generated-preview')\n")
    ffprobe.chmod(ffprobe.stat().st_mode | stat.S_IXUSR); ffmpeg.chmod(ffmpeg.stat().st_mode | stat.S_IXUSR)
    probe_id = {"sha256": hashlib.sha256(ffprobe.read_bytes()).hexdigest()}
    ffmpeg_id = {"sha256": hashlib.sha256(ffmpeg.read_bytes()).hexdigest()}
    preview_auth = PreviewAuthorization(
        authorization_id="preview-generated", policy_identity="preview-policy", scope="NON_PRODUCTION_PREVIEW",
        plan_digest=artifacts.plan_digest, source_revision_id="generated-rev", source_sha256=source_sha,
        placement_digest=artifacts.placement_digest, mapping_digest=artifacts.mapping_digest,
        output_root=output_root, ffprobe_tool_digest=probe_id["sha256"], ffmpeg_tool_digest=ffmpeg_id["sha256"],
        tool_config_digest=tool_configuration_digest(probe_id, ffmpeg_id), review_bundle_record_digest=result.bundle.record_digest,
        review_bundle_dependency_digest=result.bundle.dependency_digest, human_decision_digest=decision.record_digest,
        review_bundle_ref=str(bundle_path), decision_ref=str(decision_path),
    )
    auth_path = tmp_path / "preview-auth.json"
    auth_path.write_text(json.dumps({**preview_auth.__dict__, "output_root": str(output_root)}, default=str,
                                    sort_keys=True, separators=(",", ":")) + "\n")
    assert cli.main(["preview-real", "--plan", str(plan_path), "--preview-authorization", str(auth_path),
                     "--source", str(source), "--output-root", str(output_root),
                     "--ffprobe-executable", str(ffprobe), "--ffmpeg-executable", str(ffmpeg),
                     "--run-id", "generated-run", "--attempt-id", "generated-preview-attempt"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "PASS"
