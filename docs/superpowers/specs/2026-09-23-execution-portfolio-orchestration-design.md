# Execution Portfolio Orchestration Design v2 — Refined Execution-First Portfolio

**Status:** independently refined planning/design candidate for owner review; no product implementation authority is created by this document  
**Branch:** planning/execution-portfolio-orchestration-v1  
**Base:** canonical main at 12e3b199591511f46c9e885008ad69237f462fb7  
**Purpose:** define the execution-first operating model for completing the remaining Video Intelligence Pipeline product work with multiple parallel Codex/DeepSeek roots, aggressive useful subagent delegation, bounded failure remediation, durable machine-readable execution memory, isolated Git worktrees, and final-only review/certification.

---

## 1. Intent

The project is entering an execution-first epoch.

The primary objective is to complete useful product code and working capabilities as quickly as safely possible. Review, certification, audit-document churn, and repeated planning cycles are not the normal development loop for this epoch. They are deferred until the remaining executable product work is substantially complete, unless the owner explicitly requests them earlier.

This design is intentionally optimized for:

- high wall-clock throughput;
- many genuinely useful concurrent agents;
- clean context windows for root orchestrators and area leads;
- strong Git isolation;
- durable recovery after agent closure or context compaction;
- bounded debugging rather than infinite remediation;
- explicit problem memory, including failed and successful solution attempts;
- minimal development-time documentation;
- controlled convergence of independently developed milestone branches;
- preservation of all existing source, temporal, evidence, and authorization boundaries.

This design does not itself authorize protected/archive-media execution, provider/cloud activity, model downloads, production export, Gate promotion, destructive Git operations, or any other previously restricted activity.

---

## 2. Development epoch policy

### 2.1 Code-completion first

The default allocation of agent capacity is:

1. BUILD — code, tests, fixtures, schemas/configuration genuinely required by the code;
2. ENABLE — interfaces, migrations, tooling, adapters, data paths, or prerequisites that unlock BUILD work;
3. REPAIR — systematic debugging and bounded fixes for failures encountered during execution.

The following are not normal intermediate lane types during this epoch:

- REVIEW;
- CERTIFY;
- RECERTIFY;
- AUDIT;
- documentation-only analysis waves.

Task review, batch review, certification, and recertification are deferred to a later owner-directed final phase.

### 2.2 Verification is not review

The following remain mandatory engineering work and are not classified as review/certification:

- test-driven development for behavior changes;
- focused unit tests;
- integration and regression tests;
- deterministic/static checks;
- reproducibility checks where relevant;
- verification-before-completion;
- systematic-debugging for unexpected failures;
- source-preservation checks;
- temporal/PTS correctness checks;
- secret checks and Git safety checks;
- runtime verification required to establish that the milestone actually works.

### 2.3 Final review is a later phase

A final project review/certification phase may be created only after the remaining major execution blocks have been completed and integrated, or earlier if the owner explicitly requests it.

Until then:

- no reviewer swarm;
- no certifier swarm;
- no repeated review/remediation/certification loop;
- no review memo generation as routine development output.

External owner-controlled ChatGPT inspection may occur between Goals, but it is not automatically an execution gate unless the owner says so.

### 2.4 Transition authority — execution MUST NOT start from contradictory canonical policy

This planning branch does not silently override current canonical process contracts.

Current canonical main still contains material rules that conflict with this proposed epoch, including:

- Codex children hard-pinned to `gpt-5.6-luna`;
- nested delegation disabled by default;
- mandatory Markdown lane memos under `docs/agent-runs/`;
- child durability/integration language centered on canonical `main`;
- default intermediate review/certification waves;
- a main-sync protocol whose older sections still describe accepted child work flowing directly to `main`;
- a portfolio resource policy whose writer-controller budget does not yet express the proposed multi-root Codex execution portfolio;
- repository handoff text that references `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`, which is absent on the reviewed canonical main.

Therefore:

> NO execution Goal may claim this design as governing repository policy until the required process-policy promotion is explicitly approved and committed to canonical main.

The user's current instruction establishes the intended future direction, but this planning branch remains a design candidate. The later main-promotion step must make supersession explicit rather than depending on agents to infer that newer intent cancels older text.

This transition gate prevents two fresh agents from following different valid-looking repository contracts during the same execution epoch.

---

## 3. Goal semantics

### 3.1 Goal means milestone

A Codex/DeepSeek Goal is a meaningful product milestone, not a micro-task.

A suitable Goal should normally:

- contain several independent or partially independent execution fronts;
- support sustained delegation to multiple workers;
- produce a materially new working capability;
- be large enough that a five-minute single-edit completion would normally indicate under-scoping;
- terminate on capability completion or a genuine hard blocker, not merely because one internal task finished.

Wall-clock duration is not itself a contract. The design goal is sustained useful work, not an artificial minimum runtime.

### 3.2 Internal units

Inside a Goal, the orchestrator may create many small scheduler nodes. A Goal can therefore contain dozens of implementation, enabling, repair, migration, test, or integration tasks without exposing those nodes to the owner as separate Goals.

### 3.3 Goal terminal states

Recommended execution-oriented terminal states:

- GOAL_COMPLETE;
- GOAL_COMPLETE_WITH_DEFERRED_PROBLEMS;
- GOAL_BLOCKED_AUTHORIZATION;
- GOAL_BLOCKED_EXTERNAL_PREREQUISITE;
- GOAL_BLOCKED_TECHNICAL_EXHAUSTION;
- GOAL_BLOCKED_DESTRUCTIVE_OR_IRREVERSIBLE_ACTION;
- GOAL_BLOCKED_ARCHITECTURE_DECISION.

A nonblocking open problem does not prevent GOAL_COMPLETE_WITH_DEFERRED_PROBLEMS.

GOAL_COMPLETE_WITH_DEFERRED_PROBLEMS is valid only when:

- the declared milestone capability is working under its stated acceptance checks;
- no unresolved problem has `frontier_impact=GOAL_BLOCKER`;
- no unresolved CRITICAL problem threatens source preservation, evidence/temporal correctness, authorization/security boundaries, data integrity, or the declared capability itself;
- every deferred problem has a durable problem record and an explicit downstream impact;
- blocked descendants outside the completed milestone are identified rather than silently forgotten.

