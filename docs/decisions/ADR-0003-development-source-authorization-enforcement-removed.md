# ADR-0003: Development Source-Authorization Enforcement Removed by Owner

## Status

Accepted by the repository Owner on 2026-10-24. Supersedes the development-time
enforcement defined by the frozen Root-H source-authorization design and plan
(`docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md`,
`docs/superpowers/plans/2026-09-25-root-h-workspace-source-authorization-implementation-plan.md`).
Those documents are preserved as historical audit records.

## Context

`scripts/verify-workspace.sh` embedded a fail-closed source-authorization
resolver. For every `src/**` path, ordinary development had to satisfy a chain
rooted at the fixed canonical administrative ref
`execution/execution-portfolio-20260924-v1/bootstrap`, including:

- a matching root slot in the administrative portfolio manifest;
- a branch/path-bound task-packet grant (`exclusive_write_paths_or_domains`);
- a positive current-write witness (Gate-0 owner authorization blob or an
  owner expansion record naming the exact root and branch).

Any missing or mismatched link emitted `SOURCE-AUTH DENY` plus
`FAIL source authorization`, and an ungranted source path emitted
`FAIL unexpected source file exists outside authorized paths`. The check failed
closed and contributed to the verifier's overall failure count.

In practice this repeatedly blocked ordinary synthetic development rather than
protecting production trust. Two concrete cases:

- **Root-H (PR #143):** the candidate itself added a further mutation gate
  (`SOURCE_MUTATION-AUTH`, `root-h-mutation-base.v2`,
  `root-h-owner-decision-witness`) that denied any source mutation without an
  exact current-root grant. The branch therefore blocked its own development
  writes.
- **Gate-3 source snapshot (PR #139):** a new
  `src/vip_fvs/source_snapshot.py` was classified `UNAUTHORIZED` and failed the
  verifier solely because no branch/path-bound grant named that branch. The only
  existing record naming the file was bound to a different branch.

Satisfying these checks required administrative grants and authority records
rather than ordinary engineering work. The repository Owner explicitly directed
that the development gate be **removed**, not temporarily satisfied through
fabricated authorization records, and accepted the resulting reduction in
protection against unauthorized repository changes.

## Decision

1. Remove development-time source-authorization enforcement from
   `scripts/verify-workspace.sh`. The verifier no longer resolves the canonical
   administrative ref, classifies `src/**` paths, or emits
   `SOURCE-AUTH`/`SOURCE_MUTATION-AUTH` decisions for ordinary development.
2. Emit one explicit, non-blocking status line:
   `DISABLED  development source authorization: DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER`.
   The verifier defines `DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER`.
3. A removed check is reported as **DISABLED**, never as a successful
   verification. No `AUTHORIZED_CURRENT` classification, `PASS` line about
   source authorization, Owner Witness, or fabricated grant may be emitted.
4. Missing branch/path-bound grants, a missing administrative bootstrap ref, and
   ungranted new source paths (for example `src/vip_fvs/source_snapshot.py` or
   Root-H-shaped verifier/test changes) must not block ordinary development.
5. Do not introduce replacement administrative grants, task packets, signing
   ceremonies, or equivalent blockers under another name. The removal is a
   deliberate policy change, not a migration to a new gate.
6. Remove the obsolete development-only authorization tests and replace them
   with tests that assert the DISABLED behavior, the absence of fabricated
   success, continued unrelated safety checks, and a static guard against
   reintroducing the enforcement machinery.

## Scope: removed

- Development enforcement of `ROOT_H_DEVELOPMENT_AUTHORIZATION`,
  `ROOT_H_SOURCE_AUTH`, and `PR139_SOURCE_AUTH`.
- Branch/path-bound `SOURCE-AUTH` grant requirements for ordinary development.
- Owner Witness requirements for ordinary development writes.
- Canonical administrative bootstrap-ref resolution and authority-lineage
  validation inside `scripts/verify-workspace.sh`.
- The associated fail-closed development blocking logic, including the
  mutation-authorization variant proposed by PR #143.
- Obsolete development-only authorization tests.

## Scope: preserved

This decision removes **development authorization enforcement only**. It does not
alter protections for:

- immutable source media;
- source-native PTS/timebase correctness;
- evidence integrity and provenance;
- credentials and secrets (the high-confidence secret scan and tracked-`.env`
  check remain);
- real provider/model execution controls;
- protected/archive access;
- production Owner trust activation;
- canonical-main merge authorization.

It creates no production Owner Witness, no accepted-dependency admission, and no
authorization success for any of those separately controlled activities.

## Consequences

- **Trade-off accepted by the Owner:** repository writers can add or modify
  `src/**` paths without a branch/path-bound administrative grant. Protection
  against unauthorized repository changes is reduced to ordinary review, the
  pull-request workflow, and the remaining verifier checks (secret scan, required
  paths, media/prototype boundaries, and canonical-main merge authorization).
- Ordinary Root-H and Gate-3 development no longer needs to modify the
  administrative bootstrap ref or fabricate grants, so the work can proceed
  through the normal branch/PR path.
- Historical design and plan documents are retained with a superseded banner;
  audit history is not deleted or rewritten.
- The verifier's output now distinguishes a removed control (DISABLED) from a
  passing control, so a future reader cannot mistake the removal for successful
  verification.
- Reintroducing equivalent enforcement is prohibited; a static regression test
  guards `scripts/` against the removed markers.

## References

- PR #143 (Root-H candidate) and PR #139 (Gate-3 source snapshot): the motivating
  development blockers.
- `docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md`
  (superseded, preserved).
- `docs/superpowers/plans/2026-09-25-root-h-workspace-source-authorization-implementation-plan.md`
  (superseded, preserved).
- `scripts/verify-workspace.sh` and
  `tests/scripts/test_verify_workspace_source_authorization.py` (implementation
  and regression contract).
