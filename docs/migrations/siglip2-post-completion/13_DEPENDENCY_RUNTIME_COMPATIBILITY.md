# Dependency and Runtime Compatibility Preparation

**Information state:** `VERIFIED_CURRENT` + `OFFICIAL_EXTERNAL` + `SNAPSHOT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Repository snapshot:** `main@34106df55fc07a18fd8594f379cd143710ad0127`  
**External-source check date:** 2026-10-05

## Purpose

Record what is known, what is not locked, and what must be frozen before future SigLIP2 execution.

This document deliberately does not choose future package versions now. Doing so before V1 completion would create stale dependency work.

## Current Repository State

### Root packaging

At this snapshot, no root `pyproject.toml` was found.

### `requirements/gate0.lock`

Current content contains only:

`pytest==8.3.3`

Therefore the current repository does **not** provide a complete exact lock for the semantic-model runtime stack such as:

- Transformers;
- PyTorch;
- NumPy;
- Pillow;
- tokenizer/runtime dependencies.

This is a migration-readiness gap to close later, not evidence that the current local pilot lacked those packages.

### Historical Gate-0 Python control

Historical Gate-0 configuration records Python `3.11.9`.

That historical control must not automatically become the future SigLIP2 runtime choice. The completed V1 runtime actually used at activation should be measured/frozen separately.

### Current adapter API statement

`src/gate0/adapters/siglip_local.py` currently describes itself as targeting a “frozen Transformers 5.17 API.”

That code-level statement is a V1 snapshot, not an exact dependency lock in the repository.

## Official SigLIP2 Compatibility Evidence

### Hugging Face model repository

Current official SigLIP2 model pages expose standard Transformers loading examples based on `AutoModel` and processor assets in the repository.

For `google/siglip2-base-patch16-224`, the current upstream repository includes:

- `config.json`;
- `model.safetensors`;
- `preprocessor_config.json`;
- `special_tokens_map.json`;
- `tokenizer.json`;
- `tokenizer.model`;
- `tokenizer_config.json`.

This directly demonstrates that the current V1 fixed processor-asset list containing `spiece.model` must not be copied blindly to V2.

Official source:

`https://huggingface.co/google/siglip2-base-patch16-224/tree/main`

### Checkpoint config version metadata

The current V2 Base upstream `config.json` records:

`"transformers_version": "4.49.0.dev0"`

Treat this as serialization/config provenance, **not** as a statement that VIP must run exactly Transformers 4.49.0.dev0 or that it is the minimum supported version.

Official source:

`https://huggingface.co/google/siglip2-base-patch16-224/blob/main/config.json`

### PyTorch MPS

Current PyTorch documentation continues to expose the `mps` device and recommends explicitly checking whether MPS is built and available before use.

This aligns with the existing VIP fail-closed device discipline.

Official source:

`https://docs.pytorch.org/docs/stable/notes/mps.html`

### MPS fallback environment

Current PyTorch MPS documentation states that `PYTORCH_ENABLE_MPS_FALLBACK=1` enables CPU fallback for unsupported MPS operations.

Therefore a future “no silent fallback” verification must inspect the process environment as well as application control flow. Benchmark/run receipts should record this variable and other relevant MPS environment settings; an unexpected enabled fallback is a reproducibility finding, not an invisible implementation detail.

Official source:

`https://docs.pytorch.org/docs/stable/mps_environment_variables.html`

## Why We Should Not Pin Future Versions Now

The V1 project is still evolving.

Pinning a future migration environment today would create at least three avoidable risks:

1. the completed V1 runtime may differ;
2. Transformers/PyTorch support matrices may change before activation;
3. future exact SigLIP2 checkpoints may require or work best with a different validated combination.

The preparation objective is to define the **freeze procedure**, not prematurely choose the result.

## Required Runtime Freeze at Migration Activation

Before first V2 Base model execution, create an exact environment receipt containing at minimum:

- OS/macOS version/build;
- architecture;
- Python version and executable digest/path;
- Transformers exact version;
- PyTorch exact version;
- NumPy exact version;
- Pillow exact version;
- tokenizer-related package versions actually imported;
- any SentencePiece dependency if actually required by the selected processor path;
- FFmpeg/ffprobe identity where index generation uses them;
- MPS build/availability result;
- relevant MPS environment variables, including `PYTORCH_ENABLE_MPS_FALLBACK`;
- model ID;
- immutable model revision;
- model weights digest;
- processor/tokenizer asset inventory and digest;
- offline environment controls;
- code SHA.

