# VIP V2 SigLIP2 Integration — Architecture Design and Eight-Round Refinement

**Date:** 2026-10-09  
**Method:** Superpowers brainstorming, architectural path.  
**User decision:** architectural **direction approved** on 2026-10-09.  
**Written specification:** **OWNER_APPROVED_FOR_PLANNING** (2026-10-09 subsequent user approval). The written execution plan exists as a separate proposed artifact and is **PENDING_OWNER_PLAN_REVIEW**. No migration implementation is authorized by this approval.  
**Approval sequence:** The original 2026-10-09 publication preceded spec review; the owner subsequently responded “Tamam, ne gerekiyorsa onaylıyorum” to the stated next phase of preserving V1 and preparing the plan. Git ref preservation was completed separately and is documented in `docs/migrations/siglip2-post-completion/31_2026-10-09_V1_POST_DESIGN_BASELINE_PRESERVATION_RECEIPT.md`.  
**Scope:** design documentation and cross-repository evidence synthesis only.

## 0. Authority and current state

The owner explicitly requested that the detailed architectural evaluation be preserved in both repositories and published to their respective main branches. **Next phase, not this phase:** once both assessments are on main, take an immutable, independently verified copy/ref of the **post-documentation** canonical VIP main; subsequently create a Superpowers implementation plan for upgrading that preserved V1 pipeline with SigLIP2 findings. Do not take the copy during this documentation milestone; do not begin the upgrade.

**Live GitHub anchors observed before drafting:**

