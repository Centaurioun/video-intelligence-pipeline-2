# Four-Gate Product Completion — First-Wave Execution Plan

> **For agentic workers:** For independent READY lanes use `superpowers:dispatching-parallel-agents` under the current VIP rolling-frontier protocol; for any product behavior change first use `superpowers:test-driven-development`; use `superpowers:systematic-debugging` on unexpected failures. Do not reflexively invoke stock per-task subagent review where `AGENTS.md` overrides it. All branches/reviews require fresh independent verification.

**Goal:** Begin the approved Gate 0–3 product-completion WBS with the maximum genuinely independent readiness/implementation work, identify actual executable product gaps and unblock authorized next steps without creating fake media/model evidence.

**Architecture:** Four independent Gate-root tasks, one controller keeping a rolling READY frontier, separate Git branches/worktrees and one controlled integration path. First-wave tasks are bounded, read-only / documentation-evidence tasks; independent existing synthetic checks may be run in an authorized local worktree. Subsequent code tasks must be separately planned with exact interfaces/files/tests and owner-approved scope where applicable.

**Tech Stack:** Existing Python / NumPy / SQLite / Pytest / FFmpeg interface contracts; current GitHub main and Project WBS.

**Spec:** `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md`

## Global Constraints

- Exact approved design checkpoint: `a39d7447a364b3ceac13a5cc6d466b185235b9af`. Fetch live main before creating worktrees; freeze each packet's own BASE_SHA.
- **Never alter backup** `backup/OWNER-DO-NOT-MODIFY-main-20261024-17edacbe@17edacbe64983ae284f09a8386377200bf538ec3`. See issue #149. Do not modify canonical main directly or automatically merge any future implementation.
- Source immutable; semantic candidates are `MATCHED`, edit temporal evidence must be `MEASURED` from source-native integer PTS/timebase, never nominal FPS multiplication.
- Development `SOURCE-AUTH` remains `DISABLED_BY_OWNER`; do not restore grant/Witness/administrative permission workflow for ordinary synthetic code.
- **Not authorized by this plan:** access to real/protected archive media, real model execution/acquisition, provider/cloud/network egress, real preview/export, host-specific attestation, Gate promotion, destructive Git/ref cleanup, GitHub ruleset changes.
- Read current `AGENTS.md`, four project handoff files, respective Gate specs, `THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`, `SUBAGENT_LANE_PROTOCOL.md`, `resource-policy-v5.yaml` before execution.
- Exclusive writers; serialized shared-contract and worktree-admin operations; no duplicated implementation purely to occupy threads. Release reviewer ownership promptly; verify branch SHA and result before calling a checkbox `[x]`.

## Review Focus

1. Historical handoff percentages or SHA descriptions mistakenly upgraded over current main: report `STALE_HISTORY` rather than asserting product maturity.
2. A model-free `ModelProfile` confused with authentic tokenizer/processor acceptance: classify `NOT_OBSERVED` unless real approved runtime evidence exists.
3. Synthetic Gate-2 `PASS` interpreted as real recovery/scale evidence: keep test domain separate from measured live workload.
4. Gate-3 nonproduction `TechnicalQCReport.status == PASS` confused with export eligibility: preserve `production_eligible=False`, `export_eligible=False`.
5. Gate-0 sample windows accidentally upgraded to measured VFR edit frame endpoints: refuse unless actual PTS/frame observation supports it.

## Task 0 — Single-Wrtier Bootstrap (serial)

- [ ] Fetch current `origin/main`, verify backup SHA, record immutable `BASE_SHA`, environment/tool availability and open PRs; abort on unexpected mutation.
- [ ] Determine four clean, independent root branches/worktrees, one output path per root, and owner for shared interfaces; schedule only READY work.
- [ ] Declare the initial root portfolio; do **not** create admin grants, pretend model/source authority, or spawn agents just to maintain a numerical count.

## Task 1 — Gate 0 Diagnostic Readiness (G0.1.4 + G0.2.2)

