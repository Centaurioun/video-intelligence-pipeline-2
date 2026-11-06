# VIP — Independent ChatGPT/Codex main-comparison reconciliation

**Date:** 2026-11-06  
**Author:** ChatGPT, independent cross-review of two separately committed read-only reports  
**Status:** COMPARISON RECONCILED; DESIGN/IMPLEMENTATION/INTEGRATION NOT AUTHORIZED  
**Publication:** documentation-only LAB review branch, descended from exact pinned LAB main  
**No modifications:** Canonical main, LAB main, either DO_NOT_DELETE backup, application code, tests, workflow, model, media or provider.

## 1. Immutable evidence and reviewer independence

| Input | Exact Git ref | Report |
|---|---|---|
| Canonical source | `Centaurioun/video-intelligence-pipeline@3bfcc2ba221b36df6773e630b44479ec961d630a` | Tree `032b7ea8908fa04f1d85cf0d57c1608d28864557` |
| LAB source | `Centaurioun/video-intelligence-pipeline-2@5eab58ea2a5424424cb95f2690654b91395425df` | Tree `dae72052bbdbc1962713f302b50f8fa2fd78ed7f` |
| ChatGPT independent review | `cf3b02cc9e87a7d79ee21bd34bbb9449a9362cd7` (parent: pinned LAB) | `docs/reviews/2026-11-06_CHATGPT_INDEPENDENT_MAIN_COMPARISON.md`, blob `b7f1230966f751d6b33280b2b1b7999874857ae2` |
| Codex independent review | `a4e93bcaae244587aa36a13ff4f7a5db3da8083b` (parent: pinned LAB) | `docs/reviews/2026-11-06_CODEX_INDEPENDENT_MAIN_COMPARISON.md`, blob `fcda00e681ca318b6c8ffc9c38110f46cceb5bb2` |

Both reports were independently published on separate review branches. GitHub commits for both modify only their respective Markdown review file. Both report the same source pins. Codex reports not consulting ChatGPT's work; this review confirmed the branch ancestry and document-only diff, not the agent's unobservable internal reading history.

This reconciliation independently refetched both full, **non-truncated** GitHub recursive tree API responses, compared tracked full paths, blob SHA **and file mode**, checked key code path identities and revisited selected source code. It performed no integration test or live media/model run.

## 2. Definitive tracked-tree difference arithmetic — CORRECTED

| Mutually exclusive category | Count | Meaning |
|---|---:|---|
| Present at same path, **same blob SHA and same Git mode** | **566** | Identical tracked entries |
| Present at same path, **same blob SHA but different mode** | **8** | Content identical; executable bit changed (Canonical `100755`, LAB `100644`) |
| Present at same path, **different blob SHA** | **9** | Actual content changes |
| Only in Canonical | **1,286** | No same-path tracked LAB entry |
| Only in LAB | **149** | No same-path tracked Canonical entry |
| **Common-path differences including mode** | **17** | 8 permission differences + 9 content differences |
| **Unique different paths, including one-sided paths** | **1,452** | 1,286 + 149 + 17 |
| Canonical total tracked blobs | **1,869** | 566 + 8 + 9 + 1,286 |
| LAB total tracked blobs | **732** | 566 + 8 + 9 + 149 |

**Correction to original ChatGPT report:** its "574 identical" counted identical blob **content**, but overlooked eight differing executable modes. It correctly identified nine content-divergent same-path files but did not enumerate eight mode differences. This reconciliation corrects that incomplete metadata assessment instead of rewriting the original independent review.

**Credit to Codex:** its **17 changed** and **1,452 changed paths** numbers are verified, provided "17 modified/renamed" is rephrased accurately as **nine content changes plus eight mode-only changes**; no rename is needed to explain the number.

### Eight same-blob, different-mode scripts

All are `100755` in Canonical and `100644` in LAB:
- `scripts/bootstrap-references.py`
- `scripts/build-reference-pack.py`
- `scripts/gate0-run.sh`
- `scripts/preflight-remaining-work-launch.py`
- `scripts/render-remaining-work-launch-pack.py`
- `scripts/stage-b-build-app.sh`
- `scripts/verify-remaining-work-atlas.py`
- `scripts/verify-workspace.sh`

