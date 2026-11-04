# VIP LAB MEGA-08–14 — PARALLEL INDEPENDENT CODEX AUDIT

**Version:** LAB-MEGA-08-14-CODEX-AUDIT-v1.0
**Date:** 2026-11-04
**Target:** Centaurioun/video-intelligence-pipeline-2
**Protected canonical repo:** Centaurioun/video-intelligence-pipeline
**Stable known-good comparison commit:** 22f1ffa7064f697d4049e39587945b1decabec4e
**Audit branch created:** codex/audit-mega08-14-20261104, initially at the stable comparison commit
**Writing policy:** AUDIT BRANCH ONLY. NO LAB MAIN WRITES, NO MERGE, NO GATE PROMOTION.

## 1. Mission

Act as an independent skeptical reviewer while Google AI Studio is authoring MEGA-08–14 on LAB main.

This is a genuinely parallel, but **write-isolated** workflow:
- AI Studio is the exclusive writer of LAB main code packages and associated test source as authorized by the Owner.
- Local Codex has its own isolated Git worktree/branch, reads fetched exact main commits and produces audit notes in its audit branch only.
- Codex may report failures, ask for focused AI Studio fixes, and run permissible local synthetic tests in the AUDIT worktree when dependencies are already installed.
- Codex must NOT automatically fix/commit source on LAB main, merge its own branch, promote Gates, open real media or install/download any model.
- Inspect exact immutable main SHA, not the moving branch name alone. New main commits invalidate prior candidate conclusions until rechecked.

## 2. Fresh baseline facts: verify again before claiming

LAB main was non-forcibly fast-forwarded to prior verified head 22f1ffa7064f697d4049e39587945b1decabec4e. This head passed GitHub Actions run 41756569162 with 307 selected tests per Python 3.11 and 3.14.

Canonical main at planning time: 592952daf475b1bbae2eebdee64d992c1a744f08.

This audit branch was created independently from the verified LAB commit. The new AI Studio task spec was later authored on LAB main, so the auditor should fetch remote main and read the spec without checking out or modifying main.

**Specification:** docs/ai-studio-tasks/MEGA_08_TO_14_ALL_REMAINING_LAB_CODE_PROGRAM.md, version LAB-MEGA-08-14-v1.0.0.

**Critical branch layout:**

- origin/main — AI Studio direct-push destination, MOVING; Codex read-only.
- codex/audit-mega08-14-20261104 — independent Codex audit report branch; exclusive Codex writes.
- original VIP canonical main — protected, read-only under this assignment.
- historical codex/lab-mega03-07-remediation — earlier 307-PASS candidate; no need to merge/rewrite.

If user has multiple local VIP worktrees, identify them by actual git rev-parse/worktree list. Do not assume an absolute local path or hardcode user device names.

## 3. Safe local setup

In a local clone of the LAB repository, run commands only after verifying you are in the correct remote (Centaurioun/video-intelligence-pipeline-2, NOT the original VIP repository).

Suggested read-only preflight:

    git remote -v
    git status --short
    git worktree list
    git fetch origin main codex/audit-mega08-14-20261104
    git rev-parse origin/main
    git rev-parse origin/codex/audit-mega08-14-20261104
    git merge-base 22f1ffa7064f697d4049e39587945b1decabec4e origin/main

If the audit worktree is absent, create it at a NEW unoccupied directory using:

    git worktree add -b codex/audit-mega08-14-local <NEW_PATH> origin/codex/audit-mega08-14-20261104

If the branch name or target path already exists, inspect rather than overwrite. Do not delete or prune existing worktrees, run git clean, hard reset or force push.

Read the evolving task spec from the remote main without modifying the audit tree:

    git show origin/main:docs/ai-studio-tasks/MEGA_08_TO_14_ALL_REMAINING_LAB_CODE_PROGRAM.md

If the new task code is only on a future main commit, inspect it with:

    git diff --stat 22f1ffa7064f697d4049e39587945b1decabec4e <IMMUTABLE_MAIN_SHA>
    git diff --check 22f1ffa7064f697d4049e39587945b1decabec4e <IMMUTABLE_MAIN_SHA>
    git diff 22f1ffa7064f697d4049e39587945b1decabec4e <IMMUTABLE_MAIN_SHA> -- src/vip_lab tests/vip_lab docs/ai-studio-tasks

Use the correct immutable SHA from GitHub; never invent or reuse a previous SHA as the latest.

## 4. Audit phases — can overlap authoring

**Phase A (immediately, while AI Studio codes): preflight and scope design**
1. Inspect canonical main GitHub handoff, WBS, A-7 S5 owner decisions and PR #258; do not infer source authority from draft PR content.
2. Verify the LAB 307-PASS starting source tree and six src/gate0/media dependencies.
3. Audit the MEGA-08–14 proposal for duplicate existing functions, ambiguous source APIs, unsafe input path semantics, impossible untrusted proof and unclear acceptance criteria.
4. Record an actionable pre-execution risk inventory. Do NOT write code or interfere with AI Studio's evolving main.

