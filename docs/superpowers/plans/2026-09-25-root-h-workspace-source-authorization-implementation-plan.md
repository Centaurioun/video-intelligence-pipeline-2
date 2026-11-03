# Root H Workspace Source Authorization Implementation Plan

> **SUPERSEDED — 2026-10-24 Owner decision.** This plan's fail-closed
> source-authorization enforcement was removed by explicit Owner decision; see
> [ADR-0003](../../decisions/ADR-0003-development-source-authorization-enforcement-removed.md).
> `scripts/verify-workspace.sh` now reports
> `DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER`. The plan body is
> preserved unchanged below as historical audit evidence and must not be executed.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the stale hard-coded Gate-0-only source allowlist in `scripts/verify-workspace.sh` with a fail-closed source-authorization check that derives permitted `src` paths mechanically from owner/admin authority and classifies every relevant path deterministically.

**Architecture:** One product artifact, one test artifact. `scripts/verify-workspace.sh` keeps its existing structure, its existing `[--require-pushed]` operational CLI, and every unrelated check semantics-preserved. Its single source-boundary block (currently the `find src … -print -quit` check) is replaced by one embedded Python block delimited by stable sentinel comments. That Python block resolves the fixed canonical admin trust root through local Git, validates the authority chain and every runtime-declared digest, validates amendment records, resolves cited preimages by **exact blob identity**, preserves **source-local** observed-path/domain pairing, resolves a **real** positive current-write chain, enumerates `src` NUL-safely, classifies each path, and reports stable machine-readable lines.

**Tech Stack:** Bash 5, POSIX `git` plumbing (`rev-parse`, `ls-tree`, `ls-files`, `cat-file`, `hash-object`, `update-index`, `write-tree`, `commit-tree`, `mktree`), Python 3 standard library only (`json`, `os`, `re`, `subprocess`, `sys`, `hashlib`). `pytest` is optional: the test file is a plain Python module runnable directly with `python3`. No new dependencies, no network.

**Spec:** `docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md`

```
PLAN_APPROVAL_DOES_NOT_AUTHORIZE_IMPLEMENTATION.
A separate explicit owner implementation authorization is mandatory.
The exact Root-H test-path allocation is ownership only, not write authority.
IMPLEMENTATION_AUTHORIZED=false
```

## Global Constraints

- Authorized future write surfaces are exactly two paths, and no others:
  - product: `scripts/verify-workspace.sh`
  - test: `tests/scripts/test_verify_workspace_source_authorization.py`
- Do not create helper Python product files, new schemas, new config, new manifests, README edits, governance files, or any other test file.
- Operational CLI stays exactly `verify-workspace.sh [--require-pushed]`. No new flags.
- No environment variable may change any authority input (admin ref, root identity, manifest path, authority record path, freshness).
- No alternate authority-ref seam. The canonical ref name is a frozen constant used literally by the tests.
- No network access inside the verifier. Never invoke a real `gh` in tests; every temp-repo execution prepends the deterministic `gh` shim to `PATH`.
- Frozen authority constants: canonical ref `execution/execution-portfolio-20260924-v1/bootstrap`; supported base schema `portfolio-authority-normalization.v1`; supported base record type `OWNER_AUTHORIZED_PORTFOLIO_AUTHORITY_NORMALIZATION`; required base status `OWNER_AUTHORIZED`; supported amendment schema `portfolio-authority-normalization-amendment.v1`; supported amendment type `OWNER_AUTHORIZED_AUTHORITY_NORMALIZATION_AMENDMENT`; baseline commit `d3b477db97541d7cd2775e7c42381eb4875de519`; baseline subtree SHA `581fea73d4fc772e2f3a11d5e450951cbe2793ed`; baseline path count `88`.
- `UNAUTHORIZED` for any path, and any denial, contributes to the overall `FAIL`. Never engineer overall `EXIT 0`.
- Approved spec blob: `14a0419091a88282059b7e4fa345a13f2e91e0d8`.
- Reviewed script baseline blob: `7b681fd60408b39b48f15f148e4247a142865b20`.
- Root-H test-path allocation (ownership only, not write authority): `.orchestration/portfolios/execution-portfolio-20260924-v1/authority/root-h-test-path-allocation-20260925-v1.json` blob `2359336adb2e4b0f434a206edc16bcfd1897595f`.
- Preserve every unrelated verifier check semantically: branch-is-`main`, reference-pack integrity/materialization, prototype `.env.local`, secret scan/handling, `gh`/network/auth, required-path presence, memo counts, report-integrity hash, spec lifecycle, evidence taxonomy, sampling arithmetic, decision register.
- Implementation remains unauthorized until a separate explicit owner authorization names the exact start SHA and plan blob.

## Review Focus

Each item names the most likely failure mode and the task that owns its test.

1. **Forged local trust input** — a caller redirects authority by flag or environment. Expected: no such surface; authority is always the fixed canonical ref. → Task 1 (GUARD), Task 7.
2. **Stale or mismatched digest chain** — the manifest names a record blob that is not present, an amendment blob mismatch, or an amendment that internally amends a different base. Expected: `DENY`. → Task 1, Task 3.
3. **Cited preimage resolved by mutable path instead of blob identity** — a citation is read from `commit:path` after the path advanced or vanished. Expected: read by exact cited `blob_sha`; path is diagnostic only. → Task 1, Task 3.
4. **Cross-source authority cross-product** — an observed path from source A validated against a domain from source B. Expected: source-local pairing only. → Task 3.
5. **Broad historical domain becoming a future grant** — a new tracked file inside an old glob is treated as legitimately present. Expected: `UNAUTHORIZED` unless it is an exact member of that same source's observed set **and** inside that same source's cited domain. → Task 3, Task 4.
6. **Untracked path rescued by another predicate** — untracked file whose name matches a baseline path or lies in an authorized domain slips through. Expected: untracked always `UNAUTHORIZED`, even when the name is a frozen-baseline member. → Task 3, Task 4.
7. **Invented current-authority shape** — a synthetic permissive field combination is treated as positive authority. Expected: only real owner-record shapes prove current write; absence is `NOT TRUE`. → Task 5, Task 6.
8. **Empty derived authority reported as PASS** — no admissible authority derived, yet the boundary passes because nothing happened to be enumerated. Expected: `DENY`. → Task 3, Task 4.
9. **Hostile filename corrupting report or parsing** — newline/space/glob/leading-dash path breaks the report. Expected: JSON-escaped rendering, no word splitting, complete scan. → Task 3, Task 4.
10. **Unrelated verifier behavior accidentally changed, or a real `gh` invoked in tests** — the rewrite weakens another check, or a test reaches the network. Expected: checks byte-for-byte semantically unchanged; every test uses the fake `gh` shim. → Task 7.

---

## File Structure

| Path | Responsibility |
| --- | --- |
| `scripts/verify-workspace.sh` (modify) | Unchanged: argv parsing, all unrelated checks, aggregate `failures` counter, `pass`/`fail` helpers. Changed: the single source-boundary block is replaced by one embedded Python block delimited by stable sentinel comments. |
| `tests/scripts/test_verify_workspace_source_authorization.py` (create) | The only test artifact. Builds temporary Git repositories carrying the literal canonical bootstrap ref plus synthetic authority records that mirror real supported shapes, runs the script-under-test in those repositories with a fake `gh` shim, and asserts classification and reporting. Stdlib only; runnable via `pytest` or `python3 <file>`. |

No third file.

## Reporting Contract (frozen; tests parse only these lines)

```
SOURCE-AUTH admin-commit=<commit-sha>
SOURCE-AUTH base-record=<blob-sha>
SOURCE-AUTH amendment<n>=<blob-sha>            (one per manifest-listed amendment)
SOURCE-AUTH amendment<n>-record=<blob-sha>     (actual loaded record blob)
SOURCE-AUTH frozen-tree=<tree-sha>
SOURCE-AUTH baseline-paths=<n>
SOURCE-AUTH post-baseline-paths=<n>
SOURCE-AUTH current-root-identity=<RESOLVED:root-id|NOT_OBSERVED|AMBIGUOUS>
SOURCE-AUTH current-write-root=<root-id|NONE>
SOURCE-AUTH remote-freshness=NOT_OBSERVED
SOURCE-AUTH unauthorized-count=<n>
SOURCE-AUTH DENY reason=<reason>               (denial only, replaces the block above)
SOURCE-AUTH path=<json-escaped-path> class=<AUTHORIZED_HISTORICAL|AUTHORIZED_CURRENT|UNAUTHORIZED>   (sorted)
```

Denials also emit through the existing `fail()` helper. Path text is rendered with
`json.dumps(path)` in both the report line and the `FAIL` line so that newlines,
spaces, glob characters and leading dashes cannot corrupt structure or be misread as
options. No new artifact and no new schema.

---

### Task 0: Read-only execution preflight (no files written)

**Files:**
- Read: `docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md`
- Read: `docs/superpowers/plans/2026-09-25-root-h-workspace-source-authorization-implementation-plan.md`
- Read: `scripts/verify-workspace.sh`

**Interfaces:**
- Consumes: nothing.
- Produces: a recorded `AUTHORIZED_IMPLEMENTATION_START_SHA`, supplied by the separate owner implementation authorization.

This task writes nothing. It is the gate that stops implementation from starting on a stale or ungranted base.

- [ ] **Step 1: Confirm the separate owner implementation authorization exists**

It must name verbatim: the exact final implementation start SHA, the approved spec blob, this plan's approved blob, and the two authorized write surfaces. If it does not exist, STOP. Do not infer authority.

- [ ] **Step 2: Confirm the start SHA**

```bash
git rev-parse HEAD
# must equal the AUTHORIZED_IMPLEMENTATION_START_SHA named by the owner authorization
```

- [ ] **Step 3: Confirm the historical root base is still an ancestor**

```bash
git merge-base --is-ancestor d3b477db97541d7cd2775e7c42381eb4875de519 HEAD && echo "ANCESTOR_OK"
```

- [ ] **Step 4: Confirm the approved spec blob is unchanged**

```bash
git rev-parse HEAD:docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md
# must equal 14a0419091a88282059b7e4fa345a13f2e91e0d8
```

- [ ] **Step 5: Confirm the approved plan blob is unchanged**

```bash
git rev-parse HEAD:docs/superpowers/plans/2026-09-25-root-h-workspace-source-authorization-implementation-plan.md
# must equal the plan blob named by the owner implementation authorization
```

- [ ] **Step 6: Confirm the script target is still the plan-reviewed baseline**

```bash
git rev-parse HEAD:scripts/verify-workspace.sh
# must equal 7b681fd60408b39b48f15f148e4247a142865b20
# unless the owner authorization explicitly names a later reviewed blob
```

- [ ] **Step 7: Confirm the test-path allocation is still remotely durable**

```bash
git fetch --prune origin
git rev-parse origin/execution/execution-portfolio-20260924-v1/bootstrap:.orchestration/portfolios/execution-portfolio-20260924-v1/authority/root-h-test-path-allocation-20260925-v1.json
# must equal 2359336adb2e4b0f434a206edc16bcfd1897595f
```

- [ ] **Step 8: Confirm the canonical admin ref resolves locally and the worktree is clean**

```bash
git rev-parse 'execution/execution-portfolio-20260924-v1/bootstrap^{commit}'
git status --porcelain=v1    # must be empty
```

- [ ] **Step 9: Record the preflight result**

Record the observed values of Steps 2-8 in the run ledger. No commit is made by this task.

---

### Task 1: Harness + RED authority trust-root, digest, and amendment-integrity tests

**Files:**
- Create: `tests/scripts/test_verify_workspace_source_authorization.py`
- Test: `tests/scripts/test_verify_workspace_source_authorization.py`

**Interfaces:**
- Consumes: nothing.
- Produces (used by every later task):
  - `SCRIPT_PATH`, `REPO_ROOT`, `CANONICAL_REF`, `SANDBOX`
  - `make_repo() -> str`
  - `run(repo, *args, env=None, input=None, check=True) -> subprocess.CompletedProcess`
  - `must(repo, *args, env=None, input=None) -> str`
  - `git_env(extra_index=None) -> dict`
  - `temp_index() -> str`
  - `write_tree_from_files(repo, files: dict[str, str]) -> str` — nested tree object without touching the repo index or worktree; returns the tree OF those files (the `src` subtree when passed `src` contents)
  - `tree_listing(repo, tree) -> tuple[list[str], list[str]]` — `(tree_relative, repo_relative)` derived from real `git ls-tree`, asserted free of `src/src/`
  - `listing_digest(lines: list[str]) -> str`
  - `commit_isolated(repo, paths: list[str], message: str) -> str` — commit from a temp index without touching HEAD
  - `empty_tree(repo) -> str`
  - `json_text(obj) -> str` — the single JSON serialization contract (`json.dumps(obj, indent=2, sort_keys=True) + "\n"`)
  - `write_json_file(repo, relpath: str, obj) -> None` — serializes via `json_text`
  - `write_json_blob(repo, obj) -> str` — serializes via `json_text`, writes with `-w`, returns the blob SHA
  - `write_blob(repo, content: str) -> str` — text blob writer used by `write_json_blob`
  - `install_script(repo) -> str`
  - `fake_gh_dir(repo) -> str`
  - `run_script(repo, *args: str) -> tuple[int, str, str]` — always prepends the fake `gh` shim
  - `parse_report(stdout: str) -> dict`
  - `classes(stdout: str) -> dict`
  - `build_authority(repo, **kwargs) -> dict` — builds a complete, internally consistent synthetic authority tree and optionally creates the canonical ref
  - `track(repo, relpath, content="x\n") -> None`, `untracked(repo, relpath, content="x\n") -> None`
  - `post_baseline_source(...)`, `positive_root_slot(...)`, `load_authority_for_test(repo)`, `goal_dir_for(root_id)` fixture helpers

- [ ] **Step 1: Write the failing test file**

Create `tests/scripts/test_verify_workspace_source_authorization.py` with exactly this content.

