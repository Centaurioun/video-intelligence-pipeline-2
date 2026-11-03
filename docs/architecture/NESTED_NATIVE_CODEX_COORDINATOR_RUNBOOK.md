# Nested Native Codex Coordinators: Hierarchical Parallel Execution Runbook

> **Document type:** Reusable engineering runbook and recorded capability pattern  
> **Edition:** 1.0 — 2026-10-22  
> **Status:** Documentary guidance / example; **no task, source-writing, publication, or production authority is created by this file**  
> **Primary case study:** Video Intelligence Pipeline (VIP), Coordinator #9 → Gate Coordinators #10/#11/#12 → independently created native workers  
> **Scope:** Codex App native threads, nested delegation, Git worktree isolation, ownership, communication, scheduling, failure handling, and project portability  
> **Related governing documents:** [Native Thread Operations Runbook](CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md), [Subagent Lane Protocol](SUBAGENT_LANE_PROTOCOL.md), [Throughput-First Development Protocol](THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md), [Remote Durability and Torrent Orchestration Protocol](REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md), [Main-Agent Synchronization Protocol](MAIN_AGENT_SYNC_PROTOCOL.md), [Resource Policy v5](../portfolio/portfolio-v1/resource-policy-v5.yaml), [DeepSeek Harness Controller Profile](../portfolio/portfolio-v1/DEEPSEEK_HARNESS_CONTROLLER_PROFILE.md), and [AGENTS.md](../../AGENTS.md)

**Ownership boundary:** the [Subagent Lane Protocol](SUBAGENT_LANE_PROTOCOL.md) is the normative owner of child isolation, write-scope, BASE_SHA/stale-base acceptance, and child lifecycle/closure rules. This runbook **illustrates** those rules for a nested native Codex hierarchy; where the two differ, the lane protocol and the exact task authority govern. Nothing here restates them as a competing authority.

## 1. Purpose and evidence discipline

This document explains **how one Codex coordinator creates subordinate native Codex coordinators, which in turn create their own native worker threads**, and how those workers communicate, run concurrently, remain isolated, and return attributable results. It is intended to be adapted in other repositories.

The VIP read-only pilot reported on **2026-10-22** successfully exercised the hierarchy with three Gate leads and one worker per lead. The pilot report was supplied by the Owner from the Codex session; the **individual transient tool invocations, runtime metadata, precise worktree paths, and process overlap are not independently reproducible from the GitHub tree**. Treat the pilot-specific facts below as **CODEX/OWNER-REPORTED**, not as an independently GitHub-certified historical receipt. The governing runbook and resource-policy files are independently readable repository contracts.

This distinction matters:

- **Reported in the pilot:** each Gate lead issued its *own* native `create_thread` request; each request initially returned a pending client identifier; later thread inventory resolved the native worker; three worker tasks completed; their results traveled worker → Gate lead → H0.
- **Reported in the pilot:** six distinct, clean managed worktrees, detached at the same canonical commit; the three leads and, later, the three workers overlapped in execution.
- **Not established by this pilot:** safe nested **source-writing**, normal branch publication, live administrative writer lease release, enduring background scheduling, model execution, Gate acceptance, or real-media workflow.
- **Not portable as fixed API:** the exact tool signatures, project IDs, native IDs, supported model names, client-ID resolution behavior, or account permissions. Re-discover these at each new Goal.

The reliable principle is not “a title named Coordinator can delegate.” It is **a subordinate native thread with a positively verified tool surface can issue its own fresh native thread-creation call, then manage attributable results within an explicit hierarchy and authority boundary**.

## 2. Concepts and roles

| Term | Meaning | May do | Must not infer |
|---|---|---|---|
| **H0 / Portfolio Coordinator** | Single accountable root for the project or one governed portfolio | Own global dependency graph, admission, path and resource allocations, cross-area contracts, controlled integration | A new coordinator is a new H0 |
| **Gate/Area Lead (H1)** | Subordinate coordinator, e.g. Gate 1 | Decompose its assigned milestone, create eligible native workers when supported, verify them, report to H0 | Gate directory ownership implies write authority |
| **Native Worker (H3 execution root)** | Fresh native Codex thread with one self-contained packet | Work only within exact assigned rights; return Git/test evidence | Thread creation means valid branch/authority |
| **H4 subagent** | In-process child agent inside an already owned bounded task | Assist with a permitted subtask | Substitute for mandatory fresh native H3 worker |
| **Native thread ID** | Actual identifier accepted by read/message/wait operations | Address a verified thread | Pending client key equals thread ID |
| **Pending `clientThreadId` (client key)** | Provisional creation result returned in the actual runtime field `clientThreadId`; it is a *client-side creation key*, not a thread identity | Track/resume only through a compatible resolver or independently attributable inventory | Worker definitely exists or is ready; **never** treat it as a native thread ID |
| **Worktree** | Git-linked separate working directory | Isolate filesystem edits and branch context | Exclusive logical ownership or source authorization |
| **Execution branch** | Non-main Git branch for attributable candidate work | Retain verified commits/receipts | Permission to merge main or promote a Gate |
| **Resource lease** | Portfolio-wide allocation for CPU, FFmpeg, environment, etc. | Bound expensive parallel operations | Every coordinator has its own full quota |
| **Task grant** | Exact user/governed authority for operations and paths | Authorize only its stated scope | An orchestration directive authorizes all code under a Gate |

Here and elsewhere, **Mode A** means the Area Lead itself invokes native `create_thread`. **Mode B** means H0 acts as the native creation broker for an Area Lead that cannot safely create threads. Mode B retains the Area Lead's technical responsibility but must not be misreported as Mode A.

### Why nested native threads instead of one huge thread?

