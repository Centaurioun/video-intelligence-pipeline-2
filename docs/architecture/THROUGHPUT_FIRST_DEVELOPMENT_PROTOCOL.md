# Throughput-First Development Protocol

**Status:** CURRENT REPOSITORY PROCESS CONTRACT  
**Scope:** Codex and DeepSeek repository-development Goals.  
**Authority:** current owner-approved execution-portfolio policy.  
**Current resource policy:** `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`  
**Does not authorize:** product scope expansion, protected/archive-media execution, provider/cloud activity, model downloads, production export, Gate promotion, destructive Git, or canonical-main integration.

This protocol governs ordinary repository execution when it conflicts with older process wording. Historical audits, Gate records, lane evidence, and model provenance remain historical evidence; they are not rewritten merely to match this epoch.

## 0. 2026-10-03 Remaining-Work Atlas override

For ordinary remaining-project execution, the following rules supersede conflicting older wording in this protocol:

- maintain three concurrent rolling frontiers: **BUILD**, **VERIFY**, and **REPAIR**;
- a BUILD_GREEN H3 may unlock SOFT-dependent downstream BUILD while its VERIFY work continues;
- numeric chapter/H1 order does not create a dependency by itself;
- later H3 nodes may start whenever their actual dependency/ownership/authority/resource predicates are satisfied;
- every H3 feature candidate enters an asynchronous feature-level code-review lane before convergence/current-main integration, but that review does not block unrelated BUILD absent a declared HARD_VERIFY dependency;
- ordinary H3 execution uses the repository-native parallel portfolio: `dispatching-parallel-agents` for independent work, TDD for behavior changes, systematic-debugging for failures, and verification-before-completion for claims;
- stock `subagent-driven-development` is exceptional (`PER_TASK_REVIEW_REQUIRED`) rather than the default merely because subagents are used;
- running descendants invalidated by an upstream consumed-contract delta become `STALE_IN_FLIGHT` and are non-integrable until reconciled;
- verification/review evidence binds the exact immutable candidate generation it observed;
- top-level/root concurrency has no fixed four-root ceiling; use the maximum useful dependency-safe capacity without manufactured work or overlapping writers;
- resource leases come from resource-policy v5; HEAVY_CPU/FFMPEG begin at two concurrent ordinary-development jobs, calibrate to three when stable/useful, and fail soft by resource class;
- Launch Delta Reconciliation updates only affected prompt overlays/cores and does not reopen settled architecture;
- high-volume worker diagnostics remain file-backed; compact receipts carry only scheduler/integration facts.

The owner explicitly authorized the process/policy promotion needed to make these rules current. This does not widen protected-media, provider/cloud, production-export, Gate-promotion, destructive-Git, or other separately bounded authority.

## 1. Execution epoch

The repository is in an **execution-first** development epoch.

Normal agent capacity is allocated to:

- **BUILD** — product code, tests, fixtures, schemas/configuration genuinely required by the code;
- **ENABLE** — adapters, interfaces, migrations, tooling, data paths, and prerequisites that unlock BUILD work;
- **REPAIR** — systematic debugging and bounded fixes for failures discovered during execution.

Intermediate REVIEW / CERTIFY / RECERTIFY swarms are not the ordinary development loop.

The following remain required engineering checks where applicable:

- test-driven development for behavior changes;
- focused unit/integration/regression tests;
- systematic-debugging for unexpected failures;
- deterministic/static checks;
- source-preservation and temporal/PTS correctness checks;
- secret/Git safety checks;
- verification-before-completion.

Formal review/certification is a later owner-directed epoch after major remaining executable work is substantially complete, unless the owner explicitly requests it earlier.

## 2. Goal semantics

A user-facing Goal is a **product milestone**, not a micro-task.

A Goal should normally:

- contain multiple scheduler nodes or execution fronts;
- support sustained useful delegation;
- produce a materially new working capability;
- continue through ordinary child completions and ordinary fixable failures;
- return only at milestone completion or a genuine boundary.

Recommended terminal states:

