# SigLIP2 Post-Completion Migration Preparation Pack

**Information state:** `FROZEN_DECISION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Authority parent:** `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`  
**Preparation design:** `docs/superpowers/specs/2026-10-05-siglip2-post-completion-preparation-pack-design.md`  
**Preparation plan:** `docs/superpowers/plans/2026-10-05-siglip2-post-completion-preparation-pack-implementation-plan.md`

## Purpose

This directory is the durable preparation surface for the model-evolution work that begins only after the current SigLIP1 Base Video Intelligence Pipeline reaches its separately verified completion boundary.

The committed sequence is:

`VIP V1 Base -> VIP V2 Base -> VIP V2 So400m -> frozen three-way mini-benchmark -> representation decision -> separately authorized full-archive indexing`

The three required candidates are:

- **VIP V1 Base:** `google/siglip-base-patch16-224`
- **VIP V2 Base:** `google/siglip2-base-patch16-224`
- **VIP V2 So400m:** `google/siglip2-so400m-patch14-384`

This package reduces later rediscovery. It does not replace final verification and does not activate the migration.

## Read This First

At post-V1 activation, a fresh ChatGPT/Codex session should read in this order:

1. repository `AGENTS.md`;
2. `docs/INDEX.md`;
3. current project handoff files under `docs/project/`;
4. `docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md`;
5. this file;
6. `01_AUTHORITY_SCOPE_AND_ACTIVATION.md`;
7. `02_PACKAGE_MANIFEST.yaml`;
8. `29_SIX_CYCLE_HARDENING_AUDIT.md`;
9. `19_POST_COMPLETION_REFRESH_PROTOCOL.md`;
10. create a completed receipt from `30_post-completion-refresh-receipt-template.yaml`;
11. `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`;
12. refreshed model/migration documents in manifest order.

Current repository evidence always supersedes a stale preparation snapshot.

## Information-State Labels

Preparation artifacts use these labels:

- **FROZEN_DECISION** — accepted project decision or invariant; do not silently reinterpret it.
- **VERIFIED_CURRENT** — verified against canonical repository state at the stated SHA.
- **SNAPSHOT** — true when captured but expected to drift as V1 evolves.
- **REVERIFY_AT_V1_COMPLETION** — must be checked before migration work begins.
- **OFFICIAL_EXTERNAL** — supported by a primary external source such as an official model card, Transformers documentation, or the SigLIP2 paper.
- **INFERRED_DESIGN** — future architectural/design conclusion, not implemented state.
- **TEMPLATE** — intentionally incomplete artifact to be filled later.
- **NOT_AUTHORIZED_FOR_EXECUTION** — preparation exists, but execution remains deferred.

A document may carry more than one label.

## What This Package Contains

The migration preparation tree contains:

- authority and activation rules;
- V1 baseline snapshots;
- model contracts;
- compatibility and migration-surface maps;
- hard-coded assumption registers;
- preserve/no-touch boundaries;
- future model-profile design;
- migration runbooks;
- dependency/runtime notes;
- test/acceptance matrices;
- semantic-space/index-isolation strategy;
- risk, rollback, staleness, and refresh procedures;
- primary-source receipts;
- future Codex and ChatGPT handoffs;
- readiness and post-migration verification checklists;
- a machine-readable post-completion refresh receipt template;
- a six-cycle hardening audit trail.

The companion benchmark package lives at:

`docs/benchmarks/siglip-three-way/`

and defines the future 10-20-video frozen comparison protocol, including a pre-execution freeze checklist and an exact source-native sample-plan template.

## Critical Interpretation Rules

1. **Same dimensionality does not mean same semantic space.** SigLIP1 Base and SigLIP2 Base embeddings must never be mixed merely because both are expected to use a 768-dimensional space.
2. **Model timestamps are not edit boundaries.** Migration does not change source-native PTS/timebase requirements.
3. **Public benchmark superiority is not local proof.** The three-way project benchmark decides project-specific usefulness.
4. **Pre-completion paths are snapshots.** Current file names, symbols, constants, and dependencies must be refreshed after V1 completion.
5. **No execution by implication.** A runbook, template, or launch packet is not permission to download a model, process protected media, or index the archive.

## Current Package State

The preparation package is structurally complete:

- 31 migration-preparation artifacts are present;
- 18 three-way benchmark-preparation artifacts are present;
- the original consistency audit and the later six-cycle hardening audit have reconciled package state, technical evidence, benchmark methodology, and future handoff gaps;
- execution remains dormant and unauthorized until the activation conditions below are satisfied.

Consult `02_PACKAGE_MANIFEST.yaml` for exact machine-readable artifact state.

## Activation Trigger

Do not begin model migration or Task 1 software implementation merely because this directory exists. Task 1 is V2-related software implementation, not documentation-only preparation. It may be considered only under the exact, separately adopted Gate A exception in ADR-0002 Amendment 1 and `01_AUTHORITY_SCOPE_AND_ACTIVATION.md`.

For Gate A, this package becomes actionable only after verified V1 completion and preservation, canonical adoption of the exact owner-accepted ADR/subordinate amendment candidate, a fresh exact-main scoped Task 1 readiness decision with independent acceptance, and one exact owner execution authorization binding files, operations, method, branch/base, and supersession rules. A blocked full-migration receipt remains blocked and does not itself bar this exception once those conditions are met; without them, Task 1 remains blocked.

For Gate B/full migration, the package becomes actionable only after:

1. the current SigLIP1 Base project reaches its verified V1 completion boundary;
2. V1 is preserved at an immutable SHA/tag or equivalent reproducible identity;
3. `19_POST_COMPLETION_REFRESH_PROTOCOL.md` is run against that completed V1 state;
4. a completed post-completion refresh receipt is emitted from `30_post-completion-refresh-receipt-template.yaml`;
5. the migration-readiness checklist is satisfied;
6. any execution requiring model acquisition, protected media, or broader processing has the applicable current authorization.

Without all applicable Gate A or Gate B activation conditions, this directory remains preparation only. Gate A makes only its exact Task 1 scope actionable; every other migration activity remains dormant until Gate B requirements pass.

## Adopted pre-Gate-B synthetic slices — execution not authorized

**Status:** `OWNER_ACCEPTED — CANONICALLY_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The exact coordinated candidate `ae3939b9c0d98c24809246099c025bc3a60a0d50` / tree `11c9089016f9b0b1a8bd5ee2704d3022d74ef421` was adopted by PR #91 merge commit `25c29c07a8010db551a2ac08fcde72a9147c25d3`. This route supersedes only the specified Task 2–5 entry wording. T2-SYN/T3-SYN/T4-SYN require separate exact grants; T5-SYN is serial after independent interface verification and acceptance and requires its own later grant. Fresh exact-base/interface checks remain mandatory. Adoption alone makes no slice READY or authorizes execution. Task 0 and Gate B remain `NO_GO_BLOCKED`; Gate B/full migration remains required for authentic model/runtime/media operations and Task 6 onward. Refer to the plan's adopted pre-Gate-B synthetic exception for boundaries, exclusions, and T5 test guards.

