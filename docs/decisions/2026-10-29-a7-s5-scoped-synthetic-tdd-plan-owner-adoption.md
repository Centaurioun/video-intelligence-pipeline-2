# A-7 S5 Conditional Synthetic TDD Plan — Owner Adoption

**Status: OWNER PLAN ADOPTED — IMPLEMENTATION REQUIRES SEPARATE EXACT GRANTS — PRODUCTION BLOCKED.**

**Decision scope:** documentation and conditional execution-plan adoption only. This record does not authorize source or test writes.

**Canonical base before integration:** `bc032924d7129f3a7b96a9db17942d007757b00f`

**Canonical main after proposal integration:** `d07a5076b8ea1a9d9fb6d60c5b667f646c5d9a56`

**Controlling architecture:** the adopted A-7 D1–D7 decision in `docs/decisions/2026-10-28-a7-s5-shared-admission-owner-adoption.md`, together with the A-12/P-11 amendment adopted through PR #251.

## Owner disposition

By submitting the Goal that created this record, the Repository Owner makes these bounded decisions:

1. Accept PR #255 as a durable record of **partial synthetic diagnostic evidence**. Its verdict remains `BLOCKED_PENDING_SYNTHETIC_EVIDENCE`. The report does not establish complete reproducibility of the temporary actual-helper experiment, production resource limits, supported operating systems, comprehensive filesystem race resistance, full E01/S5/ReviewBundle integration, passing consumer regressions, or production readiness.
2. Adopt the exact reviewed plan in PR #256 at commit `494b4066caa950e4ae28c780a531299ce9acdcf0` as the conditional synthetic-only TDD execution blueprint for Gate-3 A-7 S5. Its `PROPOSED` wording remains intact as historical proposal content; this separate record is the Owner's plan-adoption disposition.
3. Keep every implementation slice subject to a separate exact Owner grant naming its base, exclusive writable paths, finite test limits, permitted commands, and stop conditions.

The dispositions are:

- `PLAN_ADOPTED_FOR_SEPARATELY_AUTHORIZED_SYNTHETIC_TDD`
- `T1_READY_FOR_SEPARATE_SYNTHETIC_IMPLEMENTATION_AUTHORIZATION`
- `T2_BLOCKED_PENDING_EXACT_D2_GRANT_AND_ATOMIC_CALLER_CLOSURE`
- `T3_BLOCKED_AT_IMPLEMENTATION_IF_PUBLIC_E01_BUDGET_PATH_UNRESOLVED`
- `IMPLEMENTATION_AUTHORIZED=FALSE`
- `PRODUCTION_READY=FALSE`
- `PRODUCTION_RESOURCE_BUDGET=PENDING_EVIDENCE`

## Integrated proposal identities

| Item | Candidate identity | Integration identity | Scope/result |
|---|---|---|---|
| PR #255 — synthetic readiness evidence | HEAD `20a2e8a76482ce31ea1648f73bed0eedf5efa7e7`, GitHub signature verified | Merge commit `aca89ed71051b98a2f9b57e68096f2e3e45335bc`; parents `bc032924…` and `20a2e8a…` | Adds only `docs/agent-runs/2026-10-28-a7-s5-synthetic-readiness-evidence.md`; verdict remains blocked. |
| PR #256 — conditional TDD plan | HEAD `494b4066caa950e4ae28c780a531299ce9acdcf0`, GitHub signature verified | Merge commit `d07a5076b8ea1a9d9fb6d60c5b667f646c5d9a56`; parents `aca89ed…` and `494b4066…` | Adds only `docs/superpowers/plans/2026-10-29-g3-a7-s5-scoped-synthetic-tdd-plan-proposal.md`; exact reviewed plan is adopted conditionally. |

Both PRs were integrated with merge commits, without rebasing, squashing, force-pushing, or rewriting candidate history. Their merged Git blobs match their reviewed candidate documents. Between the verified starting main and the resulting main, the only added paths are the two Markdown files above. No source, test, schema, receipt, sealed record, media, Atlas, or WBS path changed.

