# VIP — B-first media-free preflight: explicit GH013 credential authorization and one additional push

**Date:** 2026-11-07 (Europe/Istanbul)
**Owner approval:** Repository Owner explicitly replied "onaylıyorum. ayrıca authorize yaptım workflow'u. yeniden denetelim." to the scoped request to grant the existing Centaurioun GitHub CLI OAuth credential the workflow scope and authorize exactly one additional ordinary non-force push of the unchanged media-free preflight commit. The Owner reports having completed the workflow OAuth authorization. This declaration is an authorization, **not independent readback evidence of the local token scope**.

## Frozen purpose and source

- Canonical: Centaurioun/video-intelligence-pipeline; frozen prior B-first source base cac74495d80d9eaa144a12e9aa67eba78ba2f062; protected Canonical main at latest check 3bfcc2ba221b36df6773e630b44479ec961d630a, no main changes.
- Approved media-free preflight source commit: 54b8f945a51b634e2d3c2d955a9e1f1de9e7777b, tree 0c4db75cc70afcc5e33bf008c466fa1a326fd397, locally reviewed native reviewer 01a1b3fe-4567-7973-9fd5-c1b24ec597a8 = ACCEPT (Codex-reported). GitHub independently read the exact commit/file; relative to cac74495... it changes only .github/workflows/bfirst-tool-identity-preflight.yml, with 4 local-history commits. Source must not be amended/rebased/recommitted just to push.
- Local worktree (Codex-reported): /Users/yusuf/.codex/worktrees/a3f0/video-intelligence-pipeline, exact branch design/bfirst-a2-tool-identity-preflight-20261107. Preserve it and the separate unpublished A1 video producer commit 413d032e5635e4d8670e5565856f7fcfcfaca3ff.
- Remote branch refs/heads/design/bfirst-a2-tool-identity-preflight-20261107 was NOT_FOUND; filtered Actions run count = 0 at last independent check. GitHub API could read the immutable orphaned source commit, which does not imply a branch was created or run started.
- Active ruleset 26744266 restricts creation/update of exactly that preflight branch, one bypass actor Centaurioun user ID 86323645. Verified linked GitHub login Centaurioun/86323645 belongs to the ChatGPT connector, NOT proof of the local Git push credential scope.
- The remote Git push failed once with GH013, reported as OAuth App missing workflow scope. The initial attempt used HTTPS and gh auth git-credential; local gh auth status had repo but lacked workflow before the Owner authorized the extra scope. Prior denial remains an auditable failed attempt.
- Governing original media-free preflight owner decision and task LAB 02aab37b42c3452e98e8751be410c72ea809bcc6. Independent GH013 audit LAB 32329c0c169f933b9b938687e1216cd2530f0afe.

## Narrow added authority

**AUTHORIZATION:** Confirm the Owner's already-performed workflow OAuth permission grant (do not refresh/re-authorize it again without evidence of need and a separate decision) and allow exactly ONE additional normal, non-force, non-destructive Git push from the unchanged local verified candidate to refs/heads/design/bfirst-a2-tool-identity-preflight-20261107, through the intended Centaurioun identity. If the target branch is absent and exactly one reviewed commit/ref push occurs, the existing media-free workflow's FIRST-ATTEMPT Actions measurement is authorized under the original owner preflight packet.

### Mandatory pre-push read-only gates

1. Confirm current local gh auth status -h github.com includes workflow along with required Git permissions; avoid token printing. Confirm Git HTTPS credential helper actually uses the same authorized gh token and account Centaurioun. If scope cannot be independently confirmed, STOP with BLOCKED_WORKFLOW_SCOPE_UNVERIFIED. Do not run gh auth refresh a second time automatically, no new credential creation or token disclosure.
2. Verify clean exact local worktree HEAD 54b8f945a51b634e2d3c2d955a9e1f1de9e7777b and tree 0c4db75cc70afcc5e33bf008c466fa1a326fd397; one approved changed workflow path; existing actionlint v1.7.12 local PASS, native independent exact SHA ACCEPT remain applicable; no changes or unstaged state.
3. Fresh remote inspection: branch still absent and no prior associated first-attempt Actions run. Verify ruleset 26744266 active and exact included ref/actor, current Canonical workflows and triggering event census, no additional workflow scheduled by this branch push, effective rights, no unrelated admin writes.
4. Administrator independently reads BFIRST_B2_TOOL_PREFLIGHT_EXPECTED_SHA and confirms exact 54b8f945a51b634e2d3c2d955a9e1f1de9e7777b; do NOT update variable if already equal; missing/mismatched value stops before push. Confirm first-step guard uses this source SHA and run_attempt == 1 before any byte read, job permissions empty and no tools/media/intentional network.
5. Reconfirm accepted residual risk: standard hosted runner network is available but workflow makes no intentional egress; Github platform may schedule reruns but all run_attempt != 1 must abort BEFORE measuring tool bytes. Do not misstate this as firewall or absolute zero-rerun guarantee.

### Exactly one additional permitted push attempt

After ALL gates VERIFIED, run one normal non-force push ONLY:
git push origin HEAD:refs/heads/design/bfirst-a2-tool-identity-preflight-20261107

No force, rebase, workaround via GitHub API create_branch/update_ref, dummy branch, workflow rename, repeat retry, workflow_dispatch, other actor, or main modification. If GH013 or any new error occurs, STOP and preserve the receipt. No third attempt has been authorized.

If successful, inspect GitHub first-attempt run/ref/source SHA, numeric job, workflow source, image and actual FFmpeg/FFprobe file-byte measurements. The workflow must never invoke those binaries, read media, download/install tools, or upload artifacts. Independent reviewer must verify run/log facts and exact hash pair in separate LAB documentation branch.

**This addendum does not approve the resulting as-yet-unmeasured binary hashes**, does not authorize setting BFIRST_B2_APPROVED_FFMPEG_SHA256 or BFIRST_B2_APPROVED_FFPROBE_SHA256, does not authorize production A2 issuance/video, A3, Stage B/C, protected media/model/provider, Gate promotion, main merge, force push, backup change, or additional attempts.

## Terminal evidence states

- Before accepted push and independently verified measurement: PREFLIGHT_SOURCE_VERIFIED (native reviewer reported + remote file independently inspected), BLOCKED_PRE_PUSH_WORKFLOW_SCOPE_PENDING_LOCAL_READBACK, A2_BLOCKED_TOOL_IDENTITY, A3_NOT_RUN.
- If one authorized first-attempt hosted run yields independently verified hashes: BFIRST_B2_TOOL_PREFLIGHT_MEASURED_PENDING_OWNER_HASH_APPROVAL, A2_BLOCKED_TOOL_IDENTITY, A3_NOT_RUN.
- Any failure: BLOCKED with exact failed gate; no guessed tool hashes, no silent retries.
- Always: STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED; CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT.