- GOAL_COMPLETE;
- GOAL_COMPLETE_WITH_DEFERRED_PROBLEMS;
- GOAL_BLOCKED_AUTHORIZATION;
- GOAL_BLOCKED_EXTERNAL_PREREQUISITE;
- GOAL_BLOCKED_TECHNICAL_EXHAUSTION;
- GOAL_BLOCKED_DESTRUCTIVE_OR_IRREVERSIBLE_ACTION;
- GOAL_BLOCKED_ARCHITECTURE_DECISION.

GOAL_COMPLETE_WITH_DEFERRED_PROBLEMS is valid only when:

- the declared capability works under its acceptance checks;
- no unresolved problem has frontier_impact=GOAL_BLOCKER;
- no unresolved CRITICAL problem threatens source preservation, evidence/temporal correctness, authorization/security boundaries, data integrity, or the declared capability;
- every deferred problem is durably recorded with downstream impact;
- blocked descendants are explicit.

## 3. Portfolio-level parallel roots

Large remaining work is decomposed by actual capability/dependency boundaries, not by an artificial fixed number of roots.

Multiple root Codex/DeepSeek sessions may execute concurrently when the Execution Portfolio DAG permits it.

Each root receives:

- one milestone Goal;
- exact frozen base/anchor SHA;
- unique root identity;
- unique execution branch/worktree;
- expected write domain;
- frozen shared-contract references;
- prohibited scope;
- completion criteria;
- resource constraints.

Roots:

- never write directly to canonical main;
- never merge sibling root branches;
- never repair sibling working trees;
- may non-force checkpoint only their own assigned execution branch when authorized;
- communicate cross-root state through Git and durable machine-readable artifacts, not hidden chat.

## 4. Portfolio Bootstrap and anchor

Before a substantial multi-root wave, one serialized **Portfolio Bootstrap / Worktree Admin** operation should establish:

- current canonical/remote state;
- portfolio ID;
- exact authority/base SHA;
- optional immutable execution/portfolio-<id>-anchor SHA;
- root IDs;
- root branches/worktrees;
- Goal identities;
- PARALLEL_CLASS;
- expected write domains;
- frozen shared-contract refs;
- heavy-resource constraints;
- resolved executor/model policy;
- required terminal milestone handoff.

If a small execution does not benefit from a committed manifest, the same data may live in owner-approved Goal packets. Do not create ceremony-only artifacts.

Shared worktree/ref topology changes are serialized.

No root may independently create/delete/prune sibling worktrees, move sibling refs, or rewrite the frozen anchor.

## 5. Portfolio DAG

Each milestone block records:

- milestone ID;
- capability outcome;
- exact base SHA;
- PARALLEL_CLASS = INDEPENDENT | SOFT_DEPENDENCY | HARD_DEPENDENCY;
- expected write domain;
- consumed shared contracts;
- prohibited scope;
- completion tests/observable outcome;
- known Problem dependencies.

Only dependency-safe blocks run simultaneously.

Planning should prevent obvious overlap but must not pretend zero overlap can be guaranteed.

## 6. Shared-contract discipline

Before root dispatch, identify frozen shared-contract surfaces such as:

- public APIs;
- schemas;
- common configuration;
- lockfiles/dependency contracts;
- central registries;
- CLI contracts;
- provenance/evidence/temporal types.

A root may discover that a shared-contract change is necessary.

It must then record:

- UNPLANNED_SHARED_SURFACE;
- PRODUCED_CONTRACT_DELTA;
- known consumers;
- compatibility impact;
- tests/fixtures affected.

A branch-local interpretation is never silently promoted to a global contract.

## 7. Root-agent role

The root is primarily:

- authority interpreter;
- Goal decomposer;
- dependency-DAG owner;
- scheduler;
- ownership allocator;
- milestone-branch integrator;
- incident adjudicator;
- remote-checkpoint owner when authorized;
- milestone verifier.

The root context is the control plane, not the workbench.

Substantive coding, tests, fixtures, focused research, debugging, migrations, and bounded refactors should be delegated whenever a clean ownership boundary exists.

## 8. Preferred delegation hierarchy

Preferred maximum hierarchy:

Root Orchestrator -> Area Lead -> Worker

Area Leads may spawn workers only when runtime capability is positively verified for:

- model/reasoning;
- isolation;
- persistence;
- ownership;
- closure.

Workers do not spawn another generation by default.

If compliant nested delegation is unavailable or unverifiable:

