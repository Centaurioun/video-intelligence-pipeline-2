# Video Intelligence Pipeline — Fresh-Session Execution Handoff

**Date:** 2026-10-03  
**Purpose:** authoritative fresh-session continuity handoff for the next ChatGPT/controller  
**Canonical repository:** `Centaurioun/video-intelligence-pipeline`  
**Verified canonical `main` at handoff creation:** `9151b712e8fb3d81c6089848e61a727aa83141ee`  
**Current durable prompt-library head:** `execution/remaining-work-prompts-h1-e-20261003@bd8ab438e792801cebb58706dce76a974b984ca5`  
**Immediate next chunk:** `D6 — H1-F / H3-F01..H3-F03 Frozen Core prompt generation`

---

## 1. Read this first

This file exists because the prior ChatGPT conversation reached its context limit. The next controller must continue from **repository state**, not reconstruct the project from chat memory.

If anything in prior conversation summaries, uploaded orientation files, or remembered discussion conflicts with current verified Git state:

> **current verified repository evidence wins.**

Do **not** repeat completed brainstorming, re-derive the project backlog, regenerate frozen prompts, or restart review-heavy planning loops merely because the new chat has no conversational memory.

The owner’s standing intent is to **finish the project quickly through execution-first, dependency-safe parallelism**, while preserving evidence/authority/temporal correctness.

The owner’s standing interaction preference during this preparation sequence is simple: when the owner says **“devam et”**, execute the next durable chunk and stop at that chunk’s checkpoint. Do not ask the owner to re-approve decisions already frozen in the governing spec/plan; ask only when a genuinely new authority/design decision is unavoidable.

When the owner says only **“devam et”**, resume the earliest incomplete durable chunk from this handoff/repository state. Do not reinterpret that as permission to redesign completed chunks.

---

## 2. Mandatory fresh-session bootstrap

Before making mutable/current project-state claims:

1. use the Project-uploaded `00_PROJECT_CHARTER.md` only as stable orientation;
2. independently inspect current GitHub repository state;
3. read canonical `main`:
   - `AGENTS.md`
   - `docs/INDEX.md`
   - `docs/project/00_PROJECT_CHARTER.md`
   - `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`
   - `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`
   - `docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`
   - **this file**
   - `docs/project/STATE_MAINTENANCE_PROTOCOL.md`
4. read current execution authority:
   - `docs/superpowers/specs/2026-10-03-remaining-work-execution-atlas-and-parallel-verification-design.md`
   - `docs/superpowers/plans/2026-10-03-remaining-work-execution-atlas-implementation-plan.md`
   - `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`
5. then inspect the latest durable Remaining Work branch/head named below.

Do not trust a Codex/subagent success message by itself. Preferred evidence order remains:

`owner report -> independent repository/Git verification -> conclusion`.

## 2A. Current durable machine-state surface

For the current cumulative prompt-library state, read these files from:

`execution/remaining-work-prompts-h1-e-20261003@bd8ab438e792801cebb58706dce76a974b984ca5`

- `.orchestration/remaining-work/atlas/atlas.json`
- `.orchestration/remaining-work/atlas/contract-registry.json`
- `.orchestration/remaining-work/atlas/authority-backlog.json`
- `.orchestration/remaining-work/atlas/derivation-evidence.json`
- `.orchestration/remaining-work/atlas/progress.json`
- `.orchestration/remaining-work/controller-state.json`
- `.orchestration/remaining-work/prompts/index.json`
- `.orchestration/remaining-work/bootstrap/chunk-d5-closeout-20261003.json`

The prompt-library branches are cumulative: D5 contains the previously frozen D1–D4 cores plus H1-E. D6 must branch from the exact current cumulative D5 head unless a fresh delta reconciliation proves a different base is required.

Canonical `main` intentionally carries compact state checkpoints while the full Atlas/prompt-library surfaces remain on their execution branches until the later controlled promotion phase.

---

## 3. What the owner is trying to achieve

The owner is frustrated by repeated cycles of:

`analysis -> review -> tests -> more analysis -> re-planning -> another review loop`

that consume hours without advancing the product.

The agreed replacement is a **torrent/factory execution model**:

