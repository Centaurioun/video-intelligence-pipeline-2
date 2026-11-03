# Post-Completion Refresh Protocol

**Information state:** `INFERRED_DESIGN` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**When to run:** immediately after current V1 Base reaches its separately verified completion boundary, before actual SigLIP2 migration design/implementation.

## Purpose

Convert the pre-completion preparation package into a completion-SHA-bound migration input.

This protocol is mandatory because repository-specific preparation snapshots may be stale by the time V1 finishes.

## Inputs

Required:

- canonical repository `main`;
- verified V1 completion SHA/tag;
- current `AGENTS.md`;
- current project handoff files;
- ADR-0002;
- this preparation package;
- final V1 test/verification evidence.

Optional only when separately authorized:

- future acquired model bundles.

Do not acquire models merely to run Steps 1–7.

## Step 1 — Verify Authority

Read, in order:

1. `AGENTS.md`;
2. `docs/INDEX.md`;
3. current `docs/project/00_PROJECT_CHARTER.md`;
4. current `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`;
5. current `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`;
6. `docs/project/STATE_MAINTENANCE_PROTOCOL.md`;
7. ADR-0002;
8. this package entrypoint and authority file.

Record any superseding user/repository decision.

If ADR-0002 has been superseded, stop and reconcile authority before continuing.

## Step 2 — Freeze V1 Completion Identity

Record:

- V1 completion SHA;
- tag/release identity if used;
- branch ancestry;
- dirty/clean status evidence;
- exact V1 model ID;
- exact model revision;
- weights digest;
- processor/preprocessing digests;
- semantic-space ID;
- runtime identity;
- final relevant test/verification receipts.

Do not infer missing values.

Missing required reproducibility data is `BLOCKED`.

## Step 3 — Delta the Repository Against Preparation Snapshot

Preparation baseline snapshots were captured before V1 completion.

Compare final V1 against the preparation baseline and identify:

- moved/new/deleted model-related files;
- changed semantic-space structures;
- changed embedding constants;
- changed storage/index/search geometry;
- changed loader/processor boundaries;
- changed CLI/runtime construction;
- changed authorization gates;
- changed tests;
- changed dependency/runtime manifests.

Do not edit production code in this refresh step.

## Step 4 — Re-run Model-Coupling Searches

Search current code/tests for at least:

- `google/siglip-base-patch16-224`;
- `EMBEDDING_DIM`;
- literal `768`;
- literal `768 * 4`;
- `ROW_WIDTH_BYTES`;
- `DEFAULT_ROW_WIDTH_BYTES`;
- `SiglipModel`;
- `SiglipProcessor`;
- `AutoModel`;
- `AutoProcessor`;
- `padding=max_length`;
- `spiece.model`;
- `tokenizer.model`;
- `PROCESSOR_ASSETS`;
- `embedding_dim`;
- `processor_digest`;
- `SemanticSpace(`.

Update:

- `03_V1_BASELINE_SNAPSHOT.md`;
- `07_MIGRATION_SURFACE_SNAPSHOT.md`;
- `08_HARDCODE_AND_ASSUMPTION_REGISTER.md`;
- `18_STALENESS_AND_REVERIFY_REGISTER.md`.

## Step 5 — Reconcile the Target Design

Compare final V1 architecture with `10_TARGET_MODEL_PROFILE_DESIGN.md`.

Possible outcomes:

- final V1 still needs the proposed profile boundary;
- final V1 already implements an equivalent boundary;
- final V1 has a better seam that should replace the preparatory design.

Do not stack a new abstraction on top of an equivalent final-V1 abstraction.

Record the decision as current migration design input.

## Step 6 — Refresh Tests and Acceptance Mapping

Map `14_TEST_AND_ACCEPTANCE_MATRIX.md` to the final V1 test suite.

For each T001–T026 item:

- identify existing coverage;
- mark missing future RED test;
- identify obsolete/renamed paths;
- identify exact future test command.

Run the final V1 baseline suite before migration work begins.

Any existing failure must be understood before attributing later failures to migration.

## Step 7 — Refresh Dependency / Runtime State

Record the actual final V1:

- Python version;
- package/dependency manager;
- exact relevant dependency lock/receipt;
- Transformers version;
- PyTorch version;
- NumPy/Pillow/tokenizer dependencies;
- MPS device/runtime facts;
- FFmpeg/ffprobe identity used by relevant indexing paths.

Update `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md`.

Do not preserve obsolete 2026-10-05 runtime observations merely for consistency.

## Step 8 — Refresh External Sources

Re-fetch primary sources listed in:

- `20_EXTERNAL_EVIDENCE_AND_SOURCE_PACK.md`;
- `21_source-receipts.yaml`.

