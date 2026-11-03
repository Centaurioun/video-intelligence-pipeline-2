# VIP V2 SigLIP2 Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Repository override:** VIP's current `AGENTS.md` explicitly prefers independent, dependency-safe rolling-frontier execution and does **not** select stock per-inner-task subagent review automatically. The owner must select the execution method after reviewing this plan; follow repository-specific orchestration where it overrides this generic skill recommendation.

**Goal:** Extend the completed local-first Video Intelligence Pipeline with separately reproducible native SigLIP2 Base and SigLIP2 SO400M semantic-retrieval representations, preserving exact V1 behavior, source/PTS/editing evidence contracts, and rollback.

**Architecture:** One canonical VIP product codebase, a closed set of validated representation profiles, existing checked image/text callable runtime and SemanticSpace contract, and one model-width-aware float32 SQLite/vector indexing engine. First preserve and refresh V1; migrate to V2 Base; extend to SO400M; freeze three independent candidates for a later, **separately planned and authorized** benchmark. Spike repositories remain read-only technical evidence, not copied applications.

**Tech Stack:** Python, NumPy float32, SQLite, pytest, FFmpeg/ffprobe, local-only Hugging Face Transformers/PyTorch native inference with explicit Apple MPS, optionally separate Metal-kernels runtime for future Q4. Use **exact environment locks proven at execution**; do not invent unverified V2 Base dependency versions.

