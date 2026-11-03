# Remaining Work Execution Atlas Implementation Plan

**Status:** OWNER-APPROVED — CHUNKED EXECUTION IN PROGRESS  
**Execution start:** 2026-10-03  

> **For agentic workers:** Execute this plan under the repository-specific **Execution Portfolio Parallel** method defined by the governing spec. Use Superpowers `dispatching-parallel-agents` for independent READY work, `test-driven-development` for behavior changes, `systematic-debugging` for unexpected failures, and `verification-before-completion` before completion claims. Do **not** use stock `subagent-driven-development` by default because its mandatory reviewer-per-task loop conflicts with the current execution-first owner policy. Use per-task review only where this plan explicitly marks `PER_TASK_REVIEW_REQUIRED`.

**Goal:** Materialize the owner-approved Remaining Work Execution Atlas operating system so future ChatGPT/Codex sessions can finish the repository through prebuilt, versioned, dependency-aware prompt packets with concurrent BUILD / VERIFY / REPAIR frontiers instead of repeated serial replanning.

**Architecture:** First reconcile current repository process authority and introduce adaptive resource-policy v5. Then create machine-readable Atlas/prompt/launch-pack schemas plus a deterministic verifier. Next derive the actual H0/H1/H2/H3 remaining-work table of contents from current Git/local evidence, freeze dependency/contract fingerprints and weights, generate versioned H3 prompt cores chapter-by-chapter, and render numbered Launch Packs. The repository becomes the durable execution memory; fresh controllers perform narrow Launch Delta Reconciliation rather than redesigning the project.

**Tech Stack:** Git/GitHub, Markdown, YAML, JSON, Python 3 stdlib, existing repository verification scripts/tests, Superpowers execution workflows.

**Spec:** `docs/superpowers/specs/2026-10-03-remaining-work-execution-atlas-and-parallel-verification-design.md`

## Global Constraints

- Canonical source/archive media remains immutable.
- Semantic/model/provider timestamps remain candidate evidence only.
- Exact temporal work uses source-native PTS/timebase evidence.
- Never infer VFR frame positions as seconds × nominal FPS.
- Assertion classes remain MEASURED, MATCHED, VISUALLY_OBSERVED, AUDIO_OBSERVED, EDITORIAL_INFERENCE; NOT_OBSERVED remains a state marker.
- No protected/archive-media execution, provider/cloud calls, model/checkpoint downloads, production render/export, or Gate promotion unless separately and currently authorized.
- No destructive Git, hard reset, git clean, force push, reflog destruction, or branch/worktree destruction.
- Canonical-main writes are allowed only under the owner's explicit current authorization and after the exact change set has passed the relevant plan phase checks.
- Existing historical policy/evidence artifacts remain historical; prefer supersession/versioning over rewriting provenance.
- Independent READY work should remain active; one long-running BUILD/TEST/REVIEW/REPAIR lane must not globally serialize the portfolio.
- New H3 execution packets default to fresh top-level Codex sessions.
- Detailed worker output belongs in durable/file-backed state; human chat receipts remain compact.
- Stock Superpowers `subagent-driven-development` is not the default executor for H3/H4 because it mandates review after every inner plan task. Default execution is repository-native multi-root/multi-subagent rolling-frontier execution; completed H3 candidates still receive asynchronous feature-level `requesting-code-review` before integration.

## Execution Method Already Selected by Owner

The owner has explicitly selected:

`EXECUTION_METHOD=EXECUTION_PORTFOLIO_PARALLEL`

This means:

- fresh top-level Codex roots for new H3 packets by default;
- root/main Codex acts primarily as scheduler/integrator;
- independent H4 work is dispatched concurrently;
- workers close when terminal and slots recycle immediately;
- BUILD, VERIFY, and REPAIR frontiers proceed concurrently;
- every completed H3 candidate is queued for feature-level code review on the parallel VERIFY frontier before integration, while broader certification remains deferred to designated milestone/convergence/finalization points;
- the owner will ask to proceed in chunks rather than requesting one monolithic execution run.

## Review Focus

