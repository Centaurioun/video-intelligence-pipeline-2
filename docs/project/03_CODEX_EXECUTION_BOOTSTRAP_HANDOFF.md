# Video Intelligence Pipeline — Codex Execution Bootstrap Handoff

## 0. 2026-10-03 Remaining-Work Execution Atlas superseding bootstrap

This section is the current bootstrap for ordinary remaining-project execution and supersedes conflicting process guidance later in this document. Historical product/Gate evidence remains unchanged.

Fresh controller order for Remaining Work execution:

1. `AGENTS.md`
2. `docs/INDEX.md`
3. `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`
4. `docs/superpowers/specs/2026-10-03-remaining-work-execution-atlas-and-parallel-verification-design.md`
5. `docs/superpowers/plans/2026-10-03-remaining-work-execution-atlas-implementation-plan.md`
6. `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`
7. `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`
8. `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`
9. `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`
10. `.orchestration/remaining-work/CONTROLLER_START_HERE.md` once created by the implementation plan.

Current operating rulings:

- BUILD / VERIFY / REPAIR are concurrent rolling frontiers.
- Chapter numbers do not create scheduling barriers.
- Earlier “approximately four root Codex sessions” wording is historical bootstrap guidance, **not a current cap**.
- Top-level/root and child concurrency is adaptive to actual READY work, ownership, runtime capacity, and resource leases.
- Every H3 BUILD_GREEN feature candidate is code-reviewed asynchronously on VERIFY before convergence/current-main integration, while independent BUILD continues.
- Stock `subagent-driven-development` is not the default H3 executor; use the repository-native parallel portfolio routing defined in the Atlas spec.
- HEAVY_CPU/FFMPEG ordinary-development lease begins at 2 under v5 and is calibrated toward 3 when stable/useful; a heavy-resource failure lowers only the affected lease class.
- Known future prompt cores are prepared/versioned in advance and launched through numbered Launch Packs; future controllers patch only affected packets through Launch Delta Reconciliation.
- New H3 execution defaults to a fresh top-level Codex chat; detailed results remain durable in Git/file-backed state and chat returns a compact receipt.

The owner explicitly authorized the process/policy promotion needed to make this model current. This does not authorize protected/archive media, provider/cloud activity, model downloads, production export, Gate promotion, destructive Git, or unrelated product-scope expansion.


**Status:** CURRENT EXECUTION-BOOTSTRAP HANDOFF  
**Date:** 2026-09-24  
**Audience:** fresh ChatGPT controller/coordinator before substantive Codex implementation begins  
**Purpose:** allow a fresh ChatGPT session to continue the project without reconstructing the long prior conversation

---

## 1. What just finished

The repository has completed the process-policy transition and remote branch-hygiene campaign.

Historical branch proliferation is no longer the active problem.

Branch-hygiene cleanup baseline:

`a6a7c3bbacf1e831cc870140db6433f30317a46f`

That cleanup reduced the remote branch surface to five branches while preserving deleted history through:

- preservation tag: `archive/history/branch-preservation-v1`
- annotated tag object SHA: `b8ed6fbfbc3b8531985e3e672ec509f01059d327`
- preservation root commit: `10d5ab2eb620be3e40ffb7e6218245b51a34af8e`
- frozen preservation tree: `1f17b755e2e1889208a684a132f6d3ee5033e3c4`
- canonical recovery ledger:
  `.orchestration/maintenance/branch-hygiene-cleanup-v1/preservation-recovery.json`

Do not recreate deleted historical branches merely because an old document names them. Use the preservation tag/recovery ledger when historical branch evidence is needed.

The five retained remote branches at cleanup completion were:

