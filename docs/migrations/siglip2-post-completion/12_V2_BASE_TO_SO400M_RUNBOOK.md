# Draft Runbook — VIP V2 Base to VIP V2 So400m

**Information state:** `ADOPTED_STEP10_REFRESH` + `V1_EVIDENCE_REFRESHED` + `TASK0_NO_GO_BLOCKED` + `NOT_AUTHORIZED_FOR_EXECUTION`
**Target:** `google/siglip2-so400m-patch14-384`  
**Authority parent:** ADR-0002

## Purpose

Extend an already verified V2 Base implementation to the larger fixed-resolution SigLIP2 So400m candidate without cloning the application or reopening unrelated architecture.

## 2026-10-11 Evidence Refresh (Step 10)

V1 remains a separate 768-D semantic space identified by preserved source `3586eeaa904fc5a2e6a2745078611886f482f3de` and SemanticSpace `3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a`. V2 Base is also expected to be 768-D but must have a distinct frozen identity and index. SO400M is the separate 1152-D profile. Do not reuse vectors or compare raw cosine magnitudes across these spaces.

Planning evidence identifies SO400M as `google/siglip2-so400m-patch14-384`, pinned source revision `c65677ac77ca25276518923f7c58cbf5d81ea602`, checkpoint SHA-256 `9f4f4a49f908ef0c979bce8ff5a5c0e88882dc6c5dc4304387cbbd152558e2c2`, 384-pixel input, patch size 14, and 1152-D output. These are pinned planning/source facts, not evidence of acquired local bytes or current VIP runtime. Current E01–E10 source refresh is recorded at `229d08f564fb8c21a7a119fc900eaac82cb64cd0`; mutable public pages do not replace the pinned source or acquired local identity. FP16/FP32 remain separately identified; Q4 evidence is historical and Q8 is `NOT_VERIFIED`.

The shared BOS/EOS warning does not establish a shared cause: current public SO400M config reports vocabulary size 256000, while the historical warning reported 0..31999. Exact checkpoint tokenizer output, special-token mapping, attention mask, pooling position, and text embedding-table size remain unobserved. Preserve the existing fail-closed semantic-validation gate; do not rewrite token IDs by inference. At the time of the original Step 10 edit, the evidence refresh was proposed; it was adopted by PR #69, merged at `7f4a5ce1baf7de2aa580f1043502458336bf57fe`. Owner approval is for planning only and authorizes no asset acquisition, inference, or media.

## Entry Preconditions

Do not begin until:

- V1 Base remains reproducible;
- V2 Base migration is independently verified;
- the final V2 Base candidate SHA/tag is frozen;
- the representation/profile boundary exists and is validated;
- exact So400m model acquisition has separate current authorization before model bytes are acquired;
- any real-media execution has separate authorization.

If V2 Base still relies on hidden Base-only assumptions, fix those before introducing So400m.
- Owner acceptance of the revised plan, a verified frozen V2 Base candidate SHA, and current task-specific authorization are mandatory. If any is absent, remain `BLOCKED`.

## Phase 1 — Freeze the So400m Contract

Under separate model-acquisition authorization:

1. select an immutable So400m revision;
2. acquire the exact local checkpoint;
3. hash weights;
4. inventory/hash processor assets;
5. hash image preprocessing;
6. inspect exact model config;
7. confirm 384 image size;
8. confirm patch size 14;
9. confirm 1152-dimensional retrieval output;
10. record runtime/dependency environment.

Official checkpoint facts are planning evidence; the frozen acquired checkpoint is runtime authority.

## Phase 2 — Add the So400m Profile

Add the new profile to the already-validated V2 profile boundary.

No duplicated application should be necessary.

The So400m profile must have its own:

- model ID;
- revision;
- weights digest;
- processor digest;
- preprocessing digest;
- geometry;
- semantic-space identity.

It must not point at the V2 Base index root/generation.

## Phase 3 — Prove Generic 1152-D Plumbing First

Before real model inference, use synthetic/fake vectors to prove the generic vector path handles 1152 dimensions.

Required expectations:

- row width is 4608 bytes for float32 1152-D vectors;
- append/commit accounting uses the profile-derived row width;
- crash-tail reconciliation uses the same width;
- query memmap shape uses 1152 columns;
- exact scan rejects 768-D query vectors against 1152-D spaces;
- semantic-space mismatch remains fail-closed;
- synthetic fake vectors remain deterministic at 1152-D.

If this requires widespread representation-independent changes, stop and revisit the V2 Base profile design rather than forking the pipeline.

## Phase 4 — Verify 384-Pixel Image Preprocessing

Test the acquired processor contract:

- expected fixed input size 384 × 384;
- processor digest/asset inventory matches the frozen bundle;
- preprocessing identity differs appropriately from V2 Base;
- image path/output handling remains deterministic;
- no manual resize path bypasses the processor contract.

Do not change source media; resizing is model input preprocessing only.

## Phase 5 — Bounded So400m Runtime Smoke

Only under applicable authorization:

1. load exact local So400m checkpoint;
2. verify explicit target device;
3. embed a bounded image/text fixture set;
4. verify output width 1152;
5. verify finite/L2-normalized vectors under the VIP contract;
6. record model-load latency;
7. record bounded embedding throughput;
8. record peak memory where measurable;
9. build/query a small isolated So400m index.

Do not extrapolate this smoke as full-archive timing proof.

## Phase 6 — Cross-Candidate Isolation Tests

Prove:

- V1 Base vectors cannot enter V2 Base or V2 So400m generations;
- V2 Base vectors cannot enter So400m generations;
- V2 So400m query vectors cannot be scored against V2 Base vectors;
- index roots/generations are attributable to exact profile identity;
- identical source/sample positions can be represented independently in all three spaces.

## Phase 7 — Regression Gate

Before declaring the So400m extension complete:

- V1 regression behavior remains reproducible;
- V2 Base remains independently runnable;
- 1152-D synthetic storage/index/search tests pass;
- So400m loader/profile/provenance tests pass;
- 384 preprocessing tests pass;
- explicit device/offline behavior passes;
- no unrelated temporal/editorial/render/QC behavior changed;
- no benchmark winner claim is made.

Freeze a reproducible So400m candidate SHA/tag.

## Phase 8 — Hand Off to Benchmark Preparation

Once all three candidates are reproducible:

1. do not index the full archive;
2. activate the frozen small-corpus benchmark protocol;
3. freeze corpus/query/relevance/metric/winner rules before comparative interpretation;
4. run the three candidates under the same source/sample envelope;
5. use project-specific evidence to decide the preferred representation.

## Output of This Runbook

A successful run produces a third reproducible candidate, not a production winner.

The intended architectural result is one V2 implementation capable of validated V2 Base and V2 So400m profiles where the final code naturally supports that shape.