- do not block the Goal;
- flatten to Root -> Workers;
- Area Leads may remain planning/scheduling roles while the root performs the spawn operation.

No uncontrolled deeper delegation tree is permitted.

## 9. Codex model routing

Repository conceptual policy:

REQUESTED_MODEL_FAMILY=LUNA  
REQUESTED_REASONING=medium

At Goal start the root must:

1. inspect the actual supported spawn/model surface;
2. resolve the currently supported Luna-family concrete model identifier;
3. freeze one LUNA_MEDIUM_RESOLUTION for the Goal;
4. set both model and medium reasoning explicitly for eligible child spawns;
5. verify effective model/reasoning through supported metadata when possible;
6. persist requested/resolved/effective identities in compact Goal state.

Do not silently switch the concrete Luna generation inside one Goal.

If the resolved model becomes unavailable:

- stop new spawns;
- preserve active work;
- perform an explicit Goal-level re-resolution or obtain owner direction.

No silent fallback to a non-Luna family.

Historical records that truthfully mention older concrete Luna generations remain unchanged.

## 10. DeepSeek routing

This protocol is executor-neutral.

DeepSeek keeps its separately verified model/reasoning policy until the owner explicitly changes it.

Do not apply Codex LUNA rules to DeepSeek.

Both executors share:

- milestone Goals;
- rolling frontier;
- isolation;
- compact durable state;
- bounded remediation;
- no intermediate certification treadmill;
- convergence before canonical integration.

## 11. Clean contexts

Use isolated child context whenever the harness supports it.

### Native Portfolio roots — Native Codex Parallel Dispatch

**NATIVE_PARALLEL_DISPATCH_REQUIRED:** This procedure applies to substantial Codex Portfolio Goals; it does not grant work permission. `spawn_agent` is an in-process H4 subagent, not a fresh H3 root. `fork_thread` copies conversation history and is not the ordinary new-root path. Use `dispatching-parallel-agents` for independent H4 shards, not serial stock `subagent-driven-development` as the default scheduler.

1. **Discover:** Inspect currently exposed `list_projects`, `create_thread`, `list_threads`, `send_message_to_thread`, `wait_threads` and `read_thread` schemas, plus any resolver whose current schema explicitly accepts a pending `create_thread` client key. Resolve the current project and supported model/environment. Do not assume historical IDs, tool arguments or effective model values. `get_worktree_creation_status` accepts worktree-operation IDs, not `create_thread` client keys; do not misuse it as a thread resolver.
2. **Admit:** Compute independent READY tasks under exact grants, hard dependencies, exclusive paths and resource leases. Freeze each root's base SHA/tree, contracts, task packet, isolated worktree/branch expectation and durable handoff. Do not invent tasks to fill slots.
3. **Create before waiting:** Call fresh native `create_thread` for independently eligible H3 roots using the *currently supported* isolated-worktree target. Each self-contained first turn is READ_ONLY preflight. A pending `clientThreadId` is **not** a native `threadId`. Resolve it only through a current tool whose schema expressly accepts that `create_thread` key and returns an attributable native ID; corroborate the native identity against `list_threads` when possible. Never send, wait or read using a pending client key; thread inventory alone is not proof of client-key identity. If no compatible resolver exists, keep the lane BLOCKED/NOT_OBSERVED without retrying an ambiguous creation. Retry only after definitive failed creation and verified absence of its native thread. Start other independently eligible native roots before waiting for peer completion.
4. **Bind before writes:** Independently verify actual project, worktree/Git directory, branch or detached HEAD, HEAD/tree, base ancestry, cleanliness, task authority and exclusive ownership. Following Section 4, **Portfolio Bootstrap / Worktree Admin**, the serialized Worktree Admin may bind an authorized unique branch in a verified clean detached worktree; reverify afterward. A request or newly created thread is not branch binding. On mismatch, keep the worker READ_ONLY/BLOCKED; never modify a shared dirty checkout or use destructive Git.
5. **Run concurrently:** Grant a separate bounded write turn only to fully admitted roots; start eligible peers via `send_message_to_thread` before waiting. Monitor the running set via `wait_threads`, retrieve details via `read_thread`, and preserve actual host lifecycle/overlap evidence. Multiple thread IDs alone do not establish concurrent implementation.
6. **Verify and refill:** Independently verify handoff commits/trees, paths, contracts, tests and reviews; disposition each result, release ownership safely, recompute READY and refill legitimate capacity immediately while the Controller is active.
7. **Report compliance:** Record `NATIVE_THREAD_IDS`, `VERIFIED_WORKTREE_BINDINGS`, `READY_INDEPENDENT_TASK_COUNT`, `OBSERVED_CONCURRENT_ROOTS`, `ACTUAL_OVERLAP_EVIDENCE` and `DISPATCH_BLOCKER_IF_ANY` in the **terminal Goal/milestone handoff**. Append-only Portfolio dispatch events keep schema-valid per-lane evidence; do not add aggregate fields to their existing schema. Two eligible H3 roots processed only through sequential `spawn_agent` without a native attempt are **noncompliant**. Zero eligible parallel tasks are NOT_APPLICABLE. A documented native creation/binding failure is BLOCKED_WITH_EVIDENCE; unknown overlap is NOT_OBSERVED. Distinguish concurrent read-only diagnostics from concurrent source implementations.

