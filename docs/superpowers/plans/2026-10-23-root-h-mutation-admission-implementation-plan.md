# Root-H Mutation Admission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended when genuinely independent) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkboxes for tracking. **Implementation remains gated on a separately verified current-write grant**; do not execute tasks on product/verifier files merely because this plan exists.

**Goal:** Add mandatory, byte-safe, changed-`src/`-path current-write admission to the existing Root-H workspace verifier, preserving historical source presence and every existing fail-closed control.

**Architecture:** Preserve all current `SOURCE-AUTH` provenance classifications. Independently enumerate source mutations from an immutable authority-bound task base through committed `HEAD`, index and worktree, including untracked and ignored source files; test each changed source path against the existing positive current authorization chain. Emit distinct machine-readable `SOURCE-MUTATION-AUTH` results, and make mutation denial contribute to the existing overall verifier failure, without granting historical presence or permissions.

**Tech stack:** existing Bash+embedded Python 3 stdlib `scripts/verify-workspace.sh`, Git plumbing with NUL-delimited byte output, `pytest` or direct Python 3 for `tests/scripts/test_verify_workspace_source_authorization.py`, isolated disposable Git repositories/worktrees and fixed admin bootstrap.

**Spec:** `docs/research/2026-10-23/boost-convergence/ROOT_H_MUTATION_ADMISSION_ERRATUM_PROPOSAL.md`; Owner planning approval `docs/research/2026-10-23/boost-convergence/OWNER_ROOT_H_DESIGN_APPROVAL.md`; frozen contract `docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md`.

## Global Constraints

- **Design-approved for planning; execution NOT YET authorized.** Before Task 1 edits, confirm an authenticated owner/admin Root-H current-write grant matching the execution root, exact branch/goal/task packet, immutable base and the **two precise files**:
  - `scripts/verify-workspace.sh`
  - `tests/scripts/test_verify_workspace_source_authorization.py`
- An existing/frozen historical source record, documentation PR, broad Owner intent or a resolved root identity is not the needed current-write proof.
- No editing canonical `main`, changing the bootstrap trust ref without a separate serialized admin authorization, silently merging PR #128, destructive Git, protected media, model/provider activity or Gate promotion.
- Begin from a freshly verified, isolated non-main base. Confirm the verifier implementation lineage: `main` lacks PR #128's `dependency_authorized` feature and dynamic-ordinal regression fix; do **not** overwrite those when composing the chosen verifier base. If authorized base/lineage cannot be reconciled, stop before writing.
- Preserve current `SOURCE-AUTH` line vocabulary, frozen baseline digests, post-baseline exact membership and transfer semantics, and overall PASS/FAIL. `SOURCE-MUTATION-AUTH` is an additional *specific* result, not a substitute for any other check.
- Scope is exactly `src/`. New gate alone does **not** validate `tests/`, `schemas/`, `scripts/` or other writes; enforce those separately through the task-packet/lane ownership controls.
- **Ignored `src/` files MUST be enumerated**, but are **not automatically admitted**: `SOURCE-AUTH` may still report an untracked source as `UNAUTHORIZED`. Mutation authorization and repository presence both retain their independent fail-closed verdicts.
- Never use `git reset --hard`, `git clean`, `git worktree prune`, force pushes, or modify the owner's dirty original checkout.
- Each task uses Superpowers `systematic-debugging` if it encounters unexpected behavior, `test-driven-development` for any change, independent code review at finish and `verification-before-completion`.

## Normalization note (2026-10-24) — test selectors, counts and grant scope

This note corrects two invalid selector strings and qualifies the reported counts; the tasks and scope above are otherwise unchanged.

- `-k mutation_historical` (Task 1) and `-k mutation_base` (Task 2) occur in **no** test node name at the candidate head, so the original selections would collect zero tests. Corrected to selectors that resolve statically at PR #130 head `a7f7236705835a0477cc03c355ba5f839c23be57`: `-k 'mutation_gate or mutation_packet'` (6 + 3 functions) and `-k mutation_gate` (6), respectively. `-k mutation_inventory` (Task 3) already resolves (3 functions).
- Reported counts differ across the historical set: this plan and the witness plan cite **141**, CP3 cites **122**; the static count at `a7f7236` is **125** `def test_*` functions in `tests/scripts/test_verify_workspace_source_authorization.py`. These are reported/static counts only; **no pytest collection or execution count was observed** during normalization.
- Grant scope: the two exact paths in Global Constraints are covered by the prospective grant `root-h-mutation-admission-20261023` (branch `execution/root-h-mutation-admission-20261023-v1`, writer thread `01a162d8-71dc-7af3-ad77-2cde09ca3e13`, recorded 2026-10-23). That grant is bound to that root/branch/base/writer/date; it does not carry to a new execution attempt, and publication of this plan is not a grant.

## Review Focus

