# 32 — Provisional SigLIP2 Tokenizer, Processor and Pooling Contract (Base and SO400M)

Information state: **`INFERRED_DESIGN`** · **`PROVISIONAL`** · **`NON_EXECUTABLE`** · **`NOT_AUTHORIZED_FOR_EXECUTION`**
Snapshot base: `main@7b72e2b35716d4877d937c1eaff57cc160bc9c15` (2026-10-25)
Governing owner document: `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`
Parent plan: `docs/superpowers/plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md`
Run record: `docs/agent-runs/2026-10-25-g1-2-3-provisional-tokenizer-contract/`
WBS item: `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md:152` (G1.2.3, second bullet)

---

## 0. Non-authority banner (read before any other section)

This document **does not** establish an authentic SigLIP2 tokenizer, processor, image-preprocessing or pooling contract. It contains **no** verified tokenizer identity, vocabulary size, special-token ID, padding semantic, attention-mask semantic, pooling reduction or projection behavior for either V2 arm. Every such field below is `NOT_OBSERVED`, `NOT_RECORDED`, `HISTORICAL_ASSERTION`, or `CANDIDATE_ASSUMPTION`.

It grants no execution authority. It does not:

- authorize model acquisition, download, load, inference, device execution, provider calls, or protected-media access;
- authorize authentic adapter, CLI, or runtime source implementation (WBS G1.2.3 first bullet, G1.2.4, G1.3.x);
- clear, weaken, satisfy, waive, or re-scope Gate B `NO_GO_BLOCKED`;
- clear `03_V1_BASELINE_SNAPSHOT.md:154` or any Task 0 predicate;
- adopt the native Task-4/5 source-only exception (`PROPOSED_NOT_ADOPTED`) or any part of Amendment 1 / Amendment 3;
- flip any WBS checkbox;
- substitute for the authentic evidence listed in §10.

Its single purpose is to make the *unresolved* state non-ambiguous: which questions are open, what each field would mean if resolved either way, which records currently contradict each other, what a future authentic implementation must prove before it may open a session, and exactly what evidence would close each item. Per `docs/agent-runs/2026-10-25-g1-1-4-draft-193-independent-disposition/DECISION_MATRIX.md` (D-2) this is the "`READY` only as a clearly provisional, non-executable statement" alternative; it "resolves the phrasing only; does not assert authenticity".

Two competent implementers reading this document must reach the *same* implementation prohibition and the *same* set of required authentic evidence. If they reach different conclusions about what is already known, this document has failed.

---

## 1. Scope, and how this document relates to V1 versus V2

### 1.1 The three profiles

| Role | Profile id | Upstream model id | Repository authority |
|---|---|---|---|
| V1 SigLIP (frozen, measured) | `vip-v1-siglip-base-224` | `google/siglip-base-patch16-224` | `experiments/persistent_local_index/model_profile.py:16-26,38-42`; `docs/migrations/siglip2-post-completion/03_V1_BASELINE_SNAPSHOT.md` |
| V2 SigLIP2 Base (design only) | `vip-v2-siglip2-base-224` | `google/siglip2-base-patch16-224` | `model_profile.py:16-26` (placeholders); `ADR-0002:21-28` |
| V2 SigLIP2 SO400M (design only) | `vip-v2-siglip2-so400m-384` | `google/siglip2-so400m-patch14-384` | `model_profile.py:16-26`; `plan:26` pin `c65677ac77ca25276518923f7c58cbf5d81ea602` |

### 1.2 V1 is a *different* SigLIP, and its contract does not transfer

`ADR-0002:136-144` states that "the SigLIP1 and SigLIP2 embedding spaces are still incompatible semantic spaces" even though both Base arms are 768-D, and forbids reusing V1 embeddings. Consequently:

- V1 measured facts (`padding=max_length`, `pooler_output` extraction, 768-D float32/L2, processor digest `4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980`) are **V1 facts only**. `10_TARGET_MODEL_PROFILE_DESIGN.md:95-99` explicitly warns not to assume the V1 processor-asset tuple is correct for SigLIP2.
- V1's tokenizer asset filename is `spiece.model`; the V2 evidence pack names `tokenizer.model` (`20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md:69`, `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md:53-63`). The relationship between those two filenames — same family, different serialization, or different tokenizer families — is **nowhere stated** in the repository. This is unresolved question U-1 (§6.1).
- V1's vocabulary size, BOS/EOS/pad IDs, tokenizer class, padding side and effective maximum length are **entirely unrecorded** (§4, V1 column). Therefore the historical `0..31999` warning cannot be evaluated against V1 at all.
- The `padding=max_length` shorthand is not a complete preprocessing identity (`20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md:54`); `05_model-contracts.yaml:32-35` itself records `lower_case`, `max_length`, `truncation` as `"NOT_RECORDED_IN_CURRENT_VIP_CONTRACT"` for V1.

### 1.3 What the repository currently implements

Verified in `docs/agent-runs/2026-10-25-g1-2-3-provisional-tokenizer-contract/lanes/lane-c-code-surface.md`:

- **No repository-owned tokenizer code exists.** Zero non-doc Python occurrences of `AutoTokenizer`, `SiglipTokenizer`, `tokenize(`, `convert_tokens_to_ids`, `vocab_size`, `bos_token`, `eos_token`, `pad_token`, `AutoProcessor`, and **zero** occurrences of `attention_mask`. No `max_length=<int>` and no `truncation=` anywhere. There is likewise no special-token *semantics* code: the only `special_tokens` substring hits in non-doc Python are the filename `special_tokens_map.json` (`model_space.py:45`, `tests/test_model_space.py:130`, `tests/conftest.py:140`, `tests/test_local_model.py:25`), never a tokenizer API or field. Tokenization is delegated wholly to the external `transformers.SiglipProcessor`.
- **No SigLIP2 processor or pooling path exists.** `experiments/persistent_local_index/siglip2_native.py:200-203` refuses with `SIGLIP2_AUTHENTIC_RUNTIME_UNAVAILABLE:source_only_loader_required` when no loader is injected, and `:223-226` refuses `SIGLIP2_AUTHENTIC_HANDOFF_REQUIRES_NATIVE_ACCEPTANCE`. `_InjectedSiglip2Session.authentic` is hardcoded `False` (`:137-139`).
- **No tokenizer field exists on any profile.** `model_profile.py:45-66` defines 18 fields; none is a tokenizer class/id, vocabulary size, maximum length, special-token id, tokenizer-config digest, pooling reduction, or attention-mask rule. V2 text contracts are synthetic identity labels (`model_profile.py:5-7`, `:38-42`), not tokenizer specifications.
- **The only tokenizer artefacts in the code are digest-input filenames.** `model_space.py:40-47` lists `config.json`, `preprocessor_config.json`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `spiece.model`; they are hashed, never parsed.
- **A V1 processor-invocation and `pooler_output` path exists** (`src/gate0/adapters/siglip_local.py:61-66,81-103,115,117,123,125`; `experiments/persistent_local_index/embedding.py:112-119,239-261`) but its runtime is `NOT_OBSERVED` here; tests exercise in-memory doubles (`tests/gate0` asserts `"transformers"` is absent from `sys.modules`).

Therefore the entire V2 tokenizer/processor/pooling contract is currently **design intent plus inert requirement strings**, not implementation.

---

### 1.4 Existing architecture versus the candidate V2 path (side by side)