A HIGH or CRITICAL label by itself does not automatically define scheduler impact, but safety/integrity-critical defects may not be hidden behind a NON_BLOCKING label.

---

## 4. Portfolio-level parallelism

### 4.1 Multiple root Codex sessions

The remaining product work should be decomposed into large execution blocks. When blocks are independent or only weakly coupled, multiple root Codex sessions may run simultaneously.

Illustrative topology:

- Root A — Milestone A;
- Root B — Milestone B;
- Root C — Milestone C;
- Root D — Milestone D.

The letters are placeholders, not permanent project identities.

Each root:

- receives one bounded milestone Goal;
- receives an exact frozen base SHA;
- receives an expected write/ownership domain;
- works on its own branch and linked worktree;
- does not merge to main;
- does not merge another root's branch;
- does not repair another root's branch;
- may use its own hierarchy of subagents;
- persists code and execution state independently.

### 4.2 Same repository, separate linked worktrees

Use one repository/object store with linked worktrees rather than multiple permanent clones.

Preferred local shape:

    /Users/yusuf/Repos/video-intelligence-pipeline/
      .git/
      .worktrees/
        milestone-a/
        milestone-b/
        milestone-c/
        milestone-d/
        integration-.../

The actual placement may differ if Git safety or the Codex App requires another linked-worktree location, but the conceptual rule is one repository with isolated worktrees.

The .worktrees path must be safely ignored before use if it lives inside the primary working tree.

### 4.2.1 Serialized worktree/ref administration

Parallel roots may share one Git object store, but they must not concurrently administer shared Git topology without coordination.

Before a portfolio wave starts, one short-lived **Portfolio Bootstrap / Worktree Admin** operation should:

- verify the common repository and remote state;
- allocate unique root IDs, branch names, and worktree paths;
- create required root branches/worktrees from the exact approved anchor/base;
- record the assignments in the portfolio manifest;
- ensure no root worktree points at `main`;
- release the admin role before substantive root execution begins.

During execution:

- roots may commit and non-force push only their own assigned execution branch;
- roots must not create/delete/prune sibling root worktrees;
- roots must not move sibling refs;
- roots must not rewrite the shared portfolio anchor;
- `git worktree add/remove/prune` and other topology-changing operations require a serialized WORKTREE_ADMIN lease or equivalent single-owner mechanism;
- child worktree creation/removal under one root must still respect the repository-wide serialized worktree-administration rule.

This is coordination through durable repository state, not root-to-root chat.

The later implementation plan may choose the simplest reliable lease mechanism available on the host; the design does not require building a distributed lock service.

### 4.3 No main mutation during portfolio execution

Parallel execution roots do not merge to main.

Main remains the stable authority/integration target until the owner explicitly authorizes a final integration step.

Execution branches may be pushed for remote durability when the governing Goal explicitly permits safe non-force branch pushes. Such pushes do not authorize main integration.

### 4.4 Frozen common base when practical

Parallel roots should preferably start from one common frozen base SHA.

Benefits:

- easier changed-path comparison;
- easier provenance;
- easier overlap detection;
- clearer ownership;
- simpler later convergence analysis.

When a true dependency requires one block to start from another completed block, that dependency should be represented explicitly rather than forcing a false common base.

---

## 5. Portfolio DAG and sharding

Before starting a multi-root execution wave, create an Execution Portfolio DAG.

### 5.1 Portfolio anchor

Prefer a portfolio-specific anchor rather than letting independent roots infer their own starting state.

A typical portfolio bootstrap may:

1. start from the exact approved canonical/integration base;
2. create one non-main `execution/portfolio-<id>-anchor` branch;
3. commit only the compact machine-readable portfolio manifest needed for orchestration;
4. freeze that anchor SHA;
5. create independent milestone root branches/worktrees from that anchor.

The anchor is not a merge target and does not authorize product work by itself. Roots do not modify it after freeze.

The manifest should minimally bind:

- portfolio ID;
- authority/base SHA;
- anchor SHA;
- root IDs;
- root branch/worktree identities;
- milestone Goal identities;
- PARALLEL_CLASS;
- expected write domains;
- frozen shared-contract references;
- prohibited scope;
- heavy-resource constraints;
- resolved executor/model policy;
- required terminal handoff artifact per root.

If no portfolio manifest commit is useful for a small execution, the same data may be bound in owner-approved Goal packets; do not create an artifact merely for ceremony.

### 5.2 Per-block record

For every proposed milestone block record:

- milestone identifier;
- product capability outcome;
- exact base SHA;
- PARALLEL_CLASS:
  - INDEPENDENT;
  - SOFT_DEPENDENCY;
  - HARD_DEPENDENCY;
- expected write domain;
- shared interfaces likely to be consumed;
- required upstream capabilities;
- prohibited scope;
- completion tests or observable capability;
- known problem dependencies.

Only blocks whose dependency relationship permits it should run simultaneously.

Before dispatch, identify **frozen shared-contract surfaces** such as public APIs, schemas, lockfiles, central registries, common config, CLI contracts, and shared provenance/temporal types. Roots may discover that a shared-contract change is necessary, but they must declare it explicitly as a contract delta rather than silently treating their branch-local interpretation as globally authoritative.

The planning goal is not to guarantee zero overlap. The planning goal is:

> predict and prevent obvious overlap; isolate writers; record unavoidable shared-surface changes; reconcile actual overlap later from real Git evidence.

---

## 6. Root-agent architecture

### 6.1 Tier 0 — Root Orchestrator

The root agent is primarily:

- authority interpreter;
- Goal decomposer;
- dependency-DAG owner;
- scheduler;
- worktree/branch coordinator;
- path-ownership allocator;
- integration owner inside its own milestone branch;
- incident adjudicator;
- remote-checkpoint owner when authorized;
- milestone verifier.

The root should avoid substantive coding whenever a clean delegation boundary exists.

The root context is the control plane, not the workbench.

### 6.2 Tier 1 — Area Leads

A broad Goal may create several Area Leads, for example:

- semantic/indexing;
- archive/source lifecycle;
- temporal/refinement;
- editorial/plan;
- render/QC;
- runtime/recovery;
- CLI/API;
- migration/shared contracts.

The actual areas are Goal-specific.

An Area Lead:

- receives a clean self-contained context;
- owns a coherent subsystem frontier;
- decomposes its scope into worker tasks;
- may spawn Tier-2 workers when the Goal explicitly authorizes nested delegation;
- tracks dependencies and path ownership inside its area;
- escalates only compact state to the root;
- does not merge to main.

### 6.3 Tier 2 — Ephemeral Workers

Workers perform the substantive work:

- implementation;
- tests;
- fixtures;
- bounded refactors;
- migrations;
- focused research needed to implement;
- debugging;
- measurements required by the Goal.

Workers are disposable.

When a worker finishes:

1. authorized code/tests/state are committed;
2. its compact execution state is persisted;
3. its parent verifies the result sufficiently for scheduling/integration;
4. the child is closed/terminated;
5. its slot is immediately reusable.

A finished child is never retained merely to preserve knowledge.

### 6.4 Maximum hierarchy depth and capability fallback

Default maximum hierarchy:

Root Orchestrator -> Area Lead -> Worker.

Workers should not spawn another generation by default.

If a worker discovers a need for additional specialization, it returns the need to its Area Lead, which may spawn another worker. This keeps delegation understandable and prevents uncontrolled recursive agent trees.

Nested delegation is a **runtime capability**, not an assumption. At Goal start the root must positively verify whether Area Leads can spawn compliant children with the required model, reasoning, isolation, persistence, and closure controls.

If nested delegation is unavailable or unverifiable:

- do not block the whole Goal merely to preserve the preferred tree;
- flatten the execution topology to Root -> Workers;
- optionally retain Area Leads as analysis/scheduling roles whose requested worker tasks are spawned by the root;
- preserve the same ownership and compact-state semantics.

The three-tier shape is therefore the preferred control topology, not a reason to fabricate unsupported harness behavior.

### 6.5 Stale-base child acceptance

Rolling-frontier execution means the milestone head may advance while a child is working.

Every child handoff must therefore bind its exact `BASE_SHA`.

Before accepting a child commit, the parent compares:

- child base SHA;
- current milestone head;
- child changed paths and public-contract deltas;
- changes integrated into the milestone since the child base.

Disposition:

- **base current:** normal acceptance checks;
- **base stale, disjoint implementation and contract surfaces:** integrate through a safe non-destructive method and verify focused/regression tests;
- **base stale with overlapping paths, shared contracts, migrations, or semantic assumptions:** do not blindly cherry-pick/rebase. Park the candidate, inspect the conflict, and spawn a fresh reconciliation/repair worker from the current milestone head when needed.

A child may not hide staleness by rewriting its reported base. Stale-base detection is part of normal rolling-frontier scheduling.

---

## 7. Model routing

### 7.1 Codex

Repository policy should become version-agnostic at the family level:

- requested family: LUNA;
- reasoning effort: medium.

Do not permanently hard-code gpt-5.6-luna as the conceptual policy.

At runtime the root must:

1. inspect the actual spawn/model allowlist exposed by the current Codex harness;
2. resolve the currently available Luna-family model identifier;
3. freeze one concrete `LUNA_MEDIUM_RESOLUTION` for that Goal;
4. explicitly set both the resolved model and medium reasoning effort on every eligible spawn;
5. verify the effective child model/reasoning through supported runtime metadata when possible;
6. record requested family, resolved model, effective model, and effective reasoning.

Do not silently change the concrete Luna generation halfway through a Goal. If the resolved model becomes unavailable, stop new spawns, preserve current work, and either re-resolve through an explicit Goal-level transition or obtain owner direction.

No silent fallback to a non-Luna family should be accepted when the Goal requires Luna Medium.

The root itself may be launched by the owner on the desired current Luna generation.

### 7.2 DeepSeek

The common orchestration architecture is executor-neutral.

DeepSeek continues to use the currently verified repository model/routing policy until the owner explicitly replaces it with a newer named DeepSeek policy. Do not invent or normalize an ambiguous model/preset name without verification.

The shared behavior across Codex and DeepSeek is:

- milestone Goal;
- hierarchical delegation;
- clean child contexts;
- rolling frontier;
- durable state;
- bounded remediation;
- isolated writers;
- no intermediate review/certification;
- convergence before final integration.

---

## 8. Context-window hygiene

### 8.1 Clean child contexts

Subagents should use isolated/clean context whenever the harness supports it. For Codex, prefer the equivalent of fork_turns=none for workers and Area Leads.

Do not copy the root's full conversation into each child.

### 8.2 Self-contained task packets

Each child receives only what it needs:

- Goal/run/lane identity;
- exact base SHA;
- expected head or parent state where relevant;
- exact task;
- authority/prohibitions;
- read paths;
- write paths or write domain;
- consumed interfaces;
- required tests;
- relevant problem IDs;
- artifact/state paths;
- model/reasoning requirement.

### 8.3 Compact handoffs

Do not return long prose, full diffs, long logs, or internal analysis to the parent.

A compact handoff should contain fields such as:

- STATUS;
- TASK/LANE;
- BASE_SHA;
- HEAD_SHA;
- CHANGED_PATHS;
- PUBLIC_INTERFACES_CHANGED;
- SHARED_SURFACES_TOUCHED;
- NEW_DEPENDENCIES;
- SCHEMA_OR_MIGRATION_CHANGES;
- TEST_ENTRYPOINTS;
- OPEN_PROBLEM_IDS;
- BLOCKER;
- STATE_PATH;
- CONSUMED_CONTRACT_REFS;
- PRODUCED_CONTRACT_DELTAS;
- UNPLANNED_SHARED_SURFACES;
- ASSUMPTION_CHANGES.

Detailed recoverable information belongs in Git/code/tests or machine-readable execution state.

A terminal root milestone also emits one compact `milestone-handoff.json` (or equivalent schema-bound artifact) containing the same cross-root integration fields plus exact test entrypoints and open Problem IDs. This is an integration input, not a narrative review memo.

