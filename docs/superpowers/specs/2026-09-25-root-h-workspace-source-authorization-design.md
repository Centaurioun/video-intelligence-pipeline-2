# Root H — Workspace Source Authorization — Frozen Design Spec

> **SUPERSEDED — 2026-10-24 Owner decision.** Development-time source-authorization
> enforcement was removed by explicit Owner decision; see
> [ADR-0003](../../decisions/ADR-0003-development-source-authorization-enforcement-removed.md).
> `scripts/verify-workspace.sh` now reports
> `DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER` and applies no
> branch/path-grant, canonical-admin-ref, or Owner Witness requirement to ordinary
> development. This document is preserved unchanged below as historical audit
> evidence of the superseded design and does not govern current behavior.

**Status:** SUPERSEDED BY ADR-0003 (original status: OWNER-APPROVED DESIGN — FROZEN SPEC, AWAITING OWNER/COORDINATOR SPEC REVIEW)
**Date:** 2026-09-25
**Root:** `root-workspace-verifier-authorization`
**Goal:** `goal-20260925-workspace-verifier-authorization`
**Branch:** `execution/execution-portfolio-20260924-v1/workspace-verifier-authorization`
**Owner approval source:** explicit owner approval of the corrected Root-H V2 design, delivered directly to the Root-H design session (this prompt).
**Scope:** the source-authorization boundary check inside `scripts/verify-workspace.sh` only.

This spec freezes an owner-approved design. It authorizes no implementation. It is
not an implementation plan. Product code, test creation, and every write listed in
§13 remain separately unauthorized.

## 1. Problem

`scripts/verify-workspace.sh` enforces a source boundary with a hard-coded,
Gate-0-only allowlist whose effective logic is:

- allow `src/README.md`;
- allow `src/gate0/**`;
- reject every other `src/**` path.

That allowlist was written on 2026-09-12 (commit `496551c0`) when only `src/README.md`
and `src/gate0/**` existed. `src/gate3/**` (32 files) and `src/vip_fvs/**` (20 files)
entered `main` ten days later at commit `4c4d224a` (2026-09-22) and were never
reconciled with the check.

The check is also structurally weak independent of the stale content:

1. it derives authorization from a literal string list rather than from repository
   authority, so it cannot track legitimate authority change without a source edit;
2. it uses first-match discovery (`find … -print -quit`), so it reports at most one
   violating path and its output depends on filesystem enumeration order;
3. it treats "path exists" as the input to the decision without ever asking whether a
   path is authorized to be present.

The design objective is **not** to make the script exit zero. The objective is to make
the source-boundary check derive from real repository authority while remaining
fail-closed. Unrelated failing checks are expected to remain failing and independently
observable.

## 2. Authority and non-authority

### 2.1 Authority consumed

This design consumes only existing, owner-authorized portfolio authority reachable
from the bootstrap/admin branch:

| Artifact | Role |
| --- | --- |
| `.orchestration/portfolios/execution-portfolio-20260924-v1/manifest.json` | anchor manifest; discovery entry point |
| `authority/source-presence-and-g-test-ownership-normalization-20260925-v1.json` | base normalization: the two predicates, frozen baseline, post-baseline sources |
| `authority/root-g-test-path-scope-amendment-20260925-v1.json` | ordinal-1 amendment (test-scope only; adds no `src/` authority) |
| `authority/root-h-test-path-allocation-20260925-v1.json` | ordinal-2 amendment: exact future test-path allocation |
| `authority/root-expansion-authorization-20260924-v1.json`, `…-20260925-v2.json` | per-root expansion authority referenced by the manifest |
| per-root task packets under `goals/**` | recorded write domains and current-write authority refs |

### 2.2 Explicit non-authority

None of the following is authority, alone or in combination:

- the existence of a path in the worktree;
- the existence of a directory;
- the existence of a branch or worktree;
- a path being tracked in the index;
- a branch advancing beyond a recorded head;
- a commit message or a controller/agent report;
- a reservation, an exact-path sibling allocation, or a test-path allocation;
- a broad write domain or glob, without exact recorded membership;
- the verifier's own output, a prior run, or this spec;
- the local admin ref's equality with its remote counterpart.

