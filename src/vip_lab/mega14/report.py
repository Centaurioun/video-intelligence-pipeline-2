"""End-to-End Lab Report and Stretch S2 Cross-Artifact Digest Verifier for MEGA-14."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from vip_fvs.batch_report import verify_batch_report
from vip_lab.common import (
    NOT_OBSERVED,
    VipLabError,
    canonical_json_dumps,
    canonical_sha256,
    validate_hex_digest,
)
from vip_lab.mega08.gap_digest import MEGA_08_14_SPEC_VERSION, verify_gap_digest
from vip_lab.mega09.queue_validation import verify_candidate_queue
from vip_lab.mega10.temporal_request import verify_temporal_refinement_request
from vip_lab.mega11.editorial_proposal import verify_editorial_proposal
from vip_lab.mega11.proposal_revisions import verify_proposal_revision_chain
from vip_lab.mega12.consistency_review import REQUIRED_NOT_OBSERVED_METRICS
from vip_lab.mega12.replay_graph import verify_replay_graph
from vip_lab.mega13.lineage_audit import audit_cross_stage_lineage

E2E_REPORT_SCHEMA_VERSION = "vip-lab-e2e-report-v1"


@dataclass(frozen=True)
class EndToEndLabReport:
    schema_version: str
    spec_version: str
    scenario_id: str
    mode: str
    status: str
    workspace_git_sha: str
    declared_baseline_revision: str
    canonical_reference_sha: str
    synthetic_only: bool
    execution_authorized: bool
    authentic_model_evidence: bool
    real_media_accessed: bool
    production_export_authorized: bool
    export_status: str
    all_gates_verdict: str
    stage_digests: dict[str, str]
    artifacts: dict[str, Any]
    report_digest: str

    def payload_without_digest(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "spec_version": self.spec_version,
            "scenario_id": self.scenario_id,
            "mode": self.mode,
            "status": self.status,
            "workspace_git_sha": self.workspace_git_sha,
            "declared_baseline_revision": self.declared_baseline_revision,
            "canonical_reference_sha": self.canonical_reference_sha,
            "synthetic_only": self.synthetic_only,
            "execution_authorized": self.execution_authorized,
            "authentic_model_evidence": self.authentic_model_evidence,
            "real_media_accessed": self.real_media_accessed,
            "production_export_authorized": self.production_export_authorized,
            "export_status": self.export_status,
            "all_gates_verdict": self.all_gates_verdict,
            "stage_digests": dict(self.stage_digests),
            "artifacts": dict(self.artifacts),
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload_without_digest()
        body["report_digest"] = self.report_digest
        return body

    def to_canonical_json(self) -> str:
        return canonical_json_dumps(self.to_dict())


def compute_e2e_report_digest(payload: Mapping[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "report_digest"}
    return canonical_sha256(body)


def verify_e2e_lab_report(
    report: EndToEndLabReport | Mapping[str, Any],
) -> dict[str, Any]:
    """Stretch S2: Full cross-artifact digest, foreign-key, and non-authority verifier."""
    payload = report.to_dict() if isinstance(report, EndToEndLabReport) else dict(report)

    if payload.get("schema_version") != E2E_REPORT_SCHEMA_VERSION:
        raise VipLabError(
            "E2E_REPORT_SCHEMA_MISMATCH",
            f"Expected schema_version {E2E_REPORT_SCHEMA_VERSION!r}, got {payload.get('schema_version')!r}.",
        )
    if payload.get("spec_version") != MEGA_08_14_SPEC_VERSION:
        raise VipLabError(
            "E2E_REPORT_SPEC_VERSION_MISMATCH",
            f"Expected spec_version {MEGA_08_14_SPEC_VERSION!r}, got {payload.get('spec_version')!r}.",
        )

    if (
        payload.get("synthetic_only") is not True
        or payload.get("execution_authorized") is not False
        or payload.get("authentic_model_evidence") is not False
        or payload.get("real_media_accessed") is not False
        or payload.get("production_export_authorized") is not False
        or payload.get("export_status") != "REFUSED_NOT_AUTHORIZED"
        or payload.get("all_gates_verdict") != "NOT_APPROVED"
        or payload.get("workspace_git_sha") != NOT_OBSERVED
    ):
        raise VipLabError(
            "E2E_AUTHORITY_VIOLATION",
            "EndToEndLabReport violated synthetic-only or non-authority invariants.",
        )

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise VipLabError("E2E_ARTIFACTS_MISSING", "artifacts must be a mapping.")

    inv = artifacts.get("capability_inventory")
    batch_rep = artifacts.get("batch_report")
    queue = artifacts.get("candidate_queue")
    temp_req = artifacts.get("temporal_request")
    proposal = artifacts.get("editorial_proposal")
    rev_chain = artifacts.get("proposal_revision_chain")
    replay_graph = artifacts.get("replay_graph")
    lineage_receipt = artifacts.get("lineage_receipt")

    if not all(
        isinstance(x, Mapping)
        for x in (inv, batch_rep, queue, temp_req, proposal, replay_graph, lineage_receipt)
    ):
        raise VipLabError(
            "E2E_ARTIFACTS_INCOMPLETE",
            "One or more required stage artifacts are missing from EndToEndLabReport.",
        )

    # 1. Re-verify each individual stage artifact
    verify_gap_digest(inv)
    try:
        verified_batch = verify_batch_report(batch_rep)
    except (ValueError, TypeError) as exc:
        raise VipLabError(
            "E2E_BATCH_REPORT_INVALID",
            f"Embedded batch_report failed verification: {exc}",
        ) from exc
    verified_queue = verify_candidate_queue(queue)
    verified_temp = verify_temporal_refinement_request(temp_req)
    proposal_digest = verify_editorial_proposal(proposal)
    if not isinstance(rev_chain, list) or len(rev_chain) == 0:
        raise VipLabError(
            "E2E_REVISION_CHAIN_INVALID",
            "proposal_revision_chain must be a non-empty list.",
        )
    chain_summary = verify_proposal_revision_chain(rev_chain)
    replay_digest = verify_replay_graph(replay_graph)

    # 2. Verify cross-stage foreign-key digest equality
    if verified_queue.get("upstream_report_digest") != verified_batch.get("report_digest"):
        raise VipLabError(
            "E2E_CROSS_STAGE_DIGEST_MISMATCH",
            "candidate_queue.upstream_report_digest != batch_report.report_digest",
        )
    if verified_temp.get("upstream_queue_digest") != verified_queue.get("queue_digest"):
        raise VipLabError(
            "E2E_CROSS_STAGE_DIGEST_MISMATCH",
            "temporal_request.upstream_queue_digest != candidate_queue.queue_digest",
        )
    if proposal.get("upstream_temporal_request_digest") != verified_temp.get("request_digest"):
        raise VipLabError(
            "E2E_CROSS_STAGE_DIGEST_MISMATCH",
            "editorial_proposal.upstream_temporal_request_digest != temporal_request.request_digest",
        )
    if chain_summary["head_proposal_digest"] != proposal_digest:
        raise VipLabError(
            "E2E_CROSS_STAGE_DIGEST_MISMATCH",
            "proposal_revision_chain head does not match editorial_proposal.proposal_digest",
        )

    recomputed_lineage = audit_cross_stage_lineage(
        candidate_queue=verified_queue,
        temporal_request=verified_temp,
        editorial_proposal=proposal,
        proposal_revision_chain=rev_chain,
        replay_graph=replay_graph,
    )
    if recomputed_lineage.receipt_digest != lineage_receipt.get("receipt_digest"):
        raise VipLabError(
            "E2E_CROSS_STAGE_DIGEST_MISMATCH",
            "lineage_receipt.receipt_digest does not match recomputed cross-stage lineage audit.",
        )

    stage_packets = artifacts.get("stage_packets")
    if isinstance(stage_packets, Mapping):
        mega12_packet = stage_packets.get("mega12")
        if isinstance(mega12_packet, Mapping):
            if mega12_packet.get("evidence_state") != NOT_OBSERVED:
                raise VipLabError(
                    "E2E_AUTHORITY_VIOLATION",
                    "MEGA-12 aggregate stage packet evidence_state must remain NOT_OBSERVED.",
                )
            m12_summary = mega12_packet.get("summary")
            if (
                not isinstance(m12_summary, Mapping)
                or m12_summary.get("observation_domain") != "SYNTHETIC_FIXTURE_ONLY"
            ):
                raise VipLabError(
                    "E2E_AUTHORITY_VIOLATION",
                    "MEGA-12 summary must declare observation_domain='SYNTHETIC_FIXTURE_ONLY'.",
                )

    rec_meas = artifacts.get("recovery_measurements")
    if isinstance(rec_meas, Mapping):
        not_obs_rows = rec_meas.get("not_observed")
        if not isinstance(not_obs_rows, list):
            raise VipLabError(
                "E2E_AUTHORITY_VIOLATION",
                "recovery_measurements.not_observed must be a list of NOT_OBSERVED records.",
            )
        not_obs_ids = {
            row.get("metric_id")
            for row in not_obs_rows
            if isinstance(row, Mapping) and row.get("status") == NOT_OBSERVED
        }
        if any(metric_id not in not_obs_ids for metric_id in REQUIRED_NOT_OBSERVED_METRICS):
            raise VipLabError(
                "E2E_AUTHORITY_VIOLATION",
                "recovery_measurements missing required NOT_OBSERVED archive/scale metrics.",
            )

    stage_digests = payload.get("stage_digests")
    if not isinstance(stage_digests, Mapping):
        raise VipLabError("E2E_STAGE_DIGESTS_MISSING", "stage_digests must be a mapping.")
    expected_stage_digests = {
        "mega08_inventory_digest": str(inv["inventory_digest"]),
        "vip_fvs_batch_report_digest": str(verified_batch["report_digest"]),
        "mega09_queue_digest": str(verified_queue["queue_digest"]),
        "mega10_temporal_request_digest": str(verified_temp["request_digest"]),
        "mega11_proposal_digest": proposal_digest,
        "mega12_replay_graph_digest": replay_digest,
        "mega13_lineage_receipt_digest": recomputed_lineage.receipt_digest,
    }
    for k, expected_val in expected_stage_digests.items():
        if stage_digests.get(k) != expected_val:
            raise VipLabError(
                "E2E_CROSS_STAGE_DIGEST_MISMATCH",
                f"stage_digests[{k!r}] mismatch: {stage_digests.get(k)!r} != {expected_val!r}",
            )

    declared_digest = validate_hex_digest(
        str(payload.get("report_digest", "")),
        field_name="report_digest",
        error_code="E2E_REPORT_DIGEST_INVALID",
    )
    computed_digest = compute_e2e_report_digest(payload)
    if declared_digest != computed_digest:
        raise VipLabError(
            "E2E_REPORT_DIGEST_MISMATCH",
            f"EndToEndLabReport digest mismatch: {declared_digest} != {computed_digest}",
        )
    return dict(payload)
