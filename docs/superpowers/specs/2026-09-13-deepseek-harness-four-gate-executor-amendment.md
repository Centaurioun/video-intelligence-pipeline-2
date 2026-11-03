# DeepSeek Harness Four-Gate Executor Amendment

**Date:** 2026-09-13  
**Status:** USER-APPROVED EXECUTOR AMENDMENT  
**Scope:** orchestration/executor layer only; scientific Gate contracts and evidence semantics are unchanged.

## 1. Decision

The four-Gate portfolio remains one repository, one admin/canonical worktree, and four isolated Gate worktrees/controller branches. The portfolio is now explicitly **executor-agnostic** at the governance layer.

Preferred active Gate executor/controller: **DeepSeek Harness**.

Codex remains permitted for admin synchronization, repository maintenance, bounded fallback/recovery, and separately authorized verification, but Codex and DeepSeek Harness must never act as simultaneous writers on the same Gate controller branch/worktree.

## 2. Stable topology

- `/Users/yusuf/Repos/video-intelligence-pipeline` — admin/canonical/reconciliation only.
- `/Users/yusuf/Repos/video-intelligence-pipeline-gate0` — Gate 0.
- `/Users/yusuf/Repos/video-intelligence-pipeline-gate1` — Gate 1.
- `/Users/yusuf/Repos/video-intelligence-pipeline-gate2` — Gate 2.
- `/Users/yusuf/Repos/video-intelligence-pipeline-gate3` — Gate 3.

The existing controller branches remain authoritative. No re-clone or new permanent worktree is required for the executor transition.

## 3. DeepSeek Harness capability profile

Before a Gate session uses autonomous goal continuation, the controller must verify the required Harness capabilities rather than assuming them:

1. one durable Goal for the root Gate session;
2. automatic goal-round continuation when enabled by the Harness composition;
3. at least one subagent provider plus a model-facing delegation tool;
4. the ability to launch separate-context children for bounded work;
5. repository/shell/file access sufficient for the Gate worktree.

Official Harness references current at this amendment:

- https://github.com/deepseek-ai/deepseek-harness
- https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/goal/README.md
- https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/subagent/subagent/README.md

A Goal records the durable completion objective; it is not itself a scheduler. Automatic continuation requires the goal-round driver or equivalent enabled capability. Subagent delegation is optional/configurable in Harness and must be positively observed before relying on it.

If required capabilities are unavailable, the controller must return a specific capability blocker rather than pretending that goal/subagent behavior occurred.

## 4. Goal semantics

The durable Goal for each Gate is NOT “finish the Gate at any cost.” It is:

> Advance this Gate to the highest scientifically defensible, currently authorized, dependency-safe maturity state permitted by verified repository authority; continuously execute genuine READY work; stop cleanly when the current frontier is exhausted or remaining work is dependency-, authorization-, architecture-, or technical-gated.

Permitted terminal/frontier states:

- `GOAL_COMPLETE_CURRENT_FRONTIER`
- `GOAL_PARKED_UPSTREAM_DEPENDENCY`
- `GOAL_BLOCKED_AUTHORIZATION`
- `GOAL_BLOCKED_TECHNICAL`
- `GOAL_NEEDS_ARCHITECTURE_REVIEW`

A parked/blocked Goal is not a failed Gate and must not manufacture speculative work merely to remain active. When new upstream evidence or authority arrives, the same Gate may be resumed from durable repository state.

## 5. Parent-controller role

The root Harness agent is primarily a controller, scheduler, integrator, and verifier. It should keep its working context small even when the underlying model offers a large context window.

The parent should not perform substantial bounded work itself when that work can be safely delegated to a self-contained child. It should:

1. fetch and verify current repository authority;
2. build the current READY/dependency frontier;
3. allocate exclusive ownership;
4. dispatch independent bounded work to subagents;
5. collect and independently check child results;
6. integrate only accepted work;
7. update durable Gate-local ledgers/state;
8. refill the frontier continuously;
9. terminate completed children and stop when no authorized READY work remains.

