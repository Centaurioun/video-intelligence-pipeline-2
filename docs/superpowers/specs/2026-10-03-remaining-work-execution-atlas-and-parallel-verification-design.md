# Remaining Work Execution Atlas and Parallel Verification Design

**Status:** OWNER-APPROVED ARCHITECTURAL DESIGN — IMPLEMENTATION PLANNING/EXECUTION AUTHORIZED  
**Date:** 2026-10-03  
**Repository:** `Centaurioun/video-intelligence-pipeline`  
**Branch:** `planning/remaining-work-execution-atlas-design-20261003`  
**Canonical main baseline:** `72c71b7474968fa2dc88ecf9145489226a4cc986` at branch creation  
**Scope:** execution orchestration, remaining-work decomposition, prompt-packet preparation, parallel build/verification/repair, resource-concurrency policy direction, durable handoffs, progress accounting, and context-drift prevention  
**Does not itself authorize:** protected/archive-media execution, provider/cloud calls, model/checkpoint download, production render/export, Gate promotion, destructive Git operations, force push, or canonical-main integration.

---

## 1. Purpose

The project is already in an execution-first epoch, but repeated long-lived chat/controller sessions have drifted back toward serial analysis/review/certification loops. The owner has repeatedly requested that the remaining executable project be completed with sustained useful parallelism instead of one long-running Codex task blocking every independent next step.

This design adds a durable repository-level execution model whose primary objective is:

> preserve the execution-first intent across ChatGPT/Codex context loss, prepare the known remaining execution work in advance, continuously run every dependency-safe READY front, and prevent long-running build/test/review/repair work from unnecessarily blocking unrelated work.

The design converts the remaining project into a **Remaining Work Execution Atlas** with:

- a human-readable chapter hierarchy;
- a machine-readable dependency DAG;
- prebuilt/versioned Codex execution prompt packets;
- explicit main-agent / supervisor / worker delegation;
- continuous rolling-frontier scheduling;
- separate but concurrent BUILD, VERIFY, and REPAIR frontiers;
- parallelized testing/review when independently shardable;
- compact file-backed handoffs instead of large chat reports;
- prompt invalidation/versioning rules;
- adaptive progress accounting;
- measured heavy-resource concurrency rather than permanent `max=1`;
- later controlled convergence/integration.

This design extends, rather than replaces, the current:

- `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`;
- `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`;
- `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`;
- `docs/portfolio/portfolio-v1/resource-policy-v4.yaml`;
- current execution-first owner preference recorded in `docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`.

Where older historical review/certification process language conflicts with this design and the current execution-first protocols, ordinary development follows the current execution-first authority.

---

## 2. Owner intent frozen by this design

The owner wants the project finished rather than repeatedly re-planned.

The following intent is load-bearing:

1. **Execution is the default.** Existing approved architecture is not reopened merely because a fresh controller has a new context window.
2. **Useful work should stay continuously active.** A long-running Codex lane must not leave independent READY work idle.
3. **Parallel where possible, serial only where required.**
4. **Large goals must be decomposed enough to exploit concurrency, but not into two-minute microtasks whose orchestration overhead exceeds the work.**
5. **A top-level Codex is primarily a scheduler/integrator.** Delegable substantive work should run in subagents.
6. **Subagents should run concurrently when their work is independent.** Do not serialize independent subagent work merely for convenience.
7. **Testing and review also need sharding and parallelism.** One Codex should not spend hours serially executing independent checks if the checks can be split safely.
8. **Verification of an earlier chapter should not ordinarily block BUILD of the next chapter.**
9. **Failures are repaired promptly, but only affected descendants stop.** Independent fronts continue.
10. **Detailed worker reports should be durable/file-backed.** Parent/root contexts receive compact summaries.
11. **Fresh top-level Codex sessions are the default for new H3 execution packets.**
12. **The known remaining prompt cores should be prepared in advance** so that future controllers launch or narrowly revise them instead of redesigning the project.
13. **Speculative downstream work is an accepted tradeoff.** Some rework is preferable to global idle time, provided dependency impact is explicit and safety/authority invariants remain fail-closed.
14. **Broad formal review/certification is not the ordinary per-task loop.** It belongs at milestone/convergence/finalization boundaries unless a real blocker demands earlier review.
15. **No fixed four-root ceiling remains an owner preference.** Earlier bootstrap text describing approximately four initial roots is historical guidance, not a current cap. Launch as many genuinely independent top-level Codex roots as the READY frontier, ownership graph, harness, and machine can use safely.
16. **Numeric chapter order is navigation, not a synchronization barrier.** A later chapter or workstream may start before an earlier chapter is fully built if its actual DAG dependencies are satisfied.
17. **Manual dispatch must be low-friction.** Ready work should be packaged into numbered Launch Packs containing short labels plus copy-ready fresh-Codex prompts.
18. **The project finish line must be explicit.** Engineering completion, verification completion, and authority-dependent production/Gate completion must not be conflated.
19. **Executor choice must preserve execution-first semantics.** Standard Superpowers `subagent-driven-development` is not the default H3 executor because its mandatory reviewer-per-inner-task loop would serialize this repository's execution-first portfolio. Use the repo-native Execution Portfolio with `dispatching-parallel-agents`, TDD, systematic debugging, and verification-before-completion by default. A completed H3 feature/candidate still enters an asynchronous VERIFY lane using `requesting-code-review` before that candidate is integrated into convergence/current main; this review does not block independent downstream BUILD unless a true HARD_VERIFY dependency exists.
20. **In-flight speculative work is revocable.** If an upstream contract delta makes a running descendant stale, that descendant must not integrate merely because it later reports success.