**Exclusive output:** `docs/agent-runs/YYYY-MM-DD-four-gate-first-wave/gate0-readiness.md` (a bounded, evidence-based report; no edits to Gate-0 governing contract).

**Read:** `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`; `src/gate0/arms/{metadata,semantic}.py`; `src/gate0/stages/{inventory,embed,rank,evaluate,report}.py`; `src/gate0/feasibility/macos_stage_b_evidence_s8.py`; existing integration tests.

- [ ] **Step 1** — Map each named Gate-0 experiment artifact and quality/validity rule to exact current modules and tests. Identify a missing implementation **only** with symbol/input/output evidence.
- [ ] **Step 2** — Split status: implemented code; synthetic test evidence; real host/media/model evidence `NOT_OBSERVED`; readiness blocked by exact named scope.
- [ ] **Step 3** — Prepare a *query-set template*, **not frozen queries**, for the 24 positive / eight absent / eight development queries; wording comes from actual editor(s), not fabricated model text. Record blind human-label protocol but do not create fake labels.
- [ ] **Step 4** — List minimum prerequisites for a valid future Gate-0 experiment (corpus source identity/policy, 2 reviewers, frozen split, technical window/configuration); quote frozen thresholds without changing them.
- [ ] **Step 5** — Publish exact evidence and next READY implementation task, or `VERIFIED_NO_CHANGE`. Avoid unapproved real media.

**Independent acceptance:** Report includes source blob/ref pointers, explicit absent-data states, dependencies, and zero gate-promotion claims. If a genuine code gap is found, propose a separate tiny TDD task with exact tests rather than changing production code in this audit lane.

## Task 2 — Gate 1 V1/V2 Representation Readiness (G1.1.4)

**Exclusive output:** `docs/agent-runs/YYYY-MM-DD-four-gate-first-wave/gate1-readiness.md`.

