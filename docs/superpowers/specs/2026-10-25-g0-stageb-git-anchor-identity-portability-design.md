# Gate-0 Stage-B Git Evidence Anchor: Deterministic Identity and Portability Design

- **Status:** PROPOSED DESIGN + AUTHORITY ASSESSMENT — **NOT IMPLEMENTATION AUTHORITY**
- **Goal:** `VIP-WBS-G0-1-4-GIT-ANCHOR-PORTABILITY-DESIGN-20261025`
- **Subject:** `src/gate0/feasibility/macos_stage_b_evidence_anchor.py`
- **Base:** `078fd6f4b25cc1f684b16e249700e241b79cbe1c` (`origin/main`, merge of PR #195)
- **Branch:** `docs/g0-stageb-git-anchor-portability-design-20261025`
- **Date:** 2026-10-25
- **WBS item:** `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md:68-70` (G0.1.4)
- **Predecessor repair:** PR #194 (merged `83753c0a0c145eaede3d07ae0452f4f769d4439c`), branch `repair/g0-1-4-broad-ci-baseline-20261025`, head `6bb2f1660fedb35c8014d0d264d13f52a787d8f7`
- **Evidence class legend:** `MEASURED` = executed locally or by CI with recorded output; `MATCHED` = byte/text comparison against the pinned artifact; `EDITORIAL_INFERENCE` = reasoning from read artifacts; `NOT_OBSERVED` = availability status, not an evidence class.

---

## 0. Verdict in one screen

1. **Root cause (MEASURED, direct reproduction).** `_git_input()` runs `git` with a scrubbed environment that removes user/system Git configuration but **provides no author/committer identity**. `git commit-tree` therefore resolves identity from (a) repo-local `.git/config`, then (b) host auto-detection. Nothing in the product contract, tests, or review record makes (a) or (b) an intended requirement; the Linux CI failure in PR #194 R3 is a direct consequence.
2. **Contract status (MATCHED + EDITORIAL_INFERENCE).** No frozen Gate-0/Rev-18/S7 contract requires a host identity or a caller-visible identity input. The only normative S7 predicates that touch the commit are *parent, exact added path set, tree, and anchored byte equality* (`P18a`, Rev-18 spec line 480; `TABLE-STAGES` N3 line 325). Author/committer identity and commit timestamp are **unprotected commit metadata outside the evidence seal**. The S7 SHA is recorded **forward only** into S10/S11/S13 (`NAMES_COMMIT` edges, spec lines 394/402; additive chain `S7 ≺ S9 ≺ S13`, line 2729).
3. **Historical-artifact risk is nil (MEASURED).** No committed artifact, test token, or object in the current repository records a real S7 anchor commit (0 anchor-message commits among 9,473 commits in an 80,826-object DB; 0 anchor commits among 3,270 unique 40-hex tokens in `docs/` and 95 in `tests/`). Changing how future anchor commits are synthesized cannot rewrite or invalidate any existing evidence.
4. **Recommendation (DESIGN ONLY).** Adopt **Alternative A**: inject a **fixed, non-personal, explicitly synthetic** author/committer identity inside the existing private `_git_input` environment, and add an explicit `i18n.commitEncoding=UTF-8` argument so repo-local commit-encoding config cannot alter commit bytes. Keep timestamps real (unpinned). Do **not** add public parameters, do **not** write repo-local config, do **not** pin the clock.
5. **Companion fix, independently rejectable.** The anchor module reports *every* failure — including "Git could not synthesize the commit" — as `EVIDENCE_REFERENCE_UNRESOLVED`, while the frozen stage→failure table assigns S7 creation/verification failures the code `PREBUILD_ANCHOR_NOT_FROZEN` (`TABLE-STAGES` N3, spec lines 325, 2189). This is a measured, currently unasserted contract-conformance deviation and should be repaired in the same bounded packet (P1b) or explicitly deferred.
6. **Authority (EDITORIAL_INFERENCE + MATCHED).** **Implementation is not authorized today.** `macos_stage_b_evidence_anchor.py` is absent from the current successor write inventory (successor spec §11, blob `d3d7a4611e375317e651049bceb345fe0d879744`: "No additional product or test paths are proposed"); the V7 phase-exact regime is **not live on main** (authorization base `bd8ddce2…` is not a main ancestor, the V7 receipt dir is absent, and 28/44 FV5 paths are missing), so V7 Task-7 ownership is historical provenance rather than current permission; and `AGENTS.md` line 14 confines unrelated changes to separate explicit approval. This PR is therefore design + authority assessment only; §8 defines the exact packet an Owner authorization must name.

**Non-authorization statement:** this document proposes; it does not implement, authorize, schedule, or promote anything, and it does not alter any source, test, fixture, receipt, snapshot, or frozen contract.

---

## 1. Question, method, and what this document is not

### 1.1 Question

> How should the Gate-0 Stage-B evidence anchor synthesize the S7 Git commit so that anchor creation is deterministic with respect to **identity and host configuration**, fails **fail-closed and diagnosably** when it cannot, and preserves the exact evidence authority of the current seal — on every supported host — without changing frozen contracts or historical artifacts?

### 1.2 Method

Applied Superpowers **brainstorming** (identify intent, constraints, and alternatives before design) and **systematic-debugging** (symptom → reproduction → mechanism → phase isolation → contract classification), inside the repository's six-cycle refinement protocol (`docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md` §2, with the audit lineage in `docs/audits/ASTRA_SIX_CYCLE_LEDGER.md`). Full per-cycle record: `docs/agent-runs/run-20261025-g0-1-4-git-anchor-portability/SIX_CYCLE_REFINEMENT.md`.

### 1.3 Explicitly out of scope

No production source-code change; no test change; no fixture change; no spec/plan/WBS edit; no `.git/config` mutation; no real archive, model, provider, network, export, destructive Git, Gate promotion, or owner-backup activity. No change to signed evidence, frozen snapshots, or measurement carriers.

---

## 2. Verified starting state

### 2.1 Repository, PR #194, and CI

| Fact | Value | Class |
|---|---|---|
| Synchronized base | `origin/main = 078fd6f4b25cc1f684b16e249700e241b79cbe1c` (merge of PR #195) | MEASURED (`git fetch`/`rev-parse`) |
| PR #194 | MERGED 2026-10-25T14:42:40Z, merge commit `83753c0a0c145eaede3d07ae0452f4f769d4439c`, head `6bb2f1660fedb35c8014d0d264d13f52a787d8f7`, base `eaa90f3b984bae84f97f0cb229521378b24b7717` | MEASURED (`gh pr view 194`) |
| Previous failing baseline | broad CI run `40193765335` at head `f645609f8`: 13 failed, 842 passed, 64 skipped, 168 errors | MATCHED (PR #194 body) |
| Matched pristine-main Linux baseline | run `40197095252` at `53c86d0cc`: 10 failed, 845 passed, 64 skipped, 168 errors | MATCHED (PR #194 body) |
| #194 candidate broad CI | run `40201413236` at `6bb2f1660`: 1,024 passed, 64 skipped (Python 3.11 + 3.14) | MATCHED (PR #194 body, WBS line 9) |
| Current main CI after #195 | runs `40204041309` (Python synthetic smoke), `40204041344` (Gate-0 broad synthetic regressions), `40204041350` (D1 integrated regressions) — all `success`, 2026-10-25T14:49:30Z | MEASURED (`gh run list --branch main`) |
| Local broad suite at base | `PYTHONPATH=.:src .venv-gate0/bin/python -m pytest -q tests/gate0/unit` → **814 passed**, exit 0, on a clean *tracked* tree at `078fd6f4b` (only this run's untracked docs present) | MEASURED (`evidence/broad-baseline-20261025.log`; the independent reviewer's rerun returned 814 passed in 258.13 s) |
| CI broad-job selection | 1,024 passed, 64 skipped on Python 3.11 + 3.14 — a **different node selection** from the local 814 and not directly comparable | MATCHED (#194 run set / WBS line 9) |
| Local probe baseline | 18 passed in 45.07s, exit 0 (identical rerun 70.18s) | MEASURED (probe lane) |
| Host used for measurements | macOS 27.0.1 (Darwin 27.0.0) arm64, `git 2.55.0`, Python 3.11.9 | MEASURED (`evidence/probe-raw/environment.log`) |
| Anchor module bytes | `src/gate0/feasibility/macos_stage_b_evidence_anchor.py` = blob `5e479ab5b3ebfed33562284db246181f6d483810` at `origin/main`; identical blob already existed off-main at `3683eaf259aa8974a3e0d8666a9c196754bb503e` | MEASURED (independent authority audit, `evidence/authority-audit.md`) |

`gh run list` shows only successes for main; the *historical* #194 red baseline above is the evidence that the identity dependency is a real, observed failure, not a theoretical concern.

### 2.2 Local checkout configuration warning

This checkout's own `.git/config` currently supplies `user.name = "Disposable Test"` and a noreply `user.email` (untracked local state, not part of the base commit). It means local `commit-tree` calls here are resolved from *repo-local* config, which is exactly one of the accidental identity sources this design removes. Reproductions therefore construct fresh temporary repositories and control their config explicitly (`evidence/probe-identity.md` scenarios a–h).

### 2.3 What is NOT observed

`NOT_OBSERVED` here means availability status, not falsification:

- Linux host with an empty GECOS field was not re-run in this lane; the failure is `MATCHED` from PR #194 CI logs and local `user.useConfigOnly=true` reproduction, not re-executed on Linux.
- GitHub macOS runner behavior for this exact code path.
- Windows host behavior (not a declared supported host anywhere in the contract set — see §6.7).
- Any real S7 anchor creation on authentic archive/media (explicitly out of scope).

---

## 3. Systematic debugging: symptom → mechanism

### 3.1 Symptom

PR #194 broad CI (Linux) failed at anchor creation with `fatal: empty ident name (for <>) not allowed`; the same suites pass on macOS where Git auto-detects the host account name. PR #194 repaired the *test fixtures* only (repo-local `user.name`/`user.email` after `git init`, at `tests/gate0/unit/test_evidence_boundary.py:71-72` and `tests/gate0/unit/test_evidence_s8.py:162-163`) and recorded the product gap as unresolved. It did not touch product code.

### 3.2 Mechanism (MEASURED, code + probe)

`_git_input` at `src/gate0/feasibility/macos_stage_b_evidence_anchor.py:39-122` builds a **complete replacement** environment (`:48-55`):

```python
{
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "HOME": str(Path.home()),
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_TERMINAL_PROMPT": "0",
    "LC_ALL": "C",
}
```

`HOME` is deliberately preserved while `GIT_CONFIG_GLOBAL` is pointed at `/dev/null`, so the user's `~/.gitconfig` is neutralized; `GIT_CONFIG_NOSYSTEM=1` neutralizes `/etc/gitconfig`. **No `GIT_AUTHOR_*`/`GIT_COMMITTER_*` keys are provided.** Git's identity resolution order for `commit-tree` is therefore:

1. `GIT_AUTHOR_*`/`GIT_COMMITTER_*` environment — *absent*;
2. repository-local `.git/config` `user.name`/`user.email` — *present only if the repo happens to have it* (test fixtures, developer clones);
3. system/global config — *deliberately neutralized*;
4. host auto-detection (GECOS/`$USER@hostname`) — *the remaining, accidental source*.

`GIT_CONFIG_GLOBAL=/dev/null` also means the fix cannot be "the host's global gitconfig sets an identity" — that path is already closed by design, leaving only repo-local config or host detection. Measured host-detected identity inflates the commit to 248 bytes versus 240 bytes with an explicit identity (probe scenario b), so the anchor SHA is directly host-derived in that case.

Two further host-config leaks in the same leaf are MEASURED:

- **Commit encoding.** With repo-local `i18n.commitEncoding=ISO-8859-1`, Git emits an `encoding ISO-8859-1` header even for an ASCII message: 260 bytes instead of 240, different SHA, same second, same identity (probe scenario g). This is configuration-contaminated commit bytes.
- **Clock.** Two commits with identical parent/tree/message/identity created ~1.2 s apart differ only in author/committer epoch/offset headers and therefore in SHA (probe scenario f: `ccc1653…` → `6a120be…`).

### 3.3 Why this is an accident, not a security property (MATCHED)

- The Rev-18 spec's S7 section (§9.1) and predicates name parent, exact added set, tree shape, and anchored byte equality only; grep of the spec for identity/author/committer/timestamp/clock/GIT_ requirements yields **no normative identity or time statement**.
- The V7 implementation plan's Task-7 RED/GREEN pair (`docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md:25121-25179`) never exercises `create_s7_anchor`/`_git_input` against a host identity; its `evidence_dag_s7_anchor` fixture is a *test-support commit*, and the plan does not pin the subprocess environment.
- The frozen interface manifest contains **no entry for `_git_input`** (`git grep -c "_git_input" 078fd6f4b -- tests/gate0/unit/evidence_dag_interface_manifest.py` → no matches; the nearby lines `:3460-3476` describe `_read_host_native_image`). The manifested anchor surfaces are `create_s7_anchor`, `verify_s7_anchor`, `resolve_anchored_s1` (PUBLIC) and `_extract_registered_anchored_s1` (PRIVATE_SECURITY) — see `evidence/authority-audit.md:17,91-92`. The environment dictionary of the already-private, unmanifested helper is therefore **not** a frozen surface.
- The Oracle manifest (`tests/gate0/unit/evidence_dag_oracle_manifest.py`) lists the anchor module among A07 production paths, but every check is a feature-switch AST/TEXT_SCHEMA rule; none asserts identity, timestamp, or encoding.
- No committed test asserts a failure-code value for anchor failures (grep: `EVIDENCE_REFERENCE_UNRESOLVED`/`PREBUILD_ANCHOR_NOT_FROZEN` appear in tests only inside the manifest constant list).

### 3.4 Phase isolation: which failures are identity vs. something else

| Observed failure | Cause class | Product phase |
|---|---|---|
| `fatal: empty ident name` / `no email was given and auto-detection is disabled` (rc 128) | host identity unavailable | `create_s7_anchor` → `_git_input` |
| `fatal: bad object`/bad parent (rc 128) | caller/parentage defect | `create_s7_anchor` precheck (`:162`) |
| anchored byte mismatch / extra/missing path | tree-content defect | `verify_s7_anchor` (`:181-223`) |
| anchor commit != registered evaluation commit | lineage/binding defect | `resolve_anchored_s1` (`:226-245`) |

Only the first row is a *portability* defect. Rows 2–4 are intentional seals.

---

## 4. Exact behavior trace and downstream dependencies

### 4.1 Git-writing call sites in product code (complete grep of `src/`)

| Site | Call | Identity needed | Downstream evidence impact |
|---|---|---|---|
| `macos_stage_b_evidence_anchor.py:171-174` | `git commit-tree <tree> -p <parent> -m "Gate-0 S7 evidence anchor"` | yes | S7 commit SHA; forward-recorded in S10/S11/S13 only |
| `macos_stage_b_evidence_seal.py:99-107` | `git commit-tree <tree> -p <s7> -m "Gate-0 N4B additive seal"` | yes | B commit SHA; parent-s7 binding |
| `macos_stage_b_evidence_anchor.py:187-207` | `cat-file`/`ls-tree`/`rev-parse` rereads | no | P18a byte equality |
| `macos_stage_b_evidence_git.py:70-215` | read-only `rev-parse`, `cat-file`, `merge-base`, `rev-list`, `diff-tree` | no | context verification, generation identity |

The seal module does not duplicate environment logic: `seal.py:31-32` delegates to `anchor_mod._git_input(argv, git_mod._root(), input_bytes)`. **One private leaf controls the identity, encoding, timeout, and failure text for every product commit creation.**

### 4.2 Digest / seal dependency closure

1. `create_s7_anchor` hashes S1–S4 (`hash-object -w --stdin`), builds the exact 4-entry tree (`mktree`), commits it, then **re-reads every anchored path from the commit object and compares bytes** (`verify_s7_anchor`, P18a). Identity/encoding/timestamp affect the *commit object* but are never inputs to the anchored artifact digests.
2. `verify_repository_context` registers the verified context; `resolve_anchored_s1` binds `anchor.commit_sha == context.evaluation_commit` and `anchor.parent_commit_sha == context.base_controller_commit`; `boundary._create_verifier_owned_build_context` re-verifies the S7 seal before N4A measurement.
3. `seal_n4b` creates the additive B tree (S7 tree + exactly eight `S9/` files), re-verifies parent/tree/additivity/bytes, and `macos_stage_b_evidence_s8.py:60-140` cross-checks `SealResult` against `_git` parent/tree/blob reads.
4. The S7 SHA is *named* by S10/S11/S13 edges (`NAMES_COMMIT`), i.e. recorded forward. There is no path in which a pre-existing committed artifact's bytes or digests are recomputed from a *new* S7 commit.

Therefore: **changing how the S7 commit is synthesized changes only the identity of future anchor commits and the identity metadata inside them; it does not touch anchored bytes, trees, parentage, the seal, or any recorded digest.** This is the core evidence-authority conclusion of this design.

### 4.3 Failure surfacing today (MEASURED)

Any git failure inside `_git_input` (including missing identity) becomes:

```
EvidenceDagError(EVIDENCE_REFERENCE_UNRESOLVED, "Git anchor operation failed")
```

with **no return code, no stderr excerpt, no failing subcommand name** propagated (`:118-122`). Probe scenario c shows the exact product-level string; the manual rc-128/stderr evidence exists only outside the product. Consequently a CI identity failure is *indistinguishable* from a reference-closure failure and cannot be diagnosed from the product error alone.

### 4.4 Contract deviation found during the trace

| Failure domain | Frozen required code | Current product code |
|---|---|---|
| S7 not created as specified / anchored digest read disagrees (N3) | `PREBUILD_ANCHOR_NOT_FROZEN` (spec line 325, taxonomy line 2189) | `EVIDENCE_REFERENCE_UNRESOLVED` (`anchor.py:18`, used for all `_git_input` and verification failures) |
| reference closure / unresolved handle (N7, P19) | `EVIDENCE_REFERENCE_UNRESOLVED` (spec line 329, 2208) | same constant |

The module collapses two frozen failure domains into one. Nothing tests it, so it is invisible to CI; it becomes *relevant* here because the portability packet must decide which failure class a missing-identity failure reports.

---

## 5. Intended security properties vs. accidental host assumptions

| Behavior in `_git_input` | Classification | Rationale |
|---|---|---|
| `PATH` inherited from host | **Intentional** (needs a `git` binary) but tool identity unpinned/unrecorded | no contract pins the binary; P18a verifies bytes, so no authority loss |
| `HOME` preserved; `GIT_CONFIG_GLOBAL=/dev/null`; `GIT_CONFIG_NOSYSTEM=1` | **Intentional hermeticity** against user/system config | prevents a developer's gitconfig from changing anchor bytes |
| `GIT_TERMINAL_PROMPT=0`, `LC_ALL=C` | **Intentional** no-prompt, locale-stable behavior | no interactive hang; stable error text |
| No `GIT_AUTHOR_*`/`GIT_COMMITTER_*` | **Accidental omission** — environment is a *replacement*, not an overlay | failure observed in CI; no contract requires host identity |
| Repo-local `user.name`/`user.email` used when present | **Accidental**; fixtures happen to supply it | product never requires/documents it; makes results repo-dependent |
| Repo-local `i18n.commitEncoding` honored | **Accidental leak** | adds an `encoding` header and changes commit bytes (MEASURED) |
| Wall-clock author/committer time | **Accidental / unconstrained** | no contract requirement; variation is expected and harmless |
| `_HEX40` = strictly 40 lowercase hex (SHA-1 OID) | **Probably intentional** (Rev-18 applies to SHA-1 repositories) but undocumented | would reject SHA-256 repositories; separate portability question (§11.3) |
| Fixed commit messages `"Gate-0 S7 evidence anchor"` / `"Gate-0 N4B additive seal"` | **Intentional constants** | no behavioral significance beyond object identity |
| 10 s timeout, 1 MB output bounds, nonblocking stdin | **Intentional robustness** | unrelated to identity |

**Privacy property.** The status-quo behavior is also a *minimization* problem: on hosts where Git auto-detects identity, the host account's personal name/e-mail is written into the S7 commit object, which is reachable from the evidence repository. Rev-18 §12.4 (spec lines 2049-2100) requires personal name/e-mail not to be retained in any artifact or generation. The fixed synthetic identity therefore **improves** compliance with an existing privacy requirement; it must be labeled as a non-attestation value so no one can read it as a claim about the producing human or host.

**Security-property conclusion:** a fixed, clearly synthetic identity **adds** hermeticity and **removes** an accidental host dependency; it does not create a false attestation as long as the value is non-personal, reserved-domain (`example.invalid`), and documented as synthetic. It does not weaken any seal: the anchored bytes, exact path set, parentage, tree, reread equality, registry binding, and digest naming are untouched.

---

## 6. Governing-contract analysis (does any alternative change a frozen contract?)

### 6.1 Rev-18 design spec (frozen)

`docs/superpowers/specs/2026-09-20-gate0-recovery-evidence-dag-design.md`, blob `21e651503bff6dc2b369ad45923d16a3af8adf1c`, 2,966 lines. S7 = one commit, parent S0, exactly the four anchored paths; SHA recorded forward only; P18a/P18b/P18c and N3 taxonomy as cited. **No author/committer identity, timestamp, or commit-encoding requirement exists.** MEASURED: the exact command recorded in `evidence/verification-20261025.log` (`git grep -nE "GIT_AUTHOR|GIT_COMMITTER|commit-tree|author identity|committer identity|user\.email|git identity"` over the pinned Rev-18 design, Rev-18 spec, and V7 plan) returns rc 1 / zero matches. A deliberately *broader* pattern (`commit identity|committer identity`) matched spec lines 1029 and 1122, but those lines denote the *object identity* of a commit (object-type check plus reachability), not a person identity — verified by reading them. The log records both patterns and both return codes, so the distinction is visible rather than hidden. ⇒ Alternative A requires **no spec amendment**. Alternatives B (new public parameter) would change the frozen interface surface and would need the successor interface process.

### 6.2 V7 implementation plan (frozen)

Blob `aad90adfedd616eee25b8302ce4f937130462bd6`. Task 7 owns exactly `src/gate0/feasibility/macos_stage_b_evidence_anchor.py` + new `tests/gate0/unit/test_evidence_anchor.py`; its RED/GREEN tests do not exercise host identity; §10.5 FV5 requires changed paths to **equal** the epoch's 44/45-path receipt sets (plan lines 23979-23981; lists at 24238/24285); §11 assigns exclusive phase paths.

**The V7 phase-exact regime is NOT live on main (MEASURED by the independent audit).** The V7 authorization base `bd8ddce2eb024d927b2c8715d8545105479ae01c` is not an ancestor of main (`git merge-base --is-ancestor` rc=1; the base exists only on `agent/area-a` refs); `docs/agent-runs/run-20260923-gate0-rev18-implementation-v1/` does not exist on main; and 28 of the 44 FV5 required paths are absent from main. `PRE_RECEIPT_REQUIRED_CHANGED_PATHS` exists only as plan text and as unrelated parsing code in `macos_stage_b_evidence_constants.py:389` — no live script or test enforces FV5 path-set equality against the current tree.

⇒ The V7 plan remains **current as plan/interface truth** (the interface manifest header forbids editing the manifest to match an implementation), but it does **not** supply live write ownership for `anchor.py` on main, and its FV5 rule is not a lock a new packet could "break". A new packet must nonetheless define its own changed-path set and must not claim V7 FV5 compliance or V7-phase reactivation.

### 6.3 Lineage gap (MEASURED)

- **Main introduction vs. content origin.** The anchor module's current bytes (blob `5e479ab5b3ebfed33562284db246181f6d483810`) were introduced to main **solely** by `3598c8e4f20ea53db6597402d3c2c8dd1dfeaa12` "Checkpoint authorized A07 closure hard stop" (parent `1bdf57b423ae84034184b8c4d2c441616c78301f`; 20 files, 15,689 insertions). The **identical blob already existed off-main** at `3683eaf259aa8974a3e0d8666a9c196754bb503e` (2026-09-27, parent `4c1e39b4c069bdfc7df96f613a1b77d6d3a77df2`, tip of the V7 Task-7 lineage `2355771da` → `3683eaf25`); archived commit `424496b90` on another branch is not an ancestor of main. ⇒ 3598c8e4f **materialized already-authored bytes**; it did not author the behavior (AUD-M4).
- **The V7 Task-7 test exists off-main, not on main.** `tests/gate0/unit/test_evidence_anchor.py` exists as blob `18c3f189f767330e04878215e228930993707fef` (258 lines) in that same off-main lineage, with a `GitAnchorTestRepo` helper that sets a synthetic `test@example.invalid` identity; it never asserts a failure code. It does **not** exist at `078fd6f4b`, `3598c8e4f`, or `1bdf57b42`; `git log origin/main --` that path is empty and there is no deletion commit (MEASURED). Correct characterization: **V7 Task 7 was implemented off-main but never integrated**, so main carries the anchor product code while its dedicated regression test lives only on non-canonical refs. (An earlier draft of this document said "never implemented" — corrected by the independent audit.)
- The open Problem `H3-G02-A07-BASE-003` (`state: OPEN_BLOCKS_G02_INTEGRATION`, family `A07_PREDECESSOR_CLOSURE_INCOMPLETE_ON_FRESH_MAIN`) already records a *different* closure incompleteness (`scripts/stage-b-build-app.sh` absent at candidate HEAD). The missing anchor test is a **second** instance of the same closure family and must be handled by the same reconciliation route, not silently added inside an unrelated packet.

### 6.4 Successor chain (current live authority)

- Owner authorization `OWNER-AUTHORIZATION-G0-SUCCESSOR-2026-10-03` (`docs/agent-runs/run-20261003-gate0-successor-authority-v1/owner-implementation-authorization.md`/`.json`) authorizes successor tasks 4–12 (H3-A02…H3-A07) and binds the successor spec (blob `d3d7a46…`) and successor plan (blob `5770a34…`).
- Successor spec §11 enumerates the product write paths EXACTLY: `macos_stage_b_evidence_constants.py`, `..._boundary.py`, `..._projection.py`, `..._seal.py`; test paths exactly five files; **"No additional product or test paths are proposed."** `anchor.py` and `..._git.py` are **not** in the live write inventory.
- Successor §9 states predecessor Tasks 1–7 remain unchanged; successor Task 7 is `seal_n4b` / N4B — a different Task 7 from V7's S7 anchor Task 7.
- The successor spec, successor plan and Task-4 amendment are all **non-ancestors of main** (reachable only from `e717030ad…` / `2ffcf162…` on planning/agent/codex refs; blobs match the owner record) — they must be cited as blobs, not as merged files (AUD-M5). Their authority is the owner record, not merge state.
- **A07/G02 integration-manifest pins.** `.orchestration/remaining-work/convergence/H3-G02-20261008/generation-002/integration-manifest.json:10,90` and `generation-004/a07-integration-manifest.json:31` pin the anchor module at blob `5e479ab5…`, and that line's status is `BLOCKED_PENDING_OWNER_AUTHORITY_RECONCILIATION`; only `scripts/stage-b-build-app.sh` carries explicit per-path owner text (audit's provenance weakness, AUD-M2). Any byte change to `anchor.py` therefore creates a new candidate for which the A07 freeze rule requires rerun of the 298-test focused set plus broad suite; the pins become historical and the packet may **not** claim A07/G02 closure or Gate promotion (AUD-M3).

⇒ **No live authorization names the anchor module.** This is blocker B1 (§10.2).

### 6.5 Frozen interface and oracle manifests

Public signatures frozen: `create_s7_anchor(parent_commit_sha: str, artifacts: tuple[FrozenArtifact ×4]) -> S7AnchorCreateResult`; `verify_s7_anchor(anchor, artifacts) -> S7VerificationResult`; `resolve_anchored_s1(repository_context, anchor) -> AnchoredS1Handle`; `_extract_registered_anchored_s1(...)`; `_git_input` private. Alternative A adds **no** signature change ⇒ **no interface-manifest change** (manifest update only needed if a public signature changed — it does not). Oracle manifest needs no change (no identity assertions). ⇒ **P1a changes no manifested surface; P1b changes none under the §8.2 route (it consumes an existing enum value), and `_git_input` has no manifest entry to change.**

### 6.6 Frozen failure taxonomy

`EvidenceFailureCode` is a frozen enum in `macos_stage_b_evidence_constants.py:9` (31 values incl. both codes), enumerated by the interface manifest. Using `PREBUILD_ANCHOR_NOT_FROZEN` for N3 failures does **not** add/remove an enum value ⇒ no manifest change; it corrects which existing value the N3 domain reports. This is a behavior change that a reviewer can reject independently of the identity fix — hence P1b.

### 6.7 "Supported hosts"

No artifact in the read contract set asserts a supported-host list (`grep` of Gate-0 experiment contract, canonical contracts, v1.1 spec, Rev-18 spec, successor spec for host/platform statements → 0 hits). The evidence is: macOS local + `ubuntu-latest` CI. ⇒ the design states its host assumptions (POSIX, `git` on `PATH`, SHA-1 repos) rather than claiming a platform contract, and flags Windows as unclaimed.

---

### 6.8 Independent audit reconciliation (2026-10-25)

A separate read-only lane (`evidence/authority-audit.md`, 244 lines, base `078fd6f4b`, no src/test writes) independently audited every authority claim in §6 and returned: Q1 authority VERIFIED (split: design authority from Rev-18 spec; V7 phase ownership **not live**), Q2 identity/timestamp requirement VERIFIED ABSENCE (zero grep matches across Rev-18 spec, V7 plan, successor spec/plan), Q3 contract compatibility VERIFIED with one disclosed caveat (S7/N4B commit SHAs change observably; tree/blob bytes do not), Q4 failure-code deviation VERIFIED (AUD-M1), Q5 FV5/inventory VERIFIED (44/45 unsatisfiable on main; successor §11 excludes `anchor.py`), Q6 claim checks (6a VERIFIED; 6b PARTIALLY_VERIFIED — see §6.3; 6c VERIFIED for main with the off-main file documented; 6d VERIFIED), Q7 disposition: no current instrument authorizes editing `anchor.py`.

Corrections applied to this document as a result: §6.2 now states the V7 phase regime is not live; §6.3 now separates main introduction from content origin and records the off-main test file (258 lines); §6.4 adds the A07/G02 pin-staleness obligation; §5 records the privacy improvement; §8.2 requires P1b to carry its own authority clause and Problem id; §10 adds blockers B6/B7; Appendix A uses `example.invalid` (audit: bare `@invalid` is not the reserved form). Audit residual findings AUD-M6 (H3-A07 core read scope names an absent `test_evidence_constants.py`) and AUD-m1/m2 are recorded here for the controller's reconciliation, not resolved by this design.

---

## 7. Alternatives analysis

Scoring: **contract** = does it change a frozen contract/interface? **det.** = does it remove identity nondeterminism? **host** = host-state mutation? **auth.** = authority burden. **Risk** = residual risk.

| ID | Option | Contract change | Deterministic identity | Host mutation | Authority burden | Verdict |
|---|---|---|---|---|---|---|
| **A** | Fixed synthetic identity in private `_git_input` env (+ explicit UTF-8 commit encoding) | **None** | Yes (identity; timestamp intentionally free) | None | Bounded Owner repair packet | **RECOMMENDED (P1a)** |
| **A′** | A minus encoding hardening | None | Yes (identity only) | None | same | Acceptable fallback; encoding leak remains |
| **A″** | A plus `user.useConfigOnly=true` / GIT_CONFIG_* fail-closed guard | None | Yes, and *proves* no host detection | None | same, plus git-version floor (GIT_CONFIG_COUNT ≥ git 2.31) | **Optional**; cannot be behavior-tested while identity env is present; defer unless a second regression appears |
| **B** | Public caller-supplied sealed identity parameter on `create_s7_anchor` | **Yes** — frozen public signature + interface manifest + successor process | Only if every caller passes it | None | Architecture/interface disposition | **REJECTED** — larger than the problem, breaks frozen surface, adds an authority bypass surface |
| **C** | Product writes repo-local `user.name`/`user.email` | No (but mutates host repo) | Yes | **Yes** — persists in `.git/config`, races, pollutes user clones | Security review of mutation | **REJECTED** — non-hermetic side effect; would let a product call change unrelated commits' authorship |
| **D** | Fail-closed preflight only (detect absent identity, raise diagnostic) | No | **No** — still host-dependent | None | small | **REJECTED as standalone**; **partially retained** as P1b failure reporting |
| **E** | Pin author/committer timestamps (fully reproducible S7 SHA) | **Yes, semantically** — implies a reproducibility guarantee the spec never made, changes uniqueness/collision assumptions | fully | None | Architecture disposition | **REJECTED / DEFERRED** — not required for evidence authority; would need a contract statement on commit-time semantics; see trigger T2 |
| **F** | Do nothing; document only | None | No | None | none | **REJECTED** — knowingly leaves a reproduced CI failure in the product path |
| **G** | Absolute-path / pinned `git` binary + recorded version | No (toolchain pin) | Partially (reproducible tool, not identity) | None | separate toolchain policy | **DEFERRED** — out of scope; noted as residual gap (git version not recorded in evidence ledger) |
| **H** | Use ambient identity when present, fixed identity otherwise | None | **No** — host-dependent by design | None | none | **REJECTED** — defeats the objective |
| **I** | Hand-serialize the commit object (`git hash-object -w -t commit --stdin`) | No | Yes | **Larger** — own commit-grammar/serialization correctness surface | same | **REJECTED** — reimplements Git object formatting, risks malformed objects, no authority gain over `commit-tree` |
| **J** | `-c user.name=... -c user.email=...` on the argument vector | No | Yes | None | same | **REJECTED** — equivalent to A but repeats identity per invocation and is argv-visible; the replacement env is the existing, smaller mechanism |

### 7.1 Decision record

| ID | Decision | Rationale |
|---|---|---|
| D1 | Fixed identity lives in the **private env dict**, not in public API | It is an implementation detail of a hermetic subprocess, not a caller contract; the frozen interface stays intact; seal module inherits the fix through its existing delegation. |
| D2 | Identity is **explicitly synthetic and non-personal** (`@example.invalid`, RFC 2606 reserved labels) | Avoids any impression of human/owner authorship and **improves** minimization: today's host auto-detection writes a personal name/email into the S7 commit object, while Rev-18 §12.4 (spec `:2049-2100`) requires personal name/email not be retained in any artifact or generation; precedent `test@example.invalid`. |
| D3 | Timestamps remain **real, unpinned** | Timestamp is unprotected metadata; pinning would silently imply a reproducibility contract that does not exist and would need architecture disposition (Alternative E). |
| D4 | Encoding is fixed in the **same private leaf** via an explicit `-c i18n.commitEncoding=UTF-8` argument | One measured host-config leak, one line, no git-version floor (unlike GIT_CONFIG_COUNT); can be dropped to A′ if the Owner wants the absolute minimum. |
| D5 | Failure classification repaired **separately** (P1b) | Independently rejectable; changing the reported code is observable behavior and deserves its own acceptance line and test, even though it needs no enum/manifest change. |
| D6 | No repo-local `.git/config` write, no caller parameter, no timestamp pinning | Smallest safe surface; preserves hermeticity (Alternative C/B/E rejected). |

---

## 8. Recommended packet (design only — not implemented here)

> Everything in this section is a **proposal**. No source, test, or fixture was modified by this lane.

### 8.1 P1a — deterministic identity (core)

Single product file: `src/gate0/feasibility/macos_stage_b_evidence_anchor.py`.

1. Add a module-private constant, e.g.

   ```python
   _GIT_IDENT = {
       "GIT_AUTHOR_NAME": "Gate-0 Evidence Anchor",
       "GIT_AUTHOR_EMAIL": "gate0-evidence-anchor@example.invalid",
       "GIT_COMMITTER_NAME": "Gate-0 Evidence Anchor",
       "GIT_COMMITTER_EMAIL": "gate0-evidence-anchor@example.invalid",
   }
   ```

   with a comment stating: *synthetic container identity, not a claim of human authorship; identity/timestamp are outside P18a and the evidence seal; MUST NOT be replaced by host or user identity.* The exact string values are an Owner naming decision; whatever is chosen must be non-personal and non-deliverable.

2. Merge it into the existing env dict at `anchor.py:48-55` (replacement dict, so no host leakage):

   ```python
   "env": {**_GIT_IDENT, "PATH": ..., "HOME": ..., "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"},
   ```

3. Add explicit commit encoding where the commit object is written. Because the seal module delegates to `_git_input`, the least-duplicative form is to prepend a command-scope config to the argument vector inside `_git_input`:

   ```python
   subprocess.Popen(("git", "-c", "i18n.commitEncoding=UTF-8", *argv), ...)
   ```

   Rationale: command-scope config beats repo-local config; no git-version floor; a single site fixes both S7 and B commits. A per-call-site variant (`anchor.py:171-174` plus `seal.py:99-107`) is **not available to this packet**: `seal.py` is outside the authorized write set, and a one-site patch would leave N4B commit bytes configuration-contaminated. The single private-leaf prefix is therefore the only form that fixes both commits within the authorized two paths.

4. No other product change. `_HANDLE_REGISTRY`, verification, and public signatures untouched.

**Delta size estimate:** ~10 changed/added lines in one file; no new imports; no signature change; no manifest change.

### 8.2 P1b — failure reporting conformance (independently rejectable)

Same file, separate commit:

1. **Do not change `_git_input`'s error semantics.** It is shared with `src/gate0/feasibility/macos_stage_b_evidence_seal.py:31-32`, and the N4B `commit-tree` at `seal.py:107` relies on its current `EVIDENCE_REFERENCE_UNRESOLVED` behaviour (seal's own frozen failure surface). Keep `_fail` and the module `_FAILURE` unchanged for that leaf and for `resolve_anchored_s1`/handle-closure paths.
2. **Wrap only inside the S7 domain.** In `create_s7_anchor` (all `hash-object`/`mktree`/`commit-tree`/reread calls) catch `EvidenceDagError` and re-raise `EvidenceDagError(EvidenceFailureCode.PREBUILD_ANCHOR_NOT_FROZEN, bounded_reason)`; in `verify_s7_anchor`, catch and return `S7VerificationResult(False, EvidenceFailureCode.PREBUILD_ANCHOR_NOT_FROZEN, ())` instead of `_FAILURE`. No signature, argument vector, `_git_input` call shape, or manifest entry changes.
3. Improve the reason text only at that S7 wrap site: include the failing subcommand without host/identity values or stderr blobs, e.g. `f"Git anchor operation failed: {argv[0]}"` and, where safe, a bounded rc. Do **not** echo stderr (it can contain the host-derived identity string); allow only a whitelisted suffix such as `"empty ident"`/`"no email"` classification, never the raw line.
4. Traceability: the packet's evidence record must map each failure family to its frozen code and record that the reported code is now asserted by a test, **including an N4B non-regression test** proving seal failures keep `EVIDENCE_REFERENCE_UNRESOLVED`.
5. **Authority note (AUD-M1).** P1b changes an *observable* value (`failure_code` in frozen result objects), not just a private string. It must be named explicitly in the packet authorization and tracked as its own Problem, proposed id `G0-ANCHOR-N3-FAILURE-CODE-DEVIATION`; it must not be folded under the identity label, and an Owner may defer it without deferring P1a.

### 8.3 New test file (required by V7 Task 7, missing on main)

`tests/gate0/unit/test_evidence_anchor.py` — see §9. The path exists off-main (blob `18c3f189…`, 258 lines, `GitAnchorTestRepo` using a synthetic `test@example.invalid` identity, no failure-code assertion); the packet should carry the V7-required tests **and** the new identity/determinism matrix, taking the off-main file as a reference rather than silently re-authoring its history. Creating it addresses part of the lineage gap in §6.3 but does not close the A07 problem; **if** the closure reconciliation (`H3-G02-A07-BASE-003` route) prefers to materialize the historical file first, the packet can instead extend that file, but it must not silently treat the gap as closed.

Node-inventory note (test-matrix lane, MEASURED plan citations): the new file's test node IDs are **not** in V7's closed expected-new-test-node inventory (`"schema": "G0_REV18_V7_EXPECTED_NEW_TEST_NODE_IDS_V1"`, plan `:7425`, node lists `:7491-7493`/`:7568-7570`, prefix block `:7925`). No script mechanically enforces that inventory today (PREDICTED, no code found), but the packet's authorization must either declare the added node IDs explicitly or record a node-inventory delta.

### 8.4 Acceptance criteria (for the future packet)

- Focused: `PYTHONPATH=.:src .venv-gate0/bin/python -m pytest -q tests/gate0/unit/test_evidence_anchor.py` — all green, including the new RED-first identity tests.
- Broad: `PYTHONPATH=.:src .venv-gate0/bin/python -m pytest -q tests/gate0/unit` — no regression versus the recorded base count **814 passed** (and versus CI's broad count on the authorized base); no new skip/xfail.
- CI: broad synthetic regressions green on both Python versions, i.e. the Linux runner no longer needs a fixture-provided repo-local identity (keep those fixture fixes anyway — they are correct and hermetic).
- Evidence preservation: `git diff` of anchored-path bytes empty; `git status` shows no `.git/config` change; the test that hashes anchored/re-read bytes passes unchanged.

**Determinism statement.** The packet deliberately does not pin commit timestamps, so an S7 SHA still varies with wall-clock time and with the parent commit. The fix makes the *identity and encoding inputs* deterministic, not the SHA. Acceptance must therefore compare **structural** commit equality (tree, parent, exact four-path set, anchored bytes, author/committer lines, message); SHA equality may be asserted only when both commits are created inside the same wall-clock second, with a bracketed retry/`skip` for the boundary case.
- Documentation: no spec/plan/WBS edit inside the packet (proposal text may be recorded in the packet's evidence record); WBS change is a separate disposition (§11.4).

### 8.5 Non-goals (must be restated in the packet authorization)

No public API change; no new dependency; no repo-config write; no timestamp pinning; no SHA-256 OID support; no `seal.py`/`git.py`/manifest changes; no historical artifact or receipt rewrite; no change to frozen contracts; no real archive/model/provider/network/Gate activity.

### 8.6 Rollback

Revert the packet commit(s). No data migration; no stored evidence depends on the new identity (MEASURED: zero existing anchor commits anywhere in the object DB, docs, or tests). If a future signal exists (real anchors created after P1a), rollback remains safe: old anchor objects persist and verification is byte-based, so reverting identity logic cannot invalidate anchors already recorded forward.

---

## 9. RED→GREEN test design

Full matrix, per-test intent, mutation wording, and runnability notes: `docs/agent-runs/run-20261025-g0-1-4-git-anchor-portability/evidence/red-test-matrix.md`. Summary:

| # | Test (new file unless noted) | Scenario | Expected RED on current code | Expected GREEN after P1a |
|---|---|---|---|---|
| T1 | `test_anchor_creation_succeeds_without_host_or_repo_identity` | fresh tmp repo, no `user.*`, `user.useConfigOnly=true` repo-local (deterministic proxy for an identity-less host) | `EvidenceDagError ... Git anchor operation failed` (rc 128 upstream) | anchor created, verify passes |
| T2 | `test_anchor_identity_is_fixed_not_host_or_repo_supplied` | repo-local identity = divergent values; parent process env has divergent `GIT_AUTHOR_*` | commit author/committer = divergent repo identity (host/ambient influence) | commit author/committer = fixed synthetic constants |
| T3 | `test_anchor_commit_encoding_is_host_independent` | repo-local `i18n.commitEncoding=ISO-8859-1`; same parent/artifacts/second | commit has `encoding ISO-8859-1` header, 260-byte object | no `encoding` header, UTF-8/240-byte shape |
| T4 | `test_repeated_anchor_creation_is_structurally_identical_and_mutation_free` | two `create_s7_anchor` calls, same parent/artifacts; compare tree, parent, exact four-path set, anchored bytes, author/committer lines, message (SHA equality only if both fall in one wall-clock second) | passes today only because identity is constant within a host (not a true RED) — **regression lock**, must pass before and after | unchanged pass; also asserts `.git/config` unchanged and S1–S4 bytes unchanged |
| T5 | `test_same_second_distinct_parents_yield_distinct_anchors` | two parents, same artifacts, commits bracketed inside one wall-clock second (retry/skip at the boundary) | passes today; regression lock protecting S7 uniqueness | passes |
| T6 | `test_anchor_mutations_fail` (V7-required: missing/extra/changed/wrong_parent) | tamper S7 tree | n/a today (no test file) | fails closed for each mutation (P1b: code = `PREBUILD_ANCHOR_NOT_FROZEN`) |
| T7 | `test_scrubbed_environment_cannot_be_escaped_by_ambient_git_env` | ambient `GIT_AUTHOR_*`, `GIT_CONFIG_*`, `GIT_DIR`, `LC_ALL` set to hostile values in the parent process | the env is a total replacement, so ambient variables cannot leak by construction; the *documented residual escapes* are repo-local config (`user.name`/`user.email`, `i18n.commitEncoding`) and host auto-detection | fixed identity + UTF-8 prefix win; replacement env preserved |
| T8 | `test_verified_context_and_s7_share_exact_tmp_repo_lineage` (V7-required, port from `agent/*` historical file) | product-created S7 + `verify_repository_context` + `resolve_anchored_s1` | n/a (file absent) | exact lineage binding holds |
| T9 (P1b) | `test_missing_identity_failure_is_classified_and_diagnosable` | PATH-injected fake `git` that exits 128 with `empty ident name` on `commit-tree` only | generic `EVIDENCE_REFERENCE_UNRESOLVED: Git anchor operation failed` | `PREBUILD_ANCHOR_NOT_FROZEN` + bounded diagnostic that contains no host identity |

**Id-map warning:** the matrix lane (`evidence/red-test-matrix.md` §2) uses its own T1–T9 numbering (6 RED + 3 GREEN preservation locks, including T6 repository-state preservation and T7 byte-exact four-path set). That matrix is the canonical test-id list; the summary above is a design-level view and its ids must not be copied into a packet without re-mapping. Existing `verify_s7_anchor` already enforces the closed set/P18a; the matrix's preservation locks additionally prove the fix does not mutate `.git/config`, refs, HEAD, or anchored bytes.

Fixture policy: temp repos only (`TmpGitRepo`/`monkeypatch` root discovery as existing tests do), no network, no host config reads; assertions on commit headers use `git cat-file -p` of the created object so they are host-independent.

**Crosswalk: required user scenarios → test ids.**

| User-required scenario | Design test | Canonical matrix id |
|---|---|---|
| Missing Git identity | T1 | matrix T1 |
| Divergent host identity | T2 (repo-identity proxy; host auto-detection is unreachable post-P1a by construction, so it cannot be tested directly without a third-party `git` shim) | matrix T2 |
| Same-second commit creation | T4 / T5 (structural equality; SHA only within one second) | matrix T4/T5, matrix T8 |
| Scrubbed environment | T7 | matrix T7 |
| Source/evidence preservation | T4 preservation assertions + §8.4 acceptance | matrix T6/T7 |

---

## 10. Authority assessment, blockers, and the next executable packet

### 10.1 Assessment summary

| Question | Answer | Basis |
|---|---|---|
| Does the recommended design change a frozen contract? | **No** | §6.1–6.2, 6.6; identity/encoding are unspecified metadata outside P18a |
| Does it change a frozen public interface or manifest? | **No** | §6.5; private env/argv only |
| Does it require a separate architecture disposition? | **No architecture amendment**; yes, a **bounded Owner repair authorization** | §6.4 + `AGENTS.md` line 14 (unrelated architecture/behavior change needs separate explicit approval) |
| Is it authorized today? | **No** | `anchor.py` absent from successor write inventory; V7 Task-7 authorization consumed; no live packet names the path |
| Does it weaken the evidence seal? | **No** | §4.2; anchored bytes/tree/parent/closed set/reread/registry/forward naming untouched |
| Does it mutate historical artifacts? | **No** | §4.2 + 0 real anchor commits MEASURED |
| Is a synthetic fixed identity an attestation risk? | **No, if** non-personal, reserved-domain, documented as synthetic | §5; D2 |
| Does it stale the A07/G02 integration-manifest pins? | **Yes — must be disclosed; no closure/promotion claim** | §6.4; pins at `generation-002:10,90`, `generation-004:31` (audit AUD-M2/M3) |
| Is a second observable change bundled? | **P1b only, independently rejectable, with its own Problem id** | §8.2; AUD-M1 |

Proposed disposition tokens for the Owner record (string values for machine-readable authority, to be confirmed by the Owner/controller):

```
PACKET:                     G0_1_4_ANCHOR_IDENTITY_PORTABILITY_REPAIR
ARCHITECTURE_DECISION_REQUIRED:  NO
FROZEN_CONTRACT_CHANGE:     NO
INTERFACE_MANIFEST_CHANGE:  NO
HISTORICAL_ARTIFACT_CHANGE: NO
EVIDENCE_SEAL_WEAKENED:     NO
REQUIRES_BOUNDED_OWNER_AUTHORIZATION: YES
```

### 10.2 Blockers (in priority order)

- **B1 — No live implementation authority.** `src/gate0/feasibility/macos_stage_b_evidence_anchor.py` is not in the successor write inventory (§6.4); V7 Task-7 authorization is consumed; `AGENTS.md` line 14 requires separate explicit approval for unrelated changes. *Resolution path:* Owner/controller issues the bounded packet in §10.4 (or explicitly assigns it as ordinary REPAIR with a recorded authority instrument). **Owner/controller action required; blocked otherwise.**
- **B2 — Lineage gap: `tests/gate0/unit/test_evidence_anchor.py` absent from main** while V7 Task 7 requires it (§6.3); the open A07 closure Problem family covers incomplete materialization. *Resolution path:* the packet includes the file (preferred for this design) **or** closure reconciliation materializes the historical file first and the packet extends it. Either way, the packet must not claim closure of the A07 problem it does not address.
- **B3 — Deviation: N3 failures report N7 code** (§4.4). *Resolution:* P1b, or explicit deferral with the deviation recorded (it is currently invisible to tests/CI).
- **B4 — Host matrix unverified.** Linux empty-GECOS and GitHub macOS runner not re-executed in this lane (`NOT_OBSERVED`). *Resolution:* the packet's acceptance must include the Linux broad CI run, which is the exact observer that failed in #194.
- **B5 — Residual portability items out of scope** (SHA-256 OID assumption at `anchor.py:21/:152/:159`; git binary version unrecorded; Windows unclaimed). *Resolution:* recorded as separate triggers (§11.3), not folded into this packet.
- **B6 — A07/G02 candidate rerun and stale pins (AUD-M2/M3).** Editing `anchor.py` makes the `5e479ab5…` pins in `generation-002`/`generation-004` historical and requires the A07 freeze rule's rerun (298-test focused set + broad). The packet must state this in its authorization and evidence record and must not claim A07/G02 closure or Gate promotion.
- **B7 — Governing authority documents live only off-main (AUD-M5).** The successor spec/plan and Task-4 amendment are non-ancestors of main; the packet and any review must cite exact blobs and must not require those documents to be merged first. H3-A05/A07 cores place `anchor.py` in a broad `write_domain` but not in `read_scope`/deliverables — broad containment is not permission (AUD-B1).
- **B8 — Test-node inventory delta.** The new `tests/gate0/unit/test_evidence_anchor.py` node IDs are outside V7's closed `G0_REV18_V7_EXPECTED_NEW_TEST_NODE_IDS_V1` inventory (§8.3); the packet must declare them or record a node-inventory delta. *Resolution:* authorize a bounded node-inventory delta in the packet record, not a plan edit.

### 10.3 What is executable *today* under existing authority

Only evidence/design work, exactly what this branch contains: read-only verification, probes in temporary repositories, probe/test/contract evidence files, this design document, and docs-only run record. No product/test/fixture edit.

### 10.4 Proposed next executable packet (for authorization)

```
PACKET:           G0_1_4_ANCHOR_IDENTITY_PORTABILITY_REPAIR (P1)
BASE:             <current synchronized main SHA at dispatch>
WRITE_PATHS (exactly 2):
  src/gate0/feasibility/macos_stage_b_evidence_anchor.py        (modify)
  tests/gate0/unit/test_evidence_anchor.py                      (create)
COMMITS (evidence-only, in order):
  P1a  feat(gate0): fix Stage-B anchor Git identity and commit encoding
  P1b  fix(gate0): classify S7 anchor failures as PREBUILD_ANCHOR_NOT_FROZEN
  P1c  test(gate0): add exact S7 anchor identity and portability regressions
FORBIDDEN:  public signature change; interface/oracle manifest change; repo .git/config write;
            timestamp pinning; seal.py/git.py/constants.py edits; spec/plan/WBS edits;
            historical artifact/receipt rewrite; real archive/model/provider/network;
            destructive Git; Gate promotion; force-push.
ACCEPTANCE: focused new test file green (RED proof captured pre-implementation);
            broad tests/gate0/unit no regression vs recorded base (814 passed locally);
            Linux broad CI green on the packet head with fixture identity left in place;
            changed-path set exactly the two paths; no .git/config or anchored-byte diff.
EVIDENCE:   run record with RED log (pre-implementation), GREEN log, broad log, CI run ids,
            diff, and the failure-code mapping table.
DISCLOSURE: P1b tracked as Problem G0-ANCHOR-N3-FAILURE-CODE-DEVIATION;
            A07/G02 integration pins become historical; rerun per A07 freeze rule;
            no A07/G02 closure, no Gate promotion, no succession reactivation;
            successor §11 write inventory is expanded for exactly these two paths only.
```

Sequencing note: P1a removes the *latent* product identity dependence — it is not a repair of a currently failing test, because #194 already repaired the fixtures and base-main CI is green; the #194 red baseline is the evidence that the dependence is real. P1b is a conformance repair; P1c is the regression lock. If the Owner wants the absolute minimum, authorize P1a+P1c and defer P1b explicitly (recording B3).

### 10.5 WBS implications (recorded, not edited here)

- WBS `G0.1.4` line 70 ("Inventory only actual missing behavior, incomplete macOS Stage-B prerequisites and source-use blockers") is the correct home for this item's *result*: a missing-behavior inventory entry (host-dependent anchor identity + N3/N7 code collapse + missing anchor test file).
- Line 71's checked broad-CI item must **not** be read as having resolved the product gap — PR #194's own body says it deliberately did not. If the Owner accepts this design, a subsequent docs-only WBS reconciliation should add a sub-bullet referencing the packet and keep the main G0.1.4 checkbox unchecked until the packet lands; no WBS checkbox advances from design alone.
- G0.3.1 depends on G0.1.4 (line 96); no dependency change is implied.

---

## 11. Rejected/deferred options, reconsideration triggers, residual risk

### 11.1 Rejected (with the lesson kept)

| Option | Why rejected | Lesson |
|---|---|---|
| B caller-supplied identity | Breaks frozen public surface; creates an authority-bypass input | Smallest fix belongs in the private hermetic leaf |
| C repo-local config write | Mutates host repo; race; pollutes later unrelated commits | Product must not write persistent host state |
| D preflight-only | Detects but does not remove host dependence | Fail-closed is a reporting property, not portability |
| E timestamp pinning | Implies a reproducibility contract that does not exist | Don't trade evidence honesty for cosmetic determinism |
| H ambient-when-present | Non-deterministic by construction | Determinism requires unconditional fixed values |
| G pinned git binary | Toolchain policy, different authority | Record as residual gap, separate packet |

### 11.2 Trade-offs accepted in P1a

- Commit author/committer no longer reflect the human/CI operator. That is *intended*: the anchor commit is synthesized by the verifier, not authored by a person, and the seal never used authorship as authority.
- Real timestamps remain, so S7 SHAs still vary run-to-run. This is *expected*: uniqueness of each anchor is a feature (same-second collisions are only mitigated by parent/tree identity), and the SHA is recorded forward, never recomputed.
- Two fixed bytes (name/email) enter evidence metadata; they are non-personal and constant, so privacy projection ("no personal value") still holds.

### 11.3 Reconsideration triggers (record; re-open design if any fires)

- **T1** Owner decides anchor commit identity must be a human/CI attestation → architecture change; fixed synthetic identity is wrong for that goal.
- **T2** Owner requires reproducible S7 SHAs independent of wall clock (e.g. cross-run byte-comparable anchor) → Alternative E requires a contract statement on commit-time semantics; separate disposition.
- **T3** A supported host is added that lacks `git` on `PATH` or uses SHA-256 object format → `_HEX40` and `PATH` assumptions break; separate portability packet.
- **T4** A real S7 anchor is created (signing/Generation B) under pre-P1a code → re-run this analysis against the new historical record before changing the writer; no rewrite, and verification stays byte-based.
- **T5** The A07 closure reconciliation materializes a historical `test_evidence_anchor.py` that conflicts with the new file → merge policy: historical file wins for its existing tests; new identity tests append; no test may be weakened.
- **T6** Git version floor matters (e.g. `A″` `GIT_CONFIG_COUNT` guard adopted) → verify runner git versions first (`NOT_OBSERVED` today).
- **T7** A newer owner authorization re-opens V7 FV5-style exact path sets for this epoch → re-check the packet's 2-path set against that receipt before dispatch.

### 11.4 Residual risk (accepted, recorded)

- The anchor-synthesizing `git` binary identity/version is still not recorded in the evidence ledger; P18a byte equality means no authority loss, but a future "toolchain attestation" goal would need G.
- Windows remains unclaimed; the design states POSIX assumptions rather than pretending portability beyond them.
- Fixed identity means commit metadata can no longer distinguish two anchors created by different operators on the same host/time; the SHA, parent, and sealed bytes remain the distinguishing evidence (and are the only evidence the seal ever used).

---

## 12. Six-cycle refinement record

The WBS's six axes (`docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md` §2) applied to this design. Full record with the wrong drafts each cycle removed: `docs/agent-runs/run-20261025-g0-1-4-git-anchor-portability/SIX_CYCLE_REFINEMENT.md`.

| Cycle | What the first draft got wrong | Refined position |
|---|---|---|
| 1 — Product scope | "Fix the identity so CI goes green" — a test-infrastructure framing | Evidence-authority design: identity determinism **plus** an explicit separation of P1a (identity/encoding), P1b (failure-class conformance), timestamp determinism deliberately out of scope |
| 2 — Repository evidence | Assumed the V7 Task-7 anchor test existed on main and that FV5 was a live lock; assumed documented anchor SHAs existed | Measured the opposite: test file absent from canonical history (never committed, no deletion commit), no live FV5 enforcer, zero real anchor commits/SHAs anywhere (`evidence/probe-identity.md` scenario h) |
| 3 — Dependencies and authorization | "Small ordinary bugfix under G0.1.4" | Path absent from the live successor write inventory; V7 Task-7 authorization consumed; bounded Owner packet required (B1); A07 closure Problem family recorded (B2, B3) |
| 4 — Parallelism and ownership | One lane reading everything and one long narrative | Four independent lanes with disjoint write scopes (probe, authority audit, test matrix, adversarial review), Lead as sole integrator, docs-only branch, zero product/test writes |
| 5 — Failure/safety | Draft options that would have mutated the repo, broken the interface, or implied a reproducibility contract | Rejected repo-config writes (C), public identity parameter (B), timestamp pinning (E), ambient-when-present (H); kept fail-closed diagnostics and byte-level evidence preservation; no historical artifact touched |
| 6 — Execution simulation | "Apply the fix and open a PR" | Simulated the authorized packet: synced base → RED proof on current code → P1a → focused + broad suite → Linux broad CI (the exact observer that failed in #194) → P1b/P1c → 2-path changed-set check → rollback path; WBS annotation only after merge, never from design alone |

---

## 13. Evidence inventory and review

| Artifact | Purpose | Class |
|---|---|---|
| `docs/agent-runs/run-20261025-g0-1-4-git-anchor-portability/README.md` | Run record, base/head SHAs, commands, disposition | MEASURED |
| `.../evidence/probe-identity.md` | Identity/timestamp/encoding/history probe, sanitized | MEASURED |
| `.../evidence/probe-script.py` | Reproducible probe (stdlib + product import), sha256 `0fb8969d4aac02c293bb1acc6fe6c0f79465c440b4e6e7a83a112ecb8badfdae` | MEASURED |
| `.../evidence/probe-raw/{probe-run.log,baseline-pytest.log,environment.log}` | Raw logs (note: `baseline-pytest.log` is the **probe's 18-node** baseline, not the 814-node broad suite) | MEASURED |
| `.../evidence/authority-audit.md` | Frozen-contract/authority audit by an independent lane (244 lines; verdicts Q1–Q7, findings AUD-B1/AUD-M1–M6); reconciled in §6.8 | MEASURED/MATCHED |
| `.../evidence/red-test-matrix.md` | RED/GREEN test matrix with expected failure modes | EDITORIAL_INFERENCE (proposed tests, none implemented) |
| `.../evidence/broad-baseline-20261025.log` | Broad `tests/gate0/unit` rerun at base (814 nodes) | MEASURED |
| `.../SIX_CYCLE_REFINEMENT.md` | Six-cycle refinement record | MEASURED + EDITORIAL_INFERENCE |
| `.../evidence/independent-review.md` | **External** adversarial review by a separate lane (22 findings: 0 blocker / 6 major / 12 minor / 4 nit; verdict `PARTIALLY_VERIFIED`); not this design's own evidence; every finding reconciled in §13.1 | MATCHED (review record) |
| `.../evidence/verification-20261025.log` | Re-executed fact checks: blob hashes, commit 3598c8e4f/parent, test-file absence at base, off-main file blob, non-ancestor refs, failure-code producer grep, identity-requirement grep, zero anchor-message commits, docs-only tree status | MEASURED |

### 13.1 Independent-review reconciliation

The review lane returned **PARTIALLY_VERIFIED** (0 blocker, 6 major, 12 minor, 4 nit) and independently reproduced the 814-passed local baseline, the PR #194/CI facts, the successor §11 exclusion, V7 base non-ancestry, zero anchor commits, and that P18a/P18b/P18c, generation identity, and N4B seal propagation are unaffected. Disposition of every finding:

| Finding | Disposition in this revision |
|---|---|
| MAJOR 1 — inverted `_git_input` manifest citation | Corrected: `_git_input` has **no** manifest entry (grep 0); manifested surfaces restated (§3.3, §6.5) |
| MAJOR 2 — P1b under-specified vs shared N4B leaf | Corrected: `_git_input` semantics unchanged; S7-only wrap route, N4B non-regression test required (§8.2) |
| MAJOR 3 — flaky byte-identical SHA locks | Corrected: structural equality; SHA only within a bracketed same-second window, nondeterminism stated (§8.4, §9) |
| MAJOR 4 — false "PR opened" claim | Corrected: run record now describes the true pre-push state; PR number/head recorded by a follow-up commit after opening |
| MAJOR 5 — over-attributed CI repair | Corrected: P1a removes latent dependence; #194 repaired the fixture; base CI is green (§8.4, §10.4, run record) |
| MAJOR 6 — verification-log grep citation | Corrected: log now records both patterns with return codes; distinction explained (§6.1) |
| MINOR — baseline artifact, host version, helper span, ambient-leak wording, duplicate sentence, removal of the per-call-site fallback, Appendix B commands, evidence classes, crosswalk, extra alternatives, literal-set ownership, id warning | All applied in this revision |

**Verification performed for this document:** base SHA equality, blob hashes for every cited spec/plan, grep-based contract absence (both narrow and broad patterns recorded with return codes), local broad suite (814 passed at base), probe scenarios a–h, `git log --all` lineage checks, `gh` PR/CI state, and a rerun of every high-leverage check in `evidence/verification-20261025.log` after review corrections. No claim is marked `VERIFIED` unless a cited artifact/command supports it; unobserved host behavior is `NOT_OBSERVED`.

---

## Appendix A — proposed constants (exact strings, owner-confirmable)

```
GIT_AUTHOR_NAME      = "Gate-0 Evidence Anchor"
GIT_AUTHOR_EMAIL     = "gate0-evidence-anchor@example.invalid"
GIT_COMMITTER_NAME   = "Gate-0 Evidence Anchor"
GIT_COMMITTER_EMAIL  = "gate0-evidence-anchor@example.invalid"
argv prefix          = ("-c", "i18n.commitEncoding=UTF-8")
```

`example.invalid` uses the RFC 2606 reserved `.invalid` TLD with the RFC 2606 `example` second-level label, matching the repository's existing synthetic-identity precedent (`test@example.invalid`): syntactically valid, non-deliverable, and unambiguous that this is a synthetic container identity. The independent test-matrix lane proposes equivalent placeholder literals (`Gate 0 S7 anchor` / `anchor@gate0.invalid`). Exact strings remain owner-confirmable, but the authorizing packet must carry **exactly one** chosen literal set — this design deliberately does not authorize its own proposal — and author and committer must be identical. Values are `str`, ASCII-only, deterministic across hosts and Python versions, and contain no personal data.

## Appendix B — commands used for the cited measurements

```bash
# base / PR / CI state
git fetch --prune origin && git rev-parse origin/main
gh pr view 194 --json state,mergedAt,mergeCommit,headRefOid,baseRefOid
gh run list --branch main --limit 8 --json databaseId,name,conclusion,headSha

# frozen blob hashes (path -> blob OID at the pinned base)
git rev-parse 078fd6f4b:docs/superpowers/specs/2026-09-20-gate0-recovery-evidence-dag-design.md   # 21e65150...
git rev-parse 078fd6f4b:docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md  # aad90adf...

# contract absence (exact command + rc recorded in evidence/verification-20261025.log;
# full pattern as used by the authority audit, evidence/authority-audit.md:60-62)
git grep -nE "GIT_AUTHOR|GIT_COMMITTER|commit-tree|author identity|committer identity|user\.email|git identity" 078fd6f4b -- \
  docs/superpowers/specs/2026-09-20-gate0-recovery-evidence-dag-design.md \
  docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md   # rc 1 (no matches)

# manifest entry absence (rc 1)
git grep -c "_git_input" 078fd6f4b -- tests/gate0/unit/evidence_dag_interface_manifest.py

# required Task-7 test absent at base (rc 128); present off-main (rc 0)
git cat-file -e 078fd6f4b:tests/gate0/unit/test_evidence_anchor.py
git cat-file -e 3683eaf25:tests/gate0/unit/test_evidence_anchor.py   # blob 18c3f189...

# local broad suite (worktree at base)
PYTHONPATH=.:src .venv-gate0/bin/python -m pytest -q tests/gate0/unit   # 814 passed

# probe
.venv-gate0/bin/python docs/agent-runs/run-20261025-g0-1-4-git-anchor-portability/evidence/probe-script.py
```
