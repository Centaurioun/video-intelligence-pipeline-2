# Migration Surface Snapshot

**Information state:** `VERIFIED_CURRENT` + `SNAPSHOT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Repository snapshot:** `main@6cce8777b6aa9ad672a5ca36428506f78d30db6f`  
**Scope:** current model-coupled production/test/configuration surface relevant to ADR-0002.

## Classification

Each entry uses one of four migration classes:

- **V2_BASE_CHANGE** — likely requires change for SigLIP2 Base.
- **SO400M_CHANGE** — can remain for V2 Base but must change for 1152-D/384 So400m.
- **ALREADY_DYNAMIC** — current logic already consumes semantic-space metadata rather than a fixed Base constant.
- **PRESERVE / REVIEW_ONLY** — should normally remain behaviorally unchanged; inspect only for integration compatibility.

This is a snapshot, not a future implementation plan.

## Production / Runtime Surface

### `experiments/persistent_local_index/model_space.py`
Snapshot SHA: `6d1ec3ff52076e4c3d85c18f1fa4cc81550d7384`

Current model-coupled points:

- `TEXT_PREPROCESSING_CONTRACT = "padding=max_length"`;
- `EMBEDDING_DIM = 768`;
- `EMBEDDING_DTYPE = "float32"`;
- `VECTOR_NORMALIZATION = "l2"`;
- `PROCESSOR_ASSETS` includes `spiece.model`;
- `SemanticSpace` already stores model/revision/digests/preprocessing/dimension/dtype/normalization;
- semantic-space identity and compatibility checks already include `embedding_dim`.

Classification:

- text/processor contract: **V2_BASE_CHANGE**;
- global dimension constant: **SO400M_CHANGE**, preferably addressed during V2 Base migration as targeted future-proofing;
- semantic-space schema/identity logic: **ALREADY_DYNAMIC / PRESERVE** unless an acquired model requires an additional identity field.

### `experiments/persistent_local_index/embedding.py`
Snapshot SHA: `d7981ba7038c45250ec46a405ee776610d164788`

Current points:

- imports global `EMBEDDING_DIM`;
- returns `LocalSiglipSession(... dimension=EMBEDDING_DIM)`;
- reuses the Gate-0 SigLIP adapter;
- explicit CPU/MPS handling with no silent MPS→CPU fallback;
- validates returned vector width against session dimension;
- V1 text padding contract is embedded in the wrapper semantics.

Classification:

- loader/processor and text contract: **V2_BASE_CHANGE**;
- fixed session dimension: **SO400M_CHANGE**, best parameterized during first migration;
- explicit device/fail-closed dimension checks: **PRESERVE**.

### `experiments/persistent_local_index/local_model.py`
Snapshot SHA: `536ec01dc914746474e64c74dadd7a5c7b3eda39`

Current points:

- identity validation is model-family-neutral in structure;
- processor digest calculation depends on `PROCESSOR_ASSETS` imported from `model_space.py`;
- exact local model revision/weights/processor are verified fail-closed;
- supports explicit CPU/MPS device choices;
- does not itself implement the Transformers runtime.

Classification:

- identity boundary: **PRESERVE / ALREADY_GENERIC**;
- processor asset set dependency: **V2_BASE_CHANGE/REVALIDATE**;
- runtime seam may be reusable if future loader is injected cleanly.

### `src/gate0/adapters/siglip_local.py`
Snapshot SHA: `83ce1db771d4be19bc162cc216f58f5186208b48`

Current points:

- imports `SiglipModel` and `SiglipProcessor`;
- V1-only CPU adapter contract;
- asset identity records dimension 768;
- text call uses `padding="max_length"`;
- local-only loading and weight verification are explicit.

Classification:

- direct V1 model/processor classes: **V2_BASE_CHANGE if reused**;
- fixed dimension: **SO400M_CHANGE**;
- offline-only/digest verification principles: **PRESERVE**.

Important boundary: this file is part of historical Gate-0 implementation. Future migration design should first decide whether to introduce a successor adapter outside this historical boundary rather than silently rewriting Gate-0 semantics.

### `experiments/persistent_local_index/storage.py`
Snapshot SHA: `c95c180dc44abc59590249880d3162cc8aab7b56`

Current point:

- `DEFAULT_ROW_WIDTH_BYTES = 768 * 4`.

Other storage logic accepts explicit row widths in multiple functions and keeps SQLite as mutable commit authority.

Classification:

- fixed default width: **SO400M_CHANGE**;
- commit/tail recovery semantics: **PRESERVE**;
- sibling semantic-space rejection: **PRESERVE**.

### `experiments/persistent_local_index/indexer.py`
Snapshot SHA: `b61db24259cf53f76b687ea572c24bee0037295b`

Current point:

- `ROW_WIDTH_BYTES = 768 * 4`;
- fixed constant is passed to vector-tail reconciliation paths.

Classification:

- row width constant: **SO400M_CHANGE**;
- source hashing, probing, PTS sampling, thumbnail staging, append/commit flow: **PRESERVE**.

### `experiments/persistent_local_index/search.py`
Snapshot SHA: `f44443703acd5fa2be30b99460bd4dfaf8e2c9d2`

Current points:

- validates committed byte alignment with `live_spec.space.embedding_dim * 4`;
- derives `row_width` from `live_spec.space.embedding_dim * 4`;
- derives matrix columns from `live_spec.space.embedding_dim`.

Classification:

- core dimension handling: **ALREADY_DYNAMIC**;
- semantic-space compatibility checks: **PRESERVE**;
- still requires later 1152-D synthetic/real verification before claiming So400m compatibility.

### `experiments/persistent_local_index/cli.py`
Snapshot SHA: `aa5d4f8f85d95443a2f0c089c2d475507646b811`

Current points:

- imports global `EMBEDDING_DIM`;
- constructs semantic space with the current constant;
- fake/synthetic vectors use the current constant.

Classification:

- model/preprocessing contract construction: **V2_BASE_CHANGE**;
- vector dimension/fake helpers: **SO400M_CHANGE** or profile-driven refactor during V2 Base.

### `src/vip_fvs/retrieval_adapter.py`
Snapshot SHA: `473948ce43ecc41f1b5e68a0208f58b217457fd0`

Current points:

- fake-vector generation expands to `EMBEDDING_DIM * 4`;
- fake semantic space uses `EMBEDDING_DIM`;
- real retrieval accepts explicit image/text embedders plus a `SemanticSpace`.

Classification:

- real semantic-space injection seam: **ALREADY_DYNAMIC / USEFUL**;
- fake-vector dimension: **SO400M_CHANGE** or profile parameterization during first migration.

### `src/vip_fvs/cli.py`
Snapshot SHA: `821bcd239baa60d5feae77bf55db2aa8489a07c3`

Current points:

- real runtime imports `EMBEDDING_DIM`, dtype, text contract and processor-digest helpers;
- constructs `SemanticSpace` directly from those V1 globals;
- opens local runtime through current `load_session`;
- duplicates equivalent model-space construction in more than one real-mode path.

Classification:

- current model-space construction: **V2_BASE_CHANGE**;
- global dimension use: **SO400M_CHANGE**;
- authorization-before-real-runtime principle: **PRESERVE**.

## Test Surface

### Persistent-local-index tests

Current snapshot includes explicit `768 * 4` or `embedding_dim=768` assumptions in:

- `experiments/persistent_local_index/tests/conftest.py`;
- `experiments/persistent_local_index/tests/test_indexer.py`;
- `experiments/persistent_local_index/tests/test_storage.py`;
- `experiments/persistent_local_index/tests/test_search.py`;
- `experiments/persistent_local_index/tests/test_search_materialization.py`;
- `experiments/persistent_local_index/tests/test_source_lifecycle.py`;
- `experiments/persistent_local_index/tests/test_cli_e2e.py`.

Migration interpretation:

- do not blindly replace every 768 fixture; some should remain V1 regression fixtures;
- add profile/dimension-focused coverage when future implementation begins;
- retain explicit mismatch tests proving incompatible spaces fail closed.

### VIP FVS tests

Current snapshot includes global dimension coupling in:

- `tests/vip_fvs/helpers.py`;
- `tests/vip_fvs/unit/test_local_semantic.py`.

Additional semantic-identity tests already exercise processor-digest differences, which is useful migration coverage and should be preserved.

## Surface That Should Not Be Pulled Into Model Migration

Absent new evidence, do not treat the following as representation-migration targets:

- source inventory and source immutability;
- source-native probe/PTS/timebase measurement;
- candidate temporal refinement;
- human decision artifacts;
- edit-plan semantics;
- preview/render authorization;
- technical/editorial QC;
- evidence-class definitions.

The migration changes retrieval representation, not the authority of downstream temporal/editorial evidence.

## Required Refresh

At V1 completion, repeat repository search for at least:

- `EMBEDDING_DIM`;
- literal `768`;
- literal `768 * 4`;
- `SiglipModel`;
- `SiglipProcessor`;
- `AutoModel`;
- `AutoProcessor`;
- `padding=max_length`;
- `spiece.model`;
- `PROCESSOR_ASSETS`;
- `embedding_dim`;
- `processor_digest`;
- direct `SemanticSpace(...)` constructors.

Any new/removed path changes this snapshot before it is used for migration planning.

## 2026-10-11 Controlled Task 0 Refresh

**Current source:** canonical VIP `748818e867ce08ccc2367bad21df7d83eaf51d70`, tree `ad0d988f003954a5964a71c5fd1bae3528f088c8`. **Preserved V1:** `3586eeaa904fc5a2e6a2745078611886f482f3de`. The relevant persistent-index, VIP FVS, Gate-0 adapter, and FVS test paths are identical between preserved V1 and current canonical main. Compared with the earlier `main@6cce8777b6aa9ad672a5ca36428506f78d30db6f` preparation snapshot, the persistent-index/FVS source and test delta is 54 files (8,185 insertions, 375 deletions); the same scoped delta exists at both preserved V1 and current main.

Fresh source search confirms the migration boundary remains as previously described:

- `experiments/persistent_local_index/model_space.py` still owns global `EMBEDDING_DIM = 768`, `float32`, L2 normalization, `padding=max_length`, and the V1 `PROCESSOR_ASSETS` list containing `spiece.model`.
- `experiments/persistent_local_index/indexer.py` still passes fixed `ROW_WIDTH_BYTES = 768 * 4` to tail reconciliation. `storage.py` retains `DEFAULT_ROW_WIDTH_BYTES = 768 * 4` and rejects vector arrays whose width is not 768.
- `search.py` derives read width and columns from `SemanticSpace.embedding_dim`; this remains a partial dynamic seam and does not remove the write/recovery limitation.
- The V1 session and CLI still construct their real runtime/semantic space from V1 constants. `src/gate0/adapters/siglip_local.py` still loads `SiglipModel`/`SiglipProcessor`. No `AutoModel`, `AutoProcessor`, or closed `ModelProfile` implementation was found in the searched VIP source.
- Existing `SemanticSpace` identity remains model/revision/digest/preprocessing/dimension/dtype/normalization-bound. Same-width V1 and V2 Base still require distinct semantic identities.
- `tests/vip_fvs/` now provides broad synthetic/source-authorization/PTS coverage; the exact T001–T026 path-to-test mapping and run receipts are appended to `14_TEST_AND_ACCEPTANCE_MATRIX.md` and the Task 0 machine-readable matrix.

This refresh confirms the snapshot's principal write-side 1152-D blocker and current model-profile seam. It does not authorize or implement a source-code change.
