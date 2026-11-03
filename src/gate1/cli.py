"""Explicit command line surface for the generated, local-only Gate-1 harness."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence


_CLAIMS = "protocol readiness only; no real benchmark; no winner; no gate promotion"


class _Parser(argparse.ArgumentParser):
    """Keep readiness limits visible on every parser-generated help/error."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("epilog", _CLAIMS)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n{_CLAIMS}\n")


def _parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="python -m gate1.cli",
        description="Run the synthetic-only Gate-1 protocol readiness harness.",
    )
    commands = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)

    generate = commands.add_parser(
        "generate-fixtures", help="write the generated fixture catalog"
    )
    generate.add_argument("--output-dir", required=True, type=Path)

    run = commands.add_parser("run-generated", help="run one generated fixture case")
    run.add_argument("--mode", choices=("SYNTHETIC", "REAL"), default="SYNTHETIC")
    # These are checked after mode so REAL is refused before case/output validation.
    run.add_argument("--case-id")
    run.add_argument("--output-dir", type=Path)

    run_three = commands.add_parser(
        "run-three-arm-generated", help="run one generated case through the synthetic three-arm adapter"
    )
    run_three.add_argument("--mode", choices=("SYNTHETIC", "REAL"), default="SYNTHETIC")
    run_three.add_argument("--case-id")
    run_three.add_argument("--output-dir", type=Path)

    verify = commands.add_parser(
        "verify-generated", help="verify a generated artifact closure"
    )
    verify.add_argument("--artifact-dir", required=True, type=Path)
    return parser


def _readiness(message: str) -> str:
    return f"{message}; {_CLAIMS}"


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        from gate1.verify import verify_synthetic_only

        # Wire the synthetic-only source/import boundary check into every command.
        verify_synthetic_only(Path(__file__).resolve().parents[2])

        if args.command == "generate-fixtures":
            from gate1.harness import write_generated_fixtures

            write_generated_fixtures(args.output_dir)
            print(_readiness(f"Generated fixtures written to {args.output_dir}"))
            return 0

        if args.command == "run-generated":
            if args.mode == "REAL":
                raise ValueError("REAL execution refused: current harness authority is synthetic-only")
            if not args.case_id:
                raise ValueError("--case-id is required for SYNTHETIC execution")
            if args.output_dir is None:
                raise ValueError("--output-dir is required for SYNTHETIC execution")
            from gate1.harness import run_generated_case

            result = run_generated_case(args.case_id, args.output_dir)
            print(_readiness(f"Generated case completed: {result}"))
            return 0

        if args.command == "run-three-arm-generated":
            if args.mode == "REAL":
                raise ValueError("REAL execution refused: current harness authority is synthetic-only")
            if not args.case_id:
                raise ValueError("--case-id is required for SYNTHETIC execution")
            if args.output_dir is None:
                raise ValueError("--output-dir is required for SYNTHETIC execution")
            from gate1.harness import run_generated_three_arm_case

            result = run_generated_three_arm_case(args.case_id, args.output_dir)
            print(_readiness(f"Generated three-arm case completed: {result}"))
            return 0

        if args.command == "verify-generated":
            from gate1.verify import verify_path

            verify_path(args.artifact_dir, mode="SYNTHETIC")
            print(_readiness(f"Generated artifacts verified at {args.artifact_dir}"))
            return 0

        # Argparse's required subparser makes this unreachable; retain fail-closed behavior.
        raise ValueError("unsupported command")
    except Exception as exc:
        print(_readiness(f"error: {exc}"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
