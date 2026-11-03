# ADR-0002: Post-Completion SigLIP2 Migration and Three-Way Benchmark

## Status

**ACCEPTED — COMMITTED POST-COMPLETION WORK**

This decision is accepted and is intended to be executed **after completion of the current Video Intelligence Pipeline implementation based on `google/siglip-base-patch16-224`.**

The work described in this ADR is **not optional future research**. It is the agreed next model-evolution phase of the project after the current V1 implementation reaches its verified completion boundary.

This ADR does **not** authorize that work to begin now.

Current execution remains focused on completing the existing SigLIP1 Base implementation. Model acquisition, SigLIP2 migration, benchmark execution, protected/archive-media processing, and full-archive re-indexing remain deferred until their appropriate later execution stage and authorization.

---

## 1. Decision Summary

The project will follow this sequence:

1. **Complete and freeze the current pipeline using SigLIP1 Base**
   - `google/siglip-base-patch16-224`

2. **Migrate the completed pipeline to SigLIP2 Base**
   - `google/siglip2-base-patch16-224`

3. **Extend the SigLIP2 implementation to SigLIP2 So400m**
   - `google/siglip2-so400m-patch14-384`

4. **Preserve all three reproducible implementations long enough to run a controlled project-specific benchmark**

5. **Benchmark the three models on the same small, representative video corpus**

6. **Use the benchmark evidence to decide which SigLIP2 representation should become the preferred representation for later full-archive indexing**

The benchmark candidates will therefore be:

| Candidate | Model |
|---|---|
| **VIP V1 Base** | `google/siglip-base-patch16-224` |
| **VIP V2 Base** | `google/siglip2-base-patch16-224` |
| **VIP V2 So400m** | `google/siglip2-so400m-patch14-384` |

The historical SigLIP1 So400m model is **not part of the required benchmark**.

It may be studied later only if there is a specific need to separate the effect of model scale from the effect of the SigLIP2 training generation.

---

## 2. Why This Sequence Is Deliberate

The current SigLIP1 Base implementation is already embedded in the active project architecture, tests, provenance model and execution work.

Changing the representation now would reopen already-established work and create unnecessary risk before the current pipeline is complete.

Therefore:

> **The current project will first be finished with SigLIP1 Base.**

Only after that completion point will model migration begin.

This preserves a complete, working and reproducible baseline before introducing a new representation family.

The completed V1 implementation will also provide the reference against which the two SigLIP2 candidates are evaluated.

---

## 3. Stage 1 — Complete and Freeze VIP V1 Base

The current implementation shall continue using:

`google/siglip-base-patch16-224`

until the existing Video Intelligence Pipeline reaches its separately defined and verified completion boundary.

At completion, the project shall preserve an immutable identity for the V1 implementation, including as applicable:

- exact repository SHA and/or release tag;
- model identity;
- frozen model revision;
- model weights hash;
- processor/preprocessing identity;
- embedding-space definition;
- runtime/dependency identity;
- relevant verification evidence.

This state becomes:

**Video Intelligence Pipeline — V1 Base**

V1 Base must remain reproducible through the later benchmark.

It must not be destructively overwritten by the SigLIP2 migration.

---

## 4. Stage 2 — Migrate V1 Base to VIP V2 Base

After V1 Base is complete and frozen, the first migration shall target:

`google/siglip2-base-patch16-224`

The resulting implementation becomes:

**Video Intelligence Pipeline — V2 Base**

This is intended to be an evolutionary migration of the completed pipeline, not a rewrite of the application.

The project shall preserve all pipeline behavior that does not genuinely depend on the semantic representation.

Expected migration concerns include:

- model loading;
- processor/tokenizer loading;
- SigLIP2 text preprocessing;
- immutable model revision and weights identity;
- processor/preprocessing provenance;
- semantic-space identity;
- model-specific validation;
- focused regression tests.

The following subsystems must not be redesigned merely because the representation model changes:

- source inventory;
- source provenance;
- source immutability;
- source-native PTS/timebase handling;
- temporal refinement;
- candidate evidence;
- editorial decisions;
- edit-plan representation;
- rendering;
- technical QC;
- editorial QC.

SigLIP2 Base remains broadly aligned with the current Base representation class:

- 224-pixel fixed-resolution input;
- patch size 16;
- 768-dimensional embedding space.

However, **the SigLIP1 and SigLIP2 embedding spaces are still incompatible semantic spaces**, even when they have the same dimensionality.

Existing SigLIP1 embeddings therefore must not be reused as SigLIP2 embeddings.

---

## 5. Stage 2 Engineering Requirement — Remove Unnecessary Model Hard-Coding

The current repository contains implementation and test assumptions tied directly to the existing Base representation, including historical 768-dimensional constants.

During the V2 Base migration, the representation boundary shall be made sufficiently model-aware to support the already-planned So400m successor without requiring another broad architectural rewrite.

At minimum, model-dependent properties should be represented explicitly where required, including concepts such as:

- model identity;
- frozen revision;
- weights digest;
- processor identity;
- image preprocessing identity;
- text preprocessing contract;
- input resolution;
- patch configuration where relevant;
- embedding dimension;
- dtype;
- vector normalization.

This shall be a **targeted migration refactor**, not an unrestricted generic model framework.

Only abstractions needed by the agreed candidates should be introduced.

---

## 6. Stage 3 — Extend V2 Base to VIP V2 So400m

After V2 Base is working and independently verified, the project shall add:

`google/siglip2-so400m-patch14-384`

The resulting candidate becomes:

**Video Intelligence Pipeline — V2 So400m**

The So400m candidate materially differs from Base in model scale and visual representation parameters.

Important differences include:

- 384-pixel fixed-resolution image input instead of 224;
- patch size 14 instead of 16;
- 1152-dimensional embedding space instead of 768;
- substantially larger model/runtime requirements.

The V2 So400m work should reuse the already-established SigLIP2 integration from V2 Base.

It should **not** become a separately reimplemented copy of the complete Video Intelligence Pipeline.

Where the architecture permits it cleanly, the difference between V2 Base and V2 So400m should be confined primarily to the model/semantic-space profile and its corresponding runtime requirements.

---

## 7. Preservation Strategy

The project will temporarily preserve three independently reproducible states:

### V1 Base

`google/siglip-base-patch16-224`

### V2 Base

`google/siglip2-base-patch16-224`

### V2 So400m

`google/siglip2-so400m-patch14-384`

These should preferably be represented through immutable Git history, tags, candidate/release SHAs and isolated development branches/worktrees rather than three permanently duplicated repositories.

The objective is:

> **three independently runnable benchmark candidates, not three indefinitely diverging codebases.**

All three must remain reproducible until the comparison benchmark and its resulting model decision have been completed.

---

## 8. Mandatory Three-Way Project Benchmark

After V2 Base and V2 So400m are available, the project **will perform a controlled three-way benchmark**:

**V1 Base vs V2 Base vs V2 So400m**

This benchmark is a committed part of the post-completion migration sequence.

It will occur **before** selecting the preferred representation for full-archive re-indexing.

---

## 9. Benchmark Corpus

The benchmark will use a small frozen corpus drawn from the actual target domain.

The expected scale is approximately:

**10–20 representative videos**

rather than the complete approximately 400-hour archive.

The exact number will be frozen when the benchmark protocol is prepared.

The corpus should intentionally represent relevant variation such as:

- ballet;
- other dance styles;
- solo performance;
- group performance;
- small and large performer groups;
- close and distant framing;
- formation changes;
- stage movement;
- different costumes;
- different lighting conditions;
- visually crowded scenes;
- visually simple scenes;
- different camera positions where available.

The benchmark should be small enough to run quickly while broad enough to expose meaningful differences between candidate representations.

---

## 10. Controlled Comparison

