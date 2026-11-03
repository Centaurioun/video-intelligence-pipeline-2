"""Bounded Git object access and verified repository context for Gate 0."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from gate0.feasibility.macos_stage_b_evidence_constants import (
    AuthorityTuple, EvidenceDagError, EvidenceFailureCode, VerifiedRepositoryContext,
)

_REGISTRY: dict[int, tuple[VerifiedRepositoryContext, Path, int, int]] = {}
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_MAX_OUTPUT = 16 * 1024 * 1024


def _fail(detail: str, code=EvidenceFailureCode.GENERATION_IDENTITY_COLLISION):
    raise EvidenceDagError(code, detail)


def _run_git(argv: tuple[str, ...], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    """The sole bounded subprocess leaf. No shell and no inherited Git selectors."""
    if not isinstance(argv, tuple) or not argv or any(not isinstance(x, str) or "\x00" in x for x in argv):
        _fail("invalid git argument vector")
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(Path.home()),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
    }
    try:
        result = subprocess.run(("git", *argv), cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
                                check=False, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _fail(f"git invocation failed: {type(exc).__name__}")
    if len(result.stdout) > _MAX_OUTPUT or result.returncode != 0:
        _fail("git command failed or exceeded output bound")
    return result


def _discover_repository_root_from_module_location() -> Path:
    """Resolve the one production repository root from this module's location."""
    path = Path(__file__).resolve(strict=True)
    for parent in path.parents:
        if (parent / ".git").exists():
            return parent
    _fail("repository root not found")


def _root() -> Path:
    path = _discover_repository_root_from_module_location()
    if not isinstance(path, Path) or path.is_symlink():
        _fail("repository root must be a real directory")
    try:
        root = path.resolve(strict=True)
        st = root.stat(follow_symlinks=False)
    except OSError:
        _fail("repository root is unavailable")
    if not root.is_dir() or root != path.absolute():
        _fail("repository root is not canonical")
    return root


def _oid(value: str, expected: str | None = None) -> str:
    if not isinstance(value, str) or not _HEX40.fullmatch(value):
        _fail("malformed Git object id")
    actual = object_type(value)
    if expected is not None and actual != expected:
        _fail("Git object has wrong type")
    return value


def object_type(object_id: str) -> str:
    if not isinstance(object_id, str) or not _HEX40.fullmatch(object_id):
        _fail("malformed Git object id")
    out = _run_git(("cat-file", "-t", object_id), _root()).stdout.decode("ascii", "strict").strip()
    if out not in ("commit", "tree", "blob"):
        _fail("unsupported Git object type")
    return out


def _resolve_commit_path(commit_sha: str, repository_path: str) -> str:
    _oid(commit_sha, "commit")
    if (not isinstance(repository_path, str) or not repository_path or repository_path.startswith("/")
            or "\\" in repository_path or "\x00" in repository_path
            or any(p in ("", ".", "..") for p in repository_path.split("/"))):
        _fail("unsafe repository path")
    spec = f"{commit_sha}:{repository_path}"
    result = _run_git(("rev-parse", "--verify", spec), _root()).stdout.decode("ascii", "strict").strip()
    _oid(result, "blob")
    return result


def blob_id_at(commit_sha: str, repository_path: str) -> str:
    return _resolve_commit_path(commit_sha, repository_path)


def read_blob_at(commit_sha: str, repository_path: str) -> bytes:
    oid = _resolve_commit_path(commit_sha, repository_path)
    return _run_git(("cat-file", "blob", oid), _root()).stdout


def commit_parent(commit_sha: str) -> str:
    _oid(commit_sha, "commit")
    raw = _run_git(("rev-list", "--parents", "-n", "1", commit_sha), _root()).stdout.split()
    if len(raw) != 2:
        _fail("commit must have exactly one parent")
    parent = raw[1].decode("ascii")
    return _oid(parent, "commit")


def commit_tree(commit_sha: str) -> str:
    _oid(commit_sha, "commit")
    tree = _run_git(("rev-parse", "--verify", f"{commit_sha}^{{tree}}"), _root()).stdout.decode("ascii").strip()
    return _oid(tree, "tree")


def strict_ancestor(ancestor_commit: str, descendant_commit: str) -> bool:
    _oid(ancestor_commit, "commit")
    _oid(descendant_commit, "commit")
    if ancestor_commit == descendant_commit:
        return False
    common = _run_git(("merge-base", ancestor_commit, descendant_commit), _root()).stdout.decode().strip()
    return common == ancestor_commit


