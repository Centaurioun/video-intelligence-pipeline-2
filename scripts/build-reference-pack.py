#!/usr/bin/env python3
"""Build or verify selected immutable source snapshots in reference-pack.

Normal operation never deletes a curated file and refuses to overwrite a
non-identical snapshot. An explicit, exact-path-validated purge mode removes
only snapshots the selection manifest now marks prohibited from copying.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external"
PACK = ROOT / "reference-pack"
SELECTION = PACK / "selection-manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_child(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes its expected root: {relative}") from exc
    return candidate


def load_selection() -> list[dict[str, Any]]:
    raw = json.loads(SELECTION.read_text(encoding="utf-8"))
    if raw.get("version") != 1 or not isinstance(raw.get("references"), list):
        raise ValueError("selection-manifest.json must be a version-1 selection list")
    return raw["references"]


def purge_prohibited_snapshots(references: list[dict[str, Any]], dry_run: bool) -> int:
    """Remove only manifest-listed generated snapshots, refusing unknown files."""
    failures = 0
    removed = 0
    for reference in references:
        if reference.get("copy_source", True):
            continue
        identifier = reference.get("id")
        files = reference.get("files")
        if not isinstance(identifier, str) or not isinstance(files, list):
            print(f"FAILED {identifier!r}: invalid prohibited-copy reference", file=sys.stderr)
            failures += 1
            continue
        source_root = safe_child(PACK / identifier, "source")
        if not source_root.exists():
            print(f"ABSENT   {identifier}: no prohibited source snapshot")
            continue
        expected: set[Path] = set()
        for item in files:
            source_path = item.get("source_path") if isinstance(item, dict) else None
            if not isinstance(source_path, str):
                print(f"FAILED {identifier}: invalid source_path in selection", file=sys.stderr)
                failures += 1
                expected = set()
                break
            expected.add(safe_child(source_root, source_path))
        if not expected:
            continue
        actual = {path.resolve() for path in source_root.rglob("*") if path.is_file()}
        if actual != expected:
            unexpected = sorted(str(path.relative_to(source_root.resolve())) for path in actual - expected)
            missing = sorted(str(path.relative_to(source_root.resolve())) for path in expected - actual)
            print(
                f"FAILED {identifier}: refusing purge because source snapshot differs from generated selection "
                f"(unexpected={unexpected}, missing={missing})",
                file=sys.stderr,
            )
            failures += 1
            continue
        if dry_run:
            print(f"PLAN     {identifier}: would remove {len(actual)} prohibited generated source snapshots")
            continue
        for path in sorted(actual, key=lambda item: len(item.parts), reverse=True):
            path.unlink()
            removed += 1
        for directory in sorted((path for path in source_root.rglob("*") if path.is_dir()), key=lambda item: len(item.parts), reverse=True):
            directory.rmdir()
        source_root.rmdir()
        print(f"PURGED   {identifier}: removed {len(actual)} prohibited generated source snapshots")
    print(f"Purge summary: removed={removed} failed={failures}")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify snapshots only; do not copy")
    parser.add_argument("--id", action="append", dest="ids", help="reference id to process; repeatable")
    parser.add_argument("--purge-prohibited", action="store_true", help="remove only exact generated snapshots now prohibited by copy policy")
    parser.add_argument("--dry-run", action="store_true", help="show an explicit prohibited-snapshot purge without deleting")
    args = parser.parse_args()
    try:
        references = load_selection()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAILED selection manifest: {exc}", file=sys.stderr)
        return 2
    requested = set(args.ids or [])
    available = {item.get("id") for item in references}
    if requested - available:
        print("FAILED unknown reference id(s): " + ", ".join(sorted(requested - available)), file=sys.stderr)
        return 2
    if args.dry_run and not args.purge_prohibited:
        print("FAILED --dry-run is only valid with --purge-prohibited", file=sys.stderr)
        return 2
    if args.purge_prohibited:
        if requested:
            references = [item for item in references if item.get("id") in requested]
        return purge_prohibited_snapshots(references, args.dry_run)
    failures = 0
    copied = 0
    verified = 0
    for reference in references:
        identifier = reference.get("id")
        if requested and identifier not in requested:
            continue
        files = reference.get("files")
        copy_source = reference.get("copy_source", True)
        if not isinstance(identifier, str) or not isinstance(files, list) or not files or not isinstance(copy_source, bool):
            print(f"FAILED {identifier!r}: each reference needs a nonempty files list", file=sys.stderr)
            failures += 1
            continue
        for selected in files:
            source_path = selected.get("source_path") if isinstance(selected, dict) else None
            if not isinstance(source_path, str) or not source_path or source_path.startswith("/"):
                print(f"FAILED {identifier}: invalid source_path {source_path!r}", file=sys.stderr)
                failures += 1
                continue
            source = safe_child(EXTERNAL / identifier, source_path)
            destination = safe_child(PACK / identifier / "source", source_path)
            if not source.is_file():
                print(f"FAILED {identifier}: missing external source {source_path}", file=sys.stderr)
                failures += 1
                continue
            if not copy_source:
                if destination.exists():
                    print(f"FAILED {identifier}: raw source snapshot is prohibited by this pack's copy policy: {source_path}", file=sys.stderr)
                    failures += 1
                    continue
                print(f"MAPPED   {identifier}: {source_path}")
                verified += 1
                continue
            if destination.exists():
                if not destination.is_file() or sha256(source) != sha256(destination):
                    print(f"FAILED {identifier}: existing curated file differs: {source_path}", file=sys.stderr)
                    failures += 1
                    continue
                print(f"VERIFIED {identifier}: {source_path}")
                verified += 1
                continue
            if args.check:
                print(f"FAILED {identifier}: missing curated file: {source_path}", file=sys.stderr)
                failures += 1
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            print(f"COPIED   {identifier}: {source_path}")
            copied += 1
    print(f"Summary: copied={copied} verified={verified} failed={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