All three candidates shall be evaluated under the same comparison conditions.

They must receive, as far as technically applicable:

- the same source videos;
- the same source revisions;
- the same sampling policy;
- the same measured source-native sample positions;
- the same PTS/timebase evidence;
- the same query set;
- the same relevance judgments;
- the same Top-K definitions;
- the same evaluation procedure.

The purpose is to isolate representation/model differences rather than accidentally measure different sampling or pipeline behavior.

---

## 11. What Will Be Measured

The benchmark shall evaluate both retrieval quality and operational cost.

At minimum, it should capture:

- Top-1 retrieval success;
- Recall@5;
- Recall@10 where useful;
- ranking quality such as nDCG where appropriate;
- human/editorial usefulness;
- irrelevant-result / false-positive behavior;
- performance on visually subtle performing-arts concepts;
- group/solo differentiation;
- composition/formation-related retrieval where supported;
- Turkish query performance;
- English query performance;
- indexing wall-clock time;
- query latency;
- cold-start behavior where relevant;
- warm-query behavior;
- peak/runtime memory burden;
- persistent embedding/index storage;
- model storage;
- operational stability;
- reproducibility.

The benchmark protocol may refine these measures before execution.

It must not alter the evaluation after seeing results merely to favor a particular candidate.

---

## 12. Public Benchmark Results Are Not the Project Decision

SigLIP2 has published evidence of improved performance over corresponding SigLIP models on general image-text retrieval and other vision-language benchmarks.

That evidence justifies testing SigLIP2.

It does **not** by itself select the model for this project.

The Video Intelligence Pipeline operates on a specialized archive involving dance, ballet, music and performing arts.

Therefore:

> **Project-specific benchmark evidence controls the final representation decision.**

Hugging Face likes, downloads, model popularity, parameter count or generic benchmark superiority alone are insufficient grounds for production selection.

---

## 13. Candidate Semantic Spaces Must Remain Separate

Each candidate shall have its own attributable semantic-space identity.

Embeddings produced by:

- SigLIP1 Base;
- SigLIP2 Base;
- SigLIP2 So400m

must never be silently combined into one vector space.

Even where two candidates have the same dimensionality, their embedding coordinates are model-specific.

Likewise, raw cosine scores across different semantic spaces shall not be treated as directly comparable quality scores.

Comparison shall occur through shared benchmark outcomes such as relevance, rank and retrieval success.

---

## 14. Benchmark Before Full-Archive Re-Indexing

The approximately 400-hour archive shall **not** be fully re-indexed with all three models merely to determine which one is preferable.

The sequence shall be:

**small benchmark first → model decision second → full-archive indexing later**

This prevents unnecessary processing of the full archive.

Once a preferred representation is selected, full-archive indexing may be performed under the authorization applicable at that time.

The initial full archive is expected to represent a largely one-time bulk indexing cost.

Subsequent newly arriving videos may then be indexed incrementally under the selected representation.

---

## 15. Decision After the Benchmark

The benchmark does not assume that the largest model must win.

Valid outcomes include:

### Outcome A — V2 Base is sufficient

If SigLIP2 Base gives the best practical quality/cost balance, it becomes the preferred active representation.

In that case, the extra compute cost of So400m may not be justified.

### Outcome B — V2 So400m provides a material advantage

If V2 So400m demonstrates a meaningful project-specific retrieval improvement, it may become the preferred representation despite its greater indexing/runtime cost.

### Outcome C — SigLIP2 does not justify migration

If neither SigLIP2 candidate provides a meaningful practical gain, the completed V1 Base implementation remains a valid reference and fallback.

This outcome is considered scientifically legitimate even though SigLIP2 performs better on public benchmarks.

---

## 16. Post-Benchmark Consolidation

After the benchmark and model decision, the project does not need to maintain three active application variants indefinitely.

The expected long-term direction is:

- preserve V1 Base as immutable historical/reproducibility evidence;
- maintain the selected SigLIP2 implementation as the active successor;
- if V2 Base and V2 So400m share a sufficiently clean model boundary, they may be exposed through one V2 application with validated model profiles rather than separate application copies.

Whether both SigLIP2 profiles remain user-selectable will be decided after the benchmark.

This consolidation happens **after**, not before, the three-way comparison.

---

## 17. Preserved Project Invariants

No model migration changes the core evidence architecture of the Video Intelligence Pipeline.

The following remain mandatory:

- semantic/model timestamps are candidate evidence only;
- exact edit boundaries require source-native PTS/timebase evidence;
- VFR frame positions must never be inferred from seconds × nominal FPS;
- source media remains immutable unless separately and explicitly authorized;
- evidence classes remain unchanged;
- model confidence does not silently upgrade evidence class;
- model identity and preprocessing remain attributable;
- incompatible semantic spaces remain isolated;
- provenance must survive model replacement;
- editorial decisions remain distinct from model inference.

A stronger semantic model improves retrieval capability; it does not gain temporal authority.

---

## 18. Explicitly Deferred Details

This ADR intentionally does not freeze:

- the exact 10–20 benchmark videos;
- the exact benchmark query set;
- final relevance labels;
- exact acceptance thresholds;
- exact future SigLIP2 checkpoint revisions;
- exact model hashes;
- hardware-specific benchmark timings;
- final batch sizes;
- full-archive indexing duration;
- whether V2 Base or V2 So400m ultimately becomes default;
- whether both SigLIP2 profiles remain exposed in the final application.

Those are evidence-dependent decisions for the later benchmark-design and execution stage.

---

## 19. Activation Trigger

The work in this ADR shall begin **after the current SigLIP1 Base Video Intelligence Pipeline has reached its verified completion boundary.**

The committed next sequence is:

**Complete V1 Base**

→ **freeze/preserve V1 Base**

→ **migrate to V2 Base**

→ **verify V2 Base**

→ **extend to V2 So400m**

→ **verify V2 So400m**

→ **run the frozen small-corpus three-way benchmark**

→ **record the comparative evidence**

→ **select the preferred representation**

→ **then consider separately authorized full-archive indexing**

This sequence is the agreed post-completion direction of the project.

**It is to be carried out after the current project implementation is finished.**

---

## Proposed Amendment 1 — Two-Stage Entry for Post-V1 VIP V2 Work

**Status:** `PROPOSED_FOR_EXACT_OWNER_REVIEW — NOT APPROVED — NOT ACTIVE — NOT AUTHORIZED_FOR_EXECUTION`

This append-only amendment proposal is prepared from the owner-accepted direction for contract-amendment preparation. It does not itself amend this ADR, activate Gate A, authorize Task 1, or approve any subordinate redline. It becomes part of this ADR only if the owner accepts the exact final ADR and coordinated subordinate contract candidate and those changes are canonically adopted together.

### A. Gate A — narrowly scoped post-V1 preparatory implementation

The owner may separately authorize a preparatory-code entry after verified V1 completion for the accepted migration plan's Task 1, **“Closed, validated three-profile semantic-space contract.”** This is software implementation associated with the V2 migration program. Its synthetic-only and model-free character does not make it documentation-only work or categorically outside migration.

Gate A is a narrow exception to the ordinary full-migration entry sequence. It may be considered despite a blocked full-migration receipt only after this amendment and every coordinated subordinate change have been accepted by the owner at an exact candidate SHA/tree and canonically adopted. It then requires a fresh exact-main Task 1 scoped-readiness decision, independent review accepting that decision, and a separate explicit owner execution authorization. The decision must freshly evidence every Task 1-required A–D predicate and determine that each is satisfied under that predicate's unchanged pass criteria; any required predicate that is FAIL, BLOCKED, unresolved, or qualified without meeting its existing pass criteria blocks Gate A. An explicitly permitted `NOT_APPLICABLE` remains only where the existing predicate allows it. Literal checklist `PASS` and qualified overlay statuses such as `PASS_WITH_LIMITS` or `PASS_PLANNING_ONLY` retain their existing distinct meanings and are never normalized or promoted by this amendment. The authorization must bind the accepted plan and decision, exact allowed files and operations, execution method, branch and base SHA, and expiry/supersession rules. Missing, stale, contradictory, or mismatched evidence means blocked.

