# VIP V2 Existing-Portfolio Controller Goal Template v1

Use this template only to continue the one Portfolio `vip-v2-execution-portfolio-20261009-v1`. Do not create another Portfolio or replay the historical Root. This template describes controller operation; it grants no task authority on its own.

## Goal-start binding (required)

- Portfolio manifest: `.orchestration/portfolios/vip-v2-execution-portfolio-20261009-v1/manifest.json`
- Portfolio ID: `vip-v2-execution-portfolio-20261009-v1`
- Frozen architecture: approved VIP V2 Atlas v0.4, 28-node DAG and its exact recorded source identity.
- Read `AGENTS.md`, `.orchestration/remaining-work/CONTROLLER_START_HERE.md`, `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`, `docs/architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md`, `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`, resource-policy v5, current Root/Goal state, Atlas, plan register and applicable exact task contracts.
- Verify live `origin/main`, active source/execution refs and trees. Preserve all dirty trees/refs and historical receipts. Freeze the observed canonical SHA and source/base SHA in the Goal record; stale or divergent authority is a stop condition.
- Keep exactly one H0 identity. Reconcile, do not replay, historical accepted Tasks 1–5. Do not infer Gate/task readiness from prior synthetic acceptance.
- Classify every candidate `READY`, `PENDING`, `BLOCKED`, `NOT_OBSERVED`, `PLANNED`, `AUTHORIZED`, `RUNNING`, or `ACCEPTED` with exact evidence. Dispatch only nodes READY under DAG dependencies, current task-specific grant, accepted inputs, path/resource leases and owner-approved plan status.

## Atlas source rehydration and status binding (required)

The pinned v0.4 DAG and writing-plans register are not present on canonical `main` and may be absent from a fresh main-based worktree. Never substitute a same-named file from `main`, another branch, or the dirty shared checkout, and never copy these inputs into canonical paths as part of launch. Retrieve and read them only from the frozen source commit in the manifest:

```sh
set -eu
git fetch origin refs/heads/docs/vipv2-dual-executor-portfolio-owner-intent-20261012
git cat-file -e 2ea14e17ca9795ab3dcf703d3652f20814afc98e^{commit}
git merge-base --is-ancestor 2ea14e17ca9795ab3dcf703d3652f20814afc98e FETCH_HEAD
git cat-file -e 8b015cd7d9f958e57b6876a27c711cde6c20eb5e^{commit}
git merge-base --is-ancestor 8b015cd7d9f958e57b6876a27c711cde6c20eb5e FETCH_HEAD
test "$(git rev-parse 8b015cd7d9f958e57b6876a27c711cde6c20eb5e:docs/superpowers/specs/2026-10-12-vip-v2-full-dual-executor-execution-atlas-v0.4-design.md)" = 076e965494475605bf674d6e4f9424c36ee61986
test "$(git rev-parse 2ea14e17ca9795ab3dcf703d3652f20814afc98e:docs/superpowers/specs/2026-10-12-vip-v2-m0-m5-unified-execution-atlas-dag-v0.4.json)" = f5695a779fa619bce7f6a53e52592fe32d4aa381
test "$(git rev-parse 2ea14e17ca9795ab3dcf703d3652f20814afc98e:docs/superpowers/plans/2026-10-12-vip-v2-full-writing-plans-register.md)" = 3b1360a9bf7e7d5715bb7772e34f9f577e1ee1d1
test "$(git rev-parse 2ea14e17ca9795ab3dcf703d3652f20814afc98e:docs/agent-runs/run-20261012-vipv2-full-atlas-v04-independent-acceptance/owner-relayed-review-and-plan-constraints.md)" = 605e5463a4ae06c7edf69be9995b8bc4dbdef5b2
git show 8b015cd7d9f958e57b6876a27c711cde6c20eb5e:docs/superpowers/specs/2026-10-12-vip-v2-full-dual-executor-execution-atlas-v0.4-design.md
git show 2ea14e17ca9795ab3dcf703d3652f20814afc98e:docs/superpowers/specs/2026-10-12-vip-v2-m0-m5-unified-execution-atlas-dag-v0.4.json | jq -e '.status == "REVISED_CANDIDATE_AWAITING_INDEPENDENT_REVIEW"'
git show 2ea14e17ca9795ab3dcf703d3652f20814afc98e:docs/superpowers/plans/2026-10-12-vip-v2-full-writing-plans-register.md
git show 2ea14e17ca9795ab3dcf703d3652f20814afc98e:docs/agent-runs/run-20261012-vipv2-full-atlas-v04-independent-acceptance/owner-relayed-review-and-plan-constraints.md
```

