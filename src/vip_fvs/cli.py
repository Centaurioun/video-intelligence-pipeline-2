"""Command-line entry point for the local functional vertical slice."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .human_decision import load_human_decision
from .corpus_admission import (AdmissionBinding, CorpusAdmissionError,
                               SyntheticPreflightContext, check_synthetic_preflight,
                               require_synthetic_preflight)
from .real_plan import build_fixture_plan_artifacts, build_real_edit_plan, save_real_plan
from .real_receipt import (build_decision_receipt, build_preparation_receipt,
                           load_real_receipt, save_real_receipt)
from .real_source_service import RealSourceRequest, prepare_real_source
from .real_source_probe import DEFAULT_PROBE_TIMEOUT_SECONDS
from .review_bundle import load_review_bundle


def _load_preview_authorization(path: Path, *, output_root: Path):
    """Load the exact, digest-bound preview authorization envelope."""
    from .local_preview import PreviewAuthorization
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("preview authorization must be an object")
    # Accept either the sealed record itself or a deliberately explicit wrapper.
    record = raw.get("authorization", raw)
    if not isinstance(record, dict):
        raise ValueError("preview authorization record is missing")
    record = dict(record)
    record["output_root"] = Path(record.get("output_root", output_root))
    return PreviewAuthorization(**record)


def _preview_real(
    args: Any, *, synthetic_preflight: SyntheticPreflightContext | None = None,
    admission_bindings: Sequence[AdmissionBinding] | None = None,
) -> dict[str, Any]:
    """Run the explicitly authorized local REAL preview chain."""
    from .local_preview import LocalPreviewAdapter
    from .real_plan import load_real_plan
    from .real_preview_qc import TechnicalQC
    from .real_preview_receipt import build_real_preview_receipt, save_real_preview_receipt
    from .real_preview_verifier import verify_preview

    plan_path = Path(args.plan).resolve()
    source = Path(args.source).resolve()
    output_root = Path(args.output_root).resolve()
    artifacts = load_real_plan(plan_path)
    # A non-REAL plan must never reach the REAL renderer/verifier/QC: that would
    # materialize MEASURED-looking REAL preview evidence for non-real editorial authority.
    if artifacts.plan.plan_scope != "REAL":
        raise ValueError("PLAN_SCOPE_MISMATCH: preview-real requires a REAL plan; got "
                         f"{artifacts.plan.plan_scope}")
    authorization = _load_preview_authorization(Path(args.authorization).resolve(), output_root=output_root)
    if authorization.output_root != output_root:
        raise ValueError("preview authorization output root mismatch")
    if synthetic_preflight is not None or admission_bindings is not None:
        if synthetic_preflight is None or admission_bindings is None or len(admission_bindings) != 1:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        binding = admission_bindings[0]
        try:
            preview_authorization_digest = authorization.compute_digest()
        except (AttributeError, TypeError, ValueError) as exc:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID") from exc
        if authorization.record_digest != preview_authorization_digest:
            raise CorpusAdmissionError("CORPUS_SEPARATION_ATTESTATION_DIGEST_MISMATCH")
        require_synthetic_preflight(
            synthetic_preflight, bindings=admission_bindings,
            operation="local_preview.render_preview", output_root=output_root,
            plan_digest=artifacts.plan.digest,
            preview_authorization_digest=preview_authorization_digest,
        )
        if (not isinstance(binding.authorization, Mapping)
                or binding.revision_id != authorization.source_revision_id
                or binding.source_sha256 != authorization.source_sha256
                or binding.locator != str(source)
                or binding.authorization.get("source_revision_id", binding.revision_id) != binding.revision_id
                or binding.authorization.get("source_sha256", binding.source_sha256) != binding.source_sha256
                or binding.authorization.get("output_root", str(output_root)) != str(output_root)):
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
    preview_kwargs = {
        "authorization": authorization, "source_path": source, "output_root": output_root,
        "ffprobe_executable": Path(args.ffprobe_executable).resolve(),
        "ffmpeg_executable": Path(args.ffmpeg_executable).resolve(),
        "producer_attempt_id": f"{args.attempt_id}:producer",
    }
    if synthetic_preflight is None:
        artifact = LocalPreviewAdapter().render_preview(artifacts, **preview_kwargs)
    else:
        artifact = LocalPreviewAdapter().render_preview(
            artifacts, **preview_kwargs, synthetic_opt_in=True,
            synthetic_preflight=synthetic_preflight,
            synthetic_binding=(admission_bindings[0]
                               if admission_bindings and len(admission_bindings) == 1 else None),
        )
    verification = verify_preview(
        artifact, source_path=source, attempt_id=args.attempt_id,
        plan_artifacts=artifacts, authorization=authorization,
        probe_runner=subprocess.run,
        source_probe_runner=subprocess.run,
        strict_artifact_digests=True,
    )
    verifier = verification.to_record()
    qc_report = TechnicalQC.evaluate(verification)
    qc = qc_report.to_record()
    verifier_path = output_root / "verifier.json"
    qc_path = output_root / "technical-qc.json"
    verifier_path.write_text(json.dumps(verifier, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    qc_path.write_text(json.dumps(qc, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    receipt = build_real_preview_receipt(plan_artifacts=artifacts, authorization=authorization,
                                         preview=artifact, verifier=verifier, technical_qc=qc,
                                         run_id=args.run_id, attempt_id=args.attempt_id,
                                         plan_ref=str(plan_path), verifier_ref=str(verifier_path),
                                         technical_qc_ref=str(qc_path))
    receipt_path = save_real_preview_receipt(receipt, Path(args.receipt_path).resolve()
                                             if args.receipt_path else output_root / "preview-receipt.json",
                                             authorized_output_root=output_root)
    status = "PASS" if receipt.record["status"] == "SUCCEEDED" else "FAIL"
    return {"scope": receipt.record["scope"], "status": status, "receipt_path": str(receipt_path),
            "receipt_digest": receipt.record_digest, "preview_path": str(artifact.output_path),
            "verifier_status": verification.status, "technical_qc_status": qc_report.status}


_FIXTURE_SEALED_ARTIFACTS = ("plan.json", "authorization.json", "refinement.json",
                             "verifier.json", "technical-qc.json", "preview-receipt.json")
_FIXTURE_REAL_MODE_FLAGS = ("pilot_authorization", "model_root", "model_identity",
                            "model_revision", "weights_sha256", "source_snapshot_root",
                            "max_source_bytes", "max_store_bytes", "device")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _write_fixture_json(path: Path, value: Any) -> None:
    """Publish one canonical JSON artifact without overwriting an existing one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = path.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise ValueError(f"OUTPUT_EXISTS: {path}") from exc
    with handle:
        handle.write(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False, allow_nan=False) + "\n")


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return {name: _json_ready(getattr(value, name)) for name in value.__dataclass_fields__}
    return value


