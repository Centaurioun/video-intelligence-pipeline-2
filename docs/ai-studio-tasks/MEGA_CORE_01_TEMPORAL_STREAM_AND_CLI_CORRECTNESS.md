# MEGA-CORE-01 — Source PTS, Video Stream Identity, Semantic Timing and CLI Exit Correctness

**Status:** OWNER-AUTHORIZED LAB CODE AUTHORING PACKET — NOT EXECUTED  
**Date:** 2026-11-06  
**Work repository:** Centaurioun/video-intelligence-pipeline-2  
**Work branch:** existing main, Google AI Studio direct pull/push (no PR, new branch or repository)  
**Baseline LAB main at packet preparation:** 324f6814b9b97e5505e592e9c5d41b3a4c49b532  
**Canonical reference, STRICTLY READ ONLY:** Centaurioun/video-intelligence-pipeline at 3bfcc2ba221b36df6773e630b44479ec961d630a  
**Implementation executor:** Google AI Studio (Python source/test authoring only; no genuine pytest claim)  
**Verification executor:** Codex on local checkout (Python 3.11/3.14, real pytest and hosted CI)  
**Next packet:** CORE-02 unified report/CLI, explicitly out of scope here.

## 0. Mission and success boundary

Repair four source-inspected correctness risks in the existing single-video semantic-retrieval path, using existing modules and interfaces. Do not build a new application. This packet is for code authoring, not authentic video/model evaluation, and completion does not imply CORE_CLI_PRODUCT_COMPLETE.

Four targets:
1. Recover and validate sampled PTS with a non-unit rational timebase and the FFmpeg filter's actual timing semantics.
2. Preserve the absolute video stream index from ffprobe and bind decoding/samples to that selected stream.
3. Bind approximate semantic candidate position to trustworthy numeric hit PTS/timebase; do not reset string timestamps to 0–1 s.
4. Report a nonzero CLI exit status when index-local returns a failed source count, while preserving informative machine-readable JSON.

Existing semantic retrieval, local model interfaces, Gate-3 refinement and source policies must be reused. This is not a scene-captioning, benchmarking, UI, real-media pilot or export task.

## 1. Preflight: source authority and anti-stale rules

1. Pull current LAB main in the existing AI Studio workspace. Record its actual SHA if Git metadata is available. If unavailable, record NOT_OBSERVED; do not invent an SHA. Inspect whether any of these four fixes already exists. Do not overwrite newer work with the historical baseline listed above.
2. Read LAB AGENTS.md and docs/INDEX.md as needed, then the exact files and tests in Section 2. Previous MEGA task documents are historical context, not commands to replay or grounds to add their workstreams.
3. Inspect imports, callers, data contracts and negative paths before editing. Look specifically at FFmpeg showinfo timebase/PTS semantics, ffprobe stream index, SourceIndexResult/IndexSummary, SearchHit fields and real_source_service review-bundle validation.
4. Baseline provenance: LAB and canonical had the same blob for media.py (dcf53b4e12281a3cb6a7310eccee22919ca661d1), real_source_service.py (b9c7f1877ed3f091ee1c2a06f7c2f1e9ededb11d), and indexer.py (c2a9b0a0aa028e33ece1437c4880b0bfb9fb7f69) at audit. LAB CLI has additional synthetic commands that MUST be retained.
5. Do not edit canonical main, unrelated branches, another local checkout or historical audit documents. No destructive Git actions, force push, broad file synchronization, branch deletion or PR creation.

If current LAB source differs materially from the inspected source, reconcile the exact difference first and adjust only the still-relevant repairs. If a governing contract must change, record a BLOCKED_DESIGN_DECISION rather than silently widening authority.

## 2. Source ownership and allowed edits

Primary production files:
- experiments/persistent_local_index/media.py
- src/vip_fvs/real_source_service.py
- src/vip_fvs/cli.py

