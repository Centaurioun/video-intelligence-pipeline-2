# VIP CORE-01 Stream-Provenance Candidate Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans as appropriate, but **Canonical `AGENTS.md` and its Native Codex Portfolio execution protocol take precedence**. Steps use checkbox (`- [ ]`) syntax and require test-first RED/GREEN evidence for behavior changes.

**Goal:** Fix the verified source-to-`SearchHit` stream-index provenance gap in the existing isolated Canonical CORE-01 candidate, investigate the seven reported Python 3.14 full-suite failures against an exact pinned-main comparator, and obtain independent review without touching legacy interval contracts.

**Architecture:** Carry the already-persisted sample stream index through the read-only `SampleMeta` → `SearchHit` query API and preserve it through reference/optimized/multi-query retrieval. Retain the candidate's strict real-source fail-closed check; do not infer missing stream identity from the probe, source path or request. Keep old review-bundle V1 and its blocked legacy semantic interval separate from future CORE-02's typed `POINT`.

**Tech Stack:** Existing Python 3.11/3.14 Canonical `persistent_local_index.search`, SQLite samples/source_objects schema, `vip_fvs` semantic index/retrieval adapter/real source service, pytest, generated synthetic media with already-installed FFmpeg where available.

**Spec:** `docs/superpowers/specs/2026-11-06-vip-core01-stream-provenance-and-semantic-interval-contract-successor.md` in LAB branch `design/vip-core01-stream-provenance-interval-contract-successor-20261106`, OWNER APPROVED D1/D2/D3 on 2026-11-06 (read exact approved commit SHA from GitHub). Earlier CORE-01 Plan: `docs/superpowers/plans/2026-11-06-vip-core01-temporal-correctness-canonical-adaptation.md` at LAB planning branch `design/vip-core01-core02-selective-canonical-integration-20261106`.

## Global Constraints