- `main`
- `controller/gate1/portfolio-v1@fdb39ea358cbf8690321df2790696669818d91d6`
- `controller/gate2/portfolio-v1@2ff37268d032af7287fc1f685e0e76f5b7654d2d`
- `transition/workspace-consolidation-v2@8f43dc1fe2fd66bd87105b0f0d7529d268c54114`
- `dependabot/npm_and_yarn/reference-pack/recurser/source/frontend/npm_and_yarn-29cc12f3e6@58b60e3f8c350eb77c8497150323a711a0bb4692`

A fresh session MUST re-fetch current GitHub state before relying on these exact heads. The repository is the technical source of truth.

No product code was changed by the branch-hygiene operation.

---

## 2. What phase starts now

The project now enters the substantive **implementation / execution epoch**.

In this handoff, “execution” means primarily:

- writing/refactoring real product code;
- writing tests/fixtures/schemas required by that code;
- integrating working capabilities;
- bounded debugging;
- reliability/recovery implementation when justified;
- producing a usable local-first video-intelligence pipeline.

It does NOT mean spending the main development budget on:

- repeated independent review waves;
- certifier swarms;
- reviewer -> patch -> reviewer loops;
- documentation-only audit campaigns;
- long narrative agent memos;
- branch-hygiene work;
- reopening historical Gate review campaigns.

Formal review/certification is deferred to a later owner-directed epoch after the major remaining executable work is substantially complete.

Verification is still required. Review/certification is not the ordinary execution loop.

---

## 3. Current governing process policy

A fresh ChatGPT should read these current files in full before creating the first substantive Codex execution portfolio:

1. `AGENTS.md`
2. this file: `docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`
3. `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`
4. `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`
5. `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`
6. `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`
7. `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`
8. `docs/superpowers/specs/2026-09-23-execution-portfolio-orchestration-design.md`
9. `docs/superpowers/specs/2026-09-23-execution-portfolio-rejected-alternatives.md`

For current product state, read the **top current/superseding overlays** of:

- `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`
- `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`

Do not automatically ingest every historical section of those large files unless a current decision actually depends on it.

### Large Gate-0 documents

Do NOT make every fresh ChatGPT/root ingest the complete 25k-line Gate-0 V7 implementation plan.

Only the root that owns the Gate-0 Revision-18 implementation, plus any worker that genuinely needs a specific task section, should read:

`docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md`

Current exact blob:

`aad90adfedd616eee25b8302ce4f937130462bd6`

Gate-0 design:

`docs/superpowers/specs/2026-09-20-gate0-recovery-evidence-dag-design.md`

Exact blob:

`21e651503bff6dc2b369ad45923d16a3af8adf1c`

Owner plan approval:

`docs/agent-runs/run-20260923-gate0-rev18-plan-v7-final-review-v1/owner-final-implementation-plan-approval.md`

Exact blob:

`588072fab0a436881565b3ed522fc9ac8c7f222d`

Implementation authorization:

`docs/agent-runs/run-20260923-gate0-rev18-implementation-authorization-v1/owner-implementation-authorization.md`

Exact blob:

`470d39c734e71aa32b7c82804e8ed5d73847bdf7`

Gate-0 Revision-18 implementation authorization is already approved. Do not ask the owner for the same authorization again.

---

## 4. Product invariants that must never be lost

Long-term intended workflow:

`source/archive
-> deterministic inventory/provenance
-> semantic useful-moment retrieval
-> source-native temporal refinement
-> measured PTS/frame evidence
-> human editorial decision
-> versioned edit plan
-> render/export
-> technical/editorial QC`

Critical temporal rule:

- semantic/model/provider timestamps are candidate evidence only;
- exact edit/refinement boundaries come from source-native PTS/timebase evidence;
- never infer VFR frame position from seconds × nominal FPS.

Source media is immutable unless an explicitly approved policy says otherwise.

Canonical assertion-level evidence classes:

- MEASURED
- MATCHED
- VISUALLY_OBSERVED
- AUDIO_OBSERVED
- EDITORIAL_INFERENCE

`NOT_OBSERVED` is an availability/state marker, not an evidence class.