The existing VIP V2 Portfolio manifest at `.orchestration/portfolios/vip-v2-execution-portfolio-20261009-v1/manifest.json` and its append-only dispatch events provide provenance, not task authority. Native creation, verified write binding, observed concurrency and unattended background scheduling are separate capabilities. There is no implied persistent scheduler after the live Controller turn ends.

A child task packet should contain only:

- portfolio/Goal/lane identity;
- exact BASE_SHA;
- authority/prohibitions;
- task;
- read scope;
- write scope/domain;
- consumed contracts;
- required tests;
- relevant Problem IDs;
- state/handoff paths;
- model/reasoning requirement.

Do not inherit the root's full transcript merely for convenience.

## 12. Compact handoffs

Child-to-parent handoff should include, as applicable:

- STATUS;
- PORTFOLIO/GOAL/LANE;
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

Do not paste full diffs, long logs, or full analysis into the parent context.

A terminal root milestone emits one compact milestone-handoff.json or schema-equivalent artifact containing the cross-root integration fields above.

## 13. Child lifecycle

When a child finishes:

1. commit authorized code/tests/durable state;
2. emit compact handoff;
3. parent verifies scheduler/integration facts;
4. parent dispositions the result;
5. child is closed/terminated where supported;
6. slot is immediately reusable.

Do not keep terminal children alive for knowledge retention.

The repository/Git state is memory.

## 14. Rolling frontier

Continuously:

1. discover READY work;
2. allocate ownership;
3. spawn all useful dependency-safe work;
4. integrate/adjudicate completed results;
5. close terminal children;
6. unlock dependent nodes;
7. refill capacity immediately.

Do not wait for artificial whole-wave barriers.

## 15. Concurrency

There is no mandatory child count.

Use the highest useful safe concurrency supported by:

- dependency graph;
- path/contract ownership;
- harness limits;
- machine/runtime capacity;
- heavy-resource leases.

Do not leave useful READY work idle merely to keep the root busy.

Do not manufacture duplicate work merely to occupy slots.

## 16. Slot saturation

When all usable child slots are occupied:

- queue newly READY work;
- do not terminate productive children to free a slot;
- prioritize critical-path unblocks when capacity opens;
- use event-driven/long waits instead of tight polling when supported;
- let the root do only nondelegable scheduler/integration/verification work;
- refill the first safe slot immediately.

## 17. Heavy-resource separation

Logical/root concurrency does not expand heavy execution authority.

Heavy local model, FFmpeg, GPU/MPS, or equivalent resource-intensive work remains separately lease-gated by the current resource policy.

A lightweight four-root portfolio does not imply four concurrent heavy jobs.

## 18. Child stale-base acceptance

Rolling execution means the milestone head may advance while a child works.

Every child handoff binds exact BASE_SHA.

Before acceptance, parent compares:

- child base;
- current milestone head;
- child changed paths;
- public/contract deltas;
- parent changes since child base.

Disposition:

- base current -> normal acceptance checks;
- stale but disjoint implementation and contract surfaces -> safe non-destructive integration plus focused/regression verification;
- stale with overlapping paths/contracts/migrations/assumptions -> do not blindly cherry-pick/rebase; park candidate and reconcile from current milestone head.

