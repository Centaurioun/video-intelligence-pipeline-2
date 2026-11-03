# Root-H Mutation-Base v2 Successor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (where genuinely independent) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Actual execution remains blocked until task-specific authorization is verified.

**Goal:** Add a versioned, task-bound v2 mutation-base validator supporting pinned canonical snapshots and separately accepted dependency snapshots while preserving v1 behavior and refusing all unauthenticated/overbroad writes.

**Architecture:** Add explicit v1/v2 dispatch as a new candidate on a fresh branch from `17edacbe`. The v2 code candidate is PR #131 (`9715d57fc898ef5ad35c17d2f14e99904c5b8be4`), a **sibling** of the v1 code candidate PR #130 (`a7f7236`) — not its descendant; PR #130 code is a reference baseline, not the v2 ancestor. Authenticate observation and, when selected, dependency-acceptance records by immutable Git blob identities from the fixed administrative trust chain. Bind commit/tree/base/branch/writer/exact paths and enforce fail-closed mutation checks without weakening source-presence or historical source classifications.

**Tech Stack:** existing Bash with embedded Python 3 stdlib in `scripts/verify-workspace.sh`, Git object plumbing (including NUL-delimited changed-path inventory), JSON Schema authority records, existing Python `pytest` tests and isolated synthetic Git fixtures.

**Spec:** `docs/research/2026-10-23/boost-convergence/ROOT_H_V2_MUTATION_BASE_SUCCESSOR_DESIGN_PROPOSAL.md`; Owner approval `docs/research/2026-10-23/boost-convergence/OWNER_ROOT_H_V2_DESIGN_APPROVAL.md`; frozen Root-H design `docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md`.

## Global Constraints

- **Design approved; source/admin execution grant NOT established by this document.** Independently acquire current-write authorization for the *actual successor root/goal/writer/branch/base*, with exact owned paths, before any governed file edits.
- Use a new, clean, isolated **non-main** branch. Do not reuse PR #130's exclusive writer identity or broaden its prior two-path grant. Preserve dirty owner worktrees, Gate3 patch, B17 local candidate and G2 admin snapshot.
- Verify canonical `main`, bootstrap trust, PR #130 and PR #128 heads just before implementation; starting observed values on 2026-10-23 were `main=17edacbe64983ae284f09a8386377200bf538ec3`, trust `68d72be4375608952c3a4e0da16ab27a73053b2c`, PR #130 `a7f7236705835a0477cc03c355ba5f839c23be57`, PR #128 `152a89bc2b3f11b5d0350c42dffee5e2795f6d3c`. These are not perpetual authority. The v2 code candidate PR #131 head is `9715d57fc898ef5ad35c17d2f14e99904c5b8be4`; it is a sibling branch from `17edacbe`, not a descendant of PR #130.
- **Code writer owns only** `scripts/verify-workspace.sh` and `tests/scripts/test_verify_workspace_source_authorization.py`. Administrative schema and ledger writes belong to a **separate, serialized Portfolio Admin** lane. Never give both lanes simultaneous ownership of a shared path.
- **The v2-generation administrative surface is already published** in the administrative trust tree (observed at `ae048af`/`621385b4`; absent at `68d72be`): `root-h-mutation-task-packet.v2.schema.json`, `root-h-mutation-base-observation.v1.schema.json`, `root-h-accepted-mutation-base.v1.schema.json`, `root-h-accepted-mutation-base.v2.schema.json`, `root-h-owner-decision-witness.v1.schema.json`, `root-h-owner-decision-witness-registry.v1.schema.json`, plus the published witness registry and the `root-h-mutation-base-v2-trust-index.v1` block in `manifest.json`. Task 0/Task 1 must **preflight and verify** these records and adopt the published schema path; do **not** instruct Admin to "create" them. If a genuinely new companion schema is required, propose an exact path in the same authority-schemas directory for admin approval before writing; never invent a writable trust path.
- Freeze v1 files, schemas and evidence. Existing `schema_version=execution-root-task-packet.v1` continues to describe the outer packet; `mutation_base_schema=root-h-mutation-base.v2` dispatches v2. No v1 mutation of `selected_at`, historical records or legacy packets.
- For all task source writes, only exact prospective `src/` paths are eligible. The already-approved changed-source mutation inventory must include staged/unstaged/committed/untracked/ignored paths byte-safely. A passing `src/` gate does not authorize `scripts/`, `tests/`, `schemas/`, or `.orchestration/` writes.
- A referenced PR, GitHub CI check, review, Gate status or `dependency_authorized` cannot independently assert `ACCEPTED_AS_MUTATION_BASE`. Such acceptance must have an explicit, validated issuer/provenance/trust decision; **do not manufacture** one to make a positive integration test pass.
- Freshly reproduce RED before production modifications; independent review before non-main publication; verification-before-completion for claims.
- Never force-push, hard-reset, git-clean, prune refs/worktrees, delete preservation material, modify canonical `main`, or run protected media/models/provider/cloud tasks.

