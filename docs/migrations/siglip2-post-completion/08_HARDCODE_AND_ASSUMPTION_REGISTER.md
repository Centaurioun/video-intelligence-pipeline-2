# Hard-Code and Assumption Register

**Information state:** `VERIFIED_CURRENT` + `SNAPSHOT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Repository snapshot:** `main@6cce8777b6aa9ad672a5ca36428506f78d30db6f`

## Purpose

This register captures assumptions that are harmless for the current V1 Base representation but can become migration defects if they survive into V2 Base/So400m unchanged.

Severity here means **migration impact**, not current-V1 bug severity.

| ID | Assumption / hard-code | Current locations | V2 Base impact | So400m impact | Future action |
|---|---|---|---|---|---|
| H001 | Global embedding width is 768 | `model_space.py`, CLI/runtime helpers | Low if Base confirmed 768 | **Blocking** | Move width behind validated model/profile contract |
| H002 | Vector row width is `768 * 4` | `storage.py`, `indexer.py`, multiple tests | Low at Base | **Blocking** | Derive from semantic-space dimension × dtype width |
| H003 | Current text contract is only `padding=max_length` | `model_space.py`, embedding paths, fixtures | **Material** | Material | Encode full SigLIP2 text contract explicitly |
| H004 | Loader classes are `SiglipModel` / `SiglipProcessor` | `src/gate0/adapters/siglip_local.py` | **Material** | Material | Verify exact acquired SigLIP2 loading path; official examples use Auto* |
| H005 | Processor asset inventory includes V1 `spiece.model` list | `model_space.py`, `local_model.py` via digest helper | **Material** | Material | Recompute required asset set from frozen acquired bundle |
| H006 | Adapter asset identity dimension is literal 768 | `src/gate0/adapters/siglip_local.py` | Low at Base | **Blocking** | Do not carry literal width into V2 runtime |
| H007 | Session dimension comes from global `EMBEDDING_DIM` | `embedding.py` | Low at Base | **Blocking** | Bind session width to validated model/profile |
| H008 | Synthetic/fake vectors use global Base width | persistent CLI, VIP retrieval adapter, test helpers | Low at Base | **Blocking for representative tests** | Parameterize synthetic dimension where future tests need 1152 |
| H009 | Real VIP CLI constructs `SemanticSpace` from V1 globals | `src/vip_fvs/cli.py` | **Material** | **Blocking** | Centralize model-space construction behind validated profile/contract |
| H010 | Equal dimension might be mistaken for compatible space | human/process risk | **Critical process risk** | Critical | Preserve model/revision/digest/preprocessing in semantic-space identity |
| H011 | Search being dimension-aware might be mistaken for full pipeline support | human/process risk | Medium | **High** | Require index/write + synthetic 1152 verification |
| H012 | Existing V1 processor digest logic may be assumed valid for SigLIP2 assets | digest boundary | **High** | High | Revalidate exact file inventory before freezing V2 digest |
| H013 | V1 Gate-0 adapter may be treated as the mandatory place to modify | historical boundary | Medium | Medium | Decide successor adapter vs historical Gate-0 edit during migration design |
| H014 | `float32` element width is assumed as 4 bytes in width arithmetic | search/index/storage | Low if preserved | Medium | Keep explicit dtype→byte-width contract; fail closed on unsupported dtype |
| H015 | V2 Base success may be assumed to prove So400m memory/batch behavior | operational assumption | None | **High** | Measure So400m locally; do not extrapolate as proof |

## Detailed Notes

### H001/H002 — Dimension and Row Width

The current data model already records `embedding_dim`, but write-side code still contains fixed Base-width constants.

The future target is not “replace 768 with 1152.” The target is to ensure dimension is derived from the selected, validated semantic/model contract so both V2 Base and V2 So400m are valid without divergent storage code.

### H003 — Text Preprocessing

Current V1 identity stores only the contract string:

`padding=max_length`

Official SigLIP2 documentation describes a richer default text preprocessing behavior including lowercasing, fixed maximum length 64, and truncation.

The migration must represent preprocessing strongly enough that two semantically different text pipelines cannot accidentally share one semantic-space identity.

### H004/H013 — Loader Boundary

The current Gate-0 adapter is deliberately frozen around the V1 SigLIP contract.

The future migration should not assume the cleanest solution is to edit this historical adapter in place. A successor adapter or a model-profile-aware loader may better preserve historical evidence. That is an `INFERRED_DESIGN` question for the post-completion migration design.

### H005/H012 — Processor Asset Identity

The current processor digest is deterministic over a fixed asset list. That is good provenance discipline.

The risk is not the digest mechanism; the risk is assuming the V1 asset list is complete for a future SigLIP2 bundle.

The future flow should:

1. acquire/freeze the exact authorized model bundle;
2. inspect its processor/tokenizer assets;
3. define the exact required set;
4. hash that set deterministically;
5. bind the digest into semantic-space identity.

### H008 — Test Fixtures

Some 768-D fixtures should remain permanently as V1 regression tests. Migration does not require erasing historical fixtures.

New variable-dimension/profile tests should be additive where possible so V1, V2 Base and 1152-D behavior can be distinguished.

### H014 — Dtype Width

Current search logic uses `embedding_dim * 4`, which is valid for the current `float32` contract.

If the future migration keeps float32, this remains valid. If dtype becomes configurable later, byte width must be derived from dtype as well as dimension. ADR-0002 does not currently require dtype variation, so a generic dtype framework is YAGNI unless the migration design introduces one deliberately.

## Revalidation Queries

At V1 completion, search current code/tests for:

`768`, `768 * 4`, `EMBEDDING_DIM`, `ROW_WIDTH_BYTES`, `DEFAULT_ROW_WIDTH_BYTES`, `SiglipModel`, `SiglipProcessor`, `padding=max_length`, `spiece.model`, `PROCESSOR_ASSETS`, and direct `SemanticSpace` construction.

Close or revise each register item against the final V1 completion SHA before implementation planning.

## 2026-10-11 Controlled Task 0 Reverification

Source searched: VIP canonical `748818e867ce08ccc2367bad21df7d83eaf51d70`; the migration-relevant code and test paths match preserved V1 `3586eeaa904fc5a2e6a2745078611886f482f3de`.

| IDs | Current evidence | Refresh disposition |
|---|---|---|
| H001, H006–H009 | Global 768 width remains in `model_space.py`, the V1 adapter/session, CLI construction and fake-vector helpers. | Confirmed current; unchanged. |
| H002 | `indexer.py` and `storage.py` retain fixed `768 * 4` row width; storage validates exactly 768 columns. | Confirmed current and blocking for 1152-D writes/recovery. |
| H003 | V1 text identity remains `padding=max_length`; no SigLIP2 runtime/text contract exists in VIP source. | Confirmed V1 fact; SigLIP2 contract remains `NOT_OBSERVED`. |
| H004, H013 | `src/gate0/adapters/siglip_local.py` uses `SiglipModel` and `SiglipProcessor`. | Confirmed current; preserve the historical Gate-0 adapter boundary. |
| H005, H012 | Current V1 processor asset set still includes `spiece.model`. No V2 bundle was inspected. | V1 fact confirmed; V2 inventory/digest remains `BLOCKED` by the no-model-access scope. |
| H010 | `SemanticSpace` includes model and digest identity independently of dimension. | Confirmed contract; equal-width cross-model mixing remains prohibited. |
| H011 | Search uses `SemanticSpace.embedding_dim`, while writer/recovery remains fixed-width. | Confirmed partial support; do not infer end-to-end 1152-D support. |
| H014 | Current vector storage remains float32 and byte arithmetic uses four bytes per element. | Confirmed V1 contract; no generic dtype work is authorized by this refresh. |
| H015 | No fresh V2/SO400M runtime, memory or MPS evidence was gathered. | Remains `NOT_OBSERVED`; prior reports are historical only. |

No register item was closed based on public model documentation or historical runtime observations. This refresh records source facts only and does not authorize implementation.
