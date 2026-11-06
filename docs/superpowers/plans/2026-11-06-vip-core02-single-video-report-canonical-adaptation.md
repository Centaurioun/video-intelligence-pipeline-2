# VIP CORE-02 Query-Driven Single-Video Report — Canonical Adaptation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended for coupled tasks) or superpowers:executing-plans, subject to Canonical AGENTS.md / Native Codex Portfolio scheduling authority, to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Canonical-owned `vip-fvs analyze-local` command that performs **one authorized local-video + one text-query** semantic search and emits a validated, evidence-truthful JSON Report V1 with multiple source-bound candidate POINTs, or a genuine ZERO_MATCH.

**Architecture:** Reuse the existing identical Canonical `SemanticIndexEngine`, model-space, immutable snapshot, probe, source/stream identity and refusal APIs. Adapt the LAB `core_report.py` and `core_analysis.py` *contracts* into small Canonical-owned product modules, keeping permission, generation-evidence and publication boundaries independently testable. No duplicate decoder/indexer/model loader or Mega/batch runtime.

**Tech Stack:** Python 3.11/3.14, pytest, existing `vip_fvs` and `persistent_local_index`, SQLite read-only verified index evidence, standard-library `fractions`/`hashlib`/`json`/`os`.

**Spec:** Owner-approved `docs/superpowers/specs/2026-11-06-vip-core01-core02-selective-canonical-integration-design.md` in LAB design branch `design/vip-core01-core02-selective-canonical-integration-20261106`; references LAB `docs/ai-studio-tasks/MEGA_CORE_02_QUERY_DRIVEN_SEMANTIC_REPORT_V1.md` and `MEGA_CORE_02_CODEX_VERIFICATION_AND_BOUNDED_REPAIR.md` at pinned LAB `5eab58ea2a5424424cb95f2690654b91395425df`. **Dependency:** linked `2026-11-06-vip-core01-temporal-correctness-canonical-adaptation.md`.

## Global Constraints

- **PLAN ONLY:** Owner approved architecture/design on 2026-11-06, **not** Canonical source implementation, PR or merge; explicit separate authorization and an approved implementation plan are still required.
- Start with fresh verified Canonical `main@3bfcc2ba221b36df6773e630b44479ec961d630a` and exact tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`. LAB reference `main@5eab58ea2a5424424cb95f2690654b91395425df`. If current baseline/consumed contracts change, reconcile exact SHAs before writing.
- For an authorized execution, use one clean **isolated Canonical candidate worktree/branch** with exclusive writer ownership; never touch dirty local checkouts, Canonical main, LAB main or DO_NOT_DELETE backups. No destructive Git. Do not create a PR or merge until independently authorized.
- Preserve canonical `src/vip_fvs/bounded_admission.py`, `_bounded_admission_fs.py`, `real_source_probe.py`, `source_snapshot.py`, `pilot_authorization.py`, `semantic_index.py` and Gate-0/1/2/3 governance; do not replace or duplicate the index, model-space and snapshot implementations already identical at both pins.
- No authentic archive media, real model loads/downloads, provider/cloud egress, editing/render/QC or Gate promotion; generated synthetic/fixture tests only, with no implicit real-source permission. Real-mode code may be statically examined and negative-tested with injected interfaces, **not actually executed on protected source**.
- `MEASURED` is source-native, actually derived PTS/timebase evidence only; `MATCHED` is semantic relevance with `binding_eligible=false`; `NOT_OBSERVED` is an availability marker. No nominal-FPS frame inference, fabricated frame/edit interval, false probability, automatic captions, model-quality claims or fake-to-real promotion.
- Query analysis does not need editorial-plan/render or `refine` permission. If current Canonical owner authorization cannot express query-only rights, do not alter its schema or forge permissions: **REAL mode remains BLOCKED** until separately authorized contract successor.
- Follow TDD RED→GREEN and systematic debugging. Every code task ends with reviewable file-scoped commit and evidence. No agent success claim alone certifies completion.

## Review Focus

1. **Two occurrences of the same bytes:** must not silently merge custody, source revision or permission; **Task 3 foreign-occurrence test**.
2. **Shared/multi-source index and saturated Top-K:** must not globally rank then filter to misleading ZERO_MATCH; count unknown if saturation prevents an exhaustive count; **Task 3 and Task 4**.
3. **Revoked/expired owner scope at use/publication:** no file hashing, model open, indexing, or report publication after a failing authorization gate; **Task 2 + Task 4 tests**.
4. **PTS/timebase and selected-stream mismatch:** retrieve a MATCHED point bound to measured sample row only, not by trusting SearchHit alone; **Task 3 + Task 4 tests**.
5. **Atomic report publication / symlink / existing file:** stable schema and digest, no overwrite or incomplete success when write fails; **Task 1 + Task 5 tests**.

---

## Proposed file ownership (new files must have one responsibility)

| Task | Exact owner paths | Interface/role |
|---|---|---|
| 1 | New `src/vip_fvs/core_report.py`, new `tests/vip_fvs/unit/test_core_report.py` | Report V1 canonical schema, evidence validator, canonical digest and exclusive publication |
| 2 | New `src/vip_fvs/query_analysis_authorization.py`, new `tests/vip_fvs/unit/test_query_analysis_authorization.py` | Query-only scope check; no Gate-3 refine permission |
| 3 | New `src/vip_fvs/core_generation_evidence.py`, new `tests/vip_fvs/unit/test_core_generation_evidence.py` | Read-only single-source index verification, sample/stream/PTS binding |
| 4 | New `src/vip_fvs/core_analysis.py`, new `tests/vip_fvs/unit/test_core_analysis.py` | One coherent orchestration over existing engine/probe/snapshot; fail closed |
| 5 | Modify `src/vip_fvs/cli.py`; new `tests/vip_fvs/integration/test_core_analyze_local_cli.py` | Single CLI command, fake/real separation, exits, report target |
| 6 | No new source owner: task-5 and existing Canonical tests/workflows | Review/CI and provenance receipt; implementation candidate status |

Concretely **do not** add LAB ``batch_report.py`, `batch_retrieval.py`, `query_batch.py`, `synthetic_profiles.py`, `three_arm_batch.py` or any `src/vip_lab/**`. Keep current Canonical `.gitignore`, executable bits and workflows intact. The source modules are proposed API boundaries; execute the task *only* after design/plan review and Canonical owner source authorization.