**Phase B (for each immutable new main commit that the Owner submits): incremental review**
1. Fetch main; record exact reviewed SHA, parent and changed paths.
2. Read all new wave source/test files; classify real code changes versus empty placeholders and test-only superficial checks.
3. Compare actual imported module names, dataclass fields, constructor signatures, error codes and source paths; do not blindly trust AI Studio's final prose.
4. Check source media/model/network/FFmpeg/subprocess side effects, path traversal, no-follow, duplicate JSON keys, fake Owner/human approval and evidence-strength upgrades.
5. Check model spaces (768/768/1152), signed source occurrence identity, rational PTS and VFR policy, missing human approval/QC, no cross-arm model winner.
6. Verify GitHub Actions selected all submitted new MEGA-08–14 tests and the previous 307 baseline on BOTH Python versions.
7. Verify no file deletions, especially .github/** and src/gate0/media/**; compare commit trees, not just test logs.
8. Mark source-level concerns as P0 / P1 / P2 with exact path:line and reproduction/test guidance.
9. When a new main SHA appears, previous result remains a historical audit, not a live blanket PASS.

**Phase C (once all submitted waves pass GitHub CI): final independent review**
1. Review full original-base→candidate diff, exact test coverage, status/attestation vocabulary and results from real CI logs.
2. Check the program fulfills only synthetic LAB claims; identify which waves were NOT_NEEDED or BLOCKED and whether that is honest.
3. Provide a candidate disposition: LAB_SYNTHETIC_REVIEW_ACCEPTABLE / CHANGES_REQUESTED / BLOCKED_SCOPE.
4. Do not merge LAB main or original VIP, even if review is green.
5. Keep original canonical Gate completion, authentic model and production export separately NOT_AUTHORIZED/NOT_OBSERVED.

## 5. Source contract review checklist

- Existing vip_fvs.query_batch, batch_retrieval, three_arm_batch and batch_report are reused rather than cloned.
- MEGA-09 candidate identity includes query, arm, exact source occurrence, source revision and native locator; bytes-identical occurrences at distinct paths remain distinct.
- MEGA-10 generated-only PTS tables never become real MEASURED evidence; duplicate PTS and half-open end semantics are handled correctly.
- MEGA-11 proposal does not impersonate a HumanDecisionArtifact or issue a real EditPlan.
- MEGA-12 uses genuine Gate-2 RecoveryHarness and valid FaultClass capability; no false production restart or scale inference.
- MEGA-13 cannot accept bare QC PASS or synthetic visual/audio evidence; production export remains unauthorized.
- MEGA-14 genuinely composes existing source seams; a chain of mocks that only return preset values is not sufficient.
- Anti-regression: previous MEGA-03 S5 metadata-only boundary remains closed; no real source bytes, no positive BMFF positional mapping.
- No provider/model/corpus/real archive use, no source-media deletion, no source authorizations inferred from metadata.
- No hidden modifications outside src/vip_lab/mega08..mega14, tests/vip_lab/test_mega08..mega14, MEGA_08_14_PROGRESS.md, plus explicitly justified limited existing LAB integration paths.
- No PR #258 copy/paste, original WBS/Atlas edits or canonical merge.

## 6. Evidence and review taxonomy

Distinguish:

- VERIFIED_GITHUB: fetched exact SHA, paths, status, CI logs and test counts.
- SOURCE_INSPECTED: reviewer read code and documented specific behavior; not proof of runtime under all conditions.
- REPRODUCED: real permissible test run with command/environment/log.
- INFERRED: suspicion not yet reproduced.
- NOT_OBSERVED: no evidence.
- BLOCKED_SCOPE: review cannot progress without protected source, model or Owner decision.

A code review with no findings does not itself execute tests. A passing 307-test baseline with MEGA-08–14 steps skipped does not certify new waves. Do not upgrade evidence silently.

If local pytest is unavailable, do not install dependencies without Owner permission. Use hosted Actions, static review, and honest NOT_EXECUTED markers.

## 7. Audit output paths and writer ownership

Write reports ONLY within your separate audit branch, for example:

- docs/audits/mega08-14/PRE_EXECUTION_SCOPE_AND_RISKS.md
- docs/audits/mega08-14/COMMIT_REVIEW_LEDGER.md
- docs/audits/mega08-14/FINAL_INDEPENDENT_REVIEW.md

You may add bounded text evidence to the same audit directory; do not edit any AI Studio production/test files in main. If a separate fix is justified, propose a minimal patch in prose for Owner approval; never silently push a repair onto main.

Report in Turkish with exact source SHA, source/test paths, P0/P1/P2 findings, unknowns and recommended next action. If a review depends on an unavailable new main commit, say NOT_YET_SUBMITTED, do not claim it passed.

## 8. Superpowers skill routing

- brainstorming: identify architecture duplicates/trust gaps before implementation recommendations.
- using-git-worktrees: maintain read/write isolation; inspect existing branches before creating worktree.
- systematic-debugging: use CI symptom→root cause→falsifiable hypothesis, not random edits.
- requesting-code-review: the auditor is an independent reviewer, not an AI Studio self-check.
- receiving-code-review: verify review findings against real source before repairs.
- verification-before-completion: no "all done" without exact SHA and actual selected/tested suites.
- dispatching-parallel-agents: not required; use only if independent source paths and exclusive writer ownership are available.

**The concurrent design is safe because only AI Studio owns LAB main; Codex owns audit branch documents.**

STOP after the requested audit milestones. No canonical Gate promotion, real video processing, model downloads or automatic merges.
