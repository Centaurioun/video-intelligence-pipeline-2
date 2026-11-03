# Target Model Profile Design

**Information state:** `INFERRED_DESIGN` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Authority parent:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`  
**Repository snapshot used for this design:** `main@34106df55fc07a18fd8594f379cd143710ad0127`

## Purpose

Define the smallest future representation boundary needed to support the three accepted candidates without turning the Video Intelligence Pipeline into a generic model framework.

The target is not “make every model pluggable.”

The target is:

- preserve a reproducible V1 Base;
- migrate cleanly to V2 Base;
- make the later V2 So400m extension a bounded profile/configuration change plus only genuinely model-specific runtime work;
- keep semantic-space provenance fail-closed.

## Design Principle

The current repository already has useful semantic-space fields, but model-specific values are split across globals, loader code, CLI construction, storage defaults, and tests.

The future design should converge those values behind one validated model profile.

Conceptually:

```text
ModelProfile
  -> validated local model identity
  -> loader / processor contract
  -> SemanticSpace
  -> embedding session
  -> index/search row shape
```

The model profile is configuration/identity authority for representation-specific values. It is not source-media authority, temporal authority, or execution authorization.

## Proposed Minimal Profile

A future implementation may use a frozen structure equivalent to:

```text
ModelProfile
  profile_id
  model_id
  family
  frozen_revision
  weights_sha256
  processor_asset_names
  processor_digest
  image_preprocessing_digest
  text_preprocessing_contract
  fixed_resolution
  image_size
  patch_size
  embedding_dim
  dtype
  normalization
  loader_kind
```

The exact Python type/name is not frozen by this preparation document. The post-completion design may rename fields if semantics remain equivalent.

## Field Semantics

### `profile_id`

Stable project-facing identity for the validated contract, for example:

- `vip-v1-siglip-base-224`;
- `vip-v2-siglip2-base-224`;
- `vip-v2-siglip2-so400m-384`.

It must not substitute for the actual model ID/revision/digests.

### `model_id`

Exact upstream model identity.

Required candidates:

- `google/siglip-base-patch16-224`;
- `google/siglip2-base-patch16-224`;
- `google/siglip2-so400m-patch14-384`.

### `frozen_revision`, `weights_sha256`, `processor_digest`

These are runtime provenance requirements.

For V2 candidates they must remain unresolved until future acquisition is explicitly authorized and the exact local bundle is frozen.

A runtime profile containing `NOT_OBSERVED`, empty values, or mutable branch labels such as `main` must fail closed.

### `processor_asset_names`

Explicit list of processor/tokenizer/config assets whose exact bytes participate in identity.

The list must be derived from the acquired frozen bundle; do not assume the V1 `PROCESSOR_ASSETS` tuple is correct for SigLIP2.

### `image_preprocessing_digest`

Digest of the exact image preprocessing definition used to produce embeddings.

The current V1 implementation hashes `preprocessor_config.json`; future design should preserve equivalent attribution.

### `text_preprocessing_contract`

Must represent the complete behavior relevant to embeddings, not only a partial shorthand.

For SigLIP2 the official Transformers contract includes lowercasing plus fixed max-length padding/truncation behavior. The exact serialized representation should be deterministic and covered by identity tests.

### `image_size`, `patch_size`, `embedding_dim`

Representation geometry.

Expected candidate values:

| Profile | Image size | Patch | Embedding width |
|---|---:|---:|---:|
| V1 Base | 224 | 16 | 768 |
| V2 Base | 224 | 16 | 768 expected; verify frozen checkpoint | 
| V2 So400m | 384 | 14 | 1152 |

`embedding_dim` must be validated against the loaded checkpoint/output before a profile becomes runtime-eligible.

### `dtype` and `normalization`

Current VIP index contract is `float32` + L2 normalization.

ADR-0002 does not require alternate dtype/normalization modes. Preserve the current values unless post-completion evidence justifies a deliberate change.

### `loader_kind`

Small closed enum identifying the validated runtime path, for example a V1 SigLIP loader versus a SigLIP2 AutoModel/AutoProcessor-compatible loader.

It is not a plugin registry and must not accept arbitrary import strings.

## Required Derived Values

The future implementation should derive rather than independently hard-code:

### Vector row width

```text
row_width_bytes = embedding_dim * bytes_per_element(dtype)
```

For the current `float32` contract:

- 768-D → 3072 bytes;
- 1152-D → 4608 bytes.

### Semantic-space identity

The existing semantic-space concept should remain authoritative for vector compatibility.

At minimum it must continue to bind:

- model identity;
- revision;
- weights digest;
- processor digest;
- image preprocessing digest;
- text preprocessing contract;
- embedding dimension;
- dtype;
- normalization.

Two profiles with the same vector width remain incompatible if any semantic-space identity field differs.

## Loader Boundary

Preferred future shape:

```text
validated profile + canonical local model root
        |
        v