1. **Authority ambiguity:** a fresh controller must resolve one current execution authority, not conflicting v4/four-root/review-loop wording.
2. **Stale speculative work:** an upstream contract delta must not permit a stale in-flight descendant to integrate as current.
3. **Verification generation binding:** test/review evidence must name the exact candidate SHA/tree and cannot float to a repaired candidate automatically.
4. **Prompt drift:** a fresh ChatGPT must not regenerate Frozen Cores merely because prior chat context is gone.
5. **Parallel test interference:** ports/temp dirs/caches/global state/heavy resources must be isolated or explicitly SERIAL.

---

## Phase 0 — Evidence and authority preflight

### Task 0.1: Reverify remote canonical state and current authority

**Read:**
- `AGENTS.md`
- `docs/INDEX.md`
- `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`
- `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`
- `docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`
- `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`
- `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`
- `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`
- `docs/portfolio/portfolio-v1/resource-policy-v4.yaml`
- the approved Atlas spec.

**Produces:** a compact preflight record containing:
- canonical `main` SHA;
- current planning-branch SHA;
- current authority files + blob SHAs;
- current resource-policy version;
- current task-4/local-lineage references known from Git;
- whether any remote state has advanced since plan creation.

**Checks:**
- non-destructive fetch;
- no mutation;
- no hidden assumption that the planning branch is still based on current main.

### Task 0.2: Inventory relevant local-only branches/worktrees

**Purpose:** The current Gate-0 Task-3/Task-4 lineage includes local-only/unpushed work that GitHub alone cannot fully represent.

**Produces:** a durable inventory of:
- local branch/worktree path;
- HEAD;
- clean/dirty;
- upstream/push state;
- relation to canonical main;
- disposition relevance to Atlas;
- do-not-delete marker.

**Rules:**
- no cleanup;
- no reset/rebase;
- no destructive reconciliation;
- preserve exact local-only evidence.

**Completion:** the Atlas creation step has enough evidence to avoid silently omitting accepted local work.

---

## Phase 1 — Promote the execution model into current repository authority

### Task 1.1: Amend `AGENTS.md`

**Modify:** `AGENTS.md`

**Required semantic changes:**
- point fresh agents to the Remaining Work Atlas / `CONTROLLER_START_HERE` after it exists;
- state that numeric chapter order is not a scheduling barrier;
- define BUILD / VERIFY / REPAIR as concurrent rolling frontiers;
- state that standard `subagent-driven-development` is not the ordinary H3 executor;
- route independent execution to `dispatching-parallel-agents`;
- require stale-in-flight descendants to be non-integrable after consumed-contract invalidation;
- replace any stale “approximately four roots” interpretation with adaptive top-level concurrency;
- retain exclusive path ownership and safety rules.

**Verification:**
- grep/manual contract check for contradictory root-count/review-loop language;
- `bash scripts/verify-workspace.sh` where safe/meaningful, preserving baseline failures rather than “fixing” unrelated checks.

### Task 1.2: Amend throughput and torrent protocols

**Modify:**
- `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`
- `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`

**Add/freeze:**
- chapter overlap;
- BUILD/VERIFY/REPAIR concurrent frontiers;
- progressive verification at H3 candidate level;
- Launch Delta Reconciliation;
- Launch Packs;
- prompt Frozen Core / Launch Overlay;
- exact candidate-generation binding;
- stale-in-flight behavior;
- contract fingerprints;
- short chat receipts;
- adaptive top-level concurrency;
- test/review sharding;
- verifier evidence reuse only when coverage is mechanically unaffected.

**Guard:** do not weaken source/evidence/temporal/authority invariants.

### Task 1.3: Supersede bootstrap “four-root” wording

**Modify:**
- `docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`
- `docs/INDEX.md` if needed.

**Requirement:** preserve the historical fact that four roots were once an intended initial shape while clearly marking that it is no longer the current throughput cap.

### Task 1.4: Create resource policy v5

**Create:** `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`

**Do not rewrite:** v4 historical content.

