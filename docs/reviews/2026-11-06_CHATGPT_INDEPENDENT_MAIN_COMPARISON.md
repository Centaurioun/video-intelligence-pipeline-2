# VIP — Independent main-to-main integration comparison (ChatGPT)

**Review date:** 2026-11-06  
**Reviewer:** ChatGPT; independent GitHub repository/tree/blob inspection, not a Codex-derived verdict  
**Status:** READ-ONLY COMPARISON COMPLETED; INTEGRATION NOT AUTHORIZED / NOT EXECUTED  
**Destination of this report:** LAB documentation-only review branch. No modification to either source `main` or either DO_NOT_DELETE backup.

## 1. Immutable sources and method

| Role | Repository | Pinned main commit | Git tree |
|---|---|---|---|
| Canonical authority | `Centaurioun/video-intelligence-pipeline` | `3bfcc2ba221b36df6773e630b44479ec961d630a` | `032b7ea8908fa04f1d85cf0d57c1608d28864557` |
| LAB candidate | `Centaurioun/video-intelligence-pipeline-2` | `5eab58ea2a5424424cb95f2690654b91395425df` | `dae72052bbdbc1962713f302b50f8fa2fd78ed7f` |

Method: independently inspect both recursive GitHub Git trees (not working trees), match full repository-relative blob paths to exact Git object SHA, and inspect selected production sources, canonical governing docs and LAB scope/portability documents at the pinned commits. Historical LAB portability assessments are **dated evidence**, not current disposition: canonical PR #258's bounded-admission implementation is now present on canonical `main`. This review did **not** run integration tests, clone either private repository, exercise real media/models, or establish a cross-repository merge base. All compatibility statements below are source-review judgments, not executed migration evidence.

Tree evidence:
- Canonical tracked blobs: **1,869**; LAB tracked blobs: **732**.
- Common paths with **identical blob SHAs: 574**.
- Common paths with **different blob SHAs: 9**.
- Canonical-only paths: **1,286**; LAB-only paths: **149**.
- The shared path set comprises 583 tracked blobs; identity does not prove functional compatibility of new code.
- At `src/` specifically, **144 identical** paths, **2 divergent** paths, **2 canonical-only** paths, and **77 LAB-only** paths.
- Among LAB-only source paths, 70 are `src/vip_lab/**` synthetic/readiness harness modules and seven are `src/vip_fvs/**`: `batch_report.py`, `batch_retrieval.py`, `core_analysis.py`, `core_report.py`, `query_batch.py`, `synthetic_profiles.py`, and `three_arm_batch.py`.

Git tree API:
- Canonical: https://api.github.com/repos/Centaurioun/video-intelligence-pipeline/git/trees/032b7ea8908fa04f1d85cf0d57c1608d28864557?recursive=1
- LAB: https://api.github.com/repos/Centaurioun/video-intelligence-pipeline-2/git/trees/dae72052bbdbc1962713f302b50f8fa2fd78ed7f?recursive=1

## 2. Exact overlapping-path conflicts

All **nine** differing shared paths at the pinned trees:

| Path | Canonical blob SHA | LAB blob SHA | Preliminary disposition |
|---|---|---|---|
| `.gitignore` | `048cea2463295818e7fc5df96dda382f5f4f1f6e` | `505e594900049b2bac9266000433b59c2c08f5ca` | PRESERVE_CANONICAL; review only specific tracked media exceptions |
| `experiments/persistent_local_index/media.py` | `dcf53b4e12281a3cb6a7310eccee22919ca661d1` | `13b945b496f6e3469a8963e4714ea77cc39809aa` | CORE-01 semantic diff; targeted contract review |
| `experiments/persistent_local_index/tests/test_indexer.py` | `e6401ae79ea0960dbdf9470b35a23fb30ce8985f` | `22c1cdb5895684b3bbe12f4bb921eb75df04006f` | Test transplant candidate only after source contract mapping |
| `experiments/persistent_local_index/tests/test_media_pts.py` | `c5f46ed60fd19c44573e30fbe248992af1b617f7` | `e2ffea7e753ce5a99e9313318e4e1f9533594087` | Test transplant candidate; generated synthetic CFR/VFR fixture concerns |
| `src/vip_fvs/cli.py` | `c6ea6c043ea0525147e14b897d72b238f0ad2a69` | `bdf4350b584963b8e882cd7498377e3c4d8dcd4d` | SHARED INTERFACE; selective additions only, never wholesale overwrite |
| `src/vip_fvs/real_source_service.py` | `b9c7f1877ed3f091ee1c2a06f7c2f1e9ededb11d` | `31acf99b47edc6bb58f48cbfa1e302bc4e9ecc5f` | CORE-01 source-native hit validation/different interval semantics; high scrutiny |
| `tests/vip_fvs/integration/test_cli_acceptance.py` | `9e07bd6f312b66143573671bf3b389521a7a0317` | `446155126b306643f99f30c4401f8f370e750838` | Selective regression tests, not replacement |
| `tests/vip_fvs/integration/test_product_index_query.py` | `fddc67f7157a8a9519818eaf184f51f8964dc3e7` | `f19e5b14caa41b0df03353b1e72d9395003d63e7` | Selective regression tests |
| `tests/vip_fvs/unit/test_real_source_service.py` | `0a7eba5584e18b305b0fb4baba1b9c82c173773b` | `eaffe996cf1ddd643c38268b95cb413f8d6a9da0` | Selective CORE-01 validation tests |

**Important:** Identical `src/gate0/media/**`, `src/vip_fvs/source_snapshot.py`, `real_source_probe.py`, `pilot_authorization.py`, `semantic_index.py`, and `stream_identity_gate.py` blob identities are encouraging reuse signals, not a migration certificate. Canonical `src/vip_fvs/bounded_admission.py` and `_bounded_admission_fs.py` are canonical-only and must be preserved.

## 3. Functional comparison and candidate disposition

### 3.1 Canonical authority and already-implemented features — PRESERVE

Canonical main already contains the extensive Gate-0/1/2/3 and FVS modules, product/architecture records, governing `AGENTS.md` and state-maintenance rules. It also contains descriptor-relative, bounded file-admission primitives:
- `src/vip_fvs/bounded_admission.py`: `TrustedRoot`, `AdmissionLimits`, and `AdmittedFileBytes`; bounded validated bytes tied to file identity and digest.
- `src/vip_fvs/_bounded_admission_fs.py`: descriptor-based filesystem checks and symlink/path safety.

These two sources are absent from LAB main. The prior LAB `POST_MEGA17_CANONICAL_PORTABILITY_DECISION_MATRIX.md` called PR #258 open/draft based on **older SHAs**; the exact current canonical main includes the admitted implementation. Do **not** reintroduce the stale no-merge claim as a current fact, and do **not** overwrite the accepted canonical file-admission contract with LAB helpers.

Canonical-only documentation/PR/Gate infrastructure must stay; full-tree transplant or history merge is **REJECTED**.

### 3.2 CORE-01 PTS/stream/CLI corrections — CANDIDATE FOR SELECTIVE PORT

LAB changed `experiments/persistent_local_index/media.py`, `src/vip_fvs/real_source_service.py`, `src/vip_fvs/cli.py` plus focused tests; these are actual shared-file semantic deltas, not all-new modules.

In LAB `real_source_service._candidate_from_hit`, selected stream mismatches, noninteger/negative sample PTS, invalid rank and nonfinite scores are explicitly rejected. LAB computes a semantic sample location from PTS multiplied by a rational source timebase instead of canonical code's fallback using `timestamp_human` and an invented +1 second. This is a source-backed temporal/evidence improvement.

**Unresolved contract question:** LAB's no-coarse-window path uses `end = start` while still marking `endpoint_semantics = "half_open"`. That can represent an empty interval; CORE-02 instead deliberately uses a `POINT` semantic location. Before importing CORE-01, examine actual consumers/validators and decide whether a typed point or absent interval is required. Do not silently turn a zero-width interval into a measured event boundary.