---

## 3. Six-cycle refinement result

### Cycle 1 — Context-drift problem

The primary recurring failure is not absence of analysis; it is repeated loss of execution intent across long chat sessions. Therefore repository state, not chat memory, must carry the execution strategy.

**Decision:** create a durable Atlas + prompt library + state model. Fresh controllers should resume from those artifacts.

### Cycle 2 — Human hierarchy vs execution graph

A simple chapter tree is understandable but cannot express cross-chapter dependencies.

**Decision:** maintain both:

- **hierarchy** for navigation/progress;
- **DAG** for actual scheduling/authority.

### Cycle 3 — Prebuild prompts without pretending to know future SHAs

Static future prompts cannot safely freeze unknown future commit identities.

**Decision:** every execution prompt has:

- a versioned **Frozen Core** prepared in advance;
- a small **Launch Overlay** resolved immediately before execution.

This prevents conceptual drift while allowing real repository state to be bound correctly.

### Cycle 4 — Separate build from verification

Treating a chapter as one monolithic COMPLETE state creates artificial barriers.

**Decision:** BUILD, VERIFY, and REPAIR are concurrent rolling frontiers. A chapter may be `BUILD_GREEN` while still `VERIFYING`.

### Cycle 5 — Context-preserving hierarchy

Dozens of worker reports can overflow the main Codex context.

**Decision:** use:

`Root Orchestrator -> Area Lead/Supervisor -> Worker`

when supported; workers persist detail, supervisors aggregate, root receives compact state.

### Cycle 6 — Resource policy and throughput

The current `max_concurrent_without_new_measurement: 1` for heavy local / FFmpeg/model work was a conservative evidence boundary, not an immutable physical limit.

**Decision:** replace permanent single-job assumptions in a future policy revision with measured adaptive leases. Owner explicitly authorizes local-development concurrency calibration at 2 and, if stable, 3 concurrent heavy jobs. Failure reduces the lease; it does not stop unrelated lightweight work.

---

## 4. Remaining-work hierarchy

The Atlas uses four execution levels under one remaining-project root.

### H0 — Remaining Project

H0 represents the **entire remaining project from the Atlas baseline forward**.

For progress reporting, H0 is normalized to:

`REMAINING_WORK_BASELINE = 100.0 units`

This is not a claim that the historical project was 0% complete. It is a fresh denominator for the work that remains after Atlas creation.

### H1 — Chapter / major milestone

An H1 is a major remaining capability or milestone, analogous to a book chapter.

Examples may include:

- Gate-0 successor closure;
- semantic retrieval/multi-source productization;
- editorial/temporal pipeline completion;
- Gate-1 capability benchmark execution;
- Gate-2 reliability/scale execution;
- Gate-3 editing/QC hardening;
- portfolio convergence/integration;
- final system verification/readiness.

The exact H1 list must be derived from current repository evidence when the Atlas is instantiated. The design does not force an arbitrary chapter count.

### H2 — Workstream / sub-capability

An H2 groups coherent implementation surfaces inside one chapter.

### H3 — Top-level Codex Execution Packet

H3 is the normal unit handed to one **fresh top-level Codex**.

An H3 should:

- be substantial enough to sustain useful work, normally tens of minutes rather than a two-minute microtask;
- contain multiple meaningful H4 shards where the work supports them;
- have a bounded write domain;
- have explicit dependencies and completion criteria;
- expose enough parallel internal work to justify a root Codex acting as scheduler.

### H4 — Subagent shard

H4 is the normal unit of worker/area-lead delegation inside an H3.

H4 examples:

- disjoint production-code slice;
- focused test family;
- fixture/schema slice;
- migration slice;
- read-only contract investigation;
- debugging lane;
- focused verification lane.

H4 size is driven by ownership and meaningful test/review boundaries, not by a fixed line count.

---

## 5. Execution DAG and dependency classes

Hierarchy does not determine execution order. The DAG does.

Every H1/H2/H3 node records dependencies using:

- `INDEPENDENT`
- `SOFT_BUILD_DEPENDENCY`
- `HARD_BUILD_DEPENDENCY`
- `HARD_VERIFY_DEPENDENCY`

### INDEPENDENT

May run immediately when authority, ownership, and resources permit.

### SOFT_BUILD_DEPENDENCY

May begin after the upstream dependency reaches `BUILD_GREEN`, even if upstream verification continues.

This is the default mechanism that allows:

> Chapter 1 verifying while Chapter 2 builds.

### HARD_BUILD_DEPENDENCY

Requires a specific upstream built interface/artifact before implementation is meaningful.

### HARD_VERIFY_DEPENDENCY

Requires upstream verification, not merely build completion.

This should be used narrowly for cases where proceeding on an unverified result creates unacceptable correctness, evidence, authorization, or destructive-risk exposure.

**Default bias:** prefer INDEPENDENT / SOFT_BUILD_DEPENDENCY when technically sound. Do not mark work HARD merely to avoid speculative rework.

Chapter numbering does not itself create dependency. If an H3 in Chapter 3 consumes no unfinished Chapter-2 contract and has independent ownership, it may become READY before the rest of Chapter 2 finishes. The Atlas should exploit that overlap rather than enforce artificial chapter barriers.

---

## 6. Node state machine

