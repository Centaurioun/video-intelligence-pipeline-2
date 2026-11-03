# Goal — Bootstrap Exact Gate-0 Test Environment and Finish T01

Use Luna Medium.

Work in `/Users/yusuf/Repos/video-intelligence-pipeline`.

Execute GitHub Issue #11 as the governing task under the existing Gate-0 T00–T11 local/synthetic implementation authorization plus `docs/audits/GATE0_TEST_ENVIRONMENT_BOOTSTRAP_AUTHORIZATION.md`.

Use the repository-local `$video-intel-orchestrator`, AGENTS.md, MAIN_AGENT_SYNC_PROTOCOL.md, SUBAGENT_LANE_PROTOCOL.md, the Gate-0 v1.1 specification, v1.1.1 erratum, canonical implementation plan, Issue #9/Issue #10 ledgers and recovery memos, and the current installed Superpowers skills for their domains.

## Required skills

Use, where applicable:

- `superpowers:using-superpowers`
- `superpowers:systematic-debugging`
- `superpowers:test-driven-development`
- `superpowers:dispatching-parallel-agents`
- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-development`
- `superpowers:requesting-code-review`
- `superpowers:verification-before-completion`
- local `test-automation`

Use native `collaboration.spawn_agent`, not Codex App `create_thread`.
Every child must have VERIFIED EFFECTIVE `gpt-5.6-luna` / `medium` settings.

## Start and preservation

Run the full start-of-turn synchronization gate first. Preserve all local recovery branches/worktrees and pre-existing untracked files. Do not prune/reset/clean/delete recoverable Issue #9 candidate history before disposition.

## Phase A — exact environment bootstrap

This phase alone has temporary controlled network authorization.

Establish an isolated repository-local Gate-0 development/test environment using exactly:

- Python `3.11.9`;
- the exact versions pinned by the recoverable/current `requirements/gate0.lock`, including `pytest==8.3.3`.

Rules:

1. Use only official Python/package distribution sources.
2. Before download, recover/inspect the exact `requirements/gate0.lock` from the preserved Issue #9 candidate branch if canonical main does not yet contain it. Do not invent a new lock or alter versions during bootstrap.
3. Download/install only what is required for that exact environment. No model/provider/cloud artifacts and no unrelated package upgrades.
4. Keep the environment repo-local/isolated; do not mutate unrelated project venvs.
5. Record interpreter origin/version, package versions, commands, and provenance/checksums where available in a durable Issue #11 ledger/receipt.
6. Verify `python --version` is exactly `3.11.9` and `python -m pytest --version` is exactly `8.3.3` (plus exact lock conformance for the rest of the lock).
7. If any exact version cannot be obtained or verified, stop with `GATE0_EXACT_ENVIRONMENT_BOOTSTRAP_BLOCKED`. Do not substitute another version.
8. Once exact environment verification succeeds, turn network access back off. All later phases must run under the original no-egress/local-only boundary.

## Phase B — recover and canonicalize T00/T01 candidates

After network is disabled:

1. Recover the preserved Issue #9 candidate branch/history before reconstructing code.
2. Create a durable Issue #11 run ledger.
3. Compare recovered T00/T01 candidate paths against current canonical main and the frozen T00/T01 contract.
4. Integrate only authorized implementation/config/test/schema/verifier paths through main-agent-only canonical integration.
5. Do not treat the old T01 candidate as accepted: its final review documented load-bearing schema/FK/envelope defects.

## Phase C — T01 remediation with maximal safe parallelism

Use the Issue #10 recovery memos as the frozen defect/contract input. Partition non-overlapping candidate-write lanes and run them concurrently where safe. Recommended surfaces:

- schema group A: source/discovery/policy/split;
- schema group B: queries/gold/judgments/window-sample;
- schema group C: run/ranked/runtime-ledger/metrics/gate-decision;
- shared envelope/types/identity/schema registry;
- FK/cardinality/scope/purpose validator;
- tests/golden oracles/verifier.

Shared-file ownership must remain exclusive per wave. Do not create duplicate writers.

T01 must close all previously durable blockers:

- artifact-specific required/optional/null fields for all 13 contracts;
- field types and enums;
- finite-number constraints;
- unknown-field rejection;
- one authoritative opaque-ID syntax;
- complete ArtifactEnvelope/ArtifactRef/JSONL record-envelope validation;
- exact schema-version and timestamp validation;
- lowercase 64-hex digest validation and payload binding;
- executable cross-artifact FK/cardinality/scope/purpose validation for discovery authorization and PolicyDecision semantics;
- valid/invalid golden test oracles;
- exactly 13 persisted runtime artifact names and no fourteenth result artifact.

## TDD requirement

Now that the exact test environment is authorized, do not park pytest evidence.
For every behavior-changing remediation:

RED test first → run exact pytest command and observe intended failure → minimal GREEN implementation → rerun and observe pass → refactor/regression while green → scoped commit and durable memo.

Unexpected failures use `systematic-debugging`, not speculative patch stacking.

## Certification

After T00/T01 are integrated on canonical main and focused/full T00/T01 pytest/verifier checks are green, freeze one SHA and spawn at least three fresh Luna Medium certifiers concurrently:

1. schema/field-contract/ID/envelope certification;
2. FK/cardinality/policy/discovery-purpose certification;
3. TDD/test-oracle/verifier/process/canonical-integration certification.

Union justified blockers once. Allow at most one bounded remediation + recertification generation.

Do not start T02 in Issue #11. If T01 passes, Issue #9 can resume at T02 in a fresh subsequent Goal.

## Completion

Before ending require:

- exact Python 3.11.9 environment verified;
- exact lock including pytest 8.3.3 verified;
- network disabled after bootstrap;
- canonical main contains accepted T00/T01 implementation/config/tests/schemas/verifier and restored ledger evidence;
- focused and T00/T01 full pytest green;
- Gate-0 verifier checks green where implemented;
- all certifier lanes terminal;
- `git diff --check` green;
- secret audit green;
- `bash scripts/verify-workspace.sh` green;
- safe non-force push;
- `bash scripts/verify-workspace.sh --require-pushed` green;
- final local main == origin/main.

Finish only with one of:

`GATE0_T01_UNBLOCKED_RESUME_ISSUE9`

`GATE0_T01_RECOVERY_NEEDS_WORK`

`GATE0_EXACT_ENVIRONMENT_BOOTSTRAP_BLOCKED`

and one of:

`SYNCED`

or `SYNC_BLOCKED_<reason>`.
