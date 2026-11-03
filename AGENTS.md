# Workspace Guidance

## 2026-10-03 Remaining-Work Execution Atlas Authority Override

This section is the **current ordinary-development orchestration authority** and supersedes older process wording below where it conflicts. Historical Gate/task evidence remains historical evidence.

Native Codex thread discovery, coordinator messaging, fresh-worker launch, worktree binding, and monitoring are described in the [Codex Native Thread Operations Runbook](docs/architecture/CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md). It is subordinate to this file, governing protocols, exact task authority, and the live tool schemas.

1. Current resource authority is `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`; v4 and earlier policies remain preserved historical process evidence.
2. Current execution design/plan:
   - `docs/superpowers/specs/2026-10-03-remaining-work-execution-atlas-and-parallel-verification-design.md`
   - `docs/superpowers/plans/2026-10-03-remaining-work-execution-atlas-implementation-plan.md`
3. Execution uses concurrent rolling **BUILD / VERIFY / REPAIR** frontiers. Numeric chapter order is navigation, not a synchronization barrier.
4. New H3 execution packets default to fresh top-level Codex sessions and `PARALLEL_PORTFOLIO` execution. Independent READY work must be dispatched concurrently when ownership/resources allow.
   **`FRESH_NATIVE_THREAD_REQUIRED`:** an ordinary independent Portfolio worker/root must be created with a fresh native Codex `create_thread` and a self-contained first-turn packet. A fork copies conversation history and is allowed only for explicitly authorized historical branching; an in-process `spawn_agent` is not a substitute for a Portfolio root. Bind and verify the exact project, isolated worktree, branch and base SHA before any write-capable turn. If the current wrapper cannot bind that worktree/base, stop the write lane and report the observed limitation; do not silently fall back to local/shared checkout, fork, or subagent. This is controller-driven while the Controller is active, not a background scheduler.
   **NATIVE_PARALLEL_DISPATCH_REQUIRED:** At the start of a substantial Codex execution Goal, inspect the current native thread tools and the independent READY H3 frontier. When two or more independently authorized, ownership/resource-compatible H3 roots exist, create their fresh native `create_thread` instances and initiate eligible turns **before waiting for any peer to finish**. `spawn_agent` remains an H4 subagent mechanism, not a native-root substitute; do not use serial `subagent-driven-development` as the default scheduler. New native roots start READ_ONLY: independently verify project, isolated worktree, branch/HEAD/tree, exact base, task grant, exclusive paths and lease before source writes. A designated serialized Worktree Admin may non-destructively bind a named branch inside an already verified clean isolated worktree, followed by full reverification; never fall back to a shared/dirty checkout. On native tool/binding failure, record the exact blocker rather than silently substituting serial workers. Record native thread IDs, actual observed overlap and the disposition of unused eligible capacity. Follow **Native Codex Parallel Dispatch** in `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`. This adds no task or operational authority.
5. Do **not** select stock Superpowers `subagent-driven-development` merely because subagents are used; its mandatory reviewer-after-every-inner-task loop is not the ordinary repository executor. Route independent work through `dispatching-parallel-agents`; behavior changes through TDD; failures through systematic debugging; completion claims through verification-before-completion.
6. Every BUILD_GREEN H3 candidate is queued for feature-level code review on the asynchronous VERIFY frontier before convergence/current-main integration. That review does not block unrelated BUILD unless the DAG declares a true `HARD_VERIFY_DEPENDENCY`.
7. A consumed-contract/path delta may mark running descendants `STALE_IN_FLIGHT`; stale success messages are non-integrable until reconciled against the new exact contract fingerprint.
8. Top-level and child concurrency is adaptive, not capped at four roots or another historical number. Do not invent work to fill slots and do not overlap writers.
9. Heavy-resource concurrency follows v5 lease classes. Ordinary authorized HEAVY_CPU/FFMPEG work starts at lease 2 and may calibrate to 3; failures lower only the affected resource class and do not globally serialize lightweight work.
10. Detailed worker state is file-backed/durable and parent/chat handoffs stay compact.
11. When `.orchestration/remaining-work/CONTROLLER_START_HERE.md` exists, fresh controllers read it before dispatching Remaining Work Atlas packets.
12. The active Remaining Work H0 denominator targets the current authorized local-first engineering + verification finish line; separately authorized protected/archive/provider/production/Gate work is tracked outside that denominator until explicit rebaseline.


1. Read `docs/INDEX.md` before making architecture, specification, or implementation-planning decisions.
   Preserve `Video_Intelligence_Pipeline_Raporu_v1.0.md` as historical design
   evidence; it is not the current approved architecture contract.