```python
"""Root H source-authorization tests.

Stdlib only. Runnable as ``pytest tests/scripts/test_...py`` or directly as
``python3 tests/scripts/test_verify_workspace_source_authorization.py``.

Every test builds a temporary Git repository carrying the LITERAL canonical
bootstrap/admin ref. No alternate authority-ref seam exists, so tests exercise
the same fixed trust-root name used operationally.

No test may invoke a real ``gh``. Every temp-repo script execution prepends the
deterministic ``gh`` shim to ``PATH``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT_PATH = os.path.join(REPO_ROOT, "scripts", "verify-workspace.sh")

CANONICAL_REF = "execution/execution-portfolio-20260924-v1/bootstrap"
MANIFEST_REL = ".orchestration/portfolios/execution-portfolio-20260924-v1/manifest.json"
AUTH_DIR = ".orchestration/portfolios/execution-portfolio-20260924-v1/authority"
BASE_RECORD_NAME = "source-presence-and-g-test-ownership-normalization-20260925-v1.json"
AMENDMENT_NAME = "root-g-test-path-scope-amendment-20260925-v1.json"

BASE_SCHEMA = "portfolio-authority-normalization.v1"
BASE_TYPE = "OWNER_AUTHORIZED_PORTFOLIO_AUTHORITY_NORMALIZATION"
STATUS_OK = "OWNER_AUTHORIZED"
AMEND_SCHEMA = "portfolio-authority-normalization-amendment.v1"
AMEND_TYPE = "OWNER_AUTHORIZED_AUTHORITY_NORMALIZATION_AMENDMENT"

H_ROOT = "root-workspace-verifier-authorization"
H_BRANCH = "execution/execution-portfolio-20260924-v1/workspace-verifier-authorization"
G0_ROOT = "root-g0-rev18"
G0_BRANCH = "execution/execution-portfolio-20260924-v1/g0-rev18"
D_ROOT = "root-editorial-pipeline-generalization"
D_BRANCH = "execution/execution-portfolio-20260924-v1/editorial-pipeline"

PACKET_SCHEMA = "execution-root-task-packet.v1"
EXPANSION_SCHEMA = "portfolio-root-expansion-authorization.v1"
EXPANSION_TYPE = "OWNER_AUTHORIZED_ROOT_EXPANSION"
EXPANSION_PORTFOLIO = "execution-portfolio-20260924-v1"

SANDBOX: list[str] = []


# --------------------------------------------------------------------------
# low-level git helpers
# --------------------------------------------------------------------------
def run(repo, *args, env=None, input=None, check=True):
    p = subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True,
        env=env, input=input,
    )
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {p.stderr}")
    return p


def must(repo, *args, env=None, input=None):
    return run(repo, *args, env=env, input=input).stdout.strip()


def git_env(extra_index=None):
    env = dict(os.environ)
    if extra_index:
        env["GIT_INDEX_FILE"] = extra_index
    return env


def temp_index():
    fd, path = tempfile.mkstemp(prefix="rootsrc-idx-")
    os.close(fd)
    os.unlink(path)
    return path


def empty_tree(repo):
    return must(repo, "hash-object", "-w", "-t", "tree", "/dev/null")


def write_tree_from_files(repo, files):
    """Build a nested tree object from {relpath: content}.

    Uses a temporary index so neither the repository index nor the working tree
    is touched. Handles nested paths recursively.

    The returned tree IS the tree of `files` at that nesting level. When the
    caller passes the contents of `src`, the result is the `src` SUBTREE object
    itself, which is exactly what `frozen_baseline.subtree_tree_sha` must hold.
    """
    index = temp_index()
    env = git_env(index)
    try:
        run(repo, "read-tree", empty_tree(repo), env=env)
        for path, content in files.items():
            # -w is REQUIRED. `hash-object` without -w only computes a SHA and
            # never writes the object, so a later `cat-file -e <sha>` fails.
            blob = run(repo, "hash-object", "-w", "--stdin", input=content,
                       env=env).stdout.strip()
            run(repo, "update-index", "--add", "--cacheinfo",
                f"100644,{blob},{path}", env=env)
        return must(repo, "write-tree", env=env)
    finally:
        if os.path.exists(index):
            os.unlink(index)


def tree_listing(repo, tree):
    """Return (tree_relative_names, repo_relative_names) from REAL ls-tree.

    `tree` must be the `src` SUBTREE object. Tree-relative names are therefore
    already `src`-relative (e.g. `gate0/a.py`), and prepending exactly one
    `src/` yields the repo-relative form (e.g. `src/gate0/a.py`).
    """
    rel, repo_rel = [], []
    for line in must(repo, "ls-tree", "-r", tree).splitlines():
        meta, name = line.split("\t", 1)
        if meta.split()[0] != "100644":
            continue
        rel.append(name)
        repo_rel.append("src/" + name)
    assert not any(n.startswith("src/") for n in rel), (
        "frozen baseline subtree must be the src SUBTREE, not a parent tree "
        f"containing an src entry: {rel}"
    )
    assert not any(n.startswith("src/src/") for n in repo_rel), repo_rel
    return rel, repo_rel


def listing_digest(lines):
    return hashlib.sha256("".join(n + "\n" for n in lines).encode()).hexdigest()


def commit_isolated(repo, paths, message):
    """Commit only `paths` from a temporary index; HEAD and the worktree index
    are untouched. Returns the created commit SHA."""
    index = temp_index()
    env = git_env(index)
    try:
        run(repo, "read-tree", empty_tree(repo), env=env)
        run(repo, "add", "--", *paths, env=env)
        tree = must(repo, "write-tree", env=env)
    finally:
        if os.path.exists(index):
            os.unlink(index)
    cenv = git_env()
    cenv.update({
        "GIT_AUTHOR_NAME": "Root H Tests", "GIT_AUTHOR_EMAIL": "root-h@example.invalid",
        "GIT_COMMITTER_NAME": "Root H Tests", "GIT_COMMITTER_EMAIL": "root-h@example.invalid",
    })
    return run(repo, "commit-tree", tree, "-m", message, env=cenv).stdout.strip()


def json_text(obj):
    """THE single JSON serialization contract for this harness.

    `write_json_file` and `write_json_blob` must both serialize through this
    function so that a file's bytes and its blob bytes are identical for the
    same object.
    """
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def write_blob(repo, content):
    """Write a text blob and return its SHA. `content` must be `str`."""
    return run(repo, "hash-object", "-w", "--stdin", input=content).stdout.strip()


def write_json_file(repo, relpath, obj):
    full = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(json_text(obj))


def write_json_blob(repo, obj):
    """Serialize `obj` with `json_text` and write it as a real Git blob.

    Accepts a JSON-compatible Python object, never a pre-serialized string, and
    always writes with `-w` so the object is genuinely present in the object
    database.
    """
    return write_blob(repo, json_text(obj))


def _tmp():
    d = tempfile.mkdtemp(prefix="rootsrc-")
    SANDBOX.append(d)
    return d


def make_repo():
    repo = _tmp()
    run(repo, "init", "-q", "-b", "main", ".")
    must(repo, "config", "user.email", "root-h@example.invalid")
    must(repo, "config", "user.name", "Root H Tests")
    run(repo, "commit", "-q", "--allow-empty", "-m", "base")
    return repo


def track(repo, relpath, content="x\n"):
    full = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(content)
    run(repo, "add", "--", relpath)


def untracked(repo, relpath, content="x\n"):
    full = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(content)


def install_script(repo):
    dest = os.path.join(repo, "scripts", "verify-workspace.sh")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(SCRIPT_PATH, dest)
    os.chmod(dest, 0o755)
    return dest


def fake_gh_dir(repo):
    d = os.path.join(repo, ".fakebin")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "gh")
    with open(p, "w") as fh:
        fh.write(
            "#!/usr/bin/env bash\n"
            "case \"$*\" in\n"
            "  *\"repo view\"*) printf '%s\\n' "
            "'{\"isPrivate\":true,\"visibility\":\"PRIVATE\","
            "\"defaultBranchRef\":{\"name\":\"main\"},\"url\":\"https://example.invalid/r\"}' ;;\n"
            "  *) exit 1 ;;\n"
            "esac\n"
        )
    os.chmod(p, 0o755)
    return d


def run_script(repo, *args):
    script = install_script(repo)
    env = git_env()
    env["PATH"] = fake_gh_dir(repo) + os.pathsep + env.get("PATH", "")
    p = subprocess.run(["bash", script, *args], capture_output=True, text=True,
                       cwd=repo, env=env)
    return p.returncode, p.stdout, p.stderr


def parse_report(stdout):
    out = {"paths": {}}
    for line in stdout.splitlines():
        if not line.startswith("SOURCE-AUTH "):
            continue
        body = line[len("SOURCE-AUTH "):]
        if body.startswith("path="):
            m = re.match(r'^path=(".*") class=([A-Z_]+)$', body)
            if m:
                out["paths"][json.loads(m.group(1))] = m.group(2)
            continue
        key, _, value = body.partition("=")
        out[key] = value
    return out


def classes(stdout):
    return parse_report(stdout)["paths"]


def post_baseline_source(source_id, observed, domains, *, pointer="/values"):
    """One post-baseline source entry with a self-consistent citation."""
    return {
        "source_id": source_id,
        "observed_src_paths_beyond_baseline": list(observed),
        "_domains": list(domains),
        "_pointer": pointer,
    }


def positive_root_slot(root_id, branch, domains, *, witness_blob=None,
                       owner_on=None, authorization_ref=None):
    """A root slot mirroring a REAL positive-authority shape.

    Two supported archetypes exist in current authority data:
      * task-packet witness: slot carries `gate0_authority`
        `owner_implementation_authorization_blob` that must also appear in the
        process authority index;
      * task-packet marker: packet carries `authorized_by_owner_on` plus a
        resolvable `authorization_ref`.
    """
    slot = {"root_id": root_id, "root_branch": branch}
    if witness_blob is not None:
        slot["gate0_authority"] = {
            "owner_implementation_authorization_blob": witness_blob,
        }
    packet = {
        "schema_version": "execution-root-task-packet.v1",
        "root_id": root_id,
        "root_branch": branch,
        "exclusive_write_paths_or_domains": list(domains),
    }
    if owner_on is not None:
        packet["authorized_by_owner_on"] = owner_on
    if authorization_ref is not None:
        packet["authorization_ref"] = authorization_ref
    return slot, packet


def build_authority(
    repo,
    *,
    baseline_files=None,
    sources=None,
    root_slots=None,
    task_packets=None,
    amendments=0,
    amend_ordinals=None,
    base_schema=BASE_SCHEMA,
    base_type=BASE_TYPE,
    base_status=STATUS_OK,
    amend_schema=AMEND_SCHEMA,
    amend_type=AMEND_TYPE,
    amend_status=STATUS_OK,
    digest_mismatch_base=False,
    digest_mismatch_amendment=False,
    manifest_link_mismatch=False,
    record_link_mismatch=False,
    manifest_amend_schema_mismatch=False,
    manifest_amend_type_mismatch=False,
    manifest_amend_record_id_mismatch=False,
    manifest_amend_ordinal_mismatch=False,
    manifest_amend_missing_ordinal=False,
    pointer_mismatch=False,
    citation_path_changed=False,
    citation_path_removed=False,
    citation_blob_missing=False,
    source_missing_citation=False,
    membership_semantics="EXACT_PATH_MEMBERSHIP_IN_FROZEN_GIT_TREE",
    wildcard_future_grant=False,
    path_count_delta=0,
    tree_missing=False,
    digest_corrupt=False,
    create_ref=True,
    denial_roots=None,
    process_index_blob=None,
    current_authority_roots=None,
    extra_files=None,
):
    """Build a synthetic authority tree mirroring real supported shapes.

    Returns the manifest dict.

    `extra_files` is a {relpath: obj} mapping of additional authority
    documents to write and commit with the same commit (for example an owner
    expansion authorization record referenced by a task packet).
    `amend_ordinals` overrides the synthetic amendment ordinals so that
    duplicate and non-monotonic cases can be built.
    """
    baseline_files = baseline_files or {}
    sources = sources or []
    root_slots = list(root_slots or [])
    task_packets = dict(task_packets or {})
    extra_files = dict(extra_files or {})

    # --- authority files (written to disk; committed via a temp index) ------
    auth_paths = []
    for relpath, obj in extra_files.items():
        write_json_file(repo, relpath, obj)
        auth_paths.append(relpath)

    # H-P2-1: the frozen baseline field holds the `src` SUBTREE object, i.e.
    # the tree OF the src contents, never a parent tree containing an `src`
    # entry. `tree_listing` asserts this, so an `src/src/...` regression fails
    # the test run immediately.
    if tree_missing:
        tree = "0" * 40
        rel, repo_rel = [], []
    else:
        tree = write_tree_from_files(repo, baseline_files)
        rel, repo_rel = tree_listing(repo, tree)
    rel_dg = listing_digest(rel)
    repo_dg = listing_digest(repo_rel)
    if digest_corrupt:
        repo_dg = "0" * 64

    # process authority index (only when a task-packet-witness chain is used)
    index_path = f"{AUTH_DIR}/process-authority-refs.json"
    if process_index_blob is not None:
        write_json_file(repo, index_path, process_index_blob)
        auth_paths.append(index_path)

    # post-baseline sources
    source_entries = []
    for spec in sources:
        observed = list(spec["observed_src_paths_beyond_baseline"])
        domains = list(spec.get("_domains", []))
        if source_missing_citation:
            source_entries.append({
                "source_id": spec["source_id"],
                "observed_src_paths_beyond_baseline": observed,
            })
            continue
        domain_doc = {"values": domains if not pointer_mismatch else ["src/__mismatch__/"]}
        dom_path = f"{AUTH_DIR}/domain-{spec['source_id']}.json"

        # H-P3-2: `citation_blob_missing` simulates an EXACT OBJECT that is
        # absent. The provenance path still exists and commits normally; it is
        # not authority, so it must not rescue the missing blob.
        if citation_blob_missing:
            cited_blob = "f" * 40
            # check=False is REQUIRED: `run` raises on a non-zero git exit by
            # default, so an absent object must be probed with check=False.
            assert run(repo, "cat-file", "-e", cited_blob + "^{blob}",
                       check=False).returncode != 0, (
                "the missing-blob fixture must choose an object id that is absent"
            )
            write_json_file(repo, dom_path, domain_doc)
            auth_paths.append(dom_path)
        else:
            # H-P2-2: create the ORIGINAL document and freeze its blob SHA as
            # the citation identity. `write_json_blob` writes with -w, so the
            # object is genuinely present in the object database.
            cited_blob = write_json_blob(repo, domain_doc)
            write_json_file(repo, dom_path, domain_doc)
            auth_paths.append(dom_path)

            if citation_path_changed:
                # POSITIVE GUARD: the branch-relative path advances to DIFFERENT
                # content while the citation keeps the ORIGINAL blob.
                changed_doc = {"values": ["src/__changed__/"]}
                current_path_blob = write_json_blob(repo, changed_doc)
                write_json_file(repo, dom_path, changed_doc)
                assert current_path_blob != cited_blob, (
                    "path-change fixture must produce a different blob than the "
                    "cited blob, otherwise it does not exercise exact-blob identity"
                )
            if citation_path_removed:
                # POSITIVE GUARD: the provenance path disappears entirely while
                # the exact cited blob remains available. The path must also be
                # dropped from auth_paths or `commit_isolated` would fail on a
                # deleted path before the resolver ever runs.
                os.unlink(os.path.join(repo, dom_path))
                auth_paths = [p for p in auth_paths if p != dom_path]
                assert not os.path.exists(os.path.join(repo, dom_path))
                assert run(repo, "cat-file", "-e", cited_blob + "^{blob}",
                           check=False).returncode == 0

        source_entries.append({
            "source_id": spec["source_id"],
            "observed_src_paths_beyond_baseline": observed,
            "recorded_write_domain_citation": {
                "path": dom_path,
                "blob_sha": cited_blob,
                "json_pointer": spec.get("_pointer", "/values"),
                "values_verbatim": domains,
                "role": "POSITIVE_RECORDED_WRITE_DOMAIN",
            },
        })

    base_record = {
        "schema_version": base_schema,
        "record_type": base_type,
        "status": base_status,
        "portfolio_id": "execution-portfolio-20260924-v1",
        "historical_source_presence": {
            "frozen_baseline": {
                "anchor_commit": "d3b477db97541d7cd2775e7c42381eb4875de519",
                "subtree_path": "src",
                "subtree_tree_sha": tree,
                "membership_semantics": membership_semantics,
                "wildcard_future_grant": wildcard_future_grant,
                "path_count": len(rel) + path_count_delta,
                "path_list_canonicalization": {
                    "tree_relative_form": {"sha256": rel_dg},
                    "repo_relative_form": {"sha256": repo_dg},
                },
            },
            "post_baseline_authority_sources": source_entries,
        },
        "current_implementation_write_authority": {
            "rule": "CURRENT_WRITE_REQUIRES_POSITIVE_CURRENT_AUTHORIZATION_CHAIN",
            "historical_presence_confers_write_authority": False,
            "roots": current_authority_roots or [
                {"root_id": r, "implementation_authorized": False,
                 "denial_class": "HARD_DENIAL"}
                for r in (denial_roots or [])
            ],
        },
        "reservation_semantics": {"reservation_grants_write_authority": False},
    }
    base_path = f"{AUTH_DIR}/{BASE_RECORD_NAME}"
    write_json_file(repo, base_path, base_record)
    base_sha = write_json_blob(repo, base_record)
    auth_paths.append(base_path)
    declared_base = ("1" * 40) if digest_mismatch_base else base_sha

    # H-P2-3: manifest amendment entries carry the SAME identity metadata as the
    # real manifest: record_schema_version, record_type, status, record_id,
    # amendment_ordinal, amends_record_blob_sha. None of these is optional.
    ordinals = list(amend_ordinals) if amend_ordinals is not None else [
        i + 1 for i in range(amendments)
    ]
    assert len(ordinals) == amendments, "amend_ordinals must cover every amendment"

    amendments_entries = []
    for i in range(amendments):
        ordinal = ordinals[i]
        name = AMENDMENT_NAME if i == 0 else f"amendment-{i}.json"
        apath = f"{AUTH_DIR}/{name}"
        link_manifest = ("2" * 40) if manifest_link_mismatch else base_sha
        link_record = ("3" * 40) if record_link_mismatch else base_sha
        record = {
            "schema_version": amend_schema,
            "record_type": amend_type,
            "status": amend_status,
            "record_id": f"amendment-{i}",
            "amendment_ordinal": ordinal,
            "amends": {"amended_record_blob_sha": link_record},
        }
        write_json_file(repo, apath, record)
        asha = write_json_blob(repo, record)
        auth_paths.append(apath)

        entry = {
            "record_path": apath,
            "record_blob_sha": ("4" * 40) if digest_mismatch_amendment else asha,
            "record_schema_version": (
                "future.amend.v99" if manifest_amend_schema_mismatch else amend_schema
            ),
            "record_type": (
                "NOT_SUPPORTED_AMEND" if manifest_amend_type_mismatch else amend_type
            ),
            "status": amend_status,
            "record_id": f"amendment-{i}",
            "amendment_ordinal": ordinal,
            "amends_record_blob_sha": link_manifest,
        }
        if manifest_amend_record_id_mismatch and i == 0:
            entry["record_id"] = "some-other-amendment-id"
        if manifest_amend_ordinal_mismatch and i == 0:
            entry["amendment_ordinal"] = ordinal + 7
        if manifest_amend_missing_ordinal and i == 0:
            del entry["amendment_ordinal"]
        amendments_entries.append(entry)

    manifest = {
        "schema_version": "portfolio-manifest.v1",
        "portfolio_id": "execution-portfolio-20260924-v1",
        "root_slots": root_slots,
        "authority_normalization_20260925": {
            "record_path": base_path,
            "record_blob_sha": declared_base,
            "record_schema_version": base_schema,
            "record_type": base_type,
            "status": base_status,
        },
        "authority_normalization_amendments_20260925": amendments_entries,
    }
    for root_id, packet in task_packets.items():
        rel_packet = (
            ".orchestration/portfolios/execution-portfolio-20260924-v1/"
            f"goals/{packet['goal_dir']}/task-packet.json"
        )
        write_json_file(repo, rel_packet, packet)
        auth_paths.append(rel_packet)
        task_packets[root_id]["_rel"] = rel_packet
        # The root slot must point at its task packet, exactly as the real
        # manifest does. The resolver derives write domains and the
        # task-packet witness through this field.
        for slot in root_slots:
            if slot.get("root_id") == root_id:
                slot["task_packet"] = rel_packet
    write_json_file(repo, MANIFEST_REL, manifest)
    auth_paths.append(MANIFEST_REL)

    commit = commit_isolated(repo, auth_paths, "authority")
    if create_ref:
        run(repo, "update-ref", "refs/heads/" + CANONICAL_REF, commit)
    return manifest


def goal_dir_for(root_id):
    return {
        H_ROOT: "goal-20260925-workspace-verifier-authorization",
        G0_ROOT: "goal-20260924-g0-rev18",
        D_ROOT: "goal-20260924-editorial-pipeline",
    }.get(root_id, "goal-" + root_id)


def load_authority_for_test(repo):
    """Test-side reader for the synthetic authority. Harness assertions only;
    the product resolver under test is the embedded one in the script."""
    commit = must(repo, "rev-parse", CANONICAL_REF)
    manifest = json.loads(run(repo, "cat-file", "blob",
                              f"{commit}:{MANIFEST_REL}").stdout)
    base_path = manifest["authority_normalization_20260925"]["record_path"]
    record = json.loads(run(repo, "cat-file", "blob",
                            f"{commit}:{base_path}").stdout)
    return manifest, record, commit


def cleanup():
    while SANDBOX:
        shutil.rmtree(SANDBOX.pop(), ignore_errors=True)


# --------------------------------------------------------------------------
# Task 1 tests - authority integrity / trust root
# --------------------------------------------------------------------------
def test_json_blob_helper_matches_file_bytes():
    """H-P3-1: `write_json_blob` and `write_json_file` must produce identical
    bytes for the same object, and the blob must really exist."""
    repo = make_repo()
    obj = {"a": 1, "b": ["x"], "c": {"nested": True}}
    sha = write_json_blob(repo, obj)
    rel = f"{AUTH_DIR}/same.json"
    write_json_file(repo, rel, obj)
    file_sha = must(repo, "hash-object", "-w", "--", rel)
    assert file_sha == sha
    assert run(repo, "cat-file", "-e", sha + "^{blob}", check=False).returncode == 0
    assert run(repo, "cat-file", "blob", sha).stdout == json_text(obj)


def test_guard_unknown_cli_flag_is_rejected():
    """GUARD: pre-existing behavior, not a RED contract.

    The unchanged script already rejects unknown flags with usage and exit 2,
    so this test passes before any implementation and must be labelled GUARD.
    """
    repo = make_repo()
    rc, out, err = run_script(repo, "--authority-ref", "refs/heads/x")
    assert rc == 2
    assert "usage:" in err


def test_canonical_ref_missing_fails_closed():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, create_ref=False)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "SOURCE-AUTH" not in out or "admin-commit=" not in out
    assert "canonical admin ref" in (out + err)


def test_environment_cannot_redirect_authority():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"})
    for var in ("AUTHORITY_REF", "ROOT_ID", "AUTHORITY_MANIFEST",
                "AUTHORITY_RECORD", "REMOTE_FRESHNESS"):
        os.environ[var] = "refs/heads/forged"
    try:
        rc, out, err = run_script(repo)
    finally:
        for var in ("AUTHORITY_REF", "ROOT_ID", "AUTHORITY_MANIFEST",
                    "AUTHORITY_RECORD", "REMOTE_FRESHNESS"):
            os.environ.pop(var, None)
    assert parse_report(out).get("admin-commit")


def test_admin_commit_and_freshness_reported():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"})
    rc, out, err = run_script(repo)
    rep = parse_report(out)
    assert rep.get("admin-commit") == must(repo, "rev-parse", CANONICAL_REF)
    assert rep.get("remote-freshness") == "NOT_OBSERVED"
    assert rep.get("base-record")


def test_base_record_digest_mismatch_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    digest_mismatch_base=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "base-record digest mismatch" in (out + err).lower()


def test_amendment_digest_mismatch_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    digest_mismatch_amendment=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "amendment digest mismatch" in (out + err).lower()


def test_manifest_amendment_link_mismatch_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    manifest_link_mismatch=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "amendment base link mismatch" in (out + err).lower()


def test_amendment_record_internal_base_link_mismatch_denies():
    """H-P1-3: the loaded RECORD's own /amends link must match the base."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    record_link_mismatch=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "amendment record base link mismatch" in (out + err).lower()


def test_unsupported_amendment_schema_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    amend_schema="future.amend.v99")
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "amendment schema" in (out + err).lower()


def test_unsupported_amendment_record_type_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    amend_type="NOT_SUPPORTED_AMEND")
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "amendment record type" in (out + err).lower()


def test_manifest_record_amendment_metadata_disagreement_denies():
    """Manifest declares one amendment schema while the record declares another."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    manifest_amend_schema_mismatch=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "amendment" in (out + err).lower()


def test_unsupported_base_schema_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    base_schema="future.v99")
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "unsupported authority schema" in (out + err).lower()


def test_unsupported_base_record_type_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    base_type="NOT_SUPPORTED")
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "record type" in (out + err).lower()


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    cleanup()
    print(f"{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
```

