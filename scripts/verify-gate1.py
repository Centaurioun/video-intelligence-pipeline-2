#!/usr/bin/env python3
"""Verify one closed Gate-1 artifact root under current H0 authority."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gate1.verify import VerificationError, verify_path, verify_schemas  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_root", nargs="?", type=Path)
    parser.add_argument("--mode", choices=("SYNTHETIC", "REAL"), default="SYNTHETIC")
    parser.add_argument("--schemas", action="store_true", help="validate the checked-in schema registry")
    args = parser.parse_args()
    try:
        if args.schemas:
            verify_schemas(ROOT / "schemas" / "gate1")
        if args.artifact_root is not None:
            verify_path(args.artifact_root, mode=args.mode)
        elif not args.schemas:
            parser.error("provide an artifact root or --schemas")
    except VerificationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
