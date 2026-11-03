# VIP-2 AI Studio Lab — B08-SYN-01: Three-Profile Synthetic Product-Path Closure

**Task type:** One substantial, self-contained, model-free Gate-1 engineering block  
**Execution destination:** Centaurioun/video-intelligence-pipeline-2 ONLY  
**Status:** LAB IMPLEMENTATION REQUEST — UNVERIFIED UNTIL HOSTED CI  
**Created:** 2026-11-04  
**Language:** Implement Python; report in Turkish  
**Governing historical source:** video-intelligence-pipeline main at 592952daf475b1bbae2eebdee64d992c1a744f08  
**Lab source:** the imported ZIP/main snapshot, whose exact equivalence must be checked  
**Owner permission:** implement the bounded synthetic lab task in the imported AI Studio workspace; the user will decide when to push to the lab repository  
**Not authorized:** writing to the original video-intelligence-pipeline repository, any real-media operation, model acquisition/execution, provider use, production, or Gate promotion.

---

## 0. Mission and why this exact block

Build a coherent **model-free three-profile product-path compatibility and refusal test suite** across the existing local-first index/query surfaces, with narrowly necessary implementation fixes if the source itself demonstrates a defect.

The three existing closed profiles:

| Arm | Profile ID | Expected width | Declared image geometry | Authority |
|---|---|---:|---|---|
| V1 Base | vip-v1-siglip-base-224 | 768 | 224 / patch 16 | preserved V1 identity; synthetic execution in this task |
| V2 Base | vip-v2-siglip2-base-224 | 768 | 224 / patch 16 | model-free V2 profile only |
| V2 SO400M | vip-v2-siglip2-so400m-384 | 1152 | 384 / patch 14 | model-free V2 profile only |

**Key missing coverage to investigate:** product integration already tests a 768D fake V2 Base path, while the equivalent 1152D SO400M product-facing end-to-end fake path is not established by those existing tests. The existing model-profile and fake-adapter tests alone are not a full product index/query acceptance.

This assignment is **not** a request to write a new model loader, implement real SigLIP2 tokenization, run a benchmark, or declare the project complete. It is deliberately independent of PR #258 / A-7 S5-T1.

Deliver a robust synthetic compatibility package to make future real-model integration safer without representing synthetic evidence as real-model evidence.

### What counts as success

1. All three existing profile identities can be represented by valid, clearly synthetic profile fixtures.
2. Each profile selects its own deterministic fake runtime and semantic-space identity.
3. Index and query product seams propagate the exact selected generation/space identity.
4. V1 and V2 Base **cannot** be mixed despite sharing width 768.
5. SO400M is handled as **1152-dimensional**, including the correct 4608-byte float32 row-width geometry where the existing contract exposes row widths.
6. Invalid, conflicting, or cross-space requests fail closed before forbidden downstream effects.
7. Retrieval candidates, when involved, preserve integer PTS/rational timebase as **nonbinding locators only**.
8. Python tests are authored, but **not run inside Google AI Studio**. GitHub Actions performs execution after a human-authorized push to this lab repo.

---

## 1. Boundary: original repository versus this public laboratory

**Original canonical repository (do not modify):**
https://github.com/Centaurioun/video-intelligence-pipeline

**Writable experiment repository:**
https://github.com/Centaurioun/video-intelligence-pipeline-2

This laboratory repository is intentionally not the canonical project's accepted implementation branch. The lab is currently **PUBLIC**: never commit credentials, private archive metadata, private source paths, actual media files, model assets, or sensitive evidence.

The lab ZIP omits some historical/research/orchestration folders, and GitHub PR contents are unavailable to AI Studio. The absence of a folder in this reduced lab snapshot does not grant permission to recreate it or infer that the original canonical project has the same gaps.

**Never push this laboratory's reduced tree over the original canonical main.**

Historical decisions remain useful constraints, but the Owner's current permission here is strictly for a reversible synthetic experiment in the **second repository**. This task does not retroactively authorize work in the original repository, clear a frozen Gate-B condition, amend the original project's task ledger, or certify model readiness.

GitHub Actions workflow is managed separately:

.github/workflows/vip-ai-studio-synthetic-ci.yml

Do not edit that workflow during this code task. Do not delete it when synchronizing the AI Studio workspace. If it is missing from the imported ZIP, **do not treat the absent local workflow as an instruction to delete it remotely**. The remote lab main is the delivery destination; this task does not authorize bulk repository replacement.

---

## 2. Mandatory reading: only actual sources, no imaginary PRs

