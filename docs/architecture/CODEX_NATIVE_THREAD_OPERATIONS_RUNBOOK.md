# Codex Native Thread Operations Runbook

**Status:** Operational guidance subordinate to repository authority.
**Scope:** Codex App native-thread discovery, coordinator communication, worker launch, binding, monitoring, and handoff.
**Authority:** This document explains procedures; it grants no task, source-write, signing, lease, admission, operational, or canonical-main authority.

Read this with `AGENTS.md`, `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`, `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`, and `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`. If guidance conflicts, those governing sources and exact owner/task authorization take precedence. A thread, message, review, candidate, or successful test does not create authority.

> **Hierarchical delegation / nested native coordinator case study:** See [Nested Native Codex Coordinators: Hierarchical Parallel Execution Runbook](NESTED_NATIVE_CODEX_COORDINATOR_RUNBOOK.md) for the reported 2026-10-22 Mode-A read-only pilot, lead-to-worker creation, pending/native ID handling, messaging, worktree isolation, global ownership/leases, and a reusable cross-project checklist. This documentary link grants no additional authority.

## 1. Evidence labels and live tool discovery

Use the Codex App tools exposed in the current session. Tool names, schemas, model catalogs, project IDs, and runtime support can change. Inspect current tool descriptions and argument schemas before use. A historical request is evidence of that observed call only; it is not a permanent API contract.

Use these tools for these purposes:

| Tool | Use | Does not prove |
| --- | --- | --- |
| `list_projects({})` | Resolve the current saved project ID and repository binding. | A thread is attached to that project. |
| `list_threads({limit})` | Find visible native thread IDs, host, status, title, project context, and CWD where returned. | A thread has a safe writer worktree or valid task grant. |
| `create_thread({target, prompt, ...})` | Request a fresh native thread and initial self-contained turn. | A pending setup completed, the requested branch was bound, or task authority exists. |
| `read_thread({threadId, ...})` | Inspect a known native thread’s saved turns and progress. | The thread’s reported Git state is independently verified. |
| `send_message_to_thread({threadId, hostId?, prompt})` | Send a follow-up to an exact existing native thread. | The recipient acknowledged, accepted, or is authorized to act. |
| `wait_threads({targets, timeoutMs})` | Wait for bounded progress/completion/attention across known native IDs. | A timed-out thread has failed or a worker result is accepted. |
| `get_worktree_creation_status({operationId})` | Inspect an operation ID returned by supported worktree create/attach tools. | A `clientThreadId` resolves to a native thread. |
| Worktree Admin / Git inspection | Establish or verify isolated path, branch, HEAD, tree, base, and cleanliness under serialized authority. | A lease, grant, or global resource allocation. |

The current `create_thread` surface distinguishes `target.type: "project"` from projectless and cloud targets. Project targets include a `projectId` and an environment. The currently exposed project environment variants include `local` and `worktree`; worktree `startingState` may be `working-tree` or a branch/ref selector. Confirm the actual schema before copying examples. If an argument is unsupported or a request fails, preserve the exact error and stop; do not probe guessed variants.

Use these evidence labels in handoffs:

- **CONFIRMED** — directly returned by a tool or independently checked from the exact Git state.
- **INFERRED** — supported by observations but not directly proven; state the basis.
- **NOT_OBSERVED** — the required record or capability was not available.
- **BLOCKED** — a concrete prerequisite failed or is missing; include evidence and the next safe condition.

## 2. Coordinator-to-Coordinator communication

First verify the recipient’s actual native ID using current inventory or a trusted prior handoff plus a targeted `read_thread`. Record the recipient ID and host. A repository CWD or familiar title is not a project-binding proof.

The historically observed successful message call used this shape:

```json
{
  "threadId": "<verified-native-recipient-id>",
  "hostId": "local",
  "prompt": "<self-contained-handoff>"
}
```

Coordinator #1’s retained history records completed `send_message_to_thread` calls to Coordinators #4 and #5 with this argument shape. The message included task boundaries, thread and project-binding cautions, and security/controller separation for #5. Subsequent recipient histories show related activity, but the retained record does not show a direct acknowledgement tied specifically to those onboarding messages.

Write a concise, self-contained handoff with the recipient role, reason for contact, exact immutable source identities, what is requested, read/write scope, limits, response format, and explicit statement that the message transfers no authority. Verify the tool response reports delivery, then read the recipient thread or wait for a response and record its actual acknowledgement or disposition. A delivery result alone is not an acknowledgement.

Cross-coordinator work retains the assigned owner for each grant, path, branch/worktree, resource lease, integration route, and security decision. A message cannot transfer exclusive ownership or make a candidate accepted.

## 3. Fresh native H3 worker creation

