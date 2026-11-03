#!/usr/bin/env python3
"""PKT-D2-1: deterministic D-2 Owner-input completeness validator (text only).

Usage::

    python scripts/verify_gate0_d2_inputs.py --package <d2-package-dir> --format json

Exit codes (checklist Part C):

* ``0`` -- every one of the thirty rows is VERIFIED (structurally unreachable
  before authentic D-3 evidence exists).
* ``1`` -- incomplete; the report lists each field ID with its deterministic
  state and the evidence still missing.
* ``2`` -- refused/invalid package (duplicate/missing/unknown field ID, a
  placeholder digest, a declared media path, or any authorization claim).

This entry point is intentionally not wired into the Gate-0 run CLI or any
stage pipeline.  It reads only the abstract D-2 package directory; it never
resolves, opens or hashes a declared corpus/media path.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gate0 import d2_intake


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic text-only Gate-0 D-2 Owner-input readiness checker.",
    )
    parser.add_argument("--package", required=True, help="D-2 intake package directory")
    parser.add_argument("--format", choices=("json", "markdown"), default="json",
                        help="report format (default: json)")
    return parser


def _render_refusal(reason: str, detail: str) -> str:
    payload = {
        "schema_version": d2_intake.D2_REPORT_SCHEMA_VERSION,
        "tool_version": d2_intake.D2_TOOL_VERSION,
        "state": "REFUSED",
        "exit_code": 2,
        "error": {"reason": reason, "detail": detail},
    }
    return d2_intake.canonical_json_text(payload) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = d2_intake.evaluate_d2_package(Path(args.package))
    except d2_intake.D2IntakeError as exc:
        sys.stdout.write(_render_refusal(exc.reason, exc.detail))
        return 2
    except (OSError, ValueError) as exc:  # fail closed: no traceback, no partial pass
        sys.stdout.write(_render_refusal("D2_VALIDATOR_INTERNAL", str(exc)))
        return 2

    if args.format == "markdown":
        sys.stdout.write(d2_intake.render_report_markdown(report))
    else:
        sys.stdout.write(d2_intake.render_report_json(report))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