**v5 minimum fields:**
- `schema_version: 5`
- current execution authority refs;
- adaptive root writer policy;
- H3/H4 executor-mode rules;
- lease classes:
  - `LIGHTWEIGHT_CPU_TEST`
  - `HEAVY_CPU`
  - `FFMPEG_HEAVY`
  - `MODEL_MPS`
  - `MIXED_HEAVY`
  - `ENV_ADMIN`
- initial ordinary-development leases:
  - HEAVY_CPU: 2
  - FFMPEG_HEAVY: 2
  - MODEL_MPS: 2 only when an already-authorized local model/runtime is available
  - ENV_ADMIN: 1
- calibration target for 3 concurrent HEAVY_CPU/FFMPEG jobs;
- fail-soft lease reduction;
- no global serialization of lightweight work after one heavy-resource failure;
- no model download/provider activity authorization.

**Then update current-policy references** in AGENTS/protocols from v4 to v5 where they describe current policy, preserving historical v4 references in old evidence.

### Task 1.5: Policy contradiction audit

**Read-only check across current authority surfaces** for:
- fixed four-root ceiling;
- universal heavy max=1;
- mandatory per-task reviewer loops;
- “chapter complete before next chapter” implications;
- stale v4 “current policy” labels.

**Expected:** one current interpretation after the planned edits.

**Commit:** one coherent policy-promotion commit on the execution/policy branch.

### Task 1.6: Early canonical-main policy promotion

The owner has explicitly authorized the current process/policy updates needed to make this execution model authoritative.

After Tasks 1.1–1.5 pass their checks:

1. prepare the exact policy-only promotion set;
2. verify no Atlas/generated prompt content is accidentally included;
3. promote the verified policy candidate to canonical main non-destructively;
4. fetch/read back main;
5. confirm fresh-session reading order now points to v5/execution-first concurrent semantics;
6. record resulting main SHA.

This early promotion exists specifically so a future ChatGPT context cannot fall back to the historical four-root/max=1/review-heavy interpretation while later Atlas chunks are still being built.

---

## Phase 2 — Machine-readable Atlas contracts

### Task 2.1: Define Atlas schema

**Create:**
- `schemas/orchestration/remaining-work-atlas.schema.json`

**Required node fields:**
- `id`
- `level` = H0/H1/H2/H3
- `title`
- `parent_id`
- `weight`
- `state`
- `candidate_generation`
- `dependencies[]`
- `consumed_contracts[]`
- `produced_contracts[]`
- `write_domain[]`
- `resource_class`
- `executor_mode`
- `prompt_core_ref`
- `overlay_ref`
- `verification_ref`
- `problem_ids[]`
- `unlocks[]`

**Dependency enum:**
- INDEPENDENT
- SOFT_BUILD_DEPENDENCY
- HARD_BUILD_DEPENDENCY
- HARD_VERIFY_DEPENDENCY

**State enum:**
- PLANNED
- READY
- BUILDING
- BUILD_GREEN
- VERIFY_READY
- VERIFYING
- VERIFIED
- REPAIRING
- PARKED
- DIRTY_BY_CONTRACT_DELTA
- STALE_IN_FLIGHT
- SUPERSEDED

### Task 2.2: Define prompt-packet schema

**Create:**
- `schemas/orchestration/remaining-work-prompt-packet.schema.json`

**Frozen Core required fields:**
- task identity;
- core version/hash;
- goal;
- dependencies;
- expected deliverables;
- read/write domains;
- consumed contract fingerprints;
- prohibited scope;
- focused tests;
- verification hooks;
- H4 decomposition guidance;
- mandatory parallelism contract;
- failure policy;
- terminal receipt schema.

**Launch Overlay required fields:**
- exact BASE SHA;
- dependency heads;
- branch/worktree;
- open Problems;
- contract deltas;
- current resource leases;
- resolved model identity;
- reconciliation head/version.

### Task 2.3: Define Launch Pack schema

**Create:**
- `schemas/orchestration/remaining-work-launch-pack.schema.json`

**Required:**
- batch ID/version;
- generated-at candidate/control HEAD;
- ordered prompt entries;
- task labels;
- READY status;
- executor mode;
- resource lease;
- copy-ready prompt path;
- blocked/held entries with reason.

### Task 2.4: Add deterministic Atlas verifier

