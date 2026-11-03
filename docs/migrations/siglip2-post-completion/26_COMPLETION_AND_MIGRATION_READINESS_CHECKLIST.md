# V1 Completion and Migration Readiness Checklist

**Information state:** `TEMPLATE` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`

## Usage

Complete this checklist after V1 completion and after running `19_POST_COMPLETION_REFRESH_PROTOCOL.md`.

Status values:

- `PASS`
- `FAIL`
- `BLOCKED`
- `NOT_APPLICABLE`

A required `FAIL` or `BLOCKED` prevents Gate B/full-migration implementation under the H decision below. It does not alter or satisfy any of the 56 predicates. The separately defined Gate A decision appended after H is the only possible Task 1 exception while full-migration readiness remains blocked.

## 2026-10-11 SHA-Bound Current-Evidence Amendment (Pre-PR #69 Merge)

The following status is an immutable description of evidence as recorded before PR #69 merged. Its pending-plan and proposed-adoption statements are superseded by the post-adoption successor overlay below; the historical matrix and receipts remain preserved.

This dated evidence overlay supplements the reusable checklist below; it does not change any condition ID, meaning, checkbox, or the A–G/Go-No-Go structure. Authority base: canonical main `748818e867ce08ccc2367bad21df7d83eaf51d70`. Preserved V1: `3586eeaa904fc5a2e6a2745078611886f482f3de`. Evidence sources: Task 0 refresh `6396779e397dc9dba659f4887471de4c6d30aced`; V1 artifact identity `989c1bc6923833a11cfd11b7b756ef1f4ffbe192`; bounded authentic synthetic MPS receipt `634bfed47aec8464c8ca61b15c376f2950c21060`; cross-repository comparison `61e22acffcc3dcfeddeaa2f4a2b40e0f8693c74a`; gap reconciliation and E01–E10 refresh `229d08f564fb8c21a7a119fc900eaac82cb64cd0`; current runtime/F07 receipt `ce3f570016f3f13e9091fb6989f3a9d3ea783c7d`; separate G03 receipt `988b8790cc45ad1c1093f0d1ebbae15ab0716f38` (product candidate `e956722a0fc2109eb4651ce728e919e691162511`). The exact condition-by-condition evidence dispositions are in the linked [56-item Task 0 matrix](../../agent-runs/run-20261011-vip-v2-task0-plan-owner-review/task0-gate-matrix.json), whose SHA-256 is `594aa9d79af2384594abf149a5fb50f8db61ae4b84ea6112b871faeb5110b860`; it contains each existing A01–G05 ID once and retains the original meanings. Matrix `PASS_*`, `PARTIAL`, and `BLOCKED` qualifiers describe evidence scope and do not check any template box or mean implementation readiness.

Current evidence distinctions:

- **V1 completion:** the local-first V1 product candidate `e956722a0fc2109eb4651ce728e919e691162511` and preserved migration source above are distinct. The pinned identity evidence records SigLIP Base revision `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`, checkpoint SHA-256 `2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8`, processor digest `4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980`, preprocessing digest `d11ccb80f15d358a11bdb070e92e2d889005874b7db15823d5f10d9b2533b14a`, and 768-D float32/L2 SemanticSpace `3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a`.
- **Recorded verification:** 811 distinct model-free tests and a separate 1,290-pass historical G03 regression receipt are not rerun or combined. One authentic local synthetic image/text MPS pass is bounded current-runtime evidence, not broad reproducibility or semantic correctness.
- **F07:** `PASS_CURRENT_RUNTIME_RECEIPT_ONLY`; the current runtime receipt does not establish an exact installable dependency lock, wheel hashes, or full historical environment reconstruction.
- **Design and planning:** design remains `OWNER_APPROVED_FOR_PLANNING`; Step 12 recommends `RETAIN_DESIGN`. The implementation plan remains `PENDING_OWNER_PLAN_REVIEW` until the owner accepts the exact final plan SHA.
- **V2 and protected operations:** V2 Base revision/checkpoint/processor/preprocessing identity and model-acquisition authorization remain `BLOCKED`; protected/archive-media execution is explicitly blocked and unauthorized. No inference or media access is authorized.
- **Semantic uncertainty:** token IDs, embedding-table row count, and model/tokenizer semantic correctness remain `NOT_OBSERVED`.
- **Current decision:** `NO_GO_BLOCKED`. The GO box below remains unchecked. H3-C05 remains `UPHOLD_UNAUTHORIZED`; V2 Bootstrap remains `BLOCKED`.

The five Step 10 documents were adopted by PR #69. The owner decision and original review provenance remain recorded in the [owner-review packet](../../agent-runs/run-20261011-vip-v2-task0-plan-owner-review/owner-review-packet.md), PR #69's durable owner comment, and the exact merge SHA above.

## 2026-10-11 Post-Adoption Successor Overlay

The owner accepted original migration-plan blob `78127a9199a912531d5b2240eed66e93814d83f3` for planning through the durable PR #69 decision; PR #69 merged at canonical `main@7f4a5ce1baf7de2aa580f1043502458336bf57fe`. The accepted plan status is `OWNER_APPROVED_FOR_PLANNING`; the successor plan document is not the originally reviewed blob, and no implementation authority was granted. Step 10 documents 11, 12, 24, 25, and this checklist were adopted through that merge. The requested migration snapshot/test/runtime updates (03, 07, 08, 10, 13, 14, 18) and source refreshes (20, 21) are reconciled in the current consolidation candidate.

The successor [Task 0 readiness overlay](../../agent-runs/run-20261011-vip-v2-post-adoption-consolidation/task0-readiness-overlay.json) and [remaining gates](../../agent-runs/run-20261011-vip-v2-post-adoption-consolidation/remaining-gates.md) preserve all 56 A01–G05 condition IDs and protocol Steps 1–13. F07 remains exactly `PASS_CURRENT_RUNTIME_RECEIPT_ONLY`; tokenizer semantic uncertainty remains `NOT_OBSERVED`. Full Task 0 / V2 Bootstrap readiness remains `NO_GO_BLOCKED` / `BLOCKED`. The overlay may identify a candidate future strictly model-free Task 1 assessment if applicable A–D conditions are satisfied; it is not a GO decision or Task 1 execution authorization. A separate independently reviewed exact-scope readiness decision and owner execution authorization remain necessary.

## A. V1 Completion Identity — Required

- [ ] **A01** V1 completion is explicitly verified, not inferred from an agent summary.
- [ ] **A02** Exact V1 completion SHA recorded.
- [ ] **A03** Optional tag/release identity recorded or explicitly `NOT_APPLICABLE`.
- [ ] **A04** Candidate ancestry verified against canonical repository history.
- [ ] **A05** No unresolved dirty/uncommitted state is required for reproduction.
- [ ] **A06** Exact V1 model ID recorded.
- [ ] **A07** Exact V1 model revision recorded.
- [ ] **A08** V1 weights digest recorded.
- [ ] **A09** V1 processor/preprocessing identity recorded.
- [ ] **A10** V1 semantic-space ID recorded.

## B. V1 Verification — Required

- [ ] **B01** Final relevant V1 test suite command recorded.
- [ ] **B02** Final relevant V1 tests pass or every pre-existing failure is explicitly understood.
- [ ] **B03** V1 local runtime evidence required for later benchmark remains available.
- [ ] **B04** V1 candidate remains reproducible without V2 code/model state.
- [ ] **B05** No V1 evidence needed for benchmark was destructively removed.

## C. Preparation Refresh — Required

- [ ] **C01** Current `AGENTS.md` reviewed.
- [ ] **C02** Current project handoff/state docs reviewed.
- [ ] **C03** ADR-0002 confirmed not superseded.
- [ ] **C04** `03_V1_BASELINE_SNAPSHOT.md` refreshed.
- [ ] **C05** `07_MIGRATION_SURFACE_SNAPSHOT.md` refreshed.
- [ ] **C06** `08_HARDCODE_AND_ASSUMPTION_REGISTER.md` refreshed.
- [ ] **C07** `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md` refreshed.
- [ ] **C08** `14_TEST_AND_ACCEPTANCE_MATRIX.md` mapped to final tests.
- [ ] **C09** `18_STALENESS_AND_REVERIFY_REGISTER.md` reconciled.
- [ ] **C10** external evidence/source receipts refreshed.
- [ ] **C11** a completed post-completion refresh receipt exists from `30_post-completion-refresh-receipt-template.yaml` and is bound to the exact V1 completion SHA.

## D. Current Migration Design — Required

- [ ] **D01** Final V1 architecture compared with `10_TARGET_MODEL_PROFILE_DESIGN.md`.
- [ ] **D02** Duplicate/unnecessary abstraction avoided.
- [ ] **D03** Current Superpowers brainstorming completed.
- [ ] **D04** Migration design explicitly approved.
- [ ] **D05** Current writing-plans implementation plan exists.
- [ ] **D06** Planned work does not widen unrelated temporal/edit/render/QC scope.
- [ ] **D07** Shared-contract writer ownership/isolation strategy is explicit.

## E. V2 Base Model Identity — Required Before Real V2 Execution

- [ ] **E01** Model acquisition explicitly authorized.
- [ ] **E02** Exact immutable V2 Base revision selected.
- [ ] **E03** Exact local weights digest calculated.
- [ ] **E04** Processor/tokenizer asset inventory recorded.
- [ ] **E05** Processor digest calculated.
- [ ] **E06** Image-preprocessing digest calculated.
- [ ] **E07** Exact output dimension verified from frozen checkpoint/runtime.
- [ ] **E08** Full text preprocessing contract recorded.
- [ ] **E09** Local model root is approved/canonical.
- [ ] **E10** No mutable upstream `main` identity is being used as runtime authority.

If acquisition is intentionally delayed while code-only work proceeds, mark E items `BLOCKED` and constrain the implementation plan accordingly.

## F. Runtime / Dependency Identity — Required Before Real V2 Execution

- [ ] **F01** Python version/executable recorded.
- [ ] **F02** Transformers exact version recorded.
- [ ] **F03** PyTorch exact version recorded.
- [ ] **F04** NumPy/Pillow/tokenizer dependencies recorded.
- [ ] **F05** MPS availability/fallback environment recorded where relevant.
- [ ] **F06** FFmpeg/ffprobe identity recorded where indexing uses them.
- [ ] **F07** exact dependency lock/receipt exists.
- [ ] **F08** offline/local-only loader probe passes under the frozen environment.

## G. Authorization — Required When Applicable

- [ ] **G01** model acquisition authorization is current.
- [ ] **G02** protected/archive-media execution authorization is current before real media use.
- [ ] **G03** network/provider/cloud behavior remains within explicit authorization.
- [ ] **G04** full-archive indexing is still deferred.
- [ ] **G05** no Gate promotion is being inferred.

## H. Go / No-Go

Migration may start only if:

- all required A–D items are `PASS`;
- E–G items required by the first planned execution step are `PASS`;
- any deferred E–G item is explicitly represented as a hard boundary in the plan.

### Decision

- [ ] `GO_FOR_AUTHORIZED_MIGRATION_SCOPE`
- [ ] `NO_GO_BLOCKED`

### Evidence fields

```text
v1_completion_sha:
current_main_sha:
post_completion_refresh_receipt:
migration_design:
implementation_plan:
model_acquisition_authorization:
real_media_authorization:
blocking_items:
reviewer:
decision_date:
```

## Separate Gate A Task 1 Preparatory Entry Decision

This decision is distinct from H and from `GO_FOR_AUTHORIZED_MIGRATION_SCOPE`. Task 1 is software implementation associated with the V2 migration program; its synthetic-only/model-free scope is not documentation-only work. Gate A is not active unless the exact ADR-0002 amendment and every coordinated subordinate contract change have been explicitly accepted by the owner and canonically adopted together.

Gate A may be considered after verified V1 completion even when the full-migration receipt and H decision remain blocked, but only with all of the following evidence:

- current exact-main SHA and current blob identities for this checklist, ADR amendment, subordinate contracts, accepted plan, readiness overlay, and refresh receipt;
- preserved V1 completion identity and completed refresh history with protocol Steps 1–13 retained as written;
- a complete exact-main scoped assessment of the existing 56 predicates: A–D evidence and disposition for Task 1, and explicit E–G applicability and exclusions; every Task 1-required A–D predicate must be freshly evidenced and satisfied under its unchanged pass criteria. Any required FAIL, BLOCKED, unresolved condition, or qualification that does not satisfy the existing criterion blocks Gate A; an expressly permitted `NOT_APPLICABLE` remains only where that predicate already allows it. Literal checklist `PASS` and qualified overlay statuses such as `PASS_WITH_LIMITS` and `PASS_PLANNING_ONLY` retain their distinct meanings and are not normalized or promoted. No predicate is added, removed, redefined, or marked passed by Gate A;
- a separate Gate A outcome of `TASK1_PREPARATORY_ENTRY_APPROVED` or `TASK1_PREPARATORY_ENTRY_BLOCKED`, with the full-migration H outcome recorded separately;
- an independent review accepting the exact Gate A decision SHA/tree; and
- one separate explicit owner Task 1 execution authorization that binds the decision and accepted-plan provenance, exact allowed files and operations, execution method, execution branch and base SHA, and expiry/supersession rules.

The permitted operation scope is only the accepted plan's Task 1 closed, validated three-profile semantic-space contract, including frozen profile validation, deterministic mapping to the existing `SemanticSpace` contract, synthetic identity fixtures, model-free tests, V1 identity-preservation regression, independent feature review, and bounded verification. The owner authorization must name the exact Task 1 file scope from the accepted plan. No additional approval/token layer is required: this one owner authorization is the execution-start authority and must include all matching bindings.

Gate A never authorizes Task 2 or later, dependency/environment changes, real model or processor identity/acquisition/load, inference/MPS, media, provider/cloud/egress, benchmark, full-archive indexing, Gate promotion, or production integration. It does not change `GO_FOR_AUTHORIZED_MIGRATION_SCOPE`, a historical blocked receipt, full Task 0 `NO_GO_BLOCKED`, V2 Bootstrap `BLOCKED`, H3-C05 `UPHOLD_UNAUTHORIZED`, F07 `PASS_CURRENT_RUNTIME_RECEIPT_ONLY`, or tokenizer semantics `NOT_OBSERVED`. Missing, stale, contradictory, or mismatched evidence means `TASK1_PREPARATORY_ENTRY_BLOCKED`.

## Adopted model-free synthetic Task 2–5 exception — execution not authorized

**Status:** `OWNER_ACCEPTED — CANONICALLY_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The exact coordinated candidate `ae3939b9c0d98c24809246099c025bc3a60a0d50` / tree `11c9089016f9b0b1a8bd5ee2704d3022d74ef421` was adopted by PR #91 merge commit `25c29c07a8010db551a2ac08fcde72a9147c25d3`. The exception permits consideration of separately granted T2-SYN storage/indexer, T3-SYN search/fake seam, and T4-SYN mocked adapter slices concurrently on disjoint, exact plan-listed paths after fresh base/interface checks. T5-SYN is serial after the first three exact interfaces are independently verified and accepted together and needs a separate later grant. T5's grant must include and side-effect-screen `tests/vip_fvs/unit/test_real_source_service.py` and bind no-model-open/no-asset/no-cache/no-network guards, or narrow its authorization-order claim to the safe tests authorized. Adoption alone makes no slice READY or executable.

