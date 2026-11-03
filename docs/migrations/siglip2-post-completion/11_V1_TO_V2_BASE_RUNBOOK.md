# Draft Runbook — VIP V1 Base to VIP V2 Base

**Information state:** `ADOPTED_STEP10_REFRESH` + `V1_EVIDENCE_REFRESHED` + `TASK0_NO_GO_BLOCKED` + `NOT_AUTHORIZED_FOR_EXECUTION`
**Target:** `google/siglip2-base-patch16-224`  
**Authority parent:** ADR-0002

## Purpose

Provide a future execution sequence that minimizes rediscovery after V1 completion.

This is a preparation runbook, not current permission to execute.

## 2026-10-11 Evidence Refresh (Step 10)

The evidence baseline is canonical main `748818e867ce08ccc2367bad21df7d83eaf51d70`; the separately preserved post-design V1 source is `3586eeaa904fc5a2e6a2745078611886f482f3de` (tree `a7fbe1b0dd1aa6c1dbcc14fda77e16b9958e7d0c`). V1 identity receipts report `google/siglip-base-patch16-224`, revision `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`, weights SHA-256 `2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8`, processor digest `4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980`, preprocessing digest `d11ccb80f15d358a11bdb070e92e2d889005874b7db15823d5f10d9b2533b14a`, 768-D float32/L2, and SemanticSpace ID `3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a`. V1 and V2 Base are distinct spaces despite both being 768-D.

Evidence is bounded: 811 distinct model-free passes and 1,290 separate G03 regression passes are recorded at `6396779e397dc9dba659f4887471de4c6d30aced` and G03 receipt `988b8790cc45ad1c1093f0d1ebbae15ab0716f38`; neither was rerun here. One authentic local synthetic V1 image/text MPS pass is recorded at `634bfed47aec8464c8ca61b15c376f2950c21060`. Runtime inventory `ce3f570016f3f13e9091fb6989f3a9d3ea783c7d` records F07 as `PASS_CURRENT_RUNTIME_RECEIPT_ONLY`; it does not establish bit-for-bit historical environment reconstruction. The Transformers warning's configuration-level explanation is recorded, but emitted IDs, embedding-table bounds, and text semantic correctness remain `NOT_OBSERVED`.

At the time of the original Step 10 edit, this refresh was proposed on the owner-review branch. It was adopted by PR #69, merged at `7f4a5ce1baf7de2aa580f1043502458336bf57fe`. The implementation plan is owner-approved for planning only; Task 0 remains `NO_GO_BLOCKED`, and separately scoped execution authority is outstanding. V2 Base revision, checkpoint/processor/preprocessing digests, approved local root, and V2 runtime proof are `BLOCKED`; do not fill them from mutable public pages.

## Entry Preconditions

Do not start this runbook until all are true:

- completed V1 Base has a verified immutable completion SHA/tag;
- `19_POST_COMPLETION_REFRESH_PROTOCOL.md` has refreshed this preparation pack against that SHA;
- current Superpowers brainstorming/design for the actual migration has been approved;
- an implementation plan exists;
- model acquisition has separate current authorization before any V2 checkpoint is downloaded/acquired;
- protected/archive-media execution has separate authorization before any real corpus is processed.
- the owner-approved plan is the exact accepted original blob `78127a9199a912531d5b2240eed66e93814d83f3` recorded on PR #69; its successor documentation blob is not represented as the accepted original. Planning approval does not authorize implementation.
- Task 0 is explicitly re-evaluated from its machine-readable gate matrix. A planning artifact or this runbook alone never clears implementation entry.

If any prerequisite is absent, stop with `BLOCKED`.

## Phase 0 — Preserve the V1 Baseline

1. Record the exact V1 completion SHA/tag.
2. Record current V1 model identity/revision/weights/processor/preprocessing identity.
3. Preserve the V1 reproducibility path required for later three-way benchmark.
4. Verify V1 regression suite at the completion state.
5. Do not rewrite historical V1 audit/run evidence.

Output: immutable V1 benchmark/reference candidate.

## Phase 1 — Refresh the Migration Surface

1. Re-run searches listed in `07_MIGRATION_SURFACE_SNAPSHOT.md`.
2. Reconcile all `08_HARDCODE_AND_ASSUMPTION_REGISTER.md` entries.
3. Identify any V1 changes made after the 2026-10-05 snapshots.
4. Update file/symbol references before implementation.
5. Confirm preserve boundaries remain intact.