### 8.4 Context Curator

A broad Goal may maintain a sibling Context Curator / State Curator.

The curator:

- is not a reviewer;
- does not judge code quality;
- does not certify;
- does not make canonical product decisions;
- reads machine state and compact worker results;
- deduplicates scheduling information;
- identifies READY/ACTIVE/BLOCKED/COMPLETE nodes;
- identifies free ownership surfaces;
- surfaces dependencies and problem IDs;
- produces a compact state summary for the root.

If the curator context becomes large, close it and create a fresh curator that reconstructs state from the repository.

---

## 9. Concurrency policy

### 9.1 No artificial fixed agent count

Do not set a mandatory number such as exactly 20 or exactly 40 children.

Instead:

> use as much useful concurrency as the current harness, dependency frontier, write ownership, and machine/runtime capacity safely allow.

A Goal should aggressively delegate whenever READY work exists.

If only five genuinely independent tasks are ready, use five.

If twenty are genuinely ready and the harness supports them, use twenty.

Do not keep slots idle while useful dependency-safe work exists.

Do not manufacture duplicate tasks merely to occupy slots.

### 9.2 Rolling frontier

Do not wait for artificial wave completion.

Operating loop:

1. discover READY work;
2. allocate ownership;
3. spawn;
4. while children run, continue scheduler/integration work;
5. when a child completes, verify its state;
6. integrate/adjudicate inside the milestone branch;
7. close the child;
8. unlock dependent work;
9. refill the freed slot immediately.

This is continuous rolling-frontier scheduling.

### 9.3 Slot saturation and backpressure

When all usable child slots are occupied:

- do not terminate productive children merely to satisfy a new task;
- keep newly READY work in the scheduler queue;
- prioritize critical-path unblocks over lower-value optional work when a slot opens;
- use long/event-driven waits rather than tight polling when the harness supports it;
- let the root perform only nondelegable scheduling/integration/verification work while waiting;
- immediately refill a slot after a terminal child is verified and closed.

The system optimizes useful throughput, not simultaneous-agent count.

### 9.4 Heavy resource constraints remain separate

Large logical agent counts do not create permission for unlimited heavy model, FFmpeg, GPU/MPS, media, or external-resource execution.

Resource leases remain governed by actual measured capacity and current authority.

Root-writer concurrency and heavy-resource concurrency are different budgets. A later canonical resource-policy update must express them separately so that four lightweight isolated root writers do not accidentally imply four concurrent heavy model/FFmpeg jobs.

---

## 10. Minimal durable execution state

### 10.1 No documentation treadmill

Normal execution should not generate:

- review memos;
- certification memos;
- recertification records;
- long audit narratives;
- per-agent Markdown essays;
- redundant status documents.

### 10.2 Machine-oriented state: ephemeral vs durable

Do not force all scheduler telemetry into Git.

Use two state classes:

**Ephemeral scheduler state**
- active queues;
- transient slot assignments;
- polling/wait state;
- disposable runtime diagnostics.
- may remain local/gitignored and may be reconstructed.

**Durable execution state**
- exact portfolio/Goal identity and authority;
- accepted root/lane heads;
- terminal handoffs;
- open/resolved Problem records needed by later work;
- unplanned shared surfaces and contract deltas;
- terminal blocker/Goal disposition;
- evidence required to reconstruct after session loss.
- must be committed on the owning execution/convergence branch before the relevant agent is closed.

Prefer compact machine-readable paths such as:

    .orchestration/
      portfolios/<portfolio-id>/manifest.json
      goals/<goal-id>/handoff.json
      goals/<goal-id>/lanes/<lane-id>.json
      problems/<goal-id>/<problem-id>.json
      convergence/<portfolio-id>/...

Avoid one global append-only JSONL file shared by all parallel roots; it would manufacture merge conflicts. Shard durable records by portfolio/Goal/problem identity and generate indexes later if useful.

The exact schema may be finalized in the later implementation plan.

These files are scheduler/execution memory, not product architecture documentation.

They may remain execution-branch-local until convergence determines which durable records must travel with the integrated execution history.

### 10.3 Git remains the primary engineering memory

Code history belongs in commits.

Tests prove behavior.

Machine state tracks scheduler/problem state.

Long narrative reasoning is not required for routine execution.

---

## 11. Problem Catalog

### 11.1 Purpose

The project needs durable memory for failures without allowing debugging to consume an entire Goal indefinitely.

The Problem Catalog records:

- unresolved problems;
- resolved problems;
- failed remediation approaches;
- successful remediation approaches;
- evidence;
- approaches deliberately not attempted and why;
- recurrence signatures;
- dependencies and impact.

The catalog is a troubleshooting knowledge base and scheduling input, not a review document.

### 11.2 Problem dimensions

Use two independent dimensions.

Severity:

- LOW;
- MEDIUM;
- HIGH;
- CRITICAL.

Frontier impact:

- NON_BLOCKING;
- TASK_BLOCKER;
- AREA_BLOCKER;
- GOAL_BLOCKER.

Severity describes consequence.

Frontier impact describes scheduler effect.

A HIGH/NON_BLOCKING issue and a MEDIUM/GOAL_BLOCKER issue are both possible.

### 11.3 Problem record state and identity

Each Problem receives a stable unique ID within its Goal/portfolio namespace and a status such as:

- OPEN;
- INVESTIGATING;
- REPAIRING;
- RESOLVED;
- DEFERRED;
- SUPERSEDED.

Root-cause state should be explicit, for example:

- UNKNOWN;
- HYPOTHESIZED;
- EVIDENCE_SUPPORTED;
- CONFIRMED_FOR_CURRENT_REPAIR;
- DISPROVEN.

Do not call a root cause confirmed merely because one agent proposed it.

### 11.4 Recommended fields

Each problem record should contain enough structured data to answer:

- what failed;
- what was expected;
- what was observed;
- where it occurred;
- when it first/last occurred;
- current severity;
- current frontier impact;
- root-cause state;
- known root cause, if established;
- evidence refs;
- each remediation generation:
  - hypothesis;
  - action;
  - result;
  - tests;
  - commit/ref;
  - failure reason;
