# VIP B-first B2 Stage A — One-commit LAB debugging-report publication exception

**Date:** 2026-11-07 (Europe/Istanbul)
**Decision:** OWNER APPROVED — ONE DOCUMENTATION-ONLY LAB REVIEW-BRANCH PUSH WITH EXPLICIT, NON-PASS VERIFIER DEBT. NOT AN EXCEPTION FOR OTHER COMMITS.
**Authority record:** The Repository Owner explicitly answered **"onaylıyorum"** to the narrowly scoped question authorizing only publication of the exact locally accepted debugging-report commit to its named LAB review branch despite the recorded 26 LAB-baseline verifier failures and 1 checkout-topology failure. This document records that authorization; it does NOT independently certify the local report bytes, reviewer identity or the verifier results.

## Exact authorized payload

- Repository: `Centaurioun/video-intelligence-pipeline-2` (LAB), NOT Canonical.
- Allowed remote branch: `refs/heads/review/bfirst-a2-preflight-systematic-debug-20261107`.
- **Exact existing local commit**: `4a1324253fcd868bd6746c33e8e10f29360a5d7a`.
- **Exact expected tree**: `7b54aa4ecaf7146969f25f24fd64370b7ed41019`.
- Required sole parent: LAB `main@5eab58ea2a5424424cb95f2690654b91395425df`.
- **Only permitted changed path**: `docs/reviews/2026-11-07-vip-bfirst-a2-preflight-systematic-debugging-report.md`.
- Reported LAB worktree: `/Users/yusuf/.codex/worktrees/bfirst-preflight-debug-lab`; the local commit and review were reported by the Codex controller, and remain NOT_OBSERVED from GitHub as of this decision's initial live inspection.
- Local report branch and exact commit were NOT_FOUND in GitHub API at approval time. Do not infer local commit validity from this decision: verify locally before the single permitted publication attempt.

## Precisely waived verification failures (not relabeled PASS)

The controller reported running `bash scripts/verify-workspace.sh --mode feature-worktree --expected-head <exact_sha>` against:
- LAB report candidate: exit 1, **27 FAIL**;
- clean LAB main baseline: exit 1, **26 FAIL**.

Individual findings were reported: 26 `BASELINE_REPRODUCED`, 0 `REPORT_INTRODUCED`, 1 `WORKTREE_OR_ENVIRONMENT_SPECIFIC` (report checkout uses a standalone clone/root rather than a registered linked worktree), 0 unresolved in the **reported** classification.

Independent GitHub read-only checks of LAB `main@5eab58ea2a5424424cb95f2690654b91395425df` verified that the repository contains the exact Canonical verifier blob `fba456d3c1f3edff4e7f7d96245297dbc514fb65`, which expects the Canonical origin URL and requires 27 static file paths, **14 absent from LAB main**. This independently supports substantial baseline incompatibility; the complete 26+1 check-level reproduction is controller-REPORTED, not independently reproduced through this remote connector.

The exception waives ONLY these classified baseline/topology errors for this *one documentation-only branch publication*, provided a fresh local check shows no new report-introduced, unresolved or security-sensitive failures. It does not mean the verifier passes; record `VERIFY_WORKSPACE=FAIL (27; 26 BASELINE, 1 TOPOLOGY)`. If failure count or nature changes, STOP pending review. Do not modify verifier, copy missing Canonical files, fill fake placeholders, or introduce an undocumented global exception.

## Hard pre-push prerequisites

1. Read this exact Owner decision and applicable current LAB `AGENTS.md` / project branch and workflow rules before work. Recheck LAB remote main, current target ref existence/absence and one-document diff. Preserve existing local cloned checkout and the separate clean detached baseline checkout; do not force-reset/rebase/clean/stash or delete worktrees.
2. Verify `git rev-parse HEAD` equals the exact commit and `git rev-parse HEAD^{tree}` equals the exact tree; verify direct parent equals LAB baseline and `git diff --name-status <baseline> <commit>` names exactly the one Markdown report. Check the actual committed report in full for known secret/token leaks and verify that diagnostics are correctly labelled `REPORTED_BY_CONTROLLER` / `ROOT_CAUSE_NOT_OBSERVED`.
3. Record the exact `verify-workspace` outcome, including 26 baseline failures and 1 topology failure; do not reclassify as PASS. Verify there are no `REPORT_INTRODUCED` or unresolved failures. Check `git diff --check`, committed file integrity, secret scan and the available reviewer `ACCEPT` provenance; preserve caveat: final separate native thread and independent reviewer worktree NOT_VERIFIED.
4. The controller reported `.trail/.gitignore` and ignored local cache created in the report checkout; **do not delete or silently stage these side effects**. Check `git status --porcelain=v1 --untracked-files=all` and staged diff to ensure that the push is exact commit only. No expectation of fully clean worktree when known local Trail side effects are preserved, but no unapproved files/commit may be included.
5. Verify LAB `.github/workflows/post-mega17-reconciliation-contract.yml` and `vip-ai-studio-synthetic-ci.yml` live trigger scopes: a push to the exact review branch with only this Markdown file must not start unrelated Actions. Read any updated workflow rules; do not assume historical census suffices.
6. Recheck branch protection/rulesets and authenticated intended pusher; verify no remote ref collision or head drift. Do not change settings, variables, tools or runner policy.
7. If all above conditions hold, authorize **ONE normal non-force push of the exact existing SHA only** to `review/bfirst-a2-preflight-systematic-debug-20261107`. No retry if rejected; no branch creation through a different API path, no amend/rebase/recommit and no main merge or integration PR.

## Required independent post-push readback

After a successful push, verify through GitHub: exact target remote branch HEAD, exact commit/tree and **single added report Markdown file only**, unchanged LAB `main` and Canonical `main`, no unexpected Actions run. Preserve full verifier failure ledger and review limitation in the resulting handoff. Mark `LAB_DEBUG_REPORT_PUBLISHED_UNDER_DOCUMENTED_BASELINE_EXCEPTION` only on independently observed success. If no successful push, keep `LAB_DEBUG_REPORT_LOCAL_ACCEPT_BLOCKED_PUBLICATION` with exact cause.

## Strictly not approved

- No new FFmpeg/FFprobe preflight execution, rerun or new Canonical workflow push;
- no production A1 issuance, no artifact/media generation or download, no Stage A3, Stage B/C, no Gate promotion;
- no new workflow/tool hash variables, administrative ruleset changes, protected/real archive/model/provider operations, canonical-main or LAB-main merges, destructive Git or modification of backup objects;
- no expansion of this waiver to any other document/commit or general LAB verifier-debt exemption.

**Invariant terminal technical states:** `BFIRST_B2_TOOL_PREFLIGHT_EXECUTED_ONCE_FAILED`; `A2_BLOCKED_TOOL_IDENTITY`; `A3_NOT_RUN`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