def reachable_committed_generation_identities(evaluation_commit: str) -> tuple[str, ...]:
    _oid(evaluation_commit, "commit")
    raw = _run_git(("log", "--format=%H", "--full-history", evaluation_commit, "--", "S10/result-manifest.json"), _root()).stdout
    commits = _run_git(("rev-list", evaluation_commit), _root()).stdout.decode("ascii").splitlines()
    reachable = set(commits)
    found: set[str] = set()
    for commit in raw.decode("ascii").splitlines():
        if commit not in reachable:
            continue
        try:
            value = json.loads(read_blob_at(commit, "S10/result-manifest.json"))
        except (ValueError, UnicodeDecodeError):
            continue
        identity = value.get("generation_identity") if isinstance(value, dict) else None
        if isinstance(identity, str) and _HEX64.fullmatch(identity):
            found.add(identity)
    return tuple(sorted(found))


def additive_mdrt_paths(base_commit: str, head_commit: str) -> tuple[str, ...]:
    _oid(base_commit, "commit")
    _oid(head_commit, "commit")
    if not strict_ancestor(base_commit, head_commit):
        _fail("head is not a strict descendant of base")
    raw = _run_git(("diff", "--name-status", "-z", "--no-renames", base_commit, head_commit), _root()).stdout
    fields = raw.decode("utf-8", "strict").split("\x00")
    paths: list[str] = []
    for i in range(0, len(fields) - 1, 2):
        status, path = fields[i:i + 2]
        if status != "A" or not path or path.startswith("/") or ".." in path.split("/"):
            _fail("change set is not purely additive")
        paths.append(path)
    return tuple(sorted(paths))


def derive_generation_identity(authority: AuthorityTuple) -> str:
    if type(authority) is not AuthorityTuple:
        _fail("invalid generation authority")
    values = (authority.base_controller_commit, authority.applicable_spec_blob, authority.applicable_plan_blob)
    if any(not isinstance(x, str) or not _HEX40.fullmatch(x) for x in values):
        _fail("invalid generation authority object id")
    if type(authority.generation_ordinal) is not int or authority.generation_ordinal < 1:
        _fail("invalid generation ordinal")
    payload = json.dumps([*values, authority.generation_ordinal], separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def verify_repository_context(authority: AuthorityTuple, evaluation_commit: str) -> VerifiedRepositoryContext:
    if type(authority) is not AuthorityTuple:
        _fail("invalid authority")
    root = _root()
    try:
        before = root.stat(follow_symlinks=False)
        git_root = Path(_run_git(("rev-parse", "--show-toplevel"), root).stdout.decode().strip()).resolve(strict=True)
    except OSError:
        _fail("repository root verification failed")
    if git_root != root or root.is_symlink():
        _fail("module root and Git root differ")
    _oid(authority.base_controller_commit, "commit")
    _oid(authority.applicable_spec_blob, "blob")
    _oid(authority.applicable_plan_blob, "blob")
    _oid(evaluation_commit, "commit")
    if not strict_ancestor(authority.base_controller_commit, evaluation_commit):
        _fail("evaluation commit must descend from controller base")
    identity = derive_generation_identity(authority)
    if identity in reachable_committed_generation_identities(evaluation_commit):
        _fail("generation identity has already been committed")
    git_dir_raw = _run_git(("rev-parse", "--absolute-git-dir"), root).stdout.decode().strip()
    ctx = VerifiedRepositoryContext(root, Path(git_dir_raw).resolve(strict=True), evaluation_commit,
                                    authority.base_controller_commit, identity, before.st_dev, before.st_ino, object())
    _REGISTRY[id(ctx)] = (ctx, root, before.st_dev, before.st_ino)
    return ctx


def _validate_verified_repository_context(context: VerifiedRepositoryContext) -> None:
    record = _REGISTRY.get(id(context))
    if type(context) is not VerifiedRepositoryContext or record is None or record[0] is not context:
        _fail("repository context is not the exact registered instance")
    _, root, device, inode = record
    discovered_root = _root()
    if discovered_root != root:
        _fail("repository root discovery changed")
    try:
        current = root.stat(follow_symlinks=False)
    except OSError:
        _fail("repository root was replaced")
    if root.is_symlink() or current.st_dev != device or current.st_ino != inode:
        _fail("repository root identity changed")
