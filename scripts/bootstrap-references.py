#!/usr/bin/env python3
"""Safely create pinned sparse reference checkouts for Phase 0.

The script intentionally never pulls, resets, deletes, or overwrites an
existing checkout. It only clones a missing, exact configured source into the
Git-ignored `external/` workspace, then detaches at the recorded commit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "scripts" / "reference-sources.json"
EXTERNAL = ROOT / "external"
ID_RE = re.compile(r"^[a-z0-9_]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def run(args: list[str], *, cwd: Path | None = None, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env={**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"},
    )


def git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", str(path), *args])


def normalized_remote(url: str) -> str:
    return url.strip().removesuffix(".git").rstrip("/").lower()


def load_references() -> list[dict[str, Any]]:
    raw = json.loads(CONFIG.read_text(encoding="utf-8"))
    if raw.get("version") != 1 or not isinstance(raw.get("references"), list):
        raise ValueError("reference-sources.json must be a version-1 reference list")
    seen: set[str] = set()
    refs: list[dict[str, Any]] = []
    for ref in raw["references"]:
        identifier = ref.get("id", "")
        commit = ref.get("commit", "")
        patterns = ref.get("sparse_patterns")
        if not ID_RE.fullmatch(identifier) or identifier in seen:
            raise ValueError(f"invalid or duplicate reference id: {identifier!r}")
        if not isinstance(ref.get("clone_url"), str) or not ref["clone_url"].startswith("https://github.com/"):
            raise ValueError(f"{identifier}: clone_url must be a GitHub HTTPS URL")
        if not isinstance(ref.get("default_branch"), str) or not ref["default_branch"]:
            raise ValueError(f"{identifier}: default_branch is required")
        if not SHA_RE.fullmatch(commit):
            raise ValueError(f"{identifier}: commit must be a full lowercase SHA")
        if not isinstance(patterns, list) or not patterns or not all(isinstance(item, str) and item.startswith("/") for item in patterns):
            raise ValueError(f"{identifier}: sparse_patterns must be nonempty root-relative paths")
        seen.add(identifier)
        refs.append(ref)
    return refs


def existing_state(ref: dict[str, Any], destination: Path) -> tuple[str, str]:
    if not destination.exists():
        return "MISSING", ""
    inside = git(destination, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return "SKIP", "destination exists but is not a Git worktree; left untouched"
    status = git(destination, "status", "--porcelain", "--untracked-files=normal")
    if status.returncode != 0:
        return "SKIP", "could not inspect existing worktree; left untouched"
    if status.stdout.strip():
        return "SKIP", "existing worktree is modified/untracked; left untouched"
    remote = git(destination, "remote", "get-url", "origin")
    if remote.returncode != 0 or normalized_remote(remote.stdout) != normalized_remote(ref["clone_url"]):
        return "SKIP", "existing origin differs or is unavailable; left untouched"
    head = git(destination, "rev-parse", "HEAD")
    if head.returncode != 0:
        return "SKIP", "existing checkout has no readable HEAD; left untouched"
    if head.stdout.strip() != ref["commit"]:
        return "SKIP", f"existing HEAD {head.stdout.strip()} differs from pinned {ref['commit']}; left untouched"
    sparse = git(destination, "sparse-checkout", "list")
    actual_patterns = {line for line in sparse.stdout.splitlines() if line}
    expected_patterns = set(ref["sparse_patterns"])
    if sparse.returncode != 0 or actual_patterns != expected_patterns:
        return "SKIP", "existing sparse selection differs from the pinned config; left untouched"
    return "VERIFIED", f"already present at pinned {ref['commit']}"


def clone_reference(ref: dict[str, Any], destination: Path, dry_run: bool) -> tuple[bool, str]:
    if dry_run:
        return True, f"would sparse-clone {ref['clone_url']} at {ref['commit']}"

    EXTERNAL.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{ref['id']}.", dir=EXTERNAL) as temporary_parent:
        temporary = Path(temporary_parent) / "checkout"
        clone = run([
            "git", "clone", "--no-checkout", "--depth", "1", "--no-tags", "--single-branch",
            "--filter=blob:none", "--branch", ref["default_branch"], ref["clone_url"], str(temporary),
        ])
        if clone.returncode != 0:
            return False, "clone failed: " + clone.stdout.strip()
        sparse = git(temporary, "sparse-checkout", "init", "--no-cone")
        if sparse.returncode != 0:
            return False, "sparse-checkout init failed: " + sparse.stdout.strip()
        selected = run(
            ["git", "-C", str(temporary), "sparse-checkout", "set", "--no-cone", "--stdin"],
            input_text="\n".join(ref["sparse_patterns"]) + "\n",
        )
        if selected.returncode != 0:
            return False, "sparse-checkout set failed: " + selected.stdout.strip()
        checkout = git(temporary, "checkout", "--detach", ref["commit"])
        if checkout.returncode != 0:
            return False, "pinned checkout failed: " + checkout.stdout.strip()
        head = git(temporary, "rev-parse", "HEAD")
        if head.returncode != 0 or head.stdout.strip() != ref["commit"]:
            return False, "pinned checkout did not resolve to the configured commit"
        try:
            os.rename(temporary, destination)
        except OSError as exc:
            return False, f"cannot atomically install completed checkout: {exc}"
    return True, f"cloned pinned sparse checkout at {ref['commit']}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", action="append", dest="ids", help="reference id to process; repeatable")
    parser.add_argument("--dry-run", action="store_true", help="report planned clones without changing external/")
    args = parser.parse_args()
    try:
        references = load_references()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAILED configuration: {exc}", file=sys.stderr)
        return 2
    requested = set(args.ids or [])
    known = {ref["id"] for ref in references}
    unknown = requested - known
    if unknown:
        print("FAILED unknown reference id(s): " + ", ".join(sorted(unknown)), file=sys.stderr)
        return 2
    selected_refs = [ref for ref in references if not requested or ref["id"] in requested]
    failures = 0
    for ref in selected_refs:
        destination = EXTERNAL / ref["id"]
        state, detail = existing_state(ref, destination)
        if state != "MISSING":
            print(f"{state:8} {ref['id']}: {detail}")
            continue
        okay, detail = clone_reference(ref, destination, args.dry_run)
        print(f"{'CLONED' if okay and not args.dry_run else 'PLAN' if okay else 'FAILED':8} {ref['id']}: {detail}")
        failures += int(not okay)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