Permitted directly related regression tests:
- experiments/persistent_local_index/tests/test_media_pts.py
- experiments/persistent_local_index/tests/test_indexer.py
- tests/vip_fvs/unit/test_real_source_service.py
- tests/vip_fvs/integration/test_cli_acceptance.py
- tests/vip_fvs/integration/test_product_index_query.py

Read-only reference files unless a proven narrow dependency requires otherwise:
- experiments/persistent_local_index/indexer.py
- experiments/persistent_local_index/search.py
- experiments/persistent_local_index/model_space.py
- src/vip_fvs/coordinator.py
- src/vip_fvs/real_source_probe.py
- src/vip_fvs/refinement_adapter.py
- src/vip_fvs/review_bundle.py
- existing LAB synthetic batch/three-arm CLI and tests

If a direct dependency requires one additional edit, explain why in the final handoff and keep it minimal. Do not add dependencies, backends, provider integrations or duplicate identity/timestamp engines.

## 3. Repair A — sampling PTS and rational timebase

Observed source: media.py sample_one_pass currently calculates integer PTS as round(pts_time * info.timebase_den). This is only justified when the applicable timebase numerator is 1.

Required behavior:
- First establish whether showinfo pts/pts_time and its link timebase are identical to the selected source stream's PTS/timebase at this point of the filter chain. Inspect how the FFmpeg filter may rebase time, and require a proven mapping instead of assuming equality.
- Compute or validate native PTS using both rational numerator and denominator when the mapping supports it. No seconds multiplied by nominal FPS and no VFR frame-number inference.
- Keep emitted image and reported presentation timestamp attributable to the same selected decoded frame.
- Account explicitly for fractional ticks/rounding tolerance, negative/zero-origin timing and malformed or missing timebases; refuse unprovable exact source-native timestamps instead of inventing them.
- Retain read-only source media. Avoid broad rewrites of the one-pass decode path or new full-frame enumeration.

Author targeted regression fixtures/tests for ordinary numerator 1, numerator != 1, ambiguous filter/source timebase, negative/start-offset PTS where supported, and CFR/VFR ordering. If the filtered frame's original source PTS cannot be proven with the current machinery, STOP that subpart as a documented interface blocker instead of issuing a falsely exact tick.

## 4. Repair B — absolute stream identity

Observed source: probe_stream selects video v:0 but returns StreamInfo(stream_index=0), which may not be the absolute container stream index.

Required behavior:
- Extract the actual ffprobe stream index, not the relative v:0 ordinal. Handle missing, invalid or inconsistent index as a refusal.
- Ensure the FFmpeg decoding selection and the returned stream metadata refer to the same stream. An explicit FFmpeg -map may be justified; verify its effect on filter output and sample ordering.
- Persist the same real absolute stream index through existing index metadata and do not confuse ffprobe index with ISO-BMFF track_ID.
- Test video at stream 0, audio stream 0/video stream 1, multiple video streams with explicit selection behavior, and missing index.
- Preserve compatibility unless a wrong old test expectation must be corrected. Do not change project-wide stream identity contracts or claim adopted A-7 positive track mapping.

## 5. Repair C — semantic candidate timing

Observed source: real_source_service._candidate_from_hit assigns start=0.0 whenever hit.timestamp_human is a string, so different actual matches can be reported as the same 0–1 second candidate.

Required behavior:
- Prefer hit numeric PTS and declared rational timebase, checked against the selected measured source stream, with safe numeric and origin handling. A human timestamp is display text, not authoritative parsing input.
- Place candidates at the correct approximate source-relative temporal position. If policy provides a proven coarse-window width, use it; otherwise do not invent exact one-second coverage.
- Keep candidate semantics MATCHED, binding_eligible=false and separate from MEASURED authoritative refinement. Never promote candidate_seconds to source-native exact edit boundaries.
- Preserve existing candidate/review-bundle schema and validated source-identity/timebase refusal paths. No silent fallback to zero on absent or invalid timing.
- Add tests with two separate nonzero positions, a nonunit timebase, wrong/missing timebase, mismatched source/stream, and malformed PTS. Preserve current error priority where externally observable.