**Create:**
- `scripts/verify-remaining-work-atlas.py`
- `tests/scripts/test_verify_remaining_work_atlas.py`

**Tests first (RED):**
1. duplicate IDs refuse;
2. unknown parent refuses;
3. total leaf H3 weight for the active H0 finish line not equal to 100 refuses at baseline freeze; H1/H2 weights are derived aggregates, not additional denominator weight;
4. dependency cycle refuses;
5. invalid state/ref combination refuses;
6. READY node with unsatisfied HARD dependency refuses;
7. BUILD_GREEN node without candidate SHA refuses;
8. VERIFYING/VERIFIED result without exact candidate generation refuses;
9. prompt core hash mismatch refuses;
10. contract fingerprint mismatch marks/returns dirty state;
11. stale-in-flight node cannot be accepted/integrated;
12. overlapping exclusive write ownership in same READY batch refuses;
13. incompatible heavy leases refuse;
14. Launch Pack entry for non-READY task refuses.

**Implementation:** Python stdlib only where practical.

**Verification:** focused test file then repository-relevant regression subset.

---

## Phase 3 — Durable controller bootstrap

### Task 3.1: Create `CONTROLLER_START_HERE`

**Create:**
- `.orchestration/remaining-work/CONTROLLER_START_HERE.md`

**Must tell a fresh ChatGPT/controller exactly:**
1. what to read;
2. what not to reread by default;
3. how to find current Atlas state;
4. how to consume short Codex receipts;
5. how to perform Launch Delta Reconciliation;
6. how to identify READY work;
7. why Frozen Cores are not regenerated casually;
8. how executor mode is selected;
9. when owner escalation is actually required.

### Task 3.2: Create compact state directories/templates

**Create only durable templates needed for recovery:**
- `.orchestration/remaining-work/atlas/`
- `.orchestration/remaining-work/prompts/`
- `.orchestration/remaining-work/launch-packs/`
- `.orchestration/remaining-work/verification/`
- `.orchestration/remaining-work/problems/`
- `.orchestration/remaining-work/convergence/`

Avoid narrative memo churn.

### Task 3.3: Fresh-session recovery test

**Add a deterministic test/check** proving a controller can locate:
- current policy version;
- Atlas;
- active finish line;
- current Launch Pack;
- prompt core version/hash;
- current progress summary;
- open blocker/problem refs.

This may live in the Atlas verifier test module if no separate script is needed.

---

## Phase 4 — Build the actual Remaining Work Table of Contents

### Task 4.1: Define active finish line

Create an Atlas metadata record with:

`ACTIVE_FINISH_LINE=VERIFICATION_COMPLETE_FOR_CURRENT_AUTHORIZED_LOCAL_FIRST_SCOPE`

The H0=100 denominator includes all remaining implementation + verification required for that currently authorized local-first target.

Separately track an authority-dependent backlog for:
- protected/archive-media execution;
- provider/cloud activity;
- production render/export;
- Gate promotion;
- any other separately authorized future evidence.

Those items remain visible but outside the H0 denominator until explicit authority expands/rebaselines the finish line.

### Task 4.2: Derive H1 chapters from current repo evidence

Use:
- canonical main;
- current project overlays;
- current open problem/frontier records;
- accepted Gate-0 Task-3 lineage;
- local Task-4 successor spec lineage;
- retained Gate-1/Gate-2 evidence;
- FVS/local-real preview lineage;
- unfinished execution-portfolio roots/contract deltas;
- known integration/convergence debt.

**Output:** human-readable H1 chapter list plus machine-readable Atlas nodes.

**Rule:** chapter count is evidence-driven, not artificially fixed.

### Task 4.3: Derive H2/H3 workstreams and execution packets

For every H1:
- identify coherent H2 workstreams;
- split H3 at meaningful ownership/test boundaries;
- avoid 2-minute microtasks;
- aim for H3 packets substantial enough for a fresh Codex to sustain tens of minutes of useful orchestration when possible;
- identify candidate H4 concurrency surfaces.

### Task 4.4: Freeze dependency DAG and contract fingerprints