A child may not rewrite its reported base to conceal staleness.

## 19. Ephemeral vs durable execution state

Do not commit every scheduler event.

Ephemeral state may remain local/gitignored:

- active queue;
- slot assignment;
- polling/wait state;
- disposable runtime diagnostics.

Durable state includes:

- portfolio/Goal authority identity;
- accepted heads;
- terminal handoffs;
- open/resolved Problem records needed by later work;
- shared-surface/contract deltas;
- terminal blocker/Goal disposition;
- evidence needed for fresh-session recovery.

Preferred sharded shape:

.orchestration/
  portfolios/<portfolio-id>/manifest.json
  goals/<goal-id>/handoff.json
  goals/<goal-id>/lanes/<lane-id>.json
  problems/<goal-id>/<problem-id>.json
  convergence/<portfolio-id>/...

Do not use one global append-only problems.jsonl shared by all parallel roots.

## 20. Problem Catalog

Each Problem has stable identity and status such as:

- OPEN;
- INVESTIGATING;
- REPAIRING;
- RESOLVED;
- DEFERRED;
- SUPERSEDED.

Root-cause state may be:

- UNKNOWN;
- HYPOTHESIZED;
- EVIDENCE_SUPPORTED;
- CONFIRMED_FOR_CURRENT_REPAIR;
- DISPROVEN.

Each durable Problem record should capture enough structured information for:

- symptom;
- expected behavior;
- observed behavior;
- reproduction;
- evidence;
- environment/tool relevance;
- severity;
- frontier impact;
- root-cause state;
- remediation generations;
- failed approaches;
- successful approach;
- plausible approaches not attempted and why;
- tests;
- commits/SHAs;
- recurrence signature;
- affected dependencies;
- next action.

Resolved Problems are retained as engineering memory.

## 21. Severity and frontier impact

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

These are independent dimensions.

A safety/integrity-critical defect may not be hidden behind NON_BLOCKING.

## 22. Bounded remediation

Unexpected failure enters systematic-debugging.

Before behavior-changing repair:

1. reproduce/characterize;
2. preserve evidence;
3. form an evidence-supported root-cause hypothesis;
4. add/identify RED regression when applicable;
5. apply smallest justified fix;
6. verify GREEN;
7. update Problem record.

One remediation generation means:

evidence-supported hypothesis/repair target -> concrete behavior-changing repair -> observed verification result.

Invalid commands, malformed patches, or harness failures that never exercised the intended repair do not consume a generation.

Default maximum:

three evidence-supported failed remediation generations for the same load-bearing Problem/root-cause family.

Do not reset the budget merely by renaming the hypothesis.

A genuinely new root-cause family may receive a new bounded budget only when new evidence materially changes diagnosis and the Problem record captures that transition.

Authorization, source-preservation, evidence-integrity, or destructive-safety failures fail closed; retries may not widen scope.

After exhaustion:

- persist full Problem state;
- park only affected descendants;
- close incident workers;
- continue all other READY work.

If the unresolved problem is a GOAL_BLOCKER and no useful READY work remains, terminate with the appropriate blocker.

## 23. Incident Cells

Simple failure: one debugger may be enough.

Hard failure may use focused independent diagnostics such as:

- reproducer;
- code-path investigator;
- environment/state investigator;
- Git/history/Problem-Catalog investigator.

These are repair agents, not reviewers.

When useful, a fresh repair worker implements the evidence-supported fix.

## 24. Problem Resolution Goals

Do not create cleanup Goals on a fixed cadence.

Create a dedicated Problem Resolution Goal when evidence shows it is useful, for example:

- a Problem becomes prerequisite for next milestone;
- it recurs across Goals;
- multiple Problems share one root-cause family;
- blockers materially reduce READY frontier;
- no further useful product work remains without resolving them.

## 25. Unplanned overlap

Expected ownership has three useful categories:

- exclusive implementation paths;
- shared-contract surfaces;
- generated/derived surfaces.

If an unexpected shared path/interface must change:

- root changes only its own branch;
- record UNPLANNED_SHARED_SURFACE and PRODUCED_CONTRACT_DELTA;
- do not cross-merge sibling roots;
- do not repair sibling branches;
- defer actual reconciliation to convergence.

