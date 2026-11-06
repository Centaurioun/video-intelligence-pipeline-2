# VIP B-first — prospective TDD successor plan: policy fixture ref vs file occurrence

**Date:** 2026-11-06  
**Status:** BOUNDED TDD IMPLEMENTATION PLAN — NO MAIN MERGE.  
**Owner/context:** Approved ongoing low-assurance B-first synthetic work; bounded evidence-semantics ruling `docs/decisions/2026-11-06-vip-bfirst-policy-reference-vs-observed-file-identity-ruling.md` on this LAB decision branch.
**Independent root-cause audit:** LAB `review/vip-bfirst-manifest-source-identity-audit-20261106@0691e332b757b464fcc4f9622ca4531814b4d8c7`.
**Exact Canonical starting commit:** `c474b8702d610462c455f8598052c06fe7dd9dd9`, tree `67f62da71954f7afa081467b2f9ff6f6f01517bd`.
**Immutable main snapshot for comparison:** `3bfcc2ba221b36df6773e630b44479ec961d630a`; do not use local main as feature base.

## Scope / exclusive writers

Only amend:
- `src/vip_fvs/trusted_fixture_manifest.py`
- `tests/vip_fvs/unit/test_trusted_fixture_manifest.py`

Keep current `bounded_admission.py`, `_bounded_admission_fs.py`, `cli.py`, source snapshot, query grant, `core_report.py`, all frozen temporal contracts, fixture JSON blobs, SQLite schema, CI workflow and existing scripts read-only.

Do not create or alter any media, model, provider, protected source, Gate, production render, legacy interval, Canonical/LAB main or DO_NOT_DELETE backup. Do not use destructive Git (reset, clean, force) or touch prior dirty/worker worktrees.

Suggested isolated Canonical successor branch: `feature/vip-bfirst-policy-observed-occurrence-repair-20261106`. Exact base is `c474b870...`. New clean native worker preferred, independent reviewer uses another clean detached worktree at final candidate SHA. Use current verified native thread/project tool schema, writer lease and Git common-directory rules.

## Phase 0 — independent preflight and test environment before code

1. [ ] Verify exact GitHub branch, candidate HEAD/tree, owner ruling, repo `AGENTS.md`, current Portfolio/path ownership, permissions and worktree preconditions.
2. [ ] Inventory every code/test reference to `AdmittedTimingRecipe`, `FixturePolicyEntry`, `.occurrence_id`, `admit_fixture` at exact candidate SHA; identify whether any previously frozen contract or consumer relies on an unqualified occurrence ID. New module is currently isolated in two changed files, but verify rather than assume.
3. [ ] Resolve installed Python 3.11/3.14 **and working pytest** for the worker before writing the prospective test. If interpreter lacks pytest, use an existing approved project test environment; do not download dependencies without permission. A collection/environment error is not behavioral RED.
4. [ ] Preserve exact before/after command, failing node IDs and test logs. Do not rewrite historical `NOT_OBSERVED` RED receipt from `c474...`.

## Phase 1 — genuine RED on frozen unmodified candidate

1. [ ] Add a deterministic unit test that prepares **two simultaneous separate synthetic roots** in a safe workspace with byte-identical copies of the *already reviewed JSON timing recipe*. Avoid media generation or protected files.
2. [ ] Using a test-only controlled root seam, admit the same `fixture_id` in both roots under identical permitted operation and purpose. Both inputs must hash to the same exact pinned SHA-256 and size; their observed `device/inode` file identities must differ while coexisting.
3. [ ] Assert that the admitted `policy_fixture_ref` or equivalent clearly labels the frozen Git `commit/path/blob` **as policy reference** (MATCHED), **not** the physical opened-file occurrence. Assert that actual read file identity is separately MEASURED from the admitted descriptor; if a unique physical source occurrence ID is not evidenced, it must explicitly be `NOT_OBSERVED` as availability.
4. [ ] Assert that the old unqualified `occurrence_id="git:<commit>:<path>"` can no longer be presented as an observed file-occurrence claim. If a caller supplies such an ID as input without separate proof, refuse or treat only as an expected policy ref under a clearly distinct field—do not infer actual custody. Add a negative test that refuses before source read when a foreign claimed occurrence is supplied.
5. [ ] Run **new test(s)** against the frozen `c474...` module before editing production code. Capture true assertion/behavioral RED. If the observed behavior already meets the test, document `NO_BUG_CONFIRMED` and do not create change merely to force RED.