- [ ] **Step 2: Run the tests to verify the intended RED**

Run: `python3 tests/scripts/test_verify_workspace_source_authorization.py`
Expected:
- `test_guard_unknown_cli_flag_is_rejected` **PASSES** — it is a GUARD on pre-existing behavior, not a RED contract.
- Every other test **FAILS**, because the unchanged script emits no `SOURCE-AUTH` line at all, so `parse_report` returns an empty mapping and each denial assertion has no matching text.

Record the exact observed failure list. If any non-GUARD test passes at this step, it is mis-specified: rewrite it so it genuinely depends on the not-yet-written behavior.

- [ ] **Step 3: Verify the failure reason is the intended one**

Confirm the installed script exists at `<repo>/scripts/verify-workspace.sh`, `run_script` returns non-zero, and stdout contains no `SOURCE-AUTH` line. Fix any harness defect before proceeding.

- [ ] **Step 4: Commit**

```bash
git add tests/scripts/test_verify_workspace_source_authorization.py
git commit -m "test(root-h): add RED authority trust-root, digest and amendment-integrity tests"
```

---

### Task 2: Minimal GREEN authority resolver only

**Files:**
- Modify: `scripts/verify-workspace.sh`
- Test: `tests/scripts/test_verify_workspace_source_authorization.py`

**Interfaces:**
- Consumes: the Task 1 harness.
- Produces: the embedded Python block delimited by `# >>> SOURCE-AUTH-PYTHON BEGIN` / `# <<< SOURCE-AUTH-PYTHON END`, exposing `resolve_admin()`, `load_authority()`, `emit()`, `main()`, and the `SOURCE-AUTH` report lines.

**Scope limit:** this task implements authority resolution, digest enforcement, amendment-record validation, and reporting ONLY. It must not yet implement baseline membership, post-baseline historical paths, enumeration, or classification. Until Task 4, `main()` emits the authority report and then returns 0 without emitting any `path=` line.

- [ ] **Step 1: Add the embedded Python block**

In `scripts/verify-workspace.sh`, replace the existing source-boundary block (the `unexpected_source_path="$(find src -type f …)"` check through its terminating `fi`) with the block below. Everything else in the file stays unchanged.

