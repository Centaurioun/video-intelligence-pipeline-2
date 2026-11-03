# SigLIP2 Post-Completion Preparation Pack Implementation Plan

**Execution status:** COMPLETE — Tasks 1–8 were executed and final-audited through canonical `main@aac950c8d12438b61755dcf53e3521ce3e5eede1`. A later owner-authorized hardening pass is supplemental to this completed plan.

> **For agentic workers:** REQUIRED SUB-SKILL: follow the repository's current execution authority in `AGENTS.md`. For this documentation-only plan, prefer native execution in small sequential batches; use Superpowers skills when their trigger applies. Do not use stock `subagent-driven-development` merely because multiple artifacts exist.

**Goal:** Create the documentation, machine-readable templates, future handoffs, and benchmark-preparation artifacts needed to accelerate the post-V1 SigLIP2 migration without changing current product code, tests, model assets, runtime behavior, or execution authorization.

**Architecture:** Two new documentation trees are created: `docs/migrations/siglip2-post-completion/` for migration preparation and `docs/benchmarks/siglip-three-way/` for the later three-way benchmark. Work is deliberately divided into small mergeable batches so each batch can be independently reviewed, merged, and resumed without timeout risk. Repository-specific facts captured before V1 completion are labeled as snapshots and must be reverified at the V1 completion boundary.

**Tech Stack:** Markdown, YAML, JSON, CSV, Git/GitHub; current repository evidence; official Hugging Face/Transformers/SigLIP2 primary sources where external facts are required.

**Spec:** `docs/superpowers/specs/2026-10-05-siglip2-post-completion-preparation-pack-design.md`

## Execution Reconciliation

All original Tasks 1–8 are complete. Checkboxes below are historical execution receipts and are marked complete in this reconciliation.

During Batches 2–7, the current-state package manifest was also updated in the same docs-only PR so it would not remain stale. Where a task said "only N new files changed," the actual safe scope was "N new files plus the package-manifest state update." This was an intentional documentation-state correction, not production/test scope expansion.

Original execution culminated in PR #51. The subsequent six-cycle hardening request is tracked in `docs/migrations/siglip2-post-completion/29_SIX_CYCLE_HARDENING_AUDIT.md` and is not a reopening of migration implementation authority.

## Global Constraints

- Do not modify existing production Python files.
- Do not modify existing test files.
- Do not download SigLIP2 models or model weights.
- Do not execute model inference.
- Do not process protected/archive media.
- Do not perform full-archive indexing.
- Do not widen Gate or production authorization.
- New files may document future work but must not claim that future work is already implemented.
- Every pre-completion repository-specific fact must be labeled `VERIFIED_CURRENT`, `SNAPSHOT`, and/or `REVERIFY_AT_V1_COMPLETION` as appropriate.
- Unknown future checkpoint revisions, hashes, timings, and winner decisions must remain explicitly unresolved.
- Preserve ADR-0002's sequence: V1 Base completion/freeze -> V2 Base migration -> V2 So400m extension -> frozen three-way mini-benchmark -> representation decision -> separately authorized full-archive indexing.
- Each batch is implemented on a fresh branch from the then-current canonical `main`, merged through a PR, and read back from `main` before the next batch.
- Do not create or edit any path outside the two new preparation trees unless the owner separately requests it.
- Do not treat public model benchmarks as project-specific quality evidence.

## Review Focus

1. **Stale repository paths or symbols:** a future agent should see `REVERIFY_AT_V1_COMPLETION`, not mistake them for permanent truth.
2. **Authorization leakage:** future runbooks and launch packets must not silently authorize model downloads, protected-media use, or full-archive execution.
3. **Evidence upgrading:** external model-card/paper claims must remain external evidence and not become local `MEASURED` claims.
4. **Semantic-space mixing:** all three candidate spaces must remain isolated; raw cosine scores across spaces are not directly comparable quality measures.
5. **Benchmark goalpost drift:** corpus, queries, relevance rules, metrics, and winner logic must be frozen before final comparative interpretation.

