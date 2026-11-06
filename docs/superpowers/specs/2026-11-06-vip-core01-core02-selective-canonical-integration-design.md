# VIP — CORE-01 / CORE-02 selective Canonical integration design (PROPOSED)

**Date:** 2026-11-06  
**Design status:** PROPOSED — OWNER APPROVAL PENDING. NOT AN IMPLEMENTATION PLAN OR AUTHORIZATION.  
**Prepared by:** ChatGPT, following independent ChatGPT/Codex read-only comparison and verified reconciliation.  
**Publication surface:** Separate LAB design branch, no change to either original `main` or backup.  
**Target future repository:** `Centaurioun/video-intelligence-pipeline` (Canonical).  
**Design scope:** Local-first, one-source, one-text-query semantic candidate reporting; optional source-native refinement evidence linkage; CORE-01 data integrity repairs.

## 1. Frozen source / evidence ledger

| Identity | Exact SHA |
|---|---|
| Canonical main | `3bfcc2ba221b36df6773e630b44479ec961d630a` |
| Canonical tree | `032b7ea8908fa04f1d85cf0d57c1608d28864557` |
| LAB main | `5eab58ea2a5424424cb95f2690654b91395425df` |
| LAB tree | `dae72052bbdbc1962713f302b50f8fa2fd78ed7f` |
| ChatGPT review | `cf3b02cc9e87a7d79ee21bd34bbb9449a9362cd7` |
| Codex review | `a4e93bcaae244587aa36a13ff4f7a5db3da8083b` |
| Reconciliation | `45a3407dd520be82822cbaa03aa55df5fa440064` |
| LAB hosted CORE-02 proof | GitHub Actions [42170532090](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/42170532090): 29 CORE-02 tests PASS on each Python 3.11/3.14 job; separate earlier job step 147 PASS per version. |

At the exact pinned Git trees there are 1,286 Canonical-only paths, 149 LAB-only paths, **nine same-path differing-content blobs**, and **eight same-content paths with different executable mode** (Canonical executable, LAB non-executable). The 17 shared-path Git differences and 1,452 total different paths must not be confused with nine modified source contents. The exact same blobs already supply Canonical's `semantic_index.py`, `source_snapshot.py` and `experiments/persistent_local_index/model_space.py`. No re-import is justified for identical implementations.

Both backup GitHub Releases were previously observed PRIVATE and immutable; their existence is a protection input, not a grant for migration, media processing, or cleanup.

## 2. Purpose, exclusions, and success boundary

### Purpose

Make the previously verified **LAB CORE-01 correct source-native sample/stream handling** and **LAB CORE-02 query-driven single-video JSON report** available through **one Canonical-owned product CLI path** without weakening the existing Canonical Gate architecture, provenance or source-custody rules. A user may retrieve multiple ranked candidate samples from one explicitly eligible source/revision with one text query. The output must tell them what was matched, what was measured, and what was not observed.

### First acceptance target

Synthetic/generated-fixture-only, **test-proven Canonical candidate** of a unified `vip-fvs analyze-local` command plus validated Report V1. Do not conflate this with real SigLIP, protected archive, meaningful search quality, production readiness, Gate promotion, exact edit boundaries, or editorial approval.

### Non-goals / anti-goals

- No wholesale LAB import; no copying `src/vip_lab/**`, synthetic Mega-03..17 harness, three-arm batch runtime or LAB workflows into Canonical.
- No replacement/rewriting of already identical Canonical snapshot/index/model-space modules or of the approved bounded file-admission primitives.
- No new decoder, model loader, vector database, job scheduler, UI, caption pipeline, ASR, video editing, rendering, provider or network operation.
- No persisted LAB index **data** migration or default reuse of unverified multi-source generations.
- No transition from a sample's integer PTS or semantic location directly to an exact event boundary or edit plan.
- No generated real-world owner/reviewer/rights assertions, fabricated model inference, or treating synthetic CI as authentic evidence.
- No modifications to Canonical main or existing dirty worktrees in the design stage.