```bash
# Source-authorization boundary. Authority is derived mechanically from the
# owner/admin portfolio authority lineage on the fixed canonical admin ref.
# No caller-selectable authority input exists. No network access occurs.
# >>> SOURCE-AUTH-PYTHON BEGIN
source_auth_rc=0
python3 - "$@" <<'SOURCE_AUTH_PY'
"""Root H source-boundary authorization resolver (embedded; stdlib only)."""

import json
import subprocess
import sys

CANONICAL_REF = "execution/execution-portfolio-20260924-v1/bootstrap"
MANIFEST_REL = (
    ".orchestration/portfolios/execution-portfolio-20260924-v1/manifest.json"
)
BASE_SCHEMA = "portfolio-authority-normalization.v1"
BASE_TYPE = "OWNER_AUTHORIZED_PORTFOLIO_AUTHORITY_NORMALIZATION"
BASE_STATUS = "OWNER_AUTHORIZED"
AMEND_SCHEMA = "portfolio-authority-normalization-amendment.v1"
AMEND_TYPE = "OWNER_AUTHORIZED_AUTHORITY_NORMALIZATION_AMENDMENT"


class Deny(Exception):
    pass


def _run(args):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          check=False)


def _git(*args):
    p = _run(args)
    if p.returncode != 0:
        raise Deny("git failure: " + " ".join(args))
    return p.stdout


def resolve_admin():
    p = _run(["rev-parse", CANONICAL_REF + "^{commit}"])
    if p.returncode != 0:
        raise Deny("canonical admin ref is absent or unresolvable: " + CANONICAL_REF)
    return p.stdout.strip()


def _commit_blob(commit, path):
    p = _run(["rev-parse", "%s:%s" % (commit, path)])
    if p.returncode != 0:
        raise Deny("authority artifact unresolvable: " + path)
    return p.stdout.strip()


def _commit_text(commit, path):
    p = _run(["cat-file", "blob", "%s:%s" % (commit, path)])
    if p.returncode != 0:
        raise Deny("authority artifact unreadable: " + path)
    return p.stdout


def blob_exists(sha):
    return _run(["cat-file", "-e", sha + "^{blob}"]).returncode == 0


def blob_text(sha):
    p = _run(["cat-file", "blob", sha])
    if p.returncode != 0:
        raise Deny("cited blob is not resolvable: " + sha)
    return p.stdout


def load_json(text, what):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise Deny(what + " is not valid JSON")


def _supported(schema, record_type, status, what):
    if schema != BASE_SCHEMA and schema != AMEND_SCHEMA:
        raise Deny("unsupported " + what + " schema")
    if record_type not in (BASE_TYPE, AMEND_TYPE):
        raise Deny("unsupported " + what + " record type")
    if status != BASE_STATUS:
        raise Deny(what + " is not owner-authorized")


def load_authority(commit):
    p = _run(["cat-file", "blob", "%s:%s" % (commit, MANIFEST_REL)])
    if p.returncode != 0:
        raise Deny("anchor manifest unresolvable: " + MANIFEST_REL)
    manifest = load_json(p.stdout, "anchor manifest")

    declared = manifest.get("authority_normalization_20260925")
    if not isinstance(declared, dict):
        raise Deny("manifest does not declare an authority normalization")
    base_path = declared.get("record_path")
    base_blob = declared.get("record_blob_sha")
    if not isinstance(base_path, str) or not isinstance(base_blob, str):
        raise Deny("authority normalization declaration is incomplete")
    if _commit_blob(commit, base_path) != base_blob:
        raise Deny("base-record digest mismatch")

    record = load_json(_commit_text(commit, base_path), "base authority record")
    if record.get("schema_version") != BASE_SCHEMA:
        raise Deny("unsupported authority schema")
    if record.get("record_type") != BASE_TYPE:
        raise Deny("unsupported authority record type")
    if record.get("status") != BASE_STATUS:
        raise Deny("authority record is not owner-authorized")

    amendments = []
    seen_ordinals = []
    for index, entry in enumerate(
        manifest.get("authority_normalization_amendments_20260925") or []
    ):
        if not isinstance(entry, dict):
            raise Deny("amendment declaration is malformed")
        apath = entry.get("record_path")
        adeclared = entry.get("record_blob_sha")
        if not isinstance(apath, str) or not isinstance(adeclared, str):
            raise Deny("amendment declaration is incomplete")
        actual = _commit_blob(commit, apath)
        if actual != adeclared:
            raise Deny("amendment digest mismatch")

        # H-P2-3: manifest amendment metadata is REQUIRED. `None` is never an
        # acceptable substitute for a declared schema, type, status, identity
        # or ordinal.
        if entry.get("record_schema_version") != AMEND_SCHEMA:
            raise Deny("unsupported amendment schema in manifest")
        if entry.get("record_type") != AMEND_TYPE:
            raise Deny("unsupported amendment record type in manifest")
        if entry.get("status") != BASE_STATUS:
            raise Deny("amendment manifest status is not owner-authorized")
        declared_id = entry.get("record_id")
        if not isinstance(declared_id, str) or not declared_id:
            raise Deny("amendment manifest record_id is missing")
        declared_ordinal = entry.get("amendment_ordinal")
        if type(declared_ordinal) is not int or declared_ordinal < 1:
            raise Deny("amendment manifest ordinal is missing or malformed")
        if declared_ordinal in seen_ordinals:
            raise Deny("amendment ordinal is duplicated")
        if seen_ordinals and declared_ordinal <= seen_ordinals[-1]:
            raise Deny("amendment ordinals are not strictly increasing")
        seen_ordinals.append(declared_ordinal)

        link = entry.get("amends_record_blob_sha")
        if link != base_blob:
            raise Deny("amendment base link mismatch")

        loaded = load_json(_commit_text(commit, apath), "amendment record")
        if loaded.get("schema_version") != entry["record_schema_version"]:
            raise Deny("manifest/record amendment schema disagreement")
        if loaded.get("record_type") != entry["record_type"]:
            raise Deny("manifest/record amendment type disagreement")
        if loaded.get("status") != entry["status"]:
            raise Deny("manifest/record amendment status disagreement")
        if loaded.get("record_id") != declared_id:
            raise Deny("manifest/record amendment record_id mismatch")
        if loaded.get("amendment_ordinal") != declared_ordinal:
            raise Deny("manifest/record amendment ordinal mismatch")

        internal = (loaded.get("amends") or {}).get("amended_record_blob_sha")
        if internal is None:
            raise Deny("amendment record carries no base link")
        if internal != base_blob:
            raise Deny("amendment record base link mismatch")

        amendments.append({"index": index + 1, "blob": actual, "record": loaded})
    return manifest, record, amendments


def emit(key, value):
    sys.stdout.write("SOURCE-AUTH %s=%s\n" % (key, value))


def main():
    try:
        commit = resolve_admin()
        manifest, record, amendments = load_authority(commit)
    except Deny as denial:
        sys.stdout.write("SOURCE-AUTH DENY reason=%s\n" % str(denial))
        sys.stderr.write("FAIL  source authorization: %s\n"
                         % str(denial).replace("%", "%%"))
        return 1

    emit("admin-commit", commit)
    emit("base-record", manifest["authority_normalization_20260925"]["record_blob_sha"])
    for amendment in amendments:
        emit("amendment%d" % amendment["index"], amendment["blob"])
        emit("amendment%d-record" % amendment["index"], amendment["blob"])
    emit("remote-freshness", "NOT_OBSERVED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
SOURCE_AUTH_PY
source_auth_rc=$?
# <<< SOURCE-AUTH-PYTHON END
if [[ $source_auth_rc -ne 0 ]]; then
  failures=$((failures + 1))
fi
```

- [ ] **Step 2: Run the Task 1 tests to verify they pass**

Run: `python3 tests/scripts/test_verify_workspace_source_authorization.py`
Expected: every Task 1 test PASSES, including the GUARD.

- [ ] **Step 3: Verify the script still parses and its CLI is unchanged**

```bash
bash -n scripts/verify-workspace.sh && echo "SYNTAX_OK"
bash scripts/verify-workspace.sh --nope ; echo "rc=$?"   # usage, rc=2
```

- [ ] **Step 4: Commit**

```bash
git add scripts/verify-workspace.sh
git commit -m "feat(root-h): resolve canonical admin authority with digest and amendment-record enforcement"
```

---

### Task 3: RED baseline, exact-blob citation, source-local pairing, untracked, empty-authority, and enumeration tests

**Files:**
- Modify: `tests/scripts/test_verify_workspace_source_authorization.py`
- Test: `tests/scripts/test_verify_workspace_source_authorization.py`

**Interfaces:**
- Consumes: Task 1 helpers and fixtures.
- Produces: no new product interface; adds failing coverage for historical presence, enumeration, reporting, and denial conditions.

All tests in this task must fail against Task 2's resolver, which emits only the authority report and never a `path=` line.

- [ ] **Step 1: Write the failing tests**

Append these test functions.