---

## File Structure

### Migration preparation tree

Create under `docs/migrations/siglip2-post-completion/`:

- `00_README_AND_ENTRYPOINT.md` — entrypoint, reading order, authority hierarchy, package purpose.
- `01_AUTHORITY_SCOPE_AND_ACTIVATION.md` — current/deferred authority and activation trigger.
- `02_PACKAGE_MANIFEST.yaml` — machine-readable package inventory and refresh state.
- `03_V1_BASELINE_SNAPSHOT.md` — current V1 model/runtime/code snapshot.
- `04_MODEL_CONTRACTS.md` — human-readable three-model contract comparison.
- `05_model-contracts.yaml` — machine-readable model contract records.
- `06_MODEL_COMPATIBILITY_MATRIX.md` — V1 Base vs V2 Base vs V2 So400m compatibility map.
- `07_MIGRATION_SURFACE_SNAPSHOT.md` — model-coupled code/test/config locations.
- `08_HARDCODE_AND_ASSUMPTION_REGISTER.md` — hard-coded assumptions and migration impact.
- `09_PRESERVE_BOUNDARIES.md` — unaffected pipeline layers and invariants.
- `10_TARGET_MODEL_PROFILE_DESIGN.md` — YAGNI-constrained future model-profile design.
- `11_V1_TO_V2_BASE_RUNBOOK.md` — draft future migration runbook.
- `12_V2_BASE_TO_SO400M_RUNBOOK.md` — draft second migration runbook.
- `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md` — dependency/runtime compatibility evidence and revalidation requirements.
- `14_TEST_AND_ACCEPTANCE_MATRIX.md` — future TDD/regression/acceptance map.
- `15_SEMANTIC_SPACE_INDEX_STRATEGY.md` — index isolation and semantic-space policy.
- `16_VERSION_PRESERVATION_AND_ROLLBACK.md` — immutable candidate preservation and rollback.
- `17_RISK_REGISTER.md` — technical, evidence, runtime, and process risks.
- `18_STALENESS_AND_REVERIFY_REGISTER.md` — durable vs snapshot facts.
- `19_POST_COMPLETION_REFRESH_PROTOCOL.md` — first procedure to run after V1 completion.
- `20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md` — primary-source evidence digest.
- `21_source-receipts.yaml` — source URLs, assertions, and revalidation state.
- `22_REJECTED_ALTERNATIVES_AND_RECONSIDERATION_TRIGGERS.md` — preserved alternatives and reopening criteria.
- `23_SYNTHETIC_REHEARSAL_SPEC.md` — documentation-only fake-vector compatibility probe design.
- `24_FUTURE_CODEX_LAUNCH_PACKET.md` — future executable-oriented handoff.
- `25_FUTURE_CHATGPT_ORCHESTRATOR_HANDOFF.md` — future orchestration handoff.
- `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md` — V1 completion/migration readiness template.
- `27_POST_MIGRATION_VERIFICATION_CHECKLIST.md` — V2 Base/So400m completion verification template.
- `28_CHANGELOG.md` — preparation-pack history.

### Benchmark preparation tree

Create under `docs/benchmarks/siglip-three-way/`:

- `B00_BENCHMARK_CHARTER.md`
- `B01_CORPUS_SELECTION_AND_FREEZE_PROTOCOL.md`
- `B02_corpus-manifest-template.yaml`
- `B03_QUERY_TAXONOMY.md`
- `B04_query-set-template.csv`
- `B05_RELEVANCE_AND_ANNOTATION_GUIDE.md`
- `B06_relevance-judgment-template.csv`
- `B07_METRICS_AND_STATISTICAL_PROTOCOL.md`
- `B08_PERFORMANCE_AND_RESOURCE_PROTOCOL.md`
- `B09_BENCHMARK_EXECUTION_PROTOCOL.md`
- `B10_result-schema.json`
- `B11_benchmark-run-manifest-template.yaml`
- `B12_BENCHMARK_REPORT_TEMPLATE.md`
- `B13_WINNER_DECISION_RULES.md`
- `B14_FAILURE_MODES_AND_BIAS_CHECKLIST.md`
- `B15_BENCHMARK_AUDIT_CHECKLIST.md`

