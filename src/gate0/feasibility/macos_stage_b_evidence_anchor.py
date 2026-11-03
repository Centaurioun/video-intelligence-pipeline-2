"""Exact S7 anchoring and opaque S1 lineage handles."""
from __future__ import annotations

import hashlib
import os
import re
import selectors
import subprocess
import time

from gate0.feasibility.macos_stage_b_evidence_constants import (
    AnchoredBlob, AnchoredS1Handle, EvidenceDagError, EvidenceFailureCode,
    FrozenArtifact, S7AnchorCreateResult, S7VerificationResult,
    VerifiedRepositoryContext,
)
from gate0.feasibility import macos_stage_b_evidence_git as gitmod

_FAILURE = EvidenceFailureCode.EVIDENCE_REFERENCE_UNRESOLVED
_PATHS = ("S1.json", "S2.plist", "S3.json", "S4.json")
_ROLES = ("S1", "S2", "S3", "S4")
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HANDLE_REGISTRY: dict[int, tuple[AnchoredS1Handle, VerifiedRepositoryContext, FrozenArtifact]] = {}


def _fail(reason: str) -> EvidenceDagError:
    return EvidenceDagError(_FAILURE, reason)


def _validate_artifacts(artifacts: tuple[FrozenArtifact, ...]) -> None:
    if type(artifacts) is not tuple or len(artifacts) != 4:
        raise _fail("S7 artifact set must contain exactly four artifacts")
    for item, role, path in zip(artifacts, _ROLES, _PATHS):
        if (type(item) is not FrozenArtifact or item.role != role or item.repository_path != path
                or type(item.data) is not bytes or item.sha256 != hashlib.sha256(item.data).hexdigest()
                or type(item.octets) is not int or item.octets != len(item.data)):
            raise _fail("S7 artifact is malformed or out of canonical order")


