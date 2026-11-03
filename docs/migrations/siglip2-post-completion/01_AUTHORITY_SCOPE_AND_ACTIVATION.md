# Authority, Scope, and Activation

**Information state:** `FROZEN_DECISION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Authority parent:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`

## Role

This document prevents preparation work from being mistaken for execution authority.

The accepted post-completion direction is binding, but the actual SigLIP2 migration is intentionally deferred until the current V1 SigLIP1 Base implementation is complete and separately verified.

## Allowed During Preparation

The following work is within this documentation-only preparation project:

- read current repository files, tests, history, and existing evidence;
- inspect public official documentation and primary research sources;
- create new Markdown/YAML/JSON/CSV preparation artifacts;
- record current repository facts as dated/SHA-bound snapshots;
- record official external model facts as external evidence;
- design future runbooks, checklists, manifests, result schemas, and launch packets;
- specify a future synthetic fake-vector rehearsal without implementing it;
- identify facts that must be reverified at V1 completion.

This permission does not alter the current V1 product implementation.

## Explicitly Deferred

The following are **not authorized by this preparation package**:

- modifying current production implementation for SigLIP2, except the exact Task 1 scope only if the separate Gate A amendment and every activation precondition below are canonically adopted and the owner issues the required exact-scope execution authorization;
- modifying current tests for SigLIP2, except the exact model-free Task 1 tests under that same Gate A authorization;
- downloading or acquiring SigLIP2 checkpoints or model assets;
- provider/cloud model calls or unrelated network egress;
- real or protected archive-media execution;
- SigLIP2 MPS/CPU inference;
- full-archive indexing or re-indexing;
- production promotion;
- Gate promotion;
- destructive cleanup or deletion of V1 evidence;
- real-media editing, rendering, export, or QC;
- declaring V2 Base or V2 So400m the winner before the planned project benchmark.

Separate, current authorization remains required wherever repository policy requires it.

## Gate B Activation Preconditions — Full Migration

Full migration implementation, including Task 2 onward and all runtime/model/media work, may begin only after all of the following are true:

1. **V1 completion is verified.** The current SigLIP1 Base project has reached its separately defined finish line.
2. **V1 is preserved.** An immutable completion SHA/tag or equivalent reproducible identity exists.
3. **Preparation snapshots are refreshed.** The future `19_POST_COMPLETION_REFRESH_PROTOCOL.md` has been run against the completed V1 state.
4. **Readiness is checked.** The future `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md` is satisfied.
5. **Design authority is current.** The actual migration design is revalidated through the applicable Superpowers brainstorming/design flow.
6. **Required execution authorization exists.** Model acquisition, protected-media use, and other gated actions are separately authorized when needed.

A failure of any prerequisite is a stop condition for migration execution, not permission to infer a missing value.

## Gate A — Task 1 Preparatory Implementation Exception

Task 1 is software implementation associated with the V2 migration program; its model-free scope does not make it documentation-only work. The owner may authorize only the accepted plan's Task 1, “Closed, validated three-profile semantic-space contract,” after verified V1 completion and preservation. Gate A is a separate, narrow exception and does not activate the V2 runtime migration.

Gate A may be considered despite a blocked full-migration receipt only after an exact owner-accepted amendment to ADR-0002 and the coordinated subordinate contracts is canonically adopted. It then requires:

1. a fresh exact-main Task 1 scoped-readiness decision with current evidence for the 56 predicates and all 13 refresh steps, explicit A–D disposition, and E–G applicability. Every Task 1-required A–D predicate must be freshly evidenced and satisfied under its unchanged pass criteria; any required FAIL, BLOCKED, unresolved condition, or qualification that does not meet the existing criterion blocks Gate A. An explicitly permitted `NOT_APPLICABLE` remains only where the predicate already allows it. Literal checklist `PASS` and qualified overlay statuses (including `PASS_WITH_LIMITS` and `PASS_PLANNING_ONLY`) retain their distinct existing meanings and are not normalized or promoted;
2. independent review accepting that exact scoped decision; and
3. one separate explicit owner Task 1 execution authorization that binds the exact decision, accepted-plan provenance, allowed files and operations, execution method, branch/base SHA, and expiry/supersession rules.

No second task-start approval is implied: the single owner execution authorization must contain the required start binding. A mismatch, stale main or contract, missing field, or unresolved contradiction blocks entry.