Output: current, completion-SHA-bound migration surface.

## Phase 2 — Freeze the Exact V2 Base Contract

Only under separate acquisition authorization:

1. select an immutable upstream V2 Base revision;
2. acquire the checkpoint into an approved local immutable location;
3. calculate exact weights SHA-256;
4. inventory required processor/tokenizer/config assets;
5. calculate deterministic processor digest;
6. calculate image-preprocessing digest;
7. inspect exact checkpoint configuration;
8. verify expected embedding width from the frozen checkpoint/runtime;
9. record the exact SigLIP2 text preprocessing contract;
10. record the dependency/runtime environment.

Do not use mutable `main` as the runtime revision identity.

Output: fully resolved V2 Base profile with no `NOT_OBSERVED` runtime identity fields.

## Phase 3 — TDD the Model-Profile Boundary

Write failing tests before production changes for at least:

- V1 profile constructs the same semantic-space identity as the preserved baseline;
- V2 Base profile produces a different semantic-space identity even if dimension is also 768;
- processor/preprocessing differences change semantic-space identity;
- unresolved revision/hash/digest fails closed;
- unsupported profile/loader kind fails closed;
- session output width mismatch fails closed.

Implement only the minimal profile/contract abstraction needed to make those tests pass.

## Phase 4 — Add the SigLIP2 Runtime Path

Under the frozen V2 Base contract:

1. implement the approved SigLIP2 loader/processor path;
2. keep local-only loading;
3. keep remote-code execution disabled unless separately approved;
4. verify weights/processor/revision before and after runtime opening;
5. encode complete SigLIP2 text preprocessing;
6. preserve explicit CPU/MPS device selection;
7. preserve no-silent-fallback behavior;
8. validate image/text output width against the profile.

Do not alter source, temporal, editorial, render, or QC semantics.

## Phase 5 — Centralize Semantic-Space Construction

Replace duplicated V1-global construction in the representation runtime with the validated profile path.

Required result:

```text
validated profile
  -> validated local bundle
  -> model session
  -> exact SemanticSpace
  -> checked runtime
```

V1 and V2 Base should both remain representable without changing downstream retrieval interfaces unnecessarily.

## Phase 6 — Prepare for So400m Without Implementing It Yet

During V2 Base migration, remove only hard-coding that would otherwise force a second broad rewrite:

- global runtime dimension dependency;
- fixed vector-row width where it sits on generic write paths;
- fake-vector helpers that cannot express 1152 dimensions;
- duplicated semantic-space construction.

Do not implement So400m-specific runtime behavior in this phase.

## Phase 7 — Synthetic / Fixture Verification

Before real V2 inference:

- verify V1 768-D regression behavior;
- verify V2 Base profile identity isolation;
- verify generic storage/index/search accepts profile-derived 768-D geometry;
- verify mismatched semantic spaces fail before query/index mixing;
- verify authorization gates still precede real-runtime opening.

Synthetic success is compatibility evidence only.

## Phase 8 — Bounded Local V2 Base Smoke

Only with the applicable current model/runtime/media authorization:

1. load the frozen V2 Base model locally;
2. run a minimal bounded image/text embedding smoke;
3. verify output dimension;
4. verify finite/L2-normalized vectors under the VIP contract;
5. build/query a small isolated V2 Base index;
6. record runtime/device/memory/time evidence;
7. verify no V1 index/vector reuse occurred.

Do not run the full archive.

## Phase 9 — Regression and Completion Gate

Before declaring V2 Base migration complete:

- V1 preservation checks pass;
- V2 Base identity/provenance tests pass;
- model/profile tests pass;
- storage/index/search regression tests pass;
- relevant VIP FVS tests pass;
- authorization behavior passes;
- no forbidden downstream boundary changed;
- local V2 Base smoke evidence is recorded if execution was authorized;
- no claim of benchmark superiority is made.

Then freeze a reproducible V2 Base candidate SHA/tag for the next stage.

## Output of This Runbook

A successful run produces:

- preserved V1 Base;
- separately reproducible V2 Base;
- profile-aware representation boundary adequate for later So400m extension;
- no three-way winner claim;
- no full-archive re-indexing.