Never silently upgrade evidence strength.

---

## 5. Current authorization boundaries

The execution-first policy does NOT itself authorize:

- protected/archive-media execution;
- provider/cloud calls;
- network egress for model/provider activity;
- new model/checkpoint/weights downloads;
- profile-freeze measurement unless separately authorized;
- Homebrew/apt/yum/sudo or equivalent system-wide dependency/environment mutation;
- credentials/private-registry access;
- production render/export;
- real protected-media editing/export;
- Gate promotion;
- destructive Git cleanup;
- force push;
- canonical-main mutation by milestone roots.

For ordinary development Goals, routine project/user-local prerequisite recovery is governed by `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`. This includes bounded reuse/repair of known project environments, automatic Goal-local environments, and public package-registry retrieval required solely for routine development/test dependencies. Installing a package or SDK does not authorize using an external provider/model service.

Shared project-environment mutation is serialized under `ENV_ADMIN`; Goal-local environments remain independently creatable. A routine missing dependency is ENABLE work and is not an owner-level blocker until the v4 recovery ladder is exhausted.

Environment/import/collection failures are not behavioral TDD RED. After environment recovery, rerun the intended pre-implementation test. Post-hoc test-efficacy recovery may verify test efficacy without rewriting chronological RED history.

Gate-0 Revision-18 implementation is authorized only within its frozen approved scope.

Still preserve:

`PYTHON_NATIVE_CLOSURE_BASELINE=NOT_OBSERVED`

`GENERATION_B_ELIGIBILITY=BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`

Do not convert absence of evidence into evidence.

---

## 6. Owner's execution preference — high priority

The owner wants the remaining executable work completed rapidly with **heavy useful subagent use**.

The objective is useful wall-clock throughput, not artificial agent count.

When genuine independent READY work exists:

- delegate aggressively;
- use many children if runtime capacity permits;
- do not impose an arbitrary child ceiling such as 5, 10, 40, or 60;
- do not manufacture duplicate work merely to occupy slots;
- when one child closes, recycle its slot immediately.

Preferred Codex child policy:

- requested model family: `LUNA`
- requested reasoning: `medium`
- resolve the actually supported concrete Luna model at Goal start;
- freeze the concrete resolution for that Goal;
- explicitly set model + reasoning on eligible child spawns;
- do not silently fall back to another family.

Preferred delegation shape:

`Root Orchestrator -> Area Lead -> Worker`

Maximum default depth is three tiers.

If nested delegation is not positively supported, flatten safely to:

`Root -> Workers`

Do not block the Goal merely to preserve a preferred hierarchy.

---

## 7. Root-agent behavior

A root Codex is primarily:

- authority interpreter;
- milestone Goal decomposer;
- dependency-DAG owner;
- scheduler;
- ownership allocator;
- execution-branch integrator;
- incident adjudicator;
- milestone verifier.

The root context is the control plane, not the workbench.

When a clean ownership boundary exists, substantive coding/testing/debugging/research should be delegated.

Children should receive clean/self-contained task packets rather than the root transcript.

Compact child handoff should include as applicable:

- STATUS
- PORTFOLIO_ID / GOAL_ID / LANE_ID
- BASE_SHA
- HEAD_SHA
- CHANGED_PATHS
- PUBLIC_INTERFACES_CHANGED
- CONSUMED_CONTRACT_REFS
- PRODUCED_CONTRACT_DELTAS
- UNPLANNED_SHARED_SURFACES
- ASSUMPTION_CHANGES
- TEST_ENTRYPOINTS
- OPEN_PROBLEM_IDS
- BLOCKER
- STATE_PATH

Do not paste full diffs or long logs back into the root context unless needed.

---

## 8. Rolling-frontier scheduling

Do not run children in rigid waves.

Use continuous rolling-frontier scheduling:

`discover READY
-> allocate ownership
-> spawn useful dependency-safe work
-> receive handoff
-> validate/integrate or park
-> close child
-> unlock descendants
-> refill slot`