The permitted operations are limited to the accepted Task 1 frozen profile validation, deterministic mapping to the existing `SemanticSpace` contract, synthetic identity fixtures, model-free tests, V1 identity-preservation regression, independent feature review, and bounded verification, within the accepted Task 1 file scope. Task 2 or later, dependency/environment changes, real model or processor identity/acquisition/load, inference/MPS, media, provider/cloud/egress, benchmarking, full-archive indexing, Gate promotion, and production integration remain excluded.

Gate A does not satisfy or change any checklist predicate, replace the full Task 0 `NO_GO_BLOCKED` decision, rewrite a blocked receipt, or grant Gate B readiness. Absent every condition above, Task 1 remains blocked.

## Adopted separate synthetic Task 2–5 entry — execution not authorized

**Status:** `OWNER_ACCEPTED — CANONICALLY_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The exact coordinated candidate `ae3939b9c0d98c24809246099c025bc3a60a0d50` / tree `11c9089016f9b0b1a8bd5ee2704d3022d74ef421` was adopted by PR #91 merge commit `25c29c07a8010db551a2ac08fcde72a9147c25d3`. This section supersedes only the Task 2–5 implementation-entry wording in “Gate B Activation Preconditions”; all Gate B/full-migration predicates and operations remain unchanged. Adoption is not a worker grant or READY signal.

**Current Task 1 dependency reference for this proposal (2026-10-19):** the reviewed Task 1 candidate is `ff23e6af46ced80297c8fbc124c6ddf0b0ed288a` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`; its exact accepted `model_profile.py` source blob is `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`. The candidate is represented on current canonical main `342e6fbaa25d28511844b274bce7f927e2c0420d` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`. Its interface review remains `ACCEPT_WITH_LIMITS` for the model-free synthetic interface only. These commit/tree/blob identities are provenance bindings, not a substitute for the exact review artifact or for checking the accepted interface at each consuming task's exact base. A future grant must cite that review evidence and verify its bound interface descriptor at the exact base; missing, stale, or mismatched evidence blocks that task. This reference establishes no authentic tokenizer/model semantics, Task 2–5 readiness, adoption, or execution grant.

After adoption, the owner may issue separate exact execution grants for T2-SYN (storage/indexer), T3-SYN (search/fake seam), and T4-SYN (mocked adapter). Their exact exclusive path lists are in the plan's adopted pre-Gate-B synthetic exception. Each requires accepted Task 1 interfaces at the exact authorized base, an exact path/operation/test/environment/method/branch/base/expiry/supersession binding, and explicit synthetic-only side-effect boundaries. These three may run concurrently only with disjoint paths. T5-SYN is serial after all three exact interfaces are independently verified and accepted together and requires its own later grant. That grant must side-effect-screen `tests/vip_fvs/unit/test_real_source_service.py` and prove no model open, asset read, cache access, or network call; otherwise narrow the authorization-order claim to what the safe granted tests establish or defer T5.

All four slices exclude dependencies/config mutation, model/processor/checkpoint/cache access or acquisition, network/provider/cloud, model load/inference/MPS/hardware checks, real/protected media, benchmark, full archive, production integration, Gate promotion, and canonical-main writes. Unsafe tests are not run. No slice changes Task 0/Gate B `NO_GO_BLOCKED`, H, any of the 56 predicate identities/statuses, protocol Steps 1–13, Gate A's Task 1-only scope, or evidence classifications. Tasks 6 onward and every authentic model/runtime/media gate remain under Gate B. Fresh exact-base and contract checks plus applicable independent verification are required before any slice is called READY.

## Required Post-Completion Sequence

Once activated, the intended order remains:

1. preserve completed V1 Base;
2. migrate V1 Base to V2 Base;
3. independently verify V2 Base;
4. extend the validated SigLIP2 path to V2 So400m;
5. independently verify V2 So400m;
6. freeze the small benchmark corpus, queries, relevance rules, metrics, and winner rules;
7. run V1 Base vs V2 Base vs V2 So400m under the same comparison envelope;
8. record the comparative evidence;
9. select the preferred representation;
10. only then consider separately authorized full-archive indexing.

## Fail-Closed Rules

When authority is ambiguous:

- do not download a model;
- do not process archive media;
- do not widen network access;
- do not infer Gate promotion;
- do not replace current V1 implementation state;
- record `BLOCKED` or `NOT_OBSERVED` as appropriate and seek current authorization.

When a preparation fact conflicts with current repository evidence:

- current verified repository evidence wins;
- mark the preparation fact stale;
- refresh dependent artifacts before continuing.

When an external source conflicts with local measured evidence:

- preserve both with their evidence classes;
- do not silently upgrade or erase either;
- investigate the mismatch before relying on it operationally.

## Invariants That Migration Cannot Override

The model migration does not change these project rules:

- source media remains immutable unless a separately approved policy says otherwise;
- semantic/model timestamps remain candidate evidence only;
- exact temporal work requires source-native PTS/timebase evidence;
- VFR frame positions are never inferred as seconds multiplied by nominal FPS;
- evidence classes remain `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, and `EDITORIAL_INFERENCE`;
- `NOT_OBSERVED` remains an availability/state marker, not an evidence class;
- incompatible semantic spaces are never silently mixed;
- stronger model capability does not silently upgrade evidence strength.