An ordinary independent Codex root uses a **fresh native `create_thread`** with a complete first-turn packet. `fork_thread` copies conversation history and is for intentional, authorized conversation branching. `spawn_agent` is an in-process subagent and is not an independent native root. Neither is a silent substitute for a fresh worker.

Before creation, determine that the task is independently READY and authorized. Freeze its Portfolio/Goal/node identity, exact source base and tree, consumed contract fingerprints, exclusive paths, permitted operations, safe commands, resource class/lease, reviewer, stale-base policy, and stop conditions. Do not create a worker merely to fill capacity.

The following is a **schema-illustrative request, not a historically verified successful call**. Recheck the current schema and current project inventory first; remove or adapt any field the live schema does not support.

```json
{
  "target": {
    "type": "project",
    "projectId": "<verified-current-project-id>",
    "environment": {
      "type": "worktree",
      "startingState": {
        "type": "branch",
        "branchName": "<verified-existing-source-ref>",
        "onMissing": "error"
      }
    }
  },
  "prompt": "<complete-read-only-worker-packet>"
}
```

Other fields such as `title`, `model`, and `thinking` are schema- and policy-dependent. Follow the current repository model policy and current tool catalog; do not hard-code a historical model string.

**Historical E04 schema-mismatch candidate:** several failed calls supplied `projectId` and `type` as extra top-level fields while the nested `target` had `type:"project"` but omitted its required `projectId`. They returned `create_thread received invalid arguments`. This is a concrete schema-mismatch candidate. Later calls with different shapes also failed, so this observation does not conclusively explain every E04 failure.

The original successful F01 `create_thread` payload and raw response were **NOT_OBSERVED** in the historical investigation. Do not reconstruct them from the resulting worker ID or later reports.

## 4. Asynchronous identity resolution and duplicate prevention

Keep these identities distinct:

1. **Creation request** — the call and its returned status.
2. **Pending `clientThreadId`** — a setup key, not a native thread ID.
3. **Native `threadId`** — the actual thread ID accepted by thread tools and confirmed through inventory/read.
4. **Worktree operation ID** — identifies a create/attach-worktree operation, not a thread.
5. **Created worktree** — a filesystem/Git worktree whose path and repository identity must be checked.
6. **Verified binding** — native thread, host, project, CWD, worktree, branch, HEAD/tree/base, cleanliness, and task assignment all agree.

If creation returns a pending client key, use only a currently exposed resolver whose schema explicitly accepts that key. Do not pass it to `read_thread`, `send_message_to_thread`, or `wait_threads`, which require native IDs. Do not use `get_worktree_creation_status` with a client key; that operation accepts a worktree operation ID. If no compatible resolver is exposed, report **AMBIGUOUS / BLOCKED**, preserve the key, and do not retry creation. This prevents duplicate workers.

An actual `threadId` should be confirmed through `list_threads` or a successful targeted `read_thread`, including host and available project/CWD metadata. A title, request payload, or parent’s statement is insufficient.

## 5. Isolated worktree and branch binding

The worker’s first turn is read-only. Before any source-writing turn, independently verify project ID and repository path, actual CWD, Git top-level/common directory, separate worktree, exact base and tree, branch/detached state, cleanliness, task grant, exclusive path ownership, consumed contracts, reviewer and resource lease. Preserve any dirty or untracked state. On any mismatch, stop before writing.

Useful read-only Git checks, run from the worker’s actual CWD:

```sh
pwd -P
git rev-parse --show-toplevel
git rev-parse --git-dir
git rev-parse --git-common-dir
git worktree list --porcelain
git branch --show-current
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git status --porcelain=v1 --untracked-files=all
git merge-base --is-ancestor '<EXACT_BASE_SHA>' HEAD
git diff --name-status '<EXACT_BASE_SHA>'...HEAD
git status --short -- '<OWNED_PATH_1>' '<OWNED_PATH_2>'
```

An empty `git branch --show-current` means detached HEAD. Confirm that the worktree path is not the shared checkout and that `git rev-parse --git-common-dir` points to the expected repository. Git cannot prove exclusive task ownership by itself: compare the exact paths against the current scheduler/assignment records and leases.

**Historical F01 sequence (reported and independently recorded in thread handoffs):** the H3 worker was observed in an isolated worktree; initial preflight found detached HEAD at the intended base; a later authorized, serialized Worktree Admin operation established a unique execution branch; branch, base, tree, path and cleanliness were then rechecked before source writing. The original successful `create_thread` request and raw Worktree Admin action receipt were **NOT_OBSERVED**.

If authorized to bind a branch manually, do so only after the isolated worktree is clean, HEAD equals the exact authorized base, the branch name is unique across refs/worktrees, and a serialized Worktree Admin owner has the operation. For example, after those conditions are separately recorded:

```sh
git switch -c '<AUTHORIZED_UNIQUE_BRANCH>' '<EXACT_BASE_SHA>'
```

Then rerun and record the binding checks. A requested `startingState` may still produce detached HEAD; the request is not proof of the result. Never repair a binding mismatch in a shared or dirty checkout.

**Historical E04 manual-launch failure:** thread `01a14036-bc12-75e2-9d72-766153c56e94` was observed with CWD `/Users/yusuf/Repos/video-intelligence-pipeline`, the dirty shared checkout. Its branch/HEAD/tree did not match the intended E04 source base, and project binding was not independently observed. A thread title, prompt, or repository CWD does not prove isolation. Manual top-level launch is not verified autonomous native H3 dispatch.

## 6. Admission and authority are separate predicates

Verify the exact contract’s requirements; there is no universal issuer, signer, lease administrator, or allocation service implied by this runbook. Keep these distinct:

- **Owner Goal approval:** authorizes only the scope it names.
- **Development-task grant:** permits specified source/test operations on exact paths and bases.
- **Signed operational grant:** authenticates a specific intent only when the applicable trust profile and verifier validate it.
- **Resource lease/allocation:** task-local claims do not prove machine-wide allocation.
- **Exclusive write ownership:** prevents competing writers from owning the same paths.
- **Native project/worktree binding:** identifies where a worker runs, not what it may do.
- **Operational admission:** requires all contract-specific predicates to pass.
- **Trust/security activation:** may require separately verified profile, signer, revocation and state initialization.

Do not infer one from another. A successful thread launch or delivered task packet does not make an ungranted task READY. A development grant for admission code does not issue or validate a live operational grant.

## 7. Dispatch, monitoring, and immutable handoff

For two or more independent, authorized READY tasks, create and start their fresh native workers before waiting for one to finish. Each receives a self-contained first-turn packet and exclusive scope. Then monitor asynchronously:

```json
{
  "targets": [
    {"threadId": "<verified-native-id-a>", "hostId": "local"},
    {"threadId": "<verified-native-id-b>", "hostId": "local"}
  ],
  "timeoutMs": 60000
}
```

Use `wait_threads` with observed native IDs and returned cursors where available. Use `read_thread` to inspect actual results; a timeout or UI “Done” label for creation is not implementation completion. Send follow-ups with `send_message_to_thread` only to verified native IDs. Do not message workers to widen scope or transfer authority.

Maintain BUILD / VERIFY / REPAIR as dependency-safe rolling frontiers. On completion, verify the candidate’s exact commit/tree/blobs, changed paths, base ancestry, tests and open problems; independently adjudicate stale-base and path ownership; integrate only through the assigned non-main owner. Release only that task’s path/resource allocation according to its governing records. Refill capacity immediately only with newly verified READY work. There is no inference of unattended background scheduling.

Durable handoff should name exact thread/host and turn where available, base/head/tree, changed paths/blob IDs, consumed/produced contracts, test command and result, reviewer, stale-base disposition, open Problem IDs, current task state, and durable state/commit location. Parent verification is required; worker completion is not acceptance.

Fresh thread creation, message delivery, actual worker execution, overlapping execution, durable result retrieval, rolling refill, and persistent background scheduling are separate capabilities. Record only the ones directly observed. A live Controller may perform asynchronous monitoring/refill while it is active; do not claim a persistent scheduler without evidence.

## 8. Troubleshooting table

| Symptom | Evidence to capture | Safe action |
| --- | --- | --- |
| `create_thread received invalid arguments` | Exact current schema, complete redacted argument object, exact tool error, current project inventory. | Check shape against the live schema once. Preserve the error; do not guess/retry arbitrary variants. Classify cause as NOT_OBSERVED unless diagnostics identify it. |
| Coordinator is projectless | Current `list_threads` entry and `list_projects` result. | Do not equate CWD with project binding. Use a valid current project target for a new request; do not retroactively claim attachment. |
| Missing project ID | Current `list_projects` result and schema. | Resolve the ID from inventory; never reuse an unverified historical ID or put it in an unsupported argument location. |
| Pending client ID has no resolver | Exact returned fields and schemas of available identity tools. | Mark ambiguous; do not pass it as a thread ID or create a replacement. |
| Worktree is at wrong base | Actual path, HEAD/tree, expected base and ancestry result. | Stop. Preserve it. Do not write, rebase, reset or relabel it. |
| Detached HEAD | `git branch --show-current`, HEAD/tree, clean status. | Stop writes. A serialized Worktree Admin may bind a unique branch only under its separate authority, then reverify. |
| Dirty shared checkout | CWD/root, branch, full status. | Preserve all state. Do not use it as a worker worktree; do not stash/reset/clean. |
| Worktree missing | Creation response and any actual operation ID/status. | Wait only on a supported operation ID. Do not infer a thread ID from it or retry ambiguous thread creation. |
| Unsupported model/environment | Live schema/catalog and exact tool error. | Resolve within current policy; do not silently switch models or environment types. If no compatible option exists, block that dispatch. |
| Missing grant or lease | Exact task grant and lease records, expiry, binding and path/resource scope. | Do not start writes; a task prompt, review, message, or root approval does not substitute. |
| Ambiguous possible duplicate | Request result, client key, inventory and resolver support. | Do not retry or create a substitute until identity is resolved or verified no-thread evidence exists. |
| Message delivered but no response | Send-call response, recipient thread status/turn history, bounded wait result. | Report delivered/no acknowledgement. Do not infer execution or acceptance. |