Source: pinned `src/vip_fvs/real_source_service.py` at both SHAs and LAB CORE-01 task packet. Mandatory: targeted patch, tests-first, all existing canonical PTS/refinement authority regressions.

### 3.3 CORE-02 single-video semantic report — STRONGEST PRODUCT CAPABILITY CANDIDATE, NOT YET CANONICAL-READY

New LAB `src/vip_fvs/core_analysis.py` orchestrates a single-video query through already-present authorization, snapshot, real-source probe, semantic index and retrieval seams; `src/vip_fvs/core_report.py` defines Report V1, validation, source-native rational sample evidence and atomic no-clobber publication. `vip-fvs analyze-local` is newly added in the LAB `cli.py`. The report distinguishes `MATCHED` semantic relevance from `MEASURED` source-native PTS/timebase, uses point rather than fabricated event intervals, and retains `NOT_OBSERVED` for unsupported totals and model inference.

The CORE-02 Codex repair fixed precision-ordering, Top-K total epistemics, invalid index summaries, accidental `TypeError` retries, exception-detail leakage and unsupported inference claims. Exact LAB commit `5eab58ea...` had successful hosted GitHub Actions run 42170532090; importantly the **new CORE-02 pytest step had 29 PASS on Python 3.11 and 29 PASS on 3.14**; a separate earlier workflow step had 147 PASS on each, not 147 CORE-02-specific tests.

**Integration prerequisites, not verified by LAB CI:** `core_analysis` still interacts with private/low-level persistent-index SQLite and helper contracts; check the canonical schema, source-occurrence/snapshot/stream binding, authorization ordering, report publication under canonical admission and refusal policy, idempotency, output path safety, CLI compatibility, and deterministic digests. LAB validation with stub/fake runtime is not an authentic model or protected archive acceptance. Core module size and duplication deserve maintainability review; prefer existing canonical adapters instead of copying entire implementation without analysis.

Status: `CANONICAL_ADAPTER_CANDIDATE / REQUIRES_DESIGN_APPROVAL_AND_CANONICAL_TESTS`, **not** automatic adoption.

### 3.4 LAB-only batch/three-arm and synthetic Mega-03..17 — DO NOT MASS IMPORT

LAB-only `src/vip_fvs/batch_*.py`, `query_batch.py`, `synthetic_profiles.py`, `three_arm_batch.py` provide explicit fake-only synthetic batch/three-arm study paths. LAB-only `src/vip_lab/**` (70 tracked source paths) is an offline validation/readiness harness with separate owner/gate boundaries. These may be retained on LAB or contribute narrowly useful tests and contract ideas. They are **not** genuine multi-arm capability benchmarks, source-rights admission, editorial approval, renders, QC or gate promotion.

Keep separate from the immediate CORE-01/02 single-video product integration proposal. Import only with explicit, separate justification and owner scope.

### 3.5 Runtime and CI differences — DO NOT REPLACE CANONICAL CONFIGURATION

LAB `.gitignore` differs by explicit `!src/gate0/media/` exemptions; canonical `.gitignore` is not equivalent. Canonical and LAB workflows are distinct: canonical has broader Gate-0/Gate-2/history workflows, LAB has synthetic and reconciliation workflows. Build a new canonical focused test job only if an approved design demonstrates need; do not transplant LAB's workflow wholesale.

No runtime test was executed by this ChatGPT review. A green LAB hosted run proves its LAB inputs, not build compatibility after transplant onto canonical `main`.

## 4. Proposed minimal migration sequence (design recommendation only)

