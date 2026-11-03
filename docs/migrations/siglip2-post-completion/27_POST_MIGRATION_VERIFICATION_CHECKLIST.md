# Post-Migration Verification Checklist

**Information state:** `TEMPLATE` + `NOT_AUTHORIZED_FOR_EXECUTION`

## Purpose

Prevent a migration candidate from being called complete based only on a successful model load or a narrow test.

Use once for V2 Base and again for V2 So400m.

## Candidate Identity

- [ ] exact candidate label recorded;
- [ ] exact code SHA recorded;
- [ ] base SHA recorded;
- [ ] branch/worktree recorded;
- [ ] exact model ID recorded;
- [ ] immutable model revision recorded;
- [ ] weights digest recorded;
- [ ] processor/preprocessing digests recorded;
- [ ] semantic-space ID recorded;
- [ ] runtime/dependency receipt recorded.

## Scope Audit

- [ ] changed files match the approved migration plan or deviations have explicit rulings;
- [ ] no unrelated source inventory redesign;
- [ ] no unrelated PTS/timebase/refinement redesign;
- [ ] no human editorial-decision automation added;
- [ ] no edit-plan/render/QC scope widened;
- [ ] no protected-media execution occurred outside authorization;
- [ ] no full-archive indexing occurred as a migration shortcut.

## Profile and Provenance

- [ ] unresolved identity values fail closed;
- [ ] processor asset set is complete for the frozen candidate;
- [ ] text preprocessing contract is complete and attributable;
- [ ] image preprocessing contract is attributable;
- [ ] session output dimension equals profile dimension;
- [ ] dtype/normalization match the declared semantic-space contract;
- [ ] changing model/revision/digests/preprocessing changes semantic-space identity as expected.

## Vector / Index Correctness

- [ ] row width derives from candidate dimension/dtype;
- [ ] append/committed-byte accounting is correct;
- [ ] crash-tail recovery uses the same row width;
- [ ] query shape is candidate-correct;
- [ ] wrong-width query fails closed;
- [ ] incompatible semantic-space mixing fails closed;
- [ ] candidate has isolated generation/index identity.

For So400m additionally:

- [ ] 1152-D synthetic storage/search path passes;
- [ ] float32 row width is 4608 bytes;
- [ ] no generic representation path still requires `768 * 4`.

## Runtime / Device

- [ ] local-only runtime path verified;
- [ ] no automatic model download path introduced;
- [ ] remote-code trust remains disabled unless separately approved;
- [ ] requested MPS unavailable fails rather than silently falling back;
- [ ] relevant MPS environment settings recorded;
- [ ] model identity is revalidated after opening.

## Tests

- [ ] all migration-specific RED→GREEN tests recorded;
- [ ] model/profile unit tests pass;
- [ ] semantic-space adversarial tests pass;
- [ ] storage/index/search tests pass;
- [ ] V1 regression tests remain green;
- [ ] relevant VIP FVS authorization/provenance tests pass;
- [ ] exact test commands and outputs/receipts recorded.

Do not write “all tests pass” without fresh verification evidence.

## Bounded Real Smoke — When Authorized

- [ ] execution authorization recorded;
- [ ] bounded source/fixture identity recorded;
- [ ] output dimension measured;
- [ ] vectors finite;
- [ ] normalization verified;
- [ ] local index build/query succeeds;
- [ ] runtime/device recorded;
- [ ] wall time recorded as bounded smoke evidence;
- [ ] memory evidence recorded where measured;
- [ ] no smoke result is represented as full-archive scale evidence.

If real smoke is not authorized, mark it `BLOCKED`, not passed.

## Review

- [ ] requesting-code-review completed before integration;
- [ ] findings classified;
- [ ] Critical/Important findings fixed or explicitly block integration;
- [ ] review feedback handled through receiving-code-review discipline;
- [ ] review evidence preserved.

## Verification Before Completion

- [ ] canonical candidate SHA independently re-fetched/verified;
- [ ] intended files present at that SHA;
- [ ] current verification commands rerun;
- [ ] results read, not inferred;
- [ ] no stale success message used as evidence.

## Candidate-Specific Completion Rules

### V2 Base

Before `VERIFIED_V2_BASE`:

- [ ] V1 candidate remains reproducible;
- [ ] V2 Base is a distinct semantic space;
- [ ] complete SigLIP2 preprocessing identity exists;
- [ ] profile-aware representation boundary is adequate for planned So400m extension;
- [ ] no benchmark-winner claim has been made.

### V2 So400m

Before `VERIFIED_V2_SO400M`:

- [ ] verified V2 Base remains reproducible;
- [ ] 384/14/1152 contract verified from frozen checkpoint/runtime;
- [ ] 1152-D generic plumbing passes;
- [ ] So400m runtime smoke recorded when authorized;
- [ ] no benchmark-winner claim has been made.

## Final Status

Choose exactly one:

- [ ] `VERIFIED_CANDIDATE`
- [ ] `DONE_WITH_NONBLOCKING_FINDINGS`
- [ ] `BLOCKED`
- [ ] `FAILED_VERIFICATION`

Record:

```text
candidate:
base_sha:
final_sha:
model_revision:
semantic_space_id:
test_receipts:
review_receipt:
verification_receipt:
nonblocking_findings:
blocking_findings:
status:
```

A `VERIFIED_CANDIDATE` is eligible for the later frozen benchmark. It is not automatically the preferred production representation.