When all slots are occupied:

- queue additional READY work;
- do not kill productive children merely to free capacity;
- prioritize critical-path unblocks when capacity opens;
- avoid tight polling;
- root performs only nondelegable control-plane work.

---

## 9. Failure handling and Problem Catalog

Ordinary failures should not stop the whole Goal.

Flow:

`failure
-> preserve evidence
-> systematic debugging
-> evidence-supported root-cause hypothesis
-> targeted repair
-> RED/fix/GREEN where applicable
-> resolved record OR parked Problem
-> continue unaffected READY frontier`

One remediation generation means:

`evidence-supported hypothesis/repair target
-> concrete behavior-changing repair
-> observed verification result`

Default maximum:

**three evidence-supported failed remediation generations for the same load-bearing Problem/root-cause family.**

Malformed commands, invalid patches, or harness failures that never exercised the intended repair do not consume a generation.

After bounded exhaustion:

- persist the Problem;
- park affected descendants;
- close incident workers;
- continue independent READY work.

Return to the owner only for a genuine hard boundary such as:

- new authorization;
- irreversible/destructive action;
- credentials/user interaction;
- external prerequisite;
- architecture/product decision above current authority;
- technical exhaustion with no useful independent frontier.

Problem records should retain:

- symptom;
- expected vs observed behavior;
- reproduction;
- evidence;
- root-cause state;
- attempted repairs and outcomes;
- successful solution if found;
- plausible approaches not attempted and why;
- tests;
- commits;
- recurrence signature;
- severity;
- frontier impact;
- downstream dependencies;
- next action.

Do not persist hidden chain-of-thought.

---

## 10. Durable execution state

Do not recreate documentation churn.

Prefer compact machine-readable orchestration state.

Conceptual structure:

`.orchestration/
  portfolios/<portfolio-id>/manifest.json
  goals/<goal-id>/handoff.json
  goals/<goal-id>/lanes/<lane-id>.json
  problems/<goal-id>/<problem-id>.json
  convergence/<portfolio-id>/...`

Ephemeral queue/polling/slot telemetry may remain local and reconstructable.

Durable state should include only what another fresh session needs for recovery/integration.

Code/tests remain the primary engineering artifact.

---

## 11. Git/worktree model for the coming Codex execution

The owner wants multiple root Codex sessions operating concurrently on genuinely independent milestone blocks.

Do NOT use multiple permanent clones.

Use one repository plus linked Git worktrees.

Preferred local parent:

`/Users/yusuf/Repos/video-intelligence-pipeline`

Preferred worktree container if the local Git/harness accepts it safely:

`/Users/yusuf/Repos/video-intelligence-pipeline/.worktrees/execution-portfolio-v1/`

If using an in-repository `.worktrees/` directory:

- exclude it locally through `.git/info/exclude` or another non-repository local exclusion;
- do not create a tracked `.worktrees` tree merely for filesystem organization.

If the local Git/harness cannot safely use an in-repository worktree container, use one nearby dedicated linked-worktree container. Do not create four independent repository clones.

### Worktree administration

Shared worktree/ref topology is serialized.

One temporary **Portfolio Bootstrap / Worktree Admin** session creates:

- the portfolio identity;
- frozen common anchor;
- root branches;
- root linked worktrees;
- compact manifest;
- root task packets.

Substantive roots do not create/delete/prune sibling worktrees.

Substantive roots do not move sibling refs.

---

## 12. Historical 2026-09-24 first portfolio shape (superseded)

Historical note: the owner originally intended to begin that 2026-09-24 portfolio with approximately **four parallel root Codex sessions**. This is preserved as history; the 2026-10-03 Atlas authority removes any fixed four-root cap.

Four is the intended initial operating shape, but it is not permission to invent four fake-independent tasks.