A reservation, an allocation, and a historical-presence finding are all distinct from
write authority. A reservation or allocation constrains sibling ownership only.

## 3. Current repository anchors

Verified at the time this spec was written. These are observations, not authority; the
verifier must resolve its own anchors at runtime and report them (§6.2, §11).

| Anchor | Value |
| --- | --- |
| canonical `main` | `d3b477db97541d7cd2775e7c42381eb4875de519` |
| Root-H branch head | `d3b477db97541d7cd2775e7c42381eb4875de519` |
| bootstrap/admin head | `41b5db6e677787ec88e0355dd70ea8fff10177db` |
| `scripts/verify-workspace.sh` blob (main, Root H, admin) | `7b681fd60408b39b48f15f148e4247a142865b20` |
| base normalization record blob | `166667bb224b46a7f97c51304bb1723424b896dd` |
| ordinal-1 amendment blob | `6e214c304d68eb1a6ce22a0907a3bfa62efbaee3` |
| ordinal-2 Root-H allocation blob | `2359336adb2e4b0f434a206edc16bcfd1897595f` |
| Root-H task packet blob | `eca71aaf386be165f0ead53b855eb45d681e37fb` |
| frozen source baseline subtree SHA | `581fea73d4fc772e2f3a11d5e450951cbe2793ed` |
| frozen baseline path count | 88 |

The Root-H branch deliberately contains no portfolio metadata; authority is read
through the resolved admin ref, never from branch-local files.

## 4. The two predicates

The design models two independent questions. They must never be collapsed into one
boolean, and historical presence never implies current write authority.

### 4.1 `HISTORICAL_SOURCE_PRESENCE_AUTHORIZED`

> Is this already-tracked source path legitimately present because higher authority
> admits it — either as an exact member of an owner-admitted frozen source tree, or as
> an exact recorded post-baseline root output?

Historical presence is positive provenance. It grants no write permission.

### 4.2 `CURRENT_IMPLEMENTATION_WRITE_AUTHORIZED`

> Is this root currently allowed to create or modify this source path?

Current write authority requires a positive *current* authorization chain naming that
root and that path or domain. An explicit current `implementation_authorized=false` is
a hard denial.

### 4.3 Non-implication

```
HISTORICAL_SOURCE_PRESENCE_AUTHORIZED  =/=>  CURRENT_IMPLEMENTATION_WRITE_AUTHORIZED
CURRENT_IMPLEMENTATION_WRITE_AUTHORIZED =/=>  historical presence
RESERVED | ALLOCATED                   =/=>  either predicate
```

An accepted terminal root's frozen historical output does not imply that root may
continue writing. A historically present path is not automatically valid for a new
root to modify.

## 5. Frozen source baseline semantics

The historical baseline is exact membership in the owner-authorized frozen `src` Git
tree:

- baseline commit `d3b477db97541d7cd2775e7c42381eb4875de519`;
- subtree path `src`;
- subtree tree SHA `581fea73d4fc772e2f3a11d5e450951cbe2793ed`;
- declared path count 88;
- declared tree-relative listing digest
  `e6e213937c39889cf0e3771f368d9c95f0edaadd8605075cae4f1d1db95f97b1`;
- declared repo-relative listing digest
  `edab64739b2c5fd3f907a6407976c802a9b486c2453a67f086931999b89d0162`.

The subtree object is self-verifying: it resolves and reproduces its listing without
requiring the anchor commit object. Resolving by subtree SHA is the preferred offline
mechanism; the anchor commit is a cross-check.

A candidate path is a baseline member iff its normalized repo-relative form is an
**exact string member** of that listing.

### 5.1 Forbidden inference

Baseline membership must never be inferred from:

- `src/**`, or any wildcard, prefix, or directory grant;
- current worktree or branch existence;
- directory existence;
- tracked status alone;
- the fact that `main` contains the path.

### 5.2 Baseline validation is mandatory