A single COMPLETE flag is insufficient.

Normal node states:

- `PLANNED`
- `READY`
- `BUILDING`
- `BUILD_GREEN`
- `VERIFY_READY`
- `VERIFYING`
- `VERIFIED`
- `REPAIRING`
- `PARKED`
- `DIRTY_BY_CONTRACT_DELTA`
- `STALE_IN_FLIGHT`
- `SUPERSEDED`

Every build/verification state also binds an immutable **candidate generation**:

- exact candidate SHA/tree;
- consumed contract refs/fingerprints;
- prompt-core version;
- launch-overlay version;
- relevant environment/resource-lease identity.

Verification results never float free of the exact candidate generation they observed.

### BUILD_GREEN

Means:

- declared implementation work is complete enough for its focused local acceptance;
- required focused tests/checks for the build packet pass;
- a durable candidate/commit exists.

It does **not** mean broad milestone certification.

### VERIFIED

Means the node has passed the verification scope assigned to it.

An H1 may have descendants actively building while the earlier H1 is still `VERIFYING`.

---

## 7. Three concurrent rolling frontiers

The scheduler maintains three first-class frontiers.

### 7.1 BUILD frontier

Purpose:

- produce the remaining executable capability;
- keep forward progress continuous;
- begin downstream SOFT-dependent chapters when upstream reaches BUILD_GREEN.

### 7.2 VERIFY frontier

Purpose:

- run focused/broad testing and review behind the build frontier;
- start the required H3 feature-level code review after BUILD_GREEN;
- shard independently executable tests/reviews across multiple Codex roots;
- require review disposition before that H3 candidate is integrated into convergence/current main;
- avoid turning verification into a global barrier for independent BUILD work.

### 7.3 REPAIR frontier

Purpose:

- immediately investigate and repair failures found by build or verification;
- use systematic debugging and bounded remediation;
- block only affected descendants.

At any moment the portfolio may legitimately look like:

- Chapter 1: `REPAIRING`
- Chapter 2: `VERIFYING`
- Chapter 3: `BUILDING`
- Chapter 4: `READY`

This is a desired state, not a process error.

### 7.4 Frontier anti-starvation

No one frontier should monopolize all available lightweight capacity indefinitely.

When READY work exists, the scheduler should normally preserve simultaneous progress across:

- at least one forward BUILD path;
- VERIFY debt that is old enough to threaten convergence;
- REPAIR work that blocks a meaningful descendant set.

This is adaptive, not a fixed 8/2/2 quota. A CRITICAL safety/integrity incident may temporarily dominate only the affected blast radius when continuation elsewhere remains safe.

### 7.5 Progressive verification

Verification need not wait for an entire H1 chapter to reach BUILD_GREEN.

An immutable H3 candidate may enter VERIFY as soon as that H3 is BUILD_GREEN while sibling H3 packets in the same chapter continue building. Chapter-level verification aggregates those results later.

### 7.6 Stale in-flight work

When a contract/path delta invalidates a descendant that is already running:

- mark it `STALE_IN_FLIGHT`;
- notify/cancel it when the runtime supports safe cancellation and the saved compute is meaningful;
- otherwise allow it to finish only as non-integrable exploratory output;
- never accept its commit/handoff into the current frontier without an explicit rebase/reconciliation against the new consumed-contract fingerprint;
- recycle released capacity into current READY work.

This prevents speculative parallelism from turning stale success messages into accidental integration.

---

## 8. Parallel testing design

Testing must not be treated as one serial monolith.

Before a broad verification phase, classify checks into independent **test shards** based on:

- subsystem;
- fixtures/environment;
- write/read interaction;
- heavy resource requirement;
- candidate SHA;
- dependency on prior test output.

Examples:

- parser/unit shard;
- lifecycle/concurrency shard;
- temporal/PTS shard;
- provenance/evidence shard;
- CLI/integration shard;
- static/schema shard;
- heavy FFmpeg shard;
- model/MPS shard.

If six shards can independently validate the same immutable candidate SHA, six Codex sessions may run them concurrently.

Each verification shard records:

- exact candidate SHA/tree;
- declared coverage paths/contracts;
- exact test command/check;
- environment identity;
- resource lease class;
- result artifact/receipt.

If a repair creates a new candidate generation, prior shard results do not automatically certify the new candidate. Reuse is allowed only when the shard's declared coverage is mechanically shown unaffected by the changed paths/contracts; otherwise rerun that shard.

Test shards that use ports, temp directories, caches, mutable fixtures, environment variables, or process-global state must receive isolated resources. If isolation cannot be established cheaply and deterministically, that shard class is explicitly SERIAL rather than pretending to be parallel-safe.

A shard may itself contain multiple related tests. The rule is not “one test = one Codex.” The rule is:

> independent validation work should not be serialized merely because it belongs to one testing phase.

Within a test Codex, independent internal checks should again be dispatched concurrently to subagents when practical.

### Test completion

A test Codex writes detailed outputs to durable state and returns a compact receipt. Large raw logs should not be copied through chat unless needed to diagnose a failure.

---

## 9. Parallel review design

Formal review is not required after every H3.

When review is justified at a milestone/convergence boundary, it should be decomposed by independent concern, for example:

- API/shared-contract review;
- temporal/PTS review;
- provenance/evidence review;
- concurrency/lifecycle review;
- test-efficacy/false-green review;
- scope/authority review.

Independent review lanes may run concurrently against one immutable candidate SHA.