- freeze the known remaining work as a durable H0/H1/H2/H3 Atlas;
- prebuild/version/hash H3 prompt cores;
- use fresh top-level Codex roots by default;
- each root acts mainly as scheduler/integrator;
- split each H3 into dependency-safe H4 lanes;
- dispatch independent H4 lanes **concurrently**, not sequentially one child at a time;
- recycle child capacity as tasks terminate;
- use exclusive writer ownership rather than serializing the whole project;
- keep BUILD, VERIFY, and REPAIR as concurrent frontiers;
- once an H3 becomes BUILD_GREEN, its feature review can run asynchronously while unrelated BUILD continues;
- a failed test/review repairs only the affected subgraph where possible;
- later chapters may begin once their actual HARD dependencies are satisfied; chapter numbering itself is not a barrier;
- detailed worker findings live in the repository; chat receives compact receipts;
- future ChatGPT sessions perform narrow **Launch Delta Reconciliation**, not fresh project redesign.

The goal is **wall-clock throughput**, not “maximum agent count” for its own sake. Never manufacture duplicate work to fill slots.

---

## 4. Current process authority

The owner already approved the Remaining Work Execution Atlas design and implementation plan. Do not restart architectural brainstorming for this operating system unless a genuinely new architectural contradiction appears.

Current behavior from `resource-policy-v5.yaml`:

- execution mode: `EXECUTION_PORTFOLIO_PARALLEL`;
- frontiers: BUILD / VERIFY / REPAIR;
- numeric chapter order is **not** a hard barrier;
- independent READY work should not idle;
- fixed root quota: **none**;
- same-branch writer roots: **1**;
- branch isolation required;
- roots do not merge canonical main;
- reasoning subagents: adaptive READY work;
- preferred hierarchy: Root -> Area Lead -> Worker;
- flatten when nested delegation is unavailable;
- completed child slots are recycled immediately;
- stock Superpowers `subagent-driven-development` is **not** the default H3/H4 executor;
- independent domains -> `dispatching-parallel-agents`;
- behavior changes -> `test-driven-development`;
- unexpected failures -> `systematic-debugging`;
- completion claims -> `verification-before-completion`;
- H3 feature review -> asynchronous `requesting-code-review`;
- review feedback -> `receiving-code-review`;
- per-inner-task review is not the default.

Current Codex policy:

- requested family: `LUNA`;
- reasoning: `medium`;
- resolve/freeze concrete supported identity per Goal;
- no silent family fallback;
- no silent mid-goal model change.

---

## 5. Resource-policy v5

The old “all heavy work max concurrent = 1” policy is obsolete.

Current starting leases:

- `LIGHTWEIGHT_CPU_TEST`: adaptive READY work, no fixed quota;
- `HEAVY_CPU`: initial max 2; calibration target 3; fallback 1;
- `FFMPEG_HEAVY`: initial max 2; calibration target 3; fallback 1;
- `MODEL_MPS`: initial max 2; fallback 1; only already-authorized local model runtime;
- `MIXED_HEAVY`: calibrate separately;
- `ENV_ADMIN`: serialized, max 1.

Failure is **fail-soft by resource class**. A heavy-resource problem does not globally serialize lightweight work.

Routine development prerequisite recovery is authorized within scope. Missing routine package/tool/config is not automatically an owner blocker. Root owns environment continuity. Public-registry retrieval is allowed for routine development prerequisites only; this does **not** authorize provider/model activity, protected-media retrieval, private credentials, or model checkpoint downloads.

---

## 6. Hard scientific / evidence invariants

Long-term pipeline:

`source/archive -> deterministic inventory/provenance -> semantic useful-moment retrieval -> source-native temporal refinement -> measured PTS/frame evidence -> human editorial decision -> versioned edit plan -> render/export -> technical/editorial QC`

Hard rules:

- source media is immutable unless a separately approved policy says otherwise;
- semantic/model/provider timestamps are candidate evidence only;
- exact temporal work uses source-native PTS/timebase evidence;
- never infer VFR frame position as seconds × nominal FPS;
- semantic retrieval does not become exact edit authority by convenience.

Evidence classes:

- `MEASURED`
- `MATCHED`
- `VISUALLY_OBSERVED`
- `AUDIO_OBSERVED`
- `EDITORIAL_INFERENCE`

`NOT_OBSERVED` is an availability/state marker, not an evidence class.

Never silently upgrade evidence strength.