---

### Task 1: Migration Pack Batch 1 — Authority, Entrypoint, Baseline, Contracts

**Files:**
- Create: `docs/migrations/siglip2-post-completion/00_README_AND_ENTRYPOINT.md`
- Create: `docs/migrations/siglip2-post-completion/01_AUTHORITY_SCOPE_AND_ACTIVATION.md`
- Create: `docs/migrations/siglip2-post-completion/02_PACKAGE_MANIFEST.yaml`
- Create: `docs/migrations/siglip2-post-completion/03_V1_BASELINE_SNAPSHOT.md`
- Create: `docs/migrations/siglip2-post-completion/04_MODEL_CONTRACTS.md`

**Interfaces:**
- Consumes: ADR-0002, approved preparation-pack spec, current canonical `main`, official primary model sources.
- Produces: stable entrypoint and authority surface used by all later batches.

- [x] **Step 1: Refresh canonical repository state before writing**
  - Read `AGENTS.md`, `docs/INDEX.md`, ADR-0002, the approved design spec, and current `main` SHA.
  - Record the observed SHA in the V1 snapshot as `SNAPSHOT`, not as final V1 completion identity.

- [x] **Step 2: Create `00_README_AND_ENTRYPOINT.md`**
  - Define package purpose, read order, authority parent, candidate set, activation trigger, and information-state labels.
  - Explicitly state that preparation does not authorize migration execution.

- [x] **Step 3: Create `01_AUTHORITY_SCOPE_AND_ACTIVATION.md`**
  - Separate current allowed documentation work from deferred model acquisition, real-media execution, migration implementation, benchmark execution, and full-archive indexing.
  - Include fail-closed behavior when authorization is unclear.

- [x] **Step 4: Create `02_PACKAGE_MANIFEST.yaml`**
  - Include all migration and benchmark artifact paths from this plan.
  - For every entry record: `path`, `role`, `state`, `refresh_at_v1_completion`, and `authority_parent`.
  - Mark future artifacts not yet created as `PLANNED`.

- [x] **Step 5: Create `03_V1_BASELINE_SNAPSHOT.md`**
  - Capture only verified current V1 facts relevant to model migration.
  - Label file paths, symbols, dependency/runtime observations, and hard-coded values as `SNAPSHOT` / `REVERIFY_AT_V1_COMPLETION`.
  - Do not restate unrelated project history.

- [x] **Step 6: Create `04_MODEL_CONTRACTS.md`**
  - Compare SigLIP1 Base, SigLIP2 Base, and SigLIP2 So400m.
  - Distinguish repository-measured facts, official external facts, and future unresolved acquisition values.
  - Do not claim local SigLIP2 runtime evidence.

- [x] **Step 7: Verify Batch 1 scope**
  - Confirm the branch diff contains exactly the five new Batch-1 files.
  - Confirm no production/test path changed.
  - Confirm every snapshot-derived statement has an explicit refresh marker.
  - Confirm no future model revision/hash is fabricated.

- [x] **Step 8: Commit, open PR, merge, and read back from canonical `main`**
  - Use a docs-only commit message.
  - After merge, re-fetch all five files from `main` and record the merge SHA in the batch receipt/report to the owner.

---

### Task 2: Migration Pack Batch 2 — Machine Contracts and Migration Surface

**Files:**
- Create: `docs/migrations/siglip2-post-completion/05_model-contracts.yaml`
- Create: `docs/migrations/siglip2-post-completion/06_MODEL_COMPATIBILITY_MATRIX.md`
- Create: `docs/migrations/siglip2-post-completion/07_MIGRATION_SURFACE_SNAPSHOT.md`
- Create: `docs/migrations/siglip2-post-completion/08_HARDCODE_AND_ASSUMPTION_REGISTER.md`
- Create: `docs/migrations/siglip2-post-completion/09_PRESERVE_BOUNDARIES.md`

