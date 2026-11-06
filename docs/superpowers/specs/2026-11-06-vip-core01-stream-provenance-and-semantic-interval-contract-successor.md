# VIP — CORE-01 stream provenance and semantic-location contract successor (PROPOSAL)

**Date:** 2026-11-06
**Status:** OWNER APPROVED 2026-11-06 (D1/D2/D3); narrowly authorized CORE-01 stream-provenance implementation and comparative synthetic test investigation only. No legacy V1 schema change, CORE-02 implementation, PR, or main merge.
**Purpose:** independent GitHub source reconciliation of failed CORE-01 candidate and two bounded design decisions.
**Scope:** Canonical selective CORE-01 and CORE-02 interface decisions only. Do not change existing approved design records, `main`, backups, application code, or worktrees based on this document.

## 1. Verified immutable evidence

- Canonical base: `Centaurioun/video-intelligence-pipeline@3bfcc2ba221b36df6773e630b44479ec961d630a`, tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`.
- LAB source: `Centaurioun/video-intelligence-pipeline-2@5eab58ea2a5424424cb95f2690654b91395425df`.
- CORE-01 candidate branch: `feature/vip-core01-canonical-temporal-adoption-20261106@7c167486d66e076708fd490964f5e4d3c06aa20b`, tree `9092a6044d3ae67993dbb62f96ad1fefecaca4f4`, two commits ahead of Canonical base, 11 changed paths.
- GitHub workflow `42193537310`: `workflow_dispatch`, candidate head SHA exact, Python 3.11 and 3.14 **synthetic smoke** jobs succeeded. It does **not** certify the full FVS/CORE-01 suite or production retrieval.
- Codex operator report: Python 3.11 focused suite `1689 passed, 10 skipped, 1 xfail`; Python 3.14 full suite `4358 passed, 10 skipped, 1 xfail, 7 failed`; these are **REPORTED LOCAL OBSERVATIONS**, not independently rerun. Failed node IDs, exact baseline comparison, and root causes remain NOT_OBSERVED. Reviewer disposition `NEEDS_WORK` is from the Codex handoff, not a GitHub formal PR review.
- No PR/merge or canonical-main mutation observed; owner permitted only the originally scoped CORE-01 branch implementation, not unbounded shared API changes.

## 2. Source-verified hard blocker: persisted stream identity disappears at retrieval output

At candidate SHA:
1. `experiments/persistent_local_index/storage.py` already declares `source_objects.stream_index INTEGER NOT NULL` **and** `samples.stream_index INTEGER NOT NULL`.
2. `experiments/persistent_local_index/search.py` defines `SampleMeta` and `SearchHit` without a stream-index field; `_ROW_METADATA_SQL` retrieves sampled source SHA/PTS/timebase but **not `s.stream_index`**; constructors in both reference and optimized top-K search, and multi-query output, omit this metadata.
3. `src/vip_fvs/semantic_index.py` reexports this `SearchHit`; `src/vip_fvs/retrieval_adapter.py::retrieve` forwards hits through the product retrieval seam unchanged.
4. Candidate `src/vip_fvs/real_source_service.py::_candidate_from_hit` now requires a valid explicit hit stream index equal to the measured probe stream. Thus the ordinary persisted production `SearchHit` cannot pass that requirement although stream identity exists in storage.

**Verified impact:** a genuine integration compatibility blocker, not an issue that can be accepted just because missing provenance is safely refused.

The query source path also selects one path from `source_locations` by SHA and lexicographic order. Multiple occurrences of identical bytes can therefore require separate custody/scope treatment; a stream fix must not falsely claim source-occurrence authorization based on SHA alone.

## 3. Design alternatives: stream provenance

| Alternative | Assessment | Decision proposal |
|---|---|---|
| **A — Propagate actual persisted sample stream index through query models** | Reuses already recorded authoritative evidence; adds compatible optional field to `SampleMeta` and `SearchHit`, populated by read-only SQL and explicitly preserved through all hit constructors and product seams; no SQL schema migration in current stored representation. Touches shared query/API contracts and new tests. | **RECOMMENDED for separate owner-authorized CORE-01 successor scope** |
| B — Resolve each hit's row ID against index SQLite in real-source service | Keeps SearchHit unchanged but couples product service to index layout and read-only generation/row validation; duplicate validation and provenance/root handling. | Reserve for demonstrated inability to evolve SearchHit safely, or for a later independently designed generation-evidence adapter. |
| C — Fill missing hit stream from selected probe/request | Makes an unproven association and can falsely accept a foreign stream. | **REJECT**. |

### Proposed narrow A contract

- Add a backward-compatible, optional `stream_index: int | None = None` field at the **end** of persisted `SampleMeta` and `SearchHit`, so old synthetic fixtures and positional constructors still parse but cannot claim real-mode stream evidence. A mandatory type/API revision requires a separately versioned interface and exhaustive call-site verification.
- Extend query metadata SQL to retrieve the actual `samples.stream_index`; check source-object stream consistency and selected source provenance where the authoritative persisted model supports it. No mutation of on-disk schema; no default `0` or imputation from the probe.
- Preserve the exact same field from SQL → metadata → reference top-K → optimized top-K → multi-query result → product `retrieve` → `_candidate_from_hit`. Preserve cosine sorting, rank, score, row, source, PTS/timebase and old query semantics.
- Invalid/missing/non-integral/foreign stream indices continue to **refuse real-source preparation**, never silently pass. A backward-compatible optional field is not permission to bypass this check.
- Add RED/GREEN tests in `experiments/persistent_local_index/tests/{test_search.py,test_search_materialization.py,test_storage.py}`, `tests/vip_fvs/unit/{test_retrieval_adapter.py,test_real_source_service.py}` and existing integration `test_product_index_query.py`, including a real **generated synthetic persisted source** (audio-first/nonzero video index) passing through production query functions (not handcrafted enriched hit only).
- Negative tests: mismatch between `samples.stream_index` and source object/probe, missing metadata, invalid stream, identical bytes at two custodial occurrences, stale generation/source, and continued strict PTS/timebase semantics.
- **No permission from this proposal to change `search.py`, `storage.py` or broaden the approved CODEX write packet**. These are newly proposed ownership paths requiring explicit consent, current-main contract fingerprint, reviewer, isolated branch/worktree and TDD.

## 4. Independent semantic interval contract issue

The candidate's `_candidate_from_hit` leaves the inherited `semantic_interval` with `start + 1.0`, `endpoint_semantics="half_open"`, `time_domain="semantic_seconds"`. Its `timestamp_human` is commonly a formatted **string**; the existing conversion path sets `start = 0.0` when it is a string. This means the invented legacy interval may be `[0,1)` for unrelated matches. It is **not a measured event**, and candidate `binding_eligible=False` does not turn it into a truthful semantic window.

`src/vip_fvs/review_bundle.py` V1 validation requires `candidate.semantic_interval` with numeric start/end, semantic-seconds domain and half-open semantics. `src/vip_fvs/real_plan.py` separately requires a strictly positive **measured source_pts** interval for editorial mapping. The two coordinate types must never be silently conflated.

| Alternative | Assessment | Decision proposal |
|---|---|---|
| **I — Preserve legacy V1 only as explicitly nonbinding/deprecated compatibility, keep its candidate-interval debt BLOCKED; create typed `POINT` in the *new* CORE-02 Report V1** | Narrow and least disruptive; does not falsely declare old interval repaired. Legacy prepare-real must not be promoted as a reliable semantic-window producer; do not derive edit boundaries from it. | **RECOMMENDED immediate boundary; CORE-01 whole remains PARTIAL until legacy debt is separately resolved** |
| II — Version review-bundle contract with `semantic_location: POINT/COARSE_WINDOW` and update every consumer | Scientifically cleaner ultimate solution; broader architecture, migration/legacy-read handling, tests and owner decision required. | **SEPARATE DESIGN / FUTURE AUTHORIZATION** |
| III — Invent +1s or create empty half-open range and mark it event | False timing provenance or invalid interval. | **REJECT** |

Proposed governing clarification: only an independently observed positive coarse-window duration may justify a `COARSE_WINDOW`; an indexed sample without such evidence is a nonbinding `POINT` in the new report, carrying source-native sample PTS separately as MEASURED technical evidence (not measured event endpoint). Do not silently change Gate-3 source-native interval/refinement requirements.

**Gate decision:** under recommended I, the preserved legacy `+1` behavior is acknowledged technical debt and is NOT an approved truthful new temporal representation. It must not be copied to CORE-02, used to certify CORE-01 fully, or described as a reliable event window.

## 5. Required independent verification before any candidate certification

1. Verify current live Canonical main and candidate branch HEAD at execution time; preserve existing dirty worktrees and DO_NOT_DELETE repositories.
2. In an authorized isolated candidate successor branch, first reproduce a **production-like persisted SearchHit** without stream metadata (RED). Capture one real generated-fixture nonzero selected video stream; verify its row's SQLite stream and measured PTS/timebase. Prove the candidate's existing refusal is why the normal path fails.
3. Red tests across exact indexed/reference/multi-query ranking paths; minimal implementation of A; green same tests, legacy fixture handling, source stream mismatch/refusal and no fake-to-real promotion.
4. Compare exact **seven Python 3.14 full-suite failures** with an isolated **pinned Canonical main baseline**, using the same interpreter, dependencies and command. Record exact failed node names/logs, regression delta and genuinely unavailable evidence. Do not call them unrelated/pre-existing without a matched baseline.
5. Perform full affected persistent-index, retrieval, real-source, Gate-3 and CLI focused regression, plus 3.11/3.14 where available. The GitHub synthetic smoke workflow is narrower than full CORE-01 acceptance; record actual coverage.
6. Independent reviewer must re-review the **new exact candidate SHA** and either clear the functional blocker or issue specific NEEDS_WORK findings. No PR/merge until the separate owner integration action.
7. If the accepted scope leaves legacy Task 3 blocked, classify the result **STREAM_PROVENANCE_CANDIDATE_VERIFIED / CORE01_CANONICAL_CANDIDATE_PARTIAL**, not full CORE-01 completion. CORE-02 design may use its independently governed typed POINT only when required inputs and authority are verified.

## 6. Owner decisions requested

**D1 — Extension of development scope (required before code writes):** Approve focused production stream-index propagation into `experiments/persistent_local_index/search.py` and exactly dependent tests/call sites, limited to source-to-hit provenance. No model/protected media/real source execution, migration or Gate authorization.

**D2 — Temporal contract boundary:** Approve recommendation I (CORE-02 typed POINT; legacy review-bundle V1 retained/deprecated, not described as repaired, full CORE-01 remains PARTIAL), while making any future review-bundle V2 migration an explicit separate design decision.

**D3 — Failure investigation:** Require a pinned-main comparator for the seven full-suite Python 3.14 failures before alleging they are unrelated or deciding if the candidate is regression-free.

Explicit design authorization must precede the new implementation scope. Existing previous owner permission did not include shared `search.py` or persisted query-model contract changes.

## 7. Source anchors

- Canonical base: https://github.com/Centaurioun/video-intelligence-pipeline/tree/3bfcc2ba221b36df6773e630b44479ec961d630a
- CORE-01 candidate: https://github.com/Centaurioun/video-intelligence-pipeline/commit/7c167486d66e076708fd490964f5e4d3c06aa20b
- Candidate diff: https://github.com/Centaurioun/video-intelligence-pipeline/compare/3bfcc2ba221b36df6773e630b44479ec961d630a...7c167486d66e076708fd490964f5e4d3c06aa20b
- `experiments/persistent_local_index/storage.py`, `search.py`; `src/vip_fvs/{semantic_index.py,retrieval_adapter.py,real_source_service.py,review_bundle.py,real_plan.py}`, all at candidate SHA.
- GitHub synthetic smoke 42193537310: https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/42193537310
- Earlier approved design/plan branch: https://github.com/Centaurioun/video-intelligence-pipeline-2/tree/design/vip-core01-core02-selective-canonical-integration-20261106

**Terminal: CORE01_STREAM_AND_INTERVAL_CONTRACT_SUCCESSOR_OWNER_APPROVED — CANDIDATE_REMEDIATION_ONLY.**


## 8. Owner approval and execution-scope receipt — 2026-11-06

The Repository Owner explicitly replied **"onaylıyorum"** to the three decisions presented after the independent GitHub source review:

- **D1 APPROVED:** Bounded addition of *persisted* selected video stream provenance to the `SampleMeta` → `SearchHit` → product retrieval path, including exact dependent `search.py`/test/call-site changes. The stream index must originate in independently verified persisted sample/source metadata; no inference from probe/request. This approval broadens CORE-01 candidate remediation only to necessary explicitly named provenance code paths and tests, not arbitrary index redesign.
- **D2 APPROVED:** Keep existing `review_bundle.py` V1 semantics and the inherited `+1s` legacy behavior explicitly marked `BLOCKED_BY_CONTRACT` / nonbinding technical debt for now. Do not claim full CORE-01 closure; the new CORE-02 Report V1 will use typed nonbinding `POINT` under its separately controlled future implementation. No V1/V2 migration or Legacy API rewrite authorized here.
- **D3 APPROVED:** Investigate the seven Python 3.14 full-suite failures against clean pinned Canonical `main`, same interpreter/dependencies/test command/fixture availability as the candidate. Classify as PRE_EXISTING/REGRESSION/ENVIRONMENT/UNRESOLVED only when supported by matched evidence. No unexplained failures may be silently ignored.

**Implementation authorization boundary:** The owner approved this tightly scoped follow-up CORE-01 candidate remediation and synthetic/regression investigation. Use a clean, *new* isolated Canonical successor worktree and branch rooted at the exact observed candidate SHA after fresh Git/current-contract and owner-path checks. Reuse the existing verified native Codex worker only if its independent project/worktree/branch binding and exclusive writer ownership remain valid; otherwise use the repository-compliant fresh native worker bootstrap. Preserve dirty worktrees, Canonical and LAB `main`, and immutable backup repositories. A regular push of the successor candidate branch is in scope; PR creation, main merge, real/protected media, genuine model download/use, provider/cloud execution, production render/export, Gate promotion and broad schema migration remain **NOT AUTHORIZED**. The precise downstream task packet must list all additional shared source paths and tests, and must refuse any unapproved contract expansion.

This owner decision changes the design's disposition only; no implementation, tests, code review or readiness certification was performed by recording it.
