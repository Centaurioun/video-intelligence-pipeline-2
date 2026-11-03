# 2026-10-08 canonical adoption — current-scope and evidence reconciliation

**Status:** canonical local-first *product candidate* adopted; separate terminal-control-plane publication into canonical `main` is NOT YET COMPLETE. Historical Git branches have NOT been deleted.

## Exact identity and authority

- Initial canonical product base: `main@1bdf57b423ae84034184b8c4d2c441616c78301f`.
- G02 frozen integrated product: `e956722a0fc2109eb4651ce728e919e691162511`, tree `2996b4cca1164ba7b145145dbfe0b908a1010f82`.
- [PR #57](https://github.com/Centaurioun/video-intelligence-pipeline/pull/57): protected merge commit `e752c2fc45b533a0c679a32459225d37165a7722`. Exact product candidate -> merged main has zero changed file paths; the new merge commit is later bookkeeping in lineage, not a new independently executed product test candidate.
- [PR #58](https://github.com/Centaurioun/video-intelligence-pipeline/pull/58): preservation inventory/plan merged via `f4e40c2cba18f85e6f283113e8d7d48c4205dff8`. **This is not Git-object preservation.**
- Terminal Portfolio control-plane: `controller/remaining-work/authoritative@a81104f47667a7f9ee1f47a86e1bfe711bfa2dd4`.
- Final Area-G handoff: `controller/area/G@988b8790cc45ad1c1093f0d1ebbae15ab0716f38`.
- Terminal accepted root vector: H3-A07, H3-B05, H3-C05, H3-D05, H3-E05, H3-F03; G01 Gen023 matrix digest `32506cc4bc08ec0c73678f7cf335359c4061760e9e44ec0d277fe56ccb7720e3`.
- G02: VERIFIED exact candidate/tree. G03: VERIFIED *for the authorized current local-first scope only*. No blocking Problems under terminal Portfolio.
- Exact source-authorization trust root remains `execution/execution-portfolio-20260924-v1/bootstrap@d766def9d22978328e8767ce7cc769956f41df15`; G02 verification records **zero unauthorized source paths** against that fetched admin identity. Do not retire or repurpose that authority ref without separate reviewed migration.

## What independent testing actually established

- At G03 time, **1,290 reported passing regressions**: VIP-FVS 594, Gate 0 477, Gate 1 120, Gate 2 99.
- Eight independent G03 read-only lanes: contract/provenance PASS; temporal-authority PASS with nonblocking C05 display-risk; source-auth PASS; local-only egress/model PASS within excluded scope; index/recovery PASS with modality limit; editorial/QC PASS with fresh real preview NOT_OBSERVED; Atlas integrity PASS; falsifier PASS with no blocking counterexample.
- G03 exact verification receipt on Area-G: `.orchestration/remaining-work/verification/H3-G03-20261008/generation-001/final-verification.json`.
- Portfolio consumption receipt: `.orchestration/remaining-work/runs/portfolio-controller/area-g-g03-gen001-final-consumption-20261008.json` on terminal Portfolio authority.
- The *full workspace verifier* had inherited checkout/reference-pack/prototype environment failures. Source-auth was separately verified under the correct admin ref; do not report the entire workspace verifier as PASS.
- PR #57 had no new GitHub-hosted CI/status execution observed at adoption; historical per-candidate test receipts are evidence, not PR-host CI.

## Current-scope limitations — DO NOT UPGRADE EVIDENCE

- C05 rounded `timestamp_human` is **display-only/nonbinding**. Semantic or provider timestamps are retrieval candidates, never exact edit boundaries; source-native integer PTS/timebase is required for edit accuracy, including VFR.
- Protected/archive execution, provider/cloud calls, model/checkpoint download, production render/export, Gate promotion, real-media preview/audio/visual QC, broader modality benchmark, and real Gate-2 M4 scale reliability remain NOT_AUTHORIZED and/or NOT_OBSERVED as appropriate.
- Archive/source media remain immutable. Technical candidate refinement is not a human editorial decision.

## IMPORTANT: control-plane publication lag on main

The *terminal Portfolio* Atlas has all 33 H3 task nodes VERIFIED, covering weighted H3 100/100 within the authorized current local-first scope. This is **not** a universal production-readiness measure.

As of product merge and this reconciliation, `main` still contains an older `.orchestration/remaining-work/atlas/atlas.json` with 18 of 33 H3 nodes VERIFIED and older `progress.json` showing build=63/100, verified=60/100. The terminal Portfolio branch itself contains `progress.json` showing 99/97, which is also stale relative to its terminal Atlas.

**Never change progress counters to 100 while leaving an inconsistent underlying Atlas on main.** Control-plane reconciliation requires its own reviewed exact-content/contract-authority migration including dependent prompt/evidence references, or a documented new canonical authority pointer protocol; validate the candidate with `scripts/verify-remaining-work-atlas.py` and exact verification before any promotion of H3 roll-ups or terminal state.

Do not indiscriminately merge the divergent Portfolio admin/controller branches into main. Old historical handoffs below the current override are preserved as histories, not current dispatch instructions.

## Decision-history and branch-retirement protection

- Canonical rejected-alternative record: `docs/superpowers/specs/2026-09-23-execution-portfolio-rejected-alternatives.md`. Preserve its rationales and reconsideration triggers.
- Historical preservation tag: `archive/history/branch-preservation-v1`, former recovery ledger `.orchestration/maintenance/branch-hygiene-cleanup-v1/preservation-recovery.json`. Both predate most current execution branches.
- New canonical audit: `docs/audits/2026-10-08-branch-head-inventory.json` (non-atomic remote snapshot, 674 listed names and 664 distinct HEAD SHAs) and `docs/audits/2026-10-08-main-adoption-and-branch-preservation-plan.md`.
- Open independent draft [PR #56](https://github.com/Centaurioun/video-intelligence-pipeline/pull/56) preserves proposed event-driven protocol; do not silently adopt it by branch cleanup.
- Newer design/handoff/experiment branches can contain uniquely authored decisions not present in main. First index acceptance/rejection rationale, source SHA, and reconsideration trigger; then build and **restore-test** a permanent object-reachable archive covering every unique head.
- Treat control-plane, source-authority trust-root, open-PR heads, and dirty/local-only worktrees as **RETENTION_REQUIRED** unless independently discharged.
- **No branch deletions**, tag/branch destruction, hard resets, git clean, force pushes, reflog/object pruning, or worktree removal until owner-reviewed recovery manifests demonstrate object reachability, recovery, and per-ref freshness.

## Next authorized non-destructive workflow

1. Independent review of this handoff and its SHA-bound references.
2. Reconcile terminal Atlas/progress on a separately isolated control-plane branch and independently verify against exact records before proposing to merge.
3. Preserve decisions and unique heads in immutable, recoverable Git objects; test fresh recovery and local worktree exceptions.
4. Only then propose a bounded deletion manifest and separately review it. Retain administration trust refs and open PR dependencies.