## Evidence disposition and verification limits

PR #255 is partial diagnostic evidence, not a test or production certification. Its actual-helper run is reported as a single synthetic fixture (`n=1`); the report says pytest/consumer suites were `NOT_EXECUTED`, RSS was `NOT_OBSERVED`, shared E01/S5 admission is not implemented, and production/resource/platform guarantees remain pending. The report's own limitations and measurements are preserved unchanged.

On the exact PR heads, GitGuardian and CodeScene succeeded. All eight GitHub Actions jobs on each PR ended `FAILURE` with zero executed steps; therefore tests were **NOT_EXECUTED**, not passed. The infrastructure cause was not established and is not attributed to billing. Separate one-off documentation-only exceptions were recorded in PR #255 and PR #256 before their integration. Each exception was limited to that PR and did not waive repository rules or transfer to another change.

Local `git diff --check` passed. Gitleaks found no issue in either changed proposal document. The workspace verifier passed with one external reference-pack integrity check marked `SKIPPED / NOT_OBSERVED`; development source-authorization enforcement reported `DISABLED_BY_OWNER`. A whole-worktree Gitleaks scan produced eight generic-key heuristic matches in files unchanged from starting `main`; those matches were outside both PR diffs and were recorded in the PR-specific exception comments. No test suite was run by this adoption task.

Independent final review #5690517974 found the plan's T2/T7c integration-order blocker closed and recommended Owner plan adoption review. That review did not itself authorize implementation; this record adopts only the plan structure described below.

## Adopted D1–D7 boundaries

The dispositions below preserve the existing D1–D7 architecture decision. This record does not broaden it.

| Decision | Adopted boundary relevant to the plan |
|---|---|
| **D1 — Shared source admission** | E01 authoritative source-native timing remeasurement and S5 structural identity verification use the same bounded, digest-verified, genuinely immutable source byte view within an operation. No unbounded fallback, partial admission, locator substitution, or mutable alias. Named-byte and persisted-artifact evidence requirements remain. |
| **D2 — Parser safety** | Narrow exception in principle for `_parse_stts`, `_parse_ctts`, `parse_iso_bmff_timing_bytes`, and directly required budget plumbing. Preflight before sample allocation; one source-wide cumulative budget; no `ctts` double-count; accepted PTS/timebase values unchanged. No numeric production ceiling or code-write grant is adopted here. |
| **D3 — E01 authority** | Preserve every authoritative condition of public `is_binding_eligible`; no structural-only eligibility, caller timing arrays as proof, self-declared digest, unresolved persisted artifact, or guessed locator. T3 remains blocked if a finite budget cannot reach the existing public E01 path without a separate contract decision. |
| **D4 — Historical records** | Separate structural integrity, external E01/snapshot revalidation, fresh S5 admission, and consumer permission. Structurally valid V1/V2/V3 records with unavailable dependencies may load unverified; malformed or tampered records reject. Sealed bytes, schemas, digests, receipts and `current_e01_validated` semantics remain unchanged. |
| **D5 — Admission security** | Adopt bounded descriptor-based fail-closed admission as a principle. Unsupported path/symlink semantics refuse; no weaker fallback. No operating system is approved for production. An admitted buffer proves only bytes consumed in that operation, not future path identity. |
| **D6 — Consumer checks** | Fresh S5 admission is required at HumanDecision create/resume, real-plan single/multi-selection and lineage, and local preview. No cached, serialized, inherited, or stale S5 boolean grants authority. A later native renderer path reopen is a separate identity boundary. |
| **D7 — Budgets** | `PRODUCTION_RESOURCE_BUDGET=PENDING_EVIDENCE`. No unlimited admission and no production limit/platform adoption. |

A-12/P-11 remains controlling: S5 may inspect only the approved ISO-BMFF structural identity metadata. No extra FFmpeg/FFprobe call, S5 timing-table parse, new PTS/timebase calculation, edit boundary, serialized evidence field, receipt/schema change, or evidence-strength promotion is authorized. `PRODUCER_SEALED` is not independent source/probe proof; `demuxer_build_state=NOT_OBSERVED` remains unchanged.

