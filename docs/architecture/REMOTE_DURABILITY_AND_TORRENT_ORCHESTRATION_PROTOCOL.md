# Remote Durability and Rolling-Frontier Orchestration Protocol

**Status:** CURRENT REPOSITORY PROCESS CONTRACT  
**Scope:** substantial Codex and DeepSeek repository Goals  
**Primary authority:** `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`

This protocol governs remote durability and long-running Goal continuation. It does not authorize protected/archive media, provider/cloud activity, model downloads, destructive Git, production export, Gate promotion, or canonical-main integration.

## 0. 2026-10-03 Remaining-Work launch/continuation override

Remaining-project execution now uses the Atlas model defined in:
- `docs/superpowers/specs/2026-10-03-remaining-work-execution-atlas-and-parallel-verification-design.md`
- `docs/superpowers/plans/2026-10-03-remaining-work-execution-atlas-implementation-plan.md`

Current continuation rules:

- durable execution state, not chat history, is authoritative for resume;
- fresh H3 work defaults to a fresh top-level Codex;
- known H3 prompt **Frozen Cores** are prepared/versioned in advance; launch-time SHAs, dependency heads, open Problems, contract deltas, resource leases, and model identity live in a small **Launch Overlay**;
- owner-facing dispatch is packaged as numbered **Launch Packs** of copy-ready prompts;
- between Launch Packs, perform bounded **Launch Delta Reconciliation** only: consume receipts, update READY/DIRTY/PARKED state, patch only actually affected prompts, and render the next useful batch;
- do not regenerate unaffected prompt cores merely because the controlling ChatGPT context changed;
- BUILD, VERIFY, and REPAIR continue concurrently; an earlier verification/review/repair lane may remain active while later dependency-safe BUILD proceeds;
- an upstream contract delta may revoke an in-flight descendant; mark it `STALE_IN_FLIGHT` and do not integrate it as current;
- terminal root chat output is a compact receipt pointing to durable repository state, not a full narrative transcript.

Resource authority is `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`.

## 1. Goal boundary synchronization

At Goal start:

1. identify repository root, root worktree, active execution branch, exact HEAD, dirty state, and relevant remote;
2. fetch origin non-destructively;
3. compare canonical main with origin/main;
4. compare active execution branch with its remote counterpart;
5. preserve unknown local/remote divergence;
6. reconcile only through safe fast-forward/push-safe operations;
7. bind exact Goal base/anchor before child dispatch.

Do not:

- hard reset;
- git clean;
- auto-stash;
- force push;
- silently merge/rebase divergence;
- delete branches/worktrees as a side effect of synchronization.

## 2. Execution branch is the writable durability surface

During an execution Goal, the root's assigned execution branch is the ordinary writable remote-durability surface.

After each coherent accepted integration batch, when push authority exists:

1. run batch-appropriate focused checks;
2. fetch origin;
3. verify fast-forward-safe push;
4. push only the assigned execution branch;
5. fetch/compare and verify remote contains the checkpoint.

Do not push every child scratch branch by default.

A Goal that later blocks should still preserve all safe accepted work on its execution branch when possible.

## 3. Canonical main is observational during execution Goals

Execution Goals observe/fetch/compare canonical main, but do not mutate it merely to satisfy durability.

Canonical-main integration remains a separately authorized owner decision.

Remote durability of an execution branch does not imply:

- main integration;
- Gate promotion;
- production readiness;
- provider/model authority;
- protected/archive authority.

## 4. Remote-main advancement during a Goal

If origin/main advances after the Goal base is frozen:

- do not silently merge/rebase it into the active execution branch;
- record the new main SHA;
- determine whether the Goal's authority/base assumptions are stale;
- continue only if current authority permits the unchanged Goal base;
- otherwise park/stop with an explicit stale-authority/base blocker.

## 5. Multi-root durability

Multiple roots may checkpoint independently only to their own assigned branches.

Roots must not:

- push sibling branches;
- move sibling refs;
- mutate shared portfolio anchor after freeze;
- administer sibling worktrees without serialized Worktree Admin authority.

Cross-root communication uses Git SHAs and durable machine state, not hidden chat.

## 6. Portfolio anchor

A substantial multi-root portfolio may use an immutable non-main anchor branch/commit containing only compact execution metadata.

After root creation:

- anchor is frozen;
- roots branch from the anchor or from an explicitly declared dependency base;
- anchor is not used as a rolling integration branch;
- only a later convergence/integration phase combines root outputs.