Repository state, exact SHAs, receipts, ledgers, and handoffs remain durable memory. A large model context window is convenience, not project authority.

## 6. Subagent policy

Use subagents aggressively for genuinely independent work, not for agent-count optics.

Appropriate children include independent research, bounded implementation lanes, focused tests, audit/review, verification, and contract-reading tasks.

Each child prompt must be self-contained because Harness children do not implicitly share the parent conversation. Bind child work to exact authority/dependency SHAs and explicit file/ownership scope.

One-shot children are preferred for bounded tasks. Continuable children are reserved for tasks that genuinely need ordered follow-up turns.

### Writer isolation

Separate context does not imply separate filesystem isolation.

- Read-only/research/review children may share a Gate worktree.
- Writer children must have exclusive file ownership OR an isolated temporary child branch/worktree.
- Two children must never write the same path concurrently.
- The root Gate controller owns integration into the Gate controller branch.
- Temporary child worktrees are not permanent portfolio topology and must be safely removed after durable integration/verification.

## 7. Portfolio concurrency remains authoritative

Changing executor does not widen resource authority.

Initial portfolio-v1 limits remain:

- four logical Gate controllers;
- at most two simultaneous candidate-writer Gate controllers;
- at most one heavy local model/FFmpeg/runtime execution lease without new accepted measurement;
- one canonical integration lane;
- serialized Git worktree administration;
- immutable first-epoch shared-contract bindings;
- exact SHA cross-Gate dependencies.

Reasoning/research subagents may scale adaptively where work is truly independent and resource-light. Heavy local execution does not inherit the larger logical subagent count.

## 8. Executor exclusivity

For each Gate at any moment there is one active writer controller identity.

Preferred state:

`ACTIVE_GATE_EXECUTOR = DEEPSEEK_HARNESS`

Codex may inspect/read or perform separately authorized admin synchronization, but before Codex writes a Gate branch it must prove DeepSeek Harness is inactive for that branch or receive explicit handoff authority.

The inverse applies when returning control to Harness.

## 9. Gate-specific Goal boundaries

### Gate 0 — Diagnostic Retrieval

Advance only Gate 0. Current immediate frontier remains the Stage-B architecture/evidence-semantics review. Do not silently weaken security evidence, run protected/scored retrieval, activate Issue #17, or perform unauthorized provider transport.

### Gate 1 — Representation / Capability Benchmark

Advance reversible contracts/scaffolding/benchmark preparation to the highest dependency-safe maturity. Do not select a model/provider winner without measured benchmark evidence and required authority.

### Gate 2 — Reliability / Scale

Advance measurement, failure-injection, recovery/idempotency and reversible reliability preparation. Do not adopt Redis/Kafka/vector-service/durable-scheduler infrastructure without measured deficit evidence.

### Gate 3 — Editing / QC

Advance synthetic source-native temporal refinement, edit-plan/render/QC preparation where dependency-safe. Never treat semantic timestamps as exact edit boundaries; protected-media editing/export remains separately gated.

## 10. Authority and evidence invariants

This amendment does not alter:

- Gate definitions;
- evidence classes;
- source-media immutability;
- PTS/timebase requirements;
- protected-media authorization boundaries;
- Gate promotion rules;
- shared-contract ownership;
- preservation refs;
- canonical integration rules.

Harness model/provider choice cannot upgrade evidence strength or widen authorization.

## 11. Activation

Activation is two-step:

1. one bounded admin Codex synchronization task fast-forwards/fetches the admin and Gate worktrees to the newly amended remote state without starting Gate implementation;
2. four fresh ChatGPT Gate coordinators generate Gate-local DeepSeek Harness Goal/controller prompts and coordinate subsequent terminal reports.

No existing Gate history is restarted. No new permanent worktrees are created.