## Adopted T1–T8 conditional execution structure

The exact plan at `494b4066caa950e4ae28c780a531299ce9acdcf0` defines the candidate functions, RED/GREEN predicates, regression commands, and ownership boundaries. Its dependency order is adopted as follows:

1. T0 exact-base, environment, and authority preflight precedes implementation work.
2. T1 may be separately authorized and accepted independently on exactly `src/vip_fvs/bounded_admission.py` and `tests/vip_fvs/unit/test_bounded_admission.py`; unsupported trusted-root/no-follow capability fails closed.
3. T2 candidate development is not independently promotable. T3 and T4 require the T1/T2 candidates; T5 requires T1/T2 and T3. One atomic T2–T5 integration barrier must include every finite-budget parser caller and refusal path before T6.
4. The one callsite-only parser-signature compatibility edit in `tests/vip_fvs/integration/test_local_preview_real_tools_generated.py` belongs to the T2 owner under an exact future path grant. T7c does not own it. That native-tools file remains excluded from all executable test commands.
5. T6 begins only from the accepted T1–T5 composite; T7a, T7b, and T7c follow accepted T6; T8 follows T7a–T7c integration.

### Test-only resource profile

The following are accepted only as finite synthetic test parameters from the adopted plan. They are not production defaults, maxima, or capacity evidence:

| Parameter | Test-only value |
|---|---:|
| Reader unit source cap | 4 KiB |
| Integrated synthetic source cap | 8 MiB |
| Timing sample cap | 20,000; 20,001 refuses before expansion |
| Probe JSON cap | 1 MiB |
| Refinement JSON cap | 1 MiB |
| ReviewBundle JSON cap | 512 KiB |
| Snapshot manifest JSON cap | 64 KiB |
| Probe rows | 64 |
| JSON nesting depth | 64 |
| Read chunk | 64 KiB |
| Child-process RSS guard | 256 MiB only when enforceable; otherwise RSS is `NOT_OBSERVED` and fixtures do not grow |

Previously reported candidates of 256 MiB source, 250,000 samples, 16 MiB probe/refinement JSON, 8 MiB ReviewBundle, 4,096 rows, depth 64, and 512 MiB process peak remain diagnostic candidates only. In particular, no combined 512 MiB upper-bound claim is adopted. If a finite production policy cannot be justified, production admission remains blocked rather than unlimited.

## Implementation and production authority

**No T1–T8 implementation is authorized by this adoption.** Each slice requires its own exact Owner grant. The first possible grant may cover only the two T1 paths above and synthetic fixtures/commands explicitly named in that grant. It must preserve trusted-root capability checks, descriptor-relative no-follow traversal, finite reads, immutable returned bytes, exact-buffer SHA-256 verification, and fail-closed behavior.

T2 remains `T2_BLOCKED_PENDING_EXACT_D2_GRANT_AND_ATOMIC_CALLER_CLOSURE`; before any parser/caller write, the grant must enumerate the entire T2 path set, include the native-test callsite-only edit, close all parser callers, specify refusal mapping, and define the atomic T2–T5 promotion head. T3 remains blocked if the unchanged public E01 predicate cannot receive a finite budget without an implicit production default, skipped remeasurement, weakened eligibility, or an unapproved public API change; seek a separate contract-owner ruling in that case.

This record authorizes no authentic/protected media, FFmpeg/FFprobe, provider/model activity, rendering/export, production resource or platform adoption, or Gate promotion.

## State maintenance

Under `docs/project/STATE_MAINTENANCE_PROTOCOL.md`, adoption materially changes the immediate next action and therefore triggers a global current-state refresh. This Goal does not authorize editing global handoff files. The separate reconciliation task should update only `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` with the verified merge SHAs, adopted conditional plan status, remaining T1/T2/T3 blockers, and the next action: request a separate exact two-file synthetic T1 grant. No `00_PROJECT_CHARTER.md` change is indicated; update `02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md` only if that reconciliation finds a material orchestration change.
