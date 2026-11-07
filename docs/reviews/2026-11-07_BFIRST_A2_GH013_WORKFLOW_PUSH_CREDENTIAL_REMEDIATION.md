# VIP B-first A2 — GH013 workflow-scope push rejection and credential remediation

**Date:** 2026-11-07, Europe/Istanbul
**Disposition:** `PREFLIGHT_SOURCE_REPORTED_LOCALLY_VERIFIED_AND_REMOTE_OBJECT_INSPECTED`; `BLOCKED_PRE_PUSH_GITHUB_WORKFLOW_SCOPE`; `A2_BLOCKED_TOOL_IDENTITY`; `A3_NOT_RUN`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
**Authority:** Documentation-only independent review; no new scope, OAuth login/refresh, token, ref, workflow push, API-created branch, Actions run, media, FFmpeg process, main change or merge authorized by this audit.

## Independently verified (GitHub, exact refs)

Canonical `Centaurioun/video-intelligence-pipeline`:
- `main=3bfcc2ba221b36df6773e630b44479ec961d630a`.
- Source predecessor `cac74495d80d9eaa144a12e9aa67eba78ba2f062`.
- The locally reported preflight candidate commit `54b8f945a51b634e2d3c2d955a9e1f1de9e7777b`, tree `0c4db75cc70afcc5e33bf008c466fa1a326fd397`, was **retrievable via GitHub REST commits**, and its exact one newly added workflow was independently fetched at that SHA. Git blob `aca16c1004a7823b17770f405c6cca740ca02ae2`; `compare(cac74495...54b8f945)` lists **only** `.github/workflows/bfirst-tool-identity-preflight.yml` as an addition (4 commits of sequential local revision history). The tip commit alone modifies this path. A reachable Git object without a branch ref is not proof of an accepted push, durable published branch or an Actions run.
- Target branch `refs/heads/design/bfirst-a2-tool-identity-preflight-20261107` returned GitHub 404. Filtered repository workflow runs for that branch: `total_count=0`. No preflight tool hashes, image/version or run/job IDs can be claimed.
- Active preflight ruleset `26744266` is `bfirst-a2-tool-preflight-single-actor`, scoped exclusively to target branch, with creation/update rules and single bypass user `Centaurioun` ID `86323645`. Existing production issuance ruleset `26738994` active and separately scoped; no preflight rule weakening is needed.
- Owner's prior one media-free Strategy B approval in LAB `02aab37b42c3452e98e8751be410c72ea809bcc6`; its permission to make one normal non-force feature-branch push is constrained by immutable pre-push gates, and its controller instructions explicitly prohibited retry/rerun. A rejected network push and later GitHub-visible unreferenced objects do **not** confer permission for an automatic second push attempt.

LAB `main=5eab58ea2a5424424cb95f2690654b91395425df`; both immutable DO_NOT_DELETE backup releases verified `immutable=true`.

## Exact error and interpretation

Native Codex reported one rejected `git push`, with GitHub `GH013`: OAuth App authorization lacked the **`workflow` scope** needed to create/update `.github/workflows/bfirst-tool-identity-preflight.yml`. This matches official GitHub documentation:
- https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens
- https://github.com/cli/cli/discussions/7251

**Important:** An admin user and a matching ruleset bypass identity are insufficient if the transport's active OAuth/installation/PAT credentials lack permission for workflow source. The credential actually used by `git push` may differ from `gh` CLI credentials or the ChatGPT GitHub connector credential.

## Read-only remediation preflight — CURRENTLY SAFE