- Separate native contexts reduce cross-task transcript pollution.
- Separate worktrees prevent ordinary filesystem write collisions.
- Exclusive *logical* path ownership prevents two branches from independently changing the same contract without coordination.
- Multiple teams can progress while a separate area is blocked.
- A finished worker returns a short, auditable milestone instead of making H0 ingest its full transcript.
- One H0 retains cross-team authority, machine resources and integration ordering.

It does **not** automatically make blocked tasks READY, reduce every task's runtime, or guarantee that twenty concurrent expensive tests will finish faster.

## 3. Architecture

~~~mermaid
flowchart TD
  O[Owner: communicates only with H0]
  H0["H0: Coordinator #9 / portfolio control plane"]
  G0[Gate 0 worker pool]
  G1["Gate 1 Lead: #10"]
  G2["Gate 2 Lead: #11"]
  G3["Gate 3 Lead: #12"]
  W1[Gate 1 worker worktree]
  W2[Gate 2 worker worktree]
  W3[Gate 3 worker worktree]
  A[Serialized Worktree/Admin service]
  R[Global resource and ownership registry]
  I[Single controlled non-main integration owner]
  O --> H0
  H0 --> G0
  H0 --> G1
  H0 --> G2
  H0 --> G3
  G1 --> W1
  G2 --> W2
  G3 --> W3
  H0 --- A
  H0 --- R
  H0 --> I
~~~

Arrows show **control and reporting relationships**, not blanket write access or automated merges. Gate leads may own many successive workers; only eligible concurrent workers actually run.

**Recommended invariants:**

1. Exactly **one accountable H0** within the same portfolio.
2. Area leads own disjoint milestone responsibilities.
3. At most **one active writer per owned source path and shared contract surface**, and one active writer per worktree and branch **unless** the executor positively supports root-owned shared-worktree exclusive-path isolation (see [Subagent Lane Protocol](SUBAGENT_LANE_PROTOCOL.md) §6); Git worktree separation alone is not sufficient.
4. Only one serialized administrator creates/binds shared worktree topology or mutates administrative authority.
5. Only one controlled non-main integration owner for shared candidate convergence.
6. A worker's write manifest, branch, base and contract fingerprints are fixed before its first write turn.
7. Gate-local review cannot silently amend a shared API, source evidence class, PTS/timebase model, schema or administrative trust root.
8. Subordinate coordination cannot elevate the authority received from H0 and the Owner.

## 4. VIP 2026-10-22 pilot: reported historical example

**Reported pilot Goal:** `READ_ONLY_HIERARCHICAL_PILOT`. **Reported outcome:** all three Gates passed **Mode A**. Coordinator #9 was already an existing native controller; its actual native ID was not supplied in the pilot report and must not be guessed.

| Lead | Gate | Lead native ID | Worker native ID | Reported result |
|---|---|---|---|---|
| Coordinator #10 | Gate 1 | `01a1641c-6089-7d22-bbc4-3edf26182420` | `01a1641c-e928-7b31-8eac-bc98b9855209` | Confirmed two-arm synthetic harness vs separately documented three-arm protocol |
| Coordinator #11 | Gate 2 | `01a1641c-6082-7781-96be-3f500a5129ca` | `01a1641c-da98-75a2-b809-f992afa0a39a` | Distinguished two-path GAP-C code repair from ten-path D6 registration |
| Coordinator #12 | Gate 3 | `01a1641c-60a4-7a51-9972-944c3f0163f8` | `01a1641d-0754-7650-8c36-96cffbd7ffb7` | Located source-native temporal refinement and the PR #121 integration seam |

The pilot report stated that all six threads had **different managed project worktrees**, all clean and detached at:

- `HEAD: 17edacbe64983ae284f09a8386377200bf538ec3`
- `Tree: 2f44c4da3bb7b5fa68d1760d1a01d20988690417`

Their **individual worktree filesystem paths were not included in the pilot handoff**. Do not reconstruct them from the thread IDs.

### What the pilot report claims the pilot demonstrated

> **CODEX/OWNER-REPORTED.** The ten items below are the *claims of the Owner-relayed pilot report*, not independently verified runtime findings. No raw tool-call trace, per-turn packet log, or token/time receipt for this pilot was found in the repository. Read them as a historical claim set to be re-tested, not as a certification of the capability.

1. H0 could launch three subordinate native Gate leads.
2. Each lead could discover/use its own native thread tools.
3. Each lead submitted one `create_thread` for its own worker.
4. A pending client identifier did not prevent later native identity verification through observed inventory, with appropriate correlation.
5. The three worker worktrees were separate and clean.
6. Each worker did meaningful bounded read-only work.
7. Each lead retrieved and independently checked its worker handoff.
8. Each lead relayed a summary to H0 and acknowledged an H0 follow-up.
9. The reported live inventory showed workers overlapping — **report-only**: the durable closeout inventory records `actual_concurrency` as `NOT_OBSERVED`.
10. No source edits, commits, remote pushes, PR changes, models or protected-media operations occurred — **report-only**: the report asserts non-occurrence, but no in-repo receipt of that non-occurrence exists.

**Special incident:** the Gate-2 worker initially treated an otherwise permitted read-only binding as too strict; the same worker was resumed after identity and isolation verification. No duplicate replacement worker was created. This is an example of **recover in place after proving the original worker identity**, not “retry any failed creation.”

**Cost as reported, not a universal benchmark:** approximately **104,350 tokens / 3 minutes 36 seconds**. This figure comes from the Owner-relayed report only; there is **no in-repo token/time receipt** for it, and the durable closeout inventory carries `tokens_time_utilization: NOT_OBSERVED`. A future project should target a much smaller and more economical pilot when the same capability is already supported by established evidence.

