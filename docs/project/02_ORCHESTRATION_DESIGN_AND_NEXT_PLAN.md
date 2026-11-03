# Video Intelligence Pipeline — Orchestration Design & Next Plan

> **2026-10-08 terminal-local-first current plan:** PR #57 has merged the exact verified G02 candidate into protected `main`; PR #58 has merged a branch audit inventory/plan, not a recovery archive. The historical batch-002 and execution-active "next" notes below are superseded. The active non-destructive work is terminal control-plane consistency, rationale-index preservation, and verified Git-object recovery for branch hygiene. See `docs/project/01_CURRENT_STATE_AND_HANDOFF.md#0c-2026-10-08--canonical-product-adoption-verified-terminal-scope-historical-retention` and `docs/project/07_2026-10-08_CANONICAL_ADOPTION_AND_DECISION_RECOVERY.md`.

## 0C. 2026-10-08 Post-Adoption Next Sequence (no architecture/gate expansion)

1. **DONE:** Exact G02 product candidate `e956722a0fc2109eb4651ce728e919e691162511` merged via [PR #57](https://github.com/Centaurioun/video-intelligence-pipeline/pull/57) as `main@e752c2fc45b533a0c679a32459225d37165a7722`. G03 final terminal evidence remains under `controller/area/G@988b8790cc45ad1c1093f0d1ebbae15ab0716f38`.
2. **DONE — INVENTORY ONLY:** branch-head snapshot and audited sequence merged via [PR #58](https://github.com/Centaurioun/video-intelligence-pipeline/pull/58). This is not branch retirement or durable object reachability.
3. **NEXT — INDEPENDENT RECONCILIATION:** preserve terminal authority references `controller/remaining-work/authoritative@a81104f47667a7f9ee1f47a86e1bfe711bfa2dd4`; determine minimal valid import/pointer mechanism for terminal Atlas, controller state and progress. Validate exact content/refs and no false success upgrades before canonicalizing them. Preserve the separate admin source-authority trust root.
4. **NEXT — DECISION HISTORY:** index old accepted/rejected alternatives, main's canonical rationales, branch-unique design/handoff records, current open draft PRs and source citations. No stale proposal becomes active policy merely by preservation.
5. **REQUIRED BEFORE RETIREMENT:** fresh remote/local HEAD and dirty-worktree audit; create durable ref-reachable preservation of unique branch histories, independently restore-test a fresh clone or verified bundle, and publish a SHA-locked deletion candidate ledger with reviewer decision.
6. **LATER — OWNER REVIEW:** only after the above, perform limited reversible-by-restoration branch-retirement batches with per-ref checks and exact recovery receipts. No force push, reset, git clean, reflog expiration or object pruning.

**Excluded:** protected/archive media execution, provider/cloud/models, production export, Gate promotion, and claiming real-media visual/audio/scale evidence beyond documented observation.

> **Fresh-session resume note (execution-active):** read `docs/project/05_FRESH_SESSION_HANDOFF_2026-10-03_EXECUTION_ACTIVE_BATCH_002.md` after the standard bootstrap. Batch-001 is complete/reconciled; the current continuation target is Batch-002 plus the bounded E01/F01 durability-recovery lanes.

## 0A. 2026-10-03 Remaining-Work Atlas Next-Plan Override

The current orchestration target is the owner-approved Remaining Work Execution Atlas, not the historical fixed approximately-four-root bootstrap.

Current model:

- adaptive top-level Codex roots;
- H0/H1/H2/H3 hierarchy plus execution DAG;
- H4 concurrent subagent shards;
- BUILD / VERIFY / REPAIR concurrent frontiers;
- versioned Frozen Core prompts + launch overlays;
- Launch Packs for owner copy/paste dispatch;
- Launch Delta Reconciliation between batches;
- asynchronous H3 feature review before integration rather than reviewer-after-every-inner-task;
- resource-policy v5 class-specific adaptive leases.

Current implementation plan:
`docs/superpowers/plans/2026-10-03-remaining-work-execution-atlas-implementation-plan.md`.

Durable progress:

- Pre-dispatch hardening was promoted through PR #32 at canonical `main@dcf55530b1d08d4d025d1615fe0e99987e5a59a9`; fresh main readback confirmed the same six-task `batch-001`, Launch Bootstrap v2.0.2, and `prompts_dispatched=false`.
- The owner-approved Remaining Work Atlas architecture remains current; no new design/spec/implementation-plan cycle was opened.
- Frozen Core zigzag audit completed **33 / 33**; only H3-G02 and H3-G03 required semantic contract repair, both now **v1.0.1**. The other 31 cores were not rewritten.
- Launch Bootstrap **v2.0.2** is the single shared dispatch-time layer for safe worktree/bootstrap, canonical BASE/ancestry, core/contract/dependency/Problem/delta/resource preflight plus workspace-time packet-state recheck, verified Superpowers routing, and fail-closed stale/dirty handling.
- TDD hardening added regression coverage for core hash drift, contract drift, dependency state/head drift, current Problem drift, resource-lease drift, canonical main-ref disagreement, dirty worktrees, non-ancestor BASE, and stale embedded copy-ready Core/Overlay.
- Fresh executable evidence on exact production-script bytes at `1ab72ec241d0e158d2ad44181e9f241c51367ebd`: Python compile **3/3 PASS**; preflight harness **15/15 PASS**; renderer harness **10/10 PASS**; verifier harness **6/6 PASS**.
- GitHub Actions/status remains **NOT_OBSERVED** because this repository exposes no workflow/status run for the hardening branch.
- Real-tree byte audit: Frozen Cores **33/33 PASS**; batch-001 embedded Bootstrap/Overlay/Core **6/6 PASS**; writer overlap **0**; initial resource use **6/16 LIGHTWEIGHT_CPU_TEST**.
- Launch BASE remains `ee376e50936be6859b4b08dbbf57dbd8642f36fd`; no task-relevant delta was observed for any initial batch root.
- Current controller state remains `PROMPTS_READY_FOR_DISPATCH`; prompts are still **NOT DISPATCHED**.
- Current Launch Pack remains `.orchestration/remaining-work/launch-packs/batch-001/manifest.json`.
- After hardening is promoted and fresh-main readback passes, the next action remains: start the six batch-001 prompts concurrently in six fresh top-level Codex sessions and return compact terminal receipts for rolling-frontier reconciliation.

Do not reinterpret older sections below as requiring four roots, one heavy job, or serial chapter/certification barriers.


**Document role:** condensed repository-level orientation to the current preferred orchestration and execution sequencing  
**Update frequency:** only after material orchestration/design changes  
**Last refreshed:** 2026-09-22  
**Execution authority:** none created by this document; current explicit user authorization controls  
**Latest reconciliation:** `docs/audits/2026-09-21-real-source-fvs-mainline-integration-reconciliation.md`  
**Prior reconciliation:** `docs/audits/2026-09-13-portfolio-state-reconciliation-after-gate2-m3.md`

---

## 0. 2026-09-24 Execution Portfolio / Next-Plan Override

This section supersedes older routine orchestration/topology instructions below where they conflict. Older Gate-specific topology/state remains historical context and scientific evidence as labeled.

### Current orchestration

The preferred working model is now the **execution-first Execution Portfolio**.

Governing process protocols:

- `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`
- `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`
- `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`
- `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`
- `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`
- `docs/superpowers/specs/2026-09-23-execution-portfolio-orchestration-design.md`

Execution principles:

- Goals are milestone-sized.
- Multiple independent milestone roots may execute concurrently in isolated linked worktrees.
- Root agents are scheduler/dependency/integration controllers for their own milestone branch, not default inline workers.
- Substantive work is delegated aggressively when clean ownership exists.
- Preferred hierarchy is Root -> Area Lead -> Worker; flatten when nested delegation is unavailable.
- Rolling-frontier scheduling refills capacity continuously.
- Intermediate reviewer/certifier swarms are not the ordinary development loop.
- TDD, debugging, tests, deterministic verification, and evidence discipline remain.
- Roots never merge canonical main.
- Actual overlap/semantic conflicts are analyzed before later integration.
- Final review/certification is a later owner-directed epoch.

### Current resource policy

Current resource authority:

`docs/portfolio/portfolio-v1/resource-policy-v5.yaml`

Logical root/child concurrency is adaptive. Under v5, HEAVY_CPU/FFMPEG ordinary-development leases begin at 2 and may calibrate to 3; MODEL_MPS is measured separately. Resource-class failure lowers only that class rather than serializing unrelated work.

Routine development prerequisite recovery is also current policy:

- a routine missing package/tool/config is ENABLE work, not a terminal owner blocker by default;
- the root owns environment continuity and children return exact prerequisite evidence;
- shared project-environment mutation is serialized under `ENV_ADMIN`;
- Goal-local project/user-scoped environments may be created/repaired automatically;
- public package-registry retrieval solely for routine development dependencies is authorized;
- Homebrew/system-wide mutation, provider/model calls, model/checkpoint downloads, protected media, private credentials/registries, and unrelated network activity remain outside this authority;
- environment/import/collection failures do not count as behavioral RED;
- narrower Gate/task authority overrides the general policy, so Gate-0 Revision-18 remains unchanged.

### Current executable product evidence

The accepted real-source FVS / bounded non-production preview evidence and historical Gate evidence below remain intact. This process override does not upgrade any Gate, evidence class, production status, provider/model authority, or protected/archive-media authority.

### Immediate next sequence

Canonical process-policy promotion and remote branch hygiene are complete.

Before substantive Codex execution:

1. run S0 bounded local/remote synchronization on the primary local repository;
2. preserve/inventory local-only branches and legacy worktrees without deleting them;
3. run S1 Portfolio Bootstrap / Worktree Admin with **no product implementation**;
4. derive/freeze the current Execution Portfolio DAG from actual code/dependencies;
5. historical 2026-09-24 bootstrap targeted approximately four roots; current Atlas execution instead derives all READY H3 packets and launches an adaptive useful subset;
6. independently verify that bootstrap;
7. launch only genuinely independent root milestone Goals.

Current bootstrap contract:

`docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`

Do not reuse the old one-root/four-permanent-Gate-worktree topology as a mandatory current execution structure merely because it remains documented historically below.


---

## 1. Current Preferred Orchestration

The active orchestration remains **Hierarchical Continuous Parallelism** under one repository/remote, one admin worktree, and four isolated Gate worktrees/controller branches.

The four-Gate design is historical provenance at commit
`e69832477313c65e5ddd78e611d2eed4f5d78746`; the bootstrap evidence is historical
provenance at commit `369e8a6b141b36c81b947e406b00676987553aa4`. Both commits are
recoverable through `archive/history/branch-preservation-v1`. Current process authority is
the 2026-09-24 Execution Portfolio overlay and
[Execution Portfolio orchestration design](../superpowers/specs/2026-09-23-execution-portfolio-orchestration-design.md).

Executor amendment:

`docs/superpowers/specs/2026-09-13-deepseek-harness-four-gate-executor-amendment.md`

Preferred active Gate executor:

`DEEPSEEK_HARNESS`

Governance is executor-agnostic: repository authority, exact Gate/dependency SHAs, evidence classes, resource leases, and Gate scope control behavior. Codex is retained for bounded admin synchronization, fallback/recovery, and separately authorized verification, but must not be a simultaneous writer with Harness on the same Gate branch.

---

## 2. Stable Local Topology

```text
/Users/yusuf/Repos/video-intelligence-pipeline          # admin/canonical/reconciliation
/Users/yusuf/Repos/video-intelligence-pipeline-gate0    # Gate 0
/Users/yusuf/Repos/video-intelligence-pipeline-gate1    # Gate 1
/Users/yusuf/Repos/video-intelligence-pipeline-gate2    # Gate 2
/Users/yusuf/Repos/video-intelligence-pipeline-gate3    # Gate 3
```

No executor transition creates additional permanent worktrees. Temporary child writer worktrees are permitted only when a Gate controller needs filesystem isolation, and must be removed safely after integration and remote durability verification.

---

## 3. DeepSeek Harness Controller Pattern

Canonical controller profile:

`docs/portfolio/portfolio-v1/DEEPSEEK_HARNESS_CONTROLLER_PROFILE.md`

Resource policy:

`docs/portfolio/portfolio-v1/resource-policy-v2.yaml`

Activation plan:

`docs/superpowers/plans/2026-09-13-deepseek-harness-four-gate-activation.md`

The root Harness agent is primarily:

`CONTROLLER -> SCHEDULER -> INTEGRATOR -> VERIFIER`

It should keep its live context deliberately bounded and use durable repository evidence as project memory. Substantial independent work should be delegated to separate-context children when capability preflight passes and delegation is useful.

Child prompts must be self-contained and bind exact authority/dependency SHAs. One-shot children are preferred for bounded tasks; continuable children are reserved for genuine ordered follow-up. Read-only children may share a Gate worktree. Writer children require exclusive path ownership or isolated temporary child worktrees. The parent Gate controller owns integration.

---

## 4. Durable Goal Semantics

Milestone Goals use the bounded autonomous failure-remediation loop defined in
the repository-wide remote-durability protocol. Intermediate failures remain
internal scheduler events: preserve evidence, perform systematic root-cause
investigation, add RED coverage before behavior changes, review and verify the
smallest fix, then retry under a fresh digest-bound attempt authorization.
Standing remediation authority cannot widen source, timing, provider/model,
production/export, destructive, or Gate-promotion scope. Three confirmed
failed generations in one load-bearing area trigger architecture
reconsideration; otherwise the controller continues to the existing hard
boundary or terminal milestone state.

Each Gate root Harness session uses at most one active durable Goal.

The Goal is NOT “finish the Gate at any cost.” It means:

> Advance this Gate to the highest scientifically defensible, currently authorized, dependency-safe maturity state; execute genuine READY work; stop cleanly when the current frontier is exhausted or remaining work is gated.

Allowed frontier outcomes:

- `GOAL_COMPLETE_CURRENT_FRONTIER`
- `GOAL_PARKED_UPSTREAM_DEPENDENCY`
- `GOAL_BLOCKED_AUTHORIZATION`
- `GOAL_BLOCKED_TECHNICAL`
- `GOAL_NEEDS_ARCHITECTURE_REVIEW`

A parked/blocked state is valid. Do not invent speculative work to keep an autonomous Goal active.

A Goal records durable objective/completion state; it does not itself guarantee repeated scheduling. The controller must verify automatic goal-round continuation capability separately before claiming autonomous continuation. Subagent capability must likewise be positively observed before relying on child delegation.

---

## 5. Controller Ownership / Current Refs

Current Gate controller refs (2026-09-15 reconciliation snapshot; Gate-0/1/2 unchanged from 2026-09-13):

- Historical Gate-0 controller snapshot: `0ed4ae84fce07aa86d094d4f1e02775e095e93be`.
- Gate 1 operational controller: `controller/gate1/portfolio-v1@fdb39ea358cbf8690321df2790696669818d91d6`.
- Gate 2 operational controller: `controller/gate2/portfolio-v1@2ff37268d032af7287fc1f685e0e76f5b7654d2d`.
- Historical Gate-3 controller snapshot: `af60ab8d42c481dbbd2ecb141f3d130ab16accc1`.

Each `COORDINATOR_STATE.md` now declares DeepSeek Harness the preferred active executor and Codex the non-co-writer admin/fallback executor.

One Gate branch has exactly one active writer-controller identity at a time.

---

## 6. Gate States / Parallel Maturity Ceilings

### Gate 0 — Diagnostic Retrieval

Maturity: `M3_SYNTHETIC_READY`.

Execution base: `865c55c30147eb5320a80b70344f6201f98332f8`.

Current state: `STAGE_B_C2_IMPLEMENTATION_PLAN_REVISION_AWAITING_OWNER_APPROVAL` (Stage-B disposition
remains `STAGE_B_MACOS_APP_SANDBOX_FEASIBILITY_NEEDS_WORK_PROVIDER_PROBE_OBSERVABILITY`; no Stage-B
certified candidate exists).

Immediate frontier: owner review/approval of the revised (revision 2) C² implementation plan before
Implementation Phase A. Phase A (Tasks 1–8) is unauthorized pending that approval; Task 9's live signed
App-Sandbox hostname probe requires separate explicit owner authorization. No plan task has been executed.

### Gate 1 — Representation / Capability Benchmark

Maturity: `M3_SYNTHETIC_READY`.

Certified synthetic candidate: `2db80cdc666ef28e00e078db53d107b00a2bd41c`.

Real benchmark/model/provider winner: `NOT_OBSERVED`. Reversible benchmark preparation may be planned only
when separately authorized; winner selection remains evidence-gated.

Frontier: `PARKED_UPSTREAM_DEPENDENCY` pending an exact validity-bearing Gate-0 terminal milestone/receipt
SHA. The Gate-0 continuation base `865c55c30147eb5320a80b70344f6201f98332f8` is never acceptable as that
prerequisite.

### Gate 2 — Reliability / Scale

Maturity: `M3_SYNTHETIC_READY`.

Certified candidate: `88bff2e1be00bf3717a48c00a3529cabce3d16b5`.
Gate-local M3 closeout / state reconciliation: `2ff37268d032af7287fc1f685e0e76f5b7654d2d`.

Reliability/scale deficit: `NOT_OBSERVED`. Mechanism justified: `NONE`. `M4`: `NOT AUTHORIZED / NOT READY`.
Execution authorization for the synthetic implementation is `EXECUTED AND EXHAUSTED`.

Frontier: `PARKED_UPSTREAM_DEPENDENCY` on `DEP-1`, `DEP-5`, `DEP-6`, `DEP-9` (plus the parked Gate-0
remediation dependencies and the real-outcome bound recorded in Gate-local state). Do not preselect
Redis/Kafka/vector-service/durable-scheduler mechanisms. Queued hardening `C-1`…`C-10` is non-blocking and
unexecuted, and is not authorized by the current reconciliation.

### Gate 3 — Editing / QC

Maturity: `M1_CONTRACTED` (`M3_SYNTHETIC_READY` = `EVIDENCE_SUPPORTED`; `M3_PROMOTION = OWNER_RULING_PENDING`).

A Gate-3 local synthetic functional prototype now exists and is independently accepted: accepted functional
code SHA `1eddef9e31c705f3e07bf55b3de95f8807d1a1ab`, accepted evidence head
`dadbcfc4be1f397e5966fd8e8d68a079d93c67b1`, functional disposition
`GATE3_FUNCTIONAL_PASS_INDEPENDENTLY_ACCEPTED`. Historical static-security status remains
`AUTHORITY_PROTOCOL_STATIC_CERTIFICATION_BLOCKED`; deferred hardening remains
`DEFERRED_BY_OWNER_FOR_PROTOTYPE_COMPLETION`.

Protected-media editing/export, real-media validation and production QC remain `NOT_OBSERVED` and
unauthorized.

Frontier: `FUNCTIONAL_PROTOTYPE_COMPLETE — PARKED FOR OWNER PORTFOLIO DIRECTION`
(`STOPPED_AT_OWNER_FUNCTIONAL_FINISH_LINE`). The earlier plan-remediation frontier after the
`G3_PLAN_NEEDS_WORK` plan certification (frozen SHA `7d39003b87b908704b3da5422f01761850c809ac`, plan blob
`c2f9d937a2cdbd7375871f02c88b3cb3c8e52608`) is historical. Do not start another Gate-3 audit/repair
campaign, do not promote `M3`, and do not execute against protected/real media; continuation requires new
explicit owner direction. A plan verdict is not a Gate promotion.

---

## 7. Historical Portfolio-v1 Resource / Scheduling Policy (superseded for current scheduling)

Changing executor does not widen resources.

Current policy:

- four logical Gate controllers;
- max simultaneous candidate-writer Gate controllers: `2`;
- heavy model/FFmpeg/local-runtime execution: max `1` without new accepted measurement;
- canonical integration budget: `1`;
- Git worktree administration serialized;
- one active writer controller per Gate branch;
- shared-contract refs immutable during the current epoch;
- cross-Gate dependencies bind exact milestone/receipt SHAs;
- writer expansion follows measured ramp `2 -> 3 -> 4` only if accepted milestone throughput improves without unacceptable contention/rework.

Research/review subagents may scale adaptively where work is genuinely independent and resource-light. Logical child count never expands heavy-execution authority.

---

## 8. Gate-0 Stage-B Next Decision

The narrow Stage-B architecture/evidence-semantics review is **complete**: the owner approved the `C²`
direction (`C² — staged hostname / provider-shaped denial with route-class composition`), closing the
architecture-choice gate and ruling `SHARED_CONTRACT_AMENDMENT_NOT_REQUIRED`. Do not reopen architecture
discovery.

Do not begin broad Stage-B remediation. The current Gate-0 decision is owner review/approval of the revised
(revision 2) C² implementation plan before Implementation Phase A. Phase A (Tasks 1–8) is unauthorized until
that approval; Task 9's live signed App-Sandbox hostname probe requires a separate explicit owner
authorization afterwards. Any further PASS-contract change still requires explicit architecture approval
before implementation.

---

## 9. Current Execution Sequencing / Next Plan

Each Gate frontier is independent. There is no single serial portfolio workflow: Gate 1 and Gate 2 are
parked at `M3_SYNTHETIC_READY` before real outcome work, Gate 0 is at a plan-approval frontier before
Phase A, and Gate 3 is `FUNCTIONAL_PROTOTYPE_COMPLETE — PARKED FOR OWNER PORTFOLIO DIRECTION` under
`M1_CONTRACTED` (local synthetic functional prototype independently accepted; `M3` promotion
owner-ruling-pending).

Current per-Gate next action:

| Gate | Maturity | Current frontier | Next enabling event | Not authorized now |
| --- | --- | --- | --- | --- |
| Gate 0 | `M3_SYNTHETIC_READY` | Owner review/approval of revised C² implementation plan | Owner approval of the plan; later, separate authorization for Task 9 live signed probe | Implementation Phase A, broad Stage-B remediation, PASS-contract change |
| Gate 1 | `M3_SYNTHETIC_READY` | `PARKED_UPSTREAM_DEPENDENCY` before real benchmark outcome | Exact validity-bearing Gate-0 terminal milestone/receipt SHA, then new authorization | Real benchmark execution, winner selection |
| Gate 2 | `M3_SYNTHETIC_READY` | `PARKED_UPSTREAM_DEPENDENCY` before real reliability/scale outcome | `DEP-1`, `DEP-5`, `DEP-6`, `DEP-9` closure, then new authorization | Real workload measurement, infrastructure adoption, `C-1`…`C-10` hardening |
| Gate 3 | `M1_CONTRACTED` | `FUNCTIONAL_PROTOTYPE_COMPLETE — PARKED FOR OWNER PORTFOLIO DIRECTION` | New explicit owner direction (portfolio) | Gate-3 functional expansion, further audit/repair, `M3`/Gate promotion, protected/real media |

Historical note (completed, not current work): the one bounded admin Codex synchronization task, the
verification of the DeepSeek amendment/profile/resource-policy/activation-plan files from canonical
`origin/main`, and the opening of the four ChatGPT Gate-coordinator conversations were all part of the
executor-activation sequence and are **not** current next actions.

No new permanent worktrees are required.

---

## 10. Preservation / Prohibited Scope

Preservation refs and scientific invariants remain unchanged.

Still prohibited without separate explicit authority: protected/archive media; held-out/scored Gate-0; Issue #17; Gate promotion; MPS/CUDA; provider/cloud inference or provider transport; real-media Gate-3 validation; further Gate-3 audit/repair or functional-scope expansion; model download/change; Linux preservation mutation; Network Extension/system filtering; entitlement widening merely to force PASS; destructive cleanup; force push; hard reset; `git clean`; reflog destruction; private-key export or Apple-account/certificate mutation.

For exact current SHAs and state, read `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` first.