### Authoritative constraints

Canonical `AGENTS.md`, `docs/INDEX.md`, `docs/architecture/CANONICAL_CONTRACTS.md`, `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`, Gate-3 temporal contracts, `docs/project/00_PROJECT_CHARTER.md`, `01_CURRENT_STATE_AND_HANDOFF.md`, `02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`, `STATE_MAINTENANCE_PROTOCOL.md`, and accepted `ADR-0003` govern. ADR-0003 removes **ordinary development-workspace source-auth enforcement**, not runtime permission, protected archive, model/provider, production or Canonical merge controls.

## 3. Three design approaches and recommendation

| Approach | Advantages | Problems / tradeoffs | Proposed disposition |
|---|---|---|---|
| **A. Merge/copy all LAB source** | Few manual selections | Drops Canonical-only code, file modes, Gate/workflow rules, bounded admission, custody, may promote fake evidence | **REJECT** |
| **B. Rewrite the entire query/index/report engine in Canonical** | Potentially clean architecture | Duplicates present index/model/probe/snapshot engines; expands bugs/test surface and violates minimum viable scope | **REJECT** |
| **C. Contract-first, narrow adapters + selective CORE-01 patch** | Reuses Canonical authority/services; preserves clear compatibility seam; minimum new product behavior | Requires explicit source/authorization/index/query/report mapping and Canonical tests; some LAB code cannot be reused verbatim | **RECOMMENDED, NOT YET APPROVED** |

The selected-on-approval design is **C**. This is an architectural proposal, not evidence that all LAB code works unchanged in Canonical.

## 4. Proposed architecture and data contracts

### 4.1 Dependency and evidence flow

`[User query + exact source scope]`
→ `[fail-closed query-analysis permission / synthetic-mode separation]`
→ `[canonical source occurrence/revision + verified immutable snapshot]`
→ `[selected absolute ffprobe video stream + exact rational timebase]`
→ `[existing model/runtime identity + existing local semantic index generation]`
→ `[source-scoped query and verified sample-row/PTS binding]`
→ `[multiple ranked MATCHED candidate POINTs]`
→ `[Report V1 validation + no-clobber atomic publication]`
→ `[human review; optional separately verified source-native refinement later]`

**Never:** semantic candidate → invented semantic interval → source edit boundary.

No index/database migration is part of this design. The engine/data remains a rebuildable, source- and semantic-space-bound projection.

### 4.2 Reuse and source-code impact map

| Capability | Canonical source | LAB candidate | Design ruling |
|---|---|---|---|
| Measured source stream/probe | `src/vip_fvs/real_source_probe.py` | same blob at pinned trees | Reuse; no duplicate probe |
| Immutable snapshot/custody | `src/vip_fvs/source_snapshot.py` | same blob | Reuse; preserve lifecycle/authorization |
| Bounded descriptor-relative admission | `src/vip_fvs/bounded_admission.py` and `_bounded_admission_fs.py` | absent from LAB | **PRESERVE CANONICAL**; source read integration must not bypass an applicable canonical intake contract |
| Semantic-space/index engine | `src/vip_fvs/semantic_index.py` and `experiments/persistent_local_index/model_space.py` | same blobs | Reuse existing protocol; no new engine |
| Source-native sample PTS, absolute stream, filter timebase | `experiments/persistent_local_index/media.py` | LAB CORE-01 altered file | Evaluate narrow patch and focused regression tests |
| Existing prepare/refinement | `src/vip_fvs/real_source_service.py` | LAB CORE-01 altered file | Preserve existing consumers; remove fabricated +1s only with verified compatible point/interval contract and negative tests |
| Product CLI | `src/vip_fvs/cli.py` | LAB added analyze-local plus fake-only batch commands | Add only one Canonical-owned `analyze-local` entrypoint; preserve all existing subcommands |
| Report V1 | absent | `src/vip_fvs/core_report.py`, ~1,302 lines | Candidate contract/validation/atomic publisher. Prefer focused reuse/simplification instead of blind full-file transplant |
| Single-source orchestrator | absent | `src/vip_fvs/core_analysis.py`, ~1,944 lines | Candidate implementation reference; adapt via stable Canonical contracts, not a second parallel index authority |
| Report tests | absent | `test_core_report.py`, `test_core_analysis.py`, `test_core_analyze_local_cli.py` | Bring only applicable behavioral tests, add Canonical-specific negatives |

