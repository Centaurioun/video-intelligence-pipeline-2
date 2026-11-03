# Future ChatGPT Orchestrator Handoff

**Information state:** `STEP10_DOCUMENTS_CANONICALLY_ADOPTED` + `OWNER_APPROVED_FOR_PLANNING` + `TASK0_NO_GO_BLOCKED` + `NOT_AUTHORIZED_FOR_EXECUTION`

## Mission

After V1 completion, coordinate the committed ADR-0002 sequence:

`freeze V1 -> migrate V2 Base -> verify -> extend So400m -> verify -> frozen three-way benchmark -> winner decision`

Do not implement by conversational memory.

Bootstrap from current repository authority.

**Current evidence state (2026-10-11):** preserved V1 source `3586eeaa904fc5a2e6a2745078611886f482f3de`; canonical-main observation `748818e867ce08ccc2367bad21df7d83eaf51d70`; artifact identity `989c1bc6923833a11cfd11b7b756ef1f4ffbe192`; bounded authentic synthetic V1 MPS runtime `634bfed47aec8464c8ca61b15c376f2950c21060`; 811 distinct model-free passes at `6396779e397dc9dba659f4887471de4c6d30aced`; separate historical G03 1,290 regressions at `988b8790cc45ad1c1093f0d1ebbae15ab0716f38`; current runtime inventory / F07 assessment `ce3f570016f3f13e9091fb6989f3a9d3ea783c7d`; final Task 0 gap assessment and E01–E10 refresh `229d08f564fb8c21a7a119fc900eaac82cb64cd0`. The token warning's configuration-level explanation is known, but actual token traces and semantic correctness remain `NOT_OBSERVED`. Task 0 is `NO_GO_BLOCKED`; plan acceptance, V2 Base identity/acquisition authorization, and media authorization remain separate gates.

This handoff remains an orchestration template. It authorizes no code, model acquisition, inference, or media operations. Never begin implementation because this handoff or launch packet exists.

**Post-adoption correction (2026-10-11):** PR #69 merged at `7f4a5ce1baf7de2aa580f1043502458336bf57fe`. The owner decision accepts original plan blob `78127a9199a912531d5b2240eed66e93814d83f3` for planning only; this later documentation version does not replace that reviewed blob. The five Step 10 documents were adopted on PR #69. The successor checklist overlay remains `NO_GO_BLOCKED` for full migration and may identify a candidate model-free Task 1 scope, but no implementation is authorized. V2 identity/acquisition and protected-media permissions remain separately blocked.

## First Session Procedure

1. Verify canonical `main`.
2. Read `AGENTS.md` and `docs/INDEX.md`.
3. Read the current project charter/handoff/orchestration/state-maintenance documents.
4. Read ADR-0002.
5. Read this preparation package entrypoint and manifest.
6. Reconcile the exact source receipts above and distinguish preserved V1 source SHA from the local-first product candidate.
7. Read the successor Task 0 overlay for disposition of all 13 numbered steps of `19_POST_COMPLETION_REFRESH_PROTOCOL.md`. The accepted plan cites all 13; preserve the earlier mismatch only as historical candidate evidence.
8. Treat the exact existing refresh receipt as `BLOCKED`, not readiness clearance; any successor receipt requires a separately authorized, governed refresh run.
9. Complete `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`; all required A–D predicates must be PASS before implementation entry.
10. The owner accepted `RETAIN_DESIGN` and the exact reviewed plan blob for planning via PR #69; do not treat this as implementation approval.
11. Before any future first task, use the independently reviewed successor overlay to assess all A–D predicates and the model-free Task 1-specific E–G applicability, then obtain separate exact-scope owner execution authorization and explicit execution-method selection.

## Orchestration State Labels

Use explicit status:

- `VERIFIED`
- `PENDING`
- `NOT_OBSERVED`
- `BLOCKED`
- `INFERRED`

Do not upgrade evidence silently.

## Design Flow

For V1→V2 Base:

1. inspect final repository state;
2. use Superpowers brainstorming;
3. compare at least the minimal profile design with any seam final V1 already provides;
4. preserve rejected alternatives/reconsideration triggers;
5. record a source-grounded `RETAIN_DESIGN` or bounded amendment recommendation; the existing spec remains `OWNER_APPROVED_FOR_PLANNING`, and this assessment adds no execution authority;
6. use writing-plans;
7. execute in isolation;
8. use TDD;
9. request review;
10. verification-before-completion;
11. freeze reproducible V2 Base candidate.

Repeat the appropriate design/plan/review/verification gates for So400m.

ADR-0002 commits the direction, not the exact implementation details.

## Parallelism Guidance

Use parallel work only for genuinely independent tasks.

Good candidates may include:

- independent documentation/source refresh;
- test-surface audit separate from dependency/runtime audit;
- benchmark template preparation independent of model implementation.

Avoid parallel writers on:

- shared model-profile contract;
- semantic-space schema;
- shared test fixtures;
- migration plan authority.

Prefer one owner for shared contracts.

## V1 Preservation

Before any V2 integration:

- record V1 completion SHA/tag;
- verify V1 model/runtime identity;
- preserve reproducibility evidence;
- verify branch ancestry;
- prevent destructive cleanup.

If V1 cannot be reproduced, migration readiness is `BLOCKED`.

## Model Acquisition Boundary

Do not infer permission to download model weights.

When authorized:

- freeze exact upstream revision;
- acquire into approved local immutable location;
- hash exact bytes;
- inventory processor assets;
- record runtime/dependency identity.

A Hugging Face URL in this package is research evidence, not acquisition authorization.

## Migration Completion Discipline

For each candidate, do not accept “it works” as evidence.

Require:

- current code SHA;
- exact model identity;
- exact processor/preprocessing identity;
- targeted tests;
- regression tests;
- authorization-bound smoke evidence where permitted;
- review outcome;
- verification receipt;
- unresolved findings.

Use `27_POST_MIGRATION_VERIFICATION_CHECKLIST.md`.

## Benchmark Activation

Do not begin the comparative benchmark until all three candidates are independently reproducible and benchmark-eligible.

Before seeing final comparative results, freeze:

- corpus;
- source/sample manifest;
- query set;
- relevance/annotation rules;
- metrics/aggregation;
- performance protocol;
- winner decision rules.

Then execute the same benchmark envelope for every candidate.

## Decision Discipline

Possible outcomes remain:

- V2 Base selected;
- V2 So400m selected;
- V1 remains adequate.

Do not force a migration result because ADR-0002 planned SigLIP2 evaluation.

The benchmark is allowed to show that the additional cost is not justified.

## Full Archive Boundary

A benchmark winner does not itself authorize the full ~400-hour index.

After the winner decision:

1. record the decision and evidence;
2. update handoff/state;
3. request/confirm applicable authorization;
4. plan full-archive indexing separately.

## Handoff to Codex

Use `24_FUTURE_CODEX_LAUNCH_PACKET.md` only after replacing every placeholder with current evidence or explicit `BLOCKED`.

Never hand Codex a prompt that contains stale completion SHA/model identity as if current. The launch packet must point to the completed post-completion refresh receipt.
An owner-accepted plan is still not implementation authorization. Require a separate exact-scope implementation authorization; model acquisition/inference and protected-media access each need explicit current authorization.

## Failure Handling

Unexpected implementation/test/integration failure:

`systematic-debugging before fix proposal`

Review feedback:

`receiving-code-review before applying changes`

Completion claim:

`verification-before-completion`

If the project state conflicts with this preparation package, current verified repository evidence wins.

## Adopted pre-Gate-B synthetic execution handoff — execution not authorized