One aggregation lane deduplicates findings and maps each finding to:

- exact reviewed candidate SHA;
- affected node(s);
- severity;
- frontier impact;
- affected contract/path coverage;
- required repair/invalidated descendants.

If repair advances the candidate while a review lane is still running, that review result is retained as historical evidence for the old generation. Heavy stale review/test work may be cancelled when safe to recycle resources; lightweight work may finish, but stale results do not silently satisfy the new generation.

This prevents one multi-hour reviewer from blocking unrelated execution.

---

## 10. Failure and speculative-descendant policy

The owner accepts bounded speculative downstream work because global serialization has become a larger project risk than limited rework.

### Failure handling

A failing test/review is not deferred indefinitely.

It enters the REPAIR frontier immediately:

1. preserve failure evidence;
2. identify affected node/contract;
3. systematic-debug;
4. repair;
5. rerun focused checks;
6. update Problem state.

### Impact isolation

Failure does not automatically stop the portfolio.

Determine the **affected descendant set** from the dependency/shared-contract graph and the changed contract/path surface.

Affected descendants become:

- `PARKED`, or
- `DIRTY_BY_CONTRACT_DELTA`.

Unaffected BUILD/VERIFY/REPAIR nodes continue.

A repair that changes only internal implementation and preserves every consumed contract fingerprint should not invalidate unrelated descendants merely because the upstream commit SHA changed.

A repair that changes a consumed shared contract invalidates only nodes whose declared consumed-contract set intersects that delta.

If a failure threatens source preservation, authorization, evidence integrity, temporal correctness, data integrity, or has an initially unknown potentially broad blast radius, first quarantine the plausibly affected subgraph. Do not infer that everything is safe merely to preserve throughput; equally, do not globally stop proven-independent work.

### Bounded remediation

Retain the existing default limit of three evidence-supported failed remediation generations per load-bearing root-cause family unless a later owner policy changes it.

After exhaustion:

- preserve the Problem;
- park only affected descendants;
- continue all other READY work;
- return to owner/controller only when no useful frontier remains or a genuine authority/architecture boundary is reached.

---

## 11. Prompt Packet Library

Every known H3 should have a prebuilt versioned execution prompt.

### 11.1 Frozen Core

Prepared in advance and changed only through explicit prompt-core revision.

Fields include:

- `TASK_ID`
- `H0/H1/H2/H3 identity`
- goal/capability outcome;
- why the task exists;
- expected deliverables;
- dependency types;
- read scope;
- expected write domain;
- shared-contract surfaces;
- prohibited scope;
- focused build tests;
- verification hooks;
- failure policy;
- main-agent role;
- H4 decomposition guidance;
- subagent parallelism contract;
- handoff format;
- completion criteria.

### 11.2 Launch Overlay

Bound immediately before execution:

- exact current BASE SHA;
- accepted dependency HEADs;
- branch/worktree;
- current contract deltas;
- relevant open Problem IDs;
- current resource leases;
- resolved concrete model identity;
- any packet fields invalidated since creation.

Launch-overlay refresh is **not** permission to redesign the Frozen Core.

### 11.3 Versioning

Each packet records:

- `PROMPT_CORE_VERSION`
- `PROMPT_CORE_SHA256`
- `LAST_LAUNCH_OVERLAY_VERSION`
- `LAST_RECONCILED_AT_HEAD`
- exact consumed-contract refs/fingerprints.

If the core meaning changes:

- increment the core version;
- record why;
- identify downstream packets invalidated.

### 11.4 Contract fingerprints

For shared APIs/schemas/temporal/provenance/evidence contracts, packets consume exact immutable refs (Git blob/SHA or an equivalent deterministic fingerprint). This lets the controller distinguish:

- upstream implementation churn with no contract change;
- a real contract delta that invalidates descendants.

Do not mark future packets DIRTY merely because an unrelated upstream file changed.

### 11.5 Launch Packs

Manual owner dispatch should use **Launch Packs**.

A Launch Pack contains:

- batch ID;
- numbered H3 task labels;
- one copy-ready prompt per fresh top-level Codex;
- READY/dependency/resource status;
- a short instruction that each prompt normally opens a new Codex chat;
- no requirement that the owner remember old Codex chat identities.

The controller may return 5, 10, or another useful number of prompts according to the current READY frontier. The count is not fixed.

Each Launch Pack also marks the intended executor mode per H3:

- `PARALLEL_PORTFOLIO` — default;
- `SERIAL_TIGHT_COUPLING`;
- `PER_TASK_REVIEW_REQUIRED` — exceptional;
- `VERIFY_ONLY`;
- `REPAIR_CELL`.

This prevents a fresh Codex/controller from choosing a slower review-heavy workflow by habit.

---

## 12. Launch Delta Reconciliation

Between batches, ChatGPT/controller performs a **Launch Delta Reconciliation**, not a broad architecture review.

Its bounded questions are:

1. Which prior packets are BUILD_GREEN / VERIFYING / VERIFIED / REPAIRING / PARKED?
2. Which dependencies have become READY?
3. Which shared-contract deltas were produced?
4. Which future prompt packets are actually affected?
5. Which affected packets need a narrow overlay/core revision?
6. What is the next maximum useful READY batch?

Prompt packet statuses:

- `READY`
- `WAITING_FOR_DEPENDENCY`
- `DIRTY_BY_CONTRACT_DELTA`
- `BLOCKED_AUTHORITY`
- `PARKED_PROBLEM`