## Normalization note (2026-10-24)

- **Lineage (R2 F4):** PR #130 (`a7f7236`), PR #131 (`9715d57`), and PR #132 (`0edb12a`) are sibling branches from `17edacbe`. The v2 implementation candidate is PR #131; certification or tests of PR #130 do not transfer to #131, and neither transfers to #132.
- **Admin surface (R2 F5):** the v2 task-packet/observation/acceptance/witness schemas and the `root-h-mutation-base-v2-trust-index.v1` block are already published in the trust tree. They must be preflighted and verified, not created. The trust index currently contains only `CANONICAL_REF_SNAPSHOT` observations, `accepted_mutation_bases: []`, and `no_real_dependency_acceptance_issued: true`.
- **Grants (R2 F2):** the prospective exact-path grant `root-h-mutation-base-v2-authorized-20261023` (branch `execution/root-h-mutation-base-v2-20261023-authorized-v1`, writer thread `01a162d8-71dc-7af3-ad77-2cde09ca3e13`, recorded 2026-10-23) covers the two verifier paths and 11 exact administrative/schema paths. It is root/branch/base/writer/date-bound, authorizes no additional writer or path, and authorizes no dependency acceptance.
- **Trust identity (R2 F3):** `68d72be` above is a point-in-time target; the bootstrap branch later advanced through `ae048af` to `621385b4`. Reverify the fixed ref before use.

## Review Focus — Five adversarial inputs

1. **Moved remote ref with pinned immutable old commit:** must NOT change the selected base or revoke it without a separately authorized revocation rule (Task 2).
2. **Forged acceptance record / reviewed-but-unaccepted PR:** must be refused even when candidate SHA exists and dependency source presence is authorized (Task 3).
3. **Legacy and malformed v1/v2 packet mix:** v1 must retain exact prior semantics; old packets must not be silently promoted (Task 1).
4. **Mismatch between observation, packet, slot, writer, commit/tree and exact paths:** must fail closed; ambiguous or nonancestor bases cannot be re-selected by HEAD (Tasks 2, 4).
5. **Ignored, untracked, hostile or deleted `src/` file with apparently valid v2 grant:** must remain subject to the existing presence and changed-path guards (Task 4).

---

### Task 0 — Authority, candidate lineage, and schema-ownership preflight (READ-ONLY)

**Files:** Read `AGENTS.md`; four `docs/project/` bootstrap files; frozen Root-H spec; v2 design and Owner approval; the two code/test paths in PR #130 and #128; current bootstrap manifest/task packets and exact administrative writer ledger. No persistent file edits.

**Interfaces:**
- Consumes: main/bootstrap/PR head SHAs, existing exact packet/witness/transfer policy and Portfolio Admin ownership.
- Produces: authoritative chosen `IMPLEMENTATION_BASE_SHA`, `MUTATION_BASE_SHA`, root/goal/writer/branch, two-file code owner, admin schema/record path proposal and positive source-write receipts.

- [ ] Re-fetch refs and compare candidate/source and test blobs. **Do not automatically merge PR #130 or #128 or lose `dependency_authorized` and dynamic ordinal tests.**
- [ ] Identify a single safe implementation lineage authorized to carry the new v2 verifier without importing PR #128's still-blocked Gate2 schema/runtime files.
- [ ] Trace current admin scope for new schema file and future immutable observation/acceptance record paths; propose exact closed schemas/issuers if existing trust protocol lacks a typed acceptance assertion.
- [ ] Independently prove prospective writer authorization for BOTH code/test paths and an uncontested isolated worktree. Only separately authorized serialized admin writes may create/activate schema/trust records.
- [ ] Resolve whether pre-v2 current-write admission suffices to implement verifier changes on the authorized successor. A v2 packet cannot be presumed operational before its validator exists.
- [ ] **STOP at `BLOCKED_BY_AUTHORITY`** if no legitimate grant or base/ownership/issuer definition exists; write a minimal grant/issuer request, not an unauthorized patch.

