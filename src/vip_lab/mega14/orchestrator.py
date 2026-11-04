"""End-to-end synthetic pipeline orchestrator across MEGA-08..MEGA-14."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from gate2.workload import WorkloadSpec
from persistent_local_index.model_space import GenerationSpec, build_generation_spec
from vip_fvs.batch_report import (
    build_single_arm_batch_report,
    build_three_arm_batch_report,
    verify_batch_report,
)
from vip_fvs.batch_retrieval import run_batch_retrieval
from vip_fvs.query_batch import QUERY_CATALOG_SCHEMA_VERSION, parse_query_catalog_mapping
from vip_fvs.semantic_index import SearchHit, SemanticSpace
from vip_fvs.source_adapter import MultiSourceManifest, SourceManifestEntry
from vip_fvs.synthetic_profiles import (
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
    build_synthetic_profile_runtime,
    make_synthetic_profile,
)
from vip_fvs.three_arm_batch import (
    ARM_VIP_V1_BASE,
    ARM_VIP_V2_BASE,
    ARM_VIP_V2_SO400M,
    PROFILE_ID_TO_ARM,
    ThreeArmBatchArmResult,
    ThreeArmBatchResult,
)
from vip_lab.common import ReadinessStatus, canonical_sha256
from vip_lab.mega08 import (
    MEGA_08_14_SPEC_VERSION,
    build_capability_inventory,
    inspect_capability_gate,
)
from vip_lab.mega09 import (
    build_queue_from_batch_report,
    inspect_review_queue_intake,
)
from vip_lab.mega10 import (
    build_temporal_refinement_request,
    inspect_temporal_measurement_boundary,
)
from vip_lab.mega11 import (
    advance_proposal_revision,
    build_editorial_proposal,
    inspect_editorial_decision_boundary,
    verify_proposal_revision_chain,
)
from vip_lab.mega12 import (
    build_replay_graph_from_workload,
    build_synthetic_recovery_measurement_set,
    coerce_canonical_workload_spec,
    evaluate_fault_scenario_matrix,
    inspect_recovery_replay_consistency,
)
from vip_lab.mega13 import (
    audit_cross_stage_lineage,
    build_release_blocker_summary,
    evaluate_qc_readiness,
)
from vip_lab.mega14.report import (
    E2E_REPORT_SCHEMA_VERSION,
    EndToEndLabReport,
    compute_e2e_report_digest,
    verify_e2e_lab_report,
)
from vip_lab.mega14.scenario import (
    SyntheticLabScenario,
    default_three_arm_scenario,
    parse_e2e_scenario_mapping,
)


class _DeterministicScenarioEngine:
    """Read-only deterministic search engine backed by scenario source entries."""

    def __init__(self, space: SemanticSpace, hits: Sequence[SearchHit]) -> None:
        self.spec = build_generation_spec(space)
        self.hits = tuple(hits)

    def build_generation_spec(self, space: SemanticSpace) -> GenerationSpec:
        return self.spec

    def index_source(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("index_source is forbidden during read-only batch retrieval")

    def query(
        self,
        index_root: Path,
        spec: GenerationSpec,
        texts: Sequence[str],
        text_embedder: Any,
        *,
        top_k: int,
    ) -> Mapping[str, Sequence[SearchHit]]:
        _ = text_embedder(tuple(texts))
        return {
            text: tuple(dataclasses.replace(h, query=text) for h in self.hits[:top_k])
            for text in texts
        }


def _build_manifest_from_scenario(scenario: SyntheticLabScenario) -> MultiSourceManifest:
    entries: list[SourceManifestEntry] = []
    for s in scenario.sources:
        entries.append(
            SourceManifestEntry(
                revision_id=str(s["revision_id"]),
                content_id=str(s["content_id"]),
                source_path=Path(str(s["source_path"])),
                source_sha256=str(s["source_sha256"]),
                selected_stream_index=0,
                selection_source="explicit",
                inventory_digest="b" * 64,
                policy_decision_ref="policy-synthetic-mega14",
                custody_state="synthetic",
            )
        )
    ordered = tuple(
        sorted(
            entries,
            key=lambda e: (
                e.revision_id.encode("utf-8"),
                str(e.source_path).encode("utf-8"),
            ),
        )
    )
    body = {
        "entries": [
            {
                "revision_id": e.revision_id,
                "content_id": e.content_id,
                "source_path": str(e.source_path),
                "source_sha256": e.source_sha256,
                "selected_stream_index": e.selected_stream_index,
                "selection_source": e.selection_source,
                "inventory_digest": e.inventory_digest,
                "policy_decision_ref": e.policy_decision_ref,
                "custody_state": e.custody_state,
                "inventory_artifact_id": e.inventory_artifact_id,
                "inventory_payload_digest": e.inventory_payload_digest,
            }
            for e in ordered
        ],
        "schema_version": "vip_fvs.multi_source_manifest.v1",
    }
    raw = json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return MultiSourceManifest(ordered, hashlib.sha256(raw).hexdigest())


def _build_hits_from_scenario(scenario: SyntheticLabScenario) -> tuple[SearchHit, ...]:
    hits: list[SearchHit] = []
    for idx, s in enumerate(scenario.sources):
        hits.append(
            SearchHit(
                query="placeholder",
                rank=idx + 1,
                score=float(s.get("score", max(0.5, 0.95 - idx * 0.05))),
                row_id=idx,
                source_path=str(s["source_path"]),
                source_sha256=str(s["source_sha256"]),
                pts=int(s.get("sample_pts", 3003)),
                timebase_num=scenario.timebase_num,
                timebase_den=scenario.timebase_den,
                timestamp_human=str(s.get("timestamp_human", "00:00:00.100")),
                thumbnail_path=None,
                thumbnail_status="MISSING",
            )
        )
    return tuple(hits)


def run_end_to_end_synthetic_lab(
    scenario: SyntheticLabScenario | Mapping[str, Any] | None = None,
    *,
    workspace_root: str | Path | None = None,
) -> EndToEndLabReport:
    if scenario is None:
        scen = default_three_arm_scenario()
    elif isinstance(scenario, SyntheticLabScenario):
        scen = scenario
    else:
        scen = parse_e2e_scenario_mapping(scenario)

    root_path = (
        Path(workspace_root).resolve()
        if workspace_root is not None
        else Path(__file__).resolve().parents[3]
    )

    # 1. MEGA-08: Capability & Gap Inventory
    inv_report = build_capability_inventory(root_path)
    pkt_mega08 = inspect_capability_gate({"workspace_root": str(root_path)})

    # 2. vip_fvs (W1–W5): Query catalog, manifest, synthetic profile runtime(s), batch retrieval & batch report
    catalog = parse_query_catalog_mapping(
        {
            "schema_version": QUERY_CATALOG_SCHEMA_VERSION,
            "catalog_id": scen.catalog_id,
            "queries": [dict(q) for q in scen.queries],
        }
    )
    manifest = _build_manifest_from_scenario(scen)
    hits = _build_hits_from_scenario(scen)

    if scen.mode == "SINGLE_ARM":
        bundle = build_synthetic_profile_runtime(
            make_synthetic_profile(scen.single_arm_profile_id)
        )
        engine = _DeterministicScenarioEngine(bundle.semantic_space, hits)
        single_res = run_batch_retrieval(
            catalog,
            manifest,
            Path(f"synth-idx-{scen.single_arm_profile_id}"),
            runtime=bundle.runtime,
            semantic_space=bundle.semantic_space,
            engine=engine,
            top_k=scen.top_k,
            profile_id=scen.single_arm_profile_id,
        )
        arm_id = PROFILE_ID_TO_ARM[scen.single_arm_profile_id]
        batch_report = build_single_arm_batch_report(single_res, arm_id=arm_id)
    else:
        arms_out: list[ThreeArmBatchArmResult] = []
        for arm_id, prof_id in (
            (ARM_VIP_V1_BASE, V1_PROFILE_ID),
            (ARM_VIP_V2_BASE, V2_BASE_PROFILE_ID),
            (ARM_VIP_V2_SO400M, V2_SO400M_PROFILE_ID),
        ):
            bundle = build_synthetic_profile_runtime(make_synthetic_profile(prof_id))
            engine = _DeterministicScenarioEngine(bundle.semantic_space, hits)
            single_res = run_batch_retrieval(
                catalog,
                manifest,
                Path(f"synth-idx-{arm_id}"),
                runtime=bundle.runtime,
                semantic_space=bundle.semantic_space,
                engine=engine,
                top_k=scen.top_k,
                profile_id=prof_id,
            )
            arms_out.append(
                ThreeArmBatchArmResult(
                    arm_id=arm_id,
                    profile_id=prof_id,
                    model_identity=bundle.semantic_space.model_identity,
                    space_id=single_res.space_id,
                    generation_id=single_res.generation_id,
                    embedding_dim=bundle.profile.embedding_dim,
                    row_width_bytes=bundle.row_width_bytes,
                    manifest_digest=manifest.manifest_digest,
                    catalog_digest=catalog.catalog_digest,
                    query_count=len(catalog.query_ids),
                    candidate_count=single_res.total_candidate_count,
                    batch_result=single_res,
                )
            )
        arm_map_digest = canonical_sha256(
            {"arms": [a.arm_id for a in arms_out], "scenario_id": scen.scenario_id}
        )
        three_res = ThreeArmBatchResult(
            catalog_id=catalog.catalog_id,
            catalog_digest=catalog.catalog_digest,
            query_ids=catalog.query_ids,
            top_k=scen.top_k,
            arm_map_digest=arm_map_digest,
            arms=tuple(arms_out),
        )
        batch_report = build_three_arm_batch_report(three_res)

    verified_batch_report = verify_batch_report(batch_report)

    # 3. MEGA-09: Nonbinding CandidateReviewQueue
    candidate_queue = build_queue_from_batch_report(verified_batch_report)
    pkt_mega09 = inspect_review_queue_intake({"candidate_queue": candidate_queue.to_dict()})

    # 4. MEGA-10: TemporalRefinementRequest & PTS fixture diagnostic
    lead_item = candidate_queue.items[0]
    temporal_request = build_temporal_refinement_request(
        lead_item,
        upstream_queue_digest=candidate_queue.queue_digest,
        selected_stream_index=0,
        requested_start_pts=scen.requested_start_pts,
        requested_end_pts=scen.requested_end_pts,
        pts_ticks=scen.pts_ticks,
    )
    pkt_mega10 = inspect_temporal_measurement_boundary(
        {
            "queue_item": lead_item.to_dict(),
            "upstream_queue_digest": candidate_queue.queue_digest,
            "selected_stream_index": 0,
            "requested_start_pts": scen.requested_start_pts,
            "requested_end_pts": scen.requested_end_pts,
            "pts_ticks": list(scen.pts_ticks),
        }
    )

    # 5. MEGA-11: Versioned EditorialProposal (v1 -> v2)
    prop_v1 = build_editorial_proposal(
        queue_item=lead_item,
        temporal_request=temporal_request,
        proposed_action="REVIEW_CANDIDATE",
        rationale_note="Initial synthetic candidate review note.",
    )
    prop_v2 = advance_proposal_revision(
        prior_proposal=prop_v1,
        proposed_action="REQUEST_MEASUREMENT",
        rationale_note="Request source-native PTS/frame measurement prior to human review.",
    )
    rev_chain_dicts = [prop_v1.to_dict(), prop_v2.to_dict()]
    verify_proposal_revision_chain(rev_chain_dicts)
    pkt_mega11 = inspect_editorial_decision_boundary(
        {
            "proposal": prop_v2.to_dict(),
            "revision_chain": rev_chain_dicts,
        }
    )

    # 6. MEGA-12 (+ Stretch S3): Generated-Only Recovery & Replay Consistency
    wl_spec, wl_id = coerce_canonical_workload_spec(scen.workload)
    replay_graph = build_replay_graph_from_workload(
        workload_spec=wl_spec,
        generation_id=lead_item.generation_id,
        semantic_space_id=lead_item.space_id,
        workload_id=wl_id,
    )
    fault_matrix = evaluate_fault_scenario_matrix(
        workload_spec=wl_spec,
        generation_id=lead_item.generation_id,
        semantic_space_id=lead_item.space_id,
        workload_id=wl_id,
    )
    measurement_set = build_synthetic_recovery_measurement_set(
        replay_graph=replay_graph,
        fault_matrix=fault_matrix,
    )
    pkt_mega12 = inspect_recovery_replay_consistency(
        {
            "workload_spec": dict(scen.workload),
            "generation_id": lead_item.generation_id,
            "semantic_space_id": lead_item.space_id,
        }
    )

    # 7. MEGA-13: Cross-Stage Lineage Audit, QC Evidence Completeness & Export Refusal
    lineage_receipt = audit_cross_stage_lineage(
        candidate_queue=candidate_queue,
        temporal_request=temporal_request,
        editorial_proposal=prop_v2,
        proposal_revision_chain=rev_chain_dicts,
        replay_graph=replay_graph,
    )
    pkt_mega13 = evaluate_qc_readiness(
        {
            "candidate_queue": candidate_queue.to_dict(),
            "temporal_request": temporal_request.to_dict(),
            "editorial_proposal": prop_v2.to_dict(),
            "proposal_revision_chain": rev_chain_dicts,
            "replay_graph": replay_graph.to_dict(),
        }
    )
    blocker_summary = build_release_blocker_summary(
        lineage_receipt=lineage_receipt,
        qc_packet=pkt_mega13,
    )

    stage_digests = {
        "mega08_inventory_digest": inv_report.inventory_digest,
        "vip_fvs_batch_report_digest": str(verified_batch_report["report_digest"]),
        "mega09_queue_digest": candidate_queue.queue_digest,
        "mega10_temporal_request_digest": temporal_request.request_digest,
        "mega11_proposal_digest": prop_v2.proposal_digest,
        "mega12_replay_graph_digest": replay_graph.graph_digest,
        "mega13_lineage_receipt_digest": lineage_receipt.receipt_digest,
    }

    artifacts: dict[str, Any] = {
        "capability_inventory": inv_report.to_dict(),
        "batch_report": dict(verified_batch_report),
        "candidate_queue": candidate_queue.to_dict(),
        "temporal_request": temporal_request.to_dict(),
        "editorial_proposal": prop_v2.to_dict(),
        "proposal_revision_chain": rev_chain_dicts,
        "replay_graph": replay_graph.to_dict(),
        "fault_matrix": fault_matrix,
        "recovery_measurements": measurement_set.to_dict(),
        "lineage_receipt": lineage_receipt.to_dict(),
        "release_blocker_summary": blocker_summary,
        "stage_packets": {
            "mega08": pkt_mega08.to_dict(),
            "mega09": pkt_mega09.to_dict(),
            "mega10": pkt_mega10.to_dict(),
            "mega11": pkt_mega11.to_dict(),
            "mega12": pkt_mega12.to_dict(),
            "mega13": pkt_mega13.to_dict(),
        },
    }

    provisional = EndToEndLabReport(
        schema_version=E2E_REPORT_SCHEMA_VERSION,
        spec_version=MEGA_08_14_SPEC_VERSION,
        scenario_id=scen.scenario_id,
        mode=scen.mode,
        status=ReadinessStatus.READY_SYNTHETIC.value,
        workspace_git_sha=inv_report.workspace_git_sha,
        declared_baseline_revision=inv_report.declared_baseline_revision,
        canonical_reference_sha=inv_report.canonical_reference_sha,
        synthetic_only=True,
        execution_authorized=False,
        authentic_model_evidence=False,
        real_media_accessed=False,
        production_export_authorized=False,
        export_status="REFUSED_NOT_AUTHORIZED",
        all_gates_verdict="NOT_APPROVED",
        stage_digests=stage_digests,
        artifacts=artifacts,
        report_digest="0" * 64,
    )
    digest = compute_e2e_report_digest(provisional.payload_without_digest())
    final_report = EndToEndLabReport(
        schema_version=provisional.schema_version,
        spec_version=provisional.spec_version,
        scenario_id=provisional.scenario_id,
        mode=provisional.mode,
        status=provisional.status,
        workspace_git_sha=provisional.workspace_git_sha,
        declared_baseline_revision=provisional.declared_baseline_revision,
        canonical_reference_sha=provisional.canonical_reference_sha,
        synthetic_only=True,
        execution_authorized=False,
        authentic_model_evidence=False,
        real_media_accessed=False,
        production_export_authorized=False,
        export_status="REFUSED_NOT_AUTHORIZED",
        all_gates_verdict="NOT_APPROVED",
        stage_digests=provisional.stage_digests,
        artifacts=provisional.artifacts,
        report_digest=digest,
    )
    verify_e2e_lab_report(final_report)
    return final_report
