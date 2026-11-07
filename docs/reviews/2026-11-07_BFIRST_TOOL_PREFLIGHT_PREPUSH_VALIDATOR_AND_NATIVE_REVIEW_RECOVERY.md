# VIP B-first — Preflight pre-push validator and native reviewer recovery

**Date:** 2026-11-07 (Europe/Istanbul)
**Disposition:** `BLOCKED_PRE_PUSH_GITHUB_ACTIONS_VALIDATOR_AND_EXACT_SHA_REVIEW`; `A2_BLOCKED_TOOL_IDENTITY`; `A3_NOT_RUN`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.

## Authority and observed independent facts

- Owner's **separately scoped** one media-free Strategy B preflight approval and task: LAB `decision/vip-bfirst-a2-media-free-preflight-owner-approval-20261107@02aab37b42c3452e98e8751be410c72ea809bcc6`. It permits **one** future non-force preflight push and measurement job only after every pre-push gate; no production A2 issuance, FFmpeg/FFprobe process, artifact upload/download, main mutation, source/media or model operation.
- Source worker reports Canonical native thread `01a1b3df-2414-7c33-8f7d-512ee7ec534c`; clean isolated local worktree `/Users/yusuf/.codex/worktrees/a3f0/video-intelligence-pipeline`, branch `design/bfirst-a2-tool-identity-preflight-20261107`; candidate `c71e5959af772b93ced3631bf8a9c3d17149cae0`, tree `b70a27ca89e7c6b3d6b04ed28885e2069f52dc0d`, exact single changed path `.github/workflows/bfirst-tool-identity-preflight.yml`. **REPORTED LOCAL** only: the exact commit returned GitHub 422 `No commit found` and preflight ref returned 404; no remote implementation inspection possible.
- First independent review at local predecessor `8eb46e7...` returned `NEEDS_WORK`; source corrected PATH ambiguity and committed new exact SHA, but reviewer creation returned **only `clientThreadId`**. No verified native `threadId`, host/project binding, separate clean read-only worktree or `ACCEPT` on `c71e5959...`. Per current Canonical `docs/architecture/CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md`, a pending `clientThreadId` is **not** a native thread ID. Resolve it through a tool that explicitly supports that key, or inspect native `list_threads` and targeted `read_thread`. Do NOT pass the key to `read_thread` or `get_worktree_creation_status` (requires different operation ID) and do NOT retry creation while pending/ambiguous. If no supported resolver, record `BLOCKED_NATIVE_REVIEWER_IDENTITY` and preserve candidate.
- Developer-only local harness assertions, generic YAML parser, Bash `-n`, workspace verifier and secret scans are **REPORTED**. Generic YAML or Bash syntax does not establish GitHub Actions schema/context correctness. The next gate explicitly requires a GitHub Actions-aware validator, e.g. `actionlint`.
- Canonical GitHub `main=3bfcc2ba221b36df6773e630b44479ec961d630a`; previous B-first candidate `cac74495d80d9eaa144a12e9aa67eba78ba2f062`. LAB main `5eab58ea2a5424424cb95f2690654b91395425df`. Existing issuance ruleset `26738994` is NOT sufficient protection for different preflight branch. Both backup GitHub releases `immutable=true`.

## Bounded recovery order — DO NOT rewrite the producer or push prematurely

### P1. Resolve validator as routine ENABLE work

