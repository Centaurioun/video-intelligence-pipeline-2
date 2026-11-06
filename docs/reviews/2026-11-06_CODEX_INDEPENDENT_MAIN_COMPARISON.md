# Independent Canonical vs LAB Integration Review

**Review date:** 2026-11-06  
**Scope:** read-only source comparison and integration recommendation  
**Canonical pin:** `Centaurioun/video-intelligence-pipeline` at `3bfcc2ba221b36df6773e630b44479ec961d630a` (tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`)  
**LAB pin:** `Centaurioun/video-intelligence-pipeline-2` at `5eab58ea2a5424424cb95f2690654b91395425df` (tree `dae72052bbdbc1962713f302b50f8fa2fd78ed7f`)

## Executive decision

Do not merge LAB wholesale. The tree comparison is exceptionally asymmetric: against the pinned Canonical tree LAB has 149 LAB-only paths, 1,286 Canonical-only paths, 17 modified/renamed paths, and 1,452 changed paths overall (47,271 insertions and 402,807 deletions). This is consistent with LAB being a narrow candidate snapshot, not a drop-in successor. The useful integration boundary is a separately authorized, file-by-file extraction of CORE-01/CORE-02 mechanics after mapping each interface onto current Canonical contracts and running Canonical-owned tests.

No authentic media, model, provider, editorial, or QC execution was performed or inferred. The LAB synthetic suite and orchestration are evidence about deterministic control flow only. This review makes no claim that an integration is approved.

## Identity and method

The exact commit IDs and tree IDs above were resolved from Git objects. The review branch was observed at the LAB pin. The two original checkout directories had extensive unrelated local modifications; they were not edited. A detached LAB worktree was used for report preparation. To compare trees, the pinned Canonical commit was fetched by its exact SHA into the LAB object database; this did not change either branch. The comparison used Git tree/path differences, then source and test inspection at the pins. Remote advancement is not substituted for either pin.

Classification in this report:

- **VERIFIED:** directly observed Git/source/test fact at a named pin.
- **ASSESSMENT:** interpretation of code and tests, not runtime proof.
- **INFERENCE:** architectural recommendation derived from the contracts and observed code.
- **NOT_OBSERVED:** evidence unavailable or deliberately not exercised.
- **OWNER DECISION:** authorization or product choice that this review cannot make.

## Exact file-level comparison

At the pinned trees, Git reports 149 LAB-only files, 1,286 Canonical-only files, and 17 changed/renamed paths (1,452 changed paths total). The dominant LAB-only additions include `src/vip_lab/mega*`, `tests/vip_lab/test_mega*`, `src/vip_fvs/semantic_index.py`, `src/vip_fvs/source_snapshot.py`, `experiments/persistent_local_index/`, and corresponding schemas/specifications. The dominant Canonical-only areas include the broader `gate0`–`gate3` implementation, extensive governance/orchestration and state records, canonical workflows and their receipts, and unrelated repository capabilities. The changed-path count is a tree fact; it does not imply source compatibility.

The complete path set is reproducible with:

```sh
git diff --name-status 3bfcc2ba221b36df6773e630b44479ec961d630a 5eab58ea2a5424424cb95f2690654b91395425df
```

LAB’s current `vip-ai-studio-synthetic-ci.yml` and `post-mega17-reconciliation-contract.yml` coexist with a different workflow set from Canonical, including removed canonical-history and Gate regression workflows. Workflow names, test selectors, and branch conditions are not interchangeable evidence. Exact per-file content should be reviewed as a transfer patch, not inferred from the aggregate tree statistic.

## Findings by requested area

### CORE-01: time, stream identity, PTS, indexing, CLI

**VERIFIED in LAB source:** `src/vip_lab/mega10/pts_fixture_diagnostics.py` models rational timebases, PTS snapping and ordinal resolution, duplicate-PTS occurrence ambiguity, half-open intervals, and refusal of nominal-FPS derivation. `src/vip_lab/mega10/temporal_request.py` carries source revision, stream index, PTS and timebase fields and marks measurement as needed. `src/vip_lab/mega15/temporal_preflight.py` explicitly refuses synthetic-to-real escalation, forged source measurement, candidate-as-exact-cut, and invalid stream namespace claims. `src/vip_fvs/source_snapshot.py` verifies retained snapshot bytes and derives temporal authority from those bytes; its strict path refuses unapplied nonzero ISO-BMFF edit-list origin rather than normalizing it.

**ASSESSMENT:** these are useful fail-closed designs and better temporal distinctions than a semantic timestamp treated as an edit point. Most MEGA temporal tests exercise fixtures and offline preflight. They do not establish correct parsing for arbitrary authentic containers, decoder behavior, or source-native timing across VFR, discontinuities, edit lists, or all stream layouts. LAB’s batch-oriented interfaces also differ materially from Canonical’s more mature source authority, Gate-3 refinement and evidence records.

**Recommendation:** `ADAPT_SELECTIVELY` the pure rational-PTS rules and explicit refusal semantics only after mapping them to Canonical’s established temporal types and evidence vocabulary. Keep LAB’s synthetic fixtures and MEGA workflow `KEEP_LAB_ONLY`. Do not transfer snapshot/parser authority without independent parser review and Canonical-owned adversarial fixtures. Never promote semantic/model offsets (`MATCHED`/semantic candidates) into source-native PTS (`MEASURED`) or a frame-accurate cut.

### CORE-02: query-driven single-video retrieval and Report V1

**VERIFIED in LAB source:** `src/vip_fvs/semantic_index.py` delegates generation specification, indexing and queries to `experiments/persistent_local_index`. `experiments/persistent_local_index/model_space.py` derives a deterministic semantic-space ID by hashing canonical JSON of a `SemanticSpace`. LAB exposes both batch retrieval and query catalog/report structures, while the MEGA-14 orchestrator can execute a deterministic three-arm scenario.

**ASSESSMENT:** persistent generation identity and explicit semantic-space identity are sound compatibility concepts. A synthetic deterministic engine can test report assembly and ranking contracts but cannot establish embedding quality, model compatibility, real-video indexing, useful retrieval, latency, or editorial acceptance. A manifest/catalog batch API is not automatically the requested single-video user contract. The delegation boundary must be tested for model revision, preprocessing, dimensions, normalization, tokenizer/image encoder pairing, and stale generation refusal.

**Recommendation:** `ADAPT_SELECTIVELY` the semantic-space identity schema and a narrow query/result contract, provided Canonical owns model asset identity, source snapshot provenance, authorization, and report authority. `BLOCKED_PENDING_EVIDENCE` for any persistent-index data migration or claimed compatibility; require exact encoder/preprocessor asset identities and a Canonical fixture-built index round trip. `KEEP_LAB_ONLY` the three-arm synthetic report/orchestration as a benchmark harness.

### LAB-only batch retrieval, three-arm synthetic workflows and Mega workstreams

**VERIFIED:** LAB contains `vip_lab` and many MEGA modules/tests, while the exact tree comparison shows a narrow subset of the overall Canonical system. Three-arm synthetic code composes deterministic scenario hits across `VIP_V1_BASE`, `VIP_V2_BASE`, and `VIP_V2_SO400M` profiles. This can check deterministic orchestration, schema validation, refusal paths, and evidence-state propagation.

**ASSESSMENT:** the harness is useful for reproducible contract regression and issue discovery. Synthetic hits are supplied by the scenario engine; therefore no ranking/model superiority, actual similarity, video coverage, temporal localization, human usability, or QC result follows. Batch all-source reports and Mega gates impose maintenance and governance cost if copied into Canonical without a Canonical product need and owner-selected lifecycle.

**Decision:** `KEEP_LAB_ONLY` the synthetic orchestration, Mega workstreams, and batch report CLI. Consider porting individual pure validators only if a concrete Canonical defect and exclusive owner path are named.

### Canonical-only authority and contracts

**VERIFIED:** Canonical’s pinned tree retains far more files and workflows than LAB. Its current governing materials (including `AGENTS.md`, `docs/INDEX.md`, `docs/architecture/CANONICAL_CONTRACTS.md`, Gate-0/architecture handoffs, and state maintenance/orchestration rules) define evidence classes, source and revision provenance, authority boundaries, local-only Gate-0 restrictions, and preservation of source media. These are not replaceable by LAB implementation notes or synthetic readiness receipts.

**Decision:** `PRESERVE_CANONICAL` all Canonical governance, gate contracts, authority/refusal semantics, source custody, source identity and state maintenance rules. Migration proposals must cite the exact Canonical contract and add no relaxation by implementation accident.

### Identity, snapshots, custody, authorization and persistent index

**ASSESSMENT:** LAB snapshot-byte hashing and semantic-space hashing address different identities. Source identity/revision and immutable snapshot digest identify input bytes; semantic-space ID identifies embedding semantics/configuration; index generation identifies a materialization over inputs and a space. None substitutes for the others. A valid persistent index must be bound to all three, plus encoder/preprocessor asset revision and applicable policy. Source custody/authorization remains Canonical authority, and a locally available file does not imply permission to process it.

**Decision:** `ADAPT_SELECTIVELY` the identity decomposition. `BLOCKED_PENDING_EVIDENCE` any persisted index adoption until stale/corrupt generation refusal, source revision changes, semantic-space changes, authorization changes, atomic publication and recovery are proven under Canonical contracts.

### Temporal evidence and VFR

**VERIFIED:** LAB distinguishes semantic candidates from source PTS measurements and includes refusal guards in synthetic temporal preflight. Its fixture diagnostic requires explicit occurrence selection for duplicate PTS and refuses deriving timing from nominal FPS.

**ASSESSMENT:** VFR, repeated timestamps, decode reordering, edit-list offsets, discontinuities, missing terminal duration, and stream selection require source-native evidence. Semantic seconds or matched offsets cannot be used as frame coordinates. Synthetic diagnostics are not measurements.

**Decision:** `ADAPT_SELECTIVELY` typed temporal distinctions and refusal tests. Keep all actual measurements `NOT_OBSERVED` in this review.

### Security, privacy and publication

**VERIFIED:** Canonical policy prohibits committing credentials and protected media, requires provenance, and preserves originals. LAB modules inspected include refusal-oriented synthetic logic. This task did not perform a secret scan, dynamic security assessment, media access, provider request, or real atomic-publication failure test.

**ASSESSMENT:** report/index publication should be temp-write, validate, fsync/atomic replace as appropriate, with fail-closed recovery and no partial current pointer. Logs and receipts must avoid source paths or sensitive metadata leakage where policy requires. Any user-visible authorization check must be checked at processing time, not inferred from an earlier index.

**Decision:** `PRESERVE_CANONICAL` security and custody controls. `BLOCKED_PENDING_EVIDENCE` transfer of snapshot or publication code until failure injection, privacy review, and authorization revocation tests exist.

### Tests, CI, portability, maintenance and debt

**VERIFIED:** LAB has focused MEGA test modules and synthetic workflows; pinned path comparison shows workflow divergence, not shared CI. Canonical has a larger suite and governance/test surface. No tests or CI jobs were run for this review.

**ASSESSMENT:** LAB’s modular synthetic tests are valuable for pure contracts but can drift from Canonical APIs. The extensive MEGA layering, duplicate fixtures/schema versions, and orchestration create ongoing maintenance cost. Portability and execution coverage are `NOT_OBSERVED` from this read-only source comparison; no performance measurements are claimed.

**Decision:** Canonical CI must own any adopted behavior. Require a small, targeted Canonical test slice and relevant full regression workflow selected by Canonical owners. Do not import LAB CI wholesale.

## Integration decision matrix

| Candidate | Decision | Benefit | Conflict / risk | Minimum evidence and authorization |
|---|---|---|---|---|
| Canonical contracts, authority, custody and state rules | `PRESERVE_CANONICAL` | Keeps source and evidence claims governed | Broad candidate code could bypass authority | No relaxation; owner approval for any contract change |
| LAB rational PTS and explicit occurrence/refusal rules | `ADAPT_SELECTIVELY` | Clear handling of duplicates, rational clocks and false cut claims | Fixture-only coverage; type/interface mismatch | Canonical unit tests and adversarial parser fixtures; owner-scoped transfer |
| LAB snapshot byte verification / temporal binding | `BLOCKED_PENDING_EVIDENCE` | Possible reproducible provenance root | Parser/container coverage, edit lists and authorization scope | Independent security/parser review, real authorized fixture set, fail-closed recovery tests |
| LAB semantic-space identity | `ADAPT_SELECTIVELY` | Prevents incompatible embeddings sharing index | Hash alone omits asset/runtime facts unless complete schema binds them | Canonical schema review and golden identity compatibility tests |
| LAB persistent index implementation | `BLOCKED_PENDING_EVIDENCE` | Reusable local index engine | No proven Canonical lifecycle, migration or real encoder compatibility | Exact asset identity, rebuild/mismatch refusal, atomicity/recovery, authorized fixture round trip |
| LAB CORE-02 Report V1 single-video contract | `ADAPT_SELECTIVELY` | Query-driven user value and explicit evidence report | Batch-centric API and report authority mismatch | Canonical interface proposal, UX/product owner decision, single-video contract tests |
| LAB synthetic three-arm and Mega harness | `KEEP_LAB_ONLY` | Deterministic contract/benchmark scaffolding | Synthetic output is not product evidence; high maintenance burden | Keep synthetic labels; no integration unless an owner identifies a concrete test gap |
| LAB workflows | `REJECT` as direct transfer | Some selectors may inform test design | Workflow divergence, selectors and permissions differ | Recreate only within Canonical CI after CI-owner review |
| Any claimed model/video/editorial/QC result | `BLOCKED_PENDING_EVIDENCE` | None from synthetic source alone | Fabrication risk | Authorized real-media/model/human evidence and separately approved gate |

## Smallest useful scope and sequence

1. **No code transfer in this review.** Preserve the pinned source and evidence boundary.
2. If authorized, write a Canonical-owned mini-spec for one CORE-02 query against one authorized source revision, with explicit source snapshot, semantic-space, index generation, and report evidence identities.
3. Independently extract only pure temporal invariants (rational timebase, duplicate PTS occurrence, no nominal-FPS derivation) into Canonical types and tests; do not bring over MEGA orchestration.
4. Add Canonical tests for source revision mismatch, changed semantic space, stale index, authorization refusal, atomic publish interruption, and VFR/duplicate-PTS cases using explicitly authorized fixtures.
5. Only after local contract tests pass, evaluate an authorized authentic fixture/model run and human editorial review under the applicable owner gate. Synthetic success remains a separate status.

Owner decisions required: whether CORE-02 is a Canonical product priority; whether any media/model assets may be used; which model/preprocessor/runtime identities are approved; whether a persistent index is desired and its retention policy; and which Canonical owner grants a bounded implementation lane. No such authority is inferred here.

## Limitations and unresolved evidence

- No tests, CI, benchmarks, authentic video/model/provider operation, editorial review, QC, or media export were run.
- Git verifies the pinned commit/tree identities and path counts; this report does not certify full line-by-line semantic equivalence or security of every changed file.
- Canonical and LAB remote advancement is reported separately from the pinned comparison; pins remain the sole comparison baseline.
- The Canonical working checkout had 238 pre-existing changed paths and the LAB working checkout had local changes. Neither was modified by this analysis.
- No ChatGPT comparison report or review branch was accessed.
- Publication is a documentation action only and does not constitute integration approval.

## Sources

- Canonical `AGENTS.md`, `docs/INDEX.md`, `docs/architecture/CANONICAL_CONTRACTS.md`, `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`, and current architecture handoffs at `3bfcc2ba221b36df6773e630b44479ec961d630a`.
- LAB `src/vip_lab/mega10/pts_fixture_diagnostics.py`, `src/vip_lab/mega10/temporal_request.py`, `src/vip_lab/mega15/temporal_preflight.py`, `src/vip_fvs/source_snapshot.py`, `src/vip_fvs/semantic_index.py`, `experiments/persistent_local_index/model_space.py`, tests and workflows at `5eab58ea2a5424424cb95f2690654b91395425df`.
- Pinned-tree path comparison of those exact commit IDs.
