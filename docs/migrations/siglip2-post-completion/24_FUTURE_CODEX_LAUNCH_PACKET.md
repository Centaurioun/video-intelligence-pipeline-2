# Future Codex Launch Packet — SigLIP2 Migration

**Information state:** `STEP10_DOCUMENTS_CANONICALLY_ADOPTED` + `OWNER_APPROVED_FOR_PLANNING` + `TASK0_NO_GO_BLOCKED` + `NOT_AUTHORIZED_FOR_EXECUTION`

**2026-10-11 adoption state:** owner approval is recorded on PR #69 for exact originally reviewed implementation-plan blob `78127a9199a912531d5b2240eed66e93814d83f3`; PR #69 merged at `7f4a5ce1baf7de2aa580f1043502458336bf57fe`. The plan's current documentation version records `OWNER_APPROVED_FOR_PLANNING`. The accepted blob is provenance, not the current blob after this status correction. The Step 10 documents are canonical after PR #69. Task 0 remains `NO_GO_BLOCKED`; neither plan acceptance nor document adoption authorizes implementation.

## Use Condition

**This packet does not itself authorize implementation.** Task 1 is V2-related software implementation, not documentation-only work. Task 0 remains `NO_GO_BLOCKED` for Gate B/full migration, Tasks 2 onward, and runtime/model/media work. Task 1 may be considered despite a blocked full-migration receipt only after the exact ADR-0002 and coordinated subordinate amendment candidate is owner-accepted and canonically adopted, a fresh exact-main Task 1 scoped-readiness decision is independently accepted, and one separate explicit owner Task 1 execution authorization is issued. That decision must freshly evidence every Task 1-required A–D predicate and find it satisfied under its unchanged pass criteria; any required FAIL, BLOCKED, unresolved condition, or qualification that does not satisfy the existing criterion blocks Gate A. An explicitly permitted `NOT_APPLICABLE` remains only where the predicate already allows it. Literal checklist `PASS` and qualified overlay statuses such as `PASS_WITH_LIMITS` and `PASS_PLANNING_ONLY` retain their separate meanings and are never normalized or promoted. The authorization must bind the same decision and accepted plan, exact allowed files and operations, execution method, branch and base SHA, and expiry/supersession conditions. If any condition is missing, stale, or mismatched, stop with `TASK1_PREPARATORY_ENTRY_BLOCKED` and do not begin.

Gate A allows only the accepted plan's Task 1 closed, validated three-profile semantic-space contract: frozen profile validation, deterministic mapping to the existing `SemanticSpace` contract, synthetic identity fixtures, model-free tests, V1 identity-preservation regression, independent feature review, and bounded verification within the accepted Task 1 file scope. It does not include Task 2 or later, dependency/environment changes, real model or processor identity/acquisition/load, inference/MPS, archive/video/media input, provider/cloud/egress, benchmark, full-archive indexing, Gate promotion, or production integration. Gate A does not clear any Task 0 predicate or establish Gate B readiness.

Full migration, Gate B, remains subject to the unchanged Task 0 and all applicable model/runtime/media and later-stage gates. Any model, runtime, or media action requires its own exact current authorization.

Do not use this packet to start implementation until:

- V1 completion is verified and frozen;
- `19_POST_COMPLETION_REFRESH_PROTOCOL.md` has been completed;
- the full-migration checklist is satisfied for Gate B, or, for Gate A only, the separate scoped decision and authorization above are current;
- current migration design has passed Superpowers brainstorming approval;
- a current implementation plan exists;
- any model acquisition or real-media execution has its own explicit authorization.

## Fill Before Launch

Replace these placeholders from current repository evidence:

- `3586eeaa904fc5a2e6a2745078611886f482f3de` (preserved V1 source; local-first completion candidate `e956722a0fc2109eb4651ce728e919e691162511`)
- `NONE`
- `748818e867ce08ccc2367bad21df7d83eaf51d70` (refresh authority observation; refetch and verify before any future task)
- `docs/superpowers/specs/2026-10-09-vip-v2-siglip2-integration-design.md` (`OWNER_APPROVED_FOR_PLANNING`)
- `docs/superpowers/plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md` (`OWNER_APPROVED_FOR_PLANNING`; original accepted blob `78127a9199a912531d5b2240eed66e93814d83f3`; merged PR #69 at `7f4a5ce1baf7de2aa580f1043502458336bf57fe`)
- `BLOCKED`
- `BLOCKED`
- `BLOCKED`
- `docs/agent-runs/run-20261011-vip-v2-task0-final-gap-reconciliation/refresh-receipt.yaml` at `229d08f564fb8c21a7a119fc900eaac82cb64cd0` (`BLOCKED`, complete blocked-outcome receipt)
- Current runtime inventory: `docs/agent-runs/run-20261011-vip-v1-runtime-baseline-freeze/runtime-inventory.json` at `ce3f570016f3f13e9091fb6989f3a9d3ea783c7d` (`F07=PASS_CURRENT_RUNTIME_RECEIPT_ONLY`)

Do not invent a missing value.

## Codex Prompt Template

```text
You are implementing the post-completion SigLIP2 migration for
Centaurioun/video-intelligence-pipeline.

AUTHORITATIVE START:
- V1 preserved source SHA: `3586eeaa904fc5a2e6a2745078611886f482f3de`
- V1 local-first completion candidate: `e956722a0fc2109eb4651ce728e919e691162511`; release tag: `NONE`
- canonical-main evidence snapshot: `748818e867ce08ccc2367bad21df7d83eaf51d70` (must be freshly verified)
- accepted plan provenance: blob `78127a9199a912531d5b2240eed66e93814d83f3`; durable owner decision on PR #69; adoption merge `7f4a5ce1baf7de2aa580f1043502458336bf57fe`
- readiness: `NO_GO_BLOCKED`; design: `OWNER_APPROVED_FOR_PLANNING`

READ FIRST, IN ORDER:
1. AGENTS.md
2. docs/INDEX.md
3. current docs/project/00_PROJECT_CHARTER.md
4. current docs/project/01_CURRENT_STATE_AND_HANDOFF.md
5. current docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md
6. docs/project/STATE_MAINTENANCE_PROTOCOL.md
7. docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md
8. docs/migrations/siglip2-post-completion/00_README_AND_ENTRYPOINT.md
9. docs/migrations/siglip2-post-completion/01_AUTHORITY_SCOPE_AND_ACTIVATION.md
10. docs/migrations/siglip2-post-completion/19_POST_COMPLETION_REFRESH_PROTOCOL.md
11. `docs/agent-runs/run-20261011-vip-v2-task0-final-gap-reconciliation/refresh-receipt.yaml` (`BLOCKED`; not implementation-entry clearance)
12. docs/migrations/siglip2-post-completion/07_MIGRATION_SURFACE_SNAPSHOT.md
13. docs/migrations/siglip2-post-completion/08_HARDCODE_AND_ASSUMPTION_REGISTER.md
14. docs/migrations/siglip2-post-completion/09_PRESERVE_BOUNDARIES.md
15. docs/migrations/siglip2-post-completion/10_TARGET_MODEL_PROFILE_DESIGN.md
16. docs/migrations/siglip2-post-completion/11_V1_TO_V2_BASE_RUNBOOK.md
17. docs/migrations/siglip2-post-completion/14_TEST_AND_ACCEPTANCE_MATRIX.md
18. `docs/superpowers/specs/2026-10-09-vip-v2-siglip2-integration-design.md` (`OWNER_APPROVED_FOR_PLANNING` only)
19. `docs/superpowers/plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md` (exact accepted SHA must be supplied after owner decision)

Treat preserved V1 `3586eeaa904fc5a2e6a2745078611886f482f3de`, freshly verified canonical main, and the exact post-completion receipt as authority over preparation snapshots. If the receipt is missing or `BLOCKED`, Gate B/full migration remains blocked. The receipt's blocked status does not by itself bar Gate A once, and only once, every adopted-amendment, independent scoped-readiness, and separate owner execution-authorization condition above is met.

TASK:
Do not start implementation unless the explicit Use Condition above is proven. Planning documents do not authorize implementation. If and only if all Gate A conditions are proven, implement ONLY the accepted-plan Task 1 file and operation scope named in the matching owner execution authorization. Do not infer Gate B permission or proceed to Task 2 or later.

MANDATORY:
- use isolated branch/worktree;
- use test-driven-development for every behavior change;
- preserve V1 reproducibility;
- keep semantic spaces isolated;
- preserve source-native PTS/timebase and evidence rules;
- preserve authorization-before-real-runtime behavior;
- do not broaden into editing/render/QC refactors;
- do not implement So400m behavior beyond already-approved dimension/profile
  preparation needed by the V2 Base design;
- request code review before integration;
- run verification-before-completion before any DONE claim.

MODEL ACQUISITION:
V2 Base frozen revision: BLOCKED
V2 Base weights SHA256: BLOCKED
authorized local model root: BLOCKED

If any required model identity/authorization value is BLOCKED, do not
download, infer, or substitute it. Complete all dependency-safe code/test
work that remains authorized, then report BLOCKED precisely.

DO NOT:
- modify protected/archive media;
- run the 400-hour archive;
- claim benchmark superiority;
- mix V1 and V2 vectors;
- infer VFR frame positions from seconds × nominal FPS;
- force push, hard reset, git clean, or destructively rewrite history.

Return exact branch/worktree, base SHA, final SHA, files changed, tests run,
verification evidence, unresolved blockers, and whether the candidate is
ready for independent review.
```

## After V2 Base Completion

Do not reuse the same prompt unchanged for So400m.

Create a second launch from:

- the verified V2 Base candidate SHA;
- refreshed `12_V2_BASE_TO_SO400M_RUNBOOK.md`;
- exact frozen So400m model contract;
- current plan and authorization.

## Why This Packet Is a Template

Pre-completion paths and runtime facts may change.

The packet intentionally contains placeholders so a future agent cannot mistake today's snapshot for the final V1 migration base.

## Adopted pre-Gate-B synthetic launch path — execution not authorized

**Status:** `OWNER_ACCEPTED — CANONICALLY_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. The exact coordinated candidate `ae3939b9c0d98c24809246099c025bc3a60a0d50` / tree `11c9089016f9b0b1a8bd5ee2704d3022d74ef421` was adopted by PR #91 merge commit `25c29c07a8010db551a2ac08fcde72a9147c25d3`. The Gate B stop condition remains operative for authentic work; this adoption supersedes only the blanket Tasks 2–5 entry rule for T2-SYN/T3-SYN/T4-SYN, each under a separate exact grant. T5-SYN remains serial, requires accepted interfaces and its own later exact grant. Before any dispatch, re-read the adopted contracts, verify exact base and Task 1/interface fingerprints, and obtain a per-worker Owner grant binding exact paths, operations, side-effect-screened commands, environment, method, isolated branch/base, expiry, and supersession. Require disjoint ownership for concurrent T2/T3/T4. T5's selected tests must include and side-effect-screen `tests/vip_fvs/unit/test_real_source_service.py`, and explicitly assert no model open, asset read, cache access, or network call; if unavailable, narrow the authorization-order claim or defer T5. Unsafe tests are `NOT_RUN`. Adoption alone gives no task execution authority or READY status.

**Current Task 1 dependency reference for this proposal (2026-10-19):** the reviewed Task 1 candidate is `ff23e6af46ced80297c8fbc124c6ddf0b0ed288a` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`; its exact accepted `model_profile.py` source blob is `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`. The candidate is represented on current canonical main `342e6fbaa25d28511844b274bce7f927e2c0420d` / tree `d687a208e94eaa31a03fdd5981f57d91fecf91ee`. Its interface review remains `ACCEPT_WITH_LIMITS` for the model-free synthetic interface only. These commit/tree/blob identities are provenance bindings, not a substitute for the exact review artifact or for checking the accepted interface at each consuming task's exact base. A future grant must cite that review evidence and verify its bound interface descriptor at the exact base; missing, stale, or mismatched evidence blocks that task. This reference establishes no authentic tokenizer/model semantics, Task 2–5 readiness, adoption, or execution grant.

Every synthetic slice remains model/processor/checkpoint/cache blind, network/provider/cloud offline, and restricted to generated inputs and test-managed temporary files. Exclude dependency/config changes, real model loading/inference/MPS or hardware probes, real/protected media, benchmark/full archive, production integration, Gate promotion, and canonical-main writes. No result satisfies a checklist predicate or changes full Task 0/Gate B `NO_GO_BLOCKED`, H, the 56 IDs/statuses, protocol Steps 1–13, Gate A Task 1 scope, or authentic model/runtime/media gates. No worker is READY without the exact adoption, fresh check, and applicable grant.

## Proposed native-Base Task 4/5 launch condition — not active

**Status:** `PROPOSED_NOT_ADOPTED — NOT_AUTHORIZED_FOR_EXECUTION`. Do not launch either native slice until the exact coordinated amendment is independently reviewed, explicitly owner-adopted and canonically adopted (or accepted applicable Gate B is current), and a separate task-specific grant binds source/test/operations/environment/isolated branch/base SHA. Before Task 4 launch, require an independently accepted Task 1 `ModelProfile` interface fingerprint bound to the exact Task 4 source base; an exact previously accepted immutable source snapshot is sufficient only when its acceptance receipt/contract records and binds that fingerprint. Missing acceptance/fingerprint or stale/mismatched base/interface blocks launch; planning approval alone is not interface acceptance. Task 4 is confined to `experiments/persistent_local_index/siglip2_native.py` and its focused test. Task 5 is confined to `experiments/persistent_local_index/embedding.py`, `src/vip_fvs/cli.py`, and new `tests/vip_fvs/integration/test_native_base_cli_contract.py`; it needs its separate grant and independently accepted Task 4 interface for final verification whose acceptance receipt binds the Task 1 fingerprint. Before Task 5 launch, the exact base must also bind accepted Task 2 and Task 3 interface fingerprints. An exact, already-accepted immutable source snapshot may establish those fingerprints only when its accepted receipt or contract records each fingerprint and binds it to that snapshot; snapshot identity alone is insufficient. Recheck interfaces against their exact consuming bases and stop on stale or mismatched fingerprints. Screen the fake-injected tests for no model/processor/assets/cache/device/network/media access. Preserve V1 no-flag behavior, source authorization before factory creation, distinct V1/V2 Base semantic-space and generation identities, and native integer PTS/timebase handling. No authentic tokenizer/preprocessing/mask/pooling/device or retrieval-quality claim follows. T4-SYN/T5-SYN remains separate; Task 0/Gate B remain blocked and Tasks 6+ are excluded.

Before Task 5 BUILD starts, its exact base must bind either (a) an independently accepted Task 4 interface fingerprint whose acceptance receipt binds it to Task 4's exact source SHA, with that same fingerprint bound to Task 5's exact consuming base, or (b), only when Task 4 BUILD overlaps, an exact frozen Task 4 interface fingerprint independently reviewed and bound to both Task 4's exact source base and Task 5's exact consuming base. Final Task 5 VERIFY still requires the independently accepted Task 4 interface at the exact frozen SHA, matching the consumed fingerprint and retaining the Task 1 fingerprint binding. Any Task 4 interface change makes Task 5 descendants stale; stop and rebind/review before continuing.

## Proposed synthetic Task 9 preparatory launch path (T9-SYN) — not active

**Status (refreshed 2026-10-19):** PR #86 merged T9-SYN governance documentation at `dab471b768811a7c1e3791e4f79de4539bd12d33`; the historical M3 record still says `PREPARED_FOR_EXACT_OWNER_ADOPTION`. Keep that discrepancy visible. Neither governance adoption nor this refresh grants execution; T9-SYN remains `NOT_AUTHORIZED_FOR_EXECUTION` pending a separate exact Owner grant. The prior base `1b55bea06dd580896cab3557ee3eaf47bec959b7` and fingerprints below are historical. Current source-observation snapshot: main `3d42ed625742c606d5d6773a3b9a6263ae27c379` / tree `cfd9f3dae3256778adf0a8288095a6012134d524`. At that snapshot the source blob inventory is: Task 1 `experiments/persistent_local_index/model_profile.py` `45a2201e8aa38381978cbc3e5ef7f8898e767d0f`; Task 2 `storage.py` `b769889559c7d51955b8218e75fa870d225d143e`, `indexer.py` `c2a9b0a0aa028e33ece1437c4880b0bfb9fb7f69`; Task 3 `search.py` `61ba5cb8a4b12398094eb90a25bffa9f29e68d64`; Task 4 `siglip2_native.py` `b494379d3127e3c4600da7b7e071cc61279951d1`; Task 5 `embedding.py` `91e3f152b7dddcf182335061e2692ce57f3cbf80` and `src/vip_fvs/cli.py` `cce15b1eef6c90e07e7c30b708f705831f861991`. These hashes identify source bytes only; before any later grant, independently verify the exact post-refresh execution base and that each accepted interface/review record binds the consumed blob. Do not infer acceptance from code presence or historical candidate ancestry. The worker remains restricted to `tests/vip_fvs/integration/test_three_profile_synthetic_space_contract.py`; no production source in `src/` or `experiments/` may be edited. Generated inputs and test-managed fixtures only; no model/weights loading, network/cloud, archive/real media, or Gate B alteration.