1. In the existing verified isolated preflight worktree, first run read-only environment discovery: `command -v actionlint`; inspect known A1 locally cached/user-scoped actionlint v1.7.12 **without modifying the A1 worktree**; confirm executable identity, release checksum/provenance where available, version and compatibility with this Mac.
2. If no suitable known tool exists, follow Canonical `AGENTS.md` routine-development prerequisite policy and `resource-policy-v5.yaml`: prefer existing/cached tool, then an isolated project/user-scoped verified dependency; no `sudo`, no Homebrew/system-wide mutation, no source/workflow modification, no installer integrated into the hosted preflight. Record any dev-only public dependency retrieval separately; the preflight workflow itself remains no-download/no-egress-intent.
3. Validate exact file using `actionlint -color=false .github/workflows/bfirst-tool-identity-preflight.yml` (or actual installed version's equivalent documented CLI), plus a test of `on: push` only exact branch/path, expression contexts, one first guard preceding all file reads, `permissions: {}`, no forbidden actions, bounded timeout and rerun refusal. Verify exit status. Generic PyYAML parsers may coerce `on` under YAML 1.1 and alone do not certify workflow semantics.
4. Do not count tool-install/parse failures as TDD RED. If the validator finds a material defect, use systematic debugging and prospective TDD, amend the **one permitted workflow file only**, create a NEW candidate SHA/tree and rerun actual reviewer against new SHA. No source changes merely to generate passing evidence.
5. If no validator can be recovered under the existing bounded task authority, stay `BLOCKED_GITHUB_ACTIONS_VALIDATOR`, NO PUSH. Do not replace with a generic YAML pass.

### P2. Establish real exact-SHA independent reviewer

1. First inspect the *pending* reviewer creation response and current native tool schemas, native `list_projects`/`list_threads`, and compatible resolver if exposed; preserve `clientThreadId` as pending only.
2. If native ID can be resolved: verify actual `threadId`, local host, Canonical project ID `1c15c3b9-5df2-46fb-9d3b-285b8c2189ee`, CWD, Git common dir, unique worktree, HEAD and tree equal to **current** candidate. If not, report exact mismatch, do not accept reviewer.
3. If no reviewer exists and current protocol supports creating a truly fresh independent reviewer, use that only after checking pending duplicate state and authorized scheduler/writer leases. Distinct **clean read-only** worktree on exact candidate SHA, not producer worktree or dirty shared checkout.
4. Review FULL workflow source and local validator receipt; verify source SHA/tree, exact owner grant, trigger/replay/branch/ref and first-step SHA guard, SHA-variable semantics, PATH ambiguity/symlinks/writable dirs, regular-file stat/hash bounds, the absence of FFmpeg/FFprobe process execution/media/network commands/uploads, output limits, one-run intent vs platform rerun reality, current Canonical workflow trigger census.
5. Reviewer `ACCEPT` must name actual native ID/worktree and exact immutable final SHA/tree. Client setup token, message delivery, incomplete review, test-free source glance or prior `NEEDS_WORK` cannot substitute.
6. If reviewer cannot be established, `BLOCKED_EXACT_SHA_NATIVE_REVIEW` persists, NO PUSH.

### P3. Return to separately authorized admin pre-push checks — only after P1 and P2 pass

- Reverify target **preflight** branch ruleset creation/update controls and one named pusher (do not infer from issuance ruleset `26738994`).
- Set/read-back `BFIRST_B2_TOOL_PREFLIGHT_EXPECTED_SHA` to exact **reviewed** 40-hex commit via authorized admin; no currently reported setting is proof.
- Reinspect Canonical workflow event/branch/path triggers and possible downstream workflows, final branch/ref state, actual pusher and permissions; only one reviewed non-force branch push may launch the authorized first-attempt media-free job.
- Preserve explicit Owner acceptance that hosted runner egress exists and that unauthorized platform reruns can be started but must refuse **before tool-byte measurement**.
- If any P3 condition fails, STOP before push without weakening or editing another ruleset/setting to manufacture success.
- No FFmpeg/FFprobe invocation, media generation, protected archive, models/providers, production A2 issuance, A3 artifact operations, Stage B/C, main merge, destructive Git or backup mutation.

## Terminal reporting

Return separate measured/verified/REPORTED/NOT_OBSERVED fields: validator executable/provenance+version+command/result; native reviewer thread/project/worktree and exact `ACCEPT`; source SHA/tree and one-file diff; admin pre-push branch/ruleset/variable recheck; whether the separately authorized single first-attempt preflight actually ran. If it ran, subsequent independent review of runner metadata and exact two tool hashes may proceed under existing owner packet; no automatic approval of measured hashes.

Current state: `PREFLIGHT_SOURCE_REPORTED_LOCAL`, `BLOCKED_PRE_PUSH_GITHUB_ACTIONS_VALIDATOR_AND_EXACT_SHA_REVIEW`, `A2_BLOCKED_TOOL_IDENTITY`, `A3_NOT_RUN`, `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`, `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
