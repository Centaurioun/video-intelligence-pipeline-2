# VIP — one-run media-free FFmpeg/FFprobe tool identity preflight: execution packet

**Date:** 2026-11-07
**Status:** OWNER-APPROVED CONDITIONAL STRATEGY B PREFLIGHT. Not a grant for production A2 issuance or A3.
**Governing owner record:** Same LAB branch `docs/decisions/2026-11-07_VIP_BFIRST_A2_MEDIA_FREE_TOOL_IDENTITY_PREFLIGHT_OWNER_APPROVAL.md`.
**Preflight design:** LAB commit `58482251020713ccb4053ce14a98506739e3ed27`, `docs/superpowers/specs/2026-11-07-vip-bfirst-a2-ffmpeg-ffprobe-tool-identity-preflight-design.md`.
**Independent feasibility audit:** LAB `89c67a1602442b42887c1328a50be57c3f832e0b`.
**Canonical base:** `cac74495d80d9eaa144a12e9aa67eba78ba2f062` tree `1e851b89273e7ae9a580643b8b704a2d5945c099`, not mutable main. The source's producer candidate `413d032e5635e4d8670e5565856f7fcfcfaca3ff` is LOCAL-ONLY REPORTED; preserve it without publication.

## Work order

**0. Reverify:** GitHub current protected main and B-first refs, named preflight branch absence or existing state, active issuance and other rulesets, Canonical workflow trigger census on current exact source, GitHub action/runner capabilities, connected native tooling and v5 lease. Read Canonical `AGENTS.md`, handoffs, state maintenance and native operations runbook. Avoid local main sync, dirty shared checkout and existing A1 worker.

**1. Offline authoring:** Fresh isolated Canonical native worktree at the frozen base, exclusively own a NEW `.github/workflows/bfirst-tool-identity-preflight.yml`. Suggested branch `design/bfirst-a2-tool-identity-preflight-20261107`. Source must have one `on: push` exact-branch/workflow-only path selection, no `workflow_dispatch`, one job on `ubuntu-24.04`, `permissions: {}`, no checkout/actions/cache/artifact/upload/download/HTTP/credentials or package installation, finite 5m timeout, no matrix. First inline guard must strictly verify repository, event, ref, workflow_ref, workflow_sha, source_sha, expected-source SHA via `BFIRST_B2_TOOL_PREFLIGHT_EXPECTED_SHA`, run attempt 1. Guard runs **before** any binary read or local package query.

**2. Read-only measurement body:** Resolve PATH for both programs deterministically, require regular file target, record symlink/realpath and stat, bounded exact SHA-256/size (cap resource use; document intended max size), UTC time, OS, ImageOS/ImageVersion, package ownership/version where available; reject missing/ambiguous paths, unsafe paths, unreadable files or missing essential image evidence. Do NOT execute either FFmpeg or FFprobe, call external HTTP/cloud API, inspect media, or generate any output MP4. Record `mpeg4 capability=NOT_OBSERVED`. Only bounded Actions job summary/log, not artifact.

**3. Local verification and review:** Confirm a working local actionlint or equivalent GitHub-compatible parser and a prospective red/green workflow-contract validation exercise without running any actual hosted job. No new unapproved tracked test/source path; for local behavior tests of inline guard, use an ephemeral controlled harness outside the tracked source and capture red/green command/output as a durable reviewer-facing receipt without changing the source contract. If a reliable test requires a second tracked file, STOP `BLOCKED_BY_WRITE_SCOPE` and propose an exact test-path amendment; do not invent implicit source authority. Commit the workflow file locally once. Run syntax/diff/secret/native feature verification. Independent reviewer on a fresh clean read-only worktree checks the exact immutable preflight SHA/tree and every condition. Any repair changes SHA and requires fresh exact reviewer.

**4. Admin gate before first push:** Under explicitly authorized owner/admin controls, create an ACTIVE narrowly targeted ruleset for ONLY `refs/heads/design/bfirst-a2-tool-identity-preflight-20261107` with enforced create/update actor restrictions; establish one nominated authorized pusher, verify actor/ref enforcement, no second/update/force push under declared honest-operator scope. Set `BFIRST_B2_TOOL_PREFLIGHT_EXPECTED_SHA` to reviewed commit 40-hex SHA, independently read back. Verify no OTHER Canonical push-triggered, chained or downstream workflow will run on initial branch push. Reinspect current Actions permissions and actor/rerun access, and explicitly record accepted residual public internet and schedule-able rerun. Any requirement not met => `BLOCKED_PREPUSH`; do not push.

**5. One conditional push and runner measurement:** Only if ALL gates pass, ONE normal non-force branch push of exactly the reviewed preflight commit. It triggers one intended first-attempt job. Check actual run event/ref/head/workflow SHA and attempt via read-only API. Fail closed on any mismatch. Do not retry, re-run, amend or second-push. If hosted tools missing or identity evidence incomplete, report `PREFLIGHT_PARTIAL` or `BLOCKED` and stop; don't install packages. If a platform rerun is scheduled, guard must abort **before any binary read**; record it as unauthorized attempt, not extra measurement.

**6. Independent evidence and terminal:** An independent reader verifies exact run/log source, numeric job ID if available through read-only API, ImageOS/ImageVersion, paths, file sizes, two 64-hex SHA-256, package evidence/limitations and no binary executions/media/artifact. The reviewer writes a documentation-only LAB audit in a new isolated branch (not Canonical main/producer or existing LAB main). Do not set the later `BFIRST_B2_APPROVED_FFMPEG_SHA256` / `BFIRST_B2_APPROVED_FFPROBE_SHA256` yet; the two resulting concrete values must be presented for separately approved trust/expiry and later admin variable binding. Preserve the earlier A1 producer commit and issuance branch absent.

## Terminal status criteria

- `BFIRST_B2_TOOL_PREFLIGHT_SOURCE_VERIFIED`: local source+test+independent code reviewer valid, even if no push.
- `BFIRST_B2_TOOL_PREFLIGHT_MEASURED_PENDING_OWNER_HASH_APPROVAL`: only with one actual authorized first-attempt measurement, exact tool SHA pair independently corroborated and reviewer evidence. This is **not** A2 issuance.
- Otherwise `BLOCKED_<named_gate>` with the stage reached; do not imply completed measurement.
- Until a subsequent exact owner digest approval, `A2_BLOCKED_TOOL_IDENTITY`, `A3_NOT_RUN`, `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` and `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.

No main writes/PR/merge, no protected/real archive, no genuine model/provider, no FFmpeg/FFprobe execution, no media generation or upload/download, no Stage B/C or Gate promotion, no destructive Git or backup changes.