**Interfaces:**
- Consumes: Batch 1 contracts/authority, current repository code/tests/configuration.
- Produces: exact future migration-surface map and no-touch boundary.

- [x] **Step 1: Refresh `main` and read Batch 1**
- [x] **Step 2: Create machine-readable `05_model-contracts.yaml` without unresolved values being guessed**
- [x] **Step 3: Create compatibility matrix separating V2 Base changes from So400m-only changes**
- [x] **Step 4: Audit current code/test/config paths and create migration-surface snapshot**
- [x] **Step 5: Register hard-coded/model-specific assumptions with impact and reverify status**
- [x] **Step 6: Document preserve/no-touch boundaries for temporal, provenance, source, editing, rendering, and QC layers**
- [x] **Step 7: Verify only five new Batch-2 files changed and all current-code references are labeled snapshots**
- [x] **Step 8: Commit, PR, merge, and canonical-main readback**

---

### Task 3: Migration Pack Batch 3 — Target Design, Runbooks, Runtime, Tests

**Files:**
- Create: `docs/migrations/siglip2-post-completion/10_TARGET_MODEL_PROFILE_DESIGN.md`
- Create: `docs/migrations/siglip2-post-completion/11_V1_TO_V2_BASE_RUNBOOK.md`
- Create: `docs/migrations/siglip2-post-completion/12_V2_BASE_TO_SO400M_RUNBOOK.md`
- Create: `docs/migrations/siglip2-post-completion/13_DEPENDENCY_RUNTIME_COMPATIBILITY.md`
- Create: `docs/migrations/siglip2-post-completion/14_TEST_AND_ACCEPTANCE_MATRIX.md`

**Interfaces:**
- Consumes: Batches 1-2.
- Produces: migration design target and future execution/test skeleton.

- [x] **Step 1: Define minimal future model-profile boundary; reject unrelated generic-provider abstraction**
- [x] **Step 2: Draft V1->V2 Base runbook with explicit preconditions, verification gates, and non-authorizations**
- [x] **Step 3: Draft V2 Base->So400m runbook with 224->384 and 768->1152 impacts**
- [x] **Step 4: Record dependency/runtime evidence and mandatory migration-day revalidation**
- [x] **Step 5: Map future TDD/regression/acceptance checks to migration concerns without editing tests now**
- [x] **Step 6: Verify no runbook step silently authorizes model download or protected-media execution**
- [x] **Step 7: Commit, PR, merge, and canonical-main readback**

---

### Task 4: Migration Pack Batch 4 — Isolation, Risk, Refresh, Evidence

**Files:**
- Create: `docs/migrations/siglip2-post-completion/15_SEMANTIC_SPACE_INDEX_STRATEGY.md`
- Create: `docs/migrations/siglip2-post-completion/16_VERSION_PRESERVATION_AND_ROLLBACK.md`
- Create: `docs/migrations/siglip2-post-completion/17_RISK_REGISTER.md`
- Create: `docs/migrations/siglip2-post-completion/18_STALENESS_AND_REVERIFY_REGISTER.md`
- Create: `docs/migrations/siglip2-post-completion/19_POST_COMPLETION_REFRESH_PROTOCOL.md`
- Create: `docs/migrations/siglip2-post-completion/20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md`
- Create: `docs/migrations/siglip2-post-completion/21_source-receipts.yaml`

**Interfaces:**
- Consumes: prior migration batches, current repository evidence, primary external sources.
- Produces: safe refresh/evidence mechanism used immediately after V1 completion.

