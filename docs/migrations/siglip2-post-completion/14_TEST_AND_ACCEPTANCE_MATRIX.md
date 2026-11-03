# Future Test and Acceptance Matrix

**Information state:** `INFERRED_DESIGN` + `SNAPSHOT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Repository snapshot:** `main@34106df55fc07a18fd8594f379cd143710ad0127`

## Purpose

Define what future migration work must prove without editing current tests now.

The actual implementation remains subject to Superpowers TDD: each behavior change begins with a failing test, then the minimal implementation, then full relevant regression verification.

## Existing Test Families to Preserve

Current migration-relevant test areas include:

- `experiments/persistent_local_index/tests/test_model_space.py`;
- `experiments/persistent_local_index/tests/test_local_model.py`;
- `experiments/persistent_local_index/tests/test_storage.py`;
- `experiments/persistent_local_index/tests/test_indexer.py`;
- `experiments/persistent_local_index/tests/test_search.py`;
- `experiments/persistent_local_index/tests/test_search_materialization.py`;
- `experiments/persistent_local_index/tests/test_source_lifecycle.py`;
- `experiments/persistent_local_index/tests/test_cli_e2e.py`;
- `tests/vip_fvs/unit/test_local_semantic.py`;
- `tests/vip_fvs/adversarial/test_v5_semantic_identity.py`;
- relevant real-mode authorization tests under `tests/vip_fvs/`.

Paths are snapshots and must be refreshed at V1 completion.

## Matrix

| ID | Behavior to prove | V2 Base | So400m | Preferred test level | Acceptance |
|---|---|---:|---:|---|---|
| T001 | V1 profile reproduces preserved V1 semantic-space contract | Required | Preserve | Unit | exact expected identity/fields |
| T002 | V2 Base is a distinct semantic space from V1 despite 768 width | Required | Preserve | Unit/adversarial | mixing fails closed |
| T003 | So400m is distinct from V2 Base | N/A | Required | Unit/adversarial | mixing fails closed |
| T004 | unresolved revision/hash/digest cannot open runtime | Required | Required | Unit | explicit failure |
| T005 | processor digest change changes semantic-space identity | Required | Required | Unit/adversarial | IDs differ |
| T006 | text preprocessing contract change changes semantic-space identity | Required | Required | Unit/adversarial | IDs differ |
| T007 | loader is local-only and remote fallback is absent | Required | Required | Unit/integration | no network fallback path |
| T008 | remote code remains disabled | Required | Required | Unit/integration | `trust_remote_code=False` or equivalent |
| T009 | requested MPS unavailable fails closed | Required | Required | Unit | no CPU fallback |
| T010 | session output width equals profile width | 768 | 1152 | Unit/integration | mismatch fails |
| T011 | float32 row width derives from profile | 3072 | 4608 | Unit | exact byte width |
| T012 | append/committed-byte accounting handles profile width | Required | Required | Storage integration | counts exact |
| T013 | crash-tail reconciliation uses profile row width | Required | Required | Storage integration | tail recovered safely |
| T014 | search opens matrix with profile column count | 768 | 1152 | Search integration | expected shape |
| T015 | query vector wrong width fails | Required | Required | Search unit | explicit mismatch |
| T016 | fake vectors deterministic for requested dimension | 768 | 1152 | Unit | repeated bytes/values stable |
| T017 | V1 fixed 768 fixtures remain valid regression coverage | Required | Preserve | Regression | V1 tests remain green |
| T018 | exact same source can exist independently in different semantic spaces | Required | Required | Integration | no cross-space collision |
| T019 | index root does not silently adopt sibling incompatible space | Required | Required | Storage/index integration | explicit mismatch |
| T020 | real-mode authorization is checked before runtime/model use | Required | Required | Adversarial/integration | unauthorized request stops first |
| T021 | source PTS/timebase/refinement behavior unchanged | Required | Required | Regression | exact prior behavior |
| T022 | semantic timestamp remains candidate evidence | Required | Required | Regression/audit | no evidence upgrade |
| T023 | V2 text preprocessing matches frozen processor contract | Required | Required | Unit/integration | exact tokenization parameters/identity |
| T024 | image preprocessing matches frozen processor contract | Required | Required | Unit/integration | exact attributable config |
| T025 | local model identity is revalidated after open | Required | Required | Unit/integration | mutation fails closed |
| T026 | benchmark candidate records exact code/model/runtime identity | Required | Required | Manifest/schema | complete provenance |

## V2 Base Acceptance Gate

V2 Base migration is not complete merely because one embedding call works.

Minimum acceptance:

1. completed V1 remains reproducible;
2. V2 Base profile has immutable model revision and exact digests;
3. V2 Base semantic-space ID differs from V1;
4. full SigLIP2 preprocessing contract is attributable;
5. local loader is offline/fail-closed;
6. model/session output dimension is verified;
7. generic storage/index/search regression suite is green;
8. V1 regression suite remains green;
9. relevant VIP FVS authorization/provenance tests remain green;
10. a bounded local V2 Base smoke is recorded if execution was authorized;
11. no full-archive index was required;
12. no retrieval-winner claim is made.

Freeze the V2 Base candidate only after this gate.

## So400m Acceptance Gate

Minimum acceptance:

1. V2 Base remains independently reproducible;
2. exact So400m revision/digests are frozen;
3. profile records 384 / patch14 / 1152 from the frozen checkpoint;
4. 1152-D synthetic write/recovery/query path passes;
5. no generic production path remains coupled to `768 * 4`;
6. 384-pixel preprocessing contract is attributable;
7. local model smoke confirms 1152-D output if execution is authorized;
8. runtime memory/performance observations are recorded without extrapolating full archive;
9. V1 and V2 Base regression coverage remains green;
10. no cross-space vector reuse is possible;
11. no benchmark-winner claim is made.

Freeze the So400m candidate only after this gate.

## 2026-10-11 Controlled Task 0 Test Mapping

**Code/test source:** canonical and preserved V1 migration surface at `748818e867ce08ccc2367bad21df7d83eaf51d70` / `3586eeaa904fc5a2e6a2745078611886f482f3de` (relevant source/test paths are identical). **Exact pre-existing evidence:** the seven-file 125-test receipt from preflight commit `b296b5ca5a805d151412cf848fa397266fe23052`, imported unchanged at `docs/agent-runs/run-20261011-vip-v2-task0-controlled-refresh/preflight-checks.json`. **Additional execution:** `docs/agent-runs/run-20261011-vip-v2-task0-controlled-refresh/test-execution-results.json`.

The additional acceptance scope was the six remaining `experiments/persistent_local_index/tests/test_*.py` modules plus the complete `tests/vip_fvs/` test tree. After fixture pre-screening, the additional command collected 699 tests: 689 passed and 10 `test_media_pts.py` cases skipped because the inherited synthetic `/tmp/opt_media/{cfr,vfr}.mp4` fixtures were absent. Those two synthetic fixtures were generated without overwrite and only the 16-case `test_media_pts.py` module was rerun; it passed 16/16. Final additional-scope unique result: 699 passed, 0 failed, 0 skipped. Thirteen test cases overlap the prior 125-test receipt (`test_local_semantic.py` 5, `test_semantic_index.py` 4, `test_retrieval_adapter.py` 4); they are not double-counted. Combined distinct model-free baseline evidence is therefore **811 passed, 0 failed, 0 skipped** (125 prior + 686 additional non-overlapping cases). This is not a model/runtime reproduction result.

| ID | Current test mapping at source `748818e…` | V1 synthetic result | V2/SO400M acceptance state |
|---|---|---|---|
| T001 | `experiments/persistent_local_index/tests/test_model_space.py` | V1 semantic-space identity tests passed in imported 125 record. | V2 profile not present; candidate identity not observed. |
| T002 | `test_model_space.py`; `tests/vip_fvs/adversarial/test_v5_semantic_identity.py` | Existing V1 semantic identity coverage passed. | Equal-width V1/V2 profile separation remains future acceptance. |
| T003 | No V2/SO400M profile test exists in this tree. | Not applicable to V1 behavior. | Not implemented / not observed. |
| T004 | `experiments/persistent_local_index/tests/test_local_model.py` | Eight local synthetic identity/validation tests passed. | V2 immutable revision/hash refusal not implemented. |
| T005 | `test_model_space.py`; `tests/vip_fvs/adversarial/test_v5_semantic_identity.py` | Processor-identity differentiation coverage passed. | Profile-bound V2 processor identity remains future acceptance. |
| T006 | `test_model_space.py` | V1 semantic-space contract coverage passed. | Full SigLIP2 text contract remains not observed. |
| T007 | `test_local_model.py`; `test_embedding.py` | Offline/fail-closed V1 synthetic cases passed; no real loader opened. | V2 local-only adapter not implemented. |
| T008 | `test_local_model.py`; static source search | Existing V1 behavior checked; no `AutoModel`/`AutoProcessor` path exists. | SigLIP2 `trust_remote_code=False` acceptance not implemented. |
| T009 | `test_embedding.py`; `test_local_model.py`; `experiments/persistent_local_index/tests/test_cli_e2e.py` | Mocked MPS-unavailable/no-fallback tests passed. | No real V2 device probe; MPS remains not observed. |
| T010 | `test_embedding.py`; `tests/vip_fvs/unit/test_local_semantic.py` | Existing 768-column V1 outputs passed. | 1152 output/profile validation not implemented. |
| T011 | `test_storage.py`; `test_indexer.py` | Existing 768 × float32 byte geometry passed. | 4608-byte SO400M row geometry not implemented. |
| T012 | `test_storage.py`; `test_indexer.py`; `test_cli_e2e.py` | V1 committed-byte and restart behavior passed. | 1152 append accounting remains future acceptance. |
| T013 | `test_storage.py`; `test_indexer.py`; `test_cli_e2e.py` | V1 tail recovery cases passed. | Profile-derived 1152 recovery remains future acceptance. |
| T014 | `test_search.py`; `test_search_materialization.py` | V1 search/materialization tests passed; source search confirms read dimensions derive from `SemanticSpace.embedding_dim`. | 1152 query integration not tested. |
| T015 | `test_search.py`; `test_model_space.py` | V1 wrong-space/width refusal cases passed. | 1152 query refusal remains future acceptance. |
| T016 | `tests/vip_fvs/unit/test_retrieval_adapter.py`; `test_model_space.py` | Deterministic V1 fake-vector coverage passed. | Deterministic 1152 fake-vector behavior not implemented. |
| T017 | All persistent-index test modules and complete `tests/vip_fvs/` tree, combined with the imported 125-test record | Distinct model-free synthetic baseline: 811 passed, 0 failed, 0 skipped. | V1 regression requirement has a synthetic baseline; runtime reproducibility remains blocked. |
| T018 | `tests/vip_fvs/integration/test_multi_source_indexing.py`, `test_multi_source_retrieval.py`, `test_product_index_query.py` | Synthetic independent index/query tests passed. | Cross-profile candidate separation remains future acceptance. |
| T019 | `test_storage.py`; `tests/vip_fvs/integration/test_multi_source_lifecycle.py`; `tests/vip_fvs/unit/test_semantic_index.py` | Existing incompatible-space/lifecycle tests passed. | Sibling 1152 profile adoption remains future acceptance. |
| T020 | `tests/vip_fvs/adversarial/test_v4_pre_runtime_authorization.py`; `test_real_source_prepare.py`; `tests/vip_fvs/unit/test_real_source_service.py` | Synthetic authorization ordering tests passed; no model/source was opened. | V2 runtime selector ordering remains future acceptance. |
| T021 | `experiments/persistent_local_index/tests/test_media_pts.py`; `tests/vip_fvs/unit/test_real_source_temporal_authority.py`; `tests/vip_fvs/unit/test_refinement_adapter.py` | Synthetic PTS/timebase and refinement tests passed. | No claim of actual-media behavior. |
| T022 | `tests/vip_fvs/unit/test_real_source_temporal_authority.py`; `test_refinement_adapter.py`; `tests/vip_fvs/adversarial/test_temporal_authority.py` | Candidate/nonbinding temporal authority tests passed. | No evidence-class or timestamp authority change. |
| T023 | `experiments/persistent_local_index/tests/test_embedding.py` | V1 `padding=max_length` fixture tests passed. | SigLIP2 token IDs, mask, lowercasing, truncation and pooling not observed. |
| T024 | `tests/vip_fvs/integration/test_local_semantic_synthetic.py`; `tests/vip_fvs/integration/test_product_index_query.py` | V1 synthetic image/text path tests passed. | V2 processor-owned image preprocessing not implemented or measured. |
| T025 | `experiments/persistent_local_index/tests/test_local_model.py` | Synthetic asset identity/revalidation tests passed. | No V2 bundle was inspected; V2 revalidation not observed. |
| T026 | `tests/vip_fvs/unit/test_review_bundle.py`; `tests/vip_fvs/integration/test_review_bundle_persistence.py` | Existing V1 provenance-envelope tests passed. | V2 benchmark-candidate code/model/runtime manifest not yet implemented. |

The 639 refresh candidate recorded that its then-current plan text said “all 12 steps” while protocol 19 has Steps 1–13. That wording was corrected in the plan candidate later accepted for planning through PR #69. This test map records all 13 protocol steps; no migration code or Gate surface changed.

### Post-adoption clarification

The owner-reviewed plan blob cited by this refresh was subsequently corrected to reference all 13 numbered refresh steps and accepted for planning through PR #69. The accepted blob remains `78127a9199a912531d5b2240eed66e93814d83f3`; the merge is `7f4a5ce1baf7de2aa580f1043502458336bf57fe`. The preceding paragraph describes the earlier candidate's observation and remains historical evidence; the current plan status does not authorize implementation.

## Tests That Should Remain Separate

Do not collapse all candidate behavior into one parameterized test if doing so would hide historical regressions.

Keep explicit coverage for:

- preserved V1 behavior;
- V2 Base behavior;
- So400m 1152-D behavior;
- cross-space rejection.

Parameterization is appropriate for generic storage/search behavior only after candidate-specific identity tests exist.

## Benchmark Tests Are Different

Migration acceptance tests answer:

“Does this candidate run correctly and reproducibly?”

The later benchmark answers:

“Which candidate retrieves useful moments better for this archive, at what cost?”

Passing this matrix is therefore a prerequisite for benchmark eligibility, not evidence of benchmark superiority.

## Required V1-Completion Refresh

Before turning this matrix into implementation tasks:

- map every behavior to the final current test file/function;
- remove tests already satisfied by final V1;
- add missing RED tests to the future migration plan;
- update command lines to the final project test runner;
- identify any changed authorization boundary;
- verify the final suite’s baseline status before migration work begins.