### Task 1: Versioned report, typed POINT and no-clobber publisher

**Files:**
- Create: `src/vip_fvs/core_report.py`
- Create: `tests/vip_fvs/unit/test_core_report.py`

**Interfaces:**
- `CORE_REPORT_SCHEMA_VERSION: int = 1`; `CORE_REPORT_KIND: str = "vip_fvs.query_driven_semantic_report.v1"`.
- `format_rational_seconds(pts: int, timebase_num: int, timebase_den: int) -> dict[str, Any]` returns reduced rational `{"num":..., "den":..., "canonical":"num/den"}`.
- `build_point_semantic_location(pts: int, timebase_num: int, timebase_den: int) -> dict[str, Any]` with `location_kind="POINT"`, `time_domain="semantic_seconds"`, exact rational position, `window_width_seconds="NOT_OBSERVED"` and **no start/end**.
- `build_core_semantic_report(...) -> dict[str, Any]`, `validate_core_semantic_report(report: Mapping[str, Any]) -> None`, `compute_core_report_digest(report: Mapping[str, Any]) -> str` and `publish_core_semantic_report(report: Mapping[str, Any], report_path: str | Path, *, output_root: str | Path) -> Path`: adapt the LAB public signatures while keeping existing Canonical evidence conventions.

- [ ] **Step 1 — RED:** add `test_point_is_exact_rational_and_has_no_interval_bounds` (e.g., 9,000 ticks at 1/90,000 = 1/10 sec); `test_invalid_pts_and_timebase_refuse`; `test_match_never_measured_edit_cut`; `test_not_observed_is_not_evidence_class`; `test_report_digest_recomputed_without_self_field`; `test_zero_match_is_success_without_fake_hits`; `test_source_and_runtime_evidence_required`; `test_symlink_escape_and_existing_report_refuse`; `test_partial_publish_does_not_clobber`.
- [ ] **Step 2 — Confirm RED:** run `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_core_report.py`; ensure failures are caused by missing/new contract, not malformed fixture imports.
- [ ] **Step 3 — GREEN:** adapt LAB Report V1 validation, typed POINT and no-clobber publisher into focused Canonical file. Enforce exact report schema version, source+stream+PTS/rational identities, actual score semantics, evidence class separation, error-code constraints, stable digest and root-confinement with symlink protection. Do not carry arbitrary uncited fields, real-model success claims or new format versions.
- [ ] **Step 4 — Verify GREEN:** rerun focused tests; inject `os.link` failure and report-existing cases to prove prior output is unchanged. Verify serialized JSON/digest repeatability under frozen inputs.
- [ ] **Step 5 — Review/commit:** `git diff --check`, secret/path leak review; commit only this task's two files, exact SHA and test output.

### Task 2: Canonical query-analysis authorization adapter (contract-only; REAL remains gated)