```python
def test_exact_frozen_baseline_path_is_historical():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n", "gate0/a.py": "a\n"})
    track(repo, "src/gate0/a.py")
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/a.py"] == "AUTHORIZED_HISTORICAL"


def test_nested_baseline_path_works():
    """H-P2-1: nested baseline members must build and classify.

    Also asserts the frozen `src` subtree identity is the SUBTREE, so the
    repo-relative form is `src/gate0/...` and never `src/src/...`.
    """
    repo = make_repo()
    build_authority(repo, baseline_files={
        "README.md": "r\n", "gate0/a.py": "a\n", "gate0/nested/deep.py": "d\n",
    })
    manifest, record, commit = load_authority_for_test(repo)
    tree = record["historical_source_presence"]["frozen_baseline"]["subtree_tree_sha"]
    rel, repo_rel = tree_listing(repo, tree)
    # harness assertions on the frozen baseline identity itself
    assert "gate0/a.py" in rel, rel
    assert "src/gate0/a.py" in repo_rel, repo_rel
    assert not any(p.startswith("src/src/") for p in repo_rel), repo_rel
    # product classification through the same tree
    track(repo, "src/gate0/nested/deep.py")
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/nested/deep.py"] == "AUTHORIZED_HISTORICAL"
    assert parse_report(out)["baseline-paths"] == "3"


def test_baseline_member_untracked_now_is_unauthorized():
    """H-P2-1: baseline membership must not rescue a currently untracked path."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n", "gate0/a.py": "a\n"})
    untracked(repo, "src/gate0/a.py")
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/a.py"] == "UNAUTHORIZED"


def test_tracked_path_absent_from_all_preimages_is_unauthorized():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"})
    track(repo, "src/new/thing.py")
    rc, out, err = run_script(repo)
    assert classes(out)["src/new/thing.py"] == "UNAUTHORIZED"


def test_exact_observed_post_baseline_path_is_historical():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    sources=[post_baseline_source(
                        "ROOT_E", ["src/gate1/__init__.py"], ["src/gate1/**"])])
    track(repo, "src/gate1/__init__.py")
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate1/__init__.py"] == "AUTHORIZED_HISTORICAL"


def test_new_tracked_path_in_old_broad_domain_is_unauthorized():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    sources=[post_baseline_source(
                        "ROOT_E", ["src/gate1/__init__.py"], ["src/gate1/**"])])
    track(repo, "src/gate1/__init__.py")
    track(repo, "src/gate1/forged.py")
    rc, out, err = run_script(repo)
    result = classes(out)
    assert result["src/gate1/forged.py"] == "UNAUTHORIZED"
    assert result["src/gate1/__init__.py"] == "AUTHORIZED_HISTORICAL"


def test_cross_source_pairing_is_not_a_cross_product():
    """H-P1-2: an observed path must be authorized only by its OWN source."""
    repo = make_repo()
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        sources=[
            post_baseline_source("A", ["src/gate2/x.py"], ["src/gate1/**"]),
            post_baseline_source("B", [], ["src/gate2/**"]),
        ],
    )
    track(repo, "src/gate2/x.py")
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate2/x.py"] == "UNAUTHORIZED"


def test_source_claiming_observed_paths_without_citation_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    sources=[post_baseline_source(
                        "ROOT_E", ["src/gate1/__init__.py"], ["src/gate1/**"])],
                    source_missing_citation=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "citation" in (out + err).lower()


def test_exact_cited_blob_consumed_after_path_changed():
    """H-P2-2 / spec case 11: exact blob identity, not the mutable path.

    Mechanically proves both halves of the invariant:
      * the current branch-relative path blob DIFFERS from the cited blob;
      * the original cited blob is still present and is what classification uses.
    """
    repo = make_repo()
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        sources=[post_baseline_source(
            "ROOT_E", ["src/gate1/__init__.py"], ["src/gate1/**"])],
        citation_path_changed=True,
    )
    manifest, record, commit = load_authority_for_test(repo)
    citation = record["historical_source_presence"][
        "post_baseline_authority_sources"][0]["recorded_write_domain_citation"]
    cited_blob = citation["blob_sha"]

    # invariant 1: the path now holds a DIFFERENT blob
    current_path_blob = must(repo, "hash-object", "-w", "--stdin",
                             input=json.dumps({"values": ["src/__changed__/"]},
                                              indent=2, sort_keys=True) + "\n")
    assert current_path_blob != cited_blob
    committed_path_blob = must(repo, "rev-parse", f"{commit}:{citation['path']}")
    assert committed_path_blob != cited_blob, (
        "the canonical admin commit must point at the later, changed path blob"
    )

    # invariant 2: the ORIGINAL cited blob still resolves
    assert run(repo, "cat-file", "-e", cited_blob + "^{blob}").returncode == 0

    # product classification still succeeds from the original cited blob
    track(repo, "src/gate1/__init__.py")
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate1/__init__.py"] == "AUTHORIZED_HISTORICAL"


def test_amendment_manifest_record_id_mismatch_denies():
    """H-P2-3: manifest and loaded record must agree on record_id."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    manifest_amend_record_id_mismatch=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "record_id mismatch" in (out + err).lower()


def test_amendment_manifest_ordinal_mismatch_denies():
    """H-P2-3: manifest and loaded record must agree on amendment_ordinal."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    manifest_amend_ordinal_mismatch=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "ordinal mismatch" in (out + err).lower()


def test_amendment_missing_manifest_ordinal_denies():
    """H-P2-3: manifest ordinal is REQUIRED, never optional."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=1,
                    manifest_amend_missing_ordinal=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "ordinal" in (out + err).lower()


def test_amendment_duplicate_ordinal_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=2,
                    amend_ordinals=[1, 1])
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "ordinal" in (out + err).lower()


def test_amendment_non_monotonic_ordinal_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=2,
                    amend_ordinals=[2, 1])
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "increasing" in (out + err).lower()


def test_amendment_ordinals_one_then_two_accepted():
    """The current real manifest uses ordinals 1 then 2."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, amendments=2,
                    amend_ordinals=[1, 2])
    rc, out, err = run_script(repo)
    rep = parse_report(out)
    assert rep.get("amendment1") and rep.get("amendment2")


def test_cited_blob_object_missing_denies():
    """H-P3-2: a genuinely ABSENT exact cited object must DENY.

    The fixture must build successfully; the refusal must come from the
    resolver observing that the cited blob does not exist, not from a Git add
    failure while constructing the fixture.
    """
    repo = make_repo()
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        sources=[post_baseline_source(
            "ROOT_E", ["src/gate1/__init__.py"], ["src/gate1/**"])],
        citation_blob_missing=True,
    )
    # fixture construction succeeded and the canonical ref resolves
    assert must(repo, "rev-parse", CANONICAL_REF)
    rc, out, err = run_script(repo)
    assert rc != 0
    combined = (out + err).lower()
    assert "cited" in combined or "preimage" in combined or "resolvable" in combined
    # the denial is a resolver report, not a harness crash
    assert "SOURCE-AUTH DENY" in out or "FAIL  source authorization" in (out + err)


def test_cited_blob_survives_provenance_path_removal_or_change():
    """POSITIVE exact-blob GUARD: path removal/change never invalidates an
    existing exact cited blob, and the fixture still builds."""
    for kwargs in ({"citation_path_changed": True},
                   {"citation_path_removed": True}):
        repo = make_repo()
        build_authority(
            repo, baseline_files={"README.md": "r\n"},
            sources=[post_baseline_source(
                "ROOT_E", ["src/gate1/__init__.py"], ["src/gate1/**"])],
            **kwargs,
        )
        assert must(repo, "rev-parse", CANONICAL_REF)
        manifest, record, commit = load_authority_for_test(repo)
        citation = record["historical_source_presence"][
            "post_baseline_authority_sources"][0]["recorded_write_domain_citation"]
        # the original cited blob is still present and resolvable
        assert run(repo, "cat-file", "-e",
                   citation["blob_sha"] + "^{blob}").returncode == 0
        track(repo, "src/gate1/__init__.py")
        rc, out, err = run_script(repo)
        assert classes(out)["src/gate1/__init__.py"] == "AUTHORIZED_HISTORICAL", kwargs


def test_cited_pointer_value_mismatch_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    sources=[post_baseline_source(
                        "ROOT_E", ["src/gate1/__init__.py"], ["src/gate1/**"])],
                    pointer_mismatch=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "pointer" in (out + err).lower()


def test_baseline_tree_missing_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, tree_missing=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "baseline" in (out + err).lower()


def test_baseline_path_count_mismatch_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, path_count_delta=5)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "path count" in (out + err).lower()


def test_baseline_repo_listing_digest_mismatch_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"}, digest_corrupt=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "digest mismatch" in (out + err).lower()


def test_wildcard_future_grant_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    wildcard_future_grant=True)
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "wildcard" in (out + err).lower()


def test_unsupported_membership_semantics_denies():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    membership_semantics="PREFIX")
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "membership semantics" in (out + err).lower()


def test_empty_derived_authority_denies():
    """Spec 11.3 / H-P1-7: no admissible derived authority must DENY, not PASS."""
    repo = make_repo()
    build_authority(
        repo,
        baseline_files={},
        sources=[],
    )
    rc, out, err = run_script(repo)
    assert rc != 0
    assert "empty" in (out + err).lower()


def test_two_unauthorized_paths_both_reported_in_order():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"})
    track(repo, "src/zzz/b.py")
    track(repo, "src/aaa/a.py")
    rc, out, err = run_script(repo)
    unauthorized = [p for p, c in classes(out).items() if c == "UNAUTHORIZED"]
    assert unauthorized == ["src/aaa/a.py", "src/zzz/b.py"]
    assert parse_report(out)["unauthorized-count"] == "2"


def test_no_first_hit_truncation():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"})
    for i in range(5):
        track(repo, f"src/junk/file{i}.py")
    rc, out, err = run_script(repo)
    assert parse_report(out)["unauthorized-count"] == "5"


def test_hostile_filenames_do_not_bypass_or_corrupt():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"})
    hostile = ["src/has space.py", "src/star*.py", "src/-dash.py", "src/nl\nname.py"]
    for name in hostile:
        track(repo, name)
    rc, out, err = run_script(repo)
    result = classes(out)
    for name in hostile:
        assert result[name] == "UNAUTHORIZED"
    assert parse_report(out)["unauthorized-count"] == str(len(hostile))
    for line in out.splitlines():
        if line.startswith("SOURCE-AUTH path="):
            assert line.count("class=") == 1
```

- [ ] **Step 2: Confirm the empty-baseline fixture path**

`test_empty_derived_authority_denies` needs no extra fixture support: `build_authority(repo, baseline_files={}, sources=[])` already produces a valid empty `src` subtree object with zero entries and no post-baseline sources. The resolver can therefore prove emptiness rather than crash. Confirm `write_tree_from_files(repo, {})` returns a real (non-null) empty tree:

```bash
python3 - <<'PY'
# scratch check only; not part of the test file
import subprocess, tempfile, os
repo = tempfile.mkdtemp()
subprocess.run(["git", "-C", repo, "init", "-q", "-b", "main", "."], check=True)
subprocess.run(["git", "-C", repo, "config", "user.email", "t@t"], check=True)
subprocess.run(["git", "-C", repo, "config", "user.name", "t"], check=True)
empty = subprocess.run(["git", "-C", repo, "hash-object", "-w", "-t", "tree", "/dev/null"],
                       capture_output=True, text=True, check=True).stdout.strip()
print("empty tree object:", empty)
assert len(empty) == 40
PY
```

- [ ] **Step 3: Run the tests to verify they all fail**

Run: `python3 tests/scripts/test_verify_workspace_source_authorization.py`
Expected: every test in this task FAILS, because Task 2's resolver emits no `path=` line, no `baseline-paths`, no `unauthorized-count`, and no `empty` denial. Confirm each failure is for that reason and not a harness error.

- [ ] **Step 4: Commit**

```bash
git add tests/scripts/test_verify_workspace_source_authorization.py
git commit -m "test(root-h): add RED baseline, exact-blob citation, source-local pairing, enumeration tests"
```

---

### Task 4: GREEN baseline, historical classification, enumeration, reporting

**Files:**
- Modify: `scripts/verify-workspace.sh`
- Test: `tests/scripts/test_verify_workspace_source_authorization.py`

**Interfaces:**
- Consumes: Task 2's resolver.
- Produces: `baseline()`, `post_baseline_authorized_paths()`, `enumerate_sources()`, `classify()`, and the empty-authority denial.

- [ ] **Step 1: Add baseline validation and derivation**

Insert before `emit()` in the embedded block.

```python
MEMBERSHIP = "EXACT_PATH_MEMBERSHIP_IN_FROZEN_GIT_TREE"


def _digest(text):
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


def baseline(record):
    presence = record.get("historical_source_presence") or {}
    fb = presence.get("frozen_baseline")
    if not isinstance(fb, dict):
        raise Deny("authority record lacks a frozen baseline")
    if fb.get("membership_semantics") != MEMBERSHIP:
        raise Deny("unsupported baseline membership semantics")
    if fb.get("wildcard_future_grant") is not False:
        raise Deny("baseline must not grant a wildcard future grant")
    tree = fb.get("subtree_tree_sha")
    if not isinstance(tree, str) or not tree:
        raise Deny("baseline subtree identity is missing")
    p = _run(["ls-tree", "-r", "--name-only", tree])
    if p.returncode != 0:
        raise Deny("frozen baseline subtree is not resolvable locally")
    relative = p.stdout.splitlines()
    if len(relative) != fb.get("path_count"):
        raise Deny("frozen baseline path count mismatch")
    canonical = fb.get("path_list_canonicalization") or {}
    rel_form = canonical.get("tree_relative_form") or {}
    repo_form = canonical.get("repo_relative_form") or {}
    if rel_form.get("sha256") and _digest("".join(n + "\n" for n in relative)) != rel_form["sha256"]:
        raise Deny("tree-relative listing digest mismatch")
    if repo_form.get("sha256") and _digest("".join("src/" + n + "\n" for n in relative)) != repo_form["sha256"]:
        raise Deny("repo-relative listing digest mismatch")
    return {"src/" + n for n in relative}
```

- [ ] **Step 2: Add source-local post-baseline authorization**

Source-local pairing replaces the cross-product. Paths are admitted only when their OWN source both observes them and cites a domain containing them.

```python
def _domain_matches(path, domain):
    d = str(domain).split(" if justified")[0].strip()
    if d.endswith("/**"):
        d = d[:-3]
    if d.endswith("/"):
        d = d[:-1]
    return bool(d) and (path == d or path.startswith(d + "/"))


def _resolve_pointer(obj, pointer):
    node = obj
    for part in str(pointer).strip("/").split("/"):
        if part == "":
            continue
        if part.isdigit():
            if not isinstance(node, list) or int(part) >= len(node):
                return None
            node = node[int(part)]
        else:
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
    return node


def post_baseline_authorized_paths(record):
    """Source-LOCAL historical paths only.

    For each source independently: validate its exact cited blob, require the
    pointer/value match, then admit a path only if that source observes it AND
    that same source's cited domain contains it. A source that claims observed
    paths without a valid citation fails closed.
    """
    presence = record.get("historical_source_presence") or {}
    authorized = set()
    for source in presence.get("post_baseline_authority_sources") or []:
        observed = set(source.get("observed_src_paths_beyond_baseline") or [])
        citation = source.get("recorded_write_domain_citation")
        if not isinstance(citation, dict):
            if observed:
                raise Deny("a post-baseline source cites no write domain")
            continue
        cited_sha = citation.get("blob_sha")
        if not isinstance(cited_sha, str) or not cited_sha:
            raise Deny("cited write-domain preimage has no blob identity")
        if not blob_exists(cited_sha):
            raise Deny("cited write-domain preimage is not resolvable: " + cited_sha)
        cited = load_json(blob_text(cited_sha), "cited write-domain preimage")
        node = _resolve_pointer(cited, citation.get("json_pointer", ""))
        if node != citation.get("values_verbatim"):
            raise Deny("cited pointer/value mismatch")
        domains = list(citation.get("values_verbatim") or [])
        for path in observed:
            if any(_domain_matches(path, d) for d in domains):
                authorized.add(path)
    return authorized
```

- [ ] **Step 3: Add enumeration and classification**

```python
def enumerate_sources():
    p = _run(["ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "src"])
    if p.returncode != 0:
        raise Deny("source enumeration failed")
    return sorted(n for n in p.stdout.split("\0") if n)


def tracked_sources():
    p = _run(["ls-files", "-z", "--", "src"])
    if p.returncode != 0:
        raise Deny("tracked source enumeration failed")
    return {n for n in p.stdout.split("\0") if n}
```

- [ ] **Step 4: Rewrite `main()` to emit the authority report, then classify**

Replace Task 2's `main()` with this version. Historical predicates only; the current-write branch arrives in Task 6.

```python
def main():
    try:
        commit = resolve_admin()
        manifest, record, amendments = load_authority(commit)
        frozen = baseline(record)
        post = post_baseline_authorized_paths(record)
    except Deny as denial:
        sys.stdout.write("SOURCE-AUTH DENY reason=%s\n" % str(denial))
        sys.stderr.write("FAIL  source authorization: %s\n"
                         % str(denial).replace("%", "%%"))
        return 1

    if not frozen and not post:
        sys.stdout.write("SOURCE-AUTH DENY reason=empty derived authority set\n")
        sys.stderr.write("FAIL  source authorization: empty derived authority set\n")
        return 1

    emit("admin-commit", commit)
    emit("base-record", manifest["authority_normalization_20260925"]["record_blob_sha"])
    for amendment in amendments:
        emit("amendment%d" % amendment["index"], amendment["blob"])
        emit("amendment%d-record" % amendment["index"], amendment["blob"])
    emit("frozen-tree", record["historical_source_presence"]["frozen_baseline"]["subtree_tree_sha"])
    emit("baseline-paths", len(frozen))
    emit("post-baseline-paths", len(post))
    emit("remote-freshness", "NOT_OBSERVED")

    tracked = tracked_sources()
    unauthorized = []
    for path in enumerate_sources():
        if path not in tracked:
            classification = "UNAUTHORIZED"
        elif path in frozen or path in post:
            classification = "AUTHORIZED_HISTORICAL"
        else:
            classification = "UNAUTHORIZED"
        sys.stdout.write("SOURCE-AUTH path=%s class=%s\n"
                         % (json.dumps(path), classification))
        if classification == "UNAUTHORIZED":
            unauthorized.append(path)

    emit("unauthorized-count", len(unauthorized))
    for path in unauthorized:
        sys.stderr.write("FAIL  unexpected source file exists outside authorized "
                         "paths: %s\n" % json.dumps(path))
    return 1 if unauthorized else 0
```

- [ ] **Step 5: Run the full test file**

Run: `python3 tests/scripts/test_verify_workspace_source_authorization.py`
Expected: all Task 1 and Task 3 tests PASS.