## 26. Convergence before integration

Completed parallel roots are not automatically merged.

Default conceptual phases:

1. CONVERGENCE ANALYSIS;
2. RESOLUTION DESIGN;
3. REMEDIATION EXECUTION;
4. INTEGRATION.

These phases may use separate fresh roots when context/complexity justifies it and may collapse when trivial.

## 27. Semantic conflict analysis

Convergence uses exact completed branch heads and terminal milestone handoffs.

It inspects:

- changed paths;
- same-file overlaps;
- consumed-contract refs vs produced deltas;
- exported symbols/signatures;
- schemas/migrations;
- dependencies/lockfiles;
- CLI/config semantics;
- test/fixture assumptions;
- provenance/evidence/temporal domains;
- open Problem interactions;
- semantic assumptions even when Git reports no textual conflict.

A clean Git merge is not proof of semantic compatibility.

Integration order follows the actual dependency/shared-contract graph, not branch alphabet or completion time.

## 28. Integration branch

Portfolio integration occurs on an isolated integration branch/worktree.

The integration root:

- combines branches in dependency-safe order;
- resolves remaining mechanical conflicts;
- runs integration/regression verification;
- leaves canonical main unchanged.

Canonical-main integration is a separate explicit owner decision.

## 29. Remote durability

Substantial Goals may checkpoint safe accepted work to their own execution branch through normal non-force pushes when authorized.

Do not push every child scratch branch by default.

A blocked Goal should still preserve safe accepted work remotely when possible.

Remote durability never authorizes main integration.

## 30. Fresh-session recovery

A fresh root reconstructs from:

1. AGENTS.md/current process reading order;
2. current project handoff;
3. exact portfolio manifest/anchor;
4. assigned Goal and root branch/worktree;
5. durable Goal/lane handoff state;
6. relevant Problem records;
7. exact Git heads/remote durability state;
8. current resolved model identity and resource leases.

If durable state and Git disagree, Git plus higher owner/repository authority wins and the discrepancy is recorded.

Do not rely on old chat context.

## 31. Branch hygiene

Historical branch reduction is a separate future task.

Ordinary Goal synchronization may fetch/prune remote-tracking refs non-destructively, but may not use the execution epoch as authority to delete historical project branches.

## 32. Main policy

Milestone roots never merge to canonical main.

Convergence analysis does not merge to main.

Resolution/remediation roots do not merge to main.

Integration roots do not merge to main automatically.

Canonical-main integration requires explicit owner authorization for the exact integrated state.

## 33. Superpowers routing

Use skills by trigger:

- architecture/design -> brainstorming;
- approved design to detailed plan -> writing-plans;
- isolated execution -> using-git-worktrees;
- independent READY work -> dispatching-parallel-agents;
- behavior changes -> test-driven-development;
- unexpected failures -> systematic-debugging;
- completion claims -> verification-before-completion.

Do not use generic subagent-driven-development as the governing workflow when it would reintroduce mandatory intermediate task-review gates contrary to current owner policy.

Do not invoke requesting-code-review / receiving-code-review as ordinary execution-loop steps during this epoch.

## 34. Owner-return boundaries

Do not return merely because:

- one child finished;
- one test failed;
- one ordinary bug appeared;
- one dependency opened;
- one repair attempt failed.

Return for:

- milestone completion;
- authorization boundary;
- irreversible/destructive requirement;
- external credential/user-interaction prerequisite;
- technical exhaustion with no useful independent frontier;
- genuine higher-level architecture/product decision.

## 35. Invariants

1. execution-first until major remaining executable work is complete;
2. final review/certification is later and separately owner-directed;
3. no root writes/merges canonical main;
4. one exact writer controller per branch;
5. maximum useful concurrency, not fixed quota;
6. three-tier hierarchy preferred, flat fallback allowed;
7. finished children close and slots recycle;
8. BASE_SHA is explicit and stale candidates are checked;
9. shared-contract deltas are explicit;
10. durable state is compact and sharded;
11. Problem Catalog retains failed/successful/not-attempted approaches;
12. bounded remediation prevents infinite debugging;
13. independent work continues around blocked descendants;
14. worktree/ref administration is serialized;
15. heavy-resource leases are separate from logical agent count;
16. actual overlap is analyzed before integration;
17. clean Git merge is not semantic compatibility proof;
18. fresh sessions recover from repository state, not chat;
19. branch cleanup is separate;
20. canonical-main integration is an explicit owner decision.