1. **Freeze** the two reviewed SHA/tree pairs and preserve existing DO_NOT_DELETE backups; verify current live heads again at any later execution point. Do not import from dirty local worktrees.
2. **Contract reconciliation first**: canonical bounded admission/authorization/snapshot/PTS/source occurrence/index schema, core command and report semantics, and existing canonical test baseline. Capture accepted/rejected alternatives and owner decision points. Independent Codex review should challenge these assumptions.
3. **CORE-01 patch candidate**: carefully port only verified stream/PTS/error and CLI correctness semantics with red/green tests; settle half-open zero-width point issue before accepting anything.
4. **CORE-02 additive candidate**: add only necessary report/analysis components or narrower adapters, and integrate the `analyze-local` entrypoint selectively with original canonical CLI. Enforce no fake-to-real promotion, source-native PTS, synthetic/real authorization separation and no silent measured edit boundaries.
5. **Independent canonical verification**: Python 3.11/3.14, focused/adversarial regression, generated CFR/VFR with nonzero absolute ffprobe stream index, zero/multi-hit, top-k saturation, index reuse, source-occurrence/stream identity, paths/symlinks, digest/no-clobber, CLI refusal privacy, existing canonical workflows, review and synthetic-only CI.
6. **Only after separate owner approval**: isolated canonical candidate branch/PR, exact reviewed commit, checks, independent integration acceptance. No canonical main direct writes. LAB-only Mega/batch components remain separate.

No actual implementation plan, integration branch, PR, model/video run, or canonical mutation was authorized or performed by this review.

## 5. Open owner decisions and evidence limits

| Question | Current classification |
|---|---|
| Adopt CORE-01 refinements and CORE-02 Report V1 as the initial selective scope? | **OWNER_DECISION_PENDING** |
| CORE-01 zero-width semantic half-open representation vs CORE-02 typed POINT | **UNRESOLVED_CONTRACT; consumer verification needed** |
| Reuse `core_analysis.py` whole or extract thin canonical-bound adapters? | **DESIGN_DECISION_PENDING** |
| Canonical bounded admission vs LAB path/hash semantics: which adapter boundary? | **REQUIRES_SOURCE/CONTRACT REVIEW** |
| Exact real SigLIP inference on the intended archive | **NOT_OBSERVED / NOT_AUTHORIZED** |
| Protected source media and provider/network activity | **NOT_AUTHORIZED** |
| Human editorial decisions, real frame refinement, rendering/QC and Gate promotion | **NOT_OBSERVED / NOT_AUTHORIZED** |
| Canonical implementation/merge permission | **NOT AUTHORIZED BY THIS COMPARISON** |
| Cross-repository merge-base / reproducible canonical integration tests | **NOT_OBSERVED** |

**Recommendation:** a deliberate, narrowly scoped integration design for CORE-01 temporal corrections + CORE-02 single-video semantic Report V1, preserving canonical existing modules, rather than bulk Git merge or LAB Mega harness transplantation. Require a second independently authored Codex report before owner approval, then reconcile only verified disagreements.

## 6. Evidence pointers

- Canonical main: https://github.com/Centaurioun/video-intelligence-pipeline/tree/3bfcc2ba221b36df6773e630b44479ec961d630a
- LAB main: https://github.com/Centaurioun/video-intelligence-pipeline-2/tree/5eab58ea2a5424424cb95f2690654b91395425df
- CORE-01 task: `docs/ai-studio-tasks/MEGA_CORE_01_CODEX_VERIFICATION_AND_REPAIR.md` at LAB pinned main.
- CORE-02 task: `docs/ai-studio-tasks/MEGA_CORE_02_QUERY_DRIVEN_SEMANTIC_REPORT_V1.md` and `MEGA_CORE_02_CODEX_VERIFICATION_AND_BOUNDED_REPAIR.md` at LAB pinned main.
- Older portability evidence (stale PR state): `docs/ai-studio-tasks/POST_MEGA17_CANONICAL_PORTABILITY_DECISION_MATRIX.md`, LAB pinned main.
- Hosted CORE-02 proof: https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/42170532090
- Governing canonical: `AGENTS.md`, `docs/INDEX.md`, `docs/project/00_PROJECT_CHARTER.md`, `01_CURRENT_STATE_AND_HANDOFF.md`, `02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`, and `STATE_MAINTENANCE_PROTOCOL.md`.

**Terminal label: CHATGPT_MAIN_COMPARISON_REPORTED — NOT AN INTEGRATION AUTHORIZATION.**
