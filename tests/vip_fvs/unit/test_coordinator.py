from __future__ import annotations

import json
from pathlib import Path

import pytest

from vip_fvs.coordinator import (CoordinatorNotConfigured, FunctionalVerticalSliceServices,
                                 STAGE_ORDER, configure_services, run_vertical_slice)


def _stages():
    return {name: (lambda context, name=name: {"stage": name, "source": context["source"],
                                                **({"export_eligible": False} if name == "render" else {})})
            for name in STAGE_ORDER}


def test_complete_chain_persists_manifest_and_receipt(tmp_path):
    source = tmp_path / "source.bin"; source.write_bytes(b"fixture")
    configure_services(FunctionalVerticalSliceServices(_stages()))
    result = run_vertical_slice(source, "find action", tmp_path / "index", run_dir=tmp_path / "run")
    assert result["all_checks_passed"] is True
    assert result["export_eligible"] is False
    manifest = json.loads(Path(result["manifest"]).read_text())
    receipt = json.loads(Path(result["receipt"]).read_text())
    assert manifest["stages"] == list(STAGE_ORDER)
    assert receipt["manifest_digest"] == result["manifest_digest"]
    assert receipt["export_eligible"] is False


def test_missing_stage_fails_closed_and_records_refusal(tmp_path):
    source = tmp_path / "source.bin"; source.write_bytes(b"fixture")
    configure_services(FunctionalVerticalSliceServices({"inventory": _stages()["inventory"]}))
    result = run_vertical_slice(source, "q", tmp_path / "index", run_dir=tmp_path / "run")
    assert result["all_checks_passed"] is False
    assert any(item.startswith("STAGE_NOT_CONFIGURED:retrieval") for item in result["failures"])


def test_render_cannot_claim_export_eligibility(tmp_path):
    source = tmp_path / "source.bin"; source.write_bytes(b"fixture")
    stages = _stages(); stages["render"] = lambda context: {"export_eligible": True}
    configure_services(FunctionalVerticalSliceServices(stages))
    result = run_vertical_slice(source, "q", tmp_path / "index", run_dir=tmp_path / "run")
    assert result["all_checks_passed"] is False
    assert "export-ineligible" in result["failures"][0]


def test_unconfigured_and_invalid_invocation_fail_closed(tmp_path):
    import vip_fvs.coordinator as coordinator
    coordinator._services = None
    source = tmp_path / "source.bin"; source.write_bytes(b"fixture")
    with pytest.raises(CoordinatorNotConfigured):
        run_vertical_slice(source, "q", tmp_path / "index")
    with pytest.raises(ValueError, match="query"):
        run_vertical_slice(source, " ", tmp_path / "index")


def test_direct_run_rejects_forged_synthetic_preflight_before_source_read(tmp_path, monkeypatch):
    from vip_fvs.corpus_admission import CorpusAdmissionError

    source = tmp_path / "source.bin"
    source.write_bytes(b"controlled")
    monkeypatch.setattr(Path, "read_bytes", lambda _path: pytest.fail("source read before preflight"))
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        run_vertical_slice(source, "q", tmp_path / "index", fake_embedder=True,
                           synthetic_preflight=object(), admission_bindings=())


def test_direct_index_local_rejects_forged_synthetic_preflight_before_engine(tmp_path):
    from vip_fvs import coordinator
    from vip_fvs.corpus_admission import CorpusAdmissionError
    from vip_fvs.retrieval_adapter import fake_semantic_space
    from vip_fvs.local_semantic import checked_runtime

    source = tmp_path / "source.bin"
    source.write_bytes(b"controlled")
    runtime = checked_runtime(image_embedder=lambda paths: [], text_embedder=lambda texts: [],
                              semantic_space=fake_semantic_space(), fake=True,
                              runtime_identity="test-fake")

    class Engine:
        def build_generation_spec(self, _space):
            pytest.fail("engine reached before preflight")

    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_"):
        coordinator.index_local_source(source, tmp_path / "index", runtime=runtime,
            semantic_space=runtime.semantic_space, engine=Engine(), synthetic_preflight=object(),
            admission_bindings=())


def test_direct_run_rechecks_source_digest_after_preflight_before_output(tmp_path, monkeypatch):
    import sys
    unit_dir = str(Path(__file__).resolve().parent)
    sys.path.insert(0, unit_dir)
    try:
        from test_corpus_admission import _valid_synthetic_attestation
        attestation, authorization = _valid_synthetic_attestation()
    finally:
        sys.path.remove(unit_dir)
    from vip_fvs.corpus_admission import AdmissionBinding, CorpusAdmissionError, check_synthetic_preflight
    from vip_fvs import coordinator

    source = tmp_path / "source.bin"
    source.write_bytes(b"controlled bytes")
    run_dir = tmp_path / "run"
    binding = AdmissionBinding("candidate-c", "d" * 64, authorization, str(source))
    preflight = check_synthetic_preflight((attestation,), bindings=(binding,), operation="run",
                                          output_root=run_dir)
    monkeypatch.setattr(coordinator, "configure_services", lambda *_a, **_k: pytest.fail("service configured before digest check"))
    with pytest.raises(CorpusAdmissionError, match="CORPUS_SEPARATION_CANDIDATE_DIGEST_MISMATCH"):
        run_vertical_slice(source, "q", tmp_path / "index", fake_embedder=True, run_dir=run_dir,
                           synthetic_preflight=preflight, admission_bindings=(binding,))
    assert not run_dir.exists()