**Current Task 1 dependency reference for this proposal (2026-10-19):** the reviewed Task 1 candidate is `ff23e6af46ced80297c8fbc124c6ddf0b0ed288a` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`; its exact accepted `model_profile.py` source blob is `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`. The candidate is represented on current canonical main `342e6fbaa25d28511844b274bce7f927e2c0420d` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`. Its interface review remains `ACCEPT_WITH_LIMITS` for the model-free synthetic interface only. These commit/tree/blob identities are provenance bindings, not a substitute for the exact review artifact or for checking the accepted interface at each consuming task's exact base. A future grant must cite that review evidence and verify its bound interface descriptor at the exact base; missing, stale, or mismatched evidence blocks that task. This reference establishes no authentic tokenizer/model semantics, Task 2–5 readiness, adoption, or execution grant.

This is a separate implementation-entry decision, not H and not `GO_FOR_AUTHORIZED_MIGRATION_SCOPE`. It adds, removes, redefines, satisfies, waives, or reclassifies no A01–G05 condition; changes no existing evidence class or status; and cannot turn the full Task 0 or Gate B disposition from `NO_GO_BLOCKED`. It does not edit the blocked receipt or matrix. It preserves all 13 refresh steps and Gate A's Task 1-only scope. Synthetic results cannot establish authentic model, processor, runtime, device, media, benchmark, or full-migration readiness. Tasks 6 onward remain behind Gate B.