2. Treat `docs/audits/ASTRA_ARCHITECTURE_DECISION_PACKAGE.md`,
   `docs/architecture/ASTRA_DECISION_REGISTER.md`,
   `docs/architecture/CANONICAL_CONTRACTS.md`, and
   `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md` as the current architecture
   handoff; treat `docs/implementation-spec-v1.1.md` and
   `docs/audits/GATE0_SPEC_NORMALIZATION_REVIEW.md` as the current approved-for-
   planning Gate-0 implementation specification handoff, subject to the narrowly
   authorized v1.1.1 erratum described below.
3. Read `reference-pack/` before `external/`. Inspect full external repositories
   only for a concrete, recorded question.
4. Use targeted searches and key-file reads; do not recursively ingest or vendor
   external projects, generated assets, datasets, binaries, model weights, or
   history.
5. Preserve provider neutrality. Local, DeepSeek, Gemini, and TwelveLabs are
   capability/benchmark roles to be evaluated at their named gates, not settled
   production dependencies.
6. Evidence classification is assertion-level. Keep the five approved classes
   distinct: `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, and
   `EDITORIAL_INFERENCE`. `NOT_OBSERVED` is an availability/status condition, not
   an evidence class.
7. Never fabricate sub-second or frame-accurate timestamps. Semantic/model,
   technical-window, matched-offset, source-PTS/frame, proxy, timeline, and
   rendered-output coordinates are distinct typed domains. A semantic timestamp
   is not a frame-accurate cut.
8. Preserve source media and never automatically delete, rewrite, canonicalize,
   demote, exclude, or scheduler-skip media because of a duplicate/match result.
9. Never commit API keys, credentials, model weights, large media, caches, or
   vector stores. Keep `.env.local` local and use `.env.example` placeholders.
10. Record source identity/revision, run/attempt identity, artifact provenance,
    model/tool/configuration identity, evidence state, and applicable policy for
    every derived claim that later work materializes.
11. Prefer wrappers/adapters around mature tools to unnecessary rewrites, but
    preserve license/reuse boundaries and do not treat public source as automatic
    reuse permission.
12. Do not treat the v1.0 report's provider models, prices, FPS values, schemas,
    vector-store choices, segmentation settings, or future product stack as
    settled facts.
13. When evidence is absent, write `NOT_OBSERVED` rather than guessing. Current
    public documentation is not runtime validation.
14. The user has explicitly authorized a **narrow Gate-0 Implementation
    Specification v1.1.1 erratum only** to resolve the discovery-authorization /
    policy-decision envelope contradiction and directly dependent schema/ownership
    wording. This authorization permits only the plan-bounded local/synthetic
    T00–T11 implementation, tests, fixtures, schemas, verifier wiring,
    configuration/lockfile, and implementation receipt. It does **not** permit
    real-archive execution, model downloads, provider requests, cloud egress,
    or later gates. Any unrelated architecture change requires a separate
    explicit approval.
15. Do not mutate third-party source in `external/`; curated copies belong in
    `reference-pack/<id>/source/` and must retain original path/revision
    provenance.
16. Treat `prototypes/google-video-analyzer/` as a preserved snapshot. Do not
    refactor it into Gate 0 or reuse its browser-key/provider coupling.
17. Gate 0 must remain local-only and minimal: no cloud fallback, ASR, VDF
    execution, vector service, Drive materializer, durable scheduler, custom UI,
    edit/export/render pipeline, AI QC, MCP/agent product orchestration, or full-
    archive indexing unless the approved contract is explicitly revised in a new
    gate. Repository process orchestration for Codex/subagents is governed
    separately by `docs/architecture/SUBAGENT_LANE_PROTOCOL.md` and does not
    authorize product/runtime orchestration.
18. Verify important claims with actual commands or primary current documentation
    as appropriate. Do not label unobserved state as `VERIFIED`.
19. Keep the workspace compact enough for limited-duration review. Prefer omission
    with an explicit note over indiscriminate copying.
20. Before a push, run the workspace verifier and secret audit; never use
    force-push to make the repository fit a plan.
21. Repository-wide executor/model policy is **executor-specific** and current orchestration is governed by `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`. For **Codex**, request model family `LUNA` with reasoning `medium`; at Goal start resolve one currently supported concrete Luna model, freeze that resolution for the Goal, set model and reasoning explicitly on eligible child spawns, and verify effective values when supported. Do not silently switch Luna generations inside a Goal or fall back to another family. For **DeepSeek Harness**, retain the currently verified DeepSeek parent/child reasoning policy in the current controller profile until the owner explicitly changes it. Historical records naming older concrete models remain historical provenance.
22. For substantial multi-agent work, follow
    `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`. The main agent is the sole
    canonical integrator. Every child uses an isolated branch/worktree lane and
    never writes directly to `main`.
23. Every spawned child receives an explicit run/lane identity, exact base SHA,
    task, model/reasoning, read scope, and write mode. Review lanes write only
    their unique lane memo/supporting artifacts; candidate-write lanes may edit
    only an exclusive path set assigned by the main agent. Concurrent child
    writers may not own the same path.
24. Persist only the durable execution state needed for recovery/integration. Code/tests live in commits; scheduler state and Problem records use compact machine-readable artifacts as governed by the throughput and lane protocols. Do not require a narrative Markdown memo from every child and do not use chat as the only durable record.
25. Child-to-parent handoffs are compact pointers containing exact base/head SHAs, changed paths, contract/shared-surface deltas, test entrypoints, open Problem IDs, blocker state, and a durable state path. Do not paste full diffs, long logs, or complete child analysis into the parent context.
26. Child completion is not acceptance. The parent verifies the referenced commit/state, checks stale-base and ownership conditions, then records an explicit disposition before integration.
27. After durable handoff/disposition, explicitly close/terminate the child when supported. If explicit closure is unavailable, mark it terminal/inactive and never reuse it for new work.
28. Child worktrees/branches may be removed only after required state is durable and the candidate is dispositioned. Milestone execution branches, not canonical main, are the ordinary remote durability surface during execution Goals; canonical-main integration requires separate explicit owner authority.
29. Preferred delegation depth is `Root Orchestrator -> Area Lead -> Worker` when the runtime positively supports compliant nested delegation. Workers do not spawn another generation by default. If nested delegation is unavailable or unverifiable, flatten to `Root -> Workers` rather than blocking the Goal.
30. Treat the repository as durable memory across context compaction or fresh
    sessions. Recover orchestrated work from `AGENTS.md`, the governing issue,
    `docs/agent-runs/` ledger/memos, git SHAs, and current contracts rather than
    asking completed children to restate their full work.
31. Every repo-working **main-agent** turn follows
    `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`. Synchronize the canonical
    local `main` and `origin/main` at both turn boundaries: before substantive
    work/spawning children and again before the main agent sends its final
    response.
32. Start-of-turn synchronization is non-destructive: inspect branch/status,
    preserve pre-existing tracked/untracked state, `git fetch --prune origin`,
    compare ancestry, and fast-forward only when safe. Do not auto-stash, hard
    reset, clean, force-push, or silently merge/rebase divergence. No child may be
    spawned until the exact synchronized base SHA or an explicit sync blocker is
    recorded.
33. Before any execution-branch push, fetch again to detect remote advancement, run required verifier/secret/task checks, commit only authorized Goal work, and require a fast-forward-safe non-force push.
34. A read-only repo turn performs final fetch/compare and creates no artificial commit. Never auto-add/delete unknown filesystem state merely to make trees look identical.
35. A repo-working Goal reports execution-branch synchronization separately from canonical-main observation. Do not claim push/sync success from stale evidence.
36. Accepted child work becomes remotely durable through the owning milestone execution branch when authorized; ordinary execution does not require canonical-main integration.
37. **Execution-first parallel orchestration is the repository default.** Partition genuinely independent READY work and dispatch as much useful dependency-safe capacity as the harness, ownership graph, and resource policy safely allow.
38. Concurrency is adaptive, not a quota. Do not leave useful READY work idle, but never manufacture duplicate tasks or overlapping writers merely to occupy slots.
39. Use continuous rolling-frontier scheduling: child finishes -> verify scheduler/integration facts -> disposition/integrate safely -> close -> unlock dependencies -> refill capacity immediately.
40. Ordinary development does **not** use reviewer/certifier swarms or repeated review-remediation-certification loops. BUILD / ENABLE / REPAIR consume normal execution capacity; formal review/certification is deferred to a later owner-directed epoch.
41. Unexpected failures enter systematic-debugging and bounded remediation. Default maximum is three evidence-supported failed repair generations for the same load-bearing Problem/root-cause family; after exhaustion, preserve the Problem, park affected descendants, and continue independent READY work.
42. Before completion claims, use deterministic/static/test verification appropriate to the milestone. Verification is not certification.
43. Mechanically detectable issues such as undefined symbols, duplicate owners, invalid references, schema/artifact inconsistencies, stale bases, and path/contract ownership conflicts should be checked before spending additional agent capacity.

51. For milestone Goals, follow the bounded autonomous failure-remediation loop
    in `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`:
    preserve failure evidence, investigate root cause before fixes, use TDD for
    behavior changes, keep attempts digest-bound and file-backed, and retry
    within standing authority until a hard boundary or bounded exhaustion.
    Three confirmed failed generations in one load-bearing area require
    architecture reconsideration; do not guess a fourth fix.

44. **OWNER-APPROVED REMOTE DURABILITY + TORRENT ORCHESTRATION (2026-09-21).**
    Follow `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`
    for substantial Codex/DeepSeek Goals. User-facing Goals are milestone-sized;
    internal tasks, reviews, fixes, and child completions are not owner-return
    boundaries.
45. Every repo-working Goal synchronizes both canonical `main` and the active
    execution branch at start and end. Safe authorized local-only execution
    commits from a prior run must be pushed before new substantive work. After
    coherent integration batches, checkpoint the execution branch to origin.
    Before final response, require local execution HEAD == its remote HEAD unless
    synchronization itself is the blocker. A BLOCKED milestone still pushes safe
    integrated work. Never auto-merge canonical `main`.
46. Do not indiscriminately upload dirty filesystem state. Authorized source,
    tests, fixtures, plans, and compact ledgers may be committed/pushed after
    attribution and secret checks. Generated media/build outputs/caches/venvs,
    unrelated scratch, credentials, secrets, and sensitive artifacts are not
    promoted merely for remote symmetry.
47. For broad milestones, the main orchestrator first decomposes the work into
    roughly 20–40 candidate shards when the work genuinely supports it, then runs
    the highest safe dependency-aware concurrency. Target roughly 12–24 useful
    active children when available and 24–40 only when ownership boundaries,
    machine/runtime capacity, and dependencies make that safe. Never manufacture
    duplicate or overlapping work to fill slots.
48. The main agent is primarily scheduler, dispatcher, dependency/frontier
    manager, adjudicator, integrator, remote-checkpoint owner, and verifier.
    Substantive coding, focused analysis, fixture creation, adversarial checks,
    regressions, and review should be delegated whenever a clean ownership
    boundary exists. Do not leave ready frontier capacity idle while the main
    performs delegable substantive work.
49. Use a continuous rolling frontier: as soon as a child terminates, verify it,
    integrate/adjudicate it, unlock dependent nodes, and immediately refill safe
    capacity. Do not wait for an artificial whole-wave barrier.
50. Child details remain file-backed; code/tests live in commits; parent handoffs
    stay compact. A terminal child leaves the active schedule immediately and is
    closed when supported, otherwise marked `TERMINAL_INACTIVE` and never
    reused. Per-child remote branches remain unnecessary by default; accepted
    work becomes remotely visible through frequent execution-branch checkpoints.

52. **Routine development prerequisite recovery is ordinary ENABLE work.** Follow `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`. A missing NumPy/pytest/Pillow/equivalent routine development or test prerequisite is not an owner-level blocker by default.
53. A child blocked by a routine prerequisite preserves the exact command/error/runtime/environment/missing prerequisite and returns it to its root. The root owns environment continuity and must attempt the current v5 recovery ladder before parking the task.
54. Reuse the current Goal environment, known project environments, and compatible installed/cached dependencies first. Shared project-environment mutation requires serialized `ENV_ADMIN` ownership; ordinary workers do not concurrently mutate a shared environment.
55. Goal-local project/user-scoped environments may be created or repaired automatically. Public package-registry/CDN network access needed solely for routine development dependency retrieval is authorized under v5; record package/tool, resolved version where observable, package manager, environment, install/sync command, and network use.
56. Routine prerequisite authority does not authorize `sudo`, Homebrew/apt/yum or equivalent system-wide mutation, provider/model API calls, model/checkpoint/weights downloads, protected/archive-media retrieval, credentials/private registries, unrelated network activity, destructive Git, production render/export, or Gate promotion. Installing an SDK does not authorize using its service.
57. An environment/import/collection/missing-tool failure is not behavioral TDD RED. Repair the environment and rerun the pre-implementation test. If implementation already happened, test-efficacy recovery may prove RED on pre-implementation code and GREEN on implementation code, but historical chronological RED remains `NOT_OBSERVED`.
58. Explicit narrower Gate/task/spec/plan authority overrides the general prerequisite-recovery policy. In particular, Gate-0 Revision-18 retains its frozen no-install/no-download restrictions unless separately amended.
59. **DEVELOPMENT SOURCE-AUTHORIZATION ENFORCEMENT IS DISABLED BY OWNER DECISION (2026-10-24).** Per `docs/decisions/ADR-0003-development-source-authorization-enforcement-removed.md`, `scripts/verify-workspace.sh` reports `DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER` and contributes no failure for missing canonical-admin refs, branch/path-bound grants, or Owner Witness records during ordinary development. Do not fabricate `AUTHORIZED_CURRENT`, `PASS`, a grant, or an Owner Witness; report the control as DISABLED. Do not reintroduce equivalent administrative blockers under another name. This removal is limited to development authorization enforcement: protections for immutable source media, source-native PTS/timebase correctness, evidence integrity, credentials/secrets, real provider/model execution, protected/archive access, production Owner trust activation, and canonical-main merge authorization remain in force.