Historical instruction for that bootstrap: before creating those roots, derive the dependency DAG. Current Atlas execution instead launches any useful dependency-safe READY roots.

Only create four concurrent roots if four genuinely independent or safely soft-dependent milestone fronts exist.

If only three are initially safe:

- prepare the fourth slot/task packet but do not launch it until its dependency becomes READY.

If more than four useful fronts exist:

- historical bootstrap behavior was to begin with four roots; current Atlas execution has no fixed root count and uses adaptive dependency-safe concurrency.

### Candidate capability blocks to test against the current code DAG

These are starting hypotheses, not frozen assignments:

**Candidate A — Gate-0 Revision-18 mechanical implementation**

Implement the approved V7 Gate-0 evidence-DAG plan within its existing authorization.

Important owner override:

- intermediate code review/certification is deferred;
- do not pretend frozen Task 16 review steps occurred;
- code/test/verification closure and final review closure are separate states.

**Candidate B — Semantic core productization / index lifecycle**

Stabilize the useful semantic retrieval core currently living partly under `experiments/persistent_local_index` into a stable product-facing layer/interfaces where justified.

Study:

- indexing lifecycle;
- persistence;
- exact search;
- retrieval adapter boundaries;
- incremental update/resume/recovery;
- interface ownership.

Do not assume ANN/vector DB/Redis/Kafka is needed.

**Candidate C — Multi-source archive / retrieval operational path**

Move from bounded one-file proof toward a deterministic multi-source operational path:

- inventory/provenance;
- multi-source indexing;
- incremental update;
- restart/resume;
- product-facing natural-language retrieval;
- candidate evidence only until source-native refinement.

Remain within current source/model/provider authorization.

**Candidate D — Editorial/edit pipeline generalization**

Generalize the existing functional path:

`candidate
-> source-native measured refinement
-> explicit human editorial decision
-> versioned edit plan
-> safe non-production render/QC`

Preserve non-production boundaries and exact temporal authority.

These four candidates MUST be revalidated against the current repository before root assignment. Shared-contract/path overlaps may require a different split.

Gate-1/Gate-2 work described below may replace or join one of these candidates if the dependency analysis shows it is the better independent frontier.

---

## 13. Gate-1 retained controller — disposition, not direct merge

Remote branch retained:

`controller/gate1/portfolio-v1@fdb39ea358cbf8690321df2790696669818d91d6`

Prior read-only convergence analysis concluded:

**Do not integrate Gate-1 as-is.**

Useful concepts should be reimplemented against current contracts/current Gate-0 eligibility:

- capability descriptors/common envelope;
- controlled one-axis comparisons;
- pinned controls;
- source-disjointness;
- label firewall;
- explicit omission/failure accounting;
- validity-vs-outcome separation;
- artifact/verifier/control layer.

Current disposition summary:

- reimplement contracts/schemas;
- reimplement evaluation;
- reimplement artifact/verifier layer;
- historical synthetic adapter/runner/test lock remains historical;
- real benchmark/provider/cloud/multimodal expansion remains deferred.

The old controller's real-mode eligibility logic is stale and must not be imported blindly.

No real Gate-1 winner exists merely because current local SigLIP evidence exists.

---

## 14. Gate-2 retained controller — bounded reuse only

Remote branch retained:

`controller/gate2/portfolio-v1@2ff37268d032af7287fc1f685e0e76f5b7654d2d`

Prior read-only convergence analysis concluded:

**Do not integrate Gate-2 as-is.**

Smallest potentially reusable bounded implementation:

- `src/gate2/measure.py`
- `schemas/gate2/measurement.json`

Evaluate a bounded port rather than whole-branch integration.

Reimplement against current persistent-index/FVS/resource-policy frontier:

- preregistration;
- evidence-to-mechanism decision;
- fault/workload/recovery apparatus;
- evidence/verifier/CLI.

Do not preselect:

- ANN/vector service;
- Redis/Kafka;
- durable queue/service;
- distributed lease/multi-writer;
- retry/backoff service;
- new cache infrastructure;
- persistent model daemon.

Current measured evidence has not justified those mechanisms.

Gate-2 has no code-level dependency on the old Gate-1 controller implementation.

A future real Gate-2 workload may depend on a frozen Gate-1 representation/arm identity only when the workload actually requires that choice.

---

## 15. Workspace-consolidation retained branch

Remote branch:

`transition/workspace-consolidation-v2@8f43dc1fe2fd66bd87105b0f0d7529d268c54114`

This branch was retained because it contains unique Stage-B runtime/feasibility code not fully dispositioned during branch hygiene.

Do not delete it.

Do not wholesale merge it.

Inspect it only when a current execution milestone genuinely needs that Stage-B runtime/feasibility material.

Any useful code must be deliberately ported/reimplemented against current main and current authority.

---

## 16. Dependabot branch

Remote branch:

`dependabot/npm_and_yarn/reference-pack/recurser/source/frontend/npm_and_yarn-29cc12f3e6`

It belonged to still-open PR #1 at branch-hygiene completion.

It is not a product-execution root.

Handle it independently only if dependency maintenance becomes relevant.

---

## 17. Gate-0 Revision-18 execution specifics

Gate-0 Revision-18 remains an authorized implementation candidate.

Architecture:

Option A + A2R + M1R.

Approved V7 implementation tasks are 1–16.

Do not silently widen the task.

Owner process override for this execution epoch:

- `INTERMEDIATE_REVIEW_DEFERRED_BY_OWNER=YES`
- `CERTIFICATION_DEFERRED_BY_OWNER=YES`

This means:

- implement code/tests required by the plan;
- run deterministic/focused/integration verification;
- use TDD/systematic-debugging;
- do not create reviewer/certifier waves;
- do not claim frozen review/certification substeps completed when they were intentionally deferred;
- record code/test completion separately from deferred final review closure.

Still unauthorized:

- profile-freeze measurement;
- venv provisioning/dependency download unless separately authorized;
- Homebrew/pip;
- otool/file/host scans to manufacture profile-freeze evidence;
- build/sign;
- Generation B/live Stage B;
- provider/model/network activity;
- protected/archive media;
- runtime-policy approval;
- Gate promotion;
- destructive cleanup;
- force push;
- canonical-main mutation by the milestone root.

---

## 18. Convergence model after the first parallel roots

Do not merge Root A/B/C/D directly just because each says it finished.

After milestone roots finish, use fresh convergence context as needed.

Default conceptual phases:

1. **CONVERGENCE ANALYSIS**
   - inspect exact completed root heads;
   - inspect terminal milestone handoffs;
   - detect textual overlaps;
   - detect API/schema/config/dependency/semantic conflicts;
   - build a semantic-conflict matrix;
   - do not merge yet.

2. **RESOLUTION DESIGN**
   - determine reconciled interfaces;
   - determine integration order;
   - decompose required fixes.

3. **REMEDIATION EXECUTION**
   - implement convergence fixes with TDD/bounded debugging.

4. **INTEGRATION**
   - combine branches on an isolated integration branch/worktree;
   - run integration/regression verification;
   - still do not merge canonical main automatically.

These may collapse when trivial.

Clean Git merge is not proof of semantic compatibility.

---

## 19. What must happen before substantive root Codex sessions start

There are two preparation stages.

### Stage S0 — local/remote synchronization

Use one bounded Codex admin session on the primary local repository.

Its job is ONLY:

- fetch/prune/fetch tags;
- confirm local vs remote main;
- safely fast-forward local main if possible;
- verify the preservation tag;
- verify current remote branch surface;
- inventory local-only branches/worktrees;
- preserve unknown local state;
- report blockers.

It must NOT:

- delete local-only branches;
- delete worktrees;
- clean dangling objects;
- force anything;
- modify product code;
- create execution worktrees yet.