def _fixture_provenance(source: Path, provenance: Path) -> None:
    """Require an explicit generated-synthetic provenance sidecar before any work."""
    try:
        raw = provenance.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError, TypeError) as exc:
        raise ValueError("FIXTURE_PROVENANCE_REQUIRED: generated-media provenance sidecar "
                         "is missing, unreadable or not JSON") from exc
    if not isinstance(payload, dict) or set(payload) != {"source_kind", "sha256", "generator"}:
        raise ValueError("FIXTURE_PROVENANCE_REQUIRED: provenance sidecar shape is invalid")
    kind = payload["source_kind"]
    recorded_sha = payload["sha256"]
    generator = payload["generator"]
    if (not isinstance(kind, str) or not isinstance(recorded_sha, str)
            or not isinstance(generator, str) or not generator.strip()):
        raise ValueError("FIXTURE_PROVENANCE_REQUIRED: provenance sidecar values are invalid")
    canonical = _canonical_json_bytes(payload)
    if raw not in (canonical, canonical + b"\n"):
        raise ValueError("FIXTURE_PROVENANCE_REQUIRED: provenance sidecar must be canonical JSON")
    if kind != "synthetic":
        raise ValueError("FIXTURE_PROVENANCE_MISMATCH: provenance source_kind must be synthetic")
    if recorded_sha != hashlib.sha256(source.read_bytes()).hexdigest():
        raise ValueError("FIXTURE_PROVENANCE_MISMATCH: provenance sha256 does not match the source bytes")


def _write_fixture_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = path.open("xb")
    except FileExistsError as exc:
        raise ValueError(f"OUTPUT_EXISTS: {path}") from exc
    with handle:
        handle.write(data)


def _fixture_source_probe(source: Path, ffprobe: Path) -> dict[str, Any]:
    """Measure the generated source frames/packets with the real ffprobe binary."""
    argv = [str(ffprobe), "-v", "error", "-of", "json", "-show_streams",
            "-show_format", "-show_frames", str(source)]
    completed = subprocess.run(argv, shell=False, capture_output=True, timeout=60.0)
    if completed.returncode != 0:
        raise ValueError("FIXTURE_SOURCE_PROBE_FAILED: ffprobe exited "
                         f"{completed.returncode}: {completed.stderr.decode('utf-8', 'replace')[:200]}")
    try:
        payload = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("FIXTURE_SOURCE_PROBE_FAILED: ffprobe output is not JSON") from exc
    if not isinstance(payload, dict) or not payload.get("frames"):
        raise ValueError("FIXTURE_SOURCE_PROBE_FAILED: ffprobe reported no measured frames")
    return payload


def _fixture_measured_pts(probe_json: Mapping[str, Any], stream_index: int) -> list[int]:
    pts: set[int] = set()
    for frame in probe_json.get("frames", []) or []:
        if not isinstance(frame, Mapping):
            continue
        try:
            if int(frame.get("stream_index", -1)) != stream_index:
                continue
        except (TypeError, ValueError):
            continue
        for key in ("best_effort_timestamp", "pts", "pkt_pts"):
            try:
                pts.add(int(frame.get(key)))
            except (TypeError, ValueError):
                continue
    return sorted(pts)