**Files:**
- Create: `src/vip_fvs/query_analysis_authorization.py`
- Create: `tests/vip_fvs/unit/test_query_analysis_authorization.py`

**Interfaces:**
- Proposed immutable type `QueryAnalysisScope` with fields `source_path: Path`, `source_revision_id: str`, `query_digest: str`, `model_root: Path`, `model_identity: str`, `model_revision: str`, `weights_sha256: str`, `semantic_space_id: str`, `index_root: Path`, `output_root: Path` and `selected_stream_index: int | None`.
- Proposed `require_query_analysis_authorization(authorization: PilotAuthorization, scope: QueryAnalysisScope, *, now: datetime | None = None) -> None`; this checks exact existing owner grant fields, stage allowlist, expiry/revocation and source/stream/model/space/index/output scope **before any governed read**, with authorization rechecked at use and publication boundaries. It does NOT infer permission from fixture metadata or insert `refine` in allowed stages.

- [ ] **Step 1 — RED:** `test_missing_expired_or_revoked_grant_prevents_source_read`, `test_mismatched_revision_stream_model_space_and_output_refuse`, `test_query_only_rights_do_not_require_refine`, `test_grant_lacking_query_index_decode_embed_refuses`, `test_synthetic_grant_never_authorizes_real_mode` and `test_revoked_between_query_and_publication_refuses`. Use injected zero-read call spies, not actual source/model access.
- [ ] **Step 2 — Confirm RED:** run `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_query_analysis_authorization.py`; capture expected test failures.
- [ ] **Step 3 — HARD CONTRACT GATE:** review `PilotAuthorization`, `require_pilot_authorization`, `require_prepare_authorization`, `require_snapshot_lifecycle` and Canonical `CANONICAL_CONTRACTS.md`. If the existing frozen policy envelope cannot express an authorized query-only scope without weakening or rewriting the grant, **STOP any real-mode enablement**; retain narrowly testable adapter and refuse real-mode dispatch (`QUERY_ANALYSIS_REAL_SCOPE_NOT_AUTHORIZED`). Do not fabricate owner approval/permission or rewrite `pilot_authorization.py` under this plan.
- [ ] **Step 4 — GREEN if representable:** implement the scope check using the existing canonical record and exact fields. Keep `PilotAuthorization` unchanged. For missing real policy capability, implement explicit fail-closed refusal, not an alternate permissive route.
- [ ] **Step 5 — Verify/commit:** run focus tests and `tests/vip_fvs/unit/test_pilot_authorization.py` (if present; verify test path first), plus existing real-source authorization/refusal tests. Commit only adapter/test. Document `QUERY_ONLY_AUTHORITY=SUPPORTED_WITH_EXISTING_SCHEMA` or `BLOCKED_BY_CONTRACT` with exact source evidence. Do not claim real execution authorized.

### Task 3: Verify one-source generation and sample-binding data

**Files:**
- Create: `src/vip_fvs/core_generation_evidence.py`
- Create: `tests/vip_fvs/unit/test_core_generation_evidence.py`

**Interfaces:**
- `SourceGenerationExpectation` (frozen dataclass) with `generation_id`, `semantic_space_id`, `source_locator`, `source_revision_id`, `source_sha256`, `source_byte_count`, `selected_stream_index`, `timebase_num` and `timebase_den`; optionally a verified snapshot/occurrence binding when present in the existing index schema.
- `VerifiedGenerationEvidence` with verified `row_id -> sample metadata` map, `manifest_digest`, `source_sample_count`, `committed_row_count` and explicit eligibility state; these are **observed** fields or named absence/refusals, never invented.
- `inspect_single_source_generation(db_path: Path, manifest_path: Path, *, expected: SourceGenerationExpectation) -> VerifiedGenerationEvidence`: **read-only SQLite**, generation manifest and source/sample rows. No index mutation or schema migration.

- [ ] **Step 1 — RED:** tests `test_generation_rejects_foreign_source_even_same_sha_other_occurrence`, `test_global_multi_source_generation_refuses_before_topk`, `test_verified_sample_binds_absolute_stream_and_rational_pts`, `test_missing_sample_row_does_not_infer_stream_from_hit`, `test_invalid_generation_manifest_or_database_refuses`, `test_stale_index_generation_refuses`. Construct tiny synthetic index artifacts with the actual Canonical schema, not fake column names.
- [ ] **Step 2 — Confirm RED:** run `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_core_generation_evidence.py`. If existing schema cannot prove source occurrence/revision/stream, make the test require a named `SOURCE_SCOPE_UNPROVABLE` refusal; do not silently change the DB schema under this task.
- [ ] **Step 3 — GREEN:** move/adapt only the LAB CORE-02 *read-only index identity checks* into this focused module; interact with Canonical-owned generation manifest and read-only SQLite, never create a new index writer or scan global Top-K and postfilter. Keep missing source-level custody binding as a refusal when necessary.
- [ ] **Step 4 — Verify/commit:** run targeted test plus `tests/vip_fvs/integration/test_product_index_query.py` and relevant existing persistent-index unit tests. Review actual indexed rows, manifest fingerprints, and source invariants. Commit only two files.