Gate structure remains:

- Gate 0 — diagnostic retrieval;
- Gate 1 — representation/capability benchmark;
- Gate 2 — reliability/scale;
- Gate 3 — editing/QC.

Evidence-dependent Gate promotions remain hard gates. This Remaining Work effort does **not** itself grant promotion authority.

---

## 7. Authority boundaries that remain hard

Do not infer authority for:

- protected/archive-media execution;
- broad archive traversal;
- provider/cloud inference or provider transport;
- model/checkpoint download or model-family change;
- production render/export/publication/distribution;
- real Gate-1 benchmark winner selection;
- real Gate-2 workload/scale outcome used for promotion;
- Gate promotion/maturity promotion;
- protected/real-media production QC.

No hard reset, `git clean`, force push, reflog destruction, branch/worktree destruction, or destructive recovery-object pruning without explicit current authorization and safe recovery evidence.

The current Remaining Work H0 denominator explicitly excludes separately authorized protected/provider/production/Gate-promotion work.

---

## 8. Remaining Work Atlas — frozen structure

Active finish line:

`VERIFICATION_COMPLETE_FOR_CURRENT_AUTHORIZED_LOCAL_FIRST_SCOPE`

H0 remaining-work baseline is 100 units.

Frozen H1 chapters:

| H1 | Chapter | Weight |
|---|---|---:|
| H1-A | Gate-0 Revision-18 successor closure | 24 |
| H1-B | Semantic core productization / index lifecycle | 18 |
| H1-C | Multi-source archive / retrieval operational path | 18 |
| H1-D | Retrieval capability completion / benchmark-ready framework | 12 |
| H1-E | Editorial / edit pipeline completion | 16 |
| H1-F | Reliability / scale / restart apparatus | 7 |
| H1-G | Convergence, integration, and final verification | 5 |

Total: **100**.

Frozen H3 count: **33**.

Important interpretation:

- H0=100 measures **future product execution + verification work** at Atlas freeze.
- Prompt-library preparation is orchestration work around H0, not product H3 completion.
- As of this handoff, H1-A..H1-E Frozen Cores cover **88/100 Atlas weight** and **27/33 H3 prompt cores**, but **no product H3 execution prompt has been dispatched**.
- Therefore do **not** say “the project execution is 88% complete.” Prompt coverage and build/verify completion are different metrics.

---

## 9. Durable chunk history — do not redo

### Chunk A — policy authority

Completed and current on canonical `main`.

Key result: execution-first concurrent policy + resource-policy v5 became current process authority.

### Chunk B — Atlas machinery

Durable branch/head:

`execution/remaining-work-atlas-machinery-20261003@fd416e9ec03a2d4a5e7899dbd3d0422bec494602`

### Chunk C — frozen “book contents”

Durable branch/head:

`execution/remaining-work-atlas-toc-20261003@35585a13f1f51ac106ec67902ef6df067423c73f`

Frozen Atlas:

- 7 H1 chapters;
- 33 H3 packets;
- H0=100;
- initial READY frontier was 6 independent H3;
- initial READY weight 21/100;
- predicted independent writer overlap pairs 0.

### D1 — H1-A prompt cores

`execution/remaining-work-prompts-h1-a-20261003@fa7aeb40487ca7b767e94fbb76f094eb0b43779e`

Frozen:

`H3-A01..H3-A07`

### D2 — H1-B prompt cores

`execution/remaining-work-prompts-h1-b-20261003@97082e54de6bd1197e03dc1ab5b8ef0068ba7e42`

Frozen:

`H3-B01..H3-B05`

Combined library then: 12 cores.

### D3 — H1-C prompt cores

`execution/remaining-work-prompts-h1-c-20261003@14c4d3ba737e2b8658a13c49836a17f49b2f0e11`

Frozen:

`H3-C01..H3-C05`

Combined library then: 17 cores.

### D4 — H1-D prompt cores

`execution/remaining-work-prompts-h1-d-20261003@daf56385d0d9777f5d90abeb479a1e3c2112c9db`

Frozen:

`H3-D01..H3-D05`

Combined library then: 22 cores.

### D5 — H1-E prompt cores — CURRENT LATEST DURABLE PROMPT STATE

`execution/remaining-work-prompts-h1-e-20261003@bd8ab438e792801cebb58706dce76a974b984ca5`