Before any membership decision, the implementation must confirm the resolved listing
matches the declared path count **and** both declared listing digests. Any mismatch is
a denial (§11). `membership_semantics` must be
`EXACT_PATH_MEMBERSHIP_IN_FROZEN_GIT_TREE` and `wildcard_future_grant` must be
`false`; otherwise deny. This is the guard that prevents the baseline degrading into
`src/**`.

## 6. Post-baseline historical source presence

For a path outside the frozen baseline, historical presence requires **all** of:

1. the path is **tracked** in the index;
2. the path is an **exact string member** of the relevant source's owner-recorded
   `observed_src_paths_beyond_baseline`;
3. that source carries a positive `recorded_write_domain_citation`;
4. the citation's `blob_sha` resolves to that exact Git blob locally;
5. the citation's `json_pointer` resolves to exactly `values_verbatim`;
6. the exact path lies inside that positively cited domain.

Any step failing denies historical presence.

### 6.1 Domain-only matching is forbidden

Matching a broad recorded domain alone is never sufficient. A newly staged path inside
an old broad domain (for example a new file under a recorded `src/gate1/**` domain)
remains unauthorized unless owner authority explicitly records that exact path.

### 6.2 Cited artifacts are consumed by identity, not by path

When a citation names both a `blob_sha` and a branch-relative `path`, resolution must
use the **exact cited blob SHA**. A branch-relative read is not sufficient and is not
equivalent: the cited object may remain resolvable by SHA while the path at a mutable
ref has advanced, and the admin branch is known to lack some paths that remain
resolvable by SHA.

### 6.3 Future historical-source extension

The implementation supports only authority semantics actually defined by supported
authority records. It must not invent, infer, or interpret a new
historical-source-extension field inside `portfolio-authority-normalization-amendment.v1`.

A future owner-authorized expansion of historical source presence is consumable
**without a product-source edit** when the admin manifest points to a new valid base
normalization record that uses an already-supported normalization schema with exact
preimages.

Any of the following is a **reconsideration trigger** and must fail closed until
explicitly owner-supported:

- a new or changed authority schema version;
- a novel amendment-carried historical-source extension shape;
- an unsupported authority record type.

This resolves the V2 open problems concerning future amendment-carried source-history
semantics: they are reconsideration triggers, not implementation requirements, and
Root H may not manufacture future authority semantics.

## 7. Dynamic digest enforcement

Two different things must not be confused:

- **Forbidden:** embedding a frozen digest of the whole mutable owner-state snapshot
  into product source, such that a legitimate owner amendment forces a source edit.
- **Required:** enforcing every digest and identity declared by the authority artifacts
  that are consumed at runtime.

### 7.1 Runtime enforcement anchors

The implementation must enforce, and deny on any mismatch, absence, or inconsistency:

1. manifest base-normalization `record_blob_sha` equals the actual blob at its declared
   `record_path` under the resolved admin commit;
2. every manifest-listed amendment `record_blob_sha` equals its actual amendment blob;
3. every amendment's `amends_record_blob_sha` equals the base record blob it claims to
   amend;
4. every cited `recorded_write_domain_citation.blob_sha` resolves as that exact blob;
5. every cited `json_pointer` resolves to exactly `values_verbatim`;
6. the frozen subtree identity, path count, and both listing digests match the record.

These anchors are supplied by owner data at runtime. They are not an embedded
allowlist, and they are not optional provenance cross-checks.

### 7.2 Consequence for amendments

Because the verifier re-reads manifest and record state from the canonical admin ref,
a legitimate owner amendment is consumable with **no source-code change**. Only the
canonical ref name and the supported schema/record-type identities are fixed in source;
mutable owner state is always read.

## 8. Operational authority trust root

Normal verifier execution resolves exactly one local Git ref:

```
execution/execution-portfolio-20260924-v1/bootstrap
```

### 8.1 Frozen trust root

The canonical ref name is a stable trust-anchor/parser constant inside the verifier.
The authority record path is read from the manifest, not hard-coded.

