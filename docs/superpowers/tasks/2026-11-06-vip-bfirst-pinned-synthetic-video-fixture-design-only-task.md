# VIP B-first — Pinned synthetic video fixture readiness: design-only task

**Date:** 2026-11-06  
**Status:** DESIGN/RESEARCH ONLY — NO BINARY GENERATION/COMMIT, NO CODE/CLI CHANGE, NO MAIN MERGE  
**Project:** Video Intelligence Pipeline — CORE-02  
**Scope:** Complete the approved B-first *architectural* preparation for a tiny, immutable, auditable video fixture and strict fixture-ID admission route, under local-first synthetic-only restrictions. A new binary asset, FFmpeg invocation, source change, CI modification and runtime operation each require a separately versioned and reviewed exact implementation packet.

## Immutable evidence anchor

- Canonical `Centaurioun/video-intelligence-pipeline` source candidate: `cac74495d80d9eaa144a12e9aa67eba78ba2f062`, tree `1e851b89273e7ae9a580643b8b704a2d5945c099`.
- Canonical protected main: `3bfcc2ba221b36df6773e630b44479ec961d630a`.
- LAB protected main: `5eab58ea2a5424424cb95f2690654b91395425df`.
- Prior owner-adopted B-first design and constraints: `docs/decisions/2026-11-06_CORE02_BFIRST_TRUSTED_FIXTURE_MANIFEST_OWNER_ADOPTION.md`, LAB `decision/vip-core02-bfirst-trusted-fixture-manifest-20261106@8de8664c8ce8501f86d484b63389f8d1a1c95fec`.
- Latest independent audit: `docs/reviews/2026-11-06-vip-bfirst-occurrence-successor-independent-source-ci-reconciliation.md`, same branch as this task.
- Full recursive Canonical source tree (2283 entries, not truncated) showed zero checked-in common-format video/audio media. Existing `tests/vip_fvs/fixtures/` is JSON timing recipes only. Recheck before assuming still true.

## Mission

Design **one** smallest acceptable fixed, reviewable generated synthetic VIDEO artifact for trustworthy developer-regression tests (not for real production source approval). Select how to create and freeze it, not merely how to claim `synthetic` in a sidecar. Separate *reviewable fixture authenticity under an explicitly limited local trust model* from *tamper-proof proof of synthetic origin*, which is impossible if the same untrusted actor controls all local trust roots.

**Do not generate or download a video in this task.** Use current source code/docs only and propose an exact future task packet, subject to owner scope and independent review.

## Evidence discovery

Read exact Canonical:
- `AGENTS.md`, `docs/INDEX.md`, four `docs/project/` handoff files, current source admission/authorization contracts, Native Codex Thread Operations Runbook, appropriate current portfolio resource policy;
- `src/vip_fvs/trusted_fixture_manifest.py` at successor SHA (exact trusted policy vs observed file identity meanings);
- `src/vip_fvs/core_analysis.py`, `query_analysis_authorization.py`, `core_generation_evidence.py`, `core_report.py`, `cli.py`, source snapshot, bounded admission and snapshot/FFprobe paths;
- `tests/gate0/media/generated_media.py`, `tests/gate0/fixtures/generated-media/build_media_corpus.py`, `src/gate3/fixturegen.py`, `tests/vip_fvs/integration/test_core_analyze_local_cli.py`, `tests/vip_fvs/fixtures/materialize.py`.
- Existing test fixture binary rules, `.gitignore`, Git LFS policy if any, GitHub CI workflows and review/commit signing requirements. Do not infer tested codec support from a filename.

## Required design decisions for Owner review

1. **Fixture artifact form:** compare a *tiny checked-in Git blob* of a one-time generated/independently inspected decodable MP4 to a reviewed immutable CI artifact. Describe exact size, repo licensing/storage and binary review limitations; an unreviewed moving release URL or same-invocation manifest self-hash is not an immutable source authority.
2. **One initial case only:** choose simplest small video that exercises an actual supported image source query pipeline with deterministic fake embeddings, measured video stream index/PTS/rational timebase. State the actual feature need; defer VFR/audio-first/B-frame stress fixtures until separate named tests. A proposed 64×64 color/frame clip is a suggestion, NOT existing validated bytes.
3. **Generator custody:** identify a trusted owner/operator, exact generator script/commit, FFmpeg binary executable identity/version, container/environment and command args, generated artifact hash/byte count, creation receipt and independent raw-byte review. Distinguish `MEASURED` executable/media hashes from asserted purpose or visually observed content.
4. **Authorization order:** strict `fixture_id` must be selected against independently pinned reviewed Git/CI policy identity **before any video byte read or probing/indexing**; the subsequent bounded descriptor read proves exact authorized bytes. Report current worktree file identity/occurrence separately. No grant self-issuance and no arbitrary `--source` fallback for strict path. Existing CLI lower-assurance developer workflow remains separate until owner-approved migration.
5. **Report contract:** retain exact absolute stream index and source-native integer PTS/timebase, `MATCHED` nonbinding semantic POINT and `MEASURED` timing; no fabricated intervals or VFR FPS arithmetic. Only fake deterministic embeddings; no genuine model or protected archive.
6. **Testing/adversary model:** propose RED/GREEN tests for unauthorized pre-read, SHA/size mismatch, wrong fixture or policy revision, same bytes under copied occurrence, unlinked Git artifact, symlink/hardlink, source replacement, corrupted/non-decodable MP4, multiple ranked matches, no-clobber publication, strict-vs-legacy mode bypass and source snapshot/revalidation.
7. **Review stages:** distinguish reviewed fixture generation/registration (frozen bytes), subsequent strict verifier/CLI integration, and separate independent reviewer/CI coverage. No mixed ownership between fixture binary issuance and code for consuming that binary unless exact reviewer authority is defined.
8. **Fallback when scope is not proven:** `BLOCKED_NO_PINNED_VIDEO_FIXTURE`, `BLOCKED_TRUST_ANCHOR`, `NOT_OBSERVED` instead of claiming release-ready E2E.

## Required proposal artifact

Write one proposed design document only under **LAB** `docs/superpowers/specs/` on a **new isolated documentation-only branch** from current verified LAB main. Include full alternatives/rejection ledger, separate owner decisions for creating/adding **tiny synthetic media bytes**, expanded source/test/CI path ownership, allowed FFmpeg tool/fixture-generation execution, and a minimal subsequent TDD implementation plan outline. Do not change existing historical design/decision/audit files.

Seek independent architecture/design critique when available and preserve rejected alternatives. The document is a **proposal**; the controller must not convert it into a code-implementation instruction without an exact bounded Owner decision/review. The previous general approval to progress through synthetic planning is not authorization for an unknown new binary/source write or protected execution.

## Terminal disposition

`BFIRST_PINNED_VIDEO_FIXTURE_DESIGN_PROPOSED — BOUNDED_SOURCE_EXECUTION_PENDING`, or a specific evidenced blocker.

Keep separate unresolved states:
- `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`;
- `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.

No protected/archive media, real model/provider, downloaded model, production promotion, Gate progress, destructive Git, original main edits, branch rewrite, PR or merge.
