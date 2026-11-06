# VIP B-first B2 Stage A — explicit owner operational authorization

**Date:** 2026-11-07 (Europe/Istanbul)  
**Status:** OWNER APPROVED — **CONDITIONALLY EXECUTABLE A1–A3**, bounded synthetic-only Stage A; main merges, Gate promotion, real/protected media/models and Stage B/C remain prohibited.  
**Source of approval:** Repository Owner answered **“onaylıyorum”** directly to the explicit request: *“Canonical `cac74495…` tabanından, yukarıdaki A1–A3 aşamalarını; belirtilen dosya sınırları, tek sentetik video, tek kontrollü GitHub CI çalıştırması, tek artifact upload/download ve bağımsız inceleme koşullarıyla yürütmeyi onaylıyor musun?”* This approval applies exactly to the referenced A1–A3 scope, **not** to unspecified future operations.

## Governing frozen sources

- **Canonical:** `Centaurioun/video-intelligence-pipeline`; proposed Stage A feature source base `cac74495d80d9eaa144a12e9aa67eba78ba2f062` (tree `1e851b89273e7ae9a580643b8b704a2d5945c099`).
- Canonical main at authorization check: `3bfcc2ba221b36df6773e630b44479ec961d630a` (tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`), **read-only**.
- **LAB:** `Centaurioun/video-intelligence-pipeline-2`; LAB main `5eab58ea2a5424424cb95f2690654b91395425df`, **read-only**.
- Approved execution plan: LAB `design/vip-bfirst-b2-stage-a-issuance-execution-plan-20261106@c7761a274a432e658df4aee366b50bc900a985a4`, `docs/superpowers/plans/2026-11-06-vip-bfirst-b2-stage-a-issuance-workflow-execution-plan.md`.
- Independent audit: LAB `review/vip-b2-stage-a-operational-readiness-20261107@2795272f7ed95d61fe527d7a99f29abd70202084`, `docs/reviews/2026-11-07-vip-bfirst-b2-stage-a-independent-operational-readiness-audit.md`.
- Both DO_NOT_DELETE backup GitHub releases were checked `immutable=true`.
- The intended Canonical issuance branch `feature/vip-bfirst-video-issuance-20261106` was **NOT_FOUND** at authorization check. Active `protect-main-canonical` ruleset covers **only main**; no effective issuance-branch actor/ref protection has yet been independently observed. These are **hard unresolved pre-push conditions**, not implied grants to skip checks.

## A1 — authorized offline source/test/review preparation (may begin)

In a newly verified **clean isolated Canonical native Codex worktree** from the exact source base, authorize the controlled implementation and prospective behavioral RED/GREEN tests, without generating video or starting a hosted workflow. Exact exclusive source writer paths:

1. `tests/vip_fvs/fixtures/generated_video/build_pinned_video.py`
2. `tests/vip_fvs/unit/test_pinned_video_fixture_issuer.py`
3. `.github/workflows/bfirst-pinned-video-issuance.yml`

The fourth proposed path, `tests/vip_fvs/fixtures/generated_video/issuance-receipt.json`, is **not a pre-run source input**; it is conditionally authorized for a separate **post-run evidence branch** only under A3/receipt review. `independent-pin-record.json` likewise belongs only to an independent reviewer on a separate evidence branch, not the producer/source branch.

Use current Canonical `AGENTS.md`, handoffs, Native Thread Operations Runbook, v5 resource leases and code-owner policies. Verify clean worktree, exact source SHA/tree, exclusive source paths and trusted tool versions. Only mock/fake subprocess/API tests in A1; no actual FFmpeg/FFprobe media processing, model download, provider inference, archive reads or external network operation beyond ordinary read-only Git/GitHub/source review. Test-first RED must be **behavioral**, not missing-pytest or import/collection failure. Then GREEN, current relevant Python 3.11/3.14 tests where available, static GitHub Actions contract checks, secrets and diff checks. Before any push, require a **separate reviewer in an independent clean read-only worktree** on the exact committed producer SHA, specifically reviewing workflow trigger, permissions, full action SHA pinning, first-step identity checks, source/codec/output budgets, and possible automatic execution.

Workflow must be `push`-only on the named issuer branch with narrow path filters; it must not add `workflow_dispatch` or a main-workflow dependency. No production source, existing manifest, CLI, SQLite, temporal legacy or shared gate edits.

## A2 — authorized **conditional** exact-SHA administrator controls, one push/run and one artifact upload

The Owner authorizes the following **only if every pre-push condition independently passes**, in this order:

1. A1 implementation complete and committed locally; exact **final producer SHA** and tree recorded; all allowed diffs, tests, static workflow checks, SHA-pinned upstream actions, limited permissions and independent reviewer acceptance completed. No code change or amend after review; any edit creates a new SHA requiring new exact review and authorization reconciliation.
2. Configure and independently verify **effective issuance-branch creation/update actor/ref controls** specifically for `feature/vip-bfirst-video-issuance-20261106`, through an authorized repository administrator. The existing main-only ruleset does not suffice. Do not invent an effective one-actor restriction when GitHub capabilities cannot enforce/verify it. If no effective control can be established, **STOP `BLOCKED_BRANCH_ACTOR_CONTROL`, no first push**. Do not relax Canonical main protection or alter unrelated branches/settings.
3. Set and independently read back the non-secret repo Actions variable `BFIRST_B2_EXPECTED_PRODUCER_SHA` equal to the exact reviewed 40-character producer commit, under the authorized administrator. Missing/inconsistent readback blocks push. Do not print credentials or add high-privilege token permissions.
4. Recheck Actions settings/retention/actor privileges, event selection, workflow syntax and exact branch absence or safe expected state; require **branch/path-filtered push** and first-step refusal on repository/event/ref/workflow_ref/`github.sha`/`github.workflow_sha`/`run_attempt=1` mismatch **before checkout and source execution**. Branch/path filters and in-workflow guards are not by themselves independent authentication.
5. Only then permit **one normal non-force push** of the exact reviewed commit to the named feature ref. This push automatically triggers the issuance workflow; it must not be used as an experiment to discover whether protection works. No repeat push/re-run/retry or silent fallback. Any unintended run is separately reported and not accepted.
6. The one bounded GitHub Actions run may use `ubuntu-24.04` and already-present/approved FFmpeg and FFprobe only, after explicit measured executable identity versus approved tool boundary. No package install, unreviewed tool substitution, protected/real video input, other archive data, model/provider, arbitrary URL/input file, secrets or unrelated egress. Use only fixed generated lavfi source, single output `bfirst_tiny_video_v1.mp4` with target **64×64, 10 seconds, CFR 4/1, 40 frames, one video/no audio, proposed MPEG-4 Part 2 codec**, maximum **65,536 raw bytes**; tightly bounded timeout/CPU/file/threads under current v5 resource policy. Runtime properties remain `NOT_OBSERVED` until measured; failures are fail-closed.
7. Allow **exactly one artifact upload**, name `bfirst_tiny_video_v1`, containing exactly the one approved MP4 member, finite proposed retention 90 days subject to current verified repo setting. Do not upload receipts as extra members or commit generated binary media into Git. Record GitHub run/job/artifact ID and ZIP archive digest separately from raw MP4 digest.

If tool version/code SHA, effective branch controls, trust anchor, artifact policy, finite limits or actual source admissibility cannot be proved, **STOP before affected operation** and report the concrete `BLOCKED` condition. Do not broaden the task to unblock it automatically.

## A3 — authorized **conditional** independent artifact review and evidence records

After a successful, exact-SHA-approved A2 producer run:

1. A **different read-only native reviewer** (not producer/receipt author) independently verifies GitHub run/ref/event/workflow SHA, run attempt, job ID, artifact ID/name, artifact DIGEST `sha256:`, `expired=false`, `expires_at` and retention. The issuer's receipt is untrusted until independently matched.
2. Authorize **one bounded artifact download** by exact ID, with read-only Actions scope; verify ZIP archive bytes/digest, exactly one safe regular member named `bfirst_tiny_video_v1.mp4` (no extra/path traversal/symlink members), extracted raw MP4 SHA-256/size, independent bounded FFprobe and full decode, measured absolute video stream index, source integer PTS and rational timebase, media and FFmpeg/decoder identities. No protected media or external provider.
3. Receipt recorder may commit `tests/vip_fvs/fixtures/generated_video/issuance-receipt.json` to a **separate evidence-only branch**; independent artifact reviewer may commit `tests/vip_fvs/fixtures/generated_video/independent-pin-record.json` on a separate evidence-only branch. The producer commit/branch is **never amended** to insert runtime IDs. No unreviewed extra source/file path. Never confuse producer measurements with independent acceptance.
4. If artifact, digest, retention, decode, independent roles or exact identity cannot be verified, fail closed, record `PARTIAL/BLOCKED`, no pin adoption and no automatic reissue.
5. Independent pin record is a **candidate only**. Acceptance for Stage B closed-manifest registration remains a distinct owner-reviewed decision with exact artifact evidence; **Stage B/C are NOT AUTHORIZED** here.

## Global guardrails

No Canonical/LAB main changes/merge, no integration PR, no force push/reset/clean/destruction, no prior dirty worktree mutation, no backup edits, no production provider/model/archive media, no Gate promotion, no real editing/render/export/QC, no unrelated branch/ruleset or secret changes. The earlier repository may have historical baseline test failures; do not imply all-green without rerun. Source PTS/timebase must be measured; never infer VFR frame positions using nominal FPS; semantic `POINT` is nonbinding and legacy `+1s` remains untouched.

No claim of indefinite artifact retention, independent same-user tamper resistance, proof of media origin solely from a self-authored grant/receipt, or successful strict video E2E from issuance alone. Report each gate separately with exact SHA/ref, tests, review and APIs; distinguish `MEASURED`, `MATCHED`, review assertions and `NOT_OBSERVED`.

**Terminal owner status:** `VIP_BFIRST_B2_STAGE_A_A1_A3_OWNER_OPERATIONALLY_APPROVED_CONDITIONALLY`.  
**Pre-push gate:** `A2_BLOCKED_UNTIL_ACTOR_REF_GUARD_AND_EXPECTED_SHA_PROVEN`.  
**After actual independent pin:** `STAGE_A_ARTIFACT_PIN_CANDIDATE_ONLY`; Stage B/C still blocked.  
**Invariants:** `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`, `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