Closeout:

`.orchestration/remaining-work/bootstrap/chunk-d5-closeout-20261003.json`

Frozen:

`H3-E01..H3-E05`

Combined library now: **27 cores across H1-A..H1-E**.

D5 verified chapter rulings:

- baseline: generalize verified real-source FVS chain; do not replace it;
- temporal authority: source-native measured PTS only;
- semantic candidates: MATCHED and non-binding until refinement;
- editorial evidence: EDITORIAL_INFERENCE;
- human decision resume: sealed append-only supersession lineage;
- plan lineage: digest-bound immediate prior revision;
- render scope: NON_PRODUCTION_PREVIEW;
- automated real-tool inputs: generated/synthetic/non-protected only;
- technical QC: measured technical only;
- visual/audio/editorial suitability: NOT_OBSERVED unless separately evidenced;
- production eligible: false;
- export eligible: false;
- Gate promotion: false;
- H3-E04 resource class: FFMPEG_HEAVY under v5.

D5 static prompt/hash/Atlas audit: PASS.  
D5 exact branch runtime verifier: NOT_OBSERVED because no GitHub Actions run exists for the exact branch head and the connector surface cannot run the local suite.

**Do not regenerate D1–D5 prompt cores.**

---

## 10. Important preserved Gate-0 lineage

The prompt library already captures this, but the next controller should know why H1-A must not be redesigned.

Accepted Task-3 architecture:

`DESCRIPTOR_ANCHORED_CAPTURE + VERIFIER_OWNED_WRITE_FREE_LIFECYCLE`

Frozen accepted Task-3 candidate:

`a7075eb1bf8b7e7344f937e72d96cf573b3174a9`

Frozen tree:

`a27c26bb9ca3eab2f711418a5364fb93dfe75c01`

Final Task-3 evidence head:

`06b86219f8f5a73d158f83d8a4453425ac58a35c`

Task-4 post-Task3 successor amendment blob:

`bb2a6ccb28ce6a09f3e6aa2481f20faa54d63d96`

Projection-dataflow successor authority:

- spec blob: `d3d7a4611e375317e651049bceb345fe0d879744`
- plan blob: `5770a349b2b052e201d9c49b78092cb41bb38d39`

Historical network caveat remains durable:

- external GitHub metadata access: `NOT_OBSERVED`;
- caveat does not block Task-3 freeze;
- caveat must be preserved.

Do not substitute historical old V7 Task 4–12 numbering for the projection-dataflow successor Tasks 4–12.

---

## 11. Important chapter rulings already frozen

### H1-B — semantic core

- persistent local index engine is stabilized **in place**;
- no wholesale package relocation;
- H3-B04 owns the stable product-facing semantic-index seam;
- no daemon/service/ANN/vector-DB introduced by default;
- last-location lifecycle is explicit and local;
- exact search/materialization semantics remain deterministic.

### H1-C — multi-source

- locator != revision identity != content digest != custody context;
- same bytes at distinct locators remain distinct occurrence contexts;
- additions/changes occur before removals;
- same-digest move keeps old location until replacement succeeds/reuses;
- restart/recovery uses deterministic local file-backed idempotent journal;
- no background archive watcher/daemon/queue;
- retrieval candidates remain MATCHED and `binding_eligible=false`;
- PTS/timebase may be provenance-rich locators but are not edit boundaries.

### H1-D — retrieval capability / benchmark-ready framework

- retained old Gate-1 controller is **not** merged as-is;
- useful proven mechanisms are reimplemented against current contracts;
- certified synthetic candidate is mechanism reference only;
- stale real-execution eligibility is not imported;
- current real Gate-1 benchmark authority is NOT_AUTHORIZED;
- query modality seams: TEXT, IMAGE_REFERENCE, VIDEO_REFERENCE;
- current executable modality: TEXT only;
- image/video-reference seam does not imply executable capability;
- generated fixture harness may prove protocol readiness only;
- no real winner/model/provider selection/Gate promotion.

### H1-E — editorial/edit

See D5 summary above. Preserve the already verified one-source real FVS chain as the regression baseline; generalize it rather than replacing it.

---

## 12. Immediate next task — D6 / H1-F

Repository verified on 2026-10-03:

- no `remaining-work-prompts-h1-f` branch existed at the time of this handoff check;
- current controller state on D5 branch:
  `PROMPT_LIBRARY_PARTIAL_H1_A_H1_B_H1_C_H1_D_H1_E_FROZEN`;
- `next_chunk = D6`.

D6 scope is **only H1-F**:

### H3-F01 — weight 3 — READY

**Title:** Port Gate-2 measurement, preregistration, and evidence-to-mechanism contracts onto the current pipeline.

Current consumed contracts:

- Gate-2 synthetic candidate: `88bff2e1be00bf3717a48c00a3529cabce3d16b5`
- Gate-2 reconciliation blob: `063ae16e9ae6122bd5a460e80a4b167aa0d60a4e`
- canonical contracts: `c0b665d70b311dd98b7ff9f4f564b2d5750ed17b`

Current planned write domain:

- `src/gate2/measure.py`
- `src/gate2/preregistration.py`
- `schemas/gate2/measurement.json`
- `tests/gate2/`

Resource class: `LIGHTWEIGHT_CPU_TEST`.

### H3-F02 — weight 2 — PLANNED

**Title:** Build bounded synthetic/generated workload, fault, restart, and recovery apparatus against current index/FVS surfaces.

Hard BUILD dependencies:

- H3-F01
- H3-C04
- H3-E05

Consumed evidence includes:

- Gate-2 synthetic candidate `88bff2e...`
- persistent-index Attempt-4 reconciliation `279c585...`
- real-source FVS reconciliation `18f4817...`

Planned write domain:

- `src/gate2/workload.py`
- `src/gate2/faults.py`
- `src/gate2/recovery.py`
- `tests/gate2/`

Resource class: `LIGHTWEIGHT_CPU_TEST`.

### H3-F03 — weight 2 — PLANNED

**Title:** Produce bounded scale/restart/performance evidence and mechanism decision without preselecting ANN/queue/cache services.

Hard BUILD dependency:

- H3-F02

Consumed evidence includes:

- Gate-2 synthetic candidate `88bff2e...`
- persistent-index Attempt-4 reconciliation `279c585...`
- resource-policy v5 blob `4e6f887a5b1e6b9855736adfe63fc6ac93ea5da9`

Planned write domain:

- `src/gate2/decision.py`
- `src/gate2/verify.py`
- `src/gate2/cli.py`
- `tests/gate2/`

Resource class: `HEAVY_CPU`.

### What the next ChatGPT should do for D6

Follow the exact D1–D5 pattern:

1. verify current `main` and D5 branch/head again;
2. read the H1-F Atlas nodes from the D5 prompt branch;
3. inspect the certified Gate-2 synthetic candidate and current Gate-2 reconciliation;
4. inspect current pipeline/index/FVS interfaces H3-F will consume;
5. identify any missing consumed-contract fingerprints / overly broad write domains;
6. create a new D6 branch **from the D5 prompt-library head**, not from a stale earlier chapter;
7. add task-specific durable run-state directories;
8. generate exactly three H1-F Frozen Cores (`H3-F01..F03`);
9. preserve mandatory parallelism / async review / compact receipt contracts;
10. update prompt index and controller state to H1-A..F frozen;
11. update the self-consistency test to expect 30 frozen cores;
12. refetch each D6 core from GitHub and recompute SHA-256;
13. verify `core.md <-> core.json <-> Atlas` dependency/write-domain/contract/executor/resource equality;
14. verify launch-only fields did not leak into Frozen Core;
15. verify earlier H1-A..E core hashes/files did not drift;
16. record D6 closeout;
17. write only a state-only checkpoint to canonical `main`;
18. stop. Do not begin D7 unless the owner says “devam et”.

If a preserved Gate-2 mechanism conflicts with current pipeline contracts, reimplement the proven scientific/mechanical invariant rather than blindly merging stale controller state.

Do not preselect ANN/vector DB, cache service, durable queue, daemon, or distributed architecture. Gate-2 exists to measure whether such mechanisms are justified.

---

## 13. After D6 — remaining preparation sequence

### D7 — H1-G Frozen Cores

Three remaining prompt cores:

- H3-G01 — overlap/contract-delta convergence matrix;
- H3-G02 — reconciled integration candidate + cross-system regression;
- H3-G03 — close verification/review debt + final current-scope readiness receipt.