**Impact:** preserving Canonical modes is necessary. A wholesale LAB tree replacement might remove execute permission from scripts in addition to removing Canonical-only features. The mode differences are meaningful even with exactly identical source bytes.

### Nine content-divergent same-path files

`.gitignore`; `experiments/persistent_local_index/media.py`; `experiments/persistent_local_index/tests/test_indexer.py`; `experiments/persistent_local_index/tests/test_media_pts.py`; `src/vip_fvs/cli.py`; `src/vip_fvs/real_source_service.py`; `tests/vip_fvs/integration/test_cli_acceptance.py`; `tests/vip_fvs/integration/test_product_index_query.py`; `tests/vip_fvs/unit/test_real_source_service.py`.

## 3. Specific correction of Codex-only path claims — FACTUAL ISSUE

Codex's "dominant LAB-only additions" passage mentions `src/vip_fvs/semantic_index.py`, `src/vip_fvs/source_snapshot.py`, and `experiments/persistent_local_index/`. The first two **are NOT LAB-only**; each has the same blob SHA at both pinned trees:

| Path | Canonical and LAB identical SHA |
|---|---|
| `src/vip_fvs/semantic_index.py` | `e81fd15ee243b59b02bace14131c9d6b39b66701` |
| `src/vip_fvs/source_snapshot.py` | `4d172d1a20e559d4bb26ebd4fc0eb978f44bc501` |
| `experiments/persistent_local_index/model_space.py` | `6d1ec3ff52076e4c3d85c18f1fa4cc81550d7384` |

The wider `experiments/persistent_local_index/` directory **also exists in both**; at least `media.py` and its two tests have changed. Therefore describing the entire persistent-index subtree as LAB-only is wrong. These existing, identical engines and identity types must not be reintroduced as new Canonical modules.

**Actual LAB-only CORE-02 product sources:**
- `src/vip_fvs/core_analysis.py` (LAB blob `42437e5ac2ee5f7963a96461ce8c171177e1f939`);
- `src/vip_fvs/core_report.py` (LAB blob `e42695becf9c0edaaf672cd29343a144631372c3`);
- the LAB-only `analyze-local` parser/dispatch sections within the **divergent**, shared `src/vip_fvs/cli.py`.

Related LAB-only report/analysis tests:
- `tests/vip_fvs/unit/test_core_analysis.py`;
- `tests/vip_fvs/unit/test_core_report.py`;
- `tests/vip_fvs/integration/test_core_analyze_local_cli.py`.

This matters: Codex's CORE-02 discussion emphasizes existing index/semantic-space modules and batch frameworks while underemphasizing the actual new single-video orchestration/report implementation. ChatGPT's original report correctly identified these new sources, though it did not prove they are Canonical-compatible.

**Actual Canonical-only authority sources**:
- `src/vip_fvs/bounded_admission.py` (blob `995f7435979035c86f4735577d9d57d2d2041b40`);
- `src/vip_fvs/_bounded_admission_fs.py` (blob `bc1db5388d419057d0e7cc375283605e8832dd3d`).

These are in pinned Canonical `main`; older LAB documents labeling this as an open PR state are stale. Preserve the current Canonical API and file-mode/permission authority.

## 4. What both reviews agree on — VERIFIED CONVERGENCE

1. **REJECT wholesale merge or LAB-as-replacement.** Canonical-only governance, Gate systems, CI, work history, safeguards and product capabilities must be preserved.
2. **ADAPT_SELECTIVELY source-native rational PTS, stream identity, repeated-PTS refusal and evidence separation.** Never use nominal FPS to infer VFR frames or model/semantic timestamps as exact edits.
3. **KEEP_LAB_ONLY** Mega-03..17 and synthetic multi-arm/batch orchestration unless a separately approved, concrete Canonical need emerges. Synthetic tests do not establish actual model ranking quality, editorial acceptance or Gate promotion.
4. **PRESERVE_CANONICAL** source custody, permission boundaries, human editorial authority, immutable source media, evidence class rules, Gate rules, and CI ownership.
5. **BLOCKED_PENDING_EVIDENCE** for real model execution, protected media, external inference, production export, actual QC, and any claim of Canonical runtime compatibility.
6. **Require an owner-approved design before writing code**: source identity/revision, stream/timebase, semantic space, index generation, report digest/publication, and failure/authorization behavior must be mapped explicitly.

