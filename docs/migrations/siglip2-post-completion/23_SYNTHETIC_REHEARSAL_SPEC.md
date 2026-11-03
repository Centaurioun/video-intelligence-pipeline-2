# Synthetic Compatibility Rehearsal Specification

**Information state:** `INFERRED_DESIGN` + `TEMPLATE` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`

## Purpose

Define a future, low-cost compatibility probe that can test whether generic vector storage/index/query paths support both 768-D and 1152-D embeddings before real SigLIP2 model execution.

This document specifies behavior only.

No rehearsal code is created by the preparation project.

## What the Rehearsal Can Prove

It may prove that:

- vector width can be profile-derived;
- float32 row-byte accounting works for 768 and 1152 dimensions;
- storage append/commit/recovery logic is dimension-aware;
- search/memmap shape is dimension-aware;
- fake embeddings can be generated deterministically for both widths;
- mismatched query/index dimensions fail closed;
- incompatible semantic spaces fail closed.

## What It Cannot Prove

It cannot prove:

- SigLIP2 model loading works;
- SigLIP2 retrieval quality;
- MPS performance;
- actual model memory requirements;
- processor/tokenizer correctness;
- 384-pixel real image preprocessing;
- full-archive throughput;
- benchmark superiority.

Any such claim remains `NOT_OBSERVED`.

## Preconditions

Before implementing the rehearsal:

- V1 completion state is frozen;
- migration surface is refreshed;
- the actual migration design is approved;
- test locations/commands are mapped to final V1;
- no real model assets are required for the rehearsal.

## Synthetic Profiles

### S1 — 768-D Base-like profile

- embedding dimension: 768
- dtype: float32
- row width: 3072 bytes
- normalization: L2
- semantic-space identity: synthetic unique identity

### S2 — 1152-D So400m-like profile

- embedding dimension: 1152
- dtype: float32
- row width: 4608 bytes
- normalization: L2
- semantic-space identity: different synthetic unique identity

The profiles must differ in semantic identity, not only dimension.

## Deterministic Fake Vector Rule

Use a deterministic seed/input identity so repeated generation of the same fixture yields byte-equivalent float32 vectors after normalization where the current test contract expects determinism.

The exact generator algorithm should be chosen during implementation and frozen by tests.

Do not use random unseeded vectors.

## Required Scenarios

### SR01 — 768-D append and query

Create a small synthetic generation with S1.

Expected:

- committed byte length = rows × 3072;
- query vector has 768 columns;
- exact scan returns deterministic ranking.

### SR02 — 1152-D append and query

Create equivalent S2 generation.

Expected:

- committed byte length = rows × 4608;
- query vector has 1152 columns;
- exact scan returns deterministic ranking.

### SR03 — Wrong query width

Attempt 768-D query against 1152-D generation and inverse.

Expected:

- explicit dimension mismatch;
- no truncation/padding;
- no scoring.

### SR04 — Cross-space same-width rejection

Create two distinct 768-D semantic spaces.

Expected:

- equal vector width does not bypass semantic-space mismatch.

This is the synthetic analogue of V1 Base vs V2 Base.

### SR05 — Tail recovery at 1152-D

Append an interrupted/uncommitted byte tail to a synthetic S2 vector file.

Expected:

- authoritative committed boundary remains unchanged;
- recovery uses 4608-byte row width;
- partial/foreign tail is never searchable.

### SR06 — Generation identity

Use the same sampling policy with S1 and a second distinct 768-D space.

Expected:

- generation IDs differ because semantic-space IDs differ.

### SR07 — Fake-vector determinism

Generate the same synthetic rows twice for each profile.

Expected:

- exact repeated output under the test contract;
- finite values;
- expected shape.

### SR08 — Dtype guard

If final design supports only float32, attempt an unsupported dtype.

Expected:

- fail closed instead of silently treating element width as 4 bytes.

Do not add generic dtype support just to satisfy this scenario.

## Suggested Fixture Scale

Keep the rehearsal tiny:

- 3–10 rows per case;
- no media files required;
- no model weights;
- no network;
- temporary test directories only.

The objective is shape/contract validation, not performance benchmarking.

## TDD Requirement

When implemented later:

1. write the failing 1152-D/cross-space tests first;
2. observe the expected failure against the final V1/V2-Base code;
3. implement the smallest dimension/profile change;
4. make tests pass;
5. rerun relevant V1 regression tests.

## Exit Criteria

The rehearsal passes when all required scenarios pass and no production behavior outside the representation/storage/search boundary changes.

A passing rehearsal makes So400m plumbing **eligible for real-model smoke testing**.

It does not make So400m benchmark-eligible until the real model/profile acceptance checks pass.
