# VIP V2 Execution Portfolio — Six-Cycle Architecture Design

**Date:** 2026-10-09  
**Repository:** `Centaurioun/video-intelligence-pipeline`  
**Design approach:** Superpowers `brainstorming`, six iterative critical-refinement cycles  
**State:** `DRAFT_FOR_OWNER_WRITTEN_SPEC_REVIEW`; the user **approved the concept of a NEW Portfolio epoch and requested this design exercise**, not its immediate operational creation. This written spec, the subsequent execution plan, and their execution have **not** yet been reviewed/approved as distinct gates.  
**Scope:** execution orchestration of the *already designed* V1 -> SigLIP2 Base -> SigLIP2 SO400M representation migration; **not** a redesign of VIP product semantics.

## 1. Verified evidence and design brief

### User intent

Build a **new** Codex-controlled Portfolio **inside the same VIP repository**, similar in operating philosophy to the successful Remaining Work Portfolio, but with a new name, epoch, DAG, ledgers, controller instances, worktrees, task packets, milestone SHAs and independent progress. The old Remaining Work Portfolio is a **read-only precedent**, not a partially open set of jobs to resume. The user wants a sustained, dependency-safe, parallel upgrade of completed local-first V1 into SigLIP2-based V2, while keeping V1 independently recoverable and preserving all evidence/PTS/authorization contracts. Use Superpowers brainstorming and **six analytical iterative-refinement rounds** before designing execution steps.

### Verified GitHub anchors at design time