## 9. Reusable templates

### 9.1 Coordinator handoff

```text
To: <verified-native-thread-id> on <verified-host>
Purpose: <specific handoff or bounded decision>
Source: <exact commit/tree/contract fingerprints>
Request: <self-contained task and response format>
Scope: <read/write mode, exact owned paths, commands, resources>
Prerequisites/limits: <grant, dependencies, expiry, prohibited operations>
Please acknowledge with: <exact evidence or BLOCKED_WITH_EVIDENCE>
This message does not transfer authority or establish task acceptance.
```

### 9.2 Fresh H3 read-only bootstrap

```text
Task/run/lane: <unique IDs>
Initial mode: READ_ONLY. Do not edit, stage, test, sign or mutate refs.
Project ID: <from current list_projects>
Expected repo/CWD/worktree: <exact paths>
Expected branch/base/tree: <exact refs and SHAs>
Required consumed contracts: <exact blob/fingerprint IDs>
Report actual native thread/host, project, CWD, Git dirs, branch/HEAD/tree,
cleanliness, ancestry, path ownership, effective model evidence, and missing
grant/lease predicates. Stop on mismatch; mark unavailable facts NOT_OBSERVED.
```

### 9.3 Source-write admission after independent verification

```text
Only after parent verifies the exact native ID and read-only binding, current
task grant, base/tree, consumed contracts, exclusive paths, reviewer and lease:
perform <exact authorized operation> on <exact paths> using <exact commands>.
Stop on stale base, dirty/unexpected state, contract/path delta, grant expiry,
lease loss, or any requested operation outside scope. This packet grants only
the expressly authorized development work; it does not activate operations.
```

### 9.4 Worker completion handoff

```text
Thread/host/turn: <observed IDs>
Project/worktree/branch: <observed binding>
Base -> candidate: <commit/tree identities>
Changed paths/blobs: <exact list>
Tests: <exact command and observed output/exit status>
Review: <reviewer and exact candidate disposition or pending>
Contract deltas/open Problems: <IDs and impact>
Stale-base/path/lease disposition: <evidence>
Durable handoff: <commit/tree/state path>
Limitations: <what was not verified>
```

### 9.5 BLOCKED_WITH_EVIDENCE

```text
State: BLOCKED_WITH_EVIDENCE
Exact predicate: <missing or failed condition>
Observed: <tool call/error or Git command/result>
Expected: <exact ID/schema/base/grant/lease requirement>
Preserved state: <thread/client key/worktree/dirty evidence>
Safe next condition: <one supported resolver, owner decision, or binding check>
Not done: <writes/tests/duplicate creation/authority transfer, as applicable>
```

## 10. Historical evidence limits

The native project ID `1c15c3b9-5df2-46fb-9d3b-285b8c2189ee` was observed in the cited historical Coordinator records; resolve it again with current `list_projects` before relying on it.

Historical thread identifiers available for provenance:

- Coordinator #1: `01a132db-804e-7e32-b430-8c2756c7c425`
- Coordinator #4: `01a13f50-2d25-7b72-9fee-5a60c0599e99`
- Coordinator #5: `01a13f51-1eeb-7141-92f3-0ae841f00abb`
- Coordinator #6: `01a13fcf-2e24-7720-b46c-7635d6c2dcc1`
- Reported F01 H3 worker: `01a1401d-e374-7dd1-8c89-3edc6d843f7b`
- Incorrectly bound manual E04 thread: `01a14036-bc12-75e2-9d72-766153c56e94`

Historical evidence supports successful coordinator messaging and later F01 worker/worktree binding reports. It does not include the raw successful F01 thread-creation request or response, raw serialized Worktree Admin receipt, or client-key resolver event. E04 creation errors are confirmed, but one universal root cause is not. Use these records as bounded history, not current authority or API guarantees.