**Current Task 1 dependency reference for this proposal (2026-10-19):** the reviewed Task 1 candidate is `ff23e6af46ced80297c8fbc124c6ddf0b0ed288a` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`; its exact accepted `model_profile.py` source blob is `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`. The candidate is represented on current canonical main `342e6fbaa25d28511844b274bce7f927e2c0420d` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`. Its interface review remains `ACCEPT_WITH_LIMITS` for the model-free synthetic interface only. These commit/tree/blob identities are provenance bindings, not a substitute for the exact review artifact or for checking the accepted interface at each consuming task's exact base. A future grant must cite that review evidence and verify its bound interface descriptor at the exact base; missing, stale, or mismatched evidence blocks that task. This reference establishes no authentic tokenizer/model semantics, Task 2–5 readiness, adoption, or execution grant.

## Proposed residual native-Base Task 4/5 entry — not active

**Status:** `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. A separate candidate concerns only genuine native Base Task 4 and checked CLI Task 5 fake-injected, model-free source editing/TDD. Each requires its own exact task grant AND either accepted applicable Gate B or independent review, owner adoption, and canonical adoption of the coordinated tree. Before Task 4 launch, require an independently accepted Task 1 `ModelProfile` interface fingerprint bound to its exact source base; an exact previously accepted immutable source snapshot is sufficient only when its acceptance receipt/contract records and binds that fingerprint. Missing acceptance/fingerprint or stale/mismatched base/interface stops launch; planning approval alone is not interface acceptance. Task 5 also requires accepted Task 2 and Task 3 interface fingerprints at its exact base (or an exact accepted source snapshot whose accepted receipt binds both) and an accepted Task 4 interface for final verification whose acceptance receipt binds the Task 1 fingerprint. This does not convert T4-SYN/T5-SYN into native work. See the plan's exact paths and the governance decision packet. No other task becomes READY; Task 0/Gate B remain `NO_GO_BLOCKED`.

Before Task 5 BUILD starts, its exact base must bind either (a) an independently accepted Task 4 interface fingerprint whose acceptance receipt binds it to Task 4's exact source SHA, with that same fingerprint bound to Task 5's exact consuming base, or (b), only when Task 4 BUILD overlaps, an exact frozen Task 4 interface fingerprint independently reviewed and bound to both Task 4's exact source base and Task 5's exact consuming base. Final Task 5 VERIFY still requires the independently accepted Task 4 interface at the exact frozen SHA, matching the consumed fingerprint and retaining the Task 1 fingerprint binding. Any Task 4 interface change makes Task 5 descendants stale; stop and rebind/review before continuing.

## Proposed synthetic Task 9 preparatory entry (T9-SYN) — not active

**Status (refreshed 2026-10-19):** PR #86 merged the reviewed T9-SYN governance candidate at `dab471b768811a7c1e3791e4f79de4539bd12d33`; the PR describes documentation-only governance adoption. Its preserved M3 adjudication record remains a pre-adoption record (`PREPARED_FOR_EXACT_OWNER_ADOPTION`), so the documentary status discrepancy is not silently rewritten here. This refresh does not grant execution. T9-SYN remains `NOT_AUTHORIZED_FOR_EXECUTION` and requires a separate exact Owner grant. The former base `1b55bea06dd580896cab3557ee3eaf47bec959b7` is historical. The current observation snapshot is main `3d42ed625742c606d5d6773a3b9a6263ae27c379` / tree `cfd9f3dae3256778adf0a8288095a6012134d524`, not a future execution binding; after adoption of any refresh, rebind the exact current base and accepted Task 1–5 interfaces before considering a grant. T9-SYN remains confined to `tests/vip_fvs/integration/test_three_profile_synthetic_space_contract.py`; no product files in `src/` or `experiments/` may be modified. Task 0 and Gate B remain `NO_GO_BLOCKED`, all 56 readiness predicates remain unchanged, and Gate B remains the gate for authentic model/runtime/media operations and Tasks 6–8/authentic Task 9+.