## 7. Codex model policy

Requested Codex family:

`LUNA`

Requested reasoning:

`medium`

At Goal start:

- resolve one currently supported concrete Luna model;
- freeze that model for the Goal;
- explicitly set model/reasoning for eligible child spawns;
- verify effective values where runtime metadata supports it.

Do not silently switch concrete Luna generations mid-Goal.

## 8. DeepSeek model policy

DeepSeek follows the current verified DeepSeek controller profile.

Do not apply Codex LUNA rules to DeepSeek.

Executor switching does not change Git authority, evidence classes, source restrictions, or resource leases.

## 9. Rolling frontier

A substantial Goal is a dependency DAG.

The root continuously:

- discovers READY nodes;
- allocates non-overlapping ownership;
- dispatches all useful dependency-safe work;
- receives compact handoffs;
- checks stale-base/ownership state;
- integrates or parks results;
- closes terminal children;
- immediately refills safe capacity.

Do not wait for artificial waves.

## 10. Concurrency

Use highest useful safe concurrency supported by:

- dependency graph;
- branch/path/contract ownership;
- harness limits;
- machine/runtime capacity;
- current resource policy.

Do not manufacture duplicate workers merely to reach a number.

Logical agent concurrency never expands heavy local model/FFmpeg authority.

## 11. Root role

Root is primarily:

- scheduler;
- dispatcher;
- dependency/frontier manager;
- milestone-branch integrator;
- incident adjudicator;
- remote-checkpoint owner;
- verifier.

Delegate substantive work whenever clean ownership exists.

## 12. Durable child memory

Child detail remains repository-backed.

Code/tests live in commits.

Scheduler/problem state is compact and machine-readable.

Parent handoff remains small.

Terminal children close; do not preserve knowledge by keeping sessions active.

## 13. Failure remediation

Intermediate failure is not automatically a user-return boundary.

Use:

1. evidence preservation;
2. systematic root-cause investigation;
3. RED regression when applicable;
4. smallest justified repair;
5. GREEN verification;
6. Problem-record update.

Default budget:

three evidence-supported failed remediation generations for the same load-bearing Problem/root-cause family.

Do not reset the budget by renaming a failed hypothesis.

Malformed commands/patches that never exercised the intended repair do not consume a generation.

After exhaustion:

- preserve full Problem state;
- park affected descendants;
- continue independent READY work;
- return only if no useful frontier remains or another hard boundary applies.

## 14. No ordinary review/certification treadmill

Ordinary development uses:

- BUILD;
- ENABLE;
- REPAIR;
- TDD;
- systematic-debugging;
- deterministic/static/test verification.

Do not allocate ordinary Goal capacity to reviewer/certifier swarms or repeated review-remediation-certification generations.

Formal review/certification is a later owner-directed epoch.

## 15. Goal terminal synchronization

Before Goal response:

1. terminalize/close completed children;
2. integrate every accepted safe result into the execution branch;
3. persist compact Goal/Problem/handoff state;
4. run task-specific verification and secret/path checks;
5. fetch origin;
6. push execution branch non-force if authorized and safe;
7. fetch/compare and require local execution head == remote execution head when observable;
8. separately observe canonical main / origin/main and report whether main changed.

Blocked Goals follow the same durability rule for safe accepted work.

If push is impossible/unsafe, preserve local work and report an explicit sync blocker.

## 16. Owner-return boundaries

Continue autonomously through:

- ordinary child completion;
- ordinary test failure;
- ordinary bug;
- one repair failure;
- newly opened dependency-safe work.

Return for:

- milestone terminal condition;
- authorization boundary;
- destructive/irreversible requirement;
- external credential/user interaction prerequisite;
- three-generation technical exhaustion that leaves no useful path;
- genuine architecture/product decision above current authority;
- remote durability failure that prevents safe preservation.

## 17. Fresh-session recovery

Recover from:

- AGENTS/current reading order;
- current project handoff;
- exact portfolio manifest/anchor;
- Goal/root branch identity;
- durable Goal/lane handoffs;
- relevant Problem records;
- exact local/remote SHAs;
- resolved model identity/resource leases.

Do not ask terminal children to restate their work.

## 18. Main rule

No execution Goal merges canonical main.

No convergence-analysis Goal merges canonical main.

No remediation Goal merges canonical main automatically.

No integration Goal merges canonical main automatically.

Only explicit owner authorization for the exact integrated state permits canonical-main integration.