For every H3:
- classify dependencies;
- record exact consumed contracts/blobs/interfaces;
- identify write domains;
- mark heavy resource class;
- mark executor mode;
- identify what can start speculatively.

### Task 4.5: Freeze H0=100 remaining-work weights

Assign relative weights across H3 nodes.

Rules:
- total = 100;
- preserve baseline denominator;
- newly discovered necessary work subdivides uncompleted weight where possible;
- true scope expansion requires explicit rebaseline record.

### Task 4.6: Table-of-contents quality pass

Check only for:
- missing current work;
- duplicated work;
- impossible dependencies;
- artificial chapter barriers;
- giant H3 packets that should split;
- tiny H3 packets that should merge;
- unsafe shared writers.

Do not reopen settled product architecture during this pass.

**Milestone output:** a frozen, reviewable “book contents” for all known remaining work.

---

## Phase 5 — Prompt Packet Library

### Task 5.1: Create canonical H3 Frozen Core template

**Create:**
- `.orchestration/remaining-work/prompts/_template/core.md`
- `.orchestration/remaining-work/prompts/_template/overlay.json`

Core must include the mandatory H3 parallelism contract from the spec.

### Task 5.2: Create short terminal receipt template

**Create:** a compact machine/human-readable receipt schema/template.

Fields:
- TASK
- STATUS
- BASE_SHA
- HEAD_SHA
- CHANGED_PATHS
- FOCUSED_TESTS
- OPEN_PROBLEMS
- CONTRACT_DELTA
- DURABLE_HANDOFF
- UNLOCKS
- PUSH_STATUS

### Task 5.3: Generate Frozen Cores chapter-by-chapter

For each H1:
1. generate H3 cores from the frozen Atlas;
2. bind consumed contract fingerprints;
3. specify H4 decomposition guidance;
4. specify main-agent/supervisor/worker roles;
5. specify executor mode;
6. specify focused tests and failure policy;
7. hash/version the core;
8. validate with the Atlas verifier;
9. include an asynchronous H3 feature-review hook so BUILD_GREEN enqueues `requesting-code-review` on the VERIFY frontier before integration without blocking unrelated BUILD.

Do this one H1 at a time so the owner/controller can request another refinement pass without regenerating the whole library.

### Task 5.4: Add prompt invalidation logic

The verifier/controller logic must distinguish:
- upstream implementation SHA changed but consumed contract unchanged -> packet remains valid;
- consumed contract fingerprint changed -> packet becomes DIRTY;
- authority changed -> packet blocked/dirty as appropriate.

---

## Phase 6 — Launch Pack tooling

### Task 6.1: Create Launch Pack renderer

**Create:**
- `scripts/render-remaining-work-launch-pack.py`
- `tests/scripts/test_render_remaining_work_launch_pack.py`

**Behavior:**
- consume Atlas + prompt cores + current overlays;
- select maximum useful READY set subject to ownership/resource constraints;
- render numbered copy-ready prompt files;
- default each new H3 to a fresh Codex;
- include task label at top;
- include no hidden dependency on remembering an old chat.

### Task 6.2: Test batch selection

RED/GREEN tests:
- independent READY H3 packets appear together;
- overlapping writers cannot appear together;
- HARD dependency blocks;
- SOFT dependency unlocks after upstream BUILD_GREEN;
- VERIFY work can coexist with later BUILD;
- REPAIR work can coexist with unrelated BUILD;
- resource leases bound heavy selection;
- stale/dirty packets do not launch;
- no fixed four-root cap.

### Task 6.3: Generate first Launch Pack

Generate the first real batch but **do not dispatch it yet**.

This is the milestone at which the user can first see that all machinery is ready while prompt execution remains intentionally unstarted.

---

## Phase 7 — Heavy-resource calibration and adaptive v5 leases

### Task 7.1: Prepare safe calibration fixtures

Use only synthetic/non-protected inputs already authorized.

No model download solely for calibration.

### Task 7.2: Calibrate heavy CPU / FFmpeg

Measure:
1. baseline single-job wall clock;
2. 2 concurrent jobs;
3. if stable and throughput improves, 3 concurrent jobs.

