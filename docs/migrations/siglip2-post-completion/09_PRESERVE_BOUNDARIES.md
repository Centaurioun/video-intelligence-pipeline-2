# Preserve Boundaries — What Model Migration Must Not Redesign

**Information state:** `FROZEN_DECISION` + `VERIFIED_CURRENT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Authority parent:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`

## Purpose

SigLIP2 migration changes the semantic retrieval representation.

It does **not** authorize a broad rewrite of the Video Intelligence Pipeline.

This document defines boundaries that future migration work should preserve unless a separate, evidence-backed design explicitly reopens them.

## Preserve 1 — Source Media Immutability

Source media remains immutable unless an explicitly approved policy says otherwise.

Model migration may:

- read authorized source frames;
- create derived embeddings/index artifacts;
- create bounded derived benchmark artifacts under later authorization.

Model migration must not:

- rewrite source media;
- normalize/canonicalize source files in place;
- delete or demote source files because a representation changes;
- change source identity to fit the new model.

## Preserve 2 — Source-Native Temporal Authority

Semantic retrieval produces candidate moments, not exact edit boundaries.

Exact temporal work continues to require source-native evidence such as:

- integer PTS;
- source timebase;
- measured presentation ordering;
- source-native refinement evidence.

Never infer VFR frame position as:

`seconds × nominal FPS`

A stronger semantic model does not gain frame-accuracy authority.

## Preserve 3 — Evidence Classes

The canonical assertion-level evidence classes remain:

- `MEASURED`;
- `MATCHED`;
- `VISUALLY_OBSERVED`;
- `AUDIO_OBSERVED`;
- `EDITORIAL_INFERENCE`.

`NOT_OBSERVED` remains an availability/state marker.

Model migration must not silently promote:

- public benchmark claims → local measured evidence;
- high similarity → visual observation;
- semantic timestamp → measured edit boundary;
- model confidence → editorial decision.

## Preserve 4 — Semantic Space Isolation

Every materially different model/revision/processor/preprocessing contract remains a separate semantic space.

Preserve fail-closed behavior for:

- model identity mismatch;
- revision mismatch;
- weights mismatch;
- processor mismatch;
- preprocessing mismatch;
- embedding dimension mismatch;
- dtype/normalization mismatch where part of the contract.

No migration path may silently reinterpret old vectors as new-model vectors.

## Preserve 5 — Deterministic Source Inventory and Provenance

Model migration should consume existing deterministic source identity/provenance rather than inventing a second source-tracking system.

Preserve attribution for:

- source digest;
- source revision;
- model identity;
- model revision;
- model weights digest;
- processor/preprocessing identity;
- semantic-space identity;
- generation/run identity;
- relevant policy/authorization.

## Preserve 6 — Sampling and Refinement Are Separate from Representation Quality

For the three-way comparison, the same measured sample positions should be used as far as technically applicable.

Changing the model is not permission to change sampling in a way that confounds the comparison.

If a later experiment intentionally studies sampling density, that is a separate factor and should not be mixed into the model benchmark.

## Preserve 7 — Human Editorial Decision Boundary

Retrieval output remains candidate evidence for a human/editorial decision.

Model migration must not collapse:

`semantic retrieval -> candidate -> refinement -> human editorial decision`

into an automated edit-decision path merely because retrieval improves.

## Preserve 8 — Edit Plan Semantics

Existing edit-plan/version/provenance concepts should remain representation-independent.

The model that discovered a candidate may be attributable evidence, but it should not redefine what an edit plan means.

## Preserve 9 — Render / Export Authorization

A new semantic representation does not authorize:

- production renders;
- real-media exports;
- destructive output replacement;
- expanded codec/container policy.

Rendering/export remains governed by its own authorization and QC contracts.

## Preserve 10 — Technical and Editorial QC

Technical QC and editorial QC remain downstream checks.

Do not redefine QC thresholds solely to make one candidate representation appear superior.

Model benchmark success is retrieval evidence, not automatic render/QC approval.

## Preserve 11 — Gate Architecture

ADR-0002 records committed post-completion work but does not itself promote a Gate.

The existing Gate meanings remain:

- Gate 0 — bounded diagnostic retrieval;
- Gate 1 — representation/capability benchmark;
- Gate 2 — reliability/scale;
- Gate 3 — editing/QC.

Future work may overlap only where separately authorized; evidence-dependent promotion remains a hard gate.

## Preserve 12 — V1 Reproducibility

The completed V1 Base state must remain reproducible long enough to benchmark against both SigLIP2 candidates.

Migration must not destructively overwrite:

- the V1 completion SHA/tag;
- V1 model identity;
- V1 index/semantic-space evidence required for the benchmark;
- V1 test/evidence history.

Long-term active support may later end, but historical reproducibility is distinct from active maintenance.

## Preserve 13 — Current Authorization Discipline

Preparation documents are not execution authority.

Future agents must still distinguish:

- documentation/design work;
- model acquisition;
- local synthetic execution;
- protected/archive-media execution;
- full-archive indexing;
- production promotion.

When authority is unclear, fail closed.

## Allowed Representation-Focused Changes

The preserve boundaries do not forbid the changes actually required by ADR-0002.

Future migration may legitimately alter:

- model loader/processor integration;
- model profile/configuration;
- semantic-space identity inputs;
- text/image preprocessing contract;
- embedding dimension handling;
- vector row-width derivation;
- model-specific tests/fixtures;
- model-specific performance measurements.

Those changes should remain as local to the representation boundary as practical.

## Reconsideration Rule

A preserve boundary may be reopened only when:

1. the migration cannot be implemented correctly without doing so;
2. the dependency is demonstrated with current repository evidence;
3. alternatives that keep the boundary intact are evaluated;
4. the broader change receives the appropriate design/authorization.

“While we are here” is not sufficient justification.
