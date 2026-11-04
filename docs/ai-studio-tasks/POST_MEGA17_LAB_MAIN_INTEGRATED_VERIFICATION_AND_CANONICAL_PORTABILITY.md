# POST-MEGA-17 — Independent Integrated Regression and Selective Canonical Portability Audit

Task ID: LAB-P0P1-POST-MEGA17-20261104
Version: v1.0.0
Date: 2026-11-04
Executor: Codex (local Git, real pytest, source read, isolated worktree)
LAB: https://github.com/Centaurioun/video-intelligence-pipeline-2
Canonical reference: https://github.com/Centaurioun/video-intelligence-pipeline (STRICTLY READ ONLY)
Authority: owner authorized the LAB P0 PR merges, post-merge regression and creation of this follow-on task. This document DOES NOT authorize canonical source writes, real archive/media access, model acquisition, provider calls, Gate promotion, or actual production exports.

## 1. Verified starting milestone; do not replay

On 2026-11-04:
- LAB PR #1 merged at main commit 9dedbe965e75d8214534ef51e939cc12f8892779 (MEGA-15/16, source restoration and filesystem safety).
- LAB PR #2 merged at main commit f20f4a7efca1e9d93cb3925ec637cbf49893dc9b (MEGA-17 scenario/lineage integration and independent test remedies).
- Combined LAB main GitHub Actions run 41911453896: SUCCESS for both Python 3.11 and 3.14. Both jobs executed the MEGA-17 suite gate. This certifies hosted bounded synthetic CI on the named source commit, NOT the authentic real product.
- Previous PR-head runs: 41905139296 and 41905303990 both SUCCESS.
- Canonical main during task authoring: bee314b92981b9ae7ea38d83fe2dbae120c474e4; refresh before analysis.
- Canonical PR #258 (S5-T1 admission) and #259 (continuity documentation) were still draft/open during authoring; refresh before conflict claims.

The purpose of this task is a deeper independent local verification and safe canonical-portability decision, NOT reimplementing or merging MEGA-17.

## 2. Source-of-truth bootstrap

Synchronize source state NON-DESTRUCTIVELY; preserve all existing dirty/untracked local files. Use an isolated LAB worktree with exclusive write ownership for report files. Record exact initial Git refs and the current live CI/head state.

Read on LAB main:
- AGENTS.md; docs/INDEX.md; docs/project/00_PROJECT_CHARTER.md; docs/project/01_CURRENT_STATE_AND_HANDOFF.md; docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md; docs/project/STATE_MAINTENANCE_PROTOCOL.md.
- docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md and MEGA_15_16_PROGRESS.md.
- docs/ai-studio-tasks/MEGA_17_DESIGN_AND_GAP_LEDGER.md, MEGA_17_PROGRESS.md, MEGA_17_CROSS_WORKSTREAM_ACCEPTANCE.md, MEGA_17_TEST_MANIFEST.json, MEGA_17_REAL_EXECUTION_PREREQUISITES.md.
- Actual src/vip_lab/mega03..17, src/gate0/media, src/vip_fvs producer APIs, relevant upstream Gate-3 APIs, tests and CI workflow. Verify public interfaces, do not guess.

Read on actual canonical main, READ ONLY:
- AGENTS.md, docs/INDEX.md, charter/current handoff/state-maintenance protocol, docs/architecture/CANONICAL_CONTRACTS.md, docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md, docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md.
- Exact overlapping source paths and PR #258/#259 diffs, including which API contracts remain open or pending.

If current refs advance, update source-referenced results; dated starting refs are not live authority.

## 3. Deliverable A — Independent post-merge test and source verification

1. Independently inspect run 41911453896 at f20f4a7e and exact Python 3.11/3.14 job steps. Confirm that all six MEGA-17 test files were collected and executed with no skips. A green CI badge alone is insufficient.
2. Independently verify the six media module Git blob IDs in current LAB main:
   __init__.py = b1198560f5c8582b8be8725fed9412597ca08e96
   decode.py = a3c7efad5fdc0c24e7f592512ef176e10e95f128
   probe.py = d95b15505550f54263463e6bcbb9681f00620f17
   proc.py = 244706e9c198ab25afad5894a977cc1a31b39755
   source_guard.py = 9b0a7a64e7b163c94ad5ed62ba16bfedda99c398
   tool_identity.py = 056447631d477f57776c4db5e75cb8bad25b8ebd
3. Confirm all MEGA-03..17 source and tests exist, with no unexpected tracked deletions or .gitignore suppression.
4. Independently read MEGA-16 CLI safe report input/output implementation. Verify trusted repository-anchored outputs/vip_lab/synthetic-reports; no user-selected unsafe root; input verify creates no directory; symlink/no-follow/traversal/nonregular/no-clobber/short-write/partial-cleanup behaviors remain fail closed.
5. Run genuine pytest in a local isolated environment, on the actual LAB main tree:
   PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_lab
   PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_lab/test_mega15.py tests/vip_lab/test_mega16.py tests/vip_lab/test_mega15_16_end_to_end.py
   PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_lab/test_mega17_*.py
   Then run existing bounded Gate-0/Gate-1/Gate-2/Gate-3/FVS source-only suites selected by inspecting actual workflow/tests.