No public, argument, or environment-selectable override is permitted, including:

- `--authority-ref`;
- a root-id override;
- a manifest override;
- an authority-file or authority-record override;
- an external freshness-evidence input.

A caller-selectable authority ref would let a locally forged ref carrying a permissive
fake normalization become the verifier's trust root. That attack surface must not exist.

### 8.2 Failure and reporting

- If the canonical admin ref is absent or unresolvable locally, the source-boundary
  check fails closed.
- The exact locally resolved admin commit SHA is always reported.
- The verifier performs no network access. Its existing `gh`/network check is left
  byte-unchanged.

### 8.3 Test seam

Alternate refs may be exercised only through an internal test seam that normal CLI
execution cannot select. The operational entry point must expose no such switch, and
the seam must be demonstrably unreachable from both arguments and environment. This is
an implementation and test requirement, not a design blocker.

## 9. Current root identity

Current write authorization is root-relative, so root identity must be derived without
caller injection.

### 9.1 Derivation

1. Determine the actual checked-out branch with Git.
2. Match that branch **exactly** against root entries in the resolved owner/admin
   portfolio metadata.
3. Exactly one match yields `CURRENT_ROOT_IDENTITY=RESOLVED(<root_id>)`.
4. Zero matches yield `NOT_OBSERVED`.
5. Multiple matches yield `AMBIGUOUS`.

### 9.2 Consequences

- `NOT_OBSERVED` and `AMBIGUOUS` must not produce `AUTHORIZED_CURRENT`.
- Canonical `main` has no active execution-root identity, so it never yields
  `AUTHORIZED_CURRENT`.
- No CLI flag and no environment variable may inject or override root identity.
- Even a resolved root must additionally satisfy a positive current owner/task-packet
  authorization chain for that root and that exact path. Historical presence cannot
  substitute.
- The existing branch-is-`main` check remains an independent verifier failure. It must
  not be weakened, and it must not be repurposed as the root-identity mechanism.

## 10. Complete deterministic enumeration

First-hit discovery is replaced by complete source discovery.

Requirements:

1. enumerate every relevant **tracked** source path under `src`;
2. enumerate every relevant **untracked** source path under `src` (non-ignored);
3. normalize repo-relative form and order deterministically;
4. no silent truncation and no first-match early exit;
5. NUL-delimited Git and shell handling;
6. filenames containing spaces, newlines, glob metacharacters, or leading dashes must
   not bypass classification through word splitting or glob expansion;
7. the whole `src` tree must never be authorized wholesale.

Tracked and untracked enumeration are complementary and both are required: an
untracked-only scan misses tracked paths, and a tracked-only scan can be bypassed by a
path that is present but not yet tracked. A path deleted from the worktree but still in
the index is still tracked and is still evaluated.

## 11. Result vocabulary and fail-closed taxonomy

### 11.1 Per-path states

| State | Meaning |
| --- | --- |
| `AUTHORIZED_HISTORICAL` | informational admitted provenance; grants no write |
| `AUTHORIZED_CURRENT` | informational current positive write authority |
| `UNAUTHORIZED` | failure-producing |

### 11.2 Overall result

Overall result is only `PASS` or `FAIL`. There is no third overall success state.
`UNAUTHORIZED` contributes to `FAIL`. `AUTHORIZED_HISTORICAL` does not by itself alter
the aggregate verdict.

These are authorization/provenance states. They are not evidence classes. The approved
assertion-level evidence classes (`MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`,
`AUDIO_OBSERVED`, `EDITORIAL_INFERENCE`) are untouched, and `NOT_OBSERVED` remains an
availability/status condition.

### 11.3 Fail-closed taxonomy

The source-boundary check must deny, never silently pass, on at least:

- canonical admin ref absent or unresolvable;
- manifest unresolvable or unparseable;
- base normalization record unresolvable or unparseable;
- authority `schema_version` or `record_type` unsupported;
- base-normalization or amendment digest mismatch;
- amendment-to-base link mismatch;
- frozen subtree unresolvable;
- frozen path count or listing digest disagreement;
- unsupported baseline membership semantics, or a wildcard future grant;
- cited preimage unresolvable;
- cited pointer/value mismatch;
- root identity `NOT_OBSERVED` or `AMBIGUOUS` where current authority would be claimed;
- any path that satisfies neither predicate.