**Spec:** `docs/superpowers/specs/2026-10-09-vip-v2-siglip2-integration-design.md`  
**Binding direction:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`  
**Baseline preservation:** `docs/migrations/siglip2-post-completion/31_2026-10-09_V1_POST_DESIGN_BASELINE_PRESERVATION_RECEIPT.md`  
**Plan status:** **OWNER_APPROVED_FOR_PLANNING; IMPLEMENTATION NOT AUTHORIZED**. The owner accepted the exact reviewed plan blob `78127a9199a912531d5b2240eed66e93814d83f3` through the durable owner decision on PR #69; PR #69 merged at `7f4a5ce1baf7de2aa580f1043502458336bf57fe`. This successor documentation version records that approval and does not replace or claim to be the originally reviewed blob.

## Global Constraints

1. **Exact preserved V1 code and design:** `preservation/vip-v1-post-v2-design-20261009` points to **3586eeaa904fc5a2e6a2745078611886f482f3de**. Do not move/delete this ref. Anchor any implementation worktree to that explicit SHA unless a new owner-approved source SHA supersedes it.
2. Read current `AGENTS.md`, `docs/INDEX.md`, four `docs/project/` handoff/protocol files, ADR-0002, spec, refresh protocol, T001–T026 acceptance matrix, and current execution resource policy before starting. Verify live Git state and worktree cleanliness; no destructive reset/clean/force.
3. The preserved branch is a **Git code/reference copy**, not a checkpoint/index/environment backup. Do not mark full V1 runtime reproducibility PASS without local model/runtime/test evidence.
4. The **post-completion refresh receipt** (using `30_post-completion-refresh-receipt-template.yaml`) and checklist 26 remain hard entry gates for Gate B/full migration, Task 2 onward, and all model/runtime/media/provider/benchmark/promotion work. The sole possible exception while full Task 0 remains blocked is the accepted Task 1 scope under Gate A, and only after the ADR and all coordinated subordinate amendments are owner-accepted at an exact candidate and canonically adopted, a fresh exact-main scoped Task 1 decision is independently accepted, and one separate explicit owner execution authorization binds the exact Task 1 files/operations, execution method, branch/base SHA, and expiry/supersession rules. A blocked receipt remains blocked and is never rewritten or treated as Gate A readiness. Without every Gate A precondition, stop before Task 1 source edits or tests.
5. **V1 -> native V2 Base -> native V2 SO400M -> separate three-way benchmark** (ADR-0002 order). May schedule independent non-model prep concurrently but must not promote an evidence-dependent candidate early.
6. No model download, provider/cloud egress, protected/real archive execution, 400-hour indexing, production render/export, Gate promotion or dependency mutation merely from this plan. Real model acquisition/forward and any real-media step require current **specific authorizations** and pass their own preflights.
7. Source immutable; semantic timestamps are MATCHED candidates, not edit points. Frame precision requires measured source-native integer PTS/timebase. Never derive VFR frames from seconds × nominal FPS.
8. Keep V1 historical SiglipModel/SiglipProcessor adapter and its existing 768-D fixtures. Float32/L2 index values only, with precisely **3072 bytes per 768-D row** and **4608 bytes per 1152-D row**. No cross-space embeddings, cosine score comparisons or silent fallback.
9. SO400M native frozen model identity from spike: `google/siglip2-so400m-patch14-384`, upstream `c65677ac77ca25276518923f7c58cbf5d81ea602`, checkpoint SHA-256 `9f4f4a49f908ef0c979bce8ff5a5c0e88882dc6c5dc4304387cbbd152558e2c2`; **384x384**, patch **14**, **1152-D** normalized float32 output. Treat first precision as a separately chosen and verified **FP16 or FP32** reference. Q4 mixed treatment is **272/328 quantized, 56 FP16, group size 32** and requires separate backend/identity verification. Q8 real inference **NOT_VERIFIED**. Do not mix precision-generated indexes.
10. No direct editing of canonical main in an implementation worktree; exclusive writer per path/shared contract, isolated branches, frequent small commits, TDD for each behavior change, systematic debugging on unexpected failures, independent feature review, fresh suite verification before integration.
11. This is **not** the three-arm benchmark execution plan. Later human labels, B16/B17 freeze, dataset/source authority, winner decision and full-archive indexing remain separate.
12. The 2026-10-09 broad user approval authorized **preservation and plan preparation**, not unlimited future software/model/archive execution. Review and explicit execution method are required before code begins.

## Review Focus

Five failure cases especially easy to omit; each is assigned an explicit regression below:

- **Same width but different model:** V1 768-D and V2 Base 768-D must have different immutable semantic spaces; Task 1 `test_v1_and_v2_base_768_spaces_never_match`.
- **Crash tail with wider rows:** 1152-D truncated/extra uncommitted bytes must never become searchable, nor be “repaired” with 3072-B arithmetic; Task 2 `test_1152_tail_reconciles_only_uncommitted_bytes`.
- **Misleading valid text vectors:** tokenizer BOS/EOS/padding mismatch must fail validation even if a vector has unit norm; Task 4 `test_siglip2_text_special_token_contract_rejects_inconsistent_ids`.
- **Unauthorized source path triggers model initialization:** source-use permission must be checked **before** opening a real V2 runtime; Task 5 `test_rejected_source_does_not_open_v2_model`.
- **MPS memory/fallback:** requested MPS unavailable/guard fails must block instead of loading on CPU or opportunistically shrinking safety reserve; Task 7 `test_so400m_memory_or_mps_blocked_without_load`.

---

## Before code: frozen baseline and implementation-gate checklist

**Evidence baseline for the proposed 2026-10-11 plan review:** exact canonical main `748818e867ce08ccc2367bad21df7d83eaf51d70`, preserved V1 `3586eeaa904fc5a2e6a2745078611886f482f3de`, refresh `6396779e397dc9dba659f4887471de4c6d30aced`, artifact identity `989c1bc6923833a11cfd11b7b756ef1f4ffbe192`, authentic synthetic MPS run `634bfed47aec8464c8ca61b15c376f2950c21060`, gap reconciliation `229d08f564fb8c21a7a119fc900eaac82cb64cd0`, current runtime receipt `ce3f570016f3f13e9091fb6989f3a9d3ea783c7d`, and cross-repository comparison `61e22acffcc3dcfeddeaa2f4a2b40e0f8693c74a`. These receipts report 811 distinct model-free passes and, separately, 1,290 historical G03 regression passes; they are not rerun here. The one-pair authentic local synthetic MPS result is bounded evidence, not semantic acceptance. The current runtime inventory makes checklist F07 `PASS_CURRENT_RUNTIME_RECEIPT_ONLY`; historical full environment reconstruction remains unproven. V2 Base identity and authorization and tokenizer semantic correctness remain unresolved.

**Allowed planning precondition:** obtain owner approval of this plan and choose execution method. Task 1 is software implementation associated with the V2 migration program, not documentation-only preparation. Its only possible model-free entry while full Task 0 remains blocked is the separate Gate A exception stated above; a fresh scoped A–D/E–G assessment and independent decision review do not themselves authorize edits. One separate explicit owner execution authorization must bind the same readiness decision and exact Task 1 file/operation scope, execution method, branch/base SHA, and expiry/supersession rules. Absent all of those conditions, report `TASK1_PREPARATORY_ENTRY_BLOCKED` and refrain. Task 2 onward and every real model/runtime/media action remain behind Gate B/full Task 0 and their applicable authorizations.

## Task 0: Post-completion refresh and exact V1 baseline readiness (documentation / verification prerequisite)

**Files:**
- Read: `docs/migrations/siglip2-post-completion/19_POST_COMPLETION_REFRESH_PROTOCOL.md`, `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`, `30_post-completion-refresh-receipt-template.yaml`
- Create (on future authorized execution branch): `docs/migrations/siglip2-post-completion/32_2026-10-09_POST_COMPLETION_REFRESH_RECEIPT.yaml` (name may be a versioned date suffix if used later; do not overwrite a prior receipt)
- Modify upon verification: `docs/migrations/siglip2-post-completion/03_V1_BASELINE_SNAPSHOT.md`, `07_MIGRATION_SURFACE_SNAPSHOT.md`, `08_HARDCODE_AND_ASSUMPTION_REGISTER.md`, `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md`, `14_TEST_AND_ACCEPTANCE_MATRIX.md`, `18_STALENESS_AND_REVERIFY_REGISTER.md` where evidence actually changes

**Interfaces:** Consumes preservation SHA `3586eeaa...`; produces reviewed `refresh_receipt` with required PASS/BLOCKED status, final code-symbol/test map, and exact V1 model/runtime provenance.

- [ ] **Step 1 — Verify live refs.** On the execution machine read remote URL, clean status, fetched `main`, and preservation branch SHA; compare to preserved SHA. Expected: immutable preservation ref is unchanged.
- [ ] **Step 2 — Refresh final-V1 evidence.** Follow **all 13 numbered steps** of `19_POST_COMPLETION_REFRESH_PROTOCOL.md` in order, including Step 12 design re-entry and Step 13's blocked-or-passing receipt disposition; record completion SHA, model/revision/weights/processor/preprocessing identity, acceptance suite commands/results, actual runtime, FFmpeg/ffprobe identity, refreshed primary-source evidence, and remaining gaps. Distinguish historical receipt evidence from fresh local measurements. Step 9 checkpoint identity remains `BLOCKED` until separate acquisition authorization and verified local identity exist.
- [ ] **Step 3 — Verify baseline tests.** Determine actual root `python` interpreter and `pytest` entrypoint in that environment. Candidate first commands, run from repository root and adjust only with documented environment evidence:
  `PYTHONPATH=src:experiments python -m pytest -q experiments/persistent_local_index/tests tests/vip_fvs`
  plus governed `scripts/verify-gate0.py`, `scripts/verify-gate1.py`, and `scripts/verify-workspace.sh` as applicable; capture exact exit codes and inherited failures. **Do not claim “all pass” if inherited verifier or tooling blocks.**
- [ ] **Step 4 — Emit refresh receipt and readiness decision.** Complete the actual 30-template instance with exact source/runtime/test/gate facts; map 26 checklist A–G individually, including anything not observed. Verify YAML parses, all required fields present, and there is no unbacked PASS.
- [ ] **Step 5 — Review and commit documentary refresh only.** This Task 0 refresh does not authorize source-code work. If required readiness fields remain blocked, Gate B/full migration stays BLOCKED; Task 1 can proceed only through the separately adopted, independently accepted Gate A decision and matching owner execution authorization defined above. No forced completion claim or no-op fake receipt.

## Task 1: Closed, validated three-profile semantic-space contract

**Files:**
- Create: `experiments/persistent_local_index/model_profile.py`
- Modify: `experiments/persistent_local_index/model_space.py` only as necessary for V2 compatibility while preserving V1 persisted identity semantics
- Tests: `experiments/persistent_local_index/tests/test_model_profile.py` (new), `test_model_space.py` (existing)

**Interfaces:**
- Produces: `ModelProfile` frozen dataclass (profile_id, upstream model ID/revision, asset identities, image/text contract, width, output dtype, device/backend/precision identity); `validate_model_profile(profile: ModelProfile) -> None`; `profile_semantic_space(profile: ModelProfile) -> SemanticSpace`; `profile_row_width_bytes(profile: ModelProfile) -> int`.
- V1 projection must preserve the exact V1 SemanticSpace fields/digest in preexisting generations. For V2, distinct **effective representation identity** (including preprocessing and a separately versioned precision policy) must feed the canonical SemanticSpace ID without mutating existing V1 manifest format. Use a versioned explicit profile identity field mapping rather than arbitrary concatenated “same-model” labels. If this cannot be achieved without a schema version change, design and review that migration before code.

- [ ] **Step 1 — RED:** Write `test_v1_profile_recreates_preserved_semantic_space`, `test_v1_and_v2_base_768_spaces_never_match`, `test_so400m_profile_width_is_4608_bytes`, `test_incomplete_digest_or_revision_fails_closed`, and `test_changed_tokenizer_or_precision_changes_space`. Assert exact V1 field equality, distinct space IDs, and 3072/4608 row-byte results.
- [ ] **Step 2 — Run:** `PYTHONPATH=src:experiments python -m pytest -q experiments/persistent_local_index/tests/test_model_profile.py`. Expected intentional RED against the pre-change implementation.
- [ ] **Step 3 — GREEN:** Add minimal frozen profile validation and deterministic profile-to-existing-SemanticSpace conversion. Keep V1 constructor behavior intact; reject unresolved, mutable or unsupported profile metadata. Use `dtype="float32"` and normalization `"l2"`.
- [ ] **Step 4 — Verify:** rerun focused tests plus existing `test_model_space.py`. Expected PASS for both suites before review.
- [ ] **Step 5 — Commit:** profile/types/tests only; record exact source SHA and schema compatibility disposition.

## Task 2: Profile-derived float32 vector write, commit, and crash-recovery geometry

**Files:**
- Modify: `experiments/persistent_local_index/storage.py`, `indexer.py`
- Tests: `experiments/persistent_local_index/tests/test_storage.py`, `test_indexer.py`, `test_source_lifecycle.py`

**Interfaces:**
- Consumes: `GenerationSpec.space.embedding_dim`, fixed allowable float32 and Task 1 derived width.
- Existing `reconcile_vector_tail(paths, conn, row_width_bytes: int)` remains, but all production callsites receive derived width.
- Extend `_validate_vectors(normalized_vectors: np.ndarray, expected_rows: int, *, expected_dim: int) -> np.ndarray`.
- Extend `append_source_segment(..., expected_dim: int)` without a silent production default; update callsites and tests. The implementer must inspect current positional/keyword usage before finalizing interface.

- [ ] **Step 1 — RED:** Add `test_1152_append_commits_4608_bytes_per_row`, `test_1152_tail_reconciles_only_uncommitted_bytes`, `test_1152_wrong_width_rejected_before_write`, `test_768_legacy_append_and_restart_preserved`. Assert physical+SQLite committed bytes after restart and invalid shape refusing without modifying previous committed prefix.
- [ ] **Step 2 — Run:** `PYTHONPATH=src:experiments python -m pytest -q experiments/persistent_local_index/tests/test_storage.py experiments/persistent_local_index/tests/test_indexer.py`. Expected at least new 1152 cases RED on existing 768 literals.
- [ ] **Step 3 — GREEN:** Derive all row-byte math at the generation boundary; thread through `index_inputs`, `index_one_source`, append/validate and tail reconciliation. Do **not** alter SQLite's single-writer/commit authority or truncate a valid prefix when dimensions mismatch.
- [ ] **Step 4 — Verify:** focused files, source-lifecycle regression, `test_search.py` and `test_search_materialization.py`. Expected PASS, 768/1152 isolation retained.
- [ ] **Step 5 — Commit:** storage/indexer/tests only; flag shared-contract delta for dependent branches.

## Task 3: Model-width-aware query and deterministic fake-vector test seam

**Files:**
- Modify only when required: `experiments/persistent_local_index/search.py`, `src/vip_fvs/retrieval_adapter.py`, `experiments/persistent_local_index/cli.py`
- Tests: `experiments/persistent_local_index/tests/test_search.py`, `test_search_materialization.py`, `tests/vip_fvs/unit/test_retrieval_adapter.py`

**Interfaces:** consumes `SemanticSpace.embedding_dim` and Task 1 profiles; real query remains same-`SemanticSpace` float32 normalized vectors. Fake-vector dimension is supplied explicitly and never invents a real profile.

- [ ] **Step 1 — RED:** Add `test_exact_top_k_1152_vector_rows`, `test_wrong_space_or_768_query_refused_against_1152`, `test_fake_vectors_repeatable_at_768_and_1152`.
- [ ] **Step 2 — Run:** `PYTHONPATH=src:experiments python -m pytest -q experiments/persistent_local_index/tests/test_search.py tests/vip_fvs/unit/test_retrieval_adapter.py`. Expected RED only where real coverage missing; if existing search already passes, record “existing green coverage” rather than manufacturing a code edit.
- [ ] **Step 3 — GREEN only if needed:** Parameterize fake vector generator and CLI tests; avoid rewriting already-dynamic search. Keep exact tie-breaking and no cross-space raw score comparison.
- [ ] **Step 4 — Verify:** above tests plus `test_search_materialization.py`, no mixed-index consumption.
- [ ] **Step 5 — Commit:** only changed files/tests. This task can be independently reviewed alongside Task 2 if no overlapping writer paths.

## Task 4: Native SigLIP2 Base processor/tokenizer and model adapter (offline synthetic and mocked first)

**Files:**
- Create: `experiments/persistent_local_index/siglip2_native.py`
- Tests: `experiments/persistent_local_index/tests/test_siglip2_native.py`
- Reference only: [SO400M native diagnostic](https://github.com/Centaurioun/vip-siglip2-so400m-browser-spike/blob/32722b227e81a5595239d46d65b7a52a4504ae94/native/diagnostic.py), `native/tokenization.py`, and Base browser provenance (do **not** import/browser-link them).

**Interfaces:**
- Produces `open_siglip2_session(profile: ModelProfile, model_root: Path, *, device: str) -> Siglip2Session` (only if a fully checked local bundle is supplied);
- `Siglip2Session.encode_image_paths(paths: Sequence[Path]) -> np.ndarray`;
- `Siglip2Session.encode_texts(texts: Sequence[str]) -> np.ndarray`.
- Keep exact selected profile width, float32/L2 outputs, image preprocessing owned by processor, exact token IDs/mask/truncation/pad/pooling identity, and MPS/CPU device refusal rules. Actual session interface may adapt to avoid duplicate `embedding.py` machinery but must remain specified and reviewed before dependent Task 5.

- [ ] **Step 1 — RED (no weights):** Add `test_siglip2_rejects_mutable_or_wrong_model_bundle`, `test_siglip2_disallows_remote_or_remote_code`, `test_siglip2_text_special_token_contract_rejects_inconsistent_ids`, `test_siglip2_mask_pad_truncation_pooling_contract`, `test_encoder_rejects_wrong_width_nonfinite_or_zero`, `test_mps_requested_unavailable_refused`.
- [ ] **Step 2 — Run:** `PYTHONPATH=src:experiments python -m pytest -q experiments/persistent_local_index/tests/test_siglip2_native.py`. Expected RED for new contract before implementation; do not create a misleading RED by missing torch/pytest.
- [ ] **Step 3 — GREEN:** Implement thin native AutoModel/AutoProcessor load/encode with local_files_only=True, trust_remote_code=False, use_safetensors=True, full asset digest before/after open; reject incomplete tokenizer/model config. No model weights acquire. Use mock/fake processor objects for tests and do not alter V1 Gate0 historical adapter.
- [ ] **Step 4 — Verify:** focused module, existing `test_embedding.py` and `test_local_model.py`. Explicitly record tokenizer BOS/EOS 49406/49407 warning discrepancy as unresolved until reference evidence proves behavior; do not claim semantic correctness from numerical test.
- [ ] **Step 5 — Commit:** adapter and tests only.

## Task 5: Wire the checked V2 runtime and model-profile selection into VIP FVS/CLI

**Files:**
- Modify: `experiments/persistent_local_index/embedding.py`, `src/vip_fvs/cli.py`
- Modify only if proven necessary: `src/vip_fvs/local_semantic.py`, `src/vip_fvs/retrieval_adapter.py`
- Tests: `tests/vip_fvs/unit/test_local_semantic.py`, `tests/vip_fvs/integration/test_product_index_query.py`, `tests/vip_fvs/integration/test_cli_acceptance.py`, `experiments/persistent_local_index/tests/test_cli_e2e.py`

**Interfaces:**
- Produces `build_checked_profile_runtime(profile: ModelProfile, model_root: Path, *, device: str) -> CheckedLocalSemanticRuntime` or existing equivalent; one source of truth constructs SemanticSpace for index/query/prepare paths.
- Integrates Task 4 image/text methods as exact callables; preserves existing `index-local`, `query-local`, `query-multi`, `prepare-real` authorization ordering and explicit fake mode.

- [ ] **Step 1 — RED:** Add `test_v1_cli_default_preserved`, `test_v2_base_cli_selects_its_own_semantic_space`, `test_rejected_source_does_not_open_v2_model`, `test_query_uses_indexed_profile_not_default_v1`, `test_profile_mismatch_fails_before_embedding`.
- [ ] **Step 2 — Run:** `PYTHONPATH=src:experiments python -m pytest -q tests/vip_fvs/integration/test_product_index_query.py tests/vip_fvs/integration/test_cli_acceptance.py`. Expected RED for new V2 features, pre-existing V1 tests stay green.
- [ ] **Step 3 — GREEN:** Add one explicit closed profile flag/config selector, preserve existing V1 no-new-flag behavior, validate source authorization **before** real model load, and keep fake mode an explicit test-only selection.
- [ ] **Step 4 — Verify:** targeted FVS + CLI suites and `tests/vip_fvs/unit/test_real_source_service.py`. Confirm no renderer/Gate3 behavior modifications.
- [ ] **Step 5 — Commit:** CLI/session wiring and tests, no media payload.

## Task 6: V2 Base candidate freeze and bounded native acceptance (separately authorized runtime stage)

**Files:**
- Add evidence receipt only after actual authorized execution: `docs/migrations/siglip2-post-completion/33_V2_BASE_RUNTIME_ACCEPTANCE_RECEIPT.yaml` (version if necessary)
- Tests: `experiments/persistent_local_index/tests/test_siglip2_native.py`, `test_cli_e2e.py`, `tests/vip_fvs/integration/test_local_semantic_synthetic.py`

**Interfaces:** consumes exact `google/siglip2-base-patch16-224` checkpoint revision, local bundle hash/processor inventory, resolved code/runtime provenance, and Task 4/5 session.

- [ ] **Step 1 — Permission gate:** Confirm separately authorized native checkpoint acquisition **if absent** and real model load. Do not infer permission from documentation publication. If no frozen V2 Base local bundle, mark `BLOCKED_ASSET_AUTHORIZATION` and stop this task; Tasks 1–5 synthetic work cannot claim runtime eligibility.
- [ ] **Step 2 — Freeze exact checkpoint:** Verify official immutable revision, checkpoint SHA-256, all processor/tokenizer asset SHA/digests, output width **from actual config and runtime** (expected 768), default text semantics and exact executable/dependency locks. Do not use browser-ONNX artifact identity as native authority.
- [ ] **Step 3 — Execute one owner-approved bounded smoke:** explicitly local image+text fixture only, authentic attention mask, no cloud, record normalized [N,768] values, device/fallback/latency/memory, proven paired text/image reference behavior.
- [ ] **Step 4 — Verify and review:** real smoke + all relevant tests, no space reuse, disabled egress; store sanitized receipt and exact candidate SHA. If BOS/EOS/token semantics unresolved, disposition **BLOCKED_SEMANTIC_CORRECTNESS**, not PASS.
- [ ] **Step 5 — Freeze candidate:** only after both synthetic suite and separately authorized real runtime acceptance. Otherwise stop with evidence, no empty “success” commit.

## Task 7: SO400M fixed 384/1152 native extension (synthetic first; runtime separately authorized)

**Files:**
- Modify: `experiments/persistent_local_index/model_profile.py`, `siglip2_native.py` only in profile-specific locations
- Tests: `experiments/persistent_local_index/tests/test_siglip2_native.py`, `test_model_profile.py`, `test_embedding.py`

**Interfaces:** uses Task 6 verified V2 Base candidate as source base; new SO400M profile must be exact `google/siglip2-so400m-patch14-384` at upstream `c65677ac77ca25276518923f7c58cbf5d81ea602` with weights SHA-256 `9f4f4a49f908ef0c979bce8ff5a5c0e88882dc6c5dc4304387cbbd152558e2c2`, image input 384, patch 14, output 1152.

- [ ] **Step 1 — RED:** Add `test_so400m_image_input_384_patch14`, `test_so400m_has_1152_columns`, `test_so400m_uses_distinct_space_and_index`, `test_so400m_memory_or_mps_blocked_without_load`, `test_so400m_wrong_tokenizer_identity_rejected`. Mock model and memory snapshots; no checkpoint bytes required.
- [ ] **Step 2 — Run:** `PYTHONPATH=src:experiments python -m pytest -q experiments/persistent_local_index/tests/test_siglip2_native.py experiments/persistent_local_index/tests/test_model_profile.py`. Expected new profile tests RED pre-implementation.
- [ ] **Step 3 — GREEN:** register the narrow known SO400M geometry in the existing V2 native path; enforce known checkpoint hash and local processor identity; FP16/FP32 model dtype explicitly chosen and identity-bound; no Q4 dependency required for this stage. For Apple MPS, retain safe resource guard with **>=2 GiB post-load reserve**, no automatic CPU fallback or unsafe egress.
- [ ] **Step 4 — Verify:** synthetic tests for both 768/1152 profiles, V1 regression. Add (but do not automatically execute) a guarded authentic smoke entrypoint if not already present.
- [ ] **Step 5 — Commit:** only SO400M profile/runtime test deltas; exact Q4 behavior stays in spike until separately accepted.

## Task 8: Explicitly authorized SO400M real MPS acceptance, with precision evidence

**Files:**
- Receipt after execution: `docs/migrations/siglip2-post-completion/34_SO400M_RUNTIME_ACCEPTANCE_RECEIPT.yaml`
- Tests: same Task 7 tests; FVS bounded synthetic acceptance

**Interfaces:** requires validated Task 7 SO400M runtime, exact known local checkpoint, explicit owner authorization for model use; separate per-precision/space index identifiers.

- [ ] **Step 1 — Authorization and fresh hardware gate:** verify model use authorized, actual Mac MPS present, dependency lock exact, no fallback, local model SHA and processor assets intact, conservative available memory and >=2-GiB reserve.
- [ ] **Step 2 — Confirm tokenizer semantics:** independently explain BOS/EOS 49406/49407 vs tokenizer 0..31999, pad/mask and final-sequence-position pooling behavior; require reference test before treating retrieval semantics as verified. If uncertain, stop at `NOT_VERIFIED`.
- [ ] **Step 3 — One bounded run per separately approved session:** if authorized, run selected FP16 or FP32 first (not both by default), synthetic images+texts only; inspect genuine execution status and MPS placement, effective dtype, 1152 outputs, memory/swap, numerical validity, correspondence; do not rerun unrelated Q4/Q8 arms.
- [ ] **Step 4 — Reconcile spike provenance:** compare actual VIP encoder output with frozen SO400M source reference under identical assets, tokenizer and precision; document any deviations, avoid claiming score parity without measured vector/ranking comparison.
- [ ] **Step 5 — Accept or block:** independent review and fresh focused/regression suite, commit sanitized receipt only on valid data. Do not promote merely because spike had previously reported MPS PASS.

## Task 9: Synthetic end-to-end FVS candidate and exact PTS/provenance isolation

**Files:**
- Tests: `tests/vip_fvs/integration/test_local_semantic_synthetic.py`, `test_product_index_query.py`, `test_multi_source_indexing.py`, `test_multi_source_retrieval.py`, `tests/vip_fvs/unit/test_refinement_adapter.py`, `tests/vip_fvs/unit/test_real_source_temporal_authority.py`
- Modify product FVS source/refinement code **only** on a separately approved, demonstrated contract break; defaults unchanged.

**Interfaces:** three candidate profiles/index roots with same synthetic source-sampling PTS; MATCHED semantic retrieval candidate must never become a measured source-native edit decision without existing refinement.

- [ ] **Step 1 — RED:** Add `test_three_profiles_same_source_separate_generation`, `test_cross_space_query_refused`, `test_retrieval_hit_preserves_integer_pts_timebase`, `test_semantic_hit_not_binding_edit_interval`, `test_unauthorized_real_source_unread_and_no_model_open`.
- [ ] **Step 2 — Run:** `PYTHONPATH=src:experiments python -m pytest -q tests/vip_fvs/integration/test_local_semantic_synthetic.py tests/vip_fvs/unit/test_refinement_adapter.py`. Capture failures; do not manufacture a test-red by misconfigured environment.
- [ ] **Step 3 — GREEN:** keep existing source/sample/refinement path where correct; fix only missing profile/invocation binding; preserve MEASURED vs MATCHED and no nominal FPS interpolation. No protected media.
- [ ] **Step 4 — Verify:** relevant real-source authorization and Gate3 unit suites with generated media where already supported, isolated index roots and immutable source hash.
- [ ] **Step 5 — Commit:** relevant tests/provenance binding only; no edit/render behavior change without new approved design.

## Task 10: Independent review, baseline comparison and versioned candidate handoff

**Files:**
- Create, only after accepted implementation: `docs/migrations/siglip2-post-completion/35_V2_CANDIDATE_HANDOFF_AND_ROLLBACK_RECEIPT.yaml`
- Read: `docs/migrations/siglip2-post-completion/27_POST_MIGRATION_VERIFICATION_CHECKLIST.md`, `16_VERSION_PRESERVATION_AND_ROLLBACK.md`
- Modify current project handoff only by independent reconciliation after evidence, following `docs/project/STATE_MAINTENANCE_PROTOCOL.md`.

**Interfaces:** complete candidate code SHA(s), V1 and V2 Base and SO400M exact model/runtime/processor semantic identities, per-profile index/generation names and validated rollback reference.

- [ ] **Step 1 — Fresh baseline difference:** compare against preserved `3586eeaa...`, prove no unrelated modifications to source/time/editorial/render contracts or historic V1 files; reject stale-base contract ownership collisions.
- [ ] **Step 2 — Full applicable regression:** run authoritative exact V1, persistent-index, FVS and affected Gate suites in the verified execution environment; capture commands, exit codes and inherited workspace checker findings. **No completion claim based on tests listed but not run**.
- [ ] **Step 3 — Independent code review:** review profile schema, real loader/tokens, storage 1152 write/recovery, fallbacks, authorization ordering, provenance and rollback. Resolve blockers via systematic debugging + new RED/GREEN tests within owner scope.
- [ ] **Step 4 — Freeze eligible candidate refs:** only after actual acceptance, record immutable SHA and matching model/index/runtime artifacts; check V1 preserved ref untouched. Do not mutate or delete existing refs.
- [ ] **Step 5 — Handoff:** record PASS/BLOCKED per model arm, scope boundaries, exact remaining permissions and evidence. Canonical main integration, benchmark activation and source access require the appropriate distinct owner approvals.

## Separate future project: frozen three-arm retrieval benchmark — NOT EXECUTABLE FROM THIS PLAN

After Task 10 eligible V1/V2 Base/SO400M states exist and authorization is explicit, write a **new** scoped Superpowers benchmark plan against:

- `docs/benchmarks/siglip-three-way/B00_BENCHMARK_CHARTER.md`;
- `docs/benchmarks/siglip-three-way/B16_PRE_EXECUTION_FREEZE_CHECKLIST.md`;
- exact same authorized source bytes and integer PTS/timebase sample plan (B17);
- preregistered queries, paired Turkish/English clusters, blinded graded human judgments, Success@1/5/10, nDCG, editorial usefulness/false positives, memory/latency/storage and paired analysis;
- exact independent index roots; raw cosine magnitude not compared across model spaces;
- separate owner decision for model winner, full archive, Gate promotion and production.

The V1 seven-query anchor is a useful diagnostic probe, not the sole unbiased winner rule.

## Dependency graph and allowed rolling-frontier scheduling

```text
Gate A (only if its exact adoption/review/owner-authorization conditions pass, including fresh evidence satisfying every Task 1-required A–D predicate under its unchanged pass criteria; unresolved or unsatisfied qualified status blocks)
  -> Task 1: profile contract
     -> Tasks 2–5: remain behind Gate B/full Task 0 and their own listed dependencies