6. Run Python 3.11 and 3.14 locally when available. If one interpreter is unavailable, report its local status NOT_OBSERVED and use corresponding GitHub-hosted CI as independent evidence.
7. If broad historical tests require unavailable Git objects or .orchestration prompt snapshots, attempt the complete suite once and record exact missing cases; run a clearly scoped follow-up with separately justified deselections. Do NOT convert deselections, skips, xfails or absence of a test into a PASS claim.
8. Do NOT run media-generating, probing or encoding tests without separate authorization. No real video archive reads/stat/hash, model downloads, provider calls or real render/export.
9. Test SINGLE_ARM and THREE_ARM integration including actual source occurrence multiplicity, query/arm membership, revision/digest pins and rejection of forged human/PTS/QC claims.
10. Create a precise integrated regression receipt: source SHA, interpreter, command, totals, skipped/deselected/xfail, CI/job IDs, failures and real-world evidence boundaries.

On failure: systematic debugging before proposing a fix. This is a DOCUMENTATION-ONLY audit. Do not silently patch production code.

## 4. Deliverable B — Selective portability decision for canonical VIP

This is a SOURCE-LEVEL compatibility study, not a code transplant.

Compare current LAB source and canonical main and PR #258/#259. For each candidate list path, LAB/canonical Git blob SHA, existing consumers/producers, confirmed overlap, risks, tests, governing authority, value and source-backed disposition:

- ALREADY_CANONICAL
- EXACT_DUPLICATE_DO_NOT_IMPORT
- LAB_ONLY_SYNTHETIC_HARNESS
- CANONICAL_ADAPTER_CANDIDATE
- CONFLICTS_WITH_OPEN_CANONICAL_PR
- BLOCKED_BY_UNRESOLVED_AUTHORITY
- NOT_OBSERVED

Required attention:
- Canonical Gate-0 baseline versus bounded ONE visual arm; 24 positive + 8 absent + 8 development queries, grade-2 Hit@10 thresholds (20/24, lift 5/24, family 3/6). Three-profile SigLIP comparison belongs to Gate-1, not Gate-0.
- Canonical D-2 source admission/rights versus D-3 real-media authorization; PR #258 may change shared custody/descriptor contracts.
- PR #259 handoff is documentation, not source adoption.
- Gate-3 source-native PTS/timebase and no nominal-FPS VFR conversion; A-7 stream namespace and IT-6 terminal-tail decisions remain separate owner-governed open questions until verified otherwise.
- Human editorial authorization vs model/tool proposals, versioned edit plan, technical versus visual/audio QC and export policy.
- Existing H3-C05 and H3-A04 decisions and Atlas scheduling may be stale relative to current source; perform fresh delta validation.
- Canonical PRODUCT.md is explicitly PROPOSED UX context, not permission to build an app.

Reject blanket copying of src/vip_lab/mega03..17 into canonical VIP. Identify the minimum truly valuable compatible source slice, if any, and the needed owner-approved design and separately scoped implementation plan.

## 5. Six-cycle / Superpowers method

Cycle 1: Fresh Git provenance and source/API gap inventory.
Cycle 2: Hosted CI plus genuine local pytest, import and fixture verification.
Cycle 3: Source preservation, trusted filesystem, scenario lineage and authority-boundary adversarial checks.
Cycle 4: Canonical main versus LAB plus PR #258/#259 source/contract reconciliation.
Cycle 5: Brainstorm alternatives, rejected/no-import options, exact independent preparatory slices and reconsideration triggers.
Cycle 6: Independently verify claims, create owner-decision packet, durable documentation PR and final evidence dossier.

Use Superpowers where triggered:
- unexpected failure -> systematic-debugging;
- new design/interface proposal -> brainstorming, owner approval, then writing-plans;
- any separately authorized code fix -> TDD and isolated worktree;
- completion -> verification-before-completion and independent review.
No automatic new Gate-specific skill.

## 6. Authorized output and Git discipline

Allowed additions ONLY under LAB docs/ai-studio-tasks:
- POST_MEGA17_INTEGRATED_REGRESSION_REPORT.md
- POST_MEGA17_CANONICAL_PORTABILITY_DECISION_MATRIX.md
- POST_MEGA17_OWNER_DECISIONS_AND_NEXT_SLICES.md

Do not edit this task, existing implementation, tests, GitHub Actions, canonical files, or project-global handoff during the initial audit.

Commit/push on a NEW isolated LAB branch and open a DRAFT documentation-only PR against LAB main. Do not merge without owner permission.

No destructive Git cleanup, forced pushes, real/protected-media execution, authentic model inference, provider egress, production render/export, or Gate promotion.

## 7. Acceptance and final Turkish report

Produce:
A. exact refreshed LAB/canonical SHAs and branch/worktree status;
B. P0 merged PR identities and verified combined main GitHub CI evidence;
C. real local pytest evidence with full counts and test selection;
D. six exact gate0.media blob identities and CLI confinement verdict;
E. source/query/arm lineage and fake-authority refusal verdict;
F. canonical compatibility matrix and PR #258/#259 findings;
G. prioritized NO-IMPORT decisions, smallest proposed adoption slices, prerequisites and owner decisions;
H. any actual blocker, failure, unavailable environment, deselection or uncertainty;
I. report paths, draft PR URL and immutable candidate SHA.

Choose one final status:
POST_MEGA17_LAB_MAIN_SYNTHETIC_VERIFIED
POST_MEGA17_CI_OR_CONTRACT_BLOCKED
POST_MEGA17_EVIDENCE_INCOMPLETE

Never equate this source-only/synthetic milestone to real Gate-0..3 completion, production readiness, or authorization.
