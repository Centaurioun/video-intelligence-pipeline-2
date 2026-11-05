# MEGA-CORE-01 — Codex local Python verification and bounded repair

**Date:** 2026-11-06  
**Status:** PENDING / NOT RUN BY THIS PACKET  
**Repository:** Centaurioun/video-intelligence-pipeline-2 (LAB)  
**Exact AI Studio candidate HEAD:** `44d4e0a6c80c924b837303a34ff373fc0d2a14cc`  
**Input specification:** `docs/ai-studio-tasks/MEGA_CORE_01_TEMPORAL_STREAM_AND_CLI_CORRECTNESS.md`  
**Canonical:** Centaurioun/video-intelligence-pipeline, STRICTLY READ-ONLY  
**Goal:** Verify, and if necessary minimally repair, the eight-file CORE-01 candidate. Do not start CORE-02.

## 1. Confirm remote delivery first

The AI Studio snapshot report says `.git` was absent and CLI push was blocked. This does NOT mean its GitHub UI sync failed: GitHub independently showed the exact eight changed production/test files on LAB `main@44d4e0a6`, descended forward from packet commit `058053e5`.

Before any work, verify live LAB `origin/main`, exact candidate SHA and changed-file diff. If the ref has moved, inspect and reconcile instead of resetting or overwriting. Preserve all existing dirty checkouts (canonical checkout had ~160 tracked modifications and LAB checkout had ~2 at the previous read); use a clean isolated worktree or Codex-native isolation. No hard reset, git clean, rebase, force push, branch/worktree destruction, or unrelated cleanup.

Do not request another AI Studio implementation or re-upload the eight files when they are already present on remote.

## 2. Scope and baseline

Eight modified files in candidate commit:

- `experiments/persistent_local_index/media.py`
- `experiments/persistent_local_index/tests/test_media_pts.py`
- `experiments/persistent_local_index/tests/test_indexer.py`
- `src/vip_fvs/cli.py`
- `src/vip_fvs/real_source_service.py`
- `tests/vip_fvs/integration/test_cli_acceptance.py`
- `tests/vip_fvs/integration/test_product_index_query.py`
- `tests/vip_fvs/unit/test_real_source_service.py`

Existing hosted GitHub Actions run `42127295591` reported SUCCESS on Python 3.11/3.14, but its Gate-1 model-free selection does not exhaustively include the new PTS, indexer, real-source-service and CLI regression suites. Never substitute this general CI success for the focused acceptance below.

## 3. Required genuine local verification

Use the local, already available Python/pytest environments for 3.11 and 3.14 where possible. Do not download models, install packages without authorization, access protected video, or call a provider. Environment limitations must be reported rather than hidden.

Start with:

```bash
PYTHONPATH=src:experiments:. python -m pytest -q \
  experiments/persistent_local_index/tests/test_media_pts.py \
  experiments/persistent_local_index/tests/test_indexer.py \
  tests/vip_fvs/unit/test_real_source_service.py \
  tests/vip_fvs/integration/test_cli_acceptance.py \
  tests/vip_fvs/integration/test_product_index_query.py \
  tests/vip_fvs/integration/test_real_source_prepare.py \
  tests/vip_fvs/adversarial/test_real_prepare_plan_authority_v3.py
```

Also run fresh compile/import verification and `git diff --check`. Audit tests' actual collected, passed, failed and skipped counts; historical `/tmp/opt_media` fixtures may be absent. Generate NEW safe synthetic CFR/VFR and nonzero absolute stream-index media using available local FFmpeg/ffprobe when the task/environment permits; never substitute genuine archive footage.

Review all directly dependent tests that mock `ffprobe` or `ffmpeg`: the stricter probe now requires absolute `index` fields and filter timebase data, so older synthetic mocks may need legitimate fixture alignment (not weakening contract tests). Expand from affected tests to the repository's existing relevant smoke lanes. Preserve existing LAB batch and three-arm commands.

## 4. High-priority code review questions

Verify actual behavior, not just test pass counters:

1. Non-unit rational timebase PTS recovery; FFmpeg `showinfo` **input timebase** versus probed stream timebase mapping on generated video. The code checks every captured `config in time_base` occurrence, but also consider the **zero-occurrence** case and whether fail-closed evidence is still established. Avoid trusting missing metadata by default.
2. `-select_streams v:0` and `-map 0:<absolute_index>` reference exactly the same video stream, including audio-first and multiple-video containers. Validate persistence and no stream-index-as-track-ID promotion.
3. `real_source_service._candidate_from_hit` now uses numeric PTS/timebase. When no authorized coarse window is present, it sets `end == start`; determine whether this zero-width interval is appropriate for a half-open **candidate interval**, and whether a timestamp *point* should be represented differently without inventing a duration. Preserve MATCHED/non-binding versus MEASURED.
4. `index-local` returns nonzero for `failed > 0`, missing counts or invalid identities, while retaining exactly one parseable JSON result. Successful indexed/skipped/reused dispositions should remain zero. Verify unchanged other LAB commands.
5. `NEGATIVE_PTS` and `NON_MONOTONIC_PTS` restrictions: identify whether they reject legitimate timestamp layouts in supported codecs; do not silently rescale, clamp or fabricate source PTS.

Any concern not demonstrated must remain a hypothesis, not a declared bug. Use Superpowers systematic-debugging for observed failures, TDD for fixes, request independent code review before declaring ready, and verification-before-completion for every success claim.

## 5. Publication boundaries

If all tests pass and no material defect is found: do NOT manufacture a source change; report ACCEPTED at the verified SHA.

If a real defect is confirmed: apply only the smallest correction and corresponding regression in the isolated LAB worktree. Preserve original task scope and branch history. Forward-only push to LAB main **only** after exact old remote ref/stale-base check and verified tests. No new PR, no force push, no canonical mutation. Do not begin CORE-02.

No actual protected/real media, authentic model inference/download, provider calls, production render/export, Gate promotion or new architecture authority.

## 6. Final response in Turkish

Report: initial and final exact LAB SHA, changed files (if any), Python 3.11/3.14 results, genuine targeted test count and skips, generated FFmpeg fixture findings, confirmed defect corrections, review outcome and hosted CI checks; distinguish SOURCE_INSPECTED, TESTED_SYNTHETIC, NOT_OBSERVED and environment blockers.

End with one of:
`MEGA_CORE_01_CODEX_VERIFIED`  
`MEGA_CORE_01_CODEX_PARTIAL`
