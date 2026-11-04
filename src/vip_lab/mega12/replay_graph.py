"""Deterministic stage-input/stage-output ReplayGraph and JSONL journal verifier for MEGA-12."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

from gate2.recovery import (
    RecoveryBinding,
    RecoveryHarness,
    RecoveryRefusal,
    SimulatedCrash,
)
from gate2.workload import SyntheticFixture, WorkloadSpec, generate
from vip_lab.common import (
    VipLabError,
    canonical_json_dumps,
    canonical_sha256,
    parse_strict_json_text,
    validate_hex_digest,
)

REPLAY_GRAPH_SCHEMA_VERSION = "vip-lab-replay-graph-v1"

DEFAULT_SYNTHETIC_F01_SHA = "1" * 40
DEFAULT_SYNTHETIC_C04_SHA = "2" * 40
DEFAULT_SYNTHETIC_E05_SHA = "3" * 40
DEFAULT_SYNTHETIC_CONFIG_DIGEST = "4" * 64
DEFAULT_PREV_MANIFEST_DIGEST = "5" * 64
DEFAULT_CURR_MANIFEST_DIGEST = "6" * 64
DEFAULT_RECEIPT_IDENTITY = "e05-receipt-synth-mega12"


def coerce_canonical_workload_spec(
    spec_or_mapping: WorkloadSpec | Mapping[str, Any],
) -> tuple[WorkloadSpec, str | None]:
    """Coerce a canonical WorkloadSpec or mapping into (WorkloadSpec, optional_workload_id)."""
    if isinstance(spec_or_mapping, WorkloadSpec):
        return spec_or_mapping, None
    if not isinstance(spec_or_mapping, Mapping):
        raise VipLabError(
            "INVALID_WORKLOAD_SPEC",
            "workload_spec must be a gate2.workload.WorkloadSpec or mapping.",
        )
    jobs = int(spec_or_mapping.get("jobs", spec_or_mapping.get("job_count", 3)))
    stages = int(spec_or_mapping.get("stages", spec_or_mapping.get("stages_per_job", 2)))
    artifact_bytes = int(
        spec_or_mapping.get("artifact_bytes", spec_or_mapping.get("payload_bytes", 48))
    )
    cost_units = int(spec_or_mapping.get("cost_units", 10))
    fault_position = int(spec_or_mapping.get("fault_position", 0))
    seed = int(spec_or_mapping.get("seed", 20261104))
    f01_sha = str(spec_or_mapping.get("f01_sha", DEFAULT_SYNTHETIC_F01_SHA))
    c04_sha = str(spec_or_mapping.get("c04_sha", DEFAULT_SYNTHETIC_C04_SHA))
    e05_sha = str(spec_or_mapping.get("e05_sha", DEFAULT_SYNTHETIC_E05_SHA))
    config_digest = str(
        spec_or_mapping.get("config_digest", DEFAULT_SYNTHETIC_CONFIG_DIGEST)
    )
    concurrency = int(spec_or_mapping.get("concurrency", 1))
    repetitions = int(spec_or_mapping.get("repetitions", 2))
    raw_wl_id = spec_or_mapping.get("workload_id")
    workload_id = (
        str(raw_wl_id).strip()
        if isinstance(raw_wl_id, str) and str(raw_wl_id).strip()
        else None
    )
    return (
        WorkloadSpec(
            jobs=jobs,
            stages=stages,
            artifact_bytes=artifact_bytes,
            cost_units=cost_units,
            fault_position=fault_position,
            seed=seed,
            f01_sha=f01_sha,
            c04_sha=c04_sha,
            e05_sha=e05_sha,
            config_digest=config_digest,
            concurrency=concurrency,
            repetitions=repetitions,
        ),
        workload_id,
    )


def build_canonical_recovery_binding(
    *,
    fixture: SyntheticFixture,
    generation_id: str,
    semantic_space_id: str,
    previous_manifest_digest: str = DEFAULT_PREV_MANIFEST_DIGEST,
    current_manifest_digest: str = DEFAULT_CURR_MANIFEST_DIGEST,
    receipt_identity: str = DEFAULT_RECEIPT_IDENTITY,
) -> RecoveryBinding:
    """Construct the canonical 10-field gate2.recovery.RecoveryBinding."""
    spec = fixture.spec
    return RecoveryBinding(
        f01_sha=spec.f01_sha,
        c04_sha=spec.c04_sha,
        e05_sha=spec.e05_sha,
        workload_digest=fixture.fixture_digest,
        configuration_digest=spec.config_digest,
        previous_manifest_digest=previous_manifest_digest,
        current_manifest_digest=current_manifest_digest,
        generation_id=generation_id,
        semantic_space_id=semantic_space_id,
        receipt_identity=receipt_identity,
    )


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


class SyntheticReplayHarnessAdapter:
    """In-memory adapter implementing the canonical gate2.recovery.RecoveryHarness protocol."""

    def __init__(
        self,
        *,
        fixture: SyntheticFixture,
        generation_id: str,
        semantic_space_id: str,
        valid_receipt_identity: str = DEFAULT_RECEIPT_IDENTITY,
        stage_payload_overrides: Mapping[tuple[int, int], bytes] | None = None,
        truncated_stage_list_for_job: int | None = None,
    ) -> None:
        self.fixture = fixture
        self.generation_id = generation_id
        self.semantic_space_id = semantic_space_id
        self.valid_receipt_identity = valid_receipt_identity
        self.stage_payload_overrides = dict(stage_payload_overrides or {})
        self.truncated_stage_list_for_job = truncated_stage_list_for_job

        self.initial_state_digest = canonical_sha256(
            {
                "kind": "vip_lab.mega12.initial_state",
                "workload_digest": fixture.fixture_digest,
                "generation_id": generation_id,
                "semantic_space_id": semantic_space_id,
            }
        )
        self._current_state_digest = self.initial_state_digest
        self.reconcile_calls = 0
        self.applied_ops: dict[str, str] = {}
        self.completed_ops: set[str] = set()
        self.duplicate_side_effects = 0

        self._op_index: dict[str, tuple[int, int, bytes, str]] = {}
        self._ordered_ops: list[str] = []
        for job in fixture.jobs:
            stages = (
                job.stages[:-1]
                if self.truncated_stage_list_for_job == job.job_index
                else job.stages
            )
            for stg in stages:
                op_id = f"job-{job.job_index:03d}-stage-{stg.stage_index:03d}"
                payload = self.stage_payload_overrides.get(
                    (job.job_index, stg.stage_index),
                    stg.artifact,
                )
                self._op_index[op_id] = (
                    job.job_index,
                    stg.stage_index,
                    payload,
                    stg.artifact_digest,
                )
                self._ordered_ops.append(op_id)

    def validate_receipt(self, receipt_identity: str) -> bool:
        return receipt_identity == self.valid_receipt_identity

    def reconcile_sqlite_tail(self) -> None:
        self.reconcile_calls += 1

    def state_digest(self) -> str:
        return self._current_state_digest

    def start_or_resume(self, binding: RecoveryBinding) -> Sequence[str]:
        if binding.generation_id != self.generation_id:
            raise RecoveryRefusal(
                f"GENERATION_MISMATCH: {binding.generation_id!r} != {self.generation_id!r}"
            )
        if binding.semantic_space_id != self.semantic_space_id:
            raise RecoveryRefusal(
                f"SEMANTIC_SPACE_MISMATCH: {binding.semantic_space_id!r} != {self.semantic_space_id!r}"
            )
        expected_total = self.fixture.spec.jobs * self.fixture.spec.stages
        if len(self._ordered_ops) != expected_total:
            raise RecoveryRefusal(
                f"PARTIAL_INDEX: expected {expected_total} stage operations, got {len(self._ordered_ops)}"
            )
        return tuple(self._ordered_ops)

    def is_complete(self, operation_id: str) -> bool:
        return operation_id in self.completed_ops

    def apply_idempotent(self, operation_id: str) -> None:
        if operation_id in self.applied_ops:
            # Already applied prior to crash/resume: idempotent no-op
            return
        job_idx, stage_idx, payload, expected_sha = self._op_index[operation_id]
        expected_len = self.fixture.spec.artifact_bytes
        if len(payload) == expected_len - 1:
            raise RecoveryRefusal(
                f"PARTIAL_RECORD: stage ({job_idx}, {stage_idx}) missing trailing byte"
            )
        if len(payload) < expected_len:
            raise RecoveryRefusal(
                f"TRUNCATED_PAYLOAD: stage ({job_idx}, {stage_idx}) length {len(payload)} < {expected_len}"
            )
        actual_sha = hashlib.sha256(payload).hexdigest()
        if actual_sha != expected_sha:
            raise RecoveryRefusal(
                f"DIGEST_MISMATCH: stage ({job_idx}, {stage_idx}) sha256 {actual_sha} != {expected_sha}"
            )
        next_digest = _compute_step_state_digest(
            parent_state_digest=self._current_state_digest,
            generation_id=self.generation_id,
            semantic_space_id=self.semantic_space_id,
            job_index=job_idx,
            stage_index=stage_idx,
            stage_payload_sha256=actual_sha,
        )
        self.applied_ops[operation_id] = next_digest
        self._current_state_digest = next_digest

    def mark_complete(self, operation_id: str) -> None:
        if operation_id in self.completed_ops:
            self.duplicate_side_effects += 1
            return
        self.completed_ops.add(operation_id)


def build_replay_graph_from_workload(
    *,
    workload_spec: WorkloadSpec,
    generation_id: str = "gen-synth-001",
    semantic_space_id: str = "siglip-v1-base:768:v1",
    workload_id: str | None = None,
) -> ReplayGraph:
    if not isinstance(workload_spec, WorkloadSpec):
        raise VipLabError(
            "INVALID_WORKLOAD_SPEC",
            "workload_spec must be a gate2.workload.WorkloadSpec instance.",
        )
    fixture = generate(workload_spec)
    resolved_workload_id = (
        workload_id.strip()
        if isinstance(workload_id, str) and workload_id.strip()
        else f"wl-{fixture.fixture_digest[:16]}"
    )
    binding = build_canonical_recovery_binding(
        fixture=fixture,
        generation_id=generation_id,
        semantic_space_id=semantic_space_id,
    )
    adapter = SyntheticReplayHarnessAdapter(
        fixture=fixture,
        generation_id=generation_id,
        semantic_space_id=semantic_space_id,
    )
    initial_digest = adapter.initial_state_digest

    with tempfile.TemporaryDirectory() as tmp_dir:
        ckpt_path = Path(tmp_dir) / "recovery_checkpoint.json"
        # 1. Simulate crash after first stage side effect before completion
        harness_crash = RecoveryHarness.open(ckpt_path, binding, adapter)
        try:
            harness_crash.run(crash_point="after_side_effect_before_completion")
        except SimulatedCrash:
            pass
        # 2. Resume and complete all remaining operations
        harness_commit = RecoveryHarness.open(ckpt_path, binding, adapter)
        committed_out = harness_commit.run(crash_point=None)
        # 3. Re-run against completed checkpoint to verify idempotent replay
        harness_replay = RecoveryHarness.open(ckpt_path, binding, adapter)
        replay_out = harness_replay.run(crash_point=None)

    duplicate_side_effects = adapter.duplicate_side_effects
    idempotent_replay_verified = (
        duplicate_side_effects == 0
        and committed_out.get("post_state_digest") == replay_out.get("post_state_digest")
        and committed_out.get("post_state_digest") == adapter.state_digest()
        and len(adapter.completed_ops) == workload_spec.jobs * workload_spec.stages
    )

    nodes: list[ReplayNode] = []
    journal_lines: list[str] = []
    running_parent_digest = initial_digest

    for job in fixture.jobs:
        for stage in job.stages:
            stage_sha = stage.artifact_digest
            step_post_digest = _compute_step_state_digest(
                parent_state_digest=running_parent_digest,
                generation_id=generation_id,
                semantic_space_id=semantic_space_id,
                job_index=job.job_index,
                stage_index=stage.stage_index,
                stage_payload_sha256=stage_sha,
            )
            node = ReplayNode(
                node_id=f"node_j{job.job_index:03d}_s{stage.stage_index:03d}",
                job_index=job.job_index,
                stage_index=stage.stage_index,
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
        "workload_id": resolved_workload_id,
        "seed": workload_spec.seed,
        "generation_id": generation_id,
        "semantic_space_id": semantic_space_id,
        "job_count": workload_spec.jobs,
        "stages_per_job": workload_spec.stages,
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
        workload_id=resolved_workload_id,
        seed=workload_spec.seed,
        generation_id=generation_id,
        semantic_space_id=semantic_space_id,
        job_count=workload_spec.jobs,
        stages_per_job=workload_spec.stages,
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