def _preview_fixture(args: Any) -> dict[str, Any]:
    """Run the generated-synthetic fixture preview chain end to end.

    Every artifact this command emits is non-production: the editorial decision is a
    fixture-scoped SYNTHETIC_HUMAN acceptance, the plan scope is SYNTHETIC_FIXTURE, and
    no human editorial authority, visual/audio observation or production render
    capability is claimed.
    """
    from gate3.authority import RECORD_KIND_REFINEMENT, evidence_digest as refinement_evidence_digest
    from gate3.pts import PtsTable
    from gate3.rational import TimeBase
    from gate3.refinement import refine

    from .editorial_plan import editorial_decision
    from .local_preview import LocalPreviewAdapter, PreviewAuthorization, tool_configuration_digest
    from .real_preview_qc import TechnicalQC
    from .real_preview_receipt import build_fixture_preview_receipt, save_fixture_preview_receipt
    from .real_preview_verifier import verify_preview
    from .real_source_probe import assert_source_unchanged, probe_real_source

    source = Path(args.source).resolve()
    output_root = Path(args.output_root).resolve()
    ffprobe = Path(args.ffprobe_executable).resolve()
    ffmpeg = Path(args.ffmpeg_executable).resolve()

    ambiguous = [name for name in _FIXTURE_REAL_MODE_FLAGS if getattr(args, name, None) is not None]
    if getattr(args, "fake_embedder", False):
        ambiguous.append("fake_embedder")
    if ambiguous:
        raise ValueError("FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS: " + ",".join(sorted(ambiguous)))
    if not source.is_file():
        raise ValueError("FIXTURE_SOURCE_REQUIRED: local generated source file is required")
    try:
        source.relative_to(output_root)
    except ValueError:
        pass
    else:
        raise ValueError("PATH_ESCAPE: fixture source must live outside the output root")
    for name in _FIXTURE_SEALED_ARTIFACTS:
        if (output_root / name).exists():
            raise ValueError(f"OUTPUT_EXISTS: fixture output root already contains {name}")
    _fixture_provenance(source, Path(args.provenance))

    source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    revision_id = f"fixture-source:{source_sha256[:16]}"
    binding = probe_real_source(source, executable=ffprobe, source_revision_id=revision_id,
                                policy_identity="local-fixture-preview", run_dir=output_root)
    probe_payload = _fixture_source_probe(source, ffprobe)
    probe_bytes = _canonical_json_bytes(probe_payload) + b"\n"
    probe_path = output_root / "source-probe.json"
    _write_fixture_bytes(probe_path, probe_bytes)
    probe_digest = hashlib.sha256(probe_bytes).hexdigest()
    pts = _fixture_measured_pts(probe_payload, binding.selected_stream_index)
    if len(pts) < 2:
        raise ValueError("FIXTURE_INSUFFICIENT_MEASURED_PTS: at least two measured source PTS are required")
    start_pts, end_pts = pts[0], pts[1]

    refinement_attempt_id = f"{args.attempt_id}:refinement"
    request_payload: dict[str, Any] = {
        "request_id": f"fixture-request:{args.run_id}",
        "candidate_assertion_ref": f"fixture-assertion:{source_sha256[:16]}",
        "source_revision_id": revision_id,
        "source_locator": str(source),
        "expected_source_sha256": source_sha256,
        "selected_stream_index": binding.selected_stream_index,
        "requested_start_pts": start_pts,
        "requested_end_pts": end_pts,
        "producer_attempt_id": refinement_attempt_id,
        "idempotency_key": f"fixture-idempotency:{args.run_id}",
        "expected_timebase": None,
    }
    request_identity = {
        "request_id": request_payload["request_id"],
        "candidate_assertion_ref": request_payload["candidate_assertion_ref"],
        "producer_attempt_id": refinement_attempt_id,
        "idempotency_key": request_payload["idempotency_key"],
        "request_digest": _canonical_sha256(request_payload),
        "request": request_payload,
    }
    refinement = refine(
        PtsTable(TimeBase(binding.timebase_num, binding.timebase_den), pts),
        (start_pts, end_pts),
        attempt_id=refinement_attempt_id,
        tool_identity={"name": "vip_fvs.preview_fixture", "version": "v1"},
        time_domain="source_pts",
        precision="source-pts",
        source_revision_id=revision_id,
        source_content_digest=source_sha256,
        stream_index=binding.selected_stream_index,
        container_path=str(source),
        request_identity=request_identity,
    )
    if refinement.get("blocked"):
        raise ValueError(f"FIXTURE_REFINEMENT_REFUSED: {refinement['blocked']}")

    evidence_path = (output_root / "refinement.json").resolve()
    refinement["source_pts_interval"] = {"start": start_pts, "end": end_pts,
                                         "time_domain": "source_pts",
                                         "endpoint_semantics": "half_open"}
    refinement["timebase"] = {"num": binding.timebase_num, "den": binding.timebase_den}
    refinement["selected_stream_index"] = binding.selected_stream_index
    refinement["evidence_artifact_ref"] = str(evidence_path)
    refinement["source_probe_artifact_ref"] = str(probe_path)
    refinement["source_probe_digest"] = probe_digest
    refinement["evidence_digest"] = refinement_evidence_digest(RECORD_KIND_REFINEMENT, refinement)
    _write_fixture_json(evidence_path, refinement)

    plan_id = f"fixture-{source_sha256[:16]}"
    decision = editorial_decision(
        decision_id=f"fixture-decision:{args.attempt_id}",
        principal_kind="SYNTHETIC_HUMAN",
        principal_ref=f"fixture:synthetic-human:{source_sha256[:16]}",
        refinement_id=refinement["refinement_id"],
        plan_revision=1,
        decision_class="ACCEPT",
        rationale="Generated synthetic fixture preview acceptance; no human editorial authority is claimed.",
        fixture_scope="SYNTHETIC_FIXTURE",
    )
    artifacts = build_fixture_plan_artifacts(plan_id=plan_id, plan_revision=1,
                                             decision=decision, refinement=refinement)
    plan_path = output_root / "plan.json"
    save_real_plan(artifacts, plan_path)

    probe_id = {"sha256": hashlib.sha256(ffprobe.read_bytes()).hexdigest()}
    ffmpeg_id = {"sha256": hashlib.sha256(ffmpeg.read_bytes()).hexdigest()}
    authorization = PreviewAuthorization(
        authorization_id=f"fixture-authorization:{args.run_id}",
        policy_identity="local-fixture-preview",
        scope="NON_PRODUCTION_PREVIEW",
        plan_digest=artifacts.plan_digest,
        source_revision_id=refinement["source_revision_id"],
        source_sha256=source_sha256,
        placement_digest=_canonical_sha256(artifacts.placement.to_record()),
        mapping_digest=artifacts.mapping_digest,
        output_root=output_root,
        ffprobe_tool_digest=probe_id["sha256"],
        ffmpeg_tool_digest=ffmpeg_id["sha256"],
        tool_config_digest=tool_configuration_digest(probe_id, ffmpeg_id),
        expires_at="2099-01-01T00:00:00Z",
    )
    authorization_path = output_root / "authorization.json"
    _write_fixture_json(authorization_path, {"authorization": _json_ready(authorization)})

    preview = LocalPreviewAdapter().render_preview(
        artifacts, authorization=authorization, source_path=source,
        output_root=output_root, ffprobe_executable=ffprobe, ffmpeg_executable=ffmpeg,
        producer_attempt_id=f"{args.attempt_id}:producer",
    )
    verification = verify_preview(
        preview, source_path=source, attempt_id=args.attempt_id,
        plan_artifacts=artifacts, authorization=authorization,
        probe_runner=subprocess.run, source_probe_runner=subprocess.run,
        strict_artifact_digests=True,
    )
    verifier = verification.to_record()
    qc_report = TechnicalQC.evaluate(verification, attempt_id=args.attempt_id)
    technical_qc = qc_report.to_record()
    verifier_path = output_root / "verifier.json"
    technical_qc_path = output_root / "technical-qc.json"
    _write_fixture_json(verifier_path, verifier)
    _write_fixture_json(technical_qc_path, technical_qc)
    receipt = build_fixture_preview_receipt(
        plan_artifacts=artifacts, authorization=authorization, preview=preview,
        verifier=verifier, technical_qc=technical_qc, run_id=args.run_id,
        attempt_id=args.attempt_id, plan_ref=str(plan_path),
        verifier_ref=str(verifier_path), technical_qc_ref=str(technical_qc_path),
    )
    receipt_path = save_fixture_preview_receipt(
        receipt, Path(args.receipt_path).resolve() if args.receipt_path
        else output_root / "preview-receipt.json", authorized_output_root=output_root)
    assert_source_unchanged(binding)
    status = "PASS" if verification.status == "PASS" and qc_report.status == "PASS" else "FAIL"
    return {"scope": receipt.record["scope"], "status": status,
            "plan_path": str(plan_path), "authorization_path": str(authorization_path),
            "refinement_path": str(evidence_path), "preview_path": str(preview.output_path),
            "verifier_path": str(verifier_path), "technical_qc_path": str(technical_qc_path),
            "receipt_path": str(receipt_path), "receipt_digest": receipt.record_digest,
            "verifier_status": verification.status,
            "technical_qc_status": qc_report.status,
            "plan_scope": artifacts.plan.plan_scope,
            "principal_kind": decision.principal_kind,
            "fixture_scope": decision.fixture_scope,
            "production_eligible": False, "export_eligible": False}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vip-fvs")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run one local/synthetic slice")
    run.add_argument("--source", required=True, help="local source path")
    run.add_argument("--query", required=True, help="natural-language query")
    run.add_argument("--index-root", required=True, help="local index root")
    run.add_argument("--fake-embedder", action="store_true", help="use deterministic test embeddings")
    run.add_argument("--scenario", default="cfr_4s_shape")
    run.add_argument("--run-dir", default=None)
    run.add_argument("--pilot-authorization", default=None,
                     help="exact owner authorization artifact (required for real mode)")
    run.add_argument("--model-root", default=None)
    run.add_argument("--model-identity", default=None)
    run.add_argument("--model-revision", default=None)
    run.add_argument("--weights-sha256", default=None)
    run.add_argument("--source-snapshot-root", default=None)
    run.add_argument("--max-source-bytes", type=int, default=None)
    run.add_argument("--max-store-bytes", type=int, default=None)
    run.add_argument("--device", default="cpu", choices=["cpu", "mps"])
    _add_synthetic_admission_arguments(run)
    index_local = subparsers.add_parser("index-local", help="index one explicitly local source")
    index_local.add_argument("--source", required=True, help="local source path")
    index_local.add_argument("--index-root", required=True, help="local semantic index root")
    index_local.add_argument("--fake-embedder", action="store_true", help="use deterministic test embeddings")
    index_local.add_argument("--model-profile-json", default=None,
                             help="closed profile identity for an explicitly fake synthetic run")
    index_local.add_argument("--pilot-authorization", default=None,
                             help="exact owner authorization artifact (required for real mode)")
    index_local.add_argument("--output-root", default=None,
                             help="authorization-bound local output root (required for real mode)")
    index_local.add_argument("--model-root", default=None)
    index_local.add_argument("--model-identity", default=None)
    index_local.add_argument("--model-revision", default=None)
    index_local.add_argument("--weights-sha256", default=None)
    index_local.add_argument("--source-snapshot-root", default=None)
    index_local.add_argument("--max-source-bytes", type=int, default=None)
    index_local.add_argument("--max-store-bytes", type=int, default=None)
    index_local.add_argument("--device", default="cpu", choices=["cpu", "mps"])
    _add_synthetic_admission_arguments(index_local)
    query_local = subparsers.add_parser("query-local", help="query an existing local semantic generation")
    query_local.add_argument("--query", default=None, help="natural-language query (required for text modality)")
    _add_query_modality_arguments(query_local)
    query_local.add_argument("--index-root", required=True, help="local semantic index root")
    query_local.add_argument("--top-k", type=_positive_int, default=5)
    query_local.add_argument("--fake-embedder", action="store_true", help="use deterministic test embeddings")
    query_local.add_argument("--model-profile-json", default=None,
                             help="closed profile identity for an explicitly fake synthetic query")
    query_local.add_argument("--model-root", default=None)
    query_local.add_argument("--model-identity", default=None)
    query_local.add_argument("--model-revision", default=None)
    query_local.add_argument("--weights-sha256", default=None)
    query_local.add_argument("--device", default="cpu", choices=["cpu", "mps"])
    query_multi = subparsers.add_parser("query-multi", help="query an existing multi-source generation")
    query_multi.add_argument("--manifest", required=True, help="persisted multi-source manifest JSON")
    query_multi.add_argument("--query", default=None, help="natural-language query (required for text modality)")
    _add_query_modality_arguments(query_multi)
    query_multi.add_argument("--index-root", required=True, help="existing local semantic index root")
    query_multi.add_argument("--top-k", type=_positive_int, default=5)
    query_multi.add_argument("--fake-embedder", action="store_true", help="use deterministic test embeddings")
    query_multi.add_argument("--model-profile-json", default=None,
                             help="closed profile identity for an explicitly fake synthetic query")
    query_multi.add_argument("--model-root", default=None)
    query_multi.add_argument("--model-identity", default=None)
    query_multi.add_argument("--model-revision", default=None)
    query_multi.add_argument("--weights-sha256", default=None)
    query_multi.add_argument("--device", default="cpu", choices=["cpu", "mps"])
    prepare = subparsers.add_parser("prepare-real", help="prepare one explicitly local REAL source")
    prepare.add_argument("--source", required=True)
    prepare.add_argument("--query", required=True)
    prepare.add_argument("--index-root", required=True)
    prepare.add_argument("--output-root", required=True)
    prepare.add_argument("--run-dir", required=True)
    prepare.add_argument("--source-revision-id", required=True)
    prepare.add_argument("--attempt-id", required=True)
    prepare.add_argument("--pilot-authorization", required=True)
    prepare.add_argument("--model-root", required=True)
    prepare.add_argument("--model-identity", required=True)
    prepare.add_argument("--model-revision", required=True)
    prepare.add_argument("--weights-sha256", required=True)
    prepare.add_argument("--selected-stream-index", type=int, default=None)
    prepare.add_argument("--probe-executable", required=True)
    prepare.add_argument(
        "--allow-unbounded-local-pilot",
        action="store_true",
        help=("disable only the FFprobe elapsed-time limit for this authorized local preparation; "
              "launch in an interactive foreground terminal without an enclosing timeout; "
              "cancel manually with Ctrl-C"),
    )
    prepare.add_argument("--source-snapshot-root", required=True)
    prepare.add_argument("--preverified-snapshot-id", default=None,
                         help="reuse an existing snapshot ID after verifying its manifest and bytes")
    prepare.add_argument("--max-source-bytes", type=int, required=True)
    prepare.add_argument("--max-store-bytes", type=int, required=True)
    prepare.add_argument("--device", default="cpu", choices=["cpu", "mps"])
    _add_synthetic_admission_arguments(prepare)
    resume = subparsers.add_parser("resume-real", help="resume a sealed REAL editorial decision")
    resume.add_argument("--bundle", required=True)
    resume.add_argument("--decision", required=True)
    resume.add_argument("--output-root", required=True)
    resume.add_argument("--run-id", required=True)
    resume.add_argument("--attempt-id", required=True)
    resume.add_argument("--plan-id", default=None)
    resume.add_argument("--plan-revision", type=int, default=1)
    preview = subparsers.add_parser("preview-real", help="materialize one authorized local REAL preview")
    preview.add_argument("--plan", required=True, help="sealed REAL plan JSON")
    preview.add_argument("--authorization", "--preview-authorization", required=True, help="exact preview authorization JSON")
    preview.add_argument("--source", required=True, help="local source path")
    preview.add_argument("--output-root", required=True, help="authorized preview output root")
    preview.add_argument("--ffprobe-executable", "--ffprobe", required=True)
    preview.add_argument("--ffmpeg-executable", "--ffmpeg", required=True)
    preview.add_argument("--run-id", required=True)
    preview.add_argument("--attempt-id", required=True)
    preview.add_argument("--receipt-path", default=None)
    _add_synthetic_admission_arguments(preview)
    fixture = subparsers.add_parser("preview-fixture", help="run one generated-synthetic fixture preview chain")
    fixture.add_argument("--source", required=True, help="local generated synthetic source path")
    fixture.add_argument("--provenance", required=True, help="generated-media provenance sidecar JSON")
    fixture.add_argument("--output-root", required=True, help="fixture preview output root")
    fixture.add_argument("--ffprobe-executable", "--ffprobe", required=True)
    fixture.add_argument("--ffmpeg-executable", "--ffmpeg", required=True)
    fixture.add_argument("--run-id", required=True)
    fixture.add_argument("--attempt-id", required=True)
    fixture.add_argument("--receipt-path", default=None)
    # Real-model/pilot inputs are declared only so this fixture command can refuse them.
    fixture.add_argument("--pilot-authorization", default=None)
    fixture.add_argument("--model-root", default=None)
    fixture.add_argument("--model-identity", default=None)
    fixture.add_argument("--model-revision", default=None)
    fixture.add_argument("--weights-sha256", default=None)
    fixture.add_argument("--source-snapshot-root", default=None)
    fixture.add_argument("--max-source-bytes", type=int, default=None)
    fixture.add_argument("--max-store-bytes", type=int, default=None)
    fixture.add_argument("--device", default=None)
    fixture.add_argument("--fake-embedder", action="store_true", default=False)
    query_batch_syn = subparsers.add_parser(
        "query-batch-synthetic",
        help="run an explicit fake-only single-arm multi-source batch query",
    )
    query_batch_syn.add_argument("--catalog", required=True, help="explicit lab query catalog JSON")
    query_batch_syn.add_argument("--manifest", required=True, help="persisted multi-source manifest JSON")
    query_batch_syn.add_argument("--index-root", required=True, help="existing local semantic index root")
    query_batch_syn.add_argument("--model-profile-json", default=None,
                                 help="closed synthetic profile JSON (required)")
    query_batch_syn.add_argument("--fake-embedder", action="store_true", default=False,
                                 help="explicit synthetic-only execution flag (required)")
    query_batch_syn.add_argument("--top-k", type=int, default=5)
    _add_query_modality_arguments(query_batch_syn)
    query_batch_syn.add_argument("--pilot-authorization", default=None)
    query_batch_syn.add_argument("--output-root", default=None)
    query_batch_syn.add_argument("--model-root", default=None)
    query_batch_syn.add_argument("--model-identity", default=None)
    query_batch_syn.add_argument("--model-revision", default=None)
    query_batch_syn.add_argument("--weights-sha256", default=None)
    query_batch_syn.add_argument("--device", default=None)
    query_three_arm_syn = subparsers.add_parser(
        "query-three-arm-synthetic",
        help="run an explicit fake-only three-arm multi-source batch query",
    )
    query_three_arm_syn.add_argument("--catalog", required=True, help="explicit lab query catalog JSON")
    query_three_arm_syn.add_argument("--arm-map", required=True, help="closed three-arm configuration map JSON")
    query_three_arm_syn.add_argument("--fake-embedder", action="store_true", default=False,
                                     help="explicit synthetic-only execution flag (required)")
    query_three_arm_syn.add_argument("--top-k", type=int, default=5)
    _add_query_modality_arguments(query_three_arm_syn)
    query_three_arm_syn.add_argument("--pilot-authorization", default=None)
    query_three_arm_syn.add_argument("--output-root", default=None)
    query_three_arm_syn.add_argument("--model-root", default=None)
    query_three_arm_syn.add_argument("--model-identity", default=None)
    query_three_arm_syn.add_argument("--model-revision", default=None)
    query_three_arm_syn.add_argument("--weights-sha256", default=None)
    query_three_arm_syn.add_argument("--device", default=None)
    query_three_arm_syn.add_argument("--model-profile-json", default=None)
    return parser