Gate A may cover only the accepted Task 1 profile-contract work: frozen profile validation; deterministic mapping to the existing semantic-space contract; synthetic identity fixtures; model-free tests; V1 identity-preservation regression; independent feature review; and bounded verification, limited to Task 1's accepted file scope. It does not include Task 2 or later, dependency or environment changes, real model or processor identity/acquisition/load, inference or MPS, media, provider/cloud/egress, benchmarking, full-archive indexing, Gate promotion, or production integration.

Gate A is not documentation-only preparation, but it also does not establish V2 model/runtime readiness, clear any Task 0 predicate, change a blocked receipt, or authorize Gate B. The full Task 0 `NO_GO_BLOCKED` decision remains separate and unchanged.

### B. Gate B — full V2 migration and later stages

Gate B retains the existing full-migration sequence and every applicable Task 0, model, runtime, media, provider, benchmark, indexing, and promotion requirement. Task 2 and later remain behind the full-migration readiness gate. Real model/runtime/media operations continue to require their separately applicable current authorizations. Gate A cannot satisfy, waive, or substitute for any Gate B condition.

### C. Atomic activation and preserved strategy

Gate A is not effective unless all of the following are true: the owner accepts the exact final ADR and all coordinated subordinate contract changes; all those normative changes are canonically adopted; a fresh exact-main Task 1 scoped-readiness decision is independently accepted; and the owner separately authorizes Task 1 execution with matching files, operations, execution method, branch/base, and supersession rules. The model-free entry decision remains distinct from `GO_FOR_AUTHORIZED_MIGRATION_SCOPE`.

This proposal leaves unchanged the strategic sequence V1 Base → V2 Base → V2 So400m → separately authorized three-way benchmark; preserved V1 identity and reproducibility; distinct semantic spaces; all source-native PTS, immutability, provenance, and evidence-class rules; all historical decisions; and the existing full Task 0 and V2 runtime readiness gates. It is not a general waiver for migration implementation.

### D. Adopted Amendment 2 — model-free synthetic Tasks 2–5