- **Authorized:** narrowly scoped CORE-01 stream provenance patch, direct dependent tests/call sites, synthetic tests and pinned-main Python 3.14 failure comparison, isolated candidate successor branch/worktree, non-force push, independent review. **Not authorized:** legacy V1 interval schema rewrite, CORE-02 implementation, PR, Canonical main merge, protected/real archive, genuine model loads/downloads, provider/cloud inference, production render/export, Gate promotion, destructive Git.
- Canonical frozen main `3bfcc2ba221b36df6773e630b44479ec961d630a`, tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`; immutable predecessor CORE-01 candidate `7c167486d66e076708fd490964f5e4d3c06aa20b`, tree `9092a6044d3ae67993dbb62f96ad1fefecaca4f4`. LAB exact reference `5eab58ea2a5424424cb95f2690654b91395425df`. Verify remote identities again before any write.
- Create a **new clean isolated Canonical successor worktree and unique branch at exact candidate SHA**; do not alter the existing dirty canonical checkout, existing CORE-01 worker worktree, its uncommitted `.gitignore`/`.ignore`, local `main`, LAB, `main` or backups. If native thread/worktree binding is unavailable, stop `BLOCKED_WITH_EVIDENCE`; do not fall back to unverified shared checkout. Follow current `AGENTS.md`, native thread runbook and exclusive writer ownership rules.
- All current Canonical ABI/schema/privacy/Gate constraints remain governing. No changes to SQLite on-disk table schema and no unverified introduction of custody/occurrence claims. No attempt to fix unrelated pre-existing full-suite failures without separate authorization.
- Preserve `MEASURED` versus `MATCHED` and selected **absolute video** stream identity with exact rational PTS/timebase. Missing/mismatched metadata must refuse; do not substitute a default video stream index.
- Model/provider operations remain blocked; use tests with synthetic data only. GitHub code sync and hosted synthetic CI are within approved development scope, but do not assert CI covers tests it did not run.

## Review Focus

1. Production sample SQL has `samples.stream_index` but `SearchHit` lacks the field; **Task 1** must demonstrate a genuine persisted Query `SearchHit` carries the same measured selected stream without guessing.
2. Reference, optimized and multi-query search may reconstruct hits in several places; **Task 1** must cover all paths and identical score/rank/tie order.
3. Multiple source occurrences of identical bytes need independent custody authorization; **Task 2** refuses foreign occurrence rather than treating digest+stream equality as authority.
4. Python 3.14 seven failures might be environmental or actual regressions; **Task 3** must reproduce with matched baseline before classification.
5. Legacy V1's invented `+1s` interval is not a measured event; **Task 4** keeps its blocker explicit, never claiming full CORE-01 verified.

---

### Task 0: Current Git/contract and isolated executor admission

**Read-only inputs:** `AGENTS.md`, `docs/INDEX.md`, four `docs/project/` handoffs, `CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md`, current Portfolio policy, current report/spec/plan, exact current GitHub refs.

- [ ] **Step 1 — Verify Git:** `git rev-parse HEAD`; `git rev-parse 'HEAD^{tree}'`; `git status --porcelain=v1 --untracked-files=all`; `git worktree list --porcelain`; `git merge-base --is-ancestor 3bfcc2ba221b36df6773e630b44479ec961d630a 7c167486d66e076708fd490964f5e4d3c06aa20b`. Confirm GitHub current Canonical main and predecessor feature branch SHAs.
- [ ] **Step 2 — Isolate:** use verified native thread/worktree capability to start a *new* clean successor at exact `7c167...`, suggested `feature/vip-core01-stream-provenance-remediation-20261106`. Bind unique branch only under serialized Worktree Admin authority. Prove source path, common Git dir, clean state, base ancestry, no competing writer/lease/contract mismatch before edits.
- [ ] **Step 3 — Baseline:** capture Python 3.11/3.14 and pytest/FFmpeg versions, existing focused tests, selected test command/fixtures and initial candidate failures. No dependency download or model execution implied by setup.

### Task 1: Propagate persisted sample stream index without changing schema

**Files:**
- Modify: `experiments/persistent_local_index/search.py`
- Test: `experiments/persistent_local_index/tests/test_search.py`
- Test: `experiments/persistent_local_index/tests/test_search_materialization.py`
- Test: `tests/vip_fvs/unit/test_retrieval_adapter.py`
- Test: `tests/vip_fvs/integration/test_product_index_query.py`
- Test: `tests/vip_fvs/unit/test_real_source_service.py`
- Read-only references: `experiments/persistent_local_index/storage.py`, `indexer.py`, `src/vip_fvs/semantic_index.py`, `retrieval_adapter.py`, `real_source_service.py`.
- Additional source changes **only** if directly unavoidable for lossless stream propagation and recorded in a scope/diff receipt; otherwise stop and request owner ruling.

**Interfaces:**
- Existing frozen dataclasses `SampleMeta`, `SearchHit` remain backwards-compatible with synthetic constructors; add optional **trailing** `stream_index: int | None = None` to both without pretending absent legacy values are verified.
- `_ROW_METADATA_SQL` selects actual `samples.stream_index`, `_sample_meta_from_row` binds it, and all `SearchHit` constructions in `exact_top_k`, `exact_top_k_indexed` and `query_generation` carry it unchanged.
- Query ordering and Top-K oracle equivalence remain byte-for-byte value-equivalent except for the additive stream field. Any inconsistency between source object/sample/selected probe must refuse at the responsible boundary; no silent substitution with probe identity.

- [ ] **Step 1 — RED:** test `test_sample_meta_retains_persisted_nonzero_stream_index` with real synthetic SQLite rows and an audio-first video-stream index 1 or 2. Test `test_reference_and_optimized_topk_preserve_stream_identity` and `test_multi_query_materialized_hits_preserve_stream_identity`; verify exact rank/score/row/PTS unchanged. Test `test_default_real_source_prepare_receives_stream_bound_hit` using production query seam + injected synthetic model, source and probe (no real model), not only handwritten hit objects.
- [ ] **Step 2 — Confirm RED:** `PYTHONPATH=src:experiments:. python -m pytest -q experiments/persistent_local_index/tests/test_search.py experiments/persistent_local_index/tests/test_search_materialization.py tests/vip_fvs/unit/test_retrieval_adapter.py tests/vip_fvs/integration/test_product_index_query.py tests/vip_fvs/unit/test_real_source_service.py`. Capture explicit new test failure IDs and expected reasons.
- [ ] **Step 3 — GREEN:** minimum additive dataclass+SQL+constructor wiring. Verify actual `samples.stream_index` is an integer and not implicitly trusted when inconsistent with independently verified source/stream metadata. Leave on-disk storage schema untouched.
- [ ] **Step 4 — Verify GREEN:** rerun exact RED command plus `experiments/persistent_local_index/tests/test_storage.py`; confirm reference/optimized/multi-query ranking and legacy synthetic fixtures still pass. Add negative tests `test_wrong_stream_index_refuses`, `test_missing_stream_index_refuses_real_prepare` and `test_equal_digest_different_occurrence_not_silently_authorized`. If a test demonstrates a broader source-occurrence schema defect, document and STOP rather than invent source identity.
- [ ] **Step 5 — Commit:** `git diff --check`; targeted review; commit only approved files and record exact SHA, blob paths and RED/GREEN receipts.

### Task 2: Product-path acceptance and negative source/stream provenance

**Files:** existing focused tests in Task 1, plus `tests/vip_fvs/integration/test_real_source_prepare.py` **only if required** to prove full persisted-hit path; otherwise no new source owner.

- [ ] **Step 1 — RED:** demonstrate the pre-fix candidate rejects normal persisted `SearchHit` lacking stream (proof of original regression). Then exercise full synthetic persisted-index → product query → real-source validation path, including stream index 1/2, rational PTS and source revision. Verify mismatch/missing identity, foreign or ambiguous occurrence and invalid PTS fail closed.
- [ ] **Step 2 — Confirm expected regression fails before fix:** capture exact failing integration test before Task 1 GREEN; if already addressed with Task 1 RED test, reference that receipt rather than undoing code.
- [ ] **Step 3 — GREEN / no needless code:** reuse Task 1's propagation. Preserve `src/vip_fvs/real_source_service.py::_candidate_from_hit` strict stream validation and `MATCHED` nonbinding output. Do not add probe-derived fallback and do not modify legacy interval output.
- [ ] **Step 4 — Verify/commit:** test with `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/integration/test_real_source_prepare.py tests/vip_fvs/unit/test_real_source_service.py tests/vip_fvs/test_stream_identity_bind.py`; commit only newly necessary test edits if any.

### Task 3: Compare Python 3.14 failures against clean pinned Canonical main

**Files:** test logs/receipt only; no source edits. Keep the comparator in an isolated *read-only* clean Canonical base worktree or a verified native test runner pinned to `3bfcc2ba...`. Never run tests in the dirty checkout.

- [ ] **Step 1 — Match environments:** record exact Python version, dependency versions, environment variables excluding secrets, optional FFmpeg availability, fixture presence and full-suite invocation for both candidate and pinned main.
- [ ] **Step 2 — Run candidate:** `PYTHONPATH=src:experiments:. python -m pytest -q` on the successor candidate; enumerate every failed node, stack trace, and skip reason.
- [ ] **Step 3 — Run comparator:** run *identical* command, runtime and dependencies at pinned Canonical main; capture exact failure node list and traces. If matched environment cannot be established, classify `UNRESOLVED_ENVIRONMENT` instead of pre-existing.
- [ ] **Step 4 — Classify:** per failing test, `PRE_EXISTING`, `CANDIDATE_REGRESSION`, `ENVIRONMENT_DIFFERENCE` or `UNRESOLVED`, with trace and SHA. Fix only direct in-scope stream-provenance regressions; anything else is bounded follow-up not silently expanded work.
- [ ] **Step 5 — Preserve:** document paired-run receipts in final handoff and, if a preauthorized task-local ledger path exists, commit only such a plan-bounded receipt; no unrelated test/source changes.

### Task 4: Certification boundary and independent review

**Files:** no new broad source owner; review final successor candidate diff plus test receipt.

- [ ] **Step 1 — Scope:** `git diff --name-status 7c167486d66e076708fd490964f5e4d3c06aa20b...HEAD`; verify existing Canonical main, LAB main and backups unchanged; existing dirty and earlier CORE-01 worktree untouched.
- [ ] **Step 2 — Suite:** run targeted `search`, `storage`, `retrieval_adapter`, `real_source_prepare`, `real_source_service`, stream tests, Gate-3 temporal tests, full suite where available; repeat on Python 3.11/3.14 when possible. `python -m compileall -q src/vip_fvs experiments/persistent_local_index`; `git diff --check`; relevant secret check. Record failures/skips rather than invent all-green.
- [ ] **Step 3 — CI:** push only successor feature branch normally; run available GitHub synthetic smoke (exact final candidate SHA). State test-selection limitations, no inference that broad suite passed.
- [ ] **Step 4 — Independent review:** submit exact successor SHA to fresh reviewer; require assessment of production `SearchHit` provenance and matching, backward compatibility, source-occurrence handling and Gate-3 temporal constraints. `NEEDS_WORK` blocks any candidate acceptance; respond using receiving-code-review and verify fixes at newly reviewed immutable SHA.
- [ ] **Step 5 — Handoff:** Record terminal state **`STREAM_PROVENANCE_CANDIDATE_VERIFIED` only if production-path source/stream tests, regression assessment and reviewer evidence warrant it**; otherwise `STREAM_PROVENANCE_CANDIDATE_PARTIAL`. In **all cases `CORE01_CANONICAL_CANDIDATE_PARTIAL`** until legacy V1 Task 3 contract debt is independently resolved. Do **not** merge main, create an integration PR, or start CORE-02 implementation under this packet.

## Rejected alternatives and stops

- No stream inference from probe, request, filename, nominal FPS or timestamp string.
- No SQL schema migration, reindexing the protected archive, broad refactor or rewriting current Canonical modes/workflows.
- If strict stream evidence cannot flow through current query API without breaking frozen callers, stop for versioned API decision and preserve the current candidate.
- If source-occurrence identity is not provable, refuse; do not fabricate custody.
- If the seven Python 3.14 failures are not baseline-matched, report `NOT_OBSERVED` / `UNRESOLVED`; do not claim harmless.

**Terminal document state: OWNER-APPROVED BOUNDED CORE-01 REMEDIATION PLAN — NO PR/MAIN MERGE.**