1. **Inherited dependency delta:** a task base older than a dependency's source changes must not mistakenly re-authorize another writer's edits. Pin the correct base/lineage and reject ambiguous or mismatched provenance. Test in Task 2.
2. **Ignored/untracked source:** `.gitignore` cannot hide a source edit; testing must distinguish mutation gate positivity from the independent tracked-source presence failure. Task 3.
3. **Non-text and hostile filenames:** newline, spaces, glob characters, leading dash and invalid byte names must neither be split nor silently ignored. Task 3.
4. **Rename/delete and symlink shape:** both old and new names are evaluated; symlinked/unsafe `src/` inputs are not silently dereferenced. Task 3.
5. **Authority identity drift:** a valid branch name but wrong goal, witness, base, transfer or hard denial must not pass. Task 4.

## Dependency and ownership map

- **Task 0**: read-only preflight — establish exact authoritative verifier lineage and current isolated writer grant.
- **Task 1**: test the existing bypass and build the first mandatory mutation-gate slice.
- **Task 2**: immutable base/lineage validation and fail-closed refusal.
- **Task 3**: complete changed-path inventory, including ignored files and hostile filenames.
- **Task 4**: link changed paths to prospective positive current-write predicate and transfer/denial logic.
- **Task 5**: verify compatibility, independent review, publish non-main receipt; never claim full workspace PASS while unrelated checks fail.

The planned writer has **exclusive ownership** of the exact two implementation files. No concurrent writer may own either file. `src/` in this plan is the scanned input namespace, **not** a blanket permission to edit `src/**`.

### Task 0 — Immutable authority and implementation-base preflight (read-only; no source change)

**Files:** Read `scripts/verify-workspace.sh`, `tests/scripts/test_verify_workspace_source_authorization.py`, fixed manifest/task packets, PR #128 diff; produce execution ledger only in a separately authorized location.

**Interfaces:**
- Consumes: latest `origin/main`, `bootstrap`, chosen task packet with `root_id`, `goal_id`, `root_branch`, `base_sha`/`root_base_sha`.
- Produces: exact immutable `IMPLEMENTATION_BASE_SHA`, `MUTATION_BASE_SHA`, branch identity, writer, verified two-path positive authorization, and a no-collision ownership receipt.

- [ ] Re-fetch refs; verify clean isolated worktree, exclusive two-file writer, active branch, task packet and witness at fixed bootstrap.
- [ ] Determine **which recorded base field is authoritative**. Existing manifest may carry `base_sha`, `root_base_sha`, `substantive_base_sha`, `initial_head_sha`; do not choose by fallback guess. Cross-check the exact slot and validated packet and the spec. If the schema leaves this ambiguous, return a precise Owner design follow-up before any source mutation.
- [ ] Verify `MUTATION_BASE_SHA` is an immutable commit and ancestor of HEAD, and represents the correct starting candidate including approved dependencies. A broad parent commit shared by unrelated roots is not automatically the correct mutation comparison base.
- [ ] Compare verifier code from `main` versus PR #128. Select the authorized lineage that retains needed Root-H dependency semantics; do not silently overwrite PR #128.
- [ ] **STOP** if current-write grant for either file or correct immutable base cannot be established.

### Task 1 — Historical-write bypass RED; mandatory current-write verdict GREEN

**Files:**
- Modify: `tests/scripts/test_verify_workspace_source_authorization.py`
- Modify: `scripts/verify-workspace.sh`

**Interfaces:**
- Consumes: `current_root(manifest)`, `current_authorized(manifest, record, root_id, commit, path, branch, transfers)`, fixed task base.
- Produces: an independent `SOURCE-MUTATION-AUTH` verdict for actual `src/` changes; exit failure if even one changed path lacks a positive current-write predicate.