- plausible approaches not attempted;
- why each was not attempted;
- successful resolution, if any;
- proof of resolution;
- reusable solution notes;
- recurrence signature;
- blocked descendants/dependencies;
- next action.

### 11.5 Resolved problems are retained

Do not delete a resolved problem.

A resolved record captures reusable engineering knowledge:

- symptom;
- cause;
- failed attempts;
- working solution;
- proof;
- relevant commit/tests.

Future workers should search the catalog before repeating expensive debugging.

---

## 12. Bounded autonomous remediation

### 12.1 A failure is not automatically a Goal boundary

Unexpected failure enters Superpowers systematic-debugging.

Before behavior-changing mutation:

1. reproduce or characterize the failure;
2. preserve evidence;
3. form a root-cause hypothesis;
4. add or identify a RED regression when applicable;
5. apply the smallest justified fix;
6. verify focused GREEN behavior;
7. update the Problem Catalog.

### 12.2 Remediation generation

A remediation generation is not every command or experiment.

One generation means approximately:

root-cause hypothesis -> evidence -> concrete fix -> verification result.

Logs, source inspection, or multiple diagnostic commands supporting the same hypothesis are part of one generation.

### 12.3 Default budget

Default maximum:

three evidence-supported failed remediation generations for the same load-bearing problem/root-cause family.

A generation counts only when it contains:

- an evidence-supported root-cause hypothesis or repair target;
- a concrete behavior-changing repair;
- an observed verification result.

A typo, invalid command, broken test harness, or mechanically malformed patch that never exercised the intended repair does not consume a remediation generation; it is attempt noise and should still be recorded when useful.

Do not reset the three-generation budget by merely renaming the same hypothesis. A genuinely new root-cause family may begin a new bounded budget only when new evidence materially changes the diagnosis and the Problem record captures that transition.

Authorization, source-preservation, evidence-integrity, or destructive-safety failures bypass ordinary retry optimism: they fail closed and cannot be retried into a wider scope.

Do not guess a fourth repair merely because agents remain available.

After exhaustion:

- record the complete problem state;
- park only the affected task/area descendants;
- continue every other dependency-safe frontier;
- terminate the incident workers;
- surface the problem at Goal completion.

If the unresolved problem is a GOAL_BLOCKER and no useful READY work remains, terminate with the appropriate blocker.

### 12.4 Incident Cell

Simple failures may use one debugger.

Hard failures may spawn a focused incident cell such as:

- reproducer;
- code-path investigator;
- environment/state investigator;
- Git/history/problem-catalog investigator.

These are repair agents, not reviewers.

After evidence converges, use a fresh repair worker for the actual behavior-changing fix when useful.

### 12.5 Problem Resolution Goals

Do not open a cleanup Goal on a fixed cadence such as after every Goal or every third Goal.

Open a dedicated Problem Resolution Goal when evidence shows it is worthwhile, for example:

- an unresolved problem becomes a prerequisite for the next milestone;
- the same problem recurs across Goals;
- several problems share one root-cause family;
- HIGH blockers accumulate enough to reduce useful frontier throughput;
- no further product work is READY without resolving the cataloged blockers.

This keeps maintenance event-driven rather than bureaucratic.

---

## 13. Unplanned overlap during parallel roots

### 13.1 Expected ownership is guidance plus isolation

Each parallel root gets an expected write domain.

Ownership is tracked at three levels where applicable:

- **exclusive implementation paths** — expected to be written by only one active root;
- **shared-contract surfaces** — public API/schema/config/lockfile/registry surfaces that multiple roots may consume and must treat as frozen assumptions unless a delta is declared;
- **generated/derived surfaces** — outputs that should not become coordination primitives.

A root that must alter a shared-contract surface records both `UNPLANNED_SHARED_SURFACE` and a structured `PRODUCED_CONTRACT_DELTA`, including known consumers and compatibility impact.

However, real implementation may reveal a necessary shared surface that planning did not predict.

The root should not automatically stop merely because it must touch a shared interface.

Instead it records an explicit unplanned shared-surface event, including:

- path/interface;
- reason;
- exact change;
- affected assumptions;
- dependent milestone if known.

A suitable machine field is UNPLANNED_SHARED_SURFACE.

### 13.2 Roots remain isolated

Even when two roots modify the same path:

- each modification occurs only in that root's own worktree/branch;
- neither root reads or mutates the other's working tree as a coordination mechanism;
- neither root attempts cross-branch repair;
- no premature merge is performed merely to make the branches agree.

Actual reconciliation is deferred to portfolio convergence after the execution blocks complete.

---

## 14. Portfolio convergence after parallel blocks

### 14.1 Do not merge immediately

After parallel milestone roots complete, the next step is not automatic merge.

Default convergence phases are:

1. ANALYZE ACTUAL OVERLAPS;
2. DESIGN RESOLUTIONS;
3. EXECUTE REMEDIATIONS;
4. INTEGRATE.

These correspond conceptually to the owner's illustrative E/F/G/H model, but the labels are not fixed identities.

### 14.2 Phase 1 — Convergence Analysis

Use a fresh root Codex when the portfolio is large enough to benefit from a clean context.

This root receives the exact completed branch heads and terminal milestone handoffs.

Its job is read-mostly analysis of product branches, not merge. It may write only its own convergence-state branch/artifacts.

It may use many subagents to inspect:

- per-branch changed paths;
- same-file overlap;
- public API/interface changes;
- schema/config changes;
- dependency changes;
- assumptions made by one branch about another subsystem;
- semantic conflicts that Git would not report;
- test/fixture contract interactions;
- problem-catalog interactions;
- migration/order constraints;
- likely integration ordering;
- consumed-contract reference vs produced-contract delta mismatches;
- exported symbol/signature changes;
- schema compatibility and migration ordering;
- dependency/lockfile conflicts;
- CLI/config behavior conflicts;
- test-fixture assumptions;
- temporal/provenance/evidence-domain semantics;
- unresolved Problem interactions;
- cases where Git reports no textual conflict but two branches encode incompatible assumptions.