**Read:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`; approved V2 design/plan; `experiments/persistent_local_index/{model_profile,model_space,indexer,search,local_model}.py`; `src/vip_fvs/{semantic_index,cli}.py`; synthetic harness.

- [ ] **Step 1** — Reconcile V1 preserved ref and baseline with today's product code; do not assume older exact SHA is a current write base.
- [ ] **Step 2** — Map V2 model-profile validation, width geometry, CLI selection, native authentic Base/SO400M adapters, and acceptance tests to actual implementations.
- [ ] **Step 3** — Verify Gate-B / existing Task 0 readiness status, and whether any previous synthetic exception covers a specific product-code task. **Do not extend authorization from design approval.**
- [ ] **Step 4** — Determine smallest disjoint first coding tasks, ownership and TDD acceptance, if genuinely authorized. Keep authentic runtime and benchmark behind their own gates.
- [ ] **Step 5** — Publish baseline, missing components, blockers and dependent next READY tasks.

**Independent acceptance:** Unambiguous distinction between model-free configuration, genuine model/runtime acceptance, three-arm synthetic compatibility and real benchmark; no download or real inference.

## Task 3 — Gate 2 Workload and Observability Readiness (G2.1.3 + G2.1.4)

**Exclusive output:** `docs/agent-runs/YYYY-MM-DD-four-gate-first-wave/gate2-readiness.md`.

**Read:** `src/gate2/{workload,faults,decision}.py`; workload/measurement/fault tests; Gate-2 current decision/contract; `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`.

- [ ] **Step 1** — Inventory existing synthetic workload, fault-injection and evidence decision APIs; avoid reopening settled synthetic mechanism work.
- [ ] **Step 2** — Produce a workload-profile *schema/template* covering source count, lengths, codec/stream diversity, CPU/MPS, storage, query mix, concurrency, interruption and recovery, **not invented target archive statistics**.
- [ ] **Step 3** — Identify exact workload and tool/host measurements still `NOT_OBSERVED` and the boundary between runnable synthetic fixtures and unauthorized real work.
- [ ] **Step 4** — Propose the minimum bounded synthetic workload run (if actually runnable) and outcome records; do not add queues, ANN, Redis, cache or new schedulers before measurements.
- [ ] **Step 5** — Publish readiness and named exact next dependency unlocks.

**Independent acceptance:** The plan's resource metrics reflect actual existing APIs; all unavailable host/production quantities remain `NOT_OBSERVED`; no premature scale-mechanism commits.

## Task 4 — Gate 3 Editing/QC Chain Readiness (G3.1.5 + G3.2.1)

**Exclusive output:** `docs/agent-runs/YYYY-MM-DD-four-gate-first-wave/gate3-readiness.md`.

**Read:** `src/vip_fvs/{cli,real_source_service,source_snapshot,real_preview_qc}.py`; `src/gate3/{refinement,functional_prototype}.py`; existing synthetic FVS/PTS/refusal tests; relevant preview/plan schemas.

- [ ] **Step 1** — Trace exact code path: candidate/semantic interval → source revision/digest → authoritative PTS interval → editorial review → versioned plan → technical preview verification/QC.
- [ ] **Step 2** — Identify proven end-to-end entrypoints, synthetic coverage vs real runtime/FFmpeg results, missing product joins (not optional extra test work).
- [ ] **Step 3** — Specify a bounded, *not yet executed*, local V1 pilot scenario and exact additional media/FFmpeg/reviewer authorizations; separate this source set from Gate-0 evaluation labels.
- [ ] **Step 4** — Record blocking gaps in edit/output identity, source handling, audio or editorial QC; distinguish `NOT_OBSERVED` from product defect.
- [ ] **Step 5** — Publish next independently executable integration repair tasks and their minimum TDD interfaces.

**Independent acceptance:** No semantic timestamps as edit boundaries, no VFR FPS interpolation, no claimed production eligibility from non-production preview.

## Task 5 — Rolling-Frontier Integration (single writer, after Tasks 1–4)

- [ ] Independently fetch each Gate-root handoff and its actual committed diff; verify SHA, only owned output paths, citations to source blobs and `NOT_OBSERVED` claims.
- [ ] Review each candidate, run available synthetic checks when environment permits, and record any inherited failures separately from changes.
- [ ] Integrate accepted readiness facts into the WBS **without promoting checkmarks that are only proposals or reports**. Base-candidate changes must not modify the Owner-frozen backup.
- [ ] Immediately dispatch the next genuinely READY code tasks *if* independent, individually scoped, and authorized; each feature/bugfix must have a TDD implementation task and review.
- [ ] Report `STARTED`, `PUBLISHED`, `BLOCKED`, `NOT_OBSERVED` accurately; do not call documentation-only readiness reports a finished product.

## Ownership and Dependency Schedule

| Root | Task | Initial status | Read side | Exclusive write side | Unlock |
|---|---|---|---|---|---|
| G0 | Task 1 | READY_READ_ONLY | Gate-0 contract/stages | `gate0-readiness.md` | experiment/corpus permission, code gap tasks |
| G1 | Task 2 | READY_READ_ONLY | V1/V2 model/index source | `gate1-readiness.md` | shared contract freeze then disjoint source tasks |
| G2 | Task 3 | READY_READ_ONLY | Gate-2 source/resource contract | `gate2-readiness.md` | bounded synthetic workload, then exact real workload |
| G3 | Task 4 | READY_READ_ONLY | FVS/PTS/QC source | `gate3-readiness.md` | actual missing integration code, permitted V1 pilot |

**Root-level independence:** all four Tasks 1–4 can run concurrently after one serialized bootstrap, since they write different report files and only read the current pinned product tree. **Subtask independence:** each root may split coherent *inspection* domains, but freezes shared findings in its own report. Do not create children for a single trivial bullet. No one may write `docs/project/12_...` concurrently; the integration controller owns that tracker.

**Next natural review:** ask the Owner only for specific media/model/production/Gate decisions when an actually READY branch requires them; do not return for permission to perform ordinary, independently scoped read-only or synthetic development already approved by applicable authority.