def _git_input(argv: tuple[str, ...], cwd, input_bytes: bytes | None = None) -> bytes:
    if type(argv) is not tuple or not argv or any(type(x) is not str or not x or "\x00" in x for x in argv):
        raise _fail("invalid Git anchor argument vector")
    if input_bytes is not None and type(input_bytes) is not bytes:
        raise _fail("Git anchor input must be immutable bytes")
    from pathlib import Path

    command_options = {
        "cwd": cwd,
        "env": {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(Path.home()),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "LC_ALL": "C",
        },
        "stdin": subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "shell": False,
        "close_fds": True,
    }
    process = None
    selector = selectors.DefaultSelector()
    stdout = bytearray()
    stderr = bytearray()
    input_offset = 0
    deadline = time.monotonic() + 10
    try:
        process = subprocess.Popen(("git", *argv), **command_options)
        if process.stdout is None or process.stderr is None:
            raise _fail("Git anchor output pipes unavailable")
        for pipe, bucket in ((process.stdout, stdout), (process.stderr, stderr)):
            os.set_blocking(pipe.fileno(), False)
            selector.register(pipe, selectors.EVENT_READ, bucket)
        if input_bytes is not None:
            if process.stdin is None:
                raise _fail("Git anchor input pipe unavailable")
            os.set_blocking(process.stdin.fileno(), False)
            if input_bytes:
                selector.register(process.stdin, selectors.EVENT_WRITE, "stdin")
            else:
                process.stdin.close()
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise _fail("Git anchor operation timed out")
            events = selector.select(remaining)
            if not events:
                raise _fail("Git anchor operation timed out")
            for key, _ in events:
                if key.data == "stdin":
                    try:
                        input_offset += os.write(key.fileobj.fileno(), input_bytes[input_offset:input_offset + 65536])
                    except BlockingIOError:
                        continue
                    except BrokenPipeError as exc:
                        raise _fail("Git anchor closed its input pipe") from exc
                    if input_offset >= len(input_bytes):
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                    continue
                bucket = key.data
                chunk = os.read(key.fileobj.fileno(), min(65536, 1_000_001 - len(bucket)))
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                if len(bucket) + len(chunk) > 1_000_000:
                    raise _fail("Git anchor output exceeded bound")
                bucket.extend(chunk)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _fail("Git anchor operation timed out")
        try:
            return_code = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            raise _fail("Git anchor operation timed out") from exc
        if return_code != 0:
            raise _fail("Git anchor operation failed")
        return bytes(stdout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail(f"Git anchor operation failed: {type(exc).__name__}") from exc
    finally:
        selector.close()
        if process is not None:
            for pipe in (process.stdin, process.stdout, process.stderr):
                if pipe is not None and not pipe.closed:
                    pipe.close()
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    try:
                        process.kill()
                        process.wait(timeout=1)
                    except OSError as exc:
                        raise _fail(f"Git anchor child cleanup failed: {type(exc).__name__}") from exc
                except OSError as exc:
                    raise _fail(f"Git anchor child cleanup failed: {type(exc).__name__}") from exc


def _git(argv: tuple[str, ...], cwd) -> bytes:
    return _git_input(argv, cwd)


def _decode_oid(value: bytes, label: str) -> str:
    try:
        result = value.decode("ascii", "strict").strip()
    except UnicodeError as exc:
        raise _fail(f"invalid {label} output encoding") from exc
    if not _HEX40.fullmatch(result):
        raise _fail(f"malformed {label} object id")
    return result


def create_s7_anchor(parent_commit_sha: str, artifacts: tuple[FrozenArtifact, FrozenArtifact, FrozenArtifact, FrozenArtifact]) -> S7AnchorCreateResult:
    _validate_artifacts(artifacts)
    if not isinstance(parent_commit_sha, str) or not _HEX40.fullmatch(parent_commit_sha):
        raise _fail("invalid S7 parent commit")
    root = gitmod._root()
    if gitmod.object_type(parent_commit_sha) != "commit":
        raise _fail("S7 parent is not a commit")
    rows = []
    anchored = []
    for artifact in artifacts:
        oid = _decode_oid(_git_input(("hash-object", "-w", "--stdin"), root, artifact.data), "blob")
        rows.append(f"100644 blob {oid}\t{artifact.repository_path}\n".encode("ascii"))
        anchored.append(AnchoredBlob(artifact.repository_path, oid, artifact.sha256, artifact.octets))
    tree_sha = _decode_oid(_git_input(("mktree",), root, b"".join(sorted(rows))), "tree")
    commit = _decode_oid(
        _git_input(("commit-tree", tree_sha, "-p", parent_commit_sha, "-m", "Gate-0 S7 evidence anchor"), root),
        "commit",
    )
    anchor = S7AnchorCreateResult(commit, tree_sha, parent_commit_sha, tuple(anchored))
    if not verify_s7_anchor(anchor, artifacts).passed:
        raise _fail("new S7 anchor failed reread verification")
    return anchor


def verify_s7_anchor(anchor: S7AnchorCreateResult, artifacts: tuple[FrozenArtifact, FrozenArtifact, FrozenArtifact, FrozenArtifact]) -> S7VerificationResult:
    try:
        _validate_artifacts(artifacts)
        if type(anchor) is not S7AnchorCreateResult or type(anchor.anchored) is not tuple or len(anchor.anchored) != 4:
            raise _fail("malformed S7 anchor record")
        if tuple(x.repository_path for x in anchor.anchored if type(x) is AnchoredBlob) != _PATHS:
            raise _fail("S7 blob descriptors are not in canonical order")
        root = gitmod._root()
        gitmod._oid(anchor.commit_sha, "commit")
        gitmod._oid(anchor.parent_commit_sha, "commit")
        if gitmod.commit_parent(anchor.commit_sha) != anchor.parent_commit_sha:
            raise _fail("S7 parent differs from anchor declaration")
        tree = gitmod.commit_tree(anchor.commit_sha)
        if tree != anchor.tree_sha:
            raise _fail("S7 tree differs from anchor declaration")
        listing = gitmod._run_git(("ls-tree", "-rz", "--full-tree", anchor.commit_sha), root).stdout
        entries = []
        for record in listing.split(b"\0"):
            if not record:
                continue
            meta, name = record.split(b"\t", 1)
            mode, kind, oid = meta.split(b" ", 2)
            entries.append((name.decode("utf-8", "strict"), mode, kind, oid.decode("ascii")))
        if tuple(sorted(x[0] for x in entries)) != tuple(sorted(_PATHS)) or any(x[1:3] != (b"100644", b"blob") for x in entries):
            raise _fail("S7 tree is not the exact closed artifact set")
        by_path = {x[0]: x[3] for x in entries}
        recorded = {x.repository_path: x for x in anchor.anchored if type(x) is AnchoredBlob}
        if len(recorded) != 4 or set(recorded) != set(_PATHS):
            raise _fail("anchor blob descriptors are not exact")
        digests = []
        for artifact in artifacts:
            blob_id = by_path[artifact.repository_path]
            raw = gitmod.read_blob_at(anchor.commit_sha, artifact.repository_path)
            if raw != artifact.data or hashlib.sha256(raw).hexdigest() != artifact.sha256 or len(raw) != artifact.octets:
                raise _fail("S7 reread differs from frozen artifact")
            descriptor = recorded[artifact.repository_path]
            if (descriptor.blob_id != blob_id or descriptor.sha256 != artifact.sha256
                    or descriptor.octets != artifact.octets):
                raise _fail("S7 blob descriptor differs from committed object")
            digests.append((artifact.repository_path, artifact.sha256))
        return S7VerificationResult(True, None, tuple(digests))
    except (EvidenceDagError, ValueError, UnicodeError, IndexError):
        return S7VerificationResult(False, _FAILURE, ())


def resolve_anchored_s1(repository_context: VerifiedRepositoryContext, anchor: S7AnchorCreateResult) -> AnchoredS1Handle:
    gitmod._validate_verified_repository_context(repository_context)
    if type(anchor) is not S7AnchorCreateResult:
        raise _fail("S7 anchor has invalid type")
    artifacts_list = []
    for role, path in zip(_ROLES, _PATHS):
        raw = gitmod.read_blob_at(anchor.commit_sha, path)
        artifacts_list.append(FrozenArtifact(role, path, raw, hashlib.sha256(raw).hexdigest(), len(raw)))
    artifacts = tuple(artifacts_list)
    if not verify_s7_anchor(anchor, artifacts).passed:
        raise _fail("S7 anchor verification failed")
    if anchor.commit_sha != repository_context.evaluation_commit:
        raise _fail("S7 anchor and verified repository context differ")
    if anchor.parent_commit_sha != repository_context.base_controller_commit:
        raise _fail("S7 parent differs from verified controller base")
    s1 = artifacts[0]
    handle = AnchoredS1Handle(anchor.commit_sha, "S1.json", anchor.anchored[0].blob_id, s1,
                              repository_context.generation_identity, repository_context._registration_token, object())
    _HANDLE_REGISTRY[id(handle)] = (handle, repository_context, s1)
    return handle


def _extract_registered_anchored_s1(handle: AnchoredS1Handle, repository_context: VerifiedRepositoryContext) -> FrozenArtifact:
    gitmod._validate_verified_repository_context(repository_context)
    record = _HANDLE_REGISTRY.get(id(handle))
    if type(handle) is not AnchoredS1Handle or record is None or record[0] is not handle or record[1] is not repository_context:
        raise _fail("S1 handle is not the exact registered handle for this context")
    if handle.frozen_s1 is not record[2] or handle.repository_context_token is not repository_context._registration_token:
        raise _fail("S1 handle lineage is invalid")
    return record[2]