## 5. Preparation before creating any worker

### 5.1 Read project authority

For VIP, the relevant starting documents are:

- `AGENTS.md` — item 21 model/reasoning policy, item 29 delegation depth and flatten rule, items 26–28 acceptance and closure.
- `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`
- `docs/architecture/CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md`
- `docs/architecture/SUBAGENT_LANE_PROTOCOL.md` — normative isolation, write-scope, BASE_SHA/stale-base (§11) and child lifecycle (§13) rules; this runbook illustrates them.
- `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`
- `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`
- `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`
- `docs/portfolio/portfolio-v1/DEEPSEEK_HARNESS_CONTROLLER_PROFILE.md` — the DeepSeek executor's model/reasoning policy when the executor is not Codex.
- Current project handoffs, Gate specs, exact approved implementation plans, task packets and authority receipts.

For another project, substitute its own governing contracts. This file is a **portable operating pattern**, not a license to bypass them.

### 5.2 Establish a frozen task envelope

Before requesting a worker, record:

| Field | Required content |
|---|---|
| Portfolio / Goal / lane | Stable identifiers; do not create duplicate H0s |
| Root / lead / intended reviewer | Exact accountable native identities, or pending state |
| Repository/project | Verified remote, saved Codex project ID, expected Git common directory |
| Base | Immutable commit SHA and tree SHA |
| Worktree/branch | Intended unique isolated directory and non-main ref; actual binding checked after launch |
| Task | One outcome; dependencies and stop conditions |
| Scope | Exact permitted reads, writes and prohibited operations |
| Authority | Current Owner/grant ID, expiry and allowed publication |
| Contracts | Accepted consumed interfaces, blobs and compatibility constraints |
| Resource | Global lease class, owner and acquisition policy |
| Completion | Tests, independent review, evidence, commit and final handoff |
| Idempotency | Unique run/lane creation key and ambiguity policy |
| Model / reasoning (`model_reasoning`) | Requested model **family** + the **frozen concrete model resolved for this Goal** + the **reasoning level**. Executor-specific: for Codex, family `LUNA`, one concrete currently supported Luna model resolved and frozen at Goal start, reasoning `medium` (`AGENTS.md` item 21); for DeepSeek Harness, the policy in `DEEPSEEK_HARNESS_CONTROLLER_PROFILE.md`. Record the *requested* values and, where the runtime exposes them, the *effective* values; never hard-code one environment's model names into a portable packet. |
| Durable state (`durable_state_path`) | The repository-relative or absolute path to the child's file-backed execution state / handoff record, so the handoff survives context loss and does not live only in chat. |

**Avoid generic task packets such as “finish Gate 1.”** A Gate lead can receive a broad *milestone Goal*, but each source-writing worker needs a narrow manifest and measurable acceptance predicates.

### 5.3 Global scheduler admits READY tasks

For each proposed task classify:

- **READY**: dependencies accepted, task grant positive, source ownership free, base/contract current, resources available.
- **PENDING**: legitimate non-authority prep remains.
- **BLOCKED_AUTHORITY**: missing exact approval or source admission.
- **BLOCKED_DEPENDENCY**: upstream accepted evidence not available.
- **BLOCKED_TECHNICAL**: actual failure requiring systematic debugging.
- **NOT_OBSERVED**: cannot establish an indispensable fact.

Only READY tasks receive write-capable workers. Read-only diagnostics can run under their own narrowly allowed scope; **do not fabricate tasks to fill slots**.

## 6. Discover live tools and native thread creation

The tool surface is **session-dependent**. The names below match documented VIP practice, but they are not a permanent cross-product API guarantee.

| Operation | Historical name | Purpose |
|---|---|---|
| Project discovery | `list_projects` | Resolve target Codex project |
| Existing thread inventory | `list_threads` | Identify native IDs, host, status and available project/CWD |
| Fresh thread request | `create_thread` | Request one native thread with first-turn packet |
| Thread details | `read_thread` | Inspect turns, observations and final result |
| Inter-thread message | `send_message_to_thread` | Deliver a targeted prompt/handoff |
| Multiple-thread progress | `wait_threads` | Monitor known native threads with bounded waits |
| Worktree operation status | `get_worktree_creation_status` | Resolve only an actual worktree operation ID |

**Important:** `get_worktree_creation_status` must **not** be used to resolve a pending `create_thread` client key. These are different identity domains.

### 6.1 Schema-illustrative lead creation

The following is **illustrative**, adapted from the existing native runbook. Validate every field against the live `create_thread` schema. This is not a claim that this exact payload was captured during the pilot.

~~~json
{
  "target": {
    "type": "project",
    "projectId": "<resolved-project-id>",
    "environment": {
      "type": "worktree",
      "startingState": {
        "type": "branch",
        "branchName": "<already-verified-immutable-source-ref>",
        "onMissing": "error"
      }
    }
  },
  "prompt": "<complete-read-only-lead-first-turn-packet>"
}
~~~

A branch selector does **not** guarantee that a worktree will arrive on that branch; some observed worktree launches arrive at **detached HEAD**. Detached HEAD can be acceptable for a read-only inspection. An authorized new writer must receive a unique branch through a serialized Worktree Admin and must reverify the binding before writing.

Do not copy unknown top-level parameters (such as project ID, environment type, model, thinking) from historical examples. Check the live schema.

### 6.2 The pending-client-ID lifecycle

~~~text
H0 / Gate lead
  |
  | create_thread(self-contained packet)
  v
PENDING clientThreadId  -- client key, NOT a native thread ID
  |
  | compatible resolver, or attributable inventory + read verification
  v
NATIVE THREAD ID
  |
  | read_thread / list_threads / binding check
  v
