# VIP CORE-01 Temporal Correctness — Canonical Adaptation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended for tightly coupled tasks) or superpowers:executing-plans, subject to Canonical AGENTS.md / Native Codex Portfolio scheduling authority, to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt the LAB CORE-01 source-native PTS, absolute stream identity, candidate validation and CLI failure corrections in Canonical without changing unrelated behavior or weakening Gate-3 temporal authority.

**Architecture:** Patch a narrowly selected set of already-shared Canonical files using the pinned LAB CORE-01 changes as *candidate* evidence, not as wholesale copy authority. Keep existing probe, snapshot, semantic-index, bounded admission and Gate-3 engines unchanged. Preserve or explicitly refuse unresolved legacy semantic intervals rather than fabricating exact cut timing.

**Tech Stack:** Python 3.11 and 3.14, pytest, existing Canonical `vip_fvs` and `persistent_local_index` modules, optional installed FFmpeg/ffprobe for newly generated synthetic CFR/VFR fixtures.

**Spec:** LAB `docs/superpowers/specs/2026-11-06-vip-core01-core02-selective-canonical-integration-design.md` on `design/vip-core01-core02-selective-canonical-integration-20261106` (OWNER APPROVED 2026-11-06); reference LAB CORE-01 tasks `docs/ai-studio-tasks/MEGA_CORE_01_TEMPORAL_STREAM_AND_CLI_CORRECTNESS.md` and `MEGA_CORE_01_CODEX_VERIFICATION_AND_REPAIR.md` at pinned LAB `5eab58ea2a5424424cb95f2690654b91395425df`.

## Global Constraints