A ready-to-send S0 prompt is provided separately by the ChatGPT session that created this handoff.

### Stage S1 — Portfolio Bootstrap / Worktree Admin

Only after S0 is clean enough.

Use one fresh bounded Codex admin session.

S1 is **not product implementation**.

It must:

1. re-read current repository authority;
2. inspect actual current code/dependencies;
3. derive/freeze the first Execution Portfolio DAG;
4. confirm whether four initial roots are genuinely dependency-safe;
5. freeze one common portfolio anchor SHA from current main or another explicitly justified base;
6. create one portfolio ID;
7. create the root execution branches;
8. create linked worktrees for the roots;
9. create compact portfolio manifest/task packets;
10. assign expected write domains and shared-contract surfaces;
11. verify no root branch/worktree points at canonical main;
12. verify worktree/ref administration ownership;
13. resolve/freeze the current Codex LUNA/medium model identity for the coming Goals where the harness supports inspection;
14. verify heavy-resource lease rules;
15. run no product implementation.

Preferred root labels may be A/B/C/D for human convenience, but their milestone names should describe capabilities, not letters.

No substantive root Goal is sent until S1 terminal verification passes.

---

## 20. What a prepared root worktree contains

Do not manually copy a curated mini-repository into each worktree.

A linked Git worktree is a full checkout of its assigned root branch.

Preparation should provide through Git:

- the common repository state from the frozen portfolio anchor;
- current process policy;
- relevant code/tests;
- compact portfolio manifest;
- that root's task packet;
- shared-contract references;
- Problem/state paths.

The root should not waste context reconstructing branch topology, making its own worktree, or guessing its authority.

Its first substantive action should be milestone execution.

---

## 21. Root task-packet minimum

Each root task packet should bind:

- PORTFOLIO_ID
- ROOT_ID
- GOAL_ID
- exact BASE_SHA
- root branch
- worktree path
- capability outcome
- PARALLEL_CLASS
- dependencies
- expected read paths
- exclusive write paths/domains
- shared-contract surfaces
- prohibited scope
- required tests/acceptance outcomes
- model family/reasoning policy
- heavy-resource restrictions
- durable state/handoff paths
- relevant Problem IDs
- terminal states
- no-main-merge rule

Do not include the full historical chat.

---

## 22. Stale-base rule

Every child/root candidate must preserve its original BASE_SHA.

If parent/portfolio state advances:

- current + disjoint paths/contracts -> safe non-destructive integration + verification;
- stale + overlapping paths/contracts/migrations/assumptions -> do not blindly cherry-pick/rebase; park and reconcile from the current head.

No agent may hide staleness by rewriting reported base.

---

## 23. Shared-contract ownership

Before parallel root launch, freeze current shared-contract surfaces.

Examples:

- public APIs;
- schemas;
- canonical evidence/provenance types;
- temporal/timebase contracts;
- common config;
- central registries;
- lock/dependency files;
- CLI contracts.

If a root must change one:

- keep the change isolated on its branch;
- record `UNPLANNED_SHARED_SURFACE`;
- record `PRODUCED_CONTRACT_DELTA`;
- identify known consumers;
- do not repair sibling branches directly.

Convergence handles the reconciliation later.

---

## 24. Review/certification rule — do not regress

The project deliberately stopped the previous review/certification treadmill.

During the code-completion epoch:

DO:
- TDD;
- tests;
- integration/regression checks;
- static/deterministic checks;
- systematic debugging;
- verification-before-completion;
- bounded incident cells.

DO NOT:
- task reviewer after every implementation;
- batch certifier;
- recertification wave;
- repeated review memo generation;
- independent reviewer swarms as routine progress.

Final review/certification may be performed later if the owner requests it.

---

## 25. What the fresh ChatGPT should do when the owner says “start Codex implementation”

Do NOT immediately output four giant Goals.