**Status:** `OWNER_ACCEPTED — CANONICALLY_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The exact coordinated candidate `ae3939b9c0d98c24809246099c025bc3a60a0d50` / tree `11c9089016f9b0b1a8bd5ee2704d3022d74ef421` was adopted by PR #91 merge commit `25c29c07a8010db551a2ac08fcde72a9147c25d3`. The existing Task 0/Gate B blocked status and stop conditions remain binding. Only separately granted T2-SYN/T3-SYN/T4-SYN model-free slices may be scheduled concurrently after exact post-adoption base/interface checks and disjoint path ownership. T5-SYN is serial after the three exact interfaces are independently verified and accepted together and requires a separate later grant. Its test grant must include and side-effect-screen `tests/vip_fvs/unit/test_real_source_service.py`, plus negative no-model-open/no-asset/no-cache/no-network guards; otherwise narrow its source-authorization claim or defer it. Bind every grant to paths, operations, tests, environment, method, isolated branch/base, expiry and supersession. Adoption alone is not execution authority or READY status.

**Current Task 1 dependency reference for this proposal (2026-10-19):** the reviewed Task 1 candidate is `ff23e6af46ced80297c8fbc124c6ddf0b0ed288a` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`; its exact accepted `model_profile.py` source blob is `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`. The candidate is represented on current canonical main `342e6fbaa25d28511844b274bce7f927e2c0420d` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`. Its interface review remains `ACCEPT_WITH_LIMITS` for the model-free synthetic interface only. These commit/tree/blob identities are provenance bindings, not a substitute for the exact review artifact or for checking the accepted interface at each consuming task's exact base. A future grant must cite that review evidence and verify its bound interface descriptor at the exact base; missing, stale, or mismatched evidence blocks that task. This reference establishes no authentic tokenizer/model semantics, Task 2–5 readiness, adoption, or execution grant.

Keep generated inputs and temporary outputs synthetic/test-managed. Do not access assets/caches, use network/provider/cloud, load or infer with a model, probe MPS/hardware, process real/protected media, benchmark, index the archive, promote a Gate, mutate canonical main, or alter Task 0 evidence. Preserve Task 0/Gate B `NO_GO_BLOCKED`, H, all 56 predicate identities/statuses, all 13 refresh steps, Gate A's Task 1-only scope, and all authentic model/runtime/media gates. The integration design spec was compared and no amendment is needed: it specifies design/interfaces, not an incompatible execution authorization rule.

## Proposed native-Base Task 4/5 execution handoff — not active

**Status:** `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. A future coordinator may consider either lane only with its own exact task grant AND either accepted applicable Gate B or independent review plus exact owner/canonical adoption of this coordinated exception. Gate B can replace the exception-adoption condition only; it never replaces the task grant. Task 4 owns only `experiments/persistent_local_index/siglip2_native.py` and its focused test. Before Task 4 starts, bind the independently accepted Task 1 `ModelProfile` interface fingerprint to the exact base; an exact previously accepted immutable source snapshot is sufficient only if its acceptance receipt/contract records and binds that fingerprint. Missing acceptance/fingerprint, stale base, or mismatch stops launch; planning approval alone is insufficient. Task 5 owns only `experiments/persistent_local_index/embedding.py`, `src/vip_fvs/cli.py`, and new `tests/vip_fvs/integration/test_native_base_cli_contract.py`. Before Task 5 starts, bind accepted Task 2 and Task 3 interface fingerprints to the exact base; an exact accepted source snapshot is sufficient only if its accepted receipt binds both fingerprints. Each lane needs an isolated branch/base and exact operations/environment binding; neither overlaps the other, `model_profile.py`, V1 `local_model.py`, or main. Task 5 final VERIFY consumes the independently accepted Task 4 interface SHA (whose acceptance binds the Task 1 interface) and stops on stale identity.

Before Task 5 BUILD starts, its exact base must bind either (a) an independently accepted Task 4 interface fingerprint whose acceptance receipt binds it to Task 4's exact source SHA, with that same fingerprint bound to Task 5's exact consuming base, or (b), only when Task 4 BUILD overlaps, an exact frozen Task 4 interface fingerprint independently reviewed and bound to both Task 4's exact source base and Task 5's exact consuming base. Final Task 5 VERIFY still requires the independently accepted Task 4 interface at the exact frozen SHA, matching the consumed fingerprint and retaining the Task 1 fingerprint binding. Any Task 4 interface change makes Task 5 descendants stale; stop and rebind/review before continuing.

Use fake-injected model-free tests only. Preserve V1 no-flag behavior, source authorization before factory creation, distinct V1/V2 Base `SemanticSpace`/generation identities, and native integer source PTS/timebase. Do not claim authentic tokenizer, processor, preprocessing, mask/pooling, MPS/device or retrieval semantics. No environment changes, model/asset/cache access, network, media, benchmark, Gate promotion or Task 6+ work. T4-SYN/T5-SYN remains separate; Task 0/Gate B remain `NO_GO_BLOCKED`, with H, the 56 predicate identities/statuses, and the 13 refresh steps unchanged.

## Proposed synthetic Task 9 preparatory execution handoff (T9-SYN) — not active

**Status (refreshed 2026-10-19):** PR #86 merged the reviewed T9-SYN governance documentation at `dab471b768811a7c1e3791e4f79de4539bd12d33`; the preserved M3 adjudication remains a pre-adoption record. Keep the documentary distinction visible. T9-SYN still has no execution grant and remains `NOT_AUTHORIZED_FOR_EXECUTION`. The historical base `1b55bea06dd580896cab3557ee3eaf47bec959b7` is not a current binding. This refresh observes canonical main `3d42ed625742c606d5d6773a3b9a6263ae27c379` / tree `cfd9f3dae3256778adf0a8288095a6012134d524`; any later grant must bind a fresh exact post-refresh base and verify accepted Task 1–5 interface blobs against their applicable acceptance records. The only contemplated path is `tests/vip_fvs/integration/test_three_profile_synthetic_space_contract.py`. The slice is strictly test-only and model-free. Keep generated inputs and temporary outputs synthetic/test-managed. Do not access assets/caches, use network/provider/cloud, load or infer with a model, probe MPS/hardware, process real/protected media, benchmark, index the archive, promote a Gate, mutate canonical main directly, or alter Task 0 evidence. Preserve Task 0/Gate B `NO_GO_BLOCKED`, H, all 56 predicate identities/statuses, all 13 refresh steps, Gate A's Task 1-only scope, and all authentic model/runtime/media gates.