The exact source paths and same-blob identities come from the pinned GitHub trees. Approximate line counts describe observed LAB files, not proposed new-file sizes.

### 4.3 Source, authority and identity

A source path is a **locator**, never source identity. Content SHA-256 confirms byte identity, not the custody occurrence, permission or revision. The product evidence must bind (where actually available):

- **Source occurrence/custody:** trusted occurrence reference and source revision; if not established, record explicit availability or refuse a governed operation rather than invent an ID.
- **Immutable content:** source revision, byte count, source SHA-256, snapshot identity/digest and retained tool/probe evidence; reverify at read and publication boundaries as governed.
- **Stream:** absolute `ffprobe stream.index` (not relative `v:0` ordinal, track ID or guessed first stream), actual selected-video-stream rational `time_base=num/den`.
- **Representation:** frozen model/weights/processor/preprocessing/normalization contract and `space_id`; source sampling policy and stream identity.
- **Index:** generation ID, build/manifest digest, eligible single-source membership, row ID and source-native sampled PTS; both source and model space match actual index artifacts.
- **Query/attempt/artifact:** normalized query identity/digest, separate run and attempt IDs, Top-K, Report V1 digest, publication path, status and limitations.

Absence of a required proof causes a named refusal; optional noncritical fields may be labeled `NOT_OBSERVED`. Never use `NOT_OBSERVED` as an evidence class.

### 4.4 Real-mode authorization contract: proposed new narrow seam

LAB `_validate_and_load_real_authorization` checks pilot envelope before media hashing and model opening. Canonical's `require_prepare_authorization` is intentionally more demanding for a **prepare/refine** workflow (its required stages include `refine`). The report-only product must not *fabricate refinement permission* just to reuse it; also must not weaken it.

**Design proposal:** use a Canonical-owned, dedicated **query-analysis capability check** that validates the existing owner policy record and exact source/revision/occurrence, purpose, query digest, model/root/weights/space, selected stream, index root, output/retention, expiry/revocation and allowed `decode/embed/index/query-or-retrieve` stages **before governed reads**. Recheck permission and source/snapshot/custody at relevant read, use and publication boundaries. A fresh scoped allowance must be real Owner authority; merely adding a CLI flag or LAB helper never authorizes protected source/model use.

Whether Canonical can express this without a new policy schema is **open for owner-approved contract design**. If the existing Canonical contract cannot represent query-only operation safely, retain REAL mode **BLOCKED** pending an explicitly versioned authorization successor. Synthetic tests remain eligible only within their existing narrow fixture rights.

Never silently infer production permissions from ADR-0003's removal of development source-auth checks.

### 4.5 Stream/sample and semantic-location contract: PROPOSED decision

A retrieved sample retains exact, attributable integer source PTS and rational source timebase. That is a **measured position of the sampled frame**, not observed semantic event start/end.