- [ ] **Step 6: Verify against the real repository authority**

```bash
bash scripts/verify-workspace.sh 2>&1 | grep '^SOURCE-AUTH' | head -20
```

Expected: `admin-commit`, `base-record=166667bb…`, `amendment1=6e214c30…`, `amendment2=2359336a…`, `frozen-tree=581fea73…`, `baseline-paths=88`, and every real `src/**` path classified `AUTHORIZED_HISTORICAL`.

- [ ] **Step 7: Commit**

```bash
git add scripts/verify-workspace.sh
git commit -m "feat(root-h): classify frozen baseline and source-local post-baseline historical paths"
```

---

### Task 5: RED current-root identity and real positive current-chain tests

**Files:**
- Modify: `tests/scripts/test_verify_workspace_source_authorization.py`
- Test: `tests/scripts/test_verify_workspace_source_authorization.py`

**Interfaces:**
- Consumes: Task 1 helpers, `positive_root_slot`, `goal_dir_for`.
- Produces: failing coverage for current-root derivation, hard denial, positive chain, and absence.

- [ ] **Step 1: Write the failing tests**

Append these test functions.

```python
def test_current_root_identity_unique_match():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[{"root_id": H_ROOT, "root_branch": H_BRANCH}])
    run(repo, "checkout", "-q", "-b", H_BRANCH)
    rc, out, err = run_script(repo)
    assert parse_report(out)["current-root-identity"] == f"RESOLVED:{H_ROOT}"


def test_zero_root_match_yields_not_observed():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[{"root_id": H_ROOT, "root_branch": H_BRANCH}])
    run(repo, "checkout", "-q", "-b", "unmapped-branch")
    rc, out, err = run_script(repo)
    assert parse_report(out)["current-root-identity"] == "NOT_OBSERVED"


def test_ambiguous_root_match_yields_ambiguous():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[{"root_id": H_ROOT, "root_branch": H_BRANCH},
                                {"root_id": "root-duplicate", "root_branch": H_BRANCH}])
    run(repo, "checkout", "-q", "-b", H_BRANCH)
    rc, out, err = run_script(repo)
    assert parse_report(out)["current-root-identity"] == "AMBIGUOUS"


def test_canonical_main_has_no_current_root_identity():
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[{"root_id": H_ROOT, "root_branch": H_BRANCH}])
    run(repo, "checkout", "-q", "main")
    rc, out, err = run_script(repo)
    assert parse_report(out)["current-root-identity"] == "NOT_OBSERVED"


def test_positive_current_chain_authorizes_exact_domain_path():
    """A REAL-shaped chain reaches AUTHORIZED_CURRENT (H-P1-4)."""
    repo = make_repo()
    witness = write_blob(repo, "owner implementation authorization\n")
    index = {"gate0_rev18_authority": [
        {"role": "OWNER_IMPLEMENTATION_AUTHORIZATION", "blob_sha": witness},
    ]}
    slot, packet = positive_root_slot(
        G0_ROOT, G0_BRANCH, ["src/gate0/"], witness_blob=witness)
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        root_slots=[slot], task_packets={G0_ROOT: packet},
        process_index_blob=index,
    )
    track(repo, "src/gate0/new_module.py")
    run(repo, "checkout", "-q", "-b", G0_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/new_module.py"] == "AUTHORIZED_CURRENT"
    assert parse_report(out)["current-write-root"] == G0_ROOT


def test_positive_chain_via_owner_marker_authorizes():
    """The second supported archetype: authorized_by_owner_on + ref."""
    repo = make_repo()
    ref = f"{AUTH_DIR}/root-expansion-authorization-20260924-v1.json"
    write_json_file(repo, ref, {"schema_version": "portfolio-root-expansion-authorization.v1",
                                "roots": [{"root_id": H_ROOT, "base_sha": "0" * 40}]})
    slot, packet = positive_root_slot(
        H_ROOT, H_BRANCH, ["src/vip_fvs/**"],
        owner_on="2026-09-24", authorization_ref=ref)
    packet["goal_dir"] = goal_dir_for(H_ROOT)
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        root_slots=[slot], task_packets={H_ROOT: packet},
    )
    track(repo, "src/vip_fvs/example.py")
    run(repo, "checkout", "-q", "-b", H_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/vip_fvs/example.py"] == "AUTHORIZED_CURRENT"


def test_explicit_false_denies_current_write():
    repo = make_repo()
    witness = write_blob(repo, "w\n")
    slot, packet = positive_root_slot(G0_ROOT, G0_BRANCH, ["src/gate0/"],
                                      witness_blob=witness)
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        root_slots=[slot], task_packets={G0_ROOT: packet},
        process_index_blob={"gate0_rev18_authority": [
            {"role": "OWNER_IMPLEMENTATION_AUTHORIZATION", "blob_sha": witness}]},
        denial_roots=[G0_ROOT],
    )
    track(repo, "src/gate0/new_module.py")
    run(repo, "checkout", "-q", "-b", G0_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/new_module.py"] == "UNAUTHORIZED"


def test_absent_positive_witness_denies_current_write():
    """Absence is NOT TRUE: domains alone never grant a current write."""
    repo = make_repo()
    slot, packet = positive_root_slot(G0_ROOT, G0_BRANCH, ["src/gate0/"])
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        root_slots=[slot], task_packets={G0_ROOT: packet},
    )
    track(repo, "src/gate0/new_module.py")
    run(repo, "checkout", "-q", "-b", G0_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/new_module.py"] == "UNAUTHORIZED"


def test_reservation_only_never_grants_current_write():
    repo = make_repo()
    slot = {"root_id": H_ROOT, "root_branch": H_BRANCH,
            "reserved_future_product_paths": ["scripts/verify-workspace.sh"]}
    packet = {"goal_dir": goal_dir_for(H_ROOT),
              "schema_version": "execution-root-task-packet.v1",
              "root_id": H_ROOT, "root_branch": H_BRANCH,
              "implementation_authorized": False}
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[slot], task_packets={H_ROOT: packet})
    track(repo, "src/vip_fvs/x.py")
    run(repo, "checkout", "-q", "-b", H_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/vip_fvs/x.py"] == "UNAUTHORIZED"


def test_path_outside_positive_domain_is_unauthorized():
    repo = make_repo()
    witness = write_blob(repo, "w\n")
    slot, packet = positive_root_slot(G0_ROOT, G0_BRANCH, ["src/gate0/"],
                                      witness_blob=witness)
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        root_slots=[slot], task_packets={G0_ROOT: packet},
        process_index_blob={"gate0_rev18_authority": [
            {"role": "OWNER_IMPLEMENTATION_AUTHORIZATION", "blob_sha": witness}]},
    )
    track(repo, "src/gate0/in_domain.py")
    track(repo, "src/outside/not_in_domain.py")
    run(repo, "checkout", "-q", "-b", G0_BRANCH)
    rc, out, err = run_script(repo)
    result = classes(out)
    assert result["src/gate0/in_domain.py"] == "AUTHORIZED_CURRENT"
    assert result["src/outside/not_in_domain.py"] == "UNAUTHORIZED"


def test_owner_expansion_with_unrelated_root_denies():
    """H-P2-4: a record authorizing only another root grants nothing."""
    repo = make_repo()
    ref = f"{AUTH_DIR}/root-expansion-authorization-20260924-v1.json"
    expansion = {
        "schema_version": EXPANSION_SCHEMA,
        "record_type": EXPANSION_TYPE,
        "portfolio_id": EXPANSION_PORTFOLIO,
        "roots": [{"root_id": "root-someone-else", "branch": D_BRANCH}],
    }
    slot, packet = positive_root_slot(
        D_ROOT, D_BRANCH, ["src/gate3/"],
        owner_on="2026-09-24", authorization_ref=ref)
    packet["goal_dir"] = goal_dir_for(D_ROOT)
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[slot], task_packets={D_ROOT: packet},
                    extra_files={ref: expansion})
    track(repo, "src/gate3/x.py")
    run(repo, "checkout", "-q", "-b", D_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate3/x.py"] == "UNAUTHORIZED"


def _expansion_fixture(expansion, *, packet_overrides=None):
    repo = make_repo()
    ref = f"{AUTH_DIR}/root-expansion-authorization-20260924-v1.json"
    slot, packet = positive_root_slot(
        D_ROOT, D_BRANCH, ["src/gate3/"],
        owner_on="2026-09-24", authorization_ref=ref)
    packet["goal_dir"] = goal_dir_for(D_ROOT)
    packet.update(packet_overrides or {})
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[slot], task_packets={D_ROOT: packet},
                    extra_files={ref: expansion})
    track(repo, "src/gate3/x.py")
    run(repo, "checkout", "-q", "-b", D_BRANCH)
    return repo


def test_valid_owner_expansion_reaches_current():
    """The real Root-D-shaped archetype still reaches AUTHORIZED_CURRENT."""
    repo = _expansion_fixture({
        "schema_version": EXPANSION_SCHEMA,
        "record_type": EXPANSION_TYPE,
        "portfolio_id": EXPANSION_PORTFOLIO,
        "roots": [{"root_id": D_ROOT, "branch": D_BRANCH}],
    })
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate3/x.py"] == "AUTHORIZED_CURRENT"


def test_owner_expansion_wrong_schema_denies():
    repo = _expansion_fixture({
        "schema_version": "wrong.v9",
        "record_type": EXPANSION_TYPE,
        "portfolio_id": EXPANSION_PORTFOLIO,
        "roots": [{"root_id": D_ROOT, "branch": D_BRANCH}],
    })
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate3/x.py"] == "UNAUTHORIZED"


def test_owner_expansion_wrong_record_type_denies():
    repo = _expansion_fixture({
        "schema_version": EXPANSION_SCHEMA,
        "record_type": "NOT_AN_OWNER_EXPANSION",
        "portfolio_id": EXPANSION_PORTFOLIO,
        "roots": [{"root_id": D_ROOT, "branch": D_BRANCH}],
    })
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate3/x.py"] == "UNAUTHORIZED"


def test_owner_expansion_wrong_branch_denies():
    repo = _expansion_fixture({
        "schema_version": EXPANSION_SCHEMA,
        "record_type": EXPANSION_TYPE,
        "portfolio_id": EXPANSION_PORTFOLIO,
        "roots": [{"root_id": D_ROOT, "branch": "refs/heads/somewhere-else"}],
    })
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate3/x.py"] == "UNAUTHORIZED"


def test_task_packet_root_id_mismatch_denies_current():
    repo = make_repo()
    witness = run(repo, "hash-object", "-w", "--stdin", input="w\n").stdout.strip()
    slot, packet = positive_root_slot(G0_ROOT, G0_BRANCH, ["src/gate0/"],
                                      witness_blob=witness)
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    packet["root_id"] = "root-someone-else"
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[slot], task_packets={G0_ROOT: packet},
                    process_index_blob={"gate0_rev18_authority": [
                        {"role": "OWNER_IMPLEMENTATION_AUTHORIZATION",
                         "blob_sha": witness}]})
    track(repo, "src/gate0/x.py")
    run(repo, "checkout", "-q", "-b", G0_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/x.py"] == "UNAUTHORIZED"


def test_task_packet_root_branch_mismatch_denies_current():
    repo = make_repo()
    witness = run(repo, "hash-object", "-w", "--stdin", input="w\n").stdout.strip()
    slot, packet = positive_root_slot(G0_ROOT, G0_BRANCH, ["src/gate0/"],
                                      witness_blob=witness)
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    packet["root_branch"] = "refs/heads/somewhere-else"
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[slot], task_packets={G0_ROOT: packet},
                    process_index_blob={"gate0_rev18_authority": [
                        {"role": "OWNER_IMPLEMENTATION_AUTHORIZATION",
                         "blob_sha": witness}]})
    track(repo, "src/gate0/x.py")
    run(repo, "checkout", "-q", "-b", G0_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/x.py"] == "UNAUTHORIZED"


def test_task_packet_unsupported_schema_denies_current():
    repo = make_repo()
    witness = run(repo, "hash-object", "-w", "--stdin", input="w\n").stdout.strip()
    slot, packet = positive_root_slot(G0_ROOT, G0_BRANCH, ["src/gate0/"],
                                      witness_blob=witness)
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    packet["schema_version"] = "execution-root-task-packet.v99"
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[slot], task_packets={G0_ROOT: packet},
                    process_index_blob={"gate0_rev18_authority": [
                        {"role": "OWNER_IMPLEMENTATION_AUTHORIZATION",
                         "blob_sha": witness}]})
    track(repo, "src/gate0/x.py")
    run(repo, "checkout", "-q", "-b", G0_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/x.py"] == "UNAUTHORIZED"


def test_untracked_in_current_domain_is_unauthorized():
    repo = make_repo()
    witness = write_blob(repo, "w\n")
    slot, packet = positive_root_slot(G0_ROOT, G0_BRANCH, ["src/gate0/"],
                                      witness_blob=witness)
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    build_authority(
        repo, baseline_files={"README.md": "r\n"},
        root_slots=[slot], task_packets={G0_ROOT: packet},
        process_index_blob={"gate0_rev18_authority": [
            {"role": "OWNER_IMPLEMENTATION_AUTHORIZATION", "blob_sha": witness}]},
    )
    untracked(repo, "src/gate0/untracked.py")
    run(repo, "checkout", "-q", "-b", G0_BRANCH)
    rc, out, err = run_script(repo)
    assert classes(out)["src/gate0/untracked.py"] == "UNAUTHORIZED"
```

- [ ] **Step 2: Verify the real Gate-0 chain shape against real authority**

Add a shape-verification test that reads the real admin artifacts from the H worktree, proving the chain models real data rather than an invented schema.

