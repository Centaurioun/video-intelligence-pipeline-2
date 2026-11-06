# CORE-02 — Owner authorization for bounded synthetic-only implementation

**Date:** 2026-11-06  
**Status:** OWNER_APPROVED — BOUNDED IMPLEMENTATION ONLY; INTEGRATION NOT AUTHORIZED  
**Repository where this receipt lives:** LAB design branch `design/vip-core01-core02-selective-canonical-integration-20261106`. This receipt is not a modification of Canonical main and creates no Gate promotion.

## Explicit current Owner decision

The Repository Owner explicitly replied **"Onaylıyorum."** to the immediately preceding proposal to implement CORE-02 in a new isolated Canonical development branch **under synthetic/generated-fixture-only constraints**, using the independently examined CORE-01 successor as its starting dependency. This authorizes the implementation activities below, not main integration or any protected operation.

## Exact evidence anchors and starting scope

- **Canonical repository:** `Centaurioun/video-intelligence-pipeline`.
- **Immutable starting source dependency:** CORE-01 successor `261319d4ac7f3c2ac80b67a59baea13bba73bfed`, tree `e02cf8ef3869ccf11e865fe2fcc0abdaafe61ecc`.
- **Protected current Canonical main (must remain unchanged):** `3bfcc2ba221b36df6773e630b44479ec961d630a`, tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`.
- **LAB main reference:** `5eab58ea2a5424424cb95f2690654b91395425df`.
- **Approved architecture:** `docs/superpowers/specs/2026-11-06-vip-core01-core02-selective-canonical-integration-design.md` at LAB planning branch (original approved artifact; do not silently rewrite).
- **Implementation plan now authorized:** `docs/superpowers/plans/2026-11-06-vip-core02-single-video-report-canonical-adaptation.md` at the same LAB planning branch; Tasks 1–6 within its declared paths and acceptance scope.
- **CORE-01 predecessor:** `7c167486d66e076708fd490964f5e4d3c06aa20b`; **CORE-01 verified stream-provenance successor:** `261319d4ac7f3c2ac80b67a59baea13bba73bfed`. Its inherited semantic interval remains `BLOCKED_BY_CONTRACT`. Do not treat the existing `main` as carrying the successor code.

## Permitted work

1. Create a **fresh, clean, isolated Canonical development worktree and unique feature branch** **based exactly on `261319d4ac...`**, following Canonical `AGENTS.md`, current native Codex project/thread/worktree binding, exclusive writer/lease rules, and a verified preflight. Do not work in any existing dirty checkout.
2. Use tests-first (RED/GREEN), isolated independent review, and deterministic generated synthetic fixtures to implement only the approved CORE-02 product slice: one-source, one-text-query `analyze-local` operation; typed nonbinding semantic `POINT`; truthful source-native PTS/timebase provenance; Report V1 validation and exclusive/no-clobber publication; a fail-closed query-analysis authorization seam; source-scoped generation and sample-row evidence verification; CLI dispatch and focused integration tests.
3. Reuse existing Canonical source snapshot/probe/index/model-space and accepted bounded-admission primitives. Preserve CORE-01 source/stream fixes and existing Canonical commands; no broad database schema migration, no LAB Mega/batch/three-arm transplant, no duplicate engine or runtime.
4. Carry out synthetic-only Python 3.11/3.14 targeted tests, relevant Canonical regression suites, full-suite regression accounting against the **CORE-01 starting candidate** and (as needed for historical classification) the pinned original main, with proper PASS/FAIL/SKIP/XFAIL reporting. Prior reported seven Python 3.14 failures are not automatically treated as newly introduced CORE-02 failures; perform exact comparator checks for new failures.
5. Commit and **normally push (no force)** an isolated CORE-02 candidate branch to GitHub for independent verification, including applicable GitHub **synthetic** CI at the exact candidate SHA. No integration PR, main merge or Gate change.
6. Request a fresh independent feature-level review on the final candidate SHA and address only findings within the authorized task boundaries. Document any contract blocking prerequisite rather than fabricating access.

## Hard boundaries

- **CORE-02 synthetic development only**: Do not read/process protected/archive or other unapproved authentic media; no real model inference, model weights downloads/loads, provider calls, network/cloud inference/egress, production export, actual editing, render, QC or Gate promotion. GitHub reads/pushes/authorized synthetic CI for this repository task are allowed.
- The `REAL` query-analysis mode remains **fail-closed / BLOCKED** until an existing valid, exact query-only owner policy expression is actually verified and a further explicit owner decision authorizes execution. Do not turn on REAL mode as part of this task, even if the adapter can structurally parse permission records.
- The current CORE-01 legacy `+1s` `semantic_interval` is unresolved technical debt. **No modifications** to existing `review_bundle.py`, Gate-3 measured source interval contracts, or the prepare-real legacy interval in this task. New CORE-02 Report V1 uses `POINT` for unknown semantic window width and never infers exact edit boundaries.
- Maintain occurrence/revision/source SHA/selected absolute stream/timebase/space/index generation/query/report identity boundaries. If a field cannot be proven from the existing model, **refuse or mark NOT_OBSERVED**, never invent it. `NOT_OBSERVED` is a state, not an evidence class.
- Do not touch shared dirty worktrees, the existing CORE-01 worktrees, local main, either original remote main or either immutable DO_NOT_DELETE backup.
- Do not use hard reset, git clean, force push, history rewrite, worktree deletion or recovery-object pruning.
- Do not enlarge scope because a test fails or because a supposedly compatible LAB module assumes different schemas. Return `BLOCKED_BY_CONTRACT` or `PARTIAL` with exact file/line/test evidence for a required owner decision.

## Acceptance and handoff

- A new, peer-reviewed CORE-02 synthetic candidate on a clearly identified SHA/branch is the requested artifact, **not** a new verified Gate maturity or mainline deployment.
- The report must separately classify: `CORE02_SYNTHETIC_CANDIDATE_VERIFIED` (only if implementation, test evidence and independent review support it), `CORE02_SYNTHETIC_CANDIDATE_PARTIAL` (if blocked/unfinished), and continuing `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
- Any claim that the existing seven full-suite failures are pre-existing must be tied to the reported matched baseline evidence and/or newly rerun comparable tests; never claim a fully green full suite when failures remain.
- No PR or main merge, no production scope, and no automatic CORE-01 completion.

**Terminal authorization marker: CORE02_SYNTHETIC_OWNER_APPROVED — CODE_CANDIDATE_ONLY — NO_MAIN_MERGE.**