Read these first, where present:

- AGENTS.md
- docs/INDEX.md
- docs/project/00_PROJECT_CHARTER.md
- docs/project/01_CURRENT_STATE_AND_HANDOFF.md
- docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md
- docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md
- docs/project/PYTHON_TEST_MATRIX_AND_CI.md
- docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md
- docs/migrations/siglip2-post-completion/32_PROVISIONAL_SIGLIP2_TOKENIZER_PROCESSOR_POOLING_CONTRACT.md

Then inspect the **current source code**, not only the dated documentation:

- experiments/persistent_local_index/model_profile.py
- experiments/persistent_local_index/model_space.py
- experiments/persistent_local_index/embedding.py
- experiments/persistent_local_index/siglip2_native.py
- experiments/persistent_local_index/indexer.py
- experiments/persistent_local_index/search.py
- src/vip_fvs/semantic_index.py
- src/vip_fvs/local_semantic.py
- src/vip_fvs/coordinator.py
- src/vip_fvs/cli.py
- src/vip_fvs/retrieval_adapter.py
- src/vip_fvs/query_modality.py

Relevant existing tests:

- experiments/persistent_local_index/tests/test_model_profile.py
- experiments/persistent_local_index/tests/test_siglip2_native.py
- experiments/persistent_local_index/tests/test_siglip2_session.py
- tests/gate1/compat/test_three_arm_compat.py
- tests/vip_fvs/unit/test_semantic_index.py
- tests/vip_fvs/unit/test_local_semantic.py
- tests/vip_fvs/unit/test_query_modality.py
- tests/vip_fvs/integration/test_product_index_query.py
- tests/vip_fvs/integration/test_multi_source_retrieval.py

**Investigate before writing:** the existing fake runtime factory and existing query-local/index-local operations already exist. Reuse them. Do not build parallel implementations of functionality already covered. If any listed path is absent in this imported snapshot, report the discrepancy, adapt only within allowed paths, and never claim to have read an absent file.

---

## 3. Exact writable boundaries

### Required new test file

- tests/vip_fvs/integration/test_three_profile_product_path.py

This is the primary deliverable: meaningful synthetic, isolated, product-facing assertions rather than a second copy of existing unit tests.

### Existing test paths that may be extended, only when needed

- tests/vip_fvs/integration/test_product_index_query.py
- experiments/persistent_local_index/tests/test_model_profile.py
- experiments/persistent_local_index/tests/test_siglip2_native.py

### Production paths that may be modified only for a demonstrated source defect

- experiments/persistent_local_index/model_profile.py
- experiments/persistent_local_index/embedding.py
- experiments/persistent_local_index/siglip2_native.py
- src/vip_fvs/local_semantic.py
- src/vip_fvs/semantic_index.py
- src/vip_fvs/coordinator.py
- src/vip_fvs/cli.py

Do **not** change production modules merely to produce a larger diff. A working implementation with a substantial new safety regression suite is a valid completion for the lab block.

If an observed defect requires a production edit:
1. Describe exact violated invariant and existing call chain.
2. Add a focused regression test that would fail before the fix.
3. Make the smallest compatible production change within the allowlist.
4. Keep the original V1 behavior and all existing refusal semantics.
5. If the fix requires any path outside this list, STOP that fix, report it as BLOCKED_SCOPE, and continue with independent in-scope test coverage.

### Explicitly forbidden edits

