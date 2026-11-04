"""MEGA-12: Generated-Only Recovery & Replay Consistency (+ Stretch S3)."""

from vip_lab.mega12.consistency_review import (
    REQUIRED_NOT_OBSERVED_METRICS,
    STAGE_ID,
    build_synthetic_recovery_measurement_set,
    inspect_recovery_replay_consistency,
)
from vip_lab.mega12.fault_scenarios import evaluate_fault_scenario_matrix
from vip_lab.mega12.replay_graph import (
    REPLAY_GRAPH_SCHEMA_VERSION,
    ReplayGraph,
    ReplayNode,
    SyntheticReplayHarnessAdapter,
    build_canonical_recovery_binding,
    build_replay_graph_from_workload,
    coerce_canonical_workload_spec,
    compute_replay_graph_digest,
    verify_replay_graph,
    verify_replay_journal_lines,
)

__all__ = [
    "REPLAY_GRAPH_SCHEMA_VERSION",
    "REQUIRED_NOT_OBSERVED_METRICS",
    "STAGE_ID",
    "ReplayGraph",
    "ReplayNode",
    "SyntheticReplayHarnessAdapter",
    "build_canonical_recovery_binding",
    "build_replay_graph_from_workload",
    "build_synthetic_recovery_measurement_set",
    "coerce_canonical_workload_spec",
    "compute_replay_graph_digest",
    "evaluate_fault_scenario_matrix",
    "inspect_recovery_replay_consistency",
    "verify_replay_graph",
    "verify_replay_journal_lines",
]