H3-G01 waits on BUILD completion of A07/B05/C05/D05/E05/F03.

H3-G02 is `SERIAL_TIGHT_COUPLING`, `HEAVY_CPU`, and owns broad integration surfaces.

H3-G03 is `VERIFY_ONLY` and requires both H3-G02 BUILD completion and the chapter-terminal H3 verification dependencies.

After D7, all **33/33 H3 Frozen Cores** should exist.

### Chunk E — Phase 6 — Launch machinery

Create:

- `scripts/render-remaining-work-launch-pack.py`
- `tests/scripts/test_render_remaining_work_launch_pack.py`

Renderer must:

- consume Atlas + Frozen Cores + Launch Overlays;
- select maximum useful READY set subject to dependency/write/resource constraints;
- default new H3 to fresh Codex;
- render numbered copy-ready prompts;
- include no hidden dependency on prior chat memory.

Generate the **first real Launch Pack but do not dispatch it yet**.

### Chunk F — Phase 7 — resource calibration

Use only synthetic/non-protected fixtures.

Measure heavy CPU / FFmpeg concurrency:

- 1 job;
- 2 concurrent;
- if stable/useful, 3 concurrent.

Do not globally return to max=1 because one resource class fails.

No model download solely for calibration.

### Chunk G — Phase 8 — Launch Delta Reconciliation / readiness

Reconcile:

- current Atlas;
- prompt hashes;
- local/remote branch changes;
- open Problems;
- stale in-flight status;
- resource leases;
- candidate generation binding.

Then run final pre-dispatch checks and freeze:

`PROMPTS_READY_FOR_DISPATCH`

Expected state:

- `ATLAS_READY=YES`
- `TABLE_OF_CONTENTS_FROZEN=YES`
- `PROMPT_LIBRARY_READY=YES`
- `FIRST_LAUNCH_PACK_READY=YES`
- `RESOURCE_POLICY_V5_ACTIVE_OR_CALIBRATION_RECORDED=YES`
- `PROMPTS_DISPATCHED=NO`

### Chunk H — Phase 9 — controlled Atlas/tooling promotion

Promote the complete Atlas/tooling/prompt-library surfaces to canonical main only after exact Phase-8 verification.

Owner already authorized these process/Atlas/tooling main changes in the prior conversation, but promotion must remain:

- non-destructive;
- history-preserving;
- no force push;
- exact verified candidate only;
- followed by fresh-main readback and overlay/Launch Pack revalidation.

Only after this point should the owner begin copying the real execution prompts into fresh Codex sessions.

---

## 14. Actual Codex execution model — when dispatch finally begins

The owner does **not** want one huge Codex root that runs for hours while all other work waits.

Preferred model:

- launch as many genuinely independent top-level H3 roots as useful;
- 5–10 top-level Codex sessions are acceptable when the DAG has that many useful independent packets;
- do not force a particular count;
- each top-level root should itself dispatch multiple useful subagents concurrently;
- H4 tasks should be sized meaningfully — not two-minute microtasks, but also not giant serial mini-projects;
- a root may run 15–30+ minutes while using many child lanes;
- completed child slots should be recycled;
- no duplicate work just to occupy capacity.

Root/Main-Agent role:

- scheduler;
- dependency controller;
- integration owner for its branch;
- compact adjudicator.

Child workers:

- independent analysis/test/design/write shards where ownership is clean;
- detailed findings should be written to task-specific durable run-state directories if large;
- root receives compact summaries;
- child writers are allowed when they have exclusive file/path ownership.

Supervisor pattern is encouraged where useful:

`Root -> Area Lead/Supervisor -> Workers`

If nested delegation is not available, flatten to:

`Root -> Workers`.

---

## 15. Testing and review philosophy — do not regress to the old bottleneck

The owner is not asking to remove testing/review. The owner is asking to stop treating testing/review as a single global serial barrier.

Correct pattern:

- Chapter/H3 BUILD reaches BUILD_GREEN;
- feature-level review enters VERIFY;
- tests/review can be sharded across independent workers/roots;
- unrelated later BUILD may begin if HARD dependencies are satisfied;
- failures create REPAIR work for the affected subgraph;
- prior unrelated build keeps moving.

Example:

- H3-X BUILD_GREEN;
- verifier/reviewer roots inspect X;
- H3-Y, independent or SOFT-unlocked, starts BUILD concurrently;
- if X review finds a defect, repair X and invalidate only evidence that depends on the changed candidate generation;
- do not halt the whole portfolio.

Use one verifier per meaningful independent verification domain where useful. Do not give one Codex ten unrelated test domains and allow it to execute them sequentially for hours when they can be isolated.

But do **not** parallelize shared-state tests that would interfere or invalidate evidence.

Any review/test evidence must bind to the exact candidate SHA/tree. A repaired candidate creates a new generation; old verification does not float automatically.

---

## 16. Frozen Core vs Launch Overlay — critical anti-context-drift rule

Frozen Core contains stable task intent:

- goal;
- dependencies;
- deliverables;
- read/write scope;
- consumed contract fingerprints;
- prohibited scope;
- focused tests;
- H4 decomposition;
- parallelism contract;
- failure policy;
- terminal receipt schema.

Launch Overlay contains mutable launch-time facts:

- exact BASE SHA;
- exact dependency heads;
- branch/worktree;
- open Problems;
- current contract deltas;
- resource leases;
- resolved model identity;
- reconciliation head.

Do not regenerate a Frozen Core because only implementation SHAs changed.

Invalidation rule:

- upstream implementation SHA changed but consumed contract unchanged -> Frozen Core may remain valid;
- consumed contract fingerprint changed -> packet becomes DIRTY;
- authority changed -> packet becomes BLOCKED/DIRTY as appropriate.

Before each future batch, ChatGPT may revise the launch overlay or a genuinely dirty future core. This is expected. What is prohibited is casual whole-project replanning because context has drifted.

---

## 17. Prompt delivery style to the owner

When the time comes to give Codex prompts:

- use **separate fenced code blocks** for each Codex prompt;
- do not use writing blocks;
- clearly label task ID;
- prefer a fresh Codex session unless an exact dependency/continuity reason requires the same session;
- prompt must explicitly instruct concurrent subagent use where useful;
- prompt must explicitly preserve exclusive writer ownership;
- prompt must tell large-report workers to write durable findings to repo and return compact summaries;
- prompt must ask for a short terminal receipt.

The owner will copy Codex receipts back to ChatGPT. ChatGPT should use receipts to locate exact repo evidence, not ask the owner to paste giant logs.

---

## 18. Compact terminal receipt contract

Current prompt core receipt fields:

- `TASK`
- `STATUS`
- `BASE_SHA`
- `HEAD_SHA`
- `CHANGED_PATHS`
- `FOCUSED_TESTS`
- `CANDIDATE_GENERATION`
- `CONTRACT_DELTAS`
- `PROBLEMS`
- `DURABLE_HANDOFF`
- `UNLOCKS`
- `PUSH_STATUS`

Detailed child reports belong in repository run-state files.

A Codex “DONE” message is not proof. Independently inspect Git state/evidence before accepting it.

---

## 19. Problem / remediation behavior

Unexpected failure:

1. use systematic-debugging;
2. identify root-cause family;
3. attempt evidence-supported remediation;
4. maximum default failed product generations per load-bearing root-cause family: 3;
5. after exhaustion, PARK affected descendants;
6. keep independent READY work moving.

Environment enable work does not consume a product generation.

One broad unknown safety/integrity blast radius may quarantine an affected subgraph, but do not use that as an excuse to globally stop unrelated work.

---

## 20. What must NOT happen in the next chat

Do not:

- restart a broad “how much of the project remains?” analysis;
- re-brainstorm the already approved execution Atlas;
- regenerate H1-A..E prompts;
- return to the old “one heavy job max = 1” policy;
- return to a fixed four-root cap;
- invoke stock reviewer-after-every-inner-task subagent-driven-development as the default;
- make review/testing a global chapter barrier;
- silently treat chapter order as serial;
- silently upgrade semantic timestamps into exact edit boundaries;
- merge old Gate-1/Gate-2 controller branches wholesale;
- claim prompt-library coverage equals product execution completion;
- claim tests/runtime verification passed when it was not freshly observed;
- dispatch real H3 execution prompts before the implementation plan reaches `PROMPTS_READY_FOR_DISPATCH`;
- use protected/archive media, provider/cloud, model downloads, production export, or Gate promotion without new explicit authority.

---

