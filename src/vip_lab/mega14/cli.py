"""CLI entrypoint for MEGA-14 synthetic end-to-end orchestration and verification."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from vip_lab.common import (
    VipLabError,
    canonical_json_dumps,
    load_bounded_json_file,
)
from vip_lab.mega14.orchestrator import run_end_to_end_synthetic_lab
from vip_lab.mega14.report import verify_e2e_lab_report
from vip_lab.mega14.scenario import (
    default_single_arm_scenario,
    default_three_arm_scenario,
    load_e2e_scenario_file,
)

EXIT_OK = 0
EXIT_BLOCKED = 10
EXIT_NOT_AUTHORIZED = 20
EXIT_INVALID = 30

_FORBIDDEN_CLI_FLAGS = frozenset(
    {
        "--real",
        "--render",
        "--export",
        "--provider",
        "--download",
        "--approve",
        "--force-authorize",
    }
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m vip_lab.mega14.cli",
        description="VIP Synthetic Lab End-to-End Orchestrator & Verifier (MEGA-08..14)",
    )
    sub = parser.add_subparsers(dest="subcommand")

    run_p = sub.add_parser(
        "run-synthetic-scenario",
        help="Execute the synthetic-only MEGA-08..14 pipeline on a scenario.",
    )
    run_p.add_argument(
        "--mode",
        choices=("single-arm", "three-arm"),
        default="three-arm",
        help="Default synthetic scenario mode when --scenario is omitted.",
    )
    run_p.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Optional path to a SyntheticLabScenario JSON file.",
    )
    run_p.add_argument(
        "--workspace-root",
        type=str,
        default=None,
        help="Optional repository root path for MEGA-08 AST capability inventory.",
    )
    run_p.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional file path to write the canonical EndToEndLabReport JSON.",
    )

    ver_p = sub.add_parser(
        "verify-report",
        help="Verify an EndToEndLabReport JSON file using Stretch S2 cross-artifact checks.",
    )
    ver_p.add_argument(
        "--report",
        type=str,
        required=True,
        help="Path to the EndToEndLabReport JSON file.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)

    for token in args_list:
        flag = token.split("=", 1)[0]
        if flag in _FORBIDDEN_CLI_FLAGS:
            err = {
                "status": "NOT_AUTHORIZED",
                "error_code": "CLI_FORBIDDEN_AUTHORITY_OR_EXECUTION_FLAG",
                "rejected_flag": flag,
            }
            sys.stdout.write(canonical_json_dumps(err) + "\n")
            return EXIT_NOT_AUTHORIZED

    parser = _build_parser()
    try:
        ns = parser.parse_args(args_list)
    except SystemExit as exc:
        return 0 if exc.code == 0 else EXIT_INVALID

    if ns.subcommand == "run-synthetic-scenario":
        try:
            if ns.scenario:
                scen = load_e2e_scenario_file(ns.scenario)
            elif ns.mode == "single-arm":
                scen = default_single_arm_scenario()
            else:
                scen = default_three_arm_scenario()

            report = run_end_to_end_synthetic_lab(
                scen,
                workspace_root=ns.workspace_root,
            )
            serialized = report.to_canonical_json()
            if ns.output:
                out_path = Path(ns.output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(serialized + "\n", encoding="utf-8")
            sys.stdout.write(
                canonical_json_dumps(
                    {
                        "status": report.status,
                        "report_digest": report.report_digest,
                        "scenario_id": report.scenario_id,
                        "mode": report.mode,
                        "production_export_authorized": report.production_export_authorized,
                        "export_status": report.export_status,
                    }
                )
                + "\n"
            )
            return EXIT_OK
        except VipLabError as exc:
            sys.stdout.write(canonical_json_dumps(exc.to_dict()) + "\n")
            return EXIT_INVALID

    if ns.subcommand == "verify-report":
        try:
            raw = load_bounded_json_file(ns.report, require_mapping=True)
            verified = verify_e2e_lab_report(raw)
            sys.stdout.write(
                canonical_json_dumps(
                    {
                        "status": verified["status"],
                        "report_digest": verified["report_digest"],
                        "verified": True,
                    }
                )
                + "\n"
            )
            return EXIT_OK
        except VipLabError as exc:
            sys.stdout.write(canonical_json_dumps(exc.to_dict()) + "\n")
            return EXIT_INVALID

    parser.print_help(sys.stdout)
    return EXIT_INVALID


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