Convergence is architectural and security-oriented; it is not an implementation signoff.

## 5. High-value divergences and their resolution

| Question | ChatGPT assessment | Codex assessment | Reconciled evidence-based resolution |
|---|---|---|---|
| Exact change count | 9 content changes, original omission of permissions | 17 changed/renamed, 1,452 changed paths | **Both observations reconciled:** nine differing blobs **plus eight executable modes**, yielding 17 shared-path differences and 1,452 differing paths |
| Existing local index and source snapshot | Common/identical source code at pins | Incorrectly calls the named modules/subtree LAB-only | **ChatGPT supported by exact tree SHA:** do not transplant identical engines; audit their consumer compatibility with newly proposed modules |
| Where CORE-01 value actually resides | Focuses concrete `media.py`, `real_source_service.py`, `cli.py` deltas and tests | Focuses LAB-only `vip_lab/mega10/15` preflight | **Prioritize concrete shared-file CORE-01 patch set**; optional Mega refusal ideas are a separate test-source option |
| Where CORE-02 product value actually resides | Identifies `core_analysis.py`, `core_report.py`, and `analyze-local` | Describes Report V1 but centers preexisting `semantic_index.py`, `model_space.py` and batch code | **Prioritize actual new CORE-02 module/API contract**; existing engine is a dependency, not a new import |
| No-coarse-window semantic interval | Explicit source-derived concern: LAB CORE-01 `end=start` with half-open interval vs CORE-02 POINT | Broad PTS caution; does not specifically resolve this collision | **Open design blocker:** inspect consumers/validators; require typed POINT or explicit absence, not empty half-open semantic interval misused as event |
| Canonical bounded file admission | Notes accepted Canonical-only admission primitives | General Canonical authority preservation | **Explicitly preserve** `bounded_admission.py` + descriptor-FS; assess any CORE-02 path/read seam before reuse |
| Index data movement | No need to transplant existing identical index engine; integration fixtures still necessary | Blocks persistent-index adoption/migration until identity/recovery proofs | **Distinguish code vs data:** existing same-blob engine needs no wholesale import; do not migrate or silently reuse persisted LAB generations without canonical-accepted provenance, manifest, policy and recovery checks |
| Testing and status | Cites prior hosted LAB CORE-02 CI and its limitations | Correctly notes no tests run during Codex comparison | **Both valid:** historical LAB CI shows isolated LAB acceptance; neither read-only report performed Canonical integration tests |

## 6. Selective integration candidate matrix — NOT AUTHORIZED

| Item | Decision | Specific path or seam | Required proof before code approval/acceptance |
|---|---|---|---|
| Canonical Gate/rights/custody/PTS/evidence/CI | **PRESERVE_CANONICAL** | Existing Canonical contracts, `src/gate0/**`, `src/gate3/**`, `src/vip_fvs/bounded_admission.py`, `src/vip_fvs/_bounded_admission_fs.py` | No weakened protections or executable-mode regressions |
| CORE-01 media probe, duplicate PTS, stream selection | **ADAPT_SELECTIVELY** | `experiments/persistent_local_index/media.py`, shared-service/CLI contracts | Targeted source diff, consumer audit, generated CFR/VFR and nonzero absolute stream-index tests |
| CORE-01 candidate PTS validation / coarse semantic location | **ADAPT_SELECTIVELY** only after POINT contract decision | `src/vip_fvs/real_source_service.py`, unit and integration tests | No fabricated +1 s; no empty half-open interval claimed as event; `MATCHED` not promoted to `MEASURED` |
| CORE-02 single-video Report V1 | **ADAPT_SELECTIVELY — highest product-value candidate** | `src/vip_fvs/core_analysis.py`, `src/vip_fvs/core_report.py`, `cli.py:analyze-local`, three new CORE-02 test files | Contract design, precise source/space/generation identities, fail-closed authorization, canonical-specific tests, Python 3.11/3.14 acceptance |
| Existing semantic index, source snapshot, model-space identity code | **PRESERVE_CANONICAL; NO DUPLICATE IMPORT** | `src/vip_fvs/semantic_index.py`, `source_snapshot.py`, `experiments/persistent_local_index/model_space.py` | Prove the **new consumers** obey existing APIs, not that identical code can be copied |
| Persistent LAB index generations / model assets | **BLOCKED_PENDING_EVIDENCE** | Data/assets, NOT source-code duplicates | Exact model+processor identity, rights, stale generation/revision refusal, atomicity and recovery |
| LAB batch/three-arm/Mega runtime | **KEEP_LAB_ONLY** | `src/vip_lab/**`, batch and synthetic modules | New owner-scoped benchmark/test need; no fake evidence upgrade |
| LAB workflow and `.gitignore` | **REJECT DIRECT TRANSPLANT** | `.github/workflows/**`, `.gitignore` | Canonical-owned CI changes only when needed; preserve executable modes and media ignore policy |

