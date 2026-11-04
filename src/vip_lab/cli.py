"""Packet PX: Command-Line Interface for VIP Synthetic Multi-Gate Lab.

Subcommands:
- ``preflight-s5``
- ``preflight-gate0``
- ``preflight-gate1``
- ``preflight-gate2``
- ``preflight-gate3``
- ``summarize-program``

Deterministic Exit Codes:
- ``0``  — ``ReadinessStatus.READY_SYNTHETIC``
- ``10`` — ``ReadinessStatus.BLOCKED`` or ``ReadinessStatus.NOT_OBSERVED``
- ``20`` — ``ReadinessStatus.NOT_AUTHORIZED``
- ``30`` — ``ReadinessStatus.INVALID`` or input/parsing ``VipLabError``
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .common import (
    MAX_LAB_JSON_BYTES,
    ReadinessPacket,
    ReadinessStatus,
    VipLabError,
    canonical_json_dumps,
    load_bounded_json_file,
)
from .integration import (
    evaluate_mega03_composite,
    evaluate_mega06_composite,
    evaluate_mega07_composite,
    summarize_program,
)
from .mega03 import inspect_s5_declaration
from .mega04 import inspect_gate0_entry
from .mega05 import inspect_benchmark_entry


EXIT_READY_SYNTHETIC = 0
EXIT_BLOCKED = 10
EXIT_NOT_AUTHORIZED = 20
EXIT_INVALID = 30


def status_to_exit_code(status: ReadinessStatus) -> int:
    if status == ReadinessStatus.READY_SYNTHETIC:
        return EXIT_READY_SYNTHETIC
    if status in (ReadinessStatus.BLOCKED, ReadinessStatus.NOT_OBSERVED):
        return EXIT_BLOCKED
    if status == ReadinessStatus.NOT_AUTHORIZED:
        return EXIT_NOT_AUTHORIZED
    return EXIT_INVALID


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vip-lab",
        description="VIP Synthetic Multi-Gate Readiness & Preflight CLI (LAB-MEGA-03-07-v1.1.0)",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_s5 = sub.add_parser("preflight-s5", help="Run MEGA-03 S5 / composite preflight")
    p_s5.add_argument("--input", required=True, help="Path to JSON input payload")
    p_s5.add_argument("--snapshot-root", default=None, help="Optional synthetic snapshot root")
    p_s5.add_argument("--max-bytes", type=int, default=MAX_LAB_JSON_BYTES)

    for cmd_name, help_text in (
        ("preflight-gate0", "Run MEGA-04 Gate-0 entry preflight"),
        ("preflight-gate1", "Run MEGA-05 Gate-1 three-arm benchmark entry preflight"),
        ("preflight-gate2", "Run MEGA-06 Gate-2 workload/recovery/measurement preflight"),
        ("preflight-gate3", "Run MEGA-07 Gate-3 temporal/lineage/QC preflight"),
        ("summarize-program", "Run cross-gate MEGA-03..07 program summary"),
    ):
        p = sub.add_parser(cmd_name, help=help_text)
        p.add_argument("--input", required=True, help="Path to JSON input payload")
        p.add_argument("--max-bytes", type=int, default=MAX_LAB_JSON_BYTES)

    return parser


def run_cli(argv: Sequence[str] | None = None) -> tuple[int, dict[str, object]]:
    """Execute CLI subcommand and return ``(exit_code, output_dict)``."""
    parser = _build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else EXIT_INVALID
        return (
            EXIT_INVALID if code != 0 else 0,
            {
                "status": ReadinessStatus.INVALID.value,
                "error": {"code": "CLI_ARGUMENT_ERROR", "message": "Invalid CLI arguments"},
            },
        )

    try:
        payload = load_bounded_json_file(
            args.input,
            max_bytes=args.max_bytes,
            require_mapping=True,
        )
        cmd = args.subcommand
        packet: ReadinessPacket
        if cmd == "preflight-s5":
            if (
                "s5_declaration" in payload
                or "stream_namespace" in payload
                or "review_bundle" in payload
            ):
                merged = dict(payload)
                if getattr(args, "snapshot_root", None) is not None:
                    merged["snapshot_root"] = args.snapshot_root
                packet = evaluate_mega03_composite(merged)
            else:
                packet = inspect_s5_declaration(
                    payload,
                    snapshot_root=getattr(args, "snapshot_root", None),
                )
        elif cmd == "preflight-gate0":
            packet = inspect_gate0_entry(payload)
        elif cmd == "preflight-gate1":
            packet = inspect_benchmark_entry(payload)
        elif cmd == "preflight-gate2":
            packet = evaluate_mega06_composite(payload)
        elif cmd == "preflight-gate3":
            packet = evaluate_mega07_composite(payload)
        elif cmd == "summarize-program":
            packet = summarize_program(payload)
        else:
            raise VipLabError("CLI_UNKNOWN_SUBCOMMAND", f"Unknown subcommand {cmd!r}")
    except VipLabError as exc:
        err_out = {
            "status": ReadinessStatus.INVALID.value,
            "synthetic_only": True,
            "execution_authorized": False,
            "error": exc.to_dict(),
        }
        return EXIT_INVALID, err_out

    return status_to_exit_code(packet.status), packet.to_dict()


def main(argv: Sequence[str] | None = None) -> int:
    exit_code, result = run_cli(argv)
    sys.stdout.write(canonical_json_dumps(result) + "\n")
    sys.stdout.flush()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