No slice is READY from this proposal or adoption alone. Each worker requires a fresh exact base/contract check and a separate owner grant binding paths, operations, safe tests, environment, method, isolated branch/base, expiry, supersession, and no-network/no-model/no-media restrictions. Independent verification and acceptance apply to exact candidates before T5 can be considered.

## Proposed residual native-Base Task 4/5 source-entry decision — not active

**Status:** `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. This distinct proposal concerns genuine native Base Task 4 and checked CLI Task 5; it does not expand or relabel T4-SYN/T5-SYN. It adds, removes, redefines, satisfies, waives, or reclassifies no A01–G05 predicate and changes neither H, the 13 refresh steps, blocked receipt, Gate A Task 1-only scope, nor Task 0/Gate B `NO_GO_BLOCKED`.

If the exact tree is independently reviewed, owner-adopted and canonically adopted (or accepted applicable Gate B is current), Task 4 still needs its own exact source/test/operations/environment/branch/base grant and an independently accepted Task 1 `ModelProfile` interface fingerprint bound to the exact Task 4 base. An exact previously accepted immutable source snapshot is sufficient only when its acceptance receipt/contract records and binds that fingerprint; missing acceptance/fingerprint, stale base, or mismatch blocks launch, and planning approval alone does not count. Task 5 needs a separate grant, accepted Task 2 and Task 3 interface fingerprints bound to its exact base (or an exact accepted snapshot whose receipt binds both), and accepted Task 4 interface for final verification whose acceptance receipt binds the Task 1 fingerprint. Only plan-listed exclusive paths are contemplated. Fake-injected model-free tests may establish guarded source and CLI wiring only; they do not establish authentic tokenizer, preprocessing, mask/pooling, MPS/device, or retrieval quality. No model/processor/assets/cache, network, real/protected media, benchmark, Gate promotion, or Task 6+ work is implied. V1 no-flag behavior, source authorization ordering, semantic-space/generation isolation, and source PTS/timebase remain contract requirements.

Before Task 5 BUILD starts, its exact base must bind either (a) an independently accepted Task 4 interface fingerprint whose acceptance receipt binds it to Task 4's exact source SHA, with that same fingerprint bound to Task 5's exact consuming base, or (b), only when Task 4 BUILD overlaps, an exact frozen Task 4 interface fingerprint independently reviewed and bound to both Task 4's exact source base and Task 5's exact consuming base. Final Task 5 VERIFY still requires the independently accepted Task 4 interface at the exact frozen SHA, matching the consumed fingerprint and retaining the Task 1 fingerprint binding. Any Task 4 interface change makes Task 5 descendants stale; stop and rebind/review before continuing.

## Proposed synthetic Task 9 preparatory entry decision (T9-SYN) — not active

**Status (refreshed 2026-10-19):** PR #86 merged the reviewed T9-SYN governance documentation at `dab471b768811a7c1e3791e4f79de4539bd12d33`; the preserved M3 record remains a pre-adoption adjudication. This documentary discrepancy is retained. T9-SYN remains `NOT_AUTHORIZED_FOR_EXECUTION` because it has no separate current execution grant. This proposal concerns only the model-free synthetic regression test slice on `tests/vip_fvs/integration/test_three_profile_synthetic_space_contract.py`. It adds, removes, redefines, satisfies, waives, or reclassifies no A01–G05 predicate and changes neither H, the 13 refresh steps, blocked receipt, Gate A Task 1-only scope, nor Task 0/Gate B `NO_GO_BLOCKED`.

The former base `1b55bea06dd580896cab3557ee3eaf47bec959b7` and its interface fingerprints are historical. The current refresh observation point is main `3d42ed625742c606d5d6773a3b9a6263ae27c379` / tree `cfd9f3dae3256778adf0a8288095a6012134d524`, not a future execution base. Before any T9-SYN launch, a separate exact Owner grant must bind paths, operations, environment, branch, and the exact post-refresh base, and the worker must verify that accepted Task 1–5 interface identities and acceptance records match that base. Only the single new integration test path is contemplated; no product source in `src/` or `experiments/` may be edited. Pure fake-injected doubles and synthetic fixtures only; no real model/processor/asset/cache access, network, real/protected media, benchmark, Gate promotion, or Tasks 6–8/authentic Task 9 work is permitted. The proposed 1152-dimensional end-to-end assertion has not been revalidated against the current integrated seams; if it requires product-source changes, stop and seek separate scope authority rather than broaden the T9 test-only path.