- .github/**, .gitignore, .env*, requirements/**, config/**
- docs/decisions/**, docs/architecture/**, docs/project/**, schemas/**
- src/gate0/**, src/gate2/**, src/gate3/**, src/vip_fvs/source_snapshot.py
- src/vip_fvs/stream_identity_gate.py, src/vip_fvs/refinement_adapter.py
- src/vip_fvs/review_bundle.py, src/vip_fvs/human_decision.py
- src/vip_fvs/real_plan.py, src/vip_fvs/local_preview.py
- Any historical receipt, evidence carrier, private data file, source media or model asset

No new dependencies. No new daemon, web server, ANN service, vector database, queue, cloud adapter, or GUI. No repository-wide refactor or formatting churn.

---

## 4. Phase A — Evidence-based source audit (before editing)

Read the relevant code paths and create an internal coverage table:

| Contract | Existing evidence / file | Missing test or behavior | Safe action |
|---|---|---|---|
| Profile ID and shape | ModelProfile / model_space | 1152D product propagation | New test |
| Fake profile runtime | build_fake_profile_runtime | Three-arm runtime selection | New test |
| Product index | coordinator.index_local_source | Space/generation identity for each arm | New test |
| Product query | coordinator.query_local_index | Query-only, no re-index | New test |
| CLI fake selector | cli._product_runtime, index-local/query-local | SO400M selection and refusal | New test |
| Refusal semantics | existing validators/engine | incompatible generation and fake-to-real misuse | New test |
| Source timing locators | existing search hit | integer PTS/rational timebase preserved, never an edit boundary | New test where relevant |

The table is a planning aid, not evidence of tests passing.

Identify and avoid duplicate assertions already present in tests. If a behavior is already thoroughly covered, do not replicate it unless the existing assertion never reaches the actual product integration seam.

---

## 5. Phase B — Synthetic profile fixture matrix

Implement concise reusable test helpers (prefer test-local helpers):

1. Construct valid synthetic ModelProfile instances for all three closed IDs using the existing contract. Follow actual current ModelProfile constructor fields; do not invent unsupported fields.
2. Use unmistakably synthetic, deterministic test-only revision/digest values. Do not claim that these values are authentic model checkpoints, tokenizer assets, or measured processors.
3. Preserve the V1-specific frozen-compatible contract fields and its distinct identity rules; do not re-label V1 as V2 or copy V2 assumptions onto V1.
4. For V2 Base, validate declared 768D geometry and synthetic profile text contract.
5. For V2 SO400M, validate declared 1152D geometry and synthetic profile text contract.
6. Verify expected profile row widths using the existing exposed row-width function where applicable: V1 and V2 Base 3072 bytes; SO400M 4608 bytes.
7. Assert that:
   - V1 768D and V2 Base 768D have unequal semantic-space IDs.
   - V2 Base 768D and SO400M 1152D have unequal semantic-space IDs.
   - Recreating the same synthetic profile yields the same semantic-space ID.
   - Changing a bound identity input changes identity or is refused according to the existing contract.

Do not weaken validation to accept contradictory model ID, image geometry, dimensions, precision or processor digest.

---

## 6. Phase C — Fake adapter and vector-contract integrity

Use the existing factory:

persistent_local_index.embedding.build_fake_profile_runtime

Exercise its returned checked runtime for each V2 profile and, if the V1 contract permits, use the corresponding preserved compatible synthetic path for V1.

Assert:

- fake=True is explicit and preserved.
- Every returned vector has the exact requested row count and model-space width.
- Rows are contiguous or correctly typed where required by the existing storage/query contract.
- Numeric values are finite and float32.
- Deterministic repeated synthetic inputs give deterministic vectors.
- Distinct profile identities must not be reinterpreted as interchangeable vectors.
- SO400M vectors are not accidentally truncated to 768 columns.
- Invalid shape, nonfinite data, zero vectors or incompatible semantic spaces refuse using existing contract semantics, where those constraints are already authoritative.

**Do not assert semantic similarity quality.** The fake vector generator is deliberately NOT a valid representation of what the real model would retrieve.

**No model asset/session call is permitted.** Tests must not touch any actual model path, local cache, tokenizer or device.

---

## 7. Phase D — Product-facing index and query lifecycle

The main requirement is to reach the actual product boundaries, not only call ModelProfile directly.

Use injected deterministic in-memory or temp-directory test doubles that implement the existing SemanticIndexEngine protocol. Prefer existing CountingEngine-style fixtures if they can be reused without copying them wholesale.

Prove for each of three profiles where the actual product contracts support it:

1. The selected runtime/semantic space reaches coordinator.index_local_source.
2. The generation spec is derived from the correct space, not from a hardcoded V1 default.
3. Returned index summary carries the correct generation_id and space_id.
4. A subsequent query uses coordinator.query_local_index against the **existing generation**.
5. Query returns the same intended generation_id/space_id and correct query_count.
6. The query call never invokes index_source or a video decoder.
7. Distinct profiles have separate index/generation identities; no cross-space reuse.
8. The engine and runtime receive the exact intended text inputs and top_k.
9. Source locator and result provenance are not fabricated as real-media measurements.
10. Repeated calls against an unchanged synthetic generation are deterministic.

Prefer an injected fake engine. Do not execute a media sampling/indexing command on real source files. If a pure synthetic temporary source is required by an API, use only test-created harmless bytes or generated fixture metadata, not a protected archive path.

The product-facing path must remain **local-first and source-safe**.

---

## 8. Phase E — CLI selection and compatibility

Exercise the existing CLI pathway using, as appropriate:

- --fake-embedder
- --model-profile-json
- index-local
- query-local

For all three profile identities:

- A validated synthetic profile reaches the intended runtime/space.
- V2 SO400M retains 1152-dimensional vectors through the selected product path.
- V1 default/no-profile behavior remains compatible.
- Existing legacy CLI command parsing is preserved.
- index-local and query-local remain separate operations.
- Invalid profile JSON is rejected without defaulting to real inference.
- Omitting --fake-embedder for an explicitly synthetic profile JSON preserves the existing refusal: MODEL_PROFILE_JSON_REQUIRES_EXPLICIT_FAKE_MODE.
- Fake and real arguments together retain the existing ambiguity refusal.
- Real-mode missing authorization/model inputs must fail before constructing a real session or reading model assets.

Use monkeypatched factories and counters to prove side-effect ordering. Do not make the tests call the actual native model loader or contact a provider.

Do not add a new CLI command unless a source-verified and test-demonstrated requirement absolutely cannot be met using the current commands. In that case STOP and explain why a separate design decision is needed.

---

## 9. Phase F — Mandatory negative/refusal matrix

Cover adversarial and invalid inputs without constructing a dangerous environment.

**Identity cases**
- V1 768D generation queried by V2 Base 768D identity: refuse.
- V2 Base 768D generation queried by SO400M 1152D identity: refuse.
- SO400M 1152D generation queried with a mismatched model revision or bound processor identity: refuse.
- Invalid/unsupported profile ID, width, precision, normalization, digest or synthetic contract fields: refuse.

**Output and runtime cases**
- Injected embedding shape not equal to required width: refuse.
- Nonfinite rows and invalid dtype/numeric values: refuse where the existing adapter contract specifies it.
- Real-mode request without required source/model authorization: refuse before any unsafe call.
- Explicit fake runtime combined with real-mode inputs: refuse.
- Unsupported modality must not silently become a text query.

**Effect ordering cases**
On a refusal, prove with injected spies wherever applicable:
- no index write,
- no query scoring,
- no model factory call,
- no source-content read,
- no media decoder or probe,
- no implicit fallback to another profile.

Do not invent error strings; use exact existing error codes and ordering. If existing production behavior does not meet a specified invariant, write the failing regression and report BLOCKED_SCOPE when the minimal fix lies outside the allowlist.

---

## 10. Phase G — Candidate timing and provenance discipline

If product query hits are used to exercise the complete output contract:

- Preserve integer PTS exactly, including nonzero and nontrivial values.
- Preserve timebase_num/timebase_den as a rational pair.
- Keep timestamps as **source locators**, never exact edit-ready interval endpoints.
- Preserve source revision / source digest attribution wherever the existing hit contract carries them.
- A semantic retrieval hit is MATCHED and nonbinding; do not call it MEASURED.
- Never translate timestamp seconds to frame count by seconds × nominal FPS.
- No human editorial decision, edit plan, preview renderer or Gate-3 output is created by this task.

The following are the only assertion-level evidence classes:
MEASURED, MATCHED, VISUALLY_OBSERVED, AUDIO_OBSERVED, EDITORIAL_INFERENCE.
NOT_OBSERVED is a marker, not a sixth class.

---

## 11. Phase H — Code quality, ownership and compatibility

Use the repository's conventions:

- Python standard library + existing NumPy/pytest APIs only.
- Favor parametrized tests for V1/V2 Base/SO400M and clear invariant-specific test names.
- Use synthetic fixtures with exact, documented fake identity.
- Avoid excessive monkeypatching that only tests the monkeypatch rather than the integration.
- Keep tests side-effect-free except under pytest tmp_path.
- No real-media, model asset or network work.
- No public API or persistent-schema additions unless an existing test demonstrates the minimal compatibility need.
- No ad-hoc duplication of stable semantic index machinery.
- Preserve all existing source refusal behavior.

**Do not alter source merely to make a test superficially PASS.** Correct the verified defect or report it without changing code. Never skip, delete or xfail a test to hide a failure.

Stop if a change would require modifying a different Gate's authority, source-native temporal contracts, S5 shared-admission APIs, historical receipt formats, or any locked decision.

---

## 12. AI Studio execution restrictions — WRITE CODE, DO NOT RUN TESTS

This assignment intentionally separates code authoring from execution.

**In Google AI Studio:**

- READ relevant code and documents.
- WRITE the scoped Python production/test files necessary for the block.
- Use code review and static reasoning.
- You MAY run a purely offline syntax-only ast.parse/compile check if available, but do not call this pytest verification.
- DO NOT execute pytest or any integration script.
- DO NOT install Python or package dependencies.
- DO NOT download models, use network to obtain packages, access providers, or operate on real media.
- DO NOT use FFmpeg/FFprobe, even on fixtures, for this block.
- DO NOT push to GitHub automatically.
- DO NOT create commits, branches, PRs, or modify the CI YAML.
- DO NOT publish into the original repository.

**Human action after AI Studio finishes:** the Owner decides whether to push the changed files to the LAB repository. GitHub Actions then executes the test matrix automatically.

Do not write PASS or "tested" without an actual hosted test result.

---

## 13. CI acceptance contract — executed separately by GitHub Actions

Existing lab CI:

.github/workflows/vip-ai-studio-synthetic-ci.yml

Its target matrix is Python 3.11 and 3.14. The test selection covers:

- experiments/persistent_local_index/tests/test_model_profile.py
- experiments/persistent_local_index/tests/test_siglip2_native.py
- experiments/persistent_local_index/tests/test_siglip2_session.py
- tests/gate1/compat/test_three_arm_compat.py
- tests/vip_fvs/unit/test_semantic_index.py
- tests/vip_fvs/unit/test_local_semantic.py
- tests/vip_fvs/unit/test_query_modality.py
- tests/vip_fvs/integration/test_product_index_query.py
- tests/vip_fvs/integration/test_multi_source_retrieval.py
- tests/vip_fvs/integration/test_three_profile_product_path.py (conditional until created)

The CI installs pinned existing test prerequisites only. It does not install models or perform an authentic benchmark.

**Acceptance requires:**
1. GitHub Actions has actually assigned a runner and executed steps on the correct lab commit.
2. The new three-profile suite ran, not merely skipped because absent.
3. All selected suites passed on both interpreter versions.
4. No existing V1 / V2 Base regression was broken.
5. A separate source review finds no unsafe change or invalid assumption.

A failed or unstarted GitHub Actions job means NOT_EXECUTED or FAIL as appropriate, never PASS. CI PASS establishes only the tested synthetic scope, not real V2 readiness.

---

## 14. Explicitly rejected shortcuts

Do not:

1. Report synthetic SO400M embeddings as real SigLIP2 outputs.
2. Infer tokenizer vocabulary, BOS/EOS, padding, attention masks, pooling or projection from the fake generator.
3. Assume V1 and V2 Base are equivalent because both are 768D.
4. Create a second independent product index/search implementation.
5. Add an auto-detect model selector that silently picks a profile.
6. Substitute a mismatch with a 768D fallback or truncate 1152D to 768D.
7. Treat a semantic timestamp as a source-native measured edit boundary.
8. Use test doubles that always return preasserted output without passing through the actual product coordinator.
9. Change requirements or CI to hide package/collection failures.
10. Mark G1.2.4, Gate 1, H3-D05, or the original project as accepted/completed.
11. Overwrite historical decisions, registries, receipts or evidence.
12. Recreate PR #258 admission work inside this block.

---

## 15. Final required output — Turkish, inspectable

The final report must include:

### A. Snapshot and inspected source
List exact files read. State imported ZIP or verified git state. Do not fabricate SHA.

### B. Baseline coverage audit
State what was **already implemented** and what was genuinely missing before edits.

### C. Changes made
List every changed file and every new test, with the behavior it validates. State any source defects corrected. Identify any tests that exercise a real product seam rather than a fake-only helper.

### D. Test execution
Explicitly state:
**AI_STUDIO_PYTEST: NOT_EXECUTED (by design)**

If syntax compilation ran, report its separate result with actual scope. Do not claim Python 3.11/3.14 execution until GitHub Actions proves it.

### E. Refusal and side-effect protection
Describe exact negative tests and any unresolved gap.

### F. Known blocked items
Any unimplemented behavior, missing dependency, unavailable PR content, or out-of-scope product fix.

### G. Delivery
Show minimal diff summary, changed file list, and the exact CI tests expected to run after the human's push.

### H. Disposition
Use one of:

- IMPLEMENTED_UNVERIFIED — code delivered, awaiting GitHub CI;
- PARTIAL_BLOCKED — some in-scope code delivered, other work blocked;
- NOT_IMPLEMENTED — no useful code was produced.

Never claim TESTED, VERIFIED_COMPLETE, AUTHENTIC_MODEL_READY, BENCHMARK_PASS, or GATE_PROMOTED.

**End of single task. Do not start B09, S5-T2, or any other block.**