A practical semantic-conflict matrix should be derived from each root's changed paths, public interfaces, consumed contracts, produced deltas, shared surfaces, dependency changes, migrations, tests, and open Problems.

It records the findings on its own convergence branch/state surface.

It does not merge milestone branches merely because analysis is complete.

### 14.3 Phase 2 — Resolution Design

For substantial overlap, prefer a fresh root context.

It consumes the actual convergence findings and determines:

- which branch semantics should dominate;
- whether both changes can coexist;
- whether a shared interface needs a reconciled form;
- exact remediation tasks;
- dependency order;
- which fixes can run in parallel;
- which areas must remain serialized.

For trivial convergence findings, Phase 1 and Phase 2 may be combined. Do not force an extra root when there is no context or reasoning benefit.

### 14.4 Phase 3 — Remediation Execution

A fresh execution root may implement the agreed convergence fixes in an isolated reconciliation worktree/branch.

Use the same execution-first rules:

- many useful subagents;
- TDD;
- rolling frontier;
- bounded debugging;
- Problem Catalog;
- no reviewer/certifier swarm.

### 14.5 Phase 4 — Integration

Only after actual overlaps and required remediations are understood should an integration root combine the milestone branches in dependency-safe order.

The order is derived from the actual dependency/shared-contract graph, not alphabetical branch order or completion time.

The integration root:

- works on a separate integration branch/worktree;
- does not merge to canonical main;
- performs the actual branch integration;
- resolves remaining mechanical conflicts;
- runs integration/regression tests;
- verifies the combined capability;
- leaves main unchanged.

Final main integration remains a later explicit owner decision.

### 14.6 Phase boundaries are adaptive

Do not rigidly create four roots for every convergence.

Large/complex convergence:
- separate fresh roots are preferred for context cleanliness.

Small/trivial convergence:
- phases may collapse safely.

The default principle is fresh context when analysis, solution design, remediation, and integration are each substantial enough to contaminate or overload the previous context.

---

## 15. Root-to-root communication

Parallel milestone roots do not coordinate by chatting with one another.

Cross-root communication occurs through:

- Git commits;
- exact SHAs;
- machine-readable execution state;
- Problem Catalog entries;
- explicit interface/shared-surface metadata.

This prevents hidden context coupling and makes later reconciliation reproducible.

---

## 16. Remote/local bootstrap before execution

Before the first major execution portfolio begins, run a dedicated repository convergence Goal.

Goal 0 must reconcile repository state without also becoming the branch-hygiene campaign. Fetching/pruning remote-tracking refs is allowed as ordinary non-destructive Git synchronization; deleting historical project branches is not.

Its purpose is to make the local execution environment and remote repository state mutually understood without destructive synchronization.

Required behavior:

- inventory repository root, worktrees, branches, tags/refs, dirty state;
- fetch remote refs non-destructively;
- identify local-only commits;
- identify remote-only commits;
- fast-forward only when safe;
- safely push authorized ahead-only execution/planning branches when the Goal permits;
- preserve divergence rather than reset/rebase/force;
- preserve unknown dirty/untracked state until attributed;
- do not upload secrets, caches, media, build outputs, virtual environments, or unrelated scratch;
- verify canonical main/local main relationship;
- ensure required historical objects/branches for upcoming execution are locally available;
- finish with explicit local/remote state.

Prohibited during this bootstrap unless separately authorized:

- hard reset;
- git clean;
- force push;
- destructive branch/worktree deletion;
- reflog expiration/pruning;
- silent merge/rebase of divergence.

This bootstrap is Goal 0 conceptually, but the exact Goal text will be created later.

---

## 17. Superpowers routing for the execution epoch

Use Superpowers by trigger, not as a checklist.

### Portfolio/orchestration design
- brainstorming;
- writing-plans only after the design/spec is owner-approved.

### Isolated implementation
- using-git-worktrees.

### Independent READY work
- dispatching-parallel-agents.

### Behavior changes
- test-driven-development.

### Unexpected failures
- systematic-debugging.

### Completion assertions
- verification-before-completion.

### Later planning
- writing-plans only after this architecture and the canonical policy transition are owner-approved.

When writing-plans is later used, repository/owner instructions override its generic execution handoff where that handoff would reintroduce per-task reviewer gates. The implementation plan must point to the approved Execution Portfolio execution method rather than silently selecting an incompatible default.

### Explicitly deferred during ordinary execution
- requesting-code-review;
- receiving-code-review;
- review/certification workflows.

The existing subagent-driven-development skill contains review behavior that conflicts with the owner-directed final-only review policy. Therefore do not invoke it as the governing end-to-end execution workflow during this epoch unless a later owner-approved adaptation removes the intermediate review requirement. Its useful delegation concepts may be reflected by the repository's own hierarchical rolling-frontier policy without importing the review loop.

---

## 18. Expected remaining execution blocks

Do not assign fake percentages to project completion.

Current repository evidence supports capability-oriented blocks instead.

Provisional blocks for later portfolio planning include:

### Block A — Gate-0 Revision-18 V7 mechanical implementation
Implement the already approved Revision-18 V7 code scope, adapting terminal workflow to the current owner direction that intermediate review/certification is deferred.

### Block B — Semantic core productization
Move the persistent local semantic-index capability from experiment-shaped coupling toward stable product-owned source interfaces and lifecycle behavior.

### Block C — Multi-source/archive operational path
Generalize bounded one-file proof toward authorized multi-source inventory/index/incremental update/resume-recovery behavior without assuming protected/archive execution authority.

### Block D — Retrieval capability completion
Complete product-facing natural-language/text retrieval and appropriate seams for later image-reference/video-reference retrieval while preserving semantic timestamps as non-binding candidate evidence.

### Block E — Editorial/edit pipeline completion
Generalize candidate -> measured refinement -> human decision -> versioned plan -> safe non-production render/QC integration for real product use.

### Block F — Reliability/scale/restart
Add only reliability mechanisms justified by measured workload/failure evidence: restart, checkpoint, caching/index lifecycle, recovery, performance work, and other mechanisms as proven necessary.

### Block G — Production boundary
Production export/render, protected/archive expansion, provider/cloud/model activity, deployment, and Gate promotion remain separately authorized future boundaries, not automatically included in execution Goals.