- For a source-bound ranked candidate with no separately observed coarse-window duration: `approx_semantic_location.location_kind="POINT"`, `time_domain="semantic_seconds"` and exact rational position; **no start/end interval fields** and `window_width_seconds="NOT_OBSERVED"`.
- If an actual coarse-width provenance exists, a separate `COARSE_WINDOW` representation may be allowed only with explicit source/method/uncertainty and remains nonbinding `MATCHED`.
- Preserve separate `sampled_timing.time_domain="source_pts"`, integer PTS, rational timebase and measured provenance. No `seconds × nominal FPS` for VFR or repeated PTS ordinal.
- Never create a zero-width half-open interval or arbitrary `+1.0s` interval and describe it as a valid nonempty event.
- `binding_eligible=false` until a separate deterministic refinement produces source-native edit-boundary evidence, then a genuine human editorial decision (Gate-3) independently authorizes use.

**Actual collision:** LAB CORE-01 `src/vip_fvs/real_source_service.py::_candidate_from_hit` yields `end = start` when no coarse width but labels it `half_open`; the Canonical original fabricated `end = start + 1.0`. LAB CORE-02 `build_point_semantic_location` already uses typed `POINT`. This discrepancy requires a **consumer-by-consumer compatibility audit** before changing `prepare_real_source` or any review-bundle interface. Do not coerce existing Gate-3 source intervals to a semantic point.

Default proposed: adopt typed `POINT` in the new Report V1 contract, preserve legacy consumers until a versioned, separately reviewed adaptation is safe.

### 4.6 Source-scoped index and retrieval contract

- Use the already shared `SemanticIndexEngine` protocol and existing persistence engine. No duplicated indexing/query implementation.
- Verify generation semantic-space identity, source revision/occurrence/custody binding, selected stream, timebase and sampling manifest **before** reuse. Existing same SHA in different occurrences is not automatic reuse permission.
- For initial scope, allow a **proven one-source** generation only. Multi-source generation with global Top-K and post-hoc filtering must **refuse** `MULTI_SOURCE_INDEX_UNSUPPORTED` or `SOURCE_SCOPE_UNPROVABLE` rather than claim `ZERO_MATCH`. Native source-scoped ranking can be separately designed if product needs it.
- Ensure a SearchHit cannot independently certify its stream index. Join to a verified source/sample row record and measured probe; reject missing/mismatched source, PTS, row, stream, rational timebase.
- Do not assume successful DB paths alone certify SQLite/manifest integrity. LAB `core_analysis.py` directly reads index SQLite and adapts multiple engine signatures; assess whether a small **read-only generation-evidence adapter** on the existing engine is safer than preserving its private schema coupling. No broad database migration.
- Keep query and index output as distinct evidence. Embedding scores are finite similarity values, **not calibrated probabilities**. If Top-K saturates without an exhaustive count, `total_eligible_matches="NOT_OBSERVED"`. True empty source-scoped result reports `ZERO_MATCH` with no invented positive result.

### 4.7 Report V1 and publication boundary

Propose keeping LAB's V1 schema identity and its essential field groups: outcome and limitations; source+custody+probe; authorization; runtime and model/processor/space; generation and sampling; normalized query; multiple matches (rank/raw score/source/sample PTS/rational position/optional thumbnail status); evidence availability; report artifact digest.