| Stage | V1 (existing, measured/source) | V2 Base candidate | V2 SO400M candidate |
|---|---|---|---|
| Loader | `SiglipModel.from_pretrained(..., local_files_only=True, trust_remote_code=False, use_safetensors=True)` (`siglip_local.py:61-63`) | `AutoModel` `OFFICIAL_EXTERNAL` (`04:30`, `05:80-81`) — applicability explicitly unknown (`04:170`) | same as Base, no SO400M receipt |
| Processor | `SiglipProcessor.from_pretrained(local_files_only=True, trust_remote_code=False)` (`siglip_local.py:64-66`) | `AutoProcessor` `OFFICIAL_EXTERNAL` | same as Base |
| Text call | `self.processor(text=value, padding="max_length", return_tensors="pt")` (`siglip_local.py:115`) | `NOT_OBSERVED` | `NOT_OBSERVED` |
| Image call | `self.processor(images=image, return_tensors="pt")` (`siglip_local.py:123`) | `NOT_OBSERVED` | `NOT_OBSERVED` |
| Features | `get_text_features` / `get_image_features` (`siglip_local.py:117,125`) | `NOT_OBSERVED` | `NOT_OBSERVED` |
| Pooling | `getattr(output, "pooler_output", None)` with six explicit refusals (`siglip_local.py:81-103`) | `NOT_OBSERVED`; reduction and position unresolved | same |
| Normalization | L2 in `embedding.py:139-149`; contract `float32`/`l2` (`model_space.py:34-36`) | `INTENDED` (`05:65-72`) | same |
| Width | 768 (`model_space.py:34`) | 768 expected (`10:119-123`) | 1152 `OFFICIAL_EXTERNAL` (`04:118-129`) |
| Identity binding | `SemanticSpace` + `assert_same_space` (`model_space.py:52-64,209-217`) | fields are placeholders (`model_profile.py`); not computable | same |

Reading: **every V2 row is unobserved except external configuration values.** The V1 column is the only path this repository has ever executed, and §1.2 explains why it cannot be extended by analogy.

---

## 2. Evidence discipline used in this document

### 2.1 Provenance classes

The repository's five approved evidence classes are `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, `EDITORIAL_INFERENCE` (`AGENTS.md`, workspace guidance item 6). The migration pack adds document-state labels (`00_README_AND_ENTRYPOINT.md:46-64`: `FROZEN_DECISION`, `VERIFIED_CURRENT`, `SNAPSHOT`, `REVERIFY_AT_V1_COMPLETION`, `OFFICIAL_EXTERNAL`, `INFERRED_DESIGN`, `TEMPLATE`, `NOT_AUTHORIZED_FOR_EXECUTION`).

This document additionally uses four **row-level provisional labels**, which are not evidence classes and must never be promoted into one:

| Label | Meaning |
|---|---|
| `VERIFIED_SOURCE_FACT` | The *behavior of repository source or tests at the snapshot base*, demonstrated by reading code/tests and, where stated, running the repository's own suites. This is a statement about code, never about model assets. |
| `MATCHED_RECORD` | Two or more in-repository records agree on a value. Agreement between records is not measurement. |
| `HISTORICAL_ASSERTION` | A prose claim in a design/runbook/agent-run record, whose underlying session, validator, log, or asset is not in this repository and is not reproducible here. |
| `CANDIDATE_ASSUMPTION` | A value this document or an upstream planning record *proposes* for a future implementation, with no evidence at all. |

`NOT_OBSERVED` is used only as an availability state (`AGENTS.md` item 6), never as a class. `NOT_RECORDED` means no repository record states the field at all.

### 2.2 Source hierarchy applied

Per `20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md:171-182`, the operational order is: (1) user authorization, (2) governing repository specs/ADRs, (3) frozen local checkpoint bytes/config/runtime, (4) official upstream documentation, (5) paper results, (6) third-party. `21_source-receipts.yaml:201-202` additionally fixes `public_main_is_runtime_identity: false` and `external_claim_is_local_measured_evidence: false`.

Consequences enforced in every row below:

1. An `OFFICIAL_EXTERNAL` value (a mutable upstream `main` config page) is **never** upgraded to a project identity or a runtime fact (`20:73`, `20:200`, `21:79`).
2. No public model page, model card, or library documentation is accepted here as evidence that *any* local or future frozen bundle's tokenizer/processor matches.
3. The `256000` figure is `OFFICIAL_EXTERNAL` only. The refreshed mutable targets are Base `75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2` and SO400M `e8e487298228002f3d8a82e0cd5c8ea9c567f57f`, which is **not** the SO400M planning pin `c65677ac…` (`plan:26`, `12_V2_BASE_TO_SO400M_RUNBOOK.md:15`).

---

## 3. Field-by-field evidence matrix

**Citation key (applies to §3, §9 and §10).** `NN:line` means `docs/migrations/siglip2-post-completion/NN_*.md` or `NN_*.yaml` (`03`,`04`,`05`,`06`,`08`,`10`,`11`,`12`,`13`,`14`,`18`,`20`,`21`,`26`). `plan:` = `docs/superpowers/plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md`; `design spec:` = `docs/superpowers/specs/2026-10-09-vip-v2-siglip2-integration-design.md`; `ADR-0002:` = `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`; `WBS:` = `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md`; bare filenames such as `model_space.py`/`model_profile.py`/`embedding.py` are under `experiments/persistent_local_index/`; `siglip_local.py` is `src/gate0/adapters/siglip_local.py`.

Columns: **V1** (measured/frozen profile), **V2 Base**, **V2 SO400M**, then **Required authentic evidence** for the V2 arms. A single cell may carry more than one label. All V2 cells are, without exception, non-evidence for authenticity.

### 3.1 Tokenizer identity and vocabulary

| Field | V1 | V2 Base | V2 SO400M | Required authentic evidence |
|---|---|---|---|---|
| Tokenizer family / implementation class | `NOT_RECORDED` (V1 adapter imports `SiglipProcessor`, `src/gate0/adapters/siglip_local.py:58`) | `NOT_RECORDED` — never named in any record | `NOT_RECORDED` — no SO400M asset inventory exists | The tokenizer object's concrete class name + module + version emitted by the future authenticated load of the frozen bundle |
| Tokenizer asset filenames | `spiece.model` present (`03_V1_BASELINE_SNAPSHOT.md:58-59`); full V1 enumeration incomplete/unrecorded — the digest tuple also names `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json` (`model_space.py:40-47`) | `tokenizer.model` named in the asset list (`13:53-63`); relationship to `spiece.model` unstated | same as Base, copied, no SO400M receipt | Directory listing + per-asset digest of the frozen bundle, plus statement of which file the loader actually consumes |
| Serialized vocabulary size in `config.json` | `NOT_RECORDED` | `256000` **`OFFICIAL_EXTERNAL`** only, and **`MATCHED_RECORD`** across six independent records (agreement only) (`04_MODEL_CONTRACTS.md:123`, `05_model-contracts.yaml:121`, `20:83`, `21:63`) | `256000` **`OFFICIAL_EXTERNAL`** only (`20:116`, `21:95`) | `text_config.vocab_size` (or equivalent) read from the *frozen* `config.json`, with file digest |
| Tokenizer object's own vocabulary length | `NOT_RECORDED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `len(tokenizer)` and/or length of the tokenizer model file's vocabulary, from the frozen bundle |
| Documented library class default | n/a | `32000` **`OFFICIAL_EXTERNAL`** (`20:202`; `Siglip2TextConfig` default) | same | must not be used as a value; recorded only to explain the third number |
| Embedding-table row count | `NOT_RECORDED` | `NOT_OBSERVED` | `NOT_OBSERVED` (`12:17`: "text embedding-table size remain unobserved") | Row count of the text embedding matrix in the loaded weights |
| Consistency of declared vocabulary vs tokenizer vocabulary | `NOT_RECORDED` | `NOT_OBSERVED` | `NOT_OBSERVED` — this is the core open question (§5) | One measured triple: declared config vocab, tokenizer object vocab, embedding rows — all from one bundle |
| Recorded anomaly | see §5 — the `0..31999` warning is attributed to V1 in one record and SO400M in another | inherited anomaly, unowned | inherited anomaly, unowned | the raw warning text, its validator, its emitting object, and its session identity (`NOT_OBSERVED`; no log exists in this repository) |

### 3.2 Special tokens and padding semantics

