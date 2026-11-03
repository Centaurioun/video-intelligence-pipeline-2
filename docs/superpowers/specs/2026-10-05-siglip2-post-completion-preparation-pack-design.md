# SigLIP2 Post-Completion Preparation Pack Design

**Date:** 2026-10-05  
**Status:** IMPLEMENTED — original preparation design completed; package remains dormant and execution-unapproved  
**Authority parent:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`  
**Current implementation baseline snapshot:** `main@c818ae7ff32571161757c367b2ec79eb717775c6` (`SNAPSHOT`; reverify before later execution)  
**Execution effect:** none; this design does not authorize SigLIP2 implementation, model acquisition, protected/archive-media execution, or full-archive indexing

---

## Implementation Reconciliation

The original design was implemented and final-audited through PR #51. The original package contained 45 planned artifacts: 29 migration-preparation artifacts and 16 benchmark-preparation artifacts.

A later owner-authorized six-cycle hardening pass adds four **supplemental** artifacts without changing ADR-0002's migration direction:

- `docs/migrations/siglip2-post-completion/29_SIX_CYCLE_HARDENING_AUDIT.md`
- `docs/migrations/siglip2-post-completion/30_post-completion-refresh-receipt-template.yaml`
- `docs/benchmarks/siglip-three-way/B16_PRE_EXECUTION_FREEZE_CHECKLIST.md`
- `docs/benchmarks/siglip-three-way/B17_sample-plan-template.csv`

These supplements close documentation lifecycle, post-completion refresh receipt, benchmark pre-freeze, and exact source-native sample-plan gaps identified after the original plan completed. They do not authorize model acquisition, migration implementation, protected-media execution, or full-archive indexing.

## 1. Purpose

Prepare a durable, high-signal documentation and template package that reduces the amount of rediscovery, research, planning, and benchmark-design work required after the current SigLIP1 Base Video Intelligence Pipeline reaches its verified completion boundary.

The preparation package is intentionally created **before** V1 completion, but it must not alter current product code, tests, runtime behavior, dependency state, model assets, or the active Remaining Work execution frontier.

The package exists to make the future transition:

`V1 Base -> V2 Base -> V2 So400m -> three-way benchmark -> representation decision`

faster, safer, more reproducible, and less dependent on conversational memory.

---

## 2. Governing Constraints

The package must preserve the following boundaries:

- current V1 implementation work continues independently;
- no existing production Python files are modified as part of this preparation effort;
- no existing tests are modified as part of this preparation effort;
- no SigLIP2 checkpoint/model download is authorized;
- no real or protected archive media is processed;
- no MPS/model inference run is authorized;
- no 400-hour archive indexing is authorized;
- no Gate promotion is implied;
- no semantic/model timestamp gains temporal authority;
- source-native PTS/timebase discipline remains unchanged;
- incompatible semantic spaces remain separate;
- current repository evidence supersedes stale snapshots.

The preparation pack may contain designs, runbooks, manifests, checklists, templates, source receipts, future prompts, and synthetic-rehearsal specifications.

---

## 3. Design Principle

The package is optimized for a future ChatGPT/Codex session that starts after V1 completion.

That future session should not need to rediscover from scratch:

- why these three candidates were selected;
- what must remain unchanged;
- where model-specific assumptions exist in V1;
- which facts are durable versus stale snapshots;
- what the target SigLIP2 contracts are;
- how to prepare and verify each migration;
- how to benchmark the three candidates fairly;
- what evidence is needed before declaring a winner.

The package should reduce repeated reasoning, not replace final verification.

---

## 4. Information-State Labels

Every preparation document should use one or more explicit information-state labels where appropriate:

- **FROZEN_DECISION** — accepted project decision or invariant; not to be silently reinterpreted.
- **VERIFIED_CURRENT** — verified against current canonical repository state when written.
- **SNAPSHOT** — accurate when captured but expected to drift as V1 evolves.
- **REVERIFY_AT_V1_COMPLETION** — must be rechecked before migration work begins.
- **OFFICIAL_EXTERNAL** — supported by an official primary external source such as a model card, Transformers documentation, or the SigLIP2 paper.
- **INFERRED_DESIGN** — proposed future architecture or workflow, not yet implemented.
- **TEMPLATE** — intentionally incomplete structure to be filled later.
- **NOT_AUTHORIZED_FOR_EXECUTION** — preparation exists, but execution remains deferred.

No snapshot may be presented later as current fact without the required refresh.

---

## 5. Package Layout

The preparation work is split into two cooperating packages.

### 5.1 Migration preparation package

Target path:

`docs/migrations/siglip2-post-completion/`

Planned artifacts:

1. `00_README_AND_ENTRYPOINT.md`
2. `01_AUTHORITY_SCOPE_AND_ACTIVATION.md`
3. `02_PACKAGE_MANIFEST.yaml`
4. `03_V1_BASELINE_SNAPSHOT.md`
5. `04_MODEL_CONTRACTS.md`
6. `05_model-contracts.yaml`
7. `06_MODEL_COMPATIBILITY_MATRIX.md`
8. `07_MIGRATION_SURFACE_SNAPSHOT.md`
9. `08_HARDCODE_AND_ASSUMPTION_REGISTER.md`
10. `09_PRESERVE_BOUNDARIES.md`
11. `10_TARGET_MODEL_PROFILE_DESIGN.md`
12. `11_V1_TO_V2_BASE_RUNBOOK.md`
13. `12_V2_BASE_TO_SO400M_RUNBOOK.md`
14. `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md`
15. `14_TEST_AND_ACCEPTANCE_MATRIX.md`
16. `15_SEMANTIC_SPACE_INDEX_STRATEGY.md`
17. `16_VERSION_PRESERVATION_AND_ROLLBACK.md`
18. `17_RISK_REGISTER.md`
19. `18_STALENESS_AND_REVERIFY_REGISTER.md`
20. `19_POST_COMPLETION_REFRESH_PROTOCOL.md`
21. `20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md`
22. `21_source-receipts.yaml`
23. `22_REJECTED_ALTERNATIVES_AND_RECONSIDERATION_TRIGGERS.md`
24. `23_SYNTHETIC_REHEARSAL_SPEC.md`
25. `24_FUTURE_CODEX_LAUNCH_PACKET.md`
26. `25_FUTURE_CHATGPT_ORCHESTRATOR_HANDOFF.md`
27. `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`
28. `27_POST_MIGRATION_VERIFICATION_CHECKLIST.md`
29. `28_CHANGELOG.md`

### 5.2 Three-way benchmark package

Target path:

`docs/benchmarks/siglip-three-way/`

Planned artifacts:

1. `B00_BENCHMARK_CHARTER.md`
2. `B01_CORPUS_SELECTION_AND_FREEZE_PROTOCOL.md`
3. `B02_corpus-manifest-template.yaml`
4. `B03_QUERY_TAXONOMY.md`
5. `B04_query-set-template.csv`
6. `B05_RELEVANCE_AND_ANNOTATION_GUIDE.md`
7. `B06_relevance-judgment-template.csv`
8. `B07_METRICS_AND_STATISTICAL_PROTOCOL.md`
9. `B08_PERFORMANCE_AND_RESOURCE_PROTOCOL.md`
10. `B09_BENCHMARK_EXECUTION_PROTOCOL.md`
11. `B10_result-schema.json`
12. `B11_benchmark-run-manifest-template.yaml`
13. `B12_BENCHMARK_REPORT_TEMPLATE.md`
14. `B13_WINNER_DECISION_RULES.md`
15. `B14_FAILURE_MODES_AND_BIAS_CHECKLIST.md`
16. `B15_BENCHMARK_AUDIT_CHECKLIST.md`

The benchmark package is subordinate to ADR-0002 and the migration package's authority/scope rules.

---

## 6. Candidate Set

The required comparison set is fixed by ADR-0002:

- **VIP V1 Base** — `google/siglip-base-patch16-224`
- **VIP V2 Base** — `google/siglip2-base-patch16-224`
- **VIP V2 So400m** — `google/siglip2-so400m-patch14-384`

SigLIP1 So400m is not a required benchmark arm.

It may only be reconsidered if a later question specifically requires separating model-scale effects from SigLIP-generation effects.

---

## 7. Source and Evidence Policy

External technical facts should preferentially be grounded in primary sources:

- official Hugging Face model cards and file/config metadata;
- official Transformers SigLIP/SigLIP2 documentation;
- the SigLIP2 paper;
- current repository code and tests for V1 implementation facts.

Each external source receipt should record:

- source URL;
- title;
- access/retrieval date;
- authority class;
- the exact assertion(s) it supports;
- whether the assertion is durable or should be reverified later.

Model popularity, likes, downloads, or public benchmark scores may justify investigation but do not decide project adoption.

---

## 8. Snapshot Discipline

Repository-specific artifacts created before V1 completion are snapshots, not frozen implementation truth.

At minimum, the following should be marked `REVERIFY_AT_V1_COMPLETION`:

- file paths;
- symbol names;
- hard-coded dimensions/constants;
- loader classes;
- processor/tokenizer call sites;
- dependency versions;
- tests affected by model assumptions;
- current model/runtime invocation seams.

The preparation pack must include a dedicated refresh protocol so that future work begins with a bounded delta audit rather than blindly trusting pre-completion snapshots.

---

## 9. Model-Contract Scope

The model-contract records should capture, where supported:

- model identity;
- revision status;
- weights digest status;
- processor/tokenizer identity;
- image input size;
- patch size;
- embedding dimension;
- dtype;
- vector normalization;
- text preprocessing contract;
- image preprocessing contract;
- expected loader/API family;
- semantic-space incompatibility notes;
- model/package storage observations;
- runtime/device constraints where actually verified.

Unknown future checkpoint revisions and hashes must remain explicitly unresolved until acquisition is separately authorized.

---

## 10. Migration-Surface Audit Scope

The V1 migration-surface snapshot should identify the current code/test locations that encode model-specific assumptions, including where relevant:

- model loader classes;
- processor classes;
- frozen model identity;
- embedding dimension;
- vector row width;
- vector validation;
- fake/synthetic embedding width;
- search/index dimensionality assumptions;
- preprocessing contracts;
- processor asset lists;
- model provenance structures;
- CLI/configuration bindings;
- tests that pin those assumptions.

The audit must distinguish:

- **must change for V2 Base**;
- **must change only for So400m**;
- **already dimension/model-aware**;
- **must not change because it belongs to unrelated pipeline layers**.

---

## 11. Future Model-Profile Design Boundary

The preparation package may define a small future `ModelProfile` concept, but it must remain YAGNI-constrained.

Its purpose is only to support the accepted candidate set and remove unnecessary hard-coding.

A conceptual profile may include fields such as:

- model ID;
- frozen revision;
- weights digest;
- processor digest;
- image-preprocessing digest;
- text-preprocessing contract;
- image size;
- patch size;
- embedding dimension;
- dtype;
- normalization.

The design must not become an unrestricted provider/model plugin framework unless later evidence justifies that expansion.

---

## 12. Benchmark Design Principles

The benchmark should compare the three candidates on one frozen, representative, project-specific corpus rather than full-archive indexing.

Expected corpus scale:

**approximately 10-20 representative videos**

The exact corpus will be frozen later.

All candidate arms should receive, as far as technically applicable:

- the same source revisions;
- the same sampling policy;
- the same measured source-native sample positions;
- the same query set;
- the same relevance judgments;
- the same evaluation rules.

Candidate vector spaces remain separate.

Raw cosine values across model spaces are not quality metrics.

---

## 13. Benchmark Evaluation Scope

The benchmark preparation should support both retrieval quality and operational cost.

Planned measures include:

- Top-1 retrieval success;
- Recall@5;
- Recall@10 where useful;
- nDCG or another declared ranking metric where appropriate;
- editorial/human usefulness;
- irrelevant-result behavior;
- Turkish query behavior;
- English query behavior;
- indexing wall-clock time;
- model-load/cold-start behavior;
- warm-query latency;
- peak/runtime memory;
- model storage;
- persistent vector/index storage;
- stability and reproducibility.

The benchmark protocol must define aggregation and scoring before results are used for a winner decision.

---

## 14. Bias and Goalpost Protection

The benchmark package should explicitly guard against:

- overrepresentation of one visual category;
- one-video dominance;
- query leakage;
- cherry-picked successful examples;
- post-hoc metric changes;
- post-hoc corpus changes;
- changing relevance labels after inspecting model outputs;
- comparing different sampling positions between models;
- treating larger-model cost as irrelevant;
- treating public benchmark superiority as local proof.

Winner rules should be frozen before final comparative interpretation.

---

## 15. Future Handoff Design

The package should contain two distinct future handoffs.

### Future Codex Launch Packet

A compact executable-oriented handoff that tells Codex what to read, what to verify, what remains deferred, what migration sequence to follow, and which completion SHA becomes the authoritative starting point.

It must not embed stale current paths without a refresh step.

### Future ChatGPT Orchestrator Handoff

A coordination-oriented handoff that tells a future ChatGPT session how to:

1. bootstrap from repository authority;
2. run the post-completion refresh protocol;
3. verify the V1 completion boundary;
4. invoke Superpowers brainstorming for the actual migration design;
5. write/update the implementation plan only after that design is approved;
6. execute V1 -> V2 Base;
7. verify;
8. execute V2 Base -> So400m;
9. verify;
10. run the frozen three-way benchmark;
11. record the winner decision.

---

## 16. Synthetic Rehearsal Boundary

A synthetic rehearsal may later test whether storage/index/search paths tolerate both 768-D and 1152-D fake vectors without requiring real model inference or archive media.

At this preparation stage:

- the rehearsal specification may be written;
- rehearsal code is not part of this documentation package;
- no product code is changed;
- no model is downloaded;
- no benchmark claim may be derived from synthetic rehearsal performance.

The rehearsal is a compatibility probe only.

---

## 17. Batch Production Strategy

The package will be created in small batches to avoid long-running tool calls and timeout risk.

Preferred creation order:

### Batch 1 — Authority and entrypoint
- `00_README_AND_ENTRYPOINT.md`
- `01_AUTHORITY_SCOPE_AND_ACTIVATION.md`
- `02_PACKAGE_MANIFEST.yaml`
- `03_V1_BASELINE_SNAPSHOT.md`
- `04_MODEL_CONTRACTS.md`

### Batch 2 — Machine-readable contracts and migration map
- `05_model-contracts.yaml`
- `06_MODEL_COMPATIBILITY_MATRIX.md`
- `07_MIGRATION_SURFACE_SNAPSHOT.md`
- `08_HARDCODE_AND_ASSUMPTION_REGISTER.md`
- `09_PRESERVE_BOUNDARIES.md`

### Batch 3 — Target design and runbooks
- `10_TARGET_MODEL_PROFILE_DESIGN.md`
- `11_V1_TO_V2_BASE_RUNBOOK.md`
- `12_V2_BASE_TO_SO400M_RUNBOOK.md`
- `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md`
- `14_TEST_AND_ACCEPTANCE_MATRIX.md`

### Batch 4 — Isolation, risk, refresh, evidence
- `15_SEMANTIC_SPACE_INDEX_STRATEGY.md`
- `16_VERSION_PRESERVATION_AND_ROLLBACK.md`
- `17_RISK_REGISTER.md`
- `18_STALENESS_AND_REVERIFY_REGISTER.md`
- `19_POST_COMPLETION_REFRESH_PROTOCOL.md`
- `20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md`
- `21_source-receipts.yaml`

### Batch 5 — Future handoff and verification
- `22_REJECTED_ALTERNATIVES_AND_RECONSIDERATION_TRIGGERS.md`
- `23_SYNTHETIC_REHEARSAL_SPEC.md`
- `24_FUTURE_CODEX_LAUNCH_PACKET.md`
- `25_FUTURE_CHATGPT_ORCHESTRATOR_HANDOFF.md`
- `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`
- `27_POST_MIGRATION_VERIFICATION_CHECKLIST.md`
- `28_CHANGELOG.md`

### Batch 6 onward — benchmark package
Create the `B00`-`B15` benchmark artifacts in similarly bounded groups.

The owner may simply say “continue” to advance to the next agreed batch.

---

## 18. Verification Requirements for Preparation Files

Before any batch is declared complete:

- confirm only intended new documentation/template paths changed;
- confirm no production code or test file changed;
- scan for accidental authorization widening;
- scan for unsupported claims stated as measured/verified;
- ensure snapshot material is labeled correctly;
- ensure no secrets, credentials, model weights, binary assets, or protected-media identifiers are committed;
- ensure internal references point to real repository paths or are clearly marked future paths;
- read back the committed files from canonical `main` after merge.

A documentation batch may be complete even when some future values remain intentionally unavailable, provided they are marked as template/deferred rather than guessed.

---

## 19. Post-Completion Activation Sequence

After V1 reaches its verified completion boundary:

1. freeze/preserve V1 completion SHA/tag;
2. run `19_POST_COMPLETION_REFRESH_PROTOCOL.md`;
3. update snapshot-derived files;
4. fill `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`;
5. freeze exact target model revisions/hashes only under separate authorization;
6. refresh future Codex/ChatGPT handoffs;
7. begin the actual migration design/planning workflow;
8. migrate to V2 Base;
9. verify V2 Base;
10. extend to V2 So400m;
11. verify V2 So400m;
12. freeze benchmark corpus/query/judgment artifacts;
13. execute the three-way benchmark;
14. apply predeclared winner rules;
15. record the representation decision;
16. consider separately authorized full-archive indexing.

---

## 20. Non-Goals

This preparation project does not:

- implement SigLIP2;
- select a final production winner;
- create three permanently diverging repositories;
- require full-archive indexing for comparison;
- authorize model acquisition;
- authorize protected-media use;
- alter Gate maturity;
- redesign unrelated editing/QC architecture;
- create a generic model marketplace/plugin system;
- treat synthetic tests as model-quality evidence.

---

## 21. Success Criteria

The preparation package is successful when a future post-V1 ChatGPT/Codex session can:

- locate the authoritative decision immediately;
- understand the intended sequence without conversation history;
- distinguish frozen decisions from stale snapshots;
- identify V1 model-coupled code quickly;
- understand both SigLIP2 target contracts;
- know what must not be changed;
- refresh stale information systematically;
- begin migration design/planning without repeating broad research;
- construct the benchmark without inventing evaluation rules after seeing results;
- preserve provenance and evidence discipline throughout.

The package is preparation, not execution. Its value is measured by reduced rediscovery and safer transition after V1 completion.