An empty derived authority set is a failure condition, not a pass.

## 12. Remote freshness

Inside the offline verifier:

```
REMOTE_FRESHNESS=NOT_OBSERVED
```

always. A locally resolved named ref does **not** prove equality with the remote ref.
No caller-provided freshness-evidence input is accepted, and no in-script freshness
trust format is invented.

The verifier reports the exact locally resolved admin commit plus every consumed
record digest, and must never present `NOT_OBSERVED` as fresh. Establishing remote
equality or freshness is a separate owner/controller synchronization step performed
outside this verifier.

## 13. Future implementation surfaces

Exactly two paths:

| Kind | Path |
| --- | --- |
| product | `scripts/verify-workspace.sh` |
| test | `tests/scripts/test_verify_workspace_source_authorization.py` |

No other path. No README, no `src/**`, no schema, no configuration, no governance
artifact, and no other test path.

### 13.1 Allocation status

The exact future test path is allocated by the durable admin record
`.orchestration/portfolios/execution-portfolio-20260924-v1/authority/root-h-test-path-allocation-20260925-v1.json`
(blob `2359336adb2e4b0f434a206edc16bcfd1897595f`). The allocation:

- names exactly that one path;
- creates no `tests/**` glob and no directory or prefix allocation;
- transfers no other path;
- grants no current write authority;
- authorizes no file creation.

Allocation is not write authority. Implementation remains separately unauthorized
(§16).

## 14. Preservation of unrelated verifier behavior

The following checks must remain semantically unchanged. They must not be weakened,
deleted, bypassed, or reinterpreted:

- the branch-is-`main` check;
- reference-pack integrity and materialization checks;
- the prototype `.env.local` check;
- secret handling and secret scans;
- the `gh`/network/authentication check;
- required-path presence, memo counts, report-integrity hashes, specification
  lifecycle, evidence-taxonomy, sampling-arithmetic, and decision-register checks;
- any other existing independent verifier check.

If another check still fails after a future Root-H implementation, that is an
independent result. Root H's goal is to make the source-authorization check truthful
and fail-closed, not to engineer `EXIT 0`.

## 15. README disposition

README drift is real but is a separate reconciliation/ENABLE concern. Neither
`README.md` nor `src/README.md` participates in any imported source-authorization
predicate, and the only README-touching verifier check is an unrelated lifecycle
assertion. Root H receives no README write authority, and this spec authorizes no
README edit.

## 16. Non-authority of this spec

This spec:

- is not an implementation plan;
- authorizes no product code and no test creation;
- authorizes no `scripts/verify-workspace.sh` edit;
- authorizes no README, schema, configuration, or governance edit;
- authorizes no canonical-main mutation, no merge, and no Gate promotion;
- does not change Root G's or Root H's `implementation_authorized=false`.

```
ROOT_H_IMPLEMENTATION_AUTHORIZED=false
ROOT_G_IMPLEMENTATION_AUTHORIZED=false
```

No new product-side governance manifest is created or required. Authority remains in
the existing admin/portfolio lineage.

## 17. Normative adversarial contract cases

These are normative. A future implementation is not acceptable unless each case
behaves as stated.