Update:

- retrieval date;
- relevant upstream revision/file inventory;
- Transformers preprocessing behavior;
- checkpoint config;
- PyTorch MPS references.

External source changes are not local implementation changes. Record both.

## Step 9 — Resolve Target Checkpoint Identity

Only when model acquisition is separately authorized:

- choose immutable V2 Base revision;
- acquire/freeze it;
- compute local weights/processor/preprocessing digests;
- verify exact model config/output width;
- update model contracts.

Repeat later for So400m at its authorized stage.

Do not guess hashes from public file listings.

## Step 10 — Update Future Runbooks and Handoffs

Refresh:

- V1→V2 Base runbook;
- V2 Base→So400m runbook;
- future Codex launch packet;
- future ChatGPT orchestrator handoff;
- readiness checklist.

Remove stale paths and replace them with final V1 references.

## Step 11 — Run Readiness Checklist

Complete `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`.

Migration implementation remains blocked until required readiness items pass.

## Step 12 — Re-enter Superpowers Design Flow

ADR-0002 defines the direction, but final V1 repository evidence controls the exact implementation design.

Run:

`brainstorming -> approved current design -> writing-plans -> isolated implementation -> TDD -> review -> verification`

Do not jump directly from this preparation package into production edits.

## Step 13 — Emit the Refresh Receipt

Complete a concrete copy of:

`30_post-completion-refresh-receipt-template.yaml`

The receipt must bind the refresh to the exact V1 completion SHA, current canonical main, refreshed artifact set, test baseline, authorization state, and remaining blockers.

The template file itself remains unchanged; save the completed receipt at a governed future run/evidence location chosen by the then-current execution plan.

A missing receipt means the refresh is not complete.

## Refresh Output

A successful refresh produces:

- final V1 completion identity;
- refreshed migration surface;
- refreshed hard-code register;
- refreshed dependency/runtime state;
- current target model contracts;
- current test/acceptance mapping;
- current runbooks/handoffs;
- explicit unresolved/blocked items;
- a completed machine-readable post-completion refresh receipt.

It does not itself produce a SigLIP2 implementation or authorize execution.

## Separate Gate A Decision — Does Not Change Steps 1–13

The thirteen numbered refresh steps, their text, evidence, and full-migration disposition remain unchanged. Step 11 records the checklist's full-migration/H decision; the separately adopted Gate A exception is assessed outside that numbered sequence and does not change Step 11's full-migration result. A completed blocked receipt continues to record a blocked full-migration outcome; it is never converted into a Task 1 pass or replaced. After verified V1 completion, Task 1 may be considered despite that blocked full-migration outcome only if the exact ADR-0002 and coordinated subordinate amendment candidate has been owner-accepted and canonically adopted. A fresh exact-main Task 1 scoped-readiness decision must bind the current overlay, all 56 A01–G05 IDs, the 13-step disposition, accepted plan provenance, and explicit E–G applicability; an independent reviewer must accept that exact decision. Every Task 1-required A–D predicate must be freshly evidenced and satisfied under its unchanged pass criteria; required FAIL, BLOCKED, unresolved, or unsatisfied qualified status blocks Gate A, while an existing expressly permitted `NOT_APPLICABLE` remains only where that predicate allows it. Literal `PASS` and qualified overlay statuses such as `PASS_WITH_LIMITS` and `PASS_PLANNING_ONLY` retain their distinct meanings and are not normalized or promoted. Task 1 still requires one separate explicit owner execution authorization bound to the same decision, exact files and operations, execution method, branch/base SHA, and expiry/supersession rules. Any missing or mismatched condition leaves Task 1 blocked. This decision does not alter Task 0 or authorize Gate B.

## Adopted separate synthetic Task 2–5 exception — execution not authorized

