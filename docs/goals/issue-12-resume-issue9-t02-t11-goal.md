# Goal Template — Resume Issue #9 at T02 and Complete Gate-0 T02–T11

Use Luna Medium.

Work in `/Users/yusuf/Repos/video-intelligence-pipeline` and execute GitHub Issue #12 as the governing continuation of Issue #9.

Read first:
- `AGENTS.md`
- `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`
- `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`
- `docs/implementation-spec-v1.1.md`
- `docs/implementation-spec-v1.1.1-erratum.md`
- `docs/plans/2026-09-12-gate0-implementation.md`
- `docs/agent-runs/run-20260912-issue11/ledger.md`
- Issue #9 and Issue #11 closeout evidence.

The exact repository-local Gate-0 environment already exists at `.venv-gate0/` and must be reused offline. No new package installation or network access is authorized. Preserve Python 3.11.9 and pytest 8.3.3 exact-lock conformance.

T00 and T01 are accepted and canonical. Do not reopen or redo them unless a downstream regression proves a concrete dependency defect.

Resume implementation at T02 and continue through T11 under the original user-approved local/synthetic boundary only.

Use native `collaboration.spawn_agent`, verified effective `gpt-5.6-luna` / medium, isolated branches/worktrees, durable lane memos, compact handoffs, main-agent-only canonical integration, strict TDD, systematic debugging, and parallel-first dependency waves.

Recover the exact T02–T11 DAG and write ownership from the canonical plan. At each wave, spawn every ready non-conflicting implementation lane concurrently from one frozen SHA. Do not serialize independent tasks.

For every behavior-changing task require observed RED → minimal GREEN → REFACTOR/regression with the exact locked pytest environment. Do not substitute manual checks for required pytest evidence.

Run fresh review lanes for all integrated tasks in a wave concurrently, union justified findings once, remediate in bounded batches, and continue immediately to the next ready wave. Do not use unbounded reviewer→patch loops.

Still forbidden:
- real archive/media execution;
- model download or provider/cloud calls;
- external network egress;
- Google Drive/archive-scale materialization;
- Gate 1–3;
- editor/render/UI/archive-scale features;
- changing exact runtime/dependency pins without separate approval.

Use synthetic/fake seams for model/provider boundaries; keep unavailable real-model feasibility/inference `NOT_OBSERVED`.

After T02–T11 are integrated and the complete synthetic suite is green, freeze one SHA and run at least three fresh whole-branch Luna Medium certifiers concurrently covering: (1) spec/erratum/plan/interface/13-artifact compliance; (2) TDD/test quality + temporal/VFR/determinism/repeatability/CLI/verifier; (3) policy/security/no-egress/provenance/retention/rollback/source preservation/scope. Union blockers once and allow at most one bounded remediation + recertification generation.

Before completion require full synthetic acceptance, exactly 13 result artifacts, no forbidden side effects, Gate-0 verifier green, `git diff --check`, secret audit, `bash scripts/verify-workspace.sh`, safe non-force push, `bash scripts/verify-workspace.sh --require-pushed`, and local `main == origin/main`. Update `docs/gate0/implementation-receipt.md` with actual evidence and preserve `NOT_OBSERVED` runtime facts.

Finish only with:

`GATE0_T00_T11_SYNTHETIC_IMPLEMENTATION_COMPLETE`

or

`GATE0_T00_T11_SYNTHETIC_IMPLEMENTATION_NEEDS_WORK`

and exactly one sync state:

`SYNCED`

or `SYNC_BLOCKED_<reason>`.
