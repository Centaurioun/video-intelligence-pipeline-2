
# Execution Portfolio Canonical Policy Promotion Plan

Execution method after owner approval: isolated promotion worktree plus inline plan execution. Owner override: no task-level reviewer/certifier swarm and no generic final reviewer step; deterministic/static verification only.

Goal: Promote the refined Execution Portfolio model into one coherent canonical process policy before any Codex product Goal begins.

Spec authority:
- docs/superpowers/specs/2026-09-23-execution-portfolio-orchestration-design.md
- refined blob ab92ab94584978e4c5d71450724b5b932ac80188

Companion:
- docs/superpowers/specs/2026-09-23-execution-portfolio-rejected-alternatives.md
- refined blob 5df5102fe5192e42f2e9db85cc9b9be4551ac224

## Global constraints

- No product implementation, Gate execution, provider/cloud/model activity, protected/archive-media execution, production export, Gate promotion, or branch cleanup.
- No hard reset, git clean, force push, reflog destruction, or unrelated branch/worktree deletion.
- Historical audits, lane evidence, model provenance, and frozen Gate records are not rewritten.
- Re-fetch canonical main immediately before execution. If it differs from 12e3b199591511f46c9e885008ad69237f462fb7, stop and reconcile this plan against the new state.
- Build and verify the candidate on planning/execution-portfolio-policy-promotion-v1 rooted from exact current origin/main; do not construct directly on main.
- Codex current policy becomes version-agnostic LUNA plus medium, resolved to one supported concrete model and frozen per Goal.
- DeepSeek keeps its currently verified model policy until explicitly changed.
- Nested delegation is capability-gated; flatten to Root -> Workers if Area Lead spawning cannot be verified.
- Root-writer concurrency and heavy model/FFmpeg concurrency are separate budgets.
- Canonical-main integration is a separate owner-controlled side effect.
- Branch hygiene is a later independent task.

## Promotion surface

Promote exact refined artifacts:
- docs/superpowers/specs/2026-09-23-execution-portfolio-orchestration-design.md
- docs/superpowers/specs/2026-09-23-execution-portfolio-rejected-alternatives.md
- this plan

Create:
- docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md
- docs/portfolio/portfolio-v1/resource-policy-v3.yaml

Modify:
- AGENTS.md
- docs/INDEX.md
- docs/architecture/SUBAGENT_LANE_PROTOCOL.md
- docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md
- docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md
- docs/project/01_CURRENT_STATE_AND_HANDOFF.md
- docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md
- docs/portfolio/portfolio-v1/DEEPSEEK_HARNESS_CONTROLLER_PROFILE.md

Preserve unchanged:
- docs/portfolio/portfolio-v1/resource-policy-v2.yaml
- docs/project/00_PROJECT_CHARTER.md
- historical audits, plans, lane memos, certifications, and Gate evidence

## Static failure modes this promotion must close

1. Split authority between final-only review and mandatory intermediate certifier waves.
2. Generation-specific gpt-5.6-luna current policy or silent within-Goal model drift.
3. Main-centric durability that implies ordinary execution must land directly on canonical main.
4. Conflation of root-writer concurrency with heavy model/FFmpeg concurrency.
5. Fresh-session recovery requiring old chat or mandatory Markdown lane essays.

---

## Task 1 — Freeze a clean promotion base

1. Fetch and verify origin/main.
2. Verify the refined design and alternatives blobs match the hashes above.
3. Use superpowers:using-git-worktrees to create planning/execution-portfolio-policy-promotion-v1 from exact origin/main.
4. Record the pre-edit RED baseline by searching current governing policy for:
   - gpt-5.6-luna
   - intermediate certifier-wave rules
   - mandatory per-child Markdown lane memos
   - default no-grandchildren rule
   - main-centric child durability
5. Confirm docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md is absent before promotion.

No file commit in Task 1.

## Task 2 — Promote the exact refined authority artifacts

Copy the refined design, alternatives register, and this plan into the promotion branch without regeneration.

Verify the two spec blobs remain:
- ab92ab94584978e4c5d71450724b5b932ac80188
- 5df5102fe5192e42f2e9db85cc9b9be4551ac224

Verify no file under docs/audits, docs/agent-runs, or docs/gates changed.

Commit message: docs: add execution portfolio authority

## Task 3 — Create THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md

Make this the primary current execution contract. It must normatively define:

- Goal = milestone, not micro-task.
- BUILD / ENABLE / REPAIR as ordinary execution classes.
- No intermediate REVIEW/CERTIFY/RECERTIFY swarm as the default loop.
- TDD, systematic debugging, tests, deterministic checks, and verification-before-completion remain.
- Multiple root Goals only when the portfolio DAG permits.
- Roots use isolated branches/worktrees and never merge to main.
- Preferred Root -> Area Lead -> Worker hierarchy with flat fallback.
- Maximum useful safe concurrency; no fixed child quota or fabricated work.
- Rolling frontier, child close/recycle, compact handoffs.
- Every child handoff binds BASE_SHA and stale-base handling.
- Shared contracts remain frozen assumptions unless a structured delta is declared.
- Context Curator is optional.
- Ephemeral scheduler state may stay local; durable recovery state is compact and machine-readable.
- Problem records are sharded by Goal/problem.
- Maximum three evidence-supported failed repair generations per root-cause family by default.
- Park only affected descendants while independent READY work continues.
- Actual-overlap and semantic-conflict analysis before integration.
- Adaptive convergence: analysis -> resolution design -> remediation -> integration.
- Canonical-main integration requires separate owner authority.
- Final review/certification is a later epoch.
- Branch hygiene is separate.
- Codex model policy is LUNA plus medium, resolved to one supported concrete model and frozen per Goal.
- Portfolio Bootstrap / Worktree Admin serializes shared worktree/ref topology operations.
- Fresh-session recovery chain: canonical policy -> current handoff -> portfolio manifest/anchor -> exact Goal/root -> durable lane/problem state -> Git heads/remote state -> model/resource leases.

Static verification must prove required concepts exist and gpt-5.6-luna is absent from this new current policy.

Commit message: docs: establish throughput-first execution policy

## Task 4 — Reconcile AGENTS.md and docs/INDEX.md

AGENTS.md:
- replace generation-specific Codex pin with LUNA / medium resolved and frozen per Goal;
- remove intermediate certification-wave defaults;
- replace mandatory Markdown child memo policy with compact machine state plus Git code/tests plus Problem records;
- replace default no-grandchildren rule with capability-gated Root -> Area Lead -> Worker maximum and flat fallback;
- make execution-branch durability primary;
- state roots never merge to main;
- point to throughput-first protocol as current execution authority.

docs/INDEX.md:
make the current process reading order explicit:
1. AGENTS.md
2. current project handoff
3. throughput-first protocol
4. subagent lane protocol
5. remote durability protocol
6. main sync protocol
7. resource-policy-v3
8. refined Execution Portfolio design

Keep historical Gate/audit links but do not present them as current orchestration authority.

Static checks:
- throughput-first protocol referenced by both files;
- no gpt-5.6-luna in AGENTS.md;
- LUNA and medium present;
- no current certifier-lane mandate.

Commit message: docs: switch repository entry policy to execution portfolio

## Task 5 — Rewrite the current Subagent Lane Protocol

Required current behavior:
- BUILD / ENABLE / REPAIR plus optional read-only scheduling/analysis roles;
- no mandatory narrative Markdown memo per child;
- compact handoff includes STATUS, GOAL/LANE, BASE_SHA, HEAD_SHA, CHANGED_PATHS, PUBLIC_INTERFACES_CHANGED, SHARED_SURFACES_TOUCHED, CONSUMED_CONTRACT_REFS, PRODUCED_CONTRACT_DELTAS, UNPLANNED_SHARED_SURFACES, ASSUMPTION_CHANGES, TEST_ENTRYPOINTS, OPEN_PROBLEM_IDS, BLOCKER, STATE_PATH;
- preferred Root -> Area Lead -> Worker hierarchy;
- flat fallback when nested delegation unavailable;
- stale-base check before candidate integration;
- exclusive writer ownership;
- unplanned shared surfaces recorded rather than silently cross-repaired;
- terminal lifecycle: persist -> compact handoff -> parent verifies scheduler facts -> disposition -> close -> recycle;
- no ordinary certification-wave sections.

Static checks must prove hierarchy/stale-base/problem/contract/machine-state concepts and absence of the old Codex pin/certifier default.

Commit message: docs: align subagent lanes with execution-first orchestration

## Task 6 — Reconcile Remote Durability and Main Sync

REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md:
- execution-branch checkpoint pushes are primary during Goals;
- no per-child remote-branch explosion by default;
- add multi-root branch isolation and immutable portfolio anchor;
- serialize shared worktree/ref administration;
- use Goal-frozen LUNA/medium resolution instead of generation-specific Codex name;
- remove ordinary code-review and broad-review requirements;
- retain TDD, systematic debugging, tests, deterministic verification.

MAIN_AGENT_SYNC_PROTOCOL.md:
- observe/fetch/compare canonical main at Goal boundaries;
- do not require every Goal to write or push canonical main;
- active execution branch is the writable durability surface;
- separate explicit authority is required for canonical-main mutation;
- if remote main advances, record the authority/base change and do not silently merge/rebase it into active work.

Commit message: docs: separate execution durability from canonical main

## Task 7 — Create resource-policy-v3 and align DeepSeek profile

Create docs/portfolio/portfolio-v1/resource-policy-v3.yaml.