## Dormant State

Before V1 completion, the correct state of this package is:

`PREPARED / DORMANT / NOT_AUTHORIZED_FOR_EXECUTION`

That state is intentional.

## Proposed native-Base Task 4/5 exception — not active

**Status:** `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. This proposal cannot change dormant state unless the relevant task receives its own exact source/test/operations/environment/branch/base grant AND either accepted applicable Gate B is current or the complete exact coordinated tree is independently accepted, explicitly owner-adopted, and canonically adopted. Before Task 4 launch, require an independently accepted Task 1 `ModelProfile` interface fingerprint bound to its exact source base; an exact previously accepted immutable source snapshot is sufficient only when its acceptance receipt/contract records and binds that fingerprint. Missing acceptance/fingerprint or stale/mismatched base/interface stops launch; planning approval alone is not interface acceptance. Task 5 additionally requires accepted Task 2 and Task 3 interface fingerprints bound to its exact base (or an exact accepted source snapshot whose accepted receipt binds both), plus the accepted Task 4 interface for final verification whose acceptance receipt binds the Task 1 fingerprint. Neither this document nor previous synthetic approvals grants implementation. Only the plan-listed exclusive paths are contemplated. Fake-injected model-free work establishes no authentic tokenizer, processor, preprocessing, mask/pooling, MPS/device, or retrieval-quality claim. Task 0/Gate B remain `NO_GO_BLOCKED` and other dormant gates remain unchanged.

Before Task 5 BUILD starts, its exact base must bind either (a) an independently accepted Task 4 interface fingerprint whose acceptance receipt binds it to Task 4's exact source SHA, with that same fingerprint bound to Task 5's exact consuming base, or (b), only when Task 4 BUILD overlaps, an exact frozen Task 4 interface fingerprint independently reviewed and bound to both Task 4's exact source base and Task 5's exact consuming base. Final Task 5 VERIFY still requires the independently accepted Task 4 interface at the exact frozen SHA, matching the consumed fingerprint and retaining the Task 1 fingerprint binding. Any Task 4 interface change makes Task 5 descendants stale; stop and rebind/review before continuing.

## Proposed synthetic Task 9 preparatory exception (T9-SYN) — not active

**Status (refreshed 2026-10-19):** PR #86 merged the reviewed T9-SYN governance candidate at `dab471b768811a7c1e3791e4f79de4539bd12d33` as documented adoption of governance only. The preserved M3 adjudication still records `PREPARED_FOR_EXACT_OWNER_ADOPTION`; retain this as historical evidence and do not infer an execution grant from either record. T9-SYN remains `NOT_AUTHORIZED_FOR_EXECUTION`. The pinned base `1b55bea06dd580896cab3557ee3eaf47bec959b7` is historical; the source-observation point is main `3d42ed625742c606d5d6773a3b9a6263ae27c379` / tree `cfd9f3dae3256778adf0a8288095a6012134d524`, not a future dispatch base. Before any later grant, independently bind the exact current post-refresh base and accepted Task 1–5 interface blobs to their applicable acceptance evidence. Only exclusive test path `tests/vip_fvs/integration/test_three_profile_synthetic_space_contract.py` is contemplated. Fake-injected model-free tests establish no authentic tokenizer, processor, model, MPS/device, or retrieval-quality claim. Task 0/Gate B remain `NO_GO_BLOCKED`; Tasks 6–8 and authentic Task 9/10 remain unauthorized and behind Gate B.