No action above authorizes a Gate, real-source run, model download, merge or production release.

## 7. Proposed design-first sequence and acceptance

**Phase A — design research only (next eligible activity):**
1. Read current Canonical `AGENTS.md`, four live `docs/project/` handoffs, `docs/architecture/CANONICAL_CONTRACTS.md`, current product decisions and relevant Gate contracts at exact pinned SHA; verify current `main` before any later work.
2. Produce a **contract-to-contract migration design** covering CORE-01's differing shared-file behavior and CORE-02's new Report V1. Name every producer, consumer, identity and refusal/authority boundary, and reject wholesale merges.
3. Choose a **single semantic-location representation** across review and Report V1. Resolve `end=start` half-open vs typed `POINT` without manufacturing edit boundaries.
4. Specify how Canonical bounded admission, immutable source snapshot, source occurrence/revision, selected absolute stream, measured PTS/timebase, model/preprocessing space, index generation, query and report digest interlock.
5. Record options (reuse modules vs smaller canonical adapters), tradeoffs, rejected alternatives, reconsideration triggers and explicit Owner approval points.

**Phase B — only after separate design approval and implementation authorization:**
- Use isolated clean Canonical branch/worktree and tests-first changes; do not touch dirty local worktrees.
- Minimal CORE-01 and CORE-02 implementation candidates only, not LAB wholesale.
- Re-run Canonical's relevant existing Gate/FVS/adversarial suites plus new focused tests (3.11/3.14), synthetic CFR/VFR/nonzero absolute video-stream, PTS duplicates, source revocations, source/generation/model mismatches, zero/multiple matches, top-k saturation, no-clobber, digest validation, atomic publication/crash injection, secret/refusal privacy.
- Independent review, hosted Canonical CI tied to immutable SHA, then owner-gated merge. No fake-to-real promotion.

**Phase C — separately gated authentic pilot:**
Protected archive access, model loading/provider use, authentic video runs, precise refinement, editorial decision, render/QC and Gate promotion each require specific additional owner authorization and supporting measured/human evidence. This report grants none.

## 8. Explicit caveats and owner decisions

- **VERIFIED:** two independent report commits and parents; exact source SHA/tree pins; non-truncated tree path/mode SHA counts; key source path identities; published LAB hosted CORE-02 execution from prior verified GitHub evidence.
- **SOURCE-OBSERVED/ASSESSMENT:** CORE-01 `end=start` / half-open inconsistency, CORE-02 typed `POINT`, candidate code boundaries and inferred integration risks. These still require consumers/tests.
- **NOT_OBSERVED:** complete compatibility against Canonical's test corpus, any Canonical integration branch CI, authentic model/media/editorial/QC, failure-injection recovery, migration data integrity, full semantic/code audit of every Git path.
- **OWNER DECISION PENDING:** approve the design scope (CORE-01 PTS/correctness + CORE-02 report), approve the semantic POINT contract, choose narrow adapter vs reuse strategy after design, authorize any Canonical code branch/PR, set separate real-pilot rights/model/retention grants if ever desired.

The previous two review documents remain unchanged as independent historical observations. This document is the authoritative **reconciliation proposal**, not a governing spec or grant. Canonical main and backup repositories remain untouched.

**Terminal state: CHATGPT_CODEX_MAIN_RECONCILIATION_REPORTED — IMPLEMENTATION_NOT_AUTHORIZED.**
