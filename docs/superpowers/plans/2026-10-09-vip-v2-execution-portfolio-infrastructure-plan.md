# VIP V2 Execution Portfolio Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Repository override:** current `AGENTS.md` and resource-policy-v5 use the repository-native, rolling `BUILD/VERIFY/REPAIR` portfolio with `dispatching-parallel-agents`, RED/GREEN TDD, systematic-debugging, feature-level code review and verification-before-completion. Do **not** automatically install the stock reviewer-after-every-inner-task loop. The owner must review this plan and choose the execution method before work begins.

**Goal:** Establish a new, independently verified, restartable VIP V2 Execution Portfolio control plane in the existing VIP repository, without altering the historical Remaining Work Portfolio or dispatching any V2 product implementation/model tasks.

**Architecture:** A versioned and strictly isolated `vip-v2-execution-portfolio-20261009-v1` epoch under `.orchestration/vip-v2-portfolio/` uses a minimal Python standard-library validation/DAG/launch/reconciliation toolkit. Frozen task cores bind the already approved V1 -> SigLIP2 Base -> SO400M product plan, while disposable launch overlays bind live SHA, resource leases, authority and writer ownership. A sole portfolio coordinator owns launch, reconciliation and the integration branch; A–G areas are logical ownership domains and activate only for useful dependency-safe work.

