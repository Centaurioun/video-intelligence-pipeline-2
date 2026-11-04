"""Deterministic stage-input/stage-output ReplayGraph and JSONL journal verifier for MEGA-12."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from gate2.recovery import RecoveryBinding, RecoveryHarness
from gate2.workload import WorkloadSpec, generate
from vip_lab.common import (
    VipLabError,
    canonical_json_dumps,
    canonical_sha256,
    parse_strict_json_text,
    validate_hex_digest,
)

REPLAY_GRAPH_SCHEMA_VERSION = "vip-lab-replay-graph-v1"


@dataclass(frozen=True)
class ReplayNode:
    node_id: str
    job_index: int
    stage_index: int
    generation_id: str
    semantic_space_id: str
    parent_state_digest: str
    stage_payload_sha256: str
    post_state_digest: str
    commit_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "job_index": self.job_index,
            "stage_index": self.stage_index,
            "generation_id": self.generation_id,
            "semantic_space_id": self.semantic_space_id,
            "parent_state_digest": self.parent_state_digest,
            "stage_payload_sha256": self.stage_payload_sha256,
            "post_state_digest": self.post_state_digest,
            "commit_status": self.commit_status,
        }


@dataclass(frozen=True)
class ReplayGraph:
    schema_version: str
    workload_id: str
    seed: int
    generation_id: str
    semantic_space_id: str
    job_count: int
    stages_per_job: int
    initial_state_digest: str
    final_state_digest: str
    idempotent_replay_verified: bool
    duplicate_side_effects: int
    nodes: tuple[ReplayNode, ...]
    journal_lines: tuple[str, ...]
    graph_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "workload_id": self.workload_id,
            "seed": self.seed,
            "generation_id": self.generation_id,
            "semantic_space_id": self.semantic_space_id,
            "job_count": self.job_count,
            "stages_per_job": self.stages_per_job,
            "initial_state_digest": self.initial_state_digest,
            "final_state_digest": self.final_state_digest,
            "idempotent_replay_verified": self.idempotent_replay_verified,
            "duplicate_side_effects": self.duplicate_side_effects,
            "nodes": [n.to_dict() for n in self.nodes],
            "journal_lines": list(self.journal_lines),
            "graph_digest": self.graph_digest,
        }


def compute_replay_graph_digest(payload: Mapping[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "graph_digest"}
    return canonical_sha256(body)


def _compute_step_state_digest(
    *,
    parent_state_digest: str,
    generation_id: str,
    semantic_space_id: str,
    job_index: int,
    stage_index: int,
    stage_payload_sha256: str,
) -> str:
    return canonical_sha256(
        {
            "parent_state_digest": parent_state_digest,
            "generation_id": generation_id,
            "semantic_space_id": semantic_space_id,
            "job_index": job_index,
            "stage_index": stage_index,
            "stage_payload_sha256": stage_payload_sha256,
        }
    )


def build_replay_graph_from_workload(
    *,
    workload_spec: WorkloadSpec,
    generation_id: str = "gen-synth-001",
    semantic_space_id: str = "siglip-v1-base:768:v1",
) -> ReplayGraph:
    if not isinstance(workload_spec, WorkloadSpec):
        raise VipLabError(
            "INVALID_WORKLOAD_SPEC",
            "workload_spec must be a gate2.workload.WorkloadSpec instance.",
        )
    fixture = generate(workload_spec)
    binding = RecoveryBinding(
        generation_id=generation_id,
        semantic_space_id=semantic_space_id,
    )
    harness = RecoveryHarness(binding)
    initial_digest = harness.state_digest()

    nodes: list[ReplayNode] = []
    journal_lines: list[str] = []
    running_parent_digest = initial_digest
    duplicate_side_effects = 0
    idempotent_replay_verified = True

    for job in fixture.jobs:
        outcome = harness.run_job(
            job_id=job.job_index,
            stages=job.stages,
            expected_count=len(job.stages),
            expected_bytes=workload_spec.payload_bytes,
            generation_id=generation_id,
            semantic_space_id=semantic_space_id,
            declared_digest=job.digest,
        )
        replay_outcome = harness.run_job(
            job_id=job.job_index,
            stages=job.stages,
            expected_count=len(job.stages),
            expected_bytes=workload_spec.payload_bytes,
            generation_id=generation_id,
            semantic_space_id=semantic_space_id,
            declared_digest=job.digest,
        )
        if (
            outcome.get("status") != "COMMITTED"
            or replay_outcome.get("status") != "SKIPPED_ALREADY_COMMITTED"
            or outcome.get("post_state_digest") != replay_outcome.get("post_state_digest")
        ):
            idempotent_replay_verified = False
            duplicate_side_effects += 1

        for stage_idx, stage_bytes in enumerate(job.stages):
            stage_sha = canonical_sha256({"stage_hex": stage_bytes.hex()})
            step_post_digest = _compute_step_state_digest(
                parent_state_digest=running_parent_digest,
                generation_id=generation_id,
                semantic_space_id=semantic_space_id,
                job_index=job.job_index,
                stage_index=stage_idx,
                stage_payload_sha256=stage_sha,
            )
            node = ReplayNode(
                node_id=f"node_j{job.job_index:03d}_s{stage_idx:03d}",
                job_index=job.job_index,
                stage_index=stage_idx,
                generation_id=generation_id,
                semantic_space_id=semantic_space_id,
                parent_state_digest=running_parent_digest,
                stage_payload_sha256=stage_sha,
                post_state_digest=step_post_digest,
                commit_status="COMMITTED",
            )
            nodes.append(node)
            journal_lines.append(canonical_json_dumps(node.to_dict()))
            running_parent_digest = step_post_digest

    body: dict[str, Any] = {
        "schema_version": REPLAY_GRAPH_SCHEMA_VERSION,
        "workload_id": workload_spec.workload_id,
        "seed": workload_spec.seed,
        "generation_id": generation_id,
        "semantic_space_id": semantic_space_id,
        "job_count": workload_spec.job_count,
        "stages_per_job": workload_spec.stages_per_job,
        "initial_state_digest": initial_digest,
        "final_state_digest": running_parent_digest,
        "idempotent_replay_verified": idempotent_replay_verified,
        "duplicate_side_effects": duplicate_side_effects,
        "nodes": [n.to_dict() for n in nodes],
        "journal_lines": list(journal_lines),
    }
    graph_digest = compute_replay_graph_digest(body)
    return ReplayGraph(
        schema_version=REPLAY_GRAPH_SCHEMA_VERSION,
        workload_id=workload_spec.workload_id,
        seed=workload_spec.seed,
        generation_id=generation_id,
        semantic_space_id=semantic_space_id,
        job_count=workload_spec.job_count,
        stages_per_job=workload_spec.stages_per_job,
        initial_state_digest=initial_digest,
        final_state_digest=running_parent_digest,
        idempotent_replay_verified=idempotent_replay_verified,
        duplicate_side_effects=duplicate_side_effects,
        nodes=tuple(nodes),
        journal_lines=tuple(journal_lines),
        graph_digest=graph_digest,
    )


def verify_replay_journal_lines(
    lines: Sequence[str],
    *,
    expected_generation_id: str,
    expected_semantic_space_id: str,
    initial_state_digest: str | None = None,
) -> dict[str, Any]:
    if not isinstance(lines, Sequence) or len(lines) == 0:
        raise VipLabError(
            "REPLAY_JOURNAL_EMPTY",
            "Replay journal lines must be a non-empty sequence.",
        )

    parsed_nodes: list[dict[str, Any]] = []
    for idx, line in enumerate(lines):
        if not isinstance(line, str) or not line.strip():
            raise VipLabError(
                "REPLAY_JOURNAL_TRUNCATED_LINE",
                f"Journal line {idx} is empty or not a string.",
            )
        try:
            obj = parse_strict_json_text(line)
        except VipLabError as exc:
            raise VipLabError(
                "REPLAY_JOURNAL_TRUNCATED_LINE",
                f"Malformed or truncated JSONL at line {idx}: {exc.message}",
            ) from exc
        if not isinstance(obj, Mapping):
            raise VipLabError(
                "REPLAY_JOURNAL_TRUNCATED_LINE",
                f"Journal line {idx} must decode to a JSON object.",
            )
        parsed_nodes.append(dict(obj))

    running_parent = (
        initial_state_digest
        if initial_state_digest is not None
        else str(parsed_nodes[0].get("parent_state_digest", ""))
    )
    validate_hex_digest(running_parent, field_name="initial_state_digest")

    expected_job = 0
    expected_stage = 0

    for idx, node in enumerate(parsed_nodes):
        if node.get("generation_id") != expected_generation_id:
            raise VipLabError(
                "REPLAY_JOURNAL_GENERATION_MISMATCH",
                f"Journal line {idx} generation_id {node.get('generation_id')!r} != {expected_generation_id!r}.",
            )
        if node.get("semantic_space_id") != expected_semantic_space_id:
            raise VipLabError(
                "REPLAY_JOURNAL_SEMANTIC_SPACE_MISMATCH",
                f"Journal line {idx} semantic_space_id {node.get('semantic_space_id')!r} != {expected_semantic_space_id!r}.",
            )

        job_idx = node.get("job_index")
        stage_idx = node.get("stage_index")
        if idx == 0 and (job_idx != 0 or stage_idx != 0):
            raise VipLabError(
                "REPLAY_JOURNAL_STAGE_ORDER_INVALID",
                f"Replay journal must begin at job_index=0, stage_index=0; got ({job_idx}, {stage_idx}).",
            )
        if idx > 0:
            prev_job = parsed_nodes[idx - 1].get("job_index")
            prev_stage = parsed_nodes[idx - 1].get("stage_index")
            same_job_next_stage = job_idx == prev_job and stage_idx == prev_stage + 1
            next_job_first_stage = job_idx == prev_job + 1 and stage_idx == 0
            if not (same_job_next_stage or next_job_first_stage):
                raise VipLabError(
                    "REPLAY_JOURNAL_STAGE_ORDER_INVALID",
                    f"Out-of-order or missing ancestor stage at journal line {idx}: prev=({prev_job}, {prev_stage}), current=({job_idx}, {stage_idx}).",
                )

        parent_digest = str(node.get("parent_state_digest", ""))
        stage_sha = validate_hex_digest(
            str(node.get("stage_payload_sha256", "")),
            field_name="stage_payload_sha256",
        )
        post_digest = validate_hex_digest(
            str(node.get("post_state_digest", "")),
            field_name="post_state_digest",
        )
        if parent_digest != running_parent:
            raise VipLabError(
                "REPLAY_JOURNAL_STATE_DIGEST_MISMATCH",
                f"Journal line {idx} parent_state_digest {parent_digest!r} != expected {running_parent!r}.",
            )
        expected_post = _compute_step_state_digest(
            parent_state_digest=running_parent,
            generation_id=expected_generation_id,
            semantic_space_id=expected_semantic_space_id,
            job_index=int(job_idx),
            stage_index=int(stage_idx),
            stage_payload_sha256=stage_sha,
        )
        if post_digest != expected_post:
            raise VipLabError(
                "REPLAY_JOURNAL_STATE_DIGEST_MISMATCH",
                f"Journal line {idx} post_state_digest {post_digest!r} != computed {expected_post!r}.",
            )
        running_parent = post_digest
        expected_job = int(job_idx)
        expected_stage = int(stage_idx)

    return {
        "verified_line_count": len(parsed_nodes),
        "last_job_index": expected_job,
        "last_stage_index": expected_stage,
        "final_state_digest": running_parent,
    }


def verify_replay_graph(graph: ReplayGraph | Mapping[str, Any]) -> str:
    payload = graph.to_dict() if isinstance(graph, ReplayGraph) else dict(graph)
    if payload.get("schema_version") != REPLAY_GRAPH_SCHEMA_VERSION:
        raise VipLabError(
            "REPLAY_GRAPH_SCHEMA_MISMATCH",
            f"Expected schema_version {REPLAY_GRAPH_SCHEMA_VERSION!r}, got {payload.get('schema_version')!r}.",
        )
    if payload.get("idempotent_replay_verified") is not True:
        raise VipLabError(
            "REPLAY_GRAPH_IDEMPOTENCY_FAILED",
            "ReplayGraph must verify idempotent_replay_verified=True.",
        )
    if payload.get("duplicate_side_effects") != 0:
        raise VipLabError(
            "REPLAY_GRAPH_DUPLICATE_SIDE_EFFECTS",
            "ReplayGraph must have duplicate_side_effects == 0.",
        )

    journal_lines = payload.get("journal_lines")
    if not isinstance(journal_lines, list):
        raise VipLabError(
            "REPLAY_GRAPH_INVALID_JOURNAL",
            "journal_lines must be a list of JSON strings.",
        )
    journal_summary = verify_replay_journal_lines(
        journal_lines,
        expected_generation_id=str(payload.get("generation_id", "")),
        expected_semantic_space_id=str(payload.get("semantic_space_id", "")),
        initial_state_digest=str(payload.get("initial_state_digest", "")),
    )
    if journal_summary["final_state_digest"] != payload.get("final_state_digest"):
        raise VipLabError(
            "REPLAY_GRAPH_FINAL_DIGEST_MISMATCH",
            "ReplayGraph final_state_digest does not match verified journal tail.",
        )

    declared_digest = validate_hex_digest(
        str(payload.get("graph_digest", "")),
        field_name="graph_digest",
    )
    computed = compute_replay_graph_digest(payload)
    if declared_digest != computed:
        raise VipLabError(
            "REPLAY_GRAPH_DIGEST_MISMATCH",
            "ReplayGraph graph_digest does not match canonical payload.",
            details={"declared": declared_digest, "computed": computed},
        )
    return computed