Gate B: V1 post-completion full-migration readiness HARD GATE
  -> Task 1 under the ordinary full-migration sequence when Gate B is satisfied
  -> Task 2: width-safe writer/SQLite recovery
  -> Task 3: search/fake dimension tests (independent after Task 1)
  -> Task 4: V2 native text/image adapter (independent after Task 1)
  -> Task 5: runtime/CLI integration (depends Tasks 2,3,4)
  -> Task 6: V2 Base real acceptance (needs current model/runtime authorization)
  -> Task 7: SO400M profile extension
  -> Task 8: SO400M real MPS acceptance (needs current model-use authorization)
  -> Task 9: end-to-end profile/PTS regression (can run synthetic parts after Task 5)
  -> Task 10: independent review/handoff, complete after applicable candidate gates
  -> separately designed + authorized 3-arm benchmark
```

Do not manufacture artificial parallel work. Shared interfaces/model-space and storage contracts have one exclusive owner each; isolated execution worktrees and stable immutable candidate SHAs required. The repository's rolling BUILD/VERIFY/REPAIR frontier and resource lease policy supersede generic fixed subagent quotas. Heavy MPS calls are **serialized** and only scheduled after an explicit authorization and fresh safe memory preflight. Child work does not directly write protected canonical main.

## Self-review / explicit approval gate

- **Spec coverage:** V1 preserved, exact semantic/model profiles, tokenizer, loader, 768/1152 write/search, FVS+PTS, test/rollback, runtime/Q4 limits covered in Tasks 0–10. Broader archive, provider, editing, performance winner and benchmark execution correctly separate.
- **Known open factual dependencies:** the 811-pass model-free receipt and separate 1,290-pass G03 regression receipt are historical and were not rerun here; the refresh receipt exists at `229d08f564fb8c21a7a119fc900eaac82cb64cd0` but its outcome is `BLOCKED` and it does not clear readiness; complete historical runtime reconstruction remains unproven despite F07's current-runtime-receipt-only status; V2 Base exact native checkpoint and authorization, tokenizer semantic correctness, and future execution-method/permissions remain `NOT_OBSERVED/BLOCKED`.
- **Types/ownership:** model_profile -> model_space -> encoder -> checked_runtime -> indexer/storage/search -> FVS; historic V1 callable contract retained; Task 2 changes source storage shared contract and must be exclusively owned.
- **Red/green:** each behavior change has named failing tests, rerun command and minimal implementation step; no “PASS” asserted for tests not executed now.
- **Readiness:** **PLAN_WRITTEN_FOR_OWNER_REVIEW; IMPLEMENTATION_NOT_STARTED**. After owner reviews this plan, obtain chosen repository-compliant execution method and separately scope any model acquisition / real forward / protected media before implementation. Broad consent to planning is not blanket runtime authorization.

## Adopted pre-Gate-B synthetic exception — execution not authorized

**Status:** `OWNER_ACCEPTED — CANONICALLY_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The exact coordinated candidate `ae3939b9c0d98c24809246099c025bc3a60a0d50` / tree `11c9089016f9b0b1a8bd5ee2704d3022d74ef421` was adopted by PR #91 merge commit `25c29c07a8010db551a2ac08fcde72a9147c25d3`. This section supersedes only the blanket Task 2–5 Gate B entry wording above. The existing Gate B hard gate remains operative for all out-of-scope operations; Tasks 2–5 are not READY without subsequent exact per-slice grants and fresh base/interface checks. Adoption alone grants no execution.

