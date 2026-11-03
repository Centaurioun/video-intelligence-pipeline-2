# External Evidence and Primary-Source Pack

**Information state:** `OFFICIAL_EXTERNAL` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Captured:** 2026-10-05

## Purpose

Give future ChatGPT/Codex sessions a compact map of the primary sources behind the SigLIP2 preparation package.

These sources justify target contracts and future investigation.

They do not constitute local `MEASURED` project evidence.

Machine-readable receipts are in `21_source-receipts.yaml`.

## Source E01 — SigLIP2 Paper

**Title:** SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features  
**Primary source:** arXiv 2502.14786  
**URL:** `https://arxiv.org/abs/2502.14786`

Supports:

- SigLIP2 builds on the original SigLIP family;
- training recipe adds captioning-based pretraining, self-supervised losses and online data curation;
- authors report improvements over SigLIP counterparts across model scales in core capabilities including image-text retrieval;
- multilingual understanding and localization/dense capabilities are explicit design goals;
- released model scales include ViT-B and So400m.

Does **not** support:

- superiority on the VIP dance/performing-arts archive;
- local Mac/MPS speed;
- exact project memory usage;
- exact editing boundaries.

## Source E02 — Official Transformers SigLIP2 Documentation

**URL:** `https://huggingface.co/docs/transformers/model_doc/siglip2`

Supports:

- SigLIP2 is available through Transformers;
- retrieval/text-embedding examples use the model/processor API;
- default SigLIP2 text preprocessing includes lowercasing;
- fixed padding/truncation uses `padding="max_length"`, `max_length=64`, `truncation=True`;
- AutoProcessor handles the model's trained text preprocessing;
- FixRes and NaFlex are distinct variants;
- FixRes is documented as fixed-resolution and backwards compatible with SigLIP;
- current `Siglip2Config` documentation gives Base hidden-size default 768.

Migration implication:

The V1 shorthand text contract `padding=max_length` is not sufficient as a complete SigLIP2 preprocessing identity.

## Source E03 — SigLIP2 Base Official Model Repository

**Model:** `google/siglip2-base-patch16-224`  
**URL:** `https://huggingface.co/google/siglip2-base-patch16-224`  
**Files:** `https://huggingface.co/google/siglip2-base-patch16-224/tree/main`

Supports:

- official model identity;
- Apache-2.0 licensing shown on the model repository;
- Transformers/Safetensors distribution;
- fixed 224 Base candidate naming;
- current public repository includes model/config/preprocessor/tokenizer assets;
- current repository uses `tokenizer.model`, not the V1 preparation pack's historical `spiece.model` filename.

Operational caution:

The public `main` branch is not the future VIP frozen revision. At activation, choose an immutable revision and hash the local acquired bytes.

## Source E04 — SigLIP2 Base Config

**URL:** `https://huggingface.co/google/siglip2-base-patch16-224/blob/main/config.json`

Supports:

- model type remains `siglip`;
- text model type is `siglip_text_model`;
- text vocabulary size is 256000;
- vision model type is `siglip_vision_model`;
- config currently records `transformers_version: 4.49.0.dev0`.

Interpretation:

The compact config inherits Base defaults. The future project must inspect the exact frozen checkpoint/config rather than turn omitted default fields into unverified hard-coded assumptions.

## Source E05 — SigLIP2 So400m Official Model Repository

**Model:** `google/siglip2-so400m-patch14-384`  
**URL:** `https://huggingface.co/google/siglip2-so400m-patch14-384`

Supports:

- official model identity;
- current public repository exposes `model.safetensors`, config, preprocessor and tokenizer assets;
- official Transformers usage is provided.

Again, public `main` is not the future VIP frozen runtime identity.

## Source E06 — SigLIP2 So400m Config

**URL:** `https://huggingface.co/google/siglip2-so400m-patch14-384/blob/main/config.json`

Supports the target geometry captured in the preparation pack, including:

- image size 384;
- patch size 14;
- vision hidden size 1152;
- text hidden/projection size 1152;
- 27 text and vision layers;
- 16 attention heads;
- text vocabulary 256000.