Unaffected packets remain unchanged. Do not rereview all future prompts after every batch.

The reconciliation output should normally be operational rather than narrative:

- receipts consumed;
- packets newly READY;
- packets dirtied/parked and why;
- resource leases available;
- next Launch Pack.

A fresh ChatGPT must not regenerate Frozen Cores simply because it lacks the prior chat context. It reads the Atlas, prompt versions, current receipts, Problem records, and latest Launch Delta Reconciliation first.

---

## 13. Executor and Main Codex / supervisor / worker contract

### 13.0 Default Superpowers execution method

For H3/H4 execution, the repository default is **Execution Portfolio Parallel**, not the stock per-task-review form of `subagent-driven-development`.

Default skill routing:

- independent READY domains -> `dispatching-parallel-agents`;
- behavior change -> `test-driven-development`;
- unexpected failure -> `systematic-debugging`;
- completion claim -> `verification-before-completion`;
- every completed H3 feature/candidate -> enqueue `requesting-code-review` in the VERIFY frontier before integration;
- review feedback -> `receiving-code-review`;
- broader milestone/convergence review -> additional scoped review lanes when scheduled.

Do **not** invoke `subagent-driven-development` merely because subagents are used. Its mandatory reviewer-after-every-inner-task loop is appropriate only for an H3 explicitly marked `PER_TASK_REVIEW_REQUIRED`, not for ordinary execution-first packets. Ordinary H3 review happens asynchronously at the H3 candidate boundary.

Likewise, `executing-plans` is not the normal multi-root H3 executor because it centralizes implementation in one context. It may be used for tightly coupled/serial packets where parallel decomposition is not useful.

This routing is a repository-specific selection among Superpowers workflows; it does not waive TDD, systematic debugging, focused verification, or final milestone review.

### Root/Main Codex

Default role:

- scheduler;
- authority interpreter;
- dependency manager;
- ownership allocator;
- integrator within its execution branch;
- Problem adjudicator;
- compact state owner.

It should not perform serial substantive work itself when clean delegation exists.

### Area Lead / Supervisor

When nested delegation is supported, supervisors:

- receive coherent H4 groups;
- launch workers concurrently;
- consume file-backed worker handoffs;
- aggregate results;
- report compact state to root.

### Worker

Workers:

- implement/test/debug/measure their assigned bounded shard;
- may write code/tests only within exclusive assigned ownership;
- may write their own durable worker findings/state;
- do not send long narrative reports into parent context.

Worker detail does not need to become a committed Markdown memo by default. Use ephemeral/file-backed state for high-volume diagnostics and commit only terminal state needed for recovery, integration, a Problem record, or evidence. Supervisors aggregate before escalating to root.

If nested delegation is unsupported, flatten to Root -> Workers while preserving the same compact handoff model.

---

## 14. Mandatory H3 parallelism contract

Every H3 Frozen Core should include these rules:

1. Enumerate meaningful H4 shards before substantive execution.
2. Mark each H4 `READY`, `BLOCKED`, or `SERIAL`.
3. Dispatch all independent READY H4 shards concurrently where capacity exists.
4. Do not serialize independent H4 work merely for convenience.
5. Keep root/main context as control plane by default.
6. Give writer workers exclusive paths/contracts.
7. Allow read-only workers to share immutable candidate state.
8. Close terminal children promptly.
9. Recycle freed slots immediately into newly READY H4 work.
10. Do not wait for an artificial whole-wave barrier.
11. Heavy-resource work obeys the current measured lease.
12. If a child exposes a contract delta, record it rather than silently widening sibling scope.

---

## 15. Durable reporting and short chat receipts

The repository, not parent chat, is the detailed execution memory.

### Worker detail

Workers may persist structured state under a goal-local durable hierarchy such as:

`.orchestration/portfolios/<id>/goals/<goal>/workers/<worker-id>.json`

or an equivalent approved path.

### Supervisor aggregate

Supervisors aggregate worker outputs rather than copying every worker narrative to the root.

### Root handoff

The top-level Codex returns a short human-copyable receipt, normally about 8–15 lines. The receipt is a pointer/index, not a narrative report:

- `TASK`
- `STATUS`
- `BASE_SHA`
- `HEAD_SHA`
- `CHANGED_PATHS`
- `FOCUSED_TESTS`
- `OPEN_PROBLEMS`
- `CONTRACT_DELTA`
- `DURABLE_HANDOFF`
- `UNLOCKS`
- `PUSH_STATUS`

The controller can retrieve detail from Git/repository state when necessary.

---

## 16. Fresh-Codex default

For owner-operated manual dispatch:

- **new H3 packet -> fresh top-level Codex by default**.

Reuse an existing Codex chat only when:

- continuing the exact same unfinished H3;
- executing bounded repair of that H3 where retained ephemeral state is genuinely useful;
- the packet explicitly requires continuation.

This reduces human confusion when many Codex sessions are active.

---

## 17. Remaining-work progress accounting

At Atlas freeze:

`H0 remaining work = 100.0 completion units`

H0's denominator covers the **active currently authorized finish line**, not every imaginable future authority-dependent activity. Work requiring separate protected/archive, provider/cloud, production-export, or Gate-promotion authority is tracked in a linked authority-dependent backlog and does not prevent the current H0 denominator from reaching 100 unless/until the owner explicitly expands/rebaselines the active finish line.

Each H3 receives an estimated relative weight based on:

- implementation size;
- integration/contract risk;
- verification requirement;
- expected resource intensity;
- dependency criticality.

Weights are planning estimates, not promises of wall-clock duration.

Weights are frozen at the Atlas baseline for honest progress tracking. Newly discovered work that is necessary to complete an existing H1 should normally subdivide that H1's remaining uncompleted weight rather than silently increasing apparent progress. A genuine owner-approved scope expansion requires an explicit rebaseline/scope-delta record preserving both the old and new denominator.

Report at minimum:

- BUILD units green;
- VERIFY units verified;
- REPAIR/problem units;
- READY units;
- dependency-wait units;
- authority-blocked units.

Example conceptual status:

- `BUILD_PROGRESS = 64/100`
- `VERIFICATION_PROGRESS = 41/100`

This deliberately permits build progress to lead verification progress.

---

## 18. Verification debt

Because verification can trail build, the Atlas must expose verification debt rather than hide it.

A chapter reaching BUILD_GREEN creates/updates its VERIFY frontier.

The scheduler may shift capacity dynamically:

- early/middle epoch: more BUILD capacity;
- late epoch: progressively more VERIFY/REPAIR/convergence capacity.

No fixed ratio is required.

The only hard requirement is that verification debt remains visible and is substantially closed before final completion claims.

---

## 19. Heavy-resource policy redesign

### 19.1 Current state

Resource policy v4 currently freezes:

- heavy local execution: max 1 without new measurement;
- FFmpeg/model-heavy execution: max 1 without new measurement.

This was a conservative evidence policy, not a demonstrated machine limit.

### 19.2 Owner ruling

The owner explicitly authorizes a future policy change to test and use greater local concurrency for ordinary authorized development work.

No additional owner confirmation is required merely to perform the bounded local calibration described here.

This ruling does **not** authorize:

- protected/archive media;
- provider/cloud/model downloads;
- production export;
- system-wide privileged mutation.

### 19.3 Capacity-calibration goal

The Atlas should include an early ENABLE node that measures safe concurrent local workload.

The planned v5 transition should no longer treat one job as the normal default for ordinary authorized local development:

- `HEAVY_CPU` / `FFMPEG_HEAVY`: begin with an operational lease of **2 concurrent jobs** using synthetic/non-protected inputs;
- if stable and wall-clock throughput improves, calibrate **3 concurrent jobs**;
- `MODEL_MPS`: calibrate separately, beginning with **2** only when an already-authorized local model/runtime is available; do not download a model merely for calibration;
- test mixed lightweight-test + FFmpeg/model workloads;
- keep `ENV_ADMIN` serialized unless separate evidence justifies otherwise.

If the two-job trial is unstable, fall back to one for that resource class while the rest of the portfolio continues.

The policy transition should be fail-soft and self-correcting: a heavy-job crash/timeout/resource-pressure signal automatically lowers only the affected lease class for the current Goal and records the event for the next calibration. It must not globally lower lightweight Codex/test concurrency.

Observe:

- wall-clock throughput;
- process failures;
- OOM/memory pressure;
- swap pressure where observable;
- CPU contention;
- GPU/MPS failures;
- output determinism where relevant.

### 19.4 Adaptive policy

A future `resource-policy-v5` should prefer explicit lease classes rather than one universal single-job cap.

Possible classes:

- `LIGHTWEIGHT_CPU_TEST`
- `HEAVY_CPU`
- `FFMPEG_HEAVY`
- `MODEL_MPS`
- `MIXED_HEAVY`
- `ENV_ADMIN`

Measured safe concurrency becomes the lease limit for that class.

If concurrency causes instability or worsens throughput materially:

- reduce that class’s lease;
- rerun affected job serially or at lower concurrency;
- continue unrelated work.

A resource calibration failure is not a reason to serialize the entire project.

### 19.5 No blind overcommit

Owner preference favors speed, but concurrency should still optimize **wall-clock completion**, not process count. Ten heavy jobs that make all jobs slower are worse than three concurrent jobs.

---

## 20. Chapter transition rule

This design freezes the following default behavior:

> When Chapter N reaches BUILD_GREEN, Chapter N+1 may begin immediately if its dependency classification permits it. Chapter N testing/review/repair continues concurrently.

Examples:

### Valid

- Chapter 1 VERIFYING;
- Chapter 2 BUILDING;
- Chapter 3 READY.

### Also valid

- Chapter 1 REPAIRING a local defect;
- Chapter 2 VERIFYING;
- Chapter 3 BUILDING.

### Must wait

Chapter 3 has `HARD_VERIFY_DEPENDENCY` on a Chapter-2 evidence/authority contract that cannot safely be consumed before verification.

Hard verification edges should be explicit and uncommon.

This chapter rule is a minimum overlap guarantee, not a maximum. Dependency-safe H3 packets in later chapters may begin even earlier than whole-chapter BUILD_GREEN when their exact prerequisites are already satisfied.

---

## 21. Convergence and integration

Parallel roots are intentionally allowed to finish independently.

Convergence later:

1. collect immutable root heads and compact handoffs;
2. calculate actual path/shared-contract overlap;
3. reconcile contract deltas;
4. design only the necessary integration resolutions;
5. execute integration on an isolated integration branch;
6. run cross-system verification;
7. preserve canonical main until separately authorized.

A clean Git merge is not semantic proof.

However, convergence must also avoid reopening already-settled architecture merely because parallel work now needs mechanical reconciliation.

---

## 22. What this design explicitly rejects

