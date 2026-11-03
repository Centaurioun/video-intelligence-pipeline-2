# Model Contracts — V1 Base, V2 Base, and V2 So400m

**Information state:** `VERIFIED_CURRENT` for repository V1 facts; `OFFICIAL_EXTERNAL` for SigLIP2 public facts; `REVERIFY_AT_V1_COMPLETION` for migration use; `NOT_AUTHORIZED_FOR_EXECUTION`  
**Captured:** 2026-10-05

## Purpose

This document records the human-readable representation contracts for the three mandatory ADR-0002 benchmark candidates.

It deliberately separates:

- project-local V1 facts already measured or frozen in repository evidence;
- official external facts about future SigLIP2 targets;
- values that cannot be frozen until future model acquisition is separately authorized.

The machine-readable companion is `05_model-contracts.yaml`.

## Contract Summary

| Field | VIP V1 Base | VIP V2 Base | VIP V2 So400m |
|---|---|---|---|
| Model ID | `google/siglip-base-patch16-224` | `google/siglip2-base-patch16-224` | `google/siglip2-so400m-patch14-384` |
| Family | SigLIP | SigLIP2 FixRes | SigLIP2 FixRes |
| Image size | 224 × 224 | 224 × 224 | 384 × 384 |
| Patch size | 16 | 16 | 14 |
| Embedding/hidden width used for retrieval | 768 in current VIP contract | 768 expected from official Base configuration/defaults; verify after acquisition | 1152 in official checkpoint config |
| Current VIP dtype | `float32` | future VIP choice not yet frozen; migration should preserve existing dtype unless deliberately changed | future VIP choice not yet frozen; migration should preserve existing dtype unless deliberately changed |
| Current VIP normalization | L2 | intended to remain L2 unless later design changes it | intended to remain L2 unless later design changes it |
| Text preprocessing | current VIP contract: `padding=max_length` | official SigLIP2 preprocessing lowercases and uses fixed padding/truncation with `max_length=64` | same SigLIP2 preprocessing family |
| Official HF loading examples | not the project runtime authority | `AutoModel` + `AutoProcessor` | `AutoModel` + `AutoProcessor` |
| Frozen future revision | current V1 revision already frozen | `NOT_OBSERVED` / not yet acquired | `NOT_OBSERVED` / not yet acquired |
| Frozen future weights digest | current V1 digest already frozen | `NOT_OBSERVED` / not yet acquired | `NOT_OBSERVED` / not yet acquired |
| Local VIP runtime evidence | measured for current V1 pilot | `NOT_OBSERVED` | `NOT_OBSERVED` |
| Project-specific comparative quality | baseline only; not a three-way result | `NOT_OBSERVED` | `NOT_OBSERVED` |

## VIP V1 Base Contract

### Repository-frozen identity

Model:

`google/siglip-base-patch16-224`

Current project evidence records:

- revision: `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`;
- weights SHA-256: `2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8`;
- processor digest: `4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980`.

The current persistent-local-index contract defines:

- embedding dimension: 768;
- dtype: `float32`;
- normalization: `l2`;
- text preprocessing contract: `padding=max_length`.

The current Gate-0 adapter uses local-only `SiglipModel` / `SiglipProcessor` loading and verifies the weights digest.

### Local evidence status

V1 has measured local MPS pilot evidence in the repository. That evidence is bounded to the authorized pilot and does not establish full-archive or Gate-1 superiority.

## VIP V2 Base Target Contract

Model:

`google/siglip2-base-patch16-224`

### Official external facts

The official Hugging Face model repository identifies this as a SigLIP2 checkpoint and provides Transformers usage through `AutoModel`.

The official checkpoint preprocessing config records:

- image size 224 × 224;
- normalization enabled;
- resize enabled;
- image mean `[0.5, 0.5, 0.5]`;
- image std `[0.5, 0.5, 0.5]`.

The official Transformers SigLIP2 documentation describes FixRes checkpoints as fixed-resolution variants that are backwards compatible with SigLIP at the model-family/API level.

For SigLIP2 text inputs, the official Transformers documentation states that the processor defaults include:

- lowercasing;
- `padding="max_length"`;
- `max_length=64`;
- `truncation=True`.

The current public checkpoint uses a compact `config.json` that omits inherited Base geometry. Official Transformers SigLIP2 configuration documentation gives the Base hidden-size default as 768; the official model name/preprocessor establishes the 224 fixed input, and an official Hugging Face ONNX export config expands the Base geometry as hidden/projection width 768, image size 224, patch size 16. Those are useful external cross-checks, but the future local acquisition step must still inspect the exact frozen checkpoint/runtime before VIP freezes the V2 Base profile.

