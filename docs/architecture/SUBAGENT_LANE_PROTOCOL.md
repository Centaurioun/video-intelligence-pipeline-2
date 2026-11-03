# Repository Subagent Lane Protocol

**Status:** CURRENT REPOSITORY PROCESS CONTRACT  
**Scope:** Codex and DeepSeek repository execution under the current Execution Portfolio epoch.  
**Primary authority:** `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`  
**Current resource policy:** `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`

This protocol defines child isolation, delegation, durable state, handoff, stale-base acceptance, and closure. It does not authorize product scope, protected/archive media, provider/cloud activity, model downloads, production export, Gate promotion, destructive Git, or canonical-main integration.

## 0. 2026-10-03 Remaining-Work lane override

For Remaining Work Atlas H3/H4 execution:

- the normal hierarchy remains `Root Orchestrator -> Area Lead/Supervisor -> Worker` when nested delegation is actually supported; otherwise flatten to `Root -> Workers`;
- the root is the control plane and should not serialize delegable substantive work;
- if two or more H4 shards are independently READY, dispatch them concurrently in the same rolling frontier when capacity exists;
- terminal children are closed and their slots are recycled immediately;
- workers may persist high-volume findings in goal-local file-backed state; supervisors aggregate those records before returning compact state to the root;
- concurrent writer workers require exclusive path/contract ownership; read-only workers may share immutable candidate state;
- a child whose consumed contract becomes stale while running is marked `STALE_IN_FLIGHT`; its result is historical/exploratory until explicitly reconciled and may not be accepted into the current candidate merely because it reports success;
- every H3 BUILD_GREEN candidate queues a separate feature-level code-review lane on VERIFY before convergence/current-main integration; this is not a reviewer-after-every-H4 loop;
- stock Superpowers `subagent-driven-development` is not the default lane executor; independent H4 work uses `dispatching-parallel-agents` under the current throughput protocol;
- resource leases are class-specific under resource-policy v5 and do not impose a fixed logical child/root count.

These rules supersede conflicting older lane-completion wording but preserve isolation, stale-base, ownership, safety, and durability requirements.

## 1. Lane purpose

Subagents exist to:

- increase useful parallel execution capacity;
- keep root/Area Lead contexts small;
- isolate writable ownership;
- make failures independent;
- allow terminal agents to close without losing engineering state.

The repository is durable memory; chat is not.

## 2. Ordinary execution roles

Normal execution lane classes:

- BUILD;
- ENABLE;
- REPAIR.

Optional read-only/support roles:

- Area Lead;
- Context/State Curator;
- focused investigator;
- migration/dependency analyzer;
- convergence analyzer.

REVIEW / CERTIFY / RECERTIFY are not ordinary intermediate execution lane classes during the current epoch.

## 3. Model policy

Model/reasoning policy is executor-specific.

For Codex:

- requested family: `LUNA`;
- reasoning: `medium`;
- resolve one concrete supported Luna model at Goal start;
- freeze that resolution for the Goal;
- explicitly set model + reasoning on eligible child spawns;
- verify effective model/reasoning through supported metadata when possible.

For DeepSeek:

- follow the current verified DeepSeek controller profile and resource policy;
- do not apply the Codex LUNA rule to DeepSeek.

Unknown/unverified effective model state is a scheduling blocker for that lane when the governing Goal requires verification.

## 4. Preferred hierarchy

Preferred maximum hierarchy:

`Root Orchestrator -> Area Lead -> Worker`

Area Leads may spawn workers only when the runtime positively supports compliant nested delegation with:

- requested model/reasoning;
- isolated context;
- ownership controls;
- durable handoff;
- closure.

Workers do not spawn another generation by default.

If nested delegation is unavailable or unverifiable, flatten to:

`Root -> Workers`

An Area Lead may remain an analysis/scheduling role while the root performs the actual child spawn.

## 5. Run / Goal / lane identity

Every child receives:

- PORTFOLIO_ID when applicable;
- GOAL_ID;
- LANE_ID;
- exact BASE_SHA;
- root/Area Lead identity;
- branch/worktree identity;
- task;
- read scope;
- write mode/domain;
- consumed contract refs;
- required tests;
- relevant Problem IDs;
- model/reasoning requirement;
- durable state path.

Identities are unique inside the Goal.