| Field | V1 | V2 Base | V2 SO400M | Required authentic evidence |
|---|---|---|---|---|
| BOS token id | `NOT_RECORDED` | `NOT_RECORDED`; 49406 is a **`HISTORICAL_ASSERTION`** from the external SO400M diagnostic, not a contract value | same; 49406 asserted in the diagnostic prose | `tokenizer.bos_token_id` + the mapping entry that defines it, plus confirmation it is `<` the embedding row count |
| EOS token id | `NOT_RECORDED` | 49407 **`HISTORICAL_ASSERTION`**, unowned | same | as above |
| `pad_token_id` | `NOT_RECORDED` | `NOT_RECORDED` — zero hits for `pad_token_id` across the migration pack, design spec and plan | `NOT_RECORDED` | `tokenizer.pad_token_id` + explicit statement whether it is a distinct id or aliases another special token |
| `unk_token_id` / added tokens | `NOT_RECORDED` | `NOT_RECORDED` | `NOT_RECORDED` | `tokenizer.get_added_vocab()` + serialized `special_tokens_map.json` / `tokenizer_config.json`, with digests |
| Padding side / direction | `NOT_RECORDED`; the applied call passes only `padding="max_length"` (`siglip_local.py:115`, `embedding.py:32`) and no side is recorded | `NOT_RECORDED` as a contract field; the only recorded mention of "right padding" is the external SO400M diagnostic (`design spec:112`) | same, plus `12:90` claims SO400M preprocessing "differs appropriately from V2 Base" without ever saying how | `tokenizer.padding_side` and observed placement of pad ids in a measured batch |
| Padding strategy | `padding=max_length` (`03:20`, `05:32`; abbreviated contract) | `padding="max_length"` `OFFICIAL_EXTERNAL` (`05:73-78`) | copied from Base, no SO400M receipt | observed call arguments + emitted tensor shape `(batch, max_length)` |
| Effective `max_length` | `NOT_RECORDED_IN_CURRENT_VIP_CONTRACT` (`05:32-35`) | `64` `OFFICIAL_EXTERNAL`; `21:167` states the documentation default is "not checkpoint-specific" | copied from Base, no SO400M receipt | `tokenizer.model_max_length` and, decisively, the value the serialized `tokenizer_config.json` carries in the frozen bundle |
| Truncation | `NOT_RECORDED_IN_CURRENT_VIP_CONTRACT` (`05:32-35`) | `True`, `OFFICIAL_EXTERNAL` (`05:73-78`) | copied from Base (`05:128-133`), no SO400M receipt | observed `truncation=` argument + behavior on an over-length input |
| Lowercasing | `NOT_RECORDED_IN_CURRENT_VIP_CONTRACT` (`05:32-35`) | `True`, `OFFICIAL_EXTERNAL` (`05:73-78`) | copied from Base (`05:128-133`), no SO400M receipt | observed `do_lower_case` in the frozen processor/tokenizer config |
| Attention-mask construction | `NOT_RECORDED`; the production code never constructs or inspects a mask | `NOT_RECORDED` — `attention_mask` appears zero times in non-doc Python | `NOT_RECORDED` | observed mask tensor: shape, dtype, positions of `1`/`0`, relation to padding side |
| Caller vs processor ownership of pad/truncate | `NOT_RECORDED` — both the adapter call (`padding="max_length"`) and library defaults are in play | `NOT_RECORDED` | `NOT_RECORDED` | a recorded processor invocation and its resolved effective arguments |

### 3.3 Pooling, normalization and projection

| Field | V1 | V2 Base | V2 SO400M | Required authentic evidence |
|---|---|---|---|---|
| Pooling reduction | `VERIFIED_SOURCE_FACT` (source only): `pooler_output` is read from the model output (`siglip_local.py:81`). How that vector is reduced is library-internal and **not recorded** here; no reduction rule (mean, non-mean, masked, positional) is claimed | `NOT_OBSERVED`. `design spec:114` requires verifying "**final-sequence-position pooling**" — a verification *target*, not a recorded fact | `NOT_OBSERVED` | the actual reduction: which token position or which masked reduction produces the pooled vector — stated by the upstream model class, and confirmed numerically only under the separate authorization described in §10.2 item 4 |
| Pooling position selection under padding | `NOT_RECORDED`; V1 code relies on the library pooler | `NOT_OBSERVED`; resolver undefined | `NOT_OBSERVED`; resolver undefined | explicit rule for selecting the pooled position when `padding=max_length` + right padding is in force (see §7 hazard) |
| Mean pooling / attention-mask mean | `ABSENT` in repository source for **token** pooling | `ABSENT` | `ABSENT` | only if a measured contract proves it; do not introduce by inference |

> **Naming-collision caveat.** `src/gate0/arms/semantic.py:26,127` uses `pooling` with the value `"MEAN_TARGET_SLOTS"` (enum pinned in `schemas/gate0/run_manifest.json:865-867`). That is **temporal** pooling of target-tick frame embeddings, not text-token pooling. It is not tokenizer evidence and must never be cited as such.
| Output normalization | `VERIFIED_SOURCE_FACT`: L2 normalization applied in `embedding.py:139-149`; contract `float32` + `l2` (`model_profile.py`, `model_space.py:34-36`) | `CANDIDATE_ASSUMPTION`: `05:65-72` records `normalization: "INTENDED_L2_REQUIRES_MIGRATION_DESIGN_CONFIRMATION"` | same as Base | whether normalization is inside the model head, applied post-hoc, or both — plus L2 rule confirmed on outputs |
| Text projection size | `NOT_RECORDED` for V1 in this pack | `NOT_RECORDED`; `04:90` notes the public checkpoint `config.json` omits inherited geometry | `1152` recorded in SO400M `config.json` as `text_projection_size` / `text_hidden_size` (`04:116-129`, `05:112-127`), **`OFFICIAL_EXTERNAL`** | `text_projection_size` read from the frozen `config.json`; cross-checked against the produced output width |
| Text model class | `SiglipModel` / `SiglipProcessor` (`05:37-40`) | `AutoModel` / `AutoProcessor` (`04:30`, `05:80-81`); `04:163-174` explicitly lists "proof that the current `SiglipModel`/`SiglipProcessor` loader is the correct future SigLIP2 loader" as unknown | same as Base | the class actually resolved by the frozen bundle's own config, plus its version |
| Output dtype | `VERIFIED_SOURCE_FACT`: `float32` contract (`model_space.py:35`) | `CANDIDATE_ASSUMPTION`: three candidate precision policies exist (`model_profile.py:32-37`); none is applied | same | precision policy actually applied and observed output dtype |

### 3.4 Processor / image preprocessing

| Field | V1 | V2 Base | V2 SO400M | Required authentic evidence |
|---|---|---|---|---|
| Processor class | `SiglipProcessor` (source) | `AutoProcessor` `OFFICIAL_EXTERNAL` | same, copied | resolved class from frozen bundle |
| Input resolution | 224 (`model_profile.py:16-26`; `03`) | `224` — `05:65-72` marks it `OFFICIAL_DOC_DEFAULT_PLUS_OFFICIAL_EXPORT_CONFIG_CROSSCHECK_REVERIFY_FROZEN_CHECKPOINT` | `384` (`04:116-129`), `OFFICIAL_EXTERNAL` | `preprocessor_config.json` `size`/`crop_size` from the frozen bundle |
| Patch size | 16 | `16` (expected; `10:119-123` "verify frozen checkpoint") | `14`, `OFFICIAL_EXTERNAL` | vision `config.json` patch size from frozen bundle |
| Rescale / mean / std | `NOT_RECORDED` here | mean/std `[0.5,0.5,0.5]`, rescale `1/255` `OFFICIAL_EXTERNAL` (`04:75-79`, `21:127-130,195`) | **`NOT_RECORDED`** — no SO400M mean/std/rescale record exists | `preprocessor_config.json` values with digest |
| Resize interpolation / antialias / center crop | `NOT_RECORDED` | `NOT_RECORDED` | `NOT_RECORDED` | the processor's own resolved image-transform pipeline |
| Preprocessing identity digest | `d11ccb80f15d358a11bdb070e92e2d889005874b7db15823d5f10d9b2533b14a` (`11:15`) | `NOT_OBSERVED` | `NOT_OBSERVED` | digest of the preprocessing-relevant config actually consumed |
| Definition of the digest itself | `VERIFIED_SOURCE_FACT`: `digest_image_preprocessing_assets` (`model_space.py:126-131`) | `05:140-149` lists `image_preprocessing_digest` among `unresolved_until_authorized_acquisition` | same | an owner-accepted definition before any profile is populated |