First:

1. verify current GitHub main and retained branches;
2. read the current execution-policy files listed in §3;
3. inspect the owner's S0 Codex sync report;
4. if S0 is clean, prepare/issue exactly one S1 Portfolio Bootstrap/Admin Goal;
5. inspect S1's resulting DAG, root branches, worktrees, task packets, and authority bindings;
6. independently verify the bootstrap from GitHub plus the S1 local report;
7. only then generate the substantive root Goals.

The user should not have to re-explain this architecture.

---

## 26. Avoid unnecessary re-analysis

Do not repeat already settled work merely because the session is fresh.

Already settled:

- execution-first policy;
- final-review-later policy;
- branch-hygiene architecture;
- remote branch cleanup;
- Gate-0 authority promotion;
- Gate-1/Gate-2 whole-branch non-integration decision;
- linked-worktree parallel-root architecture;
- rolling-frontier scheduling;
- Problem Catalog/bounded remediation;
- convergence-before-merge model.

Reopen a settled decision only if current repository evidence actually falsifies an assumption.

---

## 27. Known local-state caveat

Remote branch cleanup deliberately did NOT clean the user's pre-existing local worktrees/local-only branches.

Known historical local paths may include:

- `/Users/yusuf/Repos/video-intelligence-pipeline`
- `/Users/yusuf/Repos/video-intelligence-pipeline-gate0`
- `/Users/yusuf/Repos/video-intelligence-pipeline-gate1`
- `/Users/yusuf/Repos/video-intelligence-pipeline-gate2`
- `/Users/yusuf/Repos/video-intelligence-pipeline-gate3`

Do not assume they are clean, current, or disposable.

S0 must inventory them.

A prior local `git fsck --connectivity-only` also reported:

- invalid local ref artifact `.git/refs/.DS_Store`;
- dangling Git objects.

Do not prune/delete those merely to make output clean.

If they actually obstruct the coming bootstrap, diagnose first and request explicit authority before destructive repair.

---

## 28. Expected near-term sequence

The intended near-term sequence is:

`S0 Codex local/remote sync
-> fresh ChatGPT verifies S0
-> S1 Codex Portfolio Bootstrap/Admin
-> ChatGPT independently verifies S1
-> historical 2026-09-24 target was approximately four roots; current Atlas uses adaptive READY-root concurrency
-> rolling execution
-> convergence analysis
-> resolution/remediation if required
-> isolated portfolio integration
-> owner-controlled canonical-main integration
-> continue next portfolio
-> final review/certification later`

Do not insert another branch-hygiene or review campaign between these steps unless new evidence creates a genuine blocker.

---

## 29. Completion standard for S1

The project is READY_TO_START_SUBSTANTIVE_CODEX_EXECUTION only when all are true:

- local primary repo has a known synchronized main state;
- unknown local worktree state is inventoried;
- portfolio base/anchor is exact;
- root DAG is explicit;
- historical four-slot bootstrap state was either READY or dependency-parked; current Atlas tracks an adaptive READY set instead;
- every launched root has a unique branch and linked worktree;
- no execution worktree is canonical main;
- expected write domains are explicit;
- shared-contract surfaces are explicit;
- task packets exist;
- current Codex model resolution is recorded where observable;
- heavy-resource rule is recorded;
- main-merge prohibition is explicit;
- no product code was changed during S1.

Then and only then start substantive root Goals.

---

## 30. Fresh-session bootstrap sentence

If a new ChatGPT needs one sentence to orient itself:

> Branch hygiene and execution-policy redesign are complete. Verify current GitHub, read this handoff plus the current execution protocols, validate the user's S0 local/remote sync report, then prepare one non-implementation Portfolio Bootstrap/Admin Codex session that creates the dependency-safe linked-worktree/task-packet environment for the first approximately four parallel implementation roots; do not restart audits, reviews, branch cleanup, or product coding before that bootstrap is verified.