| # | Case | Required behavior |
| --- | --- | --- |
| 1 | Exact frozen baseline path | `AUTHORIZED_HISTORICAL` |
| 2 | Merely current/tracked path absent from frozen and observed preimages | `UNAUTHORIZED` |
| 3 | Exact post-baseline observed path + valid cited preimage | `AUTHORIZED_HISTORICAL` |
| 4 | New tracked path inside an old broad domain but absent from the observed set | `UNAUTHORIZED` |
| 5 | Untracked source path under any domain | `UNAUTHORIZED` |
| 6 | Attempted forged caller authority ref | No operational surface exists; cannot influence the verifier |
| 7 | Canonical admin ref missing | DENY |
| 8 | Base-record digest mismatch | DENY |
| 9 | Amendment digest or amendment-to-base link mismatch | DENY |
| 10 | Cited pointer/value mismatch | DENY |
| 11 | Cited exact blob still valid while the branch-relative path advanced | Consume the exact cited blob |
| 12 | Unsupported schema or record type | DENY |
| 13 | Unique branch-to-root match + positive current chain | `AUTHORIZED_CURRENT` may exist |
| 14 | Zero or ambiguous root match | No current authorization |
| 15 | Canonical `main` | No active current-root identity |
| 16 | Remote freshness | `NOT_OBSERVED` |
| 17 | Two unauthorized paths | Both reported, deterministically |
| 18 | Hostile filenames (space, newline, glob, leading dash) | No bypass |
| 19 | Unrelated verifier failures | Remain independent |
| 20 | Future unsupported historical-source amendment shape | DENY until explicitly owner-supported |

## 18. Rejected alternatives

| Alternative | Rejected because |
| --- | --- |
| Keep the hard-coded Gate-0 allowlist | Cannot track authority change without a source edit; already stale |
| `src/**` wildcard authorization | Forfeits exact membership; explicitly prohibited |
| "Whatever exists on `main` is authorized" | Existence is never authority |
| Manual embedded grant table | Recreates the stale-allowlist drift this design removes |
| Current-write-only predicate | Would reject owner-integrated historical source |
| Historical-path wildcard domain matching | Turns an old broad domain into a perpetual historical grant |
| Retroactive "absent boolean means denial" | Schema evolution is not retroactive revocation |
| Caller-selectable `--authority-ref` | Makes the operational trust root caller-injectable |
| Caller/env root-id injection | Makes current authority injectable |
| In-script external freshness-evidence flag | Invents a trust input the offline verifier cannot validate |
| Pinning the whole mutable owner-state digest in source | Forces a code edit per legitimate owner amendment |
| Treating cited digests as optional provenance | Contradicts fail-closed internal consistency |
| Product-side duplicated governance manifest | Creates branch-divergent, competing authority |
| `find … -print -quit` first-hit discovery | Non-deterministic and hides all but one violation |
| Untracked-only or tracked-only enumeration | Each misses a bypass class |
| Newline-delimited shell iteration | Word-splitting and glob bypass |
| A third overall verdict | Overall result is only PASS/FAIL |

## 19. Reconsideration triggers

Reopen this design only if one of the following occurs:

1. the frozen-baseline admission mechanism is replaced by owner authority;
2. baseline membership semantics change away from exact frozen Git-tree membership;
3. a wildcard or prefix-based source grant is introduced by owner authority;
4. the base normalization record is superseded rather than amended;
5. the authority namespace moves off the bootstrap/admin branch;
6. a source subtree outside `src` becomes in-scope for this boundary;
7. an authority schema version or record type changes;
8. a novel amendment-carried historical-source extension shape appears;
9. Root H receives write authority for any path beyond the two in §13;
10. the distinction between historical presence and current write authority is
    removed from authority records.

## 20. Open problems and next safe action

Carried forward as requirements or triggers, not design blockers:

- **OP-2** the internal test seam must be demonstrably unreachable from arguments and
  environment — implementation and test requirement;
- **OP-5** shell-level realization and determinism of the complete scan are unproven
  until implementation — implementation verification requirement;
- **OP-1 / OP-4** future historical-source extension semantics — resolved as
  reconsideration triggers (§6.3), to fail closed until explicitly owner-supported.

Superseded status observations, recorded for accuracy: the Root-H V2 report's
`H_TEST_PATH_ADMIN_ALLOCATION_STATUS=NOT_ALLOCATED` and its OP-3 are stale and are
externally closed by the durable ordinal-2 admin allocation.

Next safe action:

1. owner/coordinator review of this frozen spec;
2. only after that review may a separate prompt authorize writing the detailed TDD
   implementation plan;
3. implementation remains separately unauthorized thereafter.
