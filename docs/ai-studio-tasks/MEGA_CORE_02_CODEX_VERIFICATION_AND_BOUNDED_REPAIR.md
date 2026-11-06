# MEGA-CORE-02 — Codex Independent Verification and Bounded Repair

**Date:** 2026-11-06 (Europe/Istanbul)
**Version:** VIP-MEGA-CORE-02-VERIFY-v1.0.0
**Status:** PENDING / NOT EXECUTED BY THIS PACKET
**Repository:** Centaurioun/video-intelligence-pipeline-2 (LAB only)
**Pinned AI Studio source candidate:** edb7fca5d9d999d0748021b7f001c37cb21353df
**Exact candidate parent:** c13cfdbb367d3bd9875224a71324ef03f387bbef
**Approved design:** QUERY_DRIVEN_SEMANTIC_REPORT_V1
**Governing implementation packet:** docs/ai-studio-tasks/MEGA_CORE_02_QUERY_DRIVEN_SEMANTIC_REPORT_V1.md
**Canonical:** Centaurioun/video-intelligence-pipeline, READ ONLY.

## 0. Independently VERIFIED source/GitHub facts

On 2026-11-06 GitHub confirmed LAB main at edb7fca5d9d999d0748021b7f001c37cb21353df, descended directly from the CORE-02 task-doc commit. Six affected paths, 5,126 inserted lines, zero removed:
- src/vip_fvs/cli.py (+170)
- src/vip_fvs/core_analysis.py (NEW, 1,896)
- src/vip_fvs/core_report.py (NEW, 1,284)
- tests/vip_fvs/integration/test_core_analyze_local_cli.py (NEW, 506)
- tests/vip_fvs/unit/test_core_analysis.py (NEW, 895)
- tests/vip_fvs/unit/test_core_report.py (NEW, 375)

GitHub Actions run 42140265725 is SUCCESS on that exact SHA for Python 3.11 and 3.14. BUT the current workflow tests older Gate/model/product-path suites, not these three new CORE-02 pytest files. This is NOT CORE-02 hosted acceptance.

AI Studio reports Python 3.10.12 py_compile PASS and 3 unittest methods PASS. Source inspection confirms each stdlib unittest wrapper invokes more tests (six report, seven analysis, four CLI scenario functions). This is meaningful local reported evidence, not Python 3.11/3.14 genuine pytest. The claimed AI Studio reference SHA 35a58cf2a732a33cf86de04602efca9b263d3f03 was not found as a LAB GitHub commit; actual parent and history above are independently verified.

Canonical main remained 3bfcc2ba221b36df6773e630b44479ec961d630a. Authentic single-video SigLIP model inference NOT_OBSERVED. Do not promote the CORE product on these data.

## 1. Bootstrap, safety and exact scope

1. Fetch current LAB origin/main non-destructively, verify HEAD/ancestry and the six-file diff, and preserve every dirty checkout, worktree and original commit. Use one clean isolated worktree with controlled writer ownership. If remote advanced, reconcile first; no forced or destructive Git action.
2. Read AGENTS.md, docs/INDEX.md, both CORE-01 task packets, CORE-02 implementation packet, current relevant real_source, source_snapshot, pilot_authorization, persistent_local_index and CLI contracts, and this entire document. Canonical architecture and evidence contracts are read-only reference.
3. Preserve all six src/gate0/media baseline files. CORE-01 is already verified; do not reimplement it.
4. NO protected/real archive source read/hash/copy/probe, model download/load/inference, provider/cloud egress, render/export, production activation, Gate promotion or canonical modification. Generated-only synthetic FFmpeg test media is permitted. Do not invent authorization for real processing.
5. Development source-authorization enforcement is DISABLED_BY_OWNER; it is NOT real-media/model authorization.

## 2. Genuine Python testing BEFORE proposing fixes

Use separately identified Python 3.11 and 3.14 interpreters/environments with bounded existing synthetic dependencies; run exact modules as pytest, not just unittest wrappers:

    PYTHONPATH=src:experiments:. python -m pytest -q \
      tests/vip_fvs/unit/test_core_report.py \
      tests/vip_fvs/unit/test_core_analysis.py \
      tests/vip_fvs/integration/test_core_analyze_local_cli.py \
      tests/vip_fvs/unit/test_real_source_service.py \
      tests/vip_fvs/integration/test_real_source_prepare.py \
      tests/vip_fvs/integration/test_product_index_query.py \
      tests/vip_fvs/integration/test_cli_acceptance.py

    PYTHONPATH=src:experiments:. python -m pytest -q \
      experiments/persistent_local_index/tests/test_media_pts.py \
      experiments/persistent_local_index/tests/test_indexer.py \
      tests/vip_fvs/integration/test_real_source_prepare.py \
      tests/vip_fvs/adversarial/test_real_prepare_plan_authority_v3.py

Run directly related LAB batch and three-arm CLI tests, compileall/import and git diff --check, and bounded generated-only FFmpeg/ffprobe CFR/VFR plus audio-first stream 1/2 selected-stream cases where relevant. Record exact collected, passed, failed, skipped and xfailed counts PER interpreter. State every skipped-fixture reason. Prior CORE-01 counts or hosted legacy status cannot be reused as new CORE-02 PASS evidence.

Unexpected failures: systematic-debugging first, reproduce, add failing regression, apply minimal TDD fix, rerun. Never invent defects or blanket-rewrite the 5,126-line source without evidence.

## 3. Specific source-inspected correctness concerns to verify, not presumed defects

### A. Ranking, counts, index disposition