## 21. Fresh-session one-paragraph operating instruction

After reading and verifying this file, the next ChatGPT should say internally:

> The execution architecture is already approved and durable. Repository state, not old chat memory, is authoritative. D1–D5 are complete prompt-library chunks; 27/33 cores are frozen; no H3 product execution has been dispatched. Resume with D6/H1-F only, using the same chapter-by-chapter Frozen Core generation/hash/audit/closeout/checkpoint pattern. Do not redesign prior chapters. Preserve parallel BUILD/VERIFY/REPAIR semantics and resource-policy v5. When D6 is complete, stop and wait for the owner's next “devam et”.

---

## 22. Six-cycle handoff quality criteria

This handoff should be considered valid only if all six checks remain true at read time:

### Cycle 1 — authority/state
- current main independently verified;
- current durable D5 branch independently verified;
- repository evidence wins over chat.

### Cycle 2 — continuity
- completed chunks and exact heads are recorded;
- next chunk is unambiguous;
- no completed chapter needs conversational reconstruction.

### Cycle 3 — anti-loop
- explicit prohibition on redoing broad analysis/review/planning;
- Frozen Core / Launch Overlay invalidation rules are present;
- testing/review remain asynchronous frontiers rather than global barriers.

### Cycle 4 — parallelism/ergonomics
- root/subagent/supervisor roles are explicit;
- independent work dispatches concurrently;
- exclusive writer ownership is preserved;
- compact receipts + durable repo reports preserve context.

### Cycle 5 — scientific/safety integrity
- temporal/evidence/source authority invariants preserved;
- separate authorization backlog remains visible;
- no production/protected/provider/Gate authority silently widened.

### Cycle 6 — next-action executability
- D6 exact H3s, dependencies, write domains, resources, and workflow are stated;
- later D7/E/F/G/H sequence is stated;
- “devam et” has one deterministic resume point.

If any of these are false because the repository changed after this handoff, perform a **narrow delta reconciliation**, update the handoff/current-state files, and continue. Do not restart the entire design process.


## 23. Six-cycle refinement result at handoff freeze

The handoff was re-read after creation against fresh repository evidence. Result at the handoff freeze:

1. **Authority/state — PASS**
   - canonical `main` reverified at `9151b712e8fb3d81c6089848e61a727aa83141ee`;
   - cumulative D5 prompt branch reverified at `bd8ab438e792801cebb58706dce76a974b984ca5`;
   - D6 prompt branch search returned no existing H1-F branch;
   - repository state correctly superseded the visible conversation state where they differed.

2. **Continuity — PASS**
   - Chunk A/B/C and D1–D5 durable heads are recorded;
   - cumulative machine-state paths and branch are explicit;
   - D1–D5 are explicitly marked “do not regenerate”;
   - D6 is the unique resume point.

3. **Anti-loop — PASS**
   - broad re-analysis/re-brainstorming/review-loop restart is explicitly prohibited;
   - prompt-library progress is explicitly separated from H0 product execution progress;
   - Frozen Core vs Launch Overlay invalidation semantics are explicit;
   - “devam et” is defined as advancing one durable chunk, not redesigning prior chunks.

4. **Parallelism/ergonomics — PASS**
   - BUILD/VERIFY/REPAIR concurrency is explicit;
   - root/area-lead/worker roles are explicit;
   - independent H4 work is concurrent;
   - exclusive writer ownership and adaptive resource leases are preserved;
   - compact receipts and durable repo reports are explicit.

5. **Scientific/safety integrity — PASS**
   - source immutability, source-native PTS/timebase authority, VFR prohibition, and evidence classes are preserved;
   - protected/archive/provider/model-download/production/Gate-promotion authority remains outside current scope;
   - no evidence class is silently upgraded.

6. **Next-action executability — PASS**
   - H3-F01/F02/F03 titles, weights, dependencies, current consumed contracts, write domains, and resource classes are recorded;
   - exact D6 procedure is listed;
   - D7 and Chunks E/F/G/H are listed through `PROMPTS_READY_FOR_DISPATCH` and controlled promotion.

Mechanical handoff scan at freeze:

- required continuity markers missing: `0`;
- unresolved placeholder tokens: `0`;
- handoff branch changed paths: documentation/state handoff surfaces only;
- product execution started by this handoff: `NO`.