These names and groupings are provisional. The later portfolio plan must inspect actual code dependencies and may split, combine, or reorder them.

---

## 19. Main integration policy

Canonical main is not a rolling development branch for this execution epoch.

Rules:

- no milestone root merges to main;
- no convergence analyst merges to main;
- no resolution designer merges to main;
- no remediation root merges to main;
- no integration root merges to main automatically;
- main integration occurs only after the owner has inspected the integrated execution state and explicitly authorizes it.

Repository-wide process-policy updates may still be placed on main only through a separately explicit owner-approved process.

---

## 20. Owner interaction model

The desired owner workflow is low-frequency and milestone-oriented.

Do not return merely because:

- one worker completed;
- one test failed;
- one ordinary bug was found;
- one child needs replacement;
- one internal dependency opened;
- one repair attempt failed.

Continue autonomously while useful authorized READY work remains.

Return to the owner for:

- milestone completion;
- authorization boundary;
- irreversible/destructive requirement;
- external credential/user interaction requirement;
- technical exhaustion that leaves no useful independent frontier;
- genuine architecture/product decision that cannot be resolved without changing higher authority.

---


## 21. Canonical policy transition required before execution

The refined design exposes a real transition problem: current main contains mutually incompatible process rules. Execution must not begin while fresh agents can legitimately choose either the old or new behavior.

### REQUIRED_BEFORE_EXECUTION

The later controlled main-promotion task should reconcile at least:

- `AGENTS.md` — remove generation-specific Codex child pinning, establish the approved LUNA/medium resolution rule, replace intermediate certification defaults for this epoch, permit bounded nested delegation when runtime capability is verified, and point to the execution-portfolio policy;
- `docs/INDEX.md` — make the governing execution-policy reading order unambiguous;
- `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md` — create the currently referenced-but-missing canonical execution policy from the owner-approved refined design;
- `docs/architecture/SUBAGENT_LANE_PROTOCOL.md` — transition from mandatory Markdown lane memos/main-centric durability to compact machine state, execution-branch integration, optional verified nested delegation, stale-base handling, and final-only review semantics for this epoch;
- `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md` — remove the remaining generation-specific model pin and ordinary-development review requirements, add multi-root branch isolation, portfolio anchor/worktree administration, and execution-first completion semantics;
- `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md` — remove the older implication that accepted child work is normally integrated/pushed to canonical main during every turn; preserve main synchronization/observation while making execution-branch durability primary during portfolio Goals;
- `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` — record the new current execution epoch and next action after policy promotion so fresh sessions do not restart old Gate/review frontiers;
- `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md` — replace the missing-protocol reference with the now-real policy and reconcile the older one-root/four-Gate topology text with the approved execution portfolio;
- `docs/portfolio/portfolio-v1/resource-policy-v2.yaml` — distinguish root-writer concurrency from heavy-resource concurrency and remove ambiguity that would incorrectly treat the historical two-controller Gate budget as the permanent limit for independent lightweight Codex milestone roots.

### RECOMMENDED_BEFORE_EXECUTION

- `docs/portfolio/portfolio-v1/DEEPSEEK_HARNESS_CONTROLLER_PROFILE.md` — align its Gate-centric role/model text with the common execution-portfolio architecture before DeepSeek is used as an execution root. It becomes REQUIRED before the first DeepSeek execution under this model.

### DEFER_UNTIL_AFTER_FIRST_EXECUTION

- optional optimizations to machine-state schemas/indexes that are not needed for Goal 0 or the first portfolio;
- any additional concurrency tuning that should be based on measured contention/throughput rather than speculation;
- final review/certification policy for the completed product epoch.

### HISTORICAL_ONLY / DO_NOT_TOUCH

Do not rewrite:

- historical audits/reviews/certification records;
- old lane memos and historical agent-run evidence;
- historical model provenance showing `gpt-5.6-luna` where that was actually used;
- frozen Gate designs/specifications merely to modernize orchestration wording;
- `docs/project/00_PROJECT_CHARTER.md` unless durable mission/evidence/Gate invariants themselves change.

### Promotion discipline

The main-promotion task should be one bounded process-policy change with its own exact diff and verification. It must not merge product implementation branches or perform the 177-branch cleanup.

After promotion, fresh agents should have one unambiguous current execution policy.

---

## 22. Fresh-session recovery contract

A fresh root must be able to recover without old chat context.

Minimum recovery chain:

1. canonical `AGENTS.md` and execution-policy reading order;
2. current project handoff;
3. exact portfolio manifest/anchor SHA;
4. assigned Goal packet and root branch/worktree identity;
5. durable Goal/lane handoff state;
6. Problem records relevant to the Goal;
7. exact Git heads and remote durability state;
8. current resolved model identity and resource leases.

No active agent identity is inferred from UI history alone.

If durable state and Git disagree, Git plus the higher repository/owner authority wins and the discrepancy is recorded before new work.

---

## 23. Future branch-hygiene prerequisites — separate task only

The later branch-reduction task should classify branches from evidence, never from age/name alone.

For each local/remote branch, collect where observable:

- branch head SHA;
- local vs remote presence;
- active worktree attachment;
- open PR/issue relationship;
- whether head is reachable from current main or an accepted integration/preservation ref;
- count/list of commits unique to the branch relative to appropriate current refs;
- references from current authority/handoff/spec/plan/run evidence;
- historical/audit/recovery significance;
- supersession/replacement relation;
- whether a preservation tag/ref is needed before deletion;
- whether dirty/uncommitted work exists in an attached worktree;
- whether branch deletion would orphan evidence needed for current/future work.

Candidate dispositions for that later task may include:

- KEEP_ACTIVE;
- KEEP_AUTHORITY_OR_EVIDENCE;
- PRESERVE_THEN_DELETE_CANDIDATE;
- DELETE_CANDIDATE;
- UNKNOWN_NEEDS_INVESTIGATION.

No deletion occurs in the current design-refinement task.

---

## 24. Six-Cycle iterative refinement applied to this design

### Cycle 1 — Authority / scope / owner intent