- Inspect core_analysis.py candidate logic around lines 1615-1637. Persisted scores are rounded to six decimals; sorting uses rounded raw scores at twelve decimals, whereas persistent_local_index/search.py uses actual scores, source digest, exact rational PTS and row IDs. Test near-equal high-precision scores, exact ties and VFR. Reconcile with approved truthfulness and deterministic Top-K contracts only when proven necessary. Do NOT assign probabilistic confidence.
- total_eligible_matches currently uses max(number_of_returned_hits, source_sample_count) when Top-K is filled, but reports zero for empty hits. Establish which observed metric this really denotes; distinguish indexed active sample count, query Top-K hit count and actual eligible matches. Reject unsupported counts and misleading ZERO_MATCH without inventing arbitrary thresholds.
- If index summary has no INDEXED/SKIPPED/REUSED or malformed counts, ensure analysis does not default to a false INDEXED status. Test failed > 0 and incomplete summaries.
- Verify real persistent index use, not only injected stubs: generation manifest, SQLite source_objects/samples/source_locations, first build vs skip/reuse, row/stream/timebase binding, multi-source source identity, different occurrence same SHA, sample and source revision, foreign/stale rows. If impossible, label actual path NOT_OBSERVED.

### B. Authorization, injected runtime, edge cases

- Unauthorized REAL mode must fail before protected bytes/model/index are touched. Test revoked/expired/scope mismatches with mocks. Preserve source snapshot immutable bytes and explicit separate real/fake behavior.
- Investigate broad except TypeError fallbacks for probe/index/query: internal backend TypeError must not lead to accidentally invoked alternate API, a second index operation or a masked root cause. Test first, then bounded repair if necessary.
- Test absent/malformed FFmpeg showinfo filter timebase, non-unit rational timebase, audio-first selected absolute stream index, valid legitimate negative start PTS question and VFR without nominal FPS multiplication. Do not silently extend source support when existing contract forbids it.
- Avoid uncontrolled post-index SQLite metadata mutation or artificial source_revision assignment. Assess current storage/schema contract, concurrency and exact source binding.

### C. Report/evidence/publication integrity

- Report V1 version, canonical digest excluding its own field, POINT without zero-width half-open semantic interval, source PTS rational mapping, distinct MATCHED vs MEASURED assertions, NOT_OBSERVED as availability (not evidence class), no visual captioning or edit boundary, zero hit SUCCEEDED, missing/corrupt index nonzero FAILED.
- One stdout JSON per known analyze-local product invocation, correct status/exit, no partial success artifact, fresh-process success AND failure. Existing commands and CLI parsing must remain unaffected.
- Race-safe no-clobber for identical/different existing output, symlink/path traversal, partial write, restrictive directory permissions and temp cleanup. Assess portable os.link-based publication and TOCTOU on parent path components; mitigate only demonstrated risks, preserve unrelated artifacts.
- CLI generic exception path currently serializes str(exc) into stdout JSON. Test malicious/secret-containing exception text: do not expose credentials, secret values, protected provenance or token material in error messages; retain useful named error codes.
- Validate reported authentic_inference_observed with actual runtime evidence, not a mode flag alone. No real-model execution in this task.

### D. Maintainability, coverage, evidence accuracy

- CORE-02 includes 3,180 lines of two new modules. Request independent review for duplicated engine/probe/authorization functionality and excessive branching. Do not do a cosmetic mass-refactor; propose a focused fix only for proven reliability/security/contract problems.
- Current unittest wrappers deliberately call pytest functions: record genuine pytest collection so wrapper count is not mistaken for number of distinct scenarios. No fixture test may be labeled authentic model inference.
- Query-driven does NOT mean automatic scene captioning or exhaustive event detection. No Gate-3 editorial decision or render is implied.

## 4. Close the verified hosted CORE-02 coverage gap

Current .github/workflows/vip-ai-studio-synthetic-ci.yml Python 3.11 and 3.14 matrix never lists:
- tests/vip_fvs/unit/test_core_report.py
- tests/vip_fvs/unit/test_core_analysis.py
- tests/vip_fvs/integration/test_core_analyze_local_cli.py

After local tests are green, minimally add a dedicated bounded CORE-02 pytest step for both existing Python jobs, with NO real media/model/provider activity. This is a confirmed CI acceptance gap, not authorization for general CI restructuring. Preserve existing receipt jobs and policy.

## 5. Controlled publication, review and completion

- Require independent review of every changed final file, exact scope, safety and output contracts. Classify confirmed defect, disproven concern, NOT_OBSERVED and deferred design issue separately. Do not claim review merely from a Codex success message.
- All applicable local Python 3.11/3.14 tests, source review and secret/diff checks must pass before a LAB main push. Push forward-only, normal, after rechecking latest LAB main; if blocked, preserve exact local repair commit and report PARTIAL. Do not create PR, new repo or bypass rule unless independently authorized.
- After publishing, independently fetch actual LAB final SHA, parent, diff, and GitHub Actions. BOTH hosted jobs must run the new CORE-02 focused tests on the final commit; existing run 42140265725 is NOT sufficient.
- Canonical stays untouched. No authentic real video pilot or local SigLIP execution until separate current owner authorization. CORE_CLI_PRODUCT_COMPLETE remains NOT_VERIFIED.

## 6. Turkish response contract

Return exact initial/final SHAs, changed paths, commands, per-interpreter collected/PASS/FAIL/SKIP counts, test provenance and genuine generated-media FFmpeg results, bug/fix RED-GREEN evidence, independent review, Gitleaks/diff checks, final hosted run ID/HEAD SHA and newly added test step results. Preserve unverified risks and explicit authorization blockers.

End with MEGA_CORE_02_CODEX_VERIFIED only if actual local green, independently reviewed, published and new hosted CORE-02 pytest green; otherwise MEGA_CORE_02_CODEX_PARTIAL. Do not begin canonical transplant.
