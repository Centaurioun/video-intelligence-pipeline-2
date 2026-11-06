# VIP B-first B2 — Stage A issuance preflight and exact owner packet

**Date:** 2026-11-06  
**Current authority:** READ-ONLY SOURCE/CURRENT-CI PREFLIGHT + LAB DOCUMENTATION ONLY. This task does not authorize media creation, FFmpeg/FFprobe invocation, a new executable CI workflow, feature code writes, network artifact upload/download, PR or main merge.  
**Decision anchor:** LAB B2 design `design/vip-bfirst-pinned-synthetic-video-fixture-20261106@4bec4ef197539781c47ae1ea63b7fb4ffcbdb229`. Independent audit `docs/reviews/2026-11-06-vip-bfirst-b2-design-github-actions-dispatch-and-artifact-retention-audit.md` on this branch.  
**Canonical source:** `Centaurioun/video-intelligence-pipeline@cac74495d80d9eaa144a12e9aa67eba78ba2f062`, tree `1e851b89273e7ae9a580643b8b704a2d5945c099`. Protected `main@3bfcc2ba221b36df6773e630b44479ec961d630a`. LAB main `5eab58ea2a5424424cb95f2690654b91395425df`.

## Objective

Propose the exact bounded **Stage A workflow and artifact issuance implementation packet** required to generate ONE synthetic MP4 via a feature-branch CI job, without incorrectly depending on `workflow_dispatch` for a workflow not yet present on the default branch. This is design/routing work to resolve a material deployment-feasibility omission before any source-writing operation.

## Mandatory read-only preflight

1. Inspect live GitHub Canonical and LAB main, B-first and design refs; read `AGENTS.md`, current Canonical project handoffs, resource policy v5, native operations runbook, governing contracts and prior owner B-first decision.
2. Inspect all current `.github/workflows/*.yml` event triggers and branch filters, `tests/gate0/media/generated_media.py` media prohibition, the existing CLI generated FFmpeg/FFprobe test, Canonical `.gitignore`, `src/vip_fvs/trusted_fixture_manifest.py`, `real_source_probe.py` and `core_report.py`.
3. Verify official GitHub Actions event semantics with public official documentation: **new feature-only workflow `workflow_dispatch` cannot be assumed runnable** until on the default branch. Verify `on: push` event to a named dedicated isolated issuance branch. Do not create a workflow on main or a PR to main.
4. Inspect GitHub repo artifact retention and Actions permissions **read-only if API grants access**; if unavailable, mark `NOT_OBSERVED`. Never assert specific retention or privileges from public generic docs.
5. Check whether Actions workflow syntax and Action artifact versions support the proposed content-hash receipts and exactly one uploaded file; pin resolved Action code identity and distinguish ZIP archive SHA256 from raw MP4 SHA256. Treat artifact URL as location, not trust root.

## Required bounded Stage A proposal

- **Worker/branch:** a new isolated native Codex Canonical worker from `cac74495...` with exclusive writer lease after explicit operational authorization; a separate read-only reviewer on an immutable SHA. Proposed branch is a unique `feature/vip-bfirst-video-issuance-20261106` (avoid existing active worktrees).
- **Proposed exclusive future writable paths:** `tests/vip_fvs/fixtures/generated_video/build_pinned_video.py`, `tests/vip_fvs/unit/test_pinned_video_fixture_issuer.py`, `tests/vip_fvs/fixtures/generated_video/issuance-receipt.json` (separate post-run receipt author/reviewer), `.github/workflows/bfirst-pinned-video-issuance.yml`. No other source, model, archive or legacy code.
- **Workflow trigger:** bounded `on: push` filtered to the **single named issuance feature branch**, with reviewed path filters so only the authorized commit initiates issuance. Do not use a novel `workflow_dispatch`-only trigger. Harden `permissions` minimally, restrict `concurrency`, output file paths, job timeout, runner/tool and expected source HEAD.
- **Proposed media:** ONE generated `bfirst_tiny_video_v1.mp4`; 64×64; 10 seconds; CFR target 4/1, 40 frames, one video stream, no audio, decoder-compatible `mpeg4` only if actually supported; raw MP4 maximum 65,536 bytes; no arbitrary URLs, external media, file import, model/provider activity.
- **Test-first:** prospective RED with fake FFmpeg/probe/executable wrappers (argv constraints, refusal of wrong codec/input/duration/output/cap, safe temp root, invalid receipt); GREEN before actual controlled issuance. Tool absence/collection failure is NOT behavioral RED. No downloading/installing runtime dependencies for this preliminary task.
- **Permission boundary:** Stage A future authorization must explicitly permit one bounded FFmpeg/FFprobe generation and inspection on an isolated job, bounded output bytes, GitHub Actions artifact upload and one independent re-download, plus the finite resource and network/retention scope. A broad general future-work approval does not replace a named trust and egress scope.
- **Producer trust/receipt:** The workflow run's source SHA, GitHub event/ref, run and artifact IDs, GitHub-reported ZIP digest, raw MP4 SHA/byte count, measured codec/stream/PTS/timebase, tool identities/version/hash, and retention deadline must be recorded. **Do not self-approve** these results. The separately signed-off pin is created *after* the immutable run/artifact IDs exist; it must not rewrite producer SHA.
- **Independent review:** one reviewer verifies workflow/issuer source before any authorized feature push; after run another distinct review validates artifact ZIP members and digests and performs independently bounded decode/probe. If independent review is unavailable, mark `PARTIAL/NOT_OBSERVED`, never accept self-issued provenance.
- **Failure handling:** no artifact, wrong digest, missing metadata, expired/deleted artifact, source/revision drift, output ceiling failure, codec mismatch, undeclared extra member, symlink/traversal or unsupported runner -> fail closed. No automatic reissuance under same identity; no fallback to B1 without owner-authorized change to no-media-commit policy.
- **Resource:** one bounded HEAVY_CPU issuance worker under resource policy; fixed FFmpeg/FFprobe executable and timeouts chosen after environment inspection, no protected media; no CI job run by this current preflight packet.
- **No Stage B/C:** No trusted manifest registration, CLI `fixture_id` change or production/codepath integration in this packet.

## Deliverable

Create a new **one-file proposal** under LAB `docs/superpowers/plans/` or `docs/superpowers/specs/` in a clean new isolated documentation-only branch; preserve the original B2 proposal and audit unchanged. Include an exhaustive exact future **owner approval request** for media generation, executable/tool identity, new workflow path, artifact upload/download, retention and one-time independent pinning, plus clear deferred implementation acceptance and no-merge status. Use Superpowers brainstorming then writing-plans only after documented approval. Do not create executable workflow files, source generation code or media.

Return in Turkish: exact LAB branch/commit, verified source, dispatch strategy, artifact retention evidence/unknowns, one-time issuer/reviewer roles, independent critique, deferred owner approvals, and blockers.

**Terminal:** `BFIRST_B2_STAGE_A_EXECUTION_PACKET_PROPOSED — OWNER_OPERATIONAL_APPROVAL_PENDING`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