### 3.5 Identity, digests, library versions

| Field | V1 | V2 Base | V2 SO400M | Required authentic evidence |
|---|---|---|---|---|
| Frozen revision | `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed` (`03:152`, `11:15`) | `NOT_OBSERVED`; `model_profile.py` holds the placeholder `"1"*40` | design pin `c65677ac77ca25276518923f7c58cbf5d81ea602` (`plan:26`, `12:15`) — planning pin, not an adopted identity | the revision actually staged, recorded immutably |
| Weights SHA-256 | `2c63cb7d…` (`03:152`) | `NOT_OBSERVED`; placeholder `"c"*64` | checkpoint SHA-256 `9f4f4a49f908ef0c979bce8ff5a5c0e88882dc6c5dc4304387cbbd152558e2c2` (`plan:26`) — planning pin | recomputed digest of the staged artefact |
| Processor/tokenizer digests | `4806b21b…` (`03:16`) | `NOT_OBSERVED` | `NOT_OBSERVED` | per-asset digests of the frozen bundle |
| Processor library version | `NOT_RECORDED` | `NOT_RECORDED`. `transformers_version: 4.49.0.dev0` (`20:85`, `21:175`) is **checkpoint metadata**, not the VIP runtime version | same | the version actually imported at runtime, recorded with the session |
| Semantic-space identity | `3840a0f4…` | not computable (identity fields placeholder) | not computable | the full binding: model identity, revision, weights digest, processor digest, image-preprocessing digest, text-processing contract, dimension, dtype, normalization (`10:158-170`) |

### 3.6 Matrix verdict

- V2 Base: **0** fields `VERIFIED_SOURCE_FACT` or `MEASURED`; all values are `OFFICIAL_EXTERNAL`, `HISTORICAL_ASSERTION`, or `NOT_RECORDED`/`NOT_OBSERVED`.
- V2 SO400M: same, plus SO400M-specific cells that were **copied from Base with no SO400M receipt** (text preprocessing, mean/std/rescale, tokenizer assets, pooling).
- V1: source facts and measured identity exist, but V1's tokenizer vocabulary and special tokens are `NOT_RECORDED`, so V1 cannot adjudicate the historical warning either.

---

## 4. The recorded `0..31999` tokenizer warning versus the `256000` vocabulary evidence

### 4.1 What is actually recorded

The **only** in-repository source of `0..31999` is a single prose sentence:

`docs/superpowers/specs/2026-10-09-vip-v2-siglip2-integration-design.md:112` (section heading `:110`, "3.4 Tokenizer/pooling validity is a separate acceptance gate"):

> "SO400M's current diagnostic uses padding=max_length, max_length=64, truncation=True, right padding, explicit attention_mask, but reported BOS/EOS IDs **49406/49407** exceed tokenizer vocabulary range **0..31999**. Model embedding vocabulary may differ; mere non-crash is insufficient."

That sentence was introduced unchanged by commit `e67a6ede9` (2026-10-09) and no earlier record exists (`git log --reverse -S "49406"`). It summarises an **external** spike diagnostic: the reference code is pinned at `plan:120` (`.../vip-siglip2-so400m-browser-spike/blob/32722b227e81a5595239d46d65b7a52a4504ae94/native/diagnostic.py`, `native/tokenization.py`) and a companion handoff is named at `design spec:184` (`docs/native/VIP_V2_INTEGRATION_EVIDENCE_HANDOFF_2026-10-09.md`). **Neither the handoff nor any diagnostic log, validator source, emitting object or session record exists in this repository.** The record therefore contains no warning string, no validator name, no tokenizer class, no reported vocabulary size, and no embedding shape.

All other occurrences of `0..31999` / 49406 / 49407 in the repository (15 records, enumerated in `lane-d-tokenizer-forensics.md` §1) are restatements of that sentence. None adds an observation.

The `256000` figure is a second, independent record class: an `OFFICIAL_EXTERNAL` value read from mutable upstream `main` config pages for V2 Base (`20:83`, `21:63`) and V2 SO400M (`20:116`, `21:95`, `04:123`, `05:121`). `20:202` states plainly that these are "not local MEASURED evidence", that "Neither source establishes V1 tokenizer behavior or explains the recorded V1 warning", and it records a **third** number: a `32000` `Siglip2TextConfig` documentation default.

### 4.2 Arithmetic

For a vocabulary of size `N`, valid ids are `0..N-1`.

| Declared range | Size | 49406 | 49407 |
|---|---|---|---|
| `0..31999` | 32000 | out of range by 17407 | out of range by 17408 |
| `0..255999` | 256000 | in range (margin 206593) | in range (margin 206592) |
| `0..31999` (class default 32000) | 32000 | out of range | out of range |

**Narrow verdict (asserted):** the two numbers cannot both describe the vocabulary of the same tokenizer object, checked by the same validator, at the same moment. At least one of the following holds — the range check did not measure the emitting tokenizer; the ids did not come from the checked tokenizer; the declared range came from a different field or source; the diagnostic was recorded against a different asset set. **No cause is asserted.**

**Secondary observation (asserted):** a warning rather than a bounds failure implies that either the text embedding table had more rows than the declared range, or the ids never reached an embedding lookup, or the check was a pure config/string comparison.

**Consequence (asserted):** under `0..31999` the pairing `49406/49407` is anomalous and cannot be a BOS/EOS contract; under `256000` the same ids are ordinary in-range indices. Both readings remain open. Neither is a contract.

### 4.3 Warning status as recorded — four incompatible statements

| Record | Statement |
|---|---|
| `docs/agent-runs/run-20261011-vip-v2-task0-plan-owner-review/step10-step12-assessment.md:18` | "explained as a configuration-field mismatch warning from the recorded loading session" |
| `docs/agent-runs/run-20261011-vip-v2-task0-plan-owner-review/owner-review-packet.md:34` | cause "understood" |
| `21_source-receipts.yaml:200-204` | `v1_token_warning_explained: false` |
| `12_V2_BASE_TO_SO400M_RUNBOOK.md:17` | "The shared BOS/EOS warning does not establish a shared cause" |

This document does not pick a winner. Both the "explained" and "unexplained" readings are recorded; the authoritative operational position that survives is `12:17`: preserve the fail-closed semantic-validation gate, and do not rewrite token ids by inference.

### 4.4 Profile attribution is itself contradictory

- `design spec:112` attributes the diagnostic to **SO400M**.
- `20:202` calls it "the recorded **V1** warning".
- `step10:18` calls it "the recorded loading session" with no profile.
- `11_V1_TO_V2_BASE_RUNBOOK.md:17` restates it in a V1→Base runbook.

No record attributes `256000` to V1. No record attributes `0..31999` to V2 Base. The warning's owning arm is therefore **unresolved**, which means it can neither block nor clear either V2 arm on its own.

### 4.5 Candidate hypotheses (labelled, unranked as findings)

Recorded in `lane-d-tokenizer-forensics.md` §5; reproduced here as **candidates only**. None is a finding, and no hypothesis may be cited as the cause.

| Id | Hypothesis | Distinguishing evidence |
|---|---|---|
| H1 | Declared config/default vocabulary ≠ tokenizer-object vocabulary | frozen bundle `config.json` `text_config.vocab_size` vs `len(tokenizer)` |
| H2 | Special-token ids injected or overridden by `tokenizer_config.json` / `special_tokens_map.json` | serialized special-token maps + `added_tokens` |
| H3 | Wrong tokenizer class or family was loaded | concrete tokenizer class name + which asset file it consumed; strongest repo-visible motive is `tokenizer.model` vs V1 `spiece.model` (`20:69`) |
| H4 | Embedding table resized relative to the tokenizer | embedding row count vs tokenizer vocab length |
| H5 | `pad_token_id` or another special id ≥ declared vocabulary | `pad_token_id`, `bos_token_id`, `eos_token_id` values |
| H6 | Stale or mixed asset directory | per-asset digests vs the intended revision |
| H7 | `max_length`/padding misuse caused the reported symptom | mechanically weak: truncation length is not an id-validity question |