- Canonical VIP `main`: **67591ed50f14055f876690f786e11dd7b8f2c3f4**, after [PR #65](https://github.com/Centaurioun/video-intelligence-pipeline/pull/65) published the V2 migration plan and Git preservation receipt.
- Immutable V1 *Git commit reference*: `preservation/vip-v1-post-v2-design-20261009@3586eeaa904fc5a2e6a2745078611886f482f3de`; this preserves committed code and documents **only**. It is not a local model/index/runtime/video backup.
- Historical Remaining Work top controller: `controller/remaining-work/authoritative@a81104f47667a7f9ee1f47a86e1bfe711bfa2dd4`; Area G terminal evidence: `controller/area/G@988b8790cc45ad1c1093f0d1ebbae15ab0716f38`. [Terminal adoption audit](../../project/07_2026-10-08_CANONICAL_ADOPTION_AND_DECISION_RECOVERY.md) describes V1 authorized local-first engineering scope as finished, *not* the entire archive/Gate/production project.
- The historical [Remaining Work Atlas](../../../.orchestration/remaining-work/atlas/TABLE_OF_CONTENTS.md) had **33 H3 tasks across A–G**, a 100-unit *historical* finish-line denominator, Frozen Core + Launch Overlay, BUILD/VERIFY/REPAIR frontiers and evidence-bound final G03. Its `controller-state.json` on current main still contains `RECONCILED_NEXT_PACK_GENERATED_UNDISPATCHED`, which is a **historical main-side snapshot**, not the controlling terminal controller state. Neither historical progress nor H3 IDs may be copied into V2.
- Governing process: `AGENTS.md`, [Throughput-First protocol](../../architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md), [Remote Durability protocol](../../architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md), [Subagent Lane protocol](../../architecture/SUBAGENT_LANE_PROTOCOL.md), [v5 resource policy](../../portfolio/portfolio-v1/resource-policy-v5.yaml) and [Remaining Work Atlas spec](2026-10-03-remaining-work-execution-atlas-and-parallel-verification-design.md).
- Product design: [2026-10-09 V2 integration spec](2026-10-09-vip-v2-siglip2-integration-design.md) is **OWNER_APPROVED_FOR_PLANNING**; [2026-10-09 11-task implementation plan](../plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md) is **PENDING_OWNER_PLAN_REVIEW** and not executed. Binding [ADR-0002](../../decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md) specifies **V1 Base -> V2 Base -> SO400M -> separately frozen three-arm benchmark**.
- Spike SO400M data are on separate immutable experiment branch SHAs; [native evidence transfer](https://github.com/Centaurioun/vip-siglip2-so400m-browser-spike/blob/main/docs/native/VIP_V2_INTEGRATION_EVIDENCE_HANDOFF_2026-10-09.md). Authentic local FP16, FP32 and mixed Q4/FP16 image/text forwards were reported; Q8 is NOT_VERIFIED; tokenizer BOS/EOS semantic validity is unresolved. This does not authorize additional model downloads/inference.
- **Crucial tooling fact:** `scripts/verify-remaining-work-atlas.py` hard-codes `remaining-work-atlas.v1`, `.orchestration/remaining-work/`, and historical source ledger commits/blobs. `scripts/render-remaining-work-launch-pack.py` hard-codes the same previous epoch's atlas and bootstrap locations. **These scripts cannot be safely pointed at an empty new directory by renaming a few paths.** The historical `scripts/remaining_work_contracts.py` also contains explicit legacy Git/blob anchors. Treat reusable validation rules separately from historical instance identities.

**Status interpretation:** Git refs and docs above were independently read via GitHub; fresh Codex Mac environment/build/benchmark tests were **NOT_RUN** in this design exercise. If `main` advances, the V2 launch overlay must record the new verified main plus any source-contract deltas; no implicit rebase.

## 2. Proposed scope and finish line

Working name: **VIP V2 Execution Portfolio**. Proposed unique epoch identifier: `vip-v2-execution-portfolio-20261009-v1`. Only the **new** orchestration namespace owns this identifier. Names are intentionally distinguishable from the old Remaining Work `H3-A01` etc.

**H0 target:** `V2_BASE_AND_SO400M_CANDIDATES_IMPLEMENTED_AND_INDEPENDENTLY_VERIFIED_WITH_V1_PRESERVED`, **subject to exact authorized model/runtime smoke availability**. This is a **candidate-engineering** finish line, not source-wide retrieval superiority, benchmark winner, production or Gate maturity. If essential model authorization is unavailable, H0 remains `BLOCKED_AUTHORIZATION` with dependency-safe source-independent work recorded, not falsely COMPLETE. No arbitrary percentage completion before verified nodes/weights.

The portfolio owns **only migration execution orchestration**. The separate 11-task product implementation plan owns model, storage, CLI, FVS behaviors and acceptance tests. Any new execution plan from this spec must *bind* the approved product plan rather than silently extend/rewrite it.

**Always excluded without separate current authorization:** protected/real archive reads, model/checkpoint acquisition, provider/cloud requests, network egress except explicitly allowed routine development prerequisites, real model inference/precision experiments, full archive indexing, edit/export/render, Gate promotion, integration to protected `main`, destructive Git operations. Source-native PTS/timebase, immutable source SHA and human editorial boundary remain authoritative.

## 3. Alternatives considered

### Option A — Restart historical Remaining Work Atlas (REJECTED)

Pros: almost no new files. Fatal flaws: reopens completed H3 nodes, reuses 100/100 denominator, encourages consumption of stale `main` controller-state and overwrites A–G historical provenance. Invalidates terminal V1 trust and historical prompt hashes. Reconsider **never as a state mutation**; historical records remain evidence only.

### Option B — Single monolithic Codex with sequential tasks (REJECTED)

Pros: easier to start. Fatal flaws: slow serial model/storage/adapter work, context swelling, idle independent CPU analysis while MPS load blocks, no exclusive area ownership. Useful only for inherently tiny or tightly coupled subtasks under a controller.

### Option C — **New V2 epoch + thin reuse of proven portfolio concepts** (RECOMMENDED)

One Portfolio Root Codex controls seven *logical* area domains A–G, new V2-specific H3/H4 IDs, isolated Git refs/branches, an adaptive DAG, immutable candidate lineage, Frozen Cores + per-launch overlays and separate BUILD/VERIFY/REPAIR. **Do not create seven constantly active Codex processes merely because there are seven areas.** Spawn top-level area roots only for truly READY independent work. The historical scripts remain intact; a narrow generic/parameterized V2-aware validator/launcher may be implemented **later**, with TDD and without weakening old epoch-specific evidence checks.

This option is an architectural design **recommendation**, not an executed deployment.

## 4. New epoch design

### 4.1 Identity and storage (PROPOSED, NOT CREATED)

```text
.orchestration/
  remaining-work/                  # read-only historical system, unchanged
  vip-v2-portfolio/                 # entirely NEW epoch
    START_HERE.md
    manifest.json                   # portfolio_id, exact Git baselines, authority, schema
    controller-state.json           # current next READY / frontiers / progress, distinct epoch
    atlas/
      atlas.json                    # new H0/H1/H2/H3 execution DAG
      TABLE_OF_CONTENTS.md
      contract-registry.json        # blob/fingerprint/owner for consumed/produced surfaces
      authority-backlog.json        # deferred runtime/media/winner/Gate authorizations
    prompts/<V2-H3-*>/
      core.md
      core.json
      overlay-<generation>.json
    launch-packs/<batch-id>/...
    areas/<A-G>/                    # area-specific ledgers and handoffs
    runs/<V2-H3-id>/...
    problems/<problem-id>.json
    convergence/<candidate-generation>/...
    verification/<candidate-generation>/...
```

This tree is a **future design artifact**, not current repo state. Use stable schema names such as `vip-v2-portfolio-atlas.v1`; keep `portfolio_id` in every record. Old task IDs use `H3-A01`; new tasks use `V2-H3-A01` (or an equivalent unambiguous prefix selected and validated at plan time), preventing accidental historical linkage. Exactly one control-plane writer per ledger/ref. Area ledgers are separately owned, with append/merge handled through a single reconciler; never let all workers append to one shared JSONL.

**Archive policy:** old `.orchestration/remaining-work/*`, `controller/remaining-work/*`, `controller/area/*` and their immutable SHAs remain untouched. New controller ref namespace might be `controller/vip-v2/portfolio` and `controller/vip-v2/area/<letter>` where Git branch nesting allows; confirm collisions/recovery safety when actually created.

### 4.2 Roles and task mapping

| Role | Bounded ownership | Existing approved product-plan tasks | Read/write rule |
|---|---|---|---|
| **Portfolio Root** | DAG/READY/dispatch, authority overlay, resource leases, contract deltas, candidate dispositions, owner escalation | Schedules 0–10 only; no ordinary coding | Sole Portfolio control-plane writer; never main directly |
| **Area A — Baseline & Readiness** | V1 completion evidence, mandatory post-completion refresh, runtime/dependency readiness, exact ref receipt | **Task 0** | Documentation/receipt/test-evidence exclusive; no synthetic product edits before governing readiness |
| **Area B — Model Identity** | Closed model profiles, SemanticSpace identity and asset validation | **Task 1** | Owns `model_profile.py`, `model_space.py` and companion profile tests until contract freeze |
| **Area C — Vector Persistence** | 768/1152 row geometry, storage/index/search/restart validation | **Tasks 2–3**, except shared FVS adapter path | Owns `storage.py`, `indexer.py`, `search.py` and related tests; cannot write `retrieval_adapter.py` concurrently with E |
| **Area D — Native SigLIP2 Base** | Exact native tokenizer/mask/pooling, checked loader, first V2 Base candidate | **Tasks 4,6** | Owns `siglip2_native.py` and native test surface for Base until verified candidate |
| **Area E — VIP Wiring & FVS** | CLI/session wiring, source permission, FVS provenance and source-native temporal regression | **Tasks 5,9** | Sole shared FVS/CLI owner; owns `retrieval_adapter.py` if change needed |
| **Area F — SO400M Candidate** | Immutable spike result analysis; 384/1152 upgrade and guarded MPS candidate | **Tasks 7–8** | Analytic read-only work can start early. Shared `siglip2_native.py`/`model_profile.py` edits only after D/B formally release contract ownership or through their existing owners; no concurrent conflicting writes |
| **Area G — Verification & Convergence** | Independent feature review, stale-base/contract validation, integrated candidate, acceptance + rollback handoff | **Task 10** | Read-only VERIFY may start after any BUILD_GREEN candidate; final integrator is exclusive and cannot self-certify without independent verification |

The number of root Codex processes is **adaptive**, not automatically seven. A–G are domain **responsibilities**, not fixed agent quotas or old A–G controller identities. If nested delegate spawning is not supported, flatten Root -> Workers. Multi-root automatic spawning must be actually supported by the Codex harness; if not, Root produces a numbered human-dispatch Launch Pack with copy-ready fresh-session prompts and tracks receipts.

### 4.3 Dependency classes and initial frontier

Distinguish `INDEPENDENT`, `SOFT_BUILD_DEPENDENCY`, `HARD_BUILD_DEPENDENCY`, `HARD_VERIFY_DEPENDENCY`, and **separate authority predicates**. A model authorization is not a build dependency that can become green by editing a JSON status.

```text
P0: exact preserved baseline + mandatory post-completion refresh (A)
  |-- P0-analytic-only: parallel historical spike/tokenizer/index/test reconnaissance
  |                    (B/C/D/F, READ_ONLY; no product mutation)
  v
[HARD readiness evidence gate: local V1 tests/refresh as applicable]
  -> B1: immutable profile / SemanticSpace contract (B, T1)
       |-> C1: index writer+SQLite recovery, 768/1152 (C, T2)
       |-> C2: search/fake dimension tests (C, T3; avoid shared file ownership)
       |-> D1: native V2 Base model adapter and tokenizer tests (D, T4)
       |           |
       |           +--> F0: SO400M spike-contract read-only analysis (F, independent)
       +---- [C1,C2,D1] --> E1: VIP runtime/CLI integration (E, T5)
                                 |--> E2: synthetic FVS/PTS (E, T9 partial)
                                 +--> D2: Base candidate real acceptance (D, T6)
                                      [HARD: checkpoint + explicit runtime authorization]
                                          |
                                          +--> F1: SO400M 384/1152 profile extension (F, T7)
                                                    [D2 VERIFIED per ADR dependency]
                                                --> F2: SO400M real MPS acceptance (F, T8)
                                                    [HARD: model/runtime permission + fresh preflight]
                                          |
                                          +--> E2: complete profile/PTS synthetic checks
  G: asynchronous independent feature VERIFY as candidates turn BUILD_GREEN
  G: final convergence only after necessary candidate reviews + contract matching
  -> separately designed, authorized 3-arm benchmark (NOT part of H0)
```

**Nuance:** strict Task 0 readiness is a hard **source-change entry** requirement in the existing implementation plan. Read-only technical reconnaissance, test mapping, contract delta analysis and prompt preparation may proceed without inventing a false A PASS. Do not turn a missing V2 Base checkpoint into permission to begin Task 6 or F's heavy model run. When Task 6 remains authorization-blocked, explicitly park hard descendants, keep safe READY work in other areas.

**Parallelism priority:** do not spawn B/C/D mutating code from a frozen V1 commit until A's implementation-entry preconditions pass. After B's published immutable contract is accepted, C and D are naturally independent; F can inspect spike in parallel without writing; E begins once C/D output interfaces match. Other source or FVS code paths remain outside scope.

### 4.4 Frozen Core, Launch Overlay and status machine

**Frozen Core** per genuinely independent H3 packet: approved task goal, exact file ownership, consumed/produced contracts, tests and acceptance predicates, prohibited actions, Superpowers routing, candidate receipt schema and expected review lane. Version + SHA256. Create these *only* after the new Portfolio design and execution-plan approvals, not as a substitute for them.

**Launch Overlay** is re-evaluated before dispatch: `portfolio_id`, exact baseline Git SHA, current `main` SHA, source/destination branch/worktree, actual dependency candidate SHAs/trees, consumed-contract fingerprints, active Problems, permission grant refs, resource leases, resolved Codex model identity, task deadlines if authorized, and expected report pointer. A Frozen Core never hard-codes a speculative future SHA.

Use `PLANNED, READY, BUILDING, BUILD_GREEN, VERIFY_READY, VERIFYING, VERIFIED, REPAIRING, PARKED, STALE_IN_FLIGHT, DIRTY_BY_CONTRACT_DELTA, SUPERSEDED` with exact candidate-generation binding. A worker's `PASS` output is not Portfolio `VERIFIED`: require Git object evidence and relevant tests/reviews of the **same exact tree**. Progress counts only new V2 H3 nodes with explicitly frozen denominator; no inherited historical 100/100.

**Rolling rule:** on terminal worker -> inspect exact candidate -> source/contract/authority check -> accept/reject/park -> close child -> unlock dependency-safe next work -> refill safe capacity. No artificial whole-wave sync. A BUILD_GREEN candidate can feed SOFT dependencies while VERIFY runs independently; a HARD_VERIFY descendant waits for VERIFIED.

### 4.5 Resource and execution policy

Inherit [resource-policy-v5](../../portfolio/portfolio-v1/resource-policy-v5.yaml) and current `AGENTS.md`; do not rewrite v5 or import its old `portfolio_epoch` into new state. New epoch may impose **stricter** overrides without widening authorizations.

- `MODEL_MPS`: **one active heavy SO400M/Metal model session initially**, even though generic v5 starts some MPS calibration at two; actual FP32 preflight had limited headroom. Increasing concurrency requires measured, independently authorized workload-specific memory evidence. Mere two-agent availability is not a resource grant. No Q4+FP32 concurrency by default.
- `ENV_ADMIN`: globally serialized, one writer for shared environment; code workers do not upgrade Torch/Transformers or install Metal kernels while sibling heavy work runs.
- `LIGHTWEIGHT_CPU_TEST`: parallel on disjoint tests/temporary dirs; `HEAVY_CPU`, `FFMPEG_HEAVY`: adaptive v5 leases only where permitted and measured. Do not use real archive media for calibration.
- `MODEL_DOWNLOAD`, `PROTECTED_MEDIA`, `CLOUD_INFERENCE`, `MAIN_MERGE`, `GATE_PROMOTION`: distinct explicit-authority predicates, default denied by this document.
- Reproducible separate runtime locks and effective precision/group-size/quantized coverage when used; all heavy attempts record preflight, swap and MPS allocation where available.
- Codex model/executor resolution follows current repo policy (requested `LUNA`, Medium by default, exact supported model frozen for each goal); no silent fallback or gratuitous subagent count.

### 4.6 Contract ownership, Git durability and stale candidate containment

- One exclusive **writer owner** per changed file/shared schema at a time. Shared paths `model_profile.py` (B then F) and `siglip2_native.py` (D then F) need an explicit **ownership-transfer record**, at a pinned accepted predecessor SHA. E exclusively owns `retrieval_adapter.py` and CLI integration; C may send a contract change request, not edit E's writable path.
- Root/area candidates develop on isolated branches/worktrees anchored to immutable refs, never direct `main` writes. A central controller may prepare worktrees through serialized topology operations; sibling roots cannot delete/prune/reset/rebase other worktrees.
- Accepted milestones are committed/pushed to **their assigned execution branches** with exact SHA/tree, tests, verification and handoffs. No unreviewed sibling cross-merge; G converges on a separate integration branch with stale-base/owner fingerprint checks. Protected-main merge requires a **separate explicit owner decision** and GitHub PR rules.
- Source/semantic contracts carry content-addressed fingerprints. Changed upstream API/metadata/digest causes dependent in-flight work to become `STALE_IN_FLIGHT`, non-integrable until rebased *safely through a reviewed successor branch* or verified compatible. Never assume a report from old generation can validate a new one.
- Preserve 2026-10-09 frozen V1 at `3586eeaa...`, including ability to select matching V1 model/runtime/index; no branch destruction, Git hard reset, force push, cleanup, or vector-space masquerade.

### 4.7 Failures, verification and owner's visibility

Each Problem records root cause family, exact command/failure, affected artifact/SHA, current candidates, blast radius, failed repair generations, an authorized remediation budget, and affected descendant nodes. Apply `systematic-debugging` before any fix; TDD RED-GREEN for behavior. Default three evidence-supported failed repair generations per load-bearing problem family under v5; after exhaustion PARK affected descendants, keep unaffected READY work moving and request a new decision if required. Environment prerequisite recovery is governed by existing v5, but **cannot** substitute for new model/download/real-media authorization.

Parallel VERIFY runs when exact candidate is BUILD_GREEN; route `requesting-code-review` at **feature/candidate boundary**, not per trivial worker subtask. Resolve findings via `receiving-code-review` and re-bind verification to new SHA. G final verification must cover V1 regressions, 768/1152 writer+recovery, tokenizer IDs/masks/pooling and meaningful pairing, local-only runtime constraints, source/PTS provenance, MPS guard and candidate reproducibility. Explicitly report unrun tests as NOT_OBSERVED.

User sees compact Portfolio status: active/READY/PARKED H3 nodes, progress by declared denominator, real risk, blocked authorities, exact milestone refs, and copy-ready Launch Packs where manual dispatch is necessary. No 18-hour chat transcript as primary project memory. Return to the user for genuine permission/boundary, chosen execution method or a material architecture conflict; ordinary bugs should not trigger replanning.

## 5. Six-cycle iterative refinement — challenge, correction and rerun criteria

These are **six sequential architecture-analysis/refinement passes** grounded in repository evidence. They are **not** six live agent swarms, six test executions or completed runtime certifications.

| Cycle | Initial candidate failure / adversarial challenge | Revision selected | Acceptance test for later implementation | Reopen if |
|---|---|---|---|---|
| **1 — Epoch isolation and true historical authority** | Copying `.orchestration/remaining-work` imports stale main-side controller state and completed 100/100 tasks into V2 | Fresh `vip-v2-portfolio` identity/paths/IDs/denominator/branch namespace; historical controller SHAs read-only | Cross-epoch test rejects old task IDs, atlas hashes, progress and old controller receipts | Explicit recovery evidence shows an actual shared state that must be ported without altering its provenance |
| **2 — Right-sized capabilities and parallel DAG** | Literal seven running controllers creates idle roots; serial tasks 0..10 waste independent capacity; SO400M could overtake Base | A–G *logical* domains, H3 based on real writer/test seams, true dependency and authority edges, rolling BUILD/VERIFY/REPAIR | DAG acyclic; READY nodes have unique writer domains; F runtime cannot READY before verified Base and permission; independent read-only work remains possible | Final refresh changes product file ownership or ADR-0002 sequence |
| **3 — Verifier/launcher portability and anti-drift** | Historical verifier hardcodes `.orchestration/remaining-work` and old ledger blobs; renaming the directory silently skips safeguards | Separate V2-aware, parameterized thin adapter over pure reusable validation rules; retain untouched historical verifier; one hash-bound Frozen Core + overlay for V2 | Negative tests for wrong epoch/path, malformed overlay, SHA mismatch, stale core and wrong historical ledger; old verifier regression unchanged | Safe extracted pure validation logic cannot be reused without excessive or security-weakening refactor |
| **4 — Ownership, concurrency and recovery** | B/F both edit model_profile.py and D/F both edit siglip2_native.py; one root's fix invalidates other roots' tests | Formal ownership handoff, immutable contract fingerprints, stale-in-flight quarantine, serialized topology operations, separate domain ledgers | Concurrent overlapping writers rejected, stale descendant nonintegrable, shared-contract transfer requires verified predecessor | Verified contract boundary needs a different owner split |
| **5 — Permission and Apple MPS resource safety** | Old policy's generic two-MPS initial limit misapplied to memory-tight SO400M; new Portfolio implicitly runs models or downloads them | Epoch-specific initial MPS lease 1; no model/media/provider authority inherited; environment-admin serial; explicit model/runtime checkpoint permissions | Unauthorized model fetch/inference fails before loading; memory guard blocks without fallback; unrelated CPU tests continue | Measured safe headroom and *new* explicit owner permission support cautious higher concurrency |
| **6 — Convergence, test evidence and honest finish line** | Multiple green Codex chats treated as release; incomplete tokenizer/Git+runtime indexes misrepresented as full V2 PASS | SHA-bound candidate reviews, fresh V1 regression plus V2 Base/SO400M isolated acceptance, G controlled convergence, downstream benchmark separate | Ref freeze, model/PTS/index tests bound to exact tree; G refuses unverified/mixed-space/unauthorized candidates; rollback selects exact V1 code+matching assets | Human-approved benchmark decision or genuine new Gate/production authorization extends the finish line |

**Net six-cycle effect:** no second product repo, no reuse of historical Portfolio state, no manufactured agent quota, no blind copy of hard-coded orchestration scripts, no overlapping model file owners, no automatic MPS parallelism, no synthetic smoke promoted to a retrieval winner.

## 6. Design-level correctness and implementation-planning gates

### Later machine-verifiable acceptance requirements

1. Schema: new `portfolio_id` and `epoch` on every manifest/ledger/packet/receipt, unique V2 node IDs, exact baseline refs, schema hashes; cross-epoch messages reject.
2. DAG/ownership: acyclic graph, declared dependencies satisfied by candidate-generation states, no write path overlapping READY workers, explicit transfer authority.
3. Prompt drift: Frozen Core content SHA verifies; overlays match current Git dependency heads, current lease, real permissions and model; contract delta invalidates only affected descendant cores/overlays.
4. Resource behavior: class-specific leases enforce one initial MODEL_MPS and one ENV_ADMIN; throttling heavy work does not stop independent lightweight jobs.
5. Reconciliation: exact source/head/tree, candidate tests + feature review SHA, remote push confirmation and stale-base check; no stale inflight merge.
6. Safety: source/archive immutable, model timestamp never measured edit boundary, actual PTS/timebase only, explicit permission before local model download/run, no Gate/production/main from this design.
7. Recovery: restart new controller from new state only, reconstruct READY frontier from durable receipts, detect inconsistent state, avoid duplicate work or retroactively accepting old H3.
8. Finish line: truthful separate V1/V2 Base/SO400M state labels and model/tokenizer/index test evidence; do not count unauthorized/blocked heavy tasks as PASS.

### Design-to-plan handoff (approval-dependent)

Upon **owner approval of this written spec**, invoke Superpowers `writing-plans` to create a **separate implementation plan for the V2 Portfolio *orchestration infrastructure*** (not a duplicate of the existing product migration plan). It should cover, in order:

1. Exact new epoch manifest + strict read-only legacy reference contract and baseline guard.
2. Minimal V2-aware atlas/launch verifier and renderer, with RED/GREEN tests, reusing extractable pure logic from historical scripts **without changing their published instance behavior**.
3. Formal capability DAG from the existing product Task 0–10 map and initial authorized readiness frontier.
4. Frozen Core library + launch overlays + permissions/resources/contracts/ownership validation.
5. Controller START_HERE, H3 receipt/status/Problem schema, recovery and Launch Delta Reconciliation.
6. First **readiness-only** Launch Pack, with generated/verified prompts and exact current SHAs, **not dispatched automatically**.
7. Independent review and verified portfolio bootstrap candidate/branch; request separate owner authorization and execution approach for real multi-root/agent work.

Do not implement this separate orchestration system until **both** the written spec and its own execution plan/method have been approved. The current 11-task V2 product implementation plan remains pending final plan review, and real model/media actions retain independent authorization gates. The early portfolio-bootstrap work is documentation/framework design, not V2 inference.

## 7. Self-review and decision request

- **Design brief:** matches owner's correction (“a NEW Portfolio within the SAME VIP repo, not continuation of Remaining Work”).
- **Historical separation:** immutable terminal and frozen V1 references preserved; no old H3/progress/branch writes or reinterpretation.
- **Scope:** one focused *orchestration* architecture, not bundled with product migration/benchmark specs.
- **Feasibility:** hard-coded old Atlas scripts explicitly identified, so “reuse” means extracting a supported invariant, not claiming scripts are already generic.
- **Dependencies:** no false Task 0 pass, no F real candidate before verified Base, no cross-model data sharing, no stale-base implicit integration.
- **User approval pending:** **written spec owner review required** before separate Portfolio infrastructure `writing-plans`. No new epoch, running root controllers, launch packs, model inference or source code currently exists under the proposed namespace. A design-review PR is appropriate; merge/promotion to current repository authority only after owner review.
