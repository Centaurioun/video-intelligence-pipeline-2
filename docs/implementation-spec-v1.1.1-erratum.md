# Gate-0 Implementation Specification v1.1.1 Erratum

**Status:** NORMATIVE OVERLAY — READY FOR EXPLICIT USER EXECUTION APPROVAL

**Scope:** This overlay changes only the Gate-0 v1.1 discovery-authorization /
processing-policy boundary and directly dependent plan interfaces. It does not
authorize production code, tests, fixtures, schemas, real-media execution,
model downloads, provider requests, cloud egress, or later gates.

## Authority and serialization

This overlay is read together with `docs/implementation-spec-v1.1.md`. Where
the two differ, this v1.1.1 overlay controls only the clauses below. The
13-file inventory, status namespaces, evidence classes, source-preservation
rules, and all unrelated Gate-0 architecture remain unchanged.

`policy_decisions.jsonl` is the sole serialized owner of every `PolicyDecision`
record, including discovery-purpose decisions. A discovery authorization row
in `discovery_authorizations.jsonl` contains only the required scalar
`policy_decision_id` reference; it MUST NOT embed, copy, or serialize a second
`PolicyDecision` object. `schemas/gate0/policy_decisions.json` is the sole
schema authority for the decision record. The discovery-authorization schema
owns only `DiscoveryAuthorizationRecord` and its reference field.

The T02 inventory stage creates the discovery-purpose decision record in its
single `policy_decisions.jsonl` owner before publishing either discovery-scope
artifact. T02 then writes the authorization row with the decision ID. T04
consumes that ID as a reference and may publish an effective processing
decision only as a distinct policy record with a distinct ID and purpose; it
never copies or reserializes the discovery decision.

## Cardinality, scope, and foreign keys

For one T02 inventory attempt, there is exactly one discovery `PolicyDecision`
record for the complete ordered set of included and excluded source revisions
observed by that attempt. Its `revision_scope` is the complete ordered tuple
of all revision IDs in `source_manifest.json`, including revisions excluded
after probe; an empty inventory is invalid protocol. Every discovery
authorization row references that same ID. Both T02 discovery artifact
envelopes (`source_manifest.json` and `discovery_authorizations.jsonl`) carry
that same `policy_decision_id`. Thus multi-revision inventories use one
decision-to-many-records relationship, never one decision per row and never a
set-valued envelope field.

Before atomic publication, T01/T02 validate that the decision ID exists in the
same candidate `policy_decisions.jsonl` payload, has `purpose=DISCOVER`,
`decision=ALLOW`, an exact revision scope equal to the source-manifest
revision tuple, and `allowed_artifact_types` exactly
`("source_manifest", "discovery_authorization")`. Every authorization row
must reference the same ID; missing, unknown, duplicated, out-of-scope,
expired, revoked, or differently scoped references fail closed and publish no
discovery artifact. The validator performs this cross-file FK check before
publication, not as a later repair.

## Purpose and use separation

`PolicyUseContext` has the required closed field
`purpose: Literal["DISCOVER", "HASH", "PROBE", "PROCESS", "CACHE_READ", "PROJECTION_READ"]`.
T02 treats HASH and PROBE as discovery suboperations. The exact mapping is:
`DISCOVER→DISCOVER`, `HASH→DISCOVER`, `PROBE→DISCOVER`, `PROCESS→PROCESS`,
`CACHE_READ→CACHE_READ`, and `PROJECTION_READ→PROJECTION_READ`.
`require_allow` requires the decision purpose to equal both context fields and
rejects any discovery decision for PROCESS, CACHE_READ, or PROJECTION_READ.
Discovery permission never satisfies processing, cache-read, or projection-read
authorization.

## Required oracles

The T01/T02/T04 goldens include: one decision covering one revision; one
decision covering multiple revisions; a per-row decision set; a missing or
unknown FK; a scope mismatch; a duplicated embedded decision; an expired or
revoked discovery decision; a processing-purpose decision used for discovery;
and a discovery decision presented to each of PROCESS, CACHE_READ, and
PROJECTION_READ. Only the first two valid cardinality cases pass.

## Exact CLI contracts

T08 evaluation is invoked as:

```text
python -m gate0.cli evaluate --run <run-dir> --config config/gate0/default.json --input-root <input-root> --output-root <output-root> --run-id <id> --review-input <path>
```

`--review-input` is required exactly once, must be an existing regular local
file beneath `config/gate0/default.json.review_input.authorized_root`, and is
the only reviewer-input path. Structural, missing, repeated,
normalized-outside-root, unreadable, wrong-digest, or extra reviewer-input
options are exit 30; after the path is structurally valid, a policy denial is
exit 20. The authorized root is copied into and digest-bound by the run
manifest before evaluation. The file is never accepted from a run-output
directory or gold/label path. The same form is used by the T08 plan row and
verifier.

Repeat is invoked as:

```text
python -m gate0.cli repeat --run <reported-run-dir> --config config/gate0/default.json --input-root <input-root> --output-root <output-root> --run-id <id> --mode frozen-index|full-pipeline --predecessor-run-id <id> --frozen-input-digest <64-hex-digest>
```

`--mode`, `--predecessor-run-id`, and `--frozen-input-digest` are required
exactly once; `--review-input`, stage-selection, label, gold, or output-file
options are forbidden. The predecessor must resolve to the reported run named
by `--run`, and its canonical frozen input digest must equal the supplied
digest. `run_dir` must equal `output_root/run_id`, be an existing reported run,
and be read-only except for append-only repeat attempt/comparison records.
Missing/extra/malformed options are exit 40; illegal predecessor, mode, run
directory, or digest binding is exit 20; a valid same-terminal digest returns
the prior comparison without a duplicate attempt. Full-pipeline recomputation
does not permit new inputs or artifacts.

## Gate-decision ownership

T08 owns evaluation and `metrics.json`; the `report` substage is the sole
publisher of `gate_decision.md` and is not a new architecture stage. The gate
decision authority is the named Gate-0 study owner recorded in the run
manifest. The authority is `config/gate0/default.json.policy.gate_owner_id`;
the exact same `gate_owner_id` is copied into `run_manifest.json` and T08
report validates equality before publication. Its required inputs are the T08
`metrics.json` digest, run-manifest
validity/status projection, two-reviewer judgment digest, policy/preflight
status, and repeat comparison status. The report publisher may only emit the
four declared decision values and must preserve the v1.1 precedence and
thresholds. No reviewer, ranker, policy stage, or repeat command may publish
or mutate `gate_decision.md`.