**Current Task 1 dependency reference for this proposal (2026-10-19):** the reviewed Task 1 candidate is `ff23e6af46ced80297c8fbc124c6ddf0b0ed288a` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`; its exact accepted `model_profile.py` source blob is `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`. The candidate is represented on current canonical main `342e6fbaa25d28511844b274bce7f927e2c0420d` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`. Its interface review remains `ACCEPT_WITH_LIMITS` for the model-free synthetic interface only. These commit/tree/blob identities are provenance bindings, not a substitute for the exact review artifact or for checking the accepted interface at each consuming task's exact base. A future grant must cite that review evidence and verify its bound interface descriptor at the exact base; missing, stale, or mismatched evidence blocks that task. This reference establishes no authentic tokenizer/model semantics, Task 2–5 readiness, adoption, or execution grant.

Following adoption and a fresh exact contract/base/interface check, separate owner grants may cover these slices:

| Slice | Exclusive paths | Boundaries and dependencies |
|---|---|---|
| T2-SYN | `experiments/persistent_local_index/storage.py`, `experiments/persistent_local_index/indexer.py`, and tests `experiments/persistent_local_index/tests/test_storage.py`, `experiments/persistent_local_index/tests/test_indexer.py`, `experiments/persistent_local_index/tests/test_source_lifecycle.py` | After Task 1 interfaces are accepted at the exact base. Synthetic float32 vectors and test-managed temporary SQLite/vector files only; test 768/1152 profile-derived geometry, mismatch refusal and uncommitted-tail recovery. |
| T3-SYN | `experiments/persistent_local_index/search.py`, tests `experiments/persistent_local_index/tests/test_search.py`, `experiments/persistent_local_index/tests/test_search_materialization.py`; optionally `src/vip_fvs/retrieval_adapter.py` and `tests/vip_fvs/unit/test_retrieval_adapter.py` only when necessary and explicitly granted | After Task 1 interfaces at exact base; independent of T2/T4 on disjoint paths. Synthetic queries/vectors only; explicit width, fake-vector reproducibility and same-space top-k behavior. |
| T4-SYN | New `experiments/persistent_local_index/siglip2_native.py` and `experiments/persistent_local_index/tests/test_siglip2_native.py` | After Task 1 interfaces at exact base; independent of T2/T3. In-memory doubles/generated inputs only; validate interface and fail-closed shapes/values. No actual tokenizer, processor, checkpoint, model, cache, device or runtime semantics. |
| T5-SYN | `experiments/persistent_local_index/embedding.py`, `src/vip_fvs/cli.py`; `src/vip_fvs/local_semantic.py` only if necessary and explicitly granted. Tests: `tests/vip_fvs/unit/test_local_semantic.py`, `tests/vip_fvs/unit/test_real_source_service.py`, `tests/vip_fvs/integration/test_product_index_query.py`, `tests/vip_fvs/integration/test_cli_acceptance.py`, `experiments/persistent_local_index/tests/test_cli_e2e.py` | Serial after T2/T3/T4 exact interfaces are independently verified and accepted together. Requires a separate later exact grant. Side-effect-screen every selected test; prove no model open, asset read, cache access or network call. If service-order or negative guards cannot be proven, narrow the claim or defer T5. T5 never edits T3's optional retrieval-adapter paths. |
| T9-SYN | New `tests/vip_fvs/integration/test_three_profile_synthetic_space_contract.py` | **Governance documentation was merged by PR #86** (`dab471b768811a7c1e3791e4f79de4539bd12d33`); no execution grant exists. Serial after Task 1–5 interfaces are independently verified and accepted together at a fresh exact post-refresh base. The former base `1b55bea06dd580896cab3557ee3eaf47bec959b7` is historical. Current source-observation snapshot for this refresh: main `3d42ed625742c606d5d6773a3b9a6263ae27c379` / tree `cfd9f3dae3256778adf0a8288095a6012134d524`; this is not a future execution binding. A separate exact Owner grant is mandatory. Synthetic arrays, generated inputs, in-memory doubles, and test-managed temporary files only. Strictly test-only: the proposed assertions cover three isolated index generation roots under pure synthetic `SemanticSpace` identities (768 V1, 768 Base, 1152 Synthetic), fail-closed cross-space query refusal before text embedding or scoring, source-native integer PTS and rational timebase preservation without float-seconds truncation, non-binding `MATCHED` evidence, and fail-closed unauthenticated-source/real-model-path rejection before file or model open. Revalidate these assertions against the exact current interfaces; if the 1152-dimensional end-to-end assertion requires product-source changes, stop for separate authority. No product source in `src/` or `experiments/`, no model downloads, real loading/inference/MPS or hardware checks, real/protected media, benchmark, or canonical-main mutation. Task 0 and Gate B remain `NO_GO_BLOCKED`; this documentation row grants no execution. |