Record:
- total throughput;
- per-job wall time;
- errors/timeouts;
- resource pressure observations;
- determinism where relevant.

### Task 7.3: Calibrate model/MPS separately

Only if an already-authorized local model/runtime is available.

Try 2 concurrent jobs first.

If unstable/slower, lower MODEL_MPS lease without changing other lease classes.

### Task 7.4: Update measured lease fields

Update v5 measured values and record:
- tested concurrency;
- accepted lease;
- fallback lease;
- evidence timestamp/environment.

No global return to max=1 merely because one class fails.

---

## Phase 8 — Launch Delta Reconciliation and readiness freeze

### Task 8.1: Implement first reconciliation pass

Consume:
- current Atlas;
- first policy/Atlas commits;
- any local branch changes since TOC freeze;
- verification/problem records.

Output:
- newly READY;
- newly DIRTY;
- newly PARKED;
- stale in-flight;
- next Launch Pack.

### Task 8.2: Final pre-dispatch consistency verification

Run:
- Atlas verifier;
- prompt hash verification;
- Launch Pack renderer tests;
- current policy-reference grep;
- relevant workspace/secret checks;
- Git status/diff;
- current main/branch synchronization checks.

### Task 8.3: Freeze “PROMPTS_READY_FOR_DISPATCH”

Only after fresh verification.

Expected terminal state for this implementation plan:

- `ATLAS_READY=YES`
- `TABLE_OF_CONTENTS_FROZEN=YES`
- `PROMPT_LIBRARY_READY=YES`
- `FIRST_LAUNCH_PACK_READY=YES`
- `RESOURCE_POLICY_V5_ACTIVE_OR_CALIBRATION_RECORDED=YES`
- `PROMPTS_DISPATCHED=NO`

At that point the owner can begin the actual remaining-project execution by copying prompts from the Launch Pack into fresh Codex sessions.

---

## Phase 9 — Controlled Atlas/tooling main promotion

Core process/policy authority was already promoted early in Task 1.6. This phase promotes the now-complete Atlas/tooling/prompt-library surfaces after Phase 8.

### Task 9.1: Prepare exact current-authority promotion set

List exact changed current-policy/Atlas/tooling files and exact candidate SHA.

### Task 9.2: Verify promotion candidate

Run all Phase-8 checks again on the exact candidate.

### Task 9.3: Promote to canonical main

The owner has explicitly authorized the process/policy and Atlas/tooling changes in this conversation, including canonical-main updates needed to make the new execution model current.

Promotion must still:
- be non-destructive;
- preserve history;
- avoid force push;
- use the exact verified candidate;
- record resulting main SHA.

### Task 9.4: Fresh-main readback

From updated main:
- re-read current policy refs;
- verify v5/Atlas discovery;
- verify first Launch Pack remains consistent with the promoted state;
- render/validate again if main SHA changes the launch overlay.

---

## Chunk Boundaries for This ChatGPT Project

The owner requested incremental execution rather than one large run.

Recommended conversational chunks:

**Chunk A — Policy authority**
- Phase 0
- Phase 1, including early policy-only canonical-main promotion

**Chunk B — Atlas machinery**
- Phase 2
- Phase 3

**Chunk C — “Book contents”**
- Phase 4 only

**Chunk D1...Dn — Prompt cores**
- Phase 5 one H1 chapter at a time

**Chunk E — Launch machinery**
- Phase 6

**Chunk F — Resource calibration**
- Phase 7

**Chunk G — Reconciliation/readiness**
- Phase 8

**Chunk H — Main promotion/readback**
- Phase 9

The owner may say only “devam edelim”; resume at the earliest incomplete chunk/task from durable repo state. Do not reinterpret that as permission to redesign completed chunks.

---

## Completion and Verification Contract

No chunk is called complete solely because an agent says it is complete.

Before each chunk completion claim:
1. inspect Git diff/changed paths;
2. run the chunk's declared deterministic checks;
3. verify exact candidate SHA;
4. record compact handoff/state;
5. preserve open Problems;
6. report only actual verified status.

This implementation plan creates the execution operating system and prompt library. It does **not** itself execute the remaining product H3 packets.
