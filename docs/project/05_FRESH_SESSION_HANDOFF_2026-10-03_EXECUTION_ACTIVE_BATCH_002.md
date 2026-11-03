# Video Intelligence Pipeline — Fresh Session Handoff — Execution Active / Batch-002

**Date:** 2026-10-03  
**Purpose:** authoritative fresh-session continuation handoff after Batch-001 execution, Launch Bootstrap v2.0.3 hardening, and Batch-001 reconciliation.  
**Current canonical main at handoff creation:** `71c471a7aa61914038caf096e5155225527c44ef`  
**Canonical main commit message:** `Merge PR #36: reconcile batch-001 receipts and prepare batch-002 frontier`

This file is a continuation aid, not a new source of architectural authority. Repository evidence still wins. If any SHA/state below conflicts with current GitHub, verify current `main` and use the current repository state.

---

## 1. Fresh-session bootstrap — do this first

A new ChatGPT/controller must not resume from chat memory alone.

Read, in order:

1. `AGENTS.md`
2. `docs/project/00_PROJECT_CHARTER.md`
3. `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`
4. `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`
5. `docs/project/STATE_MAINTENANCE_PROTOCOL.md`
6. **this file**
7. `.orchestration/remaining-work/CONTROLLER_START_HERE.md`
8. `.orchestration/remaining-work/controller-state.json`
9. `.orchestration/remaining-work/atlas/atlas.json`
10. `.orchestration/remaining-work/atlas/progress.json`
11. `.orchestration/remaining-work/reconciliation/batch-001-reconciliation-20261003.json`
12. `.orchestration/remaining-work/launch-packs/batch-002/manifest.json`

Then independently verify current GitHub `main` before acting.

Do **not** trust this handoff over newer repository evidence.

---

## 2. What the project is still trying to achieve

The project remains a local-first / selectively hybrid video-intelligence pipeline for a large dance, ballet, music, and performing-arts video archive.

Long-term flow remains:

`source/archive → deterministic inventory/provenance → semantic useful-moment retrieval → source-native temporal refinement → measured PTS/frame evidence → human editorial decision → versioned edit plan → render/export → technical/editorial QC`

Key scientific/technical invariants remain unchanged:

- semantic/model/provider timestamps are candidate evidence only;
- exact edit boundaries require source-native PTS/timebase evidence;
- never infer VFR frame positions with seconds × nominal FPS;
- source media is immutable unless separately authorized;
- evidence classes are `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, `EDITORIAL_INFERENCE`;
- `NOT_OBSERVED` is an availability/state marker, not an evidence class;
- no protected/archive/provider/production/Gate-promotion work is implicitly authorized by Remaining Work execution.

---

## 3. Current orchestration architecture — already approved, do not redesign

The owner-approved Remaining Work Atlas architecture remains current.

Current execution model:

- H0/H1/H2/H3 hierarchy plus execution DAG;
- H4 concurrent subagent shards;
- BUILD / VERIFY / REPAIR frontiers can proceed concurrently;
- rolling-frontier scheduling;
- exclusive writer ownership;
- immutable candidate generations;
- Frozen Core + Launch Overlay + Launch Pack;
- Launch Delta Reconciliation between batches;
- asynchronous feature review;
- adaptive resource leases under resource-policy v5;
- repository/Git is durable memory; chat is not.

Authority order remains:

`explicit user authorization > frozen architecture/governing specs > approved design > implementation plan > task packet > controller ruling > child implementation choice`

Do not create a new architecture/spec/implementation-plan cycle merely because execution has progressed.

---

## 4. Superpowers routing remains trigger-based

Use current verified skill names only.

Important routing:

- new architecture/behavior/subsystem/interface design → `brainstorming`
- approved design requiring detailed executable tasks → `writing-plans`
- implementation isolation → `using-git-worktrees`
- 2+ genuinely independent tasks → `dispatching-parallel-agents`
- behavior change → `test-driven-development`
- unexpected failure/integration issue → `systematic-debugging`
- completed candidate before convergence/integration → `requesting-code-review`
- review feedback → `receiving-code-review`
- success/completion claim → `verification-before-completion`

Do not default to stock `subagent-driven-development`; use it only when the packet/executor mode explicitly requires it.

---

## 5. Completed preparation/hardening — DO NOT REDO

These preparation stages are already complete:

- Remaining Work Atlas design and implementation plan approved.
- Full Frozen Core library completed: 33 cores across H1-A..H1-G.
- 33/33 Frozen Core semantic/hash audit completed.
- Only H3-G02 and H3-G03 required core semantic repair; both are v1.0.1.
- Launch Bootstrap v2 pre-dispatch hardening completed.
- Initial renderer-test path defect was repaired via PR #34.
- Launch Bootstrap v2.0.3 successor dependency materialization / exact VERIFY candidate hardening was completed via PR #35.
- Batch-001 was dispatched and its receipts reconciled.
- Batch-002 was generated and promoted via PR #36.

Do not regenerate the 33 Frozen Cores.  
Do not reopen H1-A..H1-G planning.  
Do not redo PR #34/#35 hardening unless fresh repository evidence reveals a new actual regression.

---

## 6. Important recent GitHub milestones

### PR #34 — renderer test-path repair

Canonical state after merge:

`ec1f45b4a87daaad98ec09c17cfcc114550d9730`

Result:

- renderer test root resolution fixed;
- focused pre-dispatch suite: 63 passed;
- no product code changed;
- Batch-001 became ready for owner dispatch.

### PR #35 — Launch Bootstrap v2.0.3

Merge commit:

`d52009c312f1f57a7701d22758cc6e6c8f4aeb3a`

Verified before merge:

- focused launch-tooling suite: 67 passed;
- dependency-materialization RED/GREEN behavior confirmed;
- exact detached VERIFY candidate behavior confirmed;
- historical Batch-001 prompt bytes preserved;
- no product paths changed;
- independent code review: no unresolved Critical/Important findings.

Current Bootstrap alias:

- version: `launch-bootstrap-v2.0.3`
- SHA256: `3111485898b77ec497f329df21391ea951ae0ecbeaecfdb058a152f17dfcf98f`
- ref: `.orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.0.3.md`

Historical Batch-001 remains immutably bound to v2.0.2:

- version: `launch-bootstrap-v2.0.2`
- SHA256: `7bf3a3947f79ac8726d4357245c7fc107bb1700445395f35c2c4e445b674c512`
- metadata ref: `.orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.0.2.json`

### PR #36 — Batch-001 reconciliation / Batch-002 frontier

Current canonical main at this handoff:

`71c471a7aa61914038caf096e5155225527c44ef`

PR #36 added/updated only controller/Atlas/launch/reconciliation artifacts for the next frontier.

The earlier working branch `state/remaining-work-batch001-reconciliation-20261003` is now superseded by PR #36. At handoff review it had **0 commits ahead of main** and was behind current main. Do not resume or merge that branch as pending work.

---

## 7. Launch Bootstrap v2.0.3 semantics that must be preserved

The v2.0.3 hardening closed two execution gaps.

### 7.1 Exact dependency materialization for successor WRITE lanes

For every non-INDEPENDENT dependency in `dependency_heads`:

1. packet preflight verifies that the exact dependency head matches the current Atlas candidate generation;
2. the exact commit object must exist locally;
3. successor worktree starts from the Overlay `base_sha`;
4. if the dependency SHA is not already an ancestor of successor HEAD, materialize the **exact SHA** with:

`git merge --no-ff --no-edit <DEPENDENCY_SHA>`

5. do not substitute branch tips;
6. do not squash, rebase, cherry-pick, or rewrite history;
7. merge conflict fails closed; do not opportunistically resolve it;
8. no product edits may occur before dependency materialization + workspace preflight;
9. workspace preflight proves every exact dependency SHA is an ancestor of successor HEAD.

A missing materialization is `STALE_IN_FLIGHT`.

### 7.2 Exact candidate VERIFY worktrees

READ_ONLY VERIFY may use an isolated detached worktree, but:

`HEAD == candidate_generation.sha`

must hold exactly.

A VERIFY worktree at another HEAD is `STALE_IN_FLIGHT`.

---

## 8. Batch-001 — dispatched and reconciled

Source launch pack:

`.orchestration/remaining-work/launch-packs/batch-001/manifest.json`

Durable reconciliation:

`.orchestration/remaining-work/reconciliation/batch-001-reconciliation-20261003.json`

### H3-A01

Final Atlas state: **VERIFIED**

- execution branch: `execution/h3-a01-batch-001-20261003`
- branch head: `82cc663f6241fa87cd4a7fe8acc048ae34bb777f`
- candidate: `1eaed512521144b5a119a0002552f53f71c20eff`
- focused verification: 252 passed
- feature review: PASS
- contract deltas: none

Unlocks H3-A02.

### H3-B01

Final Atlas state: **VERIFIED**

- execution branch: `execution/h3-b01-batch-001-20261003`
- branch head: `b113025615c33ccc4466075f2537524d8e7c09df`
- candidate: `4bbb267c654dbe3c251041da4b297d7ef1f48556`
- focused suites: 41 + 26 + 34 passed
- non-model regression suite: 152 passed
- final feature review: ACCEPT, zero actionable findings
- contract deltas: none
- model-adapter tests requiring torch were not used as an acceptance blocker

Unlocks H3-B02 and H3-B03.

### H3-C01

Current Atlas state: **VERIFY_READY**

- execution branch: `execution/h3-c01-batch-001-20261003`
- branch head: `4e9a36883f253e8bc3c61dbaeba86bfbf61e4609`
- candidate: `c52b1b8089b2f903cab08ceb673913bab736d5d0`
- source-adapter/real-source focused suite: 22 passed
- Gate-0 identity/inventory regressions: 22 passed
- compileall/diff-check: PASS
- contract deltas: none

Reason it is not yet VERIFIED:

The earlier feature review found a valid issue; the issue was repaired, producing a new exact candidate. That repaired candidate requires one independent exact-candidate VERIFY/re-review.

### H3-D01

Final Atlas state: **VERIFIED**

- execution branch: `execution/h3-d01-batch-001-20261003`
- branch head: `9a79d0a3bb5a1e913d4345d5a0b71850d2c69c13`
- candidate: `8e5690ab2b28251d4db3e4782c7fcf4173ba4ab6`
- focused suite: 43 passed
- feature review: ACCEPT
- contract deltas: none

Unlocks H3-D03 and H3-D04.

### H3-E01

Current Atlas state: **DIRTY_BY_CONTRACT_DELTA**

Observed local execution evidence:

- local candidate: `9d5d6209cbee04937174df6ba242506fea1bfbc8`
- local final head: `4c608052e1352f9a9e60a36921c3c630a466993e`
- required H3-E01 suite: 95 passed
- Gate-3 synthetic test: 1 passed
- mutation/hash regressions: 2 passed
- full run at the time: 832 passed, 10 skipped, 18 failed
- remote candidate object was **NOT OBSERVED**

Contract delta:

`H3-E01-CD-001`

Meaning:

Gate-3 refine adds `request_identity` to C2 named-byte binding evidence; downstream reconciliation is required.

Propagated dirty nodes:

- H3-E01
- H3-E02
- H3-E03

Do not launch E02/E03 until the contract delta is explicitly reconciled.

### H3-F01

Current Atlas state: **PARKED**

Observed local execution evidence:

- local candidate: `cf8567cbbba321e79059b5e029e58c326dee9d01`
- local final head: `f578a1e7e1581250dbb1f029b0c684638ee9e044`
- focused suite: 34 passed
- compileall: PASS
- duplicate-key schema JSON parse: PASS
- diff-check: PASS
- tracked-secret scan: PASS
- remote candidate object was **NOT OBSERVED**

Problem:

`H3-F01-REMOTE-DURABILITY-001`

The prior push was withheld because the legacy workspace verifier classified task-authorized `src/gate2/measure.py` as unauthorized. This was identified as verifier-authority drift relative to the Frozen Core write-domain, not as evidence that the H3-F01 product change itself was outside its Frozen Core authority.

Do not launch H3-F02 until F01 recovery/reconciliation is complete.

---

## 9. Current Atlas/controller state

At canonical main `71c471a7aa61914038caf096e5155225527c44ef`:

Controller:

- stage: `EXECUTION_ACTIVE`
- next chunk: `EXECUTION_BATCH_002`
- current launch pack: `.orchestration/remaining-work/launch-packs/batch-002/manifest.json`
- historical prompts dispatched: `true`
- current Batch-002 dispatched: `false`
- last dispatched pack: Batch-001
- current Bootstrap: v2.0.3
- open reconciliation Problems: E01 and F01
- current launch base: `d52009c312f1f57a7701d22758cc6e6c8f4aeb3a`

Progress snapshot:

- baseline total weight: 100
- build-green weight: 14
- verified weight: 10
- ready weight: 16
- planned/blocked weight: 74
- build progress: 14%
- verification progress: 10%

Current significant H3 states:

- H3-A01: VERIFIED
- H3-A02: READY
- H3-B01: VERIFIED
- H3-B02: READY
- H3-B03: READY
- H3-C01: VERIFY_READY
- H3-D01: VERIFIED
- H3-D03: READY
- H3-D04: READY
- H3-E01: DIRTY_BY_CONTRACT_DELTA
- H3-E02: DIRTY_BY_CONTRACT_DELTA
- H3-E03: DIRTY_BY_CONTRACT_DELTA
- H3-F01: PARKED

---

## 10. Batch-002 — prepared but NOT dispatched

Manifest:

`.orchestration/remaining-work/launch-packs/batch-002/manifest.json`

Batch-002 contains six copy-ready prompts:

1. `.orchestration/remaining-work/launch-packs/batch-002/prompts/01-H3-C01.md` — VERIFY / READ_ONLY
2. `.orchestration/remaining-work/launch-packs/batch-002/prompts/02-H3-A02.md` — BUILD
3. `.orchestration/remaining-work/launch-packs/batch-002/prompts/03-H3-B02.md` — BUILD
4. `.orchestration/remaining-work/launch-packs/batch-002/prompts/04-H3-B03.md` — BUILD
5. `.orchestration/remaining-work/launch-packs/batch-002/prompts/05-H3-D03.md` — BUILD
6. `.orchestration/remaining-work/launch-packs/batch-002/prompts/06-H3-D04.md` — BUILD

All use Launch Bootstrap v2.0.3.

Batch generated-at/base SHA:

`d52009c312f1f57a7701d22758cc6e6c8f4aeb3a`

This is intentionally older than current main `71c471a7…` because PR #36 only added controller/launch/reconciliation artifacts. Do not regenerate overlays merely because `base_sha != current main`. Run current preflight. Regenerate only if current repository evidence produces a real task-relevant stale/contract delta.

### Exact Batch-002 dependency heads

H3-C01 VERIFY:

- no dependency heads
- exact candidate under verification: `c52b1b8089b2f903cab08ceb673913bab736d5d0`
- overlay branch label: `execution/h3-c01-verify-batch-002-20261003`
- VERIFY may use a detached worktree at the exact candidate SHA

H3-A02 BUILD:

- H3-A01 → `1eaed512521144b5a119a0002552f53f71c20eff`

H3-B02 BUILD:

- H3-B01 → `4bbb267c654dbe3c251041da4b297d7ef1f48556`

H3-B03 BUILD:

- H3-B01 → `4bbb267c654dbe3c251041da4b297d7ef1f48556`

H3-D03 BUILD:

- H3-D01 → `8e5690ab2b28251d4db3e4782c7fcf4173ba4ab6`

H3-D04 BUILD:

- H3-D01 → `8e5690ab2b28251d4db3e4782c7fcf4173ba4ab6`

The BUILD tasks must materialize these exact SHAs under Bootstrap v2.0.3 before coding.

---

## 11. Two independent recovery prompts are also ready

These recovery tasks are not part of Batch-002 product BUILD and can run independently in parallel.

### E01 remote durability recovery

Prompt:

`.orchestration/remaining-work/reconciliation/prompts/01-H3-E01-durability-recovery.md`

Purpose:

- find the exact prior local E01 objects/branch;
- verify candidate/head identity;
- publish the existing branch non-force if safe;
- establish remote durability only;
- do **not** fix or clear `H3-E01-CD-001`;
- do not change product code;
- do not launch E02/E03.

Expected status:

`REMOTE_DURABILITY_ESTABLISHED` or `BLOCKED`

### F01 remote durability / verifier-classification recovery

Prompt:

`.orchestration/remaining-work/reconciliation/prompts/02-H3-F01-durability-recovery.md`

Purpose:

- find exact prior F01 objects/branch;
- verify candidate/head;
- confirm all changes fall within Frozen Core write-domain;
- distinguish legacy workspace-verifier authority drift from Frozen Core authority;
- publish the existing branch non-force if safe;
- establish remote durability only;
- do not modify verifier policy, product code, Atlas, Frozen Core, or main;
- do not launch F02.

Expected status:

`REMOTE_DURABILITY_ESTABLISHED` or `BLOCKED`

---

## 12. Exact next action for the new ChatGPT/controller

After fresh GitHub verification, the next ChatGPT should continue execution, not planning.

### Step A — verify current source of truth

Confirm:

- current `main`;
- controller stage;
- Batch-002 manifest;
- `current_launch_pack_dispatched=false`;
- Bootstrap v2.0.3 hash;
- Batch-002 prompt files;
- E01/F01 recovery prompt files.

If current main is newer than this handoff, inspect the delta before using any stale SHA.

### Step B — give the owner the next Codex prompts

The owner wants prompts in **plain code blocks**, not Writing Blocks.

Each Codex launcher must be in its **own separate code block**.

Recommended immediate parallel frontier:

- Batch-002: 6 fresh top-level Codex sessions
- Recovery: 2 additional fresh top-level Codex sessions

Total useful independent sessions: **8**, subject to current environment/tool availability and resource policy.

For the six Batch-002 tasks, prefer short launcher prompts that tell Codex to fetch current canonical origin/main and execute the **complete exact contents** of the corresponding copy-ready prompt file. Do not manually rewrite the full Frozen Core/Overlay unless necessary.

For E01/F01 recovery, likewise point Codex to the exact recovery prompt file.

Do not claim a session was dispatched until the owner actually starts it or a real top-level Codex session-spawn tool returns success.

### Step C — collect receipts continuously

As receipts arrive:

1. independently verify remote branch/object evidence;
2. update/reconcile Atlas state;
3. unlock newly dependency-safe tasks immediately;
4. do not wait for all eight sessions if independent later work becomes READY;
5. preserve rolling-frontier scheduling;
6. do not infer VERIFIED from BUILD_GREEN;
7. do not infer remote durability from local SHAs;
8. contract delta → fail closed for affected descendants.

### Step D — produce the next Launch Pack only from reconciled current state

Use current Bootstrap and exact dependency heads.

Do not manually invent successor bases or branch tips.

---

## 13. Known baseline/environment noise — do not misclassify automatically

Known observations from recent verification:

- `python3` may not have pytest installed;
- using `uv run --with pytest ...` for an isolated test dependency is acceptable and was already used successfully;
- do not mutate the shared repository `.venv` merely for convenience unless current policy requires it;
- broad suite can encounter missing `torch` for model-adapter tests;
- recent PR #35 full-suite practical rerun: 852 passed, 10 skipped, 6 baseline failures;
- five of those failures required unavailable torch;
- one workspace-source-authorization history expectation failure reproduced on the canonical base;
- prior workspace verifier also reported reference-pack source/map integrity and prototype `.env.local` baseline issues in some environments.

These are not blanket exemptions. Use `systematic-debugging` if a current task hits them and determine whether the failure is task-related before classifying it.

---

## 14. Local repository safety / last known local condition

Last explicitly reported local state before the later controller-only PR #36 merge:

- primary local repo: `/Users/yusuf/Repos/video-intelligence-pipeline`
- original checkout remained on a prior planning branch with 117 pre-existing untracked paths;
- that dirty checkout was intentionally preserved;
- clean verification worktrees were used for synchronization/testing.

A fresh session must fetch current `origin/main` and must not assume the local main/checkouts are already at `71c471a7…`.

Never use:

- hard reset
- git clean
- force push
- destructive worktree deletion
- reflog expiration/pruning

unless separately and explicitly authorized.

---

## 15. Scope/authorization boundaries remain unchanged

Do not infer authorization for:

- real/protected archive execution;
- provider/cloud calls;
- model downloads;
- network egress beyond ordinary authorized repository operations;
- production promotion;
- destructive cleanup;
- Gate promotion;
- real-media editing/export.

Batch-002 is local-first Remaining Work execution only.

---

## 16. User interaction preferences for this continuation

The owner wants forward progress and does not want another planning loop.

When providing multiple Codex prompts:

- use **code blocks**, not Writing Blocks;
- give each prompt in a **separate** code block;
- use fresh top-level Codex tasks for independent roots;
- parallelize genuinely independent tasks;
- do not fabricate extra tasks to fill capacity.

The owner will paste Codex receipts back into ChatGPT. Reconcile them against GitHub independently before updating conclusions.

---

## 17. Things the new ChatGPT must NOT do

Do not:

- restart Remaining Work planning;
- regenerate H1-A..H1-G;
- rewrite the 33 Frozen Cores for style;
- rerun Batch-001;
- rerender historical Batch-001 under v2.0.3;
- silently clear E01 contract delta;
- launch E02/E03 while `H3-E01-CD-001` remains unresolved;
- launch F02 while F01 is still PARKED;
- treat local E01/F01 candidate SHAs as remote durable until origin proves it;
- merge product candidates to canonical main without explicit integration authority;
- use chat memory instead of GitHub evidence.

---

## 18. Minimal fresh-session status summary

**VERIFIED repository state at handoff creation:**

- canonical main: `71c471a7aa61914038caf096e5155225527c44ef`
- controller: `EXECUTION_ACTIVE`
- next chunk: `EXECUTION_BATCH_002`
- current pack: Batch-002
- Batch-002 dispatched: **NO**
- current Bootstrap: v2.0.3
- Batch-001: dispatched + reconciled
- A01/B01/D01: VERIFIED
- C01: VERIFY_READY
- A02/B02/B03/D03/D04: READY
- E01/E02/E03: DIRTY_BY_CONTRACT_DELTA
- F01: PARKED
- next useful execution: 6 Batch-002 tasks + 2 bounded recovery tasks

If GitHub has advanced, verify and supersede this snapshot with newer evidence.

---

## 19. Handoff quality audit

This handoff was reviewed against six continuation risks:

1. **Authority/identity:** canonical main, candidate SHAs, branch heads, Bootstrap versions/hashes, and current controller refs are explicit.
2. **Semantic continuity:** project invariants, Gate boundaries, and evidence discipline are preserved.
3. **Execution continuity:** Batch-001 outcomes and Batch-002 exact tasks/dependency heads are recorded.
4. **Failure/recovery continuity:** E01 contract delta and F01 remote-durability/verifier drift remain fail-closed and separately actionable.
5. **Safety/scope continuity:** protected/archive/provider/production authority is not widened.
6. **Fresh-session usability:** exact read order, DO-NOT-REDO list, next actions, prompt-format preference, and receipt reconciliation rules are explicit.

No new architecture is created by this handoff.