**Tech Stack:** Python standard library 3.x (use the repository's actual tested Python interpreter), `pytest`, JSON/JSONL, Git/GitHub SHA/tree/blobs, GitHub-protected PRs, existing `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`. **No runtime packages, checkpoint downloads, MPS inference or protected media are needed for this infrastructure milestone.**

**Spec:** `docs/superpowers/specs/2026-10-09-vip-v2-execution-portfolio-design.md` (owner-approved architecture, merged in PR #66 at `bc20ba0c0437d035dc1b7040e96f313ddf953015`).

**Independent product plan (read-only contract):** `docs/superpowers/plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md` (Tasks 0–10; still `PENDING_OWNER_PLAN_REVIEW`).

**Preserved V1:** `preservation/vip-v1-post-v2-design-20261009@3586eeaa904fc5a2e6a2745078611886f482f3de`. This is a Git-object/code preservation ref, not model/media/runtime/index backup.

**Plan status:** `PLAN_PUBLISHED_FOR_OWNER_REVIEW`. **Not executed.** No new Portfolio epoch directories, controllers, launcher outputs or runtime tests have been created by writing this document.

## Global Constraints

1. The new Portfolio MUST NOT reuse, amend or reactivate `.orchestration/remaining-work/`, its `H3-*` IDs, controller branches, metrics, frozen prompts, hashes or ledger states. Its historical terminal controller `controller/remaining-work/authoritative@a81104f47667a7f9ee1f47a86e1bfe711bfa2dd4` and G `controller/area/G@988b8790cc45ad1c1093f0d1ebbae15ab0716f38` are **read-only evidence**.
2. Do not simply fork the old verifier: `scripts/verify-remaining-work-atlas.py`, `scripts/remaining_work_contracts.py` and `scripts/render-remaining-work-launch-pack.py` contain old-epoch paths, SHA/blob history, state schema and/or prompt-bootstrap assumptions. Extract small pure invariant ideas; **leave those scripts and their historical tests unchanged**.
3. Frozen V1 ref, current protected main, ADR-0002, 11-task product plan, all source/PTS/evidence/authorization invariants and existing resource-policy-v5 remain governing. New epoch policy can **tighten**, never silently widen, a permission.
4. The initial new `MODEL_MPS` lease is **1**. `ENV_ADMIN` has **1** global writer. Heavy work is never dispatched just because a resource lease is idle. Never treat generic v5 MPS initial 2 as a grant to load two SO400M sessions.
5. Every state/prompt/receipt has exact `portfolio_id`, schema version and compatible `epoch`; no foreign old-H3 ID allowed. Use exact, immutable SHA/tree/contract fingerprints. Keep distinct V1, V2 Base and V2 SO400M profile/index state; 768 ≠ 1152 geometry and equal dimension does not imply compatible embedding spaces.
6. A Source/Model/Runtime permission is a **separate precondition** from a DAG dependency or a resource lease. Initial permissions include **NO model acquisition/inference, NO protected-media access, NO provider/cloud use, NO main merge and NO Gate promotion**. No synthetic tool can grant these merely by changing a JSON status.
7. Existing Product Task 0 post-completion refresh/readiness is a `HARD_VERIFY_DEPENDENCY` for code-writing migration tasks. Independent read-only source/test/contract inspection may continue without inventing a refresh PASS. Native V2 Base must be accepted before SO400M real integration per ADR-0002.
8. Task writer ownership is exclusive by paths **and** consumed shared-contract identity. Ownership transfer B -> F for `model_profile.py`; D -> F for `siglip2_native.py`; E owns FVS/CLI integration. No sibling may fix another owner's source path without a durable reviewed transfer.
9. The Portfolio is a control plane, not a second product/daemon/provider platform. Do not create permanent N-agent quotas or user-facing dashboards. Fall back to **non-dispatched copy-ready Launch Packs** if nested/multi-root Codex session spawning is not actually supported.
10. Worktree/branch creation during later implementation is isolated, serialized and non-destructive; no hard reset, git clean, force push, rebase of historical branches or pruning/deletion. Canonical main integration requires **new explicit owner authorization** and protected PR checks.
11. No project feature or source code change except to this portfolio's own infrastructure; its interface to the product implementation plan is **read-only**. Tests use entirely synthetic/deterministic snapshots and fake Git execution.
12. Preserve project-specific `AGENTS.md` model policy: Codex `LUNA` family, `medium` reasoning, resolve/freeze one supported concrete model per Goal; no silent fallback. No assumption a Codex instance can spawn external top-level sessions.
13. Existing `docs/project/STATE_MAINTENANCE_PROTOCOL.md` governs later state handoff updates; do not rewrite historical audits to claim the new epoch is active.
14. Document only results actually executed in a future implementation session. Here, all test commands are **planned**, not reported as passing.

## File and ownership map (implementation targets; none created yet)

| Path | Single responsibility | Owner |
|---|---|---|
| `scripts/vip_v2_portfolio/__init__.py` | Namespace/version marker only | infrastructure |
| `scripts/vip_v2_portfolio/schema.py` | Strict epoch manifest/record schema, SHA checks and canonical hash | bootstrap owner |
| `scripts/vip_v2_portfolio/dag.py` | Dependency DAG, no overlapping writers, READY status against already validated state | scheduling owner |
| `scripts/vip_v2_portfolio/authority.py` | Permission and resource-lease acceptance; default-deny heavy actions | authority owner |
| `scripts/vip_v2_portfolio/packets.py` | Frozen Core, content hash, Launch Overlay and read-only Launch Pack renderer | launch owner |
| `scripts/vip_v2_portfolio/reconcile.py` | Candidate receipt/Git-generation verification, Problem/stale transitions, bounded recovery | reconciliation owner |
| `scripts/vip_v2_portfolio/cli.py` | Thin `verify`, `render --dry-run`, `reconcile --dry-run` entrypoints; no agent spawning | integration owner |
| `tests/scripts/test_vip_v2_portfolio_schema.py` | Cross-epoch/manifest/hash rejection | bootstrap owner |
| `tests/scripts/test_vip_v2_portfolio_dag.py` | DAG, writer collision, dependency/order | scheduling owner |
| `tests/scripts/test_vip_v2_portfolio_authority.py` | Permission, MPS/ENV_ADMIN safety | authority owner |
| `tests/scripts/test_vip_v2_portfolio_packets.py` | Frozen Core/overlay/launch signatures | launch owner |
| `tests/scripts/test_vip_v2_portfolio_reconcile.py` | Stale-base, Git evidence, receipts, problem bounds, restart | reconciliation owner |
| `tests/scripts/test_vip_v2_portfolio_cli.py` | End-to-end synthetic bootstrap/negative and nondispatch verification | integration owner |
| `.orchestration/vip-v2-portfolio/START_HERE.md` | Epoch-specific controller recovery instructions | bootstrap owner |
| `.orchestration/vip-v2-portfolio/manifest.json` | Immutable epoch identity, baseline, current design/product-plan refs | bootstrap owner |
| `.orchestration/vip-v2-portfolio/controller-state.json` | New epoch scheduler state, not historical progress | reconciliation owner |
| `.orchestration/vip-v2-portfolio/atlas/{atlas.json,TABLE_OF_CONTENTS.md,contract-registry.json,authority-backlog.json}` | Exact dependency graph, provenance, blocked permissions | DAG owner |
| `.orchestration/vip-v2-portfolio/prompts/V2-H3-*/{core.json,core.md,overlay-*.json}` | Frozen task identity and launch-only mutable inputs | launch owner |
| `.orchestration/vip-v2-portfolio/launch-packs/<batch>/manifest.json` | Safe candidate dispatch instructions, generated but **not sent** | launch owner |
| `.orchestration/vip-v2-portfolio/areas/<A-G>/` and `runs/`, `problems/` | **Runtime-created only after authorized execution**; no placeholder spam | controller owner |
| `.orchestration/vip-v2-portfolio/verification/bootstrap-<generation>.json` | Evidence receipt binding exact Atlas/cores/launch snapshot | review owner |

Avoid touching product Python modules, model weights, V1 index fixtures, existing `scripts/remaining_work_*.py`, existing `tests/scripts/test_remaining_work_*.py`, historical ledgers and protocol texts absent a separately approved design change.

## Review Focus — five most likely user-visible failure classes

1. **Wrong-epoch inputs:** an old `H3-C02` or Remaining Work receipt is treated as new V2 progress. Pin by `test_legacy_h3_or_wrong_portfolio_id_rejected` in Task 1.
2. **Stale controller restart:** an apparent BUILD_GREEN receipt from a candidate commit older than an accepted contract delta becomes READY/VERIFIED incorrectly. Pin by `test_restart_rejects_stale_candidate_and_preserves_unaffected_frontier` in Task 5.
3. **Concurrent shared writers:** B and F are both granted `model_profile.py` in the same generation. Pin by `test_disallow_overlapping_writer_domains` in Task 2.
4. **False MPS permission:** an available resource slot causes a Q4/SO400M model load even though no model/runtime grant exists. Pin by `test_mps_lease_does_not_grant_runtime_authorization` in Task 3.
5. **Misleading auto-dispatch:** a generated Launch Pack immediately starts worker sessions or marks tasks executed. Pin by `test_render_is_no_side_effect_and_undispatched` in Task 4/6.

---

## Task 1: New epoch manifest, strict schemas and legacy-state firewall

**Files:**
- Create: `scripts/vip_v2_portfolio/__init__.py`, `scripts/vip_v2_portfolio/schema.py`
- Test: `tests/scripts/test_vip_v2_portfolio_schema.py`

**Interfaces:**
- `PORTFOLIO_ID: Final[str] = "vip-v2-execution-portfolio-20261009-v1"`
- `V1_BASE_SHA: Final[str] = "3586eeaa904fc5a2e6a2745078611886f482f3de"`
- `validate_manifest(manifest: dict[str, object]) -> list[str]`
- `validate_record(record: dict[str, object], *, expected_kind: str, portfolio_id: str = PORTFOLIO_ID) -> list[str]`
- `canonical_digest(record: dict[str, object]) -> str` — SHA256 of UTF-8 `json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`; exclude explicitly declared self-`digest` field before hashing.

- [ ] **Step 1: RED.** Add `test_manifest_binds_v1_sha_and_exact_product_plan`, `test_legacy_h3_or_wrong_portfolio_id_rejected`, `test_digest_is_order_independent_and_invalid_claimed_digest_is_rejected`. Assert accepted `portfolio_id`, fixed baseline SHA, schema `vip-v2-portfolio-manifest.v1`; `H3-A01` forbidden while `V2-H3-A01` valid; foreign `remaining-work-execution-atlas-v1` denied.
- [ ] **Step 2: Run RED** `PYTHONPATH=src:experiments:scripts python -m pytest -q tests/scripts/test_vip_v2_portfolio_schema.py`. Expected fail on absent new functions (not missing pytest).
- [ ] **Step 3: GREEN.** Implement strict dict validation (no private paths, no float SHAs, exact full-hex SHA); canonical_digest stable; a record validator must compare a supplied digest against the recomputed payload digest and reject any mismatched claim. Schema distinguishes `epoch_id`, `schema_version`, `portfolio_id`, `record_type`, `base_sha`.
- [ ] **Step 4: Run GREEN** same command; expected zero failed assertions, non-zero exit blocks next task.
- [ ] **Step 5: Commit** only new code/test files with `feat(portfolio-v2): add epoch identity and legacy-state firewall`.

## Task 2: Bounded V2 DAG, dependency and writer ownership validator

**Files:**
- Create: `scripts/vip_v2_portfolio/dag.py`
- Test: `tests/scripts/test_vip_v2_portfolio_dag.py`

**Interfaces:**
- `validate_graph(nodes: list[dict[str, object]]) -> list[str]` enforces unique `V2-H3-*` IDs, acyclicity, known `INDEPENDENT`, `SOFT_BUILD_DEPENDENCY`, `HARD_BUILD_DEPENDENCY`, `HARD_VERIFY_DEPENDENCY` edge kinds, and known consumed/produced contract identifiers.
- `detect_writer_conflicts(nodes: list[dict[str, object]]) -> list[tuple[str, str, str]]` returns sorted task/task/path conflicts only when both candidate writers may concurrently be READY/BUILDING; path prefixes count as overlaps, including shared-contract owner IDs.
- `compute_build_ready(nodes: list[dict[str, object]], *, completed_state_by_id: dict[str, str]) -> list[str]` applies exact dependency satisfaction state, **not** an arbitrary chapter ordering; a blocked authority condition is not classified green.

- [ ] **Step 1: RED.** Add `test_cycle_and_unknown_dependency_rejected`, `test_hard_verify_does_not_release_on_build_green`, `test_soft_build_releases_after_build_green`, `test_disallow_overlapping_writer_domains`, `test_independent_read_only_remains_eligible`. Use small 3–5 node synthetic graphs.
- [ ] **Step 2: Run RED** `PYTHONPATH=src:experiments:scripts python -m pytest -q tests/scripts/test_vip_v2_portfolio_dag.py`. Expect missing behavior.
- [ ] **Step 3: GREEN.** Implement deterministic cycle detection and prefix/shared-contract collision checks; output sorted errors and stable eligible task IDs. Reject F's write access to B's `model_profile.py` and D's `siglip2_native.py` until explicit ownership-transfer contract is VERIFIED.
- [ ] **Step 4: Run GREEN** focused suite, then schema suite; assert no historical IDs accepted.
- [ ] **Step 5: Commit** code/tests with `feat(portfolio-v2): validate DAG and exclusive contract owners`.

## Task 3: Strict authority predicates and resource leases

**Files:**
- Create: `scripts/vip_v2_portfolio/authority.py`
- Test: `tests/scripts/test_vip_v2_portfolio_authority.py`

**Interfaces:**
- `validate_operation(task: dict[str, object], *, grants: dict[str, object], active_leases: dict[str, int]) -> list[str]`. Returns list of blockers; no implicit permission. `grants` must be exact-epoch, digest-bound and backed by an externally verified owner-authorization record for any privileged class; do not introduce an unsupported signature/minting mechanism. A bare `"allowed": true` is insufficient.
- `LEASE_LIMITS_V1 = {"MODEL_MPS": 1, "ENV_ADMIN": 1}`. `LIGHTWEIGHT_CPU_TEST` uses disjoint-write + measured-resource principles from v5 and has no fabricated fixed count.
- Represent `MODEL_DOWNLOAD`, `MODEL_RUNTIME`, `PROTECTED_MEDIA`, `PROVIDER_EGRESS`, `MAIN_MERGE`, `GATE_PROMOTION` as explicit default-DENY operations. The existence of a local checkpoint is **not** an authorization.

- [ ] **Step 1: RED.** Add `test_mps_lease_does_not_grant_runtime_authorization`, `test_second_mps_or_env_admin_job_denied`, `test_archive_path_denied_without_source_authorization`, `test_unrelated_lightweight_work_survives_mps_block`, `test_grant_wrong_epoch_or_scope_denied`.
- [ ] **Step 2: Run RED** `PYTHONPATH=src:experiments:scripts python -m pytest -q tests/scripts/test_vip_v2_portfolio_authority.py`.
- [ ] **Step 3: GREEN.** Implement default-deny grant check that validates external owner authority reference **without inventing a mechanism to mint permission from Portfolio state**. Use exact authorized action + source/checkpoint identity + applicable timestamps/expiry if actually present; no synthesis of a grant.
- [ ] **Step 4: Run GREEN** focused suite; verify resource-policy-v5 unchanged and limits strict.
- [ ] **Step 5: Commit** code/tests with `feat(portfolio-v2): require permissions and safe heavy resource leases`.

## Task 4: Frozen Core, Launch Overlay and deterministic no-dispatch renderer

**Files:**
- Create: `scripts/vip_v2_portfolio/packets.py`
- Test: `tests/scripts/test_vip_v2_portfolio_packets.py`

**Interfaces:**
- `validate_core(core: dict[str, object], core_markdown: str) -> list[str]` checks exact immutable core SHA256, epoch/task/version, ownership, tests, prohibited actions and consumed contracts.
- `validate_overlay(overlay: dict[str, object], *, core_digest: str, dependency_heads: dict[str, str]) -> list[str]` checks launch-time current refs, base SHA, branch/worktree, grants/leases, source/precision if applicable, stale ancestor fingerprint and unresolved Problems.
- `render_pack(*, manifest: dict[str, object], eligible_nodes: list[dict[str, object]], cores: dict[str, dict[str, object]], overlays: dict[str, dict[str, object]]) -> dict[str, object]` returns **pure JSON data** with `state="GENERATED_NOT_DISPATCHED"`; no subprocess, Git mutation or task spawning.
- `rendered_at_sha` is an exact SHA supplied by caller, not guessed via `datetime.now()`. Generate an explicit `run_id` only from caller input.

- [ ] **Step 1: RED.** Add `test_core_text_sha_mismatch_rejected`, `test_wrong_dependency_head_overlay_rejected`, `test_render_is_no_side_effect_and_undispatched`, `test_missing_core_blocks_pack_no_placeholder`, `test_no_resource_or_permission_implicit_fill`.
- [ ] **Step 2: Run RED** `PYTHONPATH=src:experiments:scripts python -m pytest -q tests/scripts/test_vip_v2_portfolio_packets.py`.
- [ ] **Step 3: GREEN.** Build exact canonical serialization and deterministic pack composition from Task 1–3 validation; no automatic network, write or child-spawn actions.
- [ ] **Step 4: Run GREEN** focused suite and Task 1–3 suites.
- [ ] **Step 5: Commit** only packet code/tests with `feat(portfolio-v2): render verified frozen-core launch packs without dispatch`.

## Task 5: Immutable candidate evidence, Problem ledger and restart reconciliation

**Files:**
- Create: `scripts/vip_v2_portfolio/reconcile.py`
- Test: `tests/scripts/test_vip_v2_portfolio_reconcile.py`

**Interfaces:**
- `validate_candidate_receipt(receipt: dict[str, object], *, expected_contracts: dict[str, str], git_evidence: dict[str, str]) -> list[str]`, where `git_evidence` must be obtained by actual Git verification in the caller, not accepted from the untrusted worker report itself.
- `reconcile_frontier(*, nodes: list[dict[str, object]], receipts: list[dict[str, object]], contract_heads: dict[str, str], problems: list[dict[str, object]]) -> dict[str, object]` returns a **new** epoch state without mutating input data or accepted immutable receipts.
- Model states `PLANNED, READY, BUILDING, BUILD_GREEN, VERIFY_READY, VERIFYING, VERIFIED, REPAIRING, PARKED, STALE_IN_FLIGHT, DIRTY_BY_CONTRACT_DELTA, SUPERSEDED`. `NOT_OBSERVED` remains missing-evidence marker, not evidence strength.

- [ ] **Step 1: RED.** Add `test_restart_rejects_stale_candidate_and_preserves_unaffected_frontier`, `test_build_green_without_review_not_verified`, `test_candidate_report_head_disagrees_with_verified_git_tree`, `test_three_failed_repair_generations_park_only_affected_descendants`, `test_duplicate_receipt_cannot_double_count_progress`.
- [ ] **Step 2: Run RED** `PYTHONPATH=src:experiments:scripts python -m pytest -q tests/scripts/test_vip_v2_portfolio_reconcile.py`.
- [ ] **Step 3: GREEN.** Validate exact immutable SHA/tree, Git authorization, source/contract version, verified test/reviewer candidate binding, consistent Problem severity; apply bounded v5 remediation. Never close a model permission gap by incrementing a task status. Progress weights use only newly frozen V2 H3 tasks; historical 100 units not imported.
- [ ] **Step 4: Run GREEN** focused and DAG/packet suites; restart with reordered receipts and assert same canonical outcome.
- [ ] **Step 5: Commit** new code/tests with `feat(portfolio-v2): reconcile SHA-bound milestones and quarantine stale work`.

## Task 6: Thin read-only verify/render CLI and isolated fake-Git acceptance

**Files:**
- Create: `scripts/vip_v2_portfolio/cli.py`
- Test: `tests/scripts/test_vip_v2_portfolio_cli.py`

**Interfaces:**
- `main(argv: list[str] | None = None) -> int` using `argparse` subcommands:
  - `verify --root <repo> --epoch-dir .orchestration/vip-v2-portfolio` — read-only; exit 0 only if all declared epoch/path/manifest/atlas/core/receipt checks pass; otherwise nonzero with exact errors.
  - `render --root <repo> --epoch-dir ... --batch-id <unique> --generated-at-sha <full40> --dry-run` — prints generated `GENERATED_NOT_DISPATCHED` JSON to stdout **without writing or dispatching**.
  - `reconcile --root <repo> --epoch-dir ... --dry-run` — outputs newly computed state; does not persist/merge/push automatically.
- Never import/call the existing Remaining Work verifier or renderer as an epoch state substitute; old epoch scripts remain usable independently.

- [ ] **Step 1: RED.** Add `test_cli_rejects_legacy_epoch_dir_even_if_json_looks_valid`, `test_verify_nonzero_on_invalid_core_and_bad_graph`, `test_render_dry_run_does_not_write_worktrees_or_spawn`, `test_reconcile_dry_run_has_no_side_effect`, `test_old_remaining_work_validator_still_works_on_its_existing_fixtures`.
- [ ] **Step 2: Run RED** `PYTHONPATH=src:experiments:scripts python -m pytest -q tests/scripts/test_vip_v2_portfolio_cli.py` with fixture Git repository/local temp dirs, no external network.
- [ ] **Step 3: GREEN.** Implement CLI wiring of Tasks 1–5. Check path containment under requested repository root, exact `portfolio_id` and allowed epoch subdir. Git source verification must use safe read-only commands (`git rev-parse`, `git show`, `git merge-base --is-ancestor`) with controlled argument arrays, never shell-interpolated paths.
- [ ] **Step 4: Run GREEN** focused, all `tests/scripts/test_vip_v2_portfolio_*.py`, and existing `test_verify_remaining_work_atlas.py`, `test_render_remaining_work_launch_pack.py`; new code must not mutate old epoch artifacts.
- [ ] **Step 5: Commit** with `feat(portfolio-v2): expose safe read-only CLI for new epoch`.

## Task 7: New Portfolio bootstrap, A–G Atlas and *undispatched* initial Launch Pack

**Files:**
- Create: `.orchestration/vip-v2-portfolio/START_HERE.md`, `manifest.json`, `controller-state.json`
- Create: `.orchestration/vip-v2-portfolio/atlas/{atlas.json,TABLE_OF_CONTENTS.md,contract-registry.json,authority-backlog.json}`
- Create **only actually required** `.orchestration/vip-v2-portfolio/prompts/V2-H3-*/core.json`, `core.md`, and launch-time `overlay-001.json` for the legitimate initial READY work
- Create: `.orchestration/vip-v2-portfolio/launch-packs/batch-001/manifest.json` and compact static bootstrap receipt under `verification/`
- Test: `tests/scripts/test_vip_v2_portfolio_cli.py` (fixture-backed end-to-end read)

**Interfaces/Atlas mapping (no product execution):**
- `V2-H3-A01` — Product Task 0 post-completion refresh/readiness; source-changing descendants require actual verification.
- `V2-H3-B01` — Product Task 1 profile+SemanticSpace; HARD dependency on A01 verified.
- `V2-H3-C01` and `V2-H3-C02` — Product Tasks 2/3 index writer/recovery, then search/fake query; after B01 contract.
- `V2-H3-D01` and `V2-H3-D02` — Product Tasks 4/6 V2 Base mock/native, then separately authorized real acceptance. D01 after B01; D02 after E01 integration and required model grant.
- `V2-H3-E01` / `V2-H3-E02` — Product Tasks 5/9 FVS/CLI and synthetic PTS; E01 after C01/C02/D01, E02 can start synthetic checks after E01.
- `V2-H3-F01` / `V2-H3-F02` — Product Tasks 7/8 SO400M native extension and separately authorized real smoke; F01 after D02 VERIFIED and shared path handoff; F02 requires fresh permission and MPS preflight.
- `V2-H3-G01` — Product Task 10 independent final convergence; interim read-only VERIFY is triggered by individual BUILD_GREEN receipts; main integration separately authorized.
- Optional **genuine, nonduplicate** read-only evidence packets (e.g. V1 test map, vector-geometry map, native tokenizer static audit, SO400M immutable-spike contract audit) can start before A01 verification. Create only if they produce distinct evidence needed by descendants; do not create 5 work packets just to fill A–F slots.

- [ ] **Step 1: RED.** Add `test_bootstrap_atlas_has_unique_ids_acyclic_dependency_graph`, `test_initial_pack_dispatch_count_is_zero`, `test_base_precedes_so400m_and_model_auth_defaults_denied`, `test_task0_gate_blocks_all_source_mutation`, `test_history_state_is_not_imported`.
- [ ] **Step 2: Run RED** `PYTHONPATH=src:experiments:scripts python -m pytest -q tests/scripts/test_vip_v2_portfolio_cli.py`; synthetic fixture should fail without new bootstrap files.
- [ ] **Step 3: GREEN.** Author minimum Atlas and bootstrap metadata with exact owner-reviewed `main` and preserved V1 SHA; freeze only the initial legitimate Frozen Cores and generate overlays from actual Git facts. **No invented commit IDs, completed percentages, real model asset state or authorization record**. Initial launch-pack state strictly `GENERATED_NOT_DISPATCHED`. Explicit V2 per-domain status starts `PLANNED` or `PARKED_AUTHORIZATION` as warranted; READY requires actual predicates.
- [ ] **Step 4: Verify** `PYTHONPATH=src:experiments:scripts python -m scripts.vip_v2_portfolio.cli verify --root . --epoch-dir .orchestration/vip-v2-portfolio` with expected exit 0; `render --dry-run` produces unchanged repository state and explicit nondispatch. Re-run new and old verifier tests. Compare historical preserved refs before/after.
- [ ] **Step 5: Commit** only new epoch files and bootstrap tests; no worker session dispatch, no full 11-task artificial prompt library if those tasks are not READY.

## Task 8: Independent verification, recovery trial and owner-ready handoff

**Files:**
- Create: `.orchestration/vip-v2-portfolio/verification/bootstrap-001.json` (final hash-bound verification receipt)
- Modify only if current project maintenance protocol requires: a **small pointer** in `docs/INDEX.md` or `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` after actual accepted bootstrap; no rewriting old progress.
- Tests: complete new portfolio suite and historical unaffected suites; no product runtime.

- [ ] **Step 1: Test independent recovery.** From fresh deterministic copy/checkout or synthetic snapshot, verify new controller recovers identical READY/PARKED frontiers, refuses stale and old-epoch receipts, and does not duplicate work.
- [ ] **Step 2: Run exact suite.** `PYTHONPATH=src:experiments:scripts python -m pytest -q tests/scripts/test_vip_v2_portfolio_*.py tests/scripts/test_verify_remaining_work_atlas.py tests/scripts/test_render_remaining_work_launch_pack.py tests/scripts/test_remaining_work_contracts.py tests/scripts/test_preflight_remaining_work_launch.py`. **Caveat:** shell-glob expansion is environment-specific; if using CI, list the new test paths explicitly. Report actual count, exit status and inherited environment limitations, never guess pass.
- [ ] **Step 3: Check repo safety.** Inspect `git diff --name-status <frozen-base>...HEAD`, `git status --porcelain=v1`, new state refs, `git diff --check`, `scripts/verify-workspace.sh` and secret audit under current repository rules. Verify untouched historical Remaining Work state + preservation ref. Do not pass by fabricating historical ledger objects.
- [ ] **Step 4: Independent feature-level review.** `requesting-code-review` on exact candidate SHA, including adversarial audit of five Review Focus failures, authorization forgery, stale Git evidence and source/memory gates. `receiving-code-review` + systematic-debugging/TDD on any actual findings, then re-run checks against new SHA.
- [ ] **Step 5: Commit and safely push milestone** to its designated isolated execution branch, verify local == remote SHA, keep canonical main unchanged, emit concise `PORTFOLIO_BOOTSTRAP_VERIFIED` **only if** every acceptance check actually passes; else `PORTFOLIO_BOOTSTRAP_BLOCKED` with exact reasons.
- [ ] **Step 6: Stop.** Return new Portfolio epoch ID, immutable bootstrap SHA, generated but **undispatched** Launch Pack ref, historical isolation proof, available READY and blocked nodes, actual test outputs and earliest separately authorized multi-Codex execution Goal. No model download/runtime, V1 code migration, heavy MPS worker, protected source use or automatic main merge.

## Integration and dependency order (not an invitation to dispatch)

```text
Owner review of this infrastructure plan + execution-method approval
  -> 1 schema/epoch -> 2 DAG/ownership --\
             \-> 3 authority/resources ------> 4 Frozen Core / overlay / pack
                   2,3,4 -> 5 receipts/reconciliation
                            -> 6 read-only CLI
                            -> 7 new epoch Atlas + initial nondispatched Launch Pack
                            -> 8 independent verification and handoff
  -> separately authorized Portfolio Codex root / area starts
  -> product migration plan Task 0–10 through real evidence/permission gates
  -> separately planned three-arm benchmark after candidate readiness
```

Tasks 2 and 3 can run concurrently **after Task 1** if worktrees and tests are separate; Tasks 4 and 5 depend on their verified interfaces. Do not manufacture subagent work for an idle controller. Keep historical control-plane evidence and new epoch writes in separate namespaces.

## Spec-to-plan coverage and self-review

- **Scope:** one infrastructure subsystem. This plan does not duplicate the product integration plan, implement SigLIP2 encoders/index changes or initiate model/media execution.
- **Files:** each new module has one responsibility; existing historical scripts and tests remain untouched. Initialization of files under `.orchestration/vip-v2-portfolio` occurs only during a later approved implementation task.
- **Interfaces:** Task 1 schema helpers consumed by 2–6; Task 2 DAG; Task 3 authority; Task 4 launch; Task 5 immutable reconciliation; Task 6 CLI; Task 7 bootstrap; Task 8 independent verification. All names and signatures appear where first defined.
- **Review Focus:** old-epoch H3, stale candidate, overlapping writer, MPS false-grant and unintended dispatch each have explicit negative tests.
- **Verification:** no tests executed for this plan; exact commands and outputs to look for are specified; future implementers must record actual exit statuses and refrain from unverifiable PASS claims.
- **Approval boundary:** `PLAN_PUBLISHED_FOR_OWNER_REVIEW`. **The user must review this written infrastructure plan and select a repository-compliant execution method.** Only then may Codex build the new orchestration infrastructure in isolated worktrees. Portfolio workers, actual V2 migration, checkpoint/model inference, archive work and protected main merges need their separately applicable current authorizations.
