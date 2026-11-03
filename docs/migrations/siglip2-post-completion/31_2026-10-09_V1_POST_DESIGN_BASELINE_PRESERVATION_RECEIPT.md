# Preserved V1 Post-Design Baseline — GitHub Ref Receipt

**Date:** 2026-10-09  
**Status:** **VERIFIED_GIT_REF_ONLY**. Environment / exact archived runtime and re-executed V1 tests: **PENDING**.  
**Authority:** owner-approved preservation operation, after two repository integration reports were merged, before the planned V2 migration.

## Immutable source facts

| Field | Verified value |
|---|---|
| Product repository | Centaurioun/video-intelligence-pipeline |
| Protected main SHA before preservation | `3586eeaa904fc5a2e6a2745078611886f482f3de` |
| Prior owner-approved design publication | PR #64, merge `3586eeaa904fc5a2e6a2745078611886f482f3de` |
| Separately retained experiment handoff | Centaurioun/vip-siglip2-so400m-browser-spike PR #2, main merge `e0b018cce64b8acd4a766f99097364d9c8af026d` |
| New preserved branch | `preservation/vip-v1-post-v2-design-20261009` |
| Ref target | `3586eeaa904fc5a2e6a2745078611886f482f3de` |
| Remote verification | GET git/ref/heads/preservation/... returned this exact commit |
| Branch vs source commit | GitHub compare: `identical`, ahead 0, behind 0, changed files 0 |
| Canonical main mutation in preservation operation | **None** |
| Ref deletion/movement | **Not authorized**; created once at exact SHA, do not update |

[Preservation branch](https://github.com/Centaurioun/video-intelligence-pipeline/tree/preservation/vip-v1-post-v2-design-20261009) — the Git commit tree itself is preserved, not a second mutable application repository.

## What this does and does not preserve

Preserves committed V1 source, tests, specifications, current history reachability and two-repository report links as they existed at the pinned Git commit. It does **NOT** copy a private local virtual environment, checkpoint bytes, V1 vector index, video archive, uncommitted worktrees, or ephemeral runtime state. Do not label this operation a fully reproduced release or tested rollback; those require separate evidence.

The product adoption precedent is [PR #57](https://github.com/Centaurioun/video-intelligence-pipeline/pull/57), exact product candidate `e956722a0fc2109eb4651ce728e919e691162511` adopted in merge `e752c2fc45b533a0c679a32459225d37165a7722`. The living handoff attributes G02/G03 terminal completion for the authorized local-first engineering scope. Exact current V1 local test rerun in this session: **NOT_OBSERVED**.

## Historical V1 model and pilot identity — provenance, not fresh file verification

The historical [V1 baseline snapshot](03_V1_BASELINE_SNAPSHOT.md) records:

- Model `google/siglip-base-patch16-224`; upstream revision `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`.
- Model checkpoint SHA-256 `2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8`.
- Processor digest `4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980`.
- Preserved 2026-09-21 pilot semantic space ID `3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a`.
- Preserved pilot generation ID `648dd7391ec2a92e51aacdd20d11c4bd5c1a5c3ce88755066c819e0faa852508`.
- Historical V1 width 768; float32 L2; padding=max_length; sampled 4.5 seconds.

These fields still require a post-completion checked receipt confirming their applicability to the frozen product state; do not silently infer the local model bundle or benchmark corpus remain present.

## Hard next gate

Run [post-completion refresh protocol](19_POST_COMPLETION_REFRESH_PROTOCOL.md) against the preservation SHA, emit the concrete governed **30_post-completion-refresh-receipt-template.yaml** instance, map T001–T026 against final test paths, independently run relevant V1 regressions on the intended execution Mac, freeze dependency and model artifact identity. Missing checks remain BLOCKED, not fabricated PASS.

Superpowers [VIP V2 design](../../superpowers/specs/2026-10-09-vip-v2-siglip2-integration-design.md) has owner-approved direction and the owner's subsequent broad acknowledgement for progressing to planning. The separate [implementation plan](../../superpowers/plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md) is a proposed execution plan subject to final plan review and explicit implementation method/authority. No source-code, model, protected-media, benchmark or Gate work was authorized or performed by this receipt.

## Recoverability / rollback

To inspect the V1 code tree, clone/fetch this repository in a separately approved execution workspace and check out the exact `3586eeaa...` SHA or read the protected preserved ref without altering shared main. Do **not** hard reset active worktrees, move the preservation branch, reuse V2 vector indexes as V1, or assume model artifacts exist because Git history does. Validate model/runtime/index identities before any actual V1 rerun.