VERIFIED native project + isolated worktree
  |
  | positive grants + Worktree Admin branch binding (write tasks only)
  v
READY to receive a bounded authorized turn
~~~

Throughout this runbook the "pending client key" is the value the runtime returns in its **`clientThreadId`** response field on a `create_thread` request. It is a client-side correlation key, not a native thread identity; see `CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md` §4 for the concrete field and its denial behavior. Do not rename it to "thread ID" in packets, logs, or handoffs.

The 2026-10-22 pilot **reported** pending client keys followed by native IDs resolved through `list_threads`. That observation does not prove a universal one-to-one mapping algorithm.

**Safe correlation requires more than a similar title.** Check as much as exposed:

1. Unique creation run/lane key and creation request record.
2. Project and host identity.
3. Newly observed native ID and first-turn packet/task key.
4. Timestamp/order and nonduplication in current thread inventory.
5. Successful targeted `read_thread` of that ID.
6. Actual worktree/repository binding.

If multiple candidates remain plausible, classify **AMBIGUOUS** and **do not create another worker blindly**. A pending key is never passed as a native thread ID to message/read/wait calls.

### 6.3 Mode A: lead creates its own worker

Once the Gate lead's own native project/tool access is verified, it:

1. Receives a bounded delegated Goal from H0.
2. Determines the Gate-local READY frontier within global ownership allocations.
3. Discovers the live `create_thread` schema in **its own session**.
4. Issues a fresh native creation call with the complete worker packet.
5. Resolves pending/native IDs without guessing.
6. Checks that the worker is actually in the intended isolated project worktree.
7. Requests worktree branch binding, if needed, through the single authorized Worktree Admin.
8. Sends a write-capable execution turn **only after** all source grants, leases and contracts pass.
9. Monitors and independently verifies result evidence.
10. Sends one compact terminal milestone to H0.

A lead **cannot** confer permission to its worker by copying the parent's task text. The grant must name the task and scope positively.

### 6.4 Mode B: H0 creation broker

If the Gate lead lacks a trustworthy native creation capability:

1. Gate lead writes a self-contained worker packet (no source edits).
2. H0 checks task admission and globally exclusive scope.
3. H0 issues `create_thread` and resolves the native identity.
4. H0 sends verified identity and worktree evidence to the Gate lead.
5. H0 or Gate lead relays job turns/results as permitted by actual messaging tools.
6. Gate lead remains technical owner of its Gate's accepted milestone.
7. Report **MODE_B**; do not falsely claim the lead made the creation call.

Do not use `fork_thread` or a local `spawn_agent` as a silent replacement for a required fresh native Portfolio worker. H4 helpers can still be used inside their own, independently authorized bounded work when the repository allows it.

### 6.5 Executor and capability boundary

Modes A and B describe the **Codex App native-thread surface**. They are **not** evidence that DeepSeek Harness or any other executor exposes native thread tools, pending `clientThreadId` keys, or native thread IDs. A different executor may expose only controller/task-based children (for example durable named teammates, a shared task board, or in-process subagents), in which case native `create_thread` / `read_thread` / `send_message_to_thread` discipline is simply **not applicable** and must not be simulated or reported as if observed.

When compliant nested delegation is **unavailable or unverifiable** in the active executor:

- flatten to `Root Orchestrator → Workers` per `AGENTS.md` item 29, [Subagent Lane Protocol](SUBAGENT_LANE_PROTOCOL.md) §0, and `resource-policy-v5.yaml` (`flatten_when_nested_delegation_unavailable`);
- report `MODE_B` (if an approved broker was genuinely used) or the **actual blocker** — never an implied Mode A;
- do **not** retain an unsupported Area-Lead role as a normative requirement; the Area-Lead layer is an optimization conditional on positively verified nesting, not a compliance obligation.

This boundary changes no authority: it narrows what a reader may infer. A runbook describing nested native threads is a description of one executor's realized pattern, not a repository-wide capability claim.

## 7. Sending and receiving messages

A native thread's existence does not establish that another thread can communicate with it. Verify both delivery and recipient acknowledgement.

### 7.1 Schema-illustrative direct message

The following shape is historically documented for a successful coordinator-to-coordinator message, but the current live schema must still be checked:

~~~json
{
  "threadId": "<verified-native-recipient-thread-id>",
  "hostId": "local",
  "prompt": "You are Gate 1 Lead. Run the bounded, read-only task defined in <packet>. Return TASK_ID, native ID, worktree, Git SHA, findings, limits and status to H0. This message grants no additional write authority."
}
~~~

Only verified native IDs should be used. A returned “message sent” or accepted tool invocation proves **delivery at most**, not execution, acknowledgement, or completion.

### 7.2 Recommended worker completion envelope

This is a **proposed portable handoff schema**, not an existing GitHub or Codex tool schema:

~~~json
{
  "schema_version": "native-worker-handoff.example.v1",
  "portfolio_id": "example-portfolio",
  "goal_id": "example-gate1-synthetic-compat",
  "lane_id": "gate1-harness-check",
  "status": "COMPLETED_VERIFIED",
  "native_thread_id": "<actual-native-id>",
  "lead_thread_id": "<actual-lead-id>",
  "host_id": "local",
  "worktree": "<verified-absolute-worktree>",
  "branch": "<actual-branch-or-detached>",
  "base_sha": "<40-char-git-sha>",
  "head_sha": "<40-char-git-sha>",
  "tree_sha": "<40-char-git-sha>",
  "changed_paths": [],
  "tests": [
    {
      "command": "<exact-command-or-NOT_RUN>",
      "exit_code": null,
      "disposition": "NOT_RUN_READ_ONLY_PILOT"
    }
  ],
  "review": "NOT_APPLICABLE_READ_ONLY",
  "shared_contract_delta": [],
  "source_authority": "READ_ONLY_ONLY",
  "publication": "NOT_REQUESTED",
  "blockers": [],
  "next_ready_tasks": []
}
~~~