1. Identify exact push remote protocol and credential **type** (HTTPS OAuth App vs GitHub CLI helper vs existing authorized SSH), credential owner/user ID and whether the authentication principal is the designated bypass actor. Do not print complete remote URLs if they embed secrets, OAuth/PAT values, SSH private keys, `gh auth token`, `gh auth status --show-token`, `git credential fill` outputs, raw Authorization headers, verbose credential traces, secrets in log or terminal transcript.
2. If `gh` is present, inspect `gh auth status -h github.com` **without `-t`** and separate `gh auth setup-git` helper presence read-only. A Git push over HTTPS may use a different credential helper even if `gh` has the correct scopes. If an existing SSH identity is used, verify it belongs to `Centaurioun` and is authorized to write only the reviewed ref. Read-only authentication probe must not write a branch or start Actions.
3. Prefer a **pre-existing already-authorized Git authentication route** with workflow-file write permission and the exact ruleset actor. If none exists, obtain an explicit Owner decision to expand only the required account/host workflow permission or configure a restricted credential. Example `gh auth refresh -h github.com -s workflow` is valid **only** when `gh` manages the actual push credential and the Owner authorized changing its OAuth grant. It can launch browser OAuth and change local credentials, so do not run it silently. Do not grant broad org/admin/delete scopes, issue secrets into chat, switch the repository to an unrelated actor, or alter the workflow to evade authorization.
4. DO NOT use the ChatGPT GitHub connector's `create_branch` / `update_ref` route to bypass Git push permissions: it would change the authorized event/actor/control-plane behavior and may not generate the intended `push` trigger. Do not create a dummy branch, amend candidate, modify YAML paths or change main to work around GH013.
5. Verify original source and independent reviewer `ACCEPT` evidence remain exact `54b8f945...`/tree; actionlint and local harness evidence remain as reported, not independently rerun here. Re-read `BFIRST_B2_TOOL_PREFLIGHT_EXPECTED_SHA` and branch ruleset through authorized admin immediately prior to any future push; the variable readback is NATIVE-REPORTED, not independently accessible through ChatGPT GitHub fetch. Reinspect Canonical workflows' event census and current run count.
6. Obtain a **narrow Owner clarification/addendum** authorizing one additional ordinary non-force push attempt after the previously rejected attempt, using the exact unchanged SHA and only an independently verified workflow-write-capable `Centaurioun` credential; additionally authorize changing the relevant OAuth grant ONLY IF necessary and narrowly specified. Without it remain `BLOCKED_PRE_PUSH_GITHUB_WORKFLOW_SCOPE`.
7. With explicit owner addendum AND all old gates reverified, a native authorized controller may attempt exactly one additional non-force `HEAD:refs/heads/design/bfirst-a2-tool-identity-preflight-20261107` push from the existing isolated worktree. The push is the triggering action and must not be a probe for permissions. Any failed push or unexpected extra run => STOP; no more retries, no force, no API-ref workaround. Successful run is still a **media-free tool-byte measurement**, not approval of tool digests or A2 production.
8. After run, independent reviewer validates exact event/attempt/ref/job/log/image/paths and both executable SHA-256 values, preserving `A2_BLOCKED_TOOL_IDENTITY` until concrete exact hash pair gets separate Owner acceptance and source identity matching.

## Technical trust footnotes

- The exact fetched workflow is `on: push` with exact branch+workflow path, `permissions: {}`, no checkout/actions/media/artifact steps and two commands: (1) identity/ref/workflow/expected-SHA/run_attempt guard, (2) Python read-only byte hash and bounded local package metadata. The absence of FFmpeg/FFprobe **process execution** is visible in the source; no actual runner execution is observed. GitHub workflow-aware validator version `actionlint v1.7.12` success and independent native reviewer `ACCEPT` are local Codex reports.
- The proposed GitHub Actions job can still use network through the hosted runner. This is the Owner-accepted honest-runner residual risk, not an egress firewall.
- GitHub's rejected push may have transferred Git objects despite refusing ref creation; the object's API visibility does not imply branch creation/CI and should not be 'repaired' by rewriting commit history.

**Terminal:** `BLOCKED_PRE_PUSH_GITHUB_WORKFLOW_SCOPE` pending exact credential provenance + scoped Owner addendum. No A2 issued/Stage A3.