def _add_query_modality_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the closed query envelope inputs to read-only query commands."""
    parser.add_argument("--modality", choices=("text", "image-reference", "video-reference"),
                        default="text", help="query input modality")
    parser.add_argument("--reference-id", default=None, help="opaque query reference identifier")
    parser.add_argument("--provenance-ref", default=None, help="reference provenance record")
    parser.add_argument("--source-revision-ref", default=None, help="referenced source revision")
    parser.add_argument("--interval-start-seconds", type=float, default=None,
                        help="optional coarse reference interval start; not a source timestamp")
    parser.add_argument("--interval-end-seconds", type=float, default=None,
                        help="optional coarse reference interval end; not a source timestamp")


def _add_synthetic_admission_arguments(parser: argparse.ArgumentParser) -> None:
    """Expose opt-in P1 synthetic attestations and their source bindings."""
    parser.add_argument("--synthetic-attestation", action="append", default=None,
                        help="P1 synthetic attestation JSON (repeat once per candidate)")
    parser.add_argument("--synthetic-binding", action="append", default=None,
                        help="JSON AdmissionBinding record matching each attestation")


def _load_cli_synthetic_preflight(
    args: Any,
) -> tuple[SyntheticPreflightContext | None, tuple[AdmissionBinding, ...] | None]:
    attestation_paths = getattr(args, "synthetic_attestation", None)
    binding_paths = getattr(args, "synthetic_binding", None)
    if not attestation_paths and not binding_paths:
        return None, None
    if not attestation_paths or not binding_paths or len(attestation_paths) != len(binding_paths):
        raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
    try:
        attestations = tuple(json.loads(Path(path).read_text(encoding="utf-8"))
                             for path in attestation_paths)
        bindings = tuple(AdmissionBinding(**json.loads(Path(path).read_text(encoding="utf-8")))
                         for path in binding_paths)
    except (OSError, TypeError, ValueError) as exc:
        raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID") from exc
    if args.command == "run":
        output_root = (Path(args.run_dir) if args.run_dir is not None else
                       Path(args.index_root) / "runs" / str(args.scenario))
    elif args.command == "index-local":
        output_root = Path(args.output_root) if args.output_root else Path(args.index_root)
    else:
        output_root = Path(args.output_root)
    plan_digest = None
    operation = args.command
    if args.command == "preview-real":
        from .real_plan import load_real_plan
        artifacts = load_real_plan(Path(args.plan).resolve())
        authorization = _load_preview_authorization(Path(args.authorization).resolve(),
                                                    output_root=Path(args.output_root).resolve())
        if artifacts.plan.plan_scope != "REAL":
            raise CorpusAdmissionError("CORPUS_SEPARATION_REAL_ADMISSION_FORBIDDEN")
        plan_digest = artifacts.plan.digest
        operation = "local_preview.render_preview"
        if len(bindings) != 1:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        binding = bindings[0]
        if (not isinstance(binding.authorization, Mapping)
                or binding.revision_id != authorization.source_revision_id
                or binding.source_sha256 != authorization.source_sha256
                or binding.locator != str(Path(args.source).resolve())
                or authorization.output_root != Path(args.output_root).resolve()
                or binding.authorization.get("source_revision_id", binding.revision_id) != binding.revision_id
                or binding.authorization.get("source_sha256", binding.source_sha256) != binding.source_sha256
                or binding.authorization.get("output_root", str(authorization.output_root)) != str(authorization.output_root)):
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
    preview_authorization_digest = None
    if args.command == "preview-real":
        try:
            preview_authorization_digest = authorization.compute_digest()
        except (AttributeError, TypeError, ValueError) as exc:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID") from exc
        if authorization.record_digest != preview_authorization_digest:
            raise CorpusAdmissionError("CORPUS_SEPARATION_ATTESTATION_DIGEST_MISMATCH")
    context = check_synthetic_preflight(
        attestations, bindings=bindings, operation=operation,
        output_root=output_root, plan_digest=plan_digest,
        preview_authorization_digest=preview_authorization_digest,
    )
    return context, bindings


def _query_envelope(args: Any) -> Any:
    """Parse query arguments into a typed envelope before opening any runtime."""
    from .query_modality import (
        CoarseReferenceInterval,
        QueryEnvelope,
        QueryModality,
        ReferenceQuery,
    )

    modality_by_cli = {
        "text": QueryModality.TEXT,
        "image-reference": QueryModality.IMAGE_REFERENCE,
        "video-reference": QueryModality.VIDEO_REFERENCE,
    }
    modality = modality_by_cli[args.modality]
    if modality is QueryModality.TEXT:
        if any((args.reference_id, args.provenance_ref, args.source_revision_ref,
                args.interval_start_seconds is not None, args.interval_end_seconds is not None)):
            raise ValueError("TEXT_QUERY_CANNOT_INCLUDE_REFERENCE_FIELDS")
        envelope = QueryEnvelope.from_text(args.query or "")
    else:
        if args.query is not None:
            raise ValueError("REFERENCE_QUERY_CANNOT_INCLUDE_TEXT")
        interval = None
        start, end = args.interval_start_seconds, args.interval_end_seconds
        if (start is None) != (end is None):
            raise ValueError("COARSE_REFERENCE_INTERVAL_REQUIRES_BOTH_ENDPOINTS")
        if start is not None:
            interval = CoarseReferenceInterval(start_seconds=start, end_seconds=end)
        reference = ReferenceQuery(
            reference_id=args.reference_id,
            provenance_ref=args.provenance_ref,
            source_revision_ref=args.source_revision_ref,
            interval=interval,
        )
        envelope = QueryEnvelope.from_reference(modality, reference)
    if not envelope.executable:
        raise ValueError(f"QUERY_MODALITY_NOT_EXECUTABLE:{envelope.modality.value}")
    return envelope


def _positive_int(value: str) -> int:
    """Parse a bounded positive count used by read-only query requests."""
    parsed = int(value)
    if parsed < 1 or parsed > 1000:
        raise argparse.ArgumentTypeError("must be between 1 and 1000")
    return parsed


def _fake_runtime() -> Any:
    """Construct the explicitly selected deterministic synthetic runtime."""
    from .local_semantic import fake_runtime
    return fake_runtime()


def _fake_profile_runtime(profile_path: str) -> Any:
    """Load a closed profile descriptor and build its model-free fake seam."""
    from persistent_local_index.embedding import build_fake_profile_runtime
    from persistent_local_index.model_profile import ModelProfile

    try:
        payload = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("MODEL_PROFILE_JSON_UNREADABLE") from exc
    if not isinstance(payload, dict):
        raise ValueError("MODEL_PROFILE_JSON_NOT_OBJECT")
    assets = payload.get("processor_asset_digests")
    if not isinstance(assets, list):
        raise ValueError("MODEL_PROFILE_ASSETS_INVALID")
    try:
        profile = ModelProfile(
            **{**payload, "processor_asset_digests": tuple(tuple(item) for item in assets)}
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("MODEL_PROFILE_JSON_INVALID") from exc
    return build_fake_profile_runtime(profile)


def _product_runtime(args: Any, *, index_operation: bool) -> Any:
    """Resolve an explicit fake runtime or a fully specified local real one."""
    real_values = {
        "--model-root": args.model_root,
        "--model-identity": args.model_identity,
        "--model-revision": args.model_revision,
        "--weights-sha256": args.weights_sha256,
    }
    authorization = getattr(args, "pilot_authorization", None)
    output_root = getattr(args, "output_root", None)
    profile_path = getattr(args, "model_profile_json", None)
    if profile_path and not args.fake_embedder:
        raise ValueError("MODEL_PROFILE_JSON_REQUIRES_EXPLICIT_FAKE_MODE")
    if args.fake_embedder:
        if any(real_values.values()) or authorization or output_root:
            raise ValueError("FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS")
        runtime = _fake_profile_runtime(profile_path) if profile_path else _fake_runtime()
        if not runtime.fake:
            raise ValueError("EXPLICIT_FAKE_RUNTIME_REQUIRED")
        return runtime, None

    required = dict(real_values)
    owner_authorization = None
    if index_operation:
        required.update({
            "--pilot-authorization": authorization,
            "--output-root": output_root,
        })
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError("REAL_MODE_EXPLICIT_INPUTS_REQUIRED:" + ",".join(missing))

    model_contract = SimpleNamespace(
        model_root=Path(args.model_root).resolve(),
        model_revision=args.model_revision,
        weights_sha256=args.weights_sha256,
    )
    if index_operation:
        # Validate the source-use envelope before opening the model runtime.
        from .pilot_authorization import PilotAuthorizationError
        from .coordinator import (load_index_local_authorization,
                                  require_index_local_authorization)
        try:
            owner_authorization = load_index_local_authorization(Path(authorization))
            require_index_local_authorization(
                owner_authorization, source_path=Path(args.source),
                model_contract=model_contract, index_root=Path(args.index_root),
                output_root=Path(output_root),
            )
            snapshot_values = {
                "--source-snapshot-root": getattr(args, "source_snapshot_root", None),
                "--max-source-bytes": getattr(args, "max_source_bytes", None),
                "--max-store-bytes": getattr(args, "max_store_bytes", None),
            }
            missing_snapshot_values = [name for name, value in snapshot_values.items() if not value]
            if missing_snapshot_values:
                raise ValueError("REAL_MODE_EXPLICIT_INPUTS_REQUIRED:" + ",".join(missing_snapshot_values))
            from .source_snapshot import SourceSnapshotStore
            snapshot_store = SourceSnapshotStore(
                Path(args.source_snapshot_root),
                max_source_bytes=args.max_source_bytes,
                max_store_bytes=args.max_store_bytes,
            )
            # Establish the authorized bytes before any model/runtime access.
            # The coordinator receives this exact verified object and must not
            # recapture the mutable source locator after runtime construction.
            args._preverified_source_snapshot = snapshot_store.capture(
                Path(args.source).expanduser().absolute(),
                expected_sha256=owner_authorization.source_sha256,
                authorization_id=str(owner_authorization.authorization_id),
                source_revision_id=owner_authorization.source_revision_id,
            )
        except (OSError, ValueError, PilotAuthorizationError) as exc:
            raise ValueError(f"INDEX_LOCAL_AUTHORIZATION_INVALID:{exc}") from exc

    runtime = _real_runtime(args)
    if runtime.fake:
        raise ValueError("REAL_RUNTIME_MUST_NOT_BE_FAKE")
    space = runtime.semantic_space
    if (space.model_identity != args.model_identity
            or space.frozen_revision != args.model_revision
            or space.weights_sha256 != args.weights_sha256):
        raise ValueError("LOCAL_RUNTIME_IDENTITY_MISMATCH")
    return runtime, owner_authorization


def _real_runtime(args: Any) -> Any:
    """Open the already-authorized local runtime; never a fake fallback."""
    from persistent_local_index.embedding import embed_images, embed_texts, load_session
    from persistent_local_index.local_model import LocalModelSpec, open_local_model
    from persistent_local_index.model_space import (EMBEDDING_DIM, EMBEDDING_DTYPE,
        TEXT_PREPROCESSING_CONTRACT, SemanticSpace, digest_image_preprocessing_assets,
        digest_processor_assets)
    root = Path(args.model_root).resolve()
    processor_digest = digest_processor_assets(root)
    spec = LocalModelSpec(root, args.weights_sha256, processor_digest, args.model_revision, device=args.device)
    handle = open_local_model(spec, loader=lambda checked_root, checked_device: load_session(checked_root, args.weights_sha256, device=checked_device))
    space = SemanticSpace(args.model_identity, args.model_revision, args.weights_sha256,
                          processor_digest, digest_image_preprocessing_assets(root),
                          TEXT_PREPROCESSING_CONTRACT, EMBEDDING_DIM, EMBEDDING_DTYPE, "l2")
    from .local_semantic import checked_runtime
    return checked_runtime(image_embedder=lambda paths: embed_images(handle.runtime, paths),
                           text_embedder=lambda texts: embed_texts(handle.runtime, texts),
                           semantic_space=space, runtime_identity=args.model_identity)


def _prepare_real(
    args: Any, *, synthetic_preflight: SyntheticPreflightContext | None = None,
    admission_bindings: Sequence[AdmissionBinding] | None = None,
) -> dict[str, Any]:
    if synthetic_preflight is not None or admission_bindings is not None:
        if synthetic_preflight is None or admission_bindings is None:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        require_synthetic_preflight(
            synthetic_preflight, bindings=admission_bindings, operation="prepare-real",
            output_root=Path(args.output_root),
        )
        raise CorpusAdmissionError("CORPUS_SEPARATION_REAL_ADMISSION_FORBIDDEN")
    if getattr(args, "allow_unbounded_local_pilot", False) and not getattr(args, "preverified_snapshot_id", None):
        raise SystemExit("UNBOUNDED_LOCAL_PILOT_REQUIRES_PREVERIFIED_SNAPSHOT_ID")
    from .pilot_authorization import (PilotAuthorizationError, load_pilot_authorization,
                                      require_prepare_authorization)
    authorization_path = Path(args.pilot_authorization)
    try:
        owner_authorization = load_pilot_authorization(authorization_path)
    except (OSError, ValueError, PilotAuthorizationError) as exc:
        raise SystemExit(f"PREPARE_AUTHORIZATION_INVALID:{exc}") from exc
    try:
        require_prepare_authorization(owner_authorization, source_path=Path(args.source),
            source_revision_id=args.source_revision_id, query=args.query,
            model_root=Path(args.model_root), model_identity=args.model_identity,
            model_revision=args.model_revision, weights_sha256=args.weights_sha256,
            index_root=Path(args.index_root), output_root=Path(args.output_root),
            selected_stream_index=getattr(args, "selected_stream_index", None),
            verify_source_digest=False)
    except PilotAuthorizationError as exc:
        raise SystemExit(str(exc)) from exc
    from .source_snapshot import SourceSnapshotStore
    try:
        snapshot_store = SourceSnapshotStore(
            Path(args.source_snapshot_root), max_source_bytes=args.max_source_bytes,
            max_store_bytes=args.max_store_bytes,
        )
        if getattr(args, "preverified_snapshot_id", None):
            preverified_snapshot = snapshot_store.load_verified_snapshot(args.preverified_snapshot_id)
            if (preverified_snapshot.source_locator != str(Path(args.source).expanduser().absolute())
                    or preverified_snapshot.sha256 != owner_authorization.source_sha256
                    or preverified_snapshot.authorization_id != str(owner_authorization.authorization_id)
                    or preverified_snapshot.source_revision_id != owner_authorization.source_revision_id):
                raise ValueError("PREVERIFIED_SNAPSHOT_AUTHORIZATION_BINDING_MISMATCH")
        else:
            preverified_snapshot = snapshot_store.capture(
                Path(args.source).expanduser().absolute(), expected_sha256=owner_authorization.source_sha256,
                authorization_id=str(owner_authorization.authorization_id),
                source_revision_id=owner_authorization.source_revision_id,
            )
    except (OSError, TypeError, ValueError) as exc:
        raise SystemExit(f"PREPARE_SOURCE_SNAPSHOT_REFUSED:{exc}") from exc
    runtime = _real_runtime(args)
    semantic_space = runtime.semantic_space
    from persistent_local_index.model_space import semantic_space_id
    try:
        require_prepare_authorization(owner_authorization, source_path=Path(args.source),
            source_revision_id=args.source_revision_id, query=args.query,
            model_root=Path(args.model_root), model_identity=str(semantic_space.model_identity),
            model_revision=str(semantic_space.frozen_revision),
            weights_sha256=str(semantic_space.weights_sha256), index_root=Path(args.index_root),
            output_root=Path(args.output_root), selected_stream_index=getattr(args, "selected_stream_index", None),
            semantic_space_id=semantic_space_id(semantic_space), verify_source_digest=False)
    except PilotAuthorizationError as exc:
        raise SystemExit(f"PREPARE_RUNTIME_SEMANTIC_SPACE_INVALID:{exc}") from exc
    request = RealSourceRequest(source_path=Path(args.source).expanduser().absolute(), query=args.query,
        authorization=owner_authorization,
        runtime=runtime, index_root=Path(args.index_root), output_root=Path(args.output_root),
        run_dir=Path(args.run_dir), source_revision_id=owner_authorization.source_revision_id,
        model_root=Path(args.model_root), source_snapshot_root=Path(args.source_snapshot_root),
        max_source_bytes=args.max_source_bytes, max_store_bytes=args.max_store_bytes,
        preverified_snapshot=preverified_snapshot,
        probe_timeout_seconds=(None if getattr(args, "allow_unbounded_local_pilot", False)
                               else DEFAULT_PROBE_TIMEOUT_SECONDS),
        selected_stream_index=getattr(args, "selected_stream_index", None) if getattr(args, "selected_stream_index", None) is not None else owner_authorization.selected_stream_index,
        attempt_id=args.attempt_id, probe_executable=Path(args.probe_executable))
    result = prepare_real_source(request)
    receipt = build_preparation_receipt(result, run_id=args.attempt_id, attempt_id=args.attempt_id)
    receipt_path = save_real_receipt(receipt, Path(args.output_root) / "real-receipt.json")
    return {"mode": "real", "status": receipt.record["status"],
            "bundle_path": str(result.bundle_path), "receipt_path": str(receipt_path),
            "receipt_digest": receipt.record_digest}


def _resume_real(args: Any) -> dict[str, Any]:
    bundle_path, decision_path = Path(args.bundle), Path(args.decision)
    bundle = load_review_bundle(bundle_path)
    decision = load_human_decision(decision_path, bundle_path=bundle_path)
    root = Path(args.output_root); root.mkdir(parents=True, exist_ok=True)
    plan = None; plan_path = None
    if decision.payload["decision_class"] == "ACCEPT":
        plan_id = args.plan_id or f"plan:{args.attempt_id}"
        plan = build_real_edit_plan(bundle, decision, plan_id=plan_id, plan_revision=args.plan_revision)
        plan_path = save_real_plan(plan, root / "real-plan.json")
    receipt = build_decision_receipt(bundle=bundle, decision=decision, run_id=args.run_id,
                                     attempt_id=args.attempt_id, bundle_path=bundle_path,
                                     decision_path=decision_path, plan=plan, plan_path=plan_path)
    receipt_path = save_real_receipt(receipt, root / "real-receipt.json")
    return {"mode": "real", "status": receipt.record["status"],
            "receipt_path": str(receipt_path), "receipt_digest": receipt.record_digest,
            "plan_path": str(plan_path) if plan_path else None}


def main(argv: Sequence[str] | None = None) -> int:
    """Parse ``argv``, run the slice, and emit exactly one JSON summary."""

    args = _parser().parse_args(argv)
    try:
        synthetic_preflight, admission_bindings = _load_cli_synthetic_preflight(args)
        if args.command == "prepare-real":
            if synthetic_preflight is None:
                result = _prepare_real(args)
            else:
                result = _prepare_real(args, synthetic_preflight=synthetic_preflight,
                                       admission_bindings=admission_bindings)
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0
        if args.command == "resume-real":
            result = _resume_real(args)
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0
        if args.command == "preview-real":
            if synthetic_preflight is None:
                result = _preview_real(args)
            else:
                result = _preview_real(args, synthetic_preflight=synthetic_preflight,
                                       admission_bindings=admission_bindings)
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0 if result.get("status") == "PASS" else 1
        if args.command == "preview-fixture":
            result = _preview_fixture(args)
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0 if result.get("status") == "PASS" else 1
        if args.command in {"index-local", "query-local", "query-multi"}:
            # Parse and gate the complete query envelope before constructing a
            # model runtime or opening the index. Reference modalities are
            # intentionally declared only; they never fall back to text.
            query_envelope = _query_envelope(args) if args.command in {"query-local", "query-multi"} else None
            from . import coordinator
            from .semantic_index import PersistentLocalSemanticIndexEngine
            index_operation = args.command == "index-local"
            if index_operation and synthetic_preflight is not None and not args.fake_embedder:
                if (admission_bindings is None or len(admission_bindings) != 1
                        or admission_bindings[0].locator != str(Path(args.source).expanduser().absolute())):
                    raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
                require_synthetic_preflight(
                    synthetic_preflight, bindings=admission_bindings, operation="index-local",
                    output_root=Path(args.output_root) if args.output_root else Path(args.index_root),
                )
                raise CorpusAdmissionError("CORPUS_SEPARATION_REAL_ADMISSION_FORBIDDEN")
            runtime, owner_authorization = _product_runtime(args, index_operation=index_operation)
            engine = PersistentLocalSemanticIndexEngine()
            if index_operation:
                kwargs: dict[str, Any] = {
                    "runtime": runtime,
                    "semantic_space": runtime.semantic_space,
                    "engine": engine,
                }
                if owner_authorization is not None:
                    kwargs.update(
                        pilot_authorization=owner_authorization,
                        model_contract=SimpleNamespace(
                            model_root=Path(args.model_root).resolve(),
                            model_revision=args.model_revision,
                            weights_sha256=args.weights_sha256,
                        ),
                        output_root=Path(args.output_root),
                        source_snapshot_root=Path(args.source_snapshot_root),
                        max_source_bytes=args.max_source_bytes,
                        max_store_bytes=args.max_store_bytes,
                        preverified_snapshot=getattr(args, "_preverified_source_snapshot", None),
                    )
                if synthetic_preflight is None:
                    result = coordinator.index_local_source(Path(args.source), Path(args.index_root), **kwargs)
                else:
                    result = coordinator.index_local_source(
                        Path(args.source), Path(args.index_root), synthetic_preflight=synthetic_preflight,
                        admission_bindings=admission_bindings, **kwargs,
                    )
            elif args.command == "query-local":
                result = coordinator.query_local_index(
                    Path(args.index_root), query_envelope.text, runtime=runtime,
                    semantic_space=runtime.semantic_space, engine=engine,
                    top_k=args.top_k,
                )
            else:
                from dataclasses import asdict

                from .multi_source_retrieval import retrieve_multi_source
                from .source_adapter import load_multi_source_manifest

                manifest = load_multi_source_manifest(Path(args.manifest))
                result = asdict(retrieve_multi_source(
                    Path(args.index_root), manifest, query_envelope.text,
                    runtime=runtime, semantic_space=runtime.semantic_space,
                    engine=engine, top_k=args.top_k,
                ))
                result["operation"] = "query-multi"
            summary = dict(result)
            summary["runtime_mode"] = "fake" if runtime.fake else "real"
            print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
            return 0
        if args.command in {"query-batch-synthetic", "query-three-arm-synthetic"}:
            from .batch_report import (
                build_single_arm_batch_report,
                build_three_arm_batch_report,
                serialize_batch_report,
            )
            from .batch_retrieval import run_batch_retrieval
            from .query_batch import load_query_catalog, validate_lab_top_k
            from .query_modality import QueryModality
            from .semantic_index import PersistentLocalSemanticIndexEngine
            from .source_adapter import load_multi_source_manifest
            from .synthetic_profiles import load_synthetic_profile_bundle
            from .three_arm_batch import load_three_arm_map, run_three_arm_batch

            modality_by_cli = {
                "text": QueryModality.TEXT,
                "image-reference": QueryModality.IMAGE_REFERENCE,
                "video-reference": QueryModality.VIDEO_REFERENCE,
            }
            selected_modality = modality_by_cli[args.modality]
            if selected_modality is not QueryModality.TEXT:
                raise ValueError(f"QUERY_MODALITY_NOT_EXECUTABLE:{selected_modality.value}")
            if any((
                args.reference_id,
                args.provenance_ref,
                args.source_revision_ref,
                args.interval_start_seconds is not None,
                args.interval_end_seconds is not None,
            )):
                raise ValueError("TEXT_QUERY_CANNOT_INCLUDE_REFERENCE_FIELDS")

            real_inputs = (
                getattr(args, "pilot_authorization", None),
                getattr(args, "output_root", None),
                getattr(args, "model_root", None),
                getattr(args, "model_identity", None),
                getattr(args, "model_revision", None),
                getattr(args, "weights_sha256", None),
                getattr(args, "device", None),
            )
            if any(value is not None for value in real_inputs):
                raise ValueError("FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS")
            if not args.fake_embedder:
                raise ValueError(
                    "MODEL_PROFILE_JSON_REQUIRES_EXPLICIT_FAKE_MODE:SYNTHETIC_BATCH_REQUIRES_EXPLICIT_FAKE_MODE"
                )
            top_k = validate_lab_top_k(args.top_k)

            if args.command == "query-batch-synthetic":
                if not args.model_profile_json:
                    raise ValueError("MODEL_PROFILE_JSON_REQUIRED")
                catalog = load_query_catalog(Path(args.catalog))
                bundle = load_synthetic_profile_bundle(Path(args.model_profile_json))
                manifest = load_multi_source_manifest(Path(args.manifest))
                engine = PersistentLocalSemanticIndexEngine()
                single_result = run_batch_retrieval(
                    catalog,
                    manifest,
                    Path(args.index_root),
                    runtime=bundle.runtime,
                    semantic_space=bundle.semantic_space,
                    engine=engine,
                    top_k=top_k,
                    profile_id=bundle.profile.profile_id,
                )
                report = build_single_arm_batch_report(single_result)
            else:
                if getattr(args, "model_profile_json", None) is not None:
                    raise ValueError("THREE_ARM_PROFILE_MUST_COME_FROM_ARM_MAP")
                catalog = load_query_catalog(Path(args.catalog))
                arm_map = load_three_arm_map(Path(args.arm_map))
                three_arm_result = run_three_arm_batch(
                    catalog,
                    arm_map,
                    top_k=top_k,
                    engine_factory=lambda _arm_id: PersistentLocalSemanticIndexEngine(),
                )
                report = build_three_arm_batch_report(three_arm_result)

            print(serialize_batch_report(report))
            return 0
        if args.command != "run":  # pragma: no cover - argparse enforces this
            return 2
        from .coordinator import run_vertical_slice
        local_config = None
        authorization = args.pilot_authorization
        if args.fake_embedder:
            # An explicit fake run must not silently absorb real-mode inputs:
            # a caller that passes authorization/model/snapshot evidence is
            # asking for a real run, and a synthetic PASS is not that run.
            real_mode_inputs = {
                "--pilot-authorization": authorization,
                "--model-root": args.model_root,
                "--model-identity": args.model_identity,
                "--model-revision": args.model_revision,
                "--weights-sha256": args.weights_sha256,
                "--source-snapshot-root": args.source_snapshot_root,
                "--max-source-bytes": args.max_source_bytes,
                "--max-store-bytes": args.max_store_bytes,
            }
            if any(value is not None for value in real_mode_inputs.values()) or args.device != "cpu":
                raise ValueError("FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS")
        if not args.fake_embedder:
            required = {
                "--pilot-authorization": authorization,
                "--model-root": args.model_root,
                "--model-identity": args.model_identity,
                "--model-revision": args.model_revision,
                "--weights-sha256": args.weights_sha256,
                "--source-snapshot-root": args.source_snapshot_root,
                "--max-source-bytes": args.max_source_bytes,
                "--max-store-bytes": args.max_store_bytes,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ValueError("REAL_MODE_EXPLICIT_INPUTS_REQUIRED:" + ",".join(missing))
            # Keep model opening lazy: coordinator authorization is the first
            # real-mode gate.  The factory then crosses the validated local
            # model boundary and immediately revalidates after opening.
            def runtime_factory():
                from persistent_local_index.embedding import embed_images, embed_texts, load_session
                from persistent_local_index.local_model import LocalModelSpec, open_local_model
                from persistent_local_index.model_space import SemanticSpace, TEXT_PREPROCESSING_CONTRACT, EMBEDDING_DIM, EMBEDDING_DTYPE, digest_processor_assets, digest_image_preprocessing_assets
                root = Path(args.model_root).resolve()
                processor_digest = digest_processor_assets(root)
                spec = LocalModelSpec(root, args.weights_sha256, processor_digest, args.model_revision, device=args.device)
                handle = open_local_model(spec, loader=lambda checked_root, checked_device: load_session(checked_root, args.weights_sha256, device=checked_device))
                session = handle.runtime
                space = SemanticSpace(args.model_identity, args.model_revision, args.weights_sha256,
                                      processor_digest, digest_image_preprocessing_assets(root),
                                      TEXT_PREPROCESSING_CONTRACT, EMBEDDING_DIM, EMBEDDING_DTYPE, "l2")
                from .local_semantic import checked_runtime
                return checked_runtime(image_embedder=lambda paths: embed_images(session, paths),
                                       text_embedder=lambda texts: embed_texts(session, texts),
                                       semantic_space=space, runtime_identity=args.model_identity)
            model_contract = SimpleNamespace(model_root=Path(args.model_root).resolve(), model_revision=args.model_revision, weights_sha256=args.weights_sha256)
            local_config = SimpleNamespace(runtime_factory=runtime_factory, model_contract=model_contract)
        preflight_kwargs = ({"synthetic_preflight": synthetic_preflight,
                             "admission_bindings": admission_bindings}
                            if synthetic_preflight is not None else {})
        result: dict[str, Any] = run_vertical_slice(
            args.source,
            args.query,
            args.index_root,
            fake_embedder=args.fake_embedder,
            scenario=args.scenario,
            run_dir=args.run_dir,
            local_semantic_config=local_config,
            pilot_authorization=authorization,
            source_snapshot_root=args.source_snapshot_root,
            max_source_bytes=args.max_source_bytes,
            max_store_bytes=args.max_store_bytes,
            **preflight_kwargs,
        )
    except (OSError, TypeError, ValueError, RuntimeError) as exc:
        print(json.dumps({"all_checks_passed": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result.get("all_checks_passed") is True else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())


__all__ = ["main"]