H1 and H2 are most consistent with the recorded phrasing; this is a plausibility remark, not evidence, and must not be promoted.

---

## 5. Explicitly unresolved questions

The six required questions, answered as "unresolved, here is what would close it".

### 5.1 U-1 — Upstream tokenizer family and revision per profile

- **Base:** tokenizer family is never named anywhere in the repository. The V2 asset list names both `tokenizer.model` and `tokenizer.json` (`13:53-63`); which one the loader consumes, and whether either is the SigLIP2-native tokenizer, is unstated.
- **SO400M:** no SO400M asset inventory exists at all. Every SO400M preprocessing cell is Base-copied.
- **V1:** the V1 digest tuple (`model_space.py:40-47`) names six files — `config.json`, `preprocessor_config.json`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `spiece.model` — so `spiece.model` is *present*, not sole. Which of them the V1 tokenizer actually consumes, and the V1 tokenizer class, are not recorded as contract fields. V1 enumeration is therefore **incomplete/unrecorded**, not a single-asset fact.
- **Revision:** Base has no adopted revision; SO400M has a planning pin (`c65677ac…`) that is not an adopted identity.
- **Closes on:** §10 metadata items M-1, M-2, M-3.

### 5.2 U-2 — Actual BOS/EOS token ids

Unrecorded for all three profiles. 49406/49407 exist only as `HISTORICAL_ASSERTION` prose whose emitting object is unknown. The repository has zero `bos_token_id`/`eos_token_id` occurrences in code, tests, fixtures, migration pack, design spec or plan.
**Closes on:** §10 metadata item M-4.

### 5.3 U-3 — Padding and attention-mask semantics

Padding side, padding strategy, effective maximum length, truncation rule, lowercasing, and mask construction are unrecorded or `OFFICIAL_EXTERNAL`-only. `padding=max_length` is a *shorthand*, explicitly declared insufficient as a complete SigLIP2 preprocessing identity (`20:54`). The repository never constructs or inspects an attention mask.
**Closes on:** §10 metadata item M-5.

### 5.4 U-4 — Pooling, normalization and projection behavior

The pooling reduction for V2 is `NOT_OBSERVED`. "Final-sequence-position pooling" appears only as a verification target (`design spec:114`). The resolver for "which position is final" under `padding=max_length` + right padding is undefined, and the naive reading of that phrase is unsafe (§7). L2 normalization is `INTENDED`, not measured, for V2 (`05:65-72`). The SO400M text projection width is `OFFICIAL_EXTERNAL` only.
**Closes on:** §10 metadata items M-6, M-7.

### 5.5 U-5 — Processor / image–text compatibility

No record establishes that the image processor and the tokenizer in a frozen bundle were jointly trained, share a revision, or produce inputs the paired text/vision towers accept as a matched pair. `14_TEST_AND_ACCEPTANCE_MATRIX.md` T023/T024 require the match but define no expected values. The only recorded pairing evidence is the historical V1 7/7-MISS/max_length anecdote (`design spec:112`), which is V1 and is a padding bug, not a compatibility proof.
**Closes on:** §10 metadata item M-8.

### 5.6 U-6 — Base versus SO400M identity differences

Deterministically different (384 vs 224 resolution, patch 14 vs 16, 1152 vs 768 width, different upstream pins) and both are SigLIP2. But the repository simultaneously claims a "same SigLIP2 preprocessing family" (`04:29`) and that SO400M preprocessing "differs appropriately from V2 Base" (`12:90`) without ever stating the difference. Base text projection width is unrecorded; SO400M's is `OFFICIAL_EXTERNAL`.
**Closes on:** §10 metadata items M-1, M-6, M-9.

### 5.7 Per-profile question registers

`lane-d-tokenizer-forensics.md` §6 lists V1-Q1..Q5, B-Q1..B-Q6, S-Q1..S-Q7. They are adopted here by reference and are not restated, to keep this document the sizing surface rather than a second copy. Any resolution MUST update both that register and this document.

---

## 6. Contradiction register (adopted, unresolved)

The following contradictions were verified in the design/migration record set (`lane-b-design-docs.md` §2/§3, `lane-a-authority-and-adr.md` §7). They are recorded, **not resolved by preference**. Each is a defect in the documentation that a future authentic-evidence pass or an owner decision must close.

| Id | Contradiction | Records |
|---|---|---|
| X01 | `max_length=64`/`truncation` are presented as contract values, while the same pack says class defaults are not a substitute for serialized checkpoint configuration | `05:73-78` vs `20:202` |
| X02 | Three vocabulary sizes (256000 / 32000 / 0..31999) never tied to one another or to a frozen asset | `04:123`, `05:121`, `20:202`, `design spec:112` |
| X03 | 49406/49407 cannot be emitted under `0..31999`; the pairing describes two different objects | `design spec:112` |
| X04 | Warning status stated four incompatible ways | `step10:18`, `owner-review-packet:34`, `21:200-204`, `12:17` |
| X05 | Warning attributed to SO400M, to V1, and to no profile | `design spec:112`, `20:202`, `step10:18` |
| X06 | Required profile field set (`pad direction/ID, attention mask, pooling/special-token contract`) is not representable by the single `text_preprocessing_contract` field | `design spec:69` vs `10:43-61` |
| X07 | SO400M text preprocessing asserted with no SO400M receipt | `05:102-105,128-133` |
| X08 | "Same SigLIP2 preprocessing family" vs "differs appropriately" | `04:29` vs `12:90` |
| X09 | `embedding_dimension_status` advertises a crosscheck the evidence pack says cannot substitute for the checkpoint | `05:65-72` vs `20:202` |
| X10 | T023 status cell conflates a V1 fixture pass with V2 evidence | `14:130` |
| X11 | `v2_design_change_supported: false` vs refresh disposition `PASS_RETAIN_DESIGN_RECOMMENDATION` | `21:200-204` vs `run-20261011-vip-v2-task0-plan-owner-review/owner-review-packet.md:73` (the label; `18:141` carries only the F07/`NO_GO_BLOCKED` remainder) |
| X12 | V1 text contract is both a driftable `SNAPSHOT` and a measured contract | `18:70` vs `03:20`, `05:32` |
| X13 | "Full SigLIP2 contract" is never defined as a field set | `design spec:69`, `04:163-174` |
| X14 | `spiece.model` vs `tokenizer.model` relationship never stated | `03:58-59`, `13:53-63`, `20:69` |

Plus five authority/state contradictions carried from the PR #193/#196 disposition work (`lane-a-authority-and-adr.md` §7), described here so a reader need not open the lane:

- **C-1** — the migration plan is recorded as `OWNER_APPROVED_FOR_PLANNING` (`plan:14`) while `docs/INDEX.md:53` and `26:29` record plan review as pending (`PENDING_OWNER_PLAN_REVIEW`).
- **C-2** — the local V1 bundle digest is reported as re-hashed in one record and as `NOT_OBSERVED` in another; reconciled as **temporal** (different observation dates), not as a live disagreement.
- **C-3** — T9-SYN governance adoption (`ADR-0002:547`) vs a preserved pre-adoption M3 record still labelled `PREPARED_FOR_EXACT_OWNER_ADOPTION`.
- **C-4** — the base commit itself is the merge of PR #201, and `#201` is cited nowhere under `docs/`. A provenance gap, not a defect in any claim.
- **C-5** — the vocabulary-scale contradiction, which is the subject of §4 and is the one contradiction a future authentic-evidence pass must close.

---

## 7. Alternatives and ambiguity table

Purpose: name the plausible contract shapes so that no future implementer silently picks one.