```python
def test_real_gate0_chain_shape_is_traversable():
    """Read the REAL admin authority and prove the chain shape exists."""
    import subprocess as sp

    def real(*args):
        p = sp.run(["git", "-C", REPO_ROOT, *args], capture_output=True, text=True)
        if p.returncode != 0:
            raise AssertionError(f"git {' '.join(args)}: {p.stderr}")
        return p.stdout

    manifest = json.loads(real(
        "show",
        "origin/execution/execution-portfolio-20260924-v1/bootstrap:"
        ".orchestration/portfolios/execution-portfolio-20260924-v1/manifest.json",
    ))
    slot = next(s for s in manifest["root_slots"] if s["root_id"] == G0_ROOT)
    assert slot["root_branch"] == G0_BRANCH
    packet = json.loads(real(
        "show",
        "origin/execution/execution-portfolio-20260924-v1/bootstrap:" + slot["task_packet"],
    ))
    assert packet["exclusive_write_paths_or_domains"]
    witness = slot["gate0_authority"]["owner_implementation_authorization_blob"]
    assert real("cat-file", "-t", witness).strip() == "blob"
    index = json.loads(real(
        "show",
        "origin/execution/execution-portfolio-20260924-v1/bootstrap:"
        ".orchestration/portfolios/execution-portfolio-20260924-v1/authority/"
        "process-authority-refs.json",
    ))
    roles = {e["role"]: e["blob_sha"] for e in index["gate0_rev18_authority"]}
    assert roles["OWNER_IMPLEMENTATION_AUTHORIZATION"] == witness


def test_real_root_d_expansion_shape_is_traversable():
    """H-P2-4: prove the second archetype exists in REAL admin authority.

    The Root-D-style witness must be a supported owner-expansion record naming
    the resolved root AND branch, not merely any document with a `roots` list.
    """
    import subprocess as sp

    ADMIN = "origin/execution/execution-portfolio-20260924-v1/bootstrap:"

    def real(*args):
        p = sp.run(["git", "-C", REPO_ROOT, *args], capture_output=True, text=True)
        if p.returncode != 0:
            raise AssertionError(f"git {' '.join(args)}: {p.stderr}")
        return p.stdout

    manifest = json.loads(real("show", ADMIN + MANIFEST_REL))
    slot = next(s for s in manifest["root_slots"] if s["root_id"] == D_ROOT)
    assert slot["root_branch"] == D_BRANCH

    packet = json.loads(real("show", ADMIN + slot["task_packet"]))
    assert packet["root_id"] == slot["root_id"]
    assert packet["root_branch"] == slot["root_branch"]
    assert packet["authorized_by_owner_on"]
    assert packet["exclusive_write_paths_or_domains"]

    expansion = json.loads(real("show", ADMIN + packet["authorization_ref"]))
    assert expansion["schema_version"] == EXPANSION_SCHEMA
    assert expansion["record_type"] == EXPANSION_TYPE
    assert expansion["portfolio_id"] == EXPANSION_PORTFOLIO
    matching = [e for e in expansion["roots"]
                if e.get("root_id") == slot["root_id"]
                and e.get("branch") == slot["root_branch"]]
    assert matching, "the real expansion record must name the resolved root+branch"


def test_real_amendment_records_match_manifest_identity():
    """H-P2-3: the REAL manifest and amendment records agree on identity."""
    import subprocess as sp

    ADMIN = "origin/execution/execution-portfolio-20260924-v1/bootstrap:"

    def real(*args):
        p = sp.run(["git", "-C", REPO_ROOT, *args], capture_output=True, text=True)
        if p.returncode != 0:
            raise AssertionError(f"git {' '.join(args)}: {p.stderr}")
        return p.stdout

    manifest = json.loads(real("show", ADMIN + MANIFEST_REL))
    entries = manifest["authority_normalization_amendments_20260925"]
    assert entries, "the real manifest must list amendments"
    seen = []
    for entry in entries:
        assert entry["record_schema_version"] == AMEND_SCHEMA
        assert entry["record_type"] == AMEND_TYPE
        assert entry["status"] == STATUS_OK
        assert isinstance(entry["record_id"], str) and entry["record_id"]
        assert type(entry["amendment_ordinal"]) is int
        assert entry["amendment_ordinal"] >= 1
        if seen:
            assert entry["amendment_ordinal"] > seen[-1]
        seen.append(entry["amendment_ordinal"])
        record = json.loads(real("show", ADMIN + entry["record_path"]))
        assert record["record_id"] == entry["record_id"]
        assert record["amendment_ordinal"] == entry["amendment_ordinal"]
        assert (record.get("amends") or {}).get("amended_record_blob_sha") == \
            entry["amends_record_blob_sha"]
    assert seen == [1, 2], seen
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 tests/scripts/test_verify_workspace_source_authorization.py`
Expected: all current-root tests FAIL because Task 4 never emits `current-root-identity`; all `AUTHORIZED_CURRENT` tests FAIL because Task 4 has no current-write branch. `test_real_gate0_chain_shape_is_traversable` PASSES — it validates real authority data, not product behavior, so label it a data-shape guard in its docstring (it is already labelled).

- [ ] **Step 4: Commit**

```bash
git add tests/scripts/test_verify_workspace_source_authorization.py
git commit -m "test(root-h): add RED current-root identity and real positive current-chain tests"
```

---

### Task 6: GREEN current-root identity and positive current-write authority

**Files:**
- Modify: `scripts/verify-workspace.sh`
- Test: `tests/scripts/test_verify_workspace_source_authorization.py`

**Interfaces:**
- Consumes: Task 4's classification loop.
- Produces: `current_root()`, `positive_current_witness()`, `current_authorized()`, and the `current-root-identity` / `current-write-root` report lines.

- [ ] **Step 1: Add root identity and the positive current chain**

Insert into the embedded block. The chain consumes only real owner-record shapes: a task packet with write domains, a hard-denial check from the base record, and one of two supported positive witnesses.

```python
def current_branch():
    p = _run(["branch", "--show-current"])
    return p.stdout.strip() if p.returncode == 0 else ""


def current_root(manifest):
    branch = current_branch()
    if not branch:
        return "NOT_OBSERVED", None
    matches = [s.get("root_id") for s in manifest.get("root_slots") or []
               if s.get("root_branch") == branch]
    if not matches:
        return "NOT_OBSERVED", None
    if len(matches) > 1:
        return "AMBIGUOUS", None
    return "RESOLVED", matches[0]


def _hard_denied(record, root_id):
    authority = record.get("current_implementation_write_authority") or {}
    for entry in authority.get("roots") or []:
        if entry.get("root_id") != root_id:
            continue
        if entry.get("implementation_authorized") is False:
            return True
        if entry.get("denial_class") == "HARD_DENIAL":
            return True
    return False


def resolved_slot(manifest, root_id):
    return next((s for s in manifest.get("root_slots") or []
                 if s.get("root_id") == root_id), None)


def load_validated_packet(slot, commit, *, require_domains=False):
    """H-P2-4: the task packet must be the SAME root and SAME branch before its
    domains or its witness may be used. Nothing is derived from a packet whose
    identity disagrees with the resolved manifest slot."""
    path = slot.get("task_packet")
    if not isinstance(path, str) or not path:
        raise Deny("resolved root has no task packet")
    p = _run(["cat-file", "blob", "%s:%s" % (commit, path)])
    if p.returncode != 0:
        raise Deny("task packet unresolvable")
    packet = load_json(p.stdout, "task packet")
    if packet.get("schema_version") != PACKET_SCHEMA:
        raise Deny("unsupported task packet schema")
    if packet.get("root_id") != slot.get("root_id"):
        raise Deny("task packet root_id mismatch")
    if packet.get("root_branch") != slot.get("root_branch"):
        raise Deny("task packet root_branch mismatch")
    domains = packet.get("exclusive_write_paths_or_domains")
    if require_domains:
        if not isinstance(domains, (list, tuple)) or not domains:
            raise Deny("task packet records no write domains")
        for domain in domains:
            if not isinstance(domain, str) or not domain:
                raise Deny("task packet write domain is malformed")
    return packet, list(domains or [])


def _expansion_authorizes(refdoc, slot):
    """H-P2-4: the expansion record must be the supported owner-expansion shape
    AND contain the resolved root for this exact branch. A record authorizing
    only another root never grants current write authority."""
    if refdoc.get("schema_version") != EXPANSION_SCHEMA:
        return False
    if refdoc.get("record_type") != EXPANSION_TYPE:
        return False
    if refdoc.get("portfolio_id") != EXPANSION_PORTFOLIO:
        return False
    roots = refdoc.get("roots")
    if not isinstance(roots, list):
        return False
    for entry in roots:
        if not isinstance(entry, dict):
            continue
        if entry.get("root_id") != slot.get("root_id"):
            continue
        if entry.get("branch") != slot.get("root_branch"):
            continue
        if (entry.get("goal_id") and slot.get("goal_id")
                and entry["goal_id"] != slot["goal_id"]):
            continue
        return True
    return False


def positive_current_witness(manifest, slot, commit):
    """Prove a REAL positive owner implementation-authorization witness.

    Supported archetypes, both present in current authority data:
      (a) Gate-0: the trusted manifest root slot carries gate0_authority whose
          owner_implementation_authorization_blob resolves as a blob AND appears
          in the process authority index under
          role OWNER_IMPLEMENTATION_AUTHORIZATION;
      (b) owner expansion: the validated same-root task packet carries
          authorized_by_owner_on plus an authorization_ref resolving to a
          supported owner-expansion record that names THIS root and branch.
    Anything else is NOT proven.
    """
    authority = slot.get("gate0_authority")
    if isinstance(authority, dict):
        witness = authority.get("owner_implementation_authorization_blob")
        if isinstance(witness, str) and witness and blob_exists(witness):
            index_path = f"{AUTHORITY_DIR}/process-authority-refs.json"
            p = _run(["cat-file", "blob", "%s:%s" % (commit, index_path)])
            if p.returncode == 0:
                index = load_json(p.stdout, "process authority index")
                for entries in index.values():
                    if not isinstance(entries, list):
                        continue
                    for entry in entries:
                        if not isinstance(entry, dict):
                            continue
                        if (entry.get("role") == "OWNER_IMPLEMENTATION_AUTHORIZATION"
                                and entry.get("blob_sha") == witness):
                            return True

    packet, _ = load_validated_packet(slot, commit)
    if packet.get("authorized_by_owner_on") and packet.get("authorization_ref"):
        ref = packet["authorization_ref"]
        q = _run(["cat-file", "blob", "%s:%s" % (commit, ref)])
        if q.returncode != 0:
            return False
        return _expansion_authorizes(
            load_json(q.stdout, "authorization reference"), slot)
    return False


def current_authorized(manifest, record, root_id, commit, path):
    if not root_id:
        return False
    if _hard_denied(record, root_id):
        return False
    authority = record.get("current_implementation_write_authority") or {}
    if authority.get("historical_presence_confers_write_authority") is not False:
        return False
    slot = resolved_slot(manifest, root_id)
    if slot is None:
        return False
    try:
        _, domains = load_validated_packet(slot, commit, require_domains=True)
    except Deny:
        return False
    if not positive_current_witness(manifest, slot, commit):
        return False
    return any(_domain_matches(path, d) for d in domains)
```

Add the `AUTHORITY_DIR` constant beside `MANIFEST_REL`:

```python
AUTHORITY_DIR = ".orchestration/portfolios/execution-portfolio-20260924-v1/authority"
```

- [ ] **Step 2: Wire identity and current classification into `main()`**

Extend the authority section of `main()` so identity is resolved and reported, and add the current branch to the classification chain.

```python
    identity, root_id = current_root(manifest)
    emit("current-root-identity", "RESOLVED:%s" % root_id if root_id else identity)
    emit("current-write-root", root_id if root_id else "NONE")

    tracked = tracked_sources()
    unauthorized = []
    for path in enumerate_sources():
        if path not in tracked:
            classification = "UNAUTHORIZED"
        elif path in frozen or path in post:
            classification = "AUTHORIZED_HISTORICAL"
        elif current_authorized(manifest, record, root_id, commit, path):
            classification = "AUTHORIZED_CURRENT"
        else:
            classification = "UNAUTHORIZED"
        sys.stdout.write("SOURCE-AUTH path=%s class=%s\n"
                         % (json.dumps(path), classification))
        if classification == "UNAUTHORIZED":
            unauthorized.append(path)
```

The `current-root-identity` and `current-write-root` lines must be emitted before the per-path lines, after `post-baseline-paths`.

- [ ] **Step 3: Run the full test file**

Run: `python3 tests/scripts/test_verify_workspace_source_authorization.py`
Expected: all tests PASS, including `AUTHORIZED_CURRENT` coverage and the real-chain shape guard.

- [ ] **Step 4: Confirm the real repository still classifies truthfully**

```bash
bash scripts/verify-workspace.sh 2>&1 | grep '^SOURCE-AUTH' | head -12
```

Expected on the Root-H branch: `current-root-identity=RESOLVED:root-workspace-verifier-authorization`, `current-write-root=root-workspace-verifier-authorization`, `remote-freshness=NOT_OBSERVED`, `unauthorized-count=0`, and every real `src/**` path `AUTHORIZED_HISTORICAL` (Root H is hard-denied for current writes, so nothing becomes `AUTHORIZED_CURRENT`).

- [ ] **Step 5: Commit**

```bash
git add scripts/verify-workspace.sh
git commit -m "feat(root-h): derive current root identity and enforce real positive current-write chain"
```

---

### Task 7: CLI/unrelated-check guards, review, verification, and durability

**Files:**
- Modify: `tests/scripts/test_verify_workspace_source_authorization.py`
- Verify: `scripts/verify-workspace.sh`

**Interfaces:**
- Consumes: everything from Tasks 1-6.
- Produces: GUARD coverage, review evidence, and final durability verification. No new product behavior.

- [ ] **Step 1: Write the GUARD tests**

Append these test functions. Each is labelled GUARD because it pins behavior that must remain unchanged rather than driving a new production step.