- Canonical product: Centaurioun/video-intelligence-pipeline, main at **455ef6908b46b5adc17da76c639ef69cca4af4a2**, before any documentation integration. The current handoff reports the **authorized local-first V1 implementation scope complete**. GitHub independently confirms [PR #57](https://github.com/Centaurioun/video-intelligence-pipeline/pull/57) merged the exact G02 product candidate **e956722a0fc2109eb4651ce728e919e691162511** as **e752c2fc45b533a0c679a32459225d37165a7722**. Terminal G02/G03 and 1,290 candidate-regression results are attributed to controller receipts; this design review did **not** rerun those suites or resolve inherited control-plane progress-counter differences.
- Existing binding migration authority: [ADR-0002](../../decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md), accepted sequence **V1 SigLIP Base -> V2 SigLIP2 Base -> V2 SigLIP2 SO400M -> frozen three-arm mini-benchmark -> model decision**. The original dormant preparation package is not execution authorization.
- Migration preparation to **refresh against finished V1**, not blindly trust: [entrypoint](../../migrations/siglip2-post-completion/00_README_AND_ENTRYPOINT.md), [post-completion refresh protocol](../../migrations/siglip2-post-completion/19_POST_COMPLETION_REFRESH_PROTOCOL.md), [readiness checklist](../../migrations/siglip2-post-completion/26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md), [profile design](../../migrations/siglip2-post-completion/10_TARGET_MODEL_PROFILE_DESIGN.md), [compatibility matrix](../../migrations/siglip2-post-completion/06_MODEL_COMPATIBILITY_MATRIX.md), [assumption register](../../migrations/siglip2-post-completion/08_HARDCODE_AND_ASSUMPTION_REGISTER.md), [benchmark charter](../../benchmarks/siglip-three-way/B00_BENCHMARK_CHARTER.md).
- Isolated experiment repository Centaurioun/vip-siglip2-so400m-browser-spike: its **main** was **22a6431083a79716249ed80bafaec62d2b703257** at inspection; the most recent Q4 native results are on **codex/so400m-q8-q4-preparation-20261009@32722b227e81a5595239d46d65b7a52a4504ae94**, **not** on its main at this point. Import experimental evidence by **immutable commits**, not a mutable repo main assumption.
- Pinned SO400M: google/siglip2-so400m-patch14-384; upstream revision **c65677ac77ca25276518923f7c58cbf5d81ea602**, checkpoint SHA-256 **9f4f4a49f908ef0c979bce8ff5a5c0e88882dc6c5dc4304387cbbd152558e2c2**; 384 image geometry, patch 14, normalized **1152-D float32 output**. Source/receipts on GitHub support Codex-reported real MPS synthetic image and text forwards for **FP16, FP32, and mixed Q4/FP16**. The GitHub source was independently inspected; this documentary review **did not rerun** the model on the user's Mac. **Q8 runtime NOT_VERIFIED.**
- Q4 evidence: [Q4 Metal report](https://github.com/Centaurioun/vip-siglip2-so400m-browser-spike/blob/32722b227e81a5595239d46d65b7a52a4504ae94/docs/native/Q4_METAL_VERIFICATION_REPORT_2026-10-09.md) and code-fix commit **48a2ffa7338676d50196a6d714c1fb428c24ac25**. Effective **Metal Q4/group-size 32**, **272/328** linear layers quantized, **56** intentionally FP16, computation FP16. Finite normalized embeddings do **not** prove correct text semantics; BOS/EOS tokenizer warning remains unresolved. Full successful runtime JSON/exit status and precise same-session memory readings are not retained in the report.
- V1 real retrieval is already proven *within bounded one-source trials*: [September 15 single-video spike](../../experiments/2026-09-15-single-video-semantic-retrieval-spike-findings.md) recorded **5 STRONG / 2 USEFUL / 0 MISS** after the correct max-length padding; [September 21 real semantic pilot](../../experiments/2026-09-21-local-semantic-real-pilot-report.md) recorded **7 STRONG / 0 MISS** and measured PTS/refinement attribution. Neither is full archive-scale or V2 evidence.
- Independent browser SigLIP2 Base reference lives in a **third, preserved repository**: [2026-10-08 browser baseline](https://github.com/Centaurioun/vip-siglip2-browser-spike/blob/9db72f8a16cb8b3bbb63ef7f0b2fe1e2c700476e/docs/experiments/2026-10-08-siglip2-base-browser-baseline/BASELINE_RESULTS.md). Browser Q4/Q8/FP32 candidate rankings are repeatable in two recorded sessions but human relevance, source-native PTS, independent GPU execution and exact ONNX artifact provenance are **NOT_VERIFIED**. Do not equate browser Base evidence with native SO400M or canonical VIP.

**Authority:** explicit current owner instruction > frozen ADR/architecture > approved architectural direction > this owner-approved written spec > proposed implementation plan. Preserve historical decisions. Current user permission for two-repository **documentation publication** supersedes the spike repo's historical “do not write VIP from this experiment” instruction **only for this documentary work**; it does not authorize code or model execution.

## 1. Purpose, boundaries, success criteria

**Goal:** evolve the **single** canonical VIP codebase into independently reproducible **V1 Base, V2 Base and V2 SO400M** representations, keeping all non-model source/media/editing functions and V1 rollback. Use local model evidence from spike as *inputs to* a new native V2 adapter, not as a second pipeline. Later compare models under the frozen ADR-0002 benchmark before selecting an archive-scale representation.

**Desired user outcome:** search meaningful ballet, dance and performing-arts moments using local models on Apple Silicon, attribute retrieved candidates to immutable sources and measured PTS, retain human editorial control and versioned edit/QC path, and determine whether V2 justifies its resources.

**Not authorized now:** implementation, creating a post-report preservation branch/tag, model downloads, package installs, network/provider inference, real or protected media access, re-indexing, Gate promotion, production rendering/export, destructive Git, force pushes or silent canonical main merges. No new architecture subsystem may be treated as approved simply because a source reference already exists.

**Invariants:** source bytes immutable; deterministic provenance; no VFR ordinal * nominal FPS frame inference; semantic/model timestamps candidate-only; measured source-native PTS/timebase for refinement; human editorial decisions explicit. Evidence classes MEASURED, MATCHED, VISUALLY_OBSERVED, AUDIO_OBSERVED, EDITORIAL_INFERENCE; NOT_OBSERVED is an availability/status marker.

## 2. Three architectural options and decision

| Option | Benefits | Costs/risks | Disposition |
|---|---|---|---|
| A. Clone VIP into permanent stand-alone V2 pipeline | Rapid first separation | Duplicate SQLite persistence, sample/PTS, source trust, FVS, decisions, render/QC; diverging code and rollback | **REJECTED**. Reconsider only if model runtime cannot be isolated behind existing contracts. |
| B. Copy whole native SO400M spike/CLI into VIP | Reuses successful MPS smoke quickly | Brings prototype-specific guards/caches/assumptions, ignores V2 Base step, 768-D write defects and product APIs | **REJECTED AS PRIMARY PATH**. May reuse selected, reviewed logic through a thin adapter. |
| C. One VIP with minimal closed ModelProfile + checked native runtime | One source/provenance/PTS/FVS, three isolated vector spaces, V1 remains usable; follows ADR-0002 | Requires targeted profile, processor and 768/1152 storage changes | **RECOMMENDED; OWNER APPROVED DIRECTION**. Not yet approved as final written spec. |

Do not create a universal model framework, model marketplace, automatic provider fallback, cross-model vector converter or duplicated vector database. YAGNI: support **exactly the three ADR-required model profiles** unless owner explicitly changes scope.

## 3. Proposed end-to-end design

    explicit source authorization + immutable source manifest
      -> existing inventory, source SHA and stream selection
      -> existing one-pass source-native measured-PTS sampling
      -> validated local ModelProfile -> checked image/text encoder
           V1 SigLIP Base:     224px, 768-D
           V2 SigLIP2 Base:    224px, expected 768-D, verify exact native checkpoint
           V2 SigLIP2 SO400M: 384px, 1152-D
      -> normalized float32 image rows -> profile-specific SQLite/index generation
      -> same-profile text encoder -> search/ranking -> MATCHED candidate
      -> unchanged source-native refinement (integer PTS/timebase)
      -> unchanged human decision -> versioned plan -> render/technical/editorial QC

**Data and authority do not flow backwards:** a model score cannot become a measured edit boundary, a model profile cannot authorize source reading, and a synthetic success cannot imply full-media QC.

### 3.1 Closed model-profile identity

Design a small **validated** profile descriptor, equivalent to:

- profile_id, model family and model_id; immutable upstream revision and checkpoint SHA-256;
- explicit required local artifact filenames/digests (including processor/tokenizer assets);
- processor identity, actual image preprocessing contract/digest, complete text normalization/lowercasing, pad direction/ID, truncation, max length, attention mask, pooling/special token contract;
- expected image size/patch geometry and embedding dimension;
- effective model weight/storage precision, compute precision, quantization coverage/backend and kernel identity where material;
- float32 vector output/element width, L2 normalization and exact semantic-space identity;
- runtime lock/version/OS/MPS and “no silent fallback” contract;
- closed known loader kind; no arbitrary module paths or remote model acquisition.

The existing VIP SemanticSpace remains the canonical compatibility authority. A profile maps deterministically into it; if existing fields cannot capture a meaningful precision/preprocessing distinction, extend only the necessary representation identity in a backward-safe reviewed change rather than inserting ad-hoc string hashes without migrations. Query and indexed image spaces must be identical; wrong profile/digest/dimension must refuse before reading vector bytes.

V1 and V2 Base both use 768 dimensions but are **different vector spaces**. SO400M outputs 1152; cannot reuse V1 vectors. **Changing FP16/FP32/Q4 weights/runtime may alter embedding coordinates**; freeze each effective representation separately unless matched numeric/ranking evidence supports a controlled equivalence decision. Never assume raw cosine scores are calibrated across different profiles.

### 3.2 Runtime integration seam

**Verified existing code surfaces, canonical VIP main@455ef690:**

- src/vip_fvs/local_semantic.py: CheckedLocalSemanticRuntime already takes image_embedder, text_embedder and SemanticSpace; refuses missing real runtime and fake fallback.
- src/vip_fvs/retrieval_adapter.py and semantic_index.py: pass explicit embedder callables into existing index and query operations.
- experiments/persistent_local_index/model_space.py: deterministic SemanticSpace/GenerationSpec and digests.
- experiments/persistent_local_index/local_model.py: fail-closed local asset identity/open boundary.
- experiments/persistent_local_index/embedding.py, src/vip_fvs/cli.py: existing V1-only model/session wiring.
- src/gate0/adapters/siglip_local.py: historical V1 CPU-specific SiglipModel/SiglipProcessor adapter; **do not silently replace its historical contract**.

**Proposed smallest change:** introduce a native SigLIP2 AutoModel/AutoProcessor session with a narrow model-profile selector, output shape checks and local-only/digest/device constraints; adapt the existing callable session/CLI seams to use one validated profile-to-SemanticSpace builder. Keep spike/native/diagnostic.py, precision_study.py, tokenization.py, device.py and its immutable receipts as *reference sources*; do not vendor its entire CLI/environment or the separate browser React/ONNX code into VIP.

**Dependencies:** candidate's exact lock and source SHA mandatory; isolate FP16/FP32 and Q4 Metal environments/processes if package ABI conflicts are verified. Q4 remains an independently versioned optional performance treatment and does not block the first V2 native path. No unapproved CPU fallback/cloud shortcut.

### 3.3 Critical 768-D write-side blocker

The prior migration assumption register is still matched by currently fetched files:

| Existing file | Current model-coupling issue | Proposed correction |
|---|---|---|
| experiments/persistent_local_index/model_space.py | global EMBEDDING_DIM = 768; V1 spiece.model asset list; partial text contract | profile-dependent dimension and per-checkpoint processor inventory |
| experiments/persistent_local_index/embedding.py | V1 session and width from global constant | validated profile-native SigLIP2 session; keep V1 behavior |
| src/vip_fvs/cli.py | real-runtime construction repeats V1 768/processor assumptions | single validated profile builder; preserve authorization-before-load |
| experiments/persistent_local_index/indexer.py | ROW_WIDTH_BYTES = 768 * 4 for writer/tail recovery | row width derived from generation's profile and float32 dtype |
| experiments/persistent_local_index/storage.py | DEFAULT_ROW_WIDTH_BYTES = 768 * 4 **and _validate_vectors rejects !=768** | validate against committed generation dimension in append/recovery |
| experiments/persistent_local_index/search.py | already derives query width from live_spec.space.embedding_dim | preserve and test; does not prove writer is fixed |

For float32, 768-D = **3072 bytes/row** and 1152-D = **4608 bytes/row**. Derive storage/recovery width once from the validated generation, propagate through SQLite committed bytes, vector file, append, restart and exact search. Preserve SQLite's mutable commit authority and one-writer lock. Reject mixed space/width and unsupported dtype **before writes/truncation**. Do not rewrite valid historical 768-D tests; add synthetic 1152-D and incompatible-space regression fixtures.

### 3.4 Tokenizer/pooling validity is a separate acceptance gate

The V1 one-video trial initially returned 7/7 MISS while embedding numerical checks still succeeded. The actual error was missing max_length text padding; a controlled fix restored expected correspondence. SO400M's current diagnostic uses padding=max_length, max_length=64, truncation=True, right padding, explicit attention_mask, but reported BOS/EOS IDs **49406/49407** exceed tokenizer vocabulary range **0..31999**. Model embedding vocabulary may differ; mere non-crash is insufficient.

Before the new V2 runtime can be trusted for meaningful retrieval: independently inspect exact checkpoint tokenizer, config and token IDs; verify pad/bos/eos semantics, special-token placement, attention-mask and **final-sequence-position pooling** against a supported/reference path; test identical-input stability and known paired image/text alignment; fail closed on semantic mismatch. Do **not** arbitrarily rewrite IDs, padding, pooling or scores based on intuition. Use Superpowers systematic-debugging for a confirmed discrepancy.

### 3.5 Precision and memory policy

SO400M FP16 and FP32 are synthetic-forward **reported PASS** on MPS; a Q4 Metal mixed-precision probe also reports PASS with 272/328 quantized linears and 56 FP16 exclusions, group_size=32, pinned kernels dependency. Q8 native real forward **NOT_VERIFIED**. None establishes general retrieval superiority or long-running/batched stability.

Choose one native reference precision **after** paired smoke/correctness and resource evidence in the separately approved implementation plan. Preserve a conservative memory/load guard and >=2-GiB post-load reserve in SO400M trials; record actual available memory, swap, kernel/backend and all effective precisions; no hidden MPS->CPU substitution. Store FP16, FP32 and mixed Q4 index/semantic-space versions distinctly pending validated parity.

## 4. Eight iterative design-refinement cycles

The eight cycles below are **sequential analytic refinement passes** during brainstorming, **not** eight independent agents, eight runtime tests or certified reviews. Each includes a genuine threat, a proposed countermeasure and a trigger to reopen the decision.

| Cycle | Threat / finding | Refinement incorporated | Reconsideration trigger |
|---|---|---|---|
| **1 — Authority and completed V1** | Oct-05 migration snapshots precede final V1 adoption; “V1 completed” could be overgeneralized | Bind to canonical post-completion Git SHA, G02/G03 verified scope and ADR; refresh historical templates against frozen final V1 | Canonical handoff/terminal authority contradicts code or refresh uncovers unaddressed product blockers |
| **2 — Integration ownership** | Forking pipeline or importing experimental runner duplicates product logic | Keep VIP as sole writer/product; checked image/text callable seam; spike stays an evidence source | Existing semantic runtime cannot represent required safety/processing without unacceptable churn |
| **3 — Model identity** | Same 768-D mislabeled compatible; incomplete processor asset lists | Closed profiles and model/revision/digests/text/quant precision in semantic-space identity | Final V1 already has an equivalent boundary, or exact acquired checkpoint invalidates proposed fields |
| **4 — Semantic correctness** | Finite embeddings with broken padding/BOS/EOS/pooling | Reference tokenizer comparison plus paired image/text correspondence before real retrieval | BOS/EOS issue is explained and bounded tests prove semantics, or failures need new design |
| **5 — Index storage** | Hard-coded 768-D writer and recovery violate 1152-D contract | Profile-derived float32 row widths, fail-closed SQLite/vector reconciliation, both dimensions tested | Code refresh proves write path already dimension-aware |
| **6 — Runtime and precision** | Incompatible Metal packages/quantized exclusions conflated with FP32 | Separate reproducible runtimes, explicit Q4 mixed identity, memory preflight, no silent fallback | Measured benchmark justifies different sharing/precision choices |
| **7 — Temporal/evidence integrity** | Semantic candidate timestamp silently promoted to frame cut | Preserve source-native integer PTS/timebase, source SHA, Gate3 binding and human decision | Future separately approved temporal spec deliberately changes boundary |
| **8 — Comparison/rollback** | Successful smoke prematurely declared winner; irreversible loss of V1 | Preserve V1 ref/index, require three-arm paired benchmark and separate winner/promotion; never mix embeddings | Valid frozen benchmark supports alternative representation/promotion |

**Rejected alternatives remain recorded** (permanent forked VIP, wholesale experiment import, automatic reuse of vectors, assuming V2 wins on public benchmarks, broad model plugin marketplace). No invented rationale is used to widen authorization.

## 5. Mandatory acceptance and refusal criteria

**V1 compatibility:** exact post-report baseline commit preserved later; V1 loader/index still reproducible; no unrelated source/gate/edit/QC changes; immutable source SHA and operator-visible rollback; 768-D V1 tests retained.

**Profiles / security:** hash-check exact local weights and processor assets both before and after load, enforce immutable revision, closed loader kind, no remote/fake fallback, MPS and dtype verified, all output vectors float32 finite/nonzero/L2 with expected width.

**Tokenizer:** complete SigLIP2 contract recorded and hashed, lowercasing/truncation/padding/mask/pooling checked, warning root cause explained or explicitly risk-gated, meaningful matched query/image alignment test (not norm alone).

**Index:** 768-D and 1152-D synthetic indexing, reopen, exact cosine search, row bytes, concurrent writer refusal, crash tail recovery, mismatch refusal and missing/malformed metadata handling. No cross-profile query/index reuse.

**FVS:** preserve source authorization, explicit source hash, selected stream, measured PTS/timebase through hits and refinement, authoritative separation MATCHED vs MEASURED and human editorial decision. No nominal FPS frame invention.

**Runtime:** exact code/model/runtime SHA/digests and dependency lock; preflight reserve, swap/resource evidence, MPS fallback env disabled; offline verified artifacts; sanitized receipt without user path/media/weights/frames/embeddings.

**Later benchmark:** mandatory three arms V1 Base / V2 Base / V2 SO400M under the frozen B16/B17 corpus and source-native sample-plan; identical queries and graded human judgments; Success@1/5/10, nDCG/false-positive burden, Turkish/English clusters, memory/wall cost; compare relevance outcomes, **not** raw cross-space cosine magnitudes. The historic seven V1 anchor queries may be a small diagnostic but **not** the sole unbiased winner metric.

## 6. Dependency-safe later sequence, not an executable plan

### Stage A — preserve EXACT post-report canonical V1 first

After both documentation files are actually published and independently read back on main:

1. Verify current final **VIP main HEAD**; do not reuse the pre-documentation SHA 455ef690.
2. **In a separately authorized next operation**, freeze a uniquely named, collision-checked, immutable branch/tag/candidate SHA of that **post-documentation V1 code-and-report tree**. Verify the remote ref, object reachability and rollback. Do not destroy/move existing refs or touch worktrees automatically.
3. Produce a baseline receipt with final commit, V1 model checkpoint/revision/digests, runtime/space identity, relevant existing tests and known control-plane limitations.

### Stage B — refresh, owner spec review, and writing-plans

4. Execute [post-completion refresh](../../migrations/siglip2-post-completion/19_POST_COMPLETION_REFRESH_PROTOCOL.md) against the actual frozen completion/working baseline. Recheck all 768 literals, processor inventories, loader paths, source authorization boundaries and tests. Emit the 30_post-completion-refresh receipt and complete readiness gates.
5. Owner reviews **this written spec** and requests revisions or approves it; current approval covers **the architectural direction**, not automatic implementation. After written-spec approval invoke **Superpowers writing-plans** and specify tasks, exclusive writer ownership, isolated worktrees, RED/GREEN TDD, review/verification, freeze/rollback.
6. The approved plan itself requires separate owner choice of execution method and permission for actual implementation; no automatic model download, real-media use or Gate progression.

### Stage C — future isolated implementation only after approval

7. V1-preserving synthetic tests and dynamic index width; integrate closed profile and native session seam.
8. V2 SigLIP2 Base native runtime first, matching ADR-0002 and validating exact acquired checkpoint rather than using browser ONNX evidence as substitution.
9. V2 SO400M native profile second using pinned spike source/checkpoint evidence and one selected reference precision; optional Q4 optimization as distinct profile, Q8 still unproven.
10. Controlled, explicitly authorized small real-source retrieval and later **frozen three-way benchmark**. Only after user decision may any broader indexing/Gate/promotion be considered.

### Scope and state markers

The architecture direction is **APPROVED**. This written specification awaits owner review; code changes and implementation tests were **NOT_PERFORMED** in this publication. The spike's Mac execution outcomes remain **reported evidence** bounded by immutable experiment receipts. Real V2 retrieval, Q8 native inference, V2 production readiness, archive-wide generalization, winner selection and Gate promotion remain **NOT_VERIFIED / NOT_AUTHORIZED** as applicable.

## 7. Documentation handoff

Canonical document: this file in VIP main when merged. Companion technical transfer note: [SO400M spike repository](https://github.com/Centaurioun/vip-siglip2-so400m-browser-spike) under docs/native/VIP_V2_INTEGRATION_EVIDENCE_HANDOFF_2026-10-09.md on its main when published. Both repository HEADs must be independently read back before recording “published in both mains.”

The future preservation operation must capture the **final** VIP main SHA after the documentation PR/commit(s). The current documentation branch, an intermediate commit, and old PR #57 SHA must not be mislabeled as the requested post-report copy.