- [ ] RED test: create isolated Git repo with a historically admitted tracked `src/example.py`, mutate its committed content on the correct branch with no prospective writer grant. Assert `SOURCE-AUTH` remains historical, mutation unauthorized count `1`, overall verifier exit nonzero. Distinguish Root-H failure from unrelated full verifier failures by examining the specific line.
- [ ] Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/scripts/test_verify_workspace_source_authorization.py -k 'mutation_gate or mutation_packet'`; expected behavioral RED (new mutation gate not yet implemented).
- [ ] Implement one mandatory check integrated in verifier's actual execution, not a separate optional helper. Preserve present `SOURCE-AUTH` diagnostics. Gate checks changed paths against `current_authorized` after exact-root resolution.
- [ ] Re-run the focused test; expect mutation-denial output and exit nonzero for the intended reason. On a separate exact positive-grant fixture expect unchanged historical presence plus positive mutation result.
- [ ] Commit only after the task's exact paths and tests are reviewed; do not assert full workspace success.

### Task 2 — Immutable comparison base and provenance

**Files:** Same two authorized paths.

**Interfaces:**
- Consumes: authority-selected immutable `MUTATION_BASE_SHA`; HEAD/branch, validated slot/packet.
- Produces: deterministic, read-only base/HEAD change inventory or explicit fail-closed refusal.

- [ ] RED: wrong base, missing Git object, non-ancestor base, packet/slot disagreement, wrong branch, older base accidentally including unrelated dependency modifications. Assert all deny; no fallback to current HEAD and no caller-supplied base.
- [ ] Run focused tests with `-k mutation_gate` and establish RED from behavior (collection/import failure does not count).
- [ ] Implement base-resolution contract without inventing an unstated authority field. Use existing validated packet + canonical bootstrap identity.
- [ ] Re-run focused negative and positive tests, then commit within the two-path boundary.

### Task 3 — Git mutation inventory, ignored paths, and byte safety

**Files:** Same two authorized paths.

**Interfaces:**
- Consumes: validated `MUTATION_BASE_SHA`.
- Produces: exact repository-relative `src/` paths for committed base→HEAD, staged, unstaged, untracked and ignored edits (including both sides of a rename), without changing index/worktree.

- [ ] RED cases:
  - `git diff` committed modification;
  - staged-only change; unstaged-only change;
  - added/deleted and rename old/new paths;
  - untracked in-domain file and ignored in-domain file;
  - newline, space, asterisk, bracket, leading dash, invalid-byte path;
  - symlink and path alias attempts; Git subcommands failing or malformed NUL output.
- [ ] Implement read-only Git byte-mode subprocess collection. Use NUL-terminated outputs for commands such as `git diff --name-only -z --no-renames` (base→HEAD, cached, worktree) and `git ls-files --others -z` with explicitly verified standard/ignored filters. Treat rename as both delete/add via `--no-renames`, with exact source-path filtering. Require deterministic de-duplication; never shell-split, newline-split or silently discard undecodable records.
- [ ] Explicitly refuse files represented by invalid or ambiguous authority path bytes. Do not silently coerce via replacement characters. Do not dereference symlinks to grant off-tree writes.
- [ ] Assert ignored `src/` records appear in mutation inventory but still fail independent `SOURCE-AUTH` when untracked. No source creation is implicitly authorized by ignore inclusion.
- [ ] Run focused tests with `-k mutation_inventory` and confirm failure-to-pass progression. Commit reviewed changes.

### Task 4 — Current path authorization and negative coverage

**Files:** Same two authorized paths.

**Interfaces:**
- Consumes: exact mutation inventory, `current_authorized`, transfer records, hard-denial checks, writer/goal identity.
- Produces: `SOURCE-MUTATION-AUTH status=PASS|FAIL`, `SOURCE-MUTATION-AUTH unauthorized-change-count=N`, explicit per-path negative diagnostics, ordinary overall verifier failure on any denial.

- [ ] RED tests cover current-only, historical+current, historical-only, neither, wrong branch/root/goal, ambiguous root, hard denial, missing owner witness, malformed task packet, transferred-away paths, broad-domain-only inherited access, and bad Git status.
- [ ] Compare exact prospective authorized paths to each mutated path; grant a path only where a validated matching owner chain and task packet admits it. Never treat `dependency_authorized`, historical presence, `current-write-root`, or a prior broad domain as proof of mutation authorization.
- [ ] Implement stable machine-readable output while preserving prior `SOURCE-AUTH` output and existing global PASS/FAIL vocabulary.
- [ ] Test that no changes on a clean historical tree are not spuriously denied by this *mutation* check, while lack of root identity cannot be misreported as a positive ability to write.
- [ ] Run focused suite, then full Root-H suite and stop if previously passing security negatives regress.

### Task 5 — Certification, code review and non-main handoff

**Files:** Implementation diff must contain only the two authorized paths; any admin changes require a separate serialized authority lane.

- [ ] Freeze exact base/head/tree and compare `git diff --name-status -z` against the exclusive two-path grant, including index and worktree status.
- [ ] Execute complete `tests/scripts/test_verify_workspace_source_authorization.py` with actual pass/fail count and exit code, plus applicable Gate2 adjuncts where `verify-workspace.sh` is consumed.
- [ ] Run `bash scripts/verify-workspace.sh`, retain its exact exit code and every unrelated environment failure; do not relabel exit 1 to PASS.
- [ ] Test old `SOURCE-AUTH` line compatibility against the frozen fixture expectations, and negative adversarial matrix. Verify one genuinely authorized historical mutation passes only its mutation gate.
- [ ] Run `git diff --check`, redacted security scanner and any existing schema/contract checks without disabling checks.
- [ ] Independent code review against exact authorizing task packet and immutable base/head; fix blocking feedback only within the current two-path grant using TDD.
- [ ] If all task-bound checks pass and current admin authorization permits, commit/push non-main without force, read back exact remote SHA/tree/path list. If not, keep CP0/CP1 receipts and report the reason.
- [ ] Preserve all original worktrees, PRs and source media. DO NOT merge canonical `main` or claim Gate acceptance.

## Required stage-end handoff

Report in Turkish: active root/branch/goal and administrative trust SHA; immutable implementation and mutation bases; exact changed paths; RED/GREEN receipts with exit codes; preserved `SOURCE-AUTH` tests; negative mutation cases; independent review; full workspace verifier results; non-main remote commit/tree if actually published; downstream F02/#128/Gate3/B17 authorization **still separately pending**.

**No original product completion percentage may be inferred.**