Stop if fetch, commit availability/ancestry, a blob identity, or the recorded DAG status differs. Do not refresh pins to a newer source implicitly. The separate v0.4 architecture design at `8b015cd7d9f958e57b6876a27c711cde6c20eb5e` has an owner-relayed independent `ACCEPT_WITH_LIMITS` report; that report says it is suitable for owner architectural approval and is not itself an owner-approval act. It does not change the DAG JSON's own `REVISED_CANDIDATE_AWAITING_INDEPENDENT_REVIEW` status. No later independent acceptance of that exact DAG candidate was found at the pinned source commit. Preserve that status and require its applicable independent review/adoption before treating the DAG as accepted authority. The plan register's planning statuses also do not grant dispatch authority.

## Fresh native root dispatch contract

**MANDATORY DISPATCH BINDING:** `NATIVE_DISPATCH_POLICY=NATIVE_PARALLEL_DISPATCH_REQUIRED`. Apply `AGENTS.md` and **Native Codex Parallel Dispatch** in `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md` before scheduling. Record `NATIVE_DISPATCH_STATUS`, `ACTUAL_OVERLAP_EVIDENCE` and `DISPATCH_BLOCKER_IF_ANY`. This requirement does not make an ungranted Portfolio node READY.

**Hard invariant: `FRESH_NATIVE_THREAD_REQUIRED`.** Each ordinary independent Codex Portfolio worker/root is one genuinely fresh native `create_thread` call and one fully self-contained first-turn task packet. Do not use `fork_thread` (it copies conversation history) or in-process `spawn_agent` as a substitute. A manual top-level Codex launch is permitted only when separately authorized and must be labelled MANUAL, not autonomous.

For every candidate peer, freeze before creation:

1. portfolio ID, Atlas v0.4 DAG node, independent Goal/run/lane IDs and run idempotency key;
2. exact repository project ID and `cwd`; isolated worktree path, existing branch selector, base SHA and expected Git tree;
3. explicit task grant ID, expiry/supersession, exact permitted operations and exclusive paths; safe commands and prohibited operations;
4. accepted consumed interface/contract fingerprints bound to that base; source ref and stale-base rules;
5. requested model family `LUNA`, one concrete supported model resolved and frozen for this Goal, reasoning `medium`; capture effective model/reasoning only when exposed, otherwise `NOT_OBSERVED`;
6. resource class, adaptive lease ID/limit, reviewer assignment and durable handoff path;
7. stop conditions and compact handoff fields.

Construct a self-contained first turn that includes this entire packet and applicable repository instructions. Do not rely on Coordinator chat history. Use only the exact current `create_thread` schema. Select `environment.type="worktree"`; where the wrapper supports it, bind an existing explicit branch. A returned request or new title does not prove binding. Inspect the created thread's actual project, CWD/worktree, branch and HEAD before granting writes. If any differs or is unavailable, stop that worker before source/test writes and record BLOCKED/NOT_OBSERVED. Reconcile ambiguous creation through thread inventory before retry, keyed by run ID, to prevent duplicate workers.

After verified creation, persist native thread ID and first turn ID, project/CWD, exact branch/base, requested model settings, observed effective settings, monitor cursor and lifecycle. Dispatch all genuinely READY dependency-safe work without waiting for another completion, with disjoint branch/worktree and exclusive path ownership. Never dispatch stale descendants after consumed contract/base changes.

## Live Controller loop

While this Controller turn remains active:

- monitor peers asynchronously with `wait_threads` and cursors;
- retrieve terminal results independently using `read_thread`;
- verify exact handoff commit/tree, ancestry, changed paths, consumed fingerprints, commands, grant and unresolved Problems;
- independently review candidate changes on VERIFY as applicable; perform only authorized bounded repair;
- record append-only lifecycle and disposition events under the Portfolio event contract;
- retire terminal peers after durable handoff/disposition and close/archive where supported;
- recompute DAG readiness after each verified disposition and immediately refill a vacated slot with genuinely READY authorized work;
- permit exactly one non-main integration owner; never merge a sibling or mutate canonical main without separate exact authority.

This live loop does not promise continuation after the Controller turn ends. Persistent background scheduling is unsupported/not authorized unless a later verified system is installed with separate owner approval. Do not create empty work to fill capacity.

## Failure/fallback

If native creation, exact project/worktree/base binding, model policy resolution, permission, or durable handoff fails, preserve the exact observation, mark the capability/lane state and continue only independent READY authorized work. Do not switch to local shared checkout, fork, subagent, serial preflight, another model family or unverified API. When a human separately authorizes manual dispatch, provide a complete packet for an independently launched top-level instance and label that path MANUAL.

Terminal Goal receipt lists Portfolio ID, live canonical/source identities, each observed thread and turn ID, branch/base/head/tree, grant/paths, lifecycle/disposition, effective-model evidence, active leases, refill evidence, blockers and exact next owner decision. Goal completion requires verification, not merely successful thread creation.