| Id | Axis | Alternative A | Alternative B | Alternative C | Discriminator | Current status |
|---|---|---|---|---|---|---|
| A-1 | Tokenizer family | SigLIP-1-style SentencePiece `spiece.model` continues into SigLIP2 | SigLIP2 ships a different tokenizer serialized as `tokenizer.model`/`tokenizer.json` | Both files exist but only one is consumed; the other is vestigial | the concrete class + file actually loaded from the frozen bundle | unresolved; `spiece.model` present in V1 tuple, `tokenizer.model` named for V2, relationship unstated |
| A-2 | Vocabulary size | 256000 as the public configs report | 32000 library class default | 32k-range diagnostic (`0..31999`) was the real tokenizer | declared config vs `len(tokenizer)` vs embedding rows, one bundle | unresolved; three numbers recorded |
| A-3 | BOS/EOS ids | 49406/49407 are authentic BOS/EOS | they are in-range ordinary tokens, not BOS/EOS | one is BOS/EOS and the other is not; or both are added tokens | `bos_token_id`/`eos_token_id` + `added_tokens` from the frozen tokenizer | unresolved; cannot be asserted either way |
| A-4 | Padding | right padding as in the SO400M diagnostic | left padding | no explicit padding; library default applies | `tokenizer.padding_side` + observed pad positions | unresolved for both V2 arms |
| A-5 | Max length | 64 (library default) | the frozen checkpoint's own configured value | uncapped/derived from the text tower's position limit | serialized `tokenizer_config.json` value | unresolved |
| A-6 | Attention mask | explicit mask returned by the processor | mask omitted and inferred by the model | mask present but ignored by the caller | observed processor output keys and the model call signature | unresolved |
| A-7 | Pooling | library `pooler_output` (as in the V1 path) | explicit "final sequence position" slicing | masked attention/mean reduction | upstream class behavior + numerical agreement | unresolved; `pooler_output` is V1-only precedent |
| A-8 | Pooling under padding | mask-aware selection of the last real token | naive last index of the padded window (unsafe) | the model's own pooler handles it | comparison of a short text embedded alone vs embedded in a padded batch | unresolved; **naive last index is the named hazard** |
| A-9 | Normalization | L2 applied by the repository after the forward pass | L2 applied inside the model head | no normalization; retrieval normalizes later | output norms before/after, and per-tensor inspection | unresolved; L2 is `CANDIDATE_ASSUMPTION` for V2 |
| A-10 | Text projection | projection inside the text tower yielding 768/1152 | separate projection head applied by the caller | both, double-applied (a real risk) | output width + presence/absence of a projection module in the loaded model | unresolved; SO400M `text_projection_size` is `OFFICIAL_EXTERNAL` |
| A-11 | Image/text pairing | processor and tokenizer from the same frozen revision | imported independently per module | mixed revisions in one directory | shared revision + digests + joint provenance metadata | unresolved |
| A-12 | Preprocessing identity definition | digest of a fixed asset subset | digest of the resolved processor configuration | digest of observed tensor outputs | owner-accepted definition | unresolved (`05:140-149`) |

**Named hazard (asserted, independent of the vocabulary question):** `padding="max_length"` with right padding combined with a naive "final sequence position" pool selects a **pad** position for every text shorter than `max_length`, producing a valid, unit-norm, semantically meaningless vector. `design spec:114` requires mask-aware verification; `plan:37` records the same failure class as "misleading valid text vectors". Any future authentic implementation MUST resolve pooling position as a function of the mask, and a unit-norm output MUST NOT be accepted as evidence of correctness.

---

## 8. Provisional contract statement

This is the contract a future authentic implementation MUST satisfy. It is written conditionally because no value is known. It is **non-executable**: nothing here may be turned into a constant, a default, or a loader.

**P-1 (identity before behavior).** A session may open only after the frozen bundle's tokenizer asset set is enumerated and digested, and after every artifact the loader would consume is proven to be a member of that set by digest.

**P-2 (tokenizer binding).** The session MUST record the resolved tokenizer class name, module, library version, and the exact asset file(s) it consumed. An unresolved class or an asset outside the enumerated set MUST refuse.

**P-3 (vocabulary consistency).** The session MUST record three independent numbers — declared config vocabulary size, tokenizer-object vocabulary length, text-embedding row count — and MUST refuse when any pair disagrees. No constant (`49406`, `49407`, `31999`, `32000`, `256000`) may be hardcoded as a contract value.

**P-4 (special tokens).** BOS, EOS, pad, unk and all added-token ids MUST be read from the frozen tokenizer and MUST each satisfy `0 <= id < text_embedding_rows`. A recorded BOS/EOS pair that violates the range MUST refuse, not warn.

**P-5 (padding and mask).** Padding side, padding strategy, effective maximum length, truncation and lowercasing MUST be recorded as observed resolved values, not as the shorthand string. The emitted attention mask MUST be captured and its shape and pad positions asserted.

**P-6 (pooling).** The pooling reduction and the pool-position resolver MUST be pinned and MUST be mask-aware. A pooled vector produced by a pad position MUST be rejected.

**P-7 (normalization and width).** Output width MUST equal the profile's `embedding_dim`; normalization MUST be the profile's declared rule; non-finite, zero, or wrongly-normalized rows MUST refuse.

**P-8 (pairing).** Image processor and tokenizer MUST be shown to come from the same frozen revision and to be the pair the checkpoint expects; a mismatched pair MUST refuse.

**P-9 (provenance).** All of P-1..P-8 MUST be recorded in an acceptance receipt with the exact bundle digests, library versions, device, precision policy and observed values. Anything unobserved MUST be recorded as `NOT_OBSERVED` and the session MUST be disposed `BLOCKED_SEMANTIC_CORRECTNESS`, never `PASS` (`plan:162`).

**P-10 (no inference).** No token id, vocabulary size, padding side, mask rule, pooling rule or projection behavior may be derived by inference from public documentation, from the V1 profile, or from a numerical test that passes.

---

## 9. Fail-closed validation expectations for a future authentic implementation

Test identifiers are specified here; they are **not implemented**, and specifying them creates no test authority. Naming follows the plan's existing vocabulary (`plan:128`) where a name already exists.

### 9.1 Pre-open (identity and provenance)

| Id | Requirement | Refusal on violation |
|---|---|---|
| FC-01 | Tokenizer asset set enumerated and digested before open | `SIGLIP2_TOKENIZER_ASSETS_UNVERIFIED` |
| FC-02 | Every consumed artifact is a digest member of the enumerated set | `SIGLIP2_ASSET_NOT_IN_BUNDLE` |
| FC-03 | Revision is immutable and not a mutable branch label | `SIGLIP2_MUTABLE_OR_WRONG_MODEL_BUNDLE` |
| FC-04 | Offline only: `local_files_only=True`, `trust_remote_code=False`, `use_safetensors=True`, no remote fallback | `SIGLIP2_REMOTE_OR_REMOTE_CODE_DISALLOWED` |
| FC-05 | Digests identical before and after open | `SIGLIP2_ASSET_MUTATED_DURING_OPEN` |

### 9.2 Tokenizer and vocabulary

| Id | Requirement | Refusal on violation |
|---|---|---|
| FC-06 | `test_siglip2_text_special_token_contract_rejects_inconsistent_ids` — BOS/EOS/pad within `[0, rows)` | `SIGLIP2_SPECIAL_TOKEN_OUT_OF_RANGE` |
| FC-07 | Declared config vocab == tokenizer-object vocab == embedding rows | `SIGLIP2_VOCABULARY_INCONSISTENT` |
| FC-08 | Tokenizer class resolves and matches the recorded class | `SIGLIP2_TOKENIZER_IDENTITY_MISMATCH` |
| FC-09 | Emitted ids for a fixed probe string match a recorded reference vector of ids | `SIGLIP2_TOKENIZATION_REFERENCE_MISMATCH` |

### 9.3 Padding, truncation, mask

| Id | Requirement | Refusal on violation |
|---|---|---|
| FC-10 | `test_siglip2_mask_pad_truncation_pooling_contract` — padded batch shape `(batch, L)` where `L` is supplied by M-5 (writable only once M-5 exists) | `SIGLIP2_PADDING_CONTRACT_MISMATCH` |
| FC-11 | Pad ids occupy exactly the recorded side/positions | `SIGLIP2_PADDING_SIDE_MISMATCH` |
| FC-12 | Mask is zeros exactly where pad ids occur | `SIGLIP2_ATTENTION_MASK_INCONSISTENT` |
| FC-13 | Over-length input truncates to the recorded maximum length | `SIGLIP2_TRUNCATION_CONTRACT_MISMATCH` |
| FC-14 | Lowercasing behavior matches the frozen config | `SIGLIP2_CASING_CONTRACT_MISMATCH` |