Adapt field names to existing portfolio registries rather than introducing a parallel authoritative schema without approval.

### 7.3 End-to-end reporting sequence

~~~mermaid
sequenceDiagram
  participant O as Owner
  participant H as H0 Coordinator
  participant L as Gate Lead
  participant W as Native Worker
  participant G as Git/Workspace Admin
  O->>H: One Portfolio Goal
  H->>L: Delegated Gate Goal / constraints
  L->>L: Verify tool and task admission
  L->>W: create_thread with read-only first turn
  W-->>L: Pending creation response
  L->>W: Resolve native ID and then verify binding
  opt Task is write-authorized
    L->>G: Request exclusive branch/path/resource
    G-->>L: Verified binding and lease
    L->>W: Scoped write-capable task turn
  end
  W-->>L: Evidence, tests, candidate/blocked
  L->>L: Independently verify claims
  L-->>H: Compact milestone handoff
  H->>H: Cross-Gate/authority/integration checks
  H-->>O: One consolidated decision/progress report
~~~

Each arrow is a **logical operation**. In some runtimes the parent obtains child results by `read_thread` and `wait_threads` rather than by a child actively sending a message. Do not invent automatic push callbacks.

### 7.4 Acknowledgement protocol

A useful simple contract:

- **REQUESTED** — exact sender/recipient/task/message identity recorded.
- **DELIVERED** — host message action returned success.
- **ACKNOWLEDGED** — target's actual new turn visibly responds to this request.
- **RUNNING** — bounded task execution is observed.
- **TERMINAL** — response completes with evidence and status.
- **ACCEPTED_BY_PARENT** — parent independently verifies the evidence and decides acceptance.

Do **not** collapse DELIVERED → ACKNOWLEDGED → ACCEPTED.

## 8. Safe Git/worktree isolation

A worker must check the **actual working directory**, not the worktree path requested by a coordinator.

For a local Git worktree, useful inspection commands include:

~~~sh
pwd
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git rev-parse HEAD
git rev-parse HEAD^{tree}
git branch --show-current
git status --porcelain=v1
git worktree list --porcelain
~~~

These are inspection commands. They do not prove logical source ownership. Check task packets, active writer leases and the source-authorization mechanism separately.

For the VIP pilot, clean **detached** worktrees were acceptable because all tasks were read-only. For code writing:

1. Confirm current branch/HEAD/tree/base and expected common Git directory.
2. Confirm worktree is not the dirty primary checkout or another worker's worktree.
3. Have the serialized Worktree Admin bind an approved **unique non-main branch** if necessary.
4. Recheck actual binding and cleanliness.
5. Confirm exact source and test paths and current administrative permission.
6. Confirm no sibling owns those same paths or shared contracts.
7. Acquire the global resource lease if needed.
8. Only then start TDD and source edits.
9. Verify commit, tree, changed paths, tests and review before non-force checkpoint publication.
10. Integrate only through the assigned controlled **non-main** owner; canonical main needs separate approval.

**Crucial boundary:** a branch-exact source-authority resolver may allow two distinct grants for the same path on different branches while not proving that the earlier writer is now terminal. Current source admission and **live writer quiescence** are separate predicates. Never infer owner release merely from absence of a process, an idle UI tile or old committed evidence.

## 9. Rolling-frontier scheduling and concurrency

The goal is **useful parallel progress**, not maximized thread count.

Maintain three independent frontiers:

- **BUILD:** accepted design + exact grant → source/fixture/test implementation.
- **VERIFY:** candidate-bound tests, adversarial cases and feature-level review.
- **REPAIR:** systematic debugging of observed defects, with bounded scope.

Recommended dispatch logic (conceptual pseudocode, **not an actual tool implementation**):

~~~text
while active_controller_goal:
    refresh_observed_terminal_events()
    for result in completed_workers:
        independently_check_identity_paths_tests_reviews(result)
        disposition_and_release_only_its_verified_leases(result)
    ready = dependency_graph.tasks_with_positive_grants_and_free_owners()
    capacity = global_resources.available_by_class()
    for task in ready_that_fit(capacity):
        create_fresh_native_worker_if_not_already_created(task)
        verify_project_worktree_branch_contract_and_lease(task)
        start_task_without_waiting_for_peer_completion(task)
    if not running_and_no_more_authorized_ready_tasks:
        close_with_attributed_blockers()
        break
    wait_on_known_native_threads_with_bounded_waits()
~~~

**Coordinator lifecycle limit:** a live controller can refill while it remains active, but this is **not a verified persistent scheduler after its turn/session ends**. Do not promise indefinite background work.

### 9.1 Global resource arbitration

These are **repository-wide under the current v5 resource policy**, not coordinator-local:

| Class | Initial concurrent leases | Constraints |
|---|---|---|
| LIGHTWEIGHT_CPU_TEST | Adaptive | No arbitrary fixed root quota; keep moving when a heavy class is saturated |
| HEAVY_CPU | 2 (fallback 1) | May calibrate to 3 after measured stability |
| FFMPEG_HEAVY | 2 (fallback 1) | May calibrate to 3 **only on authorized synthetic/unprotected inputs** |
| MODEL_MPS | 2 (fallback 1) | Requires an already authorized model runtime; no automatic model download |
| MIXED_HEAVY | `CALIBRATE_SEPARATELY` | No fixed initial number; calibrate the mix on measured evidence |
| ENV_ADMIN | 1 | Serialized environment mutation |
| Worktree/ref topology | 1 administrator | No sibling worktree administration |