T2/T3/T4 can run concurrently only after each has its own exact grant and disjoint path manifest. Each exact candidate receives an independent VERIFY disposition; any REPAIR is limited to that slice's granted paths. T5 is not dispatched by the earlier grants. Each grant binds exact paths, operations, safe commands, environment, method, isolated branch/base SHA, expiry and supersession. The slices allow generated synthetic data and test-managed temporary files only. No dependency or lock/config changes, model/processor/cache access, acquisition, network/provider/cloud, loading/inference/MPS or hardware probes, real/protected media, benchmark, full archive, production integration, Gate promotion or canonical-main mutation. Any unsafe test is `NOT_RUN` with its reason. These slices establish no Task 0 predicate and do not change full Task 0/Gate B `NO_GO_BLOCKED`, H, the 56 A01–G05 dispositions, protocol Steps 1–13, Gate A Task 1 scope, or Tasks 6 onward. Synthetic evidence cannot satisfy real model/runtime/media gates.

The integration spec was compared and remains unchanged; it describes architecture/task interfaces and does not conflict with the conditional authority boundary above. An independent reviewer must review the exact coordinated candidate tree before owner decision.

## Proposed separate native-Base Task 4/5 source-only entry — not active

**Status:** `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The synthetic T4-SYN/T5-SYN rows above remain their own historical proposal. This additional conditional proposal concerns only residual fake-injected, model-free source editing/TDD for genuine native Base Task 4 and checked CLI Task 5; it does not promote synthetic evidence or change Task 2/3 requirements.

| Slice | Exclusive proposed source/test paths | Entry and bounded claim |
|---|---|---|
| Native Task 4 | `experiments/persistent_local_index/siglip2_native.py`; `experiments/persistent_local_index/tests/test_siglip2_native.py` | `EXACT_PER_TASK_GRANT AND (ACCEPTED_APPLICABLE_GATE_B OR EXACT_INDEPENDENTLY_REVIEWED_OWNER_ACCEPTED_AND_CANONICALLY_ADOPTED_TASK_SPECIFIC_SOURCE_ONLY_EXCEPTION)`. For this row, the exception must be the exact Task 4 source-only exception; Gate B never replaces the separate Task 4 grant. Before launch, require the independently accepted Task 1 `ModelProfile` interface fingerprint bound to the exact Task 4 source base. An exact previously accepted immutable source snapshot may establish it only when that snapshot's acceptance receipt/contract records and binds the accepted Task 1 interface fingerprint. Missing acceptance/fingerprint, stale base, or any mismatch is a hard stop; the planning-approved Task 1 plan alone is not interface acceptance. Fake-injected local-only loader/guarded adapter only. No model, processor, asset, cache, tokenizer, hardware, or device open/probe. |
| Native Task 5 | `experiments/persistent_local_index/embedding.py`; `src/vip_fvs/cli.py`; new `tests/vip_fvs/integration/test_native_base_cli_contract.py` | `EXACT_PER_TASK_GRANT AND (ACCEPTED_APPLICABLE_GATE_B OR EXACT_INDEPENDENTLY_REVIEWED_OWNER_ACCEPTED_AND_CANONICALLY_ADOPTED_TASK_SPECIFIC_SOURCE_ONLY_EXCEPTION)`. For this row, the exception must be the exact Task 5 source-only exception; Gate B never replaces the separate Task 5 grant. Before launch, bind accepted Task 2 and Task 3 interface fingerprints to the exact base; an exact already-accepted immutable source snapshot may establish these only if its accepted receipt/contract records and binds both fingerprints. Before Task 5 BUILD starts, its exact base must also bind either (a) an independently accepted Task 4 interface fingerprint whose acceptance receipt binds it to Task 4's exact source SHA, with that same fingerprint bound to Task 5's exact consuming base, or (b), only for overlapping Task 4 BUILD, an exact frozen Task 4 interface fingerprint independently reviewed and bound to Task 4's exact source base and Task 5's exact consuming base. Final verification requires the independently accepted Task 4 interface SHA to match that consumed fingerprint and retain the Task 1 interface binding; any Task 4 interface change makes Task 5 descendants stale and stops continuation pending rebind/review. Check source authorization before factory creation, preserve V1 no-flag behavior, and keep V1 768-D and V2 Base 768-D `SemanticSpace`/generation identities distinct. |

No other test path is implicitly granted. Neither task edits `model_profile.py`, V1 `local_model.py`, each other's paths, or main. Task 4 stops on missing/stale/mismatched Task 1 interface evidence or base; Task 5 stops on stale base/interface fingerprints. Fake-injected tests cannot establish authentic tokenizer semantics, preprocessing, mask/pooling, MPS/device behavior, or retrieval quality. No dependency/environment changes, network/provider, model/cache/asset reads, real/protected media, benchmark, Gate promotion, production/default promotion, or Task 6 onward. Task 0/Gate B remain `NO_GO_BLOCKED`; H, the 56 predicate identities/statuses, all 13 refresh steps, Gate A scope, and history remain unchanged. This proposal is not adoption, a grant, or READY status.