### Unresolved until future acquisition

The following remain intentionally unresolved:

- immutable checkpoint revision selected by the project;
- local weights SHA-256;
- processor digest;
- image-preprocessing digest;
- exact local model-root asset inventory;
- actual local MPS/CPU behavior;
- actual local indexing speed;
- actual local memory burden;
- project-specific retrieval quality.

Do not copy V1 revision/digest values into V2.

## VIP V2 So400m Target Contract

Model:

`google/siglip2-so400m-patch14-384`

### Official external facts

The official checkpoint `config.json` records:

- text hidden size: 1152;
- text intermediate size: 4304;
- text attention heads: 16;
- text hidden layers: 27;
- text projection size: 1152;
- text vocabulary size: 256000;
- vision hidden size: 1152;
- vision image size: 384;
- vision intermediate size: 4304;
- vision attention heads: 16;
- vision hidden layers: 27;
- vision patch size: 14.

The official Transformers SigLIP2 documentation uses `AutoModel` and `AutoProcessor` for SigLIP2 retrieval-style embedding examples and applies the same SigLIP2 text preprocessing requirements described above.

The official model repository currently exposes a safetensors checkpoint and an Apache-2.0 license. File sizes and repository-head revisions are operational observations, not future VIP frozen identities.

### Unresolved until future acquisition

The following remain intentionally unresolved:

- immutable checkpoint revision selected by the project;
- local weights SHA-256;
- processor digest;
- image-preprocessing digest;
- exact local MPS/CPU behavior;
- actual local throughput;
- actual peak memory;
- actual project-specific quality advantage over V2 Base.

## Semantic-Space Rule

These are three distinct semantic spaces.

Even when two models use the same vector width, their embeddings are not interchangeable.

Therefore:

- V1 Base vectors must not be loaded into a V2 Base generation;
- V2 Base vectors must not be loaded into a V2 So400m generation;
- different model revisions/processors/preprocessing contracts must produce distinct semantic-space identities;
- raw cosine values from different spaces must not be treated as directly comparable quality scores.

Comparison is performed through shared benchmark outcomes, not by equating vector coordinates or raw scores.

## What “Backwards Compatible” Does Not Mean

Official SigLIP2 documentation describes FixRes as backwards compatible with SigLIP.

For this project, that must **not** be interpreted as:

- permission to reuse SigLIP1 embeddings;
- proof that the current `SiglipModel` / `SiglipProcessor` loader is the correct future SigLIP2 loader;
- proof that current V1 text preprocessing is sufficient for SigLIP2;
- proof that current processor-asset hashing covers SigLIP2 assets;
- proof that local MPS behavior is unchanged;
- proof of equal retrieval quality.

Those are migration/test questions.

## Primary External Sources Captured for This Contract

Official Hugging Face model repository:

`https://huggingface.co/google/siglip2-base-patch16-224`

Official SigLIP2 Base preprocessing config:

`https://huggingface.co/google/siglip2-base-patch16-224/blob/main/preprocessor_config.json`

Auxiliary official SigLIP2 Base expanded export config (cross-check only; not runtime authority):

`https://huggingface.co/google/siglip2-base-patch16-224/blob/5ffaac51d5e2f3367f7dab0cad4be4cb07c0caa2/onnx/config.json`

Official SigLIP2 So400m checkpoint config:

`https://huggingface.co/google/siglip2-so400m-patch14-384/blob/main/config.json`

Official Transformers SigLIP2 documentation:

`https://huggingface.co/docs/transformers/model_doc/siglip2`

SigLIP2 paper:

`https://arxiv.org/abs/2502.14786`

`20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md` and `21_source-receipts.yaml` record assertion-level source receipts and retrieval metadata, including the distinction between mutable upstream `main` observations and future frozen VIP runtime identity.

## Paper-Level Motivation, Not Project Proof

The SigLIP2 paper reports improvements over SigLIP counterparts across model scales for core capabilities including image-text retrieval and also describes stronger multilingual understanding.

This is sufficient motivation to benchmark SigLIP2 locally.

It is not evidence that V2 Base or V2 So400m is superior for the Video Intelligence Pipeline archive.

That remains `NOT_OBSERVED` until the planned frozen project benchmark is executed.