## Phase 2 — minimum GREEN without shared contract changes

1. [ ] Distinguish in the new module's output API: immutable pinned policy reference (`policy_fixture_ref` or semantically equivalent), observed file identity (`device`, `inode`, and a precisely named property), and source-occurrence availability (`NOT_OBSERVED` when a unique occurrence ID is not independently observed).
2. [ ] Keep `policy_commit`, `policy_tree`, `blob_oid` as policy references, not live Git checked-out identity. Do not assert current worktree HEAD equals old source commit, and do not equate same SHA with identical source occurrence.
3. [ ] Preserve closed allowlist, pre-read ID/purpose/operation checks, no caller-selectable root/manifest/grant, bounded no-follow descriptor reads, digest, source-size and hardlink guards. If `occurrence_id` argument remains for source compatibility, its contract must be explicit; do not accept a Git policy ref as source occurrence evidence.
4. [ ] Change only the two permitted paths. If consumer/contract evidence requires changes elsewhere or a versioned data migration, STOP with `BLOCKED_BY_CONTRACT` and exact file/line evidence.
5. [ ] Run new test to GREEN, then existing B-first tests and exact targeted CLI/report/authorization/bounded-admission regressions. Check two-root same bytes are not spuriously labeled the same observed file occurrence.

## Phase 3 — independent certification and honest status

1. [ ] Run target tests with Python 3.11 and 3.14 installed test environments; capture full counts, skipped/xfail, test node IDs. Use baseline comparator against exact `c474...` for newly observed regressions. Do not infer that original historical full-suite failures are unchanged without running comparable tests.
2. [ ] `compileall`, `git diff --check`, tracked-file secret scan, current native worktree verification. A reference-pack integrity check that cannot run remains `SKIPPED/NOT_OBSERVED`.
3. [ ] Commit only permitted paths on new isolated branch; **normal non-force push**. Run synthetic GitHub Actions against exact final SHA; note that smoke workflow excludes `test_trusted_fixture_manifest.py` unless its actual selected test list changes.
4. [ ] Obtain independent feature reviewer using **separate clean, read-only worktree** at exact SHA, with direct source/diff scrutiny and focused test rerun when a functioning environment is available. Record whether reviewer actually executed tests. A reviewer `NO_FINDING` without tests cannot be described as independent test replication.
5. [ ] Report in Turkish: immutable base/final SHA and tree, worktrees/project native IDs, exact two-path diff, observed RED/GREEN and environment details, two-root same bytes evidence, policy-vs-observed identities, retested regression delta, GitHub CI and reviewer, remaining system limits and local main unchanged.

**Acceptance:**
- Use `BFIRST_OCCURRENCE_SEMANTICS_REPAIR_VERIFIED` only if prospective TDD cycle, source semantics and final independent review/test receipts support it; otherwise `BFIRST_OCCURRENCE_SEMANTICS_REPAIR_PARTIAL`.
- Old `c474...` original TDD RED remains `NOT_OBSERVED`, even if successor has new RED.
- Whole B-first candidate status must be described with evidence classes; don't silently promote `BFIRST_MANIFEST_PRIMITIVE_PARTIAL` to VERIFIED just because a related successor has new tests.
- Always `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` (no pinned eligible video asset) and `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.

**Stop after independent successor candidate verification; no PR, main merge, protected media/model/Gate work.**