- [x] **Step 1: Define semantic-space and index-root isolation rules**
- [x] **Step 2: Define immutable V1/V2 candidate preservation and rollback rules**
- [x] **Step 3: Build risk register with triggers, consequences, mitigations, and evidence state**
- [x] **Step 4: Build staleness register covering all pre-completion repository facts**
- [x] **Step 5: Write the exact post-completion refresh protocol**
- [x] **Step 6: Build primary external evidence digest**
- [x] **Step 7: Create machine-readable source receipts with assertion mapping and retrieval dates**
- [x] **Step 8: Verify external claims remain distinguishable from local measured evidence**
- [x] **Step 9: Commit, PR, merge, and canonical-main readback**

---

### Task 5: Migration Pack Batch 5 — Future Handoffs and Verification

**Files:**
- Create: `docs/migrations/siglip2-post-completion/22_REJECTED_ALTERNATIVES_AND_RECONSIDERATION_TRIGGERS.md`
- Create: `docs/migrations/siglip2-post-completion/23_SYNTHETIC_REHEARSAL_SPEC.md`
- Create: `docs/migrations/siglip2-post-completion/24_FUTURE_CODEX_LAUNCH_PACKET.md`
- Create: `docs/migrations/siglip2-post-completion/25_FUTURE_CHATGPT_ORCHESTRATOR_HANDOFF.md`
- Create: `docs/migrations/siglip2-post-completion/26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`
- Create: `docs/migrations/siglip2-post-completion/27_POST_MIGRATION_VERIFICATION_CHECKLIST.md`
- Create: `docs/migrations/siglip2-post-completion/28_CHANGELOG.md`

**Interfaces:**
- Consumes: entire migration preparation pack.
- Produces: durable future execution/orchestration handoff without authorizing execution now.

- [x] **Step 1: Preserve rejected alternatives and explicit reconsideration triggers**
- [x] **Step 2: Specify synthetic 768/1152 compatibility rehearsal without writing code**
- [x] **Step 3: Draft future Codex packet with mandatory refresh-before-execution**
- [x] **Step 4: Draft future ChatGPT orchestration handoff with Superpowers design/plan gates**
- [x] **Step 5: Create V1 completion/migration readiness checklist**
- [x] **Step 6: Create post-migration verification checklist**
- [x] **Step 7: Initialize preparation-pack changelog**
- [x] **Step 8: Verify future handoffs cannot bypass ADR-0002 activation or separate authorization**
- [x] **Step 9: Commit, PR, merge, and canonical-main readback**

---

### Task 6: Benchmark Pack Batch 1 — Charter, Corpus, Queries, Relevance, Metrics

**Files:**
- Create: `docs/benchmarks/siglip-three-way/B00_BENCHMARK_CHARTER.md`
- Create: `docs/benchmarks/siglip-three-way/B01_CORPUS_SELECTION_AND_FREEZE_PROTOCOL.md`
- Create: `docs/benchmarks/siglip-three-way/B02_corpus-manifest-template.yaml`
- Create: `docs/benchmarks/siglip-three-way/B03_QUERY_TAXONOMY.md`
- Create: `docs/benchmarks/siglip-three-way/B04_query-set-template.csv`
- Create: `docs/benchmarks/siglip-three-way/B05_RELEVANCE_AND_ANNOTATION_GUIDE.md`
- Create: `docs/benchmarks/siglip-three-way/B06_relevance-judgment-template.csv`
- Create: `docs/benchmarks/siglip-three-way/B07_METRICS_AND_STATISTICAL_PROTOCOL.md`

**Interfaces:**
- Consumes: ADR-0002, migration authority package.
- Produces: frozen-comparison design independent of model implementation details.

- [x] **Step 1: Define benchmark purpose, non-claims, and three required arms**
- [x] **Step 2: Define representative 10-20-video corpus selection and freeze rules**
- [x] **Step 3: Create corpus manifest template without real protected-media identifiers**
- [x] **Step 4: Define balanced Turkish/English query taxonomy**
- [x] **Step 5: Create query-set CSV template**
- [x] **Step 6: Define relevance annotation rules before model outputs are inspected**
- [x] **Step 7: Create relevance-judgment CSV template**
- [x] **Step 8: Define metrics, aggregation, missing-hit handling, and ranking evaluation**
- [x] **Step 9: Verify no benchmark artifact contains real protected corpus data**
- [x] **Step 10: Commit, PR, merge, and canonical-main readback**