Rejected patterns:

1. One long-running Codex blocks all unrelated work.
2. Chapter N must be fully certified before any Chapter N+1 work begins.
3. Independent test families executed serially by one agent for hours.
4. Independent review concerns executed serially solely because they share the label “review.”
5. Reviewer -> patch -> reviewer -> certifier loops after every microtask.
6. Recreating architecture analysis at every ChatGPT context refresh.
7. Sending full worker reports through root chat.
8. Requiring the owner to remember which old Codex chat receives which new task.
9. Preparing no future prompts until the previous packet finishes.
10. Treating future prompt cores as immutable even after a real contract delta.
11. Blindly launching every future packet regardless of dependency/authority.
12. Blind heavy-resource overcommit.
13. Global stop because one speculative descendant needs rework.
14. Multiple concurrent writers on the same exact mutable file/state without explicit coordination.

---

## 23. Atlas and prompt-library artifact shape

A later implementation plan should instantiate a structure conceptually similar to:

```text
.orchestration/
  remaining-work/
    CONTROLLER_START_HERE.md
    atlas/
      atlas.json
      chapters/
        H1-...
    prompts/
      H3-.../
        core.md
        core.sha256
        overlay.json
    launch-packs/
      batch-001/
        manifest.json
        01-<task>.md
        02-<task>.md
    verification/
      ...
    problems/
      ...
    convergence/
      ...
```

Exact paths/schema are implementation-plan decisions and may reuse existing portfolio conventions rather than creating redundant structures.

---

## 24. Repository-policy promotion and Atlas creation sequence

Before Atlas execution starts, the approved implementation plan should promote the owner decisions into current repository authority so a fresh controller does not read conflicting historical defaults.

Because this work will span multiple ChatGPT contexts, the core policy promotion should occur **early**, immediately after its own verification, rather than waiting until the entire Atlas/prompt library is complete. The owner has explicitly authorized the required canonical-main process/policy updates. Later Atlas/tooling promotion may occur as a second controlled promotion.

Expected current-policy surfaces to reconcile include at least:

- `AGENTS.md` — point fresh agents at the Atlas/Launch Pack model and explicit executor routing;
- `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md` — BUILD/VERIFY/REPAIR concurrency, stale-in-flight handling, chapter overlap, Launch Delta Reconciliation;
- `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md` — Launch Packs and prompt-core/overlay durability;
- `docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md` — retire the old approximately-four-roots wording as a historical bootstrap preference;
- `docs/portfolio/portfolio-v1/resource-policy-v4.yaml` — supersede with a measured/adaptive v5 policy rather than editing historical evidence in place where preservation is preferable;
- `docs/INDEX.md` / current project handoff if needed so fresh sessions find the new authority first.

The implementation plan must choose whether each old policy file is amended in place or superseded by a new version, preserving historical truth and avoiding contradictory current authority.

### Atlas creation sequence

The future implementation/planning sequence should be:

1. reverify remote canonical state **and inventory relevant local-only branches/worktrees** so accepted/unpushed Task-3/Task-4 lineage is not omitted from the Atlas;
2. promote/reconcile the approved orchestration decisions into the current repository policy surfaces above;
3. verify that fresh-session reading order resolves to one unambiguous execution authority;
4. define the intended finish-line taxonomy for this Atlas;
5. derive the **H0/H1/H2/H3 table of contents** from actual remaining work;
6. review only that table of contents for missing/duplicate chapters;
7. freeze dependency classes, shared-contract edges, and initial contract fingerprints;
8. assign initial remaining-work weights;
9. generate H3 Frozen Core prompt packets chapter by chapter;
10. generate H4 decomposition guidance for each H3;
11. add durable short-receipt contracts and `CONTROLLER_START_HERE`;
12. build initial READY/WAITING/DIRTY state;
13. generate the first Launch Pack;
14. execute heavy-resource capacity calibration early enough to affect the remaining portfolio;
15. promote measured adaptive resource-policy limits;
16. begin rolling multi-root execution;
17. perform Launch Delta Reconciliation between dispatch batches;
18. keep BUILD, VERIFY, and REPAIR frontiers active concurrently;
19. converge/integrate completed roots;
20. close verification debt and final system-level problems;
21. only then enter final certification/release-readiness work.

---

## 25. Current Gate-0 Task-4 implication

The current Task-4 successor-spec line remains a real current dependency and is not erased by this design.

However, the next controller should treat it as one H3/H2 area inside the broader remaining-work Atlas, not as the entire project.

Once its written-spec approval/implementation plan authority is satisfied, Task-4–12 execution should follow the new rolling model:

- focused build work forward;
- verification behind it;
- independent project chapters continue where allowed;
- no return to global serial review unless a true hard dependency demands it.

---

## 26. Safety and authority invariants unchanged

No throughput optimization may weaken:

- source immutability;
- exact source-native PTS/timebase authority;
- prohibition on seconds × nominal FPS for VFR frame identity;
- evidence-class discipline;
- distinction between candidate semantic timestamps and edit boundaries;
- protected/archive-media boundaries;
- provider/cloud/model-download boundaries;
- production export boundaries;
- Gate-promotion authority;
- destructive Git prohibitions;
- explicit canonical-main integration authority.

Speculative execution may accept rework; it may not accept silent evidence or authorization corruption.

---

## 27. Finish-line taxonomy

The Atlas must distinguish at least three completion statements so “the project is finished” cannot drift in meaning.

For the initial Atlas, the active finish line is:

`ACTIVE_FINISH_LINE=VERIFICATION_COMPLETE_FOR_CURRENT_AUTHORIZED_LOCAL_FIRST_SCOPE`

This means the current H0=100 denominator targets a fully implemented and verified local-first engineering system inside current authority. Authority-dependent production/protected/Gate work remains separately visible but outside that denominator until explicitly authorized and rebaselined.

### ENGINEERING_EXECUTION_COMPLETE

All Atlas-required implementation chapters are BUILD_GREEN on converged/integrated candidate(s); no unresolved GOAL_BLOCKER prevents the declared local-first engineering capability.

### VERIFICATION_COMPLETE

Required verification debt for the engineering target is closed on the final candidate generation, except explicitly owner-accepted deferred non-blocking Problems.

### AUTHORITY_DEPENDENT_COMPLETE

Any work that inherently requires a separate authority boundary—such as protected/archive-media execution, production export, provider/cloud use, Gate promotion, or other currently unauthorized evidence—has either:

- been separately authorized and completed; or
- remains explicitly outside the current finish line and is reported as authority-blocked rather than falsely complete.

The Atlas creation pass must state which of these finish lines is the active project objective. Progress percentages alone may not imply a stronger finish line.

---

## 28. Reconsideration triggers

Reopen this design only if evidence shows one of the following:

1. the runtime cannot support useful concurrent top-level Codex sessions;
2. nested subagent delegation is unavailable and flattening cannot preserve required throughput;
3. prompt Frozen Core / Overlay separation creates systematic stale-authority failures;
4. speculative descendants create rework larger than the wall-clock savings;
5. test/review sharding produces nondeterministic or mutually interfering verification;
6. measured heavy-resource concurrency above one is consistently slower or unstable;
7. durable worker state causes materially excessive repository churn;
8. dependency/shared-contract invalidation cannot be represented without frequent global replanning.

Ordinary bugs, test failures, and bounded contract deltas are **not** reconsideration triggers.

---

## 29. Written-spec review questions

The next review pass should challenge this design only on concrete omissions/contradictions, especially:

1. Can a fresh ChatGPT recover the execution intent without the prior conversation?
2. Are H0/H1/H2/H3/H4 responsibilities unambiguous?
3. Can Chapter N+1 build while Chapter N verifies without hiding true HARD_VERIFY dependencies?
4. Are BUILD/VERIFY/REPAIR states sufficient?
5. Does the prompt Frozen Core/Launch Overlay model prevent drift while remaining updateable?
6. Is subagent concurrency explicit enough to prevent unnecessary serial execution?
7. Does file-backed worker reporting materially protect root context?
8. Are test/review shards safely parallelizable against immutable candidates?
9. Are failure impact and descendant invalidation bounded?
10. Is heavy-resource concurrency change authorized but still measured rather than blindly overcommitted?
11. Does progress accounting expose both build progress and verification debt?
12. Does this design avoid recreating a review/certification treadmill?
13. Are current safety/evidence/authorization invariants preserved?
14. Are verification/review results bound to exact candidate generations?
15. Can contract fingerprints prevent needless descendant invalidation?
16. Are parallel test shards isolated from mutable ports/temp/cache/global state?
17. Does the Launch Pack reduce manual copy/paste ambiguity?
18. Does the Atlas survive a fresh ChatGPT without regenerating prompt cores?
19. Are progress weights protected against silent denominator changes?
20. Is the project finish line explicit enough to prevent “done” from drifting?
21. Does executor routing prevent stock subagent-driven review loops from overriding the execution-first policy?
22. Can stale in-flight speculative work be prevented from integrating after an upstream contract delta?
23. Will fresh-session reading order resolve policy v4/v5 and old four-root guidance without ambiguity?
24. Does every completed H3 enqueue code review before integration without turning that review into a global BUILD barrier?
25. Is H0=100 scoped to a finishable current-authority target rather than permanently blocked by separately authorized future work?
26. Is the core policy promoted early enough to survive ChatGPT context turnover during Atlas construction?

---

## 30. Authority status

This document records the owner-approved architectural direction from the 2026-10-03 brainstorming conversation. The owner subsequently approved implementation planning and execution of the Atlas/policy system, including the policy/resource changes and the required canonical-main process-policy promotion. The detailed implementation plan now governs execution in chunks. This authority does **not** widen protected/archive-media, provider/cloud, production-export, Gate-promotion, or destructive-Git scope.

The owner has already stated that future bounded local heavy-resource concurrency calibration and a resulting increase from the historical `max=1` limit are acceptable; do not ask again merely to trial 2 then 3 local concurrent jobs within the above scope.

---

## 31. Target operating principle

The final operating rule is:

> No long-running BUILD, TEST, REVIEW, or REPAIR job may unnecessarily block independent READY project work.

Earlier “approximately four roots” bootstrap wording and numeric child-count targets are treated as historical/soft guidance, not as current throughput ceilings. Actual top-level and child concurrency is adaptive and limited only by genuine READY work, ownership, harness capability, measured resource leases, and safety/authority boundaries.

And the chapter-transition rule is:

> When Chapter N is BUILD_GREEN, Chapter N+1 starts as soon as its true dependencies permit, while Chapter N verification and repair continue in parallel.

The repository becomes the durable memory; Codex roots become schedulers/integrators; subagents perform bounded work; ChatGPT performs owner-facing launch-delta reconciliation rather than repeatedly redesigning the project.