Required semantics:
- schema_version: 3
- execution-portfolio epoch identity
- root writers adaptive dependency-safe, no fixed quota, one writer per exact branch
- worktree administration serialized
- reasoning subagents adaptive READY work and separate contexts
- Codex requested family LUNA, reasoning medium, resolve and freeze per Goal
- heavy local execution serial-or-explicit-lease, max 1 without new measurement
- FFmpeg/model-heavy execution serial-or-explicit-lease, max 1 without new measurement
- canonical main integration policy explicit owner decision, concurrency 1

Do not mutate resource-policy-v2.yaml.

Update DeepSeek profile so current Execution Portfolio use follows throughput/lane/resource-v3 policy while retaining currently verified DeepSeek model/reasoning rules.

Commit message: docs: add execution portfolio resource policy v3

## Task 8 — Update the current project handoff

01_CURRENT_STATE_AND_HANDOFF.md:
- add a new superseding top overlay;
- state Execution Portfolio is the primary day-to-day development path;
- list current governing process files and resource-v3;
- state execution-first/final-review-later;
- allow multiple isolated root milestone worktrees when DAG-safe;
- preserve all source/provider/model/production/Gate restrictions;
- state branch cleanup is a separate future hygiene task;
- state no Codex product Goal started merely because process policy was promoted.

02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md:
- point current orchestration to the now-real throughput protocol;
- classify old one-root/four-Gate worktree topology as historical rather than mandatory;
- remove current wording implying repeated review/certification is the normal next loop;
- preserve scientific/Gate facts and evidence states.

Commit message: docs: switch current handoff to execution portfolio

## Task 9 — Deterministic contradiction audit

Allowed changed paths are only:
- AGENTS.md
- docs/INDEX.md
- current architecture/process protocols including the new throughput file
- DeepSeek controller profile
- resource-policy-v3
- two current project handoffs
- refined design + alternatives + this plan

Verify:
1. no src, tests, schemas, experiments, prototypes, or scripts path changed;
2. no current governing policy hit for gpt-5.6-luna;
3. no current normative intermediate-certification mandate;
4. no current mandatory per-child Markdown lane-memo contract;
5. all current reading-order paths exist;
6. git diff --check passes;
7. resource-policy-v2.yaml is byte-unchanged from promotion base;
8. no branch deletion, force push, unrelated worktree deletion, or branch-hygiene operation occurred.

If a direct contradiction is found, fix only the responsible current policy file and rerun all Task 9 checks. No review memo.

## Task 10 — Verify candidate and stop before canonical-main mutation

1. Fetch origin/main again. If it advanced, do not merge; reconcile first.
2. Repeat Task 9 path checks.
3. Re-verify the two promoted design blobs.
4. Run one dependency-free invariant check proving:
   - no current gpt-5.6-luna pin;
   - throughput protocol referenced;
   - LUNA/medium current policy exists;
   - Area Lead hierarchy represented;
   - lane policy requires BASE_SHA;
   - remote durability uses execution branch;
   - main sync preserves separate canonical-main authority;
   - resource-v3 encodes explicit owner decision and heavy max 1;
   - final review is deferred.
5. Push only the promotion branch non-force if safe.
6. Return compact handoff:
   PROMOTION_BASE
   PROMOTION_HEAD
   CHANGED_PATHS
   THROUGHPUT_PROTOCOL_CREATED
   RESOURCE_POLICY_V3_CREATED
   RESOURCE_POLICY_V2_MUTATED=NO
   CURRENT_POLICY_CONTRADICTION_CHECK
   PRODUCT_CODE_CHANGED=NO
   BRANCH_CLEANUP_EXECUTED=NO
   CANONICAL_MAIN_MUTATED=NO
   READY_FOR_CANONICAL_MAIN_INTEGRATION

## Canonical-main integration boundary

This plan stops at a verified promotion candidate.

After the exact candidate head is explicitly accepted for canonical-main integration:
1. fetch origin;
2. verify main did not advance;
3. integrate the exact candidate non-destructively, fast-forward when possible;
4. never force push;
5. push canonical main;
6. fetch again and require local/remote main equality;
7. rerun Task 10 invariants against pushed main;
8. confirm no product code or branch cleanup was included.

If main advanced or integration is not mechanically safe, preserve the candidate and reassess.

## Self-review

Spec coverage: execution-first transition, Luna Medium, hierarchy/fallback, rolling frontier/stale-base protection, machine state, Problem Catalog direction, worktree administration, separate root/heavy budgets, semantic convergence inputs, main isolation, fresh-session handoff, historical preservation, and branch-hygiene separation are all mapped.

Placeholder scan: no unresolved placeholder marker or unspecified implementation step remains.

Interface consistency: throughput-first protocol is primary current execution contract; all other current policy surfaces point to it rather than define competing orchestration.

Static failure modes: all five header failure modes are tested in Tasks 9-10.

## Execution handoff

Superpowers requires owner review of this written plan before implementation.

After owner approval, execute Tasks 1-10 on the isolated promotion branch with deterministic verification and no reviewer/certifier swarm. Stop before canonical-main mutation unless the exact verified promotion head is explicitly authorized for integration.