---

### Task 7: Benchmark Pack Batch 2 — Performance, Execution, Results, Winner Rules, Audit

**Files:**
- Create: `docs/benchmarks/siglip-three-way/B08_PERFORMANCE_AND_RESOURCE_PROTOCOL.md`
- Create: `docs/benchmarks/siglip-three-way/B09_BENCHMARK_EXECUTION_PROTOCOL.md`
- Create: `docs/benchmarks/siglip-three-way/B10_result-schema.json`
- Create: `docs/benchmarks/siglip-three-way/B11_benchmark-run-manifest-template.yaml`
- Create: `docs/benchmarks/siglip-three-way/B12_BENCHMARK_REPORT_TEMPLATE.md`
- Create: `docs/benchmarks/siglip-three-way/B13_WINNER_DECISION_RULES.md`
- Create: `docs/benchmarks/siglip-three-way/B14_FAILURE_MODES_AND_BIAS_CHECKLIST.md`
- Create: `docs/benchmarks/siglip-three-way/B15_BENCHMARK_AUDIT_CHECKLIST.md`

**Interfaces:**
- Consumes: Benchmark Batch 1 and migration contracts.
- Produces: complete future benchmark execution/evaluation envelope.

- [x] **Step 1: Define indexing, cold/warm query, memory, and storage measurement procedures**
- [x] **Step 2: Define identical-arm execution order and contamination controls**
- [x] **Step 3: Create valid JSON result schema**
- [x] **Step 4: Create reproducibility run-manifest template**
- [x] **Step 5: Create benchmark report template**
- [x] **Step 6: Define winner decision rules before results exist**
- [x] **Step 7: Create bias/failure checklist**
- [x] **Step 8: Create post-run benchmark audit checklist**
- [x] **Step 9: Validate JSON syntax and CSV/YAML templates structurally**
- [x] **Step 10: Commit, PR, merge, and canonical-main readback**

---

### Task 8: Final Preparation-Pack Consistency Audit

**Files:**
- Modify: only newly created preparation-pack files if corrections are required.
- Do not modify production/test files.

**Interfaces:**
- Consumes: Tasks 1-7.
- Produces: internally consistent preparation package ready to wait for V1 completion.

- [x] **Step 1: Read the package in declared entrypoint order**
- [x] **Step 2: Check every planned path in `02_PACKAGE_MANIFEST.yaml` exists**
- [x] **Step 3: Check every current-state claim is labeled by evidence/staleness state**
- [x] **Step 4: Check model identifiers and dimensionality/resolution facts are consistent across all files**
- [x] **Step 5: Check all future unknown revisions/hashes/timings remain unresolved rather than guessed**
- [x] **Step 6: Check all handoffs require post-completion refresh before execution**
- [x] **Step 7: Check benchmark corpus/query/metric/winner freeze ordering prevents post-hoc goalpost changes**
- [x] **Step 8: Confirm repository diff/history shows no production/test change caused by the preparation project**
- [x] **Step 9: Record any corrections in `28_CHANGELOG.md`**
- [x] **Step 10: Commit/PR/merge only if corrections were necessary, then read back canonical `main`**

---

## Execution Cadence

Execute exactly one bounded task/batch per user continuation turn unless the owner explicitly asks for a larger batch.

After each batch, return only:

- batch identifier;
- files created;
- PR/merge status;
- canonical `main` SHA;
- verification result;
- next planned batch.

This cadence is intentionally conservative to avoid timeout and context-loss risk.

## Completion Condition

This plan is complete when Tasks 1-8 are finished, all planned artifacts exist on canonical `main`, no current production/test code was changed by the preparation work, and the package is explicitly ready to remain dormant until V1 reaches its verified completion boundary.
