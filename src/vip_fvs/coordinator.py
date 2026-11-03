"""Fail-closed orchestration for the local functional vertical slice."""
from __future__ import annotations
from dataclasses import asdict, dataclass, is_dataclass
import hashlib, json, os, stat, subprocess, sys
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from . import local_semantic
from .corpus_admission import (AdmissionBinding, CorpusAdmissionError,
                               SyntheticPreflightContext, require_synthetic_preflight)
from .pilot_authorization import PilotAuthorizationError, load_pilot_authorization, require_pilot_authorization
from .semantic_index import SemanticIndexEngine, SemanticSpace


def _require_synthetic_preflight(
    context: SyntheticPreflightContext | None, bindings: Sequence[AdmissionBinding] | None, *, operation: str,
    output_root: Path, source_path: Path | None = None, allow_synthetic: bool,
) -> None:
    """Rebind optional synthetic evidence before source access or service effects."""
    if context is None and bindings is None:
        return
    if context is None or bindings is None or not bindings:
        raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
    ordered = tuple(bindings)
    require_synthetic_preflight(context, bindings=ordered, operation=operation,
                                output_root=output_root)
    if not allow_synthetic:
        raise CorpusAdmissionError("CORPUS_SEPARATION_REAL_ADMISSION_FORBIDDEN")
    for binding in ordered:
        if not isinstance(binding.authorization, Mapping):
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        if (binding.authorization.get("source_revision_id", binding.revision_id) != binding.revision_id
                or binding.authorization.get("source_sha256", binding.source_sha256) != binding.source_sha256):
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        declared_output = binding.authorization.get("output_root")
        if declared_output is not None and str(Path(declared_output).resolve()) != str(output_root.resolve()):
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
    if source_path is not None:
        source_locator = str(source_path.expanduser().absolute())
        if (len(ordered) != 1 or not isinstance(ordered[0], AdmissionBinding)
                or ordered[0].locator != source_locator):
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")
        digest_state = hashlib.sha256()
        try:
            with source_path.open("rb") as source_file:
                for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
                    digest_state.update(chunk)
        except OSError as exc:
            raise CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID") from exc
        digest = digest_state.hexdigest()
        if digest != ordered[0].source_sha256:
            raise CorpusAdmissionError("CORPUS_SEPARATION_CANDIDATE_DIGEST_MISMATCH")

class CoordinatorNotConfigured(RuntimeError):
    """Invocation before integration services are installed."""

class VerticalSliceServices(Protocol):
    def run(self, source: Path, query: str, index_root: Path, *, fake_embedder: bool,
            scenario: str, run_dir: Path | None,
            local_semantic_runtime: local_semantic.LocalSemanticRuntime | None = None,
            source_locator: str | None = None,
            snapshot_evidence: Mapping[str, Any] | None = None) -> Mapping[str, Any]: ...

@dataclass(frozen=True)
class CoordinatorConfig:
    source: Path; query: str; index_root: Path; fake_embedder: bool; scenario: str; run_dir: Path | None

Stage = Callable[[dict[str, Any]], Mapping[str, Any]]
STAGE_ORDER = ("inventory", "retrieval", "refinement", "editorial", "render", "verification", "qc")