```python
def test_guard_cli_accepts_only_documented_forms():
    """GUARD: operational CLI is unchanged."""
    repo = make_repo()
    witness = write_blob(repo, "w\n")
    slot, packet = positive_root_slot(G0_ROOT, G0_BRANCH, ["src/gate0/"],
                                      witness_blob=witness)
    packet["goal_dir"] = goal_dir_for(G0_ROOT)
    build_authority(repo, baseline_files={"README.md": "r\n"},
                    root_slots=[slot], task_packets={G0_ROOT: packet},
                    process_index_blob={"gate0_rev18_authority": [
                        {"role": "OWNER_IMPLEMENTATION_AUTHORIZATION",
                         "blob_sha": witness}]})
    rc, out, err = run_script(repo, "--require-pushed")
    assert "usage:" not in err
    for bad in ("--authority-ref", "--root-id", "--manifest",
                "--authority-file", "--authority-record", "--freshness"):
        rc, out, err = run_script(repo, bad)
        assert rc == 2, bad
        assert "usage:" in err


def test_guard_unrelated_checks_still_execute():
    """GUARD: unrelated verifier checks remain present and independent."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"})
    rc, out, err = run_script(repo)
    combined = out + err
    assert "local branch is" in combined
    assert "not a valid local Git repository" not in combined
    assert "reference-pack" in combined or "manifest.yaml" in combined


def test_guard_resolver_uses_no_network_and_fake_gh_is_used():
    """GUARD: the resolver is local-only; the fake gh shim satisfies the
    unrelated gh check. Never invoke a real gh."""
    repo = make_repo()
    build_authority(repo, baseline_files={"README.md": "r\n"})
    rc, out, err = run_script(repo)
    assert "SOURCE-AUTH admin-commit=" in out
    assert "remote-freshness=NOT_OBSERVED" in out
    combined = out + err
    assert "GitHub repository visibility is private" in combined
    embedded = open(SCRIPT_PATH).read()
    for forbidden in ("ls-remote", "fetch", "gh repo"):
        assert forbidden not in embedded.split("SOURCE-AUTH-PYTHON BEGIN")[1].split(
            "SOURCE-AUTH-PYTHON END")[0], forbidden
```

- [ ] **Step 2: Run the full test file**

Run: `python3 tests/scripts/test_verify_workspace_source_authorization.py`
Expected: every test PASSES.

- [ ] **Step 3: Run the same file under pytest if available**

Run: `python3 -m pytest tests/scripts/test_verify_workspace_source_authorization.py -v`
Expected: PASS, or skip with a recorded note if pytest is not installed. Do not install dependencies unless the standing routine-prerequisite policy authorizes it.

- [ ] **Step 4: Shell and embedded-Python syntax checks**

```bash
bash -n scripts/verify-workspace.sh && echo SYNTAX_OK

python3 - <<'PY'
import re
src = open('scripts/verify-workspace.sh').read()
m = re.search(r"# >>> SOURCE-AUTH-PYTHON BEGIN\n(?:.*?\n)*?python3 - \"\$@\" <<'SOURCE_AUTH_PY'\n(.*?)\nSOURCE_AUTH_PY\n", src, re.S)
assert m, "embedded block not found"
compile(m.group(1), "<embedded>", "exec")
print("EMBEDDED_PYTHON_COMPILES")
PY
```

Expected: `SYNTAX_OK` and `EMBEDDED_PYTHON_COMPILES`.

- [ ] **Step 5: Run the real verifier and record exact output**

```bash
bash scripts/verify-workspace.sh >/tmp/h-out.txt 2>/tmp/h-err.txt; echo "rc=$?"
grep -c '^PASS' /tmp/h-out.txt; grep '^FAIL' /tmp/h-err.txt
```

Record the exact observed output. Truthfully report unrelated failures. Do not engineer `EXIT 0`.

- [ ] **Step 6: Request code review**

Use the `requesting-code-review` methodology over the two-file diff. Adjudicate findings.

- [ ] **Step 7: Apply only authorized remediation and commit it**

If review requires changes, modify only the two authorized paths and commit:

```bash
git add scripts/verify-workspace.sh tests/scripts/test_verify_workspace_source_authorization.py
git commit -m "fix(root-h): address source-authorization review findings"
```

Skip this step when review produced no changes. No remediation commit may happen after Step 12.

- [ ] **Step 8: Fresh focused and full verification after any remediation**

```bash
python3 tests/scripts/test_verify_workspace_source_authorization.py
bash -n scripts/verify-workspace.sh
bash scripts/verify-workspace.sh >/tmp/h-out.txt 2>/tmp/h-err.txt; echo "rc=$?"
```

Expected: the focused suite reports `N/N passed`; the real verifier's unrelated failures are unchanged and truthfully reported.

- [ ] **Step 9: Verification before completion**

Use the `verification-before-completion` methodology. Cite exact commands and exact observed output. Do not claim completion from inference.

- [ ] **Step 10: Implementation-only changed-path audit**

The base is the future `AUTHORIZED_IMPLEMENTATION_START_SHA` supplied by the owner implementation authorization, **not** the historical root base.

```bash
# BASE is the exact AUTHORIZED_IMPLEMENTATION_START_SHA named by the owner
# implementation authorization, exported by the operator before running this.
git diff --name-only "$BASE"..HEAD
```

Expected exactly:

```
scripts/verify-workspace.sh
tests/scripts/test_verify_workspace_source_authorization.py
```

Any third path is a scope violation and must be reverted. A separate cumulative audit may additionally list the approved docs:

```bash
git diff --name-only d3b477db97541d7cd2775e7c42381eb4875de519..HEAD
# docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md
# docs/superpowers/plans/2026-09-25-root-h-workspace-source-authorization-implementation-plan.md
# scripts/verify-workspace.sh
# tests/scripts/test_verify_workspace_source_authorization.py
```

The two docs are approved deliverables, not implementation scope violations.

- [ ] **Step 11: Confirm no forbidden activity occurred**

Confirm and record: no network/provider/model activity, no protected/archive media, no dependency download, no real `gh` invocation, no canonical-main mutation, no merge, no force push, no Gate promotion.

- [ ] **Step 12: Push the Root-H branch (normal, non-force)**

```bash
git fetch --prune origin
git rev-parse origin/execution/execution-portfolio-20260924-v1/workspace-verifier-authorization
git push origin execution/execution-portfolio-20260924-v1/workspace-verifier-authorization
```

The push must be a fast-forward. Never force push.

- [ ] **Step 13: Verify remote durability and unchanged anchors**

```bash
git fetch --prune origin
git rev-parse HEAD
git rev-parse origin/execution/execution-portfolio-20260924-v1/workspace-verifier-authorization
# must be equal

git rev-parse origin/execution/execution-portfolio-20260924-v1/workspace-verifier-authorization:scripts/verify-workspace.sh
git rev-parse origin/execution/execution-portfolio-20260924-v1/workspace-verifier-authorization:tests/scripts/test_verify_workspace_source_authorization.py
git rev-parse origin/main
git rev-parse origin/execution/execution-portfolio-20260924-v1/bootstrap
git rev-parse origin/execution/execution-portfolio-20260924-v1/workspace-verifier-authorization:docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md
# main, admin and the spec must be unchanged; spec must remain 14a0419091a88282059b7e4fa345a13f2e91e0d8
```

Only after this step may a completion claim be made. No commit may follow it.

---

## Spec Coverage Map

| Frozen spec section / normative case | Owning task |
| --- | --- |
| §4 two predicates | Task 5, Task 6 |
| §5 frozen baseline exact membership | Task 3, Task 4 |
| §5.1 forbidden inference | Task 3 |
| §5.2 baseline validation is mandatory | Task 3, Task 4 |
| §6 post-baseline exact + cited preimage | Task 3, Task 4 |
| §6.1 domain-only forbidden | Task 3, Task 4 |
| §6.2 cited artifacts by exact blob identity | Task 1, Task 3, Task 4 |
| §6.3 future extension fails closed | Task 1, Task 3 |
| §7 dynamic digest enforcement | Task 1, Task 2 |
| §8 frozen trust root, no injection | Task 1 (GUARD + RED), Task 7 (GUARD) |
| §8.3 test seam | Task 1 (no seam; literal canonical ref in temp repos) |
| §9 current root identity | Task 5, Task 6 |
| §10 complete deterministic enumeration | Task 3, Task 4 |
| §11 result vocabulary | Task 4, Task 6 |
| §11.3 empty derived authority is denial | Task 3 (RED), Task 4 (GREEN) |
| §12 remote freshness NOT_OBSERVED | Task 1, Task 7 |
| §13 exactly two implementation paths | Task 0, Task 7 (audit) |
| §14 unrelated check preservation | Task 7 (GUARD) |
| §15 README disposition (no writes) | Global Constraints |
| §16 spec is not implementation authority | Task 0 |
| §17 case 1 baseline path historical | Task 3 |
| §17 case 2 tracked absent from preimages | Task 3 |
| §17 case 3 exact observed post-baseline | Task 3 |
| §17 case 4 new tracked in old domain | Task 3 |
| §17 case 5 untracked under any domain | Task 3 |
| §17 case 6 forged caller authority ref | Task 1 (GUARD), Task 7 (GUARD) |
| §17 case 7 canonical ref missing | Task 1 |
| §17 case 8 base-record digest mismatch | Task 1 |
| §17 case 9 amendment digest/link mismatch | Task 1 |
| §17 case 10 cited pointer/value mismatch | Task 3 |
| §17 case 11 exact cited blob still consumed | Task 3 |
| §17 case 12 unsupported schema/type | Task 1 |
| §17 case 13 unique root + positive chain | Task 5 (RED), Task 6 (GREEN) |
| §17 case 14 zero/ambiguous root match | Task 5, Task 6 |
| §17 case 15 canonical main | Task 5, Task 6 |
| §17 case 16 remote freshness | Task 1, Task 7 |
| §17 case 17 two unauthorized paths | Task 3 |
| §17 case 18 hostile filenames | Task 3 |
| §17 case 19 unrelated failures independent | Task 7 (GUARD) |
| §17 case 20 future unsupported amendment shape | Task 1 (amendment schema/type/status/record_id/ordinal RED) |

## H-P2 Correction Map

| Review finding | Correction in this plan | Test / task |
| --- | --- | --- |
| H-P2-1 baseline subtree identity | `write_tree_from_files` result used directly as `subtree_tree_sha`; `write_isolated_tree` removed; `tree_listing` asserts no `src/src/` | `test_nested_baseline_path_works`, `test_baseline_member_untracked_now_is_unauthorized` (Task 3) |
| H-P2-2 path-change fixture | `cited_blob` frozen from `write_json_blob`; path later mutated to a different blob; citation keeps the ORIGINAL | `test_exact_cited_blob_consumed_after_path_changed` (Task 3), asserts committed path blob != cited blob |
| H-P2-3 amendment identity/ordinal | Manifest metadata REQUIRED; loaded record must match schema/type/status/record_id/ordinal; ordinals unique and strictly increasing | Six named amendment tests (Task 1) |
| H-P2-4 root/packet binding | `load_validated_packet` enforces packet schema + same root_id + same root_branch + non-empty string domains; `_expansion_authorizes` enforces expansion schema/type/portfolio and a matching root+branch entry | Eight named binding tests (Task 5) plus two real-data shape guards |

## Self-Review Notes

- **True TDD order:** Task 2 implements only the authority resolver; Task 3's tests for baseline, historical, enumeration, reporting, untracked and empty-authority behavior are all RED against it. Task 5's current-root, packet-binding and positive-chain tests are RED against Task 4 (Task 4 has no current-write branch and emits no `current-root-identity`). Every behavior-changing GREEN (Tasks 2, 4, 6) is preceded by a named failing test. Pre-existing behavior is labelled GUARD (`test_guard_unknown_cli_flag_is_rejected`, the three Task 7 guards, and the real-data shape guards, which validate repository authority data rather than product behavior).
- **Spec coverage:** every frozen section and all 20 normative cases map to named tests.
- **Placeholder scan:** the plan was mechanically scanned for the prohibited placeholder patterns. Zero occurrences outside this sentence.
- **Type consistency:** helper names introduced in Task 1 are used with identical signatures in Tasks 3, 5, 7. Embedded-block functions (`resolve_admin`, `load_authority`, `blob_exists`, `blob_text`, `load_json`, `baseline`, `post_baseline_authorized_paths`, `enumerate_sources`, `tracked_sources`, `current_root`, `resolved_slot`, `load_validated_packet`, `_expansion_authorizes`, `positive_current_witness`, `current_authorized`, `emit`, `main`) are referenced consistently. `current_write_domains` was removed; domains now come only from the validated packet.
- **Review Focus:** all ten items map to named tasks and tests above.
- **Corrections A-D:** each maps to a named test in the H-P2 Correction Map.

## Known Implementation Risks To Watch

1. **Temp-index hygiene.** `write_tree_from_files` and `commit_isolated` must always delete their temporary index, including on failure, or later Git calls inherit stale state.
2. **`hash-object` needs `-w`.** Without `-w`, `hash-object` only computes a SHA and never writes the object, so a later `cat-file -e <sha>` fails. Every blob a citation depends on must be written with `-w` (use `write_json_blob`).
3. **Frozen baseline identity is the SUBTREE.** `frozen_baseline.subtree_tree_sha` must be the tree OF the `src` contents (`write_tree_from_files(repo, baseline_files)`), never a parent tree containing an `src` entry. Otherwise tree-relative names gain a leading `src/` and classification looks for `src/src/...`. `tree_listing` asserts this.
4. **Digest source of truth.** Both listing digests must be derived from real `git ls-tree -r` output, never from a Python-sorted source list.
5. **Detached HEAD.** `git branch --show-current` is empty, so identity is `NOT_OBSERVED`. Intended.
6. **Real-repository run.** The canonical bootstrap ref must be present locally before running the real verifier; absence fails closed by design.
7. **Fixture blob scoping.** A witness blob created in one temporary repository does not exist in another. Create each witness inside the repository under test.