## 6. Isolation

A writer child never works directly on canonical main.

Writer child options:

- exclusive path ownership inside a root-owned milestone worktree where harness semantics make that safe; or
- isolated child branch/worktree.

Two active writer children may not own the same exact path unless the parent has explicitly defined them as competing disposable candidates that will not both be integrated.

Read-only children may inspect overlapping paths if their questions are genuinely distinct.

## 7. Worktree safety

If a child worktree is used:

- its base SHA is explicit;
- it is not the canonical main worktree;
- its branch/worktree identity matches the assignment;
- shared worktree/ref administration follows the serialized Worktree Admin rule;
- sibling worktrees/refs are not mutated;
- removal occurs only after the candidate/state is durable and dispositioned.

Unknown dirty/untracked state is preserved and attributed rather than deleted.

## 8. Write-scope expansion

A child may discover that implementation needs a path or shared interface outside expected ownership.

It must not silently widen global authority.

It records:

- UNPLANNED_SHARED_SURFACE;
- reason;
- exact path/interface;
- PRODUCED_CONTRACT_DELTA if applicable;
- known consumers/compatibility risk.

The change remains isolated on the child's/root's own branch and later convergence determines reconciliation.

## 9. Durable execution state

Routine child work does not require a long Markdown narrative memo.

Code/tests live in commits.

Durable child state is compact and machine-readable.

Recommended sharded path:

`.orchestration/goals/<goal-id>/lanes/<lane-id>.json`

Do not create one shared append-only lane/problemlog that every root writes.

Ephemeral queue/polling/slot state may remain local and reconstructable.

## 10. Compact handoff

Terminal child handoff includes, as applicable:

- STATUS;
- PORTFOLIO_ID;
- GOAL_ID;
- LANE_ID;
- BRANCH;
- BASE_SHA;
- HEAD_SHA;
- CHANGED_PATHS;
- PUBLIC_INTERFACES_CHANGED;
- SHARED_SURFACES_TOUCHED;
- CONSUMED_CONTRACT_REFS;
- PRODUCED_CONTRACT_DELTAS;
- UNPLANNED_SHARED_SURFACES;
- ASSUMPTION_CHANGES;
- TEST_ENTRYPOINTS;
- OPEN_PROBLEM_IDS;
- BLOCKER;
- STATE_PATH.

Do not paste:

- full diff;
- long logs;
- complete internal analysis;
- raw hidden reasoning.

## 11. BASE_SHA and stale-base acceptance

Every child handoff binds exact BASE_SHA.

Before accepting candidate work, parent compares:

- child BASE_SHA;
- current milestone HEAD;
- child changed paths;
- public/interface/contract deltas;
- changes integrated since child base.

Disposition:

### CURRENT_BASE
Normal ownership/test/integration checks.

### STALE_DISJOINT
If implementation paths and contract/semantic surfaces are disjoint:
- integrate only through a safe non-destructive method;
- run focused/regression verification.

### STALE_OVERLAP
If paths, contracts, migrations, dependency semantics, or assumptions overlap:
- do not blindly cherry-pick/rebase;
- PARK candidate;
- inspect actual conflict;
- spawn fresh reconciliation/repair work from current milestone head when needed.

A child may not rewrite its reported base to hide staleness.

## 12. Parent acceptance

Child completion is not acceptance.

Parent verifies:

- exact branch/head exists;
- BASE_SHA is truthful;
- changed paths fit ownership;
- required tests/checks actually ran where observable;
- durable state exists;
- open Problems are explicit;
- contract/shared-surface deltas are explicit.

Disposition:

- INTEGRATED;
- REJECTED;
- PARKED;
- BLOCKED.

Acceptance is into the milestone execution branch, never directly into canonical main.

## 13. Child lifecycle

Canonical lifecycle:

`PLANNED -> ACTIVE -> HANDOFF_READY -> INTEGRATED | REJECTED | PARKED | BLOCKED -> CLOSED`

When terminal:

1. persist authorized code/tests/state;
2. emit compact handoff;
3. parent verifies scheduler/integration facts;
4. parent records disposition;
5. close/terminate child where supported;
6. if explicit close is unavailable, mark TERMINAL_INACTIVE;
7. never reuse terminal child for new work;
8. recycle the slot immediately.

