# V1 Baseline Snapshot

**Information state:** `VERIFIED_CURRENT` + `SNAPSHOT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Authority parent:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`  
**Snapshot canonical main:** `e9eeaf939c7ab233b34d5c03298fd1399fa15c47`  
**Captured:** 2026-10-05  
**Purpose:** migration-relevant orientation only; this is not the final V1 completion record and does not authorize migration execution.

## Baseline Representation

The current local semantic representation is:

- model identity: `google/siglip-base-patch16-224`;
- frozen revision already used by the project: `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`;
- acquired `model.safetensors` SHA-256 recorded by the project: `2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8`;
- processor digest recorded by the real local pilot: `4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980`;
- current embedding dimension constant: `768`;
- current embedding dtype: `float32`;
- current vector normalization contract: `l2`;
- current text preprocessing contract: `padding=max_length`;
- current coarse semantic sampling interval: `4.5` seconds under the source-native PTS sampling policy.

Primary repository evidence for the frozen model identity and measured local pilot is:

- `docs/experiments/2026-09-21-local-semantic-real-pilot-report.md`;
- `docs/audits/2026-09-21-local-semantic-real-pilot-completion-reconciliation.md`;
- `docs/audits/2026-09-13-gate0-model-acquisition-reconciliation.md`.

These are historical/experimental evidence records; later V1 completion may add newer integration evidence.

## Current Semantic-Space Identity Structure

At this snapshot, `experiments/persistent_local_index/model_space.py` defines `SemanticSpace` with:

- `model_identity`;
- `frozen_revision`;
- `weights_sha256`;
- `processor_digest`;
- `image_preprocessing_digest`;
- `text_preprocessing_contract`;
- `embedding_dim`;
- `dtype`;
- `normalization`.

The semantic-space ID is deterministically derived from those fields. A mismatch in any semantic-space field fails closed.

This is a valuable migration seam: a SigLIP2 representation should become a different semantic space even when the vector dimension happens to remain 768.

## Current Model-Specific Constants

At this snapshot:

`experiments/persistent_local_index/model_space.py`

- `EMBEDDING_DIM = 768`
- `EMBEDDING_DTYPE = "float32"`
- `VECTOR_NORMALIZATION = "l2"`
- `TEXT_PREPROCESSING_CONTRACT = "padding=max_length"`
- required processor assets currently include `spiece.model`.

`experiments/persistent_local_index/storage.py`

- contains `DEFAULT_ROW_WIDTH_BYTES = 768 * 4`.

`experiments/persistent_local_index/indexer.py`

- contains `ROW_WIDTH_BYTES = 768 * 4`.

`experiments/persistent_local_index/embedding.py`

- creates `LocalSiglipSession(... dimension=EMBEDDING_DIM)`;
- loads the current Gate-0 local SigLIP adapter;
- supports explicit `cpu` and `mps` with no silent CPU fallback for requested MPS;
- checks returned image/text embedding columns against the session dimension.

`src/gate0/adapters/siglip_local.py`

- loads `SiglipModel` and `SiglipProcessor`;
- requires local-only loading and verifies the weights digest;
- records a current asset identity dimension of `768`;
- uses `padding="max_length"` for text embedding calls.

`src/vip_fvs/retrieval_adapter.py`

- current fake-vector helpers use `EMBEDDING_DIM`;
- fake semantic-space generation uses the same current dimension constant.

All paths and symbols in this section are **SNAPSHOT** facts and must be reverified after V1 completion.

## Already-Dynamic Surface

The current search path is not uniformly hard-coded to 768.

At this snapshot, `experiments/persistent_local_index/search.py` derives vector row width and matrix column count from:

`live_spec.space.embedding_dim`

for query-time opening/scanning.

This suggests part of the search layer is already dimension-aware. It does not prove that the full index/build/runtime path supports an arbitrary dimension.

## Current Local Runtime Evidence

The preserved real local pilot reports:

- runtime device: MPS;
- one source duration: 265.33 seconds;
- sampling policy: 4.5 seconds;
- exactly 59 indexed rows;
- index-build wall time: 52.55 seconds;
- semantic space: `3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a`;
- generation: `648dd7391ec2a92e51aacdd20d11c4bd5c1a5c3ce88755066c819e0faa852508`;
- seven frozen anchor queries reproduced byte-identical ranking/output on repeated equivalent runs.

The same report explicitly does **not** establish archive-scale behavior, general semantic quality, exact boundaries, or Gate-1 model superiority.

## Important Non-Claims

At this snapshot:

- full approximately 400-hour SigLIP1 indexing duration is `NOT_OBSERVED`;
- local SigLIP2 Base runtime is `NOT_OBSERVED`;
- local SigLIP2 So400m runtime is `NOT_OBSERVED`;
- project-specific V1 vs V2 retrieval superiority is `NOT_OBSERVED`;
- final V1 completion SHA is `NOT_OBSERVED`;
- final post-V1 dependency/runtime state is `NOT_OBSERVED`.

Do not replace these states with extrapolation during migration planning.

## Required Refresh at V1 Completion

Before this snapshot is used operationally, re-check at least:

1. canonical V1 completion SHA/tag;
2. all file paths and symbols listed above;
3. hard-coded `768` assumptions;
4. vector row-width assumptions;
5. model loader/processor classes;
6. processor-asset list;
7. text preprocessing contract;
8. fake-vector/test assumptions;
9. dependency/runtime versions;
10. current test coverage around semantic-space mismatch and dimensionality;
11. any new model-profile abstraction added by unrelated V1 work.

The future `19_POST_COMPLETION_REFRESH_PROTOCOL.md` will define the exact refresh procedure.

## 2026-10-11 Controlled Task 0 Refresh Evidence

This append-only observation is bound to canonical `main@748818e867ce08ccc2367bad21df7d83eaf51d70` (tree `ad0d988f003954a5964a71c5fd1bae3528f088c8`) and the preserved V1 ref `preservation/vip-v1-post-v2-design-20261009@3586eeaa904fc5a2e6a2745078611886f482f3de` (tree `a7fbe1b0dd1aa6c1dbcc14fda77e16b9958e7d0c`). The preserved commit is an ancestor of canonical main. The relevant `experiments/persistent_local_index/`, `src/vip_fvs/`, `src/gate0/adapters/`, and `tests/vip_fvs/` code/test paths are byte-identical between those two commits; current main therefore retains the preserved V1 implementation in this migration surface.

The historical pilot receipt at `docs/agent-runs/run-20260921-local-semantic-real-pilot/normalized-results.json` records model `google/siglip-base-patch16-224`, revision `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`, weights digest `2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8`, processor digest `4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980`, and semantic-space ID `3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a`. These remain historical pilot provenance; they are not freshly verified against the preserved V1 completion state. The preservation receipt is explicitly Git-ref-only and does not include private runtime, model, vector-index, or media bytes. This refresh did not inspect or hash any local model asset.

The existing 125-test record remains the exact prior evidence at preflight commit `b296b5ca5a805d151412cf848fa397266fe23052`; it is imported unchanged into the 2026-10-11 refresh evidence. Additional model-free synthetic coverage is recorded in the refresh run report. Neither test record establishes local model/runtime reproducibility. Exact completion-runtime applicability of the historical model and processor identities remains `BLOCKED` pending permitted evidence.

### Post-adoption receipt reconciliation

The later immutable artifact-identity and native runtime receipts (`989c1bc6923833a11cfd11b7b756ef1f4ffbe192`, `634bfed47aec8464c8ca61b15c376f2950c21060`) and current-runtime baseline `ce3f570016f3f13e9091fb6989f3a9d3ea783c7d` provide attributable identity/runtime evidence for the bounded local V1 run. This does not rewrite the historical pilot receipt or prove historical full-environment reconstruction. Tokenizer-emitted IDs, embedding-table compatibility, and semantic correctness remain `NOT_OBSERVED`.
