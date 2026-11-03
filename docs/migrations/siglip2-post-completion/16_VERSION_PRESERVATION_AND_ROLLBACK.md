# Version Preservation and Rollback Strategy

**Information state:** `FROZEN_DECISION` + `INFERRED_DESIGN` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`

## Purpose

Ensure V1 Base, V2 Base, and V2 So400m remain independently reproducible throughout migration and benchmark work without relying on mutable branches or conversational memory.

## Preservation Principle

Preserve **reproducible states**, not three permanently duplicated repositories.

Each candidate should be recoverable from:

- immutable Git commit SHA;
- optional release/tag identity;
- exact model ID;
- immutable model revision;
- weights digest;
- processor/preprocessing digests;
- dependency/runtime receipt;
- semantic-space ID;
- relevant test/verification receipts;
- benchmark manifest references when applicable.

## Candidate Milestones

### Milestone A — V1 Base completion

Before migration begins, freeze:

- V1 completion SHA;
- V1 model identity/revision/digests;
- V1 runtime identity;
- V1 regression status;
- any index/generation evidence required for the benchmark.

Do not begin V2 work from an uncommitted or ambiguous V1 state.

### Milestone B — V2 Base candidate

After V2 Base passes its migration acceptance gate, freeze:

- implementation SHA;
- exact V2 Base model revision/digests;
- dependency/runtime identity;
- semantic-space ID;
- bounded smoke evidence where authorized;
- regression/verification receipts.

This state becomes the base for So400m extension.

### Milestone C — V2 So400m candidate

After So400m extension passes its acceptance gate, freeze the equivalent identity set.

Only after all three candidate states exist should the three-way benchmark proceed.

## Branch / Worktree Strategy

Preferred development shape:

```text
immutable V1 completion SHA/tag
        |
        +--> V2 Base migration branch/worktree
                  |
                  +--> verified V2 Base SHA/tag
                            |
                            +--> So400m extension branch/worktree
```

The exact branch names are operational choices.

The critical requirements are:

- branch from known immutable bases;
- record candidate SHAs;
- avoid destructive history rewriting;
- preserve candidate milestones through Git history/tags.

## What Rollback Means

Rollback means selecting a previously verified candidate state and its matching semantic-space/index artifacts.

It does **not** mean:

- rewriting model identity fields in a newer index;
- downgrading code while reusing incompatible V2 vectors;
- deleting newer evidence;
- hard-resetting shared history.

A rollback to V1 requires the V1 code/model/runtime/index combination that produced V1 evidence.

A rollback to V2 Base requires the corresponding V2 Base combination.

## Index Preservation

At least until the benchmark decision is complete:

- do not delete benchmark-eligible V1 candidate index evidence;
- do not overwrite V2 Base index evidence with So400m;
- do not reuse one semantic-space root as though it belonged to another candidate.

After benchmark completion, retention/cleanup remains subject to separately approved policy.

## Historical Evidence

Do not rewrite historical design, audit, or run records to make them look as if they always supported SigLIP2.

Future records should point back to historical V1 evidence and explain the migration.

History is evidence.

## Failure During V2 Base Migration

If V2 Base implementation becomes unstable:

1. stop the migration candidate;
2. preserve failure evidence;
3. return to immutable V1 completion state;
4. do not alter V1 artifacts;
5. use systematic debugging before proposing a fix;
6. resume from an isolated branch/worktree once the cause is understood.

## Failure During So400m Extension

If So400m fails due to memory, runtime, or 1152-D plumbing:

- preserve verified V2 Base unchanged;
- treat So400m as the failed candidate under investigation;
- do not weaken V2 Base acceptance merely to make So400m pass;
- do not assume a failure invalidates V2 Base.

## Benchmark Rollback

If benchmark execution is found to be invalid because corpus/query/relevance/metric rules changed mid-run:

- invalidate that benchmark run;
- preserve its receipt as failed/invalid evidence;
- restore the last frozen benchmark protocol;
- rerun all affected arms consistently.

Do not selectively rerun only the model that lost.

## Destructive Operations

This strategy does not authorize:

- hard reset;
- force push;
- branch/worktree destruction;
- `git clean`;
- reflog expiration;
- object pruning;
- destructive archive/index cleanup.

Such actions require their own explicit authorization and safe recovery evidence.

## Completion Condition

Version preservation is adequate when a future agent can answer:

“Exactly which code, model bytes, processor bytes, runtime, semantic space, and evidence produced this candidate?”

without depending on a mutable branch name or chat history.