## 14. Rolling frontier

The parent continuously:

- discovers READY nodes;
- allocates ownership;
- dispatches all useful dependency-safe work;
- processes completed handoffs;
- closes terminal children;
- unlocks dependent work;
- refills capacity.

Do not wait for an artificial whole-wave barrier.

## 15. Slot saturation

If all usable slots are active:

- queue new READY work;
- do not kill productive children merely to create capacity;
- prioritize critical-path unblocks when a slot opens;
- use event-driven/long waits rather than tight polling when supported;
- parent performs only nondelegable scheduling/integration/verification work;
- refill immediately after terminal closure.

## 16. Context Curator

A broad Goal may use an optional Context/State Curator.

The curator:

- reads compact durable scheduler state;
- deduplicates READY/ACTIVE/BLOCKED/COMPLETE information;
- identifies free ownership surfaces;
- summarizes dependency/problem state;
- does not review code quality;
- does not certify;
- does not make canonical product decisions.

If curator context grows large, close it and create a fresh curator that reconstructs from repository state.

## 17. Problem interaction

A child encountering a failure follows systematic-debugging.

Problem records are sharded by Goal/problem ID.

A worker should consult relevant resolved/open Problem records before repeating expensive diagnostics.

Repair attempts follow the bounded remediation budget in the throughput protocol.

## 18. Root/Area Lead handoff discipline

Area Leads return compact scheduler state to the root.

They do not dump all worker outputs into root context.

The root reads deeper state only on demand.

A terminal milestone root emits one compact `milestone-handoff.json` or equivalent containing:

- exact base/head;
- changed paths;
- public interfaces;
- shared surfaces;
- consumed/produced contract refs;
- assumptions;
- dependency/migration changes;
- test entrypoints;
- open Problem IDs;
- terminal disposition.

## 19. Remote durability

Per-child remote branches are not required by default.

Accepted work becomes durable through the root's execution branch checkpoints when authorized.

A child/root may not interpret successful remote durability as permission to merge canonical main.

## 20. Historical evidence

Existing Markdown lane memos under `docs/agent-runs/` remain historical evidence.

They are not the mandatory format for new execution lanes.

Do not rewrite or delete them merely to conform to this protocol.

## 21. Completion

A lane is complete only when:

- its candidate/state is durable as required;
- BASE_SHA/HEAD_SHA are explicit;
- ownership and open Problems are explicit;
- tests/checks required by the task were observed;
- parent has dispositioned the result;
- child is closed/inactive.

Formal review/certification is not part of ordinary lane completion during the current execution-first epoch.

## 22. Routine prerequisite handoff and environment ownership

Routine development/test prerequisite failures follow resource-policy v5 and the throughput protocol; they are not ordinary owner-return boundaries.

When a child is blocked by a missing routine prerequisite, its compact handoff includes:

- `PREREQUISITE_STATUS`;
- `BLOCKED_COMMAND`;
- `ERROR`;
- `INTERPRETER_OR_RUNTIME`;
- `ENVIRONMENT_PATH`;
- `MISSING_PREREQUISITE`;
- `AFFECTED_TEST_OR_TASK`;
- `LOCAL_OR_CACHED_RECOVERY_OBSERVED`;
- `ROOT_ACTION_REQUIRED=ENVIRONMENT_RECOVERY`.

The child preserves the exact failure evidence and returns it to the root. It does not independently classify a routine package/tool absence as `GOAL_BLOCKED_AUTHORIZATION` or `GOAL_BLOCKED_EXTERNAL_PREREQUISITE`.

The root owns environment continuity. It may perform recovery directly or dispatch a bounded environment-repair worker.

A shared project environment is a `SHARED_MUTABLE_RESOURCE`: concurrent reads are allowed, but mutation requires serialized `ENV_ADMIN` ownership. Ordinary workers do not independently mutate a shared environment.

Parallel roots may create/use independent Goal-local project/user-scoped environments under resource-policy v5.

An import/collection/missing-tool failure does not satisfy behavioral RED. After recovery the pre-implementation test is rerun. If implementation already exists, test-efficacy recovery may establish RED on pre-implementation code and GREEN on implementation code, while chronological RED remains `NOT_OBSERVED` when that is historical fact.

Explicit narrower Gate/task/spec/plan restrictions override this general lane policy.