### Task 4: Orchestrate index/query → source-bound multiple candidate Report V1

**Files:**
- Create: `src/vip_fvs/core_analysis.py`
- Create: `tests/vip_fvs/unit/test_core_analysis.py`

**Interfaces:**
- `CoreAnalysisRequest` frozen request dataclass, conceptually mirroring LAB: source path, single text query, index root, report path/output root, attempt ID, source revision, Top-K, checked runtime/engine injections, pilot auth/snapshot/probe roots, selected stream and explicit `fake_embedder` for tests.
- `CoreAnalysisOutcome` containing validated `report: dict[str, Any]`, `report_path: Path`, `summary: dict[str, Any]`.
- `analyze_local_video(request: CoreAnalysisRequest) -> CoreAnalysisOutcome` calls Task 2 authorization, Canonical snapshot/probe, existing `SemanticIndexEngine` `build_generation_spec/index_source/query`, Task 3 generation verifier, and Task 1 Report V1 publisher.
- Do not copy LAB `core_analysis.py` (1,944 lines) blindly. One-source, no captioning, no refinement and no gate actions.

- [ ] **Step 1 — RED:** `test_two_ranked_hits_have_distinct_pts_and_same_revision`, `test_zero_source_scoped_matches_is_success`, `test_topk_saturated_total_is_not_observed`, `test_invalid_rank_score_or_stream_refuses`, `test_wrong_revision_or_same_sha_other_occurrence_refuses`, `test_no_default_fake_inference`, `test_real_mode_grant_missing_stops_before_probe_model_and_source`, `test_no_edit_plan_render_or_refinement_called` and `test_no_partial_report_after_index_or_probe_failure`. Fake runtime must be labeled synthetic, injected tests cannot imply actual model inference.
- [ ] **Step 2 — Confirm RED:** run `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_core_analysis.py` and record failure evidence.
- [ ] **Step 3 — GREEN:** implement the minimal in-process orchestration. Validate output target/inputs and mode first; verify query-only owner authority **before** governed reads; use an immutable source snapshot when required and independently probe its stream; verify or refuse generation provenance; index and query with existing engine, bind hits to independently verified sample rows; build POINT matches carrying sampled `source_pts`/rational timebase as measured-only technical evidence. Recheck source/snapshot authorization before publication. If Task 2 real grant remains blocked, reject REAL before source/model activity.
- [ ] **Step 4 — Verify GREEN:** targeted tests and canonical `tests/vip_fvs/integration/test_product_index_query.py` and `tests/vip_fvs/unit/test_source_snapshot.py`; prevent same source digest from silently acting as same occurrence. Confirm Top-K and ZERO_MATCH semantics with actual injected engine traces and output bytes.
- [ ] **Step 5 — Review/commit:** minimize complexity, review refusal privacy, source provenance and no-clobber; commit only orchestrator/test files and record SHA.

### Task 5: Add exactly one Canonical CLI command

**Files:**
- Modify: `src/vip_fvs/cli.py`
- Create: `tests/vip_fvs/integration/test_core_analyze_local_cli.py`

**Interfaces:**
- Existing `python -m vip_fvs.cli` argument parser, add `analyze-local` without removing/modifying existing `run`, `index-local`, `query-local`, `prepare-real`, `preview-*` etc.
- Inputs (as scoped by approved spec): `--source --query --index-root --output-root --attempt-id --source-revision-id --report-path --top-k --selected-stream-index`; explicit checked real model/authorization/snapshot options; `--fake-embedder` only for synthetic tests. One JSON summary on success or one named refusal on error, nonzero exit on failure.