- **PLAN ONLY until further explicit owner authorization:** Design approval does not authorize source edits, implementation worktrees, PR, merge, protected media, model loads/downloads, provider calls, cloud egress, render/export or Gate promotion.
- Future implementation target: **Canonical** `Centaurioun/video-intelligence-pipeline`; starting pinned `main@3bfcc2ba221b36df6773e630b44479ec961d630a`. Recheck live main, exact tree, governing contract changes and existing pending candidate branches immediately before execution; if baseline changes, stop for delta reconciliation.
- Candidate source: **LAB** `Centaurioun/video-intelligence-pipeline-2@5eab58ea2a5424424cb95f2690654b91395425df`, never its dirty worktrees. Do not alter LAB `main` or either `DO_NOT_DELETE` backup.
- Use a newly verified **isolated clean Canonical worktree/branch**, owned by exactly one integration writer; use native isolated-worktree support if available. Do not modify existing dirty checkouts or use reset, clean, force push, branch/worktree deletion, history rewriting, or destructive cleanup. No PR/merge until separately authorized.
- Keep canonical `src/vip_fvs/bounded_admission.py`, `_bounded_admission_fs.py`, `source_snapshot.py`, `semantic_index.py`, `real_source_probe.py` and `src/gate3/**` intact.
- Source PTS is an integer bound to absolute selected ffprobe stream index and a positive rational timebase. Never derive VFR frames as nominal FPS × seconds; sample timestamps are not exact event boundaries.
- Preserve evidence classes `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, `EDITORIAL_INFERENCE`; `NOT_OBSERVED` is an availability state, not evidence class.
- Existing Canonical `AGENTS.md` / portfolio dispatch / exclusive writer / shared contract rules govern implementation. No artificial parallelism across these tightly coupled shared files. TDD: test RED observed, minimal GREEN, refactor, review, verified commit.

## Review Focus

1. **Audio-first or multi-video container:** an explicitly selected absolute video stream index (`1` or `2`) must never silently become relative `v:0` or match audio; **Task 1 stream selection tests**.
2. **VFR / non-integral filter timebase:** sampled pixels and integer PTS must bind to the same decoded frame with its actual filter/source clock; missing/inconsistent timebase must refuse; **Task 1 generated-media and mocked-filter tests**.
3. **Duplicate/non-monotonic PTS:** identical timestamp without distinct occurrence evidence must not invent a unique edit frame; **Task 2 and Task 3 negative tests**.
4. **Legacy semantic interval with unknown width:** must not manufacture `+1s` or pretend an empty half-open interval is valid; **Task 3 consumer audit and fail-closed tests**.
5. **False-success CLI status:** index failure, invalid source/stream or malformed PTS must exit nonzero and never emit an apparent successful report; **Task 4 subprocess tests**.

---

## Changed-file map and sequencing

| Task | Owner / exact files | Responsibility |
|---|---|---|
| 1 | `experiments/persistent_local_index/media.py` and `experiments/persistent_local_index/tests/test_media_pts.py`, `test_indexer.py` | Deterministic selected stream, sampled-source PTS/timebase |
| 2 | `src/vip_fvs/real_source_service.py`, `tests/vip_fvs/unit/test_real_source_service.py` | Validate candidate source revision/stream/PTS/rank/finite similarity |
| 3 | Same service/test, with relevant Gate-3/review-bundle tests | Resolve legacy semantic width without fabricated cut evidence; hard compatibility stop |
| 4 | `src/vip_fvs/cli.py`, `tests/vip_fvs/integration/test_cli_acceptance.py`, `test_product_index_query.py` | Nonzero failure status; user-visible errors; whole-branch verification |

**Do not add new Gate-3 modules or port `src/vip_lab/**`.** CORE-02 Report V1 typed POINT is implemented in its own separately approved linked plan, not by rewriting every legacy interval consumer here.

### Task 1: Source-native sampling and absolute stream selection

**Files:**
- Modify: `experiments/persistent_local_index/media.py`
- Modify: `experiments/persistent_local_index/tests/test_media_pts.py`
- Modify: `experiments/persistent_local_index/tests/test_indexer.py`

**Interfaces:**
- Preserve/align `probe_stream(video: Path, *, stream_index: int | None = None) -> StreamInfo` with `StreamInfo.stream_index` equal to the **absolute** ffprobe stream `index`.
- Preserve/align `sample_one_pass(video: Path, every_seconds: float, staging_dir: Path, *, stream_index: int | None = None) -> list[SampledFrame]`; each item carries integer `pts` and positive rational `timebase_num/den` for the **same sampled frame**.
- Explicit named refusal when ffprobe/filter timebase absent or inconsistent; do not fall back to nominal FPS or parse truncated human timestamps as exact frames.

- [ ] **Step 1 — Preflight & baseline:** in a newly isolated Canonical worktree, verify exact Canonical starting commit/tree, branch ownership, dirty state, declared expected existing tests and LAB candidate diff. Enumerate available local Python 3.11/3.14, installed FFmpeg/ffprobe without downloading or installing anything. Record unavailable tools as `NOT_OBSERVED`; stop if the starting Git base is different without approved reconciliation.
- [ ] **Step 2 — RED:** add explicit tests `test_audio_first_stream_uses_absolute_ffprobe_index`, `test_selected_nonzero_video_stream_pts_tracks_sample_pixels`, `test_filter_timebase_missing_or_inconsistent_refuses`, and `test_nonuniform_vfr_pts_never_uses_nominal_fps`. Use injected `subprocess.run` fixtures for negative cases and a freshly generated synthetic audio-first CFR/VFR clip for executable timing when FFmpeg is installed. Assert integer PTS, exact rational timebase, correct selected absolute stream and source-unchanged digest.
- [ ] **Step 3 — Confirm RED:** run `PYTHONPATH=src:experiments:. python -m pytest -q experiments/persistent_local_index/tests/test_media_pts.py experiments/persistent_local_index/tests/test_indexer.py`; record the precise new test failures, and differentiate unavailable historical `/tmp/opt_media` fixtures (skips) from failures.
- [ ] **Step 4 — GREEN:** adapt the minimal source behavior from pinned LAB `media.py`, preserving current Canonical callers and public signatures. No broad decoder rewrite. Require exact selected stream and valid filter/source clocks; retain existing sensible fallback only when the authoritative timebase is still proven.
- [ ] **Step 5 — Verify GREEN:** rerun the same focused test files and generated CFR/VFR cases; assert newly required test IDs PASS. Inspect FFmpeg filter trace and ensure no `seconds * nominal FPS` source-frame inference.
- [ ] **Step 6 — Review and commit:** check `git diff --check`, review this task's file diff against source media/policy constraints, commit only three listed files with a CORE-01 media-scoped commit. Record exact commit SHA and test receipts.

### Task 2: Typed retrieval-hit validation in the shared real-source service

**Files:**
- Modify: `src/vip_fvs/real_source_service.py`
- Modify: `tests/vip_fvs/unit/test_real_source_service.py`

**Interfaces:**
- Existing `_candidate_from_hit(hit: Any, probe: RealSourceProbeBinding, attempt_id: str) -> dict[str, Any]` remains an internal consumer interface.
- Hit source SHA/path, optional explicit stream index, integer PTS, rational timebase, finite similarity score and positive integral rank must be verified independently from the actual probe; no human timestamp as exact frame authority.

- [ ] **Step 1 — RED:** add unit tests `test_candidate_refuses_foreign_source_or_stream`, `test_candidate_refuses_missing_or_negative_pts`, `test_candidate_refuses_nonfinite_score_and_invalid_rank` and `test_candidate_uses_probe_native_rational_pts_not_human_timestamp`. Use generated payloads/`RealSourceProbeBinding` and assert named `RealSourcePreparationRefusal` on invalid combinations.
- [ ] **Step 2 — Confirm RED:** run `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_real_source_service.py` and capture actual failing IDs before any source changes.
- [ ] **Step 3 — GREEN:** minimally reconcile LAB CORE-01's candidate-source/stream/PTS/score checks into the current Canonical `real_source_service.py` without copying unrelated behavior. Keep `evidence_class="MATCHED"` and `binding_eligible=False` for semantic relevance. Keep measured sample PTS in its own source-native domain.
- [ ] **Step 4 — Verify and commit:** rerun focused service tests plus `tests/vip_fvs/adversarial/test_temporal_authority.py` and `tests/vip_fvs/integration/test_real_source_prepare.py`. If existing temporal tests break, use `systematic-debugging` before making a fix. Review then commit only the service and test file, with explicit SHA.

### Task 3: Legacy semantic interval compatibility stop

**Files:**
- Inspect before any edit: `src/vip_fvs/real_source_service.py`; `src/vip_fvs/review_bundle.py`; `src/vip_fvs/real_plan.py`; `src/gate3/**`; relevant Gate-3 temporal tests.
- Modify **only if consumer audit proves compatibility**: `src/vip_fvs/real_source_service.py` and `tests/vip_fvs/unit/test_real_source_service.py`.

**Interfaces:**
- LAB CORE-01's `end=start` with `half_open` and original Canonical's invented `end=start+1.0` are both unacceptable as authoritative event intervals when width is absent.
- The approved new Report V1 uses a typed nonbinding `POINT` in CORE-02; Gate-3's nonempty source-native half-open interval contracts remain unchanged.
- For the **existing legacy prepare consumer**, the conservative proposed refusal is `SEMANTIC_WINDOW_WIDTH_NOT_OBSERVED` when an interval is required and no validated positive coarse width exists. This named refusal is a **candidate**; do not introduce it if an existing adopted schema requires a separate versioned decision.

- [ ] **Step 1 — Audit:** search and inspect every reader of `semantic_interval`/`_candidate_from_hit` and the source of coarse-window width. Record whether any legacy consumer assumes an interval unconditionally, how it validates empty intervals, and any exact contract conflicts.
- [ ] **Step 2 — RED:** add `test_unknown_semantic_width_never_creates_one_second_interval`, `test_zero_width_half_open_not_considered_valid_event` and `test_known_coarse_width_is_match_only_nonbinding`. Verify failures against the unmodified inherited implementation; verify any affected existing Gate-3 tests.
- [ ] **Step 3 — HARD STOP RULE:** if implementing named refusal for unknown width would invalidate a frozen Canonical contract or require a new interval schema, STOP Task 3, document `BLOCKED_BY_CONTRACT` with exact consumers and tests, and **do not** alter legacy `prepare_real_source` or invent a substitute. CORE-02's new report may still independently support POINT via its own approved schema.
- [ ] **Step 4 — GREEN only if safe:** require a strictly positive independently supported coarse width for any legacy `semantic_interval`, otherwise refuse with named code. Never emit an empty half-open event or a fabricated +1 second. Do not create a measured edit cut.
- [ ] **Step 5 — Verify and commit when applicable:** focused tests + existing Gate-3/refinement/integration suites, independent contract review. Commit only reviewed files; if STOP triggered, commit no source change and report explicit blocker.

### Task 4: CLI failure status, preservation and CORE-01 acceptance

**Files:**
- Modify: `src/vip_fvs/cli.py`
- Modify: `tests/vip_fvs/integration/test_cli_acceptance.py`
- Modify: `tests/vip_fvs/integration/test_product_index_query.py`

**Interfaces:**
- Existing `vip_fvs.cli.main(argv: Sequence[str] | None = None) -> int`, exact signature to be rechecked before edit; ordinary index/local command failure must return nonzero with stable bounded error, not successful or `all_checks_passed: true` output.

- [ ] **Step 1 — RED:** add subprocess and mocked product-engine tests `test_index_local_failure_is_nonzero`, `test_bad_stream_or_pts_is_not_success`, `test_existing_commands_have_same_parser_contract` and `test_failure_cli_output_does_not_leak_secret_or_protected_path`. Assert no false artifact success receipt and source unchanged.
- [ ] **Step 2 — Confirm RED:** run `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/integration/test_cli_acceptance.py tests/vip_fvs/integration/test_product_index_query.py` and capture failure details.
- [ ] **Step 3 — GREEN:** minimal CLI dispatch/exit-path correction consistent with existing Canonical behavior. Do not introduce CORE-02 or LAB synthetic batch commands in this task.
- [ ] **Step 4 — Focused verify:** rerun all Task 1–4 test files, plus `tests/vip_fvs/integration/test_real_source_prepare.py`, `tests/vip_fvs/adversarial/test_temporal_authority.py`, `tests/vip_fvs/adversarial/test_source_snapshot_temporal_safety.py` and `tests/vip_fvs/unit/test_bounded_admission.py`. Record PASS/FAIL/SKIP by ID, not just a summary.
- [ ] **Step 5 — Whole-branch verify:** run `PYTHONPATH=src:experiments:. python -m pytest -q` (if environment supports the full canonical suite), `python -m compileall -q src/vip_fvs experiments/persistent_local_index`, `git diff --check`, secret check, and relevant Canonical hosted CI on the exact proposed candidate SHA. Preserve and report preexisting missing fixtures and unrelated failure nodes. Never call a partially green suite fully green.
- [ ] **Step 6 — Review and commit:** obtain feature-level independent code review before integration; do not claim implementation completion without fresh source/CI evidence. Normal push to a separately authorized Canonical candidate branch only. **No direct Canonical main write or merge.**

## Exit condition and handoff to CORE-02

A successful CORE-01 candidate has exact reviewed source SHA, test-first receipts, no protected operations, no new provenance/cut claims, no changed Canonical-main or backup refs, and a clear legacy interval disposition `RESOLVED` or `BLOCKED_BY_CONTRACT`. If Task 3 is blocked, CORE-02 can proceed only where its new typed POINT report does not invoke the unsafe legacy consumer. It may not silently claim the entire CORE-01 behavioral surface complete.

**Owner's design approval is NOT execution approval.** This plan itself is pending separate plan review and explicit source/branch authorization. All later Gate/model/real-media work remains independently gated.