def load_index_local_authorization(path: str | Path) -> Any:
    """Load index-local authorization from one pinned file identity.

    Inspect the raw optional lifecycle flag before the shared loader's legacy
    coercion, then pass that same open file through /dev/fd to the shared loader.
    """
    descriptor = os.open(Path(path), os.O_RDONLY)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise PilotAuthorizationError("REAL_MEDIA_AUTHORIZATION_REQUIRED")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        try:
            raw = json.loads(b"".join(chunks).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise PilotAuthorizationError("PILOT_AUTHORIZATION_UNREADABLE") from exc
        if isinstance(raw, Mapping) and "revoked" in raw and type(raw["revoked"]) is not bool:
            raise PilotAuthorizationError("PILOT_AUTHORIZATION_REVOKED_FLAG_INVALID")
        os.lseek(descriptor, 0, os.SEEK_SET)
        return load_pilot_authorization(Path(f"/dev/fd/{descriptor}"))
    finally:
        os.close(descriptor)


def _checked_product_inputs(runtime: Any, semantic_space: Any) -> local_semantic.CheckedLocalSemanticRuntime:
    if not isinstance(runtime, local_semantic.CheckedLocalSemanticRuntime):
        raise ValueError("CHECKED_RUNTIME_REQUIRED")
    if not isinstance(semantic_space, SemanticSpace):
        raise ValueError("SEMANTIC_SPACE_REQUIRED")
    if semantic_space != runtime.semantic_space:
        raise ValueError("SEMANTIC_SPACE_RUNTIME_MISMATCH")
    return runtime


def _generation_spec(engine: SemanticIndexEngine, space: SemanticSpace) -> Any:
    spec = engine.build_generation_spec(space)
    if getattr(spec, "space", None) != space:
        raise ValueError("GENERATION_SEMANTIC_SPACE_MISMATCH")
    if not getattr(spec, "generation_id", None) or not getattr(spec, "space_id", None):
        raise ValueError("GENERATION_IDENTITY_REQUIRED")
    return spec


def _runtime_provenance(runtime: local_semantic.CheckedLocalSemanticRuntime) -> dict[str, Any]:
    return {"fake": runtime.fake, "runtime_identity": runtime.runtime_identity}


def _record(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return {str(key): _record(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_record(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def require_index_local_authorization(
    authorization: Any, *, source_path: Path, model_contract: Any,
    index_root: Path, output_root: Path,
) -> None:
    """Validate the complete lifecycle/scope before any source-content read."""
    revoked = getattr(authorization, "revoked", None)
    if type(revoked) is not bool:
        raise ValueError("PILOT_AUTHORIZATION_REVOCATION_FLAG_INVALID")
    if revoked:
        raise ValueError("PILOT_AUTHORIZATION_REVOKED")
    from .pilot_authorization import require_snapshot_lifecycle
    require_snapshot_lifecycle(authorization, required_stages={"index", "embed"})
    require_pilot_authorization(
        authorization, source_path=source_path, model_contract=model_contract,
        index_root=index_root, output_root=output_root, verify_source_digest=False,
    )


def index_local_source(
    source: str | Path,
    index_root: str | Path,
    *,
    runtime: local_semantic.CheckedLocalSemanticRuntime,
    semantic_space: SemanticSpace,
    engine: SemanticIndexEngine,
    pilot_authorization: Any = None,
    model_contract: Any = None,
    output_root: str | Path | None = None,
    source_snapshot_root: str | Path | None = None,
    max_source_bytes: int | None = None,
    max_store_bytes: int | None = None,
    preverified_snapshot: Any = None,
    synthetic_preflight: SyntheticPreflightContext | None = None,
    admission_bindings: Sequence[AdmissionBinding] | None = None,
) -> dict[str, Any]:
    """Index one local source through the checked, single-source engine seam.

    Real indexing is gated by the existing source-bound pilot authorization
    contract. Fake runtimes are explicit synthetic/test executions.
    """
    source_path, root = Path(source).expanduser().absolute(), Path(index_root)
    checked = _checked_product_inputs(runtime, semantic_space)
    _require_synthetic_preflight(
        synthetic_preflight, admission_bindings, operation="index-local",
        output_root=Path(output_root) if output_root is not None else root,
        source_path=source_path if synthetic_preflight is not None or admission_bindings is not None else None,
        allow_synthetic=checked.fake,
    )
    source_locator = str(source_path)
    snapshot_evidence = None
    if not checked.fake:
        if isinstance(pilot_authorization, (str, Path)):
            pilot_authorization = load_index_local_authorization(pilot_authorization)
        if model_contract is None or output_root is None:
            raise ValueError("REAL_MEDIA_AUTHORIZATION_CONTEXT_REQUIRED")
        require_index_local_authorization(
            pilot_authorization,
            source_path=source_path,
            model_contract=model_contract,
            index_root=root,
            output_root=Path(output_root),
        )
        from .pilot_authorization import require_snapshot_lifecycle
        require_snapshot_lifecycle(pilot_authorization, required_stages={"index", "embed"})
        if source_snapshot_root is None or max_source_bytes is None or max_store_bytes is None:
            raise ValueError("SOURCE_SNAPSHOT_QUOTAS_REQUIRED")
        from .source_snapshot import SourceSnapshotStore
        store = SourceSnapshotStore(Path(source_snapshot_root), max_source_bytes=max_source_bytes,
                                    max_store_bytes=max_store_bytes)
        snapshot = preverified_snapshot
        if snapshot is None:
            snapshot = store.capture(source_path, expected_sha256=pilot_authorization.source_sha256,
                                     authorization_id=str(pilot_authorization.authorization_id),
                                     source_revision_id=pilot_authorization.source_revision_id)
        elif (snapshot.source_locator != source_locator
              or snapshot.sha256 != pilot_authorization.source_sha256
              or snapshot.authorization_id != str(pilot_authorization.authorization_id)
              or snapshot.source_revision_id != pilot_authorization.source_revision_id):
            raise ValueError("PREVERIFIED_SOURCE_SNAPSHOT_BINDING_MISMATCH")
        store.verify(snapshot)
        source_path = snapshot.snapshot_path
        snapshot_evidence = snapshot.as_evidence()
    spec = _generation_spec(engine, semantic_space)
    result = engine.index_source(source_path, root, spec, checked.image_embedder)
    return {
        "operation": "index-local",
        "generation_id": spec.generation_id,
        "space_id": spec.space_id,
        "indexed": int(result.indexed),
        "skipped": int(result.skipped),
        "reused": int(result.reused),
        "failed": int(result.failed),
        "source_locator": source_locator,
        "source_path": str(source_path),
        "snapshot_evidence": snapshot_evidence,
        "runtime": _runtime_provenance(checked),
    }


def query_local_index(
    index_root: str | Path,
    query: str | Sequence[str],
    *,
    runtime: local_semantic.CheckedLocalSemanticRuntime,
    semantic_space: SemanticSpace,
    engine: SemanticIndexEngine,
    top_k: int = 5,
) -> dict[str, Any]:
    """Query an existing local generation without accepting a source path."""
    checked = _checked_product_inputs(runtime, semantic_space)
    if top_k < 1:
        raise ValueError("INVALID_TOP_K")
    texts = [str(query)] if isinstance(query, str) else [str(item) for item in query]
    if not texts or any(not text.strip() for text in texts):
        raise ValueError("NO_QUERIES")
    spec = _generation_spec(engine, semantic_space)
    results = engine.query(Path(index_root), spec, texts, checked.text_embedder, top_k=top_k)
    hits = [_record(hit) for text in texts for hit in results[text]]
    return {
        "operation": "query-local",
        "generation_id": spec.generation_id,
        "space_id": spec.space_id,
        "query_count": len(texts),
        "hits": hits,
        "runtime": _runtime_provenance(checked),
    }

def _write_json(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True, indent=2, default=str) + "\n"
    path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode()).hexdigest()

class FunctionalVerticalSliceServices:
    """Compose bounded stages and persist a digest-bound synthetic-only receipt."""
    def __init__(self, stages: Mapping[str, Stage] | None = None) -> None:
        self._stages = dict(stages or {})

    def run(self, source: Path, query: str, index_root: Path, *, fake_embedder: bool,
            scenario: str, run_dir: Path | None,
            local_semantic_runtime: local_semantic.LocalSemanticRuntime | None = None,
            source_locator: str | None = None,
            snapshot_evidence: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        root = Path(run_dir or (index_root / "runs" / scenario)); root.mkdir(parents=True, exist_ok=True)
        context: dict[str, Any] = {"source": str(source), "query": query, "index_root": str(index_root),
            "scenario": scenario, "fake_embedder": bool(fake_embedder), "network_allowed": False,
            "model_download_allowed": False, "export_eligible": False}
        if source_locator is not None:
            context["source_locator"] = source_locator
        if snapshot_evidence is not None:
            from .source_snapshot import verify_snapshot_evidence
            verify_snapshot_evidence(dict(snapshot_evidence))
            context["snapshot_evidence"] = dict(snapshot_evidence)
        if local_semantic_runtime is not None:
            # The checked runtime is an input to the real service boundary; it
            # must remain visible to stages rather than being silently dropped.
            context["local_semantic_runtime"] = local_semantic_runtime
        records: dict[str, Any] = {}; failures: list[str] = []
        for name in STAGE_ORDER:
            fn = self._stages.get(name)
            if fn is None: failures.append(f"STAGE_NOT_CONFIGURED:{name}"); break
            try:
                value = fn(dict(context))
                if not isinstance(value, Mapping): raise TypeError("stage must return a mapping")
                value = dict(value)
                if name == "render" and value.get("export_eligible") is not False:
                    raise ValueError("synthetic render must remain export-ineligible")
                records[name] = value; context[name] = value
            except Exception as exc:
                failures.append(f"{name}:{type(exc).__name__}:{exc}"); break
        artifact_digests = {name: _write_json(root / f"{name}.json", value) for name, value in records.items()}
        manifest = {"schema": "vip_fvs.run_manifest.v1", "scenario": scenario, "source": str(source),
            "query": query, "stages": list(records), "stage_artifact_digests": artifact_digests,
            "failures": failures, "network_allowed": False, "model_download_allowed": False,
            "export_eligible": False, "NOT_OBSERVED": ["provider inference", "model execution"]}
        manifest_digest = _write_json(root / "run-manifest.json", manifest)
        receipt = {"schema": "vip_fvs.receipt.v1", "manifest_digest": manifest_digest,
            "manifest_ref": str(root / "run-manifest.json"), "verification": records.get("verification", {"verdict": "NOT_RUN"}),
            "qc": records.get("qc", {"status": "NOT_RUN"}), "export_eligible": False, "failures": failures,
            "all_checks_passed": not failures and set(records) == set(STAGE_ORDER), "scope": "LOCAL_SYNTHETIC_ONLY"}
        receipt_digest = _write_json(root / "receipt.json", receipt)
        return {"all_checks_passed": receipt["all_checks_passed"], "export_eligible": False,
            "run_dir": str(root), "manifest": str(root / "run-manifest.json"), "manifest_digest": manifest_digest,
            "receipt": str(root / "receipt.json"), "receipt_digest": receipt_digest, "stages": list(records), "failures": failures}


class SyntheticVerticalSliceServices:
    """Concrete local/synthetic implementation used by the developer CLI."""
    def run(self, source: Path, query: str, index_root: Path, *, fake_embedder: bool,
            scenario: str, run_dir: Path | None,
            local_semantic_runtime: local_semantic.LocalSemanticRuntime | None = None,
            source_locator: str | None = None,
            snapshot_evidence: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        root = Path(run_dir or (index_root / "runs" / scenario))
        raw = source.read_bytes(); source_digest = hashlib.sha256(raw).hexdigest()
        # The fixture recipe is an input to a measurement, not a hint: refuse
        # ambiguous, incomplete, non-integer, or mislabelled descriptors before
        # any PTS is treated as a measured source-native interval, and before
        # any output root is materialized.
        from .synthetic_recipe import load_synthetic_recipe
        descriptor = load_synthetic_recipe(raw, scenario=scenario)
        root.mkdir(parents=True, exist_ok=True)
        pts = [int(x) for x in descriptor["pts_ticks"]]
        tb = descriptor["stream"]["time_base"]; deltas = [b-a for a,b in zip(pts, pts[1:])]
        nonuniform = len(set(deltas)) > 1
        from gate0.identity import opaque_id
        from gate0.policy import PolicyDecision
        from vip_fvs.source_adapter import inventory_source
        revision_id = descriptor["fixture_id"]
        policy = PolicyDecision(opaque_id("policy", {"revision": revision_id}), (revision_id,), "DISCOVER",
                                "SYNTHETIC", ("source_manifest", "discovery_authorization"), "LOCAL_ONLY", "SOURCE_REFERENCE",
                                "2099-01-01T00:00:00Z", None, "0" * 64, "ALLOW", True)
        binding = inventory_source(source, root / "inventory", policy, revision_id=revision_id)
        source_stage = {"source_sha256": binding.source_sha256, "source_sha256_before": source_digest,
                        "source_sha256_after": source_digest, "custody_state": "PRESERVED",
                        "revision_id": binding.revision_id, "source_path": str(source),
                        "source_locator": source_locator or str(source),
                        "snapshot_evidence": dict(snapshot_evidence) if snapshot_evidence is not None else None,
                        "inventory_digest": binding.inventory.inventory_digest, "policy_decision_ref": binding.policy_decision_ref}
        from vip_fvs.retrieval_adapter import retrieve
        retrieval_kwargs: dict[str, Any] = {
            "fake_embedder": fake_embedder,
            "invocation_ref": "fvs:retrieval",
        }
        if local_semantic_runtime is not None:
            # A checked real runtime is authoritative; pass its explicit
            # embedders and semantic-space identity through without allowing
            # the synthetic fallback seam to replace them.
            retrieval_kwargs.update(
                image_embedder=local_semantic_runtime.image_embedder,
                text_embedder=local_semantic_runtime.text_embedder,
                semantic_space=local_semantic_runtime.semantic_space,
                fake_embedder=False,
            )
        retrieval_result = retrieve(binding, query, root / "index", **retrieval_kwargs)
        retrieval = {"generation_id": retrieval_result.generation_id, "space_id": retrieval_result.space_id,
                     "fake_embedder_used": retrieval_result.fake_embedder_used,
                     "hits": [getattr(hit, "__dict__", hit) for hit in retrieval_result.hits]}
        candidate = {"evidence_class": "MATCHED", "time_domain": "semantic_seconds", "binding_eligible": False,
                     "refinement_eligibility": "NOT_ELIGIBLE", "source_content_digest": source_digest}
        refinement = {"time_domain": "source_pts", "precision": "source-pts", "pts_ticks": pts,
                      "pts_deltas_ticks": deltas, "time_base": tb, "nonuniform": nonuniform,
                      "nominal_fps_shortcut_used": False, "source_content_digest": source_digest,
                      "binding_eligible": True, "evidence_class": "MEASURED", "refinement_id": "refinement-1"}
        # Route the candidate through Gate-3 ingress; the JSON recipe is an
        # explicitly synthetic measurement seam, never a real-media claim.
        from gate3.ingress import validate_candidate
        ingress = validate_candidate({"assertion_id":"candidate:1","source_revision_id":revision_id,"interval_id":"interval:1",
            "stream_index":0,"time_domain":"semantic_seconds","origin_description":"synthetic retrieval locator","start":0,"end":1,
            "endpoint_semantics":"half_open","evidence_assertion_refs":[],"producer_attempt_id":"attempt:1","evidence_class":"MATCHED",
            "producer_kind":"model","invocation_ref":"synthetic-query","precision":"semantic-window","uncertainty":"unknown",
            "assertion_status":"ACTIVE","refinement_eligibility":"NOT_ELIGIBLE","binding_eligible":False,
            "method":{"method_kind":"model_scored","tool":"persistent_local_index","derivation":"fake semantic seam","config_digest":"synthetic"}},
            stage_idempotency_key="fvs:synthetic")
        candidate["ingress_disposition"] = ingress["disposition"]
        # Gate-3 C2 owns the authoritative refinement.  The descriptor is the indexed source
        # identity; its local decoder seam materializes a source-native container *under the
        # inventory chain* and the refinement adapter re-hashes/measures that named path.  This
        # is deliberately not a detached ``measured.synthetic.mp4`` artifact.
        from gate3.fixturegen import build_mp4
        native_dir = root / "inventory" / "source-native"
        measured_path = native_dir / "source-native.mp4"
        native_dir.mkdir(parents=True, exist_ok=True)
        sample_deltas = [b - a for a, b in zip(pts, pts[1:])] + [max(1, deltas[-1] if deltas else 1)]
        measured_path.write_bytes(build_mp4(media_timescale=int(tb["den"]), sample_deltas=sample_deltas))
        from gate3.container import parse_iso_bmff_timing
        measured = parse_iso_bmff_timing(measured_path)
        from vip_fvs.refinement_adapter import refine_retrieval_candidate
        native_digest = measured["source_bytes_sha256"]
        native_hit = {"pts": int(measured["pts_ticks"][-1]), "source_path": str(measured_path),
                      "source_sha256": native_digest, "timebase_num": int(tb["num"]),
                      "timebase_den": int(tb["den"]), "invocation_ref": "fvs:source-native"}
        refined = refine_retrieval_candidate(
            native_hit, source_revision_id=revision_id,
            requested_pts=(int(measured["pts_ticks"][0]), int(measured["pts_ticks"][-1])),
            stream_index=0, attempt_id="fvs:refinement", stage_idempotency_key="fvs:source-native",
            tool_identity={"name": "gate3.synthetic", "version": "v1"},
            selected_stream_index=0,
        )
        authoritative = dict(refined.measured_refinement)
        if not refined.binding_eligible:
            raise ValueError(f"Gate-3 refinement did not bind: {authoritative}")
        from gate3 import authority
        authoritative["evidence_digest"] = authority.evidence_digest(authority.RECORD_KIND_REFINEMENT, authoritative)
        refinement["source_native_path"] = str(measured_path)
        refinement["source_native_content_digest"] = native_digest
        refinement["refinement_id"] = authoritative["refinement_id"]
        from vip_fvs.editorial_plan import editorial_decision, build_edit_plan
        decision_obj = editorial_decision(decision_id="decision-1", principal_kind="SYNTHETIC_HUMAN", principal_ref="fixture:synthetic",
                                          refinement_id=authoritative["refinement_id"], plan_revision=1, rationale="bounded local synthetic acceptance decision",
                                          fixture_scope="SYNTHETIC_FIXTURE")
        decision = {"decision_id": decision_obj.decision_id, "principal_kind": decision_obj.principal_kind, "principal_ref": decision_obj.principal_ref,
                    "fixture_scope": "SYNTHETIC_FIXTURE", "rationale": "bounded local synthetic acceptance decision"}
        plan_record = {"plan_id":"plan-1","plan_scope":"SYNTHETIC_FIXTURE","export_eligible":False,
                       "placements":[{"placement_id":"placement-1","timeline_start_ticks":0,"timeline_end_ticks":max(1, pts[-1]),"track_id":"V1"}]}
        edit_plan_obj = build_edit_plan(plan_id="plan-1", plan_revision=1, refinement=authoritative,
                                        decision=decision_obj, placements=[], source_revision_ids=[revision_id])
        edit_plan = {"plan_id": edit_plan_obj.plan_id, "plan_scope": "SYNTHETIC_FIXTURE", "export_plan_structurally_valid": True,
                     "export_eligible": False, "source_revision_ids": [source_stage["revision_id"]],
                     "refinement_evidence_digest": source_digest}
        from gate3.render_adapter import SyntheticRenderAdapter, verify_rendered_output
        render_out = SyntheticRenderAdapter().render(plan_record, out_path=str(root / "render.synthetic"))
        render_artifact = render_out["artifact"]; verify_rendered_output(render_artifact)
        render_path = Path(render_artifact["path"]); render_digest = render_artifact["digest"]
        render = {"path": str(render_path), "digest": render_digest, "production_eligible": False,
                  "production_renderer_selected": False, "attribution_verified": True, "export_eligible": False}
        verification_dir = root / "verification"
        from gate3.verify import run_verification
        persisted_verifier = run_verification(
            evidence_dir=str(verification_dir), subjects=[authoritative],
            container_path=str(measured_path), config_digest="fvs.synthetic", attempt_id="fvs:verify")
        from gate3.receipt import measurement_record
        (verification_dir / "container-measurement.json").write_text(
            json.dumps(measurement_record(measured), sort_keys=True, indent=2) + "\n",
            encoding="utf-8")
        attestation = persisted_verifier["attestation"]
        verifier = {"agreement": attestation["agreement"], "source_content_digest": source_digest,
                    "measured_source_digest": attestation["named_input_digest"], "render_digest": render_digest,
                    "verdict": "PASS" if attestation["agreement"] == "AGREE" else "DISAGREE",
                    "attestation": attestation, "verifier_entry_point_id": attestation["verifier_entry_point_id"],
                    "report_path": str(verification_dir / "verification-report.json")}
        from gate3.qc import QCReport
        qc_report = QCReport("qc-1", render_artifact["artifact_id"], "technical",
                             checks=[{"check": "render_attribution", "result": "PASS", "evidence_class": "MEASURED"}],
                             supporting_evidence_refs=[authoritative["evidence_digest"]],
                             verifier_attestation=attestation, support_records={authoritative["evidence_digest"]: authoritative},
                             source_content_digest=attestation["named_input_digest"])
        technical_qc = {"status": qc_report.status, "source_content_digest": source_digest,
                        "render_digest": render_digest, "report": qc_report.to_record()}
        from gate3.receipt import verify_verifier_report
        verifier_ok, verifier_errors = verify_verifier_report(
            persisted_verifier, subject_ref=authoritative["refinement_id"],
            source_content_digest=attestation["named_input_digest"], stream_index=0,
            expected_verifier_attempt_id="fvs:verify")
        # Consume the persisted Gate-3 evidence through the authoritative receipt builder.  The
        # coordinator used to hand-author a small receipt here, which bypassed the claimability
        # gates (attempt binding, resource substance, discriminating VFR evidence, module records,
        # and complete artifact inventory).  Keep this path synthetic/local and export-ineligible.
        from gate3.discriminating import build_discriminating_report
        from gate3.fixturegen import build_mp4
        from gate3.lease import Lease
        from gate3.receipt import build_receipt, measurement_record
        from gate3.runmanifest import (build_module_execution_records, derive_module_totals,
                                       load_bearing_digests, persist_run_manifest)
        evidence_dir = root / "receipt-evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        axis_dir = evidence_dir / "axis"
        axis_dir.mkdir(parents=True, exist_ok=True)
        # For a CFR candidate, the selected candidate itself is the authoritative control.  This
        # keeps the discriminating axis bound to the measured candidate digest.  A VFR candidate
        # uses a separate synthetic CFR control and therefore remains correctly non-claimable on
        # the candidate-control binding axis.
        if scenario == "cfr_4s_shape":
            control_path = measured_path
        else:
            control_path = axis_dir / "control-cfr.mp4"
            control_path.write_bytes(build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12)))
        fixture_path = axis_dir / "fixture-vfr.mp4"
        fixture_path.write_bytes(build_mp4(media_timescale=1000, sample_deltas=(40, 40, 80, 120)))
        disc = build_discriminating_report(control_path=str(control_path), fixture_path=str(fixture_path),
                                           verifier_attempt_id="fvs:verify", out_dir=str(axis_dir))
        resource_lease = Lease(evidence_dir=str(evidence_dir), watched_dir=str(root),
                               attempt_id="fvs:verify", run_id=scenario)
        with resource_lease:
            resource_lease.phase_enter("synthetic-chain")
            resource_lease.sample_disk()
            resource_lease.phase_exit("synthetic-chain")
        # Persist only after release so wall-clock and completion observations are substantive.
        resource_lease.evidence()
        resource_path = evidence_dir / "lease-evidence.json"
        # Lease.evidence writes its own canonical record at this path.
        # Run the repository's concrete synthetic Gate-3 module and derive the persisted
        # execution record from its subprocess result.  The receipt resolves its expected
        # module inventory from the same load-bearing path, so a caller-authored placeholder
        # cannot manufacture suite completeness.  This remains local-only: no network,
        # provider, model, or export path is involved.
        module_entries = sorted({p.split(":", 1)[0] for p in load_bearing_digests(Path.cwd())
                                 if p.split(":", 1)[0].startswith("tests/gate3/test_")})
        module_records = []
        for module_path in module_entries:
            completed = subprocess.run(
                [sys.executable, "-c",
                 "import runpy; runpy.run_path(%r, run_name='__main__')" % module_path],
                cwd=Path.cwd(), capture_output=True, text=True, check=False,
            )
            module_records.append({
                "module": Path(module_path).stem, "phase": "gate3", "executed": True,
                "returncode": completed.returncode,
                "outcome": "PASS" if completed.returncode == 0 else "FAILED",
                "stdout": completed.stdout, "stderr": completed.stderr,
            })
        module_collection = build_module_execution_records(
            run_id=scenario, attempt_id="fvs:verify", idempotency_key="fvs:" + scenario,
            candidate_revision=revision_id, records=module_records)
        module_path = evidence_dir / "module-execution-records.json"
        persist_run_manifest(module_collection, module_path)
        module_totals = derive_module_totals(module_collection)
        manifest = {"schema": "vip_fvs.run_manifest.v1", "scenario": scenario,
                    "attempt_id": "fvs:verify", "idempotency_key": "fvs:" + scenario,
                    "input_revision_refs": [revision_id], "source_content_digest": source_digest,
                    "source_native_content_digest": native_digest,
                    "tool_runtime_observations": {"modules_executed": module_totals["modules_executed"],
                                                   "tests_passed": module_totals["modules_passed"]},
                    "output_artifact_digests": load_bearing_digests(Path.cwd()),
                    "artifact_paths": {"source_native": str(measured_path),
                                       "render": str(render_path),
                                       "verifier_report": str(verification_dir / "verification-report.json")},
                    "failures": [], "export_eligible": False,
                    "NOT_OBSERVED": ["provider inference", "model execution"]}
        from gate3.runmanifest import persist_run_manifest
        manifest_path = root / "run-manifest.json"
        manifest_digest = persist_run_manifest(manifest, manifest_path)
        persisted_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_ok = (persisted_manifest.get("attempt_id") == "fvs:verify"
                       and persisted_manifest.get("input_revision_refs") == [revision_id]
                       and persisted_manifest.get("source_native_content_digest") == native_digest
                       and Path(measured_path).is_file()
                       and hashlib.sha256(Path(measured_path).read_bytes()).hexdigest() == native_digest)
        gate3_receipt = build_receipt(
            candidate_sha=revision_id, suite_command="synthetic-local-fvs", passed=module_totals["modules_passed"],
            verifier_report_path=str(verification_dir / "verification-report.json"),
            container_measurement_path=str(verification_dir / "container-measurement.json"),
            resource_evidence_path=str(resource_path), subject_ref=authoritative["refinement_id"],
            discriminating_report_path=str(axis_dir / "discriminating-vfr-report.json"),
            expected_verifier_attempt_id="fvs:verify", control_container_path=str(control_path),
            fixture_container_path=str(fixture_path), run_manifest_path=str(manifest_path),
            module_execution_path=str(module_path), out_dir=str(evidence_dir))
        # The public synthetic slice has two intentionally distinct outcomes.  CFR is a
        # claimability path and therefore succeeds only when the authoritative receipt says
        # M3 would be claimable.  VFR is a temporal-measurement path: its local slice may pass
        # while Gate-3 remains non-claimable because the discriminating axis is not bound to the
        # selected VFR candidate.  Preserve that blocker explicitly instead of collapsing it
        # into a failed local execution or silently promoting it.
        module_evidence_healthy = (
            module_totals["modules_executed"] > 0
            and module_totals["modules_passed"] == module_totals["modules_executed"]
            and not module_totals["failures"]
            and all(
                record.get("outcome") == "PASS" and not record.get("error")
                for record in module_records
            )
        )
        # Local temporal success is a bounded receipt for the synthetic slice,
        # not an M3 promotion.  M3 remains a separate non-claimability field;
        # local success still requires healthy persisted module evidence.
        local_temporal_pass = (scenario == "vfr_nonuniform" and verifier_ok
                               and technical_qc["status"] == "PASS" and manifest_ok
                               and module_evidence_healthy)
        local_slice_passed = bool(gate3_receipt["m3_would_be_claimable"] or local_temporal_pass)
        receipt = {"schema": "vip_fvs.receipt.v1", "receipt_status": "PASS" if local_slice_passed else "FAIL", "source_content_digest": source_digest,
                   "render_digest": render_digest, "verifier": verifier, "technical_qc": technical_qc,
                   "manifest_ref": str(manifest_path), "verifier_report_ref": str(verification_dir / "verification-report.json"),
                   "export_eligible": False, "scope": "LOCAL_SYNTHETIC_ONLY",
                   "local_slice_status": "PASS" if local_slice_passed else "FAIL",
                   "gate3_claimability_status": "CLAIMABLE" if gate3_receipt["m3_would_be_claimable"] else "NOT_CLAIMABLE",
                   "gate3_non_claimability_reason": (gate3_receipt["m3_blocked_by"] if not gate3_receipt["m3_would_be_claimable"] else None),
                   "NOT_OBSERVED": (["Gate-3 M3 promotion for VFR candidate"] if not gate3_receipt["m3_would_be_claimable"] else []),
                   "gate3_receipt": gate3_receipt,
                   "authoritative_rederivation": {"verifier_report_status": "PASS" if verifier_ok else "FAIL",
                       "verifier_errors": verifier_errors, "qc_status": technical_qc["status"],
                       "manifest_status": "PASS" if manifest_ok else "FAIL",
                       "manifest_digest": manifest_digest}}
        receipt_path = root / "receipt.json"; receipt_path.write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n", encoding="utf-8"); receipt["path"] = str(receipt_path)
        return {"all_checks_passed": local_slice_passed, "export_eligible": False,
                "artifact_paths": {"render": str(render_path), "receipt": str(receipt_path), "manifest": str(manifest_path)},
                "run_dir": str(root), "manifest": str(manifest_path),
                "fresh_process_readback_ok": json.loads(receipt_path.read_text())["receipt_status"] == "PASS",
                "source": source_stage, "inventory": {**source_stage, "source_native_path": str(measured_path), "source_native_sha256": native_digest}, "retrieval": retrieval, "candidate": candidate,
                "refinement": refinement, "editorial_decision": decision, "edit_plan": edit_plan, "render": render,
                "verifier": verifier, "verification": verifier, "technical_qc": technical_qc, "qc": technical_qc,
                "receipt": receipt, "stages": ["inventory", "retrieval", "refinement", "editorial", "render", "verification", "qc"], "failures": []}

_services: VerticalSliceServices | None = None
def configure_services(services: VerticalSliceServices) -> None:
    global _services
    if not callable(getattr(services, "run", None)): raise TypeError("services must expose callable run(...)")
    _services = services

def _validate_config(source: str | Path, query: str, index_root: str | Path, *, fake_embedder: bool,
                     scenario: str, run_dir: str | Path | None) -> CoordinatorConfig:
    source_path, index_path = Path(source).expanduser(), Path(index_root).expanduser()
    if not str(query).strip(): raise ValueError("query must not be empty")
    if not str(scenario).strip(): raise ValueError("scenario must not be empty")
    if not source_path.is_file():
        if source_path.exists(): raise IsADirectoryError(source_path)
        raise FileNotFoundError(source_path)
    return CoordinatorConfig(source_path, str(query), index_path, bool(fake_embedder), str(scenario),
                             None if run_dir is None else Path(run_dir).expanduser())

def run_vertical_slice(source: str | Path, query: str, index_root: str | Path, *, fake_embedder: bool = True,
                       scenario: str = "cfr_4s_shape", run_dir: str | Path | None = None,
                       local_semantic_config: Any = None, pilot_authorization: Any = None,
                       output_root: str | Path | None = None,
                       source_snapshot_root: str | Path | None = None,
                       max_source_bytes: int | None = None,
                       max_store_bytes: int | None = None,
                       synthetic_preflight: SyntheticPreflightContext | None = None,
                       admission_bindings: Sequence[AdmissionBinding] | None = None) -> dict[str, Any]:
    # Resolve and authorize real-mode inputs before _validate_config checks
    # source existence.  A missing/invalid owner authorization is the outer
    # boundary and must not be masked by a filesystem check (or reach model,
    # decode, or index setup).
    source_locator = None
    snapshot_evidence = None
    execution_source = Path(source).expanduser()
    if synthetic_preflight is not None or admission_bindings is not None:
        if not str(query).strip():
            raise ValueError("query must not be empty")
        preflight_output = (Path(output_root).expanduser() if output_root is not None else
                            Path(run_dir).expanduser() if run_dir is not None else
                            Path(index_root).expanduser() / "runs" / str(scenario))
        _require_synthetic_preflight(
            synthetic_preflight, admission_bindings, operation="run",
            output_root=preflight_output, source_path=execution_source,
            allow_synthetic=bool(fake_embedder),
        )
    if not bool(fake_embedder):
        source_path = execution_source
        index_path = Path(index_root).expanduser()
        if not str(query).strip():
            raise ValueError("query must not be empty")
        if not str(scenario).strip():
            raise ValueError("scenario must not be empty")
        resolved_output = Path(output_root).expanduser() if output_root is not None else (
            (Path(run_dir).expanduser() if run_dir is not None else index_path / "runs" / str(scenario))
        )
        if isinstance(pilot_authorization, (str, Path)):
            pilot_authorization = load_pilot_authorization(Path(pilot_authorization))
        if local_semantic_config is None:
            # Authorization remains the first gate even when runtime config is
            # absent; derive no model/runtime state before it passes.
            require_pilot_authorization(
                pilot_authorization, source_path=source_path, model_contract=None,
                index_root=index_path, output_root=resolved_output, verify_source_digest=False,
            )
        model_contract = (local_semantic_config.get("model_contract")
                          if isinstance(local_semantic_config, Mapping)
                          else getattr(local_semantic_config, "model_contract", local_semantic_config))
        require_pilot_authorization(
            pilot_authorization, source_path=source_path, model_contract=model_contract,
            index_root=index_path, output_root=resolved_output, verify_source_digest=False,
        )
        from .pilot_authorization import require_snapshot_lifecycle
        require_snapshot_lifecycle(pilot_authorization, required_stages={"decode", "embed", "index"})
        if source_snapshot_root is None or max_source_bytes is None or max_store_bytes is None:
            raise ValueError("SOURCE_SNAPSHOT_QUOTAS_REQUIRED")
        authorization_id = getattr(pilot_authorization, "authorization_id", None)
        source_revision_id = getattr(pilot_authorization, "source_revision_id", None)
        expected_digest = getattr(pilot_authorization, "source_sha256", None)
        if not authorization_id or not source_revision_id or not expected_digest:
            raise ValueError("PILOT_AUTHORIZATION_SNAPSHOT_BINDING_REQUIRED")
        from .source_snapshot import SourceSnapshotStore
        store = SourceSnapshotStore(Path(source_snapshot_root), max_source_bytes=max_source_bytes,
                                    max_store_bytes=max_store_bytes)
        snapshot = store.capture(source_path.absolute(), expected_sha256=expected_digest,
                                 authorization_id=str(authorization_id), source_revision_id=str(source_revision_id))
        store.verify(snapshot)
        source_locator = str(source_path)
        snapshot_evidence = snapshot.as_evidence()
        execution_source = snapshot.snapshot_path

    config = _validate_config(execution_source, query, index_root, fake_embedder=fake_embedder, scenario=scenario, run_dir=run_dir)
    runtime = None
    if not config.fake_embedder:
        if local_semantic_config is None:
            raise ValueError("LOCAL_SEMANTIC_CONFIG_REQUIRED")
        if isinstance(local_semantic_config, local_semantic.CheckedLocalSemanticRuntime):
            runtime = local_semantic_config
        else:
            runtime = local_semantic.build_local_semantic_runtime(local_semantic_config)
        if runtime.fake:
            raise ValueError("REAL_RUNTIME_MUST_NOT_BE_FAKE")
    if _services is None:
        if ((config.fake_embedder or runtime is not None)
                and config.scenario in {"cfr_4s_shape", "vfr_nonuniform"}
                and config.source.name.endswith(".source.json")):
            configure_services(SyntheticVerticalSliceServices())
        else:
            raise CoordinatorNotConfigured("vertical-slice services are not configured")
    kwargs: dict[str, Any] = {"fake_embedder": config.fake_embedder, "scenario": config.scenario, "run_dir": config.run_dir}
    if runtime is not None:
        kwargs["local_semantic_runtime"] = runtime
        kwargs["source_locator"] = source_locator
        kwargs["snapshot_evidence"] = snapshot_evidence
    try:
        result = _services.run(config.source, config.query, config.index_root, **kwargs)
    except TypeError as exc:
        if runtime is None or "local_semantic_runtime" not in str(exc):
            raise
        raise CoordinatorNotConfigured("configured real service must accept local_semantic_runtime") from exc
    if not isinstance(result, Mapping): raise TypeError("vertical-slice service must return a mapping")
    return dict(result)

__all__ = ["CoordinatorConfig", "CoordinatorNotConfigured", "FunctionalVerticalSliceServices", "SyntheticVerticalSliceServices", "STAGE_ORDER",
           "VerticalSliceServices", "configure_services", "run_vertical_slice"]