These are external checkpoint facts, not local runtime measurements.

## Source E07 — PyTorch MPS Backend Documentation

**URL:** `https://docs.pytorch.org/docs/stable/notes/mps.html`

Supports:

- PyTorch exposes the `mps` device for Apple Metal;
- availability should be checked explicitly;
- modules/tensors can be moved to the MPS device.

This supports the project's explicit-device validation approach.

## Source E08 — PyTorch MPS Environment Variables

**URL:** `https://docs.pytorch.org/docs/stable/mps_environment_variables.html`

Supports:

- MPS runtime behavior can be affected by explicit environment variables;
- `PYTORCH_ENABLE_MPS_FALLBACK=1` enables CPU fallback for unsupported MPS operations.

Migration implication:

A benchmark runtime receipt should record relevant MPS environment settings. In particular, `PYTORCH_ENABLE_MPS_FALLBACK=1` would permit CPU fallback for unsupported operations; the VIP no-silent-fallback policy therefore must verify process environment as well as code.

## Source E09 — SigLIP2 Base Preprocessor Config

**URL:** `https://huggingface.co/google/siglip2-base-patch16-224/blob/main/preprocessor_config.json`

Supports:

- fixed image preprocessing size 224 × 224;
- normalization and rescaling are enabled;
- image mean/std are each `[0.5, 0.5, 0.5]`;
- the current public processor asset identifies `SiglipImageProcessor` / `SiglipProcessor`.

The upstream `main` file is mutable and must be re-fetched/frozen at migration activation.

## Source E10 — SigLIP2 Base Expanded Official Export Config

**URL:** `https://huggingface.co/google/siglip2-base-patch16-224/blob/5ffaac51d5e2f3367f7dab0cad4be4cb07c0caa2/onnx/config.json`

Supports an official Hugging Face export-side cross-check of Base geometry:

- hidden/projection width 768;
- image size 224;
- patch size 16;
- 12 layers / 12 attention heads.

This is **auxiliary external evidence**, not the future VIP runtime checkpoint identity. The actual frozen model bundle/runtime remains authoritative at acquisition time.

## Evidence Hierarchy for Migration

Use sources in this order for operational truth:

1. explicit current user authorization/decision;
2. current governing VIP repository specs/ADRs;
3. exact frozen local checkpoint bytes/config/runtime evidence;
4. official upstream model/config/docs;
5. paper-level general results;
6. third-party commentary/popularity.

For project-specific retrieval quality, the frozen VIP benchmark outranks public benchmark tables.

## Refresh Rule

Before migration implementation:

- re-fetch all sources;
- capture the immutable model revisions selected for the project;
- update changed assertions;
- preserve this historical capture through Git history;
- never silently treat changed upstream `main` as the same frozen model.

## 2026-10-11 — Append-only E01–E10 source refresh

The ten recorded official sources were re-fetched on 2026-10-11 at the exact URLs in 21_source-receipts.yaml. The current retrieval status, response-body SHA-256 values, observed revision identifiers, assertion-by-assertion comparison, same-site PyTorch documentation redirects, and migration implications are recorded in:

docs/agent-runs/run-20261011-vip-v2-task0-final-gap-reconciliation/source-refresh.json

E01–E06, E09 and E10 continue to support the prior general paper, model-family, geometry and preprocessing assertions. E07 and E08 stable documentation pages now resolve to the PyTorch 2.14 documentation set. Current Hugging Face main targets observed were 75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2 for SigLIP2 Base and e8e487298228002f3d8a82e0cd5c8ea9c567f57f for SO400M. The existing design's pinned SO400M revision remains untouched; the retrieved mutable main page does not freeze its runtime identity. No V2 Base revision was selected, and no design or checkpoint change is implied.

The public SigLIP2 documentation's class defaults are not a substitute for serialized checkpoint configuration. The refreshed Base and SO400M config pages report text vocab_size=256000; the documentation describes a 32000 Siglip2TextConfig default. Neither source establishes V1 tokenizer behavior or explains the recorded V1 warning. Public sources remain OFFICIAL_EXTERNAL evidence, not local MEASURED evidence.