A measured class that fails falls back to **1** for that class only: `resource-policy-v5.yaml` sets `fail_soft_by_class: true` and `lower_only_affected_lease_class: true`, and a heavy-resource failure must **not** globally serialize lightweight work. The synthetic/unprotected-input qualifier applies to **calibration headroom**, not to ordinary authorized execution.

A plan to start 12–20 threads is **capacity ambition**, not evidence that 12–20 source-writing tasks are READY. Keep lightweight work moving when a heavy resource is saturated.

### 9.2 A portable four-area example

Imagine another repository has four independent subsystems:

- **Area A:** ingestion and deterministic identifiers.
- **Area B:** ranking/experiments.
- **Area C:** queue/retry and reliability.
- **Area D:** export/QC.

H0 may give each lead an independently authorized milestone Goal. The leads can simultaneously work on distinct source paths, while any change to shared schema `EventV2` or `EvidenceRecord` is held for an explicit shared-contract owner. One Area's blocked shared API should not suspend another Area's nondependent internal tests.

This is the same orchestration pattern as VIP's four Gates; the **application-specific authority and dependency graph do not transfer automatically**.

## 10. Suggested task packets

### 10.1 Gate lead packet: broad milestone, bounded authority

~~~yaml
packet_type: example.gate-lead.v1
portfolio_id: <portfolio-id>
goal_id: <goal-id>
lead_label: Coordinator-10
lead_native_id: <verified-native-id>
parent_h0_native_id: <verified-native-id>
area: Gate-1
base_sha: <exact-commit>
base_tree: <exact-tree>
model_reasoning:
  requested_family: "<executor-family: LUNA-for-Codex-or-controller-profile-for-DeepSeek>"
  frozen_model: "<concrete-model-resolved-and-frozen-for-this-Goal>"
  reasoning: "<reasoning-level-required-by-policy>"
durable_state_path: "<repo-relative-or-absolute-state-file>"
mission: >
  Schedule independently READY synthetic Gate-1 engineering tasks,
  review their candidate evidence, and report milestones to H0.