Prefer a reproducible exact lock/receipt over prose-only version notes.

## Compatibility Probe Sequence

### Probe A — import/load compatibility

Using only the separately authorized frozen local model bundle:

- import the exact selected libraries;
- instantiate the intended AutoModel/AutoProcessor-compatible path locally;
- require `local_files_only=True`;
- disable remote-code trust;
- prove no network fallback is needed;
- verify processor/tokenizer assets resolve locally.

### Probe B — output contract

On bounded fixture inputs:

- text feature output exists;
- image feature output exists;
- output widths match profile expectation;
- outputs are finite;
- VIP normalization produces valid unit vectors;
- repeated deterministic fixture execution is characterized.

### Probe C — device behavior

For CPU and/or MPS targets actually selected:

- requested device is explicit;
- MPS unavailable → fail, not silent CPU fallback;
- model and tensor device movement is verified;
- any unsupported operation/fallback behavior is recorded rather than hidden.

### Probe D — persistence compatibility

With synthetic vectors first:

- profile-derived row width works;
- write/recovery/search use the same geometry;
- dtype remains exact;
- semantic-space mismatch fails closed.

## Version-Change Rule

Changing any of the following after a benchmark candidate is frozen should produce a new runtime identity/receipt and may require revalidation:

- Python minor version;
- Transformers version;
- PyTorch version;
- tokenizer implementation materially affecting preprocessing;
- model revision;
- model weights bytes;
- processor asset bytes;
- preprocessing contract;
- device class if performance results are compared.

Do not silently compare benchmark runs produced under different runtime identities.

## Future Dependency Artifact

The post-completion migration should create a concrete exact dependency artifact appropriate to the final project structure.

This preparation document does not mandate whether that artifact is:

- a requirements lock;
- a uv/Poetry lock;
- another reproducible environment manifest.

The requirement is reproducibility and attributable exact versions, not a specific package manager.

## Current Unknowns

As of this preparation snapshot:

- exact future Python version: `NOT_OBSERVED`;
- exact future Transformers version: `NOT_OBSERVED`;
- exact future PyTorch version: `NOT_OBSERVED`;
- exact future SigLIP2 Base runtime compatibility on the target Mac/MPS environment: `NOT_OBSERVED`;
- exact future So400m runtime compatibility/memory envelope: `NOT_OBSERVED`.

These are intentionally deferred to post-completion verification.

## 2026-10-11 Controlled Task 0 Environment Observation

Package metadata was read from the already-existing ``<repo>/.venv/bin/python`` environment without importing model libraries or opening any model assets. The interpreter resolves to Python **3.14.7** on Darwin **25.6.0 arm64**. Installed metadata observed: pytest **8.3.3**, NumPy **2.5.3**, Pillow **12.3.0**, and PyTorch **2.14.1**. Transformers, tokenizers, and SentencePiece are not installed in this test environment. FFmpeg and ffprobe resolve to `/opt/homebrew/bin/{ffmpeg,ffprobe}`, both **9.0.2**.

The Python/pytest/NumPy/Pillow values match the prior preflight record at `b296b5ca5a805d151412cf848fa397266fe23052`. The PyTorch presence/version is newly recorded package metadata only. This environment is the synthetic test environment; it is **not established as the frozen final V1 model runtime**. No package was installed, no model was loaded, and no MPS availability/inference probe was performed. Transformers/tokenizer/runtime compatibility, exact final V1 lock/receipt, model-local loader behavior and MPS/fallback state remain `NOT_OBSERVED` or `BLOCKED` as itemized in the Task 0 readiness matrix.

### Current-runtime receipt qualification

The separate SHA-bound receipt `docs/agent-runs/run-20261011-vip-v1-runtime-baseline-freeze/runtime-inventory.json` at `ce3f570016f3f13e9091fb6989f3a9d3ea783c7d` is the current runtime baseline for the prior verified local V1 run. Checklist F07 is exactly `PASS_CURRENT_RUNTIME_RECEIPT_ONLY`: the inventory supports current receipt evidence and matched recorded package versions, but it is not an installable lock, wheel hashes, or full historical environment reconstruction. The `.venv` observation above remains only the synthetic test environment and is not substituted for that runtime receipt.
