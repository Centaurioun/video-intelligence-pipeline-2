# Semantic-Space and Index Strategy

**Information state:** `FROZEN_DECISION` + `INFERRED_DESIGN` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Authority parent:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`

## Purpose

Define how the three required candidates remain independently attributable and reproducible without mixing incompatible embeddings or forcing three permanently divergent applications.

## Core Rule

A semantic space is identified by the complete representation contract, not by vector width alone.

At minimum, compatibility depends on:

- model identity;
- frozen revision;
- model weights digest;
- processor digest;
- image-preprocessing digest;
- text-preprocessing contract;
- embedding dimension;
- dtype;
- normalization.

A change to any semantic-space field creates a different space.

## Required Candidate Spaces

The benchmark requires three independent spaces:

1. **VIP V1 Base** — `google/siglip-base-patch16-224`
2. **VIP V2 Base** — `google/siglip2-base-patch16-224`
3. **VIP V2 So400m** — `google/siglip2-so400m-patch14-384`

V1 Base and V2 Base may both use 768-dimensional vectors, but their coordinates are not interchangeable.

V2 So400m uses a different model contract and expected 1152-dimensional output.

## Index Isolation

Preferred future layout is separate index roots or another equally explicit operator-visible isolation boundary.

Conceptually:

```text
index-v1-base/
index-v2-base/
index-v2-so400m/
```

Exact names are not frozen.

What is frozen is the rule that a runtime must not silently adopt a generation built for another semantic space.

## Existing V1 Behavior to Preserve

The current persistent index already:

- derives deterministic semantic-space IDs;
- derives generation IDs from semantic space plus sampling policy;
- validates manifest compatibility;
- rejects incompatible sibling semantic spaces in one index root;
- stores semantic-space fields in the generation manifest;
- keeps committed vector bytes/rows attributable to one generation.

Future migration should reuse this discipline rather than creating a weaker parallel mechanism.

## No Automatic Cross-Space Migration

There is no valid byte-level migration from V1 vectors to V2 vectors.

Moving from one candidate to another requires re-embedding the same source sample frames under the new model.

Forbidden shortcuts include:

- copying `vectors.f32` into another candidate index;
- treating equal 768-D widths as compatible;
- applying a mathematical transform without separately validated research;
- modifying only the manifest identity while preserving old vectors.

## Shared Source Sampling, Separate Embeddings

For fair benchmarking, the preferred comparison envelope is:

```text
same frozen source
same measured source-native PTS/sample positions
        |
        +--> V1 Base embeddings/index
        +--> V2 Base embeddings/index
        +--> V2 So400m embeddings/index
```

This isolates model representation as the main changed factor.

The sampled frame evidence may be reused as a frozen benchmark input artifact only if that artifact is explicitly designed, attributable to the same source/PTS positions, and separately authorized. Current production indexing does not automatically provide a shared cross-model frame cache.

## Score Interpretation

Within one semantic space, exact cosine ranking remains meaningful under that space's normalization contract.

Across different semantic spaces:

- raw cosine score magnitudes are not directly comparable quality metrics;
- a V2 score of 0.42 is not inherently better/worse than a V1 score of 0.42;
- benchmark comparison should use shared outcomes such as rank, relevance, Recall@K, nDCG, human/editorial usefulness, and operational cost.

## Query Isolation

A text query must be embedded by the same semantic model/profile used to create the candidate image vectors.

Fail closed if:

- model/profile identity differs;
- embedding dimensions differ;
- semantic-space identity differs;
- query vector width differs from index vector width.

Do not build a compatibility shim that silently projects one query space into another.

## Generation and Sampling Identity

A generation should continue to bind:

- semantic-space identity;
- sampling-policy identity;
- sampling interval/policy version;
- selected-stream policy.

A model change creates a new semantic space and therefore a new generation identity even if the sampling policy is unchanged.

## Benchmark Index Policy

For the future three-way benchmark:

- create one isolated index per candidate;
- use one frozen corpus;
- use one frozen sampling policy;
- use identical measured PTS/sample positions as far as technically applicable;
- never append a candidate's vectors into another candidate's index;
- record index/generation/space identifiers in benchmark run manifests;
- preserve the candidate code SHA and model/runtime identity.

## Full-Archive Policy

The full approximately 400-hour archive is not to be indexed with all three candidates merely to compare them.

Required order:

`small frozen benchmark -> representation decision -> separately authorized full-archive indexing`

If later evidence supports keeping both SigLIP2 profiles operational, their indexes still remain separate semantic spaces.

## Rebuild / Rollback Rule

Indexes are derived artifacts.

If a model/profile contract changes:

- do not mutate old semantic-space identity in place;
- create a new space/generation;
- preserve old candidate evidence long enough for rollback/reproducibility;
- rebuild only under applicable authorization.

## Non-Goals

This strategy does not introduce:

- cross-model vector conversion;
- mixed-space nearest-neighbor search;
- ensemble ranking;
- ANN/vector-database adoption;
- automatic archive-scale migration;
- model auto-selection.

Those would require separate evidence and design decisions.
