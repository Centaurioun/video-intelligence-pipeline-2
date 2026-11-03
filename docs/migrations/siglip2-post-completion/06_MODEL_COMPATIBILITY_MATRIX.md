# Model Compatibility Matrix

**Information state:** `VERIFIED_CURRENT` + `OFFICIAL_EXTERNAL` + `SNAPSHOT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Repository snapshot:** `main@6cce8777b6aa9ad672a5ca36428506f78d30db6f`

## Purpose

This matrix separates changes that are genuinely required for the first migration from changes that become necessary only when the So400m representation is added.

It is intentionally conservative: “same” means the observed contract can probably be preserved, not that migration is already proven.

## High-Level Compatibility

| Concern | V1 Base → V2 Base | V2 Base → V2 So400m | Interpretation |
|---|---|---|---|
| Model family | **CHANGE** SigLIP → SigLIP2 | SAME family | First migration introduces SigLIP2 semantics/runtime contract |
| Model ID/revision/hash | **CHANGE** | **CHANGE** | Every candidate is a distinct semantic space |
| Image input size | 224 → 224 | **224 → 384** | So400m changes image preprocessing geometry |
| Patch size | 16 → 16 | **16 → 14** | So400m-specific architecture difference |
| Embedding width | 768 → 768 expected | **768 → 1152** | So400m forces removal of fixed-width assumptions |
| Vector dtype | preserve `float32` unless design changes | preserve unless design changes | Current VIP storage/search contract is float32 |
| Vector normalization | preserve L2 unless design changes | preserve unless design changes | Current semantic-space identity records normalization |
| Loader API | **REVALIDATE/LIKELY CHANGE** | likely same SigLIP2 loader path | Official SigLIP2 examples use AutoModel/AutoProcessor |
| Text preprocessing | **CHANGE/EXPAND CONTRACT** | same SigLIP2 family | SigLIP2 docs include lowercase, fixed length 64 and truncation |
| Processor asset inventory | **REVALIDATE** | **REVALIDATE** | Current V1 digest list includes V1-specific assets |
| Semantic-space ID | **NEW** | **NEW** | Never reuse V1/V2 vectors across spaces |
| Existing index vectors | **RE-EMBED REQUIRED** | **RE-EMBED REQUIRED** | Equal dimension does not imply compatible coordinates |
| Query exact scan | structurally likely reusable | structurally likely reusable | Current search derives width from live semantic space |
| Index write width | may work at 768 without width refactor | **MUST CHANGE** | Current indexer/storage contain `768 * 4` constants |
| Fake/test vectors | can remain 768 for V2 Base but should be prepared | **MUST CHANGE/PARAMETERIZE** | Several helpers derive from global 768 constant |
| PTS/timebase refinement | **PRESERVE** | **PRESERVE** | Representation migration does not alter temporal authority |
| Source provenance | **PRESERVE** | **PRESERVE** | Source identity is model-independent |
| Human editorial decision | **PRESERVE** | **PRESERVE** | Model only changes retrieval candidate generation |
| Edit plan/render/QC | **PRESERVE** | **PRESERVE** | Not justified migration surface |
| Full-archive index | do not rebuild until benchmark winner decision | same | ADR-0002 requires mini-benchmark first |

## V1 Base → V2 Base: Expected Work

The first migration is primarily a **semantic-model contract migration**, not a broad storage redesign.

Expected change areas:

- SigLIP2-compatible model/processor loading;
- processor/tokenizer asset identity;
- SigLIP2 text preprocessing contract;
- semantic-space provenance;
- future model-profile/configuration seam;
- tests that currently assume the V1 loader or V1 preprocessing assets.

The 768-dimensional shape can remain compatible at the storage level only if the exact acquired V2 Base checkpoint confirms that width. The semantic coordinates are still incompatible and require re-embedding.

## V2 Base → V2 So400m: Additional Work

The second migration adds **shape pressure** that V2 Base alone does not expose:

- 384-pixel image input;
- patch 14;
- 1152-dimensional vectors;
- larger vector row width;
- larger model/runtime burden;
- likely different practical batch-size/memory envelope.

Any production/test code that still assumes `768`, `768 * 4`, or “Base” geometry after the V2 Base migration becomes an explicit blocker for So400m.

## Already-Compatible or Partly Dynamic Areas

At this snapshot:

- `SemanticSpace` already stores `embedding_dim`, dtype, normalization, revision and digests;
- semantic-space IDs are derived from those fields;
- query-time search in `experiments/persistent_local_index/search.py` derives row width and column count from `live_spec.space.embedding_dim`;
- semantic-space mismatch handling already fails closed;
- V1 provenance already distinguishes model, revision, weights and processor identity.

These existing seams reduce migration risk but do not prove full multi-model support.

## Compatibility Does Not Mean Reuse

The following are forbidden interpretations:

- V1 Base and V2 Base both use 768 → reuse the same vectors;
- SigLIP2 FixRes is “backwards compatible” → current loader is automatically correct;
- query search is dimension-aware → indexing is dimension-aware;
- V2 Base works → So400m only needs a model ID change;
- public SigLIP2 results are higher → skip the local benchmark.

Each of those would erase a real contract difference.

## Reverify at V1 Completion

Re-run this matrix after the final V1 completion SHA is frozen, because the ongoing V1 project may remove or relocate some current hard-coded assumptions before migration begins.