read_scope:
  - src/gate1/**
  - tests/gate1/**
write_authority: NONE_FROM_THIS_PACKET
worker_creation: MODE_A_IF_LIVE_NATIVE_TOOLS_VERIFIED
global_ownership_arbiter: H0
global_worktree_admin: SERIALIZED
shared_contract_policy: REQUEST_H0_OWNER_FOR_CROSS_AREA_CHANGE
forbidden:
  - unauthorized_source_writes
  - real_model_download_or_benchmark
  - main_merge
  - gate_promotion
  - destructive_git
handoff_fields:
  - GOAL
  - LEAD_NATIVE_ID
  - WORKER_IDS
  - VERIFIED_CANDIDATE_HEADS
  - TESTS
  - CONTRACT_DELTAS
  - BLOCKERS
  - NEXT_READY
~~~

This example does **not** grant Gate-1 write permission. Separate worker packets must bind allowed exact paths to a positive, current grant.

### 10.2 Worker packet: single bounded executable task

~~~yaml
packet_type: example.native-worker.v1
portfolio_id: <portfolio-id>
goal_id: <goal-id>
lane_id: <unique-lane-id>
parent_lead_thread_id: <actual-native-id>
creation_run_key: <unique-idempotency-key>
repository: <owner/repo>
project_id: <resolved-codex-project-id>
base_sha: <exact-commit-sha>
base_tree: <exact-tree-sha>
model_reasoning:
  requested_family: "<executor-family: LUNA-for-Codex-or-controller-profile-for-DeepSeek>"
  frozen_model: "<concrete-model-resolved-and-frozen-for-this-Goal>"
  reasoning: "<reasoning-level-required-by-policy>"
durable_state_path: "<repo-relative-or-absolute-state-file>"
expected_worktree: <separate-isolated-worktree>
expected_branch: <unique-non-main-branch-or-detached-for-read-only>
task: Verify the generated harness' declared arm count.
read_scope:
  - src/gate1/harness.py
  - tests/gate1/fixtures/generated_cases.py
write_paths: []
source_grant_id: READ_ONLY_PILOT
resource_class: LIGHTWEIGHT_CPU_TEST
required_evidence:
  - exact Git HEAD and tree
  - source paths and function/constant names
  - bounded conclusion with limitations
acceptance: Confirm two-arm declaration; do not run benchmark.
prohibited:
  - all_filesystem_writes
  - code_edits_and_commits
  - push_or_merge
  - model_inference_or_download
  - protected_media
  - destructive_git
report_to: <verified-native-lead-id>
~~~

These packets illustrate **content**, not guaranteed syntax for a native Codex API. The caller supplies the packet as the actual first-turn prompt, shaped to the runtime.

## 11. Common failure modes and safe responses

| Symptom | What it means | Safe next step |
|---|---|---|
| `create_thread` returns pending client key | Native identity not yet established | Resolve with a compatible exposed mechanism; verify actual native thread; no blind duplicate retry |
| `list_threads` lists similarly titled threads | Identity correlation is ambiguous | Use run key, first turn, project/host/worktree; if still ambiguous, stop |
| Native thread created in the dirty shared checkout | Incorrect writer binding | Refuse writes; preserve shared checkout; use authorized isolated Worktree Admin |
| Worker appears detached | Can be legitimate for read-only; not enough for write binding | Require unique authorized branch and full recheck before source edits |
| Different worktrees edit the same shared schema | Logical write ownership conflict | Park affected writers; assign one contract owner; rebase/reconcile only under explicit safe policy |
| Parent says “message sent” | Delivery, not acknowledged execution | Targeted read and recipient acknowledgement |
| Worker says “all tests pass” | Unverified claim | Independently inspect exact candidate SHA, commands, counts and exits |
| Gate blocked on Owner decision | Only affected dependency subgraph blocked | Continue other independently READY work; batch decisions |
| One worker's test consumes all CPU | Resource oversubscription | Apply shared leases; do not allocate heavy quota per Gate |
| Admin source check passes but prior owner is not terminal | Current branch grant cannot prove quiescence | Hold ownership transfer until attributable writer-release evidence |
| Parent context fills with child transcripts | Inefficient reporting | Use compact Git-backed handoffs and refs; targeted reads |
| Old candidate branch moved | Possible stale contract/base | Pin SHA/tree; re-evaluate before integration; never silently rebase |
| Tool wrapper no longer exposes nested creation | Mode A unavailable in this session | Report actual blocker; use clearly identified Mode B if approved |
| Worker process not visible | Not proof external/queued writer is gone | Report NOT_OBSERVED; preserve assignments |
| Local commit not on GitHub | GitHub cannot certify its bytes | Preserve and list exact local location; publish only with admission |
| Caller wants “synchronize everything” | Risks secrets, media and unauthorized refs | Publish only verified authorized refs; never bulk-push |

**Prohibited recovery shortcuts:** hard reset, git clean, force push, fetch/prune, destructive worktree/branch removal or object pruning without a separately approved recovery and authority process; **history rewrite or rebase of a candidate branch**; and **`git stash` or `git restore` on a shared or unowned checkout**.

## 12. Acceptance tests for the hierarchy itself

A reusable pilot for a new project should prove each capability **separately**.

| Test | Minimum positive evidence |
|---|---|
| H0 to lead creation | Three native lead IDs actually verified, not just pending client keys |
| Lead to worker native creation | Creation invoked in the **lead's own** session; request/result attributable |
| Isolation | Worker has a separate project-bound Git worktree and correct common directory |
| Read-only execution | Worker completes a bounded factual repository question |
| Child → lead | Result retrievable; lead verifies it |
| Lead → H0 | Handoff delivered and acknowledged by H0 |
| H0 → lead follow-up | Targeted message and a new attributable reply |
| Concurrency | Live overlapping work observed; thread-ID count alone insufficient |
| Write admission (**separate future test**) | Unique branch, exact positive write grant, exclusive paths, resources, TDD/test evidence |
| Publication (**separate future test**) | Authorized non-force push and independent remote commit/tree/blob readback |
| Recovery | Ambiguous creation does not create duplicates; failures preserve local state |

For VIP, the reported 2026-10-22 pilot covered the read-only portion, **not** the write-admission or publication rows.

## 13. Production-scale operating procedure

Once the nested read-only capability and real source-writing admission have each been verified, a full Goal can follow this checklist:

1. **H0 bootstrap:** verify fresh remote anchors, one portfolio H0, paused/existing Goal lifecycle, current grants and protected worktrees.
2. **Lead reattachment:** verify saved native lead IDs are reachable; reusing an old read-only lead does not reuse its workers or create new authority.
3. **One global DAG:** identify Gate-local independent tasks and cross-Gate contract dependencies.
4. **Scope arbitration:** H0 owns global leases and shared write manifests; serialized Admin handles worktree topology.
5. **Parallel native creation:** leads create READY workers before waiting; initial turns remain read-only until binding/preflight passes.
6. **Capability execution:** worker TDD, bounded debugging, independent feature-level review, focused and relevant integrated regressions.
7. **Durable candidate:** local commit and non-force remote execution-branch checkpoint when specifically authorized.
8. **Milestone convergence:** lead checks its candidate; H0 checks shared contracts and integration ancestry.
9. **Refill:** finished slots are reassigned to genuine newly READY work.
10. **Terminal Goal:** record actual accomplishments, remote/local split, unresolved worker operations, owner-only decisions, and next safe frontier.

Never let the *pilot's success* stand in for these production engineering predicates.

### 13.1 Acceptance and closure (non-delegable parent duties)

A child's completion message is **not** acceptance. The parent — not the child, not the lead's optimism — owns the following steps, in order, and may not delegate them back to the child being accepted. These rules are owned by [Subagent Lane Protocol](SUBAGENT_LANE_PROTOCOL.md) §11–§13 and `AGENTS.md` items 26–28; this runbook only illustrates them.

**1. Bind the exact `BASE_SHA`.** Every handoff must state the commit the child actually started from. A child may not rewrite its reported base to hide staleness.

**2. Classify the base relation** against the current milestone HEAD, using the child's changed paths and any public/interface/contract deltas:

| Classification | Condition | Required action |
|---|---|---|
| `CURRENT_BASE` | Child base equals current milestone HEAD (or differs only by irrelevant commits) | Normal ownership/test/integration checks |
| `STALE_DISJOINT` | Child is behind, but implementation paths and contract/semantic surfaces are disjoint | Integrate only through a safe non-destructive method; run focused/regression verification |
| `STALE_OVERLAP` | Child is behind and paths, contracts, migrations, dependency semantics or assumptions overlap | Do **not** blindly cherry-pick or rebase; PARK the candidate; inspect the actual conflict; spawn fresh reconciliation/repair from current milestone HEAD when needed |

**3. Handle consumed-contract drift.** A running child whose consumed contract or path delta changes is marked **`STALE_IN_FLIGHT`**; its result is historical/exploratory until explicitly reconciled against the new exact contract fingerprint, and may not be accepted merely because it reports success.

**4. Record one explicit disposition:** `INTEGRATED`, `REJECTED`, `PARKED`, or `BLOCKED`. Silence, a green test, or an absent complaint is not a disposition.

**5. Close or terminate the child.** After the handoff and disposition are durable, explicitly close/terminate the child where the executor supports it. If explicit closure is unavailable, mark it **`TERMINAL_INACTIVE`** and **never reuse it** for new work.
6. **Recycle the slot.** The freed capacity is immediately eligible for genuine newly READY work; do not refill it with invented or duplicate tasks.

## 14. Porting this pattern to another repository

Use the following migration checklist:

1. Establish **one H0** and a single Git remote/source of truth.
2. Define 2–4 truly distinct Areas based on bounded source domains and interfaces, not job titles.
3. Read that project's write/security policies; decide whether native top-level delegation is permitted.
4. Discover the **current** Codex project ID and live tools; do not embed VIP IDs.
5. Introduce a global worktree/branch Admin and a shared lease/ownership registry.
6. Choose a small **read-only pilot**, one worker per Area.
7. Record native IDs, project bindings, pending-resolution evidence, execution overlap and message acknowledgement.
8. Decide Mode A or explicitly brokered Mode B for each Area.
9. Create exact write-task packets separately, with tests and rollback/preservation strategy.
10. Start concurrent implementation only when real READY tasks exist; preserve a single controlled integration owner.
11. Keep compact, durable handoffs so the system is not dependent on one long conversation.
12. Re-run capability preflights if the app tool surface changes; do not assume that an earlier successful pilot is a permanent service guarantee.

### What to copy and what to replace

**Reusable:** role definitions, first-turn read-only binding, pending/native ID discipline, message acknowledgement states, serialized worktree admin, ownership/lease model, milestone receipts, Mode A/B fallback, and the pilot acceptance tests.

**Replace:** VIP Gate names, task IDs, PRs, commit SHAs, portfolio trust-root, model policies, test commands, Git paths, protected-media rules, and Owner authorization decisions. Never import historical task grants into a new repository.

## 15. Source index and maintenance

**Technical source of truth in this repository:**

- [Codex Native Thread Operations Runbook](CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md) — current native tools and identity/binding pitfalls.
- [Subagent Lane Protocol](SUBAGENT_LANE_PROTOCOL.md) — **normative owner** of lane identity, isolation, write-scope, BASE_SHA/stale-base acceptance (§11) and child lifecycle/closure (§13); this runbook only illustrates those rules.
- [Throughput-First Development Protocol](THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md) — multi-root scheduler, dependency and exclusivity rules.
- [Remote Durability and Torrent Orchestration Protocol](REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md) — milestone-sized Goals, durable state and bounded autonomous remediation.
- [Main-Agent Synchronization Protocol](MAIN_AGENT_SYNC_PROTOCOL.md) — Git main vs execution refs, publish boundaries.
- [Resource Policy v5](../portfolio/portfolio-v1/resource-policy-v5.yaml) — repository-wide leases and delegation routing.
- [DeepSeek Harness Controller Profile](../portfolio/portfolio-v1/DEEPSEEK_HARNESS_CONTROLLER_PROFILE.md) — executor-specific model/reasoning policy for DeepSeek Harness roots and children.
- [Project State Maintenance Protocol](../project/STATE_MAINTENANCE_PROTOCOL.md) — durable handoff and independent reconciliation.
- [AGENTS.md](../../AGENTS.md) — repository-wide executor, delegation, acceptance and closure policy.
- `docs/INDEX.md` — repository documentation index (registration of this file is an Owner decision and is not claimed here).

**Pilot provenance:** Owner-relayed `READ_ONLY_HIERARCHICAL_PILOT` terminal report of 2026-10-22, with native IDs tabulated in Section 4. That report is **not stored as an independently verified raw runtime trace in GitHub**.

The durable corroborating record is the published **non-main** branch `origin/execution/2026-10-22-four-gate-controlled-closeout`, under `docs/agent-runs/2026-10-22-four-gate-controlled-closeout/`:

- `PORTFOLIO_FINAL_HANDOFF.md`, `GATE1_HANDOFF.md`, `GATE2_HANDOFF.md`, `GATE3_HANDOFF.md`
- `WORKER_AND_CANDIDATE_INVENTORY.json`, `REMOTE_PUBLICATION_INDEX.md`, `REMAINING_WORK_AND_BLOCKERS.md`

Those records **corroborate** the six native IDs tabulated in Section 4 and the canonical HEAD/tree named in §4. They also **bound** what that evidence supports:

- the three pilot **worker** native IDs are recorded **`notLoaded`**, with terminal state / worktree content **`NOT_OBSERVED`** — `notLoaded` is not terminal evidence;
- `actual_concurrency: NOT_OBSERVED`;
- `tokens_time_utilization: NOT_OBSERVED`.

If a later governed run captures raw tool calls, per-thread first turns, acknowledged messages, worktree inventory, and process overlap, link the immutable receipt here; do not upgrade this historical evidence class silently.

**Maintenance triggers:** update this document if the native tool schema, pending-ID resolver, controller messaging, worktree isolation mechanism, scheduler persistence, or resource governance materially changes. Preserve older reported observations rather than rewriting them as if they had used the newer API.

---

### One-page principle

**One Owner → one H0 → specialized native Gate/Area leads → fresh isolated native workers → verified milestone handoffs → one controlled integration path.**

- A worker's **creation** proves neither worktree binding nor authority.
- A worktree's **isolation** proves neither logical exclusive ownership nor grant.
- A message's **delivery** proves neither acknowledgement nor completion.
- A test's **PASS** proves neither candidate admission nor Gate promotion.
- The hierarchy's **read-only success** does not prove nested production-writing readiness.
- High parallelism pays off only when genuine independent, authorized work exists.