## 6. Repair D — index-local CLI exit status

Observed source: coordinator.index_local_source returns an IndexSummary-derived JSON map with failed count, but vip_fvs.cli.main returns 0 unconditionally for index-local/query-local/query-multi.

Required behavior:
- For index-local only, return nonzero on a failed source count. Keep exactly one parsable JSON status/summary output so automation can inspect failures.
- Preserve legitimate success for indexed, skipped-unchanged and reused-duplicate source dispositions.
- Do not change query-local/query-multi exit behavior or LAB-specific query-batch-synthetic/query-three-arm-synthetic commands.
- Add fresh-process (or truly equivalent) deterministic tests for failed > 0, successful indexing, skipped/reused and an upstream explicit exception/refusal.
- Do not mask missing evidence or unexpected output shapes as success.

## 7. Evidence discipline and regression method

Use the relevant Superpowers methods, not a ceremonial checklist:
- systematic-debugging for each observed code defect;
- TDD: author a regression expected to fail before implementation; because AI Studio cannot run Python, mark RED_EXPECTED_NOT_RUN and have Codex independently confirm RED/GREEN on the local toolchain;
- verification-before-completion: never claim Python tests, FFmpeg execution, CI or model checks passed without actual observed commands/logs;
- brainstorming only if a new architecture/contract decision truly arises; stop that subpart for explicit Owner review.

Six concise internal refinement checks:
1. Current code and contract inspection.
2. Root-cause and adverse input analysis.
3. Smallest behavior-preserving correction.
4. Compatibility and immutable evidence audit.
5. Regression test coverage and no-fake claims.
6. Final static review and Codex handoff.

Expected later Codex test entrypoints:
- PYTHONPATH=src:experiments:. python -m pytest -q experiments/persistent_local_index/tests/test_media_pts.py experiments/persistent_local_index/tests/test_indexer.py
- PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_real_source_service.py tests/vip_fvs/integration/test_cli_acceptance.py tests/vip_fvs/integration/test_product_index_query.py
- Relevant additional canonical/LAB synthetic suites under Python 3.11 and 3.14 as the verified dependency environment permits.

AI Studio MUST mark these tests NOT_RUN unless it really executes them. Tests added are not equivalent to tests passing. No real/archive media, model load/download, provider call, cloud egress, render/export, Gate promotion or synthetic-as-real claim.

## 8. Direct-main LAB publication and continuation

The Owner uses Google AI Studio directly against LAB main. Preserve this workflow:
- No new repository, feature branch or PR.
- Change only the allowlisted code/tests. Do not replace entire repository exports, .gitignore, historical docs or missing files with stubs.
- If possible, review Git diff / changed-file set and static source compatibility before publishing.
- Normal forward-only commit/push to existing LAB main only when the packet forms one coherent candidate. Record actual commit SHA; otherwise state NOT_OBSERVED.
- If session times out, resume from the latest observed repository/source state and this same packet. Do not restart completed subparts or overwrite independent updates.
- If current LAB main advances unexpectedly, STOP and reconcile; no force push, reset, clean or history rewrite.
- No automatic Canonical transplant, no source/media execution and no CORE-02 work.

## 9. Final handoff (Turkish)

Report concisely:
A. Observed initial LAB ref and exact final pushed commit (or NOT_OBSERVED).
B. Modified files; why each edit was necessary.
C. Each of four defects: root cause, correction and edge-case behavior.
D. Regression test cases authored; explicitly TESTS_AUTHORED_NOT_EXECUTED unless actually run.
E. Preservation of fake/real, source and PTS evidence, CLI and LAB-only commands.
F. Remaining unproven FFmpeg/timebase or data-contract uncertainties.
G. Recommended exact Codex verification commands and likely failing paths.
H. Distinguish SOURCE_INSPECTED from MEASURED and NOT_OBSERVED.
I. Explicitly do NOT claim CORE_CLI_PRODUCT_COMPLETE.

End with exactly:
MEGA_CORE_01_READY_FOR_CODEX_VERIFICATION