### Task 1 — Closed v2 dispatch with v1 preservation

**Files:**
- Modify: `tests/scripts/test_verify_workspace_source_authorization.py`
- Modify: `scripts/verify-workspace.sh`
- Admin scope (serialized, separately granted): verify and adopt the already-published `.orchestration/portfolios/execution-portfolio-20260924-v1/authority/schemas/root-h-mutation-task-packet.v2.schema.json` and its companion schemas in the current trust tree; create them only if verification shows they are absent, under a separate exact admin grant.

**Interfaces:**
- Consumes: existing `_validate_mutation_packet(manifest, root_id, admin_commit, branch)`, validated root/slot/packet.
- Produces: explicit version dispatch and closed v2 validation without changing the existing v1 result.

- [ ] RED: write `test_mutation_v2_explicit_dispatch_denies_unknown_or_legacy_upgrade`, asserting unknown schema version and legacy packet without a supported mutation schema fail while an authentic v1 fixture maintains its expected v1 decision.
- [ ] Run `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/scripts/test_verify_workspace_source_authorization.py -k mutation_v2_explicit_dispatch`; require behavioral RED, not import/fixture error.
- [ ] Admin owner preflights and verifies the already-published closed v2 schema and related records through an authorized, non-stale, auditable administrative process; only if verification shows them absent may the admin lane create them under a separate exact grant. Verifier code/test writer must not forge trust records. Synthetic isolated fixtures may use synthetic records for TDD; never represent them as active trust.
- [ ] Implement minimal explicit v1/v2 branch around mutation-packet validation. Retain `schema_version=execution-root-task-packet.v1`, require `mutation_base_schema=root-h-mutation-base.v2` and trusted v2 schema path; unknown versions DENY.
- [ ] Re-run focused test GREEN and baseline v1 mutation tests; independently review the version compatibility diff and preserve the existing trusted source-presence output.

### Task 2 — Canonical immutable observation binding

**Files:** Same exact code/test paths. Additional trusted observation records only by admin owner and only at approved exact names.

**Interfaces:**
- Consumes: v2 closed task packet and `CANONICAL_REF_SNAPSHOT` observation ID/path/blob/issuer/ref/commit/tree, fixed bootstrap trust commit and current task identity.
- Produces: an authenticated immutable selected base or a specific `Deny`.

- [ ] RED: `test_mutation_v2_canonical_observation_and_moved_ref`, asserting known approved pinned commit/tree succeeds even after synthetic source ref moves; missing/mismatched observation blob/tree/issuer/base/ancestry and wrong task identity all fail.
- [ ] Run `python3 -m pytest -q -p no:cacheprovider tests/scripts/test_verify_workspace_source_authorization.py -k mutation_v2_canonical`; record initial RED.
- [ ] Implement bounded helper(s) near existing `_validate_mutation_packet` for loading pinned observation bytes from the validated admin commit and binding `mutation_base_sha`, `implementation_base_sha`, slot/packet fields and writer; `observed_at` is audit context, never a constant `2026-10-23` authorization test.
- [ ] Reject noncommit Git objects, tree disagreement, non-ancestor base, untrusted observation path/blob and empty/unverified issuer.
- [ ] Re-run focused GREEN and v1 suite; commit exact authorized implementation changes after review.

### Task 3 — Accepted dependency base with independent acceptance proof

**Files:** Same code/test paths; prospective trusted acceptance record syntax only via separately authorized admin schema/record lane.

**Interfaces:**
- Consumes: v2 `ACCEPTED_DEPENDENCY_SNAPSHOT` observation and a separately authenticated `ACCEPTED_AS_MUTATION_BASE` record with dependency candidate/tree, issuer, decision reference, consumer scope, and status.
- Produces: accepted pinned dependency base or `Deny`.

