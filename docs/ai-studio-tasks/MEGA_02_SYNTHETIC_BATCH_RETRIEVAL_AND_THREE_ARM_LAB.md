# VIDEO INTELLIGENCE PIPELINE — AI STUDIO LAB
# MEGA-02: Local-First Synthetic Batch Retrieval, Three-Arm Comparison & Reproducible Report

**Task identity:** VIP-LAB-MEGA-02  
**Execution target:** \`Centaurioun/video-intelligence-pipeline-2\` (laboratory only)  
**Task status:** **LAB DESIGN / IMPLEMENTATION EXPERIMENT — NOT CANONICAL OWNER GATE PROMOTION**  
**Creation date:** 2026-11-04  
**Required final report language:** Turkish  
**Task size:** Large multi-module implementation; implement all internally compatible workstreams in ONE AI Studio task turn  
**Verification method:** Google AI Studio authors code and pytest tests without running pytest; GitHub Actions executes on subsequent human push; Codex separately reviews  
**Baseline lab checkpoint (at task design):** \`0c5eb05ab6de2adefa8377d198c7eae9bf7a7d74\` — historical reference, not a perpetual current SHA.

---

## 0. Read this first: the boundary between speed and ungrounded code

The Owner wishes to accelerate useful Python code development by commissioning **a substantial multi-module synthetic-only lab experiment**. The purpose is to obtain meaningful, inspectable implementation quickly. It is **not** a request to code every remaining four-Gate task without prerequisites.

This is ONE coherent large task covering related **portions** of the prior planning labels:

- **B05:** Multi-source product retrieval, extended from a single CLI query to explicit bounded batch queries.
- **B08:** Three **distinct** closed synthetic representation profiles (V1 Base 768D, V2 Base 768D, V2 SO400M 1152D) flowing through the read-only batch query path.
- **B09:** Lab-only deterministic, bounded query execution, reproducible reports, fail-closed behavior, injected-fault/retry-contract tests. These are **not** representative Gate-2 reliability workload measurements.
- **B07 PREPARATION ONLY:** An explicit deterministic text-query catalog useful as a future experimental input format. This does **not** authorize or execute any Gate-0 diagnostic retrieval experiment and supplies no human labels.

This task must result in **new production Python behavior**, not merely tests copied from existing B08 coverage.

### Verified starting facts from the repository source

- \`src/vip_fvs/multi_source_retrieval.py\` already implements \`retrieve_multi_source(..., query: str | Sequence[str], ...)\`, using a checked runtime and an injected \`SemanticIndexEngine\`. It binds hits by **exact source locator + digest** to a \`MultiSourceManifest\`.
- \`src/vip_fvs/cli.py\` exposes \`query-multi\`, but the CLI \`--query\` argument is a single text value. It does not expose a complete stable batch **query-ID catalog** and three-arm synthetic report protocol.
- \`src/vip_fvs/query_modality.py\` has declared \`TEXT\`, \`IMAGE_REFERENCE\`, and \`VIDEO_REFERENCE\` envelopes; reference modalities are not executable model capabilities.
- \`experiments/persistent_local_index/model_profile.py\` validates three closed model identities. It does not certify authentic SigLIP2 tokenizer, processor or pooling.
- \`experiments/persistent_local_index/embedding.py\` has \`build_fake_profile_runtime\` for validated V2 profiles, and V1 has a separately preserved fake local-semantic boundary.
- \`tests/vip_fvs/integration/test_three_profile_product_path.py\` exists in the lab and its 39 current synthetic cases passed GitHub CI for Python 3.11 and 3.14 at the verified reference.
- \`src/gate1/harness.py\` already contains generated-only three-arm **protocol** compatibility. Do not replace or duplicate its ranking/evaluation implementation. This task builds a **read-only multi-source product query consumer**, not a new evaluation engine.

Reinspect all facts against the actual imported files. Do not create a competing implementation when an exact suitable one already exists.

---

## 1. Environment, authority, and prohibited expansion

You are in a Google AI Studio workspace imported from a reduced ZIP. \`.git\` and PR information may be absent. Do not fabricate a Git SHA, prior task acceptance or remote PR content. The original source-of-truth repository is:

https://github.com/Centaurioun/video-intelligence-pipeline

**This task's writable LAB is:**

https://github.com/Centaurioun/video-intelligence-pipeline-2

The lab is **PUBLIC**. Never create or publish:
- private/source/protected videos or frame files;
- real archive names, user data or private paths;
- real model weights, processors, tokenizers, cache files;
- secrets, API tokens, personal information;
- previously generated real or protected archival evidence.

No source media opens, image decoding, FFmpeg, FFprobe, real model inference, model download, provider/cloud calls, external network activity, production export or Gate promotion.

**Do not push from AI Studio. The Owner will push the lab changes manually.** Do not synchronize an incomplete ZIP by deleting remote files. Retain existing \`.github/workflows/\` unchanged.

This separate laboratory experiment does **not** override explicit non-authority decisions recorded in the original repository, including Gate B \`NO_GO_BLOCKED\`, H3-C05 specification-only adoption, actual human relevance labeling, or S5 shared admission work pending in an original-project PR. The implementation here is a disposable prototype candidate requiring explicit original-project adoption later.

**Canonical source files for Gate 0/1/2/3 and historical contracts must not be mutated outside the allowlist below.**

---

## 2. Required repository study

Read, when present:

1. \`AGENTS.md\`
2. \`docs/INDEX.md\`
3. \`docs/project/00_PROJECT_CHARTER.md\`
4. \`docs/project/01_CURRENT_STATE_AND_HANDOFF.md\`
5. \`docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md\`
6. \`docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md\`
7. \`docs/project/PYTHON_TEST_MATRIX_AND_CI.md\`
8. \`docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md\`
9. \`docs/decisions/2026-10-26-h3-c05-owner-adoption-v102.md\`
10. \`docs/migrations/siglip2-post-completion/32_PROVISIONAL_SIGLIP2_TOKENIZER_PROCESSOR_POOLING_CONTRACT.md\`
11. \`docs/architecture/CANONICAL_CONTRACTS.md\`

Read complete relevant source functions:

- \`src/vip_fvs/cli.py\`: parser, \`_query_envelope\`, \`_product_runtime\`, \`main\`, current \`query-multi\`.
- \`src/vip_fvs/multi_source_retrieval.py\`: the COMPLETE \`retrieve_multi_source\` and candidate types.
- \`src/vip_fvs/source_adapter.py\`: \`MultiSourceManifest\`, \`SourceManifestEntry\`, \`load_multi_source_manifest\`.
- \`src/vip_fvs/local_semantic.py\`
- \`src/vip_fvs/semantic_index.py\`
- \`src/vip_fvs/query_modality.py\`
- \`src/vip_fvs/coordinator.py\`
- \`src/vip_fvs/retrieval_adapter.py\`
- \`experiments/persistent_local_index/model_profile.py\`
- \`experiments/persistent_local_index/model_space.py\`
- \`experiments/persistent_local_index/embedding.py\`
- \`experiments/persistent_local_index/search.py\`
- \`experiments/persistent_local_index/storage.py\`
- \`src/gate1/harness.py\` only to avoid duplicate work.

Read existing relevant test conventions:

- \`tests/vip_fvs/integration/test_multi_source_retrieval.py\`
- \`tests/vip_fvs/integration/test_product_index_query.py\`
- \`tests/vip_fvs/integration/test_three_profile_product_path.py\`
- \`tests/vip_fvs/unit/test_query_modality.py\`
- \`experiments/persistent_local_index/tests/test_model_profile.py\`

If the imported ZIP differs from the stated reference, treat source behavior as authoritative and report it.

---

## 3. Deliverable map: multiple modules, one coherent outcome

### Required new production modules

- \`src/vip_fvs/query_batch.py\`  
  Closed, bounded text-query catalog, pure data representation, validation, and exact ordered query-ID mapping.
- \`src/vip_fvs/synthetic_profiles.py\`  
  Reuse the existing validated three-profile model-free seams. A **synthetic-only** profile-to-checked-runtime adapter; no authentic path.
- \`src/vip_fvs/batch_retrieval.py\`  
  Read-only multi-source batch retrieval orchestrator over the **existing** \`retrieve_multi_source\`, with query ID and source provenance attached.
- \`src/vip_fvs/three_arm_batch.py\`  
  Explicit three-arm independently isolated synthetic retrieval orchestrator (one existing generation per arm), no cross-space score comparison.
- \`src/vip_fvs/batch_report.py\`  
  Deterministic canonical output with self-contained consistency validation, closed version/status/claim limits, and integrity digest. Does NOT write media or mutate an index.

### Bounded existing production file

- \`src/vip_fvs/cli.py\` — add **two additive lab commands**, leaving existing commands and arguments unchanged:
  - \`query-batch-synthetic\`
  - \`query-three-arm-synthetic\`

Do not reimplement \`query-local\` or \`query-multi\`. Keep existing help/parse behavior and error JSON contracts compatible.

### Required new tests

- \`tests/vip_fvs/unit/test_query_batch_contract.py\`
- \`tests/vip_fvs/integration/test_batch_retrieval_three_arm.py\`
- \`tests/vip_fvs/integration/test_batch_cli_synthetic.py\`

Tests must exercise production boundaries using deterministic fake embedders, in-memory doubles, and optionally a real test-created temporary SQLite + \`vectors.f32\` index. They must never decode any media.

### Optional in-scope extensions

Only if necessary to prove compatibility, you may ADD tests to:
- \`tests/vip_fvs/integration/test_multi_source_retrieval.py\`
- \`tests/vip_fvs/unit/test_query_modality.py\`
- \`tests/vip_fvs/integration/test_three_profile_product_path.py\`

Production modifications beyond the six exact production paths above are **not authorized** in this task. If a verified integration defect requires additional production paths, stop that subproblem with \`BLOCKED_SCOPE\`, preserve completed independent work, and report.

No edits to:
- \`.github/**\`, \`requirements/**\`, \`schemas/**\`, \`config/**\`;
- \`docs/**\` (including this task);
- \`src/gate0/**\`, \`src/gate1/**\`, \`src/gate2/**\`, \`src/gate3/**\`;
- \`src/vip_fvs/multi_source_retrieval.py\`, \`source_adapter.py\`, \`semantic_index.py\`, \`coordinator.py\`, \`local_semantic.py\`;
- \`experiments/**\`;
- any existing historical test fixture, certificate, evidence carrier, receipt, versioned model space or index format.

---

## 4. Overall functional contract

The system must support:

\`Explicit Query Catalog → Validated Synthetic Runtime(s) → Existing Multi-source Manifest + Existing Local Index → Read-Only Retrieval → Manifest-bound Candidate Rows → Deterministic Lab Report\`

The single-arm command queries one existing index with one explicit fake profile. The three-arm command queries **three separate existing generation roots** using three distinct validated fake model profiles. Both commands have a strict non-production claim banner.

No pipeline stage may call:
- source discovery, filesystem scanning or video directory traversal;
- \`index_source\`, \`index_local_source\`, \`index_multi_source_manifest\`;
- source-file open/probe/hash/decode;
- any real model loader, processor/tokenizer, device initialization or provider;
- a Gate-3 refinement/edit/render function.

The only index operation is the already-established \`engine.query\` against a previously committed local generation.

A query catalog is **input text only**, not evidence of an authorized Gate-0 corpus or a frozen experimental protocol.

---

## 5. Workstream W1 — Closed query catalog and deterministic identity

Build \`query_batch.py\` with a small immutable typed interface; use the project's dataclass/standard-library conventions.

### 5.1 Input JSON shape

Accept exactly:

\`\`\`json
{
  "schema_version": "vip-lab-query-catalog-v1",
  "catalog_id": "synthetic-catalog-01",
  "queries": [
    {"query_id": "q-001", "text": "a dancer landing from a grand jeté"},
    {"query_id": "q-002", "text": "a close-up of an orchestra conductor"}
  ]
}
\`\`\`

The schema version is **lab-only**, not a canonical Gate-0 schema amendment. Do not create new files under \`schemas/\`.

### 5.2 Strict parsing and refusal

- Reject missing, additional or wrong-type top-level fields.
- Reject missing, additional or wrong-type query fields.
- Reject empty catalog, empty query list, duplicate IDs, blank text, embedded NUL.
- Query IDs must be bounded, readable, path-free identifiers; avoid accepting path traversal.
- Preserve original ordered query IDs.
- Preserve user text exactly unless existing query contract requires a specific validation/normalization; do not silently rewrite queries or synthesize labels.
- Reject JSON duplicate keys using \`object_pairs_hook\` with fail-closed detection.
- Read ONLY the explicitly named query catalog file.
- Bound file bytes and query count with small **lab-only resource ceilings**: for example ≤2 MiB catalog input, 1–64 query records, 1–50 top_k. Use constants and dedicated tests. These are NOT proposed production/global limits.
- Guard integer boolean confusion (\`True\` is not \`1\`).
- Use UTF-8, reject invalid JSON, invalid encoding and non-finite JSON numbers if present.
- If semantically duplicated query texts appear under distinct query IDs, preserve both identity rows. For one underlying engine query keyed by text, call the engine once per **distinct** text or another proven safe strategy, then re-associate candidate rows with their original query IDs in input order. Never silently collapse distinct query IDs.

### 5.3 Identity

- Use canonical JSON serialization (sorted keys, compact separators, UTF-8).
- Compute a deterministic SHA-256 digest of the validated catalog content.
- The digest means **lab input identity**, not authenticated human approval, corpus freeze, or cryptographic identity of source media.
- If canonicalization would alter the meaning of a query, refuse rather than substitute.
- Separate \`catalog_id\` (human label) from the SHA-256 digest (content identity).

### 5.4 Tests

- Valid/invalid shape matrix, duplicate keys, duplicate IDs, duplicate TEXT with different IDs, order preservation, UTF-8 and Turkish characters, NUL and pathlike IDs, size ceiling, non-finite input, repeated digest.
- Do not confuse a catalog digest with source revision digest or model weights SHA.

---

## 6. Workstream W2 — Three-model synthetic runtime factory

Implement \`synthetic_profiles.py\` using established source seams:

- \`ModelProfile\`, \`validate_model_profile\`, \`profile_semantic_space\`;
- \`build_fake_profile_runtime\` for V2 Base and V2 SO400M;
- \`local_semantic.checked_runtime\` and the existing synthetic V1 embedding helpers where appropriate.

Explicit closed IDs:

- \`vip-v1-siglip-base-224\` → 768D, image 224 / patch 16.
- \`vip-v2-siglip2-base-224\` → 768D, image 224 / patch 16.
- \`vip-v2-siglip2-so400m-384\` → 1152D, image 384 / patch 14.

**Canonical V1 representation policy is special:** \`device_backend="cpu"\`, \`precision_policy_id="v1-float32"\`, \`precision_policy_version=1\`. Do not copy the V2 \`pytorch-cpu\`/SigLIP2 representation policy onto V1. The previous AI Studio attempt made exactly that mistake; GitHub CI caught \`MODEL_PROFILE_V1_REPRESENTATION_POLICY_UNSUPPORTED\`.

The V2 text identity labels are synthetic. Do not invent authentic text preprocessing, tokenizer IDs, attention masks, pooling, model class, weights revision or processor behavior. The provisional contract explicitly records these as not yet observed.

**Critical invariants:**

1. V1 and V2 Base must remain semantically distinct although both are 768D.
2. SO400M must remain 1152D (4608-byte float32 rows), not truncated to 768D.
3. Fake runtimes are explicit and never become real-mode runtimes.
4. Do not load any model, inspect model assets/cache, call torch, contact network, or open any source media.
5. Reject malformed profile JSON before accessing the index.
6. Preserve the actual \`ModelProfile\` constructor and real existing exception semantics.
7. Avoid copying existing fake embedding implementation into a second generator.
8. Do not introduce CLI choices that could enable implicit authentic-mode execution.

### Test coverage

Check dimensions, semantic-space ID separation, repeated deterministic identity, V1-specific representation policy, invalid V2 text contract refusal, profile/model/processor digest mismatch, no model or media effects.

Do not claim vectors represent actual semantics. This factory supplies test doubles only.

---

## 7. Workstream W3 — Read-only single-arm batch retrieval

Build \`batch_retrieval.py\` as an **additive consumer** of \`retrieve_multi_source\`. Do not change the existing function or its candidate dataclasses.

Inputs:
- an already parsed catalog from W1;
- one \`MultiSourceManifest\` from \`source_adapter.load_multi_source_manifest\`;
- one existing local \`index_root\`;
- one explicitly checked fake runtime with its exact semantic space;
- an injected \`SemanticIndexEngine\` (production default is the established local index engine);
- bounded \`top_k\`.

The orchestrator must:

1. Refuse malformed catalog, manifest, runtime/space mismatch, top_k, and engine capability **before** querying.
2. Build the generation identity from the engine's established \`build_generation_spec\` (never fabricate or guess it).
3. Use only \`retrieve_multi_source\` for manifest-bound candidate creation.
4. Batch distinct query text efficiently using the existing sequence API, while preserving every original query ID and ordered result.
5. Preserve engine-provided ranking within each query. Do not sort by an arbitrary new score algorithm.
6. Preserve each hit's \`source_path\`, \`source_sha256\`, \`revision_id\`, \`content_id\`, \`rank\`, \`score\`, \`source_sample_pts\`, \`source_timebase_num\`, \`source_timebase_den\`, and thumbnail status when present.
7. Distinguish two occurrences of the same content at different exact locators; never collapse them by content digest.
8. Refuse a hit with a locator or digest not present in the supplied manifest.
9. Keep every candidate \`evidence_class="MATCHED"\` and \`binding_eligible=False\`.
10. Never interpret a semantic hit as an exact cut, measured frame, human label or editorial approval.
11. Return an immutable or well-validated structured batch result that can be serialized by W5.
12. Avoid unordered sets or ungrounded hidden filtering in result production.

Failure semantics:
- A runtime/space or generation mismatch must refuse before text embedding or scoring if the underlying index contract can enforce that ordering.
- A hit/provenance integrity error must refuse the **whole batch** rather than emit a partially trusted success report.
- No index mutation, index rebuild, source scanning or fallback to another generation.
- Avoid pretending that an unverified manifest digest proves live source content; this is a match to the provided manifest **record**, not a fresh media rehash.

### Tests

Use synthetic \`MultiSourceManifest\` and \`SourceManifestEntry\` values. Test:
- 1, 2 and 64 queries;
- duplicate-text/different-ID behavior;
- independent query ordering and rank;
- empty hits and missing engine keys;
- wrong manifest hit digest/path;
- identical content digest at two locators;
- float NaN/infinite score refusal;
- integer source PTS + rational timebase preserved exactly;
- no \`index_source\`, no image embedder, no media source open;
- stable repeated canonical report payload on identical inputs.

Use only fake engines or test-created persisted index data, not real video.

---

## 8. Workstream W4 — Explicit synthetic three-arm comparison

Build \`three_arm_batch.py\` as a small orchestrator using the W3 single-arm function.

### 8.1 Three declared arm IDs

Use exactly these lab arm labels and identities:

- \`VIP_V1_BASE\` → \`vip-v1-siglip-base-224\`.
- \`VIP_V2_BASE\` → \`vip-v2-siglip2-base-224\`.
- \`VIP_V2_SO400M\` → \`vip-v2-siglip2-so400m-384\`.

An arm is independently configured with:
- one \`model_profile_json\` path,
- one existing \`index_root\`,
- one explicit multi-source manifest path,
- one fake checked runtime,
- one derived generation and semantic-space identity.

### 8.2 Input arm map

A lab-only JSON shape, read from one explicitly specified file:

\`\`\`json
{
  "schema_version": "vip-lab-three-arm-v1",
  "arms": [
    {"arm_id": "VIP_V1_BASE", "model_profile_json": "v1-profile.json",
     "index_root": "v1-index", "manifest": "v1-manifest.json"},
    {"arm_id": "VIP_V2_BASE", "model_profile_json": "v2-base-profile.json",
     "index_root": "v2-index", "manifest": "v2-manifest.json"},
    {"arm_id": "VIP_V2_SO400M", "model_profile_json": "so400m-profile.json",
     "index_root": "so400m-index", "manifest": "so400m-manifest.json"}
  ]
}
\`\`\`

Paths above are only examples of **synthetic lab test fixture paths**; they are NOT real paths or assets to download/create from the public Internet.

- Reject unknown/missing/duplicate arm IDs; allow input arm order to vary but output use fixed documented order.
- Bind arm ID to validated \`ModelProfile.profile_id\` exactly.
- Read only the named JSON and **existing index storage**, never a source/media locator.
- Reject any attempt to reuse one index generation under a different semantic-space identity.
- Explicitly refuse any real-mode operation, missing fake selection or unrecognized model profile.
- Do not treat metadata symmetry or dimensional similarity as compatible embedding spaces.
- Use each arm's own runtime, generation and manifest; never pass one arm's text vectors to a different arm.
- A single input catalog is used for all three arms. Verify exact catalog digest and ordered query IDs are identical.
- Preserve independent per-arm candidate rows, source-native locator PTS/timebase and original rank.
- No normalized cross-arm score comparison, no winner, no percent improvement, no metric-backed model selection, no benchmark verdict.
- If any arm fails, overall report is NOT_SUCCESS with explicit refusal; do not silently report only the arms that succeeded as an accepted comparison.

### 8.3 Mandatory provenance

Each arm's report includes:
- arm ID and profile ID,
- model identity as a declared synthetic profile,
- semantic-space ID and generation ID,
- provided manifest digest,
- query catalog digest,
- counted query IDs and candidate rows,
- \`fake_runtime_used=true\`,
- explicit \`synthetic_only=true\` flag and \`authentic_model_evidence=false\`.

The report must never claim its synthetic scores are comparable retrieval quality. Do not call the task an actual three-way model benchmark.

### Tests

- all 3 closed profiles and 768/768/1152 dimensions;
- explicit V1/V2 Base 768D cross-space refusal;
- swapped profile file under an arm ID;
- swapped index root under a different arm;
- missing arm and duplicate arm;
- one arm fails, no success artifact;
- repeated run produces deterministic, byte-equivalent canonical output where the input is identical;
- no real media/model/network activity.

---

## 9. Workstream W5 — Deterministic report and bounded failure envelope

Implement \`batch_report.py\` as **pure report building and validation**, rather than a new persistence framework or claimed production reliability subsystem.

### Report contract

Every successful report must have:

- \`schema_version\` (explicit lab v1);
- \`kind\` (\`SINGLE_ARM_SYNTHETIC_BATCH\` or \`THREE_ARM_SYNTHETIC_BATCH\`);
- \`status="SYNTHETIC_ONLY"\`;
- \`benchmark_status="NOT_RUN"\`;
- \`model_evidence="NOT_OBSERVED"\`;
- \`gate_decision="NOT_AUTHORIZED"\`;
- \`catalog_id\`, \`catalog_digest\`, ordered query IDs;
- one or three structured arm records;
- exact nonbinding candidates with source sample locators;
- a deterministic \`report_digest\` of a canonical JSON payload that excludes only the digest field itself;
- a clear limitations array, e.g. \`NO_AUTHENTIC_MODEL_INFERENCE\`, \`NO_REAL_SOURCE_MEDIA\`, \`NO_HUMAN_LABELS\`, \`NO_CROSS_ARM_WINNER\`, \`NO_GATE_PROMOTION\`.

Any \`NOT_OBSERVED\` here is a **state marker**, not a sixth evidence class. These labels belong to the *report's availability/scope metadata*, not the candidate evidence taxonomy.

A report digest proves only agreement with the **bytes and validation rules of that report**, not independent authenticity of source files, weights or judgments.

### Verify path

Offer a pure \`verify_batch_report\` function (and optionally a **lab-only** CLI \`verify-batch-report\` if it fits existing parsing without scope creep) that:

- checks exact structural shape and known version;
- recomputes the report digest;
- checks query/arm ordering, no duplicate arm or query IDs;
- validates candidate attribution to a query ID and arm;
- checks candidate rank positive, score finite, PTS int (not bool), timebase rational positive;
- refuses \`binding_eligible=True\`, \`MEASURED\` promotion and any edit-boundary interval fields;
- checks catalog/report digest consistency without claiming external sources were observed;
- rejects unexpected additional evidence classes and fields;
- never resolves or opens source media paths.

No hidden source rehash, no provider and no real model evidence.

### Reliability and repeatability preparation

- Fail closed on malformed input before opening any index.
- Bound memory input via the W1 lab caps and bounded \`top_k\`.
- Exercise corrupted JSON and incomplete arm lists.
- Prove a repeated identical **synthetic** query produces deterministic output (under deterministic injected engine).
- Prove a refusal never produces a report carrying \`status="SYNTHETIC_ONLY"\` as success.
- Inject faults into each arm (exception, corrupted hit, missing manifest match), verifying no partial success.
- Do not add queueing, database migrations, ANN, daemon, caching, background agents or restart claims.
- Do not promote these checks to representative Gate-2 acceptance.

**Do not write to the index or mutate persistent store.** The CLI may print one canonical JSON report to stdout. The requirement is deterministic report serialization, not production file persistence.

---

## 10. Workstream W6 — Additive CLI commands and closed authority behavior

Extend \`src/vip_fvs/cli.py\` carefully.

### Command 1: query-batch-synthetic

Required arguments:
- \`--catalog\` path to explicit lab query catalog JSON;
- \`--manifest\` path to explicit existing multi-source manifest JSON;
- \`--index-root\` path to an existing local generation;
- \`--model-profile-json\` explicit validated closed synthetic profile JSON;
- \`--fake-embedder\` **must be explicitly present**;
- \`--top-k\` integer within lab bound.

This path must:
1. validate the query catalog and fake-only intent before index access;
2. load the explicit manifest using the existing loader;
3. construct the checked fake runtime using W2;
4. call W3 with the persistent semantic engine;
5. construct W5 report;
6. print exactly one canonical JSON success report to stdout.

### Command 2: query-three-arm-synthetic

Required arguments:
- \`--catalog\` path as above;
- \`--arm-map\` path to W4 closed arm map;
- \`--fake-embedder\` explicitly present;
- \`--top-k\` within bounds.

Run W4, then W5; emit exactly one JSON success report. No authentic model arguments are accepted.

### CLI refusal contract

- No implicit \`--fake-embedder\` default.
- No real mode fallback or parameter alias to \`prepare-real\`/other real commands.
- No compatibility break to existing \`query-multi\`, \`query-local\`, \`index-local\`, \`prepare-real\`, \`resume-real\` or previews.
- Reject undeclared image/video-reference modalities explicitly; do not coerce to text.
- Do not silently accept index roots that do not match the declared generation.
- Refusal must exit nonzero, print one non-success error JSON object with a stable error code/message, and never emit a successful report.
- Do not fabricate an output report when the underlying engine raises.
- Avoid intercepting broad \`SystemExit\` or swallowing CLI parse errors as success.
- Existing legacy command behavior remains identical; check parser before/after using new tests.

No new external package dependency. Prefer standard library plus already installed NumPy/pytest for tests.

---

## 11. Workstream W7 — Adversarial / non-regression test matrix

**All new production files must have meaningful tests.** Use pytest parametrization and focused helpers instead of 1,000 lines of duplicated assertions.

### Input validation cases
- invalid JSON, invalid UTF-8, duplicate JSON keys;
- unknown/missing/extra catalog fields;
- duplicate query ID;
- duplicate text under distinct query IDs (both output rows retained);
- pathlike/empty IDs and very large inputs;
- bool for numeric \`top_k\`, zero, negative or above lab max;
- missing/malformed arm map, duplicate arm labels, wrong profile label.

### Representation cases
- three profile IDs have exact geometry;
- V1 vs V2 Base same 768D but distinct semantic-space IDs;
- SO400M 1152D not truncated;
- changed processor/model revision/profile ID refuses incompatible generation;
- fake runtime cannot be escalated into real model inference;
- no package download/device initialization.

### Retrieval cases
- exact manifest locator AND SHA match;
- duplicate-byte occurrences at different exact paths remain different candidates;
- query rank/order and query ID attribution;
- no source-path re-resolution that merges occurrences;
- missing query result, non-finite score, bool PTS, invalid timebase refuse;
- nonbinding \`MATCHED\` and no edit boundary;
- engine.query only, never engine.index_source;
- index manifests/SQLite/vector files unchanged by query.

### Report integrity cases
- deterministic canonical JSON report;
- tampering with payload or digest refuses;
- cannot change \`MATCHED\` to \`MEASURED\`;
- cannot set \`binding_eligible=true\`;
- cannot insert exact cut/end frame fields;
- partial arm failure does not return a success report;
- report states \`NOT_RUN\` and no winner;
- no timestamps derived from nominal FPS.

### CLI cases
- valid single-arm and three-arm synthetic commands using temp fixtures;
- parser has existing commands unchanged;
- fake-only requirement;
- incorrect/missing profile file;
- one arm generation mismatch;
- unsupported modality;
- no real media open/probe/model load.

Test inputs must be tiny generated in-memory JSON, fake embeddings and \`tmp_path\` SQLite/vector data. A filename ending in \`.mp4\` may be used as an **opaque synthetic manifest locator**, but the tests must never parse or decode it.

---

## 12. Implementation order and dependency discipline

Implement these in a single task **in the following order**, because their interfaces are dependent:

1. **Preflight:** inspect real source and existing tests; list what is already done; note any ZIP/SHA uncertainty.
2. **W1:** query catalog parser and tests.
3. **W2:** synthetic profile checked-runtime factory and tests.
4. **W3:** batch retrieval orchestrator and tests.
5. **W4:** three-arm orchestrator and tests.
6. **W5:** deterministic report builder/verifier and tests.
7. **W6:** CLI wiring, without editing existing command behavior.
8. **W7:** adversarial and integration tests.
9. **Static review:** detect unresolved imports, wrong APIs, unsupported dataclass keyword args, erroneous error strings and unsafe side effects.
10. **Final report:** all files, capabilities, unresolved issues and expected hosted CI.

Stages can be implemented in one model turn, but **never start a downstream module against an invented upstream interface**. Validate actual code definitions as you write.

### Learn from last lab exercise

Last time, the first generated tests did not collect because they imported a nonexistent symbol \`CLOSED_PROFILE_IDS\`. The test suite then expected nonexistent \`IndexSummary\` fields and error strings, used wrong V1 precision policy and wrong CLI argument name. These mistakes were caught by GitHub Actions and corrected without production edits.

For this much bigger job, **inspect exact constructor field names, function signatures and error codes before using them**. Do not make up source APIs. Use exact existing \`query-multi\`, \`retrieve_multi_source\`, \`ModelProfile\`, \`SearchHit\` and \`IndexSummary\` contracts.

---

## 13. STRICT NO-TEST-EXECUTION instruction inside Google AI Studio

Your assignment is to WRITE CODE and WRITE TESTS.

- **DO NOT run pytest locally.**
- **DO NOT run integration scripts or CLI commands.**
- **DO NOT install packages, provision environments or download dependencies.**
- **DO NOT run ffmpeg/ffprobe, model loaders or external providers.**
- **DO NOT push to GitHub or rewrite the remote repository.**
- **DO NOT modify .github workflow files.**

You may perform an offline syntax-only \`ast.parse\` / \`compile(..., "exec")\` on changed Python files, if supported; that is NOT proof of imported dependencies, correct interfaces or passing tests.

The Owner will push this task's changed files to \`video-intelligence-pipeline-2\`. GitHub Actions will then test them on Python 3.11 and 3.14, and independent Codex review follows.

If tests cannot be run in AI Studio, record \`AI_STUDIO_PYTEST=NOT_EXECUTED_BY_DESIGN\`, **not PASS**.

---

## 14. Hosted CI and acceptance

The LAB already has:

\`.github/workflows/vip-ai-studio-synthetic-ci.yml\`

Before this task it verified the existing B08 + selected synthetic compatibility suite:

- 146 baseline tests per Python version.
- 39 three-profile tests per Python version.
- Both Python 3.11 and Python 3.14 green at historical lab SHA \`0c5eb05ab6de2adefa8377d198c7eae9bf7a7d74\`.

The lab controller will extend CI to select the three required MEGA-02 test files when this task's source is present. If you do not create those test files, hosted CI should refuse an incomplete handoff.

**Accept only if:**
1. CI actually executed against the exact pushed lab SHA.
2. The three required MEGA-02 test files exist and ran (not skipped).
3. The existing baseline suite still passes.
4. New tests pass on **both** 3.11 and 3.14, not just one version.
5. There is independent review of generated production code, including nonbinding retrieval evidence, private-source safety and contract preservation.
6. Output accurately says synthetic only, no authentic model evidence and no experiment/benchmark winner.

Passing CI is NOT permission to integrate into original VIP. It is a lab candidate.

---

## 15. Explicit forbidden shortcuts and rejected alternatives

Reject all of the following:

- One giant file that mixes catalog parsing, model loading, retrieval, evaluation, rendering, and CLI.
- Reimplementing \`retrieve_multi_source\` or existing SQLite index/search engine under a new name.
- Invented model behavior, tokenizer vocabulary, projector/pooling semantics, real-model assets or fake quality benchmarks.
- Comparing cosine scores across unrelated model embedding spaces as if they were directly calibrated.
- Rewriting V1 existing index model, altering serialized storage formats or schema names.
- Making untrusted semantic timestamps exact edit boundaries by \`seconds × nominal FPS\`.
- Promoting a candidate from \`MATCHED\` to \`MEASURED\` without source-native evidence.
- Adding human labels, fabricated positive queries, fake editorial decisions or fake Reviewer IDs as real evidence.
- Accessing protected media or adding new provider/cloud/online interactions.
- Indexing source content during a query-only operation.
- Automatically fetching a missing model generation instead of failing closed.
- Implementing a queue, server, background service, browser UI or ANN without workload evidence.
- Editing original repository's WBS checkboxes, Gate decisions, adopted specs, historical source receipts or PRs.
- Marking Gate 0/1/2/3 completed or accepted.
- Deleting existing tests to make CI green.
- Claiming all B00–B11 blocks completed because this lab feature is working.

---

## 16. Final delivery checklist and Turkish report

Return the complete result in Turkish with:

### A. Source snapshot and implementation basis
Actual read files and imported snapshot identity. Be honest if \`.git\` absent.

### B. Pre-implementation audit
What exact behavior already existed, and the genuinely missing product interfaces added.

### C. Architecture and interface summary
Show:
- \`query_batch\` input/output and validation;
- \`synthetic_profiles\` three-profile factory;
- \`batch_retrieval\` read-only result;
- \`three_arm_batch\` distinct per-arm generations;
- \`batch_report\` digest, claims and verifier;
- two CLI commands and their explicit fake-only behavior.

### D. Exact changed files
One path per file, additions/modifications, no vague claims.

### E. Test suite authored
List each test function/group and important refusal scenario. Distinguish scripted tests from executed tests.

### F. Verification
Always print:
\`AI_STUDIO_PYTEST=NOT_EXECUTED_BY_DESIGN\`.
If syntax-only checks ran, separately report command and actual result. Never call syntax checks "integration PASS".

### G. Safety and evidence
Explain why query execution cannot mutate or decode sources, why the three model spaces are isolated, and why PTS/timebase is only locator evidence.

### H. Partial blockers and remaining work
Identify any unresolved source-contract gap, missing ZIP source, out-of-scope API, or requirement needing original Owner adoption.

### I. Lab handoff
Explicitly name the minimum new test files that GitHub Actions must run and remind the Owner **not to publish entire reduced ZIP by destructive synchronization**.

Use one of:
- \`IMPLEMENTED_UNVERIFIED\`
- \`PARTIAL_BLOCKED\`
- \`NOT_IMPLEMENTED\`

Do not claim completion, acceptance or benchmark readiness.

**STOP AFTER THIS ONE LARGE TASK. Do not start B01–B04 S5, protected archive runs, authentic model experiments, production export, or another mega task.**
