# DeepSeek Harness Four-Gate Activation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Synchronize the existing five-worktree local portfolio to the executor amendment and activate DeepSeek Harness as the preferred Gate controller without restarting Gate history or widening authority.

**Architecture:** Keep the existing admin + Gate0–3 linked-worktree topology and controller branches. One bounded admin Codex task synchronizes local refs/worktrees to the new remote authority; afterward each Gate receives its own fresh ChatGPT coordinator conversation, which creates a Gate-specific DeepSeek Harness durable Goal/controller prompt. DeepSeek Harness becomes the only active writer controller for that Gate while Codex remains admin/fallback.

**Tech Stack:** Git linked worktrees, GitHub repository authority, DeepSeek Harness durable Goal, goal-round continuation, Harness subagents, ChatGPT Gate coordinators.

**Spec:** `docs/superpowers/specs/2026-09-13-deepseek-harness-four-gate-executor-amendment.md`

## Global Constraints

- Preserve exactly five permanent worktrees: admin + Gate0–3.
- Do not clone new repositories or create new permanent Gate worktrees.
- One active writer controller per Gate branch.
- Preferred Gate executor is DeepSeek Harness; Codex is admin/sync/fallback only unless explicitly handed a Gate writer role.
- Scientific Gate definitions, evidence classes, shared-contract bindings, protected-media rules, and promotion authority are unchanged.
- Max simultaneous candidate-writer Gate controllers remains 2.
- Heavy local model/FFmpeg/runtime execution remains max 1 without new accepted measurement.
- No provider/cloud inference, protected-media work, Gate promotion, model mutation/download, destructive cleanup, force push, hard reset, `git clean`, or reflog destruction is authorized by this plan.

---

### Task 1: Admin/local synchronization

**Files:** no repository-content changes required by the executor; this task updates local Git refs/worktree checkouts only.

**Produces:** all five local worktrees synchronized to remote authority without starting substantive Gate work.

- [ ] From `/Users/yusuf/Repos/video-intelligence-pipeline`, fetch `origin` non-destructively and record `origin/main` plus all four `origin/controller/gateN/portfolio-v1` heads.
- [ ] Verify the permanent worktree inventory contains only the admin and Gate0–3 steady-state paths relevant to this portfolio.
- [ ] Verify each worktree is clean or contains only pre-existing explicitly preserved state; stop rather than overwrite unexpected local work.
- [ ] Fast-forward/update the admin worktree to current `origin/main` only when non-destructive and compatible with its preserved state.
- [ ] For each Gate worktree, fetch and fast-forward its existing controller branch to the current remote controller head; never rebase, reset, force-move, or recreate the branch.
- [ ] Verify `docs/superpowers/specs/2026-09-13-deepseek-harness-four-gate-executor-amendment.md`, `docs/portfolio/portfolio-v1/DEEPSEEK_HARNESS_CONTROLLER_PROFILE.md`, and `docs/portfolio/portfolio-v1/resource-policy-v2.yaml` are readable from canonical `origin/main`.
- [ ] Verify no Gate implementation was started and report the resulting five local branch/HEAD identities.

### Task 2: Gate-local executor-state reconciliation

**Files:**
- Modify on each controller branch: `docs/gates/gateN/COORDINATOR_STATE.md`

**Produces:** each Gate state declares the DeepSeek Harness preferred executor, current durable Goal semantics, and Codex fallback/non-co-writer rule.

- [ ] Gate 0 state must preserve `M3_SYNTHETIC_READY`, the accepted continuation base, and the architecture/evidence-semantics review as the immediate frontier.
- [ ] Gate 1 state must preserve `M1_CONTRACTED`, no winner outcome, and reversible benchmark preparation only.
- [ ] Gate 2 state must preserve `M1_CONTRACTED`, no measured scale deficit, and reject speculative infrastructure.
- [ ] Gate 3 state must preserve `M1_CONTRACTED`, synthetic preparation only, and protected-media editing/export prohibition.
- [ ] Every Gate state must reference the canonical DeepSeek Harness controller profile and resource-policy-v2, state `PREFERRED_ACTIVE_EXECUTOR = DEEPSEEK_HARNESS`, and prohibit simultaneous Codex/Harness writer control.
- [ ] Push each controller branch normally and verify remote equality.

### Task 3: Four fresh ChatGPT Gate coordinators

**Files:** none; conversation bootstrap only.

**Produces:** one independent coordinator conversation for Gate 0, 1, 2, and 3.

- [ ] Each coordinator reads current canonical handoff, state-maintenance protocol, DeepSeek executor amendment/profile/policy, and its Gate-local state.
- [ ] Each coordinator verifies mutable SHAs before making current-state claims.
- [ ] Each coordinator remains permanently Gate-scoped and may only coordinate its own Gate.
- [ ] Each coordinator generates one self-contained DeepSeek Harness root-controller prompt/Goal appropriate to the current Gate frontier.

### Task 4: DeepSeek Harness Gate-session capability preflight

**Files:** no project file changes required unless the Gate later creates an authorized ledger/receipt.

**Produces:** a verified Harness controller capability state per Gate.

- [ ] Verify durable Goal tools/controls exist before creating a Goal.
- [ ] Verify automatic goal-round continuation is available if autonomous rounds are requested; do not infer it from Goal existence.
- [ ] Verify at least one subagent delegation backend/tool before promising child delegation.
- [ ] Verify the root session is bound to the correct Gate worktree/controller branch.
- [ ] If any required capability is missing, stop as `GOAL_BLOCKED_TECHNICAL` rather than emulating the capability silently.

### Task 5: Durable Goal creation and rolling-frontier operation

**Files:** Gate-local ledgers/receipts only when separately authorized by the Gate coordinator.

**Produces:** controlled progress to the highest currently authorized dependency-safe Gate frontier.

- [ ] Create one durable Goal whose completion semantics are current-frontier completion, not unconditional Gate completion.
- [ ] Root agent performs controller/scheduler/integrator/verifier role and delegates substantial independent work to self-contained children when safe.
- [ ] Prefer one-shot children for bounded tasks; use continuable children only for genuine ordered follow-up.
- [ ] Writer children use exclusive paths or temporary isolated child worktrees; parent controller alone integrates accepted work.
- [ ] Keep heavy local execution within portfolio-v1 leases regardless of logical child count.
- [ ] Persist exact dependency/authority SHAs and return one of the allowed Goal frontier terminal states when no authorized READY work remains.

### Task 6: Verification and handoff

**Produces:** evidence that the executor transition did not alter project authority or corrupt local topology.

- [ ] Verify admin + Gate0–3 are the only permanent portfolio worktrees.
- [ ] Verify controller branches remain the same four authoritative branches.
- [ ] Verify current Gate state and scientific maturity did not change merely due to executor transition.
- [ ] Verify Codex and DeepSeek Harness were not simultaneous writers on a Gate branch.
- [ ] Verify no protected/scored/provider/model/promotion/destructive scope was entered.
- [ ] Return exact current SHAs, executor state, and the next Gate-local frontier.