**Status:** `OWNER_ACCEPTED — CANONICALLY_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The exact coordinated candidate `ae3939b9c0d98c24809246099c025bc3a60a0d50` / tree `11c9089016f9b0b1a8bd5ee2704d3022d74ef421` was adopted by PR #91 merge commit `25c29c07a8010db551a2ac08fcde72a9147c25d3` (parent 1 `342e6fbaa25d28511844b274bce7f927e2c0420d`). This adoption changes only the stated Task 2–5 entry wording. It grants no task execution, makes no slice READY, and does not authorize source writes or model/runtime/media/Gate/production work; each synthetic slice still requires its separate exact grant and fresh base/interface checks.

**Current Task 1 dependency reference for this proposal (2026-10-19):** the reviewed Task 1 candidate is `ff23e6af46ced80297c8fbc124c6ddf0b0ed288a` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`; its exact accepted `model_profile.py` source blob is `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`. The candidate is represented on current canonical main `342e6fbaa25d28511844b274bce7f927e2c0420d` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`. Its interface review remains `ACCEPT_WITH_LIMITS` for the model-free synthetic interface only. These commit/tree/blob identities are provenance bindings, not a substitute for the exact review artifact or for checking the accepted interface at each consuming task's exact base. A future grant must cite that review evidence and verify its bound interface descriptor at the exact base; missing, stale, or mismatched evidence blocks that task. This reference establishes no authentic tokenizer/model semantics, Task 2–5 readiness, adoption, or execution grant.

This adopted amendment supersedes only the blanket Task 2–5 entry wording in §B and the corresponding coordinated plan/activation wording. No Task 2–5 work is READY from adoption alone. Fresh post-adoption contract/base checks and exact owner grants for each slice remain required.

After those conditions, the owner may separately grant only the following synthetic slices: T2-SYN storage/indexer on `experiments/persistent_local_index/storage.py`, `indexer.py` and `tests/test_storage.py`, `test_indexer.py`, `test_source_lifecycle.py`; T3-SYN search on `experiments/persistent_local_index/search.py` and `tests/test_search.py`, `test_search_materialization.py`, with `src/vip_fvs/retrieval_adapter.py` and its unit test only if proven necessary and explicitly granted; T4-SYN mocked adapter on new `experiments/persistent_local_index/siglip2_native.py` and its new focused tests; and, later, T5-SYN wiring on `experiments/persistent_local_index/embedding.py`, `src/vip_fvs/cli.py`, optionally `src/vip_fvs/local_semantic.py` only if necessary and granted, and its named unit/integration/CLI tests. T2, T3 and T4 depend on accepted Task 1 interfaces at the exact base and may run concurrently on disjoint paths. T5 is serial after their exact interfaces are independently verified and accepted together, and requires a separate later grant.

The amendment permits synthetic arrays, generated inputs, in-memory doubles, and test-managed temporary files only. T2 may validate 768/1152 dimensions and 3072/4608-byte row geometry; T3 may validate dimension-aware deterministic fake-vector search; T4 may validate a mocked interface and fail-closed checks without implementing or asserting authentic tokenizer, processor, model, device, or runtime semantics. T5 may validate mocked selector/CLI wiring and source-authorization ordering only when its granted tests prove negative no-open, no-asset-read, no-cache-access, and no-network behavior. Its grant must include and side-effect-screen `tests/vip_fvs/unit/test_real_source_service.py`, or explicitly narrow the authorization-order claim to the exact safe tests granted. T3's optional retrieval-adapter paths are never T5 paths.

Each grant binds exact paths, operations, safe test commands, environment, method, isolated branch/base SHA, expiry, and supersession conditions. Every slice excludes dependency changes, asset/model/processor/cache reads or acquisition, network/provider/cloud activity, real loading/inference/MPS or hardware checks, real/protected media, benchmarks, full archive, production integration, Gate promotion, and canonical-main mutation by a worker. Unsafe tests are not run. No synthetic result is evidence that satisfies a Task 0 predicate or establishes authentic model/runtime/media readiness. Task 0 and Gate B remain `NO_GO_BLOCKED`; H, all 56 A01–G05 identities and statuses, all 13 refresh steps, Gate A's Task 1-only scope, the V1 → V2 Base → V2 So400m → separately authorized benchmark strategy, and historical evidence remain unchanged. Task 6 onward stays behind Gate B.

The complete coordinated amendment set is this ADR, the migration plan, authority/activation 01, checklist 26, protocol 19, entrypoint 00, launch packet 24, and handoff 25. The integration spec was compared and remains unchanged: it defines architecture and task interfaces, not execution authority or an incompatible activation rule. An independent reviewer must review the complete exact candidate tree and verify these boundaries and preserved decisions before owner acceptance. Amendment acceptance and canonical adoption are separate recorded owner acts.

## Proposed residual native-Base Task 4/5 source-only exception — not active

**Status:** `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. This distinct proposal covers only fake-injected, model-free source work for genuine native SigLIP2 Base Task 4 and checked CLI Task 5. It does not convert or supersede T4-SYN/T5-SYN. A later owner must accept and canonically adopt the exact independently reviewed coordinated tree. Each task also needs its own exact source/test/operations/environment/branch/base grant. Task 4 requires that grant and either accepted applicable Gate B or this adopted Task 4 exception, and before launch requires an independently accepted Task 1 `ModelProfile` interface fingerprint bound to its exact source base. An exact previously accepted immutable source snapshot may establish that interface only when its acceptance receipt/contract records and binds the accepted fingerprint. Missing acceptance/fingerprint, stale base, or mismatch is a hard stop; approval of the Task 1 plan for planning does not establish interface acceptance. Task 5 requires its separate grant and either accepted applicable Gate B or its adopted exception, plus the Task 2/3 interfaces and the Task 4 interface freeze described below before BUILD, and an accepted Task 4 interface for final verification. Adoption alone is no grant or READY state.