## 36. Routine development prerequisite recovery

Current machine-readable authority: `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`.

A routine missing development/test prerequisite is **ENABLE work**, not a terminal owner blocker by default.

Canonical flow:

`child prerequisite failure -> preserve exact failure evidence -> report to root -> root systematic-debugging classification -> recovery ladder -> rerun exact blocked command -> behavioral RED/fix/GREEN where applicable -> park/escalate only if no authority-compliant recovery remains`.

### 36.1 Root ownership

The root orchestrator owns development-environment continuity for its Goal. A child that encounters a missing package/tool/config reports, at minimum:

- exact blocked command;
- exact error;
- interpreter/runtime and environment path;
- missing prerequisite;
- affected test/task;
- whether compatible local/cached recovery was observed.

The child does not classify an ordinary routine dependency as an owner-authorization blocker and does not independently mutate a shared project environment.

### 36.2 Recovery ladder

The root resolves routine prerequisites in this order:

1. current Goal environment;
2. known project environments;
3. compatible already-installed or cached dependency;
4. serialized shared-project-environment repair under `ENV_ADMIN`;
5. Goal-local isolated environment creation/repair;
6. ecosystem-native project-local install/sync;
7. rerun the exact blocked command.

No unbounded host scan is implied.

Shared environments may be read concurrently, but shared mutation is serialized. Goal-local project/user-scoped environments are independently creatable and repairable without owner approval.

### 36.3 Routine dependency network authority

For ordinary development Goals, network access solely to retrieve `ROUTINE_DEV_PREREQ` packages from normal public package registries/CDNs is authorized. Record package/tool, resolved version where observable, package manager, target environment, install/sync command, and whether network retrieval occurred.

This authority does **not** authorize provider/model API calls, model/checkpoint/weights downloads, protected/archive-media retrieval, credentials/private-registry access, unrelated network activity, production execution, or Gate promotion. Installing an SDK/library never authorizes using its external service.

### 36.4 System boundary

Routine recovery is project/user scoped and reversible. Automatic routine authority does not include `sudo`, Homebrew/apt/yum or equivalent system-wide mutation, global interpreter replacement, kernel/driver changes, or OS security/policy changes.

If project-local recovery cannot avoid such a boundary, persist the exact Problem, park only affected descendants, and continue independent READY work.

### 36.5 TDD semantics

Environment/bootstrap failures are not behavioral RED. `ModuleNotFoundError`, missing pytest/test runner, dependency-driven collection failure, broken PATH, or missing routine tool do not satisfy the RED step.

After environment recovery, rerun the pre-implementation test and observe the intended behavioral failure before implementation.

If implementation already preceded environment recovery, a non-destructive test-efficacy recovery may run the new test against the pre-implementation code and the implementation head. Record `test_efficacy=VERIFIED` only when intended RED and GREEN are both observed; retain `chronological_red=NOT_OBSERVED` when that is the historical truth.

### 36.6 Reproducibility and remediation budget

If a capability genuinely depends on a newly supplied package/tool, record `NEW_DEV_DEPENDENCY` with its package/tool, resolved version, reason, owning capability, environment, and relevant test entrypoint. Do not leave permanent behavior dependent only on accidental local environment state.

Routine environment bootstrap/recovery is ENABLE work and does not consume the three-generation product-remediation budget unless provisioning itself becomes a genuine load-bearing technical root-cause family.

### 36.7 Authority precedence

This section governs ordinary development only. Explicit narrower Gate/task/spec/plan authority wins. A narrower contract that forbids pip, dependency installation/download, network activity, or environment provisioning is not silently widened.

Gate-0 Revision-18 remains under its frozen narrower authority unless separately amended.

### 36.8 Terminal prerequisite rule

"Dependency/tool missing" is terminal only after bounded existing-environment reuse, cached/local reuse, authorized shared or Goal-local provisioning where applicable, and retry of the exact blocked command have been attempted and no authority-compliant recovery remains.
