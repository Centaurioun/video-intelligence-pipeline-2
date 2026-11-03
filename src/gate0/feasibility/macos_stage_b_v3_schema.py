"""Closed v3 vocabulary and dispatch policy for the Gate-0 Stage-B envelope.

This module is the single declarative source of the v3 discriminators, the closed
execution-mode and asserted-stage vocabularies, the required-field closures for
the v3 worker/receipt surfaces, and the governed/verifier module namespaces used
by the execution-source identity.

It carries **no** evaluator behaviour: version-local evaluation stays frozen in
``macos_stage_b_contract`` / ``macos_stage_b_verdict``, and current certification
eligibility is decided only by the v3 dispatcher and the v3 predicate surface.
Every value here is a constant so a producer can never flip a version at run
time.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Version dispatch vocabulary (plan Task 1, Task 6).
# ---------------------------------------------------------------------------
CURRENT_CERTIFICATION_VERSION = "stage-b-app-sandbox.v3"
HISTORICAL_V1_NON_PROMOTING = "HISTORICAL_V1_NON_PROMOTING"
HISTORICAL_V2_NON_PROMOTING = "HISTORICAL_V2_NON_PROMOTING"
INVALID_VERSION = "INVALID_VERSION"

# §27 Mode A.  A closed vocabulary: an unknown mode is never defaulted.
EXECUTION_MODES = frozenset({"STAGE_A_AND_STAGE_B", "STAGE_B_NETWORK_EVIDENCE_ONLY"})

# The stage a producer asserts for the dedicated hostname/resolver-shaped probe.
ASSERTED_STAGE_VOCABULARY = frozenset({"RESOLVER_SUPPORT", "TRANSPORT", "NOT_OBSERVED"})

# ---------------------------------------------------------------------------
# Run-configuration key closure (plan Task 3 parity test).
# ---------------------------------------------------------------------------
COMMON_REQUIRED_CONFIG_KEYS = frozenset({
    "run_id", "repo_root", "python_executable", "output_root", "deny_root",
    "worker_receipt", "runner_attestation", "loopback_port", "proxy_port",
    "execution_mode", "asserted_stage"})
STAGE_A_ONLY_CONFIG_KEYS = frozenset({
    "model_root", "synthetic_root", "synthetic_media", "ffmpeg_path",
    "ffprobe_path", "expected_weights_sha256"})

# §37 Stage-A provenance.  When Stage-A was NOT performed, the worker's
# ``stage_a`` block may carry provenance only -- never an observation.
STAGE_A_ALLOWED_WHEN_NOT_PERFORMED = frozenset({
    "execution_state", "current_run_observation", "historical_certified_candidate_sha"})

# ---------------------------------------------------------------------------
# v3 required-field closures (plan Task 1, Task 2).
# ---------------------------------------------------------------------------
# NOTE: ``lifecycle`` is deliberately absent -- it is an OUTER (receipt-level)
# object assembled by the verifier side, never a worker-level object.
V3_WORKER_REQUIRED_FIELDS = frozenset({
    "schema_version", "run_id", "status", "execution_mode", "asserted_stage",
    "immutable_identity_before", "immutable_identity_after", "child_inheritance",
    "network", "environment", "filesystem", "execution_source_identity_before",
    "execution_source_identity_after", "stage_a"})

V3_ENTITLEMENT_FIELDS = frozenset({
    "app_sandbox", "network_client", "network_server", "inherit",
    "inventory_complete", "temporary_exceptions"})

V3_ENVIRONMENT_FIELDS = frozenset({
    "observation_schema", "observed_at", "measurement_source", "allowlist_id",
    "prohibited_rule_set_id", "key_count", "keys", "values", "identity_value_digest",
    "prohibited_variables_observed", "scan_scope_keys", "run_id_observed", "pythonpath_entries"})

V3_FILESYSTEM_OPERATION_FIELDS = frozenset({
    "operation_id", "operation", "process_identity", "os_permission_denied",
    "errno", "returncode", "raw_evidence_ref", "raw_evidence_digest"})

C16_DENY_OPERATION = "deny_root_read"

# The eight-key prohibited-action tuple.  Byte-identical to the historical
# eight-key ``PROHIBITED`` tuple: v3 adds closure semantics, never a ninth key.
V3_PROHIBITED_ACTIONS = (
    "protected_media", "provider_cloud", "mps_cuda", "issue17",
    "gate_promotion", "model_mutation", "network_extension", "system_filtering")

# The four keys with NO runtime observable: they are closed by resolving a
# digest-verified authorization reference, never by observing a run.
V3_AUTHORIZATION_CLOSED_ACTIONS = ("issue17", "gate_promotion",
                                   "network_extension", "system_filtering")

# Protected/archive path prefixes.  Used ONLY for configuration path-set
# closure over declared paths: the closure opens nothing.
PROTECTED_PATH_PREFIXES = ("/Volumes/", "/protected/", "/archive/")

# Outer lifecycle surface (plan Task 9).
V3_LIFECYCLE_FIELDS = frozenset({
    "exit_status", "termination_reason", "post_cleanup_alive", "child_pid",
    "orphaned_child_pids", "census_method", "attestation_ref", "attestation_digest"})

# ---------------------------------------------------------------------------
# C4 primitives (plan Task 1 / R4-2).
#
# ``probe_execution_id`` is a STRING; the three PIDs are positive ints.  The
# producer never authors C4 ``observed``/``boundary``/``evidence``: those are
# verifier-derived.
# ---------------------------------------------------------------------------
V3_C4_PRIMITIVE_FIELDS = ("worker_pid", "probe_parent_pid", "probe_child_pid", "probe_execution_id")
C4_PID_FIELDS = ("worker_pid", "probe_parent_pid", "probe_child_pid")

# Plan Task 3: the sole census method string, produced by the Python worker and
# ingested (never re-derived) by the signed Swift runner.
CENSUS_METHOD = "WORKER_FINAL_DESCENDANT_CENSUS_PLUS_POST_CLEANUP_LIVENESS"

# ---------------------------------------------------------------------------
# Governed module namespaces (plan Task 4 / §30).
# ---------------------------------------------------------------------------
GOVERNED_MODULE_NAMESPACE = "gate0."

SANDBOX_KNOWN_MODULES = frozenset({
    "gate0.feasibility", "gate0.feasibility.macos_stage_b_worker",
    "gate0.feasibility.macos_stage_b_network",
    "gate0.feasibility.macos_stage_b_probe_entrypoint",
    "gate0.feasibility.macos_stage_b_receipt", "gate0.feasibility.macos_stage_b_contract",
    "gate0.feasibility.macos_stage_b_source_identity",
    # S2: the closed v3 vocabulary/dispatch module is a governed sandbox module.
    "gate0.feasibility.macos_stage_b_v3_schema",
    "gate0.identity", "gate0.canonical_json", "gate0.contracts", "gate0.contracts.types"})

# Stage-A-only modules.  A network-only execution must never load one of these.
SANDBOX_STAGE_A_MODULES = frozenset({
    "gate0.feasibility.macos_stage_a", "gate0.adapters", "gate0.adapters.decoder",
    "gate0.adapters.embedding", "gate0.adapters.ffmpeg_native", "gate0.adapters.siglip_local",
    "gate0.inventory", "gate0.policy"})

VERIFIER_KNOWN_MODULES = frozenset({
    "gate0.feasibility", "gate0.feasibility.macos_stage_b_verdict",
    "gate0.feasibility.macos_stage_b_v3_predicates",
    "gate0.feasibility.macos_stage_b_os_evidence",
    "gate0.feasibility.macos_stage_b_target_safety",
    "gate0.feasibility.macos_stage_b_contract", "gate0.identity", "gate0.canonical_json",
    "gate0.inventory", "gate0.policy", "gate0.contracts", "gate0.contracts.types"})