fail-closed local identity validation
        |
        v
loader selected from closed known profile family
        |
        v
session(model, processor, device, embedding_dim)
```

Required behavior:

- local path must be explicit;
- weights/revision/processor bytes validated before runtime use;
- remote fallback prohibited;
- `trust_remote_code=False` unless a future separately approved design explicitly changes that;
- requested MPS must not silently fall back to CPU;
- session output width must equal profile width;
- post-open identity revalidation remains fail-closed.

## Historical Gate-0 Boundary

The current `src/gate0/adapters/siglip_local.py` is historical V1 evidence.

The future migration should not assume that editing it in place is the correct design.

Preferred decision at V1 completion:

1. inspect current architecture;
2. determine whether a successor SigLIP2 adapter belongs in a new representation boundary;
3. preserve V1 adapter semantics if doing so improves reproducibility;
4. share only genuinely generic local-model validation utilities.

## CLI / Runtime Construction

Current `src/vip_fvs/cli.py` constructs `SemanticSpace` directly from V1 globals in multiple paths.

Future design should have one representation-construction function/seam that:

1. accepts a validated profile;
2. verifies the local bundle;
3. creates the embedding session;
4. constructs the exact `SemanticSpace`;
5. returns the already-checked runtime used by indexing/query.

Avoid duplicating semantic-space construction across commands.

## Storage and Search

Storage and search should consume the semantic-space/profile geometry.

Do not create:

- one storage implementation for Base;
- a second storage implementation for So400m.

The future genericity required by ADR-0002 is only:

`dimension-aware float32 vector storage/query for 768 and 1152 dimensions`.

Anything broader is YAGNI.

## Synthetic Test Support

Fake/synthetic vector helpers should accept an explicit dimension or a profile-derived dimension.

They should support at least:

- 768-D;
- 1152-D.

Synthetic tests do not need real model assets and do not prove model quality.

## Non-Goals

This design does not create:

- arbitrary provider support;
- cloud model routing;
- model auto-download;
- dynamic model marketplace/plugins;
- arbitrary dtype support;
- automatic index migration;
- cross-model vector conversion;
- mixed semantic-space search;
- automatic benchmark winner selection.

## Post-Completion Design Gate

Before implementation, this inferred design must be compared against the completed V1 repository.

If final V1 already introduces an equivalent clean representation boundary, reuse it rather than layering another abstraction on top.

## 2026-10-11 Controlled Task 0 Source Reconciliation

Compared against preserved V1 `3586eeaa904fc5a2e6a2745078611886f482f3de` and current canonical main `748818e867ce08ccc2367bad21df7d83eaf51d70`. No closed `ModelProfile` exists in the current VIP source; the existing `SemanticSpace` remains the validated semantic identity, and `CheckedLocalSemanticRuntime` continues to accept explicit image/text callables plus that space. The CLI still constructs its real V1 semantic space from shared 768-wide constants. Writer/recovery is still 768-fixed while query reading consumes the space dimension. These findings match the already approved profile seam and width-aware writer requirement; they do not establish a duplicate abstraction or justify changing this design. The plan was subsequently accepted for planning only: exact reviewed blob `78127a9199a912531d5b2240eed66e93814d83f3`, owner decision on PR #69, merge `7f4a5ce1baf7de2aa580f1043502458336bf57fe`. Implementation remains unauthorized.