Task 4's exclusive paths are `experiments/persistent_local_index/siglip2_native.py` and `experiments/persistent_local_index/tests/test_siglip2_native.py`. Task 5's are `experiments/persistent_local_index/embedding.py`, `src/vip_fvs/cli.py`, and new `tests/vip_fvs/integration/test_native_base_cli_contract.py`. No other test path is implied. Neither task owns `model_profile.py`, V1 `local_model.py`, the other's paths, or main. Task 4 acceptance binds the independently accepted Task 1 `ModelProfile` interface fingerprint to its exact frozen source base (or its exact previously accepted snapshot receipt binding that fingerprint). Task 5 launch additionally binds accepted Task 2 and Task 3 interface fingerprints at its exact base (or a snapshot whose accepted receipt explicitly records those fingerprints), and final verification consumes the independently accepted Task 4 interface at its frozen SHA, whose acceptance binds Task 1's interface fingerprint. Stop on missing acceptance, stale base, or mismatched interface identity.

**Task 5 dependency freeze:** Before Task 5 BUILD starts, its exact base must bind either (a) an independently accepted Task 4 interface fingerprint whose acceptance receipt binds it to Task 4's exact source SHA, with that same fingerprint bound to Task 5's exact consuming base, or (b), only when Task 4 BUILD overlaps, an exact frozen Task 4 interface fingerprint independently reviewed and bound to both Task 4's exact source base and Task 5's exact consuming base. In either case, final Task 5 VERIFY requires the independently accepted Task 4 interface at the exact frozen SHA, matching the consumed fingerprint and retaining the Task 1 fingerprint binding. Any interface change makes Task 5 descendants stale; stop and rebind/review before continuing.

The bounded claim is fake-injected local-only loader/adapter and checked CLI wiring: source authorization before factory construction, preserved V1 no-flag behavior, and distinct V1 768-D versus V2 Base 768-D `SemanticSpace`/generation identities. This does not prove authentic tokenizer, processor preprocessing, masks, pooling, MPS/device behavior, or retrieval quality. No model/processor/asset/cache access, network/provider, environment mutation, real media, benchmark, Gate promotion, or Task 6+ work is included. Task 0/Gate B remain `NO_GO_BLOCKED`; H, all 56 predicate identities/statuses, all 13 refresh steps, Gate A's Task 1-only scope, and historical receipts remain unchanged.

### E. Proposed Amendment 3 — model-free synthetic Task 9 preparatory slice (T9-SYN)

**Status (refreshed 2026-10-19):** Governance text was merged by PR #86 at `dab471b768811a7c1e3791e4f79de4539bd12d33` from reviewed candidate `177b55df193f987d768ba0d029a79d451a531d32` / tree `0a4d9093b283a200e12a6cef0d8a70d3daff6da5`; PR #86 describes this as adoption of T9-SYN governance only. The preserved pre-adoption M3 adjudication record still says `PREPARED_FOR_EXACT_OWNER_ADOPTION`; that historical record is not rewritten. The mismatch between the merge record and the pre-adoption adjudication remains explicit. In either reading, T9-SYN has **no current execution grant** and is `NOT_AUTHORIZED_FOR_EXECUTION`.

The PR #86 merge is limited to the reviewed governance amendment and does not authorize T9-SYN execution. This 2026-10-19 refresh updates stale dependency references; this refreshed text itself remains subject to exact review and any required Owner adoption. Task 9 remains PARKED behind Gate B except for the bounded synthetic preparatory proposal described here. No adoption or documentation refresh supplies execution permission: fresh exact-base/interface checks and a separate exact Owner grant remain mandatory.

