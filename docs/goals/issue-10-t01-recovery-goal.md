# Goal Template — Issue #10 T01 Recovery/Unblock

Use Luna Medium.

Work in `/Users/yusuf/Repos/video-intelligence-pipeline` and execute GitHub Issue #10 in `Centaurioun/video-intelligence-pipeline` as the governing recovery task under the existing Issue #9 implementation authorization.

Use the repository-local `$video-intel-orchestrator` and current Superpowers skills, especially `systematic-debugging`, `dispatching-parallel-agents`, `using-git-worktrees`, `test-driven-development`, `subagent-driven-development`, `requesting-code-review`, and `verification-before-completion`, plus local `test-automation` where applicable.

First run the complete start-of-turn synchronization gate. Do not delete or clean any local branch, worktree, reflog, stash, unreachable object, or pre-existing untracked file before recovery evidence is collected.

Read `docs/audits/ISSUE9_RECOVERY_AND_T01_UNBLOCK_TASK.md` completely. The verified canonical problem is that remote `main` contains T00/T01 review memos but not the claimed Gate-0 implementation surfaces or Issue #9 run ledger. Treat canonical git state, not the prior chat summary, as authoritative.

Use native `collaboration.spawn_agent`, not Codex App `create_thread`. Every child must have VERIFIED EFFECTIVE `gpt-5.6-luna` / `medium` and an isolated worktree/lane.

Immediately freeze the synchronized base SHA and dispatch the eight independent recovery/review lanes defined by the task contract concurrently: git-recovery, python-runtime, pytest-cache, t01-schema-matrix, t01-fk-cardinality, t01-envelope, t01-test-oracles, process-integrity.

No network/package-index/provider/cloud access is allowed. Search only existing local runtimes, venvs, caches, wheels, and already-present container images for a supported Python+pytest environment. Do not replace pytest with another test framework merely to continue.

After the parallel wave, union the findings once. Recover still-existing T00/T01 candidate commits if possible before reimplementing. Restore the missing canonical Issue #9 ledger. If no offline pytest-capable environment can be established, stop cleanly with `PYTEST_ENVIRONMENT_BLOCKED` after preserving recovery evidence; do not write new behavior-changing production code without executable RED/GREEN evidence.

If the pytest gate passes, recover or reconstruct T00/T01 under strict TDD. Build one frozen T01 contract matrix first, then partition non-overlapping schema-group, validator/types/identity, and tests/verifier write lanes where safe. Run all runnable independent writers/reviewers concurrently. Do not start T02 until T01 receives fresh passing scoped certification.

Close children promptly after durable memo verification/disposition. Keep the main agent as the sole canonical integrator. Preserve detailed work in repo artifacts and use compact handoffs.

Before completion run all required focused tests, Gate-0 verifier checks, `git diff --check`, secret audit, workspace verifier, safe non-force push, pushed-state verifier, and full end-of-turn sync.

Finish only with one recovery verdict from the task contract and `SYNCED` or `SYNC_BLOCKED_<reason>`.