### 9.4 Pooling, normalization, output

| Id | Requirement | Refusal on violation |
|---|---|---|
| FC-15 | Pooling is not a pad-position vector: a short text embedded alone equals the same text embedded in a padded batch. The tolerance is supplied by M-6 and MUST be recorded, never invented by the test author | `SIGLIP2_POOL_POSITION_UNSAFE` |
| FC-16 | Pooling reduction equals the reduction supplied by M-6 (not the repository's own invention; not token-mean unless M-6 says so) | `SIGLIP2_POOLING_CONTRACT_MISMATCH` |
| FC-17 | Output width == profile `embedding_dim` (768 / 1152) | `SIGLIP2_OUTPUT_WIDTH_MISMATCH` |
| FC-18 | Output dtype and normalization match the precision/normalization policy | `SIGLIP2_OUTPUT_POLICY_MISMATCH` |
| FC-19 | `test_encoder_rejects_wrong_width_nonfinite_or_zero` — non-finite / zero / wrong-width rows refuse | `SIGLIP2_OUTPUT_VALUES_INVALID` |

### 9.5 Processor, pairing, device, receipt

| Id | Requirement | Refusal on violation |
|---|---|---|
| FC-20 | Image `pixel_values` shape == `(1, 3, image_size, image_size)` per profile | `SIGLIP2_IMAGE_PREPROCESSING_MISMATCH` |
| FC-21 | Image preprocessing parameters (rescale/mean/std/interpolation/crop) equal the values supplied by M-6/M-9 per arm (the SO400M arm is writable only once SO400M values exist) | `SIGLIP2_IMAGE_PARAMETER_MISMATCH` |
| FC-22 | Image processor and tokenizer share the frozen revision | `SIGLIP2_PROCESSOR_TOKENIZER_REVISION_MISMATCH` |
| FC-23 | `test_so400m_wrong_tokenizer_identity_rejected` — a Base tokenizer with the SO400M profile refuses | `SIGLIP2_WRONG_TOKENIZER_IDENTITY` |
| FC-24 | `test_mps_requested_unavailable_refused` — no silent CPU fallback | `SIGLIP2_DEVICE_UNAVAILABLE_NO_FALLBACK` |
| FC-25 | Authentic-claim guard remains: injected doubles can never set `authentic=True` | `SIGLIP2_AUTHENTIC_HANDOFF_REQUIRES_NATIVE_ACCEPTANCE` |
| FC-26 | Acceptance receipt carries the field list defined by M-12 and marks unobserved ones `NOT_OBSERVED` | `SIGLIP2_RECEIPT_INCOMPLETE` |

### 9.6 Disposition rule

If any of FC-06..FC-09, FC-15..FC-16, or the pooling-position check cannot be resolved from authentic evidence, the only permitted disposition is `BLOCKED_SEMANTIC_CORRECTNESS` (`plan:162`) or `NOT_VERIFIED` (`plan:188`). A numerically passing retrieval metric, a unit-norm vector, or a non-crash MUST NOT upgrade the disposition. This is the operational meaning of `12:17`: preserve the fail-closed semantic-validation gate; do not rewrite token ids by inference.

---

## 10. Permitted metadata and asset evidence required before model runtime adoption

This is the exact evidence set required before any authentic V2 runtime adoption. **None of it may be collected under this document's authority.** Collection requires the owner-authorized authentic session of WBS G1.3.1 (`[ ]`, `WBS:160`).

### 10.1 Metadata items (required, per arm)

| Id | Required metadata | Why it is load-bearing | Closes |
|---|---|---|---|
| M-1 | Exact frozen revision per arm (immutable SHA, no branch label) | `10:93`: mutable branch labels must fail closed | U-1, U-6 |
| M-2 | Per-asset digests for the full tokenizer/processor asset set, plus the set's own enumeration | digests are the only membership proof (`model_space.py:95-123`) | U-1 |
| M-3 | Concrete tokenizer/processor class name + module + library version actually resolved | the V2 loader class is itself explicitly unknown (`04:163-174`) | U-1 |
| M-4 | `bos_token_id`, `eos_token_id`, `pad_token_id`, `unk_token_id`, added-token map; each with its serialized source | U-2 and the `0..31999` anomaly | U-2 |
| M-5 | Padding side, padding strategy, effective maximum length, truncation, lowercasing, and an observed attention mask | U-3 | U-3 |
| M-6 | Pooling reduction + pool-position resolver semantics, stated by the upstream model class and, only under a separate owner-scoped numeric check, confirmed numerically | U-4 and the §7 hazard | U-4 |
| M-7 | Output width, dtype, normalization rule; SO400M text projection size from the frozen config | U-4 | U-4 |
| M-8 | Joint provenance showing the image processor and tokenizer are the pair the checkpoint expects | U-5 | U-5 |
| M-9 | Base text projection width and Base tokenizer asset inventory | `04:90` notes the public Base `config.json` omits inherited geometry | U-6 |
| M-10 | Declared config vocabulary size, tokenizer-object vocabulary length, and text-embedding row count — as one measured triple | the only way to close X02/X03 | U-1, X02, X03 |
| M-11 | Owner-accepted definition of the SigLIP2 `image_preprocessing_digest` | `05:140-149` lists the field as `unresolved_until_authorized_acquisition` | X09, A-12 |
| M-12 | An acceptance receipt recording all of the above with `NOT_OBSERVED` for anything unmeasured | P-9, FC-26 | all |

### 10.2 Permitted asset evidence (minimum, still requiring authorization)

Only the following files may ever supply the tokenizer contract, and only from a frozen, digest-verified bundle:

`config.json` (specifically its text-config vocabulary declaration and projection geometry), `tokenizer_config.json`, `tokenizer.json`, `tokenizer.model`, `special_tokens_map.json`, `spiece.model`, `preprocessor_config.json`. Note that `spiece.model` is **V1-only** in the repository record; it is included here for V1 identity reconciliation and is not a V2 tokenizer assumption.

Requirements on any such read:

1. The bundle is local, frozen, and revision-pinned; nothing is fetched.
2. Every file read is digested before and after the read.
3. Reading is recorded as an explicit authorized act with its scope, not as a side effect of an import.
4. No weights are loaded, no forward pass is run, no device tensor is created, and no inference is executed to obtain M-1..M-5 or M-7..M-12. The single exception in the M list is M-6's numeric confirmation, which is **not** granted by this document and requires its own separate owner-scoped authorization; everything M-6 needs can otherwise be stated by the upstream class.
5. A read that produces a value contradicting a repository record MUST be recorded as a contradiction, not silently used to overwrite the record.

### 10.3 Explicitly not sufficient

- Public model cards, config pages, or library documentation (mutable `main` pages; `20:73`, `20:200`, `21:201-202`).
- The V1 profile's values, by analogy (`10:95-99`).
- A passing numerical or retrieval test (`design spec:21`, `plan:131`).
- Any synthetic or mocked session result (ADR-0002 `:529`, `:531`).
- Any statement in this document.

---

## 11. Blocker list

| Id | Blocker | State | Source |
|---|---|---|---|
| B-1 | Gate B full-migration gate | `NO_GO_BLOCKED` | `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md:32,:40`; `WBS:141` |
| B-2 | Native Task-4/5 source-only exception | `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION` | `ADR-0002:535-537,:543` |
| B-3 | Authentic V2 tokenizer/processor/pooling contract | `BLOCKED` (no authentic evidence) | this document; `DECISION_MATRIX.md` D-2 |
| B-4 | Authentic adapter/CLI source work (G1.2.3 first bullet, G1.2.4) | `BLOCKED` | `disposition/README.md:165`; `WBS:151,:155` |
| B-5 | `03_V1_BASELINE_SNAPSHOT.md:154` V1 receipt | `BLOCKED` (unchanged) | `WBS:136`; `01_CURRENT_STATE_AND_HANDOFF.md:3` |
| B-6 | Real weights acquisition/load (G1.3.1) | `NOT_AUTHORIZED` | `WBS:160` |
| B-7 | Benchmark (G1.4) | `BLOCKED` (depends on B-1..B-3) | `ADR-0002:380-402` |
| B-8 | The `0..31999` warning | unresolved, owner/arm unassigned; four incompatible status records | §4 |
| B-9 | Profile schema cannot represent the required contract field set | unresolved documentation defect | X06 (`design spec:69` vs `10:43-61`) |
| B-10 | Provisionally recorded contradictions X01–X14 plus C-1..C-5 | unresolved; none resolved by preference here | §6 |

---

## 12. Precise implementation prerequisites

A future implementation is permitted to start only when **all** of the following hold. Each is a gate, not a checklist item of convenience.

1. An owner instrument grants that exact implementation scope, naming the paths; ADR-0002 Amendment 2 (`:519-533`) covers synthetic slices only and grants no authentic work; the native exception is not adopted.
2. The profile schema is extended (or an accepted equivalent is authorized) so that the contract field set of `design spec:69` is representable: pad direction/ID, truncation, maximum length, attention mask, pooling and special-token contract, plus tokenizer asset digests as first-class fields. Today `10:43-61` cannot represent them (X06).
3. M-1..M-11 are collected from one frozen digest-verified bundle under the §10 constraints, and the measured vocab triple (M-10) is consistent.
4. The §9 fail-closed tests exist as RED tests before any implementation code, per the plan's TDD ordering.
5. The acceptance receipt schema (M-12) exists and can express `NOT_OBSERVED` and `BLOCKED_SEMANTIC_CORRECTNESS`.
6. Gate B's own prerequisites are satisfied for the operation requested — this document cannot help with that.
7. Any conflict between collected values and repository records is recorded as a contradiction with both citations retained.

---

## 13. WBS recommendations

Documentation-only. These recommendations change no checkbox and grant nothing; they are inputs to a future owner-authorized WBS delta packet (the disposition's D-3 item).

1. **Keep `WBS:152` unchecked and keep its `PARTIAL source-only seam` wording.** This document strengthens, and does not discharge, that bullet: the per-arm BOS/EOS/padding/pooling question remains unresolved and now has a named home (`32_…CONTRACT.md` §5, §6).
2. **Add a reference, not a status change.** Point `WBS:152` at this document as the provisional contract statement, replacing nothing. The WBS checkmark policy (`WBS:354`) forbids flipping a box from document existence.
3. **Split the residual G1.2.3 work into three explicit blockers** so no future reader collapses them: (a) authentic tokenizer contract (B-3), (b) authentic adapter source (B-4), (c) profile-schema representability (B-9).
4. **Record B-8 (`0..31999` warning) as a named unresolved item with an arm-attribution task** rather than as an explanation; four records currently disagree on its status (X04) and three on its arm (X05).
5. **Do not create a G1.2.x sub-item for "document the tokenizer contract".** It is documented, not discharged; creating a checkbox would invite a false completion signal.
6. **Note that Gate B and `03_V1_BASELINE_SNAPSHOT.md:154` are untouched** by this work, so the next WBS reader does not infer progress toward Gate acceptance.

---

## 14. Source references

### 14.1 Governing

- `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md` (`:21-28`, `:113-120`, `:136-144`, `:154-166`, `:184-191`, `:420-437`, `:493-517`, `:519-533`, `:535-543`, `:545-559`)
- `docs/decisions/ADR-0003-development-source-authorization-enforcement-removed.md:53-57,:84-98`
- `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md:136-160,:354`
- `docs/project/01_CURRENT_STATE_AND_HANDOFF.md:3`
- `docs/INDEX.md:53`

### 14.2 Migration pack

`00_README_AND_ENTRYPOINT.md`, `02_PACKAGE_MANIFEST.yaml`, `03_V1_BASELINE_SNAPSHOT.md`, `04_MODEL_CONTRACTS.md`, `05_model-contracts.yaml`, `06_MODEL_COMPATIBILITY_MATRIX.md`, `08_HARDCODE_AND_ASSUMPTION_REGISTER.md`, `10_TARGET_MODEL_PROFILE_DESIGN.md`, `11_V1_TO_V2_BASE_RUNBOOK.md`, `12_V2_BASE_TO_SO400M_RUNBOOK.md`, `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md`, `14_TEST_AND_ACCEPTANCE_MATRIX.md`, `18_STALENESS_AND_REVERIFY_REGISTER.md`, `20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md`, `21_source-receipts.yaml`, `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`.

### 14.3 Design, plan, run records

- `docs/superpowers/specs/2026-10-09-vip-v2-siglip2-integration-design.md:20-21,:69,:110-114,:131,:145,:184`
- `docs/superpowers/plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md:25-37,:115-132,:151-163,:165-177,:188,:286-295`
- `docs/agent-runs/2026-10-25-g1-1-4-draft-193-independent-disposition/README.md`, `DECISION_MATRIX.md`, `SIX_CYCLE_LEDGER.md`
- `docs/agent-runs/2026-10-25-g1-1-4-representation-baseline-reconciliation/README.md:224-235,:282-287,:432-449`
- `docs/agent-runs/run-20261011-vip-v2-task0-plan-owner-review/step10-step12-assessment.md:18`, `owner-review-packet.md:34`

### 14.4 Code and tests (snapshot base)

`experiments/persistent_local_index/model_profile.py`, `siglip2_native.py`, `model_space.py`, `embedding.py`; `src/gate0/adapters/siglip_local.py`; `experiments/persistent_local_index/tests/`; `tests/gate0/`, `tests/gate1/`, `tests/vip_fvs/`.

### 14.5 This run

`docs/agent-runs/2026-10-25-g1-2-3-provisional-tokenizer-contract/README.md`, `SIX_CYCLE_LEDGER.md`, and `lanes/lane-a-authority-and-adr.md`, `lanes/lane-b-design-docs.md`, `lanes/lane-c-code-surface.md`, `lanes/lane-d-tokenizer-forensics.md`.

---

## 15. Non-claims and verification record

### 15.1 Non-claims

This document does **not** claim, assert, imply or predict:

- any tokenizer family, class, revision, vocabulary size, or token id for V2 Base or V2 SO400M;
- that 49406/49407 are or are not authentic BOS/EOS;
- that `0..31999` or `256000` describes any project-owned tokenizer;
- any padding side, maximum length, truncation or attention-mask rule;
- any pooling reduction, pool position, normalization point or projection behavior;
- that the historical warning is explained, or that it is a V1 or SO400M defect;
- any model load, device behavior, precision, latency, memory or retrieval quality;
- that any V2 profile is runtime-eligible;
- any Gate B movement, Task 0 change, WBS checkmark, or owner approval.

### 15.2 Verification record

- Base: `7b72e2b35716d4877d937c1eaff57cc160bc9c15`, confirmed as `origin/main` before work (`git fetch --prune origin`).
- Lane evidence: four read-only lanes, each with one exclusive file, no tracked-tree writes, no model/asset/network operation.
- Code facts: `VERIFIED_SOURCE_FACT` by reading the cited source; suite counts reproduced at the snapshot base by Lane C — `experiments/persistent_local_index/tests` 310 passed / 10 skipped; `tests/gate1` 211 passed; `tests/vip_fvs` 1217 passed / 1 xfailed.
- No test in this work asserts authentic tokenizer behavior, because no authentic tokenizer evidence exists to assert.
- Prohibited operations observed as prohibited: no download, no authentic asset inspection, no model load, no inference, no provider call, no protected-media access, no authentic runtime implementation.
- Six-cycle refinement ledger: `docs/agent-runs/2026-10-25-g1-2-3-provisional-tokenizer-contract/SIX_CYCLE_LEDGER.md`.

### 15.3 Reconsideration triggers

This document must be revised when any of the following occurs: an authentic V2 arm identity is adopted; an owner authorizes a permitted read of the frozen tokenizer/processor assets; an owner accepts this provisional statement as a planning basis; the model-profile schema is extended to represent the full text contract; or any of B-1..B-10 changes state.