Material gap found:
the proposed execution-first policy contradicted several still-canonical main rules. Treating the planning branch as if it silently superseded them would let fresh agents choose incompatible behaviors.

Refinement:
added an explicit no-execution-before-policy-promotion gate, retained all protected/provider/model-download/production/destructive boundaries, and kept verification distinct from review.

Regression check:
the design creates no implementation authority and still requires explicit owner decisions for restricted runtime scope and main integration.

### Cycle 2 — Internal consistency / repository alignment

Material gaps found:
`THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md` is referenced by current handoff text but absent; current main also retains generation-specific Luna pinning, Markdown lane memos, main-centric integration language, disabled nested delegation, and certification defaults.

Refinement:
defined the exact canonical policy-transition surface and a version-agnostic per-Goal Luna resolution freeze.

Regression check:
historical audits/model provenance remain untouched; only current process-policy files are candidates for later promotion.

### Cycle 3 — Throughput / context / subagent architecture

Material gaps found:
multi-root linked worktrees can still race on shared worktree/ref administration; rolling children can return from stale bases; nested delegation may not be supported by every harness; slot saturation behavior was unspecified.

Refinement:
added Portfolio Bootstrap/Worktree Admin serialization, portfolio anchor/manifest, stale-base acceptance rules, nested-delegation flattening fallback, explicit backpressure behavior, and separate root-writer vs heavy-resource budgets.

Regression check:
no fixed agent quota was introduced and useful concurrency remains adaptive.

### Cycle 4 — Failure / Problem Catalog / autonomous repair

Material gaps found:
one global JSONL would create artificial cross-root merge conflicts; problem state/root-cause confidence were underspecified; the three-generation budget could be gamed or consumed by malformed attempts; completion-with-deferred-problems lacked safety criteria.

Refinement:
sharded Problem records by Goal/problem ID, separated ephemeral from durable state, added explicit Problem/root-cause states, tightened remediation-generation accounting, and constrained GOAL_COMPLETE_WITH_DEFERRED_PROBLEMS.

Regression check:
resolved knowledge is retained without forcing narrative Markdown or an always-growing shared file.

### Cycle 5 — Cross-root convergence / integration / main hygiene

Material gaps found:
changed-path comparison alone cannot find semantic contract conflicts; integration ordering was underspecified; current main does not yet provide one coherent process policy.

Refinement:
added consumed-contract/produced-delta handoffs, semantic-conflict matrices, dependency-derived integration order, read-mostly convergence analysis, explicit main-promotion classifications, and future branch-hygiene prerequisites.

Regression check:
parallel roots still remain isolated and no automatic main merge was introduced.

### Cycle 6 — Simplicity / YAGNI / executability / recovery

Material gap found:
adding portfolio coordination could itself become a bureaucracy.

Refinement:
kept the curator optional, kept three tiers as a preferred maximum with a flattening fallback, used one compact portfolio manifest plus sharded durable state, left exact schemas/locking mechanisms to the later implementation plan, and defined a minimal fresh-session recovery chain.

Regression check:
the design adds only controls that prevent concrete context, Git, concurrency, recovery, or integration failure modes; it does not require new review/certification documents.

---

## 25. Design invariants

The following should be treated as load-bearing for the later implementation plan:

1. execution-first until major remaining code is complete;
2. no intermediate reviewer/certifier swarms;
3. milestone-sized Goals;
4. multiple parallel root Codex sessions when blocks are dependency-safe;
5. one isolated branch/worktree per root;
6. no root merges to main;
7. hierarchical Root -> Area Lead -> Worker delegation;
8. maximum useful concurrency, no artificial agent quota;
9. clean child contexts and compact handoffs;
10. finished children close and slots recycle;
11. rolling-frontier scheduling;
12. machine-readable execution memory, not documentation churn;
13. durable Problem Catalog with failed/successful/not-attempted solution history;
14. maximum three root-cause-confirmed failed remediation generations per load-bearing problem by default;
15. park only affected DAG descendants and continue independent work;
16. record unavoidable unplanned shared surfaces;
17. analyze actual branch overlap before integration;
18. separate convergence analysis/resolution/remediation/integration when context or complexity justifies it;
19. later integration occurs on an isolated branch, not main;
20. main integration is an explicit owner decision;
21. Codex child policy is version-agnostic Luna family + medium reasoning resolved against the actual runtime allowlist;
22. final review/certification is a later separate epoch;
23. execution does not begin until contradictory canonical process policy is reconciled on main;
24. one portfolio anchor/manifest binds parallel-root identities and assumptions when useful;
25. Git worktree/ref administration is serialized even when substantive roots run concurrently;
26. every child handoff binds its exact base and stale candidates are checked before integration;
27. shared-contract deltas are explicit rather than silently assumed;
28. durable Problem state is sharded to avoid manufactured cross-root conflicts;
29. one concrete Luna/medium resolution is frozen per Goal;
30. GOAL_COMPLETE_WITH_DEFERRED_PROBLEMS cannot hide unresolved Goal blockers or critical safety/integrity defects;
31. every completed root emits a compact integration-oriented milestone handoff;
32. fresh sessions reconstruct from canonical policy + manifest + Git + durable state, not chat history.

---

## 26. Next design step

This document is intentionally a design/specification, not the executable portfolio plan.

After owner approval of this refined design:

1. perform one bounded canonical-main process-policy promotion using the classifications in §21;
2. independently verify that fresh-session authority is coherent and the missing throughput protocol now exists;
3. perform the later separate branch-hygiene task only after its own owner-approved prompt/plan;
4. define Goal 0 repository convergence in exact operational terms;
5. verify the then-current repository state after Goal 0;
6. inventory remaining executable capability gaps;
7. produce the Execution Portfolio DAG and optional portfolio anchor manifest;
8. identify the first set of truly parallel milestone roots;
9. assign exact expected ownership/shared-contract domains;
10. identify hard/soft dependencies and heavy-resource constraints;
11. define completion tests/capability outcomes;
12. prepare the owner-facing Codex Goal packets;
13. leave convergence-phase Goal details adaptive until real branch heads exist.

No Codex execution should be started from this document alone.