Published reports must:
1. Pass explicit version/schema validation and typed evidence checks.
2. Preserve Canonical `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, `EDITORIAL_INFERENCE` distinctions; `NOT_OBSERVED` is state.
3. Avoid self-referential digest ambiguity; deterministic canonical digest excludes the digest field itself.
4. Use confined destination paths, symlink refusal, no overwriting existing output, atomic or exclusive publication with fsync/durable repair policy appropriate to actual environment.
5. Never echo raw secret-bearing exceptions or unrelated protected absolute paths into a public CLI error payload. Errors carry stable named codes.
6. Treat zero eligible matches as a truthful successful analysis, not an erroneous `NO_SEMANTIC_MATCH` failure.
7. Record synthetic/real separately and genuine runtime-inference evidence only when observed; do not infer it from a REAL flag.

**Important source-based caveat:** LAB `publish_core_semantic_report` uses temp+fsync+hardlink no-clobber; this is a promising primitive, but directory symlink races, crash interruption and recovery have not been proven under Canonical integration. Retain the published V1 contract only after negative tests/failure injection.

### 4.8 CLI contract

Proposed public command: `vip-fvs analyze-local`, with one local video, one text query, index/output roots and a versioned JSON report. Required explicit source revision/attempt ID and model/source-specific scope must come from verified existing evidence or be explicitly supplied (never invented). Keep the authorized real model/device/probe fields only when valid; separately flagged `--fake-embedder` must be synthetic-test-only, never implicit fallback. Reject mixed fake/real flags. Never require `prepare-real` Gate-3 edit plan/render or artificial refine permission for a query report.

Existing Canonical `index-local`, `query-local`, `prepare-real` and every other command retain behavior except precisely approved CORE-01 correctness changes. CLI should not shell out to many CLI processes as orchestration.

## 5. Verification design, not test results

The **future authorized implementation** must start with tests-first (RED/GREEN) and include:

| Contract surface | Required synthetic/adversarial proof |
|---|---|
| CORE-01 stream/timebase/PTS | Generated CFR and VFR; audio-first video stream index 1/2; missing/invalid filter timebase refusal; nonnegative integer PTS; duplicate PTS ordinal; edit-list/source-origin refusal and non-nominal-FPS derivation |
| Legacy temporal consumer | No fabricated +1s; no zero-width half-open event; preserved refusal semantics and existing Gate-3 interval/refinement tests |
| Model + index | Incompatible model/processor/space, wrong generation, stale or corrupt SQLite/manifest, distinct occurrence same SHA, wrong stream/PTS/sample row; no global Top-K post-filter zero match |
| Query + report | Two+ ranked hits with exact score order, Top-K saturation/unknown total, real zero match, source-revision mismatch, truthful MATCHED vs MEASURED, typed POINT, no false caption/inference/QC claim |
| Security/policy | Missing/expired/revoked/scope-mismatched permission pre-read and pre-publication; snapshot mutation, source symlink and path escape, existing file/no-clobber, crash interruption, private exception disclosure |
| Execution + CI | Canonical existing Gate/FVS regression selection plus new focused unit/integration and generated-media tests on Python 3.11 and 3.14; no skipped required nodes treated as PASS; independent review, exact candidate SHA and hosted jobs |

LAB hosted 29 CORE-02 PASS per Python is a baseline for its own tree, **not** Canonical compatibility proof. No new Canonical test was executed for this design. All real model performance, protected archive readiness, quality advantage, editing/QC, and scale claims remain `NOT_OBSERVED`.

## 6. Proposed sequence and owner decision gates

**Design gate now (this document):** Owner chooses or revises approach C and the contract decisions below; independent reviewer can challenge unresolved interfaces. No source implementation or writing-plans packet before design approval.

**Then, after explicit design acceptance and a separate authorized code scope:** create a Canonical-owned implementation plan with isolated clean worktree, tests-first CORE-01 timing changes where needed, CORE-02 additive report/query seam, targeted Canonical regressions, independent code review and immutable-SHA hosted CI. Do not write directly to Canonical `main`, import whole LAB or touch dirty existing worktrees.

**Later, separately authorized:** genuine local model/assets and real media pilot, human review, Gate decisions, production render/export and QC. None is part of this design.

### Approval-required decisions

1. **Product and approach:** Is first Canonical slice `CORE-01 temporal fixes + CORE-02 single-video analyze-local/Report V1`, via narrow adaptation (C), correct?
2. **Temporal interface:** Adopt POINT for unknown semantic window width in the **new** report while preserving Gate-3's verified nonempty source interval contract and requiring explicit audit before modifying legacy prepare-real consumer?
3. **Runtime authority:** Approve designing a query-only validation seam using existing Canonical owner policy rather than pretending `refine` permission is required, with REAL mode blocked until its exact schema/authorization is approved?
4. **Scope and deployment:** Initial acceptance synthetic-only; no index-data migration, no Mega/batch import, no UI; Python 3.11/3.14 Canonical-owned validation and separate later real pilot?
5. **Implementation authorization:** Even if this design is approved, authorizing an actual Canonical code branch/PR, personnel/owner scope, merge or Gate promotion requires a **later explicit action**. Design approval alone cannot grant protected archive, models, egress or production.

### Rejected alternatives and reconsideration triggers

- **Bulk LAB tree merge:** rejected indefinitely unless Canonical authority/feature equivalence and lossless history/mode reconciliation are proven (no current reason to reconsider).
- **Whole orchestration/index rewrite:** reconsider only after a demonstrated existing engine incompatibility that a narrow adapter cannot resolve.
- **Multi-source native ranking:** reconsider only when one-source scope measurably blocks a real product need and source-scoped ranking can be proven.
- **Whole `src/vip_lab` transplant:** reconsider only if a specific Canonical reproducible regression cannot be tested more cheaply and safely in a small test fixture.
- **Real/persistent index migration now:** reconsider only with exact approved model/asset/policy/source identities, migration/recovery proof, realistic workload and explicit owner grant.
- **Unconditional zero-width interval compatibility:** rejected because it can falsely imply an event boundary.

## 7. Review status, unresolved facts, and source pointers

**VERIFIED:** Both source SHAs/trees remain pinned at publication-time check; the two independent reports and reconciliation are remote Git commits; shared vs distinct file contents/modes; existing Canonical source snapshot/index/model-space identity and bounded admission; LAB CORE-01/02 candidate module interfaces and previously hosted LAB CI.

**SOURCE-OBSERVED / DESIGN INFERENCE:** The LAB `end=start` half-open versus CORE-02 `POINT` mismatch, direct index SQLite coupling, code size, authorization adaptation need and contract-first architecture. Compatibility and security remain to be established through tests and code review.

**NOT_OBSERVED:** Exact Canonical implementation feasibility, currently approved real query-only capability, Canonical test/CI after integration, authentic SigLIP performance, protected media execution, source-native edit-boundary generation by this proposed entrypoint, human approval, rendering and QC.

**BLOCKED / NOT AUTHORIZED:** Source transfer and Canonical PR pending owner-approved design and separate implementation scope. Real-media/model/provider and Gate promotion remain separately controlled.

Primary source paths:
- Canonical `AGENTS.md`, `docs/INDEX.md`, `docs/architecture/CANONICAL_CONTRACTS.md`, `docs/decisions/ADR-0003-development-source-authorization-enforcement-removed.md`, `src/gate3/temporal.py`, `src/vip_fvs/{bounded_admission.py,_bounded_admission_fs.py,source_snapshot.py,pilot_authorization.py,real_source_probe.py,semantic_index.py,cli.py,real_source_service.py}` and `experiments/persistent_local_index/**` at pinned SHA.
- LAB `docs/ai-studio-tasks/MEGA_CORE_01_TEMPORAL_STREAM_AND_CLI_CORRECTNESS.md`, `MEGA_CORE_02_QUERY_DRIVEN_SEMANTIC_REPORT_V1.md`, `src/vip_fvs/{cli.py,core_analysis.py,core_report.py,real_source_service.py}`, `experiments/persistent_local_index/media.py` and three CORE-02 test files at pinned SHA.
- Reviews: `docs/reviews/2026-11-06_CHATGPT_INDEPENDENT_MAIN_COMPARISON.md`, `2026-11-06_CODEX_INDEPENDENT_MAIN_COMPARISON.md`, and `2026-11-06_CHATGPT_CODEX_MAIN_COMPARISON_RECONCILIATION.md` on their respective LAB read-only report branches.

**Terminal marker: VIP_CANONICAL_SELECTIVE_INTEGRATION_DESIGN_PROPOSED — OWNER_SIGNOFF_PENDING.**