- [ ] **Step 1 — RED:** `test_analyze_local_help_and_parser`, `test_synthetic_single_video_emits_report_v1_and_one_json_summary`, `test_two_hits_and_zero_hits_exit_success_truthfully`, `test_fake_real_flag_mix_is_refused`, `test_real_without_owner_scope_refuses_before_media_or_model_open`, `test_existing_report_no_clobber_and_nonzero_exit`, `test_path_escape_is_refused`, `test_all_preexisting_subcommands_preserved` and `test_cli_error_never_leaks_secret`. Run at least one **fresh Python subprocess** to prove actual CLI wiring.
- [ ] **Step 2 — Confirm RED:** run `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/integration/test_core_analyze_local_cli.py`.
- [ ] **Step 3 — GREEN:** add minimal parser+dispatch and error-summary mapping to Task 4; no separate CLI driver subprocess composition; nonzero named errors, no successful “all checks passed” on failure. Preserve existing Canonical command signatures and unrelated behavior.
- [ ] **Step 4 — Verify:** new CLI tests, `tests/vip_fvs/integration/test_cli_acceptance.py`, `test_product_index_query.py`, all CORE-01 targeted tests, and both CORE-02 report/unit tests. Verify source bytes unchanged and no data saved in source directories.
- [ ] **Step 5 — Review/commit:** commit CLI and its test only, record exact candidate SHA.

### Task 6: Canonical product-candidate verification, not Gate or REAL promotion

**Files:** no new production code owner. Produce a task-local verification receipt in an owner-authorized integration branch only if the execution packet names its exact path, else return receipt in Codex response.

**Interfaces:** consumed `CORE-01` candidate SHA, exact Canonical baseline SHA, new CORE-02 candidate SHA, full test ID and CI run provenance, confirmed no real media or model, no Canonical-main write.

- [ ] **Step 1 — Verify scope:** independent `git diff` vs exact pinned Canonical base: only authorized source/test files and necessary focused test wiring; existing Canonical-only files, all eight executable script modes, Gate governance, workflows and backups unchanged.
- [ ] **Step 2 — Run fresh integration suite:** `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_core_report.py tests/vip_fvs/unit/test_query_analysis_authorization.py tests/vip_fvs/unit/test_core_generation_evidence.py tests/vip_fvs/unit/test_core_analysis.py tests/vip_fvs/integration/test_core_analyze_local_cli.py`. Report exact per-ID PASS/FAIL/SKIP, no required skips.
- [ ] **Step 3 — Run Canonical regression:** `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs experiments/persistent_local_index/tests`, plus full available canonical `PYTHONPATH=src:experiments:. python -m pytest -q`. Add `python -m compileall -q src/vip_fvs experiments/persistent_local_index`, `git diff --check` and secret scan. Record environment-caused fixture skips as not tested, no fabricated all-green claim.
- [ ] **Step 4 — Two interpreters and hosted CI:** Python 3.11 and Python 3.14 targeted and Canonical-relevant suite on the **exact candidate SHA**. If tools unavailable, report `NOT_OBSERVED` and wait for actual authorized CI rather than assume. Do not silently install dependencies or model weights.
- [ ] **Step 5 — Independent review:** review new code for authority, data migration/occurrence false joins, temporal claims, crash-safe publication, consumer compatibility and scope. Request review before integration. Reconcile feedback through receiving-code-review, debug failures systematically, re-run tests on the **final reviewed SHA**.
- [ ] **Step 6 — Stopping rule:** do **not** create an integration PR or merge into Canonical `main` without the separate explicit owner decision naming the candidate exact SHA and permitted integration action. Synthetic acceptance is not `CORE_CLI_PRODUCT_COMPLETE` or authentic media/model acceptance.

## Execution ownership and sequencing

`CORE-01` and `CORE-02` share `cli.py` and source-temporal contracts; their writes are **dependent** and must not be done concurrently on the same branch. After an owner-authorized CORE-01 candidate, CORE-02 can start from the reviewed, reconciled candidate SHA in an isolated successor workspace. Independent, truly disjoint test review can overlap only with explicit branch/path ownership and under current Canonical Native Codex protocol. An unreadable or stale CORE-01 base is a hard stop; not an excuse to reset or import arbitrary LAB files.

## Acceptance boundary

- **Expected at first accepted candidate:** Synthetic/generated-fixture-only Canonical `analyze-local` CLI + Report V1, exact source/sample PTS and provenance, truthful multi-hit and zero-hit behavior, no-clobber publication, named refusals and matching existing Canonical tests.
- **Explicitly NOT obtained:** protected/archive data permission, genuine model retrieval quality, authentic model/source inference, production editing/QC, Gate 0/1/2/3 advancement, CLI product completeness for real-world workflows, full archive index migration.
- **Blocked if:** query-only authorization cannot be expressed without changing frozen policy; source occurrence/stream cannot be independently verified; mixed-source index cannot be source-scoped; legacy CORE-01 consumer incompatibility is unresolved; or any required suite fails.

This document records the execution-ready **plan proposal**, not permission to execute. Owner plan review and explicit Canonical source/branch authorization are still mandatory.