Any future grant may cover only the following synthetic slice: T9-SYN end-to-end multi-space regression test suite on new exclusive path `tests/vip_fvs/integration/test_three_profile_synthetic_space_contract.py`. The former base `1b55bea06dd580896cab3557ee3eaf47bec959b7` and its dependency fingerprints are historical and stale for current execution. The current source-observation snapshot is canonical main `3d42ed625742c606d5d6773a3b9a6263ae27c379` / tree `cfd9f3dae3256778adf0a8288095a6012134d524`; it is **not** a future execution binding because this documentation refresh may itself later be adopted. Before any T9-SYN grant, bind the exact post-adoption execution base and verify each accepted Task 1–5 interface and its acceptance evidence against that base. This slice is strictly test-only and owns no product source in `src/` or `experiments/`, no existing tests, and no canonical-main paths.

At the 2026-10-19 source-observation snapshot, the relevant source blobs are: Task 1 `experiments/persistent_local_index/model_profile.py` `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`; Task 2 `storage.py` `b769889559c7d51955b8218e75fa870d225d143e` and `indexer.py` `c2a9b0a0aa028e33ece1437c4880b0bfb9fb7f69`; Task 3 `search.py` `61ba5cb8a4b12398094eb90a25bffa9f29e68d64`; Task 4 `siglip2_native.py` `b494379d3127e3c4600da7b7e071cc61279951d1`; Task 5 `embedding.py` `91e3f152b7dddcf182335061e2692ce57f3cbf80` and `src/vip_fvs/cli.py` `cce15b1eef6c90e07e7c30b708f705831f861991`. These are Git byte identities, not by themselves accepted interface fingerprints. The future entry review must connect each required blob to its applicable acceptance/review record at the exact execution base; missing, stale, or mismatched evidence blocks entry. The proposed 1152-dimensional end-to-end assertion has not been revalidated against the current integrated T1–T5 seams; if it requires product-source changes, stop for separate scope authority rather than expanding the T9 test-only grant.

The amendment permits synthetic arrays, generated inputs, in-memory doubles, and test-managed temporary files only. T9-SYN may validate: (1) three isolated index generation roots under three pure synthetic `SemanticSpace` identities (768 V1, 768 Base, 1152 Synthetic); (2) fail-closed cross-space query refusal before text embedding or scoring; (3) source-native integer PTS and rational timebase preservation in search hit locators without float seconds truncation; (4) non-binding `MATCHED` evidence classification preventing automatic promotion to binding editorial boundaries without authoritative measured refinement; and (5) fail-closed rejection of unauthenticated sources and real model paths before file or model open.

The grant binds exact paths, operations, safe test commands, environment, method, isolated branch/base SHA, expiry, and supersession conditions. It strictly excludes dependency changes, asset/model/processor/cache reads or acquisition, network/provider/cloud activity, real loading/inference/MPS or hardware checks, real/protected media, benchmarks, full archive, production integration, Gate promotion, and canonical-main mutation by a worker. Unsafe tests are not run. No synthetic result is evidence that satisfies a Task 0 predicate or establishes authentic model/runtime/media readiness. Task 0 and Gate B remain `NO_GO_BLOCKED`; H, all 56 A01–G05 identities and statuses, all 13 refresh steps, Gate A's Task 1-only scope, the V1 → V2 Base → V2 So400m → separately authorized benchmark strategy, and historical evidence remain unchanged. Tasks 6–8 and authentic Task 9/10 stay behind Gate B.

The complete coordinated amendment set is this ADR, the migration plan, authority/activation 01, checklist 26, protocol 19, entrypoint 00, launch packet 24, and handoff 25. An independent reviewer must review the complete exact candidate tree and verify these boundaries and preserved decisions before owner acceptance. Amendment acceptance and canonical adoption are separate recorded owner acts.