**Status:** `OWNER_ACCEPTED — CANONICALLY_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The exact coordinated candidate `ae3939b9c0d98c24809246099c025bc3a60a0d50` / tree `11c9089016f9b0b1a8bd5ee2704d3022d74ef421` was adopted by PR #91 merge commit `25c29c07a8010db551a2ac08fcde72a9147c25d3`. It permits consideration only of separately granted synthetic-only T2-SYN, T3-SYN, and T4-SYN on disjoint plan-listed paths after fresh exact-base/interface checks. A later T5-SYN grant is separate and serial after independent verification and acceptance of all three interfaces. T5 must side-effect-screen `tests/vip_fvs/unit/test_real_source_service.py` and prove no model open, asset read, cache access or network call, or narrow the authorization-order claim to what its authorized tests establish. Adoption grants no task execution or READY status.

**Current Task 1 dependency reference for this proposal (2026-10-19):** the reviewed Task 1 candidate is `ff23e6af46ced80297c8fbc124c6ddf0b0ed288a` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`; its exact accepted `model_profile.py` source blob is `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`. The candidate is represented on current canonical main `342e6fbaa25d28511844b274bce7f927e2c0420d` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`. Its interface review remains `ACCEPT_WITH_LIMITS` for the model-free synthetic interface only. These commit/tree/blob identities are provenance bindings, not a substitute for the exact review artifact or for checking the accepted interface at each consuming task's exact base. A future grant must cite that review evidence and verify its bound interface descriptor at the exact base; missing, stale, or mismatched evidence blocks that task. This reference establishes no authentic tokenizer/model semantics, Task 2–5 readiness, adoption, or execution grant.

This proposed path is outside protocol Steps 1–13. It does not change their text, evidence, sequence, or full-migration disposition; the append-only blocked receipt and 56-ID matrix remain untouched. Task 0 and Gate B stay `NO_GO_BLOCKED`; H and all 56 predicate identities/statuses remain unchanged. No synthetic slice satisfies or waives a predicate or advances real model/runtime/media readiness. Each slice needs a separate exact owner grant and fresh base/contract check; adoption alone is no authority. No model/processor/cache access, acquisition, network/provider/cloud, loading/inference/MPS/hardware checks, real media, benchmark, full archive, production integration, Gate promotion, or dependency/config mutation is allowed.

## Proposed native-Base Task 4/5 source-only exception — not active

**Status:** `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. This candidate is outside the numbered refresh sequence. It leaves all thirteen step definitions, evidence, and dispositions untouched and cannot revise a blocked receipt, H, or any A01–G05 identity/status. If independently reviewed, owner-adopted, and canonically adopted, it still requires separate exact Task 4 and Task 5 grants. Task 4 launch also requires an independently accepted Task 1 `ModelProfile` interface fingerprint bound to the exact Task 4 base, or an exact previously accepted immutable source snapshot whose acceptance receipt/contract binds that fingerprint; missing acceptance, stale base, or mismatch blocks launch and planning approval is insufficient. Task 5 launch binds accepted Task 2 and Task 3 interface fingerprints to its exact base (or a snapshot whose accepted receipt binds both), and final verification requires the accepted Task 4 interface whose acceptance receipt binds the Task 1 fingerprint. Each uses only its exclusive plan-listed paths and fake-injected model-free tests. No authentic model/runtime/media claim, Gate B promotion, Task 6+, or other source permission follows. Task 0/Gate B remain `NO_GO_BLOCKED`.

Before Task 5 BUILD starts, its exact base must bind either (a) an independently accepted Task 4 interface fingerprint whose acceptance receipt binds it to Task 4's exact source SHA, with that same fingerprint bound to Task 5's exact consuming base, or (b), only when Task 4 BUILD overlaps, an exact frozen Task 4 interface fingerprint independently reviewed and bound to both Task 4's exact source base and Task 5's exact consuming base. Final Task 5 VERIFY still requires the independently accepted Task 4 interface at the exact frozen SHA, matching the consumed fingerprint and retaining the Task 1 fingerprint binding. Any Task 4 interface change makes Task 5 descendants stale; stop and rebind/review before continuing. This dependency clarification does not alter the thirteen numbered refresh steps.

## Proposed synthetic Task 9 preparatory exception (T9-SYN) — not active

**Status (refreshed 2026-10-19):** PR #86 merged the reviewed T9-SYN governance candidate at `dab471b768811a7c1e3791e4f79de4539bd12d33` as governance documentation; the preserved M3 record remains a pre-adoption record and does not establish an execution grant. T9-SYN remains `NOT_AUTHORIZED_FOR_EXECUTION`. This proposal is outside protocol Steps 1–13 and changes none of their text, evidence, sequence, or full-migration disposition; the append-only blocked receipt and 56-ID matrix remain untouched. Task 0 and Gate B stay `NO_GO_BLOCKED`; H and all 56 predicate identities/statuses remain unchanged. The former base `1b55bea06dd580896cab3557ee3eaf47bec959b7` is historical. Current main `3d42ed625742c606d5d6773a3b9a6263ae27c379` / tree `cfd9f3dae3256778adf0a8288095a6012134d524` is only the source-observation snapshot for this refresh; any future grant must bind a fresh exact post-refresh base and accepted Task 1–5 interfaces to their evidence. The only contemplated path remains `tests/vip_fvs/integration/test_three_profile_synthetic_space_contract.py`. No model/processor/cache access, acquisition, network/provider/cloud, loading/inference/MPS/hardware checks, real media, benchmark, full archive, production integration, Gate promotion, or dependency/config mutation is allowed.

