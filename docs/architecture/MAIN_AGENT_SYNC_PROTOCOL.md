# Main-Agent Local/Remote Synchronization Protocol

**Status:** CURRENT REPOSITORY PROCESS CONTRACT  
**Scope:** canonical-main observation plus active execution-branch synchronization  
**Primary authority:** `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`

Synchronization preserves provenance. It never grants permission to overwrite, discard, force-push, or silently integrate unknown work.

## 1. Two synchronization surfaces

Every substantial repo-working Goal observes:

1. canonical `main` / `origin/main`;
2. the active execution branch / its remote counterpart.

During ordinary execution, the active execution branch is the writable durability surface.

Canonical main is observational unless the owner explicitly authorizes a dedicated canonical integration/policy-promotion action.

## 2. Non-destructive rules

Synchronization never authorizes:

- `git reset --hard`;
- `git clean`;
- force push;
- auto-stash/drop;
- silent merge/rebase of divergence;
- deletion of unrelated branches/worktrees;
- automatic canonical-main mutation;
- indiscriminate staging of unknown filesystem state.

Preserve and attribute pre-existing tracked/untracked state.

## 3. Start-of-Goal gate

Before substantive work/child dispatch:

1. identify repository/worktree/current branch;
2. record dirty/untracked state;
3. fetch origin;
4. compare local canonical main with origin/main;
5. compare active execution branch with its remote;
6. record exact base/anchor SHA;
7. reconcile only through provably non-destructive operations.

No child dispatch until exact Goal base is recorded or an explicit sync blocker exists.

## 4. Canonical-main dispositions

For the canonical main worktree where observable:

- **equal:** proceed;
- **behind-only and safe:** fast-forward local main if needed for observation/bootstrap;
- **ahead-only:** do not push merely because it is ahead; inspect whether those commits are an explicitly authorized canonical-main action;
- **diverged:** preserve both tips; do not auto-merge/rebase;
- **dirty/unsafe:** do not stash/reset; record blocker;
- **remote unavailable:** do not claim synchronization.

Ordinary execution Goals do not create canonical-main commits.

## 5. Active execution-branch dispositions

For the assigned execution branch:

- **equal:** proceed;
- **remote behind / local ahead with known authorized Goal commits:** run checks and non-force push when authorized;
- **local behind / remote ahead and safe fast-forward:** fast-forward;
- **diverged:** preserve both tips; no force push or silent rebase;
- **dirty/unknown:** attribute before mutation.

## 6. Remote-main race during execution

Before any execution-branch push, fetch origin again.

If origin/main advanced:

- record new main SHA;
- do not overwrite/merge it automatically;
- determine whether current Goal authority/base is still valid;
- if not valid, preserve work and park/stop.

## 7. End-of-Goal gate

Before final Goal response:

1. terminalize completed children;
2. ensure accepted safe work is integrated into active execution branch;
3. persist compact Goal/Problem state;
4. run task-specific verification;
5. fetch origin;
6. non-force push execution branch when authorized;
7. fetch/compare and verify execution local/remote equality when observable;
8. separately compare canonical main with origin/main;
9. report execution sync state and main observation state.

A blocked Goal still preserves safe accepted work.

## 8. Canonical-main mutation boundary

Canonical main mutation requires explicit owner authorization for a task whose purpose/authority includes canonical integration or policy promotion.

Before such mutation:

- bind exact candidate head;
- fetch origin/main;
- verify main has not unexpectedly advanced;
- use non-destructive integration;
- never force push;
- push main only after required checks;
- fetch again;
- require post-push local/remote main equality;
- rerun the pushed-state verifier/invariants.

Passing tests alone do not grant main-merge authority.

## 9. Relationship to child lanes

Child branches/worktrees follow `SUBAGENT_LANE_PROTOCOL.md`.

Ordinary flow:

`child candidate -> compact handoff -> stale-base/ownership check -> milestone execution branch -> verified execution-branch checkpoint`

Not:

`child -> automatic canonical main`

Per-child remote branches are not required by default.

## 10. Recovery

After interruption/compaction:

1. fetch current repository state;
2. read current process authority/handoff;
3. recover exact portfolio/Goal/root identity;
4. compare Git heads with durable machine state;
5. resolve discrepancies in favor of Git plus higher owner/repository authority;
6. resume from first incomplete dependency-safe node.

Old chat is not authority.

## 11. Branch hygiene

Fetching/pruning remote-tracking refs for synchronization is not the future branch-cleanup task.

Do not delete historical project branches or worktrees under this protocol merely because they are old.