- [ ] RED: `test_mutation_v2_dependency_rejects_pr_review_without_base_acceptance`; GitHub PR open/mergeable/CI or `dependency_authorized` alone must fail. Also test acceptance blob spoofing, wrong dependency candidate/tree, wrong consumer/scope, revocation/conflicting authority and non-ancestor candidate.
- [ ] Run focused `pytest ... -k mutation_v2_dependency`; require behavioral RED.
- [ ] Implement a separate authenticated acceptance-record predicate, never a reuse of the unrelated source-presence `dependency_authorized` result. Ensure true positive in a **synthetic trusted fixture** proves parser logic only; it does NOT create a real-world accepted dependency.
- [ ] Exact issuer and revocation semantics must come from a reviewed/admin-approved contract. If current authority has no supported `ACCEPTED_AS_MUTATION_BASE` record, STOP this subtask at a draft contract and request Owner authority for that record mechanism rather than adding unauthenticated trust.
- [ ] Run focused GREEN where supported and all rejection cases; report `ACCEPTED_DEPENDENCY_SNAPSHOT` as unavailable for real tasks until a legitimate acceptance record exists.

### Task 4 — End-to-end path and historical migration protections

**Files:** Same code/test paths.

**Interfaces:**
- Consumes: selected v2 base, already-present `_source_mutation_inventory`, `current_authorized`, existing `SOURCE-AUTH` classification and task packet exact paths/transfers.
- Produces: independent `SOURCE-MUTATION-AUTH` PASS/FAIL and deterministic, fail-closed diagnostics.

- [ ] RED: `test_mutation_v2_exact_paths_and_legacy_nonmigration`, covering packet/slot mismatch, wrong branch/root/goal/assigned writer, wildcard/extra paths, transfer denial, historical-only path, ignored/untracked path, renamed/deleted source, hostile filename and Git error.
- [ ] Run focused `pytest ... -k mutation_v2_exact_paths`; require behavioral RED.
- [ ] Bind selected base to actual committed/staged/unstaged/untracked/ignored changed `src/` paths, preserving NUL-safe existing logic and denial of invalid authority. Do not create `src/**` grants or weaken `SOURCE-AUTH`.
- [ ] Verify 19 legacy current-write entries are not bulk-migrated, and that a genuinely resumed legacy task requires a new root/goal/branch/writer/observation/exact permission and transfer if needed.
- [ ] Run GREEN + full Root-H tests; peer review exact task-scoped changed paths.

### Task 5 — Certification and non-main publication

**Files:** Code/test writer diff must remain exactly the two authorized paths. Administrative schema/record changes are separately committed by the serialized admin owner with their own exact grants and SHA ledger.

**Interfaces:**
- Consumes: complete v1/v2 suites and immutable source/admin candidate receipt.
- Produces: CP3 candidate only if scope, tests, review and independent remote readback succeed.

- [ ] Execute `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/scripts/test_verify_workspace_source_authorization.py`, `bash -n scripts/verify-workspace.sh`, `git diff --check`; report exact pass/fail counts and exit codes.
- [ ] Run `bash scripts/verify-workspace.sh` and preserve its actual exit 1 and environment failures if they occur. Scoped Root-H success is NOT overall workspace PASS.
- [ ] Verify source/admission and non-`src/` write owners independently; no claim that source-only mutation gate authorizes administrative or test changes.
- [ ] Independent code/security review against immutable base/head and Owner-approved v2 spec. Apply legitimate blocking feedback only by authorized TDD; do not silently change v1 semantics.
- [ ] Commit and push only an authorized non-main candidate, without force, and re-fetch exact commit/tree and two-file diff. Do not merge PR #130 or #128; do not promote Gates.
- [ ] If no authorized acceptance-record issuer exists, record `V2_CANONICAL_IMPLEMENTED_DEPENDENCY_BLOCKED` (if accurately supported), not a false `V2_FULLY_READY`. Otherwise report `CP3_REMOTE_PUBLISHED` with scoped limitations.

## Six-Cycle Iterative Refinement

1. Evidence accuracy: verify current immutable source/trust identity, typed records and test receipts.
2. Coverage: v1 preservation, both selected snapshot types, writer/path/issuer/revocation negatives.
3. Architecture: historical presence, mutation write grant, base acceptance and admin integrity remain separate.
4. Economy: only one verifier/test writer and serialized admin lane; no needless 19-root migration or parallel duplicate workers.
5. Reliability: adversarial fail-closed tests, no fabricated acceptance and independent GitHub readback.
6. Handoff: exact shas, CP status, residual blockers, next independently authorized canary.

**End-state:** An actionable implementation roadmap, not an assertion that this design approval alone makes any code writable.
